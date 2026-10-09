import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from serviceScope import out_of_scope_stops
class ServiceScopeTests(unittest.TestCase):
 def test_cross_border_rule_does_not_exclude_a_domestic_homonym(self):
  rule={'trainNumbers':['D88'],'sourceUpdatedAt':'2026-09-11','requiredStops':['磨憨','万象'],'outsideStationNames':['万象','万荣']}
  record={'trainNumber':'D88','sourceUpdatedAt':'2026-09-11','stopNames':['万象','万荣','磨憨','昆明南']}
  self.assertEqual(out_of_scope_stops(record,[rule]),{'万象','万荣'})
  self.assertEqual(out_of_scope_stops({**record,'stopNames':['万荣','北京']},[rule]),set())
  self.assertEqual(out_of_scope_stops({**record,'sourceUpdatedAt':'2026-10-01'},[rule]),set())
  self.assertEqual(record['stopNames'],['万象','万荣','磨憨','昆明南'])
if __name__=='__main__':unittest.main()
