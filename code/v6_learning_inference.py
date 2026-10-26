from common import ROOT
import numpy as np,pandas as pd,json
R=ROOT/'revision/review_v6';L=R/'learning'
a=pd.read_csv(L/'annual_scores.csv');base=pd.read_csv(R/'mechanism/annual_scores.csv').query('lead=="D28"');keys=['N','NE','SE','SW','NW','CA','EC','TAS']
rows=[];changes=[];coef=[]
for path in L.glob('*.json'):
 m=json.loads(path.read_text());
 for label,q in m['scenarios'].items():coef.append(dict(system=m['system'],domain=m['domain'],year=m['year'],scenario=label,years=len(q['years']),coefficient_norm=q['mean_coefficient_norm']))
pd.DataFrame(coef).to_csv(L/'coefficient_norms.csv',index=False)
for system,ny in [('ECMWF',20),('ACCESS',19)]:
 s=a.query('system==@system');assert len(s)==8*ny*5*4
 ix=np.random.default_rng(2026102604+ny).integers(0,ny,(50000,ny));seqs={}
 for scenario in ['years10','years15','full','ridge020','ridge050']:
  for contrast in ['H1 minus BU-clim','H2 minus H1','Score interaction']:
   seq=[]
   for k in keys:
    t=s.query('scenario==@scenario and domain==@k').pivot(index='year',columns='method',values='crps').sort_index();b=base.query('system==@system and domain==@k').pivot(index='year',columns='method',values='crps').sort_index()
    d=t.H1-t.BUclim if contrast=='H1 minus BU-clim' else t.H2-t.H1 if contrast=='H2 minus H1' else t.H2-t.Hweekly-t.H1+b.H0_fixedH0
    seq.append(100*d.values/b.Raw.mean())
   seq=np.array(seq).mean(0);seqs[(scenario,contrast)]=seq;lo,hi=np.quantile(seq[ix].mean(1),[.025,.975]);rows.append(dict(system=system,scenario=scenario,contrast=contrast,delta=seq.mean(),lower=lo,upper=hi))
 for scenario in ['years10','years15','ridge020','ridge050']:
  for contrast in ['H1 minus BU-clim','H2 minus H1','Score interaction']:
   delta=seqs[(scenario,contrast)]-seqs[('full',contrast)];lo,hi=np.quantile(delta[ix].mean(1),[.025,.975]);changes.append(dict(system=system,scenario=scenario,contrast=contrast,change_vs_full=delta.mean(),lower=lo,upper=hi))
pd.DataFrame(rows).to_csv(L/'contrasts.csv',index=False);pd.DataFrame(changes).to_csv(L/'changes_vs_full.csv',index=False)
print(pd.DataFrame(rows).query('contrast=="H2 minus H1"').to_string(index=False));print(pd.DataFrame(changes).query('contrast=="H2 minus H1"').to_string(index=False))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.labelsize':12,'axes.titlesize':15,'pdf.fonttype':42})
fig,axes=plt.subplots(2,2,figsize=(11.5,8.4));frame=pd.DataFrame(rows)
for col,system in enumerate(['ECMWF','ACCESS']):
 for row,scenarios,names in [(0,['years10','years15','full'],['10','15','All']), (1,['full','ridge020','ridge050'],['0.05','0.20','0.50'])]:
  ax=axes[row,col];sel=frame[(frame.system==system)&(frame.contrast=='H2 minus H1')].set_index('scenario').loc[scenarios]
  ax.errorbar(np.arange(3),sel.delta,yerr=[sel.delta-sel.lower,sel.upper-sel.delta],fmt='s-',color='#245782',mfc='white',mew=1.6,ms=8,capsize=5)
  ax.axhline(0,color='.45',ls='--',lw=1);ax.set_xticks(range(3),names);ax.set_xlim(-.3,2.3);ax.margins(y=.17);ax.grid(axis='y',alpha=.15);ax.spines[['top','right']].set_visible(False)
  ax.set_xlabel('Climate-fitting years' if row==0 else 'Climate penalty');ax.set_ylabel('H2 minus H1 (% of raw CRPS)');ax.set_title(system if system=='ECMWF' else 'ACCESS-S2',pad=15)
  ax.text(-.12,1.07,'('+chr(97+row*2+col)+')',transform=ax.transAxes,fontweight='bold',fontsize=16)
fig.subplots_adjust(left=.10,right=.98,bottom=.09,top=.91,hspace=.5,wspace=.30)
for ext in ['png','pdf','svg']:fig.savefig(R/'figures'/('FigS12_learning.'+ext),dpi=450)
plt.close(fig)
