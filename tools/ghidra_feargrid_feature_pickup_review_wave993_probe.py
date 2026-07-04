#!/usr/bin/env python3
"""Validate Wave993 FearGrid/Feature/pickup read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave993-feargrid-feature-pickup-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_feargrid_feature_pickup_review_wave993_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FEARGRID_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FearGrid.cpp" / "_index.md"
FEATURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Feature.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
TRACKING_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-061908_post_wave993_feargrid_feature_pickup_review_verified"

TARGETS = {
    "0x0040dda0": ("CUnitAI__RefreshGridCooldownFromOccupiedCells", "void __thiscall CUnitAI__RefreshGridCooldownFromOccupiedCells(void * this)"),
    "0x0044c3d0": ("CFearGrid__ctor_base", "void * __thiscall CFearGrid__ctor_base(void * this, int grid_id)"),
    "0x0044c440": ("CFearGrid__RebuildOccupancyAndScheduleTick", "void __thiscall CFearGrid__RebuildOccupancyAndScheduleTick(void * this)"),
    "0x0044c720": ("CFearGrid__GetOccupancyAtWorldVector", "int __thiscall CFearGrid__GetOccupancyAtWorldVector(void * this, float vector_x, float vector_y, float vector_z, float vector_w)"),
    "0x0044c780": ("CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta", "int __thiscall CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta(void * this, float vector_x, float vector_y, float vector_z, float vector_w)"),
    "0x0044c810": ("CFearGrid__FindNearestFreeCellSpiral", "void __thiscall CFearGrid__FindNearestFreeCellSpiral(void * this, void * inout_world_vector)"),
    "0x0044ca30": ("CFeature__Init", "void __thiscall CFeature__Init(void * this, void * init)"),
    "0x0044cbe0": ("CFeature__ShutdownAndRemoveFromWorld", "void __fastcall CFeature__ShutdownAndRemoveFromWorld(void * feature)"),
    "0x0044cee0": ("CFeature__MaybeSpawnRandomPickupFromData", "void __fastcall CFeature__MaybeSpawnRandomPickupFromData(void * feature)"),
    "0x0044e300": ("PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300", "void __fastcall PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300(void * object)"),
    "0x004e7110": ("CSquadNormal__Process", "int __thiscall CSquadNormal__Process(void * this, void * process_arg)"),
}

WAVE993_TARGET = "0x0044c440"
WAVE993_TAGS = {
    "static-reaudit",
    "feargrid-feature-pickup-review-wave993",
    "wave993-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "tag-corrected",
    "fear-grid",
    "tracked-object-weight",
    "wave826-normalized",
}

DOC_TOKENS = (
    "Wave993",
    "feargrid-feature-pickup-review-wave993",
    "0x0044c440 CFearGrid__RebuildOccupancyAndScheduleTick",
    "FearGridTrackedObject__LookupFearWeightByArchetype",
    "0x0044cee0 CFeature__MaybeSpawnRandomPickupFromData",
    "0x0044e300 PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300",
    "447/1408 = 31.75%",
    "549/1478 = 37.14%",
    "6222/6222 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime ai/fear behavior proven",
    "runtime pickup behavior proven",
    "exact layout proven",
    "source identity proven",
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


def contains_path_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\\\\\") in text


def check_exports(failures: list[str]) -> None:
    expected_counts = {
        "metadata.tsv": 11,
        "tags.tsv": 11,
        "xrefs.tsv": 19,
        "instructions.tsv": 1893,
        "decompile/index.tsv": 11,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 19,
        "post-instructions.tsv": 1893,
        "post-decompile/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "post-metadata.tsv")
    tags = read_tsv(BASE / "post-tags.tsv")
    decompile_index = read_tsv(BASE / "post-decompile" / "index.tsv")
    for address, (name, signature) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}", failures)
            require(row.get("comment", "").strip() != "", f"metadata comment missing {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

    row = row_by_address(metadata, WAVE993_TARGET)
    require(row is not None, "Wave993 target metadata missing", failures)
    if row:
        comment = row.get("comment", "")
        for token in (
            "Wave993 FearGrid/Feature/pickup review",
            "FearGridTrackedObject__LookupFearWeightByArchetype",
            "stale Wave366 callee-owner wording",
            "Wave826 proved",
        ):
            require(token in comment, f"missing Wave993 comment token: {token}", failures)
        require("CFearGrid__LookupFearWeightByArchetype for occupancy marks" not in comment, "stale CFearGrid callee wording remains", failures)

    tag_row = row_by_address(tags, WAVE993_TARGET)
    require(tag_row is not None, "Wave993 target tags missing", failures)
    if tag_row:
        actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
        require(WAVE993_TAGS.issubset(actual_tags), f"missing Wave993 tags: {WAVE993_TAGS - actual_tags}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    for target, source, owner in (
        ("0x0044c440", "0x0044c406", "CFearGrid__ctor_base"),
        ("0x0044c720", "0x0040ddf3", "CUnitAI__RefreshGridCooldownFromOccupiedCells"),
        ("0x0044c720", "0x004e751d", "CSquadNormal__Process"),
        ("0x0044c780", "0x00507b5b", "OID__CanFireAtTarget_BallisticArcA"),
        ("0x0044c810", "0x004e752d", "CSquadNormal__Process"),
        ("0x0044cee0", "0x0044ccf1", "<no_function>"),
        ("0x0044e300", "0x0044e536", "PickupSpawn__UpdateAttachedPickupBurst_0044e4e0"),
    ):
        require(
            any(
                normalize_address(row.get("target_addr", "")) == normalize_address(target)
                and normalize_address(row.get("from_addr", "")) == normalize_address(source)
                and row.get("from_function") == owner
                for row in xrefs
            ),
            f"missing xref {source} -> {target} from {owner}",
            failures,
        )


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_logs = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 comment_only_updated=1 tags_added=5 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 comment_only_updated=1 tags_added=5 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=11 found=11 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "post-xrefs.log": "Wrote 19 rows",
        "post-instructions.log": "targets=11 missing=0",
        "post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "Script not found", "BADADDR", "BADNAME", "BADSIG", "BADCOMMENT", "BADTAGS", "FAIL:", "missing=1", "failed=1"):
            require(bad not in text, f"bad log token {relative}: {bad}", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6222, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "queue commentless mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "queue undefined mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "queue param_N mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173869959 or backup.get("totalBytes") == 173869959.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        FEARGRID_DOC,
        FEATURE_DOC,
        BACKLOG,
        TRACKING_STATE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_path_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:ghidra-feargrid-feature-pickup-review-wave993")
        == r"py -3 tools\ghidra_feargrid_feature_pickup_review_wave993_probe.py --check",
        "missing Wave993 package script",
        failures,
    )
    require(
        package.get("scripts", {}).get("test:ghidra-wave900-plus-through-wave993-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 993 --check",
        "missing Wave900-Wave993 recheck package script",
        failures,
    )

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave993 FearGrid Feature pickup comment-tag normalization" for row in ledger), "missing Wave993 ledger row", failures)
    require(any(row.get("task") == "Wave993 FearGrid Feature pickup comment-tag normalization" and row.get("attempt_id") == 20579 for row in attempts), "missing Wave993 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_exports(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave993 FearGrid/Feature/pickup probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave993 FearGrid/Feature/pickup probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
