#!/usr/bin/env python3
"""Preflight guard for the Goodies model-viewer runtime proof.

This checker does not launch the game. It verifies that the public-safe plan,
static evidence, helper scripts, observer command files, and release accounting
are in place before a future copied-profile runtime proof is attempted.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = Path("release/readiness/goodies_model_viewer_runtime_proof_plan_2026-05-08.md")
MANIFEST_PATH = Path("release/readiness/curated_release_manifest.json")

REQUIRED_EVIDENCE_FILES = (
    "goodies_model_viewer_alignment_2026-05-08.md",
    "goodies_model_viewer_readback_2026-05-08.md",
    "mesh_renderer_readback_2026-05-08.md",
    "goodies_input_observer_runtime_proof_2026-05-08.md",
)

REQUIRED_RUNTIME_HELPERS = (
    Path("tools/prepare_game_profile.ps1"),
    Path("tools/start_game_profile.ps1"),
    Path("tools/list_game_windows.ps1"),
    Path("tools/capture_game_window.ps1"),
    Path("tools/send_game_window_input.ps1"),
    Path("tools/start_cdb_server.ps1"),
    Path("tools/apply_bea_catalog_patch.py"),
)

REQUIRED_RUNTIME_OBSERVERS = (
    Path("tools/runtime-probes/goodies-input-observer.cdb.txt"),
    Path("tools/runtime-probes/goodies-selection-observer.cdb.txt"),
)

REQUIRED_NPM_SCRIPTS = (
    "test:goodies-model-viewer-alignment",
    "test:goodies-model-viewer-readback",
    "test:mesh-renderer-readback",
    "test:goodies-selection-observer-log",
)

REQUIRED_PLAN_PHRASES = (
    "not runtime proof",
    "do not launch bea",
    "do not mutate the installed game",
    "original bea.exe",
    "copied profile",
    "force_windowed",
    "copied executable",
    "subagents/",
    "no bea process remains",
)


@dataclass(frozen=True)
class CheckResult:
    key: str
    status: str
    summary: str


def relative_list(paths: list[Path]) -> str:
    return ", ".join(path.as_posix() for path in paths)


def check_paths(root: Path, key: str, paths: tuple[Path, ...]) -> CheckResult:
    missing = [path for path in paths if not (root / path).is_file()]
    if missing:
        return CheckResult(key, "FAIL", f"Missing required file(s): {relative_list(missing)}.")
    return CheckResult(key, "PASS", f"Found {len(paths)} required file(s).")


def check_evidence_files(root: Path) -> CheckResult:
    paths = tuple(Path("release/readiness") / name for name in REQUIRED_EVIDENCE_FILES)
    return check_paths(root, "required_evidence_files", paths)


def check_plan(root: Path) -> list[CheckResult]:
    path = root / PLAN_PATH
    if not path.is_file():
        return [CheckResult("runtime_proof_plan", "FAIL", f"{PLAN_PATH.as_posix()} is missing.")]

    text = path.read_text(encoding="utf-8").lower()
    results = [CheckResult("runtime_proof_plan", "PASS", f"{PLAN_PATH.as_posix()} exists.")]
    missing = [phrase for phrase in REQUIRED_PLAN_PHRASES if phrase not in text]
    if missing:
        results.append(
            CheckResult(
                "runtime_safety_boundary",
                "FAIL",
                f"Plan is missing safety phrase(s): {', '.join(missing)}.",
            )
        )
    else:
        results.append(
            CheckResult(
                "runtime_safety_boundary",
                "PASS",
                "Plan records copied-profile, no-original-mutation, no-runtime-launch, private-evidence, and cleanup boundaries.",
            )
        )
    return results


def check_package_scripts(root: Path) -> CheckResult:
    package_path = root / "package.json"
    if not package_path.is_file():
        return CheckResult("required_npm_scripts", "FAIL", "package.json is missing.")

    data = json.loads(package_path.read_text(encoding="utf-8"))
    scripts = data.get("scripts", {})
    missing = [script for script in REQUIRED_NPM_SCRIPTS if script not in scripts]
    if missing:
        return CheckResult("required_npm_scripts", "FAIL", f"Missing npm script(s): {', '.join(missing)}.")
    return CheckResult("required_npm_scripts", "PASS", f"Found {len(REQUIRED_NPM_SCRIPTS)} required npm script(s).")


def check_manifest(root: Path) -> CheckResult:
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.is_file():
        return CheckResult("release_manifest_entry", "FAIL", f"{MANIFEST_PATH.as_posix()} is missing.")

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    include = data.get("include", data.get("entries", []))
    included_paths = {
        entry.get("path") if isinstance(entry, dict) else str(entry)
        for entry in include
    }
    if PLAN_PATH.as_posix() in included_paths:
        return CheckResult("release_manifest_entry", "PASS", "Runtime proof plan is explicitly included in the curated manifest.")
    return CheckResult(
        "release_manifest_entry",
        "FAIL",
        f"{PLAN_PATH.as_posix()} is not explicitly included in the curated manifest.",
    )


def run_checks(root: Path = ROOT) -> list[CheckResult]:
    root = root.resolve()
    results: list[CheckResult] = []
    results.extend(check_plan(root))
    results.append(check_evidence_files(root))
    results.append(check_paths(root, "runtime_helper_files", REQUIRED_RUNTIME_HELPERS))
    results.append(check_paths(root, "runtime_observer_files", REQUIRED_RUNTIME_OBSERVERS))
    results.append(check_package_scripts(root))
    results.append(check_manifest(root))
    return results


def print_results(results: list[CheckResult]) -> None:
    for result in results:
        print(f"{result.status} {result.key}: {result.summary}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if any preflight check fails.")
    args = parser.parse_args(argv)

    results = run_checks(ROOT)
    print_results(results)
    failures = [result for result in results if result.status == "FAIL"]
    if failures:
        print(f"FAIL: {len(failures)} Goodies model-viewer runtime preflight check(s) failed.", file=sys.stderr)
        return 1
    print("PASS: Goodies model-viewer runtime proof preflight is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
