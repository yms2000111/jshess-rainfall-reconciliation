"""Triple-nested calibration of an aggregate power map, preserving weekly shares."""
from extension_cv import *
from analyse import crps
RDIR=EXT/'recalibration';RDIR.mkdir(exist_ok=True)

def joint_prediction(raw,y,dates,z,fit,val,key,seed,members=200):
 rec=records_extended(raw,y,dates,z,fit,key);mean,_,q=distributions(raw,y,dates,z,rec,val,members,True)
 base=fit_records(raw[...,[0,1,2,3,6]],y[:,[0,1,2,3,6]],dates,fit,key,'primary');bm,_,bq=distribution(raw[...,[0,1,2,3,6]],y[:,[0,1,2,3,6]],dates,base,val,members);mean[:,:4]=bm[:,:4]
 if members is None:return mean,None
 q[:,:,:4]=bq[:,:,:4];rng=np.random.default_rng(seed);days=calendar_day(dates);templates=[]
 for t in val:
  near=fit[near_day(days[fit],days[t])<=45];templates.append(y[rng.choice(near,members,replace=True)])
 return mean,couple7(q,np.array(templates),rng)

def apply_map(samples,a,b,sc):
 total=samples[...,6];mapped=sc*np.exp(a)*np.power(total/sc,np.exp(b));factor=np.divide(mapped,total,out=np.zeros_like(total),where=total>0)
 weeks=samples[...,:4]*factor[...,None]
 return weeks@S7.T

def run(task):
 key,year=task;target=RDIR/f'{key}_{year}.npz'
 if target.exists():return f'{key} {year} recal cached'
 start=time.monotonic();d,dates,r5,y5=load_data(key,'primary');raw=expand(r5);y=expand(y5);z,_=climate(dates,d);train=permitted(dates,[year-1,year,year+1]);test=np.flatnonzero(dates.year==year);innerq=[];innerix=[]
 for j,(fit,val,_) in enumerate(inner_splits(dates,train)):
  errors=[]
  for fit2,val2,_ in inner_splits(dates,fit):
   mean,_=joint_prediction(raw,y,dates,z,fit2,val2,key,0,None);errors.append(y[val2]-mean)
  W,_=shrink(np.concatenate(errors));_,q=joint_prediction(raw,y,dates,z,fit,val,key,SEED+year+1000*list(REGIONS).index(key)+j*37)
  innerq.append(reconcile(q,W,S7));innerix.extend(val)
 q=np.concatenate(innerq);ix=np.array(innerix);assert sorted(ix)==sorted(train);days=calendar_day(dates);f=np.load(EFOLDS/f'{key}_{year}.npz');out=np.empty_like(f['H1_7_NN']);rows=[]
 for month in range(1,13):
  loc=near_day(days[ix],pd.Timestamp(2000,month,15).dayofyear)<=45;obs=y[ix[loc],6];sc=max(obs.mean(),.1);vals=np.sort(q[loc,:,6]/sc,axis=1);o=obs/sc;m=vals.shape[1];coef=(2*np.arange(1,m+1)-m-1)/m**2
  def objective(ab):
   v=np.exp(ab[0])*np.power(vals,np.exp(ab[1]));return float((np.abs(v-o[:,None]).mean(1)-(v*coef).sum(1)).mean()+.01*np.sum(ab**2))
  res=minimize(objective,[0.,0.],method='L-BFGS-B',bounds=[(-.7,.7),(-.35,.35)],options={'maxiter':200,'ftol':1e-10,'maxls':40})
  use=np.flatnonzero(dates[test].month==month);out[use]=apply_map(f['H1_7_NN'][use],*res.x,sc)
  rows.append(dict(month=month,log_scale=float(res.x[0]),log_power=float(res.x[1]),reference_scale=float(sc),success=bool(res.success),n=int(loc.sum())))
 totalonly=f['H1_7_NN'].copy();totalonly[:,:,6]=out[:,:,6];np.savez_compressed(target,coherent=out,total_only=totalonly,dates=f['dates'],y=f['y'],inner_index=ix,inner_samples=q)
 target.with_suffix('.json').write_text(json.dumps(dict(domain=key,year=year,records=rows,seconds=time.monotonic()-start),indent=2))
 return f'{key} {year}: nested recalibration {time.monotonic()-start:.1f}s'

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=6);p.add_argument('--pilot',action='store_true');a=p.parse_args();tasks=[('N',2010)] if a.pilot else [(k,yr) for yr in range(2000,2020) for k in REGIONS]
 with ProcessPoolExecutor(max_workers=a.workers) as pool:
  for f in as_completed([pool.submit(run,t) for t in tasks]):print(f.result(),flush=True)
