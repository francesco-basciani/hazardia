"""Render a fresh SSH-key-only NoCloud seed directory; no passwords or private keys."""
import argparse,json,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--public-key',required=True);p.add_argument('--output',required=True);a=p.parse_args();key=Path(a.public_key).read_text().strip()
if '\n' in key or not key.startswith(('ssh-ed25519 ','ssh-rsa ','ecdsa-sha2-')) or 'PRIVATE KEY' in key:raise SystemExit('One OpenSSH PUBLIC key required')
out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
(out/'meta-data').write_text('instance-id: hazardia-'+str(uuid.uuid4())+'\nlocal-hostname: hazardia\n')
(out/'user-data').write_text('''#cloud-config
users:
  - name: hazardia
    groups: [adm, sudo]
    shell: /bin/bash
    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
    lock_passwd: true
    ssh_authorized_keys:
      - '''+json.dumps(key)+'''
ssh_pwauth: false
disable_root: true
package_update: false
package_upgrade: false
runcmd:
  - [systemctl, enable, --now, ssh]
''')
print('Seed rendered with public key only; privileged packages are installed later by explicit guest command.')
