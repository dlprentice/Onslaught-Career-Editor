#!/usr/bin/env python3
"""Validate Wave1217 lifecycle/cleanup tail current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1217-lifecycle-cleanup-tail-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1217-lifecycle-cleanup-tail-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1217-lifecycle-cleanup-tail-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1217_lifecycle_cleanup_tail_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
UNIT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "unit-battleengine-gameplay-static-contract.md"
MESH_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
TREE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "tree.cpp" / "_index.md"
ACTOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Actor.cpp" / "_index.md"
MINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Mine.cpp" / "_index.md"
CARRIER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Carrier.cpp" / "_index.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
RTMESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "rtmesh.cpp" / "_index.md"
WARSPITE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Warspite.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP = r"G:\GhidraBackups\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified"

TARGETS = {
    "0x00421b80": "CCarrierAI__scalar_deleting_dtor",
    "0x004bfce0": "CTree__scalar_deleting_dtor",
    "0x004bfd00": "CActorBase__shared_scalar_deleting_dtor_004bfd00",
    "0x004db8d0": "CRTBuilding__ScalarDeletingDestructor",
    "0x004df520": "CActor__dtor_base_Thunk",
    "0x004f3a70": "CCSPersistentThing__dtor_base",
    "0x004f63c0": "CTree__dtor_base",
    "0x005044f0": "CWarspite__ScalarDeletingDestructor",
    "0x004ba490": "CMine__VFunc02_CleanupLinkedParticleAndForward",
    "0x004ba9d0": "CMine__TryDestroyedResetAndDispatchVFunc1D4",
}

POST_SIGNATURES = {
    "0x00421b80": "void * __thiscall CCarrierAI__scalar_deleting_dtor(void * this, byte flags)",
    "0x004bfce0": "void * __thiscall CTree__scalar_deleting_dtor(void * this, byte flags)",
    "0x004bfd00": "void * __thiscall CActorBase__shared_scalar_deleting_dtor_004bfd00(void * this, byte flags)",
    "0x004db8d0": "void * __thiscall CRTBuilding__ScalarDeletingDestructor(void * this, byte flags)",
    "0x004df520": "void __fastcall CActor__dtor_base_Thunk(void * this)",
    "0x004f3a70": "void __fastcall CCSPersistentThing__dtor_base(void * this)",
    "0x004f63c0": "void __fastcall CTree__dtor_base(void * this)",
    "0x005044f0": "void * __thiscall CWarspite__ScalarDeletingDestructor(void * this, byte delete_flags)",
    "0x004ba490": "void __fastcall CMine__VFunc02_CleanupLinkedParticleAndForward(void * this)",
    "0x004ba9d0": "int __fastcall CMine__TryDestroyedResetAndDispatchVFunc1D4(void * this)",
}

COMMENT_TOKENS = {
    "0x00421b80": ("Wave1217 static current-risk read-back", "CCarrierAI", "0x005d93d8", "CDXMemoryManager__Free"),
    "0x004bfce0": ("Wave1217 static current-risk read-back", "CTree__dtor_base at 0x004f63c0", "stale comment wording"),
    "0x004bfd00": ("Wave1217 static current-risk read-back", "0x005dd5f4", "0x005ded4c", "0x005e45e4", "owner name remains intentionally shared/bounded"),
    "0x004db8d0": ("Wave1217 static current-risk read-back", "CRTBuilding__Destructor", "0x005de9c0"),
    "0x004df520": ("Wave1217 static current-risk read-back", "CActor__dtor_base", "CComplexThing__dtor_base"),
    "0x004f3a70": ("Wave1217 static current-risk read-back", "shuts down monitor state", "CCollisionSeekingRound__Destructor"),
    "0x004f63c0": ("Wave1217 static current-risk read-back", "falling-tree data pointer", "CThing__dtor_base"),
    "0x005044f0": ("Wave1217 static current-risk read-back", "CWarspite__Destructor", "0x005dfbe0"),
    "0x004ba490": ("Wave1217 static current-risk read-back", "ParticleEffectLink__SetHandleStateAndClear", "CUnit__VFunc02_CleanupWorldLinksAndForward"),
    "0x004ba9d0": ("Wave1217 static current-risk read-back", "CGroundUnit__MarkDestroyedAndResetState", "vfunc +0x1d4"),
}

TARGET_XREFS = {
    "0x00421b80": ("005d93d8",),
    "0x004bfce0": ("005dd9dc",),
    "0x004bfd00": ("005dd5f4", "005ded4c", "005e45e4"),
    "0x004db8d0": ("005de9c0",),
    "0x004df520": ("004bfd03",),
    "0x004f3a70": ("004f3a53",),
    "0x004f63c0": ("004bfce3",),
    "0x005044f0": ("005dfbe0",),
    "0x004ba490": ("005e1b8c",),
    "0x004ba9d0": ("005e1c4c",),
}

COMMON_TAGS = (
    "static-reaudit",
    "retail-binary-evidence",
    "current-risk-review",
    "wave1217-lifecycle-cleanup-tail-current-risk-review",
    "wave1217-readback-verified",
    "lifecycle-cleanup-tail",
    "rebuild-grade-static-contract",
)

DOC_TOKENS = (
    "Wave1217",
    "wave1217-lifecycle-cleanup-tail-current-risk-review",
    "10 lifecycle/cleanup tail current-risk rows",
    "1155/1179 = 97.96%",
    "remaining active focused work: 24",
    "1186/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1117",
    "live regenerated current focused candidates: 1117",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "stale CTree destructor-body reference corrected",
    "CCarrierAI tag gap corrected",
    "updated=10 skipped=0",
    "comment_only_updated=10",
    "tags_added=80",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "12 xref rows",
    "137 instruction rows",
    "10 decompile rows",
    "103 context xref rows",
    "681 context instruction rows",
    "14 context decompile rows",
    "29 data-xref rows",
    "CCarrierAI__scalar_deleting_dtor",
    "CTree__scalar_deleting_dtor",
    "CActorBase__shared_scalar_deleting_dtor_004bfd00",
    "CRTBuilding__ScalarDeletingDestructor",
    "CActor__dtor_base_Thunk",
    "CCSPersistentThing__dtor_base",
    "CTree__dtor_base",
    "CWarspite__ScalarDeletingDestructor",
    "CMine__VFunc02_CleanupLinkedParticleAndForward",
    "CMine__TryDestroyedResetAndDispatchVFunc1D4",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "static-reaudit-measurement-register.md",
    "unit-battleengine-gameplay-static-contract.md",
    "mesh-resource-render-static-contract.md",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "continuity denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OWNER_DOC_TOKENS = {
    TREE_DOC: ("Wave1217", "wave1217-lifecycle-cleanup-tail-current-risk-review", "CTree__scalar_deleting_dtor", "CTree__dtor_base", BACKUP),
    ACTOR_DOC: ("Wave1217", "wave1217-lifecycle-cleanup-tail-current-risk-review", "CActorBase__shared_scalar_deleting_dtor_004bfd00", "CActor__dtor_base_Thunk", BACKUP),
    MINE_DOC: ("Wave1217", "wave1217-lifecycle-cleanup-tail-current-risk-review", "CMine__VFunc02_CleanupLinkedParticleAndForward", "CMine__TryDestroyedResetAndDispatchVFunc1D4", BACKUP),
    CARRIER_DOC: ("Wave1217", "wave1217-lifecycle-cleanup-tail-current-risk-review", "CCarrierAI__scalar_deleting_dtor", "CCarrierAI tag gap corrected", BACKUP),
    THING_DOC: ("Wave1217", "wave1217-lifecycle-cleanup-tail-current-risk-review", "CCSPersistentThing__dtor_base", BACKUP),
    RTMESH_DOC: ("Wave1217", "wave1217-lifecycle-cleanup-tail-current-risk-review", "CRTBuilding__ScalarDeletingDestructor", BACKUP),
    WARSPITE_DOC: ("Wave1217", "wave1217-lifecycle-cleanup-tail-current-risk-review", "CWarspite__ScalarDeletingDestructor", BACKUP),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime cleanup behavior proven",
    "exact layout proven",
    "exact source identity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 10,
        "pre-tags.tsv": 10,
        "pre-xrefs.tsv": 12,
        "pre-instructions.tsv": 137,
        "pre-decompile/index.tsv": 10,
        "context-metadata.tsv": 14,
        "context-tags.tsv": 14,
        "context-xrefs.tsv": 103,
        "context-instructions.tsv": 681,
        "context-decompile/index.tsv": 14,
        "data-xrefs.tsv": 29,
        "post-metadata.tsv": 10,
        "post-tags.tsv": 10,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 137,
        "post-decompile/index.tsv": 10,
        "post-context-metadata.tsv": 14,
        "post-context-tags.tsv": 14,
        "post-context-xrefs.tsv": 103,
        "post-context-instructions.tsv": 681,
        "post-context-decompile/index.tsv": 14,
        "post-data-xrefs.tsv": 29,
    }
    for relative, expected in expected_counts.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == expected, f"{relative} row count mismatch: {len(rows)} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs_by_target: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs_by_target.setdefault(normalize_address(row["target_addr"]), set()).add(row["from_addr"].lower())

    for address, name in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata: {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == POST_SIGNATURES[address], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"comment token missing at {address}: {token}", failures)
            for token in ("Static retail Ghidra", "rebuild parity remain separate proof"):
                require(token in comment, f"comment boundary missing at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("name") == name and dec.get("status") == "OK", f"decompile mismatch at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == POST_SIGNATURES[address], f"decompile signature mismatch at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag row mismatch at {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for tag in COMMON_TAGS:
                require(tag in actual, f"missing common tag at {address}: {tag}", failures)
        for from_addr in TARGET_XREFS[address]:
            require(from_addr in xrefs_by_target.get(address, set()), f"missing xref at {address}: {from_addr}", failures)

    tree_comment = metadata["0x004bfce0"]["comment"]
    require("CTree__dtor_base at 0x004f63c0" in tree_comment, "CTree stale comment correction missing", failures)
    require("CTree__scalar_deleting_dtor_004f63c0" not in tree_comment, "stale CTree scalar-deleting callee token remains", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 tags_added=80 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=10 tags_added=80 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=10 found=10 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-xrefs.log": "Wrote 12 rows",
        "post-instructions.log": "Wrote 137 function-body instruction rows",
        "post-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "post-context-metadata.log": "targets=14 found=14 missing=0",
        "post-context-xrefs.log": "Wrote 103 rows",
        "post-context-instructions.log": "Wrote 681 function-body instruction rows",
        "post-context-decompile.log": "targets=14 dumped=14 missing=0 failed=0",
        "post-data-xrefs.log": "Wrote 29 rows",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_accounting_and_docs(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1155, "progress reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "97.96%", "progress percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 24, "progress remaining mismatch", failures)
    require(current["legacyAdditiveReviewedDeprecated"] == 1186, "legacy additive mismatch", failures)
    require(current["duplicateAddressOvercountCorrected"] == 26, "duplicate overcount mismatch", failures)
    require(current["wave1145ArithmeticOvercountCorrected"] == 5, "Wave1145 overcount mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1117, "live focused mismatch", failures)
    require(current["latestReviewTag"] == "wave1217-lifecycle-cleanup-tail-current-risk-review", "latest review tag mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger["correctedUniqueReviewed"] == 1155, "ledger reviewed mismatch", failures)
    require(ledger["correctedUniquePercent"] == "97.96%", "ledger percent mismatch", failures)
    require(ledger["remainingUnique"] == 24, "ledger remaining mismatch", failures)
    require(ledger["countedRowsThroughWave1217"] == 1181, "ledger counted-row mismatch", failures)
    require(ledger["legacyAdditiveThroughWave1217Deprecated"] == 1186, "ledger legacy additive mismatch", failures)

    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        LEDGER,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        MAPPED,
        CAMPAIGN,
        RANK,
        UNIT_CONTRACT,
        MESH_CONTRACT,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave note mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1217-lifecycle-cleanup-tail-current-risk-review")
        == r"py -3 tools\wave1217_lifecycle_cleanup_tail_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_accounting_and_docs(failures)

    if failures:
        print("Wave1217 lifecycle/cleanup tail current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1217 lifecycle/cleanup tail current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
