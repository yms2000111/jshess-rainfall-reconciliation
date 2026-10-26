from common import *
import numpy as np,json
for f in sorted((ROOT/'data/ecmwf').glob('*.npz'))[:4]:
 d=np.load(f);a=d['cumulative']
 print(f.name,'range',np.nanmin(a),np.nanmax(a),flush=True)
 for k,r in REGIONS.items():
  y=np.isin(d['lat'],r['centres_lat']);x=np.isin(d['lon'],r['centres_lon'])
  v=a[:,:,:,y,:][:,:,:,:,x]
  complete=np.isfinite(v).all(axis=(2,3,4)).sum(axis=1)
  print(k,'missing',np.isnan(v).mean(),'validmembers',complete.tolist(),flush=True)
