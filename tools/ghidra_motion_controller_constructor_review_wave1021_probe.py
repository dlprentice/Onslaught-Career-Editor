#!/usr/bin/env python3
"""Validate Wave1021 motion-controller constructor read-only artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1021-motion-controller-constructor-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_motion_controller_constructor_review_wave1021_2026-05-31.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1021_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
MINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Mine.cpp" / "_index.md"
SENTINEL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Sentinel.cpp.md"
SENTINEL_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Sentinel.cpp" / "_index.md"
MCTENTACLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MCTentacle.cpp.md"
WARSPITE_DOME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WarspiteDome.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUALITY_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-222637_post_wave1021_motion_controller_constructor_review_verified"

TARGETS = {
    "0x0049c3e0": ("CMCMine__Constructor", "void * __thiscall CMCMine__Constructor(void * this, void * owner_mine)"),
    "0x0049c5d0": ("CMCSentinel__Constructor", "void * __thiscall CMCSentinel__Constructor(void * this, void * owner_sentinel)"),
    "0x0049cad0": ("CMCTentacle__Constructor", "void * __thiscall CMCTentacle__Constructor(void * this, void * owner_tentacle)"),
    "0x0049ef80": ("CMCWarspiteDome__Constructor", "void * __thiscall CMCWarspiteDome__Constructor(void * this, void * owner_dome)"),
}

COMMENT_TOKENS = {
    "0x0049c3e0": ("Wave434", "RET 0x4", "0x005dc3f4", "+0x08", "runtime mine motion behavior"),
    "0x0049c5d0": ("Wave434", "RET 0x4", "0x005dc420", "0xc479c000", "runtime sentinel motion behavior"),
    "0x0049cad0": ("Wave435", "RET 0x4", "0x005dc450", "0xbf800000", "runtime tentacle motion behavior"),
    "0x0049ef80": ("Wave435", "RET 0x4", "0x005dc484", "+0x08", "runtime dome motion behavior"),
}

CONTEXT_TARGETS = {
    "0x004bae30": "CMotionController__ctor_base",
    "0x004bae50": "CMotionController__dtor_base",
    "0x0049c400": "CMCMine__ScalarDeletingDestructor",
    "0x0049c420": "CMCMine__Destructor",
    "0x0049c600": "CMCSentinel__ScalarDeletingDestructor",
    "0x0049c620": "CMCSentinel__Destructor",
    "0x0049cb20": "CMCTentacle__ScalarDeletingDestructor",
    "0x0049cb40": "CMCTentacle__Destructor",
    "0x0049efa0": "CMCWarspiteDome__ScalarDeletingDestructor",
    "0x0049efc0": "CMCWarspiteDome__Destructor",
}

DOC_TOKENS = (
    "Wave1021",
    "motion-controller-constructor-review-wave1021",
    "0x0049c3e0 CMCMine__Constructor",
    "0x0049c5d0 CMCSentinel__Constructor",
    "0x0049cad0 CMCTentacle__Constructor",
    "0x0049ef80 CMCWarspiteDome__Constructor",
    "532/1408 = 37.78%",
    "761/1493 = 50.97%",
    "460/500 = 92.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OWNER_DOC_TOKENS = {
    MINE_DOC: ("Wave1021", "motion-controller-constructor-review-wave1021", "CMCMine__Constructor", "0x005dc3f4", BACKUP_PATH),
    SENTINEL_DOC: ("Wave1021", "motion-controller-constructor-review-wave1021", "CMCSentinel__Constructor", "0x005dc420", BACKUP_PATH),
    SENTINEL_INDEX: ("Wave1021", "motion-controller-constructor-review-wave1021", "CMCSentinel__Constructor", "0x005dc420", BACKUP_PATH),
    MCTENTACLE_DOC: ("Wave1021", "motion-controller-constructor-review-wave1021", "CMCTentacle__Constructor", "CMCWarspiteDome__Constructor", BACKUP_PATH),
    WARSPITE_DOME_DOC: ("Wave1021", "motion-controller-constructor-review-wave1021", "CMCWarspiteDome__Constructor", "0x005dc484", BACKUP_PATH),
}

OVERCLAIMS = (
    "runtime mine motion behavior proven",
    "runtime sentinel motion behavior proven",
    "runtime tentacle motion behavior proven",
    "runtime dome motion behavior proven",
    "exact layout proven",
    "exact source-body identity proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 4,
        "primary-tags.tsv": 4,
        "primary-xrefs.tsv": 7,
        "primary-instructions.tsv": 51,
        "primary-decompile/index.tsv": 4,
        "context-metadata.tsv": 10,
        "context-xrefs.tsv": 37,
        "context-instructions.tsv": 135,
        "context-decompile/index.tsv": 10,
        "vtable-slots.tsv": 48,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "primary-metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "primary-tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "primary-decompile" / "index.tsv"), "address")
    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)
            actual_tags = set(tag_row.get("tags", "").split(";"))
            for token in ("static-reaudit", "constructor", "comment-hardened", "signature-corrected", "retail-binary-evidence"):
                require(token in actual_tags, f"missing tag {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    context = rows_by(read_tsv(BASE / "context-metadata.tsv"), "address")
    context_decompile = rows_by(read_tsv(BASE / "context-decompile" / "index.tsv"), "address")
    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}: {row.get('name')}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = context_decompile.get(address)
        require(dec is not None, f"missing context decompile {address}", failures)
        if dec:
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)

    xref_text = read_text(BASE / "primary-xrefs.tsv") + "\n" + read_text(BASE / "context-xrefs.tsv")
    for token in ("004ba3d0", "004deafd", "004f07a9", "00504918", "CMine__Init", "CSentinel__Init", "CTentacle__CreateTentacleGuide", "CWarspiteDome__Init"):
        require(token in xref_text, f"missing xref token: {token}", failures)

    instruction_text = read_text(BASE / "primary-instructions.tsv") + "\n" + read_text(BASE / "context-instructions.tsv")
    for token in (
        "0x0049c3e3\tCALL\t0x004bae30",
        "0x0049c3ec\tMOV\tdword ptr [ESI], 0x5dc3f4",
        "0x0049c5dc\tMOV\tdword ptr [ESI], 0x5dc420",
        "0x0049c5e5\tMOV\tEAX, 0xc479c000",
        "0x0049cadc\tMOV\tdword ptr [ESI], 0x5dc450",
        "0x0049cb0e\tMOV\tdword ptr [ESI + 0x28], 0xbf800000",
        "0x0049ef8c\tMOV\tdword ptr [ESI], 0x5dc484",
        "0x004bae37\tMOV\tdword ptr [EAX], 0x5dc778",
        "0x004bae56\tJMP\t0x004bac40",
        "0x0049cc20\tCALL\t0x004bae50",
        "0x0049efcd\tJMP\t0x004bae50",
    ):
        require(token in instruction_text, f"missing instruction token: {token}", failures)

    vtable_rows = read_tsv(BASE / "vtable-slots.tsv")
    by_vtable_slot = {(row.get("vtable"), row.get("slot_index")): row for row in vtable_rows}
    expected_vslots = {
        ("005dc3f4", "1"): "CMCMine__ScalarDeletingDestructor",
        ("005dc3f4", "4"): "CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440",
        ("005dc3f4", "8"): "CMCMine__VFunc_08_CheckCachedHeightState_0049c4b0",
        ("005dc420", "1"): "CMCSentinel__ScalarDeletingDestructor",
        ("005dc420", "4"): "CMCSentinel__VFunc_04_UpdateX1TurretOrBarrelTransform_0049c640",
        ("005dc450", "1"): "CMCTentacle__ScalarDeletingDestructor",
        ("005dc450", "4"): "CMCTentacle__VFunc_04_UpdateInterpolatedBoneTransform_0049e660",
        ("005dc450", "5"): "CMCTentacle__VFunc_05_WriteInterpolatedBoneFloat_0049ead0",
        ("005dc450", "8"): "CMCTentacle__VFunc_08_CheckCachedUpdateTime_0049ec80",
        ("005dc484", "1"): "CMCWarspiteDome__ScalarDeletingDestructor",
        ("005dc484", "4"): "CMCWarspiteDome__VFunc_04_UpdateDomeTransform_0049efe0",
        ("005dc484", "8"): "SharedVFunc__Return1_004014a0",
    }
    for key, name in expected_vslots.items():
        row = by_vtable_slot.get(key)
        require(row is not None, f"missing vtable slot {key}", failures)
        if row:
            require(row.get("function_name") == name, f"vtable slot {key} name mismatch: {row.get('function_name')}", failures)
            require(row.get("status") == "OK", f"vtable slot {key} status mismatch", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "primary-metadata.log": "targets=4 found=4 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "primary-xrefs.log": "Wrote 7 rows",
        "primary-instructions.log": "Wrote 51 function-body instruction rows",
        "primary-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "context-metadata.log": "targets=10 found=10 missing=0",
        "context-xrefs.log": "Wrote 37 rows",
        "context-instructions.log": "Wrote 135 function-body instruction rows",
        "context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=4 rows=48",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "FAIL:", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    quality_rows = rows_by(read_tsv(QUALITY_TSV), "address")
    for address, (name, signature) in TARGETS.items():
        row = quality_rows.get(address)
        require(row is not None, f"missing quality row {address}", failures)
        if row:
            require(row.get("name") == name, f"quality name mismatch {address}", failures)
            require(row.get("signature") == signature, f"quality signature mismatch {address}", failures)
            require(row.get("comment", "").strip(), f"quality comment missing {address}", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        TRACKING_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-motion-controller-constructor-review-wave1021")
        == r"py -3 tools\ghidra_motion_controller_constructor_review_wave1021_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1021-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1021 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1021 motion-controller constructor review" for row in ledger), "missing Wave1021 ledger row", failures)
    require(
        any(row.get("task") == "Wave1021 motion-controller constructor review" and row.get("attempt_id") == 20603 for row in attempts),
        "missing Wave1021 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue(failures)
    check_docs(failures)

    if failures:
        print("Wave1021 motion-controller constructor review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1021 motion-controller constructor review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
