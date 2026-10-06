import {ArrowUpRight} from 'lucide-react';
import type {Station} from '../types';
export function Directory({stations,hub,onSelect}:{stations:Station[];hub:string;onSelect:(id:string)=>void}){
 const groups=[...new Set(stations.map(s=>s.province))].sort((a,b)=>a.localeCompare(b,'zh-CN'));
 return <section className="directory" aria-label="直达目的地"><div className="section-heading"><div><span className="section-kicker">把地图变成下一次出发</span><h2>从{hub}，直接到达</h2></div><p>{stations.length} 个车站 · 点击站名，在地图上找到它</p></div>{!stations.length?<div className="empty-state"><h3>没有匹配的直达站点</h3><p>试试其他城市，或清除地区与列车类型筛选。</p></div>:<div className="province-directory">{groups.map(p=><div className="province-group" key={p}><h3>{p}<span>{stations.filter(s=>s.province===p).length}</span></h3><div>{stations.filter(s=>s.province===p).sort((a,b)=>a.name.localeCompare(b.name,'zh-CN')).map(s=><button key={s.id} onClick={()=>onSelect(s.id)}>{s.name}<ArrowUpRight size={13}/></button>)}</div></div>)}</div>}</section>
}
