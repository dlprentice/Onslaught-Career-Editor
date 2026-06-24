#!/usr/bin/env python3
"""Validate Wave1082 InfantryAI vtable-boundary read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1082-infantryai-vtable-boundary-review"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PACKAGE_JSON = ROOT / "package.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-110925_post_wave1082_infantryai_vtable_boundary_verified"

TARGETS = {
    "0x004ff330": ("SharedUnitAI__HandleEventAndMaybeFire_004ff330", "int __thiscall SharedUnitAI__HandleEventAndMaybeFire_004ff330(void * this, int event_code)", "0x005dbf14"),
    "0x004ff4f0": ("SharedUnitAI__UpdateTargetAndAnimationState_004ff4f0", "void __thiscall SharedUnitAI__UpdateTargetAndAnimationState_004ff4f0(void * this)", "0x005dbf24"),
    "0x004fea30": ("SharedUnitAI__CheckField24TargetState_004fea30", "int __thiscall SharedUnitAI__CheckField24TargetState_004fea30(void * this)", "0x005dbf28"),
    "0x004febe0": ("SharedUnitAI__CheckField20TargetMode1_004febe0", "int __thiscall SharedUnitAI__CheckField20TargetMode1_004febe0(void * this)", "0x005dbf2c"),
    "0x004ffb60": ("SharedUnitAI__TryStartField28TimedEvent_004ffb60", "int __thiscall SharedUnitAI__TryStartField28TimedEvent_004ffb60(void * this)", "0x005dbf30"),
    "0x004feac0": ("SharedUnitAI__CheckField24RangeAgainstCandidate_004feac0", "int __thiscall SharedUnitAI__CheckField24RangeAgainstCandidate_004feac0(void * this, void * candidate)", "0x005dbf34"),
    "0x0048a030": ("CInfantryAI__UpdateSupportSelection_0048a030", "void __thiscall CInfantryAI__UpdateSupportSelection_0048a030(void * this)", "0x005dbf38"),
    "0x004ffbb0": ("SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0", "int __thiscall SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0(void * this, void * candidate)", "0x005dbf3c"),
    "0x004ff710": ("SharedUnitAI__CheckField0cCloseTargetGate_004ff710", "int __thiscall SharedUnitAI__CheckField0cCloseTargetGate_004ff710(void * this)", "0x005dbf40"),
    "0x00402d20": ("SharedVFunc__ReturnThis_00402d20", "void * __thiscall SharedVFunc__ReturnThis_00402d20(void * this)", "0x005dbf58"),
    "0x004f45c0": ("SharedVFunc__ForwardField64FloatOrZero_004f45c0", "float __thiscall SharedVFunc__ForwardField64FloatOrZero_004f45c0(void * this)", "0x005dbff0"),
}

COMMON_TAGS = {
    "static-reaudit",
    "infantryai-vtable-boundary-review-wave1082",
    "wave1082-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "signature-hardened",
    "comment-hardened",
    "vtable-slot",
    "ai-vtable",
}

CORE_DOCS = [
    ROOT / "release" / "readiness" / "ghidra_infantryai_vtable_boundary_wave1082_2026-06-02.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Infantry.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "UnitAI.cpp" / "_index.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

ANCHORS = (
    "Wave1082",
    "infantryai-vtable-boundary-review-wave1082",
    "0x004ff330 SharedUnitAI__HandleEventAndMaybeFire_004ff330",
    "0x0048a030 CInfantryAI__UpdateSupportSelection_0048a030",
    "0x004f45c0 SharedVFunc__ForwardField64FloatOrZero_004f45c0",
    "0x005dbf14",
    "1405/1560 = 90.06%",
    "812/1408 = 57.67%",
    "6294/6294 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime ai behavior proven",
    "runtime targeting behavior proven",
    "rebuild parity proven",
    "exact source virtual names proven",
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


def status_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = row.get("status", "")
        counts[status] = counts.get(status, 0) + 1
    return counts


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 11,
        "pre-tags.tsv": 11,
        "pre-xrefs.tsv": 303,
        "pre-instructions-around.tsv": 803,
        "pre-instructions-wide.tsv": 2959,
        "pre-decompile/index.tsv": 11,
        "pre-vtable-slots.tsv": 96,
        "pre-listing-state.tsv": 29,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 303,
        "post-instructions.tsv": 1286,
        "post-decompile/index.tsv": 11,
        "post-vtable-slots.tsv": 96,
        "post-listing-state.tsv": 29,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    require(status_counts(read_tsv(BASE / "pre-listing-state.tsv")) == {"UNDEFINED": 9, "INSTRUCTION_NO_FUNCTION": 11, "NO_MEMORY_BLOCK": 9}, "pre listing-state status mismatch", failures)
    require(status_counts(read_tsv(BASE / "post-listing-state.tsv")) == {"UNDEFINED": 9, "OK": 11, "NO_MEMORY_BLOCK": 9}, "post listing-state status mismatch", failures)
    require(status_counts(read_tsv(BASE / "pre-vtable-slots.tsv")) == {"NO_FUNCTION_AT_POINTER": 25, "OK": 71}, "pre vtable status mismatch", failures)
    require(status_counts(read_tsv(BASE / "post-vtable-slots.tsv")) == {"NO_FUNCTION_AT_POINTER": 14, "OK": 82}, "post vtable status mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    vtable_refs = {(normalize_address(row["target_addr"]), normalize_address(row["from_addr"])) for row in xrefs}

    for address, (name, signature, slot) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Wave1082", "Static retail Ghidra", "runtime"):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing common tags at {address}: {COMMON_TAGS - actual_tags}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile at {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require((address, slot) in vtable_refs, f"missing CInfantryAI slot xref for {address} from {slot}", failures)


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 created=0 would_create=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "apply.log": "SUMMARY: updated=11 skipped=0 created=11 would_create=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0",
        "post-metadata.log": "targets=11 found=11 missing=0",
        "post-tags.log": "rows=11 missing=0",
        "post-xrefs.log": "Wrote 303 rows",
        "post-instructions.log": "Wrote 1286 function-body instruction rows",
        "post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "post-vtable-slots.log": "rows=96",
        "post-listing-state.log": "rows=29",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected bad token in {relative}: {bad}", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["status"] == "PASS", "queue status mismatch", failures)
    require(queue["totalFunctions"] == 6294, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174787463, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff mismatch", failures)


def check_docs_and_ledgers(failures: list[str]) -> None:
    for path in CORE_DOCS:
        text = read_text(path)
        for token in ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    script = package.get("scripts", {}).get("test:ghidra-infantryai-vtable-boundary-wave1082")
    require(script == r"py -3 tools\ghidra_infantryai_vtable_boundary_wave1082_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1082 InfantryAI vtable boundary" for row in ledger_rows), "missing Wave1082 ledger row", failures)
    require(any(row.get("task") == "Wave1082 InfantryAI vtable boundary" and row.get("attempt_id") == 20664 for row in attempt_rows), "missing Wave1082 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_backup(failures)
    check_docs_and_ledgers(failures)

    if failures:
        print("Wave1082 InfantryAI vtable-boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1082 InfantryAI vtable-boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
