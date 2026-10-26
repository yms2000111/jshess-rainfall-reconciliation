from common import *
import numpy as np,json
rows=[]
for f in sorted((ROOT/'data/ecmwf').glob('*.npz')):
 d=np.load(f);m=json.loads(f.with_suffix('.json').read_text());a=d['cumulative'].astype(float);a[np.isnan(a)]=m['fill']*m['scale']+m['add']
 for k,r in REGIONS.items():
  iy=np.isin(d['lat'],r['centres_lat']);ix=np.isin(d['lon'],r['centres_lon']);v=a[:,:,:,iy,:][:,:,:,:,ix].mean((-1,-2));w=np.diff(v,axis=2)
  idx=np.unravel_index(w.argmin(),w.shape)
  if w[idx]<-.1:
   y,mem,t=idx;rows.append(dict(file=f.name,region=k,year=int(y),member=int(mem),week=int(t+2),diff=float(w[idx]),cum=v[y,mem].tolist(),grid=a[y,mem,:,iy,:][:,:,ix].tolist(),date=str(d['times'][y].astype('datetime64[s]'))))
print(json.dumps(sorted(rows,key=lambda q:q['diff'])[:12],indent=2));(ROOT/'data/negative_audit.json').write_text(json.dumps(rows,indent=2))
p=ROOT/'data/grib_sample.bin';buf=p.read_bytes();pos=0;lengths=[]
while pos+16<len(buf):
 ln=int.from_bytes(buf[pos+8:pos+16],'big');lengths.append(ln);pos+=ln
print('GRIB message sizes',sorted(set(lengths)),lengths[:50])
