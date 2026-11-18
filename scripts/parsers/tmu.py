import pdfplumber
from core import clean,num,make_record,put,metric

def parse(paths,year,source):
 assert year==2026
 records=[];sid=source('scores',1)
 with pdfplumber.open(paths['scores']) as doc:
  text=clean(doc.pages[0].extract_text());assert '2026年度入学試験実施状況' in text and '合格平均点' in text
  tables=doc.pages[0].extract_tables();assert len(tables)==2
  for table,schedule in zip(tables,['前期','後期']):
   assert len(table[0])==11;faculty=''
   for row in table[1:]:
    if not row[1]:continue
    if row[0]:faculty=clean(row[0])
    assert faculty.endswith('学部')
    r=make_record('tmu',faculty,clean(row[1]),'一般選抜'+schedule,year)
    r['note']='一般選抜の合格点と配点合計。合格者10名以下の区分は最高点・最低点を非公表。受験者数がないため実質倍率は算出しません。'
    for k,idx in [('full',10),('maximum',7),('minimum',8),('average',9)]:
     value=num(row[idx]);put(r['total'],k,value,sid)
     if value is None:r['total'][k]=metric(None,sid,'合格者10名以下のため最高・最低点は非公表。',status='unavailable')
    for k,idx in [('capacity',2),('applicants',3),('accepted',5)]:put(r['admissions'],k,num(row[idx]),sid)
    g=r['admissions'];g['applicationRatio']=metric(round(g['applicants']['value']/g['capacity']['value'],4),sid,kind='calculated')
    records.append(r)
 assert len(records)==48
 return records
