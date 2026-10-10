import unittest, sys, tempfile, json
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from acquireJiangsu import parse_service

def page(rows):
    return '<p>列车数据更新时间：2026-09-11 02:05:13</p><table>'+''.join('<tr>'+''.join(f'<td>{cell}</td>' for cell in row)+'</tr>' for row in rows)+'</table>'
def row(number,name,duration):return [str(number),name,'D123','00:00','00:01',duration,'1分钟']

class AcquisitionEvidence(unittest.TestCase):
    def test_jilin_city_keeps_nested_catalogue_when_province_code_matches(self):
        import acquireCity
        catalogue='<a href="/jilin/jilin/">吉林</a><a href="/jilin/jilin/jilin.html">吉林站</a><a href="/jilin/jilin/jiaohe.html">蛟河站</a>'
        with tempfile.TemporaryDirectory() as directory:
            raw=Path(directory)
            with patch.object(acquireCity,'RAW',raw),patch.object(acquireCity,'services',return_value={}),patch.object(acquireCity,'fetch',return_value=page([])):
                acquireCity.acquire('jilin','jilin','吉林',catalogue)
            stations=json.loads((raw/'city-jilin-jilin-station-index.json').read_text())
            self.assertEqual({s['name'] for s in stations},{'吉林','蛟河'})
            self.assertTrue(all(s['sourceUrl'].startswith('https://www.crecc.com/jilin/jilin/') for s in stations))
            self.assertTrue((raw/'city-jilin-jilin-acquisition.json').exists())

    def test_overnight_elapsed_time_is_not_reset_at_midnight(self):
        record=parse_service('D123',page([row(1,'南京',''),row(2,'成都','26小时15分钟')]))
        self.assertEqual(record['elapsedMinutes'],[0,1575])
        self.assertTrue(record['sourceValidation']['elapsedTimeMonotonic'])
    def test_time_regression_is_quarantined_and_missing_rows_are_rejected(self):
        record=parse_service('D123',page([row(1,'南京',''),row(2,'洛阳','10小时'),row(3,'成都','3小时')]))
        self.assertFalse(record['sourceValidation']['elapsedTimeMonotonic'])
        with self.assertRaises(ValueError):parse_service('D123',page([row(1,'南京',''),row(3,'成都','26小时')]))

if __name__=='__main__':unittest.main()
