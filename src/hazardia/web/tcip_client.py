"""Optional read-only TCIP consumer; no TCIP imports, database, model or worker."""
import json
import math
import os
import re
import threading
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from hazardia.io import HazardError

UUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def invalid():
    raise HazardError('TCIP_CONTRACT', 'TCIP historical-layer contract rejected')


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def catalog_contract(data):
    if not isinstance(data, dict) or data.get('schema') != 'tcip.map-catalog/1.0' or data.get('forecast_probability_available') is not False:
        invalid()
    items = data.get('items')
    if not isinstance(items, list) or len(items) > 200:
        invalid()
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not UUID.fullmatch(item.get('release_id', '')) or item['release_id'] in seen or item.get('profile') not in ('tcip.regional-historical-share/1.0','tcip.spatial-observed-share/2.0'):
            invalid()
        seen.add(item['release_id'])
        years = item.get('years')
        if not isinstance(years, list) or not years or len(years)>100 or any(type(y) is not int for y in years) or years != sorted(set(years)):
            invalid()
    return data


def layer_contract(data):
    if not isinstance(data, dict) or data.get('type') != 'FeatureCollection' or not UUID.fullmatch(data.get('release_id', '')):
        invalid()
    metadata = data.get('metadata', {})
    if not isinstance(metadata,dict) or not isinstance(data.get('geometry_context'),dict):invalid()
    years=metadata.get('years')
    if not isinstance(years,list) or not years or len(years)>100 or any(type(y) is not int for y in years) or years!=sorted(set(years)):invalid()
    if metadata.get('probability_kind') != 'empirical_location_share_given_recorded_dataset_episode' or metadata.get('forecast_probability') is not None:
        invalid()
    detailed=data.get('profile')=='tcip.spatial-observed-share/2.0'
    if detailed and (metadata.get('level') not in ('municipality','neighborhood') or not isinstance(metadata.get('coverage'),str) or len(metadata['coverage'])>2000):invalid()
    editions={'Firenze-quartieri-2012-context','ISTAT-2024-01-01-generalized-display50m'} if detailed else {'ISTAT-2020-01-01-generalized-display150m'}
    if data.get('geometry_context', {}).get('edition') not in editions:
        invalid()
    features = data.get('features')
    if not isinstance(features,list) or not (1<=len(features)<=2000 if detailed else len(features)==20):
        invalid()
    ids=set(); counts=[];shares=[];pairs=0
    for f in features:
        if not isinstance(f,dict):invalid()
        identity=f.get('id')
        valid_id=isinstance(identity,str) and bool(UUID.fullmatch(identity)) if detailed else str(identity) in {str(i) for i in range(1,21)}
        if f.get('type')!='Feature' or not valid_id or identity in ids:
            invalid()
        ids.add(f['id']);p=f.get('properties',{});geometry=f.get('geometry',{})
        if not isinstance(p,dict) or not isinstance(geometry,dict):invalid()
        count,share=p.get('count'),p.get('share')
        if count is not None and (type(count) is not int or count<0):invalid()
        if share is not None and (not finite(share) or not 0<=share<=1):invalid()
        if not isinstance(p.get('source_region'),str) or len(p['source_region'])>100:invalid()
        counts.append(count);shares.append(share)
        if geometry.get('type') not in ('Polygon','MultiPolygon'):invalid()
        polygons=[geometry.get('coordinates')] if geometry['type']=='Polygon' else geometry.get('coordinates')
        if not isinstance(polygons,list) or not polygons:invalid()
        for polygon in polygons:
            if not isinstance(polygon,list) or not polygon:invalid()
            for ring in polygon:
                if not isinstance(ring,list) or len(ring)<4 or ring[0]!=ring[-1]:invalid()
                for pair in ring:
                    pairs+=1
                    if pairs>100000 or not isinstance(pair,list) or len(pair)!=2 or not all(finite(v) for v in pair) or not (-180<=pair[0]<=180 and -90<=pair[1]<=90):invalid()
    total=metadata.get('denominator')
    if total is not None and (type(total) is not int or total<0):invalid()
    if total is None or total==0:
        if any(v is not None for v in shares):invalid()
    elif any(v is None for v in counts+shares) or sum(counts)!=total or abs(sum(shares)-1)>1e-9 or any(abs(share-count/total)>1e-12 for count,share in zip(counts,shares)):
        invalid()
    return data


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise HazardError('TCIP_DEPENDENCY','TCIP redirect refused')


class APIClient:
    def __init__(self,root,port=18010):
        if type(port) is not int or not 1024<=port<=65535:
            raise HazardError('TCIP_CONFIG','TCIP requires an explicit loopback port1024..65535')
        self.base='http://127.0.0.1:'+str(port)
        self.token_file=Path(root)/'tcip-reader.token'
        self.capacity=threading.BoundedSemaphore(2)

    def credential(self,document_map=False,population_rates=False,local_rates=False):
        path=self.token_file.with_name("tcip-local-rate-reader.token") if local_rates else self.token_file.with_name("tcip-population-reader.token") if population_rates else self.token_file.with_name("tcip-document-reader.token") if document_map else self.token_file
        try:
            stat=path.stat()
            if path.is_symlink() or stat.st_size>200 or stat.st_mode&0o077 or stat.st_uid!=os.getuid():
                raise ValueError('private file required')
            token=path.read_text().strip()
            if not re.fullmatch(r'tcip_[A-Za-z0-9_-]{32,100}',token):raise ValueError('invalid token')
            return token
        except (OSError,ValueError):
            raise HazardError('TCIP_CONFIG','TCIP reader credential missing or not private') from None

    def request(self,path):
        from .tcip_local_rates import local_path
        local=local_path(path)
        population_path=bool(re.fullmatch(r'/api/v1/geo/population-rates\?crime=(?:theft|robbery)&period=(?:2023|2024-H1)',path))
        if not local and not population_path and path not in ('/api/v1/geo/distributions','/api/v1/geo/document-map') and not re.fullmatch(r'/api/v1/geo/distribution/[0-9a-f-]{36}(?:\?years=(?:[1-9][0-9]?|100))?',path):
            raise HazardError('INVALID_INPUT','Unsupported TCIP consumer path')
        if not self.capacity.acquire(blocking=False):raise HazardError('TCIP_BUSY','TCIP read capacity busy')
        try:
            request=Request(self.base+path,headers={'Authorization':'Bearer '+self.credential(document_map=path=='/api/v1/geo/document-map',population_rates=population_path,local_rates=local),'Accept':'application/json'})
            try:
                with build_opener(ProxyHandler({}),NoRedirect()).open(request,timeout=5) as response:
                    raw=response.read(2_000_001)
            except (HTTPError,URLError,TimeoutError,OSError):
                raise HazardError('TCIP_DEPENDENCY','TCIP unavailable or reader authorization rejected') from None
            if len(raw)>2_000_000:raise HazardError('TCIP_PAYLOAD','TCIP response exceeds bounded layer profile')
            try:return json.loads(raw,parse_constant=lambda _:invalid())
            except (ValueError,UnicodeError):invalid()
        finally:self.capacity.release()

    def local_catalog(self):
        from .tcip_local_rates import catalogue_contract
        return catalogue_contract(self.request('/api/v1/geo/territorial-rates'))

    def local_layer(self,identity):
        from .tcip_local_rates import KEY,layer_contract
        if not isinstance(identity,str) or not KEY.fullmatch(identity):raise HazardError('INVALID_INPUT','Local rate identity required')
        data=layer_contract(self.request('/api/v1/geo/territorial-rates?dataset='+identity))
        if data['dataset_id']!=identity:invalid()
        return data

    def local_context(self,bbox,level='municipality',year='2025'):
        from .tcip_local_rates import context_contract,local_path
        from urllib.parse import urlencode
        path='/api/v1/geo/territorial-context?'+urlencode({'bbox':bbox,'level':level,'year':year})
        if not local_path(path):raise HazardError('INVALID_INPUT','Bounded local population viewport required')
        return context_contract(self.request(path))

    def local_lookup(self,q,year='2025'):
        from .tcip_local_rates import lookup_contract,local_path
        from urllib.parse import urlencode
        path='/api/v1/geo/territorial-lookup?'+urlencode({'q':q,'year':year})
        if not local_path(path):raise HazardError('INVALID_INPUT','Bounded municipality lookup required')
        return lookup_contract(self.request(path))

    def population_rates(self,crime='theft',period='2023'):
        if crime not in ('theft','robbery') or period not in ('2023','2024-H1'):
            raise HazardError('INVALID_INPUT','Unsupported TCIP rate category/period')
        return population_rate_contract(self.request('/api/v1/geo/population-rates?crime='+crime+'&period='+period))

    def document_map(self):
        return document_map_contract(self.request("/api/v1/geo/document-map"))

    def catalog(self):
        return catalog_contract(self.request('/api/v1/geo/distributions'))

    def layer(self,identity,years=None):
        if not isinstance(identity,str) or not UUID.fullmatch(identity) or (years is not None and (type(years) is not int or not 1<=years<=100)):
            raise HazardError('INVALID_INPUT','TCIP requires a release UUID and optional whole-year window1..100')
        data=layer_contract(self.request('/api/v1/geo/distribution/'+identity+('' if years is None else '?years='+str(years))))
        if data['release_id']!=identity:invalid()
        return data


def document_map_contract(data):
    if not isinstance(data,dict) or data.get('type')!='FeatureCollection' or data.get('profile')!='tcip.document-event-geography/1.0':invalid()
    m=data.get('metadata',{})
    if not isinstance(m,dict):invalid()
    if m.get('private_research') is not True or m.get('forecast_probability') is not None or m.get('counts_are_unique_crimes') is not False:invalid()
    features=data.get('features');pairs=0;seen=set()
    if not isinstance(features,list) or len(features)>2000:invalid()
    for f in features:
        if not isinstance(f,dict):invalid()
        p=f.get('properties',{});g=f.get('geometry',{});code=f.get('id')
        if not isinstance(p,dict) or not isinstance(g,dict):invalid()
        if not isinstance(code,str) or not re.fullmatch(r'[0-9]{6}(?::(?:Q[1-5]|A[1-3]-[0-9]{1,4}))?',code) or code in seen:invalid()
        seen.add(code)
        if p.get('level') not in ('municipality','neighborhood') or p.get('location_basis')!='document_assertion_not_source_office' or p.get('verification_status')!='unreviewed_document_assertion':invalid()
        if set(p)-{'code','area_id','name','level','document_count','counts','publication_windows','location_basis','verification_status'}:invalid()
        if not isinstance(p.get('name'),str) or len(p['name'])>120:invalid()
        count=p.get('document_count');counts=p.get('counts')
        if type(count) is not int or count<1 or not isinstance(counts,dict) or len(counts)>16 or any(type(v)is not int or v<1 or v>count for v in counts.values()):invalid()
        windows=p.get('publication_windows',{})
        if not isinstance(windows,dict) or set(windows)-{'30','90','365','1095','3650'}:invalid()
        for cell in windows.values():
            if not isinstance(cell,dict) or set(cell)!={'document_count','counts'}:invalid()
            n=cell['document_count'];cc=cell['counts']
            if type(n)is not int or not 0<=n<=count or not isinstance(cc,dict):invalid()
            if any(k not in counts or type(v)is not int or not 1<=v<=min(n,counts[k]) for k,v in cc.items()):invalid()
        if g.get('type') not in ('Polygon','MultiPolygon'):invalid()
        polygons=[g.get('coordinates')] if g['type']=='Polygon' else g.get('coordinates')
        if not isinstance(polygons,list):invalid()
        for polygon in polygons:
            if not isinstance(polygon,list) or not polygon:invalid()
            for ring in polygon:
                if not isinstance(ring,list) or len(ring)<4 or ring[0]!=ring[-1]:invalid()
                for pair in ring:
                    pairs+=1
                    if pairs>100000 or not isinstance(pair,list) or len(pair)!=2 or not all(finite(v)for v in pair) or not (-180<=pair[0]<=180 and -90<=pair[1]<=90):invalid()
    return data


def population_rate_contract(data):
    if not isinstance(data,dict) or data.get('type')!='FeatureCollection' or data.get('profile')!='tcip.population-rates/1.0':invalid()
    m=data.get('metadata',{})
    if not isinstance(m,dict) or m.get('private_research') is not True or m.get('population_normalized') is not True or m.get('annualized') is not False or m.get('forecast_probability') is not None:invalid()
    if m.get('metric')!='reported_offences_per_100000_residents' or m.get('crime_code') not in ('theft','robbery') or m.get('period') not in ('2023','2024-H1'):invalid()
    periods={'2023':('2023-01-01','2023-12-31',False),'2024-H1':('2024-01-01','2024-06-30',True)}
    if (m.get('period_start'),m.get('period_end'),m.get('partial_period'))!=periods[m['period']]:invalid()
    national=m.get('national_rate_per_100000')
    if not finite(national) or national<=0 or national>10000000:invalid()
    features=data.get('features');seen=set();pairs=0
    if not isinstance(features,list) or len(features)!=20:invalid()
    for f in features:
        if not isinstance(f,dict) or f.get('type')!='Feature':invalid()
        code=str(f.get('id'));p=f.get('properties',{});g=f.get('geometry',{})
        if code not in {str(i) for i in range(1,21)} or code in seen or not isinstance(p,dict) or not isinstance(g,dict):invalid()
        seen.add(code)
        if set(p)-{'code','name','level','area_id','rate_per_100000','relative_to_national','population','count','status'}:invalid()
        if p.get('code')!=code or p.get('level')!='region' or not UUID.fullmatch(p.get('area_id','')) or not isinstance(p.get('name'),str) or len(p['name'])>100:invalid()
        if p.get('population') is not None or p.get('count') is not None:invalid()
        rate,ratio=p.get('rate_per_100000'),p.get('relative_to_national')
        if rate is None:
            if ratio is not None or p.get('status')!='unavailable':invalid()
        elif not finite(rate) or rate<0 or rate>10000000 or not finite(ratio) or abs(ratio-rate/national)>1e-9 or p.get('status')!='observed':invalid()
        if g.get('type') not in ('Polygon','MultiPolygon') or not isinstance(g.get('coordinates'),list):invalid()
        polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
        for polygon in polygons:
            if not isinstance(polygon,list) or not polygon:invalid()
            for ring in polygon:
                if not isinstance(ring,list) or len(ring)<4 or ring[0]!=ring[-1]:invalid()
                for pair in ring:
                    pairs+=1
                    if pairs>100000 or not isinstance(pair,list) or len(pair)!=2 or not all(finite(v) for v in pair) or not(-180<=pair[0]<=180 and -90<=pair[1]<=90):invalid()
    return data
