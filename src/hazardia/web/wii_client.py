"""Bounded local API consumer, usable independently from the server."""
class APIClient:
    """Optional loopback consumer; never opens SQLite or starts a WII worker."""
    def __init__(self, port=8081):
        if type(port) is not int or not 1024<=port<=65535:
            raise ValueError('WII client port must be1024..65535')
        self.base='http://127.0.0.1:'+str(port)

    def request(self, method, path, query='', body=None):
        import json
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError, URLError
        from hazardia.io import HazardError
        if not path.startswith('/api/wii/') or any(c in path+query for c in ('\r','\n','#')):
            raise HazardError('WII_INVALID','WII API path required')
        data=json.dumps(body,allow_nan=False).encode() if body is not None else None
        request=Request(self.base+path+('?' + query if query else ''),data=data,method=method,
            headers={'Content-Type':'application/json','X-WII-Research':'1','Origin':self.base})
        try:
            response=urlopen(request,timeout=30)
        except HTTPError as exc:response=exc
        except (URLError,TimeoutError) as exc:
            raise HazardError('WII_DEPENDENCY','Standalone WII service unavailable') from exc
        with response:
            raw=response.read(24*1024**2+1)
            if len(raw)>24*1024**2:raise HazardError('WII_PAYLOAD_LIMIT','WII response exceeds24MiB')
            return response.status,raw

    def route(self, method, path, query, body=None):
        import json
        status,raw=self.request(method,path,query,body)
        return status,json.loads(raw)

    def download_inventory(self, ident):
        from hazardia.io import HazardError
        status,raw=self.request('GET','/api/wii/inventory/exports/'+ident+'.sqlite')
        if status!=200:raise HazardError('WII_NOT_FOUND','Standalone export unavailable')
        return raw
