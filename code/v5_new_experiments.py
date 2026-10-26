"""Complete information-placement design and extend the fixed placebo experiment."""
from coverage_extension import *
import placebo_extension as pe
R=ROOT/'revision/review_v5';H=R/'placement';H.mkdir(parents=True,exist_ok=True)
P=R/'placebo';P.mkdir(exist_ok=True)
pe.P4=P

def combined(raw,y,dates,z,train,key,kind):
 w=adjusted_records(raw,y,dates,z,train,key,'Weekly_climate_BU')
 a=adjusted_records(raw,y,dates,z,train,key,'H1' if kind=='H2' else 'H0')
 return [r for r in w if r['lead']<4]+[r for r in a if r['lead']>=4]

def placement(task):
 key,year=task;path=H/f'{key}_{year}.npz'
 if path.exists():return f'{key} {year} cached'
 start=time.monotonic();d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z=lagged_climate(dates,d)
 train=permitted(dates,[year-1,year,year+1]);test=np.flatnonzero(dates.year==year);pred={};meta={}
 for kind in ['Hweekly','H2']:
  rec=combined(raw,y,dates,z,train,key,kind);_,q=predict(raw,y,dates,z,rec,test,200)
  template,rng=templates_original(y,dates,train,test,key,year);samples=couple7(q,template,rng);errors=[]
  for fit,val,_ in inner_splits(dates,train):
   rr=combined(raw,y,dates,z,fit,key,kind);mm,_=predict(raw,y,dates,z,rr,val);errors.append(y[val]-mm)
  W,lam=shrink(np.concatenate(errors));out=reconcile(samples,W,S7)
  assert out.min()>=0 and np.allclose(out[:,:,:4]@S7.T,out,atol=1e-7)
  pred[kind]=out;meta[kind]=dict(records=rec,W=W.tolist(),shrinkage=lam)
 np.savez_compressed(path,**pred,y=y[test],dates=dates[test].values)
 path.with_suffix('.json').write_text(json.dumps(dict(train=train.tolist(),test=test.tolist(),models=meta,seconds=time.monotonic()-start),indent=2))
 return f'{key} {year}: {time.monotonic()-start:.1f}s'

def score():
 rows=[]
 for path in H.glob('*.npz'):
  k,yr=path.stem.split('_');f=np.load(path)
  for m in ['Hweekly','H2']:
   c=crps(f[m],f['y'])
   for j,n in enumerate(NODES):rows.append(dict(domain=k,year=int(yr),method=m,lead=n,crps=c[:,j].mean()))
 pd.DataFrame(rows).to_csv(H/'annual_scores.csv',index=False)
 rows=[]
 for rep in range(100):
  files=[P/f'permutation_{rep:02d}_{y}.npz' for y in range(2000,2020)]
  if not all(f.exists() for f in files):continue
  rows.append(dict(permutation=rep,crps=np.mean([np.load(f)['crps'][:,6].mean() for f in files])))
 if rows:
  a=pd.DataFrame(rows);a.to_csv(P/'scores.csv',index=False);obs=a.query('permutation==0').iloc[0].crps
  (P/'summary.json').write_text(json.dumps(dict(observed=obs,permutations=len(a)-1,monte_carlo_p=(1+int((a.query('permutation>0').crps<=obs).sum()))/len(a),null_min=a.query('permutation>0').crps.min(),null_max=a.query('permutation>0').crps.max()),indent=2))
 print('Placement folds:',len(list(H.glob('*.npz'))),'complete placebo replicates:',len(rows),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['placement','placebo','score']);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
 if a.action=='score':score()
 else:
  if a.action=='placebo':
   import shutil
   for f in (ROOT/'revision/review_v4/placebo').glob('permutation_*.npz'):
    if not (P/f.name).exists():shutil.copy2(f,P/f.name)
   jobs=[(r,y) for r in range(21,100) for y in range(2000,2020)];fn=pe.run
  else:jobs=[(k,y) for y in range(2000,2020) for k in REGIONS];fn=placement
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(fn,t) for t in jobs]):print(f.result(),flush=True)
  score()
