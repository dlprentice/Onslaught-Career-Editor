#!/usr/bin/env python3
"""Validate Wave617 CDXTexture head Ghidra artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave617-cdxtexture-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cdxtexture_head_wave617_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

TARGETS = {
    "0x00557300": (
        "CDXTexture__LoadTextureFromFile",
        "int __thiscall CDXTexture__LoadTextureFromFile(void * this, int texture_slot)",
        ("Wave617", "data\\\\Resources", "CDXTexture__DecodeMappedMemoryEntry"),
        ("cdxtexture-wave617", "texture-load", "ret-0004"),
    ),
    "0x005586e0": (
        "CDXTexture__DumpTextureToRGBA",
        "void __thiscall CDXTexture__DumpTextureToRGBA(void * this, char * output_path)",
        ("CDXTexture__DumpAllTexturesToTga", "ImageIO__WriteTGA24", "temporary buffer"),
        ("cdxtexture-wave617", "texture-dump", "tga"),
    ),
    "0x00559410": (
        "CDXTexture__CreateMipmaps",
        "void __thiscall CDXTexture__CreateMipmaps(void * this, void * chunk_reader, int texture_slot, int mip_count)",
        ("CDXTexture__Deserialize", "failed direct texture create", "RET 0x0c"),
        ("cdxtexture-wave617", "mipmaps", "chunk-reader"),
    ),
    "0x00559be0": (
        "CDXTexture__Deserialize",
        "void * __cdecl CDXTexture__Deserialize(byte use_stream_payload, void * chunk_reader)",
        ("caller-cleaned", "CResourceAccumulator__ReadResourceFile", "0x158-byte CTexture"),
        ("cdxtexture-wave617", "deserialize", "cdecl"),
    ),
}

OVERCLAIM_TOKENS = (
    "runtime texture loading proven",
    "runtime mipmap behavior proven",
    "runtime resource ownership proven",
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
        "apply-wave617-dry.log": {"updated": 0, "skipped": 4, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave617-apply.log": {"updated": 4, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "apply-wave617-final-dry.log": {"updated": 0, "skipped": 4, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
    }
    for name, expected in clean_expectations.items():
        require_clean_log_summary(BASE / name, expected, failures)

    expected_log_tokens = {
        "pre-callsite-instructions.log": "targets=13 missing=0",
        "post-context-metadata.log": "targets=16 found=16 missing=0",
        "post-context-tags.log": "rows=16 missing=0",
        "post-context-xrefs.log": "Wrote 57 rows",
        "post-context-instructions.log": "Wrote 592 instruction rows",
        "post-context-decompile.log": "targets=16 dumped=16 missing=0 failed=0",
        "post-vtable-slots.log": "targets=1 rows=32",
        "post-function-quality.log": "total_functions=6093 commented_functions=3176",
    }
    for log_name, token in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, (token,), failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_and_tags(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-context-metadata.tsv")
    if len(rows) != 16:
        failures.append(f"post-context-metadata row count mismatch: {len(rows)} != 16")
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

    tag_rows = read_tsv_rows(BASE / "post-context-tags.tsv")
    tags_by_address = {
        normalize_address(row["address"]): set(filter(None, row["tags"].split(";")))
        for row in tag_rows
        if row.get("status") == "OK"
    }
    for address, (_, _, _, tag_tokens) in TARGETS.items():
        tags = tags_by_address.get(address, set())
        for token in tag_tokens:
            if token not in tags:
                failures.append(f"{address} missing tag {token}")


def check_xrefs_and_callsites(failures: list[str]) -> None:
    xrefs = read_text(BASE / "post-context-xrefs.tsv")
    for token in (
        "00559d04\t00559be0\tCDXTexture__Deserialize\tUNCONDITIONAL_CALL",
        "00557d69\t00557a90\tCDXTexture__LoadTextureFromFile_Core\tUNCONDITIONAL_CALL",
        "005588ca\t00558870\tCDXTexture__DumpAllTexturesToTga\tUNCONDITIONAL_CALL",
        "00559d9e\t00559be0\tCDXTexture__Deserialize\tUNCONDITIONAL_CALL",
        "004d764b\t004d7200\tCResourceAccumulator__ReadResourceFile\tUNCONDITIONAL_CALL",
        "00540859\t00540840\tCDXBitmapFont__Deserialize\tUNCONDITIONAL_CALL",
        "00543dff\t00543d90\tCDXImposter__Deserialize\tUNCONDITIONAL_CALL",
    ):
        require_tokens("post-context-xrefs.tsv", xrefs, (token,), failures)

    callsites = read_text(BASE / "pre-callsite-instructions.tsv")
    for token in (
        "0x00559d04\tTARGET\t0\t0x00559d04\t0x00559be0\tCDXTexture__Deserialize\tCALL\t0x00557300",
        "0x00559d9e\tTARGET\t0\t0x00559d9e\t0x00559be0\tCDXTexture__Deserialize\tCALL\t0x00559410",
        "0x005588ca\tTARGET\t0\t0x005588ca\t0x00558870\tCDXTexture__DumpAllTexturesToTga\tCALL\t0x005586e0",
        "0x004d764b\tAFTER\t1\t0x004d7650\t0x004d7200\tCResourceAccumulator__ReadResourceFile\tADD\tESP, 0x8",
        "0x0055793e\tAFTER\t11\t0x0055796f\t0x00557300\tCDXTexture__LoadTextureFromFile\tRET\t0x4",
        "0x00558867\tAFTER\t2\t0x0055886b\t0x005586e0\tCDXTexture__DumpTextureToRGBA\tRET\t0x4",
        "0x00559b64\tAFTER\t1\t0x00559b67\t0x00559410\tCDXTexture__CreateMipmaps\tRET\t0xc",
    ):
        require_tokens("pre-callsite-instructions.tsv", callsites, (token,), failures)


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    expected_backup = {
        "BackupPath": "G:\\GhidraBackups\\BEA_20260520-022015_post_wave617_cdxtexture_head_verified",
        "SourceFileCount": 19,
        "BackupFileCount": 19,
        "SourceBytes": 161614727,
        "BackupBytes": 161614727,
        "DiffCount": 0,
    }
    for key, expected in expected_backup.items():
        if backup.get(key) != expected:
            failures.append(f"backup {key} mismatch: {backup.get(key)} != {expected}")

    queue = read_json(QUEUE_JSON)
    signals = queue.get("qualitySignals", {})
    expected_signals = {
        "commentlessFunctionCount": 2917,
        "undefinedSignatureCount": 1256,
        "paramSignatureCount": 1056,
        "legacyWeakNameCount": 0,
        "uncertainOwnerNameCount": 0,
        "helperAddressNameCount": 0,
        "wrapperAddressNameCount": 0,
    }
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    for key, expected in expected_signals.items():
        if signals.get(key) != expected:
            failures.append(f"queue {key} mismatch: {signals.get(key)} != {expected}")
    head = queue.get("priorityQueues", {}).get("commentlessHighSignal", [{}])[0]
    if head.get("address") != "0x0055a350" or head.get("name") != "CDXTrees__CDXTrees":
        failures.append(f"queue head mismatch: {head}")


def check_docs(failures: list[str]) -> None:
    doc_tokens = {
        PUBLIC_NOTE: ("Wave617", "0x0055a350 CDXTrees__CDXTrees", "3176/6093 = 52.13%"),
        FUNCTION_INDEX: ("Latest saved-correction note: Wave617", "DXTexture.cpp", "3131/6093 = 51.39%"),
        DXTEXTURE_DOC: ("## Wave617 Static Read-Back Note", "void * __cdecl CDXTexture__Deserialize", "0x0055a350 CDXTrees__CDXTrees"),
        CAMPAIGN: ("after Wave617", "Current CDXTexture head follow-up", "2917"),
        BACKLOG: ("Ghidra CDXTexture head Wave617", "ApplyCDXTextureHeadWave617.java", "DiffCount=0"),
        LEDGER: ("Ghidra CDXTexture head Wave617", "0x0055a350 CDXTrees__CDXTrees", "Runtime texture loading/dumping/mipmap"),
        ATTEMPT_LOG: ("\"attempt_id\":20272", "Ghidra CDXTexture head Wave617", "readback\":\"verified"),
        PACKAGE_JSON: ("test:ghidra-cdxtexture-head-wave617", "tools\\\\ghidra_cdxtexture_head_wave617_probe.py --check"),
    }
    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20273:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')}")
    if tracking.get("counters", {}).get("ledger_rows") != 1013:
        failures.append("tracking ledger_rows mismatch")
    if tracking.get("counters", {}).get("attempt_rows") != 20273:
        failures.append("tracking attempt_rows mismatch")
    if "Wave617 CDXTexture head hardening" not in tracking.get("current_focus", ""):
        failures.append("tracking current_focus missing Wave617")

    for path, tokens in doc_tokens.items():
        text = read_text(path)
        require_tokens(str(path.relative_to(ROOT)), text, tokens, failures)
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{path.relative_to(ROOT)} overclaims: {token}")


def run_check() -> list[str]:
    failures: list[str] = []
    for step in (
        check_logs,
        check_metadata_and_tags,
        check_xrefs_and_callsites,
        check_backup_and_queue,
        check_docs,
    ):
        try:
            step(failures)
        except Exception as exc:  # pragma: no cover - command-line probe reports all hard failures.
            failures.append(f"{step.__name__} raised {exc.__class__.__name__}: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures = run_check()
    if failures:
        print("Wave617 CDXTexture head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave617 CDXTexture head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
