from common import ROOT
import zipfile,hashlib,json,datetime
out=ROOT/'archive';out.mkdir(exist_ok=True);target=out/'chronological_v1_20261023.zip'
if not target.exists():
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
  for folder in ['code','results','results_positive_part','submission','latex']:
   for p in (ROOT/folder).rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('~$'):z.write(p,p.relative_to(ROOT))
  for name in ['manuscript.md','README.md','requirements.txt']:z.write(ROOT/name,name)
 print('Frozen',target.name,round(target.stat().st_size/1e6,1),'MB')
else:print('Snapshot already exists; unchanged.')
