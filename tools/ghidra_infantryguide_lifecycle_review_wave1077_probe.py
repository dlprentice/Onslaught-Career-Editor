#!/usr/bin/env python3
"""Validate Wave1077 guide-family lifecycle boundary read-back artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1077-infantryguide-lifecycle-review"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-073929_post_wave1077_infantryguide_lifecycle_review_verified"

TARGETS = {
    "0x0047d750": {
        "name": "CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750",
        "signature": "void __fastcall CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750(void * this)",
        "tokens": ("slot 3", "0x005dbd9c", "owner pointer at this+0x18", "separate proof"),
    },
    "0x0047e2d0": {
        "name": "SharedGuide__VFunc04_SetVectorMode1_0047e2d0",
        "signature": "void __thiscall SharedGuide__VFunc04_SetVectorMode1_0047e2d0(void * this, int lane0_raw, int lane1_raw, int lane2_raw, int lane3_raw, int mode_gate)",
        "tokens": ("slot 4", "0x005dbfb8", "0x005dbda0", "RET 0x14"),
    },
    "0x0047e310": {
        "name": "SharedGuide__VFunc05_SetVectorMode2_0047e310",
        "signature": "void __thiscall SharedGuide__VFunc05_SetVectorMode2_0047e310(void * this, int lane0_raw, int lane1_raw, int lane2_raw, int lane3_raw)",
        "tokens": ("slot 5", "0x005dbfbc", "0x005dbda4", "mode 2"),
    },
    "0x0047e340": {
        "name": "SharedGuide__VFunc06_SetVectorMode3_0047e340",
        "signature": "void __thiscall SharedGuide__VFunc06_SetVectorMode3_0047e340(void * this, int lane0_raw, int lane1_raw, int lane2_raw, int lane3_raw)",
        "tokens": ("slot 6", "0x005dbfc0", "0x005dbda8", "mode 3"),
    },
    "0x0047e370": {
        "name": "SharedGuide__VFunc07_SetVectorModeFromOwnerState_0047e370",
        "signature": "void __thiscall SharedGuide__VFunc07_SetVectorModeFromOwnerState_0047e370(void * this, int lane0_raw, int lane1_raw, int lane2_raw, int lane3_raw)",
        "tokens": ("slot 7", "0x005dbfc4", "0x005dbdac", "owner+0x13c"),
    },
    "0x0047e3d0": {
        "name": "SharedGuide__VFunc08_ResetVectorsFromOwner_0047e3d0",
        "signature": "void __fastcall SharedGuide__VFunc08_ResetVectorsFromOwner_0047e3d0(void * this)",
        "tokens": ("slot 8", "0x005dbfc8", "0x005dbdb0", "owner+0x14c"),
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "infantryguide-lifecycle-review-wave1077",
    "wave1077-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "guide-shared-vtable",
    "vtable-slot",
    "signature-hardened",
    "comment-hardened",
}

DOC_TOKENS = (
    "Wave1077",
    "infantryguide-lifecycle-review-wave1077",
    "0x0047d750 CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750",
    "0x0047e2d0 SharedGuide__VFunc04_SetVectorMode1_0047e2d0",
    "0x0047e310 SharedGuide__VFunc05_SetVectorMode2_0047e310",
    "0x0047e340 SharedGuide__VFunc06_SetVectorMode3_0047e340",
    "0x0047e370 SharedGuide__VFunc07_SetVectorModeFromOwnerState_0047e370",
    "0x0047e3d0 SharedGuide__VFunc08_ResetVectorsFromOwner_0047e3d0",
    "0x005dbfa8",
    "0x005dbd90",
    "812/1408 = 57.67%",
    "1371/1560 = 87.88%",
    "500/500 = 100.00%",
    "6260/6260 = 100.00%",
    BACKUP_PATH,
)

DOCS = [
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "release" / "readiness" / "ghidra_infantryguide_lifecycle_review_wave1077_2026-06-02.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Guide.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GroundVehicle.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Infantry.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

PACKAGE_JSON = ROOT / "package.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "exact source-body identity proven",
    "all systems complete",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
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


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if unescape_tsv(row.get("comment", "")).strip())
    strict_clean = sum(
        1
        for row in rows
        if unescape_tsv(row.get("comment", "")).strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 7,
        "tags.tsv": 7,
        "xrefs.tsv": 9,
        "instructions.tsv": 830,
        "decompile/index.tsv": 7,
        "context-metadata.tsv": 18,
        "context-xrefs.tsv": 20,
        "context-instructions.tsv": 1969,
        "context-decompile/index.tsv": 18,
        "vtable-slots.tsv": 32,
        "unresolved-vtable-instructions-around.tsv": 546,
        "groundvehicle-slot3-wide.tsv": 526,
        "post-created-metadata.tsv": 6,
        "post-created-tags.tsv": 6,
        "post-created-xrefs.tsv": 90,
        "post-created-instructions.tsv": 807,
        "post-created-decompile/index.tsv": 6,
        "post-vtable-slots.tsv": 32,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-created-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-created-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-created-decompile" / "index.tsv")}

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == spec["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == spec["signature"], f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in spec["tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"missing common tags at {address}: {COMMON_TAGS - actual}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == spec["name"], f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == spec["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    vtable_rows = read_tsv(BASE / "post-vtable-slots.tsv")
    by_vtable_slot = {(row["vtable"], row["slot_index"]): row for row in vtable_rows}
    expected_slots = {
        ("005dbfa8", "4"): "SharedGuide__VFunc04_SetVectorMode1_0047e2d0",
        ("005dbfa8", "5"): "SharedGuide__VFunc05_SetVectorMode2_0047e310",
        ("005dbfa8", "6"): "SharedGuide__VFunc06_SetVectorMode3_0047e340",
        ("005dbfa8", "7"): "SharedGuide__VFunc07_SetVectorModeFromOwnerState_0047e370",
        ("005dbfa8", "8"): "SharedGuide__VFunc08_ResetVectorsFromOwner_0047e3d0",
        ("005dbd90", "3"): "CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750",
        ("005dbd90", "4"): "SharedGuide__VFunc04_SetVectorMode1_0047e2d0",
        ("005dbd90", "5"): "SharedGuide__VFunc05_SetVectorMode2_0047e310",
        ("005dbd90", "6"): "SharedGuide__VFunc06_SetVectorMode3_0047e340",
        ("005dbd90", "7"): "SharedGuide__VFunc07_SetVectorModeFromOwnerState_0047e370",
        ("005dbd90", "8"): "SharedGuide__VFunc08_ResetVectorsFromOwner_0047e3d0",
    }
    for key, expected_name in expected_slots.items():
        row = by_vtable_slot.get(key)
        require(row is not None, f"missing vtable slot {key}", failures)
        if row is not None:
            require(row.get("function_name") == expected_name, f"vtable slot {key} name mismatch", failures)
            require(row.get("status") == "OK", f"vtable slot {key} status mismatch", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "updated=6 skipped=0 created=0 would_create=6 renamed=0 would_rename=0 signature_updated=6 comment_updated=6 tag_updated=6 missing=0 bad=0",
        "apply.log": "updated=6 skipped=0 created=6 would_create=0 renamed=0 would_rename=0 signature_updated=6 comment_updated=6 tag_updated=6 missing=0 bad=0",
        "apply-final-dry.log": "updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_updated=0 tag_updated=0 missing=0 bad=0",
        "post-created-metadata.log": "targets=6 found=6 missing=0",
        "post-created-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-created-xrefs.log": "Wrote 90 rows",
        "post-created-instructions.log": "Wrote 807 function-body instruction rows",
        "post-created-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-vtable-slots.log": "targets=2 rows=32",
        "quality-refresh.log": "total_functions=6260 commented_functions=6260",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6260, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(quality["legacyWeakNameCount"] == 0, "legacy weak count mismatch", failures)
    require(quality["uncertainOwnerNameCount"] == 0, "uncertain owner count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6260, "quality TSV row count mismatch", failures)
    require(commented == 6260, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6260, "strict clean-signature count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174754695, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_ledgers(failures: list[str]) -> None:
    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-infantryguide-lifecycle-review-wave1077")
        == r"py -3 tools\ghidra_infantryguide_lifecycle_review_wave1077_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1077-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1077 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1077 InfantryGuide lifecycle review" for row in ledger_rows), "missing ledger row", failures)
    require(
        any(row.get("task") == "Wave1077 InfantryGuide lifecycle review" and row.get("attempt_id") == 20659 for row in attempts),
        "missing attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs_and_ledgers(failures)

    if failures:
        print("Wave1077 InfantryGuide lifecycle review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave1077 InfantryGuide lifecycle review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
