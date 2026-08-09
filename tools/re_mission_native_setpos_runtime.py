#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prove one bounded Mission-native SetPos runtime contract.

The owner validates two independently staged treatment runs, a matched no-call
control, a logger-disabled control, and an untouched-stock control.  Every game
launch is against a disposable copy.  The proof is intentionally narrower than
an internal write-set claim: it establishes the script-visible position passed
to SetPos and the immediately observed GetPos result for two named Level 100
objects.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "bea.re.mission-native-setpos-runtime-proof.v1"
CLAIM = "MISSION_NATIVE_SETPOS_COPIES_POSITION_AND_IMMEDIATE_GETPOS_MATCHES"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
SAFE_RUNTIME_SHA256 = "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
LOGGER_GATE1_SHA256 = "2f52b34341929c71f68d73159ca8cabd8eeb50321c79fec45e155b6f1f8ca0c2"
LOGGER_GATE0_SHA256 = "baf506d305d5438bae9213babfdcdcae7e66f611372b076c9244787c074cbdec"
STOCK_ARCHIVE_SHA256 = "ed6350c0e214d00ab1bf6a7bd137fba3e77d0afe19a6dc4c0607f56ac037496a"
TREATMENT_ARCHIVE_SHA256 = "201c807d800e2f422f55dbf82cddecb148cf6166d84cd447a9be69d5b2259a7d"
CONTROL_ARCHIVE_SHA256 = "bf474a8b06a5699b0994bc5ddfec909470c6f7d0828a178f71b13d32bf73bb4a"

ENTITY_KEY = (
    "CODE:" + SPECIMEN_SHA256
    + ":VA=0x00536c70:RANGES=679f653081c42099a6f086e0ff7e656596f1e5ca8588272c1bb35db45c7780fa"
)
CONTRACT_ID = "C-aca39413b2419b80"
OPEN_QUESTION_ID = "Q-b9d7aa552ce48a32"

EVIDENCE_RELATIVE = Path("local-lab/mission-native-setpos-runtime-20260809-v1")
READY_NAME = "runtime-proof.ready.json"

SOURCE_POSITION = "x = 239.5000, y = 266.5000, z = -11.0291"
TARGET_BEFORE = "x = 271.3750, y = 240.0000, z = -9.6310"

TREATMENT_SEGMENT = [
    "CODEX_SETPOS_BEGIN_20260809",
    "CODEX_SETPOS_SOURCE",
    SOURCE_POSITION,
    "CODEX_SETPOS_TARGET_BEFORE",
    TARGET_BEFORE,
    "CODEX_SETPOS_TARGET_AFTER",
    SOURCE_POSITION,
    "CODEX_SETPOS_DONE_20260809",
]
CONTROL_SEGMENT = [
    "CODEX_SETPOS_CONTROL_BEGIN_20260809",
    "CODEX_SETPOS_CONTROL_SOURCE",
    SOURCE_POSITION,
    "CODEX_SETPOS_CONTROL_TARGET_BEFORE",
    TARGET_BEFORE,
    "CODEX_SETPOS_CONTROL_TARGET_AFTER",
    TARGET_BEFORE,
    "CODEX_SETPOS_CONTROL_DONE_20260809",
]
ALL_NONCES = tuple(line for line in TREATMENT_SEGMENT + CONTROL_SEGMENT if line.startswith("CODEX_"))

EVIDENCE_PINS: dict[str, tuple[int, str]] = {
    "PREREGISTRATION.md": (2_546, "b9f61b87faca33a8c7ee962f1df71e6506bf721cc5f919867ad1003116c063e7"),
    "treatment.recipe.json": (1_581, "323ed08c122e81f451c78ab129c95fe2eb7ab1c2eb31bdeef2cf15d9af94daad"),
    "no-call-control.recipe.json": (1_502, "e35003fe72e46097ce22131b0ca8bab179b654358fa1bcdea20916edcb2808fb"),
    "setpos-runtime-probes.json": (6_513, "e71614c106790b38a5d1e32aa1e528bdaf2fcc2098546495d0ec2da6aa89bf39"),
    "payload/level100-setpos-treatment.aya": (1_323_681, TREATMENT_ARCHIVE_SHA256),
    "payload/level100-setpos-treatment.manifest.json": (18_328, "e533ee2ca521769ac09ece8079bcf1d5b5b431769eab8c9c4393b1d2f9b46f0b"),
    "payload/level100-setpos-no-call-control.aya": (1_323_679, CONTROL_ARCHIVE_SHA256),
    "payload/level100-setpos-no-call-control.manifest.json": (17_938, "1c8cde35783927e9b14a8d385d011f5d8c0f7b7244e657de09986992a67713d5"),
    "run-receipts/mission-setpos-treatment-r1-20260809-072757/receipt.json": (6_134, "f3d498b09ae2314736e4b0df94ebaf1d91805157c1f27928a9c2825ca0fa6d1a"),
    "run-receipts/mission-setpos-treatment-r1-20260809-072757/artefacts/probe.log": (954, "4c078af78c2eb1dff53f968f3b87810c32ba74e1f9281c6323e523634b0756a8"),
    "run-receipts/mission-setpos-treatment-r2-20260809-072837/receipt.json": (6_118, "0cbd2c8878e6d10f62eed8bf51e17f3c5707923f390154aa37ca2efac555aa70"),
    "run-receipts/mission-setpos-treatment-r2-20260809-072837/artefacts/probe.log": (954, "4c078af78c2eb1dff53f968f3b87810c32ba74e1f9281c6323e523634b0756a8"),
    "run-receipts/mission-setpos-no-call-control-20260809-072915/receipt.json": (6_182, "0e0bf4807810f231618a04417868f59c22440671d75f6cc2b1feb683b0f654b1"),
    "run-receipts/mission-setpos-no-call-control-20260809-072915/artefacts/probe.log": (993, "74d5b1c89ad89f22e2707b5b68df8ad007f92a9ef2e1c55cb89cf0c3532b6b94"),
    "run-receipts/mission-setpos-stock-control-20260809-072954/receipt.json": (6_077, "5a800d87d3c3ab01f51e3ca99c9a57d6c77520ffd22f752263e6ebc267078e43"),
    "run-receipts/mission-setpos-stock-control-20260809-072954/artefacts/probe.log": (696, "ef48defca8fff0e146eedf503d7e819a1932cde92b5c697fd8645052b88891d6"),
    "run-receipts/mission-setpos-gate0-control-20260809-073059/receipt.json": (5_611, "648b0ac53ffc64b5d0c53b84ba0f89a4518cb4bd57da865270bb8b5a78679222"),
}

UPSTREAM_PINS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2_506_752, SPECIMEN_SHA256),
    "local-lab/safe-copy-bea-pristine/BEA.exe": (2_506_752, SAFE_RUNTIME_SHA256),
    "local-lab/safe-copy-bea-pristine/data/Resources/100_res_PC.aya": (1_329_806, STOCK_ARCHIVE_SHA256),
    "local-lab/logger-oracle-pilot-2026-08-02/payloads/logger-gate1-positive.exe": (2_506_752, LOGGER_GATE1_SHA256),
    "local-lab/logger-oracle-pilot-2026-08-02/payloads/logger-gate0-control.exe": (2_506_752, LOGGER_GATE0_SHA256),
    "local-lab/logger-oracle-pilot-2026-08-02/logger-oracle.ready.json": (20_536, "b4ae49e3344ec96b72248a657af8daa7627b79f865d6f6287a369daeeb14a1a6"),
    "local-lab/logger-thing-identity-pilot-2026-08-03/logger-thing-identity.ready.json": (17_281, "b8c2cad42b30bd6d215b6637aa82e5eb4489646832c1ce6051c56c041d8c03f3"),
    "local-lab/scenario-primitives-2026-08-02/native_table.json": (44_291, "ca4c0f64efe86f7a48c0469988d6ae67d17dfc132358b9096d28f47cb894f61e"),
    "local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv": (9_016, "42027af22e1d4a0611bf7286fd1ea0df17adf01f7bf54ad5a2196f8484f40d86"),
    "local-lab/mission-native-setpos-boundary-reproof-20260809-v1/proof.ready.json": (12_100, "7fca2c1e960166603ece107c112217ea674e6c2d898622594432817a803a0a7d"),
    "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1/promotion/promotion.ready.json": (6_782, "e64be82f360203fd2864450c5b3bd2d0a46441b9120eb79c8c423c3fe1ca0340"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/generation-15-mission-native-setpos-reproof-v2/campaign.ready.json": (23_623, "629b32daf62f7c85e4819a024e0ade705be5548960d81cc320b636afa53e58a7"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/generation-15-mission-native-setpos-reproof-authority.ready.json": (9_769, "9fc1bf4eadd3ba654b80397c540515dba47022ce5905215851737673dc977ceb"),
}

TOOL_PINS: dict[str, tuple[int, str]] = {
    "tools/probe/probe_author.py": (81_470, "4bd5046a280fa94bde46982e4b1bc8de3d3079875ddad50a1a668f550caa44fe"),
    "tools/probe/mission_script_emitter.py": (18_644, "9866a1e007c6da08af57b19c568ac36f0f9314d4da64c52d035c6cf07af6d964"),
    "tools/probe/probe_harness.py": (74_586, "4709a790995f7ca69fe0bce9477b4b1ef4917bf9ebdd3eb343fc505c416a05c6"),
}

RUNS = {
    "treatmentA": {
        "name": "mission-setpos-treatment-r1",
        "dir": "mission-setpos-treatment-r1-20260809-072757",
        "payload": "payload/level100-setpos-treatment.aya",
        "payloadSha256": TREATMENT_ARCHIVE_SHA256,
        "loggerSha256": LOGGER_GATE1_SHA256,
        "verdict": "PASS",
        "oracleOutcome": "satisfied",
    },
    "treatmentB": {
        "name": "mission-setpos-treatment-r2",
        "dir": "mission-setpos-treatment-r2-20260809-072837",
        "payload": "payload/level100-setpos-treatment.aya",
        "payloadSha256": TREATMENT_ARCHIVE_SHA256,
        "loggerSha256": LOGGER_GATE1_SHA256,
        "verdict": "PASS",
        "oracleOutcome": "satisfied",
    },
    "noCallControl": {
        "name": "mission-setpos-no-call-control",
        "dir": "mission-setpos-no-call-control-20260809-072915",
        "payload": "payload/level100-setpos-no-call-control.aya",
        "payloadSha256": CONTROL_ARCHIVE_SHA256,
        "loggerSha256": LOGGER_GATE1_SHA256,
        "verdict": "PASS",
        "oracleOutcome": "satisfied",
    },
    "stockControl": {
        "name": "mission-setpos-stock-control",
        "dir": "mission-setpos-stock-control-20260809-072954",
        "payload": "../safe-copy-bea-pristine/data/Resources/100_res_PC.aya",
        "payloadSha256": STOCK_ARCHIVE_SHA256,
        "loggerSha256": LOGGER_GATE1_SHA256,
        "verdict": "PASS",
        "oracleOutcome": "satisfied",
    },
    "loggerDisabled": {
        "name": "mission-setpos-gate0-control",
        "dir": "mission-setpos-gate0-control-20260809-073059",
        "payload": "payload/level100-setpos-treatment.aya",
        "payloadSha256": TREATMENT_ARCHIVE_SHA256,
        "loggerSha256": LOGGER_GATE0_SHA256,
        "verdict": "FAIL",
        "oracleOutcome": "unsatisfied-timeout",
    },
}

RECEIPT_KEYS = {
    "probe", "startedUtc", "dryRun", "runDirectory", "scratchRoot",
    "workingDirectory", "command", "oracle", "status", "verdict", "failure",
    "sourceWitness", "staleAutoexecScan", "staging", "diagnosis", "artefacts",
    "exitClassification", "faultGate", "teardown", "wallSeconds", "finishedUtc",
}
VECTOR_RE = re.compile(r"^x = -?\d+\.\d{4}, y = -?\d+\.\d{4}, z = -?\d+\.\d{4}$")


class ProofError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ProofError(message)


def repo_root() -> Path:
    configured = os.environ.get("BEA_REPO_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path, root: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path}")
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        relative = str(path.resolve())
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"cannot parse {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def parse_utc(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} is not UTC text")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ProofError(f"{label} is not an ISO timestamp") from exc
    require(parsed.tzinfo is not None, f"{label} has no timezone")
    return parsed


def exact_map(root: Path, base: Path, pins: dict[str, tuple[int, str]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for relative, expected in sorted(pins.items()):
        actual = stamp(base / relative, root)
        require((actual["bytes"], actual["sha256"]) == expected, f"identity differs: {relative}")
        result[relative] = actual
    return result


def validate_program_manifest(root: Path, evidence: Path, *, control: bool) -> dict[str, Any]:
    stem = "level100-setpos-no-call-control" if control else "level100-setpos-treatment"
    manifest = read_json(evidence / "payload" / f"{stem}.manifest.json")
    recipe = read_json(evidence / ("no-call-control.recipe.json" if control else "treatment.recipe.json"))
    require(manifest.get("specimen_sha256") == SPECIMEN_SHA256, "program specimen differs")
    require(manifest.get("arm") == "probe" and manifest.get("label") == stem, "program label differs")
    require(manifest.get("intents") == recipe.get("intents"), "program recipe differs from manifest")
    require(manifest.get("source", {}).get("sha256") == STOCK_ARCHIVE_SHA256, "program source archive differs")
    expected_output = CONTROL_ARCHIVE_SHA256 if control else TREATMENT_ARCHIVE_SHA256
    require(manifest.get("output", {}).get("sha256") == expected_output, "program output archive differs")
    require(manifest.get("world", {}).get("script_count_before") == 25, "program source script count differs")
    require(manifest.get("world", {}).get("script_count_after") == 25, "program output script count differs")
    splice = manifest.get("splice")
    require(isinstance(splice, dict) and splice.get("kind") == "replace-script", "program is not a replacement")
    require(splice.get("script") == "Setup" and splice.get("scriptOrdinal") == 9, "program replaced the wrong script")
    emitter = splice.get("emitter")
    require(isinstance(emitter, dict), "program emitter metadata missing")
    require(emitter.get("schema") == "bea.missionscript.straight-line-program.v1", "emitter schema differs")
    require(emitter.get("nativeTable", {}).get("sha256") == "ca4c0f64efe86f7a48c0469988d6ae67d17dfc132358b9096d28f47cb894f61e", "native table differs")
    calls = emitter.get("nativeCalls")
    require(isinstance(calls, list), "native call list missing")
    expected_names = (
        ["Print", "GetThingRef", "GetThingRef", "GetPos", "GetPos", "Print", "Print", "Print", "Print", "GetPos", "Print", "Print", "Print"]
        if control else
        ["Print", "GetThingRef", "GetThingRef", "GetPos", "GetPos", "Print", "Print", "Print", "Print", "SetPos", "GetPos", "Print", "Print", "Print"]
    )
    require([call.get("native") for call in calls] == expected_names, "native call sequence differs")
    setpos = [call for call in calls if call.get("native") == "SetPos"]
    require(len(setpos) == (0 if control else 1), "SetPos call count differs")
    if setpos:
        require(setpos[0] == {"statement": 10, "native": "SetPos", "nativeIndex": 135, "argc": 1, "returns": False, "target": "target"}, "SetPos call binding differs")
    verification = manifest.get("verification", {})
    for key in (
        "source_parsed", "output_parsed", "chunk_chain_closes",
        "roundtrip_inflated_identical", "replacementScriptOrderPreserved",
        "replacementTargetOrdinalPreserved", "replacementRecordReadbackExact",
        "tail_identical", "head_ranges_within_edits",
    ):
        require(verification.get(key) is True, f"program verification failed: {key}")
    require(verification.get("replacementNonTargetRecordsIdentical") == 24, "non-target script count differs")
    require(bool(manifest.get("unproven")), "runtime limitation was removed from authored manifest")
    return {
        "manifest": stamp(evidence / "payload" / f"{stem}.manifest.json", root),
        "archive": stamp(evidence / "payload" / f"{stem}.aya", root),
        "programSha256": emitter["programSha256"],
        "recordSha256": emitter["recordSha256"],
        "instructionCount": emitter["instructionCount"],
        "nativeCalls": calls,
        "setPosCalls": len(setpos),
        "nonTargetRecordsIdentical": 24,
    }


def expected_probe_map(evidence: Path) -> dict[str, dict[str, Any]]:
    value = read_json(evidence / "setpos-runtime-probes.json")
    probes = value.get("probes")
    require(isinstance(probes, list) and len(probes) == 5, "probe manifest shape differs")
    result = {probe.get("name"): probe for probe in probes if isinstance(probe, dict)}
    require(set(result) == {run["name"] for run in RUNS.values()}, "probe manifest names differ")
    return result


def validate_receipt_data(
    receipt: dict[str, Any], *, lane: str, run: dict[str, str], configured: dict[str, Any],
    root: Path, evidence: Path,
) -> dict[str, Any]:
    require(set(receipt) == RECEIPT_KEYS, f"{lane} receipt shape differs")
    require(receipt.get("dryRun") is False and receipt.get("status") == "complete", f"{lane} was not a live completed run")
    require(receipt.get("verdict") == run["verdict"], f"{lane} verdict differs")
    require(receipt.get("failure") is None, f"{lane} records a harness failure")
    probe = receipt.get("probe")
    require(isinstance(probe, dict), f"{lane} probe metadata missing")
    require(probe.get("name") == run["name"] and probe.get("level") == 100, f"{lane} probe identity differs")
    require(probe.get("oracle") == configured.get("oracle"), f"{lane} oracle differs from preregistration")
    require(probe.get("note") == configured.get("note") and probe.get("record") is False, f"{lane} probe scope differs")
    safe_root = (root / "local-lab/safe-copy-bea-pristine").resolve()
    require(Path(probe.get("sourceRoot", "")).resolve() == safe_root, f"{lane} source root differs")

    start = parse_utc(receipt.get("startedUtc"), f"{lane}.startedUtc")
    finish = parse_utc(receipt.get("finishedUtc"), f"{lane}.finishedUtc")
    require(start < finish, f"{lane} chronology differs")
    require(30.0 <= float(receipt.get("wallSeconds", 0)) < 120.0, f"{lane} wall time differs")
    expected_run_dir = (EVIDENCE_RELATIVE / "run-receipts" / run["dir"]).as_posix()
    actual_run_dir = str(receipt.get("runDirectory", "")).replace("\\", "/")
    require(actual_run_dir == expected_run_dir, f"{lane} run directory differs")
    expected_scratch = (EVIDENCE_RELATIVE / "run-scratch" / run["dir"]).as_posix()
    actual_scratch = str(receipt.get("scratchRoot", "")).replace("\\", "/")
    require(actual_scratch == expected_scratch, f"{lane} scratch directory differs")
    require(str(receipt.get("workingDirectory", "")).replace("\\", "/") == expected_scratch, f"{lane} working directory differs")
    expected_command = f"'{str(Path(expected_scratch) / 'BEA.exe').replace('/', os.sep)}' -skipfmv -forcewindowed -level 100"
    require(receipt.get("command") == expected_command, f"{lane} command differs")

    require(receipt.get("sourceWitness") == {
        "BEA.exe": SAFE_RUNTIME_SHA256,
        "BEA.exe.original.backup": SPECIMEN_SHA256,
    }, f"{lane} protected source witnesses differ")
    require(receipt.get("staleAutoexecScan") == [], f"{lane} had a stale autoexec")
    staging = receipt.get("staging")
    require(isinstance(staging, dict), f"{lane} staging metadata missing")
    require(Path(staging.get("sourceRoot", "")).resolve() == safe_root, f"{lane} staged source differs")
    require(str(staging.get("scratchRoot", "")).replace("\\", "/") == expected_scratch, f"{lane} staged scratch differs")
    require(staging.get("executableSha256") == run["loggerSha256"], f"{lane} logger executable differs")
    require(staging.get("autoexec") is None and staging.get("removedInheritedOutputs") == [], f"{lane} staging contamination differs")
    staged = staging.get("stagedFiles")
    require(isinstance(staged, list) and len(staged) == 2, f"{lane} staged-file count differs")
    by_dest = {item.get("dest"): item for item in staged}
    require(set(by_dest) == {"BEA.exe", "data/Resources/100_res_PC.aya"}, f"{lane} staged destinations differ")
    exe = by_dest["BEA.exe"]
    archive = by_dest["data/Resources/100_res_PC.aya"]
    require(exe.get("sha256") == run["loggerSha256"] and exe.get("replacedSha256") == SAFE_RUNTIME_SHA256 and exe.get("bytes") == 2_506_752, f"{lane} staged executable binding differs")
    require(archive.get("sha256") == run["payloadSha256"] and archive.get("replacedSha256") == STOCK_ARCHIVE_SHA256, f"{lane} staged archive binding differs")
    require(archive.get("bytes") in {1_323_681, 1_323_679, 1_329_806}, f"{lane} staged archive size differs")

    oracle = receipt.get("oracle")
    require(isinstance(oracle, dict), f"{lane} oracle result missing")
    require(oracle.get("outcome") == run["oracleOutcome"], f"{lane} oracle outcome differs")
    require(oracle.get("processAliveAtDecision") is True and oracle.get("exitCode") is None, f"{lane} did not survive to decision")
    require(30.0 <= float(oracle.get("elapsedSeconds", 0)) < 35.0, f"{lane} oracle duration differs")
    diagnosis = receipt.get("diagnosis")
    require(isinstance(diagnosis, dict) and diagnosis.get("levelLoadLogged") is True, f"{lane} did not load Level 100")
    require(diagnosis.get("levelLoadMarker") == "Game::LoadLevel 100", f"{lane} level marker differs")
    require(diagnosis.get("fatalFaultLogPresent") is False, f"{lane} faulted")
    require(receipt.get("exitClassification", {}).get("isFault") is False, f"{lane} exit classified as fault")
    require(receipt.get("faultGate", {}).get("triggered") is False, f"{lane} fault gate triggered")
    require(receipt.get("teardown") == {
        "removedAutoexec": False,
        "removedScratch": True,
        "keptScratch": False,
        "verified": True,
        "errors": [],
    }, f"{lane} teardown differs")

    artefacts = receipt.get("artefacts")
    require(isinstance(artefacts, dict), f"{lane} artefacts missing")
    collected = artefacts.get("collected")
    require(isinstance(collected, list), f"{lane} collected artefacts malformed")
    current: dict[str, dict[str, Any]] = {}
    for item in collected:
        path = root / str(item.get("path", ""))
        actual = stamp(path, root)
        require(actual["bytes"] == item.get("bytes") and actual["sha256"] == item.get("sha256"), f"{lane} collected artefact differs: {item.get('from')}")
        require(actual["path"] == str(item.get("path", "")).replace("\\", "/"), f"{lane} collected path differs")
        current[str(item.get("from"))] = actual
    require("setuphistory.txt" in current, f"{lane} setup history missing")
    setup = (root / current["setuphistory.txt"]["path"]).read_text(encoding="utf-8", errors="replace")
    require("Game::LoadLevel 100" in setup, f"{lane} setup history lacks Level 100")
    if lane == "loggerDisabled":
        require(set(current) == {"setuphistory.txt"}, "logger-disabled arm collected an unexpected file")
        require(artefacts.get("missing") == ["probe.log", "OnslaughtException.txt"], "logger-disabled missing set differs")
        require("probe.log does not exist" in str(oracle.get("detail")), "logger-disabled absence was not decisive")
    else:
        require(set(current) == {"probe.log", "setuphistory.txt"}, f"{lane} collected set differs")
        require(artefacts.get("missing") == ["OnslaughtException.txt"], f"{lane} missing set differs")
    return {
        "receipt": stamp(evidence / "run-receipts" / run["dir"] / "receipt.json", root),
        "startedUtc": receipt["startedUtc"],
        "finishedUtc": receipt["finishedUtc"],
        "verdict": receipt["verdict"],
        "oracleOutcome": oracle["outcome"],
        "levelLoadLogged": True,
        "faulted": False,
        "processAliveAtDecision": True,
        "artefacts": current,
    }


def extract_segment(lines: list[str], expected: list[str], label: str) -> list[str]:
    for marker in (expected[0], expected[-1]):
        require(lines.count(marker) == 1, f"{label} marker count differs: {marker}")
    start = lines.index(expected[0])
    end = lines.index(expected[-1])
    require(start < end, f"{label} marker order differs")
    segment = lines[start:end + 1]
    require(segment == expected, f"{label} marker/value sequence differs")
    for value in (segment[2], segment[4], segment[6]):
        require(VECTOR_RE.fullmatch(value) is not None, f"{label} vector format differs")
    return segment


def validate_relations(root: Path, runs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    def log_lines(lane: str) -> list[str]:
        path = runs[lane]["artefacts"].get("probe.log")
        require(isinstance(path, dict), f"{lane} probe log missing")
        return (root / path["path"]).read_text(encoding="utf-8", errors="strict").splitlines()

    treatment_a = extract_segment(log_lines("treatmentA"), TREATMENT_SEGMENT, "treatmentA")
    treatment_b = extract_segment(log_lines("treatmentB"), TREATMENT_SEGMENT, "treatmentB")
    control = extract_segment(log_lines("noCallControl"), CONTROL_SEGMENT, "noCallControl")
    require(treatment_a == treatment_b, "treatment replications differ")
    require(treatment_a[2] != treatment_a[4], "treatment source already equals target before")
    require(treatment_a[6] == treatment_a[2], "treatment target after does not equal source")
    require(control[2] == treatment_a[2] and control[4] == treatment_a[4], "control baseline differs")
    require(control[6] == control[4], "no-call control target changed")
    require(control[6] != control[2], "no-call control source and target are not discriminating")
    stock = log_lines("stockControl")
    require(all(nonce not in stock for nonce in ALL_NONCES), "stock control contains an experiment nonce")
    return {
        "treatmentReplications": 2,
        "treatmentMarkerValueSequenceByteIdentical": True,
        "sourcePosition": SOURCE_POSITION,
        "targetPositionBefore": TARGET_BEFORE,
        "targetPositionAfter": SOURCE_POSITION,
        "sourceAndTargetInitiallyDifferent": True,
        "immediateTargetReadbackEqualsSuppliedSourcePosition": True,
        "noCallControlTargetBefore": TARGET_BEFORE,
        "noCallControlTargetAfter": TARGET_BEFORE,
        "noCallControlUnchanged": True,
        "loggerDisabledLogAbsent": True,
        "stockNoncesAbsent": True,
    }


def derive(root: Path, generated_at: str) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    evidence = root / EVIDENCE_RELATIVE
    inputs = exact_map(root, evidence, EVIDENCE_PINS)
    upstream = exact_map(root, root, UPSTREAM_PINS)
    tools = exact_map(root, root, TOOL_PINS)
    tools["tools/re_mission_native_setpos_runtime.py"] = stamp(Path(__file__).resolve(), root)
    programs = {
        "treatment": validate_program_manifest(root, evidence, control=False),
        "noCallControl": validate_program_manifest(root, evidence, control=True),
    }
    configured = expected_probe_map(evidence)
    runs: dict[str, dict[str, Any]] = {}
    for lane, run in RUNS.items():
        receipt_path = evidence / "run-receipts" / run["dir"] / "receipt.json"
        runs[lane] = validate_receipt_data(
            read_json(receipt_path), lane=lane, run=run,
            configured=configured[run["name"]], root=root, evidence=evidence,
        )
    relations = validate_relations(root, runs)
    return {
        "schema": SCHEMA,
        "verdict": "READY",
        "claim": CLAIM,
        "generatedAtUtc": generated_at,
        "specimenSha256": SPECIMEN_SHA256,
        "entity": {
            "entityKey": ENTITY_KEY,
            "entryVa": "0x00536c70",
            "shippedNativeName": "SetPos",
            "contractId": CONTRACT_ID,
            "questionAddressed": OPEN_QUESTION_ID,
        },
        "inputs": inputs,
        "upstream": upstream,
        "tools": tools,
        "programs": programs,
        "runs": runs,
        "relations": relations,
        "result": {
            "evidenceGrade": "C2_BOUNDED_RUNTIME",
            "scopeKind": "FORCED_SCRIPT_SAFE_COPY",
            "level": 100,
            "script": "Setup",
            "receiver": "Turret 02",
            "argumentSource": "Turret 01.GetPos()",
            "inputs": "one runtime CPositionDataType rendered as " + SOURCE_POSITION,
            "returns": "void at Mission descriptor boundary; no return value observed",
            "writes": "target script-visible position changes from " + TARGET_BEFORE + " to " + SOURCE_POSITION,
            "ordering": "GetPos(source); GetPos(target-before); SetPos(source-position); immediate GetPos(target-after)",
            "replications": 2,
            "controls": 3,
            "contractDisposition": "ADMIT_BOUNDED_RUNTIME_PATH_KEEP_BROADER_BEHAVIOR_OPEN",
        },
        "limitations": [
            "This is a forced generated Level 100 Setup path on disposable copied runtimes, not a naturally shipped SetPos call.",
            "Only Turret 02 receiving Turret 01's finite position was measured; other receivers and values remain open.",
            "The logger renders position components to four decimal places and does not preserve arbitrary float bit patterns.",
            "Immediate script-visible GetPos equality does not enumerate internal memory writes, orientation, collision, physics, navigation, or later persistence.",
            "The one-byte logger gate and force-windowed bytes are lab instrumentation and do not describe unmodified retail defaults.",
            "No TTD trace, live Ghidra mutation, installed-game write, or rebuild parity claim is part of this runtime proof.",
        ],
    }


def validate_saved(saved: dict[str, Any], root: Path) -> None:
    require(saved.get("schema") == SCHEMA and saved.get("verdict") == "READY", "saved proof identity differs")
    require(saved.get("claim") == CLAIM, "saved proof claim differs")
    fresh = derive(root, saved.get("generatedAtUtc"))
    require(saved == fresh, "saved proof differs from fresh derivation")


def expect_refusal(label: str, fn, contains: str) -> None:
    try:
        fn()
    except ProofError as exc:
        require(contains in str(exc), f"{label} hit the wrong gate: {exc}")
        return
    raise ProofError(f"{label} counterexample was accepted")


def selftest(root: Path) -> None:
    evidence = root / EVIDENCE_RELATIVE
    probes = expected_probe_map(evidence)
    run = RUNS["treatmentA"]
    receipt = read_json(evidence / "run-receipts" / run["dir"] / "receipt.json")
    forged = copy.deepcopy(receipt)
    forged["verdict"] = "FAIL"
    expect_refusal(
        "receipt verdict forgery",
        lambda: validate_receipt_data(forged, lane="treatmentA", run=run, configured=probes[run["name"]], root=root, evidence=evidence),
        "verdict differs",
    )
    expect_refusal(
        "treatment post-value forgery",
        lambda: extract_segment(TREATMENT_SEGMENT[:6] + [TARGET_BEFORE] + TREATMENT_SEGMENT[7:], TREATMENT_SEGMENT, "poison"),
        "sequence differs",
    )
    expect_refusal(
        "control movement forgery",
        lambda: extract_segment(CONTROL_SEGMENT[:6] + [SOURCE_POSITION] + CONTROL_SEGMENT[7:], CONTROL_SEGMENT, "poison"),
        "sequence differs",
    )
    duplicate = TREATMENT_SEGMENT + [TREATMENT_SEGMENT[0]]
    expect_refusal(
        "duplicate marker forgery",
        lambda: extract_segment(duplicate, TREATMENT_SEGMENT, "poison"),
        "marker count differs",
    )


def execute(root: Path) -> Path:
    evidence = root / EVIDENCE_RELATIVE
    ready = evidence / READY_NAME
    require(not ready.exists(), "runtime proof READY already exists; verify it instead")
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    result = derive(root, generated_at)
    selftest(root)
    payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=READY_NAME + ".", suffix=".partial", dir=evidence)
    temp = Path(temporary)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        validate_saved(read_json(temp), root)
        selftest(root)
        os.replace(temp, ready)
    finally:
        if temp.exists():
            temp.unlink()
    validate_saved(read_json(ready), root)
    selftest(root)
    return ready


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("build", "verify", "selftest"))
    args = parser.parse_args()
    root = repo_root()
    ready = root / EVIDENCE_RELATIVE / READY_NAME
    if args.mode == "build":
        path = execute(root)
        print(f"MISSION_NATIVE_SETPOS_RUNTIME_READY {stamp(path, root)}")
    elif args.mode == "verify":
        validate_saved(read_json(ready), root)
        print(f"MISSION_NATIVE_SETPOS_RUNTIME_VERIFIED {stamp(ready, root)}")
    else:
        selftest(root)
        print("MISSION_NATIVE_SETPOS_RUNTIME_SELFTEST_OK 4 targeted counterexamples rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
