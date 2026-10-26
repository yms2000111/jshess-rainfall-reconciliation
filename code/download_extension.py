"""Archive authoritative climate indices and publication metadata."""
from common import ROOT
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests,truststore,json,hashlib,re
from bs4 import BeautifulSoup
from urllib.parse import urljoin,quote
truststore.inject_into_ssl()
out=ROOT/'data/support'; records=[]
def save(url,name):
 p=out/name
 if not p.exists():
  r=requests.get(url,timeout=60);r.raise_for_status();p.write_bytes(r.content)
 records.append(dict(url=url,file=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 return p
page=save('https://psl.noaa.gov/data/timeseries/month/DMI/','dmi_source.html')
soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
links=[a.get('href') for a in soup.find_all('a') if a.get_text(strip=True)=='CSV']
assert links
save(urljoin(records[0]['url'],links[0]),'dmi.csv')
save('https://legacy.bas.ac.uk/met/gjma/sam.html','sam_source.html')
(out/'extension_manifest.json').write_text(json.dumps(records,indent=2))
dest=ROOT/'revision/reference_metadata'
dois=['10.1029/2021WR031862','10.1175/JHM-D-22-0119.1','10.1016/j.ejor.2019.05.020','10.1002/qj.4585','10.1071/ES24004','10.1071/ES23022','10.1071/ES25065','10.1175/1520-0442(2003)016<4134:TITSAM>2.0.CO;2','10.2307/4615733']
for doi in dois:
 p=dest/(re.sub(r'[^a-zA-Z0-9.-]','_',doi)+'.json')
 if not p.exists():
  r=requests.get('https://api.crossref.org/works/'+quote(doi,safe=''),timeout=45);r.raise_for_status();p.write_text(json.dumps(r.json()['message'],ensure_ascii=False,indent=2),encoding='utf-8')
 m=json.loads(p.read_text(encoding='utf-8'));print(doi,m.get('title'),m.get('volume'),m.get('page'),flush=True)
print(json.dumps(records),flush=True)
