"""Frozen 2020 forecast transfer, with predictions written before verification."""
from v5_new_experiments import combined
from coverage_extension import *
R=ROOT/'revision/review_v5/operational';F=R/'predictions';F.mkdir(exist_ok=True)
keys=['N','NE','SE','SW','NW','CA','EC','TAS']
for k in keys:REGIONS['OP_'+k]=REGIONS[k].copy()

def forecast_climate(dates):
 rmm=pd.read_csv(ROOT/'data/support/rmm_full.txt',sep=r'\s+',skiprows=2,header=None,usecols=range(7),names=['year','month','day','rmm1','rmm2','phase','amp']);rmm.index=pd.to_datetime(rmm[['year','month','day']])
 enso=pd.read_csv(ROOT/'data/support/nino34.txt',sep=r'\s+');enso.index=pd.to_datetime(dict(year=enso.YR,month=enso.MON,day=1))
 return np.column_stack([rmm.reindex(dates-pd.Timedelta(days=2))[['rmm1','rmm2']],enso.reindex(dates.to_period('M').to_timestamp()-pd.DateOffset(months=2))['NINO3.4']])

def build():
 audit=json.loads((R/'packing_audit/summary.json').read_text());assert audit['all_passed']
 dates=[];raw={k:[] for k in keys};qc=[]
 files=sorted((R/'raw').glob('*.npz'));assert len(files)==53
 for path in files:
  f=np.load(path);meta=json.loads(path.with_suffix('.json').read_text());a=f['cumulative'].astype(float);a[np.isnan(a)]=max(meta['fill']*meta['scale']+meta['add'],0)
  assert np.array_equal(f['members'],np.arange(11))
  for k in keys:
   r=REGIONS[k];iy=np.isin(f['lat'],r['centres_lat']);ix=np.isin(f['lon'],r['centres_lon']);assert iy.sum()==2 and ix.sum()==2
   w=np.broadcast_to(np.cos(np.deg2rad(f['lat'][iy]))[:,None],(2,2)).copy();w/=w.sum();cum=(a[:,:,:,iy,:][:,:,:,:,ix]*w).sum((-2,-1));inc=np.diff(cum,axis=2,prepend=np.zeros_like(cum[:,:,:1]))
   qc.extend(dict(domain=k,date=path.stem,week=j+1,negative=int((inc[:,:,j]<0).sum()),minimum=float(inc[:,:,j].min())) for j in range(4))
   for i,m in np.argwhere((inc<0).any(2)):cum[i,m,:3]=np.clip(isotonic_regression(cum[i,m,:3]).x,0,cum[i,m,3])
   inc=np.diff(cum,axis=2,prepend=np.zeros_like(cum[:,:,:1]));assert inc.min()>-1e-8;raw[k].append(np.concatenate([inc,inc.sum(2,keepdims=True)],2))
  dates.extend(f['times'].astype('datetime64[s]'))
 dates=pd.DatetimeIndex(dates);assert np.array_equal(dates.values,pd.date_range('2020-01-02','2020-12-31',freq='W-THU').values)
 for k in keys:np.savez_compressed(R/f'input_{k}.npz',dates=dates.values,raw=np.concatenate(raw[k]),climate=forecast_climate(dates))
 pd.DataFrame(qc).to_csv(R/'qc_by_week.csv',index=False);print('Inputs built without loading 2020 verification rainfall.',flush=True)

def fit(k):
 path=F/(k+'.npz')
 if path.exists():return k+' cached'
 d,dt,r5,y5=load_data(k,'primary');future=np.load(R/f'input_{k}.npz');ft=pd.DatetimeIndex(future['dates']);dates=dt.append(ft)
 raw=expand(np.concatenate([r5,future['raw']]));y=expand(np.concatenate([y5,np.zeros((len(ft),5))]));z=lagged_climate(dates,{'climate':np.concatenate([d['climate'],future['climate']])})
 train=np.flatnonzero((dates.year<=2019)&((dates+pd.Timedelta(days=28)).year<=2019));test=np.arange(len(dt),len(dates));key='OP_'+k
 assert (dates[train]+pd.Timedelta(days=28)).max()<pd.Timestamp('2020-01-01')
 pred={'Raw':raw[test]};meta={}
 for kind in ['H0','H1','Weekly_climate_BU']:
  pred[kind],meta[kind]=evaluate_variant(raw,y,dates,z,train,test,key,2020,kind)
 rec=base_records(raw,y,dates,z,train,key,'primary');_,q=predict(raw,y,dates,z,rec,test,200);template,rng=templates_original(y,dates,train,test,key,2020);q=couple7(q,template,rng);pred['Bottom_up']=q[:,:,:4]@S7.T
 for kind in ['Hweekly','H2']:
  rec=combined(raw,y,dates,z,train,key,kind);_,q=predict(raw,y,dates,z,rec,test,200);template,rng=templates_original(y,dates,train,test,key,2020);samples=couple7(q,template,rng);errors=[]
  for fit_ix,val,_ in inner_splits(dates,train):
   rr=combined(raw,y,dates,z,fit_ix,key,kind);mm,_=predict(raw,y,dates,z,rr,val);errors.append(y[val]-mm)
  W,lam=shrink(np.concatenate(errors));pred[kind]=reconcile(samples,W,S7);meta[kind]=dict(records=rec,W=W.tolist(),shrinkage=lam)
 for m,a in pred.items():assert np.isfinite(a).all() and a.min()>=0 and np.allclose(a[:,:,:4]@S7.T,a,atol=1e-7),m
 scale=float(crps(raw[train],y[train])[:,6].mean())
 np.savez_compressed(path,**pred,dates=ft.values,normalisation_raw_training_crps=scale)
 path.with_suffix('.json').write_text(json.dumps(dict(training_dates=[str(v.date()) for v in dates[train]],models=meta,normalisation_raw_training_crps=scale,verification_observations_loaded=False),indent=2));return k+' forecasts frozen'

def score():
 assert all((F/(k+'.npz')).exists() for k in keys)
 daily=pd.read_csv(ROOT/'data/processed/agcd_daily_regional_mm.csv',index_col=0,parse_dates=True).join(pd.read_csv(ROOT/'revision/review_v4/coverage/daily_observations.csv',index_col=0,parse_dates=True))
 future=np.load(R/'2021.npz');daily=pd.concat([daily,pd.DataFrame({k:future[k] for k in keys},index=pd.DatetimeIndex(future['time']).normalize())]).sort_index();assert not daily.index.duplicated().any()
 rows=[];norm={}
 for k in keys:
  f=np.load(F/(k+'.npz'));dates=pd.DatetimeIndex(f['dates']);obs=[]
  for d in dates:
   w=daily[k].reindex(pd.date_range(d+pd.Timedelta(days=1),periods=28)).values.reshape(4,7).sum(1);obs.append(np.r_[w,w.sum()])
  y=expand(np.asarray(obs));assert np.isfinite(y).all();norm[k]=float(f['normalisation_raw_training_crps'])
  for m in ['Raw','Bottom_up','Weekly_climate_BU','H0','H1','Hweekly','H2']:
   c=crps(f[m],y)
   for j in [0,1,2,3,6]:rows.extend(dict(domain=k,date=str(d.date()),method=m,lead=NODES[j],crps=float(c[i,j])) for i,d in enumerate(dates))
 a=pd.DataFrame(rows);a.to_csv(R/'case_scores.csv',index=False);a.groupby(['domain','method','lead']).crps.mean().reset_index().to_csv(R/'scores.csv',index=False)
 seq=[]
 for k in keys:
  t=a.query('domain==@k and lead=="D28"').pivot(index='date',columns='method',values='crps').sort_index();seq.append((t.H1-t.Weekly_climate_BU).values/norm[k]*100)
 seq=np.array(seq);d=seq.mean(0);out=[]
 for block in [4,6,8]:
  starts=np.random.default_rng(2026102520+block).integers(0,53,(50000,int(np.ceil(53/block))));ix=((starts[:,:,None]+np.arange(block))%53).reshape(50000,-1)[:,:53];lo,hi=np.quantile(d[ix].mean(1),[.025,.975])
  out.append(dict(block_length=block,delta=d.mean(),lower=lo,upper=hi,favourable_domains=int((seq.mean(1)<0).sum()),success=bool(d.mean()<0 and hi<0)))
 pd.DataFrame(out).to_csv(R/'confirmatory_contrast.csv',index=False);print(pd.DataFrame(out).to_string(index=False));print(a.query('lead=="D28"').groupby(['domain','method']).crps.mean().to_string())

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['build','fit','score']);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
 if a.action=='build':build()
 elif a.action=='score':score()
 else:
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(fit,k) for k in keys]):print(f.result(),flush=True)
