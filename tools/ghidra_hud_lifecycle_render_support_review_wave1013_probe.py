#!/usr/bin/env python3
"""Validate Wave1013 HUD lifecycle/render-support read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1013-hud-lifecycle-render-support-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_hud_lifecycle_render_support_review_wave1013_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
HUD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md"
DXCOMPASS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXCompass.cpp" / "_index.md"
IBUFFER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ibuffer.cpp" / "_index.md"
LEVEL_BRIEFING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "LevelBriefingLog.cpp" / "_index.md"
POST_RENDER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "CDXEngine__PostRender.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified"

TARGETS = {
    "0x00481450": ("CHud__Init", "void __thiscall CHud__Init(void * this)"),
    "0x004815c0": ("CHud__Reset", "void __thiscall CHud__Reset(void * this)"),
    "0x00481650": ("CHud__LoadTextures", "void __thiscall CHud__LoadTextures(void * this)"),
    "0x00481af0": ("CHud__PostLoadProcess", "int __thiscall CHud__PostLoadProcess(void * this)"),
    "0x00481f40": ("CHud__SetHudComponent", "void __thiscall CHud__SetHudComponent(void * this, char * component_name, byte slot_flag)"),
    "0x004821e0": ("CDXCompass__ApplyRenderStateAdditive", "void __cdecl CDXCompass__ApplyRenderStateAdditive(void)"),
    "0x00483530": ("CHud__RenderControllerSlotStatusPanel", "void __thiscall CHud__RenderControllerSlotStatusPanel(void * this)"),
    "0x00484340": ("CHud__RenderTargetMarkers3D", "void __thiscall CHud__RenderTargetMarkers3D(void * this)"),
    "0x004858d0": ("CHud__RenderObjectiveProgressGaugeAndHeadingNeedle", "void __thiscall CHud__RenderObjectiveProgressGaugeAndHeadingNeedle(void * this)"),
    "0x00486940": ("CHud__RenderObjectiveSlotFillPanel", "void __thiscall CHud__RenderObjectiveSlotFillPanel(void * this)"),
    "0x00486e00": ("CHud__RenderWorldTargetSprites", "void __thiscall CHud__RenderWorldTargetSprites(void * this)"),
    "0x00488330": ("CIBuffer__CreateConfigured", "int __thiscall CIBuffer__CreateConfigured(void * this, int size_bytes, int usage_flags, int index_format, int buffer_type)"),
    "0x004885e0": ("CIBuffer__LockDirect", "int __thiscall CIBuffer__LockDirect(void * this, void * * out_data)"),
    "0x0048f540": ("CLevelBriefingLog__ctor", "void * __thiscall CLevelBriefingLog__ctor(void * this)"),
    "0x0048f5a0": ("CLevelBriefingLog__scalar_deleting_dtor", "void * __thiscall CLevelBriefingLog__scalar_deleting_dtor(void * this, byte flags)"),
    "0x0048f5c0": ("CLevelBriefingLog__dtor", "void __thiscall CLevelBriefingLog__dtor(void * this)"),
}

CONTEXT_TARGETS = {
    "0x00481400": ("CHud__ctor_base", "void * __thiscall CHud__ctor_base(void * this)"),
    "0x00481b00": ("CHud__ShutDown", "void __thiscall CHud__ShutDown(void * this)"),
    "0x00482050": ("CHud__PromotePendingHudComponent", "void __thiscall CHud__PromotePendingHudComponent(void * this)"),
    "0x00482090": ("HudRenderState__ApplyOverlaySpriteState", "void __cdecl HudRenderState__ApplyOverlaySpriteState(void)"),
    "0x00487bc0": ("CHud__RenderOverlay", "void __thiscall CHud__RenderOverlay(void * this)"),
    "0x0048f620": ("CLevelBriefingLog__Render", "void __thiscall CLevelBriefingLog__Render(void * this, void * viewport)"),
    "0x0053bd60": ("CDXCompass__InitFields", "void * __fastcall CDXCompass__InitFields(void * this)"),
    "0x0053ecc0": ("CDXEngine__PostRender", "int __thiscall CDXEngine__PostRender(void * this, void * viewport)"),
    "0x00427210": ("CDXCompass__Render", "void __thiscall CDXCompass__Render(void * this, void * battleEngineContext)"),
}

DOC_TOKENS = (
    "Wave1013",
    "hud-lifecycle-render-support-review-wave1013",
    "0x00481450 CHud__Init",
    "0x004815c0 CHud__Reset",
    "0x00481650 CHud__LoadTextures",
    "0x00481af0 CHud__PostLoadProcess",
    "0x00481f40 CHud__SetHudComponent",
    "0x004821e0 CDXCompass__ApplyRenderStateAdditive",
    "0x00488330 CIBuffer__CreateConfigured",
    "0x004885e0 CIBuffer__LockDirect",
    "0x0048f540 CLevelBriefingLog__ctor",
    "0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor",
    "0x0048f5c0 CLevelBriefingLog__dtor",
    "505/1408 = 35.87%",
    "718/1493 = 48.09%",
    "420/500 = 84.00%",
    "6238/6238 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime hud behavior proven",
    "runtime compass behavior proven",
    "runtime briefing-log behavior proven",
    "runtime index-buffer behavior proven",
    "exact source-body identity proven",
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


def rows_by(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(field, "")): row for row in rows}


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    variants = {
        token,
        token.replace("\\", "\\\\"),
        token.replace("\\", "\\\\\\\\"),
        token.replace("\\\\", "\\"),
    }
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return any(variant in text or variant in normalized for variant in variants)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 16,
        "pre-tags.tsv": 16,
        "pre-xrefs.tsv": 23,
        "pre-instructions.tsv": 3829,
        "pre-decompile/index.tsv": 16,
        "context-metadata.tsv": 9,
        "context-xrefs.tsv": 23,
        "context-instructions.tsv": 2075,
        "context-decompile/index.tsv": 9,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = rows_by(read_tsv(BASE / "pre-metadata.tsv"), "address")
    tags = rows_by(read_tsv(BASE / "pre-tags.tsv"), "address")
    decompile = rows_by(read_tsv(BASE / "pre-decompile" / "index.tsv"), "address")

    for address, (name, signature) in TARGETS.items():
        key = normalize_address(address)
        row = metadata.get(key)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            require("Static retail evidence only" in comment or "Static retail-binary evidence only" in comment, f"comment boundary missing {address}", failures)

        tag_row = tags.get(key)
        require(tag_row is not None, f"missing tags {address}", failures)
        if tag_row:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = decompile.get(key)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    context = rows_by(read_tsv(BASE / "context-metadata.tsv"), "address")
    context_decompile = rows_by(read_tsv(BASE / "context-decompile" / "index.tsv"), "address")
    for address, (name, signature) in CONTEXT_TARGETS.items():
        row = context.get(normalize_address(address))
        require(row is not None, f"missing context metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"context name mismatch {address}", failures)
            require(row.get("signature") == signature, f"context signature mismatch {address}: {row.get('signature')}", failures)
        dec = context_decompile.get(normalize_address(address))
        require(dec is not None and dec.get("status") == "OK", f"context decompile missing/bad {address}", failures)

    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    expected_xrefs = {
        ("0x00481450", "0x0046c360", "CGame__Init"),
        ("0x004815c0", "0x0046c430", "CGame__InitRestartLoop"),
        ("0x00481650", "0x0046e240", "CGame__RunLevel"),
        ("0x00481af0", "0x0046d040", "CGame__PostLoadProcess"),
        ("0x00481f40", "0x0043f340", "CCutscene__Start"),
        ("0x00481f40", "0x0043f420", "CCutscene__Stop"),
        ("0x004821e0", "0x00427210", "CDXCompass__Render"),
        ("0x00488330", "0x005007f0", "CVBufTexture__ResizeIndexBuffer"),
        ("0x004885e0", "0x00546b40", "CDXLandscape__UpdateLOD"),
        ("0x0048f540", "0x0046c430", "CGame__InitRestartLoop"),
        ("0x0048f5a0", "<none>", "<no_function>"),
        ("0x0048f5c0", "0x0048f5a0", "CLevelBriefingLog__scalar_deleting_dtor"),
    }
    for target, source, function in expected_xrefs:
        require(
            any(
                normalize_address(row.get("target_addr", "")) == normalize_address(target)
                and (source == "<none>" or normalize_address(row.get("from_function_addr", "")) == normalize_address(source))
                and row.get("from_function") == function
                for row in xrefs
            ),
            f"missing xref {target} from {function}",
            failures,
        )

    instructions = read_text(BASE / "pre-instructions.tsv")
    for token in (
        "RET\t0x10",
        "RET\t0x4",
        "0x2800",
        "0x800",
        "CALL\t0x004f27e0",
        "CALL\t0x004bac40",
    ):
        require(token in instructions, f"missing instruction token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=16 found=16 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=16 missing=0",
        "pre-xrefs.log": "Wrote 23 rows",
        "pre-instructions.log": "Wrote 3829 function-body instruction rows",
        "pre-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "context-metadata.log": "targets=9 found=9 missing=0",
        "context-xrefs.log": "Wrote 23 rows",
        "context-instructions.log": "Wrote 2075 function-body instruction rows",
        "context-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save token in {relative}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR", "BADNAME", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 18, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (173968263, 173968263.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue_docs_ledgers(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6238, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    core_docs = [
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        HUD_DOC,
        DXCOMPASS_DOC,
        IBUFFER_DOC,
        LEVEL_BRIEFING_DOC,
        POST_RENDER_DOC,
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

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-hud-lifecycle-render-support-review-wave1013")
        == r"py -3 tools\ghidra_hud_lifecycle_render_support_review_wave1013_probe.py --check",
        "missing package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1013-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1013 --check",
        "missing aggregate recheck script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1013 HUD lifecycle render support review" for row in ledger), "missing Wave1013 ledger row", failures)
    require(any(row.get("task") == "Wave1013 HUD lifecycle render support review" for row in attempts), "missing Wave1013 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue_docs_ledgers(failures)

    if failures:
        print("Wave1013 HUD lifecycle/render-support probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1013 HUD lifecycle/render-support probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
