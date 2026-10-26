"""Post hoc baseline audit and conditional precision, 26 October 2026.
No changes to the frozen 2020 test or its decision threshold.
"""
from common import ROOT
import numpy as np,pandas as pd,json
from scipy.stats import norm
R=ROOT/'revision/review_v6';R.mkdir(exist_ok=True);V5=ROOT/'revision/review_v5';keys=['N','NE','SE','SW','NW','CA','EC','TAS']
a=pd.read_csv(V5/'access_s2/annual_scores.csv').query('lead=="D28"');means=a.groupby(['domain','method']).crps.mean().unstack().reindex(keys);means.to_csv(R/'access_baseline_scores.csv')
op=pd.read_csv(V5/'operational/case_scores.csv').query('lead=="D28"');om=op.groupby(['domain','method']).crps.mean().unstack().reindex(keys);om.to_csv(R/'2020_baseline_scores.csv')
seq=[]
for k in keys:
 t=op.query('domain==@k').pivot(index='date',columns='method',values='crps').sort_index();f=np.load(V5/f'operational/predictions/{k}.npz');scale=float(f['normalisation_raw_training_crps']);seq.append((t.H1-t.Weekly_climate_BU).values/scale*100)
d=np.array(seq).mean(0);rows=[]
for b in [4,6,8]:
 starts=np.random.default_rng(2026102520+b).integers(0,53,(50000,int(np.ceil(53/b))));ix=((starts[:,:,None]+np.arange(b))%53).reshape(50000,-1)[:,:53];boot=d[ix].mean(1);se=boot.std(ddof=1);lo,hi=np.quantile(boot,[.025,.975]);mde=(norm.ppf(.975)+norm.ppf(.8))*se
 rows.append(dict(block_length=b,estimate=d.mean(),lower=lo,upper=hi,conditional_bootstrap_se=se,normal_approximation_mde80=mde))
pd.DataFrame(rows).to_csv(R/'2020_precision.csv',index=False)
# The factorial contrast is descriptive and uses the existing annual scores.
aa=pd.concat([pd.read_csv(ROOT/'revision/review_v4/adaptive/annual_scores.csv').query('validation=="LOYO" and domain in ["N","NE","SE","SW"]'),pd.read_csv(ROOT/'revision/review_v4/coverage/annual_scores.csv'),pd.read_csv(V5/'placement/annual_scores.csv')]).query('lead=="D28"')
ds=[]
for k in keys:
 t=aa.query('domain==@k').pivot(index='year',columns='method',values='crps').sort_index();ds.append(100*((t.H2-t.Hweekly)-(t.H1-t.H0)).values/t.Raw.mean())
dd=np.array(ds).mean(0);ix=np.random.default_rng(2026102601).integers(0,20,(50000,20));lo,hi=np.quantile(dd[ix].mean(1),[.025,.975])
record=dict(date='2026-10-26',access_buclim_worse_than_burain=int((means.Weekly_climate_BU>means.Bottom_up).sum()),access_buclim_worse_than_raw=means.index[means.Weekly_climate_BU>means.Raw].tolist(),new2020_H1_better_than_burain=om.index[om.H1<om.Bottom_up].tolist(),factorial_interaction=dict(estimate=float(dd.mean()),lower=float(lo),upper=float(hi),definition='(H2-Hweekly)-(H1-H0), percent of raw domain CRPS, equal domain and year weights',scope='Post hoc descriptive contrast; separately re-estimated W prevents attributing it solely to climate adjustment.'),precision_assumptions='Post hoc conditional planning sensitivity. Normal approximation, two-sided 5% criterion and 80% power, SE from within-2020 circular blocks. Does not estimate interannual power; does not replace the predeclared percentile interval or confer evidence for the null.')
(R/'baseline_audit.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps(record,indent=2));print(pd.DataFrame(rows).to_string(index=False));print(means.to_string());print(om.to_string())
