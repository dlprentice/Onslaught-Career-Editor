#!/usr/bin/env python3
"""Reconcile Ghidra semantic corrections into affected Markdown records.

The tool inserts one compact, idempotent notice into each routed Markdown
document. Historical wave notes retain their original text as provenance;
current docs point readers to the exact machine-readable correction manifests.
Maintainer state and reference-source files are deliberately excluded.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


NOTICE_START = "<!-- ghidra-full-reaudit-20260713:start -->"
NOTICE_END = "<!-- ghidra-full-reaudit-20260713:end -->"
NOTICE_PATTERN = re.compile(
    re.escape(NOTICE_START) + r".*?" + re.escape(NOTICE_END),
    re.DOTALL,
)

CLOSEOUT_PATH = Path(
    "reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md"
)
CURSOR_CORRECTIONS_PATH = Path(
    "reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json"
)
TARGETED_CORRECTIONS_PATH = Path(
    "reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json"
)
EXCLUDED_PREFIXES = (".codex/state/", "references/")
DISCOVERY_ROOTS = (
    Path("reverse-engineering"),
    Path("release/readiness"),
    Path("roadmap"),
)
DISCOVERY_FILES = (Path("CURRENT_CAPABILITIES.md"),)
MAX_NOTICE_LABELS = 5


@dataclass(frozen=True)
class ReconcileResult:
    changed_count: int
    impacted_count: int
    excluded_count: int
    missing_count: int
    changed_paths: tuple[str, ...]
    excluded_paths: tuple[str, ...]
    missing_paths: tuple[str, ...]


def _normalize_relative(value: str) -> str:
    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _is_excluded(relative: str) -> bool:
    return relative.startswith(EXCLUDED_PREFIXES) or not relative.lower().endswith(".md")


def _resolve_repo_document(repo_root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if (
        not relative
        or relative == "."
        or candidate.is_absolute()
        or candidate.drive
        or candidate.root
        or ".." in candidate.parts
    ):
        raise ValueError(f"docFindings path must be repo-relative: {relative!r}")
    resolved = (repo_root / candidate).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError(
            f"docFindings path must resolve inside the repo: {relative!r}"
        ) from exc
    return resolved


def _record_label(record: dict) -> str:
    address = str(record["address"])
    current_name = record.get("currentName") or record.get("savedName")
    corrected_name = record.get("correctedName")
    corrected_fields = set(record.get("correctedFields") or ())
    if corrected_name and current_name and corrected_name != current_name:
        return f"`{address}` → `{corrected_name}` (was `{current_name}`)"
    if "signature" in corrected_fields:
        return f"`{address}` signature/comment correction"
    if "name" in corrected_fields:
        return f"`{address}` name correction"
    return f"`{address}` comment correction"


def _mirror_path(repo_root: Path, relative: str) -> Path | None:
    if relative.startswith(("reverse-engineering/", "roadmap/")) or relative == "CURRENT_CAPABILITIES.md":
        mirror = _resolve_repo_document(repo_root, f"lore-book/{relative}")
        return mirror if mirror.is_file() else None
    return None


def _relative_link(document: Path, repo_root: Path, target: Path) -> str:
    relative = os.path.relpath(repo_root / target, document.parent)
    return Path(relative).as_posix()


def _closeout_target(document: Path, repo_root: Path) -> Path:
    relative = document.relative_to(repo_root).as_posix()
    if relative.startswith("lore-book/"):
        return Path("lore-book") / CLOSEOUT_PATH
    return CLOSEOUT_PATH


def _render_notice(document: Path, repo_root: Path, records: Iterable[dict], newline: str) -> str:
    ordered = sorted(records, key=lambda item: str(item["address"]))
    labels = (
        "; ".join(_record_label(record) for record in ordered)
        if len(ordered) <= MAX_NOTICE_LABELS
        else f"{len(ordered)} correction records referenced in this document"
    )
    closeout = _relative_link(document, repo_root, _closeout_target(document, repo_root))
    relative = document.relative_to(repo_root).as_posix()
    links = (
        f"[closeout]({closeout}); exact records are in "
        f"`{CURSOR_CORRECTIONS_PATH.as_posix()}` and "
        f"`{TARGETED_CORRECTIONS_PATH.as_posix()}`"
    )
    if relative.startswith("release/readiness/"):
        body = (
            f"> **2026-07-13 semantic revalidation:** Historical record; {labels}. "
            f"The original text below remains provenance rather than current semantic authority. "
            f"Use the {links}."
        )
    else:
        body = (
            f"> **2026-07-13 semantic revalidation:** {labels}. "
            f"Older conflicting text below is superseded for these rows. Use the {links}."
        )
    return newline.join((NOTICE_START, body, NOTICE_END))


def _insert_or_replace_notice(text: str, notice: str, newline: str) -> str:
    existing = NOTICE_PATTERN.search(text)
    if existing:
        before = text[: existing.start()].rstrip("\r\n")
        after = text[existing.end() :].lstrip("\r\n")
        if before and after:
            text = before + newline + newline + after
        elif before:
            text = before + newline
        else:
            text = after
    lines = text.splitlines(keepends=True)
    first_content = next(
        (index for index, line in enumerate(lines) if line.strip()), None
    )
    if first_content is not None and lines[first_content].lstrip("\ufeff").startswith("# "):
        prefix = "".join(lines[: first_content + 1])
        suffix = "".join(lines[first_content + 1 :])
        return prefix + newline + notice + newline + suffix
    return notice + newline + newline + text


def _collect_documents(
    repo_root: Path, records: Iterable[dict]
) -> tuple[dict[Path, list[dict]], set[str], set[str]]:
    routed: dict[Path, list[dict]] = {}
    excluded: set[str] = set()
    missing: set[str] = set()
    for record in records:
        for raw_path in record.get("docFindings") or ():
            relative = _normalize_relative(str(raw_path))
            canonical = _resolve_repo_document(repo_root, relative)
            if _is_excluded(relative):
                excluded.add(relative)
                continue
            if not canonical.is_file():
                missing.add(relative)
                continue
            routed.setdefault(canonical, []).append(record)
            mirror = _mirror_path(repo_root, relative)
            if mirror:
                routed.setdefault(mirror, []).append(record)
    for path, path_records in routed.items():
        by_address = {str(record["address"]): record for record in path_records}
        routed[path] = list(by_address.values())
    return routed, excluded, missing


def _discover_address_documents(
    repo_root: Path, records: Iterable[dict], routed: dict[Path, list[dict]]
) -> None:
    by_address = {str(record["address"]).lower(): record for record in records}
    rename_patterns: list[tuple[dict, re.Pattern[str]]] = []
    for record in records:
        current_name = record.get("currentName")
        corrected_name = record.get("correctedName")
        if (
            isinstance(current_name, str)
            and current_name
            and isinstance(corrected_name, str)
            and corrected_name
            and current_name != corrected_name
        ):
            rename_patterns.append(
                (
                    record,
                    re.compile(
                        rf"(?<![A-Za-z0-9_]){re.escape(current_name)}(?![A-Za-z0-9_])"
                    ),
                )
            )
    excluded_authority = {
        (repo_root / CLOSEOUT_PATH).resolve(),
        (repo_root / "lore-book" / CLOSEOUT_PATH).resolve(),
    }
    discovery_paths: list[Path] = []
    for root_relative in DISCOVERY_ROOTS:
        root = _resolve_repo_document(repo_root, root_relative.as_posix())
        if not root.is_dir():
            continue
        discovery_paths.extend(root.rglob("*.md"))
    for file_relative in DISCOVERY_FILES:
        path = _resolve_repo_document(repo_root, file_relative.as_posix())
        if path.is_file():
            discovery_paths.append(path)
    for path in sorted(set(discovery_paths)):
        path = path.resolve()
        if path in excluded_authority:
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        matches_by_address = {
            str(record["address"]).lower(): record
            for address, record in by_address.items()
            if address in lowered
        }
        for record, pattern in rename_patterns:
            if pattern.search(text):
                matches_by_address[str(record["address"]).lower()] = record
        matches = list(matches_by_address.values())
        if not matches:
            continue
        routed.setdefault(path, []).extend(matches)
        relative = path.relative_to(repo_root).as_posix()
        mirror = _mirror_path(repo_root, relative)
        if mirror:
            routed.setdefault(mirror, []).extend(matches)
    for path, path_records in routed.items():
        by_path_address = {str(record["address"]): record for record in path_records}
        routed[path] = list(by_path_address.values())


def reconcile_docs(repo_root: Path, records: Iterable[dict], *, write: bool) -> ReconcileResult:
    repo_root = repo_root.resolve()
    records = tuple(records)
    routed, excluded, missing = _collect_documents(repo_root, records)
    _discover_address_documents(repo_root, records, routed)
    changed: list[str] = []
    for path in sorted(routed):
        original = path.read_bytes().decode("utf-8")
        newline = "\r\n" if "\r\n" in original else "\n"
        notice = _render_notice(path, repo_root, routed[path], newline)
        updated = _insert_or_replace_notice(original, notice, newline)
        if updated == original:
            continue
        changed.append(path.relative_to(repo_root).as_posix())
        if write:
            path.write_bytes(updated.encode("utf-8"))
    return ReconcileResult(
        changed_count=len(changed),
        impacted_count=len(routed),
        excluded_count=len(excluded),
        missing_count=len(missing),
        changed_paths=tuple(changed),
        excluded_paths=tuple(sorted(excluded)),
        missing_paths=tuple(sorted(missing)),
    )


def load_records(manifests: Iterable[Path]) -> list[dict]:
    by_address: dict[str, dict] = {}
    for manifest in manifests:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        values = payload.get("records")
        if not isinstance(values, list):
            raise ValueError(f"manifest has no records array: {manifest}")
        for value in values:
            if not isinstance(value, dict):
                raise ValueError(f"manifest has non-object correction record: {manifest}")
            address = str(value.get("address", "")).lower()
            if not address:
                raise ValueError(f"manifest correction record has no address: {manifest}")
            current = by_address.get(address)
            if current is None:
                by_address[address] = value
                continue
            if current == value:
                continue
            current_supersedes = current.get("supersedesCursorDeltaRecord") is True
            value_supersedes = value.get("supersedesCursorDeltaRecord") is True
            if current_supersedes == value_supersedes:
                raise ValueError(
                    f"duplicate correction address lacks one unambiguous superseder: {address}"
                )
            winner, loser = (current, value) if current_supersedes else (value, current)
            merged = dict(winner)
            merged["docFindings"] = sorted(
                {
                    *[str(path) for path in loser.get("docFindings") or ()],
                    *[str(path) for path in winner.get("docFindings") or ()],
                }
            )
            by_address[address] = merged
    return [by_address[address] for address in sorted(by_address)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path, action="append", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        records = load_records(args.manifest)
        result = reconcile_docs(args.repo_root, records, write=args.write)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Ghidra doc reconciliation: FAIL: {exc}")
        return 2
    mode = "WRITE" if args.write else "CHECK"
    print(
        f"Ghidra doc reconciliation: {mode} "
        f"Impacted={result.impacted_count} Changed={result.changed_count} "
        f"Excluded={result.excluded_count} Missing={result.missing_count}"
    )
    for path in result.missing_paths:
        print(f"MISSING {path}")
    if result.missing_count:
        return 2
    if not args.write and result.changed_count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
