"""Download fixed 2020 operational members, before any test scoring."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'code/download_ecmwf.py').read_text(encoding='utf-8')
source=source.replace("ROOT/'data/ecmwf'","ROOT/'revision/review_v5/operational/raw'")
source=source.replace('/data/training-input/','/data/test-input/').replace('ecmwf-hindcast-tp-','ecmwf-forecast-tp-')
source=source.replace("nmem,nyear,nlead,nlat,nlon=meta['shape']; leads=[7,14,21,28]","nmem,nyear,nlead,nlat,nlon=meta['shape']; assert nmem==51 and nyear==1; nmem=11; leads=[7,14,21,28]")
source=source.replace("members=meta['members'],leads=", "members=meta['members'][:11],leads=")
exec(compile(source,'operational_download_source','exec'))
