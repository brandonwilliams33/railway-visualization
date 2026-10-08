"""Shared, offline origin manifests. A city is added without changing Jiangsu."""
import json
from pathlib import Path
RAW=Path(__file__).resolve().parents[1]/'data/raw'
def read(path):return json.loads(path.read_text())
def indexes():
    result=[{**s,'province':'江苏','provinceId':'jiangsu'} for s in read(RAW/'jiangsu-station-index.json')]
    for path in sorted(RAW.glob('city-*-station-index.json')):result.extend(read(path))
    assert len({s['name'] for s in result})==len(result),'Duplicate origin names'
    return result
def services():
    rows={}
    for path in [RAW/'passenger-services.json',RAW/'jiangsu-services.json',*sorted(RAW.glob('city-*-services.json'))]:
        rows.update({r['trainNumber']:r for r in read(path)})
    return rows
