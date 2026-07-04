#!/usr/bin/env python3
"""Validate Wave1133 feature/pickup current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1133-feature-pickup-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1133-feature-pickup-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1133-feature-pickup-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1133_feature_pickup_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DESTROYABLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DestructableSegmentsController.cpp" / "_index.md"
FEATURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Feature.cpp" / "_index.md"
GENERAL_VOLUME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GeneralVolume.cpp" / "_index.md"
UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-093432_post_wave1132_component_ai_current_risk_review_verified"

TARGETS = {
    "0x00442710": (
        "CDestroyableSegment__SpawnConfiguredPickup",
        "int __fastcall CDestroyableSegment__SpawnConfiguredPickup(void * this)",
        ("this+0x3c", "config+0xe8", "CExplosionInitThing"),
        (
            ("0x00442f22", "CDestroyableSegment__VFunc_09_UpdatePickupAndChildSlot09", "UNCONDITIONAL_CALL"),
            ("0x004431eb", "CDestroyableSegment__VFunc_10_SpawnRubbleEffects", "UNCONDITIONAL_CALL"),
            ("0x00443d1a", "CDestroyableEndSegment__VFunc_10_SpawnEndRubbleEffects", "UNCONDITIONAL_CALL"),
        ),
        ("CWorldPhysicsManager__CreatePickup", "DAT_008553f8", "0xe8"),
        ("destructable-segment-wave348", "pickup", "retail-binary-evidence"),
    ),
    "0x0044ca30": (
        "CFeature__Init",
        "void __thiscall CFeature__Init(void * this, void * init)",
        ("init+0x3bc", "CActor__Init", "random sample"),
        (("0x005e4604", "<no_function>", "DATA"),),
        ("0x3bc", "0xe4", "0xec"),
        ("feature", "init", "signature-hardened"),
    ),
    "0x0044cbe0": (
        "CFeature__ShutdownAndRemoveFromWorld",
        "void __fastcall CFeature__ShutdownAndRemoveFromWorld(void * feature)",
        ("KillSamplesForThing", "RemoveUnitFromOccupancyGrid", "UpdateVisibility"),
        (("0x005e45e8", "<no_function>", "DATA"),),
        ("CSoundManager__KillSamplesForThing", "CWorld__RemoveUnitFromOccupancyGrid_Thunk", "CStaticShadows__UpdateVisibility"),
        ("feature", "shutdown", "signature-hardened"),
    ),
    "0x0044cee0": (
        "CFeature__MaybeSpawnRandomPickupFromData",
        "void __fastcall CFeature__MaybeSpawnRandomPickupFromData(void * feature)",
        ("feature data", "DAT_008553f8", "owner inferred"),
        (("0x0044ccf1", "<no_function>", "UNCONDITIONAL_CALL"),),
        ("CWorldPhysicsManager__CreatePickup", "DAT_008553f8", "0xe4"),
        ("feature", "pickup-spawn", "signature-hardened"),
    ),
    "0x0044e300": (
        "PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300",
        "void __fastcall PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300(void * object)",
        ("Owner-neutral", "+0x164", "attached frame"),
        (
            ("0x0044e28e", "<no_function>", "UNCONDITIONAL_CALL"),
            ("0x0044e536", "PickupSpawn__UpdateAttachedPickupBurst_0044e4e0", "UNCONDITIONAL_CALL"),
        ),
        ("CWorldPhysicsManager__CreatePickup", "DAT_008553f8", "0xec"),
        ("owner-deferred", "pickup-spawn", "signature-hardened"),
    ),
    "0x004fd230": (
        "CUnit__SpawnProfileDropPickup",
        "void __fastcall CUnit__SpawnProfileDropPickup(void * this)",
        ("AirUnit", "this+0x164", "HeightDelta__Below025_D0"),
        (
            ("0x00403750", "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport", "UNCONDITIONAL_CALL"),
            ("0x0040378a", "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes", "UNCONDITIONAL_CALL"),
            ("0x004fd0dd", "CUnit__ResetDeploymentGraphAndScheduleEvent", "UNCONDITIONAL_CALL"),
        ),
        ("CWorldPhysicsManager__CreatePickup", "HeightDelta__Below025_D0", "0xe8"),
        ("unit-pickup", "unit-support-tail-wave540", "signature-corrected"),
    ),
}

CONTEXT_TARGETS = {
    "0x0040dfb0": (
        "CGeneralVolume__SpawnPickupAndDispatch",
        "void __thiscall CGeneralVolume__SpawnPickupAndDispatch(void * this)",
    ),
    "0x004ef100": (
        "CUnit__VFunc64_SpawnConfiguredPickupThreeTimes",
        "void __fastcall CUnit__VFunc64_SpawnConfiguredPickupThreeTimes(void * this)",
    ),
}

DOC_TOKENS = (
    "Wave1133",
    "wave1133-feature-pickup-current-risk-review",
    "184/1179 = 15.61%",
    "6 rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 995",
    "feature/pickup spawn bridge cluster",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime pickup behavior proven",
    "runtime feature behavior proven",
    "runtime drop behavior proven",
    "rebuild parity proven",
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_wave1108_accounting(failures: list[str]) -> None:
    counts = wave1108_current_risk_rank.generate()
    require(counts["total"] == 6410, "Wave1108 total mismatch", failures)
    require(counts["risk"] == 6165, "Wave1108 risk mismatch", failures)
    require(counts["focused"] == 1178, "Wave1108 focused mismatch", failures)
    focused = {normalize_address(row["address"]): row for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused, f"target missing from current focused TSV: {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "pre-xrefs.log": "Wrote 22 rows",
        "pre-instructions.log": "Wrote 681 function-body instruction rows",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=2 found=2 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "context-xrefs.log": "Wrote 4 rows",
        "context-instructions.log": "Wrote 180 function-body instruction rows",
        "context-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_MISSING", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 22,
        "pre-instructions.tsv": 681,
        "pre-decompile/index.tsv": 6,
        "context-metadata.tsv": 2,
        "context-tags.tsv": 2,
        "context-xrefs.tsv": 4,
        "context-instructions.tsv": 180,
        "context-decompile/index.tsv": 2,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature, comment_tokens, xref_specs, decompile_tokens, tag_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch for {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch for {address}", failures)
            comment = row.get("comment", "").lower()
            for token in comment_tokens:
                require(token.lower() in comment, f"missing comment token for {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in tag_tokens:
                require(token in actual, f"missing tag for {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"decompile mismatch for {address}", failures)
        decompile_text = read_text(BASE / "pre-decompile" / f"{address[2:]}_{name}.c")
        for token in decompile_tokens:
            require(token in decompile_text, f"missing decompile token for {address}: {token}", failures)

        for from_addr, from_function, ref_type in xref_specs:
            require(
                any(
                    normalize_address(row.get("target_addr", "")) == address
                    and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                    and row.get("from_function") == from_function
                    and row.get("ref_type") == ref_type
                    for row in xrefs
                ),
                f"missing xref for {address}: {(from_addr, from_function, ref_type)}",
                failures,
            )


def check_context_rows(failures: list[str]) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "context-decompile" / "index.tsv")}
    for address, (name, signature) in CONTEXT_TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing context metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch for {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch for {address}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature and dec.get("status") == "OK", f"context decompile mismatch for {address}", failures)


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    address_tokens = tuple(f"{address} {target[0]}" for address, target in TARGETS.items())
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS + address_tokens:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad.lower() not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        DESTROYABLE_DOC: ("Wave1133", "wave1133-feature-pickup-current-risk-review", "0x00442710 CDestroyableSegment__SpawnConfiguredPickup", BACKUP),
        FEATURE_DOC: (
            "Wave1133",
            "wave1133-feature-pickup-current-risk-review",
            "0x0044ca30 CFeature__Init",
            "0x0044cbe0 CFeature__ShutdownAndRemoveFromWorld",
            "0x0044cee0 CFeature__MaybeSpawnRandomPickupFromData",
            "0x0044e300 PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300",
            BACKUP,
        ),
        GENERAL_VOLUME_DOC: ("Wave1133", "0x0040dfb0 CGeneralVolume__SpawnPickupAndDispatch", "context", BACKUP),
        UNIT_DOC: ("Wave1133", "0x004fd230 CUnit__SpawnProfileDropPickup", "0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes", BACKUP),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1133 Feature/Pickup current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1133-feature-pickup-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        artifact_commit = data["latestWave"].get("artifactCommit")
        require(
            artifact_commit == "pending Wave1133 artifact commit" or bool(re.fullmatch(r"[0-9a-f]{40}", str(artifact_commit or ""))),
            f"{label} artifact commit mismatch",
            failures,
        )
        require(current["focusedReviewed"] == 184, f"{label} focused reviewed mismatch", failures)
        require(current["focusedCandidates"] == 1179, f"{label} focused denominator mismatch", failures)
        require(current["focusedReviewedPercent"] == "15.61%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1133-feature-pickup-current-risk-review", f"{label} review tag mismatch", failures)
        require(current.get("liveFocusedCandidatesAfterLatestReview") == 1178, f"{label} live focused count mismatch", failures)
        require(current.get("remainingFocusedAfterLatestReview") == 995, f"{label} remaining focused count mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1133_feature_pickup_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1133-feature-pickup-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_accounting(failures)
    check_logs(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_context_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1133 feature/pickup current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1133 feature/pickup current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
