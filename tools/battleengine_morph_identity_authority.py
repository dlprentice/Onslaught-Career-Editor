#!/usr/bin/env python3
"""Validate the private authority and lease controls for the morph canary."""

from __future__ import annotations

from dataclasses import dataclass
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PROOF_PARENT = ROOT / "local-proofs"
AUTHORITY_SCHEMA = "onslaught-battleengine-morph-identity-canary-authority.v1"
LEASE_SCHEMA = "onslaught-battleengine-morph-identity-canary-resource-leases.v1"
ACTION_FAMILY = "copied-runtime-battleengine-identity-canary"
LIVE_ARM_PHRASE = "RUN BATTLEENGINE MORPH IDENTITY CANARY"
REQUIRED_ALLOWED_ACTIONS = (
    "unpatched AppCore safe-copy materialization",
    "copied-profile control binding",
    "managed launch/stop",
    "exact-PID local CDB attach",
    "read-only module/register/memory inspection",
    "one-shot hardware execution probes",
    "exact-window Q input",
    "hashing",
    "local materialization",
    "validation",
)
REQUIRED_FORBIDDEN_ACTIONS = (
    "installed-game/original mutation",
    "copied-executable or process-memory writes",
    "remote debugging",
    "broadcast/background input",
    "unknown process termination",
    "Ghidra mutation",
    "raw-proof publication",
    "destructive proof cleanup",
)
REQUIRED_RESOURCES = (
    "interactive-winui-desktop",
    "bea-runtime",
    "cdb-debugger",
    "local-proof-archive-write",
)
REQUIRED_VALIDATION_GATES = (
    r"py -3 tools\battleengine_morph_identity_canary_test.py",
    r"py -3 tools\run_battleengine_morph_identity_canary_test.py",
    r"py -3 tools\runtime_process_identity_test.py",
    r"py -3 tools\start_cdb_server_test.py",
    r"py -3 tools\send_game_window_input_test.py",
    r"py -3 tools\winui_safe_copy_live_runtime_smoke_test.py",
    "npm run test:hard-payload-safety",
    "npm run test:doc-commands",
    "npm run test:md-links",
    "npm run test:repo-hygiene",
    "git diff --check",
)
REQUIRED_CLEANUP = (
    "release held keys; detach exact receipt-bound CDB; stop exact receipt-bound "
    "managed BEA; verify zero receipt-owned BEA/CDB processes"
)
REQUIRED_ROLLBACK = (
    "preserve failed private diagnostics; perform owned cleanup; discard the "
    "interrupted run; repeat only from a fresh copy and process"
)
MAX_CONTROL_FILE_BYTES = 1024 * 1024
MINIMUM_ROLE_AUTHORITY_SECONDS = 300
_DIGEST = re.compile(r"[0-9a-f]{64}")
_AUTHORITY_KEYS = {
    "schemaVersion",
    "actionFamily",
    "issuedAtUtc",
    "expiresAtUtc",
    "proofRoot",
    "allowedActions",
    "forbiddenActions",
    "maxSpendUsd",
    "validationGates",
    "cleanup",
    "rollback",
}
_LEASE_KEYS = {
    "schemaVersion",
    "actionFamily",
    "issuedAtUtc",
    "expiresAtUtc",
    "owner",
    "leases",
}
_LEASE_ROW_KEYS = {"resource", "owner", "exclusive", "acquiredAtUtc", "expiresAtUtc"}


class AuthorityError(RuntimeError):
    """Raised when the current private runtime authority is invalid."""


@dataclass(frozen=True)
class ControlRecords:
    authority_path: Path
    authority: Mapping[str, Any]
    authority_sha256: str
    leases_path: Path
    leases: Mapping[str, Any]
    leases_sha256: str


def _absolute(path: str | Path) -> Path:
    return Path(path).expanduser().absolute()


def _normalized(path: str | Path) -> str:
    return os.path.normcase(str(_absolute(path).resolve(strict=False)))


def _same_path(left: str | Path, right: str | Path) -> bool:
    return _normalized(left) == _normalized(right)


def _is_same_or_under(path: str | Path, root: str | Path) -> bool:
    try:
        return os.path.commonpath((_normalized(path), _normalized(root))) == _normalized(root)
    except ValueError:
        return False


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


def validate_private_proof_root(
    proof_root: str | Path,
    *,
    private_parent: str | Path = PRIVATE_PROOF_PARENT,
    require_exists: bool | None = None,
) -> Path:
    parent_input = _absolute(private_parent)
    candidate_input = _absolute(proof_root)
    if has_reparse_or_symlink_ancestor(parent_input) or has_reparse_or_symlink_ancestor(candidate_input):
        raise AuthorityError("proof root includes a reparse or symlink path component")
    parent = parent_input.resolve(strict=False)
    candidate = candidate_input.resolve(strict=False)
    if candidate.parent != parent:
        raise AuthorityError("proof root must be a direct child of the ignored repository local-proofs root")
    if not candidate.name.startswith("battleengine-morph-identity-canary-"):
        raise AuthorityError("proof root name does not identify the BattleEngine morph canary")
    if require_exists is True and not candidate.is_dir():
        raise AuthorityError("proof root must already exist")
    if require_exists is False and (candidate.exists() or candidate.is_symlink()):
        raise AuthorityError("proof root must be fresh and absent")
    return candidate


def parse_utc(value: Any, label: str) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise AuthorityError(f"{label} must be an RFC 3339 UTC timestamp ending in Z")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"{label} is not a valid UTC timestamp") from exc
    if parsed.utcoffset() != dt.timedelta(0):
        raise AuthorityError(f"{label} must be UTC")
    return parsed.astimezone(dt.timezone.utc)


def _require_object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AuthorityError(f"{label} must be a JSON object")
    return value


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise AuthorityError(f"{label} keys do not match the exact schema")


def _require_exact_string_set(value: Any, expected: Sequence[str], label: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise AuthorityError(f"{label} must be a string array")
    if len(value) != len(expected) or len(set(value)) != len(value) or set(value) != set(expected):
        raise AuthorityError(f"{label} does not match the approved set")


def validate_authority(
    authority: Any,
    proof_root: str | Path,
    now: dt.datetime,
) -> None:
    value = _require_object(authority, "authority")
    _require_exact_keys(value, _AUTHORITY_KEYS, "authority")
    if value["schemaVersion"] != AUTHORITY_SCHEMA or value["actionFamily"] != ACTION_FAMILY:
        raise AuthorityError("authority schema or action family mismatch")
    if not isinstance(value["proofRoot"], str) or not _same_path(value["proofRoot"], proof_root):
        raise AuthorityError("authority proofRoot does not match the requested proof root")
    _require_exact_string_set(value["allowedActions"], REQUIRED_ALLOWED_ACTIONS, "authority allowedActions")
    _require_exact_string_set(value["forbiddenActions"], REQUIRED_FORBIDDEN_ACTIONS, "authority forbiddenActions")
    _require_exact_string_set(value["validationGates"], REQUIRED_VALIDATION_GATES, "authority validationGates")
    if type(value["maxSpendUsd"]) is not int or value["maxSpendUsd"] != 0:
        raise AuthorityError("authority maxSpendUsd must be the integer 0")
    if value["cleanup"] != REQUIRED_CLEANUP or value["rollback"] != REQUIRED_ROLLBACK:
        raise AuthorityError("authority cleanup or rollback contract mismatch")
    issued = parse_utc(value["issuedAtUtc"], "authority issuedAtUtc")
    expires = parse_utc(value["expiresAtUtc"], "authority expiresAtUtc")
    if issued > now or issued >= expires or now >= expires:
        raise AuthorityError("authority is not currently active")


def validate_leases(leases: Any, now: dt.datetime) -> None:
    value = _require_object(leases, "resource leases")
    _require_exact_keys(value, _LEASE_KEYS, "resource leases")
    if value["schemaVersion"] != LEASE_SCHEMA or value["actionFamily"] != ACTION_FAMILY:
        raise AuthorityError("resource lease schema or action family mismatch")
    owner = value["owner"]
    if not isinstance(owner, str) or not owner.strip():
        raise AuthorityError("resource lease owner must be a non-empty string")
    issued = parse_utc(value["issuedAtUtc"], "resource leases issuedAtUtc")
    expires = parse_utc(value["expiresAtUtc"], "resource leases expiresAtUtc")
    if issued > now or issued >= expires or now >= expires:
        raise AuthorityError("resource leases are not currently active")
    rows = value["leases"]
    if not isinstance(rows, list) or len(rows) != len(REQUIRED_RESOURCES):
        raise AuthorityError("resource leases must contain every required resource exactly once")
    resources: list[str] = []
    for index, row_value in enumerate(rows):
        row = _require_object(row_value, f"resource leases[{index}]")
        _require_exact_keys(row, _LEASE_ROW_KEYS, f"resource leases[{index}]")
        if row["owner"] != owner or row["exclusive"] is not True:
            raise AuthorityError("resource leases contain a conflicting or non-exclusive owner")
        acquired = parse_utc(row["acquiredAtUtc"], f"resource leases[{index}].acquiredAtUtc")
        row_expires = parse_utc(row["expiresAtUtc"], f"resource leases[{index}].expiresAtUtc")
        if acquired < issued or acquired > now or row_expires != expires or now >= row_expires:
            raise AuthorityError("resource lease interval does not match the active lease envelope")
        resources.append(row["resource"])
    if len(set(resources)) != len(resources) or set(resources) != set(REQUIRED_RESOURCES):
        raise AuthorityError("resource leases are missing or duplicated")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AuthorityError(f"control JSON contains duplicate key {key!r}")
        result[key] = value
    return result


def _read_control_file(
    path: str | Path,
    label: str,
    *,
    private_parent: Path,
) -> tuple[Path, Mapping[str, Any], str]:
    candidate = _absolute(path)
    if not _is_same_or_under(candidate, private_parent) or _same_path(candidate, private_parent):
        raise AuthorityError(f"{label} must be beneath the ignored repository local-proofs root")
    if has_reparse_or_symlink_ancestor(candidate):
        raise AuthorityError(f"{label} is reparse or symlink routed")
    try:
        with candidate.open("rb") as stream:
            before = os.fstat(stream.fileno())
            raw = stream.read(MAX_CONTROL_FILE_BYTES + 1)
            after = os.fstat(stream.fileno())
    except OSError as exc:
        raise AuthorityError(f"could not read {label}: {exc}") from exc
    if len(raw) > MAX_CONTROL_FILE_BYTES:
        raise AuthorityError(f"{label} exceeds the 1 MiB limit")
    if (before.st_dev, before.st_ino, before.st_size) != (after.st_dev, after.st_ino, after.st_size):
        raise AuthorityError(f"{label} changed while it was read")
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthorityError(f"{label} is not valid UTF-8 JSON") from exc
    return candidate.resolve(), _require_object(payload, label), hashlib.sha256(raw).hexdigest()


def load_control_records(
    authority_path: str | Path,
    leases_path: str | Path,
    proof_root: str | Path,
    now: dt.datetime,
    *,
    private_parent: str | Path = PRIVATE_PROOF_PARENT,
    expected_authority_sha256: str | None = None,
    expected_leases_sha256: str | None = None,
    proof_root_exists: bool | None = None,
    minimum_remaining_seconds: int = 0,
) -> ControlRecords:
    parent_input = _absolute(private_parent)
    if has_reparse_or_symlink_ancestor(parent_input):
        raise AuthorityError("ignored repository local-proofs root is reparse or symlink routed")
    parent = parent_input.resolve(strict=False)
    root = validate_private_proof_root(
        proof_root,
        private_parent=parent_input,
        require_exists=proof_root_exists,
    )
    authority_file, authority, authority_sha256 = _read_control_file(
        authority_path,
        "authority file",
        private_parent=parent,
    )
    leases_file, leases, leases_sha256 = _read_control_file(
        leases_path,
        "resource lease file",
        private_parent=parent,
    )
    if authority_file == leases_file or authority_file.parent != leases_file.parent:
        raise AuthorityError("authority and lease files must be distinct siblings")
    control_root = authority_file.parent
    if (
        control_root.parent != parent
        or not control_root.name.startswith("battleengine-morph-identity-canary-control-")
        or authority_file.name != "authority.json"
        or leases_file.name != "leases.json"
    ):
        raise AuthorityError(
            "authority and lease files must use the exact ignored canary control-directory layout"
        )
    if _is_same_or_under(authority_file, root) or _is_same_or_under(leases_file, root):
        raise AuthorityError("authority and lease files must not occupy the fresh proof root")
    if expected_authority_sha256 is not None:
        if not _DIGEST.fullmatch(expected_authority_sha256) or authority_sha256 != expected_authority_sha256:
            raise AuthorityError("authority file SHA-256 changed")
    if expected_leases_sha256 is not None:
        if not _DIGEST.fullmatch(expected_leases_sha256) or leases_sha256 != expected_leases_sha256:
            raise AuthorityError("resource lease file SHA-256 changed")
    validate_authority(authority, root, now)
    validate_leases(leases, now)
    if type(minimum_remaining_seconds) is not int or minimum_remaining_seconds < 0:
        raise AuthorityError("minimum remaining authority duration must be a nonnegative integer")
    minimum_expiration = now + dt.timedelta(seconds=minimum_remaining_seconds)
    if (
        parse_utc(authority["expiresAtUtc"], "authority expiresAtUtc") < minimum_expiration
        or parse_utc(leases["expiresAtUtc"], "resource leases expiresAtUtc") < minimum_expiration
    ):
        raise AuthorityError("authority or resource leases expire before the bounded role can finish")
    return ControlRecords(
        authority_path=authority_file,
        authority=authority,
        authority_sha256=authority_sha256,
        leases_path=leases_file,
        leases=leases,
        leases_sha256=leases_sha256,
    )
