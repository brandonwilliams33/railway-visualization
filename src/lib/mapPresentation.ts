import type {RailwaySegment,Station} from '../types';
type Point=[number,number];
export interface DisplayLine {id:string;positions:Point[];segmentIds:string[]}
// This graph exists only to aggregate ink at the current map scale. It is
// never used to calculate destinations, transfers or operational routes.
export function corridorLines(segments:RailwaySegment[],zoom:number,anchors:Station[]=[]):DisplayLine[]{
 if(zoom>=8)return segments.map(s=>({id:s.id,positions:s.geometry.coordinates.map(c=>[c[1],c[0]]),segmentIds:[s.id]}));
 const cellKm=zoom<6?12:zoom<7?5:1.5;
 const nodes=new Map<string,{sum:Point;count:number}>(),edges=new Map<string,{a:string;b:string;ids:Set<string>}>();
 const baseKey=(c:number[])=>`${Math.round(c[0]*91/cellKm)},${Math.round(c[1]*111/cellKm)}`;
 const anchorCells=new Map<string,Station[]>();for(const s of anchors){const k=baseKey([s.longitude,s.latitude]);anchorCells.set(k,[...(anchorCells.get(k)||[]),s])}
 const pinned=new Map<string,Point>();
 const key=(c:number[])=>{const k=baseKey(c),list=anchorCells.get(k);if(!list)return k;const s=list.reduce((best,s)=>Math.hypot((s.longitude-c[0])*91,(s.latitude-c[1])*111)<Math.hypot((best.longitude-c[0])*91,(best.latitude-c[1])*111)?s:best);const id=`station:${s.id}`;pinned.set(id,[s.latitude,s.longitude]);return id};
 function register(c:number[]){const k=key(c),n=nodes.get(k);if(n){n.sum[0]+=c[1];n.sum[1]+=c[0];n.count++}else nodes.set(k,{sum:[c[1],c[0]],count:1});return k}
 for(const segment of segments){let previous:string|undefined;
  const cs=segment.geometry.coordinates;
  for(let i=0;i<cs.length-1;i++){
   const a=cs[i],b=cs[i+1],length=Math.hypot((b[0]-a[0])*91,(b[1]-a[1])*111);
   // Sample along existing geometry only. No long stop-to-stop fallback.
   const steps=Math.max(1,Math.ceil(length/(cellKm/2)));
   for(let j=0;j<=steps;j++){
    const t=j/steps,k=register([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);
    if(previous&&previous!==k){const pair=[previous,k].sort(),id=pair.join('|');const edge=edges.get(id);if(edge)edge.ids.add(segment.id);else edges.set(id,{a:pair[0],b:pair[1],ids:new Set([segment.id])})}
    previous=k;
   }
  }
 }
 const adjacency=new Map<string,string[]>();for(const [id,e] of edges)for(const n of [e.a,e.b])adjacency.set(n,[...(adjacency.get(n)||[]),id]);
 const point=(k:string):Point=>{const n=nodes.get(k)!;if(pinned.has(k))return pinned.get(k)!;return [n.sum[0]/n.count,n.sum[1]/n.count]};
 const seen=new Set<string>(),lines:DisplayLine[]=[];
 function walk(start:string,first:string){const positions=[point(start)],ids=new Set<string>();let node=start,eid=first;
  while(!seen.has(eid)){seen.add(eid);const e=edges.get(eid)!;e.ids.forEach(id=>ids.add(id));node=e.a===node?e.b:e.a;positions.push(point(node));const next=adjacency.get(node)!;if(next.length!==2||pinned.has(node))break;const available=next.find(id=>!seen.has(id));if(!available)break;eid=available}
  const softened:Point[]=[positions[0]];
  for(let i=1;i<positions.length-1;i++){const a=positions[i-1],b=positions[i],c=positions[i+1];softened.push([a[0]*.2+b[0]*.8,a[1]*.2+b[1]*.8],[b[0]*.8+c[0]*.2,b[1]*.8+c[1]*.2])}
  softened.push(positions[positions.length-1]);
  lines.push({id:first,positions:softened,segmentIds:[...ids]});
 }
 for(const [n,adj] of adjacency)if(adj.length!==2||pinned.has(n))for(const e of adj)if(!seen.has(e))walk(n,e);
 for(const [id,e] of edges)if(!seen.has(id))walk(e.a,id);
 return lines;
}
export function visibleStations(stations:Station[],zoom:number,hubId:string,selectedId:string|null){
 if(zoom>=7||stations.length<=35)return stations;
 if(zoom<6)return stations.filter(s=>s.major||s.isHub||s.id===hubId||s.id===selectedId);
 const cells=new Map<string,Station>();const cell=zoom<6?35:15;
 for(const s of stations){const key=`${Math.round(s.longitude*91/cell)},${Math.round(s.latitude*111/cell)}`,old=cells.get(key);if(!old||(!old.major&&s.major))cells.set(key,s)}
 const ids=new Set([...cells.values()].map(s=>s.id));stations.forEach(s=>{if(s.isHub||s.id===hubId||s.id===selectedId)ids.add(s.id)});
 return stations.filter(s=>ids.has(s.id));
}
