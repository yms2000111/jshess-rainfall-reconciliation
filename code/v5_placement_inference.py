from common import ROOT
import numpy as np,pandas as pd,json
R=ROOT/'revision/review_v5';old=ROOT/'revision/review_v4'
a=pd.read_csv(old/'adaptive/annual_scores.csv').query('validation=="LOYO" and domain in ["N","NE","SE","SW"]')
a=pd.concat([a,pd.read_csv(old/'coverage/annual_scores.csv'),pd.read_csv(R/'placement/annual_scores.csv')],ignore_index=True)
a=a.query('lead=="D28"');idx=np.random.default_rng(2026102541).integers(0,20,(50000,20));rows=[]
for m,b in [('H2','H1'),('Hweekly','H1'),('Hweekly','Weekly_climate_BU'),('H2','Weekly_climate_BU')]:
 seq=[]
 for k in ['N','NE','SE','SW','NW','CA','EC','TAS']:
  t=a.query('domain==@k').pivot(index='year',columns='method',values='crps').sort_index();seq.append(100*(t[m]-t[b]).values/t.Raw.mean())
 d=np.array(seq).mean(0);lo,hi=np.quantile(d[idx].mean(1),[.025,.975]);rows.append(dict(method=m,baseline=b,delta=d.mean(),lower=lo,upper=hi,favourable_domains=int((np.mean(seq,axis=1)<0).sum())))
pd.DataFrame(rows).to_csv(R/'placement/pooled_comparisons.csv',index=False)
a.groupby(['domain','method']).crps.mean().unstack().to_csv(R/'placement/scores.csv')
print(pd.DataFrame(rows).to_string(index=False))
