"""Frozen climate-information by hierarchy experiment; extends revision_cv."""
from revision_cv import *
from bs4 import BeautifulSoup
import re,itertools,copy
EXT=OUT/'extension';EXT.mkdir(exist_ok=True)
ECACHE=EXT/'cache';ECACHE.mkdir(exist_ok=True)
EFOLDS=EXT/'folds';EFOLDS.mkdir(exist_ok=True)
S7=np.vstack([np.eye(4),[1,1,0,0],[0,0,1,1],np.ones(4)])
S5=np.vstack([np.eye(4),np.ones(4)])
NODES=['W1','W2','W3','W4','F12','F34','D28']
VERSION_EXT='fixed-base-climate-mean-ridge005-v1'

def expand(a):return np.concatenate([a[...,:4],a[...,:2].sum(-1,keepdims=True),a[...,2:4].sum(-1,keepdims=True),a[...,4:5]],axis=-1)

def shrink(errors):
 e=errors-errors.mean(0);sd=np.maximum(e.std(0,ddof=0),.1);z=e/sd;n=len(z)
 r=z.T@z/n;var_r=np.mean((z[:,:,None]*z[:,None,:]-r)**2,axis=0)/n;off=~np.eye(e.shape[1],dtype=bool)
 lam=float(np.clip(var_r[off].sum()/max((r[off]**2).sum(),1e-12),0,1));W=((1-lam)*r+lam*np.eye(e.shape[1]))*sd[:,None]*sd[None,:]+np.diag(sd**2)*1e-8
 return W,lam

def reconcile(v,W,S,nonnegative=True):
 a=np.asarray(v);flat=a.reshape(-1,S.shape[0]);Q=np.linalg.inv(W);H=S.T@Q@S;rhs=flat@Q@S
 if not nonnegative:return (np.linalg.solve(H,rhs.T).T@S.T).reshape(a.shape)
 best=np.zeros((len(flat),4));cost=np.full(len(flat),np.inf)
 for bits in itertools.product([False,True],repeat=4):
  ix=np.flatnonzero(bits);b=np.zeros_like(best)
  if len(ix):b[:,ix]=np.linalg.solve(H[np.ix_(ix,ix)],rhs[:,ix].T).T
  good=(b>=-1e-9).all(1);b=np.maximum(b,0);res=b@S.T-flat;c=np.einsum('ni,ij,nj->n',res,Q,res);take=good&(c<cost);best[take]=b[take];cost[take]=c[take]
 return (best@S.T).reshape(a.shape)

def climate(dates,data):
 dm=pd.read_csv(ROOT/'data/support/dmi.csv',index_col=0);dm.index=pd.to_datetime(dm.index)
 # BAS returned a maintenance page to requests; use the archived tool-retrieved
 # official page, keeping its source URL and retrieval details with the numbers.
 txt=(ROOT/'data/support/sam_web_snapshot.txt').read_text(encoding='utf-8')
 rows=re.findall(r'(?<!\d)(19\d{2}|20\d{2})\s+((?:[+-]?\d+\.\d+\s+){11}[+-]?\d+\.\d+)',txt)
 sam={pd.Timestamp(int(yr),m,1):float(v) for yr,row in rows for m,v in enumerate(row.split(),1)}
 months=dates.to_period('M').to_timestamp()-pd.DateOffset(months=2)
 values=np.column_stack([data['climate'],dm.reindex(months).iloc[:,0].values,[sam[t] for t in months]])
 assert np.isfinite(values).all(), 'Missing climate index'
 assert ((months+pd.offsets.MonthEnd(0))<dates).all()
 audit=pd.DataFrame(dict(origin=dates,rmm_date=dates-pd.Timedelta(days=2),monthly_period=months,rmm1=values[:,0],rmm2=values[:,1],nino34_sst=values[:,2],dmi=values[:,3],sam=values[:,4]))
 return values,audit

def records_extended(raw,y,dates,z,train,key,qc='primary'):
 stamp=hashlib.sha256((VERSION_EXT+key+('' if qc=='primary' else ':'+qc)).encode()+train.tobytes()).hexdigest()[:24];path=ECACHE/(stamp+'.json')
 if path.exists():return json.loads(path.read_text())
 base=fit_records(raw[...,[0,1,2,3,6]],y[:,[0,1,2,3,6]],dates,train,key,qc)
 records=[];days=calendar_day(dates)
 for k in range(4,7):
  warm=None;oldscale=None
  for month in range(1,13):
   tr=train[near_day(days[train],pd.Timestamp(2000,month,15).dayofyear)<=45];sc=max(y[tr,k].mean(),.1)
   x=raw[tr,:,k].mean(1)/sc;v=raw[tr,:,k].var(1,ddof=1)/sc**2;obs=y[tr,k]/sc
   if k==6:
    r=next(q for q in base if q['lead']==4 and q['group']==month);p=np.array(r['parameters']);assert np.isclose(sc,r['scale_mm']);success=r['success']
   else:
    def objective(lp):
     mu,var,de=moments(np.exp(lp),x,v);return float(np.mean(csg_crps(obs,mu,var,de)))
    p0=np.array([.1,1,.1,.5,.5,.1]) if warm is None else warm*np.array([oldscale/sc,1,(oldscale/sc)**2,oldscale/sc,1,oldscale/sc])
    result=minimize(objective,np.log(np.maximum(p0,1e-5)),method='L-BFGS-B',bounds=[(-10,5)]*6,options={'maxiter':180,'ftol':2e-8,'gtol':2e-5,'maxls':30})
    if not result.success:
     retry=minimize(objective,result.x,method='L-BFGS-B',bounds=[(-10,5)]*6,options={'maxiter':500,'ftol':2e-9,'gtol':1e-5,'maxls':40})
     if retry.fun<=result.fun:result=retry
    p=np.exp(result.x);success=bool(result.success)
   warm=p.copy();oldscale=sc;mu,var,de=moments(p,x,v)
   zm=z[tr].mean(0);zs=np.maximum(z[tr].std(0),1e-6);std=(z[tr]-zm)/zs
   def climate_objective(beta):return float(csg_crps(obs,mu*np.exp(std@beta),var,de).mean()+.05*np.sum(beta**2))
   result=minimize(climate_objective,np.zeros(5),method='L-BFGS-B',bounds=[(-1,1)]*5,options={'maxiter':150,'ftol':2e-9,'gtol':1e-5,'maxls':30})
   if not result.success:
    result=minimize(climate_objective,result.x,method='L-BFGS-B',bounds=[(-1,1)]*5,options={'maxiter':500,'ftol':2e-10,'gtol':1e-6,'maxls':40})
   records.append(dict(group=month,lead=k,scale_mm=float(sc),parameters=p.tolist(),base_success=success,beta=result.x.tolist(),z_mean=zm.tolist(),z_sd=zs.tolist(),climate_success=bool(result.success),n=len(tr),legacy=False))
 path.write_text(json.dumps(records,indent=2));return records

def distributions(raw,y,dates,z,records,ix,members=None,heterogeneous=False):
 means=np.zeros((len(ix),7));exact=np.zeros_like(means);samples=None if members is None else np.zeros((len(ix),members,7))
 for r in records:
  local=np.flatnonzero(dates.month.to_numpy()[ix]==r['group']);ids=ix[local];k=r['lead'];sc=r['scale_mm']
  if not len(local):continue
  mu,var,de=moments(r['parameters'],raw[ids,:,k].mean(1)/sc,raw[ids,:,k].var(1,ddof=1)/sc**2)
  if heterogeneous:mu*=np.exp(((z[ids]-r['z_mean'])/r['z_sd'])@np.array(r['beta']))
  means[local,k]=mean_csg(mu,var,de)*sc;exact[local,k]=csg_crps(y[ids,k]/sc,mu,var,de)*sc
  if members is not None:samples[local,:,k]=np.maximum(gamma.ppf(((np.arange(members)+.5)/members)[None,:],(mu*mu/var)[:,None],scale=(var/mu)[:,None])-de,0)*sc
 return means,exact,samples

def templates_original(y,dates,train,test,key,year,members=200):
 rng=np.random.default_rng(SEED+year+1000*list(REGIONS).index(key));days=calendar_day(dates);templates=[]
 for t in test:
  near=train[near_day(days[train],days[t])<=45];templates.append(y[rng.choice(near,members,replace=True)])
  # Preserve exact RNG consumption of the benchmark for its 200-member product.
  rng.choice(near,11,replace=False);rng.choice(near,members,replace=True)
 return np.array(templates),rng

def couple7(q,templates,rng):
 out=np.empty_like(q)
 # Same first five rank assignments as the archived five-node benchmark.
 for i in range(len(out)):
  for k in [0,1,2,3,6]:
   order=np.lexsort((rng.random(q.shape[1]),templates[i,:,k]));out[i,order,k]=q[i,:,k]
 for i in range(len(out)):
  for k in [4,5]:
   order=np.lexsort((rng.random(q.shape[1]),templates[i,:,k]));out[i,order,k]=q[i,:,k]
 return out

def run_extension(task):
 key,year=task;target=EFOLDS/f'{key}_{year}.npz'
 if target.exists():return f'{key} {year} cached'
 started=time.monotonic();d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z,audit=climate(dates,d)
 train=permitted(dates,[year-1,year,year+1]);test=np.flatnonzero(dates.year==year);old=np.load(FOLDS/f'primary_{key}_{year}.npz')
 assert np.array_equal(train,old['train_index'])
 oi=old['oof_index'];omap={int(t):i for i,t in enumerate(oi)};oof={h:np.zeros((len(oi),7)) for h in ['H0','H1']}
 for h in oof:oof[h][:,:4]=old['oof_mean'][:,:4]
 for fit,val,_ in inner_splits(dates,train):
  rec=records_extended(raw,y,dates,z,fit,key);positions=np.array([omap[int(t)] for t in val])
  for h in oof:oof[h][positions,4:]=distributions(raw,y,dates,z,rec,val,heterogeneous=h=='H1')[0][:,4:]
 rec=records_extended(raw,y,dates,z,train,key);base=fit_records(r5,y5,dates,train,key,'primary');bm,be,bq=distribution(r5,y5,dates,base,test,200)
 templates,rng=templates_original(y,dates,train,test,key,year);state=copy.deepcopy(rng.bit_generator.state)
 pred={};extras={};rows=[]
 for h in ['H0','H1']:
  mean,exact,q=distributions(raw,y,dates,z,rec,test,200,h=='H1');mean[:,:4]=bm[:,:4];exact[:,:4]=be[:,:4];q[:,:,:4]=bq[:,:,:4]
  rng.bit_generator.state=copy.deepcopy(state);samples=couple7(q,templates,rng)
  assert np.allclose(samples[:,:,:4],old['Direct_EMOS'][:,:,:4])
  pred[h+'_Direct']=samples;extras[h+'_mean']=mean;extras[h+'_exact']=exact;extras[h+'_oof']=oof[h]
  for nodes,Sx,indices in [(5,S5,[0,1,2,3,6]),(7,S7,list(range(7)))]:
   W,lam=shrink(y[oi][:,indices]-oof[h][:,indices]);reconciled=reconcile(samples[:,:,indices],W,Sx)
   if nodes==5:reconciled=expand(reconciled)
   pred[f'{h}_{nodes}_NN']=reconciled;extras[f'{h}_{nodes}_W']=W
   extras[f'{h}_{nodes}_linear']=reconcile(mean[:,indices],W,Sx,False)
   if h=='H0' and nodes==5:
    assert np.allclose(W,old['W'],atol=1e-7)
    assert np.allclose(reconciled[:,:,[0,1,2,3,6]],old['MinT_NN'],atol=1e-6)
   rows.append(dict(information=h,nodes=nodes,shrinkage=lam,min_eigenvalue=float(np.linalg.eigvalsh(W).min())))
 pred['Bottom_up']=expand(old['Bottom_up']);pred['Raw']=expand(old['Raw'])
 thresholds=[];ref=[];days=calendar_day(dates)
 for t in test:
  near=train[near_day(days[train],days[t])<=45];thresholds.append(np.quantile(y[near],.9,axis=0));s=np.sort(y[near],axis=0);n=len(near);ref.append(np.abs(s-y[t]).mean(0)-(s*(2*np.arange(1,n+1)-n-1)[:,None]).sum(0)/n**2)
 np.savez_compressed(target,**pred,**extras,y=y[test],dates=dates[test].values,threshold90=thresholds,reference=ref,train_index=train,oof_index=oi)
 target.with_suffix('.json').write_text(json.dumps(dict(domain=key,year=year,records=rec,weights=rows,train=train.tolist(),test=test.tolist(),seconds=time.monotonic()-started),indent=2))
 return f'{key} {year}: {time.monotonic()-started:.1f}s, benchmark reproduced'

def main():
 p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--workers',type=int,default=6);a=p.parse_args()
 d,dates,_,_=load_data('N','primary');_,audit=climate(dates,d);audit.to_csv(EXT/'predictor_date_audit.csv',index=False)
 tasks=[('N',2010)] if a.pilot else [(k,y) for y in range(2000,2020) for k in REGIONS]
 with ProcessPoolExecutor(max_workers=a.workers) as pool:
  for f in as_completed([pool.submit(run_extension,t) for t in tasks]):print(f.result(),flush=True)
if __name__=='__main__':main()
