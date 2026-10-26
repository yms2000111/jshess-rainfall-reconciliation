"""Post hoc 2x2 information-placement and covariance ablation, 26 Oct 2026.

All outer-year exclusions, marginal fits and historical rank templates are
unchanged. A common H0 covariance is compared with each configuration's own
inner-fold covariance. No outer score selects a model or a weight matrix.
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from coverage_extension import *
R=ROOT/'revision/review_v6/mechanism'; R.mkdir(parents=True,exist_ok=True)
KEYS=['N','NE','SE','SW','NW','CA','EC','TAS']
for k in KEYS: REGIONS['ACCESS_'+k]=REGIONS[k].copy()
KINDS=['H0','H1','Hweekly','H2']

def records(raw,y,dates,z,train,key):
    base=adjusted_records(raw,y,dates,z,train,key,'H0')
    agg=adjusted_records(raw,y,dates,z,train,key,'H1')
    week=adjusted_records(raw,y,dates,z,train,key,'Weekly_climate_BU')
    return dict(H0=base,H1=agg,Hweekly=[r for r in week if r['lead']<4]+[r for r in base if r['lead']>=4],H2=[r for r in week if r['lead']<4]+[r for r in agg if r['lead']>=4])

def run(task):
    system,k,year=task;key=('ACCESS_' if system=='ACCESS' else '')+k
    path=R/f'{system}_{k}_{year}.npz'
    if path.exists():return path.stem+' cached'
    start=time.monotonic();d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z=lagged_climate(dates,d)
    train=permitted(dates,[year-1,year,year+1]);test=np.flatnonzero(dates.year==year)
    assert not set(dates[train].year)&{year-1,year,year+1}
    rec=records(raw,y,dates,z,train,key);errors={h:[] for h in KINDS};inner=[]
    for fit,val,_ in inner_splits(dates,train):
        assert set(fit)<=set(train) and set(val)<=set(train) and not set(fit)&set(val)
        rr=records(raw,y,dates,z,fit,key);inner.append(dict(fit=fit.tolist(),validation=val.tolist()))
        for h in KINDS:
            mm,_=predict(raw,y,dates,z,rr[h],val);errors[h].append(y[val]-mm)
    weights={h:shrink(np.concatenate(errors[h])) for h in KINDS}
    result=dict(dates=dates[test].values,y=y[test],Raw_crps=crps(raw[test],y[test]))
    for h in KINDS:
        _,q=predict(raw,y,dates,z,rec[h],test,200)
        template,rng=templates_original(y,dates,train,test,key,year)
        samples=couple7(q,template,rng)
        if h in ['H0','Hweekly']:
            name='BUrain' if h=='H0' else 'BUclim';bu=samples[:,:,:4]@S7.T
            result[name+'_crps']=crps(bu,y[test])
        for mode in ['own','fixedH0']:
            W=weights[h if mode=='own' else 'H0'][0];out=reconcile(samples,W,S7)
            assert np.isfinite(out).all() and out.min()>=0 and np.allclose(out[:,:,:4]@S7.T,out,atol=1e-7)
            name=h+'_'+mode;result[name+'_crps']=crps(out,y[test]);result[name+'_mean_error']=out.mean(1)-y[test]
            result[name+'_width80']=np.quantile(out,.9,axis=1)-np.quantile(out,.1,axis=1)
    np.savez_compressed(path,**result)
    path.with_suffix('.json').write_text(json.dumps(dict(system=system,domain=k,year=year,train=train.tolist(),test=test.tolist(),inner=inner,records=rec,W={h:w[0].tolist() for h,w in weights.items()},shrinkage={h:w[1] for h,w in weights.items()},seconds=time.monotonic()-start),indent=2))
    return f'{path.stem}: {time.monotonic()-start:.1f}s'

def score():
    rows=[]
    for path in R.glob('*.npz'):
        system,k,year=path.stem.split('_');f=np.load(path)
        for name in f.files:
            if name.endswith('_crps'):
                for j,node in enumerate(NODES):rows.append(dict(system=system,domain=k,year=int(year),method=name[:-5],lead=node,crps=float(f[name][:,j].mean())))
    a=pd.DataFrame(rows);a.to_csv(R/'annual_scores.csv',index=False)
    if len(a):print(a.query('lead=="D28"').groupby(['system','method']).crps.mean().to_string(),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');p.add_argument('--score',action='store_true');p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    if a.score:score()
    else:
        jobs=[(s,k,y) for s,end in [('ECMWF',2020),('ACCESS',2019)] for y in range(2000,end) for k in KEYS]
        if a.pilot:jobs=[('ECMWF','N',2010),('ACCESS','N',2010)]
        with ProcessPoolExecutor(max_workers=a.workers) as pool:
            for f in as_completed([pool.submit(run,t) for t in jobs]):print(f.result(),flush=True)
        score()
