"""Exact Chinese aliases must not confuse foreign and domestic stations."""
import sys,unittest,json,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from resolveStationCoordinates import group_osm_candidates,apply_identity_reviews

class CoordinateIdentityTests(unittest.TestCase):
    def test_reviewed_homonyms_keep_other_objects_separate(self):
        raw=Path(__file__).resolve().parents[1]/'data/raw'
        reviews=json.loads((raw/'homonym-coordinate-reviews.json').read_text())
        registry={s['name']:s for s in json.loads((raw/'stations.json').read_text())}
        objects={f"{e['type']}/{e['id']}":e for e in json.loads((raw/'verified-coordinate-objects.json').read_text())['elements']}
        expected={'桃山':'node/9137876527','四方台':'node/2344167674','三家子':'node/9169253672'}
        for review in reviews:
            self.assertEqual(review['selectedObject'],expected[review['name']])
            chosen=objects[review['selectedObject']]
            station=registry[review['name']]
            self.assertEqual([station['longitude'],station['latitude']],[chosen['lon'],chosen['lat']])
            self.assertEqual(station['coordinateSource'],'https://www.openstreetmap.org/'+review['selectedObject'])
            for other in review['otherObjectsRetained']:
                self.assertIn(other,objects)
                self.assertGreater(abs(objects[other]['lon']-chosen['lon'])+abs(objects[other]['lat']-chosen['lat']),.04)

    def test_administrative_review_preserves_station_identity_and_position(self):
        raw=Path(__file__).resolve().parents[1]/'data/raw'
        registry=json.loads((raw/'stations.json').read_text())
        reviews=json.loads((raw/'station-identity-reviews.json').read_text())['stations']
        before={s['name']:(s['id'],s['longitude'],s['latitude']) for s in registry}
        apply_identity_reviews(registry,reviews)
        apply_identity_reviews(registry,reviews)  # Re-running the resolver is safe.
        for station in registry:
            self.assertEqual(before[station['name']],(station['id'],station['longitude'],station['latitude']))
        for review in reviews:
            station=next(s for s in registry if s['name']==review['name'])
            self.assertEqual(station['province'],'黑龙江')
            self.assertEqual(station['geographicProvince'],'内蒙古')
        changed=copy.deepcopy(reviews);changed[0]['stationId']='a-different-station'
        with self.assertRaises(AssertionError):apply_identity_reviews(registry,changed)

    def test_foreign_alias_cannot_hide_the_independent_sichuan_station(self):
        # Original OSM identities: Anju in DPRK and Anzhou in Sichuan.
        foreign={'type':'node','id':4834645005,'lat':39.6238018,'lon':125.6523328,'tags':{'name':'안주','name:zh':'安州'}}
        domestic={'type':'node','id':10574674380,'lat':31.4652016,'lon':104.2339996,'tags':{'name':'安州'}}
        province_at=lambda point:'四川' if 100<point[0]<108 and 26<point[1]<34 else None
        result=group_osm_candidates([foreign,domestic],province_at,{'安州':{'province':'四川'}})
        self.assertEqual([e['id'] for e,_ in result['安州']],[10574674380])
        self.assertEqual(result['安州'][0][1],[104.2339996,31.4652016])
        # An exact Chinese name in a conflicting province stays unaccepted.
        self.assertNotIn('安州',group_osm_candidates([domestic],province_at,{'安州':{'province':'湖南'}}))

if __name__=='__main__':unittest.main()
