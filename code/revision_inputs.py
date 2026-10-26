"""Retain untouched endpoint differences and positive-part alternatives."""
from common import ROOT,REGIONS
import numpy as np,pandas as pd,json
out=ROOT/'revision';out.mkdir(exist_ok=True)
times=[];arrays={k:[] for k in REGIONS}
for path in sorted((ROOT/'data/ecmwf').glob('*.npz')):
 d=np.load(path);meta=json.loads(path.with_suffix('.json').read_text());a=d['cumulative'].astype(float)
 a[np.isnan(a)]=max(meta['fill']*meta['scale']+meta['add'],0)
 for k,r in REGIONS.items():
  iy=np.isin(d['lat'],r['centres_lat']);ix=np.isin(d['lon'],r['centres_lon'])
  w=np.broadcast_to(np.cos(np.deg2rad(d['lat'][iy]))[:,None],(2,2)).copy();w/=w.sum()
  cum=(a[:,:,:,iy,:][:,:,:,:,ix]*w).sum((-2,-1));week=np.diff(cum,axis=2,prepend=np.zeros_like(cum[:,:,:1]))
  arrays[k].append(np.concatenate([week,cum[:,:,-1:]],2))
 times.extend(d['times'].astype('datetime64[s]').astype('datetime64[D]'))
dates=pd.DatetimeIndex(times);order=np.argsort(dates);rows=[]
for k in REGIONS:
 raw=np.concatenate(arrays[k])[order];reference=np.load(ROOT/f'data/processed/{k}.npz')
 assert np.array_equal(dates.values[order].astype('datetime64[D]'),reference['dates'].astype('datetime64[D]'))
 assert np.allclose(raw[:,:,4],reference['raw'][:,:,4])
 np.savez_compressed(out/f'raw_signed_{k}.npz',raw=raw)
 positive=np.maximum(raw[:,:,:4],0);positive=np.concatenate([positive,positive.sum(2,keepdims=True)],2)
 np.savez_compressed(out/f'raw_positive_{k}.npz',raw=positive)
 for j in range(4):
  values=raw[:,:,j];bad=values< -1e-4
  rows.append(dict(domain=k,week=j+1,n=values.size,negative=int(bad.sum()),percent=bad.mean()*100,minimum_mm=values.min(),mean_negative_mm=values[bad].mean() if bad.any() else 0,total_removed_mm=np.maximum(-values,0).sum()))
pd.DataFrame(rows).to_csv(out/'qc_by_week.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
