#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic schema gate for factory contract Markdown trees.

WHY THIS EXISTS.  The packet-to-contract factory (t_3dcc527c) drafts hundreds
of contract files per wave from triage packets. A draft that silently drops a
mandatory section, invents a ``FUN_*`` name, collides with another file's VA,
carries a malformed digest, or cites evidence the repo does not contain must
never reach review as a valid contract. This tool is the mechanical half of
that gate: it parses a tree of factory contract Markdown files against the
factory brief's skeleton and exits non-zero on any violation. It is
deliberately dumb — no LLM, no semantic grading, no opinion about whether a
claim is TRUE; only that each file is structurally complete, honest about
what it does not know, internally consistent, and anchored to things that
exist.

POLICY BOUNDARY.  Schema validation is not semantic verification and not C1
promotion.  A passing file is well-formed, not correct; see
``reverse-engineering/contract-schema/FACTORY-GATE.md``.

USAGE.
    python ./tools/contract_factory_validate.py <contracts-root> [--repo-root DIR]

Every ``*.md`` under the root is treated as a candidate contract file, so
point the tool at a drafts tree, not at a folder of rule documents. All
violations are collected (the run never short-circuits) and printed as one
``path: line: [CODE] message`` diagnostic per finding, sorted by path, then
line, then code.  Exit status: 0 = clean, 1 = violations found, 2 = usage or
environment error.  Output is byte-identical across runs on the same tree.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

# The pristine specimen's image SHA-256 (AGENTS.md hard boundary: 74154bfa…).
PRISTINE_IMAGE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)

# Section headings required by the factory brief's skeleton (TEMPLATE.md),
# matched case-insensitively; aliases cover equivalent wording already in use.
REQUIRED_SECTIONS: tuple[str, ...] = (
    "Identity",
    "Calling convention",
    "Prototype and parameter semantics",
    "Return value meaning",
    "Globals read/written",
    "Callees relied on / callers",
    "Behavior summary",
    "Error / edge behavior",
    "Runtime corroboration (TTD, bounded)",
    "Evidence",
    "Confidence",
    "Unresolved questions",
)

SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "Globals read/written": ("globally referenced data",),
}

_TITLE_RE = re.compile(r"^#[ \t]+(.+?)\s*$")
_VA_LINE_RE = re.compile(r"^ {0,3}>\s*Address:\s*`([^`]+)`\s*$")
_STEM_RE = re.compile(r"^(?P<name>.+?)__(?P<hex8>[0-9a-f]{8})$")
_ANONYMOUS_RE = re.compile(r"FUN_", re.IGNORECASE)
_CONFIDENCE_RE = re.compile(r"^\s*([0-4])\s*[-\u2014\u2013]\s+\S.*$")
_BACKTICK_RE = re.compile(r"`([^`\n]+)`")
_IMAGE_SHA_LINE_RE = re.compile(
    r"^Source File:.*\|\s*Binary:\s*BEA\.exe,\s*SHA-256\s+`([^`]+)`"
)
_PLACEHOLDER_ONLY = frozenset({"tbd", "todo", "-", "n/a"})
_TRACKED_FILE_SUFFIXES = frozenset({
    "bin", "cpp", "cs", "csv", "gd", "h", "json", "md", "ps1", "py",
    "toml", "tsv", "txt", "xml", "yaml", "yml",
})
_GITMODULES_PATH_RE = re.compile(r"^\s*path\s*=\s*(\S+)\s*$", re.MULTILINE)
_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


@dataclass(frozen=True)
class Violation:
    code: str
    line: int
    message: str


@dataclass
class FileReport:
    path: Path
    relative: str
    violations: list[Violation] = field(default_factory=list)
    normalized_va: str | None = None
    tracked_name: str | None = None
    address_line: int = 0


def normalize_va(raw: str) -> str | None:
    """Canonical VA text: 0x + at least 8 lowercase hex digits."""
    text = raw.strip().lower()
    if not re.fullmatch(r"0x[0-9a-f]+", text):
        return None
    digits = text[2:].lstrip("0") or "0"
    return "0x" + digits.zfill(8)


def _canonical_section(heading: str) -> str | None:
    folded = re.sub(r"\s+", " ", heading.strip().casefold())
    for required in REQUIRED_SECTIONS:
        if folded == required.casefold():
            return required
        if folded in SECTION_ALIASES.get(required, ()):
            return required
    return None


def _outside_fence_flags(lines: list[str]) -> list[bool]:
    """True for Markdown lines outside backtick/tilde fenced code blocks."""
    outside: list[bool] = []
    fence_char: str | None = None
    fence_length = 0
    for line in lines:
        if fence_char is None:
            match = _FENCE_OPEN_RE.match(line)
            if match is None:
                outside.append(True)
                continue
            marker = match.group(1)
            fence_char = marker[0]
            fence_length = len(marker)
            outside.append(False)
            continue

        outside.append(False)
        closing = re.fullmatch(
            rf" {{0,3}}{re.escape(fence_char)}{{{fence_length},}}\s*", line)
        if closing is not None:
            fence_char = None
            fence_length = 0
    return outside


def _section_bodies(
    lines: list[str], outside_fence: list[bool]
) -> list[tuple[str, int, list[str]]]:
    """(canonical name, heading line no, body lines) per known H2 section."""
    marks = [
        (i, _canonical_section(ln[3:]))
        for i, ln in enumerate(lines)
        if outside_fence[i] and ln.startswith("## ")
    ]
    sections = []
    for pos, (index, canonical) in enumerate(marks):
        end = marks[pos + 1][0] if pos + 1 < len(marks) else len(lines)
        body = lines[index + 1:end]
        while body and not body[-1].strip():
            body.pop()
        if canonical is not None:
            sections.append((canonical, index + 1, body))
    return sections


def _content_lines(body: list[str], heading_line: int) -> list[tuple[int, str]]:
    """1-based (absolute line no, text) for non-whitespace body lines."""
    return [
        (heading_line + i + 1, ln)
        for i, ln in enumerate(body)
        if ln.strip()
    ]


def _placeholder_only(text: str) -> bool:
    value = text.strip().casefold()
    while (prefix := re.match(
        r"^(?:[-*+>]|\d+[.)])\s+(.+)$", value
    )) is not None:
        value = prefix.group(1).strip()
    return value in _PLACEHOLDER_ONLY


def _repo_path_claim(token: str) -> bool:
    """Whether a backticked Evidence token claims a tracked repo path."""
    if (not token or token.startswith(("/", "\\", "local-lab/"))
            or "\\" in token):
        return False
    first_segment = token.split("/", 1)[0]
    if ":" in first_segment:  # drive path, URL scheme, or other absolute form
        return False
    if "/" in token:
        return True
    suffix = token.rsplit(".", 1)[-1].casefold() if "." in token else ""
    return suffix in _TRACKED_FILE_SUFFIXES


def parse_gitmodules_paths(repo_root: Path) -> frozenset[str]:
    """Registered submodule path prefixes; their trees may not be materialized."""
    gm = repo_root / ".gitmodules"
    if not gm.is_file():
        return frozenset()
    try:
        text = gm.read_text(encoding="utf-8")
    except OSError:
        return frozenset()
    return frozenset(match.group(1) for match in _GITMODULES_PATH_RE.finditer(text))


def validate_file(
    path: Path,
    relative: str,
    submodule_prefixes: frozenset[str],
    repo_root: Path,
) -> FileReport:
    report = FileReport(path=path, relative=relative)
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        report.violations.append(Violation(
            "DECODE_ERROR", 1, f"file is not valid UTF-8 ({exc}); fix encoding"))
        return report

    lines = text.splitlines()
    outside_fence = _outside_fence_flags(lines)

    # -- title -----------------------------------------------------------
    titles = []
    for i, ln in enumerate(lines):
        if outside_fence[i] and (title_match := _TITLE_RE.match(ln)) is not None:
            titles.append((i + 1, title_match.group(1)))
    title = titles[0] if titles else None
    if title is None or not title[1]:
        report.violations.append(Violation(
            "MISSING_TITLE", 1, "no `# <trackedName>` title line"))
    else:
        report.tracked_name = title[1]
        if _ANONYMOUS_RE.search(title[1]):
            report.violations.append(Violation(
                "ANONYMOUS_NAME", title[0],
                f"first-gate name {title[1]!r} is an anonymous FUN_* label; "
                "use the tracked/table name or an honest descriptive name"))
    for duplicate_line, duplicate_text in titles[1:]:
        report.violations.append(Violation(
            "DUPLICATE_TITLE", duplicate_line,
            f"additional H1 title {duplicate_text!r} makes identity ambiguous"))

    # -- filename stem identity -------------------------------------------
    stem = path.stem
    stem_match = _STEM_RE.fullmatch(stem)
    if stem_match is None:
        report.violations.append(Violation(
            "BAD_STEM", 1,
            f"filename stem {stem!r} is not <trackedName>__<8 lowercase hex "
            "digits> per the factory brief"))
    else:
        if report.tracked_name is not None and stem_match.group("name") != report.tracked_name:
            report.violations.append(Violation(
                "NAME_STEM_MISMATCH", title[0] if title else 1,
                f"title {report.tracked_name!r} does not match filename stem "
                f"name {stem_match.group('name')!r}"))
        if _ANONYMOUS_RE.search(stem_match.group("name")):
            report.violations.append(Violation(
                "ANONYMOUS_NAME", 1,
                f"filename stem name {stem_match.group('name')!r} is an "
                "anonymous FUN_* label"))

    # -- address block ------------------------------------------------------
    addresses: list[tuple[int, str]] = []
    for i, ln in enumerate(lines):
        if outside_fence[i] and (match := _VA_LINE_RE.match(ln)) is not None:
            addresses.append((i + 1, match.group(1)))
    address = addresses[0] if addresses else None
    if address is None:
        report.violations.append(Violation(
            "MISSING_ADDRESS", 1, "no `> Address: `<va>`` block"))
    else:
        report.address_line = address[0]
        normalized = normalize_va(address[1])
        if normalized is None:
            report.violations.append(Violation(
                "BAD_ADDRESS", address[0],
                f"address {address[1]!r} is not a hex VA like 0x00404dd0"))
        else:
            report.normalized_va = normalized
            if address[1] != normalized:
                report.violations.append(Violation(
                    "NONCANONICAL_ADDRESS", address[0],
                    f"address text {address[1]!r} must use canonical spelling "
                    f"{normalized!r}"))
            if stem_match is not None:
                stem_va = "0x" + stem_match.group("hex8")
                if stem_va != normalized:
                    report.violations.append(Violation(
                        "VA_STEM_MISMATCH", address[0],
                        f"filename VA {stem_va} does not match address block "
                        f"{normalized}"))
    for duplicate_line, duplicate_text in addresses[1:]:
        report.violations.append(Violation(
            "DUPLICATE_ADDRESS", duplicate_line,
            f"additional Address block {duplicate_text!r} makes identity ambiguous"))

    # -- required sections ---------------------------------------------------
    sections = _section_bodies(lines, outside_fence)
    present: dict[str, tuple[int, list[str]]] = {}
    for canonical, line_no, body in sections:
        if canonical in present:
            report.violations.append(Violation(
                "DUPLICATE_SECTION", line_no,
                f"section {canonical!r} appears more than once"))
            continue
        present[canonical] = (line_no, body)
    for required in REQUIRED_SECTIONS:
        if required not in present:
            report.violations.append(Violation(
                "MISSING_SECTION", 1,
                f"required section `## {required}` is absent (dropping a "
                "section is not the honest form; use unknown/not_applicable)"))
    for canonical, (line_no, body) in present.items():
        content = _content_lines(body, line_no)
        meaningful = [
            item for item in content
            if _FENCE_OPEN_RE.match(item[1]) is None
        ]
        if not meaningful:
            report.violations.append(Violation(
                "EMPTY_SECTION", line_no,
                f"section `{canonical}` has no content line; state "
                "unknown/not_applicable/not_determinable instead"))
        elif all(_placeholder_only(text_line) for _, text_line in meaningful):
            report.violations.append(Violation(
                "PLACEHOLDER_SECTION", meaningful[0][0],
                f"section `{canonical}` contains only placeholder content; state "
                "unknown/not_applicable/not_determinable or a bounded claim"))

    # -- confidence scale -----------------------------------------------------
    if "Confidence" in present:
        line_no, body = present["Confidence"]
        content = _content_lines(body, line_no)
        if content and not _CONFIDENCE_RE.match(content[0][1]):
            report.violations.append(Violation(
                "BAD_CONFIDENCE", content[0][0],
                "confidence must start `<0-4> - <justification>` "
                "(dash may be - en dash or em dash)"))

    # -- digests ---------------------------------------------------------------
    identity_tokens: set[str] = set()
    if "Identity" in present:
        line_no, body = present["Identity"]
        for abs_line, text_line in _content_lines(body, line_no):
            if not outside_fence[abs_line - 1]:
                continue
            if re.match(r"^\s*-\s*Body\b", text_line, re.IGNORECASE) is None:
                continue
            label_at = text_line.lower().find("sha-256")
            if label_at >= 0:
                # Only the backticked token FOLLOWING the SHA-256 label is the
                # digest claim; earlier tokens are ranges, names, or prose.
                after = text_line[label_at + len("sha-256"):]
                token_match = _BACKTICK_RE.search(after)
                token = token_match.group(1).strip() if token_match else ""
                if re.fullmatch(r"[0-9a-f]{64}", token):
                    identity_tokens.add(token)
                else:
                    report.violations.append(Violation(
                        "BAD_DIGEST", abs_line,
                        f"`{token}` after SHA-256 is not a 64-digit lowercase "
                        "hex digest"))
                continue
            report.violations.append(Violation(
                "BAD_DIGEST", abs_line,
                "Body identity line does not carry a SHA-256 backticked digest"))
        if not identity_tokens:
            report.violations.append(Violation(
                "MISSING_BODY_DIGEST", line_no,
                "Identity carries no SHA-256 body digest; the factory "
                "skeleton requires the Body `…` SHA-256 line"))

    preamble_boundaries = [
        i for i, text_line in enumerate(lines)
        if outside_fence[i] and re.match(r"^##[ \t]+", text_line)
    ]
    if address is not None:
        preamble_boundaries.append(address[0] - 1)
    preamble_end = min(preamble_boundaries, default=len(lines))
    image_claims = [
        (i + 1, match.group(1).strip())
        for i, text_line in enumerate(lines)
        if i < preamble_end
        and outside_fence[i]
        and (match := _IMAGE_SHA_LINE_RE.search(text_line)) is not None
    ]
    if not image_claims:
        report.violations.append(Violation(
            "MISSING_IMAGE_DIGEST", 1,
            "no Binary: BEA.exe SHA-256 image identity claim with a "
            "backticked digest"))
    else:
        for abs_line, token in image_claims:
            if token != PRISTINE_IMAGE_SHA256:
                report.violations.append(Violation(
                    "IMAGE_SHA_MISMATCH", abs_line,
                    f"image SHA-256 {token!r} does not equal pristine specimen "
                    f"{PRISTINE_IMAGE_SHA256}"))

    # -- evidence path existence ---------------------------------------------
    if "Evidence" in present:
        line_no, body = present["Evidence"]
        resolved_repo_root = repo_root.resolve()
        for abs_line, text_line in _content_lines(body, line_no):
            if not outside_fence[abs_line - 1]:
                continue
            for match in _BACKTICK_RE.finditer(text_line):
                token = match.group(1).strip()
                if not _repo_path_claim(token):
                    continue  # absolute paths, packets, free text: not repo claims
                if ".." in token.split("/"):
                    report.violations.append(Violation(
                        "EVIDENCE_PATH_OUTSIDE_REPO", abs_line,
                        f"evidence path {token!r} uses parent traversal"))
                    continue
                candidate = (resolved_repo_root / token).resolve()
                try:
                    candidate.relative_to(resolved_repo_root)
                except ValueError:
                    report.violations.append(Violation(
                        "EVIDENCE_PATH_OUTSIDE_REPO", abs_line,
                        f"evidence path {token!r} escapes the repository root"))
                    continue
                if candidate.exists():
                    continue
                if any(token.startswith(prefix + "/") or token == prefix
                       for prefix in submodule_prefixes):
                    continue  # registered submodule; tree may be unmaterialized
                report.violations.append(Violation(
                    "EVIDENCE_PATH_MISSING", abs_line,
                    f"evidence cites {token!r} which does not exist in the repo"))

    return report


def collect_contract_files(roots: list[Path]) -> list[Path]:
    files: set[Path] = set()
    for root in roots:
        files.update(p for p in root.rglob("*.md") if p.is_file())
    return sorted(files, key=lambda p: str(p))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contracts_root", type=str, help="tree of contract .md files")
    parser.add_argument("--repo-root", type=str, default=None,
                        help="repository root for evidence existence checks "
                             "(default: the repo this tool lives in)")
    arguments = parser.parse_args(argv)

    root = Path(arguments.contracts_root)
    repo_root = Path(arguments.repo_root) if arguments.repo_root else Path(__file__).resolve().parents[1]
    if not root.is_dir():
        print(f"error: contracts root not found: {root}")
        return 2

    files = collect_contract_files([root])
    if not files:
        print(f"error: no .md files found under {root}")
        return 2

    submodule_prefixes = parse_gitmodules_paths(repo_root)
    reports = [
        validate_file(path, path.relative_to(root).as_posix(),
                      submodule_prefixes, repo_root)
        for path in files
    ]

    # Cross-file identity: normalized VAs and tracked names are unique keys.
    va_claims: dict[str, tuple[str, int]] = {}
    name_claims: dict[str, str] = {}
    for report in reports:
        rel = report.relative
        if report.normalized_va is not None:
            prior = va_claims.get(report.normalized_va)
            if prior is not None:
                report.violations.append(Violation(
                    "DUPLICATE_VA", max(report.address_line, 1),
                    f"VA {report.normalized_va} already claimed by {prior[0]}:"
                    f"{prior[1]}"))
            else:
                va_claims[report.normalized_va] = (rel, max(report.address_line, 1))
        if report.tracked_name is not None:
            key = report.tracked_name.casefold()
            prior = name_claims.get(key)
            if prior is not None:
                report.violations.append(Violation(
                    "DUPLICATE_NAME", 1,
                    f"tracked name {report.tracked_name!r} already titled in "
                    f"{prior}"))
            else:
                name_claims[key] = rel

    diagnostics: list[tuple[str, int, str, str]] = []
    for report in reports:
        rel = report.relative
        for violation in report.violations:
            diagnostics.append((rel, violation.line, violation.code, violation.message))
    diagnostics.sort()

    for rel, line, code, message in diagnostics:
        print(f"{rel}: {line}: [{code}] {message}")
    violation_count = len(diagnostics)
    if violation_count:
        touched = len({d[0] for d in diagnostics})
        print(f"{violation_count} violation(s) in {touched} file(s) of "
              f"{len(reports)} scanned")
        return 1
    print(f"OK: {len(reports)} file(s) validated, 0 violations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
