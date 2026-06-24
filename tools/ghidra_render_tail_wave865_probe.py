#!/usr/bin/env python3
"""Validate Wave865 render-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave865-render-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_render_tail_wave865_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
CUTSCENE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Cutscene.cpp" / "_index.md"
DXIMPOSTER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXImposter.cpp" / "_index.md"
DXLANDSCAPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXLandscape.cpp" / "_index.md"
MEMORY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MemoryManager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave865 render tail"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-160100_post_wave865_render_tail_verified"
NEXT_HEAD = "0x00549570 CMeshRenderer__RenderMeshCore"
STRICT_PROXY = "5819/6105 = 95.32%"

TARGETS = {
    "0x0053df40": (
        "CDXEngine__RenderTexturedBeamQuad",
        "void __thiscall CDXEngine__RenderTexturedBeamQuad(void * this, float start_x, float start_y, float start_z, float start_w_or_pad, float end_x, float end_y, float end_z, float end_w_or_pad, int reserved_flags)",
        ("0x004e9fc9", "0x004ea110", "0x004ea2f0"),
        ("Wave865 render-tail static read-back", "CVBufTexture", "four vertices", "six indices"),
    ),
    "0x0053f010": (
        "CCutscene__SetTrackSlotByFlag",
        "void __thiscall CCutscene__SetTrackSlotByFlag(void * this, int track_slot, int use_primary_track)",
        ("0x0046d000", "0x0043f4f5", "0x0043f3d2", "0x0043fa0c"),
        ("Wave865 render-tail static read-back", "this+0x4cc", "this+0x4d0", "RET 0x8"),
    ),
    "0x00540c30": (
        "CDXFrontEnd__SetupRenderMatricesAndProjection",
        "void __cdecl CDXFrontEnd__SetupRenderMatricesAndProjection(void)",
        ("0x00540fbc",),
        ("Wave865 render-tail static read-back", "0x008a9788", "CParticleManager__InterpolatePositions", "CDXEngine__RenderParticleTexturePass"),
    ),
    "0x00541f50": (
        "CDXEngine__GenerateLandscapeCacheTileChunk",
        "void __thiscall CDXEngine__GenerateLandscapeCacheTileChunk(void * this, int detail_shift, void * source_cache_info, void * source_pixels, int tile_x, int tile_y, int dest_x, int dest_y, int tile_count_x, int tile_count_y, int output_stride_pixels)",
        ("0x00547975",),
        ("Wave865 render-tail static read-back", "CDXEngine__BuildLandscapeTextureCache", "this+0x10c4/0x10c8", "ARGB cache pixels"),
    ),
    "0x00542f90": (
        "CDXImposter__BuildQuadGeometry",
        "void __thiscall CDXImposter__BuildQuadGeometry(void * this, float * center_vec, float * right_vec, float * up_vec, float vertex_alpha, int reserved_14, float u0, float v0, float u1, float v1, int use_secondary_buffer)",
        ("0x0054386e",),
        ("Wave865 render-tail static read-back", "CDXEngine__RenderImposterBillboardSet", "0x008aa8b4", "0x008aa8cc"),
    ),
    "0x00544fb0": (
        "CDXLandscape__ResetWrapper",
        "void __thiscall CDXLandscape__ResetWrapper(void * this, int reset_x, int reset_y)",
        ("0x0044a11d",),
        ("Wave865 render-tail static read-back", "CEngine__ResetPos", "CDXLandscape__Reset(this)", "RET 0x8"),
    ),
    "0x005473b0": (
        "CDXEngine__InvalidateLandscapeTilesAndPatchSlots",
        "void __thiscall CDXEngine__InvalidateLandscapeTilesAndPatchSlots(void * this, int min_x, int min_y, int max_x, int max_y, int force_full_rebuild)",
        ("0x004ec218", "0x0044a6cc"),
        ("Wave865 render-tail static read-back", "0x80", "CLandscapeTexture__UpdateTileRange", "0x1000 cached patch entries"),
    ),
    "0x00547860": (
        "CDXEngine__BuildLandscapeTextureCache",
        "void __cdecl CDXEngine__BuildLandscapeTextureCache(void)",
        ("0x00544706",),
        ("Wave865 render-tail static read-back", "Building texture cache", "ps2data/LandscapeTextureCache", "DXPalletizer__Palletize"),
    ),
    "0x00549310": (
        "CDXMemoryManager__LogDebugStats",
        "void __thiscall CDXMemoryManager__LogDebugStats(void * this)",
        ("0x004f03b3", "0x004f027e"),
        ("Wave865 render-tail static read-back", "CMemoryHeap__LogStats", "0x009c3df0", "DebugTrace"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "render-tail-wave865",
    "wave865-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "important-connective-infrastructure",
    "render-tail",
}

CORE_ANCHORS = (
    TASK,
    "render-tail-wave865",
    "0x0053df40 CDXEngine__RenderTexturedBeamQuad",
    "0x0053f010 CCutscene__SetTrackSlotByFlag",
    "0x00540c30 CDXFrontEnd__SetupRenderMatricesAndProjection",
    "0x00541f50 CDXEngine__GenerateLandscapeCacheTileChunk",
    "0x00542f90 CDXImposter__BuildQuadGeometry",
    "0x00544fb0 CDXLandscape__ResetWrapper",
    "0x005473b0 CDXEngine__InvalidateLandscapeTilesAndPatchSlots",
    "0x00547860 CDXEngine__BuildLandscapeTextureCache",
    "0x00549310 CDXMemoryManager__LogDebugStats",
    "low local-evidence-density but high connective/system-importance",
    NEXT_HEAD,
    STRICT_PROXY,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime render behavior proven",
    "runtime cutscene behavior proven",
    "runtime landscape-cache behavior proven",
    "runtime imposter behavior proven",
    "runtime memory-debug behavior proven",
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


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 9,
        "pre-tags.tsv": 9,
        "pre-xrefs.tsv": 20,
        "pre-instructions.tsv": 1542,
        "pre-decompile-selected/index.tsv": 9,
        "pre-xref-site-instructions.tsv": 609,
        "post-metadata.tsv": 9,
        "post-tags.tsv": 9,
        "post-xrefs.tsv": 20,
        "post-instructions.tsv": 1542,
        "post-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = {
        (normalize_address(row["target_addr"]), normalize_address(row["from_addr"]), row["ref_type"])
        for row in read_tsv(BASE / "post-xrefs.tsv")
    }

    for address, (name, signature, expected_from_addrs, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in comment_tokens:
                require(contains_token(row.get("comment", ""), token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        for from_addr in expected_from_addrs:
            require((address, from_addr, "UNCONDITIONAL_CALL") in xrefs, f"missing xref {from_addr} -> {address}", failures)

    require(read_text(BASE / "post-decompile" / "00549310_CDXMemoryManager__LogDebugStats.c"), "missing memory decompile text", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=9 found=9 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "post-xrefs.log": "Wrote 20 rows",
        "post-instructions.log": "Wrote 1542 function-body instruction rows",
        "post-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "pre-xref-site-instructions.log": "Wrote 609 instruction rows",
        "quality-refresh.log": "total_functions=6105 commented_functions=5819",
        "queue-probe.log": "Commentless functions: 286",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave865.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave865_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "READBACK_BAD", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require(read_text(BASE / "apply.log").count("READBACK_OK:") == 9, "apply readback count mismatch", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6105, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 286, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for name in ("commentlessHighSignal", "signature", "nameConfidence"):
        require(queue["priorityQueues"][name] == [], f"{name} queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6105, "quality TSV row count mismatch", failures)
    require(commented == 5819, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5819, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x00549570", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CMeshRenderer__RenderMeshCore", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 172329863 or backup.get("totalBytes") == 172329863.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        ENGINE_DOC: (
            "Wave865 render tail",
            "render-tail-wave865",
            "0x0053df40 CDXEngine__RenderTexturedBeamQuad",
            "0x00540c30 CDXFrontEnd__SetupRenderMatricesAndProjection",
            "0x00541f50 CDXEngine__GenerateLandscapeCacheTileChunk",
            "0x005473b0 CDXEngine__InvalidateLandscapeTilesAndPatchSlots",
            "0x00547860 CDXEngine__BuildLandscapeTextureCache",
            NEXT_HEAD,
            BACKUP_PATH,
        ),
        CUTSCENE_DOC: ("Wave865 render tail", "0x0053f010 CCutscene__SetTrackSlotByFlag", BACKUP_PATH),
        DXIMPOSTER_DOC: ("Wave865 render tail", "0x00542f90 CDXImposter__BuildQuadGeometry", BACKUP_PATH),
        DXLANDSCAPE_DOC: ("Wave865 render tail", "0x00544fb0 CDXLandscape__ResetWrapper", BACKUP_PATH),
        MEMORY_DOC: ("Wave865 render tail", "0x00549310 CDXMemoryManager__LogDebugStats", BACKUP_PATH),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-render-tail-wave865") == r"py -3 tools\ghidra_render_tail_wave865_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave865 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20520 for row in attempts), "missing Wave865 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave865 render-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave865 render-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
