#!/usr/bin/env python3
"""Validate read-only retail read-back for the main mesh renderer dispatch.

This probe consumes an existing ignored Ghidra decompile export. It does not
launch Ghidra, read or write BEA.exe, run the game, or mutate a Ghidra project.
The generated JSON remains under subagents/.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECOMPILE_DIR = (
    ROOT / "subagents" / "battleengine-cloak-stealth-candidate" / "current" / "decompile"
)
DEFAULT_OUT = ROOT / "subagents" / "mesh-renderer-readback" / "current" / "mesh-renderer-readback.json"
DOC_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshRenderer.cpp" / "_index.md"
LORE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "MeshRenderer.cpp" / "_index.md"


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


def parse_index(index_path: Path) -> list[dict[str, str]]:
    if not index_path.is_file():
        return []
    with index_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def index_status(decompile_dir: Path) -> dict[str, object]:
    rows = parse_index(decompile_dir / "index.tsv")
    matches = [
        row
        for row in rows
        if row.get("address", "").lower() == "0x004b6350"
        and row.get("name") == "CMeshRenderer__RenderMesh"
    ]
    failures: list[str] = []
    if not rows:
        failures.append("missing or empty decompile index")
    elif not matches:
        failures.append("missing 0x004b6350 CMeshRenderer__RenderMesh index row")
    elif matches[0].get("status") != "OK":
        failures.append(f"index row status is {matches[0].get('status')}")
    return {
        "status": "PASS" if not failures else "FAIL",
        "row": matches[0] if matches else {},
        "failures": failures,
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
    render_mesh = decompile_dir / "004b6350_CMeshRenderer__RenderMesh.c"
    expectations = (
        FileExpectation(
            "retail renderer dispatch",
            render_mesh,
            "retail decompile read-back",
            (
                "/* address: 0x004b6350 */",
                "/* name: CMeshRenderer__RenderMesh */",
                "((param_7 & 1) != 1))",
                "((param_7 & 0x10) == 0x10)",
                "CParticleManager__CreateEffect();",
                "param_3 = (float *)param_3[0x49];",
                "CMeshRenderer__RenderMeshCore();",
                "CPolyBucket__DebugRender();",
                "CTexture__FindTexture(s_meshtex_default_tga_00625498,0,0,-1,1,1);",
            ),
        ),
        FileExpectation(
            "retail particle attachment state",
            render_mesh,
            "retail decompile read-back",
            (
                "if (puVar11[0x12] == 0x461c4000)",
                "if (pfVar5[0x12] == 10000.0)",
                "puVar11[0x20] = *param_1;",
                "puVar11[0x10] = *param_1;",
            ),
        ),
        FileExpectation(
            "public function index",
            DOC_INDEX,
            "public docs",
            (
                "0x004b6350 | CMeshRenderer__RenderMesh",
                "CMeshRenderer__RenderMeshCore()",
                "meshtex_default.tga",
                "CParticleManager__CreateEffect()",
            ),
        ),
        FileExpectation(
            "lore function index mirror",
            LORE_INDEX,
            "public docs",
            (
                "0x004b6350 | CMeshRenderer__RenderMesh",
                "CMeshRenderer__RenderMeshCore()",
                "meshtex_default.tga",
                "CParticleManager__CreateEffect()",
            ),
        ),
    )
    index = index_status(decompile_dir)
    results = [summarize(expectation) for expectation in expectations]
    failures = [result for result in results if result["status"] != "PASS"]
    if index["status"] != "PASS":
        failures.append(index)
    return {
        "schema": "mesh-renderer-readback.v1",
        "status": "pass" if not failures else "blocked",
        "decompileDir": relative(decompile_dir),
        "index": index,
        "filesChecked": len(results),
        "filesPassed": sum(1 for result in results if result["status"] == "PASS"),
        "results": results,
        "privacy": "Report stores repo-relative public doc/decompile filenames, token labels, and line numbers only. It does not include private decompile excerpts, binaries, raw assets, screenshots, frames, or runtime proof JSON.",
        "proven": [
            "Existing retail decompile export contains an OK index row for CMeshRenderer__RenderMesh at 0x004b6350.",
            "Existing retail decompile export contains normal render dispatch through CMeshRenderer__RenderMeshCore.",
            "Existing retail decompile export contains particle attachment and default texture fallback context.",
            "Public MeshRenderer function docs carry the same bounded behavior summary.",
        ],
        "notProven": [
            "Exact full source parity for MeshRenderer.cpp, because that source file is not present in this checkout.",
            "Retail Goodies model-viewer runtime playback.",
            "Native WinUI textured/material/animated model rendering.",
            "Camera, lighting, skeleton, animation, or material parity with the retail renderer.",
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
        description="Validate public-safe MeshRenderer decompile read-back evidence."
    )
    parser.add_argument("--check", action="store_true", help="run the read-back probe")
    parser.add_argument("--json", action="store_true", help="print full JSON report")
    parser.add_argument(
        "--decompile-dir",
        type=Path,
        default=DEFAULT_DECOMPILE_DIR,
        help="ignored decompile directory containing CMeshRenderer__RenderMesh",
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
        print("MeshRenderer read-back probe")
        print(f"Status: {report['status']}")
        print(f"Index: {report['index']['status']}")
        print(f"Files: {report['filesPassed']}/{report['filesChecked']}")
        for item in report["results"]:
            print(f"- {item['status']}: {item['name']}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
