"""Complete the existing manuscript from archived results and reference metadata."""
from common import ROOT
import json,re,html,shutil
import pandas as pd

revision=ROOT/'revision'
path=revision/'manuscript_final.md'
t=path.read_text(encoding='utf-8')
snapshot=revision/'manuscript_before_completion.md'
if not snapshot.exists():shutil.copy2(path,snapshot)
if 'RECALIBRATION_RESULTS_TO_INSERT' not in t:
    raise RuntimeError('Completion already applied; review before rerunning.')

ext=revision/'extension'
r=pd.read_csv(ext/'recalibration/comparisons.csv')
s=pd.read_csv(ext/'recalibration/scores.csv')
st=pd.read_csv(ext/'sample_stability.csv')
sizes=st.query("lead=='D28'").groupby(['domain','size']).delta_bu.mean().unstack()
assert sizes.loc['N'].between(-.55,-.52).all()
for domain,value in {'N':.425292,'NE':.401672,'SE':.069653,'SW':.043363}.items():
    row=r.query("domain==@domain and lead=='D28' and measure=='crps'").iloc[0]
    assert abs(row.delta-value)<1e-6

new_results='''Increasing the sample size leaves the main geographical pattern unchanged. Averaged over the three seeds, the northern 28-day CRPS difference between H1 seven-node reconciliation and bottom-up is −0.538 mm with 200 samples, −0.532 mm with 500 and −0.527 mm with 1000. The corresponding northeastern differences remain adverse at +0.099 to +0.104 mm. Southeastern differences remain between −0.070 and −0.065 mm, and southwestern differences between −0.009 and −0.006 mm. These changes are small relative to the year-to-year uncertainty in the main comparisons (Supplementary Table S5).

The additional power-map recalibration narrows the central 80% intervals and brings their coverage closer to the nominal level in every domain (Fig. 8; Supplementary Table S6). Coverage changes from 84.1 to 81.8% in N, 80.9 to 79.1% in NE, 80.8 to 79.6% in SE and 82.3 to 80.3% in SW. Mean interval width falls from 101.29 to 97.66 mm, 75.85 to 74.32 mm, 51.40 to 49.82 mm and 41.09 to 37.63 mm, respectively. All transformed trajectories remain nonnegative and exactly coherent.

Closer interval coverage nevertheless accompanies higher 28-day CRPS. Recalibration increases the score by 0.425 mm in N (95% interval 0.180 to 0.665 mm), 0.402 mm in NE (0.234 to 0.572 mm), 0.070 mm in SE (−0.049 to 0.206 mm) and 0.043 mm in SW (−0.059 to 0.162 mm). The northern and northeastern intervals exclude zero. In N, the reliability component decreases slightly from 0.145 to 0.137 mm, while potential CRPS rises from 20.401 to 20.834 mm. In NE, both components increase. Thus the change in central coverage captures only one aspect of the transformed distribution.

The total-only control produces the same 28-day scores but leaves mean absolute discrepancies between the adjusted total and the unchanged weekly sum of 3.59, 2.67, 1.60 and 1.54 mm in N, NE, SE and SW. Proportional redistribution removes these discrepancies by construction, while transmitting the aggregate adjustment to the weekly forecasts. Figure 8 reports the resulting weekly score changes. For this fitted power map, preserving coherence and improving nominal coverage does not translate into a lower overall distributional loss.'''
t=t.replace('RECALIBRATION_RESULTS_TO_INSERT',new_results)
t=t.replace('These relationships can affect both accumulated amounts and the sequence of wet and dry weeks. These relationships motivate testing whether climate predictors add forecast skill at longer accumulation scales.','These climate influences can affect both accumulated amounts and the sequence of wet and dry weeks, motivating a test of their additional forecast value at longer accumulation scales.')
t=t.replace('We assess the experiment in three steps. It measures the incremental value of aggregate information, distinguishes that value from the effect of adding hierarchy nodes, and diagnoses changes in mean error and predictive uncertainty.','We first measure the incremental value of aggregate information, then distinguish it from the effect of adding hierarchy nodes. Changes in mean error and predictive uncertainty help explain the resulting forecast scores.')
t=t.replace('Scheuerer and Hamill 2015;','Scheuerer and Hamill 2015a;')
t=t.replace('CRPS evaluates the full marginal predictive distribution.','CRPS evaluates the full marginal predictive distribution (Gneiting and Raftery 2007).')
t=t.replace('Upper-tail performance is evaluated with the seasonal training 90th percentile q.','Upper-tail performance is evaluated with the seasonal training 90th percentile q, following the threshold-weighted scoring approach of Gneiting and Ranjan (2011).')
t=t.replace('Energy and variogram scores assess the joint four-week forecasts in the supplementary analysis.','Energy and variogram scores assess the joint four-week forecasts in Supplementary Table S4 (Gneiting and Raftery 2007; Scheuerer and Hamill 2015b).')
t=t.replace('Our results extend that motivation to a controlled S2S information experiment, while the recalibration diagnostic examines whether a further aggregate adjustment can be passed back to the weeks without violating the sums.','The coherent recalibration experiment makes this interaction explicit. Its power map narrows intervals and brings central coverage closer to the nominal level, yet increases CRPS in all four domains. In N, a small reliability improvement is outweighed by a loss in potential CRPS. Assessing the whole predictive distribution is therefore essential when adjusting aggregate uncertainty and redistributing rainfall among weeks.')
t=t.replace('Covariance-based gain predictions explain some seasonal behaviour but remain too uncertain to determine when reconciliation should be used.','Covariance-based gain predictions agree with some seasonal behaviour but remain too uncertain to determine when reconciliation should be used. Further coherent recalibration brings central interval coverage closer to its nominal level, yet raises CRPS, with clear deterioration in the northern and northeastern domains.')
abstract='''Calibrating weekly rainfall and longer accumulations separately can produce forecasts whose amounts no longer add up. We test whether climate information added at the aggregate levels improves coherent forecasts beyond the sum of calibrated weeks. The experiment uses 1060 ECMWF hindcast origins during 2000 to 2019 in four Australian domains, verified against Australian Gridded Climate Data. Censored shifted gamma calibration and nonnegative sample reconciliation are evaluated with nested year-block validation excluding neighbouring years. A factorial comparison separates lagged climate information from the addition of two fortnightly forecasts while holding weekly distributions fixed. Climate information changes reconciled 28-day continuous ranked probability score (CRPS) by −0.31% of climatological score across domains (95% year-bootstrap interval −0.70 to 0.06%); adding the fortnightly layer changes it by 0.003% (−0.16 to 0.16%). Neither contrast passes multiplicity adjustment. In the northern domain, climate-informed reconciliation improves on weekly aggregation by 0.54 mm (0.15 to 0.95 mm), mainly during summer, while reducing excessive interval width. Effects elsewhere are smaller or adverse. Further coherent recalibration brings central interval coverage closer to its nominal level but raises CRPS, with clear deterioration in the northern and northeastern domains. Climate predictors can therefore provide local aggregate value, while additional hierarchy structure alone has little average effect. Forecast evaluation must assess the full rainfall distribution alongside agreement between accumulation scales.'''
assert len(abstract.split())<=250
t=re.sub(r'(?<=## Abstract\n\n).*?(?=\n\nKeywords:)',lambda _:abstract,t,flags=re.S)

# Use publication volume year, rather than the sometimes earlier online-first year.
selection={
'10.1016/j.ejor.2017.02.046':'2017','10.1002/env.2391':'2016',
'10.1175/JHM-D-22-0119.1':'2023','10.1175/1525-7541(2004)005<0243:TSSAMF>2.0.CO;2':'2004',
'10.1071/ES23022':'2024','10.1002/qj.2270':'2014','10.1071/ES24004':'2024',
'10.1016/j.ijforecast.2023.10.003':'2024','10.1175/MWR2904.1':'2005',
'10.1198/016214506000001437':'2007','10.1198/jbes.2010.08110':'2011',
'10.1175/1520-0434(2000)015<0559:DOTCRP>2.0.CO;2':'2000',
'10.1029/2021WR031862':'2022','10.1016/j.ejor.2019.05.020':'2019',
'10.22499/2.5804.003':'2009','10.1175/1520-0442(2003)016<4134:TITSAM>2.0.CO;2':'2003',
'10.1016/j.ejor.2022.07.040':'2023','10.1002/qj.4585':'2024',
'10.1175/2009MWR2861.1':'2009','10.1214/13-STS443':'2013',
'10.1175/MWR-D-13-00248.1':'2014','10.5194/hess-22-1615-2018':'2018',
'10.1175/MWR-D-15-0061.1':'2015a','10.1175/MWR-D-14-00269.1':'2015b',
'10.1175/BAMS-D-16-0017.1':'2017','10.1071/ES22026':'2022',
'10.1175/1520-0493(2004)132<1917:AARMMI>2.0.CO;2':'2004',
'10.1175/2008JCLI2595.1':'2009','10.1080/01621459.2018.1448825':'2019',
'10.1007/s11222-020-09930-0':'2020'}
metadata={}
for f in (revision/'reference_metadata').glob('*.json'):
    d=json.loads(f.read_text(encoding='utf-8'))
    if isinstance(d,dict) and d.get('DOI'):metadata[d['DOI'].lower()]=d
refs=[];keys=[]
def clean(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',s))).replace('‐','-').strip().rstrip('*')
for doi,year in selection.items():
    d=metadata[doi.lower()]
    authors=[]
    for a in d['author']:
        initials=''.join(w[0] for w in re.findall(r'[^\W\d_]+',a.get('given',''),flags=re.U))
        if a['family']=='Jones' and doi=='10.22499/2.5804.003':initials='DA'
        authors.append(a['family']+' '+initials)
    title=clean(d['title'][0]);journal=clean(d['container-title'][0])
    page=d.get('page') or d.get('article-number')
    assert page,(doi,'Missing page/article')
    refs.append(', '.join(authors)+f' ({year}) {title}. {journal} {d["volume"]}, {page.replace("-","–")}. https://doi.org/{doi}')
    aa=d['author'];key=aa[0]['family']+(' et al.' if len(aa)>2 else ' and '+aa[1]['family'] if len(aa)==2 else '')
    keys.append((key,year,doi))
refs += [
'Australian Bureau of Meteorology (2023) Australian Gridded Climate Data (AGCD) v1.0.1 / Australian Water Availability Project (AWAP). National Computational Infrastructure. https://doi.org/10.25914/hjqj-0x55',
'ECMWF (2021) CliMetLab S2S AI Challenge data access package. https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge (accessed 23 October 2026).',
'ECMWF (2026) Issues with data: issue with accumulated fields at day 16. S2S documentation. https://confluence.ecmwf.int/pages/viewpage.action?pageId=639218194 (accessed 23 October 2026).',
'Neubauer L, Filzmoser P (2024) Rediscovering Bottom-Up: Effective Forecasting in Temporal Hierarchies. arXiv preprint, version 1, 2407.02367. https://arxiv.org/abs/2407.02367v1']
keys += [('Australian Bureau of Meteorology','2023','10.25914/hjqj-0x55'),('ECMWF','2021','repository'),('ECMWF','2026','documentation'),('Neubauer and Filzmoser','2024','arXiv:2407.02367v1')]
refs.sort(key=str.casefold)
body=t.split('## References')[0]
for key,year,doi in keys:
    assert key+' '+year in body or key+' ('+year+')' in body,('uncited',key,year)
t=body+'## References\n\n'+'\n\n'.join(refs)+'\n'
assert 'RECALIBRATION_RESULTS_TO_INSERT' not in t and '—' not in t
path.write_text(t,encoding='utf-8')
audit={'abstract_words':len(abstract.split()),'references':len(refs),'citation_keys':keys,'results_source':'revision/extension/recalibration/{scores,comparisons}.csv; revision/extension/sample_stability.csv','status':'Results placeholder filled; references matched to text'}
(revision/'completion_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print('Completed text:',len(abstract.split()),'abstract words;',len(refs),'references')
