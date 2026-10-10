import {describe,it,expect} from 'vitest';
import manifest from '../src/data/intercity-groups.json';
import {intercityIndex,origins,parseState} from '../src/lib/network';
import {buildIntercityIndex} from '../src/lib/intercityIndex';
describe('verified intercity navigation',()=>{
 it('keeps Shenzhen hubs beside the group and four independent airport-line stops inside',()=>{
  const id=origins.find(s=>s.name==='深圳北')!.cityId,c=intercityIndex.city(id);
  expect(c.intercity.map(s=>s.name).sort()).toEqual(['沙井西','深圳机场','深圳机场北','福海西'].sort());
  expect(c.primary.map(s=>s.name)).toContain('深圳北');
  expect(c.primary.map(s=>s.name)).not.toContain('深圳机场');
  expect(new Set(c.intercity.map(s=>s.id)).size).toBe(4);
 });
 it('accounts for every original station without duplication inside a city group',()=>{
  for(const id of new Set(origins.map(s=>s.cityId))){
   const c=intercityIndex.city(id),inside=c.sections.flatMap(l=>l.stations.map(s=>s.id));
   expect(new Set(inside).size).toBe(inside.length);
   expect(new Set([...c.primary,...c.intercity].map(s=>s.id))).toEqual(new Set(c.all.map(s=>s.id)));
   for(const s of c.intercity)expect(s.cityId).toBe(id);
  }
  for(const l of manifest.lines){expect(l.sources.length).toBeGreaterThan(0);expect(l.sources.every(s=>s.startsWith('https://'))).toBe(true)}
 });
 it('restores group links, derives old station links and rejects unrelated city groups',()=>{
  const s=origins.find(s=>s.name==='深圳机场')!;
  expect(parseState(`?city=${s.cityId}&group=intercity`).group).toBe('intercity');
  expect(parseState(`?station=${s.id}`).group).toBe('intercity');
  expect(parseState('?city=xuzhou&group=intercity').group).toBeNull();
  expect(parseState('?group=intercity').group).toBeNull();
  expect(parseState(`?city=${s.cityId}&group=unknown`).group).toBeNull();
 });
 it('rejects stale or homonymous station references rather than silently grouping them',()=>{
  const id=manifest.lines[0].stations[0].stationId;
  expect(()=>buildIntercityIndex(origins.filter(s=>s.id!==id))).toThrow('Invalid intercity reference');
  expect(()=>buildIntercityIndex(origins.map(s=>s.id===id?{...s,provinceId:'hunan'}:s))).toThrow('Invalid intercity reference');
 });
 it('places Guangzhou Changlong in Guangzhou and keeps Zhuhai Changlong independent',()=>{
  const a=origins.find(s=>s.name==='广州长隆')!,b=origins.find(s=>s.name==='珠海长隆')!;
  expect(a.city).toBe('广州');expect(b.city).toBe('珠海');expect(a.id).not.toBe(b.id);
  expect(intercityIndex.city(a.cityId).intercity.map(s=>s.id)).toContain(a.id);
  expect(intercityIndex.city(b.cityId).intercity.map(s=>s.id)).not.toContain(a.id);
 });
 it('supports cross-province lines while keeping city and station identities',()=>{
  const l=manifest.lines.find(l=>l.id==='huning')!;
  expect(l.provinceIds).toEqual(['jiangsu','shanghai']);
  for(const name of ['苏州新区','苏州园区','安亭北','南翔北']){
   const s=origins.find(s=>s.name===name)!;
   expect(l.stations.some(e=>e.stationId===s.id)).toBe(true);
   expect(intercityIndex.city(s.cityId).intercity).toContainEqual(s);
   expect(intercityIndex.city(s.cityId).primary).not.toContainEqual(s);
  }
  const a=origins.find(s=>s.name==='大兴机场')!;
  expect(a.provinceId).toBe('hebei');expect(a.city).toBe('廊坊');
  expect(intercityIndex.city('beijing').intercity.map(s=>s.id)).not.toContain(a.id);
 });
 it('keeps shared hubs in the outer list unless the link explicitly retains the group',()=>{
  for(const name of ['苏州','上海虹桥','北京南','广州白云','惠州北']){
   const s=origins.find(s=>s.name===name)!;
   expect(intercityIndex.city(s.cityId).primary).toContainEqual(s);
   expect(intercityIndex.groupFor(s.id)).toBeNull();
   expect(parseState(`?station=${s.id}`).group).toBeNull();
   expect(parseState(`?station=${s.id}&group=intercity`).group).toBe('intercity');
  }
  const s=origins.find(s=>s.name==='苏州新区')!;
  expect(parseState(`?station=${s.id}`).group).toBe('intercity');
 });
 it('does not classify neighbouring stations or airports merely by name',()=>{
  for(const name of ['安亭西','太仓南','深圳北','双流机场']){
   const s=origins.find(s=>s.name===name)!;
   expect(intercityIndex.memberships.has(s.id)).toBe(false);
   expect(intercityIndex.city(s.cityId).primary).toContainEqual(s);
  }
 });
});
