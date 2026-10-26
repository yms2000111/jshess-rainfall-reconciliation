"""Final scope edit after the humanizer pass; numerical results unchanged."""
from common import ROOT
import json,re
R=ROOT/'revision/review_v5';p=R/'manuscript.md';t=p.read_text(encoding='utf-8')
old='Dependence reconstruction changes absolute calibration, although matched ECC retains the local H1-minus-H0 direction. The power-map audit also shows why fitting and application populations must match. A separate mixture experiment examines the marginal value of complexity, defined as the additional held-out skill obtained by allowing weights to respond to forecast state. The tested adaptive weights do not consistently improve on fixed weights (Supplementary Note 4); this result concerns that specification rather than adaptive forecasting in general.'
new='Dependence reconstruction changes absolute calibration, although matched ECC retains the local H1-minus-H0 direction. The power-map audit also shows why fitting and application populations must match. These checks help distinguish the information supplied by direct aggregates from changes caused by dependence or dispersion.'
assert old in t;t=t.replace(old,new)
t=t.replace('More nodes, more climate adjustments and more flexible combination weights each require their own evidence of added skill.','More nodes and more climate adjustments each require evidence of added skill.')
t=t.replace('Its interpretation depends on the comparator: within reconciliation,','The interpretation depends on the comparator: within reconciliation,')
p.write_text(t,encoding='utf-8')
a=json.loads((R/'editorial_audit.json').read_text());a['body_words_before_references']=len(t.split('## References')[0].split());a['main_mixture_discussion_removed']=True;(R/'editorial_audit.json').write_text(json.dumps(a,indent=2),encoding='utf-8')
plan=R/'analysis_record.md'
with plan.open('a',encoding='utf-8') as f:f.write('\n\n## Scope expansion recorded 25 October 2026\n\nThe original editorial scope above was expanded at the author’s request. The subsequently dated new_experiments_plan_20261025.md, operational_test_plan_20261025.md and circulation/plan.md govern the added fits and diagnostics. Hweekly/H2, 99 predictor permutations, eight-domain ACCESS-S2, the 2020 new-period test and circulation diagnostics are now complete. The 2020 confirmation condition was not met. The historical eight-domain test remains exploratory. No public deposit or DOI has been created.\n')
print(a)
