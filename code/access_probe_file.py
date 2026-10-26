from common import ROOT
import xarray as xr,truststore,json,requests
truststore.inject_into_ssl()
out=ROOT/'revision/review_v4/access_s2'
url='https://thredds.nci.org.au/thredds/dodsC/ux62/access-s2/hindcast/raw_model/atmos/pr/daily/e01/da_pr_20000101_e01.nc'
ds=xr.open_dataset(url,engine='pydap')
print(ds)
info=dict(url=url,attrs=ds.attrs,variables={k:dict(dims=v.dims,shape=v.shape,attrs=v.attrs,first=str(v.values.flat[0]) if v.size<2000 else '') for k,v in ds.variables.items()})
(out/'pilot_metadata.json').write_text(json.dumps(info,indent=2,default=str))
print(json.dumps(info,indent=2,default=str))
r=requests.get('https://thredds.nci.org.au/thredds/fileServer/ux62/access-s2/license.txt',timeout=40)
(out/'license.txt').write_text(r.text,encoding='utf-8');print('Licence:',r.text[:3500])
ds.close()
