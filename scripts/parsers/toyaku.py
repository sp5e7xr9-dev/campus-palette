import pdfplumber
from bs4 import BeautifulSoup
from core import clean,num,make_record,put,metric,add_ratios

def expand(table):
 out=[];spans={}
 for tr in table.find_all('tr'):
  row=[];column=0
  for cell in tr.find_all(['th','td']):
   while column in spans:
    value,left=spans.pop(column);row.append(value)
    if left>1:spans[column]=(value,left-1)
    column+=1
   assert int(cell.get('colspan',1))==1
   value=clean(cell.get_text());row.append(value)
   if int(cell.get('rowspan',1))>1:spans[column]=(value,int(cell['rowspan'])-1)
   column+=1
  while column in spans:
   value,left=spans.pop(column);row.append(value)
   if left>1:spans[column]=(value,left-1)
   column+=1
  out.append(row)
 return out

def parse(paths,year,source):
 assert year in [2024,2026]
 with pdfplumber.open(paths['guide']) as doc:
  pages=[31,32,33,34] if year==2026 else [29,30,31,32]
  contexts={n:clean(doc.pages[n-1].extract_text()) for n in pages}
  assert f'令和{year-2018}年度大学入学共通テスト' in contexts[pages[0]] and '本学の個別試験は課しません' in contexts[pages[0]]
  for n in ([32,33] if year==2026 else [30,31]):assert '得点調整' in contexts[n]
 soup=BeautifulSoup(paths['scores'].read_bytes(),'html.parser')
 tables=soup.find_all('table');assert len(tables)==6
 score_index=1 if year==2026 else 5
 rows=expand(tables[score_index]);assert len(rows)==16
 assert rows[1][0]==f'{year}年度' and '合格者最低点' in ''.join(rows[0])
 sid=source('scores',1);records=[]
 for row in rows[1:]:
  assert len(row)==6,row
  _,method,full,department,average,minimum=row
  assert method in ['A方式I期','A方式II期','B方式','T方式','C方式']
  section='common' if method.startswith('A') else 'individual'
  page=(31 if year==2026 else 29) if method=='A方式I期' else ((31 if year==2026 else 30) if method=='A方式II期' else ({'B方式':32,'T方式':33,'C方式':34}[method] if year==2026 else {'B方式':30,'T方式':31,'C方式':32}[method]))
  context=source('guide',page)
  r=make_record('toyaku','生命科学部',department,'一般選抜'+method,year)
  r['note']=f'{year}年度生命科学部の方式別公表値。A方式は共通テスト利用、B・T・C方式は個別試験。調査書も総合的に評価されます。'+('B・T方式は科目間の得点補正あり。' if method in ['B方式','T方式'] else '')
  for k,value in [('full',full),('average',average),('minimum',minimum)]:
   v=num(value.removesuffix('点'));assert v is not None;put(r[section],k,v,sid)
   r[section][k]['contextSource']=context;r[section][k]['note']=r['note']
  r[section]['maximum']=metric(None,sid,'当該結果表に最高点の掲載はありません。',status='unavailable')
  for k in r['total']:r['total'][k]=metric(None,sid,'独立した総合点としては転記しません。A方式は共通テスト、他方式は個別試験欄を参照してください。',status='unavailable')
  records.append(r)
 # Counts use their matching year/method/department; never transfer faculty totals.
 method=None
 for tr in tables[score_index-1].select('tbody > tr'):
  cells=[clean(c.get_text()) for c in tr.find_all(['th','td'],recursive=False)]
  headers=[clean(c.get_text()) for c in tr.find_all('th',recursive=False) if not clean(c.get_text()).endswith('年度')]
  if headers:method=headers[-1]
  if method not in ['A方式I期','A方式II期','B方式','T方式','C方式']:continue
  dept=next((v for v in cells if v in ['分子生命科学科','応用生命科学科','生命医科学科']),None);assert dept
  vals=[num(v.removesuffix('名')) for v in cells[-5:-1]]
  assert all(isinstance(v,int) for v in vals),cells
  r=next(r for r in records if r['department']==dept and r['selection']=='一般選抜'+method)
  for k,v in zip(['capacity','applicants','examinees','accepted'],vals):put(r['admissions'],k,v,sid)
  add_ratios(r,sid)
 assert all(r['admissions']['applicants']['value'] is not None for r in records)
 return records
