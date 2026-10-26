"""Create complete local release archives; public deposit is skipped."""
from common import ROOT
import zipfile,json,hashlib,importlib.metadata as md,shutil
R=ROOT/'revision/review_v4';D=R/'submission'
readme='''# Reproducing the V4 study

The manuscript separates the effects of climate information, temporal hierarchy,
and combining coherent forecasts. It includes eight ECMWF domains, a northern
ACCESS-S2 monthly sample, and nested mixture and selection experiments.

Install requirements.txt in a Python environment. Run commands at the extracted
project root. Existing parameter and forecast caches are deliberately reused.
Remove only the relevant output directory in a separate copy for a clean refit.
The release includes original processed inputs, source metadata, fitted records,
inner and outer membership, forecasts or exact mixture scoring statistics,
annual scores and the figure and document builders.

Original analyses: revision_cv.py, extension_cv.py, review_controls.py and their
corresponding score scripts. Primary tests remain the archived original family.

New geography: python code/coverage_extension.py build; then fit --workers 4;
then score. Public-source AGCD extracts are included. Downloading again uses
the same script with download. Eight boxes are geographical supports, not NRM
regions or a representative random sample of Australia.

ACCESS-S2: python code/access_s2_fast_download.py --workers 4; then
code/access_s2_analysis.py build, fit --workers 4, and score. Downloads contain
228 first-of-month origins, nine members and 28 daily flux values averaged over
the northern domain. The metadata and licence are retained. Do not compare the
systems' absolute scores as if their origins, grids and members were matched.

Mixtures: python code/adaptive_coherent.py --check; run without --check to fit
the four original domains. Add --forward or --rolling for the prescribed
retrospective forward periods; --domains ACCESS_N fits the second system.
Then run code/adaptive_scores.py and code/transfer_inference.py.
The joint distribution is a probability mixture, not an average of trajectories.
All weight fitting and selection uses inner held-out scores. Supplementary
Note 3 documents the objective, regularisation and decision expense definition.

Placebos: python code/placebo_extension.py --workers 4, then --score. Twenty
full year permutations and an identity refit are included. The Monte Carlo
probability assumes approximately exchangeable year blocks.

Text build order: review_v4_text.py, complete_v4_text.py, trim_v4_text.py,
final_v4_polish.py, style_v4_polish.py. Figure source: v4_figures.py. Final Word/LaTeX build:
build_v4_word.py, followed by audit_v4_release.py. Word uses Microsoft's
MML2OMML.XSL; numerical analyses do not depend on Microsoft Office. Portable
LaTeX sources use the same canonical equation strings. Do not rerun historical
document builders to regenerate V4. Rendered QA pages are omitted from release.

The adaptive and transfer checks are extensions motivated by earlier results.
2015–2019 was already inspected; it is not called an untouched prospective
test. ACCESS-S2 shares historical climate years with ECMWF. State weighting
does not beat constant pooling; no stable state-selection rule is claimed.
The staged plan therefore does not proceed to ERA5 composites as evidence for
a successful rule. The individual DMI fits remain exploratory, rather than a
selected operational predictor. No outcome-dependent region selection is used.

Public deposit status: the authors have chosen to skip Zenodo for this release.
This is a local package, and no public deposit or DOI is claimed.
Source data retain their original licences, including the ACCESS-S2 licence
under revision/review_v4/access_s2/license.txt. Rights for the deposited original
manuscript and code remain with the authors.
'''
(R/'REPRODUCE.md').write_text(readme,encoding='utf-8')
counts=json.loads((D/'format_audit.json').read_text())
notes=f'''# V4 revision notes

The abstract has {counts['abstract_words']} words. Main prose, captions and table titles contain {counts['main_and_captions_words']}
words; counting table cells as well gives {counts['all_inclusive_words']} words. The reading file omits
line numbering; the submission file adds continuous line numbers. Body text is
justified, titles are centred, headings left aligned, and plotted markers are
hollow squares. Word and LaTeX use the same thirteen main equations.

Four additional ECMWF domains and nineteen ACCESS-S2 validation years have
been fitted. The full northern climate contrast is not clearly replicated in
ACCESS-S2. Four original domains now have coherent equal, constant, seasonal
and state-dependent mixtures, global/seasonal selectors, a 2015–2019 forward
check and three rolling forward checks. ACCESS-S2 has the same mixture fits.
The state mixture improves on BU-clim but not on constant mixing. Twenty full
year-block placebo permutations have been added without changing the primary
factorial tests. Tercile skill, fixed-threshold scores and idealised cost–loss
values are included. The power-map audit is supplementary.

Table 5 now contains only forward results. Supplementary S1–S21 have a checked
caption/reference index. All added controls and adverse outcomes are retained.
No public DOI, acceptance probability or manuscript quality score is claimed.
'''
(D/'revision_notes.md').write_text(notes,encoding='utf-8')
metadata=dict(metadata=dict(title='Climate information and coherent combinations of subseasonal rainfall forecasts over Australia: code and reproducibility data',upload_type='dataset',creators=[dict(name='Yang, Musong',affiliation='Beijing Institute of Technology'),dict(name='Yang, Ce',affiliation='Beijing Institute of Technology')],description='Processed data, fitting records, predictions, scores and analysis code for the V4 manuscript. Includes ECMWF Australian domains and a northern ACCESS-S2 check; see REPRODUCE.md for validation scope and source licences.',keywords=['subseasonal forecasting','rainfall','temporal reconciliation','Australia','probabilistic forecasting'],version='4.0'))
req=[]
for n in ['numpy','pandas','scipy','matplotlib','xarray','pydap','h5py','fsspec','requests','truststore','beautifulsoup4','xgboost','python-docx','lxml','latex2mathml']:
 try:req.append(n+'=='+md.version(n))
 except md.PackageNotFoundError:pass
(R/'requirements.txt').write_text('\n'.join(req)+'\n')
docs=R/'JSHESS_review_v4_documents.zip'
with zipfile.ZipFile(docs,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for p in D.iterdir():
  if p.is_file() and p.name!='zenodo_metadata.json':z.write(p,'submission/'+p.name)
 for p in (R/'latex').rglob('*'):
  if p.is_file() and p.suffix in ['.tex','.pdf']:z.write(p,'latex/'+p.relative_to(R/'latex').as_posix())
paths=set()
def add(folder,suffixes):
 for p in folder.rglob('*'):
  if p.is_file() and p.suffix in suffixes and '__pycache__' not in str(p):paths.add(p)
add(ROOT/'code',{'.py','.ps1'})
for f in ['data/processed','data/support','data/ecmwf','data/agcd','data/packing_audit','revision/cache','revision/folds','revision/primary','revision/positive','revision/signed','revision/extension','revision/reference_metadata']:
 add(ROOT/f,{'.npz','.json','.txt','.csv','.gz','.geojson','.html'})
for f in ['revision/review_v3/cache','revision/review_v3/folds','revision/review_v3/spatial']:
 add(ROOT/f,{'.npz','.json','.csv','.gz'})
for p in (ROOT/'revision/review_v3').iterdir():
 if p.is_file() and p.suffix in ['.csv','.json','.gz','.md']:paths.add(p)
for p in (ROOT/'revision').glob('raw_*.npz'):paths.add(p)
for p in (ROOT/'revision').iterdir():
 if p.is_file() and p.suffix in ['.csv','.json','.md','.txt']:paths.add(p)
for p in ROOT.glob('*plan_*.md'):paths.add(p)
for f in ['coverage','access_s2','adaptive','placebo','figures']:
 add(R/f,{'.npz','.json','.txt','.csv','.gz','.png','.pdf','.svg'})
for p in R.iterdir():
 if p.is_file() and p.suffix in ['.md','.csv','.json','.txt']:paths.add(p)
archive=R/'JSHESS_review_v4_reproducibility.zip';manifest=[]
with zipfile.ZipFile(archive,'w',allowZip64=True) as z:
 for p in sorted(paths):
  rel=p.relative_to(ROOT).as_posix();z.write(p,rel,compress_type=zipfile.ZIP_STORED if p.suffix in ['.npz','.gz','.png','.pdf'] else zipfile.ZIP_DEFLATED);manifest.append(dict(path=rel,bytes=p.stat().st_size))
 z.writestr('REPRODUCE.md',readme);z.writestr('requirements.txt','\n'.join(req));z.writestr('archive_manifest.json',json.dumps(manifest,indent=2))
report={}
for p in [docs,archive]:
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 report[p.name]=dict(bytes=p.stat().st_size,sha256=h.hexdigest())
(R/'release_checksums.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
