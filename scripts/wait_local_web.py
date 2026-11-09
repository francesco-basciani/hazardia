"""Bounded readiness check for the existing loopback services (Linux VM)."""
import argparse
import time
import urllib.error
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, choices=[8080, 8081], required=True)
args = parser.parse_args()
deadline = time.monotonic() + 25
while time.monotonic() < deadline:
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{args.port}/api/health', timeout=2) as response:
            if response.status == 200:
                raise SystemExit(0)
    except (OSError, urllib.error.URLError):
        pass
    time.sleep(.25)
raise SystemExit('Local web service did not become ready within 25 seconds')
