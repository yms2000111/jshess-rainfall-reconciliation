from common import *
import pypdfium2 as pdfium
from PIL import Image,ImageOps,ImageDraw
import sys
name=sys.argv[1] if len(sys.argv)>1 else 'JSHESS_reading'
qa=ROOT/'_qa'/name;qa.mkdir(exist_ok=True);pdf=pdfium.PdfDocument(str(ROOT/'_qa'/f'{name}.pdf'))
print('Pages:',len(pdf))
for i in range(len(pdf)):
 page=pdf[i];im=page.render(scale=1.6).to_pil();im.save(qa/f'page-{i+1}.png');tx=page.get_textpage().get_text_range();print(i+1,len(tx),tx[:70].replace('\r\n',' '))
# Contact sheets are a quick overview; individual page PNGs are retained for QA.
for start in range(0,len(pdf),6):
 sheet=Image.new('RGB',(1530,2040),'#dddddd');draw=ImageDraw.Draw(sheet)
 for j,i in enumerate(range(start,min(start+6,len(pdf)))):
  im=Image.open(qa/f'page-{i+1}.png');im.thumbnail((490,980));x=(j%3)*510+10;y=(j//3)*1020+25;sheet.paste(im,(x,y));draw.text((x,y-18),f'Page {i+1}',fill='black')
 sheet.save(qa/f'contact-{start+1}.png')
