import sys, unittest, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from connectCorridors import connect_corridors
from railGapRouting import RailGapRouter

def fixture(local=True):
    stations=[{'id':x,'name':x,'longitude':100+i,'latitude':30} for i,x in enumerate('abcd')]
    def service(id,stops):return {'id':id,'category':'K','stations':stops,'completeStopNames':stops,'segmentIds':[[] for _ in stops[1:]]}
    services=[service('long',['a','d'])]
    if local:services += [service('local',list('abcd'))]
    return {'stations':stations,'segments':[],'services':services,'networks':{'a':{'serviceIds':[s['id'] for s in services],'destinationIds':['d']}},'audit':{}}
class Corridors(unittest.TestCase):
    def test_long_gap_uses_short_chain_and_preserves_destinations(self):
        d=connect_corridors(fixture())
        self.assertEqual(len(d['services'][0]['segmentIds'][0]),3)
        self.assertEqual(d['networks']['a']['destinationIds'],['d'])
        self.assertEqual(d['services'][0]['stations'],['a','d'])
        self.assertTrue(all(s['schematic'] for s in d['segments']))
        self.assertTrue(any(s['geometry']['coordinates'][0]==[100,30] for s in d['segments']))
    def test_reviewed_rail_gap_routes_follow_multiple_points(self):
        root=Path(__file__).resolve().parents[1]
        source=json.loads((root/'data/raw/physical-rails.json').read_text())
        station={s['name']:s for s in json.loads((root/'src/data/network.json').read_text())['stations']}
        router=RailGapRouter(source)
        for a,b in [('哈密','吐鲁番北'),('西宁','格尔木')]:
            start=[station[a]['longitude'],station[a]['latitude']]
            end=[station[b]['longitude'],station[b]['latitude']]
            route=router.route(start,end)
            self.assertIsNotNone(route)
            self.assertEqual(route['coordinates'][0],start)
            self.assertEqual(route['coordinates'][-1],end)
            self.assertGreater(len(route['coordinates']),10)
            self.assertTrue(route['railwayNames'])
    def test_no_evidenced_corridor_leaves_gap(self):
        d=connect_corridors(fixture(False))
        self.assertEqual(d['segments'],[])
        self.assertEqual(d['audit']['remainingUnmappedIntervals'],1)
