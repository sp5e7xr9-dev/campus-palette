#!/usr/bin/env python3
"""Low-frequency collector. Network errors never overwrite public data."""
import argparse,datetime,hashlib,importlib,json,ssl,time,urllib.error,urllib.parse,urllib.request,urllib.robotparser
from pathlib import Path
from core import ROOT,validate
UA='CampusPalette/1.0 (educational admissions facts; low-frequency single-request collector)'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def fetch(url,allowed_host,cache,format='pdf'):
 if urllib.parse.urlparse(url).scheme!='https' or urllib.parse.urlparse(url).hostname!=allowed_host:raise ValueError('unapproved origin')
 class Guard(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,req,fp,code,msg,headers,newurl):
   if urllib.parse.urlparse(newurl).hostname!=allowed_host or not newurl.startswith('https://'):raise ValueError('unapproved redirect')
   return super().redirect_request(req,fp,code,msg,headers,newurl)
 # certifi is optional; never disable certificate verification.
 try:
  import certifi
  context=ssl.create_default_context(cafile=certifi.where())
 except ImportError:context=ssl.create_default_context()
 opener=urllib.request.build_opener(Guard(),urllib.request.HTTPSHandler(context=context))
 def read(u):
  with opener.open(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=30) as r:
   b=r.read(20_000_001)
   if len(b)>20_000_000:raise ValueError('document too large')
   return b
 robots_url='https://'+allowed_host+'/robots.txt'
 if allowed_host not in cache:
  rp=urllib.robotparser.RobotFileParser()
  try:rp.parse(read(robots_url).decode('utf-8').splitlines())
  except urllib.error.HTTPError as e:
   if e.code==404:rp.parse([])
   else:raise
  cache[allowed_host]=rp
 rp=cache[allowed_host]
 if not rp.can_fetch(UA,url):raise PermissionError('robots.txt disallows collection')
 time.sleep(max(2,rp.crawl_delay(UA) or 0));b=read(url)
 if format=='pdf' and not b.startswith(b'%PDF-'):raise ValueError('not a PDF; possibly access restricted')
 if format=='html' and b'<html' not in b.lower():raise ValueError('not HTML; possibly access restricted')
 return b

def collect(cache_path,offline=False):
 config=json.loads((ROOT/'scripts/universities.json').read_text());cache_path.mkdir(parents=True,exist_ok=True)
 data=dict(version=1,updatedAt=now(),universities=[{k:v for k,v in u.items() if k not in ['documents','parser','parserByYear','policyUrl','format','formatByKey','allowedHosts']} for u in config],sources=[],records=[],coverageNote='2024〜2026年度を対象に、大学公式資料と照合した募集単位のみ収録しています。大学ごとの収録年度・範囲は各カードと注記をご確認ください。未収録・非公表の値は推測せず「入手不可」と表示します。')
 robots={}
 for u in config:
  allowed_parsers=['niigata','saitama','hirosaki','miyagi','fukushima','fukushima2026','tmu','toyaku','iwate','yamagata','obihiro','utsunomiya','tohoku','akita','chiba']
  if u['parser'] not in allowed_parsers:raise ValueError('register a reviewed parser before enabling a university')
  for yr,docs in u['documents'].items():
   year=int(yr);paths={};meta={}
   for key,url in docs.items():
    fmt=u.get('formatByKey',{}).get(key,u.get('format','pdf'));name=f"{u['id']}-{year}-{key}.{fmt}";path=cache_path/name
    if not offline:
     host=urllib.parse.urlparse(url).hostname
     if host not in u.get('allowedHosts',[urllib.parse.urlparse(u['officialUrl']).hostname]):raise ValueError('unapproved source host')
     b=fetch(url,host,robots,fmt);path.write_bytes(b)
     (cache_path/(name+'.meta.json')).write_text(json.dumps({'retrievedAt':now(),'url':url}))
    if not path.exists():raise FileNotFoundError(path)
    info=json.loads((cache_path/(name+'.meta.json')).read_text());assert info['url']==url
    paths[key]=path;meta[key]=dict(url=url,retrievedAt=info['retrievedAt'],sha256=hashlib.sha256(path.read_bytes()).hexdigest())
   def source(key,page):
    sid=f"{u['id']}-{year}-{key}-p{page}"
    if not any(s['id']==sid for s in data['sources']):
     title=f"新潟大学 データブック{year+1}（{year}年度入試結果）" if key=='book' else f"{u['name']} {year}年度 入試結果（{key}）"
     data['sources'].append(dict(id=sid,university=u['id'],year=year,title=title,page=page,format=u.get('formatByKey',{}).get(key,u.get('format','pdf')),status='pending',**meta[key]))
    return sid
   parser=u.get('parserByYear',{}).get(str(year),u['parser'])
   if parser not in allowed_parsers:raise ValueError('unreviewed year parser')
   data['records']+=importlib.import_module('parsers.'+parser).parse(paths,year,source)
 validate(data)
 return data
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=ROOT/'.cache/sources');p.add_argument('--offline',action='store_true');p.add_argument('--out',type=Path,default=ROOT/'.cache/candidate.json');a=p.parse_args()
 a.out.parent.mkdir(parents=True,exist_ok=True)
 try:
  d=collect(a.cache,a.offline);a.out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(f"Candidate: {len(d['records'])} records, {len(d['sources'])} source pages. Not published.")
 except Exception as e:
  (a.out.parent/'last-error.json').write_text(json.dumps(dict(status='failed',at=now(),error=str(e)),ensure_ascii=False,indent=2));raise
