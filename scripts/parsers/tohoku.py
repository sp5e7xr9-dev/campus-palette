import pdfplumber
from core import clean,num,make_record,put

def parse(paths,year,source):
 records=[]
 with pdfplumber.open(paths['scores']) as doc:
  page=19 if year!=2025 else 21
  p=doc.pages[page];text=clean(p.extract_text());assert '大学入学共通テストの本学配点及び個別学力試験の配点' in text
  tables=p.extract_tables();assert len(tables)==2;sid=source('scores',page+1)
  for table,schedule in zip(tables,['前期','後期']):
   current=None
   for row in table[1:]:
    if row[0]:current=clean(row[0])
    if current not in ['理学部','工学部','農学部']:continue
    label=next((clean(v) for v in row if clean(v) in ['共通テスト','個別']),None);assert label
    section='common' if label=='共通テスト' else 'individual'
    if label=='共通テスト':
     r=make_record('tohoku',current,'学部一括配点（学科・系別の成績ではない）','一般選抜'+schedule,year)
     r['note']='募集要項の満点・配点のみ収録。合格者最高点・最低点・平均点は未確認です。学科・系別の成績ではありません。2024年度と2025年度以降で配点体系が異なります。'
     put(r['total'],'full',num(row[-1]),sid);records.append(r)
    value=num(row[-2]);assert value is not None;put(r[section],'full',value,sid)
 assert len(records)==4
 return records
