"""Reject physically impossible stop-table joins; never infer a new service."""
import math

def distance_km(a,b):
    lat1,lat2=map(math.radians,[a['latitude'],b['latitude']])
    dlat=lat2-lat1;dlon=math.radians(b['longitude']-a['longitude'])
    hav=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371*2*math.asin(min(1,math.sqrt(hav)))

def impossible_intervals(record,stations):
    elapsed=record.get('elapsedMinutes')
    if elapsed is None or len(elapsed)!=len(record['stopNames']):return []
    located=[(i,name) for i,name in enumerate(record['stopNames']) if name in stations]
    maximum=400 if record['category'] in ('G','C','D') else 240
    failures=[]
    for (i,a),(j,b) in zip(located,located[1:]):
        minutes=elapsed[j]-elapsed[i]
        distance=distance_km(stations[a],stations[b])
        # Five kilometres allow minute rounding and station-coordinate
        # uncertainty. The speed bound is deliberately generous.
        if minutes>=0 and distance>minutes/60*maximum+5:
            failures.append({'from':a,'to':b,'distanceKm':round(distance,2),'elapsedMinutes':minutes,'maximumSpeedKmh':maximum})
    return failures
