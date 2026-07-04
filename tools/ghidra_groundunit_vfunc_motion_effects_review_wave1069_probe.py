#!/usr/bin/env python3
"""Validate Wave1069 ground-unit/vfunc motion-effects read-only artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1069-groundunit-vfunc-motion-effects-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_groundunit_vfunc_motion_effects_review_wave1069_2026-06-02.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1069_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260602-013945_post_wave1069_groundunit_vfunc_motion_effects_review_verified"
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
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Mech.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Mine.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

TARGETS = {
    "0x0049c1d0": ("CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0", "void __thiscall CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0(void * this, void * mesh_part, void * out_value)"),
    "0x0049c440": ("CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440", "void __thiscall CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440(void * this, void * mesh_part, void * transform_a, void * transform_b, int context_value)"),
    "0x0049f820": ("SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820", "void __thiscall SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820(void * this, void * init_context)"),
    "0x0049fc10": ("SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10", "void __fastcall SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10(void * this)"),
    "0x0049fdb0": ("SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0", "void __fastcall SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0(void * this)"),
    "0x004ba490": ("CMine__VFunc02_CleanupLinkedParticleAndForward", "void __fastcall CMine__VFunc02_CleanupLinkedParticleAndForward(void * this)"),
    "0x004ba9d0": ("CMine__TryDestroyedResetAndDispatchVFunc1D4", "int __fastcall CMine__TryDestroyedResetAndDispatchVFunc1D4(void * this)"),
    "0x004d3630": ("CPod__VFunc_66_UpdateMotionAndAccumulateScalar", "void __fastcall CPod__VFunc_66_UpdateMotionAndAccumulateScalar(void * this)"),
}

COMMENT_TOKENS = {
    "0x0049c1d0": ("Wave433", "CMCMech vtable 0x005dc3b4 slot 5", "CMCMech__Reset", "out_value"),
    "0x0049c440": ("Wave434", "CMCMine vtable 0x005dc3f4 slot 4", "owner +0x250/+0x254"),
    "0x0049f820": ("Wave436", "CGroundUnit__Init", "vtable slots 117/118/119", "CDestroyableSegment__FindChildByNameI"),
    "0x0049fc10": ("Wave437", "slot 66", "optionally creates a pickup", "CGroundUnit__UpdateLinkedEffectsByHeightClearance"),
    "0x0049fdb0": ("Wave437", "slot 71", "Generic Mesh", "CMCMech__BuildInterpolatedPoseAndAnchor"),
    "0x004ba490": ("Wave477", "ParticleEffectLink__SetHandleStateAndClear", "VFuncSlot_02_004f95d0"),
    "0x004ba9d0": ("Wave456", "CGroundUnit__MarkDestroyedAndResetState", "vfunc +0x1d4"),
    "0x004d3630": ("Wave486", "CPOD RTTI", "CUnit__UpdateMotionAttachmentsAndEffects", "this+0x84"),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence", "signature-corrected", "comment-hardened"}

EXPECTED_TAGS = {
    "0x0049c1d0": COMMON_TAGS | {"cmcmech", "vtable-slot", "bone-value"},
    "0x0049c440": COMMON_TAGS | {"cmcmine", "vtable-slot", "height-cache"},
    "0x0049f820": COMMON_TAGS | {"shared-ground-unit", "vtable-slot", "vtable-readback"},
    "0x0049fc10": COMMON_TAGS | {"shared-ground-unit", "vtable-slot-66", "vtable-readback"},
    "0x0049fdb0": COMMON_TAGS | {"shared-ground-unit", "vtable-slot-71", "mesh-effects"},
    "0x004ba490": COMMON_TAGS | {"mine", "cleanup"},
    "0x004ba9d0": COMMON_TAGS | {"mine", "groundunit"},
    "0x004d3630": COMMON_TAGS | {"cpod", "motion", "vfunc-slot-66"},
}

EXPECTED_XREFS = {
    ("0x0049c1d0", "0x005dc3c8", "DATA"),
    ("0x0049c440", "0x005dc404", "DATA"),
    ("0x0049f820", "0x004799fa", "UNCONDITIONAL_CALL"),
    ("0x0049f820", "0x005e06a8", "DATA"),
    ("0x0049f820", "0x005e3098", "DATA"),
    ("0x0049fc10", "0x00479d4e", "UNCONDITIONAL_CALL"),
    ("0x0049fc10", "0x004f492c", "UNCONDITIONAL_CALL"),
    ("0x0049fdb0", "0x005e07a0", "DATA"),
    ("0x0049fdb0", "0x005e0c4c", "DATA"),
    ("0x0049fdb0", "0x005e10fc", "DATA"),
    ("0x0049fdb0", "0x005e3190", "DATA"),
    ("0x004ba490", "0x005e1b8c", "DATA"),
    ("0x004ba9d0", "0x005e1c4c", "DATA"),
    ("0x004d3630", "0x005e0094", "DATA"),
}

EXPECTED_CALLERS = {
    "0x004799c0": "CGillM__VFunc09_InitGroundedSpawnState",
    "0x00479d10": "CGillM__UpdateGroundedVerticalDrift",
    "0x004f4920": "ProjectileBurstCallerBoundary_004f4920",
}

EXPECTED_VTABLE = {
    ("005dc3b4", "5", "0049c1d0", "CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0", "OK"),
    ("005dc3f4", "4", "0049c440", "CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440", "OK"),
    ("005e0684", "9", "0049f820", "SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820", "OK"),
    ("005e0684", "66", "0049fc10", "SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10", "OK"),
    ("005e0684", "71", "0049fdb0", "SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0", "OK"),
    ("005e3074", "9", "0049f820", "SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820", "OK"),
    ("005e3074", "66", "0049fc10", "SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10", "OK"),
    ("005e3074", "71", "0049fdb0", "SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0", "OK"),
    ("005e0fe0", "71", "0049fdb0", "SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0", "OK"),
    ("005e0b30", "71", "0049fdb0", "SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0", "OK"),
    ("005e1b84", "2", "004ba490", "CMine__VFunc02_CleanupLinkedParticleAndForward", "OK"),
    ("005e1b84", "50", "004ba9d0", "CMine__TryDestroyedResetAndDispatchVFunc1D4", "OK"),
    ("005dff8c", "66", "004d3630", "CPod__VFunc_66_UpdateMotionAndAccumulateScalar", "OK"),
}

CONTEXT_MISSING = {
    "0x0049bdc0", "0x0049c200", "0x0049c430", "0x0049f760", "0x0049f780",
    "0x0049f890", "0x0049fb70", "0x0049fd70", "0x004a0030", "0x004ba3f0",
    "0x004baac0", "0x004d3440", "0x004d38b0",
}

DOC_TOKENS = (
    "Wave1069",
    "groundunit-vfunc-motion-effects-review-wave1069",
    "0x0049c1d0 CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0",
    "0x0049c440 CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440",
    "0x0049f820 SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820",
    "0x0049fc10 SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10",
    "0x0049fdb0 SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0",
    "0x004ba490 CMine__VFunc02_CleanupLinkedParticleAndForward",
    "0x004ba9d0 CMine__TryDestroyedResetAndDispatchVFunc1D4",
    "0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar",
    "812/1408 = 57.67%",
    "1266/1560 = 81.15%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime mine behavior proven",
    "exact source identity proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 8,
        "primary-tags.tsv": 8,
        "primary-xrefs.tsv": 22,
        "primary-instructions.tsv": 498,
        "primary-decompile/index.tsv": 8,
        "caller-metadata.tsv": 3,
        "caller-instructions.tsv": 362,
        "caller-decompile/index.tsv": 3,
        "context-metadata.tsv": 13,
        "vtable.tsv": 1024,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "primary-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "primary-tags.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "primary-decompile" / "index.tsv")}
    xrefs = {
        (norm(row["target_addr"]), norm(row["from_addr"]), row["ref_type"])
        for row in read_tsv(BASE / "primary-xrefs.tsv")
    }

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            expected = EXPECTED_TAGS[address]
            require(expected.issubset(actual), f"tags missing at {address}: {expected - actual}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    for expected in EXPECTED_XREFS:
        require(expected in xrefs, f"missing xref tuple: {expected}", failures)

    callers = {norm(row["address"]): row for row in read_tsv(BASE / "caller-metadata.tsv")}
    for address, name in EXPECTED_CALLERS.items():
        row = callers.get(address)
        require(row is not None, f"missing caller metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"caller name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"caller status mismatch at {address}", failures)

    context = {norm(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    missing = {address for address, row in context.items() if row.get("status") == "MISSING"}
    require(missing == CONTEXT_MISSING, f"context missing set mismatch: {missing}", failures)

    vtable = {
        (row["vtable"], row["slot_index"], row["pointer_addr"], row["function_name"], row["status"])
        for row in read_tsv(BASE / "vtable.tsv")
    }
    for expected in EXPECTED_VTABLE:
        require(expected in vtable, f"missing vtable tuple: {expected}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=8 found=8 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "primary-xrefs.log": "Wrote 22 rows",
        "primary-instructions.log": "targets=8 missing=0",
        "primary-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "caller-metadata.log": "targets=3 found=3 missing=0",
        "caller-instructions.log": "targets=3 missing=0",
        "caller-decompile.log": "targets=3 dumped=3 missing=0 failed=0",
        "context-metadata.log": "targets=13 found=0 missing=13",
        "vtable.log": "ExportVtableSlots complete: targets=8 rows=1024",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        bad_tokens = ("LockException", "BADADDR", "BADNAME", "FAIL:", "failed=1", "bad=1")
        for bad in bad_tokens:
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
        if relative != "context-metadata.log":
            require("missing=1" not in text, f"unexpected missing token in {relative}: missing=1", failures)


def check_queue_backup_docs(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(float(backup.get("totalBytes")) == 174721927.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-groundunit-vfunc-motion-effects-review-wave1069")
        == r"py -3 tools\ghidra_groundunit_vfunc_motion_effects_review_wave1069_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1069-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1069 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1069 groundunit vfunc motion effects review" for row in ledger), "missing ledger row", failures)
    require(any(row.get("task") == "Wave1069 groundunit vfunc motion effects review" and row.get("attempt_id") == 20651 for row in attempts), "missing attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_backup_docs(failures)

    if failures:
        print("Wave1069 ground-unit/vfunc motion-effects review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1069 ground-unit/vfunc motion-effects review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
