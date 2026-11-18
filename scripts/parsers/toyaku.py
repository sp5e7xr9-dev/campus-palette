import pdfplumber
from bs4 import BeautifulSoup
from core import clean,num,make_record,put,metric

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
 assert year==2026
 with pdfplumber.open(paths['guide']) as doc:
  contexts={31:clean(doc.pages[30].extract_text()),32:clean(doc.pages[31].extract_text()),33:clean(doc.pages[32].extract_text()),34:clean(doc.pages[33].extract_text())}
  assert '令和8年度大学入学共通テスト' in contexts[31] and '本学の個別試験は課しません' in contexts[31]
  for n in [32,33]:assert '得点調整' in contexts[n]
 soup=BeautifulSoup(paths['scores'].read_bytes(),'html.parser')
 tables=soup.find_all('table');assert len(tables)==6
 rows=expand(tables[1]);assert len(rows)==16
 assert rows[1][0]=='2026年度' and '合格者最低点' in ''.join(rows[0])
 sid=source('scores',1);records=[]
 for row in rows[1:]:
  assert len(row)==6,row
  _,method,full,department,average,minimum=row
  assert method in ['A方式I期','A方式II期','B方式','T方式','C方式']
  section='common' if method.startswith('A') else 'individual'
  page=31 if method.startswith('A') else {'B方式':32,'T方式':33,'C方式':34}[method]
  context=source('guide',page)
  r=make_record('toyaku','生命科学部',department,'一般選抜'+method,year)
  r['note']='2026年度生命科学部の方式別公表値。A方式は共通テスト利用、B・T・C方式は個別試験。調査書も総合的に評価されます。'+('B・T方式は科目間の得点補正あり。' if method in ['B方式','T方式'] else '')
  for k,value in [('full',full),('average',average),('minimum',minimum)]:
   v=num(value.removesuffix('点'));assert v is not None;put(r[section],k,v,sid)
   r[section][k]['contextSource']=context;r[section][k]['note']=r['note']
  r[section]['maximum']=metric(None,sid,'当該結果表に最高点の掲載はありません。',status='unavailable')
  for k in r['total']:r['total'][k]=metric(None,sid,'独立した総合点としては転記しません。A方式は共通テスト、他方式は個別試験欄を参照してください。',status='unavailable')
  records.append(r)
 return records
