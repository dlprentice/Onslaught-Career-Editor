#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   tools/run_ghidra_batch_rename_headless.sh <rename_map_path> [dry|apply]
#
# Notes:
# - Close ALL Ghidra windows (including project window) before running headless
#   against the same project/program, otherwise project lock will fail.
# - Defaults target this workstation's active Ghidra install/project from AGENTS.md.

MAP_FILE="${1:-}"
MODE="${2:-apply}"

if [[ -z "$MAP_FILE" ]]; then
  echo "Usage: $0 <rename_map_path> [dry|apply]" >&2
  exit 2
fi

if [[ ! -f "$MAP_FILE" ]]; then
  echo "Map file not found: $MAP_FILE" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if command -v py.exe >/dev/null 2>&1; then
  py.exe -3 "$SCRIPT_DIR/ghidra_rename_map_preflight.py" "$MAP_FILE"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$SCRIPT_DIR/ghidra_rename_map_preflight.py" "$MAP_FILE"
else
  echo "Python not found for rename-map preflight" >&2
  exit 2
fi

GHIDRA_HOME_DEFAULT="/mnt/d/ghidra_12.0.3_PUBLIC_20260210/ghidra_12.0.3_PUBLIC"
PROJECT_DIR_DEFAULT="/mnt/c/Users/david/Ghidra/Projects"
PROJECT_NAME_DEFAULT="BEA"
PROGRAM_DEFAULT="BEA.exe"

GHIDRA_HOME="${GHIDRA_HOME:-$GHIDRA_HOME_DEFAULT}"
PROJECT_DIR="${GHIDRA_PROJECT_DIR:-$PROJECT_DIR_DEFAULT}"
PROJECT_NAME="${GHIDRA_PROJECT_NAME:-$PROJECT_NAME_DEFAULT}"
PROGRAM_NAME="${GHIDRA_PROGRAM_NAME:-$PROGRAM_DEFAULT}"

echo "[headless] ghidra_home=$GHIDRA_HOME"
echo "[headless] project=$PROJECT_DIR/$PROJECT_NAME"
echo "[headless] program=$PROGRAM_NAME"
echo "[headless] map=$MAP_FILE"
echo "[headless] mode=$MODE"
echo "[headless] NOTE: Ghidra GUI must be fully closed or project lock will fail."

if command -v cmd.exe >/dev/null 2>&1; then
  GHIDRA_HOME_WIN="$(wslpath -w "$GHIDRA_HOME")"
  PROJECT_DIR_WIN="$(wslpath -w "$PROJECT_DIR")"
  SCRIPT_DIR_WIN="$(wslpath -w "$SCRIPT_DIR")"
  MAP_FILE_WIN="$(wslpath -w "$MAP_FILE")"

  python3 - "$GHIDRA_HOME_WIN" "$PROJECT_DIR_WIN" "$PROJECT_NAME" "$PROGRAM_NAME" "$SCRIPT_DIR_WIN" "$MAP_FILE_WIN" "$MODE" <<'PY'
import subprocess
import sys

ghidra_home, project_dir, project_name, program_name, script_dir, map_file, mode = sys.argv[1:]
bat = ghidra_home + "\\support\\analyzeHeadless.bat"

cmd = [
    "cmd.exe", "/c",
    bat,
    project_dir,
    project_name,
    "-process", program_name,
    "-scriptPath", script_dir,
    "-postScript", "GhidraBatchRename.java", map_file, mode,
    "-noanalysis",
]

res = subprocess.run(cmd)
sys.exit(res.returncode)
PY
else
  ANALYZE="$GHIDRA_HOME/support/analyzeHeadless"
  if [[ ! -x "$ANALYZE" ]]; then
    echo "analyzeHeadless not found/executable: $ANALYZE" >&2
    exit 2
  fi
  "$ANALYZE" \
    "$PROJECT_DIR" \
    "$PROJECT_NAME" \
    -process "$PROGRAM_NAME" \
    -scriptPath "$SCRIPT_DIR" \
    -postScript GhidraBatchRename.java "$MAP_FILE" "$MODE" \
    -noanalysis
fi
