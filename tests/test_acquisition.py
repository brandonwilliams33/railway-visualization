import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from acquireJiangsu import parse_service

def page(rows):
    return '<p>列车数据更新时间：2026-09-11 02:05:13</p><table>'+''.join('<tr>'+''.join(f'<td>{cell}</td>' for cell in row)+'</tr>' for row in rows)+'</table>'
def row(number,name,duration):return [str(number),name,'D123','00:00','00:01',duration,'1分钟']

class AcquisitionEvidence(unittest.TestCase):
    def test_overnight_elapsed_time_is_not_reset_at_midnight(self):
        record=parse_service('D123',page([row(1,'南京',''),row(2,'成都','26小时15分钟')]))
        self.assertEqual(record['elapsedMinutes'],[0,1575])
        self.assertTrue(record['sourceValidation']['elapsedTimeMonotonic'])
    def test_time_regression_is_quarantined_and_missing_rows_are_rejected(self):
        record=parse_service('D123',page([row(1,'南京',''),row(2,'洛阳','10小时'),row(3,'成都','3小时')]))
        self.assertFalse(record['sourceValidation']['elapsedTimeMonotonic'])
        with self.assertRaises(ValueError):parse_service('D123',page([row(1,'南京',''),row(3,'成都','26小时')]))

if __name__=='__main__':unittest.main()
