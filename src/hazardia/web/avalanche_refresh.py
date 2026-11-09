"""Optional supervisor only. Scientific code and native runtime stay external."""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import threading


def start(app):
    config = app.root / 'avalanche-auto-config.json'
    if not config.exists():
        return
    value = json.loads(config.read_text())
    if value != {'enabled': True}:
        return
    runtime = Path.home() / 'avalanche-runtime'
    # Locally approved fixed entry point, not executable paths from HTTP/descriptors.
    command = [str(runtime / 'env/bin/python'), str(runtime / 'app/src/hazardia_avalanche/worker.py'),
               '--root', str(runtime), '--delivery', str(app.root / 'avalanche')]

    def run():
        while not app.stop.is_set():
            try:
                with app.store.connect() as db:
                    busy = db.execute("SELECT COUNT(*) FROM jobs WHERE state IN ('RUNNING','QUEUED','PREPARING')").fetchone()[0]
                if not busy:
                    with (runtime / 'logs/supervisor.log').open('ab') as log:
                        process = subprocess.Popen(command, cwd=runtime, env=dict(os.environ, OMP_NUM_THREADS='1'),
                                                   stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
                        try:
                            process.wait(timeout=2400)
                        except subprocess.TimeoutExpired:
                            import signal
                            os.killpg(process.pid, signal.SIGTERM)
                            try:
                                process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                os.killpg(process.pid, signal.SIGKILL)
                                process.wait()
                # Scientific child lock prevents duplicates across dashboard restarts.
            except (OSError, ValueError, subprocess.SubprocessError):
                from hazardia.web.avalanche_layer import record_supervisor_failure
                record_supervisor_failure(app.root, 'SUPERVISOR_FAILED')
            app.stop.wait(300)
    threading.Thread(target=run, name='avalanche-refresh-supervisor', daemon=True).start()
