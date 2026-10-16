"""Offline M2 CLI; no services or operational actions."""
import argparse,json,sys
from hazardia.io import load,write_new,HazardError
from hazardia.domain.contracts import validate_record
from hazardia.domain.state import snapshot,GeoIndex
from hazardia.domain.events import associate

def main():
    ap=argparse.ArgumentParser(prog='python -m hazardia.domain');sub=ap.add_subparsers(dest='action',required=True)
    v=sub.add_parser('validate');v.add_argument('input')
    for action in ['snapshot','events']:
        p=sub.add_parser(action);p.add_argument('--profile',required=True);p.add_argument('--records',required=True);p.add_argument('--as-of',required=True);p.add_argument('--output',required=True)
    p=sub.add_parser('window');p.add_argument('--index',required=True);p.add_argument('--bbox',required=True,type=float,nargs=4);p.add_argument('--as-of',required=True);p.add_argument('--limit',type=int,default=100)
    args=ap.parse_args()
    try:
        if args.action=='validate':r=validate_record(load(args.input));result=dict(status='PASS',kind=r['kind'],id=r['id'])
        elif args.action=='snapshot':result=snapshot(load(args.profile),load(args.records),args.as_of,args.output)
        elif args.action=='events':result=associate(load(args.records),load(args.profile),args.as_of);write_new(args.output,result)
        else:result=GeoIndex(args.index).window(args.bbox,args.as_of,args.limit)
        print(json.dumps(result,allow_nan=False));return 0
    except (HazardError,OSError,ValueError) as e:
        print(json.dumps(dict(status='ERROR',code=e.code if isinstance(e,HazardError) else 'IO_ERROR',message=str(e))),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
