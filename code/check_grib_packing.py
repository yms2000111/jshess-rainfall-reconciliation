from common import *
import truststore;truststore.inject_into_ssl()
import requests,numpy as np,json
import eccodes as ec
u='https://object-store.os-api.cci1.ecmwf.int/s2s-ai-challenge/data/training-input/0.3.0/grib/ecmwf-hindcast-tp-20200102.grib'
r=requests.get(u,headers={'Range':'bytes=0-4194303'},timeout=60);r.raise_for_status()
p=ROOT/'data/grib_sample.bin';p.write_bytes(r.content)
print('sample',r.status_code,len(r.content),r.headers.get('Content-Range'),flush=True)
report=[]
with p.open('rb') as f:
 while True:
  try:g=ec.codes_grib_new_from_file(f)
  except Exception:break
  if g is None:break
  info={k:ec.codes_get(g,k) for k in ['dataDate','step','number','bitmapPresent','numberOfMissing','min','max','packingType']}
  if len(report)<10:print(info,flush=True)
  if info['step'] in [168,336,504,672]:
   vals=ec.codes_get_values(g).reshape(121,240)
   d=np.load(ROOT/'data/ecmwf/20200102.npz')
   ts=np.datetime64(str(info['dataDate'])[:4]+'-'+str(info['dataDate'])[4:6]+'-'+str(info['dataDate'])[6:8])
   ti=np.where(d['times'].astype('datetime64[s]')==ts)[0]
   if len(ti):
    small=vals[66:91,74:105];pack=d['cumulative'][ti[0],info['number'],[7,14,21,28].index(info['step']//24)]
    miss=np.isnan(pack);info['missing_netcdf_count']=int(miss.sum());info['native_values_at_missing']=small[miss].tolist()
    info['max_abs_other_error']=float(np.max(np.abs(small[~miss]-pack[~miss])))
  report.append(info);ec.codes_release(g)
(ROOT/'data/grib_packing_audit.json').write_text(json.dumps(dict(url=u,messages=report),indent=2),encoding='utf-8')
print('messages',len(report),'matched',[x for x in report if x.get('missing_netcdf_count',0)>0][:4],flush=True)
