#!/usr/bin/env python3
"""Probe WinUI MSIX install behavior without trusting the generated certificate.

This helper intentionally does not add certificates to Windows trust stores. It
creates a signed disposable MSIX candidate under ``subagents/``, attempts to
install it, treats the expected untrusted-certificate deployment failure as a
safe blocked result, and verifies no package/process remains.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
DEFAULT_OUT_ROOT = ROOT / "subagents" / "winui-msix-install-probe" / "current"
PACKAGE_NAME = "OnslaughtCareerEditor.WinUI.LocalProbe"
SIGNED_PACKAGE = "OnslaughtCareerEditor.WinUI.LocalProbe.signed.msix"


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


def run(command: list[str], timeout_seconds: int = 180) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout_seconds,
        check=False,
    )
    return completed.returncode, completed.stdout


def powershell(script: str, timeout_seconds: int = 180) -> tuple[int, str]:
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


def build_signed_candidate(out_root: Path) -> tuple[Path, list[CheckResult], str]:
    signing_root = out_root / "signing"
    command = [
        "py",
        "-3",
        str(TOOLS / "winui_msix_signing_probe.py"),
        "--check",
        "--out-root",
        str(signing_root),
    ]
    exit_code, output = run(command, timeout_seconds=300)
    signed_package = signing_root / SIGNED_PACKAGE
    checks = [
        CheckResult(
            "signing_probe",
            "PASS" if exit_code == 0 else "FAIL",
            f"Signing probe exit code {exit_code}.",
        )
    ]
    if signed_package.is_file() and signed_package.stat().st_size > 0:
        checks.append(
            CheckResult(
                "signed_package",
                "PASS",
                f"{relative(signed_package)} exists and is non-empty.",
            )
        )
    else:
        checks.append(CheckResult("signed_package", "FAIL", f"{relative(signed_package)} is missing."))

    return signed_package, checks, output


def get_package_state() -> tuple[int, str]:
    return powershell(
        f"Get-AppxPackage -Name '{PACKAGE_NAME}' | Select-Object Name,PackageFullName,InstallLocation | ConvertTo-Json -Compress",
        timeout_seconds=60,
    )


def get_process_state() -> tuple[int, str]:
    return powershell(
        "Get-Process -Name OnslaughtCareerEditor.WinUI -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,Path | ConvertTo-Json -Compress",
        timeout_seconds=60,
    )


def remove_package_if_present() -> tuple[bool, str]:
    script = f"""
$pkg = Get-AppxPackage -Name '{PACKAGE_NAME}'
if ($null -eq $pkg) {{
  Write-Output 'not-installed'
  exit 0
}}
Remove-AppxPackage -Package $pkg.PackageFullName -ErrorAction Stop
Write-Output ('removed:' + $pkg.PackageFullName)
"""
    exit_code, output = powershell(script, timeout_seconds=180)
    return exit_code == 0, output


def attempt_install(signed_package: Path) -> tuple[int, str]:
    script = f"""
$ErrorActionPreference = 'Stop'
Add-AppxPackage -Path '{signed_package}'
"""
    return powershell(script, timeout_seconds=180)


def classify_install_result(exit_code: int, output: str) -> CheckResult:
    text = output.lower()
    if exit_code == 0:
        return CheckResult("install_attempt", "PASS", "Add-AppxPackage succeeded; cleanup is required.")
    if "0x800b0109" in text or "not trusted" in text:
        return CheckResult(
            "install_attempt",
            "PASS",
            "Add-AppxPackage was blocked by untrusted generated certificate as expected.",
        )
    return CheckResult("install_attempt", "FAIL", f"Add-AppxPackage failed with an unexpected result code {exit_code}.")


def build_report(
    out_root: Path,
    checks: list[CheckResult],
    signing_output: str,
    install_exit: int | None,
    install_output: str,
    before_package: str,
    after_package: str,
    process_state: str,
    cleanup_output: str,
) -> dict[str, object]:
    failures = [check for check in checks if check.status == "FAIL"]
    return {
        "schema": "winui-msix-install-probe.v1",
        "status": "pass" if not failures else "blocked",
        "releaseClaim": "Install is safely blocked without certificate trust; installer-grade trust/install-uninstall remains unproven.",
        "outputRoot": relative(out_root),
        "installExitCode": install_exit,
        "checks": [check.__dict__ for check in checks],
        "signingOutputTail": "\n".join(signing_output.splitlines()[-30:]),
        "installOutputTail": "\n".join(install_output.splitlines()[-40:]),
        "packageBefore": before_package.strip() or "<none>",
        "packageAfter": after_package.strip() or "<none>",
        "processAfter": process_state.strip() or "<none>",
        "cleanupOutput": cleanup_output.strip() or "<none>",
        "notProven": [
            "Trusting a signing certificate",
            "Successful package install",
            "Launch smoke from installed package identity",
            "Successful uninstall after install",
            "SmartScreen/store/distribution posture",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe WinUI MSIX install behavior without trusting the generated cert.")
    parser.add_argument("--check", action="store_true", help="run the install probe")
    parser.add_argument("--json", action="store_true", help="print JSON report")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT, help="ignored output root under subagents/")
    args = parser.parse_args()

    if not args.check:
        parser.error("expected --check")

    out_root = args.out_root
    if not out_root.is_absolute():
        out_root = ROOT / out_root
    out_root = out_root.resolve()
    try:
        out_root.relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write install probe output outside subagents/: {out_root}")
        return 1

    safe_rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    signed_package, checks, signing_output = build_signed_candidate(out_root)
    _, before_package = get_package_state()

    install_exit: int | None = None
    install_output = ""
    cleanup_output = ""
    if all(check.status != "FAIL" for check in checks):
        install_exit, install_output = attempt_install(signed_package)
        checks.append(classify_install_result(install_exit, install_output))
        cleanup_ok, cleanup_output = remove_package_if_present()
        checks.append(
            CheckResult(
                "cleanup",
                "PASS" if cleanup_ok else "FAIL",
                "No installed local probe package remained after cleanup." if cleanup_ok else "Cleanup failed.",
            )
        )

    _, after_package = get_package_state()
    _, process_state = get_process_state()
    if after_package.strip():
        checks.append(CheckResult("package_after", "FAIL", "Local probe package remains installed."))
    else:
        checks.append(CheckResult("package_after", "PASS", "No local probe package is installed."))
    if process_state.strip():
        checks.append(CheckResult("process_after", "FAIL", "WinUI process remains running after install probe."))
    else:
        checks.append(CheckResult("process_after", "PASS", "No WinUI process remains running after install probe."))

    report = build_report(
        out_root,
        checks,
        signing_output,
        install_exit,
        install_output,
        before_package,
        after_package,
        process_state,
        cleanup_output,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("WinUI MSIX install probe")
        print(f"Status: {report['status']}")
        print(f"Release claim: {report['releaseClaim']}")
        print(f"Output root: {report['outputRoot']}")
        print(f"Install exit code: {install_exit}")
        for check in report["checks"]:
            print(f"- {check['status']}: {check['key']}: {check['summary']}")
        if install_exit not in (None, 0):
            print("Install output:")
            print(report["installOutputTail"])

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
