#!/usr/bin/env python3
"""Validate Wave1118 particle/message current-risk review."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import wave1108_current_risk_rank


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1118-particle-message-current-risk-review"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1118-particle-message-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1118-particle-message-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1118_particle_message_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

FRONTEND_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
FRONTEND_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "FrontEnd.cpp" / "_index.md"
GILLMHEAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "GillMHead.cpp" / "_index.md"
GILLMHEAD_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "GillMHead.cpp" / "_index.md"
MESSAGE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MessageBox.cpp" / "_index.md"
MESSAGE_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "MessageBox.cpp" / "_index.md"
PARTICLE_MANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
PARTICLE_MANAGER_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
PARTICLE_SET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleSet.cpp" / "_index.md"
PARTICLE_SET_DOC_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleSet.cpp" / "_index.md"

BACKUP = r"G:\GhidraBackups\BEA_20260605-021103_post_wave1118_particle_message_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-014214_post_wave1117_cengine_current_risk_review_verified"
ARTIFACT_COMMIT = "b0e5dc3108ed5a2fe5908aac0411055879242765"

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
)

TARGETS = {
    "0x004729d0": (
        "CGameInterface__ctor_base",
        "void __fastcall CGameInterface__ctor_base(void * this)",
        ("constructor-style base body", "global GameInterface object", "this+0x04", "0x005dbc2c vtable"),
        ("0x004729a5", "<no_function>", "UNCONDITIONAL_CALL"),
        ("PTR_SharedVFunc__NoOpOneArg_004014c0_005dbc2c", "((int)this + 4)", "0x005dbc2c"),
    ),
    "0x0047afc0": (
        "CGillMHeadAI__UpdateAimTransformAndTargetReader",
        "void __fastcall CGillMHeadAI__UpdateAimTransformAndTargetReader(void * this)",
        ("Wave1001 GillMHeadAI review", "0x005dbcec slot 3", "CUnit__ForwardAimTransformAndAttachTargetReader", "stale Wave390 wording"),
        ("0x005dbcf8", "<no_function>", "DATA"),
        ("CUnit__ForwardAimTransformAndAttachTargetReader", "0x005db020", "support/escort"),
    ),
    "0x0047b090": (
        "CGillMHeadAI__UpdateTargetBallisticArcFlags",
        "void __fastcall CGillMHeadAI__UpdateTargetBallisticArcFlags(void * this)",
        ("Wave390 owner/name/signature correction", "0x005dbcec slot 4", "CUnit__CanFireAtTarget_BallisticArcB/A"),
        ("0x005dbcfc", "<no_function>", "DATA"),
        ("CUnit__CanFireAtTarget_BallisticArcB", "CUnit__CanFireAtTarget_BallisticArcA", "0x2c"),
    ),
    "0x004b6e50": (
        "CMessage__ctor_base",
        "void * __thiscall CMessage__ctor_base(void * this, int payload0, short * message_text, int payload2, int payload3, void * active_reader_target, int payload5, int queue_sort_key)",
        ("Wave453", "Ret 0x1c", "message_text", "active_reader_target", "queue_sort_key"),
        ("0x005374c9", "IScript__PlaySound", "UNCONDITIONAL_CALL"),
        ("WcsLen", "0x30", "0x2c"),
    ),
    "0x004cae50": (
        "CParticle__Destroy",
        "void __fastcall CParticle__Destroy(void * particle)",
        ("Wave463", "+0x88", "+0x38", "+0x58"),
        ("0x004cbe95", "CParticleManager__PruneDeadParticles", "UNCONDITIONAL_CALL"),
        ("0x88", "0x38", "0x58"),
    ),
    "0x004cb0e0": (
        "CParticleManager__Init",
        "void * __fastcall CParticleManager__Init(void * manager)",
        ("0x200-entry particle pool", "0xd8-byte particle nodes", "DAT_009c63f4", "DAT_0082b3ec"),
        ("0x004cb644", "CParticleManager__AllocateParticle", "UNCONDITIONAL_CALL"),
        ("0x200", "0xd8", "DAT_009c63f4"),
    ),
    "0x004cb1b0": (
        "CParticleManager__Shutdown",
        "void __fastcall CParticleManager__Shutdown(void * manager)",
        ("0xd8-byte particle array", "backing allocation", "next manager pointer", "DAT_0082b3ec"),
        ("0x0046ccc8", "CGame__ShutdownRestartLoop", "UNCONDITIONAL_CALL"),
        ("0xd8", "DAT_0082b3ec", "CParticleManager__Shutdown"),
    ),
    "0x004cb210": (
        "CParticleManager__Update",
        "int __thiscall CParticleManager__Update(void * this, float delta_time, int update_context)",
        ("delta time", "active particles", "render-node callbacks", "CParticleManager__CleanupHandles"),
        ("0x00466c0f", "CFrontEnd__Process", "UNCONDITIONAL_CALL"),
        ("CParticleManager__UpdateParticles", "CParticleManager__PruneDeadParticles", "CParticleManager__CleanupHandles"),
    ),
    "0x004cb5c0": (
        "CParticleManager__AllocateParticle",
        "void * __thiscall CParticleManager__AllocateParticle(void * this, void * particle_set, int force_allocate)",
        ("free list", "effect-type LOD skip thresholds", "particle-set vfunc +0x24"),
        ("0x004cb402", "CParticleManager__CreateEffect", "UNCONDITIONAL_CALL"),
        ("0x24", "CParticleManager__Init", "CParticle__Destroy"),
    ),
    "0x004cbca0": (
        "CParticleManager__UpdateParticles",
        "void __cdecl CParticleManager__UpdateParticles(void * active_head)",
        ("active particle list", "vfunc +0x54", "DAT_009c63fc"),
        ("0x004cb28a", "CParticleManager__Update", "UNCONDITIONAL_CALL"),
        ("0x54", "DAT_009c63fc", "active_head"),
    ),
    "0x004cbe30": (
        "CParticleManager__PruneDeadParticles",
        "int __fastcall CParticleManager__PruneDeadParticles(void * manager)",
        ("manager active list", "manager +0x1c", "CParticle__Destroy", "manager +0x8"),
        ("0x004cb2c8", "CParticleManager__Update", "UNCONDITIONAL_CALL"),
        ("CParticle__Destroy", "0x1c", "0x8"),
    ),
    "0x004cc870": (
        "CParticleSet__dtor_base",
        "void __fastcall CParticleSet__dtor_base(void * particle_set)",
        ("Wave464", "PTR_LAB_005ddad4"),
        ("0x004ccb43", "CParticleSet__shared_scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
        ("PTR_LAB_005ddad4",),
    ),
    "0x004cd7f0": (
        "CParticleSet__LoadFromArchive",
        "int __thiscall CParticleSet__LoadFromArchive(void * this, void * archive_source)",
        ("0x1388c archive workspace", "token ids 0/1/2/3/4", "vfunc +0x18"),
        ("0x004cdb3d", "CParticleSet__LoadParticleSetFile", "UNCONDITIONAL_CALL"),
        ("0x1388c", "0x18", "CTokenArchive__ResolveReferences"),
    ),
}

DOC_TOKENS = (
    "Wave1118",
    "wave1118-particle-message-current-risk-review",
    "100/1179 = 8.48%",
    "13 rows",
    "current focused candidates: 1179",
    "score-26 particle/message current-risk head",
    "fresh read-only Ghidra export",
    "no mutation",
    BACKUP,
    PRIOR_BACKUP,
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime particle behavior proven",
    "runtime message behavior proven",
    "runtime targeting behavior proven",
    "exact layout proven",
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


def check_wave1108_head(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    rows = read_tsv(FOCUSED_TSV)
    accounted = prior_accounted_addresses()
    remaining = [row for row in rows if normalize_address(row.get("address", "")) not in accounted]
    require(len(rows) == 1179, "Wave1108 focused row count mismatch", failures)
    require(len(accounted) == 87, f"prior accounted count mismatch: {len(accounted)}", failures)
    require(len(remaining) == 1092, f"remaining focused count mismatch: {len(remaining)}", failures)
    require([normalize_address(row.get("address", "")) for row in remaining[:13]] == list(TARGETS), "Wave1118 targets are not the next thirteen unaccounted Wave1108 focused rows", failures)
    for row in remaining[:13]:
        require(row.get("score") == "26", f"Wave1108 score mismatch: {row.get('address')}", failures)


def check_exports(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 13,
        "tags.tsv": 13,
        "xrefs.tsv": 34,
        "instructions.tsv": 1521,
        "decompile/index.tsv": 13,
    }
    for relative, expected in counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)
    log_tokens = {
        "metadata.log": "targets=13 found=13 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=13 missing=0",
        "xrefs.log": "Wrote 34 rows",
        "instructions.log": "targets=13 missing=0",
        "decompile.log": "targets=13 dumped=13 missing=0 failed=0",
    }
    for relative, token in log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING\t", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_target_rows(failures: list[str]) -> None:
    metadata = row_map(BASE / "metadata.tsv")
    tags = row_map(BASE / "tags.tsv")
    decompile = row_map(BASE / "decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "xrefs.tsv")
    queue = row_map(QUEUE_TSV)

    for address, expected in TARGETS.items():
        name, signature, comment_tokens, xref, decompile_tokens = expected
        for label, rows in (("metadata", metadata), ("current queue", queue)):
            row = rows.get(address)
            require(row is not None, f"{label} missing: {address}", failures)
            if row is not None:
                require(row.get("name") == name, f"{label} name mismatch at {address}", failures)
                require(row.get("signature") == signature, f"{label} signature mismatch at {address}", failures)
                require(row.get("status") == "OK", f"{label} status mismatch at {address}", failures)
                for token in comment_tokens:
                    require(token in row.get("comment", ""), f"{label} missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("name") == name, f"tag name mismatch at {address}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
            dec_text = read_text(BASE / "decompile" / f"{address[2:]}_{name}.c")
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
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        FRONTEND_DOC: ("Wave1118", "wave1118-particle-message-current-risk-review", "0x004729d0 CGameInterface__ctor_base", BACKUP),
        FRONTEND_DOC_MIRROR: ("Wave1118", "wave1118-particle-message-current-risk-review", "0x004729d0 CGameInterface__ctor_base", BACKUP),
        GILLMHEAD_DOC: ("Wave1118", "0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader", "0x0047b090 CGillMHeadAI__UpdateTargetBallisticArcFlags", BACKUP),
        GILLMHEAD_DOC_MIRROR: ("Wave1118", "0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader", "0x0047b090 CGillMHeadAI__UpdateTargetBallisticArcFlags", BACKUP),
        MESSAGE_DOC: ("Wave1118", "0x004b6e50 CMessage__ctor_base", "queue_sort_key", BACKUP),
        MESSAGE_DOC_MIRROR: ("Wave1118", "0x004b6e50 CMessage__ctor_base", "queue_sort_key", BACKUP),
        PARTICLE_MANAGER_DOC: ("Wave1118", "0x004cae50 CParticle__Destroy", "0x004cb210 CParticleManager__Update", "0x004cbe30 CParticleManager__PruneDeadParticles", BACKUP),
        PARTICLE_MANAGER_DOC_MIRROR: ("Wave1118", "0x004cae50 CParticle__Destroy", "0x004cb210 CParticleManager__Update", "0x004cbe30 CParticleManager__PruneDeadParticles", BACKUP),
        PARTICLE_SET_DOC: ("Wave1118", "0x004cc870 CParticleSet__dtor_base", "0x004cd7f0 CParticleSet__LoadFromArchive", BACKUP),
        PARTICLE_SET_DOC_MIRROR: ("Wave1118", "0x004cc870 CParticleSet__dtor_base", "0x004cd7f0 CParticleSet__LoadFromArchive", BACKUP),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    progress = read_json(PROGRESS)
    mirror = read_json(PROGRESS_MIRROR)
    for label, data in (("progress", progress), ("progress mirror", mirror)):
        current = data["post100Reaudit"]["currentRiskRank"]
        require(data["latestWave"]["wave"] == "Wave1118 particle/message current-risk review", f"{label} latest wave mismatch", failures)
        require(data["latestWave"]["tag"] == "wave1118-particle-message-current-risk-review", f"{label} latest tag mismatch", failures)
        require(data["latestWave"]["backup"] == BACKUP, f"{label} backup mismatch", failures)
        require(data["latestWave"]["artifactCommit"] == ARTIFACT_COMMIT, f"{label} artifact commit mismatch", failures)
        require(current["focusedReviewed"] == 100, f"{label} focused reviewed mismatch", failures)
        require(current["focusedReviewedPercent"] == "8.48%", f"{label} focused percent mismatch", failures)
        require(current["latestReviewTag"] == "wave1118-particle-message-current-risk-review", f"{label} review tag mismatch", failures)

    package = read_json(PACKAGE_JSON)
    expected_script = r"py -3 tools\wave1118_particle_message_current_risk_review.py --check"
    require(package["scripts"].get("test:wave1118-particle-message-current-risk-review") == expected_script, "missing package script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_head(failures)
    check_exports(failures)
    check_target_rows(failures)
    check_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave1118 particle/message current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1118 particle/message current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
