#!/usr/bin/env python3
"""Validate Wave1033 CDXEngine render/resource review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1033-cdxengine-render-resource-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cdxengine_render_resource_review_wave1033_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1033_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
KEMPY_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXKempyCube.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-051834_post_wave1033_cdxengine_render_resource_review_verified"

PRIMARY_TARGETS = {
    "0x0044a640": (
        "CDXEngine__SetOverlaySlotVisibilityByPlayerView",
        "void __thiscall CDXEngine__SetOverlaySlotVisibilityByPlayerView(void * this, int playerView)",
        ("CDXEngine__SetOverlaySlotsEnabledForActiveViews", "this+0x18", "playerView"),
    ),
    "0x0053d3a0": (
        "CDXEngine__ReleaseDefaultTextureAndMeshRefs",
        "void __fastcall CDXEngine__ReleaseDefaultTextureAndMeshRefs(void * this)",
        ("Wave1033 stale-comment correction", "CTexture__DecrementRefCountFromNameField", "Wave806", "this+0x4e4"),
    ),
    "0x00542a50": (
        "CDXEngine__BuildDirectionalSampleRing",
        "void __cdecl CDXEngine__BuildDirectionalSampleRing(float view_yaw_radians)",
        ("Wave598 CDXEngine/imposter head hardening", "0x008aa780", "CDXEngine__PackVec3AndDepthToSortKey"),
    ),
    "0x00544040": (
        "CDXEngine__ClearKempyCubeTextureSlots",
        "void * __fastcall CDXEngine__ClearKempyCubeTextureSlots(void * kempy_cube_resources)",
        ("Kempy cube", "zeroing five", "+0x00..+0x10"),
    ),
}

CONTEXT_TARGETS = {
    "0x0044a650": (
        "CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite",
        "void CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite(void)",
    ),
    "0x0053d3e0": ("CDXEngine__Shutdown", "void __fastcall CDXEngine__Shutdown(void * this)"),
    "0x0053d5f0": ("CDXEngine__Init", "int __fastcall CDXEngine__Init(void * this)"),
    "0x0053d6d0": ("CDXEngine__InitResources", "void __fastcall CDXEngine__InitResources(void * this)"),
    "0x00543300": (
        "CDXEngine__RenderImposterBillboardSet",
        "void __thiscall CDXEngine__RenderImposterBillboardSet(void * this, void * view_context, int alpha, int frame_index)",
    ),
    "0x005438c0": ("CDXImposter__RenderAll", "void __cdecl CDXImposter__RenderAll(void)"),
    "0x00544060": (
        "CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer",
        "void __fastcall CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer(void * kempy_cube_resources)",
    ),
    "0x005440a0": (
        "CDXEngine__InitKempyCubeTexturesAndVertexBuffer",
        "void __thiscall CDXEngine__InitKempyCubeTexturesAndVertexBuffer(void * this, int cube_index)",
    ),
    "0x005441a0": (
        "CDXEngine__InitKempyCubeResources",
        "void __thiscall CDXEngine__InitKempyCubeResources(void * this, int cube_index)",
    ),
    "0x005441b0": (
        "CDXEngine__RenderKempyCubeFaces",
        "void __fastcall CDXEngine__RenderKempyCubeFaces(void * kempy_cube_resources)",
    ),
}

DOC_TOKENS = (
    "Wave1033",
    "cdxengine-render-resource-review-wave1033",
    "0x0044a640 CDXEngine__SetOverlaySlotVisibilityByPlayerView",
    "0x0053d3a0 CDXEngine__ReleaseDefaultTextureAndMeshRefs",
    "0x00542a50 CDXEngine__BuildDirectionalSampleRing",
    "0x00544040 CDXEngine__ClearKempyCubeTextureSlots",
    "0x00544060 CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer",
    "CTexture__DecrementRefCountFromNameField",
    "supersedes older CHud__DecrementCounter9C wording",
    "635/1408 = 45.10%",
    "864/1493 = 57.87%",
    "500/500 = 100.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "two comment/tag corrections",
)

OVERCLAIMS = (
    "runtime render behavior proven",
    "runtime resource behavior proven",
    "runtime texture lifetime proven",
    "runtime shutdown behavior proven",
    "exact layout proven",
    "rebuild parity proven",
    "fully reverse-engineered",
)

CORRECTED_TAGS = {
    "cdxengine-render-resource-review-wave1033",
    "wave1033-readback-verified",
    "comment-corrected",
    "wave806-normalized",
    "texture-refcount",
}


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


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
        "metadata.tsv": 4,
        "tags.tsv": 4,
        "xrefs.tsv": 6,
        "instructions.tsv": 312,
        "decompile/index.tsv": 4,
        "context-metadata.tsv": 10,
        "context-tags.tsv": 10,
        "context-xrefs.tsv": 16,
        "context-instructions.tsv": 1113,
        "context-decompile/index.tsv": 10,
        "xref-call-site-windows.tsv": 513,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-decompile/index.tsv": 4,
        "post-context-metadata.tsv": 10,
        "post-context-tags.tsv": 10,
        "post-context-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in PRIMARY_TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in comment_tokens:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)
            if address == "0x0053d3a0":
                require("CHud__DecrementCounter9C" not in row.get("comment", ""), f"stale helper wording remains at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            if address == "0x0053d3a0":
                actual = set(tag_row.get("tags", "").split(";"))
                require(CORRECTED_TAGS.issubset(actual), f"missing correction tags at {address}: {CORRECTED_TAGS - actual}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    context_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-context-metadata.tsv")}
    context_tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-context-tags.tsv")}
    context_decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-context-decompile" / "index.tsv")}
    for address, (name, signature) in CONTEXT_TARGETS.items():
        row = context_metadata.get(address)
        require(row is not None, f"missing context metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"context name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"context metadata status mismatch at {address}", failures)
            if address == "0x00544060":
                comment = row.get("comment", "")
                for token in ("Wave1033 stale-comment correction", "CTexture__DecrementRefCountFromNameField", "Wave806", "0x008aa908"):
                    require(token in comment, f"missing context correction token at {address}: {token}", failures)
                require("CHud__DecrementCounter9C" not in comment, f"stale helper wording remains at {address}", failures)

        tag_row = context_tags.get(address)
        require(tag_row is not None, f"missing context tags at {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"context tag status mismatch at {address}", failures)
            if address == "0x00544060":
                actual = set(tag_row.get("tags", "").split(";"))
                require(CORRECTED_TAGS.issubset(actual), f"missing context correction tags at {address}: {CORRECTED_TAGS - actual}", failures)

        dec = context_decompile.get(address)
        require(dec is not None, f"missing context decompile index at {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"context decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"context decompile status mismatch at {address}", failures)

    xrefs = read_text(BASE / "xrefs.tsv")
    for token in (
        "0053e234",
        "CDXEngine__PreRender",
        "004f01b0",
        "CLTShell__ShutdownRuntimeAndReleaseResources",
        "0053e5ae",
        "CDXEngine__Render",
        "00449c53",
        "CEngine__Init",
    ):
        require(token in xrefs, f"missing xref token: {token}", failures)

    context_xrefs = read_text(BASE / "context-xrefs.tsv")
    for token in ("005e4fd0", "005e4fc8", "005e4fcc", "00449975", "0044a2ab", "0053e629"):
        require(token in context_xrefs, f"missing context xref token: {token}", failures)

    windows = read_text(BASE / "xref-call-site-windows.tsv")
    for token in ("0x0053e234", "0x004f01b0", "0x0053e5ae", "0x00449c53", "0x00544060"):
        require(token in windows, f"missing xref-call-site token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=4 found=4 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "xrefs.log": "Wrote 6 rows",
        "instructions.log": "Wrote 312 function-body instruction rows",
        "decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "context-metadata.log": "targets=10 found=10 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "context-xrefs.log": "Wrote 16 rows",
        "context-instructions.log": "Wrote 1113 function-body instruction rows",
        "context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
        "xref-call-site-windows.log": "targets=19 missing=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=11 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=11 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "post-context-metadata.log": "targets=10 found=10 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "post-context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173968263, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue_and_package(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6238, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-cdxengine-render-resource-review-wave1033")
        == r"py -3 tools\ghidra_cdxengine_render_resource_review_wave1033_probe.py --check",
        "missing Wave1033 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1033-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1033 --check",
        "missing Wave1033 aggregate package script",
        failures,
    )


def check_docs_and_ledgers(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        ENGINE_DOC,
        KEMPY_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for token in OVERCLAIMS:
            require(token not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {token}", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1033 CDXEngine render resource review" for row in ledger_rows), "missing Wave1033 ledger row", failures)
    require(
        any(row.get("task") == "Wave1033 CDXEngine render resource review" and row.get("attempt_id") == 20615 for row in attempts),
        "missing Wave1033 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue_and_package(failures)
    check_docs_and_ledgers(failures)

    if failures:
        print("Wave1033 CDXEngine render/resource review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1033 CDXEngine render/resource review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
