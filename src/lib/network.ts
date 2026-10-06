import raw from '../data/overview.json';
import type { RailData,HubId,Filters,PassengerService } from '../types';
export let data = raw as unknown as RailData;
export const stationById = new Map(data.stations.map(s=>[s.id,s]));
export const serviceById = new Map<string,PassengerService>();
let loading:Promise<void>|undefined;
export function loadNetwork(){return loading??=(async()=>{const raw=await import('../data/network.json');data=raw.default as RailData;for(const s of data.services)serviceById.set(s.id,s)})().catch(error=>{loading=undefined;throw error})}
export const isHighspeed = (s:PassengerService)=>['G','D','C'].includes(s.category);
export function getNetwork(hub:HubId,filters:Filters){
 const network=data.networks[hub];
 const hubStation=stationById.get(network.hubStationId)!;
 const services=network.serviceIds.map(id=>serviceById.get(id)!).filter(s=>filters.type==='all'||(filters.type==='highspeed'?isHighspeed(s):!isHighspeed(s)));
 const availableIds=new Set(services.flatMap(s=>s.stations));availableIds.delete(hubStation.id);
 const availableStations=data.stations.filter(s=>availableIds.has(s.id));
 const query=filters.search.trim().toLocaleLowerCase();
 const destinations=availableStations.filter(s=>(!filters.province||s.provinceId===filters.province)&&(!query||`${s.name} ${s.city} ${s.province}`.toLocaleLowerCase().includes(query)));
 const destinationIds=new Set(destinations.map(s=>s.id));
 // Retain only each service's path from the hub to a matching stop. This
 // cannot create reachability by transferring between unrelated services.
 const selectedSegments=new Set<string>();const pathStationIds=new Set([hubStation.id]);
 for(const service of services){
  const h=service.stations.indexOf(hubStation.id);
  for(let i=0;i<service.stations.length;i++){
   if(!destinationIds.has(service.stations[i]))continue;
   const a=Math.min(h,i),b=Math.max(h,i);
   service.segmentIds.slice(a,b).flat().forEach(id=>selectedSegments.add(id));
   service.stations.slice(a,b+1).forEach(id=>pathStationIds.add(id));
  }
 }
 const segments=data.segments.filter(s=>selectedSegments.has(s.id));
 segments.forEach(s=>{s.coverageStationIds.forEach(id=>pathStationIds.add(id))});
 const stations=data.stations.filter(s=>pathStationIds.has(s.id));
 return {hubStation,services,destinations,destinationIds,segments,stations,provinces:[...new Map(availableStations.map(s=>[s.provinceId,{id:s.provinceId,name:s.province}])).values()].sort((a,b)=>a.name.localeCompare(b.name,'zh-CN'))};
}
export type ViewNetwork=ReturnType<typeof getNetwork>;
export function readState(){const p=new URLSearchParams(location.search);const s=p.get('station');const t=p.get('type');return {city:p.get('city')==='xuzhou'||s==='xuzhou'||s==='xuzhou-east',hub:(s==='xuzhou'||s==='xuzhou-east'?s:null) as HubId|null,filters:{type:(t==='highspeed'||t==='conventional'?t:'all') as Filters['type'],province:p.get('province')||'',search:p.get('q')||''}}}
export function writeState(hub:HubId|null,filters:Filters,city=false){const p=new URLSearchParams();if(city&&!hub)p.set('city','xuzhou');if(hub)p.set('station',hub);if(filters.type!=='all')p.set('type',filters.type);if(filters.province)p.set('province',filters.province);if(filters.search)p.set('q',filters.search);history.replaceState(null,'',`${location.pathname}${p.size?'?'+p:''}${location.hash}`)}

export function getOverview():ViewNetwork{
 const stations=data.stations.filter(s=>s.major||s.isHub);
 return {hubStation:stationById.get('xuzhou')!,services:[],destinations:[],destinationIds:new Set(),segments:[],stations,provinces:[]};
}
