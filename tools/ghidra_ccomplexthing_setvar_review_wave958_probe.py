#!/usr/bin/env python3
"""Validate Wave958 CComplexThing SetVar read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave958-ccomplexthing-setvar-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_ccomplexthing_setvar_review_wave958_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
HIVE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HiveBoss.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-114016_post_wave958_ccomplexthing_setvar_review_verified"

EXPECTED_METADATA = {
    "0x004f45e0": ("CComplexThing__SetVar", "void __stdcall CComplexThing__SetVar(void * var_name, void * data)"),
    "0x004804c0": ("CHiveBoss__SetVar", "void __thiscall CHiveBoss__SetVar(void * this, void * name, void * data)"),
    "0x004f4230": ("CComplexThing__SetScript", "void __thiscall CComplexThing__SetScript(void * this, char * script_name)"),
    "0x004f44a0": ("CComplexThing__SetAnimMode", "bool __thiscall CComplexThing__SetAnimMode(void * this, int anim_mode, int reset_frame, int force_looped)"),
    "0x004f45a0": ("CComplexThing__FinishedPlayingCurrentAnimation", "int __fastcall CComplexThing__FinishedPlayingCurrentAnimation(void * this)"),
    "0x00441740": ("CConsole__Printf", "void __cdecl CConsole__Printf(void * console, char * format, ...)"),
    "0x0042a7b0": ("CConsole__SetVariableByName", "void __thiscall CConsole__SetVariableByName(void * this, char * variable_name, char * value_text)"),
}

COMMENT_TOKENS = {
    "0x004f45e0": ("Wave517", "CComplexThing::SetVar", "RET 0x8", "unknown variable", "rebuild parity remain unproven"),
    "0x004804c0": ("Wave397", "HiveBoss SetVar", "hb_*", "base SetVar unknown-var path"),
    "0x00441740": ("Wave386", "variadic console print sink", "DebugTrace"),
}

TAG_EXPECTATIONS = {
    "0x004f45e0": {"ccomplexthing", "ccomplexthing-animation-wave517", "mission-script", "owner-correction", "warning", "static-reaudit"},
    "0x004804c0": {"help-hive-wave397", "hiveboss", "setvar", "static-reaudit"},
    "0x004f4230": {"ccomplexthing", "mission-script", "static-reaudit"},
    "0x004f44a0": {"animation", "ccomplexthing", "mode", "static-reaudit"},
    "0x004f45a0": {"animation", "ccomplexthing", "mission-script", "static-reaudit"},
    "0x00441740": {"console-system", "diagnostic-console-wave386", "variadic", "static-reaudit"},
}

DECOMPILE_TOKENS = {
    "004f45e0_CComplexThing__SetVar.c": ("void CComplexThing__SetVar", "var_name", "CConsole__Printf", "s_Warning__Uknown_var___s__in_call_006331ec"),
    "004804c0_CHiveBoss__SetVar.c": ("void __thiscall CHiveBoss__SetVar", "CComplexThing__SetVar(name", "s_hb_safe_dist", "s_hb_min_height_above_ground"),
    "004f4230_CComplexThing__SetScript.c": ("CComplexThing__SetScript", "CWorld__CloneScriptObjectCodeByName", "0x7d1"),
    "004f44a0_CComplexThing__SetAnimMode.c": ("CComplexThing__SetAnimMode", "CAnimation__ctor", "CAnimation__SetAnimMode"),
    "004f45a0_CComplexThing__FinishedPlayingCurrentAnimation.c": ("CComplexThing__FinishedPlayingCurrentAnimation", "return 1"),
}

INSTRUCTION_EVIDENCE = (
    ("0x004f45e0", "0x004f45e0", "MOV", "ECX, dword ptr [ESP + 0x4]", "8b 4c 24 04"),
    ("0x004f45e0", "0x004f45e6", "CALL", "dword ptr [EAX + 0x38]", "ff 50 38"),
    ("0x004f45e0", "0x004f45ea", "PUSH", "0x6331ec", "68 ec 31 63 00"),
    ("0x004f45e0", "0x004f45f4", "CALL", "0x00441740", "e8 47 d1 f4 ff"),
    ("0x004f45e0", "0x004f45fc", "RET", "0x8", "c2 08 00"),
)

XREF_EVIDENCE = (
    ("0x004f45e0", "0x00480685", "CHiveBoss__SetVar", "UNCONDITIONAL_CALL"),
    ("0x00441740", "0x004f45f4", "CComplexThing__SetVar", "UNCONDITIONAL_CALL"),
    ("0x004f45e0", "0x005d8544", "<no_function>", "DATA"),
    ("0x004f45e0", "0x005e4874", "<no_function>", "DATA"),
    ("0x004804c0", "0x005e17d8", "<no_function>", "DATA"),
)

CORE_TOKENS = (
    "Wave958",
    "ccomplexthing-setvar-review-wave958",
    "0x004f45e0 CComplexThing__SetVar",
    "0x004804c0 CHiveBoss__SetVar",
    "0x004f45fc",
    "RET 0x8",
    "Warning: Uknown var",
    "293/1408 = 20.81%",
    "6151/6151 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime mission-script variable behavior proven",
    "runtime script-variable behavior proven",
    "runtime console output behavior proven",
    "source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
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


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 7,
        "tags.tsv": 7,
        "xrefs.tsv": 528,
        "instructions.tsv": 259,
        "decompile/index.tsv": 7,
    }
    for relative, expected in counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count mismatch: {actual} != {expected}", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile_index = {norm(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}

    for address, (name, signature) in EXPECTED_METADATA.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
            for token in COMMENT_TOKENS.get(address, ()):
                require(contains_token(row.get("comment", ""), token), f"missing comment token at {address}: {token}", failures)
        dec = decompile_index.get(address)
        require(dec is not None and dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for address, expected_tags in TAG_EXPECTATIONS.items():
        row = tags.get(address)
        observed = set((row or {}).get("tags", "").split(";"))
        missing = expected_tags - observed
        require(not missing, f"tags missing at {address}: {sorted(missing)}", failures)

    for filename, tokens in DECOMPILE_TOKENS.items():
        text = read_text(BASE / "decompile" / filename)
        for token in tokens:
            require(token in text, f"missing decompile token in {filename}: {token}", failures)

    instructions = read_tsv(BASE / "instructions.tsv")
    for target, instruction, mnemonic, operands, bytes_ in INSTRUCTION_EVIDENCE:
        hit = any(
            norm(row.get("target_addr", "")) == target
            and norm(row.get("instruction_addr", "")) == instruction
            and row.get("mnemonic") == mnemonic
            and row.get("operands") == operands
            and row.get("bytes") == bytes_
            for row in instructions
        )
        require(hit, f"missing instruction evidence: {target} {instruction} {mnemonic} {operands}", failures)

    xrefs = read_tsv(BASE / "xrefs.tsv")
    for target, source, from_function, ref_type in XREF_EVIDENCE:
        hit = any(
            norm(row.get("target_addr", "")) == target
            and norm(row.get("from_addr", "")) == source
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
            for row in xrefs
        )
        require(hit, f"missing xref evidence: {source} -> {target} {from_function} {ref_type}", failures)

    warning = read_tsv(BASE / "string-006331ec.tsv")
    source = read_tsv(BASE / "string-006331c0.tsv")
    require(warning and warning[0].get("cstring") == "Warning: Uknown var '%s' in call to SetVar", "warning string mismatch", failures)
    require(source and source[0].get("cstring") == r"[maintainer-local-source-export-root]\thing.cpp", "source path string mismatch", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "metadata.log": "targets=7 found=7 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "xrefs.log": "Wrote 528 rows",
        "instructions.log": "Wrote 259 instruction rows",
        "decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "string-006331ec.log": "Warning: Uknown var",
        "string-006331c0.log": r"[maintainer-local-source-export-root]\thing.cpp",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "Invalid script", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    consult = read_text(BASE / "cursor-consult-wave958.txt")
    require("likely no mutation" in consult, "missing Cursor consult no-mutation boundary", failures)
    require("composer" in consult.lower() or "Cursor Composer" in consult, "missing Cursor consult provenance", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        NOTE,
        CAMPAIGN,
        GHIDRA_REFERENCE,
        FUNCTION_INDEX,
        THING_DOC,
        HIVE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6151, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-ccomplexthing-setvar-review-wave958")
        == r"py -3 tools\ghidra_ccomplexthing_setvar_review_wave958_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave958 CComplexThing SetVar review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave958 CComplexThing SetVar review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
