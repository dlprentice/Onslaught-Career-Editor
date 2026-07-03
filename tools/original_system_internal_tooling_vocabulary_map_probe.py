#!/usr/bin/env python3
"""Validate the public-safe original-system internal tooling vocabulary map.

This checker consumes only tracked public-source Markdown. It verifies that the
canonical source map and Lore mirror stay byte-identical, that the map keeps its
source-only/non-claim vocabulary boundaries, and that all local Markdown links
used by the map resolve inside the public source tree. It does not read ignored
payload overlays, private manifests, live Ghidra state, runtime proof outputs,
release artifacts, copied executables, or generated package output.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_MAP = (
    ROOT
    / "reverse-engineering"
    / "source-code"
    / "original-system-internal-tooling-vocabulary-map.md"
)
LORE_MIRROR_MAP = (
    ROOT
    / "lore-book"
    / "reverse-engineering"
    / "source-code"
    / "original-system-internal-tooling-vocabulary-map.md"
)

MAPS = (CANONICAL_MAP, LORE_MIRROR_MAP)
ALIAS = "tmm-arm4-readiness-gate"

REQUIRED_BOUNDARY_TOKENS = (
    "Status: source-only continuity map; context only, not readiness evidence",
    f"context companion for the current `{ALIAS}` continuity lane, not a readiness-gate artifact",
    "Authority boundary: Steam retail binary, save, and separately documented runtime evidence outrank",
    "Source names are candidate vocabulary only.",
    "This artifact makes no readiness-gate execution or completion claim",
    "no command arming claim",
    "no importer-execution claim",
    "no private-asset-read claim",
    "no generated-payload claim",
    "no runtime-proof claim",
    "no Ghidra mutation claim",
    "no rebuild-parity claim",
    "no no-noticeable-difference claim",
    "It is not an instruction to run internal tools",
    "Retail feature presence, shipping UI flow, complete toolchain reconstruction, or command execution",
    "Real importer execution, generated payload correctness, textured rendering, animation, or no-noticeable-difference",
    "candidate vocabulary only; they do not prove Steam retail feature presence or runtime behavior",
    "do not describe `.bes` save format unless a separate save-file proof says so",
    "Static renderer/material contracts are planning evidence only.",
    "Source inventory gaps are gaps in the provided source/docs",
    "This file must not be used as command-arm checklist evidence",
    "Future public-safe slices can use this vocabulary map to pick one bounded question",
    "separate authority and a dedicated proof contract",
)

AUTHORITY_TIER_HEADER = ("Tier", "Evidence class", "May support", "Must not be used for")
AUTHORITY_TIER_ROWS = {
    "A": ("Retail binary, save", "Claims outside that proof class"),
    "B": ("Static RE contracts", "runtime proof, or parity"),
    "C": ("Stuart internal PC source docs", "complete toolchain reconstruction, or command execution"),
    "D": ("Asset extraction and AYA format docs", "Real importer execution"),
}

SOURCE_VOCABULARY_HEADER = (
    "Area",
    "Public anchor",
    "Source/internal signal",
    "Candidate clean-room use",
    "Evidence ceiling",
    "Higher authority still required",
    "Still out of scope here",
)

SOURCE_ROW_REQUIRED_TOKENS = {
    "Internal editor shell": (
        "Tier C source-only context",
        "Retail static or runtime evidence",
        "Readiness-gate execution",
        "tool launch",
        "visual proof",
        "parity",
    ),
    "Internal viewer/editor names": (
        "Tier C source vocabulary only",
        "Retail flag/static proof",
        "Command arming",
        "tool execution",
        "retail feature claims",
    ),
    "Development menu / level selection": (
        "Tier C unless independently tied to retail binary behavior",
        "Retail UI/static and runtime evidence",
        "Host/Join enablement",
        "runtime gameplay proof",
        "save-format changes",
    ),
    "Map/world tooling boundary": (
        "Tier B/C planning context",
        "Retail static docs, asset schemas, and runtime proof",
        "Complete map editor reconstruction",
        "generated world payloads",
        "parity",
    ),
    "Resource container vocabulary": (
        "Tier D/B tag and static context",
        "Structured parser proof and retail/static confirmation",
        "private asset reads",
        "raw manifests",
        "importer execution",
        "generated output",
    ),
    "Mesh/material sidecar vocabulary": (
        "Tier D public extraction/format context",
        "Fixture or retail/static proof",
        "Real importer execution",
        "generated payloads",
        "no-noticeable-difference",
    ),
    "Dev precompute versus release load posture": (
        "Tier D provenance only",
        "Separate retail evidence",
        "Recreating internal precompute tools",
        "importer execution",
        "rebuild parity",
    ),
    "Renderer/material static contracts": (
        "Tier B static contract only",
        "Runtime and visual proof",
        "Runtime proof",
        "visual parity",
        "no-noticeable-difference",
    ),
    "Career and mission outcome boundary": (
        "Tier A/C split",
        "Retail save/static/runtime evidence",
        "Asset importer claims",
        "runtime gameplay proof",
        "save layout expansion",
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
    "readiness-gate complete",
    "readiness gate complete",
    "readiness-gate proof complete",
    "readiness gate proof complete",
    "readiness-gate execution complete",
    "readiness gate execution complete",
    "runtime proof complete",
    "runtime proof proven",
    "runtime proof achieved",
    "rebuild parity proven",
    "rebuild parity achieved",
    "rebuild parity complete",
    "no-noticeable-difference parity proven",
    "no-noticeable-difference parity achieved",
    "command armed successfully",
    "command arm complete",
    "command arming complete",
    "command execution complete",
    "shell dispatch complete",
    "importer executed successfully",
    "importer execution complete",
    "real importer complete",
    "private asset read complete",
    "generated payload complete",
    "generated payloads complete",
    "cleared to arm",
    "ready for execution",
)

LINK_PATTERN = re.compile(r"(?<!!)\[[^\]\n]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")


class VocabularyMapProbeError(ValueError):
    """Raised when the vocabulary map violates its public-safe source boundary."""


def read_text(path: Path) -> str:
    if not path.is_file():
        raise VocabularyMapProbeError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8-sig")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VocabularyMapProbeError(message)


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def contains_token(text: str, token: str) -> bool:
    return token in text or token in compact(text)


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
        raise VocabularyMapProbeError("failed to enumerate tracked Markdown files with git ls-files") from exc
    paths = frozenset(path for path in result.stdout.decode("utf-8", errors="replace").split("\0") if path)
    require(paths, "git ls-files returned no tracked Markdown files")
    return paths


def check_public_safety(text: str, label: str) -> None:
    lower = text.lower()
    for pattern, category in FORBIDDEN_PUBLIC_PATTERNS:
        require(pattern.search(text) is None, f"{label} leaks forbidden public category: {category}")
    for phrase in FORBIDDEN_OVERCLAIMS:
        require(phrase not in lower, f"{label} contains forbidden overclaim phrase: {phrase}")


def require_required_boundaries(text: str, label: str) -> None:
    for token in REQUIRED_BOUNDARY_TOKENS:
        require(contains_token(text, token), f"{label} missing required boundary token: {token}")


def section_after_heading(text: str, heading: str, label: str) -> str:
    match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
    require(match is not None, f"{label} missing heading: {heading}")
    tail_start = match.end()
    next_heading = re.search(r"(?m)^##\s+", text[tail_start:])
    tail_end = tail_start + next_heading.start() if next_heading else len(text)
    section = text[tail_start:tail_end].strip()
    require(section != "", f"{label} section is empty after {heading}")
    return section


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_first_table(section: str, label: str) -> tuple[list[str], list[list[str]]]:
    lines = [line.rstrip() for line in section.splitlines()]
    start = next((index for index, line in enumerate(lines) if line.lstrip().startswith("|")), None)
    require(start is not None, f"{label} missing Markdown table")
    require(start + 1 < len(lines), f"{label} table missing separator")
    header = split_table_row(lines[start])
    separator = split_table_row(lines[start + 1])
    require(
        all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator),
        f"{label} table missing separator row",
    )
    rows: list[list[str]] = []
    for line in lines[start + 2 :]:
        if not line.lstrip().startswith("|"):
            break
        row = split_table_row(line)
        require(len(row) == len(header), f"{label} table row has {len(row)} cells, expected {len(header)}: {line}")
        rows.append(row)
    require(rows, f"{label} table has no body rows")
    return header, rows


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
        raise VocabularyMapProbeError(f"{label} resolves outside repo: {raw_target}") from exc
    return resolved


def check_links_resolve(text: str, source_path: Path) -> None:
    label = str(source_path.relative_to(ROOT))
    links = local_markdown_links(text)
    require(links, f"{label} has no local Markdown links to validate")
    tracked_markdown = tracked_markdown_paths()
    for raw_target in links:
        resolved = resolve_link(source_path, raw_target, label)
        relative = normalize_repo_path(resolved)
        require(relative.endswith(".md"), f"{label} local link target is not Markdown: {raw_target}")
        require(relative in tracked_markdown, f"{label} local link target is not tracked public Markdown: {raw_target}")
        require(resolved.is_file(), f"{label} tracked Markdown link does not resolve: {raw_target}")


def check_authority_tiers(text: str, label: str) -> None:
    section = section_after_heading(text, "## Authority Tiers", label)
    header, rows = parse_first_table(section, f"{label} Authority Tiers")
    require(tuple(header) == AUTHORITY_TIER_HEADER, f"{label} Authority Tiers header changed")
    require(len(rows) == len(AUTHORITY_TIER_ROWS), f"{label} Authority Tiers row count changed")
    row_by_tier = {row[0]: row for row in rows}
    require(set(row_by_tier) == set(AUTHORITY_TIER_ROWS), f"{label} Authority Tiers must contain only A-D")
    for tier, tokens in AUTHORITY_TIER_ROWS.items():
        row_text = " ".join(row_by_tier[tier])
        for token in tokens:
            require(token in row_text, f"{label} Authority Tier {tier} missing token: {token}")
        require(row_by_tier[tier][3] != "", f"{label} Authority Tier {tier} missing evidence ceiling limit")


def check_source_vocabulary_table(text: str, label: str) -> None:
    section = section_after_heading(text, "## Source-Indexed Vocabulary", label)
    header, rows = parse_first_table(section, f"{label} Source-Indexed Vocabulary")
    require(tuple(header) == SOURCE_VOCABULARY_HEADER, f"{label} Source-Indexed Vocabulary header changed")
    row_by_area = {row[0]: row for row in rows}
    expected_areas = set(SOURCE_ROW_REQUIRED_TOKENS)
    require(set(row_by_area) == expected_areas, f"{label} Source-Indexed Vocabulary areas changed")
    for area, tokens in SOURCE_ROW_REQUIRED_TOKENS.items():
        row = row_by_area[area]
        row_text = " ".join(row)
        require("Tier " in row[4], f"{label} {area} evidence ceiling must name a tier")
        require(row[5] != "", f"{label} {area} missing higher-authority requirement")
        require(row[6] != "", f"{label} {area} missing out-of-scope boundary")
        require(local_markdown_links(row[1]), f"{label} {area} missing public anchor links")
        for token in tokens:
            require(token in row_text, f"{label} {area} missing table boundary token: {token}")


def check_scope_firewall(text: str, label: str) -> None:
    section = section_after_heading(text, "## Scope Firewall", label)
    bullets = [line for line in section.splitlines() if line.startswith("- ")]
    require(len(bullets) >= 5, f"{label} Scope Firewall must keep at least five boundary bullets")
    for token in (
        "candidate vocabulary only",
        "do not prove Steam retail feature presence",
        "do not describe `.bes` save format",
        "planning evidence only",
        "not proof that a retail system is absent or complete",
        "must not be used as command-arm checklist evidence",
        "readiness-gate proof evidence",
        "generated-output evidence",
    ):
        require(contains_token(section, token), f"{label} Scope Firewall missing token: {token}")


def check_tmm_continuity_boundary(text: str, label: str) -> None:
    require(f"`{ALIAS}`" in text, f"{label} missing {ALIAS} continuity alias")
    require(
        contains_token(text, f"context companion for the current `{ALIAS}` continuity lane, not a readiness-gate artifact"),
        f"{label} does not bound {ALIAS} as context-only continuity",
    )
    require(
        contains_token(text, "not readiness evidence"),
        f"{label} missing not-readiness-evidence status",
    )
    require(
        contains_token(text, "not a readiness-gate artifact"),
        f"{label} missing readiness-gate artifact non-claim",
    )
    require(
        contains_token(text, "readiness-gate proof evidence"),
        f"{label} missing readiness-gate proof-evidence firewall",
    )


def check_map_text(text: str, path: Path) -> None:
    label = str(path.relative_to(ROOT))
    check_public_safety(text, label)
    require_required_boundaries(text, label)
    check_authority_tiers(text, label)
    check_source_vocabulary_table(text, label)
    check_scope_firewall(text, label)
    check_tmm_continuity_boundary(text, label)
    check_links_resolve(text, path)


def run_self_test() -> None:
    check_public_safety(
        "This context-only source vocabulary makes no runtime proof claim.",
        "self-test clean boundary",
    )

    for bad_text, label in (
        ("readiness-gate complete", "positive readiness-gate overclaim"),
        ("runtime proof complete", "positive runtime-proof overclaim"),
        ("rebuild parity proven", "positive rebuild-parity overclaim"),
        (r"C:\\Users\\example\\private\\game\\BEA.exe", "raw Windows/private path"),
        ("command armed successfully", "positive command-arm claim"),
        ("importer executed successfully", "positive importer execution claim"),
        ("importer execution complete", "positive importer execution completion claim"),
        ("command arming complete", "positive command-arm completion claim"),
        ("local-game/BEA.exe", "private game mirror path"),
        ("media/private.wav", "private media path"),
        ("/home/example/private/file.txt", "raw Unix private path"),
        ("a" * 64, "raw digest-like value"),
    ):
        try:
            check_public_safety(bad_text, label)
        except VocabularyMapProbeError:
            pass
        else:
            raise VocabularyMapProbeError(f"self-test failed to catch {label}")

    try:
        require_required_boundaries("not enough context", "missing required boundaries")
    except VocabularyMapProbeError:
        pass
    else:
        raise VocabularyMapProbeError("self-test failed to catch missing required boundaries")

    minimal_good = "\n".join(REQUIRED_BOUNDARY_TOKENS)
    require_required_boundaries(minimal_good, "self-test complete required boundaries")

    try:
        check_tmm_continuity_boundary(
            "This is tmm-arm4-readiness-gate readiness-gate complete.",
            "self-test missing bounded tmm relationship",
        )
    except VocabularyMapProbeError:
        pass
    else:
        raise VocabularyMapProbeError("self-test failed to catch unbounded tmm relationship")

    try:
        check_links_resolve("[package](../../package.json)", CANONICAL_MAP)
    except VocabularyMapProbeError:
        pass
    else:
        raise VocabularyMapProbeError("self-test failed to catch non-Markdown local link")


def run_check() -> None:
    canonical_bytes = CANONICAL_MAP.read_bytes()
    mirror_bytes = LORE_MIRROR_MAP.read_bytes()
    require(canonical_bytes == mirror_bytes, "vocabulary map copies differ byte-for-byte")
    for path in MAPS:
        check_map_text(read_text(path), path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate tracked vocabulary map copies")
    parser.add_argument("--self-test", action="store_true", help="run internal negative guard tests")
    args = parser.parse_args()

    if not args.check and not args.self_test:
        parser.error("choose --check and/or --self-test")

    try:
        if args.self_test:
            run_self_test()
        if args.check:
            run_check()
    except VocabularyMapProbeError as exc:
        print("Original-system internal tooling vocabulary map probe: FAIL")
        print(f"- {exc}")
        return 1

    print("Original-system internal tooling vocabulary map probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
