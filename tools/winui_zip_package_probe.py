#!/usr/bin/env python3
"""Build, zip, extract, and smoke a disposable WinUI ZIP package.

This probe is the non-cert distribution lane for the current WinUI app. It
publishes the app under ``subagents/``, stages a user-friendly portable bundle
root, creates a ZIP archive, extracts it to a fresh ignored folder, then runs
existing UI Automation smoke tests against the extracted executable through
``ONSLAUGHT_WINUI_TEST_EXE_PATH``.

It does not sign, install, create MSIX/AppInstaller artifacts, mutate Windows
certificate stores, or prove installer/SmartScreen/store readiness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "OnslaughtCareerEditor.WinUI" / "OnslaughtCareerEditor.WinUI.csproj"
UITESTS = ROOT / "OnslaughtCareerEditor.UiTests" / "OnslaughtCareerEditor.UiTests.csproj"
DEFAULT_OUT_ROOT = ROOT / "subagents" / "winui-zip-package-probe" / "current"
APP_EXE = "OnslaughtCareerEditor.WinUI.exe"
APP_PRI = "OnslaughtCareerEditor.WinUI.pri"
NOTICES = "THIRD_PARTY_NOTICES.md"
ZIP_README_SOURCE = ROOT / "release" / "readiness" / "WINUI-ZIP-README.txt"
ROOT_LAUNCHER = "Launch Onslaught Toolkit.cmd"
ROOT_README = "README.MD"
ROOT_LICENSE = "LICENSE"
APP_DIR = "app"
LORE_BOOK_DIR = "lore-book"
LORE_BOOK_REQUIRED_FILE = f"{LORE_BOOK_DIR}/BOOK.md"
LORE_BOOK_SOURCE = ROOT / LORE_BOOK_DIR
REQUIRED_APP_FILES = (
    APP_EXE,
    APP_PRI,
    NOTICES,
    "patches/catalog/patches.v2.json",
    "patches/catalog/safe-copy-profiles.v1.json",
)
REQUIRED_ROOT_FILES = (
    ROOT_LAUNCHER,
    ROOT_README,
    ROOT_LICENSE,
)
REQUIRED_PAYLOAD_FILES = REQUIRED_ROOT_FILES + (LORE_BOOK_REQUIRED_FILE,) + tuple(f"{APP_DIR}/{filename}" for filename in REQUIRED_APP_FILES)
DEFAULT_PACKAGE_NAME = "OnslaughtCareerEditor.WinUI-local-probe-win-x64.zip"
HOME_NAVIGATION_FILTER = "FullyQualifiedName~WinUiHomeNavigationSmokeTests"
LORE_SMOKE_FILTER = "FullyQualifiedName~WinUiLoreInteractionSmokeTests.LoreReader_SearchesSelectsAndShowsCurrentDocumentThroughUiAutomation"
HOME_NAVIGATION_TEST_TIMEOUT_SECONDS = 600
LORE_SMOKE_TEST_TIMEOUT_SECONDS = 240
MEDIA_SMOKE_MAX_ATTEMPTS = 2
ZIP_PAYLOAD_DENY_SEGMENTS = {
    ".codex",
    "GameProfiles",
    "Ghidra",
    "PatchBench",
    "game",
    "ghidra-local",
    "local-game",
    "local-ghidra",
    "local-lab",
    "local-media",
    "local-proofs",
    "local-saves",
    "media",
    "save-attempts",
}
ZIP_PAYLOAD_DENY_SUFFIXES = (
    ".aya",
    ".bea",
    ".bes",
    ".bik",
    ".bytes",
    ".dds",
    ".dmp",
    ".etl",
    ".fbx",
    ".gbf",
    ".gdt",
    ".gpr",
    ".gzf",
    ".mp3",
    ".mp4",
    ".raw",
    ".trx",
    ".vid",
    ".wav",
)
ZIP_PAYLOAD_DENY_FILENAMES = {
    "bea.exe",
    "bea.exe.original.backup",
    "bea_widescreen.exe",
    "defaultoptions.bea",
}


@dataclass
class CheckResult:
    key: str
    status: str
    summary: str


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def safe_rmtree(path: Path) -> None:
    path = path.resolve()
    try:
        path.relative_to((ROOT / "subagents").resolve())
    except ValueError as exc:
        raise RuntimeError(f"Refusing to remove path outside subagents/: {path}") from exc
    if path.exists():
        shutil.rmtree(path)


def run(command: list[str], timeout_seconds: int = 300, env: dict[str, str] | None = None) -> tuple[int, str]:
    effective_env = os.environ.copy()
    effective_env["MSBUILDDISABLENODEREUSE"] = "1"
    if env:
        effective_env.update(env)
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
            check=False,
            env=effective_env,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        return 124, f"Timed out after {timeout_seconds} seconds.\n{output}"
    return completed.returncode, completed.stdout


def run_powershell(script: str, timeout_seconds: int = 120) -> tuple[int, str]:
    return run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ],
        timeout_seconds=timeout_seconds,
    )


def run_publish(publish_dir: Path) -> tuple[int, str]:
    return run(
        [
            "dotnet",
            "publish",
            str(PROJECT),
            "-c",
            "Release",
            "-r",
            "win-x64",
            "--self-contained",
            "true",
            "-o",
            str(publish_dir),
            "--nologo",
        ],
        timeout_seconds=360,
    )


def write_launcher(bundle_dir: Path) -> CheckResult:
    destination = bundle_dir / ROOT_LAUNCHER
    content = "\r\n".join(
        [
            "@echo off",
            "setlocal",
            'set "APP_DIR=%~dp0app"',
            'set "APP_EXE=%APP_DIR%\\OnslaughtCareerEditor.WinUI.exe"',
            'if not exist "%APP_EXE%" (',
            "  echo Onslaught Toolkit app payload is missing:",
            '  echo   "%APP_EXE%"',
            "  pause",
            "  exit /b 1",
            ")",
            'start "" /D "%APP_DIR%" "%APP_EXE%"',
            "",
        ]
    )
    destination.write_text(content, encoding="utf-8", newline="")
    return CheckResult("bundle_launcher", "PASS", f"{relative(destination)} written with app-folder launch target.")


def copy_zip_readme(bundle_dir: Path) -> CheckResult:
    destination = bundle_dir / ROOT_README
    if not ZIP_README_SOURCE.is_file() or ZIP_README_SOURCE.stat().st_size <= 0:
        return CheckResult("zip_readme_source", "FAIL", f"{relative(ZIP_README_SOURCE)} is missing or empty.")
    shutil.copy2(ZIP_README_SOURCE, destination)
    return CheckResult("bundle_readme", "PASS", f"{relative(destination)} copied from public-safe ZIP README template.")


def copy_license(bundle_dir: Path) -> CheckResult:
    source = ROOT / ROOT_LICENSE
    destination = bundle_dir / ROOT_LICENSE
    if not source.is_file() or source.stat().st_size <= 0:
        return CheckResult("license_source", "FAIL", f"{relative(source)} is missing or empty.")
    shutil.copy2(source, destination)
    return CheckResult("bundle_license", "PASS", f"{relative(destination)} copied from repo license.")


def copy_lore_book(bundle_dir: Path) -> CheckResult:
    destination = bundle_dir / LORE_BOOK_DIR
    required_source = LORE_BOOK_SOURCE / "BOOK.md"
    if not required_source.is_file() or required_source.stat().st_size <= 0:
        return CheckResult("lore_book_source", "FAIL", f"{relative(required_source)} is missing or empty.")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(LORE_BOOK_SOURCE, destination)
    required_destination = destination / "BOOK.md"
    return CheckResult(
        "bundle_lore_book",
        "PASS" if required_destination.is_file() and required_destination.stat().st_size > 0 else "FAIL",
        f"{relative(destination)} copied so the packaged Lore page has an offline index."
        if required_destination.is_file() and required_destination.stat().st_size > 0
        else f"{relative(required_destination)} is missing after copy.",
    )


def stage_portable_bundle(publish_dir: Path, bundle_dir: Path) -> list[CheckResult]:
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    app_dir = bundle_dir / APP_DIR
    shutil.copytree(publish_dir, app_dir)
    checks = [
        write_launcher(bundle_dir),
        copy_zip_readme(bundle_dir),
        copy_license(bundle_dir),
        copy_lore_book(bundle_dir),
    ]
    return checks


def inspect_app_payload_folder(root: Path, prefix: str) -> list[CheckResult]:
    checks: list[CheckResult] = []
    for filename in REQUIRED_APP_FILES:
        path = root / filename
        key = filename.replace("/", "_").replace("\\", "_")
        checks.append(
            CheckResult(
                f"{prefix}_{key}",
                "PASS" if path.is_file() and path.stat().st_size > 0 else "FAIL",
                f"{relative(path)} exists and is non-empty." if path.is_file() and path.stat().st_size > 0 else f"{relative(path)} is missing or empty.",
            )
        )
    return checks


def inspect_root_layout_names(names: set[str], prefix: str) -> list[CheckResult]:
    checks: list[CheckResult] = []
    root_files = sorted(name for name in names if "/" not in name.rstrip("/"))
    top_levels = sorted({name.rstrip("/").split("/", 1)[0] for name in names if name.rstrip("/")})
    allowed_top_levels = set(REQUIRED_ROOT_FILES) | {APP_DIR, LORE_BOOK_DIR}
    unexpected_top_levels = [name for name in top_levels if name not in allowed_top_levels]
    root_executables = [name for name in root_files if name.lower().endswith(".exe")]
    root_dlls = [name for name in root_files if name.lower().endswith(".dll")]
    checks.append(
        CheckResult(
            f"{prefix}_friendly_root_shape",
            "PASS" if not unexpected_top_levels else "FAIL",
            "Top-level ZIP/folder entries are limited to launcher, readme, license, lore-book/, and app/."
            if not unexpected_top_levels
            else "Unexpected top-level entries: " + ", ".join(unexpected_top_levels[:12]),
        )
    )
    checks.append(
        CheckResult(
            f"{prefix}_no_root_executables",
            "PASS" if not root_executables else "FAIL",
            "No executable files are exposed at the package root."
            if not root_executables
            else "Executable files exposed at package root: " + ", ".join(root_executables[:12]),
        )
    )
    checks.append(
        CheckResult(
            f"{prefix}_no_root_dlls",
            "PASS" if not root_dlls else "FAIL",
            "No DLL files are exposed at the package root."
            if not root_dlls
            else "DLL files exposed at package root: " + ", ".join(root_dlls[:12]),
        )
    )
    return checks


def inspect_payload_safety_names(names: set[str], prefix: str) -> list[CheckResult]:
    findings: list[str] = []
    deny_segments_lower = {segment.lower() for segment in ZIP_PAYLOAD_DENY_SEGMENTS}
    for name in sorted(names):
        normalized = name.replace("\\", "/").strip("/")
        if not normalized:
            continue
        parts = [part for part in normalized.split("/") if part]
        lower_parts = [part.lower() for part in parts]
        basename = lower_parts[-1] if lower_parts else ""
        lower_name = normalized.lower()
        if any(part in deny_segments_lower for part in lower_parts):
            findings.append(f"{normalized} (payload-root segment)")
            continue
        if basename in ZIP_PAYLOAD_DENY_FILENAMES:
            findings.append(f"{normalized} (game executable/options filename)")
            continue
        if lower_name.endswith(ZIP_PAYLOAD_DENY_SUFFIXES):
            findings.append(f"{normalized} (hard-payload suffix)")
    if findings:
        return [
            CheckResult(
                f"{prefix}_payload_safety",
                "FAIL",
                "Hard-payload-like package entries: " + ", ".join(findings[:12]),
            )
        ]
    return [
        CheckResult(
            f"{prefix}_payload_safety",
            "PASS",
            "No game/proof/save/media/Ghidra hard-payload entries were found in the packaged layout.",
        )
    ]


def inspect_folder(root: Path, prefix: str) -> list[CheckResult]:
    checks: list[CheckResult] = []
    for filename in REQUIRED_PAYLOAD_FILES:
        path = root / filename
        key = filename.replace("/", "_").replace("\\", "_")
        checks.append(
            CheckResult(
                f"{prefix}_{key}",
                "PASS" if path.is_file() and path.stat().st_size > 0 else "FAIL",
                f"{relative(path)} exists and is non-empty." if path.is_file() and path.stat().st_size > 0 else f"{relative(path)} is missing or empty.",
            )
        )
    if root.is_dir():
        names = set()
        for path in root.rglob("*"):
            try:
                names.add(path.relative_to(root).as_posix())
            except ValueError:
                continue
        checks.extend(inspect_root_layout_names(names, prefix))
        checks.extend(inspect_payload_safety_names(names, prefix))
    package_suffixes = {".msix", ".appx", ".appinstaller", ".msixbundle", ".appxbundle"}
    package_files = [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in package_suffixes]
    checks.append(
        CheckResult(
            f"{prefix}_installer_artifacts",
            "FAIL" if package_files else "PASS",
            "Unexpected installer artifacts exist: " + ", ".join(relative(path) for path in package_files[:5])
            if package_files
            else "No MSIX/AppX/AppInstaller artifacts are present.",
        )
    )
    return checks


def create_zip(source_dir: Path, zip_path: Path) -> tuple[int, str]:
    try:
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as package:
            for path in sorted(source_dir.rglob("*")):
                if path.is_file():
                    package.write(path, path.relative_to(source_dir).as_posix())
    except Exception as exc:  # pragma: no cover - defensive filesystem report
        return 1, str(exc)
    return 0, f"Created {relative(zip_path)} ({zip_path.stat().st_size} bytes)."


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksum(zip_path: Path, checksum_path: Path, sha256: str) -> None:
    checksum_path.write_text(f"{sha256}  {zip_path.name}\n", encoding="utf-8", newline="\n")


def inspect_zip(zip_path: Path) -> list[CheckResult]:
    checks: list[CheckResult] = []
    if not zip_path.is_file() or zip_path.stat().st_size <= 0:
        return [CheckResult("zip_file", "FAIL", f"{relative(zip_path)} was not created.")]
    checks.append(CheckResult("zip_file", "PASS", f"{relative(zip_path)} exists and is non-empty."))
    with zipfile.ZipFile(zip_path) as package:
        names = set(package.namelist())
    for filename in REQUIRED_PAYLOAD_FILES:
        key = filename.replace("/", "_").replace("\\", "_")
        checks.append(
            CheckResult(
                f"zip_contains_{key}",
                "PASS" if filename in names else "FAIL",
                f"ZIP contains {filename}." if filename in names else f"ZIP does not contain {filename}.",
            )
        )
    checks.extend(inspect_root_layout_names(names, "zip"))
    checks.extend(inspect_payload_safety_names(names, "zip"))
    installer_suffixes = (".msix", ".appx", ".appinstaller", ".msixbundle", ".appxbundle")
    installers = [name for name in names if name.lower().endswith(installer_suffixes)]
    checks.append(
        CheckResult(
            "zip_installer_artifacts",
            "FAIL" if installers else "PASS",
            "Unexpected installer artifacts in ZIP: " + ", ".join(installers[:5])
            if installers
            else "ZIP contains no MSIX/AppX/AppInstaller artifacts.",
        )
    )
    return checks


def extract_zip(zip_path: Path, extract_dir: Path) -> tuple[int, str]:
    try:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as package:
            package.extractall(extract_dir)
    except Exception as exc:  # pragma: no cover - defensive filesystem report
        return 1, str(exc)
    return 0, f"Extracted {relative(zip_path)} to {relative(extract_dir)}."


def run_ui_test(
    test_filter: str,
    exe_path: Path,
    *,
    timeout_seconds: int = 240,
    nunit_workers: int | None = None,
) -> tuple[int, str]:
    command = [
        "dotnet",
        "test",
        str(UITESTS),
        "--nologo",
        "--filter",
        test_filter,
    ]
    if nunit_workers is not None:
        command.extend(["--", f"NUnit.NumberOfTestWorkers={nunit_workers}"])
    return run(
        command,
        timeout_seconds=timeout_seconds,
        env={"ONSLAUGHT_WINUI_TEST_EXE_PATH": str(exe_path)},
    )


def run_ui_test_with_retry(
    test_filter: str,
    exe_path: Path,
    *,
    max_attempts: int,
    timeout_seconds: int = 240,
    nunit_workers: int | None = None,
) -> tuple[int, str, int]:
    attempts: list[str] = []
    last_exit = 1
    for attempt in range(1, max_attempts + 1):
        last_exit, output = run_ui_test(
            test_filter,
            exe_path,
            timeout_seconds=timeout_seconds,
            nunit_workers=nunit_workers,
        )
        attempts.append(f"=== attempt {attempt} exit {last_exit} ===\n{output}")
        if last_exit == 0:
            return last_exit, "\n\n".join(attempts), attempt
        if attempt < max_attempts:
            stop_app_process()
    return last_exit, "\n\n".join(attempts), max_attempts


def ui_test_passed_without_skip(exit_code: int | None, output: str) -> bool:
    if exit_code != 0:
        return False
    skipped_match = re.search(r"Skipped:\s+([1-9][0-9]*)", output)
    return skipped_match is None


def get_process_state() -> tuple[int, str]:
    return run_powershell(
        "Get-Process -Name OnslaughtCareerEditor.WinUI -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,Path | ConvertTo-Json -Compress",
        timeout_seconds=60,
    )


def stop_app_process() -> tuple[int, str]:
    return run_powershell(
        "$procs = Get-Process -Name OnslaughtCareerEditor.WinUI -ErrorAction SilentlyContinue; if ($null -eq $procs) { 'not-running'; exit 0 }; $procs | Stop-Process -Force -ErrorAction Stop; 'stopped'",
        timeout_seconds=60,
    )


def build_report(
    out_root: Path,
    zip_path: Path,
    checksum_path: Path,
    zip_sha256: str,
    checks: list[CheckResult],
    publish_exit: int,
    publish_output: str,
    zip_output: str,
    extract_exit: int,
    extract_output: str,
    launch_exit: int | None,
    launch_output: str,
    home_navigation_exit: int | None,
    home_navigation_output: str,
    lore_exit: int | None,
    lore_output: str,
    media_exit: int | None,
    media_output: str,
    process_after: str,
) -> dict[str, object]:
    failures = [item for item in checks if item.status == "FAIL"]
    return {
        "schema": "winui-zip-package-probe.v1",
        "status": "pass" if publish_exit == 0 and extract_exit == 0 and not failures else "blocked",
        "releaseClaim": "Disposable friendly portable ZIP package, extraction, extracted app launch smoke, and extracted app Home navigation smoke (all WinUiHomeNavigationSmokeTests) are proven only if status is pass; signing/MSIX/installer/SmartScreen readiness remain separate gates.",
        "outputRoot": relative(out_root),
        "zipPackage": relative(zip_path),
        "zipByteSize": zip_path.stat().st_size if zip_path.is_file() else 0,
        "zipSha256": zip_sha256,
        "checksumFile": relative(checksum_path),
        "releasePackageName": zip_path.name,
        "publishExitCode": publish_exit,
        "zipOutput": zip_output,
        "extractExitCode": extract_exit,
        "extractOutput": extract_output,
        "launchSmokeExitCode": launch_exit,
        "homeNavigationSmokeExitCode": home_navigation_exit,
        "homeDeeplinkSmokeExitCode": home_navigation_exit,
        "loreSmokeExitCode": lore_exit,
        "mediaSmokeExitCode": media_exit,
        "checks": [item.__dict__ for item in checks],
        "publishOutputTail": "\n".join(publish_output.splitlines()[-20:]),
        "launchOutputTail": "\n".join(launch_output.splitlines()[-40:]),
        "homeNavigationOutputTail": "\n".join(home_navigation_output.splitlines()[-40:]),
        "homeDeeplinkOutputTail": "\n".join(home_navigation_output.splitlines()[-40:]),
        "loreOutputTail": "\n".join(lore_output.splitlines()[-40:]),
        "mediaOutputTail": "\n".join(media_output.splitlines()[-40:]),
        "processAfter": process_after.strip() or "<none>",
        "notProven": [
            "MSIX/AppInstaller packaging",
            "Certificate signing or trust",
            "Windows package identity launch",
            "Start-menu installer integration",
            "SmartScreen/store/reputation posture",
            "Legal/compliance approval for public binary redistribution",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build, zip, extract, and smoke a disposable WinUI ZIP package.")
    parser.add_argument("--check", action="store_true", help="run the ZIP package probe")
    parser.add_argument("--json", action="store_true", help="print JSON report")
    parser.add_argument("--include-media-smoke", action="store_true", help="also run representative Media playback against the extracted executable")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT, help="ignored output root under subagents/")
    parser.add_argument("--package-name", default=DEFAULT_PACKAGE_NAME, help="ZIP filename to create under the ignored output root")
    args = parser.parse_args()

    if not args.check:
        parser.error("expected --check")
    if not PROJECT.is_file() or not UITESTS.is_file():
        print("Missing WinUI project or UiTests project.")
        return 1

    out_root = args.out_root
    if not out_root.is_absolute():
        out_root = ROOT / out_root
    out_root = out_root.resolve()
    try:
        out_root.relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write ZIP probe output outside subagents/: {out_root}")
        return 1

    safe_rmtree(out_root)
    publish_dir = out_root / "publish"
    bundle_dir = out_root / "bundle"
    extract_dir = out_root / "extract"
    package_name = args.package_name
    if Path(package_name).name != package_name or not package_name.lower().endswith(".zip"):
        print("Package name must be a plain .zip filename.")
        return 1
    zip_path = out_root / package_name
    checksum_path = out_root / f"{package_name}.sha256"
    publish_dir.mkdir(parents=True, exist_ok=True)

    checks: list[CheckResult] = []
    publish_exit, publish_output = run_publish(publish_dir)
    if publish_exit == 0:
        checks.extend(inspect_app_payload_folder(publish_dir, "publish_app"))
        if all(item.status != "FAIL" for item in checks):
            checks.extend(stage_portable_bundle(publish_dir, bundle_dir))
            checks.extend(inspect_folder(bundle_dir, "bundle"))

    zip_exit = 1
    zip_output = ""
    extract_exit = 1
    extract_output = ""
    launch_exit: int | None = None
    launch_output = ""
    home_navigation_exit: int | None = None
    home_navigation_output = ""
    lore_exit: int | None = None
    lore_output = ""
    media_exit: int | None = None
    media_output = ""
    process_after = ""
    zip_sha256 = ""

    if publish_exit == 0 and all(item.status != "FAIL" for item in checks):
        zip_exit, zip_output = create_zip(bundle_dir, zip_path)
        checks.append(
            CheckResult(
                "zip_create",
                "PASS" if zip_exit == 0 else "FAIL",
                zip_output if zip_exit == 0 else f"ZIP creation failed: {zip_output}",
            )
        )
        if zip_exit == 0:
            zip_sha256 = sha256_file(zip_path)
            write_checksum(zip_path, checksum_path, zip_sha256)
            checks.append(
                CheckResult(
                    "zip_sha256",
                    "PASS" if len(zip_sha256) == 64 and checksum_path.is_file() else "FAIL",
                    f"SHA-256 checksum sidecar exists for {zip_path.name}." if len(zip_sha256) == 64 and checksum_path.is_file() else "SHA-256 checksum sidecar is missing.",
                )
            )
            checks.extend(inspect_zip(zip_path))
            extract_exit, extract_output = extract_zip(zip_path, extract_dir)
            checks.append(
                CheckResult(
                    "zip_extract",
                    "PASS" if extract_exit == 0 else "FAIL",
                    extract_output if extract_exit == 0 else f"ZIP extraction failed: {extract_output}",
                )
            )
            if extract_exit == 0:
                checks.extend(inspect_folder(extract_dir, "extract"))
                extracted_exe = extract_dir / APP_DIR / APP_EXE
                if extracted_exe.is_file():
                    launch_exit, launch_output = run_ui_test("FullyQualifiedName~WinUiLaunchSmokeTests.MainWindow_LaunchesAndShowsWinUiProductChrome", extracted_exe)
                    checks.append(
                        CheckResult(
                            "extracted_launch_smoke",
                            "PASS" if ui_test_passed_without_skip(launch_exit, launch_output) else "FAIL",
                            f"Launch smoke exit code {launch_exit}; skipped rows are not accepted.",
                        )
                    )
                    if ui_test_passed_without_skip(launch_exit, launch_output):
                        stop_app_process()
                        home_navigation_exit, home_navigation_output = run_ui_test(
                            HOME_NAVIGATION_FILTER,
                            extracted_exe,
                            timeout_seconds=HOME_NAVIGATION_TEST_TIMEOUT_SECONDS,
                            nunit_workers=1,
                        )
                        checks.append(
                            CheckResult(
                                "extracted_home_navigation_smoke",
                                "PASS" if ui_test_passed_without_skip(home_navigation_exit, home_navigation_output) else "FAIL",
                                f"Home navigation smoke exit code {home_navigation_exit}; skipped rows are not accepted.",
                            )
                        )
                    if ui_test_passed_without_skip(launch_exit, launch_output) and ui_test_passed_without_skip(home_navigation_exit, home_navigation_output):
                        stop_app_process()
                        lore_exit, lore_output = run_ui_test(
                            LORE_SMOKE_FILTER,
                            extracted_exe,
                            timeout_seconds=LORE_SMOKE_TEST_TIMEOUT_SECONDS,
                        )
                        checks.append(
                            CheckResult(
                                "extracted_lore_smoke",
                                "PASS" if ui_test_passed_without_skip(lore_exit, lore_output) else "FAIL",
                                f"Lore reader smoke exit code {lore_exit}; skipped rows are not accepted.",
                            )
                        )
                    if args.include_media_smoke and ui_test_passed_without_skip(launch_exit, launch_output) and ui_test_passed_without_skip(home_navigation_exit, home_navigation_output) and ui_test_passed_without_skip(lore_exit, lore_output):
                        stop_app_process()
                        media_exit, media_output, media_attempts = run_ui_test_with_retry(
                            "FullyQualifiedName~WinUiMediaInteractionSmokeTests.MediaPage_PlaysRepresentativeAudioAndVideoRowsThroughUi",
                            extracted_exe,
                            max_attempts=MEDIA_SMOKE_MAX_ATTEMPTS,
                        )
                        checks.append(
                            CheckResult(
                                "extracted_media_smoke",
                                "PASS" if ui_test_passed_without_skip(media_exit, media_output) else "FAIL",
                                f"Representative Media smoke exit code {media_exit} after {media_attempts} attempt(s); skipped rows are not accepted.",
                            )
                        )

    stop_app_process()
    _, process_after = get_process_state()
    checks.append(
        CheckResult(
            "process_after",
            "PASS" if not process_after.strip() else "FAIL",
            "No WinUI process remains after ZIP probe." if not process_after.strip() else "WinUI process remains after ZIP probe.",
        )
    )

    report = build_report(
        out_root,
        zip_path,
        checksum_path,
        zip_sha256,
        checks,
        publish_exit,
        publish_output,
        zip_output,
        extract_exit,
        extract_output,
        launch_exit,
        launch_output,
        home_navigation_exit,
        home_navigation_output,
        lore_exit,
        lore_output,
        media_exit,
        media_output,
        process_after,
    )
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "zip-package-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("WinUI ZIP package probe")
        print(f"Status: {report['status']}")
        print(f"Release claim: {report['releaseClaim']}")
        print(f"ZIP package: {report['zipPackage']}")
        print(f"ZIP byte size: {report['zipByteSize']}")
        for item in report["checks"]:
            print(f"- {item['status']}: {item['key']}: {item['summary']}")
        if report["status"] != "pass":
            print("Launch output:")
            print(report["launchOutputTail"])
            print("Home navigation output:")
            print(report["homeNavigationOutputTail"])
            print("Lore output:")
            print(report["loreOutputTail"])
            print("Media output:")
            print(report["mediaOutputTail"])

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
