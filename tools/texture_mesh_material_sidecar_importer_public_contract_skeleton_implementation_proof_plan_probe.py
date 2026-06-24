#!/usr/bin/env python3
"""Validate texture/mesh material-sidecar importer public contract skeleton."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from texture_mesh_material_sidecar_importer_public_contract_skeleton import (
    CONTRACT_STATUS,
    CONTRACT_VERSION,
    EXPECTED_AGGREGATES,
    EXPECTED_EDGE_CASE_IDS,
    EXPECTED_ROW_IDS,
    FALSE_GUARDS,
    PUBLIC_CONTRACT_FUNCTIONS,
    REQUIRED_PUBLIC_INTERFACES,
    SOURCE_STATUS,
    VALIDATION_SCHEMA,
    ZERO_COUNTERS,
    emit_public_validation_summary,
)


ROOT = Path(__file__).resolve().parents[1]

PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.md"
RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.v1.json"
LORE_PROOF = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.md"
LORE_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.v1.json"
READINESS = ROOT / "release" / "readiness" / "texture_mesh_material_sidecar_importer_public_contract_skeleton_implementation_proof_plan_2026-06-10.md"
MODULE = ROOT / "tools" / "texture_mesh_material_sidecar_importer_public_contract_skeleton.py"

SOURCE_PROOF = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md"
SOURCE_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.v1.json"
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

THIS_SLICE = "Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan"
THIS_SCOPE = "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan"
PREVIOUS_SLICE = "Texture / Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan"
PREVIOUS_SCOPE = "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan"
NEXT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan"
NEXT_SCOPE = "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan"
FOLLOWUP_PRIVATE_CHECKLIST_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan"
FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan"
FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE = "Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan"

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)g:[\\/]"), "private backup path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)subagents[\\/]"), "ignored artifact path"),
    (re.compile(r"(?i)\bgame[\\/]"), "private game mirror path"),
    (re.compile(r"(?i)\bmedia[\\/]"), "private media path"),
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
    "real importer implementation complete",
    "real importer execution complete",
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


def check_source_readiness(failures: list[str]) -> dict[str, Any]:
    source = read_json(SOURCE_RESULT)
    require(source["status"] == "PASS", "source readiness status mismatch", failures)
    require(source["implementationReadinessStatus"] == SOURCE_STATUS, "source readiness token mismatch", failures)
    require(source["selectedNextSlice"] == THIS_SLICE, "source selected next slice mismatch", failures)
    require(source["selectedNextScope"] == THIS_SCOPE, "source selected next scope mismatch", failures)

    decision = source["readinessDecision"]
    require(decision["implementationReadinessGateComplete"] is True, "source readiness gate not complete", failures)
    require(decision["publicContractSkeletonReadyNow"] is True, "source public skeleton not ready", failures)
    require(decision["realImporterImplementationReadyNow"] is False, "source real importer implementation ready", failures)
    require(decision["realImporterExecutionReadyNow"] is False, "source real importer execution ready", failures)
    require(decision["implementationDeferred"] is True, "source implementation not deferred", failures)

    summary = source["readinessSummary"]
    for key, expected in EXPECTED_AGGREGATES.items():
        require(summary[key] == expected, f"source readiness aggregate mismatch: {key}", failures)
    require(tuple(source["consumedFixtureRows"]) == EXPECTED_ROW_IDS, "source consumed fixture rows mismatch", failures)
    require(tuple(row["interfaceId"] for row in source["requiredPublicContractInterfaces"]) == REQUIRED_PUBLIC_INTERFACES, "source public interface ids mismatch", failures)
    require(tuple(row["caseId"] for row in source["publicEdgeCases"]) == EXPECTED_EDGE_CASE_IDS, "source public edge case ids mismatch", failures)
    return source


def check_result(source: dict[str, Any], failures: list[str]) -> None:
    result = read_json(RESULT)
    require(read_json(LORE_RESULT) == result, "lore result mirror mismatch", failures)
    require(result["schemaVersion"] == "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.v1", "schema version mismatch", failures)
    require(result["status"] == "PASS", "result status mismatch", failures)
    require(result["publicContractSkeletonStatus"] == CONTRACT_STATUS, "public skeleton status mismatch", failures)
    require(result["previousSlice"] == PREVIOUS_SLICE, "previous slice mismatch", failures)
    require(result["previousScope"] == PREVIOUS_SCOPE, "previous scope mismatch", failures)
    require(result["selectedNextSlice"] == NEXT_SLICE, "selected next slice mismatch", failures)
    require(result["selectedNextScope"] == NEXT_SCOPE, "selected next scope mismatch", failures)
    require(result["sourceImplementationReadinessStatus"] == SOURCE_STATUS, "source readiness status mismatch", failures)

    static = result["staticContext"]
    require(static["staticFunctionQuality"] == "6411/6411 = 100.00%", "static quality mismatch", failures)
    require(static["staticDebt"] == "0 / 0 / 0", "static debt mismatch", failures)
    require(static["expandedStaticSurface"] == "1560/1560 = 100.00%", "expanded static mismatch", failures)
    require(static["currentRiskFocused"] == "1179/1179 = 100.00%", "current-risk mismatch", failures)
    require(static["remainingActiveFocusedWork"] == 0, "remaining focused mismatch", failures)

    require(result["sourceEvidence"]["sourceProofCount"] == 7, "source proof count mismatch", failures)
    decision = result["skeletonDecision"]
    for key, expected in {
        "publicContractSkeletonImplemented": True,
        "contractSkeletonValidationExecuted": True,
        "readsOnlyTrackedPublicSchema": True,
        "emitsOnlyValidationSummary": True,
        "realImporterImplementation": False,
        "realImporterExecuted": False,
        "importerImplementation": False,
        "importerExecuted": False,
        "realImporterImplementationReadyNow": False,
        "realImporterExecutionReadyNow": False,
        "implementationDeferred": True,
        "explicitImporterImplementationArmPresent": False,
        "privateAssetReadAuthorizationPresent": False,
        "operatorPrivateOutputReviewAvailable": False,
        "selectedNextImplementationSliceCount": 1,
    }.items():
        require(decision[key] == expected, f"skeleton decision mismatch: {key}", failures)

    skeleton = result["publicContractSkeleton"]
    for key, expected in {
        "contractVersion": CONTRACT_VERSION,
        "validationSchema": VALIDATION_SCHEMA,
        "contractInterfaceCount": 6,
        "implementedContractInterfaceCount": 6,
        "contractFunctionCount": 2,
        "publicContractSkeletonImplementationRows": 1,
        "validationSummaryRows": 1,
        "skeletonContractCheckCount": 46,
        "failedSkeletonContractChecks": 0,
        "allowedInputMode": "tracked-public-sanitized-readiness-gate-schema",
        "allowedOutputMode": "public-contract-skeleton-validation-summary-only",
    }.items():
        require(skeleton[key] == expected, f"skeleton counter mismatch: {key}", failures)

    require(tuple(row["interfaceId"] for row in result["publicContractInterfaces"]) == REQUIRED_PUBLIC_INTERFACES, "result interface ids mismatch", failures)
    require(all(row["implemented"] is True for row in result["publicContractInterfaces"]), "result interface implemented flag mismatch", failures)
    require(tuple(result["publicContractFunctions"]) == PUBLIC_CONTRACT_FUNCTIONS, "contract function names mismatch", failures)
    require(tuple(result["consumedFixtureRows"]) == EXPECTED_ROW_IDS, "result consumed fixture rows mismatch", failures)

    counters = result["aggregateCounters"]
    for key, expected in EXPECTED_AGGREGATES.items():
        mapped_key = {
            "sourceConsumedFixtureRowCount": "sourceConsumedFixtureRowCount",
            "sourceConsumerDryRunStepCount": "sourceConsumerDryRunStepCount",
            "sourceConsumerAssertionGroupCount": "sourceConsumerAssertionGroupCount",
            "sourceConsumerAssertionCheckCount": "sourceConsumerAssertionCheckCount",
            "sourceFailedConsumerAssertions": "sourceFailedConsumerAssertions",
            "sourceUnexpectedFixtureRows": "sourceUnexpectedFixtureRows",
            "sourceConsumerOutputArtifactRows": "sourceConsumerOutputArtifactRows",
            "readinessGateCount": "sourceReadinessGateCount",
            "readinessCheckCount": "sourceReadinessCheckCount",
            "failedReadinessGateCount": "sourceFailedReadinessGateCount",
            "blockedReadinessGateCount": "sourceBlockedReadinessGateCount",
        }.get(key, key)
        require(counters[mapped_key] == expected, f"aggregate counter mismatch: {mapped_key}", failures)
    require(counters["sourceReadinessGateCount"] == 8, "source readiness gate count mismatch", failures)
    require(counters["sourceReadinessCheckCount"] == 16, "source readiness check count mismatch", failures)
    require(counters["sourceFailedReadinessGateCount"] == 0, "source readiness failed count mismatch", failures)
    require(counters["sourceBlockedReadinessGateCount"] == 0, "source readiness blocked count mismatch", failures)

    expressions = {row["checkId"]: row["expression"] for row in result["arithmeticChecks"]}
    require(expressions["row-sum-arithmetic"] == "213 + 139 = 352", "row arithmetic mismatch", failures)
    require(expressions["ref-instance-arithmetic"] == "602 + 666 = 1268", "ref arithmetic mismatch", failures)
    require(expressions["family-unique-ref-sum"] == "213 + 28 = 241", "family unique arithmetic mismatch", failures)
    require(expressions["unique-ref-union-non-additive"] == "uniqueModelTextureRefUnion = 213", "union arithmetic mismatch", failures)
    require(expressions["sidecar-match-mode-boundary"] == "212 + 1 = 213", "sidecar arithmetic mismatch", failures)
    require(expressions["embedded-duplicate-output-surplus"] == "139 - 107 = 32", "duplicate surplus arithmetic mismatch", failures)

    edge_ids = tuple(row["caseId"] for row in result["publicEdgeCases"])
    require(edge_ids == EXPECTED_EDGE_CASE_IDS, "result public edge case ids mismatch", failures)
    for row in result["publicEdgeCases"]:
        require(row["count"] == 1, f"public edge case count mismatch: {row['caseId']}", failures)
        for key in ("rawRefPublished", "rawStemPublished", "catalogVariantPublished", "filenamePublished", "pathPublished", "hashPublished"):
            require(row[key] is False, f"public edge publishes forbidden field {key}: {row['caseId']}", failures)

    module_summary = emit_public_validation_summary(source)
    require(result["validationSummary"] == module_summary, "module validation summary mismatch", failures)

    guard = result["guardSummary"]
    require(guard["falseGuardCount"] == len(FALSE_GUARDS), "false guard count mismatch", failures)
    require(guard["zeroCounterCount"] == len(ZERO_COUNTERS), "zero counter count mismatch", failures)
    require(guard["publicLeakCheck"] == "PASS", "guard leak check mismatch", failures)
    for key in FALSE_GUARDS:
        require(guard["falseGuards"][key] is False, f"false guard mismatch: {key}", failures)
    for key in ZERO_COUNTERS:
        require(guard["zeroCounters"][key] == 0, f"zero counter mismatch: {key}", failures)

    require("the public importer contract skeleton exists as a small Python module" in result["claimBoundary"]["proves"], "claim boundary missing skeleton proof", failures)
    require("real importer implementation" in result["claimBoundary"]["doesNotProve"], "claim boundary missing real importer non-proof", failures)
    require("rebuild parity" in result["claimBoundary"]["doesNotProve"], "claim boundary missing rebuild parity non-proof", failures)
    require("no-noticeable-difference parity" in result["claimBoundary"]["doesNotProve"], "claim boundary missing no-noticeable-difference non-proof", failures)
    require(len(result["contractAssertions"]) == 10, "contract assertion count mismatch", failures)
    require(all(row["status"] == "PASS" for row in result["contractAssertions"]), "contract assertion status mismatch", failures)
    require(len(result["stopConditions"]) == 7, "stop condition count mismatch", failures)
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
        "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.v1.json",
        "tools/texture_mesh_material_sidecar_importer_public_contract_skeleton.py",
        f"publicContractSkeletonStatus={CONTRACT_STATUS}",
        f"sourceImplementationReadinessStatus={SOURCE_STATUS}",
        "sourceProofCount=7",
        f"contractVersion={CONTRACT_VERSION}",
        f"validationSchema={VALIDATION_SCHEMA}",
        "contractInterfaceCount=6",
        "implementedContractInterfaceCount=6",
        "contractFunctionCount=2",
        "publicContractSkeletonImplementationRows=1",
        "validationSummaryRows=1",
        "skeletonContractCheckCount=46",
        "failedSkeletonContractChecks=0",
        "sourceReadinessGateCount=8",
        "sourceReadinessCheckCount=16",
        "sourceFailedReadinessGateCount=0",
        "sourceBlockedReadinessGateCount=0",
        "sourceConsumedFixtureRowCount=8",
        "sourceConsumerDryRunStepCount=10",
        "sourceConsumerAssertionGroupCount=8",
        "sourceConsumerAssertionCheckCount=19",
        "sourceFailedConsumerAssertions=0",
        "sourceUnexpectedFixtureRows=0",
        "sourceConsumerOutputArtifactRows=0",
        "publicSyntheticFixtureCount=8",
        "publicEdgeCaseIdCount=2",
        "uniqueModelTextureRefUnion=213",
        "familyUniqueRefsAreNotAdditive=true",
        "embeddedDuplicateOutputSurplusRows=32",
        "publicLeakCheck=PASS",
        "validate_public_contract_skeleton",
        "emit_public_validation_summary",
        "load-public-consumer-dry-run-schema",
        "enumerate-consumed-fixture-row-ids",
        "validate-aggregate-counts",
        "validate-public-edge-case-boundaries",
        "refuse-private-or-runtime-inputs",
        "emit-public-validation-summary",
        "stem-only-sidecar-match-boundary-001",
        "ambiguous-catalog-ref-boundary-001",
        "rawRefPublished=false",
        "rawStemPublished=false",
        "catalogVariantPublished=false",
        "filenamePublished=false",
        "pathPublished=false",
        "hashPublished=false",
        "213 + 139 = 352",
        "602 + 666 = 1268",
        "213 + 28 = 241",
        "212 + 1 = 213",
        "139 - 107 = 32",
        "publicContractSkeletonImplemented=true",
        "contractSkeletonValidationExecuted=true",
        "readsOnlyTrackedPublicSchema=true",
        "emitsOnlyValidationSummary=true",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
        "importerImplementation=false",
        "importerExecuted=false",
        "realImporterImplementationReadyNow=false",
        "realImporterExecutionReadyNow=false",
        "implementationDeferred=true",
        "explicitImporterImplementationArmPresent=false",
        "privateAssetReadAuthorizationPresent=false",
        "operatorPrivateOutputReviewAvailable=false",
        "runtimeExecution=false",
        "godotWork=false",
        "ghidraMutation=false",
        "rebuildImplementation=false",
        "rebuildParityProven=false",
        "noNoticeableDifferenceParityProven=false",
        "actualAssetImportRows=0",
        "generatedAssetRows=0",
        "outputArtifactRows=0",
        "dryRunOutputArtifactRows=0",
        "realImporterImplementationRows=0",
        "beProcessesAfterPublicContractSkeleton=0",
        "falseGuardCount=45",
        "zeroCounterCount=37",
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
        "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.md",
        "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.v1.json",
        CONTRACT_STATUS,
        "sourceImplementationReadinessStatus=" + SOURCE_STATUS,
        "contractInterfaceCount=6",
        "implementedContractInterfaceCount=6",
        "contractFunctionCount=2",
        "publicContractSkeletonImplementationRows=1",
        "skeletonContractCheckCount=46",
        "failedSkeletonContractChecks=0",
        "uniqueModelTextureRefUnion=213",
        "familyUniqueRefsAreNotAdditive=true",
        "embeddedDuplicateOutputSurplusRows=32",
        "realImporterImplementation=false",
        "realImporterExecuted=false",
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
    require(f"Completed {THIS_SLICE}" in backlog, "backlog missing completed public skeleton slice", failures)
    require(f"Completed {PREVIOUS_SLICE}" in backlog, "backlog missing completed readiness gate slice", failures)
    require(f"The selected active static-to-proof slice is {THIS_SLICE}. Status: selected" not in active, "active block still marks public skeleton active", failures)
    require(f"Completed {NEXT_SLICE}" in backlog, "backlog missing completed private corpus safety boundary", failures)
    require(f"The selected active static-to-proof slice is {NEXT_SLICE}. Status: selected" not in active, "active block still marks private corpus safety boundary active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_CHECKLIST_SLICE}" in backlog, "backlog missing completed private corpus safety packet checklist population", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_CHECKLIST_SLICE}. Status: selected" not in active, "active block still marks private corpus safety packet checklist population active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE}" in backlog, "backlog missing completed private corpus read-only inventory preflight", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_INVENTORY_PREFLIGHT_SLICE}. Status: selected" not in active, "active block still marks private corpus read-only inventory preflight active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE}" in backlog, "backlog missing completed private corpus read-only manifest dry-run", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_DRY_RUN_SLICE}. Status: selected" not in active, "active block still marks private corpus read-only manifest dry-run active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE}" in backlog, "backlog missing completed private corpus read-only manifest materialization", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_MATERIALIZATION_SLICE}. Status: selected" not in active, "active block still marks private corpus read-only manifest materialization active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE}" in backlog, "backlog missing completed private corpus read-only manifest consumer validation", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_CONSUMER_VALIDATION_SLICE}. Status: selected" not in active, "active block still marks private corpus read-only manifest consumer validation active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE}" in backlog, "backlog missing completed private corpus redacted manifest importer contract adapter", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_SLICE}. Status: selected" not in active, "active block still marks private corpus redacted manifest importer contract adapter active", failures)
    require(f"Completed {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE}" in backlog, "backlog missing completed private corpus redacted manifest importer contract adapter dry-run", failures)
    require(f"The selected active static-to-proof slice is {FOLLOWUP_PRIVATE_MANIFEST_ADAPTER_DRY_RUN_SLICE}. Status: selected" not in active, "active block still marks private corpus redacted manifest importer contract adapter dry-run active", failures)
    require("The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" in active, "active block missing private corpus real importer dry-run command consumer validation", failures)
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
        scripts.get("test:texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan")
        == r"py -3 tools\texture_mesh_material_sidecar_importer_public_contract_skeleton_implementation_proof_plan_probe.py --check",
        "missing package public skeleton test script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    require(MODULE.is_file(), "public contract skeleton module missing", failures)
    source = check_source_readiness(failures)
    check_result(source, failures)
    check_docs(failures)
    check_front_doors_and_package(failures)
    require(no_bea_process_running(), "BEA process is running after public skeleton probe", failures)

    if failures:
        print("Texture/mesh material sidecar importer public contract skeleton probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Texture/mesh material sidecar importer public contract skeleton probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
