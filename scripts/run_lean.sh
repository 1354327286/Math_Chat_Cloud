#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
lean_root="$repo_root/lean"
runtime_root="$repo_root/tmp/lean-runtime"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/run_lean.sh status
  bash scripts/run_lean.sh install
  bash scripts/run_lean.sh build
  bash scripts/run_lean.sh check <MathDailyLean/.../Module.lean>
  bash scripts/run_lean.sh lake <lake arguments...>
  bash scripts/run_lean.sh lean <lean arguments...>

The install subcommand is subject to the repository's explicit Lean setup gate.
All other subcommands require an existing workspace-local runtime.
EOF
}

activate_runtime() {
  if [[ ! -f "$lean_root/lean-toolchain" ]]; then
    echo "Lean toolchain pin is missing. Run the authorized install workflow first." >&2
    return 1
  fi

  local pinned version distribution
  pinned="$(tr -d '\r\n' < "$lean_root/lean-toolchain")"
  version="${pinned##*:v}"

  export ELAN_HOME="$runtime_root/elan"
  export TMPDIR="$runtime_root/tmp"
  mkdir -p "$TMPDIR"

  if [[ "$(uname -s):$(uname -m)" == "Linux:x86_64" ]]; then
    distribution="$runtime_root/lean-${version}-linux"
    if [[ ! -x "$distribution/bin/lean" || ! -x "$distribution/bin/lake" ]]; then
      echo "Workspace Lean runtime is missing for $pinned." >&2
      echo "After confirming the setup gate, run: bash scripts/run_lean.sh install" >&2
      return 1
    fi
    export PATH="$distribution/bin:$PATH"
    export LEAN_SYSROOT="$distribution"
    export LD_LIBRARY_PATH="$distribution/lib:$distribution/lib/lean${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    if [[ ! -e /proc/self/exe ]]; then
      local shim="$runtime_root/lean_proc_self_exe_shim.so"
      if [[ ! -f "$shim" ]]; then
        echo "Lean runtime shim is missing; rerun the authorized install workflow." >&2
        return 1
      fi
      export LEAN_PROC_SELF_EXE="$distribution/bin/lean"
      export LD_PRELOAD="$shim${LD_PRELOAD:+:$LD_PRELOAD}"
    fi
  else
    if [[ ! -x "$ELAN_HOME/bin/lean" || ! -x "$ELAN_HOME/bin/lake" ]]; then
      echo "Workspace elan runtime is missing." >&2
      echo "After confirming the setup gate, run: bash scripts/run_lean.sh install" >&2
      return 1
    fi
    export PATH="$ELAN_HOME/bin:$PATH"
  fi
}

command_name="${1:-}"
case "$command_name" in
  status)
    activate_runtime
    echo "Lean runtime is available."
    lean --version
    lake --version
    ;;
  install)
    if [[ "$#" -ne 1 ]]; then
      usage >&2
      exit 2
    fi
    exec bash "$repo_root/scripts/bootstrap_lean.sh" --install
    ;;
  build)
    if [[ "$#" -ne 1 ]]; then
      usage >&2
      exit 2
    fi
    activate_runtime
    cd "$lean_root"
    exec lake build
    ;;
  check)
    if [[ "$#" -ne 2 ]]; then
      usage >&2
      exit 2
    fi
    activate_runtime
    cd "$lean_root"
    exec lake env lean "$2"
    ;;
  lake)
    shift
    activate_runtime
    cd "$lean_root"
    exec lake "$@"
    ;;
  lean)
    shift
    activate_runtime
    cd "$lean_root"
    exec lean "$@"
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
