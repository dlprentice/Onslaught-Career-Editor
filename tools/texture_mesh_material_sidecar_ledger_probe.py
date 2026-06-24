#!/usr/bin/env python3
"""Validate the texture/mesh material sidecar ledger proof."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import model_texture_linkage_probe as linkage  # noqa: E402
import texture_mesh_material_sidecar_ledger as ledger_tool  # noqa: E402


BASE = ROOT / "subagents" / "texture_mesh_asset_bridge_proof_2026-06-08"
CATALOG = BASE / "asset_catalog" / "catalog.json"
LEDGER_ROOT = ROOT / "subagents" / "texture_mesh_material_sidecar_ledger_2026-06-08"
LEDGER = LEDGER_ROOT / "asset-material-sidecar-ledger.json"
OLD_LEDGER_ROOT = BASE / "material_sidecar_ledger"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-ledger-proof.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-ledger-proof.md"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_ledger_2026-06-08.md"
COPIED_CORPUS = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-copied-corpus-proof.md"
PLAN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-proof-plan.md"
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PACKAGE_JSON = ROOT / "package.json"

RESULT_LINK = "texture-mesh-material-sidecar-ledger-proof.md"
ABSOLUTE_USER_SENTINEL = "C:" + "\\Users" + "\\david"

EXPECTED_COPIED_ROOT = {
    "files": 8574,
    "bytes": 250335133,
}

EXPECTED_TOP_LEVEL_CHUNKS = {
    "TEXT": 18857,
    "MESH": 3492,
    "GDIE": 232,
    "LVLR": 301,
    "TARG": 301,
    "AYAD": 301,
}

EXPECTED_PACKED_REFS = {
    "textTextures": "601/601",
    "referenceMeshes": "209/209",
    "gdieTextures": "206/206",
    "gdieMeshes": "42/42",
}

EXPECTED_EXPORT_LANES = {
    "looseTextures": {"rows": 847, "succeeded": 847, "failed": 0, "skippedExisting": 0},
    "looseMeshes": {"rows": 213, "succeeded": 213, "failed": 0, "skippedExisting": 0},
    "embeddedMeshes": {"rows": 139, "succeeded": 139, "failed": 0, "skippedExisting": 0},
}

EXPECTED_CATALOG = {
    "textures": 828,
    "looseMeshes": 213,
    "embeddedMeshes": 139,
    "videos": 66,
    "languageRows": 2571,
    "goodies": 233,
    "totalRows": 4050,
}

EXPECTED_MODEL_COVERAGE = {
    "modelRows": 352,
    "modelRowsWithTextureRefs": 352,
    "modelTextureReferenceInstances": 1268,
    "modelRowsWithAllTextureRefsCatalogMapped": 352,
    "modelRowsWithAnyCatalogMissingTextureRef": 0,
    "modelRowsWithAnyMissingSidecarTextureRef": 0,
    "uniqueModelTextureRefs": 213,
    "sidecarTextureFiles": 213,
    "uniqueTextureRefsWithExactSidecarName": 212,
    "uniqueTextureRefsWithSidecarStemOnly": 1,
    "uniqueTextureRefsMissingSidecar": 0,
    "uniqueTextureRefsMissingCatalogRows": 0,
    "uniqueTextureRefsAmbiguousInCatalog": 1,
}

EXPECTED_KIND_COVERAGE = {
    "loose": {
        "rows": 213,
        "rowsWithRefs": 213,
        "textureRefInstances": 602,
        "uniqueTextureRefs": 213,
        "uniqueRefsMissingSidecar": 0,
        "uniqueRefsMissingCatalogRows": 0,
    },
    "embedded": {
        "rows": 139,
        "rowsWithRefs": 139,
        "textureRefInstances": 666,
        "uniqueTextureRefs": 28,
        "uniqueRefsMissingSidecar": 0,
        "uniqueRefsMissingCatalogRows": 0,
    },
}

EXPECTED_EXPORT_UNIQUENESS = {
    "looseMeshes": {
        "rows": 213,
        "uniqueOutputFiles": 213,
        "duplicateOutputGroups": 0,
        "duplicateOutputRows": 0,
    },
    "embeddedMeshes": {
        "rows": 139,
        "uniqueOutputFiles": 107,
        "duplicateOutputGroups": 28,
        "duplicateOutputRows": 32,
    },
}

FORBIDDEN_DOC_PHRASES = (
    "runtime texture pixels proven",
    "gpu upload parity proven",
    "visual qa complete",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "material/shader parity proven",
    "material visual correctness proven",
    "native textured 3d rendering proven",
    "godot parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def count_files_and_bytes(path: Path) -> tuple[int, int]:
    files = [item for item in path.rglob("*") if item.is_file()]
    return len(files), sum(item.stat().st_size for item in files)


def assert_ledger(report: dict[str, Any], prefix: str, failures: list[str]) -> None:
    require(report.get("schema") == "asset-material-sidecar-ledger.v1", f"{prefix} schema mismatch", failures)
    require(report.get("status") == "PASS", f"{prefix} status mismatch", failures)
    require(report.get("failures") == [], f"{prefix} has failures", failures)
    require(report.get("warnings") == ["embedded mesh export has duplicate-output rows; row coverage remains distinct from unique output-file count"], f"{prefix} warning mismatch", failures)

    source = report.get("sourceArtifacts", {})
    require(source.get("proofRoot") == "subagents/texture_mesh_asset_bridge_proof_2026-06-08", f"{prefix} proof root mismatch", failures)
    require(source.get("modelTextureLinkageSemantics") == "tools/model_texture_linkage_probe.py", f"{prefix} semantics path mismatch", failures)

    counts = report.get("countAnchors", {})
    require(counts.get("archives") == 301, f"{prefix} archive count mismatch", failures)
    require(counts.get("goodieArchives") == 232, f"{prefix} goodie archive count mismatch", failures)
    require(counts.get("topLevelChunks") == EXPECTED_TOP_LEVEL_CHUNKS, f"{prefix} top-level chunk counts mismatch", failures)
    require(counts.get("packedRefs") == EXPECTED_PACKED_REFS, f"{prefix} packed ref counts mismatch", failures)

    exports = report.get("exportLanes", {})
    for lane, expected in EXPECTED_EXPORT_LANES.items():
        actual = exports.get(lane, {})
        for key, value in expected.items():
            require(actual.get(key) == value, f"{prefix} {lane}.{key} mismatch: {actual.get(key)}", failures)

    require(report.get("catalogCoverage") == EXPECTED_CATALOG, f"{prefix} catalog coverage mismatch", failures)

    coverage = report.get("modelCoverage", {})
    for key, expected in EXPECTED_MODEL_COVERAGE.items():
        require(coverage.get(key) == expected, f"{prefix} model coverage mismatch {key}: {coverage.get(key)}", failures)
    kinds = coverage.get("byKind", {})
    for kind, expected in EXPECTED_KIND_COVERAGE.items():
        actual = kinds.get(kind, {})
        for key, value in expected.items():
            require(actual.get(key) == value, f"{prefix} {kind}.{key} mismatch: {actual.get(key)}", failures)

    require(report.get("exportUniqueness") == EXPECTED_EXPORT_UNIQUENESS, f"{prefix} export uniqueness mismatch", failures)

    public_safety = report.get("publicSafety", {})
    for key in ("stripsAbsoluteFbxTexturePaths", "stripsExportFilePaths"):
        require(public_safety.get(key) is True, f"{prefix} public safety should be true: {key}", failures)
    for key in ("embedsPrivateAssets", "launchesGame", "readsOrWritesOriginalExe", "commitsRawAssets"):
        require(public_safety.get(key) is False, f"{prefix} public safety should be false: {key}", failures)

    not_claimed = set(report.get("notClaimed", []))
    for token in (
        "runtime texture pixels",
        "Direct3D or GPU upload behavior",
        "visual QA",
        "material/shader parity",
        "Godot parity",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in not_claimed, f"{prefix} missing non-claim: {token}", failures)


def check_artifacts(failures: list[str]) -> None:
    require(CATALOG.is_file(), f"missing catalog: {relative(CATALOG)}", failures)
    require(LEDGER.is_file(), f"missing material sidecar ledger: {relative(LEDGER)}", failures)
    require(not OLD_LEDGER_ROOT.exists(), f"old copied-corpus proof root ledger directory still exists: {relative(OLD_LEDGER_ROOT)}", failures)

    file_count, byte_count = count_files_and_bytes(BASE)
    require(file_count == EXPECTED_COPIED_ROOT["files"], f"copied proof root file count mismatch: {file_count}", failures)
    require(byte_count == EXPECTED_COPIED_ROOT["bytes"], f"copied proof root byte count mismatch: {byte_count}", failures)

    stored_report = read_json(LEDGER)
    assert_ledger(stored_report, "stored ledger", failures)

    rebuilt_report = ledger_tool.build_ledger(BASE)
    assert_ledger(rebuilt_report, "rebuilt ledger", failures)
    for key in (
        "schema",
        "status",
        "sourceArtifacts",
        "countAnchors",
        "exportLanes",
        "catalogCoverage",
        "modelCoverage",
        "exportUniqueness",
        "publicSafety",
        "claims",
        "notClaimed",
        "warnings",
        "failures",
    ):
        require(rebuilt_report.get(key) == stored_report.get(key), f"rebuilt/stored mismatch {key}", failures)

    linkage_report = linkage.build_report(CATALOG)
    require(linkage_report.get("schema") == "model-texture-linkage.v1", "linkage helper schema mismatch", failures)
    require(linkage_report.get("status") == "PASS", "linkage helper status mismatch", failures)
    require(linkage_report.get("uniqueTextureRefsMissingSidecar") == 0, "linkage helper sidecar gap", failures)
    require(linkage_report.get("uniqueTextureRefsMissingCatalogRows") == 0, "linkage helper catalog gap", failures)

    serialized = json.dumps(stored_report) + json.dumps(rebuilt_report)
    require(ABSOLUTE_USER_SENTINEL not in serialized, "ledger leaks absolute user path", failures)
    require("Program Files" not in serialized, "ledger leaks Program Files path", failures)
    require("asset-full-install-2026-05-07" not in serialized, "ledger points at stale May full-install artifact", failures)
    for token in (
        "stripsAbsoluteFbxTexturePaths",
        "stripsExportFilePaths",
        "embedsPrivateAssets",
        "launchesGame",
        "readsOrWritesOriginalExe",
    ):
        require(token in serialized, f"ledger missing public-safety token: {token}", failures)

    tracked = subprocess.run(
        ["git", "ls-files", "subagents/texture_mesh_material_sidecar_ledger_2026-06-08"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    require(tracked.returncode == 0, "git ls-files failed for material sidecar ledger", failures)
    require(not tracked.stdout.strip(), "ignored material sidecar ledger is tracked", failures)


def check_docs(failures: list[str]) -> None:
    result = read_text(RESULT)
    require(read_text(LORE_RESULT) == result, "lore result mirror mismatch", failures)

    required_result_tokens = (
        "Status: generated material/sidecar ledger proof complete, not runtime proof",
        "not a new static re-audit wave",
        "6411/6411 = 100.00%",
        "0 / 0 / 0",
        "1560/1560 = 100.00%",
        "1179/1179 = 100.00%",
        "Remaining active focused work remains `0`",
        "asset-material-sidecar-ledger.v1",
        "subagents/texture_mesh_material_sidecar_ledger_2026-06-08/asset-material-sidecar-ledger.json",
        "8574",
        "250335133",
        "352/352",
        "1268",
        "213",
        "212",
        "1 stem-only",
        "0` missing sidecar",
        "0` catalog-missing",
        "1` ambiguous catalog ref",
        "loose `213` rows",
        "embedded `139` rows",
        "Embedded mesh duplicate-output caveat",
        "107",
        "28",
        "32",
        "generated material/sidecar ledger proof only",
    )
    for path in (RESULT, READINESS):
        text = read_text(path)
        for token in required_result_tokens:
            require(token in text, f"{relative(path)} missing token: {token}", failures)
        require(ABSOLUTE_USER_SENTINEL not in text, f"{relative(path)} leaks absolute user path", failures)
        require("Program Files" not in text, f"{relative(path)} leaks Program Files path", failures)
        for bad in FORBIDDEN_DOC_PHRASES:
            require(bad not in text.lower(), f"{relative(path)} overclaims: {bad}", failures)

    for path in (COPIED_CORPUS, PLAN, BACKLOG, MAPPED, GAME_ASSETS_INDEX, RE_INDEX):
        text = read_text(path)
        require(RESULT_LINK in text, f"{relative(path)} missing result link", failures)
        require("Material bridge completeness still requires a generated material/sidecar ledger" not in text, f"{relative(path)} still says ledger missing", failures)
        for bad in FORBIDDEN_DOC_PHRASES:
            require(bad not in text.lower(), f"{relative(path)} overclaims: {bad}", failures)


def check_progress_and_package(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total mismatch", failures)
    require(quality["commentedFunctions"] == 6411, "progress commented mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk focused mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:texture-mesh-material-sidecar-ledger") == r"py -3 tools\texture_mesh_material_sidecar_ledger_probe.py --check",
        "missing material sidecar package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_docs(failures)
    check_progress_and_package(failures)

    if failures:
        print("Texture/mesh material sidecar ledger probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Texture/mesh material sidecar ledger probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
