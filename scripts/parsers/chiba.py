import re
from bs4 import BeautifulSoup
from core import clean,make_record,put

def parse(paths,year,source):
 assert year==2026
 text=clean(BeautifulSoup(paths['scores'].read_bytes(),'html.parser').get_text(' ',strip=True))
 section=text.split('令和8年度一般選抜合格者の試験結果',1)[1].split('令和9年度',1)[0]
 match=re.search(r'配点1375点\(共通テスト475点\+個別900点\).*最高点1098点.*最低点823点.*平均点888点',section);assert match
 r=make_record('chiba','看護学部','看護学科','一般選抜前期',year);sid=source('scores',1)
 for k,v in [('full',1375),('maximum',1098),('minimum',823),('average',888)]:put(r['total'],k,v,sid)
 put(r['common'],'full',475,sid);put(r['individual'],'full',900,sid)
 r['note']='2026年度看護学部・前期日程のみ照合済み。共通テスト・個別試験の内訳は満点のみ公表。2024・2025年度の全学得点PDFは取得失敗のため確認待ち。'
 return [r]
