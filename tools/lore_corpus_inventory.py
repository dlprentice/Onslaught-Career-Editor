#!/usr/bin/env python3
"""Build a deterministic, source-safe Lore corpus editorial inventory."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import re
import stat
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence
from urllib.parse import urlsplit


STATUS_RE = re.compile(r"^Status:\s*([^\r\n]{1,80})\s*$", re.IGNORECASE)
LAST_UPDATED_RE = re.compile(r"^Last updated:\s*(\d{4}-\d{2}-\d{2})\s*$", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)
GIT_DATE_PREFIX = "@@DATE:"
DNS_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)
NON_PUBLIC_DOMAIN_SUFFIXES = (
    ".corp",
    ".home",
    ".internal",
    ".invalid",
    ".lan",
    ".local",
    ".localhost",
    ".test",
)
REGULAR_GIT_MODES = {"100644", "100755"}
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_git_log_dates(raw_log: str) -> dict[str, str]:
    dates: dict[str, str] = {}
    current_date: str | None = None
    for raw_line in raw_log.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(GIT_DATE_PREFIX):
            current_date = line[len(GIT_DATE_PREFIX) :]
            continue
        if current_date is None:
            continue
        try:
            path = normalize_repo_path(line)
        except ValueError:
            continue
        dates.setdefault(path, current_date)
    return dict(sorted(dates.items()))


def run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git command failed")
    return completed.stdout


def git_tracked_modes(root: Path, pathspec: str | None = None) -> dict[str, str]:
    args = ["ls-files", "--stage", "-z", "--"]
    if pathspec is not None:
        args.append(pathspec)
    raw_entries = run_git(root, *args)
    modes: dict[str, str] = {}
    for record in raw_entries.split("\0"):
        if not record:
            continue
        metadata, separator, raw_path = record.partition("\t")
        fields = metadata.split()
        if not separator or len(fields) != 3:
            raise ValueError("unexpected git ls-files --stage output")
        relative_path = normalize_repo_path(raw_path)
        modes[relative_path] = fields[0]
    return modes


def load_policy(policy_path: Path) -> dict[str, object]:
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict) or policy.get("schema") != "lore-corpus-taxonomy.v1":
        raise ValueError("Lore corpus taxonomy schema mismatch")
    allowed_labels = policy.get("allowedSourceRiskLabels")
    signals = policy.get("sourceRiskSignals")
    if not isinstance(allowed_labels, list) or not all(
        isinstance(label, str) and re.fullmatch(r"[a-z][a-z0-9-]*", label)
        for label in allowed_labels
    ):
        raise ValueError("Lore corpus taxonomy allowedSourceRiskLabels is invalid")
    if not isinstance(signals, list):
        raise ValueError("Lore corpus taxonomy sourceRiskSignals is invalid")
    allowed = set(allowed_labels)
    for item in signals:
        if not isinstance(item, dict) or item.get("label") not in allowed:
            raise ValueError("Lore corpus taxonomy source-risk label is not allowlisted")
    return policy


def collect_tracked_documents(
    root: Path,
    policy: Mapping[str, object],
    tracked_modes: Mapping[str, str] | None = None,
) -> list[str]:
    source_root = policy.get("sourceRoot")
    extensions = policy.get("packableExtensions")
    if not isinstance(source_root, str) or not isinstance(extensions, list):
        raise ValueError("Lore corpus taxonomy sourceRoot or packableExtensions is invalid")
    normalized_root = normalize_repo_path(source_root).rstrip("/")
    allowed_extensions = {
        item.lower() for item in extensions if isinstance(item, str) and item.startswith(".")
    }
    if tracked_modes is None:
        tracked_modes = git_tracked_modes(root, f"{normalized_root}/")
    documents: list[str] = []
    for raw_path, mode in tracked_modes.items():
        if not raw_path.startswith(f"{normalized_root}/"):
            continue
        relative_path = normalize_repo_path(raw_path)
        if PurePosixPath(relative_path).suffix.lower() not in allowed_extensions:
            continue
        if mode not in REGULAR_GIT_MODES:
            raise ValueError(f"non-regular tracked Lore source rejected: {relative_path}")
        documents.append(relative_path)
    reject_casefold_collisions(documents)
    for relative_path in documents:
        if not path_for(root, relative_path).is_file():
            raise FileNotFoundError(f"tracked Lore source is missing: {relative_path}")
    return sorted(documents, key=str.casefold)


def collect_last_commit_dates(root: Path, source_root: str) -> dict[str, str]:
    normalized_root = normalize_repo_path(source_root).rstrip("/")
    raw_log = run_git(
        root,
        "log",
        "--format=@@DATE:%cs",
        "--name-only",
        "--diff-filter=AM",
        "--",
        f"{normalized_root}/",
    )
    return parse_git_log_dates(raw_log)


def build_repository_inventory(root: Path, policy_path: Path) -> dict[str, object]:
    policy = load_policy(policy_path)
    tracked_modes = git_tracked_modes(root)
    tracked_paths = collect_tracked_documents(root, policy, tracked_modes)
    source_root = policy.get("sourceRoot")
    if not isinstance(source_root, str):
        raise ValueError("Lore corpus taxonomy sourceRoot is invalid")
    last_commit_dates = collect_last_commit_dates(root, source_root)
    return build_inventory(
        root,
        policy,
        tracked_paths,
        last_commit_dates,
        tracked_modes=tracked_modes,
    )


def normalize_repo_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        raise ValueError("inventory path must be a non-empty repository-relative POSIX path")
    parts = PurePosixPath(value).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("inventory path contains an unsafe segment")
    return PurePosixPath(*parts).as_posix()


def reject_casefold_collisions(relative_paths: Sequence[str]) -> None:
    seen: dict[str, str] = {}
    for raw_path in relative_paths:
        relative_path = normalize_repo_path(raw_path)
        folded = relative_path.casefold()
        previous = seen.get(folded)
        if previous is not None and previous != relative_path:
            raise ValueError(
                f"inventory path case-fold collision: {previous} and {relative_path}"
            )
        seen[folded] = relative_path


def path_for(root: Path, relative_path: str) -> Path:
    normalized = normalize_repo_path(relative_path)
    root_resolved = root.resolve()
    candidate = root_resolved / Path(*PurePosixPath(normalized).parts)
    current = root_resolved
    for part in PurePosixPath(normalized).parts:
        current = current / part
        if not current.exists() and not current.is_symlink():
            continue
        metadata = os.lstat(current)
        file_attributes = getattr(metadata, "st_file_attributes", 0)
        if stat.S_ISLNK(metadata.st_mode) or file_attributes & FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError("inventory path uses a symlink or reparse point")
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError("inventory path escapes the repository root") from exc
    return candidate


def prefix_matches(relative_path: str, prefix: str) -> bool:
    return relative_path.startswith(prefix) if prefix.endswith("/") else relative_path == prefix


def longest_matching_rules(
    relative_path: str,
    raw_rules: object,
    prefix_key: str,
) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    if not isinstance(raw_rules, list):
        return matches
    for item in raw_rules:
        if not isinstance(item, dict):
            continue
        prefix = item.get(prefix_key)
        if isinstance(prefix, str) and prefix_matches(relative_path, prefix):
            matches.append(item)
    return sorted(matches, key=lambda item: len(str(item[prefix_key])), reverse=True)


def classify_family(relative_path: str, policy: Mapping[str, object]) -> tuple[str, str]:
    for item in longest_matching_rules(relative_path, policy.get("families", []), "prefix"):
        family = item.get("id")
        role = item.get("editorialRole")
        if isinstance(family, str) and isinstance(role, str):
            return family, role
    return "unclassified", "requires taxonomy review"


def canonical_path_for(relative_path: str, policy: Mapping[str, object]) -> str | None:
    for item in longest_matching_rules(
        relative_path,
        policy.get("canonicalMappings", []),
        "projectionPrefix",
    ):
        projection_prefix = item.get("projectionPrefix")
        canonical_prefix = item.get("canonicalPrefix")
        if (
            isinstance(projection_prefix, str)
            and isinstance(canonical_prefix, str)
        ):
            suffix = relative_path[len(projection_prefix) :]
            return normalize_repo_path(f"{canonical_prefix}{suffix}")
    return None


def header_markers(content: str) -> tuple[bool, str | None]:
    status_present = False
    last_updated: str | None = None
    for line in content.splitlines()[:20]:
        status_match = STATUS_RE.match(line.strip())
        if status_match:
            status_present = True
        updated_match = LAST_UPDATED_RE.match(line.strip())
        if updated_match:
            last_updated = updated_match.group(1)
    return status_present, last_updated


def quotation_metrics(content: str) -> dict[str, int]:
    block_quote_lines = 0
    current_run = 0
    max_run = 0
    for line in content.splitlines():
        if re.match(r"^\s*>\s*[^>*`]", line):
            block_quote_lines += 1
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 0
    return {
        "blockQuoteLines": block_quote_lines,
        "maxConsecutiveBlockQuoteLines": max_run,
    }


def source_risk_labels(content: str, policy: Mapping[str, object]) -> tuple[list[str], dict[str, int]]:
    labels: list[str] = []
    counts: dict[str, int] = {}
    for item in policy.get("sourceRiskSignals", []):
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        pattern = item.get("pattern")
        if not isinstance(label, str) or not isinstance(pattern, str):
            continue
        count = len(re.findall(pattern, content, flags=re.IGNORECASE))
        if count:
            labels.append(label)
            counts[label] = count
    return sorted(labels), dict(sorted(counts.items()))


def is_public_domain(hostname: str) -> bool:
    host = hostname.rstrip(".").lower()
    if (
        not host
        or host == "localhost"
        or host.endswith(NON_PUBLIC_DOMAIN_SUFFIXES)
    ):
        return False
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        if "." not in host:
            return False
        if len(host) > 253:
            return False
        return all(DNS_LABEL_RE.fullmatch(label) for label in host.split("."))
    return address.is_global


def external_domains(content: str) -> list[str]:
    domains: set[str] = set()
    for raw_url in URL_RE.findall(content):
        try:
            hostname = urlsplit(raw_url.rstrip(".,;:'\"")).hostname
        except ValueError:
            continue
        if hostname and is_public_domain(hostname):
            domains.add(hostname.lower())
    return sorted(domains)


def build_inventory(
    root: Path,
    policy: Mapping[str, object],
    tracked_paths: Sequence[str],
    last_commit_dates: Mapping[str, str],
    *,
    tracked_modes: Mapping[str, str] | None = None,
) -> dict[str, object]:
    documents: list[dict[str, object]] = []
    family_counts: Counter[str] = Counter()
    divergent_count = 0

    reject_casefold_collisions(tracked_paths)

    for raw_relative_path in sorted(tracked_paths, key=str.casefold):
        relative_path = normalize_repo_path(raw_relative_path)
        if tracked_modes is not None and tracked_modes.get(relative_path) not in REGULAR_GIT_MODES:
            raise ValueError(f"non-regular tracked Lore source rejected: {relative_path}")
        source_path = path_for(root, relative_path)
        source_bytes = source_path.read_bytes()
        content = source_bytes.decode("utf-8", errors="replace")
        family, editorial_role = classify_family(relative_path, policy)
        family_counts[family] += 1
        canonical_path = canonical_path_for(relative_path, policy)
        canonical_hash: str | None = None
        if canonical_path is None:
            projection_state = "not-projected"
        else:
            canonical_file = path_for(root, canonical_path)
            if not canonical_file.is_file():
                projection_state = "canonical-missing"
            else:
                if (
                    tracked_modes is not None
                    and tracked_modes.get(canonical_path) not in REGULAR_GIT_MODES
                ):
                    raise ValueError(
                        f"non-regular tracked canonical source rejected: {canonical_path}"
                    )
                canonical_hash = sha256_bytes(canonical_file.read_bytes())
                projection_state = "equal" if canonical_hash == sha256_bytes(source_bytes) else "different"
                if projection_state == "different":
                    divergent_count += 1

        status_present, last_updated = header_markers(content)
        labels, label_counts = source_risk_labels(content, policy)
        documents.append(
            {
                "path": relative_path,
                "extension": source_path.suffix.lower(),
                "family": family,
                "editorialRole": editorial_role,
                "canonicalPath": canonical_path,
                "projectionState": projection_state,
                "sourceSha256": sha256_bytes(source_bytes),
                "canonicalSha256": canonical_hash,
                "statusMarkerPresent": status_present,
                "lastUpdatedMarker": last_updated,
                "lastCommitDate": last_commit_dates.get(relative_path),
                "triageSignals": {
                    "quotation": quotation_metrics(content),
                    "sourceRiskLabels": labels,
                    "sourceRiskMatchCounts": label_counts,
                    "externalDomains": external_domains(content),
                },
            }
        )

    return {
        "schema": policy.get("inventorySchema", "lore-corpus-inventory.v1"),
        "taxonomySchema": policy.get("schema"),
        "triageBoundary": policy.get("triageBoundary"),
        "documentCount": len(documents),
        "countsByFamily": dict(sorted(family_counts.items())),
        "divergentProjectionCount": divergent_count,
        "documents": documents,
    }


def render_inventory(inventory: Mapping[str, object]) -> str:
    return json.dumps(inventory, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def check_inventory(inventory: Mapping[str, object], output_path: Path) -> None:
    expected = render_inventory(inventory).encode("utf-8")
    if not output_path.is_file() or output_path.read_bytes() != expected:
        raise ValueError("generated inventory is stale; run the Lore corpus inventory build")


def write_inventory(inventory: Mapping[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_name(f"{output_path.name}.tmp")
    temporary_path.write_text(render_inventory(inventory), encoding="utf-8", newline="\n")
    temporary_path.replace(output_path)


def main(argv: Sequence[str] | None = None) -> int:
    default_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Build or check the deterministic Lore corpus editorial inventory."
    )
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--output", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    policy_path = (
        args.policy.resolve()
        if args.policy is not None
        else root / "lore" / "corpus-taxonomy.v1.json"
    )
    output_path = (
        args.output.resolve()
        if args.output is not None
        else root / "lore" / "generated" / "corpus-inventory.v1.json"
    )
    inventory = build_repository_inventory(root, policy_path)
    if args.build:
        write_inventory(inventory, output_path)
        action = "built"
    else:
        try:
            check_inventory(inventory, output_path)
        except ValueError as exc:
            print(f"Lore corpus inventory check: FAIL ({exc})", file=sys.stderr)
            return 1
        action = "checked"
    print(
        "Lore corpus inventory "
        f"{action}: {inventory['documentCount']} document(s), "
        f"{inventory['divergentProjectionCount']} divergent projection(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
