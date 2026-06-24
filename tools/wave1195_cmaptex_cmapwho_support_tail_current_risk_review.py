#!/usr/bin/env python3
"""Validate Wave1195 CMapTex/CMapWho support-tail current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1195-maptex-mapwho-residual-score16-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1195-cmaptex-cmapwho-support-tail-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1195-cmaptex-cmapwho-support-tail-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1195_cmaptex_cmapwho_support_tail_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
MAPTEX_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "maptex.cpp" / "_index.md"
MAPWHO_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mapwho.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
APPLY_SCRIPT = ROOT / "tools" / "ApplyMaptexMapwhoSupportTailWave1195.java"

BACKUP = r"G:\GhidraBackups\BEA_20260606-200142_post_wave1195_cmaptex_cmapwho_support_tail_current_risk_review_verified"

TARGETS = {
    "0x00491180": ("CMapTex__Reset", "void __fastcall CMapTex__Reset(void * this)", ("OID__FreeObject", "+0x00/+0x08", "+0x0c")),
    "0x00491340": ("CMapTex__DownsampleTexture", "void __thiscall CMapTex__DownsampleTexture(void * this, void * dest_buffer, void * src_buffer)", ("2x2 source texels", "fourth channel")),
    "0x004915d0": ("CMapTex__CopyFromOther", "void __thiscall CMapTex__CopyFromOther(void * this, void * source_map_tex)", ("CMapTex__DownsampleTexture", "halves the destination width")),
    "0x004916c0": ("CMapTex__Deserialize", "void __thiscall CMapTex__Deserialize(void * this, void * chunk_reader, int texture_index)", ("0x4c-byte CMapTex header", "count << 0xc")),
    "0x00491900": ("CMapWhoEntry__Init", "void __fastcall CMapWhoEntry__Init(void * entry)", ("+0x00/+0x04 next/previous",)),
    "0x00491d80": ("CMapWho__SetIteratorFromSectorHead", "void * __thiscall CMapWho__SetIteratorFromSectorHead(void * this, void * sector_entry)", ("sector head at +0x04", "this+0x00")),
    "0x00491d90": ("CMapWho__AdvanceIteratorAndGetCurrent", "void * __fastcall CMapWho__AdvanceIteratorAndGetCurrent(void * this)", ("current entry next pointer",)),
    "0x00491da0": ("CMapWho__IsSectorCoordInBounds", "int __stdcall CMapWho__IsSectorCoordInBounds(void * sector_coord)", ("64 >> (4 - level)",)),
    "0x00491df0": ("CMapWho__SetupNextRadiusLevel", "int __fastcall CMapWho__SetupNextRadiusLevel(void * this)", ("query radius at +0x28",)),
    "0x00492860": ("CMapWho__DebugDrawSector", "void __thiscall CMapWho__DebugDrawSector(void * this, int packed_sector_coord, int level)", ("CThing__RenderDebugVolumeOverlay",)),
    "0x00492950": ("CMapWho__DebugDraw", "void __fastcall CMapWho__DebugDraw(void * this)", ("CMapWhoEntry__GetOwner",)),
    "0x00492c60": ("CMapWhoEntry__Invalidate", "void __fastcall CMapWhoEntry__Invalidate(void * entry)", ("+0x0c",)),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1195-cmaptex-cmapwho-support-tail-current-risk-review",
    "wave1195-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "score16",
    "maptex-mapwho-support-tail",
    "source-identity-deferred",
    "exact-layout-deferred",
    "runtime-behavior-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1195",
    "wave1195-cmaptex-cmapwho-support-tail-current-risk-review",
    "877/1179 = 74.39%",
    "12 CMapTex/CMapWho support-tail score16 current-risk rows",
    "current focused candidates: 1142",
    "live regenerated current focused candidates: 1142",
    "remaining active focused work: 302",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=12 skipped=0",
    "comment_only_updated=12",
    "tags_added=132",
    "final dry updated=0 skipped=12",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consult used",
    "no Cursor/Composer",
    "CMapTex__Reset",
    "CMapTex__DownsampleTexture",
    "CMapTex__CopyFromOther",
    "CMapTex__Deserialize",
    "CMapWhoEntry__Init",
    "CMapWho__SetIteratorFromSectorHead",
    "CMapWho__AdvanceIteratorAndGetCurrent",
    "CMapWho__IsSectorCoordInBounds",
    "CMapWho__SetupNextRadiusLevel",
    "CMapWho__DebugDrawSector",
    "CMapWho__DebugDraw",
    "CMapWhoEntry__Invalidate",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "37 xref rows",
    "561 instruction rows",
    "12 decompile rows",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
    "rebuild-grade specification",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime terrain texture behavior proven",
    "runtime spatial-query behavior proven",
    "runtime debug rendering behavior proven",
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
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 37,
        "pre-instructions.tsv": 561,
        "pre-decompile/index.tsv": 12,
        "post-metadata.tsv": 12,
        "post-tags.tsv": 12,
        "post-xrefs.tsv": 37,
        "post-instructions.tsv": 561,
        "post-decompile/index.tsv": 12,
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
            for token in (
                "Wave1195 static current-risk read-back",
                "Static rebuild contract only",
                "clean-room/no-noticeable-difference parity remain separate proof",
            ):
                require(token in comment, f"missing common comment token at {address}: {token}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"missing common tags at {address}: {COMMON_TAGS - actual}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        rows = [row for row in xrefs if normalize_address(row.get("target_addr", "")) == address]
        require(rows, f"missing xrefs for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=12 tags_added=132 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=12 tags_added=132 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=12 found=12 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-xrefs.log": "Wrote 37 rows",
        "post-instructions.log": "Wrote 561 function-body instruction rows",
        "post-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "Input file not found", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply save report missing", failures)


def check_progress_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 877, "focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "74.39%", "focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 302, "remaining focused mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1142, "live focused mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "risk candidate mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176327559 or backup.get("totalBytes") == 176327559.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1195 note mirror mismatch", failures)
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        GHIDRA_REFERENCE,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        BINARY_INDEX,
        RE_INDEX,
        MAPTEX_DOC,
        MAPWHO_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1195-cmaptex-cmapwho-support-tail-current-risk-review")
        == r"py -3 tools\wave1195_cmaptex_cmapwho_support_tail_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1195 apply script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_progress_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1195 CMapTex/CMapWho support-tail current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1195 CMapTex/CMapWho support-tail current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
