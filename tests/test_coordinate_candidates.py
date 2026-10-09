"""Exact Chinese aliases must not confuse foreign and domestic stations."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from resolveStationCoordinates import group_osm_candidates

class CoordinateIdentityTests(unittest.TestCase):
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
