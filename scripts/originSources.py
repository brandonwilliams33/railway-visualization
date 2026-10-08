"""Shared, offline origin manifests. A city is added without changing Jiangsu."""
import json
from pathlib import Path
RAW=Path(__file__).resolve().parents[1]/'data/raw'
def read(path):return json.loads(path.read_text())
def indexes():
    result=[{**s,'province':'江苏','provinceId':'jiangsu'} for s in read(RAW/'jiangsu-station-index.json')]
    for path in sorted(RAW.glob('city-*-station-index.json')):result.extend(read(path))
    release_path=RAW/'expansion-release.json'
    paused=set(read(release_path).get('pausedCityIds',[])) if release_path.exists() else set()
    result=[s for s in result if s['cityId'] not in paused]
    corrections_path=RAW/'origin-index-corrections.json'
    corrections={(s['name'],s['sourceCityId']):s for s in read(corrections_path)} if corrections_path.exists() else {}
    result=[{**s,**{k:v for k,v in corrections.get((s['name'],s['cityId']),{}).items() if k in ('city','cityId','province','provinceId','identitySource')}} for s in result]
    exclusions_path=RAW/'origin-index-exclusions.json'
    excluded={(s['name'],s['cityId']) for s in read(exclusions_path)} if exclusions_path.exists() else set()
    result=[s for s in result if (s['name'],s['cityId']) not in excluded]
    assert len({s['name'] for s in result})==len(result),'Duplicate origin names'
    return result
def services():
    rows={}
    for path in [RAW/'passenger-services.json',RAW/'jiangsu-services.json',*sorted(RAW.glob('city-*-services.json'))]:
        rows.update({r['trainNumber']:r for r in read(path)})
    return rows
