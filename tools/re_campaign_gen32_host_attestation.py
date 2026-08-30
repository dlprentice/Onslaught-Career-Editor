#!/usr/bin/env python3
"""Attest the frozen Generation-32 campaign on the recovered Linux host.

The Generation-32 READY receipt is immutable and records the Windows checkout
where it was sealed.  This adapter proves that those exact logical paths bind
to the recovered ProjectData corpus, validates every reachable reducer before
the first frozen import, and replays the unchanged Generation-32 builder into a
temporary directory.  It never rewrites a campaign receipt or reducer.

This is intentionally Generation-32-specific.  An unexpected subprocess,
foreign drive, path alias, symlink, hardlink in a pinned file, or unrecognized
builder input fails closed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import stat
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable


ATTESTATION_SCHEMA = "bea.re.generation32-linux-host-replay-attestation.v1"
WINDOWS_REPO = r"C:\Users\david\source\Onslaught-Career-Editor"
WINDOWS_REPO_PREFIX = WINDOWS_REPO + "\\"

GEN32_RELATIVE = Path(
    "re-campaign-incident-recovery-20260808-v1/"
    "generation-32-current-8329-db18625-v1"
)
GEN32_REPLICA_RELATIVE = Path(
    "re-campaign-incident-recovery-20260808-v1/"
    "generation-32-current-8329-db18625-replica-v1"
)
GEN32_AUTHORITY_RELATIVE = Path(
    "re-campaign-incident-recovery-20260808-v1/"
    "generation-32-current-8329-db18625-authority.ready.json"
)
GEN31_RELATIVE = Path(
    "re-campaign-incident-recovery-20260808-v1/"
    "generation-31-current-8329-db18624-v2"
)
GEN31_AUTHORITY_RELATIVE = Path(
    "re-campaign-incident-recovery-20260808-v1/"
    "generation-31-current-8329-db18624-authority.ready.json"
)

GEN32_READY_BYTES = 9_539_597
GEN32_READY_SHA256 = "08ed89644ed25feb9e85fefb5b31ab2bdecbbd91b8aca720e20c53a7fbc5e73f"
GEN32_REDUCER_ID = "4c465010b3240d476eb15c89fcfa51cd155936316e897e6f6a7b450df5944db3"
GEN32_AUTHORITY_BYTES = 3_612
GEN32_AUTHORITY_SHA256 = "6238430dffb5c80517e17411db7e4505250b01f7226bcc982af675b0fe776b37"
GEN32_REPLICA_READY_SHA256 = "e8230547f694698e6fd1bb0ee6ccc8661b780cb408c283abbc12ed9c956e2cf2"
GEN32_AUTHORITY_SCHEMA = (
    "bea.re.generation32-current-8329-db18625-external-authority.v1"
)
GEN32_OWNER_SHA256 = "4408b35999f26355ef2737341e45fbf033ea26a5e337bbc0badf21eba4c54705"
GEN32_BUILDER_SHA256 = "0569a14502bc4142ba1f1472dc1ce2257b3df36a0f59c81b39bcea6c950260f6"

GEN31_READY_SHA256 = "2e77c62d236edacbe4974ca844a6ac0b692e84b3259b884b8afc25a29aad4219"
GEN31_REDUCER_ID = "21ad46fff9d2aec8034a4edcf2c83fad627c2fcae3a9a21ebac7e03976c7627b"
GEN31_AUTHORITY_SHA256 = "b29b75c10e59ec190fceb87453545d1eeb159bc3b69fb9b308165c030b0e2485"
GEN31_CANONICAL_LOGICAL = (
    WINDOWS_REPO_PREFIX
    + "local-lab\\"
    + str(GEN31_RELATIVE).replace("/", "\\")
)

BOOTSTRAP_RELATIVE = Path("tools/re_campaign_frozen_bootstrap.py")
BOOTSTRAP_SHA256 = "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b"
CLOSURE_RELATIVE = "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv"
CLOSURE_SHA256 = "cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974"

LOST_GEN4_LOGICAL = WINDOWS_REPO_PREFIX + (
    "local-lab\\re-campaign\\"
    "campaign-2026-08-02-observed40-generation-4-v5-carried-r2"
)
LOST_GEN4_READY_BYTES = 11_729
LOST_GEN4_READY_SHA256 = "5b32978da40d91f557b971da6ae0a23b3971fa1afe922c443d6ae039c7ede8ed"
LOST_ATOMIC14_RELATIVE = (
    "local-lab/console-callback-atomic14-20260803-v1/"
    "formal-proof-v2/formal-proof.ready.json"
)
EXPECTED_LOGICAL_MAPPING_SET_SHA256 = (
    "6b5d7bfa64576417b2afeadc85edee39260f64d7269ca4c595f8d64c57c0c671"
)

OUTPUTS = (
    "campaign-functions.tsv",
    "campaign-residuals.tsv",
    "campaign-questions.tsv",
    "campaign-scenarios.tsv",
    "campaign-levers.tsv",
    "campaign-contracts.tsv",
    "campaign-adjudications.tsv",
    "campaign-supersessions.tsv",
)
EXPECTED_COUNTS = {
    "functions": 8329,
    "residuals": 6035,
    "questions": 15325,
    "scenarios": 72,
    "levers": 903,
    "contracts": 14365,
    "adjudications": 5898,
    "supersessions": 592,
}


class AttestationError(RuntimeError):
    """The exact Gen32 host/replay contract failed closed."""


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _plain_root(raw: Path, label: str) -> Path:
    path = Path(os.path.abspath(raw.expanduser()))
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            ancestor = current.lstat()
        except OSError as exc:
            raise AttestationError(f"{label} is absent: {exc}") from exc
        if stat.S_ISLNK(ancestor.st_mode):
            raise AttestationError(f"{label} traverses a symlink: {current}")
    try:
        info = path.lstat()
    except OSError as exc:
        raise AttestationError(f"{label} is absent: {exc}") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise AttestationError(f"{label} is not a plain directory: {path}")
    return path.resolve(strict=True)


def _safe_components(raw: str, separator: str, label: str) -> tuple[str, ...]:
    if not raw or "\x00" in raw:
        raise AttestationError(f"{label} is empty or contains NUL")
    parts = tuple(raw.split(separator))
    if not parts or any(not part or part in {".", ".."} for part in parts):
        raise AttestationError(f"{label} contains empty or traversing components")
    for part in parts:
        if ":" in part or part.endswith((" ", ".")):
            raise AttestationError(f"{label} contains an ambiguous component: {part!r}")
    return parts


def _plain_descendant(
    root: Path,
    parts: Iterable[str],
    label: str,
    *,
    allow_missing_leaf: bool = False,
) -> Path:
    components = tuple(parts)
    if not components:
        return root
    current = root
    for index, part in enumerate(components):
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError as exc:
            if allow_missing_leaf:
                return current.joinpath(*components[index + 1 :])
            raise AttestationError(f"{label} is absent: {current}") from exc
        except OSError as exc:
            raise AttestationError(f"cannot inspect {label}: {exc}") from exc
        if stat.S_ISLNK(info.st_mode):
            raise AttestationError(f"{label} traverses a symlink: {current}")
        if index < len(components) - 1 and not stat.S_ISDIR(info.st_mode):
            raise AttestationError(f"{label} has a non-directory ancestor: {current}")
    return current


def _require_plain_file(
    path: Path,
    label: str,
    *,
    byte_count: int | None = None,
    digest: str | None = None,
) -> Path:
    try:
        info = path.lstat()
    except OSError as exc:
        raise AttestationError(f"{label} is absent: {exc}") from exc
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
    ):
        raise AttestationError(f"{label} is not a plain single-link file: {path}")
    if byte_count is not None and info.st_size != byte_count:
        raise AttestationError(f"{label} byte count differs")
    if digest is not None and sha256_path(path) != digest:
        raise AttestationError(f"{label} SHA-256 differs")
    return path


@dataclass(frozen=True)
class MappingRecord:
    purpose: str
    logicalWindowsPath: str
    physicalLinuxPath: str
    exists: bool
    receiptRewritten: bool = False


class HostPaths:
    """Bind the one sealed Windows repository namespace to two Linux roots."""

    def __init__(self, repo_root: Path, lab_root: Path):
        self.repo = _plain_root(repo_root, "canonical Git repository")
        self.lab = _plain_root(lab_root, "recovered local-lab root")
        if self.repo == self.lab:
            raise AttestationError("repository and recovered local-lab roots must differ")
        self.bootstrap_records: list[MappingRecord] = []

    def _from_parts(
        self,
        parts: tuple[str, ...],
        label: str,
        *,
        raw_identity: str,
    ) -> Path:
        if parts[0] == "local-lab":
            root = self.lab
            relative = parts[1:]
        else:
            root = self.repo
            relative = parts
        normalized_relative = "local-lab/" + "/".join(relative) if root == self.lab else "/".join(relative)
        allow_missing = raw_identity == LOST_GEN4_LOGICAL or normalized_relative == LOST_ATOMIC14_RELATIVE
        return _plain_descendant(
            root,
            relative,
            label,
            allow_missing_leaf=allow_missing,
        )

    def resolve(self, value: object, label: str = "host-bound path") -> Path:
        if isinstance(value, Path):
            raw = os.fspath(value)
        elif isinstance(value, str):
            raw = value
        else:
            raise AttestationError(f"{label} is not path text")
        if not raw or "\x00" in raw:
            raise AttestationError(f"{label} is empty or contains NUL")

        if raw == WINDOWS_REPO:
            return self.repo
        if raw.startswith(WINDOWS_REPO_PREFIX):
            if "/" in raw:
                raise AttestationError(f"{label} mixes Windows path separators")
            relative = raw[len(WINDOWS_REPO_PREFIX) :]
            return self._from_parts(
                _safe_components(relative, "\\", label),
                label,
                raw_identity=raw,
            )
        if raw.startswith(("\\\\", "\\\\?\\", "\\\\.\\")):
            raise AttestationError(f"{label} uses an unauthorized UNC/device root")
        if len(raw) >= 2 and raw[1] == ":":
            raise AttestationError(f"{label} uses an unauthorized Windows drive")

        candidate = Path(raw)
        if candidate.is_absolute():
            if ".." in candidate.parts:
                raise AttestationError(f"{label} contains traversal")
            for root in (self.repo, self.lab):
                try:
                    relative = candidate.relative_to(root)
                except ValueError:
                    continue
                return _plain_descendant(root, relative.parts, label)
            raise AttestationError(f"{label} is outside both authorized Linux roots")

        if "\\" in raw and "/" in raw:
            raise AttestationError(f"{label} mixes path separators")
        separator = "\\" if "\\" in raw else "/"
        return self._from_parts(
            _safe_components(raw, separator, label),
            label,
            raw_identity=raw.replace("\\", "/"),
        )

    def map_bootstrap(self, raw: str) -> Path:
        purpose = (
            "historicalProjectionReady"
            if raw.endswith("campaign.ready.json")
            else "parentCampaign"
        )
        path = self.resolve(raw, f"bootstrap {purpose}")
        exists = path.exists()
        self.bootstrap_records.append(
            MappingRecord(
                purpose=purpose,
                logicalWindowsPath=raw,
                physicalLinuxPath=os.fspath(path),
                exists=exists,
            )
        )
        return path


class RoutingRoot(os.PathLike[str]):
    def __init__(self, paths: HostPaths):
        self.paths = paths

    def __fspath__(self) -> str:
        return os.fspath(self.paths.repo)

    def __str__(self) -> str:
        return os.fspath(self.paths.repo)

    def __truediv__(self, other: object) -> Path:
        return self.paths.resolve(other, "routed repository child")

    def resolve(self, *_args: object, **_kwargs: object) -> Path:
        return self.paths.repo


class BuilderRoutingRoot(RoutingRoot):
    def __init__(self, paths: HostPaths, receipt_sources: set[str]):
        super().__init__(paths)
        self.receipt_sources = receipt_sources

    def __truediv__(self, other: object) -> Path:
        raw = os.fspath(other).replace("\\", "/")
        if raw == CLOSURE_RELATIVE:
            return _require_plain_file(
                self.paths.resolve(raw, "sealed Gen32 closure"),
                "sealed Gen32 closure",
            )
        if raw in self.receipt_sources:
            return _require_plain_file(
                self.paths.resolve(raw, "sealed Gen32 receipt source"),
                "sealed Gen32 receipt source",
            )
        raise AttestationError(f"Gen32 builder requested an unsealed repository input: {raw}")


class _OsPathProxy:
    def __init__(self, paths: HostPaths):
        self.paths = paths

    def abspath(self, value: object) -> str:
        raw = os.fspath(value)
        if raw == WINDOWS_REPO or raw.startswith(WINDOWS_REPO_PREFIX):
            return os.fspath(self.paths.resolve(raw, "legacy absolute path"))
        if len(raw) >= 2 and raw[1] == ":":
            raise AttestationError(f"unauthorized Windows path reached abspath: {raw!r}")
        return os.path.abspath(raw)

    def __getattr__(self, name: str) -> object:
        return getattr(os.path, name)


class _OsProxy:
    def __init__(self, paths: HostPaths):
        self.path = _OsPathProxy(paths)

    def __getattr__(self, name: str) -> object:
        if name in {
            "execl",
            "execle",
            "execlp",
            "execlpe",
            "execv",
            "execve",
            "execvp",
            "execvpe",
            "fork",
            "forkpty",
            "popen",
            "posix_spawn",
            "posix_spawnp",
            "spawnl",
            "spawnle",
            "spawnlp",
            "spawnlpe",
            "spawnv",
            "spawnve",
            "spawnvp",
            "spawnvpe",
            "system",
        }:
            raise AttestationError(
                f"process-creation API is unavailable in scoped Gen32 replay: os.{name}"
            )
        return getattr(os, name)


class _SubprocessProxy:
    def __init__(self, original: object):
        self._original = original

    def run(self, argv: object, *_args: object, **_kwargs: object) -> object:
        raise AttestationError(f"unexpected subprocess in scoped Gen32 replay: {argv!r}")

    def __getattr__(self, name: str) -> object:
        if name in {
            "Popen",
            "call",
            "check_call",
            "check_output",
            "getoutput",
            "getstatusoutput",
            "run",
        }:
            raise AttestationError(
                "process-creation API is unavailable in scoped Gen32 replay: "
                f"subprocess.{name}"
            )
        return getattr(self._original, name)


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AttestationError(f"cannot create module specification for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        if sys.modules.get(name) is module:
            del sys.modules[name]
        raise
    return module


def _load_bootstrap(repo: Path) -> tuple[ModuleType, Path]:
    path = _plain_descendant(repo, BOOTSTRAP_RELATIVE.parts, "tracked frozen bootstrap")
    _require_plain_file(path, "tracked frozen bootstrap", digest=BOOTSTRAP_SHA256)
    return _load_module("_bea_gen32_host_bootstrap", path), path


def _mapping_set_sha256(records: list[MappingRecord]) -> str:
    body = "".join(
        "\t".join(
            (
                row.purpose,
                row.logicalWindowsPath,
                row.physicalLinuxPath,
                "1" if row.exists else "0",
                "1" if row.receiptRewritten else "0",
            )
        )
        + "\n"
        for row in records
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def _logical_mapping_set_sha256(records: list[MappingRecord]) -> str:
    """Pin the sealed graph independently of its caller-selected Linux roots."""

    body = "".join(
        "\t".join(
            (
                row.purpose,
                row.logicalWindowsPath,
                "1" if row.exists else "0",
                "1" if row.receiptRewritten else "0",
            )
        )
        + "\n"
        for row in records
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AttestationError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise AttestationError(f"{label} is not a JSON object")
    return value


def _prevalidate(
    paths: HostPaths,
    campaign: Path,
    expected_ready_sha256: str,
    expected_reducer_id: str,
) -> tuple[ModuleType, dict[str, Any], Path, Path, str]:
    bootstrap, bootstrap_path = _load_bootstrap(paths.repo)
    bootstrap.VALIDATED_IDENTITIES.clear()
    bootstrap._repo_or_absolute = paths.map_bootstrap
    try:
        receipt, entry = bootstrap._validate_reachable_chain(
            campaign,
            expected_ready_sha256=expected_ready_sha256,
            expected_reducer_id=expected_reducer_id,
        )
    except bootstrap.BootstrapError as exc:
        raise AttestationError(f"frozen pre-import validation blocked: {exc}") from exc
    if receipt.get("generation") != 32:
        raise AttestationError("selected externally pinned campaign is not Generation 32")
    if len(bootstrap.VALIDATED_IDENTITIES) != 31:
        raise AttestationError(
            "prevalidated reducer identity count differs: "
            f"{len(bootstrap.VALIDATED_IDENTITIES)}"
        )
    missing = [row for row in paths.bootstrap_records if not row.exists]
    historical = [
        row for row in paths.bootstrap_records
        if row.purpose == "historicalProjectionReady"
    ]
    if (
        len(missing) != 1
        or missing[0].logicalWindowsPath != LOST_GEN4_LOGICAL
        or len(historical) != 3
    ):
        raise AttestationError("Gen32 chain does not match the exact lost-Gen4/oracle graph")
    logical_mapping_digest = _logical_mapping_set_sha256(paths.bootstrap_records)
    if logical_mapping_digest != EXPECTED_LOGICAL_MAPPING_SET_SHA256:
        raise AttestationError(
            f"Gen32 logical mapping set differs: {logical_mapping_digest}"
        )
    return (
        bootstrap,
        receipt,
        entry,
        bootstrap_path,
        _mapping_set_sha256(paths.bootstrap_records),
    )


def _manifest_file_map(root: Path, receipt: dict[str, Any]) -> dict[str, Path]:
    reducer = receipt.get("reducer")
    rows = reducer.get("files") if isinstance(reducer, dict) else None
    if not isinstance(rows, list) or len(rows) != 47:
        raise AttestationError("Gen32 reducer manifest does not contain 47 files")
    mapped: dict[str, Path] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise AttestationError("Gen32 reducer manifest row is malformed")
        relative = row["path"]
        path = root / relative
        _require_plain_file(path, f"reducer file {relative}")
        mapped[relative] = path
    if len(mapped) != 47:
        raise AttestationError("Gen32 reducer manifest repeats a path")
    return mapped


def _sealed_receipt_sources(receipt: dict[str, Any]) -> set[str]:
    advance = receipt.get("advance")
    rows = advance.get("rows") if isinstance(advance, dict) else None
    if not isinstance(rows, list) or len(rows) != 7_885:
        raise AttestationError("sealed Gen32 advance row set differs")
    sources = {
        row.get("receiptSources")
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("receiptSources"), str)
    }
    if len(sources) != 53:
        raise AttestationError(f"sealed Gen32 receipt-source set differs: {len(sources)}")
    return sources


def _reject_preloaded_manifest_modules(receipt: dict[str, Any]) -> None:
    reducer = receipt.get("reducer")
    rows = reducer.get("files") if isinstance(reducer, dict) else None
    if not isinstance(rows, list):
        raise AttestationError("Gen32 reducer manifest is malformed before import")
    owned_names = {
        Path(row["path"]).stem
        for row in rows
        if isinstance(row, dict)
        and isinstance(row.get("path"), str)
        and row["path"].endswith(".py")
    }
    contaminated = sorted(name for name in owned_names if name in sys.modules)
    if contaminated:
        raise AttestationError(
            "reducer-owned modules were loaded before the pre-import gate: "
            + ", ".join(contaminated)
        )


def _validate_external_authority(
    paths: HostPaths,
    bootstrap: ModuleType,
    campaign: Path,
    authority_path: Path,
) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    _require_plain_file(
        authority_path,
        "Generation-32 external authority",
        byte_count=GEN32_AUTHORITY_BYTES,
        digest=GEN32_AUTHORITY_SHA256,
    )
    authority = _read_json(authority_path, "Generation-32 external authority")
    campaign_block = authority.get("campaign")
    frozen_replays = authority.get("frozenReplays")
    if not isinstance(campaign_block, dict) or not isinstance(frozen_replays, dict):
        raise AttestationError("Generation-32 authority blocks are malformed")
    canonical_raw = campaign_block.get("canonical")
    replica_raw = campaign_block.get("replica")
    expected_canonical = WINDOWS_REPO_PREFIX + "local-lab\\" + str(GEN32_RELATIVE).replace("/", "\\")
    expected_replica = WINDOWS_REPO_PREFIX + "local-lab\\" + str(GEN32_REPLICA_RELATIVE).replace("/", "\\")
    if (
        authority.get("schema") != GEN32_AUTHORITY_SCHEMA
        or authority.get("verdict") != "READY"
        or authority.get("authorityClass") != "FULL_REPLAY_CAMPAIGN_AUTHORITY"
        or authority.get("generation") != 32
        or authority.get("counts") != EXPECTED_COUNTS
        or canonical_raw != expected_canonical
        or replica_raw != expected_replica
        or campaign_block.get("readySha256") != GEN32_READY_SHA256
        or campaign_block.get("readyBytes") != GEN32_READY_BYTES
        or campaign_block.get("reducerId") != GEN32_REDUCER_ID
        or campaign_block.get("replicaReadySha256") != GEN32_REPLICA_READY_SHA256
        or frozen_replays != {"canonical": "CAMPAIGN_VERIFIED", "replica": "CAMPAIGN_VERIFIED"}
        or "EIGHT_LEDGERS_BYTE_IDENTICAL" not in str(authority.get("ledgerDeterminism"))
        or authority.get("sealedClosure", {}).get("sha256") != CLOSURE_SHA256
    ):
        raise AttestationError("Generation-32 external authority identity differs")
    canonical = paths.resolve(canonical_raw, "authority canonical campaign")
    replica = paths.resolve(replica_raw, "authority replica campaign")
    if canonical != campaign:
        raise AttestationError("authority canonical does not select the requested campaign")
    try:
        replica_receipt, _replica_entry = bootstrap._validate_reducer(
            replica,
            expected_ready_sha256=GEN32_REPLICA_READY_SHA256,
            expected_reducer_id=GEN32_REDUCER_ID,
        )
    except bootstrap.BootstrapError as exc:
        raise AttestationError(f"Gen32 replica validation blocked: {exc}") from exc

    canonical_receipt = _read_json(campaign / "campaign.ready.json", "canonical Gen32 READY")
    for name in OUTPUTS:
        left = _require_plain_file(campaign / name, f"canonical {name}")
        right = _require_plain_file(replica / name, f"replica {name}")
        if left.stat().st_size != right.stat().st_size or sha256_path(left) != sha256_path(right):
            raise AttestationError(f"canonical/replica ledger differs: {name}")
    left_files = _manifest_file_map(campaign, canonical_receipt)
    right_files = _manifest_file_map(replica, replica_receipt)
    if set(left_files) != set(right_files):
        raise AttestationError("canonical/replica reducer path sets differ")
    for relative in sorted(left_files):
        left = left_files[relative]
        right = right_files[relative]
        if left.stat().st_size != right.stat().st_size or sha256_path(left) != sha256_path(right):
            raise AttestationError(f"canonical/replica reducer differs: {relative}")
    return authority, replica, replica_receipt


def _rebase_path_globals(module: ModuleType, paths: HostPaths) -> None:
    old_lab = paths.repo / "local-lab"
    for name, value in list(vars(module).items()):
        if not isinstance(value, Path):
            continue
        try:
            relative = value.relative_to(old_lab)
        except ValueError:
            continue
        setattr(module, name, paths.lab / relative)
    if hasattr(module, "REPO_ROOT"):
        module.REPO_ROOT = RoutingRoot(paths)


def _normalized_campaign_field(
    paths: HostPaths,
    campaign_module: ModuleType,
    key: str,
    value: object,
) -> object:
    if not isinstance(value, dict):
        return value
    normalized = copy.deepcopy(value)

    def bind(container: object, leaf: str, label: str) -> None:
        if not isinstance(container, dict) or not isinstance(container.get(leaf), str):
            raise AttestationError(f"{label} path leaf is malformed")
        container[leaf] = os.fspath(paths.resolve(container[leaf], label))

    if key == "parentCampaign":
        bind(normalized, "path", "Gen32 parentCampaign")
    elif key == "sourceSnapshot":
        bind(normalized, "path", "Gen32 sourceSnapshot")
        bind(normalized.get("specimen"), "path", "Gen32 sourceSnapshot specimen")
        parity = normalized.get("parityGraph")
        if not isinstance(parity, dict):
            raise AttestationError("Gen32 parityGraph is malformed")
        bind(parity.get("receipt"), "path", "Gen32 parityGraph receipt")
        bind(parity.get("bodyRanges"), "path", "Gen32 parityGraph body ranges")
        files = normalized.get("files")
        if not isinstance(files, dict) or set(files) != {
            "ledger-summary.json",
            "ledger-functions.tsv",
            "ledger-dark.tsv",
            "ledger-gaps.tsv",
            "ledger-unmapped.tsv",
            "ledger-native-handlers.tsv",
            "ledger-families.tsv",
        }:
            raise AttestationError("Gen32 sourceSnapshot file set differs")
        for name in sorted(files):
            bind(files[name], "path", f"Gen32 sourceSnapshot {name}")
    elif key == "advance":
        if (
            normalized.get("kind")
            != campaign_module.GENERATION32_STATIC_RECEIPT_RESEAT_ADVANCE_KIND
            or normalized.get("schema")
            != campaign_module.GENERATION32_STATIC_RECEIPT_RESEAT_ADVANCE_SCHEMA
        ):
            raise AttestationError("Gen32 advance identity differs during replay comparison")
        bind(normalized.get("snapshot"), "path", "Gen32 advance snapshot")
        bind(normalized.get("prepRoot"), "path", "Gen32 advance prepRoot")
    return normalized


def _install_host_hooks(
    paths: HostPaths,
    campaign_root: Path,
    receipt: dict[str, Any],
    entry: Path,
) -> tuple[ModuleType, ModuleType, set[str]]:
    _require_plain_file(entry, "frozen Gen32 owner", digest=GEN32_OWNER_SHA256)
    tools_root = entry.parent.resolve(strict=True)
    _reject_preloaded_manifest_modules(receipt)
    os.environ["BEA_REPO_ROOT"] = os.fspath(paths.repo)
    sys.path.insert(0, os.fspath(tools_root))
    campaign = _load_module("re_campaign", entry)

    frozen_modules: list[ModuleType] = []
    reducer_root = campaign_root / "_reducer"
    for module in list(sys.modules.values()):
        source = getattr(module, "__file__", None)
        if not isinstance(source, str):
            continue
        try:
            Path(source).resolve(strict=True).relative_to(reducer_root)
        except (OSError, ValueError):
            continue
        frozen_modules.append(module)
    for module in frozen_modules:
        _rebase_path_globals(module, paths)
        if hasattr(module, "os"):
            module.os = _OsProxy(paths)
        if hasattr(module, "subprocess"):
            module.subprocess = _SubprocessProxy(module.subprocess)

    campaign._resolve_repo_or_absolute = lambda raw, label: paths.resolve(raw, label)

    def receipt_bound(raw: object, expected_relative: str, label: str) -> Path:
        expected = paths.resolve(expected_relative, f"{label} expected slot")
        actual = paths.resolve(raw, label)
        if actual != expected:
            raise campaign.CampaignError(f"{label} path differs from its exact slot")
        return actual

    campaign._receipt_bound_repo_path = receipt_bound
    gen31_authority = paths.lab / GEN31_AUTHORITY_RELATIVE
    _require_plain_file(
        gen31_authority,
        "Generation-31 external authority",
        digest=GEN31_AUTHORITY_SHA256,
    )
    original_runtime_json = campaign._runtime_json

    def runtime_json(path: Path, label: str) -> dict[str, Any]:
        result = original_runtime_json(path, label)
        if Path(path).resolve() != gen31_authority.resolve():
            return result
        projected = copy.deepcopy(result)
        block = projected.get("campaign")
        if not isinstance(block, dict) or block.get("canonical") != GEN31_CANONICAL_LOGICAL:
            raise campaign.CampaignError("Generation-31 logical canonical path differs")
        mapped = paths.resolve(block["canonical"], "Generation-31 authority canonical")
        if mapped != paths.lab / GEN31_RELATIVE:
            raise campaign.CampaignError("Generation-31 canonical maps to the wrong host leaf")
        block["canonical"] = os.fspath(mapped)
        return projected

    campaign._runtime_json = runtime_json

    original_partition_context = campaign._partition_relation_context

    def partition_context(receipt_value: dict[str, Any]) -> dict[str, Any] | None:
        context = original_partition_context(receipt_value)
        if context is None:
            return None
        advance = context.get("advance")
        if (
            not isinstance(advance, dict)
            or advance.get("kind") != campaign.GHIDRA_PARTITION_RECOVERY_ADVANCE_KIND
        ):
            return context
        snapshot = advance.get("snapshot")
        ready = snapshot.get("ready") if isinstance(snapshot, dict) else None
        logical_root = snapshot.get("root") if isinstance(snapshot, dict) else None
        logical_leaf = ready.get("path") if isinstance(ready, dict) else None
        digest = ready.get("sha256") if isinstance(ready, dict) else None
        if not all(isinstance(item, str) and item for item in (logical_root, logical_leaf, digest)):
            raise campaign.CampaignError("partition recovery snapshot binding is malformed")
        physical = paths.resolve(logical_root, "partition recovery snapshot root") / logical_leaf
        expected_physical_ref = f"{physical.resolve()}#sha256={digest}"
        expected_logical_ref = f"{logical_root}\\{logical_leaf}#sha256={digest}"
        projected = copy.deepcopy(context)
        refs = projected.get("expectedEvidenceRefs")
        if not isinstance(refs, list) or not refs or refs[-1] != expected_physical_ref:
            raise campaign.CampaignError("partition physical evidence binding differs")
        refs[-1] = expected_logical_ref
        return projected

    campaign._partition_relation_context = partition_context
    campaign._normalized_campaign_field = lambda key, value: _normalized_campaign_field(
        paths, campaign, key, value
    )

    receipt_sources = _sealed_receipt_sources(receipt)
    builder_path = tools_root / "build_generation32_authority.py"
    _require_plain_file(builder_path, "frozen Gen32 builder", digest=GEN32_BUILDER_SHA256)
    builder = _load_module("build_generation32_authority", builder_path)
    builder.os = _OsProxy(paths)
    builder._repo_root = lambda: BuilderRoutingRoot(paths, receipt_sources)
    return campaign, builder, receipt_sources


def _walk_plain_files(root: Path, label: str) -> list[Path]:
    files: list[Path] = []
    stack = [root]
    while stack:
        directory = stack.pop()
        info = directory.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise AttestationError(f"{label} contains a non-plain directory: {directory}")
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as exc:
            raise AttestationError(f"cannot enumerate {label}: {exc}") from exc
        for entry in entries:
            path = Path(entry.path)
            entry_info = path.lstat()
            if stat.S_ISLNK(entry_info.st_mode):
                raise AttestationError(f"{label} contains a symlink: {path}")
            if stat.S_ISDIR(entry_info.st_mode):
                stack.append(path)
            elif stat.S_ISREG(entry_info.st_mode) and entry_info.st_nlink == 1:
                files.append(path)
            else:
                raise AttestationError(f"{label} contains a non-plain file: {path}")
    return sorted(files)


def _critical_fingerprint(paths: Iterable[Path]) -> tuple[str, int]:
    rows: list[str] = []
    file_count = 0
    for selected in paths:
        if selected.is_dir():
            candidates = _walk_plain_files(selected, f"critical input {selected}")
        else:
            candidates = [selected]
        for path in candidates:
            info = path.lstat()
            if (
                stat.S_ISLNK(info.st_mode)
                or not stat.S_ISREG(info.st_mode)
                or info.st_nlink != 1
            ):
                raise AttestationError(
                    f"critical input is not a plain single-link file: {path}"
                )
            rows.append(
                f"{path}\t"
                f"{info.st_size}\t{sha256_path(path)}\n"
            )
            file_count += 1
    return hashlib.sha256("".join(rows).encode("utf-8")).hexdigest(), file_count


def _critical_inputs(
    paths: HostPaths,
    campaign: Path,
    replica: Path,
    authority_path: Path,
    receipt: dict[str, Any],
    bootstrap_path: Path,
) -> tuple[Path, ...]:
    source_snapshot = receipt.get("sourceSnapshot")
    advance = receipt.get("advance")
    snapshot = advance.get("snapshot") if isinstance(advance, dict) else None
    prep = advance.get("prepRoot") if isinstance(advance, dict) else None
    if (
        not isinstance(source_snapshot, dict)
        or not isinstance(snapshot, dict)
        or not isinstance(prep, dict)
    ):
        raise AttestationError("Gen32 replay input blocks are malformed")
    snapshot_root = paths.resolve(snapshot.get("path"), "Gen32 replay snapshot")
    source_snapshot_root = paths.resolve(
        source_snapshot.get("path"), "Gen32 source snapshot"
    )
    if snapshot_root != source_snapshot_root:
        raise AttestationError("Gen32 source and advance snapshots bind differently")
    prep_root = paths.resolve(prep.get("path"), "Gen32 replay prep root")
    receipt_files = tuple(
        paths.resolve(raw, "Gen32 sealed receipt source")
        for raw in sorted(_sealed_receipt_sources(receipt))
    )
    return (
        campaign,
        replica,
        paths.lab / GEN31_RELATIVE,
        authority_path,
        paths.lab / GEN31_AUTHORITY_RELATIVE,
        paths.repo / CLOSURE_RELATIVE,
        bootstrap_path,
        snapshot_root,
        prep_root,
        *receipt_files,
    )


def _write_new_attestation(path: Path, value: dict[str, Any], lab_root: Path) -> str:
    allowed_parent = lab_root.parent / "host-attestations"
    if path.parent != allowed_parent:
        raise AttestationError(
            f"attestation output must be directly below {allowed_parent}"
        )
    if path.exists() or path.is_symlink():
        raise AttestationError(f"refusing existing attestation output: {path}")
    if not allowed_parent.exists():
        allowed_parent.mkdir(mode=0o700)
    parent = _plain_root(allowed_parent, "host-attestation directory")
    if parent != allowed_parent.resolve():
        raise AttestationError("host-attestation directory identity differs")
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary = parent / f".{path.name}.tmp-{os.getpid()}"
    descriptor: int | None = None
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        os.unlink(temporary)
        directory_fd = os.open(parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class Config:
    campaign: Path
    repo_root: Path
    lab_root: Path
    authority: Path
    expected_ready_sha256: str
    expected_reducer_id: str
    expected_authority_sha256: str
    mode: str
    attestation_out: Path | None


def attest_generation32(config: Config) -> tuple[dict[str, Any], str | None]:
    if config.mode not in {"integrity", "full"}:
        raise AttestationError(f"unsupported attestation mode: {config.mode!r}")
    if config.mode != "full" and config.attestation_out is not None:
        raise AttestationError("a durable attestation requires a full replay")
    if config.expected_ready_sha256 != GEN32_READY_SHA256:
        raise AttestationError("caller READY pin is not the supported Gen32 identity")
    if config.expected_reducer_id != GEN32_REDUCER_ID:
        raise AttestationError("caller reducer pin is not the supported Gen32 identity")
    if config.expected_authority_sha256 != GEN32_AUTHORITY_SHA256:
        raise AttestationError("caller authority pin is not the supported Gen32 identity")

    paths = HostPaths(config.repo_root, config.lab_root)
    campaign = paths.resolve(config.campaign, "selected canonical Gen32 campaign")
    expected_campaign = paths.lab / GEN32_RELATIVE
    if campaign != expected_campaign:
        raise AttestationError("only the exact canonical Gen32 campaign may be selected")
    authority_path = paths.resolve(config.authority, "selected Gen32 authority")
    if authority_path != paths.lab / GEN32_AUTHORITY_RELATIVE:
        raise AttestationError("only the exact Gen32 authority receipt may be selected")
    ready = _require_plain_file(
        campaign / "campaign.ready.json",
        "canonical Gen32 READY",
        byte_count=GEN32_READY_BYTES,
        digest=GEN32_READY_SHA256,
    )
    del ready

    bootstrap, receipt, entry, bootstrap_path, mapping_digest = _prevalidate(
        paths,
        campaign,
        config.expected_ready_sha256,
        config.expected_reducer_id,
    )
    authority, replica, _replica_receipt = _validate_external_authority(
        paths, bootstrap, campaign, authority_path
    )
    del authority

    critical = _critical_inputs(
        paths,
        campaign,
        replica,
        authority_path,
        receipt,
        bootstrap_path,
    )
    before_digest, critical_file_count = _critical_fingerprint(critical)
    campaign_module, _builder, receipt_sources = _install_host_hooks(
        paths, campaign, receipt, entry
    )
    try:
        verified = campaign_module.verify(
            campaign,
            _replay_generation=config.mode == "full",
        )
    except (campaign_module.CampaignError, AttestationError) as exc:
        raise AttestationError(f"unchanged frozen Gen32 verifier blocked: {exc}") from exc
    if verified.get("counts") != EXPECTED_COUNTS:
        raise AttestationError("verified Gen32 counts differ from the external authority")
    after_digest, after_file_count = _critical_fingerprint(critical)
    if before_digest != after_digest or critical_file_count != after_file_count:
        raise AttestationError("a critical frozen input changed during host replay")

    output_stamps = {
        name: {
            "bytes": (campaign / name).stat().st_size,
            "sha256": sha256_path(campaign / name),
        }
        for name in OUTPUTS
    }
    result = {
        "schema": ATTESTATION_SCHEMA,
        "verdict": "VERIFIED",
        "mode": config.mode,
        "completedAtUtc": datetime.now(timezone.utc).isoformat(),
        "campaign": {
            "logicalWindowsPath": WINDOWS_REPO_PREFIX
            + "local-lab\\"
            + str(GEN32_RELATIVE).replace("/", "\\"),
            "physicalLinuxPath": os.fspath(campaign),
            "readyBytes": GEN32_READY_BYTES,
            "readySha256": GEN32_READY_SHA256,
            "reducerId": GEN32_REDUCER_ID,
            "reducerFiles": 47,
            "counts": EXPECTED_COUNTS,
            "outputs": output_stamps,
        },
        "externalAuthority": {
            "path": os.fspath(authority_path),
            "bytes": GEN32_AUTHORITY_BYTES,
            "sha256": GEN32_AUTHORITY_SHA256,
            "schema": GEN32_AUTHORITY_SCHEMA,
        },
        "hostRoots": {
            "canonicalRepo": os.fspath(paths.repo),
            "recoveredLocalLab": os.fspath(paths.lab),
        },
        "preImportGate": {
            "bootstrapPath": os.fspath(bootstrap_path),
            "bootstrapSha256": BOOTSTRAP_SHA256,
            "validatedReducerIdentities": 31,
            "mappedReceiptPaths": len(paths.bootstrap_records),
            "historicalOracleMappings": 3,
            "allowedMissingLeaves": 1,
            "lostGen4ReadyBytesPin": LOST_GEN4_READY_BYTES,
            "lostGen4ReadySha256Pin": LOST_GEN4_READY_SHA256,
            "mappingSetSha256": mapping_digest,
            "logicalMappingSetSha256": EXPECTED_LOGICAL_MAPPING_SET_SHA256,
            "mappings": [asdict(row) for row in paths.bootstrap_records],
        },
        "hostAdapter": {
            "path": os.fspath(Path(__file__).resolve()),
            "sha256": sha256_path(Path(__file__).resolve()),
            "successMarker": "CAMPAIGN_HOST_REPLAY_VERIFIED",
            "scope": "GENERATION_32_ONLY",
        },
        "replay": {
            "frozenOwnerSha256": GEN32_OWNER_SHA256,
            "frozenBuilderSha256": GEN32_BUILDER_SHA256,
            "carryBridge": "LITERAL_PINNED_SEALED_AUTHORITY_GENERATION31_NO_REPLAY",
            "sealedClosurePath": CLOSURE_RELATIVE,
            "sealedClosureSha256": CLOSURE_SHA256,
            "sealedReceiptSourceFiles": len(receipt_sources),
            "ledgerFilesCompared": 8,
            "canonicalReplicaReducerFilesCompared": 47,
            "criticalInputFilesMeasured": critical_file_count,
            "criticalInputSetSha256Before": before_digest,
            "criticalInputSetSha256After": after_digest,
            "unexpectedSubprocesses": 0,
        },
        "immutability": {
            "receiptBytesRewritten": False,
            "reducerBytesRewritten": False,
            "frozenInputSetChanged": False,
            "replayOutputWasTemporary": config.mode == "full",
        },
    }
    attestation_sha: str | None = None
    if config.attestation_out is not None:
        attestation_sha = _write_new_attestation(
            config.attestation_out,
            result,
            paths.lab,
        )
    return result, attestation_sha


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--lab-root", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--expected-ready-sha256", required=True)
    parser.add_argument("--expected-reducer-id", required=True)
    parser.add_argument("--expected-authority-sha256", required=True)
    parser.add_argument("--mode", choices=("integrity", "full"), default="full")
    parser.add_argument("--attestation-out", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result, output_sha = attest_generation32(Config(**vars(args)))
    except Exception as exc:
        print(f"GEN32_LINUX_HOST_ATTESTATION_BLOCKED: {exc}", file=sys.stderr)
        return 10
    counts = json.dumps(result["campaign"]["counts"], sort_keys=True, separators=(",", ":"))
    marker = (
        "CAMPAIGN_HOST_REPLAY_VERIFIED"
        if args.mode == "full"
        else "CAMPAIGN_HOST_INTEGRITY_VERIFIED"
    )
    print(f"{marker} {counts} {result['campaign']['physicalLinuxPath']}")
    if args.attestation_out is not None:
        print(
            "GEN32_LINUX_HOST_ATTESTATION_WRITTEN "
            f"path={args.attestation_out} sha256={output_sha}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
