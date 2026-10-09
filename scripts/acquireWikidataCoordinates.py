"""Acquire exact-title station identity and Earth coordinates from Wikidata."""
import argparse,json,time,urllib.request,urllib.parse,urllib.error
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def fetch(base,args):
 url=base+'?'+urllib.parse.urlencode(args)
 for attempt in range(4):
  try:
   time.sleep(.5)
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Railbound-data/1.0 (railway coordinate verification)'}),timeout=30) as f:return json.load(f)
  except urllib.error.HTTPError as error:
   if error.code not in (429,503) or attempt==3:raise
   time.sleep([5,15,30][attempt])
parser=argparse.ArgumentParser();parser.add_argument('--all-needed',action='store_true');parser.add_argument('--names',type=Path,help='Explicit Chinese station names as a JSON array');args=parser.parse_args()
names=set(json.loads((root/'data/audit.json').read_text())['summary']['unlocatedStations'])
if args.all_needed:
 resolution=json.loads((root/'data/raw/coordinate-resolution.json').read_text())
 names.update(resolution['unlocatedStations']);names.update(resolution['unlocatedOrigins'])
if args.names:names=set(json.loads(args.names.read_text()))
names=sorted(n for n in names if ' ' not in n)
known={s['name'] for s in json.loads((root/'data/raw/stations.json').read_text())}
names=[n for n in names if n not in known]
overrides_path=root/'data/raw/station-title-overrides.json'
overrides=json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
titles={overrides.get(n,n+'站'):n for n in names}
ids={}
for offset in range(0,len(titles),40):
 j=fetch('https://zh.wikipedia.org/w/api.php',{'action':'query','titles':'|'.join(list(titles)[offset:offset+40]),'prop':'pageprops','format':'json'})
 ids.update({p['pageprops']['wikibase_item']:titles[p['title']] for p in j['query']['pages'].values() if p.get('pageprops',{}).get('wikibase_item') and 'disambiguation' not in p.get('pageprops',{})})
for name in set(names)-set(ids.values()):
 search=fetch('https://www.wikidata.org/w/api.php',{'action':'wbsearchentities','search':name+'站','language':'zh','format':'json','limit':5})
 matches=[v for v in search.get('search',[]) if v.get('label','').removesuffix('站')==name and any(word in v.get('description','').lower() for word in ('railway','铁路','鐵路'))]
 if len(matches)==1:ids[matches[0]['id']]=name
e={'entities':{}}
for offset in range(0,len(ids),40):
 response=fetch('https://www.wikidata.org/w/api.php',{'action':'wbgetentities','ids':'|'.join(list(ids)[offset:offset+40]),'props':'labels|descriptions|claims','languages':'zh|zh-hans|en','format':'json'})
 if 'error' in response:raise ValueError('Wikidata: '+response['error'].get('info','API error'))
 e['entities'].update(response['entities'])
previous=root/'data/raw/wikidata-coordinate-evidence.json'
facts=json.loads(previous.read_text()) if previous.exists() else []
identity_path=root/'data/raw/wikidata-station-identities.json'
identities=json.loads(identity_path.read_text()) if identity_path.exists() else []
for sid,entity in e['entities'].items():
 descriptions=[v['value'] for v in entity.get('descriptions',{}).values()]
 instances=[c['mainsnak'].get('datavalue',{}).get('value',{}).get('id') for c in entity.get('claims',{}).get('P31',[])]
 coords=[c['mainsnak'].get('datavalue',{}).get('value') for c in entity.get('claims',{}).get('P625',[]) if c.get('rank')!='deprecated']
 coords=[c for c in coords if c and c.get('globe')=='http://www.wikidata.org/entity/Q2']
 print(ids[sid],sid,descriptions,coords,flush=True)
 railway_identity='Q55488' in instances or any(any(word in d.lower() for word in ('railway','铁路','鐵路','高铁','高鐵')) for d in descriptions)
 if railway_identity:
  identities.append({'name':ids[sid],'wikidataId':sid,'sourceUrl':'https://www.wikidata.org/wiki/'+sid,'labels':entity.get('labels',{}),'descriptions':entity.get('descriptions',{}),'instanceOf':instances,'countryIds':[c['mainsnak'].get('datavalue',{}).get('value',{}).get('id') for c in entity.get('claims',{}).get('P17',[])]})
 if len(coords)==1 and railway_identity:
  facts.append({'name':ids[sid],'wikidataId':sid,'coordinate':coords[0],'sourceUrl':'https://www.wikidata.org/wiki/'+sid,'labels':entity.get('labels',{}),'descriptions':entity.get('descriptions',{}),'instanceOf':instances,'countryIds':[c['mainsnak'].get('datavalue',{}).get('value',{}).get('id') for c in entity.get('claims',{}).get('P17',[])]})
from acquireJiangsu import save
save(previous,list({f['name']:f for f in facts}.values()))

save(identity_path,list({f['name']:f for f in identities}.values()))
