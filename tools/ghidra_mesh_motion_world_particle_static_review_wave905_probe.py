#!/usr/bin/env python3
"""Validate Wave905 mesh/motion/world/particle static-review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave905-mesh-motion-world-particle-static-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BASELINE_JSON = BASE / "mesh-motion-world-particle-baseline.json"
FAMILY_TSV = BASE / "mesh-motion-world-particle-family-summary.tsv"
ANCHORS_TSV = BASE / "mesh-motion-world-particle-function-anchors.tsv"
ASSET_BRIDGE_TSV = BASE / "mesh-motion-world-particle-asset-bridge.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_mesh_motion_world_particle_static_review_wave905_2026-05-26.md"
REVIEW_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-motion-world-particle-static-review-2026-05-26.md"
STATIC_SYSTEM_REVIEW = ROOT / "reverse-engineering" / "binary-analysis" / "static-system-review-2026-05-26.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
EXTRACTION_PIPELINE = ROOT / "reverse-engineering" / "game-assets" / "extraction-pipeline.md"
MESH_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
MESHPART_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshPart.cpp" / "_index.md"
WORLD_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md"
WORLD_PHYSICS_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
PARTICLE_MANAGER_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified"

EXPECTED_FAMILIES = {
    "CThing": 28,
    "CComplexThing": 16,
    "CActor": 11,
    "CRenderThing": 6,
    "CInitThing": 3,
    "CExplosionInitThing": 13,
    "CCSPersistentThing": 2,
    "CMesh": 40,
    "CMeshPart": 54,
    "CMeshRenderer": 4,
    "CMeshCollisionVolume": 21,
    "CNamedMesh": 2,
    "CBuildingNamedMesh": 3,
    "CDXMeshVB": 13,
    "CRTMesh": 7,
    "CPDMesh": 3,
    "CWorld": 38,
    "CWorldPhysicsManager": 32,
    "CWorldMeshList": 3,
    "CDXLandscape": 27,
    "CLandscapeTexture": 16,
    "CHLCollisionDetector": 8,
    "CRoundTreeCollision": 4,
    "CPlane": 9,
    "CSphere": 4,
    "CWaypointPath": 2,
    "CInfluenceMap": 12,
    "CFearGrid": 5,
    "CParticleManager": 23,
    "CParticleSet": 10,
    "CParticleDescriptor": 6,
    "CParticle": 2,
    "DXParticleTexture": 9,
    "ParticleEffectLink": 2,
    "CMotionController": 3,
    "SharedMotionController": 3,
    "SharedUnitAnimation": 2,
    "CAnimation": 4,
    "CDestructableSegmentsMotionController": 6,
    "CBattleEngineWalkerPart": 27,
    "CBattleEngineJetPart": 23,
}

EXPECTED_ASSET_METRICS = {
    "resourceArchives": "301",
    "goodieResourceArchives": "232",
    "looseMeshesExported": "213/213",
    "embeddedMeshesExported": "139/139",
    "meshRefsResolved": "209/209",
    "gdieMeshRefsResolved": "42/42",
    "modelRows": "352",
    "modelRowsWithReadableMaterials": "352/352",
    "modelRowsWithTextureBindings": "352/352",
    "modelRowsWithCatalogResolvedTextureBinding": "352/352",
    "modelTextureSidecarRefs": "213/213",
}

REQUIRED_ANCHORS = {
    "CThing__InitRenderThingFromInitMeshName",
    "CThing__Render",
    "CComplexThing__Init",
    "CActor__GetRenderPos",
    "CMesh__LoadByNameWithStatus",
    "CMeshPart__PopulatePoseCacheRecursive",
    "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart",
    "CMeshRenderer__RenderMesh",
    "CDXMeshVB__BuildSkeletalVB",
    "CWorld__InitOccupancyBitplanes",
    "CWorldPhysicsManager__CreateThingByType",
    "CParticleManager__Update",
    "CParticleSet__LoadFromArchive",
    "CParticleDescriptor__Load",
    "DXParticleTexture__Render",
    "CBattleEngineWalkerPart__Move",
    "CBattleEngineJetPart__Thrust",
}

CORE_ANCHORS = (
    "Wave905",
    "mesh-motion-world-particle-static-review-wave905",
    "static-coherent mesh/motion/world/particle core",
    "6113/6113 = 100.00%",
    "506",
    "41",
    "CMeshPart",
    "54",
    "CMesh",
    "40",
    "CWorld",
    "38",
    "CWorldPhysicsManager",
    "32",
    "CThing",
    "28",
    "CParticleManager",
    "23",
    "CMeshCollisionVolume",
    "21",
    "CThing__InitRenderThingFromInitMeshName",
    "CMesh__LoadByNameWithStatus",
    "CMeshPart__PopulatePoseCacheRecursive",
    "CWorld__InitOccupancyBitplanes",
    "CWorldPhysicsManager__CreateThingByType",
    "CParticleManager__Update",
    "CParticleSet__LoadFromArchive",
    "CParticleDescriptor__Load",
    "213/213",
    "139/139",
    "352/352",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime collision behavior proven",
    "runtime physics behavior proven",
    "runtime particle behavior proven",
    "runtime mesh visual parity proven",
    "all object layouts proven",
    "all systems complete",
    "every system is complete",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6113, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name, entries in queue.get("priorityQueues", {}).items():
        require(entries == [], f"priority queue not empty: {name}", failures)


def check_evidence(failures: list[str]) -> None:
    baseline = read_json(BASELINE_JSON)
    require(baseline.get("wave") == 905, "baseline wave mismatch", failures)
    require(baseline.get("tag") == "mesh-motion-world-particle-static-review-wave905", "baseline tag mismatch", failures)
    require(baseline.get("classification") == "static-coherent mesh/motion/world/particle core", "baseline classification mismatch", failures)
    require(baseline.get("selectedFamilyCount") == 41, "baseline family count mismatch", failures)
    require(baseline.get("selectedFunctionRows") == 506, "baseline function count mismatch", failures)
    require(baseline.get("commentedRows") == 506, "baseline commented count mismatch", failures)
    require(baseline.get("cleanSignatureRows") == 506, "baseline clean-signature count mismatch", failures)
    require(baseline.get("missingAnchors") == [], "baseline missing anchors", failures)

    families = {row["family"]: int(row["rows"]) for row in read_tsv(FAMILY_TSV)}
    require(families == EXPECTED_FAMILIES, "family summary mismatch", failures)

    assets = {row["metric"]: row["value"] for row in read_tsv(ASSET_BRIDGE_TSV)}
    for metric, expected in EXPECTED_ASSET_METRICS.items():
        require(assets.get(metric) == expected, f"asset metric mismatch: {metric}", failures)

    anchors = read_tsv(ANCHORS_TSV)
    require(len(anchors) == 506, "anchor row count mismatch", failures)
    names = {row["name"] for row in anchors}
    for name in REQUIRED_ANCHORS:
        require(name in names, f"missing anchor: {name}", failures)
    for row in anchors:
        signature = row.get("signature", "")
        require(row.get("comment", "").strip() != "", f"anchor missing comment: {row.get('name')}", failures)
        require(not signature.startswith("undefined "), f"anchor undefined signature: {row.get('name')}", failures)
        require(re.search(r"\bparam_\d+\b", signature) is None, f"anchor param_N signature: {row.get('name')}", failures)
        require(row.get("status") == "OK", f"anchor status mismatch: {row.get('name')}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173247367, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = (
        PUBLIC_NOTE,
        REVIEW_DOC,
        STATIC_SYSTEM_REVIEW,
        MAPPED_SYSTEMS,
        BINARY_INDEX,
        GAME_ASSETS_INDEX,
        EXTRACTION_PIPELINE,
        MESH_INDEX,
        MESHPART_INDEX,
        WORLD_INDEX,
        WORLD_PHYSICS_INDEX,
        PARTICLE_MANAGER_INDEX,
        RE_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-mesh-motion-world-particle-static-review-wave905")
        == r"py -3 tools\ghidra_mesh_motion_world_particle_static_review_wave905_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_queue(failures)
    check_evidence(failures)
    check_docs(failures)

    if failures:
        print("Wave905 mesh/motion/world/particle static-review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave905 mesh/motion/world/particle static-review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
