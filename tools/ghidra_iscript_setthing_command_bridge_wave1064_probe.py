#!/usr/bin/env python3
"""Validate Wave1064 IScript SetThing command bridge read-only artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1064-iscript-setthing-command-bridge"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_iscript_setthing_command_bridge_wave1064_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1064_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-225655_post_wave1064_iscript_setthing_command_bridge_verified"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

DOCS = [
    PUBLIC_NOTE,
    AGGREGATE_NOTE,
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

EXPECTED_SIGNATURES = {
    "0x004fd830": ("CUnit__SetFactionForHierarchy", "void __thiscall CUnit__SetFactionForHierarchy(void * this, int faction_state)"),
    "0x004fe390": ("CEngine__EnableThingByNameFlag", "void __thiscall CEngine__EnableThingByNameFlag(void * this, void * thing_name)"),
    "0x004fe3f0": ("CEngine__DisableThingByNameFlag", "void __thiscall CEngine__DisableThingByNameFlag(void * this, void * thing_name)"),
    "0x0052ff30": ("ScriptCommandRegistry__InitBuiltins", "void __cdecl ScriptCommandRegistry__InitBuiltins(void)"),
    "0x005333b0": ("IScript__Constructor", "void * __thiscall IScript__Constructor(void * this, void * owner_complex_thing, void * script_object_code)"),
    "0x00533450": ("IScript__Destructor", "void __thiscall IScript__Destructor(void * this)"),
    "0x00533500": ("IScript__CallEvent0AndRegisterNestedListeners", "void __thiscall IScript__CallEvent0AndRegisterNestedListeners(void * this)"),
    "0x00533840": ("IScript__RestoreSavedStateAndGotoInstruction", "void __thiscall IScript__RestoreSavedStateAndGotoInstruction(void * this)"),
    "0x005343e0": ("IScript__PrimaryObjectiveComplete", "void __stdcall IScript__PrimaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)"),
    "0x00534410": ("IScript__SecondaryObjectiveComplete", "void __stdcall IScript__SecondaryObjectiveComplete(void * script_args, void * unused_state, void * out_result)"),
    "0x00534440": ("IScript__PrimaryObjectiveFailed", "void __stdcall IScript__PrimaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)"),
    "0x00534470": ("IScript__SecondaryObjectiveFailed", "void __stdcall IScript__SecondaryObjectiveFailed(void * script_args, void * unused_state, void * out_result)"),
    "0x00534fb0": ("IScript__SetThingValueViaVFunc198_FromArg", "void __thiscall IScript__SetThingValueViaVFunc198_FromArg(void * this, void * script_args, void * unused_state, void * out_result)"),
    "0x00534fe0": ("IScript__SetThingValueViaVFunc19C_FromArg", "void __thiscall IScript__SetThingValueViaVFunc19C_FromArg(void * this, void * script_args, void * unused_state, void * out_result)"),
    "0x00535010": ("IScript__SetThingValueViaEngineHelper4FE390_FromArg", "void __thiscall IScript__SetThingValueViaEngineHelper4FE390_FromArg(void * this, void * script_args, void * unused_state, void * out_result)"),
    "0x00535040": ("IScript__SetThingValueViaEngineHelper4FE3F0_FromArg", "void __thiscall IScript__SetThingValueViaEngineHelper4FE3F0_FromArg(void * this, void * script_args, void * unused_state, void * out_result)"),
    "0x00535530": ("IScript__SetThingFloatViaVFunc1C8_FromArg", "void __thiscall IScript__SetThingFloatViaVFunc1C8_FromArg(void * this, void * script_args, void * unused_state, void * out_result)"),
    "0x00535560": ("IScript__SetThingRefViaCUnitHelper4FD830_FromArg", "void __thiscall IScript__SetThingRefViaCUnitHelper4FD830_FromArg(void * this, void * script_args, void * unused_state, void * out_result)"),
}

PRIMARY_XREFS = {
    "0x00534fb0": "0x0053223c",
    "0x00534fe0": "0x0053225b",
    "0x00535010": "0x005331a6",
    "0x00535040": "0x005331b9",
    "0x00535530": "0x00533193",
    "0x00535560": "0x00530d3a",
}

CONTEXT_XREFS = {
    "0x004fd830": ("0x0053557b", "IScript__SetThingRefViaCUnitHelper4FD830_FromArg", "UNCONDITIONAL_CALL"),
    "0x004fe390": ("0x0053502b", "IScript__SetThingValueViaEngineHelper4FE390_FromArg", "UNCONDITIONAL_CALL"),
    "0x004fe3f0": ("0x0053505b", "IScript__SetThingValueViaEngineHelper4FE3F0_FromArg", "UNCONDITIONAL_CALL"),
    "0x0052ff30": ("0x0052ff20", "<no_function>", "UNCONDITIONAL_CALL"),
    "0x005343e0": ("0x00531ce4", "ScriptCommandRegistry__InitBuiltins", "DATA"),
    "0x00534410": ("0x00531d03", "ScriptCommandRegistry__InitBuiltins", "DATA"),
    "0x00534440": ("0x00531e98", "ScriptCommandRegistry__InitBuiltins", "DATA"),
    "0x00534470": ("0x00531eb7", "ScriptCommandRegistry__InitBuiltins", "DATA"),
}

PRIMARY_TAGS = {
    "static-reaudit",
    "iscript",
    "mission-script",
    "command-handler",
    "script-command-registry",
    "script-context-abi",
    "iscript-thing-value-wave582",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-corrected",
}

DOC_TOKENS = (
    "Wave1064",
    "iscript-setthing-command-bridge-wave1064",
    "0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg",
    "0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg",
    "0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg",
    "0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg",
    "0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg",
    "0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg",
    "0x004fd830 CUnit__SetFactionForHierarchy",
    "0x004fe390 CEngine__EnableThingByNameFlag",
    "0x004fe3f0 CEngine__DisableThingByNameFlag",
    "812/1408 = 57.67%",
    "1199/1560 = 76.86%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime missionscript behavior proven",
    "runtime mission-script behavior proven",
    "runtime command behavior proven",
    "script corpus coverage proven",
    "rebuild parity proven",
    "exact source-layout identity proven",
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


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def norm(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 6,
        "primary-tags.tsv": 6,
        "primary-xrefs.tsv": 6,
        "primary-instructions.tsv": 94,
        "primary-decompile/index.tsv": 6,
        "context-metadata.tsv": 12,
        "context-tags.tsv": 12,
        "context-xrefs.tsv": 14,
        "context-instructions.tsv": 2856,
        "context-decompile/index.tsv": 12,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {
        norm(row["address"]): row
        for relative in ("primary-metadata.tsv", "context-metadata.tsv")
        for row in read_tsv(BASE / relative)
    }
    decompile = {
        norm(row["address"]): row
        for relative in (BASE / "primary-decompile" / "index.tsv", BASE / "context-decompile" / "index.tsv")
        for row in read_tsv(relative)
    }

    for address, (name, signature) in EXPECTED_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    tags = {norm(row["address"]): set(row.get("tags", "").split(";")) for row in read_tsv(BASE / "primary-tags.tsv")}
    for address in PRIMARY_XREFS:
        require(PRIMARY_TAGS.issubset(tags.get(address, set())), f"primary tags missing {address}", failures)

    primary_xrefs = {norm(row["target_addr"]): row for row in read_tsv(BASE / "primary-xrefs.tsv")}
    for address, from_addr in PRIMARY_XREFS.items():
        row = primary_xrefs.get(address)
        require(row is not None, f"missing primary xref {address}", failures)
        if row:
            require(norm(row.get("from_addr", "")) == from_addr, f"primary xref from mismatch {address}", failures)
            require(norm(row.get("from_function_addr", "")) == "0x0052ff30", f"primary xref owner mismatch {address}", failures)
            require(row.get("from_function") == "ScriptCommandRegistry__InitBuiltins", f"primary xref function mismatch {address}", failures)
            require(row.get("ref_type") == "DATA", f"primary xref type mismatch {address}", failures)

    context_xrefs = read_tsv(BASE / "context-xrefs.tsv")
    for address, (from_addr, from_function, ref_type) in CONTEXT_XREFS.items():
        matched = any(
            norm(row.get("target_addr", "")) == address
            and norm(row.get("from_addr", "")) == from_addr
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
            for row in context_xrefs
        )
        require(matched, f"missing expected context xref {address} from {from_addr}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=6 found=6 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "primary-xrefs.log": "Wrote 6 rows",
        "primary-instructions.log": "Wrote 94 function-body instruction rows",
        "primary-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=12 found=12 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "context-xrefs.log": "Wrote 14 rows",
        "context-instructions.log": "Wrote 2856 function-body instruction rows",
        "context-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "VERIFY_", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174721927, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-iscript-setthing-command-bridge-wave1064")
        == r"py -3 tools\ghidra_iscript_setthing_command_bridge_wave1064_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1064-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1064 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    task = "Wave1064 iscript setthing command bridge review"
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1064 ledger row", failures)
    require(any(row.get("task") == task and row.get("attempt_id") == 20646 for row in attempt_rows), "missing Wave1064 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1064 IScript SetThing command bridge probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1064 IScript SetThing command bridge probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
