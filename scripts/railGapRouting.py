"""Trace remaining timetable gaps through the reviewed OSM corridor snapshot.

Returned lines are explicitly schematic: nearby track endpoints may be joined
for display and the exact operational route is not asserted.
"""
from collections import defaultdict
from math import cos, hypot, inf, radians
import heapq
from itertools import count
from physicalGeometry import km


def project(point, coordinates):
    best=(inf,None)
    scale=cos(radians(point[1]))
    for i,(a,b) in enumerate(zip(coordinates,coordinates[1:])):
        dx=(b[0]-a[0])*scale;dy=b[1]-a[1];den=dx*dx+dy*dy
        t=max(0,min(1,((point[0]-a[0])*scale*dx+(point[1]-a[1])*dy)/den)) if den else 0
        foot=[a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]
        distance=km(point,foot)
        if distance<best[0]:best=(distance,(i,foot))
    return best


def simplify(points,tolerance=.18):
    if len(points)<=2:return points
    keep={0,len(points)-1};stack=[(0,len(points)-1)]
    while stack:
        a,b=stack.pop();p,q=points[a],points[b];dx=(q[0]-p[0])*cos(radians((p[1]+q[1])/2));dy=q[1]-p[1];den=dx*dx+dy*dy
        maximum=0;index=None
        for i in range(a+1,b):
            s=points[i];vx=(s[0]-p[0])*cos(radians((p[1]+q[1])/2));vy=s[1]-p[1]
            t=max(0,min(1,(vx*dx+vy*dy)/den)) if den else 0
            distance=hypot(vx-t*dx,vy-t*dy)*111.195
            if distance>maximum:maximum=distance;index=i
        if maximum>tolerance and index is not None:keep.add(index);stack.extend([(a,index),(index,b)])
    return [points[i] for i in sorted(keep)]

class RailGapRouter:
    def __init__(self,source):
        self.edges=source['edges'];self.graph=defaultdict(list);self.boxes=[];self.prefix=[];self.coords={};buckets=defaultdict(list)
        for i,edge in enumerate(self.edges):
            cs=edge['geometry']['coordinates'];xs=[p[0] for p in cs];ys=[p[1] for p in cs]
            self.boxes.append((min(xs),max(xs),min(ys),max(ys)))
            length=[0]
            for a,b in zip(cs,cs[1:]):length.append(length[-1]+km(a,b))
            self.prefix.append(length)
            self._join((i,0),(i,1),cs,edge['railwayNames'])
            for end,p in enumerate((cs[0],cs[-1])):
                node=(i,end);self.coords[node]=p;buckets[(int(p[0]*10),int(p[1]*10))].append(node)
        for node,p in self.coords.items():
            x,y=int(p[0]*10),int(p[1]*10)
            for xx in range(x-1,x+2):
                for yy in range(y-1,y+2):
                    for other in buckets[(xx,yy)]:
                        if other>=node:continue
                        distance=km(p,self.coords[other])
                        if distance<=1:self._join(node,other,[p,self.coords[other]],[],distance*2)
    def _join(self,a,b,points,names,cost=None):
        cost=cost if cost is not None else sum(km(x,y) for x,y in zip(points,points[1:]))
        self.graph[a].append((b,cost,points,names));self.graph[b].append((a,cost,points[::-1],names))
    def candidates(self,p):
        matches=[]
        for i,(lo,hi,low,high) in enumerate(self.boxes):
            if not(lo-.18<=p[0]<=hi+.18 and low-.18<=p[1]<=high+.18):continue
            distance,cut=project(p,self.edges[i]['geometry']['coordinates'])
            if distance<=16:matches.append((distance,i,*cut))
        return sorted(matches)[:15]
    def route(self,a,b):
        starts=self.candidates(a);ends=self.candidates(b)
        if not starts or not ends:return None
        local=defaultdict(list)
        def connect(v,node,points,cost,names):
            local[v].append((node,cost,points,names));local[node].append((v,cost,points[::-1],names))
        for virtual,p,candidates in [('start',a,starts),('end',b,ends)]:
            for distance,i,j,foot in candidates:
                cs=self.edges[i]['geometry']['coordinates'];prefix=self.prefix[i];before=prefix[j]+km(cs[j],foot);total=prefix[-1];names=self.edges[i]['railwayNames']
                connect(virtual,(i,0),[p,foot,*cs[j::-1]],before+distance*2,names)
                connect(virtual,(i,1),[p,foot,*cs[j+1:]],total-before+distance*2,names)
        # Two stations can lie on one long chain; use its interior instead of
        # detouring to the chain endpoints.
        end_by_edge={i:(d,j,p) for d,i,j,p in ends}
        for da,i,ia,pa in starts:
            if i not in end_by_edge:continue
            db,ib,pb=end_by_edge[i];cs=self.edges[i]['geometry']['coordinates'];prefix=self.prefix[i]
            pos_a=prefix[ia]+km(cs[ia],pa);pos_b=prefix[ib]+km(cs[ib],pb)
            between=cs[ia+1:ib+1] if pos_a<=pos_b else cs[ib+1:ia+1][::-1]
            connect('start','end',[a,pa,*between,pb,b],abs(pos_a-pos_b)+(da+db)*2,self.edges[i]['railwayNames'])
        sequence=count();queue=[(0,next(sequence),'start')];costs={'start':0};parent={}
        while queue:
            cost,_,node=heapq.heappop(queue)
            if cost!=costs.get(node):continue
            if node=='end':break
            for nxt,weight,points,names in (*self.graph[node],*local[node]):
                new=cost+weight
                if new<costs.get(nxt,inf):costs[nxt]=new;parent[nxt]=(node,points,names);heapq.heappush(queue,(new,next(sequence),nxt))
        if 'end' not in costs or costs['end']>km(a,b)*2.2+50:return None
        chunks=[];names=[];node='end'
        while node!='start':
            previous,points,segment_names=parent[node]
            chunks.append(points);names.extend(segment_names);node=previous
        coordinates=[]
        for chunk in reversed(chunks):coordinates.extend(chunk if not coordinates else chunk[1:])
        coordinates=[p for i,p in enumerate(coordinates) if i==0 or p!=coordinates[i-1]]
        return {'coordinates':simplify(coordinates),'railwayNames':list(dict.fromkeys(names)),'lengthKm':round(costs['end'],1)}
