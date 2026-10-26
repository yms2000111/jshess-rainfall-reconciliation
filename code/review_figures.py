"""Regenerate figures with hollow squares and complete visible data ranges."""
from pathlib import Path
from common import ROOT

source=(ROOT/'code/final_figures.py').read_text(encoding='utf-8')
source=source.replace("F=ROOT/'revision/final_figures';F.mkdir(exist_ok=True)","F=ROOT/'revision/review_v3/figures';F.mkdir(exist_ok=True)")
source=source.replace("MARK={'Raw':'o','Bottom_up':'s','H0_7_NN':'^','H1_7_NN':'D','H1_Direct':'v'}","MARK={k:'s' for k in COL}\nLS={'Raw':'-','Bottom_up':'--','H0_7_NN':'-.','H1_7_NN':':','H1_Direct':'-'}")
source=source.replace("lw=1.35,label=LAB[m]","lw=1.35,ls=LS[m],label=LAB[m]")
source=source.replace("marker='o'","marker='s'").replace("fmt='o'","fmt='s'").replace('fmt=mk',"fmt='s'")
source=source.replace("marker=symbols[r.season]","marker='s'")
source=source.replace("xlabel='Change (% of climate CRPS)'","xlabel='Change (% of\\nclimatological CRPS)'")
source=source.replace("ylim=(-.08,.62)","ylim=(min(S.query(\"lead in ['W1','W2','W3','W4'] and method in ['Raw','Bottom_up','H0_7_NN','H1_7_NN']\").crpss)-.025,.62)")
source=source.replace("ax.plot([15,100],[15,100]","ax.plot([0,100],[0,100]")
source=source.replace("xlim=(15,100),ylim=(15,100)","xlim=(0,100),ylim=(0,100)")
source=source.replace("xlabel='Predicted MSE gain (%)'","xlabel='Variance-based gain (%)'")
source=source.replace("+[plt.Line2D([],[],c='black',marker=mk,mfc='white',ls='',label=ss) for ss,mk in symbols.items()]",'')
source=source.replace("ax.set(xlim=(-5,25),ylim=(-7,25)","ax.set(xlim=(-5,25),ylim=(-7,25)")
start=source.index('# Hierarchy and experiment diagram')
end=source.index('fig,axs=four()\nbase=',start)
design='''# Hierarchy, full nested fit and held-out validation.
fig,axs=plt.subplots(3,1,figsize=(6.8,7.4),gridspec_kw={'height_ratios':[2.1,1.8,1.2]});fig.subplots_adjust(left=.10,right=.96,bottom=.08,top=.93,hspace=.65)
def box(ax,x,y,w,h,txt,fc):
 ax.add_patch(Rectangle((x,y),w,h,facecolor=fc,edgecolor='#666',lw=.8));ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=10.5)
ax=axs[0];ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');panel(ax,'a')
for i in range(4):box(ax,.04+i*.22,.02,.18,.20,f'Week {i+1}','#e7eef4')
box(ax,.12,.42,.27,.20,'Days 1 to 14','#e4eee8');box(ax,.59,.42,.27,.20,'Days 15 to 28','#e4eee8');box(ax,.35,.80,.29,.20,'Days 1 to 28','#f8e6d7')
for a,b in [((.13,.22),(.255,.42)),((.35,.22),(.255,.42)),((.57,.22),(.725,.42)),((.79,.22),(.725,.42)),((.255,.62),(.495,.80)),((.725,.62),(.495,.80))]:ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1})
ax.text(.99,.86,'H1 adds climate\\nto aggregates;\\nH0 uses rainfall',ha='right',va='top',fontsize=9.5,color='#9a4100')
ax=axs[1];ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');panel(ax,'b')
for x,y,txt in [(.01,.65,'Outer fitting years'),(.365,.65,'Five inner year blocks'),(.72,.65,'Held-out errors\\nand covariance W'),(.01,.04,'Fit marginals\\nand rank templates'),(.365,.04,'Reconcile\\nforecast samples'),(.72,.04,'Evaluate in the\\nouter held-out year')]:box(ax,x,y,.27,.30,txt,'#f6f6f6')
for a,b in [((.28,.8),(.365,.8)),((.635,.8),(.72,.8)),((.145,.65),(.145,.34)),((.28,.19),(.365,.19)),((.855,.65),(.50,.34)),((.635,.19),(.72,.19))]:ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1})
ax.text(.50,-.18,'Power-map fitting adds a further nested cross-fit',ha='center',va='center',fontsize=9.5)
ax=axs[2];panel(ax,'c');ax.set(xlim=(1999.5,2019.5),ylim=(-.1,1.65),yticks=[],xticks=[2000,2005,2010,2015,2019])
for yr in range(2000,2020):ax.add_patch(Rectangle((yr-.45,.25),.9,.65,fc='#e69f00' if yr==2010 else '#e8e8e8' if yr in [2009,2011] else '#a7c8e1',ec='white'))
ax.text(2004,1.14,'Permitted fitting years',ha='center',fontsize=10);ax.annotate('Held out',xy=(2010,.85),xytext=(2013.0,1.38),ha='center',fontsize=10,arrowprops={'arrowstyle':'->'});ax.set_xlabel('Origin year; adjacent years excluded');save(fig,'Fig02_design')

'''
source=source[:start]+design+source[end:]
source=source.replace("ax.plot([-5,25],[-5,25],':',c='.6',lw=1);", "ax.plot([-5,25],[-5,25],':',c='.6',lw=1);bias=-4.96 if col=='real_linear' else -5.21;slope=.12 if col=='real_linear' else .07;ax.text(.04,.94,f'Mean bias: {bias:.2f} pp\\nSlope: {slope:.2f}',transform=ax.transAxes,va='top',fontsize=10);")
exec(compile(source,'review_figures_source','exec'))

# Northern annual differences and leave-one-year influence are both descriptive.
d=pd.read_csv(ROOT/'revision/review_v3/annual_influence.csv').query("domain=='N'")
fig,axs=plt.subplots(2,1,figsize=(6.8,6.5));fig.subplots_adjust(left=.13,right=.97,bottom=.10,top=.84,hspace=.55)
for baseline,col,ls,label in [('Bottom_up','#0072B2','-','H1 minus bottom-up'),('H0_7_NN','#D55E00','--','H1 minus H0')]:
 q=d.query('baseline==@baseline').sort_values('year')
 axs[0].plot(q.year,q.annual_delta,marker='s',mfc='white',ms=5.5,c=col,ls=ls,label=label)
 axs[1].plot(q.year,q.mean_without_year,marker='s',mfc='white',ms=5.5,c=col,ls=ls)
for ax,l in zip(axs,'ab'):
 panel(ax,l);ax.axhline(0,c='.5',ls=':',lw=1);ax.set(xticks=[2000,2005,2010,2015,2019])
axs[0].set(ylabel='Annual CRPS change (mm)',xlabel='Validation year')
axs[1].set(ylabel='Mean without one year (mm)',xlabel='Omitted validation year')
fig.legend(*axs[0].get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.53,.98));save(fig,'Fig09_annual_influence')
print('Review figures saved with hollow square markers.')
