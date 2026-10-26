"""Build an explicitly scoped public snapshot without credentials or fit caches."""
from common import ROOT
import json, hashlib, zipfile, re

OUT=ROOT/'public_release'; OUT.mkdir(exist_ok=True)
paths=set()
def add(folder,ext):
    for p in (ROOT/folder).rglob('*'):
        if p.is_file() and p.suffix.lower() in ext and '__pycache__' not in str(p): paths.add(p)
add('code',{'.py','.ps1'})
add('data/processed',{'.npz','.csv','.json'})
add('data/support',{'.csv','.txt','.json'})
for folder in ['results','revision']:
    add(folder,{'.csv'})
for folder in ['revision/review_v5/submission_math_review','revision/review_v5/latex_math_review','revision/review_v5/figures']:
    add(folder,{'.docx','.md','.json','.tex','.png','.pdf','.svg'})
for folder in ['data/ecmwf','data/agcd','data/packing_audit','revision/review_v5/reference_metadata','revision/review_v5/circulation']:
    add(folder,{'.json','.txt','.csv'})
for p in ROOT.glob('*plan_*.md'): paths.add(p)
for p in (ROOT/'revision').glob('raw_*.npz'): paths.add(p)
for folder in ['revision','revision/review_v3','revision/review_v4','revision/review_v5']:
    for p in (ROOT/folder).glob('*'):
        if p.is_file() and p.suffix in {'.md','.json','.txt'}: paths.add(p)
for p in (ROOT/'revision/review_v5/operational').glob('input_*.npz'): paths.add(p)
for name in ['requirements.txt','revision/review_v4/access_s2/license.txt','revision/review_v5/operational/2021.npz','revision/review_v5/operational/2021.json']:
    paths.add(ROOT/name)
for p in list(paths):
    if any(w in p.name.lower() for w in ['zenodo','source_probes']): paths.remove(p)
secret=re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
for p in paths:
    if p.suffix in {'.py','.ps1','.md','.txt','.json','.csv'}:
        if secret.search(p.read_text(encoding='utf-8',errors='replace')): raise RuntimeError('Credential-like content in '+str(p))
manifest=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)]
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
archive=OUT/'research_snapshot_2026-10-26.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(paths): z.write(p,p.relative_to(ROOT).as_posix())
    z.write(OUT/'manifest.json','PUBLIC_MANIFEST.json')
with zipfile.ZipFile(archive) as z: assert z.testzip() is None
(OUT/'SHA256SUMS.txt').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n',encoding='utf-8')
# Small UTF-8 source batches for the GitHub tree API; binaries are release assets.
entries=[]
for p in sorted(paths):
    if p.parent==ROOT/'code' or p==ROOT/'requirements.txt' or p.name=='operational_test_plan_20261025.md':
        entries.append(dict(path=p.relative_to(ROOT).as_posix(),mode='100644',type='blob',content=p.read_text(encoding='utf-8')))
for i in range(0,len(entries),20):
    (OUT/f'tree_{i//20:02d}.json').write_text(json.dumps(entries[i:i+20],ensure_ascii=True),encoding='utf-8')
print(json.dumps(dict(files=len(paths),bytes=archive.stat().st_size,batches=(len(entries)+19)//20,archive=str(archive))))
