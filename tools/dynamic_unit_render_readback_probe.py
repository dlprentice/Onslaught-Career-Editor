#!/usr/bin/env python3
"""Validate read-only retail read-back for the dynamic unit render pass.

This probe consumes an existing ignored Ghidra decompile export. It does not
launch Ghidra, read or write BEA.exe, run the game, or mutate a Ghidra project.
The generated JSON remains under subagents/.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECOMPILE_DIR = (
    ROOT / "subagents" / "battleengine-cloak-stealth-candidate" / "current" / "decompile"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "dynamic-unit-render-readback"
    / "current"
    / "dynamic-unit-render-readback.json"
)
DOC_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"
LORE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "vbuftexture.cpp" / "_index.md"


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


def build_report(decompile_dir: Path) -> dict[str, object]:
    dynamic_pass = decompile_dir / "00476fe0_CVBufTexture__RenderDynamicUnitPass.c"
    expectations = (
        FileExpectation(
            "retail dynamic unit render pass",
            dynamic_pass,
            "retail decompile read-back",
            (
                "/* address: 0x00476fe0 */",
                "/* name: CVBufTexture__RenderDynamicUnitPass */",
                "DAT_00855178 = DAT_00855170;",
                "CVBufTexture__QueueRenderIfDepthInRange",
                "CVBufTexture__DispatchTextureTransformThunk();",
                "CDXEngine__BuildProjectedSprites(&DAT_009c7550,piVar8);",
                "CRenderQueue__InsertSortedByDepth(&DAT_009c7550,piVar8,fVar13);",
            ),
        ),
        FileExpectation(
            "retail visibility and LOD gates",
            dynamic_pass,
            "retail decompile read-back",
            (
                "g_MeshQualityDistance",
                "g_MeshQualityLodTable",
                "_DAT_005d8568 / fStack_1f4",
                "DAT_0089d680 == '\\0'",
                "(piVar8[0xd] & 0x800000U) != 0",
            ),
        ),
        FileExpectation(
            "retail collision-map owner traversal",
            dynamic_pass,
            "retail decompile read-back",
            (
                "CCollisionSeekingRound__IterSetHeadFromMapWhoEntry",
                "CMapWhoEntry__GetOwner();",
                "CCollisionSeekingRound__IterPopNextEntry(&DAT_00704200);",
            ),
        ),
        FileExpectation(
            "public vbuftexture index",
            DOC_INDEX,
            "public docs",
            (
                "CVBufTexture__RenderDynamicUnitPass",
                "CRenderQueue__InsertSortedByDepth",
                "CDXEngine__BuildProjectedSprites",
                "g_MeshQualityLodTable",
            ),
        ),
        FileExpectation(
            "lore vbuftexture index mirror",
            LORE_INDEX,
            "public docs",
            (
                "CVBufTexture__RenderDynamicUnitPass",
                "CRenderQueue__InsertSortedByDepth",
                "CDXEngine__BuildProjectedSprites",
                "g_MeshQualityLodTable",
            ),
        ),
    )
    results = [summarize(expectation) for expectation in expectations]
    failures = [result for result in results if result["status"] != "PASS"]
    return {
        "schema": "dynamic-unit-render-readback.v1",
        "status": "pass" if not failures else "blocked",
        "decompileDir": relative(decompile_dir),
        "filesChecked": len(results),
        "filesPassed": sum(1 for result in results if result["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores repo-relative public doc/decompile filenames, token labels, and line numbers only. It does not include private decompile excerpts, binaries, raw assets, screenshots, frames, or runtime proof JSON.",
        "proven": [
            "Existing retail decompile export contains the dynamic unit render pass at 0x00476fe0.",
            "Existing retail decompile export contains unit-list traversal, collision-map owner traversal, projected-sprite path, render-queue insertion, and LOD/depth gates.",
            "Public vbuftexture function docs carry the same bounded behavior summary.",
        ],
        "notProven": [
            "Exact full source identity for the dynamic unit pass.",
            "Material, shader, skeleton, animation, or camera parity with the retail renderer.",
            "Native WinUI textured/material/animated model rendering.",
            "Runtime Goodies model-viewer playback.",
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
        description="Validate public-safe dynamic unit render decompile read-back evidence."
    )
    parser.add_argument("--check", action="store_true", help="run the read-back probe")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    parser.add_argument(
        "--decompile-dir",
        type=Path,
        default=DEFAULT_DECOMPILE_DIR,
        help="ignored decompile directory containing CVBufTexture__RenderDynamicUnitPass",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    decompile_dir = resolve_under_root(args.decompile_dir)
    out = resolve_under_root(args.out)
    for candidate in (decompile_dir, out.parent):
        if not assert_subagents_path(candidate):
            print(f"Refusing to read/write outside subagents/: {candidate}")
            return 1

    report = build_report(decompile_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Dynamic unit render read-back probe")
        print(f"Status: {report['status']}")
        print(f"Files: {report['filesPassed']}/{report['filesChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['name']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
