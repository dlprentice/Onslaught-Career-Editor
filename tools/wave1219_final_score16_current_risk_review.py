#!/usr/bin/env python3
"""Validate Wave1219 final score16 current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1219-final-score16-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1219-final-score16-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1219-final-score16-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1219_final_score16_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GENERAL_VOLUME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GeneralVolume.cpp" / "_index.md"
BOAT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Boat.cpp" / "_index.md"
PCPLATFORM_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCPlatform.cpp" / "_index.md"
END_LEVEL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "EndLevelData.cpp" / "_index.md"
HLCOLLISION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HLCollisionDetector.cpp" / "_index.md"
OGG_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "OggLoader.cpp" / "_index.md"
PLANE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Plane.cpp" / "_index.md"
SENTINEL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Sentinel.cpp" / "_index.md"
GILLMHEAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GillMHead.cpp" / "_index.md"
LTSHELL_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ltshell.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified"

TARGETS = {
    "0x004098e0": ("CLine__ctor_copy", "void __thiscall CLine__ctor_copy(void * this, void * sourceLine)", ("CGeneralVolume", "CLine")),
    "0x00414e50": ("CBoat__Init", "void __thiscall CBoat__Init(void * this, void * init)", ("CGroundUnit__Init", "CBoatGuide")),
    "0x00415d70": ("CBoatGuide__ctor", "void * __thiscall CBoatGuide__ctor(void * this, void * guideOwner)", ("CGuide__ctor_base", "0x005d8d5c")),
    "0x00423650": ("CFrameTimer__ctor", "void * __fastcall CFrameTimer__ctor(void * this)", ("performance-counter", "frequency")),
    "0x004422d0": ("CDebugMarker__ctor", "void * __fastcall CDebugMarker__ctor(void * this)", ("debug-marker", "DAT_0066ffb0")),
    "0x004496e0": ("CEndLevelData__IsAllSecondaryObjectivesComplete", "bool __fastcall CEndLevelData__IsAllSecondaryObjectivesComplete(void * this)", ("secondary objectives", "ERROR: No secondary objectives")),
    "0x00488ef0": ("CCollisionSeekingThing__ctor_base", "void __fastcall CCollisionSeekingThing__ctor_base(void * this)", ("0x005d9608", "constructor-base")),
    "0x00488f00": ("CHLCollisionDetector__ctor_base", "void __fastcall CHLCollisionDetector__ctor_base(void * this)", ("0x005dbf78", "constructor-base")),
    "0x004b6cd0": ("COggLoader__readerSubobject_dtor_body", "void __fastcall COggLoader__readerSubobject_dtor_body(void * reader_subobject)", ("COggFileRead", "CWaitingThread")),
    "0x004b6d30": ("COggLoader__ctor_base", "void * __fastcall COggLoader__ctor_base(void * this)", ("COggFileRead", "CWaitingThread")),
    "0x004d1f10": ("CPlane__Hit_CheckFatalDamageAndDie", "void __thiscall CPlane__Hit_CheckFatalDamageAndDie(void * this, void * hit_thing, void * hit_context)", ("fatal", "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000")),
    "0x004dea50": ("CSentinel__Init", "void __thiscall CSentinel__Init(void * this, void * init_data)", ("CGroundUnit__Init", "CMCSentinel")),
    "0x004f4530": ("SharedUnitAnimation__FindAnimationIndexOrZero", "int __thiscall SharedUnitAnimation__FindAnimationIndexOrZero(void * this, void * animation_name)", ("FindAnimationIndex", "BattleEngine")),
    "0x004f4560": ("SharedUnitAnimation__PlayAnimationByNameIfPresent", "void __thiscall SharedUnitAnimation__PlayAnimationByNameIfPresent(void * this, void * animation_name, int play_flag, int reset_flag)", ("animation", "vfunc +0xf0")),
    "0x00512670": ("PCLTShell__ctor", "void * __thiscall PCLTShell__ctor(void * this)", ("Battle Engine Aquila", "PCLTShell")),
    "0x005245e0": ("COggFileRead__scalar_deleting_dtor", "void * __thiscall COggFileRead__scalar_deleting_dtor(void * this, byte flags)", ("COggFileRead__dtor_body", "flags")),
}

COMMON_TAGS = {
    "static-reaudit",
    "retail-binary-evidence",
    "current-risk-review",
    "wave1219-final-score16-current-risk-review",
    "wave1219-readback-verified",
    "final-score16-tail",
    "rebuild-grade-static-contract",
}

DOC_TOKENS = (
    "Wave1219",
    "wave1219-final-score16-current-risk-review",
    "1179/1179 = 100.00%",
    "16 final score16 current-risk rows",
    "remaining active focused work: 0",
    "1210/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1117",
    "live regenerated current focused candidates: 1117",
    "current risk candidates: 6166",
    "tag-only normalization",
    "updated=16 skipped=0",
    "tags_added=84",
    "final dry updated=0 skipped=16",
    "no rename",
    "no signature change",
    "no comment change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "44 xref rows",
    "539 instruction rows",
    "16 decompile rows",
    "CLine__ctor_copy",
    "CBoat__Init",
    "CFrameTimer__ctor",
    "CEndLevelData__IsAllSecondaryObjectivesComplete",
    "COggLoader__ctor_base",
    "CPlane__Hit_CheckFatalDamageAndDie",
    "CSentinel__Init",
    "SharedUnitAnimation__PlayAnimationByNameIfPresent",
    "PCLTShell__ctor",
    "COggFileRead__scalar_deleting_dtor",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "static-reaudit-measurement-register.md",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "continuity denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OWNER_DOC_TOKENS = {
    GENERAL_VOLUME_DOC: ("Wave1219", "CLine__ctor_copy", BACKUP),
    BOAT_DOC: ("Wave1219", "CBoat__Init", "CBoatGuide__ctor", BACKUP),
    PCPLATFORM_DOC: ("Wave1219", "CFrameTimer__ctor", BACKUP),
    END_LEVEL_DOC: ("Wave1219", "CEndLevelData__IsAllSecondaryObjectivesComplete", BACKUP),
    HLCOLLISION_DOC: ("Wave1219", "CCollisionSeekingThing__ctor_base", "CHLCollisionDetector__ctor_base", BACKUP),
    OGG_DOC: ("Wave1219", "COggLoader__ctor_base", "COggFileRead__scalar_deleting_dtor", BACKUP),
    PLANE_DOC: ("Wave1219", "CPlane__Hit_CheckFatalDamageAndDie", BACKUP),
    SENTINEL_DOC: ("Wave1219", "CSentinel__Init", BACKUP),
    GILLMHEAD_DOC: ("Wave1219", "SharedUnitAnimation__PlayAnimationByNameIfPresent", BACKUP),
    LTSHELL_DOC: ("Wave1219", "PCLTShell__ctor", BACKUP),
    FUNCTION_INDEX: ("Wave1219", "CDebugMarker__ctor", BACKUP),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime streaming behavior proven",
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
        "pre-metadata.tsv": 16,
        "pre-tags.tsv": 16,
        "pre-xrefs.tsv": 44,
        "pre-instructions.tsv": 539,
        "pre-decompile/index.tsv": 16,
        "post-metadata.tsv": 16,
        "post-tags.tsv": 16,
        "post-xrefs.tsv": 44,
        "post-instructions.tsv": 539,
        "post-decompile/index.tsv": 16,
    }
    for relative, expected in expected_counts.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == expected, f"{relative} row count mismatch: {len(rows)} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    evidence_text = (
        read_text(BASE / "post-metadata.tsv")
        + read_text(BASE / "post-tags.tsv")
        + read_text(BASE / "post-xrefs.tsv")
        + read_text(BASE / "post-instructions.tsv")
        + "".join(read_text(path) for path in sorted((BASE / "post-decompile").glob("*.c")))
    )

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("rebuild parity remain" in row.get("comment", ""), f"boundary missing at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing common tags at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        for token in tokens:
            require(contains_token(evidence_text, token), f"missing evidence token for {address}: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=84 tags_removed=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=16 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=84 tags_removed=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 tags_removed=0 missing=0 bad=0",
        "post-metadata.log": "targets=16 found=16 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=0",
        "post-xrefs.log": "Wrote 44 rows",
        "post-instructions.log": "Wrote 539 function-body instruction rows",
        "post-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6411 commented_functions=6411",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave1219.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_backup_and_progress(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176458631 or backup.get("totalBytes") == 176458631.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("focusedReviewed") == 1179, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "100.00%", "progress percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 0, "progress remaining mismatch", failures)
    require(current.get("latestReviewTag") == "wave1219-final-score16-current-risk-review", "latest review tag mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1179, "ledger reviewed mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "100.00%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 0, "ledger remaining mismatch", failures)
    require(ledger.get("latestWaveTag") == "wave1219-final-score16-current-risk-review", "ledger latest tag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        LEDGER,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        MAPPED,
        CAMPAIGN,
        RANK,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave note mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1219-final-score16-current-risk-review")
        == r"py -3 tools\wave1219_final_score16_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_backup_and_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1219 final score16 current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1219 final score16 current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
