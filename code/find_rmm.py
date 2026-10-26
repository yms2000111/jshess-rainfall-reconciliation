from common import *
import truststore;truststore.inject_into_ssl()
import requests,concurrent.futures,json
urls=[
 'https://reg.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt',
 'http://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt',
 'https://www.bom.gov.au/climate/mjo/graphics/rmm.74toRealtime.txt?download=1',
 'https://ncics.org/pub/mjo/RMM/rmm.74toRealtime.txt',
 'https://nmathewa.github.io/mjo-tracker/data/rmm.json']
def task(u):
 try:
  r=requests.get(u,timeout=30);print(u,r.status_code,len(r.content),r.text[:70],r.text[-200:],flush=True)
  if r.status_code==200 and len(r.content)>500000 and 'RMM values' in r.text[:200]:
   (ROOT/'data/support/rmm_full.txt').write_text(r.text,encoding='utf-8');(ROOT/'data/support/rmm_source.txt').write_text(u,encoding='utf-8')
 except Exception as e:print(u,str(e),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as p:list(p.map(task,urls))
