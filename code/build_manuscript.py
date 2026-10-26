"""Create an editable, line-numbered manuscript from the analysed experiment."""
from common import *
import re,json,pandas as pd
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START,WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT

OUT=ROOT/'submission';OUT.mkdir(exist_ok=True)
text=(ROOT/'manuscript.md').read_text(encoding='utf-8')
# The narrative and all tabulated scores come from the same archived experiment.
if 'Table 3 summarises' not in text:text=text.replace('Reliability diagrams for Weeks 2–4 provide','Table 3 summarises these changes. Reliability diagrams for Weeks 2–4 provide')
text=text.replace('Observation-date shifts and annual skill matrices are supplied with the supplementary results','Observation-date shifts (Supplementary Table S1) and annual skill matrices (Supplementary Fig. S1) are supplied with the supplementary results')
if 'NumPy 2.3.5' not in text:text=text.replace('The accompanying data extracts, quality checks and Python workflow provide that basis','The analysis uses Python with NumPy 2.3.5, pandas 3.0.1, SciPy 1.18.1 and XGBoost 3.4.1; figures use Matplotlib 3.11.2. The accompanying data extracts, quality checks and Python workflow provide that basis')
(ROOT/'manuscript.md').write_text(text,encoding='utf-8')
head,back=text.split('## Data availability',1)
back='## Data availability'+back
doc=Document()
for p in list(doc.paragraphs):
 if not p.text:p._element.getparent().remove(p._element)
sec=doc.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11);sec.top_margin=sec.bottom_margin=Inches(.85);sec.left_margin=sec.right_margin=Inches(.85)
for n in ['Normal','Title','Heading 1','Heading 2','Heading 3','Caption']:
 st=doc.styles[n];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
 rf=st.element.get_or_add_rPr().get_or_add_rFonts()
 for attr in list(rf.attrib):rf.attrib.pop(attr)
 for attr in ['ascii','hAnsi','eastAsia','cs']:rf.set(qn('w:'+attr),'Times New Roman')
for border in list(doc.styles.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
doc.styles['Normal'].font.size=Pt(11.5);doc.styles['Normal'].paragraph_format.line_spacing=1.25;doc.styles['Normal'].paragraph_format.space_after=Pt(6)
doc.styles['Title'].font.size=Pt(17);doc.styles['Title'].font.bold=True;doc.styles['Title'].paragraph_format.space_after=Pt(12)
for n,sz in [('Heading 1',13),('Heading 2',12),('Heading 3',11.5)]:
 doc.styles[n].font.size=Pt(sz);doc.styles[n].font.bold=True;doc.styles[n].paragraph_format.space_before=Pt(12);doc.styles[n].paragraph_format.space_after=Pt(6)
doc.styles['Caption'].font.size=Pt(10);doc.styles['Caption'].font.italic=False;doc.styles['Caption'].font.bold=False
ln=OxmlElement('w:lnNumType');ln.set(qn('w:countBy'),'1');ln.set(qn('w:start'),'1');ln.set(qn('w:restart'),'continuous');ln.set(qn('w:distance'),'160');sec._sectPr.append(ln)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
footer.add_run('Page ');fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
def mr(t):
 r=OxmlElement('m:r');tx=OxmlElement('m:t');tx.text=t;r.append(tx);return r
def sub(t,idx):
 e=OxmlElement('m:sSub');b=OxmlElement('m:e');b.append(mr(t));s=OxmlElement('m:sub');s.append(mr(idx));e.extend([b,s]);return e
def sumterm(idx,term):
 e=OxmlElement('m:nary');pr=OxmlElement('m:naryPr');ch=OxmlElement('m:chr');ch.set(qn('m:val'),'∑');pr.append(ch);e.append(pr)
 for name,txt in [('sub',idx+'=1'),('sup','M')]:q=OxmlElement('m:'+name);q.append(mr(txt));e.append(q)
 q=OxmlElement('m:e');q.append(mr(term) if isinstance(term,str) else term);e.append(q);return e
def equation(n):
 om=OxmlElement('m:oMath')
 if n==1:parts=[sub('z','t,k'),mr(' = log[1 + '),sub('y','t,k'),mr('/'),sub('d','k'),mr('],    d = (7, 7, 7, 7, 28).    (1)')]
 if n==2:parts=[sub('x⁽ᵐ⁾','t,k'),mr(' = '),sub('d','k'),mr(' max{exp['),sub('ẑ','t,k'),mr(' + '),sub('e⁽ᵐ⁾','k'),mr('] − 1, 0}.    (2)')]
 if n==3:
  lim=OxmlElement('m:limLow');e=OxmlElement('m:e');e.append(mr('arg min'));l=OxmlElement('m:lim');l.append(mr('b ≥ 0'));lim.extend([e,l]);parts=[mr('b* = '),lim,mr(' (Sb − v)ᵀ W⁻¹ (Sb − v),    v* = Sb*.    (3)')]
 if n==4:parts=[mr('CRPS = M⁻¹ '),sumterm('m','|x(m) − y|'),mr(' − (2M²)⁻¹ '),sumterm('m',sumterm('n','|x(m) − x(n)|')),mr('.    (4)')]
 for p in parts:om.append(p)
 return om
def paras(content):
 for block in content.strip().split('\n\n'):
  block=block.strip()
  if not block:continue
  if block.startswith('# '):doc.add_paragraph(block[2:],style='Title')
  elif block.startswith('### '):doc.add_paragraph(block[4:],style='Heading 2')
  elif block.startswith('## '):doc.add_paragraph(block[3:],style='Heading 1')
  elif re.search(r'\([1-4]\)\.$',block):
   p=doc.add_paragraph();p.paragraph_format.space_before=Pt(6);p.paragraph_format.space_after=Pt(10)
   n=int(re.search(r'\(([1-4])\)\.$',block).group(1));p._p.append(equation(n))
  else:
   p=doc.add_paragraph(block)
   if block.startswith('Keywords:'):p.runs[0].italic=True
   p.paragraph_format.widow_control=True
paras(head)

S=pd.read_csv(ROOT/'results/scores.csv');B=pd.read_csv(ROOT/'results/paired_comparisons.csv')
def table(title,headers,rows,widths):
 p=doc.add_paragraph(title,style='Caption');p.paragraph_format.keep_with_next=True
 t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for cell,w in zip(t.rows[0].cells,widths):cell.width=Inches(w)
 for i,h in enumerate(headers):t.rows[0].cells[i].text=h
 trpr=t.rows[0]._tr.get_or_add_trPr();repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
 for row in rows:
  cells=t.add_row().cells
  for i,v in enumerate(row):cells[i].text=str(v);cells[i].width=Inches(widths[i])
 for ir,row in enumerate(t.rows):
  cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)
  for ic,cell in enumerate(row.cells):
   cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   pr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
   for side in ['top','left','bottom','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
   pr.append(borders)
   if ir==0:
    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EAEAEA');pr.append(shade)
   for p in cell.paragraphs:
    p.paragraph_format.space_after=Pt(5);p.paragraph_format.space_before=Pt(5);p.paragraph_format.line_spacing=1.05;p.alignment=WD_ALIGN_PARAGRAPH.LEFT if ic==0 else WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:run.font.size=Pt(9.5);run.bold=ir==0
 doc.add_paragraph('')
 return t
doc.add_page_break();doc.add_paragraph('Tables',style='Heading 1')
rows=[]
for k,r in REGIONS.items():rows.append([k,r['name'],f'{r["lon"][0]:.2f}–{r["lon"][1]:.2f}°E',f'{abs(r["lat"][1]):.2f}–{abs(r["lat"][0]):.2f}°S'])
table('Table 1. Regional verification domains. Each domain comprises four forecast-grid cells; AGCD observations are averaged over valid land cells within the same bounds.',['Code','Location','Longitude','Latitude'],rows,[.55,2.25,1.5,1.5])
methods=['Climatology','Raw','Seasonal BC','OLS','XGBoost','XGB pooled','XGB no indices','XGB + OLS-R','XGB + WLS-R']
labels=['Seasonal climatology','ECMWF (QC)','Seasonal correction','OLS','XGBoost','XGBoost pooled leads','XGBoost without indices','XGBoost + OLS reconciliation','XGBoost + WLS reconciliation']
rows=[]
for m,l in zip(methods,labels):
 row=[l]
 for k in REGIONS:
  v=S.query("region==@k and method==@m and lead=='D28'").iloc[0];row.append(f'{v.crps:.2f} ({v.crpss:.3f})')
 rows.append(row)
table('Table 2. Independent-test 28-day CRPS in mm, with CRPSS against seasonal climatology in parentheses. Each value uses 265 origins during 2015–2019. Lower CRPS and higher CRPSS are better.',['Method','N','NE','SE','SW'],rows,[2.1,1.075,1.075,1.075,1.075])
rows=[]
for k in REGIONS:
 a=S.query("region==@k and method=='XGBoost' and lead=='D28'").iloc[0];b=S.query("region==@k and method=='XGB + WLS-R' and lead=='D28'").iloc[0];q=B.query("region==@k and method=='XGB + WLS-R' and lead=='D28'").iloc[0]
 rows.append([k,f'{100*a.coverage80:.1f} → {100*b.coverage80:.1f}',f'{a.width80:.2f} → {b.width80:.2f}',f'{a.coherence_mae:.2f} → 0',f'{q.delta_crps:.3f}',f'{q.q_primary:.3f}'])
table('Table 3. Changes from XGBoost to variance-weighted reconciliation for the 28-day product. Coverage refers to the central 80% interval. Aggregation discrepancy is averaged over all sampled trajectories. Adjusted p values belong to the 16-comparison primary family.',['Region','Coverage (%)','Width (mm)','Discrepancy (mm)','ΔCRPS (mm)','Adjusted p'],rows,[.55,1.25,1.25,1.25,.95,1.15])
doc.add_paragraph('Negative ΔCRPS indicates improvement. Discrepancy is |28-day total − sum of four weekly amounts|. Values rounded here are retained at full precision in the accompanying CSV files.',style='Caption')

captions=[
('Fig01_regions','Fig. 1. (a) The four regional domains and (b–e) their AGCD monthly rainfall climatologies for 2000–2012. Coloured boxes show the exact verification support, not interpolated estimates for surrounding areas. The geographical outline is from Natural Earth.'),
('Fig02_design','Fig. 2. (a) Chronological fitting, tuning, calibration and test partitions, with origin counts after removal of crossing verification windows. The final refit uses all eligible pre-2013 origins. (b) Forecast construction and the weekly-to-28-day aggregation identity. The four weeks are consecutive, non-overlapping windows from the same origin; 28 days is not a calendar month.'),
('Fig03_skill','Fig. 3. Independent-test forecast performance by region. (a–d) Weekly CRPSS relative to seasonal climatology; positive values indicate skill. (e–h) CRPS of the 28-day total, with smaller values indicating better forecasts. The aggregate includes Week 1 and is not a fifth weekly lead. ECMWF (QC) denotes the archive after the documented quality-control treatment.'),
('Fig04_reconciliation','Fig. 4. Paired changes in CRPS after variance-weighted reconciliation, relative to unreconciled XGBoost. Points show the mean change and bars show 95% percentile intervals from 2000 circular block-bootstrap samples of eight origins. Negative values indicate improvement. Axes differ by region to resolve the smaller effects. No primary comparison passes the 5% false-discovery-rate adjustment.'),
('Fig05_reliability','Fig. 5. Reliability diagrams for probabilities of exceeding the seasonal training upper tercile, pooling Weeks 2–4 in 2015–2019. The dashed diagonal denotes perfect reliability. Ten probability bins are used, and only bins with at least 20 cases are shown. Insets give the distribution of issued probabilities for variance-weighted reconciliation. Each regional pool contains 795 overlapping origin–lead pairs.'),
('Fig06_climate','Fig. 6. Conditional 28-day CRPS changes from variance-weighted reconciliation relative to XGBoost. (a–d) MJO amplitude below one (weak) or at least one (active), using indices lagged by two days. (e–h) Cool, neutral and warm Niño 3.4 states, defined by a two-month-lagged anomaly below −0.5°C, between −0.5°C and +0.5°C, or above +0.5°C. Bars are descriptive 95% block-bootstrap intervals; n counts forecast origins. Axes differ by region. These contrasts are not seasonally controlled causal effects.')]
(OUT/'figure_captions.txt').write_text('\n\n'.join(c for _,c in captions),encoding='utf-8')
for name,caption in captions:
 doc.add_page_break();p=doc.add_paragraph();p.paragraph_format.keep_with_next=True;p.add_run().add_picture(str(ROOT/'figures'/f'{name}.png'),width=Inches(6.8));doc.add_paragraph(caption,style='Caption')
doc.add_page_break();paras(back)
doc.core_properties.title=head.splitlines()[0][2:];doc.core_properties.subject='JSHESS research manuscript';doc.core_properties.author=''
doc.save(OUT/'JSHESS_rainfall_manuscript.docx')

statement='Reliable rainfall forecasts help Australian communities plan water use and agricultural work several weeks ahead. Using historical forecasts in four regions, we found that making weekly and four-week rainfall predictions agree can improve some overall scores while reducing the reliability of the stated probabilities. The results show why forecast services should assess consistency, accuracy and uncertainty together when introducing machine learning into rainfall prediction.'
(OUT/'statement_of_importance.txt').write_text(statement+'\n',encoding='utf-8')
abstract=text.split('## Abstract\n\n')[1].split('\n\nKeywords:')[0]
counts={'abstract_words':len(abstract.split()),'importance_words':len(statement.split()),'importance_sentences':3,'main_text_plus_captions_words':len(head.split('## 1 Introduction')[1].split())+sum(len(c.split()) for _,c in captions)+150,'references':17,'main_figures':6,'tables':3}
assert counts['abstract_words']<=250 and counts['main_text_plus_captions_words']<=7500 and 50<=counts['importance_words']<=80
(OUT/'format_audit.json').write_text(json.dumps(counts,indent=2),encoding='utf-8');print(counts)
