from common import ROOT
import requests,truststore,numpy as np,json
truststore.inject_into_ssl()
from pydap.parsers.dds import dds_to_dataset
from pydap.handlers.dap import unpack_dap2_data,old_BytesReader
from pydap.parsers.das import parse_das
out=ROOT/'revision/review_v4/access_s2'
f=np.load(out/'20000101_e01.npz');iy=np.rint((f['lat']+89.72222222)/(5/9)).astype(int);ix=np.rint((f['lon']-5/12)/(5/6)).astype(int)
base='https://thredds.nci.org.au/thredds/dodsC/ux62/access-s2/hindcast/raw_model/atmos/pr/daily/e01/da_pr_20000101_e01.nc'
query=f'pr[0:1:27][{iy.min()}:1:{iy.max()}][{ix.min()}:1:{ix.max()}]'
s=requests.Session();r=s.get(base+'.dods',params=query,timeout=60);r.raise_for_status();dds,data=r.content.split(b'\nData:\n',1)
ds=dds_to_dataset(dds.decode());ds.data=unpack_dap2_data(old_BytesReader(data),ds)
print(dds.decode());print(type(ds['pr']),list(ds['pr'].keys()));print('time',np.asarray(ds['pr']['time'].data)[:3])
arr=np.asarray(ds['pr']['pr'].data);rain=(np.maximum(arr,0)*f['weights']).sum((1,2))*86400
assert np.allclose(rain,f['daily_mm'],rtol=1e-6)
das=s.get(base+'.das',timeout=60);das.raise_for_status();attrs=parse_das(das.text);print(attrs['pr']);print(attrs['time']);(out/'pilot_raw_attributes.json').write_text(json.dumps(attrs,indent=2,default=str))
print('Direct DAP extraction reproduces xarray pilot.')
