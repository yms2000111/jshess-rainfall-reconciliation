from common import ROOT
import re
R=ROOT/'revision/review_v4';s=(R/'manuscript.md').read_text(encoding='utf-8')
start=s.index('Two archive issues affect these calculations.');end=s.index('### 2.3 Climate predictors',start)
access=s[s.index('The second-system check uses public ACCESS-S2',start):end]
s=s[:start]+'''Two archive issues require quality control. A NetCDF code marked as missing also represents the lowest rainfall bin. Comparison with the original GRIB at all four endpoints, for the first hindcast year and control member of every production file, confirms restoration using the file-specific packing scale and offset. The audit covers all 53 files, rather than every archived field.

Cumulative fields can also decrease near the day-16 resolution transition documented by ECMWF (2026). Of 186560 primary-domain member-week increments, 4893 are negative, including 4070 in Week 3. The largest decrease is 22.46 mm. Isotonic regression repairs the first three cumulative endpoints, bounded by zero and the archived day-28 total. The latter is retained as the accounting reference. Complete positive-part and signed-predictor refits assess sensitivity to this choice (Supplementary Table S1). The primary raw comparator is labelled ECMWF (QC).

'''+access+s[end:]
s=s.replace('Here Aⱼ is the mean absolute distance between component j and the observation; Bⱼₖ is the mean pairwise absolute distance between components j and k, including within-component pairs.','The A terms are mean absolute distances from each component to the observation; the B terms are mean pairwise absolute distances between components, including within-component pairs. Equation (13) applies to the marginal at each accumulation scale.')
start=s.index('The northern seasonal setting suggests');end=s.index('Annual concentration and forward',start)
s=s[:start]+'''The northern wet season offers plausible predictability from MJO-related rainfall occurrence and persistence (Wheeler et al. 2009; Cowan et al. 2024). The DMI-only result is harder to interpret: IOD events generally peak before summer and weaken with the monsoon (Australian Bureau of Meteorology, undated b), whereas the full-model gain is concentrated in summer. A two-month lag could retain information about an earlier ocean state or correlated climate conditions. The post hoc single-group comparisons establish neither that pathway nor an independent DMI effect.

'''+s[end:]
start=s.index('Dependence remains part of the comparison.');end=s.index('The geographical extension supports',start)
s=s[:start]+'''Dependence affects the competing distributions. Historical ranks produce broad northern BU-rain intervals, but the local H1-minus-H0 contrast persists under matched ECC. Absolute calibration and skill still depend on sample construction (Bellier et al. 2023). The supplementary power-map audit further shows why fitting and application populations must be matched before interpreting recalibration performance.

'''+s[end:]
needle='Supplementary Tables S19–S21 report every candidate, rolling period, probability score and decision curve.'
extra=''' In ACCESS-S2, constant pooling scores 20.342 mm and state pooling 21.245 mm, a difference of +0.903 mm (0.534–1.314 mm). The constant mixture improves on raw by −1.533 mm (−2.685 to −0.377 mm). Across the twelve ECMWF domain-by-rolling-period cases, state weights improve on constant weights in only two. These checks favour simple pooling over the tested state rule.

Decision value also depends on location and threshold. For the 100 mm event at cost/loss ratio 0.20, constant pooling has value 0.367 (0.167–0.529) in N and 0.169 (0.027–0.277) in NE; southern intervals include zero. State weights give similar values without a consistent advantage (Supplementary Fig. S5). These are idealised decisions against training-climatology actions, rather than measured agricultural benefits.'''
s=s.replace(needle,needle+extra)
s=s.replace('Index sources, retrieval records and checksums are included with the analysis package.','ACCESS-S2 research hindcasts are publicly distributed through the NCI ACCESS-S catalogue. Index sources, retrieval records, licences and checksums are included with the analysis package.')
(R/'manuscript.md').write_text(s,encoding='utf-8');print('Main prose',len(s.split('## 1 Introduction')[1].split('## References')[0].split()))
