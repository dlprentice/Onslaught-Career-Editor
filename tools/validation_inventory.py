#!/usr/bin/env python3
"""Generate and validate the package-script dependency and contract inventory."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

try:
    from npm_script_doc_check import ACTIVE_MARKDOWN_FILES
except ModuleNotFoundError:  # Support import as tools.validation_inventory.
    from tools.npm_script_doc_check import ACTIVE_MARKDOWN_FILES


ROOT = Path(__file__).resolve().parents[1]
NPM_RUN = re.compile(r"npm\s+run\s+([A-Za-z0-9:_-]+)")
PYTHON_FILE = re.compile(r"(?:^|\s)(?:py\s+-3(?:\s+-B)?|python)\s+([^\s]+\.py)(?:\s|$)")
TEXT_SUFFIXES = {
    ".bat",
    ".cjs",
    ".cmd",
    ".cs",
    ".json",
    ".jsonl",
    ".md",
    ".mjs",
    ".props",
    ".ps1",
    ".py",
    ".sh",
    ".slnx",
    ".targets",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xaml",
    ".xml",
    ".yaml",
    ".yml",
}
ACTIVE_DOCS = ACTIVE_MARKDOWN_FILES
RUNTIME_HELPERS = {
    "test:runtime-profile-helper-safety",
    "test:runtime-cdb-helper-safety",
    "test:winui-safe-copy-live-runtime-smoke-helper",
}
READINESS_COMMANDS = {
    "test:winui-original-binary-second-host-live-readiness",
    "test:winui-original-binary-second-host-live-run-kit",
    "test:winui-original-binary-second-host-command-source",
    "test:winui-original-binary-host-join-enablement",
}
REMOVED_ALIASES = {
    "test:winui-copied-game-preflight",
    "test:winui-copied-game-runtime",
    "test:winui-copied-game-music-replacement",
}
EXPECTED_QUICK_DEPENDENCIES = {
    "test:validation-inventory",
    "test:docsync",
    "test:doc-commands",
    "test:md-links:public-core",
    "test:generated-output-safety",
    "test:winui-primary-lane",
    "test:rebuild",
}


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def npm_dependencies(command: str) -> list[str]:
    return sorted(set(NPM_RUN.findall(command)))


def classify_script(name: str) -> str:
    if name.startswith("archive:"):
        return "archive"
    if name.startswith("test:ghidra-") or name.startswith("test:wave"):
        return "historical-proof"
    if (
        name == "test:winui-copied-profile-runtime"
        or name == "test:winui-safe-copy-runtime"
        or name.startswith("test:winui-original-binary-")
    ):
        return "runtime-proof"
    if name in RUNTIME_HELPERS or name == "test:runtime-tooling-safety":
        return "runtime-tooling"
    if "rebuild" in name:
        return "rebuild"
    if name.startswith("release:") or any(
        token in name for token in ("zip-release", "installer", "msix", "notices")
    ):
        return "release-publication"
    if any(token in name for token in ("payload", "public-allowlist", "migration-inventory", "provenance")):
        return "payload-provenance"
    if any(token in name for token in ("docsync", "doc-commands", "md-links")):
        return "docs"
    if name.startswith(("build:winui", "build:cli", "build:host", "test:appcore", "test:winui")):
        return "appcore-winui"
    return "other"


def line_references(text: str, known_scripts: set[str]) -> Iterable[tuple[int, str]]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        for name in NPM_RUN.findall(line):
            if name in known_scripts:
                yield line_number, name


def git_npm_references(root: Path, known_scripts: set[str]) -> list[tuple[str, int, str]]:
    result = subprocess.run(
        [
            "git",
            "grep",
            "-I",
            "-n",
            "-E",
            r"npm[[:space:]]+run[[:space:]]+[A-Za-z0-9:_-]+",
            "--",
        ],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or "git grep failed")
    references: list[tuple[str, int, str]] = []
    for raw_line in result.stdout.splitlines():
        parts = raw_line.split(":", 2)
        if len(parts) != 3:
            continue
        path, raw_line_number, text = parts
        try:
            line_number = int(raw_line_number)
        except ValueError:
            continue
        for name in NPM_RUN.findall(text):
            if name in known_scripts:
                references.append((normalize(path), line_number, name))
    return references


def command_python_files(command: str) -> list[str]:
    return [normalize(match.strip().strip('"\'')) for match in PYTHON_FILE.findall(command)]


def reachable(roots: Iterable[str], edges: dict[str, list[str]]) -> set[str]:
    seen: set[str] = set()
    stack = [root for root in roots if root in edges]
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        seen.add(name)
        stack.extend(edges.get(name, ()))
    return seen


def find_cycles(edges: dict[str, list[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visiting: list[str] = []
    active: set[str] = set()
    finished: set[str] = set()

    def visit(name: str) -> None:
        if name in finished:
            return
        if name in active:
            start = visiting.index(name)
            cycles.append(visiting[start:] + [name])
            return
        active.add(name)
        visiting.append(name)
        for child in edges.get(name, ()):
            visit(child)
        visiting.pop()
        active.remove(name)
        finished.add(name)

    for name in edges:
        visit(name)
    return cycles


def build_inventory(
    root: Path,
    package_path: Path,
    *,
    active_docs: tuple[str, ...] = ACTIVE_DOCS,
    tracked_paths: tuple[str, ...] | None = None,
) -> dict[str, object]:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    raw_scripts = package.get("scripts", {})
    if not isinstance(raw_scripts, dict):
        raise ValueError("package.json scripts must be an object")
    scripts = {str(name): str(command) for name, command in raw_scripts.items()}
    names = set(scripts)
    declared_dependencies = {
        name: npm_dependencies(command) for name, command in scripts.items()
    }
    edges = {
        name: [dependency for dependency in dependencies if dependency in names]
        for name, dependencies in declared_dependencies.items()
    }
    unknown_dependencies = {
        name: [dependency for dependency in dependencies if dependency not in names]
        for name, dependencies in declared_dependencies.items()
    }
    callers: dict[str, list[str]] = {name: [] for name in scripts}
    for caller, dependencies in edges.items():
        for dependency in dependencies:
            callers[dependency].append(caller)

    command_groups: dict[str, list[str]] = defaultdict(list)
    for name, command in scripts.items():
        command_groups[command].append(name)
    duplicate_groups = [sorted(group) for group in command_groups.values() if len(group) > 1]
    duplicate_groups.sort(key=lambda group: (-len(group), group))
    duplicate_peers: dict[str, list[str]] = {name: [] for name in scripts}
    for group in duplicate_groups:
        for name in group:
            duplicate_peers[name] = [peer for peer in group if peer != name]

    active_set = set(active_docs)
    active_refs: dict[str, list[str]] = defaultdict(list)
    historical_doc_counts: Counter[str] = Counter()
    source_refs: dict[str, list[str]] = defaultdict(list)
    text_cache: dict[str, str] = {}

    package_rel = normalize(str(package_path.relative_to(root)))
    if tracked_paths is None:
        references = git_npm_references(root, names)
        for active_path in active_docs:
            full_path = root / active_path
            if not full_path.is_file():
                continue
            references = [item for item in references if item[0] != active_path]
            text = full_path.read_text(encoding="utf-8", errors="replace")
            text_cache[active_path] = text
            references.extend(
                (active_path, line_number, name)
                for line_number, name in line_references(text, names)
            )
    else:
        references = []
        for raw_path in tracked_paths:
            path = normalize(raw_path)
            full_path = root / path
            if not full_path.is_file() or full_path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = full_path.read_text(encoding="utf-8", errors="replace")
            text_cache[path] = text
            references.extend(
                (path, line_number, name)
                for line_number, name in line_references(text, names)
            )

    for path, line_number, name in references:
        if path == package_rel:
            continue
        reference = f"{path}:{line_number}"
        if Path(path).suffix.lower() == ".md":
            if path in active_set:
                active_refs[name].append(reference)
            else:
                historical_doc_counts[name] += 1
        else:
            source_refs[name].append(reference)

    profile_roots = {
        "quick": ("check:quick",),
        "runtimeToolingSafety": ("test:runtime-tooling-safety",),
        "historicalRuntimeProof": ("test:winui-copied-profile-runtime",),
        "publicBoundary": ("test:public-allowlist",),
        "releasePublication": (
            "test:winui-zip-release-candidate-probe",
            "test:winui-notices",
            "release:profile-check",
            "release:curated-check",
        ),
    }
    profile_reachability = {
        profile: sorted(reachable(roots, edges)) for profile, roots in profile_roots.items()
    }
    quick_set = set(profile_reachability["quick"])
    runtime_set = set(profile_reachability["runtimeToolingSafety"])
    release_set = set(profile_reachability["releasePublication"])
    runtime_proof_set = (
        set(profile_reachability["historicalRuntimeProof"]) - RUNTIME_HELPERS
    )

    script_rows: list[dict[str, object]] = []
    for name in sorted(scripts):
        self_binding = False
        for tool_path in command_python_files(scripts[name]):
            text = text_cache.get(tool_path)
            if text is None:
                full_path = root / tool_path
                if full_path.is_file():
                    text = full_path.read_text(encoding="utf-8", errors="replace")
            if text is not None and name in text:
                self_binding = True
                break

        family = "runtime-proof" if name in runtime_proof_set else classify_script(name)
        if name in quick_set:
            status = "routine"
        elif name in runtime_set:
            status = "active-safety"
        elif name in release_set:
            status = "release-only"
        elif family == "runtime-proof" and (active_refs[name] or source_refs[name]):
            status = "active-runtime-proof"
        elif family == "historical-proof" and (active_refs[name] or source_refs[name]):
            status = "active-command"
        elif family in {"historical-proof", "runtime-proof"}:
            status = "historical-retained"
        elif active_refs[name] or source_refs[name] or callers[name]:
            status = "active-command"
        else:
            status = "standalone-retained"

        script_rows.append(
            {
                "name": name,
                "command": scripts[name],
                "family": family,
                "status": status,
                "npmDependencies": edges[name],
                "unknownDependencies": unknown_dependencies[name],
                "packageCallers": sorted(callers[name]),
                "duplicateCommandPeers": duplicate_peers[name],
                "activeDocReferences": sorted(active_refs[name]),
                "historicalDocReferenceCount": historical_doc_counts[name],
                "sourceReferences": sorted(source_refs[name]),
                "selfBinding": self_binding,
            }
        )

    family_counts = Counter(str(row["family"]) for row in script_rows)
    status_counts = Counter(str(row["status"]) for row in script_rows)
    return {
        "schemaVersion": 1,
        "source": normalize(str(package_path.relative_to(root))),
        "summary": {
            "scriptCount": len(scripts),
            "edgeCount": sum(len(children) for children in edges.values()),
            "unknownDependencyCount": sum(
                len(children) for children in unknown_dependencies.values()
            ),
            "duplicateCommandGroupCount": len(duplicate_groups),
            "familyCounts": dict(sorted(family_counts.items())),
            "statusCounts": dict(sorted(status_counts.items())),
        },
        "profiles": {
            profile: {"roots": list(profile_roots[profile]), "reachable": reachable_names}
            for profile, reachable_names in profile_reachability.items()
        },
        "duplicateCommandGroups": duplicate_groups,
        "cycles": find_cycles(edges),
        "scripts": script_rows,
    }


def quick_profile_forbidden(inventory: dict[str, object]) -> list[str]:
    rows = inventory["scripts"]
    assert isinstance(rows, list)
    scripts = {str(row["name"]): row for row in rows if isinstance(row, dict)}
    profiles = inventory["profiles"]
    quick = set(profiles["quick"]["reachable"])
    proof = set(profiles["historicalRuntimeProof"]["reachable"]) - RUNTIME_HELPERS
    return sorted(
        name
        for name in quick
        if name in proof
        or name.startswith(("run:", "setup:"))
        or scripts[name]["family"] in {
            "historical-proof",
            "runtime-proof",
            "payload-provenance",
            "release-publication",
        }
        or name in {"test:repo-hygiene", "test:rebuild-godot-smoke"}
    )


def validate_repository_contracts(inventory: dict[str, object], root: Path) -> list[str]:
    rows = inventory["scripts"]
    assert isinstance(rows, list)
    scripts = {str(row["name"]): row for row in rows if isinstance(row, dict)}
    errors: list[str] = []

    cycles = inventory.get("cycles", [])
    if cycles:
        errors.append(f"package dependency cycles found: {cycles}")

    unknown = {
        name: row["unknownDependencies"]
        for name, row in scripts.items()
        if row["unknownDependencies"]
    }
    if unknown:
        errors.append(f"unknown package dependencies found: {unknown}")

    quick_row = scripts.get("check:quick")
    quick_dependencies = set(quick_row["npmDependencies"]) if quick_row else set()
    if quick_dependencies != EXPECTED_QUICK_DEPENDENCIES:
        errors.append(
            "quick profile direct dependencies must be exactly: "
            + ", ".join(sorted(EXPECTED_QUICK_DEPENDENCIES))
        )
    forbidden_quick = quick_profile_forbidden(inventory)
    if forbidden_quick:
        errors.append(f"quick profile reaches non-routine gates: {', '.join(forbidden_quick)}")

    runtime_row = scripts.get("test:runtime-tooling-safety")
    runtime_dependencies = set(runtime_row["npmDependencies"]) if runtime_row else set()
    if runtime_dependencies != RUNTIME_HELPERS:
        errors.append(
            "runtime-tooling safety profile must call exactly: "
            + ", ".join(sorted(RUNTIME_HELPERS))
        )

    for command in sorted(READINESS_COMMANDS):
        row = scripts.get(command)
        if row is None:
            errors.append(f"missing AppCore-emitted readiness command: {command}")
        elif not any(
            str(reference).startswith("OnslaughtCareerEditor.AppCore/")
            for reference in row["sourceReferences"]
        ):
            errors.append(f"readiness command lacks AppCore source reference: {command}")
        elif row["status"] != "active-runtime-proof":
            errors.append(f"readiness command is not classified active: {command}")

    present_removed = sorted(REMOVED_ALIASES & set(scripts))
    if present_removed:
        errors.append(f"proven-unreferenced aliases remain: {', '.join(present_removed)}")

    allowlist = scripts.get("test:public-allowlist")
    if allowlist is None:
        errors.append("missing test:public-allowlist")
    else:
        command = str(allowlist["command"])
        if command.count("public_allowlist_safety_check.py") != 2:
            errors.append("public allowlist must run one scanner self-test and one root+submodule scan")
        if "--self-test" not in command or "--include-submodules" not in command:
            errors.append("public allowlist must retain self-test and submodule-aware root scan")
        if set(allowlist["npmDependencies"]) != {"test:public-primary-migration-inventory"}:
            errors.append("public allowlist must call only migration inventory through npm")

    public_package_path = root / "release" / "readiness" / "public_package.json"
    if public_package_path.is_file():
        public_scripts = json.loads(public_package_path.read_text(encoding="utf-8")).get("scripts", {})
        public_quick = set(NPM_RUN.findall(str(public_scripts.get("check:quick", ""))))
        if "test:winui-primary-lane" not in public_quick:
            errors.append("public package quick profile must use test:winui-primary-lane")
        if public_quick & {"build:winui", "test:appcore", "test:winui"}:
            errors.append("public package quick profile repeats primary-lane component gates")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--package", type=Path, default=Path("package.json"))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true", help="Write the full inventory JSON to stdout.")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    package_path = args.package if args.package.is_absolute() else root / args.package
    inventory = build_inventory(root, package_path)
    errors = validate_repository_contracts(inventory, root)

    if args.json:
        print(json.dumps(inventory, indent=2, sort_keys=True))
    if args.check or not args.json:
        if errors:
            print("Validation inventory: FAIL", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        summary = inventory["summary"]
        print("Validation inventory: PASS")
        print(f"Scripts: {summary['scriptCount']}")
        print(f"NPM dependency edges: {summary['edgeCount']}")
        print(f"Duplicate command groups: {summary['duplicateCommandGroupCount']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
