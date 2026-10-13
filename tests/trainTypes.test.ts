import {beforeAll,describe,expect,it} from 'vitest';
import {data,getNetwork,loadNetwork,origins,parseState,serviceById} from '../src/lib/network';
import {isSlowFuxing,matchesTrainType,parseTrainType} from '../src/lib/trainTypes';
import type {PassengerService} from '../src/types';
const filters={type:'slow-fuxing',province:'',search:''} as const;
const service=(trainNumber:string,date='2026-09-11')=>({trainNumber,category:trainNumber[0],sourceUpdatedAt:date,passenger:true}) as PassengerService;

describe('160 km/h Fuxing snapshot mode',()=>{
 beforeAll(async()=>{await loadNetwork()});
 it('recognizes Xuzhou examples without treating every D/C train as a slow Fuxing',()=>{
  for(const code of ['C979','C980','D61','D121','D112','D299'])expect(isSlowFuxing(serviceById.get('svc-'+code.toLowerCase())!)).toBe(true);
  for(const code of ['G123','D315','D351','D701','D901','D1001','C2201','C3001','S1001','K123','Z5016'])expect(isSlowFuxing(service(code))).toBe(false);
  expect(isSlowFuxing({...service('D61'),category:'G'})).toBe(false);
  expect(isSlowFuxing({...service('C979'),passenger:false})).toBe(false);
  expect(isSlowFuxing(service('D61/62'))).toBe(false);
 });
 it('does not reuse present-day numbering assumptions for historic or undated services',()=>{
  expect(isSlowFuxing(service('D61','2023-09-11'))).toBe(false);
  expect(isSlowFuxing(service('C979','2021-09-11'))).toBe(false);
  expect(isSlowFuxing(service('D61',''))).toBe(false);
  expect(isSlowFuxing(service('D61','unknown'))).toBe(false);
 });
 it('retains existing filters and restores the new mode from share links',()=>{
  expect(parseState('?station=xuzhou&type=slow-fuxing&province=shaanxi&q=西安').filters).toEqual({...filters,province:'shaanxi',search:'西安'});
  for(const type of ['all','highspeed','conventional','slow-fuxing'] as const)expect(parseTrainType(type)).toBe(type);
  expect(parseTrainType('unknown')).toBe('all');expect(parseTrainType('__proto__')).toBe('all');
  expect(matchesTrainType(service('D61'),'highspeed')).toBe(true);
  expect(matchesTrainType(service('D61'),'conventional')).toBe(false);
 });
 it('keeps the entire same-service network for every independent departure, including empty origins',()=>{
  let populated=0,empty=0;
  for(const origin of origins){
   const view=getNetwork(origin.id,filters);
   const accepted=data.networks[origin.id].serviceIds.map(id=>serviceById.get(id)!).filter(isSlowFuxing);
   const expected=new Set(accepted.flatMap(s=>s.stations));expected.delete(origin.id);
   expect(new Set(view.destinations.map(s=>s.id))).toEqual(expected);
   expect(view.services.map(s=>s.id)).toEqual(accepted.map(s=>s.id));
   if(!accepted.length){empty++;expect(view.segments).toHaveLength(0);expect(view.stations.map(s=>s.id)).toEqual([origin.id]);continue}
   populated++;
   for(const destination of view.destinations)expect(view.services.some(s=>s.stations.includes(origin.id)&&s.stations.includes(destination.id))).toBe(true);
   const allowedPaths=new Set(accepted.flatMap(s=>s.segmentIds.flat()));
   expect(view.segments.every(s=>allowedPaths.has(s.id))).toBe(true);
  }
  expect(populated).toBeGreaterThan(100);expect(empty).toBeGreaterThan(100);
 },30000);
 it('synchronizes province, search, geometry and no-match statistics in the new mode',()=>{
  const all=getNetwork('xuzhou',filters),found=getNetwork('xuzhou',{...filters,province:'shaanxi',search:'西安'});
  expect(all.services.map(s=>s.trainNumber)).toContain('C979');expect(all.destinations.length).toBeGreaterThan(30);
  expect(found.destinations.some(s=>s.name==='西安')).toBe(true);
  expect(found.destinations.every(s=>s.province==='陕西'&&s.name.includes('西安'))).toBe(true);
  expect(found.segments.length).toBeGreaterThan(0);expect(found.segments.length).toBeLessThan(all.segments.length);
  const absent=getNetwork('xuzhou',{...filters,search:'不存在的车站'});
  expect(absent.destinations).toHaveLength(0);expect(absent.segments).toHaveLength(0);
  expect(absent.services.filter(s=>s.stations.some(id=>absent.destinationIds.has(id)))).toHaveLength(0);
 });
});
