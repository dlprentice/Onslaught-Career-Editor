#!/usr/bin/env python3
"""Validate Wave528 Unit/Warspite command-tail static RE evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave528-unit-warspite-command-004fe030"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_unit_warspite_command_wave528_2026-05-18.md"

COMMON_TAGS = {
    "comment-hardened",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
    "unit-warspite-command-wave528",
}

TARGETS = {
    "0x004fe030": {
        "name": "CUnit__TriggerEffect",
        "signature": "void __thiscall CUnit__TriggerEffect(void * this, void * trigger_context)",
        "comment_tokens": ("RET 0x4", "trigger_context+0x138", "CMessage", "remain unproven"),
        "tags": {"message-queue", "pilot-text", "unit-trigger"},
        "decompile_tokens": ("trigger_context", "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance", "Tara_Fighter"),
    },
    "0x004fe390": {
        "name": "CEngine__EnableThingByNameFlag",
        "signature": "void __thiscall CEngine__EnableThingByNameFlag(void * this, void * thing_name)",
        "comment_tokens": ("RET 0x4", "0x00535010", "this+0x18c", "remain unproven"),
        "tags": {"engine-list", "script-command", "thing-name-flag"},
        "decompile_tokens": ("thing_name", "stricmp", "0x3f4"),
    },
    "0x004fe3f0": {
        "name": "CEngine__DisableThingByNameFlag",
        "signature": "void __thiscall CEngine__DisableThingByNameFlag(void * this, void * thing_name)",
        "comment_tokens": ("RET 0x4", "0x00535040", "active reader", "remain unproven"),
        "tags": {"active-reader", "engine-list", "script-command", "thing-name-flag"},
        "decompile_tokens": ("thing_name", "CGenericActiveReader__SetReader", "CSquadNormal__SetReaderAndRefreshSupportSelection"),
    },
    "0x004fe480": {
        "name": "CEngine__DispatchBoundCallbackIfPresent",
        "signature": "int __fastcall CEngine__DispatchBoundCallbackIfPresent(void * this)",
        "comment_tokens": ("ECX-only", "this+0x208", "vfunc +0x24", "remain unproven"),
        "tags": {"callback-dispatch", "vtable-forwarder"},
        "decompile_tokens": ("this + 0x208", "return 0"),
    },
    "0x004fe500": {
        "name": "CSquadNormal__SetReaderAndUnregisterFromFactionSets",
        "signature": "void __thiscall CSquadNormal__SetReaderAndUnregisterFromFactionSets(void * this, void * reader)",
        "comment_tokens": ("RET 0x4", "this+0x148", "DAT_008550c0", "remain unproven"),
        "tags": {"active-reader", "faction-set", "squad-support"},
        "decompile_tokens": ("reader", "DAT_008550c0", "DAT_008550b0"),
    },
    "0x004fe540": {
        "name": "CUnitAI__AccumulateForwardedCommandScore",
        "signature": "void __thiscall CUnitAI__AccumulateForwardedCommandScore(void * this, int score_delta)",
        "comment_tokens": ("RET 0x4", "score_delta", "event 0xfa5", "remain unproven"),
        "tags": {"command-forwarding", "event-scheduled", "unitai-score"},
        "decompile_tokens": ("score_delta", "CEventManager__AddEvent_AtTime", "0x218"),
    },
    "0x004fe710": {
        "name": "CWarspite__Init",
        "signature": "void * __thiscall CWarspite__Init(void * this, void * owner_unit, void * init_context)",
        "comment_tokens": ("RET 0x8", "0x7d3/0xbb9/0xbba", "active readers", "remain unproven"),
        "tags": {"active-reader", "event-scheduled", "init", "warspite-ai"},
        "decompile_tokens": ("owner_unit", "init_context", "CEventManager__AddEvent_AtTime"),
    },
    "0x004fef40": {
        "name": "CWarspite__Update",
        "signature": "float __fastcall CWarspite__Update(void * this)",
        "comment_tokens": ("ECX-only", "x87", "CWarspite__TransitionToUndeploying", "remain unproven"),
        "tags": {"support-selection", "update", "warspite-ai", "x87-return"},
        "decompile_tokens": ("CUnit__ForwardAimTransformAndAttachTargetReader", "CWarspite__TransitionToUndeploying", "return"),
    },
    "0x004ffdd0": {
        "name": "CSquadNormal__SetReaderAndRefreshSupportSelection",
        "signature": "void __thiscall CSquadNormal__SetReaderAndRefreshSupportSelection(void * this, void * reader, void * selection_context)",
        "comment_tokens": ("RET 0x8", "this+0xc", "this+0x10", "remain unproven"),
        "tags": {"active-reader", "squad-support", "support-selection"},
        "decompile_tokens": ("reader", "selection_context", "CSquadNormal__SelectBestSupportOrEscort"),
    },
}

EXPECTED_XREFS = {
    ("0x004fe390", "0x0053502b", "IScript__SetThingValueViaEngineHelper4FE390_FromArg", "UNCONDITIONAL_CALL"),
    ("0x004fe3f0", "0x0053505b", "IScript__SetThingValueViaEngineHelper4FE3F0_FromArg", "UNCONDITIONAL_CALL"),
    ("0x004fe540", "0x00428d1e", "CUnitAI__ForwardCommandToAttachedNodeThenDispatch", "UNCONDITIONAL_CALL"),
    ("0x004fe710", "0x005044a7", "CWarspite__Create", "UNCONDITIONAL_CALL"),
    ("0x004fef40", "0x005d8cf4", "<no_function>", "DATA"),
    ("0x004ffdd0", "0x004fda52", "CUnit__PropagateTargetUnitToHierarchy", "UNCONDITIONAL_CALL"),
}

EXPECTED_RETS = {
    ("0x004fe2a3", "0x4", "CUnit__TriggerEffect"),
    ("0x004fe3e2", "0x4", "CEngine__EnableThingByNameFlag"),
    ("0x004fe43a", "0x4", "CEngine__DisableThingByNameFlag"),
    ("0x004fe491", "", "CEngine__DispatchBoundCallbackIfPresent"),
    ("0x004fe530", "0x4", "CSquadNormal__SetReaderAndUnregisterFromFactionSets"),
    ("0x004fe5b2", "0x4", "CUnitAI__AccumulateForwardedCommandScore"),
    ("0x004fea21", "0x8", "CWarspite__Init"),
    ("0x004ff217", "", "CWarspite__Update"),
    ("0x004ffdf3", "0x8", "CSquadNormal__SetReaderAndRefreshSupportSelection"),
}

CONTEXT_TOKENS = (
    "CUnitAI__AccumulateForwardedCommandScore(this,command)",
    "CEngine__EnableThingByNameFlag(*(void **)((int)this + 0x10),thing_name)",
    "CEngine__DisableThingByNameFlag(*(void **)((int)this + 0x10),thing_name)",
    "CWarspite__Init(this_00,this,init_thing)",
    "CWarspite__Init(this,param_1,param_2)",
    "CSquadNormal__SetReaderAndRefreshSupportSelection(this_00,reader,(void *)0x0)",
)

PUBLIC_NOTE_TOKENS = (
    "Wave528",
    "CWarspite__Init",
    "CUnit__TriggerEffect",
    "119 target xref rows",
    "runtime AI behavior",
    "rebuild parity",
)


def normalize_addr(value: str) -> str:
    value = (value or "").strip().lower()
    if not value or value.startswith("<"):
        return value
    body = value[2:] if value.startswith("0x") else value
    return f"0x{int(body, 16):08x}"


def compact(value: str) -> str:
    return "".join(" ".join((value or "").split()).lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise AssertionError(f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "instruction_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_addr(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def row_by(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str]:
    wanted = normalize_addr(address)
    for row in rows:
        if row.get(key) == wanted:
            return row
    raise AssertionError(f"missing row for {address}")


def decomp_file(decomp_dir: Path, address: str, expected_name: str) -> Path:
    candidates = sorted(decomp_dir.glob(f"{normalize_addr(address)[2:]}_*.c"))
    require(bool(candidates), f"missing decompile export for {address}")
    named = [path for path in candidates if expected_name in path.name]
    require(bool(named), f"decompile export for {address} does not contain {expected_name}")
    return named[0]


def check_log(path: Path, expected_summary: str, script_report: bool = False) -> None:
    require(path.exists(), f"missing log: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    require(expected_summary in text, f"{path.name}: missing summary {expected_summary}")
    require("REPORT: Save succeeded" in text, f"{path.name}: missing save success")
    if script_report:
        require("ApplyUnitWarspiteCommandWave528.java> REPORT: Save succeeded" in text, f"{path.name}: missing script save report")
    for bad in ("LockException", "MISSING:", "BADNAME:", "BADADDR:", "FAIL:"):
        require(bad not in text, f"{path.name}: contains {bad}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    base = args.base

    check_log(base / "apply_unit_warspite_command_wave528_dry.log", "SUMMARY updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0")
    check_log(base / "apply_unit_warspite_command_wave528_apply.log", "SUMMARY updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0", True)
    check_log(base / "apply_unit_warspite_command_wave528_verify_dry.log", "SUMMARY updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0")

    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
    xrefs = read_tsv(base / "post_xrefs.tsv")
    instructions = read_tsv(base / "post_instructions.tsv")
    require(len(metadata) == len(TARGETS), f"metadata rows {len(metadata)} != {len(TARGETS)}")
    require(len(tags) == len(TARGETS), f"tag rows {len(tags)} != {len(TARGETS)}")
    require(len(xrefs) == 119, f"xref rows {len(xrefs)} != 119")
    require(len(instructions) == 3789, f"instruction rows {len(instructions)} != 3789")

    tags_by_addr = {normalize_addr(row["address"]): row for row in tags}
    for address, expected in TARGETS.items():
        row = row_by(metadata, address)
        require(row["status"] == "OK", f"{address} metadata status {row['status']}")
        require(row["name"] == expected["name"], f"{address} name {row['name']} != {expected['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch: {row['signature']}")
        for token in expected["comment_tokens"]:
            require(token_present(row["comment"], token), f"{address} comment missing {token!r}")

        tag_row = tags_by_addr[normalize_addr(address)]
        actual_tags = {part.strip() for part in tag_row["tags"].split(";") if part.strip()}
        missing_tags = (COMMON_TAGS | expected["tags"]) - actual_tags
        require(not missing_tags, f"{address} missing tags: {sorted(missing_tags)}")

        path = decomp_file(base / "post_decomp", address, expected["name"])
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in expected["decompile_tokens"]:
            require(token_present(text, token), f"{address} decompile missing {token!r}")
        signature_lines = "\n".join(line for line in text.splitlines()[:12] if "signature:" in line or expected["name"] in line)
        for stale in ("undefined ", "param_1", "param_2", "param_3", "float10"):
            require(stale not in signature_lines, f"{address} stale signature token {stale!r} in decompile header")

    xref_set = {
        (row["target_addr"], row["from_addr"], row["from_function"], row["ref_type"])
        for row in xrefs
    }
    for expected in EXPECTED_XREFS:
        target, from_addr, function, ref_type = expected
        normalized = (normalize_addr(target), normalize_addr(from_addr), function, ref_type)
        require(normalized in xref_set, f"missing xref {expected}")

    for instruction_addr, operands, function_name in EXPECTED_RETS:
        hit = any(
            row["instruction_addr"] == normalize_addr(instruction_addr)
            and row["mnemonic"] == "RET"
            and row.get("operands", "") == operands
            and row.get("function_name", "") == function_name
            for row in instructions
        )
        require(hit, f"missing RET evidence {instruction_addr} {operands} {function_name}")

    context_index = read_tsv(base / "post_context_decomp" / "index.tsv")
    require(len(context_index) == 12, f"context index rows {len(context_index)} != 12")
    require(sum(1 for row in context_index if row["status"] == "OK") == 11, "expected 11 context decompile OK rows")
    context_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in sorted((base / "post_context_decomp").glob("*.c")))
    for token in CONTEXT_TOKENS:
        require(token_present(context_text, token), f"context decompile missing {token!r}")

    require(PUBLIC_NOTE.exists(), f"missing public note: {PUBLIC_NOTE}")
    public_note = PUBLIC_NOTE.read_text(encoding="utf-8", errors="replace")
    for token in PUBLIC_NOTE_TOKENS:
        require(token_present(public_note, token), f"public note missing {token!r}")
    for overclaim in ("runtime AI behavior proven", "source identity proven", "rebuild parity proven", "fully re'ed", "100% re"):
        require(not token_present(public_note, overclaim), f"public note overclaim: {overclaim}")

    print("Wave528 Unit/Warspite command-tail probe: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"Wave528 Unit/Warspite command-tail probe: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
