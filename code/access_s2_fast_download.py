"""Validated two-request DAP extraction with per-file units/date audits."""
from common import ROOT
import truststore;truststore.inject_into_ssl()
import numpy as np,pandas as pd,json,time,hashlib,argparse,threading,requests
from concurrent.futures import ThreadPoolExecutor,as_completed
from pydap.parsers.dds import dds_to_dataset
from pydap.handlers.dap import unpack_dap2_data,old_BytesReader
from pydap.parsers.das import parse_das
OUT=ROOT/'revision/review_v4/access_s2'
BASE='https://thredds.nci.org.au/thredds/dodsC/ux62/access-s2/hindcast/raw_model/atmos/pr/daily/'
pilot=np.load(OUT/'20000101_e01.npz');lat=pilot['lat'];lon=pilot['lon'];weights=pilot['weights']
iy=np.rint((lat+89.72222222)/(5/9)).astype(int);ix=np.rint((lon-5/12)/(5/6)).astype(int)
query=f'pr[0:1:27][{iy.min()}:1:{iy.max()}][{ix.min()}:1:{ix.max()}]'
local=threading.local()

def task(date,member):
 dest=OUT/f'{date}_e{member:02d}.npz'
 if dest.exists():
  with np.load(dest) as f:assert f['daily_mm'].shape==(28,) and np.isfinite(f['daily_mm']).all()
  return
 if not hasattr(local,'session'):local.session=requests.Session()
 url=BASE+f'e{member:02d}/da_pr_{date}_e{member:02d}.nc'
 for attempt in range(5):
  try:
   r=local.session.get(url+'.dods',params=query,timeout=75);r.raise_for_status()
   dds,data=r.content.split(b'\nData:\n',1);ds=dds_to_dataset(dds.decode());ds.data=unpack_dap2_data(old_BytesReader(data),ds);g=ds['pr']
   a=np.asarray(g['pr'].data).astype(float);assert a.shape==(28,len(lat),len(lon))
   assert np.allclose(g['lat'].data,lat) and np.allclose(g['lon'].data,lon)
   r=local.session.get(url+'.das',timeout=60);r.raise_for_status();attr=parse_das(r.text)
   assert attr['pr']['units']=='kg m-2 s-1' and attr['pr']['cell_methods']=='time: mean'
   assert attr['time']['units']=='days since 1970-01-01 00:00:00'
   t=pd.to_datetime(np.asarray(g['time'].data),unit='D',origin='unix');expected=pd.date_range(pd.Timestamp(date)+pd.Timedelta(hours=12),periods=28)
   assert np.array_equal(t.values,expected.values)
   assert np.isfinite(a).all() and a.min()>=-1e-10
   rain=(np.maximum(a,0)*weights).sum((1,2))*86400
   temp=dest.with_suffix('.part')
   with temp.open('wb') as f:np.savez_compressed(f,daily_mm=rain,time=expected.values,lat=lat,lon=lon,weights=weights)
   temp.replace(dest)
   dest.with_suffix('.json').write_text(json.dumps(dict(url=url,units=attr['pr']['units'],time_cell_method=attr['pr']['cell_methods'],time_units=attr['time']['units'],time_bounds_variable_present='time_bnd0' in attr,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),indent=2))
   return
  except Exception:
   if attempt==4:raise
   time.sleep(2+attempt)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=8);a=p.parse_args()
 jobs=[(d.strftime('%Y%m%d'),m) for d in pd.date_range('2000-01-01','2018-12-01',freq='MS') for m in range(1,10)]
 start=time.monotonic();errors=[]
 with ThreadPoolExecutor(max_workers=a.workers) as pool:
  fs={pool.submit(task,*job):job for job in jobs}
  for i,f in enumerate(as_completed(fs),1):
   try:f.result()
   except Exception as e:errors.append(dict(job=fs[f],error=str(e)));print('Failed',fs[f],str(e)[:160],flush=True)
   if i%100==0 or i==len(jobs):print(f'{i}/{len(jobs)}, {time.monotonic()-start:.0f}s, errors {len(errors)}',flush=True)
 (OUT/'download_errors.json').write_text(json.dumps(errors,indent=2));assert not errors
