#!/bin/sh

set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)

for candidate in python3.12 python3.11 python3.10; do
  if command -v "$candidate" >/dev/null 2>&1; then
    exec "$candidate" "$@"
  fi
done

if command -v python3 >/dev/null 2>&1; then
  version=$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
  case "$version" in
    3.1[0-9]|[4-9].*)
      exec python3 "$@"
      ;;
  esac
fi

echo "ProductOS requires Python 3.10+ for this command. Install python3.10+ or update PATH." >&2
exit 1
