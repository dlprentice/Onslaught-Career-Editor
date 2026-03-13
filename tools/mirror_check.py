#!/usr/bin/env python3
"""
Repo-local offline mirror check between:
  reverse-engineering/**  (canonical)
  lore-book/reverse-engineering/**  (mirror)

This is intentionally "dumb and strict": it checks file presence and byte-for-byte
equality (after normalizing line endings) for markdown files. It is meant to
support the documentation discipline used in this repo: canonical RE docs should
be mirrored into the lore-book tree so the Lore Browser can render them.

Usage:
  python3 tools/mirror_check.py --date 2026-02-12

Outputs:
  reverse-engineering/binary-analysis/mirror-check-YYYY-MM-DD.md
  reverse-engineering/binary-analysis/mirror-check-YYYY-MM-DD.json
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
from typing import Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
CANON_ROOT = REPO_ROOT / "reverse-engineering"
MIRROR_ROOT = REPO_ROOT / "lore-book" / "reverse-engineering"


def normalize_text_bytes(p: Path) -> bytes:
    data = p.read_bytes()
    # Normalize CRLF/LF for stable comparisons across Windows/WSL edits.
    data = data.replace(b"\r\n", b"\n")
    return data


def list_md(root: Path) -> Dict[str, Path]:
    out: Dict[str, Path] = {}
    for p in root.rglob("*.md"):
        rel = p.relative_to(root).as_posix()
        # Ignore transient agent wave outputs if someone placed them under reverse-engineering.
        if rel.startswith("wave_"):
            continue
        out[rel] = p
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    ap.add_argument(
        "--out-dir",
        default="reverse-engineering/binary-analysis",
        help="Output directory (workspace-relative).",
    )
    args = ap.parse_args()

    if not CANON_ROOT.is_dir():
        raise SystemExit(f"missing canonical root: {CANON_ROOT}")
    if not MIRROR_ROOT.is_dir():
        raise SystemExit(f"missing mirror root: {MIRROR_ROOT}")

    canon = list_md(CANON_ROOT)
    mirror = list_md(MIRROR_ROOT)

    missing_in_mirror: List[str] = []
    extra_in_mirror: List[str] = []
    diffs: List[Dict[str, str]] = []

    for rel, p in sorted(canon.items()):
        mp = mirror.get(rel)
        if mp is None:
            missing_in_mirror.append(rel)
            continue
        if normalize_text_bytes(p) != normalize_text_bytes(mp):
            diffs.append({"path": rel, "canonical": p.relative_to(REPO_ROOT).as_posix(), "mirror": mp.relative_to(REPO_ROOT).as_posix()})

    for rel in sorted(mirror.keys()):
        if rel not in canon:
            extra_in_mirror.append(rel)

    out_dir = (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "date": args.date,
        "canonical_root": str(CANON_ROOT.relative_to(REPO_ROOT).as_posix()),
        "mirror_root": str(MIRROR_ROOT.relative_to(REPO_ROOT).as_posix()),
        "canonical_md_files": len(canon),
        "mirror_md_files": len(mirror),
        "missing_in_mirror": missing_in_mirror,
        "extra_in_mirror": extra_in_mirror,
        "diffs": diffs,
    }

    out_json = out_dir / f"mirror-check-{args.date}.json"
    out_md = out_dir / f"mirror-check-{args.date}.md"
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines: List[str] = []
    lines.append(f"# Mirror Check (reverse-engineering -> lore-book) ({args.date})")
    lines.append("")
    lines.append(f"- Canonical markdown files: `{len(canon)}`")
    lines.append(f"- Mirror markdown files: `{len(mirror)}`")
    lines.append(f"- Missing in mirror: `{len(missing_in_mirror)}`")
    lines.append(f"- Extra in mirror: `{len(extra_in_mirror)}`")
    lines.append(f"- Content diffs: `{len(diffs)}`")
    lines.append("")

    if missing_in_mirror:
        lines.append("## Missing In Mirror (Top 200)")
        lines.append("")
        for rel in missing_in_mirror[:200]:
            lines.append(f"- `{rel}`")
        if len(missing_in_mirror) > 200:
            lines.append(f"- ... (+{len(missing_in_mirror) - 200} more)")
        lines.append("")

    if extra_in_mirror:
        lines.append("## Extra In Mirror (Top 200)")
        lines.append("")
        for rel in extra_in_mirror[:200]:
            lines.append(f"- `{rel}`")
        if len(extra_in_mirror) > 200:
            lines.append(f"- ... (+{len(extra_in_mirror) - 200} more)")
        lines.append("")

    if diffs:
        lines.append("## Content Diffs (Top 200)")
        lines.append("")
        for d in diffs[:200]:
            lines.append(f"- `{d['path']}` (canonical `{d['canonical']}` vs mirror `{d['mirror']}`)")
        if len(diffs) > 200:
            lines.append(f"- ... (+{len(diffs) - 200} more)")
        lines.append("")

    if not missing_in_mirror and not extra_in_mirror and not diffs:
        lines.append("No mirror issues detected.")
        lines.append("")

    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(out_md.relative_to(REPO_ROOT).as_posix())
    print(out_json.relative_to(REPO_ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

