#!/usr/bin/env python3
"""Validate Wave1204 geometry/terrain residual current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1204-geometry-terrain-residual-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1204-geometry-terrain-residual-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1204-geometry-terrain-residual-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1204_geometry_terrain_residual_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
MESH_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-013948_post_wave1204_geometry_terrain_residual_current_risk_review_verified"

TARGETS = {
    "0x00402dd0": ("ShadowHeightfield__AnyBoundsCornerAboveSampledHeight", "int __thiscall ShadowHeightfield__AnyBoundsCornerAboveSampledHeight(void * this)"),
    "0x00479630": ("Geometry__RaySphereEntryDistance", "double __cdecl Geometry__RaySphereEntryDistance(void * rayStart, void * rayEnd, float radius)"),
    "0x00479770": ("Geometry__DistanceOutsideAabb", "double __cdecl Geometry__DistanceOutsideAabb(void * point, void * halfExtents)"),
    "0x0047f750": ("CHeightField__Load", "void __thiscall CHeightField__Load(void * this, void * chunk_reader)"),
    "0x00490e10": ("CHeightField__Constructor", "void * __fastcall CHeightField__Constructor(void * this)"),
    "0x004f74b0": ("Triangulate__SplitTriangleAtPointAndLegalizeEdges", "int __thiscall Triangulate__SplitTriangleAtPointAndLegalizeEdges(void * this, void * triangle_indices, void * point_xy)"),
    "0x004f7660": ("Triangulate__TryFlipSharedEdgeForQuality", "void __thiscall Triangulate__TryFlipSharedEdgeForQuality(void * this, int edge_start, int edge_end)"),
    "0x004f78c0": ("Triangulate__FindTriangleByDirectedEdge", "short * __thiscall Triangulate__FindTriangleByDirectedEdge(void * this, int edge_start, int edge_end)"),
    "0x004f7940": ("Triangulate__RelaxMeshByEdgeFlips", "void __fastcall Triangulate__RelaxMeshByEdgeFlips(void * this)"),
}

SHADOW_TAGS = {
    "static-reaudit",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-corrected",
    "geometry",
    "terrain-heightfield",
    "shadow-heightfield",
    "static-shadows",
    "current-risk-review",
    "wave1204-geometry-terrain-residual-current-risk-review",
    "wave1204-readback-verified",
}

COMMENT_TOKENS = {
    "0x00402dd0": ("CStaticShadows__SampleShadowHeightBilinear", "vfunc +0xc0", "runtime shadow behavior"),
    "0x00479630": ("origin-centered sphere entry distance", "retail sentinel", "runtime collision behavior"),
    "0x00479770": ("AABB overhangs", "retail instruction sequence", "runtime collision behavior"),
    "0x0047f750": ("0x13dc", "0xa2000", "9x9 tile blocks"),
    "0x00490e10": ("global MAP constructor wrapper", "CHeightField__ResetCoreBuffersAndFlags", "runtime terrain behavior"),
    "0x004f74b0": ("epsilon 0x005d856c", "appends two triangle triplets", "quality flips"),
    "0x004f7660": ("finds triangles on both sides of the directed edge", "ratio threshold 0x005d85f8", "dirty flag"),
    "0x004f78c0": ("rotates a matching triangle", "requested edge becomes the first two indices", "absent edges return null"),
    "0x004f7940": ("up to ten passes", "TryFlipSharedEdgeForQuality", "mesh dirty"),
}

DECOMPILE_TOKENS = (
    "CStaticShadows__SampleShadowHeightBilinear",
    "CHeightField__InitColorGradient",
    "Triangulate__TryFlipSharedEdgeForQuality",
    "Triangulate__FindTriangleByDirectedEdge",
    "Geometry__RaySphereEntryDistance",
    "Geometry__DistanceOutsideAabb",
)

DOC_TOKENS = (
    "Wave1204",
    "wave1204-geometry-terrain-residual-current-risk-review",
    "9 Geometry/Terrain residual current-risk rows",
    "1071/1179 = 90.84%",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "remaining active focused work: 108",
    "legacy additive counter is deprecated",
    "1102/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "tag-only normalization",
    "updated=1 skipped=0",
    "tags_added=11",
    "final dry updated=0 skipped=1",
    "no rename",
    "no signature change",
    "no comment change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "ShadowHeightfield__AnyBoundsCornerAboveSampledHeight",
    "Geometry__RaySphereEntryDistance",
    "Geometry__DistanceOutsideAabb",
    "CHeightField__Load",
    "CHeightField__Constructor",
    "Triangulate__SplitTriangleAtPointAndLegalizeEdges",
    "Triangulate__TryFlipSharedEdgeForQuality",
    "Triangulate__FindTriangleByDirectedEdge",
    "Triangulate__RelaxMeshByEdgeFlips",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "15 xref rows",
    "1058 instruction rows",
    "9 decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime terrain behavior proven",
    "runtime collision behavior proven",
    "runtime shadow behavior proven",
    "runtime triangulation behavior proven",
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
        "pre-metadata.tsv": 9,
        "pre-tags.tsv": 9,
        "pre-xrefs.tsv": 15,
        "pre-instructions.tsv": 1058,
        "pre-decompile/index.tsv": 9,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 15,
        "post-instructions.tsv": 1058,
        "post-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("runtime" in comment.lower() or "rebuild parity" in comment.lower(), f"missing runtime/rebuild boundary at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            if address == "0x00402dd0":
                actual_tags = set(tag_row.get("tags", "").split(";"))
                require(SHADOW_TAGS.issubset(actual_tags), f"shadow-heightfield tags missing: {SHADOW_TAGS - actual_tags}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_targets = {normalize_address(row["target_addr"]) for row in xrefs}
    for address in TARGETS:
        require(address in xref_targets, f"missing xref coverage for {address}", failures)

    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (BASE / "post-decompile").glob("*.c"))
    for token in DECOMPILE_TOKENS:
        require(token in decompile_text, f"missing decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=11 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=11 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 15 rows",
        "post-instructions.log": "Wrote 1058 function-body instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save report", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = {
        "note": read_text(NOTE),
        "note_mirror": read_text(NOTE_MIRROR),
        "readiness": read_text(READINESS),
        "progress": read_text(PROGRESS),
        "ledger": read_text(LEDGER),
        "accounting": read_text(ACCOUNTING),
        "measurement_register": read_text(MEASUREMENT_REGISTER),
        "mapped": read_text(MAPPED),
        "campaign": read_text(CAMPAIGN),
        "rank": read_text(RANK),
        "binary_index": read_text(BINARY_INDEX),
        "re_index": read_text(RE_INDEX),
        "mesh_contract": read_text(MESH_CONTRACT),
        "backlog": read_text(BACKLOG),
        "developer_state": read_text(DEVELOPER_STATE),
        "documentation_state": read_text(DOCUMENTATION_STATE),
        "re_state": read_text(RE_STATE),
    }
    require(docs["note"] == docs["note_mirror"], "wave note mirror mismatch", failures)
    for name, text in docs.items():
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {name}: {bad}", failures)

    progress = read_json(PROGRESS)["post100Reaudit"]["currentRiskRank"]
    require(progress.get("focusedReviewed") == 1071, "progress focusedReviewed mismatch", failures)
    require(progress.get("focusedReviewedPercent") == "90.84%", "progress percent mismatch", failures)
    require(progress.get("remainingFocusedAfterLatestReview") == 108, "progress remaining mismatch", failures)
    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1071, "ledger unique mismatch", failures)
    require(ledger.get("remainingUnique") == 108, "ledger remaining mismatch", failures)
    require(ledger.get("legacyAdditiveThroughWave1204Deprecated") == 1102, "ledger legacy additive mismatch", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1204-geometry-terrain-residual-current-risk-review")
        == r"py -3 tools\wave1204_geometry_terrain_residual_current_risk_review.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempts = read_jsonl(ATTEMPTS)
    require(any(row.get("task") == "Wave1204 geometry/terrain residual current-risk review" for row in ledger_rows), "missing Wave1204 ledger row", failures)
    require(any(row.get("task") == "Wave1204 geometry/terrain residual current-risk review" for row in attempts), "missing Wave1204 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1204 geometry/terrain residual current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1204 geometry/terrain residual current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
