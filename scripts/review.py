#!/usr/bin/env python3
"""Exact-content local review and approval. Never automatically approves changed PDFs."""
import argparse,copy,datetime,hashlib,json
from core import ROOT,validate

def digest(record,sources):
 # Retrieval times must not invalidate a byte-identical official PDF.
 evidence={k:{'value':v['value'],'status':v['status'],'source':v.get('source'),'kind':v.get('kind'),'reason':v.get('reason')} for section in ['common','individual','total','admissions'] for k,v in [(section+'.'+key,m) for key,m in record[section].items()]}
 used={m.get('source') for s in ['common','individual','total','admissions'] for m in record[s].values() if m.get('source')}
 payload={'identity':{k:record[k] for k in ['id','university','faculty','department','selection','year']},'cells':evidence,'documents':{sid:sources[sid]['sha256'] for sid in sorted(used)}}
 return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def export(candidate,approvals):
 validate(candidate);d=copy.deepcopy(candidate);sources={s['id']:s for s in d['sources']};approved=approvals.get('records',{});used=set()
 for r in d['records']:
  a=approved.get(r['id']);ok=a and a['digest']==digest(r,sources)
  for section in ['common','individual','total','admissions']:
   for k,m in r[section].items():
    if m['value'] is not None:
     if ok:m['status']='verified';used.add(m['source'])
     else:r[section][k]={'value':None,'status':'pending','reason':'元資料の確認・承認待ちです。'}
  if ok:
   for s in sources.values():
    if s['id'] in used:s.update(status='verified',verifiedAt=a['at'],reviewer=a['reviewer'])
 for r in d['records']:
  original=next(x for x in candidate['records'] if x['id']==r['id'])
  a=approved.get(r['id'])
  if a and a['digest']==digest(original,{s['id']:s for s in candidate['sources']}):
   for section in ['common','individual','total','admissions']:
    for m in r[section].values():
     if m.get('source'):sources[m['source']].update(status='verified',verifiedAt=a['at'],reviewer=a['reviewer'])
 validate(d,public=True);return d
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['list','show','approve','export']);p.add_argument('--candidate',type=str,default=str(ROOT/'.cache/candidate.json'));p.add_argument('--approvals',default=str(ROOT/'scripts/approvals.json'));p.add_argument('--id');p.add_argument('--digest');p.add_argument('--reviewer');p.add_argument('--out',default=str(ROOT/'public/data/admissions.json'));a=p.parse_args()
 from pathlib import Path
 d=json.loads(Path(a.candidate).read_text());ss={s['id']:s for s in d['sources']};ap=Path(a.approvals);approvals=json.loads(ap.read_text()) if ap.exists() else {'records':{}}
 if a.command=='list':
  for r in d['records']:print(r['id'],r['year'],r['faculty'],r['department'],r['selection'],digest(r,ss))
 elif a.command=='show':
  r=next(r for r in d['records'] if r['id']==a.id);print(json.dumps(r,ensure_ascii=False,indent=2));print('digest:',digest(r,ss))
  for sid in sorted({m['source'] for k in ['common','individual','total','admissions'] for m in r[k].values() if m.get('source')}):print(ss[sid]['url']+'#page='+str(ss[sid]['page']),ss[sid]['sha256'])
 elif a.command=='approve':
  if not a.id or not a.digest or not a.reviewer:p.error('--id, --digest and --reviewer are required after reviewing original PDF')
  r=next(r for r in d['records'] if r['id']==a.id)
  if digest(r,ss)!=a.digest:raise ValueError('candidate changed; review again')
  validate(d);approvals['records'][a.id]={'digest':a.digest,'reviewer':a.reviewer,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()};ap.write_text(json.dumps(approvals,ensure_ascii=False,indent=2)+'\n')
 elif a.command=='export':
  out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(export(d,approvals),ensure_ascii=False,indent=2)+'\n');print('Exported approved values only:',out)
