import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validateTimetable import impossible_intervals

class TimetablePlausibility(unittest.TestCase):
    def test_rejects_a_mixed_tourist_table_that_jumps_from_linyi_to_lijiang_in_minutes(self):
        stations={'临沂':{'latitude':35.03,'longitude':118.34},'丽江':{'latitude':26.81,'longitude':100.24}}
        r={'category':'OTHER','stopNames':['临沂','丽江'],'elapsedMinutes':[554,583]}
        self.assertEqual(len(impossible_intervals(r,stations)),1)
        r['elapsedMinutes']=[554,554+30*60]
        self.assertEqual(impossible_intervals(r,stations),[])

    def test_preserves_fast_trains_and_checks_across_an_unlocated_intermediate_stop(self):
        stations={'徐州东':{'latitude':34.267,'longitude':117.31},'南京南':{'latitude':31.969,'longitude':118.798}}
        r={'category':'G','stopNames':['徐州东','未定位站','南京南'],'elapsedMinutes':[0,30,75]}
        self.assertEqual(impossible_intervals(r,stations),[])
        r['elapsedMinutes']=[0,2,5]
        self.assertEqual(len(impossible_intervals(r,stations)),1)

if __name__=='__main__':unittest.main()
