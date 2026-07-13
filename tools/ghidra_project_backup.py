#!/usr/bin/env python3
"""Create and verify recursive, content-addressed Ghidra project backups.

Detailed receipts belong in ignored local evidence.  Console summaries omit
absolute paths so they can be copied into public-safe closeout notes.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable


SCHEMA_VERSION = "onslaught-ghidra-project-backup.v1"
OPEN_SENTINEL_PREFIX = "GHIDRA_PROJECT_OPEN_PROBE_OK program="
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
DEFAULT_OPEN_TIMEOUT_SECONDS = 300


class BackupError(ValueError):
    """Raised when a backup or verification gate fails closed."""


@dataclasses.dataclass(frozen=True)
class FileRecord:
    relative_path: str
    size: int
    sha256: str

    def to_json(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class ProjectManifest:
    root: Path
    project_name: str
    files: tuple[FileRecord, ...]
    structurally_complete: bool

    @property
    def total_bytes(self) -> int:
        return sum(row.size for row in self.files)

    def to_json(self, *, include_root: bool = True) -> dict[str, object]:
        payload: dict[str, object] = {
            "projectName": self.project_name,
            "fileCount": len(self.files),
            "totalBytes": self.total_bytes,
            "structurallyComplete": self.structurally_complete,
            "files": [row.to_json() for row in self.files],
        }
        if include_root:
            payload["root"] = str(self.root)
        return payload


@dataclasses.dataclass(frozen=True)
class ManifestComparison:
    missing: tuple[str, ...]
    extra: tuple[str, ...]
    size_differences: tuple[str, ...]
    hash_differences: tuple[str, ...]

    @property
    def matches(self) -> bool:
        return not (self.missing or self.extra or self.size_differences or self.hash_differences)

    def to_json(self) -> dict[str, object]:
        return {
            "matches": self.matches,
            "missing": list(self.missing),
            "extra": list(self.extra),
            "sizeDifferences": list(self.size_differences),
            "hashDifferences": list(self.hash_differences),
            "missingCount": len(self.missing),
            "extraCount": len(self.extra),
            "sizeDiffCount": len(self.size_differences),
            "hashDiffCount": len(self.hash_differences),
        }


@dataclasses.dataclass(frozen=True)
class CopyResult:
    source_manifest: ProjectManifest
    destination_manifest: ProjectManifest
    source_stable: bool
    copy_comparison: ManifestComparison
    manifest_path: Path


@dataclasses.dataclass(frozen=True)
class OpenResult:
    opened: bool
    content_stable: bool
    exit_code: int
    expected_program_md5: str | None
    command: tuple[str, ...]
    comparison: ManifestComparison

    def to_json(self) -> dict[str, object]:
        return {
            "opened": self.opened,
            "contentStable": self.content_stable,
            "exitCode": self.exit_code,
            "expectedProgramMd5": self.expected_program_md5,
            "commandShape": [Path(self.command[0]).name, *self.command[1:3], "-process", "<PROGRAM>", "-readOnly", "-noanalysis", "-postScript", "GhidraProjectOpenProbe.java"],
            "postOpenComparison": self.comparison.to_json(),
        }


@dataclasses.dataclass(frozen=True)
class VerificationResult:
    source_manifest: ProjectManifest
    copy_result: CopyResult
    open_result: OpenResult
    source_stable: bool
    probe_copy: Path


Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_reparse(path: Path) -> bool:
    info = path.lstat()
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(attributes & reparse_flag)


def require_plain_path(path: Path, label: str) -> None:
    if is_reparse(path):
        raise BackupError(f"{label} must not be a symlink or reparse point")


def resolve_plain_path(path: Path, label: str, *, strict: bool) -> Path:
    lexical = Path(os.path.abspath(path))
    for component in reversed((lexical, *lexical.parents)):
        if os.path.lexists(component):
            require_plain_path(component, label)
    return lexical.resolve(strict=strict)


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def require_disjoint_paths(first: Path, second: Path, labels: str) -> None:
    if _is_within(first, second) or _is_within(second, first):
        raise BackupError(f"{labels} must be disjoint")


def validate_external_output_path(
    path: Path, forbidden_roots: Iterable[Path], label: str
) -> Path:
    target = resolve_plain_path(path, label, strict=False)
    for forbidden in forbidden_roots:
        root = resolve_plain_path(forbidden, "forbidden project/scratch root", strict=True)
        if _is_within(target, root):
            raise BackupError(f"{label} must be disjoint from project and scratch roots")
    return target


def iter_project_paths(root: Path, project_name: str) -> Iterable[Path]:
    gpr = root / f"{project_name}.gpr"
    rep = root / f"{project_name}.rep"
    if not gpr.is_file():
        raise BackupError(f"missing project marker: {project_name}.gpr")
    if not rep.is_dir():
        raise BackupError(f"missing recursive project store: {project_name}.rep")
    require_plain_path(root, "project root")
    require_plain_path(gpr, "project marker")
    require_plain_path(rep, "project store")
    yield gpr
    for path in sorted(rep.rglob("*"), key=lambda item: item.as_posix().lower()):
        require_plain_path(path, "project store entry")
        if path.is_file():
            yield path


def build_manifest(root: Path, project_name: str) -> ProjectManifest:
    root = resolve_plain_path(root, "project root", strict=True)
    files = tuple(
        FileRecord(
            relative_path=path.relative_to(root).as_posix(),
            size=path.stat().st_size,
            sha256=sha256_file(path),
        )
        for path in iter_project_paths(root, project_name)
    )
    idata_prefix = f"{project_name}.rep/idata/"
    has_index = any(
        row.relative_path == f"{project_name}.rep/idata/~index.dat" and row.size > 0
        for row in files
    )
    has_database_payload = any(
        row.relative_path.startswith(idata_prefix)
        and ".db/" in row.relative_path
        and row.size > 0
        for row in files
    )
    if not (has_index and has_database_payload):
        raise BackupError(f"{project_name}.rep has no meaningful recursive project data")
    return ProjectManifest(root=root, project_name=project_name, files=files, structurally_complete=True)


def compare_manifests(expected: ProjectManifest, actual: ProjectManifest) -> ManifestComparison:
    expected_rows = {row.relative_path: row for row in expected.files}
    actual_rows = {row.relative_path: row for row in actual.files}
    missing = tuple(sorted(set(expected_rows) - set(actual_rows)))
    extra = tuple(sorted(set(actual_rows) - set(expected_rows)))
    shared = sorted(set(expected_rows) & set(actual_rows))
    size_differences = tuple(
        path for path in shared if expected_rows[path].size != actual_rows[path].size
    )
    hash_differences = tuple(
        path
        for path in shared
        if expected_rows[path].size == actual_rows[path].size
        and expected_rows[path].sha256 != actual_rows[path].sha256
    )
    return ManifestComparison(missing, extra, size_differences, hash_differences)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def copy_project_pair(source_root: Path, destination_root: Path, project_name: str) -> CopyResult:
    source_root = resolve_plain_path(source_root, "source project root", strict=True)
    destination_root = resolve_plain_path(
        destination_root, "destination project root", strict=False
    )
    require_disjoint_paths(source_root, destination_root, "source and destination roots")
    if destination_root.exists():
        raise BackupError("destination already exists")
    destination_root.parent.mkdir(parents=True, exist_ok=True)
    resolve_plain_path(destination_root.parent, "destination parent", strict=True)

    source_before = build_manifest(source_root, project_name)
    staging = destination_root.parent / f".{destination_root.name}.partial-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        shutil.copy2(source_root / f"{project_name}.gpr", staging / f"{project_name}.gpr")
        shutil.copytree(source_root / f"{project_name}.rep", staging / f"{project_name}.rep", copy_function=shutil.copy2)
        source_after = build_manifest(source_root, project_name)
        source_comparison = compare_manifests(source_before, source_after)
        if not source_comparison.matches:
            raise BackupError("source content changed during recursive copy")
        destination_manifest = build_manifest(staging, project_name)
        copy_comparison = compare_manifests(source_before, destination_manifest)
        if not copy_comparison.matches:
            raise BackupError("recursive copy hash verification failed")
        manifest_payload = {
            "schemaVersion": SCHEMA_VERSION,
            "createdAtUtc": utc_now(),
            "source": source_before.to_json(include_root=False),
            "destination": destination_manifest.to_json(include_root=False),
            "sourceStable": True,
            "copyComparison": copy_comparison.to_json(),
            "readonlyOpen": None,
        }
        write_json(staging / "backup_manifest.json", manifest_payload)
        staging.rename(destination_root)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise

    final_manifest = build_manifest(destination_root, project_name)
    return CopyResult(
        source_manifest=source_before,
        destination_manifest=final_manifest,
        source_stable=True,
        copy_comparison=copy_comparison,
        manifest_path=destination_root / "backup_manifest.json",
    )


def build_open_command(
    analyze_headless: Path,
    project_root: Path,
    project_name: str,
    program_name: str,
    script_path: Path,
    program_md5: str,
) -> list[str]:
    if not re.fullmatch(r"[0-9a-fA-F]{32}", program_md5):
        raise BackupError("expected program MD5 must be exactly 32 hexadecimal characters")
    command = [
        str(analyze_headless),
        str(project_root.resolve()),
        project_name,
        "-process",
        program_name,
        "-readOnly",
        "-noanalysis",
        "-scriptPath",
        str(script_path.resolve()),
        "-postScript",
        "GhidraProjectOpenProbe.java",
        program_name,
    ]
    command.append(program_md5.lower())
    return command


def default_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            creationflags=CREATE_NO_WINDOW,
            timeout=DEFAULT_OPEN_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise BackupError(
            f"read-only Ghidra open probe timed out after {DEFAULT_OPEN_TIMEOUT_SECONDS} seconds"
        ) from exc


def verify_readonly_open(
    project_root: Path,
    project_name: str,
    program_name: str,
    analyze_headless: Path,
    script_path: Path,
    *,
    program_md5: str,
    runner: Runner = default_runner,
) -> OpenResult:
    if not re.fullmatch(r"[0-9a-fA-F]{32}", program_md5):
        raise BackupError("expected program MD5 must be exactly 32 hexadecimal characters")
    normalized_md5 = program_md5.lower()
    before = build_manifest(project_root, project_name)
    command = build_open_command(
        analyze_headless,
        project_root,
        project_name,
        program_name,
        script_path,
        normalized_md5,
    )
    completed = runner(command)
    after = build_manifest(project_root, project_name)
    comparison = compare_manifests(before, after)
    if completed.returncode != 0:
        raise BackupError(f"read-only open probe exit code {completed.returncode}")
    combined = f"{completed.stdout}\n{completed.stderr}"
    sentinel = f"{OPEN_SENTINEL_PREFIX}{program_name}"
    if normalized_md5:
        sentinel += f" md5={normalized_md5}"
    if sentinel not in combined:
        raise BackupError("read-only open probe did not emit the success sentinel")
    if not comparison.matches:
        raise BackupError("read-only open probe caused project content drift")
    return OpenResult(True, True, completed.returncode, normalized_md5, tuple(command), comparison)


def verify_on_copy(
    source_root: Path,
    scratch_root: Path,
    project_name: str,
    program_name: str,
    analyze_headless: Path,
    script_path: Path,
    *,
    program_md5: str,
    runner: Runner = default_runner,
    keep_failed_probe_copy: bool = False,
) -> VerificationResult:
    if not re.fullmatch(r"[0-9a-fA-F]{32}", program_md5):
        raise BackupError("expected program MD5 must be exactly 32 hexadecimal characters")
    source_root = resolve_plain_path(source_root, "source project root", strict=True)
    scratch_root = resolve_plain_path(scratch_root, "scratch root", strict=False)
    require_disjoint_paths(source_root, scratch_root, "source and scratch roots")
    scratch_root.mkdir(parents=True, exist_ok=True)
    scratch_root = resolve_plain_path(scratch_root, "scratch root", strict=True)
    source_before = build_manifest(source_root, project_name)
    probe_copy = scratch_root / f"{project_name}-open-probe-{uuid.uuid4().hex}"
    try:
        copy_result = copy_project_pair(source_root, probe_copy, project_name)
        open_result = verify_readonly_open(
            probe_copy,
            project_name,
            program_name,
            analyze_headless,
            script_path,
            program_md5=program_md5,
            runner=runner,
        )
        source_after = build_manifest(source_root, project_name)
        source_stable = compare_manifests(source_before, source_after).matches
        if not source_stable:
            raise BackupError("source content changed during copied-project open verification")
        return VerificationResult(source_before, copy_result, open_result, source_stable, probe_copy)
    except Exception:
        if probe_copy.exists() and not keep_failed_probe_copy:
            safe_remove_probe_copy(probe_copy, scratch_root, project_name)
        raise


def verification_receipt(result: VerificationResult) -> dict[str, object]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "verifiedAtUtc": utc_now(),
        "source": result.source_manifest.to_json(),
        "probeCopy": str(result.probe_copy),
        "sourceStable": result.source_stable,
        "copyComparison": result.copy_result.copy_comparison.to_json(),
        "readonlyOpen": result.open_result.to_json(),
    }


def sanitized_summary(result: CopyResult | VerificationResult) -> str:
    if isinstance(result, VerificationResult):
        manifest = result.source_manifest
        comparison = result.copy_result.copy_comparison
        opened = result.open_result.opened
    else:
        manifest = result.source_manifest
        comparison = result.copy_comparison
        opened = False
    return (
        f"project={manifest.project_name} Files={len(manifest.files)} Bytes={manifest.total_bytes} "
        f"MissingCount={len(comparison.missing)} ExtraCount={len(comparison.extra)} "
        f"SizeDiffCount={len(comparison.size_differences)} HashDiffCount={len(comparison.hash_differences)} "
        f"ReadOnlyOpen={'PASS' if opened else 'NOT_RUN'}"
    )


def safe_remove_probe_copy(probe_copy: Path, scratch_root: Path, project_name: str) -> None:
    probe_copy = resolve_plain_path(probe_copy, "probe copy", strict=True)
    scratch_root = resolve_plain_path(scratch_root, "scratch root", strict=True)
    expected_prefix = f"{project_name}-open-probe-"
    if probe_copy.parent != scratch_root or not probe_copy.name.startswith(expected_prefix):
        raise BackupError("refusing to remove a path outside the exact tool-created scratch scope")
    shutil.rmtree(probe_copy)


def publish_verification_result(
    result: VerificationResult,
    receipt_path: Path,
    scratch_root: Path,
    project_name: str,
    *,
    keep_probe_copy: bool,
) -> None:
    try:
        receipt_path = validate_external_output_path(
            receipt_path,
            [result.source_manifest.root, scratch_root, result.probe_copy],
            "verification receipt",
        )
        write_json(receipt_path, verification_receipt(result))
    finally:
        if result.probe_copy.exists() and not keep_probe_copy:
            safe_remove_probe_copy(result.probe_copy, scratch_root, project_name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="hash and inspect one complete project pair")
    inspect_parser.add_argument("project_root", type=Path)
    inspect_parser.add_argument("--project-name", default="BEA")
    inspect_parser.add_argument("--output", type=Path)

    copy_parser = subparsers.add_parser("copy", help="recursively copy and hash-verify one project pair")
    copy_parser.add_argument("source_root", type=Path)
    copy_parser.add_argument("destination_root", type=Path)
    copy_parser.add_argument("--project-name", default="BEA")

    verify_parser = subparsers.add_parser("verify", help="copy to scratch and prove read-only openability")
    verify_parser.add_argument("source_root", type=Path)
    verify_parser.add_argument("--scratch-root", required=True, type=Path)
    verify_parser.add_argument("--receipt", required=True, type=Path)
    verify_parser.add_argument("--project-name", default="BEA")
    verify_parser.add_argument("--program", default="BEA.exe")
    verify_parser.add_argument("--program-md5", required=True)
    verify_parser.add_argument("--analyze-headless", required=True, type=Path)
    verify_parser.add_argument("--script-path", default=Path(__file__).resolve().parent, type=Path)
    verify_parser.add_argument("--keep-probe-copy", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "inspect":
            manifest = build_manifest(args.project_root, args.project_name)
            payload = {"schemaVersion": SCHEMA_VERSION, "manifest": manifest.to_json()}
            if args.output:
                output = validate_external_output_path(
                    args.output, [manifest.root], "inspection output"
                )
                write_json(output, payload)
            print(f"project={args.project_name} Files={len(manifest.files)} Bytes={manifest.total_bytes}")
        elif args.command == "copy":
            result = copy_project_pair(args.source_root, args.destination_root, args.project_name)
            print(sanitized_summary(result))
        else:
            result = verify_on_copy(
                args.source_root,
                args.scratch_root,
                args.project_name,
                args.program,
                args.analyze_headless,
                args.script_path,
                program_md5=args.program_md5,
                keep_failed_probe_copy=args.keep_probe_copy,
            )
            print(sanitized_summary(result))
            publish_verification_result(
                result,
                args.receipt,
                args.scratch_root,
                args.project_name,
                keep_probe_copy=args.keep_probe_copy,
            )
    except (BackupError, OSError) as exc:
        print("Ghidra project backup: FAIL")
        print(f"- {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
