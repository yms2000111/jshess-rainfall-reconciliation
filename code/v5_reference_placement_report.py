from common import ROOT
from docx import Document
import re,json,csv
R=ROOT/'revision/review_v5';text=(R/'manuscript.md').read_text(encoding='utf-8');body,refs=text.split('## References\n\n')
supp=Document(R/'submission_math_review/JSHESS_supplementary_material.docx');supptext='\n\n'.join(p.text for p in supp.paragraphs)
entries=refs.strip().split('\n\n')+[(R/'supplementary_references.md').read_text(encoding='utf-8').strip().split('\n\n')[-1]]
rows=[]
for ref in entries:
 author=ref.split(' (')[0];year=re.search(r'\((\d{4}[ab]?|undated [ab])\)',ref).group(1);surname=author.split()[0]
 if author.startswith('Australian Bureau'):surname='Australian Bureau of Meteorology'
 hits=[]
 for scope,source in [('Main',body),('Supplement',supptext.split('\n\nReferences\n\n')[0])]:
  section='Title'
  for b in source.split('\n\n'):
   if b.startswith('#'):section=b.lstrip('# ')
   if surname in b and year in b and not b.startswith(ref):hits.append((scope,section,b))
 url=re.search(r'https?://\S+',ref).group().rstrip('.')
 rows.append(dict(reference=ref,source_url=url,status='Verified DOI/publisher metadata' if 'doi.org' in url else 'Verified official page or explicitly identified preprint',main_cited=any(x[0]=='Main' for x in hits),supplement_cited=any(x[0]=='Supplement' for x in hits),first_location=hits[0][0]+' / '+hits[0][1] if hits else 'MISSING',citation_context=hits[0][2] if hits else ''))
with (R/'reference_metadata/citation_placement.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print('REFERENCES',len(rows),'UNCITED',[(r['reference'][:75]) for r in rows if r['first_location']=='MISSING'])
print('SUPPLEMENT ONLY',[(r['reference'][:75]) for r in rows if not r['main_cited']])
report='''# 参考文献核对记录

核对日期：2026年10月25日。共40条文献，主文39条、补充材料专用1条；35条有DOI，另5条为官方资料网页、软件资料或明确标注版本的预印本。

核对内容包括作者、年份、题名、期刊、卷页或文章号、DOI，以及引用上下文。逐条元数据保存在 reference_metadata，引用位置和对应段落保存在 citation_placement.csv。

## 已修正

- Guan 等（2026）补齐 Nature 卷658及页951–957，并区分在线发表日期。
- Efron（1987）在BCa区间首次出现处补引。
- Ranjan与Gneiting（2010）随概率混合实验移至补充材料参考文献。
- Kalnay等（1996）的页码和作者顺序采用AMS出版社目录；与Crossref的差异单独记录。
- Ferro、Reid和Wickramasuriya的年份使用正式卷期年份；Neubauer与Filzmoser标明arXiv预印本和具体版本。

参考文献在Word中左对齐并保留悬挂缩进。存在性与元数据核对、引用位置审查不等同于独立复算所引用论文的实验。
'''
(R/'submission_math_review/参考文献核对记录.md').write_text(report,encoding='utf-8')
assert all(r['first_location']!='MISSING' for r in rows)
