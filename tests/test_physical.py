import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from passengerCorridors import approved
from physicalGeometry import apply_physical

class PhysicalGeometryTests(unittest.TestCase):
    def fixture(self, connected):
        stations=[{'id':'xuzhou','name':'甲','longitude':100.,'latitude':30.},{'id':'destination','name':'乙','longitude':100.1,'latitude':30.}]
        services=[{'id':'K1','category':'K','stations':['xuzhou','destination'],'completeStopNames':['甲','乙']},{'id':'K2','category':'K','stations':['destination','xuzhou'],'completeStopNames':['乙','甲']}]
        data={'stations':stations,'services':services,'networks':{'xuzhou':{'serviceIds':['K1','K2']}},'audit':{}}
        paths=[[[100.,30.],[100.05,30.01],[100.1,30.]]] if connected else [[[100.,30.],[100.02,30.]],[[100.08,30.],[100.1,30.]]]
        source={'edges':[{'geometry':{'coordinates':cs},'family':'ordinary','railwayNames':['京沪线'],'sourceWayIds':['way/1']} for cs in paths],'sourceSnapshot':'2026-05-10','metadata':{'builtAt':'2026-10-06'}}
        return apply_physical(data,source)
    def test_excludes_freight_and_nonoperating_track_names(self):
        for name in ['大秦铁路','浩吉铁路','京沪货线','徐州动车所','京沪专用线','试验高铁',None]:self.assertFalse(approved(name))
        for name in ['京沪线','徐盐客专线','京沪高铁','辛泰线','干武线','平齐线','达万线','榆树线','榆红线']:self.assertTrue(approved(name))
    def test_unmatched_interval_never_gets_a_chord(self):
        data=self.fixture(False)
        self.assertEqual(data['segments'],[])
        self.assertEqual(data['audit']['unmatchedPhysicalIntervals'],2)
        self.assertTrue(all(s['segmentIds']==[[]] for s in data['services']))
    def test_opposite_services_share_one_physical_curve(self):
        data=self.fixture(True)
        self.assertEqual(len(data['segments']),1)
        self.assertEqual(data['services'][0]['segmentIds'],data['services'][1]['segmentIds'])
        self.assertEqual(data['segments'][0]['geometry']['coordinates'][1],[100.05,30.01])

if __name__=='__main__':unittest.main()
