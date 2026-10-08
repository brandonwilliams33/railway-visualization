"""Verify rounded English-source candidates against original OSM objects.

A candidate coordinate is never used by itself: a Chinese station name must
match on an original railway station/stop object inside the small search box.
"""
import argparse,json,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from acquireJiangsu import save
ROOT=Path(__file__).resolve().parents[1]
def verify(path,names):
 candidates=json.loads(path.read_text());saved=ROOT/'data/raw/verified-coordinate-objects.json';elements=json.loads(saved.read_text())['elements'] if saved.exists() else []
 for chinese,english in names.items():
  matches=[s for s in candidates if s['name'].lower()==english.lower()]
  if len(matches)!=1:print('No unique candidate',chinese,flush=True);continue
  lon,lat=matches[0]['coord'];url=f'https://api.openstreetmap.org/api/0.6/map?bbox={lon-.0015},{lat-.0015},{lon+.0015},{lat+.0015}'
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Railbound-data/1.0'}),timeout=20) as response:doc=ET.fromstring(response.read())
   hits=[]
   for node in doc.findall('node'):
    tags={t.get('k'):t.get('v') for t in node.findall('tag')}
    if tags.get('railway') not in ('station','halt') or tags.get('station') in ('subway','light_rail') or tags.get('subway')=='yes':continue
    labels=[tags.get(k,'').removesuffix('站') for k in ('name','name:zh','name:zh-Hans')]
    if chinese not in labels:continue
    hits.append({'type':'node','id':int(node.get('id')),'lon':float(node.get('lon')),'lat':float(node.get('lat')),'tags':tags})
   elements=list({(e['type'],e['id']):e for e in [*elements,*hits]}.values());print('Verified',chinese,[(e['id'],e['tags'].get('name')) for e in hits],flush=True)
  except Exception as e:print('Lookup unavailable',chinese,str(e),flush=True)
  save(ROOT/'data/raw/verified-coordinate-objects.json',{'elements':elements})
 return elements
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--candidates',type=Path,required=True);p.add_argument('--names',type=Path,required=True);a=p.parse_args();verify(a.candidates,json.loads(a.names.read_text()))
