from recalibration import *
from revision_statistics import ci,hersbach
from scipy.stats import skew
rows=[];cases=[];coverage=[];comparisons=[];params=[]
draw=np.random.default_rng(SEED+17).integers(0,20,(10000,20))
for key in REGIONS:
 fs=[np.load(EFOLDS/f'{key}_{yr}.npz') for yr in range(2000,2020)];rs=[np.load(RDIR/f'{key}_{yr}.npz') for yr in range(2000,2020)]
 y=np.concatenate([f['y'] for f in fs]);dates=pd.DatetimeIndex(np.concatenate([f['dates'] for f in fs]));q90=np.concatenate([f['threshold90'] for f in fs]);ref=np.concatenate([f['reference'] for f in fs])
 pred={'Original':np.concatenate([f['H1_7_NN'] for f in fs]),'Coherent_recalibration':np.concatenate([r['coherent'] for r in rs]),'Total_only':np.concatenate([r['total_only'] for r in rs])}
 assert np.allclose(pred['Coherent_recalibration'][:,:,:4]@S7.T,pred['Coherent_recalibration']);assert pred['Coherent_recalibration'].min()>=0
 assert np.array_equal(pred['Coherent_recalibration'][:,:,6],pred['Total_only'][:,:,6])
 allc={}
 for method,a in pred.items():
  c=crps(a,y);allc[method]=c;tc=crps(np.maximum(a,q90[:,None,:]),np.maximum(y,q90));avg=a.mean(1);q=np.quantile(a,[.1,.5,.9],axis=1)
  for k,lead in enumerate(NODES):
   cover=(y[:,k]>=q[0,:,k])&(y[:,k]<=q[2,:,k]);h=hersbach(a[:,:,k],y[:,k]);discrepancy=np.abs(a[:,:,6]-a[:,:,:4].sum(2)).mean()
   rows.append(dict(domain=key,method=method,lead=lead,crps=c[:,k].mean(),twcrps=tc[:,k].mean(),coverage80=cover.mean(),width80=(q[2,:,k]-q[0,:,k]).mean(),bias=(avg[:,k]-y[:,k]).mean(),mean_q10=q[0,:,k].mean(),mean_q50=q[1,:,k].mean(),mean_q90=q[2,:,k].mean(),coherence_error=discrepancy,**h))
   cases.append(pd.DataFrame(dict(domain=key,method=method,lead=lead,year=dates.year,crps=c[:,k],twcrps=tc[:,k],covered80=cover.astype(int),width80=q[2,:,k]-q[0,:,k],reference=ref[:,k])))
   for nominal in [.2,.4,.6,.8,.9,.95]:
    lo,hi=np.quantile(a[:,:,k],[(1-nominal)/2,(1+nominal)/2],axis=1);cv=(y[:,k]>=lo)&(y[:,k]<=hi);annual=np.array([cv[dates.year==yr].mean() for yr in range(2000,2020)]);lower,upper=ci(annual,draw)
    coverage.append(dict(domain=key,method=method,lead=lead,nominal=nominal,coverage=cv.mean(),lower=lower,upper=upper))
 for yr in range(2000,2020):
  meta=json.loads((RDIR/f'{key}_{yr}.json').read_text());params.extend([dict(domain=key,year=yr,**r) for r in meta['records']])
 print('Recalibration scored',key,flush=True)
C=pd.concat(cases);C.to_csv(RDIR/'case_scores.csv.gz',index=False,compression='gzip');A=C.groupby(['domain','method','lead','year'])[['crps','twcrps','covered80','width80']].mean()
for key in REGIONS:
 for lead in NODES:
  for measure in ['crps','twcrps','covered80','width80']:
   a=A.loc[(key,'Coherent_recalibration',lead)][measure].values;b=A.loc[(key,'Original',lead)][measure].values;lo,hi=ci(a-b,draw);comparisons.append(dict(domain=key,lead=lead,measure=measure,delta=(a-b).mean(),lower=lo,upper=hi))
pd.DataFrame(rows).to_csv(RDIR/'scores.csv',index=False);pd.DataFrame(coverage).to_csv(RDIR/'coverage.csv',index=False);pd.DataFrame(comparisons).to_csv(RDIR/'comparisons.csv',index=False);pd.DataFrame(params).to_csv(RDIR/'parameters.csv',index=False)
print(pd.DataFrame(rows).query("lead=='D28'")[['domain','method','crps','coverage80','width80','coherence_error']].to_string(index=False))
print(pd.DataFrame(comparisons).query("lead=='D28'").to_string(index=False))
st=pd.read_csv(EXT/'sample_stability.csv');print('STABILITY',st.query("lead=='D28'").groupby(['domain','size'])[['crps','delta_bu']].agg(['mean','min','max']).to_string())
