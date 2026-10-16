#!/usr/bin/env bash
# Run explicitly as root INSIDE a new Ubuntu 22.04 ARM64 VM. Never used by bootstrap.
set -euo pipefail
[ "$(uname -s)" = Linux ] && [ "$(uname -m)" = aarch64 ] || { echo 'Requires Linux ARM64' >&2; exit 2; }
. /etc/os-release
[ "$ID" = ubuntu ] && [ "$VERSION_ID" = 22.04 ] || { echo 'Requires Ubuntu 22.04' >&2; exit 2; }
[ "$(id -u)" = 0 ] || { echo 'Run sudo bash infra/guest/install-system.sh after reviewing packages.' >&2; exit 2; }
script_dir=$(cd -- "$(dirname -- "$0")" && pwd)
mapfile -t packages < "$script_dir/system-packages.txt"
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${packages[@]}"
