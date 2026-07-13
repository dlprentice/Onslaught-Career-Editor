#!/usr/bin/env python3
"""Run the authority-gated three-role BattleEngine morph identity canary."""

from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from typing import Any, Callable, Mapping, Sequence

import battleengine_morph_identity_authority as authority_control
import battleengine_morph_identity_canary as canary
import winui_safe_copy_live_runtime_smoke as harness


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_SCHEMA = authority_control.AUTHORITY_SCHEMA
LEASE_SCHEMA = authority_control.LEASE_SCHEMA
ACTION_FAMILY = authority_control.ACTION_FAMILY
LIVE_ARM_PHRASE = authority_control.LIVE_ARM_PHRASE
PRIVATE_PROOF_PARENT = authority_control.PRIVATE_PROOF_PARENT
RUNTIME_PROTOCOL = harness.MORPH_CANARY_RUNTIME_PROTOCOL
RUN_ROLES = canary.RUN_ROLES
RUN_ROOT_NAMES = {
    "noInputControl": "no-input-control",
    "positiveTransform": "positive-transform",
    "positiveRepeat": "positive-repeat",
}
REQUIRED_ALLOWED_ACTIONS = authority_control.REQUIRED_ALLOWED_ACTIONS
REQUIRED_FORBIDDEN_ACTIONS = authority_control.REQUIRED_FORBIDDEN_ACTIONS
REQUIRED_RESOURCES = authority_control.REQUIRED_RESOURCES
REQUIRED_VALIDATION_GATES = authority_control.REQUIRED_VALIDATION_GATES
REQUIRED_CLEANUP = authority_control.REQUIRED_CLEANUP
REQUIRED_ROLLBACK = authority_control.REQUIRED_ROLLBACK
PRIVATE_MANIFEST_NAME = "battleengine-morph-identity-canary-private-matrix.json"
SANITIZED_SUMMARY_NAME = "battleengine-morph-identity-canary-sanitized-matrix.json"
PRIVATE_MANIFEST_SCHEMA = "onslaught-battleengine-morph-identity-canary-private-matrix.v1"
MAX_PRIVATE_FILE_BYTES = 16 * 1024 * 1024
_DIGEST = re.compile(r"[0-9a-f]{64}")


class CanaryError(RuntimeError):
    """Raised when the bounded canary contract cannot be satisfied."""


@dataclass(frozen=True)
class HarnessResult:
    exit_code: int
    artifact_path: Path
    log_path: Path
    receipt_path: Path


@dataclass(frozen=True)
class RunPlan:
    role: str
    root: Path
    command: tuple[str, ...]
    launch_arguments: tuple[str, ...]
    input_sequences: tuple[str, ...]
    command_sha256: str


@dataclass(frozen=True)
class RuntimePreflight:
    source_root: Path
    exe_override: Path
    ambient_executable_sha256: str
    executable_sha256: str
    command_sha256: str
    template_sha256: str


@dataclass(frozen=True)
class MatrixPlan:
    proof_root: Path
    runs: tuple[RunPlan, ...]


@dataclass(frozen=True)
class MatrixResult:
    private_manifest: Path
    sanitized_summary: Path


@dataclass(frozen=True)
class _PrivateRun:
    role: str
    root: Path
    artifact_path: Path
    artifact_raw: bytes
    artifact_sha256: str
    log_path: Path
    log_raw: bytes
    log_sha256: str
    receipt_path: Path
    receipt_sha256: str
    process: Mapping[str, Any]
    process_identity: tuple[int, str]
    run_id: str
    executable_path: Path
    working_directory: Path
    manifest_path: Path
    command_sha256: str
    template_sha256: str
    executable_sha256: str


HarnessCallable = Callable[[str, Path, tuple[str, ...]], HarnessResult]
RunMaterializer = Callable[[bytes, bytes, str], Mapping[str, Any]]
MatrixMaterializer = Callable[[Sequence[Mapping[str, Any]]], Mapping[str, Any]]
PublicValidator = Callable[[Any], None]
RuntimePreflightCallable = Callable[[Path, Path], RuntimePreflight]


def _require_object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CanaryError(f"{label} must be a JSON object")
    return value


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise CanaryError(f"{label} keys mismatch (missing={missing}, extra={extra})")


def _require_exact_strings(value: Any, expected: Sequence[str], label: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CanaryError(f"{label} must be an exact string array")
    if value != list(expected):
        raise CanaryError(f"{label} does not match the approved contract")


def parse_utc(value: Any, label: str) -> dt.datetime:
    try:
        return authority_control.parse_utc(value, label)
    except authority_control.AuthorityError as exc:
        raise CanaryError(str(exc)) from exc


def _format_utc(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _absolute(path: str | Path) -> Path:
    return Path(path).expanduser().absolute()


def _normalized_path(path: str | Path) -> str:
    return os.path.normcase(str(_absolute(path).resolve(strict=False)))


def _same_path(left: str | Path, right: str | Path) -> bool:
    return _normalized_path(left) == _normalized_path(right)


def _is_same_or_under(path: Path, root: Path) -> bool:
    path_text = _normalized_path(path)
    root_text = _normalized_path(root)
    try:
        return os.path.commonpath((path_text, root_text)) == root_text
    except ValueError:
        return False


def _paths_overlap(left: Path, right: Path) -> bool:
    return _is_same_or_under(left, right) or _is_same_or_under(right, left)


def has_reparse_or_symlink_ancestor(path: str | Path) -> bool:
    candidate = _absolute(path)
    for current in (candidate, *candidate.parents):
        if not current.exists() and not current.is_symlink():
            continue
        try:
            metadata = current.lstat()
        except OSError:
            return True
        attributes = getattr(metadata, "st_file_attributes", 0)
        if current.is_symlink() or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            return True
    return False


def validate_proof_root(
    proof_root: str | Path,
    *,
    create: bool,
    private_parent: str | Path = PRIVATE_PROOF_PARENT,
) -> Path:
    try:
        candidate = authority_control.validate_private_proof_root(
            proof_root,
            private_parent=private_parent,
            require_exists=False,
        )
    except authority_control.AuthorityError as exc:
        raise CanaryError(str(exc)) from exc
    if create:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            if has_reparse_or_symlink_ancestor(candidate.parent):
                raise CanaryError("proof root parent became reparse or symlink routed")
            candidate.mkdir(exist_ok=False)
        except CanaryError:
            raise
        except OSError as exc:
            raise CanaryError(f"could not create fresh proof root: {exc}") from exc
        if has_reparse_or_symlink_ancestor(candidate):
            raise CanaryError("proof root became reparse or symlink routed during creation")
    return candidate.resolve(strict=False)


def validate_authority(authority: Any, proof_root: str | Path, now: dt.datetime) -> None:
    try:
        authority_control.validate_authority(authority, proof_root, now)
    except authority_control.AuthorityError as exc:
        raise CanaryError(str(exc)) from exc


def validate_leases(leases: Any, now: dt.datetime) -> None:
    try:
        authority_control.validate_leases(leases, now)
    except authority_control.AuthorityError as exc:
        raise CanaryError(str(exc)) from exc


def build_harness_command(
    role: str,
    role_root: Path,
    source_root: Path,
    exe_override: Path,
    controls: authority_control.ControlRecords,
) -> tuple[str, ...]:
    if role not in RUN_ROLES:
        raise CanaryError(f"invalid canary role: {role}")
    command = (
        "py",
        "-3",
        str(ROOT / "tools" / "winui_safe_copy_live_runtime_smoke.py"),
        "--runtime-protocol",
        RUNTIME_PROTOCOL,
        "--canary-role",
        role,
        "--source-root",
        str(source_root),
        "--exe-override",
        str(exe_override),
        "--artifact-root",
        str(role_root),
        "--profiles-root",
        str(role_root / "app-config" / "OnslaughtCareerEditor" / "GameProfiles"),
        "--canary-authority-file",
        str(controls.authority_path),
        "--expected-canary-authority-sha256",
        controls.authority_sha256,
        "--canary-leases-file",
        str(controls.leases_path),
        "--expected-canary-leases-sha256",
        controls.leases_sha256,
        "--arm-external-artifact-root",
        harness.EXTERNAL_ARTIFACT_ROOT_ARM_PHRASE,
        "--arm-live-bea",
        harness.ARM_PHRASE,
    )
    try:
        parsed = harness.parse_args(list(command[3:]))
        protocol = harness.validate_runtime_protocol(parsed)
    except (SystemExit, ValueError) as exc:
        raise CanaryError(f"generated harness command violates the locked protocol: {exc}") from exc
    expected_input = [] if role == "noInputControl" else ["tap:Q"]
    if (
        protocol.runtime_protocol != RUNTIME_PROTOCOL
        or protocol.canary_role != role
        or protocol.input_sequences != expected_input
    ):
        raise CanaryError("generated harness command drifted from the fixed role protocol")
    return command


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _default_runtime_preflight(source_root: Path, exe_override: Path) -> RuntimePreflight:
    source_executable = source_root / "BEA.exe"
    ambient_sha256 = _file_sha256(source_executable)
    try:
        rendered = canary.render_private_command(exe_override, canary.DEFAULT_TEMPLATE)
    except (OSError, ValueError) as exc:
        raise CanaryError(f"private command preflight failed: {exc}") from exc
    if rendered.executable_sha256 != canary.CANONICAL_SHA256:
        raise CanaryError("effective executable override is not canonical")
    return RuntimePreflight(
        source_root=source_root,
        exe_override=exe_override,
        ambient_executable_sha256=ambient_sha256,
        executable_sha256=rendered.executable_sha256,
        command_sha256=rendered.sha256,
        template_sha256=rendered.template_sha256,
    )


def _default_harness(role: str, role_root: Path, command: tuple[str, ...]) -> HarnessResult:
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    interrupted = False
    while True:
        try:
            return_code = process.wait()
            break
        except KeyboardInterrupt:
            # The child owns receipt-bound teardown; let it finish instead of
            # propagating an ordinary console interrupt into the cleanup path.
            # The interrupted run remains invalid even when cleanup succeeds.
            interrupted = True
            continue
    if interrupted:
        return_code = 130
    return HarnessResult(
        return_code,
        role_root / "battleengine-morph-identity-canary-private-run.json",
        role_root / "cdb" / "windbg.log",
        role_root / "runtime-process-receipt.json",
    )


def _read_bounded_bytes(path: Path, label: str) -> bytes:
    try:
        with path.open("rb") as stream:
            before = os.fstat(stream.fileno())
            raw = stream.read(MAX_PRIVATE_FILE_BYTES + 1)
            after = os.fstat(stream.fileno())
    except OSError as exc:
        raise CanaryError(f"could not read {label}: {exc}") from exc
    if len(raw) > MAX_PRIVATE_FILE_BYTES:
        raise CanaryError(f"{label} exceeds the 16 MiB private proof limit")
    if (before.st_dev, before.st_ino, before.st_size) != (after.st_dev, after.st_ino, after.st_size):
        raise CanaryError(f"{label} changed while it was read")
    return raw


def _read_json_bytes(raw: bytes, label: str) -> Mapping[str, Any]:
    def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise CanaryError(f"{label} contains duplicate key {key!r}")
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CanaryError(f"{label} is not valid UTF-8 JSON") from exc
    return _require_object(value, label)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _validate_private_file(path: Path, role_root: Path, label: str) -> Path:
    candidate = _absolute(path)
    if not _is_same_or_under(candidate, role_root) or _same_path(candidate, role_root):
        raise CanaryError(f"{label} is outside its private role root")
    if has_reparse_or_symlink_ancestor(candidate):
        raise CanaryError(f"{label} is reparse or symlink routed")
    if not candidate.is_file():
        raise CanaryError(f"{label} is missing")
    return candidate.resolve()


_RECEIPT_KEYS = {
    "schemaVersion",
    "runId",
    "process",
    "profileManifest",
    "window",
    "module",
    "sourceExecutableSha256",
    "copiedExecutableSha256",
    "commandTemplateSha256",
    "generatedCommandSha256",
}
_PROCESS_KEYS = {"id", "startedAtUtc", "executable", "workingDirectory", "launchArguments"}
_FILE_IDENTITY_KEYS = {"path", "sha256", "size"}
_WINDOW_KEYS = {"hwndHex"}
_MODULE_KEYS = {"path", "baseAddressHex", "size"}
_HEX_POINTER = re.compile(r"0x[0-9A-Fa-f]+")


def _require_digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise CanaryError(f"{label} must be lowercase SHA-256")
    return value


def _require_private_path(value: Any, role_root: Path, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise CanaryError(f"{label} must be a non-empty path")
    candidate = _absolute(value)
    if not _is_same_or_under(candidate, role_root) or _same_path(candidate, role_root):
        raise CanaryError(f"{label} is outside its private role root")
    if has_reparse_or_symlink_ancestor(candidate):
        raise CanaryError(f"{label} is reparse or symlink routed")
    return candidate.resolve(strict=False)


def _require_file_identity(value: Any, role_root: Path, label: str) -> tuple[Path, str, int]:
    identity = _require_object(value, label)
    _require_exact_keys(identity, _FILE_IDENTITY_KEYS, label)
    path = _require_private_path(identity["path"], role_root, f"{label}.path")
    digest = _require_digest(identity["sha256"], f"{label}.sha256")
    size = identity["size"]
    if type(size) is not int or size < 0:
        raise CanaryError(f"{label}.size must be a nonnegative integer")
    if not path.is_file() or path.stat().st_size != size or _file_sha256(path) != digest:
        raise CanaryError(f"{label} no longer matches its recorded file identity")
    return path, digest, size


def _extract_process_identity(
    receipt: Mapping[str, Any],
    role_root: Path,
    artifact: Mapping[str, Any],
) -> tuple[Mapping[str, Any], tuple[int, str], str, Path, Path, Path]:
    _require_exact_keys(receipt, _RECEIPT_KEYS, "runtime receipt")
    if receipt["schemaVersion"] != "runtime-process-receipt.v1":
        raise CanaryError("runtime receipt schemaVersion mismatch")
    run_id = receipt["runId"]
    if not isinstance(run_id, str) or not run_id:
        raise CanaryError("runtime receipt runId must be non-empty")
    process = _require_object(receipt["process"], "runtime receipt process")
    _require_exact_keys(process, _PROCESS_KEYS, "runtime receipt process")
    process_id = process["id"]
    started_at = process["startedAtUtc"]
    if type(process_id) is not int or process_id <= 0:
        raise CanaryError("runtime receipt process id must be a positive integer")
    parse_utc(started_at, "runtime receipt process startedAtUtc")
    executable_path, _, _ = _require_file_identity(
        process["executable"], role_root, "runtime receipt process executable"
    )
    working_directory = _require_private_path(
        process["workingDirectory"], role_root, "runtime receipt workingDirectory"
    )
    if not isinstance(process["launchArguments"], list) or process["launchArguments"] != [
        "-skipfmv", "-level", "850", "-configuration", "2"
    ]:
        raise CanaryError("runtime receipt launchArguments drifted from the locked protocol")
    manifest_path, _, _ = _require_file_identity(
        receipt["profileManifest"], role_root, "runtime receipt profileManifest"
    )
    window = _require_object(receipt["window"], "runtime receipt window")
    _require_exact_keys(window, _WINDOW_KEYS, "runtime receipt window")
    if not isinstance(window["hwndHex"], str) or not _HEX_POINTER.fullmatch(window["hwndHex"]):
        raise CanaryError("runtime receipt window hwndHex is invalid")
    module = _require_object(receipt["module"], "runtime receipt module")
    _require_exact_keys(module, _MODULE_KEYS, "runtime receipt module")
    module_path = _require_private_path(module["path"], role_root, "runtime receipt module.path")
    if not _same_path(module_path, executable_path):
        raise CanaryError("runtime receipt module path does not match the copied executable")
    if not isinstance(module["baseAddressHex"], str) or not _HEX_POINTER.fullmatch(module["baseAddressHex"]):
        raise CanaryError("runtime receipt module baseAddressHex is invalid")
    if type(module["size"]) is not int or module["size"] <= 0:
        raise CanaryError("runtime receipt module size must be positive")
    for key in (
        "sourceExecutableSha256",
        "copiedExecutableSha256",
        "commandTemplateSha256",
        "generatedCommandSha256",
    ):
        _require_digest(receipt[key], f"runtime receipt {key}")
    if receipt["sourceExecutableSha256"] != canary.CANONICAL_SHA256:
        raise CanaryError("runtime receipt source executable is not canonical")
    if receipt["copiedExecutableSha256"] != canary.CANONICAL_SHA256:
        raise CanaryError("runtime receipt copied executable is not canonical")
    if receipt["commandTemplateSha256"] != artifact.get("templateSha256"):
        raise CanaryError("runtime receipt template digest does not match the private artifact")
    if receipt["generatedCommandSha256"] != artifact.get("commandSha256"):
        raise CanaryError("runtime receipt command digest does not match the private artifact")
    if not _same_path(executable_path, artifact.get("executablePath", "")):
        raise CanaryError("runtime receipt executable path does not match the private artifact")
    public_process = {
        "runId": run_id,
        "id": process_id,
        "startedAtUtc": started_at,
        "executablePath": str(executable_path),
        "workingDirectory": str(working_directory),
        "profileManifestPath": str(manifest_path),
    }
    return (
        public_process,
        (process_id, started_at),
        run_id,
        executable_path,
        working_directory,
        manifest_path,
    )


def _collect_private_run(role: str, role_root: Path, result: HarnessResult) -> _PrivateRun:
    if type(result.exit_code) is not int or result.exit_code != 0:
        raise CanaryError(f"live harness failed for {role} with exit code {result.exit_code}")
    artifact_path = _validate_private_file(result.artifact_path, role_root, f"{role} artifact")
    log_path = _validate_private_file(result.log_path, role_root, f"{role} CDB log")
    receipt_path = _validate_private_file(result.receipt_path, role_root, f"{role} receipt")
    artifact_raw = _read_bounded_bytes(artifact_path, f"{role} artifact")
    log_raw = _read_bounded_bytes(log_path, f"{role} CDB log")
    receipt_raw = _read_bounded_bytes(receipt_path, f"{role} receipt")
    receipt_sha256 = _sha256(receipt_raw)
    artifact = _read_json_bytes(artifact_raw, f"{role} artifact")
    if artifact.get("receiptSha256") != receipt_sha256:
        raise CanaryError(f"{role} artifact is not hash-bound to its runtime receipt")
    receipt = _read_json_bytes(receipt_raw, f"{role} receipt")
    process, process_identity, run_id, executable_path, working_directory, manifest_path = (
        _extract_process_identity(receipt, role_root, artifact)
    )
    return _PrivateRun(
        role=role,
        root=role_root.resolve(),
        artifact_path=artifact_path,
        artifact_raw=artifact_raw,
        artifact_sha256=_sha256(artifact_raw),
        log_path=log_path,
        log_raw=log_raw,
        log_sha256=_sha256(log_raw),
        receipt_path=receipt_path,
        receipt_sha256=receipt_sha256,
        process=process,
        process_identity=process_identity,
        run_id=run_id,
        executable_path=executable_path,
        working_directory=working_directory,
        manifest_path=manifest_path,
        command_sha256=_require_digest(artifact.get("commandSha256"), f"{role} artifact commandSha256"),
        template_sha256=_require_digest(artifact.get("templateSha256"), f"{role} artifact templateSha256"),
        executable_sha256=_require_digest(artifact.get("executableSha256"), f"{role} artifact executableSha256"),
    )


def _ensure_distinct(records: Sequence[_PrivateRun]) -> None:
    checks = {
        "run ID": [row.run_id for row in records],
        "artifact path": [_normalized_path(row.artifact_path) for row in records],
        "artifact digest": [row.artifact_sha256 for row in records],
        "CDB log path": [_normalized_path(row.log_path) for row in records],
        "receipt path": [_normalized_path(row.receipt_path) for row in records],
        "receipt digest": [row.receipt_sha256 for row in records],
        "process identity": [row.process_identity for row in records],
        "copied executable path": [_normalized_path(row.executable_path) for row in records],
        "working directory": [_normalized_path(row.working_directory) for row in records],
        "profile manifest path": [_normalized_path(row.manifest_path) for row in records],
    }
    for label, values in checks.items():
        if len(set(values)) != len(values):
            raise CanaryError(f"canary roles reused a {label}")


def _require_unchanged_private_run(row: _PrivateRun) -> None:
    current = {
        "artifact": _sha256(_read_bounded_bytes(row.artifact_path, f"{row.role} artifact")),
        "CDB log": _sha256(_read_bounded_bytes(row.log_path, f"{row.role} CDB log")),
        "receipt": _sha256(_read_bounded_bytes(row.receipt_path, f"{row.role} receipt")),
    }
    expected = {
        "artifact": row.artifact_sha256,
        "CDB log": row.log_sha256,
        "receipt": row.receipt_sha256,
    }
    drifted = [label for label in current if current[label] != expected[label]]
    if drifted:
        raise CanaryError(f"{row.role} private proof changed after collection: {', '.join(drifted)}")


def _materialize_stable_run(
    row: _PrivateRun,
    materializer: RunMaterializer,
) -> dict[str, Any]:
    _require_unchanged_private_run(row)
    try:
        public = dict(materializer(row.artifact_raw, row.log_raw, row.role))
    except CanaryError:
        raise
    except (OSError, TypeError, ValueError) as exc:
        raise CanaryError(f"could not materialize {row.role}: {exc}") from exc
    _require_unchanged_private_run(row)
    if public.get("receiptSha256") != row.receipt_sha256:
        raise CanaryError(f"materialized {row.role} receipt digest drifted")
    if public.get("rawCaptureSha256") != row.log_sha256:
        raise CanaryError(f"materialized {row.role} raw capture digest drifted")
    return public


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    except (TypeError, ValueError) as exc:
        raise CanaryError("proof payload is not JSON serializable") from exc
    return text.encode("utf-8")


def _write_new(path: Path, raw: bytes) -> None:
    if has_reparse_or_symlink_ancestor(path.parent):
        raise CanaryError(f"refusing proof write through reparse or symlink path: {path}")
    try:
        with path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        raise CanaryError(f"could not create private proof file {path}: {exc}") from exc


def _publish_outputs(
    manifest_path: Path,
    manifest_raw: bytes,
    summary_path: Path,
    summary_raw: bytes,
) -> None:
    pending_manifest = manifest_path.with_name(manifest_path.name + ".pending")
    pending_summary = summary_path.with_name(summary_path.name + ".pending")
    for target in (manifest_path, summary_path, pending_manifest, pending_summary):
        if target.exists() or target.is_symlink():
            raise CanaryError(f"refusing pre-existing proof output: {target}")
    try:
        _write_new(pending_manifest, manifest_raw)
        _write_new(pending_summary, summary_raw)
        os.replace(pending_manifest, manifest_path)
        os.replace(pending_summary, summary_path)
    except CanaryError:
        raise
    except OSError as exc:
        raise CanaryError(f"could not publish canary matrix outputs: {exc}") from exc
    finally:
        for pending in (pending_manifest, pending_summary):
            try:
                pending.unlink(missing_ok=True)
            except OSError:
                pass


def _assert_public_safe(value: Any, private_roots: Sequence[Path]) -> None:
    root_markers = {_normalized_path(root) for root in private_roots}
    forbidden_keys = {
        "artifactPath",
        "commandPath",
        "executablePath",
        "logPath",
        "proofRoot",
        "receiptPath",
        "sourceRoot",
        "templatePath",
        "workingDirectory",
    }

    def walk(item: Any) -> None:
        if isinstance(item, Mapping):
            for key, nested in item.items():
                if not isinstance(key, str):
                    raise CanaryError("sanitized summary contains a non-string field name")
                if key in forbidden_keys or key.endswith("Path") or key.endswith("Root"):
                    raise CanaryError(f"sanitized summary contains private field {key}")
                walk(nested)
        elif isinstance(item, list):
            for nested in item:
                walk(nested)
        elif isinstance(item, str):
            normalized = os.path.normcase(item)
            if any(marker and marker in normalized for marker in root_markers):
                raise CanaryError("sanitized summary contains a private local path")

    walk(value)


def _validate_runtime_inputs(
    proof_root: Path,
    source_root: str | Path,
    exe_override: str | Path,
) -> tuple[Path, Path]:
    source = _absolute(source_root)
    override = _absolute(exe_override)
    if not source.is_dir() or not (source / "BEA.exe").is_file():
        raise CanaryError("source root must contain BEA.exe")
    if not override.is_file():
        raise CanaryError("exe override must be an existing file")
    if has_reparse_or_symlink_ancestor(source) or has_reparse_or_symlink_ancestor(override):
        raise CanaryError("source or executable override is reparse or symlink routed")
    if not _is_same_or_under(override, source):
        raise CanaryError("exe override must stay inside the source root")
    if override.name.lower() not in {"bea.exe", "bea.exe.original.backup"}:
        raise CanaryError("exe override must be named BEA.exe or BEA.exe.original.backup")
    if override.stat().st_nlink != 1:
        raise CanaryError("exe override must not be hardlinked")
    if _paths_overlap(proof_root, source) or _paths_overlap(proof_root, override):
        raise CanaryError("proof root must not overlap source or executable override")
    return source.resolve(), override.resolve()


def _require_ambient_executable_unchanged(preflight: RuntimePreflight) -> None:
    ambient = preflight.source_root / "BEA.exe"
    if not ambient.is_file() or has_reparse_or_symlink_ancestor(ambient):
        raise CanaryError("ambient executable identity drifted from the matrix preflight")
    try:
        current_sha256 = _file_sha256(ambient)
    except OSError as exc:
        raise CanaryError("ambient executable identity could not be revalidated") from exc
    if current_sha256 != preflight.ambient_executable_sha256:
        raise CanaryError("ambient executable identity drifted from the matrix preflight")


class MatrixExecutor:
    def __init__(
        self,
        *,
        harness: HarnessCallable = _default_harness,
        materialize_run: RunMaterializer = canary.materialize_run_bytes,
        materialize_matrix: MatrixMaterializer = canary.materialize_matrix,
        validate_public: PublicValidator = canary.validate_public_matrix,
        runtime_preflight: RuntimePreflightCallable = _default_runtime_preflight,
        private_parent: str | Path = PRIVATE_PROOF_PARENT,
        now: Callable[[], dt.datetime] = lambda: dt.datetime.now(dt.timezone.utc),
    ) -> None:
        if harness is _default_harness and (
            materialize_run is not canary.materialize_run_bytes
            or materialize_matrix is not canary.materialize_matrix
            or validate_public is not canary.validate_public_matrix
            or runtime_preflight is not _default_runtime_preflight
        ):
            raise CanaryError("the real harness cannot use injected acceptance interfaces")
        self._harness = harness
        self._materialize_run = materialize_run
        self._materialize_matrix = materialize_matrix
        self._validate_public = validate_public
        self._runtime_preflight = runtime_preflight
        self._private_parent = _absolute(private_parent)
        self._now = now

    def _load_controls(
        self,
        authority_path: str | Path,
        leases_path: str | Path,
        proof_root: str | Path,
        *,
        expected: authority_control.ControlRecords | None = None,
        proof_root_exists: bool,
        minimum_remaining_seconds: int = 0,
    ) -> authority_control.ControlRecords:
        try:
            return authority_control.load_control_records(
                authority_path,
                leases_path,
                proof_root,
                self._now(),
                private_parent=self._private_parent,
                expected_authority_sha256=(expected.authority_sha256 if expected else None),
                expected_leases_sha256=(expected.leases_sha256 if expected else None),
                proof_root_exists=proof_root_exists,
                minimum_remaining_seconds=minimum_remaining_seconds,
            )
        except authority_control.AuthorityError as exc:
            raise CanaryError(str(exc)) from exc

    def _plan(
        self,
        proof_root: Path,
        preflight: RuntimePreflight,
        controls: authority_control.ControlRecords,
    ) -> MatrixPlan:
        runs = []
        for role in RUN_ROLES:
            role_root = proof_root / RUN_ROOT_NAMES[role]
            command = build_harness_command(
                role,
                role_root,
                preflight.source_root,
                preflight.exe_override,
                controls,
            )
            parsed = harness.parse_args(list(command[3:]))
            protocol = harness.validate_runtime_protocol(parsed)
            runs.append(RunPlan(
                role=role,
                root=role_root,
                command=command,
                launch_arguments=tuple(protocol.launch_arguments),
                input_sequences=tuple(protocol.input_sequences),
                command_sha256=preflight.command_sha256,
            ))
        return MatrixPlan(proof_root, tuple(runs))

    def _prepare(
        self,
        proof_root: str | Path,
        authority_path: str | Path,
        leases_path: str | Path,
        source_root: str | Path | None,
        exe_override: str | Path | None,
    ) -> tuple[Path, RuntimePreflight, authority_control.ControlRecords]:
        if source_root is None or exe_override is None:
            raise CanaryError("source root and executable override are required")
        validated_root = validate_proof_root(
            proof_root,
            create=False,
            private_parent=self._private_parent,
        )
        source, override = _validate_runtime_inputs(validated_root, source_root, exe_override)
        controls = self._load_controls(
            authority_path,
            leases_path,
            validated_root,
            proof_root_exists=False,
        )
        preflight = self._runtime_preflight(source, override)
        if (
            preflight.source_root.resolve() != source.resolve()
            or preflight.exe_override.resolve() != override.resolve()
            or not _DIGEST.fullmatch(preflight.ambient_executable_sha256)
            or preflight.ambient_executable_sha256 != _file_sha256(source / "BEA.exe")
            or preflight.executable_sha256 != canary.CANONICAL_SHA256
            or preflight.template_sha256 != canary.TEMPLATE_SHA256
            or not _DIGEST.fullmatch(preflight.command_sha256)
        ):
            raise CanaryError("runtime preflight result drifted from the canonical protocol")
        return validated_root, preflight, controls

    def dry_run(
        self,
        proof_root: str | Path,
        authority_path: str | Path,
        leases_path: str | Path,
        source_root: str | Path | None,
        exe_override: str | Path | None,
    ) -> MatrixPlan:
        validated_root, preflight, controls = self._prepare(
            proof_root,
            authority_path,
            leases_path,
            source_root,
            exe_override,
        )
        return self._plan(validated_root, preflight, controls)

    def run_live(
        self,
        proof_root: str | Path,
        authority_path: str | Path,
        leases_path: str | Path,
        arm_live: str,
        source_root: str | Path,
        exe_override: str | Path,
    ) -> MatrixResult:
        if arm_live != LIVE_ARM_PHRASE:
            raise CanaryError(f"live canary requires exact arm phrase {LIVE_ARM_PHRASE!r}")
        candidate_root, preflight, controls = self._prepare(
            proof_root,
            authority_path,
            leases_path,
            source_root,
            exe_override,
        )
        validated_root = validate_proof_root(
            candidate_root,
            create=True,
            private_parent=self._private_parent,
        )
        plan = self._plan(validated_root, preflight, controls)

        records: list[_PrivateRun] = []
        public_runs: list[dict[str, Any]] = []
        for run in plan.runs:
            _require_ambient_executable_unchanged(preflight)
            self._load_controls(
                controls.authority_path,
                controls.leases_path,
                validated_root,
                expected=controls,
                proof_root_exists=True,
                minimum_remaining_seconds=authority_control.MINIMUM_ROLE_AUTHORITY_SECONDS,
            )
            result = self._harness(run.role, run.root, run.command)
            record = _collect_private_run(run.role, run.root, result)
            if record.process.get("runId") != record.run_id:
                raise CanaryError(f"{run.role} process receipt run ID drifted")
            if (
                record.command_sha256 != run.command_sha256
                or record.template_sha256 != preflight.template_sha256
                or record.executable_sha256 != preflight.executable_sha256
            ):
                raise CanaryError(f"{run.role} private evidence drifted from the dry-run preflight")
            _ensure_distinct((*records, record))
            public_run = _materialize_stable_run(record, self._materialize_run)
            records.append(record)
            public_runs.append(public_run)
        controls = self._load_controls(
            controls.authority_path,
            controls.leases_path,
            validated_root,
            expected=controls,
            proof_root_exists=True,
        )
        _require_ambient_executable_unchanged(preflight)
        for record in records:
            _require_unchanged_private_run(record)

        try:
            matrix = dict(self._materialize_matrix(public_runs))
            self._validate_public(matrix)
            _assert_public_safe(
                matrix,
                (validated_root, preflight.source_root, preflight.exe_override),
            )
        except CanaryError:
            raise
        except (OSError, TypeError, ValueError) as exc:
            raise CanaryError(f"could not materialize sanitized canary matrix: {exc}") from exc

        summary_path = validated_root / SANITIZED_SUMMARY_NAME
        summary_raw = _canonical_json_bytes(matrix)
        manifest_path = validated_root / PRIVATE_MANIFEST_NAME
        for target in (summary_path, manifest_path):
            if target.exists() or target.is_symlink():
                raise CanaryError(f"refusing pre-existing proof output: {target}")
        private_manifest = {
            "schemaVersion": PRIVATE_MANIFEST_SCHEMA,
            "actionFamily": ACTION_FAMILY,
            "createdAtUtc": _format_utc(self._now()),
            "proofRoot": str(validated_root),
            "authoritySha256": controls.authority_sha256,
            "leasesSha256": controls.leases_sha256,
            "sanitizedSummary": {
                "path": str(summary_path),
                "sha256": _sha256(summary_raw),
            },
            "runs": [
                {
                    "role": row.role,
                    "root": str(row.root),
                    "artifact": {"path": str(row.artifact_path), "sha256": row.artifact_sha256},
                    "cdbLog": {"path": str(row.log_path), "sha256": row.log_sha256},
                    "receipt": {"path": str(row.receipt_path), "sha256": row.receipt_sha256},
                    "process": dict(row.process),
                }
                for row in records
            ],
        }
        manifest_raw = _canonical_json_bytes(private_manifest)
        for record in records:
            _require_unchanged_private_run(record)
        _require_ambient_executable_unchanged(preflight)
        _publish_outputs(manifest_path, manifest_raw, summary_path, summary_raw)
        return MatrixResult(manifest_path, summary_path)


def _plan_payload(plan: MatrixPlan) -> Mapping[str, Any]:
    return {
        "mode": "dry-run",
        "proofRoot": str(plan.proof_root),
        "runs": [
            {
                "role": run.role,
                "root": str(run.root),
                "command": list(run.command),
                "launchArguments": list(run.launch_arguments),
                "inputSequences": list(run.input_sequences),
                "privateCommandSha256": run.command_sha256,
            }
            for run in plan.runs
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--proof-root", required=True, type=Path)
    parser.add_argument("--authority", required=True, type=Path)
    parser.add_argument("--leases", required=True, type=Path)
    parser.add_argument("--source-root", type=Path, default=harness.DEFAULT_GAME_ROOT)
    parser.add_argument("--exe-override", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--arm-live", default="")
    args = parser.parse_args(argv)

    try:
        executor = MatrixExecutor()
        if args.dry_run:
            if args.exe_override is None:
                raise CanaryError("--exe-override is required for a complete dry run")
            plan = executor.dry_run(
                args.proof_root,
                args.authority,
                args.leases,
                args.source_root,
                args.exe_override,
            )
            print(json.dumps(_plan_payload(plan), indent=2))
            return 0
        if args.exe_override is None:
            raise CanaryError("--exe-override is required for a live canary")
        result = executor.run_live(
            args.proof_root,
            args.authority,
            args.leases,
            args.arm_live,
            args.source_root,
            args.exe_override,
        )
        print(json.dumps({
            "privateManifest": str(result.private_manifest),
            "sanitizedSummary": str(result.sanitized_summary),
        }, indent=2))
        return 0
    except CanaryError as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
