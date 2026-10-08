"""Use coarse Wikidata locations only to search for exact Chinese OSM objects."""
import json, urllib.request, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from acquireJiangsu import RAW, save

def acquire():
    known={s['name'] for s in json.loads((RAW/'stations.json').read_text())}
    candidates=[f for f in json.loads((RAW/'wikidata-coordinate-evidence.json').read_text()) if f['name'] not in known]
    def verify(fact):
        name=fact['name'];coord=fact['coordinate'];lon=coord['longitude'];lat=coord['latitude']
        radius=min(.02,max(.004,coord.get('precision',.01)*1.5))
        url=f'https://api.openstreetmap.org/api/0.6/map?bbox={lon-radius},{lat-radius},{lon+radius},{lat+radius}'
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Railbound-data/1.0'}),timeout=25) as response:
                doc=ET.fromstring(response.read())
            result=[]
            for node in doc.findall('node'):
                tags={tag.get('k'):tag.get('v') for tag in node.findall('tag')}
                if tags.get('railway') not in ('station','halt') or tags.get('station') in ('subway','light_rail') or tags.get('subway')=='yes':continue
                if name not in [tags.get(k,'').removesuffix('站') for k in ('name','name:zh','name:zh-Hans')]:continue
                result.append({'type':'node','id':int(node.get('id')),'lon':float(node.get('lon')),'lat':float(node.get('lat')),'tags':tags})
            print('Verified',name,[(n['id'],n['tags'].get('name')) for n in result],flush=True)
            return result
        except Exception as error:
            print('Coordinate lookup unavailable',name,str(error),flush=True)
            return []
    path=RAW/'verified-coordinate-objects.json'
    elements=json.loads(path.read_text())['elements'] if path.exists() else []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for nodes in pool.map(verify,candidates):
            elements.extend(nodes)
            elements=list({(e['type'],e['id']):e for e in elements}.values())
            save(path,{'elements':elements})

if __name__=='__main__':
    acquire()
