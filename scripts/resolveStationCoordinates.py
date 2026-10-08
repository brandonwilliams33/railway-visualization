"""Add exact-name station coordinates, retaining evidence and ambiguities.

This updates the offline registry. It never substitutes a city's centre for a
station, nor conflates distinct station names. Existing station IDs are stable.
"""
from pathlib import Path
from collections import defaultdict
import argparse, csv, hashlib, json, re, urllib.parse, urllib.request

ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'
def read(path):return json.loads(path.read_text())
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def normalize(name):return name.removesuffix('站')
def inside_ring(point,ring):
    x,y=point;inside=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside
def in_geometry(point,geometry):
    polygons=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
    return any(inside_ring(point,p[0]) and not any(inside_ring(point,h) for h in p[1:]) for p in polygons)

def resolve(csv_path,admin_path,osm_path,fetch_osm=False):
    registry=read(RAW/'stations.json');by_name={s['name']:s for s in registry}
    overrides_path=RAW/'coordinate-overrides.json'
    if overrides_path.exists():
        for station in read(overrides_path)['stations']:
            if station['name'] not in by_name:registry.append(station);by_name[station['name']]=station
    from originSources import indexes as origin_indexes, services as source_services
    indexes=origin_indexes();js={s['name']:s for s in indexes}
    records=list(source_services().values())
    needed={n for r in records for n in r['stopNames']}|set(js)
    provinces={s['province']:s['provinceId'] for s in registry}
    provinces.setdefault('海南','hainan');provinces.setdefault('西藏','xizang')
    features=[]
    for f in read(admin_path)['features']:
        if f['properties'].get('admin')!='China':continue
        name=f['properties'].get('name_zh','')
        for suffix in ('维吾尔自治区','壮族自治区','回族自治区','自治区','省','市'):name=name.removesuffix(suffix)
        if name in provinces:features.append((name,f['geometry']))
    def province_at(coord):
        return next((name for name,g in features if in_geometry(coord,g)),None)
    evidence_path=RAW/'wikidata-coordinate-evidence.json'
    if evidence_path.exists():
        for fact in read(evidence_path):
            name=fact['name'];coord=[fact['coordinate']['longitude'],fact['coordinate']['latitude']]
            province=province_at(coord)
            if name in by_name or not province or fact['coordinate'].get('precision',1)>.001:continue
            station={'id':'st-wikidata-'+fact['wikidataId'].lower(),'name':name,'city':js[name]['city'] if name in js else '城市待核验','province':province,'provinceId':provinces[province],'longitude':coord[0],'latitude':coord[1],'isHub':False,'major':False,'coordinateSource':fact['sourceUrl']}
            registry.append(station);by_name[name]=station
    csv_rows={normalize(s['站名']):s for s in csv.DictReader(csv_path.open())}
    osm_candidates=defaultdict(list)
    missing=sorted(needed-set(by_name))
    if fetch_osm:
        pattern='^('+'|'.join(re.escape(n) for n in missing)+')站?$'
        query=f'[out:json][timeout:90];nwr[railway~"^(station|halt)$"][station!=subway][station!=light_rail][~"^(name|name:zh|name:zh-Hans)$"~"{pattern}"](18,73,54,135);out center tags;'
        for host in ['https://overpass.private.coffee/api/interpreter','https://overpass-api.de/api/interpreter','https://maps.mail.ru/osm/tools/overpass/api/interpreter']:
            try:
                request=urllib.request.Request(host,data=urllib.parse.urlencode({'data':query}).encode(),headers={'Content-Type':'application/x-www-form-urlencoded','User-Agent':'Railbound-data/1.0'})
                with urllib.request.urlopen(request,timeout=115) as response:payload=json.load(response)
                if payload.get('remark'):raise ValueError(payload['remark'])
                write(osm_path,payload);print('OSM source objects',len(payload.get('elements',[])),flush=True);break
            except Exception as error:print('OSM acquisition failed',host,str(error),flush=True)
    if osm_path.exists():
        for element in read(osm_path).get('elements',[]):
            tag=element.get('tags',{});name=normalize(tag.get('name:zh-Hans',tag.get('name:zh',tag.get('name',''))))
            coord=element.get('center',element)
            if 'lon' in coord and 'lat' in coord:osm_candidates[name].append((element,[coord['lon'],coord['lat']]))
    added=[];ambiguous=[]
    for name in missing:
        candidates=osm_candidates.get(name,[])
        # Multiple OSM objects can describe one station; prefer the station
        # node only when all objects identify the same geographic location.
        if len(candidates)>1:
            first=candidates[0][1]
            if any(abs(c[0]-first[0])+abs(c[1]-first[1])>.04 for _,c in candidates):
                ambiguous.append(name);continue
            candidates.sort(key=lambda x:x[0]['type']!='node')
        row=csv_rows.get(name);city=js[name]['city'] if name in js else (row.get('市','城市待核验') if row else '城市待核验')
        if candidates:
            element,coord=candidates[0];province=js[name]['province'] if name in js else province_at(coord)
            source=f"https://www.openstreetmap.org/{element['type']}/{element['id']}";sid=f"st-osm-{element['type']}-{element['id']}"
        elif row:
            coord=[float(row['WGS84_Lng']),float(row['WGS84_Lat'])];province=row['省']
            source='https://github.com/listenzcc/China-rail-way-stations-data/blob/main/src/station.csv'
            sid='st-source-'+hashlib.sha256(name.encode()).hexdigest()[:16]
        else:continue
        if province not in provinces or not (73<coord[0]<135 and 18<coord[1]<54):continue
        station={'id':sid,'name':name,'city':city,'province':province,'provinceId':provinces[province],
                 'longitude':coord[0],'latitude':coord[1],'isHub':False,'major':name==city,'coordinateSource':source}
        registry.append(station);by_name[name]=station;added.append(name)
    # The province index is evidence for municipality membership, including
    # Jiangsu stations whose earlier registry city was still unverified.
    for name,entry in js.items():
        if name in by_name:
            by_name[name]['city']=entry['city'];by_name[name]['province']=entry['province'];by_name[name]['provinceId']=entry['provinceId']
    write(RAW/'stations.json',sorted(registry,key=lambda s:s['name']))
    remaining=sorted(needed-set(by_name))
    write(RAW/'coordinate-resolution.json',{'addedStations':added,'ambiguousNames':ambiguous,'unlocatedStations':remaining,'unlocatedOrigins':sorted(set(js)-set(by_name))})
    print('Added',len(added),'remaining',len(remaining),'Origins missing',sorted(set(js)-set(by_name)),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--csv',type=Path,required=True);parser.add_argument('--admin',type=Path,required=True);parser.add_argument('--osm',type=Path,required=True);parser.add_argument('--fetch-osm',action='store_true');args=parser.parse_args()
    resolve(args.csv,args.admin,args.osm,args.fetch_osm)
