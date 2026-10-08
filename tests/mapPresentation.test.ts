import {describe,it,expect} from 'vitest';
import {corridorLines,pathLineIds,visibleStations} from '../src/lib/mapPresentation';
import type {RailwaySegment,Station} from '../src/types';
const segment=(id:string,coordinates:number[][]):RailwaySegment=>({id,coverageStationIds:[],railwayNames:[],osmSourceId:'source',geometrySource:'OSM',routingConfidence:'inferred-corridor',family:'ordinary',geometry:{type:'LineString',coordinates},geometryAccuracy:'approximate',passengerCategories:['K'],serviceIds:['K1']});
describe('map presentation never defines passenger reachability',()=>{
 it('merges overlapping opposite-direction ink and preserves source references',()=>{const path=[[116,34],[117,34],[118,34]],lines=corridorLines([segment('a',path),segment('b',[...path].reverse())],5);expect(lines).toHaveLength(1);expect(new Set(lines[0].segmentIds)).toEqual(new Set(['a','b']))});
 it('does not join distant disconnected intervals into a stop-to-stop chord',()=>{const lines=corridorLines([segment('luoyang',[[112.4,34.7],[112.8,34.7]]),segment('chengdu',[[104,30.6],[104.4,30.6]])],5);expect(lines).toHaveLength(2);for(const l of lines){const longitudes=l.positions.map(p=>p[1]);expect(Math.max(...longitudes)-Math.min(...longitudes)).toBeLessThan(1)}});
 it('keeps close-up lines in a shared corridor while preserving endpoints',()=>{const s=segment('a',[[116,34],[116.2,34.1],[116.3,34]]);const hub={id:'hub',latitude:34,longitude:116} as Station,end={id:'end',latitude:34,longitude:116.3} as Station;const lines=corridorLines([s],8,[hub,end],'hub');expect(lines.some(l=>l.positions.some(p=>p[0]===34&&p[1]===116))).toBe(true);expect(lines.some(l=>l.positions.some(p=>p[0]===34&&p[1]===116.3))).toBe(true)});
 it('shows major stops nationally and every separate stop after zooming in',()=>{const stations=Array.from({length:60},(_,i)=>({id:`s${i}`,longitude:117+i*.001,latitude:34,name:`站${i}`,city:'城市',province:'省',provinceId:'p',isHub:i===0,major:false,coordinateSource:'test'} as Station));const visible=visibleStations(stations,5,'s0','s59');expect(visible.length).toBeLessThan(stations.length);expect(visible.map(s=>s.id)).toContain('s59');expect(visible.map(s=>s.id)).toContain('s0');expect(visibleStations(stations,6,'s0',null)).toHaveLength(60);expect(visibleStations(stations,7,'s0',null)).toHaveLength(60)});
});

describe('station anchors and complete visible paths',()=>{
 it('keeps a station on the joined line instead of replacing it with a cell average',()=>{const station={id:'anchor',name:'站',latitude:34,longitude:117,major:true,isHub:true,city:'',province:'',provinceId:'',coordinateSource:''};const lines=corridorLines([segment('a',[[116.8,34],[117,34]]),segment('b',[[117,34],[117.2,34]])],5,[station]);expect(lines.filter(l=>l.positions.some(p=>p[0]===34&&p[1]===117)).length).toBeGreaterThanOrEqual(1)});
 it('keeps nearby distinct stations as separate reachable nodes in one corridor cell',()=>{const hub={id:'hub',name:'起点',latitude:34,longitude:117,major:true,isHub:true,city:'',province:'',provinceId:'',coordinateSource:''} as Station;const north={...hub,id:'north',name:'北站',longitude:117.02,isHub:false};const south={...hub,id:'south',name:'南站',longitude:117.04,isHub:false};const stops=[hub,north,south];expect(visibleStations(stops,6,hub.id,null).map(s=>s.id)).toEqual(['hub','north','south']);const lines=corridorLines([segment('track',[[117,34],[117.02,34],[117.04,34]])],6,stops,hub.id);for(const stop of [north,south])expect(pathLineIds(lines,hub,stop).size).toBeGreaterThan(0)});
});

describe('shared corridor skeleton',()=>{
 it('chooses one route through parallel alternatives and highlights reachability',()=>{
  const hub={id:'hub',name:'起点',longitude:116,latitude:34,isHub:true,major:true,city:'',province:'',provinceId:'',coordinateSource:''} as Station;
  const end={...hub,id:'end',name:'终点',longitude:117};
  const first=segment('north',[[116,34],[116.5,34.2],[117,34]]);
  const second=segment('south',[[116,34],[116.5,33.8],[117,34]]);
  const lines=corridorLines([first,second],8,[hub,end],'hub');
  expect(lines.length).toBe(pathLineIds(lines,hub,end).size);
  expect(pathLineIds(lines,hub,end).size).toBeGreaterThan(0);
 });
});
