"""Regression cases for long passenger intervals that previously broke or detoured."""
import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from railGapRouting import RailGapRouter
from physicalGeometry import km

class ReviewedCorridorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router=RailGapRouter(json.loads((ROOT/'data/raw/physical-rails.json').read_text()),join_km=3)
        cls.points={s['name']:[s['longitude'],s['latitude']] for s in json.loads((ROOT/'data/raw/stations.json').read_text())}

    def test_remote_gaps_follow_connected_corridors_without_long_detours(self):
        for origin,destination in [('牙克石','齐齐哈尔'),('达州','梁平'),('武威','中卫'),('南博山','莱芜东'),('南峧','黎城'),('黎城','微子镇'),('依兰','宾州'),('丽江','楚雄')]:
            with self.subTest(origin=origin,destination=destination):
                a,b=self.points[origin],self.points[destination]
                route=self.router.route(a,b)
                self.assertIsNotNone(route)
                points=route['coordinates']
                self.assertLess(km(points[0],a),.01)
                self.assertLess(km(points[-1],b),.01)
                self.assertLess(sum(km(p,q) for p,q in zip(points,points[1:])),km(a,b)*2.2+50)
        # The old route went east to Harbin (126E), then returned west.
        route=self.router.route(self.points['牙克石'],self.points['齐齐哈尔'])
        self.assertLess(max(p[0] for p in route['coordinates']),124.2)


    def test_turpan_overnight_gap_uses_other_evidenced_shared_corridors(self):
        data=json.loads((ROOT/'src/data/network.json').read_text())
        ids={s['id'] for s in data['stations'] if s['name'] in ['吐鲁番北','焉耆']}
        # Exclude the repaired interval itself: verify it can be reconstructed
        # from independently evidenced station cuts and passenger corridors.
        segments=[s for s in data['segments'] if set(s.get('coverageStationIds',[])) != ids]
        source=json.loads((ROOT/'data/raw/physical-rails.json').read_text())
        router=RailGapRouter({'edges':[*source['edges'],*segments]},join_km=3)
        a,b=self.points['吐鲁番北'],self.points['焉耆']
        route=router.route(a,b)
        self.assertIsNotNone(route)
        points=route['coordinates']
        self.assertLess(km(points[0],a),.01)
        self.assertLess(km(points[-1],b),.01)
        self.assertLess(sum(km(p,q) for p,q in zip(points,points[1:])),km(a,b)*2.2+50)

if __name__=='__main__':unittest.main()
