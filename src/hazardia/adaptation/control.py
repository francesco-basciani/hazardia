"""Persisted, explicitly synthetic fault/forecast replay. Never operational health."""
import copy,uuid,math
from pathlib import Path
from hazardia.io import load,write_new,utcnow,HazardError
from hazardia.domain.state import identity
from hazardia.adaptation.alerts import AlertBook
FAULTS=('safety_unknown','flood_worker','source_stale','coordinator_down','solver_down','road_closed','resource_loss')
CAPS=('SAFETY_CHECK','SITUATIONAL_AWARENESS','RESOURCE_ALLOCATION','REGIONAL_COORDINATION','FORECASTING','EXPLAINABILITY')

def replay_forecast(index):
    issued=['12:00','12:15','12:30'][index]
    return dict(schema_version='0.4.0',kind='weather_ensemble',id='authored-forecast-'+str(index),available_at='2024-07-13T'+issued+':00Z',provenance=dict(source='HAZARDIA authored forecast replay, not measured weather',license='AUTHORED_RESEARCH_FIXTURE',qualification='SYNTHETIC_RESEARCH'),payload=dict(territory_id='abruzzo-laquila-research',bbox_wgs84=[13.36,42.33,13.40,42.37],spatial_resolution_m=25000,data_kind='FORECAST',issued_at='2024-07-13T'+issued+':00Z',valid_from='2024-07-13T13:00:00Z',valid_until='2024-07-13T14:00:00Z',step_s=3600,units=dict(precipitation='mm',wind_speed_10m='m/s',wind_direction_10m='°',temperature_2m='°C',relative_humidity_2m='%',surface_pressure='hPa',shortwave_radiation='W/m²'),members=[dict(id='control',weight=1,records=[dict(at='2024-07-13T13:00:00Z',values=dict(precipitation=[10,20,0][index],wind_speed_10m=2,wind_direction_10m=90,temperature_2m=20,relative_humidity_2m=50,surface_pressure=1000,shortwave_radiation=100))])]))

class ResearchControl:
    def __init__(self,directory):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True);paths=sorted(self.directory.glob('event-*.json'))
        self.state=load(paths[-1]) if paths else dict(revision=0,faults=[],forecast_index=-1,alerts={},alert_history=[],at=utcnow(),qualification='SYNTHETIC_RESEARCH',operational_authority=False)
    def vector(self):
        f=set(self.state['faults']);states={c:'NOMINAL' for c in CAPS};causes={c:'Research software fixture only; no operational qualification' for c in CAPS}
        for c in ['SITUATIONAL_AWARENESS','FORECASTING']:states[c]='DEGRADED';causes[c]='Uncalibrated historical maps / authored forecast replay only'
        rules={'safety_unknown':{'SAFETY_CHECK':'UNAVAILABLE','RESOURCE_ALLOCATION':'UNAVAILABLE'},'flood_worker':{'FORECASTING':'DEGRADED'},'source_stale':{'SITUATIONAL_AWARENESS':'DEGRADED','FORECASTING':'UNAVAILABLE'},'coordinator_down':{'REGIONAL_COORDINATION':'UNAVAILABLE'},'solver_down':{'RESOURCE_ALLOCATION':'UNAVAILABLE'},'road_closed':{'RESOURCE_ALLOCATION':'DEGRADED'},'resource_loss':{'RESOURCE_ALLOCATION':'DEGRADED'}}
        rank={'NOMINAL':0,'DEGRADED':1,'UNAVAILABLE':2}
        for fault in sorted(f):
            for c,s in rules[fault].items():
                if rank[s]>=rank[states[c]]:states[c]=s;causes[c]=fault+' (controlled injection)'
        return [dict(capability=c,state=states[c],cause=causes[c],confidence='CONTROLLED_FIXTURE_ONLY',source_age_s=0,at=self.state['at']) for c in CAPS]
    def snapshot(self):return dict(copy.deepcopy(self.state),capabilities=self.vector(),scope='Controlled replay health; actual Linux jobs are separately reported')
    def action(self,body):
        if set(body)-{'action','fault','expected_revision'}:raise HazardError('INVALID_INPUT','Unknown replay fields')
        if body.get('expected_revision')!=self.state['revision']:raise HazardError('STALE_REVISION','Refresh state before changing the replay')
        state=copy.deepcopy(self.state);action=body.get('action');proof=None
        if action=='inject':
            if body.get('fault') not in FAULTS:raise HazardError('INVALID_INPUT','Unknown controlled fault')
            state['faults']=sorted(set(state['faults'])|{body['fault']})
        elif action=='recover':
            # Explicitly new authored positive evidence, never a claim of repairing a real outage.
            proof=dict(id='synthetic-positive-'+uuid.uuid4().hex,at=utcnow(),previous_revision=state['revision'],available_components=list(CAPS),qualification='AUTHORED_POSITIVE_FIXTURE',meaning='New controlled availability observation, not measured infrastructure repair')
            state['faults']=[]
        elif action=='forecast_reset':
            state.update(forecast_index=-1,alerts={},alert_history=[])
        elif action in ['forecast','ack','expire']:
            book=AlertBook();book.alerts=state['alerts'];book.history=state['alert_history']
            if action=='forecast':
                if 'source_stale' in state['faults']:raise HazardError('STALE_FORECAST','Forecast unavailable in controlled fault state')
                index=(state['forecast_index']+1)%3;state['forecast_index']=index;forecast=replay_forecast(index)
                # A new cycle is a separate replay, rather than an out-of-order meteorological update.
                if index==0:book=AlertBook();state['replay_cycle']=state.get('replay_cycle',0)+1
                book.update(forecast,event_id='controlled-flood-event-cycle-'+str(state.get('replay_cycle',0)),at=forecast['available_at'],predicted_exposure=[45,50,20][index],threshold=35,effect_known=True,qualification='SYNTHETIC_RESEARCH')
            elif action=='ack':
                if not book.alerts:raise HazardError('INVALID_TRANSITION','Generate an advisory first')
                key=next(iter(book.alerts));book.acknowledge(key,book.alerts[key]['at'])
            else:book.expire('2024-07-13T14:00:00Z')
            state['alerts']=book.alerts;state['alert_history']=book.history[-100:]
        else:raise HazardError('INVALID_INPUT','Unknown research action')
        state.update(revision=state['revision']+1,at=utcnow(),action=action,positive_evidence=proof)
        write_new(self.directory/('event-%010d.json'%state['revision']),state);self.state=state;return self.snapshot()
    def apply(self,p):
        f=set(self.state['faults'])
        if 'safety_unknown' in f:raise HazardError('SAFETY_UNVERIFIED','Controlled missing critical safety input; maps remain readable')
        if 'solver_down' in f:raise HazardError('DEPENDENCY_UNAVAILABLE','Controlled solver outage; historical maps remain readable')
        if 'source_stale' in f:raise HazardError('STALE_PRODUCT','Controlled stale source: cached maps are historical, no new proposal')
        if 'flood_worker' in f and any(e['hazard']=='FLOOD' for e in p['events']):raise HazardError('DEPENDENCY_UNAVAILABLE','Controlled flood forecast outage; FIRE remains available')
        homes={r['id']:r['home_region'] for r in p['resources']};regions={e['id']:e['region'] for e in p['events']}
        for o in p['options']:
            if 'coordinator_down' in f and homes[o['resource_id']]!=regions[o['event_id']]:o['authorization']=False
            if 'road_closed' in f:o['road_open']=False
        if 'resource_loss' in f:p['resources'][0]['record']['payload']['maintenance']='UNAVAILABLE'
        return p
