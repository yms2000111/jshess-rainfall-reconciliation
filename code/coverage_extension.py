"""Prespecified four-domain geographic extension; no score-based selection."""
from review_controls import *
from scipy.optimize import isotonic_regression

NEW={
 'NW':dict(name='Western Kimberley',lon=(123.75,126.75),lat=(-18.75,-15.75),centres_lon=[124.5,126],centres_lat=[-18,-16.5]),
 'CA':dict(name='Central interior',lon=(132.75,135.75),lat=(-27.75,-24.75),centres_lon=[133.5,135],centres_lat=[-27,-25.5]),
 'EC':dict(name='Eastern coastal domain',lon=(149.25,152.25),lat=(-33.75,-30.75),centres_lon=[150,151.5],centres_lat=[-33,-31.5]),
 'TAS':dict(name='Tasmania',lon=(144.75,147.75),lat=(-44.25,-41.25),centres_lon=[145.5,147],centres_lat=[-43.5,-42])}
REGIONS.update(NEW)
V4=ROOT/'revision/review_v4';V4.mkdir(exist_ok=True)
CDIR=V4/'coverage';CDIR.mkdir(exist_ok=True)

def download(year):
 import download_agcd as ag
 ag.OUT=CDIR
 ag.REGIONS=NEW
 return ag.year_task(year)

def build():
 frames=[]
 for year in range(2000,2021):
  f=np.load(CDIR/f'{year}.npz')
  frames.append(pd.DataFrame({k:f[k] for k in NEW},index=pd.DatetimeIndex(f['time']).normalize()))
 daily=pd.concat(frames).sort_index();assert not daily.index.duplicated().any()
 assert np.isfinite(daily.values).all()
 daily.to_csv(CDIR/'daily_observations.csv',index_label='date')
 dates=[];raw={k:[] for k in NEW};qc=[]
 for path in sorted((ROOT/'data/ecmwf').glob('*.npz')):
  f=np.load(path);meta=json.loads(path.with_suffix('.json').read_text());a=f['cumulative'].astype(float)
  a[np.isnan(a)]=max(meta['fill']*meta['scale']+meta['add'],0)
  for k,r in NEW.items():
   iy=np.isin(f['lat'],r['centres_lat']);ix=np.isin(f['lon'],r['centres_lon'])
   assert iy.sum()==2 and ix.sum()==2
   w=np.broadcast_to(np.cos(np.deg2rad(f['lat'][iy]))[:,None],(2,2)).copy();w/=w.sum()
   cum=(a[:,:,:,iy,:][:,:,:,:,ix]*w).sum((-2,-1));inc=np.diff(cum,axis=2,prepend=np.zeros_like(cum[:,:,:1]))
   qc.append(dict(domain=k,file=path.stem,negative=int((inc<0).sum()),minimum=float(inc.min())))
   for i,m in np.argwhere((inc<0).any(2)):
    cum[i,m,:3]=np.clip(isotonic_regression(cum[i,m,:3]).x,0,cum[i,m,3])
   inc=np.diff(cum,axis=2,prepend=np.zeros_like(cum[:,:,:1]));assert inc.min()>=-1e-8
   raw[k].append(np.concatenate([inc,inc.sum(2,keepdims=True)],2))
  dates.extend(f['times'].astype('datetime64[s]').astype('datetime64[D]'))
 dates=pd.DatetimeIndex(dates);order=np.argsort(dates);dates=dates[order]
 original=np.load(ROOT/'data/processed/N.npz');assert np.array_equal(dates.values,original['dates'])
 for k in NEW:
  target=[]
  for d in dates:
   week=daily[k].reindex(pd.date_range(d+pd.Timedelta(days=1),periods=28)).values.reshape(4,7).sum(1)
   target.append(np.r_[week,week.sum()])
  target=np.asarray(target);assert np.isfinite(target).all() and target.min()>=0
  np.savez_compressed(ROOT/f'data/processed/{k}.npz',dates=dates.values,raw=np.concatenate(raw[k])[order],y=target,climate=original['climate'])
 pd.DataFrame(qc).to_csv(CDIR/'quality_control.csv',index=False)
 (CDIR/'domains.json').write_text(json.dumps(NEW,indent=2))
 print('Built all four new domains with 1060 matched origins.',flush=True)

def fit(task):
 key,year=task;path=CDIR/f'{key}_{year}.npz'
 if path.exists():return f'{key} {year} cached'
 start=time.monotonic();d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z=lagged_climate(dates,d)
 train=permitted(dates,[year-1,year,year+1]);test=np.flatnonzero(dates.year==year)
 pred={'Raw':raw[test]};meta={}
 for kind in ['H0','H1','Weekly_climate_BU']:
  pred[kind],meta[kind]=evaluate_variant(raw,y,dates,z,train,test,key,year,kind)
 rec=base_records(raw,y,dates,z,train,key,'primary');_,q=predict(raw,y,dates,z,rec,test,200)
 template,rng=templates_original(y,dates,train,test,key,year);q=couple7(q,template,rng);pred['Bottom_up']=q[:,:,:4]@S7.T
 for name,a in pred.items():
  assert np.isfinite(a).all() and a.min()>=-1e-8,name
  assert np.allclose(a[:,:,:4]@S7.T,a,atol=1e-7),name
 np.savez_compressed(path,**pred,y=y[test],dates=dates[test].values)
 path.with_suffix('.json').write_text(json.dumps(dict(train=train.tolist(),test=test.tolist(),models=meta,seconds=time.monotonic()-start),indent=2))
 return f'{key} {year} completed {time.monotonic()-start:.1f}s'

def score():
 rows=[]
 for k in NEW:
  for year in range(2000,2020):
   f=np.load(CDIR/f'{k}_{year}.npz')
   for m in ['Raw','Bottom_up','H0','H1','Weekly_climate_BU']:
    c=crps(f[m],f['y'])
    for j in [0,1,2,3,6]:rows.append(dict(domain=k,method=m,year=year,lead=NODES[j],crps=float(c[:,j].mean())))
 a=pd.DataFrame(rows);a.to_csv(CDIR/'annual_scores.csv',index=False)
 draw=np.random.default_rng(SEED+31).integers(0,20,(20000,20));out=[]
 for k in NEW:
  for lead in ['W1','W2','W3','W4','D28']:
   t=a.query('domain==@k and lead==@lead').pivot(index='year',columns='method',values='crps')
   for b in ['Raw','H0','Bottom_up','Weekly_climate_BU']:
    d=(t.H1-t[b]).values;lo,hi=np.quantile(d[draw].mean(1),[.025,.975]);out.append(dict(domain=k,lead=lead,baseline=b,delta=float(d.mean()),lower=lo,upper=hi,better_years=int((d<0).sum())))
 pd.DataFrame(out).to_csv(CDIR/'comparisons.csv',index=False)
 print(a.query("lead=='D28'").groupby(['domain','method']).crps.mean().to_string(),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['download','build','fit','score']);p.add_argument('--workers',type=int,default=4);p.add_argument('--pilot',action='store_true');a=p.parse_args()
 if a.action=='build':build()
 elif a.action=='score':score()
 else:
  jobs=[2000] if a.pilot else list(range(2000,2021))
  if a.action=='fit':jobs=[('NW',2010)] if a.pilot else [(k,y) for y in range(2000,2020) for k in NEW]
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(download if a.action=='download' else fit,t) for t in jobs]):print(f.result(),flush=True)
