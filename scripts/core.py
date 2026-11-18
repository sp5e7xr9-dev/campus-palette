"""Source-aware records. All parser output is pending until an exact digest is approved."""
import hashlib, json, math, re, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCORE_KEYS=['full','average','minimum','maximum','examineeAverage']
ADMISSION_KEYS=['capacity','applicants','examinees','accepted','applicationRatio','actualRatio']
def clean(v):return re.sub(r'\s+','',unicodedata.normalize('NFKC',v or ''))
def num(v):
 s=clean(v).replace(',','')
 if not re.fullmatch(r'\d+(\.\d+)?',s):return None
 return float(s) if '.' in s else int(s)
def metric(value=None,source=None,reason='公式資料で確認できる数値が未登録です。',status='not_collected',kind='official'):
 return dict(value=value,status='pending' if value is not None else status,**({'source':source} if source else {}),kind=kind,**({'reason':reason} if value is None else {}))
def make_record(uni,faculty,department,selection,year):
 key=[uni,faculty,department,selection,str(year)];return dict(id=hashlib.sha256('|'.join(key).encode()).hexdigest()[:20],university=uni,faculty=faculty,department=department,selection=selection,year=year,common={k:metric() for k in SCORE_KEYS},individual={k:metric() for k in SCORE_KEYS},total={k:metric() for k in SCORE_KEYS},admissions={k:metric() for k in ADMISSION_KEYS})
def put(group,key,value,source):
 if value is None:return
 if group[key]['value'] is not None and group[key]['value']!=value:raise ValueError(f'conflicting cell: {key}')
 group[key]=metric(value,source)
def add_ratios(r,source):
 g=r['admissions']
 for key,a,b in [('applicationRatio','applicants','capacity'),('actualRatio','examinees','accepted')]:
  if g[a]['value'] is not None and g[b]['value'] is not None and g[b]['value']>0:
   g[key]=metric(round(g[a]['value']/g[b]['value'],4),source,kind='calculated')
def selection(v):
 s=clean(v)
 for a,b in [('前期日程','一般選抜前期'),('後期日程','一般選抜後期')]:s=s.replace(a,b)
 return s

def validate(data,public=False):
 sources={s['id']:s for s in data['sources']};unis={u['id'] for u in data['universities']};ids=set()
 for r in data['records']:
  assert r['id'] not in ids,'duplicate record';ids.add(r['id'])
  assert r['university'] in unis and r['year'] in [2024,2025,2026]
  assert r['faculty'] and r['department'] and r['selection']
  assert r['department'] not in ['合計','計'] and r['faculty'].endswith(('学部','学群','学類','学環'))
  if r['university']=='niigata' and r['department'].startswith('工学科'):assert r['faculty']=='工学部'
  if r['university']=='niigata' and r['department'].startswith(('医学科','保健学科')):assert r['faculty']=='医学部'
  for section in ['common','individual','total','admissions']:
   g=r[section]
   for k,m in g.items():
    v=m['value'];assert m['status'] in ['verified','pending','unavailable','not_collected','not_applicable','failed','investigating']
    if v is None:assert m['status']!='verified';continue
    assert isinstance(v,(int,float)) and math.isfinite(v) and v>=0
    assert m['status']==('verified' if public else 'pending')
    s=sources[m['source']];assert s['university']==r['university'] and s['year']==r['year']
    assert s['sha256'] and s['page']>=1 and s['url'].startswith('https://')
    if m.get('contextSource'):
     c=sources[m['contextSource']];assert c['university']==r['university'] and c['year']==r['year'] and c['sha256']
     if public:assert c['status']=='verified'
    if public:assert s['status']=='verified'
   if section!='admissions':
    vals={k:m['value'] for k,m in g.items()}
    for k in ['average','minimum','maximum','examineeAverage']:
     if vals[k] is not None and vals['full'] is not None:assert vals[k]<=vals['full'],(r,k)
    seq=[vals[k] for k in ['minimum','average','maximum'] if vals[k] is not None];assert seq==sorted(seq),(r,'score order')
   else:
    for k in ['capacity','applicants','examinees','accepted']:
     assert g[k]['value'] is None or isinstance(g[k]['value'],int)
    for k,a,b in [('applicationRatio','applicants','capacity'),('actualRatio','examinees','accepted')]:
     if g[k]['value'] is not None:assert abs(g[k]['value']-g[a]['value']/g[b]['value'])<.00011
 return True
