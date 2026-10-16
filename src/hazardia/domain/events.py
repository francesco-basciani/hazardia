"""Conservative event association, not calibrated probability estimation."""
from hazardia.io import timestamp
from hazardia.domain.contracts import validate_record,require
from hazardia.domain.state import identity

def overlap(a,b):return a[0]<=b[2] and a[2]>=b[0] and a[1]<=b[3] and a[3]>=b[1]

def associate(records,profile,as_of,*,association_s=3600):
    validate_record(profile);require(profile['kind']=='territory','INVALID_PROFILE','Territory required');require(association_s>0,'INVALID_INPUT','Positive research association window required');cutoff=timestamp(as_of);policy=profile['payload']['source_policy']
    require(timestamp(profile['available_at'])<=cutoff,'FUTURE_SOURCE','Profile unavailable at cutoff')
    unique={};excluded=[];events=[];ambiguous=[]
    for record in records:
        validate_record(record);require(record['kind']=='detection','INVALID_CONTRACT','Detection required')
        require(record['payload']['territory_id']==profile['id'],'TERRITORY_MISMATCH','Wrong observation territory')
        require(overlap(record['payload']['bbox_wgs84'],profile['payload']['bbox_wgs84']),'INVALID_GEOMETRY','Observation outside territory')
        if record['id'] in unique:require(identity(record)==identity(unique[record['id']]),'CONFLICTING_REVISION','Same ID changed observation')
        unique[record['id']]=record
    for record in sorted(unique.values(),key=lambda r:(timestamp(r['payload']['sensed_at']),r['id'])):
        p=record['payload'];age=(cutoff-timestamp(p['sensed_at'])).total_seconds()
        if timestamp(record['available_at'])>cutoff or age>policy['max_age_s'] or p['coverage']<policy['min_coverage']:
            excluded.append(dict(id=record['id'],reason='FUTURE_SOURCE' if timestamp(record['available_at'])>cutoff else 'STALE' if age>policy['max_age_s'] else 'PARTIAL'));continue
        matches=[e for e in events if e['hazard']==p['hazard'] and overlap(e['anchor_bbox'],p['bbox_wgs84']) and abs((timestamp(p['sensed_at'])-timestamp(e['anchor_at'])).total_seconds())<=association_s]
        if len(matches)>1:ambiguous.append(dict(observation_id=record['id'],candidate_event_ids=[e['id'] for e in matches]));continue
        if matches:event=matches[0]
        else:
            event=dict(id='event-'+identity([profile['id'],p['hazard'],record['id']])[:20],hazard=p['hazard'],anchor_bbox=p['bbox_wgs84'],anchor_at=p['sensed_at'],observations=[]);events.append(event)
        event['observations'].append(record)
    for event in events:
        readings=event['observations'];groups={r['payload']['correlation_group'] for r in readings}
        event.update(status='CONFLICT' if len({r['payload']['assessment'] for r in readings})>1 else 'CONSISTENT',confidence_score=min(r['payload']['confidence'] for r in readings),confidence_semantics='Uncalibrated conservative score; no independence/probability claim',correlation_groups=sorted(groups))
    return dict(schema_version='0.4.0',kind='event_snapshot',as_of=as_of,territory_id=profile['id'],events=events,ambiguous=ambiguous,excluded=excluded,duplicate_count=len(records)-len(unique))
