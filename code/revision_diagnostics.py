from common import ROOT,REGIONS
import numpy as np,pandas as pd,json
from revision_cv import FOLDS,LEADS
p=ROOT/'revision/primary';C=pd.read_csv(p/'case_scores.csv.gz');rows=[];solver=[]
for key in REGIONS:
 for year in range(2000,2020):
  data=np.load(ROOT/f'data/processed/{key}.npz');d= np.load(FOLDS/f'primary_{key}_{year}.npz');tr=d['train_index'];dates=pd.DatetimeIndex(data['dates']);threshold=np.quantile(data['y'][tr,4],.9)
  for method in ['Raw','Seasonal_EMOS','Direct_EMOS','Bottom_up','MinT_NN']:
   sub=C[(C.domain==key)&(C.year==year)&(C.method==method)&(C.lead=='D28')];event=sub.observed>threshold
   rows.append(dict(domain=key,year=year,method=method,n=len(sub),extreme_n=int(event.sum()),crps_total=sub.crps.sum(),extreme_crps=sub.loc[event,'crps'].sum(),other_crps=sub.loc[~event,'crps'].sum()))
  meta=json.loads((FOLDS/f'primary_{key}_{year}.json').read_text());solver.extend([dict(domain=key,year=year,**r) for r in meta['records']])
pd.DataFrame(rows).to_csv(p/'extreme_contribution.csv',index=False)
sd=pd.DataFrame(solver);sd.to_csv(p/'outer_fit_parameters.csv',index=False)
summary=dict(outer_fits=len(sd),successful=int(sd.success.sum()),boundary_fits=int(sd.boundary.sum()),monthly_training_n_min=int(sd.n.min()),monthly_training_n_max=int(sd.n.max()))
(p/'solver_summary.json').write_text(json.dumps(summary,indent=2));print(summary)
e=pd.DataFrame(rows).groupby(['domain','method'])[['crps_total','extreme_crps','extreme_n','n']].sum();e['score_fraction']=e.extreme_crps/e.crps_total;e['case_fraction']=e.extreme_n/e.n;print(e.to_string())
S=pd.read_csv(p/'scores.csv');print(S[(S.lead=='D28')&S.method.isin(['Direct_EMOS','Bottom_up','MinT_NN'])][['domain','method','accuracy','dispersal','coherence']].to_string(index=False))
comparison=[]
for qc in ['primary','positive','signed']:
 s=pd.read_csv(ROOT/f'revision/{qc}/scores.csv');b=pd.read_csv(ROOT/f'revision/{qc}/comparisons.csv')
 for key in REGIONS:
  for lead in LEADS:
   for base in ['Direct_EMOS','Bottom_up']:
    r=b[(b.domain==key)&(b.lead==lead)&(b.method=='MinT_NN')&(b.baseline==base)].iloc[0].to_dict();comparison.append(dict(qc=qc,**r))
pd.DataFrame(comparison).to_csv(ROOT/'revision/qc_comparisons.csv',index=False)
