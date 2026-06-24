#!/usr/bin/env python3
"""Validate the Wave375 frontend save/load Ghidra tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/frontend-save-load-wave375/current")
OUTPUT_NAME = "frontend-save-load.json"

COMMON_TAGS = {
    "static-reaudit",
    "frontend-save-load-wave375",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00461c40": target(
        "CFEPLoadGame__Init",
        "bool __thiscall CFEPLoadGame__Init(void * this)",
        [
            "function object created",
            "initializes load-game selection fields",
            "save slot to -1",
            "source-correlated",
            "remain unproven",
        ],
        ["CFEPLoadGame__Init", "0xffffffff", "return true"],
        ["frontend", "load-game", "function-boundary", "vtable-slot", "boundary-created", "signature-hardened", "comment-hardened"],
    ),
    "0x00461c60": target(
        "CFEPLoadGame__ButtonPressed",
        "void __thiscall CFEPLoadGame__ButtonPressed(void * this, int button, float value)",
        [
            "function object created",
            "frontend directional/select/back buttons",
            "selection fields",
            "CFrontEnd__SetPage",
            "remain unproven",
        ],
        ["CFEPLoadGame__ButtonPressed", "CFrontEnd__SetPage", "0xff"],
        ["frontend", "load-game", "input", "function-boundary", "vtable-slot", "boundary-created", "signature-hardened", "comment-hardened"],
    ),
    "0x00461d60": target(
        "CFEPLoadGame__Process",
        "void __thiscall CFEPLoadGame__Process(void * this, int state)",
        [
            "name/signature correction",
            "source-correlated Process",
            "active state",
            "CFEPLoadGame__DoLoad",
            "remain unproven",
        ],
        ["CFEPLoadGame__DoLoad", "DAT_00677614"],
        ["frontend", "load-game", "process", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00461d90": target(
        "CFEPLoadGame__Render",
        "void __thiscall CFEPLoadGame__Render(void * this, float transition, int dest_page)",
        [
            "name/signature correction",
            "source-correlated Render",
            "load-game title token",
            "DrawSlidingTextBordersAndMask",
            "remain unproven",
        ],
        ["CFrontEnd__DrawTitleBar", "0xd", "CFEPMultiplayerStart__RenderHelpPromptForSelection"],
        ["frontend", "load-game", "render", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00464620": target(
        "CFEPSaveGame__Init",
        "bool __thiscall CFEPSaveGame__Init(void * this)",
        [
            "function object created",
            "initializes save-game selection fields",
            "source-correlated",
            "returns true",
            "remain unproven",
        ],
        ["CFEPSaveGame__Init", "return true"],
        ["frontend", "save-game", "function-boundary", "vtable-slot", "boundary-created", "signature-hardened", "comment-hardened"],
    ),
    "0x00464630": target(
        "CFEPSaveGame__ButtonPressed",
        "void __thiscall CFEPSaveGame__ButtonPressed(void * this, int button, float value)",
        [
            "function object created",
            "frontend directional/select/back buttons",
            "selection fields",
            "CFrontEnd__SetPage",
            "remain unproven",
        ],
        ["CFEPSaveGame__ButtonPressed", "CFrontEnd__SetPage", "0xff"],
        ["frontend", "save-game", "input", "function-boundary", "vtable-slot", "boundary-created", "signature-hardened", "comment-hardened"],
    ),
    "0x00464730": target(
        "CFEPSaveGame__Process",
        "void __thiscall CFEPSaveGame__Process(void * this, int state)",
        [
            "function object created",
            "source-correlated Process",
            "CFEPSaveGame__CreateSave",
            "message-box overwrite/delete handling",
            "remain unproven",
        ],
        ["CFEPSaveGame__CreateSave", "DAT_00677614"],
        ["frontend", "save-game", "process", "function-boundary", "vtable-slot", "boundary-created", "signature-hardened", "comment-hardened"],
    ),
    "0x00464a80": target(
        "CFEPSaveGame__Render",
        "void __thiscall CFEPSaveGame__Render(void * this, float transition, int dest_page)",
        [
            "name/signature correction",
            "source-correlated Render",
            "save-game title token",
            "DrawSlidingTextBordersAndMask",
            "remain unproven",
        ],
        ["CFrontEnd__DrawTitleBar", "0x11", "CFEPMultiplayerStart__RenderHelpPromptForSelection"],
        ["frontend", "save-game", "render", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00464b10": target(
        "FEPSaveLoad__TransitionNotification",
        "void __thiscall FEPSaveLoad__TransitionNotification(void * this, int from_page)",
        [
            "owner/name correction",
            "shared save/load transition hook",
            "PLATFORM__GetSysTimeFloat",
            "this+0x4",
            "remain unproven",
        ],
        ["PLATFORM__GetSysTimeFloat", "+ 4", "return"],
        ["frontend", "save-game", "load-game", "transition", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00464b30": target(
        "CFEPSaveGame__RemovedMUWhinge",
        "void __cdecl CFEPSaveGame__RemovedMUWhinge(int reason_token)",
        [
            "owner/name/signature correction",
            "source-correlated RemovedMUWhinge",
            "shared by load and virtual keyboard paths",
            "localized storage message",
            "remain unproven",
        ],
        ["CFEPSaveGame__GetLocalizedOrFallbackTextByToken", "DAT_00677614", "CFEPSaveGame__InitDialogAndLayoutState"],
        ["frontend", "save-game", "load-game", "storage-message", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
    "0x00464bc0": target(
        "CFEPSaveGame__AskIfYouWantToDelete",
        "void __thiscall CFEPSaveGame__AskIfYouWantToDelete(void * this, int career_in_progress, int because_4096, int no_space_for_bea)",
        [
            "owner/name/signature correction",
            "source-correlated AskIfYouWantToDelete",
            "RET 0x0c",
            "because_4096",
            "remain unproven",
        ],
        ["ControlsUI__WideStrCat", "0x9e", "0xa0", "CFEPSaveGame__InitDialogAndLayoutState"],
        ["frontend", "save-game", "storage-message", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x00461c40", "0x005db948", "DATA"),
    ("0x00461c60", "0x005db954", "DATA"),
    ("0x00461d60", "0x005db950", "DATA"),
    ("0x00461d90", "0x005db95c", "DATA"),
    ("0x00464620", "0x005db920", "DATA"),
    ("0x00464630", "0x005db92c", "DATA"),
    ("0x00464730", "0x005db928", "DATA"),
    ("0x00464a80", "0x005db934", "DATA"),
    ("0x00464b10", "0x005db938", "DATA"),
    ("0x00464b10", "0x005db960", "DATA"),
    ("0x00464b30", "0x00462020", "UNCONDITIONAL_CALL"),
    ("0x00464b30", "0x004620aa", "UNCONDITIONAL_CALL"),
    ("0x00464b30", "0x00520342", "UNCONDITIONAL_CALL"),
    ("0x00464bc0", "0x0045885b", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x00461c40", "0x00461c42", "MOV", "[ECX + 0x40]"),
    ("0x00461c40", "0x00461c4f", "MOV", "[ECX + 0x44]"),
    ("0x00461c40", "0x00461c58", "RET", ""),
    ("0x00461c60", "0x00461d1d", "CALL", "0x00466ae0"),
    ("0x00461c60", "0x00461d22", "RET", "0x8"),
    ("0x00461d60", "0x00461d86", "CALL", "0x00461e20"),
    ("0x00461d60", "0x00461d8d", "RET", "0x4"),
    ("0x00461d90", "0x00461daa", "PUSH", "0xd"),
    ("0x00461d90", "0x00461dba", "CALL", "0x00467bd0"),
    ("0x00461d90", "0x00461e18", "RET", "0x8"),
    ("0x00464620", "0x00464622", "MOV", "[ECX + 0x8]"),
    ("0x00464620", "0x0046462d", "RET", ""),
    ("0x00464630", "0x004646ed", "CALL", "0x00466ae0"),
    ("0x00464630", "0x004646f2", "RET", "0x8"),
    ("0x00464730", "0x00464766", "CALL", "0x00464c50"),
    ("0x00464730", "0x00464777", "MOV", "[0x00677624]"),
    ("0x00464a80", "0x00464a9a", "PUSH", "0x11"),
    ("0x00464a80", "0x00464aaa", "CALL", "0x00467bd0"),
    ("0x00464a80", "0x00464b08", "RET", "0x8"),
    ("0x00464b10", "0x00464b18", "CALL", "0x005159e0"),
    ("0x00464b10", "0x00464b23", "FSTP", "[ESI + 0x4]"),
    ("0x00464b10", "0x00464b27", "RET", "0x4"),
    ("0x00464b30", "0x00464b44", "CALL", "0x0046a2a0"),
    ("0x00464b30", "0x00464b5c", "MOV", "[0x00677614]"),
    ("0x00464b30", "0x00464bb5", "RET", ""),
    ("0x00464bc0", "0x00464bdf", "PUSH", "0xa0"),
    ("0x00464bc0", "0x00464bf3", "PUSH", "0x9e"),
    ("0x00464bc0", "0x00464c03", "CALL", "0x0055e624"),
    ("0x00464bc0", "0x00464c4b", "RET", "0xc"),
]

CALLSITE_EVIDENCE = [
    ("0x00462020", "0x00461e20", "CFEPLoadGame__DoLoad", "0x00464b30"),
    ("0x004620aa", "0x00461e20", "CFEPLoadGame__DoLoad", "0x00464b30"),
    ("0x00520342", "0x005202d0", "CFEPVirtualKeyboard__Process", "0x00464b30"),
    ("0x0045885b", "0x00458710", "CFEPDevelopment__RefreshWorldListCore", "0x00464bc0"),
]

VTABLE_EVIDENCE = [
    ("0x005db948", "0", "0x005db948", "0x00461c40", "CFEPLoadGame__Init"),
    ("0x005db948", "2", "0x005db950", "0x00461d60", "CFEPLoadGame__Process"),
    ("0x005db948", "3", "0x005db954", "0x00461c60", "CFEPLoadGame__ButtonPressed"),
    ("0x005db948", "5", "0x005db95c", "0x00461d90", "CFEPLoadGame__Render"),
    ("0x005db948", "6", "0x005db960", "0x00464b10", "FEPSaveLoad__TransitionNotification"),
    ("0x005db920", "0", "0x005db920", "0x00464620", "CFEPSaveGame__Init"),
    ("0x005db920", "2", "0x005db928", "0x00464730", "CFEPSaveGame__Process"),
    ("0x005db920", "3", "0x005db92c", "0x00464630", "CFEPSaveGame__ButtonPressed"),
    ("0x005db920", "5", "0x005db934", "0x00464a80", "CFEPSaveGame__Render"),
    ("0x005db920", "6", "0x005db938", "0x00464b10", "FEPSaveLoad__TransitionNotification"),
]

STALE_TOKENS = [
    "CFEPLoadGame__VFunc_02_00461d60",
    "CFEPLoadGame__VFunc_05_00461d90",
    "CFEPSaveGame__VFunc_05_00464a80",
    "CFEPLoadGame__ResolveTextByToken",
    "CFEPSaveGame__DrawLocalizedStatusPrompt",
    "CFrontEndPage__TransitionNotification",
    "param_",
]

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "rebuild parity proven",
]


def norm_addr(value: object) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or text.startswith("<"):
        return text
    return "0x" + text.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    if token == "":
        return True
    return compact(token) in compact(text)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path, *, unescape_comment: bool = False) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if unescape_comment:
        for row in rows:
            row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    match = re.search(
        r"SUMMARY:\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "created": int(match.group(3)),
        "would_create": int(match.group(4)),
        "renamed": int(match.group(5)),
        "would_rename": int(match.group(6)),
        "missing": int(match.group(7)),
        "bad": int(match.group(8)),
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def decompile_for(decompile_dir: Path, address: str) -> str:
    matches = sorted(decompile_dir.glob(f"{norm_addr(address)[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    callsites_path: Path | None = None,
    vtable_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "frontend_save_load_dry.log"
    apply_log_path = apply_log_path or root / "frontend_save_load_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    callsites_path = callsites_path or root / "callsite_instructions_after.tsv"
    vtable_path = vtable_path or root / "vtable_slots_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    expected_count = len(TARGETS)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    expected_dry = {
        "updated": 0,
        "skipped": expected_count,
        "created": 0,
        "would_create": 5,
        "renamed": 0,
        "would_rename": 6,
        "missing": 0,
        "bad": 0,
    }
    expected_apply = {
        "updated": expected_count,
        "skipped": 0,
        "created": 5,
        "would_create": 0,
        "renamed": 6,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    }
    if dry_summary != expected_dry:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != expected_apply:
        failures.append(f"unexpected apply summary: {apply_summary}")

    metadata = row_by_addr(read_tsv(metadata_path, unescape_comment=True))
    tags = row_by_addr(read_tsv(tags_path))
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)
    callsites = read_tsv(callsites_path)
    vtables = read_tsv(vtable_path)

    xref_hits = 0
    instruction_hits = 0
    callsite_hits = 0
    vtable_hits = 0
    stale_hits = 0
    overclaim_hits = 0

    for address, spec in TARGETS.items():
        row = metadata.get(norm_addr(address))
        if not row:
            failures.append(f"{address} metadata missing")
            continue
        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status mismatch: {row.get('status')}")
        if name != spec["name"]:
            failures.append(f"{address} name mismatch: {name} != {spec['name']}")
        if signature != spec["signature"]:
            failures.append(f"{address} signature mismatch: {signature} != {spec['signature']}")
        for token in STALE_TOKENS:
            if token_present(name, token) or token_present(signature, token):
                stale_hits += 1
                failures.append(f"{address} stale token present in name/signature: {token}")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address} missing comment token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                overclaim_hits += 1
                failures.append(f"{address} overclaim token present: {token}")

        tag_row = tags.get(norm_addr(address))
        if not tag_row or tag_row.get("status") != "OK":
            failures.append(f"{address} tag row missing or bad")
        else:
            actual_tags = {tag.strip() for tag in tag_row.get("tags", "").split(";") if tag.strip()}
            expected_tags = COMMON_TAGS | set(spec["tags"])
            missing_tags = expected_tags - actual_tags
            if missing_tags:
                failures.append(f"{address} missing tags: {sorted(missing_tags)}")

        decompile_text = decompile_for(decompile_dir, address)
        if not decompile_text:
            failures.append(f"{address} decompile missing")
        for token in spec["decompileTokens"]:
            if not token_present(decompile_text, str(token)):
                failures.append(f"{address} missing decompile token: {token}")

    for target, source, ref_type in XREF_EVIDENCE:
        if any_row(
            xrefs,
            lambda row, target=target, source=source, ref_type=ref_type: norm_addr(row.get("target_addr", "")) == norm_addr(target)
            and norm_addr(row.get("from_addr", "")) == norm_addr(source)
            and row.get("ref_type", "") == ref_type,
        ):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence: {target} <- {source} {ref_type}")

    for target, instruction_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instructions,
            lambda row, target=target, instruction_addr=instruction_addr, mnemonic=mnemonic, operand_token=operand_token: norm_addr(row.get("target_addr", "")) == norm_addr(target)
            and norm_addr(row.get("instruction_addr", "")) == norm_addr(instruction_addr)
            and row.get("mnemonic", "") == mnemonic
            and token_present(row.get("operands", ""), operand_token),
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target} {instruction_addr} {mnemonic} {operand_token}")

    for source, caller, caller_name, target in CALLSITE_EVIDENCE:
        if any_row(
            callsites,
            lambda row, source=source, caller=caller, caller_name=caller_name, target=target: norm_addr(row.get("target_addr", "")) == norm_addr(source)
            and norm_addr(row.get("instruction_addr", "")) == norm_addr(source)
            and norm_addr(row.get("function_entry", "")) == norm_addr(caller)
            and row.get("function_name", "") == caller_name
            and row.get("mnemonic", "") == "CALL"
            and token_present(row.get("operands", ""), target),
        ):
            callsite_hits += 1
        else:
            failures.append(f"missing callsite evidence: {source} in {caller_name} -> {target}")

    for vtable, slot_index, slot_addr, pointer, function_name in VTABLE_EVIDENCE:
        if any_row(
            vtables,
            lambda row, vtable=vtable, slot_index=slot_index, slot_addr=slot_addr, pointer=pointer, function_name=function_name: norm_addr(row.get("vtable", "")) == norm_addr(vtable)
            and row.get("slot_index", "") == slot_index
            and norm_addr(row.get("slot_addr", "")) == norm_addr(slot_addr)
            and norm_addr(row.get("pointer_addr", "")) == norm_addr(pointer)
            and row.get("function_name", "") == function_name,
        ):
            vtable_hits += 1
        else:
            failures.append(f"missing vtable evidence: {vtable} slot {slot_index} -> {function_name}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-frontend-save-load.v1",
        "status": status,
        "root": root.as_posix(),
        "summary": {
            "targets": expected_count,
            "drySummary": dry_summary,
            "applySummary": apply_summary,
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "callsiteEvidenceHits": callsite_hits,
            "vtableEvidenceHits": vtable_hits,
            "staleTokenHits": stale_hits,
            "overclaimHits": overclaim_hits,
        },
        "targets": TARGETS,
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project has FEPLoadGame and FEPSaveGame init/button/process/render boundaries for the checked vtable slots.",
            "The saved Ghidra names/signatures/comments/tags correct the old save/load VFunc labels to source-correlated Process/Render/Input names.",
            "The saved Ghidra project classifies 0x00464b30 as the shared CFEPSaveGame::RemovedMUWhinge-style storage-message helper and 0x00464bc0 as CFEPSaveGame::AskIfYouWantToDelete-style delete-space prompt logic.",
        ],
        "notProven": [
            "This does not prove exact local variable types, complete FEPLoadGame/FEPSaveGame class layouts, or every frontend save/load vtable slot.",
            "This does not prove runtime save/load behavior, packaged-app behavior, BEA launch behavior, or rebuild parity.",
            "This does not mutate the installed game or BEA.exe.",
        ],
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    report = build_report(root=args.root)
    out = args.out or (args.root / OUTPUT_NAME)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra frontend save/load probe")
        print(f"Status: {report['status']}")
        print(f"Output: {out.as_posix()}")
        summary = report["summary"]
        print(f"Targets: {summary['targets']}")
        print(f"Xref evidence hits: {summary['xrefEvidenceHits']}")
        print(f"Instruction evidence hits: {summary['instructionEvidenceHits']}")
        print(f"Callsite evidence hits: {summary['callsiteEvidenceHits']}")
        print(f"Vtable evidence hits: {summary['vtableEvidenceHits']}")
        for failure in report["failures"]:
            print(f"- {failure}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
