"""Download fine-grid regional AGCD slices and retain exact area-weighted means."""
from common import *
import truststore;truststore.inject_into_ssl()
import numpy as np,pandas as pd,xarray as xr,json,concurrent.futures,time,hashlib
OUT=ROOT/'data/agcd';OUT.mkdir(parents=True,exist_ok=True)
BASE='https://thredds.nci.org.au/thredds/dodsC/zv2/agcd/v1-0-1/precip/total/r005/01day/'
def year_task(year):
 dest=OUT/f'{year}.npz'
 if dest.exists():return f'cached {year}'
 t=time.time();url=BASE+f'agcd_v1-0-1_precip_total_r005_daily_{year}.nc'
 ds=xr.open_dataset(url,engine='pydap')
 res=dict(time=ds.time.values)
 for key,r in REGIONS.items():
  da=ds.precip.sel(lat=slice(r['lat'][0]-.05,r['lat'][1]+.05),lon=slice(r['lon'][0]-.05,r['lon'][1]+.05)).load()
  lat=da.lat.values.astype(float);lon=da.lon.values.astype(float)
  y1=np.maximum(lat-.025,r['lat'][0]);y2=np.minimum(lat+.025,r['lat'][1]);
  xw=np.maximum(0,np.minimum(lon+.025,r['lon'][1])-np.maximum(lon-.025,r['lon'][0]))
  yw=np.maximum(0,np.sin(np.deg2rad(y2))-np.sin(np.deg2rad(y1)))
  weights=yw[:,None]*xw[None,:]
  v=da.values.astype(float);valid=np.isfinite(v);v[~valid]=0
  den=(valid*weights).sum(axis=(1,2));mean=(v*weights).sum(axis=(1,2))/den
  # Record missing support rather than renormalising away major gaps silently.
  land=np.any(valid,axis=0);coverage=den/weights[land].sum()
  mean[coverage<.99]=np.nan
  res[key]=mean;res[key+'_coverage']=coverage
  res[key+'_clim_sum']=v.sum(axis=0);res[key+'_clim_n']=valid.sum(axis=0)
  res[key+'_lat']=lat;res[key+'_lon']=lon
 np.savez_compressed(dest,**res)
 dest.with_suffix('.json').write_text(json.dumps(dict(url=url,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),attrs=ds.attrs,variable_attrs=ds.precip.attrs),default=str,indent=2),encoding='utf-8')
 ds.close();return f'{year} completed {time.time()-t:.1f} s'
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:
  for msg in p.map(year_task,range(2000,2021)):print(msg,flush=True)
