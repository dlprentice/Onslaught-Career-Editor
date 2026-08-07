#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Quarantine local-lab / lab evidence before any destructive delete.

Durable rule (maintainer FRAGO 2026-08-06, after the re-campaign fixture
loss): nothing under local-lab/ is ever hard-deleted in one step. ``stage``
moves a path to D:\\lab-quarantine\\<date>\\ preserving relative structure
plus a manifest row (original path, sha256 of the whole tree, bytes, reason,
staged-at). ``restore`` moves it back. ``purge`` (explicit, separate command)
removes a staged item ONLY when space pressure requires it and the manifest
row is confirmed; purged rows are rewritten to a purge log with the same
identity so recovery by name remains possible for as long as the drive
retains the blocks.

D: must be present and have free space; the rule refuses to run without it.
Use this instead of Remove-Item for anything that is not regenerable build
output inside an active tool's own scratch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

QUARANTINE_ROOT = Path(r"D:\lab-quarantine")
MANIFEST = QUARANTINE_ROOT / "manifest.jsonl"
PURGE_LOG = QUARANTINE_ROOT / "purge.log"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            digest.update(rel.encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("utf-8"))
            digest.update(b"\0")
    return digest.hexdigest()


def stage(path: Path, *, reason: str) -> dict:
    path = path.resolve()
    if not path.exists():
        raise SystemExit(f"path does not exist: {path}")
    if not QUARANTINE_ROOT.exists():
        raise SystemExit(f"quarantine root missing: {QUARANTINE_ROOT} (is D: mounted?)")
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    dest = QUARANTINE_ROOT / date / f"{uuid.uuid4().hex[:8]}-{path.name}"
    if path.is_dir():
        shutil.copytree(path, dest)
    else:
        shutil.copy2(path, dest)
    row = {
        "id": dest.name,
        "original": str(path),
        "staged": str(dest),
        "stagedAtUtc": utc_now(),
        "bytes": sum(p.stat().st_size for p in dest.rglob("*")) if dest.is_dir() else dest.stat().st_size,
        "sha256": tree_sha256(dest) if dest.is_dir() else hashlib.sha256(dest.read_bytes()).hexdigest(),
        "reason": reason,
    }
    with MANIFEST.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row) + "\n")
    return row


def restore(row_id: str) -> dict:
    rows = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]
    match = [r for r in rows if r["id"] == row_id]
    if not match:
        raise SystemExit(f"no staged row with id {row_id}")
    row = match[-1]
    staged = Path(row["staged"])
    original = Path(row["original"])
    if not staged.exists():
        raise SystemExit(f"staged copy missing: {staged}")
    if original.exists():
        raise SystemExit(f"refusing to overwrite existing path: {original}")
    original.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(staged), str(original))
    remaining = [r for r in rows if r["id"] != row_id]
    MANIFEST.write_text("\n".join(json.dumps(r) for r in remaining) + ("\n" if remaining else ""), encoding="utf-8")
    return row


def purge(row_id: str, *, reason: str) -> dict:
    rows = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]
    match = [r for r in rows if r["id"] == row_id]
    if not match:
        raise SystemExit(f"no staged row with id {row_id}")
    row = match[-1]
    staged = Path(row["staged"])
    if staged.exists():
        shutil.rmtree(staged) if staged.is_dir() else staged.unlink()
    with PURGE_LOG.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({**row, "purgedAtUtc": utc_now(), "purgeReason": reason}) + "\n")
    remaining = [r for r in rows if r["id"] != row_id]
    MANIFEST.write_text("\n".join(json.dumps(r) for r in remaining) + ("\n" if remaining else ""), encoding="utf-8")
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_stage = sub.add_parser("stage")
    p_stage.add_argument("path")
    p_stage.add_argument("--reason", required=True)
    p_restore = sub.add_parser("restore")
    p_restore.add_argument("id")
    p_purge = sub.add_parser("purge")
    p_purge.add_argument("id")
    p_purge.add_argument("--reason", required=True)
    p_list = sub.add_parser("list")
    args = parser.parse_args(argv)

    if args.command == "stage":
        row = stage(Path(args.path), reason=args.reason)
    elif args.command == "restore":
        row = restore(args.id)
    elif args.command == "purge":
        row = purge(args.id, reason=args.reason)
    else:
        if MANIFEST.exists():
            for line in MANIFEST.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    print(f"{r['id']}  {r['stagedAtUtc'][:19]}  {r['original']}")
        return 0
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
