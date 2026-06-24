#!/usr/bin/env python3
"""Build and inspect the current disposable WinUI publish output.

This is a smoke helper for the current unpackaged WinUI release posture. It does
not create, sign, install, or prove an MSIX/installer candidate.
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
PROJECT = ROOT / "OnslaughtCareerEditor.WinUI" / "OnslaughtCareerEditor.WinUI.csproj"
DEFAULT_OUT_ROOT = ROOT / "subagents" / "winui-publish-smoke" / "current"
PUBLISH_DIR_NAME = "publish"


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


def inspect_publish(out_dir: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    expected_files = {
        "exe": out_dir / "OnslaughtCareerEditor.WinUI.exe",
        "pri": out_dir / "OnslaughtCareerEditor.WinUI.pri",
        "notices": out_dir / "THIRD_PARTY_NOTICES.md",
    }

    for key, path in expected_files.items():
        if path.is_file() and path.stat().st_size > 0:
            results.append(CheckResult(key, "PASS", f"{relative(path)} exists and is non-empty."))
        else:
            results.append(CheckResult(key, "FAIL", f"{relative(path)} is missing or empty."))

    package_suffixes = {".msix", ".appx", ".appinstaller", ".msixbundle", ".appxbundle"}
    package_files = [
        path
        for path in out_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in package_suffixes
    ]
    if package_files:
        listed = ", ".join(relative(path) for path in package_files[:5])
        results.append(
            CheckResult(
                "package_files",
                "FAIL",
                "Unexpected package artifacts exist in the unpackaged publish smoke output: " + listed,
            )
        )
    else:
        results.append(
            CheckResult(
                "package_files",
                "PASS",
                "No MSIX/AppX/AppInstaller artifacts were produced; this remains an unpackaged publish smoke.",
            )
        )

    return results


def build_report(out_dir: Path, publish_exit: int, publish_output: str, checks: list[CheckResult]) -> dict[str, object]:
    failures = [check for check in checks if check.status == "FAIL"]
    return {
        "schema": "winui-publish-smoke.v1",
        "status": "pass" if publish_exit == 0 and not failures else "fail",
        "releaseClaim": "Disposable unpackaged WinUI publish output is buildable and inspectable; signed/MSIX installer release remains unproven.",
        "project": relative(PROJECT),
        "publishDirectory": relative(out_dir),
        "publishExitCode": publish_exit,
        "publishOutputTail": "\n".join(publish_output.splitlines()[-20:]),
        "checks": [check.__dict__ for check in checks],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and inspect disposable WinUI publish output.")
    parser.add_argument("--check", action="store_true", help="run publish and inspect output")
    parser.add_argument("--json", action="store_true", help="print JSON report")
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT, help="output root for the disposable smoke")
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
        out_root.relative_to(ROOT / "subagents")
    except ValueError:
        print(f"Refusing to write publish smoke output outside subagents/: {out_root}")
        return 1

    publish_dir = out_root / PUBLISH_DIR_NAME
    if out_root.exists():
        shutil.rmtree(out_root)
    publish_dir.mkdir(parents=True, exist_ok=True)

    publish_exit, publish_output = run_publish(publish_dir)
    checks = inspect_publish(publish_dir) if publish_exit == 0 else []
    report = build_report(publish_dir, publish_exit, publish_output, checks)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("WinUI publish smoke")
        print(f"Status: {report['status']}")
        print(f"Release claim: {report['releaseClaim']}")
        print(f"Publish directory: {report['publishDirectory']}")
        print(f"Publish exit code: {publish_exit}")
        for check in checks:
            print(f"- {check.status}: {check.key}: {check.summary}")
        if publish_exit != 0:
            print("Publish output:")
            print(report["publishOutputTail"])

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
