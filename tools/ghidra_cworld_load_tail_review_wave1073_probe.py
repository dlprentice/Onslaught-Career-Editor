#!/usr/bin/env python3
"""Validate Wave1073 CWorld load/tail read-only review artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1073-cworld-load-tail-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cworld_load_tail_review_wave1073_2026-06-02.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1073_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-044834_post_wave1073_cworld_load_tail_review_verified"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

TARGETS = {
    "0x0050a870": ("CWorld__ClearSetArrays", "void __fastcall CWorld__ClearSetArrays(void * world)", "cworld-load-core-wave555", "Wave555"),
    "0x0050a9c0": ("CWorld__InitSetArraysAndState", "void * __fastcall CWorld__InitSetArraysAndState(void * world)", "cworld-load-core-wave555", "Wave555"),
    "0x0050abb0": ("CWorld__ShutdownAndClear_Thunk", "void __fastcall CWorld__ShutdownAndClear_Thunk(void * world)", "cworld-load-core-wave555", "Wave555"),
    "0x0050abc0": ("CWorld__CloneScriptObjectCodeByName", "void * __thiscall CWorld__CloneScriptObjectCodeByName(void * this, char * script_name)", "cworld-load-core-wave555", "Wave555"),
    "0x0050ac70": ("CWorld__LoadScriptEvents", "void __thiscall CWorld__LoadScriptEvents(void * this, void * mem_buffer)", "cworld-load-core-wave555", "Wave555"),
    "0x0050ada0": ("CWorld__ShutdownAndClear", "void __fastcall CWorld__ShutdownAndClear(void * world)", "cworld-load-core-wave555", "Wave555"),
    "0x0050af70": ("CWorld__FindThingByName", "void * __thiscall CWorld__FindThingByName(void * this, char * thing_name)", "cworld-load-core-wave555", "Wave555"),
    "0x0050b520": ("CWorld__LoadWorldFile", "int __thiscall CWorld__LoadWorldFile(void * this, int world_id, int is_base_world)", "cworld-load-core-wave555", "Wave555"),
    "0x0050b780": ("CWorld__DeserializeWorld", "void __thiscall CWorld__DeserializeWorld(void * this, void * chunk_reader)", "cworld-load-core-wave555", "Wave555"),
    "0x0050d4c0": ("CWorld__LoadWorldHeader", "void __thiscall CWorld__LoadWorldHeader(void * this, void * mem_buffer, int is_base_world)", "cworld-load-core-wave555", "Wave555"),
    "0x0050d580": ("CWorld__InitLODLists", "void __fastcall CWorld__InitLODLists(void * world)", "cworld-load-core-wave555", "Wave555"),
    "0x0050d680": ("CWorld__ReleaseSubObject_AndMaybeFree", "void * __thiscall CWorld__ReleaseSubObject_AndMaybeFree(void * this, uint flags)", "cworld-tail-wave556", "Wave556"),
    "0x0050d6a0": ("CWorld__PushWorldTextSlot", "void __thiscall CWorld__PushWorldTextSlot(void * this, int text_id, int slot_state)", "cworld-tail-wave556", "Wave556"),
    "0x0050d720": ("CWorld__UpdateWorldTextSlotTiming", "void __thiscall CWorld__UpdateWorldTextSlotTiming(void * this, int text_id, float primary_time, float secondary_time)", "cworld-tail-wave556", "Wave556"),
    "0x0050d760": ("CWorld__GetWorldTextSlotTimerValue", "double __thiscall CWorld__GetWorldTextSlotTimerValue(void * this, int slot_index)", "cworld-tail-wave556", "Wave556"),
    "0x0050d7a0": ("CWorld__ClearWorldTextSlot", "void __thiscall CWorld__ClearWorldTextSlot(void * this, int text_id)", "cworld-tail-wave556", "Wave556"),
    "0x0050d7d0": ("CWorld__IsMultiplayerMode", "int __fastcall CWorld__IsMultiplayerMode(void * world)", "cworld-tail-wave556", "Wave556"),
    "0x0050d7f0": ("CWorld__ClearLinkedObjectPairSet", "void __fastcall CWorld__ClearLinkedObjectPairSet(void * pair_set)", "cworld-tail-wave556", "Wave556"),
    "0x0050d9a0": ("CWorldMeshList__Clear", "void __cdecl CWorldMeshList__Clear(void)", "cworld-tail-wave556", "Wave556"),
    "0x0050d9e0": ("CWorldMeshList__Add", "void __cdecl CWorldMeshList__Add(char * mesh_name)", "cworld-tail-wave556", "Wave556"),
    "0x0050dc20": ("CWorldMeshList__MarkUsed", "void __cdecl CWorldMeshList__MarkUsed(char * mesh_name)", "cworld-tail-wave556", "Wave556"),
    "0x0050dcb0": ("CWorld__SpawnInitialThings", "void __cdecl CWorld__SpawnInitialThings(void)", "cworld-tail-wave556", "Wave556"),
    "0x0050df80": ("CWorldPhysicsManager__CreateThingByType", "void * __cdecl CWorldPhysicsManager__CreateThingByType(int thing_type_index)", "cworld-tail-wave556", "Wave556"),
}

CONTEXT_TARGETS = {
    "0x0050b9c0": "CWorld__LoadWorld",
    "0x0046cdf0": "CGame__LoadLevel",
    "0x004d7200": "CResourceAccumulator__ReadResourceFile",
    "0x00449dc0": "CEngine__LoadAllNamedMeshes",
    "0x0050f4b0": "CWorldPhysicsManager__CreateSquad",
    "0x00510060": "CWorldPhysicsManager__CreateEffect",
    "0x00510150": "CWorldPhysicsManager__CreateTrigger",
    "0x0048c650": "InitThing__CreateThingByType",
    "0x00505ae0": "CWaypointManager__LoadWaypoints",
    "0x004bcbf0": "CWorld__ApplyStaticMaskToOccupancyBitplanes",
    "0x004bcd60": "CWorld__RebuildOccupancyGridFromDynamicSet",
    "0x004f2580": "CText__GetStringById",
    "0x00483530": "CHud__RenderControllerSlotStatusPanel",
    "0x005362a0": "IScript__GetTextWidth",
    "0x004e3010": "CSpawnerThng__Init",
    "0x005392a0": "CScriptObjectCode__CollectSpawnThings",
    "0x004f86d0": "CUnit__Init",
    "0x0040f180": "BattleEngineConfigurations__Load",
}

KEY_XREFS = {
    ("0x0050b520", "0x0046cea9", "CGame__LoadLevel"),
    ("0x0050b520", "0x0050bbf5", "CWorld__LoadWorld"),
    ("0x0050d9e0", "0x0050cad1", "CWorld__LoadWorld"),
    ("0x0050d9e0", "0x004e32fc", "CSpawnerThng__Init"),
    ("0x0050d9e0", "0x0053932d", "CScriptObjectCode__CollectSpawnThings"),
    ("0x0050dc20", "0x004f908e", "CUnit__Init"),
    ("0x0050dcb0", "0x0050d431", "CWorld__LoadWorld"),
    ("0x0050df80", "0x0050ca98", "CWorld__LoadWorld"),
    ("0x0050df80", "0x0050dd5b", "CWorld__SpawnInitialThings"),
    ("0x0050df80", "0x004e4160", "CSpawnerThng__ProcessSpawnWave"),
}

RAW_TARGETS = {
    "0x00536d3c",
    "0x00537c51",
    "0x004d027b",
    "0x004dfa78",
}

CORE_DOCS = [
    PUBLIC_NOTE,
    AGGREGATE_NOTE,
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

OWNER_DOC_TOKENS = {
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "World.cpp" / "_index.md": (
        "Wave1073",
        "cworld-load-tail-review-wave1073",
        "0x0050b520 CWorld__LoadWorldFile",
        "0x0050d6a0 CWorld__PushWorldTextSlot",
        "0x0050dcb0 CWorld__SpawnInitialThings",
        "1357/1560 = 86.99%",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldMeshList.cpp" / "_index.md": (
        "Wave1073",
        "cworld-load-tail-review-wave1073",
        "0x0050d9e0 CWorldMeshList__Add",
        "0x0050dc20 CWorldMeshList__MarkUsed",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md": (
        "Wave1073",
        "cworld-load-tail-review-wave1073",
        "0x0050df80 CWorldPhysicsManager__CreateThingByType",
        "0x0050f4b0 CWorldPhysicsManager__CreateSquad",
        BACKUP_PATH,
    ),
}

DOC_TOKENS = (
    "Wave1073",
    "cworld-load-tail-review-wave1073",
    "0x0050a870 CWorld__ClearSetArrays",
    "0x0050ac70 CWorld__LoadScriptEvents",
    "0x0050b520 CWorld__LoadWorldFile",
    "0x0050d6a0 CWorld__PushWorldTextSlot",
    "0x0050d9e0 CWorldMeshList__Add",
    "0x0050dcb0 CWorld__SpawnInitialThings",
    "0x0050df80 CWorldPhysicsManager__CreateThingByType",
    "0x00537c40",
    "0x004dfa47",
    "812/1408 = 57.67%",
    "1357/1560 = 86.99%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime world-load behavior proven",
    "runtime spawn behavior proven",
    "exact raw-boundary identities proven",
    "exact layout proven",
    "exact source-body identity proven",
    "rebuild parity proven",
)


def norm(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def strict_clean_count(rows: list[dict[str, str]]) -> int:
    total = 0
    for row in rows:
        comment = row.get("comment", "").strip()
        signature = row.get("signature", "")
        if comment and not signature.startswith("undefined ") and not re.search(r"\bparam_\d+\b", signature):
            total += 1
    return total


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 23,
        "primary-tags.tsv": 23,
        "primary-xrefs.tsv": 62,
        "primary-instructions.tsv": 2095,
        "primary-decompile/index.tsv": 23,
        "context-metadata.tsv": 18,
        "context-tags.tsv": 18,
        "context-xrefs.tsv": 362,
        "context-instructions.tsv": 6272,
        "context-decompile/index.tsv": 18,
        "raw-xref-instructions.tsv": 253,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    quality = {norm(row["address"]): row for row in read_tsv(QUEUE_TSV)}
    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "primary-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "primary-tags.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "primary-decompile" / "index.tsv")}
    context = {norm(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    xrefs = read_tsv(BASE / "primary-xrefs.tsv")
    raw_rows = read_tsv(BASE / "raw-xref-instructions.tsv")

    for address, (name, signature, required_tag, historical_wave) in TARGETS.items():
        qrow = quality.get(address)
        row = metadata.get(address)
        require(qrow is not None, f"missing queue row for {address}", failures)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is None or qrow is None:
            continue

        require(row.get("name") == name, f"name mismatch at {address}", failures)
        require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
        require(row.get("name") == qrow.get("name"), f"queue name mismatch at {address}", failures)
        require(row.get("signature") == qrow.get("signature"), f"queue signature mismatch at {address}", failures)
        require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
        comment = row.get("comment", "")
        require(historical_wave in comment, f"missing historical wave token at {address}: {historical_wave}", failures)
        require("Static retail-binary evidence only" in comment, f"missing bounded static token at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = {"static-reaudit", "retail-binary-evidence", "comment-hardened", "signature-corrected", required_tag}
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)

    actual_xrefs = {(norm(row["target_addr"]), norm(row["from_addr"]), row["from_function"]) for row in xrefs}
    for key in KEY_XREFS:
        require(key in actual_xrefs, f"missing key xref {key}", failures)

    raw_targets = {norm(row["target_raw"]) for row in raw_rows}
    for address in RAW_TARGETS:
        require(address in raw_targets, f"missing raw xref window for {address}", failures)
    require(any(row.get("function_name") == "<no_function>" for row in raw_rows), "raw windows lost no-function evidence", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=23 found=23 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=23 missing=0",
        "primary-xrefs.log": "Wrote 62 rows",
        "primary-instructions.log": "Wrote 2095 function-body instruction rows",
        "primary-decompile.log": "targets=23 dumped=23 missing=0 failed=0",
        "context-metadata.log": "targets=18 found=18 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=18 missing=0",
        "context-xrefs.log": "Wrote 362 rows",
        "context-instructions.log": "Wrote 6272 function-body instruction rows",
        "context-decompile.log": "targets=18 dumped=18 missing=0 failed=0",
        "raw-xref-instructions.log": "Wrote 253 instruction rows",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    require(len(rows) == 6246, "quality TSV row count mismatch", failures)
    require(commented == 6246, "quality TSV commented count mismatch", failures)
    require(strict_clean_count(rows) == 6246, "quality TSV strict-clean count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174721927 or backup.get("totalBytes") == 174721927.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in CORE_DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-cworld-load-tail-review-wave1073") == r"py -3 tools\ghidra_cworld_load_tail_review_wave1073_probe.py --check", "missing focused package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1073-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1073 --check", "missing aggregate package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1073 CWorld load/tail review" for row in ledger_rows), "missing Wave1073 ledger row", failures)
    require(any(row.get("task") == "Wave1073 CWorld load/tail review" and row.get("attempt_id") == 20655 for row in attempts), "missing Wave1073 attempt row", failures)


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
        print("Wave1073 CWorld load/tail review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1073 CWorld load/tail review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
