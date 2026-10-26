"""Numerical and small-sample audits of the existing factorial experiment."""
from review_controls import *
from scipy.stats import bootstrap,linregress
from recalibration import apply_map,joint_prediction

def numeric_audit():
 C=pd.read_csv(EXT/'case_scores.csv.gz');rows=[]
 for k in REGIONS:
  d=C.query("domain==@k and lead=='D28' and method=='H0_Direct'")
  event=d.event90.astype(bool)
  rows.append(dict(domain=k,n=len(d),events=int(event.sum()),event_percent=event.mean()*100,crps_share_above_q90=d.loc[event,'crps'].sum()/d.crps.sum()*100,threshold='origin calendar date plus/minus 45 days in permitted training data'))
 pd.DataFrame(rows).to_csv(REVIEW/'threshold_audit.csv',index=False)
 annual=C.query("lead=='D28'").groupby(['domain','method','year'])[['crps','reference']].mean();years=np.arange(2000,2020);rows=[];influence=[]
 for k in REGIONS:
  for a,b in [('H1_7_NN','H0_7_NN'),('H1_7_NN','Bottom_up')]:
   ds=(annual.loc[(k,a)].reindex(years).crps-annual.loc[(k,b)].reindex(years).crps).values
   result=bootstrap((ds,),np.mean,method='BCa',n_resamples=20000,random_state=20261024)
   row=dict(domain=k,method=a,baseline=b,delta=ds.mean(),bca_lower=result.confidence_interval.low,bca_upper=result.confidence_interval.high,better_years=int((ds<0).sum()),leave_one_out_min=min((ds.sum()-ds)/19),leave_one_out_max=max((ds.sum()-ds)/19))
   for size in [2,3]:
    rng=np.random.default_rng(SEED+size);start=rng.integers(0,20,(20000,int(np.ceil(20/size))));ix=((start[:,:,None]+np.arange(size))%20).reshape(20000,-1)[:,:20];lo,hi=np.quantile(ds[ix].mean(1),[.025,.975]);row[f'block{size}_lower']=lo;row[f'block{size}_upper']=hi
   rows.append(row)
   influence.extend([dict(domain=k,method=a,baseline=b,year=int(yr),annual_delta=di,mean_without_year=(ds.sum()-di)/19) for yr,di in zip(years,ds)])
 pd.DataFrame(rows).to_csv(REVIEW/'small_sample_intervals.csv',index=False);pd.DataFrame(influence).to_csv(REVIEW/'annual_influence.csv',index=False)
 g=pd.read_csv(EXT/'mechanism_summary.csv');rows=[]
 for col in ['real_linear','real_nn']:
  bias=(g[col]-g.predicted).mean()*100;reg=linregress(g.predicted,g[col]);rows.append(dict(mapping=col,mean_observed_minus_predicted_pp=bias,slope=reg.slope,intercept_pp=100*reg.intercept,r_squared=reg.rvalue**2,below_diagonal=int((g[col]<g.predicted).sum()),n=len(g)))
 pd.DataFrame(rows).to_csv(REVIEW/'mechanism_bias.csv',index=False)
 print('Thresholds:',pd.read_csv(REVIEW/'threshold_audit.csv').to_string(index=False),flush=True)

def inner_audit(key):
 rows=[];wrows=[];windowrows=[];d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z=climate(dates,d)[0]
 for year in range(2000,2020):
  f=np.load(EXT/f'recalibration/{key}_{year}.npz');meta=json.loads((EXT/f'recalibration/{key}_{year}.json').read_text());q=f['inner_samples'];ix=f['inner_index'];mapped=np.empty_like(q)
  for r in meta['records']:
   loc=dates[ix].month==r['month'];mapped[loc]=apply_map(q[loc],r['log_scale'],r['log_power'],r['reference_scale'])
   window=near_day(calendar_day(dates)[ix],pd.Timestamp(2000,r['month'],15).dayofyear)<=45
   altered=apply_map(q[window],r['log_scale'],r['log_power'],r['reference_scale'])
   base_score=crps(q[window,:,6:7],y[ix[window],6:7])[:,0].mean();altered_score=crps(altered[:,:,6:7],y[ix[window],6:7])[:,0].mean()
   penalised_delta=(altered_score-base_score)/r['reference_scale']+.01*(r['log_scale']**2+r['log_power']**2)
   assert penalised_delta<1e-6,(key,year,r['month'],penalised_delta)
   windowrows.append(dict(domain=key,year=year,month=r['month'],before=base_score,after=altered_score,delta=altered_score-base_score,penalised_delta=penalised_delta))
  before=crps(q[:,:,6:7],y[ix,6:7])[:,0];after=crps(mapped[:,:,6:7],y[ix,6:7])[:,0]
  old=np.load(EFOLDS/f'{key}_{year}.npz');outer=crps(old['H1_7_NN'][:,:,6:7],old['y'][:,6:7])[:,0];new=crps(f['coherent'][:,:,6:7],old['y'][:,6:7])[:,0]
  rows.append(dict(domain=key,year=year,inner_before=before.mean(),inner_after=after.mean(),inner_delta=(after-before).mean(),outer_before=outer.mean(),outer_after=new.mean(),outer_delta=(new-outer).mean()))
  outerW=old['H1_7_W'];train=old['train_index']
  for j,(fit,val,_) in enumerate(inner_splits(dates,train)):
   errors=[]
   for fit2,val2,_ in inner_splits(dates,fit):
    mm,_=joint_prediction(raw,y,dates,z,fit2,val2,key,0,None);errors.append(y[val2]-mm)
   W,_=shrink(np.concatenate(errors))
   wrows.append(dict(domain=key,year=year,inner_block=j,relative_frobenius=np.linalg.norm(W-outerW)/np.linalg.norm(outerW),total_variance_ratio=W[6,6]/outerW[6,6],inner_fit_n=len(fit),outer_fit_n=len(train)))
  print('Inner audit',key,year,flush=True)
 pd.DataFrame(rows).to_csv(REVIEW/f'recalibration_inner_{key}.csv',index=False);pd.DataFrame(wrows).to_csv(REVIEW/f'covariance_shift_{key}.csv',index=False);pd.DataFrame(windowrows).to_csv(REVIEW/f'recalibration_windows_{key}.csv',index=False)
 return key+' recalibration audited'

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--inner',action='store_true');p.add_argument('--workers',type=int,default=3);a=p.parse_args()
 if a.inner:
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(inner_audit,k) for k in REGIONS]):print(f.result(),flush=True)
 else:numeric_audit()
