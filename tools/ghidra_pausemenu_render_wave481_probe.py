#!/usr/bin/env python3
"""Validate Wave481 pause-menu render owner/signature correction."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave481-render-menu-transition-004d11d0"

TARGET_PAUSE_RENDER = "0x004d11d0"
TARGET_RANGE_RENDER = "0x004a4810"

OLD_PAUSE_RENDER_NAME = "CEngine__RenderOverlayAndMenuTransitions"
NEW_PAUSE_RENDER_NAME = "CPauseMenu__Render"
RANGE_RENDER_NAME = "CMenuItemRange__Render"

EXPECTED_PAUSE_SIGNATURE = "short * __thiscall CPauseMenu__Render(void * this)"
EXPECTED_RANGE_SIGNATURE = "short * __thiscall CMenuItemRange__Render(void * this, void * binding_context)"

EXPECTED_SUMMARIES = {
    "apply_pausemenu_render_wave481_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 1,
        "missing": 0,
        "bad": 0,
    },
    "apply_pausemenu_render_wave481_apply.log": {
        "updated": 2,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 1,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_pausemenu_render_wave481_verify_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

COMMON_TAGS = {
    "comment-hardened",
    "frontend-menu",
    "pause-menu",
    "pausemenu-render-wave481",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}

EXPECTED_METADATA = {
    TARGET_PAUSE_RENDER: {
        "name": NEW_PAUSE_RENDER_NAME,
        "signature": EXPECTED_PAUSE_SIGNATURE,
        "comment_tokens": [
            "not a CEngine method",
            "GAME.GetPauseMenu()->Render()",
            "g_pOptionsContext",
            "PauseMenu__Init",
            "draws the black fade",
            "paired transition sprites",
            "returns the active range title text pointer",
            "runtime pause/options UI behavior",
            "rebuild parity remain unproven",
        ],
        "tags": COMMON_TAGS | {"owner-corrected", "render", "title-text-return"},
        "decompile_tokens": [
            NEW_PAUSE_RENDER_NAME,
            "short *",
            "void *this",
            "CMenuItemRange__Render(this",
            "CDXEngine__RenderMouseCursorSprite()",
        ],
    },
    TARGET_RANGE_RENDER: {
        "name": RANGE_RENDER_NAME,
        "signature": EXPECTED_RANGE_SIGNATURE,
        "comment_tokens": [
            "return-type correction",
            "FrontEnd_v2/FE_Blank.tga",
            "range title text pointer",
            "stored at this+0x04",
            "CPauseMenu__Render consumes that pointer",
            "source MenuItem.cpp body is absent",
            "runtime frontend behavior",
            "rebuild parity remain unproven",
        ],
        "tags": COMMON_TAGS | {"range", "title-text-return"},
        "decompile_tokens": [
            RANGE_RENDER_NAME,
            "short *",
            "void *binding_context",
            "CMenuItemDropdown__ClearPending()",
            "CMenuItemDropdown__ProcessPending()",
            "return *(short **)((int)this + 4)",
        ],
    },
}

EXPECTED_XREFS = {
    (TARGET_PAUSE_RENDER, "0x0053ee24", "CDXEngine__PostRender"),
    (TARGET_PAUSE_RENDER, "0x0051f71d", "CFEPOptions__Update"),
}

OVERCLAIMS = (
    "runtime pause/options ui behavior proven",
    "runtime frontend behavior proven",
    "exact source-body identity proven",
    "concrete cpausemenu layout proven",
    "rebuild parity proven",
    "fully re'ed",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "instruction_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"updated=(?P<updated>\d+)\s+skipped=(?P<skipped>\d+)\s+created=(?P<created>\d+)\s+"
        r"would_create=(?P<would_create>\d+)\s+renamed=(?P<renamed>\d+)\s+"
        r"would_rename=(?P<would_rename>\d+)\s+missing=(?P<missing>\d+)\s+bad=(?P<bad>\d+)",
        text,
    )
    if not match:
        return {}
    return {key: int(value) for key, value in match.groupdict().items()}


def check_summaries(base: Path, failures: list[str]) -> None:
    for filename, expected in EXPECTED_SUMMARIES.items():
        path = base / filename
        actual = parse_summary(path)
        if actual != expected:
            failures.append(f"{filename}: expected summary {expected}, got {actual or '<missing>'}")
        if "REPORT: Save succeeded" not in read_text(path):
            failures.append(f"{filename}: missing REPORT: Save succeeded")


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def strip_c_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//.*", "", text)


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    tag_rows = read_tsv(base / "post_tags.tsv")
    for address, expected in EXPECTED_METADATA.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: expected name {expected['name']}, got {row.get('name')}")
        if compact(row.get("signature", "")) != compact(expected["signature"]):
            failures.append(f"{address}: expected signature {expected['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in expected["comment_tokens"]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for overclaim in OVERCLAIMS:
            if token_present(comment, overclaim):
                failures.append(f"{address}: comment contains overclaim {overclaim!r}")

        tag_row = row_by_address(tag_rows, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            actual_tags = set(filter(None, re.split(r"[;,]\s*", tag_row.get("tags", ""))))
            missing_tags = set(expected["tags"]) - actual_tags
            if missing_tags:
                failures.append(f"{address}: missing tags {sorted(missing_tags)}")

        decompile = decompile_text_for(base, address)
        decompile_without_comments = strip_c_comments(decompile)
        for token in expected["decompile_tokens"]:
            if not token_present(decompile_without_comments, token):
                failures.append(f"{address}: decompile missing token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    actual = {
        (normalize_address(row.get("target_addr", "")), normalize_address(row.get("from_addr", "")), row.get("from_function", ""))
        for row in rows
    }
    for expected in EXPECTED_XREFS:
        if expected not in actual:
            failures.append(f"missing xref {expected}")
    range_callers = {
        row.get("from_function", "")
        for row in rows
        if normalize_address(row.get("target_addr", "")) == normalize_address(TARGET_RANGE_RENDER)
    }
    if NEW_PAUSE_RENDER_NAME not in range_callers:
        failures.append(f"{TARGET_RANGE_RENDER}: missing xref from {NEW_PAUSE_RENDER_NAME}")


def check_instructions(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    by_addr = {row.get("instruction_addr"): row for row in rows}
    expected = {
        "0x004d11d5": ("MOV", "ESI, ECX"),
        "0x004d154d": ("CALL", "0x004e5c90"),
        "0x004d1554": ("CALL", "0x004a4810"),
        "0x004d15ad": ("CALL", "0x00523a70"),
    }
    for address, (mnemonic, operand_token) in expected.items():
        row = by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing instruction row")
            continue
        if row.get("mnemonic") != mnemonic or not token_present(row.get("operands", ""), operand_token):
            failures.append(f"{address}: expected {mnemonic} {operand_token}, got {row.get('mnemonic')} {row.get('operands')}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_summaries(base, failures)
    check_metadata(base, failures)
    check_xrefs(base, failures)
    check_instructions(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave481 pause-menu render probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave481 pause-menu render probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
