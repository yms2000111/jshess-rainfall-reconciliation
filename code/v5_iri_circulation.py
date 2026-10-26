"""Retrieve the same NCEP/NCAR monthly fields from the IRI Data Library."""
from common import ROOT
import truststore;truststore.inject_into_ssl()
import requests,json,hashlib
R=ROOT/'revision/review_v5/circulation';rows=[]
base='https://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP-NCAR/.CDAS-1/.MONTHLY/.Intrinsic/.PressureLevel/'
for var,name in [('u','uwnd'),('v','vwnd'),('qa','shum')]:
 if (R/(name+'_850_monthly.nc')).exists():continue
 url=base+'.'+var+'/T/(Jan%202000)/(Dec%202019)/RANGE/P/850/VALUE/Y/-25/5/RANGE/X/100/155/RANGE/data.nc'
 try:
  r=requests.get(url,timeout=90);r.raise_for_status();assert r.content.startswith(b'CDF') or r.content.startswith(b'\x89HDF')
  p=R/(name+'_850_monthly.nc');p.write_bytes(r.content);rows.append(dict(variable=var,url=url,bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest()));print(name,len(r.content),flush=True)
 except Exception as e:rows.append(dict(variable=var,url=url,error=str(e)));print(name,str(e),flush=True)
 (R/'iri_retrieval.json').write_text(json.dumps(rows,indent=2))
