#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python -m pip install --no-index --no-build-isolation --no-deps -e .
python -m compileall -q \
  reference_index.py \
  search_arxiv_theorems.py \
  search_references.py \
  scripts
python scripts/check_project_registry.py
python scripts/check_public_scope.py --tracked
bash scripts/bootstrap_lean.sh --check

echo "Cloud workspace bootstrap complete."
