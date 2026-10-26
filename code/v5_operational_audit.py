from common import ROOT
source=(ROOT/'code/audit_all_packing.py').read_text(encoding='utf-8')
source=source.replace("ROOT/'data/packing_audit'","ROOT/'revision/review_v5/operational/packing_audit'").replace("ROOT/'data/ecmwf'","ROOT/'revision/review_v5/operational/raw'")
source=source.replace('/data/training-input/','/data/test-input/').replace('ecmwf-hindcast-tp-','ecmwf-forecast-tp-')
source=source.replace('max_workers=6','max_workers=1')
exec(compile(source,'operational_packing_audit','exec'))
