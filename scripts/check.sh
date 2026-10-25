#!/usr/bin/env bash
# Local checks (formerly run on GitHub Actions). Run from the repo root.
set -euo pipefail
cd "$(dirname "$0")/.."
# deps: python -m pip install numpy
python tools/test_range_recovery.py
python tools/test_dctl_pipeline.py
python tools/validate_presets.py presets/presets.json
bash -n tools/build_mac_installer.sh
bash -n tools/create_releases.sh
bash -n installers/mac/scripts/preinstall
bash -n installers/mac/scripts/postinstall
echo "All checks passed."
