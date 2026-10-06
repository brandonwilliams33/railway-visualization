import json,collections,pathlib
from datetime import date
from passengerCorridors import approved,family
import argparse
parser=argparse.ArgumentParser(description='Filter and simplify a HOTOSM railway GeoJSON into named passenger corridors')
parser.add_argument('geojson',type=pathlib.Path)
parser.add_argument('--snapshot',default='2026-05-10')
args=parser.parse_args()
ROOT=pathlib.Path(__file__).resolve().parents[1];raw=ROOT/'data/raw'
print('Reading full OSM rail extract',flush=True)
j=json.load(open(args.geojson));nodes={};adj=collections.defaultdict(list);edges=[]
for f in j['features']:
 p=f['properties'];g=f['geometry'];name=p.get('name')
 if g['type']!='LineString' or p['railway']!='rail' or not approved(name):continue
 fam=family(name)
 for a,b in zip(g['coordinates'],g['coordinates'][1:]):
  na=(fam,round(a[0],5),round(a[1],5));nb=(fam,round(b[0],5),round(b[1],5))
  if na==nb:continue
  nodes.setdefault(na,a);nodes.setdefault(nb,b)
  idx=len(edges);edges.append((na,nb,name,p['id']));adj[na].append((nb,idx));adj[nb].append((na,idx))
print('Named passenger graph nodes',len(nodes),'edges',len(edges),flush=True)
del j
# Branches and OSM line-name changes preserve true topology. Stations will
# be snapped to the resulting geometry by the offline coverage matcher.
ends={n for n,aa in adj.items() if len(aa)!=2 or edges[aa[0][1]][2]!=edges[aa[1][1]][2]}
seen=set();output=[]
def dp(points,tol=.0003):
 if len(points)<3:return points
 a,b=points[0],points[-1];dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
 def d(p):
  t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
  return (p[0]-a[0]-t*dx)**2+(p[1]-a[1]-t*dy)**2
 i=max(range(1,len(points)-1),key=lambda i:d(points[i]))
 if d(points[i])<=tol*tol:return [a,b]
 return dp(points[:i+1],tol)[:-1]+dp(points[i:],tol)
for start in sorted(ends):
 for nxt,eid in adj[start]:
  if eid in seen:continue
  seen.add(eid);chain=[start,nxt];ways={edges[eid][3]};name=edges[eid][2];current=nxt
  while current not in ends:
   opts=[(n,e) for n,e in adj[current] if e not in seen]
   if len(opts)!=1:break
   n,e=opts[0];seen.add(e);chain.append(n);ways.add(edges[e][3]);current=n
  if current==start:continue
  coords=dp([nodes[n] for n in chain])
  output.append({'id':'named-'+str(len(output)),'geometry':{'type':'LineString','coordinates':coords},'railwayNames':[name],'family':start[0],'sourceWayIds':sorted(ways),'geometrySource':'HOTOSM / OpenStreetMap','corridorMatch':'Reviewed named passenger corridor','geometryAccuracy':'approximate'})
print('Contracted named corridors',len(output),'points',sum(len(e['geometry']['coordinates']) for e in output),collections.Counter(e['family'] for e in output),flush=True)
source={'metadata':{'source':'HOTOSM / OSM','builtAt':date.today().isoformat(),'license':'ODbL-1.0'},'sourceSnapshot':args.snapshot,'edges':output,'excludedFreightNames':['瓦日','浩吉','大秦','朔黄','神朔'],'excludedEdges':None}
(raw/'physical-rails.json').write_text(json.dumps(source,ensure_ascii=False,separators=(',',':')))
