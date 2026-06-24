#!/usr/bin/env python3
"""Validate Wave1096 CRenderQueue core/multipass read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1096-crenderqueue-core-multipass-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_crenderqueue_core_multipass_review_wave1096_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1096_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260604-174618_post_wave1096_crenderqueue_core_multipass_review_verified"
WAVE_TAG = "crenderqueue-core-multipass-review-wave1096"

TARGETS = {
    "0x005515a0": (
        "CDXEngine__InitConsoleVar_UseRenderQueue",
        "void __fastcall CDXEngine__InitConsoleVar_UseRenderQueue(void * storage)",
        ("Wave870", "cg_userenderqueue", "CGame__Init"),
    ),
    "0x005515e0": (
        "CRenderQueueBucket__RenderAndRecycle",
        "void __thiscall CRenderQueueBucket__RenderAndRecycle(void * this, void * bucket_set, int bucket_index)",
        ("Wave870", "bucket-linked", "CEngine__DrawIndexedPrimitives"),
    ),
    "0x00551920": (
        "CRenderQueue__BeginFrame",
        "void __fastcall CRenderQueue__BeginFrame(void * queue)",
        ("Wave870", "CDXEngine__Render", "CRenderQueueBucket__RenderAndRecycle"),
    ),
    "0x00551f20": (
        "CRenderQueue__ctor",
        "void * __fastcall CRenderQueue__ctor(void * this)",
        ("Wave870", "active-reader arrays", "CRenderQueue vtable"),
    ),
    "0x00551fe0": (
        "CRenderQueue__dtor",
        "void __fastcall CRenderQueue__dtor(void * this)",
        ("Wave870", "CGenericActiveReader__dtor", "DeviceObject__dtor_body"),
    ),
    "0x00552410": (
        "CRenderQueue__ResetOrCreateField6C0Resource",
        "int __fastcall CRenderQueue__ResetOrCreateField6C0Resource(void * this)",
        ("Wave872", "0x005e5134", "this+0x6c0"),
    ),
    "0x00552470": (
        "CRenderQueue__ReleaseField6C0Resource",
        "int __fastcall CRenderQueue__ReleaseField6C0Resource(void * this)",
        ("Wave872", "0x005e5138", "resource cleanup"),
    ),
    "0x005524a0": (
        "CRenderQueue__UpdateViewVectorAndMatrix",
        "void __thiscall CRenderQueue__UpdateViewVectorAndMatrix(void * this, float x, float y, float z, int flags)",
        ("Wave872", "CEngine__SetupLights", "0x009c7550"),
    ),
    "0x005526c0": (
        "CRenderQueue__InsertSortedByDepth",
        "void __thiscall CRenderQueue__InsertSortedByDepth(void * this, void * item, float depth)",
        ("Wave870", "CVBufTexture__RenderDynamicUnitPass", "depth array"),
    ),
    "0x00552740": (
        "CRenderQueue__RecycleInactiveItems",
        "void __fastcall CRenderQueue__RecycleInactiveItems(void * this)",
        ("Wave870", "free-entry pointer list", "DAT_00652230"),
    ),
    "0x00552800": (
        "CRenderQueue__MergePendingItems",
        "void __fastcall CRenderQueue__MergePendingItems(void * this)",
        ("Wave870", "pending reader slots", "CGenericActiveReader__SetReader"),
    ),
    "0x005528b0": (
        "CRenderQueue__RenderAll",
        "void __fastcall CRenderQueue__RenderAll(void * this)",
        ("Wave870", "CFastVB__RenderTriangleStripImmediate", "CDXEngine__SetGlobalTintColorOpaque"),
    ),
    "0x00553960": (
        "CRenderQueue__RenderMultipassLayerA",
        "void __fastcall CRenderQueue__RenderMultipassLayerA(void * this)",
        ("Wave873", "CDXLandscape__RenderTileRange", "0x009c7550"),
    ),
    "0x00554170": (
        "CRenderQueue__RenderMultipassLayerB",
        "void __fastcall CRenderQueue__RenderMultipassLayerB(void * this)",
        ("Wave873", "D3D device draw slot", "0x009c7550"),
    ),
    "0x005545d0": (
        "CRenderQueue__BuildProjectedSprites",
        "void __thiscall CRenderQueue__BuildProjectedSprites(void * this, void * unit)",
        ("Wave873", "CVBufTexture__RenderDynamicUnitPass", "CStaticShadows__SampleShadowHeightBilinear"),
    ),
    "0x00554750": (
        "CRenderQueue__EmitBillboardStrip",
        "void __thiscall CRenderQueue__EmitBillboardStrip(void * this, float x, float y, int z_bits, int w_bits, float scale, int count)",
        ("Wave873", "CVBufTexture__AddVertices", "CVBufTexture__AddIndices"),
    ),
    "0x00554df0": (
        "CRenderQueue__RenderVBufTextureWithStateToggle",
        "void __fastcall CRenderQueue__RenderVBufTextureWithStateToggle(void * this)",
        ("Wave873", "CVBufTexture__Render", "reset_after_render"),
    ),
}

COMMON_DOC_TOKENS = (
    "Wave1096",
    WAVE_TAG,
    "0x005515a0 CDXEngine__InitConsoleVar_UseRenderQueue",
    "0x005515e0 CRenderQueueBucket__RenderAndRecycle",
    "0x00551920 CRenderQueue__BeginFrame",
    "0x005528b0 CRenderQueue__RenderAll",
    "0x00553960 CRenderQueue__RenderMultipassLayerA",
    "0x00554170 CRenderQueue__RenderMultipassLayerB",
    "0x005545d0 CRenderQueue__BuildProjectedSprites",
    "0x00554750 CRenderQueue__EmitBillboardStrip",
    "0x00554df0 CRenderQueue__RenderVBufTextureWithStateToggle",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime rendering behavior proven",
    "runtime render output proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-body identity proven",
    "exact source layout identity proven",
)


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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 17,
        "tags.tsv": 17,
        "xrefs.tsv": 22,
        "instructions.tsv": 3087,
        "decompile/index.tsv": 17,
    }
    for relative, expected in expected_counts.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == expected, f"{relative} row count mismatch: {len(rows)} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "metadata.log": "targets=17 found=17 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "xrefs.log": "Wrote 22 rows",
        "instructions.log": "Wrote 3087 function-body instruction rows",
        "decompile.log": "targets=17 dumped=17 missing=0 failed=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (175541127, 175541127.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        ENGINE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
        AGENTS,
    ]
    for path in docs:
        text = read_text(path)
        for token in COMMON_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-crenderqueue-core-multipass-review-wave1096")
        == r"py -3 tools\ghidra_crenderqueue_core_multipass_review_wave1096_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1096-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1096 --check",
        "missing aggregate package script",
        failures,
    )

    progress = read_json(PROGRESS_JSON)
    require(progress["latestWave"]["wave"] == "Wave1096 CRenderQueue core multipass review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["status"] in {"validation_pending", "validated_pending_commit", "committed"}, "progress status mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP_PATH, "progress backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6410, "progress total mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["completed"] == 1560, "expanded count mismatch", failures)
    require(progress["post100Reaudit"]["wave911Focused"]["completed"] == 812, "wave911 focused mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1096 CRenderQueue core multipass review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1096 CRenderQueue core multipass review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
