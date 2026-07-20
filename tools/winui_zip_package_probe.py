#!/usr/bin/env python3
"""Build, zip, extract, and smoke a disposable WinUI ZIP package.

This probe is the non-cert distribution lane for the current WinUI app. It
publishes the app under ignored ``.artifacts/``, stages a user-friendly portable bundle
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
import posixpath
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import winui_lore_pack_builder
import generate_winui_third_party_notices as winui_third_party_notices

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "OnslaughtCareerEditor.WinUI" / "OnslaughtCareerEditor.WinUI.csproj"
UITESTS = ROOT / "OnslaughtCareerEditor.UiTests" / "OnslaughtCareerEditor.UiTests.csproj"
ARTIFACTS_ROOT = ROOT / ".artifacts"
DEFAULT_OUT_ROOT = ARTIFACTS_ROOT / "winui-zip-package-probe"
APP_EXE = "OnslaughtCareerEditor.WinUI.exe"
APP_PRI = "OnslaughtCareerEditor.WinUI.pri"
NOTICES = "THIRD_PARTY_NOTICES.md"
THIRD_PARTY_LICENSES_DIR = "THIRD_PARTY_LICENSES"
THIRD_PARTY_LICENSES_INDEX = f"{THIRD_PARTY_LICENSES_DIR}/README.txt"
DOTNET_LICENSE = f"{THIRD_PARTY_LICENSES_DIR}/DOTNET-LICENSE.txt"
DOTNET_NOTICES = f"{THIRD_PARTY_LICENSES_DIR}/DOTNET-THIRD-PARTY-NOTICES.txt"
LICENSE_TEMPLATE_ROOT = ROOT / "release" / "readiness" / "licenses"
LICENSE_TEMPLATES = {
    "MIT": LICENSE_TEMPLATE_ROOT / "MIT.template.txt",
    "BSD-2-Clause": LICENSE_TEMPLATE_ROOT / "BSD-2-Clause.template.txt",
}
PACKAGE_LICENSE_OVERRIDES = {
    "sharpdx": "MIT",
    "sharpdx.direct3d11": "MIT",
    "sharpdx.dxgi": "MIT",
}
# These old packages declare an SPDX expression or legacy license URL but do
# not embed their exact tagged-source copyright notice in the nupkg.
PACKAGE_COPYRIGHT_OVERRIDES = {
    "markdig": "Copyright (c) 2018-2019, Alexandre Mutel\nAll rights reserved.",
    "sharpdx": "Copyright (c) 2010-2014 SharpDX - Alexandre Mutel",
    "sharpdx.direct3d11": "Copyright (c) 2010-2014 SharpDX - Alexandre Mutel",
    "sharpdx.dxgi": "Copyright (c) 2010-2014 SharpDX - Alexandre Mutel",
}
PACKAGE_LICENSE_FILE_REGEX = re.compile(r"^(?:license|licence|copying|notice)(?:\..*)?$", re.IGNORECASE)
ZIP_README_SOURCE = ROOT / "release" / "readiness" / "WINUI-ZIP-README.txt"
ROOT_LAUNCHER = "Launch Onslaught Toolkit.cmd"
ROOT_README = "README.MD"
ROOT_LICENSE = "LICENSE"
APP_DIR = "app"
LORE_BOOK_DIR = "lore-book"
LORE_PACK_DIR = "lore-pack"
LORE_BOOK_REQUIRED_FILE = f"{LORE_BOOK_DIR}/BOOK.md"
LORE_PACK_INDEX_FILE = f"{LORE_PACK_DIR}/{winui_lore_pack_builder.INDEX_FILE_NAME}"
LORE_PACK_CONTENT_FILE = f"{LORE_PACK_DIR}/{winui_lore_pack_builder.CONTENT_FILE_NAME}"
LORE_BOOK_SOURCE = ROOT / LORE_BOOK_DIR
LORE_BOOK_LINK_REGEX = re.compile(r"\[[^\]]+\]\((?P<target>[^)]+)\)")
LORE_BOOK_MARKDOWN_LINK_REGEX = re.compile(r"(?P<prefix>\[[^\]]+\]\()(?P<target>[^)]+)(?P<suffix>\))")
LORE_PACK_DOCUMENT_ID_REGEX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
GITHUB_SOURCE_BLOB_BASE = "https://github.com/dlprentice/Onslaught-Career-Editor/blob/main"
GITHUB_SOURCE_SEARCH_BASE = "https://github.com/dlprentice/Onslaught-Career-Editor/search"
PACKAGED_LORE_FORBIDDEN_CLAIMS = (
    "Internal links stay inside the app.",
    "without leaving the app",
)
LORE_PACK_FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"\b[A-Z]:\\", re.IGNORECASE),
    re.compile(r"\b[A-Z]:\\(?:Users|Steam|GhidraBackups|OnslaughtRuntimeProofArchive)\\", re.IGNORECASE),
    re.compile(r"\bG:\\(?:GhidraBackups|OnslaughtRuntimeProofArchive)\\", re.IGNORECASE),
    re.compile(r"https?://(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|127\.\d{1,3}\.\d{1,3}\.\d{1,3}|localhost)(?::\d+)?(?:/[^\s<>()\]]*)?", re.IGNORECASE),
    re.compile(r"\b(?:0:000>|Child-SP|RetAddr)\b", re.IGNORECASE),
    re.compile(r"\bdata:image/(?:png|jpeg|webp);base64,", re.IGNORECASE),
    re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9_]{20,})\b"),
)
WINDOWS_EXPLORER_SAFE_ENTRY_LENGTH = 180
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
REQUIRED_PAYLOAD_FILES = (
    REQUIRED_ROOT_FILES
    + (
        LORE_BOOK_REQUIRED_FILE,
        LORE_PACK_INDEX_FILE,
        LORE_PACK_CONTENT_FILE,
        THIRD_PARTY_LICENSES_INDEX,
        DOTNET_LICENSE,
        DOTNET_NOTICES,
    )
    + tuple(f"{APP_DIR}/{filename}" for filename in REQUIRED_APP_FILES)
)
DEFAULT_PACKAGE_NAME = "OnslaughtCareerEditor.WinUI-local-probe-win-x64.zip"
HOME_NAVIGATION_FILTER = (
    "FullyQualifiedName~WinUiHomeNavigationSmokeTests"
    "&FullyQualifiedName!~Home_NewcomerHierarchy_CapturesFirstRunReadyAndCompactWithoutNavigation"
)
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
    "local-rom-input",
    "local-saves",
    "media",
    "mcps",
    "save-attempts",
}
ZIP_PAYLOAD_DENY_SUFFIXES = (
    ".aya",
    ".bea",
    ".bes",
    ".bik",
    ".bin",
    ".bytes",
    ".db",
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
    ".obj",
    ".ogg",
    ".pem",
    ".png",
    ".jpg",
    ".jpeg",
    ".raw",
    ".sqlite",
    ".trx",
    ".vid",
    ".wav",
    ".webp",
    ".zip",
)
ZIP_PACKAGE_ALLOWED_IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")
ZIP_PACKAGE_ALLOWED_IMAGE_PREFIXES = (
    f"{APP_DIR}/microsoft.ui.xaml/assets/",
    f"{APP_DIR}/libvlc/",
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
        path.relative_to(ARTIFACTS_ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"Refusing to remove path outside .artifacts/: {path}") from exc
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
            'set "LORE_BOOK=%~dp0lore-book\\BOOK.md"',
            'set "LORE_PACK_INDEX=%~dp0lore-pack\\onslaught-lore.v1.index.json"',
            'set "LORE_PACK_CONTENT=%~dp0lore-pack\\onslaught-lore.v1.jsonl"',
            'if not exist "%APP_EXE%" (',
            "  echo Onslaught Toolkit app payload is missing:",
            '  echo   "%APP_EXE%"',
            "  pause",
            "  exit /b 1",
            ")",
            'if not exist "%LORE_BOOK%" (',
            "  echo Onslaught Toolkit Lore files are missing:",
            '  echo   "%LORE_BOOK%"',
            "  echo Extract the full ZIP and keep the top-level folders together.",
            "  pause",
            "  exit /b 1",
            ")",
            'if not exist "%LORE_PACK_INDEX%" (',
            "  echo Onslaught Toolkit Lore pack is missing:",
            '  echo   "%LORE_PACK_INDEX%"',
            "  echo Extract the full ZIP and keep the top-level folders together.",
            "  pause",
            "  exit /b 1",
            ")",
            'if not exist "%LORE_PACK_CONTENT%" (',
            "  echo Onslaught Toolkit Lore pack content is missing:",
            '  echo   "%LORE_PACK_CONTENT%"',
            "  echo Extract the full ZIP and keep the top-level folders together.",
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


def published_nuget_packages(publish_dir: Path) -> dict[str, str]:
    deps_path = publish_dir / "OnslaughtCareerEditor.WinUI.deps.json"
    if not deps_path.is_file():
        raise ValueError(f"{relative(deps_path)} is missing.")

    data = json.loads(deps_path.read_text(encoding="utf-8"))
    packages: dict[str, str] = {}
    for key, row in data.get("libraries", {}).items():
        if row.get("type") != "package" or "/" not in key:
            continue
        package_id, version = key.rsplit("/", 1)
        packages[package_id.lower()] = version

    # VideoLAN's native package contributes through MSBuild rather than the
    # deps.json library table. It is part of the release only when the managed
    # LibVLC wrapper is present in the published graph.
    if "libvlcsharp" in packages:
        direct_refs = winui_third_party_notices.parse_direct_package_refs(PROJECT)
        native_version = direct_refs.get("videolan.libvlc.windows")
        if not native_version:
            raise ValueError("LibVLCSharp is published but VideoLAN.LibVLC.Windows is not pinned by the WinUI project.")
        packages["videolan.libvlc.windows"] = native_version

    return dict(sorted(packages.items()))


def package_license_files(package_root: Path) -> list[Path]:
    return sorted(
        path
        for path in package_root.rglob("*")
        if path.is_file() and PACKAGE_LICENSE_FILE_REGEX.fullmatch(path.name)
    )


def normalize_license_expression(package_id: str, license_signal: str) -> str | None:
    override = PACKAGE_LICENSE_OVERRIDES.get(package_id)
    if override:
        return override
    lowered = license_signal.lower()
    for expression in LICENSE_TEMPLATES:
        if expression.lower() in lowered:
            return expression
    return None


def safe_package_directory_name(package_id: str, version: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", f"{package_id}-{version}")


def find_dotnet_distribution_root() -> Path | None:
    candidates: list[Path] = []
    env_root = os.environ.get("DOTNET_ROOT")
    if env_root:
        candidates.append(Path(env_root))
    dotnet_exe = shutil.which("dotnet")
    if dotnet_exe:
        candidates.append(Path(dotnet_exe).resolve().parent)
    for candidate in candidates:
        if (candidate / "LICENSE.txt").is_file() and (candidate / "ThirdPartyNotices.txt").is_file():
            return candidate
    return None


def copy_third_party_licenses(publish_dir: Path, bundle_dir: Path) -> CheckResult:
    destination_root = bundle_dir / THIRD_PARTY_LICENSES_DIR
    if destination_root.exists():
        shutil.rmtree(destination_root)
    destination_root.mkdir(parents=True)

    dotnet_root = find_dotnet_distribution_root()
    if dotnet_root is None:
        return CheckResult("bundle_third_party_licenses", "FAIL", "The .NET distribution license/notice files could not be located.")
    shutil.copy2(dotnet_root / "LICENSE.txt", bundle_dir / DOTNET_LICENSE)
    shutil.copy2(dotnet_root / "ThirdPartyNotices.txt", bundle_dir / DOTNET_NOTICES)

    try:
        packages = published_nuget_packages(publish_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return CheckResult("bundle_third_party_licenses", "FAIL", str(exc))

    package_root = winui_third_party_notices.global_packages_root()
    rows: list[tuple[str, str, str, str, list[str]]] = []
    metadata_by_package: dict[str, dict[str, str]] = {}
    for package_id, version in packages.items():
        source_root = package_root / package_id / version
        if not source_root.is_dir():
            return CheckResult(
                "bundle_third_party_licenses",
                "FAIL",
                f"Restored NuGet package is missing for {package_id} {version}.",
            )
        metadata = winui_third_party_notices.read_nuspec_metadata(package_id, version)
        if not metadata:
            return CheckResult(
                "bundle_third_party_licenses",
                "FAIL",
                f"NuGet license metadata is missing for {package_id} {version}.",
            )
        metadata_by_package[package_id] = metadata

        package_destination = destination_root / "packages" / safe_package_directory_name(package_id, version)
        included_files: list[str] = []
        for source in package_license_files(source_root):
            target = package_destination / source.relative_to(source_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            included_files.append(target.relative_to(destination_root).as_posix())

        if not included_files:
            expression = normalize_license_expression(package_id, metadata["license_signal"])
            template = LICENSE_TEMPLATES.get(expression or "")
            if template is None or not template.is_file():
                return CheckResult(
                    "bundle_third_party_licenses",
                    "FAIL",
                    f"No package-provided or reviewed standard license text covers {package_id} {version} ({metadata['license_signal']}).",
                )
            package_destination.mkdir(parents=True, exist_ok=True)
            target = package_destination / "LICENSE.txt"
            content = template.read_text(encoding="utf-8")
            if "{copyright}" in content:
                copyright_notice = PACKAGE_COPYRIGHT_OVERRIDES.get(package_id, metadata["copyright"])
                if not copyright_notice:
                    return CheckResult(
                        "bundle_third_party_licenses",
                        "FAIL",
                        f"Copyright metadata is missing for templated license package {package_id} {version}.",
                    )
                content = content.replace("{copyright}", copyright_notice)
            target.write_text(content, encoding="utf-8", newline="\n")
            included_files.append(target.relative_to(destination_root).as_posix())

        source_url = metadata["repository_url"] or metadata["project_url"]
        rows.append(
            (
                winui_third_party_notices.display_id(package_id),
                version,
                metadata["license_signal"],
                source_url,
                included_files,
            )
        )

    libvlc_lines: list[str] = []
    wrapper_version = packages.get("libvlcsharp")
    native_version = packages.get("videolan.libvlc.windows")
    if wrapper_version and native_version:
        wrapper_metadata = metadata_by_package["libvlcsharp"]
        wrapper_source = wrapper_metadata["repository_url"] or wrapper_metadata["project_url"]
        wrapper_commit = wrapper_metadata["repository_commit"]
        wrapper_source_at_version = f"{wrapper_source}/-/tree/{wrapper_commit}" if wrapper_commit else wrapper_source
        vlc_source_version = ".".join(native_version.split(".")[:3])
        libvlc_lines = [
            "LibVLC replacement and source",
            "-----------------------------",
            "",
            "LibVLCSharp and VideoLAN.LibVLC.Windows are LGPL-2.1-or-later components",
            "distributed as separate dynamically loaded files. The Toolkit does not",
            "statically link them or apply installer/signature integrity enforcement.",
            "After closing the Toolkit, a user may replace app\\LibVLCSharp.dll and the",
            "app\\libvlc\\win-x64 directory with interface-compatible modified builds,",
            "then restart the app. Replacement compatibility is the user's responsibility.",
            "",
            "Exact upstream source locations:",
            f"- LibVLCSharp {wrapper_version}: {wrapper_source_at_version}",
            f"- VLC {vlc_source_version} source used by VideoLAN.LibVLC.Windows {native_version}:",
            f"  https://download.videolan.org/pub/videolan/vlc/{vlc_source_version}/vlc-{vlc_source_version}.tar.xz",
            "- Native NuGet packaging source:",
            "  https://code.videolan.org/videolan/libvlc-nuget",
            "",
        ]

    lines = [
        "Onslaught Toolkit - Third-Party Licenses",
        "=========================================",
        "",
        "This directory accompanies the exact self-contained WinUI publish graph.",
        "Package-specific license and notice files are copied from the restored",
        "NuGet packages. Standard license texts are materialized only when a package",
        "declares a recognized SPDX expression without embedding its own file.",
        "",
        ".NET runtime",
        "------------",
        "",
        "The self-contained .NET runtime terms and third-party notices are in:",
        "- DOTNET-LICENSE.txt",
        "- DOTNET-THIRD-PARTY-NOTICES.txt",
        "",
        *libvlc_lines,
        "Published package graph",
        "-----------------------",
        "",
    ]
    for package_id, version, license_signal, source_url, included_files in rows:
        lines.append(f"{package_id} {version}")
        lines.append(f"  Declared license: {license_signal}")
        if source_url:
            lines.append(f"  Source/project: {source_url}")
        for included_file in included_files:
            lines.append(f"  Included terms: {included_file}")
        lines.append("")
    lines.extend(
        [
            "These notices document the package boundary; they are not legal advice,",
            "affiliation, endorsement, or permission for unrelated retail game assets.",
            "",
        ]
    )
    (bundle_dir / THIRD_PARTY_LICENSES_INDEX).write_text("\n".join(lines), encoding="utf-8", newline="\n")

    package_count = len(rows)
    license_file_count = sum(len(row[4]) for row in rows) + 2
    return CheckResult(
        "bundle_third_party_licenses",
        "PASS",
        f"Packaged {license_file_count} license/notice file(s) for .NET and {package_count} published NuGet package(s).",
    )


def keep_only_target_libvlc_runtime(app_dir: Path) -> CheckResult:
    wrapper = app_dir / "LibVLCSharp.dll"
    runtime_root = app_dir / "libvlc"
    if not wrapper.is_file():
        return CheckResult("bundle_libvlc_runtime", "PASS", "No LibVLCSharp payload is present in this synthetic package fixture.")

    target_root = runtime_root / "win-x64"
    required = (target_root / "libvlc.dll", target_root / "libvlccore.dll")
    if any(not path.is_file() for path in required):
        return CheckResult("bundle_libvlc_runtime", "FAIL", "The required win-x64 LibVLC runtime is missing.")

    removed: list[str] = []
    for candidate in sorted(runtime_root.iterdir()):
        if candidate.is_dir() and candidate.name.lower() != "win-x64":
            removed.append(candidate.name)
            shutil.rmtree(candidate)
    return CheckResult(
        "bundle_libvlc_runtime",
        "PASS",
        "Retained the win-x64 LibVLC runtime and removed non-target architecture payloads"
        + (": " + ", ".join(removed) if removed else "."),
    )


def copy_lore_book(bundle_dir: Path) -> CheckResult:
    destination = bundle_dir / LORE_BOOK_DIR
    required_source = LORE_BOOK_SOURCE / "BOOK.md"
    if not required_source.is_file() or required_source.stat().st_size <= 0:
        return CheckResult("lore_book_source", "FAIL", f"{relative(required_source)} is missing or empty.")
    if destination.exists():
        shutil.rmtree(destination)
    try:
        packaged_files = resolve_packaged_lore_entry_files(required_source)
    except ValueError as exc:
        return CheckResult("bundle_lore_book", "FAIL", str(exc))
    for source in sorted(packaged_files):
        destination_path = destination / source.relative_to(LORE_BOOK_SOURCE)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() in {".md", ".txt"}:
            content = source.read_text(encoding="utf-8")
            content = rewrite_packaged_lore_links(source, content, packaged_files)
            destination_path.write_text(content, encoding="utf-8", newline="\n")
        else:
            shutil.copy2(source, destination_path)
    required_destination = destination / "BOOK.md"
    copied_count = sum(1 for path in destination.rglob("*") if path.is_file()) if destination.exists() else 0
    return CheckResult(
        "bundle_lore_book",
        "PASS" if required_destination.is_file() and required_destination.stat().st_size > 0 and copied_count == len(packaged_files) else "FAIL",
        f"{relative(destination)} copied with {copied_count} short entry-point file(s); packaged Lore library content lives in lore-pack/ and deeper source links are rewritten to GitHub."
        if required_destination.is_file() and required_destination.stat().st_size > 0
        else f"{relative(required_destination)} is missing after BOOK.md-linked lore copy.",
    )


def build_lore_pack(bundle_dir: Path) -> CheckResult:
    destination = bundle_dir / LORE_PACK_DIR
    if destination.exists():
        shutil.rmtree(destination)
    try:
        report = winui_lore_pack_builder.build_lore_pack(ROOT, destination, use_git=True)
    except Exception as exc:
        return CheckResult("bundle_lore_pack", "FAIL", f"Lore pack build failed: {exc}")
    document_count = report.get("documentCount", 0)
    return CheckResult(
        "bundle_lore_pack",
        "PASS" if (destination / winui_lore_pack_builder.INDEX_FILE_NAME).is_file() and (destination / winui_lore_pack_builder.CONTENT_FILE_NAME).is_file() else "FAIL",
        f"{relative(destination)} generated with {document_count} public-safe offline Lore document(s).",
    )


def resolve_packaged_lore_entry_files(book_path: Path) -> set[Path]:
    lore_root = LORE_BOOK_SOURCE.resolve()
    packaged_files: set[Path] = {book_path.resolve()}
    for match in LORE_BOOK_LINK_REGEX.finditer(book_path.read_text(encoding="utf-8")):
        target = unquote(match.group("target").strip()).split("#", 1)[0]
        if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            continue
        candidate = (LORE_BOOK_SOURCE / target.replace("\\", "/")).resolve()
        try:
            candidate.relative_to(lore_root)
        except ValueError:
            continue
        if not candidate.is_file():
            raise ValueError(f"missing local BOOK.md link: {target}")
    return packaged_files


def rewrite_packaged_lore_links(source: Path, content: str, packaged_files: set[Path]) -> str:
    packaged_resolved = {path.resolve() for path in packaged_files}
    lore_root = LORE_BOOK_SOURCE.resolve()
    repo_root = ROOT.resolve()

    def replace(match: re.Match[str]) -> str:
        target = match.group("target").strip()
        path_part, anchor = split_link_target(target)
        if not path_part or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", path_part):
            return match.group(0)

        candidate = resolve_source_link_candidate(source, path_part)
        resolved = resolve_existing_repo_link(candidate)

        if resolved is not None and is_relative_to(resolved, lore_root) and resolved in packaged_resolved:
            return match.group(0)

        github_url = build_github_source_url(candidate, path_part, anchor, resolved, repo_root)
        if github_url is None:
            return match.group(0)

        return f"{match.group('prefix')}{github_url}{match.group('suffix')}"

    return LORE_BOOK_MARKDOWN_LINK_REGEX.sub(replace, content)


def resolve_source_link_candidate(source: Path, path_part: str) -> Path:
    normalized = path_part.replace("\\", "/")
    if normalized.startswith("/"):
        return (ROOT / normalized.lstrip("/")).resolve()
    return (source.parent / normalized).resolve()


def split_link_target(target: str) -> tuple[str, str]:
    path_part, separator, anchor = target.partition("#")
    return unquote(path_part), f"#{anchor}" if separator else ""


def resolve_existing_repo_link(candidate: Path) -> Path | None:
    if candidate.is_file():
        return candidate.resolve()
    if candidate.is_dir():
        for filename in ("_index.md", "README.md", "index.md"):
            index_path = candidate / filename
            if index_path.is_file():
                return index_path.resolve()
        return None
    if candidate.suffix:
        return None
    for suffix in (".md", ".html", ".htm"):
        suffixed = Path(f"{candidate}{suffix}")
        if suffixed.is_file():
            return suffixed.resolve()
    return None


def build_github_source_url(candidate: Path, path_part: str, anchor: str, resolved: Path | None, repo_root: Path) -> str | None:
    if resolved is not None:
        if not is_relative_to(resolved, repo_root):
            return None
        repo_relative = resolved.relative_to(repo_root).as_posix()
        return f"{GITHUB_SOURCE_BLOB_BASE}/{quote(repo_relative, safe='/')}{anchor}"
    if is_relative_to(candidate, repo_root):
        try:
            repo_relative = candidate.relative_to(repo_root).as_posix()
        except ValueError:
            repo_relative = path_part.strip("/")
        query = quote(repo_relative or path_part, safe="")
        return f"{GITHUB_SOURCE_SEARCH_BASE}?q={query}&type=code"
    return None


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def stage_portable_bundle(publish_dir: Path, bundle_dir: Path) -> list[CheckResult]:
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    app_dir = bundle_dir / APP_DIR
    shutil.copytree(publish_dir, app_dir)
    checks = [
        keep_only_target_libvlc_runtime(app_dir),
        write_launcher(bundle_dir),
        copy_zip_readme(bundle_dir),
        copy_license(bundle_dir),
        copy_third_party_licenses(publish_dir, bundle_dir),
        copy_lore_book(bundle_dir),
        build_lore_pack(bundle_dir),
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
    allowed_top_levels = set(REQUIRED_ROOT_FILES) | {APP_DIR, LORE_BOOK_DIR, LORE_PACK_DIR, THIRD_PARTY_LICENSES_DIR}
    unexpected_top_levels = [name for name in top_levels if name not in allowed_top_levels]
    root_executables = [name for name in root_files if name.lower().endswith(".exe")]
    root_dlls = [name for name in root_files if name.lower().endswith(".dll")]
    checks.append(
        CheckResult(
            f"{prefix}_friendly_root_shape",
            "PASS" if not unexpected_top_levels else "FAIL",
            "Top-level ZIP/folder entries are limited to launcher, readme, licenses, lore-book/, lore-pack/, and app/."
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
        if lower_name.endswith(ZIP_PACKAGE_ALLOWED_IMAGE_SUFFIXES) and any(
            lower_name.startswith(allowed_prefix) for allowed_prefix in ZIP_PACKAGE_ALLOWED_IMAGE_PREFIXES
        ):
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


def inspect_explorer_path_safety_names(names: set[str], prefix: str, default_extract_folder_name: str | None = None) -> list[CheckResult]:
    files = [name.rstrip("/") for name in names if name.rstrip("/") and not name.endswith("/")]
    measured_names = list(files)
    if default_extract_folder_name:
        measured_names.extend(f"{default_extract_folder_name}/{name}" for name in files)
    over_limit = sorted((name for name in measured_names if len(name) > WINDOWS_EXPLORER_SAFE_ENTRY_LENGTH), key=len, reverse=True)
    max_length = max((len(name) for name in measured_names), default=0)
    return [
        CheckResult(
            f"{prefix}_explorer_path_safety",
            "PASS" if not over_limit else "FAIL",
            f"Longest packaged Explorer-relative path is {max_length} character(s), within the {WINDOWS_EXPLORER_SAFE_ENTRY_LENGTH}-character Explorer-safe ZIP entry budget."
            if not over_limit
            else f"ZIP/folder entries exceed the {WINDOWS_EXPLORER_SAFE_ENTRY_LENGTH}-character Explorer-safe ZIP entry budget after default extraction-folder accounting: "
            + ", ".join(over_limit[:8]),
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
        checks.extend(inspect_explorer_path_safety_names(names, prefix))
        checks.extend(inspect_packaged_lore_link_safety(root, prefix))
        checks.extend(inspect_packaged_lore_copy_truth(read_folder_lore_texts(root), prefix))
        checks.extend(inspect_lore_pack_folder(root, prefix))
        checks.extend(inspect_raw_deep_lore_book_leakage(names, prefix))
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
        lore_texts = read_zip_lore_texts(package)
        lore_pack_texts = read_zip_lore_pack_texts(package)
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
    checks.extend(inspect_explorer_path_safety_names(names, "zip", default_extract_folder_name=zip_path.stem))
    checks.extend(inspect_packaged_lore_link_safety_archive(names, lore_texts, "zip"))
    checks.extend(inspect_packaged_lore_copy_truth(lore_texts, "zip"))
    checks.extend(inspect_lore_pack_texts(lore_pack_texts, "zip"))
    checks.extend(inspect_raw_deep_lore_book_leakage(names, "zip"))
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


def read_zip_lore_texts(package: zipfile.ZipFile) -> dict[str, str]:
    texts: dict[str, str] = {}
    for name in package.namelist():
        normalized = name.replace("\\", "/")
        if not normalized.startswith(f"{LORE_BOOK_DIR}/") or normalized.endswith("/"):
            continue
        suffix = Path(normalized).suffix.lower()
        if suffix not in {".md", ".txt"}:
            continue
        try:
            texts[normalized] = package.read(name).decode("utf-8", errors="replace")
        except KeyError:
            continue
    return texts


def read_zip_lore_pack_texts(package: zipfile.ZipFile) -> dict[str, str]:
    texts: dict[str, str] = {}
    for name in package.namelist():
        normalized = name.replace("\\", "/")
        if normalized not in {LORE_PACK_INDEX_FILE, LORE_PACK_CONTENT_FILE}:
            continue
        try:
            texts[normalized] = package.read(name).decode("utf-8", errors="replace")
        except KeyError:
            continue
    return texts


def normalize_pack_relative_path(path: str) -> str | None:
    parts: list[str] = []
    for part in PurePosixPath(path.replace("\\", "/")).parts:
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
                continue
            return None
        parts.append(part)
    return "/".join(parts)


def resolve_pack_link_candidate(source_relative_path: str, target: str, available_paths: set[str]) -> str | None:
    normalized_target = target.replace("\\", "/")
    if normalized_target.startswith("/"):
        candidate = normalize_pack_relative_path(normalized_target.lstrip("/"))
    else:
        source_parent = PurePosixPath(source_relative_path).parent.as_posix()
        prefix = "" if source_parent == "." else f"{source_parent}/"
        candidate = normalize_pack_relative_path(f"{prefix}{normalized_target}")
    if candidate is None:
        return None

    candidate_without_suffix = str(PurePosixPath(candidate).with_suffix("")) if PurePosixPath(candidate).suffix else candidate
    candidates = (
        candidate,
        f"{candidate}.md",
        f"{candidate}.html",
        f"{candidate}/_index.md",
        f"{candidate}/README.md",
        f"{candidate}/index.md",
        f"{candidate_without_suffix}.md",
        f"{candidate_without_suffix}.html",
        f"{candidate_without_suffix}.htm",
    )
    for item in candidates:
        normalized = normalize_pack_relative_path(item)
        if normalized is not None and normalized.lower() in available_paths:
            return normalized
    return None


def read_folder_lore_texts(root: Path) -> dict[str, str]:
    lore_root = root / LORE_BOOK_DIR
    if not lore_root.is_dir():
        return {}
    texts: dict[str, str] = {}
    for source in sorted(lore_root.rglob("*")):
        if not source.is_file() or source.suffix.lower() not in {".md", ".txt"}:
            continue
        texts[source.relative_to(root).as_posix()] = source.read_text(encoding="utf-8", errors="replace")
    return texts


def inspect_lore_pack_folder(root: Path, prefix: str) -> list[CheckResult]:
    pack_root = root / LORE_PACK_DIR
    if not pack_root.is_dir():
        return [CheckResult(f"{prefix}_lore_pack", "FAIL", f"{relative(pack_root)} is missing.")]
    texts: dict[str, str] = {}
    for relative_name in (LORE_PACK_INDEX_FILE, LORE_PACK_CONTENT_FILE):
        path = root / relative_name
        if path.is_file():
            texts[relative_name] = path.read_text(encoding="utf-8", errors="replace")
    return inspect_lore_pack_texts(texts, prefix)


def inspect_lore_pack_texts(pack_texts: dict[str, str], prefix: str) -> list[CheckResult]:
    if LORE_PACK_INDEX_FILE not in pack_texts or LORE_PACK_CONTENT_FILE not in pack_texts:
        return [
            CheckResult(
                f"{prefix}_lore_pack",
                "FAIL",
                "Lore pack index/content files are missing.",
            )
        ]

    findings: list[str] = []
    try:
        index = json.loads(pack_texts[LORE_PACK_INDEX_FILE])
        if index.get("schema") != winui_lore_pack_builder.SCHEMA:
            findings.append("schema mismatch")
        documents = index.get("documents")
        if not isinstance(documents, list):
            documents = []
            findings.append("index documents are missing or invalid")
        if index.get("documentCount") != len(documents):
            findings.append("documentCount does not match index row count")

        expected_rows: dict[str, dict[str, object]] = {}
        expected_row_keys: set[str] = set()
        indexed_relative_paths: set[str] = set()
        for item_number, item in enumerate(documents, start=1):
            if not isinstance(item, dict):
                findings.append(f"index row {item_number} is invalid")
                continue

            doc_id = validate_probe_document_id(item.get("id"), f"index row {item_number}", findings)
            if doc_id is None:
                continue

            doc_key = doc_id.lower()
            if doc_key in expected_row_keys:
                findings.append(f"index row {item_number} duplicates id")
                continue

            relative_path = validate_probe_relative_path(item.get("relativePath"), f"index row {item_number}", findings)
            if relative_path is None:
                continue

            relative_key = relative_path.lower()
            if relative_key in indexed_relative_paths:
                findings.append(f"index row {item_number} duplicates relativePath")
                continue

            expected_row_keys.add(doc_key)
            indexed_relative_paths.add(relative_key)
            expected_row = dict(item)
            expected_row["relativePath"] = relative_path
            expected_rows[doc_key] = expected_row

        available_paths = set(indexed_relative_paths)
        seen_rows: set[str] = set()
        for line_number, line in enumerate(pack_texts[LORE_PACK_CONTENT_FILE].splitlines(), start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                findings.append(f"row {line_number} is invalid")
                continue
            allowed_keys = {"id", "relativePath", "title", "sha256", "byteLength", "content"}
            extra_keys = sorted(set(row) - allowed_keys)
            if extra_keys:
                findings.append(f"row {line_number} has unexpected keys")
                continue
            doc_id = validate_probe_document_id(row.get("id"), f"row {line_number}", findings)
            if doc_id is None:
                continue
            doc_key = doc_id.lower()
            if doc_key not in expected_rows:
                findings.append(f"row {line_number} has unknown id")
                continue
            if doc_key in seen_rows:
                findings.append(f"row {line_number} duplicates id")
                continue
            content = row.get("content")
            if not isinstance(content, str):
                findings.append(f"row {line_number} is missing text content")
                continue
            relative_path = validate_probe_relative_path(row.get("relativePath"), f"row {line_number}", findings)
            if relative_path is None:
                continue
            content_byte_length = len(content.encode("utf-8"))
            expected_row = expected_rows[doc_key]
            if row.get("byteLength") != content_byte_length or expected_row.get("byteLength") != content_byte_length:
                findings.append(f"row {line_number} byteLength mismatch")
                continue
            if relative_path != expected_row.get("relativePath"):
                findings.append(f"row {line_number} relativePath mismatch")
                continue
            if has_payload_like_lore_pack_text(relative_path) or has_payload_like_lore_pack_text(content):
                findings.append(f"row {line_number} contains payload-like/local/private text")
                continue
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if digest != row.get("sha256") or digest != expected_row.get("sha256"):
                findings.append(f"row {line_number} hash mismatch")
                continue
            unresolved_links: list[str] = []
            for match in LORE_BOOK_MARKDOWN_LINK_REGEX.finditer(content):
                target = match.group("target").strip()
                path_part, _ = split_link_target(target)
                if not path_part or path_part.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", path_part):
                    continue
                if resolve_pack_link_candidate(relative_path, path_part, available_paths) is None:
                    unresolved_links.append(target)
            if unresolved_links:
                findings.append(f"row {line_number} has unresolved packed links")
                continue
            seen_rows.add(doc_key)
        missing_rows = sorted(set(expected_rows) - seen_rows)
        if missing_rows:
            findings.append(f"missing content rows: {len(missing_rows)}")
    except Exception as exc:
        findings.append("Lore pack validation raised an unexpected error")

    return [
        CheckResult(
            f"{prefix}_lore_pack",
            "PASS" if not findings else "FAIL",
            "Lore pack index/content schema, hashes, and content safety passed."
            if not findings
            else "Lore pack validation failed: " + "; ".join(findings[:8]),
        )
    ]


def validate_probe_document_id(value: object, context: str, findings: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip() or value.strip() != value or not LORE_PACK_DOCUMENT_ID_REGEX.fullmatch(value):
        findings.append(f"{context} has invalid id")
        return None
    return value


def validate_probe_relative_path(value: object, context: str, findings: list[str]) -> str | None:
    try:
        return winui_lore_pack_builder.validate_lore_pack_relative_path(value)
    except ValueError:
        findings.append(f"{context} has invalid relativePath")
        return None


def has_payload_like_lore_pack_text(value: str) -> bool:
    lower = value.lower()
    if any(lower.endswith(suffix) for suffix in ZIP_PAYLOAD_DENY_SUFFIXES):
        return True
    if any(pattern.search(value) for pattern in LORE_PACK_FORBIDDEN_TEXT_PATTERNS):
        return True
    return False


def inspect_raw_deep_lore_book_leakage(names: set[str], prefix: str) -> list[CheckResult]:
    has_pack = LORE_PACK_INDEX_FILE in names and LORE_PACK_CONTENT_FILE in names
    if not has_pack:
        return []
    allowed_lore_book = {
        f"{LORE_BOOK_DIR}/BOOK.md",
    }
    leaked = sorted(
        name for name in names
        if name.startswith(f"{LORE_BOOK_DIR}/") and
        name.rstrip("/") not in allowed_lore_book
    )
    return [
        CheckResult(
            f"{prefix}_raw_deep_lore_book_leakage",
            "PASS" if not leaked else "FAIL",
            "Raw deep lore-book mirror entries are not packaged beside the generated Lore pack."
            if not leaked
            else "Raw deep lore-book entries leaked into package: " + ", ".join(leaked[:8]),
        )
    ]


def inspect_packaged_lore_copy_truth(lore_texts: dict[str, str], prefix: str) -> list[CheckResult]:
    if not lore_texts:
        return []
    findings: list[str] = []
    for source_name, content in sorted(lore_texts.items()):
        for claim in PACKAGED_LORE_FORBIDDEN_CLAIMS:
            if claim in content:
                findings.append(f"{source_name}: {claim}")
    return [
        CheckResult(
            f"{prefix}_lore_copy_truth",
            "PASS" if not findings else "FAIL",
            "Packaged Lore copy accurately distinguishes offline chapters from source links that may open online."
            if not findings
            else "Packaged Lore copy contains stale all-in-app claims: " + ", ".join(findings[:8]),
        )
    ]


def inspect_packaged_lore_link_safety(root: Path, prefix: str) -> list[CheckResult]:
    lore_root = root / LORE_BOOK_DIR
    if not lore_root.is_dir():
        return []
    root_resolved = root.resolve()
    findings: list[str] = []
    for source in sorted(lore_root.rglob("*")):
        if not source.is_file() or source.suffix.lower() not in {".md", ".txt"}:
            continue
        content = source.read_text(encoding="utf-8", errors="replace")
        source_relative = source.relative_to(root).as_posix()
        for match in LORE_BOOK_MARKDOWN_LINK_REGEX.finditer(content):
            target = match.group("target").strip()
            path_part, _ = split_link_target(target)
            if not path_part or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", path_part):
                continue
            candidate = resolve_packaged_link_candidate(root, source, path_part)
            resolved = resolve_existing_repo_link(candidate)
            if resolved is None or not is_relative_to(resolved, root_resolved):
                findings.append(f"{source_relative} -> {target}")
    return [
        CheckResult(
            f"{prefix}_lore_link_safety",
            "PASS" if not findings else "FAIL",
            "Packaged Lore markdown has no dead local links; unbundled source links must be externalized."
            if not findings
            else "Packaged Lore markdown has dead local links: " + ", ".join(findings[:8]),
        )
    ]


def inspect_packaged_lore_link_safety_archive(names: set[str], lore_texts: dict[str, str], prefix: str) -> list[CheckResult]:
    if not any(name.rstrip("/").startswith(f"{LORE_BOOK_DIR}/") for name in names):
        return []
    normalized_names = {name.rstrip("/").replace("\\", "/") for name in names if name.rstrip("/")}
    findings: list[str] = []
    for source_name, content in sorted(lore_texts.items()):
        for match in LORE_BOOK_MARKDOWN_LINK_REGEX.finditer(content):
            target = match.group("target").strip()
            path_part, _ = split_link_target(target)
            if not path_part or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", path_part):
                continue
            candidate = resolve_packaged_archive_link_candidate(source_name, path_part)
            if resolve_existing_archive_link(candidate, normalized_names) is None:
                findings.append(f"{source_name} -> {target}")
    return [
        CheckResult(
            f"{prefix}_lore_link_safety",
            "PASS" if not findings else "FAIL",
            "Packaged Lore markdown has no dead local links inside the ZIP; unbundled source links must be externalized."
            if not findings
            else "Packaged Lore markdown has dead local ZIP links: " + ", ".join(findings[:8]),
        )
    ]


def resolve_packaged_link_candidate(package_root: Path, source: Path, path_part: str) -> Path:
    normalized = path_part.replace("\\", "/")
    if normalized.startswith("/"):
        return (package_root / normalized.lstrip("/")).resolve()
    return (source.parent / normalized).resolve()


def resolve_packaged_archive_link_candidate(source_name: str, path_part: str) -> str:
    normalized = path_part.replace("\\", "/")
    if normalized.startswith("/"):
        return posixpath.normpath(normalized.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(source_name), normalized))


def resolve_existing_archive_link(candidate: str, names: set[str]) -> str | None:
    candidate = candidate.rstrip("/")
    if candidate in names:
        return candidate
    for index_name in ("_index.md", "README.md", "index.md"):
        indexed = f"{candidate}/{index_name}"
        if indexed in names:
            return indexed
    if not Path(candidate).suffix:
        for suffix in (".md", ".html", ".htm"):
            suffixed = f"{candidate}{suffix}"
            if suffixed in names:
                return suffixed
    return None


def extract_zip(zip_path: Path, extract_dir: Path) -> tuple[int, str]:
    try:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as package:
            extract_root = extract_dir.resolve()
            for member in package.infolist():
                member_name = member.filename.replace("\\", "/")
                member_name_without_trailing_slash = member_name.rstrip("/")
                raw_parts = member_name_without_trailing_slash.split("/") if member_name_without_trailing_slash else []
                member_path = PurePosixPath(member_name)
                if (
                    not member_name_without_trailing_slash
                    or member_path.is_absolute()
                    or any(part in ("", ".", "..") for part in raw_parts)
                    or re.match(r"^[A-Za-z]:", member_name)
                ):
                    raise ValueError("unsafe ZIP member path")
                destination = (extract_root / Path(*raw_parts)).resolve()
                if destination != extract_root and extract_root not in destination.parents:
                    raise ValueError("unsafe ZIP member path")
            package.extractall(extract_root)
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
        "releaseClaim": "Disposable friendly portable ZIP package, Explorer-safe entry paths, extraction, extracted app launch smoke, representative extracted-app Home navigation, extracted Lore smoke, and representative Media smoke when requested are proven only if status is pass; signing/MSIX/installer/SmartScreen readiness remain separate gates.",
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
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT, help="ignored output root under .artifacts/")
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
        out_root.relative_to(ARTIFACTS_ROOT.resolve())
    except ValueError:
        print(f"Refusing to write ZIP probe output outside .artifacts/: {out_root}")
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
