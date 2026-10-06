import {useEffect,useMemo,useState} from 'react';
import {MapContainer,GeoJSON,CircleMarker,Polyline,Tooltip,TileLayer,useMap,useMapEvents} from 'react-leaflet';
import {latLngBounds} from 'leaflet';
import {Plus,Minus,Maximize,Layers,Navigation} from 'lucide-react';
import type {FeatureCollection} from 'geojson';
import geography from '../data/geography.json';
import {corridorLines,visibleStations} from '../lib/mapPresentation';
import {stationById} from '../lib/network';
import type {ViewNetwork} from '../lib/network';
import type {RailwaySegment} from '../types';
const geo=geography as FeatureCollection;
const reduceMotion=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function Controls({view,selectedId,resetKey,onZoom}:{view:ViewNetwork;selectedId:string|null;resetKey:number;onZoom:(n:number)=>void}){
 const map=useMap();useMapEvents({zoomend:()=>onZoom(map.getZoom())});
 const fit=()=>{const points=view.stations.map(s=>[s.latitude,s.longitude] as [number,number]);if(points.length>1)map.fitBounds(latLngBounds(points),{padding:[45,55],maxZoom:7,animate:!reduceMotion()});else map.setView([view.hubStation.latitude,view.hubStation.longitude],7)};
 useEffect(()=>{fit(); /* bounds follow the filter, never a new hub from a destination */},[view.hubStation.id,resetKey]);
 useEffect(()=>{if(!selectedId)return;const s=stationById.get(selectedId);if(s)map.flyTo([s.latitude,s.longitude],Math.max(map.getZoom(),7),{animate:!reduceMotion(),duration:.5})},[selectedId]);
 useEffect(()=>{const observer=new ResizeObserver(()=>map.invalidateSize());observer.observe(map.getContainer());return()=>observer.disconnect()},[map]);
 return <div className="map-controls"><button aria-label="放大地图" onClick={()=>map.zoomIn()}><Plus size={18}/></button><button aria-label="缩小地图" onClick={()=>map.zoomOut()}><Minus size={18}/></button><span/><button aria-label="显示完整网络" onClick={fit}><Maximize size={17}/></button></div>
}
export default function RailMap({view,selectedId,selectedSegment,onStation,onSegment,resetKey,active=true}:{active?:boolean;view:ViewNetwork;selectedId:string|null;selectedSegment:string|null;onStation:(id:string)=>void;onSegment:(s:RailwaySegment)=>void;resetKey:number}){
 const [zoom,setZoom]=useState(5),[street,setStreet]=useState(false),[tileError,setTileError]=useState(false),[hoveredId,setHoveredId]=useState<string|null>(null);
 const highlighted=useMemo(()=>{
  const ids=new Set<string>();
  if(selectedId){
   const byId=new Map(view.segments.map(s=>[s.id,s]));let best:string[]=[];let bestScore=Infinity;
   for(const service of view.services){
    const a=service.stations.indexOf(view.hubStation.id),b=service.stations.indexOf(selectedId);if(b<0||a<0)continue;
    const legs=service.segmentIds.slice(Math.min(a,b),Math.max(a,b));const route=[...new Set(legs.flat())];if(!route.length)continue;
    let length=0;for(const id of route){const cs=byId.get(id)?.geometry.coordinates||[];for(let i=1;i<cs.length;i++)length+=Math.hypot((cs[i][0]-cs[i-1][0])*91,(cs[i][1]-cs[i-1][1])*111)}
    const score=legs.filter(l=>!l.length).length*100000+length;
    if(score<bestScore){best=route;bestScore=score}
   }
   best.forEach(id=>ids.add(id));
  }
  if(selectedSegment)ids.add(selectedSegment);return ids;
 },[selectedId,selectedSegment,view]);
 const displayLines=useMemo(()=>corridorLines(view.segments,zoom),[view.segments,zoom]);
 const markers=useMemo(()=>active?visibleStations(view.stations,zoom,view.hubStation.id,selectedId):view.stations,[active,view.stations,zoom,view.hubStation.id,selectedId]);
 const labels=useMemo(()=>{const major=view.stations.filter(s=>s.major&&!s.isHub);if(zoom>=7)return new Set(major.map(s=>s.id));const cities=['北京','上海','西安','广州','成都','重庆','武汉','杭州','南京','郑州','长沙','昆明','沈阳','哈尔滨','乌鲁木齐','兰州','贵阳','福州'];return new Set(cities.flatMap(city=>{const station=major.find(s=>s.city===city&&(s.name.endsWith('南')||s.name.endsWith('北')||s.name.endsWith('东')||s.name.endsWith('虹桥')))||major.find(s=>s.city===city);return station?[station.id]:[]}))},[view.stations,zoom]);
 return <div className="map-wrap" id="network-map"><MapContainer center={[34.3,113]} zoom={5} zoomSnap={0.25} minZoom={3} maxZoom={14} zoomControl={false} preferCanvas scrollWheelZoom={false} className="rail-map" aria-label={active?`${view.hubStation.name}客运直达网络地图`:'中国主要客运车站地图'}><GeoJSON attribution='© <a href="https://www.naturalearthdata.com/">Natural Earth</a> · Stations © <a href="https://www.openstreetmap.org/copyright">OSM contributors</a>' data={geo} style={f=>({color:'#ccd1c4',weight:.8,fillColor:f?.properties?.china?'#f0f2e9':'#e8ece3',fillOpacity:1})} interactive={false}/>{street&&<TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>' eventHandlers={{tileerror:()=>setTileError(true),load:()=>setTileError(false)}}/>}<Controls view={view} selectedId={selectedId} resetKey={resetKey} onZoom={setZoom}/>{displayLines.map(line=>{const lit=line.segmentIds.some(id=>highlighted.has(id));return <Polyline key={line.id} positions={line.positions} smoothFactor={zoom<7?2.5:1} pathOptions={{color:lit?'#bd5036':'#476c60',weight:lit?3:zoom<7?1.5:1.6,opacity:highlighted.size?(lit?0.95:0.1):zoom<7?0.58:0.7,lineCap:'round',lineJoin:'round'}} eventHandlers={{click:()=>{const s=view.segments.find(s=>line.segmentIds.includes(s.id));if(s)onSegment(s)}}}/>})}{markers.map(s=>{const hub=active&&s.id===view.hubStation.id,selected=s.id===selectedId,match=view.destinationIds.has(s.id);return <CircleMarker key={s.id} center={[s.latitude,s.longitude]} radius={hub?7:selected?6:!active?4:s.major?3.3:zoom>=7?3:2} pathOptions={{color:hub||selected?'#bd5036':match?'#46685d':'#87988e',fillColor:hub||selected?'#bd5036':'#f7f8f2',fillOpacity:1,weight:hub||selected?2.5:1,opacity:1}} eventHandlers={{click:()=>onStation(s.id),mouseover:()=>setHoveredId(s.id),mouseout:()=>setHoveredId(null)}}><Tooltip key={`${active}-${hub||selected||labels.has(s.id)}`} direction="top" permanent={hub||selected||labels.has(s.id)} className={hub?'hub-label':'station-label'} offset={[0,-4]}><strong>{s.name}{hub?' · 出发站':''}</strong>{(hoveredId===s.id||!(hub||selected||labels.has(s.id)))&&<span>{s.province} · {s.city}<br/>{!active?'主要客运车站':view.services.some(v=>v.stations.includes(s.id))?`${view.hubStation.name}可直达`:'地理路径参考站'}</span>}</Tooltip></CircleMarker>})}</MapContainer><div className="map-caption"><Navigation size={17}/><span>{active?'一张地图，连接徐州与远方':'中国主要客运站点'}<small>{active?(selectedId?'突出一条已匹配客运路径，部分区间可能留空':'点击沿线车站，探索直达目的地'):'先选择出发城市，再展开客运网络'}</small></span></div><button className="base-toggle" onClick={()=>{setStreet(!street);setTileError(false)}} aria-pressed={street}><Layers size={16}/>{street?'简洁底图':'街道底图'}</button><div className="map-legend">{active&&<><span><i className="hub-dot"/>中心站</span><span><i className="rail-line"/>客运网络</span></>}<span><i className="station-dot"/>{active?(zoom<6?'主要站点 · 放大看小站':'沿线车站'):'主要客运站'}</span></div>{active&&<details className="segment-browser"><summary>浏览客运区段</summary><select aria-label="选择客运区段" value="" onChange={e=>{const segment=view.segments.find(s=>s.id===e.target.value);if(segment)onSegment(segment)}}><option value="">选择区段，查看详情</option>{view.segments.map(s=><option key={s.id} value={s.id}>{s.name||'铁路区段'} · {s.id.slice(-5)}</option>)}</select></details>}{active&&<div className="geometry-note">{tileError?'街道底图暂不可用，可切换简洁底图。':zoom<7?'概览合并邻近走廊 · 放大查看细节':'少停站区间不直接连线 · 部分路径待核验'}</div>}{active&&view.destinations.length===0&&<div className="map-empty">没有匹配站点，请调整筛选条件。</div>}</div>
}
