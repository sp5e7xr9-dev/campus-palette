import pdfplumber
from core import clean,num,make_record,put

def parse(paths,year,source):
 records=[];sid=source('scores',1)
 with pdfplumber.open(paths['scores']) as doc:
  text=clean(doc.pages[0].extract_text());assert '帯広畜産大学一般選抜合格者成績' in text
  table=doc.pages[0].extract_tables()[0];assert len(table[0])==10;current=None
  for row in table[2:]:
   if row[0]:current=int(row[0])+2018
   if current!=year:continue
   for offset,schedule in [(2,'前期'),(6,'後期')]:
    r=make_record('obihiro','畜産学部',clean(row[1]),'一般選抜'+schedule,year)
    r['note']='大学の年度別総合点。最低点・平均点には追加合格者を含みません。2025年度に配点変更あり。'
    for key,i in zip(['full','maximum','minimum','average'],range(offset,offset+4)):
     v=num(row[i]);assert v is not None;put(r['total'],key,v,sid)
    records.append(r)
 assert len(records)==4
 return records
