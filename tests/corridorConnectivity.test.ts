import {beforeAll,describe,it,expect} from 'vitest';
import {loadNetwork,getNetwork,data} from '../src/lib/network';
import {corridorLines,visibleStations} from '../src/lib/mapPresentation';
beforeAll(loadNetwork);
describe('real network regression checks',()=>{
 it('connects Xuzhou to Chengdu West in the actual overview drawing',()=>{
  const v=getNetwork('xuzhou',{type:'all',province:'',search:''});
  const target=v.stations.find(s=>s.name==='成都西')!;
  const stations=visibleStations(v.stations,5,'xuzhou',target.id);
  const lines=corridorLines(v.segments,5,stations);
  const key=(p:number[])=>p.map(c=>c.toFixed(6)).join(',');
  const adj=new Map<string,Set<string>>();
  for(const l of lines){const a=key(l.positions[0]),b=key(l.positions.at(-1)!);if(!adj.has(a))adj.set(a,new Set());if(!adj.has(b))adj.set(b,new Set());adj.get(a)!.add(b);adj.get(b)!.add(a)}
  const start=key([v.hubStation.latitude,v.hubStation.longitude]),end=key([target.latitude,target.longitude]);
  const seen=new Set([start]),queue=[start];for(const n of queue)for(const next of adj.get(n)||[])if(!seen.has(next)){seen.add(next);queue.push(next)}
  expect(seen.has(end)).toBe(true);
 });
 it('quarantines the mixed D111 table rather than drawing Luoyang–Chengdu from it',()=>{expect(data.audit.invalidTimingServices).toContain('D111');expect(data.services.some(s=>s.trainNumber==='D111')).toBe(false)});
 it('uses multi-point geometry instead of long schematic chords',()=>{for(const s of data.segments.filter(s=>s.schematic))for(const [a,b] of s.geometry.coordinates.slice(1).map((p,i)=>[s.geometry.coordinates[i],p])){const km=Math.hypot((a[0]-b[0])*Math.cos((a[1]+b[1])/2*Math.PI/180),(a[1]-b[1]))*111.195;expect(km).toBeLessThanOrEqual(180.001)}});
});

describe('whole-map connectivity audit',()=>{
 for(const hub of ['xuzhou','xuzhou-east'] as const)for(const type of ['all','highspeed','conventional'] as const)for(const zoom of [5,6,7,8])it(`${hub} ${type} at zoom ${zoom}: every shown station joins its departure hub`,()=>{
  const view=getNetwork(hub,{type,province:'',search:''});
  const markers=visibleStations(view.stations,zoom,hub,null);
  const lines=corridorLines(view.segments,zoom,markers);
  const key=(p:number[])=>p.map(v=>v.toFixed(8)).join(',');
  const graph=new Map<string,Set<string>>();
  for(const line of lines){const points=line.positions;const a=key(points[0]),b=key(points.at(-1)!);if(!graph.has(a))graph.set(a,new Set());if(!graph.has(b))graph.set(b,new Set());graph.get(a)!.add(b);graph.get(b)!.add(a)}
  const start=key([view.hubStation.latitude,view.hubStation.longitude]);
  const seen=new Set([start]),queue=[start];for(const n of queue)for(const next of graph.get(n)||[])if(!seen.has(next)){seen.add(next);queue.push(next)}
  const isolated=markers.filter(s=>!seen.has(key([s.latitude,s.longitude]))).map(s=>s.name);
  expect(isolated).toEqual([]);
 });
});

it('checks every published service interval for a continuous drawn route',()=>{
 const segments=new Map(data.segments.map(s=>[s.id,s]));
 const station=new Map(data.stations.map(s=>[s.id,s]));
 const checked=new Set<string>();let count=0;
 const key=(c:number[])=>c.map(n=>n.toFixed(8)).join(',');
 for(const service of data.services)for(let i=0;i<service.segmentIds.length;i++){
  const ids=service.segmentIds[i];
  expect(ids.length,`${service.trainNumber} interval ${i} missing geometry`).toBeGreaterThan(0);
  const [a,b]=service.stations.slice(i,i+2);
  const signature=`${a}|${b}|${ids.slice().sort().join(',')}`;
  if(checked.has(signature))continue;checked.add(signature);count++;
  const graph=new Map<string,Set<string>>();
  for(const id of ids){const cs=segments.get(id)!.geometry.coordinates;const p=key(cs[0]),q=key(cs.at(-1)!);if(!graph.has(p))graph.set(p,new Set());if(!graph.has(q))graph.set(q,new Set());graph.get(p)!.add(q);graph.get(q)!.add(p)}
  const sa=station.get(a)!,sb=station.get(b)!;
  const start=key([sa.longitude,sa.latitude]),end=key([sb.longitude,sb.latitude]);
  const seen=new Set([start]),queue=[start];for(const n of queue)for(const next of graph.get(n)||[])if(!seen.has(next)){seen.add(next);queue.push(next)}
  expect(seen.has(end),`${service.trainNumber} ${sa.name}→${sb.name} has disconnected pieces`).toBe(true);
 }
 expect(count).toBeGreaterThan(2000);
});
