import pdfplumber
from core import clean,num,make_record,put,add_ratios,metric

def parse(paths,year,source):
 records={}
 def get(f,d,s):
  key=(f,d,s)
  if key not in records:records[key]=make_record('saitama',f,d,s,year)
  return records[key]
 with pdfplumber.open(paths['scores']) as doc:
  assert f'令和{year-2018}年度' in clean(doc.pages[0].extract_text())
  table=doc.pages[0].extract_tables()[0];assert len(table[0])==14
  labels=['','','','']
  for row in table[2:]:
   for i in range(4):
    if row[i] is not None:
     labels[i]=clean(row[i])
     for j in range(i+1,4):labels[j]=''
   faculty=labels[0];department=''.join(labels[1:]);assert faculty.endswith('学部') and department
   for offset,sel in [(4,'一般選抜前期'),(9,'一般選抜後期')]:
    # A blank full score means the selection is not offered in this score table.
    if num(row[offset]) is None:continue
    r=get(faculty,department,sel);g=r['total'];sid=source('scores',1)
    for k,idx in [('full',offset),('minimum',offset+1),('average',offset+3)]:
     v=num(row[idx]);put(g,k,v,sid)
     if v is None:g[k]=metric(None,sid,'公式資料で非公表（合格者数などの開示条件による）。',status='unavailable')
    for idx in [1,3]:
     v=num(row[offset+idx]);pct=num(clean(row[offset+idx+1]).replace('%',''))
     if v is not None and pct is not None:assert abs(v/num(row[offset])*100-pct)<.02
    g['maximum']=metric(None,sid,'当該公式結果資料には最高点が掲載されていません。',status='unavailable')
 with pdfplumber.open(paths['admissions']) as doc:
  assert f'令和{year-2018}年度埼玉大学一般選抜実施状況' in clean(doc.pages[0].extract_text())
  table=doc.pages[0].extract_tables()[0];assert len(table[0])==11
  faculty=department=''
  for row in table[2:]:
   if row[0]:faculty=clean(row[0])
   if row[1]:department=clean(row[1])
   s=clean(row[3]);cap=num(row[4])
   if s not in ['前期','後期','国際枠'] or cap is None or department in ['計','合計'] or not faculty.endswith('学部'):continue
   d='国際プログラム枠' if s=='国際枠' else department
   r=get(faculty,d,'一般選抜後期' if s=='後期' else '一般選抜前期');sid=source('admissions',1)
   for k,idx in [('capacity',4),('applicants',5),('examinees',7),('accepted',8)]:
    # Parenthetical counts are a subset, never a second headcount to add.
    v=num((row[idx] or '').split('(')[0]);put(r['admissions'],k,v,sid)
   add_ratios(r,sid)
 return list(records.values())
