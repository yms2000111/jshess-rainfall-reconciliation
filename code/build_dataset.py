from common import *
import numpy as np,pandas as pd,json
from scipy.optimize import isotonic_regression
OUT=ROOT/'data/processed';OUT.mkdir(exist_ok=True)
def build(positive_part=False):
 audit=json.loads((ROOT/'data/packing_audit/summary.json').read_text());assert audit['all_passed'] and audit['files']==53
 files=sorted((ROOT/'data/ecmwf').glob('*.npz'));assert len(files)==53
 agfiles=sorted((ROOT/'data/agcd').glob('*.npz'));assert len(agfiles)==21
 obs=[]
 for f in agfiles:
  d=np.load(f);obs.append(pd.DataFrame({k:d[k] for k in REGIONS},index=pd.to_datetime(d['time']).normalize()))
 daily=pd.concat(obs).sort_index();assert not daily.index.duplicated().any();daily.to_csv(OUT/'agcd_daily_regional_mm.csv',index_label='date')
 rmm=pd.read_csv(ROOT/'data/support/rmm_full.txt',sep=r'\s+',skiprows=2,header=None,usecols=range(7),names=['year','month','day','rmm1','rmm2','phase','amp'])
 rmm.index=pd.to_datetime(rmm[['year','month','day']]);rmm.loc[(abs(rmm.rmm1)>100)|(abs(rmm.rmm2)>100),['rmm1','rmm2']]=np.nan
 enso=pd.read_csv(ROOT/'data/support/nino34.txt',sep=r'\s+')
 enso.index=pd.to_datetime(dict(year=enso.YR,month=enso.MON,day=1))
 times=[];regraw={k:[] for k in REGIONS};regqc={k:[] for k in REGIONS};nrestore=0;negative=0;min_week=0.;max_repair=0.
 for f in files:
  d=np.load(f);meta=json.loads(f.with_suffix('.json').read_text());a=d['cumulative'].astype(float);missing=np.isnan(a);nrestore+=int(missing.sum())
  fill=meta['fill']*meta['scale']+meta['add'];a[missing]=max(fill,0)
  assert a.min()>=-1e-5
  for key,r in REGIONS.items():
   iy=np.isin(d['lat'],r['centres_lat']);ix=np.isin(d['lon'],r['centres_lon'])
   weights=np.broadcast_to(np.cos(np.deg2rad(d['lat'][iy]))[:,None],(2,2)).copy();weights/=weights.sum()
   sub=a[:,:,:,iy,:][:,:,:,:,ix];cum=(sub*weights).sum(axis=(-2,-1))
   week=np.diff(cum,axis=2,prepend=np.zeros_like(cum[:,:,:1]));negative+=int((week<-1e-4).sum());min_week=min(min_week,float(week.min()))
   regqc[key].append(np.maximum(-week,0).max((1,2)))
   # Preserve the archived day-28 total. Project earlier cumulative values onto
   # the monotone cone bounded by zero and that total. This is a QC convention,
   # not a reconstruction of precipitation lost at the IFS resolution transition.
   fixed=cum.copy()
   for iy0,im in np.argwhere((week<0).any(2)):
    fixed[iy0,im,:3]=np.clip(isotonic_regression(cum[iy0,im,:3]).x,0,cum[iy0,im,3])
   max_repair=max(max_repair,float(np.abs(fixed-cum).max()))
   week=np.maximum(week,0) if positive_part else np.diff(fixed,axis=2,prepend=np.zeros_like(fixed[:,:,:1]));assert week.min()>-1e-8
   regraw[key].append(np.concatenate([week,week.sum(axis=2,keepdims=True)],axis=2))
  times.extend(d['times'].astype('datetime64[s]').astype('datetime64[D]'))
 times=pd.DatetimeIndex(times);order=np.argsort(times);times=times[order];assert not times.duplicated().any()
 feats=rmm.reindex(times-pd.Timedelta(days=2))[['rmm1','rmm2']].values
 enso_dates=times.to_period('M').to_timestamp()-pd.DateOffset(months=2)
 sst=enso.reindex(enso_dates)['NINO3.4'].to_numpy();enso_anom=enso.reindex(enso_dates)['ANOM.3'].to_numpy();feat=np.column_stack([feats,sst]);assert np.isfinite(feat).all()
 for key,r in REGIONS.items():
  raw=np.concatenate(regraw[key],axis=0)[order]
  target=[]
  for shift in [-1,0,1]:
   w=[]
   for start in times:
    vals=daily[key].reindex(pd.date_range(start+pd.Timedelta(days=1+shift),periods=28)).values
    weeks=vals.reshape(4,7).sum(axis=1);w.append(np.r_[weeks,weeks.sum()])
   target.append(np.array(w))
  np.savez_compressed(OUT/f'{key}.npz',dates=times.values,raw=raw,y=target[1],y_shift_minus=target[0],y_shift_plus=target[2],climate=feat,enso_anom=enso_anom,qc_max_decrease=np.concatenate(regqc[key])[order],rmm_phase=rmm.reindex(times-pd.Timedelta(days=2)).phase.values)
 report=dict(origins=len(times),first=str(times.min()),last=str(times.max()),restored_values_in_australian_rectangle=nrestore,negative_regional_week_totals=negative,minimum_week_before_qc_mm=min_week,maximum_cumulative_adjustment_mm=max_repair,qc='isotonic cumulative endpoints with day-28 total fixed',dates_files=len(files),observed_year_files=len(agfiles))
 (OUT/'sample_manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(report)
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--positive-part',action='store_true');args=parser.parse_args()
 if args.positive_part:OUT=ROOT/'data/processed_positive_part';OUT.mkdir(exist_ok=True)
 build(args.positive_part)
