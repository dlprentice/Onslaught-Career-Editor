#!/usr/bin/env python3
"""Validate Wave846 WorldPhysicsManager load/resolve read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave846-worldphysics-load-resolve"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_worldphysics_load_resolve_wave846_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
WPM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260525-060333_post_wave846_worldphysics_load_resolve_verified"
NEXT_HEAD = "0x00512040 CLTShell__InitUnhandledExceptionLogFile"

TARGETS = {
    "0x00510520": {
        "name": "CWorldPhysicsManager__ResolveLoadedDefinitionReferences",
        "xref": "0x0046cdd7",
        "tokens": (
            "CGame__LoadResources",
            "DAT_008553ec",
            "DAT_008553f0",
            "DAT_008553f8",
            "DAT_008553fc",
            "DAT_00855400",
            "DAT_00855404",
            "DAT_00855408",
            "CParticleSet__FindByNameAndTrackLinkSlot",
            "CSoundManager__GetEffectByName",
        ),
    },
    "0x00510740": {
        "name": "CWorldPhysicsManager__FreeNestedThingSets_6C",
        "xref": "0x0046cc61",
        "tokens": ("CGame__ShutdownRestartLoop", "entry's nested CSPtrSet at +0x6c", "DAT_008553fc", "DAT_00855400"),
    },
    "0x00510800": {
        "name": "CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData",
        "xref": "0x004f0092",
        "tokens": (
            "CLTShell__InitializeRuntimeAndLoadCoreResources",
            "data/default_physics.dat",
            "data/battle_engine_configuration",
            "DAT_006602a0",
            "CBattleEngineData",
        ),
    },
    "0x00510a90": {
        "name": "CWorldPhysicsManager__ClearAndFreeAllDefinitionLists",
        "xref": "0x004f00e0",
        "tokens": (
            "CLTShell__ShutdownRuntimeAndReleaseResources",
            "0x0051081e",
            "DAT_008553e8 through DAT_00855408",
            "Wave559 per-entry cleanup helpers",
            "DAT_00855408",
        ),
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "worldphysics-load-resolve-wave846",
    "wave846-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "worldphysicsmanager",
    "definition-list",
    "load-resolve",
}

DOC_TOKENS = (
    "Wave846 WorldPhysics load/resolve",
    "worldphysics-load-resolve-wave846",
    "0x00510520 CWorldPhysicsManager__ResolveLoadedDefinitionReferences",
    "0x00510740 CWorldPhysicsManager__FreeNestedThingSets_6C",
    "0x00510800 CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData",
    "0x00510a90 CWorldPhysicsManager__ClearAndFreeAllDefinitionLists",
    "void __cdecl CWorldPhysicsManager__ResolveLoadedDefinitionReferences(void)",
    "void __cdecl CWorldPhysicsManager__FreeNestedThingSets_6C(void)",
    "void __cdecl CWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData(void)",
    "void __cdecl CWorldPhysicsManager__ClearAndFreeAllDefinitionLists(void)",
    "0x0046cdd7",
    "0x0046cc61",
    "0x004f0092",
    "0x004f00e0",
    "0x0051081e",
    "data/default_physics.dat",
    "data/battle_engine_configuration",
    "5673/6098 = 93.03%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime load behavior proven",
    "runtime resolve behavior proven",
    "runtime shutdown behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
    "exact source method identity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_for(name: str) -> str:
    return f"void __cdecl {name}(void)"


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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 5,
        "pre-instructions.tsv": 14004,
        "pre-context-metadata.tsv": 23,
        "pre-context-tags.tsv": 23,
        "pre-decompile/index.tsv": 4,
        "pre-xref-site-instructions.tsv": 445,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 5,
        "post-instructions.tsv": 3300,
        "post-context-metadata.tsv": 23,
        "post-context-tags.tsv": 23,
        "post-decompile/index.tsv": 4,
        "post-xref-site-instructions.tsv": 325,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {normalize_address(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}
    xref_rows = read_tsv(BASE / "post-xrefs.tsv")
    xref_pairs = {(normalize_address(row["target_addr"]), normalize_address(row["from_addr"])) for row in xref_rows}

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata row for {address}", failures)
        if row is not None:
            signature = signature_for(spec["name"])
            require(row.get("name") == spec["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Wave846 static read-back", "no pushed arguments or ECX receiver setup", "Static retail Ghidra evidence only", *spec["tokens"]):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing tags at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature_for(spec["name"]), f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require((address, normalize_address(spec["xref"])) in xref_pairs, f"missing xref {spec['xref']} -> {address}", failures)

    require(("0x00510a90", "0x0051081e") in xref_pairs, "missing reload self-call xref to clear/free", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 5 rows",
        "post-instructions.log": "Wrote 3300 instruction rows",
        "post-context-metadata.log": "targets=23 found=23 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=23 missing=0",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-xref-site-instructions.log": "Wrote 325 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=5673",
        "queue-probe.log": "Commentless functions: 425",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave846.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave846_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "READBACK_BAD", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 425, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5673, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5673, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00512040", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CLTShell__InitUnhandledExceptionLogFile", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171871111 or backup.get("totalBytes") == 171871111.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        WPM_DOC,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-worldphysics-load-resolve-wave846")
        == r"py -3 tools\ghidra_worldphysics_load_resolve_wave846_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave846 WorldPhysics load/resolve" for row in ledger_rows), "missing Wave846 ledger row", failures)
    require(any(row.get("task") == "Wave846 WorldPhysics load/resolve" and row.get("attempt_id") == 20501 for row in attempts), "missing Wave846 attempt row", failures)


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
        print("Wave846 WorldPhysics load/resolve probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave846 WorldPhysics load/resolve probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
