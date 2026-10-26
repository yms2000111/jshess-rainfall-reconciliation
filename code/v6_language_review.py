"""Claim-preserving editorial review using the installed GitHub writing skill."""
from common import ROOT
import re,json,hashlib
R=ROOT/'revision/review_v6';p=R/'manuscript.md';before=p.read_text(encoding='utf-8');s=before
changes={
'Climate predictors may improve rainfall calibration, but their value depends on where they enter a coherent forecast and which baseline is used.':'Climate predictors may improve rainfall calibration, but their value depends on the accumulation scale and the reference forecast.',
'We compare weekly, aggregate and all-node climate adjustments for subseasonal rainfall in eight Australian domains using nested ECMWF validation, ACCESS-S2 and a previously unused 2020 forecast period.':'We compare climate adjustments to weekly forecasts, longer accumulations and both using nested ECMWF validation in eight Australian domains, ACCESS-S2 and a previously unused 2020 forecast period.',
'Their 95% intervals are respectively':'The corresponding 95% intervals are',
'All-node deterioration persists under common covariance in both systems, while circulation describes the seasonal setting rather than a reliable gain predictor.':'Adjusting every node remains less effective under common covariance in both systems. Circulation diagnostics describe the seasonal setting but do not reliably predict gains.',
'Larger climate-fitting samples and stronger regularisation reduce the all-node penalty in both systems, consistent with unstable climate adjustments contributing to the differences. Temporal benefit remains uncertain.':'More climate-fitting years and stronger regularisation reduce this penalty in both systems, consistent with unstable climate adjustments contributing to the differences. Benefits in later forecast periods remain uncertain.',
'The open question here is where additional climate information should enter a rainfall hierarchy, and whether its apparent benefit survives comparison with simpler coherent forecasts.':'The question is where climate information should enter a rainfall hierarchy and whether it adds value beyond simpler coherent forecasts.',
'We isolate climate adjustments at weekly nodes, aggregate nodes or both, retaining raw forecasts, rainfall-only weekly sums and rainfall-only reconciliation.':'We apply climate adjustments to weekly forecasts, aggregate forecasts or both, and compare them with raw forecasts, rainfall-only weekly sums and rainfall-only reconciliation.',
'Common-covariance and conditional learning experiments separate information placement, reconciliation weights and climate-coefficient stability.':'Experiments with common covariance and different climate-fitting samples examine how information placement, reconciliation weights and coefficient stability contribute to the results.',
'The aim is to identify the added value and limits of information placement, rather than assume that more adjusted scales improve a forecast.':'The aim is to determine when adding climate information at different scales improves the forecast.',
'They are geographical supports, not official climate regions.':'These boxes define the areas over which rainfall is averaged; they are not official climate regions.',
'Both experiments are consistent with unstable climate adjustments contributing to the comparison.':'Both experiments support a contribution from unstable climate adjustments.',
'The main finding is a contrast between partial and comprehensive climate adjustment.':'Climate adjustment performs differently when applied to part of the hierarchy and to every node.',
'The pattern therefore involves the component distributions and their joint adjustment, rather than only different estimated weights.':'Differences in estimated weights therefore account for only part of the pattern; the component distributions also matter.',
'The conditional learning curves strengthen this interpretation: larger climate-fitting samples and stronger penalties reduce H2 deterioration in both systems.':'The conditional learning curves help explain this result. More climate-fitting years and stronger penalties reduce H2 deterioration in both systems.',
'Retaining rainfall-only components can therefore act as a statistical constraint on variable climate adjustments in these experiments. The tests do not isolate that contribution from changes in marginal bias and spread.':'These results are consistent with rainfall-only components constraining unstable climate adjustments. Changes in marginal bias and spread may also contribute.',
'Temporal transfer is less stable.':'Performance in later forecast periods is less consistent.',
'More climate-fitting years and stronger regularisation reduce the penalty in both systems, supporting an estimation-stability explanation. This does not establish a physical mechanism or select an operational penalty.':'More climate-fitting years and stronger regularisation reduce the penalty in both systems, supporting the role of estimation stability. A physical explanation and an operational choice of penalty require separate evidence.',
'The northern forward ordering and inconclusive 2020 test prevent a claim of stable temporal benefit.':'The northern forward comparison reverses the ranking, and the 2020 test leaves temporal benefit uncertain.',
}
applied=[]
for old,new in changes.items():
 if old in s:s=s.replace(old,new);applied.append({'before':old,'after':new})
assert re.findall(r'\d+(?:\.\d+)?',before)==re.findall(r'\d+(?:\.\d+)?',s),'Numerical sequence changed'
assert before.split('## References')[1]==s.split('## References')[1]
assert re.findall(r'\[\[EQ\d+\]\]',before)==re.findall(r'\[\[EQ\d+\]\]',s)
assert '\u2014' not in s
p.write_text(s,encoding='utf-8')
audit=dict(date='2026-10-26',skill='https://github.com/Zink-Liu/Academic-Writing-Humanizer/blob/main/SKILL.md',github_blob_sha='e54ad6eae8b8495d9f696f194b31d21a94715ade',review_type='Manual claim-level language and logic review using the GitHub skill, with deterministic numerical/reference/equation-preservation checks',changes=applied,abstract_words=len(s.split('## Abstract')[1].split('Keywords:')[0].split()),numbers_unchanged=True,references_unchanged=True,equations_unchanged=True,detector_status='Not tested; no external detector upload',before_sha256=hashlib.sha256(before.encode()).hexdigest(),after_sha256=hashlib.sha256(s.encode()).hexdigest())
(R/'language_review_20261026.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'edits':len(applied),'abstract_words':audit['abstract_words'],'numbers_references_equations':'unchanged'}))
