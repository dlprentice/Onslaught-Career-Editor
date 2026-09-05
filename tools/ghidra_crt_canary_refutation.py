#!/usr/bin/env python3
"""Historical owner for the CRT 0x00542710 body-envelope refutation.

The tracked CLI is retired and refusal-only. Database-level replay requires a
catalog-guided restore plus the exact frozen owner sealed with the old READY.

The original CRT boundary proposal preregistered one ten-byte function body.
An address-only disposable-Ghidra run instead created one discontiguous,
32-byte function.  This owner turns that counterexample into a durable result;
it does not authorize the learned two-range body or any live-project mutation.

The historical finalizer reused the frozen v9 promotion runner only as a
library of hardened process, inventory, and preflight helpers.  It never edits
that runner or the address-only Java instrument whose behavior is under test.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
from typing import Any


_BASE_PATH = Path(__file__).resolve().with_name("ghidra_promotion_scratch_proof.py")
_BASE_SPEC = importlib.util.spec_from_file_location(
    "ghidra_promotion_scratch_proof",
    _BASE_PATH,
)
if _BASE_SPEC is None or _BASE_SPEC.loader is None:
    raise RuntimeError(f"cannot load frozen Ghidra proof helper: {_BASE_PATH}")
base = importlib.util.module_from_spec(_BASE_SPEC)
sys.modules[_BASE_SPEC.name] = base
_BASE_SPEC.loader.exec_module(base)


SCHEMA = "bea.re.ghidra-crt-canary-refutation.v1"
STATUS = "READY"
VERDICT = "REFUTED_EXACT_ONE_RESIDUAL_BODY"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
SOURCE_PROOF_READY_SHA256 = "2bd58c84cb0ea907bab22f13cc4bb2a236a403aa12c8409d9c53b7e6b3a62999"
PROPOSAL_READY_SHA256 = "4b7c1c49fa56cf4ea8dcc98430bef78e70dbf3cbda3b001494d2a056d97939dd"
PROPOSAL_MANIFEST_SHA256 = "8921790cf41ec7fbcdf5591c32394692cd48234a9adfe8ecc51220dc025dcd1e"
CANARY_LIST_SHA256 = "69f1ee328e10650bd27b50a20ad56aeb67a8d1d393dee8a78685089b32297c69"
FROZEN_RUNNER_SHA256 = "895405aea9da78f72901250c7edb4e042ec28fadf6fbf9409d83097f8dd228be"
PROMOTION_TOOL_SHA256 = "1c3d6820a7f4d06fe3b08601a0878b4a3ec2acfce7390f32e3105756829bafe9"
INVENTORY_TOOL_SHA256 = "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"
SOURCE_FUNCTIONS_SHA256 = "26977c69e3530ff9344c6456b3a0dac218775eaf0c1043ac2c89c6a9b95ab368"
SOURCE_PROGRAM_SHA256 = "eaf62f346c0c0efebb629bef775f519882bfad0aaa61917929d5fda6805c43ad"
SOURCE_PROJECT_FILESET_SHA256 = "74db2e939d91046114e767334a55582936eb8c791b8ae3572ad3618658e85717"
CANARY_ADDRESS = "0x00542710"
TAIL_ADDRESS = "0x00542720"
EXPECTED_END_EXCLUSIVE = "0x0054271a"
EXPECTED_BYTES = 10
EXPECTED_BYTES_SHA256 = "74fe35a3b08bbfcb8f47c3b11d839c8b8af7c7283b1122b816f3387e2232e19a"
OBSERVED_BODY_BYTES = 32
OBSERVED_BODY_MIN = "0x00542710"
OBSERVED_BODY_MAX = "0x00542735"
OBSERVED_BODY_RANGES = 2
OBSERVED_BODY_RANGE_DIGEST = "f0f8f544b4fc3bdad54cb818a519db949906caf2b798bf0a5cdee84f96f1f2b3"
OBSERVED_BODY_BYTES_SHA256 = "cdc88702c69f4171d35d7aa3d4283ef7f788c74dfe7873783496e7e3572f7356"
OBSERVED_INSTRUCTIONS = 9
BASELINE_FUNCTIONS = 7595
AFTER_FUNCTIONS = 7596
INSTRUCTIONS = 549864
TAIL_ERROR = "target lies inside existing function: 0x00542720 containing=0x00542710"
ROOT = Path(__file__).resolve().parents[1]

DEFAULT_SOURCE_PROOF = ROOT / "local-lab/ghidra-promotion-v2-proof-2026-08-02/frozen-tool-proof-v9-alias-state-bound-v4"
DEFAULT_PROPOSAL = ROOT / "local-lab/crt-recursive-cohort-2026-08-02/clean521-boundary-v2-envelope-bound"
DEFAULT_MANUAL = ROOT / "local-lab/crt-recursive-cohort-2026-08-02/thunk-canary-scratch-v1"
DEFAULT_SPECIMEN = ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
DEFAULT_HEADLESS = Path("D:/ghidra_12.1.2_PUBLIC_20260605/ghidra_12.1.2_PUBLIC/support/analyzeHeadless.bat")
COLD_PACKAGE_PARENT = Path("/srv/archive-a/onslaught-ghidra-cold/codex-consolidated-2026-08-31")
HISTORICAL_RETIREMENT_MESSAGE = (
    "this tracked CRT canary owner is a frozen Windows-era one-shot and its "
    "bound frozen-v9 main project plus retained canary project are no longer "
    "live inputs. Locate their aliases in a package catalog under "
    f"{COLD_PACKAGE_PARENT}, restore every required tree to fresh empty paths, "
    "and execute the exact frozen owner recorded beside the historical READY; "
    "never substitute the active mutable Linux Ghidra project"
)

MANUAL_INPUTS = {
    "manual-copy-manifest.json": ("project/backup_manifest.json", "516f126289ad0ecfd7e73cc4f9c62d0d8340ad6d556c104fae8b8cfcf7c97f11"),
    "baseline-functions.tsv": ("runs/baseline-functions.tsv", SOURCE_FUNCTIONS_SHA256),
    "baseline-program.tsv": ("runs/baseline-program.json", SOURCE_PROGRAM_SHA256),
    "after-functions.tsv": ("runs/after-functions.tsv", "88da149da31062a26ccb1e4fe6e41c304b32df02c1a6a7133392403b676df6d1"),
    "after-program.tsv": ("runs/after-program.json", "162d40fc3e0f35e533aee07114a7cdd3d101e1177a208f62bb018144195b3955"),
    "canary-dry.tsv": ("runs/canary-dry.tsv", "96cf533ad23c2791ea6d36ca10795ddbbaf3090b72d5fd49f77f3024d055a700"),
    "canary-dry.ready.json": ("runs/canary-dry.ready.json", "e1668a8b83529adde55803da1255643bc92f5190d704e0fcc8ae71c36cc13074"),
    "canary-apply.tsv": ("runs/canary-apply.tsv", "6b5eeb938b02d1e327ac582c9b5cec1f36f8a74f1dd00984122fd3febf7e5206"),
    "canary-apply.ready.json": ("runs/canary-apply.ready.json", "da9dc0e6b41dee99880a624ec69ff855930d7c8a2fcd2bde3ea4ed56b46fe2dd"),
    "canary-readback.tsv": ("runs/canary-readback.tsv", "f6eb809597c3ad39aa1cee5f8aa49e1b01fb3ffda0cf1f821560bea211a9316e"),
    "canary-readback.ready.json": ("runs/canary-readback.ready.json", "3d2916514f571d7be29d7bf5439f12e6a341b2be13fb6a35380bdb924d44c242"),
    "inventory-diff.json": ("runs/inventory-diff.json", "02f976f2388f6c1dff2f4cf2b51fb7b2fe1f9dcf5cbf97bd8fbf61524dbbe7f7"),
}


class RefutationError(ValueError):
    """Raised when the counterexample no longer reproduces exactly."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RefutationError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RefutationError(f"cannot read {label}: {path}: {exc}") from exc
    require(isinstance(value, dict), f"{label} is not an object")
    return value


def read_tsv(path: Path, label: str) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise RefutationError(f"cannot read {label}: {path}: {exc}") from exc
    require(reader.fieldnames is not None, f"{label} has no header")
    require(all(None not in row for row in rows), f"{label} has malformed rows")
    return rows


def stamp(path: Path, root: Path) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), f"missing/plain-file failure: {path}")
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def external_stamp(path: Path) -> dict[str, Any]:
    require(path.is_file() and not path.is_symlink(), f"missing/plain-file failure: {path}")
    return {"path": str(path.resolve()), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def write_new(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(content)


def copy_exact(source: Path, destination: Path, expected_sha256: str) -> dict[str, Any]:
    require(source.is_file() and not source.is_symlink(), f"input is not a plain file: {source}")
    require(sha256_file(source) == expected_sha256, f"input hash drift: {source}")
    write_new(destination, source.read_bytes())
    require(sha256_file(destination) == expected_sha256, f"copied input drift: {destination}")
    return stamp(destination, destination.parents[1])


def inventory_map(path: Path, label: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in read_tsv(path, label):
        address = row.get("address", "").lower()
        require(address.startswith("0x") and address not in result, f"{label} duplicate/bad address")
        result[address] = row
    return result


def program_metrics(path: Path, label: str) -> dict[str, str]:
    rows = read_tsv(path, label)
    require(all(set(row) == {"metric", "value"} for row in rows), f"{label} columns drift")
    values = {row["metric"]: row["value"] for row in rows}
    require(len(values) == len(rows), f"{label} duplicate metric")
    return values


def validate_hash(path: Path, expected: str, label: str) -> None:
    require(path.is_file() and not path.is_symlink(), f"missing {label}: {path}")
    require(sha256_file(path) == expected, f"{label} hash drift")


def pe_ranges(specimen: Path, ranges: tuple[tuple[int, int], ...]) -> bytes:
    data = specimen.read_bytes()
    require(sha256_bytes(data) == SPECIMEN_SHA256, "pristine specimen drift")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    require(data[:2] == b"MZ" and data[pe_offset : pe_offset + 4] == b"PE\0\0", "specimen PE header drift")
    count = struct.unpack_from("<H", data, pe_offset + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
    optional = pe_offset + 24
    image_base = struct.unpack_from("<I", data, optional + 28)[0]
    section_table = optional + optional_size
    sections = []
    for index in range(count):
        offset = section_table + index * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", data, offset + 8)
        sections.append((virtual_address, virtual_size, raw_pointer, raw_size))
    output = bytearray()
    for start, end in ranges:
        rva = start - image_base
        length = end - start
        match = None
        for virtual_address, virtual_size, raw_pointer, raw_size in sections:
            if virtual_address <= rva and rva + length <= virtual_address + max(virtual_size, raw_size):
                raw = raw_pointer + rva - virtual_address
                require(raw + length <= raw_pointer + raw_size, "body range escapes raw section")
                match = data[raw : raw + length]
                break
        require(match is not None, "body range is outside specimen sections")
        output.extend(match)
    return bytes(output)


def proposal_row(proposal_root: Path) -> dict[str, Any]:
    ready_path = proposal_root / "boundary-targets.ready.json"
    manifest_path = proposal_root / "boundary-targets.tsv"
    target_path = proposal_root / "canary-targets.txt"
    validate_hash(ready_path, PROPOSAL_READY_SHA256, "proposal READY")
    validate_hash(manifest_path, PROPOSAL_MANIFEST_SHA256, "proposal manifest")
    validate_hash(target_path, CANARY_LIST_SHA256, "canary list")
    require(target_path.read_bytes() == b"0x00542710\n", "canary target bytes drift")
    ready = read_json(ready_path, "proposal READY")
    rows = [row for row in ready.get("targets", []) if isinstance(row, dict) and row.get("address") == CANARY_ADDRESS]
    require(len(rows) == 1, "proposal does not contain one canary row")
    row = rows[0]
    require(
        row.get("endExclusive") == EXPECTED_END_EXCLUSIVE
        and row.get("bytes") == EXPECTED_BYTES
        and row.get("bytesSha256") == EXPECTED_BYTES_SHA256,
        "proposal canary body drift",
    )
    manifest_rows = [row for row in read_tsv(manifest_path, "proposal manifest") if row.get("address") == CANARY_ADDRESS]
    require(len(manifest_rows) == 1, "proposal manifest canary multiplicity drift")
    manifest = manifest_rows[0]
    require(
        manifest.get("endExclusive") == EXPECTED_END_EXCLUSIVE
        and manifest.get("bytes") == str(EXPECTED_BYTES)
        and manifest.get("bytesSha256") == EXPECTED_BYTES_SHA256
        and manifest.get("promotionLane") == "ISOLATED_THUNK_CANARY",
        "proposal manifest row drift",
    )
    return row


def validate_manual_ready(path: Path, mode: str, output: Path, target: Path, tool: Path) -> dict[str, Any]:
    ready = read_json(path, f"manual {mode} READY")
    expected_counts = base.expected_counts(mode, 1)
    counts = ready.get("counts")
    require(isinstance(counts, dict), f"manual {mode} counts missing")
    require(
        ready.get("schemaVersion") == base.READY_SCHEMA
        and ready.get("mode") == mode
        and ready.get("program", {}).get("executableSha256") == SPECIMEN_SHA256
        and ready.get("tool", {}).get("sha256") == PROMOTION_TOOL_SHA256
        and ready.get("tool", {}).get("path") == str(tool.resolve())
        and ready.get("input", {}).get("sha256") == CANARY_LIST_SHA256
        and ready.get("input", {}).get("path") == str(target.resolve())
        and ready.get("input", {}).get("expectedCount") == 1
        and ready.get("input", {}).get("semanticTargetSetSha256") == CANARY_LIST_SHA256
        and Path(str(ready.get("output", {}).get("path", ""))).name == output.name
        and ready.get("output", {}).get("sha256") == sha256_file(output)
        and ready.get("output", {}).get("bytes") == output.stat().st_size
        and all(counts.get(key) == value for key, value in expected_counts.items())
        and counts.get("programInstructionsBefore") == INSTRUCTIONS
        and counts.get("programInstructionsAfter") == INSTRUCTIONS
        and ready.get("namesAuthorized") is False
        and ready.get("mutationCommitted") is (mode == "apply")
        and ready.get("allTargetsVerified") is (mode in {"apply", "readback"}),
        f"manual {mode} READY does not rederive",
    )
    return ready


def claim_boundary() -> list[str]:
    return [
        "One disposable address-only creation falsified the preregistered ten-byte, one-residual body envelope at 0x00542710.",
        "The result does not falsify 0x00542710 as an entry; Ghidra created that entry and naturally inferred a two-range body.",
        "The learned two-range body is retrospective and requires a fresh prospective, replicated proof before promotion.",
        "No live maintainer Ghidra project was opened or mutated by this finalizer; all Ghidra checks are read-only against retained disposable projects.",
    ]


def validate_manual_evidence(inputs: Path, proposal_target: Path, promotion_tool: Path) -> dict[str, Any]:
    baseline_path = inputs / "baseline-functions.tsv"
    after_path = inputs / "after-functions.tsv"
    before = inventory_map(baseline_path, "manual baseline inventory")
    after = inventory_map(after_path, "manual after inventory")
    require(len(before) == BASELINE_FUNCTIONS and len(after) == AFTER_FUNCTIONS, "manual function counts drift")
    require(set(after) - set(before) == {CANARY_ADDRESS} and not (set(before) - set(after)), "manual created/destroyed set drift")
    require(all(after[key] == row for key, row in before.items()), "manual run changed an existing function row")
    created = after[CANARY_ADDRESS]
    require(
        created.get("name") == "FUN_00542710"
        and created.get("nameSource") == "DEFAULT"
        and created.get("bodyBytes") == str(OBSERVED_BODY_BYTES)
        and created.get("bodyMin") == OBSERVED_BODY_MIN
        and created.get("bodyMax") == OBSERVED_BODY_MAX
        and created.get("bodyRanges") == str(OBSERVED_BODY_RANGES)
        and created.get("bodyDigest") == OBSERVED_BODY_RANGE_DIGEST
        and created.get("instrCount") == str(OBSERVED_INSTRUCTIONS)
        and created.get("isThunk") == "false",
        "manual created function envelope drift",
    )
    require(TAIL_ADDRESS not in after, "weak tail unexpectedly became a separate function")
    before_metrics = program_metrics(inputs / "baseline-program.tsv", "manual baseline program")
    after_metrics = program_metrics(inputs / "after-program.tsv", "manual after program")
    require(before_metrics.get("functions") == str(BASELINE_FUNCTIONS), "manual baseline program function count drift")
    require(after_metrics.get("functions") == str(AFTER_FUNCTIONS), "manual after program function count drift")
    require(before_metrics.get("instructions") == str(INSTRUCTIONS) == after_metrics.get("instructions"), "instruction count drift")
    changed_metrics = {key for key in before_metrics if before_metrics.get(key) != after_metrics.get(key)}
    require(set(before_metrics) == set(after_metrics) and changed_metrics == {"functions"}, "manual program delta exceeds function count")
    dry_rows = read_tsv(inputs / "canary-dry.tsv", "manual dry ledger")
    apply_rows = read_tsv(inputs / "canary-apply.tsv", "manual apply ledger")
    readback_rows = read_tsv(inputs / "canary-readback.tsv", "manual readback ledger")
    require(len(dry_rows) == len(apply_rows) == len(readback_rows) == 1, "manual ledgers are not one-target")
    require(dry_rows[0].get("address") == CANARY_ADDRESS and dry_rows[0].get("status") == "would_create", "manual dry row drift")
    require(apply_rows[0].get("address") == CANARY_ADDRESS and apply_rows[0].get("status") == "created", "manual apply row drift")
    require(readback_rows[0].get("address") == CANARY_ADDRESS and readback_rows[0].get("status") == "verified", "manual readback row drift")
    for field, value in {
        "name": "FUN_00542710",
        "nameSource": "DEFAULT",
        "bodyBytes": str(OBSERVED_BODY_BYTES),
        "bodyMin": OBSERVED_BODY_MIN,
        "bodyMax": OBSERVED_BODY_MAX,
        "bodyRanges": str(OBSERVED_BODY_RANGES),
        "instrCount": str(OBSERVED_INSTRUCTIONS),
    }.items():
        require(apply_rows[0].get(field) == value == readback_rows[0].get(field), f"manual apply/readback {field} drift")
    for mode in ("dry", "apply", "readback"):
        validate_manual_ready(
            inputs / f"canary-{mode}.ready.json",
            mode,
            inputs / f"canary-{mode}.tsv",
            proposal_target,
            promotion_tool,
        )
    diff = read_json(inputs / "inventory-diff.json", "manual inventory diff")
    require(
        diff.get("counts", {}).get("before") == BASELINE_FUNCTIONS
        and diff.get("counts", {}).get("after") == AFTER_FUNCTIONS
        and diff.get("counts", {}).get("created") == 1
        and diff.get("counts", {}).get("destroyed") == 0
        and all(value == 0 for key, value in diff.get("counts", {}).items() if key not in {"before", "after", "created", "destroyed"})
        and [row.get("address") for row in diff.get("created", [])] == [CANARY_ADDRESS]
        and not diff.get("destroyed"),
        "manual inventory diff exceeds one creation",
    )
    return {
        "created": created,
        "changedProgramMetrics": sorted(changed_metrics),
        "baselineFunctionCount": len(before),
        "afterFunctionCount": len(after),
    }


def project_rows_from_manifest(path: Path, side: str) -> list[tuple[str, int, str]]:
    document = read_json(path, "manual copy manifest")
    section = document.get(side)
    require(document.get("schemaVersion") == base.BACKUP_SCHEMA and isinstance(section, dict), "manual copy manifest schema drift")
    rows = []
    for row in section.get("files", []):
        require(isinstance(row, dict) and set(row) == {"relative_path", "size", "sha256"}, "manual copy manifest row drift")
        rows.append((str(row["relative_path"]), int(row["size"]), str(row["sha256"])))
    rows.sort()
    return rows


def artifact_manifest(proof_root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for owner in ("tools", "inputs", "runs"):
        root = proof_root / owner
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                raise RefutationError(f"evidence tree contains symlink: {path}")
            if path.is_file():
                relative = path.relative_to(proof_root).as_posix()
                result[relative] = stamp(path, proof_root)
    return result


def validate_artifact_manifest(proof_root: Path, expected: object) -> dict[str, dict[str, Any]]:
    require(isinstance(expected, dict), "refutation has no artifact manifest")
    actual = artifact_manifest(proof_root)
    require(actual == expected, "refutation evidence tree has changed")
    return actual


def run_source_replay(
    proof_root: Path,
    frozen_runner: Path,
    source_ready: Path,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, Any]:
    result, output = base.run_process(
        proof_root=proof_root,
        run_id="source-proof-replay",
        argv=[str(Path(sys.executable).resolve()), "-I", "-B", str(frozen_runner.resolve()), "--verify-ready", str(source_ready.resolve())],
        cwd=cwd,
        environment=environment,
        timeout_seconds=600,
    )
    expected = (
        "GHIDRA_SCRATCH_PROOF_VERIFIED count=40 before=7555 after=7595 "
        f"readySha256={SOURCE_PROOF_READY_SHA256}"
    )
    require(result.get("exitCode") == 0 and output.count(expected) == 1 and "REFUSED:" not in output, "frozen v9 proof replay failed")
    return base.finish_run(proof_root, result, exactVerifierSentinel=expected)


def run_current_inventory(
    proof_root: Path,
    run_id: str,
    project: Path,
    headless: Path,
    inventory_tool: Path,
    cwd: Path,
    environment: dict[str, str],
) -> tuple[dict[str, Any], Path, Path]:
    return base.run_inventory(
        proof_root=proof_root,
        run_id=run_id,
        headless=headless,
        project_root=project,
        project_name="BEA",
        tool=inventory_tool,
        tool_stamp=base.external_stamp(inventory_tool),
        cwd=cwd,
        environment=environment,
    )


def finalize(args: argparse.Namespace) -> Path:
    raise RefutationError(HISTORICAL_RETIREMENT_MESSAGE)

    proof_root = args.out.resolve()
    local_lab = (ROOT / "local-lab").resolve()
    require(not proof_root.exists(), f"refusing existing output: {proof_root}")
    try:
        proof_root.relative_to(local_lab)
    except ValueError as exc:
        raise RefutationError("output must stay under ignored local-lab") from exc
    if os.name == "nt":
        import ctypes

        require(not ctypes.windll.shell32.IsUserAnAdmin(), "refutation finalizer must run non-elevated")

    source_proof = args.source_proof.resolve()
    proposal = args.proposal.resolve()
    manual = args.manual.resolve()
    specimen = args.specimen.resolve()
    source_ready = source_proof / "proof.ready.json"
    validate_hash(source_ready, SOURCE_PROOF_READY_SHA256, "frozen v9 READY")
    proposal = proposal.resolve()
    proposal_data = proposal_row(proposal)
    validate_hash(specimen, SPECIMEN_SHA256, "pristine specimen")

    headless, _application_properties, host_java = base.require_expected_external_toolchain(args.headless.resolve())
    proof_root.mkdir(parents=True)
    for name in ("tools", "inputs", "runs", "work"):
        (proof_root / name).mkdir()
    environment = base.prepare_sanitized_environment(proof_root, host_java)
    cwd = proof_root / "work"

    frozen_sources = {
        "ghidra_crt_canary_refutation.py": (Path(__file__).resolve(), None),
        "ghidra_promotion_scratch_proof.py": (source_proof / "tools/ghidra_promotion_scratch_proof.py", FROZEN_RUNNER_SHA256),
        "CreateFunctionsFromAddressList.java": (source_proof / "tools/CreateFunctionsFromAddressList.java", PROMOTION_TOOL_SHA256),
        "ExportFullFunctionInventory.java": (source_proof / "tools/ExportFullFunctionInventory.java", INVENTORY_TOOL_SHA256),
    }
    for name, (source, expected) in frozen_sources.items():
        if expected is not None:
            validate_hash(source, expected, f"frozen tool {name}")
        write_new(proof_root / "tools" / name, source.read_bytes())

    inputs = proof_root / "inputs"
    copied = {
        "frozen-v9.ready.json": (source_ready, SOURCE_PROOF_READY_SHA256),
        "proposal.ready.json": (proposal / "boundary-targets.ready.json", PROPOSAL_READY_SHA256),
        "proposal-boundary-targets.tsv": (proposal / "boundary-targets.tsv", PROPOSAL_MANIFEST_SHA256),
        "proposal-canary-targets.txt": (proposal / "canary-targets.txt", CANARY_LIST_SHA256),
        "pristine-specimen.sha256.txt": (None, None),
    }
    for name, value in copied.items():
        if value[0] is not None:
            copy_exact(value[0], inputs / name, str(value[1]))
    write_new(inputs / "pristine-specimen.sha256.txt", f"{SPECIMEN_SHA256}  {specimen}\n".encode("utf-8"))
    for destination_name, (relative, expected) in MANUAL_INPUTS.items():
        copy_exact(manual / relative, inputs / destination_name, expected)
    write_new(inputs / "weak-tail-target.txt", b"0x00542720\n")

    source_receipt = read_json(inputs / "frozen-v9.ready.json", "frozen v9 READY copy")
    source_project_value = source_receipt.get("projects", {}).get("mainScratch", {}).get("root")
    require(isinstance(source_project_value, str), "frozen v9 READY has no main project")
    source_project = Path(source_project_value).resolve()
    require(source_project == (source_proof / "main-project").resolve(), "frozen v9 project path drift")
    require(source_receipt.get("projects", {}).get("mainScratch", {}).get("finalFileSetSha256") == SOURCE_PROJECT_FILESET_SHA256, "frozen v9 project file-set drift")
    manual_project = manual / "project"
    manifest_source = project_rows_from_manifest(inputs / "manual-copy-manifest.json", "source")
    require(base.project_rows_from_disk(source_project, "BEA") == manifest_source, "manual canary source no longer equals frozen v9 main project")

    promotion_tool = proof_root / "tools/CreateFunctionsFromAddressList.java"
    inventory_tool = proof_root / "tools/ExportFullFunctionInventory.java"
    manual_result = validate_manual_evidence(inputs, proposal / "canary-targets.txt", source_proof / "tools/CreateFunctionsFromAddressList.java")

    expected_bytes = pe_ranges(specimen, ((0x00542710, 0x0054271A),))
    observed_bytes = pe_ranges(specimen, ((0x00542710, 0x0054271A), (0x00542720, 0x00542736)))
    require(len(expected_bytes) == EXPECTED_BYTES and sha256_bytes(expected_bytes) == EXPECTED_BYTES_SHA256, "preregistered body bytes do not reproduce")
    require(len(observed_bytes) == OBSERVED_BODY_BYTES and sha256_bytes(observed_bytes) == OBSERVED_BODY_BYTES_SHA256, "observed body bytes do not reproduce")

    actions = []
    actions.append(run_source_replay(proof_root, proof_root / "tools/ghidra_promotion_scratch_proof.py", source_ready, cwd, environment))
    source_run, source_functions, source_program = run_current_inventory(
        proof_root, "source-current", source_project, headless, inventory_tool, cwd, environment
    )
    actions.append(source_run)
    require(sha256_file(source_functions) == SOURCE_FUNCTIONS_SHA256 and sha256_file(source_program) == SOURCE_PROGRAM_SHA256, "current frozen-v9 source inventory drift")
    retained_run, retained_functions, retained_program = run_current_inventory(
        proof_root, "retained-current", manual_project, headless, inventory_tool, cwd, environment
    )
    actions.append(retained_run)
    require(retained_functions.read_bytes() == (inputs / "after-functions.tsv").read_bytes(), "retained canary function inventory drift")
    require(retained_program.read_bytes() == (inputs / "after-program.tsv").read_bytes(), "retained canary program inventory drift")

    tail_target = inputs / "weak-tail-target.txt"
    tail_action, tail_tsv, tail_ready = base.run_promotion(
        proof_root=proof_root,
        run_id="weak-tail-containment-guard",
        headless=headless,
        project_root=manual_project,
        project_name="BEA",
        tool=promotion_tool,
        tool_stamp=base.external_stamp(promotion_tool),
        target_path=tail_target,
        target_stamp=base.stamp(tail_target, proof_root),
        target_count=1,
        semantic_target_sha256=sha256_file(tail_target),
        mode="dry",
        expected_sha256=sha256_file(tail_target),
        cwd=cwd,
        environment=environment,
        expected_error=TAIL_ERROR,
    )
    require(tail_tsv is None and tail_ready is None, "weak-tail guard unexpectedly produced promotion output")
    actions.append(tail_action)

    project_rows = base.project_rows_from_disk(manual_project, "BEA")
    project_digest = base.canonical_rows_sha(project_rows)
    require(project_rows_from_manifest(inputs / "manual-copy-manifest.json", "destination") != project_rows, "manual scratch did not record a mutation")
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "verdict": VERDICT,
        "finalizedAtUtc": datetime.now(timezone.utc).isoformat(),
        "tool": stamp(proof_root / "tools/ghidra_crt_canary_refutation.py", proof_root),
        "program": {
            "specimen": external_stamp(specimen),
            "name": base.PROGRAM_NAME,
            "imageBase": base.IMAGE_BASE,
            "language": base.LANGUAGE,
            "compilerSpec": base.COMPILER_SPEC,
        },
        "preregistration": {
            "ready": stamp(inputs / "proposal.ready.json", proof_root),
            "manifest": stamp(inputs / "proposal-boundary-targets.tsv", proof_root),
            "canaryList": stamp(inputs / "proposal-canary-targets.txt", proof_root),
            "target": proposal_data,
            "expectedBody": {
                "ranges": [[CANARY_ADDRESS, EXPECTED_END_EXCLUSIVE]],
                "bytes": EXPECTED_BYTES,
                "bytesSha256": EXPECTED_BYTES_SHA256,
            },
        },
        "sourceAuthority": {
            "ready": stamp(inputs / "frozen-v9.ready.json", proof_root),
            "projectRoot": str(source_project),
            "projectFileSetSha256": SOURCE_PROJECT_FILESET_SHA256,
            "baselineFunctions": stamp(inputs / "baseline-functions.tsv", proof_root),
            "baselineProgram": stamp(inputs / "baseline-program.tsv", proof_root),
        },
        "manualObservation": {
            "projectRoot": str(manual_project.resolve()),
            "copyManifest": stamp(inputs / "manual-copy-manifest.json", proof_root),
            "afterFunctions": stamp(inputs / "after-functions.tsv", proof_root),
            "afterProgram": stamp(inputs / "after-program.tsv", proof_root),
            "inventoryDiff": stamp(inputs / "inventory-diff.json", proof_root),
            "createdFunction": manual_result["created"],
            "observedBody": {
                "ranges": [["0x00542710", "0x0054271a"], ["0x00542720", "0x00542736"]],
                "bytes": OBSERVED_BODY_BYTES,
                "rangeDigest": OBSERVED_BODY_RANGE_DIGEST,
                "bytesSha256": OBSERVED_BODY_BYTES_SHA256,
                "instructionCount": OBSERVED_INSTRUCTIONS,
            },
            "createdEntries": [CANARY_ADDRESS],
            "destroyedEntries": [],
            "existingRowsChanged": 0,
            "changedProgramMetrics": manual_result["changedProgramMetrics"],
            "tailEntryAbsent": True,
            "tailContainedBy": CANARY_ADDRESS,
            "retainedProjectFileSetSha256": project_digest,
        },
        "runs": [action["receipt"] for action in actions],
        "checks": {
            "sourceProofReplayed": True,
            "sourceInventoryMatchesPost40": True,
            "retainedInventoryMatchesObservation": True,
            "weakTailGuardRejectedInsideCreatedFunction": True,
            "originalExactBodyClaimRefuted": True,
            "entryHypothesisRefuted": False,
            "learnedTwoRangeBodyAuthorized": False,
            "batch520Authorized": False,
        },
        "batchGate": "BLOCKED_PENDING_NEW_TWO_RANGE_CANARY_AUTHORITY",
        "claimBoundary": claim_boundary(),
    }
    receipt["artifacts"] = artifact_manifest(proof_root)
    ready_path = proof_root / "canary-refutation.ready.json"
    write_new(ready_path, (json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
    return ready_path


def parse_run_receipts(proof_root: Path, receipt: dict[str, Any]) -> None:
    expected_ids = ["source-proof-replay", "source-current", "retained-current", "weak-tail-containment-guard"]
    values = receipt.get("runs")
    require(isinstance(values, list) and len(values) == len(expected_ids), "run receipt list drift")
    for expected_id, spec in zip(expected_ids, values):
        require(isinstance(spec, dict), "run stamp missing")
        path = proof_root / str(spec.get("path", ""))
        require(stamp(path, proof_root) == spec, f"run receipt changed: {expected_id}")
        run = read_json(path, f"run {expected_id}")
        require(run.get("id") == expected_id and run.get("verdict") == "SURVIVED", f"run did not survive: {expected_id}")
    replay_log = proof_root / "runs/source-proof-replay/headless.log"
    require(f"readySha256={SOURCE_PROOF_READY_SHA256}" in replay_log.read_text(encoding="utf-8"), "source replay sentinel missing")
    tail_log = proof_root / "runs/weak-tail-containment-guard/headless.log"
    tail_text = tail_log.read_text(encoding="utf-8")
    require(tail_text.count(TAIL_ERROR) == 1 and "FUNCTION_PROMOTION_PREFLIGHT_OK" not in tail_text, "weak-tail guard log drift")


def verify_ready(ready_path: Path, *, live_readback: bool = True) -> dict[str, Any]:
    raise RefutationError(HISTORICAL_RETIREMENT_MESSAGE)

    ready_path = ready_path.resolve()
    proof_root = ready_path.parent
    receipt = read_json(ready_path, "canary refutation READY")
    expected_keys = {
        "schema", "status", "verdict", "finalizedAtUtc", "tool", "program",
        "preregistration", "sourceAuthority", "manualObservation", "runs",
        "checks", "batchGate", "claimBoundary", "artifacts",
    }
    require(receipt.get("schema") == SCHEMA and receipt.get("status") == STATUS and receipt.get("verdict") == VERDICT and set(receipt) == expected_keys, "refutation schema/verdict drift")
    timestamp = datetime.fromisoformat(str(receipt.get("finalizedAtUtc")))
    require(timestamp.tzinfo is not None and timestamp.utcoffset() is not None, "refutation timestamp has no timezone")
    require(stamp(proof_root / str(receipt.get("tool", {}).get("path", "")), proof_root) == receipt.get("tool"), "refutation tool changed")
    require((proof_root / str(receipt["tool"]["path"])).resolve() == Path(__file__).resolve(), "verify with the frozen refutation owner recorded by READY")
    validate_artifact_manifest(proof_root, receipt.get("artifacts"))
    parse_run_receipts(proof_root, receipt)

    inputs = proof_root / "inputs"
    validate_hash(inputs / "frozen-v9.ready.json", SOURCE_PROOF_READY_SHA256, "frozen v9 READY copy")
    validate_hash(inputs / "proposal.ready.json", PROPOSAL_READY_SHA256, "proposal READY copy")
    validate_hash(inputs / "proposal-boundary-targets.tsv", PROPOSAL_MANIFEST_SHA256, "proposal manifest copy")
    validate_hash(inputs / "proposal-canary-targets.txt", CANARY_LIST_SHA256, "proposal canary list copy")
    for destination_name, (_relative, expected) in MANUAL_INPUTS.items():
        validate_hash(inputs / destination_name, expected, f"manual evidence {destination_name}")
    checks = receipt.get("checks")
    require(
        checks == {
            "sourceProofReplayed": True,
            "sourceInventoryMatchesPost40": True,
            "retainedInventoryMatchesObservation": True,
            "weakTailGuardRejectedInsideCreatedFunction": True,
            "originalExactBodyClaimRefuted": True,
            "entryHypothesisRefuted": False,
            "learnedTwoRangeBodyAuthorized": False,
            "batch520Authorized": False,
        },
        "refutation checks drift",
    )
    require(receipt.get("batchGate") == "BLOCKED_PENDING_NEW_TWO_RANGE_CANARY_AUTHORITY", "batch gate drift")
    require(receipt.get("claimBoundary") == claim_boundary(), "claim boundary drift")
    program = receipt.get("program")
    require(isinstance(program, dict), "program envelope missing")
    specimen_path = Path(str(program.get("specimen", {}).get("path", "")))
    require(
        external_stamp(specimen_path) == program.get("specimen")
        and program.get("name") == base.PROGRAM_NAME
        and program.get("imageBase") == base.IMAGE_BASE
        and program.get("language") == base.LANGUAGE
        and program.get("compilerSpec") == base.COMPILER_SPEC
        and program.get("specimen", {}).get("sha256") == SPECIMEN_SHA256,
        "program/specimen envelope drift",
    )
    preregistration = receipt.get("preregistration")
    require(isinstance(preregistration, dict), "preregistration envelope missing")
    require(
        preregistration.get("ready") == stamp(inputs / "proposal.ready.json", proof_root)
        and preregistration.get("manifest") == stamp(inputs / "proposal-boundary-targets.tsv", proof_root)
        and preregistration.get("canaryList") == stamp(inputs / "proposal-canary-targets.txt", proof_root),
        "preregistration artifact envelope drift",
    )
    copied_proposal = read_json(inputs / "proposal.ready.json", "proposal READY copy")
    proposal_targets = [
        row for row in copied_proposal.get("targets", [])
        if isinstance(row, dict) and row.get("address") == CANARY_ADDRESS
    ]
    require(len(proposal_targets) == 1 and preregistration.get("target") == proposal_targets[0], "preregistered target row drift")
    source_authority = receipt.get("sourceAuthority")
    require(isinstance(source_authority, dict), "source authority envelope missing")
    source_receipt = read_json(inputs / "frozen-v9.ready.json", "frozen v9 READY copy")
    source_project = Path(str(source_authority.get("projectRoot", "")))
    require(
        source_authority.get("ready") == stamp(inputs / "frozen-v9.ready.json", proof_root)
        and source_authority.get("projectFileSetSha256") == SOURCE_PROJECT_FILESET_SHA256
        and source_authority.get("baselineFunctions") == stamp(inputs / "baseline-functions.tsv", proof_root)
        and source_authority.get("baselineProgram") == stamp(inputs / "baseline-program.tsv", proof_root)
        and str(source_project.resolve())
        == str(Path(str(source_receipt.get("projects", {}).get("mainScratch", {}).get("root", ""))).resolve()),
        "source authority envelope drift",
    )
    manual_observation = receipt.get("manualObservation")
    require(isinstance(manual_observation, dict), "manual observation envelope missing")
    require(
        manual_observation.get("copyManifest") == stamp(inputs / "manual-copy-manifest.json", proof_root)
        and manual_observation.get("afterFunctions") == stamp(inputs / "after-functions.tsv", proof_root)
        and manual_observation.get("afterProgram") == stamp(inputs / "after-program.tsv", proof_root)
        and manual_observation.get("inventoryDiff") == stamp(inputs / "inventory-diff.json", proof_root)
        and manual_observation.get("createdEntries") == [CANARY_ADDRESS]
        and manual_observation.get("destroyedEntries") == []
        and manual_observation.get("existingRowsChanged") == 0
        and manual_observation.get("changedProgramMetrics") == ["functions"]
        and manual_observation.get("tailEntryAbsent") is True
        and manual_observation.get("tailContainedBy") == CANARY_ADDRESS,
        "manual observation envelope drift",
    )
    require(receipt.get("preregistration", {}).get("expectedBody") == {"ranges": [[CANARY_ADDRESS, EXPECTED_END_EXCLUSIVE]], "bytes": EXPECTED_BYTES, "bytesSha256": EXPECTED_BYTES_SHA256}, "preregistered body envelope drift")
    observed = receipt.get("manualObservation", {}).get("observedBody")
    require(observed == {
        "ranges": [["0x00542710", "0x0054271a"], ["0x00542720", "0x00542736"]],
        "bytes": OBSERVED_BODY_BYTES,
        "rangeDigest": OBSERVED_BODY_RANGE_DIGEST,
        "bytesSha256": OBSERVED_BODY_BYTES_SHA256,
        "instructionCount": OBSERVED_INSTRUCTIONS,
    }, "observed body envelope drift")
    manual_result = validate_manual_evidence(
        inputs,
        Path(str(read_json(inputs / "canary-apply.ready.json", "manual apply READY")["input"]["path"])),
        Path(str(read_json(inputs / "canary-apply.ready.json", "manual apply READY")["tool"]["path"])),
    )
    require(manual_result["created"] == receipt.get("manualObservation", {}).get("createdFunction"), "created function receipt drift")

    if live_readback:
        headless, _properties, host_java = base.require_expected_external_toolchain(DEFAULT_HEADLESS)
        inventory_tool = proof_root / "tools/ExportFullFunctionInventory.java"
        source_project = Path(str(receipt["sourceAuthority"]["projectRoot"]))
        retained_project = Path(str(receipt["manualObservation"]["projectRoot"]))
        with base.tempfile.TemporaryDirectory(prefix="bea-crt-canary-refutation-verify-") as temporary:
            verify_root = Path(temporary).resolve()
            (verify_root / "runs").mkdir()
            work = verify_root / "work"
            work.mkdir()
            environment = base.prepare_sanitized_environment(verify_root, host_java)
            _source_run, source_functions, source_program = run_current_inventory(
                verify_root, "source-current", source_project, headless, inventory_tool, work, environment
            )
            require(source_functions.read_bytes() == (inputs / "baseline-functions.tsv").read_bytes() and source_program.read_bytes() == (inputs / "baseline-program.tsv").read_bytes(), "live source inventory drift")
            _retained_run, retained_functions, retained_program = run_current_inventory(
                verify_root, "retained-current", retained_project, headless, inventory_tool, work, environment
            )
            require(retained_functions.read_bytes() == (inputs / "after-functions.tsv").read_bytes() and retained_program.read_bytes() == (inputs / "after-program.tsv").read_bytes(), "live retained inventory drift")
        retained_rows = base.project_rows_from_disk(retained_project, "BEA")
        require(
            base.canonical_rows_sha(retained_rows)
            == receipt["manualObservation"].get("retainedProjectFileSetSha256"),
            "retained raw project file-set drift",
        )

    return {
        "status": STATUS,
        "verdict": VERDICT,
        "ready": external_stamp(ready_path),
        "baselineFunctions": BASELINE_FUNCTIONS,
        "afterFunctions": AFTER_FUNCTIONS,
        "expectedBodyBytes": EXPECTED_BYTES,
        "observedBodyBytes": OBSERVED_BODY_BYTES,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-ready", type=Path)
    parser.add_argument("--no-live-readback", action="store_true")
    parser.add_argument("--source-proof", type=Path, default=DEFAULT_SOURCE_PROOF)
    parser.add_argument("--proposal", type=Path, default=DEFAULT_PROPOSAL)
    parser.add_argument("--manual", type=Path, default=DEFAULT_MANUAL)
    parser.add_argument("--specimen", type=Path, default=DEFAULT_SPECIMEN)
    parser.add_argument("--headless", type=Path, default=DEFAULT_HEADLESS)
    parser.add_argument("--out", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.verify_ready is not None:
            result = verify_ready(args.verify_ready, live_readback=not args.no_live_readback)
            print(
                "GHIDRA_CRT_CANARY_REFUTATION_VERIFIED "
                f"verdict={result['verdict']} before={result['baselineFunctions']} "
                f"after={result['afterFunctions']} expectedBodyBytes={result['expectedBodyBytes']} "
                f"observedBodyBytes={result['observedBodyBytes']} readySha256={result['ready']['sha256']}"
            )
            return 0
        require(args.out is not None, "--out is required when finalizing")
        ready_path = finalize(args)
        frozen_runner = ready_path.parent / "tools/ghidra_crt_canary_refutation.py"
        completed = subprocess.run(
            [str(Path(sys.executable).resolve()), "-I", "-B", str(frozen_runner), "--verify-ready", str(ready_path)],
            cwd=ready_path.parent / "work",
            text=True,
            capture_output=True,
            check=False,
            timeout=600,
        )
        require(completed.returncode == 0 and completed.stdout.startswith("GHIDRA_CRT_CANARY_REFUTATION_VERIFIED ") and not completed.stderr.strip(), f"frozen refutation replay failed: {completed.stdout[-300:]!r} {completed.stderr[-300:]!r}")
        print(completed.stdout.strip().replace("_VERIFIED ", "_READY ", 1))
        return 0
    except (OSError, RefutationError, base.ProofError, UnicodeError, ValueError) as exc:
        print(f"REFUSED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
