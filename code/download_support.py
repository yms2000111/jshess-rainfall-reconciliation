from common import *
import truststore;truststore.inject_into_ssl()
import requests,json,hashlib,concurrent.futures
OUT=ROOT/'data/support';OUT.mkdir(parents=True,exist_ok=True)
SOURCES={
 'nino34.txt':'https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii',
 'rmm_full.txt':'https://reg.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt',
 'countries.geojson':'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson',
}
def get(item):
 name,url=item;r=requests.get(url,timeout=60);r.raise_for_status();(OUT/name).write_bytes(r.content)
 print(name,len(r.content),r.text[:100],flush=True)
 return dict(file=name,url=url,sha256=hashlib.sha256(r.content).hexdigest())
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:res=list(p.map(get,SOURCES.items()))
(OUT/'manifest.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
