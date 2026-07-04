#!/usr/bin/env python3
"""Validate Wave992 cannon/turret activation read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave992-cannon-turret-activation-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cannon_turret_activation_review_wave992_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
CANNON_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Cannon.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-053822_post_wave992_cannon_turret_activation_review_verified"

TARGETS = {
    "0x0041b1a0": ("CCannon__Init", "void __thiscall CCannon__Init(void * this, void * init)"),
    "0x0041b370": ("CCannon__UpdateState", "void __fastcall CCannon__UpdateState(void * this)"),
    "0x0041b450": ("CCannon__VFuncSlot_02_RemoveFromWorldAndForward", "void __fastcall CCannon__VFuncSlot_02_RemoveFromWorldAndForward(void * this)"),
    "0x0041b470": ("CCannon__AdvanceActivationAnimationState", "int __fastcall CCannon__AdvanceActivationAnimationState(void * this)"),
    "0x0041b540": ("CCannon__GetMidpoint", "void __thiscall CCannon__GetMidpoint(void * this, float * outMidpoint)"),
    "0x0041b590": ("CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph", "int __fastcall CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph(void * this)"),
    "0x0047c970": ("CGroundUnit__UpdateLinkedEffectsByHeightClearance", "void __fastcall CGroundUnit__UpdateLinkedEffectsByHeightClearance(void * this)"),
    "0x0047ce80": ("CGroundUnit__MarkDestroyedAndResetState", "int __fastcall CGroundUnit__MarkDestroyedAndResetState(void * this)"),
    "0x004fd4d0": ("CCannon__SelectTarget", "void __thiscall CCannon__SelectTarget(void * this, float * outTargetPosition)"),
    "0x00495230": ("CMCCannon__Ctor", "void * __thiscall CMCCannon__Ctor(void * this, void * ownerField8)"),
    "0x00495260": ("CMCCannon__ScalarDeletingDestructor", "void * __thiscall CMCCannon__ScalarDeletingDestructor(void * this, uint flags)"),
    "0x00495280": ("CMCCannon__Dtor", "void __thiscall CMCCannon__Dtor(void * this)"),
    "0x004952a0": ("CMCCannon__VFunc_04_UpdateTurretBarrelTransform", "void __thiscall CMCCannon__VFunc_04_UpdateTurretBarrelTransform(void * this, void * meshPart, void * heightAdjustOut, void * transformOut, int reservedArg)"),
}

PRIMARY_TARGETS = (
    "0x0041b1a0",
    "0x0041b370",
    "0x0041b450",
    "0x0041b470",
    "0x0041b540",
    "0x0041b590",
    "0x004fd4d0",
)

COMMON_TAGS = {
    "static-reaudit",
    "cannon-turret-activation-review-wave992",
    "wave992-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "tag-corrected",
    "cannon",
}

COMMENT_TOKENS = {
    "0x0041b1a0": ("Wave992 Cannon/turret activation review", "CGroundUnit__Init", "+0x260/+0x264"),
    "0x0041b370": ("Wave992 Cannon/turret activation review", "CGroundUnit__UpdateLinkedEffectsByHeightClearance", "+0x214"),
    "0x0041b450": ("Wave992 Cannon/turret activation review", "not a destructor body", "CUnit__VFunc02_CleanupWorldLinksAndForward"),
    "0x0041b470": ("Wave992 Cannon/turret activation review", "Activate/Deactivate/Active/Inactive", "+0x260"),
    "0x0041b540": ("Wave992 Cannon/turret activation review", "CCannon__SelectTarget", "0.5 constant"),
    "0x0041b590": ("Wave992 Cannon/turret activation review", "does not support the old CanFire label", "CGroundUnit__MarkDestroyedAndResetState"),
    "0x004fd4d0": ("Wave992 Cannon/turret activation review", "CThing__GetCentrePos", "CDiveBomber__SelectTarget"),
}

DOC_TOKENS = (
    "Wave992",
    "cannon-turret-activation-review-wave992",
    "0x0041b1a0 CCannon__Init",
    "0x0041b370 CCannon__UpdateState",
    "0x0041b450 CCannon__VFuncSlot_02_RemoveFromWorldAndForward",
    "0x0041b470 CCannon__AdvanceActivationAnimationState",
    "0x0041b590 CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph",
    "0x004fd4d0 CCannon__SelectTarget",
    "446/1408 = 31.68%",
    "538/1478 = 36.40%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime turret activation behavior proven",
    "runtime firing behavior proven",
    "exact layout proven",
    "source-body identity proven",
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


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_path_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\\\\\") in text


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 13,
        "tags.tsv": 13,
        "xrefs.tsv": 57,
        "instructions.tsv": 1044,
        "decompile/index.tsv": 13,
        "post-metadata.tsv": 13,
        "post-tags.tsv": 13,
        "post-xrefs.tsv": 57,
        "post-instructions.tsv": 1044,
        "post-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require(row.get("comment", "").strip() != "", f"metadata comment missing {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    for address in PRIMARY_TARGETS:
        row = row_by_address(metadata, address)
        require(row is not None, f"primary metadata missing {address}", failures)
        if row:
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token {address}: {token}", failures)
        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"tags missing {address}", failures)
        if tag_row:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            require(COMMON_TAGS.issubset(actual_tags), f"missing Wave992 tags at {address}: {COMMON_TAGS - actual_tags}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    expected_xrefs = (
        ("0x0041b1a0", "0x005e2500", "<no_function>"),
        ("0x0041b370", "0x005e25e4", "<no_function>"),
        ("0x0041b450", "0x005e24e4", "<no_function>"),
        ("0x0041b470", "0x005e25c8", "<no_function>"),
        ("0x0041b590", "0x005e25a4", "<no_function>"),
        ("0x0047c970", "0x0041b3e2", "CCannon__UpdateState"),
        ("0x0047ce80", "0x0041b593", "CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph"),
        ("0x00495230", "0x0041b2fe", "CCannon__Init"),
        ("0x004fd4d0", "0x0041b549", "CCannon__GetMidpoint"),
    )
    for target, source, owner in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == normalize_address(target)
                and normalize_address(row.get("from_addr", "")) == normalize_address(source)
                and row.get("from_function") == owner
                for row in xrefs
            ),
            f"missing xref {source} -> {target} from {owner}",
            failures,
        )


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=7 comment_only_updated=7 tags_added=69 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 comment_only_updated=7 tags_added=69 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "post-xrefs.log": "Wrote 57 rows",
        "post-instructions.log": "targets=13 missing=0",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "Script not found", "BADADDR", "BADNAME", "BADSIG", "BADCOMMENT", "BADTAGS", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"bad log token {relative}: {bad}", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6222, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "queue commentless mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "queue undefined mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "queue param_N mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173837191 or backup.get("totalBytes") == 173837191.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        CANNON_DOC,
        BACKLOG,
        TRACKING_STATE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_path_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-cannon-turret-activation-review-wave992")
        == r"py -3 tools\ghidra_cannon_turret_activation_review_wave992_probe.py --check",
        "missing package script",
        failures,
    )
    require(
        package.get("scripts", {}).get("test:ghidra-wave900-plus-through-wave992-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 992 --check",
        "missing Wave900-Wave992 recheck package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave992 cannon turret activation comment-tag normalization" for row in ledger), "missing Wave992 ledger row", failures)
    require(any(row.get("task") == "Wave992 cannon turret activation comment-tag normalization" and row.get("attempt_id") == 20578 for row in attempts), "missing Wave992 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_exports(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave992 cannon turret activation probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave992 cannon turret activation probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
