from review_controls import *
from scipy.stats import bootstrap

old=pd.read_csv(EXT/'case_scores.csv.gz');control=pd.read_csv(REVIEW/'control_case_scores.csv.gz')
A=pd.concat([old,control]).query("lead=='D28'").groupby(['domain','method','year']).crps.mean()
draw=np.random.default_rng(SEED+17).integers(0,20,(10000,20));rows=[]
for key in ['N','NE','SE','SW']:
 for method in control.query('domain==@key').method.unique():
  ds=(A.loc[(key,method)]-A.loc[(key,'H0_7_NN')]).reindex(range(2000,2020)).values;lo,hi=np.quantile(ds[draw].mean(1),[.025,.975]);rows.append(dict(domain=key,method=method,baseline='H0_7_NN',delta=ds.mean(),lower=lo,upper=hi))
pd.DataFrame(rows).to_csv(REVIEW/'controls_vs_H0.csv',index=False)
rows=[]
for base in ['H0_7_NN','H1_5_NN','Bottom_up']:
 ds=[]
 for key in ['N','NE','SE','SW']:
  ref=old.query("domain==@key and method=='H1_7_NN' and lead=='D28'").reference.mean();ds.append((A.loc[(key,'H1_7_NN')]-A.loc[(key,base)]).reindex(range(2000,2020)).values/ref*100)
 d=np.mean(ds,axis=0);b=bootstrap((d,),np.mean,method='BCa',n_resamples=20000,random_state=SEED)
 row=dict(baseline=base,delta=d.mean(),bca_lower=b.confidence_interval.low,bca_upper=b.confidence_interval.high)
 for size in [2,3]:
  rng=np.random.default_rng(SEED+size);start=rng.integers(0,20,(20000,int(np.ceil(20/size))));ix=((start[:,:,None]+np.arange(size))%20).reshape(20000,-1)[:,:20];lo,hi=np.quantile(d[ix].mean(1),[.025,.975]);row[f'block{size}_lower']=lo;row[f'block{size}_upper']=hi
 rows.append(row)
pd.DataFrame(rows).to_csv(REVIEW/'primary_robustness.csv',index=False)
rows=[];eventrows=[]
for key in ['N','NE','SE','SW']:
 data,dates,_,y5=load_data(key,'primary');y=expand(y5);days=calendar_day(dates);refs=[]
 for year in range(2000,2020):
  f=np.load(EFOLDS/f'{key}_{year}.npz');train=f['train_index'];test=np.flatnonzero(dates.year==year)
  for j,t in enumerate(test):
   near=train[near_day(days[train],days[t])<=45];q=f['threshold90'][j,6];p=(y[near,6]>q).mean();event=y[t,6]>q;refs.append((p-event)**2);eventrows.append(dict(domain=key,date=dates[t],year=year,month=dates[t].month,training_exceedance=p,threshold=q,observed=y[t,6],event=int(event)))
 clim=np.mean(refs)
 for m in ['Raw','Bottom_up','H0_7_NN','H1_7_NN']:
  d=old.query('domain==@key and method==@m and lead=="D28"');bs=d.brier90.mean();rows.append(dict(domain=key,method=m,brier=bs,reference_brier=clim,brier_skill_score=1-bs/clim))
pd.DataFrame(rows).to_csv(REVIEW/'brier_skill.csv',index=False);pd.DataFrame(eventrows).to_csv(REVIEW/'threshold_dates.csv',index=False)
print('Brier skill:',pd.DataFrame(rows).to_string(index=False),flush=True)
print('Primary robust intervals:',pd.read_csv(REVIEW/'primary_robustness.csv').to_string(index=False),flush=True)

# Explicitly verify the new control engine reproduces the unmodified H0 model.
data,dates,r5,y5=load_data('N','primary');r=expand(r5);y=expand(y5);z=lagged_climate(dates,data);f=np.load(EFOLDS/'N_2010.npz');test=np.flatnonzero(dates.year==2010)
prediction,_=evaluate_variant(r,y,dates,z,f['train_index'],test,'N',2010,'H0')
assert np.allclose(prediction,f['H0_7_NN'],atol=1e-6)
print('PASS: control engine reproduces archived H0 forecast.',flush=True)
