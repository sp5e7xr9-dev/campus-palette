import pdfplumber
from core import clean,num,make_record,put,metric

def parse(paths,year,source):
 assert year==2026
 records=[];sid=source('scores',57)
 with pdfplumber.open(paths['scores']) as doc:
  p=doc.pages[56];assert '令和8年度一般選抜の成績情報提供' in clean(p.extract_text())
  table=p.extract_tables()[0];assert len(table[0])==10
  faculty='';base=''
  for row in table[2:]:
   if row[0]:
    raw=clean(row[0]);faculty='データサイエンス経営学部' if 'サ' in raw else raw
   if row[1]:base=clean(row[1])
   schedules=(row[3] or '').splitlines();suffixes=(row[2] or '').splitlines()
   for n,schedule in enumerate(schedules):
    suffix=clean(suffixes[n] if len(suffixes)==len(schedules) else ''.join(suffixes));r=make_record('utsunomiya',faculty,base+suffix,'一般選抜'+clean(schedule).replace('日程',''),year)
    r['note']='2027年度向け募集要項に掲載された2026年度合格者成績。合格者10人未満は非公表。共通テストと個別学力検査は別々の公表値です。'
    for offset,section in [(4,'common'),(7,'individual')]:
     def cell(i):
      lines=(row[i] or '').splitlines();return lines[n] if len(lines)==len(schedules) else ''.join(lines)
     full=num(cell(offset));assert full is not None
     put(r[section],'full',full,sid)
     if row[offset+2] is None:
      values=cell(offset+1).split();values=values if len(values)==2 else [cell(offset+1)]*2
     else:values=[cell(offset+1),cell(offset+2)]
     for key,raw in zip(['maximum','average'],values):
      value=num(raw);put(r[section],key,value,sid)
      if value is None:r[section][key]=metric(None,sid,'合格者10人未満のため非公表。',status='unavailable')
     r[section]['minimum']=metric(None,sid,'当該公式成績表に最低点の掲載はありません。',status='unavailable')
    records.append(r)
 assert len(records)==24
 return records
