#!/usr/bin/env python3
"""Validate Wave1072 OID/target-profile ballistic read-only review artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1072-oid-target-profile-ballistic-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_oid_target_profile_ballistic_review_wave1072_2026-06-02.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1072_recheck_2026-06-02.md"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260602-035902_post_wave1072_oid_target_profile_ballistic_review_verified"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"

TARGETS = {
    "0x00507ab0": ("OID__CanFireAtTarget_BallisticArcA", "int __thiscall OID__CanFireAtTarget_BallisticArcA(void * this, void * target_unit, int ballistic_context)", "monitor-oid-ballistic-wave553", "Wave553"),
    "0x005088b0": ("OID__CanFireAtTarget_BallisticArcB", "int __thiscall OID__CanFireAtTarget_BallisticArcB(void * this, void * target_unit)", "monitor-oid-ballistic-wave553", "Wave553"),
    "0x00509140": ("OID__UpdateAimTransformAndAttachTargetReader", "void __thiscall OID__UpdateAimTransformAndAttachTargetReader(void * this, void * target_reader, void * target_transform)", "monitor-oid-ballistic-wave553", "Wave553"),
    "0x005094b0": ("OID__SolveBallisticPitchToTarget", "double __thiscall OID__SolveBallisticPitchToTarget(void * this, float target_x, float target_y, float target_z, float target_w)", "monitor-oid-ballistic-wave553", "Wave553"),
    "0x005096a0": ("CUnit__ComputeMinBallisticTravelDistance", "double __thiscall CUnit__ComputeMinBallisticTravelDistance(void * this, float target_x, float target_y, float target_z, float target_w)", "monitor-oid-ballistic-wave553", "Wave553"),
    "0x005099a0": ("CUnit__ComputeMaxBallisticTravelDistance", "double __thiscall CUnit__ComputeMaxBallisticTravelDistance(void * this, float target_x, float target_y, float target_z, float target_w)", "monitor-oid-ballistic-wave553", "Wave553"),
    "0x00509c80": ("CBattleEngine__ComputeProjectileMetricFromTargetProfile", "double __thiscall CBattleEngine__ComputeProjectileMetricFromTargetProfile(void * this, float target_x, float target_y, float target_z, float target_w)", "monitor-oid-ballistic-wave553", "Wave553"),
    "0x00509e40": ("TargetSet__GetEntryByIndex", "void * __cdecl TargetSet__GetEntryByIndex(int target_entry_index)", "target-profile-gates-wave554", "Wave554"),
    "0x00509e90": ("ProjectileBurst__ResolvePresetByPercentBucketFallback", "void * __fastcall ProjectileBurst__ResolvePresetByPercentBucketFallback(void * burst_context)", "target-profile-gates-wave554", "Wave554"),
    "0x00509f70": ("TargetProfileContext__IsEligibleByDistanceBucketOrRange", "int __fastcall TargetProfileContext__IsEligibleByDistanceBucketOrRange(void * target_context)", "target-profile-gates-wave554", "Wave554"),
    "0x0050a080": ("TargetProfileContext__CanProceedByTargetRangeGate", "int __fastcall TargetProfileContext__CanProceedByTargetRangeGate(void * target_context)", "target-profile-gates-wave554", "Wave554"),
    "0x0050a0b0": ("CSquadNormal__HasActiveMaskMatchWithTarget", "uint __thiscall CSquadNormal__HasActiveMaskMatchWithTarget(void * this, void * target_unit)", "target-profile-gates-wave554", "Wave554"),
    "0x0050a0d0": ("CUnit__HasMaskBitsA8", "uint __thiscall CUnit__HasMaskBitsA8(void * this, uint mask_bits)", "target-profile-gates-wave554", "Wave554"),
    "0x0050a0e0": ("OID__ComputeForwardProjectedPointTowardTarget", "void __thiscall OID__ComputeForwardProjectedPointTowardTarget(void * this, void * out_point, void * target_unit)", "target-profile-gates-wave554", "Wave554"),
    "0x0050a290": ("CUnit__IsTargetTimeoutBeforeProfileLimit", "int __fastcall CUnit__IsTargetTimeoutBeforeProfileLimit(void * unit)", "target-profile-gates-wave554", "Wave554"),
}

CONTEXT_TARGETS = {
    "0x0040acc0": "CBattleEngine__CalcUnitOverCrossHair",
    "0x0040b120": "CBattleEngine__UpdateAutoAim",
    "0x0040c2e0": "CBattleEngine__CanSpawnBurstForResolvedEntry",
    "0x00411bf0": "CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
    "0x00413cf0": "CBattleEngineWalkerPart__ChargeWeapon",
    "0x00413cc0": "CBattleEngineWalkerPart__FireWeapon",
    "0x004fb500": "CUnit__CanFireAtTarget_BallisticArcA",
    "0x004fb5a0": "CUnit__CanFireAtTarget_BallisticArcB",
    "0x004fb650": "CUnit__ForwardAimTransformAndAttachTargetReader",
    "0x004fb670": "CUnit__ClassifyTargetRangeBand",
    "0x004fd760": "CUnit__HasAnyLinkedUnitBeforeTargetTimeout",
    "0x00506010": "ProjectileBurst__SpawnFromPercentBucketFallback",
    "0x005068f0": "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    "0x00506930": "CWeapon__HandleFireBurstEvent",
    "0x005078b0": "ProjectileBurstPreset__GetListEntryIdByIndex",
    "0x005078f0": "CMonitor__UpdateTrackedRenderPair",
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
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md": (
        "Wave1072",
        "oid-target-profile-ballistic-review-wave1072",
        "0x00509c80 CBattleEngine__ComputeProjectileMetricFromTargetProfile",
        "0x00509e90 ProjectileBurst__ResolvePresetByPercentBucketFallback",
        "1334/1560 = 85.51%",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md": (
        "Wave1072",
        "oid-target-profile-ballistic-review-wave1072",
        "0x005096a0 CUnit__ComputeMinBallisticTravelDistance",
        "0x005099a0 CUnit__ComputeMaxBallisticTravelDistance",
        "0x0050a290 CUnit__IsTargetTimeoutBeforeProfileLimit",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadNormal.cpp" / "_index.md": (
        "Wave1072",
        "oid-target-profile-ballistic-review-wave1072",
        "0x0050a0b0 CSquadNormal__HasActiveMaskMatchWithTarget",
        "0x0050a0d0 CUnit__HasMaskBitsA8",
        BACKUP_PATH,
    ),
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GeneralVolume.cpp" / "_index.md": (
        "Wave1072",
        "oid-target-profile-ballistic-review-wave1072",
        "0x0050a080 TargetProfileContext__CanProceedByTargetRangeGate",
        "0x00411bf0 CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
        BACKUP_PATH,
    ),
}

DOC_TOKENS = (
    "Wave1072",
    "oid-target-profile-ballistic-review-wave1072",
    "0x00507ab0 OID__CanFireAtTarget_BallisticArcA",
    "0x00509c80 CBattleEngine__ComputeProjectileMetricFromTargetProfile",
    "0x00509e90 ProjectileBurst__ResolvePresetByPercentBucketFallback",
    "0x00509f70 TargetProfileContext__IsEligibleByDistanceBucketOrRange",
    "0x0050a0e0 OID__ComputeForwardProjectedPointTowardTarget",
    "812/1408 = 57.67%",
    "1334/1560 = 85.51%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime targeting behavior proven",
    "runtime projectile behavior proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 15,
        "primary-tags.tsv": 15,
        "primary-xrefs.tsv": 40,
        "primary-instructions.tsv": 2997,
        "primary-decompile/index.tsv": 15,
        "context-metadata.tsv": 16,
        "context-xrefs.tsv": 70,
        "context-instructions.tsv": 1769,
        "context-decompile/index.tsv": 16,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    quality = {norm(row["address"]): row for row in read_tsv(QUEUE_TSV)}
    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "primary-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "primary-tags.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "primary-decompile" / "index.tsv")}
    context = {norm(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    xrefs = read_tsv(BASE / "primary-xrefs.tsv")

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
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    expected_xrefs = {
        "0x00507ab0": "0x004fb578",
        "0x005088b0": "0x004fb629",
        "0x00509140": "0x004fb664",
        "0x00509c80": "0x0040ad64",
        "0x00509e90": "0x00506100",
        "0x0050a080": "0x00411c61",
        "0x0050a0e0": "0x00507c9d",
    }
    for target, source in expected_xrefs.items():
        require(
            any(norm(row["target_addr"]) == target and norm(row["from_addr"]) == source for row in xrefs),
            f"missing expected xref {source} -> {target}",
            failures,
        )

    for address, name in CONTEXT_TARGETS.items():
        row = context.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=15 found=15 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "primary-xrefs.log": "Wrote 40 rows",
        "primary-instructions.log": "Wrote 2997 function-body instruction rows",
        "primary-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
        "context-metadata.log": "targets=16 found=16 missing=0",
        "context-xrefs.log": "Wrote 70 rows",
        "context-instructions.log": "Wrote 1769 function-body instruction rows",
        "context-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


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
    require(
        scripts.get("test:ghidra-oid-target-profile-ballistic-review-wave1072")
        == r"py -3 tools\ghidra_oid_target_profile_ballistic_review_wave1072_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1072-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1072 --check",
        "missing aggregate package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1072 OID target/profile ballistic review" for row in ledger), "missing ledger row", failures)
    require(any(row.get("task") == "Wave1072 OID target/profile ballistic review" and row.get("attempt_id") == 20654 for row in attempts), "missing attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_backup_docs(failures)

    if failures:
        print("Wave1072 OID target/profile ballistic review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1072 OID target/profile ballistic review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
