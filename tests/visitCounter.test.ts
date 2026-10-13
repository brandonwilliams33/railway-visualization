import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest';
import {canCountVisits,parseVisitCount} from '../src/lib/visitCounter';

describe('cumulative website visitors',()=>{
 beforeEach(()=>{vi.resetModules();vi.useFakeTimers()});
 afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals()});
 function runtime(hostname='railbound.github.io',protocol='https:'){
  const scope:Record<string,unknown>={location:{hostname,protocol,search:'?station=xuzhou&q=私人搜索'}};
  const script={src:'',referrerPolicy:'',async:false,onerror:null as null|(()=>void),remove:vi.fn()};
  const append=vi.fn();
  vi.stubGlobal('window',scope);
  vi.stubGlobal('document',{createElement:()=>script,head:{appendChild:append}});
  const respond=(payload:unknown)=>{const key=new URL(script.src).searchParams.get('jsonpCallback')!;(scope[key] as (data:unknown)=>void)(payload)};
  return{script,append,respond};
 }
 it('excludes local previews while allowing HTTPS Pages and custom domains',()=>{
  for(const hostname of ['localhost','127.0.0.1','192.168.1.2','[::1]','demo.local','demo.localhost','demo.test','demo.invalid',''])expect(canCountVisits({hostname,protocol:'https:'})).toBe(false);
  expect(canCountVisits({hostname:'railbound.github.io',protocol:'https:'})).toBe(true);
  expect(canCountVisits({hostname:'railbound.cn',protocol:'https:'})).toBe(true);
  expect(canCountVisits({hostname:'railbound.cn',protocol:'http:'})).toBe(false);
 });
 it('validates remote data and keeps large totals exact',()=>{
  expect(parseVisitCount({site_uv:12345})).toBe('12,345');
  expect(parseVisitCount({site_uv:'9007199254740993'})).toBe('9,007,199,254,740,993');
  expect(parseVisitCount({site_uv:0})).toBe('0');
  for(const site_uv of [-1,1.5,NaN,Infinity,9007199254740993,'<img src=x onerror=alert(1)>','1,234','1e6','',null,{},'1'.repeat(25)])expect(parseVisitCount({site_uv})).toBeNull();
  expect(parseVisitCount({site_uv:42,site_pv:1000})).toBe('42');
  expect(parseVisitCount({site_uv:42,site_pv:1001})).toBe('42');
  expect(parseVisitCount(null)).toBeNull();expect(parseVisitCount({site_pv:42,page_pv:42})).toBeNull();
 });
 it('counts once across repeated subscribers and never sends app search or station data',async()=>{
  const env=runtime();const {loadVisitCount}=await import('../src/lib/visitCounter');
  const first=loadVisitCount(),second=loadVisitCount();
  expect(first).toBe(second);expect(env.append).toHaveBeenCalledTimes(1);
  expect(env.script.referrerPolicy).toBe('origin');
  expect(new URL(env.script.src).origin).toBe('https://busuanzi.ibruce.info');
  expect([...new URL(env.script.src).searchParams.keys()]).toEqual(['jsonpCallback']);
  expect(env.script.src).not.toContain('xuzhou');
  env.respond({site_uv:42,site_pv:1000});expect(await first).toEqual({status:'ready',count:'42'});
  expect(await loadVisitCount()).toEqual({status:'ready',count:'42'});expect(env.append).toHaveBeenCalledTimes(1);
 });
 it('does not contact the provider during a local preview',async()=>{
  const env=runtime('localhost');const {loadVisitCount}=await import('../src/lib/visitCounter');
  expect(await loadVisitCount()).toEqual({status:'local'});expect(env.append).not.toHaveBeenCalled();
 });
 it('reports network errors instead of fabricating a zero count',async()=>{
  const env=runtime();const {loadVisitCount}=await import('../src/lib/visitCounter');
  const pending=loadVisitCount();env.script.onerror!();
  expect(await pending).toEqual({status:'unavailable'});expect(env.script.remove).toHaveBeenCalled();
 });
 it('ignores malformed and late responses after timeout',async()=>{
  const env=runtime();const {loadVisitCount}=await import('../src/lib/visitCounter');
  const pending=loadVisitCount();vi.advanceTimersByTime(8000);
  expect(await pending).toEqual({status:'unavailable'});
  expect(()=>env.respond({site_uv:100})).not.toThrow();
  expect(await loadVisitCount()).toEqual({status:'unavailable'});expect(env.append).toHaveBeenCalledTimes(1);
 });
 it('rejects page-view totals when the visitor total is missing',async()=>{
  const env=runtime();const {loadVisitCount}=await import('../src/lib/visitCounter');
  const pending=loadVisitCount();env.respond({site_pv:500,page_pv:100});expect(await pending).toEqual({status:'unavailable'});
 });
});
