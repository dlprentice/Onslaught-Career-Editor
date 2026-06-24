#!/usr/bin/env python3
"""Validate Wave1149 particle/effects current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1149-particle-effects-score20-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1149-particle-effects-score20-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1149-particle-effects-score20-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1149_particle_effects_score20_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
WAVE1108_NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
WAVE1108_READINESS = ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
PARTICLE_DESCRIPTOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md"
PARTICLE_MANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
PARTICLE_SET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleSet.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified"

TARGETS = {
    "0x004c35d0": ("CEngine__ConfigureParticleBurstForDistance", "void __thiscall CEngine__ConfigureParticleBurstForDistance(void * this, void * particle, int unused_context)", ("CParticleManager__SetParticleResource", "+0x80", "+0x88")),
    "0x004c5410": ("CParticleDescriptor__Update", "int __thiscall CParticleDescriptor__Update(void * this, void * particle)", ("CParticleManager__CreateEffect", "fallback particle")),
    "0x004c5730": ("CParticleDescriptor__Load", "int __thiscall CParticleDescriptor__Load(void * this, void * token_archive)", ("CTokenArchive__ReadNextToken", "terminator token 5")),
    "0x004c8060": ("CEngine__ComputeSpriteTintByDistance", "int __thiscall CEngine__ComputeSpriteTintByDistance(void * this, int particle_index, int alpha_scale, float descriptor_context, float distance_context)", ("sprite tint", "distance")),
    "0x004caed0": ("CParticleManager__SetParticleResource", "bool __thiscall CParticleManager__SetParticleResource(void * this, int resource_size)", ("+0x88", "OID__AllocObject")),
    "0x004caf60": ("CParticleManager__CleanupHandles", "void __cdecl CParticleManager__CleanupHandles(void)", ("DAT_0082b3e4", "+0xb4")),
    "0x004cb0b0": ("ParticleEffectLink__SetHandleStateAndClear", "void __thiscall ParticleEffectLink__SetHandleStateAndClear(void * this, int set_state_one)", ("owner-link", "+0xb4")),
    "0x004cb300": ("CParticleManager__InterpolatePositions", "void __cdecl CParticleManager__InterpolatePositions(void)", ("DAT_0082b3e8", "10000.0")),
    "0x004cb3d0": ("CParticleManager__CreateEffect", "void __stdcall CParticleManager__CreateEffect(void * manager, void * out_handle_slot, float spawn_x, float spawn_y, float spawn_z, float spawn_w, int looping_flag, int force_allocate)", ("DAT_0082b3e4", "0xb8")),
    "0x004cb920": ("CParticleManager__UpdateParticleAndRecycleIfDead", "void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * particle)", ("UpdateParticleAndRecycleIfDead", "Wave994")),
    "0x004cba30": ("CParticleManager__ProjectPointToTerrainWithRadiusClamp", "int __stdcall CParticleManager__ProjectPointToTerrainWithRadiusClamp(void * world_pos, float radius, void * out_pos)", ("terrain height", "radius")),
    "0x004cba90": ("CParticleManager__ComputeMinCameraDistanceSqForParticle", "double __stdcall CParticleManager__ComputeMinCameraDistanceSqForParticle(void * particle)", ("camera-distance", "+0x58")),
    "0x004cbff0": ("CParticleManager__DestroyParticleList", "void __fastcall CParticleManager__DestroyParticleList(void * list_head_ptr)", ("vfunc slot 0", "delete flag")),
    "0x004cc020": ("CParticleSet__CreateByType", "void * __thiscall CParticleSet__CreateByType(void * this, char * set_name, int type_id, void * context)", ("DAT_0082b450", "type id")),
    "0x004cc850": ("CParticleSet__Init", "void __fastcall CParticleSet__Init(void * particle_set)", ("base particle-set", "vtable")),
}

DOC_TOKENS = (
    "Wave1149",
    "wave1149-particle-effects-score20-current-risk-review",
    "344/1179 = 29.18%",
    "15 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 835",
    "current risk candidates: 6166",
    "particle/effects score20 current-risk review",
    "fresh Ghidra export",
    "particle descriptor update/load, engine burst/tint, particle manager handles/effects/update/distance/list, and ParticleSet factory/init helpers",
    "read-only review",
    "no mutation",
    "no Codex subagent",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CEngine__ConfigureParticleBurstForDistance",
    "CParticleDescriptor__Update",
    "CParticleDescriptor__Load",
    "CEngine__ComputeSpriteTintByDistance",
    "CParticleManager__SetParticleResource",
    "CParticleManager__CleanupHandles",
    "ParticleEffectLink__SetHandleStateAndClear",
    "CParticleManager__InterpolatePositions",
    "CParticleManager__CreateEffect",
    "CParticleManager__UpdateParticleAndRecycleIfDead",
    "CParticleManager__ProjectPointToTerrainWithRadiusClamp",
    "CParticleManager__ComputeMinCameraDistanceSqForParticle",
    "CParticleManager__DestroyParticleList",
    "CParticleSet__CreateByType",
    "CParticleSet__Init",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIM_TOKENS = (
    "runtime particle behavior proven",
    "runtime effect behavior proven",
    "runtime render behavior proven",
    "runtime particleset loading proven",
    "runtime particle descriptor loading proven",
    "exact particle layout proven",
    "exact descriptor layout proven",
    "exact manager layout proven",
    "exact handle layout proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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
        "pre-metadata.tsv": 15,
        "pre-tags.tsv": 15,
        "pre-xrefs.tsv": 118,
        "pre-instructions.tsv": 1891,
        "pre-decompile/index.tsv": 15,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xref_targets = {normalize_address(row["target_addr"]) for row in read_tsv(BASE / "pre-xrefs.tsv")}
    evidence = "\n".join(row.get("comment", "") for row in metadata.values())
    evidence += "\n" + "\n".join(read_text(path) for path in (BASE / "pre-decompile").glob("*.c"))
    evidence += "\n" + "\n".join(
        f"{row.get('mnemonic','')} {row.get('operands','')}" for row in read_tsv(BASE / "pre-instructions.tsv")
    )
    compact = evidence.lower().replace(" ", "")

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in tokens:
                token_ok = token.lower().replace(" ", "") in compact or token in evidence
                require(token_ok, f"missing evidence token at {address}: {token}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require(address in xref_targets, f"missing xrefs for {address}", failures)

    for token in ("CTokenArchive__ReadNextToken", "DAT_0082b3e4", "DAT_0082b450", "CParticleManager__CreateEffect"):
        require(token in evidence, f"missing global instruction/decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=15 found=15 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "pre-xrefs.log": "Wrote 118 rows",
        "pre-instructions.log": "Wrote 1891 function-body instruction rows",
        "pre-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue_progress(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)
    focused_addresses = {normalize_address(row["address"]) for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused_addresses, f"target absent from focused list: {address}", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    latest = progress["latestWave"]
    require(latest["wave"] == "Wave1149 particle/effects score20 current-risk review", "progress latest wave mismatch", failures)
    require(latest["tag"] == "wave1149-particle-effects-score20-current-risk-review", "progress latest tag mismatch", failures)
    require(latest["backup"] == BACKUP, "progress backup mismatch", failures)
    require(current["focusedReviewed"] == 344, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "29.18%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 835, "progress remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1178, "progress live focused mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        WAVE1108_NOTE,
        WAVE1108_READINESS,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        ENGINE_DOC,
        PARTICLE_DESCRIPTOR_DOC,
        PARTICLE_MANAGER_DOC,
        PARTICLE_SET_DOC,
        PROGRESS,
        PROGRESS_MIRROR,
        README,
        AGENTS,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1149 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1149-particle-effects-score20-current-risk-review")
        == r"py -3 tools\wave1149_particle_effects_score20_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue_progress(failures)
    check_docs(failures)
    if failures:
        print("Wave1149 particle/effects score20 current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1149 particle/effects score20 current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
