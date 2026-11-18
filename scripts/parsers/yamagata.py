import pdfplumber
from core import clean,num,make_record,put,metric

def parse(paths,year,source):
 records=[];sid=source('scores',1)
 with pdfplumber.open(paths['scores']) as doc:
  page=doc.pages[0];text=clean(page.extract_text());assert f'令和{year-2018}年度' in text and '(一般選抜)' in text
  table=page.extract_tables()[0];assert len(table[0])==9
  faculty='';labels=['']*3
  for row in table[1:]:
   if row[0]:
    raw=clean(row[0]);faculty='人文社会科学部' if '人' in raw else '地域教育文化学部' if raw=='地文域化教学育部' else raw;labels=['']*3
   for i in range(3):
    if row[i+1] is not None:
     raw=clean(row[i+1]).replace('※','');labels[i]='人文社会科学科' if i==0 and faculty=='人文社会科学部' else '地域教育文化学科' if i==0 and faculty=='地域教育文化学部' else '学校教育教員養成課程' if i==0 and faculty=='教育学部' else raw.replace('コ|ス','コース')
     for j in range(i+1,3):labels[j]=''
   department=''.join(labels) or '学環一括公表'
   schedule=clean(row[4]);assert schedule.startswith(('前期','後期'))
   r=make_record('yamagata',faculty,department,'一般選抜'+schedule,year)
   r['note']='一般選抜の総合点。合格者10人以下の学科等は非公表。'+('理学科前期は個別学力検査の成績順上位5%以内に該当した者を含みます。' if year<2026 and faculty=='理学部' and schedule=='前期' else '')
   for key,i in zip(['full','maximum','minimum','average'],range(5,9)):
    v=num(row[i]);put(r['total'],key,v,sid)
    if v is None:r['total'][key]=metric(None,sid,'合格者10人以下の学科等は非公表（原本の点線）。',status='unavailable')
   records.append(r)
 return records
