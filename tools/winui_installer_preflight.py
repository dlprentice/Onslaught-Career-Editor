#!/usr/bin/env python3
"""Check WinUI installer/signing readiness posture.

This is a guardrail, not an installer builder. The current WinUI lane has
validated disposable unpackaged publish output, disposable unsigned MSIX
assembly, disposable local signing, untrusted-certificate install blocking, and
TrustedPeople-only trust-store cleanup/blocker evidence.
Installer release readiness remains unproven until certificate trust posture,
install/uninstall smoke, notices, and LGPL redistribution review are all
checked together.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "OnslaughtCareerEditor.WinUI" / "OnslaughtCareerEditor.WinUI.csproj"
NOTICE_DRAFT = ROOT / "release" / "readiness" / "THIRD_PARTY_NOTICES.winui-draft.md"
REQUIRED_EVIDENCE = {
    "unpackaged_publish_smoke": ROOT / "release" / "readiness" / "winui_publish_smoke_2026-05-05.md",
    "windows_appsdk2_migration": ROOT
    / "release"
    / "readiness"
    / "winui_windows_appsdk2_migration_2026-05-06.md",
    "published_notice_inclusion": ROOT
    / "release"
    / "readiness"
    / "winui_published_notice_inclusion_2026-05-06.md",
    "dependency_license_review": ROOT
    / "release"
    / "readiness"
    / "winui_dependency_license_review_2026-05-06.md",
    "lgpl_redistribution_review": ROOT
    / "release"
    / "readiness"
    / "winui_lgpl_redistribution_review_2026-05-06.md",
    "unsigned_msix_candidate_probe": ROOT
    / "release"
    / "readiness"
    / "winui_msix_current_candidate_probe_2026-05-08.md",
    "local_msix_signing_probe": ROOT
    / "release"
    / "readiness"
    / "winui_msix_current_signing_probe_2026-05-08.md",
    "untrusted_install_probe": ROOT
    / "release"
    / "readiness"
    / "winui_msix_current_untrusted_install_probe_2026-05-08.md",
    "trusted_install_probe": ROOT
    / "release"
    / "readiness"
    / "winui_msix_trusted_install_guarded_blocker_2026-05-22.md",
}
RELEASE_CHECKLIST = ROOT / "release" / "readiness" / "release_readiness_checklist.md"
PACKAGE_MANIFEST = PROJECT.parent / "Package.appxmanifest"
WINDOWS_KITS_BIN = Path("C:/Program Files (x86)/Windows Kits/10/bin")

EXPECTED_UNPACKAGED_PROPERTIES = {
    "EnableMsixTooling": "false",
    "AppxPackage": "false",
    "WindowsPackageType": "None",
    "WindowsAppSDKSelfContained": "true",
}

CERTIFICATE_PROPERTIES = (
    "PackageCertificateKeyFile",
    "PackageCertificatePassword",
    "PackageCertificateThumbprint",
)


@dataclass
class CheckResult:
    key: str
    status: str
    summary: str


def strip_namespace(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def read_properties(project: Path) -> dict[str, str]:
    tree = ET.parse(project)
    props: dict[str, str] = {}
    for element in tree.iter():
        tag = strip_namespace(element.tag)
        text = (element.text or "").strip()
        if text:
            props[tag] = text
    return props


def check_project_properties(props: dict[str, str]) -> list[CheckResult]:
    results: list[CheckResult] = []

    for key, expected in EXPECTED_UNPACKAGED_PROPERTIES.items():
        actual = props.get(key)
        if actual == expected:
            results.append(CheckResult(key, "PASS", f"{key} is {actual}."))
        else:
            results.append(
                CheckResult(
                    key,
                    "FAIL",
                    f"{key} is {actual or '<missing>'}; expected {expected} for the current guarded unpackaged posture.",
                )
            )

    configured = [key for key in CERTIFICATE_PROPERTIES if props.get(key)]
    if configured:
        results.append(
            CheckResult(
                "package_certificate",
                "FAIL",
                "Package certificate properties are present; signed packaging needs a fresh evidence pass.",
            )
        )
    else:
        results.append(
            CheckResult(
                "package_certificate",
                "PASS",
                "No package certificate properties are configured in the WinUI project.",
            )
        )

    return results


def check_evidence_files() -> list[CheckResult]:
    results: list[CheckResult] = []

    if NOTICE_DRAFT.is_file():
        results.append(CheckResult("notice_draft", "PASS", "WinUI third-party notice draft exists."))
    else:
        results.append(CheckResult("notice_draft", "FAIL", "WinUI third-party notice draft is missing."))

    for key, path in REQUIRED_EVIDENCE.items():
        if path.is_file():
            results.append(CheckResult(key, "PASS", f"{path.relative_to(ROOT)} exists."))
        else:
            results.append(CheckResult(key, "FAIL", f"{path.relative_to(ROOT)} is missing."))

    return results


def check_package_inputs() -> list[CheckResult]:
    results: list[CheckResult] = []

    if PACKAGE_MANIFEST.is_file():
        results.append(
            CheckResult(
                "package_manifest",
                "FAIL",
                "Package.appxmanifest exists; MSIX/package identity needs a fresh packaging evidence pass.",
            )
        )
    else:
        results.append(
            CheckResult(
                "package_manifest",
                "PASS",
                "No source Package.appxmanifest is present; current WinUI project is not configured as an MSIX package.",
            )
        )

    package_projects = sorted(ROOT.glob("*.wapproj"))
    if package_projects:
        names = ", ".join(path.name for path in package_projects)
        results.append(
            CheckResult(
                "package_project",
                "FAIL",
                f"Windows packaging project(s) are present ({names}); run a fresh packaging evidence pass.",
            )
        )
    else:
        results.append(
            CheckResult(
                "package_project",
                "PASS",
                "No Windows packaging project is present at the repo root.",
            )
        )

    return results


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


def check_packaging_tools() -> list[CheckResult]:
    results: list[CheckResult] = []
    for key, tool_name in (("makeappx_tool", "makeappx.exe"), ("signtool_tool", "signtool.exe")):
        tool_path = find_windows_sdk_tool(tool_name)
        if tool_path is None:
            results.append(
                CheckResult(
                    key,
                    "WARN",
                    f"{tool_name} was not found on PATH or under the Windows Kits 10 bin directory.",
                )
            )
        else:
            results.append(
                CheckResult(
                    key,
                    "PASS",
                    f"{tool_name} is available from the Windows SDK toolchain.",
                )
            )

    return results


def check_release_wording() -> list[CheckResult]:
    if not RELEASE_CHECKLIST.is_file():
        return [CheckResult("release_checklist", "FAIL", "Release readiness checklist is missing.")]

    text = RELEASE_CHECKLIST.read_text(encoding="utf-8")
    required_phrases = (
        "MSIX",
        "Installer-grade trust",
        "successful install",
        "uninstall",
        "remain unproven",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    if missing:
        return [
            CheckResult(
                "release_checklist",
                "FAIL",
                "Release checklist does not clearly preserve installer/signing blockers: "
                + ", ".join(missing),
            )
        ]

    return [
        CheckResult(
            "release_checklist",
            "PASS",
            "Release checklist clearly marks installer/install-uninstall proof as unproven.",
        )
    ]


def build_report(results: list[CheckResult]) -> dict[str, object]:
    failures = [result for result in results if result.status == "FAIL"]
    return {
        "schema": "winui-installer-preflight.v1",
        "status": "blocked" if failures else "guarded-not-ready",
        "releaseClaim": "Disposable unpackaged publish, unsigned MSIX assembly, local signing, untrusted install blocking, and TrustedPeople-only cleanup/blocker evidence are proven; install is blocked without certificate trust; trusted install/launch/uninstall remains unproven.",
        "project": str(PROJECT.relative_to(ROOT)),
        "checks": [result.__dict__ for result in results],
        "requiredBeforeInstallerRelease": [
            "Choose the installer shape: MSIX, installer, or ZIP plus launcher.",
            "Create a disposable candidate from a clean checkout.",
            "Choose the real signing identity and certificate trust chain.",
            "Install, launch, smoke, uninstall, and verify no stale app process remains.",
            "Verify THIRD_PARTY_NOTICES.md and required package license files are present in the final output.",
            "Complete LGPL redistribution review for LibVLC-related runtime components.",
            "Keep private game assets, generated exports, screenshots, and local proof artifacts out of public output.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check current WinUI installer/signing readiness posture")
    parser.add_argument("--check", action="store_true", help="run the posture check and print a human summary")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a human summary")
    args = parser.parse_args()

    if not PROJECT.is_file():
        print(f"Missing WinUI project: {PROJECT}")
        return 1

    results: list[CheckResult] = []
    results.extend(check_project_properties(read_properties(PROJECT)))
    results.extend(check_package_inputs())
    results.extend(check_packaging_tools())
    results.extend(check_evidence_files())
    results.extend(check_release_wording())

    report = build_report(results)
    failures = [result for result in results if result.status == "FAIL"]

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("WinUI installer/signing preflight")
        print(f"Status: {report['status']}")
        print(f"Release claim: {report['releaseClaim']}")
        for result in results:
            print(f"- {result.status}: {result.key}: {result.summary}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
