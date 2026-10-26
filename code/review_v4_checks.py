"""Score-only robustness and a matched-period validation comparison."""
from common import ROOT
import pandas as pd,numpy as np,itertools,json
R=ROOT/'revision/review_v4';R.mkdir(exist_ok=True)
V3=ROOT/'revision/review_v3'
a=pd.read_csv(V3/'annual_influence.csv').query("domain=='N'")
selected=[2000,2008,2010,2016,2019]
rows=[]
for base,t in a.groupby('baseline'):
 t=t.sort_values('year');d=t.annual_delta.to_numpy();years=t.year.to_numpy()
 for label,omit in [('All years',[]),('Reviewer five years',selected),('Boundary years',[2000,2019])]:
  take=~np.isin(years,omit);rows.append(dict(baseline=base,omission=label,omitted_years=','.join(map(str,omit)),remaining_years=int(take.sum()),delta=float(d[take].mean()),better_years=int((d[take]<0).sum()),removed_share_of_net_change=float(d[~take].sum()/d.sum())))
 ix=np.asarray(list(itertools.combinations(range(20),5)));remaining=(d.sum()-d[ix].sum(1))/15
 rows.append(dict(baseline=base,omission='Exhaustive five-year omissions',remaining_years=15,delta=np.nan,minimum=float(remaining.min()),maximum=float(remaining.max()),fraction_favourable=float((remaining<0).mean()),combinations=len(ix)))
pd.DataFrame(rows).to_csv(R/'multiyear_influence.csv',index=False)

old=pd.read_csv(ROOT/'revision/extension/case_scores.csv.gz')
controls=pd.read_csv(V3/'control_case_scores.csv.gz')
cv=pd.concat([old,controls]).query("lead=='D28' and year>=2015 and method in ['Raw','Bottom_up','H0_7_NN','H1_7_NN','Weekly_climate_BU']").groupby(['domain','method','year']).crps.mean().reset_index()
cv['method']=cv.method.replace({'H0_7_NN':'H0','H1_7_NN':'H1'})
fw=pd.read_csv(V3/'forward_annual.csv').query("lead=='D28'").rename(columns={'crps':'forward_crps'})
joined=cv.rename(columns={'crps':'loyo_crps'}).merge(fw,on=['domain','method','year'],validate='one_to_one')
joined['forward_minus_loyo']=joined.forward_crps-joined.loyo_crps
assert np.allclose(joined.query("method=='Raw'").forward_minus_loyo,0)
joined.to_csv(R/'matched_validation_annual.csv',index=False)
joined.groupby(['domain','method'])[['loyo_crps','forward_crps','forward_minus_loyo']].mean().to_csv(R/'matched_validation_summary.csv')
print(pd.DataFrame(rows).to_string(index=False))
print(joined.query("domain=='N'").groupby('method')[['loyo_crps','forward_crps','forward_minus_loyo']].mean().to_string())
