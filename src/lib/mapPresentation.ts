import type {RailwaySegment,Station} from '../types';
type Point=[number,number];
export interface DisplayLine {id:string;positions:Point[];segmentIds:string[]}
// This graph exists only to aggregate ink at the current map scale. It is
// never used to calculate destinations, transfers or operational routes.
export function corridorLines(segments:RailwaySegment[],zoom:number,anchors:Station[]=[],hubId?:string):DisplayLine[]{
 if(!segments.length)return [];
 // Nearby tracks share one geographic corridor at every scale. The map shows
 // reachability, not an individual train's rail-by-rail itinerary.
 const cellKm=zoom<6?24:zoom<7?12:zoom<8?6:zoom<9?3:1.5;
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
 // Retain a single shared trunk from the departure station to each visible
 // station. This removes parallel alternatives and loops near busy junctions.
 if(hubId&&adjacency.has(`station:${hubId}`)){
  const root=`station:${hubId}`,distance=new Map([[root,0]]),parent=new Map<string,string>();
  const heap:{cost:number;node:string}[]=[];
  function push(cost:number,node:string){let i=heap.length;heap.push({cost,node});while(i){const p=(i-1)>>1;if(heap[p].cost<=cost)break;heap[i]=heap[p];i=p}heap[i]={cost,node}}
  function pop(){const top=heap[0],last=heap.pop()!;if(heap.length){let i=0;while(i*2+1<heap.length){let child=i*2+1;if(child+1<heap.length&&heap[child+1].cost<heap[child].cost)child++;if(last.cost<=heap[child].cost)break;heap[i]=heap[child];i=child}heap[i]=last}return top}
  push(0,root);
  while(heap.length){const {cost,node}=pop();if(cost!==distance.get(node))continue;
   for(const id of adjacency.get(node)||[]){const edge=edges.get(id)!,next=edge.a===node?edge.b:edge.a,a=point(node),b=point(next);
    const km=Math.hypot((a[1]-b[1])*91,(a[0]-b[0])*111);
    const candidate=cost+km/(1+Math.log2(1+edge.ids.size)*.45);
    if(candidate<(distance.get(next)??Infinity)){distance.set(next,candidate);parent.set(next,id);push(candidate,next)}
   }
  }
  const kept=new Set<string>();
  for(const s of anchors){let node=`station:${s.id}`;const visited=new Set<string>();
   while(node!==root&&parent.has(node)&&!visited.has(node)){visited.add(node);const id=parent.get(node)!;kept.add(id);const e=edges.get(id)!;node=e.a===node?e.b:e.a}
  }
  if(kept.size){for(const id of edges.keys())if(!kept.has(id))edges.delete(id);
   adjacency.clear();for(const [id,e] of edges)for(const n of [e.a,e.b])adjacency.set(n,[...(adjacency.get(n)||[]),id]);
  }
 }
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
export function pathLineIds(lines:DisplayLine[],start:Station,end:Station):Set<string>{
 const key=(p:Point)=>p.map(v=>v.toFixed(8)).join(',');
 const graph=new Map<string,{next:string;id:string}[]>();
 for(const line of lines){const a=key(line.positions[0]),b=key(line.positions.at(-1)!);
  graph.set(a,[...(graph.get(a)||[]),{next:b,id:line.id}]);graph.set(b,[...(graph.get(b)||[]),{next:a,id:line.id}]);
 }
 const source=key([start.latitude,start.longitude]),target=key([end.latitude,end.longitude]);
 const seen=new Set([source]),parent=new Map<string,{previous:string;id:string}>(),queue=[source];
 for(const node of queue){if(node===target)break;for(const edge of graph.get(node)||[])if(!seen.has(edge.next)){seen.add(edge.next);parent.set(edge.next,{previous:node,id:edge.id});queue.push(edge.next)}}
 const ids=new Set<string>();let node=target;
 while(node!==source&&parent.has(node)){const p=parent.get(node)!;ids.add(p.id);node=p.previous}
 return ids;
}
export function visibleStations(stations:Station[],zoom:number,hubId:string,selectedId:string|null){
 // Only limit which stops are shown at the nationwide scale. Once the map is
 // enlarged, every station keeps its own marker and interaction target.
 if(zoom>=6||stations.length<=35)return stations;
 return stations.filter(s=>s.major||s.id===hubId||s.id===selectedId);
}
