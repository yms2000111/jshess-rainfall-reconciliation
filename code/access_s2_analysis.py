"""Second-system northern check using unchanged fitting methods."""
import coverage_extension as c
from coverage_extension import *
ADIR=V4/'access_s2';AF=ADIR/'folds';AF.mkdir(exist_ok=True)
REGIONS['ACCESS_N']=REGIONS['N'].copy()
c.CDIR=AF

def build_access():
 dates=pd.date_range('2000-01-01','2018-12-01',freq='MS');raw=[]
 for d in dates:
  members=[]
  for m in range(1,10):
   f=np.load(ADIR/f'{d:%Y%m%d}_e{m:02d}.npz');w=f['daily_mm'].reshape(4,7).sum(1);members.append(np.r_[w,w.sum()])
  raw.append(members)
 daily=pd.read_csv(ROOT/'data/processed/agcd_daily_regional_mm.csv',index_col=0,parse_dates=True).N
 y=[]
 for d in dates:
  w=daily.reindex(pd.date_range(d+pd.Timedelta(days=1),periods=28)).values.reshape(4,7).sum(1);y.append(np.r_[w,w.sum()])
 rmm=pd.read_csv(ROOT/'data/support/rmm_full.txt',sep=r'\s+',skiprows=2,header=None,usecols=range(7),names=['year','month','day','rmm1','rmm2','phase','amp'])
 rmm.index=pd.to_datetime(rmm[['year','month','day']])
 enso=pd.read_csv(ROOT/'data/support/nino34.txt',sep=r'\s+');enso.index=pd.to_datetime(dict(year=enso.YR,month=enso.MON,day=1))
 z=np.column_stack([rmm.reindex(dates-pd.Timedelta(days=2))[['rmm1','rmm2']],enso.reindex(dates.to_period('M').to_timestamp()-pd.DateOffset(months=2))['NINO3.4']])
 assert np.isfinite(raw).all() and np.isfinite(y).all() and np.isfinite(z).all()
 np.savez_compressed(ROOT/'data/processed/ACCESS_N.npz',dates=dates.values,raw=raw,y=y,climate=z)
 print('ACCESS-S2: 228 monthly origins, nine members, 19 years.',flush=True)

def score_access():
 rows=[];cases=[]
 for year in range(2000,2019):
  f=np.load(AF/f'ACCESS_N_{year}.npz');ds=pd.DatetimeIndex(f['dates'])
  for m in ['Raw','Bottom_up','H0','H1','Weekly_climate_BU']:
   score=crps(f[m],f['y'])
   for j in [0,1,2,3,6]:
    rows.append(dict(domain='ACCESS_N',method=m,year=year,lead=NODES[j],crps=float(score[:,j].mean())))
    cases.extend(dict(method=m,year=year,month=d.month,date=str(d.date()),lead=NODES[j],crps=float(score[i,j])) for i,d in enumerate(ds))
 a=pd.DataFrame(rows);a.to_csv(ADIR/'annual_scores.csv',index=False);pd.DataFrame(cases).to_csv(ADIR/'case_scores.csv',index=False)
 draw=np.random.default_rng(SEED+32).integers(0,19,(20000,19));rows=[]
 for lead in ['W1','W2','W3','W4','D28']:
  t=a.query('lead==@lead').pivot(index='year',columns='method',values='crps')
  for b in ['Raw','Bottom_up','H0','Weekly_climate_BU']:
   d=(t.H1-t[b]).values;lo,hi=np.quantile(d[draw].mean(1),[.025,.975]);rows.append(dict(lead=lead,baseline=b,delta=float(d.mean()),lower=lo,upper=hi,better_years=int((d<0).sum())))
 pd.DataFrame(rows).to_csv(ADIR/'comparisons.csv',index=False)
 print(a.query("lead=='D28'").groupby('method').crps.mean().to_string(),flush=True)
 print(pd.DataFrame(rows).query("lead=='D28'").to_string(index=False),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['build','fit','score']);p.add_argument('--workers',type=int,default=6);a=p.parse_args()
 if a.action=='build':build_access()
 elif a.action=='score':score_access()
 else:
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(c.fit,('ACCESS_N',year)) for year in range(2000,2019)]):print(f.result(),flush=True)
