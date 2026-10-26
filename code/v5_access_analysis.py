"""Eight-domain ACCESS-S2 validation, unchanged calibration and exclusions."""
import coverage_extension as c
from coverage_extension import *
import shutil
R=ROOT/'revision/review_v5/access_s2';F=R/'folds';F.mkdir(exist_ok=True)
keys=['N','NE','SE','SW','NW','CA','EC','TAS']
for k in keys:REGIONS['ACCESS_'+k]=REGIONS[k].copy()
c.CDIR=F

def build():
 dates=pd.date_range('2000-01-01','2018-12-01',freq='MS')
 daily=pd.read_csv(ROOT/'data/processed/agcd_daily_regional_mm.csv',index_col=0,parse_dates=True).join(pd.read_csv(ROOT/'revision/review_v4/coverage/daily_observations.csv',index_col=0,parse_dates=True))
 clim=np.load(ROOT/'data/processed/ACCESS_N.npz')['climate']
 for k in keys:
  if k=='N':continue
  raw=[];obs=[]
  for d in dates:
   members=[]
   for m in range(1,10):
    f=np.load(R/f'{d:%Y%m%d}_e{m:02d}.npz');w=f[k].reshape(4,7).sum(1);members.append(np.r_[w,w.sum()])
   raw.append(members);w=daily[k].reindex(pd.date_range(d+pd.Timedelta(days=1),periods=28)).values.reshape(4,7).sum(1);obs.append(np.r_[w,w.sum()])
  assert np.isfinite(raw).all() and np.isfinite(obs).all()
  np.savez_compressed(ROOT/f'data/processed/ACCESS_{k}.npz',dates=dates.values,raw=raw,y=obs,climate=clim)
 for f in (ROOT/'revision/review_v4/access_s2/folds').glob('ACCESS_N_*'):
  if not (F/f.name).exists():shutil.copy2(f,F/f.name)
 print('Built eight ACCESS domains.',flush=True)

def score():
 rows=[];cases=[]
 for k in keys:
  for year in range(2000,2019):
   f=np.load(F/f'ACCESS_{k}_{year}.npz');dates=pd.DatetimeIndex(f['dates'])
   for m in ['Raw','Bottom_up','Weekly_climate_BU','H0','H1']:
    scores=crps(f[m],f['y'])
    for j in [0,1,2,3,6]:
     rows.append(dict(domain=k,year=year,method=m,lead=NODES[j],crps=scores[:,j].mean()))
     cases.extend(dict(domain=k,year=year,date=str(d.date()),month=d.month,method=m,lead=NODES[j],crps=scores[i,j]) for i,d in enumerate(dates))
 a=pd.DataFrame(rows);a.to_csv(R/'annual_scores.csv',index=False);pd.DataFrame(cases).to_csv(R/'case_scores.csv',index=False)
 idx=np.random.default_rng(2026102511).integers(0,19,(50000,19));sign=np.random.default_rng(2026102512).choice([-1,1],(100000,19));pooled=[];local=[]
 for m,b in [('H1','H0'),('H1','Weekly_climate_BU'),('H0','Bottom_up')]:
  seq=[]
  for k in keys:
   t=a.query('domain==@k and lead=="D28"').pivot(index='year',columns='method',values='crps');d=(t[m]-t[b]).values;lo,hi=np.quantile(d[idx].mean(1),[.025,.975]);seq.append(100*d/t.Raw.mean())
   local.append(dict(domain=k,method=m,baseline=b,delta=d.mean(),lower=lo,upper=hi))
  seq=np.array(seq);d=seq.mean(0);lo,hi=np.quantile(d[idx].mean(1),[.025,.975]);p=(1+(abs((sign*d).mean(1))>=abs(d.mean())).sum())/(len(sign)+1)
  pooled.append(dict(method=m,baseline=b,delta=d.mean(),lower=lo,upper=hi,p=p,favourable_domains=int((seq.mean(1)<0).sum())))
 order=np.argsort([r['p'] for r in pooled]);adj=0
 for rank,i in enumerate(order):adj=max(adj,min(1,pooled[i]['p']*(3-rank)));pooled[i]['holm_p']=adj
 pd.DataFrame(pooled).to_csv(R/'pooled_comparisons.csv',index=False);pd.DataFrame(local).to_csv(R/'domain_comparisons.csv',index=False)
 print(pd.DataFrame(pooled).to_string(index=False));print(pd.DataFrame(local).query('domain=="N"').to_string(index=False))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['build','fit','score']);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
 if a.action=='build':build()
 elif a.action=='score':score()
 else:
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(c.fit,('ACCESS_'+k,y)) for y in range(2000,2019) for k in keys]):print(f.result(),flush=True)
  score()
