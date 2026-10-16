"""Export a reviewed complete source snapshot from Git, never private Git history.
No push/network/VM mutation. The destination must not already exist.
"""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
EXCLUDED_PREFIXES=('.m0-runtime/','.runtime/','.cache/','.venv/','.publication/','experiments/','data/','node_modules/','qa-results/','reports/dashboard-evidence/')
EXCLUDED_SUFFIXES=('.png','.jpg','.jpeg','.gif','.webp','.tif','.tiff','.npz','.npy','.sqlite','.db','.img','.qcow2','.iso','.pem','.key','.tar.gz','.bundle')
PATTERNS=[('private-key',re.compile(rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----')),('github-token',re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})')),('aws-key',re.compile(rb'AKIA[0-9A-Z]{16}')),('credential-query',re.compile(rb'(?:api_key|access_token|apikey|password)=[A-Za-z0-9_-]{24,}',re.I))]
def excluded(name):
    p=Path(name)
    return name in ['PUBLICATION.json','research/PAPER-NOTES.md'] or name.startswith(EXCLUDED_PREFIXES) or name.endswith(EXCLUDED_SUFFIXES) or p.name in ['.env','id_rsa','id_ed25519','ssh-key','known_hosts'] or (p.name.startswith('.env.') and p.name!='.env.example') or '.utm' in p.suffixes

def git(source,*args):return subprocess.check_output(['git','-C',str(source),*args])
def prepare(source,ref,destination):
    source=Path(source).resolve();destination=Path(destination).resolve()
    if destination.exists():raise ValueError('Destination exists; no overwrite')
    commit=git(source,'rev-parse','--verify',ref+'^{commit}').decode().strip()
    entries=git(source,'ls-tree','-rz','--full-tree',commit).split(b'\0');approved=[];omitted=[]
    for row in entries:
        if not row:continue
        meta,path=row.split(b'\t',1);mode,kind,oid=meta.decode().split();name=path.decode()
        if excluded(name):omitted.append(name);continue
        if mode not in ['100644','100755'] or kind!='blob':raise ValueError('Unsupported source entry: '+name)
        data=git(source,'cat-file','blob',oid)
        for label,pattern in PATTERNS:
            if pattern.search(data):raise ValueError('Secret-like '+label+' in '+name+'; contents suppressed')
        if len(data)>10*1024**2:raise ValueError('Review large source file explicitly: '+name)
        approved.append((name,data,mode))
    destination.mkdir(parents=True)
    files={}
    for name,data,mode in approved:
        p=destination/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);p.chmod(0o755 if mode=='100755' else 0o644);files[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    result=dict(schema='hazardia-publication/1',source_git_sha=commit,files=files,excluded_paths=omitted,scope='Complete current application/provisioning source; private history, runtime state, large/generated media excluded. Fetch/generate inputs via documented bootstrap.',secret_scan='PASS known-pattern scan of every exported blob; not a universal secret-detection guarantee')
    (destination/'PUBLICATION.json').write_text(json.dumps(result,indent=2))
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True);ap.add_argument('--source',default=str(Path(__file__).resolve().parents[1]));ap.add_argument('--ref',default='HEAD');a=ap.parse_args();r=prepare(a.source,a.ref,a.output);print(json.dumps(dict(source=r['source_git_sha'],files=len(r['files']),omitted=len(r['excluded_paths']),status='PASS',meaning='Prepared only; nothing uploaded'),indent=2))
if __name__=='__main__':main()
