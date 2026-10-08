"""Store shared service interval paths once, without changing passenger facts."""

def compact_network(data):
    segment_indices = {segment['id']: i for i, segment in enumerate(data['segments'])}
    paths = []
    path_indices = {}
    services = []
    for service in data['services']:
        refs = []
        for leg in service['segmentIds']:
            key = tuple(segment_indices[sid] for sid in leg)
            if key not in path_indices:
                path_indices[key] = len(paths)
                paths.append(list(key))
            refs.append(path_indices[key])
        services.append({**{k: v for k, v in service.items() if k != 'segmentIds'}, 'segmentPathIndexes': refs})
    networks = {hub: {k: v for k, v in network.items() if k != 'railwaySegmentIds'} for hub, network in data['networks'].items()}
    return {**data, 'schemaVersion': 2, 'segmentPaths': paths, 'services': services, 'networks': networks}
