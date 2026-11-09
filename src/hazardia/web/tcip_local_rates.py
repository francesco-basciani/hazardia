"""Bounded private local-rate consumer contracts. No provider databases/models imported."""
import hashlib
import json
import re
from datetime import date,timedelta
from urllib.parse import urlsplit,parse_qs
from .tcip_client import invalid,finite,UUID

CODE=re.compile(r'(?:[0-9]{6}(?::(?:Q[1-5]|A[1-3]-[0-9]{1,4}))?|P[0-9]{3}|R[0-9]{2}|IT)')
LEVELS=('best_available','country','region','province','municipality','neighborhood')
KEY=re.compile(r'[a-f0-9]{20}')
CRIMES={'all_recorded_offences','theft','robbery','assault','fraud','property_damage','extortion','drug_offences','burglary.commercial','burglary.residential','theft.commercial','theft.pickpocket','theft.snatch','attempted_homicide','battery','threats','sexual_violence','femicide','female_homicide','femicide_monitoring_nudm'}


VICTIM_SERIES={
 'femicide':('statistical_estimate','istat-gender-related-killings-estimate-2019-2024'),
 'female_homicide':('recorded_victims','istat-female-homicide-victims-2019-2024'),
 'femicide_monitoring_nudm':('civil_society_monitoring','nudm-explicit-femicide-monitoring-2024-2026'),
}

def victim_contract(m):
    expected=VICTIM_SERIES.get(m.get('crime_code'))
    if expected:
        if m.get('level')!='country' or m.get('count_unit')!='victims' or m.get('national_only') is not True or m.get('denominator_scope')!='all_residents' or (m.get('count_kind'),m.get('definition_id'))!=expected:invalid()
    elif m.get('level')=='country' or m.get('count_unit') is not None:invalid()
    return bool(expected)


def local_path(path):
    if len(path)>1200 or any(c.isspace() or ord(c)<32 for c in path):return False
    try:p=urlsplit(path)
    except ValueError:return False
    if p.scheme or p.netloc or p.fragment:return False
    query=parse_qs(p.query,keep_blank_values=True)
    if any(len(v)!=1 for v in query.values()):return False
    if p.path=='/api/v1/geo/territorial-rates':return not query or set(query)=={'dataset'} and bool(KEY.fullmatch(query['dataset'][0]))
    if p.path=='/api/v1/geo/territorial-lookup':
        return set(query)=={'q','year'} and 2<=len(query['q'][0])<=80 and query['year'][0] in ('2024','2025','2026')
    if p.path=='/api/v1/geo/territorial-context':
        if set(query)!={'bbox','level','year'} or query['level'][0] not in ('municipality','neighborhood') or query['year'][0] not in ('2024','2025','2026'):return False
        try:w,s,e,n=[float(x) for x in query['bbox'][0].split(',')]
        except (ValueError,TypeError):return False
        return all(finite(x) for x in (w,s,e,n)) and 5<=w<e<=20 and 35<=s<n<=49 and e-w<=2 and n-s<=2
    return False


def calendar(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):invalid()
    try:return date.fromisoformat(value)
    except ValueError:invalid()


def catalogue_contract(data):
    if not isinstance(data,dict) or data.get('schema')!='tcip.territorial-rate-catalog/1.0' or data.get('private_research') is not True or data.get('complete_national_crime_counts') is not False:invalid()
    items=data.get('items');seen=set()
    if not isinstance(items,list) or len(items)>750:invalid()
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not KEY.fullmatch(item['id']) or item['id'] in seen:invalid()
        seen.add(item['id'])
        if item.get('level') not in LEVELS or item.get('crime_code') not in CRIMES or type(item.get('areas')) is not int or not 1<=item['areas']<=2000:invalid()
        if calendar(item.get('period_start'))>calendar(item.get('period_end')):invalid()
        if item.get('aggregation') is not None:
            if item['aggregation']!='cumulative' or item.get('window') not in ('all','3','5','10','2018-2024'):invalid()
            expected=hashlib.sha256(json.dumps(['cumulative',item['level'],item['crime_code'],item['window']],separators=(',',':')).encode()).hexdigest()[:20]
            if item['id']!=expected:invalid()
        if not isinstance(item.get('crime_label'),str) or len(item['crime_label'])>150 or not isinstance(item.get('title'),str) or len(item['title'])>400:invalid()
    categories=data.get('crime_types')
    if categories is not None:
        if not isinstance(categories,list) or not 1<=len(categories)<=32:invalid()
        codes=set();observed={item['crime_code'] for item in items}
        for category in categories:
            if not isinstance(category,dict) or set(category)!={'code','label','definition','definition_source','availability'}:invalid()
            code=category.get('code')
            if code not in CRIMES or code in codes:invalid()
            codes.add(code)
            for field,limit in [('label',150),('definition',1000),('definition_source',500)]:
                if not isinstance(category.get(field),str) or len(category[field])>limit:invalid()
            if not category['label'] or (category['definition_source'] and not category['definition_source'].startswith('https://')):invalid()
            if category['availability']!=('available' if code in observed else 'no_qualified_territorial_data'):invalid()
        if not observed<=codes:invalid()
    if not isinstance(data.get('coverage'),dict):invalid()
    return data


def polygons(features,maximum):
    if not isinstance(features,list) or len(features)>maximum:invalid()
    seen=set();pairs=0
    for f in features:
        if not isinstance(f,dict) or f.get('type')!='Feature':invalid()
        code=f.get('id');p=f.get('properties',{});g=f.get('geometry',{})
        if not isinstance(code,str) or not CODE.fullmatch(code) or code in seen or not isinstance(p,dict) or not isinstance(g,dict):invalid()
        seen.add(code)
        if p.get('code')!=code or not isinstance(p.get('name'),str) or len(p['name'])>200 or p.get('level') not in ('country','region','province','municipality','neighborhood'):invalid()
        if (code=='IT')!=(p['level']=='country'):invalid()
        if (':' in code)!=(p['level']=='neighborhood') or code.startswith('P')!=(p['level']=='province') or code.startswith('R')!=(p['level']=='region'):invalid()
        if g.get('type') not in ('Polygon','MultiPolygon') or not isinstance(g.get('coordinates'),list):invalid()
        for polygon in ([g['coordinates']] if g['type']=='Polygon' else g['coordinates']):
            if not isinstance(polygon,list) or not polygon:invalid()
            for ring in polygon:
                if not isinstance(ring,list) or len(ring)<4 or ring[0]!=ring[-1]:invalid()
                for pair in ring:
                    pairs+=1
                    if pairs>100000 or not isinstance(pair,list) or len(pair)!=2 or not all(finite(v) for v in pair) or not (-180<=pair[0]<=180 and -90<=pair[1]<=90):invalid()


def layer_contract(data):
    if isinstance(data,dict) and data.get("profile")=="tcip.cumulative-population-rate/1.0":return cumulative_contract(data)
    if not isinstance(data,dict) or data.get('type')!='FeatureCollection' or data.get('profile') not in ('tcip.territorial-population-rate/1.0','tcip.territorial-population-rate/1.1') or not isinstance(data.get('dataset_id'),str) or not KEY.fullmatch(data['dataset_id']):invalid()
    m=data.get('metadata',{})
    if not isinstance(m,dict) or m.get('private_research') is not True or m.get('population_normalized') is not True or m.get('forecast_probability') is not None or m.get('annualized') is not False or m.get('rates_are_probabilities') is not False or m.get('national_reference') is not None:invalid()
    victim=victim_contract(m)
    if m.get('metric')!=('victims_per_100000_resident_stock' if victim else 'recorded_offences_per_100000_resident_stock') or m.get('crime_code') not in CRIMES or m.get('level') not in LEVELS:invalid()
    start,end=calendar(m.get('period_start')),calendar(m.get('period_end'))
    if start>end:invalid()
    semantic_key=hashlib.sha256(json.dumps([m['level'],m['crime_code'],m['period_start'],m['period_end']],separators=(',',':')).encode()).hexdigest()[:20]
    if semantic_key!=data['dataset_id']:invalid()
    features=data.get('features');polygons(features,2000)
    if not features:invalid()
    for f in features:
        p=f['properties']
        allowed={'code','name','level','crime_code','crime_label','count','population','population_date','population_provisional','population_basis','period_start','period_end','count_source_id','count_source_url','population_source_id','population_source_url','territory_matched','count_provisional','geometry_edition','rate_per_100000','status','source_area_code'}
        if set(p)-allowed:invalid()
        if p.get('crime_code')!=m['crime_code'] or (m['level']!='best_available' and p.get('level')!=m['level']) or p.get('period_start')!=m['period_start'] or p.get('period_end')!=m['period_end'] or p.get('territory_matched') is not True:invalid()
        count,pop,rate=p.get('count'),p.get('population'),p.get('rate_per_100000')
        if type(count) is not int or count<0 or type(pop) is not int or pop<=0 or pop>1000000000 or not finite(rate) or rate<0 or abs(rate-count/pop*100000)>1e-7 or p.get('status')!='observed':invalid()
        allowed_dates={date(start.year,1,1),date(start.year,1,1)-timedelta(days=1)}
        if p.get('population_basis')=='next_1_january_stock_equivalent_to_31_december' and start==date(start.year,1,1) and end==date(start.year,12,31):allowed_dates.add(end)
        if calendar(p.get('population_date')) not in allowed_dates:invalid()
        if type(p.get('population_provisional')) is not bool or type(p.get('count_provisional')) is not bool:invalid()
        for key in ('count_source_id','population_source_id'):
            if not UUID.fullmatch(p.get(key,'')):invalid()
        for key in ('count_source_url','population_source_url'):
            if not isinstance(p.get(key),str) or len(p[key])>2048 or not p[key].startswith('https://'):invalid()
    if m['level']=='best_available':
        if m.get('overlapping_geographic_levels') is not True or m.get('counts_additive') is not False or m.get('complete_country_display') is not True:invalid()
        if {f['id'] for f in features if f['properties']['level']=='region'}!={f'R{i:02d}' for i in range(1,21)}:invalid()
        order={'region':0,'province':1,'municipality':2,'neighborhood':3};ranks=[order[f['properties']['level']] for f in features]
        if ranks!=sorted(ranks):invalid()
    for f in features:
        p=f['properties']
        if 'source_area_code' in p and (not isinstance(p['source_area_code'],str) or not re.fullmatch(r'(?:[0-9]{6}|IT[A-Z0-9]{0,3})',p['source_area_code'])):invalid()
    return data


def context_contract(data):
    if not isinstance(data,dict) or data.get('profile')!='tcip.population-coverage/1.0' or data.get('type')!='FeatureCollection':invalid()
    m=data.get('metadata',{})
    if not isinstance(m,dict) or m.get('private_research') is not True or m.get('context_only') is not True or m.get('missing_crime_is_zero') is not False or type(m.get('truncated')) is not bool:invalid()
    polygons(data.get('features'),300)
    for f in data['features']:
        p=f['properties']
        if set(p)-{'code','name','level','population','population_date','population_provisional','population_basis','count','rate_per_100000','status'} or p.get('count') is not None or p.get('rate_per_100000') is not None or p.get('status')!='crime_count_unavailable':invalid()
        pop=p.get('population')
        if pop is not None and (type(pop) is not int or pop<0 or pop>1000000000):invalid()
        if p.get('population_date') is not None:calendar(p['population_date'])
    return data


def lookup_contract(data):
    if not isinstance(data,dict) or data.get('counts_not_inferred') is not True or not isinstance(data.get('items'),list) or len(data['items'])>20:invalid()
    for item in data['items']:
        if not isinstance(item,dict) or not isinstance(item.get('code'),str) or not re.fullmatch(r'\d{6}',item['code']) or not isinstance(item.get('name'),str) or len(item['name'])>200:invalid()
        bounds=item.get('bounds')
        if not isinstance(bounds,list) or len(bounds)!=4 or not all(finite(v) for v in bounds) or not(5<=bounds[0]<bounds[2]<=20 and 35<=bounds[1]<bounds[3]<=49):invalid()
        pop=item.get('population')
        if pop is not None and (type(pop) is not int or pop<0 or pop>1000000000):invalid()
        if item.get('population_date') is not None:calendar(item['population_date'])
    return data


def cumulative_contract(data):
    """Verify each count/population component, their sum and nonoverlapping coverage."""
    if not isinstance(data,dict) or data.get('profile')!='tcip.cumulative-population-rate/1.0' or data.get('type')!='FeatureCollection':invalid()
    m=data.get('metadata',{})
    if not isinstance(m,dict):invalid()
    if m.get('metric')!='sum_nonoverlapping_period_rates_per_100000' or m.get('aggregation')!='cumulative' or m.get('window') not in ('all','3','5','10','2018-2024') or m.get('level') not in LEVELS or m.get('crime_code') not in CRIMES:invalid()
    if m.get('private_research') is not True or m.get('population_normalized') is not True or m.get('annualized') is not False or m.get('rates_are_probabilities') is not False or m.get('forecast_probability') is not None or m.get('variable_territorial_periods') is not (m['window']!='2018-2024') or m.get('counts_additive') is not False:invalid()
    victim_contract(m)
    key=hashlib.sha256(json.dumps(['cumulative',m['level'],m['crime_code'],m['window']],separators=(',',':')).encode()).hexdigest()[:20]
    if data.get('dataset_id')!=key:invalid()
    start,end=calendar(m.get('period_start')),calendar(m.get('period_end'))
    if start>end:invalid()
    features=data.get('features');polygons(features,2000)
    if not features:invalid()
    if type(m.get('reference_year')) is not int or not 1900<=m['reference_year']<=2200:invalid()
    component_count=0
    for f in features:
        p=f['properties'];components=p.get('components')
        if set(p)-{'code','name','level','crime_code','crime_label','count','population','rate_per_100000','period_start','period_end','years','components','omitted_periods','territory_matched','status','count_provisional','population_provisional'}:invalid()
        if p.get('crime_code')!=m['crime_code'] or p.get('status')!='cumulative_observed' or p.get('territory_matched') is not True or p.get('population') is not None:invalid()
        if m['level']!='best_available' and p.get('level')!=m['level']:invalid()
        if not isinstance(components,list) or not 1<=len(components)<=200:invalid()
        omitted=p.get('omitted_periods')
        if not isinstance(omitted,list) or len(omitted)>1000:invalid()
        for omission in omitted:
            if not isinstance(omission,dict) or set(omission)-{'year','period_start','period_end','reason'} or not isinstance(omission.get('reason'),str) or len(omission['reason'])>200:invalid()
            if 'year' in omission and (type(omission['year']) is not int or not 1900<=omission['year']<=2200):invalid()
            for field in ('period_start','period_end'):
                if field in omission:calendar(omission[field])
        for flag in ('count_provisional','population_provisional'):
            if type(p.get(flag)) is not bool:invalid()
        component_count+=len(components)
        if component_count>10000:invalid()
        total=rate=0;intervals=[];years=set()
        for c in components:
            if not isinstance(c,dict) or set(c)-{'code','level','crime_code','count','population','population_date','population_provisional','population_basis','period_start','period_end','count_source_id','count_source_url','population_source_id','population_source_url','count_provisional','geometry_edition','rate_per_100000'}:invalid()
            if (c.get('code'),c.get('level'),c.get('crime_code'))!=(p['code'],p['level'],p['crime_code']):invalid()
            a,b=calendar(c.get('period_start')),calendar(c.get('period_end'));ref=calendar(c.get('population_date'))
            if not start<=a<=b<=end or a.year!=b.year or b.year>m['reference_year']:invalid()
            if m['window']=='2018-2024':
                if not 2018<=a.year<=2024 or a!=date(a.year,1,1) or b!=date(a.year,12,31):invalid()
            elif m['window']!='all' and a.year<m['reference_year']-int(m['window'])+1:invalid()
            allowed={date(a.year,1,1),date(a.year,1,1)-timedelta(days=1)}
            if c.get('population_basis')=='next_1_january_stock_equivalent_to_31_december' and a==date(a.year,1,1) and b==date(a.year,12,31):allowed.add(b)
            if ref not in allowed or any(x<=b and a<=y for x,y in intervals):invalid()
            n,pop,value=c.get('count'),c.get('population'),c.get('rate_per_100000')
            if type(n) is not int or n<0 or type(pop) is not int or pop<=0 or not finite(value) or abs(value-n/pop*100000)>1e-7:invalid()
            for field in ('count_source_id','population_source_id'):
                if not UUID.fullmatch(c.get(field,'')):invalid()
            for field in ('count_source_url','population_source_url'):
                if not isinstance(c.get(field),str) or not c[field].startswith('https://') or len(c[field])>2048:invalid()
            for field in ('count_provisional','population_provisional'):
                if type(c.get(field)) is not bool:invalid()
            intervals.append((a,b));years.add(a.year);total+=n;rate+=value
        if m['window']=='2018-2024' and years!=set(range(2018,2025)):invalid()
        if type(p.get('count')) is not int or p['count']!=total or not finite(p.get('rate_per_100000')) or abs(p['rate_per_100000']-rate)>1e-7 or p.get('years')!=sorted(years):invalid()
        if calendar(p.get('period_start'))!=min(x for x,_ in intervals) or calendar(p.get('period_end'))!=max(y for _,y in intervals):invalid()
    if m['level']=='best_available':
        if {f['id'] for f in features if f['properties']['level']=='region'}!={f'R{i:02d}' for i in range(1,21)}:invalid()
        ranks=[LEVELS.index(f['properties']['level']) for f in features]
        if ranks!=sorted(ranks):invalid()
    return data
