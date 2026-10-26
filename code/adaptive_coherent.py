"""Nested empirical-distribution mixtures and simple inner-score selectors."""
from review_controls import *
from scipy.special import softmax

V4=ROOT/'revision/review_v4';AD=V4/'adaptive';AD.mkdir(exist_ok=True)
COMP=['Raw','Weekly_climate_BU','H1']
CAND=['Raw','Bottom_up','Weekly_climate_BU','H0','H1']
FEATURES=['intercept','sin_year','cos_year','rmm1','rmm2','dmi','log_spread','aggregate_difference']
REGIONS['ACCESS_N']=REGIONS['N'].copy()

def distance(x,y):
 """Mean pair distance for each case, without a quadratic sample array."""
 ans=[]
 for a,b in zip(x,y):
  b=np.sort(b);s=np.r_[0,np.cumsum(b)];n=np.searchsorted(b,a,side='right')
  ans.append(np.mean((a*n-s[n])+(s[-1]-s[n]-a*(len(b)-n)))/len(b))
 return np.array(ans)

def terms(pred,y,lead=6):
 x=[pred[m][:,:,lead] for m in COMP]
 A=np.column_stack([np.abs(v-y[:,lead,None]).mean(1) for v in x]);B=np.zeros((len(y),3,3))
 for j in range(3):
  for k in range(j+1):B[:,j,k]=B[:,k,j]=distance(x[j],x[k])
 return A,B

def mix_score(A,B,w):return (A*w).sum(1)-.5*np.einsum('ni,nij,nj->n',w,B,w)

def features(pred,dates,z):
 angle=2*np.pi*calendar_day(dates)/366
 return np.column_stack([np.ones(len(dates)),np.sin(angle),np.cos(angle),z[:,:2],z[:,3],np.log1p(pred['Raw'][:,:,6].std(1)),pred['H1'][:,:,6].mean(1)-pred['Weekly_climate_BU'][:,:,6].mean(1)])

def learn(A,B,X,dates,obs,kind):
 n=1 if kind=='Constant' else 3 if kind=='Seasonal' else X.shape[1]
 X=X[:,:n];mean=X.mean(0);sd=np.maximum(X.std(0),1e-6);mean[0]=0;sd[0]=1;D=(X-mean)/sd
 scale=max(float(np.mean(obs)),1.);counts=pd.Series(dates.year).value_counts();cw=np.array([1/counts[v] for v in dates.year]);cw/=cw.sum()
 def objective(v):
  beta=v.reshape(n,2);w=softmax(np.column_stack([D@beta,np.zeros(len(D))]),axis=1)
  score=mix_score(A,B,w);dw=(A-np.einsum('nij,nj->ni',B,w))/scale
  dl=w*(dw-(w*dw).sum(1,keepdims=True));gradient=D.T@(dl[:,:2]*cw[:,None])+.02*beta/beta.size
  return float(cw@score/scale+.01*np.mean(beta**2)),gradient.ravel()
 fit=minimize(objective,np.zeros(n*2),jac=True,method='L-BFGS-B',bounds=[(-6,6)]*(n*2),options={'maxiter':500,'ftol':1e-11,'gtol':1e-7})
 assert fit.success,fit.message
 return dict(beta=fit.x.reshape(n,2).tolist(),mean=mean.tolist(),sd=sd.tolist(),objective=float(fit.fun),n=n,scale=scale)

def weights(model,X):
 D=(X[:,:model['n']]-model['mean'])/model['sd'];return softmax(np.column_stack([D@np.array(model['beta']),np.zeros(len(D))]),axis=1)

def components(raw,y,dates,z,fit,val,key,seed,cached_h1=None):
 p={'Raw':raw[val]}
 for k in ['H0','Weekly_climate_BU']:
  p[k],_=evaluate_variant(raw,y,dates,z,fit,val,key,seed,k)
 if cached_h1 is None:p['H1'],_=evaluate_variant(raw,y,dates,z,fit,val,key,seed,'H1')
 else:p['H1']=cached_h1
 rec=base_records(raw,y,dates,z,fit,key,'primary');_,q=predict(raw,y,dates,z,rec,val,200)
 template,rng=templates_original(y,dates,fit,val,key,seed);q=couple7(q,template,rng);p['Bottom_up']=q[:,:,:4]@S7.T
 for a in p.values():assert a.min()>=0 and np.allclose(a[...,:4]@S7.T,a,atol=1e-7)
 return p

def outer(key,year,raw,y,dates,z,train,test):
 if isinstance(year,str) and year.startswith('roll'):
  return components(raw,y,dates,z,train,test,key,int(year[4:])+1)
 if year=='forward':
  f=RFOLDS/f'forward_{key}.npz'
  if f.exists():return {k:np.load(f)[k] for k in CAND}
  return components(raw,y,dates,z,train,test,key,2015)
 if key in ['N','NE','SE','SW']:
  old=np.load(EFOLDS/f'{key}_{year}.npz');r=np.load(RFOLDS/f'{key}_{year}.npz')
  return dict(Raw=raw[test],Bottom_up=old['Bottom_up'],H0=old['H0_7_NN'],H1=old['H1_7_NN'],Weekly_climate_BU=r['Weekly_climate_BU'])
 f=np.load(V4/('access_s2/folds' if key=='ACCESS_N' else 'coverage')/f'{key}_{year}.npz')
 return {k:f[k] for k in CAND}

def run(task):
 key,year=task;target=AD/f'{key}_{year}.npz'
 if target.exists():return f'{key} {year} adaptive cached'
 start=time.monotonic();d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z=lagged_climate(dates,d)
 if isinstance(year,str) and year.startswith('roll'):
  cutoff=int(year[4:]);train=np.flatnonzero((dates.year<=cutoff)&((dates+pd.Timedelta(days=28)).year<=cutoff));test=np.flatnonzero((dates.year>cutoff)&(dates.year<=cutoff+3));seed=cutoff+1
 elif year=='forward':
  train=np.flatnonzero((dates.year<=2014)&((dates+pd.Timedelta(days=28)).year<=2014));test=np.flatnonzero(dates.year>=2015);seed=2015
 else:train=permitted(dates,[year-1,year,year+1]);test=np.flatnonzero(dates.year==year);seed=year
 assert not set(train)&set(test)
 cache=AD/f'inner_{key}_{year}.npz'
 if cache.exists():
  f=np.load(cache);A,B,X,ix,loss=[f[k] for k in ['A','B','X','index','loss']]
 else:
  old=EXT/'recalibration'/f'{key}_{year}.npz';old=np.load(old) if old.exists() else None
  if old is not None:
   assert sorted(old['inner_index'])==sorted(train);lookup={int(v):i for i,v in enumerate(old['inner_index'])}
  aa=[];bb=[];xx=[];ii=[];ll=[]
  for j,(fit,val,embargo) in enumerate(inner_splits(dates,train)):
   h=None if old is None else old['inner_samples'][[lookup[int(i)] for i in val]]
   p=components(raw,y,dates,z,fit,val,key,seed+j*37,h)
   a,b=terms(p,y[val]);aa.append(a);bb.append(b);xx.append(features(p,dates[val],z[val]));ii.extend(val)
   ll.append(np.column_stack([crps(p[k],y[val])[:,6] for k in CAND]))
  A=np.concatenate(aa);B=np.concatenate(bb);X=np.concatenate(xx);ix=np.array(ii);loss=np.concatenate(ll)
  assert sorted(ix)==sorted(train)
  np.savez_compressed(cache,A=A,B=B,X=X,index=ix,loss=loss)
 p=outer(key,year,raw,y,dates,z,train,test);Xt=features(p,dates[test],z[test]);mods={k:learn(A,B,X,dates[ix],y[ix,6],k) for k in ['Constant','Seasonal','State']}
 w={k:weights(v,Xt) for k,v in mods.items()};w['Equal']=np.full((len(test),3),1/3)
 # Match the annual weighting used by mixture training and evaluation.
 iy=dates[ix].year;cnt=pd.Series(iy).value_counts();iw=np.array([1/cnt[t] for t in iy]);iw/=iw.sum()
 global_choice=int(np.argmin(iw@loss));seasons=((dates[ix].month%12)//3).values;testseasons=((dates[test].month%12)//3).values
 seasonal={int(s):int(np.argmin(np.average(loss[seasons==s],axis=0,weights=iw[seasons==s]))) for s in range(4)}
 methods=CAND+['Equal','Constant','Seasonal','State','Select_global','Select_season']
 scores=np.zeros((len(test),len(methods),7));probs=np.zeros((len(test),len(methods),2));rps=np.zeros((len(test),len(methods)))
 thresholds=[];climp=[];climrps=[];days=calendar_day(dates)
 for t in test:
  near=train[near_day(days[train],days[t])<=45];obs=y[near,6];q=np.quantile(obs,[1/3,2/3]);thresholds.append(q)
  climp.append([(obs>v).mean() for v in [50,100]])
  climrps.append(np.sum((np.array([(obs<=v).mean() for v in q])-(y[t,6]<=q))**2))
 thresholds=np.array(thresholds);probcomp={};cdfcomp={}
 for k in CAND:
  scores[:,methods.index(k)]=crps(p[k],y[test]);probcomp[k]=np.column_stack([(p[k][:,:,6]>v).mean(1) for v in [50,100]])
  cdfcomp[k]=(p[k][:,:,6,None]<=thresholds[:,None,:]).mean(1)
  probs[:,methods.index(k)]=probcomp[k];rps[:,methods.index(k)]=((cdfcomp[k]-(y[test,6,None]<=thresholds))**2).sum(1)
 for name,ww in w.items():
  at=methods.index(name)
  for lead in range(7):a,b=terms(p,y[test],lead);scores[:,at,lead]=mix_score(a,b,ww)
  probs[:,at]=sum(ww[:,j,None]*probcomp[k] for j,k in enumerate(COMP))
  cdf=sum(ww[:,j,None]*cdfcomp[k] for j,k in enumerate(COMP));rps[:,at]=((cdf-(y[test,6,None]<=thresholds))**2).sum(1)
 for name,choice in [('Select_global',np.full(len(test),global_choice)),('Select_season',np.array([seasonal[int(s)] for s in testseasons]))]:
  at=methods.index(name);scores[:,at]=scores[np.arange(len(test)),choice];probs[:,at]=probs[np.arange(len(test)),choice];rps[:,at]=rps[np.arange(len(test)),choice]
 np.savez_compressed(target,methods=methods,dates=dates[test].values,y=y[test],scores=scores,probs=probs,rps=rps,climp=climp,climrps=climrps,thresholds=thresholds,**{'weight_'+k:v for k,v in w.items()})
 target.with_suffix('.json').write_text(json.dumps(dict(domain=key,year=year,train=train.tolist(),test=test.tolist(),models=mods,features=FEATURES,global_choice=CAND[global_choice],season_choice={s:CAND[v] for s,v in seasonal.items()},seconds=time.monotonic()-start),indent=2))
 return f'{key} {year}: adaptive {time.monotonic()-start:.1f}s'

def check():
 rng=np.random.default_rng(17);p={k:rng.gamma(2,3,(4,n,4))@S7.T for k,n in zip(CAND,[11,200,200,200,200])};y=rng.gamma(2,3,(4,4))@S7.T
 A,B=terms(p,y);w=rng.dirichlet([1,1,1],4);got=mix_score(A,B,w)
 for i in range(4):
  x=np.concatenate([p[k][i,:,6] for k in COMP]);v=np.concatenate([np.full(p[k].shape[1],w[i,j]/p[k].shape[1]) for j,k in enumerate(COMP)])
  expected=v@abs(x-y[i,6])-.5*np.sum(v[:,None]*v[None,:]*abs(x[:,None]-x[None,:]));assert np.isclose(got[i],expected)
 for j,k in enumerate(COMP):assert np.allclose(mix_score(A,B,np.eye(3)[[j]*4]),crps(p[k],y)[:,6])
 print('Weighted CRPS matches brute force and all one-component limits.',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=6);p.add_argument('--check',action='store_true');p.add_argument('--pilot',action='store_true');p.add_argument('--forward',action='store_true');p.add_argument('--rolling',action='store_true');p.add_argument('--domains',nargs='+',default=['N','NE','SE','SW']);a=p.parse_args()
 if a.check:check()
 else:
  tasks=[('N',2010)] if a.pilot else [(k,'forward' if a.forward else yr) for k in a.domains for yr in ([2015] if a.forward else range(2000,2019 if k=='ACCESS_N' else 2020))]
  if a.rolling:tasks=[(k,'roll'+str(c)) for k in a.domains for c in [2009,2012,2015]]
  with ProcessPoolExecutor(max_workers=a.workers) as pool:
   for f in as_completed([pool.submit(run,t) for t in tasks]):print(f.result(),flush=True)
