#!/usr/bin/env python3
"""Import-safe launcher for an immutable RE campaign reducer.

The campaign owner normally lives inside ``_reducer/tools``.  Executing that
file directly places its directory on ``sys.path`` before the reducer can
validate its own manifest, so an unmanifested sibling such as ``json.py`` could
shadow a standard-library import.  This launcher is run with ``python -I``.  It
validates every reachable on-disk reducer bundle before adding the selected
tools directory to ``sys.path`` or importing campaign code.

This file deliberately uses only the standard library and is itself carried in
new reducer snapshots.  Older frozen owners that launch another campaign owner
through ``subprocess.run`` are wrapped so their child is routed back through the
same pre-import gate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


REDUCER_SCHEMA = "bea.re.campaign-reducer.v1"
REDUCER_ENTRY = "_reducer/tools/re_campaign.py"
REPARSE_ATTRIBUTE = 0x400
BOOTSTRAP_SOURCE = Path(__file__).resolve()
ORIGINAL_SUBPROCESS_RUN = subprocess.run
GEN5_RECOVERY_READY_SHA256 = (
    "5bddceb51c131d9c3a1ac634fd0672d0e9999b7ccab3f65dd2b33b4a68947cde"
)
GEN5_RECOVERY_REDUCER_ID = (
    "384c325149a4244a5eb48fa70d01bff541584d7b3c5b90b69e4658eed96852d6"
)
LOST_GEN4_READY_BYTES = 11729
LOST_GEN4_READY_SHA256 = (
    "5b32978da40d91f557b971da6ae0a23b3971fa1afe922c443d6ae039c7ede8ed"
)
VALIDATED_IDENTITIES: dict[str, tuple[str, str]] = {}


class BootstrapError(RuntimeError):
    """The frozen owner is unsafe to import or differs from its receipt."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BootstrapError(f"{label} is not an object")
    return value


def _plain_stat(path: Path, label: str) -> os.stat_result:
    try:
        result = path.lstat()
    except OSError as exc:
        raise BootstrapError(f"{label} is absent: {exc}") from exc
    if stat.S_ISLNK(result.st_mode) or (
        getattr(result, "st_file_attributes", 0) & REPARSE_ATTRIBUTE
    ):
        raise BootstrapError(f"{label} is a symlink or reparse point")
    return result


def _walk_plain_files(root: Path) -> set[str]:
    """Return every regular file below root and reject link/reparse entries."""

    files: set[str] = set()
    stack = [root]
    while stack:
        directory = stack.pop()
        directory_stat = _plain_stat(directory, f"reducer directory {directory}")
        if not stat.S_ISDIR(directory_stat.st_mode):
            raise BootstrapError(f"reducer path is not a directory: {directory}")
        try:
            entries = list(os.scandir(directory))
        except OSError as exc:
            raise BootstrapError(f"cannot enumerate reducer directory {directory}: {exc}") from exc
        for entry in entries:
            path = Path(entry.path)
            entry_stat = _plain_stat(path, f"reducer entry {path}")
            if stat.S_ISDIR(entry_stat.st_mode):
                stack.append(path)
                continue
            if not stat.S_ISREG(entry_stat.st_mode):
                raise BootstrapError(f"reducer entry is not a regular file: {path}")
            if entry_stat.st_nlink != 1:
                raise BootstrapError(f"reducer file has multiple hard links: {path}")
            files.add(path.relative_to(root.parent).as_posix())
    return files


def _reducer_id(files: list[dict[str, Any]]) -> str:
    canonical = "".join(
        f"{row['role']}\t{row['sha256']}\t{row['bytes']}\t{row['path']}\n"
        for row in sorted(files, key=lambda item: str(item["path"]))
    ).encode("utf-8")
    return _sha256_bytes(canonical)


def _read_ready(root: Path) -> tuple[Path, dict[str, Any]]:
    ready_path = root / "campaign.ready.json"
    ready_stat = _plain_stat(ready_path, f"campaign READY {ready_path}")
    if not stat.S_ISREG(ready_stat.st_mode) or ready_stat.st_nlink != 1:
        raise BootstrapError(f"campaign READY is not a plain single-link file: {ready_path}")
    try:
        receipt = json.loads(ready_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BootstrapError(f"cannot read campaign READY {ready_path}: {exc}") from exc
    return ready_path, _mapping(receipt, f"campaign READY {ready_path}")


def _validate_reducer(
    root: Path,
    *,
    expected_ready_sha256: str | None = None,
    expected_reducer_id: str | None = None,
) -> tuple[dict[str, Any], Path]:
    root = Path(os.path.abspath(root))
    root_stat = _plain_stat(root, f"campaign root {root}")
    if not stat.S_ISDIR(root_stat.st_mode):
        raise BootstrapError(f"campaign root is not a directory: {root}")
    ready_path, receipt = _read_ready(root)
    if expected_ready_sha256 and _sha256_path(ready_path) != expected_ready_sha256:
        raise BootstrapError("campaign READY differs from the externally pinned identity")

    manifest = _mapping(receipt.get("reducer"), "campaign reducer manifest")
    if set(manifest) != {"schema", "id", "entry", "files"}:
        raise BootstrapError("campaign reducer manifest shape differs")
    rows = manifest.get("files")
    if (
        manifest.get("schema") != REDUCER_SCHEMA
        or manifest.get("entry") != REDUCER_ENTRY
        or not isinstance(rows, list)
        or not rows
    ):
        raise BootstrapError("campaign reducer manifest is unsupported")

    seen_roles: set[str] = set()
    seen_paths: set[str] = set()
    actual_rows: list[dict[str, Any]] = []
    for raw_row in rows:
        row = _mapping(raw_row, "campaign reducer file stamp")
        if set(row) != {"role", "path", "bytes", "sha256"}:
            raise BootstrapError("campaign reducer file stamp shape differs")
        role = row.get("role")
        relative = row.get("path")
        byte_count = row.get("bytes")
        digest = row.get("sha256")
        relative_path = Path(str(relative))
        if (
            not isinstance(role, str)
            or not role
            or role in seen_roles
            or not isinstance(relative, str)
            or relative in seen_paths
            or not relative.startswith("_reducer/")
            or "\\" in relative
            or relative_path.is_absolute()
            or ".." in relative_path.parts
            or not isinstance(byte_count, int)
            or byte_count < 0
            or not isinstance(digest, str)
            or len(digest) != 64
        ):
            raise BootstrapError("campaign reducer contains a duplicate or escaping file")
        seen_roles.add(role)
        seen_paths.add(relative)
        path = root / relative_path
        path_stat = _plain_stat(path, f"campaign reducer file {relative}")
        if not stat.S_ISREG(path_stat.st_mode) or path_stat.st_nlink != 1:
            raise BootstrapError(f"campaign reducer file is not plain/single-link: {relative}")
        actual_row = {
            "role": role,
            "path": relative,
            "bytes": path_stat.st_size,
            "sha256": _sha256_path(path),
        }
        if actual_row != row:
            raise BootstrapError(f"campaign reducer file has changed: {relative}")
        actual_rows.append(actual_row)

    actual_paths = _walk_plain_files(root / "_reducer")
    if actual_paths != seen_paths:
        missing = sorted(seen_paths - actual_paths)
        extra = sorted(actual_paths - seen_paths)
        raise BootstrapError(
            f"campaign reducer file set differs: missing={missing} extra={extra}"
        )
    actual_id = _reducer_id(actual_rows)
    if actual_id != manifest.get("id"):
        raise BootstrapError("campaign reducer bundle digest is inconsistent")
    if expected_reducer_id and actual_id != expected_reducer_id:
        raise BootstrapError("campaign reducer differs from the externally pinned identity")
    entry = root / REDUCER_ENTRY
    return receipt, entry


def _repo_or_absolute(raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return Path(os.path.abspath(candidate))
    repo = os.environ.get("BEA_REPO_ROOT")
    if not repo:
        raise BootstrapError("BEA_REPO_ROOT is required for a relative campaign parent")
    return Path(os.path.abspath(Path(repo) / candidate))


def _validate_receipt_bound_historical_oracle(receipt: dict[str, Any]) -> None:
    """Prevalidate an exact integrity-only oracle named by a recovery receipt.

    The first recovery reducer predates this bootstrap and launches its frozen
    historical projection oracle through a short ``python -c`` loader.  That
    oracle is not a parent, so it is absent from the ordinary parent-chain
    walk.  Admit only the exact READY path/bytes/hash already committed by the
    externally selected recovery receipt, and validate the oracle's complete
    reducer bundle before the legacy loader can be replaced.
    """

    advance = receipt.get("advance")
    if not isinstance(advance, dict):
        return
    projection = advance.get("historicalProjection")
    if not isinstance(projection, dict):
        return
    if projection.get("historicalAuthorityClass") != "HISTORICAL_FROZEN_INTEGRITY_ONLY":
        return
    ready_stamp = _mapping(
        projection.get("historicalReady"),
        "campaign historical projection READY",
    )
    if set(ready_stamp) != {"path", "bytes", "sha256", "lastWriteUtc"}:
        raise BootstrapError("campaign historical projection READY shape differs")
    raw_path = ready_stamp.get("path")
    expected_bytes = ready_stamp.get("bytes")
    expected_sha256 = ready_stamp.get("sha256")
    if (
        not isinstance(raw_path, str)
        or not raw_path
        or not isinstance(expected_bytes, int)
        or expected_bytes < 0
        or not isinstance(expected_sha256, str)
        or len(expected_sha256) != 64
    ):
        raise BootstrapError("campaign historical projection READY identity differs")
    ready_path = _repo_or_absolute(raw_path)
    if ready_path.name != "campaign.ready.json":
        raise BootstrapError("campaign historical projection READY path differs")
    ready_stat = _plain_stat(
        ready_path, "campaign historical projection READY"
    )
    if (
        not stat.S_ISREG(ready_stat.st_mode)
        or ready_stat.st_nlink != 1
        or ready_stat.st_size != expected_bytes
        or _sha256_path(ready_path) != expected_sha256
    ):
        raise BootstrapError("campaign historical projection READY has changed")
    oracle_root = ready_path.parent
    oracle_receipt, _entry = _validate_reducer(
        oracle_root,
        expected_ready_sha256=expected_sha256,
    )
    oracle_identity = os.path.normcase(os.fspath(oracle_root))
    VALIDATED_IDENTITIES[oracle_identity] = (
        expected_sha256,
        str(oracle_receipt["reducer"]["id"]),
    )


def _validate_reachable_chain(
    root: Path,
    *,
    expected_ready_sha256: str | None,
    expected_reducer_id: str | None,
) -> tuple[dict[str, Any], Path]:
    """Validate every reducer on the existing parent chain before first import."""

    current = Path(os.path.abspath(root))
    visited: set[str] = set()
    first: tuple[dict[str, Any], Path] | None = None
    while True:
        identity = os.path.normcase(os.fspath(current))
        if identity in visited:
            raise BootstrapError("campaign parent chain contains a cycle")
        visited.add(identity)
        validated = _validate_reducer(
            current,
            expected_ready_sha256=expected_ready_sha256 if first is None else None,
            expected_reducer_id=expected_reducer_id if first is None else None,
        )
        current_ready_sha256 = _sha256_path(current / "campaign.ready.json")
        current_reducer_id = str(validated[0]["reducer"]["id"])
        VALIDATED_IDENTITIES[identity] = (
            current_ready_sha256,
            current_reducer_id,
        )
        _validate_receipt_bound_historical_oracle(validated[0])
        if first is None:
            first = validated
        receipt = validated[0]
        parent = receipt.get("parentCampaign")
        if parent is None:
            break
        parent_map = _mapping(parent, "campaign parentCampaign")
        raw_path = parent_map.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            raise BootstrapError("campaign parent path is missing")
        parent_root = _repo_or_absolute(raw_path)
        parent_ready = parent_root / "campaign.ready.json"
        if not parent_ready.is_file():
            expected_parent = _mapping(
                parent_map.get("ready"), "campaign parent READY stamp"
            )
            exact_gen5_bridge = bool(
                receipt.get("generation") == 5
                and current_ready_sha256 == GEN5_RECOVERY_READY_SHA256
                and current_reducer_id == GEN5_RECOVERY_REDUCER_ID
                and expected_parent.get("bytes") == LOST_GEN4_READY_BYTES
                and expected_parent.get("sha256") == LOST_GEN4_READY_SHA256
            )
            if not exact_gen5_bridge:
                raise BootstrapError(
                    "campaign parent is missing outside the exact Generation-5 recovery bridge"
                )
            break
        expected_parent = _mapping(parent_map.get("ready"), "campaign parent READY stamp")
        if (
            expected_parent.get("bytes") != parent_ready.stat().st_size
            or expected_parent.get("sha256") != _sha256_path(parent_ready)
        ):
            raise BootstrapError("campaign parent READY differs before frozen import")
        current = parent_root
    if first is None:  # pragma: no cover - defensive only
        raise BootstrapError("campaign chain validation produced no root")
    return first


def _nested_campaign_invocation(argv: object) -> tuple[str, str] | None:
    if not isinstance(argv, (list, tuple)):
        return None
    values = [os.fspath(value) for value in argv]
    for index, value in enumerate(values):
        normalized = value.replace("\\", "/").lower()
        if not normalized.endswith("/_reducer/tools/re_campaign.py"):
            continue
        if "--campaign" in values:
            campaign_index = values.index("--campaign") + 1
            if campaign_index < len(values):
                return values[campaign_index], "full"
        if index + 1 < len(values):
            # Historical integrity wrappers pass ENTRY and CAMPAIGN as the last
            # two arguments to a short ``python -c`` loader.
            return values[index + 1], "integrity"
    return None


def _guarded_subprocess_run(argv: object, *args: object, **kwargs: object):
    nested = _nested_campaign_invocation(argv)
    if nested is None:
        return ORIGINAL_SUBPROCESS_RUN(argv, *args, **kwargs)
    campaign_root, mode = nested
    identity = VALIDATED_IDENTITIES.get(
        os.path.normcase(os.fspath(Path(os.path.abspath(campaign_root))))
    )
    if identity is None:
        raise BootstrapError(
            "nested frozen campaign invocation was not prevalidated by the root chain"
        )
    replacement = [
        sys.executable,
        "-I",
        "-B",
        os.fspath(BOOTSTRAP_SOURCE),
        "--campaign",
        campaign_root,
        "--mode",
        mode,
        "--expected-ready-sha256",
        identity[0],
        "--expected-reducer-id",
        identity[1],
    ]
    return ORIGINAL_SUBPROCESS_RUN(replacement, *args, **kwargs)


def _load_and_verify(root: Path, entry: Path, mode: str) -> None:
    sys.path.insert(0, os.fspath(entry.parent))
    spec = importlib.util.spec_from_file_location("_bea_frozen_campaign_owner", entry)
    if spec is None or spec.loader is None:
        raise BootstrapError("cannot create frozen campaign module specification")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.subprocess.run = _guarded_subprocess_run
    replay = mode == "full"
    receipt = module.verify(root, _replay_generation=replay)
    if replay:
        print(f"CAMPAIGN_VERIFIED {receipt['counts']} {root}")
    else:
        print(
            "FROZEN_CAMPAIGN_INTEGRITY_VERIFIED "
            f"{receipt.get('schema')} {receipt.get('generation')}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--mode", choices=("full", "integrity"), default="full")
    parser.add_argument("--expected-ready-sha256")
    parser.add_argument("--expected-reducer-id")
    args = parser.parse_args(argv)
    try:
        if not args.expected_ready_sha256 or not args.expected_reducer_id:
            raise BootstrapError(
                "external READY and reducer pins are required before frozen import"
            )
        root = Path(os.path.abspath(args.campaign))
        _receipt, entry = _validate_reachable_chain(
            root,
            expected_ready_sha256=args.expected_ready_sha256,
            expected_reducer_id=args.expected_reducer_id,
        )
        _load_and_verify(root, entry, args.mode)
    except (BootstrapError, OSError, ValueError) as exc:
        print(f"FROZEN_BOOTSTRAP_BLOCKED: {exc}", file=sys.stderr)
        return 10
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
