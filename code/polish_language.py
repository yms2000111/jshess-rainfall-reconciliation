"""Apply reviewed editorial changes; preserve numerical and equation tokens."""
from pathlib import Path
import re
import json
import hashlib

root = Path(__file__).resolve().parents[1]
path = root / 'revision/manuscript_final.md'
source = path.read_text(encoding='utf-8')
backup = path.with_name('manuscript_before_language_edit.md')
if backup.exists():
    raise RuntimeError('Editorial snapshot already exists; review before rerunning.')

changes = [
('Separate calibration of weekly rainfall and longer accumulations can produce forecasts that do not add up.', 'Calibrating weekly rainfall and longer accumulations separately can produce forecasts whose amounts no longer add up.'),
('We test whether adding lagged climate indices to fortnightly and 28-day distributions improves on aggregation of unchanged weekly forecasts.', 'We test whether lagged climate indices improve fortnightly and 28-day distributions enough to outperform the sum of unchanged weekly forecasts.'),
('The results distinguish useful aggregate information from additional hierarchy structure: extra climate predictors can help locally, whereas extra aggregation constraints alone provide little average benefit.', 'Climate predictors provide a local benefit, whereas adding aggregation constraints alone has little average effect.'),
('The additional work in reconciliation is justified only if the direct aggregates contribute useful information beyond the calibrated weeks. This distinction motivates the present experiment.', 'The value of reconciliation therefore depends on what the direct aggregates contribute beyond the calibrated weeks. We examine that contribution here.'),
('These studies make clear that neither consistency nor a particular reconciliation formula establishes predictive value by itself.', 'These studies show that predictive value depends on the base forecasts and their dependence structure as well as the reconciliation method.'),
('They provide a physical reason to test climate predictors at longer accumulation scales, without assuming that an observed climate relationship supplies additional forecast skill.', 'These relationships motivate testing whether climate predictors add forecast skill at longer accumulation scales.'),
('The analysis separates three issues that can otherwise be conflated.', 'We assess the experiment in three steps.'),
('The contribution is an empirical test of these relationships in ECMWF subseasonal rainfall, supported by transparent archive checks and nested validation across twenty years.', 'Archive checks and nested validation across twenty years support this assessment of ECMWF subseasonal rainfall forecasts.'),
('These are geographical sampling domains, not official climate-region boundaries.', 'Their fixed geographical boundaries define sampling domains rather than official climate regions.'),
('Fixing that endpoint defines the accounting reference rather than demonstrating that it is error-free.', 'The archived endpoint serves as the accounting reference; its uncertainty remains part of the quality-control sensitivity analysis.'),
('The embargo prevents overlapping target windows and close temporal neighbours from entering the fit, but it does not make climate variability across distant years independent.', 'The embargo removes overlapping target windows and close temporal neighbours from the fit. Climate variability can still link more distant years.'),
('Its comparisons are reported as a second-stage experiment on the same archive, not as an independent replication.', 'It forms a second-stage experiment using the same archive.'),
('These fixed regularisation choices prevent the experiment from changing the forecast family or selecting predictor flexibility on the validation scores. They define one reproducible test of added climate information, rather than an unrestricted search for the best climate model.', 'The fixed regularisation settings keep the forecast family unchanged and specify predictor flexibility before validation. H1 therefore tests a defined climate adjustment within the existing forecast model.'),
('Merely summing the weekly forecasts to manufacture extra nodes would supply no independent base forecast for reconciliation.', 'Fitting the aggregates separately allows them to contribute information beyond sums of the weekly forecasts.'),
('An independent random permutation is not used as the principal dependence benchmark.', 'This matched comparison provides the principal dependence benchmark.'),
('That discrepancy can contain additional signal, calibration differences or estimation noise. A common dynamical source does not prove that it contains no signal, and a nonzero discrepancy does not prove that it is useful. The H0/H1 comparison tests this distinction empirically.', 'That discrepancy combines any additional signal with calibration differences and estimation noise. The H0/H1 comparison tests whether the added climate information makes it useful for prediction.'),
('These components describe changes in the distributional score; they do not uniquely attribute a change to a physical process.', 'These components describe how the distributional score changes; identifying the responsible physical processes requires further evidence.'),
('This tests the fitted variance explanation rather than assuming that its theoretical optimum carries over to estimated, constrained probabilistic forecasts.', 'The comparison tests how well the fitted variance relationships describe the gains realised by the constrained probabilistic forecasts.'),
('Thus the later weeks provide little additional discrimination relative to seasonal climatology, even though their distributions still contribute to the accumulated rainfall forecast.', 'The later weeks consequently have little skill relative to seasonal climatology, while still contributing to the accumulated rainfall distribution.'),
('The average favourable point estimate therefore represents a geographically uneven response rather than a generally established improvement.', 'The favourable average is driven mainly by N, with uncertain effects in the other domains.'),
('The weekly forecasts also show why a longer hierarchy should not be judged only at its top.', 'The weekly scores reveal how the adjustments affect the lower levels of the hierarchy.'),
('The northern aggregate gain therefore accompanies reduced overcoverage, rather than the severe undercoverage reported for the earlier XGBoost formulation.', 'The northern aggregate gain therefore accompanies a reduction in excessive coverage.'),
('These results provide some local agreement but do not establish a reliable rule for selecting reconciliation from the fitted covariance.', 'The covariance predictions agree with some local results, but their uncertainty limits their use in choosing a reconciliation method.'),
('The diagnostic is therefore informative about the assumptions behind the adjustment, rather than a substitute for out-of-fold verification.', 'Out-of-fold verification shows where these fitted error relationships carry through to forecast performance.'),
('Thus a larger hierarchy and a larger predictor set have different consequences. Neither should be interpreted as an automatic increase in useful information.', 'In this experiment, changing the predictor set matters more than increasing the number of hierarchy nodes.'),
('However, this experiment introduces the five predictors jointly and does not isolate their individual mechanisms. The summer improvement supports a local predictive relationship under the specified model; it does not demonstrate that reconciliation has recovered a particular mode of atmospheric predictability.', 'The summer improvement supports a local predictive relationship under the specified model. Because the five predictors enter jointly, their individual contributions and physical mechanisms remain unresolved.'),
('Several features delimit the practical conclusion.', 'Applying these findings to operational forecasts requires attention to the data and model settings.'),
('It does not establish an operational selection rule or an optimal predictor architecture.', 'Operational selection rules and alternative predictor models require separate validation.'),
('For the present forecast products, bottom-up aggregation remains a strong default reference; additional aggregate models should earn their place through local out-of-fold improvements in both scores and uncertainty diagnostics.', 'For these forecast products, bottom-up aggregation provides a strong reference. Additional aggregate models are useful when local out-of-fold scores and uncertainty diagnostics support their inclusion.'),
('Coherence provides a necessary accounting property for rainfall products at nested horizons.', 'Coherence ensures that rainfall amounts agree across nested forecast horizons.'),
]

edited = source
for old, new in changes:
    if edited.count(old) != 1:
        raise ValueError(f'Expected one occurrence: {old}')
    edited = edited.replace(old, new)

def numbers(text):
    return re.findall(r'(?<![A-Za-z])[-−+]?\d+(?:\.\d+)?', text)

assert numbers(source) == numbers(edited), 'Numeric tokens changed'
assert re.findall(r'\[\[EQ\d+\]\]', source) == re.findall(r'\[\[EQ\d+\]\]', edited)
assert '—' not in edited
backup.write_text(source, encoding='utf-8')
path.write_text(edited, encoding='utf-8')
abstract = edited.split('## Abstract\n\n')[1].split('\n\nKeywords:')[0]
audit = {
    'revision': 'Language R1',
    'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
    'edited_sha256': hashlib.sha256(edited.encode()).hexdigest(),
    'reviewed_replacements': len(changes),
    'word_count_method': 'Whitespace-delimited tokens',
    'abstract_words': len(abstract.split()),
    'numeric_tokens_unchanged': True,
    'equation_markers_unchanged': True,
    'detector_status': 'Not tested',
    'scope': 'Editorial revision; existing incomplete results and reference sections remain to be completed.',
    'skill': 'https://github.com/Zink-Liu/Academic-Writing-Humanizer',
}
path.with_name('language_edit_audit.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(audit, ensure_ascii=False, indent=2))
