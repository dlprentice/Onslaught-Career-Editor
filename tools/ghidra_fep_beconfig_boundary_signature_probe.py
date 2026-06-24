#!/usr/bin/env python3
"""Validate the Wave367 FEPBEConfig boundary/signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/fep-config-wave367/current")
OUTPUT_NAME = "fep-beconfig-boundary-signature.json"

COMMON_TAGS = {
    "static-reaudit",
    "fep-beconfig-wave367",
    "retail-binary-evidence",
}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str]) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0044eab0": target(
        "CFEPMultiplayerStart__GetConfigIdByIndex",
        "int __cdecl CFEPMultiplayerStart__GetConfigIdByIndex(int config_index)",
        ["selected BattleEngine profile", "config_index", "remain unproven"],
        ["fep-multiplayer-start", "config-list", "comment-hardened"],
    ),
    "0x0044eb30": target(
        "CFEPMultiplayerStart__SetConfigDescriptionByIndex",
        "void __cdecl CFEPMultiplayerStart__SetConfigDescriptionByIndex(int config_index)",
        ["config name", "Unknown Configuration", "remain unproven"],
        ["fep-multiplayer-start", "config-list", "text"],
    ),
    "0x0044ecf0": target(
        "CFEPMultiplayerStart__GetConfigCount",
        "int __cdecl CFEPMultiplayerStart__GetConfigCount(void)",
        ["config count", "DAT_0089d94c", "remain unproven"],
        ["fep-multiplayer-start", "config-list", "comment-hardened"],
    ),
    "0x0044ed40": target(
        "CFEPMultiplayerStart__LookupProfileField5CBySelectionIndex",
        "int __cdecl CFEPMultiplayerStart__LookupProfileField5CBySelectionIndex(int config_index)",
        ["field at +0x5c", "remain unproven"],
        ["fep-multiplayer-start", "config-record", "field-reader"],
    ),
    "0x0044eea0": target(
        "CFEPMultiplayerStart__LookupProfileField4CPlusFlagBySelectionIndex",
        "int __cdecl CFEPMultiplayerStart__LookupProfileField4CPlusFlagBySelectionIndex(int config_index)",
        ["field +0x4c", "flag at +0x60", "remain unproven"],
        ["fep-multiplayer-start", "config-record", "field-reader"],
    ),
    "0x0044f030": target(
        "CFEPBEConfig__GetWeaponProperty",
        "int __cdecl CFEPBEConfig__GetWeaponProperty(void * config, int weapon_index, int property_index)",
        ["primary weapon-name list", "+0x10/+0x11/+0x12", "remain unproven"],
        ["fep-beconfig", "weapon-config", "property-reader"],
    ),
    "0x0044f300": target(
        "CFEPBEConfig__GetWeaponPropertyAlt",
        "int __cdecl CFEPBEConfig__GetWeaponPropertyAlt(void * config, int weapon_index, int property_index)",
        ["alternate weapon-name list", "+0x50/+0x58", "remain unproven"],
        ["fep-beconfig", "weapon-config", "property-reader", "alternate-list"],
    ),
    "0x0044f530": target(
        "CFEPBEConfig__PlayWeaponSound",
        "void __cdecl CFEPBEConfig__PlayWeaponSound(void * config, int weapon_index)",
        ["field +0x0f", "Unknown Weapon", "remain unproven"],
        ["fep-beconfig", "weapon-config", "sound-text"],
    ),
    "0x0044f830": target(
        "CFEPBEConfig__PlayWeaponSoundAlt",
        "void __cdecl CFEPBEConfig__PlayWeaponSoundAlt(void * config, int weapon_index)",
        ["alternate weapon-name list", "Unknown Weapon", "remain unproven"],
        ["fep-beconfig", "weapon-config", "sound-text", "alternate-list"],
    ),
    "0x0044fa90": target(
        "CFEPBEConfig__Init",
        "void __thiscall CFEPBEConfig__Init(void * this)",
        ["SEH prologue", "beconf::init() 0-5", "0x0044fa93", "remain unproven"],
        ["fep-beconfig", "function-boundary", "init", "boundary-corrected"],
    ),
    "0x0044fda0": target(
        "CFEPBEConfig__Cleanup",
        "void __thiscall CFEPBEConfig__Cleanup(void * this)",
        ["this+0x08", "this+0x20", "CleanupSquads", "remain unproven"],
        ["fep-beconfig", "cleanup", "comment-hardened"],
    ),
    "0x0044fdf0": target(
        "CFEPBEConfig__CleanupSquads",
        "void __thiscall CFEPBEConfig__CleanupSquads(void * this)",
        ["pointer set at +0x14", "freeing nested strings", "remain unproven"],
        ["fep-beconfig", "cleanup", "squad-list"],
    ),
    "0x0044fe70": target(
        "CFEPBEConfig__Load",
        "void __thiscall CFEPBEConfig__Load(void * this, void * mem_buffer)",
        ["CDXMemBuffer", "0x24-byte entry", "stdcall", "remain unproven"],
        ["fep-beconfig", "loader", "signature-hardened"],
    ),
    "0x00450010": target(
        "CFEPBEConfig__UpdateTransitionTimers",
        "void __thiscall CFEPBEConfig__UpdateTransitionTimers(void * this, int menu_state)",
        ["vtable slot 1", "this+0x0c/+0x14/+0x18", "RET 0x4", "remain unproven"],
        ["fep-beconfig", "function-boundary", "vtable-slot", "timer-state"],
    ),
    "0x00450090": target(
        "CFEPBEConfig__ButtonPressed",
        "void __thiscall CFEPBEConfig__ButtonPressed(void * this, int button, int player_index)",
        ["vtable slot 2", "0x2a-0x2e", "selected config", "remain unproven"],
        ["fep-beconfig", "function-boundary", "vtable-slot", "button-handler"],
    ),
    "0x00450390": target(
        "CFEPBEConfig__RenderPreCommon",
        "void __thiscall CFEPBEConfig__RenderPreCommon(void * this, float transition, int dest)",
        ["vtable slot 3", "selection marker", "dest/state is 4", "remain unproven"],
        ["fep-beconfig", "function-boundary", "vtable-slot", "render-pre-common"],
    ),
    "0x00450400": target(
        "CFEPBEConfig__PushProjectionMatrixForRender",
        "void __cdecl CFEPBEConfig__PushProjectionMatrixForRender(void)",
        ["Saves the active projection matrix", "remain unproven"],
        ["fep-beconfig", "render", "projection"],
    ),
    "0x00450440": target(
        "CFEPBEConfig__PopProjectionMatrixAfterRender",
        "void __cdecl CFEPBEConfig__PopProjectionMatrixAfterRender(void)",
        ["Restores the saved projection matrix", "remain unproven"],
        ["fep-beconfig", "render", "projection"],
    ),
    "0x00450460": target(
        "CFEPMultiplayerStart__RenderConfigPipRow",
        "void __cdecl CFEPMultiplayerStart__RenderConfigPipRow(float x, float y, float rating, uint argb)",
        ["rating pips", "argb", "CDXSurf__RenderSurface", "remain unproven"],
        ["fep-multiplayer-start", "fep-beconfig", "render", "pip-row"],
    ),
    "0x004505b0": target(
        "CFEPBEConfig__Render",
        "void __thiscall CFEPBEConfig__Render(void * this, float transition, int dest)",
        ["vtable slot 4", "projection push/pop", "pip rows", "remain unproven"],
        ["fep-beconfig", "function-boundary", "vtable-slot", "render"],
    ),
    "0x00451930": target(
        "CFEPBEConfig__FindEntryByName",
        "void * __cdecl CFEPBEConfig__FindEntryByName(char * entry_name)",
        ["DAT_006602a0", "entry_name", "+0xa8", "remain unproven"],
        ["fep-beconfig", "config-record", "lookup", "signature-hardened"],
    ),
    "0x004519c0": target(
        "CFEPBEConfig__ResetTimestampAndModeFlag",
        "void __thiscall CFEPBEConfig__ResetTimestampAndModeFlag(void * this)",
        ["vtable slot 5", "PLATFORM time", "this+0x10", "remain unproven"],
        ["fep-beconfig", "vtable-slot", "timestamp", "mode-flag", "name-corrected"],
    ),
}

VTABLE_EXPECTED = {
    0: ("0x0044fda0", "CFEPBEConfig__Cleanup"),
    1: ("0x00450010", "CFEPBEConfig__UpdateTransitionTimers"),
    2: ("0x00450090", "CFEPBEConfig__ButtonPressed"),
    3: ("0x00450390", "CFEPBEConfig__RenderPreCommon"),
    4: ("0x004505b0", "CFEPBEConfig__Render"),
    5: ("0x004519c0", "CFEPBEConfig__ResetTimestampAndModeFlag"),
    8: ("0x0044fe70", "CFEPBEConfig__Load"),
}

INSTRUCTION_EVIDENCE = [
    ("0x0044fa90", "0x0044fa90", "MOV", "FS:[0x0]"),
    ("0x00450010", "0x00450010", "MOV", "[ESP + 0x4]"),
    ("0x00450010", "0x00450089", "RET", "0x4"),
    ("0x00450090", "0x004500a3", "JMP", "0x450378"),
    ("0x00450090", "0x0045036b", "RET", "0x8"),
    ("0x00450390", "0x004503c4", "CALL", "0x004530b0"),
    ("0x00450390", "0x004503f5", "RET", "0x8"),
    ("0x004505b0", "0x004506ce", "PUSH", "0x3f400000"),
]

STALE_SIGNATURE_TOKENS = ["param_1", "param_2", "param_3", "param_4", "unaff_"]
STALE_NAME_TOKENS = [
    "CFEPBEConfig__VFunc_06_004519c0",
    "CFEPBEConfig__Unk_00450400",
    "CFEPBEConfig__Unk_00450440",
]
OVERCLAIM_TOKENS = ["fully re'ed", "100% re", "runtime behavior proven", "source identity proven"]


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
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if not match:
        return {}
    return {
        "targets": int(match.group(1)),
        "changed_or_would_change": int(match.group(2)),
        "failed": int(match.group(3)),
        "dry": match.group(4) == "true",
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    vtable_path: Path | None = None,
    instructions_path: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "fep_beconfig_boundary_signature_dry.log"
    apply_log_path = apply_log_path or root / "fep_beconfig_boundary_signature_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    vtable_path = vtable_path or root / "vtable_slots_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"

    failures: list[str] = []
    metadata = row_by_addr(read_tsv(metadata_path, unescape_comment=True))
    tags = row_by_addr(read_tsv(tags_path))
    vtable_rows = read_tsv(vtable_path)
    instruction_rows = read_tsv(instructions_path)
    expected_count = len(TARGETS)

    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"targets": expected_count, "changed_or_would_change": expected_count, "failed": 0, "dry": True}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"targets": expected_count, "changed_or_would_change": expected_count, "failed": 0, "dry": False}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    stale_name_hits = 0
    stale_signature_hits = 0
    vtable_hits = 0
    instruction_hits = 0

    for address, spec in TARGETS.items():
        row = metadata.get(norm_addr(address))
        if row is None:
            failures.append(f"missing metadata for {address}")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"name mismatch for {address}: {row.get('name')} != {spec['name']}")
        signature = row.get("signature", "")
        if signature != spec["signature"]:
            failures.append(f"signature mismatch for {address}: {signature} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"missing comment token for {address}: {token}")
        for token in STALE_NAME_TOKENS:
            if token_present(row.get("name", ""), token):
                stale_name_hits += 1
                failures.append(f"stale name token for {address}: {token}")
        for token in STALE_SIGNATURE_TOKENS:
            if token_present(signature, token):
                stale_signature_hits += 1
                failures.append(f"stale signature token for {address}: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"overclaim token for {address}: {token}")

        tag_row = tags.get(norm_addr(address))
        if tag_row is None:
            failures.append(f"missing tags for {address}")
        else:
            tag_set = set(filter(None, re.split(r"[;,]\s*", tag_row.get("tags", ""))))
            expected_tags = COMMON_TAGS | set(spec["tags"])
            missing = sorted(expected_tags - tag_set)
            if missing:
                failures.append(f"missing tags for {address}: {missing}")

    for slot_index, (expected_addr, expected_name) in VTABLE_EXPECTED.items():
        hit = any_row(
            vtable_rows,
            lambda row, slot_index=slot_index, expected_addr=expected_addr, expected_name=expected_name: (
                row.get("slot_index") == str(slot_index)
                and norm_addr(row.get("pointer_addr")) == norm_addr(expected_addr)
                and norm_addr(row.get("function_entry")) == norm_addr(expected_addr)
                and row.get("function_name") == expected_name
                and row.get("status") == "OK"
            ),
        )
        if hit:
            vtable_hits += 1
        else:
            failures.append(f"missing vtable read-back for slot {slot_index}: {expected_addr} {expected_name}")

    for target, instr_addr, mnemonic, operands in INSTRUCTION_EVIDENCE:
        hit = any_row(
            instruction_rows,
            lambda row, target=target, instr_addr=instr_addr, mnemonic=mnemonic, operands=operands: (
                norm_addr(row.get("target_addr")) == norm_addr(target)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instr_addr)
                and row.get("mnemonic") == mnemonic
                and token_present(row.get("operands", ""), operands)
            ),
        )
        if hit:
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target} {instr_addr} {mnemonic} {operands}")

    status = "PASS" if not failures else "FAIL"
    return {
        "status": status,
        "root": str(root),
        "summary": {
            "targets": expected_count,
            "metadataRows": len(metadata),
            "vtableEvidenceHits": vtable_hits,
            "instructionEvidenceHits": instruction_hits,
            "staleNameHits": stale_name_hits,
            "staleSignatureHits": stale_signature_hits,
        },
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    output_path = args.json or args.root / OUTPUT_NAME
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"status={report['status']} targets={report['summary']['targets']} output={output_path}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
