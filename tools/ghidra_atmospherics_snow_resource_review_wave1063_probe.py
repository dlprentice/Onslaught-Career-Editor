#!/usr/bin/env python3
"""Validate Wave1063 Atmospherics snow/resource review artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1063-atmospherics-snow-resource-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_atmospherics_snow_resource_review_wave1063_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1063_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-222739_post_wave1063_atmospherics_snow_resource_review_verified"
BACKUP_SUMMARY = BASE / "backup-summary.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

DOCS = [
    PUBLIC_NOTE,
    AGGREGATE_NOTE,
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Atmospherics.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]

EXPECTED_SIGNATURES = {
    "0x00404a00": ("Atmospherics__Init", "void __cdecl Atmospherics__Init(void)"),
    "0x00404b90": ("Atmospherics__ResetAndUpdate", "void __cdecl Atmospherics__ResetAndUpdate(void)"),
    "0x00404bd0": ("Atmospherics__UpdateAll", "void __cdecl Atmospherics__UpdateAll(void)"),
    "0x00404bf0": ("Atmospherics__RenderAll", "void __cdecl Atmospherics__RenderAll(void)"),
    "0x00404c10": ("Atmospherics__Shutdown", "void __cdecl Atmospherics__Shutdown(void)"),
    "0x00404c90": ("Atmospherics__NotifyAll", "void __cdecl Atmospherics__NotifyAll(int eventCode)"),
    "0x00554e80": ("DXSnow__StaticInitPrimaryTransformGlobals", "void __cdecl DXSnow__StaticInitPrimaryTransformGlobals(void)"),
    "0x00554f50": ("DXSnow__StaticInitDisableSnowConfig", "void __cdecl DXSnow__StaticInitDisableSnowConfig(void)"),
    "0x00554f70": ("DXSnow__StaticDestroyDisableSnowConfig", "void __cdecl DXSnow__StaticDestroyDisableSnowConfig(void)"),
    "0x00554f80": ("CAtmosphericsProfile__ctor", "void * __fastcall CAtmosphericsProfile__ctor(void * this)"),
    "0x00555010": ("CAtmosphericsProfile__VFunc00_GetNameString", "char * __fastcall CAtmosphericsProfile__VFunc00_GetNameString(void * this)"),
    "0x00555020": ("CAtmosphericsProfile__ResetAndInitSnowResources", "void __thiscall CAtmosphericsProfile__ResetAndInitSnowResources(void * this)"),
    "0x00555410": ("CAtmosphericsProfile__ReleaseResources", "void __fastcall CAtmosphericsProfile__ReleaseResources(void * this)"),
    "0x00555460": ("CAtmosphericsProfile__RenderOverlay", "void __fastcall CAtmosphericsProfile__RenderOverlay(void * this)"),
    "0x00555600": ("CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay", "void __fastcall CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay(void * this)"),
    "0x00555af0": ("DXSnow__StaticZeroOverlayVectorGlobals", "void __cdecl DXSnow__StaticZeroOverlayVectorGlobals(void)"),
    "0x00555b10": ("DXSnow__StaticInitOverlayTransformGlobals", "void __cdecl DXSnow__StaticInitOverlayTransformGlobals(void)"),
}

TAGGED_ADDRESSES = {
    "0x00404a00": {"init", "snow-resource", "cvar-registration", "console-command"},
    "0x00404b90": {"reset-update", "wind-vector", "vtable-slot-0x0c"},
    "0x00404bd0": {"update-all", "vtable-slot-0x08"},
    "0x00404bf0": {"render-all", "vtable-slot-0x04"},
    "0x00404c10": {"shutdown", "resource-release", "vtable-slot-0x10"},
    "0x00404c90": {"notify-all", "event-code", "vtable-slot-0x14"},
}

COMMON_TAGS = {
    "static-reaudit",
    "atmospherics-snow-resource-review-wave1063",
    "wave1063-readback-verified",
    "retail-binary-evidence",
    "tag-normalized",
    "comment-hardened",
    "signature-corrected",
    "atmospherics",
    "weather",
    "list-dispatch",
}

DOC_TOKENS = (
    "Wave1063",
    "atmospherics-snow-resource-review-wave1063",
    "0x00404a00 Atmospherics__Init",
    "0x00404b90 Atmospherics__ResetAndUpdate",
    "0x00404bd0 Atmospherics__UpdateAll",
    "0x00404bf0 Atmospherics__RenderAll",
    "0x00404c10 Atmospherics__Shutdown",
    "0x00404c90 Atmospherics__NotifyAll",
    "0x00555020 CAtmosphericsProfile__ResetAndInitSnowResources",
    "812/1408 = 57.67%",
    "1187/1548 = 76.68%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "tag normalization",
)

OVERCLAIMS = (
    "runtime weather behavior proven",
    "runtime snow behavior proven",
    "runtime render behavior proven",
    "rebuild parity proven",
    "exact source-layout identity proven",
)


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


def norm(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 6,
        "primary-tags.tsv": 6,
        "primary-xrefs.tsv": 6,
        "primary-instructions.tsv": 802,
        "primary-decompile/index.tsv": 6,
        "context-metadata.tsv": 11,
        "context-tags.tsv": 11,
        "context-xrefs.tsv": 12,
        "context-instructions.tsv": 272,
        "context-decompile/index.tsv": 11,
        "post-metadata.tsv": 17,
        "post-tags.tsv": 17,
        "post-xrefs.tsv": 18,
        "post-instructions.tsv": 1074,
        "post-decompile/index.tsv": 17,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature) in EXPECTED_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)

    for address, extra in TAGGED_ADDRESSES.items():
        row = tags.get(address)
        require(row is not None, f"missing tags {address}", failures)
        actual_tags = set((row or {}).get("tags", "").split(";"))
        require((COMMON_TAGS | extra).issubset(actual_tags), f"Wave1063 tags missing {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 tags_added=77 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 tags_added=77 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=17 found=17 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=17 missing=0",
        "post-xrefs.log": "Wrote 18 rows",
        "post-instructions.log": "Wrote 1074 function-body instruction rows",
        "post-decompile.log": "targets=17 dumped=17 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "VERIFY_", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save report", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174721927, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-atmospherics-snow-resource-review-wave1063")
        == r"py -3 tools\ghidra_atmospherics_snow_resource_review_wave1063_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1063-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1063 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1063 atmospherics snow resource review" for row in ledger_rows), "missing Wave1063 ledger row", failures)
    require(any(row.get("task") == "Wave1063 atmospherics snow resource review" and row.get("attempt_id") == 20645 for row in attempt_rows), "missing Wave1063 attempt row", failures)


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
        print("Wave1063 Atmospherics snow/resource probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1063 Atmospherics snow/resource probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
