#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
fi

echo "Docsync gate: validating canonical/mirror policy..."
python3 tools/docsync_check.py
echo

if ((DRY_RUN == 1)); then
  echo "Release snapshot gate: validating content-aware classification/profile/private inventory..."
  python3 tools/release_profile_snapshot.py --check
else
  echo "Release snapshot gate: refreshing content-aware classification/profile/private inventory..."
  python3 tools/release_profile_snapshot.py
fi
echo

if ((DRY_RUN == 1)); then
  echo "Curated manifest gate: validating allowlist expansion..."
else
  echo "Curated manifest gate: regenerating and validating allowlist expansion..."
  python3 tools/release_curated_manifest.py
fi
python3 tools/release_curated_manifest.py --check
python3 tools/public_allowlist_safety_check.py --self-test
python3 tools/public_allowlist_safety_check.py
echo

echo "Release gate parity checks (canonical vs lore-book artifacts):"
python3 - <<'PY'
from pathlib import Path
import sys

root = Path.cwd()
pairs = [
    ("roadmap/release-allowlist-profile.md", "lore-book/roadmap/release-allowlist-profile.md"),
    ("roadmap/release-allowlist-classification.tsv", "lore-book/roadmap/release-allowlist-classification.tsv"),
]

ok = True
for canonical, mirror in pairs:
    c = root / canonical
    m = root / mirror
    if not c.is_file() or not m.is_file():
        print(f"  FAIL missing pair: {canonical} <-> {mirror}")
        ok = False
        continue
    cb = c.read_bytes().replace(b"\r\n", b"\n")
    mb = m.read_bytes().replace(b"\r\n", b"\n")
    if cb != mb:
        print(f"  FAIL mismatch: {canonical} <-> {mirror}")
        ok = False
    else:
        print(f"  PASS match: {canonical} <-> {mirror}")

if not ok:
    sys.exit(1)
PY
echo

if ((DRY_RUN == 1)); then
  echo "Dry-run only: no archive created and no tracked release artifacts were rewritten."
  exit 0
fi

echo "Packaging is curated-allowlist-driven and intentionally not auto-executed by default."
echo "Curated allowlist file: release/readiness/public_candidate_allowlist.tsv"
echo "To refresh artifacts manually: python3 tools/release_profile_snapshot.py && python3 tools/release_curated_manifest.py"
echo "To materialize the standalone public-candidate tree: python3 tools/export_curated_release_tree.py --dest ../Onslaught-Career-Editor-public-candidate --force-clean"
