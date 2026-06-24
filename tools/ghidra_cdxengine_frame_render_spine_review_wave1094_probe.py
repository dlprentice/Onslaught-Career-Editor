#!/usr/bin/env python3
"""Validate Wave1094 CDXEngine frame/render spine review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1094-cdxengine-frame-render-spine-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cdxengine_frame_render_spine_review_wave1094_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1094_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260604-163255_post_wave1094_cdxengine_frame_render_spine_review_verified"
WAVE_TAG = "cdxengine-frame-render-spine-review-wave1094"

PRIMARY_TARGETS = {
    "0x0053e220": (
        "CDXEngine__PreRender",
        "int __fastcall CDXEngine__PreRender(void * this, void * viewport)",
        ("Wave1094 static read-back", "0x0046e5c3", "per-frame engine state"),
    ),
    "0x0053e2e0": (
        "CDXEngine__Render",
        "int __thiscall CDXEngine__Render(void * this, uint viewpoint)",
        ("Wave1094 static read-back", "0x0046e68b", "render queue", "water", "particles"),
    ),
    "0x0053ecc0": (
        "CDXEngine__PostRender",
        "int __thiscall CDXEngine__PostRender(void * this, void * viewport)",
        ("Wave1094 static read-back", "0x0046e892", "CHud__RenderBattleline"),
    ),
    "0x0053bb50": (
        "CDXEngine__RenderOptionalFullscreenEffectPass",
        "void __fastcall CDXEngine__RenderOptionalFullscreenEffectPass(void * this)",
        ("Wave591", "optional fullscreen/effect path"),
    ),
    "0x005441b0": (
        "CDXEngine__RenderKempyCubeFaces",
        "void __fastcall CDXEngine__RenderKempyCubeFaces(void * kempy_cube_resources)",
        ("Wave600", "Kempy cube"),
    ),
    "0x0054f7e0": (
        "CDXEngine__RenderParticleTexturePass",
        "void __fastcall CDXEngine__RenderParticleTexturePass(void * particle_bundle)",
        ("Wave612", "particle bundle"),
    ),
    "0x004b82b0": (
        "CDXEngine__RenderBattleLinePulseSprites",
        "void __thiscall CDXEngine__RenderBattleLinePulseSprites(void * this, int screen_x, float screen_y, int viewport_height)",
        ("Wave450", "battle-line pulse"),
    ),
    "0x00542a50": (
        "CDXEngine__BuildDirectionalSampleRing",
        "void __cdecl CDXEngine__BuildDirectionalSampleRing(float view_yaw_radians)",
        ("Wave598", "sample-ring"),
    ),
    "0x00441490": (
        "CDXEngine__UpdateWrappedThingPositionsAndDistance",
        "void __cdecl CDXEngine__UpdateWrappedThingPositionsAndDistance(float camera_x, float camera_y, float camera_z)",
        ("Wave364", "wraps positions"),
    ),
    "0x004903a0": (
        "CDXEngine__BuildOverlaySlotFromSortedEntry",
        "void __thiscall CDXEngine__BuildOverlaySlotFromSortedEntry(void * this, int slot_index, int candidate_index)",
        ("Wave425", "active overlay slot"),
    ),
    "0x004905f0": (
        "CDXEngine__UpdateOverlaySlotsFromCandidateList",
        "void __fastcall CDXEngine__UpdateOverlaySlotsFromCandidateList(void * burst_overlay_state)",
        ("Wave425", "Sort__QuickSortGeneric"),
    ),
    "0x00490780": (
        "CDXEngine__SetOverlaySlotsEnabledForActiveViews",
        "void __thiscall CDXEngine__SetOverlaySlotsEnabledForActiveViews(void * this, int enabled)",
        ("Wave425", "overlay enable flags"),
    ),
}

NORMALIZED_TARGETS = {
    "0x0053e220",
    "0x0053e2e0",
    "0x0053ecc0",
    "0x0046e460",
}

CONTEXT_TARGETS = {
    "0x0046e460": (
        "CGame__Render",
        "void __thiscall CGame__Render(void * this, int num_renders)",
        ("Wave1094 static read-back", "CGame__MainLoop", "CDXEngine__PreRender"),
    ),
    "0x0053d5f0": ("CDXEngine__Init", "int __fastcall CDXEngine__Init(void * this)", ("Wave592", "CGame__Init")),
    "0x0053d6d0": ("CDXEngine__InitResources", "void __fastcall CDXEngine__InitResources(void * this)", ("Wave592", "CGame__RunLevel")),
    "0x0053d3e0": ("CDXEngine__Shutdown", "void __fastcall CDXEngine__Shutdown(void * this)", ("Wave592", "CEngine__Shutdown")),
    "0x0053d3a0": ("CDXEngine__ReleaseDefaultTextureAndMeshRefs", "void __fastcall CDXEngine__ReleaseDefaultTextureAndMeshRefs(void * this)", ("Wave1033", "CTexture__DecrementRefCountFromNameField")),
    "0x004685f0": ("CFrontEnd__RenderStart", "int __thiscall CFrontEnd__RenderStart(void * this)", ("Wave467", "RenderStart")),
    "0x004685a0": ("CFrontEnd__UpdateCamera", "void __thiscall CFrontEnd__UpdateCamera(void * this)", ("Wave467", "UpdateCamera")),
    "0x004879e0": ("CHud__RenderOverlayForViewpoint", "void __thiscall CHud__RenderOverlayForViewpoint(void * this, void * viewpoint, int viewpoint_index, float unused_overlay_param)", ("Wave410", "overlay")),
    "0x00487d10": ("CHud__RenderBattleline", "void __thiscall CHud__RenderBattleline(void * this, void * viewport)", ("Wave412", "RenderBattleline")),
    "0x00546490": ("CDXLandscape__RenderShadowMap", "bool __thiscall CDXLandscape__RenderShadowMap(void * this, int record_index)", ("Wave604", "shadow-map")),
    "0x0055b6c0": ("CWaterRenderSystem__RenderMainPass", "void __fastcall CWaterRenderSystem__RenderMainPass(void * this)", ("Wave877", "water render")),
    "0x00551920": ("CRenderQueue__BeginFrame", "void __fastcall CRenderQueue__BeginFrame(void * queue)", ("Wave870", "frame-phase identity")),
    "0x005528b0": ("CRenderQueue__RenderAll", "void __fastcall CRenderQueue__RenderAll(void * this)", ("Wave870", "top-level queue render pass")),
    "0x00553960": ("CRenderQueue__RenderMultipassLayerA", "void __fastcall CRenderQueue__RenderMultipassLayerA(void * this)", ("Wave873", "render multipass")),
    "0x00554170": ("CRenderQueue__RenderMultipassLayerB", "void __fastcall CRenderQueue__RenderMultipassLayerB(void * this)", ("Wave873", "render multipass")),
    "0x0044a020": ("CEngine__SetViewpoint", "void __thiscall CEngine__SetViewpoint(void * this, int viewpoint, void * camera, void * viewport, void * player)", ("Saved signature/comment/tag hardening", "SetViewpoint")),
    "0x0044a2d0": ("CEngine__SetupLights", "void CEngine__SetupLights(void)", ("Saved owner/comment/tag correction", "SetupLights-style body")),
}

DOC_TOKENS = (
    "Wave1094",
    WAVE_TAG,
    "0x0053e220 CDXEngine__PreRender",
    "0x0053e2e0 CDXEngine__Render",
    "0x0053ecc0 CDXEngine__PostRender",
    "0x0046e460 CGame__Render",
    "0x0053bb50 CDXEngine__RenderOptionalFullscreenEffectPass",
    "0x005441b0 CDXEngine__RenderKempyCubeFaces",
    "0x0054f7e0 CDXEngine__RenderParticleTexturePass",
    "0x00542a50 CDXEngine__BuildDirectionalSampleRing",
    "0x00551920 CRenderQueue__BeginFrame",
    "0x005528b0 CRenderQueue__RenderAll",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "comment/tag normalization",
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
    "exact source-layout identity proven",
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


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_metadata_group(
    metadata_path: Path,
    tags_path: Path,
    decompile_path: Path,
    targets: dict[str, tuple[str, str, tuple[str, ...]]],
    failures: list[str],
) -> None:
    metadata = {normalize_address(row["address"]): row for row in read_tsv(metadata_path)}
    tags = {normalize_address(row["address"]): row for row in read_tsv(tags_path)}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(decompile_path)}

    for address, (name, signature, comment_tokens) in targets.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)
            if address in NORMALIZED_TARGETS:
                require("Wave1094 static read-back" in comment, f"missing Wave1094 comment at {address}", failures)
                require("runtime" in comment and "rebuild parity" in comment, f"missing boundary text at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            require("static-reaudit" in tag_text, f"missing static-reaudit tag at {address}", failures)
            require("retail-binary-evidence" in tag_text, f"missing retail-binary-evidence tag at {address}", failures)
            if address in NORMALIZED_TARGETS:
                for token in (WAVE_TAG, "wave1094-readback-verified", "comment-hardened", "tag-normalized", "frame-render-spine"):
                    require(token in tag_text, f"missing Wave1094 tag at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile at {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 12,
        "primary-tags.tsv": 12,
        "primary-xrefs.tsv": 17,
        "primary-instructions.tsv": 2340,
        "primary-decompile/index.tsv": 12,
        "context-metadata.tsv": 17,
        "context-tags.tsv": 17,
        "context-xrefs.tsv": 36,
        "context-instructions.tsv": 5415,
        "context-decompile/index.tsv": 17,
        "post-primary-metadata.tsv": 12,
        "post-primary-tags.tsv": 12,
        "post-primary-xrefs.tsv": 17,
        "post-primary-instructions.tsv": 2340,
        "post-primary-decompile/index.tsv": 12,
        "post-context-metadata.tsv": 17,
        "post-context-tags.tsv": 17,
        "post-context-xrefs.tsv": 36,
        "post-context-instructions.tsv": 5415,
        "post-context-decompile/index.tsv": 17,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    check_metadata_group(
        BASE / "post-primary-metadata.tsv",
        BASE / "post-primary-tags.tsv",
        BASE / "post-primary-decompile" / "index.tsv",
        PRIMARY_TARGETS,
        failures,
    )
    check_metadata_group(
        BASE / "post-context-metadata.tsv",
        BASE / "post-context-tags.tsv",
        BASE / "post-context-decompile" / "index.tsv",
        CONTEXT_TARGETS,
        failures,
    )

    primary_xrefs = read_tsv(BASE / "post-primary-xrefs.tsv")
    context_xrefs = read_tsv(BASE / "post-context-xrefs.tsv")
    xref_pairs = {
        (normalize_address(row["target_addr"]), row.get("from_function", ""))
        for row in primary_xrefs + context_xrefs
    }
    for address, caller in (
        ("0x0053e220", "CGame__Render"),
        ("0x0053e2e0", "CGame__Render"),
        ("0x0053ecc0", "CGame__Render"),
        ("0x0053bb50", "CDXEngine__Render"),
        ("0x005441b0", "CDXEngine__Render"),
        ("0x0054f7e0", "CDXEngine__Render"),
        ("0x00542a50", "CDXEngine__Render"),
        ("0x00441490", "CDXEngine__Render"),
        ("0x004905f0", "CDXEngine__Render"),
        ("0x004903a0", "CDXEngine__UpdateOverlaySlotsFromCandidateList"),
        ("0x0046e460", "CGame__MainLoop"),
        ("0x00487d10", "CDXEngine__PostRender"),
        ("0x0055b6c0", "CDXEngine__Render"),
        ("0x00551920", "CDXEngine__Render"),
        ("0x005528b0", "CDXEngine__Render"),
        ("0x00553960", "CDXEngine__Render"),
        ("0x00554170", "CDXEngine__Render"),
        ("0x0044a020", "CGame__Render"),
        ("0x0044a2d0", "CDXEngine__Render"),
    ):
        require((address, caller) in xref_pairs, f"missing xref {caller} -> {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-primary-metadata.log": "targets=12 found=12 missing=0",
        "post-primary-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "post-primary-xrefs.log": "Wrote 17 rows",
        "post-primary-instructions.log": "Wrote 2340 function-body instruction rows",
        "post-primary-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-context-metadata.log": "targets=17 found=17 missing=0",
        "post-context-tags.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "post-context-xrefs.log": "Wrote 36 rows",
        "post-context-instructions.log": "Wrote 5415 function-body instruction rows",
        "post-context-decompile.log": "targets=17 dumped=17 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply did not report save succeeded", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 175541127 or backup.get("totalBytes") == 175541127.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        ENGINE_DOC,
        BACKLOG,
        TRACKING_STATE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
        AGENTS,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    progress = read_json(PROGRESS_JSON)
    require(progress["latestWave"]["wave"] == "Wave1094 CDXEngine frame render spine review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["status"] in {"validation_pending", "validated_pending_commit", "committed"}, "progress status mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP_PATH, "progress backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6410, "progress total mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["completed"] == 1560, "expanded count mismatch", failures)
    require(progress["post100Reaudit"]["wave911Focused"]["completed"] == 812, "wave911 focused mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-cdxengine-frame-render-spine-review-wave1094") == r"py -3 tools\ghidra_cdxengine_frame_render_spine_review_wave1094_probe.py --check", "missing focused package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1094-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1094 --check", "missing aggregate package script", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1094 CDXEngine frame render spine review" for row in ledger), "missing Wave1094 ledger row", failures)
    require(any(row.get("task") == "Wave1094 CDXEngine frame render spine review" and row.get("attempt_id") == 20674 for row in attempts), "missing Wave1094 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave1094 CDXEngine frame render spine review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1094 CDXEngine frame render spine review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
