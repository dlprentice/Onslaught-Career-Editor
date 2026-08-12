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
    / "ghidra-function-name-table-2026-08-12.tsv"
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
    starts: list[int]
    ends: list[int]
    labels: list[str]
    text_lo: int
    text_hi: int
    source: str

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


def load_table(path: Path) -> NameTable:
    entry: dict[str, str] = {}
    spans: list[tuple[int, int, str]] = []
    text_lo, text_hi = 0x00401000, 0x005D7FFF
    with path.open(encoding="utf-8") as handle:
        header: list[str] | None = None
        for raw in handle:
            line = raw.rstrip("\n")
            if not line:
                continue
            if line.startswith("#"):
                match = re.match(r"#\s*text_range:\s*(0x[0-9a-fA-F]+)-(0x[0-9a-fA-F]+)", line)
                if match:
                    text_lo = int(match.group(1), 16)
                    text_hi = int(match.group(2), 16)
                continue
            cells = line.split("\t")
            if header is None:
                header = [c.strip() for c in cells]
                continue
            row = dict(zip(header, cells))
            address = row.get("address", "").strip().lower()
            name = row.get("name", "").strip()
            if not address or not name:
                continue
            entry[address] = name
            try:
                lo = int(row.get("bodyMin", address), 16)
                hi = int(row.get("bodyMax", address), 16)
            except ValueError:
                continue
            spans.append((lo, hi, name))
    if not entry:
        raise ValueError(f"name table has no rows: {path}")
    spans.sort()
    return NameTable(
        entry=entry,
        starts=[s[0] for s in spans],
        ends=[s[1] for s in spans],
        labels=[s[2] for s in spans],
        text_lo=text_lo,
        text_hi=text_hi,
        source=str(path),
    )


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


def run(doc_root: Path, table_path: Path, include_prose: bool, strict: bool,
        report_path: Path | None) -> int:
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

    lines: list[str] = []
    lines.append(f"documents scanned      : {len(docs)}")
    lines.append(f"name table             : {table.source}")
    lines.append(f"table rows             : {len(table.entry)}")
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
    return run(args.docs, args.table, args.include_prose, args.strict, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
