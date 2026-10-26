"""Resolve every manuscript DOI, retaining publisher-deposited metadata."""
from common import ROOT
import re,json,requests,truststore,unicodedata
from urllib.parse import quote
truststore.inject_into_ssl()
R=ROOT/'revision/review_v5';dest=R/'reference_metadata';dest.mkdir(exist_ok=True)
text=(R/'manuscript.md').read_text(encoding='utf-8');refs=text.split('## References\n\n')[1].strip().split('\n\n');report=[]
for entry in refs:
 match=re.search(r'https://doi.org/(\S+)',entry)
 if not match:continue
 doi=match[1].rstrip('.');name=re.sub(r'[^a-zA-Z0-9.-]','_',doi)+'.json';old=ROOT/'revision/reference_metadata'/name;p=dest/name
 if p.exists():m=json.loads(p.read_text(encoding='utf-8'))
 elif old.exists():m=json.loads(old.read_text(encoding='utf-8'));p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
 else:
  r=requests.get('https://api.crossref.org/works/'+quote(doi,safe=''),timeout=45);r.raise_for_status();m=r.json()['message'];p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
 authors=m.get('author',[]);year=m.get('published',{}).get('date-parts',[[]])[0]
 report.append({'doi':doi,'reference':entry,'deposited_title':m.get('title'),'deposited_year':year,'volume':m.get('volume'),'page':m.get('page'),'article_number':m.get('article-number'),'journal':m.get('container-title'),'authors':[a.get('family',a.get('name',''))+' '+a.get('given','') for a in authors],'abstract':m.get('abstract',''),'status':'DOI metadata resolved','cache_origin':'earlier verified publisher metadata' if old.exists() else 'Crossref 2026-10-25'})
 print(doi,'|',m.get('title'),'|',year,'|',m.get('volume'),m.get('page'),m.get('article-number'),'|',report[-1]['authors'],flush=True)
(dest/'doi_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('Resolved',len(report),'DOIs out of',len(refs),'references')
