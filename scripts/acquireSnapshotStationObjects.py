"""Find candidate IDs in HOTOSM, then verify original OSM station objects.

The extract omits subway attributes, so its names/points alone are insufficient.
Only current, visible, exact-Chinese-name passenger-rail nodes are retained.
"""
import argparse, json, time, urllib.error, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from acquireJiangsu import RAW, save


def acquire(snapshot, names):
    features=json.loads(snapshot.read_text())['features']
    ids=set()
    for feature in features:
        p=feature['properties'];identity=p.get('id','')
        if feature['geometry']['type']!='Point' or not identity.startswith('node/'):continue
        if p.get('railway') not in ('station','halt'):continue
        if not any((p.get(k) or '').removesuffix('站') in names for k in ('name','name_zh')):continue
        ids.add(int(identity.split('/')[1]))
    del features
    path=RAW/'verified-coordinate-objects.json'
    elements=json.loads(path.read_text())['elements'] if path.exists() else []
    existing={(e['type'],e['id']) for e in elements}
    ids=sorted(i for i in ids if ('node',i) not in existing)
    print('Candidate original station nodes',len(ids),flush=True)
    def fetch(batch):
        url='https://api.openstreetmap.org/api/0.6/nodes?nodes='+','.join(map(str,batch))
        for attempt in range(3):
            try:
                request=urllib.request.Request(url,headers={'User-Agent':'Railbound-data/1.0'})
                with urllib.request.urlopen(request,timeout=30) as response:doc=ET.fromstring(response.read())
                if doc.find('error') is not None:raise ValueError('Incomplete OSM response')
                return doc
            except urllib.error.HTTPError as error:
                if error.code==404 and len(batch)>1:
                    middle=len(batch)//2;doc=ET.Element('osm')
                    for chunk in (batch[:middle],batch[middle:]):
                        result=fetch(chunk)
                        if result is not None:doc.extend(result)
                    return doc
                if error.code not in (429,500,502,503,504) or attempt==2:
                    print('Original objects unavailable',batch,str(error),flush=True);return None
            except Exception as error:
                if attempt==2:
                    print('Original objects unavailable',batch,str(error),flush=True);return None
            time.sleep(2*(attempt+1))
    for offset in range(0,len(ids),100):
        doc=fetch(ids[offset:offset+100]);accepted=[]
        if doc is None:continue
        for node in doc.findall('node'):
            if node.get('visible')=='false' or node.get('lon') is None:continue
            tags={t.get('k'):t.get('v') for t in node.findall('tag')}
            if tags.get('railway') not in ('station','halt'):continue
            if tags.get('station') in ('subway','light_rail') or tags.get('subway')=='yes':continue
            labels=[tags.get(k,'').removesuffix('站') for k in ('name','name:zh','name:zh-Hans')]
            if not names.intersection(labels):continue
            accepted.append({'type':'node','id':int(node.get('id')),'lon':float(node.get('lon')),'lat':float(node.get('lat')),'tags':tags,'version':int(node.get('version','1')),'timestamp':node.get('timestamp')})
        elements.extend(accepted)
        save(path,{'elements':list({(e['type'],e['id']):e for e in elements}.values())})
        print('Verified batch',offset//100+1,len(accepted),[e['tags'].get('name') for e in accepted],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('snapshot',type=Path)
    parser.add_argument('--names',type=Path,required=True)
    args=parser.parse_args()
    acquire(args.snapshot,set(json.loads(args.names.read_text())))
