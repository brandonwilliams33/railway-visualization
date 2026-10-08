"""Offline ETL. Only verified passenger stop sequences create coverage.

Approximate geographic interval union is not an exact physical-track union.
No OSM routing graph or freight track is imported into passenger coverage.
"""
from pathlib import Path
from collections import defaultdict
import json
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
def load(name):
    return json.loads((RAW / name).read_text())

def build():
    acquisition=load('acquisition.json')
    registry=load('stations.json')
    by_name={s['name']:s for s in registry}
    assert len(by_name)==len(registry), 'Duplicate station names'
    assert len({s['id'] for s in registry})==len(registry), 'Duplicate station IDs'
    from originSources import indexes as origin_indexes, services as source_services
    indexes=origin_indexes()
    origin_names={s['name'] for s in indexes}
    rows=source_services()
    js_acquisition=load('jiangsu-acquisition.json')
    acquisition['retrievedAt']=max([js_acquisition['retrievedAt']]+[s.get('retrievedAt','') for s in indexes])
    acquisition['candidates']=len({c for s in indexes for c in s.get('candidateTrainNumbers',[])})
    acquired=set(rows)
    candidate_codes={code for s in indexes for code in s.get('candidateTrainNumbers',[])}
    acquisition['failedPages']=[f'/huoche/{code.lower()}.html' for code in sorted(candidate_codes-acquired)]
    services=[];rejected=[];temporary=[];nonpassenger=[];malformed=[]
    missing=set();invalid_timing=[]
    for code,r in sorted(rows.items()):
        if not r['passenger'] or len(r['stopNames'])<2 or r['category'] not in ['G','C','D','Z','T','K','OTHER']:
            nonpassenger.append(code);continue
        if (code[0] in 'GDK' and len(code[1:])==4 and code[1] in '459') or code.startswith('L'):
            temporary.append(code);continue
        if not origin_names.intersection(r['stopNames']):
            rejected.append(code);continue
        if r.get('sourceValidation',{}).get('elapsedTimeMonotonic') is False:
            invalid_timing.append(code);continue
        if any(' ' in n for n in r['stopNames']):
            malformed.append(code);continue
        names=[n for i,n in enumerate(r['stopNames']) if i==0 or n!=r['stopNames'][i-1]]
        if len(names)!=len(set(names)):
            malformed.append(code);continue
        missing.update(n for n in names if n not in by_name)
        known=[by_name[n]['id'] for n in names if n in by_name]
        services.append({'id':'svc-'+code.lower(),'trainNumber':code,'category':r['category'],'stations':known,
            'completeStopNames':names,'unknownStopNames':[n for n in names if n not in by_name],
            'passenger':True,'sourceUrl':r['sourceUrl'],'sourceUpdatedAt':r['sourceUpdatedAt'],'segmentIds':[]})
    # Every departure station is an independent origin. Published stop lists
    # create direct destinations; geometry is built separately afterward.
    service_at=defaultdict(list)
    for service in services:
        for sid in service['stations']:service_at[sid].append(service)
    networks={};origins=[];pending=[]
    for entry in indexes:
        station=by_name.get(entry['name'])
        if not station or not service_at[station['id']]:
            pending.append({'name':entry['name'],'reason':'coordinate missing' if not station else 'no validated regular passenger service'});continue
        hub=station['id'];ss=service_at[hub]
        station['isHub']=True
        major=entry.get('major',entry['name'] in {entry['city']+suffix for suffix in ('','东','西','南','北','虹桥')})
        station['major']=station['major'] or major
        origins.append({'id':hub,'name':entry['name'],'city':entry['city'],'cityId':entry['cityId'],'province':entry['province'],'provinceId':entry['provinceId'],
            'tier':'major' if major else 'local','sourceUrl':entry['sourceUrl'],'sourceUpdatedAt':entry.get('sourceUpdatedAt') or max(s['sourceUpdatedAt'] for s in ss),
            'candidateServiceCount':len(entry.get('candidateTrainNumbers',[])),'verifiedServiceCount':len(ss)})
        networks[hub]={'hubStationId':hub,'destinationStationIds':sorted({x for service in ss for x in service['stations']}-{hub}),
            'railwaySegmentIds':[],'serviceIds':[service['id'] for service in ss]}
    used={x for service in services for x in service['stations']}
    for station in registry:station['isHub']=station['id'] in networks
    sources=[
        {'name':'HOTOSM / OpenStreetMap 铁路轨道','url':'https://data.humdata.org/dataset/hotosm_chn_railways','description':'2026-05-10 OSM 轨道快照；采用具名客运走廊原始线形，排除货运专线与车辆段。ODbL 1.0。'},
        {'name':'铁路网 · 江苏车站目录','url':'https://www.crecc.com/jiangsu/','description':'13 城市、86 个独立车站入口；先获取大站，再补充小站的公开时刻与完整服务停站表。'},
        {'name':'铁路网 · 徐州站公开时刻表','url':'https://www.crecc.com/jiangsu/xuzhou/xuzhou.html','description':'候选车次入口；每个服务保存完整停站页面 URL，核验含中心站后入库。'},
        {'name':'铁路网 · 徐州东站公开时刻表','url':'https://www.crecc.com/jiangsu/xuzhou/xuzhoudong.html','description':'第三方客运时刻快照，源页面标注 2026-09-11 更新；不保证当天运行。'},
        {'name':'OpenStreetMap · @railroute-ts/china','url':'https://github.com/mayurrawte/railroutes/tree/main/packages/china','description':'仅用于真实站点坐标，以标准化站名精确匹配；不把全轨道图当作客运网络。数据 ODbL 1.0。'},
        {'name':'China-rail-way-stations-data','url':'https://github.com/listenzcc/China-rail-way-stations-data','description':'WGS84 车站坐标与城市信息补充；保留每个车站的坐标来源。'},
        {'name':'Natural Earth','url':'https://www.naturalearthdata.com/','description':'公共领域行政区地理底图，离线静态展示。'},
    ]
    for province in sorted({s['provinceId'] for s in indexes}-{'jiangsu'}):
        entries=[s for s in indexes if s['provinceId']==province]
        sources.append({'name':'铁路网 · '+entries[0]['province']+'车站目录','url':'https://www.crecc.com/'+province+'/','description':'按城市获取独立车站与完整客运停站表；未核验入口不开放。'})
    sources.append({'name':'Wikidata 车站坐标','url':'https://www.wikidata.org/','description':'仅采用已确认铁路车站身份、位于中国省级范围内的高精度地球坐标；同名消歧义页、海外同名站和粗略坐标不用于定位。结构化数据 CC0。'})
    data={'updatedAt':max(s['sourceUpdatedAt'] for s in services),'retrievedAt':acquisition['retrievedAt'],'stations':[s for s in registry if s['id'] in used], 'services':services,'segments':[],'networks':networks,'origins':origins,'sources':sources,'audit':{'candidates':acquisition['candidates'],'acceptedServices':len(services),'rejectedNoHub':len(rejected),'excludedTemporary':len(temporary),'nonPassenger':len(nonpassenger),'malformedSequences':len(malformed),'unlocatedStations':sorted(missing),'failedPages':len(acquisition['failedPages']),'invalidTimingServices':invalid_timing,'pendingOrigins':pending,'originCount':len(origins),'cityCount':len({s['cityId'] for s in origins})}}
    from physicalGeometry import apply_physical
    physical=load('physical-rails.json')
    data=apply_physical(data,physical)
    from connectCorridors import connect_corridors
    data=connect_corridors(data, physical)
    overview={k:data[k] for k in ['updatedAt','retrievedAt','stations','sources','audit','origins']}
    overview.update({'services':[],'segments':[],'networks':{},'physicalSources':{}})
    (ROOT/'src/data/overview.json').write_text(json.dumps(overview,ensure_ascii=False,separators=(',',':'))+'\n')
    (ROOT/'src/data/network.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    geo={'type':'FeatureCollection','features':[{'type':'Feature','id':s['id'],'properties':{k:v for k,v in s.items() if k!='geometry'},'geometry':s['geometry']} for s in data['segments']]}
    (ROOT/'data/railway-segments.geojson').write_text(json.dumps(geo,ensure_ascii=False,separators=(',',':'))+'\n')
    audit={'summary':data['audit'],'failedPages':acquisition['failedPages'],'rejectedNoHub':rejected,'originMembershipMismatches':{entry['name']:[code for code in entry.get('candidateTrainNumbers',[]) if code in rows and entry['name'] not in rows[code]['stopNames']] for entry in indexes},'excludedTemporary':temporary,'nonPassenger':nonpassenger,'malformedSequences':malformed,'geometryMethod':'Reviewed OSM corridor geometry, with schematic station links and short published-stop corridors. Remaining long gaps are traced along reviewed OSM and shared passenger corridor geometry; nearby corridor cuts may be joined for readability without merging station identities. Display routes do not establish operational train paths or create direct destinations.'}
    (ROOT/'data/audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'origins':len(origins),'cities':len({s['cityId'] for s in origins}),'stations':len(data['stations']),'segments':len(data['segments']),'services':len(services),'audit':data['audit']},ensure_ascii=False))
if __name__=='__main__':build()
