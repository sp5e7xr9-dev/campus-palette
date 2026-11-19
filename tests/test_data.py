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
  config=json.loads((ROOT/'scripts/universities.json').read_text())
  allowed={u['id']:u.get('allowedHosts',[urlparse(u['officialUrl']).hostname]) for u in config}
  for s in DATA['sources']:
   self.assertIn(urlparse(s['url']).hostname,allowed[s['university']]);self.assertEqual(len(s['sha256']),64)
 def test_tohoku_faculty_averages_keep_weighted_basis_and_year(self):
  rs=[r for r in DATA['records'] if r['university']=='tohoku'];self.assertEqual(len(rs),12)
  for r in rs:
   self.assertIn('学部一括公表',r['department'])
   for section in ['common','individual','total']:
    self.assertIsNotNone(r[section]['average']['value']);self.assertIsNone(r[section]['minimum']['value']);self.assertIsNone(r[section]['maximum']['value'])
  r=next(r for r in rs if r['year']==2024 and r['faculty']=='理学部' and r['selection']=='一般選抜前期');self.assertEqual(r['total']['full']['value'],1250)
  r=next(r for r in rs if r['year']==2026 and r['faculty']=='理学部' and r['selection']=='一般選抜前期');self.assertEqual(r['total']['full']['value'],2350)
 def test_utsunomiya_book_year_is_not_admission_year(self):
  rs=[r for r in DATA['records'] if r['university']=='utsunomiya' and r['year']==2026];self.assertEqual(len(rs),24)
  r=next(r for r in rs if r['faculty']=='データサイエンス経営学部' and r['selection']=='一般選抜前期')
  self.assertEqual(r['year'],2026);self.assertEqual(r['common']['average']['value'],670.7);self.assertEqual(r['individual']['average']['value'],264.1)
  r=next(r for r in rs if r['faculty']=='データサイエンス経営学部' and r['selection']=='一般選抜後期')
  self.assertIsNone(r['common']['average']['value']);self.assertEqual(r['common']['average']['status'],'unavailable')
 def test_rechecked_historical_values_and_reorganizations(self):
  for y,average,full in [(2024,917.72,1260),(2025,1000.78,1310)]:
   r=find('tmu',y,'人文社会学部','人間社会学科');self.assertEqual(r['total']['average']['value'],average);self.assertEqual(r['total']['full']['value'],full)
  for y,average,full in [(2024,610.9,900),(2025,687.6,1000)]:
   r=find('utsunomiya',y,'データサイエンス経営学部','データサイエンス経営学科');self.assertEqual(r['common']['average']['value'],average);self.assertEqual(r['common']['full']['value'],full)
  self.assertFalse(any(r['university']=='utsunomiya' and r['year']==2024 and r['department']=='森林科学科' and r['selection']=='一般選抜後期' for r in DATA['records']))
  self.assertTrue(any(r['university']=='utsunomiya' and r['year']==2025 and r['department']=='森林科学科' and r['selection']=='一般選抜後期' for r in DATA['records']))
  for y,avg in [(2024,827.57),(2025,1647.29),(2026,1608.74)]:
   r=next(r for r in DATA['records'] if r['university']=='tohoku' and r['year']==y and r['faculty']=='理学部' and r['selection']=='一般選抜前期')
   self.assertEqual(r['total']['average']['value'],avg)
  r=find('toyaku',2024,'生命科学部','分子生命科学科','一般選抜A方式I期');self.assertEqual(r['common']['average']['value'],420);self.assertIsNone(r['individual']['average']['value']);self.assertEqual(r['admissions']['accepted']['value'],78)
 def test_obihiro_changed_weights(self):
  for year,full in [(2024,1050),(2025,1110),(2026,1110)]:
   self.assertEqual(find('obihiro',year,'畜産学部','共同獣医学課程')['total']['full']['value'],full)
 def test_chiba_does_not_invent_component_averages(self):
  r=find('chiba',2026,'看護学部','看護学科')
  self.assertEqual(r['total']['average']['value'],888)
  self.assertEqual(r['common']['full']['value'],475);self.assertIsNone(r['common']['average']['value'])
  self.assertEqual(r['individual']['full']['value'],900);self.assertIsNone(r['individual']['average']['value'])
 def test_hirosaki_education_mapping_and_physical_page(self):
  r=find('hirosaki',2026,'教育学部','養護教諭養成課程')
  self.assertEqual(r['total']['average']['value'],901.8)
  family=find('hirosaki',2026,'教育学部','学校教育教員養成課程初等中等教育専攻中学校コース家庭科専修')
  self.assertIsNone(family['total']['average']['value'])
  self.assertEqual(family['total']['average']['status'],'unavailable')
  self.assertFalse(any(r['university']=='hirosaki' and r['year']==2026 and any(x in r['department'] for x in ['音楽専修','美術専修','保健体育専修','技術専修']) for r in DATA['records']))
  s=next(s for s in DATA['sources'] if s['id']==r['total']['average']['source']);self.assertEqual(s['page'],5)
 def test_unweighted_common_is_not_total_weight(self):
  r=find('hirosaki',2026,'人文社会科学部','文化創生課程')
  self.assertEqual(r['common']['full']['basis'],'unweighted');self.assertEqual(r['common']['full']['value'],900)
  self.assertEqual(r['total']['full']['value'],1500)
 def test_miyagi_faculty_scope_and_no_invented_total(self):
  rs=[r for r in DATA['records'] if r['university']=='miyagi'];self.assertEqual(len(rs),6)
  for r in rs:self.assertTrue(r['faculty'].endswith('学群'));self.assertTrue(all(m['value'] is None for m in r['total'].values()))
  r=next(r for r in rs if r['faculty']=='看護学群' and r['selection']=='一般選抜前期')
  self.assertEqual(r['common']['average']['value'],594.2);self.assertEqual(r['individual']['average']['value'],159.6)
 def test_tmu_suppression_and_no_invented_actual_ratio(self):
  r=find('tmu',2026,'人文社会学部','人間社会学科','一般選抜後期')
  self.assertIsNone(r['total']['minimum']['value']);self.assertEqual(r['total']['average']['value'],1016.19)
  self.assertIsNone(r['admissions']['actualRatio']['value'])
 def test_toyaku_method_classification_and_context(self):
  r=find('toyaku',2026,'生命科学部','分子生命科学科','一般選抜A方式I期')
  self.assertEqual(r['common']['average']['value'],446.7);self.assertIsNone(r['total']['average']['value'])
  self.assertEqual(r['common']['minimum']['value'],384)
  self.assertIn('contextSource',r['common']['average'])
  r=find('toyaku',2026,'生命科学部','分子生命科学科','一般選抜B方式')
  self.assertEqual(r['individual']['average']['value'],218.9);self.assertIn('得点補正',r['note'])
 def test_fukushima_partial_year_preserved(self):
  r=find('fukushima',2025,'人間発達文化学類','教育実践コース')
  self.assertEqual(r['total']['minimum']['value'],769.2);self.assertIsNone(r['total']['average']['value'])
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
 def test_changed_score_basis_or_context_revokes_approval(self):
  ss={s['id']:s for s in self.d['sources']}
  r=next(r for r in self.d['records'] if r['university']=='hirosaki');h=digest(r,ss)
  r['common']['full']['basis']='weighted';self.assertNotEqual(digest(r,ss),h)
  r=next(r for r in self.d['records'] if r['university']=='toyaku');h=digest(r,ss)
  ss[r['common']['average']['contextSource']]['sha256']='e'*64;self.assertNotEqual(digest(r,ss),h)
 def test_failed_fetch_keeps_public_file(self):
  import subprocess,tempfile
  before=(ROOT/'public/data/admissions.json').read_bytes()
  with tempfile.TemporaryDirectory() as tmp:
   p=subprocess.run([sys.executable,str(ROOT/'scripts/collect.py'),'--offline','--cache',tmp,'--out',tmp+'/candidate.json'],capture_output=True)
   self.assertNotEqual(p.returncode,0);self.assertTrue((Path(tmp)/'last-error.json').exists())
  self.assertEqual((ROOT/'public/data/admissions.json').read_bytes(),before)
if __name__=='__main__':unittest.main()
