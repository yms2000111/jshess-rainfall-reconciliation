"""Focused V6 narrative; preserve equations and move supporting detail explicitly."""
from common import ROOT
import re,json
R=ROOT/'revision/review_v6';p=R/'manuscript.md'
original=p.read_text(encoding='utf-8')
if not (R/'manuscript_before_focus.md').exists():(R/'manuscript_before_focus.md').write_text(original,encoding='utf-8')
t=(R/'manuscript_before_focus.md').read_text(encoding='utf-8')
def section(start,end,value):
 global t
 a=t.index(start);b=t.index(end,a);t=t[:a]+value.strip()+'\n\n'+t[b:]

intro='''## 1 Introduction

Weekly rainfall forecasts support field operations, while longer accumulations inform planting and water management. Four weekly amounts and their 28-day total describe the same weather sequence and should agree when added. This property, temporal coherence, holds for each dynamical ensemble member but can be lost when accumulation scales are calibrated separately.

Bottom-up aggregation restores coherence by summing calibrated weekly samples. Temporal reconciliation instead combines those samples with direct forecasts of longer accumulations and adjusts the scales together. Both satisfy the accounting identity. Reconciliation adds value when aggregate forecasts supply useful information or help correct errors left by weekly summation. Whether that occurs depends on the component forecasts, not on coherence alone.

Temporal hierarchies and probabilistic reconciliation are established approaches (Athanasopoulos et al. 2017; Jeon et al. 2019; Panagiotelis et al. 2023; Girolimetto et al. 2024). Rainfall applications show mixed effects across basins and scales, and interactions with temporal dependence reconstruction (Jahangir and Quilty 2022; Bellier et al. 2023). The open question here is where additional climate information should enter a rainfall hierarchy, and whether its apparent benefit survives comparison with simpler coherent forecasts.

Australia provides contrasting rainfall settings. The northern wet season is influenced by the monsoon and Madden–Julian Oscillation (MJO), whereas southwestern rainfall is concentrated in cooler months. Relationships with El Niño–Southern Oscillation (ENSO), the Indian Ocean Dipole (IOD) and the Southern Annular Mode (SAM) vary with location and season (Risbey et al. 2009; Wheeler et al. 2009). Climate indices may help predict longer accumulations, but may also duplicate information already represented by the dynamical ensemble or improve weekly forecasts without direct aggregates.

Australian calibration and bridging studies already combine statistical and dynamical predictors, including daily rainfall reordering (Schepen et al. 2014, 2018). ACCESS-S2 and studies of rainy-season retreat, southwestern rainfall and moisture transport provide the forecasting context (Wedd et al. 2022; Cowan et al. 2024; Firth et al. 2024; Reid et al. 2024). Recent subseasonal machine-learning work further motivates comparison with strong calibrated baselines (Guan et al. 2026).

We isolate climate adjustments at weekly nodes, aggregate nodes or both, retaining raw forecasts, rainfall-only weekly sums and rainfall-only reconciliation. Eight-domain ECMWF validation is followed by an ACCESS-S2 check and a previously unused 2020 forecast period. A common-covariance experiment separates information placement from changes in reconciliation weights. These extensions follow earlier results and are identified as exploratory; the locally dated 2020 protocol precedes its scoring. The aim is to identify the added value and limits of information placement, rather than assume that more adjusted scales improve a forecast.
'''
section('## 1 Introduction','## 2 Data',intro)

data='''## 2 Data and experimental design

### 2.1 Domains and observations

Four fixed 3° by 3° domains represent northern, northeastern, southeastern and southwestern Australia (N, NE, SE and SW). An exploratory extension adds equally sized boxes in the western Kimberley (NW), central interior (CA), eastern coast (EC) and Tasmania (TAS), fixed before fitting and all retained (Table 1; Fig. 1). Each contains four archived 1.5° ECMWF cells. They are geographical supports with contrasting seasonality, not official or randomly sampled climate regions.

Verification uses 0.05° AGCD/AWAP version 1.0.1 daily rainfall from NCI (Australian Bureau of Meteorology 2023; Jones et al. 2009). Valid land cells receive exact domain-overlap and latitude-dependent area weights; forecast cells use the same bounds. AGCD totals end at 09:00 local time. For origin t, dates t + 1 through t + 28 are paired with UTC forecast accumulations, leaving a subdaily boundary offset of approximately half an hour to two hours depending on domain and daylight saving. Alternative daily pairings are retained. The late-2019 targets require 2020 observations, and the issued-2020 test requires observations through 28 January 2021.

### 2.2 Forecast archives and quality control

The ECMWF S2S AI Challenge archive contains 53 Thursday production dates in 2020, each with 20 corresponding hindcast dates during 2000–2019 and 11 members, giving 1060 origins per domain (ECMWF 2021; Vitart et al. 2017). These hindcasts use configurations associated with the production dates rather than systems operating in each verification year. Cumulative fields at days 7, 14, 21 and 28 yield four weeks, two nonoverlapping fortnights and a 28-day total, which is not a calendar month.

GRIB comparisons show that a NetCDF missing-value code also represents the lowest rainfall bin; each file's packing parameters restore it. Cumulative rainfall can decrease near the documented day-16 resolution transition (ECMWF 2026). In the primary domains, 4893/186560 member-week increments are negative, including 4070 in Week 3. Isotonic regression repairs the first three endpoints between zero and the archived day-28 total, which remains the accounting reference. Positive-part and signed-predictor refits assess sensitivity; the raw comparator is labelled ECMWF (QC) (Supplementary Table S1 and Note 5).

ACCESS-S2 research hindcasts supply nine members and 228 monthly first-day origins during 2000–2018 in every domain (Wedd et al. 2022; Australian Bureau of Meteorology, undated a). The first 28 daily fluxes are converted to millimetres, with exact cell-overlap averaging. Midpoint timestamps define UTC daily means; missing time-bound metadata are documented. Different origins, grids and ensemble sizes require within-system comparisons.

The separate issued-forecast test uses all 53 Thursday ECMWF origins in 2020 and members 0–10, fixed to match the hindcast ensemble size. Training origins and targets end by 31 December 2019; forecasts were saved before scoring. Revised indices and pooled 2020 hindcast configurations prevent interpreting this archived-period check as an exact reconstruction of historical operations.

### 2.3 Predictors and validation

RMM1 and RMM2 represent MJO state (Wheeler and Hendon 2004), alongside Niño3.4 sea surface temperature, DMI and station-based SAM (Marshall 2003). RMM is lagged two days and monthly indices two months. Every fitting sample supplies its own standardisation; the index set and lags are common across domains. Sources and archive revisions are documented in Supplementary Note 5. Independent monthly NCEP/NCAR 850 hPa winds and humidity provide physical context rather than fitting inputs (Kalnay et al. 1996; Supplementary Note 8).

Outer validation holds out each year and excludes its neighbours and all origins whose targets end in excluded years. ECMWF folds contain 897–954 training and 53 validation origins; ACCESS-S2 verifies twelve origins per fold. Five inner consecutive-year blocks, each with adjacent-year exclusions, provide held-out mean errors for covariance estimation. Parameters, standardisation, rank templates and climatology use only permitted fitting observations. Permitted years can lie on either side of the outer year, so forward verification is assessed separately. Dated plans distinguish original primary tests from later extensions (Fig. 2).
'''
section('## 2 Data','## 3 Forecast',data)

# Archive supporting text before shortening, with its original numerical detail.
detail=[]
for a,b in [('### 3.6 Extension inference','## 4 Results'),('### 4.5 Covariance','### 4.6'),('### 4.12 Monsoon','## 5 Discussion')]:
 detail.append(t[t.index(a):t.index(b,t.index(a))])
extra='## Supplementary Note 8 Supporting inference and physical diagnostics\n\n'+'\n\n'.join(detail)
extra=extra.replace('### 3.6 Extension inference and the frozen forecast test','### Additional inference conventions').replace('### 4.5 Covariance and upper-tail diagnostics','### Covariance and event-score diagnostics').replace('### 4.12 Monsoon circulation describes the seasonal setting','### Northern circulation context').replace('Fig. 7','Fig. S9').replace('Fig. 10','Fig. S10')
(R/'supporting_detail.md').write_text(extra,encoding='utf-8')
section('### 3.6 Extension inference','## 4 Results','')

results='''## 4 Results

### 4.1 Calibration provides a competitive but imperfect baseline

Monthly EMOS has Week-1 CRPSS of 0.49–0.55 across the primary domains, falling by Week 4 to 0.038 in N, 0.002 in NE, 0.022 in SE and −0.007 in SW (Fig. 3). Direct 28-day rainfall-only EMOS improves on raw ECMWF over the full cross-validation period in every domain, although the more flexible monthly model worsens the simpler seasonal score in NE by 0.24 mm (Table 2).

Before adding climate predictors, five-node reconciliation changes 28-day CRPS by −0.16% of climatological score (95% interval −0.35 to 0.03%) relative to BU-rain; none of its primary comparisons passes Holm adjustment. Adding fortnightly nodes within H1 changes the normalised score by only +0.003% (−0.159 to 0.160%), with absolute domain changes below 0.02 mm. Additional nodes alone therefore contribute little (Supplementary Table S3).

### 4.2 Eight-domain comparisons depend on the reference forecast

Across ECMWF domains, H1 changes 28-day CRPS by −5.824% of raw score relative to raw forecasts (95% interval −7.564 to −4.140%; Holm p = 0.00004), −0.781% relative to BU-rain (−1.418 to −0.258%; p = 0.01462), −1.046% relative to BU-clim (−1.501 to −0.606%; p = 0.00084), and −0.331% relative to H0 (−0.742 to 0.056%; p = 0.13023). Favourable domains number eight, six, eight and five, respectively (Table 6; Fig. 5; Supplementary Table S23).

Hweekly and H1 have similar scores: their difference is +0.025% (−0.212 to 0.260%). Both improve on BU-clim by about 1%, whereas H2 minus BU-clim spans zero and H2 is worse than H1 in every domain. Thus the pooled result does not identify aggregate-only climate adjustment as uniquely effective (Supplementary Table S22).

### 4.3 ACCESS-S2 reveals the weakness of weekly climate adjustment

ACCESS-S2 H1 minus BU-clim is −5.726% of raw score (95% interval −7.659 to −3.900%; Holm p = 0.00009). Yet BU-clim is worse than BU-rain in seven domains and worse than raw forecasts in NE, NW and EC. In NE, BU-rain, H1 and BU-clim score 17.806, 17.997 and 19.775 mm. Across all eight domains, H1 minus BU-rain is only −0.069% (descriptive interval −0.946 to 0.774%). Improvement over BU-clim is consequently insufficient evidence of a gain over simple calibrated summation (Supplementary Tables S24 and S28).

H1 minus H0 is +0.468% (−0.556 to 1.451%; Holm p = 0.440). Northern H0 improves on BU-rain by −0.759 mm, but H1 adds only −0.025 mm relative to H0, with an interval of −1.166 to 1.431 mm. That interval contains both zero and the ECMWF northern difference. The second system is informative about baseline weakness, but insufficient to establish either replication or absence of the northern climate increment (Table 6).

### 4.4 The northern signal accompanies changes in the predictive distribution

The original four-domain H1-minus-H0 test gives −0.31% of climatological score (95% interval −0.70 to 0.06%; Holm p = 0.268; Table 3). Northern CRPS falls by 0.372 mm, with most of the effect in December–February, when it falls from 47.69 to 46.14 mm. March–May instead worsens from 16.93 to 17.11 mm. The northern finding was selected for examination after these results and remains exploratory (Fig. 4; Supplementary Fig. S4).

In N, bottom-up summation widens the central 80% interval to 109.68 mm and produces 88.8% coverage. H1 narrows it to 101.29 mm with 84.1% coverage (Fig. 6; Table 4). Relative to BU-rain, both reliability CRPS and potential CRPS decrease, by 0.085 and 0.456 mm, respectively. The difference is therefore not solely a spread correction. Seasonal 90th-percentile exceedances account for 68/1060 origins (6.4%) and 20.7% of direct-total CRPS. Wet-season amounts dominate millimetre-valued losses; event and joint-trajectory diagnostics retain mixed rankings (Supplementary Tables S4 and S7).

### 4.5 Robustness checks identify concentration rather than a universal climate effect

H1 improves on BU-rain in fourteen northern years (Fig. 9). Five years account for 87.0% of the net difference. Across all 15504 five-year omissions, the retained difference ranges from −0.884 to −0.094 mm, with median −0.543 mm. Against H0, three omissions reverse the sign. These are score-sensitivity distributions, not confidence intervals or refits (Supplementary Table S14; Fig. S8). Multiyear blocks widen uncertainty, and four constituent northern grid cells give H1-minus-BU-rain effects from −1.259 to +0.044 mm (Supplementary Tables S10 and S13).

The northern direction persists under quality-control alternatives and matched-size dependence controls, although absolute calibration changes (Supplementary Tables S1, S2, S5 and S9). Of 99 joint year-block permutations, two beat the identity score, giving a one-sided Monte Carlo p of 0.030 under approximate year exchangeability. Intercept, individual-index and lag controls do not identify a stable causal pathway; DMI's favourable single-index score was inspected post hoc (Supplementary Tables S8 and S18).

### 4.6 Forward and new-period tests change the ordering

Northern 2015–2019 forward scores favour raw ECMWF (17.847 mm), followed by BU-clim (18.225), H1 (18.639), H0 (19.134) and BU-rain (19.282). Climate information helps within the calibrated system while every individual calibrated alternative remains worse than raw forecasts (Table 5). On those same years, cross-validation gives H1 18.073 mm and BU-clim 18.182 mm. Both period and validation design matter (Supplementary Tables S12 and S15; Fig. S7).

In 2020, H1 beats BU-clim in six domains but BU-rain in only N, NW and EC. The frozen pooled H1-minus-BU-clim contrast is −0.923% of training raw CRPS (95% four-origin block interval −2.555 to 0.413%); longer blocks also include zero (Fig. 8). The confirmation criterion is unmet, leaving insufficient information about transfer rather than demonstrating no effect. A post hoc normal approximation gives an 80%-power effect size of about 2.15%, conditional on within-year block variability. It cannot quantify interannual power (Supplementary Note 7 and Tables S25 and S27).

### 4.7 All-node deterioration persists with common reconciliation weights

With each configuration's own covariance, H2 minus H1 is +0.978% of raw CRPS in ECMWF and +5.536% in ACCESS-S2. Fixing all four configurations to H0's covariance reduces these differences to +0.757% (95% descriptive interval 0.389–1.116%) and +3.849% (2.779–5.019%), respectively. Re-estimated weights therefore influence the magnitude but do not fully account for H2's disadvantage (Supplementary Table S28; Fig. S11).

The score interaction asks whether adjusting the weeks changes the incremental effect of aggregate adjustment. It is defined as (H2 minus Hweekly) minus (H1 minus H0), with positive values indicating less favourable aggregate adjustment when weeks are already adjusted. Under common H0 weights it is +1.083% (0.845–1.363%) in ECMWF and +2.249% (1.561–3.316%) in ACCESS-S2. This cross-system pattern supports a statistical interaction in the sampled forecasts. It does not identify information-theoretic redundancy, overfitting or a physical cause. Hweekly minus H1 remains uncertain with common weights in both systems.
'''
section('## 4 Results','## 5 Discussion',results)

discussion='''## 5 Discussion

The main finding is a contrast between partial and comprehensive climate adjustment. H1 and Hweekly retain rainfall-only forecasts at one level, whereas H2 adjusts every node. In both systems, H2's disadvantage persists when reconciliation uses the same covariance. The pattern therefore involves the component distributions and their joint adjustment, rather than only different estimated weights. Retaining rainfall-only components may constrain unstable climate adjustments, but learning curves and regularisation experiments are needed to separate estimation noise from duplicated signals and altered dependence.

Baseline choice determines the practical meaning of this pattern. ECMWF H1 improves on raw forecasts and both summation baselines in retrospective pooling, but not clearly on H0. ACCESS-S2 H1 substantially improves on a weak BU-clim comparator while remaining close to BU-rain overall. The cross-system interaction does not establish that climate predictors provide a useful increment over rainfall-only reconciliation. The original primary comparisons, exploratory pooled tests and new covariance contrasts retain their separate evidential status (Table 7).

Temporal transfer is less stable. Northern forward scores favour BU-clim over H1 and raw ECMWF over both; the 2020 pooled interval also crosses zero. A single new forecast year supplies a temporal check without estimating interannual uncertainty. Additional untouched years would require a new externally timestamped protocol, matched member counts and explicit handling of model-version changes. The current public deposit cannot retrospectively supply that timestamp for the earlier test.

The physical setting helps interpret where large score differences arise. Northern summer has humid low-level westerlies and concentrated rainfall, consistent with MJO and rainy-season research (Wheeler et al. 2009; Cowan et al. 2024). However, the wind–gain correlation is −0.25 with an interval of −0.66 to 0.23. Circulation composites describe the wet-season background rather than predict reconciliation gains (Supplementary Table S26; Fig. S10). DMI's post hoc performance could reflect earlier or correlated ocean conditions; IOD events usually weaken with the summer monsoon (Australian Bureau of Meteorology, undated b).

Covariance-based theoretical gains are also optimistic in these fitted forecasts (Supplementary Note 8; Fig. S9). Linear minimum-trace theory does not guarantee improvements in CRPS after covariance estimation, nonnegative projection and temporal transfer. Results for particular autoregressive hierarchies do not resolve this application either (Neubauer and Filzmoser 2024). Dependence and power-map checks further show why dispersion changes should not automatically be interpreted as new predictive information (Supplementary Notes 1 and 2).

The evidence concerns eight geographical boxes and the sampled systems, not all Australia or the general usefulness of reconciliation. A practical comparison should retain raw forecasts, rainfall-only and climate-informed weekly sums, and rainfall-only reconciliation. More flexible mixtures and training-only selectors did not establish a consistently superior adaptive rule and remain supplementary (Notes 3 and 4). Any operational rule needs temporal verification against those simple alternatives.
'''
section('## 5 Discussion','## 6 Conclusions',discussion)
conclusion='''## 6 Conclusions

In eight-domain ECMWF cross-validation, aggregate climate adjustment with reconciliation improves on raw forecasts and both weekly-summation baselines, but not clearly on rainfall-only reconciliation. ACCESS-S2 also favours it over climate-informed summation, whose poor performance against simpler forecasts limits that comparison.

Adjusting every node is less effective than adjusting aggregates alone in both systems. This deterioration persists under a common covariance, showing that differences in estimated reconciliation weights are not its sole explanation. The result motivates tests of estimation noise and cross-scale information overlap without establishing either mechanism.

The northern forward ordering and inconclusive 2020 test prevent a claim of stable temporal benefit. Physical diagnostics describe the wet-season setting but do not identify a reliable predictor of gain. Climate information should therefore be evaluated at the scale where it is introduced, against raw and simple coherent forecasts, with temporal transfer assessed separately from retrospective agreement.
'''
section('## 6 Conclusions','## Data availability',conclusion)
section('## Data availability','## Conflicts of interest','''## Data availability

Analysis source and the versioned research snapshot are available at https://github.com/yms2000111/jshess-rainfall-reconciliation (release v0.1.0, commit 9605a8a5cd5a9c3f580a9d4a44afabb6510cc2bd). The snapshot includes processed regional inputs, score tables, metadata, mathematical audits and manuscript materials; its manifest records file hashes. Large fitting caches and global source archives are excluded and can be regenerated using the supplied scripts. Later revisions are identified separately. The public deposit dated 26 October 2026 is not evidence of prospective preregistration. ECMWF inputs come from the S2S AI Challenge archive, AGCD from NCI (https://doi.org/10.25914/hjqj-0x55), ACCESS-S2 from the NCI research catalogue and NCEP/NCAR reanalysis from NOAA PSL through IRI. Source licences and attribution continue to apply. Natural Earth supplies the public-domain outline.
''')
# Transfer detailed extension conventions to supplement while retaining essentials.
t=t.replace('### 3.5 Controls and transfer checks','### 3.5 Controls, transfer checks and common-covariance comparison')
pos=t.index('## 4 Results')
methods='''Eight-domain effects divide paired annual CRPS differences by each domain's raw score and average domains equally. Common-year bootstrap draws preserve cross-domain dependence. Four exploratory ECMWF comparisons form one Holm family; three ACCESS comparisons form a separate family. The 2020 denominator is frozen training raw CRPS, with common circular blocks of four weekly origins and a confirmation requirement that the entire 95% interval be negative. Supplementary Notes 7 and 8 give the full protocol and inference conventions.

The additional covariance ablation evaluates H0, H1, Hweekly and H2 with their own inner-fold covariance and, separately, one common H0 covariance within each outer fold. Marginal parameters, quantiles, templates and exclusions are unchanged. This holds the reconciliation metric fixed while varying information placement. All 312 system–domain–year combinations are retained; comparisons and score interactions are exploratory, with descriptive common-year intervals (Supplementary Note 9).

'''
t=t[:pos]+methods+t[pos:]
t=t.replace('Northern circulation composites describe the wet-season setting without identifying a reliable gain predictor.', 'All-node deterioration persists under common covariance in both systems, while circulation describes the seasonal setting rather than a reliable gain predictor.')
# Update main numbering to first-appearance order; move two diagnostics to supplement.
fm={1:1,2:2,3:3,5:4,4:5,6:6,9:7,8:8,7:'S9',10:'S10'}
tm={1:1,2:2,6:3,3:4,4:5,5:6,7:7}
t=re.sub(r'Fig\. (\d+)(?!\d)',lambda m:'Fig. '+str(fm[int(m[1])]),t)
t=re.sub(r'(?<!Supplementary )Table (\d+)(?!\d)',lambda m:'Table '+str(tm[int(m[1])]),t)
t=t.replace('They are geographical supports with contrasting seasonality, not official or randomly sampled climate regions.','They are geographical supports, not official climate regions.')
p.write_text(t,encoding='utf-8')
main=t[t.index('## 1 Introduction'):t.index('## Data availability')]
print('Main prose words:',len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b",main)))
print('Abstract words:',len(t.split('## Abstract')[1].split('Keywords:')[0].split()))
