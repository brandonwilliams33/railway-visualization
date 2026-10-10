import manifest from '../data/intercity-groups.json';
import type {DepartureOrigin} from '../types';

/** Navigation references only: no station, route or service is combined. */
export function buildIntercityIndex(origins:DepartureOrigin[]){
 const byId=new Map(origins.map(s=>[s.id,s]));
 const memberships=new Map<string,{lines:typeof manifest.lines;keepPrimary:boolean}>();
 for(const line of manifest.lines){
  for(const entry of line.stations){
   const station=byId.get(entry.stationId);
   if(!station||station.name!==entry.name||!line.provinceIds.includes(station.provinceId))throw new Error(`Invalid intercity reference: ${entry.name}`);
   const member=memberships.get(entry.stationId)||{lines:[],keepPrimary:false};
   member.lines.push(line);member.keepPrimary ||= entry.keepPrimary;
   memberships.set(entry.stationId,member);
  }
 }
 const rank=(a:DepartureOrigin,b:DepartureOrigin)=>Number(a.tier==='local')-Number(b.tier==='local')||b.verifiedServiceCount-a.verifiedServiceCount||a.name.localeCompare(b.name,'zh-CN');
 function city(id:string|null){
  const all=origins.filter(s=>s.cityId===id).sort(rank);
  const intercity=all.filter(s=>memberships.has(s.id));
  const primary=all.filter(s=>!memberships.has(s.id)||memberships.get(s.id)!.keepPrimary);
  // A shared stop is shown once, with all its verified lines as labels.
  const sections=manifest.lines.flatMap(line=>{
   const stations=intercity.filter(s=>memberships.get(s.id)!.lines[0].id===line.id);
   return stations.length?[{id:line.id,name:line.name,stations}]:[];
  });
  return {all,primary,intercity,sections};
 }
 const groupFor=(stationId:string|null)=>stationId&&memberships.has(stationId)&&!memberships.get(stationId)!.keepPrimary?'intercity' as const:null;
 const resolve=(id:string|null,group:string|null)=>group==='intercity'&&city(id).intercity.length?'intercity' as const:null;
 return {city,memberships,groupFor,resolve};
}
