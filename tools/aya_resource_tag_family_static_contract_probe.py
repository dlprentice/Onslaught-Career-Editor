#!/usr/bin/env python3
"""Validate the AYA resource tag-family static contract.

This checker consumes only tracked public Markdown and package metadata. It
does not inspect ignored payload overlays, private manifests, raw proof bundles,
copied executables, live Ghidra state, runtime logs, auth/session/cache data, or
secrets. It validates that the tag-family table remains a source/static routing
contract and does not become corpus proof, runtime proof, importer execution, or
generated asset output.
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
PLAN = ROOT / "reverse-engineering" / "game-assets" / "aya-resource-tag-family-static-contract.md"
LORE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "aya-resource-tag-family-static-contract.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
LORE_GAME_ASSETS_INDEX = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "_index.md"
CHUNKER_SYSTEM = ROOT / "reverse-engineering" / "source-code" / "io" / "chunker-system.md"
AYA_FORMAT = ROOT / "reverse-engineering" / "game-assets" / "aya-asset-format.md"
EXTRACTION_PIPELINE = ROOT / "reverse-engineering" / "game-assets" / "extraction-pipeline.md"
CHUNKER_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "chunker.cpp" / "_index.md"
RESOURCE_ACCUMULATOR_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ResourceAccumulator.cpp" / "_index.md"
CHAIN_MAP = ROOT / "roadmap" / "rebuild-front-door-chain-map.md"
PACKAGE_JSON = ROOT / "package.json"

PLAN_NAME = "aya-resource-tag-family-static-contract.md"
SCOPE = "aya-resource-tag-family-static-contract"
ALIAS = "aya-tag-family-static-contract"
PACKAGE_SCRIPT = "test:aya-resource-tag-family-static-contract"
PACKAGE_COMMAND = r"py -3 tools\aya_resource_tag_family_static_contract_probe.py --check"
TAGS = ("LVLR", "WRES", "ERES", "LNDS", "PAGE", "GDIE", "MESH", "TEXT")

REQUIRED_PLAN_TOKENS = (
    "Status: source/static public-safe contract, not runtime parser proof",
    f"Scope: `{SCOPE}`",
    "`LVLR`, `WRES`, `ERES`, `LNDS`, `PAGE`, `GDIE`, `MESH`, and `TEXT`",
    "The current proof class is Tier C source/file-format documentation plus Tier B",
    "retail/static loader documentation",
    "Tier C source and file-format docs",
    "Tier B retail/static loader docs",
    "Tier A runtime/corpus proof",
    "Not used in this slice.",
    "tracked `CChunkReader` and `CResourceAccumulator` static docs",
    "Corpus counts, exact payload schemas",
    "runtime parser behavior",
    "generated asset output",
    "importer execution",
    "renderer behavior",
    "rebuild parity require higher-authority proof",
    "This checker-backed slice may read only tracked public Markdown and package",
    "launch BEA",
    "attach CDB",
    "mutate Ghidra",
    "patch an executable",
    "mutate an installed game",
    "run an extractor",
    "execute an importer",
    "generate asset payloads",
    "claim fresh archive counts",
    "full corpus coverage",
    "exact payload schemas",
    "runtime resource loading",
    "visual output",
    "gameplay behavior",
    "no-noticeable-difference",
    "add AppCore, WinUI, CLI, release, installer, packaging, command-arm",
    "game-assets indexes link this contract",
    "without changing active rebuild proof scope",
    "No runtime proof, extractor run",
    "importer execution, generated asset output, product exposure, or release action",
)

REQUIRED_PLAN_LINK_NAMES = (
    "chunker-system.md",
    "aya-asset-format.md",
    "extraction-pipeline.md",
    "_index.md",
    "_index.md",
    "rebuild-front-door-chain-map.md",
)

ANCHOR_TOKENS = {
    CHUNKER_SYSTEM: (
        "Resource Accumulator",
        "`LVLR`",
        "`WRES`",
        "`ERES`",
        "`LNDS`",
        "`PAGE`",
        "`GDIE`",
        "`MESH`",
        "`TEXT`",
    ),
    AYA_FORMAT: (
        "Compression Architecture",
        "zlib",
        "Tagged Chunk System",
        "Model Binary Structure",
        "Texture Format",
    ),
    EXTRACTION_PIPELINE: (
        "Public-Safe Posture",
        "bring-your-own-game-files",
        "`301` PC resource archives",
        "`TEXT 18857`",
        "`MESH 3492`",
        "`GDIE 232`",
    ),
    CHUNKER_INDEX: (
        "CChunkReader__GetNext",
        "CChunkReader__Read",
        "CChunkReader__Skip",
        "Known consumers include",
        "does not prove runtime archive coverage",
    ),
    RESOURCE_ACCUMULATOR_INDEX: (
        "CResourceAccumulator__ReadResourceFile",
        "MESH",
        "TEXT",
        "ERES",
        "WRES",
        "GDIE",
        "runtime loading behavior",
        "rebuild parity remain open",
    ),
    GAME_ASSETS_INDEX: (
        PLAN_NAME,
        ALIAS,
        "source/static planning contract",
        "not corpus proof",
    ),
    LORE_GAME_ASSETS_INDEX: (
        PLAN_NAME,
        ALIAS,
        "source/static planning contract",
        "not corpus proof",
    ),
    CHAIN_MAP: (
        PLAN_NAME,
        ALIAS,
        "AYA tag-family static contract",
        "source/static loader-contract vocabulary",
        "does not change the active rebuild proof scope",
    ),
}

FORBIDDEN_PUBLIC_PATTERNS = (
    (re.compile(r"\b[A-Za-z]:[\\/]"), "machine-local absolute path"),
    (re.compile(r"(?i)c:[\\/]users"), "user profile path"),
    (re.compile(r"(?i)/(?:home|mnt|var|opt|tmp|users?)/"), "machine-local absolute path"),
    (re.compile(r"(?i)program files"), "installed game path"),
    (re.compile(r"(?i)steamapps"), "installed game path"),
    (re.compile(r"(?i)(?:local-)?game[\\/]"), "private game mirror path"),
    (re.compile(r"(?i)(?:local-)?media[\\/]"), "private media path"),
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
    "fresh archive counts proven",
    "full corpus coverage proven",
    "exact payload schemas proven",
    "runtime parser behavior proven",
    "runtime resource loading proven",
    "generated asset output complete",
    "extractor run complete",
    "importer execution complete",
    "real importer executed",
    "renderer behavior proven",
    "visual output proven",
    "gameplay behavior proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
    "appcore support added",
    "winui support added",
    "cli support added",
    "release action authorized",
    "product exposure approved",
)

LINK_PATTERN = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")


class AyaTagContractError(ValueError):
    """Raised when the AYA tag-family contract violates its boundary."""


def read_text(path: Path) -> str:
    if not path.is_file():
        raise AyaTagContractError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8-sig")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AyaTagContractError(message)


def normalize_repo_path(path: Path) -> str:
    return path.relative_to(ROOT.resolve()).as_posix()


@lru_cache(maxsize=1)
def tracked_markdown_paths() -> frozenset[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.md"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AyaTagContractError("failed to enumerate public Markdown files with git ls-files") from exc
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
        raise AyaTagContractError(f"{label} resolves outside repo: {raw_target}") from exc
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
        require(relative in tracked_markdown, f"{label} local link target is not public Markdown: {raw_target}")
        require(resolved.is_file(), f"{label} Markdown link does not resolve: {raw_target}")


def check_plan_text(text: str, label: str) -> None:
    check_public_safety(text, label)
    for token in REQUIRED_PLAN_TOKENS:
        require(contains_token(text, token), f"{label} missing required token: {token}")
    for tag in TAGS:
        require(f"| `{tag}` |" in text, f"{label} missing tag-family row: {tag}")
    require(text.count("| Tier C source and file-format docs |") == 1, f"{label} missing Tier C table row")
    require(text.count("| Tier B retail/static loader docs |") == 1, f"{label} missing Tier B table row")
    require(text.count("| Tier A runtime/corpus proof | Not used in this slice. |") == 1, f"{label} missing Tier A non-use row")
    require(text.count("| Tag | Routing family | Current public-safe use | Higher authority still required |") == 1, f"{label} tag-family table header count mismatch")


def check_anchor_tokens() -> None:
    for path, tokens in ANCHOR_TOKENS.items():
        text = read_text(path)
        label = str(path.relative_to(ROOT))
        for token in tokens:
            require(contains_token(text, token), f"{label} missing anchor token: {token}")


def check_package_script() -> None:
    try:
        package = json.loads(read_text(PACKAGE_JSON))
    except json.JSONDecodeError as exc:
        raise AyaTagContractError(f"invalid JSON: {PACKAGE_JSON.relative_to(ROOT)}: {exc}") from exc
    scripts = package.get("scripts")
    require(isinstance(scripts, dict), "package.json scripts must be an object")
    require(scripts.get(PACKAGE_SCRIPT) == PACKAGE_COMMAND, f"package.json missing {PACKAGE_SCRIPT}")


def run_check() -> None:
    require(PLAN.read_bytes() == LORE_PLAN.read_bytes(), "AYA tag-family contract copies differ byte-for-byte")
    for path in (PLAN, LORE_PLAN):
        text = read_text(path)
        check_plan_text(text, str(path.relative_to(ROOT)))
        check_links_resolve(text, path)
    check_anchor_tokens()
    check_package_script()


def run_self_test() -> None:
    check_public_safety(
        "Source/static tag-family routing only; no runtime proof and no generated asset output.",
        "self-test clean boundary",
    )
    for bad_text, label in (
        ("runtime parser behavior proven", "positive runtime parser proof"),
        ("full corpus coverage proven", "positive corpus proof"),
        ("generated asset output complete", "positive generated output"),
        ("importer execution complete", "positive importer execution"),
        ("rebuild parity proven", "positive rebuild parity"),
        (r"C:\\Users\\example\\private\\file.txt", "raw Windows path"),
        ("/home/example/private/file.txt", "raw Unix path"),
        ("a" * 64, "raw digest-like value"),
    ):
        try:
            check_public_safety(bad_text, label)
        except AyaTagContractError:
            pass
        else:
            raise AyaTagContractError(f"self-test failed to catch {label}")

    try:
        check_plan_text("not enough context", "self-test incomplete plan")
    except AyaTagContractError:
        pass
    else:
        raise AyaTagContractError("self-test failed to catch incomplete plan")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate tracked AYA tag-family static contract")
    parser.add_argument("--self-test", action="store_true", help="run internal negative guard tests")
    args = parser.parse_args()

    if not args.check and not args.self_test:
        parser.error("choose --check and/or --self-test")

    try:
        if args.self_test:
            run_self_test()
        if args.check:
            run_check()
    except AyaTagContractError as exc:
        print("AYA resource tag-family static contract probe: FAIL")
        print(f"- {exc}")
        return 1

    print("AYA resource tag-family static contract probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
