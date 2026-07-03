#!/usr/bin/env python3
"""Validate the career progression bridge static contract.

This checker consumes only tracked public Markdown and package metadata. It
does not inspect ignored payload overlays, private saves, raw proof bundles,
copied executables, live Ghidra state, runtime logs, auth/session/cache data, or
secrets. It validates that the career bridge remains source/static planning
context and does not become runtime save/load, mission-outcome, gameplay, UI,
patch, generated-output, or rebuild proof.
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
PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "career-progression-static-bridge-contract.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "career-progression-static-bridge-contract.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
LORE_BINARY_INDEX = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "_index.md"
CAREER_SYSTEM = ROOT / "reverse-engineering" / "source-code" / "gameplay" / "career-system.md"
GAME_SYSTEM = ROOT / "reverse-engineering" / "source-code" / "gameplay" / "game-system.md"
SAVE_INDEX = ROOT / "reverse-engineering" / "save-file" / "_index.md"
CAREER_GRAPH = ROOT / "reverse-engineering" / "save-file" / "career-graph.md"
CAREER_LINKS = ROOT / "reverse-engineering" / "save-file" / "career-links.md"
CAREER_FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Career.cpp" / "_index.md"
GAME_FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
ENDLEVEL_FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "EndLevelData.cpp" / "_index.md"
CHAIN_MAP = ROOT / "roadmap" / "rebuild-front-door-chain-map.md"
PACKAGE_JSON = ROOT / "package.json"

PLAN_NAME = "career-progression-static-bridge-contract.md"
SCOPE = "career-progression-static-bridge-contract"
ALIAS = "career-progression-static-bridge-contract"
PACKAGE_SCRIPT = "test:career-progression-static-bridge-contract"
PACKAGE_COMMAND = r"py -3 tools\career_progression_static_bridge_contract_probe.py --check"
BRIDGE_ITEMS = (
    "`level_structure` graph vocabulary",
    "`CCareer` progression update vocabulary",
    "`CGame` outcome snapshot vocabulary",
    "`CEndLevelData` objective predicate vocabulary",
)

REQUIRED_PLAN_TOKENS = (
    "Status: source/static public-safe bridge contract, not runtime mission-outcome or save-behavior proof",
    f"Scope: `{SCOPE}`",
    "how should `CCareer`, `level_structure`, `CGame`, and `CEndLevelData` be",
    "use those names only as bridge vocabulary",
    "The current proof class is Tier C source gameplay architecture plus Tier B retail/static",
    "Tier C source gameplay architecture",
    "Tier B retail/static save and career docs",
    "Tier A runtime save/load and mission-outcome proof",
    "Not used in this slice.",
    "Live copied-runtime save/load behavior, mission win/loss persistence",
    "`CCareer`, `CAREER_VERSION`, `CSArray`, `level_structure`",
    "`CGame` slots, level state, mission-outcome",
    "fixed-size `.bes` true-view",
    "campaign node/link map, `CCareer__Update -> CCareer__ReCalcLinks`",
    "`CGame__FillOutEndLevelData`, `CGame__DeclareLevelWon`, and `CGame__DeclareLevelLost`",
    "`CEndLevelData__IsAllSecondaryObjectivesComplete`",
    "This checker-backed slice may read only tracked public Markdown and package",
    "launch BEA",
    "attach CDB",
    "mutate Ghidra",
    "patch an executable",
    "mutate an installed game",
    "run a save editor",
    "run an extractor",
    "execute an importer",
    "generate asset or save payloads",
    "claim runtime save/load behavior",
    "defaultoptions boot behavior",
    "menu behavior",
    "runtime mission-outcome persistence",
    "runtime objective UI",
    "runtime Goodies wall behavior",
    "runtime Goodies recomputation",
    "live MissionScript command effects",
    "gameplay behavior",
    "rebuild parity",
    "no-noticeable-difference parity",
    "add AppCore, WinUI, CLI, Godot, save-editor",
    "binary-analysis indexes link this contract",
    "campaign/career progression side guard without changing active rebuild proof",
    "No runtime proof, save-editor run",
    "generated asset or save output, gameplay claim",
)

REQUIRED_PLAN_LINK_PATHS = (
    "reverse-engineering/source-code/gameplay/career-system.md",
    "reverse-engineering/source-code/gameplay/game-system.md",
    "reverse-engineering/save-file/_index.md",
    "reverse-engineering/save-file/career-graph.md",
    "reverse-engineering/save-file/career-links.md",
    "reverse-engineering/binary-analysis/functions/Career.cpp/_index.md",
    "reverse-engineering/binary-analysis/functions/game.cpp/_index.md",
    "reverse-engineering/binary-analysis/functions/EndLevelData.cpp/_index.md",
    "roadmap/rebuild-front-door-chain-map.md",
)

ANCHOR_TOKENS = {
    CAREER_SYSTEM: (
        "`CAREER_VERSION`",
        "`level_structure[43][5]`",
        "`CSArray<T, size>`",
        "retail `.bes` persistence is not a strict 1:1 replay",
        "true view mapping",
    ),
    GAME_SYSTEM: (
        "mSlots = CAREER.GetSlots()",
        "CCareer::Update()",
        "DeclareLevelLost",
        "mission completed",
        "runtime state",
    ),
    SAVE_INDEX: (
        "10,004-byte `.bes`",
        "version `0x4BD1`",
        "true-view base `0x0002`",
        "Runtime save/load",
        "not runtime proof",
    ),
    CAREER_GRAPH: (
        "CCareer__Update -> CCareer__ReCalcLinks",
        "Campaign Graph Structure (level_structure)",
        "On-Disk Structure Validation (Steam Saves)",
        "CN_COMPLETE_BROKEN",
        "file + 2",
    ),
    CAREER_LINKS: (
        "Career Link Index Map (Steam)",
        "level_structure",
        "lower",
        "higher",
        "World 500 special-case",
    ),
    CAREER_FUNCTION_INDEX: (
        "CCareer__Update",
        "CCareer__ReCalcLinks",
        "CEndLevelData__IsAllSecondaryObjectivesComplete",
        "runtime save/career progression",
        "rebuild",
    ),
    GAME_FUNCTION_INDEX: (
        "CGame__FillOutEndLevelData",
        "CGame__DeclareLevelWon",
        "CGame__DeclareLevelLost",
        "runtime level outcomes",
        "runtime save/career behavior",
    ),
    ENDLEVEL_FUNCTION_INDEX: (
        "CEndLevelData__IsAllSecondaryObjectivesComplete",
        "CGame__FillOutEndLevelData",
        "CCareer__Update",
        "runtime progression behavior",
        "rebuild parity",
    ),
    BINARY_INDEX: (
        PLAN_NAME,
        ALIAS,
        "source/static bridge contract",
        "not runtime save/load",
    ),
    LORE_BINARY_INDEX: (
        PLAN_NAME,
        ALIAS,
        "source/static bridge contract",
        "not runtime save/load",
    ),
    CHAIN_MAP: (
        PLAN_NAME,
        ALIAS,
        "campaign/career progression side guard",
        "source/static save and career vocabulary",
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
    "runtime save/load behavior proven",
    "defaultoptions boot behavior proven",
    "menu behavior proven",
    "runtime mission-outcome persistence proven",
    "runtime objective ui proven",
    "runtime goodies wall behavior proven",
    "runtime goodies recomputation proven",
    "live missionscript command effects proven",
    "gameplay behavior proven",
    "patch behavior proven",
    "visual output proven",
    "renderer behavior proven",
    "runtime proof complete",
    "save-editor run complete",
    "generated save output complete",
    "generated asset output complete",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "appcore support added",
    "winui support added",
    "cli support added",
    "godot support added",
    "release action authorized",
    "product exposure approved",
)

LINK_PATTERN = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")


class CareerBridgeContractError(ValueError):
    """Raised when the career bridge contract violates its boundary."""


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CareerBridgeContractError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8-sig")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CareerBridgeContractError(message)


def normalize_repo_path(path: Path) -> str:
    return path.relative_to(ROOT.resolve()).as_posix()


@lru_cache(maxsize=1)
def tracked_markdown_paths() -> frozenset[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--", "*.md"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CareerBridgeContractError("failed to enumerate public Markdown files with git ls-files") from exc
    paths = frozenset(path for path in result.stdout.decode("utf-8", errors="replace").split("\0") if path)
    require(paths, "git ls-files returned no public Markdown files")
    return paths


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def contains_token(text: str, token: str) -> bool:
    return token in text or token in compact(text)


def check_public_safety(text: str, label: str) -> None:
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{label} leaks forbidden public category: {category}")
    lower = text.lower()
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{label} contains forbidden overclaim phrase: {phrase}")


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
    if clean_target.startswith("/"):
        resolved = (ROOT / clean_target.lstrip("/")).resolve()
    else:
        target_path = Path(clean_target)
        require(not target_path.is_absolute(), f"{label} uses absolute local link target: {raw_target}")
        resolved = (source_path.parent / target_path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise CareerBridgeContractError(f"{label} resolves outside repo: {raw_target}") from exc
    return resolved


def check_links_resolve(text: str, source_path: Path) -> None:
    label = str(source_path.relative_to(ROOT))
    links = local_markdown_links(text)
    require(links, f"{label} has no local Markdown links to validate")
    tracked_markdown = tracked_markdown_paths()
    resolved_relatives: list[str] = []
    for raw_target in links:
        resolved = resolve_link(source_path, raw_target, label)
        relative = normalize_repo_path(resolved)
        resolved_relatives.append(relative)
        require(relative.endswith(".md"), f"{label} local link target is not Markdown: {raw_target}")
        require(relative in tracked_markdown, f"{label} local link target is not public Markdown: {raw_target}")
        require(resolved.is_file(), f"{label} Markdown link does not resolve: {raw_target}")
    for required_path in REQUIRED_PLAN_LINK_PATHS:
        require(required_path in resolved_relatives, f"{label} missing required resolved link target: {required_path}")


def check_plan_text(text: str, label: str) -> None:
    check_public_safety(text, label)
    for token in REQUIRED_PLAN_TOKENS:
        require(contains_token(text, token), f"{label} missing required token: {token}")
    for item in BRIDGE_ITEMS:
        require(f"| {item} |" in text, f"{label} missing bridge row: {item}")
    require(text.count("| Tier C source gameplay architecture |") == 1, f"{label} missing Tier C table row")
    require(text.count("| Tier B retail/static save and career docs |") == 1, f"{label} missing Tier B table row")
    require(text.count("| Tier A runtime save/load and mission-outcome proof | Not used in this slice. |") == 1, f"{label} missing Tier A non-use row")
    require(text.count("| Bridge item | Static route allowed | Higher authority still required |") == 1, f"{label} bridge table header count mismatch")


def check_anchor_tokens() -> None:
    for path, tokens in ANCHOR_TOKENS.items():
        text = read_text(path)
        label = str(path.relative_to(ROOT))
        for token in tokens:
            require(contains_token(text, token), f"{label} missing anchor token: {token}")


def check_registration_line_safety() -> None:
    for path in (BINARY_INDEX, LORE_BINARY_INDEX, CHAIN_MAP):
        label = str(path.relative_to(ROOT))
        lines = read_text(path).splitlines()
        matching_lines = [line for line in lines if ALIAS in line or PLAN_NAME in line]
        require(matching_lines, f"{label} has no registration line for {ALIAS}")
        for line in matching_lines:
            check_public_safety(line, f"{label} registration line")


def check_package_script() -> None:
    try:
        package = json.loads(read_text(PACKAGE_JSON))
    except json.JSONDecodeError as exc:
        raise CareerBridgeContractError(f"invalid JSON: {PACKAGE_JSON.relative_to(ROOT)}: {exc}") from exc
    scripts = package.get("scripts")
    require(isinstance(scripts, dict), "package.json scripts must be an object")
    require(scripts.get(PACKAGE_SCRIPT) == PACKAGE_COMMAND, f"package.json missing {PACKAGE_SCRIPT}")


def run_check() -> None:
    require(PLAN.read_bytes() == LORE_PLAN.read_bytes(), "career progression bridge contract copies differ byte-for-byte")
    for path in (PLAN, LORE_PLAN):
        text = read_text(path)
        check_plan_text(text, str(path.relative_to(ROOT)))
        check_links_resolve(text, path)
    check_anchor_tokens()
    check_registration_line_safety()
    check_package_script()


def run_self_test() -> None:
    check_public_safety(
        "Source/static career bridge only; no runtime proof and no save output.",
        "self-test clean boundary",
    )
    for bad_text, label in (
        ("runtime save/load behavior proven", "positive runtime save proof"),
        ("runtime mission-outcome persistence proven", "positive mission outcome proof"),
        ("live MissionScript command effects proven", "positive command effect proof"),
        ("generated save output complete", "positive generated save output"),
        ("gameplay behavior proven", "positive gameplay proof"),
        ("rebuild parity proven", "positive rebuild parity"),
        (r"C:\\Users\\example\\private\\file.txt", "raw Windows path"),
        ("/home/example/private/file.txt", "raw Unix path"),
        ("a" * 64, "raw digest-like value"),
    ):
        try:
            check_public_safety(bad_text, label)
        except CareerBridgeContractError:
            pass
        else:
            raise CareerBridgeContractError(f"self-test failed to catch {label}")

    try:
        check_plan_text("not enough context", "self-test incomplete plan")
    except CareerBridgeContractError:
        pass
    else:
        raise CareerBridgeContractError("self-test failed to catch incomplete plan")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate tracked career progression bridge static contract")
    parser.add_argument("--self-test", action="store_true", help="run internal negative guard tests")
    args = parser.parse_args()

    if not args.check and not args.self_test:
        parser.error("choose --check and/or --self-test")

    try:
        if args.self_test:
            run_self_test()
        if args.check:
            run_check()
    except CareerBridgeContractError as exc:
        print("Career progression bridge static contract probe: FAIL")
        print(f"- {exc}")
        return 1

    print("Career progression bridge static contract probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
