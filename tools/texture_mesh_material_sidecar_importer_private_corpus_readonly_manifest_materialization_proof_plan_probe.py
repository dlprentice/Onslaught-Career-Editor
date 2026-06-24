#!/usr/bin/env python3
"""Validate private-corpus read-only manifest materialization proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight import (
    REQUIRED_ARCHIVE_CLASSES,
    RedactedInventoryCounts,
)
from texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_dry_run import (
    DRY_RUN_STATUS,
    build_public_safe_manifest_dry_run_summary,
)
from texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_materialization import (
    FALSE_GUARDS,
    MATERIALIZATION_STATUS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REDACTED_FIELDS,
    SCHEMA_VERSION as MODULE_SCHEMA_VERSION,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_manifest_materialization_proof,
    build_public_safe_manifest_materialization_summary,
    validate_public_safe_manifest_materialization_summary,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_read_only_manifest_materialization_proof_plan_2026-06-10.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_materialization.py"

SOURCE_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan.v1.json"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"

BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
LORE_MAPPED = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BIN_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
LORE_RE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "RE-INDEX.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
LORE_GAME_ASSETS_INDEX = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
ADAPTER_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan"
ADAPTER_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan"

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)subagents[\\/]"), "ignored artifact path"),
    (re.compile(r"(?i)\bgame[\\/]"), "private game mirror path"),
    (re.compile(r"(?i)\bmedia[\\/]"), "private media path"),
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)textureRefSample|sampleRows|canonical_ref|canonicalRef|fbxTexturePath|exportFilePath"), "row-level private sample field"),
    (re.compile(r"(?i)asset-material-sidecar-ledger\.json|catalog\.json"), "raw generated artifact name"),
    (re.compile(r"(?i)hwnd"), "window identifier"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framehash|framesha256|framebytelength"), "private frame locator/hash field"),
    (re.compile(r"(?i)\.private\.png"), "private frame filename"),
    (re.compile(r"(?i)save-attempts"), "private save path"),
    (re.compile(r"(?i)onslaught_codex_directive"), "operator directive marker"),
    (re.compile(r"(?i)password|token="), "secret-like marker"),
)

FORBIDDEN_OVERCLAIMS = (
    "private asset content parsed",
    "raw private corpus manifest materialized",
    "private raw manifest rows observed",
    "real importer complete",
    "real importer implementation complete",
    "real importer execution complete",
    "dry-run succeeded on private corpus assets",
    "all sidecars resolved",
    "asset import complete",
    "private asset import complete",
    "runtime resource archive parser behavior proven",
    "runtime texture parser behavior proven",
    "runtime texture pixels proven",
    "runtime mesh loading proven",
    "runtime mesh skinning proven",
    "runtime direct3d upload proven",
    "gpu behavior proven",
    "native textured 3d rendering proven",
    "material visual correctness proven",
    "material/shader parity proven",
    "asset format completeness proven",
    "visual qa complete",
    "godot parity proven",
    "rebuild implementation complete",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
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


def no_bea_process_running() -> bool:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "if (Get-Process -Name BEA -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def active_slice_block(text: str) -> str:
    marker = "## Active Proof Slice"
    start = text.find(marker)
    if start < 0:
        return ""
    next_heading = text.find("\n## ", start + len(marker))
    return text[start:] if next_heading < 0 else text[start:next_heading]


def check_no_bad_public_content(path: Path, failures: list[str]) -> None:
    text = read_text(path)
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{path.relative_to(ROOT)} leaks forbidden public category: {category}", failures)
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{path.relative_to(ROOT)} overclaims forbidden category: {phrase}", failures)


def observed_counts_from_result(result: dict[str, Any]) -> RedactedInventoryCounts:
    summary = result["archiveClassSummary"]
    return RedactedInventoryCounts(
        resource_root_exists=summary["resourceRootExists"],
        resource_directory_exists=summary["resourceDirectoryExists"],
        aya_archive_total_count=summary["ayaArchiveTotalCount"],
        base_archive_class_count=summary["baseArchiveClassCount"],
        frontend_archive_class_count=summary["frontendArchiveClassCount"],
        loading_archive_class_count=summary["loadingArchiveClassCount"],
        numeric_level_archive_class_count=summary["numericLevelArchiveClassCount"],
        goodie_archive_class_count=summary["goodieArchiveClassCount"],
        unknown_aya_archive_class_count=summary["unknownAyaArchiveClassCount"],
    )


def check_source(failures: list[str]) -> None:
    source = read_json(SOURCE_RESULT)
    require(source["status"] == "PASS", "source dry-run status mismatch", failures)
    require(source["privateCorpusReadOnlyManifestDryRunStatus"] == DRY_RUN_STATUS, "source dry-run token mismatch", failures)
    require(source["selectedNextSlice"] == THIS_SLICE, "source selected next slice mismatch", failures)
    require(source["selectedNextScope"] == THIS_SCOPE, "source selected next scope mismatch", failures)
    decision = source["readOnlyManifestDecision"]
    require(decision["privateCorpusReadOnlyManifestDryRunExecuted"] is True, "source dry-run not executed", failures)
    require(decision["privateAssetContentRead"] is False, "source should not read private content", failures)
    require(decision["privateManifestMaterialized"] is False, "source should not materialize manifest", failures)
    require(decision["realImporterExecuted"] is False, "source should not execute importer", failures)


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    require(result["schemaVersion"] == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["privateCorpusReadOnlyManifestMaterializationStatus"] == MATERIALIZATION_STATUS, "materialization token mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["previousScope"] == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(result["sourceDryRunStatus"] == DRY_RUN_STATUS, "source dry-run continuity mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)
    require(result["sourceEvidence"]["sourceProofCount"] == 12, "source proof count mismatch", failures)

    decision = result["materializationDecision"]
    for key in (
        "readOnlyManifestMaterializationOnly",
        "privateCorpusReadOnlyManifestMaterializationExecuted",
        "sourceDryRunEvidenceConsumed",
        "redactedPrivateManifestMaterialized",
        "redactedPrivateManifestArtifactWritten",
        "redactedPrivateManifestArtifactStoredOutsidePublicReleaseScope",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision[key] is True, f"decision should be true: {key}", failures)
    for key in (
        "redactedPrivateManifestArtifactPathPublished",
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "privateManifestMaterialized",
        "privateRawManifestMaterialized",
        "privateRawManifestRowsObserved",
        "privateManifestRowsPublished",
        "realImporterImplementation",
        "realImporterExecuted",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        require(decision[key] is False, f"decision should be false: {key}", failures)

    archive = result["archiveClassSummary"]
    expected_archive = {
        "sourceRootClass": "user-owned-installed-or-copied-game-resource-root",
        "resourceRootExists": True,
        "resourceDirectoryExists": True,
        "requiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "observedRequiredArchiveClassCount": len(REQUIRED_ARCHIVE_CLASSES),
        "allRequiredArchiveClassesObserved": True,
        "ayaArchiveTotalCount": 301,
        "baseArchiveClassCount": 1,
        "frontendArchiveClassCount": 1,
        "loadingArchiveClassCount": 1,
        "numericLevelArchiveClassCount": 66,
        "goodieArchiveClassCount": 232,
        "unknownAyaArchiveClassCount": 0,
    }
    for key, expected in expected_archive.items():
        require(archive[key] == expected, f"archive summary mismatch: {key}", failures)

    materialized = result["redactedMaterializedManifest"]
    require(materialized["manifestKind"] == "redacted-private-corpus-class-count-manifest", "manifest kind mismatch", failures)
    require(materialized["manifestRowMode"] == "class-count-status-token-only", "manifest row mode mismatch", failures)
    require(materialized["redactedPrivateManifestRows"] == len(REQUIRED_ARCHIVE_CLASSES), "redacted manifest rows mismatch", failures)
    require(materialized["redactedPrivateManifestSummaryRows"] == 1, "redacted manifest summary rows mismatch", failures)
    require(materialized["redactedPrivateManifestArtifactPathPublished"] is False, "manifest path should not be published", failures)
    require(materialized["publicSafeRedactedManifestArtifactRows"] == 1, "public-safe artifact row count mismatch", failures)
    require(materialized["materializedRedactedManifestClassRowCount"] == len(REQUIRED_ARCHIVE_CLASSES), "materialized class rows mismatch", failures)
    require(materialized["materializedRedactedManifestArchiveTotalCount"] == 301, "materialized archive total mismatch", failures)
    rows = materialized["redactedManifestClassRows"]
    require([row["archiveClass"] for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "manifest archive class order mismatch", failures)
    for row in rows:
        require(row["manifestRowMode"] == "class-count-status-token-only", "manifest row mode mismatch", failures)
        require(row["privateAssetContentRead"] is False, "row content-read guard mismatch", failures)
        require(row["privateArchiveBytesRead"] is False, "row archive-read guard mismatch", failures)
        for key in ("rawPathRows", "rawFilenameRows", "rawTextureRefRows", "rawMeshRefRows", "byteLengthRows"):
            require(row[key] == 0, f"row zero counter mismatch: {key}", failures)

    redaction = result["redactionPolicy"]
    require(redaction["publicAllowedOutputCount"] == len(PUBLIC_ALLOWED_OUTPUTS), "public output count mismatch", failures)
    require(redaction["redactedFieldCount"] == len(REDACTED_FIELDS), "redacted field count mismatch", failures)
    require(tuple(redaction["publicAllowedOutputs"]) == PUBLIC_ALLOWED_OUTPUTS, "public outputs mismatch", failures)
    require(tuple(redaction["redactedFields"]) == REDACTED_FIELDS, "redacted fields mismatch", failures)
    require(redaction["publicLeakCheck"] == "PASS", "redaction public leak check mismatch", failures)

    guard = result["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    for key in ZERO_COUNTERS:
        require(guard[key] == 0, f"zero counter mismatch: {key}", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard public leak check mismatch", failures)

    dry_run_summary = build_public_safe_manifest_dry_run_summary(observed_counts_from_result(result))
    module_summary = build_public_safe_manifest_materialization_summary(dry_run_summary)
    validate_public_safe_manifest_materialization_summary(module_summary)
    module_proof = build_public_safe_manifest_materialization_proof(module_summary)
    require(module_summary["schemaVersion"] == MODULE_SCHEMA_VERSION, "module schema mismatch", failures)
    for key in (
        "status",
        "privateCorpusReadOnlyManifestMaterializationStatus",
        "selectedNextSlice",
        "selectedNextScope",
        "sourceDryRunStatus",
    ):
        require(result.get(key) == module_proof.get(key), f"module proof mismatch: {key}", failures)
    require(materialized["redactedManifestClassRows"] == module_proof["redactedMaterializedManifest"]["redactedManifestClassRows"], "module materialized rows mismatch", failures)
    require(redaction["publicLeakCheck"] == module_proof["redactionPolicy"]["publicLeakCheck"], "module public leak check mismatch", failures)

    proves = result["claimBoundary"]["proves"]
    unproven = result["claimBoundary"]["doesNotProve"]
    require("the selected read-only manifest materialization wrote a redacted private manifest artifact outside public release scope" in proves, "claim boundary missing materialization proof", failures)
    require("private raw manifest materialization, private manifest row observation, real importer implementation, and real importer execution remain unperformed" in proves, "claim boundary missing non-proof", failures)
    for token in (
        "private asset content parsing",
        "private raw corpus manifest materialization",
        "private raw manifest row observation",
        "real importer implementation",
        "real importer execution",
        "runtime texture parser behavior",
        "runtime texture pixels",
        "runtime mesh loading or skinning",
        "Godot parity",
        "rebuild parity",
        "no-noticeable-difference parity",
    ):
        require(token in unproven, f"claim boundary missing unproven token: {token}", failures)
    check_no_bad_public_content(RESULT, failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(LORE_PROOF) == read_text(PROOF), "lore proof mirror mismatch", failures)
    common_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        PREVIOUS_SCOPE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.v1.json",
        "tools/texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_materialization.py",
        f"privateCorpusReadOnlyManifestMaterializationStatus={MATERIALIZATION_STATUS}",
        f"sourceDryRunStatus={DRY_RUN_STATUS}",
        "sourceProofCount=12",
        "readOnlyManifestMaterializationOnly=true",
        "privateCorpusReadOnlyManifestMaterializationExecuted=true",
        "sourceDryRunEvidenceConsumed=true",
        "redactedPrivateManifestMaterialized=true",
        "redactedPrivateManifestArtifactWritten=true",
        "redactedPrivateManifestArtifactStoredOutsidePublicReleaseScope=true",
        "redactedPrivateManifestArtifactPathPublished=false",
        "privateEvidenceStoredOutsidePublicReleaseScope=true",
        "privateAssetContentRead=false",
        "privateArchiveBytesRead=false",
        "privateManifestMaterialized=false",
        "privateRawManifestMaterialized=false",
        "privateRawManifestRowsObserved=false",
        "privateManifestRowsPublished=false",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "installedGameMutationAllowed=false",
        "originalExecutableMutationAllowed=false",
        "sourceRootClass=user-owned-installed-or-copied-game-resource-root",
        "resourceRootExists=true",
        "resourceDirectoryExists=true",
        "requiredArchiveClassCount=5",
        "observedRequiredArchiveClassCount=5",
        "allRequiredArchiveClassesObserved=true",
        "ayaArchiveTotalCount=301",
        "baseArchiveClassCount=1",
        "frontendArchiveClassCount=1",
        "loadingArchiveClassCount=1",
        "numericLevelArchiveClassCount=66",
        "goodieArchiveClassCount=232",
        "unknownAyaArchiveClassCount=0",
        "sourceManifestDryRunClassRowCount=5",
        "materializedRedactedManifestClassRowCount=5",
        "materializedRedactedManifestArchiveTotalCount=301",
        "redactedPrivateManifestRows=5",
        "redactedPrivateManifestSummaryRows=1",
        "publicSafeRedactedManifestArtifactRows=1",
        "publicAllowedOutputCount=10",
        "redactedFieldCount=15",
        "falseGuardCount=40",
        "zeroCounterCount=35",
        "outputArtifactRows=0",
        "privateArtifactRows=0",
        "privateManifestRows=0",
        "rawPrivateManifestRows=0",
        "rawPathRows=0",
        "rawFilenameRows=0",
        "rawStemRows=0",
        "rawHashRows=0",
        "byteLengthRows=0",
        "rawTextureRefRows=0",
        "rawMeshRefRows=0",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "publicLeakCheck=PASS",
    )
    for path in (PROOF, READINESS):
        text = read_text(path)
        for token in common_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing token: {token}", failures)
        check_no_bad_public_content(path, failures)


def check_front_doors_and_package(failures: list[str]) -> None:
    front_tokens = (
        THIS_SLICE,
        THIS_SCOPE,
        PREVIOUS_SLICE,
        NEXT_SLICE,
        NEXT_SCOPE,
        "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.md",
        "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.v1.json",
        MATERIALIZATION_STATUS,
        "sourceDryRunStatus=" + DRY_RUN_STATUS,
        "privateCorpusReadOnlyManifestMaterializationExecuted=true",
        "redactedPrivateManifestMaterialized=true",
        "redactedPrivateManifestArtifactWritten=true",
        "redactedPrivateManifestArtifactStoredOutsidePublicReleaseScope=true",
        "redactedPrivateManifestArtifactPathPublished=false",
        "privateManifestMaterialized=false",
        "privateRawManifestRowsObserved=false",
        "publicSafeRedactedManifestArtifactRows=1",
        "allRequiredArchiveClassesObserved=true",
        "ayaArchiveTotalCount=301",
        "materializedRedactedManifestClassRowCount=5",
        "materializedRedactedManifestArchiveTotalCount=301",
        "outputArtifactRows=0",
        "rawPathRows=0",
        "rawFilenameRows=0",
        "rawHashRows=0",
        "byteLengthRows=0",
        "publicLeakCheck=PASS",
    )
    for path in (BACKLOG, MAPPED, BIN_INDEX, RE_INDEX, GAME_ASSETS_INDEX):
        text = read_text(path)
        for token in front_tokens:
            require(token in text, f"{path.relative_to(ROOT)} missing front-door token: {token}", failures)

    for source, mirror in (
        (BACKLOG, LORE_BACKLOG),
        (MAPPED, LORE_MAPPED),
        (BIN_INDEX, LORE_BIN_INDEX),
        (RE_INDEX, LORE_RE_INDEX),
        (GAME_ASSETS_INDEX, LORE_GAME_ASSETS_INDEX),
    ):
        require(read_text(source) == read_text(mirror), f"lore mirror mismatch for {source.relative_to(ROOT)}", failures)

    backlog = read_text(BACKLOG)
    active = active_slice_block(backlog)
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed read-only manifest materialization slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed read-only manifest dry-run slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "active block still marks manifest materialization active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed read-only manifest consumer validation", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in active, "active block still marks read-only manifest consumer validation active", failures)
    require(f"Completed {ADAPTER_SLICE}" in backlog, "backlog missing completed redacted manifest importer contract adapter", failures)
    require(f"The selected active static-to-proof slice is {ADAPTER_SLICE}. Status: selected" not in active, "active block still marks redacted manifest importer contract adapter active", failures)
    require(f"Completed {ADAPTER_DRY_RUN_SLICE}" in backlog, "backlog missing completed redacted manifest importer contract adapter dry-run", failures)
    require(f"The selected active static-to-proof slice is {ADAPTER_DRY_RUN_SLICE}. Status: selected" not in active, "active block still marks redacted manifest importer contract adapter dry-run active", failures)
    require("The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" in active, "active block missing private corpus real importer dry-run harness checklist population", failures)
    require(active.count("The selected active static-to-proof slice is ") == 1, "active block should have exactly one active slice sentence", failures)

    progress = read_json(PROGRESS)
    quality = progress["functionQuality"]
    require(quality["totalFunctions"] == 6411, "progress total mismatch", failures)
    require(quality["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(quality["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(quality["paramSignatures"] == 0, "progress param_N mismatch", failures)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk reviewed mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_materialization_proof_plan_probe.py --check",
        "missing package private-corpus read-only manifest materialization test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "read-only manifest materialization module missing", failures)
    check_source(failures)
    check_result(failures)
    check_docs(failures)
    check_front_doors_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after read-only manifest materialization probe", failures)

    if failures:
        print("Texture/mesh material sidecar importer private-corpus read-only manifest materialization probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar importer private-corpus read-only manifest materialization probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
