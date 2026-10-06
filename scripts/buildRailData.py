"""Offline ETL. Only verified passenger stop sequences create coverage.

Approximate geographic interval union is not an exact physical-track union.
No OSM routing graph or freight track is imported into passenger coverage.
"""
from pathlib import Path
from collections import defaultdict
import json, math, hashlib
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
def load(name):
    return json.loads((RAW / name).read_text())
def distance(a,b):
    dx=(a['longitude']-b['longitude'])*math.cos(math.radians((a['latitude']+b['latitude'])/2))
    dy=a['latitude']-b['latitude']
    return math.hypot(dx,dy)*111.195

def build():
    acquisition=load('acquisition.json')
    registry=load('stations.json')
    by_name={s['name']:s for s in registry}
    assert len(by_name)==len(registry), 'Duplicate station names'
    assert len({s['id'] for s in registry})==len(registry), 'Duplicate station IDs'
    raw=load('passenger-services.json')
    services=[];rejected=[];temporary=[];nonpassenger=[];malformed=[]
    missing=set()
    for r in raw:
        code=r['trainNumber']
        if not r['passenger'] or not r['stopNames'] or r['category'] not in ['G','C','D','Z','T','K','OTHER']:
            nonpassenger.append(code);continue
        # Conservative exclusion: these numbering ranges often denote extra
        # services; do not imply they are part of a regular operating diagram.
        if (code[0] in 'GDK' and len(code[1:])==4 and code[1] in '459') or code.startswith('L'):
            temporary.append(code);continue
        if not any(h in r['stopNames'] for h in ['徐州','徐州东']):
            rejected.append(code);continue
        r['stopNames']=[n for i,n in enumerate(r['stopNames']) if i==0 or n!=r['stopNames'][i-1]]
        if len(r['stopNames'])!=len(set(r['stopNames'])):
            malformed.append(code);continue
        missing.update(n for n in r['stopNames'] if n not in by_name)
        known=[(i,by_name[n]['id']) for i,n in enumerate(r['stopNames']) if n in by_name]
        services.append({'id':'svc-'+code.lower(),'trainNumber':code,'category':r['category'],'stations':[x[1] for x in known], 'completeStopNames':r['stopNames'],'unknownStopNames':[n for n in r['stopNames'] if n not in by_name], 'passenger':True,'sourceUrl':r['sourceUrl'],'sourceUpdatedAt':r['sourceUpdatedAt'],'knownStopIndices':[x[0] for x in known]})
    by_id={s['id']:s for s in registry}
    # Learn a finer stop sequence only when both endpoints occur on ONE
    # published service of the same train family. No network pathfinding.
    alternatives={}
    for s in services:
        family='hs' if s['category'] in 'GCD' else 'ordinary'
        ids=s['stations'];indices=s['knownStopIndices']
        for i in range(len(ids)):
            cost=0
            for j in range(i+1,min(len(ids),i+16)):
                if indices[j]!=indices[j-1]+1:break
                cost+=distance(by_id[ids[j-1]],by_id[ids[j]])
                if j==i+1:continue
                straight=distance(by_id[ids[i]],by_id[ids[j]])
                if cost>straight*1.12+2:continue
                key=(family,*sorted([ids[i],ids[j]]))
                chain=ids[i:j+1]
                if ids[i]>ids[j]:chain=chain[::-1]
                if key not in alternatives or len(chain)>len(alternatives[key]):alternatives[key]=chain
    segments={}
    def interval(a,b,family,seen=None):
        pair=tuple(sorted([a,b]));key=(family,*pair);seen=seen or set()
        if key in alternatives and key not in seen:
            chain=alternatives[key]
            if a!=chain[0]:chain=chain[::-1]
            return sum((interval(x,y,family,seen|{key}) for x,y in zip(chain,chain[1:])),[])
        segment_id='seg-'+hashlib.sha256('|'.join(pair).encode()).hexdigest()[:16]
        if segment_id not in segments:
            aa,bb=[by_id[x] for x in pair]
            segments[segment_id]={'id':segment_id,'fromStationId':pair[0],'toStationId':pair[1],'geometry':{'type':'LineString','coordinates':[[aa['longitude'],aa['latitude']],[bb['longitude'],bb['latitude']]]},'geometryAccuracy':'approximate','passengerCategories':set(),'serviceIds':set()}
        return [segment_id]
    for s in services:
        family='hs' if s['category'] in 'GCD' else 'ordinary';indices=s.pop('knownStopIndices');s['segmentIds']=[]
        for i,(a,b) in enumerate(zip(s['stations'],s['stations'][1:])):
            # Missing coordinates break the line. Never invent a bypass.
            ids=interval(a,b,family) if indices[i+1]==indices[i]+1 else []
            s['segmentIds'].append(ids)
            for sid in ids:
                segments[sid]['passengerCategories'].add(s['category']);segments[sid]['serviceIds'].add(s['id'])
    for s in segments.values():
        s['passengerCategories']=sorted(s['passengerCategories']);s['serviceIds']=sorted(s['serviceIds'])
    networks={}
    for hub in ['xuzhou','xuzhou-east']:
        ss=[s for s in services if hub in s['stations']]
        destinations=set(x for s in ss for x in s['stations'])-{hub}
        networks[hub]={'hubStationId':hub,'destinationStationIds':sorted(destinations),'railwaySegmentIds':sorted(set(x for s in ss for ids in s['segmentIds'] for x in ids)),'serviceIds':[s['id'] for s in ss]}
    used={x for n in networks.values() for x in n['destinationStationIds']}|{'xuzhou','xuzhou-east'}
    used.update(x for s in segments.values() for x in [s['fromStationId'],s['toStationId']])
    sources=[
        {'name':'HOTOSM / OpenStreetMap 铁路轨道','url':'https://data.humdata.org/dataset/hotosm_chn_railways','description':'2026-05-10 OSM 轨道快照；采用具名客运走廊原始线形，排除货运专线与车辆段。ODbL 1.0。'},
        {'name':'铁路网 · 徐州站公开时刻表','url':'https://www.crecc.com/jiangsu/xuzhou/xuzhou.html','description':'候选车次入口；每个服务保存完整停站页面 URL，核验含中心站后入库。'},
        {'name':'铁路网 · 徐州东站公开时刻表','url':'https://www.crecc.com/jiangsu/xuzhou/xuzhoudong.html','description':'第三方客运时刻快照，源页面标注 2026-09-11 更新；不保证当天运行。'},
        {'name':'OpenStreetMap · @railroute-ts/china','url':'https://github.com/mayurrawte/railroutes/tree/main/packages/china','description':'仅用于真实站点坐标，以标准化站名精确匹配；不把全轨道图当作客运网络。数据 ODbL 1.0。'},
        {'name':'China-rail-way-stations-data','url':'https://github.com/listenzcc/China-rail-way-stations-data','description':'WGS84 车站坐标与城市信息补充；保留每个车站的坐标来源。'},
        {'name':'Natural Earth','url':'https://www.naturalearthdata.com/','description':'公共领域行政区地理底图，离线静态展示。'},
    ]
    data={'updatedAt':acquisition['sourceUpdatedAt'],'retrievedAt':acquisition['retrievedAt'],'stations':[s for s in registry if s['id'] in used], 'services':services,'segments':sorted(segments.values(),key=lambda s:s['id']),'networks':networks,'sources':sources,'audit':{'candidates':acquisition['candidates'],'acceptedServices':len(services),'rejectedNoHub':len(rejected),'excludedTemporary':len(temporary),'nonPassenger':len(nonpassenger),'malformedSequences':len(malformed),'unlocatedStations':sorted(missing),'failedPages':len(acquisition['failedPages'])}}
    from physicalGeometry import apply_physical
    data=apply_physical(data,load('physical-rails.json'))
    overview={k:data[k] for k in ['updatedAt','retrievedAt','stations','sources','audit']}
    overview.update({'services':[],'segments':[],'networks':{},'physicalSources':{}})
    (ROOT/'src/data/overview.json').write_text(json.dumps(overview,ensure_ascii=False,separators=(',',':'))+'\n')
    (ROOT/'src/data/network.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    geo={'type':'FeatureCollection','features':[{'type':'Feature','id':s['id'],'properties':{k:v for k,v in s.items() if k!='geometry'},'geometry':s['geometry']} for s in data['segments']]}
    (ROOT/'data/railway-segments.geojson').write_text(json.dumps(geo,ensure_ascii=False,separators=(',',':'))+'\n')
    audit={'summary':data['audit'],'failedPages':acquisition['failedPages'],'rejectedNoHub':rejected,'excludedTemporary':temporary,'nonPassenger':nonpassenger,'malformedSequences':malformed,'geometryMethod':'OSM physical corridor matching on reviewed passenger mainlines, deduplicated by track geometry. Operational routing remains inferred; unmatched intervals are not drawn.'}
    (ROOT/'data/audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({**{h:len(n['destinationStationIds']) for h,n in networks.items()},'segments':len(data['segments']),'services':len(services),'audit':data['audit']},ensure_ascii=False))
if __name__=='__main__':build()
