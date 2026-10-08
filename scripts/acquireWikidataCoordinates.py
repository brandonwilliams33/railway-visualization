"""Acquire exact-title station identity and Earth coordinates from Wikidata."""
import json,urllib.request,urllib.parse
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def fetch(base,args):
 url=base+'?'+urllib.parse.urlencode(args)
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Railbound-data/1.0 (railway coordinate verification)'}),timeout=30) as f:return json.load(f)
names=json.loads((root/'data/audit.json').read_text())['summary']['unlocatedStations']
overrides_path=root/'data/raw/station-title-overrides.json'
overrides=json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
titles={overrides.get(n,n+'站'):n for n in names}
j=fetch('https://zh.wikipedia.org/w/api.php',{'action':'query','titles':'|'.join(titles),'prop':'pageprops','format':'json'})
ids={p.get('pageprops',{}).get('wikibase_item'):titles[p['title']] for p in j['query']['pages'].values() if p.get('pageprops',{}).get('wikibase_item')}
for name in set(names)-set(ids.values()):
 search=fetch('https://www.wikidata.org/w/api.php',{'action':'wbsearchentities','search':name+'站','language':'zh','format':'json','limit':5})
 matches=[v for v in search.get('search',[]) if v.get('label','').removesuffix('站')==name and any(word in v.get('description','').lower() for word in ('railway','铁路','鐵路'))]
 if len(matches)==1:ids[matches[0]['id']]=name
e=fetch('https://www.wikidata.org/w/api.php',{'action':'wbgetentities','ids':'|'.join(ids),'props':'labels|descriptions|claims','languages':'zh|zh-hans|en','format':'json'}) if ids else {'entities':{}}
previous=root/'data/raw/wikidata-coordinate-evidence.json'
facts=[f for f in json.loads(previous.read_text()) if f['name'] not in names] if previous.exists() else []
for sid,entity in e['entities'].items():
 descriptions=[v['value'] for v in entity.get('descriptions',{}).values()]
 coords=[c['mainsnak'].get('datavalue',{}).get('value') for c in entity.get('claims',{}).get('P625',[]) if c.get('rank')!='deprecated']
 coords=[c for c in coords if c and c.get('globe')=='http://www.wikidata.org/entity/Q2']
 print(ids[sid],sid,descriptions,coords,flush=True)
 if len(coords)==1 and any('station' in d.lower() or '车站' in d or '車站' in d for d in descriptions):
  facts.append({'name':ids[sid],'wikidataId':sid,'coordinate':coords[0],'sourceUrl':'https://www.wikidata.org/wiki/'+sid,'labels':entity.get('labels',{}),'descriptions':entity.get('descriptions',{})})
(root/'data/raw/wikidata-coordinate-evidence.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
