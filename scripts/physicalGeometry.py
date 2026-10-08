"""Match published passenger intervals to reviewed, OSM-shaped corridors.

This is conservative physical-geometry matching, NOT a claim of a verified
operational train path. No fallback chord is rendered for an unmatched leg.
"""
from collections import defaultdict
import heapq, math, hashlib

def km(a,b):
    dx=(a[0]-b[0])*math.cos(math.radians((a[1]+b[1])/2));dy=a[1]-b[1]
    return math.hypot(dx,dy)*111.195

def apply_physical(data,source):
    nodes={};graphs=defaultdict(lambda:defaultdict(list));edges={};spatial=defaultdict(list)
    def node(coord,family):
        key=(family,round(coord[0],4),round(coord[1],4))
        if key not in nodes:
            nodes[key]=tuple(coord);spatial[(family,int(coord[0]*20),int(coord[1]*20))].append(key)
        return key
    # Snap stations to the actual polyline, inserting anchor cuts. Snapping
    # only to a simplified vertex can miss a station on a long straight rail.
    line_grid=defaultdict(list)
    for ci,chain in enumerate(source['edges']):
        cs=chain['geometry']['coordinates'];fam=chain['family']
        for vi,(a,b) in enumerate(zip(cs,cs[1:])):
            for x in range(int(min(a[0],b[0])*20),int(max(a[0],b[0])*20)+1):
                for y in range(int(min(a[1],b[1])*20),int(max(a[1],b[1])*20)+1):line_grid[(fam,x,y)].append((ci,vi))
    cuts=defaultdict(list);station_points={}
    for station in data['stations']:
        c=(station['longitude'],station['latitude']);x,y=int(c[0]*20),int(c[1]*20)
        for fam in ['hs','ordinary']:
            best=None;bd=2.5
            candidates=set(p for i in range(x-1,x+2) for j in range(y-1,y+2) for p in line_grid.get((fam,i,j),[]))
            for ci,vi in candidates:
                a,b=source['edges'][ci]['geometry']['coordinates'][vi:vi+2];dx,dy=b[0]-a[0],b[1]-a[1];scale=math.cos(math.radians(c[1]));den=dx*dx*scale*scale+dy*dy
                t=max(0,min(1,((c[0]-a[0])*dx*scale*scale+(c[1]-a[1])*dy)/den)) if den else 0
                point=(a[0]+t*dx,a[1]+t*dy);d=km(c,point)
                if d<bd:bd=d;best=(ci,vi,t,point)
            if best:
                ci,vi,t,point=best;cuts[(ci,vi)].append((t,point));station_points[(station['id'],fam)]=(fam,round(point[0],4),round(point[1],4))
    for ci,chain in enumerate(source['edges']):
        original=chain['geometry']['coordinates'];family=chain['family'];cs=[]
        for vi,(a,b) in enumerate(zip(original,original[1:])):
            cs.append(a);cs.extend(c for _,c in sorted(cuts.get((ci,vi),[])))
        cs.append(original[-1])
        for a,b in zip(cs,cs[1:]):
            na,nb=node(a,family),node(b,family)
            if na==nb:continue
            pair=tuple(sorted((na,nb)));eid='osm-'+hashlib.sha256(str(pair).encode()).hexdigest()[:16]
            if eid in edges:continue
            edges[eid]={'a':na,'b':nb,'coords':[list(nodes[na]),list(nodes[nb])],'names':chain['railwayNames'],'sources':chain['sourceWayIds'],'family':family}
            weight=km(a,b)
            graphs[family][na].append((nb,eid,weight));graphs[family][nb].append((na,eid,weight))
    stations={s['id']:s for s in data['stations']};snaps=station_points
    def snap(sid,family):
        key=(sid,family)
        if key in snaps:return snaps[key]
        snaps[key]=None;return None
    # Contract degree-two runs, protecting real station anchors and junctions.
    for sid in stations:
        for family in ['hs','ordinary']:snap(sid,family)
    protected={n for n in snaps.values() if n};contracted=defaultdict(lambda:defaultdict(list));contract_edges={}
    for family,graph in graphs.items():
        ends={n for n,adj in graph.items() if len(adj)!=2}|{n for n in protected if n[0]==family}
        seen=set()
        for start in sorted(ends):
            for nxt,eid,weight in graph[start]:
                if eid in seen:continue
                seen.add(eid);route=[(eid,start,nxt)];current=nxt;cost=weight
                while current not in ends:
                    opts=[(n,e,w) for n,e,w in graph[current] if e not in seen]
                    if len(opts)!=1:break
                    n,e,w=opts[0];seen.add(e);route.append((e,current,n));cost+=w;current=n
                if current==start:continue
                coords=[];names=[];sources=set()
                for e,a,b in route:
                    edge=edges[e];cs=edge['coords'] if a==edge['a'] else edge['coords'][::-1]
                    coords.extend(cs if not coords else cs[1:]);names.extend(edge['names']);sources.update(edge['sources'])
                # Each contracted geometry is uniquely identified by the
                # actual track run, independent of service or direction.
                cid='track-'+hashlib.sha256('|'.join(sorted(e for e,_,_ in route)).encode()).hexdigest()[:16]
                contract_edges[cid]={'id':cid,'geometry':{'type':'LineString','coordinates':coords},'name':' / '.join(dict.fromkeys(names)),'railwayNames':list(dict.fromkeys(names)),'geometrySource':'OpenStreetMap','geometryAccuracy':'approximate','routingConfidence':'inferred-corridor','osmWayIds':sorted(sources),'family':family}
                contracted[family][start].append((current,cid,cost));contracted[family][current].append((start,cid,cost))
    print('Physical graph',len(nodes),'nodes;',len(contract_edges),'contracted track sections',flush=True)
    cache={};matched=0;unmatched=0;used={}
    def route(a,b,family):
        key=(family,*sorted([a,b]))
        if key in cache:return cache[key]
        na,nb=snap(a,family),snap(b,family)
        if not na or not nb:cache[key]=[];return []
        graph=contracted[family];limit=km(nodes[na],nodes[nb])*2.8+25
        queue=[(km(nodes[na],nodes[nb]),0,na)];costs={na:0};parent={};visited=0;reached=False
        while queue:
            _,cost,n=heapq.heappop(queue)
            if cost>costs.get(n,math.inf):continue
            if n==nb:reached=True;break
            visited+=1
            if visited>40000:break
            for nxt,e,w in graph.get(n,[]):
                candidate=cost+w
                if candidate>limit or candidate>=costs.get(nxt,math.inf):continue
                costs[nxt]=candidate;parent[nxt]=(n,e);heapq.heappush(queue,(candidate+km(nodes[nxt],nodes[nb]),candidate,nxt))
        else:cache[key]=[];return []
        if not reached:cache[key]=[];return []
        result=[];n=nb
        while n!=na:
            n,e=parent[n];result.append(e)
        cache[key]=result;return result
    for service in data['services']:
        # Preserve directness from the published service, not graph reachability.
        indices=[service['completeStopNames'].index(stations[s]['name']) for s in service['stations']]
        prefer='hs' if 'xuzhou-east' in service['stations'] or service['category']=='G' else 'ordinary'
        service['segmentIds']=[]
        for i,(a,b) in enumerate(zip(service['stations'],service['stations'][1:])):
            if indices[i+1]!=indices[i]+1:
                service['segmentIds'].append([]);unmatched+=1;continue
            categories=[prefer] if service['category'] not in ['C','D'] else [prefer,'ordinary' if prefer=='hs' else 'hs']
            ids=[]
            for family in categories:
                ids=route(a,b,family)
                if ids:break
            service['segmentIds'].append(ids)
            if ids:matched+=1
            else:unmatched+=1
            for eid in ids:
                if eid not in used:used[eid]={**contract_edges[eid],'passengerCategories':set(),'serviceIds':set(),'coverageStationIds':set()}
                used[eid]['passengerCategories'].add(service['category']);used[eid]['serviceIds'].add(service['id']);used[eid]['coverageStationIds'].update([a,b])
    for e in used.values():
        for key in ['passengerCategories','serviceIds','coverageStationIds']:e[key]=sorted(e[key])
    provenance={}
    for e in used.values():
        ways=e.pop('osmWayIds');ref='source-'+hashlib.sha256('|'.join(ways).encode()).hexdigest()[:16]
        provenance[ref]=ways;e['osmSourceId']=ref
    data['physicalSources']=provenance
    data['segments']=sorted(used.values(),key=lambda e:e['id'])
    for hub,n in data['networks'].items():
        ss=[s for s in data['services'] if s['id'] in n['serviceIds']]
        n['railwaySegmentIds']=sorted({e for s in ss for ids in s['segmentIds'] for e in ids})
    data['audit']['matchedPhysicalIntervals']=matched;data['audit']['unmatchedPhysicalIntervals']=unmatched
    data['audit']['physicalSourceSnapshot']=source['sourceSnapshot'];data['audit']['physicalGeometryBuild']=source['metadata']['builtAt']
    print('Matched passenger intervals',matched,'unmatched',unmatched,'unique physical track sections',len(used),'cache',len(cache),flush=True)
    return data
