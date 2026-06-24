#!/usr/bin/env python3
"""Sign a disposable WinUI MSIX candidate with a generated local PFX.

This proof is intentionally narrower than installer readiness. It creates a
throwaway certificate file under ``subagents/``, signs a copied local MSIX with
Windows SDK ``signtool.exe``, and verifies that the signed package contains an
Appx signature. It does not install the certificate, trust the certificate, add
anything to the Windows certificate stores, install the package, or launch the
app from a package identity.
"""

from __future__ import annotations

import argparse
import json
import secrets
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import winui_msix_candidate_probe as candidate_probe  # noqa: E402


DEFAULT_OUT_ROOT = ROOT / "subagents" / "winui-msix-signing-probe" / "current"
SUBJECT = "CN=Onslaught Career Editor Local Probe"
PASSWORD_LENGTH = 32


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


def write_cert_generator(project_dir: Path) -> Path:
    project_dir.mkdir(parents=True, exist_ok=True)
    csproj = project_dir / "LocalPfxGenerator.csproj"
    program = project_dir / "Program.cs"
    csproj.write_text(
        """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
""",
        encoding="utf-8",
        newline="\n",
    )
    program.write_text(
        """using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;

if (args.Length != 3)
{
    Console.Error.WriteLine("Usage: <pfx-path> <password> <subject>");
    return 2;
}

var pfxPath = args[0];
var password = args[1];
var subject = args[2];
var publicCertPath = Path.ChangeExtension(pfxPath, ".cer");

using var rsa = RSA.Create(2048);
var request = new CertificateRequest(
    new X500DistinguishedName(subject),
    rsa,
    HashAlgorithmName.SHA256,
    RSASignaturePadding.Pkcs1);

request.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, false));
request.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature, false));
request.CertificateExtensions.Add(new X509SubjectKeyIdentifierExtension(request.PublicKey, false));

using var certificate = request.CreateSelfSigned(
    DateTimeOffset.UtcNow.AddDays(-1),
    DateTimeOffset.UtcNow.AddYears(1));

File.WriteAllBytes(pfxPath, certificate.Export(X509ContentType.Pfx, password));
File.WriteAllBytes(publicCertPath, certificate.Export(X509ContentType.Cert));
Console.WriteLine("Generated local PFX without importing it into a certificate store.");
return 0;
""",
        encoding="utf-8",
        newline="\n",
    )
    return csproj


def generate_pfx(cert_dir: Path, password: str) -> tuple[Path, int, str]:
    pfx_path = cert_dir / "OnslaughtCareerEditor.LocalProbe.pfx"
    project_path = write_cert_generator(cert_dir / "generator")
    command = [
        "dotnet",
        "run",
        "--project",
        str(project_path),
        "--",
        str(pfx_path),
        password,
        SUBJECT,
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return pfx_path, completed.returncode, completed.stdout


def create_unsigned_candidate(candidate_root: Path) -> tuple[Path | None, list[CheckResult], str]:
    publish_dir = candidate_root / "publish"
    package_root = candidate_root / "package"
    unsigned_msix = candidate_root / "OnslaughtCareerEditor.WinUI.LocalProbe.msix"
    publish_dir.mkdir(parents=True, exist_ok=True)

    publish_exit, publish_output = candidate_probe.run_publish(publish_dir)
    checks: list[CheckResult] = [
        CheckResult(
            "candidate_publish",
            "PASS" if publish_exit == 0 else "FAIL",
            f"dotnet publish exit code {publish_exit}.",
        )
    ]
    if publish_exit != 0:
        return None, checks, publish_output

    for check in candidate_probe.stage_package_root(publish_dir, package_root):
        checks.append(CheckResult(check.key, check.status, check.summary))

    makeappx = candidate_probe.find_windows_sdk_tool("makeappx.exe")
    if makeappx is None:
        checks.append(CheckResult("makeappx_tool", "FAIL", "makeappx.exe was not found."))
        return None, checks, publish_output

    pack_exit, pack_output = candidate_probe.run_makeappx(package_root, unsigned_msix, makeappx)
    checks.append(
        CheckResult(
            "makeappx_pack",
            "PASS" if pack_exit == 0 else "FAIL",
            f"makeappx.exe exit code {pack_exit}.",
        )
    )
    if pack_exit != 0:
        return None, checks, pack_output

    for check in candidate_probe.inspect_msix(unsigned_msix):
        checks.append(CheckResult(check.key, check.status, check.summary))

    return unsigned_msix, checks, pack_output


def sign_msix(unsigned_msix: Path, signed_msix: Path, pfx_path: Path, password: str) -> tuple[int, str, Path | None]:
    signtool = candidate_probe.find_windows_sdk_tool("signtool.exe")
    if signtool is None:
        return 127, "signtool.exe was not found.", None

    shutil.copy2(unsigned_msix, signed_msix)
    command = [
        str(signtool),
        "sign",
        "/fd",
        "SHA256",
        "/f",
        str(pfx_path),
        "/p",
        password,
        str(signed_msix),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode, completed.stdout, signtool


def inspect_signed_msix(signed_msix: Path) -> list[CheckResult]:
    checks: list[CheckResult] = []
    if not signed_msix.is_file() or signed_msix.stat().st_size <= 0:
        return [CheckResult("signed_msix_file", "FAIL", f"{relative(signed_msix)} was not created.")]

    checks.append(
        CheckResult(
            "signed_msix_file",
            "PASS",
            f"{relative(signed_msix)} exists and is non-empty ({signed_msix.stat().st_size} bytes).",
        )
    )
    with zipfile.ZipFile(signed_msix) as package:
        names = set(package.namelist())

    if "AppxSignature.p7x" in names:
        checks.append(CheckResult("appx_signature", "PASS", "Signed package contains AppxSignature.p7x."))
    else:
        checks.append(CheckResult("appx_signature", "FAIL", "Signed package does not contain AppxSignature.p7x."))

    return checks


def build_report(
    out_root: Path,
    candidate_checks: list[CheckResult],
    pfx_path: Path | None,
    pfx_exit: int | None,
    pfx_output: str,
    signtool_path: Path | None,
    sign_exit: int | None,
    sign_output: str,
    signed_checks: list[CheckResult],
) -> dict[str, object]:
    checks = list(candidate_checks)
    if pfx_path is not None:
        checks.append(
            CheckResult(
                "local_pfx",
                "PASS" if pfx_exit == 0 and pfx_path.is_file() else "FAIL",
                f"Local PFX file {'exists' if pfx_path.is_file() else 'is missing'} under ignored output.",
            )
        )
    if signtool_path is not None:
        checks.append(CheckResult("signtool_tool", "PASS", "signtool.exe is available from the Windows SDK."))
    else:
        checks.append(CheckResult("signtool_tool", "FAIL", "signtool.exe was not found."))

    if sign_exit is not None:
        checks.append(
            CheckResult(
                "signtool_sign",
                "PASS" if sign_exit == 0 else "FAIL",
                f"signtool sign exit code {sign_exit}.",
            )
        )
    checks.extend(signed_checks)

    failures = [check for check in checks if check.status == "FAIL"]
    return {
        "schema": "winui-msix-signing-probe.v1",
        "status": "pass" if not failures else "blocked",
        "releaseClaim": "Disposable local MSIX signing is proven only if status is pass; trust/install/uninstall remain separate release gates.",
        "outputRoot": relative(out_root),
        "pfxExitCode": pfx_exit,
        "pfxOutputTail": "\n".join(pfx_output.splitlines()[-20:]),
        "signtoolPath": str(signtool_path) if signtool_path is not None else None,
        "signtoolExitCode": sign_exit,
        "signtoolOutputTail": "\n".join(sign_output.splitlines()[-40:]),
        "checks": [check.__dict__ for check in checks],
        "notProven": [
            "Certificate trust posture",
            "Install smoke",
            "Launch smoke from installed package identity",
            "Uninstall smoke",
            "SmartScreen/store/distribution posture",
            "Legal/compliance approval for public binary redistribution",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sign and inspect a disposable WinUI MSIX candidate.")
    parser.add_argument("--check", action="store_true", help="run the signing probe")
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
        print(f"Refusing to write signing probe output outside subagents/: {out_root}")
        return 1

    safe_rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    unsigned_msix, candidate_checks, candidate_output = create_unsigned_candidate(out_root / "candidate")
    pfx_path: Path | None = None
    pfx_exit: int | None = None
    pfx_output = ""
    signtool_path: Path | None = None
    sign_exit: int | None = None
    sign_output = candidate_output
    signed_checks: list[CheckResult] = []

    if unsigned_msix is not None and all(check.status != "FAIL" for check in candidate_checks):
        password = secrets.token_urlsafe(PASSWORD_LENGTH)
        pfx_path, pfx_exit, pfx_output = generate_pfx(out_root / "cert", password)
        if pfx_exit == 0 and pfx_path.is_file():
            signed_msix = out_root / "OnslaughtCareerEditor.WinUI.LocalProbe.signed.msix"
            sign_exit, sign_output, signtool_path = sign_msix(unsigned_msix, signed_msix, pfx_path, password)
            if sign_exit == 0:
                signed_checks = inspect_signed_msix(signed_msix)
        else:
            signed_checks = [CheckResult("local_pfx", "FAIL", "Local PFX generation failed.")]

    report = build_report(
        out_root,
        candidate_checks,
        pfx_path,
        pfx_exit,
        pfx_output,
        signtool_path,
        sign_exit,
        sign_output,
        signed_checks,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("WinUI MSIX signing probe")
        print(f"Status: {report['status']}")
        print(f"Release claim: {report['releaseClaim']}")
        print(f"Output root: {report['outputRoot']}")
        print(f"PFX exit code: {pfx_exit}")
        print(f"SignTool exit code: {sign_exit}")
        for check in report["checks"]:
            print(f"- {check['status']}: {check['key']}: {check['summary']}")
        if pfx_exit not in (None, 0):
            print("PFX generation output:")
            print(report["pfxOutputTail"])
        if sign_exit not in (None, 0):
            print("SignTool output:")
            print(report["signtoolOutputTail"])

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
