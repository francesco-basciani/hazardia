"""Local CLI for ingestion snapshots and bounded simulation jobs; no dispatch."""
import argparse,json,sys
from hazardia.io import load,HazardError,write_new
from hazardia.jobs import JobStore
from hazardia.contracts import migrate_observation_010

def main(argv=None):
    ap=argparse.ArgumentParser(prog='hazardia');ap.add_argument('--runtime-root',required=True);ap.add_argument('--config',required=True)
    sub=ap.add_subparsers(dest='action',required=True)
    p=sub.add_parser('submit');p.add_argument('--request',required=True);p.add_argument('--snapshot-root',required=True)
    for action in ['status','events','cancel','retry']:
        p=sub.add_parser(action);p.add_argument('job_id')
    sub.add_parser('work-once');sub.add_parser('recover')
    p=sub.add_parser('migrate-observation');p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    args=ap.parse_args(argv)
    try:
        if args.action=='migrate-observation':write_new(args.output,migrate_observation_010(load(args.input)));result=dict(status='PASS',scope='METADATA_MIGRATION_ONLY')
        else:
            store=JobStore(args.runtime_root,args.config)
            if args.action=='submit':result=dict(job_id=store.submit(load(args.request),args.snapshot_root),state='QUEUED')
            elif args.action=='status':result=store.get(args.job_id)
            elif args.action=='events':result=store.events(args.job_id)
            elif args.action=='cancel':result=dict(cancel_accepted=store.cancel(args.job_id),job=store.get(args.job_id))
            elif args.action=='retry':result=dict(job_id=store.retry(args.job_id),state='QUEUED',parent_job=args.job_id)
            elif args.action=='recover':result=dict(recovered=store.recover())
            else:result=store.work_once() or dict(state='IDLE')
        print(json.dumps(result,allow_nan=False));return 0
    except (HazardError,OSError,ValueError) as exc:
        print(json.dumps(dict(status='ERROR',code=exc.code if isinstance(exc,HazardError) else 'IO_ERROR',message=str(exc))),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
