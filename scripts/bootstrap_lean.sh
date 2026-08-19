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
    export TMPDIR="$lean_runtime_root/tmp"
    mkdir -p "$lean_runtime_root" "$TMPDIR"

    if [[ ! -f "$lean_root/lean-toolchain" ]]; then
      toolchain_download="$lean_runtime_root/mathlib-lean-toolchain"
      curl --proto '=https' --tlsv1.2 -sSf \
        https://raw.githubusercontent.com/leanprover-community/mathlib4/master/lean-toolchain \
        -o "$toolchain_download"
      install -m 0644 "$toolchain_download" "$lean_root/lean-toolchain"
    fi

    if [[ "$(uname -s):$(uname -m)" == "Linux:x86_64" ]]; then
      pinned_toolchain="$(tr -d '\r\n' < "$lean_root/lean-toolchain")"
      if [[ "$pinned_toolchain" != "leanprover/lean4:v4.34.0-rc1" ]]; then
        echo "Unsupported direct Lean toolchain for this cloud sandbox: $pinned_toolchain" >&2
        exit 1
      fi
      lean_version="4.34.0-rc1"
      lean_archive="$lean_runtime_root/lean-${lean_version}-linux.tar.zst"
      lean_archive_sha256="41dc6a6ec143ece8ed4ba4c4c6978c91f21ad5cbe3c4e7728ad31b869961dc17"
      lean_distribution="$lean_runtime_root/lean-${lean_version}-linux"
      if [[ ! -x "$lean_distribution/bin/lean" || ! -x "$lean_distribution/bin/lake" ]]; then
        if [[ ! -f "$lean_archive" ]]; then
          curl --proto '=https' --tlsv1.2 -sSfL \
            "https://github.com/leanprover/lean4/releases/download/v${lean_version}/lean-${lean_version}-linux.tar.zst" \
            -o "$lean_archive"
        fi
        printf '%s  %s\n' "$lean_archive_sha256" "$lean_archive" | sha256sum --check
        tar --no-same-owner --zstd -xf "$lean_archive" -C "$lean_runtime_root"
      fi
      export PATH="$lean_distribution/bin:$PATH"
      export LEAN_SYSROOT="$lean_distribution"
      export LD_LIBRARY_PATH="$lean_distribution/lib:$lean_distribution/lib/lean${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
      if [[ ! -e /proc/self/exe ]]; then
        lean_proc_shim_source="$repo_root/scripts/lean_proc_self_exe_shim.c"
        lean_proc_shim="$lean_runtime_root/lean_proc_self_exe_shim.so"
        cc -shared -fPIC -O2 -Wall -Wextra -Werror \
          "$lean_proc_shim_source" -ldl -o "$lean_proc_shim"
        export LEAN_PROC_SELF_EXE="$lean_distribution/bin/lean"
        export LD_PRELOAD="$lean_proc_shim${LD_PRELOAD:+:$LD_PRELOAD}"
      fi
    else
      export PATH="$ELAN_HOME/bin:$PATH"
      if [[ ! -x "$ELAN_HOME/bin/elan" ]]; then
        elan_installer="$lean_runtime_root/elan-init.sh"
        curl --proto '=https' --tlsv1.2 -sSf \
          https://elan.lean-lang.org/elan-init.sh \
          -o "$elan_installer"
        sh "$elan_installer" -y --no-modify-path --default-toolchain none
      fi
    fi

    cd "$lean_root"
    root_build="$lean_root/.lake/build/lib/lean/MathDailyLean.olean"
    mathlib_build="$lean_root/.lake/packages/mathlib/.lake/build/lib/lean/Mathlib.olean"
    if [[ -f "$lean_root/lake-manifest.json" && -f "$root_build" && -f "$mathlib_build" ]]; then
      echo "Existing Lean and Mathlib build detected; reusing the local cache."
    else
      lake update
      lake exe cache get
    fi
    lake build

    echo "Lean setup and initial build complete."
    echo "Review and commit lean/lean-toolchain and lean/lake-manifest.json for reproducibility."
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
