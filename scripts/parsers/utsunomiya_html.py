"""Historical score tables, not next year's subject/weight tables on the same page."""
from bs4 import BeautifulSoup
from core import clean,num,make_record,put,metric

def expanded_rows(table):
 spans={}
 for tr in table.select('tbody > tr'):
  row=[];col=0
  for cell in tr.find_all(['th','td'],recursive=False):
   while col in spans:
    value,left=spans.pop(col);row.append(value)
    if left>1:spans[col]=(value,left-1)
    col+=1
   value=clean(cell.get_text());width=int(cell.get('colspan',1));height=int(cell.get('rowspan',1))
   for _ in range(width):
    row.append(value)
    if height>1:spans[col]=(value,height-1)
    col+=1
  while col in spans:
   value,left=spans.pop(col);row.append(value)
   if left>1:spans[col]=(value,left-1)
   col+=1
  yield tr,row

def parse(paths,year,source):
 assert year in [2024,2025]
 soup=BeautifulSoup(paths['scores'].read_bytes(),'html.parser');records=[];sid=source('scores',1)
 headings=[h for h in soup.find_all('h5') if clean(h.get_text())==f'令和{year-2018}年度一般選抜合格者成績']
 assert len(headings)==6
 for h in headings:
  faculty=clean(h.find_previous('h4').get_text());assert faculty.endswith('学部')
  for tr,row in expanded_rows(h.find_next('table')):
   assert len(row)>=7,(faculty,row)
   values=row[-6:];labels=row[:-6]
   if not any(values):
    assert year==2024 and faculty=='農学部' and labels==['森林科学科']
    continue
   # Schedule is encoded by the official table's mae/ato classes.
   schedule='後期' if tr.select_one('.ato') else '前期'
   department=''.join(dict.fromkeys(v for v in labels if v))
   if faculty=='共同教育学部':department='学校教育教員養成課程'+department
   r=make_record('utsunomiya',faculty,department,'一般選抜'+schedule,year)
   r['note']=f'{year+1}年度直前特設サイトの{year}年度合格者成績表。同ページの翌年度配点表とは区別しています。合格者10人未満は非公表。学科再編前の名称を保持。'
   for offset,section in [(0,'common'),(3,'individual')]:
    assert num(values[offset]) is not None,(faculty,row)
    for k,raw in zip(['full','maximum','average'],values[offset:offset+3]):
     v=num(raw);put(r[section],k,v,sid)
     if v is None:
      assert raw=='非公表',raw
      r[section][k]=metric(None,sid,'合格者10人未満のため非公表。',status='unavailable')
    r[section]['minimum']=metric(None,sid,'当該公式成績表に最低点の掲載はありません。',status='unavailable')
   records.append(r)
 assert len(records)==(25 if year==2024 else 26),len(records)
 return records
