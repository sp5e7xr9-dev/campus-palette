"""Read the official score table, preserving merged labels and unweighted scores."""
import pdfplumber
from core import clean,num,selection,make_record,put,metric

def parse(paths,year,source):
 assert year in [2024,2025,2026]
 records=[]
 with pdfplumber.open(paths['scores']) as doc:
  page=doc.pages[4];text=clean(page.extract_text())
  assert f'令和{year-2018}年度弘前大学一般選抜' in text
  assert '傾斜配点前' in text and ('900点満点' in text if year==2024 else '1000点満点' in text)
  tables=page.extract_tables();assert len(tables)==1
  table=tables[0];assert len(table[0])==12 and 50<=len(table)<=54
  labels=['']*5;faculty=sel='';sid=source('scores',5)
  for row in table[1:]:
   if row[0]:
    faculty='人文社会科学部' if '人' in clean(row[0]) else clean(row[0]);labels=['']*5
   for i in range(5):
    if row[i+1] is not None:
     labels[i]=clean(row[i+1])
     for j in range(i+1,5):labels[j]=''
   # Four empty education rows have no schedule or score: do not invent an offering.
   if not clean(row[6]) and not clean(row[7]):continue
   if row[6]:sel=selection(row[6])
   department=''.join(labels).replace('コ|ス','コース')
   r=make_record('hirosaki',faculty,department,sel,year)
   r['note']='追加合格者を除く総点。共通テスト平均は傾斜配点前（'+('全学部900点満点' if year==2024 else '人文社会科学部900点、その他1000点満点')+'）で、総合点の内訳配点とは異なります。'
   for key,idx in [('full',7),('maximum',8),('minimum',9),('average',10)]:
    value=num(row[idx]);put(r['total'],key,value,sid)
    if value is None:r['total'][key]=metric(None,sid,'合格者10名未満のため不開示（原本の＊）。',status='unavailable')
   put(r['common'],'full',900 if year==2024 or faculty=='人文社会科学部' else 1000,sid)
   put(r['common'],'average',num(row[11]),sid)
   if num(row[11]) is None:r['common']['average']=metric(None,sid,'合格者10名未満のため不開示（原本の＊）。',status='unavailable')
   for m in r['common'].values():
    m['basis']='unweighted';m['note']='傾斜配点前の共通テスト得点。総合点からの逆算や配点構成の合算には使用できません。'
   for g,keys in [('common',['maximum','minimum','examineeAverage']),('individual',list(r['individual'])),('total',['examineeAverage'])]:
    for k in keys:r[g][k]=metric(None,sid,'当該結果表には掲載されていません。',status='unavailable')
   records.append(r)
 assert len(records)>=45
 return records
