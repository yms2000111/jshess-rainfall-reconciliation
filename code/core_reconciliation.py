"""EMOS dependence coupling, bottom-up and full-covariance nonnegative reconciliation.
All arrays store W1,W2,W3,W4,D28; the manuscript displays the permuted total-first form.
Uses frozen pre-2013 EMOS fits and independent 2013-14 covariance calibration.
"""
from common import *
import numpy as np,pandas as pd,json,itertools
from scipy.stats import gamma
from scipy.special import gammainc
from analyse import crps,bh,SEED,LEADS,distance
OUT=ROOT/'results';S=np.vstack([np.eye(4),np.ones(4)])

def covariance_shrink(errors):
 e=errors-errors.mean(0);sd=np.maximum(e.std(0,ddof=0),.1);z=e/sd;n=len(z)
 r=z.T@z/n;products=z[:,:,None]*z[:,None,:]
 var_r=np.mean((products-r)**2,axis=0)/n
 off=~np.eye(5,dtype=bool)
 lam=float(np.clip(var_r[off].sum()/max((r[off]**2).sum(),1e-12),0,1))
 corr=(1-lam)*r+lam*np.eye(5)
 W=corr*sd[:,None]*sd[None,:]+np.diag(sd**2)*1e-8
 return W,lam

def project(v,W,nonnegative=True):
 """Enumerate the 16 faces of the four-dimensional nonnegative cone."""
 a=np.asarray(v);flat=a.reshape(-1,5);Q=np.linalg.inv(W);H=S.T@Q@S;rhs=flat@Q@S
 if not nonnegative:
  b=rhs@np.linalg.inv(H);return (b@S.T).reshape(a.shape)
 best=np.zeros((len(flat),4));cost=np.full(len(flat),np.inf)
 for bits in itertools.product([False,True],repeat=4):
  ix=np.flatnonzero(bits);b=np.zeros_like(best)
  if len(ix):b[:,ix]=np.linalg.solve(H[np.ix_(ix,ix)],rhs[:,ix].T).T
  good=(b>=-1e-9).all(1);b=np.maximum(b,0);res=b@S.T-flat;c=np.einsum('ni,ij,nj->n',res,Q,res)
  take=good&(c<cost);best[take]=b[take];cost[take]=c[take]
 return (best@S.T).reshape(a.shape)

def emos_distribution(raw,dates,records,ix):
 season=(dates.month.to_numpy()%12)//3;n=len(ix);out=np.zeros((n,200,5));mean=np.zeros((n,5))
 p=(np.arange(200)+.5)/200
 for rec in records:
  s,k=rec['season'],rec['lead'];q=np.flatnonzero(season[ix]==s);sc=rec['scale_mm'];a,b,c,d,delta=rec['parameters']
  x=raw[ix[q],:,k].mean(1)/sc;mu=a+b*x;var=c+d*x;shape=mu*mu/var;theta=var/mu
  out[q,:,k]=np.maximum(gamma.ppf(p[None,:],shape[:,None],scale=theta[:,None])-delta,0)*sc
  mean[q,k]=(mu*(1-gammainc(shape+1,delta/theta))-delta*(1-gammainc(shape,delta/theta)))*sc
 return out,mean

def run():
 scores=pd.read_csv(OUT/'scores.csv');cases=pd.read_csv(OUT/'case_scores.csv');scores=scores[~scores.method.str.startswith('EMOS') & (scores.method!='CSG EMOS')];cases=cases[~cases.method.str.startswith('EMOS') & (cases.method!='CSG EMOS')]
 rows=[];case_rows=[];comparisons=[];sensitivity=[]
 for key in REGIONS:
  d=np.load(ROOT/f'data/processed/{key}.npz');dates=pd.DatetimeIndex(d['dates']);end=dates+pd.Timedelta(days=28);raw=d['raw'];y=d['y'];fit=np.flatnonzero(end<pd.Timestamp('2013-01-01'));cal=np.flatnonzero((dates>=pd.Timestamp('2013-01-01'))&(end<pd.Timestamp('2015-01-01')));test=np.flatnonzero(dates>=pd.Timestamp('2015-01-01'))
  rec=json.loads((OUT/f'{key}_emos_fit.json').read_text());sorted_samples,mean=emos_distribution(raw,dates,rec,test);_,calmean=emos_distribution(raw,dates,rec,cal)
  errors=y[cal]-calmean;W,lam=covariance_shrink(errors);rng=np.random.default_rng(SEED+31);samples=np.empty_like(sorted_samples);independent=np.empty_like(samples)
  for i,t in enumerate(test):
   near=fit[distance(dates[t].dayofyear,dates[fit].dayofyear).ravel()<=45];template=y[rng.choice(near,200,replace=True)]
   for k in range(5):
    order=np.lexsort((rng.random(200),template[:,k]));samples[i,order,k]=sorted_samples[i,:,k];independent[i,:,k]=sorted_samples[i,rng.permutation(200),k]
  bu=samples.copy();bu[:,:,4]=bu[:,:,:4].sum(2);linear=project(samples,W,False);clipped=np.maximum(linear[:,:,:4],0);clipped=np.concatenate([clipped,clipped.sum(2,keepdims=True)],2)
  pred={'CSG EMOS':samples,'EMOS bottom-up':bu,'EMOS MinT-NN':project(samples,W),'EMOS diagonal-NN':project(samples,np.diag(np.diag(W))),'EMOS clip-sum':clipped,'EMOS independent-NN':project(independent,W)}
  archive=dict(np.load(OUT/f'{key}_predictions.npz'));archive.update({m.replace(' ','_'):v for m,v in pred.items()});np.savez_compressed(OUT/f'{key}_predictions.npz',**archive)
  obs=y[test];threshold=archive['threshold'];clim=archive['Climatology'];ref=crps(clim,obs);allc={m:crps(a,obs) for m,a in pred.items()};year=dates[test].year.to_numpy();years=np.unique(year);draw=np.random.default_rng(SEED+9).choice(years,(5000,len(years)),replace=True)
  for method,ens in pred.items():
   c=allc[method];fc=crps(ens,obs,True);avg=ens.mean(1);err=avg-obs;p=(ens>threshold[:,None,:]).mean(1);event=obs>threshold;bs=(p-event)**2;lo,hi=np.quantile(ens,[.1,.9],axis=1);cover=((obs>=lo)&(obs<=hi));bref=((clim>threshold[:,None,:]).mean(1)-event)**2
   for k,lead in enumerate(LEADS):
    row=dict(region=key,method=method,lead=lead,n=len(test),crps=c[:,k].mean(),fair_crps=fc[:,k].mean(),crpss=1-c[:,k].mean()/ref[:,k].mean(),rmse=np.mean(err[:,k]**2)**.5,mae=np.abs(err[:,k]).mean(),bias=err[:,k].mean(),coverage80=cover[:,k].mean(),width80=(hi[:,k]-lo[:,k]).mean(),coherence_mae=np.abs(ens[:,:,4]-ens[:,:,:4].sum(2)).mean(),brier=bs[:,k].mean(),bss=1-bs[:,k].mean()/bref[:,k].mean());rows.append(row)
    for i,t in enumerate(test):case_rows.append(dict(region=key,method=method,lead=lead,date=str(dates[t].date()),observed=obs[i,k],mean=avg[i,k],crps=c[i,k],brier=bs[i,k],probability=p[i,k],event=int(event[i,k]),threshold=threshold[i,k],lower80=lo[i,k],upper80=hi[i,k],rmm_amp=float(np.hypot(*d['climate'][t,:2])),nino_anomaly=d['enso_anom'][t],qc_max_decrease=d['qc_max_decrease'][t]))
   for shift,ys in [(-1,d['y_shift_minus'][test]),(1,d['y_shift_plus'][test])]:
    for k,lead in enumerate(LEADS):sensitivity.append(dict(region=key,method=method,lead=lead,shift_days=shift,crps=crps(ens,ys)[:,k].mean()))
  for base in ['CSG EMOS','EMOS bottom-up']:
   diff=allc['EMOS MinT-NN']-allc[base]
   for k,lead in enumerate(LEADS):
    annual={yr:diff[year==yr,k].mean() for yr in years};boot=np.array([[annual[yr] for yr in dr] for dr in draw]).mean(1);lower,upper=np.quantile(boot,[.025,.975]);p=(1+np.sum(np.abs(boot-diff[:,k].mean())>=abs(diff[:,k].mean())))/(len(boot)+1)
    comparisons.append(dict(region=key,baseline=base,lead=lead,delta_crps=diff[:,k].mean(),lower=lower,upper=upper,p=p,years=5))
  (OUT/f'{key}_covariance.json').write_text(json.dumps(dict(shrinkage=lam,W_mm2=W.tolist(),calibration_n=len(cal),min_eigenvalue=float(np.linalg.eigvalsh(W).min()),negative_linear_fraction=float((linear[:,:,:4]<0).mean()),sample_order=LEADS),indent=2))
  print(key,'shrinkage',round(lam,4),'D28', {m:round(allc[m][:,4].mean(),3) for m in pred},flush=True)
 pd.concat([scores,pd.DataFrame(rows)],ignore_index=True).to_csv(OUT/'scores.csv',index=False);pd.concat([cases,pd.DataFrame(case_rows)],ignore_index=True).to_csv(OUT/'case_scores.csv',index=False)
 comp=pd.DataFrame(comparisons);comp['q']=bh(comp.p);comp.to_csv(OUT/'core_comparisons.csv',index=False);pd.DataFrame(sensitivity).to_csv(OUT/'core_date_sensitivity.csv',index=False)

if __name__=='__main__':run()
