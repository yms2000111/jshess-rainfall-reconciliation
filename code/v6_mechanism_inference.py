"""Descriptive paired annual inference and replication checks for V6 ablations."""
from common import ROOT
import numpy as np,pandas as pd,json
R=ROOT/'revision/review_v6/mechanism'
a=pd.read_csv(R/'annual_scores.csv').query('lead=="D28"');keys=['N','NE','SE','SW','NW','CA','EC','TAS'];rows=[];audit=[]
for system,ny in [('ECMWF',20),('ACCESS',19)]:
    d=a.query('system==@system');assert len(d)==8*ny*11
    ix=np.random.default_rng(2026102602+ny).integers(0,ny,(50000,ny))
    contrasts={
      'H2 minus H1, own W':{'H2_own':1,'H1_own':-1},
      'H2 minus H1, fixed H0 W':{'H2_fixedH0':1,'H1_fixedH0':-1},
      'Hweekly minus H1, own W':{'Hweekly_own':1,'H1_own':-1},
      'Hweekly minus H1, fixed H0 W':{'Hweekly_fixedH0':1,'H1_fixedH0':-1},
      'Score interaction, own W':{'H2_own':1,'Hweekly_own':-1,'H1_own':-1,'H0_own':1},
      'Score interaction, fixed H0 W':{'H2_fixedH0':1,'Hweekly_fixedH0':-1,'H1_fixedH0':-1,'H0_fixedH0':1},
      'H1 minus BU-rain, own W':{'H1_own':1,'BUrain':-1},
      'H1 minus raw, own W':{'H1_own':1,'Raw':-1},
      'H1 minus BU-clim, own W':{'H1_own':1,'BUclim':-1}}
    for label,coef in contrasts.items():
        seq=[]
        for k in keys:
            t=d.query('domain==@k').pivot(index='year',columns='method',values='crps').sort_index()
            seq.append(100*sum(v*t[m] for m,v in coef.items()).values/t.Raw.mean())
        seq=np.array(seq);delta=seq.mean(0);lo,hi=np.quantile(delta[ix].mean(1),[.025,.975])
        rows.append(dict(system=system,contrast=label,delta=delta.mean(),lower=lo,upper=hi,negative_domains=int((seq.mean(1)<0).sum())))
    if system=='ACCESS':old=pd.read_csv(ROOT/'revision/review_v5/access_s2/annual_scores.csv')
    else:old=pd.concat([pd.read_csv(ROOT/'revision/review_v4/adaptive/annual_scores.csv').query('validation=="LOYO" and domain in ["N","NE","SE","SW"]'),pd.read_csv(ROOT/'revision/review_v4/coverage/annual_scores.csv')])
    for new,legacy in [('Raw','Raw'),('BUrain','Bottom_up'),('BUclim','Weekly_climate_BU'),('H0_own','H0'),('H1_own','H1')]:
        x=d.query('method==@new').set_index(['domain','year']).crps
        y=old.query('lead=="D28" and method==@legacy').set_index(['domain','year']).crps
        err=float((x-y.reindex(x.index)).abs().max());audit.append(dict(system=system,method=new,max_abs_score_difference=err))
        # Earlier H1 paths fit equivalent climate objectives independently.
        # Require agreement far below the manuscript's 0.001 mm precision.
        assert err<1e-4,(system,new,err)
pd.DataFrame(rows).to_csv(R/'contrasts.csv',index=False)
a.groupby(['system','domain','method']).crps.mean().unstack().to_csv(R/'domain_scores.csv')
(R/'replication_audit.json').write_text(json.dumps(audit,indent=2))
print(pd.DataFrame(rows).to_string(index=False));print('Archived baseline score replication passed.')
