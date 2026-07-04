#!/usr/bin/env python3
"""Validate Wave1114 mixed score-27 current-risk head supersession evidence."""

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
WAVE1108_DIR = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank"
FOCUSED_TSV = WAVE1108_DIR / "wave1108-current-focused-candidates.tsv"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BASE = ROOT / "subagents" / "ghidra-static-reaudit"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1114-mixed-score27-current-risk-head-supersession.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1114-mixed-score27-current-risk-head-supersession.md"
READINESS = ROOT / "release" / "readiness" / "wave1114_mixed_score27_current_risk_head_supersession_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

LATEST_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified"

PRIOR_PROBES = (
    "wave1109_cfastvb_current_risk_head_supersession.py",
    "wave1110_cfastvb_wave1053_remainder_supersession.py",
    "wave1111_cnamedmesh_current_risk_supersession.py",
    "wave1112_animal_wave1016_current_risk_supersession.py",
    "wave1113_battleengine_wave936_wave1010_current_risk_supersession.py",
)

TARGETS = {
    "0x00425a10": {
        "name": "CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags",
        "signature": "bool __thiscall CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags(void * this, void * candidateRound)",
        "score": "27",
        "source": "Wave1059",
        "tag": "collision-seeking-round-tail-review-wave1059",
        "base": "wave1059-collision-seeking-round-tail-review",
        "backup": r"[maintainer-local-ghidra-backup-root]\BEA_20260601-195206_post_wave1059_collision_seeking_round_tail_review_verified",
        "backup_bytes": 174689159,
        "files": ("post-context-metadata.tsv", "post-context-tags.tsv", "post-context-xrefs.tsv", "post-context-instructions.tsv", "post-context-decompile/index.tsv"),
        "counts": (6, 6, 18, 257, 6),
        "decompile_file": "post-context-decompile/00425a10_CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags.c",
        "comment_tokens": ("infantry-bloke collision-seeking filter", "CBattleEngine__IsWeaponModeCompatibleWithMountState", "CCollisionSeekingRound__CheckCollisionFlags"),
        "xref": ("0x005dbf68", "<no_function>", "DATA"),
        "decompile_tokens": ("CUnit__IsCandidateSideCompatibleForTargeting", "CCollisionSeekingRound__CheckCollisionFlags", "candidateRound"),
    },
    "0x0042c420": {
        "name": "CConsoleMenu__ctor_like_0042c420",
        "signature": "void * __fastcall CConsoleMenu__ctor_like_0042c420(void * this)",
        "score": "27",
        "source": "Wave972",
        "tag": "console-wave326",
        "base": "wave972-console-menu-constructor-review",
        "backup": r"[maintainer-local-ghidra-backup-root]\BEA_20260528-185042_post_wave972_console_menu_boundary_recovery_verified",
        "backup_bytes": 173771655,
        "files": ("metadata.tsv", "tags.tsv", "xrefs.tsv", "instructions.tsv", "decompile/index.tsv"),
        "counts": (5, 5, 15, 112, 5),
        "decompile_file": "decompile/0042c420_CConsoleMenu__ctor_like_0042c420.c",
        "comment_tokens": ("Console menu node vtable", "first-child", "child-count"),
        "xref": ("0x004e01b1", "CSoundManager__Init", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("CConsoleMenu__ctor_like_0042c420", "PTR_CRT__Purecall", "return this"),
    },
    "0x00437490": {
        "name": "CPhysicsScriptStatements__CreateStatementType5",
        "signature": "void * __cdecl CPhysicsScriptStatements__CreateStatementType5(int valueType)",
        "score": "27",
        "source": "Wave991",
        "tag": "round-sound-value-tranche",
        "base": "wave991-round-config-bridge-review",
        "backup": r"[maintainer-local-ghidra-backup-root]\BEA_20260531-045300_post_wave991_round_config_bridge_review_verified",
        "backup_bytes": 173837191,
        "files": ("post-metadata.tsv", "post-tags.tsv", "post-xrefs.tsv", "post-instructions.tsv", "post-decompile/index.tsv"),
        "counts": (8, 8, 12, 1430, 8),
        "decompile_file": "post-decompile/00437490_CPhysicsScriptStatements__CreateStatementType5.c",
        "comment_tokens": ("type-5/round value factory", "0x1 through 0x26", "round value"),
        "xref": ("0x00430286", "CRoundStatement__LoadFromMemBuffer", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("CPhysicsScriptStatements__CreateStatementType5", "CPhysicsRoundValueLeaf", "valueType"),
    },
    "0x00479020": {
        "name": "CMeshCollisionVolume__IsDirectionInsideTrianglePrism",
        "signature": "int __cdecl CMeshCollisionVolume__IsDirectionInsideTrianglePrism(void * vertex0, void * vertex1, void * vertex2, void * vertex3, void * direction)",
        "score": "27",
        "source": "Wave1098",
        "tag": "primitive-collision-bridge-review-wave1098",
        "base": "wave1098-primitive-collision-bridge-review",
        "backup": r"[maintainer-local-ghidra-backup-root]\BEA_20260604-190557_post_wave1098_primitive_collision_bridge_review_verified",
        "backup_bytes": 175541127,
        "files": ("post-metadata.tsv", "post-tags.tsv", "post-xrefs.tsv", "post-instructions.tsv", "post-decompile/index.tsv"),
        "counts": (21, 21, 79, 3707, 21),
        "decompile_file": "post-decompile/00479020_CMeshCollisionVolume__IsDirectionInsideTrianglePrism.c",
        "comment_tokens": ("signed edge/plane dot tests", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore", "runtime collision behavior"),
        "xref": ("0x004788e2", "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("CMeshCollisionVolume__IsDirectionInsideTrianglePrism", "vertex0", "direction"),
    },
    "0x004799c0": {
        "name": "CGillM__VFunc09_InitGroundedSpawnState",
        "signature": "void __thiscall CGillM__VFunc09_InitGroundedSpawnState(void * this, void * spawn_state)",
        "score": "27",
        "source": "Wave1000",
        "tag": "gillm-family-wave389",
        "base": "wave1000-gillm-grounded-movement-review",
        "backup": r"[maintainer-local-ghidra-backup-root]\BEA_20260531-101059_post_wave1000_gillm_grounded_movement_review_verified",
        "backup_bytes": 173869959,
        "files": ("pre-metadata.tsv", "pre-tags.tsv", "pre-xrefs.tsv", "pre-instructions.tsv", "pre-decompile/index.tsv"),
        "counts": (10, 10, 10, 526, 10),
        "decompile_file": "pre-decompile/004799c0_CGillM__VFunc09_InitGroundedSpawnState.c",
        "comment_tokens": ("CGillM RTTI vtable 0x005e0b30 slot 9", "+0x26c", "static-shadow ground height"),
        "xref": ("0x005e0b54", "<no_function>", "DATA"),
        "decompile_tokens": ("SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820", "CStaticShadows__SampleShadowHeightBilinear", "spawn_state"),
    },
    "0x0047ea20": {
        "name": "CHeightField__GetHeightSamplePacked16",
        "signature": "uint __fastcall CHeightField__GetHeightSamplePacked16(void * this, uint x_packed, uint z_packed)",
        "score": "27",
        "source": "Wave935",
        "tag": "map-resource-wave426",
        "base": "wave935-world-footprint-heightfield-review",
        "backup": r"[maintainer-local-ghidra-backup-root]\BEA_20260528-011246_post_wave935_world_footprint_heightfield_review_verified",
        "backup_bytes": 173247367,
        "files": ("metadata.tsv", "tags.tsv", "xrefs.tsv", "instructions.tsv", "decompile/index.tsv"),
        "counts": (2, 2, 12, 422, 2),
        "decompile_file": "decompile/0047ea20_CHeightField__GetHeightSamplePacked16.c",
        "comment_tokens": ("packed 16-bit height data", "+0x1028", "0xa1ffe"),
        "xref": ("0x00490e79", "CHeightField__BuildCellMinMaxHeightTable", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("x_packed", "z_packed", "0xa1ffe"),
    },
    "0x00487d10": {
        "name": "CHud__RenderBattleline",
        "signature": "void __thiscall CHud__RenderBattleline(void * this, void * viewport)",
        "score": "27",
        "source": "Wave1004",
        "tag": "hud-battleline-tail-wave412",
        "base": "wave1004-hud-render-body-review",
        "backup": r"[maintainer-local-ghidra-backup-root]\BEA_20260531-124610_post_wave1004_hud_render_body_review_verified",
        "backup_bytes": 173869959,
        "files": ("pre-metadata.tsv", "pre-tags.tsv", "pre-xrefs.tsv", "pre-instructions.tsv", "pre-decompile/index.tsv"),
        "counts": (15, 15, 30, 6350, 15),
        "decompile_file": "pre-decompile/00487d10_CHud__RenderBattleline.c",
        "comment_tokens": ("CHud::RenderBattleline", "HUD singleton 0x8aa4e8", "influence-overlay"),
        "xref": ("0x0053ed79", "CDXEngine__PostRender", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("HudRenderState__ApplyOverlaySpriteState", "CDXBattleLine", "viewport"),
    },
    "0x004aa6b0": {
        "name": "CMesh__GetNameOrUnknown",
        "signature": "void * __thiscall CMesh__GetNameOrUnknown(void * this)",
        "score": "27",
        "source": "Wave814",
        "tag": "mesh-segment-tail-wave814",
        "base": "wave814-mesh-segment-tail",
        "backup": r"[maintainer-local-ghidra-backup-root]\BEA_20260524-141602_post_wave814_mesh_segment_tail_verified",
        "backup_bytes": 171346823,
        "files": ("post-metadata.tsv", "post-tags.tsv", "post-xrefs.tsv", "post-instructions.tsv", "post-decompile/index.tsv"),
        "counts": (4, 4, 24, 884, 4),
        "decompile_file": "post-decompile/004aa6b0_CMesh__GetNameOrUnknown.c",
        "comment_tokens": ("DAT_00704ad8", "unknown mesh name", "signature was stale"),
        "xref": ("0x004ae34c", "CMeshPart__CreatePolyBucket", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("DAT_00704ad8", "s_unknown_mesh_name_0062f8d4", "+0x158"),
    },
    "0x004bff30": {
        "name": "CComplexThing__dtor_base_Thunk_004bff30",
        "signature": "void __fastcall CComplexThing__dtor_base_Thunk_004bff30(void * this)",
        "score": "27",
        "source": "Wave1022",
        "tag": "object-cleanup-wave460",
        "base": "wave1022-object-lifecycle-dtor-review",
        "backup": r"[maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified",
        "backup_bytes": 173968263,
        "files": ("post-primary-metadata.tsv", "post-primary-tags.tsv", "post-primary-xrefs.tsv", "post-primary-instructions.tsv", "post-primary-decompile/index.tsv"),
        "counts": (7, 7, 11, 152, 7),
        "decompile_file": "post-primary-decompile/004bff30_CComplexThing__dtor_base_Thunk_004bff30.c",
        "comment_tokens": ("jump thunk", "0x004f3f00", "no standalone cleanup body"),
        "xref": ("0x004e5e53", "SharedComplexThing__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("CComplexThing__dtor_base", "return", "Thunk"),
    },
    "0x004fd3d0": {
        "name": "CUnit__IsCandidateSideCompatibleForTargeting",
        "signature": "bool __thiscall CUnit__IsCandidateSideCompatibleForTargeting(void * this, int candidate_side)",
        "score": "27",
        "source": "Wave927",
        "tag": "unit-support-tail-wave540",
        "base": "wave927-cunit-active-reader-targeting-review",
        "backup": r"[maintainer-local-ghidra-backup-root]\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified",
        "backup_bytes": 173247367,
        "files": ("metadata.tsv", "tags.tsv", "xrefs.tsv", "instructions.tsv", "decompile/index.tsv"),
        "counts": (5, 5, 23, 464, 5),
        "decompile_file": "decompile/004fd3d0_CUnit__IsCandidateSideCompatibleForTargeting.c",
        "comment_tokens": ("RET 0x4", "candidate_side", "this+0x164->0x128"),
        "xref": ("0x00406ddc", "CBattleEngine__SelectNearestForwardTargetFromGlobalSet", "UNCONDITIONAL_CALL"),
        "decompile_tokens": ("candidate_side", "0x164", "0x128"),
    },
}

DOC_TOKENS = (
    "Wave1114",
    "wave1114-mixed-score27-current-risk-head-supersession",
    "43/1179 = 3.65%",
    "10 rows",
    "current focused candidates: 1179",
    "mixed score-27 current-risk head",
    "0x00425a10 CCollisionSeekingInfantryBloke__CheckMountStateOrCollisionFlags",
    "0x0042c420 CConsoleMenu__ctor_like_0042c420",
    "0x00437490 CPhysicsScriptStatements__CreateStatementType5",
    "0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism",
    "0x004799c0 CGillM__VFunc09_InitGroundedSpawnState",
    "0x0047ea20 CHeightField__GetHeightSamplePacked16",
    "0x00487d10 CHud__RenderBattleline",
    "0x004aa6b0 CMesh__GetNameOrUnknown",
    "0x004bff30 CComplexThing__dtor_base_Thunk_004bff30",
    "0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting",
    "Wave1059",
    "Wave972",
    "Wave991",
    "Wave1098",
    "Wave1000",
    "Wave935",
    "Wave1004",
    "Wave814",
    "Wave1022",
    "Wave927",
    LATEST_BACKUP,
    "no new Ghidra export",
    "no mutation",
)

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime targeting behavior proven",
    "runtime hud behavior proven",
    "runtime collision behavior proven",
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
    if value in {"", "<none>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def contains_token(text: str, token: str) -> bool:
    normalized = text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    return token in text or token.replace("\\", "\\\\") in text or token in normalized


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def row_map(path: Path, key: str = "address") -> dict[str, dict[str, str]]:
    return {normalize_address(row.get(key, "")): row for row in read_tsv(path)}


def import_probe(path: Path):
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prior_accounted_addresses() -> set[str]:
    accounted: set[str] = set()
    for name in PRIOR_PROBES:
        module = import_probe(TOOLS / name)
        for attr in ("TOP15", "REMAINDER", "TARGETS"):
            if hasattr(module, attr):
                value = getattr(module, attr)
                if isinstance(value, dict):
                    accounted.update(normalize_address(address) for address in value)
                elif isinstance(value, (list, tuple, set)):
                    for item in value:
                        if isinstance(item, str):
                            accounted.add(normalize_address(item))
                        elif isinstance(item, (list, tuple)) and item and isinstance(item[0], str):
                            accounted.add(normalize_address(item[0]))
        if hasattr(module, "ADDRESS"):
            accounted.add(normalize_address(getattr(module, "ADDRESS")))
    return accounted


def check_wave1108_head(failures: list[str]) -> None:
    wave1108_current_risk_rank.generate()
    focused_rows = read_tsv(FOCUSED_TSV)
    require(len(focused_rows) == 1179, "Wave1108 focused row count mismatch", failures)
    focused = {normalize_address(row.get("address", "")): row for row in focused_rows}
    accounted = prior_accounted_addresses()
    require(len(accounted) == 33, f"prior accounted count mismatch: {len(accounted)}", failures)
    remaining = [row for row in focused_rows if normalize_address(row.get("address", "")) not in accounted]
    require(len(remaining) == 1146, f"remaining focused count mismatch: {len(remaining)}", failures)
    require(
        [normalize_address(row.get("address", "")) for row in remaining[:10]] == list(TARGETS),
        "Wave1114 targets are not the next ten unaccounted Wave1108 focused rows",
        failures,
    )

    for address, expected in TARGETS.items():
        row = focused.get(address)
        require(row is not None, f"Wave1108 focused row missing: {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"Wave1108 name mismatch: {address}", failures)
        require(row.get("score") == expected["score"], f"Wave1108 score mismatch: {address}", failures)
        for signal in ("stale_or_corrected", "runtime_or_rebuild_deferred"):
            require(signal in row.get("signals", ""), f"Wave1108 missing signal {address}: {signal}", failures)


def check_current_queue(failures: list[str]) -> None:
    queue = row_map(QUEUE_TSV)
    for address, expected in TARGETS.items():
        row = queue.get(address)
        require(row is not None, f"current queue row missing: {address}", failures)
        if row is None:
            continue
        require(row.get("name") == expected["name"], f"current queue name mismatch: {address}", failures)
        require(row.get("signature") == expected["signature"], f"current queue signature mismatch: {address}", failures)
        require(row.get("status") == "OK", f"current queue status mismatch: {address}", failures)
        for token in expected["comment_tokens"]:
            require(token in row.get("comment", ""), f"current queue missing comment token {address}: {token}", failures)


def check_artifacts(failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        base = BASE / expected["base"]
        files = [base / relative for relative in expected["files"]]
        for path, expected_count in zip(files, expected["counts"]):
            require(path.is_file(), f"missing artifact file {path.relative_to(ROOT)}", failures)
            if path.is_file():
                actual = len(read_tsv(path))
                require(actual == expected_count, f"{path.relative_to(ROOT)} row count {actual} != {expected_count}", failures)

        metadata = row_map(files[0])
        tags = row_map(files[1])
        xrefs = read_tsv(files[2])
        instructions = read_tsv(files[3])
        decompile = row_map(files[4])

        row = metadata.get(address)
        require(row is not None, f"{expected['source']} metadata missing: {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"{expected['source']} metadata name mismatch: {address}", failures)
            require(row.get("signature") == expected["signature"], f"{expected['source']} metadata signature mismatch: {address}", failures)
            require(row.get("status") == "OK", f"{expected['source']} metadata status mismatch: {address}", failures)
            for token in expected["comment_tokens"]:
                require(token in row.get("comment", ""), f"{expected['source']} metadata missing token {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"{expected['source']} tags missing: {address}", failures)
        if tag_row is not None:
            require(expected["tag"] in tag_row.get("tags", ""), f"{expected['source']} missing tag {address}: {expected['tag']}", failures)
            require(tag_row.get("status") == "OK", f"{expected['source']} tag status mismatch: {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"{expected['source']} decompile index missing: {address}", failures)
        if dec is not None:
            require(dec.get("name") == expected["name"], f"{expected['source']} decompile name mismatch: {address}", failures)
            require(dec.get("signature") == expected["signature"], f"{expected['source']} decompile signature mismatch: {address}", failures)
            require(dec.get("status") == "OK", f"{expected['source']} decompile status mismatch: {address}", failures)

        from_addr, from_function, ref_type = expected["xref"]
        require(
            any(
                normalize_address(row.get("target_addr", "")) == address
                and normalize_address(row.get("from_addr", "")) == normalize_address(from_addr)
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
                for row in xrefs
            ),
            f"{expected['source']} missing xref {from_addr} -> {address}",
            failures,
        )
        require(
            any(row.get("function_name") == expected["name"] or normalize_address(row.get("function_addr", "")) == address for row in instructions),
            f"{expected['source']} missing instruction rows for {address}",
            failures,
        )
        decompile_text = read_text(base / expected["decompile_file"])
        for token in expected["decompile_tokens"]:
            require(token in decompile_text, f"{expected['source']} decompile missing token {address}: {token}", failures)


def check_backups(failures: list[str]) -> None:
    for expected in TARGETS.values():
        backup = read_json(BASE / expected["base"] / "backup-summary.json")
        require(backup.get("backupPath") == expected["backup"], f"{expected['source']} backup path mismatch", failures)
        require(backup.get("fileCount") == 19, f"{expected['source']} backup file count mismatch", failures)
        require(int(backup.get("totalBytes", -1)) == expected["backup_bytes"], f"{expected['source']} backup byte count mismatch", failures)
        require(backup.get("diffCount") == 0, f"{expected['source']} backup diff mismatch", failures)
        if "hashDiffCount" in backup:
            require(backup.get("hashDiffCount") == 0, f"{expected['source']} backup hash diff mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = {
        "wave1114 note": read_text(NOTE),
        "wave1114 readiness": read_text(READINESS),
        "mapped systems": read_text(MAPPED_SYSTEMS),
        "campaign": read_text(CAMPAIGN),
        "binary index": read_text(BINARY_INDEX),
        "RE index": read_text(RE_INDEX),
        "progress": read_text(PROGRESS),
        "developer state": read_text(DEVELOPER_STATE),
        "documentation state": read_text(DOCUMENTATION_STATE),
        "re state": read_text(RE_STATE),
    }
    for name, text in docs.items():
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {name}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lowered, f"overclaim token in {name}: {bad}", failures)
    for expected in TARGETS.values():
        for name, text in docs.items():
            require(contains_token(text, expected["backup"]), f"missing backup in {name}: {expected['backup']}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave1114 note mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "static progress mirror mismatch", failures)
    current = read_json(PROGRESS).get("post100Reaudit", {}).get("currentRiskRank", {})
    require(current.get("focusedReviewed") == 43, "progress focusedReviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "3.65%", "progress focusedReviewedPercent mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1114-mixed-score27-current-risk-head-supersession")
        == r"py -3 tools\wave1114_mixed_score27_current_risk_head_supersession.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_wave1108_head(failures)
    check_current_queue(failures)
    check_artifacts(failures)
    check_backups(failures)
    check_docs(failures)

    if failures:
        print("Wave1114 mixed score-27 current-risk head supersession probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1114 mixed score-27 current-risk head supersession probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
