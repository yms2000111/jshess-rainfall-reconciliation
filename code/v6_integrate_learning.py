from common import ROOT
import re,json
R=ROOT/'revision/review_v6'
p=R/'manuscript.md'
s=p.read_text(encoding='utf-8')
if '### 4.8' not in s:
 s=s.replace('The results motivate testing whether retaining rainfall-only components limits climate-adjustment noise; they do not establish that mechanism or a stable advantage over simple alternatives.','Larger climate-fitting samples and stronger regularisation reduce the all-node penalty in both systems, consistent with unstable climate adjustments contributing to the differences. Temporal benefit remains uncertain.')
 s=s.replace('A common-covariance experiment separates information placement from changes in reconciliation weights.','Common-covariance and conditional learning experiments separate information placement, reconciliation weights and climate-coefficient stability.')
 s=s.replace('### 3.5 Controls, transfer checks and common-covariance comparison','### 3.5 Controls and mechanism experiments')
 anchor='All 312 system–domain–year combinations are retained; comparisons and score interactions are exploratory, with descriptive common-year intervals (Supplementary Note 9).'
 s=s.replace(anchor,anchor+' A conditional learning experiment fixes the rainfall-only distributions, templates and H0 covariance while fitting climate coefficients on nested subsets of 10, 15 or all permitted years. Adjacent-year exclusions leave 16–18 years, not 19. Full-sample penalties of 0.05, 0.20 and 0.50 assess regularisation. These settings are compared without choosing a winner from outer scores (Supplementary Note 10).')
 result='''### 4.8 More climate-fitting data and stronger regularisation reduce the penalty

With common H0 covariance, the H2-minus-H1 contrast decreases from +1.712% to +0.757% of raw CRPS as ECMWF climate fitting expands from ten to all permitted years. The paired difference is +0.955 percentage points (95% descriptive interval 0.633–1.277). ACCESS-S2 gives a corresponding decrease from +8.502% to +3.849%, a difference of +4.653 points (2.723–6.907). Fifteen-year fits lie between these endpoints (Supplementary Table S29; Fig. S12).

Increasing the full-sample penalty from 0.05 to 0.50 reduces H2 minus H1 to −0.010% in ECMWF and +0.729% in ACCESS-S2. H1's advantage over BU-clim also contracts, from −0.906% to −0.325% and from −4.514% to −1.041%, respectively. Both experiments are consistent with unstable climate adjustments contributing to the comparison. Because the rainfall-only model remains fixed, this is a learning curve for the climate adjustment, not the complete forecasting pipeline.

'''
 s=s.replace('## 5 Discussion',result+'## 5 Discussion')
 s=s.replace('Retaining rainfall-only components may constrain unstable climate adjustments, but learning curves and regularisation experiments are needed to separate estimation noise from duplicated signals and altered dependence.','The conditional learning curves strengthen this interpretation: larger climate-fitting samples and stronger penalties reduce H2 deterioration in both systems. They also narrow H1’s advantage over BU-clim. Retaining rainfall-only components can therefore act as a statistical constraint on variable climate adjustments in these experiments. The tests do not isolate that contribution from changes in marginal bias and spread.')
 s=s.replace('The result motivates tests of estimation noise and cross-scale information overlap without establishing either mechanism.','More climate-fitting years and stronger regularisation reduce the penalty in both systems, supporting an estimation-stability explanation. This does not establish a physical mechanism or select an operational penalty.')
 p.write_text(s,encoding='utf-8')
main=s.split('## 1 Introduction')[1].split('## Data availability')[0]
abstract=s.split('## Abstract')[1].split('Keywords:')[0]
print('Main split words',len(main.split()),'abstract',len(abstract.split()))
# Verify all completed optimisations and the exclusions actually recorded.
fail=[];counts={};bounds=[]
for f in (R/'learning').glob('*.json'):
 d=json.loads(f.read_text());year=d['year']
 for name,q in d['scenarios'].items():
  assert not set(q['years']).intersection({year-1,year,year+1})
  counts[name]=counts.get(name,0)+1
  if name=='full':bounds.append(len(q['years']))
  for j,r in enumerate(q['records']):
   if not r.get('success',True):fail.append([f.name,name,j])
audit=dict(folds=sum(1 for _ in (R/'learning').glob('*.json')),scenario_counts=counts,full_year_range=[min(bounds),max(bounds)],unsuccessful_optimisations=fail)
(R/'learning/fit_audit_summary.txt').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit))
