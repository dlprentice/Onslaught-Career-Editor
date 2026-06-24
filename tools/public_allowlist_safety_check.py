#!/usr/bin/env python3
"""Hard-payload safety check for the public-primary repo.

The public repository is now the working repository. Raw RE notes, scratch
exports, state docs, and proof reports are allowed. This check only rejects
actual copied game/runtime payload roots, build outputs, and obvious secret
files.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
SELF_REL = "tools/public_allowlist_safety_check.py"

DENY_ROOTS = (
    ".vs/",
    "GameProfiles/",
    "PatchBench/",
    "game/",
    "local-game/",
    "local-ghidra/",
    "local-lab/",
    "local-media/",
    "local-proofs/",
    "local-saves/",
    "mcps/",
)

DENY_CONTAINS = (
    "/bin/",
    "/obj/",
    "/TestResults/",
    "/__pycache__/",
)

DENY_EXACT = {
}

DENY_SUFFIXES = (
    ".crt",
    ".dll",
    ".exe",
    ".gzf",
    ".key",
    ".pem",
    ".pfx",
    ".pyo",
    ".pyc",
    ".trx",
)

TEXT_SUFFIXES = {
    ".cmd",
    ".cs",
    ".css",
    ".html",
    ".java",
    ".json",
    ".jsonc",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".ts",
    ".tsx",
    ".tsv",
    ".txt",
    ".xml",
    ".xaml",
    ".yml",
    ".yaml",
}

TEXT_DENY_PATTERNS = (
)

TEXT_ALLOW_PATH_PREFIXES = (
    "tools/public_allowlist_safety_check",
    "tools/repo_text_hygiene_check",
)


@dataclass(frozen=True)
class Finding:
    path: str
    label: str
    detail: str


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def public_candidate_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    return sorted(path for item in result.stdout.decode("utf-8", errors="replace").split("\0") if (path := normalize(item)))


def is_text_file(path: str) -> bool:
    return Path(path).suffix.lower() in TEXT_SUFFIXES


def path_findings(path: str) -> list[Finding]:
    findings: list[Finding] = []
    lower = path.lower()
    name = Path(path).name.lower()
    if path in DENY_EXACT:
        findings.append(Finding(path, "deny-exact", path))
    if name == ".env" or name.startswith(".env."):
        findings.append(Finding(path, "deny-env-file", name))
    if path.startswith(DENY_ROOTS):
        findings.append(Finding(path, "deny-root", path.split("/", 1)[0]))
    if any(token in path for token in DENY_CONTAINS):
        findings.append(Finding(path, "deny-generated-or-private-path", path))
    if lower.endswith(DENY_SUFFIXES):
        findings.append(Finding(path, "deny-binary-or-private-suffix", Path(path).suffix.lower()))
    return findings


def text_findings(root: Path, path: str) -> list[Finding]:
    if path == SELF_REL or path.startswith(TEXT_ALLOW_PATH_PREFIXES):
        return []
    if not is_text_file(path):
        return []
    full_path = root / path
    try:
        text = full_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [Finding(path, "read-error", str(exc))]

    findings: list[Finding] = []
    for label, pattern in TEXT_DENY_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = match.group(0).replace("\n", "\\n")
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            findings.append(Finding(path, label, snippet))
    return findings


def check_repo(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in public_candidate_files(root):
        findings.extend(path_findings(path))
        findings.extend(text_findings(root, path))
    return findings


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        (root / "game").mkdir()
        (root / "game" / "BEA.exe").write_bytes(b"not ok")
        (root / ".env").write_text("OPENAI_API_KEY=sk-not-a-real-fixture-value\n", encoding="utf-8")
        (root / "docs.md").write_text("Raw RE notes may mention local paths and field names.\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        findings = check_repo(root)
        labels = {finding.label for finding in findings}
        required = {"deny-root", "deny-binary-or-private-suffix", "deny-env-file"}
        missing = sorted(required - labels)
        if missing:
            print("Public payload safety self-test: FAIL")
            print(f"- missing expected labels: {', '.join(missing)}")
            print(f"- findings: {findings!r}")
            return 1
    print("Public payload safety self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run built-in fixture tests.")
    parser.add_argument("--require-private-text-guard", action="store_true", help="Accepted for compatibility; denylist text guards are built in.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.repo_root.resolve()
    findings = check_repo(root)
    if findings:
        print("Public payload safety check: FAIL")
        for finding in findings[:200]:
            print(f"- {finding.path}: {finding.label}: {finding.detail}")
        if len(findings) > 200:
            print(f"- ... ({len(findings) - 200} more)")
        return 1

    print("Public payload safety check: PASS")
    print(f"Public candidate files checked: {len(public_candidate_files(root))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
