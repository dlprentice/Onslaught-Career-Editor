#!/usr/bin/env python3
"""Validate Wave913 mesh/collision read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave913-mesh-collision-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_mesh_collision_review_wave913_2026-05-27.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGETS = {
    "0x00479020": ("CMeshCollisionVolume__IsDirectionInsideTrianglePrism", "triangle-prism"),
    "0x00479200": ("Geometry__SelectClosestPointOnTriangleEdges", "closest-point"),
    "0x004ad830": ("CMeshCollisionVolume__VFunc_04_004ad830", "vtable-slot"),
    "0x00478c20": ("Geometry__IntersectSegmentTriangleAndStoreHit", "segment-triangle"),
    "0x00478510": ("CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore", "swept-sphere"),
    "0x00477ba0": ("Vec3__MagnitudeSquared", "magnitude-squared"),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def row_by_addr(rows: list[dict[str, str]], addr: str) -> dict[str, str] | None:
    want = addr.lower().replace("0x", "")
    for row in rows:
        got = (row.get("address") or "").lower().replace("0x", "")
        if got == want:
            return row
    return None


def build_report() -> dict[str, object]:
    failures: list[str] = []
    metadata = read_tsv(BASE / "metadata.tsv")
    tags = read_tsv(BASE / "tags.tsv")
    index = read_tsv(BASE / "decompile" / "index.tsv")
    instructions = read_tsv(BASE / "instructions.tsv")

    if len(instructions) < 1000:
        failures.append(f"instruction export too small: {len(instructions)}")

    for addr, (name, tag_token) in TARGETS.items():
        meta = row_by_addr(metadata, addr)
        if meta is None or meta.get("name") != name or meta.get("status") != "OK":
            failures.append(f"metadata mismatch for {addr}")
        tag_row = row_by_addr(tags, addr)
        if tag_row is None or tag_token not in tag_row.get("tags", ""):
            failures.append(f"tag token missing for {addr}: {tag_token}")
        decomp = row_by_addr(index, addr)
        if decomp is None or decomp.get("name") != name or decomp.get("status") != "OK":
            failures.append(f"decompile mismatch for {addr}")

    queue = json.loads(read_text(QUEUE_JSON) or "{}")
    if queue.get("status") != "PASS":
        failures.append("queue json is not PASS")

    for label, text in {
        "public_note": read_text(PUBLIC_NOTE),
        "mesh_doc": read_text(MESH_DOC),
        "campaign": read_text(CAMPAIGN),
    }.items():
        for required in ("Wave913", "CMeshCollisionVolume__IsDirectionInsideTrianglePrism", "Geometry__SelectClosestPointOnTriangleEdges"):
            if required not in text:
                failures.append(f"{label} missing {required}")

    return {
        "schema": "ghidra-mesh-collision-review-wave913.v1",
        "status": "PASS" if not failures else "FAIL",
        "targets": sorted(TARGETS),
        "mutatedTargets": 0,
        "instructionRows": len(instructions),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE / "wave913-mesh-collision-review.json")
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Ghidra Wave913 mesh/collision review probe")
    print("Status:", report["status"])
    print("Output:", args.out.relative_to(ROOT))
    if report["failures"]:
        for failure in report["failures"]:
            print("-", failure)
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
