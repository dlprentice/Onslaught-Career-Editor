#!/usr/bin/env python3
"""Validate Wave1004 HUD render-body review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1004-hud-render-body-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_hud_render_body_review_wave1004_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1004_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
HUD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md"
POST_RENDER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "CDXEngine__PostRender.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified"

TARGETS = {
    "0x00482590": ("CHud__RenderTargetIndicatorOverlay", "void __thiscall CHud__RenderTargetIndicatorOverlay(void * this)"),
    "0x00483530": ("CHud__RenderControllerSlotStatusPanel", "void __thiscall CHud__RenderControllerSlotStatusPanel(void * this)"),
    "0x00484340": ("CHud__RenderTargetMarkers3D", "void __thiscall CHud__RenderTargetMarkers3D(void * this)"),
    "0x00484c50": ("CHud__RenderTacticalRadarContacts", "void __thiscall CHud__RenderTacticalRadarContacts(void * this)"),
    "0x004857e0": ("HudOverlay__DrawSpriteQuad", "void __cdecl HudOverlay__DrawSpriteQuad(float x, float y, void * texture, float argb_tint_bits)"),
    "0x00485830": ("CHud__SelectMarkerTextureIndexByUnitFlags", "int __thiscall CHud__SelectMarkerTextureIndexByUnitFlags(void * this, void * unit)"),
    "0x004858d0": ("CHud__RenderObjectiveProgressGaugeAndHeadingNeedle", "void __thiscall CHud__RenderObjectiveProgressGaugeAndHeadingNeedle(void * this)"),
    "0x00485d50": ("CHud__RenderObjectiveStatusPanel", "void __thiscall CHud__RenderObjectiveStatusPanel(void * this)"),
    "0x00486940": ("CHud__RenderObjectiveSlotFillPanel", "void __thiscall CHud__RenderObjectiveSlotFillPanel(void * this)"),
    "0x00486e00": ("CHud__RenderWorldTargetSprites", "void __thiscall CHud__RenderWorldTargetSprites(void * this)"),
    "0x004879e0": ("CHud__RenderOverlayForViewpoint", "void __thiscall CHud__RenderOverlayForViewpoint(void * this, void * viewpoint, int viewpoint_index, float unused_overlay_param)"),
    "0x00487bc0": ("CHud__RenderOverlay", "void __thiscall CHud__RenderOverlay(void * this)"),
    "0x00487d10": ("CHud__RenderBattleline", "void __thiscall CHud__RenderBattleline(void * this, void * viewport)"),
    "0x00488090": ("CHud__RenderActiveHudComponentPass", "void __thiscall CHud__RenderActiveHudComponentPass(void * this)"),
    "0x004881e0": ("CHud__ResolveOverlaySlotRenderMode", "int __thiscall CHud__ResolveOverlaySlotRenderMode(void * this, int slot_index)"),
}

CONTEXT_TARGETS = {
    "0x0053ecc0": ("CDXEngine__PostRender", "int __thiscall CDXEngine__PostRender(void * this, void * viewport)"),
    "0x00482050": ("CHud__PromotePendingHudComponent", "void __thiscall CHud__PromotePendingHudComponent(void * this)"),
    "0x00482090": ("HudRenderState__ApplyOverlaySpriteState", "void __cdecl HudRenderState__ApplyOverlaySpriteState(void)"),
    "0x0044a0d0": ("CEngine__SelectViewpoint", "void __thiscall CEngine__SelectViewpoint(void * this, int viewpoint)"),
    "0x0053cd30": ("CDXCompass__RenderWorldSpaceOverlay", "void __thiscall CDXCompass__RenderWorldSpaceOverlay(void * this, void * battleEngineContext)"),
    "0x0053c510": ("CDXCompass__UpdateDynamicOverlayTexture", "void __thiscall CDXCompass__UpdateDynamicOverlayTexture(void * this, void * battleEngineContext)"),
    "0x00427210": ("CDXCompass__Render", "void __thiscall CDXCompass__Render(void * this, void * battleEngineContext)"),
}

DOC_TOKENS = (
    "Wave1004",
    "hud-render-body-review-wave1004",
    "0x00482590 CHud__RenderTargetIndicatorOverlay",
    "0x00484c50 CHud__RenderTacticalRadarContacts",
    "0x004857e0 HudOverlay__DrawSpriteQuad",
    "0x004879e0 CHud__RenderOverlayForViewpoint",
    "0x00487bc0 CHud__RenderOverlay",
    "0x00487d10 CHud__RenderBattleline",
    "0x00488090 CHud__RenderActiveHudComponentPass",
    "0x004881e0 CHud__ResolveOverlaySlotRenderMode",
    "0x0053ecc0 CDXEngine__PostRender",
    "485/1408 = 34.45%",
    "654/1478 = 44.25%",
    "380/500 = 76.00%",
    "6223/6223 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime hud behavior proven",
    "runtime render behavior proven",
    "exact source-body identity proven",
    "exact source-layout identity proven",
    "exact layout proven",
    "rebuild parity proven",
)


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


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    if token in text or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\\\\\") in text:
        return True
    return token.replace("\\\\", "\\") in text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 15,
        "pre-tags.tsv": 15,
        "pre-xrefs.tsv": 30,
        "pre-instructions.tsv": 6350,
        "pre-decompile/index.tsv": 15,
        "context-metadata.tsv": 7,
        "context-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "pre-metadata.tsv")
    tags = read_tsv(BASE / "pre-tags.tsv")
    decompile_index = read_tsv(BASE / "pre-decompile" / "index.tsv")

    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require("CHud" in comment or "HUD" in comment, f"metadata comment missing HUD token {address}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"tags missing {address}", failures)
        if tag_row:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            for tag in ("static-reaudit", "retail-binary-evidence", "comment-hardened", "signature-hardened"):
                require(tag in actual_tags, f"missing tag {address}: {tag}", failures)
            require("hud" in actual_tags, f"missing hud tag {address}", failures)

    context = read_tsv(BASE / "context-metadata.tsv")
    context_index = read_tsv(BASE / "context-decompile" / "index.tsv")
    for address, (name, signature) in CONTEXT_TARGETS.items():
        row = row_by_address(context, address)
        require(row is not None, f"context metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"context status mismatch {address}", failures)
        dec = row_by_address(context_index, address)
        require(dec is not None, f"context decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"context decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"context decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"context decompile status mismatch {address}", failures)

    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    expected_xrefs = (
        ("0x00482590", "0x00487b72", "UNCONDITIONAL_CALL"),
        ("0x00483530", "0x00487b8a", "UNCONDITIONAL_CALL"),
        ("0x00484340", "0x00487b91", "UNCONDITIONAL_CALL"),
        ("0x00484c50", "0x00487bb2", "UNCONDITIONAL_CALL"),
        ("0x004858d0", "0x00487b98", "UNCONDITIONAL_CALL"),
        ("0x00485d50", "0x00487b9f", "UNCONDITIONAL_CALL"),
        ("0x00486940", "0x00487ba6", "UNCONDITIONAL_CALL"),
        ("0x00486e00", "0x00487b6b", "UNCONDITIONAL_CALL"),
        ("0x004879e0", "0x00487c57", "UNCONDITIONAL_CALL"),
        ("0x00487bc0", "0x0053ed01", "UNCONDITIONAL_CALL"),
        ("0x00487d10", "0x0053ed79", "UNCONDITIONAL_CALL"),
        ("0x00488090", "0x0053ef26", "UNCONDITIONAL_CALL"),
        ("0x004881e0", "0x0053d0f3", "UNCONDITIONAL_CALL"),
    )
    for target, source, ref_type in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == target
                and normalize_address(row.get("from_addr", "")) == source
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"missing xref {source} -> {target} {ref_type}",
            failures,
        )
    require(sum(1 for row in xrefs if normalize_address(row.get("target_addr", "")) == "0x004857e0") == 7, "sprite helper xref count mismatch", failures)
    require(sum(1 for row in xrefs if normalize_address(row.get("target_addr", "")) == "0x00485830") == 4, "marker selector xref count mismatch", failures)

    overlay = read_text(BASE / "pre-decompile" / "004879e0_CHud__RenderOverlayForViewpoint.c")
    for token in (
        "CHud__RenderWorldTargetSprites",
        "CHud__RenderTargetIndicatorOverlay",
        "CHud__RenderControllerSlotStatusPanel",
        "CHud__RenderTargetMarkers3D",
        "CHud__RenderObjectiveProgressGaugeAndHeadingNeedle",
        "CHud__RenderObjectiveStatusPanel",
        "CHud__RenderObjectiveSlotFillPanel",
        "CHud__RenderTacticalRadarContacts",
    ):
        require(token in overlay, f"overlay dispatcher missing token: {token}", failures)

    tactical = read_text(BASE / "pre-decompile" / "00484c50_CHud__RenderTacticalRadarContacts.c")
    for token in ("HudOverlay__DrawSpriteQuad", "CHud__SelectMarkerTextureIndexByUnitFlags"):
        require(token in tactical, f"tactical radar decompile missing token: {token}", failures)

    post_render = read_text(BASE / "context-decompile" / "0053ecc0_CDXEngine__PostRender.c")
    for token in (
        "CHud__RenderOverlay(&DAT_008aa4e8)",
        "CHud__RenderBattleline(&DAT_008aa4e8",
        "CHud__RenderActiveHudComponentPass(&DAT_008aa4e8)",
        "CHud__PromotePendingHudComponent(&DAT_008aa4e8)",
    ):
        require(token in post_render, f"PostRender decompile missing token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "pre-metadata.log": ("targets=15 found=15 missing=0", "REPORT: Save succeeded"),
        "pre-tags.log": ("ExportFunctionTagsByAddress complete: rows=15 missing=0", "REPORT: Save succeeded"),
        "pre-xrefs.log": ("Wrote 30 rows", "REPORT: Save succeeded"),
        "pre-instructions.log": ("Wrote 6350 function-body instruction rows", "targets=15 missing=0", "REPORT: Save succeeded"),
        "pre-decompile.log": ("targets=15 dumped=15 missing=0 failed=0", "REPORT: Save succeeded"),
        "context-metadata.log": ("targets=7 found=7 missing=0", "REPORT: Save succeeded"),
        "context-decompile.log": ("targets=7 dumped=7 missing=0 failed=0", "REPORT: Save succeeded"),
    }
    for relative, tokens in expected_log_tokens.items():
        text = read_text(BASE / relative)
        for token in tokens:
            require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"bad log token {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173869959 or backup.get("totalBytes") == 173869959.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = (
        NOTE,
        RECHECK_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        HUD_DOC,
        POST_RENDER_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-hud-render-body-review-wave1004")
        == r"py -3 tools\ghidra_hud_render_body_review_wave1004_probe.py --check",
        "missing Wave1004 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1004-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1004 --check",
        "missing Wave1004 recheck package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6223, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param mismatch", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1004 HUD render-body review" for row in ledger_rows), "missing Wave1004 ledger row", failures)
    require(any(row.get("task") == "Wave1004 HUD render-body review" and row.get("attempt_id") == 20586 for row in attempts), "missing Wave1004 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1004 HUD render-body review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1004 HUD render-body review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
