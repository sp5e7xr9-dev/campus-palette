import re,pdfplumber
from core import clean,num,make_record,put

def parse(paths,year,source):
 assert year==2025
 records=[]
 with pdfplumber.open(paths['scores']) as doc:
  assert '令和7年度福島大学人間発達文化学類一般選抜前期日程' in clean(doc.pages[0].extract_text())
  for n,page in enumerate(doc.pages):
   text=clean(page.extract_text())
   for label,full,minimum in re.findall(r'([^。]+?コース.*?)合格者の最低点\(総合点([\d,]+)点\)は,([\d.]+)点です。',text):
    # Start after preceding IDs/headings; use the explicit course label only.
    match=re.search(r'(教育実践|心理学・幼児教育|特別支援・生活科学|人文科学|数理自然科学|スポーツ健康科学)コース.*$',label)
    assert match,label
    r=make_record('fukushima','人間発達文化学類',match[0],'一般選抜前期',year);sid=source('scores',n+1)
    put(r['total'],'full',num(full),sid);put(r['total'],'minimum',num(minimum),sid)
    r['note']='2025年度 人間発達文化学類の前期合格発表資料に記載された総合最低点のみ収録。最高点・平均点、他学類、他年度は未収録。'
    records.append(r)
 assert len(records)==9
 return records
