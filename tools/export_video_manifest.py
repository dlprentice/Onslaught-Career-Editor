#!/usr/bin/env python3
"""
Build a read-only manifest for the loose .vid/Bink corpus.

Examples:
    py -3 tools/export_video_manifest.py
    py -3 tools/export_video_manifest.py --video-root game/data/video --out-dir .artifacts/video-manifest
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from collections import Counter
from pathlib import Path

from safe_generated_output import SecuredOutputRoot, UnsafeGeneratedOutputError


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


def build_manifest(
    video_root: Path,
    files: list[Path] | None = None,
) -> dict[str, object]:
    files = sorted(video_root.rglob("*.vid")) if files is None else files
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


def write_tsv(output: SecuredOutputRoot, path: Path, manifest: dict[str, object]) -> None:
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
    output.atomic_write_text(path, "\n".join(rows) + "\n")


def write_manifest_outputs(video_root: Path, out_dir: Path) -> tuple[Path, Path, Path]:
    video_root = video_root.resolve(strict=True)
    out_dir = out_dir.resolve()
    video_files = sorted(path.resolve(strict=True) for path in video_root.rglob("*.vid"))
    json_path = out_dir / "manifest.json"
    tsv_path = out_dir / "manifest.tsv"
    summary_path = out_dir / "summary.json"

    with SecuredOutputRoot(
        out_dir,
        protected_sources=(video_root, *video_files),
    ) as output:
        manifest = build_manifest(video_root, video_files)
        output.atomic_write_json(json_path, manifest)
        write_tsv(output, tsv_path, manifest)
        output.atomic_write_json(summary_path, manifest["summary"])
    return json_path, tsv_path, summary_path


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video-root", type=Path, default=Path("game/data/video"))
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path(".artifacts") / "video-manifest",
    )
    ap.add_argument("--self-test", action="store_true", help="Run built-in parser/guard checks without game assets")
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

        out_dir = Path(tmp) / "out"
        out_dir.mkdir()
        external = Path(tmp) / "outside.json"
        external.write_text("outside-canary", encoding="utf-8")
        try:
            (out_dir / "manifest.json").hardlink_to(external)
        except OSError:
            pass
        else:
            try:
                write_manifest_outputs(root, out_dir)
                raise AssertionError("hardlinked child destination should be rejected")
            except UnsafeGeneratedOutputError:
                assert external.read_text(encoding="utf-8") == "outside-canary"

    print("export_video_manifest self-test: PASS")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    if not args.video_root.is_dir():
        print(f"ERROR: video root does not exist or is not a directory: {args.video_root}")
        return 1

    json_path, tsv_path, summary_path = write_manifest_outputs(
        args.video_root,
        args.out_dir,
    )

    print(json.dumps({"json": str(json_path), "tsv": str(tsv_path), "summary": str(summary_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
