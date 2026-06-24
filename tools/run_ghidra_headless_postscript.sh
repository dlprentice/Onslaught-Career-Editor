#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   tools/run_ghidra_headless_postscript.sh <ScriptName.java> [script-arg1 ...]
#
# Example:
#   tools/run_ghidra_headless_postscript.sh ExportWeakFunctionList.java C:\\temp\\weak.tsv weak
#
# Requires all Ghidra GUI windows closed for the target project.

SCRIPT_NAME="${1:-}"
shift || true

if [[ -z "$SCRIPT_NAME" ]]; then
  echo "Usage: $0 <ScriptName.java> [script-args...]" >&2
  exit 2
fi

GHIDRA_HOME_DEFAULT="/mnt/d/ghidra_12.0.3_PUBLIC_20260210/ghidra_12.0.3_PUBLIC"
PROJECT_DIR_DEFAULT="/mnt/c/Users/david/Ghidra/Projects"
PROJECT_NAME_DEFAULT="BEA"
PROGRAM_DEFAULT="BEA.exe"
SCRIPT_DIR_DEFAULT="/mnt/c/Users/david/source/Onslaught-Career-Editor-private/tools"

GHIDRA_HOME="${GHIDRA_HOME:-$GHIDRA_HOME_DEFAULT}"
PROJECT_DIR="${GHIDRA_PROJECT_DIR:-$PROJECT_DIR_DEFAULT}"
PROJECT_NAME="${GHIDRA_PROJECT_NAME:-$PROJECT_NAME_DEFAULT}"
PROGRAM_NAME="${GHIDRA_PROGRAM_NAME:-$PROGRAM_DEFAULT}"
SCRIPT_DIR="${GHIDRA_SCRIPT_DIR:-$SCRIPT_DIR_DEFAULT}"

echo "[headless] script=$SCRIPT_NAME"
echo "[headless] ghidra_home=$GHIDRA_HOME"
echo "[headless] project=$PROJECT_DIR/$PROJECT_NAME"
echo "[headless] program=$PROGRAM_NAME"
echo "[headless] script_dir=$SCRIPT_DIR"
echo "[headless] args=$*"
echo "[headless] NOTE: all Ghidra GUI windows must be closed"

GHIDRA_HOME_WIN="$(wslpath -w "$GHIDRA_HOME")"
PROJECT_DIR_WIN="$(wslpath -w "$PROJECT_DIR")"
SCRIPT_DIR_WIN="$(wslpath -w "$SCRIPT_DIR")"

# Convert args to Windows path if they look like existing Unix paths; otherwise pass as-is.
WIN_ARGS=()
for a in "$@"; do
  if [[ -e "$a" ]]; then
    WIN_ARGS+=("$(wslpath -w "$a")")
  elif [[ "$a" == /* ]]; then
    WIN_ARGS+=("$(wslpath -w "$a")")
  else
    WIN_ARGS+=("$a")
  fi
done

python3 - "$GHIDRA_HOME_WIN" "$PROJECT_DIR_WIN" "$PROJECT_NAME" "$PROGRAM_NAME" "$SCRIPT_DIR_WIN" "$SCRIPT_NAME" "${WIN_ARGS[@]}" <<'PY'
import subprocess
import sys

ghidra_home = sys.argv[1]
project_dir = sys.argv[2]
project_name = sys.argv[3]
program_name = sys.argv[4]
script_dir = sys.argv[5]
script_name = sys.argv[6]
script_args = sys.argv[7:]

bat = ghidra_home + "\\support\\analyzeHeadless.bat"
cmd = [
    "cmd.exe", "/c", bat,
    project_dir,
    project_name,
    "-process", program_name,
    "-scriptPath", script_dir,
    "-postScript", script_name,
    *script_args,
    "-noanalysis",
]

res = subprocess.run(cmd)
sys.exit(res.returncode)
PY
