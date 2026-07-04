#!/usr/bin/env python3
"""Validate Wave1003 HUD head/render-state review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1003-hud-head-render-state-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_hud_head_render_state_review_wave1003_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1003_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
GAME_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "_index.md"
GAME_SHUTDOWN_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "game.cpp" / "CGame__Shutdown.md"
HUD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md"
DXFEVIDEO_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXFrontEndVideo.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-120949_post_wave1003_hud_head_render_state_review_verified"

TARGETS = {
    "0x0046c990": ("CGame__Shutdown", "void __fastcall CGame__Shutdown(void * this)"),
    "0x00481400": ("CHud__ctor_base", "void * __thiscall CHud__ctor_base(void * this)"),
    "0x00481450": ("CHud__Init", "void __thiscall CHud__Init(void * this)"),
    "0x004815c0": ("CHud__Reset", "void __thiscall CHud__Reset(void * this)"),
    "0x00481650": ("CHud__LoadTextures", "void __thiscall CHud__LoadTextures(void * this)"),
    "0x00481af0": ("CHud__PostLoadProcess", "int __thiscall CHud__PostLoadProcess(void * this)"),
    "0x00481b00": ("CHud__ShutDown", "void __thiscall CHud__ShutDown(void * this)"),
    "0x00481f40": ("CHud__SetHudComponent", "void __thiscall CHud__SetHudComponent(void * this, char * component_name, byte slot_flag)"),
    "0x00482050": ("CHud__PromotePendingHudComponent", "void __thiscall CHud__PromotePendingHudComponent(void * this)"),
    "0x00482090": ("HudRenderState__ApplyOverlaySpriteState", "void __cdecl HudRenderState__ApplyOverlaySpriteState(void)"),
    "0x004821b0": ("CDXCompass__ApplyRenderStateModulate", "void __cdecl CDXCompass__ApplyRenderStateModulate(void)"),
    "0x004821e0": ("CDXCompass__ApplyRenderStateAdditive", "void __cdecl CDXCompass__ApplyRenderStateAdditive(void)"),
    "0x00482210": ("CHud__RenderSegmentedMeterBar", "void __thiscall CHud__RenderSegmentedMeterBar(void * this, float x, float y, float width, float scale, float fill_fraction)"),
}

COMMENT_TOKENS = {
    "0x0046c990": (
        "Wave1003 CGame shutdown boundary recovery",
        "source-aligned CGame::Shutdown",
        "0x005dbbbc",
        "0x005e50a4",
        "CHud__ShutDown",
        "0x0046ca6b RET",
        "references/Onslaught/game.cpp:CGame::Shutdown",
    ),
    "0x00481b00": ("Wave400", "CHud shut down", "compass/BattleLine"),
    "0x00482090": ("Wave400", "HUD/message/compass/battleline overlay render-state setup"),
    "0x00482210": ("Wave400", "segmented objective/message meter"),
}

DOC_TOKENS = (
    "Wave1003",
    "hud-head-render-state-review-wave1003",
    "0x0046c990 CGame__Shutdown",
    "0x00481b00 CHud__ShutDown",
    "0x00481400 CHud__ctor_base",
    "0x00482090 HudRenderState__ApplyOverlaySpriteState",
    "0x004821b0 CDXCompass__ApplyRenderStateModulate",
    "0x00482210 CHud__RenderSegmentedMeterBar",
    "472/1408 = 33.52%",
    "641/1478 = 43.37%",
    "371/500 = 74.20%",
    "6223/6223 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime shutdown behavior proven",
    "runtime hud behavior proven",
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
        "pre-metadata.tsv": 12,
        "pre-tags.tsv": 12,
        "pre-xrefs.tsv": 30,
        "pre-instructions.tsv": 1268,
        "pre-decompile/index.tsv": 12,
        "pre-context-instructions.tsv": 246,
        "pre-shutdown-context-instructions.tsv": 363,
        "pre-shutdown-context-xrefs.tsv": 8,
        "pre-shutdown-context-metadata.tsv": 3,
        "pre-shutdown-context-decompile/index.tsv": 3,
        "post-metadata.tsv": 13,
        "post-tags.tsv": 13,
        "post-xrefs.tsv": 32,
        "post-instructions.tsv": 1324,
        "post-decompile/index.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    pre_context = read_tsv(BASE / "pre-shutdown-context-metadata.tsv")
    require(row_by_address(pre_context, "0x0046c990") and row_by_address(pre_context, "0x0046c990").get("status") == "MISSING", "pre context did not show 0x0046c990 missing", failures)
    require(row_by_address(pre_context, "0x0046c9ac") and row_by_address(pre_context, "0x0046c9ac").get("status") == "MISSING", "pre context did not show 0x0046c9ac missing", failures)
    require(row_by_address(pre_context, "0x0046ca70") and row_by_address(pre_context, "0x0046ca70").get("name") == "CGame__ShutdownRestartLoop", "pre context missing CGame__ShutdownRestartLoop anchor", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")

    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            for token in COMMENT_TOKENS.get(address, ()):
                require(token in row.get("comment", ""), f"comment token missing {address}: {token}", failures)

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
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag {address}", failures)
            if address == "0x0046c990":
                for tag in (
                    "hud-head-render-state-review-wave1003",
                    "wave1003-readback-verified",
                    "function-boundary-recovered",
                    "source-parity",
                    "signature-hardened",
                ):
                    require(tag in actual_tags, f"missing Wave1003 tag {address}: {tag}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    expected_xrefs = (
        ("0x0046c990", "0x005dbbbc", "DATA"),
        ("0x0046c990", "0x005e50a4", "DATA"),
        ("0x00481b00", "0x0046c9ac", "UNCONDITIONAL_CALL"),
        ("0x00481450", "0x0046c3d8", "UNCONDITIONAL_CALL"),
        ("0x004815c0", "0x0046c463", "UNCONDITIONAL_CALL"),
        ("0x00481650", "0x0046e367", "UNCONDITIONAL_CALL"),
        ("0x00481af0", "0x0046d052", "UNCONDITIONAL_CALL"),
        ("0x00482050", "0x0053ef5e", "UNCONDITIONAL_CALL"),
        ("0x004821b0", "0x0042722c", "UNCONDITIONAL_CALL"),
        ("0x004821e0", "0x00427911", "UNCONDITIONAL_CALL"),
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

    shutdown_decompile = read_text(BASE / "post-decompile" / "0046c990_CGame__Shutdown.c")
    for token in (
        "void __fastcall CGame__Shutdown(void *this)",
        "CHud__ShutDown",
        "CGameInterface__Shutdown",
        "CStaticShadows__ClearAllShadowEntries",
        "CDXEngine__Shutdown",
        "CTexture__FreeLevelResources",
        "CGame__RunOutroFMV",
        "CConsole__ClearCommandAndVariableLists",
    ):
        require(token in shutdown_decompile, f"CGame shutdown decompile missing token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "pre-metadata.log": ("targets=12 found=12 missing=0", "REPORT: Save succeeded"),
        "pre-tags.log": ("ExportFunctionTagsByAddress complete: rows=12 missing=0", "REPORT: Save succeeded"),
        "pre-xrefs.log": ("Wrote 30 rows", "REPORT: Save succeeded"),
        "pre-instructions.log": ("Wrote 1268 function-body instruction rows", "targets=12 missing=0", "REPORT: Save succeeded"),
        "pre-decompile.log": ("targets=12 dumped=12 missing=0 failed=0", "REPORT: Save succeeded"),
        "pre-context-instructions.log": ("Wrote 246 instruction rows", "targets=6 missing=0", "REPORT: Save succeeded"),
        "apply-dry.log": ("SUMMARY: updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0", "REPORT: Save succeeded"),
        "apply.log": ("SUMMARY: updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=2 missing=0 bad=0", "REPORT: Save succeeded"),
        "apply-final-dry.log": ("SUMMARY: updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0", "REPORT: Save succeeded"),
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
        GAME_DOC,
        GAME_SHUTDOWN_DOC,
        HUD_DOC,
        DXFEVIDEO_DOC,
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
        scripts.get("test:ghidra-hud-head-render-state-review-wave1003")
        == r"py -3 tools\ghidra_hud_head_render_state_review_wave1003_probe.py --check",
        "missing Wave1003 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1003-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1003 --check",
        "missing Wave1003 recheck package script",
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
    require(any(row.get("task") == "Wave1003 HUD head render-state review" for row in ledger_rows), "missing Wave1003 ledger row", failures)
    require(any(row.get("task") == "Wave1003 HUD head render-state review" and row.get("attempt_id") == 20585 for row in attempts), "missing Wave1003 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1003 HUD head/render-state review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1003 HUD head/render-state review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
