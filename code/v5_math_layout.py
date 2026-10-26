"""Native Word equation-array layout for the canonical three-line Eqn 11."""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
def equation_array(key,equations,renderer,label):
 original=equations[key]
 assert original.startswith(r'\begin{gathered}') and original.endswith(r'\end{gathered}')
 lines=original.removeprefix(r'\begin{gathered}').removesuffix(r'\end{gathered}').split(r'\\')
 arr=OxmlElement('m:eqArr');pr=OxmlElement('m:eqArrPr');base=OxmlElement('m:baseJc');base.set(qn('m:val'),'center');pr.append(base);arr.append(pr)
 number=None
 try:
  for line in lines:
   equations[key]=line;part=renderer(key);math=part.find(qn('m:oMath'));number=math[-1];math.remove(number)
   row=OxmlElement('m:e')
   for child in list(math):row.append(child)
   arr.append(row)
 finally:equations[key]=original
 root=OxmlElement('m:oMath');root.append(arr)
 list(number.iter(qn('m:t')))[-1].text='\u2003('+str(label)+')';root.append(number)
 para=OxmlElement('m:oMathPara');para.append(root)
 assert len(arr.findall(qn('m:e')))==3
 return para
