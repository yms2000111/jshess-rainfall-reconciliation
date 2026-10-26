"""Northern support sensitivity using four exhaustive single-cell subdomains."""
from review_controls import *
from scipy.optimize import isotonic_regression

SUB={
 'N_SW':dict(name='Northern southwest cell',lon=(131.25,132.75),lat=(-15.75,-14.25),centres_lon=[132],centres_lat=[-15]),
 'N_SE':dict(name='Northern southeast cell',lon=(132.75,134.25),lat=(-15.75,-14.25),centres_lon=[133.5],centres_lat=[-15]),
 'N_NW':dict(name='Northern northwest cell',lon=(131.25,132.75),lat=(-14.25,-12.75),centres_lon=[132],centres_lat=[-13.5]),
 'N_NE':dict(name='Northern northeast cell',lon=(132.75,134.25),lat=(-14.25,-12.75),centres_lon=[133.5],centres_lat=[-13.5])}
REGIONS.update(SUB)
SDIR=REVIEW/'spatial';SDIR.mkdir(exist_ok=True)

def download_year(year):
 path=SDIR/f'agcd_{year}.npz'
 if path.exists():return f'AGCD {year} cached'
 import truststore;truststore.inject_into_ssl()
 import xarray as xr
 url=f'https://thredds.nci.org.au/thredds/dodsC/zv2/agcd/v1-0-1/precip/total/r005/01day/agcd_v1-0-1_precip_total_r005_daily_{year}.nc'
 ds=xr.open_dataset(url,engine='pydap');da=ds.precip.sel(lat=slice(-15.8,-12.7),lon=slice(131.2,134.3)).load()
 lat=da.lat.values.astype(float);lon=da.lon.values.astype(float);v=da.values.astype(float);valid=np.isfinite(v);v[~valid]=0;result=dict(time=ds.time.values)
 for key,bounds in dict(N=REGIONS['N'],**SUB).items():
  x0,x1=bounds['lon'];y0,y1=bounds['lat'];wx=np.maximum(0,np.minimum(lon+.025,x1)-np.maximum(lon-.025,x0));wy=np.maximum(0,np.sin(np.deg2rad(np.minimum(lat+.025,y1)))-np.sin(np.deg2rad(np.maximum(lat-.025,y0))));w=wy[:,None]*wx[None,:];den=(valid*w).sum((1,2));result[key]=(v*w).sum((1,2))/den
 np.savez_compressed(path,**result);path.with_suffix('.json').write_text(json.dumps(dict(source=url,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bounds=SUB),indent=2));ds.close();return f'AGCD {year} extracted'

def build():
 obs=[]
 for year in range(2000,2021):
  f=np.load(SDIR/f'agcd_{year}.npz');obs.append(pd.DataFrame({key:f[key] for key in ['N',*SUB]},index=pd.DatetimeIndex(f['time']).normalize()))
 daily=pd.concat(obs).sort_index();daily.to_csv(SDIR/'daily_observations.csv',index_label='date');original=pd.read_csv(ROOT/'data/processed/agcd_daily_regional_mm.csv',index_col=0,parse_dates=True)
 assert np.allclose(daily.N,original.reindex(daily.index).N,atol=1e-6)
 times=[];raw={key:[] for key in SUB}
 for path in sorted((ROOT/'data/ecmwf').glob('*.npz')):
  f=np.load(path);meta=json.loads(path.with_suffix('.json').read_text());a=f['cumulative'].astype(float);a[np.isnan(a)]=max(meta['fill']*meta['scale']+meta['add'],0)
  for key,r in SUB.items():
   iy=np.flatnonzero(np.isin(f['lat'],r['centres_lat']))[0];ix=np.flatnonzero(np.isin(f['lon'],r['centres_lon']))[0];cum=a[:,:,:,iy,ix].copy();week=np.diff(cum,axis=2,prepend=np.zeros_like(cum[:,:,:1]))
   for row,member in np.argwhere((week<0).any(2)):cum[row,member,:3]=np.clip(isotonic_regression(cum[row,member,:3]).x,0,cum[row,member,3])
   w=np.diff(cum,axis=2,prepend=np.zeros_like(cum[:,:,:1]));raw[key].append(np.concatenate([w,w.sum(2,keepdims=True)],axis=2))
  times.extend(f['times'].astype('datetime64[s]').astype('datetime64[D]'))
 dates=pd.DatetimeIndex(times);order=np.argsort(dates);dates=dates[order];original_data=np.load(ROOT/'data/processed/N.npz')
 assert np.array_equal(dates.values,original_data['dates'])
 for key in SUB:
  target=[]
  for origin in dates:
   w=daily[key].reindex(pd.date_range(origin+pd.Timedelta(days=1),periods=28)).values.reshape(4,7).sum(1);target.append(np.r_[w,w.sum()])
  np.savez_compressed(ROOT/f'data/processed/{key}.npz',dates=dates.values,raw=np.concatenate(raw[key])[order],y=target,climate=original_data['climate'])
 print('Four subdomains built; original N observation mean reproduced.',flush=True)

def fit(task):
 key,year=task;path=SDIR/f'{key}_{year}.npz'
 if path.exists():return f'{key} {year} cached'
 d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z=lagged_climate(dates,d);train=permitted(dates,[year-1,year,year+1]);test=np.flatnonzero(dates.year==year);pred={};metadata={}
 for kind in ['H0','H1','Weekly_climate_BU']:pred[kind],metadata[kind]=evaluate_variant(raw,y,dates,z,train,test,key,year,kind)
 rec=base_records(raw,y,dates,z,train,key,'primary');_,q=predict(raw,y,dates,z,rec,test,200);template,rng=templates_original(y,dates,train,test,key,year);q=couple7(q,template,rng);pred['Bottom_up']=q[:,:,:4]@S7.T
 np.savez_compressed(path,**pred,y=y[test],dates=dates[test].values);path.with_suffix('.json').write_text(json.dumps(dict(train=train.tolist(),test=test.tolist(),models=metadata),indent=2));return f'{key} {year} fitted'

def score():
 rows=[]
 for key in SUB:
  _,all_dates,all_raw,_=load_data(key,'primary')
  for year in range(2000,2020):
   f=np.load(SDIR/f'{key}_{year}.npz')
   for m in ['Raw','H0','H1','Weekly_climate_BU','Bottom_up']:
    c=crps(expand(all_raw[all_dates.year==year]) if m=='Raw' else f[m],f['y'])
    for j in [0,1,2,3,6]:rows.append(dict(domain=key,year=year,method=m,lead=NODES[j],crps=c[:,j].mean()))
 pd.DataFrame(rows).to_csv(SDIR/'annual_scores.csv',index=False)
 print(pd.DataFrame(rows).query("lead=='D28'").groupby(['domain','method']).crps.mean().to_string(),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--download',action='store_true');p.add_argument('--build',action='store_true');p.add_argument('--score',action='store_true');p.add_argument('--workers',type=int,default=4);p.add_argument('--year',type=int);a=p.parse_args()
 if a.download:
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(download_year,yr) for yr in ([a.year] if a.year else range(2000,2021))]):print(f.result(),flush=True)
 elif a.build:build()
 elif a.score:score()
 else:
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(fit,(key,yr)) for yr in range(2000,2020) for key in SUB]):print(f.result(),flush=True)
