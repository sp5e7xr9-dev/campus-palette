import pdfplumber
from core import clean,num,make_record,put,metric

def parse(paths,year,source):
 records=[];sid=source('scores',1)
 with pdfplumber.open(paths['scores']) as doc:
  p=doc.pages[0];text=clean(p.extract_text());assert f'令和{year-2018}年度岩手大学' in text and '第1志望' in text
  table=p.extract_tables()[0];assert len(table[0])==12
  faculty='';labels=['']*3
  for row in table[2:]:
   if row[0]:faculty=clean(row[0]);labels=['']*3
   for i in range(3):
    if row[i+1] is not None:
     labels[i]=clean(row[i+1])
     for j in range(i+1,3):labels[j]=''
   for offset,schedule in [(4,'前期'),(8,'後期')]:
    if num(row[offset]) is None:continue
    r=make_record('iwate',faculty,''.join(labels), '一般選抜'+schedule,year)
    r['note']='第1志望の合格者のみの集計。第1志望合格者5名以下は最高点・最低点・平均点を非開示。総合点と内訳を混同しません。'
    for key,i in zip(['full','maximum','minimum','average'],range(offset,offset+4)):
     v=num(row[i]);put(r['total'],key,v,sid)
     if v is None:r['total'][key]=metric(None,sid,'第1志望合格者5名以下のため非開示。',status='unavailable')
    records.append(r)
 return records
