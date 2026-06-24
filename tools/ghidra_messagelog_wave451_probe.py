#!/usr/bin/env python3
"""Validate Wave451 MessageLog/overlay metadata hardening."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave451-messagelog-overlay-current"
COMMON_TAGS = {"static-reaudit", "messagelog-wave451", "retail-binary-evidence"}
EXPECTED_APPLY = {
    "updated": 11,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 5,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 11,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004b8850": target(
        "CMessageBox__RenderOverlay",
        "void __thiscall CMessageBox__RenderOverlay(void * this, int viewport_height)",
        ["CMessageBox overlay", "ret 0x4", "CMessage__WordWrapToLineBuffer", "rebuild parity remain unproven"],
        ["messagebox", "overlay", "render", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CMessageBox__StopVoicePlaybackIfNotInCutscene", "CMessage__WordWrapToLineBuffer", "CHud__RenderSegmentedMeterBar"],
    ),
    "0x004b8dd0": target(
        "CMessageLog__ctor_base",
        "void * __fastcall CMessageLog__ctor_base(void * this)",
        ["constructor", "pointer-set queue", "shared arrow texture", "returns this", "rebuild parity remain unproven"],
        ["messagelog", "constructor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Init", "DAT_00807418"],
    ),
    "0x004b8e50": target(
        "CMessageLog__scalar_deleting_dtor",
        "void * __thiscall CMessageLog__scalar_deleting_dtor(void * this, byte flags)",
        ["scalar-deleting destructor", "CMessageLog__dtor_base", "ret 0x4", "rebuild parity remain unproven"],
        ["messagelog", "destructor", "scalar-deleting-dtor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CMessageLog__dtor_base", "CDXMemoryManager__Free", "flags"],
    ),
    "0x004b8e70": target(
        "CMessageLog__LoadTextures",
        "void __fastcall CMessageLog__LoadTextures(void * this)",
        ["end-curve", "head-frame", "DAT_00807418", "rebuild parity remain unproven"],
        ["messagelog", "textures", "signature-corrected", "comment-hardened"],
        ["MessageLog_endcurve", "MessageLog_messge_headframe", "DAT_00807418"],
    ),
    "0x004b8ef0": target(
        "CMessageLog__EnqueueMessageNode",
        "void __thiscall CMessageLog__EnqueueMessageNode(void * this, void * message_node)",
        ["message_node", "this+0x18", "ret 0x4", "phantom second argument", "rebuild parity remain unproven"],
        ["messagelog", "queue", "signature-corrected", "comment-hardened"],
        ["message_node", "CSPtrSet__AddToHead"],
    ),
    "0x004b8f00": target(
        "CMessageLog__dtor_base",
        "void __fastcall CMessageLog__dtor_base(void * this)",
        ["base destructor", "queued message nodes", "texture", "CMonitor__Shutdown", "rebuild parity remain unproven"],
        ["messagelog", "destructor", "textures", "queue", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Clear", "CHud__DecrementCounter9C", "CMonitor__Shutdown"],
    ),
    "0x004b9010": target(
        "CMessageLog__RenderPanelFrame",
        "void __thiscall CMessageLog__RenderPanelFrame(void * this, int screen_x, int screen_y, int width, int height, float alpha)",
        ["panel", "ret 0x14", "screen_x", "alpha", "rebuild parity remain unproven"],
        ["messagelog", "render", "panel-frame", "signature-corrected", "comment-hardened"],
        ["screen_x", "screen_y", "CVBufTexture__DrawSpriteEx", "width", "height", "alpha"],
    ),
    "0x004b93f0": target(
        "CMessageLog__Render",
        "void __thiscall CMessageLog__Render(void * this, int render_context)",
        ["active CMessageLog overlay", "scroll arrows", "ret 0x4", "rebuild parity remain unproven"],
        ["messagelog", "render", "input", "signature-corrected", "comment-hardened"],
        ["CMessageLog__RenderPanelFrame", "CMessageLog__RenderMessageCard", "Input__GetClickStateInRect"],
    ),
    "0x004b9a80": target(
        "CMessageLog__RenderMessageCard",
        "int __thiscall CMessageLog__RenderMessageCard(void * this, void * message_node, float screen_x, float screen_y, float alpha, int measure_only)",
        ["message_node", "ret 0x14", "measure_only", "card height", "rebuild parity remain unproven"],
        ["messagelog", "render", "message-card", "signature-corrected", "comment-hardened"],
        ["message_node", "CMessage__WordWrapToLineBuffer", "CMessageBox__SelectPortraitIndex", "measure_only"],
    ),
    "0x004b9ea0": target(
        "CMessageLog__ResetRenderState",
        "void __fastcall CMessageLog__ResetRenderState(void * this)",
        ["enables", "+0x2c", "+0x30", "+0x38", "+0x3c", "rebuild parity remain unproven"],
        ["messagelog", "state-reset", "signature-corrected", "comment-hardened"],
        ["0x28", "0x2c", "0x30", "0x38", "0x3c"],
    ),
    "0x004b9ec0": target(
        "CMessageLog__HandleInputCommand",
        "void __thiscall CMessageLog__HandleInputCommand(void * this, int controller_index, int button_code, float analog_value)",
        ["button 0x2a", "0x2b", "0x2e", "ret 0xc", "rebuild parity remain unproven"],
        ["messagelog", "input", "scroll", "name-corrected", "signature-corrected", "comment-hardened"],
        ["button_code", "CPauseMenu__InitPauseSession", "CRocket__RelinquishControllerOwnership", "CFrontEnd__PlaySound"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004b8850", "CHud__RenderBattleline"),
    ("0x004b8dd0", "CGame__InitRestartLoop"),
    ("0x004b8e70", "CGame__RunLevel"),
    ("0x004b8f00", "CMessageLog__scalar_deleting_dtor"),
    ("0x004b9010", "CDXEngine__RenderPostMissionOverlayAndMenu"),
    ("0x004b9010", "CMessageLog__Render"),
    ("0x004b9010", "CMessageLog__RenderMessageCard"),
    ("0x004b93f0", "CDXEngine__PostRender"),
    ("0x004b9a80", "CMessageLog__Render"),
    ("0x004b9a80", "CMessageLog__HandleInputCommand"),
    ("0x004b9ea0", "CGameInterface__HandleMenuSelection"),
    ("0x004b9ea0", "CPauseMenu__ButtonPressed"),
]

INSTRUCTION_TOKENS = {
    "0x004b8850": ["CMessageBox__RenderOverlay\tRET\t0x4"],
    "0x004b8e50": ["CMessageLog__scalar_deleting_dtor\tRET\t0x4"],
    "0x004b8ef0": ["CMessageLog__EnqueueMessageNode\tRET\t0x4"],
    "0x004b9010": ["CMessageLog__RenderPanelFrame\tRET\t0x14"],
    "0x004b93f0": ["CMessageLog__Render\tRET\t0x4"],
    "0x004b9a80": ["CMessageLog__RenderMessageCard\tRET\t0x14"],
    "0x004b9ec0": ["CMessageLog__HandleInputCommand\tRET\t0xc"],
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry"):
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


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    return read_text(matches[0]) if matches else ""


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def check_log(base: Path, filename: str, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(base / filename)
    if not text:
        failures.append(f"{filename}: missing or empty")
        return
    summary = parse_summary(text)
    if summary != expected:
        failures.append(f"{filename}: summary mismatch expected {expected}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"{filename}: unexpected failure token {token!r}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{filename}: missing Ghidra save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
    if len(metadata) != len(TARGETS):
        failures.append(f"post_metadata.tsv: expected {len(TARGETS)} rows, got {len(metadata)}")
    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing post_metadata row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')!r}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')!r}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: overclaim token in comment {token!r}")
        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
            continue
        actual_tags = {tag.strip() for tag in re.split(r"[;,]", tag_row.get("tags", "")) if tag.strip()}
        missing_tags = set(spec["tags"]) - actual_tags  # type: ignore[arg-type]
        if missing_tags:
            failures.append(f"{address}: missing tags {sorted(missing_tags)}")


def check_decompiles(base: Path, failures: list[str]) -> None:
    for address, spec in TARGETS.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"{address}: missing post-decomp text")
            continue
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(EXPECTED_XREF_EDGES):
        failures.append(f"post_xrefs.tsv: expected at least {len(EXPECTED_XREF_EDGES)} rows, got {len(rows)}")
    found = {(row.get("target_addr", ""), row.get("from_function", "")) for row in rows}
    for edge in EXPECTED_XREF_EDGES:
        if edge not in found:
            failures.append(f"post_xrefs.tsv: missing edge {edge}")


def check_instruction_tokens(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post_instructions_full.tsv") or read_text(base / "pre_instructions_full.tsv")
    if not text:
        failures.append("post_instructions_full.tsv/pre_instructions_full.tsv: missing instruction export")
        return
    for address, tokens in INSTRUCTION_TOKENS.items():
        for token in tokens:
            if not token_present(text, token):
                failures.append(f"{address}: missing instruction token {token!r}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_log(base, "apply.log", EXPECTED_APPLY, failures)
    check_log(base, "apply_verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_decompiles(base, failures)
    check_xrefs(base, failures)
    check_instruction_tokens(base, failures)
    return ("PASS" if not failures else "FAIL", failures)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE, help="Wave451 evidence directory")
    parser.add_argument("--check", action="store_true", help="Fail nonzero on validation failures")
    parser.add_argument("--json", type=Path, help="Optional JSON report path")
    args = parser.parse_args(argv)

    status, failures = run_checks(args.base)
    report = {
        "status": status,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "base": relative_or_absolute(args.base),
        "targetCount": len(TARGETS),
        "failures": failures,
    }

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Wave451 MessageLog probe: {status}")
    print(f"Base: {relative_or_absolute(args.base)}")
    print(f"Targets: {len(TARGETS)}")
    for failure in failures:
        print(f"- {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
