"""Read-only inspection/compatibility CLI. No runtime, providers or models started."""
import argparse
import json
import sys
from pathlib import Path
from hazardia.io import loads, HazardError
from hazardia.exchange.contracts import MAX_BYTES, validate_product
from hazardia.exchange.compatibility import check_compatibility


def read(path):
    with Path(path).open('rb') as stream:raw=stream.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise HazardError('INVALID_EXCHANGE','Metadata exceeds 256 KiB')
    return loads(raw)


def unknowns(value, path=''):
    result=[]
    if isinstance(value,dict):
        if value.get('state')=='UNKNOWN':result.append(path)
        for key,item in value.items():result.extend(unknowns(item,path+'.'+key if path else key))
    elif isinstance(value,list):
        for index,item in enumerate(value):result.extend(unknowns(item,path+'['+str(index)+']'))
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--product',required=True);ap.add_argument('--requirement');ap.add_argument('--root');a=ap.parse_args()
    try:
        value=read(a.product)
        if a.requirement:
            result=check_compatibility(value,read(a.requirement),root=a.root)
            print(json.dumps(result,allow_nan=False));return {'COMPATIBLE':0,'UNKNOWN':3,'INCOMPATIBLE':2}[result['status']]
        validate_product(value,a.root)
        print(json.dumps(dict(status='PASS',domain_id=value['domain_id'],variables=[v['id'] for v in value['variables']],unknown_fields=unknowns(value),asset_hashes_verified=a.root is not None,scope='METADATA_ONLY_NOT_PHYSICAL_QUALIFICATION',operationally_approvable=False)));return 0
    except (HazardError,OSError,ValueError) as exc:
        print(json.dumps(dict(status='ERROR',code=getattr(exc,'code','EXCHANGE_IO'),message=str(exc))),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
