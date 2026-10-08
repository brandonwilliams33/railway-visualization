import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from compactNetwork import compact_network

class CompactPassengerPaths(unittest.TestCase):
    def test_shared_paths_round_trip_and_preserve_service_membership(self):
        data = {'segments': [{'id': 'a'}, {'id': 'b'}], 'services': [
            {'id': 'day', 'stations': ['one', 'two'], 'segmentIds': [['a', 'b']]},
            {'id': 'night', 'stations': ['two', 'one'], 'segmentIds': [['b', 'a']]},
            {'id': 'express', 'stations': ['one', 'two'], 'segmentIds': [['a', 'b']]},
        ], 'networks': {'one': {'serviceIds': ['day', 'night', 'express'], 'railwaySegmentIds': ['a', 'b']}}}
        wire = compact_network(data)
        self.assertEqual(len(wire['segmentPaths']), 2)
        for source, encoded in zip(data['services'], wire['services']):
            restored = [[wire['segments'][i]['id'] for i in wire['segmentPaths'][path]] for path in encoded['segmentPathIndexes']]
            self.assertEqual(restored, source['segmentIds'])
            self.assertEqual(encoded['stations'], source['stations'])
        self.assertEqual(wire['networks']['one']['serviceIds'], data['networks']['one']['serviceIds'])
        self.assertNotIn('railwaySegmentIds', wire['networks']['one'])
        self.assertIn('segmentIds', data['services'][0])

    def test_invalid_segment_is_rejected_during_generation(self):
        with self.assertRaises(KeyError):
            compact_network({'segments': [], 'services': [{'segmentIds': [['missing']]}], 'networks': {}})

if __name__ == '__main__':
    unittest.main()
