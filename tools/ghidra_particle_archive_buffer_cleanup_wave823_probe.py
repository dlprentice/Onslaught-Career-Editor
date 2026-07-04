#!/usr/bin/env python3
"""Validate Wave823 particle archive/buffer cleanup read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave823-particle-archive-buffer-cleanup"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_particle_archive_buffer_cleanup_wave823_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleSet.cpp" / "_index.md"
DXMEMBUFFER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMemBuffer.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-183746_post_wave823_particle_archive_buffer_cleanup_verified"
NEXT_HEAD = "0x004cf050 CMenuItem__Destructor"

TARGET_NAMES = {
    "0x004cd7a0": "CParticleSet__FindByNameAndTrackLinkSlot",
    "0x004cdb90": "CDXMemBuffer__dtor_base_Thunk",
}

TARGET_SIGNATURES = {
    "0x004cd7a0": "void * __thiscall CParticleSet__FindByNameAndTrackLinkSlot(void * this, char * set_name)",
    "0x004cdb90": "void __fastcall CDXMemBuffer__dtor_base_Thunk(void)",
}

COMMENT_TOKENS = {
    "0x004cd7a0": (
        "Wave823 static read-back/name/signature correction",
        "&DAT_0082b400",
        "RET 0x4",
        "DAT_0082b3f8",
        "+0x38",
        "+0x4",
        "stricmp",
        "CWorldPhysicsManager-owned label",
        "unused_ctx phantom parameter",
    ),
    "0x004cdb90": (
        "Wave823 static read-back/name correction",
        "single-instruction jump thunk",
        "0x00547d90 CDXMemBuffer__dtor_base",
        "0x005d4230 Unwind@005d4230",
        "ParticleSet.cpp cleanup",
        "EBP-0x140",
        "not the destructor body itself",
    ),
}

TARGET_XREFS = {
    "0x004cd7a0": {"0x00510588", "0x00511cb0", "0x00404ef4", "0x004d8059", "0x0053d745"},
    "0x004cdb90": {"0x005d4236"},
}

COMMON_TAGS = {
    "static-reaudit",
    "particle-archive-buffer-cleanup-wave823",
    "wave823-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "particle-set",
    "cdxmembuffer",
}

EXTRA_TAGS = {
    "0x004cd7a0": {"name-corrected", "sorted-name-list", "link-slot-cursor"},
    "0x004cdb90": {"name-corrected", "jump-thunk", "particleset-cleanup"},
}

HELPER_NAMES = {
    "CDXMemBuffer__OpenReadMode11",
    "CDXMemBuffer__Close_Thunk",
    "CParticleSet__CreateByType",
    "CParticleSet__Init",
    "CParticleSet__dtor_base",
    "CParticleSet__LoadFromArchive",
    "CParticleSet__LoadParticleSetFile",
    "CParticleManager__LinkNodeByOffset3C40",
    "CParticleManager__UnlinkNodeByOffset3C40",
    "CDXMemBuffer__ctor",
    "CDXMemBuffer__dtor_base",
    "CDXMemBuffer__InitFromFile",
    "CDXMemBuffer__Read",
    "CDXMemBuffer__Close",
}

CORE_ANCHORS = (
    "Wave823 particle archive buffer cleanup",
    "particle-archive-buffer-cleanup-wave823",
    "0x004cd7a0 CParticleSet__FindByNameAndTrackLinkSlot",
    "0x004cdb90 CDXMemBuffer__dtor_base_Thunk",
    "5628/6098 = 92.29%",
    NEXT_HEAD,
    BACKUP_PATH,
)

PARTICLE_DOC_TOKENS = (
    "Wave823",
    "particle-archive-buffer-cleanup-wave823",
    "0x004cd7a0 CParticleSet__FindByNameAndTrackLinkSlot",
    "&DAT_0082b400",
    "DAT_0082b3f8",
    "RET 0x4",
    "0x004cdb90 CDXMemBuffer__dtor_base_Thunk",
    BACKUP_PATH,
)

DXMEMBUFFER_DOC_TOKENS = (
    "Wave823",
    "particle-archive-buffer-cleanup-wave823",
    "0x004cdb90 CDXMemBuffer__dtor_base_Thunk",
    "0x00547d90 CDXMemBuffer__dtor_base",
    "0x005d4230 Unwind@005d4230",
    "EBP-0x140",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime particle/effect lookup behavior proven",
    "runtime particle archive behavior proven",
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
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 46,
        "pre-instructions.tsv": 490,
        "pre-helper-metadata.tsv": 14,
        "pre-helper-instructions.tsv": 2030,
        "pre-caller-decompile/index.tsv": 8,
        "pre-caller-instructions.tsv": 840,
        "pre-decompile/index.tsv": 2,
        "post-apply-metadata.tsv": 2,
        "post-metadata.tsv": 2,
        "post-tags.tsv": 2,
        "post-xrefs.tsv": 46,
        "post-instructions.tsv": 490,
        "post-helper-metadata.tsv": 14,
        "post-helper-instructions.tsv": 2030,
        "post-caller-decompile/index.tsv": 8,
        "post-caller-instructions.tsv": 840,
        "post-decompile/index.tsv": 2,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    post_apply_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-apply-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    xrefs: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))

    require(HELPER_NAMES.issubset(helper_names), f"missing helper rows: {HELPER_NAMES - helper_names}", failures)

    for address, name in TARGET_NAMES.items():
        row = metadata.get(address)
        post_apply_row = post_apply_metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        require(post_apply_row is not None, f"missing post-apply metadata for {address}", failures)
        for candidate, label in ((row, "post"), (post_apply_row, "post-apply")):
            if candidate is None:
                continue
            require(candidate.get("name") == name, f"{label} name mismatch at {address}", failures)
            require(candidate.get("signature") == TARGET_SIGNATURES[address], f"{label} signature mismatch at {address}: {candidate.get('signature')}", failures)
            require(candidate.get("status") == "OK", f"{label} metadata status mismatch at {address}", failures)

        if row is not None:
            comment = row.get("comment", "")
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = COMMON_TAGS | EXTRA_TAGS[address]
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == TARGET_SIGNATURES[address], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(TARGET_XREFS[address].issubset(xrefs.get(address, set())), f"xrefs missing at {address}", failures)

    particle_decompile = read_text(BASE / "post-decompile" / "004cd7a0_CParticleSet__FindByNameAndTrackLinkSlot.c")
    for token in ("CParticleSet__FindByNameAndTrackLinkSlot", "stricmp", "DAT_0082b3f8"):
        require(token in particle_decompile, f"missing particle decompile token: {token}", failures)

    thunk_decompile = read_text(BASE / "post-decompile" / "004cdb90_CDXMemBuffer__dtor_base_Thunk.c")
    for token in ("CDXMemBuffer__dtor_base_Thunk", "CDXMemBuffer__dtor_base"):
        require(token in thunk_decompile, f"missing thunk decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=2 signature_updated=2 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=2 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=1",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-apply-metadata.log": "targets=2 found=2 missing=0",
        "post-metadata.log": "targets=2 found=2 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-xrefs.log": "Wrote 46 rows",
        "post-instructions.log": "Wrote 490 instruction rows",
        "post-helper-metadata.log": "targets=14 found=14 missing=0",
        "post-helper-instructions.log": "Wrote 2030 instruction rows",
        "post-caller-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "post-caller-instructions.log": "Wrote 840 instruction rows",
        "post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5628",
        "queue-probe.log": "Commentless functions: 470",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave823.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave823_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        bad_tokens = ("LockException", "MISSING:", "BADNAME:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "failed=1")
        if relative != "apply.log":
            bad_tokens = bad_tokens + ("BADSIG:", "bad=1")
        for bad in bad_tokens:
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    apply_text = read_text(BASE / "apply.log")
    require("BADSIG: 0x004cd7a0" in apply_text, "missing expected apply-log BADSIG diagnostic", failures)
    require("actual=void * __thiscall CParticleSet__FindByNameAndTrackLinkSlot(void * this, char * set_name)" in apply_text, "missing expected saved-signature diagnostic", failures)
    final_text = read_text(BASE / "apply-final-dry.log")
    require("BADSIG:" not in final_text, "final dry should not have BADSIG", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 470, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5628, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5628, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004cf050", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CMenuItem__Destructor", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171543431 or backup.get("totalBytes") == 171543431.0, "backup byte count mismatch", failures)
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
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in ((PARTICLE_DOC, PARTICLE_DOC_TOKENS), (DXMEMBUFFER_DOC, DXMEMBUFFER_DOC_TOKENS)):
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-particle-archive-buffer-cleanup-wave823")
        == r"py -3 tools\ghidra_particle_archive_buffer_cleanup_wave823_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave823 particle archive buffer cleanup" for row in ledger_rows), "missing Wave823 ledger row", failures)
    require(
        any(row.get("task") == "Wave823 particle archive buffer cleanup" and row.get("attempt_id") == 20478 for row in attempts),
        "missing Wave823 attempt row",
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
        print("Wave823 particle archive/buffer cleanup probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave823 particle archive/buffer cleanup probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
