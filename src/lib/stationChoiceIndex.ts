import localManifest from '../data/local-station-groups.json';
import type {DepartureOrigin} from '../types';
import type {buildIntercityIndex} from './intercityIndex';

export type StationGroup='intercity'|'local';
export const stationGroupNames:Record<StationGroup,string>={intercity:'城际铁路',local:'市内及周边小站'};

/** A navigation density rule, not an official station grade or service boundary. */
export function buildStationChoiceIndex(origins:DepartureOrigin[],intercity:ReturnType<typeof buildIntercityIndex>){
 const byId=new Map(origins.map(s=>[s.id,s]));
 for(const line of localManifest.lines)for(const entry of line.stations){
  const s=byId.get(entry.stationId);
  if(!s||s.name!==entry.name||s.cityId!==line.cityId||s.provinceId!==line.provinceId)throw new Error(`Invalid local station reference: ${entry.name}`);
 }
 const cities=new Map<string,ReturnType<typeof intercity.city>>();
 for(const id of new Set(origins.map(s=>s.cityId)))cities.set(id,intercity.city(id));
 const choices=new Map<string,{all:DepartureOrigin[];primary:DepartureOrigin[];groups:{id:StationGroup;name:string;stations:DepartureOrigin[];sections:{id:string;name:string;stations:DepartureOrigin[]}[]}[]}>();
 for(const [id,c] of cities){
  const primary=c.primary.filter(s=>s.tier==='major'||s.verifiedServiceCount>=100||intercity.memberships.get(s.id)?.keepPrimary);
  // Every city retains an immediately selectable station, even with only small stops.
  if(!primary.length&&c.primary.length)primary.push(c.primary[0]);
  const primaryIds=new Set(primary.map(s=>s.id));
  const local=c.all.filter(s=>!primaryIds.has(s.id)&&!intercity.memberships.has(s.id));
  const covered=new Set<string>();
  const localSections=localManifest.lines.filter(l=>l.cityId===id).flatMap(l=>{
   const stations=l.stations.map(e=>byId.get(e.stationId)!).filter(s=>local.some(v=>v.id===s.id)&&!covered.has(s.id));
   stations.forEach(s=>covered.add(s.id));
   return stations.length?[{id:l.id,name:l.name,stations}]:[];
  });
  const other=local.filter(s=>!covered.has(s.id));
  if(other.length)localSections.push({id:'other-local',name:'其他小站',stations:other});
  const groups=[];
  if(c.intercity.length)groups.push({id:'intercity' as const,name:stationGroupNames.intercity,stations:c.intercity,sections:c.sections});
  if(local.length)groups.push({id:'local' as const,name:stationGroupNames.local,stations:local,sections:localSections});
  choices.set(id,{all:c.all,primary,groups});
 }
 const city=(id:string|null)=>choices.get(id||'')||{all:[],primary:[],groups:[]};
 const resolve=(id:string|null,group:string|null)=>city(id).groups.find(g=>g.id===group)?.id||null;
 const groupFor=(stationId:string|null)=>{
  const s=byId.get(stationId||'');if(!s)return null;
  const c=city(s.cityId);if(c.primary.some(v=>v.id===s.id))return null;
  return c.groups.find(g=>g.stations.some(v=>v.id===s.id))?.id||null;
 };
 return {city,resolve,groupFor};
}
