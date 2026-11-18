import pdfplumber
from core import clean,num,make_record,put

def parse(paths,year,source):
 assert year==2026
 records=[];sid=source('scores',1)
 with pdfplumber.open(paths['scores']) as doc:
  p=doc.pages[0];assert '令和8年度入学試験統計資料(合格最低点)' in clean(p.extract_text())
  table=p.extract_tables()[0];assert len(table[0])==13;faculty=department=test=''
  for row in table[1:]:
   if row[0]:faculty=clean(row[0])
   if row[1]:department=clean(row[1])
   if '人間発達文化' in faculty:
    if row[2]:test=row[2]
    values=(row[3] or '').splitlines();tests=test.splitlines()
    items=[('前期'+clean(tests[n] if len(tests)==len(values) else ''.join(tests)),v,department) for n,v in enumerate(values)]
   else:
    items=[(s,row[idx] or '', '学類一括公表（コース別区分なし）') for s,idx in [('前期',2),('後期',4)]]
   for schedule,raw,dept in items:
    chunks=clean(raw).split('/');minimum=num(chunks[0])
    if minimum is None:continue
    r=make_record('fukushima',faculty,dept,'一般選抜'+schedule,year)
    put(r['total'],'minimum',minimum,sid)
    if len(chunks)==2:put(r['total'],'full',num(chunks[1]),sid)
    r['note']='2026年度一般選抜の総合最低点のみ公表。満点の記載がない欄は未収録。学類一括の最低点を個別コースに複製しません。'
    records.append(r)
 assert len(records)==16
 return records
