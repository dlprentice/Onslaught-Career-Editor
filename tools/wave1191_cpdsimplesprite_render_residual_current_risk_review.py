#!/usr/bin/env python3
"""Validate Wave1191 CPDSimpleSprite render residual current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1191-cpdsimplesprite-render-residual-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1191-cpdsimplesprite-render-residual-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1191-cpdsimplesprite-render-residual-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1191_cpdsimplesprite_render_residual_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
APPLY_SCRIPT = ROOT / "tools" / "ApplyCPDSimpleSpriteRenderResidualCurrentRiskWave1191.java"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-175052_post_wave1191_cpdsimplesprite_render_residual_current_risk_review_verified"

TARGETS = {
    "0x004c0940": (
        "CPDSimpleSprite__SetUVFromTileIndex",
        "void __thiscall CPDSimpleSprite__SetUVFromTileIndex(void * this, int tile_index, uint tile_grid_selector, int unused_context)",
        ("tile-grid selector jump table", "this+0xb8..this+0xc4", "0..1 UVs"),
        "sprite-uv",
    ),
    "0x004c5280": (
        "CPDSimpleSprite__CopyTransformMatrix",
        "void __thiscall CPDSimpleSprite__CopyTransformMatrix(void * this, void * out_matrix, void * unused_context)",
        ("basis/transform float fields", "unused/context artifact", "conservative"),
        "matrix-copy",
    ),
    "0x004c5c50": (
        "CPDSimpleSprite__BuildUvAtlasBuckets",
        "void __fastcall CPDSimpleSprite__BuildUvAtlasBuckets(float unused_seed)",
        ("DAT_00829e58", "DAT_0082b39c", "five tile-grid bucket families"),
        "global-atlas-table",
    ),
    "0x004c5d50": (
        "CPDSimpleSprite__ProcessAndRenderSpriteList",
        "void __fastcall CPDSimpleSprite__ProcessAndRenderSpriteList(void * descriptor)",
        ("CVBufTexture__GetVertexPtrAt", "DXParticleTexture__GetIndexBuffer", "six indices"),
        "vertex-emission",
    ),
    "0x004c78b0": (
        "CPDSimpleSprite__ScaleVec3InPlace",
        "void __thiscall CPDSimpleSprite__ScaleVec3InPlace(void * this, float scale, float unused_context)",
        ("0x004c745f", "0x004c7689", "three consecutive float components"),
        "vec3",
    ),
    "0x004c78d0": (
        "CPDSimpleSprite__ReciprocalVec3Magnitude",
        "double __fastcall CPDSimpleSprite__ReciprocalVec3Magnitude(void * vec3)",
        ("1.0 / sqrt", "no zero-length guard", "three float components"),
        "reciprocal-magnitude",
    ),
    "0x004c7950": (
        "CPDSimpleSprite__EvaluateCurveDrivenScale",
        "double __thiscall CPDSimpleSprite__EvaluateCurveDrivenScale(void * this, void * x_value, float lifetime, float particle_context, float eval_flags)",
        ("recursive expression nodes", "pow/exp/sin/cos/inv/log/rand-style", "clamp/wrap output modes"),
        "expression-eval",
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1191-cpdsimplesprite-render-residual-current-risk-review",
    "wave1191-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "cpdsimplesprite",
    "particle-render",
    "sprite-render",
    "source-identity-deferred",
    "exact-layout-deferred",
    "runtime-behavior-deferred",
    "visual-parity-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1191",
    "wave1191-cpdsimplesprite-render-residual-current-risk-review",
    "826/1179 = 70.06%",
    "7 CPDSimpleSprite render residual current-risk rows",
    "current focused candidates: 1169",
    "live regenerated current focused candidates: 1169",
    "remaining active focused work: 353",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=7 skipped=0",
    "comment_only_updated=7",
    "tags_added=100",
    "final dry updated=0 skipped=7",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "CPDSimpleSprite__SetUVFromTileIndex",
    "CPDSimpleSprite__CopyTransformMatrix",
    "CPDSimpleSprite__BuildUvAtlasBuckets",
    "CPDSimpleSprite__ProcessAndRenderSpriteList",
    "CPDSimpleSprite__ScaleVec3InPlace",
    "CPDSimpleSprite__ReciprocalVec3Magnitude",
    "CPDSimpleSprite__EvaluateCurveDrivenScale",
    "CVBufTexture__GetVertexPtrAt",
    "DXParticleTexture__GetIndexBuffer",
    "DAT_00829e58",
    "DAT_0082b39c",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "9 xref rows",
    "2369 instruction rows",
    "7 decompile rows",
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
    "runtime particle rendering proven",
    "visual parity proven",
    "exact descriptor layout proven",
    "exact particle layout proven",
    "exact cvbuftexture layout proven",
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
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 9,
        "pre-instructions.tsv": 2369,
        "pre-decompile/index.tsv": 7,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 9,
        "post-instructions.tsv": 2369,
        "post-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature, comment_tokens, specific_tag) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Wave1191 static current-risk read-back", "Static rebuild contract only", "clean-room/no-noticeable-difference parity remain separate proof"):
                require(token in comment, f"missing common comment token at {address}: {token}", failures)
            for token in comment_tokens:
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

    require(
        any(row.get("from_function") == "CPDSimpleSprite__VFunc_23_004c8040" for row in xrefs),
        "missing CPDSimpleSprite__VFunc_23_004c8040 xref",
        failures,
    )
    require(
        sum(1 for row in xrefs if row.get("from_function") == "CPDSimpleSprite__ProcessAndRenderSpriteList") >= 5,
        "render-list xref count too small",
        failures,
    )


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=100 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=100 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-xrefs.log": "Wrote 9 rows",
        "post-instructions.log": "Wrote 2369 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
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
    require(current["focusedReviewed"] == 826, "focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "70.06%", "focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 353, "remaining focused mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1169, "live focused mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "risk candidate mismatch", failures)
    require(progress["latestWave"]["artifactCommit"] in ("pending Wave1191 artifact commit",) or len(progress["latestWave"]["artifactCommit"]) == 40, "artifact commit field mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176196487 or backup.get("totalBytes") == 176196487.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1191 note mirror mismatch", failures)
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
        package.get("scripts", {}).get("test:wave1191-cpdsimplesprite-render-residual-current-risk-review")
        == r"py -3 tools\wave1191_cpdsimplesprite_render_residual_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1191 apply script", failures)


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
        print("Wave1191 CPDSimpleSprite render residual current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1191 CPDSimpleSprite render residual current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
