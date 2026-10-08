"""Acquire factual Jiangsu station indexes and complete passenger stop tables.

Resumable, bounded concurrency, stdlib only. Pages are reduced to facts with
URL/date/hash provenance; unverified indexes never create direct services.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
import argparse, hashlib, json, re, time, urllib.request, subprocess

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
BASE = 'https://www.crecc.com'

class Tables(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.links=[]; self.rows=[]; self.text=[]
        self.row=None; self.cell=None; self.href=None; self.anchor=[]
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='tr': self.row=[]
        if tag in ('td','th') and self.row is not None: self.cell=[]
        if tag=='a': self.href=attrs.get('href',''); self.anchor=[]
    def handle_data(self, value):
        self.text.append(value)
        if self.cell is not None: self.cell.append(value)
        if self.href is not None: self.anchor.append(value)
    def handle_endtag(self, tag):
        if tag=='a' and self.href is not None:
            self.links.append((self.href,''.join(self.anchor).strip())); self.href=None
        if tag in ('td','th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split())); self.cell=None
        if tag=='tr' and self.row is not None:
            self.rows.append(self.row); self.row=None

def fetch(url):
    last=None
    for attempt in range(2):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Railbound-data/1.0 (public timetable facts; bounded requests)'})
            with urllib.request.urlopen(req,timeout=12) as response: return response.read().decode('utf-8')
        except Exception as error:
            last=error
            if 'SSL' in str(error):
                try:
                    result=subprocess.run(['curl','-fL','--max-time','12','--retry','0','-sS',url],capture_output=True,check=True)
                    return result.stdout.decode('utf-8')
                except Exception:pass
            time.sleep(.5*(attempt+1))
    raise last

def date(page):
    match=re.search(r'数据更新时间\s*[：:]\s*(\d{4}-\d{2}-\d{2})',page)
    if not match: raise ValueError('Missing source snapshot date')
    return match.group(1)

def elapsed(text):
    if not text or text=='----': return 0
    hours=re.search(r'(\d+)小时',text); minutes=re.search(r'(\d+)分钟',text)
    if hours or minutes: return int(hours.group(1) if hours else 0)*60+int(minutes.group(1) if minutes else 0)
    clock=re.fullmatch(r'(\d+):(\d+)',text)
    if clock: return int(clock.group(1))*60+int(clock.group(2))
    raise ValueError('Unknown running duration: '+text)

def parse_service(code, page):
    doc=Tables(page)
    rows=[r for r in doc.rows if len(r)==7 and r[0].isdigit()]
    if len(rows)<2: raise ValueError('No complete passenger stop table')
    if [int(r[0]) for r in rows]!=list(range(1,len(rows)+1)):
        raise ValueError('Incomplete or out-of-order station rows')
    stops=[r[1] for r in rows]; times=[elapsed(r[5]) for r in rows]
    bad=[i+1 for i in range(1,len(times)) if times[i]<times[i-1]]
    category=code[0] if code[0] in 'GCDZTK' else 'OTHER'
    return {'trainNumber':code,'category':category,'stopNames':stops,'passenger':True,
            'sourceUrl':f'{BASE}/huoche/{code.lower()}.html','sourceUpdatedAt':date(page),
            'sourceSha256':hashlib.sha256(page.encode()).hexdigest(),
            'elapsedMinutes':times,'sourceValidation':{'elapsedTimeMonotonic':not bad,'regressionRows':bad}}

def station_index(page):
    doc=Tables(page); cities=dict((href.split('/')[2],name) for href,name in doc.links if re.fullmatch(r'/jiangsu/[^/]+/',href))
    result={}
    for href,name in doc.links:
        if re.fullmatch(r'/jiangsu/[^/]+/[^/]+\.html',href) and name.endswith('站'):
            slug=href.split('/')[2]; result[href]={'name':name[:-1],'city':cities[slug],'cityId':slug,'sourceUrl':BASE+href}
    return list(result.values())

def save(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def acquire(index_only=False, max_new=None):
    RAW.mkdir(exist_ok=True)
    index_path=RAW/'jiangsu-station-index.json'
    if index_path.exists(): indexes=json.loads(index_path.read_text())
    else:
        indexes=station_index(fetch(BASE+'/jiangsu/')); save(index_path,indexes)
    # Visit major cities first; small stations then add services absent at hubs.
    def priority(station):
        return (not (station['name']==station['city'] or station['name'] in [station['city']+x for x in ('南','北','东','西')]),station['city'],station['name'])
    missing=[s for s in sorted(indexes,key=priority) if 'candidateTrainNumbers' not in s]
    def read_station(station):
        page=fetch(station['sourceUrl']); doc=Tables(page)
        codes=sorted({href.rsplit('/',1)[-1][:-5].upper() for href,_ in doc.links if re.fullmatch(r'/huoche/[a-z0-9]+\.html',href)})
        return {**station,'candidateTrainNumbers':codes,'sourceUpdatedAt':date(page),'sourceSha256':hashlib.sha256(page.encode()).hexdigest(),'retrievedAt':time.strftime('%Y-%m-%d')}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(read_station,s):s for s in missing}
        for future in as_completed(futures):
            station=futures[future]
            try:
                record=future.result(); indexes[indexes.index(station)]=record
                print('Station',record['name'],len(record['candidateTrainNumbers']),flush=True)
            except Exception as error: print('Station failed',station['name'],str(error),flush=True)
            save(index_path,indexes)
    codes={code for s in indexes for code in s.get('candidateTrainNumbers',[])}
    original=json.loads((RAW/'passenger-services.json').read_text())
    known={s['trainNumber'] for s in original}
    service_path=RAW/'jiangsu-services.json'; records=json.loads(service_path.read_text()) if service_path.exists() else []
    known.update(s['trainNumber'] for s in records)
    missing=sorted(codes-known)
    print('Indexed stations',sum('candidateTrainNumbers' in s for s in indexes),'candidate services',len(codes),'existing',len(codes&known),'new',len(missing),flush=True)
    if index_only:return
    if max_new is not None:missing=missing[:max_new]
    failures=[]
    def read_service(code): return parse_service(code,fetch(f'{BASE}/huoche/{code.lower()}.html'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(read_service,code):code for code in missing}
        for i,future in enumerate(as_completed(futures),1):
            code=futures[future]
            try:records.append(future.result())
            except Exception as error:failures.append({'trainNumber':code,'error':str(error)})
            if i%40==0 or i==len(missing):
                save(service_path,sorted(records,key=lambda r:r['trainNumber']));print('Services',i,'/',len(missing),'failures',len(failures),flush=True)
    save(RAW/'jiangsu-acquisition.json',{'retrievedAt':time.strftime('%Y-%m-%d'),'stationCount':len(indexes),'candidateServices':len(codes),'acquiredAdditionalServices':len(records),'failedPages':failures})

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--index-only',action='store_true');parser.add_argument('--max-new',type=int)
    args=parser.parse_args();acquire(args.index_only,args.max_new)
