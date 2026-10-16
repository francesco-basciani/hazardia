#!/usr/bin/env bash
# Host provisioning assets only. Does not launch/create a VM or install anything.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "$0")" && pwd)
output=''; public_key=''; image_file=''; download=0
while [ "$#" -gt 0 ]; do
 case "$1" in
 --output) output=$2; shift 2;;
 --public-key) public_key=$2; shift 2;;
 --image-file) image_file=$2; shift 2;;
 --download) download=1; shift;;
 *) echo "Unknown argument: $1" >&2; exit 2;;
 esac
done
[ -n "$output" ] && [ -n "$public_key" ] || { echo 'Use --output DIR --public-key FILE.pub [--image-file CACHED.img | --download]' >&2; exit 2; }
[ "$(uname -s)" = Darwin ] || { echo 'UTM asset preparation is for macOS' >&2; exit 2; }
[ ! -e "$output" ] || { echo 'Output exists; refusing overwrite' >&2; exit 2; }
mkdir -p "$output"
python3 "$script_dir/cloud_init.py" --public-key "$public_key" --output "$output/seed"
if [ -n "$image_file" ]; then
 cp "$image_file" "$output/ubuntu-arm64.img"
elif [ "$download" = 1 ]; then
 curl -fL --max-filesize 900000000 --max-time 1200 'https://cloud-images.ubuntu.com/jammy/20261004/jammy-server-cloudimg-arm64.img' -o "$output/ubuntu-arm64.img"
else
 echo 'Supply cached image or explicit --download (~669 MiB). Seed preserved.' >&2; exit 2
fi
printf '%s  %s\n' '86e13258765945ad792dac75fac7f02f4db9fa73a4a535ffa472266e7041fa19' "$output/ubuntu-arm64.img" | shasum -a 256 -c -
hdiutil makehybrid -iso -joliet -default-volume-name cidata -o "$output/seed.iso" "$output/seed"
printf 'Prepared assets in %s. Import image into UTM using infra/utm/vm.json and docs/INSTALLAZIONE.md. No VM was created.\n' "$output"
