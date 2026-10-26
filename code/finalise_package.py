"""Supplementary material, reproducibility notes and transparent release contents."""
from common import *
import numpy as np,pandas as pd,json,zipfile,hashlib
from build_publication import document,paragraphs,table,OUT,Inches,Pt

# Replace the earlier independent-draw EMOS date scores with the final coupled product.
ds=pd.read_csv(ROOT/'results/date_sensitivity.csv');core=pd.read_csv(ROOT/'results/core_date_sensitivity.csv')
ds=ds[~ds.method.str.startswith('EMOS') & (ds.method!='CSG EMOS')];pd.concat([ds,core],ignore_index=True).to_csv(ROOT/'results/date_sensitivity.csv',index=False)
paired=pd.read_csv(ROOT/'results/paired_comparisons.csv');paired[paired.method!='CSG EMOS'].to_csv(ROOT/'results/paired_comparisons.csv',index=False)
S=pd.read_csv(ROOT/'results/scores.csv');rows=[];approx=[]
for k in REGIONS:
 for method in ['CSG EMOS','EMOS bottom-up','EMOS MinT-NN']:
  row=[k,method.replace('CSG EMOS','Direct EMOS').replace('EMOS ','')]
  for sh in [-1,0,1]:
   v=S.query("region==@k and method==@method and lead=='D28'").iloc[0].crps if sh==0 else core.query("region==@k and method==@method and lead=='D28' and shift_days==@sh").iloc[0].crps
   row.append(f'{v:.3f}')
  rows.append(row)
 exact=np.load(ROOT/f'results/{k}_emos_exact_crps.npy').mean(0)
 for j,lead in enumerate(['W1','W2','W3','W4','D28']):
  finite=S.query("region==@k and method=='CSG EMOS' and lead==@lead").iloc[0].crps;approx.append(dict(region=k,lead=lead,exact_crps=exact[j],quantile_crps=finite,difference=finite-exact[j]))
pd.DataFrame(approx).to_csv(ROOT/'results/emos_quantile_accuracy.csv',index=False)
doc=document();paragraphs(doc,'''# Supplementary material

## S1 Verification windows and numerical checks

Table S1 shifts the observed rainfall windows by one day in either direction while holding all fitted forecasts fixed. This diagnoses sensitivity to the daily pairing convention; the models are not refitted for the shifted observations. The unshifted column reproduces the manuscript's 28-day scores.

The file emos_quantile_accuracy.csv compares exact analytic EMOS CRPS with the 200-midpoint-quantile approximation for every region and scale. Reordering the quantiles preserves their marginal scores. Tests also compare the constrained full-covariance projection with independent nonnegative least squares, verify the diagonal numerical example, and compare the closed-form censored gamma CRPS with direct integration of the predictive cumulative distribution.
''')
table(doc,'Table S1. Observation-date sensitivity of 28-day CRPS (mm). Offsets refer to the daily observation labels; lower scores are better.',['Region','Method','−1 day','Primary','+1 day'],rows,[.6,1.85,1.45,1.45,1.45])
paragraphs(doc,'''## S2 Annual and climate-state diagnostics

Figure S1 shows year-to-year variation in weekly CRPSS. All forecasts use the same fixed fitting and calibration periods. The annual reference score is calculated from the same fitted seasonal-climatology distribution evaluated on that year's observations.

Figure S2 groups the 265 test origins by lagged MJO amplitude and Niño 3.4 anomaly. Weak and active MJO categories use amplitudes below one and at least one; cool, neutral and warm Niño 3.4 categories use −0.5°C and +0.5°C thresholds. The categories contain 101 weak, 164 active, 50 cool, 109 neutral and 106 warm origins. These descriptive means are not adjusted for season and do not identify causal climate effects. EMOS itself uses no climate-index predictors.

## S3 Secondary XGBoost experiments

The archived pooled-lead and no-index XGBoost forecasts assess modelling choices outside the main EMOS comparison. Diagonal nonnegative reconciliation reduces their main XGBoost 28-day CRPS by approximately 4.7%, 2.9%, 0.2% and 1.7% in N, NE, SE and SW. Weekly outcomes differ, and northern central 80% interval coverage falls from 78.5% to 64.2%. These results use joint calibration-residual sampling rather than the EMOS historical rank template.

The results_positive_part directory contains a separately refitted XGBoost experiment using zero-clipped negative weekly increments. Its reconciled-minus-base 28-day CRPS differences are approximately −0.88, −0.46, −0.02 and −0.13 mm. This sensitivity does not constitute a refit of the newly introduced EMOS reconciliation branch. The files robustness.csv and paired_comparisons.csv describe this secondary analysis and its moving-block resampling; core_comparisons.csv contains the main EMOS whole-year comparisons.

## S4 Reproducibility files

The processed regional inputs contain 1060 origins and eleven physical-model members per region. The final scores.csv contains 320 rows for sixteen methods, four domains and five accumulation scales. Every evaluated trajectory is retained in the regional predictions archives. Covariance matrices, shrinkage intensities, seasonal EMOS parameter estimates, model hyperparameters and source-file provenance are recorded separately. The README gives the required execution order and identifies which steps need network access.
''')
for name,caption in [('FigS01_annual_skill','Fig. S1. Annual weekly CRPSS relative to the fitted seasonal-climatology reference, by region and EMOS construction. Rows show direct, bottom-up and MinT-NN forecasts. Direct and bottom-up weekly values are identical. The colour scale is shared, with end triangles indicating values outside its displayed limits.'),('FigS02_climate','Fig. S2. Mean 28-day CRPS change from direct EMOS to MinT-NN within broad climate states. Negative values indicate improvement. Open points show descriptive means; labels give origin counts. Weak/active describe lagged MJO amplitude and cool/neutral/warm describe lagged Niño 3.4 anomaly. All regions use the same vertical range.')]:
 p=doc.add_paragraph();p.paragraph_format.page_break_before=True;p.paragraph_format.keep_with_next=True;p.add_run().add_picture(str(ROOT/f'figures/{name}.png'),width=Inches(6.8));doc.add_paragraph(caption,style='Caption')
doc.save(OUT/'JSHESS_supplement.docx')
(OUT/'cover_letter.txt').write_text('''Dear Editor,

Please consider our Research Article, “Temporal coherence and probabilistic skill of subseasonal rainfall forecasts in four Australian regions”, for the Journal of Southern Hemisphere Earth Systems Science.

The paper evaluates an issue relevant to rainfall forecast services: separately calibrated weekly and four-week forecasts can give incompatible totals. Using ECMWF hindcasts and AGCD observations, we compare direct precipitation EMOS, bottom-up aggregation and nonnegative probabilistic reconciliation. The independent test shows that reconciliation slightly improves direct aggregate forecasts, but bottom-up aggregation remains better in two of four regions. Weekly outcomes and dependence sensitivities explain why exact consistency is not sufficient to select a forecast product.

The submission includes original figures, supplementary analyses and a reproducible Python workflow with source-data audits. Its focus on Australian subseasonal prediction and forecast verification fits the journal's weather and climate remit.

[Authors: add the corresponding author's details and confirm author approval, originality, exclusive submission, funding and competing interests before sending.]

Yours sincerely,
[Corresponding author]
''',encoding='utf-8')
readme='''# 澳大利亚次季节降水论文与复现代码

论文围绕一个问题：分别订正后的周与28天概率降水预报，在恢复时间一致性后，哪些尺度改善、哪些退化？主比较为直接EMOS、自底向上和完整协方差非负协调；XGBoost、MJO/ENSO分层为辅助分析。

## 最新文件

- `submission/JSHESS_reading.docx`：无行号阅读版。题目20磅、作者居中；一级标题16磅、二级标题14磅、左对齐；正文12磅、两端对齐。
- `submission/JSHESS_submission.docx`：内容相同，增加期刊要求的连续审稿行号。
- `submission/JSHESS_supplement.docx`：观测日期敏感性、年度技巧、气候分层和辅助实验。
- `latex/main.tex`：无行号LaTeX版本；`latex/review.tex`启用审稿行号。图件放在`latex/images`。
- `code/equations.py`：Word与LaTeX的8个公式共用的唯一表达式源。Word使用可编辑的原生数学对象。
- `submission/statement_of_importance.txt`：65词、3句话；`cover_letter.txt`为投稿信草稿。

正文及图表说明约4346词，摘要200词，20条参考文献；6幅正文图与2幅补充图均为真实计算结果，提供600 dpi PNG、矢量PDF和SVG。`manuscript_previous.md`与旧版生成脚本仅为本地历史，不在最新交付包中。

## 实际数据与结果

使用ECMWF公开S2S AI Challenge档案中2020年的53个周四生产日期文件；每个含2000—2019年的20个历史起报日期、11个成员。每区域共1060个起报日期，2015—2019年的265个用于独立检验。AGCD观测为0.05°日降水，读取2000—2020年。四个3°×3°验证框并非正式NRM气候区。

MinT-NN相对直接EMOS的28天CRPS降低约0.39%、1.64%、2.11%、0.03%；但东北和东南的自底向上方法更好，16个周尺度对比中13个变差。完整协方差并不普遍优于对角近似。正文报告这些实际结果，没有预设协调或机器学习必胜。

## 复现顺序

安装`requirements.txt`后，已有区域输入可直接运行：

```powershell
python code/test_methods.py
python code/analyse.py
python code/core_reconciliation.py
python code/diagnostics.py
python code/publication_figures.py
python code/revise_narrative.py
python code/build_publication.py
python code/finalise_package.py
```

`analyse.py`拟合全部边际基线；`core_reconciliation.py`使用冻结EMOS参数恢复相依结构并执行主比较，必须在前者之后运行。后续脚本生成图文。Word数学转换使用已安装Microsoft Office的`MML2OMML.XSL`，当前路径在`build_publication.py`开头；其他系统需提供等效XSL文件。数值分析与绘图不依赖Office。

从原始公开资料开始：依次运行`download_ecmwf.py`、`download_agcd.py`、`download_support.py`、`audit_all_packing.py`和`build_dataset.py`，再执行上述分析。下载支持跳过已完成文件。`build_dataset.py --positive-part`及`analyse.py --positive-part`用于另一种预处理；当前归档的替代预处理结果用于辅助XGBoost实验，不是EMOS主实验的替代拟合。

## 结果文件

| 文件 | 内容 |
| --- | --- |
| `data/processed/*.npz` | 区域观测、11成员预报、日期、气候指标和质量标记 |
| `data/ecmwf/*.json`、`data/agcd/*.json` | 下载来源、提取参数和哈希 |
| `data/packing_audit` | 全部53个生产文件的NetCDF/GRIB编码核对 |
| `results/scores.csv` | 16方法×4区域×5尺度，320行 |
| `results/core_comparisons.csv` | MinT-NN相对直接与自底向上EMOS的整年分块比较 |
| `results/core_date_sensitivity.csv` | 固定EMOS预报、观测日期前后移动一天的分数 |
| `results/emos_quantile_accuracy.csv` | 200分位点与精确解析EMOS CRPS的差异 |
| `results/*_covariance.json` | 完整协方差、收缩系数、线性投影负值比例 |
| `results/*_emos_fit.json` | 80组季节EMOS参数及收敛记录 |
| `results/*_predictions.npz` | 所有独立检验轨迹 |
| `results/paired_comparisons.csv`、`robustness.csv` | 辅助XGBoost实验，不是EMOS主比较 |

主分析保持第28天累计值，对较早累计端点施加单调约束，处理ECMWF已记录的累计降水跳变。代码使用周在前、总量在后的顺序；论文使用总量在前，两者通过行置换对应。协调在毫米空间进行，全部样本保持非负与精确加总。

GitHub插件已用于核实官方数据读取项目；本目录可整理为GitHub仓库，但尚未发布远程仓库。原始数据许可由提供方规定，随元数据保留，代码说明不替代数据许可。参考图片仅用于多面板布局，未复制其图像、数值或水印。

## 期刊与作者信息

已按JSHESS初投要求核对字数、摘要、Statement of importance、编号章节、参考文献、图表和声明位置。期刊允许初投格式自由；阅读版去掉行号，投稿版保留。作者姓名、单位、通信邮箱、资助、利益冲突和最终公开存档链接需填写真实信息。

- https://connectsci.au/es/pages/es-authors
- https://connectsci.au/DocumentLibrary/Tables-and-figures.pdf
- https://github.com/ecmwf-lab/climetlab-s2s-ai-challenge
- https://doi.org/10.25914/hjqj-0x55

LaTeX工程已用桌面编译器检查。Word使用隐藏的本机Word进程导出校样并逐页检查；`_qa`仅为本地检查文件。
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
req=ROOT/'requirements.txt';r=req.read_text();r+='\nlatex2mathml==3.81.1\nlxml\n' if 'latex2mathml' not in r else '';req.write_text(r)
print('Supplement, cover letter, README and score-file consistency updated.')
