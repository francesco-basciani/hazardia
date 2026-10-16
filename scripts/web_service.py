"""VM-local dashboard start/stop; no host scientific runtime or public binding."""
import argparse,subprocess,sys,os,signal,time
from pathlib import Path
from hazardia.io import load,write_new
from hazardia.jobs import JobStore

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['start','stop']);ap.add_argument('--runtime',required=True);args=ap.parse_args();root=Path(args.runtime);app=Path(__file__).resolve().parents[1];pidfile=root/'web-server.pid'
    if args.action=='stop':
        if not pidfile.exists():raise SystemExit('No owned server PID; inspect existing process before stopping')
        pid=int(pidfile.read_text());cmd=Path('/proc')/str(pid)/'cmdline'
        if cmd.exists() and b'hazardia.web' in cmd.read_bytes():os.kill(pid,signal.SIGTERM)
        pidfile.unlink();return
    # Refuse a second listener before recovering any previous job.
    import socket
    with socket.socket() as probe:
        if probe.connect_ex(('127.0.0.1',8080))==0:raise SystemExit('Dashboard already listening on127.0.0.1:8080')
    store=JobStore(root/'jobs',root/'runtime-v2.json');recovered=store.recover()
    with (root/'web-server.log').open('ab') as log:
        p=subprocess.Popen([str(root/'core-env/bin/python'),'-m','hazardia.web','--runtime',str(root),'--port','8080'],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,cwd=app,start_new_session=True)
    pidfile.write_text(str(p.pid));print('Started VM-only dashboard PID',p.pid,'interrupted jobs explicitly classified',recovered)
if __name__=='__main__':main()
