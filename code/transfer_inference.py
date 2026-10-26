"""System-specific and spatially paired year-block transfer inference."""
from adaptive_coherent import *

def main():
 a=pd.read_csv(V4/'access_s2/case_scores.csv').query('lead=="D28"');rows=[]
 for season,months in [('Annual',range(1,13)),('DJF',[12,1,2]),('MAM',[3,4,5]),('JJA',[6,7,8]),('SON',[9,10,11])]:
  t=a[a.month.isin(months)].groupby(['year','method']).crps.mean().unstack();idx=np.random.default_rng(SEED+81).integers(0,len(t),(20000,len(t)))
  for b in ['Raw','Bottom_up','H0','Weekly_climate_BU']:
   d=(t.H1-t[b]).values;lo,hi=np.quantile(d[idx].mean(1),[.025,.975]);rows.append(dict(season=season,baseline=b,delta=d.mean(),lower=lo,upper=hi,h1=t.H1.mean(),baseline_score=t[b].mean(),n_years=len(t)))
 pd.DataFrame(rows).to_csv(V4/'access_s2/season_comparisons.csv',index=False)
 a=pd.read_csv(V4/'coverage/annual_scores.csv').query('lead=="D28"');idx=np.random.default_rng(SEED+82).integers(0,20,(20000,20));sign=np.random.default_rng(SEED+83).choice([-1,1],(100000,20));rows=[]
 for b in ['Raw','H0','Bottom_up','Weekly_climate_BU']:
  seq=[]
  for k in ['NW','CA','EC','TAS']:
   t=a.query('domain==@k').pivot(index='year',columns='method',values='crps');seq.append((t.H1-t[b]).values/t.Raw.mean()*100)
  seq=np.array(seq);d=seq.mean(0);lo,hi=np.quantile(d[idx].mean(1),[.025,.975]);fraction=(seq[:,idx].mean(2)<0).mean(0);p=(1+(abs((sign*d).mean(1))>=abs(d.mean())).sum())/(len(sign)+1)
  rows.append(dict(baseline=b,delta=d.mean(),lower=lo,upper=hi,p=p,fraction=(seq.mean(1)<0).mean(),fraction_lower=np.quantile(fraction,.025),fraction_upper=np.quantile(fraction,.975)))
 order=np.argsort([r['p'] for r in rows]);adj=0
 for rank,i in enumerate(order):adj=max(adj,min(1,rows[i]['p']*(len(rows)-rank)));rows[i]['holm_p']=adj
 pd.DataFrame(rows).to_csv(V4/'coverage/pooled_comparisons.csv',index=False)
 print(pd.read_csv(V4/'access_s2/season_comparisons.csv').query('season=="DJF"').to_string(index=False))
 print(pd.DataFrame(rows).to_string(index=False))

if __name__=='__main__':main()
