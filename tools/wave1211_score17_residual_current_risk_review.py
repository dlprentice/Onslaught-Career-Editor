#!/usr/bin/env python3
"""Validate Wave1211 score-17 residual current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1211-score17-residual-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1211-score17-residual-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1211-score17-residual-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1211_score17_residual_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ACTOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Actor.cpp" / "_index.md"
BUILDING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Building.cpp" / "_index.md"
RADAR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "RadarWarningReceiver.cpp" / "_index.md"
SQUAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadNormal.cpp" / "_index.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
D3D_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "d3dapp.cpp" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
APPLY_SCRIPT = ROOT / "tools" / "ApplyScore17ResidualCurrentRiskWave1211.java"

BACKUP = r"G:\GhidraBackups\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified"

TARGETS = {
    "0x00402030": ("CActor__StickToGround", "void __thiscall CActor__StickToGround(void * this)", ("CThing::StickToGround", "mOldPos=mPos")),
    "0x0040c5b0": ("CRepairPadAI__IsWithinRepairBounds", "int __thiscall CRepairPadAI__IsWithinRepairBounds(void * this)", ("CRepairPadAI__IsCompatibleDockCandidate", "+0xf8/+0xfc")),
    "0x004d66b0": ("CRadarWarningReceiver__Update", "void __fastcall CRadarWarningReceiver__Update(void * this)", ("DAT_008551a0", "event 0x0fa2")),
    "0x004e97e0": ("CGenericActiveReader__SwapWithCandidateIfFormationCloser", "bool __thiscall CGenericActiveReader__SwapWithCandidateIfFormationCloser(void * this, void * candidate_reader)", ("CGenericActiveReader__SetReader", "formation")),
    "0x004e9f00": ("CSquadNormal__VFunc_52_004e9f00", "void __fastcall CSquadNormal__VFunc_52_004e9f00(void * this)", ("CUnit__RenderWithIdentityWorldAndShadowProbe", "0x006fadc8")),
    "0x004f45e0": ("CComplexThing__SetVar", "void __stdcall CComplexThing__SetVar(void * var_name, void * data)", ("CComplexThing::SetVar", "unknown variable")),
    "0x0052a830": ("CD3DApplication__FindDepthStencilFormat", "bool __thiscall CD3DApplication__FindDepthStencilFormat(void * this, uint adapter_index, int device_type, int target_format, int * out_depth_stencil_format)", ("CD3DApplication__BuildDeviceList", "RET 0x10")),
    "0x005d06f0": ("CRT__InitSehFrameNoop", "void CRT__InitSehFrameNoop(void)", ("CDXTexture__InitCpuVendorAndSimdFlags", "FS:[0]")),
}

TARGET_XREFS = {
    "0x00402030": ("0x004dfd13", "UNCONDITIONAL_CALL"),
    "0x0040c5b0": ("0x004d6e0a", "UNCONDITIONAL_CALL"),
    "0x004d66b0": ("0x004d6a1c", "UNCONDITIONAL_CALL"),
    "0x004e97e0": ("0x004e8640", "UNCONDITIONAL_CALL"),
    "0x004e9f00": ("0x005df1c4", "DATA"),
    "0x004f45e0": ("0x005d8544", "DATA"),
    "0x0052a830": ("0x00529f8f", "UNCONDITIONAL_CALL"),
    "0x005d06f0": ("0x005891cb", "UNCONDITIONAL_CALL"),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1211-score17-residual-current-risk-review",
    "wave1211-readback-verified",
    "current-risk-review",
    "retail-binary-evidence",
    "score17-residual",
    "rebuild-grade-static-contract",
}

DOC_TOKENS = (
    "Wave1211",
    "wave1211-score17-residual-current-risk-review",
    "8 score-17 residual current-risk rows",
    "1110/1179 = 94.15%",
    "remaining active focused work: 69",
    "1141/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1127",
    "live regenerated current focused candidates: 1127",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "tag-only normalization",
    "tags_added=41",
    "final dry updated=0 skipped=8",
    "no rename",
    "no signature change",
    "no comment change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "106 xref rows",
    "1132 instruction rows",
    "8 decompile rows",
    "217 context xref rows",
    "3103 context instruction rows",
    "15 context decompile rows",
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
    ACTOR_DOC: (
        "Wave1211",
        "wave1211-score17-residual-current-risk-review",
        "CActor__StickToGround",
        "1110/1179 = 94.15%",
        BACKUP,
    ),
    BUILDING_DOC: (
        "Wave1211",
        "wave1211-score17-residual-current-risk-review",
        "CRepairPadAI__IsWithinRepairBounds",
        "1110/1179 = 94.15%",
        BACKUP,
    ),
    RADAR_DOC: (
        "Wave1211",
        "wave1211-score17-residual-current-risk-review",
        "CRadarWarningReceiver__Update",
        "1110/1179 = 94.15%",
        BACKUP,
    ),
    SQUAD_DOC: (
        "Wave1211",
        "wave1211-score17-residual-current-risk-review",
        "CGenericActiveReader__SwapWithCandidateIfFormationCloser",
        "CSquadNormal__VFunc_52_004e9f00",
        "1110/1179 = 94.15%",
        BACKUP,
    ),
    THING_DOC: (
        "Wave1211",
        "wave1211-score17-residual-current-risk-review",
        "CComplexThing__SetVar",
        "1110/1179 = 94.15%",
        BACKUP,
    ),
    D3D_DOC: (
        "Wave1211",
        "wave1211-score17-residual-current-risk-review",
        "CD3DApplication__FindDepthStencilFormat",
        "1110/1179 = 94.15%",
        BACKUP,
    ),
    DXTEXTURE_DOC: (
        "Wave1211",
        "wave1211-score17-residual-current-risk-review",
        "CRT__InitSehFrameNoop",
        "1110/1179 = 94.15%",
        BACKUP,
    ),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime docking behavior proven",
    "runtime radar behavior proven",
    "runtime squad behavior proven",
    "runtime d3d behavior proven",
    "runtime exception behavior proven",
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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 106,
        "pre-instructions.tsv": 1132,
        "pre-decompile/index.tsv": 8,
        "context-metadata.tsv": 15,
        "context-tags.tsv": 15,
        "context-xrefs.tsv": 217,
        "context-instructions.tsv": 3103,
        "context-decompile/index.tsv": 15,
        "post-metadata.tsv": 8,
        "post-tags.tsv": 8,
        "post-xrefs.tsv": 106,
        "post-instructions.tsv": 1132,
        "post-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("runtime" in comment.lower() and "rebuild parity" in comment.lower(), f"missing runtime/rebuild boundary at {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"missing Wave1211 tags at {address}: {COMMON_TAGS - actual}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        expected_from, expected_type = TARGET_XREFS[address]
        rows = [
            row
            for row in xrefs
            if normalize_address(row.get("target_addr", "")) == address
            and normalize_address(row.get("from_addr", "")) == expected_from
            and row.get("ref_type") == expected_type
        ]
        require(rows, f"missing expected xref for {address}: {expected_from} {expected_type}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=41 tags_removed=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=41 tags_removed=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 tags_removed=0 missing=0 bad=0",
        "post-metadata.log": "targets=8 found=8 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "post-xrefs.log": "Wrote 106 rows",
        "post-instructions.log": "Wrote 1132 function-body instruction rows",
        "post-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "context-metadata.log": "targets=15 found=15 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "context-xrefs.log": "Wrote 217 rows",
        "context-instructions.log": "Wrote 3103 function-body instruction rows",
        "context-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply save report missing", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_accounting(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    progress = read_json(PROGRESS)
    ledger = read_json(LEDGER)
    current = progress["post100Reaudit"]["currentRiskRank"]
    for data, label in ((current, "progress"), (ledger, "ledger")):
        getter = data.get
        require(getter("focusedReviewed", getter("correctedUniqueReviewed")) == 1110, f"{label} reviewed mismatch", failures)
        require(getter("focusedReviewedPercent", getter("correctedUniquePercent")) == "94.15%", f"{label} percent mismatch", failures)
        require(getter("remainingFocusedAfterLatestReview", getter("remainingUnique")) == 69, f"{label} remaining mismatch", failures)
        require(getter("liveFocusedCandidatesAfterLatestReview") == 1127, f"{label} live focused mismatch", failures)
    require(ledger.get("latestWaveTag") == "wave1211-score17-residual-current-risk-review", "ledger latest tag mismatch", failures)
    require(ledger.get("legacyAdditiveThroughWave1211Deprecated") == 1141, "legacy additive mismatch", failures)
    require(ledger.get("countedRowsThroughWave1211") == 1136, "counted rows mismatch", failures)
    require(ledger.get("duplicateAddressOvercount") == 26, "duplicate overcount mismatch", failures)
    require(ledger.get("wave1145ArithmeticOvercount") == 5, "Wave1145 overcount mismatch", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1211 note mirror mismatch", failures)
    core_docs = [
        NOTE,
        READINESS,
        PROGRESS,
        LEDGER,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        MAPPED,
        CAMPAIGN,
        RANK,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_INDEX,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
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
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1211-score17-residual-current-risk-review")
        == r"py -3 tools\wave1211_score17_residual_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1211 apply script", failures)
    require(any(row.get("task") == "Wave1211 score-17 residual current-risk review" for row in read_jsonl(LEDGER_JSONL)), "missing Wave1211 ledger row", failures)
    require(any(row.get("task") == "Wave1211 score-17 residual current-risk review" for row in read_jsonl(ATTEMPTS)), "missing Wave1211 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_accounting(failures)
    check_docs(failures)

    if failures:
        print("Wave1211 score-17 residual current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1211 score-17 residual current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
