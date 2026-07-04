#!/usr/bin/env python3
"""Validate Wave965 Carver init/combat/wing read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave965-carver-init-combat-wing-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_carver_init_combat_wing_review_wave965_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
CARVER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Carver.cpp.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-144929_post_wave965_carver_init_combat_wing_review_verified"

EXPECTED_METADATA = {
    "0x00422440": ("CCarver__Init", "void __thiscall CCarver__Init(void * this, void * init)"),
    "0x00422580": ("CCarverAI__dtor_base", "void __fastcall CCarverAI__dtor_base(void * this)"),
    "0x00422620": ("CCarver__UpdateMotionAndWingPose", "void __fastcall CCarver__UpdateMotionAndWingPose(void * this)"),
    "0x00422760": ("CCarverAI__OpenWings", "void __fastcall CCarverAI__OpenWings(void * this)"),
    "0x004227a0": ("CCarverAI__CloseWings", "void __fastcall CCarverAI__CloseWings(void * this)"),
    "0x004227e0": ("CCarverAI__OnHit", "void __thiscall CCarverAI__OnHit(void * this, void * otherThing, void * collisionReport)"),
    "0x00422820": ("CCarverAI__Fire", "int __fastcall CCarverAI__Fire(void * this)"),
    "0x00422930": ("CCarverAI__SetLastAttackTime", "void __fastcall CCarverAI__SetLastAttackTime(void * this)"),
    "0x00422940": ("CCarverAI__IsRecentlyAttacked", "int __fastcall CCarverAI__IsRecentlyAttacked(void * this)"),
    "0x004229b0": ("CarverAimGlobals__ResetVector", "void __cdecl CarverAimGlobals__ResetVector(void)"),
    "0x004229d0": ("CarverAimGlobals__InitMatrix", "void __cdecl CarverAimGlobals__InitMatrix(void)"),
    "0x00422750": ("CCarver__Thunk_CallGuideVFunc08", "void __fastcall CCarver__Thunk_CallGuideVFunc08(void * this)"),
    "0x004228b0": ("CCarver__VFunc35_RenderWithFadeGlobal", "void __thiscall CCarver__VFunc35_RenderWithFadeGlobal(void * this, uint render_flags)"),
    "0x00422910": ("CCarver__VFunc104_IsWingBlendAboveThreshold", "int __fastcall CCarver__VFunc104_IsWingBlendAboveThreshold(void * this)"),
}

COMMENT_TOKENS = {
    "0x00422440": ("CAirUnit__Init", "+0x208", "+0x13c"),
    "0x00422580": ("CMonitor__Shutdown", "+0x28", "+0x24", "+0xc"),
    "0x00422620": ("CUnit__UpdateMotionAndTrailEffects", "wing/blend", "+0x70"),
    "0x00422760": ("wingopen", "+0x27c"),
    "0x004227a0": ("wingclose", "+0x27c"),
    "0x004227e0": ("otherThing", "collisionReport"),
    "0x00422820": ("weapon/fire readiness", "returns 0"),
    "0x00422930": ("last-attack timestamp", "+0x288"),
    "0x00422940": ("short cooldown", "last-attack timestamp"),
    "0x004229b0": ("0x00662c60", "0x00662c68"),
    "0x004229d0": ("0x00662c30", "0x00662c5c"),
}

VTABLE_EVIDENCE = {
    "8": ("00422440", "CCarver__Init"),
    "35": ("004228b0", "CCarver__VFunc35_RenderWithFadeGlobal"),
    "38": ("004227e0", "CCarverAI__OnHit"),
    "58": ("00422820", "CCarverAI__Fire"),
    "63": ("00422750", "CCarver__Thunk_CallGuideVFunc08"),
    "65": ("00422620", "CCarver__UpdateMotionAndWingPose"),
    "67": ("00403730", "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport"),
    "103": ("00422970", "CCarverAI__CanStartAttack"),
    "104": ("00422910", "CCarver__VFunc104_IsWingBlendAboveThreshold"),
}

XREF_EVIDENCE = (
    ("0x00422440", "0x005e0db0", "<no_function>", "DATA"),
    ("0x00422620", "0x005e0e94", "<no_function>", "DATA"),
    ("0x00422760", "0x00422c64", "CCarverAI__UpdateAttackAndReschedule", "UNCONDITIONAL_CALL"),
    ("0x004227a0", "0x00422b66", "CCarverAI__RefreshTargetReaderAndScheduleMove", "UNCONDITIONAL_CALL"),
    ("0x004227a0", "0x00422c6b", "CCarverAI__UpdateAttackAndReschedule", "UNCONDITIONAL_CALL"),
    ("0x00422930", "0x00422e93", "CCarverAI__CheckNearbyEnemies", "UNCONDITIONAL_CALL"),
    ("0x004229b0", "0x006220e0", "<no_function>", "DATA"),
    ("0x004229d0", "0x006220e4", "<no_function>", "DATA"),
)

INSTRUCTION_EVIDENCE = (
    ("0x00422620", "0x00422667", "CALL", "0x00402fa0"),
    ("0x00422620", "0x0042273b", "CALL", "[EDX + 0x70]"),
    ("0x00422760", "0x00422791", "MOV", "[ESI + 0x27c], 0x1"),
    ("0x004227a0", "0x004227d0", "MOV", "[ESI + 0x27c], 0x2"),
    ("0x004227e0", "0x0042281c", "RET", "0x8"),
    ("0x00422820", "0x0042282a", "CALL", "[EAX + 0x58]"),
    ("0x00422820", "0x00422861", "MOV", "[ESI + 0x27c], 0x0"),
    ("0x00422930", "0x00422930", "MOV", "[0x00672fd0]"),
    ("0x00422930", "0x00422935", "MOV", "[ECX + 0x288]"),
    ("0x00422940", "0x0042294c", "FCOMP", "[0x00672fd0]"),
    ("0x004229b0", "0x004229b0", "MOV", "[0x00662c60]"),
    ("0x004229b0", "0x004229c4", "MOV", "[0x00662c68]"),
    ("0x004229d0", "0x00422a07", "MOV", "[0x00662c30]"),
    ("0x004229d0", "0x00422a83", "MOV", "[0x00662c58]"),
)

GLOBAL_XREFS = (
    ("0x00662c30", "0x00422a07", "CarverAimGlobals__InitMatrix", "WRITE"),
    ("0x00662c60", "0x004229b0", "CarverAimGlobals__ResetVector", "WRITE"),
    ("0x00662c64", "0x004229ba", "CarverAimGlobals__ResetVector", "WRITE"),
    ("0x00662c68", "0x004229c4", "CarverAimGlobals__ResetVector", "WRITE"),
)

CORE_TOKENS = (
    "Wave965",
    "carver-init-combat-wing-review-wave965",
    "0x00422440 CCarver__Init",
    "0x00422580 CCarverAI__dtor_base",
    "0x00422620 CCarver__UpdateMotionAndWingPose",
    "0x00422760 CCarverAI__OpenWings",
    "0x004227a0 CCarverAI__CloseWings",
    "0x004227e0 CCarverAI__OnHit",
    "0x00422820 CCarverAI__Fire",
    "0x00422930 CCarverAI__SetLastAttackTime",
    "0x00422940 CCarverAI__IsRecentlyAttacked",
    "0x004229b0 CarverAimGlobals__ResetVector",
    "0x004229d0 CarverAimGlobals__InitMatrix",
    "0x005e0d90",
    "334/1408 = 23.72%",
    "6152/6152 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime wing timing proven",
    "runtime damage proven",
    "runtime fire behavior proven",
    "runtime aim behavior proven",
    "exact source method names proven",
    "layout proven",
    "patching proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def norm(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if value in {"", "<none>", "none"}:
        return value
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return token in text or token in stripped or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\") in stripped


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_counts(failures: list[str]) -> None:
    expected = {
        "pre-metadata.tsv": 28,
        "pre-tags.tsv": 28,
        "pre-xrefs.tsv": 46,
        "pre-instructions.tsv": 4060,
        "pre-body-instructions.tsv": 1522,
        "pre-decompile/index.tsv": 28,
        "pre-vtable-slots.tsv": 128,
        "pre-global-xrefs.tsv": 4,
    }
    for relative, count in expected.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == count, f"{relative} row count mismatch: {actual} != {count}", failures)


def check_artifacts(failures: list[str]) -> None:
    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    body = read_tsv(BASE / "pre-body-instructions.tsv")
    vtable = read_tsv(BASE / "pre-vtable-slots.tsv")
    global_xrefs = read_tsv(BASE / "pre-global-xrefs.tsv")

    for address, (name, signature) in EXPECTED_METADATA.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS.get(address, ()):
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for slot, (pointer, name) in VTABLE_EVIDENCE.items():
        require(
            any(row.get("slot_index") == slot and row.get("pointer_addr", "").lower() == pointer and row.get("function_name") == name and row.get("status") == "OK" for row in vtable),
            f"missing vtable slot evidence: slot {slot} -> {pointer} {name}",
            failures,
        )

    for target, from_addr, from_name, ref_type in XREF_EVIDENCE:
        require(
            any(norm(row.get("target_addr", "")) == target and norm(row.get("from_addr", "")) == from_addr and row.get("from_function", "") == from_name and row.get("ref_type", "") == ref_type for row in xrefs),
            f"missing xref evidence: {target} from {from_addr}",
            failures,
        )

    for target, instr_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        require(
            any(norm(row.get("target_addr", "")) == target and norm(row.get("instruction_addr", "")) == instr_addr and row.get("mnemonic", "") == mnemonic and operand_token in row.get("operands", "") for row in body),
            f"missing instruction evidence: {target} {instr_addr} {mnemonic} {operand_token}",
            failures,
        )

    for target, from_addr, from_name, ref_type in GLOBAL_XREFS:
        require(
            any(norm(row.get("target_addr", "")) == target and norm(row.get("from_addr", "")) == from_addr and row.get("from_function", "") == from_name and row.get("ref_type", "") == ref_type for row in global_xrefs),
            f"missing global xref evidence: {target} from {from_addr}",
            failures,
        )


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=28 found=28 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=28 missing=0",
        "pre-xrefs.log": "Wrote 46 rows",
        "pre-instructions.log": "Wrote 4060 instruction rows",
        "pre-body-instructions.log": "Wrote 1522 function-body instruction rows",
        "pre-decompile.log": "targets=28 dumped=28 missing=0 failed=0",
        "pre-vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=128",
        "pre-global-xrefs.log": "Wrote 4 rows",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6152, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUALITY_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6152, "quality TSV row count mismatch", failures)
    require(commented == 6152, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6152, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [NOTE, CAMPAIGN, GHIDRA_REFERENCE, FUNCTION_INDEX, CARVER_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    expected = r"py -3 tools\ghidra_carver_init_combat_wing_review_wave965_probe.py --check"
    actual = package.get("scripts", {}).get("test:ghidra-carver-init-combat-wing-review-wave965")
    require(actual == expected, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_counts(failures)
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave965 Carver init/combat/wing probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave965 Carver init/combat/wing probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
