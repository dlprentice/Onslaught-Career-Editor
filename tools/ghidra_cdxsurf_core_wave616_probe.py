#!/usr/bin/env python3
"""Validate Wave616 CDXSurf core Ghidra artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave616-cdxsurf-core"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxsurf_core_wave616_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXSURF_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXSurf.cpp.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGETS = {
    "0x005563d0": (
        "CDXSurf__RenderSurface",
        "void __cdecl CDXSurf__RenderSurface(float draw_x, float draw_y, float draw_z, void * texture_or_resource, float draw_width, float draw_height, float draw_depth, int color_a, int color_b, float scale_x, float scale_y)",
        ("Wave616", "CVBufTexture__DrawSpriteEx", "default UV bounds"),
        ("cdxsurf-wave616", "render-surface", "sprite-wrapper"),
    ),
    "0x00556460": (
        "CDXSurf__Init",
        "void __thiscall CDXSurf__Init(void * this)",
        ("clears", "+0x0c", "initialized flag"),
        ("cdxsurf-wave616", "init", "zero-fields"),
    ),
    "0x00556470": (
        "CDXSurf__LoadWavesTexture",
        "void __thiscall CDXSurf__LoadWavesTexture(void * this)",
        ("mixers\\\\waves.tga", "CTexture__FindTexture", "this+0x8"),
        ("cdxsurf-wave616", "waves-texture", "texture-resource"),
    ),
    "0x00556490": (
        "CDXSurf__CreateSurfaceArray",
        "void __thiscall CDXSurf__CreateSurfaceArray(void * this, void * chunk_reader)",
        ("CResourceAccumulator__ReadResourceFile", "count*0x0c+4", "CDXSurf__CreateSurfaceStrip"),
        ("cdxsurf-wave616", "surface-array", "chunk-reader"),
    ),
    "0x005565b0": (
        "CDXSurf__DestroyBuffers",
        "void __fastcall CDXSurf__DestroyBuffers(void * surface_strip)",
        ("vector cleanup callback", "delete flag 1", "strip+0x04"),
        ("cdxsurf-wave616", "buffer-destroy", "callback"),
    ),
    "0x005565d0": (
        "CDXSurf__CreateSurfaceStrip",
        "void __thiscall CDXSurf__CreateSurfaceStrip(void * this, void * chunk_reader)",
        ("shader 0x242", "DAT_0082b4a4", "wave vertices"),
        ("cdxsurf-wave616", "surface-strip", "wave-geometry"),
    ),
    "0x005569e0": (
        "CDXSurf__Destroy",
        "void __thiscall CDXSurf__Destroy(void * this)",
        ("CDXLandscape__Shutdown", "CHud__DecrementCounter9C", "this+0x8"),
        ("cdxsurf-wave616", "destroy", "texture-release"),
    ),
    "0x00556a30": (
        "CDXSurf__Render",
        "void __thiscall CDXSurf__Render(void * this, byte validated_mode)",
        ("CWaterRenderSystem__RenderMainPass", "triangle strips", "depth bias"),
        ("cdxsurf-wave616", "render", "water-pass"),
    ),
    "0x00556d70": (
        "CDXSurf__ScalarDeletingDestructor",
        "void * __thiscall CDXSurf__ScalarDeletingDestructor(void * this, byte delete_flags)",
        ("vtable 0x005e59a0 slot 0", "CDXSurf__dtor", "delete_flags"),
        ("cdxsurf-wave616", "scalar-deleting-dtor", "vtable-verified"),
    ),
    "0x00556d90": (
        "CDXSurf__dtor",
        "void __fastcall CDXSurf__dtor(void * this)",
        ("Texture: %s refcount %d", "unaff_ESI", "global list"),
        ("cdxsurf-wave616", "destructor", "texture-refcount"),
    ),
    "0x00556f80": (
        "CDXSurf__DestroyRenderTarget",
        "void __thiscall CDXSurf__DestroyRenderTarget(void * this)",
        ("CFEPGoodies__FreeUpGoodyResources", "this+0x140", "CVBufTexture"),
        ("cdxsurf-wave616", "render-target", "resource-release"),
    ),
    "0x00556fc0": (
        "CDXSurf__SetupSurface",
        "bool __thiscall CDXSurf__SetupSurface(void * this, int setup_value, short format_word, int size_x, int size_y, byte setup_flags, int extra_config)",
        ("vtable 0x005e59a0 slot +0x18", "RET 0x18", "0x00556e90/0x00558600"),
        ("cdxsurf-wave616", "setup-surface", "vtable-slot-18"),
    ),
}

CONTEXT_OK = {
    "0x00557060": "CTextureSequence__EnsureLoaded",
    "0x005572c0": "CTextureSequence__ReleaseIfLoaded",
    "0x00557a90": "CDXTexture__LoadTextureFromFile_Core",
}

CONTEXT_MISSING = {"0x00558600", "0x00556e90"}

OVERCLAIM_TOKENS = (
    "runtime water behavior proven",
    "runtime rendering behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "fully reverse-engineered",
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


def read_tsv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require_tokens(label: str, text: str, tokens: tuple[str, ...] | set[str], failures: list[str]) -> None:
    normalized = text.replace("\\\\", "\\")
    for token in tokens:
        token = token.replace("\\\\", "\\")
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_clean_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in (
        "LockException",
        "Input file not found",
        "BADADDR",
        "ERROR REPORT SCRIPT ERROR",
        "BAD:",
        "BADNAME:",
        "Read-back signature mismatch",
    ):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    clean_expectations = {
        "apply-wave616-dry.log": {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave616-dry-after-thiscall-fix.log": {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave616-apply.log": {"updated": 1, "skipped": 11, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave616-final-dry.log": {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave616-dry-render-param-names.log": {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave616-apply-render-param-names.log": {"updated": 1, "skipped": 11, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave616-final-dry-after-render-param-names.log": {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
    }
    for name, expected in clean_expectations.items():
        require_clean_log_summary(BASE / name, expected, failures)

    mismatch = read_text(BASE / "apply-wave616-apply-inserted-this-mismatch.log")
    require_tokens(
        "preserved mismatch log",
        mismatch,
        (
            "SUMMARY: updated=11 skipped=0 renamed=0 would_rename=0 missing=0 bad=1",
            "BAD: 0x005565d0 CDXSurf__CreateSurfaceStrip",
            "Read-back signature mismatch at 0x005565d0",
            "void __thiscall CDXSurf__CreateSurfaceStrip(void * this, void * surface_strip, void * chunk_reader)",
            "ERROR REPORT SCRIPT ERROR",
            "REPORT: Save succeeded",
        ),
        failures,
    )

    expected_log_tokens = {
        "post-context-metadata.log": "targets=17 found=15 missing=2",
        "post-context-tags.log": "rows=15 missing=2",
        "post-context-xrefs.log": "Wrote 169 rows",
        "post-context-instructions.log": "Wrote 1445 instruction rows",
        "post-context-decompile.log": "targets=17 dumped=15 missing=2 failed=0",
        "post-vtable-slots.log": "targets=1 rows=32",
        "export-quality-snapshot-final.log": "total_functions=6093 commented_functions=3172",
    }
    for log_name, token in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, (token,), failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_and_tags(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 17:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 17")
    by_address = {normalize_address(row["address"]): row for row in rows}

    for address, (name, signature, comment_tokens, tag_tokens) in TARGETS.items():
        row = by_address.get(address)
        if not row:
            failures.append(f"post-context-metadata missing {address}")
            continue
        if row["status"] != "OK":
            failures.append(f"{address} status mismatch: {row['status']}")
        if row["name"] != name:
            failures.append(f"{address} name mismatch: {row['name']} != {name}")
        if row["signature"] != signature:
            failures.append(f"{address} signature mismatch: {row['signature']} != {signature}")
        require_tokens(f"{address} comment", row["comment"], comment_tokens, failures)
        for token in OVERCLAIM_TOKENS:
            if token in row["comment"].lower():
                failures.append(f"{address} comment overclaims: {token}")

    for address, name in CONTEXT_OK.items():
        row = by_address.get(address)
        if not row or row.get("name") != name or row.get("status") != "OK":
            failures.append(f"context row mismatch for {address}: {row}")
    for address in CONTEXT_MISSING:
        row = by_address.get(address)
        if not row or row.get("status") != "MISSING":
            failures.append(f"missing context row mismatch for {address}: {row}")

    tag_rows = read_tsv_rows(BASE / "post-context-tags.tsv")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
    }
    for address, (_, _, _, expected_tags) in TARGETS.items():
        tags = tags_by_address.get(address)
        if tags is None:
            failures.append(f"post-context-tags missing {address}")
            continue
        required = {"static-reaudit", "retail-binary-evidence", "comment-hardened", *expected_tags}
        missing = required - tags
        if missing:
            failures.append(f"{address} missing tags: {sorted(missing)}")


def check_exports(failures: list[str]) -> None:
    counts = {
        "post-context-xrefs.tsv": (len(read_tsv_rows(BASE / "post-context-xrefs.tsv")), 169),
        "post-context-instructions.tsv": (len(read_tsv_rows(BASE / "post-context-instructions.tsv")), 1445),
        "post-context-decompile/index.tsv": (len(read_tsv_rows(BASE / "post-context-decompile" / "index.tsv")), 17),
        "post-vtable-slots.tsv": (len(read_tsv_rows(BASE / "post-vtable-slots.tsv")), 32),
    }
    for label, (actual, expected) in counts.items():
        if actual != expected:
            failures.append(f"{label} row count mismatch: {actual} != {expected}")

    require_tokens(
        "post-vtable-slots.tsv",
        read_text(BASE / "post-vtable-slots.tsv"),
        (
            "005e59a0\t0\t005e59a0\t0x00556d70\t00556d70\t00556d70\tCDXSurf__ScalarDeletingDestructor",
            "005e59a0\t1\t005e59a4\t0x00557a90\t00557a90\t00557a90\tCDXTexture__LoadTextureFromFile_Core",
            "005e59a0\t4\t005e59b0\t0x00558600\t00558600\t<none>\t<no_function>",
            "005e59a0\t5\t005e59b4\t0x00556e90\t00556e90\t<none>\t<no_function>",
            "005e59a0\t6\t005e59b8\t0x00556fc0\t00556fc0\t00556fc0\tCDXSurf__SetupSurface",
            "005e59a0\t7\t005e59bc\t0x00405930\t00405930\t00405930\tSharedVFunc__ReturnZero_00405930",
            "005e59a0\t14\t005e59d8\t0x0055a360",
            "005e59a0\t19\t005e59ec\t0x3f000000",
        ),
        failures,
    )
    require_tokens(
        "post decompile RenderSurface",
        read_text(BASE / "post-context-decompile" / "005563d0_CDXSurf__RenderSurface.c"),
        (
            "/* signature: void __cdecl CDXSurf__RenderSurface(float draw_x, float draw_y, float draw_z, void * texture_or_resource, float draw_width, float draw_height, float draw_depth, int color_a, int color_b, float scale_x, float scale_y) */",
            "CDXSurf__RenderSurface",
            "CVBufTexture__DrawSpriteEx",
            "scale_x",
            "scale_y",
        ),
        failures,
    )
    require_tokens(
        "post decompile CreateSurfaceStrip",
        read_text(BASE / "post-context-decompile" / "005565d0_CDXSurf__CreateSurfaceStrip.c"),
        (
            "void __thiscall CDXSurf__CreateSurfaceStrip(void *this,void *chunk_reader)",
            "CDXMemoryManager__Alloc",
            "CVBuffer__Create",
            "fsin",
        ),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupRoot") != "[maintainer-local-ghidra-backup-root]\\BEA_20260520-020900_post_wave616_cdxsurf_core_verified":
        failures.append(f"backup path mismatch: {backup.get('backupRoot')}")
    expected_backup = {
        "sourceFileCount": 19,
        "destFileCount": 19,
        "sourceBytes": 161614727,
        "destBytes": 161614727,
        "diffCount": 0,
    }
    for key, expected in expected_backup.items():
        if backup.get(key) != expected:
            failures.append(f"backup {key} mismatch: {backup.get(key)} != {expected}")
    if backup.get("diffs"):
        failures.append("backup diffs not empty")

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    expected_queue = {
        "totalFunctions": 6093,
        "commentlessFunctionCount": 2921,
        "undefinedSignatureCount": 1260,
        "paramSignatureCount": 1056,
    }
    if queue.get("totalFunctions") != expected_queue["totalFunctions"]:
        failures.append(f"queue total mismatch: {queue.get('totalFunctions')}")
    for key, expected in expected_queue.items():
        if key == "totalFunctions":
            continue
        if quality.get(key) != expected:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected}")
    high_signal = queue.get("priorityQueues", {}).get("commentlessHighSignal", [])
    if not high_signal or high_signal[0].get("address") != "0x00557300":
        failures.append("queue next high-signal head mismatch")


def check_public_docs(failures: list[str]) -> None:
    public_note = read_text(PUBLIC_NOTE)
    require_tokens(
        "public note",
        public_note,
        (
            "# Ghidra CDXSurf Core Wave616",
            "Wave616 hardened `12` CDXSurf rows",
            "Preserved first apply mismatch",
            "Read-back exports verified `15` context metadata rows plus `2` expected missing unbounded vtable targets",
            "Next queue head: `0x00557300 CDXTexture__LoadTextureFromFile`",
            "Runtime water/render behavior remains unproven.",
        ),
        failures,
    )
    for token in OVERCLAIM_TOKENS:
        if token in public_note.lower():
            failures.append(f"public note overclaims: {token}")

    require_tokens(
        "package.json",
        read_text(PACKAGE_JSON),
        ("test:ghidra-cdxsurf-core-wave616", "ghidra_cdxsurf_core_wave616_probe.py"),
        failures,
    )
    require_tokens(
        "function index",
        read_text(FUNCTION_INDEX),
        ("Wave616 CDXSurf core hardening", "0x00557300 CDXTexture__LoadTextureFromFile", "3172/6093 = 52.06%", "3127/6093 = 51.32%"),
        failures,
    )
    require_tokens(
        "DXSurf doc",
        read_text(DXSURF_DOC),
        (
            "Last updated: 2026-05-20",
            "Wave616",
            "CDXSurf__RenderSurface",
            "CDXSurf__SetupSurface",
            "0x00558600",
            "0x00556e90",
            "Runtime water/render behavior remains unproven.",
        ),
        failures,
    )
    require_tokens(
        "campaign",
        read_text(CAMPAIGN),
        ("after Wave616", "ghidra_cdxsurf_core_wave616_2026-05-20.md", "0x00557300 CDXTexture__LoadTextureFromFile"),
        failures,
    )
    require_tokens(
        "backlog",
        read_text(BACKLOG),
        ("0x005563d0,0x00556460,0x00556470", "Ghidra CDXSurf core Wave616 signature/comment hardening", "DiffCount=0"),
        failures,
    )
    require_tokens(
        "ledger",
        read_text(LEDGER),
        ("Ghidra CDXSurf core Wave616 signature/comment hardening", "cdxsurf-wave616", "0x00557300 CDXTexture__LoadTextureFromFile"),
        failures,
    )
    require_tokens(
        "attempt log",
        read_text(ATTEMPT_LOG),
        ("\"attempt_id\":20271", "Ghidra CDXSurf core Wave616 signature/comment hardening", "headless_java_apply_signature_comment_tags_no_renames_no_boundary_change"),
        failures,
    )
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20272:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    if tracking.get("counters", {}).get("ledger_rows") != 1012:
        failures.append(f"tracking ledger_rows mismatch: {tracking.get('counters', {}).get('ledger_rows')}")
    require_tokens("tracking", json.dumps(tracking), ("Wave616", "0x00557300 CDXTexture__LoadTextureFromFile"), failures)


def run_checks() -> list[str]:
    failures: list[str] = []
    try:
        check_logs(failures)
        check_metadata_and_tags(failures)
        check_exports(failures)
        check_backup_and_queue(failures)
        check_public_docs(failures)
    except Exception as exc:  # pragma: no cover - failure reporting path
        failures.append(f"{exc.__class__.__name__}: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_checks()
    if failures:
        print("Wave616 CDXSurf core probe FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave616 CDXSurf core probe PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
