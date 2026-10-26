from common import ROOT
p=ROOT/'manuscript.md';s=p.read_text(encoding='utf-8');start=s.index('## Acknowledgements and use of AI');end=s.index('## References',start)
s=s[:start]+'''## Acknowledgements and use of AI

Data and geographical outlines were provided by ECMWF, the Australian Bureau of Meteorology, NCI, NOAA and Natural Earth, and OpenAI Codex assisted with literature retrieval, code development, data analysis, figure preparation and manuscript drafting.

'''+s[end:];p.write_text(s,encoding='utf-8')
