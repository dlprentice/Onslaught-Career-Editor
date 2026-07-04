#!/usr/bin/env python3
"""Validate Wave1076 CInfantryUnit lifecycle boundary read-back artifacts."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1076-infantryunit-lifecycle-review"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-065500_post_wave1076_infantryunit_lifecycle_boundary_verified"

TARGETS = {
    "0x00488f10": {
        "name": "CInfantryUnit__VFunc38_HandleHitOrDispatchHit",
        "signature": "void __thiscall CInfantryUnit__VFunc38_HandleHitOrDispatchHit(void * this, void * otherThing, void * collisionReport)",
        "slot": "38",
        "slot_addr": "0x005e27c8",
        "end": "0x00488f5c",
        "next": "0x00488f60",
        "tokens": ("slot 38", "CThing__CreateHitRefEvaluateImpulseAndDispatchHit", "0x00488f5c", "separate proof"),
    },
    "0x00488f80": {
        "name": "CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius",
        "signature": "void __thiscall CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius(void * this, void * collisionOwner)",
        "slot": "34",
        "slot_addr": "0x005e27b8",
        "end": "0x0048902f",
        "next": "0x00489040",
        "tokens": ("slot 34", "CGroundUnit__CreateCollisionSphere", "0x0062d4a8", "separate proof"),
    },
    "0x00489090": {
        "name": "CInfantryUnit__VFunc59_SelectAnimationMode",
        "signature": "int __thiscall CInfantryUnit__VFunc59_SelectAnimationMode(void * this, int requestedMode, int resetFrame, int forceLooped)",
        "slot": "59",
        "slot_addr": "0x005e281c",
        "end": "0x004892af",
        "next": "0x004892c0",
        "tokens": ("slot 59", "CComplexThing__SetAnimMode", "CMesh__FindAnimationIndexByName", "separate proof"),
    },
    "0x004892c0": {
        "name": "CInfantryUnit__VFunc65_UpdateMotionAnimationState",
        "signature": "void __fastcall CInfantryUnit__VFunc65_UpdateMotionAnimationState(void * this)",
        "slot": "65",
        "slot_addr": "0x005e2834",
        "end": "0x0048964d",
        "next": "0x00489650",
        "tokens": ("slot 65", "CGroundUnit__UpdateLinkedEffectsByHeightClearance", "CStaticShadows__SampleShadowHeightBilinear", "separate proof"),
    },
    "0x00489650": {
        "name": "CInfantryUnit__VFunc39_HandleCollisionDamageReaction",
        "signature": "void __thiscall CInfantryUnit__VFunc39_HandleCollisionDamageReaction(void * this, void * collisionContext, void * otherThing, void * impactContext, void * damageContext)",
        "slot": "39",
        "slot_addr": "0x005e27cc",
        "end": "0x00489b36",
        "next": "0x00489b40",
        "tokens": ("slot 39", "CUnit__ApplyDamage", "CRound__GetPresetScalarByConfigName", "separate proof"),
    },
    "0x00489b40": {
        "name": "CInfantryUnit__VFunc49_HandleDeathPickupAndEffects",
        "signature": "int __fastcall CInfantryUnit__VFunc49_HandleDeathPickupAndEffects(void * this)",
        "slot": "49",
        "slot_addr": "0x005e27f4",
        "end": "0x00489dde",
        "next": "0x00489de0",
        "tokens": ("slot 49", "CWorldPhysicsManager__CreatePickup", "CParticleManager__CreateEffect", "separate proof"),
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "infantryunit-lifecycle-boundary-wave1076",
    "wave1076-readback-verified",
    "retail-binary-evidence",
    "function-boundary-recovered",
    "cinfantryunit",
    "vtable-slot",
    "signature-hardened",
    "comment-hardened",
}

CORE_DOCS = [
    ROOT / "README.md",
    ROOT / "CURRENT_CAPABILITIES.md",
    ROOT / "release" / "readiness" / "ghidra_infantryunit_lifecycle_boundary_wave1076_2026-06-02.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
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

DOC_TOKENS = (
    "Wave1076",
    "infantryunit-lifecycle-boundary-wave1076",
    "0x00488f10 CInfantryUnit__VFunc38_HandleHitOrDispatchHit",
    "0x00488f80 CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius",
    "0x00489090 CInfantryUnit__VFunc59_SelectAnimationMode",
    "0x004892c0 CInfantryUnit__VFunc65_UpdateMotionAnimationState",
    "0x00489650 CInfantryUnit__VFunc39_HandleCollisionDamageReaction",
    "0x00489b40 CInfantryUnit__VFunc49_HandleDeathPickupAndEffects",
    "0x005e2730",
    "0x005e27b8",
    "0x005e27c8",
    "0x005e27cc",
    "0x005e27f4",
    "0x005e281c",
    "0x005e2834",
    "812/1408 = 57.67%",
    "1365/1560 = 87.50%",
    "500/500 = 100.00%",
    "6254/6254 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime infantry behavior proven",
    "exact source virtual name proven",
    "exact source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
    "all systems complete",
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
    return sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 10,
        "tags.tsv": 10,
        "xrefs.tsv": 12,
        "instructions.tsv": 281,
        "decompile/index.tsv": 10,
        "context-metadata.tsv": 15,
        "context-instructions.tsv": 701,
        "context-decompile/index.tsv": 15,
        "vtable-slots.tsv": 384,
        "candidate-diagnose.tsv": 6,
        "candidate-metadata.tsv": 6,
        "candidate-xrefs.tsv": 6,
        "candidate-instructions.tsv": 1014,
        "candidate-instructions-wide.tsv": 2214,
        "candidate-decompile/index.tsv": 6,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 6,
        "post-instructions.tsv": 1121,
        "post-decompile/index.tsv": 6,
        "post-vtable-slots.tsv": 96,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    diagnose = {norm(row["address"]): row for row in read_tsv(BASE / "candidate-diagnose.tsv")}
    candidate_meta = {norm(row["address"]): row for row in read_tsv(BASE / "candidate-metadata.tsv")}
    candidate_xrefs = {norm(row["target_addr"]): row for row in read_tsv(BASE / "candidate-xrefs.tsv")}
    post_meta = {norm(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    post_tags = {norm(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    post_xrefs = {norm(row["target_addr"]): row for row in read_tsv(BASE / "post-xrefs.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    vtable_slots = read_tsv(BASE / "post-vtable-slots.tsv")
    vtable_by_slot = {row["slot_index"]: row for row in vtable_slots}

    for address, spec in TARGETS.items():
        require(diagnose.get(address, {}).get("status") == "INSTRUCTION_NO_FUNCTION", f"candidate diagnose mismatch at {address}", failures)
        require(candidate_meta.get(address, {}).get("status") == "MISSING", f"candidate metadata should be missing at {address}", failures)
        xref = candidate_xrefs.get(address)
        require(xref is not None, f"missing candidate xref at {address}", failures)
        if xref is not None:
            require(norm(xref.get("from_addr", "")) == spec["slot_addr"], f"candidate xref slot mismatch at {address}", failures)
            require(xref.get("ref_type") == "DATA", f"candidate xref type mismatch at {address}", failures)

        row = post_meta.get(address)
        require(row is not None, f"missing post metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == spec["name"], f"post name mismatch at {address}", failures)
            require(row.get("signature") == spec["signature"], f"post signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"post metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in ("Wave1076 boundary recovery", "0x005e2730", spec["slot_addr"], spec["next"], *spec["tokens"]):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tags = set(post_tags.get(address, {}).get("tags", "").split(";"))
        require(COMMON_TAGS.issubset(tags), f"post tags missing at {address}: {COMMON_TAGS - tags}", failures)

        post_xref = post_xrefs.get(address)
        require(post_xref is not None, f"missing post xref at {address}", failures)
        if post_xref is not None:
            require(norm(post_xref.get("from_addr", "")) == spec["slot_addr"], f"post xref slot mismatch at {address}", failures)
            require(post_xref.get("ref_type") == "DATA", f"post xref type mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing post decompile at {address}", failures)
        if dec is not None:
            require(dec.get("name") == spec["name"], f"post decompile name mismatch at {address}", failures)
            require(dec.get("signature") == spec["signature"], f"post decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"post decompile status mismatch at {address}", failures)

        slot = vtable_by_slot.get(spec["slot"])
        require(slot is not None, f"missing vtable slot {spec['slot']}", failures)
        if slot is not None:
            require(norm(slot.get("slot_addr", "")) == spec["slot_addr"], f"vtable slot address mismatch at {address}", failures)
            require(norm(slot.get("pointer_addr", "")) == address, f"vtable pointer mismatch at {address}", failures)
            require(slot.get("function_name") == spec["name"], f"vtable function name mismatch at {address}", failures)
            require(slot.get("status") == "OK", f"vtable status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=6 skipped=0 created=0 would_create=6 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=6 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 created=6 would_create=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 6 rows",
        "post-instructions.log": "Wrote 1121 function-body instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-vtable-slots.log": "ExportVtableSlots complete: targets=1 rows=96",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "FAIL:", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6254, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    by_address = {norm(row["address"]): row for row in rows}
    require(len(rows) == 6254, "quality TSV row count mismatch", failures)
    require(strict_clean_count(rows) == 6254, "strict clean count mismatch", failures)
    for address, spec in TARGETS.items():
        require(by_address.get(address, {}).get("name") == spec["name"], f"quality name mismatch at {address}", failures)
        require(by_address.get(address, {}).get("signature") == spec["signature"], f"quality signature mismatch at {address}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174754695 or backup.get("totalBytes") == 174754695.0, "backup bytes mismatch", failures)
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

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:ghidra-infantryunit-lifecycle-boundary-wave1076") == r"py -3 tools\ghidra_infantryunit_lifecycle_boundary_wave1076_probe.py --check", "missing focused package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1076-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1076 --check", "missing aggregate package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1076 InfantryUnit lifecycle boundary" for row in ledger_rows), "missing Wave1076 ledger row", failures)
    require(any(row.get("task") == "Wave1076 InfantryUnit lifecycle boundary" and row.get("attempt_id") == 20658 for row in attempts), "missing Wave1076 attempt row", failures)


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
        print("Wave1076 InfantryUnit lifecycle boundary probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1076 InfantryUnit lifecycle boundary probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
