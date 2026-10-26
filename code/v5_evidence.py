"""Post hoc synthesis of existing held-out scores, recorded 25 October 2026."""
from common import ROOT
import numpy as np
import pandas as pd
import json,itertools

R=ROOT/'revision/review_v5';R.mkdir(exist_ok=True)
V4=ROOT/'revision/review_v4'
(R/'analysis_record.md').write_text('''# Analysis record dated 25 October 2026

All eight ECMWF domain effects and the northern forward scores were already inspected before this synthesis. The eight-domain contrasts are exploratory, not newly preregistered confirmatory tests. Original primary comparisons retain their separate status.

Use equal domain weights after normalising each annual paired CRPS difference by that domain\'s full-record raw CRPS. Resample common complete years across all eight domains. Report percentile intervals and two-sided annual sign-flip tests with Holm adjustment over H1 versus Raw, BU-rain, BU-clim and H0. Preserve all domains and years. Enumerate every five-year northern score omission without refitting and report the entire distribution.

Move probability mixtures, forecast selection and their decision analyses to the supplement, retaining their methods and results. Keep the main question on climate-information placement and incremental reconciliation value. This revision adds no H2, additional ACCESS-S2 domains or untouched operational validation; those require new fits and data. It does not deposit files publicly.
''',encoding='utf-8')
a=pd.read_csv(V4/'adaptive/annual_scores.csv').query('validation=="LOYO" and domain in ["N","NE","SE","SW"] and lead=="D28"')
b=pd.read_csv(V4/'coverage/annual_scores.csv').query('lead=="D28"')
a=pd.concat([a,b],ignore_index=True)
keys=['N','NE','SE','SW','NW','CA','EC','TAS']
idx=np.random.default_rng(2026102501).integers(0,20,(50000,20))
sign=np.random.default_rng(2026102502).choice([-1,1],(100000,20))
rows=[];domain_rows=[]
for ref in ['Raw','Bottom_up','Weekly_climate_BU','H0']:
 seq=[]
 for k in keys:
  t=a.query('domain==@k').pivot(index='year',columns='method',values='crps').sort_index()
  assert list(t.index)==list(range(2000,2020))
  d=(t.H1-t[ref]).to_numpy();v=d/t.Raw.mean()*100;seq.append(v)
  lo,hi=np.quantile(d[idx].mean(1),[.025,.975])
  domain_rows.append(dict(domain=k,baseline=ref,delta=d.mean(),lower=lo,upper=hi,normalised_delta=v.mean()))
 seq=np.array(seq);d=seq.mean(0);lo,hi=np.quantile(d[idx].mean(1),[.025,.975]);p=(1+(abs((sign*d).mean(1))>=abs(d.mean())).sum())/(len(sign)+1)
 rows.append(dict(baseline=ref,delta=d.mean(),lower=lo,upper=hi,p=p,favourable_domains=int((seq.mean(1)<0).sum()),domains=8))
order=np.argsort([r['p'] for r in rows]);adj=0
for rank,i in enumerate(order):
 adj=max(adj,min(1,rows[i]['p']*(len(rows)-rank)));rows[i]['holm_p']=adj
pd.DataFrame(rows).to_csv(R/'eight_domain_comparisons.csv',index=False)
pd.DataFrame(domain_rows).to_csv(R/'domain_comparisons.csv',index=False)
t=a.query('domain=="N"').pivot(index='year',columns='method',values='crps').sort_index()
out=[];summary=[]
for ref in ['Bottom_up','H0','Weekly_climate_BU']:
 d=(t.H1-t[ref]).to_numpy();vals=[]
 for ix in itertools.combinations(range(20),5):
  v=(d.sum()-d[list(ix)].sum())/15;vals.append(v)
  out.append(dict(baseline=ref,omitted_years=' '.join(str(2000+i) for i in ix),delta=v))
 q=np.quantile(vals,[0,.025,.25,.5,.75,.975,1])
 summary.append(dict(baseline=ref,minimum=q[0],q025=q[1],q25=q[2],median=q[3],q75=q[4],q975=q[5],maximum=q[6],fraction_favourable=float((np.array(vals)<0).mean()),combinations=len(vals)))
pd.DataFrame(out).to_csv(R/'all_five_year_omissions.csv',index=False)
pd.DataFrame(summary).to_csv(R/'omission_summary.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
print(pd.DataFrame(summary).to_string(index=False))
