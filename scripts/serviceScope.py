"""Keep cross-border source stops without conflating domestic same-name stations."""
def out_of_scope_stops(record,rules):
    stops=set(record['stopNames']);outside=set()
    for rule in rules:
        if record['trainNumber'] not in rule['trainNumbers'] or record['sourceUpdatedAt']!=rule['sourceUpdatedAt']:continue
        if not set(rule['requiredStops']).issubset(stops):continue
        outside.update(stops.intersection(rule['outsideStationNames']))
    return outside
