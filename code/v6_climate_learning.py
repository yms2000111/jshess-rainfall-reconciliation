"""Conditional climate-adjustment learning curve with fixed base forecasts and W."""
from v6_mechanism import *
import copy
L=ROOT/'revision/review_v6/learning';L.mkdir(exist_ok=True)

def adjusted(base,raw,y,dates,z,train,penalty):
    rec=copy.deepcopy(base);days=calendar_day(dates)
    for r in rec:
        k=r['lead'];tr=train[near_day(days[train],pd.Timestamp(2000,r['group'],15).dayofyear)<=45]
        sc=r['scale_mm'];mu,var,de=moments(r['parameters'],raw[tr,:,k].mean(1)/sc,raw[tr,:,k].var(1,ddof=1)/sc**2);obs=y[tr,k]/sc
        zm=z[tr].mean(0);zs=np.maximum(z[tr].std(0),1e-6);design=(z[tr]-zm)/zs
        def objective(beta):return float(csg_crps(obs,mu*np.exp(design@beta),var,de).mean()+penalty*np.sum(beta**2))
        result=minimize(objective,np.zeros(5),method='L-BFGS-B',bounds=[(-1,1)]*5,options={'maxiter':150,'ftol':2e-9,'gtol':1e-5,'maxls':30})
        if not result.success:result=minimize(objective,result.x,method='L-BFGS-B',bounds=[(-1,1)]*5,options={'maxiter':500,'ftol':2e-10,'gtol':1e-6,'maxls':40})
        if not result.success:
            result=minimize(objective,result.x,method='Powell',bounds=[(-1,1)]*5,options={'maxiter':2000,'xtol':1e-8,'ftol':1e-10})
        if not result.success:raise RuntimeError('Climate fit failed for lead '+str(k)+' month '+str(r['group']))
        r.update(adjusted=True,control_beta=result.x.tolist(),control_mean=zm.tolist(),control_sd=zs.tolist(),indices=list(range(5)),intercept=False,success=bool(result.success),climate_fit_origins=len(tr))
    return rec

def fit_learning(task):
    system,k,year=task;key=('ACCESS_' if system=='ACCESS' else '')+k;path=L/f'{system}_{k}_{year}.npz'
    if path.exists():return path.stem+' cached'
    start=time.monotonic();d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z=lagged_climate(dates,d)
    train=permitted(dates,[year-1,year,year+1]);test=np.flatnonzero(dates.year==year)
    old=json.loads((R/f'{system}_{k}_{year}.json').read_text());base=old['records']['H0'];W=np.array(old['W']['H0'])
    years=np.unique(dates[train].year);order=np.random.default_rng(2026102603+year).permutation(years)
    scenarios=[('years10',10,.05),('years15',15,.05),('full',len(years),.05),('ridge020',len(years),.2),('ridge050',len(years),.5)]
    out=dict(y=y[test],dates=dates[test].values);meta={}
    for label,count,pen in scenarios:
        selected=order[:count];tr=train[np.isin(dates[train].year,selected)]
        if label=='full':adj=[r for r in old['records']['H2']]
        else:adj=adjusted(base,raw,y,dates,z,tr,pen)
        constructions={'H1':[r for r in base if r['lead']<4]+[r for r in adj if r['lead']>=4],'Hweekly':[r for r in adj if r['lead']<4]+[r for r in base if r['lead']>=4],'H2':adj}
        for kind,rec in constructions.items():
            _,q=predict(raw,y,dates,z,rec,test,200);template,rng=templates_original(y,dates,train,test,key,year);samples=couple7(q,template,rng)
            coherent=reconcile(samples,W,S7);name=label+'_'+kind
            assert coherent.min()>=0 and np.allclose(coherent[:,:,:4]@S7.T,coherent,atol=1e-7)
            out[name+'_crps']=crps(coherent,y[test]);out[name+'_width80']=np.quantile(coherent,.9,axis=1)-np.quantile(coherent,.1,axis=1)
            if kind=='Hweekly':out[label+'_BUclim_crps']=crps(samples[:,:,:4]@S7.T,y[test])
        beta=np.array([r['control_beta'] for r in adj]);out[label+'_beta']=beta
        meta[label]=dict(years=sorted(map(int,selected)),climate_train=tr.tolist(),penalty=pen,records=adj,mean_coefficient_norm=float(np.linalg.norm(beta,axis=1).mean()))
    # Replicate the fixed-W full-data configuration before accepting a fold.
    f=np.load(R/f'{system}_{k}_{year}.npz')
    for h in ['H1','Hweekly','H2']:assert np.allclose(out['full_'+h+'_crps'],f[h+'_fixedH0_crps'],atol=1e-9)
    np.savez_compressed(path,**out);path.with_suffix('.json').write_text(json.dumps(dict(system=system,domain=k,year=year,base_train=train.tolist(),test=test.tolist(),scenarios=meta,seconds=time.monotonic()-start),indent=2))
    return f'{path.stem}: {time.monotonic()-start:.1f}s'

def score_learning():
    rows=[]
    for path in L.glob('*.npz'):
        system,k,year=path.stem.split('_');f=np.load(path)
        for name in f.files:
            if name.endswith('_crps'):
                scenario,method=name[:-5].split('_')
                rows.append(dict(system=system,domain=k,year=int(year),scenario=scenario,method=method,crps=float(f[name][:,6].mean())))
    pd.DataFrame(rows).to_csv(L/'annual_scores.csv',index=False)
    print('Learning folds:',len(list(L.glob('*.npz'))),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--workers',type=int,default=4);p.add_argument('--score',action='store_true');a=p.parse_args()
    if a.score:score_learning()
    else:
        jobs=[(s,k,y) for s,end in [('ECMWF',2020),('ACCESS',2019)] for y in range(2000,end) for k in KEYS]
        if a.pilot:jobs=[('ECMWF','N',2010),('ACCESS','N',2010)]
        with ProcessPoolExecutor(max_workers=a.workers) as pool:
            for f in as_completed([pool.submit(fit_learning,t) for t in jobs]):print(f.result(),flush=True)
        score_learning()
