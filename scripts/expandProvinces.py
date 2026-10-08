"""Expand source-listed cities sequentially, with a checkpoint for each city."""
import argparse, json, re, time
from acquireCity import acquire
from acquireJiangsu import BASE, RAW, Tables, fetch, save

def expand(province, name):
    for attempt in range(3):
        try:
            page=fetch(BASE+'/'+province+'/');break
        except Exception:
            if attempt==2:raise
            time.sleep(2)
    doc=Tables(page)
    cities={href.split('/')[2]:city for href,city in doc.links if re.fullmatch('/'+province+r'/[^/]+/',href)}
    if not cities:
        cities={province:name}
    completed=[];failures=[]
    for city, city_name in cities.items():
        print('\nCITY',province,city_name,flush=True)
        try:
            acquire(province,city,name,page)
            completed.append(city)
        except Exception as error:
            failures.append({'city':city,'error':str(error)})
            print('City acquisition unavailable',city,str(error),flush=True)
        save(RAW/f'province-{province}-acquisition.json',{'completedCities':completed,'failedCities':failures})
    # Retry only failed station-page requests, rather than treating a network
    # error as evidence that a passenger station has closed.
    for city in completed:
        index=json.loads((RAW/f'city-{province}-{city}-station-index.json').read_text())
        if any('candidateTrainNumbers' not in station for station in index):
            print('\nRETRY CITY',province,city,flush=True)
            acquire(province,city,name,page)
    return failures

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('provinces',nargs='+',help='province-id:Chinese-name')
    args=parser.parse_args()
    for item in args.provinces:
        province,name=item.split(':',1)
        expand(province,name)
