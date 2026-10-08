import {describe,it,expect} from 'vitest';
import {decodeNetwork} from '../src/lib/decodeNetwork';

const wire=()=>({schemaVersion:2,segments:[{id:'track-a'},{id:'track-b'}],segmentPaths:[[0,1],[1,0]],services:[
 {id:'day',stations:['origin','destination'],segmentPathIndexes:[0]},
 {id:'night',stations:['destination','origin'],segmentPathIndexes:[1]},
 {id:'express',stations:['origin','destination'],segmentPathIndexes:[0]},
]});
describe('shared service interval storage',()=>{
 it('restores each service interval and its direction without changing separate station identities',()=>{
  const data=decodeNetwork(wire());
  expect(data.services.map(s=>s.segmentIds)).toEqual([[['track-a','track-b']],[['track-b','track-a']],[['track-a','track-b']]]);
  expect(data.services[0].stations).toEqual(['origin','destination']);
  expect(data.services[1].stations).toEqual(['destination','origin']);
  expect(data.services[0].segmentIds[0]).toBe(data.services[2].segmentIds[0]);
 });
 it('rejects broken references instead of silently leaving a disconnected line',()=>{
  const missingSegment=wire();missingSegment.segmentPaths[0]=[9];
  expect(()=>decodeNetwork(missingSegment)).toThrow('无效区段');
  const missingPath=wire();missingPath.services[0].segmentPathIndexes=[9];
  expect(()=>decodeNetwork(missingPath)).toThrow('无效路径');
 });
});
