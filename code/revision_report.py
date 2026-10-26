from common import ROOT,REGIONS
import pandas as pd,numpy as np,json
p=ROOT/'revision/primary';S=pd.read_csv(p/'scores.csv');C=pd.read_csv(p/'case_scores.csv.gz');B=pd.read_csv(p/'comparisons.csv')
print(S[S.lead.eq('D28')][['domain','method','crps','crpss','rmse','coverage80','width80','bss']].to_string(index=False))
print(B[B.lead.eq('D28')].to_string(index=False))
rows=[]
for key in REGIONS:
 for period in ['all','2000-2014','2015-2019']:
  for season in ['all','wet','dry']:
   df=C[(C.domain==key)&(C.lead=='D28')].copy();month=pd.to_datetime(df.date).dt.month
   if period=='2000-2014':df=df[df.year<=2014]
   if period=='2015-2019':df=df[df.year>=2015]
   if season!='all':
    wet=month.isin([11,12,1,2,3,4]);df=df[wet.loc[df.index] if season=='wet' else ~wet.loc[df.index]]
   for method in ['Raw','Seasonal_EMOS','Direct_EMOS','Bottom_up','MinT_NN']:
    sub=df[df.method==method];rows.append(dict(domain=key,period=period,season=season,method=method,n=len(sub),crps=sub.crps.mean(),reference=sub.reference.mean(),width=(sub.upper80-sub.lower80).mean(),coverage=((sub.observed>=sub.lower80)&(sub.observed<=sub.upper80)).mean()))
R=pd.DataFrame(rows);R.to_csv(p/'seasonal_diagnostics.csv',index=False);print(R[R.domain.eq('N')].to_string(index=False))
print('Weekly MinT vs BU',B[(B.method=='MinT_NN')&(B.baseline=='Bottom_up')&(B.lead!='D28')].to_string(index=False))
print('Fit',pd.read_csv(p/'fit_diagnostics.csv').groupby(['domain','lead'])[['in_sample_exact','outer_exact','legacy_exact']].mean().to_string())
meta=[]
for path in (ROOT/'revision/cache').glob('*.json'):
 rec=json.loads(path.read_text());meta.extend(rec)
print('FITS',len(meta),'FAILED',sum(not r['success'] for r in meta),'BOUNDARY',sum(r['boundary'] for r in meta))
print('Authors of new references')
for name in ['10.1071_ES22026.json','10.5194_hess-22-1615-2018.json','10.1175_MWR-D-13-00248.1.json','10.25914_hjqj-0x55.json']:
 m=json.loads((ROOT/'revision/reference_metadata'/name).read_text(encoding='utf-8'));print(name,m['author'],m['published'])
