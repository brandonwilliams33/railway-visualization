import {describe,it,expect} from 'vitest';
import {stationChoiceIndex,intercityIndex,origins,parseState} from '../src/lib/network';
import {buildStationChoiceIndex} from '../src/lib/stationChoiceIndex';
describe('small-station navigation',()=>{
 it('puts Xinzhuang and the independent Jinshan stops in a separate local group',()=>{
  const s=origins.find(s=>s.name==='莘庄')!,c=stationChoiceIndex.city(s.cityId),g=c.groups.find(g=>g.id==='local')!;
  expect(c.primary.map(s=>s.id)).not.toContain(s.id);
  expect(intercityIndex.memberships.has(s.id)).toBe(false);
  expect(g.sections.find(l=>l.id==='shanghai-jinshan')!.stations.map(s=>s.name)).toEqual(['莘庄','春申','新桥','车墩','叶榭','亭林','金山园区','金山卫']);
  expect(new Set(g.stations.map(s=>s.id)).size).toBe(g.stations.length);
  expect(c.primary.map(s=>s.name)).toContain('上海虹桥');
 });
 it('keeps every station reachable, with disjoint inner groups and independent city identities',()=>{
  for(const id of new Set(origins.map(s=>s.cityId))){
   const c=stationChoiceIndex.city(id),nested=c.groups.flatMap(g=>g.stations);
   expect(new Set([...c.primary,...nested].map(s=>s.id))).toEqual(new Set(c.all.map(s=>s.id)));
   expect(new Set(nested.map(s=>s.id)).size).toBe(nested.length);
   expect(c.primary.length+c.groups.length).toBeGreaterThan(0);
   for(const g of c.groups){expect(new Set(g.sections.flatMap(l=>l.stations.map(s=>s.id)))).toEqual(new Set(g.stations.map(s=>s.id)));for(const s of g.stations)expect(s.cityId).toBe(id)}
  }
 });
 it('retains busy hubs even if the old tier marks them local',()=>{
  for(const name of ['北京丰台','北京朝阳','清河','深圳坪山','福田','广州白云']){
   const s=origins.find(s=>s.name===name)!;
   expect(stationChoiceIndex.city(s.cityId).primary).toContainEqual(s);
   expect(stationChoiceIndex.groupFor(s.id)).toBeNull();
  }
 });
 it('restores local station links and rejects groups belonging to a different city',()=>{
  const s=origins.find(s=>s.name==='莘庄')!;
  expect(parseState(`?station=${s.id}`).group).toBe('local');
  expect(parseState(`?city=${s.cityId}&group=local`).group).toBe('local');
  const hub=origins.find(s=>s.name==='上海虹桥')!;
  expect(parseState(`?station=${hub.id}`).group).toBeNull();
  expect(parseState(`?station=${hub.id}&group=local`).group).toBe('local');
  expect(stationChoiceIndex.resolve(null,'local')).toBeNull();
  expect(stationChoiceIndex.resolve('missing-city','local')).toBeNull();
  expect(stationChoiceIndex.resolve(s.cityId,'unknown')).toBeNull();
 });
 it('rejects stale or wrong-city local-line references',()=>{
  const s=origins.find(s=>s.name==='莘庄')!;
  expect(()=>buildStationChoiceIndex(origins.filter(v=>v.id!==s.id),intercityIndex)).toThrow('Invalid local station reference');
  expect(()=>buildStationChoiceIndex(origins.map(v=>v.id===s.id?{...v,cityId:'suzhou'}:v),intercityIndex)).toThrow('Invalid local station reference');
 });
});
