from common import ROOT
import requests,truststore,sys,hashlib,json
from lxml import etree
truststore.inject_into_ssl()
out=ROOT/'revision/review_v4/access_s2';out.mkdir(parents=True,exist_ok=True)
url=sys.argv[1]
r=requests.get(url,timeout=50);r.raise_for_status();p=out/(hashlib.sha256(url.encode()).hexdigest()[:16]+'.xml');p.write_text(r.text,encoding='utf-8')
print('URL',url,'saved',p.name)
root=etree.fromstring(r.content)
for e in root.iter():
 if etree.QName(e).localname in ['catalogRef','dataset','documentation']:print(dict(e.attrib),e.text or '')
