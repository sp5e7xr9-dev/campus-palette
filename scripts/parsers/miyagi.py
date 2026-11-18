from bs4 import BeautifulSoup
from core import clean,num,make_record,put,metric

def parse(paths,year,source):
 assert year==2026
 soup=BeautifulSoup(paths['scores'].read_bytes(),'html.parser')
 heading=soup.find(string=lambda t:t and '合格者最高点・最低点・平均点（令和8年度入学）' in t)
 assert heading is not None
 records=[];sid=source('scores',1)
 for faculty in ['看護学群','事業構想学群','食産業学群']:
  h=soup.find(['h3','h4'],string=lambda s:s and clean(s)==faculty);assert h
  table=h.find_next('table');rows=table.find_all('tr');assert len(rows)==5
  for offset,schedule in [(1,'前期'),(3,'後期')]:
   r=make_record('miyagi',faculty,'学群一括公表（学科・学類別の区分なし）','一般選抜'+schedule,year)
   r['note']='学群一括の公表です。調査書等の内容も総合的に判定されます。共通テスト・個別試験の最高点同士や最低点同士を合算しません。'
   for n,section in [(offset,'common'),(offset+1,'individual')]:
    cells=[clean(c.get_text()) for c in rows[n].find_all(['td','th'])]
    assert ('大学入学共通テスト' if section=='common' else '個別学力検査') in cells
    for k,v in zip(['full','maximum','minimum','average'],cells[-4:]):
     assert num(v) is not None;put(r[section],k,num(v),sid)
    if section=='common':
     put(r['admissions'],'capacity',num(cells[1]),sid);put(r['admissions'],'accepted',num(cells[2]),sid)
   for k in r['total']:r['total'][k]=metric(None,sid,'当該公式ページに総合点の掲載はありません。内訳の合算は行いません。',status='unavailable')
   records.append(r)
 return records
