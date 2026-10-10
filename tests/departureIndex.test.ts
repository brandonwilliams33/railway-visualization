import {describe,it,expect} from 'vitest';
import {departureIndex,origins,parseState} from '../src/lib/network';

describe('regional departure index',()=>{
 it('places every independent origin in exactly one region, province and city',()=>{
  expect(departureIndex.regions.map(r=>r.name)).toEqual(['华北','东北','华东','华中','华南','西南','西北']);
  expect(departureIndex.provinces.size).toBe(31);
  for(const origin of origins){
   const path=departureIndex.resolve({city:origin.cityId});
   expect(path.province).toBe(origin.provinceId);
   expect(departureIndex.provincesIn(path.region).some(p=>p.id===origin.provinceId)).toBe(true);
   expect(departureIndex.citiesIn(path.province).some(c=>c.id===origin.cityId)).toBe(true);
  }
  expect(departureIndex.citiesIn('jiangsu').map(c=>c.id)).toContain('suzhou');
  expect(departureIndex.citiesIn('anhui').map(c=>c.id)).toContain('anhui-suzhou');
  expect(departureIndex.citiesIn('anhui').map(c=>c.id)).not.toContain('suzhou');
 });
 it('rejects inconsistent parent selections and restores older city and station links',()=>{
  expect(parseState('?region=south&departureProvince=jiangsu').departure).toEqual({region:'south',province:null,city:null});
  expect(parseState('?region=unknown&departureProvince=jiangsu').departure).toEqual({region:null,province:null,city:null});
  expect(parseState('?region=east&departureProvince=jiangsu').departure).toEqual({region:'east',province:'jiangsu',city:null});
  expect(parseState('?city=xuzhou&region=south').departure).toEqual({region:'east',province:'jiangsu',city:'xuzhou'});
  expect(parseState('?station=xuzhou-east&city=anhui-suzhou').departure).toEqual({region:'east',province:'jiangsu',city:'xuzhou'});
  expect(parseState('?region=east&departureProvince=jiangsu&province=shaanxi').filters.province).toBe('shaanxi');
 });
});
