from common import ROOT
import truststore;truststore.inject_into_ssl()
import requests,json,h5py,fsspec
R=ROOT/'revision/review_v5';out=[]
urls=[
 'https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/Monthlies/pressure/uwnd.mon.mean.nc',
 'https://psl.noaa.gov/thredds/fileServer/Datasets/ncep.reanalysis.derived/pressure/uwnd.mon.mean.nc',
 'https://upwell.pfeg.noaa.gov/erddap/search/index.json?page=1&itemsPerPage=100&searchFor=uwnd+monthly',
 'https://object-store.os-api.cci1.ecmwf.int/s2s-ai-challenge/data/test-input/0.3.0/netcdf/ecmwf-forecast-tp-20200102.nc']
for u in urls:
 try:
  r=requests.get(u,headers={'Range':'bytes=0-8191'},timeout=40);r.raise_for_status()
  item=dict(url=u,status=r.status_code,bytes=len(r.content),headers=dict(r.headers))
  if 'json' in u:item['text']=r.text
  else:item['signature']=r.content[:16].hex()
  out.append(item);print(u,r.status_code,len(r.content),flush=True)
 except Exception as e:out.append(dict(url=u,error=str(e)));print(u,str(e),flush=True)
(R/'source_probes.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
u=urls[-1]
try:
 with fsspec.open(u,block_size=65536,cache_type='blockcache').open() as f:
  with h5py.File(f,'r') as h:
   metadata={k:dict(shape=v.shape,chunks=v.chunks,attrs={a:str(b) for a,b in v.attrs.items()}) for k,v in h.items()};print(metadata,flush=True)
 (R/'operational_metadata.json').write_text(json.dumps(metadata,indent=2))
except Exception as e:print('Forecast metadata',str(e),flush=True)
