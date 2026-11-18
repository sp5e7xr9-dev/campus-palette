import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from core import validate,make_record,put,metric
from review import digest,export
DATA=json.loads((ROOT/'public/data/admissions.json').read_text())
def find(uni,year,faculty,department,selection='一般選抜前期'):
 return next(r for r in DATA['records'] if (r['university'],r['year'],r['faculty'],r['department'],r['selection'])==(uni,year,faculty,department,selection))
class OfficialDataTests(unittest.TestCase):
 def test_all_public_data_valid(self):self.assertTrue(validate(DATA,public=True))
 def test_years_not_confused_with_book_title(self):
  for y,value,full in [(2024,302.8,450),(2025,352.2,500),(2026,340.5,500)]:
   r=find('niigata',y,'人文学部','人文学科');self.assertEqual(r['common']['average']['value'],value);self.assertEqual(r['common']['full']['value'],full)
 def test_stages_and_total_separate(self):
  r=find('niigata',2026,'人文学部','人文学科');self.assertEqual(r['individual']['average']['value'],277.8)
  self.assertTrue(all(m['value'] is None for m in r['total'].values()));self.assertIsNone(r['common']['examineeAverage']['value'])
 def test_saitama_official_totals(self):
  for y,average,minimum,full in [(2024,866.74,819.60,1200),(2025,880.38,840.45,1225),(2026,918.24,881.55,1225)]:
   r=find('saitama',y,'教養学部','教養学科');self.assertEqual(r['total']['average']['value'],average);self.assertEqual(r['total']['minimum']['value'],minimum);self.assertEqual(r['total']['full']['value'],full);self.assertIsNone(r['common']['average']['value'])
 def test_selection_not_mixed(self):
  r=find('saitama',2026,'教養学部','教養学科','一般選抜後期');self.assertEqual(r['total']['average']['value'],943.96)
 def test_ratios_exclude_parenthetical_counts(self):
  r=find('saitama',2026,'教養学部','教養学科');g=r['admissions'];self.assertEqual(g['examinees']['value'],315);self.assertEqual(g['accepted']['value'],151);self.assertAlmostEqual(g['actualRatio']['value'],315/151,places=4);self.assertEqual(g['actualRatio']['kind'],'calculated')
 def test_niigata_official_examinee_ratio_is_not_actual_ratio(self):
  g=find('niigata',2026,'人文学部','人文学科')['admissions'];self.assertAlmostEqual(g['actualRatio']['value'],307/157,places=4);self.assertNotEqual(g['actualRatio']['value'],2.2)
 def test_engineering_page_break_not_assigned_to_dentistry(self):
  rs=[r for r in DATA['records'] if r['department'].startswith('工学科')];self.assertGreater(len(rs),10);self.assertTrue(all(r['faculty']=='工学部' for r in rs))
 def test_medicine_not_assigned_to_science(self):
  for y in [2024,2025,2026]:
   r=find('niigata',y,'医学部','医学科');self.assertIsNotNone(r['common']['average']['value'])
  self.assertFalse(any(r['university']=='niigata' and r['department']=='医学科' and r['faculty']!='医学部' for r in DATA['records']))
 def test_missing_never_numeric(self):
  for r in DATA['records']:
   for k in ['common','individual','total','admissions']:
    for m in r[k].values():
     if m['status']!='verified':self.assertIsNone(m['value'])
 def test_no_aggregate_department(self):
  self.assertFalse(any(r['department'] in ['合計','計'] for r in DATA['records']))
 def test_official_sources_only(self):
  from urllib.parse import urlparse
  for s in DATA['sources']:
   self.assertIn(urlparse(s['url']).hostname,['www.niigata-u.ac.jp','www.saitama-u.ac.jp']);self.assertEqual(len(s['sha256']),64)
 def test_invalid_year_or_score_rejected(self):
  for field,value in [('year',2027)]:
   d=copy.deepcopy(DATA);d['records'][0][field]=value
   with self.assertRaises(AssertionError):validate(d,True)
  d=copy.deepcopy(DATA);d['records'][0]['common']['average']['value']=999999
  with self.assertRaises(AssertionError):validate(d,True)
class ApprovalTests(unittest.TestCase):
 def setUp(self):
  self.d=copy.deepcopy(DATA)
  for r in self.d['records']:
   for g in ['common','individual','total','admissions']:
    for m in r[g].values():
     if m['value'] is not None:m['status']='pending'
  for s in self.d['sources']:s['status']='pending'
 def test_unapproved_values_redacted(self):
  d=export(self.d,{'records':{}});self.assertTrue(all(m['value'] is None for r in d['records'] for g in ['common','individual','total','admissions'] for m in r[g].values()))
 def test_changed_record_revokes_approval(self):
  ss={s['id']:s for s in self.d['sources']};r=self.d['records'][0];h=digest(r,ss);r['common']['average']['value']+=.1;self.assertNotEqual(digest(r,ss),h)
 def test_changed_pdf_revokes_approval(self):
  ss={s['id']:s for s in self.d['sources']};r=self.d['records'][0];h=digest(r,ss);ss[r['common']['average']['source']]['sha256']='f'*64;self.assertNotEqual(digest(r,ss),h)
 def test_failed_fetch_keeps_public_file(self):
  import subprocess,tempfile
  before=(ROOT/'public/data/admissions.json').read_bytes()
  with tempfile.TemporaryDirectory() as tmp:
   p=subprocess.run([sys.executable,str(ROOT/'scripts/collect.py'),'--offline','--cache',tmp,'--out',tmp+'/candidate.json'],capture_output=True)
   self.assertNotEqual(p.returncode,0);self.assertTrue((Path(tmp)/'last-error.json').exists())
  self.assertEqual((ROOT/'public/data/admissions.json').read_bytes(),before)
if __name__=='__main__':unittest.main()
