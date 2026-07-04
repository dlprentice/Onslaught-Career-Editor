#!/usr/bin/env python3
"""Guard selected active coordination/state surfaces against legacy backup roots.

The repo intentionally preserves old Ghidra backup IDs and historical evidence
inside RE notes. Current coordination/state surfaces should instead describe
configured ignored roots and backup classes without embedding exact local roots.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_SCRIPT = "test:ghidra-legacy-backup-root-provenance-guard"
PACKAGE_COMMAND = (
    r"py -3 tools\ghidra_legacy_backup_root_provenance_guard.py --self-test "
    r"&& py -3 tools\ghidra_legacy_backup_root_provenance_guard.py --check"
)

ACTIVE_SURFACES = (
    "goal.md",
    "developer_agent_state.json",
    "documentation_agent_state.json",
    "re_orchestrator_state.json",
    "coordination/AUTOMATION_STORAGE_GHIDRA_POSTURE.md",
    "coordination/README.md",
    "coordination/REPORT_CONTRACT.md",
    "coordination/RESOURCE_LEASES.md",
    "coordination/WORKSTREAM_CONTRACT.md",
    "LOCAL_LAB_OVERLAY.md",
)

HISTORICAL_SURFACE_ROOTS = (
    "reverse-engineering/",
    "lore-book/reverse-engineering/",
    "release/readiness/",
)

SANITIZED_BACKUP_ROOT_TOKEN = "[maintainer-local-ghidra-backup-root]"

FORBIDDEN_ACTIVE_PATTERNS = (
    (re.compile(r"(?i)\b[a-z]:[\\/](?:[^ \t\r\n`\"'<>|]*[\\/])*GhidraBackups[\\/]"), "exact GhidraBackups drive root"),
    (re.compile(r"(?i)(?:^|[\\/\s`\"'(<])GhidraBackups[\\/]"), "drive-less GhidraBackups root"),
    (re.compile(r"(?i)\b[a-z]:[\\/]"), "drive-letter absolute path"),
    (re.compile(r"(?i)\\\\[^\\/\s]+\\[^\\/\s]+"), "UNC/private network path"),
    (re.compile(r"(?i)/(?:home|mnt|var|opt|tmp|users?)/"), "Unix absolute local path"),
)

REQUIRED_ACTIVE_TOKENS = {
    "coordination/AUTOMATION_STORAGE_GHIDRA_POSTURE.md": (
        "configured removable scratch/backup root",
        "Exact drive letters, roots, volume identifiers",
        "Historical backup/archive drive strings in old wave evidence are provenance only",
    ),
    "goal.md": (
        "latest backup class redaction",
        "Storage/Ghidra backup details remain local campaign evidence only",
    ),
}

REQUIRED_HISTORICAL_TOKENS = (
    SANITIZED_BACKUP_ROOT_TOKEN,
    "Verified backup",
)


class LegacyBackupRootGuardError(ValueError):
    """Raised when active surfaces drift back to exact local backup roots."""


def read_text(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise LegacyBackupRootGuardError(f"missing file: {relative}")
    return path.read_text(encoding="utf-8-sig")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LegacyBackupRootGuardError(message)


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def contains_token(text: str, token: str) -> bool:
    return token in text or token in compact(text)


def check_active_surface(relative: str) -> None:
    text = read_text(relative)
    for pattern, label in FORBIDDEN_ACTIVE_PATTERNS:
        match = pattern.search(text)
        if match is not None:
            raise LegacyBackupRootGuardError(
                f"{relative} contains forbidden active-surface {label}: {match.group(0)}"
            )

    if relative.endswith(".json"):
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            raise LegacyBackupRootGuardError(f"{relative} is invalid JSON: {exc}") from exc

    for token in REQUIRED_ACTIVE_TOKENS.get(relative, ()):
        require(contains_token(text, token), f"{relative} missing required posture token: {token}")


def historical_reference_count() -> int:
    count = 0
    for root in HISTORICAL_SURFACE_ROOTS:
        base = ROOT / root
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".jsonl", ".tsv", ".txt"}:
                try:
                    text = path.read_text(encoding="utf-8-sig")
                except UnicodeDecodeError:
                    continue
                if SANITIZED_BACKUP_ROOT_TOKEN in text:
                    count += 1
    return count


def check_historical_provenance_exists() -> None:
    count = historical_reference_count()
    require(count > 0, "expected historical RE provenance references to remain present")

    sampled = read_text("reverse-engineering/RE-INDEX.md")
    for token in REQUIRED_HISTORICAL_TOKENS:
        require(token in sampled, f"reverse-engineering/RE-INDEX.md missing historical token: {token}")


def check_package_script() -> None:
    package = json.loads(read_text("package.json"))
    scripts = package.get("scripts")
    require(isinstance(scripts, dict), "package.json scripts must be an object")
    require(scripts.get(PACKAGE_SCRIPT) == PACKAGE_COMMAND, f"package.json missing {PACKAGE_SCRIPT}")


def run_check() -> None:
    for relative in ACTIVE_SURFACES:
        check_active_surface(relative)
    check_historical_provenance_exists()
    check_package_script()


def run_self_test() -> None:
    clean = "Configured removable scratch/backup root; backup id BEA_20260703-152228Z_live_project_backup_verified."
    for pattern, label in FORBIDDEN_ACTIVE_PATTERNS:
        require(pattern.search(clean) is None, f"self-test clean text matched {label}")

    bad_samples = (
        "G:" + "\\GhidraBackups\\BEA_20260607-110625_post_wave1217_verified",
        "\\GhidraBackups\\BEA_20260607-110625_post_wave1217_verified",
        "GhidraBackups/BEA_20260607-110625_post_wave1217_verified",
        "F:" + "\\cleanup-manifests\\run.json",
        "\\\\server\\share\\BEA_20260607",
        "/home/example/.ghidra/project",
    )
    for sample in bad_samples:
        matched = any(pattern.search(sample) for pattern, _ in FORBIDDEN_ACTIVE_PATTERNS)
        require(matched, f"self-test failed to catch forbidden active root: {sample}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate active backup-root provenance posture")
    parser.add_argument("--self-test", action="store_true", help="run internal negative guard tests")
    args = parser.parse_args()

    if not args.check and not args.self_test:
        parser.error("choose --check and/or --self-test")

    try:
        if args.self_test:
            run_self_test()
        if args.check:
            run_check()
    except LegacyBackupRootGuardError as exc:
        print("Ghidra legacy backup root provenance guard: FAIL")
        print(f"- {exc}")
        return 1

    print("Ghidra legacy backup root provenance guard: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
