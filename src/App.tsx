import {lazy,Suspense,useEffect,useMemo,useState} from 'react';
import {ArrowUpRight,ArrowRight} from 'lucide-react';
import {Header,CityBar,FilterBar} from './components/Chrome';
import {Details} from './components/Details';
import {Directory} from './components/Directory';
import {Methodology} from './components/Methodology';
import TravelNote from './travel/TravelNote';
import {data,loadNetwork,getNetwork,getOverview,readState,writeState,stationById,originById,origins,departureCities,departureIndex,stationChoiceIndex} from './lib/network';
import type {HubId,CityId,Filters,RailwaySegment} from './types';
const RailMap=lazy(()=>import('./map/RailMap'));
const emptyFilters:Filters={type:'all',province:'',search:''};
export default function App(){
 const [initial]=useState(readState),[departure,setDeparture]=useState(initial.departure),[group,setGroup]=useState(initial.group),[hub,setHub]=useState<HubId|null>(initial.hub),[filters,setFilters]=useState<Filters>(initial.filters),[selected,setSelected]=useState<string|null>(null),[segment,setSegment]=useState<RailwaySegment|null>(null),[about,setAbout]=useState(false),[resetKey,setResetKey]=useState(0);
 const city=departure.city;
 const [ready,setReady]=useState(false),[loadError,setLoadError]=useState(false);
 useEffect(()=>{if((hub||about)&&!ready){setLoadError(false);loadNetwork().then(()=>setReady(true)).catch(()=>setLoadError(true))}},[hub,about,ready]);
 const view=useMemo(()=>hub&&ready?getNetwork(hub,filters):null,[hub,filters,ready]);
 const overview=useMemo(()=>getOverview(city),[city]);
 useEffect(()=>{writeState(hub,filters,city,departure,group)},[hub,filters,city,departure,group]);
 useEffect(()=>{const pop=()=>{const s=readState();setDeparture(s.departure);setGroup(s.group);setHub(s.hub);setFilters(s.filters);setSelected(null);setSegment(null);setResetKey(k=>k+1)};window.addEventListener('popstate',pop);return()=>window.removeEventListener('popstate',pop)},[]);
 useEffect(()=>{if(view&&filters.province&&!view.provinces.some(p=>p.id===filters.province))setFilters(f=>({...f,province:''}))},[view,filters.province]);
 function clear(){setSelected(null);setSegment(null);setFilters(emptyFilters);setResetKey(k=>k+1)}
 function choose(id:HubId){const origin=originById.get(id);if(!origin)return;setDeparture(departureIndex.resolve({city:origin.cityId}));setGroup(origin.cityId===city&&group&&stationChoiceIndex.resolve(city,group)?group:stationChoiceIndex.groupFor(id));setHub(id);clear()}
 function changeCity(selected:CityId|null){setDeparture(departureIndex.resolve({city:selected}));setGroup(null);setHub(null);clear()}
 function changeScope(region:string|null,province:string|null){setDeparture(departureIndex.resolve({region,province}));setGroup(null);setHub(null);clear()}
 function update(change:Partial<Filters>){setFilters(f=>({...f,...change}));setSelected(null);setSegment(null);setResetKey(k=>k+1)}
 function select(id:string){setSelected(id);setSegment(null);if(!hub&&originById.has(id)){setDeparture(departureIndex.resolve({city:originById.get(id)!.cityId}));setGroup(stationChoiceIndex.groupFor(id));setResetKey(k=>k+1)}}
 function directorySelect(id:string){select(id);document.getElementById('network-map')?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'})}
 return <><Header onHome={()=>changeCity(null)} active={!!hub} onSwitch={()=>{setHub(null);clear()}} onAbout={()=>setAbout(true)}/><main className={`network-page ${!hub?'overview-page':''}`}><section className="network-heading"><div><h1>{view?`${view.hubStation.name}站`:'从这里，去远方。'}{view&&<span>，出发。</span>}</h1><p>{view?'从这里，可以直接坐火车去哪里？':'从一座车站，看中国。'}</p></div><div className="heading-aside"><span>{view?'无需换乘的远方':'真实地理 · 铁路客运'}</span><ArrowUpRight size={26} strokeWidth={1}/></div></section>{view?<FilterBar view={view} filters={filters} onChange={update}/>:<CityBar group={group} onGroup={setGroup} selection={departure} onScope={changeScope} onCity={changeCity} onHub={choose}/>}{(hub||about)&&!ready&&<p role="status">{loadError?'网络数据加载失败，请刷新重试。':'正在加载所选车站的客运网络…'}</p>}<section className="map-section" aria-label="客运网络"><Suspense fallback={<div className="map-loading">正在展开铁路地图…</div>}><RailMap active={!!view} view={view||overview} selectedId={selected} selectedSegment={segment?.id||null} onStation={select} onSegment={s=>{setSegment(s);setSelected(null)}} resetKey={resetKey}/></Suspense><Details inactive={!view} station={selected?stationById.get(selected):undefined} segment={segment||undefined} view={view||overview} onDepart={choose} onClose={()=>{setSelected(null);setSegment(null)}}/></section>{view?<><div className="network-overview" aria-live="polite"><div className="overview-title"><span className="signal"/> 网络概览<small>同一段客运联系，仅绘制一次</small></div><div className="stat"><b>{view.destinations.length}</b><span>直达站点</span></div><div className="stat"><b>{new Set(view.destinations.map(s=>s.province)).size}</b><span>省级地区</span></div><div className="stat"><b>{view.services.filter(s=>s.stations.some(id=>view.destinationIds.has(id))).length}</b><span>相关客运车次</span></div><button className="overview-reset" onClick={()=>update(emptyFilters)}>重置筛选 <ArrowRight size={16}/></button></div><Directory stations={view.destinations} hub={view.hubStation.name} onSelect={directorySelect}/><TravelNote/></>:<p className="overview-hint"><span className="signal"/> 已开放 {departureCities.length} 个城市、{origins.length} 个独立车站，选择后查看可直达的全国目的地。</p>}</main><footer className="site-footer"><span>沿线 <small>让远方，有迹可循。</small></span><div><span>源数据更新 {data.updatedAt}</span><button onClick={()=>setAbout(true)}>数据与方法 <ArrowUpRight size={14}/></button></div></footer>{about&&ready&&<Methodology onClose={()=>setAbout(false)}/>}</>
}
