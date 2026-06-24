#!/usr/bin/env python3
"""Probe reversible current-user trusted install/launch/uninstall for WinUI MSIX.

This helper is intentionally local and disposable. It creates a signed MSIX
candidate under ``subagents/``, imports only the generated public certificate to
the current user's trust store, installs the local probe package identity,
launches it, stops the app process, uninstalls the package, removes the
certificate, and verifies no package/process/certificate remains.

It does not use LocalMachine certificate stores, does not use a real signing
identity, and does not prove SmartScreen/store/distribution readiness.
"""

from __future__ import annotations

import argparse
import json
import secrets
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import winui_msix_signing_probe as signing_probe  # noqa: E402


DEFAULT_OUT_ROOT = ROOT / "subagents" / "winui-msix-trusted-install-probe" / "current"
PACKAGE_NAME = "OnslaughtCareerEditor.WinUI.LocalProbe"
APP_PROCESS_NAME = "OnslaughtCareerEditor.WinUI"
APP_ID = "App"
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
    subagents_root = (ROOT / "subagents").resolve()
    try:
        path.relative_to(subagents_root)
    except ValueError as exc:
        raise RuntimeError(f"Refusing to remove path outside subagents/: {path}") from exc
    if path.exists():
        shutil.rmtree(path)


def run(command: list[str], timeout_seconds: int = 180) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        return 124, f"Timed out after {timeout_seconds} seconds.\n{output}"
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


def build_signed_candidate(out_root: Path) -> tuple[Path | None, Path | None, str, list[CheckResult], str]:
    checks: list[CheckResult] = []
    unsigned_msix, candidate_checks, candidate_output = signing_probe.create_unsigned_candidate(out_root / "candidate")
    checks.extend(CheckResult(check.key, check.status, check.summary) for check in candidate_checks)

    pfx_path: Path | None = None
    signed_msix: Path | None = None
    password = ""
    signing_output = candidate_output
    signtool_path: Path | None = None
    sign_exit: int | None = None

    if unsigned_msix is not None and all(check.status != "FAIL" for check in checks):
        password = secrets.token_urlsafe(signing_probe.PASSWORD_LENGTH)
        pfx_path, pfx_exit, pfx_output = signing_probe.generate_pfx(out_root / "cert", password)
        checks.append(
            CheckResult(
                "local_pfx",
                "PASS" if pfx_exit == 0 and pfx_path.is_file() else "FAIL",
                "Generated local PFX under ignored output." if pfx_exit == 0 and pfx_path.is_file() else "Local PFX generation failed.",
            )
        )
        signing_output = pfx_output
        if pfx_exit == 0 and pfx_path.is_file():
            signed_msix = out_root / SIGNED_PACKAGE
            sign_exit, signing_output, signtool_path = signing_probe.sign_msix(unsigned_msix, signed_msix, pfx_path, password)
            checks.append(
                CheckResult(
                    "signtool_sign",
                    "PASS" if sign_exit == 0 else "FAIL",
                    f"signtool sign exit code {sign_exit}.",
                )
            )
            if signtool_path is not None:
                checks.append(CheckResult("signtool_tool", "PASS", "signtool.exe is available from the Windows SDK."))
            if sign_exit == 0:
                checks.extend(CheckResult(check.key, check.status, check.summary) for check in signing_probe.inspect_signed_msix(signed_msix))

    return signed_msix, pfx_path, password, checks, signing_output


def get_package_state() -> tuple[int, str]:
    return powershell(
        f"Get-AppxPackage -Name '{PACKAGE_NAME}' | Select-Object Name,PackageFullName,PackageFamilyName,InstallLocation | ConvertTo-Json -Compress",
        timeout_seconds=60,
    )


def get_cert_state(thumbprint: str | None) -> tuple[int, str]:
    if not thumbprint:
        return 0, ""
    script = f"""
$thumb = '{thumbprint}'
$stores = @('TrustedPeople', 'Root')
$found = foreach ($store in $stores) {{
  $x509Store = [System.Security.Cryptography.X509Certificates.X509Store]::new(
    $store,
    [System.Security.Cryptography.X509Certificates.StoreLocation]::CurrentUser)
  $x509Store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly)
  try {{
    $matches = $x509Store.Certificates.Find(
      [System.Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,
      $thumb,
      $false)
    foreach ($cert in $matches) {{
      [pscustomobject]@{{Thumbprint=$cert.Thumbprint; Subject=$cert.Subject; Store=('CurrentUser\\' + $store)}}
    }}
  }} finally {{
    $x509Store.Close()
  }}
}}
$found | ConvertTo-Json -Compress
"""
    return powershell(script, timeout_seconds=60)


def get_process_state() -> tuple[int, str]:
    return powershell(
        f"Get-Process -Name '{APP_PROCESS_NAME}' -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,Path | ConvertTo-Json -Compress",
        timeout_seconds=60,
    )


def export_public_cert(pfx_path: Path, password: str, cert_path: Path) -> tuple[int, str, str | None]:
    companion_cert = pfx_path.with_suffix(".cer")
    if companion_cert.is_file():
        cert_path.parent.mkdir(parents=True, exist_ok=True)
        if companion_cert.resolve() != cert_path.resolve():
            shutil.copy2(companion_cert, cert_path)
        script = f"""
$ErrorActionPreference = 'Stop'
$certPath = '{cert_path}'
$cert = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($certPath)
$cert.Thumbprint
"""
        exit_code, output = powershell(script, timeout_seconds=60)
        thumbprint = output.strip().splitlines()[-1].strip() if exit_code == 0 and output.strip() else None
        return exit_code, "Copied public certificate emitted by local PFX generator.\n" + output, thumbprint

    script = f"""
$ErrorActionPreference = 'Stop'
$pfx = '{pfx_path}'
$certPath = '{cert_path}'
$password = ConvertTo-SecureString '{password}' -AsPlainText -Force
$cert = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new(
  $pfx,
  $password,
  [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::EphemeralKeySet)
[System.IO.File]::WriteAllBytes($certPath, $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert))
$cert.Thumbprint
"""
    exit_code, output = powershell(script, timeout_seconds=60)
    thumbprint = output.strip().splitlines()[-1].strip() if exit_code == 0 and output.strip() else None
    return exit_code, output, thumbprint


def import_public_cert_to_current_user(cert_path: Path, thumbprint: str, stores: list[str]) -> tuple[int, str]:
    store_array = "@(" + ",".join(f"'{store}'" for store in stores) + ")"
    script = f"""
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$certPath = '{cert_path}'
$thumb = '{thumbprint}'
$stores = {store_array}
$cert = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($certPath)
foreach ($storeName in $stores) {{
  $x509Store = [System.Security.Cryptography.X509Certificates.X509Store]::new(
    $storeName,
    [System.Security.Cryptography.X509Certificates.StoreLocation]::CurrentUser)
  $x509Store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
  try {{
    $existing = $x509Store.Certificates.Find(
      [System.Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,
      $thumb,
      $false)
    if ($existing.Count -eq 0) {{
      $x509Store.Add($cert)
    }}
  }} finally {{
    $x509Store.Close()
  }}
}}
$thumb
"""
    return powershell(script, timeout_seconds=120)


def remove_current_user_cert(thumbprint: str | None) -> tuple[int, str]:
    if not thumbprint:
        return 0, "no-thumbprint"
    script = f"""
$ErrorActionPreference = 'Continue'
$thumb = '{thumbprint}'
$stores = @('TrustedPeople', 'Root')
$removed = @()
foreach ($store in $stores) {{
  $x509Store = [System.Security.Cryptography.X509Certificates.X509Store]::new(
    $store,
    [System.Security.Cryptography.X509Certificates.StoreLocation]::CurrentUser)
  $x509Store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
  try {{
    $matches = $x509Store.Certificates.Find(
      [System.Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,
      $thumb,
      $false)
    foreach ($cert in $matches) {{
      $x509Store.Remove($cert)
      $removed += ('CurrentUser\\' + $store)
    }}
  }} finally {{
    $x509Store.Close()
  }}
}}
if ($removed.Count -eq 0) {{ 'not-found' }} else {{ 'removed:' + ($removed -join ',') }}
"""
    return powershell(script, timeout_seconds=120)


def install_package(signed_msix: Path) -> tuple[int, str]:
    script = f"""
$ErrorActionPreference = 'Stop'
Add-AppxPackage -Path '{signed_msix}'
"""
    return powershell(script, timeout_seconds=240)


def launch_package() -> tuple[int, str]:
    script = f"""
$ErrorActionPreference = 'Stop'
$pkg = Get-AppxPackage -Name '{PACKAGE_NAME}'
if ($null -eq $pkg) {{
  throw 'local probe package is not installed'
}}
$target = 'shell:AppsFolder\\' + $pkg.PackageFamilyName + '!{APP_ID}'
Start-Process $target
$deadline = (Get-Date).AddSeconds(30)
$proc = $null
while ((Get-Date) -lt $deadline) {{
  $proc = Get-Process -Name '{APP_PROCESS_NAME}' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($null -ne $proc) {{ break }}
  Start-Sleep -Milliseconds 500
}}
if ($null -eq $proc) {{
  throw 'WinUI process did not appear after package launch'
}}
$proc | Select-Object Id,ProcessName,Path | ConvertTo-Json -Compress
"""
    return powershell(script, timeout_seconds=90)


def stop_app_process() -> tuple[int, str]:
    script = f"""
$procs = Get-Process -Name '{APP_PROCESS_NAME}' -ErrorAction SilentlyContinue
if ($null -eq $procs) {{
  'not-running'
  exit 0
}}
$procs | Stop-Process -Force -ErrorAction Stop
'stopped'
"""
    return powershell(script, timeout_seconds=60)


def remove_package_if_present() -> tuple[int, str]:
    script = f"""
$ErrorActionPreference = 'Stop'
$pkg = Get-AppxPackage -Name '{PACKAGE_NAME}'
if ($null -eq $pkg) {{
  'not-installed'
  exit 0
}}
Remove-AppxPackage -Package $pkg.PackageFullName
'removed:' + $pkg.PackageFullName
"""
    return powershell(script, timeout_seconds=240)


def check(status_key: str, ok: bool, success: str, failure: str) -> CheckResult:
    return CheckResult(status_key, "PASS" if ok else "FAIL", success if ok else failure)


def build_report(
    out_root: Path,
    checks: list[CheckResult],
    thumbprint: str | None,
    package_before: str,
    package_after: str,
    cert_after: str,
    process_after: str,
    install_exit: int | None,
    install_output: str,
    launch_exit: int | None,
    launch_output: str,
    stop_output: str,
    remove_package_output: str,
    remove_cert_output: str,
) -> dict[str, object]:
    failures = [item for item in checks if item.status == "FAIL"]
    failure_keys = {item.key for item in failures}
    cleanup_keys = {
        "stop_process",
        "remove_package",
        "remove_certificate",
        "package_after",
        "certificate_after",
        "process_after",
    }
    cleanup_passed = all(
        any(item.key == key and item.status == "PASS" for item in checks)
        for key in cleanup_keys
    )
    install_text = install_output.lower()
    expected_trust_blocker = (
        failure_keys == {"install_package"}
        and install_exit not in (None, 0)
        and cleanup_passed
        and ("0x800b0109" in install_text or "root certificate" in install_text)
    )
    status = "pass" if not failures else "guarded-blocked" if expected_trust_blocker else "blocked"
    return {
        "schema": "winui-msix-trusted-install-probe.v1",
        "status": status,
        "releaseClaim": "Disposable current-user trusted MSIX install, package launch, app stop, uninstall, and certificate cleanup are proven only if status is pass; real signing, SmartScreen/store/distribution posture, and legal approval remain separate gates.",
        "outputRoot": relative(out_root),
        "packageName": PACKAGE_NAME,
        "certificateThumbprint": thumbprint,
        "installExitCode": install_exit,
        "launchExitCode": launch_exit,
        "checks": [item.__dict__ for item in checks],
        "packageBefore": package_before.strip() or "<none>",
        "packageAfter": package_after.strip() or "<none>",
        "certificateAfter": cert_after.strip() or "<none>",
        "processAfter": process_after.strip() or "<none>",
        "installOutputTail": "\n".join(install_output.splitlines()[-40:]),
        "launchOutputTail": "\n".join(launch_output.splitlines()[-40:]),
        "stopOutput": stop_output.strip() or "<none>",
        "removePackageOutput": remove_package_output.strip() or "<none>",
        "removeCertificateOutput": remove_cert_output.strip() or "<none>",
        "notProven": [
            "Real public signing identity",
            "Installer/MSIXBundle/AppInstaller distribution channel",
            "SmartScreen/store/reputation posture",
            "Legal/compliance approval for public binary redistribution",
            "End-user install UX beyond this local current-user trust probe",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a reversible trusted WinUI MSIX install/launch/uninstall probe.")
    parser.add_argument("--check", action="store_true", help="run the trusted install probe")
    parser.add_argument("--json", action="store_true", help="print JSON report")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT, help="ignored output root under subagents/")
    parser.add_argument(
        "--allow-current-user-cert-trust",
        action="store_true",
        help="temporarily import the generated public certificate into CurrentUser trust stores",
    )
    parser.add_argument(
        "--trust-root-too",
        action="store_true",
        help="also add the generated public certificate to CurrentUser Root; requires --allow-interactive-root-cert-prompt",
    )
    parser.add_argument(
        "--allow-interactive-root-cert-prompt",
        action="store_true",
        help="allow the CurrentUser Root import path, which may require an interactive Windows trust confirmation",
    )
    args = parser.parse_args()

    if not args.check:
        parser.error("expected --check")
    if not args.allow_current_user_cert_trust:
        print("Refusing trusted install probe without --allow-current-user-cert-trust.")
        return 2
    if args.trust_root_too and not args.allow_interactive_root_cert_prompt:
        print("Refusing CurrentUser Root trust probe without --allow-interactive-root-cert-prompt.")
        print("TrustedPeople-only probing is non-interactive; Root trust may prompt and is not safe for unattended runs.")
        return 2

    out_root = args.out_root
    if not out_root.is_absolute():
        out_root = ROOT / out_root
    out_root = out_root.resolve()
    try:
        out_root.relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write trusted install probe output outside subagents/: {out_root}")
        return 1

    safe_rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    checks: list[CheckResult] = []
    signed_msix: Path | None = None
    pfx_path: Path | None = None
    password = ""
    thumbprint: str | None = None
    package_before = ""
    package_after = ""
    cert_after = ""
    process_after = ""
    install_exit: int | None = None
    launch_exit: int | None = None
    install_output = ""
    launch_output = ""
    stop_output = ""
    remove_package_output = ""
    remove_cert_output = ""

    try:
        signed_msix, pfx_path, password, candidate_checks, signing_output = build_signed_candidate(out_root)
        checks.extend(candidate_checks)
        if signed_msix is None or not signed_msix.is_file():
            checks.append(CheckResult("signed_package", "FAIL", "Signed package was not created."))
        else:
            checks.append(CheckResult("signed_package", "PASS", "Signed disposable package exists under ignored output."))

        _, package_before = get_package_state()
        if signed_msix is not None and pfx_path is not None and all(item.status != "FAIL" for item in checks):
            stores = ["TrustedPeople"]
            if args.trust_root_too:
                stores.append("Root")
            cert_path = out_root / "cert" / "OnslaughtCareerEditor.LocalProbe.cer"
            export_exit, export_output, thumbprint = export_public_cert(pfx_path, password, cert_path)
            checks.append(
                check(
                    "public_cert_export",
                    export_exit == 0 and bool(thumbprint) and cert_path.is_file(),
                    "Generated public certificate was exported under ignored output before trust-store mutation.",
                    f"Generated public certificate export failed with exit code {export_exit}.",
                )
            )
            trust_exit = 1
            trust_output = ""
            if export_exit == 0 and thumbprint and cert_path.is_file():
                trust_exit, trust_output = import_public_cert_to_current_user(cert_path, thumbprint, stores)
            checks.append(
                check(
                    "current_user_cert_trust",
                    trust_exit == 0 and bool(thumbprint),
                    "Generated public certificate was temporarily trusted for CurrentUser.",
                    f"Generated public certificate trust import failed with exit code {trust_exit}.",
                )
            )

            if trust_exit == 0 and thumbprint:
                install_exit, install_output = install_package(signed_msix)
                checks.append(
                    check(
                        "install_package",
                        install_exit == 0,
                        "Add-AppxPackage installed the disposable local probe package.",
                        f"Add-AppxPackage failed with exit code {install_exit}.",
                    )
                )

            if install_exit == 0:
                launch_exit, launch_output = launch_package()
                checks.append(
                    check(
                        "launch_package",
                        launch_exit == 0,
                        "Installed package launched and produced a WinUI process.",
                        f"Installed package launch failed with exit code {launch_exit}.",
                    )
                )
    finally:
        stop_exit, stop_output = stop_app_process()
        checks.append(
            check(
                "stop_process",
                stop_exit == 0,
                "WinUI process stop/absence check completed.",
                f"WinUI process cleanup failed with exit code {stop_exit}.",
            )
        )
        remove_pkg_exit, remove_package_output = remove_package_if_present()
        checks.append(
            check(
                "remove_package",
                remove_pkg_exit == 0,
                "Disposable local probe package was absent or removed.",
                f"Disposable local probe package removal failed with exit code {remove_pkg_exit}.",
            )
        )
        remove_cert_exit, remove_cert_output = remove_current_user_cert(thumbprint)
        checks.append(
            check(
                "remove_certificate",
                remove_cert_exit == 0,
                "Generated CurrentUser certificate was absent or removed.",
                f"Generated CurrentUser certificate removal failed with exit code {remove_cert_exit}.",
            )
        )
        _, package_after = get_package_state()
        _, cert_after = get_cert_state(thumbprint)
        _, process_after = get_process_state()
        checks.append(
            check(
                "package_after",
                not package_after.strip(),
                "No disposable local probe package remains installed.",
                "Disposable local probe package remains installed.",
            )
        )
        checks.append(
            check(
                "certificate_after",
                not cert_after.strip(),
                "Generated certificate is not present in CurrentUser trust stores after cleanup.",
                "Generated certificate remains in a CurrentUser trust store.",
            )
        )
        checks.append(
            check(
                "process_after",
                not process_after.strip(),
                "No WinUI process remains running after cleanup.",
                "WinUI process remains running after cleanup.",
            )
        )

    report = build_report(
        out_root,
        checks,
        thumbprint,
        package_before,
        package_after,
        cert_after,
        process_after,
        install_exit,
        install_output,
        launch_exit,
        launch_output,
        stop_output,
        remove_package_output,
        remove_cert_output,
    )
    (out_root / "trusted-install-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("WinUI MSIX trusted install probe")
        print(f"Status: {report['status']}")
        print(f"Release claim: {report['releaseClaim']}")
        print(f"Output root: {report['outputRoot']}")
        for item in report["checks"]:
            print(f"- {item['status']}: {item['key']}: {item['summary']}")
        if report["status"] != "pass":
            print("Install output:")
            print(report["installOutputTail"])
            print("Launch output:")
            print(report["launchOutputTail"])

    return 0 if report["status"] in ("pass", "guarded-blocked") else 1


if __name__ == "__main__":
    raise SystemExit(main())
