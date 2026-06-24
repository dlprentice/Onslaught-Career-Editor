#!/usr/bin/env python3
"""Validate private-corpus redacted manifest importer-contract adapter materialization proof."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_private_corpus_readonly_inventory_preflight import REQUIRED_ARCHIVE_CLASSES
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter import (
    ADAPTER_CONTRACT_INTERFACES,
    ADAPTER_STATUS,
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_dry_run import (
    DRY_RUN_INTERFACES,
    DRY_RUN_STATUS,
)
from texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization import (
    FALSE_GUARDS,
    MATERIALIZATION_INTERFACES,
    MATERIALIZATION_STATUS,
    NEXT_SCOPE,
    NEXT_SLICE,
    PREVIOUS_SCOPE,
    PREVIOUS_SLICE,
    PROOF_SCHEMA_VERSION,
    PUBLIC_ALLOWED_OUTPUTS,
    REDACTED_FIELDS,
    THIS_SCOPE,
    THIS_SLICE,
    ZERO_COUNTERS,
    build_public_safe_adapter_materialization_proof,
    build_public_safe_adapter_materialization_summary,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization_proof_plan_2026-06-15.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization.py"

SOURCE_DRY_RUN_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan.v1.json"
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
    "raw private corpus manifest consumed",
    "private raw manifest rows consumed",
    "real importer complete",
    "real importer implementation complete",
    "real importer execution complete",
    "private importer dry-run complete",
    "real importer dry-run complete",
    "dry-run succeeded on private corpus assets",
    "all sidecars resolved",
    "asset import complete",
    "private asset import complete",
    "generated asset output complete",
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


def check_result(failures: list[str]) -> None:
    result = read_json(RESULT)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    source_dry_run = read_json(SOURCE_DRY_RUN_RESULT)
    module_summary = build_public_safe_adapter_materialization_summary(source_dry_run)
    module_proof = build_public_safe_adapter_materialization_proof(module_summary)
    require(result == module_proof, "tracked adapter materialization proof differs from module rebuild", failures)

    require(result["schemaVersion"] == PROOF_SCHEMA_VERSION, "proof schema mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["privateCorpusRedactedManifestImporterContractAdapterMaterializationStatus"] == MATERIALIZATION_STATUS, "materialization status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["previousScope"] == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(result["sourceAdapterDryRunStatus"] == DRY_RUN_STATUS, "source dry-run continuity mismatch", failures)
    require(result["sourceAdapterStatus"] == ADAPTER_STATUS, "source adapter continuity mismatch", failures)
    require(result["sourceEvidence"]["sourceProofCount"] == 17, "source proof count mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)

    decision = result["adapterMaterializationDecision"]
    for key in (
        "redactedManifestImporterContractAdapterMaterializationOnly",
        "adapterDryRunProofConsumed",
        "adapterDryRunProofContinuityValidated",
        "adapterMaterializationExecuted",
        "adapterMaterializationInputAccepted",
        "materializedAdapterArtifactWritten",
        "materializedAdapterArtifactStoredInTrackedProof",
        "materializedAdapterRowsGenerated",
        "materializedAdapterRowsValidated",
        "materializedAdapterAggregateCountsValidated",
        "materializationInterfacesValidated",
        "materializedAdapterEmitsOnlyPublicSafeRows",
        "privateEvidenceStoredOutsidePublicReleaseScope",
        "publicPrivateSeparationRequired",
    ):
        require(decision[key] is True, f"decision should be true: {key}", failures)
    for key in (
        "materializedAdapterArtifactPathPublished",
        "privateAssetContentRead",
        "privateArchiveBytesRead",
        "privateManifestMaterialized",
        "privateRawManifestMaterialized",
        "privateRawManifestRowsObserved",
        "privateManifestRowsPublished",
        "rawPrivateManifestConsumed",
        "rawPrivateManifestRowsConsumed",
        "redactedPrivateManifestArtifactPathPublished",
        "ignoredArtifactPathPublished",
        "realImporterImplementation",
        "realImporterExecuted",
        "privateImporterDryRunExecuted",
        "realImporterDryRunExecuted",
        "privateImporterMaterializationExecuted",
        "realImporterMaterializationExecuted",
        "adapterMaterializationReadPrivateInputs",
        "adapterMaterializationPublishedPrivateInput",
        "privateMaterializationArtifactPublished",
        "installedGameMutationAllowed",
        "originalExecutableMutationAllowed",
    ):
        require(decision[key] is False, f"decision should be false: {key}", failures)

    contract = result["adapterMaterializationContract"]
    expected_counts = {
        "sourceAdapterContractInterfaceCount": len(ADAPTER_CONTRACT_INTERFACES),
        "sourceAdapterDryRunInterfaceCount": len(DRY_RUN_INTERFACES),
        "adapterMaterializationInterfaceCount": len(MATERIALIZATION_INTERFACES),
        "materializedAdapterRows": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedAdapterArchiveClassRows": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedAdapterValidationRows": len(REQUIRED_ARCHIVE_CLASSES),
        "materializedAdapterSummaryRows": 1,
        "materializedAdapterArchiveTotalCount": 301,
        "baseArchiveClassCount": 1,
        "frontendArchiveClassCount": 1,
        "loadingArchiveClassCount": 1,
        "numericLevelArchiveClassCount": 66,
        "goodieArchiveClassCount": 232,
        "unknownAyaArchiveClassCount": 0,
        "publicSafeMaterializedAdapterArtifactRows": 1,
    }
    for key, expected in expected_counts.items():
        require(contract[key] == expected, f"materialization count mismatch: {key}", failures)
    require(tuple(contract["sourceAdapterContractInterfaces"]) == ADAPTER_CONTRACT_INTERFACES, "source adapter interfaces mismatch", failures)
    require(tuple(contract["sourceAdapterDryRunInterfaces"]) == DRY_RUN_INTERFACES, "source dry-run interfaces mismatch", failures)
    require(tuple(contract["adapterMaterializationInterfaces"]) == MATERIALIZATION_INTERFACES, "materialization interfaces mismatch", failures)

    artifact = contract["materializedAdapterArtifact"]
    require(artifact["artifactKind"] == "public-safe-redacted-manifest-importer-contract-adapter-materialized-artifact", "artifact kind mismatch", failures)
    require(artifact["artifactRowMode"] == "public-safe-archive-class-count-status-token-only", "artifact row mode mismatch", failures)
    require(artifact["materializationStatus"] == MATERIALIZATION_STATUS, "artifact materialization status mismatch", failures)
    require(artifact["materializedAdapterArtifactPathPublished"] is False, "artifact path should not be published", failures)
    require(artifact["materializedAdapterRows"] == len(REQUIRED_ARCHIVE_CLASSES), "artifact row count mismatch", failures)
    require(artifact["materializedAdapterSummaryRows"] == 1, "artifact summary row count mismatch", failures)
    require(artifact["materializedAdapterArchiveTotalCount"] == 301, "artifact archive total mismatch", failures)
    rows = artifact["materializedAdapterRowsBody"]
    require([row["sourceArchiveClass"] for row in rows] == list(REQUIRED_ARCHIVE_CLASSES), "artifact row order mismatch", failures)
    for row in rows:
        require(row["materializedPrivateIdentifiersPresent"] is False, "artifact row private identifier guard mismatch", failures)
        for key in (
            "rawPathRows",
            "rawFilenameRows",
            "rawStemRows",
            "rawHashRows",
            "byteLengthRows",
            "rawTextureRefRows",
            "rawMeshRefRows",
            "actualAssetImportRows",
            "generatedAssetRows",
            "privateDryRunRows",
            "realImporterDryRunRows",
            "realImporterMaterializationRows",
            "rawDryRunTraceRows",
        ):
            require(row[key] == 0, f"artifact row zero counter mismatch: {key}", failures)

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

    unproven = result["claimBoundary"]["doesNotProve"]
    for token in (
        "private asset content parsing",
        "raw private manifest consumption",
        "real importer implementation",
        "real importer execution",
        "private importer dry run",
        "real importer dry run",
        "adapter materialization consumer validation",
        "actual asset import",
        "generated asset outputs",
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
        "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan.v1.json",
        "tools/texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization.py",
        f"privateCorpusRedactedManifestImporterContractAdapterMaterializationStatus={MATERIALIZATION_STATUS}",
        f"sourceAdapterDryRunStatus={DRY_RUN_STATUS}",
        f"sourceAdapterStatus={ADAPTER_STATUS}",
        "sourceProofCount=17",
        "redactedManifestImporterContractAdapterMaterializationOnly=true",
        "adapterDryRunProofConsumed=true",
        "adapterDryRunProofContinuityValidated=true",
        "adapterMaterializationExecuted=true",
        "adapterMaterializationInputAccepted=true",
        "materializedAdapterArtifactWritten=true",
        "materializedAdapterArtifactStoredInTrackedProof=true",
        "materializedAdapterArtifactPathPublished=false",
        "materializedAdapterRowsGenerated=true",
        "materializedAdapterRowsValidated=true",
        "materializedAdapterAggregateCountsValidated=true",
        "materializationInterfacesValidated=true",
        "materializedAdapterEmitsOnlyPublicSafeRows=true",
        "adapterMaterializationInputMode=tracked-public-safe-adapter-dry-run-proof-json",
        "adapterMaterializationOutputMode=tracked-public-safe-materialized-adapter-artifact",
        "sourceAdapterContractInterfaceCount=7",
        "sourceAdapterDryRunInterfaceCount=8",
        "adapterMaterializationInterfaceCount=8",
        "materializedAdapterRows=5",
        "materializedAdapterArchiveClassRows=5",
        "materializedAdapterValidationRows=5",
        "materializedAdapterSummaryRows=1",
        "materializedAdapterArchiveTotalCount=301",
        "publicSafeMaterializedAdapterArtifactRows=1",
        "publicAllowedOutputCount=11",
        "redactedFieldCount=19",
        "falseGuardCount=56",
        "zeroCounterCount=47",
        "privateAssetContentRead=false",
        "privateArchiveBytesRead=false",
        "privateManifestMaterialized=false",
        "privateRawManifestMaterialized=false",
        "privateRawManifestRowsObserved=false",
        "privateManifestRowsPublished=false",
        "rawPrivateManifestConsumed=false",
        "rawPrivateManifestRowsConsumed=false",
        "redactedPrivateManifestArtifactPathPublished=false",
        "ignoredArtifactPathPublished=false",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "privateImporterDryRunExecuted=false",
        "realImporterDryRunExecuted=false",
        "privateImporterMaterializationExecuted=false",
        "realImporterMaterializationExecuted=false",
        "adapterMaterializationReadPrivateInputs=false",
        "adapterMaterializationPublishedPrivateInput=false",
        "privateMaterializationArtifactPublished=false",
        "installedGameMutationAllowed=false",
        "originalExecutableMutationAllowed=false",
        "rawPathRows=0",
        "rawFilenameRows=0",
        "rawStemRows=0",
        "rawHashRows=0",
        "byteLengthRows=0",
        "rawTextureRefRows=0",
        "rawMeshRefRows=0",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "outputArtifactRows=0",
        "privateArtifactRows=0",
        "privateDryRunRows=0",
        "realImporterDryRunRows=0",
        "realImporterMaterializationRows=0",
        "rawDryRunTraceRows=0",
        "realImporterImplementationRows=0",
        "rebuildImplementationRows=0",
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
        "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan.md",
        "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan.v1.json",
        MATERIALIZATION_STATUS,
        "sourceAdapterDryRunStatus=" + DRY_RUN_STATUS,
        "sourceAdapterStatus=" + ADAPTER_STATUS,
        "adapterMaterializationExecuted=true",
        "materializedAdapterArtifactWritten=true",
        "materializedAdapterArtifactStoredInTrackedProof=true",
        "materializedAdapterArtifactPathPublished=false",
        "materializedAdapterRowsGenerated=true",
        "materializedAdapterRowsValidated=true",
        "materializedAdapterArchiveClassRows=5",
        "materializedAdapterArchiveTotalCount=301",
        "publicSafeMaterializedAdapterArtifactRows=1",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "privateImporterDryRunExecuted=false",
        "realImporterDryRunExecuted=false",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed adapter materialization slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed adapter dry-run slice", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed adapter materialization consumer-validation slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "active block still marks adapter materialization active", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in active, "active block still marks adapter materialization consumer validation active", failures)
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" in active,
        "active block missing real importer dry-run harness checklist readiness gate",
        failures,
    )
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
        scripts.get("test:texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_importer_private_corpus_redacted_manifest_importer_contract_adapter_materialization_proof_plan_probe.py --check",
        "missing package private-corpus redacted manifest importer contract adapter materialization test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "redacted manifest importer contract adapter materialization module missing", failures)
    check_result(failures)
    check_docs(failures)
    check_front_doors_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after redacted manifest importer contract adapter materialization probe", failures)

    if failures:
        print("Texture/mesh material sidecar importer private-corpus redacted manifest importer contract adapter materialization probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar importer private-corpus redacted manifest importer contract adapter materialization probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
