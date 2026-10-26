from common import ROOT
import truststore;truststore.inject_into_ssl()
import xarray as xr,numpy as np,pandas as pd,json,time,hashlib,argparse,warnings
from concurrent.futures import ThreadPoolExecutor,as_completed
warnings.filterwarnings('ignore',message='PyDAP was unable')
OUT=ROOT/'revision/review_v4/access_s2';OUT.mkdir(parents=True,exist_ok=True)
BASE='https://thredds.nci.org.au/thredds/dodsC/ux62/access-s2/hindcast/raw_model/atmos/pr/daily/'

def task(date,member):
 dest=OUT/f'{date}_e{member:02d}.npz'
 if dest.exists():return f'{date} e{member:02d} cached'
 url=BASE+f'e{member:02d}/da_pr_{date}_e{member:02d}.nc';last=None
 for retry in range(4):
  try:
   ds=xr.open_dataset(url,engine='pydap')
   assert ds.pr.attrs['units']=='kg m-2 s-1'
   assert ds.pr.attrs['cell_methods']=='time: mean'
   origin=pd.Timestamp(date);expected=pd.date_range(origin+pd.Timedelta(hours=12),periods=28,freq='D')
   assert np.array_equal(ds.time.values[:28],expected.values)
   da=ds.pr.isel(time=slice(0,28)).sel(lat=slice(-16.1,-12.4),lon=slice(130.8,134.7)).load()
   v=da.values.astype(float);lat=da.lat.values.astype(float);lon=da.lon.values.astype(float)
   assert np.isfinite(v).all() and v.min()>=-1e-10
   # Native cells are 5/9 degrees latitude by 5/6 degrees longitude.
   yw=np.maximum(0,np.sin(np.deg2rad(np.minimum(lat+5/18,-12.75)))-np.sin(np.deg2rad(np.maximum(lat-5/18,-15.75))))
   xw=np.maximum(0,np.minimum(lon+5/12,134.25)-np.maximum(lon-5/12,131.25))
   w=yw[:,None]*xw[None,:];w/=w.sum();rain=(np.maximum(v,0)*w).sum((1,2))*86400
   assert np.isfinite(rain).all()
   np.savez_compressed(dest,daily_mm=rain,time=expected.values,lat=lat,lon=lon,weights=w)
   dest.with_suffix('.json').write_text(json.dumps(dict(url=url,units=ds.pr.attrs['units'],time_cell_method=ds.pr.attrs['cell_methods'],time_bounds_variable_present='time_bnd0' in ds,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),indent=2))
   ds.close();return f'{date} e{member:02d} retrieved'
  except Exception as e:
   last=e
   if retry<3:time.sleep(2+retry)
 raise RuntimeError(f'{url}: {last}')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--workers',type=int,default=6);a=p.parse_args()
 jobs=[('20000101',1),('20000101',9)] if a.pilot else [(d.strftime('%Y%m%d'),m) for d in pd.date_range('2000-01-01','2018-12-01',freq='MS') for m in range(1,10)]
 with ThreadPoolExecutor(max_workers=a.workers) as pool:
  futures=[pool.submit(task,*job) for job in jobs]
  for i,f in enumerate(as_completed(futures),1):
   msg=f.result()
   if a.pilot or i%30==0 or i==len(jobs):print(f'{i}/{len(jobs)} {msg}',flush=True)
