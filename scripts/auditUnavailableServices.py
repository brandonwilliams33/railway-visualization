"""Retry missing timetable sources and quarantine demonstrably incomplete snapshots."""
import hashlib,json,re,time
from concurrent.futures import ThreadPoolExecutor
from acquireJiangsu import RAW,BASE,fetch,parse_service,Tables,date,save
from originSources import services

if __name__=='__main__':
    candidates=set()
    for path in RAW.glob('*station-index.json'):
        if path.name.startswith('city-') and not path.with_name(path.name.replace('-station-index.json','-acquisition.json')).exists():continue
        for entry in json.loads(path.read_text()):candidates.update(entry.get('candidateTrainNumbers',[]))
    known=services();codes=sorted(candidates-set(known))
    path=RAW/'service-source-exclusions.json'
    exclusions={e['trainNumber']:e for e in json.loads(path.read_text())} if path.exists() else {}
    recovery=RAW/'city-service-recovery-services.json'
    recovered={r['trainNumber']:r for r in json.loads(recovery.read_text())} if recovery.exists() else {}
    def retry(code):
        try:
            page=fetch(BASE+'/huoche/'+code.lower()+'.html')
            try:return code,parse_service(code,page),None
            except ValueError as error:
                rows=[r for r in Tables(page).rows if len(r)==7 and r[0].isdigit()]
                # A published header and date with a missing/incomplete stop
                # table is evidence of unusable input, never a service fact.
                if code.lower() not in page.lower():raise
                snapshot=date(page)
                quarantine={'trainNumber':code,'sourceUrl':BASE+'/huoche/'+code.lower()+'.html','sourceUpdatedAt':snapshot,'retrievedAt':time.strftime('%Y-%m-%d'),'sourceSha256':hashlib.sha256(page.encode()).hexdigest(),'reason':str(error),'completeStopRowCount':len(rows)}
                return code,None,quarantine
        except Exception as error:
            print('Still unavailable',code,str(error),flush=True);return code,None,None
    print('Retry missing services',len(codes),flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for code,record,quarantine in pool.map(retry,codes):
            if record:
                recovered[code]=record;exclusions.pop(code,None);print('Recovered',code,flush=True)
            elif quarantine:
                exclusions[code]=quarantine;print('Incomplete source quarantined',code,quarantine['reason'],flush=True)
            save(recovery,list(recovered.values()));save(path,list(exclusions.values()))
