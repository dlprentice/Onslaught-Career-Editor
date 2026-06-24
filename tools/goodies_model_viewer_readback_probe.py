#!/usr/bin/env python3
"""Validate read-only retail read-back for the Goodies model-viewer path.

This probe consumes existing ignored Ghidra decompile exports and Stuart source
files. It does not launch Ghidra, read or write BEA.exe, run the game, or mutate
any Ghidra project. The generated JSON remains under subagents/.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIMARY_DECOMPILE_DIR = (
    ROOT / "subagents" / "goodies-71-73-ghidra-readback" / "current" / "decompile"
)
DEFAULT_FULL_DECOMPILE_DIR = (
    ROOT / "subagents" / "ghidra-goodies-readback-2026-05-07" / "decompile"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-model-viewer-readback"
    / "current"
    / "goodies-model-viewer-readback.json"
)
SOURCE_CPP = ROOT / "references" / "Onslaught" / "FEPGoodies.cpp"
SOURCE_HEADER = ROOT / "references" / "Onslaught" / "FEPGoodies.h"


@dataclass(frozen=True)
class FileExpectation:
    name: str
    path: Path
    role: str
    required_tokens: tuple[str, ...]


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def line_hits(lines: list[str], tokens: tuple[str, ...]) -> dict[str, list[int]]:
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def summarize(expectation: FileExpectation) -> dict[str, object]:
    failures: list[str] = []
    token_hits: dict[str, list[int]] = {}
    if not expectation.path.is_file():
        failures.append("missing file")
    else:
        token_hits = line_hits(read_lines(expectation.path), expectation.required_tokens)
        failures.extend(
            f"missing token: {token}"
            for token, hits in token_hits.items()
            if not hits
        )
    return {
        "name": expectation.name,
        "role": expectation.role,
        "status": "PASS" if not failures else "FAIL",
        "file": relative(expectation.path),
        "tokenLineHits": token_hits,
        "failures": failures,
    }


def build_report(primary_decompile_dir: Path, full_decompile_dir: Path) -> dict[str, object]:
    expectations: tuple[FileExpectation, ...] = (
        FileExpectation(
            "source mesh deserialization branch",
            SOURCE_CPP,
            "source anchor",
            (
                "else if (mCurrentGoodyType==GT_MESH)",
                "mCurrentGoodyMesh=CMESH::Deserialize(c);",
            ),
        ),
        FileExpectation(
            "source mesh interaction controls",
            SOURCE_CPP,
            "source anchor",
            (
                "else if (mCurrentGoodyType == GT_MESH)",
                "mManualControl=!mManualControl;",
                "mMeshDistance+=dz*0.1f;",
                "Clamp(mMeshDistance, mCurrentGoodyMesh->mBoundingBox->mRadius",
            ),
        ),
        FileExpectation(
            "source mesh renderer path",
            SOURCE_CPP,
            "source anchor",
            (
                "CMESHRENDERER::SetRenderMode(R_NoTexture);",
                "CMESHRENDERER::SetRenderMode(R_Normal);",
                "CMESHRENDERER::RenderMesh(pos,ori,mCurrentGoodyMesh,NULL,NULL,0,FALSE,0);",
            ),
        ),
        FileExpectation(
            "source field anchors",
            SOURCE_HEADER,
            "source anchor",
            (
                "CMESH\t\t*mCurrentGoodyMesh;",
                "EGoodieType\tmCurrentGoodyType;",
                "BOOL\t\tmManualControl;",
                "float\t\tmMeshDistance;",
                "EGoodyState mGoodyState;",
            ),
        ),
        FileExpectation(
            "retail mesh deserialization branch",
            full_decompile_dir / "0045c870_CFEPGoodies__Deserialise.c",
            "retail decompile read-back",
            (
                "if (iVar4 == 1) {",
                "CMesh__Deserialize(chunk_reader,0);",
                "*(int *)((int)this + 0x148) = iVar4;",
                "*(int *)(iVar4 + 0x170) = *(int *)(iVar4 + 0x170) + 1;",
            ),
        ),
        FileExpectation(
            "retail mesh interaction controls",
            primary_decompile_dir / "0045cde0_CFEPGoodies__ButtonPressed.c",
            "retail decompile read-back",
            (
                "if (*(int *)((int)this + 0x154) != 1) {",
                "case 0x40:",
                "*(uint *)((int)this + 0x158) = (uint)(*(int *)((int)this + 0x158) == 0);",
                "*(float *)((int)this + 0x1d0) = fVar22 * _DAT_005d85c0 + *(float *)((int)this + 0x1d0);",
                "*(int *)(*(int *)((int)this + 0x148) + 0x150)",
            ),
        ),
        FileExpectation(
            "retail mesh update branch",
            primary_decompile_dir / "0045d7e0_CFEPGoodies__Process.c",
            "retail decompile read-back",
            (
                "else if (*(int *)((int)this + 0x154) == 1) {",
                "*(undefined4 *)((int)this + 0x158) = 1;",
                "(0x28,(float)(DAT_0089bda8 - DAT_006292ec) * _DAT_005d8588);",
                "(0x26,(float)(DAT_0089bda4 - DAT_006292f0) * _DAT_005d97d0);",
            ),
        ),
    )
    results = [summarize(expectation) for expectation in expectations]
    failures = [result for result in results if result["status"] != "PASS"]
    return {
        "schema": "goodies-model-viewer-readback.v1",
        "status": "pass" if not failures else "blocked",
        "primaryDecompileDir": relative(primary_decompile_dir),
        "fullDecompileDir": relative(full_decompile_dir),
        "filesChecked": len(results),
        "filesPassed": sum(1 for result in results if result["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores repo-relative source/decompile filenames, token labels, and line numbers only. It does not include private decompile excerpts, binaries, raw assets, screenshots, frames, or runtime proof JSON.",
        "proven": [
            "Stuart source contains the Goodies mesh deserialization, interaction, and render paths.",
            "Existing retail decompile exports contain the mesh deserialization branch and current mesh pointer assignment.",
            "Existing retail decompile exports contain the mesh interaction/update branch keyed by Goodie content bucket 1.",
        ],
        "notProven": [
            "Runtime in-game model-viewer replay in the Steam build.",
            "Native WinUI textured/material/animated model rendering parity.",
            "Camera, lighting, skeleton, animation, and material parity with the retail model viewer.",
        ],
    }


def resolve_under_root(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def assert_subagents_path(path: Path) -> bool:
    try:
        path.resolve().relative_to((ROOT / "subagents").resolve())
        return True
    except ValueError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate public-safe Goodies model-viewer decompile read-back evidence."
    )
    parser.add_argument("--check", action="store_true", help="run the read-back probe")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    parser.add_argument(
        "--primary-decompile-dir",
        type=Path,
        default=DEFAULT_PRIMARY_DECOMPILE_DIR,
        help="ignored decompile directory containing ButtonPressed/Process",
    )
    parser.add_argument(
        "--full-decompile-dir",
        type=Path,
        default=DEFAULT_FULL_DECOMPILE_DIR,
        help="ignored decompile directory containing Deserialise",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    primary_decompile_dir = resolve_under_root(args.primary_decompile_dir)
    full_decompile_dir = resolve_under_root(args.full_decompile_dir)
    out = resolve_under_root(args.out)
    for candidate in (primary_decompile_dir, full_decompile_dir, out.parent):
        if not assert_subagents_path(candidate):
            print(f"Refusing to read/write outside subagents/: {candidate}")
            return 1

    report = build_report(primary_decompile_dir, full_decompile_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Goodies model-viewer read-back probe")
        print(f"Status: {report['status']}")
        print(f"Files: {report['filesPassed']}/{report['filesChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['name']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
