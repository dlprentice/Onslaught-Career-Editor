#!/usr/bin/env python3
"""Validate the internal viewer/editor command-boundary proof plan.

This checker consumes only tracked public Markdown and package metadata. It
does not inspect ignored payload overlays, private manifests, raw proof bundles,
copied executables, live Ghidra state, runtime logs, auth/session/cache data, or
secrets. It validates that the plan remains source-only command-boundary
planning and does not authorize command use, runtime proof, product exposure, or
release work.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "reverse-engineering" / "source-code" / "internal-viewer-editor-command-boundary-proof-plan.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "source-code" / "internal-viewer-editor-command-boundary-proof-plan.md"
VOCAB_MAP = ROOT / "reverse-engineering" / "source-code" / "original-system-internal-tooling-vocabulary-map.md"
SOURCE_INDEX = ROOT / "reverse-engineering" / "source-code" / "_index.md"
LORE_SOURCE_INDEX = ROOT / "lore-book" / "reverse-engineering" / "source-code" / "_index.md"
ENGINE_SYSTEM = ROOT / "reverse-engineering" / "source-code" / "core" / "engine-system.md"
PLATFORM_SYSTEM = ROOT / "reverse-engineering" / "source-code" / "core" / "platform-system.md"
SOURCE_FILE_INVENTORY = ROOT / "reverse-engineering" / "source-code" / "source-file-inventory.md"
CLIPARAMS_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "CLIParams.cpp" / "_index.md"
D3DAPP_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "d3dapp.cpp" / "_index.md"
WINDOWED_MODE = ROOT / "reverse-engineering" / "binary-analysis" / "windowed-mode-analysis.md"
MOD_REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CHAIN_MAP = ROOT / "roadmap" / "rebuild-front-door-chain-map.md"
PACKAGE_JSON = ROOT / "package.json"

PLAN_NAME = "internal-viewer-editor-command-boundary-proof-plan.md"
SCOPE = "internal-viewer-editor-command-boundary"
PACKAGE_SCRIPT = "test:internal-viewer-editor-command-boundary-proof-plan"
PACKAGE_COMMAND = r"py -3 tools\internal_viewer_editor_command_boundary_proof_plan_probe.py --check"
VOCABULARY_COMMAND = r"py -3 tools\original_system_internal_tooling_vocabulary_map_probe.py --check"

REQUIRED_PLAN_TOKENS = (
    "Status: source-only public-safe proof plan, not command authorization",
    f"Scope: `{SCOPE}`",
    "what evidence is required before source/internal viewer and editor vocabulary",
    "`-modelviewer`",
    "`-cutsceneeditor`",
    "The current public-safe proof class is Tier C source vocabulary plus",
    "tracked Tier B static command-boundary docs",
    "not command authorization",
    "not command dispatch",
    "not runtime proof",
    "not evidence that the Steam retail build exposes either tool",
    "Tier C source vocabulary",
    "Tier B static command-boundary docs",
    "Tier A runtime evidence",
    "Current tracked docs keep it source/internal and blocked.",
    "New retail static evidence plus explicit product command-boundary review",
    "No. This plan requires those terms to stay blocked",
    "This checker-backed slice may read only tracked public Markdown and package",
    "run, arm, materialize, dispatch, or recommend any command using these flags",
    "launch BEA",
    "attach CDB",
    "mutate Ghidra",
    "patch an executable",
    "mutate an installed game",
    "add AppCore, WinUI, CLI, release, installer, or packaging support",
    "read ignored payload overlays",
    "publish raw local paths, hashes, private filenames, command traces, or generated payloads",
    "claim runtime behavior, tool availability, visual output, gameplay behavior",
    "source-code indexes link this plan",
    "without changing the active rebuild proof scope",
    "No executable use, product exposure, runtime proof, or release action is",
)

REQUIRED_PLAN_LINK_NAMES = (
    "original-system-internal-tooling-vocabulary-map.md",
    "_index.md",
    "engine-system.md",
    "platform-system.md",
    "source-file-inventory.md",
    "_index.md",
    "_index.md",
    "windowed-mode-analysis.md",
    "mod-patch-runtime-rebuild-register.md",
)

ANCHOR_TOKENS = {
    VOCAB_MAP: (
        "Internal viewer/editor names",
        "Tier C source vocabulary only",
        "flag names are not runnable instructions",
        "Retail flag/static proof and separate command-boundary review before any executable use",
        "Future public-safe slices can use this vocabulary map to pick one bounded",
    ),
    SOURCE_INDEX: (
        "`-modelviewer` / `-cutsceneeditor`",
        "Internal tools (DEV_VERSION)",
        PLAN_NAME,
    ),
    LORE_SOURCE_INDEX: (
        "`-modelviewer` / `-cutsceneeditor`",
        "Internal tools (DEV_VERSION)",
        PLAN_NAME,
    ),
    ENGINE_SYSTEM: (
        "Internal Editor Infrastructure (EditorD3DApp)",
        "Model Viewer",
        "`-modelviewer`",
        "Cutscene Editor",
        "`-cutsceneeditor`",
        "`DEV_VERSION`",
    ),
    PLATFORM_SYSTEM: (
        "`DEV_VERSION`",
        "Fullscreen unless modelviewer/cutsceneeditor",
        "Context menus are disabled in the retail build",
    ),
    SOURCE_FILE_INVENTORY: (
        "EditorD3DApp.cpp",
        "Internal dev tool - stripped",
    ),
    CLIPARAMS_INDEX: (
        "Parameters NOT in Retail",
        "`-modelviewer` - Model viewer",
        "`-cutsceneeditor` - Cutscene editor",
        "does not prove every flag's runtime effect",
    ),
    D3DAPP_INDEX: (
        "D3D application shell",
        "Runtime Direct3D device",
        "remain separate proof",
    ),
    WINDOWED_MODE: (
        "mModelViewer",
        "mCutsceneEditor",
        "startup fullscreen flow",
        "retail branch behavior is confirmed from BEA.exe evidence",
    ),
    MOD_REGISTER: (
        "Source-only/dev/file-writing flags",
        "`-modelviewer`",
        "stay blocked",
        "These are process launch arguments only",
    ),
    CHAIN_MAP: (
        PLAN_NAME,
        "`internal-viewer-editor-boundary`",
        "bounded internal-tooling side guard",
        "not command authorization",
        "does not change the active rebuild proof scope",
    ),
}

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)/(?:home|mnt|var|opt|tmp|users?)/"), "machine-local absolute path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)(?<![A-Za-z0-9-])(?:local-)?game[\\/]"), "private game mirror path"),
    (re.compile(r"(?i)(?<![A-Za-z0-9-])(?:local-)?media[\\/]"), "private media path"),
    (re.compile(r"(?i)save-attempts[\\/]"), "private save path"),
    (re.compile(r"(?i)(?:local-)?proofs?[\\/]"), "private proof path"),
    (re.compile(r"(?i)(?:local-ghidra|ghidra-local)[\\/]"), "private Ghidra path"),
    (re.compile(r"(?i)private_runtime_evidence"), "private runtime evidence marker"),
    (re.compile(r"(?i)capturepath|framepath|capturehash|framebytelength"), "private frame locator field"),
    (re.compile(r"(?i)password|token=|secret="), "secret-like marker"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "raw digest-like value"),
    (re.compile(r"\b[a-fA-F0-9]{40}\b"), "raw digest-like value"),
)

FORBIDDEN_OVERCLAIMS = (
    "command authorized",
    "command authorization complete",
    "command armed successfully",
    "command arming complete",
    "command dispatch complete",
    "command execution complete",
    "shell dispatch complete",
    "modelviewer is supported",
    "cutsceneeditor is supported",
    "steam retail modelviewer",
    "steam retail cutscene editor",
    "tool availability proven",
    "runtime proof complete",
    "runtime proof proven",
    "visual proof complete",
    "gameplay proof complete",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "product exposure approved",
    "appcore allowlist updated",
    "winui support added",
    "release action authorized",
    "ready for execution",
)

LINK_PATTERN = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")


class CommandBoundaryProbeError(ValueError):
    """Raised when the command-boundary plan violates its public-safe contract."""


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CommandBoundaryProbeError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8-sig")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CommandBoundaryProbeError(message)


def normalize_repo_path(path: Path) -> str:
    return path.relative_to(ROOT.resolve()).as_posix()


@lru_cache(maxsize=1)
def tracked_markdown_paths() -> frozenset[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", "*.md"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CommandBoundaryProbeError("failed to enumerate tracked Markdown files with git ls-files") from exc
    paths = frozenset(path for path in result.stdout.decode("utf-8", errors="replace").split("\0") if path)
    require(paths, "git ls-files returned no tracked Markdown files")
    return paths


def check_public_safety(text: str, label: str) -> None:
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{label} leaks forbidden public category: {category}")
    lower = text.lower()
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{label} contains forbidden overclaim phrase: {phrase}")


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def contains_token(text: str, token: str) -> bool:
    return token in text or token in compact(text)


def local_markdown_links(text: str) -> list[str]:
    links: list[str] = []
    for match in LINK_PATTERN.finditer(text):
        target = unquote(match.group(1).strip())
        if target.startswith("#"):
            continue
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
            continue
        links.append(target)
    return links


def resolve_link(source_path: Path, raw_target: str, label: str) -> Path:
    clean_target = raw_target.split("#", 1)[0]
    require(clean_target != "", f"{label} has empty local link target")
    require("\\" not in clean_target, f"{label} uses backslash link target: {raw_target}")
    target_path = Path(clean_target)
    require(not target_path.is_absolute(), f"{label} uses absolute local link target: {raw_target}")
    resolved = (source_path.parent / target_path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise CommandBoundaryProbeError(f"{label} resolves outside repo: {raw_target}") from exc
    return resolved


def check_links_resolve(text: str, source_path: Path) -> None:
    label = str(source_path.relative_to(ROOT))
    links = local_markdown_links(text)
    require(links, f"{label} has no local Markdown links to validate")
    tracked_markdown = tracked_markdown_paths()
    linked_names = [Path(link.split("#", 1)[0]).name for link in links]
    for required_name in REQUIRED_PLAN_LINK_NAMES:
        require(required_name in linked_names, f"{label} missing required link target name: {required_name}")
    for raw_target in links:
        resolved = resolve_link(source_path, raw_target, label)
        relative = normalize_repo_path(resolved)
        require(relative.endswith(".md"), f"{label} local link target is not Markdown: {raw_target}")
        require(relative in tracked_markdown, f"{label} local link target is not tracked public Markdown: {raw_target}")
        require(resolved.is_file(), f"{label} tracked Markdown link does not resolve: {raw_target}")


def check_plan_text(text: str, label: str) -> None:
    check_public_safety(text, label)
    for token in REQUIRED_PLAN_TOKENS:
        require(contains_token(text, token), f"{label} missing required token: {token}")
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in text.lower(), f"{label} contains forbidden overclaim phrase: {phrase}")
    require("| Tier C source vocabulary |" in text, f"{label} missing Tier C table row")
    require("| Tier B static command-boundary docs |" in text, f"{label} missing Tier B table row")
    require("| Tier A runtime evidence | Not used in this slice. |" in text, f"{label} missing Tier A non-use row")
    require(text.count("| Row | Question | Current public-safe answer | Higher authority still required |") == 1, f"{label} boundary table header count mismatch")
    require(text.count("Current tracked docs keep it source/internal and blocked.") == 2, f"{label} must keep both tool rows blocked")


def check_anchor_tokens() -> None:
    for path, tokens in ANCHOR_TOKENS.items():
        text = read_text(path)
        label = str(path.relative_to(ROOT))
        for token in tokens:
            require(token in text, f"{label} missing anchor token: {token}")


def check_package_script() -> None:
    try:
        package = json.loads(read_text(PACKAGE_JSON))
    except json.JSONDecodeError as exc:
        raise CommandBoundaryProbeError(f"invalid JSON: {PACKAGE_JSON.relative_to(ROOT)}: {exc}") from exc
    scripts = package.get("scripts")
    require(isinstance(scripts, dict), "package.json scripts must be an object")
    require(scripts.get(PACKAGE_SCRIPT) == PACKAGE_COMMAND, f"package.json missing {PACKAGE_SCRIPT}")
    require(
        scripts.get("test:original-system-internal-tooling-vocabulary-map") == VOCABULARY_COMMAND,
        "package.json vocabulary-map script changed unexpectedly",
    )


def run_check() -> None:
    canonical_bytes = PLAN.read_bytes()
    mirror_bytes = LORE_PLAN.read_bytes()
    require(canonical_bytes == mirror_bytes, "command-boundary proof-plan copies differ byte-for-byte")

    for path in (PLAN, LORE_PLAN):
        text = read_text(path)
        check_plan_text(text, str(path.relative_to(ROOT)))
        check_links_resolve(text, path)

    check_anchor_tokens()
    check_package_script()


def run_self_test() -> None:
    check_public_safety(
        "Source-only command-boundary planning keeps no runtime proof and no product exposure.",
        "self-test clean boundary",
    )
    for bad_text, label in (
        ("command authorized", "positive command authorization"),
        ("command execution complete", "positive command execution"),
        ("modelviewer is supported", "positive modelviewer support"),
        ("runtime proof complete", "positive runtime proof"),
        ("rebuild parity proven", "positive rebuild parity"),
        (r"C:\\Users\\example\\private\\file.txt", "raw Windows path"),
        ("/home/example/private/file.txt", "raw Unix path"),
        ("a" * 64, "raw digest-like value"),
    ):
        try:
            check_public_safety(bad_text, label)
        except CommandBoundaryProbeError:
            pass
        else:
            raise CommandBoundaryProbeError(f"self-test failed to catch {label}")

    try:
        check_plan_text("not enough context", "self-test missing required plan tokens")
    except CommandBoundaryProbeError:
        pass
    else:
        raise CommandBoundaryProbeError("self-test failed to catch incomplete plan")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate tracked command-boundary proof plan")
    parser.add_argument("--self-test", action="store_true", help="run internal negative guard tests")
    args = parser.parse_args()

    if not args.check and not args.self_test:
        parser.error("choose --check and/or --self-test")

    try:
        if args.self_test:
            run_self_test()
        if args.check:
            run_check()
    except CommandBoundaryProbeError as exc:
        print("Internal viewer/editor command-boundary proof-plan probe: FAIL")
        print(f"- {exc}")
        return 1

    print("Internal viewer/editor command-boundary proof-plan probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
