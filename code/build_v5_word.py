"""Build focused V5 Word and LaTeX documents from one prose source."""
from common import ROOT
setup=(ROOT/'code/build_v4_word.py').read_text(encoding='utf-8').split("exec(compile(source,'build_v4_source','exec'))")[0]
exec(compile(setup,'v5_builder_setup','exec'))
source=source.replace('from v4_equations import EQUATIONS','from v5_equations import EQUATIONS')
source=source.replace('    result=original_math(n)',"    if n==12:\n        from v5_math_layout import equation_array\n        return equation_array(n,EQUATIONS,original_math,DISPLAY[n])\n    result=original_math(n)")
source=source.replace('p.alignment=WD_ALIGN_PARAGRAPH.CENTER\n            p.paragraph_format.space_before', 'p.alignment=WD_ALIGN_PARAGRAPH.CENTER\n            p.paragraph_format.keep_together=True\n            p.paragraph_format.space_before')
# JSHESS specifies 7500 words including captions/table descriptions, excluding
# abstract/references. Keep table-cell totals in the audit without imposing a
# stricter, undocumented all-inclusive limit (official instructions, 2026-10-25).
source=source.replace("assert audit['all_inclusive_words']<=7500","assert audit['main_and_captions_words']<=7500")
source=source.replace("V4/'supplementary_notes.md'","ROOT/'revision/review_v5/supplementary_notes_math.md'")
source=source.replace("OUT=ROOT/'revision/review_v4/submission'","OUT=ROOT/'revision/review_v5/submission'").replace("F=ROOT/'revision/review_v4/figures'","F=ROOT/'revision/review_v5/figures'").replace("ROOT/'revision/review_v4/manuscript.md'","ROOT/'revision/review_v5/manuscript.md'")
source=source.replace('doc=document();doc.core_properties.title=',(ROOT/'code/v5_tables.py').read_text(encoding='utf-8')+'\ndoc=document();doc.core_properties.title=',1)
source=source.replace("OUT=ROOT/'revision/review_v5/submission'","OUT=ROOT/'revision/review_v5/submission_math_review'")
source=source.replace('p.paragraph_format.line_spacing=1.1;p.paragraph_format.space_after=Pt(8)','p.paragraph_format.line_spacing=1.1;p.paragraph_format.space_after=Pt(6)')
source=source.replace("pp=pd.read_csv(V4/'placebo/scores.csv')","pp=pd.read_csv(R5/'placebo/scores.csv')")
source=source.replace("rows=[[str(int(r.permutation)),f'{r.crps:.3f}'] for r in pp.itertuples()]","rows=[[str(i),f'{pp.iloc[i].crps:.3f}',str(i+50),f'{pp.iloc[i+50].crps:.3f}'] for i in range(50)]")
source=source.replace("['Permutation','28-day CRPS (mm)'],rows,[3.4,3.4]","['Permutation','CRPS (mm)','Permutation','CRPS (mm)'],rows,[1.7,1.7,1.7,1.7]")
source=source.replace('Table S14. Northern score omissions.','Table S14a. Northern score omissions.')
source=source.replace('Twenty full year-block predictor permutations.','Ninety-nine full year-block predictor permutations.').replace('The Monte Carlo p value is 1/21 = 0.048','Two of the 99 permuted scores are lower than the unpermuted score; the Monte Carlo p value is (2+1)/(99+1) = 0.030')
# Correct annual ACCESS bounds to the eight-domain analysis; seasonal legacy bounds retain their own resampling.
source=source.replace("annual_access=pd.read_csv(V4/'access_s2/comparisons.csv').query('lead==\"D28\"').set_index('baseline')","annual_access=pd.read_csv(R5/'access_s2/domain_comparisons.csv').query('domain==\"N\" and method==\"H1\"').set_index('baseline')")
source=source.replace("for field in ['delta','lower','upper']:aa.loc[idx,field]=annual_access.loc[r.baseline,field]","if r.baseline in annual_access.index:\n  for field in ['delta','lower','upper']:aa.loc[idx,field]=annual_access.loc[r.baseline,field]")
source=source.replace("# Put the S1c block",(ROOT/'code/v5_supplement.py').read_text(encoding='utf-8')+'\n# Put the S1c block',1)
# Reorder tables before notes and figures, preserving every caption and native equation.
source=source.replace("supp.save(OUT/'JSHESS_supplementary_material.docx')",'''body=supp._element.body
blocks=[]
for e in list(body):
 if e.tag==qn('w:p'):
  value=''.join(e.itertext())
  match=re.match(r'Table S(\\d+)([a-z]?)\\.',value)
  if match and e.getnext() is not None and e.getnext().tag==qn('w:tbl'):
   blocks.append(((int(match.group(1)),match.group(2)),e,e.getnext()))
anchor=next(e for e in body if e.tag==qn('w:p') and ''.join(e.itertext()).startswith('Supplementary Note'))
for _,cap,tbl in sorted(blocks,key=lambda b:b[0]):anchor.addprevious(cap);anchor.addprevious(tbl)
# Move all eight supplementary figures to the end, in numerical order.
for i in range(1,9):
 cap=next(e for e in body if e.tag==qn('w:p') and ''.join(e.itertext()).startswith('Fig. S'+str(i)+'.'))
 picture=cap.getprevious();assert list(picture.iter(qn('w:drawing')))
 sect=body.find(qn('w:sectPr'));sect.addprevious(picture);sect.addprevious(cap)
supp.save(OUT/'JSHESS_supplementary_material.docx')''')
start=source.index("statement='");end=source.index("\n(OUT/'statement_of_importance",start)
source=source[:start]+"statement='Weekly rainfall forecasts and longer accumulations should give a consistent picture for planning. This study separates the contribution of climate predictors from the value of combining accumulation scales in eight Australian domains. Direct aggregate forecasts improve on climate-informed weekly sums in retrospective comparisons, but a new forecast-year test remains inconclusive. The findings show why forecast services should retain simple coherent references and test information placement before adding predictors.'"+source[end:]
exec(compile(source,'build_v5_source','exec'))
latex=(ROOT/'code/review_latex.py').read_text(encoding='utf-8').replace('revision/review_v3/latex','revision/review_v5/latex_math_review').replace('justification=raggedright','justification=justified').replace(r'\fontsize{11.5}{14}\selectfont\hangindent',r'\fontsize{11.5}{14}\selectfont\raggedright\hangindent')
(ROOT/'revision/review_v5/latex_math_review').mkdir(exist_ok=True)
ns={};exec(compile(latex,'v5_latex_export','exec'),ns);ns['write'](globals())
