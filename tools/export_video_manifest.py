#!/usr/bin/env python3
"""
Build a read-only manifest for the loose .vid/Bink corpus.

Examples:
    py -3 tools/export_video_manifest.py
    py -3 tools/export_video_manifest.py --video-root game/data/video --out-dir subagents/video_manifest_wave1_2026-03-13
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from collections import Counter
from pathlib import Path


BRIEFING_RE = re.compile(r"^PC_(\d{3})_exact\.vid$", re.IGNORECASE)
CUTSCENE_RE = re.compile(r"^(\d{2})\.vid$", re.IGNORECASE)


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify_family(relative_path: str) -> tuple[str, str | None]:
    name = Path(relative_path).name
    if (m := BRIEFING_RE.match(name)) is not None:
        return "briefing", m.group(1)
    if (m := CUTSCENE_RE.match(name)) is not None:
        return "cutscene_numeric", m.group(1)
    return "named_root", None


def build_manifest(video_root: Path) -> dict[str, object]:
    files = sorted(video_root.rglob("*.vid"))
    records: list[dict[str, object]] = []
    family_counts: Counter[str] = Counter()
    briefing_episode_counts: Counter[str] = Counter()
    cutscene_numbers: list[int] = []
    total_bytes = 0

    for path in files:
        relative_path = path.relative_to(video_root).as_posix()
        family, sequence_id = classify_family(relative_path)
        size = path.stat().st_size
        magic = path.read_bytes()[:4].decode("ascii", errors="replace")
        sha256 = sha256_path(path)

        family_counts[family] += 1
        total_bytes += size

        if family == "briefing" and sequence_id is not None:
            briefing_episode_counts[sequence_id[0]] += 1
        if family == "cutscene_numeric" and sequence_id is not None:
            cutscene_numbers.append(int(sequence_id))

        records.append(
            {
                "relative_path": relative_path,
                "family": family,
                "sequence_id": sequence_id,
                "size": size,
                "sha256": sha256,
                "magic": magic,
            }
        )

    expected_cutscene_numbers = set(range(1, 34))
    present_cutscene_numbers = set(cutscene_numbers)
    missing_cutscene_numbers = sorted(expected_cutscene_numbers - present_cutscene_numbers)

    return {
        "video_root": str(video_root),
        "summary": {
            "file_count": len(records),
            "total_bytes": total_bytes,
            "family_counts": dict(sorted(family_counts.items())),
            "briefing_episode_counts": dict(sorted(briefing_episode_counts.items())),
            "cutscene_range_min": min(cutscene_numbers) if cutscene_numbers else None,
            "cutscene_range_max": max(cutscene_numbers) if cutscene_numbers else None,
            "missing_cutscene_numbers": missing_cutscene_numbers,
            "all_magic_values": sorted({record["magic"] for record in records}),
        },
        "files": records,
    }


def write_tsv(path: Path, manifest: dict[str, object]) -> None:
    rows = [
        "relative_path\tfamily\tsequence_id\tsize\tsha256\tmagic",
    ]
    for record in manifest["files"]:
        rows.append(
            "\t".join(
                [
                    str(record["relative_path"]),
                    str(record["family"]),
                    str(record["sequence_id"] or ""),
                    str(record["size"]),
                    str(record["sha256"]),
                    str(record["magic"]),
                ]
            )
        )
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video-root", type=Path, default=Path("game/data/video"))
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("subagents") / "video_manifest_wave1_2026-03-13",
    )
    ap.add_argument("--self-test", action="store_true", help="Run built-in parser/guard checks without private game assets")
    return ap.parse_args()


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "video"
        briefing_dir = root / "briefings"
        briefing_dir.mkdir(parents=True)
        (briefing_dir / "PC_100_exact.vid").write_bytes(b"BIKi" + b"\x00" * 12)
        (root / "01.vid").write_bytes(b"BIKi" + b"\x01" * 8)
        (root / "intro.vid").write_bytes(b"BIKi" + b"\x02" * 4)

        missing = Path(tmp) / "missing-video-root"
        if missing.is_dir():
            raise AssertionError("self-test missing root unexpectedly exists")

        manifest = build_manifest(root)
        summary = manifest["summary"]
        assert summary["file_count"] == 3
        assert summary["family_counts"] == {"briefing": 1, "cutscene_numeric": 1, "named_root": 1}
        assert summary["all_magic_values"] == ["BIKi"]
        assert summary["cutscene_range_min"] == 1
        assert summary["cutscene_range_max"] == 1
        assert 32 in summary["missing_cutscene_numbers"]

    print("export_video_manifest self-test: PASS")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    if not args.video_root.is_dir():
        print(f"ERROR: video root does not exist or is not a directory: {args.video_root}")
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(args.video_root)
    json_path = args.out_dir / "manifest.json"
    tsv_path = args.out_dir / "manifest.tsv"
    summary_path = args.out_dir / "summary.json"

    json_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_tsv(tsv_path, manifest)
    summary_path.write_text(json.dumps(manifest["summary"], indent=2), encoding="utf-8")

    print(json.dumps({"json": str(json_path), "tsv": str(tsv_path), "summary": str(summary_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
