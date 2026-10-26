"""Exploratory controls requested in the second review; resumable, purged fits."""
from extension_cv import *
from analyse import crps
import urllib.parse

REVIEW=OUT/'review_v3';REVIEW.mkdir(exist_ok=True)
RCACHE=REVIEW/'cache';RCACHE.mkdir(exist_ok=True)
RFOLDS=REVIEW/'folds';RFOLDS.mkdir(exist_ok=True)
GROUPS={'MJO':[0,1],'ENSO':[2],'DMI':[3],'SAM':[4]}

def lagged_climate(dates,data,lag=2):
 if lag==2:return climate(dates,data)[0]
 months=dates.to_period('M').to_timestamp()-pd.DateOffset(months=lag)
 ni=np.loadtxt(ROOT/'data/support/nino34.txt',skiprows=1)
 nd={pd.Timestamp(int(r[0]),int(r[1]),1):r[8] for r in ni}
 dm=pd.read_csv(ROOT/'data/support/dmi.csv',index_col=0);dm.index=pd.to_datetime(dm.index)
 txt=(ROOT/'data/support/sam_web_snapshot.txt').read_text(encoding='utf-8')
 rows=re.findall(r'(?<!\d)(19\d{2}|20\d{2})\s+((?:[+-]?\d+\.\d+\s+){11}[+-]?\d+\.\d+)',txt)
 sam={pd.Timestamp(int(yr),m,1):float(v) for yr,row in rows for m,v in enumerate(row.split(),1)}
 z=np.column_stack([data['climate'][:,:2],[nd[t] for t in months],dm.reindex(months).iloc[:,0].values,[sam[t] for t in months]])
 assert np.isfinite(z).all() and ((months+pd.offsets.MonthEnd(0))<dates).all()
 return z

def base_records(raw,y,dates,z,train,key,qc):
 b=fit_records(raw[...,[0,1,2,3,6]],y[:,[0,1,2,3,6]],dates,train,key,qc)
 a=records_extended(raw,y,dates,z,train,key,qc)
 return [dict(r,lead=r['lead']) for r in b if r['lead']<4]+[dict(r) for r in a]

def placebo_values(z,dates,train,rep):
 # Permute year blocks only inside this particular fitting set; use closest
 # calendar dates in the donor year if boundary embargoes shorten a year.
 out=z.copy();years=np.unique(dates[train].year)
 seed=int(hashlib.sha256(train.tobytes()+bytes([rep])).hexdigest()[:8],16)
 rng=np.random.default_rng(seed);donor=years.copy()
 for _ in range(100):
  rng.shuffle(donor)
  if (donor!=years).all():break
 if (donor==years).any():donor=np.roll(years,1)
 days=calendar_day(dates)
 for yy,dd in zip(years,donor):
  to=train[dates[train].year==yy];fr=train[dates[train].year==dd]
  source=fr[np.argmin(near_day(days[to,None],days[fr][None,:]),axis=1)]
  out[to]=z[source]
 return out

def adjusted_records(raw,y,dates,z,train,key,kind,qc='primary'):
 stamp=hashlib.sha256(('review-controls-v1'+key+kind+qc).encode()+train.tobytes()+z.tobytes()).hexdigest()[:28]
 path=RCACHE/(stamp+'.json')
 if path.exists():return json.loads(path.read_text())
 rec=base_records(raw,y,dates,z,train,key,qc);days=calendar_day(dates)
 zz=placebo_values(z,dates,train,int(kind[-1])) if kind.startswith('Placebo') else z
 indices=GROUPS.get(kind,list(range(5)))
 changed=range(4) if kind=='Weekly_climate_BU' else range(4,7)
 for r in rec:
  k=r['lead'];r['adjusted']=k in changed and kind!='H0'
  if not r['adjusted']:continue
  tr=train[near_day(days[train],pd.Timestamp(2000,r['group'],15).dayofyear)<=45]
  sc=r['scale_mm'];mu,var,de=moments(r['parameters'],raw[tr,:,k].mean(1)/sc,raw[tr,:,k].var(1,ddof=1)/sc**2);obs=y[tr,k]/sc
  zm=zz[tr].mean(0);zs=np.maximum(zz[tr].std(0),1e-6)
  design=np.ones((len(tr),1)) if kind=='Intercept' else ((zz[tr]-zm)/zs)[:,indices]
  def objective(beta):return float(csg_crps(obs,mu*np.exp(design@beta),var,de).mean()+.05*np.sum(beta**2))
  result=minimize(objective,np.zeros(design.shape[1]),method='L-BFGS-B',bounds=[(-1,1)]*design.shape[1],options={'maxiter':150,'ftol':2e-9,'gtol':1e-5,'maxls':30})
  if not result.success:result=minimize(objective,result.x,method='L-BFGS-B',bounds=[(-1,1)]*design.shape[1],options={'maxiter':500,'ftol':2e-10,'gtol':1e-6,'maxls':40})
  r.update(control_beta=result.x.tolist(),control_mean=zm.tolist(),control_sd=zs.tolist(),indices=indices,intercept=kind=='Intercept',success=bool(result.success),identity_loss=objective(np.zeros(design.shape[1])),fitted_loss=float(result.fun))
 path.write_text(json.dumps(rec,indent=2));return rec

def predict(raw,y,dates,z,rec,ix,size=None):
 mean=np.zeros((len(ix),7));q=None if size is None else np.zeros((len(ix),size,7))
 for r in rec:
  loc=np.flatnonzero(dates[ix].month==r['group']);ids=ix[loc];k=r['lead'];sc=r['scale_mm']
  if not len(loc):continue
  mu,var,de=moments(r['parameters'],raw[ids,:,k].mean(1)/sc,raw[ids,:,k].var(1,ddof=1)/sc**2)
  if r.get('adjusted'):
   design=np.ones((len(ids),1)) if r['intercept'] else ((z[ids]-r['control_mean'])/r['control_sd'])[:,r['indices']]
   mu*=np.exp(design@r['control_beta'])
  mean[loc,k]=mean_csg(mu,var,de)*sc
  if size is not None:q[loc,:,k]=np.maximum(gamma.ppf(((np.arange(size)+.5)/size)[None,:],(mu*mu/var)[:,None],scale=(var/mu)[:,None])-de,0)*sc
 return mean,q

def evaluate_variant(raw,y,dates,z,train,test,key,year,kind,qc='primary',forward=False):
 rec=adjusted_records(raw,y,dates,z,train,key,kind,qc);mean,q=predict(raw,y,dates,z,rec,test,200)
 template,rng=templates_original(y,dates,train,test,key,year);samples=couple7(q,template,rng)
 if kind=='Weekly_climate_BU':return samples[:,:,:4]@S7.T,dict(records=rec)
 errors=[]
 for fit,val,_ in inner_splits(dates,train):
  rr=adjusted_records(raw,y,dates,z,fit,key,kind,qc);mm,_=predict(raw,y,dates,z,rr,val)
  errors.append(y[val]-mm)
 W,lam=shrink(np.concatenate(errors));out=reconcile(samples,W,S7)
 return out,dict(records=rec,W=W.tolist(),shrinkage=lam)

def run(task):
 key,year=task;path=RFOLDS/f'{key}_{year}.npz'
 if path.exists():return f'{key} {year} cached'
 started=time.monotonic();d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z=lagged_climate(dates,d)
 old=np.load(EFOLDS/f'{key}_{year}.npz');train=old['train_index'];test=np.flatnonzero(dates.year==year)
 kinds=['Weekly_climate_BU','Intercept']
 if key=='N':kinds+=['MJO','ENSO','DMI','SAM','Placebo1','Placebo2','Placebo3','Lag1']
 preds={};meta={}
 for kind in kinds:
  zz=lagged_climate(dates,d,1) if kind=='Lag1' else z
  preds[kind],meta[kind]=evaluate_variant(raw,y,dates,zz,train,test,key,year,kind)
 # The full factorial dependence control uses common, matched-size quantiles.
 base=base_records(raw,y,dates,z,train,key,'primary')
 templates,rng=templates_original(y,dates,train,test,key,year,11)
 for h in ['H0','H1']:
  _,_,q=distributions(raw,y,dates,z,records_extended(raw,y,dates,z,train,key),test,11,h=='H1')
  _,_,wq=distribution(r5,y5,dates,fit_records(r5,y5,dates,train,key,'primary'),test,11);q[:,:,:4]=wq[:,:,:4]
  for dep,template in [('ECC',raw[test]),('Schaake',templates)]:
   rr=np.random.default_rng(SEED+year);samples=couple7(q,template,rr)
   preds[h+'_'+dep+'_NN']=reconcile(samples,old[h+'_7_W'],S7)
   if h=='H0':preds[dep+'_BU']=samples[:,:,:4]@S7.T
 if key=='N':
  for qc in ['positive','signed']:
   _,_,rqc,_=load_data(key,qc);rqc=expand(rqc)
   for h in ['H0','H1']:
    name=h+'_'+qc;preds[name],meta[name]=evaluate_variant(rqc,y,dates,z,train,test,key,year,h,qc)
   # Each QC branch has its own unaltered calibrated weekly reference.
   rec=base_records(rqc,y,dates,z,train,key,qc);_,q=predict(rqc,y,dates,z,rec,test,200)
   template,rng=templates_original(y,dates,train,test,key,year);q=couple7(q,template,rng)
   preds[qc+'_BU']=q[:,:,:4]@S7.T
 for name,a in preds.items():
  assert np.isfinite(a).all() and a.min()>=0,name
  assert np.allclose(a[:,:,:4]@S7.T,a,atol=1e-7),name
 np.savez_compressed(path,**preds,y=old['y'],dates=old['dates'],threshold90=old['threshold90'],reference=old['reference'])
 path.with_suffix('.json').write_text(json.dumps(dict(domain=key,year=year,train=train.tolist(),test=test.tolist(),models=meta,seconds=time.monotonic()-started),indent=2))
 return f'{key} {year}: {len(preds)} controls, {time.monotonic()-started:.1f}s'

def forward(key):
 path=RFOLDS/f'forward_{key}.npz'
 if path.exists():return f'forward {key} cached'
 d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z=lagged_climate(dates,d)
 train=np.flatnonzero((dates.year<=2014)&((dates+pd.Timedelta(days=28)).year<=2014));test=np.flatnonzero(dates.year>=2015)
 pred={'Raw':raw[test]};meta={}
 for kind in ['H0','H1','Weekly_climate_BU']:
  pred[kind],meta[kind]=evaluate_variant(raw,y,dates,z,train,test,key,2015,kind,forward=True)
 rec=base_records(raw,y,dates,z,train,key,'primary');_,q=predict(raw,y,dates,z,rec,test,200);template,rng=templates_original(y,dates,train,test,key,2015);q=couple7(q,template,rng);pred['Bottom_up']=q[:,:,:4]@S7.T
 np.savez_compressed(path,**pred,y=y[test],dates=dates[test].values)
 path.with_suffix('.json').write_text(json.dumps(dict(train=train.tolist(),test=test.tolist(),models=meta),indent=2));return f'forward {key} complete'

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=4);p.add_argument('--pilot',action='store_true');p.add_argument('--forward',action='store_true');a=p.parse_args()
 tasks=[('N',2010)] if a.pilot else [(k,yr) for yr in range(2000,2020) for k in REGIONS]
 with ProcessPoolExecutor(max_workers=a.workers) as pool:
  futures=[pool.submit(forward,k) for k in REGIONS] if a.forward else [pool.submit(run,t) for t in tasks]
  for f in as_completed(futures):print(f.result(),flush=True)
