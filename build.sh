#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 was not found."
  exit 1
fi

echo "Creating virtual environment..."
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r requirements-build.txt

echo "Building PDF2PNG..."
.venv/bin/python -m PyInstaller --noconfirm --clean pdf2png.spec

echo
echo "Done."
echo "Output: $(pwd)/dist/PDF2PNG"
