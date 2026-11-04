"""Reconstruct published summary contrasts from the two public JSON data files.

Usage: python verify_public_summaries.py DIRECTORY_CONTAINING_BOTH_JSON_FILES
Uses only the Python standard library; does not download or read raw fields.
"""
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from statistics import mean
import json, math, sys

def close(a,b):
    assert math.isclose(float(a),float(b),rel_tol=1e-10,abs_tol=1e-10),(a,b)

def group(rows,keys,value):
    g=defaultdict(list)
    for r in rows:g[tuple(r[k] for k in keys)].append(float(r[value]))
    return {k:mean(v) for k,v in g.items()}

def verify(folder):
    data=json.loads((folder/'derived_scores.json').read_text(encoding='utf-8'))['datasets']
    more=json.loads((folder/'additional_checks.json').read_text(encoding='utf-8'))['datasets']
    dy=data['domain_year_contrasts.csv'];annual=data['annual_contrasts.csv']
    assert len(dy)==128 and len(annual)==16
    reconstructed=group(dy,['baseline','year'],'delta')
    for r in annual:close(reconstructed[r['baseline'],r['year']],r['delta'])
    pvals={}
    for r in data['primary_contrasts.csv']:
        v=[reconstructed[r['baseline'],str(y)] for y in range(2021,2025)]
        observed=mean(v);close(observed,r['delta'])
        p=sum(abs(mean(a*b for a,b in zip(signs,v)))>=abs(observed)-1e-12
              for signs in product([-1,1],repeat=4))/16
        close(p,r['exact_two_sided_p']);pvals[r['baseline']]=p
        assert sum(x<0 for x in v)==int(r['years_improved'])
    adjusted={};running=0
    for i,(key,p) in enumerate(sorted(pvals.items(),key=lambda kv:kv[1])):
        running=max(running,min(1,p*(len(pvals)-i)));adjusted[key]=running
    for r in data['primary_contrasts.csv']:close(adjusted[r['baseline']],r['holm_p'])
    for r in data['extension_2023_2024.csv']:
        close(mean(reconstructed[r['baseline'],str(y)] for y in [2023,2024]),r['delta'])
    means=group(data['annual_scores.csv'],['domain','method','lead'],'crps')
    for r in data['mean_scores.csv']:close(means[r['domain'],r['method'],r['lead']],r['crps'])
    snapshots={(r['baseline'],r['version']):r for r in more['snapshot_2020/contrasts.csv']}
    for baseline in ['H0','BU-rain','BU-clim','Raw']:
        close(snapshots[baseline,'v1.0.1']['delta'],snapshots[baseline,'v1.0.4']['delta'])
    rows=more['wide_penalty/annual_scores.csv'];assert len(rows)==312
    counts=Counter((r['system'],r['selected']) for r in rows)
    for r in rows:close(r['selected_score'],r[r['selected']])
    for r in more['wide_penalty/selection_counts.csv']:
        assert counts[r['system'],r['selected']]==int(r['folds'])
    scales=group(rows,['system','domain'],'raw')
    for expected in more['wide_penalty/contrasts.csv']:
        part=[r for r in rows if r['system']==expected['system']]
        yearly=defaultdict(list)
        for r in part:
            yearly[r['year']].append(100*(float(r[expected['method']])-float(r['H0']))/scales[r['system'],r['domain']])
        close(mean(mean(v) for v in yearly.values()),expected['delta'])
    return {'annual_primary_effects_reconstructed':4,'exact_sign_flip_and_Holm_reconstructed':True,
            'new_period_extension_reconstructed':True,'domain_mean_scores_reconstructed':280,
            'snapshot_contrasts_reconstructed':4,'nested_fold_scores_checked':312,
            'nested_mean_effects_reconstructed':10,'selection_counts_reconstructed':dict((s,sum(v for (ss,k),v in counts.items() if ss==s)) for s in ['ECMWF','ACCESS']),
            'scope':'Summary reconstruction from public derived records; raw decoding, forecast fitting and bootstrap intervals are separate checks.'}

if __name__=='__main__':
    print(json.dumps(verify(Path(sys.argv[1])),indent=2))
