#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
lean_root="$repo_root/lean"
mode="${1:---check}"

usage() {
  echo "Usage: bash scripts/bootstrap_lean.sh [--check|--install]"
}

check_scaffold() {
  local required=(
    "$lean_root/AGENTS.md"
    "$lean_root/README.md"
    "$lean_root/FORMALIZATION_INDEX.md"
    "$lean_root/lakefile.toml"
    "$lean_root/MathDailyLean.lean"
    "$lean_root/MathDailyLean/Common/Basic.lean"
  )
  local path
  local missing=0

  for path in "${required[@]}"; do
    if [[ ! -f "$path" ]]; then
      echo "Missing Lean scaffold file: ${path#"$repo_root/"}" >&2
      missing=1
    fi
  done

  if [[ -d "$lean_root/.git" ]]; then
    echo "Nested Git repository is not allowed: lean/.git" >&2
    missing=1
  fi

  if [[ "$missing" -ne 0 ]]; then
    return 1
  fi

  echo "Lean scaffold is complete."
  if [[ -f "$lean_root/lean-toolchain" ]]; then
    echo "Pinned toolchain: $(tr -d '\r\n' < "$lean_root/lean-toolchain")"
  else
    echo "Lean toolchain is not installed or pinned yet."
  fi
  if [[ -f "$lean_root/lake-manifest.json" ]]; then
    echo "Lake dependency manifest is present."
  else
    echo "Lake dependency manifest has not been generated yet."
  fi
}

case "$mode" in
  --check)
    check_scaffold
    ;;
  --install)
    check_scaffold

    lean_runtime_root="$repo_root/tmp/lean-runtime"
    export ELAN_HOME="$lean_runtime_root/elan"
    export PATH="$ELAN_HOME/bin:$PATH"
    mkdir -p "$lean_runtime_root"

    if [[ ! -x "$ELAN_HOME/bin/elan" ]]; then
      elan_installer="$lean_runtime_root/elan-init.sh"
      curl --proto '=https' --tlsv1.2 -sSf \
        https://elan.lean-lang.org/elan-init.sh \
        -o "$elan_installer"
      sh "$elan_installer" -y --no-modify-path --default-toolchain none
    fi

    if [[ ! -f "$lean_root/lean-toolchain" ]]; then
      toolchain_download="$lean_runtime_root/mathlib-lean-toolchain"
      curl --proto '=https' --tlsv1.2 -sSf \
        https://raw.githubusercontent.com/leanprover-community/mathlib4/master/lean-toolchain \
        -o "$toolchain_download"
      install -m 0644 "$toolchain_download" "$lean_root/lean-toolchain"
    fi

    cd "$lean_root"
    lake update
    lake exe cache get
    lake build

    echo "Lean setup and initial build complete."
    echo "Review and commit lean/lean-toolchain and lean/lake-manifest.json for reproducibility."
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
