from common import ROOT
import pandas as pd,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=ROOT/'revision/review_v6';F=R/'figures';F.mkdir(exist_ok=True)
a=pd.read_csv(R/'mechanism/contrasts.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.labelsize':13,'axes.titlesize':15,'pdf.fonttype':42,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,2,figsize=(12,5.3),sharey=True)
labels=['H2 minus H1','Hweekly minus H1','Score interaction']
for ax,system,letter in zip(axes,['ECMWF','ACCESS'],['a','b']):
 for mode,color,off in [('own W','#245782',-.12),('fixed H0 W','#ae4c25',.12)]:
  for i,label in enumerate(labels):
   r=a[(a.system==system)&(a.contrast==label+', '+mode)].iloc[0]
   ax.errorbar(r.delta,i+off,xerr=[[r.delta-r.lower],[r.upper-r.delta]],fmt='s',mfc='white',mec=color,mew=1.5,color=color,capsize=4,ms=7,label=mode if i==0 else None)
 ax.axvline(0,color='.4',lw=1,ls='--');ax.set_yticks(range(3),labels);ax.set_ylim(2.5,-.5);ax.set_xlabel('Change (% of raw CRPS)');ax.set_title('ACCESS-S2' if system=='ACCESS' else system,pad=17)
 ax.text(-.07,1.06,'('+letter+')',transform=ax.transAxes,fontweight='bold',fontsize=16);ax.grid(axis='x',alpha=.16);ax.spines[['top','right']].set_visible(False);ax.margins(x=.15)
handles,names=axes[0].get_legend_handles_labels()
fig.legend(handles,names,loc='lower center',bbox_to_anchor=(.59,.01),ncol=2,frameon=False,fontsize=12)
fig.subplots_adjust(left=.20,right=.98,wspace=.18,top=.83,bottom=.25)
for ext in ['png','pdf','svg']:fig.savefig(F/('FigS11_covariance_ablation.'+ext),dpi=450)
plt.close(fig)
