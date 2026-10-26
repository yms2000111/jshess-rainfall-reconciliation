"""Score every added review control with paired annual-block comparisons."""
from review_controls import *
from revision_statistics import ci

def main():
 cases=[];summaries=[];forwardrows=[]
 for key in REGIONS:
  fs=[np.load(RFOLDS/f'{key}_{year}.npz') for year in range(2000,2020)]
  y=np.concatenate([f['y'] for f in fs]);dates=pd.DatetimeIndex(np.concatenate([f['dates'] for f in fs]));q90=np.concatenate([f['threshold90'] for f in fs])
  methods=[m for m in fs[0].files if m not in ['y','dates','threshold90','reference']]
  for method in methods:
   a=np.concatenate([f[method] for f in fs]);cc=crps(a,y);tc=crps(np.maximum(a,q90[:,None,:]),np.maximum(y,q90));bs=((a>q90[:,None,:]).mean(1)-(y>q90))**2;lo,hi=np.quantile(a,[.1,.9],axis=1)
   for j in [0,1,2,3,6]:
    lead=NODES[j];summaries.append(dict(domain=key,method=method,lead=lead,crps=cc[:,j].mean(),twcrps=tc[:,j].mean(),brier90=bs[:,j].mean(),coverage80=np.mean((y[:,j]>=lo[:,j])&(y[:,j]<=hi[:,j])),width80=(hi[:,j]-lo[:,j]).mean()))
    cases.append(pd.DataFrame(dict(domain=key,method=method,lead=lead,year=dates.year,date=dates,crps=cc[:,j],twcrps=tc[:,j],brier90=bs[:,j])))
  ff=np.load(RFOLDS/f'forward_{key}.npz');fd=pd.DatetimeIndex(ff['dates'])
  for method in ['Raw','H0','H1','Weekly_climate_BU','Bottom_up']:
   c=crps(ff[method],ff['y'])
   for year in range(2015,2020):
    mask=fd.year==year
    for j in [0,1,2,3,6]:forwardrows.append(dict(domain=key,method=method,year=year,lead=NODES[j],crps=c[mask,j].mean()))
 C=pd.concat(cases);C.to_csv(REVIEW/'control_case_scores.csv.gz',index=False,compression='gzip');pd.DataFrame(summaries).to_csv(REVIEW/'control_scores.csv',index=False);pd.DataFrame(forwardrows).to_csv(REVIEW/'forward_annual.csv',index=False)
 old=pd.read_csv(EXT/'case_scores.csv.gz',usecols=['domain','method','lead','year','crps','twcrps','brier90'])
 annual=pd.concat([C,old]).groupby(['domain','method','lead','year'])[['crps','twcrps','brier90']].mean();draw=np.random.default_rng(SEED+17).integers(0,20,(10000,20));rows=[]
 for key in REGIONS:
  methods=[s['method'] for s in summaries if s['domain']==key and s['lead']=='D28']
  for method in methods:
   baselines=['H1_7_NN','Bottom_up']
   if method.startswith('H0_') or method.startswith('H1_'):
    if 'ECC' in method:baselines+=['ECC_BU','H0_ECC_NN']
    if 'Schaake' in method:baselines+=['Schaake_BU','H0_Schaake_NN']
    if 'positive' in method:baselines+=['positive_BU','H0_positive']
    if 'signed' in method:baselines+=['signed_BU','H0_signed']
   if method=='Weekly_climate_BU':baselines+=['H0_7_NN']
   for baseline in set(baselines):
    if baseline==method:continue
    for lead in ['W1','W2','W3','W4','D28']:
     for metric in ['crps','twcrps','brier90']:
      a=annual.loc[(key,method,lead)][metric].reindex(range(2000,2020)).values;b=annual.loc[(key,baseline,lead)][metric].reindex(range(2000,2020)).values;ds=a-b;lo,hi=ci(ds,draw)
      rows.append(dict(domain=key,method=method,baseline=baseline,lead=lead,score=metric,delta=ds.mean(),lower=lo,upper=hi,better_years=int((ds<0).sum())))
 pd.DataFrame(rows).to_csv(REVIEW/'control_comparisons.csv',index=False)
 print(pd.DataFrame(summaries).query("lead=='D28'")[['domain','method','crps','coverage80']].to_string(index=False),flush=True)
 print('Forward:',pd.DataFrame(forwardrows).query("lead=='D28'").groupby(['domain','method']).crps.mean().to_string(),flush=True)
if __name__=='__main__':main()
