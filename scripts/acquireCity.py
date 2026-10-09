"""Resume one city at a time; reuse complete service facts across all cities."""
import argparse,hashlib,json,re,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from acquireJiangsu import RAW,BASE,Tables,fetch,date,parse_service,save
from originSources import services

def acquire(province,city,province_name,catalog_page=None):
    key=province+'-'+city; index_path=RAW/f'city-{key}-station-index.json'
    if index_path.exists():index=json.loads(index_path.read_text())
    else:
        doc=Tables(catalog_page if catalog_page is not None else fetch(BASE+'/'+province+'/'))
        names={h.split('/')[2]:n for h,n in doc.links if re.fullmatch('/'+province+r'/[^/]+/',h)}
        city_name=province_name if city==province else names[city]
        prefix='/'+province+'/' if city==province else '/'+province+'/'+city+'/'
        entries={h:{'name':n[:-1],'city':city_name,'cityId':key,'province':province_name,'provinceId':province,'sourceUrl':BASE+h}
                 for h,n in doc.links if re.fullmatch(re.escape(prefix)+r'[^/]+\.html',h) and n.endswith('站')}
        index=list(entries.values());assert index,'Empty city index';save(index_path,index)
    def major(s):return s['name'] in {s['city']+x for x in ('','东','西','南','北','虹桥')}
    index.sort(key=lambda s:(not major(s),s['name']))
    def read_station(s):
        try:page=fetch(s['sourceUrl'])
        except Exception as e:
            print('Station unavailable',s['name'],str(e),flush=True);return None
        doc=Tables(page)
        codes=sorted({h.rsplit('/',1)[-1][:-5].upper() for h,_ in doc.links if re.fullmatch(r'/huoche/[a-z0-9]+\.html',h)})
        try:snapshot=date(page)
        except ValueError:
            codes=[];snapshot='';print('No published timetable',s['name'],flush=True)
        print('Station',s['name'],len(codes),flush=True)
        return {**s,'candidateTrainNumbers':codes,'sourceUpdatedAt':snapshot,'sourceSha256':hashlib.sha256(page.encode()).hexdigest(),'retrievedAt':time.strftime('%Y-%m-%d')}
    # Finish the major-station phase first. Bounded parallel page requests
    # inside one city do not mix checkpoints from different cities.
    for is_major in (True,False):
        pending=[(i,s) for i,s in enumerate(index) if 'candidateTrainNumbers' not in s and major(s)==is_major]
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures={pool.submit(read_station,s):i for i,s in pending}
            for future in as_completed(futures):
                result=future.result()
                if result is not None:index[futures[future]]=result;save(index_path,index)
    codes={c for s in index for c in s.get('candidateTrainNumbers',[])};known=services();missing=sorted(codes-set(known))
    exclusion_path=RAW/'service-source-exclusions.json'
    if exclusion_path.exists():
        quarantine={e['trainNumber']:e for e in json.loads(exclusion_path.read_text())}
        missing=[c for c in missing if c not in quarantine or not any(c in s.get('candidateTrainNumbers',[]) and s.get('sourceUpdatedAt')==quarantine[c]['sourceUpdatedAt'] for s in index)]
    service_path=RAW/f'city-{key}-services.json';records=json.loads(service_path.read_text()) if service_path.exists() else []
    print(key,'stations',len(index),'new services',len(missing),flush=True);failures=[]
    def read_service(code):return parse_service(code,fetch(BASE+'/huoche/'+code.lower()+'.html'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(read_service,c):c for c in missing}
        for i,future in enumerate(as_completed(futures),1):
            code=futures[future]
            try:records.append(future.result())
            except Exception as e:failures.append({'trainNumber':code,'error':str(e)})
            if i%40==0 or i==len(missing):save(service_path,sorted(records,key=lambda r:r['trainNumber']));print('Services',i,'/',len(missing),'failures',len(failures),flush=True)
    if not service_path.exists():save(service_path,records)
    save(RAW/f'city-{key}-acquisition.json',{'retrievedAt':time.strftime('%Y-%m-%d'),'city':index[0]['city'],'stationCount':len(index),'candidateServices':len(codes),'acquiredAdditionalServices':len(records),'failedPages':failures,'stationIssues':[s['name'] for s in index if not s.get('candidateTrainNumbers')]})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('province');p.add_argument('city');p.add_argument('province_name');a=p.parse_args();acquire(a.province,a.city,a.province_name)
