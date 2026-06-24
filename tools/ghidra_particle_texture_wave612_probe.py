#!/usr/bin/env python3
"""Validate Wave612 particle texture Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave612-particle-texture-0054f6e0-00550220"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_particle_texture_wave612_2026-05-20.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DXPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXParticleTexture.cpp.md"
ENGINE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

SIGNATURES = {
    "0x0054f6e0": "void __fastcall CDXEngine__ShutdownParticleSystemBundle(void * particle_bundle)",
    "0x0054f740": "void __fastcall CDXEngine__ResetParticleSystemBundle(void * particle_bundle)",
    "0x0054f760": "void __cdecl CDXEngine__SetParticleRenderStatePreset(void)",
    "0x0054f7e0": "void __fastcall CDXEngine__RenderParticleTexturePass(void * particle_bundle)",
    "0x0054fbc0": "void * __cdecl DXParticleTexture__GetOrCreate(char * texture_path, int texture_type)",
    "0x0054fd80": "void __cdecl DXParticleTexture__ReleaseAll(void)",
    "0x0054fde0": "void __cdecl DXParticleTexture__RestoreAll(void)",
    "0x0054fee0": "void __cdecl DXParticleTexture__DestroyAll(void)",
    "0x0054ff20": "void __cdecl DXParticleTexture__RenderAll(void)",
    "0x00550110": "void __thiscall DXParticleTexture__Release(void * this)",
    "0x00550180": "void __thiscall DXParticleTexture__AddTriangleIndices(void * this, ushort index0, ushort index1, ushort index2)",
    "0x005501b0": "void * __thiscall DXParticleTexture__GetIndexBuffer(void * this, int index_count)",
    "0x00550220": "void __thiscall DXParticleTexture__Render(void * this)",
}

NAMES = {
    "0x0054f6e0": "CDXEngine__ShutdownParticleSystemBundle",
    "0x0054f740": "CDXEngine__ResetParticleSystemBundle",
    "0x0054f760": "CDXEngine__SetParticleRenderStatePreset",
    "0x0054f7e0": "CDXEngine__RenderParticleTexturePass",
    "0x0054fbc0": "DXParticleTexture__GetOrCreate",
    "0x0054fd80": "DXParticleTexture__ReleaseAll",
    "0x0054fde0": "DXParticleTexture__RestoreAll",
    "0x0054fee0": "DXParticleTexture__DestroyAll",
    "0x0054ff20": "DXParticleTexture__RenderAll",
    "0x00550110": "DXParticleTexture__Release",
    "0x00550180": "DXParticleTexture__AddTriangleIndices",
    "0x005501b0": "DXParticleTexture__GetIndexBuffer",
    "0x00550220": "DXParticleTexture__Render",
}

COMMON_TAGS = {
    "static-reaudit",
    "particle-texture-wave612",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "particle-texture",
    "callsite-verified",
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime particle output proven",
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
        if token not in normalized:
            failures.append(f"{label} missing token: {token}")


def parse_log_summary(path: Path, failures: list[str]) -> dict[str, int]:
    text = read_text(path)
    match = re.search(r"SUMMARY:\s+([^\r\n]+)", text)
    if not match:
        failures.append(f"{path.name} missing SUMMARY")
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=([0-9]+)", match.group(1))}


def require_log_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    values = parse_log_summary(path, failures)
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            failures.append(f"{path.name} {key} mismatch: {values.get(key)} != {expected_value}")
    text = read_text(path)
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{path.name} missing save-success report")
    for bad_token in ("LockException", "Function not found", "Input file not found", "BADADDR", "MISSING:", "ERROR REPORT SCRIPT ERROR", "BAD:", "BADNAME:", "Read-back signature mismatch"):
        if bad_token in text:
            failures.append(f"{path.name} contains {bad_token}")


def check_logs(failures: list[str]) -> None:
    require_log_summary(
        BASE / "apply-wave612-dry.log",
        {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-wave612-apply.log",
        {"updated": 13, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )
    require_log_summary(
        BASE / "apply-wave612-final-dry.log",
        {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        failures,
    )

    expected_log_tokens = {
        "post-metadata.log": "targets=13 found=13 missing=0",
        "post-tags.log": "rows=13 missing=0",
        "post-xrefs.log": "Wrote 23 rows",
        "post-instructions.log": "targets=13 missing=0",
        "post-decompile.log": "targets=13 dumped=13 missing=0 failed=0",
        "post-callsite-instructions.log": "targets=23 missing=0",
        "queue-refresh.log": "total_functions=6093 commented_functions=3147",
    }
    for log_name, token in expected_log_tokens.items():
        text = read_text(BASE / log_name)
        require_tokens(log_name, text, (token,), failures)
        for bad_token in ("ERROR REPORT SCRIPT ERROR", "FileNotFoundException", "LockException", "BADADDR", "missing=1", "failed=1"):
            if bad_token in text:
                failures.append(f"{log_name} contains {bad_token}")


def check_metadata_and_tags(failures: list[str]) -> None:
    rows = read_tsv_rows(BASE / "post-metadata.tsv")
    if len(rows) != len(SIGNATURES):
        failures.append(f"post-metadata row count mismatch: {len(rows)} != {len(SIGNATURES)}")
        return
    for row in rows:
        address = normalize_address(row["address"])
        if address not in SIGNATURES:
            failures.append(f"unexpected metadata address: {row['address']}")
            continue
        if row["name"] != NAMES[address]:
            failures.append(f"metadata name mismatch for {address}: {row['name']} != {NAMES[address]}")
        if row["signature"] != SIGNATURES[address]:
            failures.append(f"metadata signature mismatch for {address}: {row['signature']} != {SIGNATURES[address]}")
        if row["status"] != "OK":
            failures.append(f"metadata status mismatch for {address}: {row['status']}")
        require_tokens("metadata comment", row["comment"], ("Wave612", "Static retail decompile/instruction/xref evidence only", "rebuild parity remain unproven"), failures)
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"metadata comment overclaims for {address}: {token}")

    tag_rows = read_tsv_rows(BASE / "post-tags.tsv")
    if len(tag_rows) != len(SIGNATURES):
        failures.append(f"post-tags row count mismatch: {len(tag_rows)} != {len(SIGNATURES)}")
        return
    for row in tag_rows:
        address = normalize_address(row["address"])
        tags = set(filter(None, row["tags"].split(";")))
        missing = COMMON_TAGS - tags
        if missing:
            failures.append(f"missing common tags for {address}: {sorted(missing)}")
        if address in ("0x0054f6e0", "0x0054f740", "0x0054f7e0") and "particle-bundle" not in tags:
            failures.append(f"missing particle-bundle tag for {address}")
        if address >= "0x0054fbc0" and "dxparticletexture" not in tags:
            failures.append(f"missing dxparticletexture tag for {address}")
        if address in ("0x00550110", "0x00550180", "0x005501b0", "0x00550220") and "thiscall-helper" not in tags:
            failures.append(f"missing thiscall-helper tag for {address}")


def check_exports(failures: list[str]) -> None:
    counts = {
        "post-xrefs.tsv": (len(read_tsv_rows(BASE / "post-xrefs.tsv")), 23),
        "post-instructions.tsv": (len(read_tsv_rows(BASE / "post-instructions.tsv")), 3393),
        "post-decompile/index.tsv": (len(read_tsv_rows(BASE / "post-decompile" / "index.tsv")), 13),
        "post-callsite-instructions.tsv": (len(read_tsv_rows(BASE / "post-callsite-instructions.tsv")), 667),
    }
    for label, (actual, expected) in counts.items():
        if actual != expected:
            failures.append(f"{label} row count mismatch: {actual} != {expected}")

    require_tokens(
        "post-xrefs.tsv",
        read_text(BASE / "post-xrefs.tsv"),
        ("004c57b9", "CParticleDescriptor__Load", "0054f9ec", "0054fefd", "00550082"),
        failures,
    )
    require_tokens(
        "post-instructions.tsv",
        read_text(BASE / "post-instructions.tsv"),
        ("CALL\t0x0054ff20", "DXParticleTexture__AddTriangleIndices", "RET\t0xc", "CALL\t0x00550220"),
        failures,
    )
    require_tokens(
        "post-callsite-instructions.tsv",
        read_text(BASE / "post-callsite-instructions.tsv"),
        ("0x004c57b9", "CALL\t0x0054fbc0", "ADD\tESP, 0x8", "0x0054fefd", "CALL\t0x00550110"),
        failures,
    )
    decompile_blob = "\n".join(path.read_text(encoding="utf-8-sig") for path in sorted((BASE / "post-decompile").glob("005*.c")))
    require_tokens(
        "post-decompile",
        decompile_blob,
        (
            "DXParticleTexture__GetOrCreate",
            "DAT_009c64d0",
            "DAT_009c6468",
            "CVertexShader__Create(s_particleshader_00651ed0",
            "CVBufTexture__GetIndexPtr",
            "DXParticleTexture__Render(this)",
        ),
        failures,
    )


def check_backup_and_queue(failures: list[str]) -> None:
    backup = read_json(BACKUP_SUMMARY)
    if backup.get("backupRoot") != "G:\\GhidraBackups\\BEA_20260519-234626_post_wave612_particle_texture_verified":
        failures.append(f"backup path mismatch: {backup.get('backupRoot')}")
    expected_backup = {
        "sourceFileCount": 19,
        "destFileCount": 19,
        "sourceBytes": 161581959,
        "destBytes": 161581959,
        "diffCount": 0,
    }
    for key, expected_value in expected_backup.items():
        actual = backup.get(key)
        if isinstance(actual, float):
            actual = int(actual)
        if actual != expected_value:
            failures.append(f"backup {key} mismatch: {actual} != {expected_value}")

    queue = read_json(QUEUE_JSON)
    if queue.get("status") != "PASS":
        failures.append(f"queue status mismatch: {queue.get('status')}")
    if queue.get("totalFunctions") != 6093:
        failures.append(f"queue totalFunctions mismatch: {queue.get('totalFunctions')} != 6093")
    quality = queue.get("qualitySignals", {})
    expected_quality = {
        "commentlessFunctionCount": 2946,
        "undefinedSignatureCount": 1283,
        "paramSignatureCount": 1056,
    }
    for key, expected_value in expected_quality.items():
        if quality.get(key) != expected_value:
            failures.append(f"queue {key} mismatch: {quality.get(key)} != {expected_value}")
    head = (queue.get("priorityQueues", {}).get("commentlessHighSignal") or [{}])[0]
    if head.get("address") != "0x00550380" or head.get("name") != "CDXPatch__Constructor":
        failures.append(f"queue head mismatch: {head}")


def check_public_docs(failures: list[str]) -> None:
    for path in (PUBLIC_NOTE, PACKAGE_JSON, FUNCTION_INDEX, DXPART_DOC, ENGINE_INDEX, CAMPAIGN, BACKLOG, LEDGER, ATTEMPT_LOG, TRACKING):
        if not path.is_file():
            failures.append(f"missing expected file: {path}")
            return

    note = read_text(PUBLIC_NOTE)
    require_tokens(
        "public note",
        note,
        (
            "Ghidra Particle Texture Wave612",
            "DXParticleTexture__GetOrCreate",
            "`13` metadata rows",
            "`23` xref rows",
            "`3393` instruction rows",
            "`667` callsite instruction rows",
            "G:\\GhidraBackups\\BEA_20260519-234626_post_wave612_particle_texture_verified",
            "Next queue head: `0x00550380 CDXPatch__Constructor`",
            "runtime particle output",
            "rebuild parity remain unproven",
        ),
        failures,
    )
    for token in OVERCLAIM_TOKENS:
        if token in note.lower():
            failures.append(f"public note overclaims: {token}")

    package_text = read_text(PACKAGE_JSON)
    require_tokens(
        "package.json",
        package_text,
        ("test:ghidra-particle-texture-wave612", "tools\\ghidra_particle_texture_wave612_probe.py --check"),
        failures,
    )

    for label, path in (
        ("functions index", FUNCTION_INDEX),
        ("DXParticleTexture doc", DXPART_DOC),
        ("engine index", ENGINE_INDEX),
        ("campaign", CAMPAIGN),
        ("backlog", BACKLOG),
        ("ledger", LEDGER),
        ("attempt log", ATTEMPT_LOG),
    ):
        text = read_text(path)
        require_tokens(
            label,
            text,
            (
                "Wave612",
                "DXParticleTexture__GetOrCreate",
                "DXParticleTexture__RenderAll",
                "2946",
                "1283",
                "CDXPatch__Constructor",
                "G:\\GhidraBackups\\BEA_20260519-234626_post_wave612_particle_texture_verified",
            ),
            failures,
        )

    tracking = read_json(TRACKING)
    if tracking.get("next_attempt_id") != 20268:
        failures.append(f"tracking next_attempt_id mismatch: {tracking.get('next_attempt_id')} != 20268")
    if tracking.get("counters", {}).get("attempt_rows") != 20268:
        failures.append(f"tracking attempt_rows mismatch: {tracking.get('counters', {}).get('attempt_rows')} != 20268")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    failures: list[str] = []
    check_logs(failures)
    check_metadata_and_tags(failures)
    check_exports(failures)
    check_backup_and_queue(failures)
    check_public_docs(failures)

    if failures:
        print("Wave612 particle texture probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave612 particle texture probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
