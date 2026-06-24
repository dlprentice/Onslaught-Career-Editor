#!/usr/bin/env python3
"""Validate Wave853 SoundManager backend-tail read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave853-soundmanager-backend-tail"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_soundmanager_backend_tail_wave853_2026-05-25.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PCSOUNDMANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "pcsoundmanager.cpp" / "_index.md"
SOUNDMANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SoundManager.cpp" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

TASK = "Wave853 SoundManager backend tail"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260525-101054_post_wave853_soundmanager_backend_tail_verified"
NEXT_HEAD = "0x0051a6a0 CFastVB__RenderIndexedImmediate"

COMMON_TAGS = {
    "static-reaudit",
    "soundmanager-backend-tail-wave853",
    "wave853-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "source-reference-soundmanager",
    "pc-sound-backend",
}

TARGETS = {
    "0x005168d0": {
        "name": "CPCSample__dtor",
        "signature": "void __fastcall CPCSample__dtor(void * this)",
        "tokens": ("CPCSample destructor body", "CSoundManager__KillAllInstancesOfSample", "this+0x78", "this+0x80"),
        "tags": {"name-corrected", "cpcsample", "sample-lifetime", "directsound-buffer"},
    },
    "0x00516960": {
        "name": "CPCSample__scalar_deleting_dtor",
        "signature": "void * __thiscall CPCSample__scalar_deleting_dtor(void * this, uchar free_flag)",
        "tokens": ("CPCSample scalar deleting destructor", "0x005e4988", "vtable slot 0"),
        "tags": {"name-corrected", "cpcsample", "scalar-deleting-dtor", "vtable-slot"},
    },
    "0x00516980": {
        "name": "CPCSoundManager__GetDeviceCount",
        "signature": "int __cdecl CPCSoundManager__GetDeviceCount(void)",
        "tokens": ("DAT_00896ca0", "PC sound-options", "0x004cf1f0"),
        "tags": {"device-enumeration", "frontend-options"},
    },
    "0x00516990": {
        "name": "CPCSoundManager__GetDeviceInfoPtr",
        "signature": "void * __cdecl CPCSoundManager__GetDeviceInfoPtr(int index)",
        "tokens": ("DAT_008964ec", "index*0x78", "CPCSoundManager__GetDeviceCount"),
        "tags": {"device-enumeration", "frontend-options", "record-stride-0x78"},
    },
    "0x005171e0": {
        "name": "CPCSoundManager__DeviceShutdown",
        "signature": "void __fastcall CPCSoundManager__DeviceShutdown(void * this)",
        "tokens": ("DeviceShutdown", "Shutting down sound device", "this+0x1c4", "this+0x2c8"),
        "tags": {"name-corrected", "device-shutdown", "directsound-release", "voice-buffer"},
    },
    "0x00517260": {
        "name": "CPCSoundManager__DeviceReset",
        "signature": "void __fastcall CPCSoundManager__DeviceReset(void * this)",
        "tokens": ("DeviceReset", "this+0xc4", "slot 0x48"),
        "tags": {"name-corrected", "device-reset", "directsound-stop", "voice-buffer"},
    },
    "0x00517290": {
        "name": "CPCSoundManager__LoadSampleFromBuffer_StubFail",
        "signature": "void * __stdcall CPCSoundManager__LoadSampleFromBuffer_StubFail(void * mem_buffer, int music)",
        "tokens": ("XOR EAX,EAX; RET 0x8", "LoadSampleFromBuffer", "unimplemented PC stub"),
        "tags": {"name-corrected", "signature-corrected", "stub", "sample-loading"},
    },
    "0x00517790": {
        "name": "CPCSoundManager__PlaySound",
        "signature": "void __thiscall CPCSoundManager__PlaySound(void * this, void * sound_event)",
        "tokens": ("PlaySound backend", "DirectSound buffer", "CSoundManager__UpdateSoundPosition", "event+0x08"),
        "tags": {"name-corrected", "playback", "directsound-buffer", "channel"},
    },
    "0x00517960": {
        "name": "CPCSoundManager__UnPauseSound",
        "signature": "void __thiscall CPCSoundManager__UnPauseSound(void * this, void * sound_event)",
        "tokens": ("UnPauseSound", "this+0xc4", "event looping flag"),
        "tags": {"name-corrected", "unpause", "directsound-play", "channel"},
    },
    "0x00517990": {
        "name": "CPCSoundManager__PauseSound",
        "signature": "void __thiscall CPCSoundManager__PauseSound(void * this, void * sound_event)",
        "tokens": ("PauseSound", "this+0xc4", "DirectSound Stop"),
        "tags": {"name-corrected", "pause", "directsound-stop", "channel"},
    },
    "0x005179b0": {
        "name": "CPCSoundManager__StopSound",
        "signature": "void __thiscall CPCSoundManager__StopSound(void * this, void * sound_event)",
        "tokens": ("StopSound", "this+0xc4", "this+0x1c4", "CSoundManager__StopSoundEvent"),
        "tags": {"name-corrected", "stop-sound", "directsound-release", "channel"},
    },
    "0x00517a20": {
        "name": "CPCSoundManager__UpdateGlobals",
        "signature": "void __fastcall CPCSoundManager__UpdateGlobals(void * this)",
        "tokens": ("UpdateGlobals", "DS3DLISTENER", "this+0x2c4", "deferred flag 1"),
        "tags": {"name-corrected", "listener", "directsound3d", "update-globals"},
    },
    "0x00517ad0": {
        "name": "CSoundManager__GetOutputEnabledFlag",
        "signature": "uchar __cdecl CSoundManager__GetOutputEnabledFlag(void)",
        "tokens": ("DAT_00896c58", "CSoundManager__PlayEffect", "effect can proceed"),
        "tags": {"audio-gate", "global-flag", "play-effect"},
    },
    "0x00517ae0": {
        "name": "CPCSoundManager__UpdateSound",
        "signature": "void __thiscall CPCSoundManager__UpdateSound(void * this, void * sound_event, int first_time)",
        "tokens": ("UpdateSound backend", "this+0x1c4", "slot 0x3c", "DAT_008964d0"),
        "tags": {"name-corrected", "update-sound", "directsound3d", "channel-params"},
    },
    "0x00517c40": {
        "name": "CPCSoundManager__UpdatesDone",
        "signature": "void __fastcall CPCSoundManager__UpdatesDone(void * this)",
        "tokens": ("UpdatesDone", "this+0x2c4", "slot 0x44"),
        "tags": {"name-corrected", "listener", "commit-deferred", "directsound3d"},
    },
    "0x00517c60": {
        "name": "CPCSoundManager__GetSampleLength",
        "signature": "double __stdcall CPCSoundManager__GetSampleLength(void * sample)",
        "tokens": ("GetSampleLength", "44100/22050/11025", "sample+0x7c"),
        "tags": {"name-corrected", "sample-length", "timing", "sample-rate"},
    },
    "0x00517cb0": {
        "name": "CPCSoundManager__FindFreeChannel",
        "signature": "int __fastcall CPCSoundManager__FindFreeChannel(void * this)",
        "tokens": ("FindFreeChannel", "this+0x2cc", "DAT_00896994"),
        "tags": {"name-corrected", "channel-allocation", "voice-count"},
    },
    "0x00517d00": {
        "name": "CSoundManager__LoadCompressedSampleBank",
        "signature": "void __thiscall CSoundManager__LoadCompressedSampleBank(void * this, char stream_mode)",
        "tokens": ("compressed sample-bank loader", "this+0x88", "CDXMemBuffer__InitFromFile", "CSoundManager__CreateSample"),
        "tags": {"compressed-sample-bank", "xap", "language-bank", "mem-buffer"},
    },
}

STRING_EXPECTATIONS = {
    "string-00632428.tsv": r"C:\dev\ONSLAUGHT2\SoundManager.cpp",
    "string-0063e46c.tsv": r"C:\dev\ONSLAUGHT2\pcsoundmanager.cpp",
    "string-0063e750.tsv": "Shutting down sound device\\x0a",
    "string-0063e76c.tsv": "Failed to create sample\\x0a",
    "string-0063e788.tsv": "Caching sample %s\\x0a",
    "string-0063e79c.tsv": "Caching %d samples from PC XAP\\x0a",
    "string-0063e7bc.tsv": "Loading PC XAP file\\x0a",
    "string-0063e7ec.tsv": "Not loading compressed sounds.\\x0a",
    "string-0063e80c.tsv": "Not loading XAP during resource build\\x0a",
    "string-0063e2b0.tsv": r"%s\data\sounds\sounds_%s_pc.xap",
}

CORE_DOC_TOKENS = (
    TASK,
    "soundmanager-backend-tail-wave853",
    "0x005168d0 CPCSample__dtor",
    "0x00516960 CPCSample__scalar_deleting_dtor",
    "0x005171e0 CPCSoundManager__DeviceShutdown",
    "0x00517290 CPCSoundManager__LoadSampleFromBuffer_StubFail",
    "0x00517790 CPCSoundManager__PlaySound",
    "0x00517ae0 CPCSoundManager__UpdateSound",
    "0x00517d00 CSoundManager__LoadCompressedSampleBank",
    "5754/6098 = 94.36%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime directsound playback proven",
    "runtime sample-bank loading proven",
    "fully reverse-engineered",
    "rebuild parity proven",
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


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 18,
        "pre-tags.tsv": 18,
        "pre-xrefs.tsv": 40,
        "pre-instructions.tsv": 3978,
        "pre-decompile/index.tsv": 18,
        "pre-context-metadata.tsv": 12,
        "pre-context-decompile/index.tsv": 12,
        "pre-vtable-005e4988.tsv": 32,
        "post-metadata.tsv": 18,
        "post-tags.tsv": 18,
        "post-xrefs.tsv": 40,
        "post-instructions.tsv": 666,
        "post-decompile/index.tsv": 18,
        "post-context-metadata.tsv": 12,
        "post-context-decompile/index.tsv": 12,
        "post-vtable-005e4988.tsv": 32,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    for relative, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / relative)
        require(rows and rows[0].get("cstring") == expected, f"{relative} string mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"common tags missing at {address}", failures)
            require(set(expected["tags"]).issubset(actual_tags), f"specific tags missing at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    vtable = read_tsv(BASE / "post-vtable-005e4988.tsv")
    slot0 = vtable[0] if vtable else {}
    require(slot0.get("pointer_addr") == "00516960", "CPCSample vtable slot 0 pointer mismatch", failures)
    require(slot0.get("function_name") == "CPCSample__scalar_deleting_dtor", "CPCSample vtable slot 0 name mismatch", failures)

    source = read_text(BASE / "source-context.txt")
    for token in ("SOUND.UnloadSample(this)", "CPCSoundManager::DeviceShutdown", "LoadSampleFromBuffer", "CPCSoundManager::PlaySound", "CPCSoundManager::FindFreeChannel", "CSoundManager::StartSoundEvent"):
        require(token in source, f"missing source context token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=18 renamed=0 would_rename=14 signature_updated=4 comment_only_updated=18 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=18 skipped=0 renamed=14 would_rename=14 signature_updated=4 comment_only_updated=18 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=18 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=18 found=18 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=18 missing=0",
        "post-xrefs.log": "Wrote 40 rows",
        "post-instructions.log": "Wrote 666 instruction rows",
        "post-decompile.log": "targets=18 dumped=18 missing=0 failed=0",
        "post-context-metadata.log": "targets=12 found=12 missing=0",
        "post-context-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "post-vtable-005e4988.log": "ExportVtableSlots complete: targets=1 rows=32",
        "quality-refresh.log": "total_functions=6098 commented_functions=5754",
        "queue-probe.log": "Commentless functions: 344",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave853.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave853_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 344, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue not empty", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5754, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5754, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0051a6a0", "raw head address mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CFastVB__RenderIndexedImmediate", "raw head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 172133255, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    common_owner_tokens = (TASK, "soundmanager-backend-tail-wave853", "5754/6098 = 94.36%", NEXT_HEAD, BACKUP_PATH)
    owner_docs = {
        PCSOUNDMANAGER_DOC: (
            "0x005168d0 CPCSample__dtor",
            "0x005171e0 CPCSoundManager__DeviceShutdown",
            "0x00517790 CPCSoundManager__PlaySound",
            "0x00517cb0 CPCSoundManager__FindFreeChannel",
        ),
        SOUNDMANAGER_DOC: (
            "0x00517ad0 CSoundManager__GetOutputEnabledFlag",
            "0x00517d00 CSoundManager__LoadCompressedSampleBank",
            "CPCSoundManager__UpdateSound",
            "DirectSound backend",
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in common_owner_tokens + tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-soundmanager-backend-tail-wave853")
        == r"py -3 tools\ghidra_soundmanager_backend_tail_wave853_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == TASK for row in ledger_rows), "missing Wave853 ledger row", failures)
    require(any(row.get("task") == TASK and row.get("attempt_id") == 20508 for row in attempts), "missing Wave853 attempt row", failures)


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
        print("Wave853 SoundManager backend-tail probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave853 SoundManager backend-tail probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
