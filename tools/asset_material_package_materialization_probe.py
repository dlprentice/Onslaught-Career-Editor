#!/usr/bin/env python3
"""Validate guarded asset material package materialization."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_NAME = "material-package-manifest.v1.json"
WORK_ORDER_NAME = "material-package-work-order.v1.json"
IMPORTER_DRY_RUN_NAME = "material-package-importer-dry-run.v1.json"
IMPORTER_INPUT_NAME = "material-package-importer-input.v1.json"
IMPORTER_INPUT_ROOT = "importer-input"
REBUILD_PREVIEW_NAME = "material-package-rebuild-preview.v1.json"
REBUILD_PREVIEW_ROOT = "rebuild-preview"
REBUILD_SCENE_NAME = "material-package-rebuild-scene.v1.json"
REBUILD_SCENE_ROOT = "rebuild-scene"
REBUILD_MESH_NAME = "material-package-rebuild-mesh.v1.json"
REBUILD_MESH_ROOT = "rebuild-mesh"
REBUILD_MESH_IMPORT_NAME = "material-package-rebuild-mesh-import.v1.json"
DEFAULT_CATALOG = (
    ROOT
    / "subagents"
    / "texture_mesh_asset_bridge_proof_2026-06-08"
    / "asset_catalog"
    / "catalog.json"
)
HOST_PROJECT = ROOT / "OnslaughtCareerEditor.AppCore.Host" / "OnslaughtCareerEditor.AppCore.Host.csproj"
CLI_PROJECT = ROOT / "OnslaughtCareerEditor.Cli" / "OnslaughtCareerEditor.Cli.csproj"
HOST_DLL = ROOT / "OnslaughtCareerEditor.AppCore.Host" / "bin" / "Debug" / "net10.0" / "OnslaughtCareerEditor.AppCore.Host.dll"
CLI_DLL = ROOT / "OnslaughtCareerEditor.Cli" / "bin" / "Debug" / "net10.0-windows" / "OnslaughtCareerEditor.Cli.dll"
OUT_ROOT = ROOT / "subagents" / "asset-material-package-materialization-probe"
ARM_PHRASE = "MATERIALIZE ASSET MATERIAL PACKAGE"


def run(command: list[str], *, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if expect_success and result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    if not expect_success and result.returncode == 0:
        raise RuntimeError(f"command unexpectedly succeeded: {' '.join(command)}")
    return result


def parse_json(output: str) -> dict:
    return json.loads(output)


def count_files(path: Path) -> int:
    return sum(1 for child in path.rglob("*") if child.is_file())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_host(catalog: Path, output_root: Path) -> dict:
    preflight_out = output_root / "host-preflight"
    preflight = parse_json(
        run(
            [
                "dotnet",
                str(HOST_DLL),
                "materialize-asset-material-import-package",
                str(catalog),
                str(preflight_out),
                "--preflight",
            ]
        ).stdout
    )
    preflight_result = preflight["materialImportPackageMaterialization"]
    require(preflight["mode"] == "preflight", "host preflight mode mismatch")
    require(preflight["mutation"] is False, "host preflight mutation flag mismatch")
    require(preflight_result["executed"] is False, "host preflight executed flag mismatch")
    require(preflight_result["completed"] is True, "host preflight did not complete")
    require(preflight_result["plannedFiles"] == 565, "host preflight planned file count mismatch")
    require(preflight_result["wouldCopyFiles"] == 565, "host preflight would-copy count mismatch")
    require(preflight_result["manifestWritten"] is False, "host preflight wrote manifest")
    require(preflight_result["manifestStatus"] == "preflight-not-written", "host preflight manifest status mismatch")
    require(preflight_result["workOrderSidecarWritten"] is False, "host preflight wrote work-order sidecar")
    require(preflight_result["workOrderSidecarStatus"] == "preflight-not-written", "host preflight sidecar status mismatch")
    require(preflight_result["importerDryRunSidecarWritten"] is False, "host preflight wrote importer dry-run sidecar")
    require(preflight_result["importerDryRunSidecarStatus"] == "preflight-not-written", "host preflight importer dry-run sidecar status mismatch")
    require(not preflight_out.exists(), "host preflight created output root")

    copy_out = output_root / "host-copy"
    copy = parse_json(
        run(
            [
                "dotnet",
                str(HOST_DLL),
                "materialize-asset-material-import-package",
                str(catalog),
                str(copy_out),
                "--arm-private-asset-output",
                ARM_PHRASE,
            ]
        ).stdout
    )
    copy_result = copy["materialImportPackageMaterialization"]
    require(copy["mode"] == "copy", "host copy mode mismatch")
    require(copy["mutation"] is True, "host copy mutation flag mismatch")
    require(copy_result["executed"] is True, "host copy executed flag mismatch")
    require(copy_result["completed"] is True, "host copy did not complete")
    require(copy_result["copiedFiles"] == 565, "host copied file count mismatch")
    require(copy_result["modelFilesCopied"] == 352, "host model copied count mismatch")
    require(copy_result["textureFilesCopied"] == 213, "host texture copied count mismatch")
    require(copy_result["manifestWritten"] is True, "host copy did not write manifest")
    require(copy_result["manifestRelativePath"] == MANIFEST_NAME, "host manifest relative path mismatch")
    require(copy_result["manifestStatus"] == "written", "host manifest status mismatch")
    require(copy_result["workOrderSidecarWritten"] is True, "host copy did not write work-order sidecar")
    require(copy_result["workOrderSidecarRelativePath"] == WORK_ORDER_NAME, "host work-order sidecar relative path mismatch")
    require(copy_result["workOrderSidecarStatus"] == "written", "host work-order sidecar status mismatch")
    require(copy_result["importerDryRunSidecarWritten"] is True, "host copy did not write importer dry-run sidecar")
    require(copy_result["importerDryRunSidecarRelativePath"] == IMPORTER_DRY_RUN_NAME, "host importer dry-run sidecar relative path mismatch")
    require(copy_result["importerDryRunSidecarStatus"] == "written", "host importer dry-run sidecar status mismatch")
    manifest_path = copy_out / MANIFEST_NAME
    require(manifest_path.is_file(), "host manifest file missing")
    manifest = parse_json(manifest_path.read_text(encoding="utf-8"))
    require(manifest["schema"] == "onslaught.asset-material-package-manifest.v1", "host manifest schema mismatch")
    require(manifest["totalPackageFiles"] == 565, "host manifest package file count mismatch")
    require(len(manifest["files"]) == 565, "host manifest rows mismatch")
    require(len(manifest["models"]) == 352, "host manifest model graph rows mismatch")
    require(
        sum(len(model["textureReferences"]) for model in manifest["models"]) == 1268,
        "host manifest texture-reference graph rows mismatch",
    )
    require(str(catalog.parent) not in manifest_path.read_text(encoding="utf-8"), "host manifest leaked catalog source path")
    sidecar_path = copy_out / WORK_ORDER_NAME
    require(sidecar_path.is_file(), "host work-order sidecar file missing")
    sidecar_raw = sidecar_path.read_text(encoding="utf-8")
    require(str(catalog.parent) not in sidecar_raw, "host work-order sidecar leaked catalog source path")
    require(str(copy_out) not in sidecar_raw, "host work-order sidecar leaked package root path")
    sidecar = parse_json(sidecar_raw)
    require(sidecar["schema"] == "onslaught.asset-material-package-work-order.v1", "host work-order sidecar schema mismatch")
    sidecar_work_order = sidecar["materialPackageWorkOrder"]
    require(sidecar_work_order["completed"] is True, "host work-order sidecar completion mismatch")
    require(sidecar_work_order["workOrderModelRows"] == 352, "host work-order sidecar model row mismatch")
    require(sidecar_work_order["readyWorkOrderModelRows"] == 352, "host work-order sidecar ready model row mismatch")
    require(sidecar_work_order["readyTextureReferenceRows"] == 1268, "host work-order sidecar texture row mismatch")
    importer_dry_run_path = copy_out / IMPORTER_DRY_RUN_NAME
    require(importer_dry_run_path.is_file(), "host importer dry-run sidecar file missing")
    importer_dry_run_raw = importer_dry_run_path.read_text(encoding="utf-8")
    require(str(catalog.parent) not in importer_dry_run_raw, "host importer dry-run sidecar leaked catalog source path")
    require(str(copy_out) not in importer_dry_run_raw, "host importer dry-run sidecar leaked package root path")
    importer_dry_run_sidecar = parse_json(importer_dry_run_raw)
    require(importer_dry_run_sidecar["schema"] == "onslaught.asset-material-package-importer-dry-run.v1", "host importer dry-run sidecar schema mismatch")
    sidecar_dry_run = importer_dry_run_sidecar["materialPackageImporterDryRun"]
    require(sidecar_dry_run["completed"] is True, "host importer dry-run sidecar completion mismatch")
    require(sidecar_dry_run["modelTaskRows"] == 352, "host importer dry-run sidecar model task row mismatch")
    require(sidecar_dry_run["textureTaskRows"] == 1268, "host importer dry-run sidecar texture task row mismatch")
    require(sidecar_dry_run["plannedAdapterRows"] == 1620, "host importer dry-run sidecar planned adapter row mismatch")
    require(sidecar_dry_run["readyAdapterRows"] == 1620, "host importer dry-run sidecar ready adapter row mismatch")
    require(len(sidecar_dry_run["rows"]) == 1620, "host importer dry-run sidecar rows mismatch")
    require(count_files(copy_out) == 568, "host output file count mismatch")

    inspection = parse_json(
        run(
            [
                "dotnet",
                str(HOST_DLL),
                "inspect-asset-material-package",
                str(copy_out),
            ]
        ).stdout
    )
    inspection_result = inspection["materialPackageInspection"]
    require(inspection["mutation"] is False, "host inspection mutation flag mismatch")
    require(inspection_result["completed"] is True, "host package inspection did not complete")
    require(inspection_result["manifestStatus"] == "ok", "host package inspection status mismatch")
    require(inspection_result["manifestFileRows"] == 565, "host package inspection manifest rows mismatch")
    require(inspection_result["manifestModelGraphRows"] == 352, "host package inspection model graph rows mismatch")
    require(inspection_result["manifestReadyModelGraphRows"] == 352, "host package inspection ready model graph rows mismatch")
    require(inspection_result["manifestTextureReferenceRows"] == 1268, "host package inspection texture graph rows mismatch")
    require(inspection_result["manifestResolvedTextureReferenceRows"] == 1268, "host package inspection resolved texture graph rows mismatch")
    require(inspection_result["existingManifestFiles"] == 565, "host package inspection existing files mismatch")
    require(inspection_result["missingManifestFiles"] == 0, "host package inspection missing files mismatch")
    require(inspection_result["extraPayloadFiles"] == 0, "host package inspection extra files mismatch")
    require(inspection_result["unsafeManifestPaths"] == 0, "host package inspection unsafe path mismatch")
    require(inspection_result["unsafeModelGraphPaths"] == 0, "host package inspection unsafe graph path mismatch")
    require(inspection_result["manifestContainsPackageRoot"] is False, "host package inspection path leak flag mismatch")

    work_order_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "build-asset-material-package-work-order",
            str(copy_out),
        ]
    ).stdout
    require(str(catalog.parent) not in work_order_raw, "host work order leaked catalog source path")
    require(str(copy_out) not in work_order_raw, "host work order leaked package root path")
    work_order = parse_json(work_order_raw)
    work_order_result = work_order["materialPackageWorkOrder"]
    require(work_order["mutation"] is False, "host work-order mutation flag mismatch")
    require(work_order_result["completed"] is True, "host work order did not complete")
    require(work_order_result["manifestStatus"] == "ok", "host work-order manifest status mismatch")
    require(work_order_result["manifestInspectionCompleted"] is True, "host work-order inspection flag mismatch")
    require(work_order_result["manifestModelGraphRows"] == 352, "host work-order graph row mismatch")
    require(work_order_result["manifestReadyModelGraphRows"] == 352, "host work-order ready graph row mismatch")
    require(work_order_result["workOrderModelRows"] == 352, "host work-order model row mismatch")
    require(work_order_result["readyWorkOrderModelRows"] == 352, "host work-order ready model row mismatch")
    require(work_order_result["textureReferenceRows"] == 1268, "host work-order texture row mismatch")
    require(work_order_result["resolvedTextureReferenceRows"] == 1268, "host work-order resolved texture row mismatch")
    require(work_order_result["readyTextureReferenceRows"] == 1268, "host work-order ready texture row mismatch")
    require(work_order_result["missingPackageFiles"] == 0, "host work-order missing file mismatch")
    require(work_order_result["unsafePackagePaths"] == 0, "host work-order unsafe path mismatch")
    require(work_order_result["manifestContainsPackageRoot"] is False, "host work-order path leak flag mismatch")
    require(len(work_order_result["models"]) == 352, "host work-order model list mismatch")
    require(
        all(model["readyForImporter"] is True and model["importReadiness"] == "ready-for-importer" for model in work_order_result["models"]),
        "host work-order model readiness mismatch",
    )

    sidecar_validation_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "validate-asset-material-package-work-order-sidecar",
            str(copy_out),
        ]
    ).stdout
    require(str(catalog.parent) not in sidecar_validation_raw, "host sidecar validation leaked catalog source path")
    require(str(copy_out) not in sidecar_validation_raw, "host sidecar validation leaked package root path")
    sidecar_validation = parse_json(sidecar_validation_raw)
    sidecar_validation_result = sidecar_validation["materialPackageWorkOrderSidecarValidation"]
    require(sidecar_validation["mutation"] is False, "host sidecar validation mutation flag mismatch")
    require(sidecar_validation_result["completed"] is True, "host sidecar validation did not complete")
    require(sidecar_validation_result["sidecarStatus"] == "ok", "host sidecar validation status mismatch")
    require(sidecar_validation_result["sidecarExists"] is True, "host sidecar validation missing sidecar")
    require(sidecar_validation_result["schemaValid"] is True, "host sidecar validation schema mismatch")
    require(sidecar_validation_result["sidecarContainsPackageRoot"] is False, "host sidecar validation path leak flag mismatch")
    require(sidecar_validation_result["sidecarCompletedFlag"] is True, "host sidecar validation sidecar completion mismatch")
    require(sidecar_validation_result["freshWorkOrderCompleted"] is True, "host sidecar validation fresh completion mismatch")
    require(sidecar_validation_result["workOrderMatchesFreshBuild"] is True, "host sidecar validation fresh match mismatch")
    require(sidecar_validation_result["sidecarWorkOrderModelRows"] == 352, "host sidecar validation sidecar model rows mismatch")
    require(sidecar_validation_result["freshWorkOrderModelRows"] == 352, "host sidecar validation fresh model rows mismatch")
    require(sidecar_validation_result["sidecarReadyWorkOrderModelRows"] == 352, "host sidecar validation sidecar ready rows mismatch")
    require(sidecar_validation_result["freshReadyWorkOrderModelRows"] == 352, "host sidecar validation fresh ready rows mismatch")
    require(sidecar_validation_result["sidecarReadyTextureReferenceRows"] == 1268, "host sidecar validation sidecar texture rows mismatch")
    require(sidecar_validation_result["freshReadyTextureReferenceRows"] == 1268, "host sidecar validation fresh texture rows mismatch")
    require(sidecar_validation_result["freshMissingPackageFiles"] == 0, "host sidecar validation missing files mismatch")

    importer_batch_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "build-asset-material-package-importer-batch",
            str(copy_out),
        ]
    ).stdout
    require(str(catalog.parent) not in importer_batch_raw, "host importer batch leaked catalog source path")
    require(str(copy_out) not in importer_batch_raw, "host importer batch leaked package root path")
    importer_batch = parse_json(importer_batch_raw)
    importer_batch_result = importer_batch["materialPackageImporterBatch"]
    require(importer_batch["mutation"] is False, "host importer batch mutation flag mismatch")
    require(importer_batch_result["completed"] is True, "host importer batch did not complete")
    require(importer_batch_result["sidecarStatus"] == "ok", "host importer batch sidecar status mismatch")
    require(importer_batch_result["sidecarValidated"] is True, "host importer batch sidecar validation mismatch")
    require(importer_batch_result["workOrderCompleted"] is True, "host importer batch work-order completion mismatch")
    require(importer_batch_result["modelTaskRows"] == 352, "host importer batch model task rows mismatch")
    require(importer_batch_result["textureTaskRows"] == 1268, "host importer batch texture task rows mismatch")
    require(importer_batch_result["totalTaskRows"] == 1620, "host importer batch total task rows mismatch")
    require(importer_batch_result["readyTaskRows"] == 1620, "host importer batch ready task rows mismatch")
    require(importer_batch_result["blockedTaskRows"] == 0, "host importer batch blocked task rows mismatch")
    require(len(importer_batch_result["tasks"]) == 1620, "host importer batch task list mismatch")
    require(importer_batch_result["tasks"][0]["ordinal"] == 1, "host importer batch first ordinal mismatch")
    require(importer_batch_result["tasks"][-1]["ordinal"] == 1620, "host importer batch last ordinal mismatch")
    require(
        all(task["readyForImporter"] is True and task["taskStatus"] == "ready-for-importer" for task in importer_batch_result["tasks"]),
        "host importer batch readiness mismatch",
    )

    importer_dry_run_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "build-asset-material-package-importer-dry-run",
            str(copy_out),
        ]
    ).stdout
    require(str(catalog.parent) not in importer_dry_run_raw, "host importer dry run leaked catalog source path")
    require(str(copy_out) not in importer_dry_run_raw, "host importer dry run leaked package root path")
    importer_dry_run = parse_json(importer_dry_run_raw)
    importer_dry_run_result = importer_dry_run["materialPackageImporterDryRun"]
    require(importer_dry_run["mutation"] is False, "host importer dry run mutation flag mismatch")
    require(importer_dry_run_result["completed"] is True, "host importer dry run did not complete")
    require(importer_dry_run_result["sourceBatchStatus"] == "ok", "host importer dry run source batch status mismatch")
    require(importer_dry_run_result["sourceBatchValidated"] is True, "host importer dry run batch validation mismatch")
    require(importer_dry_run_result["sourceBatchCompleted"] is True, "host importer dry run batch completion mismatch")
    require(importer_dry_run_result["modelTaskRows"] == 352, "host importer dry run model task rows mismatch")
    require(importer_dry_run_result["textureTaskRows"] == 1268, "host importer dry run texture task rows mismatch")
    require(importer_dry_run_result["totalTaskRows"] == 1620, "host importer dry run total task rows mismatch")
    require(importer_dry_run_result["readyTaskRows"] == 1620, "host importer dry run ready task rows mismatch")
    require(importer_dry_run_result["blockedTaskRows"] == 0, "host importer dry run blocked task rows mismatch")
    require(importer_dry_run_result["plannedAdapterRows"] == 1620, "host importer dry run planned adapter rows mismatch")
    require(importer_dry_run_result["readyAdapterRows"] == 1620, "host importer dry run ready adapter rows mismatch")
    require(len(importer_dry_run_result["rows"]) == 1620, "host importer dry run row list mismatch")
    require(importer_dry_run_result["rows"][0]["ordinal"] == 1, "host importer dry run first ordinal mismatch")
    require(importer_dry_run_result["rows"][-1]["ordinal"] == 1620, "host importer dry run last ordinal mismatch")
    require(
        all(row["readyForAdapter"] is True and row["taskStatus"] == "ready-for-importer" for row in importer_dry_run_result["rows"]),
        "host importer dry run readiness mismatch",
    )

    importer_dry_run_sidecar_validation_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "validate-asset-material-package-importer-dry-run-sidecar",
            str(copy_out),
        ]
    ).stdout
    require(str(catalog.parent) not in importer_dry_run_sidecar_validation_raw, "host importer dry-run sidecar validation leaked catalog source path")
    require(str(copy_out) not in importer_dry_run_sidecar_validation_raw, "host importer dry-run sidecar validation leaked package root path")
    importer_dry_run_sidecar_validation = parse_json(importer_dry_run_sidecar_validation_raw)
    importer_dry_run_sidecar_validation_result = importer_dry_run_sidecar_validation["materialPackageImporterDryRunSidecarValidation"]
    require(importer_dry_run_sidecar_validation["mutation"] is False, "host importer dry-run sidecar validation mutation flag mismatch")
    require(importer_dry_run_sidecar_validation_result["completed"] is True, "host importer dry-run sidecar validation did not complete")
    require(importer_dry_run_sidecar_validation_result["sidecarStatus"] == "ok", "host importer dry-run sidecar validation status mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarExists"] is True, "host importer dry-run sidecar validation missing sidecar")
    require(importer_dry_run_sidecar_validation_result["schemaValid"] is True, "host importer dry-run sidecar validation schema mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarContainsPackageRoot"] is False, "host importer dry-run sidecar validation path leak flag mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarCompletedFlag"] is True, "host importer dry-run sidecar validation sidecar completion mismatch")
    require(importer_dry_run_sidecar_validation_result["freshDryRunCompleted"] is True, "host importer dry-run sidecar validation fresh completion mismatch")
    require(importer_dry_run_sidecar_validation_result["dryRunMatchesFreshBuild"] is True, "host importer dry-run sidecar validation fresh match mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarPlannedAdapterRows"] == 1620, "host importer dry-run sidecar validation sidecar planned rows mismatch")
    require(importer_dry_run_sidecar_validation_result["freshPlannedAdapterRows"] == 1620, "host importer dry-run sidecar validation fresh planned rows mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarReadyAdapterRows"] == 1620, "host importer dry-run sidecar validation sidecar ready rows mismatch")
    require(importer_dry_run_sidecar_validation_result["freshReadyAdapterRows"] == 1620, "host importer dry-run sidecar validation fresh ready rows mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarTotalTaskRows"] == 1620, "host importer dry-run sidecar validation sidecar task rows mismatch")
    require(importer_dry_run_sidecar_validation_result["freshTotalTaskRows"] == 1620, "host importer dry-run sidecar validation fresh task rows mismatch")
    require(importer_dry_run_sidecar_validation_result["freshBlockedTaskRows"] == 0, "host importer dry-run sidecar validation blocked rows mismatch")

    importer_input_preflight_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-importer-input",
            str(copy_out),
            "--preflight",
        ]
    ).stdout
    require(str(catalog.parent) not in importer_input_preflight_raw, "host importer input preflight leaked catalog source path")
    require(str(copy_out) not in importer_input_preflight_raw, "host importer input preflight leaked package root path")
    require("sha256" not in importer_input_preflight_raw.lower(), "host importer input preflight leaked asset hash tokens")
    importer_input_preflight = parse_json(importer_input_preflight_raw)
    importer_input_preflight_result = importer_input_preflight["materialPackageImporterInputMaterialization"]
    require(importer_input_preflight["mode"] == "preflight", "host importer input preflight mode mismatch")
    require(importer_input_preflight["mutation"] is False, "host importer input preflight mutation flag mismatch")
    require(importer_input_preflight_result["executed"] is False, "host importer input preflight executed flag mismatch")
    require(importer_input_preflight_result["completed"] is True, "host importer input preflight did not complete")
    require(importer_input_preflight_result["sourceDryRunSidecarValidated"] is True, "host importer input preflight sidecar validation mismatch")
    require(importer_input_preflight_result["sourceDryRunCompleted"] is True, "host importer input preflight dry-run completion mismatch")
    require(importer_input_preflight_result["plannedAdapterRows"] == 1620, "host importer input preflight planned row mismatch")
    require(importer_input_preflight_result["inputRowsReady"] == 1620, "host importer input preflight ready row mismatch")
    require(importer_input_preflight_result["modelInputRows"] == 352, "host importer input preflight model row mismatch")
    require(importer_input_preflight_result["textureInputRows"] == 1268, "host importer input preflight texture row mismatch")
    require(importer_input_preflight_result["uniqueAdapterFiles"] == 565, "host importer input preflight unique file mismatch")
    require(importer_input_preflight_result["wouldCopyFiles"] == 565, "host importer input preflight would-copy mismatch")
    require(importer_input_preflight_result["wouldUsePlannedCopyRows"] == 1055, "host importer input preflight duplicate-row mismatch")
    require(importer_input_preflight_result["manifestWritten"] is False, "host importer input preflight wrote manifest")
    require(importer_input_preflight_result["manifestStatus"] == "preflight-not-written", "host importer input preflight manifest status mismatch")
    require(not (copy_out / IMPORTER_INPUT_ROOT).exists(), "host importer input preflight created importer-input root")

    bad_importer_input = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-importer-input",
            str(copy_out),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to stage private asset bytes" in bad_importer_input.stdout, "host importer input wrong-arm error mismatch")
    require(not (copy_out / IMPORTER_INPUT_ROOT).exists(), "host importer input wrong-arm created importer-input root")

    importer_input_copy_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-importer-input",
            str(copy_out),
            "--arm-private-asset-output",
            ARM_PHRASE,
        ]
    ).stdout
    require(str(catalog.parent) not in importer_input_copy_raw, "host importer input copy leaked catalog source path")
    require(str(copy_out) not in importer_input_copy_raw, "host importer input copy leaked package root path")
    require("sha256" not in importer_input_copy_raw.lower(), "host importer input copy leaked asset hash tokens")
    importer_input_copy = parse_json(importer_input_copy_raw)
    importer_input_copy_result = importer_input_copy["materialPackageImporterInputMaterialization"]
    require(importer_input_copy["mode"] == "copy", "host importer input copy mode mismatch")
    require(importer_input_copy["mutation"] is True, "host importer input copy mutation flag mismatch")
    require(importer_input_copy["artifact"]["originalGameMutation"] is False, "host importer input original game mutation flag mismatch")
    require(importer_input_copy_result["executed"] is True, "host importer input copy executed flag mismatch")
    require(importer_input_copy_result["completed"] is True, "host importer input copy did not complete")
    require(importer_input_copy_result["sourceDryRunSidecarValidated"] is True, "host importer input copy sidecar validation mismatch")
    require(importer_input_copy_result["sourceDryRunCompleted"] is True, "host importer input copy dry-run completion mismatch")
    require(importer_input_copy_result["plannedAdapterRows"] == 1620, "host importer input copy planned row mismatch")
    require(importer_input_copy_result["inputRowsReady"] == 1620, "host importer input copy ready row mismatch")
    require(importer_input_copy_result["uniqueAdapterFiles"] == 565, "host importer input copy unique file mismatch")
    require(importer_input_copy_result["copiedFiles"] == 565, "host importer input copy copied file mismatch")
    require(importer_input_copy_result["existingFilesSkipped"] == 1055, "host importer input copy duplicate-skip mismatch")
    require(importer_input_copy_result["existingHashMismatches"] == 0, "host importer input copy hash mismatch count")
    require(importer_input_copy_result["missingSourceFiles"] == 0, "host importer input copy missing source count")
    require(importer_input_copy_result["unsafeSourcePaths"] == 0, "host importer input copy unsafe source count")
    require(importer_input_copy_result["unsafeDestinationPaths"] == 0, "host importer input copy unsafe destination count")
    require(importer_input_copy_result["manifestWritten"] is True, "host importer input copy did not write manifest")
    require(importer_input_copy_result["manifestRelativePath"] == IMPORTER_INPUT_NAME, "host importer input manifest path mismatch")
    require(importer_input_copy_result["manifestStatus"] == "written", "host importer input manifest status mismatch")
    importer_input_manifest_path = copy_out / IMPORTER_INPUT_NAME
    require(importer_input_manifest_path.is_file(), "host importer input manifest file missing")
    importer_input_manifest_raw = importer_input_manifest_path.read_text(encoding="utf-8")
    require(str(catalog.parent) not in importer_input_manifest_raw, "host importer input manifest leaked catalog source path")
    require(str(copy_out) not in importer_input_manifest_raw, "host importer input manifest leaked package root path")
    require("sha256" not in importer_input_manifest_raw.lower(), "host importer input manifest leaked asset hash tokens")
    importer_input_manifest = parse_json(importer_input_manifest_raw)
    require(importer_input_manifest["schema"] == "onslaught.asset-material-package-importer-input.v1", "host importer input manifest schema mismatch")
    require(importer_input_manifest["completed"] is True, "host importer input manifest completion mismatch")
    require(importer_input_manifest["plannedAdapterRows"] == 1620, "host importer input manifest planned rows mismatch")
    require(importer_input_manifest["readyAdapterRows"] == 1620, "host importer input manifest ready rows mismatch")
    require(importer_input_manifest["uniqueAdapterFiles"] == 565, "host importer input manifest unique file mismatch")
    require(len(importer_input_manifest["rows"]) == 1620, "host importer input manifest row count mismatch")
    require(count_files(copy_out / IMPORTER_INPUT_ROOT) == 565, "host importer-input file count mismatch")
    require(count_files(copy_out) == 1134, "host staged output file count mismatch")

    post_stage_inspection = parse_json(
        run(
            [
                "dotnet",
                str(HOST_DLL),
                "inspect-asset-material-package",
                str(copy_out),
            ]
        ).stdout
    )
    post_stage_inspection_result = post_stage_inspection["materialPackageInspection"]
    require(post_stage_inspection_result["completed"] is True, "host post-stage package inspection did not complete")
    require(post_stage_inspection_result["extraPayloadFiles"] == 0, "host post-stage inspection saw importer-input as extra payload")

    importer_input_plan_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "build-asset-material-package-importer-input-plan",
            str(copy_out),
        ]
    ).stdout
    require(str(catalog.parent) not in importer_input_plan_raw, "host importer input plan leaked catalog source path")
    require(str(copy_out) not in importer_input_plan_raw, "host importer input plan leaked package root path")
    require("sha256" not in importer_input_plan_raw.lower(), "host importer input plan leaked asset hash tokens")
    importer_input_plan = parse_json(importer_input_plan_raw)
    importer_input_plan_result = importer_input_plan["materialPackageImporterInputPlan"]
    require(importer_input_plan["mutation"] is False, "host importer input plan mutation flag mismatch")
    require(importer_input_plan_result["completed"] is True, "host importer input plan did not complete")
    require(importer_input_plan_result["manifestStatus"] == "ready", "host importer input plan status mismatch")
    require(importer_input_plan_result["inputManifestSchemaValid"] is True, "host importer input plan input schema mismatch")
    require(importer_input_plan_result["inputManifestCompletedFlag"] is True, "host importer input plan input completion mismatch")
    require(importer_input_plan_result["sourceDryRunSidecarValidated"] is True, "host importer input plan source sidecar mismatch")
    require(importer_input_plan_result["plannedAdapterRows"] == 1620, "host importer input plan planned rows mismatch")
    require(importer_input_plan_result["manifestRows"] == 1620, "host importer input plan manifest rows mismatch")
    require(importer_input_plan_result["modelJobRows"] == 352, "host importer input plan model rows mismatch")
    require(importer_input_plan_result["textureBindingJobRows"] == 1268, "host importer input plan texture rows mismatch")
    require(importer_input_plan_result["totalJobRows"] == 1620, "host importer input plan total rows mismatch")
    require(importer_input_plan_result["readyJobRows"] == 1620, "host importer input plan ready rows mismatch")
    require(importer_input_plan_result["blockedJobRows"] == 0, "host importer input plan blocked rows mismatch")
    require(importer_input_plan_result["uniqueInputFiles"] == 565, "host importer input plan unique file mismatch")
    require(importer_input_plan_result["existingUniqueInputFiles"] == 565, "host importer input plan existing file mismatch")
    require(importer_input_plan_result["missingInputFiles"] == 0, "host importer input plan missing file mismatch")
    require(importer_input_plan_result["unsafeInputPaths"] == 0, "host importer input plan unsafe path mismatch")
    require(importer_input_plan_result["readableModelRows"] == 352, "host importer input plan readable model mismatch")
    require(importer_input_plan_result["modelGeometryRows"] == 352, "host importer input plan model geometry mismatch")
    require(importer_input_plan_result["readableTextureBindingRows"] == 1268, "host importer input plan readable texture mismatch")
    require(importer_input_plan_result["uniqueReadableTextureFiles"] == 213, "host importer input plan unique texture mismatch")
    require(len(importer_input_plan_result["modelJobs"]) == 352, "host importer input plan model job list mismatch")
    require(len(importer_input_plan_result["textureBindingJobs"]) == 1268, "host importer input plan texture job list mismatch")
    require(
        all(job["readyForImportPlan"] is True and job["planStatus"] == "ready-for-import-plan" for job in importer_input_plan_result["modelJobs"]),
        "host importer input plan model readiness mismatch",
    )
    require(
        all(job["readyForImportPlan"] is True and job["planStatus"] == "ready-for-import-plan" for job in importer_input_plan_result["textureBindingJobs"]),
        "host importer input plan texture readiness mismatch",
    )

    rebuild_preview_preflight_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-preview",
            str(copy_out),
            "--preflight",
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_preview_preflight_raw, "host rebuild preview preflight leaked catalog source path")
    require(str(copy_out) not in rebuild_preview_preflight_raw, "host rebuild preview preflight leaked package root path")
    require("sha256" not in rebuild_preview_preflight_raw.lower(), "host rebuild preview preflight leaked asset hash tokens")
    rebuild_preview_preflight = parse_json(rebuild_preview_preflight_raw)
    rebuild_preview_preflight_result = rebuild_preview_preflight["materialPackageRebuildPreview"]
    require(rebuild_preview_preflight["mode"] == "preflight", "host rebuild preview preflight mode mismatch")
    require(rebuild_preview_preflight["mutation"] is False, "host rebuild preview preflight mutation flag mismatch")
    require(rebuild_preview_preflight_result["executed"] is False, "host rebuild preview preflight executed flag mismatch")
    require(rebuild_preview_preflight_result["completed"] is True, "host rebuild preview preflight did not complete")
    require(rebuild_preview_preflight_result["sourceInputPlanCompleted"] is True, "host rebuild preview input-plan completion mismatch")
    require(rebuild_preview_preflight_result["sourceInputPlanStatus"] == "ready", "host rebuild preview input-plan status mismatch")
    require(rebuild_preview_preflight_result["modelPreviewRows"] == 352, "host rebuild preview model row mismatch")
    require(rebuild_preview_preflight_result["readyPreviewRows"] == 352, "host rebuild preview ready row mismatch")
    require(rebuild_preview_preflight_result["blockedPreviewRows"] == 0, "host rebuild preview blocked row mismatch")
    require(rebuild_preview_preflight_result["wouldWritePreviewRows"] == 352, "host rebuild preview would-write mismatch")
    require(rebuild_preview_preflight_result["objFileRows"] == 352, "host rebuild preview obj row mismatch")
    require(rebuild_preview_preflight_result["bindingSidecarRows"] == 352, "host rebuild preview sidecar row mismatch")
    require(rebuild_preview_preflight_result["textureBindingRows"] == 1268, "host rebuild preview texture binding mismatch")
    require(rebuild_preview_preflight_result["manifestWritten"] is False, "host rebuild preview preflight wrote manifest")
    require(not (copy_out / REBUILD_PREVIEW_ROOT).exists(), "host rebuild preview preflight created preview root")

    bad_rebuild_preview = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-preview",
            str(copy_out),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to write rebuild preview outputs" in bad_rebuild_preview.stdout, "host rebuild preview wrong-arm error mismatch")
    require(not (copy_out / REBUILD_PREVIEW_ROOT).exists(), "host rebuild preview wrong-arm created preview root")

    rebuild_preview_copy_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-preview",
            str(copy_out),
            "--arm-private-asset-output",
            ARM_PHRASE,
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_preview_copy_raw, "host rebuild preview copy leaked catalog source path")
    require(str(copy_out) not in rebuild_preview_copy_raw, "host rebuild preview copy leaked package root path")
    require("sha256" not in rebuild_preview_copy_raw.lower(), "host rebuild preview copy leaked asset hash tokens")
    rebuild_preview_copy = parse_json(rebuild_preview_copy_raw)
    rebuild_preview_copy_result = rebuild_preview_copy["materialPackageRebuildPreview"]
    require(rebuild_preview_copy["mode"] == "write", "host rebuild preview copy mode mismatch")
    require(rebuild_preview_copy["mutation"] is True, "host rebuild preview copy mutation flag mismatch")
    require(rebuild_preview_copy["artifact"]["originalGameMutation"] is False, "host rebuild preview original game mutation flag mismatch")
    require(rebuild_preview_copy_result["executed"] is True, "host rebuild preview copy executed flag mismatch")
    require(rebuild_preview_copy_result["completed"] is True, "host rebuild preview copy did not complete")
    require(rebuild_preview_copy_result["modelPreviewRows"] == 352, "host rebuild preview copy model row mismatch")
    require(rebuild_preview_copy_result["readyPreviewRows"] == 352, "host rebuild preview copy ready row mismatch")
    require(rebuild_preview_copy_result["writtenPreviewRows"] == 352, "host rebuild preview copy written row mismatch")
    require(rebuild_preview_copy_result["existingPreviewRows"] == 0, "host rebuild preview copy existing row mismatch")
    require(rebuild_preview_copy_result["objFileRows"] == 352, "host rebuild preview copy obj row mismatch")
    require(rebuild_preview_copy_result["bindingSidecarRows"] == 352, "host rebuild preview copy sidecar row mismatch")
    require(rebuild_preview_copy_result["textureBindingRows"] == 1268, "host rebuild preview copy texture binding mismatch")
    require(rebuild_preview_copy_result["manifestWritten"] is True, "host rebuild preview copy did not write manifest")
    require(rebuild_preview_copy_result["manifestRelativePath"] == REBUILD_PREVIEW_NAME, "host rebuild preview manifest path mismatch")
    require(count_files(copy_out / REBUILD_PREVIEW_ROOT) == 704, "host rebuild-preview file count mismatch")
    rebuild_preview_manifest_path = copy_out / REBUILD_PREVIEW_NAME
    require(rebuild_preview_manifest_path.is_file(), "host rebuild preview manifest missing")
    rebuild_preview_manifest_raw = rebuild_preview_manifest_path.read_text(encoding="utf-8")
    require(str(catalog.parent) not in rebuild_preview_manifest_raw, "host rebuild preview manifest leaked catalog source path")
    require(str(copy_out) not in rebuild_preview_manifest_raw, "host rebuild preview manifest leaked package root path")
    require("sha256" not in rebuild_preview_manifest_raw.lower(), "host rebuild preview manifest leaked asset hash tokens")
    rebuild_preview_manifest = parse_json(rebuild_preview_manifest_raw)
    require(rebuild_preview_manifest["schema"] == "onslaught.asset-material-package-rebuild-preview.v1", "host rebuild preview manifest schema mismatch")
    require(rebuild_preview_manifest["completed"] is True, "host rebuild preview manifest completion mismatch")
    require(rebuild_preview_manifest["modelPreviewRows"] == 352, "host rebuild preview manifest model rows mismatch")
    require(rebuild_preview_manifest["objFileRows"] == 352, "host rebuild preview manifest obj rows mismatch")
    require(rebuild_preview_manifest["bindingSidecarRows"] == 352, "host rebuild preview manifest sidecar rows mismatch")
    sample_obj = next((copy_out / REBUILD_PREVIEW_ROOT / "models").glob("*.wire.obj"))
    sample_obj_raw = sample_obj.read_text(encoding="utf-8-sig")
    require("# onslaught asset material package rebuild preview obj v1" in sample_obj_raw, "host rebuild preview sample obj marker missing")
    require("\nv " in sample_obj_raw, "host rebuild preview sample obj vertex rows missing")
    require("\nl " in sample_obj_raw, "host rebuild preview sample obj edge rows missing")

    rebuild_scene_preflight_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-scene",
            str(copy_out),
            "--preflight",
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_scene_preflight_raw, "host rebuild scene preflight leaked catalog source path")
    require(str(copy_out) not in rebuild_scene_preflight_raw, "host rebuild scene preflight leaked package root path")
    require("sha256" not in rebuild_scene_preflight_raw.lower(), "host rebuild scene preflight leaked asset hash tokens")
    rebuild_scene_preflight = parse_json(rebuild_scene_preflight_raw)
    rebuild_scene_preflight_result = rebuild_scene_preflight["materialPackageRebuildScene"]
    require(rebuild_scene_preflight["mode"] == "preflight", "host rebuild scene preflight mode mismatch")
    require(rebuild_scene_preflight["mutation"] is False, "host rebuild scene preflight mutation flag mismatch")
    require(rebuild_scene_preflight_result["executed"] is False, "host rebuild scene preflight executed flag mismatch")
    require(rebuild_scene_preflight_result["completed"] is True, "host rebuild scene preflight did not complete")
    require(rebuild_scene_preflight_result["sourceRebuildPreviewCompleted"] is True, "host rebuild scene source preview mismatch")
    require(rebuild_scene_preflight_result["sceneRows"] == 352, "host rebuild scene row mismatch")
    require(rebuild_scene_preflight_result["readySceneRows"] == 352, "host rebuild scene ready row mismatch")
    require(rebuild_scene_preflight_result["wouldWriteSceneRows"] == 352, "host rebuild scene would-write mismatch")
    require(rebuild_scene_preflight_result["textureBindingRows"] == 1268, "host rebuild scene texture binding mismatch")
    require(rebuild_scene_preflight_result["fbxVertexRows"] > 0, "host rebuild scene fbx vertex rows missing")
    require(rebuild_scene_preflight_result["fbxPolygonIndexRows"] > 0, "host rebuild scene polygon index rows missing")
    require(rebuild_scene_preflight_result["textureToMaterialConnectionRows"] > 0, "host rebuild scene texture-material links missing")
    require(rebuild_scene_preflight_result["manifestWritten"] is False, "host rebuild scene preflight wrote manifest")
    require(not (copy_out / REBUILD_SCENE_ROOT).exists(), "host rebuild scene preflight created scene root")

    bad_rebuild_scene = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-scene",
            str(copy_out),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to write rebuild scene contract outputs" in bad_rebuild_scene.stdout, "host rebuild scene wrong-arm error mismatch")
    require(not (copy_out / REBUILD_SCENE_ROOT).exists(), "host rebuild scene wrong-arm created scene root")

    bad_rebuild_scene_option = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-scene",
            str(copy_out),
            "--unsupported-materialization-option",
        ],
        expect_success=False,
    )
    require("Unsupported materialization option" in bad_rebuild_scene_option.stdout, "host rebuild scene unsupported-option error mismatch")
    require(not (copy_out / REBUILD_SCENE_ROOT).exists(), "host rebuild scene unsupported option created scene root")

    rebuild_scene_copy_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-scene",
            str(copy_out),
            "--arm-private-asset-output",
            ARM_PHRASE,
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_scene_copy_raw, "host rebuild scene copy leaked catalog source path")
    require(str(copy_out) not in rebuild_scene_copy_raw, "host rebuild scene copy leaked package root path")
    require("sha256" not in rebuild_scene_copy_raw.lower(), "host rebuild scene copy leaked asset hash tokens")
    rebuild_scene_copy = parse_json(rebuild_scene_copy_raw)
    rebuild_scene_copy_result = rebuild_scene_copy["materialPackageRebuildScene"]
    require(rebuild_scene_copy["mode"] == "write", "host rebuild scene copy mode mismatch")
    require(rebuild_scene_copy["mutation"] is True, "host rebuild scene copy mutation flag mismatch")
    require(rebuild_scene_copy["artifact"]["originalGameMutation"] is False, "host rebuild scene original game mutation flag mismatch")
    require(rebuild_scene_copy_result["executed"] is True, "host rebuild scene copy executed flag mismatch")
    require(rebuild_scene_copy_result["completed"] is True, "host rebuild scene copy did not complete")
    require(rebuild_scene_copy_result["sceneRows"] == 352, "host rebuild scene copy row mismatch")
    require(rebuild_scene_copy_result["readySceneRows"] == 352, "host rebuild scene copy ready row mismatch")
    require(rebuild_scene_copy_result["writtenSceneRows"] == 352, "host rebuild scene copy written row mismatch")
    require(rebuild_scene_copy_result["existingSceneRows"] == 0, "host rebuild scene copy existing row mismatch")
    require(rebuild_scene_copy_result["textureBindingRows"] == 1268, "host rebuild scene copy texture binding mismatch")
    require(rebuild_scene_copy_result["fbxVertexRows"] > 0, "host rebuild scene copy fbx vertex rows missing")
    require(rebuild_scene_copy_result["fbxPolygonIndexRows"] > 0, "host rebuild scene copy polygon index rows missing")
    require(rebuild_scene_copy_result["fbxTextureCoordinateRows"] > 0, "host rebuild scene copy uv rows missing")
    require(rebuild_scene_copy_result["textureToMaterialConnectionRows"] > 0, "host rebuild scene copy texture-material links missing")
    require(rebuild_scene_copy_result["manifestWritten"] is True, "host rebuild scene copy did not write manifest")
    require(rebuild_scene_copy_result["manifestRelativePath"] == REBUILD_SCENE_NAME, "host rebuild scene manifest path mismatch")
    require(count_files(copy_out / REBUILD_SCENE_ROOT) == 352, "host rebuild-scene file count mismatch")
    rebuild_scene_manifest_path = copy_out / REBUILD_SCENE_NAME
    require(rebuild_scene_manifest_path.is_file(), "host rebuild scene manifest missing")
    rebuild_scene_manifest_raw = rebuild_scene_manifest_path.read_text(encoding="utf-8")
    require(str(catalog.parent) not in rebuild_scene_manifest_raw, "host rebuild scene manifest leaked catalog source path")
    require(str(copy_out) not in rebuild_scene_manifest_raw, "host rebuild scene manifest leaked package root path")
    require("sha256" not in rebuild_scene_manifest_raw.lower(), "host rebuild scene manifest leaked asset hash tokens")
    rebuild_scene_manifest = parse_json(rebuild_scene_manifest_raw)
    require(rebuild_scene_manifest["schema"] == "onslaught.asset-material-package-rebuild-scene.v1", "host rebuild scene manifest schema mismatch")
    require(rebuild_scene_manifest["completed"] is True, "host rebuild scene manifest completion mismatch")
    require(rebuild_scene_manifest["sceneRows"] == 352, "host rebuild scene manifest row mismatch")
    require(rebuild_scene_manifest["readySceneRows"] == 352, "host rebuild scene manifest ready row mismatch")
    require(rebuild_scene_manifest["textureBindingRows"] == 1268, "host rebuild scene manifest texture binding mismatch")
    require(rebuild_scene_manifest["fbxPolygonIndexRows"] > 0, "host rebuild scene manifest polygon index rows missing")
    sample_scene = next((copy_out / REBUILD_SCENE_ROOT / "models").glob("*.scene.json"))
    sample_scene_raw = sample_scene.read_text(encoding="utf-8")
    require(str(catalog.parent) not in sample_scene_raw, "host rebuild scene sample leaked catalog source path")
    require(str(copy_out) not in sample_scene_raw, "host rebuild scene sample leaked package root path")
    require("sha256" not in sample_scene_raw.lower(), "host rebuild scene sample leaked asset hash tokens")
    sample_scene_json = parse_json(sample_scene_raw)
    require(sample_scene_json["schema"] == "onslaught.asset-material-package-rebuild-scene-file.v1", "host rebuild scene sample schema mismatch")
    require(sample_scene_json["meshContract"]["polygonIndexCount"] > 0, "host rebuild scene sample polygon index rows missing")
    require(sample_scene_json["meshContract"]["textureToMaterialConnectionCount"] > 0, "host rebuild scene sample texture-material links missing")
    require(len(sample_scene_json["textures"]) > 0, "host rebuild scene sample texture rows missing")

    rebuild_mesh_preflight_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-mesh",
            str(copy_out),
            "--preflight",
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_mesh_preflight_raw, "host rebuild mesh preflight leaked catalog source path")
    require(str(copy_out) not in rebuild_mesh_preflight_raw, "host rebuild mesh preflight leaked package root path")
    require("sha256" not in rebuild_mesh_preflight_raw.lower(), "host rebuild mesh preflight leaked asset hash tokens")
    rebuild_mesh_preflight = parse_json(rebuild_mesh_preflight_raw)
    rebuild_mesh_preflight_result = rebuild_mesh_preflight["materialPackageRebuildMesh"]
    require(rebuild_mesh_preflight["mode"] == "preflight", "host rebuild mesh preflight mode mismatch")
    require(rebuild_mesh_preflight["mutation"] is False, "host rebuild mesh preflight mutation flag mismatch")
    require(rebuild_mesh_preflight_result["executed"] is False, "host rebuild mesh preflight executed flag mismatch")
    require(rebuild_mesh_preflight_result["completed"] is True, "host rebuild mesh preflight did not complete")
    require(rebuild_mesh_preflight_result["sourceRebuildSceneCompleted"] is True, "host rebuild mesh source scene mismatch")
    require(rebuild_mesh_preflight_result["sourceExistingSceneRows"] == 352, "host rebuild mesh source scene existing row mismatch")
    require(rebuild_mesh_preflight_result["meshRows"] == 352, "host rebuild mesh row mismatch")
    require(rebuild_mesh_preflight_result["readyMeshRows"] == 352, "host rebuild mesh ready row mismatch")
    require(rebuild_mesh_preflight_result["wouldWriteMeshRows"] == 352, "host rebuild mesh would-write mismatch")
    require(rebuild_mesh_preflight_result["blockedMeshRows"] == 0, "host rebuild mesh blocked rows mismatch")
    require(rebuild_mesh_preflight_result["missingSceneContractRows"] == 0, "host rebuild mesh missing scene contracts")
    require(rebuild_mesh_preflight_result["missingModelInputRows"] == 0, "host rebuild mesh missing model input")
    require(rebuild_mesh_preflight_result["missingMeshPayloadRows"] == 0, "host rebuild mesh missing payload")
    require(rebuild_mesh_preflight_result["objFileRows"] == 352, "host rebuild mesh obj row mismatch")
    require(rebuild_mesh_preflight_result["mtlFileRows"] == 352, "host rebuild mesh mtl row mismatch")
    require(
        rebuild_mesh_preflight_result["completeMeshPayloadRows"] + rebuild_mesh_preflight_result["partialMeshPayloadRows"] == 352,
        "host rebuild mesh payload row accounting mismatch",
    )
    require(rebuild_mesh_preflight_result["vertexRows"] > 0, "host rebuild mesh vertex rows missing")
    require(rebuild_mesh_preflight_result["faceRows"] > 0, "host rebuild mesh face rows missing")
    require(rebuild_mesh_preflight_result["normalRows"] > 0, "host rebuild mesh normal rows missing")
    require(rebuild_mesh_preflight_result["textureCoordinateRows"] > 0, "host rebuild mesh uv rows missing")
    require(rebuild_mesh_preflight_result["materialRows"] > 0, "host rebuild mesh material rows missing")
    require(rebuild_mesh_preflight_result["textureBindingRows"] == 1268, "host rebuild mesh texture binding mismatch")
    require(rebuild_mesh_preflight_result["manifestWritten"] is False, "host rebuild mesh preflight wrote manifest")
    require(not (copy_out / REBUILD_MESH_ROOT).exists(), "host rebuild mesh preflight created mesh root")

    bad_rebuild_mesh = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-mesh",
            str(copy_out),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to write rebuild mesh outputs" in bad_rebuild_mesh.stdout, "host rebuild mesh wrong-arm error mismatch")
    require(not (copy_out / REBUILD_MESH_ROOT).exists(), "host rebuild mesh wrong-arm created mesh root")

    rebuild_mesh_copy_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-mesh",
            str(copy_out),
            "--arm-private-asset-output",
            ARM_PHRASE,
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_mesh_copy_raw, "host rebuild mesh copy leaked catalog source path")
    require(str(copy_out) not in rebuild_mesh_copy_raw, "host rebuild mesh copy leaked package root path")
    require("sha256" not in rebuild_mesh_copy_raw.lower(), "host rebuild mesh copy leaked asset hash tokens")
    rebuild_mesh_copy = parse_json(rebuild_mesh_copy_raw)
    rebuild_mesh_copy_result = rebuild_mesh_copy["materialPackageRebuildMesh"]
    require(rebuild_mesh_copy["mode"] == "write", "host rebuild mesh copy mode mismatch")
    require(rebuild_mesh_copy["mutation"] is True, "host rebuild mesh copy mutation flag mismatch")
    require(rebuild_mesh_copy["artifact"]["originalGameMutation"] is False, "host rebuild mesh original game mutation flag mismatch")
    require(rebuild_mesh_copy_result["executed"] is True, "host rebuild mesh copy executed flag mismatch")
    require(rebuild_mesh_copy_result["completed"] is True, "host rebuild mesh copy did not complete")
    require(rebuild_mesh_copy_result["meshRows"] == 352, "host rebuild mesh copy row mismatch")
    require(rebuild_mesh_copy_result["readyMeshRows"] == 352, "host rebuild mesh copy ready row mismatch")
    require(rebuild_mesh_copy_result["writtenMeshRows"] == 352, "host rebuild mesh copy written row mismatch")
    require(rebuild_mesh_copy_result["existingMeshRows"] == 0, "host rebuild mesh copy existing row mismatch")
    require(rebuild_mesh_copy_result["objFileRows"] == 352, "host rebuild mesh copy obj row mismatch")
    require(rebuild_mesh_copy_result["mtlFileRows"] == 352, "host rebuild mesh copy mtl row mismatch")
    require(rebuild_mesh_copy_result["faceRows"] > 0, "host rebuild mesh copy face rows missing")
    require(rebuild_mesh_copy_result["textureBindingRows"] == 1268, "host rebuild mesh copy texture binding mismatch")
    require(rebuild_mesh_copy_result["manifestWritten"] is True, "host rebuild mesh copy did not write manifest")
    require(rebuild_mesh_copy_result["manifestRelativePath"] == REBUILD_MESH_NAME, "host rebuild mesh manifest path mismatch")
    require(count_files(copy_out / REBUILD_MESH_ROOT) == 704, "host rebuild-mesh file count mismatch")
    rebuild_mesh_manifest_path = copy_out / REBUILD_MESH_NAME
    require(rebuild_mesh_manifest_path.is_file(), "host rebuild mesh manifest missing")
    rebuild_mesh_manifest_raw = rebuild_mesh_manifest_path.read_text(encoding="utf-8")
    require(str(catalog.parent) not in rebuild_mesh_manifest_raw, "host rebuild mesh manifest leaked catalog source path")
    require(str(copy_out) not in rebuild_mesh_manifest_raw, "host rebuild mesh manifest leaked package root path")
    require("sha256" not in rebuild_mesh_manifest_raw.lower(), "host rebuild mesh manifest leaked asset hash tokens")
    rebuild_mesh_manifest = parse_json(rebuild_mesh_manifest_raw)
    require(rebuild_mesh_manifest["schema"] == "onslaught.asset-material-package-rebuild-mesh.v1", "host rebuild mesh manifest schema mismatch")
    require(rebuild_mesh_manifest["completed"] is True, "host rebuild mesh manifest completion mismatch")
    require(rebuild_mesh_manifest["meshRows"] == 352, "host rebuild mesh manifest row mismatch")
    require(rebuild_mesh_manifest["readyMeshRows"] == 352, "host rebuild mesh manifest ready row mismatch")
    require(rebuild_mesh_manifest["objFileRows"] == 352, "host rebuild mesh manifest obj row mismatch")
    require(rebuild_mesh_manifest["mtlFileRows"] == 352, "host rebuild mesh manifest mtl row mismatch")
    require(rebuild_mesh_manifest["faceRows"] > 0, "host rebuild mesh manifest face rows missing")
    sample_mesh_obj = next((copy_out / REBUILD_MESH_ROOT / "models").glob("*.mesh.obj"))
    sample_mesh_obj_raw = sample_mesh_obj.read_text(encoding="utf-8-sig")
    require(str(catalog.parent) not in sample_mesh_obj_raw, "host rebuild mesh sample obj leaked catalog source path")
    require(str(copy_out) not in sample_mesh_obj_raw, "host rebuild mesh sample obj leaked package root path")
    require("sha256" not in sample_mesh_obj_raw.lower(), "host rebuild mesh sample obj leaked asset hash tokens")
    require("# onslaught asset material package rebuild mesh obj v1" in sample_mesh_obj_raw, "host rebuild mesh sample obj marker missing")
    require("\nv " in sample_mesh_obj_raw, "host rebuild mesh sample obj vertex rows missing")
    require("\nf " in sample_mesh_obj_raw, "host rebuild mesh sample obj face rows missing")
    sample_mesh_mtl = next((copy_out / REBUILD_MESH_ROOT / "models").glob("*.mesh.mtl"))
    sample_mesh_mtl_raw = sample_mesh_mtl.read_text(encoding="utf-8-sig")
    require(str(catalog.parent) not in sample_mesh_mtl_raw, "host rebuild mesh sample mtl leaked catalog source path")
    require(str(copy_out) not in sample_mesh_mtl_raw, "host rebuild mesh sample mtl leaked package root path")
    require("sha256" not in sample_mesh_mtl_raw.lower(), "host rebuild mesh sample mtl leaked asset hash tokens")
    require("# onslaught asset material package rebuild mesh mtl v1" in sample_mesh_mtl_raw, "host rebuild mesh sample mtl marker missing")
    require("\nnewmtl " in sample_mesh_mtl_raw, "host rebuild mesh sample mtl material rows missing")
    require(
        any("map_Kd importer-input/textures/" in path.read_text(encoding="utf-8-sig") for path in (copy_out / REBUILD_MESH_ROOT / "models").glob("*.mesh.mtl")),
        "host rebuild mesh mtl texture binding rows missing",
    )

    rebuild_mesh_import_preflight_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-mesh-import",
            str(copy_out),
            "--preflight",
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_mesh_import_preflight_raw, "host rebuild mesh import preflight leaked catalog source path")
    require(str(copy_out) not in rebuild_mesh_import_preflight_raw, "host rebuild mesh import preflight leaked package root path")
    require("sha256" not in rebuild_mesh_import_preflight_raw.lower(), "host rebuild mesh import preflight leaked asset hash tokens")
    rebuild_mesh_import_preflight = parse_json(rebuild_mesh_import_preflight_raw)
    rebuild_mesh_import_preflight_result = rebuild_mesh_import_preflight["materialPackageRebuildMeshImport"]
    require(rebuild_mesh_import_preflight["mode"] == "preflight", "host rebuild mesh import preflight mode mismatch")
    require(rebuild_mesh_import_preflight["mutation"] is False, "host rebuild mesh import preflight mutation flag mismatch")
    require(rebuild_mesh_import_preflight_result["executed"] is False, "host rebuild mesh import preflight executed flag mismatch")
    require(rebuild_mesh_import_preflight_result["completed"] is True, "host rebuild mesh import preflight did not complete")
    require(rebuild_mesh_import_preflight_result["sourceRebuildMeshCompleted"] is True, "host rebuild mesh import source mesh mismatch")
    require(rebuild_mesh_import_preflight_result["importRows"] == 352, "host rebuild mesh import row mismatch")
    require(rebuild_mesh_import_preflight_result["readyImportRows"] == 352, "host rebuild mesh import ready row mismatch")
    require(rebuild_mesh_import_preflight_result["blockedImportRows"] == 0, "host rebuild mesh import blocked row mismatch")
    require(rebuild_mesh_import_preflight_result["objParsedRows"] == 352, "host rebuild mesh import obj parsed row mismatch")
    require(rebuild_mesh_import_preflight_result["mtlParsedRows"] == 352, "host rebuild mesh import mtl parsed row mismatch")
    require(rebuild_mesh_import_preflight_result["vertexRows"] == rebuild_mesh_copy_result["vertexRows"], "host rebuild mesh import vertex count mismatch")
    require(rebuild_mesh_import_preflight_result["faceRows"] == rebuild_mesh_copy_result["faceRows"], "host rebuild mesh import face count mismatch")
    require(rebuild_mesh_import_preflight_result["normalRows"] == rebuild_mesh_copy_result["normalRows"], "host rebuild mesh import normal count mismatch")
    require(rebuild_mesh_import_preflight_result["textureCoordinateRows"] == rebuild_mesh_copy_result["textureCoordinateRows"], "host rebuild mesh import uv count mismatch")
    require(rebuild_mesh_import_preflight_result["materialRows"] == rebuild_mesh_copy_result["materialRows"], "host rebuild mesh import material count mismatch")
    require(rebuild_mesh_import_preflight_result["faceMaterialUseRows"] == rebuild_mesh_copy_result["faceRows"], "host rebuild mesh import face material usage mismatch")
    require(rebuild_mesh_import_preflight_result["textureReferenceRows"] > 0, "host rebuild mesh import texture references missing")
    require(rebuild_mesh_import_preflight_result["missingTextureRows"] == 0, "host rebuild mesh import missing texture mismatch")
    require(rebuild_mesh_import_preflight_result["countMismatchRows"] == 0, "host rebuild mesh import count mismatch rows")
    require(rebuild_mesh_import_preflight_result["undefinedMaterialUseRows"] == 0, "host rebuild mesh import undefined material rows")
    require(rebuild_mesh_import_preflight_result["unsafePathRows"] == 0, "host rebuild mesh import unsafe path rows")
    require(rebuild_mesh_import_preflight_result["manifestWritten"] is False, "host rebuild mesh import preflight wrote manifest")
    require(not (copy_out / REBUILD_MESH_IMPORT_NAME).exists(), "host rebuild mesh import preflight wrote manifest file")

    bad_rebuild_mesh_import = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-mesh-import",
            str(copy_out),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to write rebuild mesh import contract" in bad_rebuild_mesh_import.stdout, "host rebuild mesh import wrong-arm error mismatch")
    require(not (copy_out / REBUILD_MESH_IMPORT_NAME).exists(), "host rebuild mesh import wrong-arm wrote manifest")

    rebuild_mesh_import_copy_raw = run(
        [
            "dotnet",
            str(HOST_DLL),
            "materialize-asset-material-package-rebuild-mesh-import",
            str(copy_out),
            "--arm-private-asset-output",
            ARM_PHRASE,
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_mesh_import_copy_raw, "host rebuild mesh import copy leaked catalog source path")
    require(str(copy_out) not in rebuild_mesh_import_copy_raw, "host rebuild mesh import copy leaked package root path")
    require("sha256" not in rebuild_mesh_import_copy_raw.lower(), "host rebuild mesh import copy leaked asset hash tokens")
    rebuild_mesh_import_copy = parse_json(rebuild_mesh_import_copy_raw)
    rebuild_mesh_import_copy_result = rebuild_mesh_import_copy["materialPackageRebuildMeshImport"]
    require(rebuild_mesh_import_copy["mode"] == "write", "host rebuild mesh import copy mode mismatch")
    require(rebuild_mesh_import_copy["mutation"] is True, "host rebuild mesh import copy mutation flag mismatch")
    require(rebuild_mesh_import_copy["artifact"]["originalGameMutation"] is False, "host rebuild mesh import original game mutation flag mismatch")
    require(rebuild_mesh_import_copy_result["completed"] is True, "host rebuild mesh import copy did not complete")
    require(rebuild_mesh_import_copy_result["importRows"] == 352, "host rebuild mesh import copy row mismatch")
    require(rebuild_mesh_import_copy_result["readyImportRows"] == 352, "host rebuild mesh import copy ready row mismatch")
    require(rebuild_mesh_import_copy_result["manifestWritten"] is True, "host rebuild mesh import copy did not write manifest")
    require(rebuild_mesh_import_copy_result["manifestRelativePath"] == REBUILD_MESH_IMPORT_NAME, "host rebuild mesh import manifest path mismatch")
    rebuild_mesh_import_manifest_path = copy_out / REBUILD_MESH_IMPORT_NAME
    require(rebuild_mesh_import_manifest_path.is_file(), "host rebuild mesh import manifest missing")
    rebuild_mesh_import_manifest_raw = rebuild_mesh_import_manifest_path.read_text(encoding="utf-8")
    require(str(catalog.parent) not in rebuild_mesh_import_manifest_raw, "host rebuild mesh import manifest leaked catalog source path")
    require(str(copy_out) not in rebuild_mesh_import_manifest_raw, "host rebuild mesh import manifest leaked package root path")
    require("sha256" not in rebuild_mesh_import_manifest_raw.lower(), "host rebuild mesh import manifest leaked asset hash tokens")
    rebuild_mesh_import_manifest = parse_json(rebuild_mesh_import_manifest_raw)
    require(rebuild_mesh_import_manifest["schema"] == "onslaught.asset-material-package-rebuild-mesh-import.v1", "host rebuild mesh import manifest schema mismatch")
    require(rebuild_mesh_import_manifest["completed"] is True, "host rebuild mesh import manifest completion mismatch")
    require(rebuild_mesh_import_manifest["importRows"] == 352, "host rebuild mesh import manifest row mismatch")
    require(rebuild_mesh_import_manifest["readyImportRows"] == 352, "host rebuild mesh import manifest ready row mismatch")
    require(rebuild_mesh_import_manifest["countMismatchRows"] == 0, "host rebuild mesh import manifest count mismatch rows")
    require(rebuild_mesh_import_manifest["missingTextureRows"] == 0, "host rebuild mesh import manifest missing texture rows")

    post_preview_inspection = parse_json(
        run(
            [
                "dotnet",
                str(HOST_DLL),
                "inspect-asset-material-package",
                str(copy_out),
            ]
        ).stdout
    )
    post_preview_inspection_result = post_preview_inspection["materialPackageInspection"]
    require(post_preview_inspection_result["completed"] is True, "host post-mesh package inspection did not complete")
    require(post_preview_inspection_result["extraPayloadFiles"] == 0, "host post-mesh package inspection extra files mismatch")
    return copy_result


def validate_cli(catalog: Path, output_root: Path, host_copy_root: Path) -> dict:
    preflight_out = output_root / "cli-preflight"
    preflight = parse_json(
        run(
            [
                "dotnet",
                str(CLI_DLL),
                "--asset-material-import-package-materialize",
                str(catalog),
                "--asset-material-package-output",
                str(preflight_out),
                "--asset-material-package-preflight",
            ]
        ).stdout
    )
    preflight_result = preflight["materialImportPackageMaterialization"]
    require(preflight["mode"] == "preflight", "cli preflight mode mismatch")
    require(preflight["mutation"] is False, "cli preflight mutation flag mismatch")
    require(preflight_result["completed"] is True, "cli preflight did not complete")
    require(preflight_result["plannedFiles"] == 565, "cli preflight planned file count mismatch")
    require(preflight_result["manifestWritten"] is False, "cli preflight wrote manifest")
    require(preflight_result["workOrderSidecarWritten"] is False, "cli preflight wrote work-order sidecar")
    require(preflight_result["workOrderSidecarStatus"] == "preflight-not-written", "cli preflight sidecar status mismatch")
    require(preflight_result["importerDryRunSidecarWritten"] is False, "cli preflight wrote importer dry-run sidecar")
    require(preflight_result["importerDryRunSidecarStatus"] == "preflight-not-written", "cli preflight importer dry-run sidecar status mismatch")
    require(not preflight_out.exists(), "cli preflight created output root")

    bad_arm_out = output_root / "cli-bad-arm"
    bad = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-import-package-materialize",
            str(catalog),
            "--asset-material-package-output",
            str(bad_arm_out),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to copy private asset bytes" in bad.stderr, "cli wrong-arm error message mismatch")
    require(not bad_arm_out.exists(), "cli wrong-arm created output root")

    inspection = parse_json(
        run(
            [
                "dotnet",
                str(CLI_DLL),
                "--asset-material-package-inspect",
                str(host_copy_root),
            ]
        ).stdout
    )
    inspection_result = inspection["materialPackageInspection"]
    require(inspection["mutation"] is False, "cli inspection mutation flag mismatch")
    require(inspection_result["completed"] is True, "cli package inspection did not complete")
    require(inspection_result["manifestStatus"] == "ok", "cli package inspection status mismatch")
    require(inspection_result["manifestFileRows"] == 565, "cli package inspection manifest rows mismatch")
    require(inspection_result["manifestModelGraphRows"] == 352, "cli package inspection model graph rows mismatch")
    require(inspection_result["manifestReadyModelGraphRows"] == 352, "cli package inspection ready model graph rows mismatch")
    require(inspection_result["manifestTextureReferenceRows"] == 1268, "cli package inspection texture graph rows mismatch")
    require(inspection_result["manifestResolvedTextureReferenceRows"] == 1268, "cli package inspection resolved texture graph rows mismatch")
    require(inspection_result["existingManifestFiles"] == 565, "cli package inspection existing files mismatch")
    require(inspection_result["missingManifestFiles"] == 0, "cli package inspection missing files mismatch")
    require(inspection_result["extraPayloadFiles"] == 0, "cli package inspection extra files mismatch")
    require(inspection_result["unsafeManifestPaths"] == 0, "cli package inspection unsafe path mismatch")
    require(inspection_result["unsafeModelGraphPaths"] == 0, "cli package inspection unsafe graph path mismatch")

    work_order_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-work-order",
            str(host_copy_root),
        ]
    ).stdout
    require(str(catalog.parent) not in work_order_raw, "cli work order leaked catalog source path")
    require(str(host_copy_root) not in work_order_raw, "cli work order leaked package root path")
    work_order = parse_json(work_order_raw)
    work_order_result = work_order["materialPackageWorkOrder"]
    require(work_order["mutation"] is False, "cli work-order mutation flag mismatch")
    require(work_order_result["completed"] is True, "cli work order did not complete")
    require(work_order_result["manifestStatus"] == "ok", "cli work-order manifest status mismatch")
    require(work_order_result["workOrderModelRows"] == 352, "cli work-order model row mismatch")
    require(work_order_result["readyWorkOrderModelRows"] == 352, "cli work-order ready model row mismatch")
    require(work_order_result["textureReferenceRows"] == 1268, "cli work-order texture row mismatch")
    require(work_order_result["readyTextureReferenceRows"] == 1268, "cli work-order ready texture row mismatch")
    require(work_order_result["missingPackageFiles"] == 0, "cli work-order missing file mismatch")
    require(work_order_result["unsafePackagePaths"] == 0, "cli work-order unsafe path mismatch")

    sidecar_validation_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-work-order-sidecar-validate",
            str(host_copy_root),
        ]
    ).stdout
    require(str(catalog.parent) not in sidecar_validation_raw, "cli sidecar validation leaked catalog source path")
    require(str(host_copy_root) not in sidecar_validation_raw, "cli sidecar validation leaked package root path")
    sidecar_validation = parse_json(sidecar_validation_raw)
    sidecar_validation_result = sidecar_validation["materialPackageWorkOrderSidecarValidation"]
    require(sidecar_validation["mutation"] is False, "cli sidecar validation mutation flag mismatch")
    require(sidecar_validation_result["completed"] is True, "cli sidecar validation did not complete")
    require(sidecar_validation_result["sidecarStatus"] == "ok", "cli sidecar validation status mismatch")
    require(sidecar_validation_result["sidecarExists"] is True, "cli sidecar validation missing sidecar")
    require(sidecar_validation_result["schemaValid"] is True, "cli sidecar validation schema mismatch")
    require(sidecar_validation_result["sidecarContainsPackageRoot"] is False, "cli sidecar validation path leak flag mismatch")
    require(sidecar_validation_result["workOrderMatchesFreshBuild"] is True, "cli sidecar validation fresh match mismatch")
    require(sidecar_validation_result["sidecarWorkOrderModelRows"] == 352, "cli sidecar validation sidecar model rows mismatch")
    require(sidecar_validation_result["freshWorkOrderModelRows"] == 352, "cli sidecar validation fresh model rows mismatch")
    require(sidecar_validation_result["sidecarReadyWorkOrderModelRows"] == 352, "cli sidecar validation sidecar ready rows mismatch")
    require(sidecar_validation_result["freshReadyWorkOrderModelRows"] == 352, "cli sidecar validation fresh ready rows mismatch")
    require(sidecar_validation_result["sidecarReadyTextureReferenceRows"] == 1268, "cli sidecar validation sidecar texture rows mismatch")
    require(sidecar_validation_result["freshReadyTextureReferenceRows"] == 1268, "cli sidecar validation fresh texture rows mismatch")
    require(sidecar_validation_result["freshMissingPackageFiles"] == 0, "cli sidecar validation missing files mismatch")

    importer_batch_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-importer-batch",
            str(host_copy_root),
        ]
    ).stdout
    require(str(catalog.parent) not in importer_batch_raw, "cli importer batch leaked catalog source path")
    require(str(host_copy_root) not in importer_batch_raw, "cli importer batch leaked package root path")
    importer_batch = parse_json(importer_batch_raw)
    importer_batch_result = importer_batch["materialPackageImporterBatch"]
    require(importer_batch["mutation"] is False, "cli importer batch mutation flag mismatch")
    require(importer_batch_result["completed"] is True, "cli importer batch did not complete")
    require(importer_batch_result["sidecarStatus"] == "ok", "cli importer batch sidecar status mismatch")
    require(importer_batch_result["sidecarValidated"] is True, "cli importer batch sidecar validation mismatch")
    require(importer_batch_result["workOrderCompleted"] is True, "cli importer batch work-order completion mismatch")
    require(importer_batch_result["modelTaskRows"] == 352, "cli importer batch model task rows mismatch")
    require(importer_batch_result["textureTaskRows"] == 1268, "cli importer batch texture task rows mismatch")
    require(importer_batch_result["totalTaskRows"] == 1620, "cli importer batch total task rows mismatch")
    require(importer_batch_result["readyTaskRows"] == 1620, "cli importer batch ready task rows mismatch")
    require(importer_batch_result["blockedTaskRows"] == 0, "cli importer batch blocked task rows mismatch")
    require(len(importer_batch_result["tasks"]) == 1620, "cli importer batch task list mismatch")

    importer_dry_run_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-importer-dry-run",
            str(host_copy_root),
        ]
    ).stdout
    require(str(catalog.parent) not in importer_dry_run_raw, "cli importer dry run leaked catalog source path")
    require(str(host_copy_root) not in importer_dry_run_raw, "cli importer dry run leaked package root path")
    importer_dry_run = parse_json(importer_dry_run_raw)
    importer_dry_run_result = importer_dry_run["materialPackageImporterDryRun"]
    require(importer_dry_run["mutation"] is False, "cli importer dry run mutation flag mismatch")
    require(importer_dry_run_result["completed"] is True, "cli importer dry run did not complete")
    require(importer_dry_run_result["sourceBatchStatus"] == "ok", "cli importer dry run source batch status mismatch")
    require(importer_dry_run_result["sourceBatchValidated"] is True, "cli importer dry run batch validation mismatch")
    require(importer_dry_run_result["sourceBatchCompleted"] is True, "cli importer dry run batch completion mismatch")
    require(importer_dry_run_result["modelTaskRows"] == 352, "cli importer dry run model task rows mismatch")
    require(importer_dry_run_result["textureTaskRows"] == 1268, "cli importer dry run texture task rows mismatch")
    require(importer_dry_run_result["totalTaskRows"] == 1620, "cli importer dry run total task rows mismatch")
    require(importer_dry_run_result["readyTaskRows"] == 1620, "cli importer dry run ready task rows mismatch")
    require(importer_dry_run_result["blockedTaskRows"] == 0, "cli importer dry run blocked task rows mismatch")
    require(importer_dry_run_result["plannedAdapterRows"] == 1620, "cli importer dry run planned adapter rows mismatch")
    require(importer_dry_run_result["readyAdapterRows"] == 1620, "cli importer dry run ready adapter rows mismatch")
    require(len(importer_dry_run_result["rows"]) == 1620, "cli importer dry run row list mismatch")

    importer_dry_run_sidecar_validation_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-importer-dry-run-sidecar-validate",
            str(host_copy_root),
        ]
    ).stdout
    require(str(catalog.parent) not in importer_dry_run_sidecar_validation_raw, "cli importer dry-run sidecar validation leaked catalog source path")
    require(str(host_copy_root) not in importer_dry_run_sidecar_validation_raw, "cli importer dry-run sidecar validation leaked package root path")
    importer_dry_run_sidecar_validation = parse_json(importer_dry_run_sidecar_validation_raw)
    importer_dry_run_sidecar_validation_result = importer_dry_run_sidecar_validation["materialPackageImporterDryRunSidecarValidation"]
    require(importer_dry_run_sidecar_validation["mutation"] is False, "cli importer dry-run sidecar validation mutation flag mismatch")
    require(importer_dry_run_sidecar_validation_result["completed"] is True, "cli importer dry-run sidecar validation did not complete")
    require(importer_dry_run_sidecar_validation_result["sidecarStatus"] == "ok", "cli importer dry-run sidecar validation status mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarExists"] is True, "cli importer dry-run sidecar validation missing sidecar")
    require(importer_dry_run_sidecar_validation_result["schemaValid"] is True, "cli importer dry-run sidecar validation schema mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarContainsPackageRoot"] is False, "cli importer dry-run sidecar validation path leak flag mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarCompletedFlag"] is True, "cli importer dry-run sidecar validation sidecar completion mismatch")
    require(importer_dry_run_sidecar_validation_result["freshDryRunCompleted"] is True, "cli importer dry-run sidecar validation fresh completion mismatch")
    require(importer_dry_run_sidecar_validation_result["dryRunMatchesFreshBuild"] is True, "cli importer dry-run sidecar validation fresh match mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarPlannedAdapterRows"] == 1620, "cli importer dry-run sidecar validation sidecar planned rows mismatch")
    require(importer_dry_run_sidecar_validation_result["freshPlannedAdapterRows"] == 1620, "cli importer dry-run sidecar validation fresh planned rows mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarReadyAdapterRows"] == 1620, "cli importer dry-run sidecar validation sidecar ready rows mismatch")
    require(importer_dry_run_sidecar_validation_result["freshReadyAdapterRows"] == 1620, "cli importer dry-run sidecar validation fresh ready rows mismatch")
    require(importer_dry_run_sidecar_validation_result["sidecarTotalTaskRows"] == 1620, "cli importer dry-run sidecar validation sidecar task rows mismatch")
    require(importer_dry_run_sidecar_validation_result["freshTotalTaskRows"] == 1620, "cli importer dry-run sidecar validation fresh task rows mismatch")
    require(importer_dry_run_sidecar_validation_result["freshBlockedTaskRows"] == 0, "cli importer dry-run sidecar validation blocked rows mismatch")

    importer_input_preflight_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-importer-input-materialize",
            str(host_copy_root),
            "--asset-material-package-preflight",
        ]
    ).stdout
    require(str(catalog.parent) not in importer_input_preflight_raw, "cli importer input preflight leaked catalog source path")
    require(str(host_copy_root) not in importer_input_preflight_raw, "cli importer input preflight leaked package root path")
    require("sha256" not in importer_input_preflight_raw.lower(), "cli importer input preflight leaked asset hash tokens")
    importer_input_preflight = parse_json(importer_input_preflight_raw)
    importer_input_preflight_result = importer_input_preflight["materialPackageImporterInputMaterialization"]
    require(importer_input_preflight["mode"] == "preflight", "cli importer input preflight mode mismatch")
    require(importer_input_preflight["mutation"] is False, "cli importer input preflight mutation flag mismatch")
    require(importer_input_preflight_result["executed"] is False, "cli importer input preflight executed flag mismatch")
    require(importer_input_preflight_result["completed"] is True, "cli importer input preflight did not complete")
    require(importer_input_preflight_result["sourceDryRunSidecarValidated"] is True, "cli importer input preflight sidecar validation mismatch")
    require(importer_input_preflight_result["plannedAdapterRows"] == 1620, "cli importer input preflight planned row mismatch")
    require(importer_input_preflight_result["inputRowsReady"] == 1620, "cli importer input preflight ready row mismatch")
    require(importer_input_preflight_result["uniqueAdapterFiles"] == 565, "cli importer input preflight unique file mismatch")
    require(importer_input_preflight_result["existingFilesDetected"] == 1620, "cli importer input preflight existing row mismatch")
    require(importer_input_preflight_result["manifestWritten"] is False, "cli importer input preflight wrote manifest")

    bad_importer_input = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-importer-input-materialize",
            str(host_copy_root),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to stage private asset bytes" in bad_importer_input.stderr, "cli importer input wrong-arm error mismatch")

    importer_input_copy_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-importer-input-materialize",
            str(host_copy_root),
            "--arm-private-asset-output",
            ARM_PHRASE,
        ]
    ).stdout
    require(str(catalog.parent) not in importer_input_copy_raw, "cli importer input copy leaked catalog source path")
    require(str(host_copy_root) not in importer_input_copy_raw, "cli importer input copy leaked package root path")
    require("sha256" not in importer_input_copy_raw.lower(), "cli importer input copy leaked asset hash tokens")
    importer_input_copy = parse_json(importer_input_copy_raw)
    importer_input_copy_result = importer_input_copy["materialPackageImporterInputMaterialization"]
    require(importer_input_copy["mode"] == "copy", "cli importer input copy mode mismatch")
    require(importer_input_copy["mutation"] is True, "cli importer input copy mutation flag mismatch")
    require(importer_input_copy["artifact"]["originalGameMutation"] is False, "cli importer input original game mutation flag mismatch")
    require(importer_input_copy_result["executed"] is True, "cli importer input copy executed flag mismatch")
    require(importer_input_copy_result["completed"] is True, "cli importer input copy did not complete")
    require(importer_input_copy_result["plannedAdapterRows"] == 1620, "cli importer input copy planned row mismatch")
    require(importer_input_copy_result["inputRowsReady"] == 1620, "cli importer input copy ready row mismatch")
    require(importer_input_copy_result["uniqueAdapterFiles"] == 565, "cli importer input copy unique file mismatch")
    require(importer_input_copy_result["copiedFiles"] == 0, "cli importer input idempotent copy copied files")
    require(importer_input_copy_result["existingFilesSkipped"] == 1620, "cli importer input idempotent skip mismatch")
    require(importer_input_copy_result["existingHashMismatches"] == 0, "cli importer input idempotent hash mismatch count")
    require(importer_input_copy_result["manifestWritten"] is True, "cli importer input idempotent copy did not write manifest")

    importer_input_plan_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-importer-input-plan",
            str(host_copy_root),
        ]
    ).stdout
    require(str(catalog.parent) not in importer_input_plan_raw, "cli importer input plan leaked catalog source path")
    require(str(host_copy_root) not in importer_input_plan_raw, "cli importer input plan leaked package root path")
    require("sha256" not in importer_input_plan_raw.lower(), "cli importer input plan leaked asset hash tokens")
    importer_input_plan = parse_json(importer_input_plan_raw)
    importer_input_plan_result = importer_input_plan["materialPackageImporterInputPlan"]
    require(importer_input_plan["mutation"] is False, "cli importer input plan mutation flag mismatch")
    require(importer_input_plan_result["completed"] is True, "cli importer input plan did not complete")
    require(importer_input_plan_result["manifestStatus"] == "ready", "cli importer input plan status mismatch")
    require(importer_input_plan_result["modelJobRows"] == 352, "cli importer input plan model rows mismatch")
    require(importer_input_plan_result["textureBindingJobRows"] == 1268, "cli importer input plan texture rows mismatch")
    require(importer_input_plan_result["totalJobRows"] == 1620, "cli importer input plan total rows mismatch")
    require(importer_input_plan_result["readyJobRows"] == 1620, "cli importer input plan ready rows mismatch")
    require(importer_input_plan_result["blockedJobRows"] == 0, "cli importer input plan blocked rows mismatch")
    require(importer_input_plan_result["uniqueInputFiles"] == 565, "cli importer input plan unique file mismatch")
    require(importer_input_plan_result["existingUniqueInputFiles"] == 565, "cli importer input plan existing file mismatch")
    require(importer_input_plan_result["readableModelRows"] == 352, "cli importer input plan readable model mismatch")
    require(importer_input_plan_result["readableTextureBindingRows"] == 1268, "cli importer input plan readable texture mismatch")

    rebuild_preview_preflight_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-preview-materialize",
            str(host_copy_root),
            "--asset-material-package-preflight",
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_preview_preflight_raw, "cli rebuild preview preflight leaked catalog source path")
    require(str(host_copy_root) not in rebuild_preview_preflight_raw, "cli rebuild preview preflight leaked package root path")
    require("sha256" not in rebuild_preview_preflight_raw.lower(), "cli rebuild preview preflight leaked asset hash tokens")
    rebuild_preview_preflight = parse_json(rebuild_preview_preflight_raw)
    rebuild_preview_preflight_result = rebuild_preview_preflight["materialPackageRebuildPreview"]
    require(rebuild_preview_preflight["mode"] == "preflight", "cli rebuild preview preflight mode mismatch")
    require(rebuild_preview_preflight["mutation"] is False, "cli rebuild preview preflight mutation flag mismatch")
    require(rebuild_preview_preflight_result["completed"] is True, "cli rebuild preview preflight did not complete")
    require(rebuild_preview_preflight_result["modelPreviewRows"] == 352, "cli rebuild preview preflight model row mismatch")
    require(rebuild_preview_preflight_result["readyPreviewRows"] == 352, "cli rebuild preview preflight ready row mismatch")
    require(rebuild_preview_preflight_result["existingPreviewRows"] == 352, "cli rebuild preview preflight existing row mismatch")
    require(rebuild_preview_preflight_result["wouldWritePreviewRows"] == 0, "cli rebuild preview preflight would-write mismatch")
    require(rebuild_preview_preflight_result["manifestWritten"] is False, "cli rebuild preview preflight wrote manifest")

    bad_rebuild_preview = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-preview-materialize",
            str(host_copy_root),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to write rebuild preview outputs" in bad_rebuild_preview.stderr, "cli rebuild preview wrong-arm error mismatch")

    rebuild_preview_copy_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-preview-materialize",
            str(host_copy_root),
            "--arm-private-asset-output",
            ARM_PHRASE,
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_preview_copy_raw, "cli rebuild preview copy leaked catalog source path")
    require(str(host_copy_root) not in rebuild_preview_copy_raw, "cli rebuild preview copy leaked package root path")
    require("sha256" not in rebuild_preview_copy_raw.lower(), "cli rebuild preview copy leaked asset hash tokens")
    rebuild_preview_copy = parse_json(rebuild_preview_copy_raw)
    rebuild_preview_copy_result = rebuild_preview_copy["materialPackageRebuildPreview"]
    require(rebuild_preview_copy["mode"] == "write", "cli rebuild preview copy mode mismatch")
    require(rebuild_preview_copy["mutation"] is True, "cli rebuild preview copy mutation flag mismatch")
    require(rebuild_preview_copy["artifact"]["originalGameMutation"] is False, "cli rebuild preview original game mutation flag mismatch")
    require(rebuild_preview_copy_result["completed"] is True, "cli rebuild preview copy did not complete")
    require(rebuild_preview_copy_result["writtenPreviewRows"] == 0, "cli rebuild preview idempotent written row mismatch")
    require(rebuild_preview_copy_result["existingPreviewRows"] == 352, "cli rebuild preview idempotent existing row mismatch")
    require(rebuild_preview_copy_result["objFileRows"] == 352, "cli rebuild preview obj row mismatch")
    require(rebuild_preview_copy_result["bindingSidecarRows"] == 352, "cli rebuild preview sidecar row mismatch")
    require(rebuild_preview_copy_result["textureBindingRows"] == 1268, "cli rebuild preview texture binding mismatch")
    require(rebuild_preview_copy_result["manifestWritten"] is True, "cli rebuild preview copy did not write manifest")

    rebuild_scene_preflight_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-scene-materialize",
            str(host_copy_root),
            "--asset-material-package-preflight",
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_scene_preflight_raw, "cli rebuild scene preflight leaked catalog source path")
    require(str(host_copy_root) not in rebuild_scene_preflight_raw, "cli rebuild scene preflight leaked package root path")
    require("sha256" not in rebuild_scene_preflight_raw.lower(), "cli rebuild scene preflight leaked asset hash tokens")
    rebuild_scene_preflight = parse_json(rebuild_scene_preflight_raw)
    rebuild_scene_preflight_result = rebuild_scene_preflight["materialPackageRebuildScene"]
    require(rebuild_scene_preflight["mode"] == "preflight", "cli rebuild scene preflight mode mismatch")
    require(rebuild_scene_preflight["mutation"] is False, "cli rebuild scene preflight mutation flag mismatch")
    require(rebuild_scene_preflight_result["completed"] is True, "cli rebuild scene preflight did not complete")
    require(rebuild_scene_preflight_result["sceneRows"] == 352, "cli rebuild scene preflight row mismatch")
    require(rebuild_scene_preflight_result["readySceneRows"] == 352, "cli rebuild scene preflight ready row mismatch")
    require(rebuild_scene_preflight_result["existingSceneRows"] == 352, "cli rebuild scene preflight existing row mismatch")
    require(rebuild_scene_preflight_result["wouldWriteSceneRows"] == 0, "cli rebuild scene preflight would-write mismatch")
    require(rebuild_scene_preflight_result["textureBindingRows"] == 1268, "cli rebuild scene preflight texture binding mismatch")
    require(rebuild_scene_preflight_result["fbxPolygonIndexRows"] > 0, "cli rebuild scene preflight polygon index rows missing")
    require(rebuild_scene_preflight_result["textureToMaterialConnectionRows"] > 0, "cli rebuild scene preflight texture-material links missing")
    require(rebuild_scene_preflight_result["manifestWritten"] is False, "cli rebuild scene preflight wrote manifest")

    bad_rebuild_scene = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-scene-materialize",
            str(host_copy_root),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to write rebuild scene contract outputs" in bad_rebuild_scene.stderr, "cli rebuild scene wrong-arm error mismatch")

    rebuild_scene_copy_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-scene-materialize",
            str(host_copy_root),
            "--arm-private-asset-output",
            ARM_PHRASE,
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_scene_copy_raw, "cli rebuild scene copy leaked catalog source path")
    require(str(host_copy_root) not in rebuild_scene_copy_raw, "cli rebuild scene copy leaked package root path")
    require("sha256" not in rebuild_scene_copy_raw.lower(), "cli rebuild scene copy leaked asset hash tokens")
    rebuild_scene_copy = parse_json(rebuild_scene_copy_raw)
    rebuild_scene_copy_result = rebuild_scene_copy["materialPackageRebuildScene"]
    require(rebuild_scene_copy["mode"] == "write", "cli rebuild scene copy mode mismatch")
    require(rebuild_scene_copy["mutation"] is True, "cli rebuild scene copy mutation flag mismatch")
    require(rebuild_scene_copy["artifact"]["originalGameMutation"] is False, "cli rebuild scene original game mutation flag mismatch")
    require(rebuild_scene_copy_result["completed"] is True, "cli rebuild scene copy did not complete")
    require(rebuild_scene_copy_result["writtenSceneRows"] == 0, "cli rebuild scene idempotent written row mismatch")
    require(rebuild_scene_copy_result["existingSceneRows"] == 352, "cli rebuild scene idempotent existing row mismatch")
    require(rebuild_scene_copy_result["sceneRows"] == 352, "cli rebuild scene copy row mismatch")
    require(rebuild_scene_copy_result["readySceneRows"] == 352, "cli rebuild scene copy ready row mismatch")
    require(rebuild_scene_copy_result["textureBindingRows"] == 1268, "cli rebuild scene texture binding mismatch")
    require(rebuild_scene_copy_result["fbxPolygonIndexRows"] > 0, "cli rebuild scene copy polygon index rows missing")
    require(rebuild_scene_copy_result["fbxTextureCoordinateRows"] > 0, "cli rebuild scene copy uv rows missing")
    require(rebuild_scene_copy_result["textureToMaterialConnectionRows"] > 0, "cli rebuild scene copy texture-material links missing")
    require(rebuild_scene_copy_result["manifestWritten"] is True, "cli rebuild scene copy did not write manifest")

    rebuild_mesh_preflight_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-mesh-materialize",
            str(host_copy_root),
            "--asset-material-package-preflight",
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_mesh_preflight_raw, "cli rebuild mesh preflight leaked catalog source path")
    require(str(host_copy_root) not in rebuild_mesh_preflight_raw, "cli rebuild mesh preflight leaked package root path")
    require("sha256" not in rebuild_mesh_preflight_raw.lower(), "cli rebuild mesh preflight leaked asset hash tokens")
    rebuild_mesh_preflight = parse_json(rebuild_mesh_preflight_raw)
    rebuild_mesh_preflight_result = rebuild_mesh_preflight["materialPackageRebuildMesh"]
    require(rebuild_mesh_preflight["mode"] == "preflight", "cli rebuild mesh preflight mode mismatch")
    require(rebuild_mesh_preflight["mutation"] is False, "cli rebuild mesh preflight mutation flag mismatch")
    require(rebuild_mesh_preflight_result["completed"] is True, "cli rebuild mesh preflight did not complete")
    require(rebuild_mesh_preflight_result["meshRows"] == 352, "cli rebuild mesh preflight row mismatch")
    require(rebuild_mesh_preflight_result["readyMeshRows"] == 352, "cli rebuild mesh preflight ready row mismatch")
    require(rebuild_mesh_preflight_result["existingMeshRows"] == 352, "cli rebuild mesh preflight existing row mismatch")
    require(rebuild_mesh_preflight_result["wouldWriteMeshRows"] == 0, "cli rebuild mesh preflight would-write mismatch")
    require(rebuild_mesh_preflight_result["objFileRows"] == 352, "cli rebuild mesh obj row mismatch")
    require(rebuild_mesh_preflight_result["mtlFileRows"] == 352, "cli rebuild mesh mtl row mismatch")
    require(rebuild_mesh_preflight_result["faceRows"] > 0, "cli rebuild mesh face rows missing")
    require(rebuild_mesh_preflight_result["textureBindingRows"] == 1268, "cli rebuild mesh texture binding mismatch")
    require(rebuild_mesh_preflight_result["manifestWritten"] is False, "cli rebuild mesh preflight wrote manifest")

    bad_rebuild_mesh = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-mesh-materialize",
            str(host_copy_root),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to write rebuild mesh outputs" in bad_rebuild_mesh.stderr, "cli rebuild mesh wrong-arm error mismatch")

    rebuild_mesh_copy_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-mesh-materialize",
            str(host_copy_root),
            "--arm-private-asset-output",
            ARM_PHRASE,
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_mesh_copy_raw, "cli rebuild mesh copy leaked catalog source path")
    require(str(host_copy_root) not in rebuild_mesh_copy_raw, "cli rebuild mesh copy leaked package root path")
    require("sha256" not in rebuild_mesh_copy_raw.lower(), "cli rebuild mesh copy leaked asset hash tokens")
    rebuild_mesh_copy = parse_json(rebuild_mesh_copy_raw)
    rebuild_mesh_copy_result = rebuild_mesh_copy["materialPackageRebuildMesh"]
    require(rebuild_mesh_copy["mode"] == "write", "cli rebuild mesh copy mode mismatch")
    require(rebuild_mesh_copy["mutation"] is True, "cli rebuild mesh copy mutation flag mismatch")
    require(rebuild_mesh_copy["artifact"]["originalGameMutation"] is False, "cli rebuild mesh original game mutation flag mismatch")
    require(rebuild_mesh_copy_result["completed"] is True, "cli rebuild mesh copy did not complete")
    require(rebuild_mesh_copy_result["writtenMeshRows"] == 0, "cli rebuild mesh idempotent written row mismatch")
    require(rebuild_mesh_copy_result["existingMeshRows"] == 352, "cli rebuild mesh idempotent existing row mismatch")
    require(rebuild_mesh_copy_result["meshRows"] == 352, "cli rebuild mesh copy row mismatch")
    require(rebuild_mesh_copy_result["readyMeshRows"] == 352, "cli rebuild mesh copy ready row mismatch")
    require(rebuild_mesh_copy_result["objFileRows"] == 352, "cli rebuild mesh copy obj row mismatch")
    require(rebuild_mesh_copy_result["mtlFileRows"] == 352, "cli rebuild mesh copy mtl row mismatch")
    require(rebuild_mesh_copy_result["faceRows"] > 0, "cli rebuild mesh copy face rows missing")
    require(rebuild_mesh_copy_result["textureBindingRows"] == 1268, "cli rebuild mesh texture binding mismatch")
    require(rebuild_mesh_copy_result["manifestWritten"] is True, "cli rebuild mesh copy did not write manifest")

    rebuild_mesh_import_preflight_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-mesh-import-materialize",
            str(host_copy_root),
            "--asset-material-package-preflight",
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_mesh_import_preflight_raw, "cli rebuild mesh import preflight leaked catalog source path")
    require(str(host_copy_root) not in rebuild_mesh_import_preflight_raw, "cli rebuild mesh import preflight leaked package root path")
    require("sha256" not in rebuild_mesh_import_preflight_raw.lower(), "cli rebuild mesh import preflight leaked asset hash tokens")
    rebuild_mesh_import_preflight = parse_json(rebuild_mesh_import_preflight_raw)
    rebuild_mesh_import_preflight_result = rebuild_mesh_import_preflight["materialPackageRebuildMeshImport"]
    require(rebuild_mesh_import_preflight["mode"] == "preflight", "cli rebuild mesh import preflight mode mismatch")
    require(rebuild_mesh_import_preflight["mutation"] is False, "cli rebuild mesh import preflight mutation flag mismatch")
    require(rebuild_mesh_import_preflight_result["completed"] is True, "cli rebuild mesh import preflight did not complete")
    require(rebuild_mesh_import_preflight_result["sourceRebuildMeshCompleted"] is True, "cli rebuild mesh import source mesh mismatch")
    require(rebuild_mesh_import_preflight_result["importRows"] == 352, "cli rebuild mesh import row mismatch")
    require(rebuild_mesh_import_preflight_result["readyImportRows"] == 352, "cli rebuild mesh import ready row mismatch")
    require(rebuild_mesh_import_preflight_result["blockedImportRows"] == 0, "cli rebuild mesh import blocked row mismatch")
    require(rebuild_mesh_import_preflight_result["objParsedRows"] == 352, "cli rebuild mesh import obj parsed row mismatch")
    require(rebuild_mesh_import_preflight_result["mtlParsedRows"] == 352, "cli rebuild mesh import mtl parsed row mismatch")
    require(rebuild_mesh_import_preflight_result["vertexRows"] == rebuild_mesh_copy_result["vertexRows"], "cli rebuild mesh import vertex count mismatch")
    require(rebuild_mesh_import_preflight_result["faceRows"] == rebuild_mesh_copy_result["faceRows"], "cli rebuild mesh import face count mismatch")
    require(rebuild_mesh_import_preflight_result["normalRows"] == rebuild_mesh_copy_result["normalRows"], "cli rebuild mesh import normal count mismatch")
    require(rebuild_mesh_import_preflight_result["textureCoordinateRows"] == rebuild_mesh_copy_result["textureCoordinateRows"], "cli rebuild mesh import uv count mismatch")
    require(rebuild_mesh_import_preflight_result["materialRows"] == rebuild_mesh_copy_result["materialRows"], "cli rebuild mesh import material count mismatch")
    require(rebuild_mesh_import_preflight_result["faceMaterialUseRows"] == rebuild_mesh_copy_result["faceRows"], "cli rebuild mesh import face material usage mismatch")
    require(rebuild_mesh_import_preflight_result["textureReferenceRows"] > 0, "cli rebuild mesh import texture references missing")
    require(rebuild_mesh_import_preflight_result["missingTextureRows"] == 0, "cli rebuild mesh import missing texture mismatch")
    require(rebuild_mesh_import_preflight_result["countMismatchRows"] == 0, "cli rebuild mesh import count mismatch rows")
    require(rebuild_mesh_import_preflight_result["undefinedMaterialUseRows"] == 0, "cli rebuild mesh import undefined material rows")
    require(rebuild_mesh_import_preflight_result["unsafePathRows"] == 0, "cli rebuild mesh import unsafe path rows")
    require(rebuild_mesh_import_preflight_result["manifestWritten"] is False, "cli rebuild mesh import preflight wrote manifest")

    bad_rebuild_mesh_import = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-mesh-import-materialize",
            str(host_copy_root),
            "--arm-private-asset-output",
            "WRONG PHRASE",
        ],
        expect_success=False,
    )
    require("Refusing to write rebuild mesh import contract" in bad_rebuild_mesh_import.stderr, "cli rebuild mesh import wrong-arm error mismatch")

    rebuild_mesh_import_copy_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-rebuild-mesh-import-materialize",
            str(host_copy_root),
            "--arm-private-asset-output",
            ARM_PHRASE,
        ]
    ).stdout
    require(str(catalog.parent) not in rebuild_mesh_import_copy_raw, "cli rebuild mesh import copy leaked catalog source path")
    require(str(host_copy_root) not in rebuild_mesh_import_copy_raw, "cli rebuild mesh import copy leaked package root path")
    require("sha256" not in rebuild_mesh_import_copy_raw.lower(), "cli rebuild mesh import copy leaked asset hash tokens")
    rebuild_mesh_import_copy = parse_json(rebuild_mesh_import_copy_raw)
    rebuild_mesh_import_copy_result = rebuild_mesh_import_copy["materialPackageRebuildMeshImport"]
    require(rebuild_mesh_import_copy["mode"] == "write", "cli rebuild mesh import copy mode mismatch")
    require(rebuild_mesh_import_copy["mutation"] is True, "cli rebuild mesh import copy mutation flag mismatch")
    require(rebuild_mesh_import_copy["artifact"]["originalGameMutation"] is False, "cli rebuild mesh import original game mutation flag mismatch")
    require(rebuild_mesh_import_copy_result["completed"] is True, "cli rebuild mesh import copy did not complete")
    require(rebuild_mesh_import_copy_result["importRows"] == 352, "cli rebuild mesh import copy row mismatch")
    require(rebuild_mesh_import_copy_result["readyImportRows"] == 352, "cli rebuild mesh import copy ready row mismatch")
    require(rebuild_mesh_import_copy_result["manifestWritten"] is True, "cli rebuild mesh import copy did not write manifest")
    require(rebuild_mesh_import_copy_result["manifestRelativePath"] == REBUILD_MESH_IMPORT_NAME, "cli rebuild mesh import manifest path mismatch")

    post_scene_inspection_raw = run(
        [
            "dotnet",
            str(CLI_DLL),
            "--asset-material-package-inspect",
            str(host_copy_root),
        ]
    ).stdout
    require(str(catalog.parent) not in post_scene_inspection_raw, "cli post-scene inspection leaked catalog source path")
    require(str(host_copy_root) not in post_scene_inspection_raw, "cli post-scene inspection leaked package root path")
    post_scene_inspection = parse_json(post_scene_inspection_raw)
    post_scene_inspection_result = post_scene_inspection["materialPackageInspection"]
    require(post_scene_inspection_result["completed"] is True, "cli post-mesh package inspection did not complete")
    require(post_scene_inspection_result["extraPayloadFiles"] == 0, "cli post-mesh package inspection extra files mismatch")
    return preflight_result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()

    catalog = args.catalog.resolve()
    require(catalog.is_file(), f"copied-corpus catalog missing: {catalog}")

    run(["dotnet", "build", str(HOST_PROJECT), "--nologo"])
    run(["dotnet", "build", str(CLI_PROJECT), "--nologo"])

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_root = OUT_ROOT / stamp
    host_result = validate_host(catalog, output_root)
    cli_result = validate_cli(catalog, output_root, output_root / "host-copy")

    print("Asset material package materialization probe: PASS")
    print(f"Catalog: {catalog.name}")
    print(f"Output root: {output_root}")
    print(f"Host copied files: {host_result['copiedFiles']}")
    print(f"Host model files copied: {host_result['modelFilesCopied']}")
    print(f"Host texture files copied: {host_result['textureFilesCopied']}")
    print(f"Host manifest: {host_result['manifestRelativePath']} ({host_result['manifestStatus']})")
    print(f"Host work-order sidecar: {host_result['workOrderSidecarRelativePath']} ({host_result['workOrderSidecarStatus']})")
    print(f"Host importer dry-run sidecar: {host_result['importerDryRunSidecarRelativePath']} ({host_result['importerDryRunSidecarStatus']})")
    print("Host/CLI manifest inspection: ok (352 model rows, 1268 texture references)")
    print("Host/CLI package work order: ok (352 ready model tasks, 1268 ready texture-reference tasks)")
    print("Host/CLI package work-order sidecar validation: ok (fresh sidecar matches package)")
    print("Host/CLI importer batch: ok (1620 ready flat model/texture task rows)")
    print("Host/CLI importer dry run: ok (1620 ready adapter rows)")
    print("Host/CLI importer dry-run sidecar validation: ok (fresh sidecar matches package)")
    print("Host/CLI importer input staging: ok (565 unique files, 1620 adapter rows)")
    print("Host/CLI importer input plan: ok (1620 ready consumer jobs, 352 model imports, 1268 texture binds)")
    print("Host/CLI rebuild preview adapter: ok (352 OBJ wireframes, 352 binding sidecars, 1268 texture bindings)")
    print("Host/CLI rebuild scene contract: ok (352 scene contracts, FBX mesh/material facts, 1268 texture bindings)")
    print("Host/CLI rebuild mesh output: ok (352 OBJ meshes, 352 MTL files, face-bearing package-local geometry)")
    print("Host/CLI rebuild mesh import validation: ok (352 OBJ/MTL rows parsed and consumer-ready)")
    print(f"CLI preflight planned files: {cli_result['plannedFiles']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - command-line guard
        print(f"Asset material package materialization probe: FAIL\n{exc}", file=sys.stderr)
        raise SystemExit(1)
