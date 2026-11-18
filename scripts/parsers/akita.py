"""Reviewed subset from scanned official tables; stop if the PDF bytes change."""
import hashlib,json
from pathlib import Path
from core import make_record,put

def parse(paths,year,source):
 snapshot=json.loads(Path(__file__).with_name('akita_reviewed.json').read_text())
 assert hashlib.sha256(paths['scores'].read_bytes()).hexdigest()==snapshot['sha256'][str(year)],'scanned PDF changed; original-image review required'
 records={}
 for faculty,department,selection,section,page,values in snapshot['rows'][str(year)]:
  key=(faculty,department,selection)
  if key not in records:
   records[key]=make_record('akita',faculty,department,selection,year)
   records[key]['note']='原本と照合した一部募集単位のみ収録。共通テストは傾斜配点後。総合点と各試験の最高・最低点は別の値です。学部改組・方式別配点の変更に注意してください。'
  sid=source('scores',page)
  for k,v in zip(['full','maximum','minimum','average'],values):put(records[key][section],k,v,sid)
 return list(records.values())
