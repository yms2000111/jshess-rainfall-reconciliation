from common import ROOT
import requests,json,truststore
truststore.inject_into_ssl()
from pathlib import Path
out=ROOT/'revision/review_v4/access_s2';out.mkdir(parents=True,exist_ok=True)
urls=[
 'https://thredds.nci.org.au/thredds/catalog/catalogs/ux62/access-s2/hindcast/hindcast.xml',
 'https://thredds.nci.org.au/thredds/catalog/ux62/access-s2/hc/catalog.xml',
 'https://thredds.nci.org.au/thredds/catalog/catalogs/ux62/catalog.xml']
report=[]
for i,url in enumerate(urls):
 try:
  r=requests.get(url,timeout=40);(out/f'catalog_{i}.txt').write_text(r.text,encoding='utf-8')
  report.append(dict(url=url,status=r.status_code,bytes=len(r.content),preview=r.text[:800]))
 except Exception as e:report.append(dict(url=url,error=str(e)))
(out/'access_probe.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
