#!/usr/bin/env python3
"""Validate Wave1121 mixed score-24 current-risk review."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1121-mixed-score24-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1121-mixed-score24-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1121-mixed-score24-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1121_mixed_score24_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

UNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
UNIT_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md"
MESH_COLLISION_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md"
MESH_COLLISION_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "MeshCollisionVolume.cpp" / "_index.md"
VERTEX_SHADER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
VERTEX_SHADER_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"

BACKUP = r"G:\GhidraBackups\BEA_20260605-033658_post_wave1121_mixed_score24_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-025952_post_wave1120_mixed_score25_current_risk_review_verified"
STALE_SLOT2_PHRASE = "remains an unrecovered no-function-at-pointer boundary"

PRIOR_PROBES = (
    "wave1109_cfastvb_current_risk_head_supersession.py",
    "wave1110_cfastvb_wave1053_remainder_supersession.py",
    "wave1111_cnamedmesh_current_risk_supersession.py",
    "wave1112_animal_wave1016_current_risk_supersession.py",
    "wave1113_battleengine_wave936_wave1010_current_risk_supersession.py",
    "wave1114_mixed_score27_current_risk_head_supersession.py",
    "wave1115_unitai_carver_motion_activation_current_risk_review.py",
    "wave1116_door_wing_ai_current_risk_review.py",
    "wave1117_cengine_current_risk_review.py",
    "wave1118_particle_message_current_risk_review.py",
    "wave1119_mixed_score26_current_risk_review.py",
    "wave1120_mixed_score25_current_risk_review.py",
)

TARGETS = {
    "0x004037a0": (
        "SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0",
        "void __thiscall SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0(void * this, void * hitContext, void * sourceThing, void * arg2, void * arg3)",
        ("Wave1086", "CUnit__ApplyDamage", "selector 0x19", "RET 0x10"),
        ("0x005e2ec0", "<no_function>", "DATA"),
        ("CUnit__ApplyDamage", "0x160", "0x19"),
    ),
    "0x004ac6e0": (
        "CMeshCollisionVolume__VFunc_03_004ac6e0",
        "int __thiscall CMeshCollisionVolume__VFunc_03_004ac6e0(void * this, void * query_arg0, float * motion_record, void * query_arg2, void * contact_record)",
        ("Wave446", "0x005d95d4", "swept-sphere", "contact normal"),
        ("0x005d95d4", "<no_function>", "DATA"),
        ("CMeshCollisionVolume__TestSweptSphereAgainstBounds", "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart", "CMeshCollisionVolume__ResolveContactNormalAndPlane"),
    ),
    "0x004ad830": (
        "CMeshCollisionVolume__VFunc_04_004ad830",
        "int __thiscall CMeshCollisionVolume__VFunc_04_004ad830(void * this, void * query_arg0, void * state_record, void * segment_offsets, void * contact_record)",
        ("Wave446", "0x005d95d8", "Geometry__IntersectSegmentTriangleAndStoreHit"),
        ("0x005d95d8", "<no_function>", "DATA"),
        ("CMeshCollisionVolume__SetPartBounds", "Geometry__IntersectSegmentTriangleAndStoreHit", "return 0"),
    ),
    "0x005019c0": (
        "VFuncSlot_09_005019c0",
        "int __cdecl VFuncSlot_09_005019c0(void)",
        ("Wave1121 current-risk comment refresh", "0x00501a10", "CVertexShader__VFunc_02_00501a10", "default/false"),
        ("0x005dfbc8", "<no_function>", "DATA"),
        ("return 0;",),
    ),
}

DOC_TOKENS = (
    "Wave1121",
    "wave1121-mixed-score24-current-risk-review",
    "122/1179 = 10.35%",
    "4 rows",
    "current focused candidates: 1179",
    "score-24 mixed current-risk head",
    "comment-only",
    "0 / 0 / 0",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime damage behavior proven",
    "runtime mesh collision behavior proven",
    "runtime shader behavior proven",
    "runtime frontend behavior proven",
    "source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
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


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def import_probe(path: Path):
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_probe_addresses(module) -> set[str]:
    addresses: set[str] = set()
    for attr in ("TOP15", "REMAINDER", "TARGETS"):
        if not hasattr(module, attr):
            continue
        value = getattr(module, attr)
        if isinstance(value, dict):
            addresses.update(normalize_address(address) for address in value)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                if isinstance(item, str):
                    addresses.add(normalize_address(item))
                elif isinstance(item, (list, tuple)) and item and isinstance(item[0], str):
                    addresses.add(normalize_address(item[0]))
    if hasattr(module, "ADDRESS"):
        addresses.add(normalize_address(getattr(module, "ADDRESS")))
    return addresses


def prior_accounted_addresses() -> set[str]:
    accounted: set[str] = set()
    for name in PRIOR_PROBES:
        accounted.update(extract_probe_addresses(import_probe(TOOLS / name)))
    return accounted


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def check_wave1108_head(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    rows = read_tsv(FOCUSED_TSV)
    accounted = prior_accounted_addresses()
    remaining = [row for row in rows if normalize_address(row.get("address", "")) not in accounted]
    require(len(rows) == 1179, "Wave1108 focused row count mismatch", failures)
    require(len(accounted) == 118, f"prior accounted count mismatch: {len(accounted)}", failures)
    require(len(remaining) == 1061, f"remaining focused count mismatch: {len(remaining)}", failures)
    require([normalize_address(row.get("address", "")) for row in remaining[:4]] == list(TARGETS), "Wave1121 targets are not the next four unaccounted Wave1108 focused rows", failures)
    for row in remaining[:4]:
        require(row.get("score") == "24", f"Wave1108 score mismatch: {row.get('address')}", failures)


def check_exports_and_logs(failures: list[str]) -> None:
    counts = {
        "pre-metadata.tsv": 4,
        "pre-tags.tsv": 4,
        "pre-xrefs.tsv": 42,
        "pre-instructions.tsv": 1207,
        "pre-decompile/index.tsv": 4,
        "post-metadata.tsv": 4,
        "post-tags.tsv": 4,
        "post-xrefs.tsv": 42,
        "post-instructions.tsv": 1207,
        "post-decompile/index.tsv": 4,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    log_tokens = {
        "pre-metadata.log": "targets=4 found=4 missing=0",
        "pre-tags.log": "rows=4 missing=0",
        "pre-xrefs.log": "Wrote 42 rows",
        "pre-instructions.log": "targets=4 missing=0",
        "pre-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
        "apply-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=3 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=3 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=4 found=4 missing=0",
        "post-tags.log": "rows=4 missing=0",
        "post-xrefs.log": "Wrote 42 rows",
        "post-instructions.log": "targets=4 missing=0",
        "post-decompile.log": "targets=4 dumped=4 missing=0 failed=0",
    }
    for relative, token in log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "missing=1", "failed=1", "bad=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply log missing save report", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = row_map(BASE / "post-metadata.tsv")
    tags = row_map(BASE / "post-tags.tsv")
    decompile = row_map(BASE / "post-decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    queue = row_map(QUEUE_TSV)

    pre_metadata = row_map(BASE / "pre-metadata.tsv")
    require(STALE_SLOT2_PHRASE in pre_metadata["0x005019c0"].get("comment", ""), "pre metadata lacks stale slot-2 phrase", failures)

    for address, expected in TARGETS.items():
        name, signature, comment_tokens, xref, decompile_tokens = expected
        for label, rows in (("post metadata", metadata), ("current queue", queue)):
            row = rows.get(address)
            require(row is not None, f"{label} missing: {address}", failures)
            if row is not None:
                comment = unescape_tsv(row.get("comment", ""))
                require(row.get("name") == name, f"{label} name mismatch at {address}", failures)
                require(row.get("signature") == signature, f"{label} signature mismatch at {address}", failures)
                require(row.get("status") == "OK", f"{label} status mismatch at {address}", failures)
                for token in comment_tokens:
                    require(token in comment, f"{label} missing comment token at {address}: {token}", failures)
                if address == "0x005019c0":
                    require(STALE_SLOT2_PHRASE not in comment, f"{label} still has stale slot-2 phrase", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("name") == name, f"tag name mismatch at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            if address == "0x005019c0":
                for token in ("wave1121-mixed-score24-current-risk-review", "wave1121-readback-verified", "comment-refresh"):
                    require(token in tag_row.get("tags", ""), f"missing Wave1121 tag at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            dec_text = read_text(BASE / "post-decompile" / f"{address[2:]}_{name}.c")
            for token in decompile_tokens:
                require(token in dec_text, f"missing decompile token at {address}: {token}", failures)

        xref_from, xref_function, xref_type = xref
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == normalize_address(xref_from)
                and row.get("from_function") == xref_function
                and row.get("ref_type") == xref_type
                for row in xrefs
            ),
            f"missing expected xref for {address}",
            failures,
        )


def check_backup(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175541127, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    address_tokens = tuple(f"{address} {target[0]}" for address, target in TARGETS.items())
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS + address_tokens:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        if path != NOTE:
            require(STALE_SLOT2_PHRASE not in text, f"stale slot-2 phrase remains in {path.relative_to(ROOT)}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad.lower() not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        UNIT_DOC: ("Wave1121", "0x004037a0 SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0", BACKUP),
        UNIT_DOC_MIRROR: ("Wave1121", "0x004037a0 SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0", BACKUP),
        MESH_COLLISION_DOC: ("Wave1121", "0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0", "0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830", BACKUP),
        MESH_COLLISION_DOC_MIRROR: ("Wave1121", "0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0", "0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830", BACKUP),
        VERTEX_SHADER_DOC: ("Wave1121", "0x005019c0 VFuncSlot_09_005019c0", "0x00501a10 CVertexShader__VFunc_02_00501a10", BACKUP),
        VERTEX_SHADER_DOC_MIRROR: ("Wave1121", "0x005019c0 VFuncSlot_09_005019c0", "0x00501a10 CVertexShader__VFunc_02_00501a10", BACKUP),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        require(STALE_SLOT2_PHRASE not in text, f"stale slot-2 phrase remains in {path.relative_to(ROOT)}", failures)

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    commit_pattern = re.compile(r"^(pending Wave1121 artifact commit|[0-9a-f]{40})$")
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1121 mixed score-24 current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1121-mixed-score24-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(bool(commit_pattern.match(data["latestWave"].get("artifactCommit", ""))), f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 122, f"{label} focused reviewed mismatch", failures)
        require(current["focusedReviewedPercent"] == "10.35%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1121-mixed-score24-current-risk-review", f"{label} review tag mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1121_mixed_score24_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1121-mixed-score24-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_head(failures)
    check_exports_and_logs(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1121 mixed score-24 current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1121 mixed score-24 current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
