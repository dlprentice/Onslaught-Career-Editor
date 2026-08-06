#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seed and query a specimen-bound recursive RE campaign from a coverage ledger.

This is the durable join between the executable/function ledger, finite Mission
surface, scenario evidence, and the probe selector. It does not make semantic
claims and never edits Ghidra. `seed` refuses hull-only snapshots and publishes
its READY receipt last; `next` reads only a verified campaign.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import re_coverage_ledger as coverage
import ghidra_project_backup as ghidra_backup

_FROZEN_LOCAL_LAB = Path(__file__).resolve().parent.parent / "local-lab"
if (_FROZEN_LOCAL_LAB / "aya_roundtrip.py").is_file():
    # A frozen reducer must consume its own measured codec/parser bytes even if
    # the host happens to define BEA_LOCAL_LAB for another working corpus.
    os.environ["BEA_LOCAL_LAB"] = str(_FROZEN_LOCAL_LAB)

PROBE_DIR = Path(__file__).resolve().parent / "probe"
sys.path.insert(0, str(PROBE_DIR))
import select_probe  # noqa: E402
import probe_author  # noqa: E402
import refute as probe_refute  # noqa: E402


SCHEMA = "bea.re.campaign.v5"
REDUCER_SCHEMA = "bea.re.campaign-reducer.v1"
CAMPAIGN_RESEED_KIND = "CAMPAIGN_RESEED_CARRY"
CAMPAIGN_RESEED_SCHEMA = "bea.re.campaign-reseed-carry.v2"
LEGACY_CAMPAIGN_SCHEMA = "bea.re.campaign.v4"
BOUNDARY_EXPORT_SCHEMA = "bea.re.boundary-targets.v1"
RUNTIME_ADVANCE_KIND = "RUNTIME_CONTRACT_ADJUDICATION"
RUNTIME_ADVANCE_SCHEMA = "bea.re.runtime-contract-advance.v1"
REFUTER_SUBJECT_SCHEMA = "bea.re.refuter-subject.v1"
REBUILD_GATE_SCHEMA = "bea.re.rebuild-parity-gate.v2"
REBUILD_RESULT_SCHEMA = "bea.re.rebuild-parity-result.v2"
GHIDRA_ADVANCE_KIND = "GHIDRA_FUNCTION_BOUNDARY_PROMOTION"
GHIDRA_RESIDUAL_ADVANCE_KIND = "GHIDRA_RESIDUAL_FUNCTION_BOUNDARY_PROMOTION"
GHIDRA_RESIDUAL_ADVANCE_SCHEMA = (
    "bea.re.ghidra-residual-function-boundary-advance.v1"
)
GHIDRA_PARTITION_ADVANCE_KIND = "GHIDRA_RESIDUAL_EXACT_PARTITION_PROMOTION"
GHIDRA_PARTITION_ADVANCE_SCHEMA = (
    "bea.re.ghidra-residual-exact-partition-advance.v1"
)
GHIDRA_SEMANTIC_ADVANCE_KIND = "GHIDRA_FUNCTION_SEMANTIC_PROMOTION"
GHIDRA_SEMANTIC_ADVANCE_SCHEMA = (
    "bea.re.ghidra-function-semantic-promotion-advance.v1"
)
GHIDRA_SEMANTIC_LIVE_READY_SCHEMA = (
    "bea.re.ghidra-target-lock-semantic-live-promotion.v1"
)
GHIDRA_SEMANTIC_PREPARED_SCHEMA = (
    "bea.re.ghidra-target-lock-semantic-live-prepared.v1"
)
GHIDRA_SEMANTIC_PROOF_READY_SCHEMA = (
    "bea.re.ghidra-target-lock-semantic-proof-ready.v2"
)
GHIDRA_SEMANTIC_OBSERVATION_SCHEMA = (
    "bea.re.ghidra-target-lock-semantic-live-observation.v1"
)
TTD_CALL_CONTEXT_ADVANCE_KIND = "TTD_CALL_CONTEXT_OBSERVATION"
TTD_CALL_CONTEXT_ADVANCE_SCHEMA = "bea.re.ttd-call-context-observation-advance.v1"
TTD_CALL_CONTEXT_PROOF_SCHEMA = "bea-level521-impact-schema3-proof.v2"
TTD_CALL_CONTEXT_PARENT_RELATIVE = (
    Path("local-lab/ghidra-target-lock-semantic-generation9-20260804-v1")
    / "generation-9-live-semantic-promoted"
)
TTD_CALL_CONTEXT_PARENT_READY_SHA256 = (
    "8e254d25ab6e6054848e64530eeb51dd635d65751cda1e9a210a699f6582bd94"
)
TTD_CALL_CONTEXT_PARENT_REDUCER_ID = (
    "480af29c0d51a02527a8b0e144dc5c6f5127ec6399f0dfefbdcd221ecae94db4"
)
TTD_CALL_CONTEXT_PARENT_COUNTS = {
    "functions": 8124,
    "residuals": 6117,
    "questions": 15238,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14241,
    "adjudications": 3,
    "supersessions": 584,
}
TTD_CALL_CONTEXT_EVIDENCE_RELATIVE = Path(
    "local-lab/ttd-call-context-level521-impact-schema3-20260804-v1"
)
TTD_CALL_CONTEXT_PROOF_READY_SHA256 = (
    "7d784a6741c791677fa0083390c53424c0102ef9e7b5edca419eb23a97921765"
)
TTD_CALL_CONTEXT_VERIFIER_SHA256 = (
    "77efcca17feaa9a359713110a061df4aed5539098fbff07fd1729d78a81acec7"
)
TTD_CALL_CONTEXT_SEMANTIC_VERIFICATION_SHA256 = (
    "23455b52704ca7fadd4d4b541a7cbe759eb0d1f851fee691f6097596102f9529"
)
TTD_CALL_CONTEXT_TRACE_SHA256 = (
    "45ab04297f32bb27ac0c80e8ecb0b332e666a9955caea0763a83984affb74ac2"
)
TTD_CALL_CONTEXT_RUNTIME_SHA256 = (
    "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
)
TTD_CALL_CONTEXT_MEASURED_AT_UTC = "2026-08-04T12:26:52.9620884Z"
TTD_CALL_CONTEXT_PATH_NEUTRAL_SHA256 = (
    "3e12c0a391540ba79e50ee559bc04ccff344729fcbe0cec288731e12c5dc7558"
)
TTD_CALL_CONTEXT_EXPECTED_GENERATION10_COUNTS = {
    "functions": 8124,
    "residuals": 6117,
    "questions": 15241,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14241,
    "adjudications": 6,
    "supersessions": 584,
}
ATOMIC14_PARENT_READY_SHA256 = (
    "2160bf4963c07742cb4dd1aafb45e5d7caff74222381e01570d93fc9aafdde99"
)
ATOMIC14_FORMAL_READY_SHA256 = (
    "a504c24b1eab555da8a01fc56d91561d3147a508dd3f906b0ac41e97697a83e6"
)
ATOMIC14_LIVE_READY_SHA256 = (
    "f3d58ccb74891a20bade971f043382ab77b3c32bebdef977fabcd76274752541"
)
ATOMIC14_TARGETS_SHA256 = (
    "d3a042abacf69b99b46d4318c008f81cfde5c032ad09006220967c50e6bffc5a"
)
ATOMIC14_PADDING_SHA256 = (
    "90cdba62946e54fa181f8a3b209462152a49114946d1d955cb5e639501c8902a"
)
ATOMIC14_POST_PARITY_EXPORT_SHA256 = (
    "2b2415505ea4c280c2dcb0cdb3b66d3ecc3cf76d7d00ba89ba1061b1fa9eda5b"
)
ATOMIC14_POST_SNAPSHOT_READY_SHA256 = (
    "efabd9c2ae7a0be5adee2bf478df0cbec69482918197ae87ed7d6a9fc3ac6b3f"
)
ATOMIC14_POST_FUNCTIONS_SHA256 = (
    "e7ffc76b6073cf9f96c057ded436e24958596d9d14162e89f3e2d1007b620950"
)
ATOMIC14_POST_PROJECT_FILESET_SHA256 = (
    "309ba7f6fcf6a0d8ecdbd2803c0d7a1279a3d3027b7ee219efbbb0312e1143ab"
)
TARGET_LOCK_SEMANTIC_PARENT_RELATIVE = (
    Path("local-lab/console-callback-atomic14-post-campaign-20260803-v1")
    / "generation-8-live-promoted"
)
TARGET_LOCK_SEMANTIC_PARENT_READY_SHA256 = (
    "2ec4ac8acbe2affedd19d0896dc2b96e52fece8338bc776c1cd866b24368e47b"
)
TARGET_LOCK_SEMANTIC_PARENT_REDUCER_ID = (
    "04acc723a5ecbe40544223b3fa26fa15d3d5d50ce0fd64682147d4073c5670b5"
)
TARGET_LOCK_SEMANTIC_PARENT_COUNTS = {
    "functions": 8124,
    "residuals": 6117,
    "questions": 15238,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14241,
    "adjudications": 3,
    "supersessions": 584,
}
ATOMIC14_OLD_RESIDUAL = (
    "TEXT_RESIDUAL:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:"
    "0x004295BC-0x00429BC0"
)
ATOMIC14_OLD_QUESTION = "Q-f7892189985bc3ad"
ATOMIC14_OLD_CONTRACT = "C-b22fb6c9c19cfc0e"
ATOMIC14_START_VA = 0x004295BC
ATOMIC14_END_VA = 0x00429BC0
ATOMIC14_FUNCTION_COUNT = 14
ATOMIC14_FUNCTION_BYTES = 1433
ATOMIC14_PADDING_COUNT = 15
ATOMIC14_PADDING_BYTES = 107
GLOBAL_INIT515_LINEAGE_SCHEMA = "bea.re.global-init515-campaign-lineage.v1"
GLOBAL_INIT515_LINEAGE_READY_SHA256 = (
    "384a9ba709dd9657ca2e06fce427fbc265a8915cb62dc4b992ee6da0ae8e2e8c"
)
GLOBAL_INIT515_LINEAGE_OWNER_SHA256 = (
    "54e8a92fc01314baaf24e24d03c19aa52adb8b1481ce2ecffb225e4cace61685"
)
GLOBAL_INIT515_LINEAGE_TSV_SHA256 = (
    "bd66c5f88f5b4d93c95a5e57f97fb0159ebf4ceef969e5809d5fd0e95c773bf1"
)
GLOBAL_INIT515_TARGET_SET_SHA256 = (
    "73bb797ee4d76da87c348b2908ac684cf06f7fcc4eecae9b9a67985bb5f2d6f9"
)
GLOBAL_INIT515_LIVE_PROMOTION_SCHEMA = (
    "bea.re.ghidra-global-init515-live-promotion.v1"
)
GLOBAL_INIT515_LIVE_PREPARED_SCHEMA = (
    "bea.re.ghidra-global-init515-live-prepared.v1"
)
GLOBAL_INIT515_LIVE_OBSERVATION_SCHEMA = (
    "bea.re.ghidra-global-init515-live-observation.v1"
)
GLOBAL_INIT515_PROCESS_SCHEMA = "bea.re.contained-process.v1"
GLOBAL_INIT515_COUNT = 515
GLOBAL_INIT515_LIVE_OWNER_SHA256 = (
    "a1adf103f4c18487553970c62a21f01ea5cfa49c8039b3f299042ff6fc9e8747"
)
GLOBAL_INIT515_FORMAL_READY_SHA256 = (
    "0fa28300606f55d96e9e4c4168501c39d8eee25823033042d89339ae58d40729"
)
GLOBAL_INIT515_MANIFEST_SHA256 = (
    "d9b919ee08d9d8becaa10ce2e248c604730fc7cbb97989da1e8e4d632d4e1abd"
)
GLOBAL_INIT515_ENVELOPE_TOOL_SHA256 = (
    "f8a2b456c30969d6b7af480f391f340748db8db65771f239d925b4d0b4ef1201"
)
GLOBAL_INIT515_APPLY_OUTPUT_SHA256 = (
    "93da623428ad53bd511a656c071ba2f53886c2d99a2f05f592efa5cdc9782c40"
)
GLOBAL_INIT515_PRE_FUNCTIONS_SHA256 = (
    "26977c69e3530ff9344c6456b3a0dac218775eaf0c1043ac2c89c6a9b95ab368"
)
GLOBAL_INIT515_PRE_PROGRAM_SHA256 = (
    "eaf62f346c0c0efebb629bef775f519882bfad0aaa61917929d5fda6805c43ad"
)
GLOBAL_INIT515_PRE_SYMBOLS_SHA256 = (
    "9f736e1c268550371a951315e79ad5bc85058a89127269ac15002cf95155e8c4"
)
GLOBAL_INIT515_PRE_FILESET_SHA256 = (
    "317a93b9de718f5c0b483fa5e6c7ae0869b7fd99b895d28c2864633f1c104345"
)
GLOBAL_INIT515_SYMBOL_TOOL_SHA256 = (
    "6ea0e6ce2669dd9cb325a052df70cd2f84cd5ebc1319cf5ba8c089691d660327"
)
GLOBAL_INIT515_INVENTORY_TOOL_SHA256 = (
    "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"
)
GLOBAL_INIT515_OUTSIDE_SYMBOLS_SHA256 = (
    "149b88937826f6a8146eaf24f773fd9bad325b0eacbac576c2a32d4e300649da"
)
GLOBAL_INIT515_ANALYZE_HEADLESS_SHA256 = (
    "dd7b9d17d32ed70a71df82a43a21cdaed6c4ce67064e30f8642c149f81c2ae07"
)
GLOBAL_INIT515_PYTHON_SHA256 = (
    "fda7026477256845afab371e354c4d512896665f1761939cb5887d0a9dec257a"
)
GLOBAL_INIT515_JAVA_SHA256 = (
    "5f6248f9c0f32b38ffaba813819bf3331536a48c7ddc45b18e73acd15a6cf7ef"
)
GLOBAL_INIT515_WINDOWS_COMMAND_SHA256 = (
    "8dd1ebb0b969370c70a5ee7f7ee347949aa7046aa5e1a33fcd7b1e9415b21fc3"
)
GLOBAL_INIT515_FORMAL_OWNER_SHA256 = (
    "2fea029379aaf81df072907a87e142f03e4c1d261d19325933b18823b4fef972"
)
GLOBAL_INIT515_CAMPAIGN_OWNER_SHA256 = (
    "a05b0af174870fa45ea33895775680e003328a2cb29e8ed071aee09aa852af86"
)
GLOBAL_INIT515_POST_FUNCTIONS_SHA256 = (
    "2e25b287ad5521780286f6b30e92172c84ab4f1e92ac933581593cc0f6cfc542"
)
GLOBAL_INIT515_POST_PROGRAM_SHA256 = (
    "c8bbbebaee33a0bacf1f762948bd9ff2beb8595a86ac431f6b690c22ef2ae0cb"
)
GLOBAL_INIT515_POST_SYMBOLS_SHA256 = (
    "02edbc524890117385f14ad74fb7d400c8cfd53c2c0ef08da5bfc1624c03ed29"
)
CONTRACT_CANDIDATE_SCHEMA = "bea.re.contract-candidates.v1"
RUNTIME_CONTRACT_INPUT_SCHEMA = "bea.re.runtime-contract.v1"
RUNTIME_CONTRACT_OVERLAY_SCHEMA = "bea.re.runtime-contract-overlay.v1"
RUNTIME_ADJUDICATION_SCHEMA = "bea.re.runtime-contract-adjudication.v1"
RUNTIME_HOLDOUT_INPUT_SCHEMA = "bea.re.runtime-question-holdout.v1"
RUNTIME_HOLDOUT_PREREG_SCHEMA = "bea.re.runtime-holdout-preregistration.v1"
RUNTIME_HOLDOUT_CONTROL_PREREG_SCHEMA = (
    "bea.re.runtime-holdout-control-preregistration.v1"
)
REFUTER_RESULT_SCHEMA = "bea.re.refuter-result.v1"
GHIDRA_PROMOTION_EVIDENCE_SCHEMA = "bea.re.ghidra-function-promotion-evidence.v2"
LEGACY_GHIDRA_PROMOTION_EVIDENCE_SCHEMA = "bea.re.ghidra-function-promotion-evidence.v1"
GHIDRA_PROMOTION_READY_SCHEMA = "bea-ghidra-function-promotion.v2"
LEGACY_GHIDRA_PROMOTION_READY_SCHEMA = "bea-ghidra-function-promotion.v1"
GHIDRA_PROJECT_BACKUP_SCHEMA = "onslaught-ghidra-project-backup.v2"
LEGACY_GHIDRA_PROJECT_BACKUP_SCHEMA = "onslaught-ghidra-project-backup.v1"
REQUIRED_SNAPSHOT_SCHEMA = "bea.re.coverage-ledger.v2"


def _repo_root() -> Path:
    """Resolve evidence paths from the owning checkout, including frozen reducers."""
    configured = os.environ.get("BEA_REPO_ROOT")
    if configured:
        return Path(configured).resolve()
    cwd = Path.cwd().resolve()
    if (cwd / "tools" / "re_campaign.py").is_file() and (cwd / ".git").exists():
        return cwd
    return Path(__file__).resolve().parent.parent


REPO_ROOT = _repo_root()
GLOBAL_INIT515_FORMAL_ROOT = (
    REPO_ROOT / "local-lab/formal-global-init515-proof-20260803-v4"
)
GLOBAL_INIT515_ENVELOPE_TOOL_PATH = (
    GLOBAL_INIT515_FORMAL_ROOT / "tools/CreateFunctionsFromBoundaryManifest.java"
)
GLOBAL_INIT515_INVENTORY_TOOL_PATH = (
    GLOBAL_INIT515_FORMAL_ROOT / "tools/ExportFullFunctionInventory.java"
)
GLOBAL_INIT515_SYMBOL_TOOL_PATH = (
    GLOBAL_INIT515_FORMAL_ROOT / "tools/ExportTargetSymbolInventory.java"
)
GLOBAL_INIT515_MANIFEST_PATH = (
    GLOBAL_INIT515_FORMAL_ROOT / "inputs/admissible515.tsv"
)
GLOBAL_INIT515_ANALYZE_HEADLESS_PATH = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)
GLOBAL_INIT515_PYTHON_PATH = Path(
    r"C:\Users\david\AppData\Local\Python\pythoncore-3.14-64\python.exe"
)
GLOBAL_INIT515_JAVA_PATH = Path(
    r"C:\Program Files\Eclipse Adoptium\jdk-21.0.9.10-hotspot\bin\java.exe"
)
GLOBAL_INIT515_WINDOWS_ROOT = Path(r"C:\Windows")
GLOBAL_INIT515_WINDOWS_COMMAND_PATH = GLOBAL_INIT515_WINDOWS_ROOT / "System32/cmd.exe"
GLOBAL_INIT515_FORMAL_OWNER_PATH = (
    GLOBAL_INIT515_FORMAL_ROOT / "tools/ghidra_global_init_full520_proof.py"
)
GLOBAL_INIT515_LINEAGE_ROOT = (
    REPO_ROOT / "local-lab/global-init515-campaign-lineage-v1-ready"
)
GLOBAL_INIT515_LINEAGE_OWNER_PATH = GLOBAL_INIT515_LINEAGE_ROOT / "lineage-owner.py"
GLOBAL_INIT515_MUTEX_NAME = (
    r"Local\OnslaughtToolkit.BEA.Ghidra.GlobalInit515.Live.v1"
)
LEGACY_CAMPAIGN_CARRY_READY_SHA256 = (
    "bb878d54510c39d834094bd947b80e50fc182ff4e9c9ef05a02b77cc1435b604"
)
LEGACY_CAMPAIGN_CARRY_SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
LEGACY_CAMPAIGN_CARRY_ROOT = (
    REPO_ROOT
    / "local-lab"
    / "re-campaign"
    / "campaign-2026-08-02-ghidra-promotion-generation-3-v5"
)
FROZEN_V5_CAMPAIGN_CARRY_READY_SHA256 = (
    "5bddceb51c131d9c3a1ac634fd0672d0e9999b7ccab3f65dd2b33b4a68947cde"
)
FROZEN_V5_CAMPAIGN_CARRY_REDUCER_ID = (
    "384c325149a4244a5eb48fa70d01bff541584d7b3c5b90b69e4658eed96852d6"
)
FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
FROZEN_V5_CAMPAIGN_CARRY_GENERATION = 5
FROZEN_V5_CAMPAIGN_CARRY_ROOT = (
    REPO_ROOT
    / "local-lab"
    / "re-campaign"
    / "campaign-2026-08-02-observed40-generation-5-v5-carried-r3-invariant-bound"
)
GLOBAL_INIT515_CAMPAIGN_ROOT = FROZEN_V5_CAMPAIGN_CARRY_ROOT
GLOBAL_INIT515_CAMPAIGN_OWNER_PATH = (
    GLOBAL_INIT515_CAMPAIGN_ROOT / "_reducer/tools/re_campaign.py"
)
LEGACY_GHIDRA_PROMOTION_EVIDENCE_SHA256 = (
    "2ce5eddef7798f8379137c3804a51f5ff6a4458e15f0fa3268177d4afedbace4"
)
LEGACY_GHIDRA_PROMOTION_TOOL_SHA256 = (
    "9fef78a42e14c1ff1b0a4ed934f96178828ba31544e97512067e85ef6fea1961"
)
LEGACY_GHIDRA_PROMOTION_TOOL_SNAPSHOT = (
    REPO_ROOT
    / "local-lab"
    / "ghidra-live-promotion-2026-08-02"
    / "historical-tool-snapshots"
    / LEGACY_GHIDRA_PROMOTION_TOOL_SHA256
    / "CreateFunctionsFromAddressList.java"
)
OUTPUTS = (
    "campaign-functions.tsv",
    "campaign-residuals.tsv",
    "campaign-questions.tsv",
    "campaign-scenarios.tsv",
    "campaign-levers.tsv",
    "campaign-contracts.tsv",
    "campaign-adjudications.tsv",
    "campaign-supersessions.tsv",
)


class CampaignError(ValueError):
    """A campaign input or READY receipt is incomplete or inconsistent."""


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _reducer_sources() -> list[tuple[str, str, Path]]:
    """Return the complete deterministic reducer dependency set.

    Campaign generations carry these exact bytes. A later tool revision may
    migrate an older generation, but it may not silently reinterpret it.
    """
    lab_root = (
        _FROZEN_LOCAL_LAB
        if (_FROZEN_LOCAL_LAB / "aya_roundtrip.py").is_file()
        else REPO_ROOT / "local-lab"
    )
    return [
        ("campaign", "_reducer/tools/re_campaign.py", Path(__file__).resolve()),
        (
            "coverage",
            "_reducer/tools/re_coverage_ledger.py",
            Path(coverage.__file__).resolve(),
        ),
        (
            "ghidra-backup",
            "_reducer/tools/ghidra_project_backup.py",
            Path(ghidra_backup.__file__).resolve(),
        ),
        (
            "probe-selector",
            "_reducer/tools/probe/select_probe.py",
            Path(select_probe.__file__).resolve(),
        ),
        (
            "probe-author",
            "_reducer/tools/probe/probe_author.py",
            Path(probe_author.__file__).resolve(),
        ),
        (
            "probe-container",
            "_reducer/tools/probe/bea_lab.py",
            Path(probe_author.bea_lab.__file__).resolve(),
        ),
        (
            "mission-emitter",
            "_reducer/tools/probe/mission_script_emitter.py",
            Path(probe_author.mse.__file__).resolve(),
        ),
        (
            "probe-refuter",
            "_reducer/tools/probe/refute.py",
            Path(probe_refute.__file__).resolve(),
        ),
        (
            "probe-finding-schema",
            "_reducer/tools/probe/finding_schema.json",
            Path(probe_refute.SCHEMA_PATH).resolve(),
        ),
        (
            "aya-container-codec",
            "_reducer/local-lab/aya_roundtrip.py",
            (lab_root / "aya_roundtrip.py").resolve(),
        ),
        (
            "mission-bytecode-parser",
            "_reducer/local-lab/msl/script_parse.py",
            (lab_root / "msl" / "script_parse.py").resolve(),
        ),
        (
            "aya-independent-walker",
            "_reducer/local-lab/msl/bea_aya.py",
            (lab_root / "msl" / "bea_aya.py").resolve(),
        ),
        (
            "level521-call-context-refuter",
            "_reducer/local-lab/ttd-call-context-level521-impact-schema3-20260804-v1/verify.py",
            (
                lab_root
                / "ttd-call-context-level521-impact-schema3-20260804-v1"
                / "verify.py"
            ).resolve(),
        ),
    ]


def _reducer_id(files: list[dict[str, object]]) -> str:
    canonical = "".join(
        f"{row['role']}\t{row['sha256']}\t{row['bytes']}\t{row['path']}\n"
        for row in sorted(files, key=lambda item: str(item["path"]))
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _current_reducer_manifest() -> dict[str, object]:
    files: list[dict[str, object]] = []
    for role, relative, source in _reducer_sources():
        if not source.is_file():
            raise CampaignError(f"campaign reducer dependency is missing: {source}")
        files.append(
            {
                "role": role,
                "path": relative,
                "bytes": source.stat().st_size,
                "sha256": coverage.sha256_of(source),
            }
        )
    return {
        "schema": REDUCER_SCHEMA,
        "id": _reducer_id(files),
        "entry": "_reducer/tools/re_campaign.py",
        "files": sorted(files, key=lambda item: str(item["path"])),
    }


def _publish_reducer(stage: Path) -> dict[str, object]:
    manifest = _current_reducer_manifest()
    by_role = {role: source for role, _relative, source in _reducer_sources()}
    for row in manifest["files"]:
        destination = stage / str(row["path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        source = by_role[str(row["role"])]
        destination.write_bytes(source.read_bytes())
        actual = coverage.file_stamp(destination)
        if (
            actual["bytes"] != row["bytes"]
            or actual["sha256"] != row["sha256"]
        ):
            raise CampaignError(f"campaign reducer snapshot changed while copying: {source}")
    return manifest


def _validate_reducer_snapshot(campaign: Path, receipt: dict) -> dict[str, object]:
    manifest = receipt.get("reducer")
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema",
        "id",
        "entry",
        "files",
    }:
        raise CampaignError("campaign READY lacks an exact reducer manifest")
    if (
        manifest.get("schema") != REDUCER_SCHEMA
        or manifest.get("entry") != "_reducer/tools/re_campaign.py"
        or not isinstance(manifest.get("files"), list)
    ):
        raise CampaignError("campaign reducer manifest is unsupported")
    files = manifest["files"]
    seen_roles: set[str] = set()
    seen_paths: set[str] = set()
    actual_files: list[dict[str, object]] = []
    for row in files:
        if not isinstance(row, dict) or set(row) != {"role", "path", "bytes", "sha256"}:
            raise CampaignError("campaign reducer contains a malformed file stamp")
        role = row.get("role")
        relative = row.get("path")
        if (
            not isinstance(role, str)
            or not role
            or role in seen_roles
            or not isinstance(relative, str)
            or not relative.startswith("_reducer/")
            or relative in seen_paths
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
        ):
            raise CampaignError("campaign reducer contains a duplicate/escaping file")
        seen_roles.add(role)
        seen_paths.add(relative)
        path = campaign / Path(relative)
        if not path.is_file():
            raise CampaignError(f"campaign reducer file is missing: {relative}")
        actual = coverage.file_stamp(path)
        actual_row = {
            "role": role,
            "path": relative,
            "bytes": actual["bytes"],
            "sha256": actual["sha256"],
        }
        if actual_row != row:
            raise CampaignError(f"campaign reducer file has changed: {relative}")
        actual_files.append(actual_row)
    if _reducer_id(actual_files) != manifest.get("id"):
        raise CampaignError("campaign reducer bundle digest is inconsistent")
    return manifest


def _validate_reducer_bundle(campaign: Path, receipt: dict) -> dict[str, object]:
    manifest = _validate_reducer_snapshot(campaign, receipt)
    current = _current_reducer_manifest()
    if current["id"] != manifest.get("id"):
        raise CampaignError(
            "campaign reducer differs from this verifier; use its frozen "
            f"{manifest['entry']} or publish an explicit migration"
        )
    return manifest


def _read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise CampaignError(f"required ledger is missing: {path}")
    with open(path, encoding="utf-8") as handle:
        rows = [line for line in handle if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


def _write_tsv(
    path: Path,
    columns: list[str],
    rows: list[dict],
    *,
    schema: str = SCHEMA,
) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {schema}\n")
        writer = csv.DictWriter(
            handle,
            fieldnames=columns,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _bool(value: object) -> bool:
    return str(value).lower() == "true"


def _integer(value: object, default: int = 0) -> int:
    try:
        return int(str(value), 0)
    except (TypeError, ValueError):
        try:
            return int(str(value))
        except (TypeError, ValueError):
            return default


def _question_id(question_type: str, entity_key: str) -> str:
    return f"Q-{_sha256_text(question_type + '|' + entity_key)[:16]}"


def _contract_id(entity_key: str) -> str:
    return f"C-{_sha256_text(entity_key)[:16]}"


def _candidate_key(specimen_sha: str, va: str) -> str:
    return f"CODE_CANDIDATE:{specimen_sha}:VA={va.upper()}"


def _residual_key(specimen_sha: str, start: str, end: str) -> str:
    return (
        f"TEXT_RESIDUAL:{specimen_sha}:"
        f"0x{int(start, 16):08X}-0x{int(end, 16):08X}"
    )


def _region_key(specimen_sha: str, start: str, end: str) -> str:
    return (
        f"DARK_REGION:{specimen_sha}:"
        f"0x{int(start, 16):08X}-0x{int(end, 16):08X}"
    )


def load_snapshot(snapshot: Path) -> dict:
    try:
        ready = coverage.verify_snapshot(snapshot)
    except coverage.LedgerInputError as exc:
        raise CampaignError(f"campaign refuses unverified coverage snapshot: {exc}") from exc
    summary_path = snapshot / "ledger-summary.json"
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot read coverage summary {summary_path}: {exc}") from exc
    if summary.get("schema") != REQUIRED_SNAPSHOT_SCHEMA:
        raise CampaignError(
            f"campaign requires {REQUIRED_SNAPSHOT_SCHEMA}, got {summary.get('schema')!r}"
        )
    if summary.get("denominators", {}).get("bodyAccountingMethod") != "EXACT_GHIDRA_FRAGMENTS":
        raise CampaignError("campaign refuses hull-only function accounting")
    graph = summary.get("inputs", {}).get("parityGraph")
    if not graph:
        raise CampaignError("campaign requires an authenticated parity-graph input")

    functions = _read_tsv(snapshot / "ledger-functions.tsv")
    natives = _read_tsv(snapshot / "ledger-native-handlers.tsv")
    gaps = _read_tsv(snapshot / "ledger-gaps.tsv")
    residuals = _read_tsv(snapshot / "ledger-unmapped.tsv")
    dark_regions = select_probe.load_dark_regions(snapshot)
    expected_functions = summary["denominators"]["functionPopulation"]
    expected_natives = summary["denominators"]["nativeRegistryPopulation"]
    if len(functions) != expected_functions or len(natives) != expected_natives:
        raise CampaignError(
            "snapshot row counts do not reproduce denominators: "
            f"functions={len(functions)}/{expected_functions}, "
            f"natives={len(natives)}/{expected_natives}"
        )
    bad_keys = [row.get("va", "") for row in functions if not row.get("entityKey", "").startswith("CODE:")]
    if bad_keys:
        raise CampaignError(f"{len(bad_keys)} function rows lack exact CODE entity keys")
    specimen_sha = str(summary.get("inputs", {}).get("specimen", {}).get("sha256", ""))
    residual_bytes = 0
    residual_observed = 0
    residual_keys: set[str] = set()
    for row in residuals:
        expected_key = _residual_key(specimen_sha, row.get("startVa", ""), row.get("endVa", ""))
        if row.get("entityKey") != expected_key:
            raise CampaignError(
                f"residual row does not reproduce its specimen/range entity key: {row.get('entityKey')!r}"
            )
        if row["entityKey"] in residual_keys:
            raise CampaignError(f"coverage snapshot repeats residual entity {row['entityKey']}")
        residual_keys.add(row["entityKey"])
        residual_bytes += _integer(row.get("bytes"), -1)
        residual_observed += _integer(row.get("observedBytes"), -1)
    byte_summary = summary.get("bytes", {})
    if residual_bytes != byte_summary.get("unmappedByAnyFunction"):
        raise CampaignError("residual rows do not reproduce the unmapped-byte denominator")
    if residual_observed != byte_summary.get("executedButUnmapped"):
        raise CampaignError("residual rows do not reproduce executed-unmapped bytes")
    if len(residuals) != byte_summary.get("allUnmappedSegments"):
        raise CampaignError("residual row count does not reproduce the snapshot summary")
    return {
        "ready": ready,
        "summary": summary,
        "functions": functions,
        "natives": natives,
        "gaps": gaps,
        "residuals": residuals,
        "darkRegions": dark_regions,
        "snapshotFiles": {
            name: coverage.file_stamp(snapshot / name)
            for name in coverage.SNAPSHOT_FILES
        },
    }


def _scored_regions(dark_regions: list[dict[str, str]]) -> list[dict]:
    return [select_probe.score_region(row) for row in dark_regions]


def _lever_for_function(va: int, regions: list[dict]) -> dict | None:
    for region in regions:
        lo = int(region["startVa"], 16)
        hi = int(region["endVa"], 16)
        if lo <= va < hi:
            return region
    return None


def build_campaign_rows(data: dict) -> dict[str, list[dict]]:
    summary = data["summary"]
    specimen_sha = summary["inputs"]["specimen"]["sha256"]
    generated = summary["generatedAtUtc"]
    regions = _scored_regions(data["darkRegions"])

    function_rows = []
    for row in data["functions"]:
        va = int(row["va"], 16)
        lever = _lever_for_function(va, regions) if row["execState"] == "DARK" else None
        evidence = ["BASELINE_STATIC", "ANALYST_METADATA_ONLY"]
        if row["execState"] != "DARK":
            evidence.append("RUNTIME_BOUNDED")
        function_rows.append(
            {
                "entityKey": row["entityKey"],
                "entryVa": row["va"],
                "entryRva": row["entryRva"],
                "currentName": row["name"],
                "nativeShippedName": row.get("nativeShippedName", ""),
                "nativeRegistryStatus": row.get("nativeRegistryStatus", ""),
                "bodyRangesRva": row["bodyRangesRva"],
                "bodyRangeSetSha256": row["bodyRangeSetSha256"],
                "bodyBytes": row["bodyBytes"],
                "executionState": row["execState"],
                "observedBytes": row["observedBytes"],
                "nameClass": row["nameClass"],
                "understoodTier": row["understoodTier"],
                "reachClass": row["reachClass"],
                "evidenceStates": ";".join(evidence),
                "resolutionState": "OPEN_JOIN" if row["execState"] != "DARK" else "UNKNOWN_WITH_FALSIFIER",
                "semanticGrade": "OPAQUE",
                "campaignState": "OPEN_EXECUTED" if row["execState"] != "DARK" else "OPEN_DARK",
                "lever": (lever or {}).get("lever", "existing-trace-static-join"),
                "leverConfidence": (lever or {}).get("leverConfidence", "OBSERVED"),
                "requiresElevation": (lever or {}).get("needsElevation", False),
                "cheapestFalsifier": (
                    (lever or {}).get("falsifier")
                    or "Mine an existing trace and require receiver/write/return evidence to discriminate the proposed identity."
                ),
                "lastMeasurementDate": generated,
            }
        )

    residual_rows = []
    for row in data["residuals"]:
        observed = _integer(row["observedBytes"]) > 0
        residual_rows.append(
            {
                "entityKey": row["entityKey"],
                "startVa": row["startVa"],
                "endVa": row["endVa"],
                "bytes": row["bytes"],
                "observedBytes": row["observedBytes"],
                "observationState": row["observationState"],
                "classification": row["classification"],
                "classificationVerdict": row["classificationVerdict"],
                "terminalState": row["terminalState"],
                "bytePattern": row["bytePattern"],
                "prevFunc": row["prevFunc"],
                "nextFunc": row["nextFunc"],
                "campaignState": (
                    "OPEN_EXECUTED_RESIDUAL" if observed else "OPEN_DARK_RESIDUAL"
                ),
                "lever": (
                    "INDEPENDENT_DISASSEMBLY_PLUS_EXISTING_TRACE"
                    if observed
                    else "STATIC_CLASSIFICATION_FIRST"
                ),
                "requiresElevation": False,
                "cheapestFalsifier": (
                    "Independent decoding shows an interior fragment, shared tail, or data rather than a new entry."
                    if observed
                    else "Cross-references, decoding, and neighboring control flow distinguish code, data, and alignment; byte appearance alone cannot."
                ),
                "questionIds": "",
                "lastMeasurementDate": generated,
            }
        )

    questions: list[dict] = []
    question_keys: set[tuple[str, str]] = set()

    def add_question(
        question_type: str,
        entity_key: str,
        priority: int,
        question: str,
        instrument: str,
        falsifier: str,
        requires_elevation: bool = False,
        score: float = 0.0,
        source: str = "",
    ) -> None:
        key = (question_type, entity_key)
        if key in question_keys:
            return
        question_keys.add(key)
        questions.append(
            {
                "questionId": _question_id(question_type, entity_key),
                "questionType": question_type,
                "entityKey": entity_key,
                "priority": priority,
                "score": round(score, 3),
                "state": "OPEN",
                "requiresElevation": requires_elevation,
                "recommendedInstrument": instrument,
                "question": question,
                "cheapestFalsifier": falsifier,
                "source": source,
                "currentOwner": "recursive-re-campaign",
                "generation": 0,
                "attemptCount": 0,
                "parentQuestionId": "",
                "lastOutcome": "UNSCORED",
                "lastMeasurementDate": generated,
            }
        )

    function_by_va = {row["entryVa"].lower(): row for row in function_rows}
    for native in data["natives"]:
        handler = native["handlerVa"]
        native_order_score = 1000.0 - float(native["index"])
        function = function_by_va.get(handler.lower())
        key = function["entityKey"] if function else _candidate_key(specimen_sha, handler)
        observed = _bool(native["observed"])
        terminal = native["terminalState"]
        if terminal == "BOUNDARY_MISSING":
            add_question(
                "NATIVE_BOUNDARY",
                key,
                0 if observed else 3,
                f"What are the exact body fragments and ABI of Mission native {native['shippedName']} at {handler}?",
                "STATIC_BOUNDARY_REVIEW_PLUS_EXISTING_COVERAGE" if observed else "STATIC_BOUNDARY_REVIEW",
                "Independent disassembly rejects the proposed start/end or the entry byte is not executable code.",
                score=native_order_score,
                source=f"native:{native['index']}",
            )
        elif terminal == "WRONG_PRIOR_NAME":
            add_question(
                "NATIVE_IDENTITY",
                key,
                1 if observed else 3,
                f"Which scoped behavior owns shipped native {native['shippedName']} after the prior Ghidra name was contradicted?",
                "EXISTING_TRACE_CALL_AND_STATE_QUERY" if observed else "AUTHORED_SINGLETON_PROBE",
                "Receiver, arguments, or state transition select a competing identity.",
                requires_elevation=not observed,
                score=native_order_score,
                source=f"native:{native['index']}",
            )
        elif observed:
            add_question(
                "NATIVE_BEHAVIOR",
                key,
                1,
                f"What receiver, inputs, writes, return, and side effects define Mission native {native['shippedName']} on an observed path?",
                "EXISTING_TRACE_CONTRACT_QUERY",
                "The observed handler call has a receiver/state transition incompatible with the shipped name.",
                score=native_order_score,
                source=f"native:{native['index']}",
            )

    for function in function_rows:
        if function["executionState"] != "DARK" and function["nameClass"] in ("FUN", "VFUNC_SLOT"):
            add_question(
                "EXECUTED_FUNCTION_IDENTITY",
                function["entityKey"],
                1,
                f"Which scoped behavior owns executed function {function['entryVa']}?",
                "STATIC_NEIGHBORHOOD_PLUS_EXISTING_TRACE",
                function["cheapestFalsifier"],
                score=float(function["observedBytes"]),
                source="ledger-functions",
            )

    entities_with_questions = {row["entityKey"] for row in questions}
    for function in function_rows:
        if function["entityKey"] in entities_with_questions:
            continue
        if function["executionState"] == "DARK":
            question_type = "DARK_FUNCTION_CONTRACT"
            question = (
                f"What behavior, callers, inputs, outputs, and writes define dark function "
                f"{function['entryVa']} ({function['currentName']})?"
            )
            instrument = function["lever"]
            priority = 3
            score = float(function["bodyBytes"])
        else:
            question_type = "EXECUTED_FUNCTION_CONTRACT"
            question = (
                f"What receiver, inputs, outputs, writes, ordering, and failure behavior define "
                f"executed function {function['entryVa']} ({function['currentName']})?"
            )
            instrument = "EXISTING_TRACE_STATIC_CONTRACT_JOIN"
            priority = 2
            score = float(function["observedBytes"])
        add_question(
            question_type,
            function["entityKey"],
            priority,
            question,
            instrument,
            function["cheapestFalsifier"],
            requires_elevation=_bool(function["requiresElevation"]),
            score=score,
            source="ledger-functions:complete-frontier",
        )

    for residual in residual_rows:
        observed = residual["observationState"] == "EXECUTED"
        add_question(
            "EXECUTED_TEXT_BOUNDARY" if observed else "DARK_TEXT_CLASSIFICATION",
            residual["entityKey"],
            1 if observed else 4,
            (
                f"Which exact function body or data/code boundary owns executed residual "
                f"{residual['startVa']}..{residual['endVa']}?"
                if observed
                else f"Is dark residual {residual['startVa']}..{residual['endVa']} code, data, or padding, and what falsifies that classification?"
            ),
            residual["lever"],
            residual["cheapestFalsifier"],
            score=float(residual["bytes"]),
            source="ledger-unmapped",
        )

    for region in regions:
        key = _region_key(specimen_sha, region["startVa"], region["endVa"])
        add_question(
            "DARK_REGION_REACHABILITY",
            key,
            2 if region["inCallersObserved"] else 4,
            f"Can the declared lever reach and discriminate dark region {region['startVa']}..{region['endVa']}?",
            region["lever"],
            region["falsifier"],
            requires_elevation=bool(region["needsElevation"]),
            score=float(region["score"]),
            source="ledger-dark",
        )

    questions.sort(key=lambda row: (row["priority"], -float(row["score"]), row["questionId"]))

    scenario_rows = []
    for source in summary.get("sources", []):
        scenario_rows.append(
            {
                "scenarioId": f"S-{source['coverageSha256'][:16]}",
                "sourceId": source.get("sourceId", ""),
                "coverageSha256": source["coverageSha256"],
                "coverageIndex": source.get("coverageIndex", ""),
                "observedTextBytes": source.get("textBytesObserved", 0),
                "moduleName": source.get("moduleName") or "",
                "trace": source.get("trace") or "",
                "evidenceState": "RUNTIME_BOUNDED",
                "scopeState": "LEGACY_CAPTURE_SCOPE_ONLY",
                "requiresElevationToReuse": False,
                "lastMeasurementDate": generated,
            }
        )

    lever_rows = []
    for region in regions:
        lever_rows.append(
            {
                "regionKey": _region_key(specimen_sha, region["startVa"], region["endVa"]),
                "startVa": region["startVa"],
                "endVa": region["endVa"],
                "darkBytes": region["darkBytes"],
                "funcCount": region["funcCount"],
                "reachClass": region["reachClass"],
                "families": region["families"],
                "inCallersObserved": region["inCallersObserved"],
                "score": region["score"],
                "lever": region["lever"],
                "leverConfidence": region["leverConfidence"],
                "needsTtd": region["needsTtd"],
                "requiresElevation": region["needsElevation"],
                "reachableByProbing": region["reachableByProbing"],
                "falsifier": region["falsifier"],
                "state": "UNTESTED",
            }
        )

    question_ids_by_entity: dict[str, list[str]] = {}
    for question in questions:
        question_ids_by_entity.setdefault(question["entityKey"], []).append(
            question["questionId"]
        )
    for residual in residual_rows:
        residual["questionIds"] = ";".join(
            sorted(question_ids_by_entity.get(residual["entityKey"], []))
        )
    contract_rows = []
    for function in function_rows:
        question_ids = sorted(question_ids_by_entity.get(function["entityKey"], []))
        contract_rows.append(
            {
                "contractId": _contract_id(function["entityKey"]),
                "entityKey": function["entityKey"],
                "entityKind": "FUNCTION",
                "entryVa": function["entryVa"],
                "currentName": function["currentName"],
                "nativeShippedName": function["nativeShippedName"],
                "contractState": "OPEN",
                "semanticGrade": "C0_OPAQUE",
                "receiver": "UNKNOWN",
                "inputs": "UNKNOWN",
                "returns": "UNKNOWN",
                "writes": "UNKNOWN",
                "sideEffects": "UNKNOWN",
                "preconditions": "UNKNOWN",
                "failureModes": "UNKNOWN",
                "authorVerdict": "UNSCORED",
                "runtimeVerdict": "UNSCORED",
                "refuterVerdict": "UNSCORED",
                "questionIds": ";".join(question_ids),
                "evidenceRefs": "",
                "cheapestFalsifier": function["cheapestFalsifier"],
                "rebuildOwner": "UNASSIGNED",
                "rebuildImplementation": "UNMAPPED",
                "parityTests": "UNMAPPED",
                "rebuildState": "NOT_READY",
                "remainingUncertainty": "receiver; inputs; returns; writes; side effects; preconditions; failure modes",
                "supersedesEntityKeys": "",
                "lastMeasurementDate": generated,
            }
        )

    for residual in residual_rows:
        question_ids = sorted(question_ids_by_entity.get(residual["entityKey"], []))
        contract_rows.append(
            {
                "contractId": _contract_id(residual["entityKey"]),
                "entityKey": residual["entityKey"],
                "entityKind": "TEXT_RESIDUAL",
                "entryVa": residual["startVa"],
                "currentName": "<unmapped .text residual>",
                "nativeShippedName": "",
                "contractState": "OPEN_CLASSIFICATION",
                "semanticGrade": "C0_OPAQUE",
                "receiver": "UNKNOWN",
                "inputs": "UNKNOWN",
                "returns": "UNKNOWN",
                "writes": "UNKNOWN",
                "sideEffects": "UNKNOWN",
                "preconditions": "UNKNOWN",
                "failureModes": "UNKNOWN",
                "authorVerdict": "UNSCORED",
                "runtimeVerdict": (
                    "EXECUTED_BYTES_MEASURED"
                    if residual["observationState"] == "EXECUTED"
                    else "UNSCORED"
                ),
                "refuterVerdict": "UNSCORED",
                "questionIds": ";".join(question_ids),
                "evidenceRefs": "ledger-unmapped.tsv",
                "cheapestFalsifier": residual["cheapestFalsifier"],
                "rebuildOwner": "UNASSIGNED",
                "rebuildImplementation": "UNMAPPED",
                "parityTests": "UNMAPPED",
                "rebuildState": "NOT_READY",
                "remainingUncertainty": "code/data/padding classification and ownership",
                "supersedesEntityKeys": "",
                "lastMeasurementDate": generated,
            }
        )

    missing_questions = [
        row["entityKey"] for row in contract_rows if not row["questionIds"]
    ]
    if missing_questions:
        raise CampaignError(
            f"{len(missing_questions)} nonterminal contracts are unreachable from the question frontier"
        )

    return {
        "functions": function_rows,
        "residuals": residual_rows,
        "questions": questions,
        "scenarios": scenario_rows,
        "levers": lever_rows,
        "contracts": contract_rows,
        "adjudications": [],
        "supersessions": [],
    }


FUNCTION_COLUMNS = [
    "entityKey", "entryVa", "entryRva", "currentName", "nativeShippedName",
    "nativeRegistryStatus", "bodyRangesRva",
    "bodyRangeSetSha256", "bodyBytes", "executionState", "observedBytes",
    "nameClass", "understoodTier", "reachClass", "evidenceStates",
    "resolutionState", "semanticGrade", "campaignState", "lever",
    "leverConfidence", "requiresElevation", "cheapestFalsifier", "lastMeasurementDate",
]
RESIDUAL_COLUMNS = [
    "entityKey", "startVa", "endVa", "bytes", "observedBytes",
    "observationState", "classification", "classificationVerdict", "terminalState",
    "bytePattern", "prevFunc", "nextFunc", "campaignState", "lever",
    "requiresElevation", "cheapestFalsifier", "questionIds", "lastMeasurementDate",
]
QUESTION_COLUMNS = [
    "questionId", "questionType", "entityKey", "priority", "score", "state",
    "requiresElevation", "recommendedInstrument", "question", "cheapestFalsifier",
    "source", "currentOwner", "generation", "attemptCount",
    "parentQuestionId", "lastOutcome", "lastMeasurementDate",
]
SCENARIO_COLUMNS = [
    "scenarioId", "sourceId", "coverageSha256", "coverageIndex", "observedTextBytes",
    "moduleName", "trace", "evidenceState", "scopeState", "requiresElevationToReuse",
    "lastMeasurementDate",
]
LEVER_COLUMNS = [
    "regionKey", "startVa", "endVa", "darkBytes", "funcCount", "reachClass",
    "families", "inCallersObserved", "score", "lever", "leverConfidence", "needsTtd",
    "requiresElevation", "reachableByProbing", "falsifier", "state",
]
CONTRACT_COLUMNS = [
    "contractId", "entityKey", "entityKind", "entryVa", "currentName", "nativeShippedName",
    "contractState", "semanticGrade", "receiver", "inputs", "returns", "writes",
    "sideEffects", "preconditions", "failureModes", "authorVerdict", "runtimeVerdict",
    "refuterVerdict", "questionIds", "evidenceRefs", "cheapestFalsifier",
    "rebuildOwner", "rebuildImplementation", "parityTests", "rebuildState",
    "remainingUncertainty", "supersedesEntityKeys", "lastMeasurementDate",
]
CANDIDATE_CONTRACT_COLUMNS = [
    "contractId", "entityKey", "entryVa", "currentName", "proposedName",
    "nativeShippedName", "contractState", "semanticGrade", "receiver", "inputs",
    "returns", "writes", "sideEffects", "preconditions", "failureModes",
    "authorVerdict", "runtimeVerdict", "refuterVerdict", "questionIds", "cdbCalls",
    "traces", "argCountRuntime", "levelsCovered", "bodySpan", "argAccessors",
    "assertLine", "behaviourNote", "evidenceRefs", "cheapestFalsifier",
]
RUNTIME_CONTRACT_COLUMNS = CONTRACT_COLUMNS + [
    "scopeKind", "payloadSha256", "receiverVtable", "observedCallVas",
    "controlSummary", "runtimeEvidenceSha256", "baseContractId",
    "questionIdsAddressed",
]
ADJUDICATION_COLUMNS = [
    "adjudicationId", "baseContractId", "entityKey", "overlaySchema",
    "overlayReadySha256", "questionIdsAddressed", "refuterVerdict",
    "refuterEvidenceSha256", "semanticPromotionApplied", "terminalState",
    "successorQuestionIds", "remainingUncertainty", "measuredAtUtc",
]
SUPERSESSION_COLUMNS = [
    "supersessionId", "oldEntityKey", "newEntityKey", "kind", "verdict",
    "evidenceRefs", "measuredAtUtc",
]


def _campaign_rows_from_root(root: Path) -> dict[str, list[dict[str, str]]]:
    return {
        "functions": _read_tsv(root / "campaign-functions.tsv"),
        "residuals": _read_tsv(root / "campaign-residuals.tsv"),
        "questions": _read_tsv(root / "campaign-questions.tsv"),
        "scenarios": _read_tsv(root / "campaign-scenarios.tsv"),
        "levers": _read_tsv(root / "campaign-levers.tsv"),
        "contracts": _read_tsv(root / "campaign-contracts.tsv"),
        "adjudications": _read_tsv(root / "campaign-adjudications.tsv"),
        "supersessions": _read_tsv(root / "campaign-supersessions.tsv"),
    }


def _state_values(value: object, label: str) -> list[str]:
    values = [item for item in str(value or "").split(";") if item]
    if len(values) != len(set(values)):
        raise CampaignError(f"campaign {label} contains duplicate values")
    return values


def _partition_relation_context(receipt: dict) -> dict[str, object] | None:
    visited_parents: set[tuple[str, str]] = set()
    while True:
        advance = receipt.get("advance")
        if isinstance(advance, dict) and advance.get("kind") == GHIDRA_PARTITION_ADVANCE_KIND:
            break
        parent = receipt.get("parentCampaign")
        if parent is None:
            return None
        if not isinstance(parent, dict):
            raise CampaignError("campaign partition lineage parent is malformed")
        child_generation = _integer(receipt.get("generation"), -1)
        parent_path = _resolve_repo_or_absolute(
            parent.get("path"), "campaign partition lineage parent"
        )
        parent_ready = parent.get("ready")
        if not isinstance(parent_ready, dict):
            raise CampaignError("campaign partition lineage parent READY is malformed")
        parent_ready_path = parent_path / "campaign.ready.json"
        actual_parent_ready = _require_file_stamp(
            parent_ready_path,
            parent_ready,
            "campaign partition lineage parent READY",
        )
        parent_identity = (
            str(parent_ready_path.resolve()).casefold(),
            actual_parent_ready["sha256"],
        )
        if parent_identity in visited_parents:
            raise CampaignError("campaign partition lineage contains a parent cycle")
        visited_parents.add(parent_identity)
        parent_receipt = _runtime_json(
            parent_ready_path, "campaign partition lineage parent READY"
        )
        if _integer(parent_receipt.get("generation"), -1) != child_generation - 1:
            raise CampaignError("campaign partition lineage generation is non-monotone")
        receipt = parent_receipt
    if advance.get("schema") != GHIDRA_PARTITION_ADVANCE_SCHEMA:
        raise CampaignError("Ghidra exact-partition campaign advance schema is unsupported")
    retired = advance.get("retiredSubject")
    partition = advance.get("partition")
    if not isinstance(retired, dict) or not isinstance(partition, dict):
        raise CampaignError("Ghidra exact-partition campaign advance lacks its retired subject/partition")
    residual = retired.get("residual")
    question = retired.get("question")
    contract = retired.get("contract")
    if not all(isinstance(row, dict) for row in (residual, question, contract)):
        raise CampaignError("Ghidra exact-partition retired subject rows are malformed")
    successor_questions = partition.get("successorQuestionIds")
    successor_entities = partition.get("successorEntityKeys")
    if (
        not isinstance(successor_questions, list)
        or not isinstance(successor_entities, list)
        or any(not isinstance(value, str) or not value for value in successor_questions)
        or any(not isinstance(value, str) or not value for value in successor_entities)
        or len(successor_questions) != len(set(successor_questions))
        or len(successor_entities) != len(set(successor_entities))
    ):
        raise CampaignError("Ghidra exact-partition successor identity lists are malformed")
    if (
        residual.get("entityKey") != ATOMIC14_OLD_RESIDUAL
        or question.get("questionId") != ATOMIC14_OLD_QUESTION
        or question.get("entityKey") != ATOMIC14_OLD_RESIDUAL
        or contract.get("contractId") != ATOMIC14_OLD_CONTRACT
        or contract.get("entityKey") != ATOMIC14_OLD_RESIDUAL
        or not isinstance(advance.get("adjudicationId"), str)
        or not advance.get("adjudicationId")
    ):
        raise CampaignError("Ghidra exact-partition retired subject identity differs")

    parent_spec = receipt.get("parentCampaign")
    if not isinstance(parent_spec, dict):
        raise CampaignError("Ghidra exact-partition campaign lacks its parent")
    parent_path = _resolve_repo_or_absolute(
        parent_spec.get("path"), "Ghidra exact-partition parent campaign"
    )
    parent_ready = parent_spec.get("ready")
    _require_file_stamp(
        parent_path / "campaign.ready.json",
        parent_ready,
        "Ghidra exact-partition parent READY",
    )
    if not isinstance(parent_ready, dict) or parent_ready.get("sha256") != ATOMIC14_PARENT_READY_SHA256:
        raise CampaignError("Ghidra exact-partition parent identity differs")
    parent_rows = _campaign_rows_from_root(parent_path)

    def exact_parent_row(
        rows: list[dict[str, str]], field: str, value: str, label: str
    ) -> dict[str, str]:
        matches = [row for row in rows if row.get(field) == value]
        if len(matches) != 1:
            raise CampaignError(f"Ghidra exact-partition parent {label} is absent/ambiguous")
        return matches[0]

    if (
        residual
        != exact_parent_row(
            parent_rows["residuals"], "entityKey", ATOMIC14_OLD_RESIDUAL, "residual"
        )
        or question
        != exact_parent_row(
            parent_rows["questions"], "questionId", ATOMIC14_OLD_QUESTION, "question"
        )
        or contract
        != exact_parent_row(
            parent_rows["contracts"], "contractId", ATOMIC14_OLD_CONTRACT, "contract"
        )
    ):
        raise CampaignError("Ghidra exact-partition retired rows differ from Generation 7")

    snapshot = advance.get("snapshot")
    if not isinstance(snapshot, dict):
        raise CampaignError("Ghidra exact-partition snapshot stamp is malformed")
    snapshot_ready = snapshot.get("ready")
    if not isinstance(snapshot_ready, dict):
        raise CampaignError("Ghidra exact-partition snapshot READY stamp is malformed")
    snapshot_root = _resolve_repo_or_absolute(
        snapshot.get("root"), "Ghidra exact-partition snapshot root"
    )
    snapshot_ready_path = snapshot_ready.get("path")
    if (
        not isinstance(snapshot_ready_path, str)
        or not snapshot_ready_path
        or Path(snapshot_ready_path).is_absolute()
    ):
        raise CampaignError("Ghidra exact-partition snapshot READY path differs")
    evidence_stamps = []
    for field in ("liveReady", "formalReady", "targets", "padding", "parityExport"):
        stamp = advance.get(field)
        if not isinstance(stamp, dict):
            raise CampaignError(f"Ghidra exact-partition {field} stamp is malformed")
        evidence_stamps.append(stamp)
    evidence_stamps.append(
        {
            **snapshot_ready,
            "path": str((snapshot_root / snapshot_ready_path).resolve()),
        }
    )
    expected_evidence_refs = [
        f"{stamp.get('path')}#sha256={stamp.get('sha256')}" for stamp in evidence_stamps
    ]
    expected_evidence_hashes = [str(stamp.get("sha256", "")) for stamp in evidence_stamps]
    if any(
        not isinstance(stamp.get("path"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", str(stamp.get("sha256", "")))
        for stamp in evidence_stamps
    ):
        raise CampaignError("Ghidra exact-partition evidence stamps are malformed")
    return {
        "advance": advance,
        "retiredResidual": residual,
        "retiredQuestion": question,
        "retiredContract": contract,
        "successorQuestionIds": set(successor_questions),
        "successorEntityKeys": set(successor_entities),
        "adjudicationId": str(advance.get("adjudicationId", "")),
        "expectedEvidenceRefs": expected_evidence_refs,
        "expectedEvidenceHashes": expected_evidence_hashes,
    }


def _validate_campaign_relations(rows: dict[str, list[dict]], receipt: dict) -> None:
    """Validate semantic graph invariants independently of reducer replay."""

    functions = rows["functions"]
    residuals = rows["residuals"]
    questions = rows["questions"]
    contracts = rows["contracts"]
    adjudications = rows["adjudications"]
    supersessions = rows["supersessions"]
    partition_context = _partition_relation_context(receipt)

    def unique_map(items: list[dict], key: str, label: str) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for row in items:
            value = str(row.get(key, ""))
            if not value or value in result:
                raise CampaignError(
                    f"campaign {label} contains missing or duplicate {key} values"
                )
            result[value] = row
        return result

    function_by_entity = unique_map(functions, "entityKey", "functions")
    residual_by_entity = unique_map(residuals, "entityKey", "residuals")
    question_by_id = unique_map(questions, "questionId", "questions")
    contract_by_id = unique_map(contracts, "contractId", "contracts")
    contract_by_entity = unique_map(contracts, "entityKey", "contracts")
    if set(function_by_entity) & set(residual_by_entity):
        raise CampaignError("campaign function and residual entity keys overlap")
    entity_keys = set(function_by_entity) | set(residual_by_entity)
    if set(contract_by_entity) != entity_keys:
        raise CampaignError(
            "campaign contracts do not account for every function and residual exactly once"
        )

    for entity, function in function_by_entity.items():
        evidence_states = set(
            _state_values(
                function.get("evidenceStates"),
                f"function {entity} evidenceStates",
            )
        )
        if "MAINTAINER_GHIDRA_SEMANTIC_PROMOTED" not in evidence_states:
            continue
        contract = contract_by_entity[entity]
        evidence_refs = _state_values(
            contract.get("evidenceRefs"),
            f"contract {contract['contractId']} evidenceRefs",
        )
        if (
            function.get("nativeRegistryStatus")
            != "FUNCTION_PROMOTED_LIVE_SEMANTIC"
            or function.get("nameClass") != "NAMED"
            or function.get("understoodTier") != "U2_ADDRESS_CITED"
            or not str(function.get("currentName", "")).strip()
            or contract.get("currentName") != function.get("currentName")
            or len(evidence_refs) < 2
            or any(
                re.search(r"#sha256=[0-9a-fA-F]{64}$", value) is None
                for value in evidence_refs
            )
        ):
            raise CampaignError(
                f"campaign semantic Ghidra promotion is malformed: {entity}"
            )

    for question in questions:
        child_generation = _integer(question.get("generation"), -1)
        if child_generation < 0:
            raise CampaignError(
                f"campaign question has an invalid generation: {question['questionId']}"
            )
        for parent_id in _state_values(
            question.get("parentQuestionId"),
            f"question {question['questionId']} parentQuestionId",
        ):
            parent = question_by_id.get(parent_id)
            if parent is None:
                raise CampaignError(
                    f"campaign question has a missing parent: {question['questionId']}"
                )
            partition_cross_entity = bool(
                partition_context is not None
                and parent_id == ATOMIC14_OLD_QUESTION
                and question.get("questionId")
                in partition_context["successorQuestionIds"]
            )
            if (
                parent.get("entityKey") != question.get("entityKey")
                and not partition_cross_entity
            ):
                raise CampaignError(
                    f"campaign question parent crosses entities: {question['questionId']}"
                )
            if _integer(parent.get("generation"), -1) >= child_generation:
                raise CampaignError(
                    f"campaign question lineage is cyclic/non-monotone: {question['questionId']}"
                )

    for contract in contracts:
        entity = contract["entityKey"]
        expected_kind = "FUNCTION" if entity in function_by_entity else "TEXT_RESIDUAL"
        if contract.get("entityKind") != expected_kind:
            raise CampaignError(
                f"campaign contract entity kind disagrees with its ledger: {contract['contractId']}"
            )
        for question_id in _state_values(
            contract.get("questionIds"),
            f"contract {contract['contractId']} questionIds",
        ):
            question = question_by_id.get(question_id)
            if question is None:
                raise CampaignError(
                    f"campaign contract references a missing question: {contract['contractId']}"
                )
            if question.get("entityKey") != entity:
                raise CampaignError(
                    f"campaign contract question crosses entities: {contract['contractId']}"
                )

    addressed_by: dict[str, str] = {}
    successor_by: dict[str, str] = {}
    for adjudication in adjudications:
        adjudication_id = str(adjudication.get("adjudicationId", ""))
        partition_adjudication = bool(
            partition_context is not None
            and adjudication_id == partition_context["adjudicationId"]
        )
        contract = (
            partition_context["retiredContract"]
            if partition_adjudication
            else contract_by_id.get(str(adjudication.get("baseContractId", "")))
        )
        if contract is None or adjudication.get("entityKey") != contract.get("entityKey"):
            raise CampaignError(
                f"campaign adjudication does not match its base contract: {adjudication_id}"
            )
        if adjudication.get("baseContractId") != contract.get("contractId"):
            raise CampaignError(
                f"campaign adjudication base-contract identity differs: {adjudication_id}"
            )
        verdict = str(adjudication.get("refuterVerdict", ""))
        if verdict not in {"SURVIVED", "REFUTED", "UNSCORED"}:
            raise CampaignError(
                f"campaign adjudication has an invalid verdict: {adjudication_id}"
            )
        semantic_promotion = _bool(adjudication.get("semanticPromotionApplied"))
        semantic_flag_valid = (
            verdict == "SURVIVED" and not semantic_promotion
            if partition_adjudication
            else semantic_promotion == (verdict == "SURVIVED")
        )
        if not semantic_flag_valid:
            raise CampaignError(
                f"campaign adjudication semantic-promotion flag disagrees with its verdict: {adjudication_id}"
            )
        if partition_adjudication and (
            adjudication.get("overlaySchema") != GHIDRA_PARTITION_ADVANCE_SCHEMA
            or adjudication.get("terminalState") != "TERMINAL_EXACT_PARTITION"
            or adjudication.get("overlayReadySha256")
            != partition_context["expectedEvidenceHashes"][1]
        ):
            raise CampaignError(
                f"campaign exact-partition adjudication boundary differs: {adjudication_id}"
            )
        if not re.fullmatch(
            r"[0-9a-fA-F]{64}", str(adjudication.get("overlayReadySha256", ""))
        ):
            raise CampaignError(
                f"campaign adjudication has an invalid overlay hash: {adjudication_id}"
            )
        evidence_hashes = _state_values(
            adjudication.get("refuterEvidenceSha256"),
            f"adjudication {adjudication_id} refuterEvidenceSha256",
        )
        if not evidence_hashes or any(
            not re.fullmatch(r"[0-9a-fA-F]{64}", value)
            for value in evidence_hashes
        ):
            raise CampaignError(
                f"campaign adjudication has invalid refuter evidence hashes: {adjudication_id}"
            )
        addressed = _state_values(
            adjudication.get("questionIdsAddressed"),
            f"adjudication {adjudication_id} questionIdsAddressed",
        )
        successors = _state_values(
            adjudication.get("successorQuestionIds"),
            f"adjudication {adjudication_id} successorQuestionIds",
        )
        if partition_adjudication and (
            set(addressed) != {ATOMIC14_OLD_QUESTION}
            or set(successors) != partition_context["successorQuestionIds"]
            or evidence_hashes != partition_context["expectedEvidenceHashes"]
        ):
            raise CampaignError(
                f"campaign exact-partition adjudication question set differs: {adjudication_id}"
            )
        if not addressed:
            raise CampaignError(
                f"campaign adjudication addresses no questions: {adjudication_id}"
            )
        linked = set(
            _state_values(
                contract.get("questionIds"),
                f"contract {contract['contractId']} questionIds",
            )
        )
        for question_id in addressed:
            question = question_by_id.get(question_id)
            if (
                question is None
                or question.get("entityKey") != contract.get("entityKey")
                or question_id not in linked
                or question.get("state") != f"CLOSED_{verdict}"
                or question.get("lastOutcome") != verdict
                or question_id in addressed_by
            ):
                raise CampaignError(
                    f"campaign adjudication does not own its addressed question: {adjudication_id}"
                )
            addressed_by[question_id] = adjudication_id
        for question_id in successors:
            question = question_by_id.get(question_id)
            partition_successor = bool(
                partition_adjudication
                and question_id in partition_context["successorQuestionIds"]
            )
            if (
                question is None
                or (
                    not partition_successor
                    and question.get("entityKey") != contract.get("entityKey")
                )
                or (not partition_successor and question_id not in linked)
                or (
                    question.get("state") != "OPEN"
                    and not str(question.get("state", "")).startswith("CLOSED_")
                )
                or question_id in successor_by
                or set(
                    _state_values(
                        question.get("parentQuestionId"),
                        f"question {question_id} parentQuestionId",
                    )
                )
                != set(addressed)
            ):
                raise CampaignError(
                    f"campaign adjudication does not own its successor question: {adjudication_id}"
                )
            successor_by[question_id] = adjudication_id

    if partition_context is not None and partition_context["adjudicationId"] not in {
        str(row.get("adjudicationId", "")) for row in adjudications
    }:
        raise CampaignError("campaign exact-partition adjudication is absent")

    for question in questions:
        if str(question.get("state", "")).startswith("CLOSED_") and (
            question["questionId"] not in addressed_by
        ):
            raise CampaignError(
                f"closed campaign question lacks adjudication provenance: {question['questionId']}"
            )
        if (
            question["questionId"] in successor_by
            and str(question.get("state", "")).startswith("CLOSED_")
            and question["questionId"] not in addressed_by
        ):
            raise CampaignError(
                f"closed campaign successor lacks a later adjudication: {question['questionId']}"
            )

    specimen_sha = str(
        receipt.get("sourceSnapshot", {}).get("specimen", {}).get("sha256", "")
    ).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", specimen_sha):
        raise CampaignError("campaign READY lacks a valid specimen identity")
    image_base_text = str(
        receipt.get("sourceSnapshot", {})
        .get("parityGraph", {})
        .get("program", {})
        .get("imageBase", "")
    )
    image_base = (
        int(image_base_text, 16)
        if re.fullmatch(r"0x[0-9a-f]{8}", image_base_text)
        else None
    )
    supersession_by_new: dict[str, set[str]] = {}
    supersessions_by_old: dict[str, list[dict[str, object]]] = {}
    partition_intervals: dict[str, list[tuple[int, int, str, str]]] = {}
    seen_ids: set[str] = set()
    for supersession in supersessions:
        supersession_id = str(supersession.get("supersessionId", ""))
        old = str(supersession.get("oldEntityKey", ""))
        new = str(supersession.get("newEntityKey", ""))
        expected_id = "S-" + _sha256_text(old + "|" + new)[:16]
        legacy_old_match = re.fullmatch(
            r"CODE_CANDIDATE:([0-9a-fA-F]{64}):VA=(0[xX][0-9a-fA-F]+)",
            old,
        )
        residual_old_match = re.fullmatch(
            r"TEXT_RESIDUAL:([0-9a-fA-F]{64}):(0[xX][0-9a-fA-F]+)-(0[xX][0-9a-fA-F]+)",
            old,
        )
        new_match = re.fullmatch(
            r"CODE:([0-9a-fA-F]{64}):VA=(0[xX][0-9a-fA-F]+):RANGES=([0-9a-fA-F]{64})",
            new,
        )
        residual_new_match = re.fullmatch(
            r"TEXT_RESIDUAL:([0-9a-fA-F]{64}):(0[xX][0-9a-fA-F]+)-(0[xX][0-9a-fA-F]+)",
            new,
        )
        kind = supersession.get("kind")
        kind_valid = False
        partition_interval: tuple[int, int, str, str] | None = None
        if kind == GHIDRA_ADVANCE_KIND:
            kind_valid = (
                legacy_old_match is not None
                and residual_old_match is None
                and new_match is not None
                and legacy_old_match.group(1).lower() == specimen_sha
                and new_match.group(1).lower() == specimen_sha
                and int(legacy_old_match.group(2), 16) == int(new_match.group(2), 16)
            )
        elif kind == GHIDRA_RESIDUAL_ADVANCE_KIND:
            function = function_by_entity.get(new)
            residual_start = (
                int(residual_old_match.group(2), 16)
                if residual_old_match is not None
                else -1
            )
            residual_end = (
                int(residual_old_match.group(3), 16)
                if residual_old_match is not None
                else -1
            )
            start_rva = residual_start - image_base if image_base is not None else -1
            end_rva = residual_end - image_base if image_base is not None else -1
            expected_range_digest = (
                hashlib.sha256(
                    json.dumps(
                        [(start_rva, end_rva)],
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
                if 0 <= start_rva < end_rva
                else ""
            )
            canonical_old = (
                f"TEXT_RESIDUAL:{specimen_sha}:"
                f"0x{residual_start:08X}-0x{residual_end:08X}"
            )
            canonical_new = (
                f"CODE:{specimen_sha}:VA=0x{residual_start:08x}:"
                f"RANGES={expected_range_digest}"
            )
            kind_valid = (
                residual_old_match is not None
                and legacy_old_match is None
                and new_match is not None
                and function is not None
                and image_base is not None
                and residual_start >= image_base
                and residual_end > residual_start
                and old == canonical_old
                and new == canonical_new
                and old not in entity_keys
                and residual_old_match.group(1).lower() == specimen_sha
                and new_match.group(1).lower() == specimen_sha
                and residual_start == int(new_match.group(2), 16)
                and new_match.group(3) == expected_range_digest
                and function.get("entryVa") == f"0x{residual_start:08x}"
                and function.get("entryRva") == f"0x{start_rva:08x}"
                and function.get("bodyRangesRva")
                == f"0x{start_rva:x}-0x{end_rva:x}"
                and _integer(function.get("bodyBytes"), -1)
                == residual_end - residual_start
                and function.get("bodyRangeSetSha256") == expected_range_digest
                and "MAINTAINER_GHIDRA_BOUNDARY_PROMOTED"
                in _state_values(
                    function.get("evidenceStates"),
                    f"function {new} evidenceStates",
                )
            )
        elif kind == GHIDRA_PARTITION_ADVANCE_KIND:
            function = function_by_entity.get(new)
            residual = residual_by_entity.get(new)
            contract = contract_by_entity.get(new)
            child_start = -1
            child_end = -1
            child_kind = ""
            if function is not None and image_base is not None:
                body_match = re.fullmatch(
                    r"0x([0-9a-fA-F]+)-0x([0-9a-fA-F]+)",
                    str(function.get("bodyRangesRva", "")),
                )
                if body_match is not None:
                    child_start = image_base + int(body_match.group(1), 16)
                    child_end = image_base + int(body_match.group(2), 16)
                    child_kind = "FUNCTION"
            elif residual is not None and residual_new_match is not None:
                child_start = int(residual_new_match.group(2), 16)
                child_end = int(residual_new_match.group(3), 16)
                child_kind = "PADDING"
            partition_interval = (child_start, child_end, new, child_kind)
            function_valid = bool(
                function is not None
                and residual is None
                and new_match is not None
                and child_kind == "FUNCTION"
                and new_match.group(1).lower() == specimen_sha
                and int(new_match.group(2), 16) == child_start
                and new_match.group(3).lower()
                == str(function.get("bodyRangeSetSha256", "")).lower()
                and function.get("entryVa") == f"0x{child_start:08x}"
                and _integer(function.get("bodyBytes"), -1) == child_end - child_start
                and re.fullmatch(r"FUN_[0-9a-fA-F]{8}", str(function.get("currentName", "")))
                and function.get("nameClass") == "FUN"
                and function.get("semanticGrade") == "OPAQUE"
                and contract is not None
                and contract.get("contractState") == "OPEN"
                and contract.get("semanticGrade") == "C0_OPAQUE"
                and contract.get("rebuildState") == "NOT_READY"
                and "MAINTAINER_GHIDRA_BOUNDARY_PROMOTED"
                in _state_values(
                    function.get("evidenceStates"),
                    f"function {new} evidenceStates",
                )
            )
            padding_valid = bool(
                residual is not None
                and function is None
                and residual_new_match is not None
                and child_kind == "PADDING"
                and residual_new_match.group(1).lower() == specimen_sha
                and residual.get("startVa") == f"0x{child_start:08x}"
                and residual.get("endVa") == f"0x{child_end:08x}"
                and _integer(residual.get("bytes"), -1) == child_end - child_start
                and residual.get("classification") == "PADDING"
                and residual.get("classificationVerdict") == "FORMAL_STATIC_PROOF_SURVIVED"
                and residual.get("terminalState") == "TERMINAL_PADDING"
                and residual.get("campaignState") == "TERMINAL_PADDING"
                and not residual.get("questionIds")
                and contract is not None
                and contract.get("contractState") == "TERMINAL_PADDING"
                and contract.get("semanticGrade") == "C0_OPAQUE"
                and contract.get("refuterVerdict") == "SURVIVED"
                and not contract.get("questionIds")
                and contract.get("rebuildState") == "NOT_READY"
            )
            kind_valid = bool(
                partition_context is not None
                and old == ATOMIC14_OLD_RESIDUAL
                and residual_old_match is not None
                and residual_old_match.group(1).lower() == specimen_sha
                and int(residual_old_match.group(2), 16) == ATOMIC14_START_VA
                and int(residual_old_match.group(3), 16) == ATOMIC14_END_VA
                and old not in entity_keys
                and new in partition_context["successorEntityKeys"]
                and ATOMIC14_START_VA <= child_start < child_end <= ATOMIC14_END_VA
                and (function_valid or padding_valid)
            )
        evidence_refs = _state_values(
            supersession.get("evidenceRefs"),
            f"supersession {supersession_id} evidenceRefs",
        )
        if (
            not supersession_id
            or supersession_id in seen_ids
            or supersession_id != expected_id
            or old == new
            or new not in contract_by_entity
            or not kind_valid
            or supersession.get("verdict") != "SURVIVED"
            or not evidence_refs
            or any(
                re.search(r"#sha256=[0-9a-fA-F]{64}$", value) is None
                for value in evidence_refs
            )
            or (
                kind == GHIDRA_PARTITION_ADVANCE_KIND
                and partition_context is not None
                and evidence_refs != partition_context["expectedEvidenceRefs"]
            )
            or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T[^\s]+",
                str(supersession.get("measuredAtUtc", "")),
            )
        ):
            raise CampaignError(
                f"campaign contains an invalid supersession: {supersession_id}"
            )
        seen_ids.add(supersession_id)
        supersessions_by_old.setdefault(old, []).append(supersession)
        if partition_interval is not None:
            partition_intervals.setdefault(old, []).append(partition_interval)
        supersession_by_new.setdefault(new, set()).add(old)

    for old, grouped in supersessions_by_old.items():
        kinds = {str(row.get("kind", "")) for row in grouped}
        if len(grouped) > 1 and kinds != {GHIDRA_PARTITION_ADVANCE_KIND}:
            raise CampaignError(
                f"campaign supersessions repeat an old entity outside exact partition: {old}"
            )

    if partition_context is not None:
        grouped = partition_intervals.get(ATOMIC14_OLD_RESIDUAL, [])
        ordered = sorted(grouped, key=lambda row: (row[0], row[1], row[2]))
        partition_questions = [
            question_by_id.get(question_id)
            for question_id in partition_context["successorQuestionIds"]
        ]
        expected_region = _region_key(
            specimen_sha, f"0x{ATOMIC14_START_VA + 4:08x}", f"0x{ATOMIC14_END_VA - 10:08x}"
        )
        function_children = {row[2] for row in ordered if row[3] == "FUNCTION"}
        function_question_entities = {
            str(row.get("entityKey", ""))
            for row in partition_questions
            if isinstance(row, dict) and row.get("questionType") == "DARK_FUNCTION_CONTRACT"
        }
        region_questions = [
            row
            for row in partition_questions
            if isinstance(row, dict) and row.get("questionType") == "DARK_REGION_REACHABILITY"
        ]
        if (
            len(grouped) != ATOMIC14_FUNCTION_COUNT + ATOMIC14_PADDING_COUNT
            or len(partition_intervals) != 1
            or not ordered
            or ordered[0][0] != ATOMIC14_START_VA
            or ordered[-1][1] != ATOMIC14_END_VA
            or any(left[1] != right[0] for left, right in zip(ordered, ordered[1:]))
            or len({row[2] for row in ordered}) != len(ordered)
            or {row[2] for row in ordered} != partition_context["successorEntityKeys"]
            or sum(row[1] - row[0] for row in ordered if row[3] == "FUNCTION")
            != ATOMIC14_FUNCTION_BYTES
            or sum(row[1] - row[0] for row in ordered if row[3] == "PADDING")
            != ATOMIC14_PADDING_BYTES
            or sum(1 for row in ordered if row[3] == "FUNCTION")
            != ATOMIC14_FUNCTION_COUNT
            or sum(1 for row in ordered if row[3] == "PADDING")
            != ATOMIC14_PADDING_COUNT
            or any(row is None for row in partition_questions)
            or function_question_entities != function_children
            or len(region_questions) != 1
            or region_questions[0].get("entityKey") != expected_region
        ):
            raise CampaignError("campaign exact-partition successors do not exactly cover the parent")
    elif partition_intervals:
        raise CampaignError("campaign contains exact-partition supersessions without that advance")

    for contract in contracts:
        mirrored = set(
            _state_values(
                contract.get("supersedesEntityKeys"),
                f"contract {contract['contractId']} supersedesEntityKeys",
            )
        )
        if mirrored != supersession_by_new.get(contract["entityKey"], set()):
            raise CampaignError(
                f"campaign contract supersession mirror disagrees with the ledger: {contract['contractId']}"
            )


def _verify_legacy_campaign_carry(root: Path) -> dict:
    """Verify the one reviewed pre-reducer campaign allowed to seed v5 lineage.

    This is deliberately not a generic v4 verifier. The path, READY bytes, every
    ledger output, and the specimen identity are all frozen. Any other v4
    campaign must be migrated explicitly rather than inheriting this exception.
    """

    resolved = root.resolve()
    expected_root = LEGACY_CAMPAIGN_CARRY_ROOT.resolve()
    if resolved != expected_root:
        raise CampaignError(
            "legacy campaign carry is not the one exact reviewed bridge"
        )
    ready_path = resolved / "campaign.ready.json"
    if (
        not ready_path.is_file()
        or coverage.sha256_of(ready_path) != LEGACY_CAMPAIGN_CARRY_READY_SHA256
    ):
        raise CampaignError("legacy campaign carry READY is absent or changed")
    try:
        receipt = json.loads(ready_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot read legacy campaign carry READY: {exc}") from exc
    specimen_sha = (
        receipt.get("sourceSnapshot", {}).get("specimen", {}).get("sha256", "")
    )
    if (
        receipt.get("schema") != LEGACY_CAMPAIGN_SCHEMA
        or _integer(receipt.get("generation"), -1) != 3
        or specimen_sha.lower() != LEGACY_CAMPAIGN_CARRY_SPECIMEN_SHA256
    ):
        raise CampaignError("legacy campaign carry identity is unsupported")
    for name in OUTPUTS:
        expected = receipt.get("outputs", {}).get(name)
        path = resolved / name
        if not isinstance(expected, dict) or not path.is_file():
            raise CampaignError(f"legacy campaign carry output is missing: {name}")
        actual = coverage.file_stamp(path)
        if (
            actual["bytes"] != expected.get("bytes")
            or actual["sha256"] != expected.get("sha256")
        ):
            raise CampaignError(f"legacy campaign carry output has changed: {name}")
    rows = _campaign_rows_from_root(resolved)
    counts = {name: len(rows[name]) for name in rows}
    if counts != receipt.get("counts"):
        raise CampaignError("legacy campaign carry row counts disagree with READY")
    verified = dict(receipt)
    verified["_carryBridge"] = "EXACT_REVIEWED_LEGACY_V4"
    return verified


def _verify_frozen_v5_campaign_carry(root: Path) -> dict:
    """Verify the one exact v5 generation allowed across the reducer-v2 cut.

    The prior reducer cannot be treated as the current verifier after this
    module changes.  This bridge therefore accepts only the independently
    audited carried-r3 root, READY bytes, specimen, generation, output hashes,
    and row counts.  It is a migration fixture, not a generic old-v5 verifier.
    """

    resolved = root.resolve()
    if resolved != FROZEN_V5_CAMPAIGN_CARRY_ROOT.resolve():
        raise CampaignError("frozen v5 carry is not the one exact reviewed bridge")
    ready_path = resolved / "campaign.ready.json"
    if (
        not ready_path.is_file()
        or coverage.sha256_of(ready_path) != FROZEN_V5_CAMPAIGN_CARRY_READY_SHA256
    ):
        raise CampaignError("frozen v5 carry READY is absent or changed")
    try:
        receipt = json.loads(ready_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot read frozen v5 carry READY: {exc}") from exc
    specimen_sha = (
        receipt.get("sourceSnapshot", {}).get("specimen", {}).get("sha256", "")
    )
    if (
        receipt.get("schema") != SCHEMA
        or _integer(receipt.get("generation"), -1)
        != FROZEN_V5_CAMPAIGN_CARRY_GENERATION
        or specimen_sha.lower() != FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256
    ):
        raise CampaignError("frozen v5 carry identity is unsupported")
    reducer = _validate_reducer_snapshot(resolved, receipt)
    if reducer.get("id") != FROZEN_V5_CAMPAIGN_CARRY_REDUCER_ID:
        raise CampaignError("frozen v5 carry reducer identity is unsupported")
    for name in OUTPUTS:
        expected = receipt.get("outputs", {}).get(name)
        path = resolved / name
        if not isinstance(expected, dict) or not path.is_file():
            raise CampaignError(f"frozen v5 carry output is missing: {name}")
        actual = coverage.file_stamp(path)
        if (
            actual["bytes"] != expected.get("bytes")
            or actual["sha256"] != expected.get("sha256")
        ):
            raise CampaignError(f"frozen v5 carry output has changed: {name}")
    rows = _campaign_rows_from_root(resolved)
    counts = {name: len(rows[name]) for name in rows}
    if counts != receipt.get("counts"):
        raise CampaignError("frozen v5 carry row counts disagree with READY")
    _validate_campaign_relations(rows, receipt)
    verified = dict(receipt)
    verified["_carryBridge"] = "EXACT_AUDITED_FROZEN_V5_R3"
    return verified


def _verify_campaign_carry_source(root: Path) -> dict:
    try:
        raw = json.loads((root / "campaign.ready.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot read campaign carry source: {exc}") from exc
    if (
        raw.get("schema") == SCHEMA
        and root.resolve() == FROZEN_V5_CAMPAIGN_CARRY_ROOT.resolve()
    ):
        return _verify_frozen_v5_campaign_carry(root)
    if raw.get("schema") == SCHEMA:
        return verify(root)
    if raw.get("schema") == LEGACY_CAMPAIGN_SCHEMA:
        return _verify_legacy_campaign_carry(root)
    raise CampaignError(
        f"unsupported campaign carry source schema: {raw.get('schema')!r}"
    )


def _verify_atomic14_parent_campaign(root: Path) -> dict:
    """Verify the exact Generation 7 migration parent with its own frozen reducer."""
    ready_path = root / "campaign.ready.json"
    if not ready_path.is_file() or coverage.sha256_of(ready_path) != ATOMIC14_PARENT_READY_SHA256:
        raise CampaignError("Atomic14 parent campaign READY is absent or changed")
    try:
        receipt = json.loads(ready_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot read Atomic14 parent campaign: {exc}") from exc
    manifest = _validate_reducer_snapshot(root.resolve(), receipt)
    frozen_entry = root.resolve() / str(manifest.get("entry", ""))
    if not frozen_entry.is_file():
        raise CampaignError("Atomic14 parent frozen reducer entry is absent")
    environment = os.environ.copy()
    environment["BEA_REPO_ROOT"] = str(REPO_ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(frozen_entry),
                "verify",
                "--campaign",
                str(root.resolve()),
            ],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CampaignError("Atomic14 parent frozen verifier timed out") from exc
    if completed.returncode != 0 or "CAMPAIGN_VERIFIED" not in completed.stdout:
        raise CampaignError(
            "Atomic14 parent campaign failed its frozen verifier: "
            f"exit={completed.returncode} stderr={completed.stderr.strip()!r}"
        )
    rows = _campaign_rows_from_root(root)
    if {name: len(value) for name, value in rows.items()} != receipt.get("counts"):
        raise CampaignError("Atomic14 parent campaign rows disagree with READY")
    _validate_campaign_relations(rows, receipt)
    verified = dict(receipt)
    verified["_carryBridge"] = "EXACT_FROZEN_GENERATION7_REPLAY"
    return verified


def _verify_target_lock_semantic_parent_campaign(root: Path) -> dict:
    """Verify exact Generation 8 with its own frozen reducer."""

    resolved = root.resolve()
    expected_root = (REPO_ROOT / TARGET_LOCK_SEMANTIC_PARENT_RELATIVE).resolve()
    if resolved != expected_root:
        raise CampaignError(
            "target-lock semantic parent is not the exact reviewed Generation 8"
        )
    ready_path = resolved / "campaign.ready.json"
    if (
        not ready_path.is_file()
        or coverage.sha256_of(ready_path)
        != TARGET_LOCK_SEMANTIC_PARENT_READY_SHA256
    ):
        raise CampaignError("target-lock semantic parent READY is absent or changed")
    try:
        receipt = json.loads(ready_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(
            f"cannot read target-lock semantic parent campaign: {exc}"
        ) from exc
    specimen_sha = (
        receipt.get("sourceSnapshot", {}).get("specimen", {}).get("sha256", "")
    )
    manifest = _validate_reducer_snapshot(resolved, receipt)
    if (
        receipt.get("schema") != SCHEMA
        or _integer(receipt.get("generation"), -1) != 8
        or specimen_sha.lower()
        != "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
        or receipt.get("counts") != TARGET_LOCK_SEMANTIC_PARENT_COUNTS
        or manifest.get("id") != TARGET_LOCK_SEMANTIC_PARENT_REDUCER_ID
    ):
        raise CampaignError("target-lock semantic parent identity is unsupported")
    frozen_entry = resolved / str(manifest.get("entry", ""))
    if not frozen_entry.is_file():
        raise CampaignError("target-lock semantic parent frozen reducer is absent")
    environment = os.environ.copy()
    environment["BEA_REPO_ROOT"] = str(REPO_ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(frozen_entry),
                "verify",
                "--campaign",
                str(resolved),
            ],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CampaignError(
            "target-lock semantic parent frozen verifier timed out"
        ) from exc
    if completed.returncode != 0 or "CAMPAIGN_VERIFIED" not in completed.stdout:
        raise CampaignError(
            "target-lock semantic parent failed its frozen verifier: "
            f"exit={completed.returncode} stderr={completed.stderr.strip()!r}"
        )
    rows = _campaign_rows_from_root(resolved)
    if {name: len(value) for name, value in rows.items()} != receipt.get("counts"):
        raise CampaignError("target-lock semantic parent rows disagree with READY")
    _validate_campaign_relations(rows, receipt)
    verified = dict(receipt)
    verified["_carryBridge"] = "EXACT_FROZEN_GENERATION8_REPLAY"
    return verified


def _verify_ttd_call_context_parent_campaign(root: Path) -> dict:
    """Verify the exact finalized Generation 9 parent with its frozen reducer."""

    resolved = root.resolve()
    expected_root = (REPO_ROOT / TTD_CALL_CONTEXT_PARENT_RELATIVE).resolve()
    if resolved != expected_root:
        raise CampaignError(
            "TTD call-context parent is not the exact finalized Generation 9"
        )
    ready_path = resolved / "campaign.ready.json"
    if (
        not ready_path.is_file()
        or coverage.sha256_of(ready_path) != TTD_CALL_CONTEXT_PARENT_READY_SHA256
    ):
        raise CampaignError("TTD call-context parent READY is absent or changed")
    receipt = _runtime_json(ready_path, "TTD call-context parent campaign")
    reducer = _validate_reducer_snapshot(resolved, receipt)
    specimen_sha = str(
        receipt.get("sourceSnapshot", {}).get("specimen", {}).get("sha256", "")
    ).lower()
    if (
        receipt.get("schema") != SCHEMA
        or _integer(receipt.get("generation"), -1) != 9
        or specimen_sha
        != "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
        or receipt.get("counts") != TTD_CALL_CONTEXT_PARENT_COUNTS
        or reducer.get("id") != TTD_CALL_CONTEXT_PARENT_REDUCER_ID
    ):
        raise CampaignError("TTD call-context parent identity is unsupported")
    frozen_entry = resolved / str(reducer.get("entry", ""))
    if not frozen_entry.is_file():
        raise CampaignError("TTD call-context parent frozen reducer is absent")
    environment = os.environ.copy()
    environment["BEA_REPO_ROOT"] = str(REPO_ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(frozen_entry),
                "verify",
                "--campaign",
                str(resolved),
            ],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=240,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CampaignError("TTD call-context parent frozen verifier timed out") from exc
    if completed.returncode != 0 or "CAMPAIGN_VERIFIED" not in completed.stdout:
        raise CampaignError(
            "TTD call-context parent failed its frozen verifier: "
            f"exit={completed.returncode} stderr={completed.stderr.strip()!r}"
        )
    rows = _campaign_rows_from_root(resolved)
    if {name: len(value) for name, value in rows.items()} != receipt.get("counts"):
        raise CampaignError("TTD call-context parent rows disagree with READY")
    _validate_campaign_relations(rows, receipt)
    verified = dict(receipt)
    verified["_carryBridge"] = "EXACT_FROZEN_GENERATION9_REPLAY"
    return verified


def _question_has_progress(row: dict[str, str]) -> bool:
    return (
        row.get("state") != "OPEN"
        or _integer(row.get("attemptCount"), 0) > 0
        or bool(row.get("parentQuestionId"))
        or row.get("lastOutcome") not in ("", "UNSCORED")
    )


def _contract_has_progress(row: dict[str, str]) -> bool:
    return (
        row.get("contractState") not in ("OPEN", "OPEN_CLASSIFICATION")
        or row.get("semanticGrade") != "C0_OPAQUE"
        or row.get("authorVerdict") not in ("", "UNSCORED")
        or row.get("runtimeVerdict")
        not in ("", "UNSCORED", "EXECUTED_BYTES_MEASURED")
        or row.get("refuterVerdict") not in ("", "UNSCORED")
        or row.get("evidenceRefs") not in ("", "ledger-unmapped.tsv")
        or row.get("rebuildState") != "NOT_READY"
        or row.get("rebuildOwner") != "UNASSIGNED"
        or row.get("rebuildImplementation") != "UNMAPPED"
        or row.get("parityTests") != "UNMAPPED"
        or bool(row.get("supersedesEntityKeys"))
    )


def _function_has_progress(row: dict[str, str]) -> bool:
    evidence = set(filter(None, row.get("evidenceStates", "").split(";")))
    return (
        row.get("resolutionState") not in ("OPEN_JOIN", "UNKNOWN_WITH_FALSIFIER")
        or row.get("semanticGrade") != "OPAQUE"
        or row.get("campaignState") not in ("OPEN_EXECUTED", "OPEN_DARK")
        or row.get("nativeRegistryStatus") == "FUNCTION_PROMOTED_LIVE_BOUNDARY_ONLY"
        or bool(
            evidence
            & {
                "RUNTIME_CONTRACT_REFUTER_SURVIVED",
                "MAINTAINER_GHIDRA_BOUNDARY_PROMOTED",
                "MAINTAINER_GHIDRA_SEMANTIC_PROMOTED",
            }
        )
    )


def _residual_has_progress(row: dict[str, str]) -> bool:
    return (
        row.get("campaignState")
        not in ("OPEN_EXECUTED_RESIDUAL", "OPEN_DARK_RESIDUAL")
        or row.get("classification") not in ("AMBIGUOUS", "CODE_CANDIDATE")
        or row.get("classificationVerdict")
        not in ("", "UNSCORED", "MEASURED_EXECUTION")
        or row.get("terminalState")
        not in ("", "OPEN_CLASSIFICATION", "OPEN_CODE_BOUNDARY")
    )


def _union_semicolon(left: str, right: str) -> str:
    return ";".join(
        dict.fromkeys(value for value in (left + ";" + right).split(";") if value)
    )


def _merge_reseed_carry(
    fresh: dict[str, list[dict]],
    carry_root: Path,
) -> dict[str, object]:
    """Overlay only verified progress onto a freshly derived structural frontier."""

    carried = _campaign_rows_from_root(carry_root)
    report: dict[str, object] = {
        "matchedQuestions": 0,
        "successorQuestions": 0,
        "functionRows": 0,
        "residualRows": 0,
        "contractRows": 0,
        "adjudications": 0,
        "supersessions": 0,
        "leverStates": 0,
        "staleQuestions": 0,
        "staleFunctions": 0,
        "staleResiduals": 0,
        "staleContracts": 0,
        "staleAdjudications": 0,
        "staleSupersessions": 0,
    }

    function_by_entity = {row["entityKey"]: row for row in fresh["functions"]}
    residual_by_entity = {row["entityKey"]: row for row in fresh["residuals"]}
    contract_by_id = {row["contractId"]: row for row in fresh["contracts"]}
    contract_entities = {row["entityKey"] for row in fresh["contracts"]}
    question_by_id = {row["questionId"]: row for row in fresh["questions"]}
    adjudicated_entities = {
        row.get("entityKey", "") for row in carried["adjudications"]
    }
    superseded_new_entities = {
        row.get("newEntityKey", "") for row in carried["supersessions"]
    }
    semantic_promoted_entities = {
        row.get("entityKey", "")
        for row in carried["functions"]
        if "MAINTAINER_GHIDRA_SEMANTIC_PROMOTED"
        in set(filter(None, row.get("evidenceStates", "").split(";")))
    }
    progressed_entities = (
        adjudicated_entities | superseded_new_entities | semantic_promoted_entities
    )

    question_shape = (
        "questionType",
        "entityKey",
        "recommendedInstrument",
        "question",
        "cheapestFalsifier",
    )
    question_progress = (
        "state",
        "currentOwner",
        "generation",
        "attemptCount",
        "parentQuestionId",
        "lastOutcome",
        "lastMeasurementDate",
    )
    for prior in carried["questions"]:
        if not _question_has_progress(prior):
            continue
        current = question_by_id.get(prior["questionId"])
        if current is not None:
            if any(current.get(field) != prior.get(field) for field in question_shape):
                raise CampaignError(
                    "campaign carry would close a changed question shape: "
                    f"{prior['questionId']}"
                )
            for field in question_progress:
                current[field] = prior.get(field, "")
            report["matchedQuestions"] = int(report["matchedQuestions"]) + 1
            continue
        if prior.get("entityKey") not in contract_entities:
            report["staleQuestions"] = int(report["staleQuestions"]) + 1
            continue
        copied = {field: prior.get(field, "") for field in QUESTION_COLUMNS}
        fresh["questions"].append(copied)
        question_by_id[copied["questionId"]] = copied
        report["successorQuestions"] = int(report["successorQuestions"]) + 1

    all_question_ids = set(question_by_id)
    for row in fresh["questions"]:
        parents = [
            value for value in row.get("parentQuestionId", "").split(";") if value
        ]
        if any(parent not in all_question_ids for parent in parents):
            raise CampaignError(
                f"campaign carry question has a missing parent: {row['questionId']}"
            )

    function_fields = (
        "nativeRegistryStatus",
        "resolutionState",
        "semanticGrade",
        "campaignState",
        "lever",
        "leverConfidence",
        "requiresElevation",
        "cheapestFalsifier",
        "lastMeasurementDate",
    )
    for prior in carried["functions"]:
        if (
            prior.get("entityKey") not in progressed_entities
            or not _function_has_progress(prior)
        ):
            continue
        current = function_by_entity.get(prior.get("entityKey"))
        if current is None:
            report["staleFunctions"] = int(report["staleFunctions"]) + 1
            continue
        if prior.get("entityKey") in semantic_promoted_entities and (
            current.get("currentName") != prior.get("currentName")
            or current.get("nameClass") != prior.get("nameClass")
            or current.get("understoodTier") != prior.get("understoodTier")
        ):
            raise CampaignError(
                "campaign carry semantic Ghidra identity differs from the fresh snapshot: "
                f"{prior['entityKey']}"
            )
        for field in function_fields:
            current[field] = prior.get(field, "")
        current["evidenceStates"] = _union_semicolon(
            current.get("evidenceStates", ""), prior.get("evidenceStates", "")
        )
        report["functionRows"] = int(report["functionRows"]) + 1

    residual_fields = (
        "classification",
        "classificationVerdict",
        "terminalState",
        "campaignState",
        "lever",
        "requiresElevation",
        "cheapestFalsifier",
        "lastMeasurementDate",
    )
    for prior in carried["residuals"]:
        if (
            prior.get("entityKey") not in adjudicated_entities
            or not _residual_has_progress(prior)
        ):
            continue
        current = residual_by_entity.get(prior.get("entityKey"))
        if current is None:
            report["staleResiduals"] = int(report["staleResiduals"]) + 1
            continue
        for field in residual_fields:
            current[field] = prior.get(field, "")
        current["questionIds"] = _union_semicolon(
            current.get("questionIds", ""), prior.get("questionIds", "")
        )
        report["residualRows"] = int(report["residualRows"]) + 1

    contract_progress_fields = (
        "contractState",
        "semanticGrade",
        "receiver",
        "inputs",
        "returns",
        "writes",
        "sideEffects",
        "preconditions",
        "failureModes",
        "authorVerdict",
        "runtimeVerdict",
        "refuterVerdict",
        "evidenceRefs",
        "cheapestFalsifier",
        "rebuildOwner",
        "rebuildImplementation",
        "parityTests",
        "rebuildState",
        "remainingUncertainty",
        "supersedesEntityKeys",
        "lastMeasurementDate",
    )
    for prior in carried["contracts"]:
        if (
            prior.get("entityKey") not in progressed_entities
            or not _contract_has_progress(prior)
        ):
            continue
        current = contract_by_id.get(prior.get("contractId"))
        if current is None or current.get("entityKey") != prior.get("entityKey"):
            report["staleContracts"] = int(report["staleContracts"]) + 1
            continue
        if prior.get("entityKey") in semantic_promoted_entities and (
            current.get("currentName") != prior.get("currentName")
        ):
            raise CampaignError(
                "campaign carry semantic contract name differs from the fresh snapshot: "
                f"{prior['entityKey']}"
            )
        prior_questions = [
            value for value in prior.get("questionIds", "").split(";") if value
        ]
        missing = [value for value in prior_questions if value not in all_question_ids]
        if missing:
            raise CampaignError(
                "campaign carry contract references missing questions: "
                + ", ".join(missing)
            )
        for field in contract_progress_fields:
            current[field] = prior.get(field, "")
        current["questionIds"] = _union_semicolon(
            current.get("questionIds", ""), prior.get("questionIds", "")
        )
        report["contractRows"] = int(report["contractRows"]) + 1

    adjudication_ids = {row["adjudicationId"] for row in fresh["adjudications"]}
    for prior in carried["adjudications"]:
        addressed = [
            value for value in prior.get("questionIdsAddressed", "").split(";") if value
        ]
        successors = [
            value for value in prior.get("successorQuestionIds", "").split(";") if value
        ]
        if (
            prior.get("baseContractId") not in contract_by_id
            or prior.get("entityKey") not in contract_entities
        ):
            report["staleAdjudications"] = int(report["staleAdjudications"]) + 1
            continue
        if any(value not in all_question_ids for value in addressed + successors):
            raise CampaignError(
                "campaign carry adjudication references a missing question: "
                f"{prior.get('adjudicationId', '')}"
            )
        if prior["adjudicationId"] in adjudication_ids:
            continue
        fresh["adjudications"].append(
            {field: prior.get(field, "") for field in ADJUDICATION_COLUMNS}
        )
        adjudication_ids.add(prior["adjudicationId"])
        report["adjudications"] = int(report["adjudications"]) + 1

    supersession_ids = {row["supersessionId"] for row in fresh["supersessions"]}
    for prior in carried["supersessions"]:
        if prior.get("newEntityKey") not in contract_entities:
            report["staleSupersessions"] = int(report["staleSupersessions"]) + 1
            continue
        if prior["supersessionId"] in supersession_ids:
            continue
        fresh["supersessions"].append(
            {field: prior.get(field, "") for field in SUPERSESSION_COLUMNS}
        )
        supersession_ids.add(prior["supersessionId"])
        report["supersessions"] = int(report["supersessions"]) + 1

    lever_by_key = {row["regionKey"]: row for row in fresh["levers"]}
    for prior in carried["levers"]:
        current = lever_by_key.get(prior.get("regionKey"))
        if current is not None and prior.get("state") not in ("", "UNTESTED"):
            current["state"] = prior["state"]
            report["leverStates"] = int(report["leverStates"]) + 1

    return report


def seed(
    snapshot: Path,
    out: Path,
    *,
    carry: Path | None = None,
    _self_check: bool = True,
    _verified_carry_receipt: dict | None = None,
) -> dict:
    if out.exists():
        raise CampaignError(f"refusing existing campaign destination: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    data = load_snapshot(snapshot)
    rows = build_campaign_rows(data)
    carry_receipt = None
    carry_ready = None
    carry_report = None
    if carry is not None:
        carry = carry.resolve()
        carry_receipt = (
            _verified_carry_receipt
            if _verified_carry_receipt is not None
            else _verify_campaign_carry_source(carry)
        )
        fresh_specimen = data["summary"]["inputs"]["specimen"]["sha256"].lower()
        carried_specimen = (
            carry_receipt.get("sourceSnapshot", {})
            .get("specimen", {})
            .get("sha256", "")
            .lower()
        )
        if fresh_specimen != carried_specimen:
            raise CampaignError(
                "campaign carry specimen differs from the fresh snapshot specimen"
            )
        carry_ready = coverage.file_stamp(carry / "campaign.ready.json")
        carry_report = _merge_reseed_carry(rows, carry)

    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        columns_by_output = {
            "campaign-functions.tsv": (FUNCTION_COLUMNS, rows["functions"]),
            "campaign-residuals.tsv": (RESIDUAL_COLUMNS, rows["residuals"]),
            "campaign-questions.tsv": (QUESTION_COLUMNS, rows["questions"]),
            "campaign-scenarios.tsv": (SCENARIO_COLUMNS, rows["scenarios"]),
            "campaign-levers.tsv": (LEVER_COLUMNS, rows["levers"]),
            "campaign-contracts.tsv": (CONTRACT_COLUMNS, rows["contracts"]),
            "campaign-adjudications.tsv": (
                ADJUDICATION_COLUMNS,
                rows["adjudications"],
            ),
            "campaign-supersessions.tsv": (
                SUPERSESSION_COLUMNS,
                rows["supersessions"],
            ),
        }
        for name, (columns, output_rows) in columns_by_output.items():
            _write_tsv(stage / name, columns, output_rows)
        reducer = _publish_reducer(stage)
        generation = (
            _integer(carry_receipt.get("generation"), -1) + 1
            if carry_receipt is not None
            else 0
        )
        receipt = {
            "schema": SCHEMA,
            "reducer": reducer,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "sourceSnapshot": {
                "path": str(snapshot.resolve()),
                "schema": data["summary"]["schema"],
                "coverageSetSha256": data["summary"]["denominators"]["coverageSetSha256"],
                "specimen": data["summary"]["inputs"]["specimen"],
                "parityGraph": data["summary"]["inputs"]["parityGraph"],
                "files": data["snapshotFiles"],
            },
            "counts": {name: len(rows[name]) for name in rows},
            "generation": generation,
            "parentCampaign": (
                {
                    "path": str(carry),
                    "ready": {**carry_ready, "path": "campaign.ready.json"},
                }
                if carry is not None
                else None
            ),
            "questionTypes": dict(Counter(row["questionType"] for row in rows["questions"])),
            "policies": [
                "Coverage is execution evidence, never naming authority.",
                "Every open semantic row remains OPAQUE until a reviewed contract earns a higher grade.",
                "UNSCORED and INSTRUMENT_NEEDED are valid accounting outcomes.",
                "This campaign never mutates Ghidra or the pristine specimen.",
                "Every function has one contract row; UNKNOWN and C0_OPAQUE are required until evidence closes them.",
                "Every nonterminal function and exact .text residual has at least one explicit open question.",
                "Rebuild mappings remain UNMAPPED until evidence and a focused parity test make them REBUILD_READY.",
            ],
            "outputs": {
                name: {**coverage.file_stamp(stage / name), "path": name}
                for name in OUTPUTS
            },
        }
        if carry_receipt is not None:
            receipt["advance"] = {
                "kind": CAMPAIGN_RESEED_KIND,
                "schema": CAMPAIGN_RESEED_SCHEMA,
                "parentSchema": carry_receipt.get("schema"),
                "legacyBridgeUsed": carry_receipt.get("schema") == LEGACY_CAMPAIGN_SCHEMA,
                "carryVerification": carry_receipt.get(
                    "_carryBridge", "CURRENT_REDUCER_REPLAY"
                ),
                "freshCoverageSetSha256": data["summary"]["denominators"][
                    "coverageSetSha256"
                ],
                "carried": carry_report,
            }
            receipt["policies"].extend(
                [
                    "Fresh snapshot rows remain structural truth; progress carries only across exact specimen-bound entity identities.",
                    "Verified closed questions, successor lineage, adjudications, and supersessions cannot silently reopen on reseed.",
                    "Function, residual, contract, question, adjudication, and supersession progress requires campaign provenance; stale identities are counted and skipped rather than transferred.",
                ]
            )
        (stage / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        if _self_check:
            verify(stage)
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _require_exact_promotion_advance_provenance(
    advance: dict,
    validated: dict,
) -> None:
    expected = {
        "preregistration": validated["preregistrationStamp"],
        "targets": validated["targetStamp"],
        "tool": validated["toolStamp"],
        "toolProvenance": validated["toolProvenance"],
        "evidenceSchema": validated["evidenceSchema"],
        "legacyBridgeUsed": validated["legacyBridgeUsed"],
        "backup": validated["backupOpenStamp"],
        "liveApply": {
            key: value
            for key, value in validated["liveApply"].items()
            if key != "tsvPath"
        },
        "liveReadback": {
            key: value
            for key, value in validated["liveReadback"].items()
            if key != "tsvPath"
        },
        "liveAfterFunctions": validated["afterFunctionsStamp"],
        "liveInventoryDiff": validated["liveDiffStamp"],
    }
    for key, expected_value in expected.items():
        actual_json = json.dumps(advance.get(key), sort_keys=True, separators=(",", ":"))
        expected_json = json.dumps(expected_value, sort_keys=True, separators=(",", ":"))
        if actual_json != expected_json:
            raise CampaignError(
                f"promotion advance {key} disagrees with the reproduced live evidence"
            )


def _resolve_repo_or_absolute(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise CampaignError(f"{label} has no path")
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def _require_file_stamp(path: Path, expected: object, label: str) -> dict:
    if not isinstance(expected, dict) or not path.is_file():
        raise CampaignError(f"{label} is missing from disk/receipt")
    actual = coverage.file_stamp(path)
    if (
        actual["bytes"] != expected.get("bytes")
        or actual["sha256"] != expected.get("sha256")
    ):
        raise CampaignError(f"{label} has changed")
    return actual


def _same_json(left: object, right: object) -> bool:
    return json.dumps(left, sort_keys=True, separators=(",", ":")) == json.dumps(
        right, sort_keys=True, separators=(",", ":")
    )


def _normalized_campaign_field(key: str, value: object) -> object:
    if key not in {"sourceSnapshot", "parentCampaign"} or not isinstance(value, dict):
        return value
    normalized = json.loads(json.dumps(value))

    def normalize_paths(node: object, *, recursive: bool) -> None:
        if isinstance(node, dict):
            raw = node.get("path")
            if isinstance(raw, str) and raw.strip():
                node["path"] = str(
                    _resolve_repo_or_absolute(raw, f"campaign {key}")
                )
            if recursive:
                for child in node.values():
                    normalize_paths(child, recursive=True)
        elif recursive and isinstance(node, list):
            for child in node:
                normalize_paths(child, recursive=True)

    normalize_paths(normalized, recursive=key == "sourceSnapshot")
    return normalized


def _compare_replayed_campaign(
    actual_root: Path,
    actual_receipt: dict,
    replay_root: Path,
) -> None:
    replay_receipt = _runtime_json(
        replay_root / "campaign.ready.json", "replayed campaign READY"
    )
    for name in OUTPUTS:
        actual_path = actual_root / name
        replay_path = replay_root / name
        if (
            actual_path.stat().st_size != replay_path.stat().st_size
            or coverage.sha256_of(actual_path) != coverage.sha256_of(replay_path)
        ):
            raise CampaignError(
                f"campaign output does not reproduce from its verified parent and advance: {name}"
            )
    for key in (
        "schema",
        "reducer",
        "generation",
        "parentCampaign",
        "sourceSnapshot",
        "advance",
        "counts",
        "questionTypes",
        "policies",
    ):
        if not _same_json(
            _normalized_campaign_field(key, actual_receipt.get(key)),
            _normalized_campaign_field(key, replay_receipt.get(key)),
        ):
            raise CampaignError(
                f"campaign {key} does not reproduce from its verified parent and advance"
            )
    for name in OUTPUTS:
        actual = actual_receipt.get("outputs", {}).get(name)
        replayed = replay_receipt.get("outputs", {}).get(name)
        for field in ("path", "bytes", "sha256"):
            if not isinstance(actual, dict) or actual.get(field) != replayed.get(field):
                raise CampaignError(
                    f"campaign output receipt does not reproduce for {name}.{field}"
                )


def _replay_campaign_generation(campaign: Path, receipt: dict) -> None:
    generation = _integer(receipt.get("generation"), -1)
    with tempfile.TemporaryDirectory(prefix="bea-campaign-replay-") as temporary:
        replay = Path(temporary) / "campaign"
        if generation == 0:
            if receipt.get("parentCampaign") is not None or receipt.get("advance") is not None:
                raise CampaignError("generation zero cannot declare a parent or advance")
            source = _runtime_mapping(
                receipt.get("sourceSnapshot"), "seed sourceSnapshot"
            )
            snapshot = _resolve_repo_or_absolute(
                source.get("path"), "seed sourceSnapshot"
            )
            seed(snapshot, replay, _self_check=False)
        elif generation > 0:
            parent = _runtime_mapping(
                receipt.get("parentCampaign"), "campaign parentCampaign"
            )
            parent_path = _resolve_repo_or_absolute(
                parent.get("path"), "campaign parentCampaign"
            )
            parent_ready = _runtime_mapping(
                parent.get("ready"), "campaign parentCampaign.ready"
            )
            _require_file_stamp(
                parent_path / "campaign.ready.json",
                parent_ready,
                "campaign parent READY",
            )
            advance = _runtime_mapping(receipt.get("advance"), "campaign advance")
            kind = advance.get("kind")
            if kind == CAMPAIGN_RESEED_KIND:
                parent_receipt = _verify_campaign_carry_source(parent_path)
            elif kind == GHIDRA_PARTITION_ADVANCE_KIND:
                parent_receipt = _verify_atomic14_parent_campaign(parent_path)
            elif kind == GHIDRA_SEMANTIC_ADVANCE_KIND:
                parent_receipt = _verify_target_lock_semantic_parent_campaign(
                    parent_path
                )
            elif kind == TTD_CALL_CONTEXT_ADVANCE_KIND:
                parent_receipt = _verify_ttd_call_context_parent_campaign(
                    parent_path
                )
            else:
                parent_receipt = verify(parent_path)
            if generation != _integer(parent_receipt.get("generation"), -1) + 1:
                raise CampaignError("campaign generation is not parent generation plus one")
            if kind == CAMPAIGN_RESEED_KIND:
                if advance.get("schema") != CAMPAIGN_RESEED_SCHEMA:
                    raise CampaignError("campaign reseed carry schema is unsupported")
                source = _runtime_mapping(
                    receipt.get("sourceSnapshot"), "reseed sourceSnapshot"
                )
                snapshot = _resolve_repo_or_absolute(
                    source.get("path"), "reseed sourceSnapshot"
                )
                seed(
                    snapshot,
                    replay,
                    carry=parent_path,
                    _self_check=False,
                    _verified_carry_receipt=parent_receipt,
                )
            elif kind == RUNTIME_ADVANCE_KIND:
                if advance.get("schema") != RUNTIME_ADVANCE_SCHEMA:
                    raise CampaignError("runtime campaign advance schema is unsupported")
                overlay_spec = _runtime_mapping(
                    advance.get("overlay"), "runtime advance overlay"
                )
                overlay_root = _resolve_repo_or_absolute(
                    overlay_spec.get("root"), "runtime advance overlay"
                )
                _require_file_stamp(
                    overlay_root / "runtime-contracts.ready.json",
                    overlay_spec.get("ready"),
                    "runtime advance overlay READY",
                )
                adjudication_spec = _runtime_mapping(
                    advance.get("adjudication"), "runtime advance adjudication"
                )
                adjudication_path = _resolve_repo_or_absolute(
                    adjudication_spec.get("path"), "runtime advance adjudication"
                )
                _require_file_stamp(
                    adjudication_path,
                    adjudication_spec,
                    "runtime advance adjudication",
                )
                advance_runtime_contract(
                    parent_path,
                    overlay_root,
                    adjudication_path,
                    replay,
                    _self_check=False,
                    _verified_parent_receipt=parent_receipt,
                )
            elif kind == GHIDRA_ADVANCE_KIND:
                evidence_spec = _runtime_mapping(
                    advance.get("evidence"), "Ghidra advance evidence"
                )
                evidence_path = _resolve_repo_or_absolute(
                    evidence_spec.get("path"), "Ghidra advance evidence"
                )
                _require_file_stamp(
                    evidence_path, evidence_spec, "Ghidra advance evidence"
                )
                advance_ghidra_promotion(
                    parent_path,
                    evidence_path,
                    replay,
                    _self_check=False,
                    _verified_parent_receipt=parent_receipt,
                )
            elif kind == GHIDRA_SEMANTIC_ADVANCE_KIND:
                if advance.get("schema") != GHIDRA_SEMANTIC_ADVANCE_SCHEMA:
                    raise CampaignError(
                        "Ghidra semantic campaign advance schema is unsupported"
                    )
                live_spec = _runtime_mapping(
                    advance.get("liveReady"), "Ghidra semantic advance live READY"
                )
                live_ready_path = _resolve_repo_or_absolute(
                    live_spec.get("path"), "Ghidra semantic advance live READY"
                )
                _require_file_stamp(
                    live_ready_path,
                    live_spec,
                    "Ghidra semantic advance live READY",
                )
                advance_ghidra_semantic_promotion(
                    parent_path,
                    live_ready_path,
                    replay,
                    _self_check=False,
                    _verified_parent_receipt=parent_receipt,
                )
            elif kind == GHIDRA_RESIDUAL_ADVANCE_KIND:
                if advance.get("schema") != GHIDRA_RESIDUAL_ADVANCE_SCHEMA:
                    raise CampaignError(
                        "Ghidra residual campaign advance schema is unsupported"
                    )
                evidence_spec = _runtime_mapping(
                    advance.get("evidence"), "Ghidra residual advance evidence"
                )
                evidence_path = _resolve_repo_or_absolute(
                    evidence_spec.get("path"), "Ghidra residual advance evidence"
                )
                _require_file_stamp(
                    evidence_path, evidence_spec, "Ghidra residual advance evidence"
                )
                lineage_spec = _runtime_mapping(
                    advance.get("lineage"), "Ghidra residual advance lineage"
                )
                lineage_root = _resolve_repo_or_absolute(
                    lineage_spec.get("root"), "Ghidra residual advance lineage root"
                )
                for field in ("ready", "owner", "rows"):
                    stamp = _runtime_mapping(
                        lineage_spec.get(field),
                        f"Ghidra residual advance lineage {field}",
                    )
                    relative = stamp.get("path")
                    if not isinstance(relative, str) or Path(relative).is_absolute():
                        raise CampaignError(
                            f"Ghidra residual advance lineage {field} path differs"
                        )
                    _require_file_stamp(
                        lineage_root / relative,
                        stamp,
                        f"Ghidra residual advance lineage {field}",
                    )
                advance_ghidra_residual_promotion(
                    parent_path,
                    evidence_path,
                    lineage_root,
                    replay,
                    _self_check=False,
                    _verified_parent_receipt=parent_receipt,
                )
            elif kind == GHIDRA_PARTITION_ADVANCE_KIND:
                if advance.get("schema") != GHIDRA_PARTITION_ADVANCE_SCHEMA:
                    raise CampaignError(
                        "Ghidra exact-partition campaign advance schema is unsupported"
                    )
                snapshot_spec = _runtime_mapping(
                    advance.get("snapshot"), "Ghidra exact-partition snapshot"
                )
                snapshot_root = _resolve_repo_or_absolute(
                    snapshot_spec.get("root"), "Ghidra exact-partition snapshot root"
                )
                snapshot_ready = _runtime_mapping(
                    snapshot_spec.get("ready"), "Ghidra exact-partition snapshot READY"
                )
                _require_file_stamp(
                    snapshot_root / "ledger.ready.json",
                    snapshot_ready,
                    "Ghidra exact-partition snapshot READY",
                )
                artifact_paths: dict[str, Path] = {}
                for field in (
                    "liveReady",
                    "formalReady",
                    "targets",
                    "padding",
                    "parityExport",
                ):
                    stamp = _runtime_mapping(
                        advance.get(field), f"Ghidra exact-partition {field}"
                    )
                    path = _resolve_repo_or_absolute(
                        stamp.get("path"), f"Ghidra exact-partition {field} path"
                    )
                    _require_file_stamp(path, stamp, f"Ghidra exact-partition {field}")
                    artifact_paths[field] = path
                advance_ghidra_residual_partition(
                    parent_path,
                    snapshot_root,
                    artifact_paths["liveReady"],
                    artifact_paths["formalReady"],
                    artifact_paths["targets"],
                    artifact_paths["padding"],
                    artifact_paths["parityExport"],
                    replay,
                    _self_check=False,
                    _verified_parent_receipt=parent_receipt,
                )
            elif kind == TTD_CALL_CONTEXT_ADVANCE_KIND:
                if advance.get("schema") != TTD_CALL_CONTEXT_ADVANCE_SCHEMA:
                    raise CampaignError(
                        "TTD call-context campaign advance schema is unsupported"
                    )
                evidence_spec = _runtime_mapping(
                    advance.get("evidence"), "TTD call-context advance evidence"
                )
                evidence_root = _resolve_repo_or_absolute(
                    evidence_spec.get("root"),
                    "TTD call-context advance evidence root",
                )
                advance_ttd_call_context_observation(
                    parent_path,
                    evidence_root,
                    replay,
                    _self_check=False,
                    _verified_parent_receipt=parent_receipt,
                )
            else:
                raise CampaignError(f"unsupported campaign advance kind: {kind!r}")
        else:
            raise CampaignError("campaign generation is missing or negative")
        _compare_replayed_campaign(campaign, receipt, replay)


def verify(campaign: Path, *, _replay_generation: bool = True) -> dict:
    receipt_path = campaign / "campaign.ready.json"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot read campaign READY receipt: {exc}") from exc
    if receipt.get("schema") != SCHEMA:
        raise CampaignError(f"unsupported campaign schema: {receipt.get('schema')!r}")
    _validate_reducer_bundle(campaign.resolve(), receipt)
    for name in OUTPUTS:
        path = campaign / name
        expected = receipt.get("outputs", {}).get(name)
        if not path.is_file() or not isinstance(expected, dict):
            raise CampaignError(f"campaign output missing from disk/receipt: {name}")
        actual = coverage.file_stamp(path)
        if actual["bytes"] != expected.get("bytes") or actual["sha256"] != expected.get("sha256"):
            raise CampaignError(f"campaign output disagrees with READY receipt: {name}")
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    questions = _read_tsv(campaign / "campaign-questions.tsv")
    scenarios = _read_tsv(campaign / "campaign-scenarios.tsv")
    levers = _read_tsv(campaign / "campaign-levers.tsv")
    contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    adjudications = _read_tsv(campaign / "campaign-adjudications.tsv")
    supersessions = _read_tsv(campaign / "campaign-supersessions.tsv")
    actual_counts = {
        "functions": len(functions),
        "residuals": len(residuals),
        "questions": len(questions),
        "scenarios": len(scenarios),
        "levers": len(levers),
        "contracts": len(contracts),
        "adjudications": len(adjudications),
        "supersessions": len(supersessions),
    }
    if actual_counts != receipt.get("counts"):
        raise CampaignError(
            f"campaign row counts disagree with READY receipt: {actual_counts} != {receipt.get('counts')}"
        )

    def require_unique(rows: list[dict[str, str]], column: str, label: str) -> set[str]:
        values = [row.get(column, "") for row in rows]
        if any(not value for value in values) or len(values) != len(set(values)):
            raise CampaignError(f"campaign {label} contains missing or duplicate {column} values")
        return set(values)

    function_entities = require_unique(functions, "entityKey", "functions")
    residual_entities = require_unique(residuals, "entityKey", "residuals")
    if function_entities & residual_entities:
        raise CampaignError("campaign function and residual entity keys overlap")
    question_ids = require_unique(questions, "questionId", "questions")
    contract_ids = require_unique(contracts, "contractId", "contracts")
    del contract_ids
    contract_entities = require_unique(contracts, "entityKey", "contracts")
    expected_contract_entities = function_entities | residual_entities
    if contract_entities != expected_contract_entities:
        raise CampaignError("campaign contracts do not account for every function and residual exactly once")
    if adjudications:
        require_unique(adjudications, "adjudicationId", "adjudications")
    if supersessions:
        require_unique(supersessions, "supersessionId", "supersessions")
        grouped_old: dict[str, list[dict[str, str]]] = {}
        for row in supersessions:
            grouped_old.setdefault(row.get("oldEntityKey", ""), []).append(row)
        if any(
            not old
            or (
                len(grouped) > 1
                and {row.get("kind") for row in grouped}
                != {GHIDRA_PARTITION_ADVANCE_KIND}
            )
            for old, grouped in grouped_old.items()
        ):
            raise CampaignError(
                "campaign supersessions contain a duplicate oldEntityKey outside exact partition"
            )
        for row in supersessions:
            if (
                row.get("newEntityKey") not in expected_contract_entities
                or row.get("oldEntityKey") == row.get("newEntityKey")
                or not row.get("kind")
                or row.get("verdict") != "SURVIVED"
                or not row.get("evidenceRefs")
                or not row.get("measuredAtUtc")
            ):
                raise CampaignError(
                    f"campaign contains an invalid supersession: {row.get('supersessionId', '')}"
                )
    _validate_campaign_relations(
        {
            "functions": functions,
            "residuals": residuals,
            "questions": questions,
            "scenarios": scenarios,
            "levers": levers,
            "contracts": contracts,
            "adjudications": adjudications,
            "supersessions": supersessions,
        },
        receipt,
    )
    question_by_id = {row["questionId"]: row for row in questions}
    for contract in contracts:
        if contract.get("contractState", "").startswith("TERMINAL_"):
            continue
        linked = [value for value in contract.get("questionIds", "").split(";") if value]
        if not linked or any(value not in question_ids for value in linked):
            raise CampaignError(
                f"nonterminal contract is unreachable from the question frontier: {contract['contractId']}"
            )
        if not any(question_by_id[value].get("state") == "OPEN" for value in linked):
            raise CampaignError(
                f"nonterminal contract has no open question: {contract['contractId']}"
            )

    expected_keys = {
        "schema",
        "reducer",
        "generatedAtUtc",
        "generation",
        "parentCampaign",
        "sourceSnapshot",
        "counts",
        "questionTypes",
        "policies",
        "outputs",
    }
    if _integer(receipt.get("generation"), -1) > 0:
        expected_keys.add("advance")
    if set(receipt) != expected_keys:
        raise CampaignError(
            f"campaign READY has unsupported/missing fields: {sorted(set(receipt) ^ expected_keys)}"
        )
    if _replay_generation:
        _replay_campaign_generation(campaign.resolve(), receipt)
    return receipt


def next_questions(campaign: Path, top: int, unattended: bool) -> list[dict[str, str]]:
    verify(campaign)
    rows = _read_tsv(campaign / "campaign-questions.tsv")
    rows = [row for row in rows if row["state"] == "OPEN"]
    if unattended:
        rows = [row for row in rows if not _bool(row["requiresElevation"])]
    rows.sort(
        key=lambda row: (
            _integer(row["priority"], 999),
            -float(row["score"] or 0),
            row["questionId"],
        )
    )
    return rows[:top]


def _eligible_boundary_questions(campaign: Path, limit: int) -> list[dict[str, str]]:
    if limit < 0:
        raise CampaignError("boundary-export limit cannot be negative")
    rows = _read_tsv(campaign / "campaign-questions.tsv")
    rows = [
        row
        for row in rows
        if row["state"] == "OPEN"
        and row["questionType"] == "NATIVE_BOUNDARY"
        and _integer(row["priority"], 999) == 0
        and not _bool(row["requiresElevation"])
    ]
    rows.sort(key=lambda row: (-float(row["score"] or 0), row["questionId"]))
    return rows[:limit] if limit else rows


def _boundary_targets(
    rows: list[dict[str, str]], specimen_sha: str
) -> list[dict[str, str]]:
    targets = []
    for row in rows:
        match = re.fullmatch(
            r"CODE_CANDIDATE:([0-9a-fA-F]{64}):VA=(0[xX][0-9a-fA-F]+)",
            row["entityKey"],
        )
        if not match:
            raise CampaignError(
                f"native boundary {row['questionId']} is not a CODE_CANDIDATE entity"
            )
        if match.group(1).lower() != specimen_sha.lower():
            raise CampaignError(
                f"native boundary {row['questionId']} names a different specimen"
            )
        targets.append(
            {
                "questionId": row["questionId"],
                "entityKey": row["entityKey"],
                "address": f"0x{int(match.group(2), 16):08x}",
                "source": row["source"],
            }
        )
    return targets


def export_observed_boundaries(campaign: Path, out: Path, limit: int = 0) -> dict:
    """Publish an address-only Ghidra input for observed missing native entries.

    Names are intentionally absent: coverage proves that the entry executed, but
    the shipped registry string still needs an independent behavior contract
    before it can become naming authority.
    """
    campaign_receipt = verify(campaign)
    if out.exists():
        raise CampaignError(f"refusing existing boundary-export destination: {out}")
    rows = _eligible_boundary_questions(campaign, limit)
    if not rows:
        raise CampaignError("campaign has no eligible observed native boundary questions")

    specimen_sha = campaign_receipt["sourceSnapshot"]["specimen"]["sha256"].lower()
    targets = _boundary_targets(rows, specimen_sha)

    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        address_path = stage / "boundary-targets.txt"
        address_path.write_text(
            "".join(f"{target['address']}\n" for target in targets),
            encoding="ascii",
        )
        receipt = {
            "schema": BOUNDARY_EXPORT_SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "sourceCampaign": {
                "path": str(campaign),
                "ready": coverage.file_stamp(campaign / "campaign.ready.json"),
                "coverageSetSha256": campaign_receipt["sourceSnapshot"]["coverageSetSha256"],
                "specimen": campaign_receipt["sourceSnapshot"]["specimen"],
            },
            "selection": {
                "questionType": "NATIVE_BOUNDARY",
                "priority": 0,
                "requiresElevation": False,
                "state": "OPEN",
                "limit": limit,
                "namesAuthorized": False,
            },
            "count": len(targets),
            "targets": targets,
            "output": {
                **coverage.file_stamp(address_path),
                "path": address_path.name,
            },
        }
        (stage / "boundary-targets.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify_boundary_export(out: Path) -> dict:
    receipt_path = out / "boundary-targets.ready.json"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot read boundary-export READY receipt: {exc}") from exc
    if receipt.get("schema") != BOUNDARY_EXPORT_SCHEMA:
        raise CampaignError(f"unsupported boundary-export schema: {receipt.get('schema')!r}")
    expected_keys = {
        "schema", "generatedAtUtc", "sourceCampaign", "selection",
        "count", "targets", "output",
    }
    if set(receipt) != expected_keys:
        raise CampaignError("boundary-export READY has unsupported/missing fields")
    address_path = out / "boundary-targets.txt"
    expected = receipt.get("output")
    if not address_path.is_file() or not isinstance(expected, dict):
        raise CampaignError("boundary-export address list is missing from disk/receipt")
    actual = coverage.file_stamp(address_path)
    if actual["bytes"] != expected.get("bytes") or actual["sha256"] != expected.get("sha256"):
        raise CampaignError("boundary-export address list disagrees with READY receipt")
    addresses = address_path.read_text(encoding="ascii").splitlines()
    target_addresses = [row.get("address") for row in receipt.get("targets", [])]
    if addresses != target_addresses or len(addresses) != receipt.get("count"):
        raise CampaignError("boundary-export targets do not reproduce the address list")
    if any(not re.fullmatch(r"0x[0-9a-f]{8}", address) for address in addresses):
        raise CampaignError("boundary-export contains a non-canonical address")
    selection = _runtime_mapping(receipt.get("selection"), "boundary selection")
    expected_selection = {
        "questionType": "NATIVE_BOUNDARY",
        "priority": 0,
        "requiresElevation": False,
        "state": "OPEN",
        "limit": selection.get("limit"),
        "namesAuthorized": False,
    }
    if not isinstance(selection.get("limit"), int) or selection.get("limit") < 0:
        raise CampaignError("boundary-export selection limit is invalid")
    if selection != expected_selection:
        raise CampaignError("boundary-export selection policy is not exact")

    source = _runtime_mapping(receipt.get("sourceCampaign"), "boundary sourceCampaign")
    source_root = _resolve_repo_or_absolute(
        source.get("path"), "boundary sourceCampaign"
    )
    source_ready_spec = _runtime_mapping(
        source.get("ready"), "boundary sourceCampaign.ready"
    )
    source_ready_path = source_root / "campaign.ready.json"
    _require_file_stamp(
        source_ready_path, source_ready_spec, "boundary source campaign READY"
    )
    source_ready = _runtime_json(source_ready_path, "boundary source campaign READY")
    source_outputs = _runtime_mapping(
        source_ready.get("outputs"), "boundary source campaign outputs"
    )
    for name, stamp_spec in source_outputs.items():
        if not isinstance(name, str) or Path(name).name != name:
            raise CampaignError("boundary source campaign output path is not local")
        _require_file_stamp(
            source_root / name,
            stamp_spec,
            f"boundary source campaign output {name}",
        )
    source_snapshot = _runtime_mapping(
        source_ready.get("sourceSnapshot"), "boundary source snapshot"
    )
    if (
        source.get("coverageSetSha256")
        != source_snapshot.get("coverageSetSha256")
        or not _same_json(source.get("specimen"), source_snapshot.get("specimen"))
        or re.fullmatch(
            r"[0-9a-f]{64}",
            str(source_snapshot.get("specimen", {}).get("sha256", "")).lower(),
        )
        is None
    ):
        raise CampaignError("boundary-export source campaign identity is inconsistent")
    expected_targets = _boundary_targets(
        _eligible_boundary_questions(source_root, selection["limit"]),
        source_snapshot["specimen"]["sha256"],
    )
    if receipt.get("targets") != expected_targets or receipt.get("count") != len(expected_targets):
        raise CampaignError("boundary-export does not reproduce from its source campaign")
    return receipt


def import_native_contract_candidates(
    campaign: Path,
    proposal: Path,
    out: Path,
    evidence_doc: Path | None = None,
) -> dict:
    """Turn a prior native proposal into a fail-closed, unadjudicated overlay."""
    campaign_receipt = verify(campaign)
    if out.exists():
        raise CampaignError(f"refusing existing contract-candidate destination: {out}")
    if not proposal.is_file():
        raise CampaignError(f"native proposal is missing: {proposal}")
    if evidence_doc is not None and not evidence_doc.is_file():
        raise CampaignError(f"native proposal evidence document is missing: {evidence_doc}")

    base_contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    contract_by_va = {row["entryVa"].lower(): row for row in base_contracts}
    proposal_rows = _read_tsv(proposal)
    required = {
        "handler", "proposedName", "shippedName", "cdbCalls", "traces",
        "argCountRuntime", "levelsCovered", "bodySpan", "argAccessors", "assertLine",
        "behaviourNote",
    }
    if not proposal_rows or not required.issubset(proposal_rows[0]):
        raise CampaignError(
            f"native proposal is missing required columns: {sorted(required - set(proposal_rows[0] if proposal_rows else []))}"
        )

    seen_handlers: set[str] = set()
    candidates = []
    evidence_refs = [str(proposal)]
    if evidence_doc is not None:
        evidence_refs.append(str(evidence_doc))
    for proposal_row in proposal_rows:
        try:
            address = f"0x{int(proposal_row['handler'], 16):08x}"
            calls = int(proposal_row["cdbCalls"])
            body_span = int(proposal_row["bodySpan"])
        except ValueError as exc:
            raise CampaignError("native proposal has a non-numeric handler/count/bodySpan") from exc
        if address in seen_handlers:
            raise CampaignError(f"native proposal repeats handler {address}")
        seen_handlers.add(address)
        if calls <= 0 or body_span <= 0 or not proposal_row["traces"].strip():
            raise CampaignError(f"native proposal lacks positive runtime/body evidence at {address}")
        shipped = proposal_row["shippedName"].strip()
        if proposal_row["proposedName"].strip() != f"IScript__{shipped}":
            raise CampaignError(f"native proposal name does not reproduce shipped name at {address}")
        base = contract_by_va.get(address)
        if base is None:
            raise CampaignError(f"native proposal handler is not a campaign function: {address}")
        if base["nativeShippedName"] != shipped:
            raise CampaignError(
                f"native proposal/campaign shipped names disagree at {address}: "
                f"{shipped!r} != {base['nativeShippedName']!r}"
            )
        note = proposal_row["behaviourNote"].strip()
        if not note:
            raise CampaignError(f"native proposal has no behavior note at {address}")
        arg_count = proposal_row["argCountRuntime"].strip()
        accessors = proposal_row["argAccessors"].strip()
        candidates.append(
            {
                **base,
                "proposedName": proposal_row["proposedName"].strip(),
                "contractState": "CANDIDATE_NEEDS_REFUTER",
                "semanticGrade": "C1_CANDIDATE_PARTIAL",
                "receiver": "UNKNOWN",
                "inputs": f"argc={arg_count or 'UNKNOWN'}; accessors={accessors or 'UNKNOWN'}",
                "returns": "UNKNOWN",
                "writes": "UNKNOWN",
                "sideEffects": note,
                "preconditions": "UNKNOWN",
                "failureModes": "UNKNOWN",
                "authorVerdict": "SUPPORTED_BY_PROPOSAL",
                "runtimeVerdict": f"PRESENCE_COUNTED:{calls}",
                "refuterVerdict": "UNSCORED",
                "cdbCalls": calls,
                "traces": proposal_row["traces"].strip(),
                "argCountRuntime": arg_count,
                "levelsCovered": proposal_row["levelsCovered"].strip(),
                "bodySpan": body_span,
                "argAccessors": accessors,
                "assertLine": proposal_row["assertLine"].strip(),
                "behaviourNote": note,
                "evidenceRefs": ";".join(evidence_refs),
            }
        )
    candidates.sort(key=lambda row: int(row["entryVa"], 16))

    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        candidate_path = stage / "candidate-contracts.tsv"
        _write_tsv(
            candidate_path,
            CANDIDATE_CONTRACT_COLUMNS,
            candidates,
            schema=CONTRACT_CANDIDATE_SCHEMA,
        )
        receipt = {
            "schema": CONTRACT_CANDIDATE_SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "sourceCampaign": {
                "path": str(campaign),
                "ready": coverage.file_stamp(campaign / "campaign.ready.json"),
                "specimen": campaign_receipt["sourceSnapshot"]["specimen"],
            },
            "proposal": coverage.file_stamp(proposal),
            "evidenceDocument": coverage.file_stamp(evidence_doc) if evidence_doc else None,
            "count": len(candidates),
            "policy": {
                "namesAuthorized": False,
                "requiresRefuter": True,
                "maximumImportedGrade": "C1_CANDIDATE_PARTIAL",
                "note": (
                    "Positive call counts and matching static behavior are candidate evidence only. "
                    "Receiver, values, writes, returns, and failure behavior remain open unless stated."
                ),
            },
            "output": {**coverage.file_stamp(candidate_path), "path": candidate_path.name},
        }
        (stage / "candidate-contracts.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify_native_contract_candidates(out: Path) -> dict:
    receipt_path = out / "candidate-contracts.ready.json"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot read contract-candidate READY receipt: {exc}") from exc
    if receipt.get("schema") != CONTRACT_CANDIDATE_SCHEMA:
        raise CampaignError(f"unsupported contract-candidate schema: {receipt.get('schema')!r}")
    candidate_path = out / "candidate-contracts.tsv"
    expected = receipt.get("output")
    if not candidate_path.is_file() or not isinstance(expected, dict):
        raise CampaignError("contract-candidate ledger is missing from disk/receipt")
    actual = coverage.file_stamp(candidate_path)
    if actual["bytes"] != expected.get("bytes") or actual["sha256"] != expected.get("sha256"):
        raise CampaignError("contract-candidate ledger disagrees with READY receipt")
    rows = _read_tsv(candidate_path)
    if len(rows) != receipt.get("count"):
        raise CampaignError("contract-candidate row count disagrees with READY receipt")
    if any(
        row["contractState"] != "CANDIDATE_NEEDS_REFUTER"
        or row["semanticGrade"] != "C1_CANDIDATE_PARTIAL"
        or row["refuterVerdict"] != "UNSCORED"
        for row in rows
    ):
        raise CampaignError("contract-candidate ledger bypasses the candidate/refuter gate")
    policy = receipt.get("policy", {})
    if policy.get("namesAuthorized") is not False or policy.get("requiresRefuter") is not True:
        raise CampaignError("contract-candidate receipt bypasses naming/refuter policy")
    return receipt


def _runtime_artifact_stamp(
    contract_path: Path,
    relative_path: object,
    expected_sha256: object,
    label: str,
) -> dict:
    artifact = _runtime_artifact_path(contract_path, relative_path, label)
    expected = str(expected_sha256).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise CampaignError(f"runtime contract {label} has an invalid SHA-256")
    stamp = coverage.file_stamp(artifact)
    if stamp["sha256"] != expected:
        raise CampaignError(
            f"runtime contract {label} artifact hash mismatch: "
            f"expected {expected}, found {stamp['sha256']}"
        )
    return {
        "role": label,
        "path": relative_path,
        "bytes": stamp["bytes"],
        "sha256": stamp["sha256"],
    }


def _runtime_artifact_path(
    contract_path: Path,
    relative_path: object,
    label: str,
) -> Path:
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise CampaignError(f"runtime contract {label} has no artifact path")
    rel = Path(relative_path)
    if rel.is_absolute():
        raise CampaignError(f"runtime contract {label} must use a relative artifact path")
    artifact = (contract_path.parent / rel).resolve()
    if not artifact.is_file():
        raise CampaignError(f"runtime contract {label} artifact is missing: {artifact}")
    return artifact


def _runtime_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"runtime contract {label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CampaignError(f"runtime contract {label} JSON root is not an object")
    return value


def _runtime_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise CampaignError(f"cannot read runtime contract {label}: {exc}") from exc


def _runtime_mapping(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise CampaignError(f"runtime contract {label} must be an object")
    return value


def _runtime_list(value: object, label: str) -> list:
    if not isinstance(value, list):
        raise CampaignError(f"runtime contract {label} must be a list")
    return value


def _validate_authored_manifest_from_disk(
    manifest_path: Path,
    *,
    source_path: Path,
    output_path: Path,
    label: str,
) -> dict:
    """Re-run the authoring verifier; manifest PASS labels are not evidence."""
    manifest = _runtime_json(manifest_path, label)
    source = _runtime_mapping(manifest.get("source"), f"{label}.source")
    output = _runtime_mapping(manifest.get("output"), f"{label}.output")
    try:
        declared_source = Path(str(source.get("path", ""))).resolve()
        declared_output = Path(str(output.get("path", ""))).resolve()
    except OSError as exc:
        raise CampaignError(f"runtime {label} declares an invalid artifact path") from exc
    if declared_source != source_path.resolve() or declared_output != output_path.resolve():
        raise CampaignError(f"runtime {label} does not name the identity-bound source/output files")
    try:
        report = probe_author.verify_manifest(manifest_path)
    except Exception as exc:  # the verifier's parser errors are evidence failures
        raise CampaignError(f"runtime {label} could not be independently re-verified: {exc}") from exc
    if not isinstance(report, dict) or report.get("ok") is not True:
        raise CampaignError(f"runtime {label} failed independent author-manifest verification")
    checks = report.get("checks")
    required = {
        "source_sha256",
        "source_inflated_sha256",
        "all_anchors_still_present_in_source",
        "output_readable",
        "output_sha256",
        "output_inflated_sha256",
        "output_blocks",
        "all_new_bytes_present_in_output",
    }
    if not isinstance(checks, dict) or any(checks.get(key) is not True for key in required):
        raise CampaignError(f"runtime {label} verifier omitted or failed load-bearing checks")
    if manifest.get("splice") is not None and (
        checks.get("splice_anchor_still_present_in_source") is not True
        or checks.get("splice_insert_present_in_output") is not True
    ):
        raise CampaignError(f"runtime {label} verifier did not authenticate its splice")
    return report


def _runtime_patch_relation(pristine: Path, runtime: Path, relation: object) -> None:
    if not isinstance(relation, dict) or relation.get("kind") != "DECLARED_BYTE_RANGES":
        raise CampaignError("runtime contract lacks a declared runtime/pristine byte relation")
    ranges = relation.get("ranges")
    if not isinstance(ranges, list) or not ranges:
        raise CampaignError("runtime contract runtime/pristine relation has no byte ranges")
    pristine_bytes = pristine.read_bytes()
    runtime_bytes = runtime.read_bytes()
    if len(pristine_bytes) != len(runtime_bytes):
        raise CampaignError("runtime and pristine executables differ in length")

    expected: dict[int, tuple[int, int]] = {}
    for index, row in enumerate(ranges):
        if not isinstance(row, dict):
            raise CampaignError(f"runtime patch range {index} is not an object")
        offset_text = row.get("offset")
        before_text = row.get("pristineHex")
        after_text = row.get("runtimeHex")
        if not isinstance(offset_text, str) or not re.fullmatch(r"0x[0-9a-fA-F]+", offset_text):
            raise CampaignError(f"runtime patch range {index} has no canonical offset")
        if (
            not isinstance(before_text, str)
            or not isinstance(after_text, str)
            or not re.fullmatch(r"(?:[0-9a-fA-F]{2})+", before_text)
            or not re.fullmatch(r"(?:[0-9a-fA-F]{2})+", after_text)
            or len(before_text) != len(after_text)
        ):
            raise CampaignError(f"runtime patch range {index} has invalid byte strings")
        offset = int(offset_text, 16)
        before = bytes.fromhex(before_text)
        after = bytes.fromhex(after_text)
        if offset + len(before) > len(pristine_bytes):
            raise CampaignError(f"runtime patch range {index} lies outside the executable")
        for delta, (old, new) in enumerate(zip(before, after)):
            absolute = offset + delta
            if absolute in expected:
                raise CampaignError("runtime patch ranges overlap")
            if old == new:
                raise CampaignError("runtime patch relation includes an unchanged byte")
            expected[absolute] = (old, new)

    actual = {
        index: (old, new)
        for index, (old, new) in enumerate(zip(pristine_bytes, runtime_bytes))
        if old != new
    }
    if actual != expected:
        raise CampaignError(
            "runtime executable does not reproduce the declared pristine byte relation"
        )
    if relation.get("differentBytes") != len(expected):
        raise CampaignError("runtime patch relation differentBytes is inconsistent")


def _runtime_staged_file(receipt: dict, destination: str, label: str) -> dict:
    staging = receipt.get("staging")
    files = staging.get("stagedFiles") if isinstance(staging, dict) else None
    if not isinstance(files, list):
        raise CampaignError(f"runtime {label} receipt has no staged-files ledger")
    matches = [
        row for row in files
        if isinstance(row, dict)
        and str(row.get("dest", "")).replace("\\", "/").lower() == destination.lower()
    ]
    if len(matches) != 1:
        raise CampaignError(
            f"runtime {label} receipt must stage exactly one {destination} artifact"
        )
    return matches[0]


def _validate_runtime_receipt(
    receipt: dict,
    *,
    label: str,
    scope: dict,
    trigger: dict,
    identity: dict,
    payload_sha256: str,
    expect_fault: bool,
) -> None:
    probe = receipt.get("probe")
    oracle = receipt.get("oracle")
    diagnosis = receipt.get("diagnosis")
    fault_gate = receipt.get("faultGate")
    source_witness = receipt.get("sourceWitness")
    staging = receipt.get("staging")
    teardown = receipt.get("teardown")
    if not all(
        isinstance(value, dict)
        for value in (probe, oracle, diagnosis, fault_gate, source_witness, staging, teardown)
    ):
        raise CampaignError(f"runtime {label} receipt lacks required structured sections")
    probe_oracle = _runtime_mapping(probe.get("oracle"), f"{label} receipt probe.oracle")
    if (
        receipt.get("dryRun") is not False
        or receipt.get("status") != "complete"
        or receipt.get("verdict") != "PASS"
        or oracle.get("outcome") != "satisfied"
        or teardown.get("verified") is not True
        or probe.get("level") != scope.get("level")
    ):
        raise CampaignError(f"runtime {label} receipt did not complete its declared oracle")
    if source_witness.get("BEA.exe") != identity.get("runtimeExecutableSha256"):
        raise CampaignError(f"runtime {label} receipt names a different runtime executable")
    if source_witness.get("BEA.exe.original.backup") != identity.get("pristineSpecimenSha256"):
        raise CampaignError(f"runtime {label} receipt names a different pristine specimen")
    if staging.get("executableSha256") != identity.get("runtimeExecutableSha256"):
        raise CampaignError(f"runtime {label} staged executable hash is inconsistent")
    expected_args = trigger.get("launchArguments")
    if not isinstance(expected_args, list) or not expected_args:
        raise CampaignError("runtime contract trigger has no launchArguments")
    if not str(receipt.get("command", "")).endswith(" " + " ".join(map(str, expected_args))):
        raise CampaignError(f"runtime {label} receipt used different launch arguments")

    staged = _runtime_staged_file(receipt, "data/resources/100_res_pc.aya", label)
    if str(staged.get("sha256", "")).lower() != payload_sha256.lower():
        raise CampaignError(f"runtime {label} receipt staged a different payload")
    if str(staged.get("replacedSha256", "")).lower() != str(
        identity.get("sourceArchiveSha256", "")
    ).lower():
        raise CampaignError(f"runtime {label} receipt replaced a different source archive")

    if diagnosis.get("levelLoadLogged") is not True:
        raise CampaignError(f"runtime {label} receipt never reached the level-load marker")
    if expect_fault:
        exit_classification = receipt.get("exitClassification")
        if (
            probe_oracle.get("kind") != "fatalFault"
            or diagnosis.get("fatalFaultLogPresent") is not True
            or fault_gate.get("triggered") is not True
            or fault_gate.get("optedIn") is not True
            or not isinstance(exit_classification, dict)
            or exit_classification.get("isFault") is not True
            or exit_classification.get("hex") != "0xC0000005"
        ):
            raise CampaignError(f"runtime {label} receipt did not reproduce the poison fault")
    else:
        oracle_members = _runtime_list(
            probe_oracle.get("of"), f"{label} receipt probe.oracle.of"
        )
        oracle_kinds = {
            row.get("kind")
            for row in oracle_members
            if isinstance(row, dict)
        }
        if (
            probe_oracle.get("kind") != "all"
            or not {"setupHistoryContains", "fileAppears", "survives"}.issubset(oracle_kinds)
            or diagnosis.get("fatalFaultLogPresent") is not False
            or oracle.get("processAliveAtDecision") is not True
            or fault_gate.get("triggered") is not False
        ):
            raise CampaignError(f"runtime {label} receipt did not reproduce valid payload liveness")


def _validate_runtime_authoring(
    *,
    recipe: dict,
    author_manifest: dict,
    poison_manifest: dict,
    scope: dict,
    trigger: dict,
    identity: dict,
    amount_value: float,
) -> None:
    recipe_intents = recipe.get("intents")
    manifest_intents = author_manifest.get("intents")
    if (
        recipe.get("world") != "RLWD"
        or not isinstance(recipe_intents, list)
        or len(recipe_intents) != 1
        or manifest_intents != recipe_intents
    ):
        raise CampaignError("runtime recipe and author manifest do not describe one identical edit")
    intent = _runtime_mapping(recipe_intents[0], "recipe intent")
    program = intent.get("program")
    if (
        intent.get("op") != "replace-script"
        or intent.get("script") != scope.get("script")
        or not isinstance(program, list)
        or len(program) != 5
    ):
        raise CampaignError("runtime recipe is not the bounded five-statement Setup program")
    native_names = [row.get("native") for row in program if isinstance(row, dict)]
    if native_names != ["GetThingRef", "SetVulnerable", "SetHealth", "Pause", "Damage"]:
        raise CampaignError("runtime recipe native order differs from the bounded scenario")
    try:
        receiver_name = program[0]["args"][0]["string"]
        health = float(program[2]["args"][0]["float"])
        pause = float(program[3]["args"][0]["float"])
        damage = float(program[4]["args"][0]["float"])
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise CampaignError("runtime recipe has malformed bounded arguments") from exc
    if (
        receiver_name != scope.get("receiverName")
        or health != 0.001
        or pause != 1.0
        or damage != amount_value
        or program[1].get("args") != [{"bool": True}]
    ):
        raise CampaignError("runtime recipe arguments differ from the declared scenario")

    verification = _runtime_mapping(
        author_manifest.get("verification"), "author manifest verification"
    )
    author_source = _runtime_mapping(author_manifest.get("source"), "author manifest source")
    author_output = _runtime_mapping(author_manifest.get("output"), "author manifest output")
    author_world = _runtime_mapping(author_manifest.get("world"), "author manifest world")
    splice = _runtime_mapping(author_manifest.get("splice"), "author manifest splice")
    emitter = _runtime_mapping(splice.get("emitter"), "author manifest emitter")
    native_calls = _runtime_list(emitter.get("nativeCalls"), "author manifest native calls")
    if (
        author_manifest.get("arm") != "probe"
        or author_manifest.get("specimen_sha256") != identity.get("pristineSpecimenSha256")
        or author_source.get("sha256") != identity.get("sourceArchiveSha256")
        or author_output.get("sha256") != identity.get("payloadSha256")
        or author_world.get("level_id") != scope.get("level")
        or verification.get("replacementScriptOrderPreserved") is not True
        or verification.get("replacementTargetOrdinalPreserved") is not True
        or verification.get("replacementRecordReadbackExact") is not True
        or verification.get("replacementNonTargetRecordsIdentical") != trigger.get(
            "nonTargetScriptRecordsByteIdentical"
        )
        or emitter.get("instructionCount") != trigger.get("emittedInstructionCount")
        or emitter.get("recordBytes") != trigger.get("emittedRecordBytes")
        or any(not isinstance(row, dict) for row in native_calls)
        or [row.get("native") for row in native_calls] != native_names
    ):
        raise CampaignError("runtime author manifest does not reproduce the authored payload")

    poison_verification = _runtime_mapping(
        poison_manifest.get("verification"), "poison manifest verification"
    )
    poison_source = _runtime_mapping(poison_manifest.get("source"), "poison manifest source")
    poison_output = _runtime_mapping(poison_manifest.get("output"), "poison manifest output")
    poison_edits = _runtime_list(poison_manifest.get("edits"), "poison manifest edits")
    if (
        poison_manifest.get("arm") != "poison-opcode"
        or poison_manifest.get("specimen_sha256") != identity.get("pristineSpecimenSha256")
        or poison_source.get("sha256") != identity.get("payloadSha256")
        or poison_output.get("sha256") != identity.get("poisonPayloadSha256")
        or poison_verification.get("diff_ranges") != 1
        or poison_verification.get("changed_bytes") != 1
        or poison_verification.get("differs_from_probe_only_by_this_arm") is not True
        or len(poison_edits) != 1
        or not isinstance(poison_edits[0], dict)
        or poison_edits[0].get("kind") != "poison-opcode"
        or poison_edits[0].get("old_opcode") != 0x17
        or poison_edits[0].get("new_opcode") != 0x7F
    ):
        raise CampaignError("runtime poison manifest is not the one-byte authored control")


def _validate_runtime_cdb_evidence(
    *,
    evidence_paths: dict[str, Path],
    calls: list[dict],
    inputs: dict,
    transition: dict,
) -> None:
    amount = _runtime_mapping(inputs.get("amount"), "inputsAtApplyDamage.amount")
    life = _runtime_mapping(transition.get("life"), "stateTransition.life")
    shields = _runtime_mapping(transition.get("shields"), "stateTransition.shields")
    state_1f0 = _runtime_mapping(
        transition.get("immediateField1f0"), "stateTransition.immediateField1f0"
    )
    expected_names = [
        "IScript__GetThingRef",
        "IScript__SetVulnerable",
        "IScript__SetHealth",
        "IScript__Pause",
        "IScript__Damage",
        "CUnit__ApplyDamage",
        "CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph",
        "CGroundUnit__MarkDestroyedAndResetState",
        "CUnit__ResetDeploymentGraphAndScheduleEvent",
        "SharedVFunc__NoOpRet8_00405db0",
    ]
    if [row.get("boundedName") for row in calls] != expected_names:
        raise CampaignError("runtime call order does not match the bounded damage-chain schema")
    vas = [str(row["va"]).lower() for row in calls]

    ordered = _runtime_text(evidence_paths["ordered five-native chain"], "ordered CDB log")
    markers = re.findall(
        r"^CHAIN\s+([1-5])\s+(GetThingRef|SetVulnerable|SetHealth|Pause|Damage)\s+"
        r"eip=([0-9a-fA-F]{8})\s+esp=[0-9a-fA-F]{8}\r?\n"
        r"[0-9a-fA-F]{8}\s+([0-9a-fA-F]{8})\b",
        ordered,
        flags=re.MULTILINE,
    )
    expected_markers = [
        (str(index + 1), name.removeprefix("IScript__"), va[2:], "0052eb56")
        for index, (name, va) in enumerate(zip(expected_names[:5], vas[:5]))
    ]
    if [(a, b, c.lower(), d.lower()) for a, b, c, d in markers] != expected_markers:
        raise CampaignError("ordered CDB log does not reproduce the five VM-dispatch entries")

    abi = _runtime_text(evidence_paths["receiver, vtable, callee, ABI"], "ABI CDB log")
    dispatch = re.search(
        r"DAMAGE_DISPATCH receiver=([0-9a-fA-F]{8}) vtable=([0-9a-fA-F]{8}) "
        r"callee=([0-9a-fA-F]{8}) amount_bits=([0-9a-fA-F]{8})\r?\n"
        r"[0-9a-fA-F]{8}\s+([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+"
        r"([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})",
        abi,
    )
    if (
        dispatch is None
        or dispatch.group(2).lower() != str(inputs.get("receiverVtable", ""))[2:].lower()
        or dispatch.group(3).lower() != vas[5][2:]
        or dispatch.group(4).lower() != str(amount.get("bits", ""))[2:].lower()
        or dispatch.group(5).lower() != dispatch.group(4).lower()
        or int(dispatch.group(6), 16) == 0
        or dispatch.group(7).lower() != "00000001"
        or dispatch.group(8).lower() != "ffffffff"
    ):
        raise CampaignError("ABI CDB log does not reproduce the declared damage dispatch")

    transition_text = _runtime_text(
        evidence_paths["life and shield transition"], "transition CDB log"
    )
    entry = re.search(
        r"APPLY_ENTRY receiver=([0-9a-fA-F]{8}) vtable=([0-9a-fA-F]{8}) "
        r"amount_bits=([0-9a-fA-F]{8}) source=([0-9a-fA-F]{8}) "
        r"apply_shields=(\d+) mesh_part=([0-9a-fA-F]{8}) "
        r"life_bits=([0-9a-fA-F]{8}) shield_bits=([0-9a-fA-F]{8}) "
        r"state_1f0=([0-9a-fA-F]{8})",
        transition_text,
    )
    returned = re.search(
        r"APPLY_RETURN receiver=([0-9a-fA-F]{8}) vtable=([0-9a-fA-F]{8}) "
        r"life_bits=([0-9a-fA-F]{8}) shield_bits=([0-9a-fA-F]{8}) "
        r"state_1f0=([0-9a-fA-F]{8})",
        transition_text,
    )
    if (
        entry is None
        or returned is None
        or entry.group(1).lower() != returned.group(1).lower()
        or entry.group(2).lower() != str(inputs.get("receiverVtable", ""))[2:].lower()
        or entry.group(2).lower() != returned.group(2).lower()
        or entry.group(3).lower() != str(amount.get("bits", ""))[2:].lower()
        or int(entry.group(4), 16) == 0
        or entry.group(5) != "1"
        or entry.group(6).lower() != "ffffffff"
        or entry.group(7).lower() != str(life.get("beforeBits", ""))[2:].lower()
        or returned.group(3).lower() != str(life.get("afterBits", ""))[2:].lower()
        or entry.group(8).lower() != str(shields.get("beforeBits", ""))[2:].lower()
        or returned.group(4).lower() != str(shields.get("afterBits", ""))[2:].lower()
        or int(entry.group(9), 16) != state_1f0.get("before")
        or int(returned.group(5), 16) != state_1f0.get("after")
    ):
        raise CampaignError("transition CDB log does not reproduce the declared receiver state")

    death = _runtime_text(evidence_paths["death virtual call order"], "death CDB log")
    death_markers = re.findall(
        r"^DEATH_([1-4])\s+(slot_c8|MarkDestroyed|ResetDeployment|slot_11c_noop) "
        r"receiver=([0-9a-fA-F]{8})(?: life_bits=([0-9a-fA-F]{8}))?",
        death,
        flags=re.MULTILINE,
    )
    if (
        [(row[0], row[1]) for row in death_markers]
        != [
            ("1", "slot_c8"),
            ("2", "MarkDestroyed"),
            ("3", "ResetDeployment"),
            ("4", "slot_11c_noop"),
        ]
        or len({row[2].lower() for row in death_markers}) != 1
        or any(
            row[3] and row[3].lower() != str(life.get("afterBits", ""))[2:].lower()
            for row in death_markers
        )
    ):
        raise CampaignError("death CDB log does not reproduce the declared virtual-call order")


def _runtime_float(bits: object, value: object, label: str) -> float:
    if not isinstance(bits, str) or not re.fullmatch(r"0x[0-9a-fA-F]{8}", bits):
        raise CampaignError(f"runtime contract {label} lacks canonical float32 bits")
    measured = struct.unpack("<f", struct.pack("<I", int(bits, 16)))[0]
    try:
        declared = float(value)
    except (TypeError, ValueError) as exc:
        raise CampaignError(f"runtime contract {label} has no numeric float value") from exc
    if struct.pack("<f", declared) != struct.pack("<f", measured):
        raise CampaignError(
            f"runtime contract {label} value {declared!r} does not reproduce {bits}"
        )
    return measured


def _holdout_dword(value: object, label: str) -> str:
    text = str(value).lower()
    if not re.fullmatch(r"0x[0-9a-f]{8}", text):
        raise CampaignError(f"runtime holdout {label} lacks a canonical 32-bit value")
    return text[2:]


def _holdout_artifact_paths(
    preregistration_path: Path,
    preregistration: dict,
    required_roles: set[str],
    label: str,
) -> dict[str, Path]:
    rows = _runtime_list(preregistration.get("artifacts"), f"{label}.artifacts")
    paths: dict[str, Path] = {}
    resolved: set[Path] = set()
    for index, raw in enumerate(rows):
        row = _runtime_mapping(raw, f"{label}.artifacts[{index}]")
        role = str(row.get("role", "")).strip()
        if not role or role in paths:
            raise CampaignError(f"runtime holdout {label} repeats or omits an artifact role")
        path = _runtime_artifact_path(
            preregistration_path, row.get("path"), f"{label}:{role}"
        )
        _runtime_artifact_stamp(
            preregistration_path,
            row.get("path"),
            row.get("sha256"),
            f"{label}:{role}",
        )
        if path in resolved:
            raise CampaignError(f"runtime holdout {label} aliases artifact paths")
        resolved.add(path)
        paths[role] = path
    if set(paths) != required_roles:
        raise CampaignError(
            f"runtime holdout {label} artifact roles differ: "
            f"{sorted(paths)} != {sorted(required_roles)}"
        )
    return paths


def _holdout_output_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not re.match(r"^\d+:\d+>", line.strip())
    ]


def _validate_holdout_markers(text: str, outcome: dict, label: str) -> None:
    required = _runtime_list(outcome.get("requiredMarkers"), f"{label}.requiredMarkers")
    forbidden = _runtime_list(outcome.get("forbiddenMarkers"), f"{label}.forbiddenMarkers")
    if (
        not required
        or any(not isinstance(value, str) or not value.strip() for value in required + forbidden)
        or len(required) != len(set(required))
        or len(forbidden) != len(set(forbidden))
    ):
        raise CampaignError(f"runtime holdout {label} has an invalid marker plan")
    lines = _holdout_output_lines(text)
    for marker in required:
        if sum(line == marker for line in lines) != 1:
            raise CampaignError(
                f"runtime holdout {label} did not emit required marker exactly once: {marker}"
            )
    for marker in forbidden:
        if marker == "Syntax error":
            present = any(marker.lower() in line.lower() for line in lines)
        elif marker.endswith("_"):
            present = any(line.startswith(marker) for line in lines)
        else:
            present = any(line == marker or line.startswith(marker + " ") for line in lines)
        if present:
            raise CampaignError(f"runtime holdout {label} emitted forbidden marker: {marker}")
    generic_errors = (
        "Unable to load command file",
        "Couldn't resolve error",
        "Syntax error",
    )
    if any(any(marker.lower() in line.lower() for marker in generic_errors) for line in lines):
        raise CampaignError(f"runtime holdout {label} debugger instrument reported an error")


def _parse_holdout_fields(text: str, prefix: str, label: str) -> dict[str, str]:
    matches = re.findall(
        rf"^{re.escape(prefix)} receiver=([0-9a-fA-F]{{8}}) "
        rf"vtable=([0-9a-fA-F]{{8}}) return=([0-9a-fA-F]{{8}}) "
        rf"amount=([0-9a-fA-F]{{8}}) source=([0-9a-fA-F]{{8}}) "
        rf"shields=([0-9a-fA-F]{{8}}) mesh=([0-9a-fA-F]{{8}})$",
        text,
        flags=re.MULTILINE,
    )
    if len(matches) != 1:
        raise CampaignError(f"runtime holdout {label} lacks one exact measured-fields line")
    row = matches[0]
    return {
        "receiver": row[0].lower(),
        "vtable": row[1].lower(),
        "return": row[2].lower(),
        "amount": row[3].lower(),
        "source": row[4].lower(),
        "shields": row[5].lower(),
        "mesh": row[6].lower(),
    }


def _validate_holdout_log(
    log_path: Path,
    *,
    runtime_path: Path,
    scope: dict,
    outcome: dict,
    observation: dict,
    field_prefix: str,
    label: str,
) -> dict[str, str]:
    text = _runtime_text(log_path, label)
    level = scope.get("level")
    command = (
        f"CommandLine: {runtime_path} -skipfmv -forcewindowed -level {level}"
    ).lower()
    if command not in text.lower():
        raise CampaignError(f"runtime holdout {label} launched another executable or argument set")
    if text.count("Breakpoint 0 hit") != 1 or "quit:" not in _holdout_output_lines(text):
        raise CampaignError(f"runtime holdout {label} did not reach and cleanly leave one breakpoint")
    callee = _holdout_dword(observation.get("callee"), "observation.callee")
    if f"{callee} 6aff" not in text.lower() or f"eip={callee}" not in text.lower():
        raise CampaignError(f"runtime holdout {label} did not authenticate the callee entry")
    _validate_holdout_markers(text, outcome, label)
    fields = _parse_holdout_fields(text, field_prefix, label)
    amount = _runtime_mapping(observation.get("amount"), "holdout observation.amount")
    expected = {
        "vtable": _holdout_dword(
            observation.get("receiverVtable"), "observation.receiverVtable"
        ),
        "return": _holdout_dword(
            observation.get("returnAddress"), "observation.returnAddress"
        ),
        "amount": _holdout_dword(amount.get("bits"), "observation.amount.bits"),
        "shields": f"{int(observation.get('applyShields', -1)) & 0xffffffff:08x}",
        "mesh": f"{int(observation.get('meshPartIndex', 0)) & 0xffffffff:08x}",
    }
    if any(fields[key] != value for key, value in expected.items()):
        raise CampaignError(f"runtime holdout {label} fields disagree with the observation")
    if (
        fields["receiver"] == "00000000"
        or observation.get("damageSource") != "NON_NULL"
        or fields["source"] == "00000000"
    ):
        raise CampaignError(f"runtime holdout {label} lacks the declared receiver/source")
    return fields


def _validate_holdout_recipe(
    recipe: dict,
    manifest: dict,
    *,
    scope: dict,
    amount_value: float,
    specimen_sha256: str,
) -> None:
    intents = recipe.get("intents")
    if recipe.get("world") != "RLWD" or not isinstance(intents, list) or len(intents) != 1:
        raise CampaignError("runtime holdout recipe is not one RLWD script replacement")
    expected_program = [
        {
            "op": "let",
            "name": "target",
            "native": "GetThingRef",
            "args": [{"string": str(scope.get("receiverName"))}],
        },
        {
            "op": "call",
            "target": "target",
            "native": "SetVulnerable",
            "args": [{"bool": True}],
        },
        {
            "op": "call",
            "target": "target",
            "native": "SetHealth",
            "args": [{"float": 0.001}],
        },
        {"op": "call", "native": "Pause", "args": [{"float": 1.0}]},
        {
            "op": "call",
            "target": "target",
            "native": "Damage",
            "args": [{"float": amount_value}],
        },
    ]
    intent = _runtime_mapping(intents[0], "holdout recipe intent")
    if (
        intent.get("op") != "replace-script"
        or intent.get("script") != scope.get("script")
        or intent.get("program") != expected_program
    ):
        raise CampaignError("runtime holdout recipe does not reproduce the bounded program")
    if manifest.get("intents") != intents:
        raise CampaignError("runtime holdout manifest and recipe describe different programs")
    world = _runtime_mapping(manifest.get("world"), "holdout author manifest.world")
    verification = _runtime_mapping(
        manifest.get("verification"), "holdout author manifest.verification"
    )
    emitter = _runtime_mapping(
        _runtime_mapping(manifest.get("splice"), "holdout author manifest.splice").get(
            "emitter"
        ),
        "holdout author manifest.splice.emitter",
    )
    native_calls = emitter.get("nativeCalls")
    if (
        manifest.get("tool") != "tools/probe/probe_author.py"
        or str(manifest.get("specimen_sha256", "")).lower() != specimen_sha256
        or world.get("level_id") != scope.get("level")
        or emitter.get("script") != scope.get("script")
        or [row.get("native") for row in native_calls if isinstance(row, dict)]
        != ["GetThingRef", "SetVulnerable", "SetHealth", "Pause", "Damage"]
        or verification.get("replacementScriptOrderPreserved") is not True
        or verification.get("replacementTargetOrdinalPreserved") is not True
        or verification.get("replacementRecordReadbackExact") is not True
        or verification.get("replacementNonTargetRecordsIdentical") != 24
    ):
        raise CampaignError("runtime holdout author manifest omits a load-bearing program check")


def _holdout_receipt_stamp(root: Path, artifact: Path, role: str) -> dict:
    stamp = coverage.file_stamp(artifact)
    return {
        "role": role,
        "path": os.path.relpath(artifact, root),
        "bytes": stamp["bytes"],
        "sha256": stamp["sha256"],
    }


def import_runtime_holdout(campaign: Path, holdout_path: Path, out: Path) -> dict:
    """Publish one preregistered question holdout behind the existing refuter gate."""
    campaign_receipt = verify(campaign)
    if out.exists():
        raise CampaignError(f"refusing existing runtime-holdout destination: {out}")
    holdout = _runtime_json(holdout_path, "runtime holdout")
    if holdout.get("schema") != RUNTIME_HOLDOUT_INPUT_SCHEMA:
        raise CampaignError(f"unsupported runtime-holdout schema: {holdout.get('schema')!r}")
    if holdout.get("status") != "BOUNDED_RUNTIME_SURVIVED_CONTROL":
        raise CampaignError("runtime holdout has not survived its bounded negative control")

    scope = _runtime_mapping(holdout.get("scope"), "holdout scope")
    identity = _runtime_mapping(holdout.get("identity"), "holdout identity")
    observation = _runtime_mapping(holdout.get("observation"), "holdout observation")
    if (
        scope.get("kind") != "FORCED_SCRIPT"
        or scope.get("level") != 100
        or scope.get("script") != "Setup"
        or not str(scope.get("receiverName", "")).strip()
    ):
        raise CampaignError("runtime holdout lies outside the bounded Level 100 script scope")

    identity_paths: dict[str, Path] = {}
    identity_fields = {
        "pristineSpecimen": "pristineSpecimen",
        "runtimeExecutable": "runtimeExecutable",
        "sourceArchive": "sourceArchive",
        "payload": "payload",
        "recipe": "recipe",
        "authorManifest": "authorManifest",
    }
    for stem, label in identity_fields.items():
        identity_paths[stem] = _runtime_artifact_path(
            holdout_path, identity.get(f"{stem}Path"), f"identity:{label}"
        )
        _runtime_artifact_stamp(
            holdout_path,
            identity.get(f"{stem}Path"),
            identity.get(f"{stem}Sha256"),
            f"identity:{label}",
        )
    if len(set(identity_paths.values())) != len(identity_paths):
        raise CampaignError("runtime holdout identity artifacts alias one another")
    specimen_sha = campaign_receipt["sourceSnapshot"]["specimen"]["sha256"].lower()
    if str(identity.get("pristineSpecimenSha256", "")).lower() != specimen_sha:
        raise CampaignError("runtime holdout and campaign name different pristine specimens")
    _runtime_patch_relation(
        identity_paths["pristineSpecimen"],
        identity_paths["runtimeExecutable"],
        identity.get("runtimeRelationToPristine"),
    )

    positive = _runtime_mapping(holdout.get("positiveRun"), "holdout positiveRun")
    control = _runtime_mapping(holdout.get("negativeControl"), "holdout negativeControl")
    positive_prereg_path = _runtime_artifact_path(
        holdout_path, positive.get("preregistrationPath"), "positive preregistration"
    )
    positive_log_path = _runtime_artifact_path(
        holdout_path, positive.get("logPath"), "positive CDB log"
    )
    control_prereg_path = _runtime_artifact_path(
        holdout_path, control.get("preregistrationPath"), "control preregistration"
    )
    control_log_path = _runtime_artifact_path(
        holdout_path, control.get("logPath"), "control CDB log"
    )
    for block, stem, label in (
        (positive, "preregistration", "positive preregistration"),
        (positive, "log", "positive CDB log"),
        (control, "preregistration", "control preregistration"),
        (control, "log", "control CDB log"),
    ):
        _runtime_artifact_stamp(
            holdout_path, block.get(f"{stem}Path"), block.get(f"{stem}Sha256"), label
        )
    if len({positive_prereg_path, positive_log_path, control_prereg_path, control_log_path}) != 4:
        raise CampaignError("runtime holdout positive/control evidence aliases artifacts")

    positive_prereg = _runtime_json(positive_prereg_path, "positive preregistration")
    if positive_prereg.get("schema") != RUNTIME_HOLDOUT_PREREG_SCHEMA:
        raise CampaignError("runtime holdout has an unsupported positive preregistration")
    positive_artifacts = _holdout_artifact_paths(
        positive_prereg_path,
        positive_prereg,
        {
            "recipe",
            "payload",
            "author-manifest",
            "pristine-backup",
            "runtime-exe",
            "staged-payload",
            "cdb-primary-script",
        },
        "positive preregistration",
    )
    expected_positive_paths = {
        "recipe": identity_paths["recipe"],
        "payload": identity_paths["payload"],
        "author-manifest": identity_paths["authorManifest"],
        "pristine-backup": identity_paths["pristineSpecimen"],
        "runtime-exe": identity_paths["runtimeExecutable"],
    }
    if any(positive_artifacts[role] != path for role, path in expected_positive_paths.items()):
        raise CampaignError("runtime holdout positive preregistration names another identity")
    if coverage.file_stamp(positive_artifacts["staged-payload"])["sha256"] != str(
        identity.get("payloadSha256", "")
    ).lower():
        raise CampaignError("runtime holdout staged payload differs from its authored payload")

    addressed = _runtime_list(
        holdout.get("questionIdsAddressed"), "holdout questionIdsAddressed"
    )
    if (
        not addressed
        or len(addressed) != len(set(addressed))
        or any(not isinstance(value, str) or not value for value in addressed)
        or positive_prereg.get("questionId") not in addressed
    ):
        raise CampaignError("runtime holdout does not bind unique addressed questions")
    claim_outcome = _runtime_mapping(
        positive_prereg.get("claimOutcome"), "positive preregistration.claimOutcome"
    )
    amount = _runtime_mapping(observation.get("amount"), "holdout observation.amount")
    amount_value = _runtime_float(
        amount.get("bits"), amount.get("float32"), "holdout damage amount"
    )
    expected_claim = {
        "callee": str(observation.get("callee", "")).lower(),
        "returnAddress": str(observation.get("returnAddress", "")).lower(),
        "receiverVtable": str(observation.get("receiverVtable", "")).lower(),
        "amountBits": str(amount.get("bits", "")).lower(),
        "damageSource": observation.get("damageSource"),
        "applyShields": observation.get("applyShields"),
        "meshPartIndex": observation.get("meshPartIndex"),
    }
    if any(claim_outcome.get(key) != value for key, value in expected_claim.items()):
        raise CampaignError("runtime holdout preregistered claim differs from its observation")

    predecessor = _runtime_mapping(
        positive_prereg.get("predecessorAttempt"), "positive predecessorAttempt"
    )
    if predecessor.get("verdict") != "UNSCORED" or not str(
        predecessor.get("reason", "")
    ).strip():
        raise CampaignError("runtime holdout predecessor was not explicitly UNSCORED")
    predecessor_path = _runtime_artifact_path(
        positive_prereg_path, predecessor.get("path"), "positive predecessor log"
    )
    _runtime_artifact_stamp(
        positive_prereg_path,
        predecessor.get("path"),
        predecessor.get("sha256"),
        "positive predecessor log",
    )

    control_prereg = _runtime_json(control_prereg_path, "control preregistration")
    if (
        control_prereg.get("schema") != RUNTIME_HOLDOUT_CONTROL_PREREG_SCHEMA
        or control_prereg.get("questionId") not in addressed
        or control_prereg.get("controlKind") != "WRONG_EXPECTED_AMOUNT"
    ):
        raise CampaignError("runtime holdout has an unsupported negative control")
    subject = _runtime_mapping(control_prereg.get("subjectRun"), "control subjectRun")
    subject_prereg_path = _runtime_artifact_path(
        control_prereg_path,
        subject.get("preregistrationPath"),
        "control subject preregistration",
    )
    subject_log_path = _runtime_artifact_path(
        control_prereg_path, subject.get("logPath"), "control subject log"
    )
    _runtime_artifact_stamp(
        control_prereg_path,
        subject.get("preregistrationPath"),
        subject.get("preregistrationSha256"),
        "control subject preregistration",
    )
    _runtime_artifact_stamp(
        control_prereg_path,
        subject.get("logPath"),
        subject.get("logSha256"),
        "control subject log",
    )
    if subject_prereg_path != positive_prereg_path or subject_log_path != positive_log_path:
        raise CampaignError("runtime holdout negative control names another positive subject")
    control_artifacts = _holdout_artifact_paths(
        control_prereg_path,
        control_prereg,
        {"payload", "pristine-backup", "runtime-exe", "staged-payload", "cdb-primary-script"},
        "control preregistration",
    )
    expected_hashes = {
        "payload": identity.get("payloadSha256"),
        "staged-payload": identity.get("payloadSha256"),
        "pristine-backup": identity.get("pristineSpecimenSha256"),
        "runtime-exe": identity.get("runtimeExecutableSha256"),
    }
    if any(
        coverage.file_stamp(control_artifacts[role])["sha256"] != str(expected).lower()
        for role, expected in expected_hashes.items()
    ):
        raise CampaignError("runtime holdout negative control changed a protected identity")

    positive_script = _runtime_text(
        positive_artifacts["cdb-primary-script"], "positive CDB script"
    ).lower()
    control_script = _runtime_text(
        control_artifacts["cdb-primary-script"], "control CDB script"
    ).lower()
    amount_bits = _holdout_dword(amount.get("bits"), "observation.amount.bits")
    positive_expectations = re.findall(
        r"dwo\(@esp\+4\) != 0x([0-9a-f]{8})", positive_script
    )
    control_expectations = re.findall(
        r"dwo\(@esp\+4\) != 0x([0-9a-f]{8})", control_script
    )
    if positive_expectations != [amount_bits] or len(control_expectations) != 1:
        raise CampaignError("runtime holdout scripts do not contain one exact amount check")
    if control_expectations[0] == amount_bits:
        raise CampaignError("runtime holdout negative control did not poison its amount expectation")

    recipe = _runtime_json(identity_paths["recipe"], "holdout recipe")
    manifest = _runtime_json(identity_paths["authorManifest"], "holdout author manifest")
    _validate_holdout_recipe(
        recipe,
        manifest,
        scope=scope,
        amount_value=amount_value,
        specimen_sha256=specimen_sha,
    )
    author_report = _validate_authored_manifest_from_disk(
        identity_paths["authorManifest"],
        source_path=identity_paths["sourceArchive"],
        output_path=identity_paths["payload"],
        label="holdout author manifest",
    )
    _validate_holdout_log(
        positive_log_path,
        runtime_path=identity_paths["runtimeExecutable"],
        scope=scope,
        outcome=claim_outcome,
        observation=observation,
        field_prefix="HOLDOUT_FIELDS",
        label="positive CDB log",
    )
    control_outcome = _runtime_mapping(
        control_prereg.get("predictedOutcome"), "control predictedOutcome"
    )
    _validate_holdout_log(
        control_log_path,
        runtime_path=control_artifacts["runtime-exe"],
        scope=scope,
        outcome=control_outcome,
        observation=observation,
        field_prefix="HOLDOUT_CONTROL_FIELDS",
        label="control CDB log",
    )

    contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    base_contract_id = str(holdout.get("baseContractId", ""))
    base = next((row for row in contracts if row["contractId"] == base_contract_id), None)
    if base is None:
        raise CampaignError("runtime holdout base contract is absent from the campaign")
    base_question_ids = {value for value in base.get("questionIds", "").split(";") if value}
    if not set(addressed).issubset(base_question_ids):
        raise CampaignError("runtime holdout addresses a question outside its base contract")
    questions = {row["questionId"]: row for row in _read_tsv(campaign / "campaign-questions.tsv")}
    for question_id in addressed:
        question = questions.get(question_id)
        if (
            question is None
            or question.get("entityKey") != base["entityKey"]
            or question.get("state") != "OPEN"
        ):
            raise CampaignError(f"runtime holdout question is not open on the base entity: {question_id}")

    measured_at = str(holdout.get("measuredAtUtc", ""))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T[^\s]+", measured_at):
        raise CampaignError("runtime holdout lacks measuredAtUtc")
    claim_boundary = _runtime_list(holdout.get("claimBoundary"), "holdout claimBoundary")
    next_frontier = _runtime_list(holdout.get("nextFrontier"), "holdout nextFrontier")
    if (
        not claim_boundary
        or not next_frontier
        or any(not isinstance(value, str) or not value.strip() for value in claim_boundary + next_frontier)
    ):
        raise CampaignError("runtime holdout lacks a bounded claim or next frontier")

    evidence_refs = ";".join(
        value for value in (base.get("evidenceRefs", ""), str(holdout_path)) if value
    )
    runtime_row = {
        **base,
        "contractState": "RUNTIME_CANDIDATE_NEEDS_REFUTER",
        "semanticGrade": "C2_BOUNDED_RUNTIME",
        "receiver": f"{scope['receiverName']}; vtable={observation['receiverVtable']}",
        "inputs": (
            f"{base.get('inputs', '')} | holdout amount={amount_value:g} "
            f"bits={amount.get('bits')}; source=NON_NULL; applyShields=1; meshPartIndex=-1"
        ),
        "sideEffects": (
            f"{base.get('sideEffects', '')} | holdout entry: "
            f"0x005348c0 -> {str(observation.get('callee')).lower()} amount={amount_value:g}"
        ),
        "preconditions": (
            f"{base.get('preconditions', '')} | holdout payload={identity.get('payloadSha256')}"
        ),
        "failureModes": " | ".join(
            [base.get("failureModes", "")] + [str(value) for value in claim_boundary]
        ).strip(" |"),
        "authorVerdict": "AUTHORED_HOLDOUT_MANIFEST_REVERIFIED",
        "runtimeVerdict": "VALUE_HOLDOUT_AND_WRONG_EXPECTATION_CONTROL_MEASURED",
        "refuterVerdict": "UNSCORED",
        "questionIds": ";".join(addressed),
        "evidenceRefs": evidence_refs,
        "cheapestFalsifier": str(next_frontier[0]),
        "lastMeasurementDate": measured_at[:10],
        "scopeKind": scope["kind"],
        "payloadSha256": str(identity.get("payloadSha256", "")).lower(),
        "receiverVtable": str(observation.get("receiverVtable", "")).lower(),
        "observedCallVas": "0x005348c0;" + str(observation.get("callee", "")).lower(),
        "controlSummary": "WRONG_EXPECTED_AMOUNT=FAILED_AS_PREDICTED",
        "runtimeEvidenceSha256": ";".join(
            [
                coverage.file_stamp(positive_prereg_path)["sha256"],
                coverage.file_stamp(positive_log_path)["sha256"],
                coverage.file_stamp(control_prereg_path)["sha256"],
                coverage.file_stamp(control_log_path)["sha256"],
            ]
        ),
        "baseContractId": base["contractId"],
        "questionIdsAddressed": ";".join(addressed),
    }

    receipt_artifacts: dict[str, Path] = {
        **{f"identity:{role}": path for role, path in identity_paths.items()},
        "positive:preregistration": positive_prereg_path,
        "positive:log": positive_log_path,
        "positive:predecessor-log": predecessor_path,
        "control:preregistration": control_prereg_path,
        "control:log": control_log_path,
    }
    receipt_artifacts.update(
        {f"positive-artifact:{role}": path for role, path in positive_artifacts.items()}
    )
    receipt_artifacts.update(
        {f"control-artifact:{role}": path for role, path in control_artifacts.items()}
    )
    artifact_stamps = [
        _holdout_receipt_stamp(holdout_path.parent, path, role)
        for role, path in receipt_artifacts.items()
    ]

    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        output_path = stage / "runtime-contracts.tsv"
        _write_tsv(
            output_path,
            RUNTIME_CONTRACT_COLUMNS,
            [runtime_row],
            schema=RUNTIME_CONTRACT_OVERLAY_SCHEMA,
        )
        receipt = {
            "schema": RUNTIME_CONTRACT_OVERLAY_SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "experimentKind": "QUESTION_HOLDOUT",
            "sourceCampaign": {
                "path": str(campaign),
                "ready": coverage.file_stamp(campaign / "campaign.ready.json"),
                "specimen": campaign_receipt["sourceSnapshot"]["specimen"],
            },
            "inputContract": coverage.file_stamp(holdout_path),
            "artifacts": artifact_stamps,
            "authorVerification": {"authorManifestChecks": author_report["checks"]},
            "count": 1,
            "policy": {
                "namesAuthorized": False,
                "ghidraMutationAuthorized": False,
                "promotionAuthorized": False,
                "requiresRefuter": True,
                "maximumImportedGrade": "C2_BOUNDED_RUNTIME",
                "artifactClaimsParsed": True,
                "runtimeExecutableRelationValidated": True,
                "instrumentNegativeControlValidated": True,
            },
            "output": {**coverage.file_stamp(output_path), "path": output_path.name},
        }
        (stage / "runtime-contracts.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def import_runtime_contract(campaign: Path, contract_path: Path, out: Path) -> dict:
    """Parse and publish one artifact-bound runtime contract behind the refuter gate."""
    campaign_receipt = verify(campaign)
    if out.exists():
        raise CampaignError(f"refusing existing runtime-contract destination: {out}")
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot read runtime contract {contract_path}: {exc}") from exc
    if not isinstance(contract, dict):
        raise CampaignError("runtime contract JSON root is not an object")
    if contract.get("schema") != RUNTIME_CONTRACT_INPUT_SCHEMA:
        raise CampaignError(f"unsupported runtime-contract schema: {contract.get('schema')!r}")
    if contract.get("status") != "BOUNDED_RUNTIME_SURVIVED_CONTROLS":
        raise CampaignError("runtime contract has not survived its bounded controls")

    identity = contract.get("identity")
    scope = contract.get("scope")
    verdict = contract.get("verdict")
    if not all(isinstance(value, dict) for value in (identity, scope, verdict)):
        raise CampaignError("runtime contract lacks identity, scope, or verdict")
    specimen_sha = campaign_receipt["sourceSnapshot"]["specimen"]["sha256"].lower()
    if str(identity.get("pristineSpecimenSha256", "")).lower() != specimen_sha:
        raise CampaignError("runtime contract and campaign name different pristine specimens")
    required_verdicts = {
        "execution": "SURVIVED",
        "identity": "SURVIVED_FOR_SCOPED_PATH",
        "inputs": "MEASURED",
        "immediateOutputs": "MEASURED",
        "refuter": "UNSCORED",
        "promotion": "NOT_AUTHORIZED",
    }
    for key, expected in required_verdicts.items():
        if verdict.get(key) != expected:
            raise CampaignError(
                f"runtime contract verdict {key} must be {expected}, got {verdict.get(key)!r}"
            )

    artifact_stamps = []
    identity_paths: dict[str, Path] = {}
    for stem in (
        "pristineSpecimen", "runtimeExecutable", "launchedArchive", "sourceArchive",
        "payload", "poisonPayload", "recipe", "authorManifest", "poisonManifest",
    ):
        identity_paths[stem] = _runtime_artifact_path(
            contract_path, identity.get(f"{stem}Path"), f"identity:{stem}"
        )
        artifact_stamps.append(
            _runtime_artifact_stamp(
                contract_path,
                identity.get(f"{stem}Path"),
                identity.get(f"{stem}Sha256"),
                f"identity:{stem}",
            )
        )
    if len(set(identity_paths.values())) != len(identity_paths):
        raise CampaignError("runtime identity roles must resolve to distinct artifacts")
    if identity.get("launchedArchiveSha256") != identity.get("payloadSha256"):
        raise CampaignError("exact launched archive does not match the authored payload")
    _runtime_patch_relation(
        identity_paths["pristineSpecimen"],
        identity_paths["runtimeExecutable"],
        identity.get("runtimeRelationToPristine"),
    )

    controls = contract.get("controls")
    if not isinstance(controls, list):
        raise CampaignError("runtime contract controls must be a list")
    if any(not isinstance(row, dict) for row in controls):
        raise CampaignError("runtime contract controls contain a non-object row")
    control_kinds = [str(row.get("kind", "")) for row in controls]
    if any(not kind for kind in control_kinds) or len(control_kinds) != len(set(control_kinds)):
        raise CampaignError("runtime contract controls contain missing or duplicate kinds")
    controls_by_kind = {str(row["kind"]): row for row in controls}
    required_controls = {
        "VALID_EXISTING_TARGET": "PASS",
        "INVALID_OPCODE_POISON": "PASS",
        "ORDERED_CDB_ENTRY_CHAIN": "PASS",
    }
    for kind, expected in required_controls.items():
        control = controls_by_kind.get(kind)
        if control is None or control.get("verdict") != expected:
            raise CampaignError(f"runtime contract control {kind} must be {expected}")
    if controls_by_kind["VALID_EXISTING_TARGET"].get("receiptPath") is None:
        raise CampaignError("runtime valid control must carry its probe receipt")
    if controls_by_kind["INVALID_OPCODE_POISON"].get("receiptPath") is None:
        raise CampaignError("runtime poison control must carry its probe receipt")
    if controls_by_kind["ORDERED_CDB_ENTRY_CHAIN"].get("logPath") is None:
        raise CampaignError("runtime ordered-call control must carry its CDB log")
    control_paths: dict[str, Path] = {}
    for index, control in enumerate(controls):
        if not isinstance(control, dict):
            raise CampaignError(f"runtime contract control {index} is not an object")
        if control.get("receiptPath") is not None and control.get("logPath") is not None:
            raise CampaignError(f"runtime control {control.get('kind')!r} mixes receipt and log roles")
        if control.get("receiptPath") is not None:
            control_paths[str(control.get("kind"))] = _runtime_artifact_path(
                contract_path,
                control.get("receiptPath"),
                f"control:{control.get('kind', index)}",
            )
            artifact_stamps.append(
                _runtime_artifact_stamp(
                    contract_path, control.get("receiptPath"), control.get("receiptSha256"),
                    f"control:{control.get('kind', index)}",
                )
            )
        if control.get("logPath") is not None:
            control_paths[str(control.get("kind"))] = _runtime_artifact_path(
                contract_path,
                control.get("logPath"),
                f"control:{control.get('kind', index)}",
            )
            artifact_stamps.append(
                _runtime_artifact_stamp(
                    contract_path, control.get("logPath"), control.get("logSha256"),
                    f"control:{control.get('kind', index)}",
                )
            )
    if control_paths.get("VALID_EXISTING_TARGET") == control_paths.get(
        "INVALID_OPCODE_POISON"
    ):
        raise CampaignError("runtime valid and poison controls alias the same receipt")

    evidence = contract.get("runtimeEvidence")
    if not isinstance(evidence, list) or not evidence:
        raise CampaignError("runtime contract has no runtime evidence")
    evidence_roles = set()
    evidence_hashes = []
    evidence_paths: dict[str, Path] = {}
    for index, item in enumerate(evidence):
        if not isinstance(item, dict) or not str(item.get("role", "")).strip():
            raise CampaignError(f"runtime evidence {index} lacks a role")
        role = str(item["role"])
        if role in evidence_roles:
            raise CampaignError(f"runtime contract repeats evidence role {role!r}")
        evidence_roles.add(role)
        evidence_paths[role] = _runtime_artifact_path(
            contract_path, item.get("path"), f"evidence:{role}"
        )
        stamp = _runtime_artifact_stamp(
            contract_path, item.get("path"), item.get("sha256"), f"evidence:{role}"
        )
        artifact_stamps.append(stamp)
        evidence_hashes.append(stamp["sha256"])
    required_roles = {
        "ordered five-native chain",
        "receiver, vtable, callee, ABI",
        "life and shield transition",
        "death virtual call order",
    }
    if not required_roles.issubset(evidence_roles):
        raise CampaignError(
            f"runtime contract lacks required evidence roles: {sorted(required_roles - evidence_roles)}"
        )
    if len(set(evidence_paths.values())) != len(evidence_paths):
        raise CampaignError("runtime evidence roles must use distinct artifacts")
    if (
        control_paths["ORDERED_CDB_ENTRY_CHAIN"]
        != evidence_paths["ordered five-native chain"]
    ):
        raise CampaignError("ordered-call control and ordered-call evidence name different logs")

    primary_va = scope.get("primaryEntryVa")
    if not isinstance(primary_va, str) or not re.fullmatch(r"0x[0-9a-fA-F]{8}", primary_va):
        raise CampaignError("runtime contract has no canonical primaryEntryVa")
    primary_va = primary_va.lower()
    shipped_name = str(scope.get("primaryShippedName", "")).strip()
    base_contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    base = next((row for row in base_contracts if row["entryVa"].lower() == primary_va), None)
    if base is None:
        raise CampaignError(f"runtime contract primary function is not in the campaign: {primary_va}")
    if base["nativeShippedName"] != shipped_name:
        raise CampaignError(
            f"runtime contract/campaign shipped names disagree: "
            f"{shipped_name!r} != {base['nativeShippedName']!r}"
        )
    if contract.get("baseContractId") != base["contractId"]:
        raise CampaignError("runtime contract does not name its exact base contractId")
    addressed = contract.get("questionIdsAddressed")
    if (
        not isinstance(addressed, list)
        or not addressed
        or any(not isinstance(value, str) or not value for value in addressed)
        or len(addressed) != len(set(addressed))
    ):
        raise CampaignError("runtime contract must explicitly name unique questionIdsAddressed")
    base_question_ids = {value for value in base.get("questionIds", "").split(";") if value}
    if not set(addressed).issubset(base_question_ids):
        raise CampaignError("runtime contract addresses a question outside its base contract")
    campaign_questions = {
        row["questionId"]: row
        for row in _read_tsv(campaign / "campaign-questions.tsv")
    }
    for question_id in addressed:
        question = campaign_questions.get(question_id)
        if (
            question is None
            or question.get("entityKey") != base["entityKey"]
            or question.get("state") != "OPEN"
        ):
            raise CampaignError(
                f"runtime contract question is missing, closed, or bound to another entity: {question_id}"
            )

    calls = contract.get("observedCallOrder")
    if not isinstance(calls, list) or not calls:
        raise CampaignError("runtime contract has no observed call order")
    call_vas = []
    for index, call in enumerate(calls):
        va = call.get("va") if isinstance(call, dict) else None
        if not isinstance(va, str) or not re.fullmatch(r"0x[0-9a-fA-F]{8}", va):
            raise CampaignError(f"runtime contract call {index} has no canonical VA")
        call_vas.append(va.lower())
    if len(call_vas) != len(set(call_vas)) or primary_va not in call_vas:
        raise CampaignError("runtime contract call order repeats or omits the primary function")
    primary_call = calls[call_vas.index(primary_va)]
    if primary_call.get("boundedName") != f"IScript__{shipped_name}":
        raise CampaignError("runtime primary bounded name does not reproduce the shipped registry name")

    inputs = contract.get("inputsAtApplyDamage")
    transition = contract.get("stateTransition")
    if not isinstance(inputs, dict) or not isinstance(transition, dict):
        raise CampaignError("runtime contract lacks measured inputs or transition")
    amount = _runtime_mapping(inputs.get("amount"), "inputsAtApplyDamage.amount")
    amount_value = _runtime_float(amount.get("bits"), amount.get("float32"), "damage amount")
    life = _runtime_mapping(transition.get("life"), "stateTransition.life")
    shields = _runtime_mapping(transition.get("shields"), "stateTransition.shields")
    life_before = _runtime_float(life.get("beforeBits"), life.get("beforeFloat32"), "life before")
    life_after = _runtime_float(life.get("afterBits"), life.get("afterFloat32"), "life after")
    shield_before = _runtime_float(
        shields.get("beforeBits"), shields.get("beforeFloat32"), "shields before"
    )
    shield_after = _runtime_float(
        shields.get("afterBits"), shields.get("afterFloat32"), "shields after"
    )
    if inputs.get("applyShields") != 1 or inputs.get("meshPartIndex") != -1:
        raise CampaignError("runtime damage ABI lacks applyShields=1 or meshPartIndex=-1")
    if struct.pack("<f", life_after) != struct.pack("<f", life_before - amount_value):
        raise CampaignError("runtime life transition does not reproduce life-before minus amount")
    if struct.pack("<f", shield_after) != struct.pack("<f", shield_before):
        raise CampaignError("runtime shield transition changed despite the declared zero-shield path")

    trigger = contract.get("trigger")
    if not isinstance(trigger, dict):
        raise CampaignError("runtime contract lacks its authored trigger")
    recipe = _runtime_json(identity_paths["recipe"], "recipe")
    author_manifest = _runtime_json(identity_paths["authorManifest"], "author manifest")
    poison_manifest = _runtime_json(identity_paths["poisonManifest"], "poison manifest")
    _validate_runtime_authoring(
        recipe=recipe,
        author_manifest=author_manifest,
        poison_manifest=poison_manifest,
        scope=scope,
        trigger=trigger,
        identity=identity,
        amount_value=amount_value,
    )
    author_report = _validate_authored_manifest_from_disk(
        identity_paths["authorManifest"],
        source_path=identity_paths["sourceArchive"],
        output_path=identity_paths["payload"],
        label="author manifest",
    )
    poison_report = _validate_authored_manifest_from_disk(
        identity_paths["poisonManifest"],
        source_path=identity_paths["payload"],
        output_path=identity_paths["poisonPayload"],
        label="poison manifest",
    )
    _validate_runtime_receipt(
        _runtime_json(control_paths["VALID_EXISTING_TARGET"], "valid control receipt"),
        label="valid control",
        scope=scope,
        trigger=trigger,
        identity=identity,
        payload_sha256=str(identity.get("payloadSha256", "")),
        expect_fault=False,
    )
    _validate_runtime_receipt(
        _runtime_json(control_paths["INVALID_OPCODE_POISON"], "poison control receipt"),
        label="poison control",
        scope=scope,
        trigger=trigger,
        identity=identity,
        payload_sha256=str(identity.get("poisonPayloadSha256", "")),
        expect_fault=True,
    )
    _validate_runtime_cdb_evidence(
        evidence_paths=evidence_paths,
        calls=calls,
        inputs=inputs,
        transition=transition,
    )

    scope_kind = str(scope.get("kind", ""))
    if scope_kind not in {"NATURAL", "FORCED_DATA", "FORCED_SCRIPT", "FORCED_CODE"}:
        raise CampaignError(f"runtime contract has unsupported scope kind {scope_kind!r}")
    claim_boundary = contract.get("claimBoundary")
    next_frontier = contract.get("nextFrontier")
    if not isinstance(claim_boundary, list) or not claim_boundary:
        raise CampaignError("runtime contract has no claim boundary")
    if not isinstance(next_frontier, list) or not next_frontier:
        raise CampaignError("runtime contract has no next frontier")

    measured_date = str(contract.get("measuredAtUtc", ""))[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", measured_date):
        raise CampaignError("runtime contract has no measuredAtUtc date")
    control_summary = ";".join(
        f"{row.get('kind')}={row.get('verdict')}" for row in controls if isinstance(row, dict)
    )
    runtime_row = {
        **base,
        "contractState": "RUNTIME_CANDIDATE_NEEDS_REFUTER",
        "semanticGrade": "C2_BOUNDED_RUNTIME",
        "receiver": (
            f"{scope.get('receiverName', 'UNKNOWN')}; "
            f"vtable={inputs.get('receiverVtable', 'UNKNOWN')}"
        ),
        "inputs": (
            f"amount={amount_value:g}; source={inputs.get('damageSource', 'UNKNOWN')}; "
            "applyShields=1; meshPartIndex=-1"
        ),
        "returns": "void on observed path",
        "writes": (
            f"life {life_before!r}->{life_after!r}; "
            f"shields {shield_before!r}->{shield_after!r}"
        ),
        "sideEffects": "ordered calls: " + " -> ".join(call_vas),
        "preconditions": (
            f"{scope_kind}; level={scope.get('level')}; script={scope.get('script')}; "
            f"receiver={scope.get('receiverName')}"
        ),
        "failureModes": " | ".join(str(item) for item in claim_boundary),
        "authorVerdict": "AUTHORED_RECIPE_AND_CONTROLS_SURVIVED",
        "runtimeVerdict": "ORDERED_CALLS_AND_STATE_TRANSITION_MEASURED",
        "refuterVerdict": "UNSCORED",
        "questionIds": ";".join(addressed),
        "evidenceRefs": str(contract_path),
        "cheapestFalsifier": str(next_frontier[0]),
        "lastMeasurementDate": measured_date,
        "scopeKind": scope_kind,
        "payloadSha256": str(identity.get("payloadSha256", "")).lower(),
        "receiverVtable": str(inputs.get("receiverVtable", "")),
        "observedCallVas": ";".join(call_vas),
        "controlSummary": control_summary,
        "runtimeEvidenceSha256": ";".join(evidence_hashes),
        "baseContractId": base["contractId"],
        "questionIdsAddressed": ";".join(addressed),
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        output_path = stage / "runtime-contracts.tsv"
        _write_tsv(
            output_path,
            RUNTIME_CONTRACT_COLUMNS,
            [runtime_row],
            schema=RUNTIME_CONTRACT_OVERLAY_SCHEMA,
        )
        receipt = {
            "schema": RUNTIME_CONTRACT_OVERLAY_SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "sourceCampaign": {
                "path": str(campaign),
                "ready": coverage.file_stamp(campaign / "campaign.ready.json"),
                "specimen": campaign_receipt["sourceSnapshot"]["specimen"],
            },
            "inputContract": coverage.file_stamp(contract_path),
            "artifacts": artifact_stamps,
            "authorVerification": {
                "authorManifestChecks": author_report["checks"],
                "poisonManifestChecks": poison_report["checks"],
            },
            "count": 1,
            "policy": {
                "namesAuthorized": False,
                "ghidraMutationAuthorized": False,
                "promotionAuthorized": False,
                "requiresRefuter": True,
                "maximumImportedGrade": "C2_BOUNDED_RUNTIME",
                "artifactClaimsParsed": True,
                "runtimeExecutableRelationValidated": True,
            },
            "output": {**coverage.file_stamp(output_path), "path": output_path.name},
        }
        (stage / "runtime-contracts.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify_runtime_contract_overlay(out: Path) -> dict:
    receipt_path = out / "runtime-contracts.ready.json"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot read runtime-contract READY receipt: {exc}") from exc
    if receipt.get("schema") != RUNTIME_CONTRACT_OVERLAY_SCHEMA:
        raise CampaignError(f"unsupported runtime-contract overlay: {receipt.get('schema')!r}")
    source = _runtime_mapping(receipt.get("sourceCampaign"), "overlay sourceCampaign")
    source_path = Path(str(source.get("path", ""))).resolve()
    source_ready = _runtime_mapping(source.get("ready"), "overlay sourceCampaign.ready")
    if not source_path.is_dir():
        raise CampaignError("runtime-contract overlay source campaign is missing")
    actual_source_ready = coverage.file_stamp(source_path / "campaign.ready.json")
    if (
        actual_source_ready["bytes"] != source_ready.get("bytes")
        or actual_source_ready["sha256"] != source_ready.get("sha256")
    ):
        raise CampaignError("runtime-contract overlay source campaign READY has changed")
    verify(source_path)

    input_stamp = _runtime_mapping(receipt.get("inputContract"), "overlay inputContract")
    input_path = Path(str(input_stamp.get("path", ""))).resolve()
    if not input_path.is_file():
        raise CampaignError("runtime-contract overlay input contract is missing")
    actual_input = coverage.file_stamp(input_path)
    if (
        actual_input["bytes"] != input_stamp.get("bytes")
        or actual_input["sha256"] != input_stamp.get("sha256")
    ):
        raise CampaignError("runtime-contract overlay input contract has changed")
    artifacts = _runtime_list(receipt.get("artifacts"), "overlay artifacts")
    roles: set[str] = set()
    for index, raw in enumerate(artifacts):
        artifact = _runtime_mapping(raw, f"overlay artifacts[{index}]")
        role = str(artifact.get("role", "")).strip()
        relative = artifact.get("path")
        if not role or role in roles:
            raise CampaignError("runtime-contract overlay repeats or omits an artifact role")
        roles.add(role)
        if not isinstance(relative, str) or not relative.strip() or Path(relative).is_absolute():
            raise CampaignError(f"runtime-contract overlay artifact {role} has an invalid path")
        path = (input_path.parent / relative).resolve()
        if not path.is_file():
            raise CampaignError(f"runtime-contract overlay artifact is missing: {role}")
        actual_artifact = coverage.file_stamp(path)
        if (
            actual_artifact["bytes"] != artifact.get("bytes")
            or actual_artifact["sha256"] != artifact.get("sha256")
        ):
            raise CampaignError(f"runtime-contract overlay artifact has changed: {role}")
    output_path = out / "runtime-contracts.tsv"
    expected = receipt.get("output")
    if not output_path.is_file() or not isinstance(expected, dict):
        raise CampaignError("runtime-contract ledger is missing from disk/receipt")
    actual = coverage.file_stamp(output_path)
    if actual["bytes"] != expected.get("bytes") or actual["sha256"] != expected.get("sha256"):
        raise CampaignError("runtime-contract ledger disagrees with READY receipt")
    rows = _read_tsv(output_path)
    if len(rows) != receipt.get("count") or not rows:
        raise CampaignError("runtime-contract row count disagrees with READY receipt")
    if any(
        row["contractState"] != "RUNTIME_CANDIDATE_NEEDS_REFUTER"
        or row["semanticGrade"] != "C2_BOUNDED_RUNTIME"
        or row["refuterVerdict"] != "UNSCORED"
        for row in rows
    ):
        raise CampaignError("runtime-contract overlay bypasses the refuter gate")
    policy = receipt.get("policy", {})
    if (
        policy.get("namesAuthorized") is not False
        or policy.get("ghidraMutationAuthorized") is not False
        or policy.get("promotionAuthorized") is not False
        or policy.get("requiresRefuter") is not True
        or policy.get("artifactClaimsParsed") is not True
        or policy.get("runtimeExecutableRelationValidated") is not True
    ):
        raise CampaignError("runtime-contract overlay bypasses mutation/promotion policy")
    return receipt


def _append_state(value: str, state: str) -> str:
    states = [item for item in value.split(";") if item]
    if state not in states:
        states.append(state)
    return ";".join(states)


def _runtime_refuter_subject(overlay_row: dict[str, str], overlay_sha256: str) -> dict:
    canonical_row = json.dumps(
        overlay_row, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "schema": REFUTER_SUBJECT_SCHEMA,
        "baseContractId": overlay_row["baseContractId"],
        "entityKey": overlay_row["entityKey"],
        "overlayReadySha256": overlay_sha256,
        "questionIdsAddressed": [
            value
            for value in overlay_row.get("questionIdsAddressed", "").split(";")
            if value
        ],
        "candidateRowSha256": hashlib.sha256(canonical_row).hexdigest(),
    }


def _rebuild_source_fingerprint() -> dict[str, object]:
    rebuild_root = (REPO_ROOT / "rebuild").resolve()
    suffixes = {
        ".c", ".cc", ".cpp", ".cs", ".csproj", ".h", ".hpp", ".json",
        ".props", ".sln", ".targets",
    }
    rows: list[tuple[str, int, str]] = []
    for path in sorted(rebuild_root.rglob("*")):
        if (
            not path.is_file()
            or path.suffix.casefold() not in suffixes
            or any(part.casefold() in {"bin", "obj"} for part in path.parts)
        ):
            continue
        relative = path.relative_to(REPO_ROOT).as_posix()
        rows.append((relative, path.stat().st_size, coverage.sha256_of(path)))
    canonical = "".join(
        f"{sha256}\t{size}\t{relative}\n"
        for relative, size, sha256 in rows
    ).encode("utf-8")
    return {
        "count": len(rows),
        "bytes": sum(size for _relative, size, _sha256 in rows),
        "sha256": hashlib.sha256(canonical).hexdigest(),
    }


def _parse_dotnet_test_summary(text: str) -> tuple[int, int, int, int]:
    vstest_success = re.findall(r"(?m)^\s*Test Run Successful\.\s*$", text)
    vstest_total = re.findall(r"(?mi)^\s*Total tests:\s*(\d+)\s*$", text)
    vstest_passed = re.findall(r"(?mi)^\s*Passed:\s*(\d+)\s*$", text)
    vstest_failed = re.findall(r"(?mi)^\s*Failed:\s*(\d+)\s*$", text)
    vstest_skipped = re.findall(r"(?mi)^\s*Skipped:\s*(\d+)\s*$", text)
    if vstest_success or vstest_total or vstest_passed:
        if (
            len(vstest_success) != 1
            or len(vstest_total) != 1
            or len(vstest_passed) != 1
            or len(vstest_failed) > 1
            or len(vstest_skipped) > 1
        ):
            raise CampaignError("rebuild-ready VSTest summary is missing or ambiguous")
        total = int(vstest_total[0])
        passed = int(vstest_passed[0])
        failed = int(vstest_failed[0]) if vstest_failed else 0
        skipped = int(vstest_skipped[0]) if vstest_skipped else 0
        if total != passed + failed + skipped:
            raise CampaignError("rebuild-ready VSTest summary counts are inconsistent")
        return failed, passed, skipped, total

    patterns = (
        re.compile(
            r"Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)",
            re.IGNORECASE,
        ),
        re.compile(
            r"total:\s*(\d+),\s*failed:\s*(\d+),\s*succeeded:\s*(\d+),\s*skipped:\s*(\d+)",
            re.IGNORECASE,
        ),
    )
    first = patterns[0].search(text)
    if first is not None:
        failed, passed, skipped, total = (int(value) for value in first.groups())
        return failed, passed, skipped, total
    second = patterns[1].search(text)
    if second is not None:
        total, failed, passed, skipped = (int(value) for value in second.groups())
        return failed, passed, skipped, total
    raise CampaignError("rebuild-ready runner output lacks an exact test summary")


def _run_rebuild_test(argv: list[str]) -> dict[str, object]:
    try:
        completed = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=300,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CampaignError(f"rebuild-ready runner could not execute: {exc}") from exc
    output = f"{completed.stdout}\n{completed.stderr}".replace("\r\n", "\n")
    if completed.returncode != 0:
        raise CampaignError(
            f"rebuild-ready runner exited {completed.returncode}: {output[-500:]}"
        )
    if "No test matches" in output or "No test is available" in output:
        raise CampaignError("rebuild-ready runner selected no tests")
    try:
        filter_index = argv.index("--filter")
        filter_value = argv[filter_index + 1]
    except (ValueError, IndexError) as exc:
        raise CampaignError("rebuild-ready runner lacks its exact test filter") from exc
    prefix = "FullyQualifiedName="
    if not filter_value.startswith(prefix) or filter_value[len(prefix):] not in output:
        raise CampaignError("rebuild-ready runner output does not name its selected test")
    failed, passed, skipped, total = _parse_dotnet_test_summary(output)
    return {
        "exitCode": completed.returncode,
        "failed": failed,
        "passed": passed,
        "skipped": skipped,
        "total": total,
    }


def _validate_rebuild_ready_gate(
    decision: dict,
    adjudication_path: Path,
    overlay_row: dict[str, str],
    overlay_sha256: str,
) -> None:
    gate = _runtime_mapping(decision.get("rebuildGate"), "rebuild-ready gate")
    expected_gate_keys = {
        "schema", "runner", "owner", "implementation", "test", "testName",
        "project", "expectedTests", "result",
    }
    if gate.get("schema") != REBUILD_GATE_SCHEMA or set(gate) != expected_gate_keys:
        raise CampaignError("REBUILD_READY lacks a supported rebuild gate")
    if gate.get("runner") != "dotnet-test-v1":
        raise CampaignError("REBUILD_READY names an unsupported gate runner")
    stamped: dict[str, tuple[Path, dict]] = {}
    rebuild_root = (REPO_ROOT / "rebuild").resolve()
    for role in ("owner", "test", "project"):
        spec = _runtime_mapping(gate.get(role), f"rebuild-ready {role}")
        if set(spec) != {"path", "bytes", "sha256"}:
            raise CampaignError(f"rebuild-ready {role} stamp is not exact")
        raw_path = spec.get("path")
        if not isinstance(raw_path, str) or not raw_path or Path(raw_path).is_absolute():
            raise CampaignError(f"rebuild-ready {role} must be repository-relative")
        path = (REPO_ROOT / raw_path).resolve()
        try:
            path.relative_to(rebuild_root)
        except ValueError as exc:
            raise CampaignError(f"rebuild-ready {role} is outside rebuild/") from exc
        stamped[role] = (
            path,
            _require_file_stamp(path, spec, f"rebuild-ready {role}"),
        )
    if stamped["project"][0].suffix.casefold() != ".csproj":
        raise CampaignError("dotnet rebuild-ready project is not a .csproj")

    mapping = _runtime_mapping(
        decision.get("rebuildMapping"), "adjudication rebuildMapping"
    )
    owner_relative = stamped["owner"][0].relative_to(REPO_ROOT).as_posix()
    implementation = str(gate.get("implementation", "")).strip()
    test_name = str(gate.get("testName", "")).strip()
    if (
        not all(
            isinstance(mapping.get(field), str)
            for field in (
                "rebuildOwner", "rebuildImplementation", "parityTests", "rebuildState"
            )
        )
        or mapping.get("rebuildOwner", "").replace("\\", "/") != owner_relative
        or mapping.get("rebuildImplementation") != implementation
        or mapping.get("parityTests") != test_name
        or mapping.get("rebuildState") != "REBUILD_READY"
    ):
        raise CampaignError("REBUILD_READY gate is not joined to its rebuild mapping")
    if (
        not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.+`]*", implementation)
        or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.+`]*", test_name)
    ):
        raise CampaignError("REBUILD_READY implementation/test symbol is malformed")
    owner_text = stamped["owner"][0].read_text(encoding="utf-8", errors="replace")
    test_text = stamped["test"][0].read_text(encoding="utf-8", errors="replace")
    if not re.search(rf"\b{re.escape(implementation.rsplit('.', 1)[-1])}\b", owner_text):
        raise CampaignError("REBUILD_READY implementation is absent from its owner")
    if not re.search(rf"\b{re.escape(test_name.rsplit('.', 1)[-1])}\b", test_text):
        raise CampaignError("REBUILD_READY test symbol is absent from its test source")
    expected_tests = gate.get("expectedTests")
    if not isinstance(expected_tests, int) or expected_tests < 1:
        raise CampaignError("REBUILD_READY expectedTests must be a positive integer")

    dotnet_raw = shutil.which("dotnet")
    if dotnet_raw is None:
        raise CampaignError("REBUILD_READY dotnet runner is unavailable")
    dotnet = Path(dotnet_raw).resolve()
    dotnet_stamp = {
        "path": str(dotnet),
        "bytes": dotnet.stat().st_size,
        "sha256": coverage.sha256_of(dotnet),
    }
    argv = [
        str(dotnet),
        "test",
        str(stamped["project"][0]),
        "--no-restore",
        "--filter",
        f"FullyQualifiedName={test_name}",
        "--logger",
        "console;verbosity=normal",
    ]
    source_fingerprint = _rebuild_source_fingerprint()
    result_spec = _runtime_mapping(gate.get("result"), "rebuild-ready result")
    if set(result_spec) != {"path", "bytes", "sha256"}:
        raise CampaignError("rebuild-ready result stamp is not exact")
    result_path = _runtime_artifact_path(
        adjudication_path, result_spec.get("path"), "rebuild-ready result"
    )
    _require_file_stamp(result_path, result_spec, "rebuild-ready result")
    result = _runtime_json(result_path, "rebuild-ready result")
    expected = {
        "schema": REBUILD_RESULT_SCHEMA,
        "baseContractId": overlay_row["baseContractId"],
        "entityKey": overlay_row["entityKey"],
        "overlayReadySha256": overlay_sha256,
        "ownerSha256": stamped["owner"][1]["sha256"],
        "testSha256": stamped["test"][1]["sha256"],
        "projectSha256": stamped["project"][1]["sha256"],
        "implementation": implementation,
        "testName": test_name,
        "expectedTests": expected_tests,
        "rebuildSource": source_fingerprint,
        "dotnet": dotnet_stamp,
        "cwd": str(REPO_ROOT),
        "argv": argv,
    }
    expected_result_keys = set(expected) | {
        "exitCode", "failed", "passed", "skipped", "total"
    }
    if set(result) != expected_result_keys or any(
        result.get(key) != value for key, value in expected.items()
    ):
        raise CampaignError("REBUILD_READY result does not reproduce its subject/gate")
    replay = _run_rebuild_test(argv)
    if _rebuild_source_fingerprint() != source_fingerprint:
        raise CampaignError("REBUILD_READY source tree changed during parity replay")
    for role, (path, before_stamp) in stamped.items():
        after_stamp = coverage.file_stamp(path)
        if (
            after_stamp["bytes"] != before_stamp["bytes"]
            or after_stamp["sha256"] != before_stamp["sha256"]
        ):
            raise CampaignError(f"REBUILD_READY {role} changed during parity replay")
    result_after = coverage.file_stamp(result_path)
    if (
        result_after["bytes"] != result_spec["bytes"]
        or result_after["sha256"] != result_spec["sha256"]
    ):
        raise CampaignError("REBUILD_READY result changed during parity replay")
    expected_summary = {
        "exitCode": 0,
        "failed": 0,
        "passed": expected_tests,
        "skipped": 0,
        "total": expected_tests,
    }
    if replay != expected_summary or any(
        result.get(key) != value for key, value in expected_summary.items()
    ):
        raise CampaignError("REBUILD_READY focused parity test did not reproduce")


def _promotion_artifact(
    evidence_path: Path,
    value: object,
    label: str,
    *,
    content_fallback: Path | None = None,
) -> tuple[Path, dict]:
    spec = _runtime_mapping(value, f"Ghidra promotion {label}")
    relative = spec.get("path")
    if not isinstance(relative, str) or not relative.strip() or Path(relative).is_absolute():
        raise CampaignError(f"Ghidra promotion {label} must use a repository-relative path")
    artifact = (REPO_ROOT / Path(relative)).resolve()
    try:
        artifact.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise CampaignError(f"Ghidra promotion {label} escapes the repository") from exc
    stamp = coverage.file_stamp(artifact) if artifact.is_file() else None
    if stamp is None or stamp["bytes"] != spec.get("bytes") or stamp["sha256"] != spec.get("sha256"):
        if content_fallback is None:
            reason = "missing" if stamp is None else "changed"
            raise CampaignError(f"Ghidra promotion {label} artifact has {reason}: {artifact}")
        fallback = content_fallback.resolve()
        try:
            fallback.relative_to(REPO_ROOT)
        except ValueError as exc:
            raise CampaignError(f"Ghidra promotion {label} fallback escapes the repository") from exc
        if not fallback.is_file():
            raise CampaignError(f"Ghidra promotion {label} historical snapshot is missing")
        fallback_stamp = coverage.file_stamp(fallback)
        if (
            fallback_stamp["bytes"] != spec.get("bytes")
            or fallback_stamp["sha256"] != spec.get("sha256")
        ):
            raise CampaignError(f"Ghidra promotion {label} historical snapshot has changed")
        artifact = fallback
        stamp = fallback_stamp
    return artifact, {**stamp, "path": relative}


def _promotion_owned_artifact(
    owner_path: Path,
    value: object,
    label: str,
) -> tuple[Path, dict]:
    spec = _runtime_mapping(value, f"Ghidra promotion {label}")
    relative = spec.get("path")
    if not isinstance(relative, str) or not relative.strip() or Path(relative).is_absolute():
        raise CampaignError(f"Ghidra promotion {label} must be relative to its receipt")
    artifact = (owner_path.parent / Path(relative)).resolve()
    try:
        artifact.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise CampaignError(f"Ghidra promotion {label} escapes the repository") from exc
    if not artifact.is_file():
        raise CampaignError(f"Ghidra promotion {label} artifact is missing: {artifact}")
    stamp = coverage.file_stamp(artifact)
    if stamp["bytes"] != spec.get("bytes") or stamp["sha256"] != spec.get("sha256"):
        raise CampaignError(f"Ghidra promotion {label} artifact has changed")
    return artifact, {**stamp, "path": relative}


def _promotion_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"Ghidra promotion {label} is not valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CampaignError(f"Ghidra promotion {label} root is not an object")
    return value


def _promotion_output_from_ready(
    ready: dict,
    *,
    expected_path: Path,
    expected_stamp: dict,
    label: str,
) -> None:
    output = _runtime_mapping(ready.get("output"), f"Ghidra promotion {label}.output")
    try:
        declared = Path(str(output.get("path", ""))).resolve()
    except OSError as exc:
        raise CampaignError(f"Ghidra promotion {label} output path is invalid") from exc
    if declared != expected_path.resolve():
        raise CampaignError(f"Ghidra promotion {label} READY names another output")
    if (
        output.get("bytes") != expected_stamp["bytes"]
        or output.get("sha256") != expected_stamp["sha256"]
    ):
        raise CampaignError(f"Ghidra promotion {label} READY output stamp is inconsistent")


def _validate_promotion_ready(
    ready: dict,
    *,
    required_schema: str,
    mode: str,
    target_path: Path,
    target_sha256: str,
    target_bytes: int,
    target_count: int,
    semantic_target_sha256: str,
    tool_path: Path,
    tool_stamp: dict,
    output_path: Path,
    output_stamp: dict,
    label: str,
) -> None:
    if ready.get("schemaVersion") != required_schema:
        raise CampaignError(f"Ghidra promotion {label} has an unsupported READY schema")
    if ready.get("mode") != mode:
        raise CampaignError(f"Ghidra promotion {label} mode mismatch")
    program = _runtime_mapping(ready.get("program"), f"Ghidra promotion {label}.program")
    expected_program = {
        "name": "BEA.exe",
        "executableMd5": "3b456964020070efe696d2cc09464a55",
        "imageBase": "0x00400000",
        "language": "x86:LE:32:default",
        "compilerSpec": "windows",
    }
    if required_schema == GHIDRA_PROMOTION_READY_SCHEMA:
        expected_program["executableSha256"] = (
            "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
        )
        tool = _runtime_mapping(ready.get("tool"), f"Ghidra promotion {label}.tool")
        try:
            declared_tool_path = Path(str(tool.get("path", ""))).resolve()
        except OSError as exc:
            raise CampaignError(f"Ghidra promotion {label} tool path is invalid") from exc
        if (
            declared_tool_path != tool_path.resolve()
            or tool.get("bytes") != tool_stamp["bytes"]
            or tool.get("sha256") != tool_stamp["sha256"]
        ):
            raise CampaignError(f"Ghidra promotion {label} names another executed tool")
    if any(program.get(key) != value for key, value in expected_program.items()):
        raise CampaignError(f"Ghidra promotion {label} names another program identity")
    input_spec = _runtime_mapping(ready.get("input"), f"Ghidra promotion {label}.input")
    try:
        declared_input_path = Path(str(input_spec.get("path", ""))).resolve()
    except OSError as exc:
        raise CampaignError(f"Ghidra promotion {label} input path is invalid") from exc
    if (
        declared_input_path != target_path.resolve()
        or input_spec.get("bytes") != target_bytes
        or input_spec.get("sha256") != target_sha256
        or input_spec.get("expectedCount") != target_count
        or input_spec.get("semanticTargetSetSha256") != semantic_target_sha256
    ):
        raise CampaignError(f"Ghidra promotion {label} names another target set")
    counts = _runtime_mapping(ready.get("counts"), f"Ghidra promotion {label}.counts")
    expected_counts = {
        "dry": {
            "targets": target_count,
            "wouldCreate": target_count,
            "created": 0,
            "alreadyExists": 0,
            "verified": 0,
        },
        "apply": {
            "targets": target_count,
            "wouldCreate": 0,
            "created": target_count,
            "alreadyExists": 0,
            "verified": target_count,
        },
        "readback": {
            "targets": target_count,
            "wouldCreate": 0,
            "created": 0,
            "alreadyExists": 0,
            "verified": target_count,
        },
    }[mode]
    if required_schema == GHIDRA_PROMOTION_READY_SCHEMA:
        before = counts.get("programInstructionsBefore")
        after = counts.get("programInstructionsAfter")
        if (
            not isinstance(before, int)
            or before <= 0
            or after != before
            or set(counts) != set(expected_counts) | {
                "programInstructionsBefore", "programInstructionsAfter"
            }
            or any(counts.get(key) != value for key, value in expected_counts.items())
        ):
            raise CampaignError(
                f"Ghidra promotion {label} instruction/count accounting is not exact"
            )
    elif counts != expected_counts:
        raise CampaignError(f"Ghidra promotion {label} count accounting is not exact")
    if ready.get("namesAuthorized") is not False:
        raise CampaignError(f"Ghidra promotion {label} authorized semantic names")
    if ready.get("mutationCommitted") is not (mode == "apply"):
        raise CampaignError(f"Ghidra promotion {label} mutation flag is inconsistent")
    if ready.get("allTargetsVerified") is not (mode in {"apply", "readback"}):
        raise CampaignError(f"Ghidra promotion {label} verification flag is inconsistent")
    _promotion_output_from_ready(
        ready,
        expected_path=output_path,
        expected_stamp=output_stamp,
        label=label,
    )


def _validate_promotion_log(
    text: str,
    *,
    ready_schema: str,
    mode: str,
    target_path: Path,
    target_sha256: str,
    target_count: int,
    output_path: Path,
    ready_path: Path,
    tool_path: Path,
    tool_stamp: dict,
    expected_project_root: Path,
    project_name: str,
    require_save: bool,
    label: str,
) -> None:
    sentinels = {
        "dry": (
            f"FUNCTION_PROMOTION_OK mode=dry targets={target_count} "
            f"would_create={target_count} created=0 already_exists=0 verified=0 "
            "mutation_committed=false"
        ),
        "apply": (
            f"FUNCTION_PROMOTION_OK mode=apply targets={target_count} "
            f"would_create=0 created={target_count} already_exists=0 "
            f"verified={target_count} mutation_committed=true"
        ),
        "readback": (
            f"FUNCTION_PROMOTION_OK mode=readback targets={target_count} "
            f"would_create=0 created=0 already_exists=0 verified={target_count} "
            "mutation_committed=false"
        ),
    }
    if text.count(sentinels[mode]) != 1:
        raise CampaignError(f"Ghidra promotion {label} lacks the exact success sentinel")
    if any(
        marker in text
        for marker in (
            "REPORT SCRIPT ERROR",
            "FUNCTION_PROMOTION_FAIL",
            "FUNCTION_PROMOTION_RECEIPT_LOST",
            "Exception",
        )
    ):
        raise CampaignError(f"Ghidra promotion {label} contains a script error marker")
    if require_save and "Save succeeded for processed file: /BEA.exe" not in text:
        raise CampaignError(f"Ghidra promotion {label} lacks the project-save sentinel")
    expected_open = (
        f"Opening existing project: {expected_project_root.resolve() / project_name} "
        "(HeadlessAnalyzer)"
    )
    if text.count(expected_open) != 1:
        raise CampaignError(f"Ghidra promotion {label} opened another project path")
    expected_execute = (
        "REPORT: Execute script: CreateFunctionsFromAddressList.java "
        f"'{target_path.resolve()}' '{target_sha256}' '{target_count}' "
        f"'{output_path.resolve()}' '{ready_path.resolve()}' '{mode}'"
    )
    expected_script = f"SCRIPT: {tool_path.resolve()} (HeadlessAnalyzer)"
    if text.count(expected_execute) != 1 or text.count(expected_script) != 1:
        raise CampaignError(f"Ghidra promotion {label} log names another invocation/tool")
    if ready_schema == GHIDRA_PROMOTION_READY_SCHEMA:
        tool_sentinel = (
            f"FUNCTION_PROMOTION_TOOL_OK path={tool_path.resolve()} "
            f"bytes={tool_stamp['bytes']} sha256={tool_stamp['sha256']}"
        )
        if text.count(tool_sentinel) != 1:
            raise CampaignError(f"Ghidra promotion {label} lacks measured tool identity")
    read_only_marker = "REPORT: Processing read-only project file: /BEA.exe"
    writable_marker = "REPORT: Processing project file: /BEA.exe"
    if mode == "apply":
        if writable_marker not in text or read_only_marker in text:
            raise CampaignError(f"Ghidra promotion {label} was not one writable apply")
    elif read_only_marker not in text:
        raise CampaignError(f"Ghidra promotion {label} was not read-only")
    program_sentinel = (
        "FUNCTION_PROMOTION_PROGRAM_OK name=BEA.exe "
        "md5=3b456964020070efe696d2cc09464a55 "
    )
    if ready_schema == GHIDRA_PROMOTION_READY_SCHEMA:
        program_sentinel += (
            "sha256=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750 "
        )
    program_sentinel += (
        "imageBase=0x00400000 language=x86:LE:32:default compiler=windows"
    )
    if text.count(program_sentinel) != 1:
        raise CampaignError(f"Ghidra promotion {label} lacks measured program identity")


def _promotion_rows(path: Path, key: str, label: str) -> dict[str, dict[str, str]]:
    rows = _read_tsv(path)
    values = [row.get(key, "") for row in rows]
    if any(not value for value in values) or len(values) != len(set(values)):
        raise CampaignError(f"Ghidra promotion {label} has missing or duplicate {key} rows")
    return {row[key].lower(): row for row in rows}


def _manifest_file_rows(value: object, label: str) -> list[tuple[str, int, str]]:
    manifest = _runtime_mapping(value, f"Ghidra promotion {label}")
    files = _runtime_list(manifest.get("files"), f"Ghidra promotion {label}.files")
    rows: list[tuple[str, int, str]] = []
    for index, raw in enumerate(files):
        row = _runtime_mapping(raw, f"Ghidra promotion {label}.files[{index}]")
        relative = str(row.get("relative_path", ""))
        size = row.get("size")
        sha256 = str(row.get("sha256", ""))
        if (
            not relative
            or not isinstance(size, int)
            or size < 0
            or not re.fullmatch(r"[0-9a-f]{64}", sha256)
        ):
            raise CampaignError(f"Ghidra promotion {label} has an invalid project file row")
        rows.append((relative, size, sha256))
    if len(rows) != len(set(row[0] for row in rows)):
        raise CampaignError(f"Ghidra promotion {label} repeats a project file")
    if manifest.get("fileCount") != len(rows) or manifest.get("totalBytes") != sum(row[1] for row in rows):
        raise CampaignError(f"Ghidra promotion {label} project totals are inconsistent")
    if manifest.get("projectName") != "BEA" or manifest.get("structurallyComplete") is not True:
        raise CampaignError(f"Ghidra promotion {label} project identity/structure is invalid")
    return rows


def _manifest_root(value: object, label: str) -> Path:
    manifest = _runtime_mapping(value, f"Ghidra promotion {label}")
    raw = manifest.get("root")
    if not isinstance(raw, str) or not raw.strip() or not Path(raw).is_absolute():
        raise CampaignError(f"Ghidra promotion {label} has no absolute project root")
    return Path(raw).resolve()


def _validate_poisoned_sha_semantic_stability(
    *,
    reported_raw_project_changed: object,
    pre_project_rows: list[tuple[str, int, str]],
    post_project_rows: list[tuple[str, int, str]],
    before_functions_stamp: dict,
    after_functions_stamp: dict,
    before_program_stamp: dict,
    after_program_stamp: dict,
) -> bool:
    raw_project_changed = pre_project_rows != post_project_rows
    if reported_raw_project_changed is not raw_project_changed:
        raise CampaignError(
            "Ghidra poisoned-SHA raw-project observation disagrees with its manifests"
        )
    if (
        before_functions_stamp.get("sha256") != after_functions_stamp.get("sha256")
        or before_program_stamp.get("sha256") != after_program_stamp.get("sha256")
    ):
        raise CampaignError(
            "Ghidra poisoned-SHA control changed the semantic function/program inventory"
        )
    return raw_project_changed


def _parse_utc_timestamp(value: object, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise CampaignError(f"Ghidra promotion {label} has no timestamp")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise CampaignError(f"Ghidra promotion {label} has an invalid timestamp") from exc
    if parsed.tzinfo is None:
        raise CampaignError(f"Ghidra promotion {label} timestamp has no timezone")
    return parsed.astimezone(timezone.utc)


def _local_scratch_project_root(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value.strip() or not Path(value).is_absolute():
        raise CampaignError(f"Ghidra promotion {label} has no absolute scratch project root")
    root = Path(value).resolve()
    try:
        root.relative_to((REPO_ROOT / "local-lab").resolve())
    except ValueError as exc:
        raise CampaignError(f"Ghidra promotion {label} is outside local-lab") from exc
    return root


def _require_distinct_artifact_paths(values: dict[str, Path]) -> None:
    by_path: dict[Path, list[str]] = {}
    for label, path in values.items():
        by_path.setdefault(path.resolve(), []).append(label)
    aliases = {path: labels for path, labels in by_path.items() if len(labels) > 1}
    if aliases:
        details = "; ".join(
            f"{path}: {', '.join(labels)}"
            for path, labels in sorted(aliases.items(), key=lambda item: str(item[0]))
        )
        raise CampaignError(f"Ghidra promotion aliases independent artifacts: {details}")


def _verify_project_manifest_bytes(
    root: Path,
    expected_rows: list[tuple[str, int, str]],
    project_name: str,
    label: str,
    *,
    require_single_link: bool = False,
) -> None:
    try:
        actual = ghidra_backup.build_manifest(root, project_name)
    except (ghidra_backup.BackupError, OSError) as exc:
        raise CampaignError(f"Ghidra promotion {label} cannot be rehashed: {exc}") from exc
    actual_rows = [
        (row.relative_path, row.size, row.sha256)
        for row in actual.files
    ]
    if actual_rows != expected_rows:
        raise CampaignError(f"Ghidra promotion {label} bytes differ from the stamped manifest")
    if require_single_link:
        for relative, _size, _digest in expected_rows:
            try:
                path = ghidra_backup.resolve_plain_path(
                    root / Path(relative), f"Ghidra promotion {label}", strict=True
                )
                link_count = path.stat().st_nlink
            except (ghidra_backup.BackupError, OSError) as exc:
                raise CampaignError(
                    f"Ghidra promotion {label} file identity cannot be read: {exc}"
                ) from exc
            if link_count != 1:
                raise CampaignError(
                    f"Ghidra promotion {label} contains a hardlinked project file: {relative}"
                )


def _require_empty_manifest_comparison(value: object, label: str) -> None:
    comparison = _runtime_mapping(value, f"Ghidra promotion {label}")
    expected = {
        "matches": True,
        "missing": [],
        "extra": [],
        "sizeDifferences": [],
        "hashDifferences": [],
        "missingCount": 0,
        "extraCount": 0,
        "sizeDiffCount": 0,
        "hashDiffCount": 0,
    }
    if comparison != expected:
        raise CampaignError(f"Ghidra promotion {label} is not an exact empty manifest diff")


def _validate_inventory_log(
    text: str,
    *,
    expected_project_root: Path,
    project_name: str,
    expected_function_count: int,
    functions_path: Path,
    program_path: Path,
    tool_path: Path,
    tool_stamp: dict | None,
    label: str,
) -> None:
    expected_open = (
        f"Opening existing project: {expected_project_root.resolve() / project_name} "
        "(HeadlessAnalyzer)"
    )
    expected_inventory = f"INVENTORY_OK functions={expected_function_count} "
    expected_execute = (
        "REPORT: Execute script: ExportFullFunctionInventory.java "
        f"'{functions_path.resolve()}' '{program_path.resolve()}'"
    )
    expected_script = f"SCRIPT: {tool_path.resolve()} (HeadlessAnalyzer)"
    if (
        text.count(expected_open) != 1
        or "REPORT: Processing read-only project file: /BEA.exe" not in text
        or text.count(expected_inventory) != 1
        or text.count(expected_execute) != 1
        or text.count(expected_script) != 1
        or any(marker in text for marker in ("REPORT SCRIPT ERROR", "INVENTORY_FAIL", "Exception"))
    ):
        raise CampaignError(f"Ghidra promotion {label} inventory export is not exact/read-only")
    if tool_stamp is not None:
        expected_tool = (
            f"INVENTORY_TOOL_OK path={tool_path.resolve()} "
            f"bytes={tool_stamp['bytes']} sha256={tool_stamp['sha256']}"
        )
        if text.count(expected_tool) != 1:
            raise CampaignError(
                f"Ghidra promotion {label} inventory lacks measured tool identity"
            )


def validate_ghidra_promotion_evidence(
    evidence_path: Path,
    campaign: Path | None = None,
    *,
    _verified_campaign_receipt: dict | None = None,
) -> dict:
    """Reproduce a live boundary promotion from its hash-bound receipts and exports."""
    evidence_path = evidence_path.resolve()
    evidence = _promotion_json(evidence_path, "evidence envelope")
    evidence_stamp = coverage.file_stamp(evidence_path)
    evidence_schema = evidence.get("schema")
    legacy_evidence = evidence_schema == LEGACY_GHIDRA_PROMOTION_EVIDENCE_SCHEMA
    if legacy_evidence:
        if evidence_stamp["sha256"] != LEGACY_GHIDRA_PROMOTION_EVIDENCE_SHA256:
            raise CampaignError("unrecognized legacy Ghidra promotion evidence")
        ready_schema = LEGACY_GHIDRA_PROMOTION_READY_SCHEMA
        backup_schema = LEGACY_GHIDRA_PROJECT_BACKUP_SCHEMA
    elif evidence_schema == GHIDRA_PROMOTION_EVIDENCE_SCHEMA:
        ready_schema = GHIDRA_PROMOTION_READY_SCHEMA
        backup_schema = GHIDRA_PROJECT_BACKUP_SCHEMA
    else:
        raise CampaignError(f"unsupported Ghidra promotion evidence: {evidence.get('schema')!r}")
    if evidence.get("verdict") != "SURVIVED":
        raise CampaignError("only a SURVIVED Ghidra promotion can advance the campaign")
    measured_at = str(evidence.get("measuredAtUtc", ""))
    evidence_time = _parse_utc_timestamp(measured_at, "evidence measurement")

    campaign_ready_path, campaign_stamp = _promotion_artifact(
        evidence_path, evidence.get("campaign"), "campaign READY"
    )
    if campaign_ready_path.name != "campaign.ready.json":
        raise CampaignError("Ghidra promotion campaign artifact is not a READY receipt")
    source_campaign = campaign_ready_path.parent
    if campaign is not None and source_campaign.resolve() != campaign.resolve():
        raise CampaignError("Ghidra promotion evidence names another campaign")
    base_receipt = (
        _verified_campaign_receipt
        if _verified_campaign_receipt is not None
        else verify(source_campaign)
    )

    prereg_path, prereg_stamp = _promotion_artifact(
        evidence_path, evidence.get("preregistration"), "preregistration"
    )
    prereg = _promotion_json(prereg_path, "preregistration")
    if prereg.get("schema") != "bea.re.ghidra-function-promotion-preregistration.v1":
        raise CampaignError("Ghidra promotion preregistration schema is unsupported")

    program = _runtime_mapping(evidence.get("program"), "Ghidra promotion program")
    expected_program = {
        "projectName": "BEA",
        "programName": "BEA.exe",
        "executableMd5": "3b456964020070efe696d2cc09464a55",
        "imageBase": "0x00400000",
        "language": "x86:LE:32:default",
        "compilerSpec": "windows",
    }
    if not legacy_evidence:
        expected_program["executableSha256"] = (
            "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
        )
    if any(program.get(key) != value for key, value in expected_program.items()):
        raise CampaignError("Ghidra promotion evidence names another program identity")
    project_root_raw = program.get("projectRoot")
    if (
        not isinstance(project_root_raw, str)
        or not project_root_raw.strip()
        or not Path(project_root_raw).is_absolute()
    ):
        raise CampaignError("Ghidra promotion has no absolute maintainer project root")
    live_project_root = Path(project_root_raw).resolve()
    try:
        live_project_root.relative_to(REPO_ROOT)
    except ValueError:
        pass
    else:
        raise CampaignError("Ghidra maintainer project root is inside the repository/scratch scope")
    prereg_program = _runtime_mapping(prereg.get("program"), "preregistered Ghidra program")
    prereg_expected = {
        **expected_program,
        "projectRoot": str(live_project_root),
        "specimenSha256": "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
    }
    if any(prereg_program.get(key) != value for key, value in prereg_expected.items()):
        raise CampaignError("Ghidra promotion preregistered another maintainer program/project")
    specimen_path, specimen_stamp = _promotion_artifact(
        evidence_path, program.get("specimen"), "pristine specimen"
    )
    if specimen_stamp["sha256"] != "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750":
        raise CampaignError("Ghidra promotion evidence is not bound to the pristine specimen")
    if base_receipt.get("sourceSnapshot", {}).get("specimen", {}).get("sha256") != specimen_stamp["sha256"]:
        raise CampaignError("Ghidra promotion specimen differs from the campaign specimen")

    targets = _runtime_mapping(evidence.get("targets"), "Ghidra promotion targets")
    boundary_ready_path, boundary_ready_stamp = _promotion_artifact(
        evidence_path, targets.get("ready"), "boundary READY"
    )
    target_path, target_stamp = _promotion_artifact(
        evidence_path, targets.get("list"), "boundary target list"
    )
    boundary_ready = verify_boundary_export(boundary_ready_path.parent)
    if target_path != boundary_ready_path.parent / "boundary-targets.txt":
        raise CampaignError("Ghidra promotion target list is not owned by the boundary READY")
    target_spec = _runtime_mapping(targets.get("list"), "Ghidra promotion target list")
    target_count = target_spec.get("count")
    semantic_target_sha = str(target_spec.get("semanticTargetSetSha256", ""))
    if (
        not isinstance(target_count, int)
        or target_count <= 0
        or target_spec.get("namesAuthorized") is not False
        or (legacy_evidence and target_count != 40)
    ):
        raise CampaignError("Ghidra promotion target count/naming policy is not the reviewed cohort")
    addresses = target_path.read_text(encoding="ascii").splitlines()
    if (
        len(addresses) != target_count
        or len(addresses) != len(set(addresses))
        or any(not re.fullmatch(r"0x[0-9a-f]{8}", address) for address in addresses)
        or [row.get("address") for row in boundary_ready.get("targets", [])] != addresses
    ):
        raise CampaignError("Ghidra promotion target list is not exact and unique")
    canonical_target_bytes = "".join(f"{address}\n" for address in sorted(addresses)).encode("ascii")
    if hashlib.sha256(canonical_target_bytes).hexdigest() != semantic_target_sha:
        raise CampaignError("Ghidra promotion semantic target-set hash is inconsistent")

    tool_spec = _runtime_mapping(evidence.get("tool"), "Ghidra promotion tool")
    tool_declared_path = (REPO_ROOT / Path(str(tool_spec.get("path", "")))).resolve()
    tool_path, tool_stamp = _promotion_artifact(
        evidence_path,
        tool_spec,
        "promotion tool",
        content_fallback=LEGACY_GHIDRA_PROMOTION_TOOL_SNAPSHOT if legacy_evidence else None,
    )
    if legacy_evidence:
        if tool_stamp["sha256"] != LEGACY_GHIDRA_PROMOTION_TOOL_SHA256:
            raise CampaignError("legacy Ghidra promotion used another mutation tool")
    else:
        try:
            tool_path.relative_to(evidence_path.parent)
        except ValueError as exc:
            raise CampaignError("Ghidra promotion tool was not snapshotted with its evidence") from exc
    executed_tool_path = tool_declared_path if legacy_evidence else tool_path
    if legacy_evidence:
        inventory_tool_path = (REPO_ROOT / "tools" / "ExportFullFunctionInventory.java").resolve()
        inventory_tool_stamp = None
    else:
        inventory_tool_path, inventory_tool_stamp = _promotion_artifact(
            evidence_path, evidence.get("inventoryTool"), "inventory export tool"
        )
        try:
            inventory_tool_path.relative_to(evidence_path.parent)
        except ValueError as exc:
            raise CampaignError(
                "Ghidra inventory export tool was not snapshotted with its evidence"
            ) from exc

    backup = _runtime_mapping(evidence.get("backup"), "Ghidra promotion backup")
    backup_manifest_path, backup_manifest_stamp = _promotion_artifact(
        evidence_path, backup.get("manifest"), "backup manifest"
    )
    backup_open_path, backup_open_stamp = _promotion_artifact(
        evidence_path, backup.get("openVerification"), "backup open verification"
    )
    backup_manifest = _promotion_json(backup_manifest_path, "backup manifest")
    backup_open = _promotion_json(backup_open_path, "backup open verification")
    if (
        backup_manifest.get("schemaVersion") != backup_schema
        or backup_manifest.get("sourceStable") is not True
        or backup_manifest.get("copyComparison", {}).get("matches") is not True
        or backup_manifest.get("readonlyOpen") is not None
        or backup_open.get("schemaVersion") != backup_schema
        or backup_open.get("sourceStable") is not True
        or backup_open.get("copyComparison", {}).get("matches") is not True
        or backup_open.get("readonlyOpen", {}).get("opened") is not True
        or backup_open.get("readonlyOpen", {}).get("contentStable") is not True
        or backup_open.get("readonlyOpen", {}).get("expectedProgramMd5")
        != expected_program["executableMd5"]
        or backup_open.get("readonlyOpen", {}).get("postOpenComparison", {}).get("matches") is not True
    ):
        raise CampaignError("Ghidra promotion lacks a stable, hash-equal, openable backup")
    _require_empty_manifest_comparison(
        backup_manifest.get("copyComparison"), "backup copy comparison"
    )
    _require_empty_manifest_comparison(
        backup_open.get("copyComparison"), "backup verification copy comparison"
    )
    readonly_open_value = _runtime_mapping(
        backup_open.get("readonlyOpen"), "Ghidra backup readonly open"
    )
    _require_empty_manifest_comparison(
        readonly_open_value.get("postOpenComparison"), "backup post-open comparison"
    )
    if readonly_open_value.get("exitCode") != 0:
        raise CampaignError("Ghidra backup read-only open did not exit cleanly")
    backup_source_rows = _manifest_file_rows(backup_manifest.get("source"), "backup source")
    if backup_source_rows != _manifest_file_rows(backup_manifest.get("destination"), "backup destination"):
        raise CampaignError("Ghidra promotion backup source/destination manifests differ")
    if backup_source_rows != _manifest_file_rows(backup_open.get("source"), "open-verified backup"):
        raise CampaignError("Ghidra promotion open verification names another backup")
    backup_root = _manifest_root(backup_open.get("source"), "open-verified backup")
    if backup_root != backup_manifest_path.parent.resolve():
        raise CampaignError("Ghidra promotion open verification names another backup root")
    try:
        backup_root.relative_to(REPO_ROOT / "local-lab")
    except ValueError as exc:
        raise CampaignError("Ghidra promotion backup is outside the ignored local evidence scope") from exc
    _verify_project_manifest_bytes(
        backup_root,
        backup_source_rows,
        expected_program["projectName"],
        "backup project",
    )
    backup_verified_time = _parse_utc_timestamp(
        backup_open.get("verifiedAtUtc"), "backup open verification"
    )
    backup_observed_function_count: int | None = None
    if not legacy_evidence:
        readonly_open = _runtime_mapping(
            backup_open.get("readonlyOpen"), "Ghidra measured backup reopen"
        )
        open_probe_path, _open_probe_stamp = _promotion_artifact(
            evidence_path, backup.get("openProbeTool"), "backup open-probe tool"
        )
        try:
            open_probe_path.relative_to(evidence_path.parent)
        except ValueError as exc:
            raise CampaignError("Ghidra backup open-probe tool was not snapshotted") from exc
        probe_copy_raw = backup_open.get("probeCopy")
        if (
            not isinstance(probe_copy_raw, str)
            or not probe_copy_raw.strip()
            or not Path(probe_copy_raw).is_absolute()
        ):
            raise CampaignError("Ghidra backup reopen has no absolute probe-copy path")
        probe_copy_path = Path(probe_copy_raw).resolve()
        try:
            probe_copy_path.relative_to((REPO_ROOT / "local-lab").resolve())
        except ValueError as exc:
            raise CampaignError("Ghidra backup probe copy escaped local-lab") from exc
        if (
            readonly_open.get("expectedProgramSha256") != specimen_stamp["sha256"]
            or readonly_open.get("observedProgramName") != expected_program["programName"]
            or readonly_open.get("observedProgramMd5") != expected_program["executableMd5"]
            or readonly_open.get("observedProgramSha256") != specimen_stamp["sha256"]
            or backup_open.get("probeCopyDisposition") != "DELETED_AFTER_VERIFICATION"
        ):
            raise CampaignError("Ghidra backup reopen did not measure the exact program identity")
        backup_observed_function_count = readonly_open.get("observedFunctionCount")
        if not isinstance(backup_observed_function_count, int) or backup_observed_function_count <= 0:
            raise CampaignError("Ghidra backup reopen has no measured function count")
        command_argv = readonly_open.get("commandArgv")
        expected_command_tail = [
            str(probe_copy_path),
            expected_program["projectName"],
            "-process",
            expected_program["programName"],
            "-readOnly",
            "-noanalysis",
            "-scriptPath",
            str(open_probe_path.parent.resolve()),
            "-postScript",
            open_probe_path.name,
            expected_program["programName"],
            expected_program["executableMd5"],
            specimen_stamp["sha256"],
        ]
        if (
            not isinstance(command_argv, list)
            or any(not isinstance(value, str) or not value for value in command_argv)
            or len(command_argv) != 14
            or Path(command_argv[0]).name.lower() != "analyzeheadless.bat"
            or command_argv[1:] != expected_command_tail
            or probe_copy_path.exists()
        ):
            raise CampaignError("Ghidra backup reopen receipt does not contain the actual safe argv")
        probe_log_path, _probe_log_stamp = _promotion_owned_artifact(
            backup_open_path, readonly_open.get("probeLog"), "backup open-probe log"
        )
        probe_log = _runtime_text(probe_log_path, "backup open-probe log")
        try:
            _observed_name, _observed_md5, _observed_sha256, parsed_function_count = (
                ghidra_backup.parse_clean_open_probe(
                    probe_log,
                    expected_program=expected_program["programName"],
                    expected_md5=expected_program["executableMd5"],
                    expected_sha256=specimen_stamp["sha256"],
                )
            )
        except ghidra_backup.BackupError as exc:
            raise CampaignError(
                "Ghidra backup reopen log lacks one measured success sentinel"
            ) from exc
        if parsed_function_count != backup_observed_function_count:
            raise CampaignError("Ghidra backup reopen log function count differs from its receipt")

    manifests = _runtime_mapping(evidence.get("projectManifests"), "Ghidra project manifests")
    pre_manifest_path, pre_manifest_stamp = _promotion_artifact(
        evidence_path, manifests.get("before"), "live preapply project manifest"
    )
    post_manifest_path, post_manifest_stamp = _promotion_artifact(
        evidence_path, manifests.get("after"), "live postapply project manifest"
    )
    pre_manifest = _promotion_json(pre_manifest_path, "live preapply project manifest")
    post_manifest = _promotion_json(post_manifest_path, "live postapply project manifest")
    if pre_manifest.get("schemaVersion") != backup_schema:
        raise CampaignError("Ghidra preapply project manifest schema is unsupported")
    if post_manifest.get("schemaVersion") != backup_schema:
        raise CampaignError("Ghidra postapply project manifest schema is unsupported")
    pre_manifest_value = pre_manifest.get("manifest")
    post_manifest_value = post_manifest.get("manifest")
    if _manifest_root(pre_manifest_value, "live preapply project") != live_project_root:
        raise CampaignError("Ghidra preapply manifest names another project root")
    if _manifest_root(post_manifest_value, "live postapply project") != live_project_root:
        raise CampaignError("Ghidra postapply manifest names another project root")
    if _manifest_file_rows(pre_manifest_value, "live preapply project") != backup_source_rows:
        raise CampaignError("Ghidra live preapply project did not equal the verified backup")
    post_project_rows = _manifest_file_rows(post_manifest_value, "live postapply project")
    if post_project_rows == backup_source_rows:
        raise CampaignError("Ghidra live project did not change during the apply")

    scratch = _runtime_mapping(evidence.get("scratchProof"), "Ghidra scratch proof")
    scratch_ready: dict[str, tuple[Path, dict, dict]] = {}
    scratch_ready_docs: dict[str, dict] = {}
    independent_artifacts: dict[str, Path] = {}
    scratch_project_root: Path | None = None
    scratch_before_functions_path: Path | None = None
    scratch_before_functions_stamp: dict | None = None
    scratch_before_program_path: Path | None = None
    scratch_before_program_stamp: dict | None = None
    scratch_before_log_text: str | None = None
    scratch_after_log_text: str | None = None
    negative_project_root: Path | None = None
    negative_pre_manifest_stamp: dict | None = None
    negative_post_manifest_stamp: dict | None = None
    negative_before_functions_path: Path | None = None
    negative_before_functions_stamp: dict | None = None
    negative_before_program_path: Path | None = None
    negative_before_program_stamp: dict | None = None
    negative_before_log_path: Path | None = None
    negative_before_log_text: str | None = None
    negative_after_functions_path: Path | None = None
    negative_after_functions_stamp: dict | None = None
    negative_after_program_path: Path | None = None
    negative_after_program_stamp: dict | None = None
    negative_after_log_path: Path | None = None
    negative_after_log_text: str | None = None
    negative_raw_project_changed: bool | None = None
    if not legacy_evidence:
        scratch_project_root = _local_scratch_project_root(
            scratch.get("projectRoot"), "scratch proof"
        )
        if scratch_project_root == live_project_root:
            raise CampaignError("Ghidra scratch proof aliases the maintainer project")
        scratch_pre_manifest_path, _scratch_pre_manifest_stamp = _promotion_artifact(
            evidence_path, scratch.get("preapplyManifest"), "scratch preapply project manifest"
        )
        scratch_pre_manifest = _promotion_json(
            scratch_pre_manifest_path, "scratch preapply project manifest"
        )
        if scratch_pre_manifest.get("schemaVersion") != backup_schema:
            raise CampaignError("Ghidra scratch preapply project manifest schema is unsupported")
        scratch_pre_manifest_value = scratch_pre_manifest.get("manifest")
        if (
            _manifest_root(scratch_pre_manifest_value, "scratch preapply project")
            != scratch_project_root
            or _manifest_file_rows(
                scratch_pre_manifest_value, "scratch preapply project"
            )
            != backup_source_rows
        ):
            raise CampaignError("Ghidra scratch project was not cloned from the verified backup")
        scratch_before_functions_path, scratch_before_functions_stamp = _promotion_artifact(
            evidence_path, scratch.get("beforeFunctions"), "scratch baseline functions"
        )
        scratch_before_program_path, scratch_before_program_stamp = _promotion_artifact(
            evidence_path, scratch.get("beforeProgram"), "scratch baseline program"
        )
        scratch_before_log_path, _scratch_before_log_stamp = _promotion_artifact(
            evidence_path, scratch.get("beforeLog"), "scratch baseline inventory log"
        )
        scratch_after_log_path, _scratch_after_log_stamp = _promotion_artifact(
            evidence_path, scratch.get("afterLog"), "scratch after inventory log"
        )
        scratch_before_log_text = _runtime_text(
            scratch_before_log_path, "scratch baseline inventory log"
        )
        scratch_after_log_text = _runtime_text(
            scratch_after_log_path, "scratch after inventory log"
        )
        independent_artifacts.update(
            {
                "scratch baseline functions": scratch_before_functions_path,
                "scratch baseline program": scratch_before_program_path,
                "scratch baseline inventory log": scratch_before_log_path,
                "scratch after inventory log": scratch_after_log_path,
                "scratch preapply project manifest": scratch_pre_manifest_path,
            }
        )
    for key, mode in (("dryReady", "dry"), ("applyReady", "apply"), ("readbackReady", "readback")):
        ready_path, ready_stamp = _promotion_artifact(
            evidence_path, scratch.get(key), f"scratch {mode} READY"
        )
        ready_doc = _promotion_json(ready_path, f"scratch {mode} READY")
        output = _runtime_mapping(ready_doc.get("output"), f"scratch {mode} READY output")
        output_path = Path(str(output.get("path", ""))).resolve()
        try:
            output_path.relative_to((REPO_ROOT / "local-lab").resolve())
        except ValueError as exc:
            raise CampaignError(f"scratch {mode} output is outside local-lab") from exc
        if not output_path.is_file():
            raise CampaignError(f"scratch {mode} output is missing")
        output_stamp = coverage.file_stamp(output_path)
        _validate_promotion_ready(
            ready_doc,
            required_schema=ready_schema,
            mode=mode,
            target_path=target_path,
            target_sha256=target_stamp["sha256"],
            target_bytes=target_stamp["bytes"],
            target_count=target_count,
            semantic_target_sha256=semantic_target_sha,
            tool_path=executed_tool_path,
            tool_stamp=tool_stamp,
            output_path=output_path,
            output_stamp=output_stamp,
            label=f"scratch {mode}",
        )
        scratch_ready[mode] = (ready_path, ready_stamp, output_stamp)
        scratch_ready_docs[mode] = ready_doc
        independent_artifacts[f"scratch {mode} READY"] = ready_path
        independent_artifacts[f"scratch {mode} TSV"] = output_path
        if not legacy_evidence:
            log_path, _log_stamp = _promotion_artifact(
                evidence_path, scratch.get(f"{mode}Log"), f"scratch {mode} log"
            )
            _validate_promotion_log(
                _runtime_text(log_path, f"scratch {mode} log"),
                ready_schema=ready_schema,
                mode=mode,
                target_path=target_path,
                target_sha256=target_stamp["sha256"],
                target_count=target_count,
                output_path=output_path,
                ready_path=ready_path,
                tool_path=executed_tool_path,
                tool_stamp=tool_stamp,
                expected_project_root=scratch_project_root,
                project_name=expected_program["projectName"],
                require_save=mode == "apply",
                label=f"scratch {mode}",
            )
            independent_artifacts[f"scratch {mode} log"] = log_path

    negative = _runtime_mapping(scratch.get("poisonedShaControl"), "Ghidra poisoned-SHA control")
    negative_log_path, negative_log_stamp = _promotion_artifact(
        evidence_path, negative.get("log"), "poisoned-SHA log"
    )
    negative_text = _runtime_text(negative_log_path, "poisoned-SHA log")
    if not legacy_evidence:
        negative_project_root = _local_scratch_project_root(
            negative.get("projectRoot"), "poisoned-SHA control"
        )
        if negative_project_root in (scratch_project_root, live_project_root):
            raise CampaignError(
                "Ghidra poisoned-SHA control must use its own disposable project clone"
            )
        negative_pre_manifest_path, negative_pre_manifest_stamp = _promotion_artifact(
            evidence_path,
            negative.get("preapplyManifest"),
            "poisoned-SHA preapply project manifest",
        )
        negative_post_manifest_path, negative_post_manifest_stamp = _promotion_artifact(
            evidence_path,
            negative.get("postapplyManifest"),
            "poisoned-SHA postapply project manifest",
        )
        negative_pre_manifest = _promotion_json(
            negative_pre_manifest_path, "poisoned-SHA preapply project manifest"
        )
        negative_post_manifest = _promotion_json(
            negative_post_manifest_path, "poisoned-SHA postapply project manifest"
        )
        if (
            negative_pre_manifest.get("schemaVersion") != backup_schema
            or negative_post_manifest.get("schemaVersion") != backup_schema
        ):
            raise CampaignError("Ghidra poisoned-SHA project manifest schema is unsupported")
        negative_pre_value = negative_pre_manifest.get("manifest")
        negative_post_value = negative_post_manifest.get("manifest")
        negative_pre_rows = _manifest_file_rows(
            negative_pre_value, "poisoned-SHA preapply project"
        )
        negative_post_rows = _manifest_file_rows(
            negative_post_value, "poisoned-SHA postapply project"
        )
        if (
            _manifest_root(negative_pre_value, "poisoned-SHA preapply project")
            != negative_project_root
            or _manifest_root(negative_post_value, "poisoned-SHA postapply project")
            != negative_project_root
            or negative_pre_rows != backup_source_rows
        ):
            raise CampaignError(
                "Ghidra poisoned-SHA project was not an independent verified-backup clone"
            )
        _verify_project_manifest_bytes(
            negative_project_root,
            negative_post_rows,
            expected_program["projectName"],
            "poisoned-SHA project",
        )
        negative_before_functions_path, negative_before_functions_stamp = _promotion_artifact(
            evidence_path,
            negative.get("beforeFunctions"),
            "poisoned-SHA baseline functions",
        )
        negative_before_program_path, negative_before_program_stamp = _promotion_artifact(
            evidence_path,
            negative.get("beforeProgram"),
            "poisoned-SHA baseline program",
        )
        negative_before_log_path, _negative_before_log_stamp = _promotion_artifact(
            evidence_path,
            negative.get("beforeLog"),
            "poisoned-SHA baseline inventory log",
        )
        negative_after_functions_path, negative_after_functions_stamp = _promotion_artifact(
            evidence_path,
            negative.get("afterFunctions"),
            "poisoned-SHA after functions",
        )
        negative_after_program_path, negative_after_program_stamp = _promotion_artifact(
            evidence_path,
            negative.get("afterProgram"),
            "poisoned-SHA after program",
        )
        negative_after_log_path, _negative_after_log_stamp = _promotion_artifact(
            evidence_path,
            negative.get("afterLog"),
            "poisoned-SHA after inventory log",
        )
        negative_before_log_text = _runtime_text(
            negative_before_log_path, "poisoned-SHA baseline inventory log"
        )
        negative_after_log_text = _runtime_text(
            negative_after_log_path, "poisoned-SHA after inventory log"
        )
        negative_raw_project_changed = _validate_poisoned_sha_semantic_stability(
            reported_raw_project_changed=negative.get("rawProjectChanged"),
            pre_project_rows=negative_pre_rows,
            post_project_rows=negative_post_rows,
            before_functions_stamp=negative_before_functions_stamp,
            after_functions_stamp=negative_after_functions_stamp,
            before_program_stamp=negative_before_program_stamp,
            after_program_stamp=negative_after_program_stamp,
        )
        independent_artifacts.update(
            {
                "poisoned-SHA preapply project manifest": negative_pre_manifest_path,
                "poisoned-SHA postapply project manifest": negative_post_manifest_path,
                "poisoned-SHA baseline functions": negative_before_functions_path,
                "poisoned-SHA baseline program": negative_before_program_path,
                "poisoned-SHA baseline inventory log": negative_before_log_path,
                "poisoned-SHA after functions": negative_after_functions_path,
                "poisoned-SHA after program": negative_after_program_path,
                "poisoned-SHA after inventory log": negative_after_log_path,
            }
        )

        wrong_sha = str(negative.get("expectedSha256", ""))
        negative_tsv_raw = negative.get("outputTsvPath")
        negative_ready_raw = negative.get("outputReadyPath")
        if (
            not re.fullmatch(r"[0-9a-f]{64}", wrong_sha)
            or wrong_sha == target_stamp["sha256"]
            or not isinstance(negative_tsv_raw, str)
            or not Path(negative_tsv_raw).is_absolute()
            or not isinstance(negative_ready_raw, str)
            or not Path(negative_ready_raw).is_absolute()
            or negative.get("expectedCount") != target_count
        ):
            raise CampaignError("Ghidra poisoned-SHA control has no exact rejected invocation")
        negative_tsv_path = Path(negative_tsv_raw).resolve()
        negative_ready_path = Path(negative_ready_raw).resolve()
        try:
            negative_tsv_path.relative_to((REPO_ROOT / "local-lab").resolve())
            negative_ready_path.relative_to((REPO_ROOT / "local-lab").resolve())
        except ValueError as exc:
            raise CampaignError("Ghidra poisoned-SHA outputs escape local-lab") from exc
        expected_negative_execute = (
            "REPORT: Execute script: CreateFunctionsFromAddressList.java "
            f"'{target_path.resolve()}' '{wrong_sha}' '{target_count}' "
            f"'{negative_tsv_path}' '{negative_ready_path}' 'apply'"
        )
        expected_negative_open = (
            f"Opening existing project: "
            f"{negative_project_root.resolve() / expected_program['projectName']} "
            "(HeadlessAnalyzer)"
        )
        expected_mismatch = (
            f"address-list sha256 mismatch expected={wrong_sha} "
            f"actual={target_stamp['sha256']}"
        )
        save_marker = "Save succeeded for processed file: /BEA.exe"
        save_reported = negative.get("saveReported")
        expected_tool_sentinel = (
            f"FUNCTION_PROMOTION_TOOL_OK path={executed_tool_path.resolve()} "
            f"bytes={tool_stamp['bytes']} sha256={tool_stamp['sha256']}"
        )
        if (
            negative.get("mode") != "apply"
            or negative_text.count(expected_negative_open) != 1
            or "REPORT: Processing project file: /BEA.exe" not in negative_text
            or "REPORT: Processing read-only project file: /BEA.exe" in negative_text
            or negative_text.count(expected_negative_execute) != 1
            or negative_text.count(
                f"SCRIPT: {executed_tool_path.resolve()} (HeadlessAnalyzer)"
            )
            != 1
            or negative_text.count(expected_tool_sentinel) != 1
            or negative_text.count(expected_mismatch) != 1
            or not isinstance(save_reported, bool)
            or negative_text.count(save_marker) != (1 if save_reported else 0)
            or negative_tsv_path.exists()
            or negative_ready_path.exists()
        ):
            raise CampaignError("Ghidra poisoned-SHA control is not one isolated apply-mode preflight")
        independent_artifacts["scratch poisoned-SHA absent TSV"] = negative_tsv_path
        independent_artifacts["scratch poisoned-SHA absent READY"] = negative_ready_path
    independent_artifacts["scratch poisoned-SHA log"] = negative_log_path
    if (
        "FUNCTION_PROMOTION_OK" in negative_text
        or "FUNCTION_PROMOTION_PREFLIGHT_OK" in negative_text
        or "FUNCTION_PROMOTION_RECEIPT_LOST" in negative_text
        or negative_text.count("REPORT SCRIPT ERROR") != 1
        or negative_text.count("address-list sha256 mismatch") != 1
        or negative.get("successSentinelPresent") is not False
        or negative.get("scriptErrorPresent") is not True
        or negative.get("addressListShaMismatchPresent") is not True
        or negative.get("tsvPublished") is not False
        or negative.get("readyPublished") is not False
    ):
        raise CampaignError("Ghidra poisoned-SHA control did not fail closed")

    live = _runtime_mapping(evidence.get("liveRun"), "Ghidra live run")
    live_artifacts: dict[str, dict] = {}
    live_ready_docs: dict[str, dict] = {}
    for section_name, mode in (("apply", "apply"), ("readback", "readback")):
        section = _runtime_mapping(live.get(section_name), f"Ghidra live {mode}")
        tsv_path, tsv_stamp = _promotion_artifact(
            evidence_path, section.get("tsv"), f"live {mode} TSV"
        )
        ready_path, ready_stamp = _promotion_artifact(
            evidence_path, section.get("ready"), f"live {mode} READY"
        )
        log_path, log_stamp = _promotion_artifact(
            evidence_path, section.get("log"), f"live {mode} log"
        )
        ready_doc = _promotion_json(ready_path, f"live {mode} READY")
        _validate_promotion_ready(
            ready_doc,
            required_schema=ready_schema,
            mode=mode,
            target_path=target_path,
            target_sha256=target_stamp["sha256"],
            target_bytes=target_stamp["bytes"],
            target_count=target_count,
            semantic_target_sha256=semantic_target_sha,
            tool_path=executed_tool_path,
            tool_stamp=tool_stamp,
            output_path=tsv_path,
            output_stamp=tsv_stamp,
            label=f"live {mode}",
        )
        _validate_promotion_log(
            _runtime_text(log_path, f"live {mode} log"),
            ready_schema=ready_schema,
            mode=mode,
            target_path=target_path,
            target_sha256=target_stamp["sha256"],
            target_count=target_count,
            output_path=tsv_path,
            ready_path=ready_path,
            tool_path=executed_tool_path,
            tool_stamp=tool_stamp,
            expected_project_root=live_project_root,
            project_name=expected_program["projectName"],
            require_save=mode == "apply",
            label=f"live {mode}",
        )
        if tsv_stamp["sha256"] != scratch_ready[mode][2]["sha256"]:
            raise CampaignError(f"Ghidra live {mode} output differs from scratch")
        live_artifacts[mode] = {
            "tsvPath": tsv_path,
            "tsv": tsv_stamp,
            "ready": ready_stamp,
            "log": log_stamp,
        }
        live_ready_docs[mode] = ready_doc
        independent_artifacts[f"live {mode} TSV"] = tsv_path
        independent_artifacts[f"live {mode} READY"] = ready_path
        independent_artifacts[f"live {mode} log"] = log_path

    after = _runtime_mapping(live.get("afterInventory"), "Ghidra live after inventory")
    after_functions_path, after_functions_stamp = _promotion_artifact(
        evidence_path, after.get("functions"), "live after functions"
    )
    after_program_path, after_program_stamp = _promotion_artifact(
        evidence_path, after.get("program"), "live after program"
    )
    live_diff_path, live_diff_stamp = _promotion_artifact(
        evidence_path, after.get("diff"), "live inventory diff"
    )
    after_log_path, after_log_stamp = _promotion_artifact(
        evidence_path, after.get("log"), "live inventory log"
    )
    after_log = _runtime_text(after_log_path, "live inventory log")
    independent_artifacts.update(
        {
            "live after functions": after_functions_path,
            "live after program": after_program_path,
            "live after diff": live_diff_path,
            "live after log": after_log_path,
        }
    )

    scratch_functions_path, scratch_functions_stamp = _promotion_artifact(
        evidence_path, scratch.get("functions"), "scratch after functions"
    )
    scratch_program_path, scratch_program_stamp = _promotion_artifact(
        evidence_path, scratch.get("program"), "scratch after program"
    )
    scratch_diff_path, scratch_diff_stamp = _promotion_artifact(
        evidence_path, scratch.get("inventoryDiff"), "scratch inventory diff"
    )
    independent_artifacts.update(
        {
            "scratch after functions": scratch_functions_path,
            "scratch after program": scratch_program_path,
            "scratch after diff": scratch_diff_path,
        }
    )
    if after_functions_stamp["sha256"] != scratch_functions_stamp["sha256"]:
        raise CampaignError("Ghidra live and scratch function inventories differ")
    if after_program_stamp["sha256"] != scratch_program_stamp["sha256"]:
        raise CampaignError("Ghidra live and scratch program inventories differ")

    prereg_campaign_path, prereg_campaign_stamp = _promotion_artifact(
        prereg_path, prereg.get("campaign"), "preregistered campaign READY"
    )
    if prereg_campaign_path != campaign_ready_path or prereg_campaign_stamp["sha256"] != campaign_stamp["sha256"]:
        raise CampaignError("Ghidra promotion preregistered another campaign")
    prereg_targets = _runtime_mapping(prereg.get("targets"), "preregistered targets")
    prereg_target_ready_path, prereg_target_ready_stamp = _promotion_artifact(
        prereg_path, prereg_targets.get("ready"), "preregistered boundary READY"
    )
    prereg_target_path, prereg_target_stamp = _promotion_artifact(
        prereg_path, prereg_targets.get("list"), "preregistered boundary list"
    )
    if (
        prereg_target_ready_path != boundary_ready_path
        or prereg_target_ready_stamp["sha256"] != boundary_ready_stamp["sha256"]
        or prereg_target_path != target_path
        or prereg_target_stamp["sha256"] != target_stamp["sha256"]
    ):
        raise CampaignError("Ghidra promotion used another target set than preregistered")
    prereg_tool_path, prereg_tool_stamp = _promotion_artifact(
        prereg_path,
        prereg.get("tool"),
        "preregistered promotion tool",
        content_fallback=LEGACY_GHIDRA_PROMOTION_TOOL_SNAPSHOT if legacy_evidence else None,
    )
    if prereg_tool_path != tool_path or prereg_tool_stamp["sha256"] != tool_stamp["sha256"]:
        raise CampaignError("Ghidra promotion used another tool than preregistered")
    prereg_scratch = _runtime_mapping(
        prereg.get("scratchProof"), "preregistered scratch proof"
    )
    expected_prereg_scratch = {
        "dryReadySha256": scratch_ready["dry"][1]["sha256"],
        "applyReadySha256": scratch_ready["apply"][1]["sha256"],
        "readbackReadySha256": scratch_ready["readback"][1]["sha256"],
        "inventoryDiffSha256": scratch_diff_stamp["sha256"],
        "afterFunctionsSha256": scratch_functions_stamp["sha256"],
        "independentPriorAfterFunctionsSha256": scratch_functions_stamp["sha256"],
        "poisonedShaRejectedWithoutOutputs": True,
    }
    if not legacy_evidence:
        expected_prereg_scratch.update(
            {
                "poisonedShaProjectRoot": str(negative_project_root),
                "poisonedShaPreapplyManifestSha256": negative_pre_manifest_stamp["sha256"],
                "poisonedShaPostapplyManifestSha256": negative_post_manifest_stamp["sha256"],
                "poisonedShaLogSha256": negative_log_stamp["sha256"],
                "poisonedShaBeforeFunctionsSha256": negative_before_functions_stamp["sha256"],
                "poisonedShaAfterFunctionsSha256": negative_after_functions_stamp["sha256"],
                "poisonedShaBeforeProgramSha256": negative_before_program_stamp["sha256"],
                "poisonedShaAfterProgramSha256": negative_after_program_stamp["sha256"],
                "poisonedShaRawProjectChanged": negative_raw_project_changed,
            }
        )
    if any(
        prereg_scratch.get(key) != value
        for key, value in expected_prereg_scratch.items()
    ):
        raise CampaignError("Ghidra promotion preregistered another scratch proof")
    scratch_dry_time = _parse_utc_timestamp(
        scratch_ready_docs["dry"].get("completedAtUtc"), "scratch dry READY"
    )
    scratch_apply_time = _parse_utc_timestamp(
        scratch_ready_docs["apply"].get("completedAtUtc"), "scratch apply READY"
    )
    scratch_readback_time = _parse_utc_timestamp(
        scratch_ready_docs["readback"].get("completedAtUtc"), "scratch readback READY"
    )
    prereg_time = _parse_utc_timestamp(prereg.get("createdAtUtc"), "preregistration")
    apply_time = _parse_utc_timestamp(
        live_ready_docs["apply"].get("completedAtUtc"), "live apply READY"
    )
    readback_time = _parse_utc_timestamp(
        live_ready_docs["readback"].get("completedAtUtc"), "live readback READY"
    )
    if not (
        backup_verified_time
        < scratch_dry_time
        < scratch_apply_time
        < scratch_readback_time
        < prereg_time
        < apply_time
        < readback_time
        <= evidence_time
    ):
        raise CampaignError(
            "Ghidra promotion chronology is not backup < scratch dry/apply/readback "
            "< preregistration < live apply/readback <= evidence"
        )
    prereg_baseline = _runtime_mapping(prereg.get("liveBaseline"), "preregistered live baseline")
    before_functions_path, before_functions_stamp = _promotion_artifact(
        prereg_path, prereg_baseline.get("functions"), "live baseline functions"
    )
    before_program_path, before_program_stamp = _promotion_artifact(
        prereg_path, prereg_baseline.get("program"), "live baseline program"
    )
    before_log_path: Path | None = None
    before_log_text: str | None = None
    if not legacy_evidence:
        before_log_path, _before_log_stamp = _promotion_artifact(
            prereg_path, prereg_baseline.get("log"), "live baseline inventory log"
        )
        before_log_text = _runtime_text(before_log_path, "live baseline inventory log")
        independent_artifacts["live baseline inventory log"] = before_log_path
    independent_artifacts["live baseline functions"] = before_functions_path
    independent_artifacts["live baseline program"] = before_program_path
    _require_distinct_artifact_paths(independent_artifacts)
    baseline_function_count = prereg_baseline.get("functionCount")
    if (
        not isinstance(baseline_function_count, int)
        or baseline_function_count <= 0
        or prereg_baseline.get("targetCountPresent") != 0
    ):
        raise CampaignError("Ghidra promotion live baseline was not the preregistered empty cohort")
    expected_after_function_count = baseline_function_count + target_count
    if (
        backup_observed_function_count is not None
        and backup_observed_function_count != baseline_function_count
    ):
        raise CampaignError("Ghidra backup reopen function count differs from the live baseline")
    if not legacy_evidence:
        if (
            scratch_before_functions_stamp["sha256"] != before_functions_stamp["sha256"]
            or scratch_before_program_stamp["sha256"] != before_program_stamp["sha256"]
        ):
            raise CampaignError("Ghidra scratch baseline differs from the live preregistered baseline")
        if (
            negative_before_functions_stamp["sha256"]
            != scratch_before_functions_stamp["sha256"]
            or negative_before_program_stamp["sha256"]
            != scratch_before_program_stamp["sha256"]
            or negative_after_functions_stamp["sha256"]
            != negative_before_functions_stamp["sha256"]
            or negative_after_program_stamp["sha256"]
            != negative_before_program_stamp["sha256"]
        ):
            raise CampaignError(
                "Ghidra poisoned-SHA control changed the semantic function/program inventory"
            )
        _validate_inventory_log(
            scratch_before_log_text,
            expected_project_root=scratch_project_root,
            project_name=expected_program["projectName"],
            expected_function_count=baseline_function_count,
            functions_path=scratch_before_functions_path,
            program_path=scratch_before_program_path,
            tool_path=inventory_tool_path,
            tool_stamp=inventory_tool_stamp,
            label="scratch baseline",
        )
        _validate_inventory_log(
            scratch_after_log_text,
            expected_project_root=scratch_project_root,
            project_name=expected_program["projectName"],
            expected_function_count=expected_after_function_count,
            functions_path=scratch_functions_path,
            program_path=scratch_program_path,
            tool_path=inventory_tool_path,
            tool_stamp=inventory_tool_stamp,
            label="scratch after",
        )
        _validate_inventory_log(
            negative_before_log_text,
            expected_project_root=negative_project_root,
            project_name=expected_program["projectName"],
            expected_function_count=baseline_function_count,
            functions_path=negative_before_functions_path,
            program_path=negative_before_program_path,
            tool_path=inventory_tool_path,
            tool_stamp=inventory_tool_stamp,
            label="poisoned-SHA baseline",
        )
        _validate_inventory_log(
            negative_after_log_text,
            expected_project_root=negative_project_root,
            project_name=expected_program["projectName"],
            expected_function_count=baseline_function_count,
            functions_path=negative_after_functions_path,
            program_path=negative_after_program_path,
            tool_path=inventory_tool_path,
            tool_stamp=inventory_tool_stamp,
            label="poisoned-SHA after",
        )
        _validate_inventory_log(
            before_log_text,
            expected_project_root=live_project_root,
            project_name=expected_program["projectName"],
            expected_function_count=baseline_function_count,
            functions_path=before_functions_path,
            program_path=before_program_path,
            tool_path=inventory_tool_path,
            tool_stamp=inventory_tool_stamp,
            label="live baseline",
        )
    _validate_inventory_log(
        after_log,
        expected_project_root=live_project_root,
        project_name=expected_program["projectName"],
        expected_function_count=expected_after_function_count,
        functions_path=after_functions_path,
        program_path=after_program_path,
        tool_path=inventory_tool_path,
        tool_stamp=inventory_tool_stamp,
        label="live after",
    )
    prereg_backup = _runtime_mapping(prereg.get("recoverableBackup"), "preregistered backup")
    prereg_backup_manifest_path, prereg_backup_manifest_stamp = _promotion_artifact(
        prereg_path, prereg_backup.get("manifest"), "preregistered backup manifest"
    )
    prereg_backup_open_path, prereg_backup_open_stamp = _promotion_artifact(
        prereg_path, prereg_backup.get("openVerification"), "preregistered backup verification"
    )
    if (
        prereg_backup_manifest_path != backup_manifest_path
        or prereg_backup_manifest_stamp["sha256"] != backup_manifest_stamp["sha256"]
        or prereg_backup_open_path != backup_open_path
        or prereg_backup_open_stamp["sha256"] != backup_open_stamp["sha256"]
    ):
        raise CampaignError("Ghidra promotion used another backup than preregistered")
    authorized = _runtime_mapping(prereg.get("authorizedMutation"), "preregistered mutation")
    expected_authorized = {
        "createExactlyTheseFunctionEntries": target_count,
        "assignSemanticNames": False,
        "expectedFunctionCountAfter": expected_after_function_count,
        "expectedCreatedSetEqualsTargets": True,
        "expectedDestroyed": 0,
        "expectedExistingBoundsChanged": 0,
        "expectedNamesChanged": 0,
        "expectedSignaturesChanged": 0,
        "expectedExistingInstructionCountsChanged": 0,
        "expectedDangerousReviewedChanges": 0,
    }
    if any(authorized.get(key) != value for key, value in expected_authorized.items()):
        raise CampaignError("Ghidra live mutation exceeded or differed from preregistration")

    before_rows = _promotion_rows(before_functions_path, "address", "live baseline functions")
    after_rows = _promotion_rows(after_functions_path, "address", "live after functions")
    created = set(after_rows) - set(before_rows)
    destroyed = set(before_rows) - set(after_rows)
    shared = set(before_rows) & set(after_rows)
    target_set = set(addresses)
    if (
        created != target_set
        or destroyed
        or len(before_rows) != baseline_function_count
        or len(after_rows) != expected_after_function_count
    ):
        raise CampaignError("Ghidra promotion full inventories do not reproduce the exact target creation")
    if any(before_rows[address] != after_rows[address] for address in shared):
        raise CampaignError("Ghidra promotion changed an existing function inventory row")
    for address in addresses:
        row = after_rows[address]
        if (
            row.get("name", "").lower() != f"fun_{address[2:]}"
            or row.get("nameSource") != "DEFAULT"
            or row.get("bodyMin", "").lower() != address
            or _integer(row.get("bodyBytes"), 0) <= 0
            or _integer(row.get("instrCount"), 0) <= 0
        ):
            raise CampaignError(f"Ghidra promotion created an invalid boundary row at {address}")

    before_program = _promotion_rows(before_program_path, "metric", "live baseline program")
    after_program = _promotion_rows(after_program_path, "metric", "live after program")
    if set(before_program) != set(after_program):
        raise CampaignError("Ghidra promotion changed program-inventory metric keys")
    for metric in before_program:
        before_value = before_program[metric].get("value")
        after_value = after_program[metric].get("value")
        if metric == "functions":
            if (
                before_value != str(baseline_function_count)
                or after_value != str(expected_after_function_count)
            ):
                raise CampaignError("Ghidra promotion function metric did not advance by the target count")
        elif before_value != after_value:
            raise CampaignError(f"Ghidra promotion changed program metric {metric}")

    apply_rows = _promotion_rows(live_artifacts["apply"]["tsvPath"], "address", "live apply")
    readback_rows = _promotion_rows(live_artifacts["readback"]["tsvPath"], "address", "live readback")
    if set(apply_rows) != target_set or set(readback_rows) != target_set:
        raise CampaignError("Ghidra apply/readback ledgers do not reproduce the target set")
    for address in addresses:
        apply_row = apply_rows[address]
        readback_row = readback_rows[address]
        inventory_row = after_rows[address]
        if apply_row.get("status") != "created" or readback_row.get("status") != "verified":
            raise CampaignError(f"Ghidra promotion status mismatch at {address}")
        for field in ("name", "nameSource", "bodyBytes", "bodyMin", "bodyMax", "bodyRanges", "instrCount"):
            if apply_row.get(field) != inventory_row.get(field) or readback_row.get(field) != inventory_row.get(field):
                raise CampaignError(f"Ghidra promotion readback differs at {address} field {field}")

    live_diff = _promotion_json(live_diff_path, "live inventory diff")
    scratch_diff = _promotion_json(scratch_diff_path, "scratch inventory diff")
    for label, report in (("live", live_diff), ("scratch", scratch_diff)):
        counts = _runtime_mapping(report.get("counts"), f"{label} inventory diff counts")
        expected_counts = {
            "before": baseline_function_count,
            "after": expected_after_function_count,
            "created": target_count,
            "destroyed": 0,
            "boundsChanged": 0,
            "callingConvChanged": 0,
            "instrCountChanged": 0,
            "namesChanged": 0,
            "noReturnChanged": 0,
            "paramCountChanged": 0,
            "returnTypeChanged": 0,
            "sigSourceChanged": 0,
            "signaturesChanged": 0,
            "thunkFlagChanged": 0,
        }
        if any(counts.get(key) != value for key, value in expected_counts.items()):
            raise CampaignError(f"Ghidra {label} inventory diff exceeds the authorized mutation")
        dangerous = _runtime_mapping(report.get("dangerous"), f"{label} inventory dangerous")
        if any(
            dangerous.get(key) != 0
            for key in (
                "gradedDestroyedCount", "gradedRenamedCount", "gradedDemotedCount",
                "gradedBoundsMovedCount",
            )
        ):
            raise CampaignError(f"Ghidra {label} inventory diff changed reviewed work")
        diff_created = {str(row.get("address", "")).lower() for row in report.get("created", [])}
        if diff_created != target_set:
            raise CampaignError(f"Ghidra {label} inventory diff created another target set")

    observed = _runtime_mapping(evidence.get("observed"), "Ghidra promotion observations")
    expected_observed = {
        "beforeFunctionCount": baseline_function_count,
        "afterFunctionCount": expected_after_function_count,
        "created": target_count,
        "createdSetEqualsTargets": True,
        "destroyed": 0,
        "existingBoundsChanged": 0,
        "namesChanged": 0,
        "signaturesChanged": 0,
        "existingInstructionCountsChanged": 0,
        "reviewedDangerousChanges": 0,
        "readbackVerified": target_count,
        "liveEqualsScratchFunctions": True,
        "liveEqualsScratchProgram": True,
        "semanticNamesAssigned": 0,
    }
    if any(observed.get(key) != value for key, value in expected_observed.items()):
        raise CampaignError("Ghidra promotion observation summary disagrees with parsed artifacts")
    claim_boundary = _runtime_list(evidence.get("claimBoundary"), "Ghidra claimBoundary")
    if len(claim_boundary) < 2 or any(not isinstance(value, str) or not value.strip() for value in claim_boundary):
        raise CampaignError("Ghidra promotion lacks an explicit claim boundary")

    campaign_functions = _read_tsv(source_campaign / "campaign-functions.tsv")
    campaign_by_address = {row["entryVa"].lower(): row for row in campaign_functions}
    boundary_targets = {row["address"]: row for row in boundary_ready["targets"]}
    mappings = []
    for address in addresses:
        function = campaign_by_address.get(address)
        boundary = boundary_targets[address]
        if function is None:
            raise CampaignError(f"Ghidra promoted target is absent from the campaign: {address}")
        if function.get("nativeRegistryStatus") != "NO_FUNCTION":
            raise CampaignError(f"Ghidra promoted target is not an unsuperseded campaign row: {address}")
        expected_old = _candidate_key(specimen_stamp["sha256"], address)
        if boundary.get("entityKey") != expected_old:
            raise CampaignError(f"Ghidra boundary candidate identity mismatch at {address}")
        inventory = after_rows[address]
        if (
            function.get("currentName") != inventory.get("name")
            or function.get("bodyBytes") != inventory.get("bodyBytes")
            or not function.get("entityKey", "").startswith(
                f"CODE:{specimen_stamp['sha256']}:VA={address}:RANGES="
            )
        ):
            raise CampaignError(f"Ghidra live inventory and campaign function differ at {address}")
        mappings.append(
            {
                "address": address,
                "questionId": boundary.get("questionId"),
                "oldEntityKey": expected_old,
                "newEntityKey": function["entityKey"],
            }
        )

    return {
        "evidence": evidence,
        "evidenceStamp": evidence_stamp,
        "campaign": source_campaign,
        "campaignStamp": campaign_stamp,
        "preregistrationStamp": prereg_stamp,
        "boundaryReadyStamp": boundary_ready_stamp,
        "targetStamp": target_stamp,
        "toolStamp": tool_stamp,
        "toolProvenance": {
            "declaredExecutionPath": str(tool_declared_path),
            "verifiedContentPath": str(tool_path),
            "historicalFallbackUsed": tool_path != tool_declared_path,
        },
        "evidenceSchema": evidence_schema,
        "legacyBridgeUsed": legacy_evidence,
        "backupManifestStamp": backup_manifest_stamp,
        "backupOpenStamp": backup_open_stamp,
        "preManifestStamp": pre_manifest_stamp,
        "postManifestStamp": post_manifest_stamp,
        "negativeLogStamp": negative_log_stamp,
        "liveApply": live_artifacts["apply"],
        "liveReadback": live_artifacts["readback"],
        "afterFunctionsStamp": after_functions_stamp,
        "afterProgramStamp": after_program_stamp,
        "liveDiffStamp": live_diff_stamp,
        "scratchDiffStamp": scratch_diff_stamp,
        "afterLogStamp": after_log_stamp,
        "specimenPath": specimen_path,
        "specimenStamp": specimen_stamp,
        "measuredAtUtc": measured_at,
        "addresses": addresses,
        "mappings": mappings,
    }


def advance_ghidra_promotion(
    campaign: Path,
    evidence_path: Path,
    out: Path,
    *,
    _self_check: bool = True,
    _verified_parent_receipt: dict | None = None,
) -> dict:
    """Record a boundary-only live-project promotion without promoting semantics."""
    base_receipt = (
        _verified_parent_receipt
        if _verified_parent_receipt is not None
        else verify(campaign)
    )
    if out.exists():
        raise CampaignError(f"refusing existing advanced-campaign destination: {out}")
    validated = validate_ghidra_promotion_evidence(
        evidence_path,
        campaign,
        _verified_campaign_receipt=base_receipt,
    )
    base_ready = coverage.file_stamp(campaign / "campaign.ready.json")
    if validated["campaignStamp"]["sha256"] != base_ready["sha256"]:
        raise CampaignError("Ghidra promotion evidence names another campaign READY")

    functions = _read_tsv(campaign / "campaign-functions.tsv")
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    questions = _read_tsv(campaign / "campaign-questions.tsv")
    scenarios = _read_tsv(campaign / "campaign-scenarios.tsv")
    levers = _read_tsv(campaign / "campaign-levers.tsv")
    contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    adjudications = _read_tsv(campaign / "campaign-adjudications.tsv")
    supersessions = _read_tsv(campaign / "campaign-supersessions.tsv")
    functions_by_entity = {row["entityKey"]: row for row in functions}
    contracts_by_entity = {row["entityKey"]: row for row in contracts}
    existing_old = {row.get("oldEntityKey") for row in supersessions}
    measured_at = validated["measuredAtUtc"]
    evidence_ref = (
        f"{evidence_path.resolve()}#sha256={validated['evidenceStamp']['sha256']}"
    )
    for mapping in validated["mappings"]:
        old = mapping["oldEntityKey"]
        new = mapping["newEntityKey"]
        if old in existing_old:
            raise CampaignError(f"Ghidra boundary candidate was already superseded: {old}")
        function = functions_by_entity[new]
        contract = contracts_by_entity[new]
        function["nativeRegistryStatus"] = "FUNCTION_PROMOTED_LIVE_BOUNDARY_ONLY"
        function["evidenceStates"] = _append_state(
            function.get("evidenceStates", ""), "MAINTAINER_GHIDRA_BOUNDARY_PROMOTED"
        )
        function["lastMeasurementDate"] = measured_at[:10]
        contract["evidenceRefs"] = _append_state(contract.get("evidenceRefs", ""), evidence_ref)
        contract["supersedesEntityKeys"] = _append_state(
            contract.get("supersedesEntityKeys", ""), old
        )
        contract["lastMeasurementDate"] = measured_at[:10]
        supersessions.append(
            {
                "supersessionId": "S-" + _sha256_text(old + "|" + new)[:16],
                "oldEntityKey": old,
                "newEntityKey": new,
                "kind": GHIDRA_ADVANCE_KIND,
                "verdict": "SURVIVED",
                "evidenceRefs": evidence_ref,
                "measuredAtUtc": measured_at,
            }
        )
        existing_old.add(old)

    output_rows = {
        "campaign-functions.tsv": (FUNCTION_COLUMNS, functions),
        "campaign-residuals.tsv": (RESIDUAL_COLUMNS, residuals),
        "campaign-questions.tsv": (QUESTION_COLUMNS, questions),
        "campaign-scenarios.tsv": (SCENARIO_COLUMNS, scenarios),
        "campaign-levers.tsv": (LEVER_COLUMNS, levers),
        "campaign-contracts.tsv": (CONTRACT_COLUMNS, contracts),
        "campaign-adjudications.tsv": (ADJUDICATION_COLUMNS, adjudications),
        "campaign-supersessions.tsv": (SUPERSESSION_COLUMNS, supersessions),
    }
    next_generation = _integer(base_receipt.get("generation"), 0) + 1
    promotion_id = "P-" + _sha256_text(
        "|".join(
            (
                base_ready["sha256"],
                validated["evidenceStamp"]["sha256"],
                validated["targetStamp"]["sha256"],
                validated["afterFunctionsStamp"]["sha256"],
            )
        )
    )[:16]
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        for name, (columns, rows) in output_rows.items():
            _write_tsv(stage / name, columns, rows)
        reducer = _publish_reducer(stage)
        counts = {
            "functions": len(functions),
            "residuals": len(residuals),
            "questions": len(questions),
            "scenarios": len(scenarios),
            "levers": len(levers),
            "contracts": len(contracts),
            "adjudications": len(adjudications),
            "supersessions": len(supersessions),
        }
        receipt = {
            "schema": SCHEMA,
            "reducer": reducer,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "generation": next_generation,
            "parentCampaign": {
                "path": str(campaign.resolve()),
                "ready": {**base_ready, "path": "campaign.ready.json"},
            },
            "sourceSnapshot": base_receipt["sourceSnapshot"],
            "advance": {
                "kind": GHIDRA_ADVANCE_KIND,
                "promotionId": promotion_id,
                "verdict": "SURVIVED",
                "count": len(validated["mappings"]),
                "evidence": {
                    **validated["evidenceStamp"],
                    "path": str(evidence_path.resolve()),
                },
                "preregistration": validated["preregistrationStamp"],
                "targets": validated["targetStamp"],
                "tool": validated["toolStamp"],
                "toolProvenance": validated["toolProvenance"],
                "evidenceSchema": validated["evidenceSchema"],
                "legacyBridgeUsed": validated["legacyBridgeUsed"],
                "backup": validated["backupOpenStamp"],
                "liveApply": {
                    key: value
                    for key, value in validated["liveApply"].items()
                    if key != "tsvPath"
                },
                "liveReadback": {
                    key: value
                    for key, value in validated["liveReadback"].items()
                    if key != "tsvPath"
                },
                "liveAfterFunctions": validated["afterFunctionsStamp"],
                "liveInventoryDiff": validated["liveDiffStamp"],
                "semanticPromotionApplied": False,
            },
            "counts": counts,
            "questionTypes": dict(Counter(row["questionType"] for row in questions)),
            "policies": [
                "Only the exact address-only function-boundary cohort was promoted.",
                "Whole-inventory scratch and live refuters found no collateral metadata changes.",
                "Boundary promotion assigns no semantic names and closes no contract questions.",
                (
                    "Candidate entry identities are superseded by Ghidra-flow-analysis "
                    "range-bound CODE entity keys; body bounds remain independently unrefuted."
                ),
                (
                    "This generation uses the one exact-hash legacy-v1 evidence bridge; "
                    "future promotions require schema v2."
                    if validated["legacyBridgeUsed"]
                    else "This generation was validated directly under the schema-v2 promotion gate."
                ),
            ],
            "outputs": {
                name: {**coverage.file_stamp(stage / name), "path": name}
                for name in OUTPUTS
            },
        }
        (stage / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        if _self_check:
            verify(stage)
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _plain_contained_evidence_path(root: Path, relative: str, label: str) -> Path:
    if (
        not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
        or "\\" in relative
    ):
        raise CampaignError(f"{label} stamp path is unsafe")
    try:
        root = ghidra_backup.resolve_plain_path(root, f"{label} root", strict=True)
    except (ghidra_backup.BackupError, OSError) as exc:
        raise CampaignError(f"{label} evidence root is not plain: {exc}") from exc
    candidate = Path(os.path.abspath(root / Path(relative)))
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise CampaignError(f"{label} stamp escapes its evidence root") from exc
    try:
        path = ghidra_backup.resolve_plain_path(candidate, label, strict=True)
    except (ghidra_backup.BackupError, OSError) as exc:
        raise CampaignError(f"{label} is not one plain evidence file: {exc}") from exc
    try:
        link_count = path.stat().st_nlink
    except OSError as exc:
        raise CampaignError(f"{label} file identity cannot be read: {exc}") from exc
    if link_count != 1:
        raise CampaignError(f"{label} has multiple hard links")
    return path


def _validate_relative_evidence_stamp(
    root: Path, value: object, label: str
) -> tuple[Path, dict]:
    stamp = _runtime_mapping(value, f"{label} stamp")
    if set(stamp) != {"path", "bytes", "sha256"}:
        raise CampaignError(f"{label} stamp shape differs")
    relative = stamp.get("path")
    if not isinstance(relative, str):
        raise CampaignError(f"{label} stamp path is unsafe")
    path = _plain_contained_evidence_path(root, relative, label)
    actual = _require_file_stamp(path, stamp, label)
    return path, {**actual, "path": relative}


def _require_disjoint_evidence_files(
    files: list[tuple[str, Path]], label: str
) -> None:
    for index, (first_label, first) in enumerate(files):
        for second_label, second in files[index + 1 :]:
            try:
                aliases = os.path.samefile(first, second)
            except OSError as exc:
                raise CampaignError(f"{label} file identity cannot be read: {exc}") from exc
            if aliases:
                raise CampaignError(
                    f"{label} files alias: {first_label} / {second_label}"
                )


def _semantic_stamped_file(
    value: object,
    label: str,
    *,
    relative_root: Path | None = None,
) -> tuple[Path, dict[str, object]]:
    stamp = _runtime_mapping(value, f"{label} stamp")
    if (
        not {"path", "sha256"}.issubset(stamp)
        or not set(stamp).issubset({"path", "bytes", "sha256", "rows"})
    ):
        raise CampaignError(f"{label} stamp shape differs")
    raw_path = stamp.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise CampaignError(f"{label} has no path")
    if relative_root is not None and not Path(raw_path).is_absolute():
        path = _plain_contained_evidence_path(relative_root, raw_path, label)
    else:
        path = _resolve_repo_or_absolute(raw_path, label)
        try:
            path = ghidra_backup.resolve_plain_path(path, label, strict=True)
        except (ghidra_backup.BackupError, OSError) as exc:
            raise CampaignError(f"{label} is not one plain file: {exc}") from exc
        if path.stat().st_nlink != 1:
            raise CampaignError(f"{label} has multiple hard links")
    actual = coverage.file_stamp(path)
    if actual["sha256"] != stamp.get("sha256") or (
        "bytes" in stamp and actual["bytes"] != stamp.get("bytes")
    ):
        raise CampaignError(f"{label} has changed")
    return path, {
        "path": str(path),
        "bytes": actual["bytes"],
        "sha256": actual["sha256"],
    }


def _semantic_observation_rows(
    observation: object,
    *,
    expected_state: str,
    expected_mode: str,
    root: Path,
    label: str,
) -> tuple[dict[str, dict], dict[str, dict[str, object]]]:
    value = _runtime_mapping(observation, label)
    if (
        value.get("schema") != GHIDRA_SEMANTIC_OBSERVATION_SCHEMA
        or value.get("state") != expected_state
    ):
        raise CampaignError(f"{label} state/schema differs")
    semantic = _runtime_mapping(value.get("semantic"), f"{label} semantic")
    if semantic.get("mode") != expected_mode:
        raise CampaignError(f"{label} semantic mode differs")
    artifacts: dict[str, dict[str, object]] = {}
    artifact_paths: list[tuple[str, Path]] = []
    for role in ("output", "process", "ready"):
        path, stamp = _semantic_stamped_file(
            semantic.get(role),
            f"{label} {role}",
            relative_root=root,
        )
        artifacts[role] = stamp
        artifact_paths.append((role, path))
    _require_disjoint_evidence_files(artifact_paths, label)
    rows_value = semantic.get("normalizedRows")
    if not isinstance(rows_value, list) or not rows_value:
        raise CampaignError(f"{label} has no normalized semantic rows")
    rows: dict[str, dict] = {}
    for row in rows_value:
        if not isinstance(row, dict):
            raise CampaignError(f"{label} contains a malformed semantic row")
        address = str(row.get("address", ""))
        if not re.fullmatch(r"0x[0-9a-f]{8}", address) or address in rows:
            raise CampaignError(f"{label} contains a duplicate/malformed address")
        if row.get("state") != expected_state:
            raise CampaignError(f"{label} row state differs: {address}")
        rows[address] = row
    return rows, artifacts


def _semantic_snapshot_key(value: object, label: str) -> tuple:
    snapshot = _runtime_mapping(value, label)
    files = snapshot.get("files")
    if not isinstance(files, list) or any(not isinstance(row, dict) for row in files):
        raise CampaignError(f"{label} file inventory differs")
    normalized = tuple(
        sorted(
            (
                str(row.get("path", "")),
                _integer(row.get("bytes"), -1),
                str(row.get("sha256", "")),
            )
            for row in files
        )
    )
    if (
        _integer(snapshot.get("fileCount"), -1) != len(normalized)
        or _integer(snapshot.get("totalBytes"), -1)
        != sum(row[1] for row in normalized)
        or any(
            not row[0]
            or row[1] < 0
            or not re.fullmatch(r"[0-9a-f]{64}", row[2])
            for row in normalized
        )
    ):
        raise CampaignError(f"{label} file inventory is malformed")
    canonical = "".join(f"{sha}\t{size}\t{path}\n" for path, size, sha in normalized)
    if _sha256_text(canonical) != snapshot.get("fileSetSha256"):
        raise CampaignError(f"{label} file-set digest differs")
    return normalized


def validate_ghidra_semantic_promotion(
    campaign: Path,
    live_ready_path: Path,
    *,
    _verified_campaign_receipt: dict | None = None,
) -> dict[str, object]:
    """Reproduce one same-range semantic Ghidra promotion from frozen evidence."""

    base_receipt = (
        _verified_campaign_receipt
        if _verified_campaign_receipt is not None
        else _verify_target_lock_semantic_parent_campaign(campaign)
    )
    live_ready_path = live_ready_path.resolve()
    try:
        live_ready_path = ghidra_backup.resolve_plain_path(
            live_ready_path, "semantic live READY", strict=True
        )
    except (ghidra_backup.BackupError, OSError) as exc:
        raise CampaignError(f"semantic live READY is not one plain file: {exc}") from exc
    if live_ready_path.stat().st_nlink != 1:
        raise CampaignError("semantic live READY has multiple hard links")
    live_stamp = {
        **coverage.file_stamp(live_ready_path),
        "path": str(live_ready_path),
    }
    live = _promotion_json(live_ready_path, "semantic live READY")
    if (
        live.get("schema") != GHIDRA_SEMANTIC_LIVE_READY_SCHEMA
        or live.get("status") != "READY"
        or live.get("state") != "POST"
        or live.get("campaignPublicationAuthorized") is not True
        or live.get("automaticRestorePerformed") is not False
        or live.get("retryAuthorized") is not False
        or live.get("trackedSnapshotRefreshed") is not False
        or live.get("mutationSpawns") != 1
        or live.get("classificationError") not in (None, "")
        or live.get("postObservationError") not in (None, "")
        or live.get("postBackupError") not in (None, "")
    ):
        raise CampaignError("semantic live READY did not close cleanly")
    measured_at = str(live.get("completedAtUtc", ""))
    _parse_utc_timestamp(measured_at, "semantic live completion")
    live_root = live_ready_path.parent
    owner_root = live_root.parent

    attempt_path, attempt_stamp = _semantic_stamped_file(
        live.get("attempt"), "semantic live attempt", relative_root=live_root
    )
    result_path, result_stamp = _semantic_stamped_file(
        live.get("result"), "semantic live result", relative_root=live_root
    )
    process_path, process_stamp = _semantic_stamped_file(
        live.get("process"), "semantic live apply process", relative_root=live_root
    )
    owner_path, owner_stamp = _semantic_stamped_file(
        live.get("owner"), "semantic live owner"
    )
    _require_disjoint_evidence_files(
        [
            ("live READY", live_ready_path),
            ("attempt", attempt_path),
            ("result", result_path),
            ("apply process", process_path),
            ("owner", owner_path),
        ],
        "semantic live root",
    )
    result = _promotion_json(result_path, "semantic live result")
    for field in (
        "schema",
        "state",
        "protocol",
        "postObservation",
        "classification",
        "postBackup",
        "campaignPublicationAuthorized",
        "automaticRestorePerformed",
        "mutationSpawns",
        "retryAuthorized",
    ):
        if not _same_json(result.get(field), live.get(field)):
            raise CampaignError(f"semantic live result differs from READY: {field}")

    attempt = _promotion_json(attempt_path, "semantic live attempt")
    if (
        attempt.get("schema")
        != "bea.re.ghidra-target-lock-semantic-live-attempt.v1"
        or attempt.get("mutationSpawnLimit") != 1
        or attempt.get("automaticRestoreAuthorized") is not False
        or attempt.get("retryAuthorized") is not False
        or not _same_json(attempt.get("owner"), live.get("owner"))
        or not _same_json(attempt.get("launchGate"), live.get("launchGate"))
    ):
        raise CampaignError("semantic live attempt boundary differs")
    prepared_path, prepared_stamp = _semantic_stamped_file(
        attempt.get("preparedReady"),
        "semantic prepared READY",
        relative_root=owner_root,
    )
    prepared = _promotion_json(prepared_path, "semantic prepared READY")
    if (
        prepared.get("schema") != GHIDRA_SEMANTIC_PREPARED_SCHEMA
        or prepared.get("status") != "READY"
        or not _same_json(prepared.get("owner"), live.get("owner"))
        or not _same_json(prepared.get("launchGate"), live.get("launchGate"))
    ):
        raise CampaignError("semantic prepared READY differs")
    authority = _runtime_mapping(prepared.get("authority"), "semantic authority")
    program = _runtime_mapping(authority.get("program"), "semantic program")
    expected_program = {
        "name": "BEA.exe",
        "executableMd5": "3b456964020070efe696d2cc09464a55",
        "executableSha256": (
            "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
        ),
        "imageBase": "0x00400000",
        "language": "x86:LE:32:default",
        "compilerSpec": "windows",
        "functions": 8124,
    }
    if any(program.get(key) != value for key, value in expected_program.items()):
        raise CampaignError("semantic promotion names another program")

    plan_path, plan_stamp = _semantic_stamped_file(
        authority.get("plan"), "semantic plan"
    )
    evidence_path, evidence_stamp = _semantic_stamped_file(
        authority.get("evidence"), "semantic evidence"
    )
    tool_path, tool_stamp = _semantic_stamped_file(
        authority.get("semanticTool"), "semantic apply tool"
    )
    proof_path, proof_stamp = _semantic_stamped_file(
        authority.get("proofReady"), "semantic proof READY"
    )
    attempt_proof_path, attempt_proof_stamp = _semantic_stamped_file(
        attempt.get("proofReady"), "semantic attempt proof READY"
    )
    if proof_path != attempt_proof_path or proof_stamp != attempt_proof_stamp:
        raise CampaignError("semantic proof READY identity differs across boundaries")
    _require_disjoint_evidence_files(
        [
            ("plan", plan_path),
            ("evidence", evidence_path),
            ("tool", tool_path),
            ("proof", proof_path),
            ("prepared", prepared_path),
        ],
        "semantic authority",
    )

    proof = _promotion_json(proof_path, "semantic proof READY")
    if (
        proof.get("schema") != GHIDRA_SEMANTIC_PROOF_READY_SCHEMA
        or proof.get("status") != "READY"
        or proof.get("verdict") != "SCRATCH_SEMANTIC_COHORT_AUTHORIZED"
        or proof.get("semanticNamesAuthorized") is not True
        or proof.get("liveMutationAuthorized") is not False
        or proof.get("rebuildParityProved") is not False
        or proof.get("globalTargetLockParityProved") is not False
        or proof.get("staleOrGapCrossedReturnBacklinksAdmitted") is not False
    ):
        raise CampaignError("semantic proof READY claim boundary differs")
    proof_root = proof_path.parent
    proof_files: list[tuple[str, Path]] = [("proof READY", proof_path)]
    for role in ("core", "subject", "refuter"):
        path, _stamp = _semantic_stamped_file(
            proof.get(role), f"semantic proof {role}", relative_root=proof_root
        )
        proof_files.append((role, path))
    _require_disjoint_evidence_files(proof_files, "semantic proof")

    plan_rows = _read_tsv(plan_path)
    if len(plan_rows) != 5:
        raise CampaignError("semantic plan is not the exact five-row cohort")
    plan_by_address = {row.get("address", ""): row for row in plan_rows}
    addresses = sorted(plan_by_address)
    if (
        len(plan_by_address) != 5
        or any(not re.fullmatch(r"0x[0-9a-f]{8}", value) for value in addresses)
        or sorted(str(value) for value in authority.get("addresses", [])) != addresses
        or sorted(str(value) for value in proof.get("addresses", [])) != addresses
    ):
        raise CampaignError("semantic promotion target set differs")
    evidence_rows = _read_tsv(evidence_path)
    evidence_addresses = set(row.get("address", "") for row in evidence_rows)
    if (
        not evidence_rows
        or not set(addresses).issubset(evidence_addresses)
        or not evidence_addresses.issubset(set(addresses) | {"GLOBAL"})
        or _integer(authority.get("evidence", {}).get("rows"), -1)
        != len(evidence_rows)
    ):
        raise CampaignError("semantic evidence target accounting differs")

    proof_decisions = proof.get("decisions")
    if not isinstance(proof_decisions, list) or len(proof_decisions) != 5:
        raise CampaignError("semantic proof decision set differs")
    decisions = {
        str(row.get("address", "")): row
        for row in proof_decisions
        if isinstance(row, dict)
    }
    if set(decisions) != set(addresses) or any(
        row.get("verdict") != "ACCEPT" for row in decisions.values()
    ):
        raise CampaignError("semantic proof did not accept the exact five rows")
    proposed_names = proof.get("proposedNames")
    if not isinstance(proposed_names, dict) or {
        str(key): str(value) for key, value in proposed_names.items()
    } != {address: str(decisions[address].get("proposedName", "")) for address in addresses}:
        raise CampaignError("semantic proof proposed-name map differs")

    pre_rows, _pre_artifacts = _semantic_observation_rows(
        prepared.get("finalObservation"),
        expected_state="PRE",
        expected_mode="dry",
        root=owner_root,
        label="semantic final PRE observation",
    )
    post_rows, post_artifacts = _semantic_observation_rows(
        live.get("postObservation"),
        expected_state="POST",
        expected_mode="readback",
        root=live_root,
        label="semantic live POST observation",
    )
    backup = _runtime_mapping(live.get("postBackup"), "semantic post backup")
    if backup.get("state") != "POST":
        raise CampaignError("semantic post backup state differs")
    backup_rows, backup_artifacts = _semantic_observation_rows(
        backup.get("backupObservation"),
        expected_state="POST",
        expected_mode="readback",
        root=live_root,
        label="semantic post-backup observation",
    )
    protocol = _runtime_mapping(live.get("protocol"), "semantic apply protocol")
    protocol_semantic = _runtime_mapping(
        protocol.get("semantic"), "semantic apply protocol rows"
    )
    protocol_rows_value = protocol_semantic.get("normalizedRows")
    if (
        protocol.get("status") != "COMPLETE"
        or protocol.get("reasons") != []
        or protocol_semantic.get("mode") != "apply"
        or not isinstance(protocol_rows_value, list)
    ):
        raise CampaignError("semantic apply protocol differs")
    protocol_rows = {
        str(row.get("address", "")): row
        for row in protocol_rows_value
        if isinstance(row, dict)
    }
    if (
        set(pre_rows) != set(addresses)
        or set(post_rows) != set(addresses)
        or set(backup_rows) != set(addresses)
        or set(protocol_rows) != set(addresses)
        or not _same_json(post_rows, backup_rows)
        or not _same_json(post_rows, protocol_rows)
    ):
        raise CampaignError("semantic PRE/apply/readback row sets differ")

    post_observation = _runtime_mapping(
        live.get("postObservation"), "semantic POST observation"
    )
    expected_delta = _runtime_mapping(
        post_observation.get("delta"), "semantic POST delta"
    )
    if (
        sorted(str(value) for value in expected_delta.get("changedFunctions", []))
        != addresses
        or set(expected_delta) != {"changedFunctions", "programDelta"}
        or not _same_json(expected_delta, backup.get("backupObservation", {}).get("delta"))
    ):
        raise CampaignError("semantic live delta is not the exact five-row set")
    program_delta = _runtime_mapping(
        expected_delta.get("programDelta"), "semantic program delta"
    )
    if set(program_delta) != {"comments", "commentsSha256"}:
        raise CampaignError("semantic program delta contains an unreviewed field")

    classification = _runtime_mapping(live.get("classification"), "semantic classification")
    if (
        classification.get("schema") != GHIDRA_SEMANTIC_OBSERVATION_SCHEMA
        or classification.get("state") != "POST"
    ):
        raise CampaignError("semantic post classification differs")
    inventory = _runtime_mapping(classification.get("inventory"), "semantic inventory")
    inventory_stamps: dict[str, dict[str, object]] = {}
    inventory_files: list[tuple[str, Path]] = []
    for role in ("functions", "program", "process"):
        path, stamp = _semantic_stamped_file(
            inventory.get(role),
            f"semantic post inventory {role}",
            relative_root=live_root,
        )
        inventory_stamps[role] = stamp
        inventory_files.append((role, path))
    _require_disjoint_evidence_files(inventory_files, "semantic post inventory")

    snapshot_values = [
        (post_observation.get("rawBefore"), "semantic POST raw before"),
        (post_observation.get("rawAfter"), "semantic POST raw after"),
        (classification.get("rawBefore"), "semantic classification raw before"),
        (classification.get("rawAfter"), "semantic classification raw after"),
        (backup.get("sourceSnapshot"), "semantic backup source"),
        (backup.get("backupSnapshot"), "semantic backup copy"),
        (backup.get("restoreSnapshot"), "semantic backup restore"),
    ]
    snapshot_keys = [_semantic_snapshot_key(value, label) for value, label in snapshot_values]
    if any(key != snapshot_keys[0] for key in snapshot_keys[1:]):
        raise CampaignError("semantic live POST and backup project bytes differ")
    post_fileset = str(post_observation.get("rawAfter", {}).get("fileSetSha256", ""))
    pre_fileset = str(prepared.get("livePreimage", {}).get("fileSetSha256", ""))
    if (
        not re.fullmatch(r"[0-9a-f]{64}", post_fileset)
        or not re.fullmatch(r"[0-9a-f]{64}", pre_fileset)
        or post_fileset == pre_fileset
    ):
        raise CampaignError("semantic live project did not cross one PRE-to-POST boundary")

    functions = _read_tsv(campaign / "campaign-functions.tsv")
    contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    functions_by_address = {row.get("entryVa", ""): row for row in functions}
    contracts_by_entity = {row.get("entityKey", ""): row for row in contracts}
    semantic_rows: list[dict[str, str]] = []
    for address in addresses:
        plan = plan_by_address[address]
        decision = decisions[address]
        before = pre_rows[address]
        after = post_rows[address]
        function = functions_by_address.get(address)
        if function is None:
            raise CampaignError(f"semantic target is absent from the campaign: {address}")
        contract = contracts_by_entity.get(function.get("entityKey", ""))
        if contract is None or contract.get("currentName") != function.get("currentName"):
            raise CampaignError(f"semantic target contract identity differs: {address}")
        body_match = re.fullmatch(
            r"0x([0-9a-f]+)-0x([0-9a-f]+)",
            str(function.get("bodyRangesRva", "")),
        )
        if body_match is None:
            raise CampaignError(f"semantic campaign body range is malformed: {address}")
        campaign_min = 0x00400000 + int(body_match.group(1), 16)
        campaign_end = 0x00400000 + int(body_match.group(2), 16)
        proposed_comment = str(plan.get("proposed_comment", ""))
        expected = {
            "body_min": plan.get("expected_body_min"),
            "body_max": plan.get("expected_body_max"),
            "body_bytes": plan.get("expected_body_bytes"),
            "body_digest": plan.get("expected_body_digest"),
            "body_bytes_sha256": plan.get("expected_body_bytes_sha256"),
        }
        if (
            before.get("name") != plan.get("expected_name")
            or function.get("currentName") != plan.get("expected_name")
            or after.get("name") != plan.get("proposed_name")
            or decision.get("proposedName") != plan.get("proposed_name")
            or decision.get("proposedSignature") != plan.get("proposed_signature")
            or decision.get("proposedTags") != plan.get("proposed_tags")
            or decision.get("proposedCommentSha256") != _sha256_text(proposed_comment)
            or after.get("comment_sha256") != decision.get("proposedCommentSha256")
            or after.get("tags") != decision.get("proposedTags")
            or after.get("prototype_key_base64")
            != plan.get("proposed_prototype_key_base64")
            or after.get("signature_source") != "USER_DEFINED"
            or after.get("name_source") != "USER_DEFINED"
            or after.get("namespace") != "Global"
            or any(before.get(key) != value for key, value in expected.items())
            or any(after.get(key) != value for key, value in expected.items())
            or _integer(function.get("bodyBytes"), -1) != int(expected["body_bytes"])
            or campaign_min != int(address, 16)
            or campaign_end - 1 != int(str(expected["body_max"]), 16)
            or campaign_end - campaign_min != int(expected["body_bytes"])
        ):
            raise CampaignError(f"semantic target PRE/POST contract differs: {address}")
        semantic_rows.append(
            {
                "entityKey": function["entityKey"],
                "address": address,
                "previousName": function["currentName"],
                "promotedName": str(after["name"]),
                "bodyDigest": str(after["body_digest"]),
                "signatureSha256": str(after["signature_sha256"]),
                "commentSha256": str(after["comment_sha256"]),
                "tagsSha256": str(after["tags_sha256"]),
            }
        )

    return {
        "baseReceipt": base_receipt,
        "liveReady": live_stamp,
        "attempt": attempt_stamp,
        "result": result_stamp,
        "preparedReady": prepared_stamp,
        "proofReady": proof_stamp,
        "plan": plan_stamp,
        "evidence": evidence_stamp,
        "semanticTool": tool_stamp,
        "owner": owner_stamp,
        "applyProcess": process_stamp,
        "postArtifacts": post_artifacts,
        "backupArtifacts": backup_artifacts,
        "inventory": inventory_stamps,
        "measuredAtUtc": measured_at,
        "preProjectFileSetSha256": pre_fileset,
        "postProjectFileSetSha256": post_fileset,
        "rows": semantic_rows,
    }


def advance_ghidra_semantic_promotion(
    campaign: Path,
    live_ready_path: Path,
    out: Path,
    *,
    _self_check: bool = True,
    _verified_parent_receipt: dict | None = None,
) -> dict:
    base_receipt = (
        _verified_parent_receipt
        if _verified_parent_receipt is not None
        else _verify_target_lock_semantic_parent_campaign(campaign)
    )
    if out.exists():
        raise CampaignError(f"refusing existing advanced-campaign destination: {out}")
    validated = validate_ghidra_semantic_promotion(
        campaign,
        live_ready_path,
        _verified_campaign_receipt=base_receipt,
    )
    functions = _read_tsv(campaign / "campaign-functions.tsv")
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    questions = _read_tsv(campaign / "campaign-questions.tsv")
    scenarios = _read_tsv(campaign / "campaign-scenarios.tsv")
    levers = _read_tsv(campaign / "campaign-levers.tsv")
    contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    adjudications = _read_tsv(campaign / "campaign-adjudications.tsv")
    supersessions = _read_tsv(campaign / "campaign-supersessions.tsv")
    functions_by_entity = {row["entityKey"]: row for row in functions}
    contracts_by_entity = {row["entityKey"]: row for row in contracts}
    evidence_refs = [
        f"{validated['liveReady']['path']}#sha256={validated['liveReady']['sha256']}",
        f"{validated['proofReady']['path']}#sha256={validated['proofReady']['sha256']}",
        f"{validated['plan']['path']}#sha256={validated['plan']['sha256']}",
        f"{validated['evidence']['path']}#sha256={validated['evidence']['sha256']}",
    ]
    measured_date = str(validated["measuredAtUtc"])[:10]
    for promoted in validated["rows"]:
        function = functions_by_entity[promoted["entityKey"]]
        contract = contracts_by_entity[promoted["entityKey"]]
        function["currentName"] = promoted["promotedName"]
        function["nativeRegistryStatus"] = "FUNCTION_PROMOTED_LIVE_SEMANTIC"
        function["nameClass"] = "NAMED"
        function["understoodTier"] = "U2_ADDRESS_CITED"
        function["evidenceStates"] = _append_state(
            function.get("evidenceStates", ""),
            "MAINTAINER_GHIDRA_SEMANTIC_PROMOTED",
        )
        function["evidenceStates"] = _append_state(
            function["evidenceStates"], "INDEPENDENT_REFUTATION_SURVIVED"
        )
        function["lastMeasurementDate"] = measured_date
        contract["currentName"] = promoted["promotedName"]
        for evidence_ref in evidence_refs:
            contract["evidenceRefs"] = _append_state(
                contract.get("evidenceRefs", ""), evidence_ref
            )
        contract["lastMeasurementDate"] = measured_date

    output_rows = {
        "campaign-functions.tsv": (FUNCTION_COLUMNS, functions),
        "campaign-residuals.tsv": (RESIDUAL_COLUMNS, residuals),
        "campaign-questions.tsv": (QUESTION_COLUMNS, questions),
        "campaign-scenarios.tsv": (SCENARIO_COLUMNS, scenarios),
        "campaign-levers.tsv": (LEVER_COLUMNS, levers),
        "campaign-contracts.tsv": (CONTRACT_COLUMNS, contracts),
        "campaign-adjudications.tsv": (ADJUDICATION_COLUMNS, adjudications),
        "campaign-supersessions.tsv": (SUPERSESSION_COLUMNS, supersessions),
    }
    base_ready = coverage.file_stamp(campaign / "campaign.ready.json")
    next_generation = _integer(base_receipt.get("generation"), 0) + 1
    promotion_id = "SP-" + _sha256_text(
        "|".join(
            (
                base_ready["sha256"],
                str(validated["liveReady"]["sha256"]),
                str(validated["proofReady"]["sha256"]),
            )
        )
    )[:16]
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        for name, (columns, rows) in output_rows.items():
            _write_tsv(stage / name, columns, rows)
        reducer = _publish_reducer(stage)
        counts = {
            "functions": len(functions),
            "residuals": len(residuals),
            "questions": len(questions),
            "scenarios": len(scenarios),
            "levers": len(levers),
            "contracts": len(contracts),
            "adjudications": len(adjudications),
            "supersessions": len(supersessions),
        }
        advance = {
            "kind": GHIDRA_SEMANTIC_ADVANCE_KIND,
            "schema": GHIDRA_SEMANTIC_ADVANCE_SCHEMA,
            "promotionId": promotion_id,
            "verdict": "SURVIVED",
            "count": len(validated["rows"]),
            "liveReady": validated["liveReady"],
            "preparedReady": validated["preparedReady"],
            "proofReady": validated["proofReady"],
            "plan": validated["plan"],
            "evidence": validated["evidence"],
            "semanticTool": validated["semanticTool"],
            "owner": validated["owner"],
            "applyProcess": validated["applyProcess"],
            "preProjectFileSetSha256": validated["preProjectFileSetSha256"],
            "postProjectFileSetSha256": validated["postProjectFileSetSha256"],
            "rows": validated["rows"],
            "metadataSemanticPromotionApplied": True,
            "contractSemanticPromotionApplied": False,
            "questionsClosed": 0,
            "rebuildParityProved": False,
        }
        receipt = {
            "schema": SCHEMA,
            "reducer": reducer,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "generation": next_generation,
            "parentCampaign": {
                "path": str(campaign.resolve()),
                "ready": {**base_ready, "path": "campaign.ready.json"},
            },
            "sourceSnapshot": base_receipt["sourceSnapshot"],
            "advance": advance,
            "counts": counts,
            "questionTypes": dict(Counter(row["questionType"] for row in questions)),
            "policies": [
                "Only the exact five same-range Ghidra names, signatures, comments, and tags crossed the live semantic boundary.",
                "No function/residual entity key changed, so this advance creates no supersession.",
                "Campaign contracts remain OPEN/C0_OPAQUE; no question or rebuild-parity claim is closed by metadata alone.",
                "The live POST project, independent readback, post backup, and restore drill agree exactly.",
            ],
            "outputs": {
                name: {**coverage.file_stamp(stage / name), "path": name}
                for name in OUTPUTS
            },
        }
        (stage / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        if _self_check:
            verify(stage)
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _global_init515_observation_evidence_files(
    observation: dict, prefix: str
) -> list[tuple[str, Path]]:
    files = [(f"{prefix} observation", observation["path"])]
    files.extend(
        (f"{prefix} {name}", artifact["path"])
        for name, artifact in observation["artifacts"].items()
    )
    for run_name in ("inventoryRun", "symbolRun"):
        run = observation[run_name]
        files.append((f"{prefix} {run_name} receipt", run["path"]))
        files.append((f"{prefix} {run_name} log", run["log"]["path"]))
    return files


def _global_init515_reproduction_evidence_files(
    reproductions: dict[str, dict], prefix: str
) -> list[tuple[str, Path]]:
    files = []
    for name, reproduction in reproductions.items():
        run = reproduction["run"]
        files.append((f"{prefix} {name} receipt", run["path"]))
        files.append((f"{prefix} {name} log", run["log"]["path"]))
    return files


def _global_init515_expected_process_context(root: Path) -> dict[str, object]:
    root = root.resolve()
    java = _exact_external_stamp(
        GLOBAL_INIT515_JAVA_PATH,
        GLOBAL_INIT515_JAVA_SHA256,
        "global-init515 Java",
    )
    command = _exact_external_stamp(
        GLOBAL_INIT515_WINDOWS_COMMAND_PATH,
        GLOBAL_INIT515_WINDOWS_COMMAND_SHA256,
        "global-init515 Windows command processor",
    )
    windows = GLOBAL_INIT515_WINDOWS_ROOT.resolve()
    system32 = windows / "System32"
    runtime = root / "runtime-home"
    environment = {
        "APPDATA": str(runtime / "roaming"),
        "BEA_REPO_ROOT": str(REPO_ROOT.resolve()),
        "COMSPEC": command["path"],
        "JAVA_HOME": str(Path(java["path"]).resolve().parent.parent),
        "LOCALAPPDATA": str(runtime / "local"),
        "NoDefaultCurrentDirectoryInExePath": "1",
        "PATH": os.pathsep.join(
            (
                str(Path(java["path"]).resolve().parent),
                str(system32),
                str(windows),
            )
        ),
        "PATHEXT": ".COM;.EXE;.BAT;.CMD",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONUTF8": "1",
        "SystemRoot": str(windows),
        "TEMP": str(runtime / "temp"),
        "TMP": str(runtime / "temp"),
        "USERPROFILE": str(runtime / "profile"),
        "WINDIR": str(windows),
    }
    return {"cwd": str((root / "work").resolve()), "environment": environment}


def _validate_global_init515_process_context(
    root: Path, receipt: dict, label: str
) -> None:
    expected = _global_init515_expected_process_context(root)
    if (
        receipt.get("cwd") != expected["cwd"]
        or receipt.get("environment") != expected["environment"]
    ):
        raise CampaignError(f"{label} process context differs")
    directories = [
        Path(str(expected["cwd"])),
        *(
            Path(str(expected["environment"][key]))
            for key in ("APPDATA", "LOCALAPPDATA", "TEMP", "USERPROFILE")
        ),
    ]
    for directory in directories:
        try:
            plain = ghidra_backup.resolve_plain_path(directory, label, strict=True)
        except (ghidra_backup.BackupError, OSError) as exc:
            raise CampaignError(f"{label} process context directory is not plain: {exc}") from exc
        if plain != directory.resolve() or not plain.is_dir():
            raise CampaignError(f"{label} process context directories differ")
    java_home = (
        Path(str(expected["environment"]["APPDATA"]))
        / "ghidra/ghidra_12.1.2_PUBLIC/java_home.save"
    )
    expected_java_home = f"{expected['environment']['JAVA_HOME']}\r\n".encode()
    try:
        java_home = ghidra_backup.resolve_plain_path(java_home, label, strict=True)
        actual_java_home = java_home.read_bytes()
    except (ghidra_backup.BackupError, OSError) as exc:
        raise CampaignError(f"{label} Java runtime selection cannot be read: {exc}") from exc
    if java_home.stat().st_nlink != 1:
        raise CampaignError(f"{label} Java runtime selection has multiple hard links")
    if actual_java_home != expected_java_home:
        raise CampaignError(f"{label} Java runtime selection differs")


def _exact_external_stamp(path: Path, expected_sha256: str, label: str) -> dict:
    try:
        path = ghidra_backup.resolve_plain_path(path, label, strict=True)
    except (ghidra_backup.BackupError, OSError) as exc:
        raise CampaignError(f"{label} is not one plain external file: {exc}") from exc
    try:
        measured = coverage.file_stamp(path)
    except OSError as exc:
        raise CampaignError(f"{label} cannot be rehashed: {exc}") from exc
    if measured["sha256"] != expected_sha256:
        raise CampaignError(f"{label} bytes differ")
    return {
        "path": str(path),
        "bytes": measured["bytes"],
        "sha256": measured["sha256"],
    }


def _validate_contained_process_stamp(
    root: Path,
    value: object,
    label: str,
    *,
    expected_relative_path: str | None = None,
    expected_id: str | None = None,
    expected_argv: list[str] | None = None,
) -> dict:
    path, stamp = _validate_relative_evidence_stamp(root, value, f"{label} receipt")
    receipt = _promotion_json(path, f"{label} receipt")
    if (
        receipt.get("schema") != GLOBAL_INIT515_PROCESS_SCHEMA
        or receipt.get("status") != "COMPLETED"
        or receipt.get("exitCode") != 0
        or receipt.get("error") not in (None, "")
        or receipt.get("readerError") not in (None, "")
    ):
        raise CampaignError(f"{label} process did not complete cleanly")
    started_at = _parse_utc_timestamp(receipt.get("startedAtUtc"), f"{label} start")
    completed_at = _parse_utc_timestamp(
        receipt.get("completedAtUtc"), f"{label} completion"
    )
    if started_at > completed_at:
        raise CampaignError(f"{label} process chronology differs")
    if expected_relative_path is not None and stamp["path"] != expected_relative_path:
        raise CampaignError(f"{label} receipt path differs")
    if expected_id is not None and receipt.get("id") != expected_id:
        raise CampaignError(f"{label} process id differs")
    if expected_argv is not None and receipt.get("argv") != expected_argv:
        raise CampaignError(f"{label} argv differs")
    _validate_global_init515_process_context(root, receipt, label)
    log_path, log_stamp = _validate_relative_evidence_stamp(
        root, receipt.get("log"), f"{label} log"
    )
    return {
        "path": path,
        "stamp": stamp,
        "receipt": receipt,
        "log": {"path": log_path, "stamp": log_stamp},
        "startedAt": started_at,
        "completedAt": completed_at,
    }


def _project_snapshot_identity(value: object, label: str) -> dict:
    snapshot = _runtime_mapping(value, label)
    files = _runtime_list(snapshot.get("files"), f"{label} files")
    if (
        not isinstance(snapshot.get("root"), str)
        or not isinstance(snapshot.get("fileCount"), int)
        or not isinstance(snapshot.get("totalBytes"), int)
        or re.fullmatch(r"[0-9a-f]{64}", str(snapshot.get("fileSetSha256", ""))) is None
        or snapshot.get("fileCount") != len(files)
    ):
        raise CampaignError(f"{label} project snapshot is malformed")
    canonical_rows = []
    for index, raw in enumerate(files):
        row = _runtime_mapping(raw, f"{label} files[{index}]")
        relative = row.get("path")
        byte_count = row.get("bytes")
        digest = row.get("sha256")
        if (
            not isinstance(relative, str)
            or not relative
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or "\\" in relative
            or not isinstance(byte_count, int)
            or byte_count < 0
            or re.fullmatch(r"[0-9a-f]{64}", str(digest)) is None
        ):
            raise CampaignError(f"{label} project file row is malformed")
        canonical_rows.append((relative, byte_count, str(digest)))
    if len(canonical_rows) != len(set(row[0] for row in canonical_rows)):
        raise CampaignError(f"{label} project snapshot repeats a file")
    canonical = "".join(
        f"{digest}\t{byte_count}\t{relative}\n"
        for relative, byte_count, digest in sorted(canonical_rows)
    )
    if (
        snapshot["totalBytes"] != sum(row[1] for row in canonical_rows)
        or snapshot["fileSetSha256"] != _sha256_text(canonical)
    ):
        raise CampaignError(f"{label} project snapshot digest differs")
    return {
        "fileCount": snapshot["fileCount"],
        "totalBytes": snapshot["totalBytes"],
        "fileSetSha256": snapshot["fileSetSha256"],
        "files": files,
    }


def _global_init515_backup_project_manifest(snapshot: dict) -> dict:
    return {
        "projectName": "BEA",
        "fileCount": snapshot["fileCount"],
        "totalBytes": snapshot["totalBytes"],
        "structurallyComplete": True,
        "files": [
            {
                "relative_path": row["path"],
                "size": row["bytes"],
                "sha256": row["sha256"],
            }
            for row in snapshot["files"]
        ],
    }


def _validate_global_init515_backup_manifest_file(
    path: Path, snapshot: dict, label: str
) -> datetime:
    manifest = _promotion_json(path, label)
    created_at = _parse_utc_timestamp(manifest.get("createdAtUtc"), f"{label} creation")
    expected_project = _global_init515_backup_project_manifest(snapshot)
    expected_comparison = {
        "matches": True,
        "missing": [],
        "extra": [],
        "sizeDifferences": [],
        "hashDifferences": [],
        "missingCount": 0,
        "extraCount": 0,
        "sizeDiffCount": 0,
        "hashDiffCount": 0,
    }
    if (
        set(manifest)
        != {
            "schemaVersion",
            "createdAtUtc",
            "source",
            "destination",
            "sourceStable",
            "copyComparison",
            "readonlyOpen",
        }
        or manifest.get("schemaVersion") != "onslaught-ghidra-project-backup.v2"
        or manifest.get("source") != expected_project
        or manifest.get("destination") != expected_project
        or manifest.get("sourceStable") is not True
        or manifest.get("copyComparison") != expected_comparison
        or manifest.get("readonlyOpen") is not None
    ):
        raise CampaignError(f"{label} payload differs")
    return created_at


def _validate_global_init515_backup_manifests(
    evidence_root: Path,
    copy_manifest_stamp: object,
    *,
    backup_relative: str,
    restore_relative: str,
    snapshot: dict,
    label: str,
) -> dict:
    backup_path, backup_stamp = _validate_relative_evidence_stamp(
        evidence_root, copy_manifest_stamp, f"{label} backup manifest"
    )
    if backup_stamp["path"] != backup_relative:
        raise CampaignError(f"{label} backup manifest path differs")
    restore_path = _plain_contained_evidence_path(
        evidence_root, restore_relative, f"{label} restore manifest"
    )
    return {
        "backupPath": backup_path,
        "backupStamp": backup_stamp,
        "backupCreatedAt": _validate_global_init515_backup_manifest_file(
            backup_path, snapshot, f"{label} backup manifest"
        ),
        "restorePath": restore_path,
        "restoreCreatedAt": _validate_global_init515_backup_manifest_file(
            restore_path, snapshot, f"{label} restore manifest"
        ),
    }


def _global_init515_windows_batch_argv(
    headless: Path, arguments: list[str]
) -> list[str]:
    values = [str(headless.resolve()), *map(str, arguments)]
    return [
        str(Path(r"C:\Windows\System32\cmd.exe")),
        "/d",
        "/s",
        "/c",
        "call " + subprocess.list2cmdline(values),
    ]


def _validate_global_init515_tool_log(
    process: dict,
    *,
    prefix: str,
    tool: dict,
    expected_relative_path: str,
    label: str,
) -> None:
    if process["log"]["stamp"]["path"] != expected_relative_path:
        raise CampaignError(f"{label} log path differs")
    try:
        text = process["log"]["path"].read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise CampaignError(f"{label} log cannot be read: {exc}") from exc
    marker = (
        f"{prefix} path={tool['path']} bytes={tool['bytes']} "
        f"sha256={tool['sha256']}"
    )
    if text.count(marker) != 1 or any(
        bad in text
        for bad in (
            "REPORT SCRIPT ERROR",
            "FUNCTION_ENVELOPE_MUTATION_TAINTED",
            "INVENTORY_FAIL",
        )
    ):
        raise CampaignError(f"{label} log differs")


def _validate_global_init515_observation_stamp(
    root: Path,
    value: object,
    label: str,
    *,
    expected_project_root: Path,
    expected_state: str,
    expected_hashes: dict[str, str],
    expected_observation_label: str,
) -> dict:
    path, stamp = _validate_relative_evidence_stamp(root, value, label)
    observation = _promotion_json(path, label)
    if (
        observation.get("schema") != GLOBAL_INIT515_LIVE_OBSERVATION_SCHEMA
        or observation.get("label") != expected_observation_label
        or observation.get("projectRoot") != str(expected_project_root.resolve())
        or observation.get("rawStable") is not True
        or observation.get("classification")
        != {"state": expected_state, "reasons": []}
    ):
        raise CampaignError(
            f"{label} is not one exact stable {expected_state} observation"
        )
    if stamp["path"] != f"observations/{expected_observation_label}.json":
        raise CampaignError(f"{label} receipt path differs")
    observed_at = _parse_utc_timestamp(
        observation.get("observedAtUtc"), f"{label} observation"
    )
    expected_root = str(expected_project_root.resolve())
    if (
        observation.get("rawBefore", {}).get("root") != expected_root
        or observation.get("rawAfter", {}).get("root") != expected_root
    ):
        raise CampaignError(f"{label} raw snapshot roots differ")
    before = _project_snapshot_identity(observation.get("rawBefore"), f"{label} rawBefore")
    after = _project_snapshot_identity(observation.get("rawAfter"), f"{label} rawAfter")
    if before != after:
        raise CampaignError(f"{label} raw project changed during observation")
    artifacts = {}
    expected_artifact_paths = {
        "functions": f"runs/{expected_observation_label}-inventory/functions.tsv",
        "program": f"runs/{expected_observation_label}-inventory/program.tsv",
        "symbols": f"runs/{expected_observation_label}-symbols/target-symbols.tsv",
        "symbolsReady": f"runs/{expected_observation_label}-symbols/target-symbols.ready.json",
    }
    for field in ("functions", "program", "symbols", "symbolsReady"):
        artifact_path, artifact_stamp = _validate_relative_evidence_stamp(
            root, observation.get(field), f"{label} {field}"
        )
        if field in expected_hashes and artifact_stamp["sha256"] != expected_hashes[field]:
            raise CampaignError(
                f"{label} {field} is not the exact proven {expected_state} export"
            )
        if artifact_stamp["path"] != expected_artifact_paths[field]:
            raise CampaignError(f"{label} {field} path differs")
        artifacts[field] = {"path": artifact_path, "stamp": artifact_stamp}

    symbols_ready = _promotion_json(
        artifacts["symbolsReady"]["path"], f"{label} symbols READY"
    )
    expected_program = {
        "name": "BEA.exe",
        "md5": "3b456964020070efe696d2cc09464a55",
        "sha256": FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256,
        "imageBase": "0x00400000",
        "language": "x86:LE:32:default",
        "compilerSpec": "windows",
    }
    expected_tool = _exact_external_stamp(
        GLOBAL_INIT515_SYMBOL_TOOL_PATH,
        GLOBAL_INIT515_SYMBOL_TOOL_SHA256,
        f"{label} symbol tool",
    )
    expected_manifest = _exact_external_stamp(
        GLOBAL_INIT515_MANIFEST_PATH,
        GLOBAL_INIT515_MANIFEST_SHA256,
        f"{label} manifest",
    )
    expected_manifest["expectedCount"] = GLOBAL_INIT515_COUNT
    expected_output = {
        "path": str(artifacts["symbols"]["path"].resolve()),
        "bytes": artifacts["symbols"]["stamp"]["bytes"],
        "sha256": artifacts["symbols"]["stamp"]["sha256"],
    }
    expected_symbol_counts = (
        {
            "targets": GLOBAL_INIT515_COUNT,
            "targetSymbols": 513,
            "zeroSymbols": 2,
            "dynamicDefaultLabels": 513,
            "nonDynamicDefaultFunctions": 0,
            "outsideTargetSymbols": 86091,
        }
        if expected_state == "PRE"
        else {
            "targets": GLOBAL_INIT515_COUNT,
            "targetSymbols": 515,
            "zeroSymbols": 0,
            "dynamicDefaultLabels": 0,
            "nonDynamicDefaultFunctions": 515,
            "outsideTargetSymbols": 86091,
        }
    )
    if (
        symbols_ready.get("schemaVersion")
        != "bea.re.ghidra-target-symbol-inventory.v1"
        or symbols_ready.get("program") != expected_program
        or symbols_ready.get("tool") != expected_tool
        or symbols_ready.get("manifest") != expected_manifest
        or symbols_ready.get("output") != expected_output
        or symbols_ready.get("counts") != expected_symbol_counts
        or symbols_ready.get("outsideTargetSymbolsSha256")
        != GLOBAL_INIT515_OUTSIDE_SYMBOLS_SHA256
    ):
        raise CampaignError(f"{label} symbols READY differs")

    inventory_tool = _exact_external_stamp(
        GLOBAL_INIT515_INVENTORY_TOOL_PATH,
        GLOBAL_INIT515_INVENTORY_TOOL_SHA256,
        f"{label} inventory tool",
    )
    headless = _exact_external_stamp(
        GLOBAL_INIT515_ANALYZE_HEADLESS_PATH,
        GLOBAL_INIT515_ANALYZE_HEADLESS_SHA256,
        f"{label} analyzeHeadless",
    )
    inventory_argv = _global_init515_windows_batch_argv(
        Path(headless["path"]),
        [
            expected_root,
            "BEA",
            "-process",
            "BEA.exe",
            "-readOnly",
            "-noanalysis",
            "-scriptPath",
            str(GLOBAL_INIT515_INVENTORY_TOOL_PATH.resolve().parent),
            "-postScript",
            GLOBAL_INIT515_INVENTORY_TOOL_PATH.name,
            str(artifacts["functions"]["path"].resolve()),
            str(artifacts["program"]["path"].resolve()),
        ],
    )
    symbol_argv = _global_init515_windows_batch_argv(
        Path(headless["path"]),
        [
            expected_root,
            "BEA",
            "-process",
            "BEA.exe",
            "-readOnly",
            "-noanalysis",
            "-scriptPath",
            str(GLOBAL_INIT515_SYMBOL_TOOL_PATH.resolve().parent),
            "-postScript",
            GLOBAL_INIT515_SYMBOL_TOOL_PATH.name,
            str(GLOBAL_INIT515_MANIFEST_PATH.resolve()),
            GLOBAL_INIT515_MANIFEST_SHA256,
            str(GLOBAL_INIT515_COUNT),
            str(artifacts["symbols"]["path"].resolve()),
            str(artifacts["symbolsReady"]["path"].resolve()),
        ],
    )
    inventory_run = _validate_contained_process_stamp(
        root,
        observation.get("inventoryRun"),
        f"{label} inventory",
        expected_relative_path=f"runs/{expected_observation_label}-inventory/run.json",
        expected_id=f"{expected_observation_label}-inventory",
        expected_argv=inventory_argv,
    )
    symbol_run = _validate_contained_process_stamp(
        root,
        observation.get("symbolRun"),
        f"{label} symbols",
        expected_relative_path=f"runs/{expected_observation_label}-symbols/run.json",
        expected_id=f"{expected_observation_label}-symbols",
        expected_argv=symbol_argv,
    )
    _validate_global_init515_tool_log(
        inventory_run,
        prefix="INVENTORY_TOOL_OK",
        tool=inventory_tool,
        expected_relative_path=(
            f"runs/{expected_observation_label}-inventory/headless.partial.log"
        ),
        label=f"{label} inventory",
    )
    _validate_global_init515_tool_log(
        symbol_run,
        prefix="TARGET_SYMBOL_TOOL_OK",
        tool=expected_tool,
        expected_relative_path=(
            f"runs/{expected_observation_label}-symbols/headless.partial.log"
        ),
        label=f"{label} symbols",
    )
    if not (
        inventory_run["completedAt"] <= symbol_run["startedAt"]
        and symbol_run["completedAt"] <= observed_at
    ):
        raise CampaignError(f"{label} observation chronology differs")
    return {
        "path": path,
        "stamp": stamp,
        "observation": observation,
        "projectIdentity": after,
        "artifacts": artifacts,
        "inventoryRun": inventory_run,
        "symbolRun": symbol_run,
        "observedAt": observed_at,
    }


def _validate_post_observation_stamp(
    root: Path,
    value: object,
    label: str,
    *,
    expected_project_root: Path,
    expected_observation_label: str,
) -> dict:
    return _validate_global_init515_observation_stamp(
        root,
        value,
        label,
        expected_project_root=expected_project_root,
        expected_state="POST",
        expected_hashes={
            "functions": GLOBAL_INIT515_POST_FUNCTIONS_SHA256,
            "program": GLOBAL_INIT515_POST_PROGRAM_SHA256,
            "symbols": GLOBAL_INIT515_POST_SYMBOLS_SHA256,
        },
        expected_observation_label=expected_observation_label,
    )


def _validate_global_init515_reproductions(
    root: Path, value: object, label: str
) -> dict[str, dict]:
    reproductions = _runtime_mapping(value, label)
    expected_results = {
        "formal": {
            "verdict": "SURVIVED",
            "admissibleTargets": GLOBAL_INIT515_COUNT,
            "publicationStatus": "READY",
        },
        "lineage": {"status": "READY", "summary.rows": GLOBAL_INIT515_COUNT},
        "campaign": {
            "generation": 5,
            "counts.functions": 7595,
            "counts.residuals": 6618,
        },
    }
    python = _exact_external_stamp(
        GLOBAL_INIT515_PYTHON_PATH,
        GLOBAL_INIT515_PYTHON_SHA256,
        f"{label} Python",
    )
    formal_owner = _exact_external_stamp(
        GLOBAL_INIT515_FORMAL_OWNER_PATH,
        GLOBAL_INIT515_FORMAL_OWNER_SHA256,
        f"{label} formal owner",
    )
    lineage_owner = _exact_external_stamp(
        GLOBAL_INIT515_LINEAGE_OWNER_PATH,
        GLOBAL_INIT515_LINEAGE_OWNER_SHA256,
        f"{label} lineage owner",
    )
    campaign_owner = _exact_external_stamp(
        GLOBAL_INIT515_CAMPAIGN_OWNER_PATH,
        GLOBAL_INIT515_CAMPAIGN_OWNER_SHA256,
        f"{label} campaign owner",
    )
    expected_argv = {
        "formal": [
            python["path"],
            "-I",
            "-B",
            formal_owner["path"],
            "--verify-ready",
            str((GLOBAL_INIT515_FORMAL_ROOT / "proof.ready.json").resolve()),
        ],
        "lineage": [
            python["path"],
            "-I",
            "-B",
            lineage_owner["path"],
            "verify",
            "--bundle",
            str(GLOBAL_INIT515_LINEAGE_ROOT.resolve()),
        ],
        "campaign": [
            python["path"],
            "-B",
            campaign_owner["path"],
            "verify",
            "--campaign",
            str(GLOBAL_INIT515_CAMPAIGN_ROOT.resolve()),
        ],
    }
    validated: dict[str, dict] = {}
    for name, expected in expected_results.items():
        reproduction = _runtime_mapping(
            reproductions.get(name), f"{label} {name} reproduction"
        )
        run = _validate_contained_process_stamp(
            root,
            reproduction.get("run"),
            f"{label} {name} verifier",
            expected_relative_path=f"runs/authority-{name}/run.json",
            expected_id=f"authority-{name}",
            expected_argv=expected_argv[name],
        )
        payload = _runtime_mapping(
            reproduction.get("result"), f"{label} {name} result"
        )
        for key, expected_value in expected.items():
            actual: object = payload
            for part in key.split("."):
                actual = actual.get(part) if isinstance(actual, dict) else None
            if actual != expected_value:
                raise CampaignError(f"{label} {name} result differs")
        if run["log"]["stamp"]["path"] != f"runs/authority-{name}/headless.partial.log":
            raise CampaignError(f"{label} {name} log path differs")
        try:
            log_text = run["log"]["path"].read_text(
                encoding="utf-8", errors="strict"
            ).strip()
            if name == "campaign":
                prefix = "CAMPAIGN_VERIFIED "
                suffix = f" {GLOBAL_INIT515_CAMPAIGN_ROOT}"
                if not log_text.startswith(prefix) or not log_text.endswith(suffix):
                    raise CampaignError(f"{label} campaign log format differs")
                counts_text = log_text[len(prefix) : -len(suffix)]
                counts = ast.literal_eval(counts_text)
                if not isinstance(counts, dict):
                    raise CampaignError(f"{label} campaign counts differ")
                logged = {"generation": 5, "counts": counts}
            else:
                logged = json.loads(log_text)
        except (OSError, UnicodeError, json.JSONDecodeError, SyntaxError, ValueError) as exc:
            raise CampaignError(f"{label} {name} log cannot be parsed: {exc}") from exc
        if not isinstance(logged, dict) or not _same_json(logged, payload):
            raise CampaignError(f"{label} {name} log/result differs")
        validated[name] = {"run": run, "result": payload}
    if not (
        validated["formal"]["run"]["completedAt"]
        <= validated["lineage"]["run"]["startedAt"]
        and validated["lineage"]["run"]["completedAt"]
        <= validated["campaign"]["run"]["startedAt"]
    ):
        raise CampaignError(f"{label} verifier chronology differs")
    return validated


def _require_disjoint_project_files(
    first_root: Path,
    second_root: Path,
    files: list[object],
    label: str,
) -> None:
    first_files: list[Path] = []
    second_files: list[Path] = []
    for index, raw in enumerate(files):
        row = _runtime_mapping(raw, f"{label} files[{index}]")
        relative = str(row.get("path", ""))
        first_files.append(first_root / Path(relative))
        second_files.append(second_root / Path(relative))
    for first in first_files:
        for second in second_files:
            relative = f"{first.name}/{second.name}"
            try:
                if os.path.samefile(first, second):
                    raise CampaignError(f"{label} project copies alias: {relative}")
            except FileNotFoundError as exc:
                raise CampaignError(
                    f"{label} project copy file is absent: {relative}"
                ) from exc
            except OSError as exc:
                raise CampaignError(
                    f"{label} project copy identity failed: {exc}"
                ) from exc


def _validate_global_init515_prepared(
    owner_root: Path,
    value: object,
    *,
    live_root: Path,
) -> dict:
    path, stamp = _validate_relative_evidence_stamp(
        owner_root, value, "global-init515 prepared READY"
    )
    prepared = _promotion_json(path, "global-init515 prepared READY")
    if (
        prepared.get("schema") != GLOBAL_INIT515_LIVE_PREPARED_SCHEMA
        or prepared.get("status") != "READY"
        or stamp["path"] != "prepared.ready.json"
    ):
        raise CampaignError("global-init515 prepared READY identity differs")

    owner = _runtime_mapping(prepared.get("owner"), "global-init515 prepared owner")
    expected_owner = REPO_ROOT / "tools/ghidra_global_init515_live_promotion.py"
    if (
        Path(str(owner.get("path", ""))).resolve() != expected_owner.resolve()
        or owner.get("sha256") != GLOBAL_INIT515_LIVE_OWNER_SHA256
    ):
        raise CampaignError("global-init515 prepared owner identity differs")
    _exact_external_stamp(
        expected_owner,
        GLOBAL_INIT515_LIVE_OWNER_SHA256,
        "global-init515 prepared owner",
    )
    prepared_at = _parse_utc_timestamp(
        prepared.get("preparedAtUtc"), "global-init515 prepared"
    )
    mutex = _runtime_mapping(prepared.get("mutex"), "global-init515 prepared mutex")
    if mutex != {"name": GLOBAL_INIT515_MUTEX_NAME, "abandoned": False}:
        raise CampaignError("global-init515 prepared mutex differs")

    authority = _runtime_mapping(
        prepared.get("authority"), "global-init515 prepared authority"
    )
    formal_ready = _runtime_mapping(
        authority.get("formalReady"), "global-init515 prepared formal READY"
    )
    manifest = _runtime_mapping(
        authority.get("manifest"), "global-init515 prepared manifest"
    )
    lineage_ready = _runtime_mapping(
        authority.get("lineageReady"), "global-init515 prepared lineage READY"
    )
    campaign_ready = _runtime_mapping(
        authority.get("campaignReady"), "global-init515 prepared campaign READY"
    )
    program = _runtime_mapping(
        authority.get("program"), "global-init515 prepared program"
    )
    expected_formal_ready_path = GLOBAL_INIT515_FORMAL_ROOT / "proof.ready.json"
    expected_lineage_ready_path = GLOBAL_INIT515_LINEAGE_ROOT / "READY.json"
    expected_campaign_ready_path = GLOBAL_INIT515_CAMPAIGN_ROOT / "campaign.ready.json"
    if (
        formal_ready
        != {
            "path": str(expected_formal_ready_path.resolve()),
            "sha256": GLOBAL_INIT515_FORMAL_READY_SHA256,
        }
        or manifest
        != {
            "path": str(GLOBAL_INIT515_MANIFEST_PATH.resolve()),
            "sha256": GLOBAL_INIT515_MANIFEST_SHA256,
            "count": GLOBAL_INIT515_COUNT,
        }
        or lineage_ready
        != {
            "path": str(expected_lineage_ready_path.resolve()),
            "sha256": GLOBAL_INIT515_LINEAGE_READY_SHA256,
        }
        or campaign_ready
        != {
            "path": str(expected_campaign_ready_path.resolve()),
            "sha256": FROZEN_V5_CAMPAIGN_CARRY_READY_SHA256,
        }
        or program
        != {
            "name": "BEA.exe",
            "md5": "3b456964020070efe696d2cc09464a55",
            "sha256": FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256,
            "imageBase": "0x00400000",
        }
        or authority.get("liveProject") != str(live_root.resolve())
    ):
        raise CampaignError("global-init515 prepared authority differs")
    for authority_path, authority_sha, authority_label in (
        (
            expected_formal_ready_path,
            GLOBAL_INIT515_FORMAL_READY_SHA256,
            "global-init515 formal READY",
        ),
        (
            GLOBAL_INIT515_MANIFEST_PATH,
            GLOBAL_INIT515_MANIFEST_SHA256,
            "global-init515 manifest",
        ),
        (
            expected_lineage_ready_path,
            GLOBAL_INIT515_LINEAGE_READY_SHA256,
            "global-init515 lineage READY",
        ),
        (
            expected_campaign_ready_path,
            FROZEN_V5_CAMPAIGN_CARRY_READY_SHA256,
            "global-init515 campaign READY",
        ),
    ):
        _exact_external_stamp(authority_path, authority_sha, authority_label)

    preimage_raw = _runtime_mapping(
        prepared.get("livePreimage"), "global-init515 prepared live preimage"
    )
    if preimage_raw.get("root") != str(live_root.resolve()):
        raise CampaignError("global-init515 prepared live preimage root differs")
    preimage = _project_snapshot_identity(
        preimage_raw, "global-init515 prepared live preimage"
    )
    if preimage["fileSetSha256"] != GLOBAL_INIT515_PRE_FILESET_SHA256:
        raise CampaignError("global-init515 prepared live preimage bytes differ")

    reproductions = _validate_global_init515_reproductions(
        owner_root,
        prepared.get("reproductions"),
        "global-init515 prepared authority",
    )
    quiescence_times: dict[str, datetime] = {}
    for field in ("firstQuiescence", "finalQuiescence"):
        quiescence = _runtime_mapping(
            prepared.get(field), f"global-init515 prepared {field}"
        )
        checked_at = _parse_utc_timestamp(
            quiescence.get("checkedAtUtc"), f"global-init515 prepared {field}"
        )
        if (
            quiescence.get("javaProcesses") != []
            or quiescence.get("nativeLockAbsent") is not True
            or quiescence.get("exclusiveFilesProbed") != preimage["fileCount"]
            or quiescence.get("projectFileSetSha256")
            != preimage["fileSetSha256"]
        ):
            raise CampaignError(f"global-init515 prepared {field} differs")
        quiescence_times[field] = checked_at

    pre_hashes = {
        "functions": GLOBAL_INIT515_PRE_FUNCTIONS_SHA256,
        "program": GLOBAL_INIT515_PRE_PROGRAM_SHA256,
        "symbols": GLOBAL_INIT515_PRE_SYMBOLS_SHA256,
    }
    initial = _validate_global_init515_observation_stamp(
        owner_root,
        prepared.get("initialObservation"),
        "global-init515 prepared initial observation",
        expected_project_root=live_root,
        expected_state="PRE",
        expected_hashes=pre_hashes,
        expected_observation_label="live-pre-initial",
    )
    final = _validate_global_init515_observation_stamp(
        owner_root,
        prepared.get("finalObservation"),
        "global-init515 prepared final observation",
        expected_project_root=live_root,
        expected_state="PRE",
        expected_hashes=pre_hashes,
        expected_observation_label="live-pre-final",
    )
    if initial["projectIdentity"] != preimage or final["projectIdentity"] != preimage:
        raise CampaignError("global-init515 prepared live PRE observations differ")

    pre_backup = _runtime_mapping(
        prepared.get("preBackup"), "global-init515 prepared PRE backup"
    )
    if pre_backup.get("expectedState") != "PRE":
        raise CampaignError("global-init515 prepared PRE backup state differs")
    backup_root = _resolve_repo_or_absolute(
        pre_backup.get("backupRoot"), "global-init515 prepared PRE backup root"
    )
    restore_root = _resolve_repo_or_absolute(
        pre_backup.get("restoreRoot"), "global-init515 prepared PRE restore root"
    )
    expected_backup_root = owner_root / "backups/pre-live"
    expected_restore_root = owner_root / "backups/pre-live-restore-drill"
    if (
        backup_root != expected_backup_root.resolve()
        or restore_root != expected_restore_root.resolve()
    ):
        raise CampaignError("global-init515 prepared PRE backup roots differ")
    if len({str(live_root.resolve()), str(backup_root), str(restore_root)}) != 3:
        raise CampaignError("global-init515 prepared PRE roots are not disjoint")
    source_raw = _runtime_mapping(
        pre_backup.get("sourceSnapshot"),
        "global-init515 prepared PRE source snapshot",
    )
    backup_raw = _runtime_mapping(
        pre_backup.get("backupSnapshot"),
        "global-init515 prepared PRE backup snapshot",
    )
    restore_raw = _runtime_mapping(
        pre_backup.get("restoreSnapshot"),
        "global-init515 prepared PRE restore snapshot",
    )
    if (
        source_raw.get("root") != str(live_root.resolve())
        or backup_raw.get("root") != str(backup_root.resolve())
        or restore_raw.get("root") != str(restore_root.resolve())
    ):
        raise CampaignError("global-init515 prepared PRE snapshot roots differ")
    source_identity = _project_snapshot_identity(
        source_raw, "global-init515 prepared PRE source snapshot"
    )
    backup_identity = _project_snapshot_identity(
        backup_raw, "global-init515 prepared PRE backup snapshot"
    )
    restore_identity = _project_snapshot_identity(
        restore_raw, "global-init515 prepared PRE restore snapshot"
    )
    if not source_identity == backup_identity == restore_identity == preimage:
        raise CampaignError("global-init515 prepared PRE backup/restore bytes differ")
    for project_root, snapshot, backup_label in (
        (backup_root, backup_raw, "global-init515 prepared PRE backup"),
        (restore_root, restore_raw, "global-init515 prepared PRE restore drill"),
    ):
        expected_rows = [
            (
                str(row.get("path", "")),
                _integer(row.get("bytes"), -1),
                str(row.get("sha256", "")),
            )
            for row in _runtime_list(snapshot.get("files"), f"{backup_label} files")
        ]
        _verify_project_manifest_bytes(
            project_root,
            expected_rows,
            "BEA",
            backup_label,
            require_single_link=True,
        )
    _require_disjoint_project_files(
        backup_root,
        restore_root,
        _runtime_list(backup_raw.get("files"), "global-init515 PRE backup files"),
        "global-init515 prepared PRE backup/restore",
    )
    pre_manifests = _validate_global_init515_backup_manifests(
        owner_root,
        pre_backup.get("copyManifest"),
        backup_relative="backups/pre-live/backup_manifest.json",
        restore_relative="backups/pre-live-restore-drill/backup_manifest.json",
        snapshot=preimage,
        label="global-init515 prepared PRE",
    )
    backup_observation = _validate_global_init515_observation_stamp(
        owner_root,
        pre_backup.get("backupObservation"),
        "global-init515 prepared PRE backup observation",
        expected_project_root=backup_root,
        expected_state="PRE",
        expected_hashes=pre_hashes,
        expected_observation_label="pre-live-backup",
    )
    restore_observation = _validate_global_init515_observation_stamp(
        owner_root,
        pre_backup.get("restoreObservation"),
        "global-init515 prepared PRE restore observation",
        expected_project_root=restore_root,
        expected_state="PRE",
        expected_hashes=pre_hashes,
        expected_observation_label="pre-live-restore",
    )
    if (
        backup_observation["projectIdentity"] != preimage
        or restore_observation["projectIdentity"] != preimage
    ):
        raise CampaignError("global-init515 prepared PRE backup observations differ")
    prepared_observations = (
        ("initial", initial),
        ("backup", backup_observation),
        ("restore", restore_observation),
        ("final", final),
    )
    _require_disjoint_evidence_files(
        [
            item
            for observation_label, prepared_observation in prepared_observations
            for item in _global_init515_observation_evidence_files(
                prepared_observation, f"prepared {observation_label}"
            )
        ],
        "global-init515 prepared observation evidence",
    )
    _require_disjoint_evidence_files(
        _global_init515_reproduction_evidence_files(reproductions, "prepared"),
        "global-init515 prepared authority evidence",
    )
    first_quiescence_at = quiescence_times["firstQuiescence"]
    final_quiescence_at = quiescence_times["finalQuiescence"]
    if not (
        first_quiescence_at <= reproductions["formal"]["run"]["startedAt"]
        and reproductions["campaign"]["run"]["completedAt"]
        <= initial["inventoryRun"]["startedAt"]
        and initial["observedAt"] <= pre_manifests["backupCreatedAt"]
        and pre_manifests["backupCreatedAt"]
        <= backup_observation["inventoryRun"]["startedAt"]
        and backup_observation["observedAt"]
        <= pre_manifests["restoreCreatedAt"]
        and pre_manifests["restoreCreatedAt"]
        <= restore_observation["inventoryRun"]["startedAt"]
        and restore_observation["observedAt"] <= final["inventoryRun"]["startedAt"]
        and final["observedAt"] <= final_quiescence_at <= prepared_at
    ):
        raise CampaignError("global-init515 prepared chronology differs")
    return {
        "path": path,
        "stamp": stamp,
        "prepared": prepared,
        "preimage": preimage,
        "reproductions": reproductions,
        "initialObservation": initial,
        "finalObservation": final,
        "preBackup": pre_backup,
        "backupObservation": backup_observation,
        "restoreObservation": restore_observation,
        "backupManifests": pre_manifests,
        "preparedAt": prepared_at,
        "firstQuiescenceAt": first_quiescence_at,
        "finalQuiescenceAt": final_quiescence_at,
    }


def _validate_global_init515_apply_artifacts(
    evidence_root: Path,
    process: dict,
) -> dict:
    output_path = _plain_contained_evidence_path(
        evidence_root,
        "runs/live-apply/envelopes.tsv",
        "global-init515 live apply TSV",
    )
    ready_path = _plain_contained_evidence_path(
        evidence_root,
        "runs/live-apply/envelopes.ready.json",
        "global-init515 live apply READY",
    )
    output_external = _exact_external_stamp(
        output_path,
        GLOBAL_INIT515_APPLY_OUTPUT_SHA256,
        "global-init515 live apply TSV",
    )
    tool_external = _exact_external_stamp(
        GLOBAL_INIT515_ENVELOPE_TOOL_PATH,
        GLOBAL_INIT515_ENVELOPE_TOOL_SHA256,
        "global-init515 live apply tool",
    )
    manifest_external = _exact_external_stamp(
        GLOBAL_INIT515_MANIFEST_PATH,
        GLOBAL_INIT515_MANIFEST_SHA256,
        "global-init515 live apply manifest",
    )
    headless_external = _exact_external_stamp(
        GLOBAL_INIT515_ANALYZE_HEADLESS_PATH,
        GLOBAL_INIT515_ANALYZE_HEADLESS_SHA256,
        "global-init515 analyzeHeadless",
    )
    ready = _promotion_json(ready_path, "global-init515 live apply READY")
    expected_manifest = {**manifest_external, "expectedCount": GLOBAL_INIT515_COUNT}
    expected_program = {
        "name": "BEA.exe",
        "executableMd5": "3b456964020070efe696d2cc09464a55",
        "executableSha256": FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256,
        "imageBase": "0x00400000",
        "language": "x86:LE:32:default",
        "compilerSpec": "windows",
    }
    expected_counts = {
        "targets": GLOBAL_INIT515_COUNT,
        "functionsBefore": 7595,
        "functionsTransient": 8110,
        "functionManagerViewAfterNestedTransaction": 8110,
        "instructionsBefore": 549864,
        "instructionsAfter": 549864,
    }
    flags = (
        ready.get("commitRequested"),
        ready.get("rollbackRequested"),
        ready.get("transactionEndReturnedCommitted"),
        ready.get("loadedStateVerified"),
        ready.get("reopenVerificationRequired"),
    )
    ready_completed_at = _parse_utc_timestamp(
        ready.get("completedAtUtc"), "global-init515 live apply READY completion"
    )
    if (
        ready.get("schemaVersion") != "bea-ghidra-function-body-envelope.v3"
        or ready.get("mode") != "apply"
        or ready.get("tool") != tool_external
        or ready.get("program") != expected_program
        or ready.get("manifest") != expected_manifest
        or ready.get("output") != output_external
        or ready.get("counts") != expected_counts
        or flags != (True, False, False, False, True)
        or ready.get("namesAuthorized") is not False
        or ready.get("functionKindsBoundByManifest") is not True
        or ready.get("loadedOrTransientEnvelopesVerified") is not True
    ):
        raise CampaignError("global-init515 live apply READY differs")

    command_values = [
        headless_external["path"],
        str(Path(r"C:\Users\david\Ghidra\Projects").resolve()),
        "BEA",
        "-process",
        "BEA.exe",
        "-noanalysis",
        "-scriptPath",
        str(GLOBAL_INIT515_ENVELOPE_TOOL_PATH.resolve().parent),
        "-postScript",
        GLOBAL_INIT515_ENVELOPE_TOOL_PATH.name,
        str(GLOBAL_INIT515_MANIFEST_PATH.resolve()),
        GLOBAL_INIT515_MANIFEST_SHA256,
        str(GLOBAL_INIT515_COUNT),
        str(output_path.resolve()),
        str(ready_path.resolve()),
        "apply",
    ]
    expected_argv = [
        str(Path(r"C:\Windows\System32\cmd.exe")),
        "/d",
        "/s",
        "/c",
        "call " + subprocess.list2cmdline(command_values),
    ]
    if (
        process["stamp"]["path"] != "runs/live-apply/run.json"
        or process["receipt"].get("id") != "live-apply"
        or process["receipt"].get("argv") != expected_argv
        or process["log"]["stamp"]["path"]
        != "runs/live-apply/headless.partial.log"
    ):
        raise CampaignError("global-init515 live apply process/argv differs")
    try:
        log_text = process["log"]["path"].read_text(
            encoding="utf-8", errors="replace"
        )
    except OSError as exc:
        raise CampaignError(f"global-init515 live apply log cannot be read: {exc}") from exc
    marker = (
        "FUNCTION_ENVELOPE_TOOL_OK "
        f"path={tool_external['path']} bytes={tool_external['bytes']} "
        f"sha256={tool_external['sha256']}"
    )
    if log_text.count(marker) != 1 or any(
        bad in log_text
        for bad in (
            "REPORT SCRIPT ERROR",
            "FUNCTION_ENVELOPE_MUTATION_TAINTED",
            "INVENTORY_FAIL",
        )
    ):
        raise CampaignError("global-init515 live apply log differs")
    try:
        ready_measured = coverage.file_stamp(ready_path)
    except OSError as exc:
        raise CampaignError(
            f"global-init515 live apply READY cannot be rehashed: {exc}"
        ) from exc
    ready_external = {
        "path": str(ready_path.resolve()),
        "bytes": ready_measured["bytes"],
        "sha256": ready_measured["sha256"],
    }
    return {
        "output": output_external,
        "ready": ready_external,
        "readyPayload": ready,
        "expectedArgv": expected_argv,
        "completedAt": ready_completed_at,
        "outputPath": output_path,
        "readyPath": ready_path,
    }


def validate_global_init515_live_promotion(evidence_path: Path) -> dict:
    try:
        evidence_path = ghidra_backup.resolve_plain_path(
            evidence_path, "global-init515 live promotion READY", strict=True
        )
    except (ghidra_backup.BackupError, OSError) as exc:
        raise CampaignError(
            f"global-init515 live promotion READY is not plain: {exc}"
        ) from exc
    if evidence_path.stat().st_nlink != 1:
        raise CampaignError("global-init515 live promotion READY has multiple hard links")
    evidence_root = evidence_path.parent
    evidence_stamp = coverage.file_stamp(evidence_path)
    if evidence_path != evidence_root / "promotion.ready.json":
        raise CampaignError("global-init515 live promotion READY path differs")
    ready = _promotion_json(evidence_path, "global-init515 live promotion READY")
    if (
        ready.get("schema") != GLOBAL_INIT515_LIVE_PROMOTION_SCHEMA
        or ready.get("status") != "READY"
        or ready.get("state") != "POST"
        or ready.get("protocol") != {"status": "COMPLETE", "reasons": []}
        or ready.get("campaignPublicationAuthorized") is not True
        or ready.get("mutationSpawns") != 1
        or ready.get("retryAuthorized") is not False
        or ready.get("automaticRestorePerformed") is not False
        or ready.get("observationError") not in (None, "")
        or ready.get("postBackupError") not in (None, "")
    ):
        raise CampaignError("global-init515 live promotion is not publication-ready POST evidence")
    completed_at = _parse_utc_timestamp(
        ready.get("completedAtUtc"), "global-init515 live promotion completion"
    )
    measured_at = str(ready.get("completedAtUtc"))

    result_path, result_stamp = _validate_relative_evidence_stamp(
        evidence_root, ready.get("result"), "global-init515 promotion result"
    )
    result = _promotion_json(result_path, "global-init515 promotion result")
    if result_stamp["path"] != "promotion.result.json":
        raise CampaignError("global-init515 promotion result path differs")
    ready_without_wrapper = {
        key: value for key, value in ready.items() if key not in {"status", "result"}
    }
    if not _same_json(result, ready_without_wrapper):
        raise CampaignError("global-init515 promotion READY and result disagree")

    process = _validate_contained_process_stamp(
        evidence_root, ready.get("process"), "global-init515 live apply"
    )
    live_root = Path(r"C:\Users\david\Ghidra\Projects")
    observation = _validate_post_observation_stamp(
        evidence_root,
        ready.get("observation"),
        "global-init515 live observation",
        expected_project_root=live_root,
        expected_observation_label="live-post-attempt",
    )
    attempt_path, attempt_stamp = _validate_relative_evidence_stamp(
        evidence_root, ready.get("attempt"), "global-init515 apply intent"
    )
    attempt = _promotion_json(attempt_path, "global-init515 apply intent")
    if attempt_stamp["path"] != "attempt.started.json":
        raise CampaignError("global-init515 apply intent path differs")
    prepared = _validate_global_init515_prepared(
        evidence_root.parent,
        attempt.get("preparedReady"),
        live_root=live_root,
    )
    attempt_preimage_raw = _runtime_mapping(
        attempt.get("livePreimage"), "global-init515 apply intent preimage"
    )
    if attempt_preimage_raw.get("root") != str(live_root.resolve()):
        raise CampaignError("global-init515 apply intent preimage root differs")
    attempt_preimage = _project_snapshot_identity(
        attempt_preimage_raw, "global-init515 apply intent preimage"
    )
    apply_artifacts = _validate_global_init515_apply_artifacts(evidence_root, process)
    argv = _runtime_list(attempt.get("argv"), "global-init515 apply intent argv")
    attempt_at = _parse_utc_timestamp(
        attempt.get("startedAtUtc"), "global-init515 apply intent"
    )
    if (
        attempt.get("schema") != "bea.re.ghidra-global-init515-live-attempt.v1"
        or attempt.get("mutex")
        != {"name": GLOBAL_INIT515_MUTEX_NAME, "abandoned": False}
        or attempt.get("mutationSpawnLimit") != 1
        or attempt.get("retryAuthorized") is not False
        or argv != process["receipt"].get("argv")
        or argv != apply_artifacts["expectedArgv"]
        or attempt_preimage != prepared["preimage"]
        or attempt_preimage == observation["projectIdentity"]
    ):
        raise CampaignError("global-init515 apply intent/process identity differs")

    post_backup = _runtime_mapping(ready.get("postBackup"), "global-init515 POST backup")
    if post_backup.get("expectedState") != "POST":
        raise CampaignError("global-init515 POST backup state differs")
    backup_root = _resolve_repo_or_absolute(
        post_backup.get("backupRoot"), "global-init515 POST backup root"
    )
    restore_root = _resolve_repo_or_absolute(
        post_backup.get("restoreRoot"), "global-init515 POST restore root"
    )
    expected_backup_root = evidence_root / "backups/post-live"
    expected_restore_root = evidence_root / "backups/post-live-restore-drill"
    if (
        backup_root != expected_backup_root.resolve()
        or restore_root != expected_restore_root.resolve()
    ):
        raise CampaignError("global-init515 POST backup roots differ")
    if len({str(live_root.resolve()), str(backup_root), str(restore_root)}) != 3:
        raise CampaignError("global-init515 live/backup/restore roots are not disjoint")
    source_raw = _runtime_mapping(
        post_backup.get("sourceSnapshot"), "global-init515 POST source snapshot"
    )
    backup_raw = _runtime_mapping(
        post_backup.get("backupSnapshot"), "global-init515 POST backup snapshot"
    )
    restore_raw = _runtime_mapping(
        post_backup.get("restoreSnapshot"), "global-init515 POST restore snapshot"
    )
    if (
        source_raw.get("root") != str(live_root.resolve())
        or backup_raw.get("root") != str(backup_root.resolve())
        or restore_raw.get("root") != str(restore_root.resolve())
    ):
        raise CampaignError("global-init515 POST snapshot roots differ")
    source_identity = _project_snapshot_identity(
        source_raw, "global-init515 POST source snapshot"
    )
    backup_identity = _project_snapshot_identity(
        backup_raw, "global-init515 POST backup snapshot"
    )
    restore_identity = _project_snapshot_identity(
        restore_raw, "global-init515 POST restore snapshot"
    )
    if not (
        source_identity
        == backup_identity
        == restore_identity
        == observation["projectIdentity"]
    ):
        raise CampaignError("global-init515 POST backup/restore bytes differ from live POST")
    for project_root, snapshot, label in (
        (backup_root, backup_raw, "global-init515 POST backup"),
        (restore_root, restore_raw, "global-init515 POST restore drill"),
    ):
        expected_rows = [
            (str(row.get("path", "")), _integer(row.get("bytes"), -1), str(row.get("sha256", "")))
            for row in _runtime_list(snapshot.get("files"), f"{label} files")
        ]
        _verify_project_manifest_bytes(
            project_root,
            expected_rows,
            "BEA",
            label,
            require_single_link=True,
        )
    post_manifests = _validate_global_init515_backup_manifests(
        evidence_root,
        post_backup.get("copyManifest"),
        backup_relative="backups/post-live/backup_manifest.json",
        restore_relative="backups/post-live-restore-drill/backup_manifest.json",
        snapshot=source_identity,
        label="global-init515 POST",
    )
    _require_disjoint_project_files(
        backup_root,
        restore_root,
        _runtime_list(
            backup_raw.get("files"),
            "global-init515 POST backup files",
        ),
        "global-init515 POST backup/restore",
    )
    backup_observation = _validate_post_observation_stamp(
        evidence_root,
        post_backup.get("backupObservation"),
        "global-init515 POST backup observation",
        expected_project_root=backup_root,
        expected_observation_label="post-live-backup",
    )
    restore_observation = _validate_post_observation_stamp(
        evidence_root,
        post_backup.get("restoreObservation"),
        "global-init515 POST restore observation",
        expected_project_root=restore_root,
        expected_observation_label="post-live-restore",
    )
    if (
        backup_observation["projectIdentity"] != source_identity
        or restore_observation["projectIdentity"] != source_identity
    ):
        raise CampaignError("global-init515 POST backup observations differ")

    reproductions = _validate_global_init515_reproductions(
        evidence_root,
        ready.get("authorityReproductions"),
        "global-init515 authority",
    )
    post_observations = (
        ("live", observation),
        ("backup", backup_observation),
        ("restore", restore_observation),
    )
    _require_disjoint_evidence_files(
        [
            item
            for observation_label, post_observation in post_observations
            for item in _global_init515_observation_evidence_files(
                post_observation, f"post {observation_label}"
            )
        ],
        "global-init515 POST observation evidence",
    )
    _require_disjoint_evidence_files(
        [
            *_global_init515_reproduction_evidence_files(
                prepared["reproductions"], "prepared"
            ),
            *_global_init515_reproduction_evidence_files(reproductions, "promotion"),
        ],
        "global-init515 authority phase evidence",
    )
    _require_disjoint_evidence_files(
        [
            ("promotion READY", evidence_path),
            ("promotion result", result_path),
            ("apply intent", attempt_path),
            ("apply process receipt", process["path"]),
            ("apply process log", process["log"]["path"]),
            ("apply output", apply_artifacts["outputPath"]),
            ("apply READY", apply_artifacts["readyPath"]),
        ],
        "global-init515 apply evidence",
    )
    if not (
        prepared["preparedAt"] <= reproductions["formal"]["run"]["startedAt"]
        and reproductions["campaign"]["run"]["completedAt"] <= attempt_at
        and attempt_at <= process["startedAt"]
        and process["startedAt"] <= apply_artifacts["completedAt"]
        and apply_artifacts["completedAt"] <= process["completedAt"]
        and process["completedAt"] <= observation["inventoryRun"]["startedAt"]
        and observation["observedAt"] <= post_manifests["backupCreatedAt"]
        and post_manifests["backupCreatedAt"]
        <= backup_observation["inventoryRun"]["startedAt"]
        and backup_observation["observedAt"]
        <= post_manifests["restoreCreatedAt"]
        and post_manifests["restoreCreatedAt"]
        <= restore_observation["inventoryRun"]["startedAt"]
        and restore_observation["observedAt"] <= completed_at
    ):
        raise CampaignError("global-init515 live promotion chronology differs")

    return {
        "ready": ready,
        "evidenceStamp": {**evidence_stamp, "path": str(evidence_path)},
        "resultStamp": result_stamp,
        "attemptStamp": attempt_stamp,
        "prepared": prepared,
        "process": process,
        "applyArtifacts": apply_artifacts,
        "observation": observation,
        "postBackup": post_backup,
        "postBackupManifests": post_manifests,
        "backupObservation": backup_observation,
        "restoreObservation": restore_observation,
        "measuredAtUtc": measured_at,
    }


def validate_global_init515_lineage(lineage_root: Path) -> dict:
    lineage_root = lineage_root.resolve()
    ready_path = lineage_root / "READY.json"
    owner_path = lineage_root / "lineage-owner.py"
    lineage_path = lineage_root / "lineage515.tsv"
    if coverage.sha256_of(ready_path) != GLOBAL_INIT515_LINEAGE_READY_SHA256:
        raise CampaignError("global-init515 lineage READY hash differs")
    if coverage.sha256_of(owner_path) != GLOBAL_INIT515_LINEAGE_OWNER_SHA256:
        raise CampaignError("global-init515 lineage owner hash differs")
    if coverage.sha256_of(lineage_path) != GLOBAL_INIT515_LINEAGE_TSV_SHA256:
        raise CampaignError("global-init515 lineage TSV hash differs")
    completed = subprocess.run(
        [sys.executable, "-I", "-B", str(owner_path), "verify", "--bundle", str(lineage_root)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    if completed.returncode != 0:
        raise CampaignError(
            "global-init515 lineage owner refused: "
            + (completed.stderr.strip() or completed.stdout.strip())
        )
    result = _runtime_mapping(
        json.loads(completed.stdout), "global-init515 lineage verifier result"
    )
    if (
        result.get("schema") != GLOBAL_INIT515_LINEAGE_SCHEMA
        or result.get("status") != "READY"
        or result.get("readySha256") != GLOBAL_INIT515_LINEAGE_READY_SHA256
        or result.get("summary", {}).get("rows") != GLOBAL_INIT515_COUNT
    ):
        raise CampaignError("global-init515 lineage verifier result differs")
    ready = _promotion_json(ready_path, "global-init515 lineage READY")
    if (
        ready.get("schema") != GLOBAL_INIT515_LINEAGE_SCHEMA
        or ready.get("status") != "READY"
        or ready.get("targetSetSha256") != GLOBAL_INIT515_TARGET_SET_SHA256
        or ready.get("summary", {}).get("rows") != GLOBAL_INIT515_COUNT
    ):
        raise CampaignError("global-init515 lineage READY values differ")
    rows = _read_tsv(lineage_path)
    if len(rows) != GLOBAL_INIT515_COUNT:
        raise CampaignError("global-init515 lineage row count differs")
    return {
        "root": lineage_root,
        "ready": ready,
        "readyStamp": {**coverage.file_stamp(ready_path), "path": "READY.json"},
        "ownerStamp": {**coverage.file_stamp(owner_path), "path": "lineage-owner.py"},
        "lineageStamp": {**coverage.file_stamp(lineage_path), "path": "lineage515.tsv"},
        "rows": rows,
    }


def _unique_row_map(rows: list[dict[str, str]], key: str, label: str) -> dict[str, dict[str, str]]:
    values = [row.get(key, "") for row in rows]
    if any(not value for value in values) or len(values) != len(set(values)):
        raise CampaignError(f"{label} contains missing or duplicate {key} values")
    return {row[key]: row for row in rows}


def validate_global_init515_post_reseed(
    campaign: Path,
    receipt: dict,
    lineage: dict,
) -> dict:
    expected_counts = {
        "functions": 8110,
        "residuals": 6103,
        "questions": 15223,
        "scenarios": 72,
        "levers": 914,
        "contracts": 14213,
        "adjudications": 2,
        "supersessions": 40,
    }
    parent = _runtime_mapping(receipt.get("parentCampaign"), "global-init515 reseed parent")
    parent_ready = _runtime_mapping(
        parent.get("ready"), "global-init515 reseed parent READY"
    )
    advance = _runtime_mapping(receipt.get("advance"), "global-init515 reseed advance")
    if (
        receipt.get("generation") != 6
        or receipt.get("counts") != expected_counts
        or advance.get("kind") != CAMPAIGN_RESEED_KIND
        or advance.get("schema") != CAMPAIGN_RESEED_SCHEMA
        or parent_ready.get("sha256") != FROZEN_V5_CAMPAIGN_CARRY_READY_SHA256
        or _resolve_repo_or_absolute(parent.get("path"), "global-init515 reseed parent")
        != FROZEN_V5_CAMPAIGN_CARRY_ROOT.resolve()
    ):
        raise CampaignError("global-init515 post reseed is not the exact generation-5 successor")
    carried = _runtime_mapping(advance.get("carried"), "global-init515 reseed carry report")
    stale = {key: value for key, value in carried.items() if key.startswith("stale")}
    if not stale or any(value != 0 for value in stale.values()):
        raise CampaignError("global-init515 post reseed lost campaign lineage")

    generation5_receipt = _verify_campaign_carry_source(FROZEN_V5_CAMPAIGN_CARRY_ROOT)
    if generation5_receipt.get("generation") != 5:
        raise CampaignError("global-init515 frozen generation-5 identity differs")
    generation5_rows = {
        "residuals": _read_tsv(FROZEN_V5_CAMPAIGN_CARRY_ROOT / "campaign-residuals.tsv"),
        "questions": _read_tsv(FROZEN_V5_CAMPAIGN_CARRY_ROOT / "campaign-questions.tsv"),
        "contracts": _read_tsv(FROZEN_V5_CAMPAIGN_CARRY_ROOT / "campaign-contracts.tsv"),
        "supersessions": _read_tsv(FROZEN_V5_CAMPAIGN_CARRY_ROOT / "campaign-supersessions.tsv"),
    }
    fresh = {
        "functions": _read_tsv(campaign / "campaign-functions.tsv"),
        "residuals": _read_tsv(campaign / "campaign-residuals.tsv"),
        "questions": _read_tsv(campaign / "campaign-questions.tsv"),
        "scenarios": _read_tsv(campaign / "campaign-scenarios.tsv"),
        "levers": _read_tsv(campaign / "campaign-levers.tsv"),
        "contracts": _read_tsv(campaign / "campaign-contracts.tsv"),
        "adjudications": _read_tsv(campaign / "campaign-adjudications.tsv"),
        "supersessions": _read_tsv(campaign / "campaign-supersessions.tsv"),
    }
    maps = {
        "functions": _unique_row_map(fresh["functions"], "entityKey", "post-reseed functions"),
        "residuals": _unique_row_map(fresh["residuals"], "entityKey", "post-reseed residuals"),
        "questions": _unique_row_map(fresh["questions"], "questionId", "post-reseed questions"),
        "contracts": _unique_row_map(fresh["contracts"], "contractId", "post-reseed contracts"),
        "levers": _unique_row_map(fresh["levers"], "regionKey", "post-reseed levers"),
    }
    generation5_maps = {
        "residuals": _unique_row_map(
            generation5_rows["residuals"], "entityKey", "generation-5 residuals"
        ),
        "questions": _unique_row_map(
            generation5_rows["questions"], "questionId", "generation-5 questions"
        ),
        "contracts": _unique_row_map(
            generation5_rows["contracts"], "contractId", "generation-5 contracts"
        ),
    }
    existing_old = {row.get("oldEntityKey") for row in fresh["supersessions"]}
    specimen = FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256
    image_base = 0x00400000
    mappings = []
    seen = {"old": set(), "new": set(), "question": set(), "contract": set()}
    for row in lineage["rows"]:
        start = int(row["entry"], 16)
        range_parts = row["expectedRanges"].split("-")
        if len(range_parts) != 2:
            raise CampaignError(f"global-init515 lineage range framing differs at {row['entry']}")
        range_start, end = (int(value, 16) for value in range_parts)
        body_bytes = _integer(row.get("expectedBodyBytes"), -1)
        start_rva = start - image_base
        end_rva = end - image_base
        range_set = hashlib.sha256(
            json.dumps(
                [(start_rva, end_rva)], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        old = row["oldResidualEntityKey"]
        new = row["expectedNewEntityKey"]
        new_question_id = row["expectedNewQuestionId"]
        new_contract_id = row["expectedNewContractId"]
        expected_old = _residual_key(specimen, f"0x{start:08x}", f"0x{end:08x}")
        expected_new = f"CODE:{specimen}:VA=0x{start:08x}:RANGES={range_set}"
        expected_question_id = _question_id(row["expectedNewQuestionType"], expected_new)
        expected_contract_id = _contract_id(expected_new)
        expected_supersession_id = "S-" + _sha256_text(old + "|" + new)[:16]
        if (
            start != range_start
            or end - start != body_bytes
            or start_rva < 0
            or old != expected_old
            or new != expected_new
            or row.get("expectedBodyRangeSetSha256") != range_set
            or new_question_id != expected_question_id
            or new_contract_id != expected_contract_id
            or row.get("expectedSupersessionId") != expected_supersession_id
        ):
            raise CampaignError(f"global-init515 lineage identity differs at {row['entry']}")
        for key, value in (
            ("old", old), ("new", new), ("question", new_question_id),
            ("contract", new_contract_id),
        ):
            if value in seen[key]:
                raise CampaignError(f"global-init515 lineage duplicates {key}: {value}")
            seen[key].add(value)

        old_residual = generation5_maps["residuals"].get(old)
        old_question = generation5_maps["questions"].get(row["oldQuestionId"])
        old_contract = generation5_maps["contracts"].get(row["oldContractId"])
        if (
            old_residual is None
            or old_residual.get("questionIds") != row["oldQuestionId"]
            or old_question is None
            or old_question.get("entityKey") != old
            or old_contract is None
            or old_contract.get("entityKey") != old
            or old_contract.get("questionIds") != row["oldQuestionId"]
        ):
            raise CampaignError(f"global-init515 generation-5 source lineage differs at {row['entry']}")
        if (
            old in maps["residuals"]
            or row["oldQuestionId"] in maps["questions"]
            or row["oldContractId"] in maps["contracts"]
            or old in existing_old
        ):
            raise CampaignError(f"global-init515 old residual lineage survived reseed at {row['entry']}")

        function = maps["functions"].get(new)
        question = maps["questions"].get(new_question_id)
        contract = maps["contracts"].get(new_contract_id)
        if (
            function is None
            or function.get("entryVa") != f"0x{start:08x}"
            or function.get("entryRva") != f"0x{start_rva:08x}"
            or function.get("currentName") != row["expectedNewName"]
            or function.get("nameClass") != row["expectedNewNameClass"]
            or function.get("bodyRangesRva") != f"0x{start_rva:x}-0x{end_rva:x}"
            or function.get("bodyRangeSetSha256") != range_set
            or function.get("bodyBytes") != str(body_bytes)
            or function.get("executionState") != "COVERED"
            or function.get("observedBytes") != str(body_bytes)
            or "MAINTAINER_GHIDRA_BOUNDARY_PROMOTED" in function.get("evidenceStates", "")
            or question is None
            or question.get("entityKey") != new
            or question.get("questionType") != row["expectedNewQuestionType"]
            or question.get("state") != "OPEN"
            or contract is None
            or contract.get("entityKey") != new
            or contract.get("entityKind") != "FUNCTION"
            or contract.get("questionIds") != new_question_id
            or old in contract.get("supersedesEntityKeys", "").split(";")
        ):
            raise CampaignError(f"global-init515 exact post-reseed successor differs at {row['entry']}")
        mappings.append(
            {
                "entry": row["entry"],
                "oldEntityKey": old,
                "newEntityKey": new,
                "newQuestionId": new_question_id,
                "newContractId": new_contract_id,
                "supersessionId": expected_supersession_id,
            }
        )

    old_region = f"DARK_REGION:{specimen}:0x00538780-0x0053885B"
    split_regions = {
        f"DARK_REGION:{specimen}:0x00538780-0x005387A0": ("0x00538780", "0x005387a0", "32"),
        f"DARK_REGION:{specimen}:0x005387B0-0x0053885B": ("0x005387b0", "0x0053885b", "171"),
    }
    question_entities = {row.get("entityKey"): row for row in fresh["questions"]}
    if old_region in maps["levers"] or old_region in question_entities:
        raise CampaignError("global-init515 post reseed retained the unsplit dark region")
    for region, (start_va, end_va, dark_bytes) in split_regions.items():
        lever = maps["levers"].get(region)
        question = question_entities.get(region)
        if (
            lever is None
            or lever.get("startVa") != start_va
            or lever.get("endVa") != end_va
            or lever.get("darkBytes") != dark_bytes
            or question is None
            or question.get("questionId") != _question_id("DARK_REGION_REACHABILITY", region)
            or question.get("questionType") != "DARK_REGION_REACHABILITY"
        ):
            raise CampaignError(f"global-init515 post reseed dark-region split differs: {region}")

    if len(mappings) != GLOBAL_INIT515_COUNT:
        raise CampaignError("global-init515 post-reseed mapping count differs")
    return {
        "mappings": mappings,
        "fresh": fresh,
        "counts": expected_counts,
        "sourceGeneration5Ready": {
            **coverage.file_stamp(FROZEN_V5_CAMPAIGN_CARRY_ROOT / "campaign.ready.json"),
            "path": str(FROZEN_V5_CAMPAIGN_CARRY_ROOT.resolve() / "campaign.ready.json"),
        },
        "darkRegionSplit": sorted(split_regions),
    }


def advance_ghidra_residual_promotion(
    campaign: Path,
    evidence_path: Path,
    lineage_root: Path,
    out: Path,
    *,
    _self_check: bool = True,
    _verified_parent_receipt: dict | None = None,
) -> dict:
    """Publish the exact residual-to-function lineage after a verified live POST."""
    base_receipt = (
        _verified_parent_receipt
        if _verified_parent_receipt is not None
        else verify(campaign)
    )
    if out.exists():
        raise CampaignError(f"refusing existing advanced-campaign destination: {out}")
    lineage = validate_global_init515_lineage(lineage_root)
    live = validate_global_init515_live_promotion(evidence_path)
    post_reseed = validate_global_init515_post_reseed(campaign, base_receipt, lineage)

    rows = post_reseed["fresh"]
    functions = rows["functions"]
    contracts = rows["contracts"]
    supersessions = rows["supersessions"]
    functions_by_entity = {row["entityKey"]: row for row in functions}
    contracts_by_entity = {row["entityKey"]: row for row in contracts}
    existing_old = {row.get("oldEntityKey") for row in supersessions}
    measured_at = live["measuredAtUtc"]
    evidence_stamp = live["evidenceStamp"]
    evidence_ref = f"{evidence_path.resolve()}#sha256={evidence_stamp['sha256']}"
    lineage_ready_path = lineage["root"] / "READY.json"
    lineage_ref = (
        f"{lineage_ready_path.resolve()}#sha256="
        f"{lineage['readyStamp']['sha256']}"
    )
    evidence_refs = f"{evidence_ref};{lineage_ref}"

    for mapping in post_reseed["mappings"]:
        old = mapping["oldEntityKey"]
        new = mapping["newEntityKey"]
        if old in existing_old:
            raise CampaignError(f"global-init515 residual was already superseded: {old}")
        function = functions_by_entity[new]
        contract = contracts_by_entity[new]
        function["evidenceStates"] = _append_state(
            function.get("evidenceStates", ""), "MAINTAINER_GHIDRA_BOUNDARY_PROMOTED"
        )
        function["lastMeasurementDate"] = measured_at[:10]
        contract["evidenceRefs"] = _append_state(
            _append_state(contract.get("evidenceRefs", ""), evidence_ref), lineage_ref
        )
        contract["supersedesEntityKeys"] = _append_state(
            contract.get("supersedesEntityKeys", ""), old
        )
        contract["lastMeasurementDate"] = measured_at[:10]
        supersessions.append(
            {
                "supersessionId": mapping["supersessionId"],
                "oldEntityKey": old,
                "newEntityKey": new,
                "kind": GHIDRA_RESIDUAL_ADVANCE_KIND,
                "verdict": "SURVIVED",
                "evidenceRefs": evidence_refs,
                "measuredAtUtc": measured_at,
            }
        )
        existing_old.add(old)

    output_rows = {
        "campaign-functions.tsv": (FUNCTION_COLUMNS, functions),
        "campaign-residuals.tsv": (RESIDUAL_COLUMNS, rows["residuals"]),
        "campaign-questions.tsv": (QUESTION_COLUMNS, rows["questions"]),
        "campaign-scenarios.tsv": (SCENARIO_COLUMNS, rows["scenarios"]),
        "campaign-levers.tsv": (LEVER_COLUMNS, rows["levers"]),
        "campaign-contracts.tsv": (CONTRACT_COLUMNS, contracts),
        "campaign-adjudications.tsv": (ADJUDICATION_COLUMNS, rows["adjudications"]),
        "campaign-supersessions.tsv": (SUPERSESSION_COLUMNS, supersessions),
    }
    base_ready = coverage.file_stamp(campaign / "campaign.ready.json")
    promotion_id = "RP-" + _sha256_text(
        "|".join(
            (
                base_ready["sha256"],
                evidence_stamp["sha256"],
                lineage["readyStamp"]["sha256"],
                GLOBAL_INIT515_TARGET_SET_SHA256,
            )
        )
    )[:16]
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        for name, (columns, output) in output_rows.items():
            _write_tsv(stage / name, columns, output)
        reducer = _publish_reducer(stage)
        counts = {
            "functions": len(functions),
            "residuals": len(rows["residuals"]),
            "questions": len(rows["questions"]),
            "scenarios": len(rows["scenarios"]),
            "levers": len(rows["levers"]),
            "contracts": len(contracts),
            "adjudications": len(rows["adjudications"]),
            "supersessions": len(supersessions),
        }
        expected_counts = {**post_reseed["counts"], "supersessions": 555}
        if counts != expected_counts:
            raise CampaignError(
                f"global-init515 advanced counts differ: {counts} != {expected_counts}"
            )
        receipt = {
            "schema": SCHEMA,
            "reducer": reducer,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "generation": _integer(base_receipt.get("generation"), -1) + 1,
            "parentCampaign": {
                "path": str(campaign.resolve()),
                "ready": {**base_ready, "path": "campaign.ready.json"},
            },
            "sourceSnapshot": base_receipt["sourceSnapshot"],
            "advance": {
                "kind": GHIDRA_RESIDUAL_ADVANCE_KIND,
                "schema": GHIDRA_RESIDUAL_ADVANCE_SCHEMA,
                "promotionId": promotion_id,
                "verdict": "SURVIVED",
                "count": GLOBAL_INIT515_COUNT,
                "targetSetSha256": GLOBAL_INIT515_TARGET_SET_SHA256,
                "evidence": {
                    **evidence_stamp,
                    "path": str(evidence_path.resolve()),
                },
                "lineage": {
                    "root": str(lineage["root"]),
                    "ready": lineage["readyStamp"],
                    "owner": lineage["ownerStamp"],
                    "rows": lineage["lineageStamp"],
                },
                "sourceGeneration5Ready": post_reseed["sourceGeneration5Ready"],
                "postReseedCounts": post_reseed["counts"],
                "darkRegionSplit": post_reseed["darkRegionSplit"],
                "semanticPromotionApplied": False,
            },
            "counts": counts,
            "questionTypes": dict(Counter(row["questionType"] for row in rows["questions"])),
            "policies": [
                "Only the exact 515 residual-to-function boundary lineage was superseded.",
                "The fresh post-live coverage reseed, not the lineage label, created the new function/question/contract identities.",
                "Boundary promotion assigns no semantic name, ABI, behavior, or rebuild-parity verdict.",
                "The verified disjoint POST backup is the durable source for post-live coverage accounting.",
                "The dark-region split caused by 0x005387a0 is preserved as a whole-campaign delta.",
            ],
            "outputs": {
                name: {**coverage.file_stamp(stage / name), "path": name}
                for name in OUTPUTS
            },
        }
        (stage / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        if _self_check:
            verify(stage)
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _atomic14_stamp(path: Path, expected_sha256: str, label: str) -> dict[str, object]:
    if not path.is_file():
        raise CampaignError(f"Atomic14 {label} is missing: {path}")
    actual = coverage.file_stamp(path)
    if actual["sha256"] != expected_sha256:
        raise CampaignError(
            f"Atomic14 {label} bytes differ: {actual['sha256']} != {expected_sha256}"
        )
    return {**actual, "path": str(path.resolve())}


def _atomic14_relative_stamp(
    root: Path, value: object, label: str
) -> tuple[Path, dict]:
    stamp = _runtime_mapping(value, label)
    relative = stamp.get("path")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise CampaignError(f"Atomic14 {label} path is not one relative artifact")
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise CampaignError(f"Atomic14 {label} escapes its evidence root") from exc
    _require_file_stamp(path, stamp, f"Atomic14 {label}")
    return path, stamp


def _validate_atomic14_partition_inputs(
    campaign: Path,
    base_receipt: dict,
    snapshot: Path,
    live_ready: Path,
    formal_ready: Path,
    targets_path: Path,
    padding_path: Path,
    parity_export_path: Path,
) -> dict[str, object]:
    parent_ready = _atomic14_stamp(
        campaign / "campaign.ready.json",
        ATOMIC14_PARENT_READY_SHA256,
        "parent campaign READY",
    )
    if (
        _integer(base_receipt.get("generation"), -1) != 7
        or base_receipt.get("counts")
        != {
            "functions": 8110,
            "residuals": 6103,
            "questions": 15223,
            "scenarios": 72,
            "levers": 914,
            "contracts": 14213,
            "adjudications": 2,
            "supersessions": 555,
        }
    ):
        raise CampaignError("Atomic14 parent campaign generation/counts differ")

    snapshot_ready = _atomic14_stamp(
        snapshot / "ledger.ready.json",
        ATOMIC14_POST_SNAPSHOT_READY_SHA256,
        "POST coverage snapshot READY",
    )
    live_stamp = _atomic14_stamp(
        live_ready, ATOMIC14_LIVE_READY_SHA256, "live promotion READY"
    )
    formal_stamp = _atomic14_stamp(
        formal_ready, ATOMIC14_FORMAL_READY_SHA256, "formal proof READY"
    )
    targets_stamp = _atomic14_stamp(
        targets_path, ATOMIC14_TARGETS_SHA256, "target manifest"
    )
    padding_stamp = _atomic14_stamp(
        padding_path, ATOMIC14_PADDING_SHA256, "padding manifest"
    )
    parity_export_stamp = _atomic14_stamp(
        parity_export_path,
        ATOMIC14_POST_PARITY_EXPORT_SHA256,
        "POST parity-export READY",
    )

    formal = _runtime_json(formal_ready, "Atomic14 formal proof READY")
    formal_inputs = _runtime_mapping(formal.get("inputs"), "Atomic14 formal inputs")
    if (
        formal.get("schema") != "bea.re.console-callback-atomic14-formal-proof.v2"
        or formal.get("verdict") != "PASS"
        or _runtime_mapping(
            formal_inputs.get("combinedManifest"), "Atomic14 formal combined manifest"
        ).get("sha256")
        != targets_stamp["sha256"]
        or _runtime_mapping(
            formal_inputs.get("paddingManifest"), "Atomic14 formal padding manifest"
        ).get("sha256")
        != padding_stamp["sha256"]
    ):
        raise CampaignError("Atomic14 formal proof boundary differs")

    live = _runtime_json(live_ready, "Atomic14 live promotion READY")
    if (
        live.get("schema") != "bea.re.console-callback-atomic14-live-promotion.v1"
        or live.get("status") != "READY"
        or live.get("state") != "POST"
        or live.get("campaignPublicationAuthorized") is not True
        or live.get("semanticPromotionApplied") is not False
    ):
        raise CampaignError("Atomic14 live promotion is not the admitted boundary-only POST")
    result_path, _result_stamp = _atomic14_relative_stamp(
        live_ready.parent, live.get("result"), "live promotion result"
    )
    result = _runtime_json(result_path, "Atomic14 live promotion result")
    post_backup = _runtime_mapping(result.get("postBackup"), "Atomic14 POST backup")
    backup_observation = _runtime_mapping(
        post_backup.get("backupObservation"), "Atomic14 POST backup observation"
    )
    backup_inventory = _runtime_mapping(
        backup_observation.get("inventory"), "Atomic14 POST backup inventory"
    )
    backup_functions = _runtime_mapping(
        backup_inventory.get("functions"), "Atomic14 POST backup functions"
    )
    backup_snapshot = _runtime_mapping(
        post_backup.get("backupSnapshot"), "Atomic14 POST backup snapshot"
    )
    measured_at = str(result.get("completedAtUtc", ""))
    if (
        result.get("schema") != live.get("schema")
        or result.get("state") != "POST"
        or result.get("campaignPublicationAuthorized") is not True
        or result.get("semanticPromotionApplied") is not False
        or backup_functions.get("sha256") != ATOMIC14_POST_FUNCTIONS_SHA256
        or backup_snapshot.get("fileSetSha256")
        != ATOMIC14_POST_PROJECT_FILESET_SHA256
        or backup_snapshot.get("fileCount") != 19
        or backup_snapshot.get("totalBytes") != 186387333
        or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T[^\s]+", measured_at)
    ):
        raise CampaignError("Atomic14 live promotion result/POST backup differs")

    parity_export = _runtime_json(
        parity_export_path, "Atomic14 POST parity-export READY"
    )
    project_before = _runtime_mapping(
        parity_export.get("projectBefore"), "Atomic14 parity projectBefore"
    )
    project_after = _runtime_mapping(
        parity_export.get("projectAfter"), "Atomic14 parity projectAfter"
    )
    if (
        parity_export.get("schema") != "bea.re.atomic14-live-post-parity-export.v1"
        or parity_export.get("status") != "READY"
        or project_before != project_after
        or project_before.get("fileSetSha256")
        != ATOMIC14_POST_PROJECT_FILESET_SHA256
        or project_before.get("fileCount") != 19
        or project_before.get("totalBytes") != 186387333
        or _runtime_mapping(
            parity_export.get("promotionReady"), "Atomic14 parity promotion READY"
        ).get("sha256")
        != live_stamp["sha256"]
        or _runtime_mapping(
            parity_export.get("formalReady"), "Atomic14 parity formal READY"
        ).get("sha256")
        != formal_stamp["sha256"]
    ):
        raise CampaignError("Atomic14 POST parity-export source boundary differs")
    parity_root = parity_export_path.parent
    run_path, _run_stamp = _atomic14_relative_stamp(
        parity_root, parity_export.get("run"), "POST parity-export process"
    )
    run = _runtime_json(run_path, "Atomic14 POST parity-export process")
    argv_text = " ".join(str(value) for value in run.get("argv", []))
    if (
        run.get("schema") != GLOBAL_INIT515_PROCESS_SCHEMA
        or run.get("status") != "COMPLETED"
        or run.get("exitCode") != 0
        or run.get("error")
        or run.get("readerError")
        or " -readOnly " not in f" {argv_text} "
        or " -noanalysis " not in f" {argv_text} "
        or str(Path(str(backup_observation.get("projectRoot", ""))).resolve())
        not in argv_text
        or "ExportParityLabGraph.java" not in argv_text
    ):
        raise CampaignError("Atomic14 POST parity-export process differs")
    parity_outputs = _runtime_mapping(
        parity_export.get("outputs"), "Atomic14 parity outputs"
    )
    parity_ready_spec = _runtime_mapping(
        parity_outputs.get("parityReady"), "Atomic14 parity graph READY"
    )
    parity_ready_path = _resolve_repo_or_absolute(
        parity_ready_spec.get("path"), "Atomic14 parity graph READY path"
    )
    _require_file_stamp(
        parity_ready_path, parity_ready_spec, "Atomic14 parity graph READY"
    )
    parity_ready = _runtime_json(parity_ready_path, "Atomic14 parity graph READY")
    if (
        parity_ready.get("schemaVersion") != "bea-ghidra-parity-graph-receipt.v2"
        or _runtime_mapping(
            parity_ready.get("bodyRanges"), "Atomic14 parity body ranges"
        ).get("functionCount")
        != 8124
        or _runtime_mapping(
            parity_ready.get("bodyRanges"), "Atomic14 parity body ranges"
        ).get("rangeCount")
        != 8241
    ):
        raise CampaignError("Atomic14 parity graph population differs")

    data = load_snapshot(snapshot)
    summary = data["summary"]
    denominators = _runtime_mapping(
        summary.get("denominators"), "Atomic14 snapshot denominators"
    )
    byte_summary = _runtime_mapping(summary.get("bytes"), "Atomic14 snapshot bytes")
    inputs = _runtime_mapping(summary.get("inputs"), "Atomic14 snapshot inputs")
    name_table = _runtime_mapping(inputs.get("nameTable"), "Atomic14 snapshot name table")
    parity_graph = _runtime_mapping(inputs.get("parityGraph"), "Atomic14 snapshot parity graph")
    parity_receipt = _runtime_mapping(
        parity_graph.get("receipt"), "Atomic14 snapshot parity receipt"
    )
    if (
        denominators.get("functionPopulation") != 8124
        or denominators.get("exactBodyByteTotal") != 1767100
        or denominators.get("exactBodyRangeCount") != 8241
        or byte_summary.get("unmappedByAnyFunction") != 162017
        or name_table.get("sha256") != ATOMIC14_POST_FUNCTIONS_SHA256
        or parity_receipt.get("sha256") != parity_ready_spec.get("sha256")
        or summary.get("inputs", {}).get("specimen", {}).get("sha256", "").lower()
        != LEGACY_CAMPAIGN_CARRY_SPECIMEN_SHA256
    ):
        raise CampaignError("Atomic14 POST snapshot accounting differs")

    target_rows = _read_tsv(targets_path)
    padding_rows = _read_tsv(padding_path)
    if len(target_rows) != ATOMIC14_FUNCTION_COUNT or len(padding_rows) != ATOMIC14_PADDING_COUNT:
        raise CampaignError("Atomic14 target/padding row counts differ")
    specimen_path = Path(str(inputs["specimen"]["path"]))
    if not specimen_path.is_absolute():
        specimen_path = REPO_ROOT / specimen_path
    specimen = coverage.Specimen(specimen_path)
    function_by_va = {row["va"].lower(): row for row in data["functions"]}
    residual_by_range = {
        (int(row["startVa"], 16), int(row["endVa"], 16)): row
        for row in data["residuals"]
    }
    intervals: list[tuple[int, int, str]] = []
    for row in target_rows:
        match = re.fullmatch(
            r"(0x[0-9a-fA-F]+)-(0x[0-9a-fA-F]+)", row.get("expectedRanges", "")
        )
        if match is None:
            raise CampaignError("Atomic14 target contains a non-canonical range")
        start, end = int(match.group(1), 16), int(match.group(2), 16)
        entry = row.get("entry", "").lower()
        function = function_by_va.get(entry)
        expected_rva = (
            f"0x{start - specimen.image_base:x}-0x{end - specimen.image_base:x}"
        )
        body = specimen.bytes_at_rva(start - specimen.image_base, end - start)
        if (
            start != int(entry, 16)
            or function is None
            or _integer(row.get("expectedBodyBytes"), -1) != end - start
            or function.get("bodyRangesRva") != expected_rva
            or _integer(function.get("bodyBytes"), -1) != end - start
            or hashlib.sha256(body).hexdigest()
            != row.get("expectedBodyBytesSha256")
            or row.get("expectedIsThunk") != "false"
            or row.get("expectedThunkTarget")
            or row.get("residualEntityKeys") != ATOMIC14_OLD_RESIDUAL
            or row.get("questionIds") != ATOMIC14_OLD_QUESTION
            or row.get("contractIds") != ATOMIC14_OLD_CONTRACT
            or row.get("promotionLane") != "CONSOLE_CALLBACK_COHORT"
            or not re.fullmatch(r"[0-9a-f]{64}", row.get("expectedRangeDigest", ""))
        ):
            raise CampaignError(f"Atomic14 target/snapshot body differs at {entry}")
        intervals.append((start, end, "FUNCTION"))

    for row in padding_rows:
        start, end = int(row.get("start", ""), 16), int(row.get("endExclusive", ""), 16)
        body = specimen.bytes_at_rva(start - specimen.image_base, end - start)
        residual = residual_by_range.get((start, end))
        if (
            end <= start
            or _integer(row.get("bytes"), -1) != end - start
            or row.get("allNop") != "true"
            or body != b"\x90" * (end - start)
            or hashlib.sha256(body).hexdigest() != row.get("bytesSha256")
            or residual is None
        ):
            raise CampaignError(
                f"Atomic14 padding/snapshot bytes differ at 0x{start:08x}"
            )
        intervals.append((start, end, "PADDING"))

    ordered = sorted(intervals)
    if (
        ordered[0][0] != ATOMIC14_START_VA
        or ordered[-1][1] != ATOMIC14_END_VA
        or any(left[1] != right[0] for left, right in zip(ordered, ordered[1:]))
        or sum(end - start for start, end, kind in ordered if kind == "FUNCTION")
        != ATOMIC14_FUNCTION_BYTES
        or sum(end - start for start, end, kind in ordered if kind == "PADDING")
        != ATOMIC14_PADDING_BYTES
    ):
        raise CampaignError("Atomic14 target/padding manifests do not exactly partition the parent")

    parent_rows = _campaign_rows_from_root(campaign)
    old_residuals = [
        row for row in parent_rows["residuals"] if row.get("entityKey") == ATOMIC14_OLD_RESIDUAL
    ]
    old_questions = [
        row for row in parent_rows["questions"] if row.get("questionId") == ATOMIC14_OLD_QUESTION
    ]
    old_contracts = [
        row for row in parent_rows["contracts"] if row.get("contractId") == ATOMIC14_OLD_CONTRACT
    ]
    if (
        len(old_residuals) != 1
        or len(old_questions) != 1
        or len(old_contracts) != 1
        or old_residuals[0].get("bytes") != "1540"
        or old_questions[0].get("state") != "OPEN"
        or old_questions[0].get("entityKey") != ATOMIC14_OLD_RESIDUAL
        or old_contracts[0].get("contractState") != "OPEN_CLASSIFICATION"
        or old_contracts[0].get("entityKey") != ATOMIC14_OLD_RESIDUAL
    ):
        raise CampaignError("Atomic14 retired parent residual/question/contract differs")

    return {
        "parentReady": parent_ready,
        "snapshotReady": snapshot_ready,
        "liveStamp": live_stamp,
        "formalStamp": formal_stamp,
        "targetsStamp": targets_stamp,
        "paddingStamp": padding_stamp,
        "parityExportStamp": parity_export_stamp,
        "parityReadyStamp": parity_ready_spec,
        "data": data,
        "targetRows": target_rows,
        "paddingRows": padding_rows,
        "measuredAtUtc": measured_at,
        "retiredResidual": old_residuals[0],
        "retiredQuestion": old_questions[0],
        "retiredContract": old_contracts[0],
    }


def advance_ghidra_residual_partition(
    campaign: Path,
    snapshot: Path,
    live_ready: Path,
    formal_ready: Path,
    targets_path: Path,
    padding_path: Path,
    parity_export_path: Path,
    out: Path,
    *,
    _self_check: bool = True,
    _verified_parent_receipt: dict | None = None,
) -> dict:
    """Replace one proven residual with its exact function/padding partition."""
    base_receipt = (
        _verified_parent_receipt
        if _verified_parent_receipt is not None
        else _verify_atomic14_parent_campaign(campaign)
    )
    if out.exists():
        raise CampaignError(f"refusing existing exact-partition destination: {out}")
    validated = _validate_atomic14_partition_inputs(
        campaign,
        base_receipt,
        snapshot,
        live_ready,
        formal_ready,
        targets_path,
        padding_path,
        parity_export_path,
    )
    data = validated["data"]
    rows = build_campaign_rows(data)
    carry_report = _merge_reseed_carry(rows, campaign)
    pre_partition_counts = {name: len(value) for name, value in rows.items()}
    if pre_partition_counts != {
        "functions": 8124,
        "residuals": 6117,
        "questions": 15252,
        "scenarios": 72,
        "levers": 915,
        "contracts": 14241,
        "adjudications": 2,
        "supersessions": 555,
    }:
        raise CampaignError(
            f"Atomic14 fresh carried frontier counts differ: {pre_partition_counts}"
        )
    if any(
        _integer(carry_report.get(field), -1) != 0
        for field in (
            "staleQuestions",
            "staleFunctions",
            "staleResiduals",
            "staleContracts",
            "staleAdjudications",
            "staleSupersessions",
        )
    ):
        raise CampaignError(f"Atomic14 reseed carry reports stale lineage: {carry_report}")

    functions_by_va = {row["entryVa"].lower(): row for row in rows["functions"]}
    contracts_by_entity = {row["entityKey"]: row for row in rows["contracts"]}
    questions_by_entity: dict[str, list[dict]] = {}
    for question in rows["questions"]:
        questions_by_entity.setdefault(question["entityKey"], []).append(question)
    residuals_by_range = {
        (int(row["startVa"], 16), int(row["endVa"], 16)): row
        for row in rows["residuals"]
    }
    measured_at = str(validated["measuredAtUtc"])
    measured_date = measured_at[:10]
    next_generation = _integer(base_receipt.get("generation"), -1) + 1

    evidence_stamps = [
        validated["liveStamp"],
        validated["formalStamp"],
        validated["targetsStamp"],
        validated["paddingStamp"],
        validated["parityExportStamp"],
        validated["snapshotReady"],
    ]
    evidence_refs = ";".join(
        f"{stamp['path']}#sha256={stamp['sha256']}" for stamp in evidence_stamps
    )

    function_children: list[tuple[int, int, str, dict, dict, dict]] = []
    for target in validated["targetRows"]:
        match = re.fullmatch(
            r"(0x[0-9a-fA-F]+)-(0x[0-9a-fA-F]+)", target["expectedRanges"]
        )
        if match is None:
            raise CampaignError("Atomic14 target range changed after validation")
        start, end = int(match.group(1), 16), int(match.group(2), 16)
        function = functions_by_va.get(target["entry"].lower())
        if function is None:
            raise CampaignError(f"Atomic14 fresh function is absent: {target['entry']}")
        contract = contracts_by_entity.get(function["entityKey"])
        function_questions = [
            row
            for row in questions_by_entity.get(function["entityKey"], [])
            if row.get("questionType") == "DARK_FUNCTION_CONTRACT"
        ]
        if len(function_questions) != 1 or contract is None:
            raise CampaignError(
                f"Atomic14 fresh function contract/question shape differs: {target['entry']}"
            )
        question = function_questions[0]
        function["evidenceStates"] = _append_state(
            function.get("evidenceStates", ""), "MAINTAINER_GHIDRA_BOUNDARY_PROMOTED"
        )
        function["lastMeasurementDate"] = measured_date
        question["generation"] = next_generation
        question["parentQuestionId"] = ATOMIC14_OLD_QUESTION
        question["lastOutcome"] = "PENDING"
        question["lastMeasurementDate"] = measured_at
        contract["evidenceRefs"] = _union_semicolon(
            contract.get("evidenceRefs", ""), evidence_refs
        )
        contract["supersedesEntityKeys"] = _append_state(
            contract.get("supersedesEntityKeys", ""), ATOMIC14_OLD_RESIDUAL
        )
        contract["lastMeasurementDate"] = measured_date
        function_children.append(
            (start, end, function["entityKey"], function, contract, question)
        )

    padding_children: list[tuple[int, int, str, dict, dict]] = []
    padding_question_ids: set[str] = set()
    padding_falsifier = (
        "Any non-NOP byte, instruction/function membership, incoming flow/reference, "
        "or overlap contradicts terminal padding classification."
    )
    for padding in validated["paddingRows"]:
        start = int(padding["start"], 16)
        end = int(padding["endExclusive"], 16)
        residual = residuals_by_range.get((start, end))
        if residual is None:
            raise CampaignError(f"Atomic14 fresh padding residual is absent: 0x{start:08x}")
        contract = contracts_by_entity.get(residual["entityKey"])
        residual_questions = questions_by_entity.get(residual["entityKey"], [])
        if contract is None or len(residual_questions) != 1:
            raise CampaignError(
                f"Atomic14 fresh padding contract/question shape differs: 0x{start:08x}"
            )
        padding_question_ids.add(residual_questions[0]["questionId"])
        residual.update(
            {
                "classification": "PADDING",
                "classificationVerdict": "FORMAL_STATIC_PROOF_SURVIVED",
                "terminalState": "TERMINAL_PADDING",
                "campaignState": "TERMINAL_PADDING",
                "lever": "NONE",
                "requiresElevation": False,
                "cheapestFalsifier": padding_falsifier,
                "questionIds": "",
                "lastMeasurementDate": measured_date,
            }
        )
        contract.update(
            {
                "contractState": "TERMINAL_PADDING",
                "authorVerdict": "STATIC_FORMAL_PROOF",
                "runtimeVerdict": "UNSCORED",
                "refuterVerdict": "SURVIVED",
                "questionIds": "",
                "evidenceRefs": _union_semicolon(
                    contract.get("evidenceRefs", ""), evidence_refs
                ),
                "cheapestFalsifier": padding_falsifier,
                "remainingUncertainty": (
                    "No behavior contract is claimed; this range is structurally proven alignment padding."
                ),
                "supersedesEntityKeys": _append_state(
                    contract.get("supersedesEntityKeys", ""), ATOMIC14_OLD_RESIDUAL
                ),
                "lastMeasurementDate": measured_date,
            }
        )
        padding_children.append((start, end, residual["entityKey"], residual, contract))

    if len(padding_question_ids) != ATOMIC14_PADDING_COUNT:
        raise CampaignError("Atomic14 padding questions are not one-per-range")
    rows["questions"] = [
        row for row in rows["questions"] if row["questionId"] not in padding_question_ids
    ]

    specimen_sha = data["summary"]["inputs"]["specimen"]["sha256"]
    region_key = _region_key(
        specimen_sha,
        f"0x{function_children[0][0]:08x}",
        f"0x{function_children[-1][1]:08x}",
    )
    region_questions = [
        row
        for row in rows["questions"]
        if row.get("entityKey") == region_key
        and row.get("questionType") == "DARK_REGION_REACHABILITY"
    ]
    if len(region_questions) != 1:
        raise CampaignError("Atomic14 dark-region successor question differs")
    region_question = region_questions[0]
    region_question["generation"] = next_generation
    region_question["parentQuestionId"] = ATOMIC14_OLD_QUESTION
    region_question["lastOutcome"] = "PENDING"
    region_question["lastMeasurementDate"] = measured_at

    old_question = {
        field: validated["retiredQuestion"].get(field, "") for field in QUESTION_COLUMNS
    }
    old_question["state"] = "CLOSED_SURVIVED"
    old_question["lastOutcome"] = "SURVIVED"
    old_question["attemptCount"] = _integer(old_question.get("attemptCount"), 0) + 1
    old_question["lastMeasurementDate"] = measured_at
    if any(row.get("questionId") == ATOMIC14_OLD_QUESTION for row in rows["questions"]):
        raise CampaignError("Atomic14 retired question unexpectedly survived the fresh reseed")
    rows["questions"].append(old_question)

    successor_questions = [row[5]["questionId"] for row in function_children]
    successor_questions.append(region_question["questionId"])
    children = sorted(
        [
            (start, end, entity, "FUNCTION")
            for start, end, entity, _function, _contract, _question in function_children
        ]
        + [
            (start, end, entity, "PADDING")
            for start, end, entity, _residual, _contract in padding_children
        ]
    )
    successor_entities = [row[2] for row in children]
    adjudication_id = "A-" + _sha256_text(
        "|".join(
            (
                validated["parentReady"]["sha256"],
                validated["snapshotReady"]["sha256"],
                validated["liveStamp"]["sha256"],
                validated["formalStamp"]["sha256"],
                validated["targetsStamp"]["sha256"],
                validated["paddingStamp"]["sha256"],
                validated["parityExportStamp"]["sha256"],
                ATOMIC14_OLD_CONTRACT,
                ATOMIC14_OLD_QUESTION,
                "SURVIVED",
            )
        )
    )[:16]
    rows["adjudications"].append(
        {
            "adjudicationId": adjudication_id,
            "baseContractId": ATOMIC14_OLD_CONTRACT,
            "entityKey": ATOMIC14_OLD_RESIDUAL,
            "overlaySchema": GHIDRA_PARTITION_ADVANCE_SCHEMA,
            "overlayReadySha256": validated["formalStamp"]["sha256"],
            "questionIdsAddressed": ATOMIC14_OLD_QUESTION,
            "refuterVerdict": "SURVIVED",
            "refuterEvidenceSha256": ";".join(
                stamp["sha256"] for stamp in evidence_stamps
            ),
            "semanticPromotionApplied": False,
            "terminalState": "TERMINAL_EXACT_PARTITION",
            "successorQuestionIds": ";".join(successor_questions),
            "remainingUncertainty": (
                "Fourteen function contracts and their shared reachability remain opaque; "
                "only boundaries and padding are terminally classified."
            ),
            "measuredAtUtc": measured_at,
        }
    )

    existing_supersession_ids = {
        row["supersessionId"] for row in rows["supersessions"]
    }
    for _start, _end, entity, _kind in children:
        supersession_id = "S-" + _sha256_text(
            ATOMIC14_OLD_RESIDUAL + "|" + entity
        )[:16]
        if supersession_id in existing_supersession_ids:
            raise CampaignError(f"Atomic14 successor was already superseded: {entity}")
        rows["supersessions"].append(
            {
                "supersessionId": supersession_id,
                "oldEntityKey": ATOMIC14_OLD_RESIDUAL,
                "newEntityKey": entity,
                "kind": GHIDRA_PARTITION_ADVANCE_KIND,
                "verdict": "SURVIVED",
                "evidenceRefs": evidence_refs,
                "measuredAtUtc": measured_at,
            }
        )
        existing_supersession_ids.add(supersession_id)

    output_rows = {
        "campaign-functions.tsv": (FUNCTION_COLUMNS, rows["functions"]),
        "campaign-residuals.tsv": (RESIDUAL_COLUMNS, rows["residuals"]),
        "campaign-questions.tsv": (QUESTION_COLUMNS, rows["questions"]),
        "campaign-scenarios.tsv": (SCENARIO_COLUMNS, rows["scenarios"]),
        "campaign-levers.tsv": (LEVER_COLUMNS, rows["levers"]),
        "campaign-contracts.tsv": (CONTRACT_COLUMNS, rows["contracts"]),
        "campaign-adjudications.tsv": (ADJUDICATION_COLUMNS, rows["adjudications"]),
        "campaign-supersessions.tsv": (SUPERSESSION_COLUMNS, rows["supersessions"]),
    }
    counts = {name: len(rows[name]) for name in rows}
    expected_counts = {
        "functions": 8124,
        "residuals": 6117,
        "questions": 15238,
        "scenarios": 72,
        "levers": 915,
        "contracts": 14241,
        "adjudications": 3,
        "supersessions": 584,
    }
    if counts != expected_counts:
        raise CampaignError(f"Atomic14 advanced counts differ: {counts} != {expected_counts}")
    if any(
        row.get("questionId") in padding_question_ids for row in rows["questions"]
    ):
        raise CampaignError("Atomic14 terminal padding retained an open question")

    snapshot_ready_for_receipt = {
        **validated["snapshotReady"],
        "path": "ledger.ready.json",
    }
    promotion_id = "XP-" + _sha256_text(
        validated["parentReady"]["sha256"]
        + "|"
        + validated["snapshotReady"]["sha256"]
        + "|"
        + adjudication_id
    )[:16]
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        for name, (columns, output) in output_rows.items():
            _write_tsv(stage / name, columns, output)
        reducer = _publish_reducer(stage)
        receipt = {
            "schema": SCHEMA,
            "reducer": reducer,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "generation": next_generation,
            "parentCampaign": {
                "path": str(campaign.resolve()),
                "ready": {
                    **validated["parentReady"],
                    "path": "campaign.ready.json",
                },
            },
            "sourceSnapshot": {
                "path": str(snapshot.resolve()),
                "schema": data["summary"]["schema"],
                "coverageSetSha256": data["summary"]["denominators"][
                    "coverageSetSha256"
                ],
                "specimen": data["summary"]["inputs"]["specimen"],
                "parityGraph": data["summary"]["inputs"]["parityGraph"],
                "files": data["snapshotFiles"],
            },
            "advance": {
                "kind": GHIDRA_PARTITION_ADVANCE_KIND,
                "schema": GHIDRA_PARTITION_ADVANCE_SCHEMA,
                "promotionId": promotion_id,
                "verdict": "SURVIVED",
                "adjudicationId": adjudication_id,
                "semanticPromotionApplied": False,
                "snapshot": {
                    "root": str(snapshot.resolve()),
                    "ready": snapshot_ready_for_receipt,
                },
                "liveReady": validated["liveStamp"],
                "formalReady": validated["formalStamp"],
                "targets": validated["targetsStamp"],
                "padding": validated["paddingStamp"],
                "parityExport": validated["parityExportStamp"],
                "retiredSubject": {
                    "residual": validated["retiredResidual"],
                    "question": validated["retiredQuestion"],
                    "contract": validated["retiredContract"],
                },
                "partition": {
                    "parentStartVa": f"0x{ATOMIC14_START_VA:08x}",
                    "parentEndVa": f"0x{ATOMIC14_END_VA:08x}",
                    "parentBytes": ATOMIC14_END_VA - ATOMIC14_START_VA,
                    "functionCount": ATOMIC14_FUNCTION_COUNT,
                    "functionBytes": ATOMIC14_FUNCTION_BYTES,
                    "paddingCount": ATOMIC14_PADDING_COUNT,
                    "paddingBytes": ATOMIC14_PADDING_BYTES,
                    "children": [
                        {
                            "startVa": f"0x{start:08x}",
                            "endVa": f"0x{end:08x}",
                            "entityKey": entity,
                            "kind": kind,
                        }
                        for start, end, entity, kind in children
                    ],
                    "successorEntityKeys": successor_entities,
                    "successorQuestionIds": successor_questions,
                    "darkRegionEntityKey": region_key,
                },
                "carried": carry_report,
            },
            "counts": counts,
            "questionTypes": dict(
                Counter(row["questionType"] for row in rows["questions"])
            ),
            "policies": [
                "The old 1,540-byte residual is retired only through an exact disjoint 14-function/15-padding partition.",
                "The original classification question remains closed in history; terminal padding publishes no replacement question.",
                "Boundary promotion assigns no semantic name, ABI, behavior, contract grade, or rebuild readiness.",
                "Every successor contract mirrors the retired residual through one hash-bound supersession row.",
                "The pristine specimen supplies byte truth; the verified POST backup supplies maintainer-project structure.",
            ],
            "outputs": {
                name: {**coverage.file_stamp(stage / name), "path": name}
                for name in OUTPUTS
            },
        }
        (stage / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        if _self_check:
            verify(stage)
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _successor_question(
    spec: dict,
    *,
    entity_key: str,
    parents: list[dict[str, str]],
    history: list[dict[str, str]],
    generation: int,
    measured_at: str,
) -> dict:
    required = ("questionType", "question", "recommendedInstrument", "cheapestFalsifier")
    if any(not isinstance(spec.get(key), str) or not spec[key].strip() for key in required):
        raise CampaignError("runtime adjudication successor question lacks required text")
    if not isinstance(spec.get("requiresElevation", False), bool):
        raise CampaignError("runtime adjudication successor requiresElevation must be boolean")
    try:
        priority = int(spec.get("priority", 3))
        score = float(spec.get("score", 0.0))
    except (TypeError, ValueError) as exc:
        raise CampaignError("runtime adjudication successor has invalid priority/score") from exc
    if not 0 <= priority <= 9:
        raise CampaignError("runtime adjudication successor priority lies outside 0..9")
    def normalized(value: object) -> str:
        return " ".join(str(value).split()).casefold()

    old_shapes = {
        (
            normalized(row["question"]),
            normalized(row["recommendedInstrument"]),
            normalized(row["cheapestFalsifier"]),
        )
        for row in history
    }
    new_shape = (
        spec["question"].strip(),
        spec["recommendedInstrument"].strip(),
        spec["cheapestFalsifier"].strip(),
    )
    if tuple(normalized(value) for value in new_shape) in old_shapes:
        raise CampaignError(
            "runtime adjudication would repeat a historical question/instrument/falsifier"
        )
    parent_ids = sorted(row["questionId"] for row in parents)
    seed = "|".join(
        [
            "ADVANCE",
            *parent_ids,
            str(generation),
            spec["questionType"].strip(),
            *new_shape,
        ]
    )
    return {
        "questionId": f"Q-{_sha256_text(seed)[:16]}",
        "questionType": spec["questionType"].strip(),
        "entityKey": entity_key,
        "priority": priority,
        "score": round(score, 3),
        "state": "OPEN",
        "requiresElevation": spec.get("requiresElevation", False),
        "recommendedInstrument": spec["recommendedInstrument"].strip(),
        "question": spec["question"].strip(),
        "cheapestFalsifier": spec["cheapestFalsifier"].strip(),
        "source": str(spec.get("source", "runtime-adjudication")).strip(),
        "currentOwner": str(spec.get("currentOwner", "recursive-re-campaign")).strip(),
        "generation": generation,
        "attemptCount": max(_integer(row.get("attemptCount"), 0) for row in parents) + 1,
        "parentQuestionId": ";".join(parent_ids),
        "lastOutcome": "PENDING",
        "lastMeasurementDate": measured_at,
    }


def _ttd_call_context_exact_stamp(
    path: Path, expected_sha256: str, label: str
) -> dict[str, object]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise CampaignError(f"TTD call-context {label} is absent")
    actual = coverage.file_stamp(resolved)
    if actual["sha256"] != expected_sha256.lower():
        raise CampaignError(f"TTD call-context {label} identity differs")
    return {
        "path": str(resolved),
        "bytes": actual["bytes"],
        "sha256": actual["sha256"],
    }


def _ttd_call_context_hex(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise CampaignError(f"TTD call-context {label} is not hexadecimal text")
    try:
        return f"0x{int(value, 16):X}"
    except ValueError as exc:
        raise CampaignError(
            f"TTD call-context {label} is not hexadecimal text"
        ) from exc


def _ttd_call_context_stack32(event: dict, count: int) -> tuple[int, ...]:
    stack = event.get("stack")
    if not isinstance(stack, dict) or stack.get("query_valid") is not True:
        raise CampaignError("TTD call-context event has no valid stack capture")
    try:
        raw = bytes.fromhex(str(stack.get("hex", "")))
    except ValueError as exc:
        raise CampaignError("TTD call-context stack bytes are malformed") from exc
    if len(raw) < 4 * (count + 1):
        raise CampaignError("TTD call-context stack capture is too short")
    return struct.unpack_from(f"<{count}I", raw, 4)


def _validate_ttd_call_context_jsonl(path: Path) -> dict[str, object]:
    """Independently parse the exact bounded schema-v3 observation."""

    try:
        raw_lines = path.read_bytes().splitlines(keepends=True)
        rows = [json.loads(line) for line in raw_lines]
    except (OSError, json.JSONDecodeError) as exc:
        raise CampaignError(f"cannot parse TTD call-context JSONL {path}: {exc}") from exc
    if len(rows) != 23 or any(not isinstance(row, dict) for row in rows):
        raise CampaignError("TTD call-context JSONL row population differs")
    expected_kinds = Counter(
        {
            "metadata": 1,
            "target": 4,
            "event": 12,
            "invocation": 4,
            "gap-summary": 1,
            "summary": 1,
        }
    )
    if Counter(row.get("kind") for row in rows) != expected_kinds:
        raise CampaignError("TTD call-context JSONL kind census differs")
    metadata = rows[0]
    expected_metadata = {
        "kind": "metadata",
        "schema": "bea.ttd.call-context.v3",
        "processor_architecture": "x86",
        "raw_value_policy": "untyped-registers-and-bytes",
        "entry_phase": "execute-watchpoint-before-entry-instruction",
        "call_phase": "callback-position-at-call-instruction",
        "return_phase": "callback-position-at-ret-instruction",
        "association_policy": "global-epoch-breaks-on-every-non-no-gap-and-continuity-callback",
        "window_semantics": "inclusive-position-bounds",
        "requested_from": "0x14A000:0x0",
        "requested_to": "0x14C000:0x0",
    }
    if any(metadata.get(key) != value for key, value in expected_metadata.items()):
        raise CampaignError("TTD call-context metadata policy differs")

    targets = sorted(
        (row for row in rows if row.get("kind") == "target"),
        key=lambda row: _integer(row.get("target_index"), -1),
    )
    expected_targets = (
        (0, "0x7350", "0x407350", "0x7350", "0x74CC", "1", "1", "1", "1", "0", "1"),
        (1, "0xA890", "0x40A890", "0xA890", "0xAC25", "1", "1", "1", "0", "1", "0"),
        (2, "0xBFD0", "0x40BFD0", "0xBFD0", "0xC17C", "0", "0", "0", "0", "0", "0"),
        (3, "0xD8AE0", "0x4D8AE0", "0xD8AE0", "0xD8DBE", "2", "2", "2", "0", "2", "0"),
    )
    for row, expected in zip(targets, expected_targets, strict=True):
        (
            index,
            entry_rva,
            entry_va,
            range_start,
            range_end,
            entries,
            calls,
            returns,
            validated_returns,
            orphan_returns,
            gap_free,
        ) = expected
        if (
            row.get("target_index") != index
            or _ttd_call_context_hex(row.get("entry_rva"), f"target {index} RVA")
            != entry_rva
            or _ttd_call_context_hex(row.get("entry_va"), f"target {index} VA")
            != entry_va
            or row.get("ranges")
            != [{"rva_start": range_start, "rva_end_exclusive": range_end}]
        ):
            raise CampaignError(f"TTD call-context target {index} identity differs")
        for prefix, count in (
            ("expected_entry", entries),
            ("expected_call", calls),
            ("expected_return", returns),
            ("observed_entry", entries),
            ("observed_call", calls),
            ("observed_return", returns),
        ):
            if row.get(f"{prefix}_count") != count:
                raise CampaignError(
                    f"TTD call-context target {index} {prefix} count differs"
                )
        if (
            row.get("observed_call_entry_pair_count") != calls
            or row.get("observed_validated_return_count") != validated_returns
            or row.get("observed_orphan_return_count") != orphan_returns
            or row.get("observed_gap_free_envelope_count") != gap_free
            or row.get("expectations_passed") is not True
        ):
            raise CampaignError(f"TTD call-context target {index} grade differs")

    events = sorted(
        (row for row in rows if row.get("kind") == "event"),
        key=lambda row: _integer(row.get("event_index"), -1),
    )
    expected_events = (
        (0, "call", 3, "0x14B569:0x66D", "0x4268CB", "0x4D8AE0", "0x4268D1"),
        (1, "entry", 3, "0x14B569:0x66E", "0x4D8AE0", "0x4D8AE0", None),
        (2, "call", 1, "0x14B569:0x6F2", "0x4D8CEF", "0x40A890", "0x4D8CF5"),
        (3, "entry", 1, "0x14B569:0x6F3", "0x40A890", "0x40A890", None),
        (4, "return", 1, "0x14B571:0x77", "0x40AC22", "0x4D8CF5", None),
        (5, "return", 3, "0x14B654:0x25D", "0x4D8D97", "0x4268D1", None),
        (6, "call", 0, "0x14B654:0x264", "0x4268DE", "0x407350", "0x4268E4"),
        (7, "entry", 0, "0x14B654:0x265", "0x407350", "0x407350", None),
        (8, "return", 0, "0x14B654:0x29B", "0x4074C9", "0x4268E4", None),
        (9, "call", 3, "0x14B6BA:0x292D", "0x4268CB", "0x4D8AE0", "0x4268D1"),
        (10, "entry", 3, "0x14B6BA:0x292E", "0x4D8AE0", "0x4D8AE0", None),
        (11, "return", 3, "0x14B775:0x25D", "0x4D8D97", "0x4268D1", None),
    )
    for event, expected in zip(events, expected_events, strict=True):
        index, kind, target_index, position, pc, target, fallthrough = expected
        if (
            event.get("event_index") != index
            or event.get("event_type") != kind
            or event.get("target_index") != target_index
            or event.get("position") != position
            or _ttd_call_context_hex(event.get("pc"), f"event {index} PC") != pc
            or _ttd_call_context_hex(
                event.get("instruction_target"), f"event {index} target"
            )
            != target
            or event.get("unique_thread_id") != "5"
            or event.get("control_registers_valid") is not True
            or event.get("integer_registers_valid") is not True
            or event.get("register_views_agree") is not True
        ):
            raise CampaignError(f"TTD call-context event {index} differs")
        if fallthrough is not None and _ttd_call_context_hex(
            event.get("fallthrough"), f"event {index} fallthrough"
        ) != fallthrough:
            raise CampaignError(f"TTD call-context event {index} fallthrough differs")

    expected_returns = {
        4: ("0x1", "0x1", "0x100000001"),
        5: ("0x3865B38", "0x2B", "0x2B03865B38"),
        8: ("0x7A30830", "0x5D89C4", "0x5D89C407A30830"),
        11: ("0x3865AA0", "0x33", "0x3303865AA0"),
    }
    for index, (eax, edx, combined) in expected_returns.items():
        registers = events[index].get("registers")
        if not isinstance(registers, dict) or (
            _ttd_call_context_hex(registers.get("eax"), f"event {index} EAX")
            != eax
            or _ttd_call_context_hex(registers.get("edx"), f"event {index} EDX")
            != edx
            or _ttd_call_context_hex(
                events[index].get("raw_edx_eax"), f"event {index} EDX:EAX"
            )
            != combined
        ):
            raise CampaignError(f"TTD call-context event {index} raw carrier differs")

    carrier_expectations = (
        (0, "0x7A30830", (0x079B9750, 0x001AF2CC)),
        (2, "0x79B9750", (0x3D4CCCCD, 0x07A30830, 1, 0xFFFFFFFF)),
        (6, "0x79B9750", (0x07A30830, 0x001AF2CC)),
        (9, "0x7994020", (0x079C2C60, 0x001AF2CC)),
    )
    for index, ecx, stack_words in carrier_expectations:
        registers = events[index].get("registers")
        if (
            not isinstance(registers, dict)
            or _ttd_call_context_hex(registers.get("ecx"), f"event {index} ECX")
            != ecx
            or _ttd_call_context_stack32(events[index], len(stack_words))
            != stack_words
        ):
            raise CampaignError(f"TTD call-context event {index} inputs differ")
    if _ttd_call_context_stack32(events[0], 2) == _ttd_call_context_stack32(
        events[9], 2
    ):
        raise CampaignError("TTD call-context contrasting slot-39 carriers collapsed")

    invocations = sorted(
        (row for row in rows if row.get("kind") == "invocation"),
        key=lambda row: _integer(row.get("invocation_index"), -1),
    )
    expected_invocations = (
        (0, 3, "3968", 0, 1, "CALL_ENTRY", None, False, True, False),
        (1, 1, "3968", 2, 3, "CALL_ENTRY", None, False, True, False),
        (2, 0, "4075", 6, 7, "CALL_ENTRY_RETURN", 8, True, False, False),
        (3, 3, "4095", 9, 10, "CALL_ENTRY", None, False, False, True),
    )
    for invocation, expected in zip(invocations, expected_invocations, strict=True):
        (
            index,
            target_index,
            epoch,
            call_index,
            entry_index,
            grade,
            return_index,
            return_checks,
            gap,
            continuity,
        ) = expected
        if (
            invocation.get("invocation_index") != index
            or invocation.get("target_index") != target_index
            or invocation.get("unique_thread_id") != "5"
            or invocation.get("association_epoch") != epoch
            or invocation.get("call_event_index") != call_index
            or invocation.get("entry_event_index") != entry_index
            or invocation.get("grade") != grade
            or invocation.get("return_event_index") != return_index
            or invocation.get("return_checks_passed") is not return_checks
            or invocation.get("gap_crossed") is not gap
            or invocation.get("continuity_break_crossed") is not continuity
            or invocation.get("call_entry_checks_passed") is not True
        ):
            raise CampaignError(f"TTD call-context invocation {index} differs")

    summary_rows = [row for row in rows if row.get("kind") == "summary"]
    summary = summary_rows[0]
    expected_summary = {
        "target_count": 4,
        "event_count": 12,
        "invocation_count": 4,
        "call_entry_pair_count": "4",
        "validated_return_count": "1",
        "raw_return_count": "4",
        "orphan_return_count": "3",
        "gap_free_envelope_count": "1",
        "association_barrier_count": "5744",
        "final_association_epoch": "5744",
        "final_position": "0x14C000:0x0",
        "stop_reason": "Position",
        "truncated": False,
        "callback_failed": False,
        "replay_counters_sane": True,
        "ordering_valid": True,
        "contexts_valid": True,
        "expectations_passed": True,
        "pairing_expectations_passed": True,
        "replay_complete": True,
        "collector_checks_passed": True,
    }
    if any(summary.get(key) != value for key, value in expected_summary.items()):
        raise CampaignError("TTD call-context summary differs")
    path_neutral = b"".join(raw_lines[1:])
    if (
        len(path_neutral) != 17804
        or hashlib.sha256(path_neutral).hexdigest()
        != TTD_CALL_CONTEXT_PATH_NEUTRAL_SHA256
    ):
        raise CampaignError("TTD call-context path-neutral evidence differs")
    return {
        "rawLines": raw_lines,
        "rows": rows,
        "targets": targets,
        "events": events,
        "invocations": invocations,
        "summary": summary,
    }


def _ttd_call_context_target_bindings() -> tuple[dict[str, object], ...]:
    specimen = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
    return (
        {
            "targetIndex": 0,
            "entryVa": "0x00407350",
            "entryRva": "0x00007350",
            "range": "0x7350-0x74cc",
            "rangeDigest": "1a0755c4837fed137b5c71d5a64c8318c45d535980eed6ff29c31142bb803879",
            "currentName": "CBattleEngine__VFunc_39_00407350",
            "contractId": "C-2f608ec63fd10347",
            "parentQuestionId": "Q-70f66b90e0dcf87b",
            "successorQuestionId": "Q-657753f5f004e39b",
            "entityKey": f"CODE:{specimen}:VA=0x00407350:RANGES=1a0755c4837fed137b5c71d5a64c8318c45d535980eed6ff29c31142bb803879",
            "positive": True,
        },
        {
            "targetIndex": 1,
            "entryVa": "0x0040a890",
            "entryRva": "0x0000a890",
            "range": "0xa890-0xac25",
            "rangeDigest": "bb7ad6db94943e1277f3036ffcd260b626115df2abd24670e57fcb80ba2bb244",
            "currentName": "CBattleEngine__VFunc_40_0040a890",
            "contractId": "C-62b3c956518ff9a5",
            "parentQuestionId": "Q-ba65fc321b8130ff",
            "successorQuestionId": "Q-c3a67dd02f317206",
            "entityKey": f"CODE:{specimen}:VA=0x0040a890:RANGES=bb7ad6db94943e1277f3036ffcd260b626115df2abd24670e57fcb80ba2bb244",
            "positive": True,
        },
        {
            "targetIndex": 2,
            "entryVa": "0x0040bfd0",
            "entryRva": "0x0000bfd0",
            "range": "0xbfd0-0xc17c",
            "rangeDigest": "9991ab479aabe7545a52a1044c37c13c6ea79fa975ba9095cded103809087817",
            "currentName": "CBattleEngine__StartDieProcess",
            "contractId": "C-54fb2fda0c8f391b",
            "parentQuestionId": "Q-3d0569982944c210",
            "successorQuestionId": None,
            "entityKey": f"CODE:{specimen}:VA=0x0040bfd0:RANGES=9991ab479aabe7545a52a1044c37c13c6ea79fa975ba9095cded103809087817",
            "positive": False,
        },
        {
            "targetIndex": 3,
            "entryVa": "0x004d8ae0",
            "entryRva": "0x000d8ae0",
            "range": "0xd8ae0-0xd8dbe",
            "rangeDigest": "528bde45ec7e6a660db02716e87c5d8accd8672ed5f89af729ec99ba8c6a1cbc",
            "currentName": "VFuncSlot_39_004d8ae0",
            "contractId": "C-a14d999cf14fbbe3",
            "parentQuestionId": "Q-df0c3509b8bb6d3a",
            "successorQuestionId": "Q-6fd2be929c0f027a",
            "entityKey": f"CODE:{specimen}:VA=0x004d8ae0:RANGES=528bde45ec7e6a660db02716e87c5d8accd8672ed5f89af729ec99ba8c6a1cbc",
            "positive": True,
        },
    )


def validate_ttd_call_context_observation(
    campaign: Path,
    evidence_root: Path,
    *,
    _verified_campaign_receipt: dict | None = None,
) -> dict[str, object]:
    """Reproduce and bind the exact replicated Level 521 schema-v3 evidence."""

    campaign = campaign.resolve()
    evidence_root = evidence_root.resolve()
    expected_evidence_root = (REPO_ROOT / TTD_CALL_CONTEXT_EVIDENCE_RELATIVE).resolve()
    if evidence_root != expected_evidence_root:
        raise CampaignError("TTD call-context evidence root is not the reviewed bundle")
    base_receipt = (
        _verified_campaign_receipt
        if _verified_campaign_receipt is not None
        else _verify_ttd_call_context_parent_campaign(campaign)
    )
    if (
        campaign != (REPO_ROOT / TTD_CALL_CONTEXT_PARENT_RELATIVE).resolve()
        or _integer(base_receipt.get("generation"), -1) != 9
        or base_receipt.get("counts") != TTD_CALL_CONTEXT_PARENT_COUNTS
        or coverage.sha256_of(campaign / "campaign.ready.json")
        != TTD_CALL_CONTEXT_PARENT_READY_SHA256
    ):
        raise CampaignError("TTD call-context parent is not finalized Generation 9")

    evidence_hashes = {
        "preregistration": ("preregistration.md", "cfe0f2bb03ebc554a9f207cbc48d4636213352ec054ca2f2c11f19a8037383a5"),
        "targets": ("targets.tsv", "38e69aaa8375c88982403b2c7760b1822e779cbaafdfb1612ed62806cbb4b885"),
        "semanticVerification": ("semantic-verification.json", TTD_CALL_CONTEXT_SEMANTIC_VERIFICATION_SHA256),
        "verifier": ("verify.py", TTD_CALL_CONTEXT_VERIFIER_SHA256),
        "proof": ("proof.ready.json", TTD_CALL_CONTEXT_PROOF_READY_SHA256),
        "runAReady": ("run-a/READY", "c132ec3b60a45b9b9d24fdef2462fc91ebc7dc961136255927bb04c92d2e233c"),
        "runAManifest": ("run-a/manifest.json", "bfff54237a9326ba9aad112ee258fc3fc5a25bfd710f4b0732e245d555588ee2"),
        "runAReceipt": ("run-a/receipt.json", "418a6e6793f7c643a040f5b53dd2a7e024f1c52eee0a4540cac4fba3b20d9503"),
        "runAContext": ("run-a/call-context.jsonl", "cc77ac676651bdea378ad57e414d5229d6f56b999e50757d1c1b308a34cdd72a"),
        "runATargets": ("run-a/targets.tsv", "38e69aaa8375c88982403b2c7760b1822e779cbaafdfb1612ed62806cbb4b885"),
        "runACollector": ("run-a/collector-tool/ttd_exec_coverage.exe", "6467c076f2ab987187b3674b7b43a86b34f1d2c23ed59b0cf820f49edf61c8d4"),
        "runAReplay": ("run-a/collector-tool/TTDReplay.dll", "b705235016778648f2c194aa76b54669c19ae318d16d340019f8a6f6c86fabbc"),
        "runAReplayCpu": ("run-a/collector-tool/TTDReplayCPU.dll", "b2a9a06a3c292ef58df31df70ab35a9440dceb3ee36de9c2b08ff4507dd8ef93"),
        "runABuildReceipt": ("run-a/collector-build-receipt.json", "69ab11c7ae841398f8e6a1efb4b9926ae80ab616e0536d08704ebd934b7dc4ef"),
        "runBReady": ("run-b/READY", "e13275f585673a0da358e0ee05b47c95d8fca5227beecd7edc79c4688e9487d1"),
        "runBManifest": ("run-b/manifest.json", "d1b5426ab47d978126efac6a09eaa8140d8a5e94f60652186b639ef2bfb3a559"),
        "runBReceipt": ("run-b/receipt.json", "91a0b248d6fe81db90fa1b89efb95de557b6cddf5ba174c27aa54f18495d6c24"),
        "runBContext": ("run-b/call-context.jsonl", "d99811a52911099818b07295e703398bcea96e7c5f3fdba987c5ca92150a37a1"),
        "runBTargets": ("run-b/targets.tsv", "38e69aaa8375c88982403b2c7760b1822e779cbaafdfb1612ed62806cbb4b885"),
        "runBCollector": ("run-b/collector-tool/ttd_exec_coverage.exe", "6467c076f2ab987187b3674b7b43a86b34f1d2c23ed59b0cf820f49edf61c8d4"),
        "runBReplay": ("run-b/collector-tool/TTDReplay.dll", "b705235016778648f2c194aa76b54669c19ae318d16d340019f8a6f6c86fabbc"),
        "runBReplayCpu": ("run-b/collector-tool/TTDReplayCPU.dll", "b2a9a06a3c292ef58df31df70ab35a9440dceb3ee36de9c2b08ff4507dd8ef93"),
        "runBBuildReceipt": ("run-b/collector-build-receipt.json", "69ab11c7ae841398f8e6a1efb4b9926ae80ab616e0536d08704ebd934b7dc4ef"),
    }
    artifacts = {
        role: _ttd_call_context_exact_stamp(
            evidence_root / relative, digest, role
        )
        for role, (relative, digest) in evidence_hashes.items()
    }
    repo_artifacts = {
        "pristine": _ttd_call_context_exact_stamp(
            REPO_ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup",
            "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
            "pristine specimen",
        ),
        "runtimeTarget": _ttd_call_context_exact_stamp(
            REPO_ROOT / "local-lab/safe-copy-bea-pristine/BEA.exe",
            TTD_CALL_CONTEXT_RUNTIME_SHA256,
            "runtime target",
        ),
        "wrapper": _ttd_call_context_exact_stamp(
            REPO_ROOT / "tools/Invoke-TtdCallContext.ps1",
            "c3f68cf2fffda9eb69d79d3e3a21d80ac5e656c33d2a6a20db851bf093e09400",
            "wrapper",
        ),
        "collectorSource": _ttd_call_context_exact_stamp(
            REPO_ROOT / "tools/ttd-exec-coverage/ttd_exec_coverage.cpp",
            "1b0140cc45fdd5e3a5dd66a3b2fe59914757b650865fbdea4ba307408d3375f0",
            "collector source",
        ),
    }

    frozen_verifier = (
        _FROZEN_LOCAL_LAB
        / "ttd-call-context-level521-impact-schema3-20260804-v1/verify.py"
    ).resolve()
    if (
        not frozen_verifier.is_file()
        or coverage.sha256_of(frozen_verifier) != TTD_CALL_CONTEXT_VERIFIER_SHA256
    ):
        raise CampaignError("TTD call-context frozen verifier identity differs")
    environment = os.environ.copy()
    environment["BEA_REPO_ROOT"] = str(REPO_ROOT.resolve())
    environment["BEA_TTD_CALL_CONTEXT_EVIDENCE"] = str(evidence_root)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                str(frozen_verifier),
                str(evidence_root / "run-a"),
                str(evidence_root / "run-b"),
            ],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CampaignError("TTD call-context frozen verifier timed out") from exc
    if completed.returncode != 0:
        raise CampaignError(
            "TTD call-context frozen verifier failed: "
            f"exit={completed.returncode} stderr={completed.stderr.strip()!r}"
        )
    try:
        reproduced_proof = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise CampaignError("TTD call-context frozen verifier emitted invalid JSON") from exc
    proof = _runtime_json(evidence_root / "proof.ready.json", "TTD call-context proof")
    if not _same_json(reproduced_proof, proof):
        raise CampaignError("TTD call-context proof does not reproduce byte-semantically")
    if (
        proof.get("schemaVersion") != TTD_CALL_CONTEXT_PROOF_SCHEMA
        or proof.get("status") != "READY_REPLICATED"
        or proof.get("verdict") != "SURVIVED"
        or proof.get("refutation", {}).get("verdict") != "SURVIVED"
        or str(proof.get("boundary", {}).get("verifierSha256", "")).lower()
        != TTD_CALL_CONTEXT_VERIFIER_SHA256
    ):
        raise CampaignError("TTD call-context proof boundary did not survive")

    run_a = _validate_ttd_call_context_jsonl(evidence_root / "run-a/call-context.jsonl")
    run_b = _validate_ttd_call_context_jsonl(evidence_root / "run-b/call-context.jsonl")
    if run_a["rawLines"][1:] != run_b["rawLines"][1:]:
        raise CampaignError("TTD call-context replicas differ after path-bearing metadata")

    target_rows = _read_tsv(evidence_root / "targets.tsv")
    expected_target_rows = [
        {
            "target_index": str(index),
            "entry_rva": entry,
            "range_start_rva": start,
            "range_end_rva_exclusive": end,
            "expected_entry_count": entries,
            "expected_call_count": calls,
            "expected_return_count": returns,
        }
        for index, entry, start, end, entries, calls, returns in (
            (0, "0x7350", "0x7350", "0x74CC", "1", "1", "1"),
            (1, "0xA890", "0xA890", "0xAC25", "1", "1", "1"),
            (2, "0xBFD0", "0xBFD0", "0xC17C", "0", "0", "0"),
            (3, "0xD8AE0", "0xD8AE0", "0xD8DBE", "2", "2", "2"),
        )
    ]
    if target_rows != expected_target_rows:
        raise CampaignError("TTD call-context target table rows differ")

    campaign_rows = _campaign_rows_from_root(campaign)
    function_by_va = {row["entryVa"]: row for row in campaign_rows["functions"]}
    contract_by_id = {row["contractId"]: row for row in campaign_rows["contracts"]}
    question_by_id = {row["questionId"]: row for row in campaign_rows["questions"]}
    if len(function_by_va) != len(campaign_rows["functions"]):
        raise CampaignError("TTD call-context parent has duplicate function VAs")
    for binding in _ttd_call_context_target_bindings():
        function = function_by_va.get(str(binding["entryVa"]))
        contract = contract_by_id.get(str(binding["contractId"]))
        question = question_by_id.get(str(binding["parentQuestionId"]))
        if function is None or contract is None or question is None:
            raise CampaignError("TTD call-context target is absent from Generation 9")
        if (
            function.get("entityKey") != binding["entityKey"]
            or function.get("entryRva") != binding["entryRva"]
            or function.get("bodyRangesRva") != binding["range"]
            or function.get("bodyRangeSetSha256") != binding["rangeDigest"]
            or function.get("currentName") != binding["currentName"]
            or contract.get("entityKey") != binding["entityKey"]
            or contract.get("entryVa") != binding["entryVa"]
            or contract.get("currentName") != binding["currentName"]
            or contract.get("contractState") != "OPEN"
            or contract.get("semanticGrade") != "C0_OPAQUE"
            or contract.get("writes") != "UNKNOWN"
            or contract.get("rebuildState") != "NOT_READY"
            or question.get("entityKey") != binding["entityKey"]
            or question.get("state") != "OPEN"
            or question.get("generation") != "0"
            or str(binding["parentQuestionId"])
            not in contract.get("questionIds", "").split(";")
        ):
            raise CampaignError("TTD call-context Generation 9 target binding differs")

    pristine_bytes = Path(str(repo_artifacts["pristine"]["path"])).read_bytes()
    runtime_bytes = Path(str(repo_artifacts["runtimeTarget"]["path"])).read_bytes()
    if len(pristine_bytes) != len(runtime_bytes) or tuple(
        (index, left, right)
        for index, (left, right) in enumerate(
            zip(pristine_bytes, runtime_bytes, strict=True)
        )
        if left != right
    ) != (
        (0x12A644, 0xA1, 0xB8),
        (0x12A645, 0xF0, 0x01),
        (0x12A646, 0x2D, 0x00),
        (0x12A647, 0x66, 0x00),
    ):
        raise CampaignError("TTD runtime target is not the exact four-byte derivative")

    receipt_a = _runtime_json(evidence_root / "run-a/receipt.json", "TTD run A receipt")
    receipt_b = _runtime_json(evidence_root / "run-b/receipt.json", "TTD run B receipt")
    trace_a = _runtime_mapping(receipt_a.get("trace"), "TTD run A trace")
    trace_b = _runtime_mapping(receipt_b.get("trace"), "TTD run B trace")
    if not _same_json(trace_a, trace_b):
        raise CampaignError("TTD call-context replicas name different traces")
    trace_path = Path(str(trace_a.get("path", ""))).resolve()
    if (
        str(trace_a.get("sha256", "")).lower() != TTD_CALL_CONTEXT_TRACE_SHA256
        or _integer(trace_a.get("bytes"), -1) != 14214496256
        or not trace_path.is_file()
        or trace_path.stat().st_size != 14214496256
    ):
        raise CampaignError("TTD call-context bound trace stat/identity differs")
    if str(receipt_b.get("generatedAtUtc", "")) != TTD_CALL_CONTEXT_MEASURED_AT_UTC:
        raise CampaignError("TTD call-context measurement timestamp differs")

    evidence_refs = [
        f"{stamp['path']}#sha256={stamp['sha256']}"
        for stamp in (
            repo_artifacts["pristine"],
            repo_artifacts["runtimeTarget"],
            artifacts["preregistration"],
            artifacts["targets"],
            artifacts["verifier"],
            artifacts["runAReady"],
            artifacts["runBReady"],
            artifacts["semanticVerification"],
            artifacts["proof"],
        )
    ]
    return {
        "baseReceipt": base_receipt,
        "evidenceRoot": str(evidence_root),
        "artifacts": artifacts,
        "repoArtifacts": repo_artifacts,
        "trace": {
            "path": str(trace_path),
            "bytes": 14214496256,
            "sha256": TTD_CALL_CONTEXT_TRACE_SHA256,
            "hashReadFromBoundReceipt": True,
            "actualBytesVerified": True,
        },
        "proof": proof,
        "evidenceRefs": evidence_refs,
        "bindings": list(_ttd_call_context_target_bindings()),
        "measuredAtUtc": TTD_CALL_CONTEXT_MEASURED_AT_UTC,
        "observation": {
            "window": "0x14A000:0x0..0x14C000:0x0 inclusive",
            "thread": "5",
            "calls": 4,
            "entries": 4,
            "rawReturns": 4,
            "validatedReturns": 1,
            "orphanReturns": 3,
            "gapFreeEnvelopes": 1,
            "associationBarriers": 5744,
            "pathNeutralEvidenceBytes": 17804,
            "pathNeutralEvidenceSha256": TTD_CALL_CONTEXT_PATH_NEUTRAL_SHA256,
        },
    }


def _ttd_call_context_contract_specs() -> dict[str, dict[str, object]]:
    return {
        "0x004d8ae0": {
            "successor": {
                "questionType": "EXECUTED_FUNCTION_CONTRACT",
                "priority": 1,
                "score": 666.0,
                "requiresElevation": False,
                "recommendedInstrument": "TTD_THREAD_AWARE_CALL_CONTEXT_PLUS_STATIC_BRANCH_JOIN",
                "question": "What branch predicate and complete per-invocation contract distinguish the observed 0x004d8ae0 slot-39 path that calls 0x0040a890 from the contrasting path that does not, and what concrete virtual identity, writes, and typed return (if any) does the function have?",
                "cheapestFalsifier": "A thread-aware replay over the same window fails to preserve the two distinct slot-39 paths or links a return/value that contradicts the schema-v3 raw events.",
                "source": "ttd-call-context-observation",
                "currentOwner": "recursive-re-campaign",
            },
            "receiver": "RAW_ECX=0x07A30830 (invocation 0); RAW_ECX=0x07994020 (invocation 3); capture-local untyped carriers",
            "inputs": "invocation 0 stack32=[0x079B9750,0x001AF2CC]; invocation 3 stack32=[0x079C2C60,0x001AF2CC]; raw untyped carriers",
            "returns": "UNKNOWN; raw orphan RET@0x004D8D97 carriers EDX:EAX=0x0000002B:0x03865B38 and 0x00000033:0x03865AA0; neither is linked to an invocation",
            "writes": "UNKNOWN; schema-v3 records no memory-write observations",
            "sideEffects": "selected same-thread order: call 0x004268CB->0x004D8AE0; first observed invocation later calls 0x004D8CEF->0x0040A890; after its orphan raw return, caller 0x004268DE calls 0x00407350; contrasting second 0x004D8AE0 invocation has no selected 0x0040A890/0x00407350 event before its orphan raw return",
            "preconditions": "natural Level 521 take-4 trace; inclusive 0x14A000:0x0..0x14C000:0x0 window; unique thread 5; exactly two selected calls/entries/raw returns",
            "failureModes": "UNKNOWN; carriers are untyped and capture-local; both raw returns are orphaned by association barriers; no memory-write, typed-return, complete-callee, or outside-window claim is admitted; the contrasting invocation refutes a universal slot-39-damages law",
            "remaining": "concrete virtual identity; branch predicate; typed receiver and inputs; memory writes; typed return; complete callees and failure behavior; behavior outside the inclusive window; rebuild mapping and focused parity test",
        },
        "0x0040a890": {
            "successor": {
                "questionType": "EXECUTED_FUNCTION_CONTRACT",
                "priority": 2,
                "score": 680.0,
                "requiresElevation": False,
                "recommendedInstrument": "TTD_THREAD_AWARE_CALL_CONTEXT_PLUS_DATA_WRITE_WINDOW",
                "question": "Which exact fields change across the observed 0x0040a890 call, what conditions select those writes, and can its raw return boundary be linked to the invocation without crossing an association barrier?",
                "cheapestFalsifier": "A bounded data-write replay or CDB watchpoint shows no write attributable to 0x0040a890, or a thread-aware replay disproves the observed call carriers.",
                "source": "ttd-call-context-observation",
                "currentOwner": "recursive-re-campaign",
            },
            "receiver": "RAW_ECX=0x079B9750; capture-local untyped carrier",
            "inputs": "stack32=[0x3D4CCCCD,0x07A30830,0x00000001,0xFFFFFFFF] at caller 0x004D8CEF; raw untyped carriers; 0x3D4CCCCD is not promoted as a typed float by this lane",
            "returns": "UNKNOWN; raw RET@0x0040AC22 carried EDX:EAX=0x00000001:0x00000001 but was orphaned after an association-epoch change",
            "writes": "UNKNOWN; schema-v3 records no memory-write observations",
            "sideEffects": "selected call 0x004D8CEF->0x0040A890 with fallthrough 0x004D8CF5 occurs after the first 0x004D8AE0 slot-39 entry; no gap-free return envelope is admitted",
            "preconditions": "natural Level 521 take-4 trace; inclusive 0x14A000:0x0..0x14C000:0x0 window; unique thread 5; exactly one selected call/entry/raw return",
            "failureModes": "UNKNOWN; carriers are untyped and capture-local; the raw return is orphaned; no memory-write, typed-return, branch, failure-path, or outside-window claim is admitted",
            "remaining": "typed receiver and inputs; exact memory writes and selecting conditions; linked return semantics; failure behavior; other values and classes; behavior outside the inclusive window; rebuild mapping and focused parity test",
        },
        "0x00407350": {
            "successor": {
                "questionType": "EXECUTED_FUNCTION_CONTRACT",
                "priority": 2,
                "score": 345.0,
                "requiresElevation": False,
                "recommendedInstrument": "TTD_DATA_WRITE_WINDOW_PLUS_STATIC_ABI_JOIN",
                "question": "Which exact fields change across the observed 0x00407350 call, and what—if anything—does its linked raw EAX carrier mean under the retail ABI?",
                "cheapestFalsifier": "A bounded data-write replay finds no attributable write, or static ABI evidence contradicts any proposed type for the linked raw EAX carrier.",
                "source": "ttd-call-context-observation",
                "currentOwner": "recursive-re-campaign",
            },
            "receiver": "RAW_ECX=0x079B9750; capture-local untyped carrier",
            "inputs": "stack32=[0x07A30830,0x001AF2CC] at caller 0x004268DE; raw untyped carriers",
            "returns": "semantic return UNKNOWN; linked ordinary RET@0x004074C9 carried raw EDX:EAX=0x005D89C4:0x07A30830",
            "writes": "UNKNOWN; schema-v3 records no memory-write observations",
            "sideEffects": "gap-free CALL_ENTRY_RETURN envelope from caller 0x004268DE to target 0x00407350 with fallthrough 0x004268E4; selected after the first slot-39 raw return",
            "preconditions": "natural Level 521 take-4 trace; inclusive 0x14A000:0x0..0x14C000:0x0 window; unique thread 5; exactly one selected gap-free invocation",
            "failureModes": "UNKNOWN; the linked raw carrier is not promoted as a pointer or semantic return; carriers remain untyped; no memory-write, alternate-path, failure-path, or outside-window claim is admitted",
            "remaining": "typed receiver and inputs; exact memory writes; raw return meaning; failure behavior; alternate paths; behavior outside the inclusive window; rebuild mapping and focused parity test",
        },
    }


def _ttd_call_context_delta(
    before: dict[str, list[dict[str, str]]],
    after: dict[str, list[dict[str, str]]],
) -> dict[str, object]:
    unchanged = ("residuals", "scenarios", "levers", "supersessions")
    if any(before[name] != after[name] for name in unchanged):
        raise CampaignError("TTD call-context advance changed an unrelated ledger")

    def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
        result = {row[field]: row for row in rows}
        if len(result) != len(rows):
            raise CampaignError(f"TTD call-context delta has duplicate {field}")
        return result

    function_before = keyed(before["functions"], "entityKey")
    function_after = keyed(after["functions"], "entityKey")
    contract_before = keyed(before["contracts"], "contractId")
    contract_after = keyed(after["contracts"], "contractId")
    question_before = keyed(before["questions"], "questionId")
    question_after = keyed(after["questions"], "questionId")
    adjudication_before = keyed(before["adjudications"], "adjudicationId")
    adjudication_after = keyed(after["adjudications"], "adjudicationId")
    if (
        set(function_before) != set(function_after)
        or set(contract_before) != set(contract_after)
        or not set(question_before) <= set(question_after)
        or not set(adjudication_before) <= set(adjudication_after)
    ):
        raise CampaignError("TTD call-context advance changed entity identities")

    function_allowed = {
        "semanticGrade",
        "resolutionState",
        "campaignState",
        "lever",
        "requiresElevation",
        "cheapestFalsifier",
        "evidenceStates",
        "lastMeasurementDate",
    }
    zero_allowed = {"evidenceStates", "lastMeasurementDate"}
    contract_allowed = {
        "contractState",
        "semanticGrade",
        "receiver",
        "inputs",
        "returns",
        "writes",
        "sideEffects",
        "preconditions",
        "failureModes",
        "authorVerdict",
        "runtimeVerdict",
        "refuterVerdict",
        "questionIds",
        "evidenceRefs",
        "cheapestFalsifier",
        "remainingUncertainty",
        "lastMeasurementDate",
    }
    zero_contract_allowed = {
        "authorVerdict",
        "runtimeVerdict",
        "evidenceRefs",
        "remainingUncertainty",
        "lastMeasurementDate",
    }
    bindings = _ttd_call_context_target_bindings()
    positive_entities = {
        str(row["entityKey"]) for row in bindings if row["positive"] is True
    }
    zero_entity = next(
        str(row["entityKey"]) for row in bindings if row["positive"] is False
    )
    function_changes: dict[str, list[str]] = {}
    for entity, prior in function_before.items():
        current = function_after[entity]
        changed = sorted(field for field in FUNCTION_COLUMNS if prior[field] != current[field])
        if changed:
            allowed = zero_allowed if entity == zero_entity else function_allowed
            if entity not in positive_entities | {zero_entity} or not set(changed) <= allowed:
                raise CampaignError("TTD call-context function delta exceeds its whitelist")
            function_changes[entity] = changed
    if set(function_changes) != positive_entities | {zero_entity}:
        raise CampaignError("TTD call-context function delta population differs")

    positive_contracts = {
        str(row["contractId"]) for row in bindings if row["positive"] is True
    }
    zero_contract = next(
        str(row["contractId"]) for row in bindings if row["positive"] is False
    )
    contract_changes: dict[str, list[str]] = {}
    for contract_id, prior in contract_before.items():
        current = contract_after[contract_id]
        changed = sorted(field for field in CONTRACT_COLUMNS if prior[field] != current[field])
        if changed:
            allowed = zero_contract_allowed if contract_id == zero_contract else contract_allowed
            if contract_id not in positive_contracts | {zero_contract} or not set(changed) <= allowed:
                raise CampaignError("TTD call-context contract delta exceeds its whitelist")
            contract_changes[contract_id] = changed
    if set(contract_changes) != positive_contracts | {zero_contract}:
        raise CampaignError("TTD call-context contract delta population differs")

    modified_questions: dict[str, list[str]] = {}
    for question_id, prior in question_before.items():
        current = question_after[question_id]
        changed = sorted(field for field in QUESTION_COLUMNS if prior[field] != current[field])
        if changed:
            if set(changed) - {
                "state",
                "attemptCount",
                "lastOutcome",
                "lastMeasurementDate",
            }:
                raise CampaignError("TTD call-context parent-question delta exceeds its whitelist")
            modified_questions[question_id] = changed
    expected_parents = {
        str(row["parentQuestionId"]) for row in bindings if row["positive"] is True
    }
    added_questions = sorted(set(question_after) - set(question_before))
    expected_successors = sorted(
        str(row["successorQuestionId"])
        for row in bindings
        if row["positive"] is True
    )
    if set(modified_questions) != expected_parents or added_questions != expected_successors:
        raise CampaignError("TTD call-context question delta population differs")
    added_adjudications = sorted(set(adjudication_after) - set(adjudication_before))
    if len(added_adjudications) != 3:
        raise CampaignError("TTD call-context adjudication delta population differs")
    if any(
        function_before[entity].get("currentName")
        != function_after[entity].get("currentName")
        or function_before[entity].get("bodyRangesRva")
        != function_after[entity].get("bodyRangesRva")
        for entity in function_before
    ):
        raise CampaignError("TTD call-context advance changed a name or range")
    return {
        "functionRowsChanged": function_changes,
        "contractRowsChanged": contract_changes,
        "questionRowsChanged": modified_questions,
        "questionIdsAdded": added_questions,
        "adjudicationIdsAdded": added_adjudications,
        "unchangedLedgers": list(unchanged),
        "namesChanged": 0,
        "rangesChanged": 0,
        "supersessionsAdded": 0,
        "rebuildMappingsChanged": 0,
    }


def advance_ttd_call_context_observation(
    campaign: Path,
    evidence_root: Path,
    out: Path,
    *,
    _self_check: bool = True,
    _verified_parent_receipt: dict | None = None,
) -> dict:
    """Admit the exact Level 521 observation without overpromoting semantics."""

    if out.exists():
        raise CampaignError(f"refusing existing advanced-campaign destination: {out}")
    base_receipt = (
        _verified_parent_receipt
        if _verified_parent_receipt is not None
        else _verify_ttd_call_context_parent_campaign(campaign)
    )
    validated = validate_ttd_call_context_observation(
        campaign,
        evidence_root,
        _verified_campaign_receipt=base_receipt,
    )
    before = _campaign_rows_from_root(campaign)
    rows = json.loads(json.dumps(before))
    functions_by_entity = {row["entityKey"]: row for row in rows["functions"]}
    contracts_by_id = {row["contractId"]: row for row in rows["contracts"]}
    questions_by_id = {row["questionId"]: row for row in rows["questions"]}
    specs = _ttd_call_context_contract_specs()
    measured_at = str(validated["measuredAtUtc"])
    measured_date = measured_at[:10]
    next_generation = 10
    proof_sha = str(validated["artifacts"]["proof"]["sha256"])
    semantic_sha = str(
        validated["artifacts"]["semanticVerification"]["sha256"]
    )
    evidence_refs = list(validated["evidenceRefs"])
    evidence_hashes = [
        proof_sha,
        str(validated["artifacts"]["verifier"]["sha256"]),
        str(validated["artifacts"]["runAReady"]["sha256"]),
        str(validated["artifacts"]["runBReady"]["sha256"]),
        str(validated["artifacts"]["preregistration"]["sha256"]),
        str(validated["artifacts"]["targets"]["sha256"]),
        semantic_sha,
    ]
    parent_ready_sha = coverage.sha256_of(campaign / "campaign.ready.json")
    promoted_rows: list[dict[str, object]] = []

    for binding in validated["bindings"]:
        entity = str(binding["entityKey"])
        function = functions_by_entity[entity]
        contract = contracts_by_id[str(binding["contractId"])]
        if binding["positive"] is not True:
            function["evidenceStates"] = _append_state(
                function["evidenceStates"], "TTD_BOUNDED_ZERO_EVENT_CONTROL"
            )
            function["lastMeasurementDate"] = measured_date
            contract["authorVerdict"] = "PREREGISTERED_ZERO_EVENT_CONTROL"
            contract["runtimeVerdict"] = "REPLICATED_BOUNDED_ZERO_EVENT_CONTROL"
            for reference in evidence_refs:
                contract["evidenceRefs"] = _append_state(
                    contract.get("evidenceRefs", ""), reference
                )
            contract["remainingUncertainty"] = (
                "receiver; inputs; returns; writes; side effects; preconditions; "
                "failure modes; the replicated zero selected events apply only to "
                "the exact Level 521 window and do not establish non-reachability"
            )
            contract["lastMeasurementDate"] = measured_date
            continue

        spec = specs[str(binding["entryVa"])]
        parent = questions_by_id[str(binding["parentQuestionId"])]
        successor = _successor_question(
            dict(spec["successor"]),
            entity_key=entity,
            parents=[parent],
            history=[row for row in rows["questions"] if row["entityKey"] == entity],
            generation=next_generation,
            measured_at=measured_at,
        )
        if successor["questionId"] != binding["successorQuestionId"]:
            raise CampaignError("TTD call-context successor identity differs")
        parent["state"] = "CLOSED_SURVIVED"
        parent["attemptCount"] = _integer(parent.get("attemptCount"), 0) + 1
        parent["lastOutcome"] = "SURVIVED"
        parent["lastMeasurementDate"] = measured_at
        rows["questions"].append(successor)
        questions_by_id[successor["questionId"]] = successor

        function["semanticGrade"] = "C2_BOUNDED_RUNTIME"
        function["resolutionState"] = "BOUNDED_CONTRACT"
        function["campaignState"] = "OPEN_AFTER_SURVIVED"
        function["lever"] = successor["recommendedInstrument"]
        function["requiresElevation"] = str(successor["requiresElevation"])
        function["cheapestFalsifier"] = successor["cheapestFalsifier"]
        function["evidenceStates"] = _append_state(
            function["evidenceStates"], "TTD_CALL_CONTEXT_OBSERVATION"
        )
        function["evidenceStates"] = _append_state(
            function["evidenceStates"], "INDEPENDENT_REFUTATION_SURVIVED"
        )
        function["lastMeasurementDate"] = measured_date

        contract["contractState"] = "BOUNDED_CONTRACT_ADVANCED"
        contract["semanticGrade"] = "C2_BOUNDED_RUNTIME"
        for field in (
            "receiver",
            "inputs",
            "returns",
            "writes",
            "sideEffects",
            "preconditions",
            "failureModes",
        ):
            contract[field] = str(spec[field])
        contract["authorVerdict"] = "PREREGISTERED_REPLICATED_NATURAL_TRACE"
        contract["runtimeVerdict"] = (
            "REPLICATED_SCHEMA3_CALL_ENTRY_CONTEXT_MEASURED"
        )
        contract["refuterVerdict"] = "SURVIVED"
        contract["questionIds"] = _append_state(
            contract["questionIds"], successor["questionId"]
        )
        for reference in evidence_refs:
            contract["evidenceRefs"] = _append_state(
                contract.get("evidenceRefs", ""), reference
            )
        contract["cheapestFalsifier"] = successor["cheapestFalsifier"]
        contract["remainingUncertainty"] = str(spec["remaining"])
        contract["lastMeasurementDate"] = measured_date
        if (
            contract["rebuildOwner"] != "UNASSIGNED"
            or contract["rebuildImplementation"] != "UNMAPPED"
            or contract["parityTests"] != "UNMAPPED"
            or contract["rebuildState"] != "NOT_READY"
            or contract["supersedesEntityKeys"]
        ):
            raise CampaignError("TTD call-context contract crossed the rebuild boundary")

        adjudication_id = "A-" + _sha256_text(
            "|".join(
                (
                    parent_ready_sha,
                    semantic_sha,
                    proof_sha,
                    contract["contractId"],
                    parent["questionId"],
                    "SURVIVED",
                )
            )
        )[:16]
        if any(
            row.get("adjudicationId") == adjudication_id
            for row in rows["adjudications"]
        ):
            raise CampaignError("TTD call-context adjudication already exists")
        rows["adjudications"].append(
            {
                "adjudicationId": adjudication_id,
                "baseContractId": contract["contractId"],
                "entityKey": entity,
                "overlaySchema": TTD_CALL_CONTEXT_PROOF_SCHEMA,
                "overlayReadySha256": proof_sha,
                "questionIdsAddressed": parent["questionId"],
                "refuterVerdict": "SURVIVED",
                "refuterEvidenceSha256": ";".join(evidence_hashes),
                "semanticPromotionApplied": True,
                "terminalState": "",
                "successorQuestionIds": successor["questionId"],
                "remainingUncertainty": contract["remainingUncertainty"],
                "measuredAtUtc": measured_at,
            }
        )
        promoted_rows.append(
            {
                "entityKey": entity,
                "entryVa": binding["entryVa"],
                "contractId": contract["contractId"],
                "parentQuestionId": parent["questionId"],
                "successorQuestionId": successor["questionId"],
                "adjudicationId": adjudication_id,
            }
        )

    delta = _ttd_call_context_delta(before, rows)
    counts = {name: len(rows[name]) for name in rows}
    if counts != TTD_CALL_CONTEXT_EXPECTED_GENERATION10_COUNTS:
        raise CampaignError("TTD call-context Generation 10 row counts differ")
    observation_id = "CO-" + _sha256_text(
        "|".join((parent_ready_sha, proof_sha, TTD_CALL_CONTEXT_ADVANCE_KIND))
    )[:16]
    output_rows = {
        "campaign-functions.tsv": (FUNCTION_COLUMNS, rows["functions"]),
        "campaign-residuals.tsv": (RESIDUAL_COLUMNS, rows["residuals"]),
        "campaign-questions.tsv": (QUESTION_COLUMNS, rows["questions"]),
        "campaign-scenarios.tsv": (SCENARIO_COLUMNS, rows["scenarios"]),
        "campaign-levers.tsv": (LEVER_COLUMNS, rows["levers"]),
        "campaign-contracts.tsv": (CONTRACT_COLUMNS, rows["contracts"]),
        "campaign-adjudications.tsv": (ADJUDICATION_COLUMNS, rows["adjudications"]),
        "campaign-supersessions.tsv": (SUPERSESSION_COLUMNS, rows["supersessions"]),
    }
    base_ready = coverage.file_stamp(campaign / "campaign.ready.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        for name, (columns, output) in output_rows.items():
            _write_tsv(stage / name, columns, output)
        reducer = _publish_reducer(stage)
        advance = {
            "kind": TTD_CALL_CONTEXT_ADVANCE_KIND,
            "schema": TTD_CALL_CONTEXT_ADVANCE_SCHEMA,
            "observationId": observation_id,
            "verdict": "SURVIVED",
            "evidence": {
                "root": str(evidence_root.resolve()),
                "artifacts": validated["artifacts"],
                "repoArtifacts": validated["repoArtifacts"],
                "trace": validated["trace"],
            },
            "proofSchema": TTD_CALL_CONTEXT_PROOF_SCHEMA,
            "proofReadySha256": proof_sha,
            "measuredAtUtc": measured_at,
            "observation": validated["observation"],
            "targets": validated["bindings"],
            "promotions": promoted_rows,
            "boundedZeroEventControl": {
                "entryVa": "0x0040bfd0",
                "contractId": "C-54fb2fda0c8f391b",
                "calls": 0,
                "entries": 0,
                "rawReturns": 0,
                "questionClosed": False,
                "semanticGradeChanged": False,
                "negativeBehavioralLawClaimed": False,
            },
            "delta": delta,
            "questionsClosed": 3,
            "questionsAdded": 3,
            "adjudicationsAdded": 3,
            "namesChanged": 0,
            "writesProved": 0,
            "rebuildParityProved": False,
            "supersessionsAdded": 0,
            "semanticLimitations": [
                "0x004D8AE0 retains its address/slot label; no concrete virtual identity was proved.",
                "All ECX, stack, EAX, and EDX values remain raw untyped capture-local carriers.",
                "Only one Hit return was linked; three raw returns remain orphaned across association barriers.",
                "The lane records no memory writes and proves no typed return or rebuild-ready behavior.",
                "StartDie zero events apply only to the exact inclusive window and are not a non-reachability law.",
            ],
        }
        receipt = {
            "schema": SCHEMA,
            "reducer": reducer,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "generation": next_generation,
            "parentCampaign": {
                "path": str(campaign.resolve()),
                "ready": {**base_ready, "path": "campaign.ready.json"},
            },
            "sourceSnapshot": base_receipt["sourceSnapshot"],
            "advance": advance,
            "counts": counts,
            "questionTypes": dict(
                Counter(row["questionType"] for row in rows["questions"])
            ),
            "policies": [
                "Only three exact Generation 9 function contracts receive C2 bounded-runtime advances.",
                "Raw carriers remain untyped; orphan return boundaries are never forged into invocation backlinks.",
                "The StartDie zero-event control remains OPEN/C0 and is bounded to the exact replay window.",
                "No name, range, memory-write, rebuild mapping, parity, or supersession claim is promoted.",
                "The frozen reducer replays both replicas, the independent proof, and the exact row delta.",
            ],
            "outputs": {
                name: {**coverage.file_stamp(stage / name), "path": name}
                for name in OUTPUTS
            },
        }
        (stage / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        if _self_check:
            verify(stage)
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def advance_runtime_contract(
    campaign: Path,
    overlay: Path,
    adjudication_path: Path,
    out: Path,
    *,
    _self_check: bool = True,
    _verified_parent_receipt: dict | None = None,
) -> dict:
    """Reduce one refuted runtime overlay into a new immutable campaign generation."""
    base_receipt = (
        _verified_parent_receipt
        if _verified_parent_receipt is not None
        else verify(campaign)
    )
    overlay_receipt = verify_runtime_contract_overlay(overlay)
    if out.exists():
        raise CampaignError(f"refusing existing advanced-campaign destination: {out}")
    adjudication = _runtime_json(adjudication_path, "runtime adjudication")
    if adjudication.get("schema") != RUNTIME_ADJUDICATION_SCHEMA:
        raise CampaignError(
            f"unsupported runtime adjudication schema: {adjudication.get('schema')!r}"
        )
    base_ready = coverage.file_stamp(campaign / "campaign.ready.json")
    overlay_ready = coverage.file_stamp(overlay / "runtime-contracts.ready.json")
    if adjudication.get("baseCampaignReadySha256") != base_ready["sha256"]:
        raise CampaignError("runtime adjudication names a different base campaign READY receipt")
    if adjudication.get("overlayReadySha256") != overlay_ready["sha256"]:
        raise CampaignError("runtime adjudication names a different runtime overlay READY receipt")
    overlay_source = _runtime_mapping(
        overlay_receipt.get("sourceCampaign"), "runtime overlay sourceCampaign"
    )
    overlay_source_ready = _runtime_mapping(
        overlay_source.get("ready"), "runtime overlay sourceCampaign.ready"
    )
    if overlay_source_ready.get("sha256") != base_ready["sha256"]:
        raise CampaignError("runtime overlay was not derived from the supplied base campaign")

    overlay_rows = _read_tsv(overlay / "runtime-contracts.tsv")
    if len(overlay_rows) != 1:
        raise CampaignError("runtime advance currently requires exactly one overlay contract")
    overlay_row = overlay_rows[0]
    decision = _runtime_mapping(adjudication.get("decision"), "adjudication decision")
    verdict = decision.get("refuterVerdict")
    if verdict not in {"SURVIVED", "REFUTED", "UNSCORED"}:
        raise CampaignError("runtime adjudication refuterVerdict is unsupported")
    if decision.get("baseContractId") != overlay_row.get("baseContractId"):
        raise CampaignError("runtime adjudication and overlay name different base contracts")
    addressed = _runtime_list(
        decision.get("questionIdsAddressed"), "adjudication questionIdsAddressed"
    )
    if (
        not addressed
        or any(not isinstance(value, str) or not value for value in addressed)
        or len(addressed) != len(set(addressed))
        or set(addressed)
        != {value for value in overlay_row.get("questionIdsAddressed", "").split(";") if value}
    ):
        raise CampaignError("runtime adjudication question IDs do not exactly reproduce the overlay")
    measured_at = str(decision.get("measuredAtUtc", ""))
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T[^\s]+", measured_at):
        raise CampaignError("runtime adjudication lacks measuredAtUtc")

    evidence_specs = _runtime_list(decision.get("refuterEvidence"), "refuter evidence")
    if not evidence_specs or any(not isinstance(row, dict) for row in evidence_specs):
        raise CampaignError("runtime adjudication requires structured refuter evidence")
    evidence_stamps = []
    evidence_paths: dict[str, Path] = {}
    for index, item in enumerate(evidence_specs):
        role = str(item.get("role", "")).strip()
        if not role or role in evidence_paths:
            raise CampaignError("runtime adjudication refuter evidence has duplicate/missing roles")
        evidence_paths[role] = _runtime_artifact_path(
            adjudication_path, item.get("path"), f"refuter:{role or index}"
        )
        evidence_stamps.append(
            _runtime_artifact_stamp(
                adjudication_path,
                item.get("path"),
                item.get("sha256"),
                f"refuter:{role or index}",
            )
        )
    if len(set(evidence_paths.values())) != len(evidence_paths):
        raise CampaignError("runtime adjudication refuter evidence aliases artifacts")
    result_path = evidence_paths.get("refuter-result")
    if result_path is None:
        raise CampaignError("runtime adjudication lacks the parsed refuter-result artifact")
    refuter_result = _runtime_json(result_path, "refuter result")
    expected_subject = _runtime_refuter_subject(
        overlay_row, overlay_ready["sha256"]
    )
    if refuter_result.get("tool") == "tools/probe/refute.py":
        finding_path = evidence_paths.get("refuter-finding")
        if finding_path is None:
            raise CampaignError("probe refuter result lacks its hash-bound finding input")
        finding = _runtime_json(finding_path, "refuter finding")
        if (
            not _same_json(finding.get("subject"), expected_subject)
            or not _same_json(refuter_result.get("subject"), expected_subject)
        ):
            raise CampaignError(
                "probe refuter finding/result is not bound to the exact candidate contract"
            )
        min_sample = refuter_result.get("minSampleN")
        if not isinstance(min_sample, int) or min_sample < 1:
            raise CampaignError("probe refuter result has an invalid minSampleN")
        reproduced = probe_refute.adjudicate(finding, min_sample_n=min_sample)
        observed_without_source = {
            key: value for key, value in refuter_result.items() if key != "source"
        }
        if reproduced != observed_without_source:
            raise CampaignError("probe refuter result does not reproduce from its finding")
        if refuter_result.get("verdict") != verdict:
            raise CampaignError("probe refuter verdict disagrees with the adjudication")
    elif verdict == "SURVIVED":
        raise CampaignError(
            "SURVIVED semantic promotion requires a mechanically replayed probe refuter"
        )
    elif (
        refuter_result.get("schema") != REFUTER_RESULT_SCHEMA
        or refuter_result.get("verdict") != verdict
        or refuter_result.get("baseContractId") != overlay_row.get("baseContractId")
        or refuter_result.get("overlayReadySha256") != overlay_ready["sha256"]
        or set(refuter_result.get("questionIdsAddressed", [])) != set(addressed)
        or not isinstance(refuter_result.get("findings"), list)
        or not str(refuter_result.get("reason", "")).strip()
    ):
        raise CampaignError("refuter result does not reproduce the adjudication subject/verdict")

    functions = _read_tsv(campaign / "campaign-functions.tsv")
    residuals = _read_tsv(campaign / "campaign-residuals.tsv")
    questions = _read_tsv(campaign / "campaign-questions.tsv")
    scenarios = _read_tsv(campaign / "campaign-scenarios.tsv")
    levers = _read_tsv(campaign / "campaign-levers.tsv")
    contracts = _read_tsv(campaign / "campaign-contracts.tsv")
    adjudications = _read_tsv(campaign / "campaign-adjudications.tsv")
    supersessions = _read_tsv(campaign / "campaign-supersessions.tsv")
    contract = next(
        (row for row in contracts if row["contractId"] == overlay_row["baseContractId"]),
        None,
    )
    if contract is None or contract["entityKey"] != overlay_row["entityKey"]:
        raise CampaignError("runtime overlay base contract is absent or names another entity")
    question_by_id = {row["questionId"]: row for row in questions}
    parent_questions = []
    for question_id in addressed:
        question = question_by_id.get(question_id)
        if (
            question is None
            or question["entityKey"] != contract["entityKey"]
            or question["state"] != "OPEN"
        ):
            raise CampaignError(f"runtime adjudication cannot close question {question_id}")
        parent_questions.append(question)

    terminal_state = str(decision.get("terminalState", "")).strip()
    allowed_terminal = {
        "TERMINAL_REBUILD_READY",
        "TERMINAL_DATA",
        "TERMINAL_PADDING",
        "TERMINAL_BOUNDED_AMBIGUITY",
    }
    if terminal_state and terminal_state not in allowed_terminal:
        raise CampaignError("runtime adjudication terminalState is unsupported")
    if terminal_state and verdict != "SURVIVED":
        raise CampaignError("only a SURVIVED refuter result can terminally classify an entity")
    if terminal_state == "TERMINAL_REBUILD_READY":
        _validate_rebuild_ready_gate(
            decision,
            adjudication_path,
            overlay_row,
            overlay_ready["sha256"],
        )
    if terminal_state in {"TERMINAL_DATA", "TERMINAL_PADDING"} and contract["entityKind"] != "TEXT_RESIDUAL":
        raise CampaignError("only a text residual can terminate as DATA or PADDING")
    other_open = [
        row["questionId"]
        for row in questions
        if row["entityKey"] == contract["entityKey"]
        and row["state"] == "OPEN"
        and row["questionId"] not in set(addressed)
    ]
    if terminal_state and other_open:
        raise CampaignError("terminal adjudication leaves other entity questions open")
    next_specs = decision.get("nextQuestions", [])
    next_specs = _runtime_list(next_specs, "adjudication nextQuestions")
    if terminal_state and next_specs:
        raise CampaignError("terminal adjudication cannot also create successor questions")
    if not terminal_state and not next_specs:
        raise CampaignError("nonterminal adjudication must create a changed successor question")

    next_generation = _integer(base_receipt.get("generation"), 0) + 1
    successors = [
        _successor_question(
            _runtime_mapping(spec, "successor question"),
            entity_key=contract["entityKey"],
            parents=parent_questions,
            history=[
                row for row in questions if row["entityKey"] == contract["entityKey"]
            ],
            generation=next_generation,
            measured_at=measured_at,
        )
        for spec in next_specs
    ]
    if len({row["questionId"] for row in successors}) != len(successors):
        raise CampaignError("runtime adjudication produced duplicate successor questions")
    for question in parent_questions:
        question["state"] = f"CLOSED_{verdict}"
        question["lastOutcome"] = verdict
        question["attemptCount"] = _integer(question.get("attemptCount"), 0) + 1
        question["lastMeasurementDate"] = measured_at
    questions.extend(successors)

    remaining = str(decision.get("remainingUncertainty", "")).strip()
    if not terminal_state and not remaining:
        raise CampaignError("nonterminal adjudication must state remainingUncertainty")
    if not terminal_state:
        normalized_remaining = " ".join(remaining.split()).casefold()
        historical_remaining = {
            " ".join(row.get("remainingUncertainty", "").split()).casefold()
            for row in adjudications
            if row.get("baseContractId") == contract["contractId"]
            and row.get("remainingUncertainty", "").strip()
        }
        if normalized_remaining in historical_remaining:
            raise CampaignError(
                "runtime adjudication repeats historical remaining uncertainty without progress"
            )
    linked_ids = [value for value in contract.get("questionIds", "").split(";") if value]
    linked_ids.extend(row["questionId"] for row in successors)
    contract["questionIds"] = ";".join(dict.fromkeys(linked_ids))
    contract["lastMeasurementDate"] = measured_at[:10]
    contract["remainingUncertainty"] = remaining
    if successors:
        contract["cheapestFalsifier"] = successors[0]["cheapestFalsifier"]
    if verdict == "SURVIVED":
        prior_evidence_refs = contract.get("evidenceRefs", "")
        for field in (
            "semanticGrade", "receiver", "inputs", "returns", "writes", "sideEffects",
            "preconditions", "failureModes", "authorVerdict", "runtimeVerdict",
        ):
            contract[field] = overlay_row[field]
        for evidence_ref in overlay_row.get("evidenceRefs", "").split(";"):
            if evidence_ref:
                prior_evidence_refs = _append_state(prior_evidence_refs, evidence_ref)
        contract["evidenceRefs"] = prior_evidence_refs
        contract["refuterVerdict"] = "SURVIVED"
        contract["contractState"] = terminal_state or "BOUNDED_CONTRACT_ADVANCED"
        mapping = decision.get("rebuildMapping", {})
        mapping = _runtime_mapping(mapping, "adjudication rebuildMapping")
        for field in (
            "rebuildOwner", "rebuildImplementation", "parityTests", "rebuildState"
        ):
            if field in mapping:
                if not isinstance(mapping[field], str) or not mapping[field].strip():
                    raise CampaignError(f"adjudication rebuildMapping.{field} is empty")
                contract[field] = mapping[field].strip()
        if terminal_state == "TERMINAL_REBUILD_READY" and (
            contract["rebuildState"] != "REBUILD_READY"
            or contract["rebuildOwner"] == "UNASSIGNED"
            or contract["parityTests"] == "UNMAPPED"
        ):
            raise CampaignError("REBUILD_READY termination lacks an owner and focused parity test")
    else:
        contract["contractState"] = f"OPEN_AFTER_{verdict}"
        contract["refuterVerdict"] = verdict

    entity_row = next(
        (row for row in functions + residuals if row["entityKey"] == contract["entityKey"]),
        None,
    )
    if entity_row is None:
        raise CampaignError("runtime adjudication entity is absent from function/residual ledgers")
    entity_row["campaignState"] = terminal_state or f"OPEN_AFTER_{verdict}"
    entity_row["lastMeasurementDate"] = measured_at[:10]
    if successors:
        entity_row["lever"] = successors[0]["recommendedInstrument"]
        entity_row["cheapestFalsifier"] = successors[0]["cheapestFalsifier"]
        entity_row["requiresElevation"] = successors[0]["requiresElevation"]
    if verdict == "SURVIVED" and contract["entityKind"] == "FUNCTION":
        entity_row["semanticGrade"] = overlay_row["semanticGrade"]
        entity_row["resolutionState"] = terminal_state or "BOUNDED_CONTRACT"
        entity_row["evidenceStates"] = _append_state(
            entity_row["evidenceStates"], "RUNTIME_CONTRACT_REFUTER_SURVIVED"
        )
    if contract["entityKind"] == "TEXT_RESIDUAL":
        entity_row["questionIds"] = contract["questionIds"]

    adjudication_stamp = coverage.file_stamp(adjudication_path)
    evidence_identity = "|".join(
        f"{row['role']}:{row['sha256']}" for row in evidence_stamps
    )
    adjudication_id = "A-" + _sha256_text(
        "|".join(
            (
                base_ready["sha256"],
                overlay_ready["sha256"],
                adjudication_stamp["sha256"],
                evidence_identity,
                verdict,
            )
        )
    )[:16]
    if any(row.get("adjudicationId") == adjudication_id for row in adjudications):
        raise CampaignError("runtime adjudication was already reduced into this lineage")
    adjudications.append(
        {
            "adjudicationId": adjudication_id,
            "baseContractId": contract["contractId"],
            "entityKey": contract["entityKey"],
            "overlaySchema": RUNTIME_CONTRACT_OVERLAY_SCHEMA,
            "overlayReadySha256": overlay_ready["sha256"],
            "questionIdsAddressed": ";".join(addressed),
            "refuterVerdict": verdict,
            "refuterEvidenceSha256": ";".join(row["sha256"] for row in evidence_stamps),
            "semanticPromotionApplied": verdict == "SURVIVED",
            "terminalState": terminal_state,
            "successorQuestionIds": ";".join(row["questionId"] for row in successors),
            "remainingUncertainty": remaining,
            "measuredAtUtc": measured_at,
        }
    )

    supersession_specs = _runtime_list(
        decision.get("supersessions", []), "adjudication supersessions"
    )
    if supersession_specs:
        raise CampaignError(
            "runtime adjudication cannot create entity supersessions; use the "
            "exact evidence-bound Ghidra boundary-promotion lane"
        )

    output_rows = {
        "campaign-functions.tsv": (FUNCTION_COLUMNS, functions),
        "campaign-residuals.tsv": (RESIDUAL_COLUMNS, residuals),
        "campaign-questions.tsv": (QUESTION_COLUMNS, questions),
        "campaign-scenarios.tsv": (SCENARIO_COLUMNS, scenarios),
        "campaign-levers.tsv": (LEVER_COLUMNS, levers),
        "campaign-contracts.tsv": (CONTRACT_COLUMNS, contracts),
        "campaign-adjudications.tsv": (ADJUDICATION_COLUMNS, adjudications),
        "campaign-supersessions.tsv": (SUPERSESSION_COLUMNS, supersessions),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        for name, (columns, rows) in output_rows.items():
            _write_tsv(stage / name, columns, rows)
        reducer = _publish_reducer(stage)
        counts = {
            "functions": len(functions),
            "residuals": len(residuals),
            "questions": len(questions),
            "scenarios": len(scenarios),
            "levers": len(levers),
            "contracts": len(contracts),
            "adjudications": len(adjudications),
            "supersessions": len(supersessions),
        }
        receipt = {
            "schema": SCHEMA,
            "reducer": reducer,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "generation": next_generation,
            "parentCampaign": {
                "path": str(campaign.resolve()),
                "ready": {**base_ready, "path": "campaign.ready.json"},
            },
            "sourceSnapshot": base_receipt["sourceSnapshot"],
            "advance": {
                "kind": RUNTIME_ADVANCE_KIND,
                "schema": RUNTIME_ADVANCE_SCHEMA,
                "overlay": {
                    "root": str(overlay.resolve()),
                    "ready": {
                        **overlay_ready,
                        "path": "runtime-contracts.ready.json",
                    },
                },
                "adjudication": {
                    **adjudication_stamp,
                    "path": str(adjudication_path.resolve()),
                },
                "refuterEvidence": [
                    {
                        **stamp,
                        "path": str(evidence_paths[role.removeprefix("refuter:")].resolve()),
                    }
                    for stamp in evidence_stamps
                    for role in [str(stamp["role"])]
                ],
                "adjudicationId": adjudication_id,
                "verdict": verdict,
            },
            "counts": counts,
            "questionTypes": dict(Counter(row["questionType"] for row in questions)),
            "policies": [
                "Only explicitly addressed question IDs changed state.",
                "REFUTED and UNSCORED never promote candidate semantics.",
                "Every nonterminal decision creates a changed successor question.",
                "Terminal REBUILD_READY requires an implementation owner and focused parity test.",
            ],
            "outputs": {
                name: {**coverage.file_stamp(stage / name), "path": name}
                for name in OUTPUTS
            },
        }
        (stage / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        if _self_check:
            verify(stage)
        os.replace(stage, out)
        return receipt
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def render_next(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "No eligible open questions.\n"
    lines = []
    for index, row in enumerate(rows, 1):
        cost = "elevation" if _bool(row["requiresElevation"]) else "unattended"
        lines.extend(
            [
                f"{index}. {row['questionId']}  P{row['priority']}  {row['questionType']}  [{cost}]",
                f"   {row['question']}",
                f"   instrument: {row['recommendedInstrument']}",
                f"   falsifier: {row['cheapestFalsifier']}",
            ]
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    seed_parser = commands.add_parser("seed", help="create a READY campaign from one exact snapshot")
    seed_parser.add_argument("--snapshot", type=Path, required=True)
    seed_parser.add_argument("--out", type=Path, required=True)
    seed_parser.add_argument(
        "--carry",
        type=Path,
        help="verified prior campaign whose adjudicated progress must survive the fresh reseed",
    )

    verify_parser = commands.add_parser("verify", help="verify every campaign output against READY")
    verify_parser.add_argument("--campaign", type=Path, required=True)

    next_parser = commands.add_parser("next", help="show the highest-priority open questions")
    next_parser.add_argument("--campaign", type=Path, required=True)
    next_parser.add_argument("--top", type=int, default=10)
    next_parser.add_argument("--unattended", action="store_true")
    next_parser.add_argument("--json", action="store_true")

    export_parser = commands.add_parser(
        "export-boundaries",
        help="publish address-only Ghidra targets for observed missing native entries",
    )
    export_parser.add_argument("--campaign", type=Path, required=True)
    export_parser.add_argument("--out", type=Path, required=True)
    export_parser.add_argument("--limit", type=int, default=0)

    verify_export_parser = commands.add_parser(
        "verify-boundaries", help="verify an address-only boundary export against READY"
    )
    verify_export_parser.add_argument("--out", type=Path, required=True)

    import_candidates_parser = commands.add_parser(
        "import-native-candidates",
        help="publish unadjudicated native contract candidates from a prior proposal",
    )
    import_candidates_parser.add_argument("--campaign", type=Path, required=True)
    import_candidates_parser.add_argument("--proposal", type=Path, required=True)
    import_candidates_parser.add_argument("--evidence-doc", type=Path)
    import_candidates_parser.add_argument("--out", type=Path, required=True)

    verify_candidates_parser = commands.add_parser(
        "verify-native-candidates", help="verify a native candidate overlay against READY"
    )
    verify_candidates_parser.add_argument("--out", type=Path, required=True)

    import_runtime_parser = commands.add_parser(
        "import-runtime-contract",
        help="publish one hash-bound, refuter-gated runtime contract overlay",
    )
    import_runtime_parser.add_argument("--campaign", type=Path, required=True)
    import_runtime_parser.add_argument("--contract", type=Path, required=True)
    import_runtime_parser.add_argument("--out", type=Path, required=True)

    import_holdout_parser = commands.add_parser(
        "import-runtime-holdout",
        help="publish one preregistered question holdout behind the refuter gate",
    )
    import_holdout_parser.add_argument("--campaign", type=Path, required=True)
    import_holdout_parser.add_argument("--holdout", type=Path, required=True)
    import_holdout_parser.add_argument("--out", type=Path, required=True)

    verify_runtime_parser = commands.add_parser(
        "verify-runtime-contract", help="verify a runtime contract overlay against READY"
    )
    verify_runtime_parser.add_argument("--out", type=Path, required=True)

    advance_runtime_parser = commands.add_parser(
        "advance-runtime",
        help="reduce one parsed refuter verdict into a new immutable campaign generation",
    )
    advance_runtime_parser.add_argument("--campaign", type=Path, required=True)
    advance_runtime_parser.add_argument("--overlay", type=Path, required=True)
    advance_runtime_parser.add_argument("--adjudication", type=Path, required=True)
    advance_runtime_parser.add_argument("--out", type=Path, required=True)

    validate_ghidra_parser = commands.add_parser(
        "validate-ghidra-promotion",
        help="read-only revalidate a Ghidra promotion evidence envelope",
    )
    validate_ghidra_parser.add_argument("--evidence", type=Path, required=True)
    validate_ghidra_parser.add_argument("--campaign", type=Path)

    advance_ghidra_parser = commands.add_parser(
        "advance-ghidra-promotion",
        help="reduce a preregistered boundary-only live Ghidra promotion into a new generation",
    )
    advance_ghidra_parser.add_argument("--campaign", type=Path, required=True)
    advance_ghidra_parser.add_argument("--evidence", type=Path, required=True)
    advance_ghidra_parser.add_argument("--out", type=Path, required=True)

    advance_semantic_parser = commands.add_parser(
        "advance-ghidra-semantic-promotion",
        help=(
            "reduce one proof-bound, same-range live Ghidra semantic promotion "
            "into a new generation"
        ),
    )
    advance_semantic_parser.add_argument("--campaign", type=Path, required=True)
    advance_semantic_parser.add_argument("--live-ready", type=Path, required=True)
    advance_semantic_parser.add_argument("--out", type=Path, required=True)

    advance_residual_parser = commands.add_parser(
        "advance-ghidra-residual-promotion",
        help=(
            "reduce the exact 515 residual-to-function live boundary lineage "
            "into a post-reseed generation"
        ),
    )
    advance_residual_parser.add_argument("--campaign", type=Path, required=True)
    advance_residual_parser.add_argument("--evidence", type=Path, required=True)
    advance_residual_parser.add_argument("--lineage", type=Path, required=True)
    advance_residual_parser.add_argument("--out", type=Path, required=True)

    advance_partition_parser = commands.add_parser(
        "advance-ghidra-residual-partition",
        help=(
            "reduce the exact Atomic14 residual-to-functions-and-padding live lineage "
            "into a post-reseed generation"
        ),
    )
    advance_partition_parser.add_argument("--campaign", type=Path, required=True)
    advance_partition_parser.add_argument("--snapshot", type=Path, required=True)
    advance_partition_parser.add_argument("--live-ready", type=Path, required=True)
    advance_partition_parser.add_argument("--formal-ready", type=Path, required=True)
    advance_partition_parser.add_argument("--targets", type=Path, required=True)
    advance_partition_parser.add_argument("--padding", type=Path, required=True)
    advance_partition_parser.add_argument("--parity-export", type=Path, required=True)
    advance_partition_parser.add_argument("--out", type=Path, required=True)

    advance_ttd_parser = commands.add_parser(
        "advance-ttd-call-context-observation",
        help=(
            "admit the exact replicated Level 521 schema-v3 call-context "
            "observation as a bounded campaign generation"
        ),
    )
    advance_ttd_parser.add_argument("--campaign", type=Path, required=True)
    advance_ttd_parser.add_argument("--evidence", type=Path, required=True)
    advance_ttd_parser.add_argument("--out", type=Path, required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "seed":
            receipt = seed(args.snapshot, args.out, carry=args.carry)
            print(
                f"CAMPAIGN_READY functions={receipt['counts']['functions']} "
                f"residuals={receipt['counts']['residuals']} "
                f"questions={receipt['counts']['questions']} "
                f"scenarios={receipt['counts']['scenarios']} "
                f"levers={receipt['counts']['levers']} "
                f"contracts={receipt['counts']['contracts']} out={args.out}"
            )
            return 0
        if args.command == "verify":
            receipt = verify(args.campaign)
            print(f"CAMPAIGN_VERIFIED {receipt['counts']} {args.campaign}")
            return 0
        if args.command == "export-boundaries":
            receipt = export_observed_boundaries(args.campaign, args.out, args.limit)
            print(f"BOUNDARY_TARGETS_READY count={receipt['count']} out={args.out}")
            return 0
        if args.command == "verify-boundaries":
            receipt = verify_boundary_export(args.out)
            print(f"BOUNDARY_TARGETS_VERIFIED count={receipt['count']} out={args.out}")
            return 0
        if args.command == "import-native-candidates":
            receipt = import_native_contract_candidates(
                args.campaign, args.proposal, args.out, args.evidence_doc
            )
            print(f"CONTRACT_CANDIDATES_READY count={receipt['count']} out={args.out}")
            return 0
        if args.command == "verify-native-candidates":
            receipt = verify_native_contract_candidates(args.out)
            print(f"CONTRACT_CANDIDATES_VERIFIED count={receipt['count']} out={args.out}")
            return 0
        if args.command == "import-runtime-contract":
            receipt = import_runtime_contract(args.campaign, args.contract, args.out)
            print(f"RUNTIME_CONTRACT_READY count={receipt['count']} out={args.out}")
            return 0
        if args.command == "import-runtime-holdout":
            receipt = import_runtime_holdout(args.campaign, args.holdout, args.out)
            print(f"RUNTIME_HOLDOUT_READY count={receipt['count']} out={args.out}")
            return 0
        if args.command == "verify-runtime-contract":
            receipt = verify_runtime_contract_overlay(args.out)
            print(f"RUNTIME_CONTRACT_VERIFIED count={receipt['count']} out={args.out}")
            return 0
        if args.command == "advance-runtime":
            receipt = advance_runtime_contract(
                args.campaign, args.overlay, args.adjudication, args.out
            )
            print(
                f"CAMPAIGN_ADVANCED generation={receipt['generation']} "
                f"verdict={receipt['advance']['verdict']} out={args.out}"
            )
            return 0
        if args.command == "validate-ghidra-promotion":
            validated = validate_ghidra_promotion_evidence(args.evidence, args.campaign)
            print(
                f"GHIDRA_PROMOTION_VERIFIED count={len(validated['addresses'])} "
                f"schema={validated['evidenceSchema']} "
                f"legacyBridge={str(validated['legacyBridgeUsed']).lower()} "
                f"evidence={args.evidence}"
            )
            return 0
        if args.command == "advance-ghidra-promotion":
            receipt = advance_ghidra_promotion(
                args.campaign, args.evidence, args.out
            )
            print(
                f"CAMPAIGN_GHIDRA_PROMOTED generation={receipt['generation']} "
                f"count={receipt['advance']['count']} out={args.out}"
            )
            return 0
        if args.command == "advance-ghidra-semantic-promotion":
            receipt = advance_ghidra_semantic_promotion(
                args.campaign, args.live_ready, args.out
            )
            print(
                f"CAMPAIGN_GHIDRA_SEMANTIC_PROMOTED generation={receipt['generation']} "
                f"count={receipt['advance']['count']} out={args.out}"
            )
            return 0
        if args.command == "advance-ghidra-residual-promotion":
            receipt = advance_ghidra_residual_promotion(
                args.campaign, args.evidence, args.lineage, args.out
            )
            print(
                f"CAMPAIGN_GHIDRA_RESIDUAL_PROMOTED generation={receipt['generation']} "
                f"count={receipt['advance']['count']} out={args.out}"
            )
            return 0
        if args.command == "advance-ghidra-residual-partition":
            receipt = advance_ghidra_residual_partition(
                args.campaign,
                args.snapshot,
                args.live_ready,
                args.formal_ready,
                args.targets,
                args.padding,
                args.parity_export,
                args.out,
            )
            print(
                f"CAMPAIGN_GHIDRA_PARTITION_PROMOTED generation={receipt['generation']} "
                f"functions={receipt['advance']['partition']['functionCount']} "
                f"padding={receipt['advance']['partition']['paddingCount']} out={args.out}"
            )
            return 0
        if args.command == "advance-ttd-call-context-observation":
            receipt = advance_ttd_call_context_observation(
                args.campaign, args.evidence, args.out
            )
            print(
                f"CAMPAIGN_TTD_CALL_CONTEXT_ADVANCED generation={receipt['generation']} "
                f"contracts={receipt['advance']['questionsClosed']} "
                f"out={args.out}"
            )
            return 0
        rows = next_questions(args.campaign, args.top, args.unattended)
        print(json.dumps(rows, indent=2) if args.json else render_next(rows))
        return 0
    except CampaignError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
