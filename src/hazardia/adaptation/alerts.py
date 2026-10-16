"""Versioned impact-based advisory lifecycle using explicitly qualified inputs."""
import copy,math
from hazardia.io import timestamp,HazardError
from hazardia.domain.state import identity

class AlertBook:
    def __init__(self):self.alerts={};self.history=[]
    def update(self,forecast,*,event_id,at,predicted_exposure,threshold,effect_known,qualification):
        if forecast.get('kind')!='weather_ensemble' or forecast['payload'].get('data_kind')!='FORECAST':raise HazardError('SOURCE_KIND','Issued forecast required')
        from hazardia.domain.contracts import validate_record
        validate_record(forecast);p=forecast['payload'];now=timestamp(at)
        if timestamp(forecast['available_at'])>now or not (timestamp(p['issued_at'])<=now<timestamp(p['valid_until'])):raise HazardError('STALE_FORECAST','Unavailable or expired forecast')
        if qualification!='SYNTHETIC_RESEARCH' or predicted_exposure is None or not effect_known:raise HazardError('UNKNOWN_EFFECT','This alert rule only supports declared synthetic impact fixtures')
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in [predicted_exposure,threshold]):raise HazardError('INVALID_INPUT','Finite nonnegative impact/threshold required')
        key=identity([event_id,p['territory_id'],p['valid_from'],p['valid_until']])[:24];old=self.alerts.get(key)
        if old and (timestamp(p['issued_at'])<timestamp(old['issued_at']) or now<timestamp(old['at'])):raise HazardError('OUT_OF_ORDER','Older forecast revision rejected')
        if old and old['forecast_id']==forecast['id']:
            if old['source_hash']!=identity(forecast):raise HazardError('IDENTITY_CONFLICT','Same forecast id with changed content')
            return copy.deepcopy(old)
        state='OPEN' if predicted_exposure>=threshold else 'RESOLVED'
        if old and state=='OPEN':state='UPDATED'
        record=dict(schema_version='0.5.0',id=key,event_id=event_id,forecast_id=forecast['id'],source_hash=identity(forecast),issued_at=p['issued_at'],at=at,state=state,revision=1 if old is None else old['revision']+1,predicted_exposure=predicted_exposure,threshold=threshold,valid_from=p['valid_from'],valid_until=p['valid_until'],lead_s=(timestamp(p['valid_from'])-now).total_seconds(),qualification=qualification,operational_authority=False)
        self.alerts[key]=record;self.history.append(copy.deepcopy(record));return copy.deepcopy(record)
    def acknowledge(self,key,at):
        old=self.alerts[key]
        if old['state'] not in ['OPEN','UPDATED']:raise HazardError('INVALID_TRANSITION','Only open/updated advisories can be acknowledged')
        if timestamp(at)<timestamp(old['at']) or timestamp(at)>=timestamp(old['valid_until']):raise HazardError('INVALID_TIME','Acknowledgment outside live advisory interval')
        record=dict(old,state='ACKNOWLEDGED',at=at,revision=old['revision']+1);self.alerts[key]=record;self.history.append(copy.deepcopy(record));return copy.deepcopy(record)
    def expire(self,at):
        for key,old in list(self.alerts.items()):
            if timestamp(at)>=timestamp(old['valid_until']) and old['state'] not in ['EXPIRED','RESOLVED']:
                record=dict(old,state='EXPIRED',at=at,revision=old['revision']+1);self.alerts[key]=record;self.history.append(copy.deepcopy(record))
        return copy.deepcopy(self.alerts)
