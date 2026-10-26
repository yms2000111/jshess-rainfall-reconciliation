"""Extract Australia from public, contiguous ECMWF challenge NetCDF files.
Only selected cumulative horizons are transferred. Original packed bytes are decoded
using per-file metadata; HTTP range lengths and identities are verified.
"""
import sys,pathlib,time,threading,json,concurrent.futures,hashlib,datetime,argparse
ROOT=pathlib.Path(__file__).resolve().parents[1]; sys.path.append(str(ROOT/'_deps'))
import truststore; truststore.inject_into_ssl()
import numpy as np,pandas as pd,h5py,fsspec,requests
OUT=ROOT/'data/ecmwf'; OUT.mkdir(parents=True,exist_ok=True)
BASE='https://object-store.os-api.cci1.ecmwf.int/s2s-ai-challenge/data/training-input/0.3.0/netcdf/'
local=threading.local()
def getrange(url,a,b):
 if not hasattr(local,'s'): local.s=requests.Session()
 for attempt in range(6):
  try:
   r=local.s.get(url,headers={'Range':f'bytes={a}-{b}'},timeout=60)
   r.raise_for_status()
   if r.status_code!=206 or len(r.content)!=b-a+1:raise ValueError(f'Bad range {r.status_code} {len(r.content)}')
   if not r.headers['Content-Range'].startswith(f'bytes {a}-{b}/'):raise ValueError('Wrong range')
   return r.content
  except Exception:
   if attempt==5:raise
   time.sleep(1+attempt)
def metadata(date):
 url=BASE+f'ecmwf-hindcast-tp-{date}.nc'
 with fsspec.open(url,block_size=65536,cache_type='blockcache').open() as f:
  with h5py.File(f,'r') as h:
   d=h['tp']; assert d.chunks is None and d.dtype==np.dtype('int16')
   return dict(url=url,offset=int(d.id.get_offset()),shape=d.shape,
      scale=float(d.attrs['scale_factor'][0]),add=float(d.attrs['add_offset'][0]),
      fill=int(d.attrs['_FillValue'][0]),lat=h['latitude'][:],lon=h['longitude'][:],
      times=h['forecast_time'][:],leads=h['lead_time'][:],members=h['realization'][:])
def run_date(date,workers=32):
 dest=OUT/f'{date}.npz'
 if dest.exists(): print('cached',date,flush=True);return
 t=time.time();meta=metadata(date)
 yi=np.where((meta['lat']>=-45)&(meta['lat']<=-9))[0]
 xi=np.where((meta['lon']>=111)&(meta['lon']<=156))[0]
 nmem,nyear,nlead,nlat,nlon=meta['shape']; leads=[7,14,21,28]
 arr=np.full((nyear,nmem,4,len(yi),len(xi)),np.nan,np.float32)
 def task(idx):
  y,m,k=idx; l=int(np.flatnonzero(meta['leads']==leads[k]*24)[0])
  a=meta['offset']+((((m*nyear+y)*nlead+l)*nlat+yi[0])*nlon)*2
  raw=np.frombuffer(getrange(meta['url'],a,a+len(yi)*nlon*2-1),dtype='<i2').reshape(len(yi),nlon)[:,xi]
  v=raw.astype(np.float64)*meta['scale']+meta['add']; v[raw==meta['fill']]=np.nan
  v[np.isfinite(v)&(v<0)&(v>-meta['scale'])]=0
  return idx,v
 jobs=[(y,m,k) for y in range(nyear) for m in range(nmem) for k in range(4)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
  for idx,v in pool.map(task,jobs):arr[idx]=v
 np.savez_compressed(dest,cumulative=arr,times=meta['times'],lat=meta['lat'][yi],lon=meta['lon'][xi],members=meta['members'],leads=np.array(leads))
 audit={k:v for k,v in meta.items() if k not in ['lat','lon','times','leads','members']}
 audit.update(sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=time.time()-t,missing_fraction=float(np.isnan(arr).mean()))
 dest.with_suffix('.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
 print(date,arr.shape,'seconds',round(time.time()-t,1),'missing',audit['missing_fraction'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--date');p.add_argument('--workers',type=int,default=24);p.add_argument('--parallel-dates',type=int,default=3);p.add_argument('--stride',type=int,default=1);a=p.parse_args()
 dates=[a.date] if a.date else pd.date_range('2020-01-02','2020-12-31',freq='W-THU').strftime('%Y%m%d')[::a.stride]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.parallel_dates) as pool:
  for result in pool.map(lambda date:run_date(date,a.workers),dates):pass
