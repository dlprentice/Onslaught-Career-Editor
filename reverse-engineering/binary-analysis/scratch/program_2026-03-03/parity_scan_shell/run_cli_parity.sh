#!/usr/bin/env bash
set -euo pipefail

OUT="reverse-engineering/binary-analysis/scratch/program_2026-03-03/parity_scan_shell"
mkdir -p "$OUT"

CS="/mnt/c/Program Files/dotnet/dotnet.exe"
DLL="bin/Debug/net10.0-windows/Onslaught - Career Editor.dll"
BASE_BES="save-attempts/haha-cannon-goes-brrrrr.bes"
BASE_BEA="game/defaultoptions.bea"

run_case() {
  name="$1"; shift
  infile="$1"; shift
  cs_out="$OUT/${name}.csharp.out"
  py_out="$OUT/${name}.python.out"
  cs_log="$OUT/${name}.csharp.log"
  py_log="$OUT/${name}.python.log"

  rm -f "$cs_out" "$py_out" "$cs_log" "$py_log" "$OUT/${name}.csharp.goodies.txt" "$OUT/${name}.python.goodies.txt"

  set +e
  "$CS" "$DLL" "$infile" "$cs_out" "$@" >"$cs_log" 2>&1
  cs_rc=$?
  python3 patcher.py "$infile" "$py_out" "$@" >"$py_log" 2>&1
  py_rc=$?
  set -e

  cs_ok=0
  py_ok=0
  [[ $cs_rc -eq 0 && -f "$cs_out" ]] && cs_ok=1
  [[ $py_rc -eq 0 && -f "$py_out" ]] && py_ok=1

  byte_equal="N/A"
  if [[ $cs_ok -eq 1 && $py_ok -eq 1 ]]; then
    if cmp -s "$cs_out" "$py_out"; then
      byte_equal="yes"
    else
      byte_equal="no"
      cmp -l "$cs_out" "$py_out" | head -n 12 > "$OUT/${name}.byte_diff.txt" || true
    fi
  fi

  list_equal="N/A"
  if [[ $cs_ok -eq 1 && $py_ok -eq 1 ]]; then
    set +e
    "$CS" "$DLL" "$cs_out" --list-goodies --show-reserved-goodies >"$OUT/${name}.csharp.goodies.txt" 2>&1
    csg_rc=$?
    python3 patcher.py "$py_out" --list-goodies --show-reserved-goodies >"$OUT/${name}.python.goodies.txt" 2>&1
    pyg_rc=$?
    set -e
    if [[ $csg_rc -eq 0 && $pyg_rc -eq 0 ]]; then
      if cmp -s "$OUT/${name}.csharp.goodies.txt" "$OUT/${name}.python.goodies.txt"; then
        list_equal="yes"
      else
        list_equal="no"
        diff -u "$OUT/${name}.csharp.goodies.txt" "$OUT/${name}.python.goodies.txt" | head -n 200 > "$OUT/${name}.goodies_diff.patch" || true
      fi
    else
      list_equal="error"
    fi
  fi

  printf "%s\tcs_rc:%s\tpy_rc:%s\tcs_ok:%s\tpy_ok:%s\tbytes:%s\tgoodies:%s\n" \
    "$name" "$cs_rc" "$py_rc" "$cs_ok" "$py_ok" "$byte_equal" "$list_equal" >> "$OUT/summary.tsv"
}

: > "$OUT/summary.tsv"

run_case career_default_unlock "$BASE_BES" --rank S --kills 400
run_case career_kills_only_custom "$BASE_BES" --kills-only --aircraft-kills 25 --vehicle-kills 201 --emplacement-kills 51 --infantry-kills 160 --mech-kills 40
run_case career_partial_rank_and_bindings "$BASE_BES" --rank E --level-rank 1:S --level-rank 13:B --level-rank 43:A --bind-select-weapon MouseRight "Key ;" --bind-transform RControl "Key X" --invert-walker-p1 on --invert-walker-p2 off
run_case options_settings_only "$BASE_BEA" --no-nodes --no-links --no-goodies --no-kills --sound-volume 0.31 --music-volume 0.77 --invert-flight-p1 off --invert-flight-p2 on --vibration-p1 on --vibration-p2 off --controller-config-p1 2 --controller-config-p2 3
run_case options_copy_entries_only "$BASE_BEA" --no-nodes --no-links --no-goodies --no-kills --copy-options-from "$BASE_BES" --no-copy-options-tail --bind-air-brake LShift RShift

cat "$OUT/summary.tsv"
