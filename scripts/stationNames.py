"""Only official, evidenced former names of the same railway station normalize."""
import json
from pathlib import Path
path=Path(__file__).resolve().parents[1]/'data/raw/station-name-evidence.json'
facts=json.loads(path.read_text())['stations'] if path.exists() else []
ALIASES={r['sourceName']:r['currentName'] for r in facts}
def canonical(name):return ALIASES.get(name,name)
def former_names(name):return [old for old,current in ALIASES.items() if current==name]
