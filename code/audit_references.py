"""Fetch publisher-supplied Crossref metadata for every manuscript DOI."""
from common import ROOT
import requests,truststore,json,re,time
from urllib.parse import quote
truststore.inject_into_ssl()
text=(ROOT/'manuscript.md').read_text(encoding='utf-8')
dois=[v.rstrip('.') for v in re.findall(r'https://doi.org/(\S+)',text)]
dois+=['10.1175/MWR2904.1','10.1214/13-STS443','10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2','10.1071/ES22026','10.5194/hess-22-1615-2018','10.1175/MWR-D-13-00248.1']
out=ROOT/'revision/reference_metadata';out.mkdir(exist_ok=True)
rows=[]
for doi in dict.fromkeys(dois):
 path=out/(re.sub(r'[^a-zA-Z0-9.-]','_',doi)+'.json')
 try:
  if path.exists():m=json.loads(path.read_text(encoding='utf-8'))
  elif doi.startswith('10.25914/'):
   response=requests.get('https://api.datacite.org/dois/'+quote(doi,safe=''),timeout=45);response.raise_for_status();a=response.json()['data']['attributes'];m={'title':[v['title'] for v in a['titles']],'published':{'date-parts':[[a['publicationYear']]]},'author':a['creators'],'publisher':a['publisher'],'datacite':a};path.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
  else:
   response=requests.get('https://api.crossref.org/works/'+quote(doi,safe=''),timeout=45);response.raise_for_status();m=response.json()['message'];path.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
  rows.append(dict(doi=doi,title=m.get('title'),year=m.get('published'),volume=m.get('volume'),page=m.get('page'),journal=m.get('container-title'),authors=m.get('author'),status='verified metadata'))
  print(doi,m.get('title'),m.get('volume'),m.get('page'),flush=True)
 except Exception as e:rows.append(dict(doi=doi,status=str(e)));print('FAILED',doi,str(e),flush=True)
(out/'audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
