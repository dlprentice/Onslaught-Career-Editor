#!/usr/bin/env python3
"""Assemble and inspect a disposable unsigned WinUI MSIX candidate.

This probe intentionally keeps all generated package material under
``subagents/``. It does not change the WinUI project packaging settings, does
not sign the package, and does not install it.
"""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import subprocess
import sys
import zlib
import zipfile
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "OnslaughtCareerEditor.WinUI" / "OnslaughtCareerEditor.WinUI.csproj"
DEFAULT_OUT_ROOT = ROOT / "subagents" / "winui-msix-candidate" / "current"
WINDOWS_KITS_BIN = Path("C:/Program Files (x86)/Windows Kits/10/bin")

APP_EXE = "OnslaughtCareerEditor.WinUI.exe"
APP_PRI = "OnslaughtCareerEditor.WinUI.pri"
NOTICES = "THIRD_PARTY_NOTICES.md"


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
    subagents_root = (ROOT / "subagents").resolve()
    try:
        path.relative_to(subagents_root)
    except ValueError as exc:
        raise RuntimeError(f"Refusing to remove path outside subagents/: {path}") from exc

    if path.exists():
        shutil.rmtree(path)


def find_windows_sdk_tool(tool_name: str) -> Path | None:
    path_tool = shutil.which(tool_name)
    if path_tool:
        return Path(path_tool)

    if not WINDOWS_KITS_BIN.is_dir():
        return None

    candidates = sorted(
        WINDOWS_KITS_BIN.glob(f"*/x64/{tool_name}"),
        key=lambda path: path.parts[-3],
        reverse=True,
    )
    return candidates[0] if candidates else None


def run_publish(out_dir: Path) -> tuple[int, str]:
    command = [
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
        str(out_dir),
        "--nologo",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode, completed.stdout


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def write_png(path: Path, width: int, height: int, rgba: tuple[int, int, int, int]) -> None:
    """Write a small solid-color PNG without external dependencies."""

    r, g, b, a = rgba
    row = b"\x00" + bytes((r, g, b, a)) * width
    raw = row * height
    payload = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            png_chunk(b"IDAT", zlib.compress(raw, level=9)),
            png_chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(payload)


def write_manifest(package_root: Path) -> None:
    manifest = """<?xml version="1.0" encoding="utf-8"?>
<Package
  xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
  xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
  xmlns:uap10="http://schemas.microsoft.com/appx/manifest/uap/windows10/10"
  xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
  IgnorableNamespaces="uap uap10 rescap">
  <Identity
    Name="OnslaughtCareerEditor.WinUI.LocalProbe"
    Publisher="CN=Onslaught Career Editor Local Probe"
    Version="0.0.1.0"
    ProcessorArchitecture="x64" />
  <Properties>
    <DisplayName>Onslaught Career Editor</DisplayName>
    <PublisherDisplayName>Onslaught Career Editor Local Probe</PublisherDisplayName>
    <Logo>Assets\\StoreLogo.png</Logo>
  </Properties>
  <Resources>
    <Resource Language="en-us" />
  </Resources>
  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.19041.0" MaxVersionTested="10.0.26100.0" />
  </Dependencies>
  <Capabilities>
    <rescap:Capability Name="runFullTrust" />
  </Capabilities>
  <Applications>
    <Application
      Id="App"
      Executable="OnslaughtCareerEditor.WinUI.exe"
      EntryPoint="Windows.FullTrustApplication"
      uap10:RuntimeBehavior="packagedClassicApp"
      uap10:TrustLevel="mediumIL">
      <uap:VisualElements
        DisplayName="Onslaught Career Editor"
        Description="Battle Engine Aquila save, media, lore, and patch workbench."
        BackgroundColor="#243447"
        Square150x150Logo="Assets\\Square150x150Logo.png"
        Square44x44Logo="Assets\\Square44x44Logo.png" />
    </Application>
  </Applications>
</Package>
"""
    (package_root / "AppxManifest.xml").write_text(manifest, encoding="utf-8", newline="\r\n")


def stage_package_root(publish_dir: Path, package_root: Path) -> list[CheckResult]:
    checks: list[CheckResult] = []
    shutil.copytree(publish_dir, package_root)

    assets = package_root / "Assets"
    assets.mkdir(parents=True, exist_ok=True)
    write_png(assets / "Square150x150Logo.png", 150, 150, (36, 52, 71, 255))
    write_png(assets / "Square44x44Logo.png", 44, 44, (216, 154, 70, 255))
    write_png(assets / "StoreLogo.png", 50, 50, (78, 101, 128, 255))
    write_manifest(package_root)

    for filename in (APP_EXE, APP_PRI, NOTICES, "AppxManifest.xml"):
        path = package_root / filename
        if path.is_file() and path.stat().st_size > 0:
            checks.append(CheckResult(filename, "PASS", f"{relative(path)} exists and is non-empty."))
        else:
            checks.append(CheckResult(filename, "FAIL", f"{relative(path)} is missing or empty."))

    return checks


def run_makeappx(package_root: Path, msix_path: Path, makeappx: Path) -> tuple[int, str]:
    command = [
        str(makeappx),
        "pack",
        "/d",
        str(package_root),
        "/p",
        str(msix_path),
        "/o",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode, completed.stdout


def inspect_msix(msix_path: Path) -> list[CheckResult]:
    checks: list[CheckResult] = []
    if not msix_path.is_file() or msix_path.stat().st_size <= 0:
        return [CheckResult("msix_file", "FAIL", f"{relative(msix_path)} was not created.")]

    checks.append(
        CheckResult(
            "msix_file",
            "PASS",
            f"{relative(msix_path)} exists and is non-empty ({msix_path.stat().st_size} bytes).",
        )
    )

    with zipfile.ZipFile(msix_path) as package:
        names = set(package.namelist())

    for filename in ("AppxManifest.xml", APP_EXE, APP_PRI, NOTICES):
        if filename in names:
            checks.append(CheckResult(f"contains_{filename}", "PASS", f"Package contains {filename}."))
        else:
            checks.append(CheckResult(f"contains_{filename}", "FAIL", f"Package does not contain {filename}."))

    if "AppxSignature.p7x" in names:
        checks.append(CheckResult("unsigned_posture", "FAIL", "Package unexpectedly contains AppxSignature.p7x."))
    else:
        checks.append(
            CheckResult(
                "unsigned_posture",
                "PASS",
                "Package is intentionally unsigned; install/signing proof remains a separate gate.",
            )
        )

    return checks


def build_report(
    out_root: Path,
    publish_exit: int,
    publish_output: str,
    stage_checks: list[CheckResult],
    makeappx_path: Path | None,
    makeappx_exit: int | None,
    makeappx_output: str,
    msix_checks: list[CheckResult],
) -> dict[str, object]:
    all_checks = list(stage_checks) + list(msix_checks)
    if makeappx_path is None:
        all_checks.append(CheckResult("makeappx_tool", "FAIL", "makeappx.exe was not found."))
    else:
        all_checks.append(CheckResult("makeappx_tool", "PASS", f"Using {makeappx_path.name} from Windows SDK."))

    failures = [check for check in all_checks if check.status == "FAIL"]
    status = "pass" if publish_exit == 0 and makeappx_exit == 0 and not failures else "blocked"
    return {
        "schema": "winui-msix-candidate-probe.v1",
        "status": status,
        "releaseClaim": "Unsigned disposable MSIX assembly is proven only if status is pass; signing/install/uninstall remain separate release gates.",
        "outputRoot": relative(out_root),
        "publishExitCode": publish_exit,
        "publishOutputTail": "\n".join(publish_output.splitlines()[-20:]),
        "makeappxPath": str(makeappx_path) if makeappx_path is not None else None,
        "makeappxExitCode": makeappx_exit,
        "makeappxOutputTail": "\n".join(makeappx_output.splitlines()[-40:]),
        "checks": [check.__dict__ for check in all_checks],
        "notProven": [
            "Package signing",
            "Certificate trust posture",
            "Install smoke",
            "Launch smoke from installed package identity",
            "Uninstall smoke",
            "SmartScreen/store/distribution posture",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble and inspect a disposable unsigned WinUI MSIX candidate.")
    parser.add_argument("--check", action="store_true", help="run the candidate probe")
    parser.add_argument("--json", action="store_true", help="print JSON report")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT, help="ignored output root under subagents/")
    args = parser.parse_args()

    if not args.check:
        parser.error("expected --check")

    if not PROJECT.is_file():
        print(f"Missing WinUI project: {PROJECT}")
        return 1

    out_root = args.out_root
    if not out_root.is_absolute():
        out_root = ROOT / out_root
    out_root = out_root.resolve()
    try:
        out_root.relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write MSIX probe output outside subagents/: {out_root}")
        return 1

    safe_rmtree(out_root)
    publish_dir = out_root / "publish"
    package_root = out_root / "package"
    msix_path = out_root / "OnslaughtCareerEditor.WinUI.LocalProbe.msix"
    publish_dir.mkdir(parents=True, exist_ok=True)

    publish_exit, publish_output = run_publish(publish_dir)
    stage_checks: list[CheckResult] = []
    msix_checks: list[CheckResult] = []
    makeappx_output = ""
    makeappx_exit: int | None = None
    makeappx_path = find_windows_sdk_tool("makeappx.exe")

    if publish_exit == 0:
        stage_checks = stage_package_root(publish_dir, package_root)
        if makeappx_path is not None:
            makeappx_exit, makeappx_output = run_makeappx(package_root, msix_path, makeappx_path)
            if makeappx_exit == 0:
                msix_checks = inspect_msix(msix_path)
            else:
                msix_checks = [
                    CheckResult(
                        "makeappx_pack",
                        "FAIL",
                        "makeappx.exe failed to assemble the package candidate.",
                    )
                ]

    report = build_report(
        out_root,
        publish_exit,
        publish_output,
        stage_checks,
        makeappx_path,
        makeappx_exit,
        makeappx_output,
        msix_checks,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("WinUI MSIX candidate probe")
        print(f"Status: {report['status']}")
        print(f"Release claim: {report['releaseClaim']}")
        print(f"Output root: {report['outputRoot']}")
        print(f"Publish exit code: {publish_exit}")
        print(f"MakeAppx exit code: {makeappx_exit}")
        for check in report["checks"]:
            print(f"- {check['status']}: {check['key']}: {check['summary']}")
        if publish_exit != 0:
            print("Publish output:")
            print(report["publishOutputTail"])
        if makeappx_exit not in (None, 0):
            print("MakeAppx output:")
            print(report["makeappxOutputTail"])

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
