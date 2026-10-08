"""Complete display corridors using evidenced local passenger intervals.

Schematic connections are explicitly distinguished from surveyed OSM geometry.
Routing only supplies drawing geometry; never creates direct destinations.
"""
import hashlib, heapq, math
from collections import defaultdict
from physicalGeometry import km
from railGapRouting import RailGapRouter

def connect_corridors(data, physical_source=None):
    stations={s['id']:s for s in data['stations']}
    segments={s['id']:s for s in data['segments']}
    coords={sid:[s['longitude'],s['latitude']] for sid,s in stations.items()}
    graph=defaultdict(lambda:defaultdict(dict)); repairs=0
    def family(s):return 'hs' if s['category']=='G' or ('xuzhou-east' in s['stations'] and s['category'] in 'DC') else 'ordinary'
    def schematic(a,b,fam,kind='corridor',end=None):
        pair=sorted([a,b]) if kind=='corridor' else [a,b]
        sid='schematic-'+hashlib.sha256((fam+'|'+kind+'|'+'|'.join(pair)).encode()).hexdigest()[:16]
        if sid not in segments:
            points=[coords[pair[0]],coords[pair[1]]] if end is None else [coords[a],end]
            segments[sid]={'id':sid,'name':f"{stations[a]['name']}—{stations[b]['name']} · 走廊示意" if end is None else f"{stations[a]['name']} · 站点衔接",'coverageStationIds':pair if end is None else [a], 'railwayNames':[], 'osmSourceId':'','geometrySource':'passenger-stop-corridor','geometryAccuracy':'approximate','routingConfidence':'inferred-corridor','family':fam,'schematic':True,'geometry':{'type':'LineString','coordinates':points},'passengerCategories':[],'serviceIds':[]}
        return sid
    def attach(ids,service,a,b):
        for sid in ids:
            seg=segments[sid]
            for field,value in [('serviceIds',service['id']),('passengerCategories',service['category'])]:
                if value not in seg[field]:seg[field].append(value)
    def add_edge(a,b,fam,ids,cost):
        old=graph[fam][a].get(b)
        if old is None or cost<old[0]:graph[fam][a][b]=(cost,ids);graph[fam][b][a]=(cost,ids)
    # Join matched track endpoints to the actual station anchor, not a grid mean.
    for service in data['services']:
        fam=family(service)
        for i,(a,b) in enumerate(zip(service['stations'],service['stations'][1:])):
            ids=service['segmentIds'][i]
            if not ids:continue
            original=list(ids)
            for stop in [a,b]:
                endpoints=[(km(coords[stop],p),p,sid) for sid in original for p in [segments[sid]['geometry']['coordinates'][0],segments[sid]['geometry']['coordinates'][-1]]]
                distance,p,track=min(endpoints)
                if 0.000001<distance<=2.6:
                    sid=schematic(stop,track,fam,'anchor',p)
                    attach([sid],service,a,b);ids.append(sid)
            length=sum(sum(km(x,y) for x,y in zip(segments[sid]['geometry']['coordinates'],segments[sid]['geometry']['coordinates'][1:])) for sid in ids)
            add_edge(a,b,fam,ids,max(length,km(coords[a],coords[b])))
    # A short, published adjacent-stop interval is a local schematic edge.
    # Long express/overnight gaps are routed through these local corridors.
    for service in data['services']:
        fam=family(service)
        for i,(a,b) in enumerate(zip(service['stations'],service['stations'][1:])):
            if service['segmentIds'][i]:continue
            names=service['completeStopNames']
            if names.index(stations[b]['name'])!=names.index(stations[a]['name'])+1:continue
            distance=km(coords[a],coords[b])
            if distance>180:continue
            sid=schematic(a,b,fam);attach([sid],service,a,b)
            add_edge(a,b,fam,[sid],distance*1.15)
    def route(a,b,fam):
        limit=km(coords[a],coords[b])*2+40
        queue=[(0,a)];costs={a:0};parents={}
        while queue:
            cost,node=heapq.heappop(queue)
            if cost!=costs.get(node):continue
            if node==b:
                result=[]
                while node!=a:node,ids=parents[node];result.extend(ids)
                return list(dict.fromkeys(result))
            for nxt,(weight,ids) in graph[fam][node].items():
                new=cost+weight
                if new<=limit and new<costs.get(nxt,math.inf):costs[nxt]=new;parents[nxt]=(node,ids);heapq.heappush(queue,(new,nxt))
        return []
    remaining=0
    for service in data['services']:
        fam=family(service)
        for i,(a,b) in enumerate(zip(service['stations'],service['stations'][1:])):
            if service['segmentIds'][i]:continue
            ids=route(a,b,fam)
            if not ids and service['category'] in 'DC':ids=route(a,b,'ordinary' if fam=='hs' else 'hs')
            if ids:service['segmentIds'][i]=ids;attach(ids,service,a,b);repairs+=1
            else:remaining+=1
    # Resolve the remaining long gaps on the reviewed rail snapshot itself.
    # These are drawing paths, not claims about the train's exact itinerary.
    rail_repairs=0
    if physical_source:
        router=RailGapRouter(physical_source)
        cache={}
        for service in data['services']:
            for i,(a,b) in enumerate(zip(service['stations'],service['stations'][1:])):
                if service['segmentIds'][i]:continue
                pair=tuple(sorted([a,b]))
                if pair not in cache:
                    route=router.route(coords[pair[0]],coords[pair[1]])
                    if route:
                        sid='schematic-'+hashlib.sha256(('rail-path|'+'|'.join(pair)).encode()).hexdigest()[:16]
                        segments[sid]={'id':sid,'name':f"{stations[pair[0]]['name']}—{stations[pair[1]]['name']} · 走廊示意",'coverageStationIds':list(pair),'railwayNames':route['railwayNames'],'osmSourceId':'','geometrySource':'reviewed-OSM-corridor-route','geometryAccuracy':'approximate','routingConfidence':'inferred-corridor','family':'mixed','schematic':True,'geometry':{'type':'LineString','coordinates':route['coordinates']},'passengerCategories':[],'serviceIds':[]}
                        cache[pair]=sid
                    else:cache[pair]=None
                sid=cache[pair]
                if sid:service['segmentIds'][i]=[sid];attach([sid],service,a,b);rail_repairs+=1
    remaining=sum(not leg for service in data['services'] for leg in service['segmentIds'])
    used={sid for s in data['services'] for leg in s['segmentIds'] for sid in leg}
    data['segments']=[segments[sid] for sid in sorted(used)]
    for hub,n in data['networks'].items():
        n['railwaySegmentIds']=sorted({sid for s in data['services'] if s['id'] in n['serviceIds'] for leg in s['segmentIds'] for sid in leg})
    data['audit']['schematicRepairedIntervals']=repairs+rail_repairs
    data['audit']['railCorridorRepairedIntervals']=rail_repairs
    data['audit']['remainingUnmappedIntervals']=remaining
    data['audit']['schematicSegments']=sum(bool(s.get('schematic')) for s in data['segments'])
    print('Schematic interval repairs',repairs,'OSM corridor repairs',rail_repairs,'remaining',remaining,'schematic sections',data['audit']['schematicSegments'],flush=True)
    return data
