"""Archive the completed revision and its local reproducibility material."""
from common import ROOT
from pathlib import Path
import zipfile,json,hashlib,importlib.metadata as md

R=ROOT/'revision/review_v3';D=R/'submission'
notes='''# Revision notes

The revision adds climate-informed weekly aggregation, intercept-only aggregate
adjustments, four northern climate groups, three predictor-year placebos,
one-month monthly-index lags, matched ECC/Schaake factorial forecasts, northern
factorial archive-correction sensitivities, a strictly forward 2015–2019
evaluation, and all four 1.5-degree cells inside the northern domain.

The primary factorial tests remain unchanged. New comparisons are exploratory.
The forward table includes the raw forecast as well as all calibrated methods.
The northern weekly climate forecast is better than aggregate reconciliation
in that forward period; the raw northern forecast is better than both.

The threshold audit replaces the mismatched northern event percentage and score
share with 68/1060 (6.4%) and 20.7%, using the same threshold as the main table.
Northeastern power-map coverage crosses 80% with the same absolute discrepancy.
The power-map discussion now distinguishes fitting-window loss from central-month
application and outer validation. Covariance gain bias and slopes are reported.

The reading and submission manuscripts have identical scientific content. The
submission file adds continuous line numbers. Both use justified body text,
native editable Word equations, hollow square data markers, larger labels and
complete figure ranges. The LaTeX file uses the same canonical equation source
and has compiled successfully. Supplementary Tables S1–S13 accompany the files.

The local archive has not been deposited in Zenodo and has no public DOI.
The study still uses one forecast system and does not establish national skill.
'''
(D/'revision_notes.md').write_text(notes,encoding='utf-8')
requirements=[]
for name in ['numpy','pandas','scipy','matplotlib','xarray','pydap','h5py','fsspec','requests','truststore','beautifulsoup4','xgboost','python-docx','lxml','latex2mathml']:
 try:requirements.append(name+'=='+md.version(name))
 except md.PackageNotFoundError:pass
(R/'requirements.txt').write_text('\n'.join(requirements)+'\n',encoding='utf-8')
readme='''# Reproducibility instructions

Create a Python environment and install requirements.txt. Extract this archive
at a project root and run scripts from that root. The _deps directory used in
the original workspace is not distributed; normal environment packages work.

The archive contains processed inputs, public-source extracts and retrieval
metadata, fitted parameter caches, validation folds, forecast samples, case
scores, figure sources and document builders. It excludes runtime libraries,
temporary rendering images and historical publication files.

Primary analysis: code/revision_cv.py, code/revision_statistics.py and
code/revision_diagnostics.py. The primary, positive and signed treatments are
separate branches. Factorial analysis: code/extension_cv.py and
code/extension_scores.py. Power-map analysis: code/recalibration.py and
code/recalibration_scores.py.

Additional controls: code/review_controls.py --workers 4; then run the same
script with --forward. code/review_control_scores.py calculates scores.
code/review_audit.py runs small-sample and threshold audits; its --inner option
checks the recalibration populations and covariance shifts.
code/review_more_stats.py reports Brier skill and further intervals.

Spatial inputs are included. To retrieve them again use
code/review_spatial.py --download, followed by --build. Run that script without
options to fit all subdomains, then with --score. code/review_finalise_stats.py
retains the forward raw baseline and the spatial paired comparisons.

Final figures: code/review_figures.py. Final documents:
code/build_review_word.py. The Word mathematical transform requires the local
Microsoft Office MML2OMML.XSL stylesheet. Portable LaTeX sources are included
under revision/review_v3/latex. All numerical analyses are independent of Word.

Dated analysis plans describe the original, factorial and review stages. The
new controls are exploratory and do not replace the original primary tests.
Existing fold files and caches are reused; use a fresh output directory when
intentionally refitting. Source provenance and hashes are preserved in JSON.
'''
(R/'REPRODUCE.md').write_text(readme,encoding='utf-8')

docs=R/'JSHESS_review_v3_documents.zip'
with zipfile.ZipFile(docs,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(D.iterdir()):
  if p.is_file():z.write(p,'submission/'+p.name)
 for p in sorted((R/'latex').rglob('*')):
  if p.is_file() and p.suffix in ['.tex','.pdf']:z.write(p,'latex/'+str(p.relative_to(R/'latex')))

archive=R/'JSHESS_review_v3_reproducibility.zip'
paths=set()
def addtree(folder,suffixes=None):
 for p in folder.rglob('*'):
  if p.is_file() and (suffixes is None or p.suffix in suffixes) and '__pycache__' not in str(p):paths.add(p)
addtree(ROOT/'code',{'.py','.ps1'})
for folder in ['data/processed','data/support','data/ecmwf','data/agcd','data/packing_audit']:
 addtree(ROOT/folder,{'.npz','.json','.txt','.csv','.geojson','.html'})
for folder in ['revision/cache','revision/folds','revision/primary','revision/positive','revision/signed','revision/extension','revision/reference_metadata']:
 addtree(ROOT/folder,{'.npz','.json','.csv','.gz'})
for p in (ROOT/'revision').glob('raw_*.npz'):paths.add(p)
for p in ROOT.glob('*plan_*.md'):paths.add(p)
for p in R.iterdir():
 if p.is_file() and p.suffix in ['.md','.txt','.json','.csv','.gz']:paths.add(p)
for folder in ['cache','folds','spatial']:
 addtree(R/folder,{'.npz','.json','.csv','.gz'})
addtree(R/'figures',{'.png','.pdf','.svg'})
manifest=[]
with zipfile.ZipFile(archive,'w',allowZip64=True) as z:
 for p in sorted(paths):
  relative=p.relative_to(ROOT).as_posix();compression=zipfile.ZIP_STORED if p.suffix in ['.npz','.gz','.png','.pdf'] else zipfile.ZIP_DEFLATED
  z.write(p,relative,compress_type=compression);manifest.append(dict(path=relative,bytes=p.stat().st_size))
 z.writestr('REPRODUCE.md',readme)
 z.writestr('requirements.txt',(R/'requirements.txt').read_text())
 z.writestr('archive_manifest.json',json.dumps(manifest,indent=2))
report={}
for p in [docs,archive]:
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 report[p.name]=dict(bytes=p.stat().st_size,sha256=h.hexdigest())
(R/'release_checksums.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
