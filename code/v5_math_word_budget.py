"""Retain formula definitions within the verified JSHESS text/caption limit."""
from common import ROOT
R=ROOT/'revision/review_v5';p=R/'manuscript.md';text=p.read_text(encoding='utf-8');moved=[]
replacements={
'The same-period comparison separates part of the validation effect': 'On the same 2015–2019 period, cross-validation gives northern H1 18.073 mm and BU-clim 18.182 mm, both worse than raw ECMWF. Forward fitting increases their scores by 0.566 and 0.042 mm, respectively. Thus both period and validation design matter (Supplementary Table S15).',
'Within N, the four constituent forecast cells also differ:': 'Within N, H1-minus-BU-rain ranges from −1.259 to +0.044 mm across the four constituent cells, which are correlated spatial supports (Supplementary Table S13).',
'Northern H1 scores 14.672 mm, compared': 'Northern 2020 H1 scores 14.672 mm, BU-clim 14.980 mm and raw ECMWF 17.144 mm. EC and SW favour BU-clim. H2 improves on H1 in two domains. These domain comparisons are descriptive; Supplementary Table S25 retains every score.',
}
blocks=text.split('\n\n')
for i,b in enumerate(blocks):
 for prefix,new in replacements.items():
  if b.startswith(prefix) and b!=new:moved.append(b);blocks[i]=new
text='\n\n'.join(blocks)
old='In exploratory single-group fits, DMI scores 20.423 mm and MJO 20.671 mm. Neither is clearly better than full H1 in the paired comparisons. Niño3.4 is uncertain and SAM is adverse. These results were inspected after the full model and were not used to select its predictors. One-month monthly-index lags score 20.616 mm, differing from H1 by +0.070 mm (−0.254 to 0.416 mm).'
new='Exploratory single-index fits favour DMI and MJO in point estimates but do not establish superiority to full H1. Predictor and lag controls are retained in Supplementary Table S18; none was used to select the full model.'
if old in text:moved.append(old);text=text.replace(old,new)
p.write_text(text,encoding='utf-8')
if moved:
 p=R/'implementation_details.md';p.write_text(p.read_text(encoding='utf-8')+'\n\n### Companion detail retained with the formula clarification\n\n'+'\n\n'.join(moved)+'\n',encoding='utf-8')
print('Moved',len(moved),'supporting detail passages; all numerical records retained.')
