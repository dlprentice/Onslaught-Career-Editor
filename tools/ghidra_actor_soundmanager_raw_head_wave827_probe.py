#!/usr/bin/env python3
"""Validate Wave827 actor/SoundManager raw-head read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave827-actor-soundmanager-raw-head"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_actor_soundmanager_raw_head_wave827_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
ACTOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Actor.cpp" / "_index.md"
SOUNDMANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SoundManager.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-203238_post_wave827_actor_soundmanager_raw_head_verified"
NEXT_HEAD = "0x004e1260 CMonitor__UpdateTrackedValueAndDirection"

TARGETS = {
    "0x004df520": {
        "old": "CActor__dtor_base",
        "name": "CActor__dtor_base_Thunk",
        "signature": "void __fastcall CActor__dtor_base_Thunk(void * this)",
        "xref": ("0x004bfd03", "CActorBase__shared_scalar_deleting_dtor_004bfd00"),
        "comment": ("Wave827 static read-back/name correction", "one-instruction CActor destructor thunk", "0x004013d0"),
        "tags": {"actor", "destructor", "thunk", "name-corrected", "signature-verified"},
    },
    "0x004e0300": {
        "old": "CSoundManager__UpdateAllSoundVolumes",
        "name": "CSoundManager__UpdateVolumeForAllSoundEvents",
        "signature": "void __thiscall CSoundManager__UpdateVolumeForAllSoundEvents(void * this)",
        "xref": ("0x004e0134", "CSoundManager__Init"),
        "comment": ("UpdateVolumeForAllSoundEvents", "mFirstSoundEvent", "event+0x68/+0x64"),
        "tags": {"sound-manager", "sound-volume", "sound-event-list", "name-corrected", "signature-hardened"},
    },
    "0x004e04c0": {
        "old": "CSoundManager__SetMasterVolume",
        "name": "CSoundManager__SetMasterVolume",
        "signature": "void __thiscall CSoundManager__SetMasterVolume(void * this, float volume)",
        "xref": ("0x00421305", "CCareer__Load"),
        "comment": ("sound master volume", "CAREER_mSoundVolume", "Steam-build behavior"),
        "tags": {"sound-manager", "master-volume", "career-options", "signature-verified"},
    },
    "0x004e06b0": {
        "old": "CSoundManager__StopAllStreams",
        "name": "CSoundManager__DeleteAllSamples",
        "signature": "void __thiscall CSoundManager__DeleteAllSamples(void * this)",
        "xref": ("0x00517f22", "CSoundManager__ReinitializeAfterDeviceLoss"),
        "comment": ("DeleteAllSamples", "sample+0x74", "virtual deleting destructor"),
        "tags": {"sound-manager", "sample-list", "destructor", "name-corrected", "signature-hardened"},
    },
    "0x004e06e0": {
        "old": "CSoundManager__Shutdown",
        "name": "CSoundManager__Shutdown",
        "signature": "void __thiscall CSoundManager__Shutdown(void * this)",
        "xref": ("0x004f0183", "CLTShell__ShutdownRuntimeAndReleaseResources"),
        "comment": ("SoundManager teardown", "releases backend voice buffers", "global CEffect list"),
        "tags": {"sound-manager", "shutdown", "sample-list", "effect-list", "signature-hardened"},
    },
    "0x004e0820": {
        "old": "CSoundDefinition__Destructor",
        "name": "CEffect__scalar_deleting_dtor",
        "signature": "void * __thiscall CEffect__scalar_deleting_dtor(void * this, byte flags)",
        "xref": ("0x004e07bd", "CSoundManager__Shutdown"),
        "comment": ("CEffect scalar-deleting destructor", "this+0xd4", "this+0xd8"),
        "tags": {"sound-manager", "effect-list", "scalar-deleting-dtor", "name-corrected", "signature-hardened"},
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "actor-soundmanager-raw-head-wave827",
    "wave827-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
}

CORE_ANCHORS = (
    "Wave827 actor/SoundManager raw head",
    "actor-soundmanager-raw-head-wave827",
    "0x004df520 CActor__dtor_base_Thunk",
    "0x004e0300 CSoundManager__UpdateVolumeForAllSoundEvents",
    "0x004e06b0 CSoundManager__DeleteAllSamples",
    "0x004e0820 CEffect__scalar_deleting_dtor",
    "5640/6098 = 92.49%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime audio behavior proven",
    "runtime lifetime behavior proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
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
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 9,
        "pre-instructions.tsv": 1806,
        "pre-decompile/index.tsv": 6,
        "pre-context-metadata.tsv": 11,
        "pre-context-instructions.tsv": 2211,
        "pre-context-decompile/index.tsv": 11,
        "post-metadata.tsv": 6,
        "post-tags.tsv": 6,
        "post-xrefs.tsv": 9,
        "post-instructions.tsv": 1806,
        "post-decompile/index.tsv": 6,
        "post-context-metadata.tsv": 11,
        "post-context-instructions.tsv": 3311,
        "post-context-decompile/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    pre_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs: dict[str, list[dict[str, str]]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), []).append(row)

    for address, spec in TARGETS.items():
        old_row = pre_metadata.get(address)
        require(old_row is not None and old_row.get("name") == spec["old"], f"pre-state old name missing at {address}", failures)

        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == spec["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == spec["signature"], f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in spec["comment"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            expected_tags = COMMON_TAGS | spec["tags"]
            require(expected_tags.issubset(actual_tags), f"tags missing at {address}: {expected_tags - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == spec["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        xref_rows = xrefs.get(address, [])
        require(xref_rows, f"missing xref for {address}", failures)
        expected_from, expected_owner = spec["xref"]
        require(
            any(
                normalize_address(xref.get("from_addr", "")) == expected_from
                and xref.get("from_function") == expected_owner
                for xref in xref_rows
            ),
            f"missing representative xref at {address}: {expected_from} {expected_owner}",
            failures,
        )

    update_volume = read_text(BASE / "post-decompile" / "004e0300_CSoundManager__UpdateVolumeForAllSoundEvents.c")
    for token in ("*(void **)((int)this + 0xc)", "sound_event + 0x74", "sound_event + 0x68", "CSoundManager__UpdateChannelParams"):
        require(token in update_volume, f"missing update-volume decompile token: {token}", failures)

    delete_samples = read_text(BASE / "post-decompile" / "004e06b0_CSoundManager__DeleteAllSamples.c")
    for token in ("puVar2 = *(undefined4 **)this", "puVar2[0x1d]", "(**(code **)*puVar2)(1)", "*(undefined4 *)this = 0"):
        require(token in delete_samples, f"missing delete-samples decompile token: {token}", failures)

    effect_dtor = read_text(BASE / "post-decompile" / "004e0820_CEffect__scalar_deleting_dtor.c")
    for token in ("this + 0xd4", "g_pSoundDefinitionListHead", "this + 0xd8", "CDXMemoryManager__Free", "return this"):
        require(token in effect_dtor, f"missing effect-dtor decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=4 signature_updated=5 comment_only_updated=1 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=6 skipped=0 renamed=4 would_rename=0 signature_updated=4 comment_only_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=6 found=6 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "post-xrefs.log": "Wrote 9 rows",
        "post-instructions.log": "Wrote 1806 instruction rows",
        "post-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-context-metadata.log": "targets=11 found=11 missing=0",
        "post-context-instructions.log": "Wrote 3311 instruction rows",
        "post-context-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5640",
        "queue-probe.log": "Commentless functions: 458",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave827.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave827_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_text = read_text(BASE / "apply.log")
    for address, spec in TARGETS.items():
        require(f"READBACK_OK: {address} {spec['signature']}" in apply_text, f"missing readback token for {address}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 458, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5640, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5640, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004e1260", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CMonitor__UpdateTrackedValueAndDirection", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171576199 or backup.get("totalBytes") == 171576199.0, "backup byte count mismatch", failures)
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
        ACTOR_DOC,
        SOUNDMANAGER_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-actor-soundmanager-raw-head-wave827")
        == r"py -3 tools\ghidra_actor_soundmanager_raw_head_wave827_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave827 actor/SoundManager raw head" for row in ledger_rows), "missing Wave827 ledger row", failures)
    require(
        any(row.get("task") == "Wave827 actor/SoundManager raw head" and row.get("attempt_id") == 20482 for row in attempts),
        "missing Wave827 attempt row",
        failures,
    )


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
        print("Wave827 actor/SoundManager raw-head probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave827 actor/SoundManager raw-head probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
