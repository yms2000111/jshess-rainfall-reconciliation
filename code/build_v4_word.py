"""Build matched V4 Word documents without overwriting the inspected V3."""
from common import ROOT
wrapper=(ROOT/'code/build_review_word.py').read_text(encoding='utf-8').split("exec(compile(source,'build_review_word_source','exec'))")[0]
exec(compile(wrapper,'v3_builder_setup','exec'))
source=source.replace("OUT=ROOT/'revision/review_v3/submission'","OUT=ROOT/'revision/review_v4/submission'").replace("F=ROOT/'revision/review_v3/figures'","F=ROOT/'revision/review_v4/figures'").replace("ROOT/'revision/review_v3/manuscript.md'","ROOT/'revision/review_v4/manuscript.md'")
source=source.replace('from final_equations import EQUATIONS','from v4_equations import EQUATIONS')
start=source.index("FA=pd.read_csv(REVIEW/'forward_annual.csv')")
end=source.index("SP=pd.read_csv(REVIEW/'spatial/annual_scores.csv')",start)
source=source[:start]+'''FA=pd.read_csv(REVIEW/'forward_annual.csv').query('lead=="D28"');rows=[]
for k in REGIONS:
 for m in ['Raw','Bottom_up','H0','H1','Weekly_climate_BU']:
  a=FA.query('domain==@k and method==@m').set_index('year').crps
  rows.append([k,SHORT[m]]+[f'{a.loc[y]:.3f}' for y in range(2015,2020)])
table(supp,'Table S12. Individual annual forward CRPS (mm), with all training ending in 2014. These are annual scores, not confidence bounds.',['Code','Method','2015','2016','2017','2018','2019'],rows,[.5,1.8,.9,.9,.9,.9,.9],newpage=True)
'''+source[end:]
source=source.replace('SPATIAL_RESULT_V3','SPATIAL_RESULT_V3|EXTENSION_|RESULT_V4')
source=source.replace('doc=document();doc.core_properties.title=',(ROOT/'code/v4_tables.py').read_text(encoding='utf-8')+'\ndoc=document();doc.core_properties.title=',1)
source=source.replace("supp.save(OUT/'JSHESS_supplementary_material.docx')",(ROOT/'code/v4_supplement.py').read_text(encoding='utf-8')+"\nsupp.save(OUT/'JSHESS_supplementary_material.docx')")
source=source.replace("supp.save(OUT/'JSHESS_supplementary_material.docx')",'''# Put the S1c block with S1a and S1b, before Table S2.
body=supp._element.body
captions={''.join(e.itertext()):e for e in body if e.tag==qn('w:p')}
first=next(e for e in body if e.tag==qn('w:p') and ''.join(e.itertext()).startswith('Table S1c.'))
anchor=next(e for e in body if e.tag==qn('w:p') and ''.join(e.itertext()).startswith('Table S2.'))
tbl=first.getnext();assert tbl.tag==qn('w:tbl')
anchor.addprevious(first);anchor.addprevious(tbl)
# Keep short companion tables together instead of leaving almost empty pages.
for p in supp.paragraphs:
 if p.text.startswith(('Table S1c.','Table S16b.','Table S17b.')):
  p.paragraph_format.page_break_before=False
  p.paragraph_format.space_before=Pt(16)
# Keep supplementary method labels identical to the main text.
method_names={'Bottom-up':'BU-rain','Bottom_up':'BU-rain','Weekly_climate_BU':'BU-clim','H0_7_NN':'H0','H0, seven':'H0','H1, seven':'H1','H0, seven nodes':'H0','H1, seven nodes':'H1','H1 vs H0, seven nodes':'H1 vs H0','H1, seven nodes vs bottom-up':'H1 vs BU-rain','Reviewer five years':'Selected five years','ACCESS_N':'ACCESS N'}
for t in supp.tables:
 for row in t.rows:
  for cell in row.cells:
   for p in cell.paragraphs:
    if p.text in method_names:
     value=method_names[p.text]
     if p.runs:
      p.runs[0].text=value
      for run in p.runs[1:]:run.text=''
# Group all supplementary figures after the tables and method notes.
fig3=next(e for e in body if e.tag==qn('w:p') and ''.join(e.itertext()).startswith('Fig. S3.'))
fig_anchor=fig3.getprevious()
for number in [1,2]:
 caption=next(e for e in body if e.tag==qn('w:p') and ''.join(e.itertext()).startswith('Fig. S'+str(number)+'.'))
 picture=caption.getprevious()
 fig_anchor.addprevious(picture);fig_anchor.addprevious(caption)
supp.save(OUT/'JSHESS_supplementary_material.docx')''')
source=source.replace('All scores use the same 20 outer validation years as the main manuscript.','Original ECMWF analyses use twenty outer years; ACCESS-S2 uses nineteen years. Forward and rolling checks have their stated shorter periods.')
source=source.replace("statement='Rainfall forecasts", "statement='Rainfall forecasts")
start=source.index("statement='Rainfall forecasts");end=source.index("\n(OUT/'statement_of_importance",start)
source=source[:start]+"statement='Weekly rainfall forecasts and longer accumulations should give a consistent picture for planning. Australian hindcast comparisons show that useful climate information does not always make reconciliation better than weekly summation, and state-dependent combinations do not consistently improve on fixed mixtures. Forecast services should retain raw and simple coherent alternatives when assessing added modelling complexity across locations and evaluation periods.'"+source[end:]
exec(compile(source,'build_v4_source','exec'))
latex=(ROOT/'code/review_latex.py').read_text(encoding='utf-8').replace("revision/review_v3/latex","revision/review_v4/latex")
(ROOT/'revision/review_v4/latex').mkdir(exist_ok=True)
ns={};exec(compile(latex,'v4_latex_export','exec'),ns);ns['write'](globals())
