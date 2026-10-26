from common import ROOT,REGIONS
import json
REGIONS.update(json.loads((ROOT/'revision/review_v4/coverage/domains.json').read_text()))
import download_agcd as ag
source=(ROOT/'code/download_agcd.py').read_text(encoding='utf-8').replace("OUT=ROOT/'data/agcd'","OUT=ROOT/'revision/review_v5/operational'")
source=source.replace('dict(time=ds.time.values)','dict(time=ds.time.values[:28])').replace('ds.precip.sel(','ds.precip.isel(time=slice(0,28)).sel(')
exec(compile(source,'agcd_january_source','exec'),ag.__dict__)
ag.REGIONS=REGIONS
print(ag.year_task(2021),flush=True)
