"""Common-year inference and decision scores for the frozen adaptive extension."""
from adaptive_coherent import *

def summarise():
 rows=[];dec=[];weights_rows=[]
 for path in sorted(AD.glob('*.npz')):
  if path.name.startswith('inner_'):continue
  f=np.load(path);key,year=path.stem.rsplit('_',1);mode='Forward' if year=='forward' else ('Rolling'+year[4:] if year.startswith('roll') else 'LOYO');dates=pd.DatetimeIndex(f['dates'])
  for yy in np.unique(dates.year):
   use=dates.year==yy
   for j,m in enumerate(f['methods']):
    for k in [0,1,2,3,6]:rows.append(dict(domain=key,validation=mode,year=int(yy),method=str(m),lead=NODES[k],crps=float(f['scores'][use,j,k].mean())))
    obs=f['y'][use,6];pp=f['probs'][use,j];cp=f['climp'][use]
    for t,threshold in enumerate([50,100]):
     event=obs>threshold
     dec.append(dict(domain=key,validation=mode,year=int(yy),method=str(m),metric='Brier',threshold=threshold,ratio=0,forecast=float(np.mean((pp[:,t]-event)**2)),reference=float(np.mean((cp[:,t]-event)**2)),perfect=0))
     for ratio in np.arange(.05,1,.05):
      act=pp[:,t]>ratio;ca=cp[:,t]>ratio
      dec.append(dict(domain=key,validation=mode,year=int(yy),method=str(m),metric='Expense',threshold=threshold,ratio=float(ratio),forecast=float(np.mean(ratio*act+event*(~act))),reference=float(np.mean(ratio*ca+event*(~ca))),perfect=float(ratio*event.mean())))
    dec.append(dict(domain=key,validation=mode,year=int(yy),method=str(m),metric='RPS',threshold=0,ratio=0,forecast=float(f['rps'][use,j].mean()),reference=float(f['climrps'][use].mean()),perfect=0))
   for model in ['Constant','Seasonal','State']:
    for season in range(4):
     s=use&(((dates.month%12)//3)==season)
     for j,c in enumerate(COMP):weights_rows.append(dict(domain=key,validation=mode,year=int(yy),model=model,season=['DJF','MAM','JJA','SON'][season],component=c,weight=float(f['weight_'+model][s,j].mean())))
 annual=pd.DataFrame(rows);annual.to_csv(AD/'annual_scores.csv',index=False);decision=pd.DataFrame(dec);decision.to_csv(AD/'annual_decision.csv',index=False);pd.DataFrame(weights_rows).to_csv(AD/'annual_weights.csv',index=False)
 draw=np.random.default_rng(SEED+77).integers(0,20,(20000,20));comparisons=[]
 for (k,mode,lead),a in annual.groupby(['domain','validation','lead']):
  t=a.pivot(index='year',columns='method',values='crps');local=np.random.default_rng(SEED+78).integers(0,len(t),(20000,len(t)))
  for m in ['Constant','Seasonal','State','Select_global','Select_season']:
   for b in ['Raw','Weekly_climate_BU','H1','Constant']:
    if m==b:continue
    d=(t[m]-t[b]).values;lo,hi=np.quantile(d[local].mean(1),[.025,.975]);comparisons.append(dict(domain=k,validation=mode,lead=lead,method=m,baseline=b,delta=d.mean(),lower=lo,upper=hi,better_years=int((d<0).sum())))
 pd.DataFrame(comparisons).to_csv(AD/'comparisons.csv',index=False)
 primary=[];rng=np.random.default_rng(SEED+79);signs=rng.choice([-1,1],size=(100000,20))
 for b in ['Constant','Weekly_climate_BU']:
  series=[]
  for k in ['N','NE','SE','SW']:
   t=annual.query('domain==@k and validation=="LOYO" and lead=="D28"').pivot(index='year',columns='method',values='crps');series.append((t.State-t[b])/t.Raw.mean()*100)
  d=np.array(series).mean(0);lo,hi=np.quantile(d[draw].mean(1),[.025,.975]);p=(1+(abs((signs*d).mean(1))>=abs(d.mean())).sum())/(len(signs)+1)
  primary.append(dict(baseline=b,delta=d.mean(),lower=lo,upper=hi,p=p,improved_domains=int((np.array(series).mean(1)<0).sum())))
 order=np.argsort([r['p'] for r in primary]);adj=0
 for rank,i in enumerate(order):adj=max(adj,min(1,primary[i]['p']*(len(order)-rank)));primary[i]['holm_p']=adj
 pd.DataFrame(primary).to_csv(AD/'primary_comparisons.csv',index=False)
 # Skill is a ratio of pooled expenses, not a mean of year-specific ratios.
 dr=[]
 for keys,a in decision.groupby(['domain','validation','method','metric','threshold','ratio']):
  t=a.sort_values('year');f=t.forecast.values;r=t.reference.values;perf=t.perfect.values;idx=np.random.default_rng(SEED+80).integers(0,len(t),(10000,len(t)));den=r.mean()-perf.mean()
  if den<=1e-12:skill=np.nan;lo=hi=np.nan
  else:
   skill=(r.mean()-f.mean())/den;bd=(r[idx]-perf[idx]).mean(1);bs=np.divide((r[idx]-f[idx]).mean(1),bd,out=np.full(len(idx),np.nan),where=bd>1e-12);lo,hi=np.nanquantile(bs,[.025,.975])
  dr.append(dict(zip(['domain','validation','method','metric','threshold','ratio'],keys),forecast=f.mean(),reference=r.mean(),skill=skill,lower=lo,upper=hi))
 pd.DataFrame(dr).to_csv(AD/'decision_summary.csv',index=False)
 print(annual.query('lead=="D28"').groupby(['validation','domain','method']).crps.mean().unstack().round(3).to_string())
 print(pd.DataFrame(primary).to_string(index=False))

if __name__=='__main__':summarise()
