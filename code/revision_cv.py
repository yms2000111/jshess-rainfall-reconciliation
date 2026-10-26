"""Purged nested year cross-validation; resumable per domain/year/QC.

All array scales are W1,W2,W3,W4,D28. No validation observation enters a fit.
The frozen plan is analysis_plan_20261023.md. Run --pilot before --workers N.
"""
import os
os.environ['OMP_NUM_THREADS']='1'
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['MKL_NUM_THREADS']='1'
from common import ROOT,REGIONS
import numpy as np,pandas as pd,json,hashlib,time,argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from scipy.optimize import minimize
from scipy.special import gammainc
from scipy.stats import gamma
from rainfall_baselines import csg_crps
from core_reconciliation import covariance_shrink,project,S

OUT=ROOT/'revision';CACHE=OUT/'cache';FOLDS=OUT/'folds'
for p in [OUT,CACHE,FOLDS]:p.mkdir(exist_ok=True)
SEED=20261023;LEADS=['W1','W2','W3','W4','D28'];VERSION='csg-spread-monthly-v1'

def calendar_day(dates):
 return pd.to_datetime(['2000-'+d.strftime('%m-%d') for d in dates]).dayofyear.to_numpy()

def near_day(a,b):
 d=np.abs(np.asarray(a)-np.asarray(b));return np.minimum(d,366-d)

def permitted(dates,excluded,base=None):
 """Exclude any origin or 28-day end in the embargo years."""
 end=dates+pd.Timedelta(days=28)
 good=~np.isin(dates.year,excluded)&~np.isin(end.year,excluded)
 if base is not None:
  mask=np.zeros(len(dates),bool);mask[base]=True;good&=mask
 return np.flatnonzero(good)

def inner_splits(dates,train):
 years=np.unique(dates[train].year)
 for group in np.array_split(years,5):
  validation=train[np.isin(dates[train].year,group)]
  embargo=np.unique(np.r_[group-1,group,group+1])
  fit=permitted(dates,embargo,train)
  assert not set(dates[fit].year)&set(embargo)
  assert not set((dates[fit]+pd.Timedelta(days=28)).year)&set(embargo)
  yield fit,validation,embargo

def moments(parameters,x,v):
 a,b,c,d,e,shift=parameters
 # Only the signed-archive sensitivity can have a negative ensemble mean.
 mu=np.maximum(a+b*x,1e-6);var=np.maximum(c+d*np.maximum(x,0)+e*v,1e-7)
 return mu,var,shift

def mean_csg(mu,var,shift):
 shape=mu*mu/var;theta=var/mu;z=shift/theta
 return mu*(1-gammainc(shape+1,z))-shift*(1-gammainc(shape,z))

def fit_records(raw,y,dates,train,key,qc,legacy=False):
 stamp=hashlib.sha256((VERSION+key+qc+str(legacy)).encode()+train.tobytes()).hexdigest()[:24]
 path=CACHE/(stamp+'.json')
 if path.exists():return json.loads(path.read_text())
 days=calendar_day(dates);records=[]
 groups=range(4) if legacy else range(1,13)
 for k in range(5):
  warm=None;oldscale=None
  for month in groups:
   if legacy:tr=train[((dates.month.to_numpy()[train]%12)//3)==month]
   else:
    center=pd.Timestamp(2000,month,15).dayofyear;tr=train[near_day(days[train],center)<=45]
   scale=max(float(y[tr,k].mean()),.1);x=raw[tr,:,k].mean(1)/scale;v=raw[tr,:,k].var(1,ddof=1)/scale**2;obs=y[tr,k]/scale
   if legacy:v=np.zeros_like(v)
   def objective(logp):
    p=np.exp(logp)
    if legacy:p=np.r_[p[:4],0.,p[4]]
    mu,var,shift=moments(p,x,v);values=csg_crps(obs,mu,var,shift)
    return float(np.mean(values)) if np.isfinite(values).all() else 1e8
   default=np.array([.1,1.,.1,.5,.5,.1])
   if warm is not None:
    ratio=oldscale/scale;start=warm*np.array([ratio,1,ratio**2,ratio,1,ratio])
   else:start=default
   if legacy:start=start[[0,1,2,3,5]]
   res=minimize(objective,np.log(np.maximum(start,1e-5)),method='L-BFGS-B',bounds=[(-10,5)]*len(start),options={'maxiter':180,'ftol':2e-8,'gtol':2e-5,'maxls':30})
   attempts=1
   if not res.success or not np.isfinite(res.fun):
    st=default[[0,1,2,3,5]] if legacy else default
    retry=minimize(objective,np.log(st),method='L-BFGS-B',bounds=[(-10,5)]*len(st),options={'maxiter':500,'ftol':2e-9,'gtol':1e-5,'maxls':40})
    if retry.fun<res.fun or (retry.success and not res.success):res=retry
    attempts+=1
   p=np.exp(res.x)
   if legacy:p=np.r_[p[:4],0.,p[4]]
   warm=p.copy();oldscale=scale
   records.append(dict(group=int(month),lead=k,scale_mm=scale,parameters=p.tolist(),n=len(tr),success=bool(res.success),iterations=int(res.nit),objective=float(res.fun),attempts=attempts,boundary=bool((res.x< -9.9).any() or (res.x>4.9).any()),legacy=legacy))
 path.write_text(json.dumps(records,indent=2));return records

def distribution(raw,y,dates,records,ix,members=None):
 means=np.empty((len(ix),5));exact=np.empty_like(means)
 samples=None if members is None else np.empty((len(ix),members,5))
 groups=((dates.month.to_numpy()%12)//3) if records[0]['legacy'] else dates.month.to_numpy()
 for r in records:
  local=np.flatnonzero(groups[ix]==r['group']);tr=ix[local];k=r['lead'];sc=r['scale_mm']
  if not len(tr):continue
  mu,var,shift=moments(r['parameters'],raw[tr,:,k].mean(1)/sc,raw[tr,:,k].var(1,ddof=1)/sc**2)
  means[local,k]=mean_csg(mu,var,shift)*sc
  exact[local,k]=csg_crps(y[tr,k]/sc,mu,var,shift)*sc
  if members is not None:
   u=(np.arange(members)+.5)/members
   samples[local,:,k]=np.maximum(gamma.ppf(u[None,:],(mu*mu/var)[:,None],scale=(var/mu)[:,None])-shift,0)*sc
 return means,exact,samples

def couple(quantiles,templates,rng):
 out=np.empty_like(quantiles)
 for i in range(len(out)):
  for k in range(5):
   order=np.lexsort((rng.random(out.shape[1]),templates[i,:,k]));out[i,order,k]=quantiles[i,:,k]
 return out

def bottomup(a):
 out=a.copy();out[:,:,4]=out[:,:,:4].sum(2);return out

def load_data(key,qc):
 d=np.load(ROOT/f'data/processed/{key}.npz');raw=d['raw']
 if qc!='primary':raw=np.load(OUT/f'raw_{qc}_{key}.npz')['raw']
 return d,pd.DatetimeIndex(d['dates']),raw,d['y']

def run_fold(task):
 key,year,qc=task;target=FOLDS/f'{qc}_{key}_{year}.npz'
 if target.exists():return f'{qc} {key} {year}: cached'
 started=time.monotonic();d,dates,raw,y=load_data(key,qc);days=calendar_day(dates)
 excluded=[year-1,year,year+1];train=permitted(dates,excluded);test=np.flatnonzero(dates.year==year)
 assert not set(dates[train].year)&set(excluded)
 errors=[];inner_metadata=[];oof_ix=[];oof_mean=[]
 for fit,val,embargo in inner_splits(dates,train):
  rec=fit_records(raw,y,dates,fit,key,qc)
  mean,_,_=distribution(raw,y,dates,rec,val)
  errors.append(y[val]-mean);oof_ix.extend(val);oof_mean.extend(mean)
  inner_metadata.append(dict(train=fit.tolist(),validation=val.tolist(),excluded_years=embargo.tolist()))
 W,shrink=covariance_shrink(np.concatenate(errors));rec=fit_records(raw,y,dates,train,key,qc)
 mean,exact,quantiles=distribution(raw,y,dates,rec,test,200)
 rng=np.random.default_rng(SEED+year+1000*list(REGIONS).index(key));templates=[];templates11=[];clim=[];threshold=[];qm=[]
 for t in test:
  near=train[near_day(days[train],days[t])<=45]
  templates.append(y[rng.choice(near,200,replace=True)]);templates11.append(y[rng.choice(near,11,replace=False)])
  # Exact empirical climatology is evaluated downstream from its full support.
  clim.append(y[rng.choice(near,200,replace=True)]);threshold.append(np.quantile(y[near],2/3,axis=0))
  q=np.empty((11,5))
  for k in range(5):
   a=np.sort(raw[near,:,k].ravel());unique,first,count=np.unique(a,return_index=True,return_counts=True);prob=(first+(count-1)/2+.5)/len(a)
   q[:,k]=np.quantile(y[near,k],np.interp(raw[t,:,k],unique,prob))
  qm.append(q)
 samples=couple(quantiles,np.asarray(templates),rng)
 pred={'Climatology':np.asarray(clim),'Raw':raw[test],'Quantile_mapping':np.asarray(qm),'Direct_EMOS':samples,'Bottom_up':bottomup(samples),'MinT_NN':project(samples,W)}
 linear=project(samples,W,False);b=np.maximum(linear[:,:,:4],0);pred['Clip_sum']=np.concatenate([b,b.sum(2,keepdims=True)],2);pred['Diagonal_NN']=project(samples,np.diag(np.diag(W)))
 if qc=='primary':
  _,_,q11=distribution(raw,y,dates,rec,test,11)
  ss11=couple(q11,np.asarray(templates11),rng);ecc=couple(q11,raw[test],rng)
  pred.update(Schaake11=ss11,Schaake11_BU=bottomup(ss11),Schaake11_NN=project(ss11,W),ECC11=ecc,ECC11_BU=bottomup(ecc),ECC11_NN=project(ecc,W))
  old=fit_records(raw,y,dates,train,key,qc,True);oldmean,oldexact,oldq=distribution(raw,y,dates,old,test,200);pred['Seasonal_EMOS']=oldq
 else:oldmean=np.empty((0,5));oldexact=np.empty((0,5))
 insample_mean,insample_exact,_=distribution(raw,y,dates,rec,train)
 # Full permitted seasonal empirical climatology: no sampling error in reference.
 climatology_crps=[];clim_brier=[]
 for i,t in enumerate(test):
  near=train[near_day(days[train],days[t])<=45];s=np.sort(y[near],axis=0);n=len(near);coef=(2*np.arange(1,n+1)-n-1)[:,None]
  climatology_crps.append(np.abs(s-y[t]).mean(0)-(s*coef).sum(0)/n**2)
  pp=(s>threshold[i]).mean(0);clim_brier.append((pp-(y[t]>threshold[i]))**2)
 G=np.linalg.solve(S.T@np.linalg.solve(W,S),S.T@np.linalg.inv(W));V=S@G@W@G.T@S.T
 np.savez_compressed(target,**pred,dates=dates[test].values,y=y[test],mean_exact=mean,crps_exact=exact,threshold=np.array(threshold),climatology_crps=climatology_crps,climatology_brier=clim_brier,mean_linear=project(mean,W,False),W=W,shrinkage=shrink,gain_predicted=1-V[4,4]/W[:4,:4].sum(),oof_index=oof_ix,oof_mean=oof_mean,train_index=train,insample_exact=insample_exact,legacy_exact=oldexact,legacy_mean=oldmean)
 metadata=dict(domain=key,year=year,qc=qc,excluded_years=excluded,train=train.tolist(),test=test.tolist(),inner=inner_metadata,records=rec,shrinkage=shrink,n_residuals=sum(len(e) for e in errors),min_eigenvalue=float(np.linalg.eigvalsh(W).min()),seconds=time.monotonic()-started)
 target.with_suffix('.json').write_text(json.dumps(metadata,indent=2))
 return f'{qc} {key} {year}: {len(train)} fit, {metadata["n_residuals"]} OOF, {metadata["seconds"]:.1f}s'

def main():
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=6);p.add_argument('--pilot',action='store_true');p.add_argument('--qc',default='primary');p.add_argument('--domain',default='all');args=p.parse_args()
 keys=list(REGIONS) if args.domain=='all' else [args.domain]
 qcs=['primary','positive','signed'] if args.qc=='all' else [args.qc]
 tasks=[(k,y,qc) for qc in qcs for y in range(2000,2020) for k in keys]
 if args.pilot:tasks=[('N',2010,args.qc)]
 print('CPUs',os.cpu_count(),'workers',args.workers,'tasks',len(tasks),flush=True)
 with ProcessPoolExecutor(max_workers=args.workers) as pool:
  futures=[pool.submit(run_fold,t) for t in tasks]
  for f in as_completed(futures):print(f.result(),flush=True)

if __name__=='__main__':main()
