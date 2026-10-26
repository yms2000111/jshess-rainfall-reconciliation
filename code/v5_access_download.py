"""Extract all eight fixed domains from the same validated ACCESS files."""
from common import ROOT,REGIONS
import truststore;truststore.inject_into_ssl()
import numpy as np,pandas as pd,json,time,hashlib,threading,requests,argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from pydap.parsers.dds import dds_to_dataset
from pydap.handlers.dap import unpack_dap2_data,old_BytesReader
REGIONS.update(json.loads((ROOT/'revision/review_v4/coverage/domains.json').read_text()))
OUT=ROOT/'revision/review_v5/access_s2';OUT.mkdir(parents=True,exist_ok=True)
BASE='https://thredds.nci.org.au/thredds/dodsC/ux62/access-s2/hindcast/raw_model/atmos/pr/daily/'
lat=-89.72222222+np.arange(324)*(5/9);lon=5/12+np.arange(432)*(5/6)
iy=np.flatnonzero((lat+5/18>-44.25)&(lat-5/18<-12.75));ix=np.flatnonzero((lon+5/12>116.25)&(lon-5/12<152.25))
query=f'pr[0:1:27][{iy.min()}:1:{iy.max()}][{ix.min()}:1:{ix.max()}]';local=threading.local()

def task(date,member):
 dest=OUT/f'{date}_e{member:02d}.npz'
 if dest.exists():return
 if not hasattr(local,'session'):local.session=requests.Session()
 url=BASE+f'e{member:02d}/da_pr_{date}_e{member:02d}.nc'
 old=ROOT/f'revision/review_v4/access_s2/{date}_e{member:02d}.json';attr=json.loads(old.read_text())
 assert attr['url']==url and attr['units']=='kg m-2 s-1' and attr['time_cell_method']=='time: mean'
 for attempt in range(4):
  try:
   r=local.session.get(url+'.dods',params=query,timeout=90);r.raise_for_status()
   dds,data=r.content.split(b'\nData:\n',1);ds=dds_to_dataset(dds.decode());ds.data=unpack_dap2_data(old_BytesReader(data),ds);g=ds['pr'];a=np.asarray(g['pr'].data,dtype=float)
   la=np.asarray(g['lat'].data,dtype=float);lo=np.asarray(g['lon'].data,dtype=float)
   assert a.shape==(28,len(iy),len(ix)) and np.isfinite(a).all() and a.min()>-1e-10
   assert np.allclose(la,lat[iy]) and np.allclose(lo,lon[ix])
   t=pd.to_datetime(np.asarray(g['time'].data),unit='D',origin='unix');expected=pd.date_range(pd.Timestamp(date)+pd.Timedelta(hours=12),periods=28)
   assert np.array_equal(t.values,expected.values)
   output={}
   for k,d in REGIONS.items():
    y0=np.maximum(la-5/18,d['lat'][0]);y1=np.minimum(la+5/18,d['lat'][1]);wy=np.maximum(0,np.sin(np.deg2rad(y1))-np.sin(np.deg2rad(y0)))
    wx=np.maximum(0,np.minimum(lo+5/12,d['lon'][1])-np.maximum(lo-5/12,d['lon'][0]));w=wy[:,None]*wx[None,:];w/=w.sum()
    output[k]=(a*w).sum((1,2))*86400
   prev=np.load(ROOT/f'revision/review_v4/access_s2/{date}_e{member:02d}.npz')['daily_mm'];assert np.allclose(output['N'],prev,atol=1e-5)
   np.savez_compressed(dest,**output,time=t.values)
   dest.with_suffix('.json').write_text(json.dumps(dict(url=url,query=query,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),source_metadata=str(old.relative_to(ROOT)),northern_max_difference=float(abs(output['N']-prev).max())),indent=2));return
  except Exception:
   if attempt==3:raise
   time.sleep(2+attempt)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=10);p.add_argument('--pilot',action='store_true');a=p.parse_args()
 jobs=[('20000101',1)] if a.pilot else [(d.strftime('%Y%m%d'),m) for d in pd.date_range('2000-01-01','2018-12-01',freq='MS') for m in range(1,10)]
 errors=[];start=time.monotonic()
 with ThreadPoolExecutor(max_workers=a.workers) as pool:
  fs={pool.submit(task,*j):j for j in jobs}
  for i,f in enumerate(as_completed(fs),1):
   try:f.result()
   except Exception as exc:errors.append(dict(job=fs[f],error=str(exc)));print(errors[-1],flush=True)
   if i%100==0 or i==len(jobs):print(i,len(jobs),round(time.monotonic()-start),len(errors),flush=True)
 (OUT/'download_errors.json').write_text(json.dumps(errors,indent=2));assert not errors
