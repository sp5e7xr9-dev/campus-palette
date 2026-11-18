import re
import pdfplumber
from core import clean,num,selection,make_record,put,add_ratios,metric

def parse(paths,year,source):
 records={}
 def get(f,d,s):
  key=(f,d,s)
  if key not in records:records[key]=make_record('niigata',f,d,s,year)
  return records[key]
 with pdfplumber.open(paths['book']) as doc:
  text=clean(doc.pages[1].extract_text())
  assert f'令和{year-2018}年度入学試験結果' in text
  assert '新潟大学' in clean(doc.pages[0].extract_text())
  faculty=department=''
  table=doc.pages[1].extract_tables()[0];assert len(table[0])==21
  for row in table[2:]:
   if row[0]:faculty=clean(row[0])
   if row[1] and clean(row[1])!='合計':department=clean(row[1])
   s=selection(row[2])
   if not s or '計' in s or not num(row[3]):continue
   r=get(faculty,department,s);sid=source('book',2)
   for k,idx in [('capacity',3),('applicants',4),('examinees',8),('accepted',13)]:put(r['admissions'],k,num(row[idx]),sid)
   add_ratios(r,sid)
  department_faculties={r['department']:r['faculty'] for r in records.values()}
  faculty=department=sel=stage=''
  for p in range(2,7):
   table=doc.pages[p].extract_tables()[0];assert len(table[0])==7
   sid=source('book',p+1)
   for row in table[1:]:
    if row[0]:faculty=clean(row[0])
    if row[1]:
     department=clean(row[1])
     # A vertically centered merged faculty label can appear after its first rows.
     # Resolve using the independent official admissions table, not prior-page carryover.
     matches=[(d,f) for d,f in department_faculties.items() if department.startswith(d)]
     if not matches:raise ValueError(f'no official faculty mapping for {department}')
     matches.sort(key=lambda x:len(x[0]),reverse=True)
     faculty=matches[0][1]
    if row[2]:sel=selection(row[2])
    if row[3]:
     fragment=clean(row[3])
     stage=(re.sub(r'\(配点[\d,]+\)','',stage)+fragment) if fragment.startswith('(配点') else fragment
    if not (faculty and department and sel):raise ValueError('unresolved merged cell')
    # Stage text must explicitly identify the test. No total is inferred.
    section='common' if '共通テスト' in stage else 'individual' if ('個別学力検査' in stage or '本学が実施' in stage) else None
    if section is None:raise ValueError(f'unknown stage {stage}')
    r=get(faculty,department,sel);g=r[section]
    full=re.search(r'配点([\d,]+)',stage)
    if full:put(g,'full',num(full[1]),sid)
    label=clean(row[4]);k={'最高点':'maximum','最低点':'minimum','平均点':'average'}.get(label)
    if k:
     v=num(row[5]);put(g,k,v,sid)
     if v is not None and row[6] and '%' in row[6] and full:
      pct=num(clean(row[6]).replace('%',''))
      assert pct is not None and abs(v/num(full[1])*100-pct)<.15,(year,p,row)
     if v is None:g[k]=metric(None,sid,'この資料の当該欄は非公表または段階評価です。',status='unavailable')
  for r in records.values():
   for k in r['total']:r['total'][k]=metric(None,source('book',3),'公式結果資料に総合点の掲載を確認できません。共通テストと個別試験の点数は合計しません。',status='unavailable')
 return list(records.values())
