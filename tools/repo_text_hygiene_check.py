#!/usr/bin/env python3
"""Catch high-risk stale text that should not re-enter tracked files."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = "tools/repo_text_hygiene_check.py"

TEXT_SUFFIXES = {
    ".cjs",
    ".cs",
    ".css",
    ".html",
    ".json",
    ".jsonc",
    ".jsonl",
    ".java",
    ".md",
    ".patch",
    ".ps1",
    ".py",
    ".sh",
    ".ts",
    ".tsx",
    ".tsv",
    ".txt",
    ".csv",
    ".xml",
    ".xaml",
    ".yml",
    ".yaml",
}

WINDOWS_USER_ROOT_PATTERN_TEXT = r"C:\\{1,2}Users\\{1,2}[A-Za-z0-9._-]+"
WSL_USER_ROOT_PATTERN_TEXT = r"/mnt/c/[Uu]sers/[A-Za-z0-9._-]+"
LINUX_USER_ROOT_PATTERN_TEXT = r"(?-i:/home/[a-z][a-z0-9._-]*(?=/|$))"
MAINTAINER_USER_ROOT_PATTERN = re.compile(
    rf"(?:{WINDOWS_USER_ROOT_PATTERN_TEXT}|C:/Users/[A-Za-z0-9._-]+|{WSL_USER_ROOT_PATTERN_TEXT}|{LINUX_USER_ROOT_PATTERN_TEXT})",
    re.IGNORECASE,
)
MAINTAINER_LOCAL_ROOT_PATTERN = re.compile(
    r"(?:[A-Z]:\\{1,4}GhidraBackups|[A-Z]:/GhidraBackups|"
    r"[A-Z]:\\{1,4}GhydraMCP(?:-[^\\\s\"'<>|,)\\]]*)?|[A-Z]:/GhydraMCP(?:-[^/\s\"'<>|,)\\]]*)?|"
    r"[A-Z]:\\{1,4}OnslaughtRuntimeProof(?:s|Archive)?|[A-Z]:/OnslaughtRuntimeProof(?:s|Archive)?|"
    r"[A-Z]:\\{1,4}dev\\{1,4}ONSLAUGHT2|[A-Z]:/dev/ONSLAUGHT2)",
    re.IGNORECASE,
)
STANDALONE_BACKUP_DRIVE_REF_TEXT = r"(?<![A-Za-z0-9_])[D-Z]:(?![A-Za-z0-9_\\/])"
BACKUP_DRIVE_CONTEXT_WORD_TEXT = (
    r"(?i:backup|backed up|verified|verification|availability|unavailable|drive|volume|storage)"
)
STANDALONE_BACKUP_DRIVE_PATTERN = re.compile(
    rf"(?:`{STANDALONE_BACKUP_DRIVE_REF_TEXT}`|"
    rf"{BACKUP_DRIVE_CONTEXT_WORD_TEXT}[^\n]{{0,120}}{STANDALONE_BACKUP_DRIVE_REF_TEXT}|"
    rf"{STANDALONE_BACKUP_DRIVE_REF_TEXT}[^\n]{{0,120}}"
    rf"{BACKUP_DRIVE_CONTEXT_WORD_TEXT})"
)
PRIVATE_REPO_ROOT_PATTERN = re.compile(
    rf"(?:{WINDOWS_USER_ROOT_PATTERN_TEXT}\\{{1,2}}source\\{{1,2}}Onslaught-Career-Editor-private|C:/Users/[A-Za-z0-9._-]+/source/Onslaught-Career-Editor-private|{WSL_USER_ROOT_PATTERN_TEXT}/source/Onslaught-Career-Editor-private|{LINUX_USER_ROOT_PATTERN_TEXT}/source/Onslaught-Career-Editor-private)",
    re.IGNORECASE,
)
@dataclass(frozen=True)
class TextRule:
    label: str
    pattern: re.Pattern[str]
    path_prefix: str | None = None
    include_path_prefixes: tuple[str, ...] = ()
    exclude_path_prefixes: tuple[str, ...] = ()

    def applies_to(self, path: str) -> bool:
        if any(path.startswith(prefix) for prefix in self.exclude_path_prefixes):
            return False
        if self.include_path_prefixes and not any(path.startswith(prefix) for prefix in self.include_path_prefixes):
            return False
        return self.path_prefix is None or path.startswith(self.path_prefix)


@dataclass(frozen=True)
class PathRule:
    label: str
    pattern: re.Pattern[str]
    exclude_path_prefixes: tuple[str, ...] = ()

    def applies_to(self, path: str) -> bool:
        return not any(path.startswith(prefix) for prefix in self.exclude_path_prefixes)


PATH_RULES = (
    PathRule(
        "tracked-generated-build-or-test-output",
        re.compile(
            r"(^|/)(bin|obj|dist|TestResults|AppPackages|BundleArtifacts|MsixPackages|publish)/|"
            r"(^|/)release/artifacts/|"
            r"\.(trx|tsbuildinfo|pyc|pyo|log)$",
            re.IGNORECASE,
        ),
        exclude_path_prefixes=(
            "game/",
            "media/",
            "save-attempts/",
            "subagents/",
            "release/readiness/private_runtime_evidence/",
        ),
    ),
    PathRule(
        "legacy-winui-bundle-helper-in-active-release-dir",
        re.compile(r"^release/(Build-PortableBundle\.ps1|BUNDLE-LAUNCHER\.cmd|BUNDLE-README\.MD)$", re.IGNORECASE),
    ),
)

REQUIRED_TEXT_MARKERS = (
    (
        "onslaught_codex_directive.md",
        "private-directive-superseded-banner",
        "Status: superseded historical directive",
    ),
)


RULES = (
    TextRule(
        "visible-mojibake-marker",
        re.compile(r"\u00c3|\u00c2|\ufffd|\u00e2[\u0080-\u00bf]|[\uf000-\uf8ff]"),
        include_path_prefixes=(
            ".gitignore",
            "AGENTS.md",
            "README.MD",
            "CURRENT_CAPABILITIES.md",
            "README.RELEASE.md",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/",
            "roadmap/",
            "lore-book/",
            "reverse-engineering/",
            "packages/",
            "apps/",
            "tools/",
            "archive/",
        ),
    ),
    TextRule(
        "unresolved-evidence-report-commit-placeholder",
        re.compile(r"Evidence-report commit:\s*assigned by the commit containing this file", re.IGNORECASE),
    ),
    TextRule(
        "split-evidence-report-commit-line",
        re.compile(r"^Evidence-report commit:\s*$", re.IGNORECASE | re.MULTILINE),
    ),
    TextRule(
        "unresolved-post-review-fix-placeholder",
        re.compile(r"Post-review fix commit:\s*<[^>\n]+>", re.IGNORECASE),
    ),
    TextRule(
        "sandbox-attachment-link",
        re.compile("sandbox:" + r"/mnt/data/", re.IGNORECASE),
    ),
    TextRule(
        "archive-doc-private-repo-root-path",
        PRIVATE_REPO_ROOT_PATTERN,
        include_path_prefixes=("archive/",),
    ),
    TextRule(
        "tracked-private-repo-root-path",
        PRIVATE_REPO_ROOT_PATTERN,
        include_path_prefixes=(
            "developer_agent_state.json",
            "documentation_agent_state.json",
            "lore-book/",
            "MCP_DEBUGGING_OPTIONS.md",
            "re_orchestrator_state.json",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "reverse-engineering/",
            "roadmap/",
        ),
        exclude_path_prefixes=("release/readiness/private_runtime_evidence/",),
    ),
    TextRule(
        "tracked-maintainer-user-root-path",
        MAINTAINER_USER_ROOT_PATTERN,
        include_path_prefixes=(
            "developer_agent_state.json",
            "documentation_agent_state.json",
            "lore-book/",
            "MCP_DEBUGGING_OPTIONS.md",
            "re_orchestrator_state.json",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "reverse-engineering/",
            "roadmap/",
        ),
    ),
    TextRule(
        "tracked-maintainer-local-root-path",
        MAINTAINER_LOCAL_ROOT_PATTERN,
        include_path_prefixes=(
            "developer_agent_state.json",
            "documentation_agent_state.json",
            "lore-book/",
            "MCP_DEBUGGING_OPTIONS.md",
            "re_orchestrator_state.json",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "reverse-engineering/",
            "roadmap/",
        ),
    ),
    TextRule(
        "tracked-maintainer-backup-drive-reference",
        STANDALONE_BACKUP_DRIVE_PATTERN,
        include_path_prefixes=(
            "developer_agent_state.json",
            "documentation_agent_state.json",
            "lore-book/",
            "MCP_DEBUGGING_OPTIONS.md",
            "re_orchestrator_state.json",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "reverse-engineering/",
            "roadmap/",
        ),
    ),
    TextRule(
        "stale-current-consult-stack-requires-gemini-opus",
        re.compile(r"Grok(?:,\s*Grok Composer| Composer)?,\s*Opus,\s*and\s*Gemini\s+consults", re.IGNORECASE),
        include_path_prefixes=(
            "developer_agent_state.json",
            "documentation_agent_state.json",
            "lore-book/roadmap/",
            "re_orchestrator_state.json",
            "roadmap/",
        ),
    ),
    TextRule(
        "top-level-fixture-parity-shorthand",
        re.compile(r"fixture-proven|fixture parity", re.IGNORECASE),
        include_path_prefixes=("README.MD", "CURRENT_CAPABILITIES.md", "README.RELEASE.md", "RELEASE_SCOPE_AND_TEST_COMMANDS.md"),
    ),
    TextRule(
        "stale-repo-hygiene-text-only-description",
        re.compile(
            r"test:repo-hygiene` scans tracked text files|"
            r"test:repo-hygiene` passes for tracked stale-placeholder and renderer preview-mode copy regressions",
            re.IGNORECASE,
        ),
        include_path_prefixes=(
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
        ),
    ),
    TextRule(
        "stale-game-harness-browser-fixture-signoff",
        re.compile(r"Game Harness can prepare a copied profile through the browser " r"fixture", re.IGNORECASE),
    ),
    TextRule(
        "stale-winui-archived-product-claim",
        re.compile(
            r"`?OnslaughtCareerEditor\.WinUI`?[^\n]{0,120}(?:archiv(?:e|ed|ing)|non-expanding|historical product surface)|"
            r"(?:archiv(?:e|ed|ing)|non-expanding|historical product surface)[^\n]{0,120}`?OnslaughtCareerEditor\.WinUI`?",
            re.IGNORECASE,
        ),
        include_path_prefixes=(
            "AGENTS.md",
            "README.MD",
            "CURRENT_CAPABILITIES.md",
            "README.RELEASE.md",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "roadmap/",
            "lore-book/roadmap/",
        ),
    ),
    TextRule(
        "stale-maladim-no-effect-claim",
        re.compile(r"(?:Maladim[^\n]{0,160}(?:no effect|not working)|no god mode effect|User reports no effect)", re.IGNORECASE),
        include_path_prefixes=(
            "AGENTS.md",
            "README.MD",
            "CURRENT_CAPABILITIES.md",
            "README.RELEASE.md",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "roadmap/",
            "lore-book/roadmap/",
            "reverse-engineering/",
            "lore-book/reverse-engineering/",
        ),
    ),
    TextRule(
        "stale-maladim-unrevalidated-hypothesis",
        re.compile(
            r"Candidate effects \(unrevalidated\)[^\n]{0,240}Maladim|"
            r"Maladim=god mode[^\n]{0,160}unrevalidated",
            re.IGNORECASE,
        ),
        include_path_prefixes=(
            "AGENTS.md",
            "README.MD",
            "CURRENT_CAPABILITIES.md",
            "README.RELEASE.md",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "roadmap/",
            "lore-book/roadmap/",
            "reverse-engineering/",
            "lore-book/reverse-engineering/",
        ),
    ),
    TextRule(
        "stale-save-god-mode-no-effect-comment",
        re.compile(
            r"God mode patching[^\n]{0,120}none of the encodings worked|"
            r"None had any effect[^\n]{0,120}(?:stripped|disabled)",
            re.IGNORECASE,
        ),
        include_path_prefixes=(
            "OnslaughtCareerEditor.AppCore/",
            "reverse-engineering/",
            "lore-book/reverse-engineering/",
        ),
    ),
    TextRule(
        "stale-goodie-78-developer-item-claim",
        re.compile(
            r"\|\s*78\s*\|\s*First concept art\s*\|\s*43\s*\||"
            r"Goodie\s+78[^\n]{0,180}(?:requires\s+43|S-rank|S-ranks|43 S|43-rank)",
            re.IGNORECASE,
        ),
        include_path_prefixes=(
            "AGENTS.md",
            "README.MD",
            "CURRENT_CAPABILITIES.md",
            "README.RELEASE.md",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "roadmap/",
            "lore-book/roadmap/",
            "reverse-engineering/",
            "lore-book/reverse-engineering/",
        ),
    ),
    TextRule(
        "stale-battleengine-transform-method-name",
        re.compile(r"CBattleEngine::Transform"),
        include_path_prefixes=(
            "AGENTS.md",
            "README.MD",
            "CURRENT_CAPABILITIES.md",
            "README.RELEASE.md",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "roadmap/",
            "lore-book/roadmap/",
            "reverse-engineering/",
            "lore-book/reverse-engineering/",
            "tools/",
        ),
    ),
    TextRule(
        "stale-electron-migration-status-label",
        re.compile(
            r"Status:\s+active(?:\s+Electron)?\s+migration\b|"
            r"\bElectron migration candidate\b|"
            r"\bElectron migration workspace\b|"
            r"\bmigration release candidate\b|"
            r"\bMigration-ready means\b|"
            r"\bMandatory Migration Gates\b|"
            r"\bcurated Electron migration allowlist\b|"
            r"\bActive product migration\b|"
            r"\bSuperseded by Electron migration\b|"
            r"\bElectron migration:\s*\[|"
            r"\bElectron migration/product architecture\b|"
            r"\bactive Electron " r"migration bundle\b|"
            r"\bactive product " r"migration surface\b|"
            r"^#\s+Electron workbench migration\b|"
            r"\bElectron-first Onslaught Toolkit " r"migration\b|"
            r"\bfuture application surface is an Electron\b|"
            r"\bparity (?:and reference )?surfaces during migration\b|"
            r"\bElectron workbench migration\b",
            re.IGNORECASE,
        ),
        include_path_prefixes=(
            "AGENTS.md",
            "package.json",
            "README.MD",
            "CURRENT_CAPABILITIES.md",
            "README.RELEASE.md",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "archive/electron-workbench/release/ELECTRON-BUNDLE-README.MD",
            "release/BUNDLE-README.MD",
            "release/BUNDLE-LAUNCHER.cmd",
            "release/Build-PortableBundle.ps1",
            "archive/README.md",
            "roadmap/ROADMAP-INDEX.md",
            "lore-book/roadmap/ROADMAP-INDEX.md",
            "roadmap/agent-workflow.md",
            "lore-book/roadmap/agent-workflow.md",
            "roadmap/electron-workbench-migration.md",
            "lore-book/roadmap/electron-workbench-migration.md",
            "roadmap/app-delivery-phases.md",
            "lore-book/roadmap/app-delivery-phases.md",
            "roadmap/technical-debt.md",
            "lore-book/roadmap/technical-debt.md",
        ),
    ),
    TextRule(
        "stale-lore-catalog-migration-title",
        re.compile(r'title:\s*"(?:Electron|Workbench) migration"', re.IGNORECASE),
        include_path_prefixes=(
            "archive/electron-workbench/apps/electron/src/content-browser.ts",
            "archive/electron-workbench/packages/ui/src/lib/mock-data.ts",
        ),
    ),
    TextRule(
        "stale-electron-release-future-model",
        re.compile(
            r"The next public release model should be Electron-first|"
            r"release authority must move from WinUI/CLI to Electron packaging|"
            r"Electron release packaging and bundle smoke must become the final authority",
            re.IGNORECASE,
        ),
        include_path_prefixes=(
            "README.RELEASE.md",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
        ),
    ),
    TextRule(
        "stale-state-electron-current-authority",
        re.compile(
            r"Electron packaging lane is current|"
            r"Electron packaging/bundle smoke as present-tense portable-app release authority|"
            r"normal desktop dev launch|"
            r"Archive move batch pending review/commit|"
            r"Asset extraction docs and (?:the export-game-assets summary )?now (?:say|point to) Electron workbench integration",
            re.IGNORECASE,
        ),
        include_path_prefixes=(
            "developer_agent_state.json",
            "documentation_agent_state.json",
        ),
    ),
    TextRule(
        "stale-open-winui-doc-supersession-debt",
        re.compile(r"- \[ \] Mark historical WinUI/AppCore/CLI planning docs as superseded instead of active\."),
        include_path_prefixes=(
            "roadmap/technical-debt.md",
            "lore-book/roadmap/technical-debt.md",
        ),
    ),
    TextRule(
        "stale-operator-community-app-label",
        re.compile(
            r"Electron is the active operator/community " r"app\.|"
            r"Operator/community desktop " r"app|"
            r"Useful for " r"operators",
            re.IGNORECASE,
        ),
        include_path_prefixes=(
            "archive/electron-workbench/apps/electron/src/",
            "roadmap/csharp-python-parity.md",
            "lore-book/roadmap/csharp-python-parity.md",
            "archive/electron-workbench/packages/ui/src/",
        ),
    ),
    TextRule(
        "public-doc-browser-fixture-proof-copy",
        re.compile(
            r"\bbrowser[-\s]+fixtures?\b|"
            r"\bfixture " r"jobs?\b|"
            r"\bfixture " r"surfaces?\b|"
            r"\bfixture " r"bridge\b|"
            r"\bbrowser://" r"fixture/|"
            r"\bstale Vite HMR " r"entry\b|"
            r"\bpre-existing Vite HMR " r"warning\b|"
            r"fixture-" r"only|fixture " r"files|fixture " r"flows|fixture versus native|mocked " r"browser bridge",
            re.IGNORECASE,
        ),
        include_path_prefixes=(
            "AGENTS.md",
            "README.MD",
            "CURRENT_CAPABILITIES.md",
            "README.RELEASE.md",
            "RELEASE_SCOPE_AND_TEST_COMMANDS.md",
            "release/readiness/",
            "roadmap/",
            "lore-book/roadmap/",
        ),
        exclude_path_prefixes=("release/readiness/private_runtime_evidence/",),
    ),
    TextRule(
        "renderer-browser-fixture-user-copy",
        re.compile(r"Browser " r"fixture|Browser mock only|Unknown browser " r"fixture|browser " r"fixture"),
        path_prefix="archive/electron-workbench/packages/ui/src/",
    ),
)


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def tracked_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        raw_paths = result.stdout.decode("utf-8", errors="replace").split("\0")
        files = [
            normalized
            for path in raw_paths
            if path and (ROOT / (normalized := normalize_path(path))).exists()
        ]
        if files:
            return files
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return filesystem_files()


def filesystem_files() -> list[str]:
    files: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = normalize_path(str(path.relative_to(ROOT)))
        if should_skip_filesystem_path(rel):
            continue
        files.append(rel)
    return sorted(files)


def should_skip_filesystem_path(path: str) -> bool:
    skip_prefixes = (
        ".git/",
        ".vs/",
        "node_modules/",
        "subagents/",
        "release/artifacts/",
        "release/out/",
    )
    if path.startswith(skip_prefixes):
        return True
    if "/bin/" in path or "/obj/" in path or "/TestResults/" in path or "__pycache__/" in path:
        return True
    return False


def is_text_file(path: str) -> bool:
    return Path(path).suffix.lower() in TEXT_SUFFIXES


def scan_file(path: str) -> list[str]:
    full_path = ROOT / path
    try:
        text = full_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"{path}: unable to read file: {exc}"]

    errors: list[str] = []
    errors.extend(check_required_markers(path, text))
    for rule in RULES:
        if not rule.applies_to(path):
            continue
        for match in rule.pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            snippet = match.group(0).replace("\n", "\\n")
            errors.append(f"{path}:{line}: {rule.label}: {snippet}")
    return errors


def check_required_markers(path: str, text: str) -> list[str]:
    errors: list[str] = []
    for required_path, label, marker in REQUIRED_TEXT_MARKERS:
        if path == required_path and marker not in text:
            errors.append(f"{path}: {label}: missing {marker!r}")
    return errors


def scan_path(path: str) -> list[str]:
    errors: list[str] = []
    for rule in PATH_RULES:
        if rule.applies_to(path) and rule.pattern.search(path):
            errors.append(f"{path}: {rule.label}")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in tracked_files():
        errors.extend(scan_path(path))
        if path != SELF_PATH and is_text_file(path):
            errors.extend(scan_file(path))

    if errors:
        print("Repo text hygiene check: FAIL")
        for error in errors[:200]:
            print(f"- {error}")
        if len(errors) > 200:
            print(f"- ... ({len(errors) - 200} more)")
        return 1

    print("Repo text hygiene check: PASS")
    print(f"Rules checked: {len(RULES)} text, {len(PATH_RULES)} path, {len(REQUIRED_TEXT_MARKERS)} required marker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
