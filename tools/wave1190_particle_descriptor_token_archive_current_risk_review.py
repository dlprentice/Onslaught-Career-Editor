#!/usr/bin/env python3
"""Validate Wave1190 particle descriptor / TokenArchive current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1190-particle-descriptor-token-archive-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1190-particle-descriptor-token-archive-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1190-particle-descriptor-token-archive-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1190_particle_descriptor_token_archive_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md"
TOKEN_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "TokenArchive.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
APPLY_SCRIPT = ROOT / "tools" / "ApplyParticleDescriptorTokenArchiveCurrentRiskWave1190.java"

BACKUP = r"G:\GhidraBackups\BEA_20260606-173000_post_wave1190_particle_descriptor_token_archive_current_risk_review_verified"

TOKEN_WRITERS = {
    "0x004c07f0": ("CPDSimpleSprite__WriteTokenFields", "void __fastcall CPDSimpleSprite__WriteTokenFields(void * this)", "0x005ddf7c", "tokens 6 through 0x1b", "simple-sprite"),
    "0x004c1970": ("CPDEmitter__WriteTokenFields", "void __fastcall CPDEmitter__WriteTokenFields(void * this)", "0x005ddf14", "tokens 0x1a through 0x28", "emitter"),
    "0x004c2220": ("CPDSelector__WriteTokenFields", "void __fastcall CPDSelector__WriteTokenFields(void * this)", "0x005dde44", "tokens 0x29 through 0x30", "selector"),
    "0x004c2400": ("CPDColourRange__WriteTokenFields", "void __fastcall CPDColourRange__WriteTokenFields(void * this)", "0x005ddddc", "tokens 0x31 through 0x3c", "colour-range"),
    "0x004c2ca0": ("CPDShape__WriteTokenFields", "void __fastcall CPDShape__WriteTokenFields(void * this)", "0x005ddd0c", "tokens 0x3f through 0x46", "shape"),
    "0x004c3440": ("CPDTrail__WriteTokenFields", "void __fastcall CPDTrail__WriteTokenFields(void * this)", "0x005ddca4", "tokens 0x47 through 0x54", "trail"),
    "0x004c4920": ("CPDFunction__WriteTokenFields", "void __fastcall CPDFunction__WriteTokenFields(void * this)", "0x005ddbd4", "tokens 0x5c through 0x64", "function-curve"),
    "0x004c4c70": ("CPDMesh__WriteTokenFields", "void __fastcall CPDMesh__WriteTokenFields(void * this)", "0x005ddb58", "tokens 0x65 through 0x68", "mesh"),
    "0x004c53b0": ("CPDFoR__WriteTokenFields", "void __fastcall CPDFoR__WriteTokenFields(void * this)", "0x005ddfe4", "tokens 0x69, 0x6a, and 0x28", "frame-of-reference"),
    "0x004c59e0": ("CPDPMesh__WriteTokenFields", "void __fastcall CPDPMesh__WriteTokenFields(void * this)", "0x005de04c", "tokens 0x6b through 0x7b", "particle-mesh"),
}

TARGETS = {
    **TOKEN_WRITERS,
    "0x004f5b70": (
        "CTokenArchive__BindIndexedFieldPointer",
        "void __thiscall CTokenArchive__BindIndexedFieldPointer(void * this, int slot_index, void * field_ptr)",
        "CALLS",
        "CParticleDescriptor__Load",
        "indexed-field-binder",
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1190-particle-descriptor-token-archive-current-risk-review",
    "wave1190-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "particle-descriptor",
    "token-archive",
    "token-writer",
    "source-identity-deferred",
    "exact-layout-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1190",
    "wave1190-particle-descriptor-token-archive-current-risk-review",
    "819/1179 = 69.47%",
    "11 particle descriptor token-writer/TokenArchive current-risk rows",
    "current focused candidates: 1169",
    "live regenerated current focused candidates: 1169",
    "remaining active focused work: 360",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=11 skipped=0",
    "comment_only_updated=11",
    "tags_added=123",
    "final dry updated=0 skipped=11",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "CPDSimpleSprite__WriteTokenFields",
    "CPDEmitter__WriteTokenFields",
    "CPDSelector__WriteTokenFields",
    "CPDColourRange__WriteTokenFields",
    "CPDShape__WriteTokenFields",
    "CPDTrail__WriteTokenFields",
    "CPDFunction__WriteTokenFields",
    "CPDMesh__WriteTokenFields",
    "CPDFoR__WriteTokenFields",
    "CPDPMesh__WriteTokenFields",
    "CTokenArchive__BindIndexedFieldPointer",
    "CParticleDescriptor__Load",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "25 xref rows",
    "733 instruction rows",
    "11 decompile rows",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime particle parsing proven",
    "runtime particle rendering proven",
    "exact descriptor layout proven",
    "exact tokenarchive layout proven",
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
        "pre-metadata.tsv": 11,
        "pre-tags.tsv": 11,
        "pre-xrefs.tsv": 25,
        "pre-instructions.tsv": 733,
        "pre-decompile/index.tsv": 11,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 25,
        "post-instructions.tsv": 733,
        "post-decompile/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature, xref_anchor, token_span, specific_tag) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave1190 static read-back", token_span, "clean-room/no-noticeable-difference parity remain separate proof"):
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"missing common tags at {address}: {COMMON_TAGS - actual}", failures)
            require(specific_tag in actual, f"missing specific tag at {address}: {specific_tag}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        rows = [row for row in xrefs if normalize_address(row.get("target_addr", "")) == address]
        require(rows, f"missing xrefs for {address}", failures)
        if xref_anchor != "CALLS":
            require(
                any(normalize_address(row.get("from_addr", "")) == xref_anchor and row.get("ref_type") == "DATA" for row in rows),
                f"missing DATA vtable xref at {address}: {xref_anchor}",
                failures,
            )
        else:
            require(len(rows) >= 15, "TokenArchive binder xref count too small", failures)
            require(any(row.get("from_function") == "CParticleDescriptor__Load" for row in rows), "missing CParticleDescriptor__Load binder xref", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 tags_added=123 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 tags_added=123 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=11 found=11 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "post-xrefs.log": "Wrote 25 rows",
        "post-instructions.log": "Wrote 733 function-body instruction rows",
        "post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_progress_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 819, "focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "69.47%", "focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 360, "remaining focused mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1169, "live focused mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "risk candidate mismatch", failures)
    require(progress["latestWave"]["artifactCommit"] in ("pending Wave1190 artifact commit",) or len(progress["latestWave"]["artifactCommit"]) == 40, "artifact commit field mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176196487 or backup.get("totalBytes") == 176196487.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1190 note mirror mismatch", failures)
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        BINARY_INDEX,
        RE_INDEX,
        PARTICLE_DOC,
        TOKEN_DOC,
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
        package.get("scripts", {}).get("test:wave1190-particle-descriptor-token-archive-current-risk-review")
        == r"py -3 tools\wave1190_particle_descriptor_token_archive_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1190 apply script", failures)


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
        print("Wave1190 particle descriptor / TokenArchive current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1190 particle descriptor / TokenArchive current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
