"""Acquire exact Chinese passenger-station objects; never invent coordinates."""
import argparse,json,re,urllib.parse,urllib.request
from acquireJiangsu import RAW,save

def acquire(names,bbox):
    pattern='^('+'|'.join(re.escape(n) for n in names)+')站?$'
    clauses=[f'nwr[railway~"^(station|halt)$"][station!=subway][station!=light_rail][subway!=yes]["{key}"~"{pattern}"]({bbox});' for key in ('name','name:zh','name:zh-Hans')]
    query='[out:json][timeout:35];('+''.join(clauses)+' );out center body;'
    for host in ['https://maps.mail.ru/osm/tools/overpass/api/interpreter','https://overpass-api.de/api/interpreter','https://overpass.private.coffee/api/interpreter']:
        try:
            request=urllib.request.Request(host,data=urllib.parse.urlencode({'data':query}).encode(),headers={'Content-Type':'application/x-www-form-urlencoded','User-Agent':'Railbound-data/1.0'})
            with urllib.request.urlopen(request,timeout=45) as response:payload=json.load(response)
            if payload.get('remark'):raise ValueError(payload['remark'])
            accepted=[]
            for element in payload.get('elements',[]):
                tags=element.get('tags',{})
                if tags.get('railway') not in ('station','halt') or tags.get('station') in ('subway','light_rail') or tags.get('subway')=='yes':continue
                if not any(tags.get(k,'').removesuffix('站') in names for k in ('name','name:zh','name:zh-Hans')):continue
                coord=element.get('center',element)
                if 'lon' not in coord or 'lat' not in coord:continue
                accepted.append(element)
            path=RAW/'verified-coordinate-objects.json'
            previous=json.loads(path.read_text()).get('elements',[]) if path.exists() else []
            save(path,{'elements':list({(e['type'],e['id']):e for e in [*previous,*accepted]}.values())})
            print('Exact station objects',[(e['id'],e['tags'].get('name')) for e in accepted],flush=True)
            return
        except Exception as error:print('Station lookup unavailable',host,str(error),flush=True)
    raise RuntimeError('All exact station lookup providers unavailable; previous evidence preserved')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--names',required=True);parser.add_argument('--bbox',default='18,73,54,135',help='south,west,north,east');args=parser.parse_args()
    acquire(set(json.loads(open(args.names).read())),args.bbox)
