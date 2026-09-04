#!/usr/bin/env python3
"""Re-validate per-function RE notes against a current Ghidra function-name table.

Every document under ``reverse-engineering/binary-analysis/functions/`` asserts,
in one form or another, "at address A the Ghidra symbol is N". Those documents
outlive the database they describe: between 2026-04 and 2026-07 the live
maintainer project absorbed an RTTI re-prefix wave, a 533-name vtable wave, and
several deliberate demotions. A note that still asserts a withdrawn name is
worse than no note, because it looks authoritative.

This check reads the tracked name table, re-resolves every assertion, and exits
non-zero when any of them has drifted.

Exit codes
----------
0   every extracted assertion resolves to the current name (or carries an
    accepted, still-accurate drift marker)
1   at least one assertion names something the table does not
2   the check could not run -- missing table, unreadable inputs, bad arguments.
    Never silently succeeds: "I could not look" is not "I found no problem".

Assertion forms that gate
-------------------------
header   ``# <Symbol>`` plus ``> Address: `0x...`` in the first lines of a
         per-function note. One assertion per document; the strongest form,
         because the filename, the title and the address are the document's
         own identity claim.
table    a markdown table row whose first cell is exactly a backticked address
         and whose second cell is an identifier.
pair     a ``` `0xADDRESS Symbol` ``` code span appearing inside a markdown
         table row.
current  an explicit ``ghidra-current-name`` marker in an active synthesis
         document. These focused markers gate current prose without treating
         every deliberately quoted historical name as current.

Prose ``0xADDRESS Symbol`` spans outside tables are scanned only under
``--include-prose`` and never gate. That is deliberate, not laziness: these
documents quote superseded names on purpose. ``DXFMV.cpp.md`` contains

    Wave802 corrected `0x00465640 CLTShell__InvokeWithLoadingTransitionGate`
    to `0x00465640 CFMV__PlayFullscreenWithLoadingGate`.

Gating on prose would report the left-hand side as drift, i.e. would fail a
document precisely because it recorded the correction properly. A gate that
punishes correct history gets switched off.

Accepting a drift
-----------------
When a name legitimately moved and the note was updated with a dated supersede
paragraph, add a marker line to that note:

    <!-- ghidra-name-drift-accepted: 0x00406fc0 CBattleEngine__AddTrackedActiveReader (2026-07-28) -->

The marker names the address and the name that is current *at the time of
acceptance*. The check passes only while the table still agrees with the
marker, so a later rename re-opens the finding instead of being absorbed by a
permanent exemption.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DOC_ROOT = REPO_ROOT / "reverse-engineering" / "binary-analysis" / "functions"
DEFAULT_TABLE = (
    REPO_ROOT
    / "reverse-engineering"
    / "binary-analysis"
    / "ghidra-function-name-table-2026-08-31.tsv"
)
BASELINE_TABLE = (
    REPO_ROOT
    / "reverse-engineering"
    / "binary-analysis"
    / "ghidra-function-name-table-2026-08-17.tsv"
)
CURRENT_CLAIM_DOCS = (REPO_ROOT / "reverse-engineering" / "ghidra-functions.md",)

EXPECTED_COLUMNS = ("address", "name", "bodyMin", "bodyMax")
EXPECTED_CURRENT_ROWS = 8_329
EXPECTED_CURRENT_NAME_DELTA = 37
EXPECTED_CURRENT_TABLE_SHA256 = (
    "73c913ac542133d60b08c7a6dd7d7f4722a679643f2f9e4a958451e8f210cb02"
)
EXPECTED_BASELINE_TABLE_SHA256 = (
    "4590dff93f4ee85c5a5c3450139b2e696118646af3401f6eb9719dc4237d3213"
)
REQUIRED_CURRENT_PROVENANCE = (
    "# Projection date: 2026-08-31",
    "# Specimen SHA-256: 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
    "# Source  : local-lab/ghidra-linux-12.1.3-activation-20260830-v1/semantic-post/",
    "#           db18635-ghidra12.1.3.functions.tsv",
    "# Source bytes: 7193456",
    "# Source SHA-256: 8bff8a24f27161c6c654c51a639bfdc8c8ba0b32caff2b2a3847be08be414603",
    "# Receipt : local-lab/ghidra-linux-12.1.3-activation-20260830-v1/receipts/",
    "#           linux-ghidra12.1.3-activation-db18635-complete.json",
    "# Receipt SHA-256: e463284c6c409dc971099db31140e8a7a644a4d563c3a6cdb1d6b02c3ed33817",
    "# Rows    : 8329 internal functions; this is a discovered census, not a final ceiling.",
    "# text_range: 0x00401000-0x005d7fff",
)

# These two files intentionally do not assert a current address/name identity:
# one is a source-string cross-reference survey and one is a link-stability
# alias. Every other function-note document must yield at least one assertion
# under --strict so a newly unsupported Markdown form cannot pass unseen.
ZERO_ASSERTION_ALLOWLIST = {
    "Bomber.cpp.md",
    "Career.cpp/CCareer__GetUnlockedGoodieCount.md",
}

SYMBOL = r"[A-Za-z_][A-Za-z0-9_@.]*"
# Ghidra retains a small number of compiler helper spellings such as
# `` `vector_constructor_iterator' ``. Documentation assertions deliberately
# use the narrower SYMBOL grammar, while the complete oracle must admit those
# exact saved names.
TABLE_SYMBOL = r"[A-Za-z_`][A-Za-z0-9_@.`']*"
RE_HEADING = re.compile(r"^#\s+(" + SYMBOL + r")\s*$")
RE_HEADER_ADDRESS = re.compile(r"\bAddress\s*:[^\n]*?`?(0x[0-9A-Fa-f]{6,8})")
RE_EXPLICIT_HEADER_PAIR = re.compile(
    r"`(0x[0-9A-Fa-f]{6,8})`\s*\(\s*`(" + SYMBOL + r")`\s*\)"
)
RE_CURRENT_HEADER_NAME = re.compile(
    r"\b(?:Current\s+(?:saved\s+name|static\s+identity)|now\s+named)"
    r"[^`\n]*`(" + SYMBOL + r")`",
    re.IGNORECASE,
)
RE_NOW_NAMED_PAIR = re.compile(
    r"`(0x[0-9A-Fa-f]{6,8})`[^\n]*\bnow\s+named[^`\n]*`(" + SYMBOL + r")`",
    re.IGNORECASE,
)
RE_BARE_ADDRESS_CELL = re.compile(r"^`?(0x[0-9A-Fa-f]{6,8})`?$")
RE_BARE_SYMBOL_CELL = re.compile(r"^`?(" + SYMBOL + r")`?$")
RE_SIGNATURE_SYMBOL = re.compile(r"\b(" + SYMBOL + r")\s*\(")
RE_SIGNATURE_COLUMN = re.compile(
    r"\b(name|symbol|label|signature|saved\s+state|current)\b",
    re.IGNORECASE,
)
RE_ADDRESS_NAME_PAIR = re.compile(r"`(0x[0-9A-Fa-f]{6,8})\s+(" + SYMBOL + r")`")
RE_SEPARATOR_CELL = re.compile(r"^:?-{3,}:?$")
RE_ACCEPTED = re.compile(
    r"<!--\s*ghidra-name-drift-accepted:\s*(0x[0-9A-Fa-f]{6,8})\s+(" + SYMBOL + r")"
)
RE_CURRENT_CLAIM = re.compile(
    r"<!--\s*ghidra-current-name:\s*(0x[0-9A-Fa-f]{8})\s+(" + SYMBOL + r")\s*-->"
)
RE_CANONICAL_ADDRESS = re.compile(r"0x[0-9a-f]{8}")

# A column whose heading matches this holds a name the document is deliberately
# recording as no longer current. DXMemBuffer.cpp.md carries a whole
# "## Superseded Labels" table of them; reading column 2 blindly reported all
# fourteen rows as drift, i.e. failed the document for documenting the rename
# properly. When such a table also has a "Current ..." column, that column is
# read instead, which turns the same rows into real assertions.
RE_SUPERSEDED_HEADING = re.compile(
    r"\b(superseded|legacy|old|previous|former|stale|historic(al)?|alias|was)\b",
    re.IGNORECASE,
)
RE_CURRENT_HEADING = re.compile(r"\bcurrent\b", re.IGNORECASE)

OK = "OK"
DRIFT = "DRIFT"
UNRESOLVED = "UNRESOLVED"
ACCEPTED = "ACCEPTED"


@dataclass(frozen=True)
class Assertion:
    path: str
    line: int
    form: str
    address: str
    name: str


@dataclass
class NameTable:
    """Address -> current Ghidra symbol, plus body extents for containment."""

    entry: dict[str, str]
    geometry: dict[str, tuple[int, int]]
    starts: list[int]
    ends: list[int]
    labels: list[str]
    text_lo: int
    text_hi: int
    source: str
    comments: tuple[str, ...]

    def lookup_entry(self, address: str) -> str | None:
        return self.entry.get(address)

    def lookup_containing(self, value: int) -> str | None:
        """Name of the function whose body covers ``value``, if any."""
        idx = bisect.bisect_right(self.starts, value) - 1
        if idx < 0:
            return None
        if value <= self.ends[idx]:
            return self.labels[idx]
        return None

    def in_text(self, value: int) -> bool:
        return self.text_lo <= value <= self.text_hi


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_table(path: Path) -> NameTable:
    entry: dict[str, str] = {}
    geometry: dict[str, tuple[int, int]] = {}
    spans: list[tuple[int, int, str]] = []
    text_lo, text_hi = 0x00401000, 0x005D7FFF
    text_range_seen = False
    comments: list[str] = []
    with path.open(encoding="utf-8") as handle:
        header: list[str] | None = None
        for line_number, raw in enumerate(handle, start=1):
            line = raw.rstrip("\n")
            if not line:
                continue
            if line.startswith("#"):
                comments.append(line)
                match = re.match(r"#\s*text_range:\s*(0x[0-9a-fA-F]+)-(0x[0-9a-fA-F]+)", line)
                if match:
                    if text_range_seen:
                        raise ValueError(f"duplicate text_range declaration at {path}:{line_number}")
                    text_lo = int(match.group(1), 16)
                    text_hi = int(match.group(2), 16)
                    if text_lo > text_hi:
                        raise ValueError(f"reversed text_range at {path}:{line_number}")
                    text_range_seen = True
                continue
            cells = line.split("\t")
            if header is None:
                header = [c.strip() for c in cells]
                if tuple(header) != EXPECTED_COLUMNS:
                    raise ValueError(
                        f"name table columns differ at {path}:{line_number}: "
                        f"expected {EXPECTED_COLUMNS}, got {tuple(header)}"
                    )
                continue
            if len(cells) != len(EXPECTED_COLUMNS):
                raise ValueError(
                    f"name table row has {len(cells)} columns at {path}:{line_number}; "
                    f"expected {len(EXPECTED_COLUMNS)}"
                )
            row = dict(zip(header, (cell.strip() for cell in cells), strict=True))
            address = row["address"]
            name = row["name"]
            body_min = row["bodyMin"]
            body_max = row["bodyMax"]
            if RE_CANONICAL_ADDRESS.fullmatch(address) is None:
                raise ValueError(f"non-canonical address at {path}:{line_number}: {address!r}")
            if re.fullmatch(TABLE_SYMBOL, name) is None:
                raise ValueError(f"invalid symbol at {path}:{line_number}: {name!r}")
            if address in entry:
                raise ValueError(f"duplicate function address at {path}:{line_number}: {address}")
            if (
                RE_CANONICAL_ADDRESS.fullmatch(body_min) is None
                or RE_CANONICAL_ADDRESS.fullmatch(body_max) is None
            ):
                raise ValueError(
                    f"non-canonical body range at {path}:{line_number}: "
                    f"{body_min!r}-{body_max!r}"
                )
            try:
                value = int(address, 16)
                lo = int(body_min, 16)
                hi = int(body_max, 16)
            except ValueError:
                raise ValueError(f"invalid hexadecimal row at {path}:{line_number}") from None
            if not lo <= value <= hi:
                raise ValueError(
                    f"entry lies outside body range at {path}:{line_number}: "
                    f"{address} not in {body_min}-{body_max}"
                )
            entry[address] = name
            geometry[address] = (lo, hi)
            spans.append((lo, hi, name))
    if header is None:
        raise ValueError(f"name table has no header: {path}")
    if not entry:
        raise ValueError(f"name table has no rows: {path}")
    spans.sort()
    return NameTable(
        entry=entry,
        geometry=geometry,
        starts=[s[0] for s in spans],
        ends=[s[1] for s in spans],
        labels=[s[2] for s in spans],
        text_lo=text_lo,
        text_hi=text_hi,
        source=str(path),
        comments=tuple(comments),
    )


def validate_current_table_contract(
    path: Path,
    baseline_path: Path = BASELINE_TABLE,
    *,
    expected_table_sha256: str = EXPECTED_CURRENT_TABLE_SHA256,
    expected_baseline_sha256: str = EXPECTED_BASELINE_TABLE_SHA256,
    expected_rows: int = EXPECTED_CURRENT_ROWS,
    expected_name_delta: int = EXPECTED_CURRENT_NAME_DELTA,
    required_provenance: tuple[str, ...] = REQUIRED_CURRENT_PROVENANCE,
) -> NameTable:
    """Validate the complete current projection, not merely referenced rows."""

    actual_table_sha256 = sha256_file(path)
    if actual_table_sha256 != expected_table_sha256:
        raise ValueError(
            f"current name table SHA-256 differs: expected {expected_table_sha256}, "
            f"got {actual_table_sha256}"
        )
    actual_baseline_sha256 = sha256_file(baseline_path)
    if actual_baseline_sha256 != expected_baseline_sha256:
        raise ValueError(
            f"2026-08-17 baseline table SHA-256 differs: expected "
            f"{expected_baseline_sha256}, got {actual_baseline_sha256}"
        )

    current = load_table(path)
    baseline = load_table(baseline_path)
    missing_provenance = [
        line for line in required_provenance if line not in current.comments
    ]
    if missing_provenance:
        raise ValueError(
            "current name table provenance is incomplete; missing: "
            + "; ".join(missing_provenance)
        )
    if len(current.entry) != expected_rows:
        raise ValueError(
            f"current name table row count differs: expected {expected_rows}, "
            f"got {len(current.entry)}"
        )
    if len(baseline.entry) != expected_rows:
        raise ValueError(
            f"2026-08-17 baseline row count differs: expected {expected_rows}, "
            f"got {len(baseline.entry)}"
        )
    if current.geometry != baseline.geometry:
        current_keys = set(current.geometry)
        baseline_keys = set(baseline.geometry)
        missing = sorted(baseline_keys - current_keys)
        added = sorted(current_keys - baseline_keys)
        moved = sorted(
            address
            for address in current_keys & baseline_keys
            if current.geometry[address] != baseline.geometry[address]
        )
        raise ValueError(
            "current/baseline address-body geometry differs: "
            f"missing={missing[:3]} added={added[:3]} moved={moved[:3]}"
        )
    name_delta = sum(
        current.entry[address] != baseline.entry[address]
        for address in current.entry
    )
    if name_delta != expected_name_delta:
        raise ValueError(
            f"current/baseline name delta differs: expected {expected_name_delta}, "
            f"got {name_delta}"
        )
    return current


def _cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in body.split("|")]


def extract(path: Path, text: str, include_prose: bool) -> list[Assertion]:
    rel = path.as_posix()
    lines = text.splitlines()
    found: list[Assertion] = []

    heading = RE_HEADING.match(lines[0]) if lines else None
    head_blob = "\n".join(lines[:10])
    if heading:
        addr = RE_HEADER_ADDRESS.search(head_blob)
        if addr:
            found.append(
                Assertion(rel, 1, "header", addr.group(1).lower(), heading.group(1))
            )

    explicit_pairs = [
        (number, pair)
        for number, line in enumerate(lines[:12], start=1)
        for pair in RE_EXPLICIT_HEADER_PAIR.finditer(line)
    ]
    for number, pair in explicit_pairs:
        found.append(
            Assertion(
                rel,
                number,
                "header-pair",
                pair.group(1).lower(),
                pair.group(2),
            )
        )

    for number, line in enumerate(lines[:12], start=1):
        now_named = RE_NOW_NAMED_PAIR.search(line)
        if now_named:
            found.append(
                Assertion(
                    rel,
                    number,
                    "current-pair",
                    now_named.group(1).lower(),
                    now_named.group(2),
                )
            )

    current_name = RE_CURRENT_HEADER_NAME.search(head_blob)
    current_address = RE_HEADER_ADDRESS.search(head_blob)
    if current_name and current_address:
        found.append(
            Assertion(
                rel,
                1,
                "current-header",
                current_address.group(1).lower(),
                current_name.group(1),
            )
        )

    headings: list[str] = []
    previous_row: list[str] = []
    for number, line in enumerate(lines, start=1):
        if not line.lstrip().startswith("|"):
            headings = []
            previous_row = []
            continue

        cells = _cells(line)
        if cells and all(RE_SEPARATOR_CELL.match(c) for c in cells if c):
            headings = previous_row
            previous_row = []
            continue

        # Some early per-function notes use a two-column identity table:
        #   | Property | Value |
        #   | Address  | `0x004f6430` |
        # The document heading is the symbol assertion in that form.
        if (
            heading
            and len(cells) >= 2
            and cells[0].strip("` ").lower() == "address"
            and RE_BARE_ADDRESS_CELL.match(cells[1])
        ):
            found.append(
                Assertion(
                    rel,
                    number,
                    "property",
                    RE_BARE_ADDRESS_CELL.match(cells[1]).group(1).lower(),
                    heading.group(1),
                )
            )

        name_column = _resolve_name_column(headings)
        name_match = None
        if cells and name_column is not None and name_column < len(cells):
            name_match = RE_BARE_SYMBOL_CELL.match(cells[name_column])
            if (
                name_match is None
                and name_column < len(headings)
                and RE_SIGNATURE_COLUMN.search(headings[name_column])
            ):
                name_match = RE_SIGNATURE_SYMBOL.search(cells[name_column])
        if (
            cells
            and RE_BARE_ADDRESS_CELL.match(cells[0])
            and name_column is not None
            and name_column < len(cells)
            and name_match
        ):
            found.append(
                Assertion(
                    rel,
                    number,
                    "table",
                    RE_BARE_ADDRESS_CELL.match(cells[0]).group(1).lower(),
                    name_match.group(1),
                )
            )

        for index, cell in enumerate(cells):
            if _is_superseded_column(headings, index):
                continue
            for pair in RE_ADDRESS_NAME_PAIR.finditer(cell):
                found.append(
                    Assertion(rel, number, "pair", pair.group(1).lower(), pair.group(2))
                )
        previous_row = cells

    if include_prose:
        for number, line in enumerate(lines, start=1):
            if line.lstrip().startswith("|"):
                continue
            for pair in RE_ADDRESS_NAME_PAIR.finditer(line):
                found.append(
                    Assertion(rel, number, "prose", pair.group(1).lower(), pair.group(2))
                )
    return found


def _is_superseded_column(headings: list[str], index: int) -> bool:
    if index >= len(headings):
        return False
    return bool(RE_SUPERSEDED_HEADING.search(headings[index]))


def _resolve_name_column(headings: list[str]) -> int | None:
    """Which column of an address-first table holds the name to validate."""
    if not headings:
        return 1
    if len(headings) > 1 and not RE_SUPERSEDED_HEADING.search(headings[1]):
        return 1
    for index, heading in enumerate(headings):
        if index == 0:
            continue
        if RE_CURRENT_HEADING.search(heading) and not RE_SUPERSEDED_HEADING.search(
            heading
        ):
            return index
    return None


def accepted_markers(text: str) -> dict[str, str]:
    return {m.group(1).lower(): m.group(2) for m in RE_ACCEPTED.finditer(text)}


def current_claims(path: Path, text: str) -> list[Assertion]:
    """Extract explicitly marked current-name claims from active synthesis docs."""

    claims: list[Assertion] = []
    seen: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in RE_CURRENT_CLAIM.finditer(line):
            address = match.group(1).lower()
            if address in seen:
                raise ValueError(
                    f"duplicate ghidra-current-name marker at {path}:{line_number}: "
                    f"{address}"
                )
            seen.add(address)
            claims.append(
                Assertion(
                    path.as_posix(), line_number, "current-claim", address, match.group(2)
                )
            )
    return claims


def judge(
    assertion: Assertion, table: NameTable, accepted: dict[str, str]
) -> tuple[str, str, str]:
    """Return (verdict, current_name, note)."""
    value = int(assertion.address, 16)
    if not table.in_text(value):
        return ("SKIP", "", "address is not in .text")

    current = table.lookup_entry(assertion.address)
    kind = "entry"
    if current is None:
        current = table.lookup_containing(value)
        kind = "interior"
    if current is None:
        return (UNRESOLVED, "", "no function covers this address in the current table")

    if current == assertion.name:
        return (OK, current, kind)

    marker = accepted.get(assertion.address)
    if marker is not None and marker == current:
        return (ACCEPTED, current, f"{kind}; accepted supersede marker")
    if marker is not None:
        return (
            DRIFT,
            current,
            f"{kind}; accepted marker says '{marker}' but the table now says "
            f"'{current}' -- the acceptance is itself stale",
        )
    return (DRIFT, current, kind)


def run(
    doc_root: Path,
    table_path: Path,
    include_prose: bool,
    strict: bool,
    report_path: Path | None,
    current_claim_docs: tuple[Path, ...] = (),
) -> int:
    if not doc_root.is_dir():
        print(f"UNAVAILABLE: document root not found: {doc_root}", file=sys.stderr)
        return 2
    if not table_path.is_file():
        print(
            f"UNAVAILABLE: Ghidra function-name table not found: {table_path}\n"
            "             This check abstains rather than passing. Regenerate the "
            "table or pass --table.",
            file=sys.stderr,
        )
        return 2
    try:
        if table_path.resolve() == DEFAULT_TABLE.resolve():
            table = validate_current_table_contract(table_path)
        else:
            table = load_table(table_path)
    except (OSError, ValueError) as exc:
        print(f"UNAVAILABLE: could not read name table: {exc}", file=sys.stderr)
        return 2

    docs = sorted(p for p in doc_root.rglob("*.md") if p.name != "_index.md")
    if not docs:
        print(f"UNAVAILABLE: no documents under {doc_root}", file=sys.stderr)
        return 2

    counts = {OK: 0, DRIFT: 0, UNRESOLVED: 0, ACCEPTED: 0, "SKIP": 0}
    drifts: list[tuple[Assertion, str, str]] = []
    unresolved: list[Assertion] = []
    zero_assertion_docs: list[str] = []
    current_claim_count = 0
    by_form: dict[str, dict[str, int]] = {}

    for doc in docs:
        text = doc.read_text(encoding="utf-8", errors="replace")
        accepted = accepted_markers(text)
        try:
            rel = doc.relative_to(REPO_ROOT)
        except ValueError:
            rel = doc
        assertions = extract(rel, text, include_prose)
        try:
            local_rel = doc.relative_to(doc_root).as_posix()
        except ValueError:
            local_rel = doc.name
        if not assertions and local_rel not in ZERO_ASSERTION_ALLOWLIST:
            zero_assertion_docs.append(rel.as_posix())
        for assertion in assertions:
            verdict, current, note = judge(assertion, table, accepted)
            counts[verdict] += 1
            bucket = by_form.setdefault(assertion.form, dict.fromkeys(counts, 0))
            bucket[verdict] += 1
            if verdict == DRIFT:
                drifts.append((assertion, current, note))
            elif verdict == UNRESOLVED:
                unresolved.append(assertion)

    for claim_doc in current_claim_docs:
        if not claim_doc.is_file():
            print(
                f"UNAVAILABLE: current-claim document not found: {claim_doc}",
                file=sys.stderr,
            )
            return 2
        try:
            rel = claim_doc.relative_to(REPO_ROOT)
        except ValueError:
            rel = claim_doc
        try:
            claims = current_claims(rel, claim_doc.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"UNAVAILABLE: could not read current-name claims: {exc}", file=sys.stderr)
            return 2
        if not claims:
            print(
                f"UNAVAILABLE: no ghidra-current-name claims in {rel}", file=sys.stderr
            )
            return 2
        current_claim_count += len(claims)
        for assertion in claims:
            verdict, current, note = judge(assertion, table, {})
            counts[verdict] += 1
            bucket = by_form.setdefault(assertion.form, dict.fromkeys(counts, 0))
            bucket[verdict] += 1
            if verdict == DRIFT:
                drifts.append((assertion, current, note))
            elif verdict == UNRESOLVED:
                unresolved.append(assertion)

    lines: list[str] = []
    lines.append(f"documents scanned      : {len(docs)}")
    lines.append(f"name table             : {table.source}")
    lines.append(f"table rows             : {len(table.entry)}")
    lines.append(f"focused current claims : {current_claim_count}")
    gated = counts[OK] + counts[DRIFT] + counts[ACCEPTED] + counts[UNRESOLVED]
    lines.append(f"assertions resolved    : {gated}")
    lines.append(f"  current              : {counts[OK]}")
    lines.append(f"  accepted supersede   : {counts[ACCEPTED]}")
    lines.append(f"  DRIFTED              : {counts[DRIFT]}")
    lines.append(f"  UNRESOLVED (abstain) : {counts[UNRESOLVED]}")
    lines.append(f"  skipped (not .text)  : {counts['SKIP']}")
    lines.append(f"  zero-assertion docs   : {len(zero_assertion_docs)}")
    for form in sorted(by_form):
        b = by_form[form]
        lines.append(
            f"  by form {form:<7}: ok={b[OK]} accepted={b[ACCEPTED]} "
            f"drift={b[DRIFT]} unresolved={b[UNRESOLVED]}"
        )

    if drifts:
        lines.append("")
        lines.append("DRIFTED assertions:")
        for assertion, current, note in drifts:
            lines.append(
                f"  {assertion.path}:{assertion.line} [{assertion.form}] "
                f"{assertion.address}\n"
                f"      document says : {assertion.name}\n"
                f"      Ghidra says   : {current}   ({note})"
            )
    if unresolved:
        lines.append("")
        lines.append("UNRESOLVED assertions (address covered by no function):")
        for assertion in unresolved:
            lines.append(
                f"  {assertion.path}:{assertion.line} [{assertion.form}] "
                f"{assertion.address} {assertion.name}"
            )
    if zero_assertion_docs:
        lines.append("")
        lines.append("ZERO-ASSERTION documents (unsupported identity form):")
        lines.extend(f"  {path}" for path in zero_assertion_docs)

    report = "\n".join(lines)
    print(report)
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report + "\n", encoding="utf-8")

    if counts[DRIFT]:
        print(
            f"\nFAIL: {counts[DRIFT]} assertion(s) name a symbol the current "
            "Ghidra table does not.",
            file=sys.stderr,
        )
        return 1
    if strict and counts[UNRESOLVED]:
        print(
            f"\nFAIL (--strict): {counts[UNRESOLVED]} assertion(s) could not be "
            "resolved against the current table.",
            file=sys.stderr,
        )
        return 1
    if strict and zero_assertion_docs:
        print(
            f"\nFAIL (--strict): {len(zero_assertion_docs)} document(s) yielded "
            "no current address/name assertion and are not explicit non-identity "
            "exceptions.",
            file=sys.stderr,
        )
        return 1
    print("\nPASS: every gated assertion matches the current Ghidra name table.")
    return 0


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------

_TABLE_FIXTURE = """# text_range: 0x00401000-0x005d7fff
address\tname\tbodyMin\tbodyMax
0x00401000\tCThing__Alpha\t0x00401000\t0x0040100f
0x00402000\tCThing__Beta\t0x00402000\t0x004020ff
"""

_DOC_CURRENT = """# CThing__Alpha

> Address: `0x00401000` | Source family: `references/Onslaught/Thing.cpp`
"""

_DOC_STALE = """# CThing__Gamma

> Address: `0x00401000` | Source family: `references/Onslaught/Thing.cpp`
"""

_DOC_ACCEPTED = """# CThing__Gamma

> Address: `0x00401000` | Source family: `references/Onslaught/Thing.cpp`

<!-- ghidra-name-drift-accepted: 0x00401000 CThing__Alpha (2026-07-28) -->
"""

_DOC_ACCEPT_STALE = """# CThing__Gamma

> Address: `0x00401000` | Source family: `references/Onslaught/Thing.cpp`

<!-- ghidra-name-drift-accepted: 0x00401000 CThing__Delta (2026-07-28) -->
"""

_DOC_TABLE_STALE = """# Thing.cpp Functions

| Address | Saved name |
| --- | --- |
| `0x00402000` | `CThing__Wrong` |
"""

_DOC_PAIR_INTERIOR = """# Thing.cpp Interior

| Address | Note |
| --- | --- |
| `0x00402040 CThing__Beta` | callsite inside the body |
"""

_DOC_PAIR_INTERIOR_STALE = """# Thing.cpp Interior

| Address | Note |
| --- | --- |
| `0x00402040 CThing__Wrong` | callsite inside the body |
"""

_DOC_PROSE_STALE = """# CThing__Beta

> Address: `0x00402000` | Source family: `references/Onslaught/Thing.cpp`

Wave801 corrected `0x00402000 CThing__Historic` to the current reading.
"""

_DOC_ORPHAN = """# CThing__Nowhere

> Address: `0x00403000` | Source family: `references/Onslaught/Thing.cpp`
"""

_DOC_DATA = """# Thing.cpp Data

| Address | Symbol |
| --- | --- |
| `0x00650f6c` | `g_SomeGlobal` |
"""

_DOC_PROPERTY_VALUE = """# CThing__Alpha

| Property | Value |
| --- | --- |
| Address | `0x00401000` |
"""

_DOC_SUPERSEDED_COLUMN = """# Thing.cpp Renames

| Address | Superseded label | Current label |
| --- | --- | --- |
| `0x00402000` | `CThing__Historic` | `CThing__Beta` |
"""

_DOC_SUPERSEDED_COLUMN_STALE = """# Thing.cpp Renames

| Address | Superseded label | Current label |
| --- | --- | --- |
| `0x00402000` | `CThing__Historic` | `CThing__NotBeta` |
"""

_DOC_SUPERSEDED_ONLY = """# Thing.cpp Renames

| Address | Superseded label |
| --- | --- |
| `0x00402000` | `CThing__Historic` |
"""

_DOC_PAIR_IN_SUPERSEDED_COLUMN = """# Thing.cpp Renames

| Note | Old reading |
| --- | --- |
| slot 0 | `0x00402000 CThing__Historic` |
"""

_DOC_EXPLICIT_HEADER_PAIRS = """# CThing__Topic

> Addresses: `0x00401000` (`CThing__Alpha`), `0x00402000` (`CThing__Beta`)
"""

_DOC_EXPLICIT_HEADER_PAIR_STALE = """# CThing__Topic

> Addresses: `0x00401000` (`CThing__Alpha`), `0x00402000` (`CThing__Wrong`)
"""

_DOC_STALE_PRIMARY_WITH_VALID_RELATED_PAIR = """# CThing__Wrong

> Address: `0x00402000`
>
> Related: `0x00401000` (`CThing__Alpha`)
"""

_DOC_DEPRECATED_CURRENT_HEADER = """# Deprecated: CThing__Historic

- **Address:** `0x00402000`
- **Current saved name:** `CThing__Beta`
"""

_DOC_CURRENT_SIGNATURE_TABLE = """# Thing.cpp Functions

| Address | Saved state |
| --- | --- |
| `0x00402000` | `void __fastcall CThing__Beta(void * this)` |
"""

_DOC_NO_ASSERTIONS = """# Thing.cpp survey

This page contains no current address/name identity.
"""


def _self_test() -> int:
    cases = [
        ("current header passes", {"a.md": _DOC_CURRENT}, False, False, 0),
        ("stale header fails", {"a.md": _DOC_STALE}, False, False, 1),
        ("accepted marker passes", {"a.md": _DOC_ACCEPTED}, False, False, 0),
        ("stale acceptance fails", {"a.md": _DOC_ACCEPT_STALE}, False, False, 1),
        ("stale table row fails", {"a.md": _DOC_TABLE_STALE}, False, False, 1),
        ("interior pair passes", {"a.md": _DOC_PAIR_INTERIOR}, False, False, 0),
        ("stale interior pair fails", {"a.md": _DOC_PAIR_INTERIOR_STALE}, False, False, 1),
        ("stale prose ignored by default", {"a.md": _DOC_PROSE_STALE}, False, False, 0),
        ("stale prose fails with --include-prose", {"a.md": _DOC_PROSE_STALE}, True, False, 1),
        ("orphan abstains by default", {"a.md": _DOC_ORPHAN}, False, False, 0),
        ("orphan fails under --strict", {"a.md": _DOC_ORPHAN}, False, True, 1),
        ("non-.text address skipped", {"a.md": _DOC_DATA}, False, False, 0),
        ("property/value identity passes",
         {"a.md": _DOC_PROPERTY_VALUE}, False, False, 0),
        ("superseded column is not read as a claim",
         {"a.md": _DOC_SUPERSEDED_COLUMN}, False, False, 0),
        ("a wrong 'Current label' column still fails",
         {"a.md": _DOC_SUPERSEDED_COLUMN_STALE}, False, False, 1),
        ("superseded-only table asserts nothing",
         {"a.md": _DOC_SUPERSEDED_ONLY}, False, False, 0),
        ("pair inside a superseded column is not read as a claim",
         {"a.md": _DOC_PAIR_IN_SUPERSEDED_COLUMN}, False, False, 0),
        ("explicit plural header pairs pass",
         {"a.md": _DOC_EXPLICIT_HEADER_PAIRS}, False, False, 0),
        ("a stale explicit plural header pair fails",
         {"a.md": _DOC_EXPLICIT_HEADER_PAIR_STALE}, False, False, 1),
        ("a related pair cannot hide a stale primary header",
         {"a.md": _DOC_STALE_PRIMARY_WITH_VALID_RELATED_PAIR}, False, False, 1),
        ("deprecated page gates its current saved name",
         {"a.md": _DOC_DEPRECATED_CURRENT_HEADER}, False, False, 0),
        ("signature table gates the function identifier",
         {"a.md": _DOC_CURRENT_SIGNATURE_TABLE}, False, False, 0),
        ("zero-assertion document passes only outside strict mode",
         {"a.md": _DOC_NO_ASSERTIONS}, False, False, 0),
        ("zero-assertion document fails under strict mode",
         {"a.md": _DOC_NO_ASSERTIONS}, False, True, 1),
        ("drift is found among many clean docs",
         {"a.md": _DOC_CURRENT, "b.md": _DOC_TABLE_STALE, "c.md": _DOC_PAIR_INTERIOR},
         False, False, 1),
    ]
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        table = base / "table.tsv"
        table.write_text(_TABLE_FIXTURE, encoding="utf-8")
        for index, (label, docs, prose, strict, expected) in enumerate(cases):
            root = base / f"case{index}"
            root.mkdir()
            for name, body in docs.items():
                (root / name).write_text(body, encoding="utf-8")
            devnull = open(os.devnull, "w", encoding="utf-8")
            saved_out, saved_err = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = devnull
            try:
                actual = run(root, table, prose, strict, None)
            finally:
                sys.stdout, sys.stderr = saved_out, saved_err
                devnull.close()
            status = "ok " if actual == expected else "FAIL"
            if actual != expected:
                failures += 1
            print(f"  [{status}] {label}: expected exit {expected}, got {actual}")

        missing = run(base / "case0", base / "no-such-table.tsv", False, False, None)
        status = "ok " if missing == 2 else "FAIL"
        if missing != 2:
            failures += 1
        print(f"  [{status}] missing table abstains: expected exit 2, got {missing}")

        def expect_error(label: str, expected: str, action: object) -> None:
            nonlocal failures
            try:
                action()  # type: ignore[operator]
            except ValueError as exc:
                ok = expected in str(exc)
                status = "ok " if ok else "FAIL"
                if not ok:
                    failures += 1
                print(f"  [{status}] {label}: {exc}")
                return
            failures += 1
            print(f"  [FAIL] {label}: malformed input was accepted")

        bad_schema = base / "bad-schema.tsv"
        bad_schema.write_text(
            "address\tname\tbodyMin\textra\n"
            "0x00401000\tCThing__Alpha\t0x00401000\t0x0040100f\n",
            encoding="utf-8",
        )
        expect_error(
            "exact four-column schema is required",
            "columns differ",
            lambda: load_table(bad_schema),
        )

        duplicate = base / "duplicate.tsv"
        duplicate.write_text(
            "address\tname\tbodyMin\tbodyMax\n"
            "0x00401000\tCThing__Alpha\t0x00401000\t0x0040100f\n"
            "0x00401000\tCThing__Beta\t0x00401000\t0x0040100f\n",
            encoding="utf-8",
        )
        expect_error(
            "duplicate addresses are rejected",
            "duplicate function address",
            lambda: load_table(duplicate),
        )

        baseline = base / "baseline.tsv"
        current = base / "current.tsv"
        baseline.write_text(
            "# fixture-provenance\n"
            "# text_range: 0x00401000-0x005d7fff\n"
            "address\tname\tbodyMin\tbodyMax\n"
            "0x00401000\tCThing__Alpha\t0x00401000\t0x0040100f\n"
            "0x00402000\tCThing__Beta\t0x00402000\t0x004020ff\n",
            encoding="utf-8",
        )
        current.write_text(
            "# fixture-provenance\n"
            "# text_range: 0x00401000-0x005d7fff\n"
            "address\tname\tbodyMin\tbodyMax\n"
            "0x00401000\tCThing__Alpha\t0x00401000\t0x0040100f\n"
            "0x00402000\tCThing__Gamma\t0x00402000\t0x004020ff\n",
            encoding="utf-8",
        )
        try:
            validated = validate_current_table_contract(
                current,
                baseline,
                expected_table_sha256=sha256_file(current),
                expected_baseline_sha256=sha256_file(baseline),
                expected_rows=2,
                expected_name_delta=1,
                required_provenance=("# fixture-provenance",),
            )
            ok = validated.entry["0x00402000"] == "CThing__Gamma"
        except ValueError:
            ok = False
        status = "ok " if ok else "FAIL"
        failures += 0 if ok else 1
        print(f"  [{status}] complete table contract accepts exact geometry + one rename")

        moved = base / "moved.tsv"
        moved.write_text(
            current.read_text(encoding="utf-8").replace("0x004020ff", "0x004020fe"),
            encoding="utf-8",
        )
        expect_error(
            "address/body geometry drift is rejected",
            "geometry differs",
            lambda: validate_current_table_contract(
                moved,
                baseline,
                expected_table_sha256=sha256_file(moved),
                expected_baseline_sha256=sha256_file(baseline),
                expected_rows=2,
                expected_name_delta=1,
                required_provenance=("# fixture-provenance",),
            ),
        )
        expect_error(
            "exact name delta is required",
            "name delta differs",
            lambda: validate_current_table_contract(
                current,
                baseline,
                expected_table_sha256=sha256_file(current),
                expected_baseline_sha256=sha256_file(baseline),
                expected_rows=2,
                expected_name_delta=2,
                required_provenance=("# fixture-provenance",),
            ),
        )
        expect_error(
            "required provenance is enforced",
            "provenance is incomplete",
            lambda: validate_current_table_contract(
                current,
                baseline,
                expected_table_sha256=sha256_file(current),
                expected_baseline_sha256=sha256_file(baseline),
                expected_rows=2,
                expected_name_delta=1,
                required_provenance=("# missing-provenance",),
            ),
        )

        claim_doc = base / "claims.md"
        claim_doc.write_text(
            "<!-- ghidra-current-name: 0x00402000 CThing__Gamma -->\n",
            encoding="utf-8",
        )
        claims = current_claims(claim_doc, claim_doc.read_text(encoding="utf-8"))
        claim_table = load_table(current)
        claim_ok = len(claims) == 1 and judge(claims[0], claim_table, {})[0] == OK
        status = "ok " if claim_ok else "FAIL"
        failures += 0 if claim_ok else 1
        print(f"  [{status}] focused current-name claim resolves through the oracle")
        stale_claim = Assertion(
            claim_doc.as_posix(), 1, "current-claim", "0x00402000", "CThing__Wrong"
        )
        stale_ok = judge(stale_claim, claim_table, {})[0] == DRIFT
        status = "ok " if stale_ok else "FAIL"
        failures += 0 if stale_ok else 1
        print(f"  [{status}] stale focused current-name claim fails")

    if failures:
        print(f"\nSELF-TEST FAILED: {failures} case(s)", file=sys.stderr)
        return 1
    print("\nSELF-TEST PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--docs", type=Path, default=DEFAULT_DOC_ROOT)
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    parser.add_argument(
        "--include-prose",
        action="store_true",
        help="also gate on address+name spans outside markdown tables "
        "(noisy: these documents quote superseded names on purpose)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also fail when an asserted address is covered by no function",
    )
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()
    return run(
        args.docs,
        args.table,
        args.include_prose,
        args.strict,
        args.report,
        CURRENT_CLAIM_DOCS,
    )


if __name__ == "__main__":
    raise SystemExit(main())
