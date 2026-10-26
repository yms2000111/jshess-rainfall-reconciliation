from common import *
import truststore;truststore.inject_into_ssl()
import requests,numpy as np,json,concurrent.futures,io,time
import eccodes as ec
OUT=ROOT/'data/packing_audit';OUT.mkdir(exist_ok=True)
def audit(f):
 date=f.stem;dest=OUT/f'{date}.json'
 if dest.exists():return json.loads(dest.read_text())
 u=f'https://object-store.os-api.cci1.ecmwf.int/s2s-ai-challenge/data/training-input/0.3.0/grib/ecmwf-hindcast-tp-{date}.grib'
 r=requests.get(u,headers={'Range':'bytes=0-2097151'},timeout=90);r.raise_for_status()
 buf=r.content;meta=json.loads(f.with_suffix('.json').read_text());d=np.load(f)
 restored=meta['fill']*meta['scale']+meta['add'];records=[];offset=0
 while offset+16<=len(buf):
  assert buf[offset:offset+4]==b'GRIB'
  length=int.from_bytes(buf[offset+8:offset+16],'big')
  if offset+length>len(buf):break
  g=ec.codes_new_from_message(buf[offset:offset+length]);offset+=length
  step=int(ec.codes_get(g,'step'));date2=int(ec.codes_get(g,'dataDate'));member=int(ec.codes_get(g,'number'))
  if step in [168,336,504,672]:
   val=ec.codes_get_values(g).reshape(121,240)[66:91,74:105]
   ts=np.datetime64(f'{date2:08d}'[:4]+'-'+f'{date2:08d}'[4:6]+'-'+f'{date2:08d}'[6:])
   y=int(np.flatnonzero(d['times'].astype('datetime64[s]')==ts)[0]);k=[168,336,504,672].index(step)
   packed=d['cumulative'][y,member,k].astype(float);missing=np.isnan(packed);packed[missing]=restored
   err=float(np.max(np.abs(packed-val)))
   records.append(dict(step=step,member=member,date=date2,bitmap=int(ec.codes_get(g,'bitmapPresent')),missing_native=int(ec.codes_get(g,'numberOfMissing')),restored_count=int(missing.sum()),max_abs_error_mm=err))
  ec.codes_release(g)
 passed=len(records)>=4 and all(q['bitmap']==0 and q['missing_native']==0 and q['max_abs_error_mm']<=meta['scale']/2+0.0005 for q in records)
 report=dict(date=date,url=u,packed_fill_value_mm=restored,quantisation_step_mm=meta['scale'],passed=passed,records=records)
 dest.write_text(json.dumps(report,indent=2),encoding='utf-8');print(date,'PASS' if passed else 'FAIL',len(records),flush=True);return report
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as p:reports=list(p.map(audit,sorted((ROOT/'data/ecmwf').glob('*.npz'))))
assert len(reports)==53 and all(r['passed'] for r in reports)
(OUT/'summary.json').write_text(json.dumps(dict(files=len(reports),all_passed=True,max_quantisation_step_mm=max(q['quantisation_step_mm'] for q in reports),total_restored_values_checked=sum(x['restored_count'] for q in reports for x in q['records'])),indent=2))
