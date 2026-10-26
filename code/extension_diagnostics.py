"""Sampling, multivariate and seasonally stratified diagnostics."""
from extension_cv import *
from analyse import crps
from scipy.spatial.distance import pdist

def stability(task):
 key,year=task;path=EXT/f'stability_{key}_{year}.csv'
 if path.exists():return str(path.name)
 d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z,_=climate(dates,d);f=np.load(EFOLDS/f'{key}_{year}.npz');train=f['train_index'];test=np.flatnonzero(dates.year==year);records=records_extended(raw,y,dates,z,train,key);base=fit_records(r5,y5,dates,train,key,'primary');rows=[]
 for size in [200,500,1000]:
  _,_,q=distributions(raw,y,dates,z,records,test,size,True);_,_,bq=distribution(r5,y5,dates,base,test,size);q[:,:,:4]=bq[:,:,:4]
  for seed in range(3):
   templates,rng=templates_original(y,dates,train,test,key,year+seed*10000,size);samples=couple7(q,templates,rng);rec=reconcile(samples,f['H1_7_W'],S7);bu=samples[:,:,:4]@S7.T
   a=crps(rec,y[test]);b=crps(bu,y[test]);assert seed!=0 or size!=200 or np.allclose(rec,f['H1_7_NN'])
   for k in [0,1,2,3,6]:rows.append(dict(domain=key,year=year,size=size,seed=seed,lead=NODES[k],crps=a[:,k].mean(),delta_bu=(a[:,k]-b[:,k]).mean()))
 pd.DataFrame(rows).to_csv(path,index=False);return f'{key} {year} sample sensitivity'

def joint_scores():
 rows=[]
 for key in REGIONS:
  for year in range(2000,2020):
   f=np.load(EFOLDS/f'{key}_{year}.npz');y=f['y'][:,:4]
   for method in ['Raw','Bottom_up','H0_7_NN','H1_7_NN']:
    a=f[method][:,:,:4];m=a.shape[1];energy=[];variogram=np.zeros(len(a))
    for i in range(len(a)):energy.append(np.linalg.norm(a[i]-y[i],axis=1).mean()-pdist(a[i]).sum()/m**2)
    for j in range(4):
     for k in range(j):variogram+=(np.abs(y[:,j]-y[:,k])**.5-(np.abs(a[:,:,j]-a[:,:,k])**.5).mean(1))**2
    rows.append(dict(domain=key,year=year,method=method,energy=np.mean(energy),variogram=variogram.mean()))
  print('Joint scores',key,flush=True)
 pd.DataFrame(rows).to_csv(EXT/'joint_scores_annual.csv',index=False)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=4);p.add_argument('--joint',action='store_true');args=p.parse_args()
 if args.joint:joint_scores()
 else:
  with ProcessPoolExecutor(max_workers=args.workers) as pool:
   for f in as_completed([pool.submit(stability,(k,y)) for y in range(2000,2020) for k in REGIONS]):print(f.result(),flush=True)
  pd.concat([pd.read_csv(p) for p in EXT.glob('stability_*_*.csv')]).to_csv(EXT/'sample_stability.csv',index=False)
