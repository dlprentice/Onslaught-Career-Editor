#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Own the one-shot maintainer-Ghidra promotion of the proven Atomic14 island.

This owner is deliberately project-, specimen-, proof-, tool-, and cohort-
specific.  ``prepare`` is read-only: it reproduces the formal proof verifier,
observes the exact live PRE state, and creates two disjoint verified copies.
``promote`` rechecks that immutable preparation, writes an apply intent, spawns
the fixed mutator exactly once, then separately reopens and reads back the
result.  ``recover-status`` is observation-only and never restores or retries.

The proof establishes function/listing boundaries only.  This owner cannot
assign semantic names, signatures, types, comments, or rebuild readiness.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from types import SimpleNamespace
from typing import Mapping, Sequence


TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
OWNER_ROOT = REPO / "local-lab/console-callback-atomic14-live-promotion-20260803-v2"
LIVE_PROJECT = Path(r"C:\Users\david\Ghidra\Projects")
PROJECT_NAME = "BEA"
PROGRAM_NAME = "BEA.exe"
MUTEX_NAME = "Local\\OnslaughtToolkit.BEA.Ghidra.LivePromotion.v1"

SCHEMA = "bea.re.console-callback-atomic14-live-promotion.v1"
PREPARED_SCHEMA = "bea.re.console-callback-atomic14-live-prepared.v1"
OBSERVATION_SCHEMA = "bea.re.console-callback-atomic14-live-observation.v1"
ATTEMPT_SCHEMA = "bea.re.console-callback-atomic14-live-attempt.v1"
RECOVERY_SCHEMA = "bea.re.console-callback-atomic14-live-recovery.v1"

SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
FORMAL_ROOT = REPO / "local-lab/console-callback-atomic14-20260803-v1"
FORMAL_AUTHOR = FORMAL_ROOT / "run_formal_proof.py"
FORMAL_AUTHOR_SHA256 = "b85f9b3955aff646d47b4686ff700ef2a59d98371a03d62afb0f589c24776171"
FORMAL_READY = FORMAL_ROOT / "formal-proof-v2/formal-proof.ready.json"
FORMAL_READY_SHA256 = "a504c24b1eab555da8a01fc56d91561d3147a508dd3f906b0ac41e97697a83e6"
FORMAL_VERIFY_LINE = (
    "VERIFIED atomic14 formal proof PASS on two persistent apply/readback replicas"
)
ATOMIC_TOOL = FORMAL_ROOT / "RepairAndCreateConsoleCallbacks.java"
ATOMIC_TOOL_SHA256 = "0140bf6d5e1c449cdc7020f931e4388ffeec6d22b35144926ef62b5f8119ac1b"

BASELINE_PROJECT = (
    REPO
    / "local-lab/global-init515-live-promotion-20260803-v4/promotion/backups/post-live"
)
BASELINE_MANIFEST = BASELINE_PROJECT / "backup_manifest.json"
BASELINE_MANIFEST_SHA256 = "ccb47580355075548b213064a8b0e2e6f255b932da58b3f65c89bfc1f4a3e249"
BASELINE_FILESET_SHA256 = "3f3cdc53bcd1e38d11bad822500a776f8885f42d8f7093fbba0bc403133936dd"

HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)
HEADLESS_SHA256 = "dd7b9d17d32ed70a71df82a43a21cdaed6c4ce67064e30f8642c149f81c2ae07"
JAVA = Path(r"C:\Program Files\Eclipse Adoptium\jdk-21.0.9.10-hotspot\bin\java.exe")
JAVA_SHA256 = "5f6248f9c0f32b38ffaba813819bf3331536a48c7ddc45b18e73acd15a6cf7ef"
PYTHON = Path(r"C:\Users\david\AppData\Local\Python\pythoncore-3.14-64\python.exe")
PYTHON_SHA256 = "fda7026477256845afab371e354c4d512896665f1761939cb5887d0a9dec257a"

INVENTORY_TOOL = TOOLS / "ExportFullFunctionInventory.java"
INVENTORY_TOOL_SHA256 = "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"
SYMBOL_TOOL = TOOLS / "ExportTargetSymbolInventory.java"
SYMBOL_TOOL_SHA256 = "6ea0e6ce2669dd9cb325a052df70cd2f84cd5ebc1319cf5ba8c089691d660327"
STRING_TOOL = TOOLS / "ExportDefinedStrings.java"
STRING_TOOL_SHA256 = "1370b6107a3421b3ebf7c2cf06c8643c8e4ce780304fda0511c98a2dd01f92f9"
BACKUP_TOOL = TOOLS / "ghidra_project_backup.py"
BACKUP_TOOL_SHA256 = "36969a237eef29fea0daa52fe4a657127bdbbb5091523c9ca7cd92c69566b452"

GUARD_TOOL = TOOLS / "ghidra_global_init515_live_promotion.py"
GUARD_TOOL_SHA256 = "a1adf103f4c18487553970c62a21f01ea5cfa49c8039b3f299042ff6fc9e8747"
GUARD_DEPENDENCIES = {
    TOOLS / "ghidra_function_batch_proof.py":
        "f76a3e74bd618ef824b0185ce7bebf7476387381e8ace991af72c38560741afa",
    TOOLS / "ghidra_function_envelope_proof.py":
        "e20d619c39dd0f2037523b4577860b6640ed76b0be058472834a587192b305e8",
    TOOLS / "ghidra_global_init_full520_proof.py":
        "2fea029379aaf81df072907a87e142f03e4c1d261d19325933b18823b4fef972",
    TOOLS / "ghidra_promotion_scratch_proof.py":
        "895405aea9da78f72901250c7edb4e042ec28fadf6fbf9409d83097f8dd228be",
}


class PromotionError(ValueError):
    """A fail-closed Atomic14 live-owner refusal."""


class ProjectState(StrEnum):
    PRE = "PRE"
    POST = "POST"
    UNKNOWN = "UNKNOWN"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PromotionError(message)


def exact_file(path: Path, expected: str, label: str) -> Path:
    require(path.is_file() and not path.is_symlink(), f"{label} is absent or unsafe: {path}")
    require(sha256_file(path) == expected, f"{label} SHA-256 differs: {path}")
    return path.resolve()


def plain_single_file(path: Path, label: str) -> Path:
    require(path.is_file() and not path.is_symlink(), f"{label} is absent or unsafe: {path}")
    require(path.stat().st_nlink == 1, f"{label} is hard-linked: {path}")
    return path.resolve()


# Pin every local module before importing code from it.
exact_file(GUARD_TOOL, GUARD_TOOL_SHA256, "live guard")
for _dependency, _digest in GUARD_DEPENDENCIES.items():
    exact_file(_dependency, _digest, f"live guard dependency {_dependency.name}")
exact_file(BACKUP_TOOL, BACKUP_TOOL_SHA256, "backup dependency")
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import ghidra_global_init515_live_promotion as guard  # noqa: E402

# The formal module is executable Python: pin it before import, not merely in
# the later preflight that calls it.
exact_file(FORMAL_AUTHOR, FORMAL_AUTHOR_SHA256, "formal verifier")
_formal_spec = importlib.util.spec_from_file_location("atomic14_formal", FORMAL_AUTHOR)
require(_formal_spec is not None and _formal_spec.loader is not None, "formal verifier cannot load")
formal = importlib.util.module_from_spec(_formal_spec)
_formal_spec.loader.exec_module(formal)

# Use one repository-wide live-Ghidra mutex, not the historical 515-only name.
guard.MUTEX_NAME = MUTEX_NAME


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def owner_stamp() -> dict[str, object]:
    path = Path(__file__).resolve()
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def relative_stamp(path: Path, root: Path) -> dict[str, object]:
    try:
        return guard.relative_stamp(path, root)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc


def validate_stamp(value: object, root: Path, label: str) -> Path:
    try:
        return guard.validate_relative_stamp(value, root, label)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc


def write_json_new(path: Path, value: object) -> None:
    try:
        guard.write_json_new(path, value)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc


def preflight() -> dict[str, object]:
    require(os.name == "nt", "Atomic14 live promotion is Windows-only")
    require(not ctypes.windll.shell32.IsUserAnAdmin(), "Atomic14 live promotion must run non-elevated")
    fixed = (
        (FORMAL_AUTHOR, FORMAL_AUTHOR_SHA256, "formal verifier"),
        (FORMAL_READY, FORMAL_READY_SHA256, "formal READY"),
        (ATOMIC_TOOL, ATOMIC_TOOL_SHA256, "Atomic14 mutator"),
        (BASELINE_MANIFEST, BASELINE_MANIFEST_SHA256, "baseline project manifest"),
        (HEADLESS, HEADLESS_SHA256, "analyzeHeadless"),
        (JAVA, JAVA_SHA256, "Java"),
        (PYTHON, PYTHON_SHA256, "Python"),
        (INVENTORY_TOOL, INVENTORY_TOOL_SHA256, "inventory tool"),
        (SYMBOL_TOOL, SYMBOL_TOOL_SHA256, "symbol tool"),
        (STRING_TOOL, STRING_TOOL_SHA256, "string tool"),
        (BACKUP_TOOL, BACKUP_TOOL_SHA256, "backup tool"),
        (GUARD_TOOL, GUARD_TOOL_SHA256, "live guard"),
    )
    for path, digest, label in fixed:
        exact_file(path, digest, label)
    for path, digest in GUARD_DEPENDENCIES.items():
        exact_file(path, digest, f"live guard dependency {path.name}")
    formal.preflight()
    formal_receipt = json.loads(FORMAL_READY.read_text(encoding="utf-8"))
    formal.validate_formal_receipt(formal_receipt)
    baseline_snapshot = guard.project_snapshot(BASELINE_PROJECT)
    require(baseline_snapshot["fileCount"] == 19, "baseline project file count differs")
    require(baseline_snapshot["totalBytes"] == 186207109, "baseline project bytes differ")
    require(baseline_snapshot["fileSetSha256"] == BASELINE_FILESET_SHA256,
            "baseline project fileset differs")
    baseline_manifest = json.loads(BASELINE_MANIFEST.read_text(encoding="utf-8"))
    destination = baseline_manifest.get("destination", {})
    manifest_files = [
        {"path": row.get("relative_path"), "bytes": row.get("size"), "sha256": row.get("sha256")}
        for row in destination.get("files", [])
    ]
    require(
        destination.get("projectName") == PROJECT_NAME
        and destination.get("structurallyComplete") is True
        and destination.get("fileCount") == 19
        and destination.get("totalBytes") == 186207109
        and manifest_files == baseline_snapshot["files"]
        and baseline_manifest.get("sourceStable") is True
        and baseline_manifest.get("copyComparison", {}).get("matches") is True,
        "baseline manifest does not exactly bind the baseline project files",
    )
    return {
        "formalReady": {"path": str(FORMAL_READY), "sha256": FORMAL_READY_SHA256},
        "formalAuthor": {"path": str(FORMAL_AUTHOR), "sha256": FORMAL_AUTHOR_SHA256},
        "baselineManifest": {"path": str(BASELINE_MANIFEST), "sha256": BASELINE_MANIFEST_SHA256},
        "baselineProject": baseline_snapshot,
        "owner": owner_stamp(),
    }


def environment_for(root: Path) -> tuple[dict[str, str], Path]:
    try:
        return guard.environment_for(root, SimpleNamespace(java=JAVA))
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc


def clean_process(process: Mapping[str, object], text: str, label: str) -> None:
    try:
        guard.require_success(process, label)
    except ValueError as exc:
        raise PromotionError(str(exc)) from exc
    require("REPORT SCRIPT ERROR" not in text, f"{label} reported a script error")
    require("ATOMIC14_MUTATION_TAINTED" not in text, f"{label} reported mutation taint")


def validate_process_stamp(value: object, root: Path, label: str) -> dict[str, object]:
    try:
        return guard.validate_process_receipt(value, root, label)
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc


def run_process(
    root: Path,
    run_id: str,
    argv: list[str],
    cwd: Path,
    environment: dict[str, str],
    *,
    timeout: int = 600,
) -> tuple[dict[str, object], str]:
    try:
        return guard.run_contained(
            session_root=root,
            run_id=run_id,
            argv=argv,
            cwd=cwd,
            environment=environment,
            timeout_seconds=timeout,
        )
    except (ValueError, OSError) as exc:
        raise PromotionError(str(exc)) from exc


def batch_argv(arguments: list[str]) -> list[str]:
    return guard.envelope.windows_batch_argv(HEADLESS, arguments)


def run_formal_verifier(
    root: Path, run_id: str, cwd: Path, environment: dict[str, str]
) -> dict[str, object]:
    process, text = run_process(
        root,
        run_id,
        [str(PYTHON), "-I", "-B", str(FORMAL_AUTHOR), "verify"],
        cwd,
        environment,
        timeout=120,
    )
    clean_process(process, text, run_id)
    require(text.strip() == FORMAL_VERIFY_LINE, f"{run_id} formal-verifier output differs")
    return {"process": process["receipt"], "output": FORMAL_VERIFY_LINE}


def validate_formal_verification(
    value: Mapping[str, object], root: Path, label: str
) -> None:
    require(value.get("output") == FORMAL_VERIFY_LINE, f"{label} recorded output differs")
    process = validate_process_stamp(value.get("process"), root, f"{label} process")
    expected_argv = [str(PYTHON), "-I", "-B", str(FORMAL_AUTHOR), "verify"]
    require(process.get("argv") == expected_argv, f"{label} argv differs")
    log = root / process["log"]["path"]
    require(log.read_text(encoding="utf-8").strip() == FORMAL_VERIFY_LINE,
            f"{label} log output differs")


def run_inventory(
    project: Path,
    root: Path,
    run_id: str,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    run_root = root / "runs" / run_id
    functions = run_root / "functions.tsv"
    program = run_root / "program.tsv"
    argv = batch_argv([
        str(project.resolve()), PROJECT_NAME, "-process", PROGRAM_NAME,
        "-readOnly", "-noanalysis", "-scriptPath", str(INVENTORY_TOOL.parent),
        "-postScript", INVENTORY_TOOL.name, str(functions), str(program),
    ])
    process, text = run_process(root, run_id, argv, cwd, environment)
    clean_process(process, text, run_id)
    require("INVENTORY_OK" in text, f"{run_id} inventory marker is absent")
    require(functions.is_file() and program.is_file(), f"{run_id} inventory outputs are absent")
    return {
        "functions": relative_stamp(functions, root),
        "program": relative_stamp(program, root),
        "process": process["receipt"],
    }


def inventory_paths(value: Mapping[str, object], root: Path, label: str) -> dict[str, Path]:
    return {
        "functions": validate_stamp(value.get("functions"), root, f"{label} functions"),
        "program": validate_stamp(value.get("program"), root, f"{label} program"),
    }


def classify_inventory(value: Mapping[str, object], root: Path, label: str) -> ProjectState:
    paths = inventory_paths(value, root, label)
    function_hash = sha256_file(paths["functions"])
    program_hash = sha256_file(paths["program"])
    if (
        function_hash == formal.BASE_FUNCTIONS_SHA256
        and program_hash == formal.BASE_PROGRAM_SHA256
    ):
        formal.validate_baseline({**paths, "log": paths["functions"]}, label)
        return ProjectState.PRE
    reference = formal_receipt()["replicas"][0]["post"]
    expected_functions = str(reference["functions"]["sha256"])
    expected_program = str(reference["program"]["sha256"])
    if function_hash == expected_functions and program_hash == expected_program:
        formal.validate_post_inventory({**paths, "log": paths["functions"]}, label)
        return ProjectState.POST
    return ProjectState.UNKNOWN


def run_derived_symbol(
    project: Path,
    root: Path,
    run_id: str,
    state: str,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    run_root = root / "runs" / run_id
    output = run_root / "derived-symbol.tsv"
    ready = run_root / "derived-symbol.ready.json"
    argv = batch_argv([
        str(project.resolve()), PROJECT_NAME, "-process", PROGRAM_NAME,
        "-readOnly", "-noanalysis", "-scriptPath", str(SYMBOL_TOOL.parent),
        "-postScript", SYMBOL_TOOL.name, str(formal.DERIVED_SYMBOL_MANIFEST),
        formal.DERIVED_SYMBOL_MANIFEST_SHA256, "1", str(output), str(ready),
    ])
    process, text = run_process(root, run_id, argv, cwd, environment)
    clean_process(process, text, run_id)
    require(output.is_file() and ready.is_file(), f"{run_id} derived-symbol outputs are absent")
    formal.validate_derived_symbol(output, ready, state, run_id)
    return {
        "output": relative_stamp(output, root),
        "ready": relative_stamp(ready, root),
        "process": process["receipt"],
    }


def run_atomic_readback(
    project: Path,
    root: Path,
    run_id: str,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    run_root = root / "runs" / run_id
    output = run_root / "atomic14.tsv"
    ready = run_root / "atomic14.ready.json"
    argv = atomic_argv(project, output, ready, "readback")
    process, text = run_process(root, run_id, argv, cwd, environment)
    clean_process(process, text, run_id)
    marker = formal.atomic_success_marker("readback")
    require(marker in text, f"{run_id} Atomic14 readback marker is absent")
    require(output.is_file() and ready.is_file(), f"{run_id} Atomic14 outputs are absent")
    formal.validate_atomic(output, ready, "readback")
    execution = execution_record(process, text, "readback")
    formal.validate_atomic_execution(execution, root / process["log"]["path"], "readback", run_id)
    return {
        "output": relative_stamp(output, root),
        "ready": relative_stamp(ready, root),
        "process": process["receipt"],
        "execution": execution,
    }


def run_symbols(
    project: Path,
    root: Path,
    run_id: str,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    run_root = root / "runs" / run_id
    output = run_root / "target-symbols.tsv"
    ready = run_root / "target-symbols.ready.json"
    argv = batch_argv([
        str(project.resolve()), PROJECT_NAME, "-process", PROGRAM_NAME,
        "-readOnly", "-noanalysis", "-scriptPath", str(SYMBOL_TOOL.parent),
        "-postScript", SYMBOL_TOOL.name, str(formal.COMBINED), formal.COMBINED_SHA256,
        "14", str(output), str(ready),
    ])
    process, text = run_process(root, run_id, argv, cwd, environment)
    clean_process(process, text, run_id)
    require(output.is_file() and ready.is_file(), f"{run_id} target-symbol outputs are absent")
    formal.validate_symbols(output, ready, run_id)
    return {
        "output": relative_stamp(output, root),
        "ready": relative_stamp(ready, root),
        "process": process["receipt"],
    }


def run_strings(
    project: Path,
    root: Path,
    run_id: str,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    run_root = root / "runs" / run_id
    output = run_root / "defined-strings.tsv"
    ready = run_root / "defined-strings.ready.json"
    argv = batch_argv([
        str(project.resolve()), PROJECT_NAME, "-process", PROGRAM_NAME,
        "-readOnly", "-noanalysis", "-scriptPath", str(STRING_TOOL.parent),
        "-postScript", STRING_TOOL.name, str(output), str(ready), SPECIMEN_SHA256,
    ])
    process, text = run_process(root, run_id, argv, cwd, environment)
    clean_process(process, text, run_id)
    require(output.is_file() and ready.is_file(), f"{run_id} string outputs are absent")
    formal.validate_strings(output, ready, run_id)
    return {
        "output": relative_stamp(output, root),
        "ready": relative_stamp(ready, root),
        "process": process["receipt"],
    }


def formal_receipt() -> dict[str, object]:
    receipt = json.loads(FORMAL_READY.read_text(encoding="utf-8"))
    formal.validate_formal_receipt(receipt)
    return receipt


def reference_path(group: str, artifact: str) -> Path:
    value = formal_receipt()["replicas"][0][group][artifact]
    path = REPO / str(value["path"])
    return exact_file(path, str(value["sha256"]), f"formal reference {group}/{artifact}")


def require_reference_bytes(path: Path, group: str, artifact: str, label: str) -> None:
    reference = reference_path(group, artifact)
    require(path.read_bytes() == reference.read_bytes(), f"{label} differs from both formal replicas")


def observe_pre(
    project: Path,
    root: Path,
    label: str,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    guard.assert_quiescent(project)
    before = guard.project_snapshot(project)
    inventory = run_inventory(project, root, f"{label}-inventory", cwd, environment)
    require(classify_inventory(inventory, root, label) == ProjectState.PRE, f"{label} is not exact PRE")
    derived = run_derived_symbol(project, root, f"{label}-derived", "pre", cwd, environment)
    after = guard.project_snapshot(project)
    require(guard.same_project_snapshot(before, after), f"{label} changed during read-only observation")
    guard.assert_quiescent(project)
    return {
        "schema": OBSERVATION_SCHEMA,
        "state": ProjectState.PRE,
        "projectRoot": str(project.resolve()),
        "rawBefore": before,
        "rawAfter": after,
        "inventory": inventory,
        "derivedSymbol": derived,
    }


def observe_post(
    project: Path,
    root: Path,
    label: str,
    cwd: Path,
    environment: dict[str, str],
    *,
    apply_ready: Path | None = None,
) -> dict[str, object]:
    guard.assert_quiescent(project)
    before = guard.project_snapshot(project)
    readback = run_atomic_readback(project, root, f"{label}-readback", cwd, environment)
    inventory = run_inventory(project, root, f"{label}-inventory", cwd, environment)
    require(classify_inventory(inventory, root, label) == ProjectState.POST, f"{label} is not exact POST")
    symbols = run_symbols(project, root, f"{label}-symbols", cwd, environment)
    derived = run_derived_symbol(project, root, f"{label}-derived", "post", cwd, environment)
    strings = run_strings(project, root, f"{label}-strings", cwd, environment)
    readback_output = validate_stamp(readback["output"], root, f"{label} readback output")
    inventory_paths_value = inventory_paths(inventory, root, f"{label} inventory")
    symbols_output = validate_stamp(symbols["output"], root, f"{label} symbols output")
    derived_output = validate_stamp(derived["output"], root, f"{label} derived output")
    strings_output = validate_stamp(strings["output"], root, f"{label} strings output")
    require_reference_bytes(readback_output, "readback", "output", f"{label} readback")
    require_reference_bytes(inventory_paths_value["functions"], "post", "functions", f"{label} functions")
    require_reference_bytes(inventory_paths_value["program"], "post", "program", f"{label} program")
    require_reference_bytes(symbols_output, "symbols", "output", f"{label} symbols")
    require_reference_bytes(derived_output, "derivedSymbolPost", "output", f"{label} derived symbol")
    require_reference_bytes(strings_output, "strings", "output", f"{label} strings")
    readback_ready = validate_stamp(readback["ready"], root, f"{label} readback READY")
    if apply_ready is not None:
        formal.validate_apply_readback_binding(apply_ready, readback_ready, label)
    after = guard.project_snapshot(project)
    require(guard.same_project_snapshot(before, after), f"{label} changed during read-only observation")
    guard.assert_quiescent(project)
    return {
        "schema": OBSERVATION_SCHEMA,
        "state": ProjectState.POST,
        "projectRoot": str(project.resolve()),
        "rawBefore": before,
        "rawAfter": after,
        "readback": readback,
        "inventory": inventory,
        "symbols": symbols,
        "derivedSymbol": derived,
        "strings": strings,
    }


def run_copy(
    root: Path,
    run_id: str,
    source: Path,
    destination: Path,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    require(not destination.exists(), f"{run_id} destination already exists")
    argv = [
        str(PYTHON), "-I", "-B", str(BACKUP_TOOL), "copy",
        str(source.resolve()), str(destination.resolve()), "--project-name", PROJECT_NAME,
    ]
    process, text = run_process(root, run_id, argv, cwd, environment, timeout=240)
    clean_process(process, text, run_id)
    require("HashDiffCount=0" in text, f"{run_id} copy verification marker is absent")
    manifest = destination / "backup_manifest.json"
    require(manifest.is_file(), f"{run_id} backup manifest is absent")
    return {"process": process["receipt"], "manifest": relative_stamp(manifest, root)}


def copy_and_drill(
    root: Path,
    label: str,
    source: Path,
    backup_root: Path,
    restore_root: Path,
    state: ProjectState,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    guard.assert_quiescent(source)
    source_before = guard.project_snapshot(source)
    backup_copy = run_copy(root, f"{label}-backup-copy", source, backup_root, cwd, environment)
    backup_snapshot = guard.project_snapshot(backup_root)
    require(guard.same_project_snapshot(source_before, backup_snapshot), f"{label} backup bytes differ")
    guard.require_disjoint_project_files(source, backup_root)
    backup_observation = (
        observe_pre(backup_root, root, f"{label}-backup", cwd, environment)
        if state == ProjectState.PRE
        else observe_post(backup_root, root, f"{label}-backup", cwd, environment)
    )
    restore_copy = run_copy(root, f"{label}-restore-copy", backup_root, restore_root, cwd, environment)
    restore_snapshot = guard.project_snapshot(restore_root)
    require(guard.same_project_snapshot(source_before, restore_snapshot), f"{label} restore-drill bytes differ")
    guard.require_disjoint_project_files(source, restore_root)
    guard.require_disjoint_project_files(backup_root, restore_root)
    restore_observation = (
        observe_pre(restore_root, root, f"{label}-restore", cwd, environment)
        if state == ProjectState.PRE
        else observe_post(restore_root, root, f"{label}-restore", cwd, environment)
    )
    source_after = guard.project_snapshot(source)
    require(guard.same_project_snapshot(source_before, source_after), f"{label} source changed during backup drill")
    return {
        "state": state,
        "sourceRoot": str(source.resolve()),
        "backupRoot": str(backup_root.resolve()),
        "restoreRoot": str(restore_root.resolve()),
        "sourceSnapshot": source_before,
        "backupSnapshot": backup_snapshot,
        "restoreSnapshot": restore_snapshot,
        "backupCopy": backup_copy,
        "restoreCopy": restore_copy,
        "backupObservation": backup_observation,
        "restoreObservation": restore_observation,
    }


def validate_pre_observation(value: Mapping[str, object], root: Path, label: str) -> None:
    require(value.get("schema") == OBSERVATION_SCHEMA, f"{label} schema differs")
    require(value.get("state") == ProjectState.PRE, f"{label} state differs")
    inventory = value.get("inventory")
    derived = value.get("derivedSymbol")
    require(isinstance(inventory, dict) and isinstance(derived, dict), f"{label} artifacts are absent")
    before = value.get("rawBefore")
    after = value.get("rawAfter")
    require(isinstance(before, dict) and isinstance(after, dict), f"{label} raw snapshots are absent")
    require(guard.same_project_snapshot(before, after), f"{label} raw snapshots differ")
    validate_process_stamp(inventory.get("process"), root, f"{label} inventory process")
    validate_process_stamp(derived.get("process"), root, f"{label} derived process")
    paths = inventory_paths(inventory, root, label)
    formal.validate_baseline({**paths, "log": paths["functions"]}, label)
    derived_output = validate_stamp(derived.get("output"), root, f"{label} derived output")
    derived_ready = validate_stamp(derived.get("ready"), root, f"{label} derived READY")
    formal.validate_derived_symbol(derived_output, derived_ready, "pre", label)


def validate_copy_payload(value: Mapping[str, object], root: Path, label: str) -> None:
    state = ProjectState(str(value.get("state")))
    source = Path(str(value.get("sourceRoot")))
    backup = Path(str(value.get("backupRoot")))
    restore = Path(str(value.get("restoreRoot")))
    require(len({str(source.resolve()), str(backup.resolve()), str(restore.resolve())}) == 3,
            f"{label} roots are not disjoint")
    source_snapshot = value.get("sourceSnapshot")
    backup_snapshot = guard.validate_project_snapshot(value.get("backupSnapshot"), backup, f"{label} backup")
    restore_snapshot = guard.validate_project_snapshot(value.get("restoreSnapshot"), restore, f"{label} restore")
    require(isinstance(source_snapshot, dict), f"{label} source snapshot is absent")
    require(source_snapshot.get("root") == str(source.resolve()),
            f"{label} source snapshot root differs")
    require(guard.same_project_snapshot(source_snapshot, backup_snapshot), f"{label} backup snapshot differs")
    require(guard.same_project_snapshot(source_snapshot, restore_snapshot), f"{label} restore snapshot differs")
    guard.require_disjoint_project_files(source, backup)
    guard.require_disjoint_project_files(source, restore)
    guard.require_disjoint_project_files(backup, restore)
    for copy_name in ("backupCopy", "restoreCopy"):
        copy_value = value.get(copy_name)
        require(isinstance(copy_value, dict), f"{label} {copy_name} is absent")
        validate_stamp(copy_value.get("manifest"), root, f"{label} {copy_name} manifest")
        validate_process_stamp(copy_value.get("process"), root, f"{label} {copy_name} process")
    if state == ProjectState.PRE:
        validate_pre_observation(value["backupObservation"], root, f"{label} backup observation")
        validate_pre_observation(value["restoreObservation"], root, f"{label} restore observation")
    else:
        validate_post_observation(value["backupObservation"], root, f"{label} backup observation")
        validate_post_observation(value["restoreObservation"], root, f"{label} restore observation")
    backup_observation = value["backupObservation"]
    restore_observation = value["restoreObservation"]
    require(backup_observation.get("projectRoot") == str(backup.resolve()),
            f"{label} backup observation root differs")
    require(restore_observation.get("projectRoot") == str(restore.resolve()),
            f"{label} restore observation root differs")
    require(backup_observation.get("rawAfter") == backup_snapshot,
            f"{label} backup observation bytes differ from backup snapshot")
    require(restore_observation.get("rawAfter") == restore_snapshot,
            f"{label} restore observation bytes differ from restore snapshot")


def validate_post_observation(value: Mapping[str, object], root: Path, label: str) -> None:
    require(value.get("schema") == OBSERVATION_SCHEMA, f"{label} schema differs")
    require(value.get("state") == ProjectState.POST, f"{label} state differs")
    readback = value.get("readback")
    inventory = value.get("inventory")
    symbols = value.get("symbols")
    derived = value.get("derivedSymbol")
    strings = value.get("strings")
    require(all(isinstance(v, dict) for v in (readback, inventory, symbols, derived, strings)),
            f"{label} artifacts are absent")
    before = value.get("rawBefore")
    after = value.get("rawAfter")
    require(isinstance(before, dict) and isinstance(after, dict), f"{label} raw snapshots are absent")
    require(guard.same_project_snapshot(before, after), f"{label} raw snapshots differ")
    for process_value, process_label in (
        (readback.get("process"), "readback"),
        (inventory.get("process"), "inventory"),
        (symbols.get("process"), "symbols"),
        (derived.get("process"), "derived"),
        (strings.get("process"), "strings"),
    ):
        validate_process_stamp(process_value, root, f"{label} {process_label} process")
    readback_output = validate_stamp(readback["output"], root, f"{label} readback output")
    readback_ready = validate_stamp(readback["ready"], root, f"{label} readback READY")
    formal.validate_atomic(readback_output, readback_ready, "readback")
    readback_process = validate_process_stamp(
        readback["process"], root, f"{label} readback execution process"
    )
    readback_log = root / readback_process["log"]["path"]
    formal.validate_atomic_execution(
        readback.get("execution", {}), readback_log, "readback", label
    )
    paths = inventory_paths(inventory, root, label)
    formal.validate_post_inventory({**paths, "log": paths["functions"]}, label)
    symbol_output = validate_stamp(symbols["output"], root, f"{label} symbol output")
    symbol_ready = validate_stamp(symbols["ready"], root, f"{label} symbol READY")
    formal.validate_symbols(symbol_output, symbol_ready, label)
    derived_output = validate_stamp(derived["output"], root, f"{label} derived output")
    derived_ready = validate_stamp(derived["ready"], root, f"{label} derived READY")
    formal.validate_derived_symbol(derived_output, derived_ready, "post", label)
    strings_output = validate_stamp(strings["output"], root, f"{label} strings output")
    strings_ready = validate_stamp(strings["ready"], root, f"{label} strings READY")
    formal.validate_strings(strings_output, strings_ready, label)
    for path, group, artifact in (
        (readback_output, "readback", "output"),
        (paths["functions"], "post", "functions"),
        (paths["program"], "post", "program"),
        (symbol_output, "symbols", "output"),
        (derived_output, "derivedSymbolPost", "output"),
        (strings_output, "strings", "output"),
    ):
        require_reference_bytes(path, group, artifact, f"{label} {group}/{artifact}")


def prepare(owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    require(not owner_root.exists(), f"Atomic14 owner root already exists: {owner_root}")
    with guard.acquire_mutex() as lease:
        authority = preflight()
        first_quiescence = guard.assert_quiescent(LIVE_PROJECT)
        owner_root.mkdir(parents=True)
        environment, cwd = environment_for(owner_root)
        verifier = run_formal_verifier(owner_root, "formal-verify", cwd, environment)
        baseline = guard.project_snapshot(BASELINE_PROJECT)
        live_before = guard.project_snapshot(LIVE_PROJECT)
        require(guard.same_project_snapshot(baseline, live_before),
                "maintainer project differs from the frozen 8,110-function baseline")
        initial = observe_pre(LIVE_PROJECT, owner_root, "live-pre-initial", cwd, environment)
        backup = copy_and_drill(
            owner_root,
            "pre-live",
            LIVE_PROJECT,
            owner_root / "backups/pre-live",
            owner_root / "backups/pre-live-restore-drill",
            ProjectState.PRE,
            cwd,
            environment,
        )
        final = observe_pre(LIVE_PROJECT, owner_root, "live-pre-final", cwd, environment)
        require(guard.same_project_snapshot(live_before, final["rawAfter"]),
                "maintainer PRE project changed during preparation")
        final_quiescence = guard.assert_quiescent(LIVE_PROJECT)
        ready = {
            "schema": PREPARED_SCHEMA,
            "status": "READY",
            "preparedAtUtc": utc_now(),
            "owner": owner_stamp(),
            "mutex": {"name": lease.name, "abandoned": lease.abandoned},
            "authority": authority,
            "formalVerification": verifier,
            "firstQuiescence": first_quiescence,
            "finalQuiescence": final_quiescence,
            "livePreimage": live_before,
            "initialObservation": initial,
            "finalObservation": final,
            "preBackup": backup,
            "policies": [
                "Preparation spawned no mutating Ghidra process.",
                "Promotion may spawn the fixed Atomic14 mutator exactly once.",
                "An immutable apply intent forbids every retry.",
                "No automatic restore is authorized for PRE, POST, or UNKNOWN.",
                "This boundary proof authorizes no semantic promotion.",
            ],
        }
        ready_path = owner_root / "prepared.ready.json"
        write_json_new(ready_path, ready)
        return {**ready, "ready": str(ready_path), "readySha256": sha256_file(ready_path)}


def load_prepared(owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    ready_path = plain_single_file(owner_root / "prepared.ready.json", "prepared READY")
    ready = json.loads(ready_path.read_text(encoding="utf-8"))
    require(ready.get("schema") == PREPARED_SCHEMA and ready.get("status") == "READY",
            "prepared READY identity differs")
    require(ready.get("owner") == owner_stamp(), "prepared owner identity differs")
    require(ready.get("mutex") == {"name": MUTEX_NAME, "abandoned": False},
            "prepared mutex identity differs")
    authority = preflight()
    require(ready.get("authority") == authority, "prepared authority differs")
    verify = ready.get("formalVerification")
    require(isinstance(verify, dict), "prepared formal verification is absent")
    validate_formal_verification(verify, owner_root, "prepared formal verifier")
    validate_pre_observation(ready["initialObservation"], owner_root, "prepared initial")
    validate_pre_observation(ready["finalObservation"], owner_root, "prepared final")
    validate_copy_payload(ready["preBackup"], owner_root, "prepared PRE backup")
    baseline = guard.project_snapshot(BASELINE_PROJECT)
    require(guard.same_project_snapshot(ready["livePreimage"], baseline),
            "prepared live preimage differs from frozen baseline")
    require(ready["livePreimage"].get("root") == str(LIVE_PROJECT.resolve()),
            "prepared live preimage root differs")
    for observation_name in ("initialObservation", "finalObservation"):
        observation = ready[observation_name]
        require(observation.get("projectRoot") == str(LIVE_PROJECT.resolve()),
                f"prepared {observation_name} project root differs")
        require(observation.get("rawBefore") == ready["livePreimage"]
                and observation.get("rawAfter") == ready["livePreimage"],
                f"prepared {observation_name} bytes differ from live preimage")
    pre_backup = ready["preBackup"]
    require(pre_backup.get("sourceRoot") == str(LIVE_PROJECT.resolve()),
            "prepared PRE backup source root differs")
    for snapshot_name in ("sourceSnapshot", "backupSnapshot", "restoreSnapshot"):
        require(guard.same_project_snapshot(
            pre_backup.get(snapshot_name, {}), ready["livePreimage"]
        ), f"prepared PRE {snapshot_name} differs from live preimage")
    return ready


def atomic_argv(project: Path, output: Path, ready: Path, mode: str) -> list[str]:
    arguments = [str(project.resolve()), PROJECT_NAME, "-process", PROGRAM_NAME]
    if mode == "readback":
        arguments.append("-readOnly")
    arguments.extend([
        "-noanalysis", "-scriptPath", str(FORMAL_ROOT), "-postScript", ATOMIC_TOOL.name,
        str(formal.CLEAN), formal.CLEAN_SHA256,
        str(formal.REPAIR), formal.REPAIR_SHA256,
        str(formal.PADDING), formal.PADDING_SHA256,
        str(output), str(ready), mode,
    ])
    return batch_argv(arguments)


def execution_record(process: Mapping[str, object], text: str, mode: str) -> dict[str, object]:
    marker = formal.atomic_success_marker(mode)
    return {
        "wrapperExitCode": process.get("exitCode"),
        "semanticSuccessMarker": marker,
        "semanticSuccessMarkerPresent": marker in text,
        "scriptErrorAbsent": "REPORT SCRIPT ERROR" not in text,
        "mutationTaintAbsent": "ATOMIC14_MUTATION_TAINTED" not in text,
    }


def validate_apply(
    process: Mapping[str, object],
    text: str,
    output: Path,
    ready: Path,
    log: Path,
) -> tuple[dict[str, object], list[str]]:
    reasons: list[str] = []
    execution = execution_record(process, text, "apply")
    try:
        clean_process(process, text, "live apply")
        require(output.is_file() and ready.is_file(), "live apply artifacts are absent")
        formal.validate_atomic(output, ready, "apply")
        formal.validate_atomic_execution(execution, log, "apply", "live apply")
        require_reference_bytes(output, "apply", "output", "live apply output")
    except (ValueError, OSError) as exc:
        reasons.append(str(exc))
    return execution, reasons


def classify_live_after_apply(
    root: Path, cwd: Path, environment: dict[str, str]
) -> tuple[ProjectState, dict[str, object] | None, str]:
    try:
        guard.assert_quiescent(LIVE_PROJECT)
        before = guard.project_snapshot(LIVE_PROJECT)
        inventory = run_inventory(LIVE_PROJECT, root, "live-post-classify", cwd, environment)
        state = classify_inventory(inventory, root, "live post-apply classification")
        after = guard.project_snapshot(LIVE_PROJECT)
        require(guard.same_project_snapshot(before, after),
                "live project changed during post-apply classification")
        return state, {
            "schema": OBSERVATION_SCHEMA,
            "state": state,
            "projectRoot": str(LIVE_PROJECT.resolve()),
            "rawBefore": before,
            "rawAfter": after,
            "inventory": inventory,
        }, ""
    except (ValueError, OSError) as exc:
        return ProjectState.UNKNOWN, None, str(exc)


def promote(owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    promotion_root = owner_root / "promotion"
    require(not promotion_root.exists(), "promotion attempt already exists; use recover-status")
    with guard.acquire_mutex() as lease:
        guard.assert_quiescent(LIVE_PROJECT)
        prepared = load_prepared(owner_root)
        current = guard.project_snapshot(LIVE_PROJECT)
        require(guard.same_project_snapshot(prepared["livePreimage"], current),
                "live project differs from prepared PRE bytes")
        promotion_root.mkdir()
        environment, cwd = environment_for(promotion_root)
        verifier = run_formal_verifier(promotion_root, "formal-verify", cwd, environment)
        live_pre = observe_pre(LIVE_PROJECT, promotion_root, "live-immediate-pre", cwd, environment)
        require(guard.same_project_snapshot(prepared["livePreimage"], live_pre["rawAfter"]),
                "live project differs from prepared PRE after observation")
        pre_backup = prepared["preBackup"]
        pre_backup_recheck = observe_pre(
            Path(pre_backup["backupRoot"]), promotion_root,
            "pre-backup-recheck", cwd, environment
        )
        pre_restore_recheck = observe_pre(
            Path(pre_backup["restoreRoot"]), promotion_root,
            "pre-restore-recheck", cwd, environment
        )

        apply_root = promotion_root / "runs/live-apply"
        output = apply_root / "atomic14.tsv"
        java_ready = apply_root / "atomic14.ready.json"
        argv = atomic_argv(LIVE_PROJECT, output, java_ready, "apply")
        attempt = {
            "schema": ATTEMPT_SCHEMA,
            "startedAtUtc": utc_now(),
            "owner": owner_stamp(),
            "preparedReady": relative_stamp(owner_root / "prepared.ready.json", owner_root),
            "formalReady": {"path": str(FORMAL_READY), "sha256": FORMAL_READY_SHA256},
            "livePreimage": live_pre["rawAfter"],
            "liveImmediatePre": live_pre,
            "preBackupRecheck": pre_backup_recheck,
            "preRestoreRecheck": pre_restore_recheck,
            "argv": argv,
            "mutationSpawnLimit": 1,
            "retryAuthorized": False,
            "automaticRestoreAuthorized": False,
            "mutex": {"name": lease.name, "abandoned": lease.abandoned},
        }
        intent_path = promotion_root / "attempt.started.json"
        write_json_new(intent_path, attempt)
        guard.assert_quiescent(LIVE_PROJECT)
        process, text = run_process(
            promotion_root, "live-apply", argv, cwd, environment, timeout=900
        )
        log = promotion_root / process["log"]["path"]
        execution, protocol_reasons = validate_apply(process, text, output, java_ready, log)

        state, classification, classification_error = classify_live_after_apply(
            promotion_root, cwd, environment
        )
        post_observation: dict[str, object] | None = None
        post_error = ""
        if state == ProjectState.POST:
            try:
                post_observation = observe_post(
                    LIVE_PROJECT,
                    promotion_root,
                    "live-post",
                    cwd,
                    environment,
                    apply_ready=java_ready if java_ready.is_file() else None,
                )
            except (ValueError, OSError) as exc:
                post_error = str(exc)
        elif state == ProjectState.PRE:
            try:
                observe_pre(LIVE_PROJECT, promotion_root, "live-still-pre", cwd, environment)
            except (ValueError, OSError) as exc:
                post_error = str(exc)

        post_backup: dict[str, object] | None = None
        post_backup_error = ""
        if state == ProjectState.POST and post_observation is not None:
            try:
                post_backup = copy_and_drill(
                    promotion_root,
                    "post-live",
                    LIVE_PROJECT,
                    promotion_root / "backups/post-live",
                    promotion_root / "backups/post-live-restore-drill",
                    ProjectState.POST,
                    cwd,
                    environment,
                )
            except (ValueError, OSError) as exc:
                post_backup_error = str(exc)

        protocol = {
            "status": "COMPLETE" if not protocol_reasons else "PARTIAL",
            "reasons": protocol_reasons,
            "execution": execution,
            "output": relative_stamp(output, promotion_root) if output.is_file() else None,
            "ready": relative_stamp(java_ready, promotion_root) if java_ready.is_file() else None,
        }
        publish = bool(
            state == ProjectState.POST
            and protocol["status"] == "COMPLETE"
            and post_observation is not None
            and not post_error
            and post_backup is not None
            and not post_backup_error
        )
        result = {
            "schema": SCHEMA,
            "completedAtUtc": utc_now(),
            "state": state,
            "owner": owner_stamp(),
            "formalVerification": verifier,
            "attempt": relative_stamp(intent_path, promotion_root),
            "process": process["receipt"],
            "protocol": protocol,
            "classification": classification,
            "classificationError": classification_error,
            "postObservation": post_observation,
            "postObservationError": post_error,
            "postBackup": post_backup,
            "postBackupError": post_backup_error,
            "mutationSpawns": 1,
            "retryAuthorized": False,
            "automaticRestorePerformed": False,
            "semanticPromotionApplied": False,
            "campaignPublicationAuthorized": publish,
        }
        if publish:
            validate_promotion_payload(result, owner_root)
        result_path = promotion_root / "promotion.result.json"
        write_json_new(result_path, result)
        if publish:
            frozen_result = json.loads(result_path.read_text(encoding="utf-8"))
            require(frozen_result == result, "frozen promotion result differs from validated result")
            validate_promotion_payload(frozen_result, owner_root)
            ready_payload = {
                **frozen_result,
                "status": "READY",
                "result": relative_stamp(result_path, promotion_root),
            }
            ready_path = promotion_root / "promotion.ready.json"
            write_json_new(ready_path, ready_payload)
            result["ready"] = str(ready_path)
            result["readySha256"] = sha256_file(ready_path)
        return result


def recover_status(owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    recovery_root = owner_root / "recoveries" / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    )
    recovery_root.mkdir(parents=True)
    state = ProjectState.UNKNOWN
    observation: dict[str, object] | None = None
    error = ""
    mutex: dict[str, object] = {"name": MUTEX_NAME, "abandoned": None}
    try:
        with guard.acquire_mutex(allow_abandoned=True) as lease:
            mutex = {"name": lease.name, "abandoned": lease.abandoned}
            preflight()
            environment, cwd = environment_for(recovery_root)
            guard.assert_quiescent(LIVE_PROJECT)
            inventory = run_inventory(LIVE_PROJECT, recovery_root, "live-recovery", cwd, environment)
            state = classify_inventory(inventory, recovery_root, "live recovery")
            observation = {
                "state": state,
                "inventory": inventory,
                "raw": guard.project_snapshot(LIVE_PROJECT),
            }
            if state == ProjectState.POST:
                observation["post"] = observe_post(
                    LIVE_PROJECT, recovery_root, "live-recovery-post", cwd, environment
                )
            elif state == ProjectState.PRE:
                observation["pre"] = run_derived_symbol(
                    LIVE_PROJECT, recovery_root, "live-recovery-pre-derived", "pre", cwd, environment
                )
    except (ValueError, OSError) as exc:
        error = str(exc)
    receipt = {
        "schema": RECOVERY_SCHEMA,
        "observedAtUtc": utc_now(),
        "state": state,
        "mutex": mutex,
        "observation": observation,
        "error": error,
        "attemptExists": (owner_root / "promotion/attempt.started.json").is_file(),
        "resultExists": (owner_root / "promotion/promotion.result.json").is_file(),
        "readyExists": (owner_root / "promotion/promotion.ready.json").is_file(),
        "automaticRestorePerformed": False,
        "retryAuthorized": False,
    }
    path = recovery_root / "recovery.ready.json"
    write_json_new(path, receipt)
    return {**receipt, "receipt": str(path), "receiptSha256": sha256_file(path)}


def validate_mutation_census(owner_root: Path) -> None:
    prepare_mutators: list[Path] = []
    promotion_mutators: list[Path] = []
    for receipt_path in owner_root.rglob("run.json"):
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        argv = receipt.get("argv", [])
        require(isinstance(argv, list), f"process argv is malformed: {receipt_path}")
        command = " ".join(str(value) for value in argv)
        read_only = re.search(r"(?<!\S)-readOnly(?!\S)", command) is not None
        if "analyzeHeadless.bat" not in command or read_only:
            continue
        if "promotion" in receipt_path.relative_to(owner_root).parts:
            promotion_mutators.append(receipt_path)
        else:
            prepare_mutators.append(receipt_path)
        require(ATOMIC_TOOL.name in command and re.search(r"\bapply\b", command) is not None,
                f"unexpected mutating Ghidra command: {receipt_path}")
    require(not prepare_mutators, "preparation contains a mutating Ghidra process")
    require(len(promotion_mutators) == 1, "promotion mutating-process census differs from one")


def validate_promotion_payload(
    payload: Mapping[str, object], owner_root: Path
) -> dict[str, object]:
    prepared = load_prepared(owner_root)
    promotion_root = owner_root / "promotion"
    require(payload.get("schema") == SCHEMA, "promotion result schema differs")
    require(payload.get("state") == ProjectState.POST, "promotion result state differs")
    require(payload.get("owner") == owner_stamp(), "promotion result owner differs")
    require(re.fullmatch(r"\d{4}-\d{2}-\d{2}T[^\s]+", str(payload.get("completedAtUtc", "")))
            is not None, "promotion completion timestamp differs")
    require(payload.get("mutationSpawns") == 1 and payload.get("retryAuthorized") is False,
            "promotion mutation policy differs")
    require(payload.get("automaticRestorePerformed") is False,
            "promotion restore policy differs")
    require(payload.get("semanticPromotionApplied") is False,
            "promotion improperly claims semantic work")
    require(payload.get("campaignPublicationAuthorized") is True,
            "promotion result does not authorize campaign publication")
    for field in (
        "classificationError", "postObservationError", "postBackupError"
    ):
        require(payload.get(field) == "", f"promotion result retains {field}")
    formal_verification = payload.get("formalVerification")
    require(isinstance(formal_verification, dict), "promotion formal verification is absent")
    validate_formal_verification(
        formal_verification, promotion_root, "promotion-time formal verifier"
    )
    attempt_path = validate_stamp(
        payload.get("attempt"), promotion_root, "published apply intent"
    )
    attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
    require(attempt.get("schema") == ATTEMPT_SCHEMA, "published apply-intent schema differs")
    require(attempt.get("owner") == owner_stamp(), "published apply-intent owner differs")
    require(attempt.get("formalReady") == {"path": str(FORMAL_READY), "sha256": FORMAL_READY_SHA256},
            "published apply-intent formal proof differs")
    require(attempt.get("mutationSpawnLimit") == 1 and attempt.get("retryAuthorized") is False,
            "published apply-intent mutation policy differs")
    require(attempt.get("automaticRestoreAuthorized") is False,
            "published apply-intent restore policy differs")
    validate_stamp(attempt.get("preparedReady"), owner_root, "published prepared READY")
    validate_pre_observation(
        attempt.get("liveImmediatePre", {}), promotion_root, "published immediate PRE"
    )
    validate_pre_observation(
        attempt.get("preBackupRecheck", {}), promotion_root, "published PRE backup recheck"
    )
    validate_pre_observation(
        attempt.get("preRestoreRecheck", {}), promotion_root, "published PRE restore recheck"
    )
    require(attempt.get("livePreimage") == prepared.get("livePreimage"),
            "published apply-intent PRE differs from prepared PRE")
    require(attempt["liveImmediatePre"].get("rawAfter") == prepared.get("livePreimage"),
            "published immediate PRE differs from prepared PRE")
    prepared_backup = prepared.get("preBackup", {})
    require(attempt["preBackupRecheck"].get("rawAfter") == prepared_backup.get("backupSnapshot"),
            "published PRE backup recheck differs from prepared backup")
    require(attempt["preRestoreRecheck"].get("rawAfter") == prepared_backup.get("restoreSnapshot"),
            "published PRE restore recheck differs from prepared restore drill")
    protocol = payload.get("protocol")
    require(isinstance(protocol, dict) and protocol.get("status") == "COMPLETE",
            "promotion protocol is incomplete")
    require(protocol.get("reasons") == [], "promotion protocol retains failure reasons")
    apply_output = validate_stamp(protocol.get("output"), promotion_root, "apply output")
    apply_ready = validate_stamp(protocol.get("ready"), promotion_root, "apply READY")
    formal.validate_atomic(apply_output, apply_ready, "apply")
    require_reference_bytes(apply_output, "apply", "output", "published apply")
    apply_process = validate_process_stamp(
        payload.get("process"), promotion_root, "published apply process"
    )
    expected_apply_argv = atomic_argv(
        LIVE_PROJECT,
        owner_root / "promotion/runs/live-apply/atomic14.tsv",
        owner_root / "promotion/runs/live-apply/atomic14.ready.json",
        "apply",
    )
    require(attempt.get("argv") == expected_apply_argv,
            "published apply-intent argv differs from the fixed mutator")
    require(apply_process.get("argv") == expected_apply_argv,
            "published apply process argv differs from its immutable intent")
    apply_log = promotion_root / apply_process["log"]["path"]
    formal.validate_atomic_execution(
        protocol.get("execution", {}), apply_log, "apply", "published live apply"
    )
    classification = payload.get("classification")
    require(isinstance(classification, dict), "published POST classification is absent")
    require(classification.get("schema") == OBSERVATION_SCHEMA
            and classification.get("state") == ProjectState.POST,
            "published POST classification differs")
    classification_inventory = classification.get("inventory")
    require(isinstance(classification_inventory, dict), "published classification inventory is absent")
    validate_process_stamp(
        classification_inventory.get("process"), promotion_root,
        "published classification inventory process"
    )
    require(classify_inventory(
        classification_inventory, promotion_root, "published POST classification"
    ) == ProjectState.POST, "published classification does not reproduce POST")
    require(guard.same_project_snapshot(
        classification.get("rawBefore", {}), classification.get("rawAfter", {})
    ), "published classification raw snapshots differ")
    post = payload.get("postObservation")
    require(isinstance(post, dict), "published post observation is absent")
    validate_post_observation(post, promotion_root, "published live POST")
    require(post.get("rawAfter") == classification.get("rawAfter"),
            "published full POST differs from the initial POST classification")
    readback_ready = validate_stamp(
        post["readback"]["ready"], promotion_root, "published readback READY"
    )
    formal.validate_apply_readback_binding(apply_ready, readback_ready, "published live")
    backup = payload.get("postBackup")
    require(isinstance(backup, dict), "published POST backup is absent")
    validate_copy_payload(backup, promotion_root, "published POST backup")
    require(backup.get("sourceSnapshot") == post.get("rawAfter"),
            "published POST backup source differs from live POST")
    validate_mutation_census(owner_root)
    return {
        "state": ProjectState.POST,
        "functions": formal.EXPECTED_FUNCTIONS_POST,
        "formalReadySha256": FORMAL_READY_SHA256,
    }


def verify_artifacts(owner_root: Path = OWNER_ROOT) -> dict[str, object]:
    prepared = load_prepared(owner_root)
    promotion_root = owner_root / "promotion"
    promotion_ready = promotion_root / "promotion.ready.json"
    if not promotion_ready.is_file():
        if promotion_root.exists() or (promotion_root / "attempt.started.json").exists():
            raise PromotionError(
                "promotion was attempted but has no READY; use recover-status and do not retry"
            )
        return {"status": "PREPARED", "preparedAtUtc": prepared["preparedAtUtc"]}
    promotion_ready = plain_single_file(promotion_ready, "promotion READY")
    ready = json.loads(promotion_ready.read_text(encoding="utf-8"))
    require(ready.get("status") == "READY", "promotion READY status differs")
    result_path = validate_stamp(ready.get("result"), promotion_root, "promotion result")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    expected_ready = {**result, "status": "READY", "result": ready.get("result")}
    require(ready == expected_ready, "promotion READY and frozen result differ")
    summary = validate_promotion_payload(result, owner_root)
    return {
        **summary,
        "status": "READY",
        "promotionReadySha256": sha256_file(promotion_ready),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "prepare", "promote", "recover-status", "verify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "preflight":
            result = preflight()
        elif args.command == "prepare":
            result = prepare()
        elif args.command == "promote":
            result = promote()
        elif args.command == "recover-status":
            result = recover_status()
        else:
            result = verify_artifacts()
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
        return 0
    except (PromotionError, ValueError, OSError) as exc:
        print(json.dumps({"status": "REFUSED", "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
