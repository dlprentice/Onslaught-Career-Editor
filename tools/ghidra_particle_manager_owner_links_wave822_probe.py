#!/usr/bin/env python3
"""Validate Wave822 particle-manager owner-link read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave822-particle-manager-owner-links"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_particle_manager_owner_links_wave822_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
AIRUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AirUnit.cpp" / "CAirUnit__Init.md"
PLANE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Plane.cpp" / "_index.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshRenderer.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-180249_post_wave822_particle_manager_owner_links_verified"
NEXT_HEAD = "0x004cd7a0 CWorldPhysicsManager__FindNodeByNameGE"

TARGET_NAMES = {
    "0x004caf30": "CParticleManager__ClearParticleOwnerBacklinks",
    "0x004cb040": "ParticleEffectLink__PushGlobalList",
    "0x004cb080": "CParticleManager__PruneDeadOwnerLinks",
    "0x004cbc60": "CParticleManager__UpdateRenderNodesAndResetState",
}

TARGET_SIGNATURES = {
    "0x004caf30": "void __cdecl CParticleManager__ClearParticleOwnerBacklinks(void)",
    "0x004cb040": "void __fastcall ParticleEffectLink__PushGlobalList(void * link_node)",
    "0x004cb080": "void __cdecl CParticleManager__PruneDeadOwnerLinks(void)",
    "0x004cbc60": "void __cdecl CParticleManager__UpdateRenderNodesAndResetState(void)",
}

COMMENT_TOKENS = {
    "0x004caf30": (
        "Wave822 static read-back",
        "DAT_0082b3e4",
        "+0xa4/+0xa8",
        "CGame__ShutdownRestartLoop",
        "CDXEngine__ShutdownParticleSystemBundle",
        "CFrontEnd__ReleaseParticleHudWaypointResources",
    ),
    "0x004cb040": (
        "Wave822 static read-back/name/signature correction",
        "ECX carries link_node",
        "DAT_0082b3e8",
        "CWorldPhysicsManager-only label",
        "reads no stack parameter",
    ),
    "0x004cb080": (
        "Wave822 static read-back",
        "DAT_0082b3e8",
        "link_node+0x4",
        "+0xa4",
        "CParticleManager__ClearParticleOwnerBacklinks",
    ),
    "0x004cbc60": (
        "Wave822 static read-back",
        "DAT_0082b404",
        "vfunc +0x4",
        "observed type 0xb",
        "vfunc +0x5c",
        "RenderState_Set",
    ),
}

TARGET_XREFS = {
    "0x004caf30": {"0x0046ccad", "0x0054f709", "0x004691fd"},
    "0x004cb040": {"0x00402c00", "0x0040ef95", "0x004c54b4", "0x00507511", "0x004d1b85"},
    "0x004cb080": {"0x0046ccb2", "0x0054f70e", "0x00469202"},
    "0x004cbc60": {"0x0053e8c3", "0x00540edc"},
}

COMMON_TAGS = {
    "static-reaudit",
    "particle-manager-owner-links-wave822",
    "wave822-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "particle-manager",
    "owner-link",
}

EXTRA_TAGS = {
    "0x004caf30": {"effect-handle", "shutdown-cleanup"},
    "0x004cb040": {"effect-owner-link", "global-list", "name-corrected"},
    "0x004cb080": {"global-list", "owner-link-prune", "shutdown-cleanup"},
    "0x004cbc60": {"render-node", "render-state"},
}

HELPER_NAMES = {
    "CParticleManager__AppendNodeToActiveList",
    "CParticleManager__UnlinkNodeFromActiveList",
    "CParticle__Destroy",
    "CParticleManager__CleanupHandles",
    "CParticleManager__RemoveFromGlobalList",
    "ParticleEffectLink__SetHandleStateAndClear",
    "CParticleManager__Update",
    "CParticleManager__UpdateParticleAndRecycleIfDead",
    "CParticleManager__UpdateParticles",
    "CParticleManager__PruneDeadParticles",
    "CParticleManager__DestroyParticleList",
    "CParticleManager__LinkNodeByOffset3C40",
    "CParticleManager__UnlinkNodeByOffset3C40",
}

CORE_ANCHORS = (
    "Wave822 particle manager owner links",
    "particle-manager-owner-links-wave822",
    "0x004caf30 CParticleManager__ClearParticleOwnerBacklinks",
    "0x004cb040 ParticleEffectLink__PushGlobalList",
    "0x004cb080 CParticleManager__PruneDeadOwnerLinks",
    "0x004cbc60 CParticleManager__UpdateRenderNodesAndResetState",
    "5626/6098 = 92.26%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime particle shutdown behavior proven",
    "runtime particle/effect behavior proven",
    "runtime render behavior proven",
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
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 46,
        "pre-instructions.tsv": 1684,
        "pre-helper-metadata.tsv": 13,
        "pre-helper-instructions.tsv": 2353,
        "pre-decompile/index.tsv": 4,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 46,
        "post-instructions.tsv": 1684,
        "post-helper-metadata.tsv": 13,
        "post-helper-instructions.tsv": 2353,
        "post-decompile/index.tsv": 4,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    xrefs: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))

    require(HELPER_NAMES.issubset(helper_names), f"missing helper rows: {HELPER_NAMES - helper_names}", failures)

    for address, name in TARGET_NAMES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == TARGET_SIGNATURES[address], f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
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

    renamed_decompile = BASE / "post-decompile" / "004cb040_ParticleEffectLink__PushGlobalList.c"
    text = read_text(renamed_decompile)
    for token in ("void __fastcall ParticleEffectLink__PushGlobalList(void *link_node)", "DAT_0082b3e8 = link_node"):
        require(token in text, f"missing renamed decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=1 signature_updated=4 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=1 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=4 missing=0",
        "post-xrefs.log": "Wrote 46 rows",
        "post-instructions.log": "Wrote 1684 instruction rows",
        "post-helper-metadata.log": "targets=13 found=13 missing=0",
        "post-helper-instructions.log": "Wrote 2353 instruction rows",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5626",
        "queue-probe.log": "Commentless functions: 472",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave822.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave822_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 472, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["commentlessHighSignal"] == [], "high-signal queue should be empty", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)
    require(queue["priorityQueues"]["nameConfidence"] == [], "name-confidence queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5626, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5626, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x004cd7a0", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CWorldPhysicsManager__FindNodeByNameGE", "raw commentless head name mismatch", failures)

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
        PARTICLE_DOC,
        AIRUNIT_DOC,
        PLANE_DOC,
        MESH_DOC,
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
        scripts.get("test:ghidra-particle-manager-owner-links-wave822")
        == r"py -3 tools\ghidra_particle_manager_owner_links_wave822_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave822 particle manager owner links" for row in ledger_rows), "missing Wave822 ledger row", failures)
    require(
        any(row.get("task") == "Wave822 particle manager owner links" and row.get("attempt_id") == 20477 for row in attempts),
        "missing Wave822 attempt row",
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
        print("Wave822 particle-manager owner-links probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave822 particle-manager owner-links probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
