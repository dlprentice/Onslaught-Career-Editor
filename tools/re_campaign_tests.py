#!/usr/bin/env python3
"""Contract tests for the specimen-bound recursive RE campaign owner."""

from __future__ import annotations

import csv
import functools
import hashlib
import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import re_campaign as campaign
import re_gen73_reseal as gen73_reseal


def write_tsv(path: Path, columns: list[str], rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_snapshot(
    root: Path,
    exact: bool = True,
    native_present: bool = False,
    native_name: str = "FollowWaypoint",
    specimen_sha: str = "7" * 64,
) -> Path:
    snapshot = root / "snapshot"
    snapshot.mkdir()
    summary = {
        "schema": campaign.REQUIRED_SNAPSHOT_SCHEMA,
        "generatedAtUtc": "2026-08-02T00:00:00+00:00",
        "denominators": {
            "functionPopulation": 2,
            "nativeRegistryPopulation": 1,
            "bodyAccountingMethod": "EXACT_GHIDRA_FRAGMENTS" if exact else "BODY_MIN_MAX_HULLS",
            "coverageSetSha256": "8" * 64,
        },
        "bytes": {
            "unmappedByAnyFunction": 8,
            "executedButUnmapped": 3,
            "allUnmappedSegments": 2,
        },
        "inputs": {
            "specimen": {"sha256": specimen_sha, "path": "specimen.exe"},
            "parityGraph": {"bodyRanges": {"sha256": "9" * 64}} if exact else None,
        },
        "sources": [
            {
                "sourceId": "existing-trace",
                "coverageSha256": "a" * 64,
                "coverageIndex": "coverage.jsonl",
                "textBytesObserved": 12,
                "moduleName": "BEA.exe",
                "trace": "capture.run",
            }
        ],
    }
    (snapshot / "ledger-summary.json").write_text(json.dumps(summary), encoding="utf-8")

    function_columns = [
        "va", "entryRva", "entityKey", "name", "bodyRangesRva", "bodyRangeSetSha256",
        "bodyBytes", "execState", "observedBytes", "nameClass", "understoodTier", "reachClass",
        "nativeShippedName", "nativeRegistryStatus",
    ]
    first_va = "0x00402000" if native_present else "0x00401000"
    first_rva = "0x00002000" if native_present else "0x00001000"
    write_tsv(
        snapshot / "ledger-functions.tsv",
        function_columns,
        [
            {
                "va": first_va, "entryRva": first_rva,
                "entityKey": f"CODE:{specimen_sha}:VA={first_va}:RANGES={'b' * 64}",
                "name": "FUN_00401000", "bodyRangesRva": "0x1000-0x1004",
                "bodyRangeSetSha256": "b" * 64, "bodyBytes": "4", "execState": "COVERED",
                "observedBytes": "4", "nameClass": "FUN", "understoodTier": "U0_NONE",
                "reachClass": "COMBAT_AI",
                "nativeShippedName": native_name if native_present else "",
                "nativeRegistryStatus": "NO_FUNCTION" if native_present else "",
            },
            {
                "va": "0x00401010", "entryRva": "0x00001010",
                "entityKey": f"CODE:{specimen_sha}:VA=0x00401010:RANGES={'c' * 64}",
                "name": "CWeapon__Dark", "bodyRangesRva": "0x1010-0x1018",
                "bodyRangeSetSha256": "c" * 64, "bodyBytes": "8", "execState": "DARK",
                "observedBytes": "0", "nameClass": "NAMED", "understoodTier": "U1_NAMED_ONLY",
                "reachClass": "COMBAT_AI",
                "nativeShippedName": "", "nativeRegistryStatus": "",
            },
        ],
    )
    write_tsv(
        snapshot / "ledger-native-handlers.tsv",
        [
            "index", "recordVa", "handlerVa", "shippedName", "currentGhidraName",
            "registryStatus", "functionPresent", "observed", "terminalState",
            "needsBoundaryReview", "needsBehaviorContract",
        ],
        [
            {
                "index": "0", "recordVa": "0x0064ce20", "handlerVa": "0x00402000",
                "shippedName": native_name, "currentGhidraName": "",
                "registryStatus": "NO_FUNCTION", "functionPresent": "False", "observed": "True",
                "terminalState": (
                    "ENTRY_CONFIRMED_BEHAVIOR_UNKNOWN" if native_present else "BOUNDARY_MISSING"
                ),
                "needsBoundaryReview": "False" if native_present else "True",
                "needsBehaviorContract": "True",
            }
        ],
    )
    write_tsv(
        snapshot / "ledger-gaps.tsv",
        ["startVa", "endVa", "bytes", "prevFunc", "nextFunc"],
        [
            {
                "startVa": "0x00403000", "endVa": "0x00403003", "bytes": "3",
                "prevFunc": "Previous", "nextFunc": "Next",
            }
        ],
    )
    write_tsv(
        snapshot / "ledger-unmapped.tsv",
        [
            "entityKey", "startVa", "endVa", "bytes", "observedBytes",
            "observationState", "classification", "classificationVerdict",
            "terminalState", "bytePattern", "prevFunc", "nextFunc",
        ],
        [
            {
                "entityKey": (
                    f"TEXT_RESIDUAL:{specimen_sha}:0x00403000-0x00403003"
                ),
                "startVa": "0x00403000", "endVa": "0x00403003", "bytes": "3",
                "observedBytes": "3", "observationState": "EXECUTED",
                "classification": "CODE_CANDIDATE",
                "classificationVerdict": "MEASURED_EXECUTION",
                "terminalState": "OPEN_CODE_BOUNDARY",
                "bytePattern": "MIXED_OR_CODE_LIKE_BYTES",
                "prevFunc": "Previous", "nextFunc": "Next",
            },
            {
                "entityKey": (
                    f"TEXT_RESIDUAL:{specimen_sha}:0x00403010-0x00403015"
                ),
                "startVa": "0x00403010", "endVa": "0x00403015", "bytes": "5",
                "observedBytes": "0", "observationState": "DARK",
                "classification": "AMBIGUOUS", "classificationVerdict": "UNSCORED",
                "terminalState": "OPEN_CLASSIFICATION",
                "bytePattern": "PADDING_LIKE_BYTES",
                "prevFunc": "Previous", "nextFunc": "Next",
            },
        ],
    )
    write_tsv(
        snapshot / "ledger-dark.tsv",
        [
            "startVa", "endVa", "darkBytes", "funcCount", "namedCount", "topReachClass",
            "topFamilies", "largestFunc", "largestFuncBytes", "inCallersObserved", "inCallersTotal",
        ],
        [
            {
                "startVa": "0x00401010", "endVa": "0x00401018", "darkBytes": "8",
                "funcCount": "1", "namedCount": "1", "topReachClass": "COMBAT_AI",
                "topFamilies": "CWeapon(1)", "largestFunc": "CWeapon__Dark",
                "largestFuncBytes": "8", "inCallersObserved": "1", "inCallersTotal": "1",
            }
        ],
    )
    write_tsv(
        snapshot / "ledger-families.tsv",
        ["family", "totalFuncs", "totalBytes", "observedBytes", "darkFuncs", "darkBytes"],
        [],
    )
    ready = {
        "schema": campaign.coverage.SNAPSHOT_READY_SCHEMA,
        "generatedAtUtc": "2026-08-02T00:00:00+00:00",
        "files": {
            name: {**campaign.coverage.file_stamp(snapshot / name), "path": name}
            for name in campaign.coverage.SNAPSHOT_FILES
        },
    }
    (snapshot / "ledger.ready.json").write_text(
        json.dumps(ready, indent=2) + "\n", encoding="utf-8"
    )
    return snapshot


def refresh_snapshot_ready(snapshot: Path) -> None:
    ready_path = snapshot / "ledger.ready.json"
    ready = json.loads(ready_path.read_text(encoding="utf-8"))
    ready["files"] = {
        name: {**campaign.coverage.file_stamp(snapshot / name), "path": name}
        for name in campaign.coverage.SNAPSHOT_FILES
    }
    ready_path.write_text(json.dumps(ready, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def float32(bits: str) -> float:
    return struct.unpack("<f", struct.pack("<I", int(bits, 16)))[0]


def manifest_verification_report() -> dict:
    return {
        "ok": True,
        "checks": {
            "source_sha256": True,
            "source_inflated_sha256": True,
            "all_anchors_still_present_in_source": True,
            "output_readable": True,
            "output_sha256": True,
            "output_inflated_sha256": True,
            "output_blocks": True,
            "all_new_bytes_present_in_output": True,
            "splice_anchor_still_present_in_source": True,
            "splice_insert_present_in_output": True,
        },
    }


def make_runtime_contract(root: Path, specimen_path: Path) -> Path:
    evidence_root = root / "runtime-evidence"
    evidence_root.mkdir(exist_ok=True)

    def artifact(name: str, payload: bytes) -> tuple[str, str]:
        path = evidence_root / name
        path.write_bytes(payload)
        return name, sha256(path)

    def json_artifact(name: str, value: dict) -> tuple[str, str]:
        return artifact(name, (json.dumps(value, indent=2) + "\n").encode("utf-8"))

    pristine_bytes = specimen_path.read_bytes()
    runtime_bytes = bytearray(pristine_bytes)
    patch_offset = 4
    patch_before = bytes(runtime_bytes[patch_offset:patch_offset + 4])
    patch_after = bytes(value ^ 0xFF for value in patch_before)
    runtime_bytes[patch_offset:patch_offset + 4] = patch_after
    runtime = artifact("runtime.exe", bytes(runtime_bytes))
    source_archive = artifact("source.aya", b"source archive")
    payload = artifact("payload.aya", b"payload")
    launched_archive = artifact("launched.aya", b"payload")
    poison_payload = artifact("poison.aya", b"poison payload")
    program = [
        {
            "op": "let", "name": "target", "native": "GetThingRef",
            "args": [{"string": "Turret 01"}],
        },
        {
            "op": "call", "target": "target", "native": "SetVulnerable",
            "args": [{"bool": True}],
        },
        {
            "op": "call", "target": "target", "native": "SetHealth",
            "args": [{"float": 0.001}],
        },
        {"op": "call", "native": "Pause", "args": [{"float": 1.0}]},
        {
            "op": "call", "target": "target", "native": "Damage",
            "args": [{"float": 1000.0}],
        },
    ]
    intents = [{"op": "replace-script", "script": "Setup", "program": program}]
    recipe = json_artifact("recipe.json", {"world": "RLWD", "intents": intents})
    manifest = json_artifact(
        "manifest.json",
        {
            "arm": "probe",
            "specimen_sha256": sha256(specimen_path),
            "source": {
                "path": str((evidence_root / source_archive[0]).resolve()),
                "sha256": source_archive[1],
            },
            "output": {
                "path": str((evidence_root / payload[0]).resolve()),
                "sha256": payload[1],
            },
            "world": {"level_id": 100},
            "intents": intents,
            "splice": {
                "emitter": {
                    "instructionCount": 24,
                    "recordBytes": 685,
                    "nativeCalls": [{"native": row["native"]} for row in program],
                }
            },
            "verification": {
                "replacementScriptOrderPreserved": True,
                "replacementTargetOrdinalPreserved": True,
                "replacementRecordReadbackExact": True,
                "replacementNonTargetRecordsIdentical": 24,
            },
        },
    )
    poison_manifest = json_artifact(
        "poison-manifest.json",
        {
            "arm": "poison-opcode",
            "specimen_sha256": sha256(specimen_path),
            "source": {
                "path": str((evidence_root / payload[0]).resolve()),
                "sha256": payload[1],
            },
            "output": {
                "path": str((evidence_root / poison_payload[0]).resolve()),
                "sha256": poison_payload[1],
            },
            "edits": [{"kind": "poison-opcode", "old_opcode": 0x17, "new_opcode": 0x7F}],
            "verification": {
                "diff_ranges": 1,
                "changed_bytes": 1,
                "differs_from_probe_only_by_this_arm": True,
            },
        },
    )
    launch_arguments = ["-skipfmv", "-forcewindowed", "-level", "100"]

    def receipt(*, poison: bool) -> dict:
        staged_sha = poison_payload[1] if poison else payload[1]
        return {
            "probe": {
                "level": 100,
                "oracle": (
                    {"kind": "fatalFault", "timeoutSeconds": 35}
                    if poison
                    else {
                        "kind": "all",
                        "of": [
                            {"kind": "setupHistoryContains"},
                            {"kind": "fileAppears"},
                            {"kind": "survives"},
                        ],
                    }
                ),
            },
            "dryRun": False,
            "status": "complete",
            "verdict": "PASS",
            "command": "'scratch/runtime.exe' " + " ".join(launch_arguments),
            "oracle": {
                "outcome": "satisfied",
                "processAliveAtDecision": not poison,
            },
            "sourceWitness": {
                "BEA.exe": runtime[1],
                "BEA.exe.original.backup": sha256(specimen_path),
            },
            "staging": {
                "executableSha256": runtime[1],
                "stagedFiles": [
                    {
                        "dest": "data/Resources/100_res_PC.aya",
                        "sha256": staged_sha,
                        "replacedSha256": source_archive[1],
                    }
                ],
            },
            "diagnosis": {
                "levelLoadLogged": True,
                "fatalFaultLogPresent": poison,
            },
            "exitClassification": {
                "isFault": poison,
                "hex": "0xC0000005" if poison else None,
            },
            "faultGate": {
                "triggered": poison,
                "optedIn": poison,
            },
            "teardown": {"verified": True},
        }

    valid = json_artifact("valid.json", receipt(poison=False))
    poison = json_artifact("poison.json", receipt(poison=True))
    ordered = artifact(
        "ordered.log",
        (
            "CHAIN 1 GetThingRef eip=00403000 esp=001af47c\n"
            "001af47c  0052eb56 00000000 00000000 00000000\n"
            "CHAIN 2 SetVulnerable eip=00403010 esp=001af47c\n"
            "001af47c  0052eb56 00000000 00000000 00000000\n"
            "CHAIN 3 SetHealth eip=00403020 esp=001af47c\n"
            "001af47c  0052eb56 00000000 00000000 00000000\n"
            "CHAIN 4 Pause eip=00403030 esp=001af47c\n"
            "001af47c  0052eb56 00000000 00000000 00000000\n"
            "CHAIN 5 Damage eip=00402000 esp=001af47c\n"
            "001af47c  0052eb56 00000000 00000000 00000000\n"
        ).encode("ascii"),
    )
    abi = artifact(
        "abi.log",
        (
            "DAMAGE_DISPATCH receiver=077e2630 vtable=005e24dc "
            "callee=00401010 amount_bits=447a0000\n"
            "001af48c  447a0000 077e7a10 00000001 ffffffff\n"
        ).encode("ascii"),
    )
    transition = artifact(
        "transition.log",
        (
            "APPLY_ENTRY receiver=077e2630 vtable=005e24dc amount_bits=447a0000 "
            "source=077e7a10 apply_shields=1 mesh_part=ffffffff "
            "life_bits=3ba3d70b shield_bits=00000000 state_1f0=00000000\n"
            "APPLY_RETURN receiver=077e2630 vtable=005e24dc life_bits=c479ffae "
            "shield_bits=00000000 state_1f0=00000000\n"
        ).encode("ascii"),
    )
    death = artifact(
        "death.log",
        (
            "DEATH_1 slot_c8 receiver=077e2630 life_bits=c479ffae\n"
            "DEATH_2 MarkDestroyed receiver=077e2630 life_bits=c479ffae\n"
            "DEATH_3 ResetDeployment receiver=077e2630 life_bits=c479ffae\n"
            "DEATH_4 slot_11c_noop receiver=077e2630\n"
        ).encode("ascii"),
    )

    contract = {
        "schema": campaign.RUNTIME_CONTRACT_INPUT_SCHEMA,
        "contractId": "RC-TEST-DAMAGE",
        "baseContractId": campaign._contract_id(
            f"CODE:{sha256(specimen_path)}:VA=0x00402000:RANGES={'b' * 64}"
        ),
        "questionIdsAddressed": [
            campaign._question_id(
                "NATIVE_BEHAVIOR",
                f"CODE:{sha256(specimen_path)}:VA=0x00402000:RANGES={'b' * 64}",
            )
        ],
        "measuredAtUtc": "2026-08-02T00:00:00Z",
        "status": "BOUNDED_RUNTIME_SURVIVED_CONTROLS",
        "scope": {
            "kind": "FORCED_SCRIPT", "level": 100, "script": "Setup",
            "receiverName": "Turret 01", "primaryEntryVa": "0x00402000",
            "primaryShippedName": "Damage",
        },
        "identity": {
            "pristineSpecimenPath": str(specimen_path.relative_to(evidence_root)),
            "pristineSpecimenSha256": sha256(specimen_path),
            "runtimeExecutablePath": runtime[0], "runtimeExecutableSha256": runtime[1],
            "launchedArchivePath": launched_archive[0],
            "launchedArchiveSha256": launched_archive[1],
            "sourceArchivePath": source_archive[0], "sourceArchiveSha256": source_archive[1],
            "payloadPath": payload[0], "payloadSha256": payload[1],
            "poisonPayloadPath": poison_payload[0],
            "poisonPayloadSha256": poison_payload[1],
            "recipePath": recipe[0], "recipeSha256": recipe[1],
            "authorManifestPath": manifest[0], "authorManifestSha256": manifest[1],
            "poisonManifestPath": poison_manifest[0],
            "poisonManifestSha256": poison_manifest[1],
            "runtimeRelationToPristine": {
                "kind": "DECLARED_BYTE_RANGES",
                "differentBytes": 4,
                "ranges": [
                    {
                        "offset": hex(patch_offset),
                        "pristineHex": patch_before.hex(),
                        "runtimeHex": patch_after.hex(),
                    }
                ],
            },
        },
        "trigger": {
            "launchArguments": launch_arguments,
            "emittedInstructionCount": 24,
            "emittedRecordBytes": 685,
            "nonTargetScriptRecordsByteIdentical": 24,
        },
        "observedCallOrder": [
            {"va": "0x00403000", "boundedName": "IScript__GetThingRef"},
            {"va": "0x00403010", "boundedName": "IScript__SetVulnerable"},
            {"va": "0x00403020", "boundedName": "IScript__SetHealth"},
            {"va": "0x00403030", "boundedName": "IScript__Pause"},
            {"va": "0x00402000", "boundedName": "IScript__Damage"},
            {"va": "0x00401010", "boundedName": "CUnit__ApplyDamage"},
            {
                "va": "0x00404000",
                "boundedName": "CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph",
            },
            {
                "va": "0x00404010",
                "boundedName": "CGroundUnit__MarkDestroyedAndResetState",
            },
            {
                "va": "0x00404020",
                "boundedName": "CUnit__ResetDeploymentGraphAndScheduleEvent",
            },
            {"va": "0x00404030", "boundedName": "SharedVFunc__NoOpRet8_00405db0"},
        ],
        "inputsAtApplyDamage": {
            "receiverVtable": "0x005e24dc", "damageSource": "sample",
            "amount": {"bits": "0x447a0000", "float32": float32("447a0000")},
            "applyShields": 1, "meshPartIndex": -1,
        },
        "stateTransition": {
            "life": {
                "beforeBits": "0x3ba3d70b", "beforeFloat32": float32("3ba3d70b"),
                "afterBits": "0xc479ffae", "afterFloat32": float32("c479ffae"),
            },
            "shields": {
                "beforeBits": "0x00000000", "beforeFloat32": 0.0,
                "afterBits": "0x00000000", "afterFloat32": 0.0,
            },
            "immediateField1f0": {"before": 0, "after": 0},
        },
        "controls": [
            {"kind": "VALID_EXISTING_TARGET", "verdict": "PASS", "receiptPath": valid[0], "receiptSha256": valid[1]},
            {"kind": "INVALID_OPCODE_POISON", "verdict": "PASS", "receiptPath": poison[0], "receiptSha256": poison[1]},
            {"kind": "ORDERED_CDB_ENTRY_CHAIN", "verdict": "PASS", "logPath": ordered[0], "logSha256": ordered[1]},
        ],
        "runtimeEvidence": [
            {"role": "ordered five-native chain", "path": ordered[0], "sha256": ordered[1]},
            {"role": "receiver, vtable, callee, ABI", "path": abi[0], "sha256": abi[1]},
            {"role": "life and shield transition", "path": transition[0], "sha256": transition[1]},
            {"role": "death virtual call order", "path": death[0], "sha256": death[1]},
        ],
        "verdict": {
            "execution": "SURVIVED", "identity": "SURVIVED_FOR_SCOPED_PATH",
            "inputs": "MEASURED", "immediateOutputs": "MEASURED",
            "refuter": "UNSCORED", "promotion": "NOT_AUTHORIZED",
        },
        "claimBoundary": ["forced script path only"],
        "nextFrontier": ["repeat with a holdout target"],
    }
    path = evidence_root / "contract.json"
    path.write_text(json.dumps(contract), encoding="utf-8")
    return path


def make_imported_runtime_overlay(root: Path) -> tuple[Path, Path, Path]:
    evidence_root = root / "runtime-evidence"
    evidence_root.mkdir()
    specimen = evidence_root / "specimen.exe"
    specimen.write_bytes(b"pristine specimen")
    campaign_dir = root / "campaign"
    campaign.seed(
        make_snapshot(
            root,
            native_present=True,
            native_name="Damage",
            specimen_sha=sha256(specimen),
        ),
        campaign_dir,
    )
    contract = make_runtime_contract(root, specimen)
    overlay = root / "runtime-overlay"
    with patch.object(
        campaign.probe_author,
        "verify_manifest",
        return_value=manifest_verification_report(),
    ):
        campaign.import_runtime_contract(campaign_dir, contract, overlay)
    return campaign_dir, contract, overlay


def make_runtime_adjudication(
    root: Path,
    campaign_dir: Path,
    overlay: Path,
    verdict: str,
) -> Path:
    overlay_row = campaign._read_tsv(overlay / "runtime-contracts.tsv")[0]
    overlay_sha = sha256(overlay / "runtime-contracts.ready.json")
    evidence = root / f"adjudication-{verdict.lower()}"
    evidence.mkdir()
    result = evidence / "refuter-result.json"
    refuter_evidence = []
    if verdict == "SURVIVED":
        fixture = (
            Path(campaign.__file__).resolve().parent
            / "probe"
            / "fixtures"
            / "skin-weight-2026-07-31-executed-law.json"
        )
        finding_data = json.loads(fixture.read_text(encoding="utf-8"))
        finding_data["subject"] = campaign._runtime_refuter_subject(
            overlay_row, overlay_sha
        )
        finding = evidence / "refuter-finding.json"
        finding.write_text(json.dumps(finding_data), encoding="utf-8")
        refuter = campaign.probe_refute.adjudicate(finding_data)
        refuter["source"] = finding.name
        refuter_evidence.append(
            {
                "role": "refuter-finding",
                "path": finding.name,
                "sha256": sha256(finding),
            }
        )
    else:
        refuter = {
            "schema": campaign.REFUTER_RESULT_SCHEMA,
            "verdict": verdict,
            "baseContractId": overlay_row["baseContractId"],
            "overlayReadySha256": overlay_sha,
            "questionIdsAddressed": overlay_row["questionIdsAddressed"].split(";"),
            "findings": ["independent bounded refuter result"],
            "reason": f"synthetic contract test exercises {verdict} reduction",
        }
    result.write_text(json.dumps(refuter), encoding="utf-8")
    refuter_evidence.insert(
        0,
        {
            "role": "refuter-result",
            "path": result.name,
            "sha256": sha256(result),
        },
    )
    adjudication = {
        "schema": campaign.RUNTIME_ADJUDICATION_SCHEMA,
        "baseCampaignReadySha256": sha256(campaign_dir / "campaign.ready.json"),
        "overlayReadySha256": overlay_sha,
        "decision": {
            "baseContractId": overlay_row["baseContractId"],
            "questionIdsAddressed": overlay_row["questionIdsAddressed"].split(";"),
            "refuterVerdict": verdict,
            "measuredAtUtc": "2026-08-02T12:00:00Z",
            "refuterEvidence": refuter_evidence,
            "nextQuestions": [
                {
                    "questionType": "NATURAL_DAMAGE_CHAIN",
                    "priority": 1,
                    "score": 100,
                    "requiresElevation": False,
                    "recommendedInstrument": "HOLDOUT_TARGET_EXISTING_TRACE_FIRST",
                    "question": "Does a natural projectile path reproduce the bounded damage dispatch?",
                    "cheapestFalsifier": "A holdout target selects another callee or state transition.",
                    "source": "synthetic-refuter-test",
                }
            ],
            "remainingUncertainty": "natural projectile, collision, and target-class paths",
            "rebuildMapping": {
                "rebuildOwner": "OnslaughtRebuild.Core/Combat",
                "rebuildImplementation": "DamageContractCandidate",
                "parityTests": "DamageContractCandidateTests",
                "rebuildState": "PARTIAL_CONTRACT",
            },
            "supersessions": [],
        },
    }
    path = evidence / "adjudication.json"
    path.write_text(json.dumps(adjudication), encoding="utf-8")
    return path


def make_rebuild_ready_decision(root: Path) -> tuple[dict, dict[str, str], str]:
    owner = campaign.REPO_ROOT / "rebuild/OnslaughtRebuild.Core/Level100Destruction.cs"
    test = (
        campaign.REPO_ROOT
        / "rebuild/OnslaughtRebuild.Core.Tests/Level100DestructionContactTests.cs"
    )
    project = (
        campaign.REPO_ROOT
        / "rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj"
    )

    def source_stamp(path: Path) -> dict:
        measured = campaign.coverage.file_stamp(path)
        return {
            "path": path.relative_to(campaign.REPO_ROOT).as_posix(),
            "bytes": measured["bytes"],
            "sha256": measured["sha256"],
        }

    implementation = "Level100DestructionState.ApplyRoundHit"
    test_name = (
        "OnslaughtRebuild.Core.Tests.Level100DestructionContactTests."
        "WholeBodyLifeRequiresStrictlyNegativeRemainingLifeToBecomeTerminal"
    )
    dotnet = Path(str(shutil.which("dotnet"))).resolve()
    dotnet_stamp = {
        "path": str(dotnet),
        "bytes": dotnet.stat().st_size,
        "sha256": campaign.coverage.sha256_of(dotnet),
    }
    argv = [
        str(dotnet),
        "test",
        str(project.resolve()),
        "--no-restore",
        "--filter",
        f"FullyQualifiedName={test_name}",
        "--logger",
        "console;verbosity=normal",
    ]
    overlay_row = {
        "baseContractId": "C-rebuild-gate-test",
        "entityKey": "CODE:test-rebuild-gate",
    }
    overlay_sha = "a" * 64
    result = {
        "schema": campaign.REBUILD_RESULT_SCHEMA,
        "baseContractId": overlay_row["baseContractId"],
        "entityKey": overlay_row["entityKey"],
        "overlayReadySha256": overlay_sha,
        "ownerSha256": campaign.coverage.sha256_of(owner),
        "testSha256": campaign.coverage.sha256_of(test),
        "projectSha256": campaign.coverage.sha256_of(project),
        "implementation": implementation,
        "testName": test_name,
        "expectedTests": 1,
        "rebuildSource": campaign._rebuild_source_fingerprint(),
        "dotnet": dotnet_stamp,
        "cwd": str(campaign.REPO_ROOT),
        "argv": argv,
        "exitCode": 0,
        "failed": 0,
        "passed": 1,
        "skipped": 0,
        "total": 1,
    }
    result_path = root / "rebuild-result.json"
    result_path.write_text(json.dumps(result), encoding="utf-8")
    result_stamp = campaign.coverage.file_stamp(result_path)
    gate = {
        "schema": campaign.REBUILD_GATE_SCHEMA,
        "runner": "dotnet-test-v1",
        "owner": source_stamp(owner),
        "implementation": implementation,
        "test": source_stamp(test),
        "testName": test_name,
        "project": source_stamp(project),
        "expectedTests": 1,
        "result": {
            "path": result_path.name,
            "bytes": result_stamp["bytes"],
            "sha256": result_stamp["sha256"],
        },
    }
    decision = {
        "rebuildMapping": {
            "rebuildOwner": owner.relative_to(campaign.REPO_ROOT).as_posix(),
            "rebuildImplementation": implementation,
            "parityTests": test_name,
            "rebuildState": "REBUILD_READY",
        },
        "rebuildGate": gate,
    }
    return decision, overlay_row, overlay_sha


class CampaignTests(unittest.TestCase):
    def test_seed_publishes_eight_bound_ledgers_and_a_ready_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = make_snapshot(root)
            out = root / "campaign"
            receipt = campaign.seed(snapshot, out)
            verified = campaign.verify(out)

            self.assertEqual(receipt["counts"], verified["counts"])
            self.assertEqual(2, receipt["counts"]["functions"])
            self.assertEqual(2, receipt["counts"]["residuals"])
            self.assertEqual(4, receipt["counts"]["contracts"])
            self.assertEqual(1, receipt["counts"]["scenarios"])
            self.assertGreaterEqual(receipt["counts"]["questions"], 3)
            self.assertTrue((out / "campaign.ready.json").is_file())
            self.assertEqual("bea.re.campaign.v5", receipt["schema"])
            self.assertEqual(campaign.REDUCER_SCHEMA, receipt["reducer"]["schema"])
            self.assertEqual(campaign._current_reducer_manifest(), receipt["reducer"])
            self.assertIn(
                "level521-call-context-refuter",
                {row["role"] for row in receipt["reducer"]["files"]},
            )

            contracts = campaign._read_tsv(out / "campaign-contracts.tsv")
            self.assertTrue(all(row["semanticGrade"] == "C0_OPAQUE" for row in contracts))
            self.assertTrue(all(row["refuterVerdict"] == "UNSCORED" for row in contracts))
            self.assertTrue(all(row["questionIds"] for row in contracts))

    def test_reseed_carry_preserves_adjudication_and_successor_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base, _contract, overlay = make_imported_runtime_overlay(root)
            addressed = campaign._read_tsv(overlay / "runtime-contracts.tsv")[0][
                "questionIdsAddressed"
            ]
            adjudication = make_runtime_adjudication(root, base, overlay, "SURVIVED")
            progressed = root / "progressed"
            campaign.advance_runtime_contract(base, overlay, adjudication, progressed)

            fresh_root = root / "fresh"
            fresh_root.mkdir()
            specimen_sha = sha256(root / "runtime-evidence" / "specimen.exe")
            fresh_snapshot = make_snapshot(
                fresh_root,
                native_present=True,
                native_name="Damage",
                specimen_sha=specimen_sha,
            )
            carried = root / "carried"
            receipt = campaign.seed(fresh_snapshot, carried, carry=progressed)
            campaign.verify(carried)

            questions = {
                row["questionId"]: row
                for row in campaign._read_tsv(carried / "campaign-questions.tsv")
            }
            contracts = campaign._read_tsv(carried / "campaign-contracts.tsv")
            damage = next(row for row in contracts if row["nativeShippedName"] == "Damage")
            adjudications = campaign._read_tsv(
                carried / "campaign-adjudications.tsv"
            )

        self.assertEqual(2, receipt["generation"])
        self.assertEqual(campaign.CAMPAIGN_RESEED_KIND, receipt["advance"]["kind"])
        self.assertFalse(receipt["advance"]["legacyBridgeUsed"])
        self.assertEqual(1, receipt["advance"]["carried"]["functionRows"])
        self.assertEqual(0, receipt["advance"]["carried"]["residualRows"])
        self.assertEqual(1, receipt["advance"]["carried"]["contractRows"])
        self.assertEqual("CLOSED_SURVIVED", questions[addressed]["state"])
        self.assertTrue(
            any(row["parentQuestionId"] == addressed for row in questions.values())
        )
        self.assertEqual("C2_BOUNDED_RUNTIME", damage["semanticGrade"])
        self.assertEqual("SURVIVED", damage["refuterVerdict"])
        self.assertEqual(1, len(adjudications))

    def test_reseed_does_not_treat_source_residual_classification_as_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prior_root = root / "prior-source"
            prior_root.mkdir()
            prior_snapshot = make_snapshot(prior_root)
            residual_path = prior_snapshot / "ledger-unmapped.tsv"
            residuals = campaign._read_tsv(residual_path)
            residuals[0]["classification"] = "DATA"
            residuals[0]["classificationVerdict"] = "STATIC_LEDGER_CLASSIFICATION"
            residuals[0]["terminalState"] = "TERMINAL_DATA"
            write_tsv(residual_path, list(residuals[0]), residuals)
            refresh_snapshot_ready(prior_snapshot)
            prior = root / "prior"
            campaign.seed(prior_snapshot, prior)

            fresh_root = root / "fresh-source"
            fresh_root.mkdir()
            carried = root / "carried"
            receipt = campaign.seed(make_snapshot(fresh_root), carried, carry=prior)
            carried_residuals = campaign._read_tsv(
                carried / "campaign-residuals.tsv"
            )
            target = next(
                row
                for row in carried_residuals
                if row["startVa"] == "0x00403000"
            )

        self.assertEqual(0, receipt["advance"]["carried"]["residualRows"])
        self.assertEqual("CODE_CANDIDATE", target["classification"])
        self.assertEqual("MEASURED_EXECUTION", target["classificationVerdict"])
        self.assertEqual("OPEN_CODE_BOUNDARY", target["terminalState"])

    def test_reseed_counts_every_stale_progressed_entity_layer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base, _contract, overlay = make_imported_runtime_overlay(root)
            adjudication = make_runtime_adjudication(root, base, overlay, "SURVIVED")
            progressed = root / "progressed"
            campaign.advance_runtime_contract(base, overlay, adjudication, progressed)

            fresh_root = root / "fresh-source"
            fresh_root.mkdir()
            specimen_sha = sha256(root / "runtime-evidence" / "specimen.exe")
            fresh_snapshot = make_snapshot(
                fresh_root,
                native_present=True,
                native_name="Damage",
                specimen_sha=specimen_sha,
            )
            functions_path = fresh_snapshot / "ledger-functions.tsv"
            functions = campaign._read_tsv(functions_path)
            functions[0]["bodyRangeSetSha256"] = "d" * 64
            functions[0]["entityKey"] = (
                f"CODE:{specimen_sha}:VA={functions[0]['va']}:RANGES={'d' * 64}"
            )
            write_tsv(functions_path, list(functions[0]), functions)
            refresh_snapshot_ready(fresh_snapshot)

            receipt = campaign.seed(
                fresh_snapshot,
                root / "carried",
                carry=progressed,
            )
            carried = receipt["advance"]["carried"]

        self.assertEqual(1, carried["staleFunctions"])
        self.assertEqual(1, carried["staleContracts"])
        self.assertEqual(1, carried["staleAdjudications"])
        self.assertGreaterEqual(carried["staleQuestions"], 1)

    def test_reseed_carry_refuses_a_different_specimen(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first_root = root / "first"
            first_root.mkdir()
            prior = root / "prior"
            campaign.seed(make_snapshot(first_root, specimen_sha="1" * 64), prior)
            fresh_root = root / "fresh"
            fresh_root.mkdir()

            with self.assertRaisesRegex(campaign.CampaignError, "specimen differs"):
                campaign.seed(
                    make_snapshot(fresh_root, specimen_sha="2" * 64),
                    root / "carried",
                    carry=prior,
                )

    def test_reseed_carry_refuses_an_unreviewed_v4_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake = root / "fake-v4"
            fake.mkdir()
            (fake / "campaign.ready.json").write_text(
                json.dumps({"schema": campaign.LEGACY_CAMPAIGN_SCHEMA}),
                encoding="utf-8",
            )
            fresh_root = root / "fresh"
            fresh_root.mkdir()

            with self.assertRaisesRegex(campaign.CampaignError, "exact reviewed bridge"):
                campaign.seed(
                    make_snapshot(fresh_root),
                    root / "carried",
                    carry=fake,
                )

    def test_exact_hash_legacy_bridge_can_reseed_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            legacy_snapshot_root = root / "legacy-snapshot"
            legacy_snapshot_root.mkdir()
            legacy = root / "legacy"
            specimen_sha = campaign.LEGACY_CAMPAIGN_CARRY_SPECIMEN_SHA256
            campaign.seed(
                make_snapshot(legacy_snapshot_root, specimen_sha=specimen_sha),
                legacy,
            )
            ready_path = legacy / "campaign.ready.json"
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            ready["schema"] = campaign.LEGACY_CAMPAIGN_SCHEMA
            ready["generation"] = 3
            ready.pop("reducer")
            ready_path.write_text(json.dumps(ready), encoding="utf-8")
            ready_sha = sha256(ready_path)

            fresh_root = root / "fresh"
            fresh_root.mkdir()
            fresh_snapshot = make_snapshot(fresh_root, specimen_sha=specimen_sha)
            carried = root / "carried"
            with (
                patch.object(campaign, "LEGACY_CAMPAIGN_CARRY_ROOT", legacy),
                patch.object(
                    campaign, "LEGACY_CAMPAIGN_CARRY_READY_SHA256", ready_sha
                ),
            ):
                receipt = campaign.seed(fresh_snapshot, carried, carry=legacy)
                campaign.verify(carried)

        self.assertEqual(4, receipt["generation"])
        self.assertTrue(receipt["advance"]["legacyBridgeUsed"])

    def test_exact_hash_frozen_v5_bridge_can_reseed_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prior_snapshot_root = root / "prior-snapshot"
            prior_snapshot_root.mkdir()
            prior = root / "prior"
            specimen_sha = campaign.FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256
            campaign.seed(
                make_snapshot(prior_snapshot_root, specimen_sha=specimen_sha),
                prior,
            )
            ready_path = prior / "campaign.ready.json"
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            ready["generation"] = campaign.FROZEN_V5_CAMPAIGN_CARRY_GENERATION
            ready["advance"] = {"kind": "SYNTHETIC_FROZEN_BRIDGE_TEST"}
            ready_path.write_text(json.dumps(ready), encoding="utf-8")
            ready_sha = sha256(ready_path)

            fresh_root = root / "fresh"
            fresh_root.mkdir()
            fresh_snapshot = make_snapshot(fresh_root, specimen_sha=specimen_sha)
            carried = root / "carried"
            with (
                patch.object(campaign, "FROZEN_V5_CAMPAIGN_CARRY_ROOT", prior),
                patch.object(
                    campaign, "FROZEN_V5_CAMPAIGN_CARRY_READY_SHA256", ready_sha
                ),
                patch.object(
                    campaign,
                    "FROZEN_V5_CAMPAIGN_CARRY_REDUCER_ID",
                    ready["reducer"]["id"],
                ),
            ):
                receipt = campaign.seed(fresh_snapshot, carried, carry=prior)
                campaign.verify(carried)

        self.assertEqual(
            campaign.FROZEN_V5_CAMPAIGN_CARRY_GENERATION + 1,
            receipt["generation"],
        )
        self.assertEqual(
            "EXACT_AUDITED_FROZEN_V5_R3",
            receipt["advance"]["carryVerification"],
        )

    def test_frozen_v5_bridge_refuses_any_unpinned_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fake = root / "fake-v5"
            fake.mkdir()
            (fake / "campaign.ready.json").write_text(
                json.dumps({"schema": campaign.SCHEMA}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(campaign.CampaignError, "exact reviewed bridge"):
                campaign._verify_frozen_v5_campaign_carry(fake)

    def test_frozen_v5_bridge_rehashes_its_historical_reducer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot_root = root / "snapshot"
            snapshot_root.mkdir()
            prior = root / "prior"
            campaign.seed(
                make_snapshot(
                    snapshot_root,
                    specimen_sha=campaign.FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256,
                ),
                prior,
            )
            ready_path = prior / "campaign.ready.json"
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            ready["generation"] = campaign.FROZEN_V5_CAMPAIGN_CARRY_GENERATION
            ready_path.write_text(json.dumps(ready), encoding="utf-8")
            reducer = prior / "_reducer" / "tools" / "re_campaign.py"
            reducer.write_text(
                reducer.read_text(encoding="utf-8") + "\n# tampered\n",
                encoding="utf-8",
            )

            with (
                patch.object(campaign, "FROZEN_V5_CAMPAIGN_CARRY_ROOT", prior),
                patch.object(
                    campaign,
                    "FROZEN_V5_CAMPAIGN_CARRY_READY_SHA256",
                    sha256(ready_path),
                ),
                patch.object(
                    campaign,
                    "FROZEN_V5_CAMPAIGN_CARRY_REDUCER_ID",
                    ready["reducer"]["id"],
                ),
                self.assertRaisesRegex(campaign.CampaignError, "reducer file has changed"),
            ):
                campaign._verify_frozen_v5_campaign_carry(prior)

    def test_campaign_reducer_bytes_are_part_of_the_ready_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "campaign"
            campaign.seed(make_snapshot(root), out)
            reducer = out / "_reducer" / "tools" / "probe" / "refute.py"
            reducer.write_text(
                reducer.read_text(encoding="utf-8") + "\n# tampered\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(campaign.CampaignError, "reducer file has changed"):
                campaign.verify(out)

    def test_campaign_refuses_current_reducer_drift_without_migration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "campaign"
            campaign.seed(make_snapshot(root), out)
            current = campaign._current_reducer_manifest()
            drifted = json.loads(json.dumps(current))
            drifted["id"] = "0" * 64

            with patch.object(
                campaign, "_current_reducer_manifest", return_value=drifted
            ), self.assertRaisesRegex(campaign.CampaignError, "explicit migration"):
                campaign.verify(out)

    def test_successor_cannot_cycle_back_to_any_historical_question_shape(self) -> None:
        parent = {
            "questionId": "Q-parent",
            "question": "Question B?",
            "recommendedInstrument": "Instrument B",
            "cheapestFalsifier": "Falsifier B",
            "attemptCount": "2",
        }
        history = [
            parent,
            {
                "questionId": "Q-old",
                "question": "Question A?",
                "recommendedInstrument": "Instrument A",
                "cheapestFalsifier": "Falsifier A",
                "attemptCount": "1",
            },
        ]
        spec = {
            "questionType": "CONTRACT",
            "question": "  QUESTION   A? ",
            "recommendedInstrument": "instrument a",
            "cheapestFalsifier": "falsifier a",
        }

        with self.assertRaisesRegex(campaign.CampaignError, "historical question"):
            campaign._successor_question(
                spec,
                entity_key="CODE:test",
                parents=[parent],
                history=history,
                generation=3,
                measured_at="2026-08-02T12:00:00Z",
            )

    def test_observed_missing_handler_is_the_first_unattended_question(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "campaign"
            campaign.seed(make_snapshot(root), out)
            rows = campaign.next_questions(out, top=1, unattended=True)

        self.assertEqual("NATIVE_BOUNDARY", rows[0]["questionType"])
        self.assertEqual("0", rows[0]["priority"])

    def test_hull_only_snapshot_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(campaign.CampaignError, "hull-only"):
                campaign.seed(make_snapshot(root, exact=False), root / "campaign")

    def test_existing_destination_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snapshot = make_snapshot(root)
            out = root / "campaign"
            campaign.seed(snapshot, out)
            with self.assertRaisesRegex(campaign.CampaignError, "refusing existing"):
                campaign.seed(snapshot, out)

    def test_ready_verification_detects_a_tampered_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "campaign"
            campaign.seed(make_snapshot(root), out)
            questions = out / "campaign-questions.tsv"
            questions.write_text(questions.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(campaign.CampaignError, "disagrees"):
                campaign.verify(out)

    def test_boundary_export_is_address_only_and_bound_to_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "campaign"
            export = root / "boundary-export"
            campaign.seed(make_snapshot(root), out)
            receipt = campaign.export_observed_boundaries(out, export)
            verified = campaign.verify_boundary_export(export)

            self.assertEqual(1, receipt["count"])
            self.assertEqual(receipt["targets"], verified["targets"])
            self.assertEqual("0x00402000\n", (export / "boundary-targets.txt").read_text())
            self.assertFalse(receipt["selection"]["namesAuthorized"])

    def test_boundary_export_refuses_overwrite_and_detects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir = root / "campaign"
            export = root / "boundary-export"
            campaign.seed(make_snapshot(root), campaign_dir)
            campaign.export_observed_boundaries(campaign_dir, export, limit=1)
            with self.assertRaisesRegex(campaign.CampaignError, "refusing existing"):
                campaign.export_observed_boundaries(campaign_dir, export, limit=1)

            address_file = export / "boundary-targets.txt"
            address_file.write_text("0x00402001\n", encoding="ascii")
            with self.assertRaisesRegex(campaign.CampaignError, "disagrees"):
                campaign.verify_boundary_export(export)

    def test_native_proposal_import_stays_candidate_and_requires_refuter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir = root / "campaign"
            campaign.seed(make_snapshot(root, native_present=True), campaign_dir)
            proposal = root / "proposal.tsv"
            write_tsv(
                proposal,
                [
                    "handler", "proposedName", "shippedName", "cdbCalls", "traces",
                    "argCountRuntime", "levelsCovered", "bodySpan", "argAccessors",
                    "assertLine", "behaviourNote",
                ],
                [
                    {
                        "handler": "0x00402000", "proposedName": "IScript__FollowWaypoint",
                        "shippedName": "FollowWaypoint", "cdbCalls": "2", "traces": "trace-a",
                        "argCountRuntime": "2", "levelsCovered": "6/66", "bodySpan": "4",
                        "argAccessors": "string+int", "assertLine": "2040",
                        "behaviourNote": "reads a path and mode then dispatches movement",
                    }
                ],
            )
            evidence_doc = root / "evidence.md"
            evidence_doc.write_text("candidate evidence\n", encoding="utf-8")
            out = root / "candidates"
            receipt = campaign.import_native_contract_candidates(
                campaign_dir, proposal, out, evidence_doc
            )
            verified = campaign.verify_native_contract_candidates(out)
            rows = campaign._read_tsv(out / "candidate-contracts.tsv")

        self.assertEqual(1, verified["count"])
        self.assertFalse(receipt["policy"]["namesAuthorized"])
        self.assertTrue(receipt["policy"]["requiresRefuter"])
        self.assertEqual("C1_CANDIDATE_PARTIAL", rows[0]["semanticGrade"])
        self.assertEqual("UNSCORED", rows[0]["refuterVerdict"])

    def test_runtime_contract_import_revalidates_artifacts_and_stays_refuter_gated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence_root = root / "runtime-evidence"
            evidence_root.mkdir()
            specimen = evidence_root / "specimen.exe"
            specimen.write_bytes(b"pristine specimen")
            campaign_dir = root / "campaign"
            campaign.seed(
                make_snapshot(
                    root,
                    native_present=True,
                    native_name="Damage",
                    specimen_sha=sha256(specimen),
                ),
                campaign_dir,
            )
            contract = make_runtime_contract(root, specimen)
            out = root / "runtime-overlay"
            with patch.object(
                campaign.probe_author,
                "verify_manifest",
                return_value=manifest_verification_report(),
            ):
                receipt = campaign.import_runtime_contract(campaign_dir, contract, out)
            verified = campaign.verify_runtime_contract_overlay(out)
            rows = campaign._read_tsv(out / "runtime-contracts.tsv")

        self.assertEqual(1, verified["count"])
        self.assertFalse(receipt["policy"]["namesAuthorized"])
        self.assertFalse(receipt["policy"]["ghidraMutationAuthorized"])
        self.assertFalse(receipt["policy"]["promotionAuthorized"])
        self.assertTrue(receipt["policy"]["requiresRefuter"])
        self.assertEqual("C2_BOUNDED_RUNTIME", rows[0]["semanticGrade"])
        self.assertEqual("UNSCORED", rows[0]["refuterVerdict"])
        self.assertIn("life 0.005", rows[0]["writes"])

    def test_runtime_contract_import_refuses_tampered_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence_root = root / "runtime-evidence"
            evidence_root.mkdir()
            specimen = evidence_root / "specimen.exe"
            specimen.write_bytes(b"pristine specimen")
            campaign_dir = root / "campaign"
            campaign.seed(
                make_snapshot(
                    root,
                    native_present=True,
                    native_name="Damage",
                    specimen_sha=sha256(specimen),
                ),
                campaign_dir,
            )
            contract = make_runtime_contract(root, specimen)
            (evidence_root / "abi.log").write_bytes(b"tampered")
            with self.assertRaisesRegex(campaign.CampaignError, "artifact hash mismatch"):
                campaign.import_runtime_contract(campaign_dir, contract, root / "runtime-overlay")

    def test_runtime_overlay_verification_rechecks_source_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            abi = root / "runtime-evidence" / "abi.log"
            abi.write_bytes(abi.read_bytes() + b"tampered")

            with self.assertRaisesRegex(campaign.CampaignError, "artifact has changed"):
                campaign.verify_runtime_contract_overlay(overlay)

    def test_runtime_import_rejects_a_manifest_verifier_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence_root = root / "runtime-evidence"
            evidence_root.mkdir()
            specimen = evidence_root / "specimen.exe"
            specimen.write_bytes(b"pristine specimen")
            campaign_dir = root / "campaign"
            campaign.seed(
                make_snapshot(
                    root,
                    native_present=True,
                    native_name="Damage",
                    specimen_sha=sha256(specimen),
                ),
                campaign_dir,
            )
            contract = make_runtime_contract(root, specimen)
            with patch.object(
                campaign.probe_author,
                "verify_manifest",
                return_value={"ok": False, "checks": {}},
            ), self.assertRaisesRegex(campaign.CampaignError, "failed independent"):
                campaign.import_runtime_contract(campaign_dir, contract, root / "runtime-overlay")

    def test_holdout_log_requires_exact_fields_clean_markers_and_clean_exit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / "runtime.exe"
            runtime.write_bytes(b"runtime")
            log = root / "holdout.log"
            observation = {
                "callee": "0x00401010",
                "returnAddress": "0x005348e9",
                "receiverVtable": "0x005e24dc",
                "amount": {"bits": "0x447a0000", "float32": 1000.0},
                "damageSource": "NON_NULL",
                "applyShields": 1,
                "meshPartIndex": -1,
            }
            outcome = {
                "requiredMarkers": ["HOLDOUT_SURVIVED", "HOLDOUT_OBSERVER_COMPLETE"],
                "forbiddenMarkers": ["HOLDOUT_REFUTED", "HOLDOUT_MISMATCH", "Syntax error"],
            }
            clean = (
                f"CommandLine: {runtime.resolve()} -skipfmv -forcewindowed -level 100\n"
                "00401010 6aff            push    0FFFFFFFFh\n"
                "Breakpoint 0 hit\n"
                "eip=00401010 esp=001af488\n"
                "HOLDOUT_FIELDS receiver=077a1630 vtable=005e24dc return=005348e9 "
                "amount=447a0000 source=077a6a10 shields=00000001 mesh=ffffffff\n"
                "HOLDOUT_SURVIVED\n"
                "HOLDOUT_OBSERVER_COMPLETE\n"
                "quit:\n"
            )
            log.write_text(clean, encoding="utf-8")
            fields = campaign._validate_holdout_log(
                log,
                runtime_path=runtime.resolve(),
                scope={"level": 100},
                outcome=outcome,
                observation=observation,
                field_prefix="HOLDOUT_FIELDS",
                label="test holdout",
            )
            self.assertEqual("447a0000", fields["amount"])

            log.write_text(clean + "^ Syntax error in observer\n", encoding="utf-8")
            with self.assertRaisesRegex(campaign.CampaignError, "forbidden marker"):
                campaign._validate_holdout_log(
                    log,
                    runtime_path=runtime.resolve(),
                    scope={"level": 100},
                    outcome=outcome,
                    observation=observation,
                    field_prefix="HOLDOUT_FIELDS",
                    label="test holdout",
                )

    def test_survived_runtime_adjudication_closes_only_addressed_question_and_advances(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            before_questions = campaign._read_tsv(campaign_dir / "campaign-questions.tsv")
            addressed = campaign._read_tsv(overlay / "runtime-contracts.tsv")[0][
                "questionIdsAddressed"
            ]
            adjudication = make_runtime_adjudication(
                root, campaign_dir, overlay, "SURVIVED"
            )
            out = root / "campaign-generation-1"
            receipt = campaign.advance_runtime_contract(
                campaign_dir, overlay, adjudication, out
            )
            campaign.verify(out)
            after_questions = campaign._read_tsv(out / "campaign-questions.tsv")
            after_by_id = {row["questionId"]: row for row in after_questions}
            contracts = campaign._read_tsv(out / "campaign-contracts.tsv")
            damage = next(row for row in contracts if row["nativeShippedName"] == "Damage")

        self.assertEqual(1, receipt["generation"])
        self.assertEqual("CLOSED_SURVIVED", after_by_id[addressed]["state"])
        self.assertEqual(
            len(before_questions) + 1,
            len(after_questions),
        )
        untouched = [
            row for row in before_questions if row["questionId"] != addressed
        ]
        self.assertTrue(
            all(after_by_id[row["questionId"]]["state"] == row["state"] for row in untouched)
        )
        self.assertEqual("C2_BOUNDED_RUNTIME", damage["semanticGrade"])
        self.assertEqual("SURVIVED", damage["refuterVerdict"])
        self.assertEqual("PARTIAL_CONTRACT", damage["rebuildState"])

    def test_survived_runtime_adjudication_preserves_prior_evidence_refs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            verified_parent = campaign.verify(campaign_dir)
            verified_overlay = campaign.verify_runtime_contract_overlay(overlay)
            adjudication = make_runtime_adjudication(
                root, campaign_dir, overlay, "SURVIVED"
            )
            contracts_path = campaign_dir / "campaign-contracts.tsv"
            contracts = campaign._read_tsv(contracts_path)
            damage = next(
                row for row in contracts if row["nativeShippedName"] == "Damage"
            )
            prior_ref = "name-proof.ready.json#sha256=" + "e" * 64
            damage["evidenceRefs"] = campaign._append_state(
                damage.get("evidenceRefs", ""), prior_ref
            )
            campaign._write_tsv(
                contracts_path, campaign.CONTRACT_COLUMNS, contracts
            )
            out = root / "campaign-generation-1"
            with patch.object(
                campaign,
                "verify_runtime_contract_overlay",
                return_value=verified_overlay,
            ):
                campaign.advance_runtime_contract(
                    campaign_dir,
                    overlay,
                    adjudication,
                    out,
                    _self_check=False,
                    _verified_parent_receipt=verified_parent,
                )
            advanced = next(
                row
                for row in campaign._read_tsv(out / "campaign-contracts.tsv")
                if row["nativeShippedName"] == "Damage"
            )
            overlay_row = campaign._read_tsv(
                overlay / "runtime-contracts.tsv"
            )[0]

        advanced_refs = set(filter(None, advanced["evidenceRefs"].split(";")))
        self.assertIn(prior_ref, advanced_refs)
        self.assertTrue(
            set(filter(None, overlay_row["evidenceRefs"].split(";")))
            <= advanced_refs
        )

    def test_runtime_adjudication_refuses_arbitrary_entity_supersession(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            adjudication = make_runtime_adjudication(
                root, campaign_dir, overlay, "SURVIVED"
            )
            data = json.loads(adjudication.read_text(encoding="utf-8"))
            overlay_row = campaign._read_tsv(overlay / "runtime-contracts.tsv")[0]
            data["decision"]["supersessions"] = [
                {
                    "oldEntityKey": "NOT_AN_EXACT_ENTITY:wrong-specimen:free-text",
                    "newEntityKey": overlay_row["entityKey"],
                    "kind": "UNBOUND_RUNTIME_ASSERTION",
                    "evidenceRefs": "self-attested",
                }
            ]
            adjudication.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(
                campaign.CampaignError,
                "cannot create entity supersessions",
            ):
                campaign.advance_runtime_contract(
                    campaign_dir,
                    overlay,
                    adjudication,
                    root / "advanced",
                )

    def test_runtime_generation_replays_advance_and_rejects_forged_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            adjudication = make_runtime_adjudication(
                root, campaign_dir, overlay, "SURVIVED"
            )
            out = root / "campaign-generation-1"
            campaign.advance_runtime_contract(
                campaign_dir, overlay, adjudication, out
            )
            ready_path = out / "campaign.ready.json"
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            ready["advance"]["verdict"] = "REFUTED"
            ready_path.write_text(json.dumps(ready), encoding="utf-8")

            with self.assertRaisesRegex(
                campaign.CampaignError, "advance does not reproduce"
            ):
                campaign.verify(out)

    def test_runtime_generation_replay_rejects_false_terminal_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            adjudication = make_runtime_adjudication(
                root, campaign_dir, overlay, "SURVIVED"
            )
            out = root / "campaign-generation-1"
            campaign.advance_runtime_contract(
                campaign_dir, overlay, adjudication, out
            )
            contracts_path = out / "campaign-contracts.tsv"
            contracts = campaign._read_tsv(contracts_path)
            target = next(
                row for row in contracts if row["nativeShippedName"] == "Damage"
            )
            target["contractState"] = "TERMINAL_REBUILD_READY"
            target["rebuildOwner"] = "fake.cs"
            target["parityTests"] = "never-ran"
            target["rebuildState"] = "REBUILD_READY"
            campaign._write_tsv(
                contracts_path, campaign.CONTRACT_COLUMNS, contracts
            )
            ready_path = out / "campaign.ready.json"
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            ready["outputs"]["campaign-contracts.tsv"] = {
                **campaign.coverage.file_stamp(contracts_path),
                "path": "campaign-contracts.tsv",
            }
            ready_path.write_text(json.dumps(ready), encoding="utf-8")

            with self.assertRaisesRegex(
                campaign.CampaignError,
                "does not reproduce from its verified parent and advance",
            ):
                campaign.verify(out)

    def test_unscored_runtime_adjudication_never_promotes_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            overlay_row = campaign._read_tsv(overlay / "runtime-contracts.tsv")[0]
            adjudication = make_runtime_adjudication(
                root, campaign_dir, overlay, "UNSCORED"
            )
            out = root / "campaign-generation-1"
            receipt = campaign.advance_runtime_contract(
                campaign_dir, overlay, adjudication, out
            )
            questions = campaign._read_tsv(out / "campaign-questions.tsv")
            contracts = campaign._read_tsv(out / "campaign-contracts.tsv")
            damage = next(row for row in contracts if row["nativeShippedName"] == "Damage")
            closed = next(
                row for row in questions
                if row["questionId"] == overlay_row["questionIdsAddressed"]
            )

        self.assertEqual("UNSCORED", receipt["advance"]["verdict"])
        self.assertEqual("CLOSED_UNSCORED", closed["state"])
        self.assertEqual("C0_OPAQUE", damage["semanticGrade"])
        self.assertEqual("UNKNOWN", damage["receiver"])
        self.assertEqual("UNASSIGNED", damage["rebuildOwner"])

    def test_refuted_runtime_adjudication_never_promotes_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            overlay_row = campaign._read_tsv(overlay / "runtime-contracts.tsv")[0]
            adjudication = make_runtime_adjudication(
                root, campaign_dir, overlay, "REFUTED"
            )
            out = root / "campaign-generation-1"
            receipt = campaign.advance_runtime_contract(
                campaign_dir, overlay, adjudication, out
            )
            questions = campaign._read_tsv(out / "campaign-questions.tsv")
            contracts = campaign._read_tsv(out / "campaign-contracts.tsv")
            damage = next(row for row in contracts if row["nativeShippedName"] == "Damage")
            closed = next(
                row for row in questions
                if row["questionId"] == overlay_row["questionIdsAddressed"]
            )

        self.assertEqual("REFUTED", receipt["advance"]["verdict"])
        self.assertEqual("CLOSED_REFUTED", closed["state"])
        self.assertEqual("C0_OPAQUE", damage["semanticGrade"])
        self.assertEqual("UNKNOWN", damage["receiver"])
        self.assertEqual("UNASSIGNED", damage["rebuildOwner"])

    def test_runtime_adjudication_refuses_a_mismatched_refuter_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            adjudication = make_runtime_adjudication(
                root, campaign_dir, overlay, "SURVIVED"
            )
            data = json.loads(adjudication.read_text(encoding="utf-8"))
            result = adjudication.parent / data["decision"]["refuterEvidence"][0]["path"]
            result_data = json.loads(result.read_text(encoding="utf-8"))
            result_data["verdict"] = "REFUTED"
            result.write_text(json.dumps(result_data), encoding="utf-8")
            data["decision"]["refuterEvidence"][0]["sha256"] = sha256(result)
            adjudication.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(campaign.CampaignError, "refuter result"):
                campaign.advance_runtime_contract(
                    campaign_dir, overlay, adjudication, root / "advanced"
                )

    def test_survived_generic_refuter_cannot_promote_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            adjudication = make_runtime_adjudication(
                root, campaign_dir, overlay, "SURVIVED"
            )
            data = json.loads(adjudication.read_text(encoding="utf-8"))
            overlay_row = campaign._read_tsv(overlay / "runtime-contracts.tsv")[0]
            result = adjudication.parent / "generic-result.json"
            result.write_text(
                json.dumps(
                    {
                        "schema": campaign.REFUTER_RESULT_SCHEMA,
                        "verdict": "SURVIVED",
                        "baseContractId": overlay_row["baseContractId"],
                        "overlayReadySha256": data["overlayReadySha256"],
                        "questionIdsAddressed": data["decision"]["questionIdsAddressed"],
                        "findings": ["self-attested"],
                        "reason": "no registered refuter tool",
                    }
                ),
                encoding="utf-8",
            )
            data["decision"]["refuterEvidence"] = [
                {
                    "role": "refuter-result",
                    "path": result.name,
                    "sha256": sha256(result),
                }
            ]
            adjudication.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(
                campaign.CampaignError, "mechanically replayed probe refuter"
            ):
                campaign.advance_runtime_contract(
                    campaign_dir, overlay, adjudication, root / "advanced"
                )

    def test_rebuild_ready_refuses_fake_owner_and_unexecuted_test(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            campaign_dir, _contract, overlay = make_imported_runtime_overlay(root)
            adjudication = make_runtime_adjudication(
                root, campaign_dir, overlay, "SURVIVED"
            )
            data = json.loads(adjudication.read_text(encoding="utf-8"))
            decision = data["decision"]
            decision["terminalState"] = "TERMINAL_REBUILD_READY"
            decision["nextQuestions"] = []
            decision["rebuildMapping"] = {
                "rebuildOwner": "fake.cs",
                "rebuildImplementation": "invented",
                "parityTests": "never-ran",
                "rebuildState": "REBUILD_READY",
            }
            adjudication.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(
                campaign.CampaignError, "rebuild-ready gate"
            ):
                campaign.advance_runtime_contract(
                    campaign_dir, overlay, adjudication, root / "advanced"
                )

    def test_rebuild_ready_gate_replays_the_exact_joined_test(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            decision, overlay_row, overlay_sha = make_rebuild_ready_decision(root)
            summary = {
                "exitCode": 0,
                "failed": 0,
                "passed": 1,
                "skipped": 0,
                "total": 1,
            }
            with patch.object(
                campaign, "_run_rebuild_test", return_value=summary
            ) as runner:
                campaign._validate_rebuild_ready_gate(
                    decision, root / "adjudication.json", overlay_row, overlay_sha
                )

            expected_argv = json.loads(
                (root / "rebuild-result.json").read_text(encoding="utf-8")
            )["argv"]
            runner.assert_called_once_with(expected_argv)

    def test_rebuild_runner_parses_the_repo_vstest_multiline_summary(self) -> None:
        text = """
  Passed OnslaughtRebuild.Core.Tests.ExampleTests.One [12 ms]

Test Run Successful.
Total tests: 1
     Passed: 1
 Total time: 0.8107 Seconds
"""
        self.assertEqual((0, 1, 0, 1), campaign._parse_dotnet_test_summary(text))

        ambiguous = text + "\nTotal tests: 1\n"
        with self.assertRaisesRegex(campaign.CampaignError, "ambiguous"):
            campaign._parse_dotnet_test_summary(ambiguous)

    def test_form_complete_rebuild_result_cannot_replace_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            decision, overlay_row, overlay_sha = make_rebuild_ready_decision(root)
            with patch.object(
                campaign,
                "_run_rebuild_test",
                side_effect=campaign.CampaignError("registered runner did not execute"),
            ):
                with self.assertRaisesRegex(
                    campaign.CampaignError, "did not execute"
                ):
                    campaign._validate_rebuild_ready_gate(
                        decision,
                        root / "adjudication.json",
                        overlay_row,
                        overlay_sha,
                    )

    def test_rebuild_ready_gate_must_join_the_declared_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            decision, overlay_row, overlay_sha = make_rebuild_ready_decision(root)
            decision["rebuildMapping"]["parityTests"] = "Unrelated.Test"

            with self.assertRaisesRegex(campaign.CampaignError, "not joined"):
                campaign._validate_rebuild_ready_gate(
                    decision, root / "adjudication.json", overlay_row, overlay_sha
                )

    def test_runtime_import_refuses_duplicate_controls_and_malformed_nested_json(self) -> None:
        for mutation, expected in (
            ("duplicate", "duplicate kinds"),
            ("malformed", "probe.oracle"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                campaign_dir, contract_path, _overlay = make_imported_runtime_overlay(root)
                # Use a fresh destination and delete only the prior generated overlay directory.
                contract = json.loads(contract_path.read_text(encoding="utf-8"))
                if mutation == "duplicate":
                    contract["controls"].append(dict(contract["controls"][0]))
                else:
                    valid_path = contract_path.parent / contract["controls"][0]["receiptPath"]
                    valid = json.loads(valid_path.read_text(encoding="utf-8"))
                    valid["probe"]["oracle"] = []
                    valid_path.write_text(json.dumps(valid), encoding="utf-8")
                    contract["controls"][0]["receiptSha256"] = sha256(valid_path)
                contract_path.write_text(json.dumps(contract), encoding="utf-8")
                with patch.object(
                    campaign.probe_author,
                    "verify_manifest",
                    return_value=manifest_verification_report(),
                ), self.assertRaisesRegex(campaign.CampaignError, expected):
                    campaign.import_runtime_contract(
                        campaign_dir, contract_path, root / "runtime-overlay-second"
                    )

    def test_promotion_ready_v2_requires_exact_instruction_stability_and_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "dry.tsv"
            output.write_text("address\tstatus\n", encoding="utf-8")
            target = root / "targets.txt"
            target.write_text("0x00401000\n0x00402000\n", encoding="ascii")
            tool = root / "CreateFunctionsFromAddressList.java"
            tool.write_text("// promotion tool\n", encoding="utf-8")
            stamp = campaign.coverage.file_stamp(output)
            tool_stamp = campaign.coverage.file_stamp(tool)
            target_sha = "1" * 64
            semantic_sha = "2" * 64
            ready = {
                "schemaVersion": campaign.GHIDRA_PROMOTION_READY_SCHEMA,
                "mode": "dry",
                "tool": {"path": str(tool.resolve()), **tool_stamp},
                "program": {
                    "name": "BEA.exe",
                    "executableMd5": "3b456964020070efe696d2cc09464a55",
                    "executableSha256": (
                        "74154bfae14ddc8ecb87a0766f5bc381"
                        "c7b7f1ab334ed7a753040eda1e1e7750"
                    ),
                    "imageBase": "0x00400000",
                    "language": "x86:LE:32:default",
                    "compilerSpec": "windows",
                },
                "input": {
                    "path": str(target.resolve()),
                    "bytes": target.stat().st_size,
                    "sha256": target_sha,
                    "expectedCount": 2,
                    "semanticTargetSetSha256": semantic_sha,
                },
                "output": {"path": str(output.resolve()), **stamp},
                "counts": {
                    "targets": 2,
                    "wouldCreate": 2,
                    "created": 0,
                    "alreadyExists": 0,
                    "verified": 0,
                    "programInstructionsBefore": 123,
                    "programInstructionsAfter": 123,
                },
                "namesAuthorized": False,
                "mutationCommitted": False,
                "allTargetsVerified": False,
            }
            campaign._validate_promotion_ready(
                ready,
                required_schema=campaign.GHIDRA_PROMOTION_READY_SCHEMA,
                mode="dry",
                target_path=target,
                target_sha256=target_sha,
                target_bytes=target.stat().st_size,
                target_count=2,
                semantic_target_sha256=semantic_sha,
                tool_path=tool,
                tool_stamp=tool_stamp,
                output_path=output,
                output_stamp=stamp,
                label="test dry",
            )

            mutated = json.loads(json.dumps(ready))
            mutated["counts"]["programInstructionsAfter"] = 124
            with self.assertRaisesRegex(campaign.CampaignError, "instruction/count"):
                campaign._validate_promotion_ready(
                    mutated,
                    required_schema=campaign.GHIDRA_PROMOTION_READY_SCHEMA,
                    mode="dry",
                    target_path=target,
                    target_sha256=target_sha,
                    target_bytes=target.stat().st_size,
                    target_count=2,
                    semantic_target_sha256=semantic_sha,
                    tool_path=tool,
                    tool_stamp=tool_stamp,
                    output_path=output,
                    output_stamp=stamp,
                    label="test dry",
                )

            missing_sha = json.loads(json.dumps(ready))
            del missing_sha["program"]["executableSha256"]
            with self.assertRaisesRegex(campaign.CampaignError, "another program identity"):
                campaign._validate_promotion_ready(
                    missing_sha,
                    required_schema=campaign.GHIDRA_PROMOTION_READY_SCHEMA,
                    mode="dry",
                    target_path=target,
                    target_sha256=target_sha,
                    target_bytes=target.stat().st_size,
                    target_count=2,
                    semantic_target_sha256=semantic_sha,
                    tool_path=tool,
                    tool_stamp=tool_stamp,
                    output_path=output,
                    output_stamp=stamp,
                    label="test dry",
                )

    def test_promotion_log_is_bound_to_project_and_rejects_lost_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_root = Path(temporary).resolve()
            target = project_root / "targets.txt"
            output = project_root / "dry.tsv"
            ready = project_root / "dry.ready.json"
            tool = project_root / "CreateFunctionsFromAddressList.java"
            tool.write_text("// promotion tool\n", encoding="utf-8")
            tool_stamp = campaign.coverage.file_stamp(tool)
            log = "\n".join(
                [
                    f"Opening existing project: {project_root / 'BEA'} (HeadlessAnalyzer)",
                    "REPORT: Processing read-only project file: /BEA.exe",
                    (
                        "REPORT: Execute script: CreateFunctionsFromAddressList.java "
                        f"'{target}' '{'1' * 64}' '2' '{output}' '{ready}' 'dry'"
                    ),
                    f"SCRIPT: {tool} (HeadlessAnalyzer)",
                    (
                        f"FUNCTION_PROMOTION_TOOL_OK path={tool} "
                        f"bytes={tool_stamp['bytes']} sha256={tool_stamp['sha256']}"
                    ),
                    (
                        "FUNCTION_PROMOTION_PROGRAM_OK name=BEA.exe "
                        "md5=3b456964020070efe696d2cc09464a55 "
                        "sha256=74154bfae14ddc8ecb87a0766f5bc381"
                        "c7b7f1ab334ed7a753040eda1e1e7750 "
                        "imageBase=0x00400000 language=x86:LE:32:default compiler=windows"
                    ),
                    (
                        "FUNCTION_PROMOTION_OK mode=dry targets=2 would_create=2 "
                        "created=0 already_exists=0 verified=0 mutation_committed=false"
                    ),
                ]
            )
            campaign._validate_promotion_log(
                log,
                ready_schema=campaign.GHIDRA_PROMOTION_READY_SCHEMA,
                mode="dry",
                target_path=target,
                target_sha256="1" * 64,
                target_count=2,
                output_path=output,
                ready_path=ready,
                tool_path=tool,
                tool_stamp=tool_stamp,
                expected_project_root=project_root,
                project_name="BEA",
                require_save=False,
                label="test dry",
            )
            with self.assertRaisesRegex(campaign.CampaignError, "another project path"):
                campaign._validate_promotion_log(
                    log,
                    ready_schema=campaign.GHIDRA_PROMOTION_READY_SCHEMA,
                    mode="dry",
                    target_path=target,
                    target_sha256="1" * 64,
                    target_count=2,
                    output_path=output,
                    ready_path=ready,
                    tool_path=tool,
                    tool_stamp=tool_stamp,
                    expected_project_root=project_root / "other",
                    project_name="BEA",
                    require_save=False,
                    label="test dry",
                )
            with self.assertRaisesRegex(campaign.CampaignError, "script error marker"):
                campaign._validate_promotion_log(
                    log + "\nFUNCTION_PROMOTION_RECEIPT_LOST",
                    ready_schema=campaign.GHIDRA_PROMOTION_READY_SCHEMA,
                    mode="dry",
                    target_path=target,
                    target_sha256="1" * 64,
                    target_count=2,
                    output_path=output,
                    ready_path=ready,
                    tool_path=tool,
                    tool_stamp=tool_stamp,
                    expected_project_root=project_root,
                    project_name="BEA",
                    require_save=False,
                    label="test dry",
                )

    def test_promotion_independent_artifacts_may_not_alias(self) -> None:
        shared = Path("shared.tsv").resolve()
        with self.assertRaisesRegex(campaign.CampaignError, "aliases independent artifacts"):
            campaign._require_distinct_artifact_paths(
                {"scratch functions": shared, "live functions": shared}
            )

    def test_poisoned_sha_allows_raw_rollover_but_never_semantic_inventory_drift(self) -> None:
        pre_rows = [("BEA.gpr", 0, "1" * 64), ("db.1.gbf", 10, "2" * 64)]
        rolled_rows = [("BEA.gpr", 0, "1" * 64), ("db.2.gbf", 10, "3" * 64)]
        functions = {"sha256": "4" * 64}
        program = {"sha256": "5" * 64}

        self.assertTrue(
            campaign._validate_poisoned_sha_semantic_stability(
                reported_raw_project_changed=True,
                pre_project_rows=pre_rows,
                post_project_rows=rolled_rows,
                before_functions_stamp=functions,
                after_functions_stamp=functions,
                before_program_stamp=program,
                after_program_stamp=program,
            )
        )
        self.assertFalse(
            campaign._validate_poisoned_sha_semantic_stability(
                reported_raw_project_changed=False,
                pre_project_rows=pre_rows,
                post_project_rows=pre_rows,
                before_functions_stamp=functions,
                after_functions_stamp=functions,
                before_program_stamp=program,
                after_program_stamp=program,
            )
        )
        with self.assertRaisesRegex(campaign.CampaignError, "raw-project observation"):
            campaign._validate_poisoned_sha_semantic_stability(
                reported_raw_project_changed=False,
                pre_project_rows=pre_rows,
                post_project_rows=rolled_rows,
                before_functions_stamp=functions,
                after_functions_stamp=functions,
                before_program_stamp=program,
                after_program_stamp=program,
            )
        for field in ("functions", "program"):
            with self.subTest(field=field), self.assertRaisesRegex(
                campaign.CampaignError, "semantic function/program"
            ):
                campaign._validate_poisoned_sha_semantic_stability(
                    reported_raw_project_changed=True,
                    pre_project_rows=pre_rows,
                    post_project_rows=rolled_rows,
                    before_functions_stamp=functions,
                    after_functions_stamp=(
                        {"sha256": "6" * 64} if field == "functions" else functions
                    ),
                    before_program_stamp=program,
                    after_program_stamp=(
                        {"sha256": "7" * 64} if field == "program" else program
                    ),
                )

    def test_promotion_advance_preserves_reproduced_schema_tool_and_artifact_provenance(self) -> None:
        def stamp(value: str) -> dict:
            return {"path": f"{value}.json", "bytes": len(value), "sha256": value * 64}

        validated = {
            "preregistrationStamp": stamp("1"),
            "targetStamp": stamp("2"),
            "toolStamp": stamp("3"),
            "toolProvenance": {
                "declaredExecutionPath": "C:/repo/tools/CreateFunctionsFromAddressList.java",
                "verifiedContentPath": "C:/evidence/CreateFunctionsFromAddressList.java",
                "historicalFallbackUsed": True,
            },
            "evidenceSchema": campaign.LEGACY_GHIDRA_PROMOTION_EVIDENCE_SCHEMA,
            "legacyBridgeUsed": True,
            "backupOpenStamp": stamp("4"),
            "liveApply": {"tsvPath": Path("apply.tsv"), "tsv": stamp("5"), "ready": stamp("6")},
            "liveReadback": {
                "tsvPath": Path("readback.tsv"),
                "tsv": stamp("7"),
                "ready": stamp("8"),
            },
            "afterFunctionsStamp": stamp("9"),
            "liveDiffStamp": stamp("a"),
        }
        advance = {
            "preregistration": validated["preregistrationStamp"],
            "targets": validated["targetStamp"],
            "tool": validated["toolStamp"],
            "toolProvenance": validated["toolProvenance"],
            "evidenceSchema": validated["evidenceSchema"],
            "legacyBridgeUsed": True,
            "backup": validated["backupOpenStamp"],
            "liveApply": {"tsv": stamp("5"), "ready": stamp("6")},
            "liveReadback": {"tsv": stamp("7"), "ready": stamp("8")},
            "liveAfterFunctions": validated["afterFunctionsStamp"],
            "liveInventoryDiff": validated["liveDiffStamp"],
        }
        campaign._require_exact_promotion_advance_provenance(advance, validated)

        for field, forged in (
            ("evidenceSchema", "forged.v999"),
            ("legacyBridgeUsed", False),
            (
                "toolProvenance",
                {**advance["toolProvenance"], "historicalFallbackUsed": False},
            ),
            ("liveInventoryDiff", stamp("b")),
        ):
            with self.subTest(field=field):
                mutated = json.loads(json.dumps(advance))
                mutated[field] = forged
                with self.assertRaisesRegex(campaign.CampaignError, field):
                    campaign._require_exact_promotion_advance_provenance(mutated, validated)

    def test_promotion_rehashes_backup_project_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "BEA.gpr").write_bytes(b"")
            idata = root / "BEA.rep" / "idata"
            database = idata / "00" / "~00000000.db"
            database.mkdir(parents=True)
            (idata / "~index.dat").write_bytes(b"index")
            payload = database / "db.1.gbf"
            payload.write_bytes(b"database")
            manifest = campaign.ghidra_backup.build_manifest(root, "BEA")
            expected = [
                (row.relative_path, row.size, row.sha256) for row in manifest.files
            ]
            campaign._verify_project_manifest_bytes(root, expected, "BEA", "test backup")
            payload.write_bytes(b"tampered")
            with self.assertRaisesRegex(campaign.CampaignError, "bytes differ"):
                campaign._verify_project_manifest_bytes(root, expected, "BEA", "test backup")


class ResidualSupersessionRelationTests(unittest.TestCase):
    def relation_fixture(self) -> tuple[dict[str, list[dict]], dict, str, str]:
        specimen = "a" * 64
        range_digest = hashlib.sha256(
            json.dumps([(0x2A00, 0x2AC3)], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        old = f"TEXT_RESIDUAL:{specimen}:0x00402A00-0x00402AC3"
        new = f"CODE:{specimen}:VA=0x00402a00:RANGES={range_digest}"
        question_id = "Q-test"
        contract_id = "C-test"
        supersession_id = "S-" + campaign._sha256_text(old + "|" + new)[:16]
        rows = {
            "functions": [{
                "entityKey": new,
                "entryVa": "0x00402a00",
                "entryRva": "0x00002a00",
                "bodyRangesRva": "0x2a00-0x2ac3",
                "bodyRangeSetSha256": range_digest,
                "bodyBytes": "195",
                "evidenceStates": "BASELINE_STATIC;MAINTAINER_GHIDRA_BOUNDARY_PROMOTED",
            }],
            "residuals": [],
            "questions": [{
                "questionId": question_id,
                "entityKey": new,
                "generation": "1",
                "state": "OPEN",
            }],
            "contracts": [{
                "contractId": contract_id,
                "entityKey": new,
                "entityKind": "FUNCTION",
                "questionIds": question_id,
                "supersedesEntityKeys": old,
            }],
            "adjudications": [],
            "supersessions": [{
                "supersessionId": supersession_id,
                "oldEntityKey": old,
                "newEntityKey": new,
                "kind": campaign.GHIDRA_RESIDUAL_ADVANCE_KIND,
                "verdict": "SURVIVED",
                "evidenceRefs": "evidence.json#sha256=" + "c" * 64,
                "measuredAtUtc": "2026-08-03T12:00:00+00:00",
            }],
        }
        receipt = {
            "sourceSnapshot": {
                "specimen": {"sha256": specimen},
                "parityGraph": {"program": {"imageBase": "0x00400000"}},
            }
        }
        return rows, receipt, old, new

    def test_exact_text_residual_to_code_relation_passes(self) -> None:
        rows, receipt, _old, _new = self.relation_fixture()
        campaign._validate_campaign_relations(rows, receipt)

    def test_residual_and_native_supersession_kinds_cannot_alias(self) -> None:
        attacks = []
        rows, receipt, old, new = self.relation_fixture()
        rows["supersessions"][0]["kind"] = campaign.GHIDRA_ADVANCE_KIND
        attacks.append(rows)

        rows, _receipt, _old, _new = self.relation_fixture()
        rows["supersessions"][0]["oldEntityKey"] = (
            f"CODE_CANDIDATE:{'a' * 64}:VA=0x00402a00"
        )
        rows["contracts"][0]["supersedesEntityKeys"] = rows["supersessions"][0]["oldEntityKey"]
        rows["supersessions"][0]["supersessionId"] = "S-" + campaign._sha256_text(
            rows["supersessions"][0]["oldEntityKey"] + "|" + new
        )[:16]
        attacks.append(rows)

        for poisoned in attacks:
            with self.subTest(kind=poisoned["supersessions"][0]["kind"]):
                with self.assertRaisesRegex(campaign.CampaignError, "invalid supersession"):
                    campaign._validate_campaign_relations(poisoned, receipt)

    def test_residual_relation_rejects_range_digest_size_and_marker_attacks(self) -> None:
        mutations = (
            ("bodyRangeSetSha256", "d" * 64),
            ("bodyBytes", "194"),
            ("evidenceStates", "BASELINE_STATIC"),
        )
        for field, value in mutations:
            rows, receipt, _old, _new = self.relation_fixture()
            rows["functions"][0][field] = value
            with self.subTest(field=field):
                with self.assertRaisesRegex(campaign.CampaignError, "invalid supersession"):
                    campaign._validate_campaign_relations(rows, receipt)

    def test_residual_relation_rejects_wrong_range_and_noncanonical_identity(self) -> None:
        mutations = (
            ("entryVa", "0x00402a01"),
            ("entryRva", "0x00002a01"),
            ("bodyRangesRva", "0x2a01-0x2ac4"),
        )
        for field, value in mutations:
            rows, receipt, _old, _new = self.relation_fixture()
            rows["functions"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(
                campaign.CampaignError, "invalid supersession"
            ):
                campaign._validate_campaign_relations(rows, receipt)

        rows, receipt, old, new = self.relation_fixture()
        poisoned_old = old.replace("0x00402A00", "0X00402A00")
        rows["supersessions"][0]["oldEntityKey"] = poisoned_old
        rows["contracts"][0]["supersedesEntityKeys"] = poisoned_old
        rows["supersessions"][0]["supersessionId"] = "S-" + campaign._sha256_text(
            poisoned_old + "|" + new
        )[:16]
        with self.assertRaisesRegex(campaign.CampaignError, "invalid supersession"):
            campaign._validate_campaign_relations(rows, receipt)

        rows, receipt, old, new = self.relation_fixture()
        poisoned_old = old.replace("0x00402A00", "0x00402a00")
        rows["supersessions"][0]["oldEntityKey"] = poisoned_old
        rows["contracts"][0]["supersedesEntityKeys"] = poisoned_old
        rows["supersessions"][0]["supersessionId"] = "S-" + campaign._sha256_text(
            poisoned_old + "|" + new
        )[:16]
        with self.assertRaisesRegex(campaign.CampaignError, "invalid supersession"):
            campaign._validate_campaign_relations(rows, receipt)

    def test_residual_relation_rejects_live_old_entity_and_specimen_drift(self) -> None:
        rows, receipt, old, _new = self.relation_fixture()
        rows["residuals"].append({"entityKey": old})
        rows["questions"].append({
            "questionId": "Q-old",
            "entityKey": old,
            "generation": "1",
            "state": "OPEN",
        })
        rows["contracts"].append({
            "contractId": "C-old",
            "entityKey": old,
            "entityKind": "TEXT_RESIDUAL",
            "questionIds": "Q-old",
            "supersedesEntityKeys": "",
        })
        with self.assertRaisesRegex(campaign.CampaignError, "invalid supersession"):
            campaign._validate_campaign_relations(rows, receipt)

        rows, receipt, _old, _new = self.relation_fixture()
        receipt["sourceSnapshot"]["specimen"]["sha256"] = "d" * 64
        with self.assertRaisesRegex(campaign.CampaignError, "invalid supersession"):
            campaign._validate_campaign_relations(rows, receipt)


def v5_carry_reducer_restored_byte_exact() -> bool:
    """Require every receipt-bound reducer byte, not merely marker absence."""

    root = campaign.FROZEN_V5_CAMPAIGN_CARRY_ROOT
    ready_path = root / "campaign.ready.json"
    if (
        not ready_path.is_file()
        or sha256(ready_path) != campaign.FROZEN_V5_CAMPAIGN_CARRY_READY_SHA256
    ):
        return False
    try:
        ready = json.loads(ready_path.read_text(encoding="utf-8"))
        reducer = ready["reducer"]
        files = reducer["files"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return False
    if reducer.get("id") != campaign.FROZEN_V5_CAMPAIGN_CARRY_REDUCER_ID:
        return False
    for row in files:
        try:
            path = root / row["path"]
            if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
                return False
        except (OSError, KeyError, TypeError):
            return False
    return campaign._reducer_id(files) == reducer["id"]


def require_v5_carry_reducer(test_method):
    """Skip a test that replays the strict frozen v5 carry reducer snapshot."""

    @functools.wraps(test_method)
    def wrapper(self, *args, **kwargs):
        if not v5_carry_reducer_restored_byte_exact():
            self.skipTest(
                "frozen v5 carry reducer does not match all receipt-bound bytes"
            )
        return test_method(self, *args, **kwargs)

    return wrapper


def missing_atomic14_replay_inputs() -> list[str]:
    """List exact external inputs still absent from the historical Gen8 replay."""

    root = (
        Path(__file__).resolve().parent.parent
        / "local-lab/console-callback-atomic14-post-campaign-20260803-v1"
        / "generation-8-live-promoted"
    )
    try:
        ready = json.loads((root / "campaign.ready.json").read_text(encoding="utf-8"))
        advance = ready["advance"]
        stamps = {
            field: advance[field]
            for field in ("liveReady", "formalReady", "targets", "padding", "parityExport")
        }
        snapshot = advance["snapshot"]
        stamps["snapshot.ready"] = {
            **snapshot["ready"],
            "path": str(Path(snapshot["root"]) / snapshot["ready"]["path"]),
        }
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return ["Generation 8 advance receipt"]
    missing = []
    for label, stamp in stamps.items():
        try:
            path = Path(stamp["path"])
            if path.stat().st_size != stamp["bytes"] or sha256(path) != stamp["sha256"]:
                missing.append(label)
        except (OSError, KeyError, TypeError):
            missing.append(label)
    return missing


def require_atomic14_replay_inputs(test_method):
    """Skip only tests whose claim actually needs the lost Atomic14 inputs."""

    @functools.wraps(test_method)
    def wrapper(self, *args, **kwargs):
        missing = missing_atomic14_replay_inputs()
        if missing:
            self.skipTest(
                "exact Atomic14 replay inputs are unavailable: " + ", ".join(missing)
            )
        return test_method(self, *args, **kwargs)

    return wrapper


class GlobalInit515ResidualAdvanceTests(unittest.TestCase):
    @staticmethod
    def stamp(root: Path, path: Path) -> dict:
        measured = campaign.coverage.file_stamp(path)
        return {
            "path": path.relative_to(root).as_posix(),
            "bytes": measured["bytes"],
            "sha256": measured["sha256"],
        }

    def make_process(
        self,
        root: Path,
        name: str,
        *,
        argv: list[str] | None = None,
        log_text: str = "ok\n",
        started_at: str = "2026-08-03T00:00:00Z",
        completed_at: str = "2026-08-03T00:00:01Z",
    ) -> dict:
        run_root = root / "runs" / name
        run_root.mkdir(parents=True, exist_ok=True)
        context = campaign._global_init515_expected_process_context(root)
        Path(str(context["cwd"])).mkdir(parents=True, exist_ok=True)
        environment = context["environment"]
        for key in ("APPDATA", "LOCALAPPDATA", "TEMP", "USERPROFILE"):
            Path(str(environment[key])).mkdir(parents=True, exist_ok=True)
        java_home = (
            Path(str(environment["APPDATA"]))
            / "ghidra/ghidra_12.1.2_PUBLIC/java_home.save"
        )
        java_home.parent.mkdir(parents=True, exist_ok=True)
        if not java_home.exists():
            java_home.write_bytes(f"{environment['JAVA_HOME']}\r\n".encode())
        log = run_root / "headless.partial.log"
        log.write_text(log_text, encoding="utf-8")
        receipt = {
            "schema": campaign.GLOBAL_INIT515_PROCESS_SCHEMA,
            "id": name,
            "startedAtUtc": started_at,
            "completedAtUtc": completed_at,
            "argv": argv or [name],
            "cwd": context["cwd"],
            "environment": environment,
            "status": "COMPLETED",
            "exitCode": 0,
            "error": "",
            "readerError": "",
            "log": self.stamp(root, log),
        }
        receipt_path = run_root / "run.json"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        return self.stamp(root, receipt_path)

    @staticmethod
    def make_project(root: Path, *, payload: bytes = b"database payload") -> dict:
        root.mkdir(parents=True)
        (root / "BEA.gpr").write_bytes(b"")
        database = root / "BEA.rep" / "idata" / "00" / "~00000000.db"
        database.mkdir(parents=True)
        (root / "BEA.rep" / "idata" / "~index.dat").write_bytes(b"index")
        (database / "db.1.gbf").write_bytes(payload)
        manifest = campaign.ghidra_backup.build_manifest(root, "BEA")
        rows = [
            (row.relative_path, row.size, row.sha256)
            for row in manifest.files
        ]
        canonical = "".join(
            f"{digest}\t{size}\t{relative}\n"
            for relative, size, digest in sorted(rows)
        )
        return {
            "root": str(root.resolve()),
            "fileCount": len(rows),
            "totalBytes": sum(row[1] for row in rows),
            "fileSetSha256": hashlib.sha256(canonical.encode()).hexdigest(),
            "files": [
                {"path": relative, "bytes": size, "sha256": digest}
                for relative, size, digest in rows
            ],
        }

    @staticmethod
    def write_backup_manifest(path: Path, snapshot: dict, created_at: str) -> None:
        project = {
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
        comparison = {
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
        path.write_text(
            json.dumps(
                {
                    "schemaVersion": "onslaught-ghidra-project-backup.v2",
                    "createdAtUtc": created_at,
                    "source": project,
                    "destination": project,
                    "sourceStable": True,
                    "copyComparison": comparison,
                    "readonlyOpen": None,
                }
            ),
            encoding="utf-8",
        )

    def make_observation(
        self,
        root: Path,
        name: str,
        project_root: Path,
        snapshot: dict,
        artifacts: dict[str, dict],
        *,
        headless: Path,
        inventory_tool: Path,
        symbol_tool: Path,
        manifest: Path,
        inventory_started_at: str,
        inventory_completed_at: str,
        symbol_started_at: str,
        symbol_completed_at: str,
        observed_at: str,
        state: str = "POST",
    ) -> dict:
        inventory_root = root / "runs" / f"{name}-inventory"
        symbol_root = root / "runs" / f"{name}-symbols"
        inventory_root.mkdir(parents=True, exist_ok=True)
        symbol_root.mkdir(parents=True, exist_ok=True)

        source_paths = {
            field: root / artifacts[field]["path"]
            for field in ("functions", "program", "symbols", "symbolsReady")
        }
        local_paths = {
            "functions": inventory_root / "functions.tsv",
            "program": inventory_root / "program.tsv",
            "symbols": symbol_root / "target-symbols.tsv",
            "symbolsReady": symbol_root / "target-symbols.ready.json",
        }
        for field in ("functions", "program", "symbols"):
            shutil.copyfile(source_paths[field], local_paths[field])

        symbols_ready = json.loads(source_paths["symbolsReady"].read_text(encoding="utf-8"))
        symbol_stamp = campaign.coverage.file_stamp(local_paths["symbols"])
        symbols_ready["output"] = {
            "path": str(local_paths["symbols"].resolve()),
            "bytes": symbol_stamp["bytes"],
            "sha256": symbol_stamp["sha256"],
        }
        local_paths["symbolsReady"].write_text(json.dumps(symbols_ready), encoding="utf-8")
        local_artifacts = {
            field: self.stamp(root, path) for field, path in local_paths.items()
        }

        inventory_argv = campaign._global_init515_windows_batch_argv(
            headless,
            [
                str(project_root.resolve()),
                "BEA",
                "-process",
                "BEA.exe",
                "-readOnly",
                "-noanalysis",
                "-scriptPath",
                str(inventory_tool.resolve().parent),
                "-postScript",
                inventory_tool.name,
                str(local_paths["functions"].resolve()),
                str(local_paths["program"].resolve()),
            ],
        )
        symbol_argv = campaign._global_init515_windows_batch_argv(
            headless,
            [
                str(project_root.resolve()),
                "BEA",
                "-process",
                "BEA.exe",
                "-readOnly",
                "-noanalysis",
                "-scriptPath",
                str(symbol_tool.resolve().parent),
                "-postScript",
                symbol_tool.name,
                str(manifest.resolve()),
                campaign.coverage.sha256_of(manifest),
                str(campaign.GLOBAL_INIT515_COUNT),
                str(local_paths["symbols"].resolve()),
                str(local_paths["symbolsReady"].resolve()),
            ],
        )
        inventory_marker = (
            f"INVENTORY_TOOL_OK path={inventory_tool.resolve()} "
            f"bytes={inventory_tool.stat().st_size} "
            f"sha256={campaign.coverage.sha256_of(inventory_tool)}\n"
        )
        symbol_marker = (
            f"TARGET_SYMBOL_TOOL_OK path={symbol_tool.resolve()} "
            f"bytes={symbol_tool.stat().st_size} "
            f"sha256={campaign.coverage.sha256_of(symbol_tool)}\n"
        )
        observation = {
            "schema": campaign.GLOBAL_INIT515_LIVE_OBSERVATION_SCHEMA,
            "label": name,
            "observedAtUtc": observed_at,
            "projectRoot": str(project_root.resolve()),
            "rawBefore": {**snapshot, "root": str(project_root.resolve())},
            "rawAfter": {**snapshot, "root": str(project_root.resolve())},
            "rawStable": True,
            **local_artifacts,
            "inventoryRun": self.make_process(
                root,
                f"{name}-inventory",
                argv=inventory_argv,
                log_text=inventory_marker,
                started_at=inventory_started_at,
                completed_at=inventory_completed_at,
            ),
            "symbolRun": self.make_process(
                root,
                f"{name}-symbols",
                argv=symbol_argv,
                log_text=symbol_marker,
                started_at=symbol_started_at,
                completed_at=symbol_completed_at,
            ),
            "classification": {"state": state, "reasons": []},
        }
        path = root / "observations" / f"{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(observation), encoding="utf-8")
        return self.stamp(root, path)

    def make_state_artifacts(
        self,
        *,
        receipt_root: Path,
        artifact_root: Path,
        state: str,
        symbol_tool: Path,
        manifest: Path,
        exact_sources: dict[str, Path] | None = None,
    ) -> tuple[dict[str, dict], dict[str, str]]:
        artifact_root.mkdir(parents=True)
        paths: dict[str, Path] = {}
        for name, payload in (
            ("functions", f"{state.lower()}-functions".encode()),
            ("program", f"{state.lower()}-program".encode()),
            ("symbols", f"{state.lower()}-symbols".encode()),
        ):
            path = artifact_root / f"{name}.dat"
            if exact_sources is not None:
                shutil.copyfile(exact_sources[name], path)
            else:
                path.write_bytes(payload)
            paths[name] = path

        def external(path: Path) -> dict:
            measured = campaign.coverage.file_stamp(path)
            return {
                "path": str(path.resolve()),
                "bytes": measured["bytes"],
                "sha256": measured["sha256"],
            }

        counts = (
            {
                "targets": campaign.GLOBAL_INIT515_COUNT,
                "targetSymbols": 513,
                "zeroSymbols": 2,
                "dynamicDefaultLabels": 513,
                "nonDynamicDefaultFunctions": 0,
                "outsideTargetSymbols": 86091,
            }
            if state == "PRE"
            else {
                "targets": campaign.GLOBAL_INIT515_COUNT,
                "targetSymbols": 515,
                "zeroSymbols": 0,
                "dynamicDefaultLabels": 0,
                "nonDynamicDefaultFunctions": 515,
                "outsideTargetSymbols": 86091,
            }
        )
        symbols_ready = artifact_root / "symbolsReady.dat"
        symbols_ready.write_text(
            json.dumps(
                {
                    "schemaVersion": "bea.re.ghidra-target-symbol-inventory.v1",
                    "program": {
                        "name": "BEA.exe",
                        "md5": "3b456964020070efe696d2cc09464a55",
                        "sha256": campaign.FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256,
                        "imageBase": "0x00400000",
                        "language": "x86:LE:32:default",
                        "compilerSpec": "windows",
                    },
                    "tool": external(symbol_tool),
                    "manifest": {
                        **external(manifest),
                        "expectedCount": campaign.GLOBAL_INIT515_COUNT,
                    },
                    "output": external(paths["symbols"]),
                    "counts": counts,
                    "outsideTargetSymbolsSha256": campaign.GLOBAL_INIT515_OUTSIDE_SYMBOLS_SHA256,
                }
            ),
            encoding="utf-8",
        )
        paths["symbolsReady"] = symbols_ready
        artifacts = {
            name: self.stamp(receipt_root, path) for name, path in paths.items()
        }
        hashes = {
            name: campaign.coverage.sha256_of(paths[name])
            for name in ("functions", "program", "symbols")
        }
        return artifacts, hashes

    def make_live_ready(
        self,
        root: Path,
        *,
        exact_post_artifacts: bool = False,
        pre_equals_post: bool = False,
    ) -> tuple[Path, dict[str, str], Path]:
        root.mkdir(parents=True, exist_ok=True)
        owner_root = root.parent
        live_root = Path(r"C:\Users\david\Ghidra\Projects")
        formal_root = (
            Path(__file__).resolve().parent.parent
            / "local-lab/formal-global-init515-proof-20260803-v4"
        )
        if exact_post_artifacts:
            apply_tool = formal_root / "tools/CreateFunctionsFromBoundaryManifest.java"
            inventory_tool = formal_root / "tools/ExportFullFunctionInventory.java"
            symbol_tool = formal_root / "tools/ExportTargetSymbolInventory.java"
            apply_manifest = formal_root / "inputs/admissible515.tsv"
            headless = campaign.GLOBAL_INIT515_ANALYZE_HEADLESS_PATH
            pre_sources = {
                "functions": formal_root / "inputs/base-functions.tsv",
                "program": formal_root / "inputs/base-program.tsv",
                "symbols": formal_root
                / "runs/source-target-symbols-before/target-symbols.tsv",
            }
            post_sources = {
                "functions": formal_root
                / "runs/replica-a-apply-reopened/functions.tsv",
                "program": formal_root / "runs/replica-a-apply-reopened/program.tsv",
                "symbols": formal_root
                / "runs/replica-a-target-symbols/target-symbols.tsv",
            }
        else:
            inputs = owner_root / "authority-inputs"
            inputs.mkdir()
            apply_tool = inputs / "CreateFunctionsFromBoundaryManifest.java"
            inventory_tool = inputs / "ExportFullFunctionInventory.java"
            symbol_tool = inputs / "ExportTargetSymbolInventory.java"
            apply_manifest = inputs / "admissible515.tsv"
            headless = inputs / "analyzeHeadless.bat"
            apply_tool.write_text("// synthetic exact envelope tool\n", encoding="utf-8")
            inventory_tool.write_text("// synthetic exact inventory tool\n", encoding="utf-8")
            symbol_tool.write_text("// synthetic exact symbol tool\n", encoding="utf-8")
            apply_manifest.write_text("synthetic exact manifest\n", encoding="utf-8")
            headless.write_text("@echo synthetic headless\n", encoding="utf-8")
            pre_sources = None
            post_sources = None

        pre_payload = (
            b"distinct POST database payload"
            if pre_equals_post
            else b"distinct PRE database payload"
        )
        pre_snapshot = self.make_project(
            owner_root / "pre-project", payload=pre_payload
        )
        pre_backup_root = owner_root / "backups" / "pre-live"
        pre_restore_root = owner_root / "backups" / "pre-live-restore-drill"
        pre_backup_snapshot = self.make_project(
            pre_backup_root, payload=pre_payload
        )
        pre_restore_snapshot = self.make_project(
            pre_restore_root, payload=pre_payload
        )
        backup_root = root / "backups" / "post-live"
        restore_root = root / "backups" / "post-live-restore-drill"
        backup_snapshot = self.make_project(
            backup_root, payload=b"distinct POST database payload"
        )
        restore_snapshot = self.make_project(
            restore_root, payload=b"distinct POST database payload"
        )
        self.assertEqual(
            campaign._project_snapshot_identity(backup_snapshot, "backup"),
            campaign._project_snapshot_identity(restore_snapshot, "restore"),
        )
        self.assertEqual(
            campaign._project_snapshot_identity(pre_snapshot, "pre"),
            campaign._project_snapshot_identity(pre_backup_snapshot, "pre backup"),
        )
        self.assertEqual(
            campaign._project_snapshot_identity(pre_snapshot, "pre"),
            campaign._project_snapshot_identity(pre_restore_snapshot, "pre restore"),
        )

        pre_artifacts, pre_hashes = self.make_state_artifacts(
            receipt_root=owner_root,
            artifact_root=owner_root / "pre-artifacts",
            state="PRE",
            symbol_tool=symbol_tool,
            manifest=apply_manifest,
            exact_sources=pre_sources,
        )
        artifacts, post_hashes = self.make_state_artifacts(
            receipt_root=root,
            artifact_root=root / "artifacts",
            state="POST",
            symbol_tool=symbol_tool,
            manifest=apply_manifest,
            exact_sources=post_sources,
        )
        hashes = {
            "functions": post_hashes["functions"],
            "program": post_hashes["program"],
            "symbols": post_hashes["symbols"],
            "preFunctions": pre_hashes["functions"],
            "preProgram": pre_hashes["program"],
            "preSymbols": pre_hashes["symbols"],
            "preFileSet": pre_snapshot["fileSetSha256"],
            "envelopeToolPath": str(apply_tool.resolve()),
            "inventoryToolPath": str(inventory_tool.resolve()),
            "symbolToolPath": str(symbol_tool.resolve()),
            "manifestPath": str(apply_manifest.resolve()),
            "headlessPath": str(headless.resolve()),
            "symbolTool": campaign.coverage.sha256_of(symbol_tool),
            "inventoryTool": campaign.coverage.sha256_of(inventory_tool),
            "headless": campaign.coverage.sha256_of(headless),
        }
        live_observation = self.make_observation(
            root,
            "live-post-attempt",
            live_root,
            backup_snapshot,
            artifacts,
            headless=headless,
            inventory_tool=inventory_tool,
            symbol_tool=symbol_tool,
            manifest=apply_manifest,
            inventory_started_at="2026-08-03T10:11:00Z",
            inventory_completed_at="2026-08-03T10:12:00Z",
            symbol_started_at="2026-08-03T10:13:00Z",
            symbol_completed_at="2026-08-03T10:14:00Z",
            observed_at="2026-08-03T10:15:00Z",
        )
        backup_observation = self.make_observation(
            root,
            "post-live-backup",
            backup_root,
            backup_snapshot,
            artifacts,
            headless=headless,
            inventory_tool=inventory_tool,
            symbol_tool=symbol_tool,
            manifest=apply_manifest,
            inventory_started_at="2026-08-03T10:16:00Z",
            inventory_completed_at="2026-08-03T10:17:00Z",
            symbol_started_at="2026-08-03T10:18:00Z",
            symbol_completed_at="2026-08-03T10:19:00Z",
            observed_at="2026-08-03T10:20:00Z",
        )
        restore_observation = self.make_observation(
            root,
            "post-live-restore",
            restore_root,
            restore_snapshot,
            artifacts,
            headless=headless,
            inventory_tool=inventory_tool,
            symbol_tool=symbol_tool,
            manifest=apply_manifest,
            inventory_started_at="2026-08-03T10:21:00Z",
            inventory_completed_at="2026-08-03T10:22:00Z",
            symbol_started_at="2026-08-03T10:23:00Z",
            symbol_completed_at="2026-08-03T10:24:00Z",
            observed_at="2026-08-03T10:25:00Z",
        )
        manifest = root / "backups" / "post-live" / "backup_manifest.json"
        self.write_backup_manifest(
            manifest, backup_snapshot, "2026-08-03T10:15:30Z"
        )
        self.write_backup_manifest(
            restore_root / "backup_manifest.json",
            restore_snapshot,
            "2026-08-03T10:20:30Z",
        )

        pre_initial = self.make_observation(
            owner_root,
            "live-pre-initial",
            live_root,
            pre_snapshot,
            pre_artifacts,
            headless=headless,
            inventory_tool=inventory_tool,
            symbol_tool=symbol_tool,
            manifest=apply_manifest,
            inventory_started_at="2026-08-03T09:07:00Z",
            inventory_completed_at="2026-08-03T09:08:00Z",
            symbol_started_at="2026-08-03T09:09:00Z",
            symbol_completed_at="2026-08-03T09:10:00Z",
            observed_at="2026-08-03T09:11:00Z",
            state="PRE",
        )
        pre_final = self.make_observation(
            owner_root,
            "live-pre-final",
            live_root,
            pre_snapshot,
            pre_artifacts,
            headless=headless,
            inventory_tool=inventory_tool,
            symbol_tool=symbol_tool,
            manifest=apply_manifest,
            inventory_started_at="2026-08-03T09:22:00Z",
            inventory_completed_at="2026-08-03T09:23:00Z",
            symbol_started_at="2026-08-03T09:24:00Z",
            symbol_completed_at="2026-08-03T09:25:00Z",
            observed_at="2026-08-03T09:26:00Z",
            state="PRE",
        )
        pre_backup_observation = self.make_observation(
            owner_root,
            "pre-live-backup",
            pre_backup_root,
            pre_backup_snapshot,
            pre_artifacts,
            headless=headless,
            inventory_tool=inventory_tool,
            symbol_tool=symbol_tool,
            manifest=apply_manifest,
            inventory_started_at="2026-08-03T09:12:00Z",
            inventory_completed_at="2026-08-03T09:13:00Z",
            symbol_started_at="2026-08-03T09:14:00Z",
            symbol_completed_at="2026-08-03T09:15:00Z",
            observed_at="2026-08-03T09:16:00Z",
            state="PRE",
        )
        pre_restore_observation = self.make_observation(
            owner_root,
            "pre-live-restore",
            pre_restore_root,
            pre_restore_snapshot,
            pre_artifacts,
            headless=headless,
            inventory_tool=inventory_tool,
            symbol_tool=symbol_tool,
            manifest=apply_manifest,
            inventory_started_at="2026-08-03T09:17:00Z",
            inventory_completed_at="2026-08-03T09:18:00Z",
            symbol_started_at="2026-08-03T09:19:00Z",
            symbol_completed_at="2026-08-03T09:20:00Z",
            observed_at="2026-08-03T09:21:00Z",
            state="PRE",
        )
        pre_manifest = owner_root / "backups" / "pre-live" / "backup_manifest.json"
        self.write_backup_manifest(
            pre_manifest, pre_backup_snapshot, "2026-08-03T09:11:30Z"
        )
        self.write_backup_manifest(
            pre_restore_root / "backup_manifest.json",
            pre_restore_snapshot,
            "2026-08-03T09:16:30Z",
        )

        def make_reproductions(receipt_root: Path, phase: str) -> dict:
            if phase == "prepared":
                times = {
                    "formal": ("2026-08-03T09:01:00Z", "2026-08-03T09:02:00Z"),
                    "lineage": ("2026-08-03T09:03:00Z", "2026-08-03T09:04:00Z"),
                    "campaign": ("2026-08-03T09:05:00Z", "2026-08-03T09:06:00Z"),
                }
            else:
                times = {
                    "formal": ("2026-08-03T10:00:00Z", "2026-08-03T10:01:00Z"),
                    "lineage": ("2026-08-03T10:02:00Z", "2026-08-03T10:03:00Z"),
                    "campaign": ("2026-08-03T10:04:00Z", "2026-08-03T10:05:00Z"),
                }
            results = {
                "formal": {
                    "verdict": "SURVIVED",
                    "admissibleTargets": campaign.GLOBAL_INIT515_COUNT,
                    "publicationStatus": "READY",
                },
                "lineage": {
                    "status": "READY",
                    "summary": {"rows": campaign.GLOBAL_INIT515_COUNT},
                },
                "campaign": {
                    "generation": 5,
                    "counts": {"functions": 7595, "residuals": 6618},
                },
            }
            expected_argv = {
                "formal": [
                    str(campaign.GLOBAL_INIT515_PYTHON_PATH.resolve()),
                    "-I",
                    "-B",
                    str(campaign.GLOBAL_INIT515_FORMAL_OWNER_PATH.resolve()),
                    "--verify-ready",
                    str((campaign.GLOBAL_INIT515_FORMAL_ROOT / "proof.ready.json").resolve()),
                ],
                "lineage": [
                    str(campaign.GLOBAL_INIT515_PYTHON_PATH.resolve()),
                    "-I",
                    "-B",
                    str(campaign.GLOBAL_INIT515_LINEAGE_OWNER_PATH.resolve()),
                    "verify",
                    "--bundle",
                    str(campaign.GLOBAL_INIT515_LINEAGE_ROOT.resolve()),
                ],
                "campaign": [
                    str(campaign.GLOBAL_INIT515_PYTHON_PATH.resolve()),
                    "-B",
                    str(campaign.GLOBAL_INIT515_CAMPAIGN_OWNER_PATH.resolve()),
                    "verify",
                    "--campaign",
                    str(campaign.GLOBAL_INIT515_CAMPAIGN_ROOT.resolve()),
                ],
            }
            reproductions = {}
            for name in ("formal", "lineage", "campaign"):
                result = results[name]
                log_text = (
                    f"CAMPAIGN_VERIFIED {result['counts']!r} "
                    f"{campaign.GLOBAL_INIT515_CAMPAIGN_ROOT}\n"
                    if name == "campaign"
                    else json.dumps(result)
                )
                reproductions[name] = {
                    "run": self.make_process(
                        receipt_root,
                        f"authority-{name}",
                        argv=expected_argv[name],
                        log_text=log_text,
                        started_at=times[name][0],
                        completed_at=times[name][1],
                    ),
                    "result": result,
                }
            return reproductions

        prepared = {
            "schema": campaign.GLOBAL_INIT515_LIVE_PREPARED_SCHEMA,
            "status": "READY",
            "preparedAtUtc": "2026-08-03T09:28:00Z",
            "owner": {
                "path": str(
                    campaign.REPO_ROOT
                    / "tools/ghidra_global_init515_live_promotion.py"
                ),
                "sha256": campaign.GLOBAL_INIT515_LIVE_OWNER_SHA256,
            },
            "authority": {
                "formalReady": {
                    "path": str(
                        (campaign.GLOBAL_INIT515_FORMAL_ROOT / "proof.ready.json").resolve()
                    ),
                    "sha256": campaign.GLOBAL_INIT515_FORMAL_READY_SHA256,
                },
                "manifest": {
                    "path": str(apply_manifest.resolve()),
                    "sha256": campaign.GLOBAL_INIT515_MANIFEST_SHA256,
                    "count": campaign.GLOBAL_INIT515_COUNT,
                },
                "lineageReady": {
                    "path": str(
                        (campaign.GLOBAL_INIT515_LINEAGE_ROOT / "READY.json").resolve()
                    ),
                    "sha256": campaign.GLOBAL_INIT515_LINEAGE_READY_SHA256,
                },
                "campaignReady": {
                    "path": str(
                        (campaign.GLOBAL_INIT515_CAMPAIGN_ROOT / "campaign.ready.json").resolve()
                    ),
                    "sha256": campaign.FROZEN_V5_CAMPAIGN_CARRY_READY_SHA256,
                },
                "program": {
                    "name": "BEA.exe",
                    "md5": "3b456964020070efe696d2cc09464a55",
                    "sha256": campaign.FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256,
                    "imageBase": "0x00400000",
                },
                "liveProject": str(live_root.resolve()),
            },
            "mutex": {
                "name": campaign.GLOBAL_INIT515_MUTEX_NAME,
                "abandoned": False,
            },
            "reproductions": make_reproductions(owner_root, "prepared"),
            "firstQuiescence": {
                "checkedAtUtc": "2026-08-03T09:00:00Z",
                "javaProcesses": [],
                "nativeLockAbsent": True,
                "exclusiveFilesProbed": pre_snapshot["fileCount"],
                "projectFileSetSha256": pre_snapshot["fileSetSha256"],
            },
            "finalQuiescence": {
                "checkedAtUtc": "2026-08-03T09:27:00Z",
                "javaProcesses": [],
                "nativeLockAbsent": True,
                "exclusiveFilesProbed": pre_snapshot["fileCount"],
                "projectFileSetSha256": pre_snapshot["fileSetSha256"],
            },
            "livePreimage": {**pre_snapshot, "root": str(live_root.resolve())},
            "initialObservation": pre_initial,
            "finalObservation": pre_final,
            "preBackup": {
                "sourceSnapshot": {
                    **pre_snapshot,
                    "root": str(live_root.resolve()),
                },
                "backupRoot": str(pre_backup_root.resolve()),
                "backupSnapshot": pre_backup_snapshot,
                "restoreRoot": str(pre_restore_root.resolve()),
                "restoreSnapshot": pre_restore_snapshot,
                "copyManifest": self.stamp(owner_root, pre_manifest),
                "backupObservation": pre_backup_observation,
                "restoreObservation": pre_restore_observation,
                "expectedState": "PRE",
            },
        }
        prepared_path = owner_root / "prepared.ready.json"
        apply_root = root / "runs" / "live-apply"
        apply_output = apply_root / "envelopes.tsv"
        apply_ready_path = apply_root / "envelopes.ready.json"
        tool_hash = campaign.coverage.sha256_of(apply_tool)
        manifest_hash = campaign.coverage.sha256_of(apply_manifest)
        prepared["authority"]["manifest"]["sha256"] = manifest_hash
        prepared_path.write_text(json.dumps(prepared), encoding="utf-8")
        command_values = [
            str(headless.resolve()),
            str(live_root.resolve()),
            "BEA",
            "-process",
            "BEA.exe",
            "-noanalysis",
            "-scriptPath",
            str(apply_tool.resolve().parent),
            "-postScript",
            apply_tool.name,
            str(apply_manifest.resolve()),
            manifest_hash,
            str(campaign.GLOBAL_INIT515_COUNT),
            str(apply_output.resolve()),
            str(apply_ready_path.resolve()),
            "apply",
        ]
        apply_argv = [
            str(Path(r"C:\Windows\System32\cmd.exe")),
            "/d",
            "/s",
            "/c",
            "call " + subprocess.list2cmdline(command_values),
        ]
        marker = (
            "FUNCTION_ENVELOPE_TOOL_OK "
            f"path={apply_tool.resolve()} bytes={apply_tool.stat().st_size} "
            f"sha256={tool_hash}\n"
        )
        apply_process = self.make_process(
            root,
            "live-apply",
            argv=apply_argv,
            log_text=marker,
            started_at="2026-08-03T10:07:00Z",
            completed_at="2026-08-03T10:10:00Z",
        )
        if exact_post_artifacts:
            assert formal_root is not None
            shutil.copyfile(
                formal_root / "runs/replica-a-apply/envelopes.tsv", apply_output
            )
        else:
            apply_output.write_text("synthetic exact apply output\n", encoding="utf-8")
        apply_output_stamp = campaign.coverage.file_stamp(apply_output)
        apply_output_external = {
            "path": str(apply_output.resolve()),
            "bytes": apply_output_stamp["bytes"],
            "sha256": apply_output_stamp["sha256"],
        }
        apply_ready = {
            "schemaVersion": "bea-ghidra-function-body-envelope.v3",
            "completedAtUtc": "2026-08-03T10:09:00Z",
            "mode": "apply",
            "tool": {
                "path": str(apply_tool.resolve()),
                "bytes": apply_tool.stat().st_size,
                "sha256": tool_hash,
            },
            "program": {
                "name": "BEA.exe",
                "executableMd5": "3b456964020070efe696d2cc09464a55",
                "executableSha256": campaign.FROZEN_V5_CAMPAIGN_CARRY_SPECIMEN_SHA256,
                "imageBase": "0x00400000",
                "language": "x86:LE:32:default",
                "compilerSpec": "windows",
            },
            "manifest": {
                "path": str(apply_manifest.resolve()),
                "bytes": apply_manifest.stat().st_size,
                "sha256": manifest_hash,
                "expectedCount": campaign.GLOBAL_INIT515_COUNT,
            },
            "output": apply_output_external,
            "counts": {
                "targets": campaign.GLOBAL_INIT515_COUNT,
                "functionsBefore": 7595,
                "functionsTransient": 8110,
                "functionManagerViewAfterNestedTransaction": 8110,
                "instructionsBefore": 549864,
                "instructionsAfter": 549864,
            },
            "namesAuthorized": False,
            "functionKindsBoundByManifest": True,
            "loadedOrTransientEnvelopesVerified": True,
            "commitRequested": True,
            "rollbackRequested": False,
            "transactionEndReturnedCommitted": False,
            "loadedStateVerified": False,
            "reopenVerificationRequired": True,
        }
        apply_ready_path.write_text(json.dumps(apply_ready), encoding="utf-8")
        hashes.update(
            {
                "applyOutput": apply_output_stamp["sha256"],
                "envelopeTool": tool_hash,
                "manifest": manifest_hash,
            }
        )
        attempt = {
            "schema": "bea.re.ghidra-global-init515-live-attempt.v1",
            "startedAtUtc": "2026-08-03T10:06:00Z",
            "argv": apply_argv,
            "preparedReady": self.stamp(owner_root, prepared_path),
            "livePreimage": {**pre_snapshot, "root": str(live_root.resolve())},
            "mutationSpawnLimit": 1,
            "retryAuthorized": False,
            "mutex": {
                "name": campaign.GLOBAL_INIT515_MUTEX_NAME,
                "abandoned": False,
            },
        }
        attempt_path = root / "attempt.started.json"
        attempt_path.write_text(json.dumps(attempt), encoding="utf-8")

        reproductions = make_reproductions(root, "promotion")
        result = {
            "schema": campaign.GLOBAL_INIT515_LIVE_PROMOTION_SCHEMA,
            "completedAtUtc": "2026-08-03T10:26:00Z",
            "state": "POST",
            "protocol": {"status": "COMPLETE", "reasons": []},
            "process": apply_process,
            "attempt": self.stamp(root, attempt_path),
            "authorityReproductions": reproductions,
            "observation": live_observation,
            "observationError": "",
            "postBackup": {
                "sourceSnapshot": {**backup_snapshot, "root": str(live_root.resolve())},
                "backupRoot": str(backup_root.resolve()),
                "backupSnapshot": backup_snapshot,
                "restoreRoot": str(restore_root.resolve()),
                "restoreSnapshot": restore_snapshot,
                "copyManifest": self.stamp(root, manifest),
                "backupObservation": backup_observation,
                "restoreObservation": restore_observation,
                "expectedState": "POST",
            },
            "postBackupError": "",
            "mutationSpawns": 1,
            "retryAuthorized": False,
            "automaticRestorePerformed": False,
            "campaignPublicationAuthorized": True,
        }
        result_path = root / "promotion.result.json"
        result_path.write_text(json.dumps(result), encoding="utf-8")
        ready = {**result, "status": "READY", "result": self.stamp(root, result_path)}
        ready_path = root / "promotion.ready.json"
        ready_path.write_text(json.dumps(ready), encoding="utf-8")
        return ready_path, hashes, backup_root / "BEA.rep" / "idata" / "~index.dat"

    @staticmethod
    def live_constant_patch(hashes: dict[str, str]):
        return patch.multiple(
            campaign,
            GLOBAL_INIT515_POST_FUNCTIONS_SHA256=hashes["functions"],
            GLOBAL_INIT515_POST_PROGRAM_SHA256=hashes["program"],
            GLOBAL_INIT515_POST_SYMBOLS_SHA256=hashes["symbols"],
            GLOBAL_INIT515_PRE_FUNCTIONS_SHA256=hashes["preFunctions"],
            GLOBAL_INIT515_PRE_PROGRAM_SHA256=hashes["preProgram"],
            GLOBAL_INIT515_PRE_SYMBOLS_SHA256=hashes["preSymbols"],
            GLOBAL_INIT515_APPLY_OUTPUT_SHA256=hashes["applyOutput"],
            GLOBAL_INIT515_ENVELOPE_TOOL_SHA256=hashes["envelopeTool"],
            GLOBAL_INIT515_INVENTORY_TOOL_SHA256=hashes["inventoryTool"],
            GLOBAL_INIT515_SYMBOL_TOOL_SHA256=hashes["symbolTool"],
            GLOBAL_INIT515_MANIFEST_SHA256=hashes["manifest"],
            GLOBAL_INIT515_ANALYZE_HEADLESS_SHA256=hashes["headless"],
            GLOBAL_INIT515_PRE_FILESET_SHA256=hashes["preFileSet"],
            GLOBAL_INIT515_ENVELOPE_TOOL_PATH=Path(hashes["envelopeToolPath"]),
            GLOBAL_INIT515_INVENTORY_TOOL_PATH=Path(hashes["inventoryToolPath"]),
            GLOBAL_INIT515_SYMBOL_TOOL_PATH=Path(hashes["symbolToolPath"]),
            GLOBAL_INIT515_MANIFEST_PATH=Path(hashes["manifestPath"]),
            GLOBAL_INIT515_ANALYZE_HEADLESS_PATH=Path(hashes["headlessPath"]),
        )

    def rewrite_promotion_ready(self, root: Path, result: dict) -> Path:
        result_path = root / "promotion.result.json"
        result_path.write_text(json.dumps(result), encoding="utf-8")
        ready = {**result, "status": "READY", "result": self.stamp(root, result_path)}
        ready_path = root / "promotion.ready.json"
        ready_path.write_text(json.dumps(ready), encoding="utf-8")
        return ready_path

    @require_v5_carry_reducer
    def test_live_ready_rehashes_nested_receipts_and_post_backups(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            ready, hashes, backup_payload = self.make_live_ready(root)
            with self.live_constant_patch(hashes):
                validated = campaign.validate_global_init515_live_promotion(ready)
                self.assertEqual("POST", validated["ready"]["state"])
                backup_payload.write_bytes(b"tampered")
                with self.assertRaisesRegex(campaign.CampaignError, "bytes differ"):
                    campaign.validate_global_init515_live_promotion(ready)

    def test_live_ready_rejects_partial_protocol_even_when_state_is_post(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            ready_path, hashes, _payload = self.make_live_ready(root)
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            result_path = root / ready["result"]["path"]
            result = json.loads(result_path.read_text(encoding="utf-8"))
            ready["protocol"] = result["protocol"] = {"status": "PARTIAL", "reasons": ["lost log"]}
            result_path.write_text(json.dumps(result), encoding="utf-8")
            ready["result"] = self.stamp(root, result_path)
            ready_path.write_text(json.dumps(ready), encoding="utf-8")
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "publication-ready"
            ):
                campaign.validate_global_init515_live_promotion(ready_path)

    @require_v5_carry_reducer
    def test_live_ready_rejects_unchanged_pre_and_post_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            ready, hashes, _payload = self.make_live_ready(
                root, pre_equals_post=True
            )
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "intent/process identity differs"
            ):
                campaign.validate_global_init515_live_promotion(ready)

    def test_live_ready_rejects_a_different_prepared_preimage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            ready, hashes, _payload = self.make_live_ready(root)
            with self.live_constant_patch(hashes), patch.object(
                campaign, "GLOBAL_INIT515_PRE_FILESET_SHA256", "0" * 64
            ), self.assertRaisesRegex(
                campaign.CampaignError, "prepared live preimage bytes differ"
            ):
                campaign.validate_global_init515_live_promotion(ready)

    @require_v5_carry_reducer
    def test_live_ready_rejects_future_dated_apply_intent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            _ready, hashes, _payload = self.make_live_ready(root)
            attempt_path = root / "attempt.started.json"
            attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
            attempt["startedAtUtc"] = "2099-01-01T00:00:00Z"
            attempt_path.write_text(json.dumps(attempt), encoding="utf-8")
            result_path = root / "promotion.result.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["attempt"] = self.stamp(root, attempt_path)
            ready_path = self.rewrite_promotion_ready(root, result)
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "chronology differs"
            ):
                campaign.validate_global_init515_live_promotion(ready_path)

    def test_observation_rejects_a_forged_raw_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            ready_path, hashes, _payload = self.make_live_ready(root)
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            observation_path = root / ready["observation"]["path"]
            observation = json.loads(observation_path.read_text(encoding="utf-8"))
            observation["rawBefore"]["root"] = str((root / "forged").resolve())
            observation_path.write_text(json.dumps(observation), encoding="utf-8")
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "raw snapshot roots differ"
            ):
                campaign._validate_post_observation_stamp(
                    root,
                    self.stamp(root, observation_path),
                    "live observation",
                    expected_project_root=Path(r"C:\Users\david\Ghidra\Projects"),
                    expected_observation_label="live-post-attempt",
                )

    def test_observation_rejects_a_shared_artifact_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            ready_path, hashes, _payload = self.make_live_ready(root)
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            observation_path = root / ready["observation"]["path"]
            observation = json.loads(observation_path.read_text(encoding="utf-8"))
            source = root / observation["functions"]["path"]
            shared = root / "runs/shared/functions.tsv"
            shared.parent.mkdir(parents=True)
            shutil.copyfile(source, shared)
            observation["functions"] = self.stamp(root, shared)
            observation_path.write_text(json.dumps(observation), encoding="utf-8")
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "functions path differs"
            ):
                campaign._validate_post_observation_stamp(
                    root,
                    self.stamp(root, observation_path),
                    "live observation",
                    expected_project_root=Path(r"C:\Users\david\Ghidra\Projects"),
                    expected_observation_label="live-post-attempt",
                )

    def test_live_ready_rejects_hardlinked_observation_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            ready_path, hashes, _payload = self.make_live_ready(root)
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            live_observation = json.loads(
                (root / ready["observation"]["path"]).read_text(encoding="utf-8")
            )
            backup_observation = json.loads(
                (
                    root
                    / ready["postBackup"]["backupObservation"]["path"]
                ).read_text(encoding="utf-8")
            )
            source = root / live_observation["functions"]["path"]
            destination = root / backup_observation["functions"]["path"]
            destination.unlink()
            os.link(source, destination)
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "multiple hard links|files alias"
            ):
                campaign.validate_global_init515_live_promotion(ready_path)

    @require_v5_carry_reducer
    def test_live_ready_rejects_hardlinked_authority_phase_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            ready_path, hashes, _payload = self.make_live_ready(root)
            prepared_log = root.parent / "runs/authority-formal/headless.partial.log"
            promotion_log = root / "runs/authority-formal/headless.partial.log"
            promotion_log.unlink()
            os.link(prepared_log, promotion_log)
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "multiple hard links|files alias"
            ):
                campaign.validate_global_init515_live_promotion(ready_path)

    @require_v5_carry_reducer
    def test_live_ready_rejects_symlinked_apply_artifacts(self) -> None:
        for relative in (
            "runs/live-apply/envelopes.tsv",
            "runs/live-apply/envelopes.ready.json",
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "promotion"
                ready_path, hashes, _payload = self.make_live_ready(root)
                path = root / relative
                hidden = path.with_name(f"hidden-{path.name}")
                path.replace(hidden)
                try:
                    os.symlink(hidden.name, path)
                except OSError as exc:
                    self.skipTest(f"file symlink unavailable: {exc}")
                with self.live_constant_patch(hashes), self.assertRaisesRegex(
                    campaign.CampaignError, "not one plain evidence file"
                ):
                    campaign.validate_global_init515_live_promotion(ready_path)

    def test_observation_rejects_a_self_attested_process_argv(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            ready_path, hashes, _payload = self.make_live_ready(root)
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            observation_path = root / ready["observation"]["path"]
            observation = json.loads(observation_path.read_text(encoding="utf-8"))
            run_path = root / observation["inventoryRun"]["path"]
            run = json.loads(run_path.read_text(encoding="utf-8"))
            run["argv"] = ["echo", "INVENTORY_TOOL_OK"]
            run_path.write_text(json.dumps(run), encoding="utf-8")
            observation["inventoryRun"] = self.stamp(root, run_path)
            observation_path.write_text(json.dumps(observation), encoding="utf-8")
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "argv differs"
            ):
                campaign._validate_post_observation_stamp(
                    root,
                    self.stamp(root, observation_path),
                    "live observation",
                    expected_project_root=Path(r"C:\Users\david\Ghidra\Projects"),
                    expected_observation_label="live-post-attempt",
                )

    @require_v5_carry_reducer
    def test_authority_reproduction_rejects_an_unparsed_ok_log(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            _ready, hashes, _payload = self.make_live_ready(root)
            owner_root = root.parent
            prepared_path = owner_root / "prepared.ready.json"
            prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
            formal_run_path = owner_root / prepared["reproductions"]["formal"]["run"]["path"]
            formal_run = json.loads(formal_run_path.read_text(encoding="utf-8"))
            formal_log_path = owner_root / formal_run["log"]["path"]
            formal_log_path.write_text("ok\n", encoding="utf-8")
            formal_run["log"] = self.stamp(owner_root, formal_log_path)
            formal_run_path.write_text(json.dumps(formal_run), encoding="utf-8")
            prepared["reproductions"]["formal"]["run"] = self.stamp(
                owner_root, formal_run_path
            )
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "formal log cannot be parsed"
            ):
                campaign._validate_global_init515_reproductions(
                    owner_root,
                    prepared["reproductions"],
                    "prepared authority",
                )

    @require_v5_carry_reducer
    def test_authority_reproduction_rejects_a_forged_process_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            _ready, hashes, _payload = self.make_live_ready(root)
            owner_root = root.parent
            prepared_path = owner_root / "prepared.ready.json"
            prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
            run_path = owner_root / prepared["reproductions"]["campaign"]["run"]["path"]
            run = json.loads(run_path.read_text(encoding="utf-8"))
            run["cwd"] = r"X:\attacker"
            run["environment"] = {
                "PYTHONPATH": r"X:\attacker",
                "BEA_REPO_ROOT": r"X:\fake-repo",
            }
            run_path.write_text(json.dumps(run), encoding="utf-8")
            prepared["reproductions"]["campaign"]["run"] = self.stamp(
                owner_root, run_path
            )
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "process context differs"
            ):
                campaign._validate_global_init515_reproductions(
                    owner_root,
                    prepared["reproductions"],
                    "prepared authority",
                )

    @require_v5_carry_reducer
    def test_authority_reproduction_rejects_a_symlinked_log(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            _ready, hashes, _payload = self.make_live_ready(root)
            owner_root = root.parent
            prepared_path = owner_root / "prepared.ready.json"
            prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
            run_path = owner_root / prepared["reproductions"]["campaign"]["run"]["path"]
            run = json.loads(run_path.read_text(encoding="utf-8"))
            log_path = owner_root / run["log"]["path"]
            hidden = log_path.with_name("hidden.log")
            log_path.replace(hidden)
            try:
                os.symlink(hidden.name, log_path)
            except OSError as exc:
                self.skipTest(f"file symlink unavailable: {exc}")
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "not one plain evidence file"
            ):
                campaign._validate_global_init515_reproductions(
                    owner_root,
                    prepared["reproductions"],
                    "prepared authority",
                )

    def test_prepared_boundary_rejects_fake_authority_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            _ready, hashes, _payload = self.make_live_ready(root)
            owner_root = root.parent
            prepared_path = owner_root / "prepared.ready.json"
            prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
            prepared["authority"]["formalReady"]["path"] = r"X:\fake\proof.ready.json"
            prepared_path.write_text(json.dumps(prepared), encoding="utf-8")
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "prepared authority differs"
            ):
                campaign._validate_global_init515_prepared(
                    owner_root,
                    self.stamp(owner_root, prepared_path),
                    live_root=Path(r"C:\Users\david\Ghidra\Projects"),
                )

    @require_v5_carry_reducer
    def test_live_ready_rejects_crosswired_backup_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            _ready, hashes, _payload = self.make_live_ready(root)
            result_path = root / "promotion.result.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["postBackup"]["backupRoot"] = result["postBackup"]["restoreRoot"]
            ready_path = self.rewrite_promotion_ready(root, result)
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "POST backup roots differ"
            ):
                campaign.validate_global_init515_live_promotion(ready_path)

    @require_v5_carry_reducer
    def test_live_ready_rejects_an_unbound_backup_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            _ready, hashes, _payload = self.make_live_ready(root)
            result_path = root / "promotion.result.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            manifest_path = root / result["postBackup"]["copyManifest"]["path"]
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["sourceStable"] = False
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result["postBackup"]["copyManifest"] = self.stamp(root, manifest_path)
            ready_path = self.rewrite_promotion_ready(root, result)
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "backup manifest payload differs"
            ):
                campaign.validate_global_init515_live_promotion(ready_path)

    @require_v5_carry_reducer
    def test_live_ready_rejects_external_project_file_hardlinks(self) -> None:
        for tree in ("post-live", "post-live-restore-drill"):
            with self.subTest(tree=tree), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "promotion"
                ready_path, hashes, _payload = self.make_live_ready(root)
                project_file = root / "backups" / tree / "BEA.rep/idata/~index.dat"
                external = root.parent / f"external-{tree}.dat"
                os.link(project_file, external)
                with self.live_constant_patch(hashes), self.assertRaisesRegex(
                    campaign.CampaignError, "hardlinked project file"
                ):
                    campaign.validate_global_init515_live_promotion(ready_path)

    @require_v5_carry_reducer
    def test_live_ready_rejects_tampered_apply_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            ready, hashes, _payload = self.make_live_ready(root)
            (root / "runs/live-apply/envelopes.tsv").write_bytes(b"tampered")
            with self.live_constant_patch(hashes), self.assertRaisesRegex(
                campaign.CampaignError, "apply TSV bytes differ"
            ):
                campaign.validate_global_init515_live_promotion(ready)

    def test_prepared_boundary_requires_the_pre_backup_and_observations(self) -> None:
        for removed in ("preBackup", "initialObservation", "finalObservation"):
            with self.subTest(removed=removed), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "promotion"
                _ready, hashes, _payload = self.make_live_ready(root)
                owner_root = root.parent
                prepared_path = owner_root / "prepared.ready.json"
                prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
                del prepared[removed]
                prepared_path.write_text(json.dumps(prepared), encoding="utf-8")
                with self.live_constant_patch(hashes), self.assertRaises(
                    campaign.CampaignError
                ):
                    campaign._validate_global_init515_prepared(
                        owner_root,
                        self.stamp(owner_root, prepared_path),
                        live_root=Path(r"C:\Users\david\Ghidra\Projects"),
                    )

    def test_apply_process_rejects_a_fake_command_with_required_substrings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "promotion"
            _ready, hashes, _payload = self.make_live_ready(root)
            receipt_path = root / "runs/live-apply/run.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["argv"] = [
                "echo",
                str(root / "runs/live-apply/envelopes.tsv"),
                str(root / "runs/live-apply/envelopes.ready.json"),
                hashes["envelopeToolPath"],
                hashes["manifestPath"],
                hashes["manifest"],
                str(campaign.GLOBAL_INIT515_COUNT),
                " apply",
            ]
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.live_constant_patch(hashes):
                process = campaign._validate_contained_process_stamp(
                    root,
                    self.stamp(root, receipt_path),
                    "global-init515 live apply",
                )
                with self.assertRaisesRegex(
                    campaign.CampaignError, "process/argv differs"
                ):
                    campaign._validate_global_init515_apply_artifacts(root, process)

    def test_apply_ready_requires_exact_stamps_flags_and_timestamp(self) -> None:
        attacks = {
            "committed": lambda ready: ready.__setitem__(
                "transactionEndReturnedCommitted", True
            ),
            "tool-bytes": lambda ready: ready["tool"].__setitem__("bytes", 0),
            "manifest-bytes": lambda ready: ready["manifest"].__setitem__(
                "bytes", 0
            ),
            "timestamp": lambda ready: ready.pop("completedAtUtc"),
        }
        for name, attack in attacks.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "promotion"
                _ready, hashes, _payload = self.make_live_ready(root)
                ready_path = root / "runs/live-apply/envelopes.ready.json"
                payload = json.loads(ready_path.read_text(encoding="utf-8"))
                attack(payload)
                ready_path.write_text(json.dumps(payload), encoding="utf-8")
                process_path = root / "runs/live-apply/run.json"
                with self.live_constant_patch(hashes):
                    process = campaign._validate_contained_process_stamp(
                        root,
                        self.stamp(root, process_path),
                        "global-init515 live apply",
                    )
                    with self.assertRaisesRegex(
                        campaign.CampaignError, "apply READY"
                    ):
                        campaign._validate_global_init515_apply_artifacts(
                            root, process
                        )

    def test_exact_lineage_bundle_runs_its_frozen_owner(self) -> None:
        root = (
            Path(__file__).resolve().parent.parent
            / "local-lab/global-init515-campaign-lineage-v1-ready"
        )
        validated = campaign.validate_global_init515_lineage(root)
        self.assertEqual(campaign.GLOBAL_INIT515_COUNT, len(validated["rows"]))

    @require_v5_carry_reducer
    def test_full_residual_producer_self_replays_on_post_surrogate(self) -> None:
        repo = Path(__file__).resolve().parent.parent
        snapshot = (
            repo
            / "local-lab/global-init515-residual-producer-surrogate-20260803-v4/snapshot"
        )
        lineage = repo / "local-lab/global-init515-campaign-lineage-v1-ready"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generation6 = root / "generation-6"
            campaign.seed(
                snapshot,
                generation6,
                carry=campaign.FROZEN_V5_CAMPAIGN_CARRY_ROOT,
            )
            evidence, hashes, _payload = self.make_live_ready(
                root / "evidence", exact_post_artifacts=True
            )
            self.assertEqual(
                campaign.GLOBAL_INIT515_POST_FUNCTIONS_SHA256, hashes["functions"]
            )
            out = root / "generation-7"
            with patch.object(
                campaign,
                "GLOBAL_INIT515_PRE_FILESET_SHA256",
                hashes["preFileSet"],
            ):
                receipt = campaign.advance_ghidra_residual_promotion(
                    generation6, evidence, lineage, out
                )
                self.assertEqual(555, receipt["counts"]["supersessions"])
                self.assertEqual(
                    campaign.GLOBAL_INIT515_COUNT, receipt["advance"]["count"]
                )
                replayed = campaign.verify(out)
            self.assertEqual(receipt["counts"], replayed["counts"])


class Atomic14ExactPartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = (
            Path(__file__).resolve().parent.parent
            / "local-lab/console-callback-atomic14-post-campaign-20260803-v1"
            / "generation-8-live-promoted"
        )
        if not (cls.root / "campaign.ready.json").is_file():
            raise unittest.SkipTest("maintainer-local Atomic14 Generation 8 is unavailable")

    def load_generation(self) -> tuple[dict[str, list[dict[str, str]]], dict]:
        rows = campaign._campaign_rows_from_root(self.root)
        receipt = json.loads(
            (self.root / "campaign.ready.json").read_text(encoding="utf-8")
        )
        return rows, receipt

    def test_generation_8_replays_or_reports_the_exact_lost_identity(self) -> None:
        missing = missing_atomic14_replay_inputs()
        if missing:
            self.assertEqual(["formalReady"], missing)
            with self.assertRaisesRegex(
                campaign.CampaignError, "formalReady is missing"
            ):
                campaign._verify_target_lock_semantic_parent_campaign(self.root)
            return
        receipt = campaign._verify_target_lock_semantic_parent_campaign(self.root)
        self.assertEqual(
            {
                "functions": 8124,
                "residuals": 6117,
                "questions": 15238,
                "scenarios": 72,
                "levers": 915,
                "contracts": 14241,
                "adjudications": 3,
                "supersessions": 584,
            },
            receipt["counts"],
        )
        self.assertEqual("EXACT_FROZEN_GENERATION8_REPLAY", receipt["_carryBridge"])
        self.assertFalse(receipt["advance"]["semanticPromotionApplied"])

    def test_generation_8_frozen_integrity_without_historical_replay(self) -> None:
        receipt, reducer = campaign._verify_frozen_campaign_integrity(
            self.root, "Generation 8"
        )
        self.assertEqual(8, receipt["generation"])
        self.assertEqual(
            "04acc723a5ecbe40544223b3fa26fa15d3d5d50ce0fd64682147d4073c5670b5",
            reducer["id"],
        )

    def test_relation_gate_rejects_atomic14_overclaims_and_lineage_attacks(self) -> None:
        import copy

        attacks = {}

        def forged_digest(rows: dict, _receipt: dict) -> None:
            row = next(
                item for item in rows["functions"] if item["entryVa"] == "0x004295c0"
            )
            row["bodyRangeSetSha256"] = "0" * 64

        attacks["forged campaign digest"] = forged_digest

        def semantic_name(rows: dict, _receipt: dict) -> None:
            row = next(
                item for item in rows["functions"] if item["entryVa"] == "0x004295c0"
            )
            row["currentName"] = "CConsole__Invented"

        attacks["semantic name overclaim"] = semantic_name

        def retired_row(_rows: dict, receipt: dict) -> None:
            receipt["advance"]["retiredSubject"]["contract"][
                "remainingUncertainty"
            ] = "forged"

        attacks["retired row forgery"] = retired_row

        def incomplete_evidence(rows: dict, _receipt: dict) -> None:
            row = next(
                item
                for item in rows["supersessions"]
                if item["kind"] == campaign.GHIDRA_PARTITION_ADVANCE_KIND
            )
            row["evidenceRefs"] = ";".join(row["evidenceRefs"].split(";")[:-1])

        attacks["incomplete evidence set"] = incomplete_evidence

        def semantic_promotion(rows: dict, receipt: dict) -> None:
            receipt["advance"]["semanticPromotionApplied"] = True
            adjudication_id = receipt["advance"]["adjudicationId"]
            next(
                item
                for item in rows["adjudications"]
                if item["adjudicationId"] == adjudication_id
            )["semanticPromotionApplied"] = "True"

        attacks["semantic promotion overclaim"] = semantic_promotion

        base_rows, base_receipt = self.load_generation()
        for label, attack in attacks.items():
            with self.subTest(attack=label):
                rows = copy.deepcopy(base_rows)
                receipt = copy.deepcopy(base_receipt)
                attack(rows, receipt)
                with self.assertRaises(campaign.CampaignError):
                    campaign._validate_campaign_relations(rows, receipt)


class TargetLockSemanticGeneration9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        cls.parent = (
            repo
            / "local-lab/console-callback-atomic14-post-campaign-20260803-v1"
            / "generation-8-live-promoted"
        )
        cls.live_ready = (
            repo
            / "local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2"
            / "promotion/promotion.ready.json"
        )
        if not (cls.parent / "campaign.ready.json").is_file() or not cls.live_ready.is_file():
            raise unittest.SkipTest(
                "maintainer-local Generation 8 / target-lock live evidence is unavailable"
            )

    @staticmethod
    def file_sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_generation_9_replays_or_reports_the_exact_lost_identity(self) -> None:
        missing = missing_atomic14_replay_inputs()
        if missing:
            self.assertEqual(["formalReady"], missing)
            with self.assertRaisesRegex(
                campaign.CampaignError, "formalReady is missing"
            ):
                campaign._verify_target_lock_semantic_parent_campaign(self.parent)
            return
        expected_names = {
            "0x00406fc0": "CBattleEngine__StartLock",
            "0x00407060": "CBattleEngine__FireLock",
            "0x00407140": "CBattleEngine__LockHit",
            "0x004071b0": "CBattleEngine__GetCurrentTarget",
            "0x00407310": "CBattleEngine__DisplayLock",
        }
        unchanged_outputs = {
            "campaign-residuals.tsv",
            "campaign-questions.tsv",
            "campaign-scenarios.tsv",
            "campaign-levers.tsv",
            "campaign-adjudications.tsv",
            "campaign-supersessions.tsv",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "generation-9"
            receipt = campaign.advance_ghidra_semantic_promotion(
                self.parent, self.live_ready, out
            )
            verified = campaign.verify(out, _replay_generation=False)
            self.assertEqual(receipt["counts"], verified["counts"])
            self.assertEqual(9, receipt["generation"])
            self.assertEqual(5, receipt["advance"]["count"])
            self.assertEqual(
                {
                    "functions": 8124,
                    "residuals": 6117,
                    "questions": 15238,
                    "scenarios": 72,
                    "levers": 915,
                    "contracts": 14241,
                    "adjudications": 3,
                    "supersessions": 584,
                },
                receipt["counts"],
            )
            for name in unchanged_outputs:
                self.assertEqual(
                    self.file_sha256(self.parent / name),
                    self.file_sha256(out / name),
                    name,
                )

            old_functions = {
                row["entityKey"]: row
                for row in campaign._read_tsv(
                    self.parent / "campaign-functions.tsv"
                )
            }
            new_functions = {
                row["entityKey"]: row
                for row in campaign._read_tsv(out / "campaign-functions.tsv")
            }
            changed_function_entities = {
                entity
                for entity in old_functions
                if old_functions[entity] != new_functions[entity]
            }
            self.assertEqual(
                set(expected_names),
                {
                    new_functions[entity]["entryVa"]
                    for entity in changed_function_entities
                },
            )
            preserved_function_fields = {
                "entityKey",
                "entryVa",
                "entryRva",
                "bodyRangesRva",
                "bodyRangeSetSha256",
                "bodyBytes",
                "executionState",
                "observedBytes",
                "resolutionState",
                "semanticGrade",
                "campaignState",
                "lever",
                "requiresElevation",
                "cheapestFalsifier",
            }
            allowed_function_changes = {
                "currentName",
                "nativeRegistryStatus",
                "nameClass",
                "understoodTier",
                "evidenceStates",
                "lastMeasurementDate",
            }
            for entity in changed_function_entities:
                old = old_functions[entity]
                new = new_functions[entity]
                changed_fields = {
                    field for field in old if old[field] != new[field]
                }
                self.assertTrue(
                    changed_fields <= allowed_function_changes,
                    (new["entryVa"], changed_fields),
                )
                self.assertEqual(expected_names[new["entryVa"]], new["currentName"])
                self.assertEqual(
                    "FUNCTION_PROMOTED_LIVE_SEMANTIC",
                    new["nativeRegistryStatus"],
                )
                for field in preserved_function_fields:
                    self.assertEqual(old[field], new[field], (new["entryVa"], field))
            start_lock = next(
                row
                for row in new_functions.values()
                if row["entryVa"] == "0x00406fc0"
            )
            self.assertEqual("DARK", start_lock["executionState"])
            self.assertEqual(
                "UNKNOWN_WITH_FALSIFIER", start_lock["resolutionState"]
            )

            old_contracts = {
                row["entityKey"]: row
                for row in campaign._read_tsv(
                    self.parent / "campaign-contracts.tsv"
                )
            }
            new_contracts = {
                row["entityKey"]: row
                for row in campaign._read_tsv(out / "campaign-contracts.tsv")
            }
            changed_contract_entities = {
                entity
                for entity in old_contracts
                if old_contracts[entity] != new_contracts[entity]
            }
            self.assertEqual(changed_function_entities, changed_contract_entities)
            for entity in changed_contract_entities:
                old = old_contracts[entity]
                new = new_contracts[entity]
                changed_fields = {
                    field for field in old if old[field] != new[field]
                }
                self.assertEqual(
                    {"currentName", "evidenceRefs", "lastMeasurementDate"},
                    changed_fields,
                )
                self.assertEqual("C0_OPAQUE", new["semanticGrade"])
                self.assertEqual("OPEN", new["contractState"])
                self.assertEqual("NOT_READY", new["rebuildState"])

            forged_state = root / "forged-state"
            shutil.copytree(out, forged_state)
            functions_path = forged_state / "campaign-functions.tsv"
            forged_functions = campaign._read_tsv(functions_path)
            next(
                row
                for row in forged_functions
                if row["entryVa"] == "0x00406fc0"
            )["resolutionState"] = "OPEN_JOIN"
            campaign._write_tsv(
                functions_path, campaign.FUNCTION_COLUMNS, forged_functions
            )
            forged_ready_path = forged_state / "campaign.ready.json"
            forged_ready = json.loads(forged_ready_path.read_text(encoding="utf-8"))
            forged_ready["outputs"]["campaign-functions.tsv"] = {
                **campaign.coverage.file_stamp(functions_path),
                "path": "campaign-functions.tsv",
            }
            forged_ready_path.write_text(
                json.dumps(forged_ready, indent=2) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                campaign.CampaignError, "does not reproduce"
            ):
                campaign.verify(forged_state)

            missing_evidence = root / "missing-evidence"
            shutil.copytree(out, missing_evidence)
            contracts_path = missing_evidence / "campaign-contracts.tsv"
            forged_contracts = campaign._read_tsv(contracts_path)
            target_contract = next(
                row
                for row in forged_contracts
                if row["entryVa"] == "0x00406fc0"
            )
            target_contract["evidenceRefs"] = target_contract[
                "evidenceRefs"
            ].split(";")[0]
            campaign._write_tsv(
                contracts_path, campaign.CONTRACT_COLUMNS, forged_contracts
            )
            missing_ready_path = missing_evidence / "campaign.ready.json"
            missing_ready = json.loads(
                missing_ready_path.read_text(encoding="utf-8")
            )
            missing_ready["outputs"]["campaign-contracts.tsv"] = {
                **campaign.coverage.file_stamp(contracts_path),
                "path": "campaign-contracts.tsv",
            }
            missing_ready_path.write_text(
                json.dumps(missing_ready, indent=2) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                campaign.CampaignError, "semantic Ghidra promotion"
            ):
                campaign.verify(missing_evidence, _replay_generation=False)

            partition_poison = root / "partition-poison"
            shutil.copytree(out, partition_poison)
            supersessions_path = partition_poison / "campaign-supersessions.tsv"
            poisoned_supersessions = campaign._read_tsv(supersessions_path)
            partition_row = next(
                row
                for row in poisoned_supersessions
                if row["kind"] == campaign.GHIDRA_PARTITION_ADVANCE_KIND
            )
            partition_row["evidenceRefs"] = ";".join(
                partition_row["evidenceRefs"].split(";")[:-1]
            )
            campaign._write_tsv(
                supersessions_path,
                campaign.SUPERSESSION_COLUMNS,
                poisoned_supersessions,
            )
            partition_ready_path = partition_poison / "campaign.ready.json"
            partition_ready = json.loads(
                partition_ready_path.read_text(encoding="utf-8")
            )
            partition_ready["outputs"]["campaign-supersessions.tsv"] = {
                **campaign.coverage.file_stamp(supersessions_path),
                "path": "campaign-supersessions.tsv",
            }
            partition_ready_path.write_text(
                json.dumps(partition_ready, indent=2) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                campaign.CampaignError, "invalid supersession"
            ):
                campaign.verify(partition_poison, _replay_generation=False)

    def test_generation_9_frozen_integrity_without_historical_replay(self) -> None:
        root = (
            Path(__file__).resolve().parent.parent
            / "local-lab/ghidra-target-lock-semantic-generation9-20260804-v1"
            / "generation-9-live-semantic-promoted"
        )
        receipt, reducer = campaign._verify_frozen_campaign_integrity(
            root, "Generation 9"
        )
        self.assertEqual(9, receipt["generation"])
        self.assertEqual(
            "480af29c0d51a02527a8b0e144dc5c6f5127ec6399f0dfefbdcd221ecae94db4",
            reducer["id"],
        )

    def test_partition_context_rejects_non_monotone_parent_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary) / "parent"
            parent.mkdir()
            ready_path = parent / "campaign.ready.json"
            ready_path.write_text(
                json.dumps({"generation": 1, "parentCampaign": None}),
                encoding="utf-8",
            )
            receipt = {
                "generation": 1,
                "parentCampaign": {
                    "path": str(parent),
                    "ready": {
                        **campaign.coverage.file_stamp(ready_path),
                        "path": "campaign.ready.json",
                    },
                },
            }
            with self.assertRaisesRegex(
                campaign.CampaignError, "generation is non-monotone"
            ):
                campaign._partition_relation_context(receipt)


class TtdCallContextGeneration10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        cls.parent = (
            repo
            / "local-lab/ghidra-target-lock-semantic-generation9-20260804-v1"
            / "generation-9-live-semantic-promoted"
        )
        cls.evidence = (
            repo / "local-lab/ttd-call-context-level521-impact-schema3-20260804-v1"
        )
        cls.generation = (
            repo
            / "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1"
            / "generation-10-ttd-call-context-observation-v2"
        )
        if not all(
            path.is_file()
            for path in (
                cls.parent / "campaign.ready.json",
                cls.evidence / "proof.ready.json",
                cls.generation / "campaign.ready.json",
            )
        ):
            raise unittest.SkipTest(
                "maintainer-local Generation 9 / Level 521 evidence is unavailable"
            )

    @staticmethod
    def keyed(root: Path, name: str, field: str) -> dict[str, dict[str, str]]:
        return {
            row[field]: row
            for row in campaign._read_tsv(root / f"campaign-{name}.tsv")
        }

    def test_generation_10_replays_or_reports_the_exact_lost_identity(self) -> None:
        missing = missing_atomic14_replay_inputs()
        if missing:
            self.assertEqual(["formalReady"], missing)
            completed = CampaignRecoveryGeneration10Tests.frozen_verify(self.generation)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("formalReady is missing", completed.stderr)
            return
        receipt = campaign.verify(self.generation)
        self.assertEqual(10, receipt["generation"])
        self.assertEqual(
            campaign.TTD_CALL_CONTEXT_EXPECTED_GENERATION10_COUNTS,
            receipt["counts"],
        )
        self.assertEqual(
            campaign.TTD_CALL_CONTEXT_ADVANCE_KIND,
            receipt["advance"]["kind"],
        )
        self.assertEqual("SURVIVED", receipt["advance"]["verdict"])
        self.assertEqual(0, receipt["advance"]["namesChanged"])
        self.assertEqual(0, receipt["advance"]["writesProved"])
        self.assertFalse(receipt["advance"]["rebuildParityProved"])
        self.assertEqual(0, receipt["advance"]["supersessionsAdded"])
        for ledger in ("residuals", "scenarios", "levers", "supersessions"):
            self.assertEqual(
                sha256(self.parent / f"campaign-{ledger}.tsv"),
                sha256(self.generation / f"campaign-{ledger}.tsv"),
                ledger,
            )

        old_functions = self.keyed(self.parent, "functions", "entityKey")
        new_functions = self.keyed(self.generation, "functions", "entityKey")
        changed_functions = {
            key for key in old_functions if old_functions[key] != new_functions[key]
        }
        expected_bindings = campaign._ttd_call_context_target_bindings()
        self.assertEqual(
            {str(row["entityKey"]) for row in expected_bindings},
            changed_functions,
        )
        for binding in expected_bindings:
            old = old_functions[str(binding["entityKey"])]
            new = new_functions[str(binding["entityKey"])]
            self.assertEqual(old["currentName"], new["currentName"])
            self.assertEqual(old["bodyRangesRva"], new["bodyRangesRva"])
            self.assertEqual(old["requiresElevation"], new["requiresElevation"])
            if binding["positive"] is True:
                self.assertEqual("C2_BOUNDED_RUNTIME", new["semanticGrade"])
                self.assertEqual("BOUNDED_CONTRACT", new["resolutionState"])
                self.assertIn(
                    "TTD_CALL_CONTEXT_OBSERVATION",
                    new["evidenceStates"].split(";"),
                )
            else:
                self.assertEqual("OPAQUE", new["semanticGrade"])
                self.assertEqual("UNKNOWN_WITH_FALSIFIER", new["resolutionState"])
                self.assertIn(
                    "TTD_BOUNDED_ZERO_EVENT_CONTROL",
                    new["evidenceStates"].split(";"),
                )

        contracts = self.keyed(self.generation, "contracts", "contractId")
        for binding in expected_bindings:
            contract = contracts[str(binding["contractId"])]
            self.assertEqual("NOT_READY", contract["rebuildState"])
            self.assertEqual("UNASSIGNED", contract["rebuildOwner"])
            self.assertEqual("UNMAPPED", contract["rebuildImplementation"])
            self.assertEqual("UNMAPPED", contract["parityTests"])
            if binding["positive"] is True:
                self.assertEqual("BOUNDED_CONTRACT_ADVANCED", contract["contractState"])
                self.assertEqual("C2_BOUNDED_RUNTIME", contract["semanticGrade"])
                self.assertEqual("SURVIVED", contract["refuterVerdict"])
                self.assertTrue(contract["writes"].startswith("UNKNOWN;"))
                self.assertIn(
                    str(binding["successorQuestionId"]),
                    contract["questionIds"].split(";"),
                )
            else:
                self.assertEqual("OPEN", contract["contractState"])
                self.assertEqual("C0_OPAQUE", contract["semanticGrade"])
                self.assertEqual("UNSCORED", contract["refuterVerdict"])
                self.assertEqual("UNKNOWN", contract["writes"])

        questions = self.keyed(self.generation, "questions", "questionId")
        for binding in expected_bindings:
            parent = questions[str(binding["parentQuestionId"])]
            if binding["positive"] is True:
                successor = questions[str(binding["successorQuestionId"])]
                self.assertEqual("CLOSED_SURVIVED", parent["state"])
                self.assertEqual("SURVIVED", parent["lastOutcome"])
                self.assertEqual("OPEN", successor["state"])
                self.assertEqual(parent["questionId"], successor["parentQuestionId"])
                self.assertEqual("10", successor["generation"])
            else:
                self.assertEqual("OPEN", parent["state"])
                self.assertEqual("UNSCORED", parent["lastOutcome"])

    def test_generation_10_frozen_integrity_without_historical_replay(self) -> None:
        receipt, reducer = campaign._verify_frozen_campaign_integrity(
            self.generation, "Generation 10"
        )
        self.assertEqual(10, receipt["generation"])
        self.assertEqual(
            "7dfa4015aad676bfeb22977adf3aadcddac49ba31fa8203a63a32f76d941f5d9",
            reducer["id"],
        )

    def test_independent_jsonl_parser_rejects_same_length_poison(self) -> None:
        source = (self.evidence / "run-a/call-context.jsonl").read_bytes()
        attacks = {
            "target range": (
                b'"rva_end_exclusive":"0x74CC"',
                b'"rva_end_exclusive":"0x74CD"',
            ),
            "caller": (b'"pc":"0x4268CB"', b'"pc":"0x4268CC"'),
            "raw return": (b'"eax":"0x3865B38"', b'"eax":"0x3865B39"'),
            "association backlink": (
                b'"kind":"invocation","invocation_index":0,"target_index":3,"unique_thread_id":"5","association_epoch":"3968"',
                b'"kind":"invocation","invocation_index":0,"target_index":3,"unique_thread_id":"5","association_epoch":"3969"',
            ),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for label, (old, new) in attacks.items():
                with self.subTest(attack=label):
                    self.assertGreaterEqual(source.count(old), 1, label)
                    poisoned = source.replace(old, new, 1)
                    path = root / f"{label.replace(' ', '-')}.jsonl"
                    path.write_bytes(poisoned)
                    path_neutral = b"".join(
                        poisoned.splitlines(keepends=True)[1:]
                    )
                    with patch.object(
                        campaign,
                        "TTD_CALL_CONTEXT_PATH_NEUTRAL_SHA256",
                        hashlib.sha256(path_neutral).hexdigest(),
                    ):
                        with self.assertRaises(campaign.CampaignError):
                            campaign._validate_ttd_call_context_jsonl(path)

    def test_exact_delta_rejects_name_and_startdie_overclaims(self) -> None:
        import copy

        before = campaign._campaign_rows_from_root(self.parent)
        after = campaign._campaign_rows_from_root(self.generation)
        renamed = copy.deepcopy(after)
        next(
            row for row in renamed["functions"] if row["entryVa"] == "0x004d8ae0"
        )["currentName"] = "CRound__DamagePlayer"
        with self.assertRaisesRegex(campaign.CampaignError, "whitelist"):
            campaign._ttd_call_context_delta(before, renamed)

        closed = copy.deepcopy(after)
        next(
            row for row in closed["contracts"] if row["entryVa"] == "0x0040bfd0"
        )["contractState"] = "TERMINAL_BOUNDED_AMBIGUITY"
        with self.assertRaisesRegex(campaign.CampaignError, "whitelist"):
            campaign._ttd_call_context_delta(before, closed)

    def test_historical_replay_attack_or_exact_lost_identity_is_explicit(self) -> None:
        missing = missing_atomic14_replay_inputs()
        if missing:
            self.assertEqual(["formalReady"], missing)
            completed = CampaignRecoveryGeneration10Tests.frozen_verify(self.generation)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("formalReady is missing", completed.stderr)
            return
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            contracts_path = forged / "campaign-contracts.tsv"
            contracts = campaign._read_tsv(contracts_path)
            next(
                row for row in contracts if row["entryVa"] == "0x0040a890"
            )["writes"] = "life -= damage"
            campaign._write_tsv(
                contracts_path, campaign.CONTRACT_COLUMNS, contracts
            )
            ready_path = forged / "campaign.ready.json"
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            ready["outputs"]["campaign-contracts.tsv"] = {
                **campaign.coverage.file_stamp(contracts_path),
                "path": "campaign-contracts.tsv",
            }
            ready_path.write_text(
                json.dumps(ready, indent=2) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(campaign.CampaignError, "does not reproduce"):
                campaign.verify(forged)

    def test_evidence_verifier_rejects_replica_alias(self) -> None:
        completed = subprocess.run(
            [
                os.fspath(Path(os.sys.executable)),
                "-B",
                os.fspath(self.evidence / "verify.py"),
                os.fspath(self.evidence / "run-a"),
                os.fspath(self.evidence / "run-a"),
            ],
            cwd=self.evidence.parent.parent,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(10, completed.returncode)
        self.assertIn("replica roots alias", completed.stderr)


class FrozenCampaignBootstrapTests(unittest.TestCase):
    def test_manifested_missing_parent_reducer_is_rejected_before_import(self) -> None:
        bootstrap = Path(__file__).resolve().parent / "re_campaign_frozen_bootstrap.py"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "campaign"
            owner = root / "_reducer/tools/re_campaign.py"
            owner.parent.mkdir(parents=True)
            marker = Path(td) / "MALICIOUS_IMPORT_MARKER"
            owner.write_text(
                "from pathlib import Path\n"
                f"Path({os.fspath(marker)!r}).write_text('IMPORTED', encoding='utf-8')\n"
                "def verify(root, _replay_generation=True):\n"
                "    return {'counts': {}}\n",
                encoding="utf-8",
            )
            owner_bytes = owner.read_bytes()
            owner_row = {
                "role": "campaign",
                "path": "_reducer/tools/re_campaign.py",
                "bytes": len(owner_bytes),
                "sha256": hashlib.sha256(owner_bytes).hexdigest(),
            }
            reducer_id = hashlib.sha256(
                (
                    f"{owner_row['role']}\t{owner_row['sha256']}\t"
                    f"{owner_row['bytes']}\t{owner_row['path']}\n"
                ).encode("utf-8")
            ).hexdigest()
            receipt = {
                "schema": campaign.SCHEMA,
                "reducer": {
                    "schema": campaign.REDUCER_SCHEMA,
                    "id": reducer_id,
                    "entry": "_reducer/tools/re_campaign.py",
                    "files": [owner_row],
                },
                "generation": 99,
                "parentCampaign": {
                    "path": os.fspath(Path(td) / "missing-parent"),
                    "ready": {
                        "path": "campaign.ready.json",
                        "bytes": 1,
                        "sha256": "0" * 64,
                    },
                },
            }
            ready_path = root / "campaign.ready.json"
            ready_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            completed = subprocess.run(
                [
                    os.fspath(Path(os.sys.executable)),
                    "-I",
                    "-B",
                    os.fspath(bootstrap),
                    "--campaign",
                    os.fspath(root),
                    "--mode",
                    "integrity",
                    "--expected-ready-sha256",
                    hashlib.sha256(ready_path.read_bytes()).hexdigest(),
                    "--expected-reducer-id",
                    reducer_id,
                ],
                cwd=Path(__file__).resolve().parent.parent,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(10, completed.returncode)
            self.assertIn("outside the exact Generation-5 recovery bridge", completed.stderr)
            self.assertFalse(marker.exists(), "unsafe reducer imported before parent gate")


class CampaignRecoveryGeneration8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        prerequisite = repo / campaign.ATOMIC14_RECOVERY_PARENT_RELATIVE
        cls.generation = base / "generation-8-atomic14-recovered-v2"
        cls.replica = base / "generation-8-atomic14-recovered-v2-replica"
        if not (prerequisite / "campaign.ready.json").is_file():
            raise unittest.SkipTest("maintainer-local Generation 7 prerequisite is unavailable")
        for root in (cls.generation, cls.replica):
            if not (root / "campaign.ready.json").is_file():
                raise AssertionError(f"required recovered Generation 8 is missing: {root}")

    @staticmethod
    def frozen_verify(root: Path, *, replay: bool = True) -> subprocess.CompletedProcess:
        bootstrap = Path(__file__).resolve().parent / "re_campaign_frozen_bootstrap.py"
        ready_path = root / "campaign.ready.json"
        receipt = json.loads(ready_path.read_text(encoding="utf-8"))
        reducer_id = receipt.get("reducer", {}).get("id")
        if not isinstance(reducer_id, str) or not reducer_id:
            raise AssertionError(f"campaign has no exact reducer identity: {root}")
        argv = [
            os.fspath(Path(os.sys.executable)),
            "-I",
            "-B",
            os.fspath(bootstrap),
            "--campaign",
            os.fspath(root),
            "--mode",
            "full" if replay else "integrity",
            "--expected-ready-sha256",
            hashlib.sha256(ready_path.read_bytes()).hexdigest(),
            "--expected-reducer-id",
            reducer_id,
        ]
        environment = os.environ.copy()
        environment["BEA_REPO_ROOT"] = os.fspath(Path(__file__).resolve().parent.parent)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            argv,
            cwd=Path(__file__).resolve().parent.parent,
            env=environment,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )

    def test_two_independent_builds_reproduce_and_fully_replay(self) -> None:
        names = tuple(campaign.OUTPUTS)
        for name in names:
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        receipts = []
        for root in (self.generation, self.replica):
            completed = self.frozen_verify(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
            receipt = json.loads((root / "campaign.ready.json").read_text(encoding="utf-8"))
            receipt["generatedAtUtc"] = "<generated>"
            for stamp in receipt["outputs"].values():
                stamp["lastWriteUtc"] = "<write>"
            receipts.append(receipt)
        self.assertEqual(receipts[0], receipts[1])
        self.assertEqual(
            campaign.GHIDRA_PARTITION_RECOVERY_LINEAGE_ID,
            receipts[0]["advance"]["branchId"],
        )

    def test_integrity_gate_rejects_recovery_metadata_laundering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            ready_path = forged / "campaign.ready.json"
            original = json.loads(ready_path.read_text(encoding="utf-8"))

            def rejected(mutator, expected: str) -> None:
                poisoned = json.loads(json.dumps(original))
                mutator(poisoned)
                ready_path.write_text(
                    json.dumps(poisoned, indent=2) + "\n", encoding="utf-8"
                )
                completed = self.frozen_verify(forged, replay=False)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(
                lambda value: value["advance"]["formalReady"].update(
                    {"bytes": 23028, "sha256": campaign.ATOMIC14_FORMAL_READY_SHA256}
                ),
                "recovery partition formal proof differs",
            )
            rejected(
                lambda value: value["advance"]["historicalFormalReady"].update(
                    {"disposition": "SUBSTITUTED"}
                ),
                "recovery partition provenance differs",
            )
            rejected(
                lambda value: value["advance"]["historicalProjection"].update(
                    {"historicalAuthorityClass": "FULL_REPLAY_AUTHORITY"}
                ),
                "nested frozen campaign invocation was not prevalidated by the root chain",
            )
            rejected(
                lambda value: value["advance"]["historicalProjection"][
                    "changedRows"
                ].update({"contracts": 28}),
                "historical projection differs",
            )
            rejected(
                lambda value: value["advance"]["historicalProjection"][
                    "canonicalLedgerSha256"
                ].update({"functions": "0" * 64}),
                "historical projection differs",
            )
            rejected(
                lambda value: value["advance"].update({"branchId": "wrong-branch"}),
                "recovery partition provenance differs",
            )

    def test_integrity_gate_rejects_an_unchanged_ledger_poison(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            functions_path = forged / "campaign-functions.tsv"
            functions = campaign._read_tsv(functions_path)
            target = next(
                row
                for row in functions
                if row["entryVa"] == "0x00401000"
            )
            target["requiresElevation"] = (
                "False" if target["requiresElevation"] == "True" else "True"
            )
            campaign._write_tsv(
                functions_path, campaign.FUNCTION_COLUMNS, functions
            )
            ready_path = forged / "campaign.ready.json"
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            ready["outputs"]["campaign-functions.tsv"] = {
                **campaign.coverage.file_stamp(functions_path),
                "path": "campaign-functions.tsv",
            }
            ready_path.write_text(
                json.dumps(ready, indent=2) + "\n", encoding="utf-8"
            )
            completed = self.frozen_verify(forged, replay=False)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("non-provenance state", completed.stderr)


class CampaignRecoveryGeneration9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        cls.parent = base / "generation-8-atomic14-recovered-v2"
        cls.generation = base / "generation-9-target-lock-recovered-v2"
        cls.replica = base / "generation-9-target-lock-recovered-v2-replica"
        cls.owner_recovery = base / "target-lock-owner-recovery.ready.json"
        if not (cls.parent / "campaign.ready.json").is_file():
            raise unittest.SkipTest("maintainer-local Generation 8R prerequisite is unavailable")
        for root in (cls.generation, cls.replica):
            if not (root / "campaign.ready.json").is_file():
                raise AssertionError(f"required recovered Generation 9 is missing: {root}")

    @staticmethod
    def frozen_verify(root: Path, *, replay: bool = True) -> subprocess.CompletedProcess:
        return CampaignRecoveryGeneration8Tests.frozen_verify(root, replay=replay)

    @staticmethod
    def reducer_files(root: Path) -> dict[str, bytes]:
        reducer = root / "_reducer"
        return {
            path.relative_to(reducer).as_posix(): path.read_bytes()
            for path in reducer.rglob("*")
            if path.is_file()
        }

    def test_two_independent_builds_reproduce_and_fully_replay(self) -> None:
        self.assertEqual(["formalReady"], missing_atomic14_replay_inputs())
        for name in campaign.OUTPUTS:
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        self.assertEqual(
            self.reducer_files(self.generation), self.reducer_files(self.replica)
        )
        receipts = []
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
        for root in (self.generation, self.replica):
            completed = self.frozen_verify(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
            receipt = json.loads((root / "campaign.ready.json").read_text(encoding="utf-8"))
            self.assertEqual(9, receipt["generation"])
            self.assertEqual(expected_counts, receipt["counts"])
            self.assertEqual(
                campaign.GHIDRA_SEMANTIC_RECOVERY_ADVANCE_KIND,
                receipt["advance"]["kind"],
            )
            self.assertEqual(
                campaign.GHIDRA_SEMANTIC_RECOVERY_ADVANCE_SCHEMA,
                receipt["advance"]["schema"],
            )
            self.assertEqual(
                campaign.GHIDRA_PARTITION_RECOVERY_LINEAGE_ID,
                receipt["advance"]["branchId"],
            )
            receipt["generatedAtUtc"] = "<generated>"
            for stamp in receipt["outputs"].values():
                stamp["lastWriteUtc"] = "<write>"
            receipts.append(receipt)
        self.assertEqual(receipts[0], receipts[1])

        parent_functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.parent / "campaign-functions.tsv")
        }
        child_functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.generation / "campaign-functions.tsv")
        }
        parent_contracts = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.parent / "campaign-contracts.tsv")
        }
        child_contracts = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.generation / "campaign-contracts.tsv")
        }
        self.assertEqual(
            5,
            sum(parent_functions[key] != child_functions[key] for key in parent_functions),
        )
        self.assertEqual(
            5,
            sum(parent_contracts[key] != child_contracts[key] for key in parent_contracts),
        )
        for name in (
            "campaign-residuals.tsv",
            "campaign-questions.tsv",
            "campaign-scenarios.tsv",
            "campaign-levers.tsv",
            "campaign-adjudications.tsv",
            "campaign-supersessions.tsv",
        ):
            self.assertEqual(
                (self.parent / name).read_bytes(),
                (self.generation / name).read_bytes(),
                name,
            )

    def test_integrity_gate_rejects_semantic_recovery_laundering(self) -> None:
        expected_changed = {
            "functions": 0,
            "residuals": 0,
            "questions": 0,
            "scenarios": 0,
            "levers": 0,
            "contracts": 29,
            "adjudications": 1,
            "supersessions": 29,
        }
        ready = json.loads(
            (self.generation / "campaign.ready.json").read_text(encoding="utf-8")
        )
        projection = ready["advance"]["historicalProjection"]
        self.assertEqual(campaign.TTD_CALL_CONTEXT_PARENT_READY_SHA256,
                         projection["historicalReady"]["sha256"])
        self.assertEqual("HISTORICAL_FROZEN_INTEGRITY_ONLY",
                         projection["historicalAuthorityClass"])
        self.assertEqual(expected_changed, projection["changedRows"])

        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            ready_path = forged / "campaign.ready.json"
            original = json.loads(ready_path.read_text(encoding="utf-8"))

            def rejected(mutator, expected: str) -> None:
                poisoned = json.loads(json.dumps(original))
                mutator(poisoned)
                ready_path.write_text(
                    json.dumps(poisoned, indent=2) + "\n", encoding="utf-8"
                )
                completed = self.frozen_verify(forged, replay=False)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(lambda value: value.update({"advance": None}), "not the exact semantic recovery")
            rejected(
                lambda value: value["advance"].update(
                    {
                        "kind": campaign.GHIDRA_SEMANTIC_ADVANCE_KIND,
                        "schema": campaign.GHIDRA_SEMANTIC_ADVANCE_SCHEMA,
                    }
                ),
                "not the exact semantic recovery",
            )
            rejected(
                lambda value: value["advance"].update({"branchId": "wrong"}),
                "not the exact semantic recovery",
            )
            rejected(
                lambda value: value["advance"]["historicalProjection"].update(
                    {"historicalAuthorityClass": "FULL_REPLAY_AUTHORITY"}
                ),
                "historical projection differs",
            )
            rejected(
                lambda value: value["advance"]["historicalProjection"][
                    "changedRows"
                ].update({"contracts": 28}),
                "historical projection differs",
            )
            rejected(
                lambda value: value["advance"]["historicalProjection"][
                    "canonicalLedgerSha256"
                ].update({"functions": "0" * 64}),
                "historical projection differs",
            )
            rejected(
                lambda value: value["advance"]["ownerRecovery"][
                    "recoveredOwner"
                ].update({"sha256": "0" * 64}),
                "owner recovery binding differs",
            )
            rejected(
                lambda value: value["advance"]["owner"].update(
                    {"sha256": "0" * 64}
                ),
                "changes historical evidence: owner",
            )
            rejected(
                lambda value: value.update({"sourceSnapshot": {}}),
                "source snapshot differs",
            )
            rejected(
                lambda value: value.update({"questionTypes": {}}),
                "question types differ",
            )
            rejected(
                lambda value: value.update({"policies": []}),
                "policies differ",
            )
            rejected(
                lambda value: value.update({"generatedAtUtc": "not-a-time"}),
                "has an invalid timestamp",
            )
            rejected(
                lambda value: value["outputs"].update({"extra.tsv": {}}),
                "output set differs",
            )
            rejected(
                lambda value: value["outputs"]["campaign-functions.tsv"].update(
                    {"authority": "invented"}
                ),
                "output stamp shape differs",
            )

            alternate_parent = (
                Path(__file__).resolve().parent.parent
                / "local-lab/re-campaign-incident-recovery-20260808-v1"
                / "generation-8-atomic14-recovered"
            )

            def alternate_8r_historical_kind(value) -> None:
                value["parentCampaign"] = {
                    "path": os.fspath(alternate_parent.resolve()),
                    "ready": {
                        **campaign.coverage.file_stamp(
                            alternate_parent / "campaign.ready.json"
                        ),
                        "path": "campaign.ready.json",
                    },
                }
                value["advance"]["kind"] = campaign.GHIDRA_SEMANTIC_ADVANCE_KIND
                value["advance"]["schema"] = campaign.GHIDRA_SEMANTIC_ADVANCE_SCHEMA

            rejected(
                alternate_8r_historical_kind,
                "not the exact semantic recovery",
            )

    def test_integrity_gate_rejects_unchanged_function_poison(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            functions_path = forged / "campaign-functions.tsv"
            functions = campaign._read_tsv(functions_path)
            target = next(row for row in functions if row["entryVa"] == "0x00401000")
            target["requiresElevation"] = (
                "False" if target["requiresElevation"] == "True" else "True"
            )
            campaign._write_tsv(functions_path, campaign.FUNCTION_COLUMNS, functions)
            ready_path = forged / "campaign.ready.json"
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            ready["outputs"]["campaign-functions.tsv"] = {
                **campaign.coverage.file_stamp(functions_path),
                "path": "campaign-functions.tsv",
            }
            ready_path.write_text(json.dumps(ready, indent=2) + "\n", encoding="utf-8")
            completed = self.frozen_verify(forged, replay=False)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("non-provenance state", completed.stderr)

    def test_owner_git_recovery_is_exact_and_rejects_git_poison(self) -> None:
        validated = campaign._validate_target_lock_owner_recovery(self.owner_recovery)
        recovered = Path(validated["recoveredOwner"]["path"])
        self.assertEqual(campaign.TARGET_LOCK_HISTORICAL_OWNER_BYTES,
                         recovered.stat().st_size)
        self.assertEqual(campaign.TARGET_LOCK_HISTORICAL_OWNER_SHA256,
                         hashlib.sha256(recovered.read_bytes()).hexdigest())
        current = Path(__file__).resolve().parent / "ghidra_target_lock_semantic_live_promotion.py"
        self.assertNotEqual(
            campaign.TARGET_LOCK_HISTORICAL_OWNER_SHA256,
            hashlib.sha256(current.read_bytes()).hexdigest(),
        )

        actual_run = campaign.subprocess.run

        def wrong_tree(argv, **kwargs):
            if argv[:2] == ["git", "ls-tree"]:
                return subprocess.CompletedProcess(argv, 0, "wrong\n", "")
            return actual_run(argv, **kwargs)

        with patch.object(campaign.subprocess, "run", side_effect=wrong_tree):
            with self.assertRaisesRegex(campaign.CampaignError, "does not reproduce"):
                campaign._validate_target_lock_owner_recovery(self.owner_recovery)

        def wrong_blob(argv, **kwargs):
            if argv[:3] == ["git", "cat-file", "blob"]:
                data = bytearray(recovered.read_bytes())
                data[-1] ^= 1
                return subprocess.CompletedProcess(argv, 0, bytes(data), b"")
            return actual_run(argv, **kwargs)

        with patch.object(campaign.subprocess, "run", side_effect=wrong_blob):
            with self.assertRaisesRegex(campaign.CampaignError, "does not reproduce"):
                campaign._validate_target_lock_owner_recovery(self.owner_recovery)

    def test_authority_files_must_be_plain_single_link_files(self) -> None:
        for relative, expected in (
            (
                Path("campaign.ready.json"),
                "campaign READY is not a plain single-link file",
            ),
            (
                Path("_reducer/tools/re_campaign.py"),
                "campaign reducer file is not plain/single-link",
            ),
        ):
            with self.subTest(relative=relative.as_posix()):
                with tempfile.TemporaryDirectory() as temporary:
                    forged = Path(temporary) / "forged"
                    shutil.copytree(self.generation, forged)
                    target = forged / relative
                    anchor = Path(temporary) / (relative.name + ".anchor")
                    shutil.copy2(target, anchor)
                    target.unlink()
                    os.link(anchor, target)
                    completed = self.frozen_verify(forged, replay=False)
                    self.assertNotEqual(0, completed.returncode)
                    self.assertIn(expected, completed.stderr)

    def test_unmanifested_reducer_module_is_rejected_before_import(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            marker = Path(temporary) / "shadow-module-executed.txt"
            (forged / "_reducer/tools/json.py").write_text(
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('EXECUTED', encoding='utf-8')\n",
                encoding="utf-8",
            )
            completed = self.frozen_verify(forged, replay=False)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("campaign reducer file set differs", completed.stderr)
            self.assertFalse(marker.exists(), "shadow module executed before rejection")


class CampaignRecoveryGeneration10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        cls.parent = base / "generation-9-target-lock-recovered-v2"
        cls.generation = base / "generation-10-ttd-call-context-recovered-v2"
        cls.replica = base / "generation-10-ttd-call-context-recovered-v2-replica"
        cls.evidence = (
            repo / "local-lab/ttd-call-context-level521-impact-schema3-20260804-v1"
        )
        if not (cls.parent / "campaign.ready.json").is_file():
            raise unittest.SkipTest("maintainer-local Generation 9R prerequisite is unavailable")
        for root in (cls.generation, cls.replica):
            if not (root / "campaign.ready.json").is_file():
                raise AssertionError(
                    f"required recovered Generation 10 is missing: {root}"
                )

    @staticmethod
    def frozen_verify(root: Path, *, replay: bool = True) -> subprocess.CompletedProcess:
        return CampaignRecoveryGeneration8Tests.frozen_verify(root, replay=replay)

    @staticmethod
    def reducer_files(root: Path) -> dict[str, bytes]:
        return CampaignRecoveryGeneration9Tests.reducer_files(root)

    @staticmethod
    def write_ready(root: Path, receipt: dict) -> None:
        (root / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def test_two_independent_builds_reproduce_and_fully_replay(self) -> None:
        self.assertEqual(["formalReady"], missing_atomic14_replay_inputs())
        expected_hashes = {
            "campaign-functions.tsv": "6b18eda4b537fa17aba9e41a519cc47fb3c41836f9ff9877cf735ebe7a8933f1",
            "campaign-residuals.tsv": "aa62128b8b472311ebd2c3279a59a354495855e8640e4dbaa1147d507efd25f2",
            "campaign-questions.tsv": "dc918c4c3fa507dba4e943cd842c8d0ada71961d14e7ed95f3d3238b067915ec",
            "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
            "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
            "campaign-contracts.tsv": "05f73d3dfdfcdbd454fad97f90d9f5c02094b26047e6b5d4648509f1eecfdf5a",
            "campaign-adjudications.tsv": "8693f81f9cf8531961460d09087b018c73b981246bdc839c88b438947e41ff0c",
            "campaign-supersessions.tsv": "7569852a3fe9aea25a4fcc4f6d17b6d9d81ff658f644b007bda1f50ae55559cb",
        }
        for name, digest in expected_hashes.items():
            self.assertEqual(digest, campaign.coverage.sha256_of(self.generation / name))
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        self.assertEqual(
            self.reducer_files(self.generation), self.reducer_files(self.replica)
        )

        receipts = []
        expected_ids = {
            "C-2f608ec63fd10347": "A-1836c8724e6ec854",
            "C-62b3c956518ff9a5": "A-198768719510d9d5",
            "C-a14d999cf14fbbe3": "A-59a5ffd7fe0634da",
        }
        for root in (self.generation, self.replica):
            completed = self.frozen_verify(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
            receipt = json.loads(
                (root / "campaign.ready.json").read_text(encoding="utf-8")
            )
            self.assertEqual(10, receipt["generation"])
            self.assertEqual(
                campaign.TTD_CALL_CONTEXT_EXPECTED_GENERATION10_COUNTS,
                receipt["counts"],
            )
            advance = receipt["advance"]
            self.assertEqual(campaign.TTD_CALL_CONTEXT_RECOVERY_ADVANCE_KIND, advance["kind"])
            self.assertEqual(campaign.TTD_CALL_CONTEXT_RECOVERY_ADVANCE_SCHEMA, advance["schema"])
            self.assertEqual("CO-eb39e64982981579", advance["observationId"])
            self.assertEqual(
                expected_ids,
                {
                    row["contractId"]: row["adjudicationId"]
                    for row in advance["promotions"]
                },
            )
            self.assertEqual(
                sorted(expected_ids.values()), advance["delta"]["adjudicationIdsAdded"]
            )
            self.assertEqual(
                {
                    "hashReadFromBoundReceipt": True,
                    "actualSizeVerified": True,
                    "actualHashVerified": False,
                    "currentContentIdentityClaimed": False,
                },
                {
                    key: advance["evidence"]["trace"][key]
                    for key in (
                        "hashReadFromBoundReceipt",
                        "actualSizeVerified",
                        "actualHashVerified",
                        "currentContentIdentityClaimed",
                    )
                },
            )
            projection = advance["historicalProjection"]
            self.assertEqual(
                campaign.TTD_CALL_CONTEXT_HISTORICAL_GENERATION10_READY_SHA256,
                projection["historicalReady"]["sha256"],
            )
            self.assertEqual(
                {
                    "functions": 0,
                    "residuals": 0,
                    "questions": 0,
                    "scenarios": 0,
                    "levers": 0,
                    "contracts": 29,
                    "adjudications": 4,
                    "supersessions": 29,
                },
                projection["changedRows"],
            )
            receipt["generatedAtUtc"] = "<generated>"
            for stamp in receipt["outputs"].values():
                stamp["lastWriteUtc"] = "<write>"
            receipts.append(receipt)
        self.assertEqual(receipts[0], receipts[1])

    def test_integrity_gate_rejects_ttd_recovery_laundering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            ready_path = forged / "campaign.ready.json"
            original = json.loads(ready_path.read_text(encoding="utf-8"))

            def rejected(mutator, expected: str) -> None:
                poisoned = json.loads(json.dumps(original))
                mutator(poisoned)
                self.write_ready(forged, poisoned)
                completed = self.frozen_verify(forged, replay=False)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(
                lambda value: value.update({"advance": None}),
                "not the exact TTD recovery",
            )
            rejected(
                lambda value: value["advance"].update(
                    {
                        "kind": campaign.TTD_CALL_CONTEXT_ADVANCE_KIND,
                        "schema": campaign.TTD_CALL_CONTEXT_ADVANCE_SCHEMA,
                    }
                ),
                "not the exact TTD recovery",
            )
            rejected(
                lambda value: value["advance"].update({"branchId": "wrong"}),
                "not the exact TTD recovery",
            )
            rejected(
                lambda value: value["advance"].update(
                    {"observationEvidenceMode": "RERUN"}
                ),
                "advance identity differs",
            )
            rejected(
                lambda value: value["advance"].update(
                    {"traceHashDisposition": "ACTUAL_HASH_VERIFIED"}
                ),
                "advance identity differs",
            )
            rejected(
                lambda value: value["advance"]["historicalProjection"].update(
                    {"historicalAuthorityClass": "FULL_REPLAY_AUTHORITY"}
                ),
                "historical projection",
            )
            rejected(
                lambda value: value["advance"]["historicalProjection"][
                    "changedRows"
                ].update({"contracts": 28}),
                "historical projection",
            )
            rejected(
                lambda value: value["advance"]["historicalProjection"][
                    "canonicalLedgerSha256"
                ].update({"functions": "0" * 64}),
                "historical projection",
            )
            historical_candidate = (
                Path(__file__).resolve().parent.parent
                / "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1"
                / "generation-10-ttd-call-context-observation"
                / "campaign.ready.json"
            )
            if historical_candidate.is_file():
                candidate_stamp = {
                    **campaign.coverage.file_stamp(historical_candidate),
                    "path": str(historical_candidate.resolve()),
                }
                rejected(
                    lambda value: value["advance"]["historicalProjection"].update(
                        {"historicalReady": candidate_stamp}
                    ),
                    "historical projection",
                )
            rejected(
                lambda value: value.update({"sourceSnapshot": {}}),
                "source snapshot differs",
            )
            rejected(
                lambda value: value.update({"questionTypes": {}}),
                "question types differ",
            )
            rejected(
                lambda value: value.update({"policies": []}),
                "policies differ",
            )
            rejected(
                lambda value: value.update({"generatedAtUtc": "not-a-time"}),
                "invalid timestamp",
            )
            rejected(
                lambda value: value["outputs"].update({"extra.tsv": {}}),
                "output set differs",
            )

    def test_integrity_gate_rejects_forged_adjudication_and_contract_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            ready_path = forged / "campaign.ready.json"

            adjudications_path = forged / "campaign-adjudications.tsv"
            adjudications = campaign._read_tsv(adjudications_path)
            target = next(
                row
                for row in adjudications
                if row["baseContractId"] == "C-2f608ec63fd10347"
            )
            old_id = target["adjudicationId"]
            target["adjudicationId"] = "A-0000000000000000"
            campaign._write_tsv(
                adjudications_path, campaign.ADJUDICATION_COLUMNS, adjudications
            )
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            promotion = next(
                row
                for row in ready["advance"]["promotions"]
                if row["contractId"] == "C-2f608ec63fd10347"
            )
            promotion["adjudicationId"] = "A-0000000000000000"
            ready["advance"]["delta"]["adjudicationIdsAdded"] = sorted(
                "A-0000000000000000" if value == old_id else value
                for value in ready["advance"]["delta"]["adjudicationIdsAdded"]
            )
            ready["outputs"]["campaign-adjudications.tsv"] = {
                **campaign.coverage.file_stamp(adjudications_path),
                "path": "campaign-adjudications.tsv",
            }
            self.write_ready(forged, ready)
            completed = self.frozen_verify(forged, replay=False)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("exact historical projection", completed.stderr)

        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            contracts_path = forged / "campaign-contracts.tsv"
            contracts = campaign._read_tsv(contracts_path)
            target = next(
                row for row in contracts if row["contractId"] == "C-2f608ec63fd10347"
            )
            target["writes"] = "FORGED_WRITE_CLAIM"
            campaign._write_tsv(contracts_path, campaign.CONTRACT_COLUMNS, contracts)
            ready_path = forged / "campaign.ready.json"
            ready = json.loads(ready_path.read_text(encoding="utf-8"))
            ready["outputs"]["campaign-contracts.tsv"] = {
                **campaign.coverage.file_stamp(contracts_path),
                "path": "campaign-contracts.tsv",
            }
            self.write_ready(forged, ready)
            completed = self.frozen_verify(forged, replay=False)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("non-provenance state", completed.stderr)

    def test_authority_and_evidence_modules_are_rejected_before_import(self) -> None:
        for relative, expected in (
            (Path("campaign.ready.json"), "campaign READY is not a plain single-link file"),
            (
                Path("_reducer/tools/re_campaign.py"),
                "campaign reducer file is not plain/single-link",
            ),
        ):
            with self.subTest(relative=relative.as_posix()):
                with tempfile.TemporaryDirectory() as temporary:
                    forged = Path(temporary) / "forged"
                    shutil.copytree(self.generation, forged)
                    target = forged / relative
                    anchor = Path(temporary) / (relative.name + ".anchor")
                    shutil.copy2(target, anchor)
                    target.unlink()
                    os.link(anchor, target)
                    completed = self.frozen_verify(forged, replay=False)
                    self.assertNotEqual(0, completed.returncode)
                    self.assertIn(expected, completed.stderr)

        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            marker = Path(temporary) / "reducer-shadow-executed.txt"
            (forged / "_reducer/tools/json.py").write_text(
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('EXECUTED', encoding='utf-8')\n",
                encoding="utf-8",
            )
            completed = self.frozen_verify(forged, replay=False)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("campaign reducer file set differs", completed.stderr)
            self.assertFalse(marker.exists())

        with tempfile.TemporaryDirectory() as temporary:
            lab = Path(temporary) / "local-lab"
            copied_evidence = lab / self.evidence.name
            shutil.copytree(self.evidence, copied_evidence)
            marker = Path(temporary) / "evidence-shadow-executed.txt"
            (copied_evidence / "json.py").write_text(
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('EXECUTED', encoding='utf-8')\n",
                encoding="utf-8",
            )
            parent_receipt = json.loads(
                (self.parent / "campaign.ready.json").read_text(encoding="utf-8")
            )
            with patch.object(campaign, "_FROZEN_LOCAL_LAB", lab), patch.object(
                campaign, "TTD_CALL_CONTEXT_EVIDENCE_RELATIVE", copied_evidence
            ):
                with self.assertRaisesRegex(campaign.CampaignError, "evidence file set differs"):
                    campaign.validate_ttd_call_context_observation(
                        self.parent,
                        copied_evidence,
                        _verified_campaign_receipt=parent_receipt,
                        _recovery_profile=True,
                    )
            self.assertFalse(marker.exists())


class CampaignRecoveryGeneration11Tests(unittest.TestCase):
    AUTHORITY_REDUCER_ID = (
        "e88c973967a0458f500ff2cc1508d417b60487a4886703c4bd3dcfd197246993"
    )
    AUTHORITY_READY_SHA256 = {
        "generation-11-gen73-claims-resealed-v2": (
            "9b3769c503f003b34d3915047be28c24036567f260de1933591f0254d992686d"
        ),
        "generation-11-gen73-claims-resealed-replica-v2": (
            "755168fb8b8ff480fe4458792ef9ad3225e7cd0c4cbe6b59395f671c5ce0b463"
        ),
    }

    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        cls.parent = base / "generation-10-ttd-call-context-recovered-v2"
        cls.closure = base / "gen73-claim-closure-v1"
        cls.generation = base / "generation-11-gen73-claims-resealed-v2"
        cls.replica = base / "generation-11-gen73-claims-resealed-replica-v2"
        cls.authority = base / "generation-11-recovery-authority.ready.json"
        if not (cls.parent / "campaign.ready.json").is_file():
            raise unittest.SkipTest("maintainer-local canonical 10R prerequisite is unavailable")
        for root, label in (
            (cls.closure, "claim closure"),
            (cls.generation, "canonical Generation 11"),
            (cls.replica, "replicated Generation 11"),
        ):
            ready_name = "closure.ready.json" if root == cls.closure else "campaign.ready.json"
            if not (root / ready_name).is_file():
                raise AssertionError(f"required {label} is missing: {root}")

    @staticmethod
    def frozen_verify(root: Path, *, replay: bool = True) -> subprocess.CompletedProcess:
        return CampaignRecoveryGeneration8Tests.frozen_verify(root, replay=replay)

    @classmethod
    def authority_verify(cls, root: Path) -> subprocess.CompletedProcess:
        expected_ready = cls.AUTHORITY_READY_SHA256.get(root.name)
        if expected_ready is None:
            raise AssertionError(f"root is not an externally selected Gen11 authority: {root}")
        repo = Path(__file__).resolve().parent.parent
        bootstrap = Path(__file__).resolve().parent / "re_campaign_frozen_bootstrap.py"
        environment = os.environ.copy()
        environment["BEA_REPO_ROOT"] = os.fspath(repo)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                os.fspath(Path(os.sys.executable)),
                "-I",
                "-B",
                os.fspath(bootstrap),
                "--campaign",
                os.fspath(root),
                "--mode",
                "full",
                "--expected-ready-sha256",
                expected_ready,
                "--expected-reducer-id",
                cls.AUTHORITY_REDUCER_ID,
            ],
            cwd=repo,
            env=environment,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )

    @staticmethod
    def reducer_files(root: Path) -> dict[str, bytes]:
        return CampaignRecoveryGeneration9Tests.reducer_files(root)

    @staticmethod
    def write_ready(root: Path, receipt: dict) -> None:
        (root / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def test_two_independent_builds_are_deterministic_and_fully_replay(self) -> None:
        expected_hashes = {
            "campaign-functions.tsv": "a0ad6ff40d6188d66b73d651305d11cda70ebe43d0ae1fcb85aa2d9f26a5f494",
            "campaign-residuals.tsv": "30d390b75a9984efc6bebedf5ddb00412326d36e51d2c9f3c1883032dd25ef49",
            "campaign-questions.tsv": "8be824b54e1cd665ae901d68611f88269430ffd1a76b230de4e30831aed53c3d",
            "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
            "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
            "campaign-contracts.tsv": "d15311626833cf3202ad99d36f76f87b17f3a8c51ea1876a76f44223006f8d83",
            "campaign-adjudications.tsv": "5e002a12364a7b1da4b09b5fdf1e4a51d42d236ced2bf6f3efa474a934378f99",
            "campaign-supersessions.tsv": "7569852a3fe9aea25a4fcc4f6d17b6d9d81ff658f644b007bda1f50ae55559cb",
        }
        for name, digest in expected_hashes.items():
            self.assertEqual(digest, campaign.coverage.sha256_of(self.generation / name))
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        self.assertEqual(self.reducer_files(self.generation), self.reducer_files(self.replica))

        normalized = []
        for root in (self.generation, self.replica):
            completed = self.authority_verify(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
            receipt = json.loads((root / "campaign.ready.json").read_text(encoding="utf-8"))
            self.assertEqual(11, receipt["generation"])
            self.assertEqual(gen73_reseal.EXPECTED_COUNTS, receipt["counts"])
            self.assertEqual(campaign.GEN73_RESEAL_RECOVERY_ADVANCE_KIND, receipt["advance"]["kind"])
            self.assertEqual(campaign.GEN73_RESEAL_RECOVERY_ADVANCE_SCHEMA, receipt["advance"]["schema"])
            self.assertEqual("SUPERSEDED_PROJECTION_ORACLE_NOT_PARENT", receipt["advance"]["candidateTipDisposition"])
            self.assertEqual(6082, receipt["advance"]["newAdjudications"]["count"])
            self.assertFalse(receipt["advance"]["newAdjudications"]["semanticPromotionApplied"])
            receipt["generatedAtUtc"] = "<generated>"
            for stamp in receipt["outputs"].values():
                stamp["lastWriteUtc"] = "<write>"
            normalized.append(receipt)
        self.assertEqual(normalized[0], normalized[1])

    def test_reseal_boundary_preserves_valid_claims_and_quarantines_overclaims(self) -> None:
        rows = {
            family: campaign._read_tsv(self.generation / name)
            for family, name in zip(gen73_reseal.LEDGER_KEYS, campaign.OUTPUTS)
        }
        functions_by_va = {row["entryVa"].lower(): row for row in rows["functions"]}
        contracts_by_entity = {row["entityKey"]: row for row in rows["contracts"]}
        for va in (
            "0x00535590", "0x00535a30", "0x005367c0", "0x00536920",
            "0x00537ad0", "0x00537c70", "0x00537e40",
        ):
            function = functions_by_va[va]
            contract = contracts_by_entity[function["entityKey"]]
            self.assertEqual("OPAQUE", function["semanticGrade"])
            self.assertEqual("OPEN_JOIN", function["resolutionState"])
            self.assertEqual("C0_OPAQUE", contract["semanticGrade"])
            self.assertEqual("OPEN", contract["contractState"])
            self.assertEqual("UNSCORED", contract["refuterVerdict"])

        apply_damage = functions_by_va["0x004f9a90"]
        apply_contract = contracts_by_entity[apply_damage["entityKey"]]
        self.assertEqual("C1_CANDIDATE_PARTIAL", apply_damage["semanticGrade"])
        self.assertEqual("C1_CANDIDATE_PARTIAL", apply_contract["semanticGrade"])
        self.assertEqual("CANDIDATE_NEEDS_REFUTER", apply_contract["contractState"])
        self.assertEqual("UNSCORED", apply_contract["refuterVerdict"])
        self.assertNotIn("61295806d62f68e6", apply_contract["evidenceRefs"])

        near_clone = functions_by_va["0x0056473e"]
        self.assertEqual("FUN_0056473e", near_clone["currentName"])
        self.assertEqual("OPAQUE", near_clone["semanticGrade"])
        self.assertEqual("UNKNOWN_WITH_FALSIFIER", near_clone["resolutionState"])

        parent_residuals = {
            row["entityKey"]: row for row in campaign._read_tsv(self.parent / "campaign-residuals.tsv")
        }
        output_residuals = {row["entityKey"]: row for row in rows["residuals"]}
        closure = gen73_reseal.derive_projection()
        self.assertEqual(20, len(closure["preservedPolice"]))
        for entity in closure["preservedPolice"]:
            self.assertEqual(parent_residuals[entity], output_residuals[entity])
            self.assertEqual("OPEN_CLASSIFICATION", output_residuals[entity]["terminalState"])
        self.assertNotIn(closure["reclosedPolice"], closure["preservedPolice"])

        function_names = {row["entityKey"]: row["currentName"] for row in rows["functions"]}
        self.assertTrue(
            all(
                contract["currentName"] == function_names[contract["entityKey"]]
                for contract in rows["contracts"]
                if contract["entityKind"] == "FUNCTION"
            )
        )

    def test_exact_parent_provenance_and_new_nonsemantic_adjudications(self) -> None:
        receipt = json.loads((self.generation / "campaign.ready.json").read_text(encoding="utf-8"))
        self.assertEqual(campaign.GEN73_RESEAL_PARENT_READY_SHA256, receipt["parentCampaign"]["ready"]["sha256"])
        self.assertNotEqual(gen73_reseal.CANDIDATE_READY_SHA256, receipt["parentCampaign"]["ready"]["sha256"])
        closure_ready = gen73_reseal.verify_closure(self.closure)
        self.assertEqual(campaign.GEN73_RESEAL_CLOSURE_READY_SHA256, campaign.coverage.sha256_of(self.closure / "closure.ready.json"))
        self.assertEqual(7294, closure_ready["accounting"]["sourceAdjudications"])

        parent_adjudications = campaign._read_tsv(self.parent / "campaign-adjudications.tsv")
        output_adjudications = campaign._read_tsv(self.generation / "campaign-adjudications.tsv")
        parent_ids = {row["adjudicationId"] for row in parent_adjudications}
        candidate_ids = {
            row["adjudicationId"]
            for row in campaign._read_tsv(
                gen73_reseal.REPO_ROOT / gen73_reseal.CANDIDATE_RELATIVE / "campaign-adjudications.tsv"
            )
        }
        self.assertEqual(6, len(parent_ids))
        self.assertTrue(parent_ids <= {row["adjudicationId"] for row in output_adjudications})
        new_rows = [row for row in output_adjudications if row["adjudicationId"] not in parent_ids]
        self.assertEqual(6082, len(new_rows))
        self.assertFalse({row["adjudicationId"] for row in new_rows} & candidate_ids)
        self.assertTrue(all(row["semanticPromotionApplied"] == "False" for row in new_rows))
        self.assertTrue(all(row["overlayReadySha256"] == campaign.GEN73_RESEAL_CLOSURE_READY_SHA256 for row in new_rows))

        parent_supersessions = (self.parent / "campaign-supersessions.tsv").read_bytes()
        self.assertEqual(parent_supersessions, (self.generation / "campaign-supersessions.tsv").read_bytes())
        contracts = {row["contractId"]: row for row in campaign._read_tsv(self.generation / "campaign-contracts.tsv")}
        derived = gen73_reseal.derive_projection()
        self.assertEqual(29, len(derived["recoveryContractIds"]))
        for contract_id in derived["recoveryContractIds"]:
            self.assertIn("8a83b9617de616d6", contracts[contract_id]["evidenceRefs"])
            self.assertNotIn("a504c24b1eab555d", contracts[contract_id]["evidenceRefs"])

    def test_external_authority_receipt_selects_only_canonical_v2(self) -> None:
        self.assertTrue(self.authority.is_file(), f"missing authority receipt: {self.authority}")
        self.assertFalse(self.authority.is_symlink())
        self.assertEqual(1, self.authority.stat().st_nlink)
        self.assertEqual(10_501, self.authority.stat().st_size)
        self.assertEqual(
            "2594d78d7ec6b4908ecfba9509122fedbe1959ff0e5eeaceb6d1164ae758238c",
            campaign.coverage.sha256_of(self.authority),
        )
        receipt = json.loads(self.authority.read_text(encoding="utf-8"))
        self.assertEqual("bea.re.campaign-incident-recovery-authority.v2", receipt["schema"])
        self.assertEqual("READY", receipt["verdict"])
        self.assertEqual("FULL_REPLAY_RECOVERY_BRANCH_BOUNDARY", receipt["authorityClass"])
        self.assertEqual("FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_OR_TTD_REPLAY", receipt["replayScope"])
        self.assertEqual("incident-20260806-recovery-v1", receipt["lineageId"])
        self.assertEqual(os.fspath(self.generation.resolve()), receipt["canonical"]["absolutePath"])
        self.assertEqual(os.fspath(self.replica.resolve()), receipt["replica"]["absolutePath"])
        self.assertEqual(
            self.AUTHORITY_READY_SHA256[self.generation.name],
            receipt["canonical"]["ready"]["sha256"],
        )
        self.assertEqual(
            self.AUTHORITY_READY_SHA256[self.replica.name],
            receipt["replica"]["ready"]["sha256"],
        )
        self.assertEqual(self.AUTHORITY_REDUCER_ID, receipt["canonical"]["reducerId"])
        self.assertEqual(self.AUTHORITY_REDUCER_ID, receipt["replica"]["reducerId"])
        self.assertEqual("REPRODUCTION_ONLY_NOT_AUTHORITY_SELECTOR", receipt["replica"]["role"])
        self.assertEqual(
            os.fspath(self.generation.resolve()),
            receipt["selectionRule"]["requiredAbsolutePath"],
        )
        self.assertEqual(
            {
                "path": (
                    "local-lab/re-campaign-incident-recovery-20260808-v1/"
                    "generation-10-ttd-call-context-recovered-v2"
                ),
                "readySha256": "12cb61f9d8cad06cd0c58ca5262a9c497a62d7268fc108d546ed988b9a757561",
                "reducerId": "88d61c227970ead0807e110ff14712ca74fcf23ce51b4bc88434b98bc0e956d4",
                "authorityReceiptSha256": "dd41e3b01ae410bdcfc9c1a0b273b15e45b5829d13fb6247a3a7e6fce54ac61b",
            },
            receipt["parent"],
        )
        self.assertEqual(
            {
                "path": (
                    "local-lab/re-campaign-incident-recovery-20260808-v1/"
                    "generation-11-gen73-claims-resealed-v2/_reducer/tools/"
                    "re_campaign_frozen_bootstrap.py"
                ),
                "bytes": 15_209,
                "sha256": "5f4725569e3e1578fa2a963d2ea6046ad0dbba6653e6fc76491ec8024fc37f0e",
            },
            receipt["frozenOwners"]["preImportLauncher"],
        )
        self.assertEqual(campaign.GEN73_RESEAL_CLOSURE_READY_SHA256, receipt["closure"]["readySha256"])
        self.assertEqual(gen73_reseal.CANDIDATE_READY_SHA256, receipt["candidateProjectionOracle"]["readySha256"])
        self.assertEqual("SUPERSEDED_NOT_PARENT_NOT_AUTHORITY", receipt["candidateProjectionOracle"]["disposition"])
        self.assertEqual(
            self.AUTHORITY_READY_SHA256,
            receipt["selectionRule"]["literalReadySha256ByRoot"],
        )
        self.assertEqual(self.AUTHORITY_REDUCER_ID, receipt["selectionRule"]["requiredReducerId"])
        self.assertEqual("FULL", receipt["selectionRule"]["requiredMode"])
        for root, role in ((self.generation, "canonical"), (self.replica, "replica")):
            ready_path = root / "campaign.ready.json"
            self.assertEqual(receipt[role]["ready"]["bytes"], ready_path.stat().st_size)
            self.assertEqual(receipt[role]["ready"]["sha256"], campaign.coverage.sha256_of(ready_path))
        for name, expected in receipt["outputs"].items():
            self.assertEqual(expected["bytes"], (self.generation / name).stat().st_size)
            self.assertEqual(expected["sha256"], campaign.coverage.sha256_of(self.generation / name))

    def test_integrity_gate_rejects_metadata_and_row_laundering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            ready_path = forged / "campaign.ready.json"
            original = json.loads(ready_path.read_text(encoding="utf-8"))

            def rejected(mutator, expected: str) -> None:
                receipt = json.loads(json.dumps(original))
                mutator(receipt)
                self.write_ready(forged, receipt)
                completed = self.frozen_verify(forged, replay=False)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(lambda value: value.update({"advance": None}), "reseal advance is missing")
            rejected(
                lambda value: value["advance"].update({"kind": "GEN73_CANDIDATE_CARRY"}),
                "reseal identity differs",
            )
            rejected(
                lambda value: value["parentCampaign"]["ready"].update(
                    {"sha256": gen73_reseal.CANDIDATE_READY_SHA256}
                ),
                "campaign parent READY differs",
            )
            rejected(
                lambda value: value.update({"generatedAtUtc": "not-a-time"}),
                "invalid timestamp",
            )
            rejected(
                lambda value: value.update({"sourceSnapshot": {}}),
                "source snapshot differs",
            )
            rejected(
                lambda value: value.update({"questionTypes": {}}),
                "question types differ",
            )
            rejected(
                lambda value: value.update({"policies": []}),
                "policies differ",
            )
            rejected(
                lambda value: value["outputs"].update({"extra.tsv": {}}),
                "output set differs",
            )

        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            contracts_path = forged / "campaign-contracts.tsv"
            contracts = campaign._read_tsv(contracts_path)
            target = next(row for row in contracts if row["entityKey"] == gen73_reseal.APPLY_DAMAGE_ENTITY)
            target["semanticGrade"] = "C2_BOUNDED_RUNTIME"
            target["contractState"] = "BOUNDED_CONTRACT_ADVANCED"
            campaign._write_tsv(contracts_path, campaign.CONTRACT_COLUMNS, contracts)
            ready = json.loads((forged / "campaign.ready.json").read_text(encoding="utf-8"))
            ready["outputs"]["campaign-contracts.tsv"] = {
                **campaign.coverage.file_stamp(contracts_path),
                "path": "campaign-contracts.tsv",
            }
            self.write_ready(forged, ready)
            completed = self.frozen_verify(forged, replay=False)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("contracts rows do not reproduce", completed.stderr)

        for relative, expected in (
            (Path("campaign.ready.json"), "campaign READY is not a plain single-link file"),
            (
                Path("campaign-functions.tsv"),
                "output has multiple hard links: campaign-functions.tsv",
            ),
        ):
            with self.subTest(relative=relative.as_posix()):
                with tempfile.TemporaryDirectory() as temporary:
                    forged = Path(temporary) / "forged"
                    shutil.copytree(self.generation, forged)
                    target = forged / relative
                    anchor = Path(temporary) / (relative.name + ".anchor")
                    shutil.copy2(target, anchor)
                    target.unlink()
                    os.link(anchor, target)
                    completed = self.frozen_verify(forged, replay=False)
                    self.assertNotEqual(0, completed.returncode)
                    self.assertIn(expected, completed.stderr)


class CampaignRecoveryGeneration12DamageWritesTests(unittest.TestCase):
    AUTHORITY_RECEIPT_BYTES = 8456
    AUTHORITY_RECEIPT_SHA256 = (
        "c3531b495084ec73fc2b76a70be3409ca120448ba6831cbfa96a70866e182cba"
    )
    AUTHORITY_AUTHOR_SHA256 = (
        "c8f2a9160fc5c0e650680e9efdb6e3c4fef1177abfda2aaf787c92cfb475dbeb"
    )
    AUTHORITY_BOOTSTRAP_SHA256 = (
        "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b"
    )
    AUTHORITY_REDUCER_ID = (
        "1bcd8b1bff0bd9182872c221df8060aff8da263a89d94052ede2e80127812385"
    )
    AUTHORITY_READY_SHA256 = {
        "generation-12-level521-damage-hit-writes-v1": (
            "9d2b903d451cb62fd6fb599b915dd57a0e6f313e610a348022fabf26ee265747"
        ),
        "generation-12-level521-damage-hit-writes-replica-v1": (
            "0635f8bb828cc4bb1f325bb2fc50d385597a38a999d91d3af3ff38dfb86c9319"
        ),
    }
    OUTPUT_SHA256 = {
        "campaign-functions.tsv": "f129dcb3f894cb3822fb320e7627b487a345b1c7b64183c4a79d87b9d764a516",
        "campaign-residuals.tsv": "30d390b75a9984efc6bebedf5ddb00412326d36e51d2c9f3c1883032dd25ef49",
        "campaign-questions.tsv": "86f1d48e2f92950926a3acfe7b3c4219ad778e3b2e19c627202b7053f5866782",
        "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
        "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
        "campaign-contracts.tsv": "da9e8cbc0afe26a6d83cd68e6cab289d17a12f7a3818bf1dc2da193aca6a23da",
        "campaign-adjudications.tsv": "b31ed77711ebcde4cd878cf9e846fa065c2f1def0e7c135d7650dd3e465e16b5",
        "campaign-supersessions.tsv": "7569852a3fe9aea25a4fcc4f6d17b6d9d81ff658f644b007bda1f50ae55559cb",
    }

    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        cls.parent = base / "generation-11-gen73-claims-resealed-v2"
        cls.generation = base / "generation-12-level521-damage-hit-writes-v1"
        cls.replica = base / "generation-12-level521-damage-hit-writes-replica-v1"
        cls.authority = base / "generation-12-level521-damage-hit-writes-authority.ready.json"
        cls.proof = repo / campaign.LEVEL521_DAMAGE_WRITES_PROOF_RELATIVE
        if not (cls.parent / "campaign.ready.json").is_file():
            raise unittest.SkipTest("maintainer-local canonical Gen11 prerequisite is unavailable")
        for root, label in (
            (cls.proof, "Level 521 Damage/Hit proof"),
            (cls.generation, "canonical Generation 12"),
            (cls.replica, "replicated Generation 12"),
        ):
            ready_name = "proof.ready.json" if root == cls.proof else "campaign.ready.json"
            if not (root / ready_name).is_file():
                raise AssertionError(f"required {label} is missing: {root}")
        if not cls.authority.is_file():
            raise AssertionError(f"required Generation 12 authority receipt is missing: {cls.authority}")

    @classmethod
    def authority_verify(cls, root: Path) -> subprocess.CompletedProcess:
        expected_ready = cls.AUTHORITY_READY_SHA256.get(root.name)
        if expected_ready is None:
            raise AssertionError(f"root is not an externally selected Gen12 copy: {root}")
        repo = Path(__file__).resolve().parent.parent
        bootstrap = Path(__file__).resolve().parent / "re_campaign_frozen_bootstrap.py"
        environment = os.environ.copy()
        environment["BEA_REPO_ROOT"] = os.fspath(repo)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                os.fspath(Path(os.sys.executable)),
                "-I",
                "-B",
                os.fspath(bootstrap),
                "--campaign",
                os.fspath(root),
                "--mode",
                "full",
                "--expected-ready-sha256",
                expected_ready,
                "--expected-reducer-id",
                cls.AUTHORITY_REDUCER_ID,
            ],
            cwd=repo,
            env=environment,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )

    @staticmethod
    def frozen_verify(root: Path, *, replay: bool = False) -> subprocess.CompletedProcess:
        return CampaignRecoveryGeneration8Tests.frozen_verify(root, replay=replay)

    @staticmethod
    def reducer_files(root: Path) -> dict[str, bytes]:
        return CampaignRecoveryGeneration9Tests.reducer_files(root)

    @staticmethod
    def write_ready(root: Path, receipt: dict) -> None:
        (root / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def test_two_independent_builds_are_deterministic_and_fully_replay(self) -> None:
        for name, digest in self.OUTPUT_SHA256.items():
            self.assertEqual(digest, campaign.coverage.sha256_of(self.generation / name))
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        self.assertEqual(self.reducer_files(self.generation), self.reducer_files(self.replica))
        normalized = []
        for root in (self.generation, self.replica):
            completed = self.authority_verify(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
            receipt = json.loads((root / "campaign.ready.json").read_text(encoding="utf-8"))
            self.assertEqual(12, receipt["generation"])
            self.assertEqual(
                campaign.LEVEL521_DAMAGE_WRITES_EXPECTED_GENERATION12_COUNTS,
                receipt["counts"],
            )
            self.assertEqual(campaign.LEVEL521_DAMAGE_WRITES_ADVANCE_KIND, receipt["advance"]["kind"])
            self.assertEqual(campaign.LEVEL521_DAMAGE_WRITES_ADVANCE_SCHEMA, receipt["advance"]["schema"])
            self.assertEqual("DW-073a47ed96f6d5a4", receipt["advance"]["observationId"])
            receipt["generatedAtUtc"] = "<generated>"
            for stamp in receipt["outputs"].values():
                stamp["lastWriteUtc"] = "<write>"
            normalized.append(receipt)
        self.assertEqual(normalized[0], normalized[1])

    def test_external_authority_receipt_selects_only_canonical_generation12(self) -> None:
        repo = Path(__file__).resolve().parent.parent
        author = repo / "tools/re_level521_damage_writes_authority.py"
        bootstrap = repo / "tools/re_campaign_frozen_bootstrap.py"
        self.assertEqual(self.AUTHORITY_RECEIPT_BYTES, self.authority.stat().st_size)
        self.assertEqual(
            self.AUTHORITY_RECEIPT_SHA256,
            campaign.coverage.sha256_of(self.authority),
        )
        receipt = json.loads(self.authority.read_text(encoding="utf-8"))
        self.assertEqual("bea.re.level521-damage-hit-generation12-authority.v1", receipt["schema"])
        self.assertEqual("READY", receipt["verdict"])
        self.assertEqual("FULL_REPLAY_CAMPAIGN_AUTHORITY", receipt["authorityClass"])
        self.assertEqual(
            "FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY",
            receipt["replayScope"],
        )
        self.assertEqual(str(self.generation.resolve()), receipt["canonical"]["absolutePath"])
        self.assertEqual(str(self.replica.resolve()), receipt["replica"]["absolutePath"])
        self.assertEqual(
            "REPRODUCTION_ONLY_NOT_AUTHORITY_SELECTOR", receipt["replica"]["role"]
        )
        self.assertEqual(str(self.generation.resolve()), receipt["selectionRule"]["requiredAbsolutePath"])
        self.assertEqual(self.AUTHORITY_READY_SHA256, receipt["selectionRule"]["literalReadySha256ByRoot"])
        self.assertEqual(self.AUTHORITY_REDUCER_ID, receipt["selectionRule"]["requiredReducerId"])
        self.assertEqual("FULL", receipt["selectionRule"]["requiredMode"])
        self.assertEqual(
            "9b3769c503f003b34d3915047be28c24036567f260de1933591f0254d992686d",
            receipt["parent"]["readySha256"],
        )
        self.assertEqual(
            "2594d78d7ec6b4908ecfba9509122fedbe1959ff0e5eeaceb6d1164ae758238c",
            receipt["parent"]["authorityReceiptSha256"],
        )
        self.assertEqual(campaign.LEVEL521_DAMAGE_WRITES_PROOF_READY_SHA256, receipt["proof"]["readySha256"])
        self.assertEqual(campaign.LEVEL521_DAMAGE_WRITES_PROOF_AUTHOR_SHA256, receipt["proof"]["authorSha256"])
        self.assertEqual(campaign.LEVEL521_DAMAGE_WRITES_EXPECTED_GENERATION12_COUNTS, receipt["counts"])
        self.assertEqual(self.OUTPUT_SHA256, {name: stamp["sha256"] for name, stamp in receipt["outputs"].items()})
        self.assertEqual(13, receipt["limitations"]["nextValidGeneration"])
        self.assertFalse(receipt["limitations"]["liveGhidraMutation"])
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, campaign.coverage.sha256_of(author))
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, receipt["author"]["sha256"])
        self.assertEqual(self.AUTHORITY_BOOTSTRAP_SHA256, campaign.coverage.sha256_of(bootstrap))
        self.assertEqual(
            self.AUTHORITY_BOOTSTRAP_SHA256,
            receipt["frozenOwners"]["preImportLauncher"]["sha256"],
        )
        for root_name, section in (
            (self.generation.name, "canonicalLiteralPinnedFullReplay"),
            (self.replica.name, "replicaLiteralPinnedFullReplay"),
        ):
            replay = receipt["verification"][section]
            self.assertEqual(0, replay["exitCode"])
            self.assertEqual("CAMPAIGN_VERIFIED", replay["marker"])
            self.assertEqual(
                self.AUTHORITY_READY_SHA256[root_name],
                replay["command"][replay["command"].index("--expected-ready-sha256") + 1],
            )
            self.assertEqual(
                self.AUTHORITY_REDUCER_ID,
                replay["command"][replay["command"].index("--expected-reducer-id") + 1],
            )
            self.assertEqual(bootstrap.resolve(), Path(replay["command"][3]).resolve())

    def test_exact_two_row_contract_and_partial_parity_advance(self) -> None:
        parent_functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.parent / "campaign-functions.tsv")
        }
        functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.generation / "campaign-functions.tsv")
        }
        parent_contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-contracts.tsv")
        }
        contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-contracts.tsv")
        }
        changed_functions = {
            key for key in functions if functions[key] != parent_functions[key]
        }
        changed_contracts = {
            key for key in contracts if contracts[key] != parent_contracts[key]
        }
        specs = campaign._level521_damage_writes_specs()
        self.assertEqual(
            {str(spec["entityKey"]) for spec in specs.values()}, changed_functions
        )
        self.assertEqual(
            {str(spec["contractId"]) for spec in specs.values()}, changed_contracts
        )
        damage = contracts["C-62b3c956518ff9a5"]
        hit = contracts["C-2f608ec63fd10347"]
        self.assertEqual("CBattleEngine__Damage", damage["currentName"])
        self.assertIn("+0x100 mShields", damage["writes"])
        self.assertIn("+0xFC mEnergy", damage["writes"])
        self.assertIn("across five gaps", damage["failureModes"])
        self.assertEqual("PARTIAL_CONTRACT", damage["rebuildState"])
        self.assertEqual(
            "OnslaughtRebuild.Core.Level100PlayerDamage.Apply",
            damage["rebuildImplementation"],
        )
        self.assertEqual("CBattleEngine__Hit", hit["currentName"])
        self.assertIn("seven watched fields", hit["writes"])
        self.assertIn("all other memory is outside this control", hit["writes"])
        self.assertEqual("NOT_READY", hit["rebuildState"])
        self.assertNotIn("MAINTAINER_GHIDRA_SEMANTIC_PROMOTED", functions[specs["0x0040a890"]["entityKey"]]["evidenceStates"])
        for name in (
            "campaign-residuals.tsv",
            "campaign-scenarios.tsv",
            "campaign-levers.tsv",
            "campaign-supersessions.tsv",
        ):
            self.assertEqual((self.parent / name).read_bytes(), (self.generation / name).read_bytes(), name)

    def test_exact_questions_adjudications_and_proof_boundary(self) -> None:
        parent_questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-questions.tsv")
        }
        questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-questions.tsv")
        }
        self.assertEqual(
            {"Q-dc20c0ae0488b9f1", "Q-f786eb45230f7d43"},
            set(questions) - set(parent_questions),
        )
        for parent, successor in (
            ("Q-c3a67dd02f317206", "Q-dc20c0ae0488b9f1"),
            ("Q-657753f5f004e39b", "Q-f786eb45230f7d43"),
        ):
            self.assertEqual("CLOSED_SURVIVED", questions[parent]["state"])
            self.assertEqual("OPEN", questions[successor]["state"])
            self.assertEqual(parent, questions[successor]["parentQuestionId"])
        parent_adjudications = {
            row["adjudicationId"]
            for row in campaign._read_tsv(self.parent / "campaign-adjudications.tsv")
        }
        adjudications = campaign._read_tsv(self.generation / "campaign-adjudications.tsv")
        fresh = [row for row in adjudications if row["adjudicationId"] not in parent_adjudications]
        self.assertEqual({"A-2b0389d42d79a795", "A-e1aa3cc450894a11"}, {row["adjudicationId"] for row in fresh})
        self.assertTrue(all(row["semanticPromotionApplied"] == "True" for row in fresh))
        self.assertTrue(all(row["overlayReadySha256"] == campaign.LEVEL521_DAMAGE_WRITES_PROOF_READY_SHA256 for row in fresh))
        self.assertEqual(
            campaign.LEVEL521_DAMAGE_WRITES_PROOF_READY_SHA256,
            campaign.coverage.sha256_of(self.proof / "proof.ready.json"),
        )

    def test_frozen_integrity_rejects_metadata_row_and_link_laundering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            ready_path = forged / "campaign.ready.json"
            original = json.loads(ready_path.read_text(encoding="utf-8"))

            def rejected(mutator, expected: str) -> None:
                receipt = json.loads(json.dumps(original))
                mutator(receipt)
                self.write_ready(forged, receipt)
                completed = self.frozen_verify(forged)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(lambda value: value.update({"advance": None}), "exact Level 521 Damage/Hit advance")
            rejected(lambda value: value["advance"].update({"kind": "TTD_DATA_WRITE_GUESS"}), "exact Level 521 Damage/Hit advance")
            rejected(lambda value: value.update({"generatedAtUtc": "not-a-time"}), "invalid timestamp")
            rejected(lambda value: value.update({"sourceSnapshot": {}}), "source snapshot differs")
            rejected(lambda value: value.update({"policies": []}), "policies differ")
            rejected(lambda value: value["outputs"].update({"extra.tsv": {}}), "output set differs")

        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            contracts_path = forged / "campaign-contracts.tsv"
            contracts = campaign._read_tsv(contracts_path)
            damage = next(row for row in contracts if row["contractId"] == "C-62b3c956518ff9a5")
            damage["writes"] = "ALL DAMAGE WRITES ARE PROVED"
            campaign._write_tsv(contracts_path, campaign.CONTRACT_COLUMNS, contracts)
            ready = json.loads((forged / "campaign.ready.json").read_text(encoding="utf-8"))
            ready["outputs"]["campaign-contracts.tsv"] = {
                **campaign.coverage.file_stamp(contracts_path),
                "path": "campaign-contracts.tsv",
            }
            self.write_ready(forged, ready)
            completed = self.frozen_verify(forged)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("campaign rows differ", completed.stderr)

        for relative, expected in (
            (Path("campaign.ready.json"), "campaign READY is not a plain single-link file"),
            (Path("campaign-functions.tsv"), "output has multiple hard links: campaign-functions.tsv"),
        ):
            with self.subTest(relative=relative.as_posix()):
                with tempfile.TemporaryDirectory() as temporary:
                    forged = Path(temporary) / "forged"
                    shutil.copytree(self.generation, forged)
                    target = forged / relative
                    anchor = Path(temporary) / (relative.name + ".anchor")
                    shutil.copy2(target, anchor)
                    target.unlink()
                    os.link(anchor, target)
                    completed = self.frozen_verify(forged)
                    self.assertNotEqual(0, completed.returncode)
                    self.assertIn(expected, completed.stderr)


class CampaignRecoveryGeneration13ApplyDamageTests(unittest.TestCase):
    AUTHORITY_RECEIPT_BYTES = 8873
    AUTHORITY_RECEIPT_SHA256 = (
        "772f65ba5210c6d022bff64aefb6523a563ed1b8c3ab53eb87aef8dfe4b1944d"
    )
    AUTHORITY_AUTHOR_SHA256 = (
        "71acd049a65404f7ba0248e4583fae8e47b7b9c64dcd6a1b621b273afa6bd8ea"
    )
    AUTHORITY_BOOTSTRAP_SHA256 = (
        "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b"
    )
    AUTHORITY_REDUCER_ID = (
        "988e0660634b6fa59b2018a96545cdf84666e2c219c7a7ac89809c4ef99fac2e"
    )
    AUTHORITY_READY_SHA256 = {
        "generation-13-applydamage-primary-reproof-v1": (
            "8436a5a99145f6910cd147bdb419a0efbfb071fcf16d8f42ec330182a97df63e"
        ),
        "generation-13-applydamage-primary-reproof-replica-v1": (
            "a6af8a9345107caabe0b2241ee306e6efbb5113552082935a287fe0b495c4c4c"
        ),
    }
    OUTPUT_SHA256 = {
        "campaign-functions.tsv": "eeb992ab962308b97834f314675521bb82064f50d37ca57f40ff6ad5c54a4534",
        "campaign-residuals.tsv": "30d390b75a9984efc6bebedf5ddb00412326d36e51d2c9f3c1883032dd25ef49",
        "campaign-questions.tsv": "d4bfeae6720aad38e8508ec6b868ba55715dfd317d1cffba00b1f74049dffb0c",
        "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
        "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
        "campaign-contracts.tsv": "b27ea5a153833cda4fbeaae9a2f93a65312e64e956e72e01c57055f794713392",
        "campaign-adjudications.tsv": "0e5dc2d203a123231eacc7a4b629b77259bfd48429951c4ed514ede459d7e59c",
        "campaign-supersessions.tsv": "7569852a3fe9aea25a4fcc4f6d17b6d9d81ff658f644b007bda1f50ae55559cb",
    }

    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        cls.parent = base / "generation-12-level521-damage-hit-writes-v1"
        cls.generation = base / "generation-13-applydamage-primary-reproof-v1"
        cls.replica = base / "generation-13-applydamage-primary-reproof-replica-v1"
        cls.authority = base / "generation-13-applydamage-primary-reproof-authority.ready.json"
        cls.proof = repo / campaign.APPLYDAMAGE_REPROOF_RELATIVE
        if not (cls.parent / "campaign.ready.json").is_file():
            raise unittest.SkipTest("maintainer-local canonical Gen12 prerequisite is unavailable")
        for root, label in (
            (cls.proof, "ApplyDamage reproof"),
            (cls.generation, "canonical Generation 13"),
            (cls.replica, "replicated Generation 13"),
        ):
            ready_name = "proof.ready.json" if root == cls.proof else "campaign.ready.json"
            if not (root / ready_name).is_file():
                raise AssertionError(f"required {label} is missing: {root}")

    @classmethod
    def authority_verify(cls, root: Path) -> subprocess.CompletedProcess:
        expected_ready = cls.AUTHORITY_READY_SHA256.get(root.name)
        if expected_ready is None:
            raise AssertionError(f"root is not an externally selected Gen13 copy: {root}")
        repo = Path(__file__).resolve().parent.parent
        bootstrap = Path(__file__).resolve().parent / "re_campaign_frozen_bootstrap.py"
        environment = os.environ.copy()
        environment["BEA_REPO_ROOT"] = os.fspath(repo)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                os.fspath(Path(os.sys.executable)),
                "-I",
                "-B",
                os.fspath(bootstrap),
                "--campaign",
                os.fspath(root),
                "--mode",
                "full",
                "--expected-ready-sha256",
                expected_ready,
                "--expected-reducer-id",
                cls.AUTHORITY_REDUCER_ID,
            ],
            cwd=repo,
            env=environment,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )

    @staticmethod
    def frozen_verify(root: Path, *, replay: bool = False) -> subprocess.CompletedProcess:
        return CampaignRecoveryGeneration8Tests.frozen_verify(root, replay=replay)

    @staticmethod
    def reducer_files(root: Path) -> dict[str, bytes]:
        return CampaignRecoveryGeneration9Tests.reducer_files(root)

    @staticmethod
    def write_ready(root: Path, receipt: dict) -> None:
        (root / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def test_two_independent_builds_are_deterministic_and_fully_replay(self) -> None:
        for name, digest in self.OUTPUT_SHA256.items():
            self.assertEqual(digest, campaign.coverage.sha256_of(self.generation / name))
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        self.assertEqual(self.reducer_files(self.generation), self.reducer_files(self.replica))
        normalized = []
        for root in (self.generation, self.replica):
            completed = self.authority_verify(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
            receipt = json.loads((root / "campaign.ready.json").read_text(encoding="utf-8"))
            self.assertEqual(13, receipt["generation"])
            self.assertEqual(
                campaign.APPLYDAMAGE_REPROOF_EXPECTED_GENERATION13_COUNTS,
                receipt["counts"],
            )
            self.assertEqual(campaign.APPLYDAMAGE_REPROOF_ADVANCE_KIND, receipt["advance"]["kind"])
            self.assertEqual(campaign.APPLYDAMAGE_REPROOF_ADVANCE_SCHEMA, receipt["advance"]["schema"])
            self.assertEqual("AD-211e63bf8c1437ac", receipt["advance"]["observationId"])
            receipt["generatedAtUtc"] = "<generated>"
            for stamp in receipt["outputs"].values():
                stamp["lastWriteUtc"] = "<write>"
            normalized.append(receipt)
        self.assertEqual(normalized[0], normalized[1])

    def test_exact_bounded_contract_questions_and_parity_mapping(self) -> None:
        parent_functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.parent / "campaign-functions.tsv")
        }
        functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.generation / "campaign-functions.tsv")
        }
        parent_contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-contracts.tsv")
        }
        contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-contracts.tsv")
        }
        self.assertEqual(
            {campaign.applydamage_reproof.ENTITY_KEY},
            {key for key in functions if functions[key] != parent_functions[key]},
        )
        self.assertEqual(
            {campaign.applydamage_reproof.CONTRACT_ID},
            {key for key in contracts if contracts[key] != parent_contracts[key]},
        )
        function = functions[campaign.applydamage_reproof.ENTITY_KEY]
        contract = contracts[campaign.applydamage_reproof.CONTRACT_ID]
        self.assertEqual("C2_BOUNDED_RUNTIME", function["semanticGrade"])
        self.assertEqual("BOUNDED_CONTRACT", function["resolutionState"])
        self.assertEqual("C2_BOUNDED_RUNTIME", contract["semanticGrade"])
        self.assertEqual("BOUNDED_CONTRACT_ADVANCED", contract["contractState"])
        self.assertEqual("SURVIVED", contract["refuterVerdict"])
        self.assertIn("0x3BA3D70B->0xC479FFAE", contract["writes"])
        self.assertIn("0x00000000->0x00000000", contract["writes"])
        self.assertIn("withholds association", contract["returns"])
        self.assertIn("positive-shield absorption", contract["failureModes"])
        self.assertEqual("PARTIAL_CONTRACT", contract["rebuildState"])
        self.assertEqual(
            "OnslaughtRebuild.Core.Level100DestructionState.ApplyRoundHit",
            contract["rebuildImplementation"],
        )
        for name in (
            "campaign-residuals.tsv",
            "campaign-scenarios.tsv",
            "campaign-levers.tsv",
            "campaign-supersessions.tsv",
        ):
            self.assertEqual((self.parent / name).read_bytes(), (self.generation / name).read_bytes(), name)

        parent_questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-questions.tsv")
        }
        questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-questions.tsv")
        }
        expected_successors = {"Q-c82daeb2bd82e5ac", "Q-694f9ecf56cd917f"}
        self.assertEqual(expected_successors, set(questions) - set(parent_questions))
        self.assertEqual("CLOSED_SURVIVED", questions["Q-178b10ce57ab15db"]["state"])
        for successor in expected_successors:
            self.assertEqual("OPEN", questions[successor]["state"])
            self.assertEqual("Q-178b10ce57ab15db", questions[successor]["parentQuestionId"])
            self.assertIn(successor, contract["questionIds"].split(";"))
        parent_adjudications = {
            row["adjudicationId"]
            for row in campaign._read_tsv(self.parent / "campaign-adjudications.tsv")
        }
        fresh = [
            row
            for row in campaign._read_tsv(self.generation / "campaign-adjudications.tsv")
            if row["adjudicationId"] not in parent_adjudications
        ]
        self.assertEqual(["A-40616e3ffc00936a"], [row["adjudicationId"] for row in fresh])
        self.assertEqual("True", fresh[0]["semanticPromotionApplied"])
        self.assertEqual(campaign.APPLYDAMAGE_REPROOF_READY_SHA256, fresh[0]["overlayReadySha256"])

    def test_frozen_integrity_rejects_strength_metadata_row_and_link_laundering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            original = json.loads((forged / "campaign.ready.json").read_text(encoding="utf-8"))

            def rejected(mutator, expected: str) -> None:
                receipt = json.loads(json.dumps(original))
                mutator(receipt)
                self.write_ready(forged, receipt)
                completed = self.frozen_verify(forged)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(lambda value: value.update({"advance": None}), "exact ApplyDamage reproof advance")
            rejected(
                lambda value: value["advance"]["promotion"].update({"gradeTo": "C3_ALL_PATHS"}),
                "ApplyDamage reproof advance receipt differs",
            )
            rejected(lambda value: value.update({"generatedAtUtc": "not-a-time"}), "invalid timestamp")
            rejected(lambda value: value.update({"policies": []}), "policies differ")

        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            contracts_path = forged / "campaign-contracts.tsv"
            contracts = campaign._read_tsv(contracts_path)
            target = next(
                row
                for row in contracts
                if row["contractId"] == campaign.applydamage_reproof.CONTRACT_ID
            )
            target["writes"] = "POSITIVE SHIELD ABSORPTION AND ALL PATHS PROVED"
            campaign._write_tsv(contracts_path, campaign.CONTRACT_COLUMNS, contracts)
            ready = json.loads((forged / "campaign.ready.json").read_text(encoding="utf-8"))
            ready["outputs"]["campaign-contracts.tsv"] = {
                **campaign.coverage.file_stamp(contracts_path),
                "path": "campaign-contracts.tsv",
            }
            self.write_ready(forged, ready)
            completed = self.frozen_verify(forged)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("ApplyDamage reproof campaign rows differ", completed.stderr)

        for relative, expected in (
            (Path("campaign.ready.json"), "campaign READY is not a plain single-link file"),
            (Path("campaign-functions.tsv"), "output has multiple hard links: campaign-functions.tsv"),
        ):
            with self.subTest(relative=relative.as_posix()):
                with tempfile.TemporaryDirectory() as temporary:
                    forged = Path(temporary) / "forged"
                    shutil.copytree(self.generation, forged)
                    target = forged / relative
                    anchor = Path(temporary) / (relative.name + ".anchor")
                    shutil.copy2(target, anchor)
                    target.unlink()
                    os.link(anchor, target)
                    completed = self.frozen_verify(forged)
                    self.assertNotEqual(0, completed.returncode)
                    self.assertIn(expected, completed.stderr)

    def test_external_authority_receipt_selects_only_canonical_generation13(self) -> None:
        if not self.authority.is_file():
            self.fail(f"required Generation 13 authority receipt is missing: {self.authority}")
        repo = Path(__file__).resolve().parent.parent
        author = repo / "tools/re_applydamage_primary_campaign_authority.py"
        bootstrap = repo / "tools/re_campaign_frozen_bootstrap.py"
        self.assertEqual(self.AUTHORITY_RECEIPT_BYTES, self.authority.stat().st_size)
        self.assertEqual(
            self.AUTHORITY_RECEIPT_SHA256,
            campaign.coverage.sha256_of(self.authority),
        )
        receipt = json.loads(self.authority.read_text(encoding="utf-8"))
        self.assertEqual("bea.re.cunit-applydamage-generation13-authority.v1", receipt["schema"])
        self.assertEqual("READY", receipt["verdict"])
        self.assertEqual("FULL_REPLAY_CAMPAIGN_AUTHORITY", receipt["authorityClass"])
        self.assertEqual("FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY", receipt["replayScope"])
        self.assertEqual(str(self.generation.resolve()), receipt["canonical"]["absolutePath"])
        self.assertEqual(str(self.replica.resolve()), receipt["replica"]["absolutePath"])
        self.assertEqual("REPRODUCTION_ONLY_NOT_AUTHORITY_SELECTOR", receipt["replica"]["role"])
        self.assertEqual(str(self.generation.resolve()), receipt["selectionRule"]["requiredAbsolutePath"])
        self.assertEqual(self.AUTHORITY_READY_SHA256, receipt["selectionRule"]["literalReadySha256ByRoot"])
        self.assertEqual(self.AUTHORITY_REDUCER_ID, receipt["selectionRule"]["requiredReducerId"])
        self.assertEqual("FULL", receipt["selectionRule"]["requiredMode"])
        self.assertEqual(campaign.APPLYDAMAGE_REPROOF_PARENT_READY_SHA256, receipt["parent"]["readySha256"])
        self.assertEqual(campaign.APPLYDAMAGE_REPROOF_PARENT_REDUCER_ID, receipt["parent"]["reducerId"])
        self.assertEqual(campaign.APPLYDAMAGE_REPROOF_READY_SHA256, receipt["proof"]["readySha256"])
        self.assertEqual(campaign.APPLYDAMAGE_REPROOF_AUTHOR_SHA256, receipt["proof"]["authorSha256"])
        self.assertEqual(campaign.APPLYDAMAGE_REPROOF_EXPECTED_GENERATION13_COUNTS, receipt["counts"])
        self.assertEqual(self.OUTPUT_SHA256, {name: stamp["sha256"] for name, stamp in receipt["outputs"].items()})
        self.assertEqual(14, receipt["limitations"]["nextValidGeneration"])
        self.assertFalse(receipt["limitations"]["liveGhidraMutation"])
        self.assertFalse(receipt["claimBoundary"]["positiveShieldAbsorptionProved"])
        self.assertEqual("WITHHELD_RECORDED_GAP", receipt["claimBoundary"]["returnAssociation"])
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, campaign.coverage.sha256_of(author))
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, receipt["author"]["sha256"])
        self.assertEqual(self.AUTHORITY_BOOTSTRAP_SHA256, campaign.coverage.sha256_of(bootstrap))
        self.assertEqual(self.AUTHORITY_BOOTSTRAP_SHA256, receipt["frozenOwners"]["preImportLauncher"]["sha256"])
        for root_name, section in (
            (self.generation.name, "canonicalLiteralPinnedFullReplay"),
            (self.replica.name, "replicaLiteralPinnedFullReplay"),
        ):
            replay = receipt["verification"][section]
            self.assertEqual(0, replay["exitCode"])
            self.assertEqual("CAMPAIGN_VERIFIED", replay["marker"])
            self.assertEqual(
                self.AUTHORITY_READY_SHA256[root_name],
                replay["command"][replay["command"].index("--expected-ready-sha256") + 1],
            )
            self.assertEqual(
                self.AUTHORITY_REDUCER_ID,
                replay["command"][replay["command"].index("--expected-reducer-id") + 1],
            )


class CampaignRecoveryGeneration14TokenArchiveTests(unittest.TestCase):
    AUTHORITY_RECEIPT_BYTES = 8215
    AUTHORITY_RECEIPT_SHA256 = (
        "83a5544bdde805762b01983171c336826ea62a8b2dd8be94109bef959560ff72"
    )
    AUTHORITY_AUTHOR_SHA256 = (
        "0d1056c4dc4b49408f0dcb39c4e38c80be99ce8db8bf304a3ed998dc51f043b9"
    )
    AUTHORITY_BOOTSTRAP_SHA256 = (
        "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b"
    )
    AUTHORITY_REDUCER_ID = (
        "ec58dc9ec399d719677c5ab98ab0ac2efe60d8138c4f2c829f3e5930a946dec2"
    )
    AUTHORITY_READY_SHA256 = {
        "generation-14-tokenarchive-dispatch-reproof-v1": (
            "9864424def44034a5a5e9a68814ce111076182ad7ea898c9d0040d888c92f32b"
        ),
        "generation-14-tokenarchive-dispatch-reproof-replica-v1": (
            "4f834364ebd9f39e02a4a1781180d79b95ededda3f8d6f6aaac0845bfb8d8a01"
        ),
    }
    OUTPUT_SHA256 = {
        "campaign-functions.tsv": "eeb992ab962308b97834f314675521bb82064f50d37ca57f40ff6ad5c54a4534",
        "campaign-residuals.tsv": "b0611722b49bbebbb666bce2c51d534e30ac7ad561d43daa594f5c40fcfdb1c3",
        "campaign-questions.tsv": "49e3987f4bfa1996838d62823c2d8cc74f26e82843099fadbd055ef52cf4b40d",
        "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
        "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
        "campaign-contracts.tsv": "7d5cefef1a6c18fdac8cbe9fa46ea119a6e6d47528f1a5743d9124c22c12a4f8",
        "campaign-adjudications.tsv": "de317f245b8c3c0e71002a82f73f2dbcc08284cee7c9cddd84c30e8777da7994",
        "campaign-supersessions.tsv": "7569852a3fe9aea25a4fcc4f6d17b6d9d81ff658f644b007bda1f50ae55559cb",
    }

    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        cls.parent = base / "generation-13-applydamage-primary-reproof-v1"
        cls.generation = base / "generation-14-tokenarchive-dispatch-reproof-v1"
        cls.replica = base / "generation-14-tokenarchive-dispatch-reproof-replica-v1"
        cls.authority = base / "generation-14-tokenarchive-dispatch-reproof-authority.ready.json"
        cls.proof = repo / campaign.TOKENARCHIVE_DISPATCH_PROOF_RELATIVE
        if not (cls.parent / "campaign.ready.json").is_file():
            raise unittest.SkipTest("maintainer-local canonical Gen13 prerequisite is unavailable")
        for root, label in (
            (cls.proof, "TokenArchive dispatch proof"),
            (cls.generation, "canonical Generation 14"),
            (cls.replica, "replicated Generation 14"),
        ):
            ready_name = "proof.ready.json" if root == cls.proof else "campaign.ready.json"
            if not (root / ready_name).is_file():
                raise AssertionError(f"required {label} is missing: {root}")

    @classmethod
    def authority_verify(cls, root: Path) -> subprocess.CompletedProcess:
        expected_ready = cls.AUTHORITY_READY_SHA256.get(root.name)
        if expected_ready is None:
            raise AssertionError(f"root is not an externally selected Gen14 copy: {root}")
        repo = Path(__file__).resolve().parent.parent
        bootstrap = Path(__file__).resolve().parent / "re_campaign_frozen_bootstrap.py"
        environment = os.environ.copy()
        environment["BEA_REPO_ROOT"] = os.fspath(repo)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                os.fspath(Path(os.sys.executable)),
                "-I",
                "-B",
                os.fspath(bootstrap),
                "--campaign",
                os.fspath(root),
                "--mode",
                "full",
                "--expected-ready-sha256",
                expected_ready,
                "--expected-reducer-id",
                cls.AUTHORITY_REDUCER_ID,
            ],
            cwd=repo,
            env=environment,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )

    @staticmethod
    def frozen_verify(root: Path, *, replay: bool = False) -> subprocess.CompletedProcess:
        return CampaignRecoveryGeneration8Tests.frozen_verify(root, replay=replay)

    @staticmethod
    def reducer_files(root: Path) -> dict[str, bytes]:
        return CampaignRecoveryGeneration9Tests.reducer_files(root)

    @staticmethod
    def write_ready(root: Path, receipt: dict) -> None:
        (root / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def test_two_independent_builds_are_deterministic_and_fully_replay(self) -> None:
        for name, digest in self.OUTPUT_SHA256.items():
            self.assertEqual(digest, campaign.coverage.sha256_of(self.generation / name))
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        self.assertEqual(self.reducer_files(self.generation), self.reducer_files(self.replica))
        self.assertEqual(20, len(self.reducer_files(self.generation)))
        normalized = []
        for root in (self.generation, self.replica):
            completed = self.authority_verify(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
            receipt = json.loads((root / "campaign.ready.json").read_text(encoding="utf-8"))
            self.assertEqual(14, receipt["generation"])
            self.assertEqual(
                campaign.TOKENARCHIVE_DISPATCH_EXPECTED_GENERATION14_COUNTS,
                receipt["counts"],
            )
            self.assertEqual(campaign.TOKENARCHIVE_DISPATCH_ADVANCE_KIND, receipt["advance"]["kind"])
            self.assertEqual(campaign.TOKENARCHIVE_DISPATCH_ADVANCE_SCHEMA, receipt["advance"]["schema"])
            self.assertEqual("TD-489e2736dd47aa51", receipt["advance"]["proofId"])
            receipt["generatedAtUtc"] = "<generated>"
            for stamp in receipt["outputs"].values():
                stamp["lastWriteUtc"] = "<write>"
            normalized.append(receipt)
        self.assertEqual(normalized[0], normalized[1])

    def test_exact_nonsemantic_residual_delta_and_proof_binding(self) -> None:
        parent_rows = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.parent / "campaign-residuals.tsv")
        }
        rows = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.generation / "campaign-residuals.tsv")
        }
        key = campaign.tokenarchive_reproof.ENTITY_KEY
        self.assertEqual({key}, {item for item in rows if rows[item] != parent_rows[item]})
        self.assertEqual("DATA", rows[key]["classification"])
        self.assertEqual("TERMINAL_DATA", rows[key]["terminalState"])
        self.assertEqual(
            "STATIC_CONSUMER_BOUND_DISPATCH_TABLE_PARTITION",
            rows[key]["classificationVerdict"],
        )
        parent_questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-questions.tsv")
        }
        questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-questions.tsv")
        }
        question_id = campaign.tokenarchive_reproof.QUESTION_ID
        self.assertEqual({question_id}, {item for item in questions if questions[item] != parent_questions[item]})
        self.assertEqual("CLOSED_SURVIVED", questions[question_id]["state"])
        self.assertEqual(set(), set(questions) - set(parent_questions))
        parent_adjudications = {
            row["adjudicationId"]
            for row in campaign._read_tsv(self.parent / "campaign-adjudications.tsv")
        }
        fresh = [
            row
            for row in campaign._read_tsv(self.generation / "campaign-adjudications.tsv")
            if row["adjudicationId"] not in parent_adjudications
        ]
        self.assertEqual(["A-6c8984dc61c86b0d"], [row["adjudicationId"] for row in fresh])
        self.assertEqual("False", fresh[0]["semanticPromotionApplied"])
        self.assertEqual(campaign.TOKENARCHIVE_DISPATCH_PROOF_READY_SHA256, fresh[0]["overlayReadySha256"])
        for name in (
            "campaign-functions.tsv",
            "campaign-scenarios.tsv",
            "campaign-levers.tsv",
            "campaign-supersessions.tsv",
        ):
            self.assertEqual((self.parent / name).read_bytes(), (self.generation / name).read_bytes(), name)

    def test_frozen_integrity_rejects_advance_row_and_link_laundering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            original = json.loads((forged / "campaign.ready.json").read_text(encoding="utf-8"))

            def rejected(mutator, expected: str) -> None:
                receipt = json.loads(json.dumps(original))
                mutator(receipt)
                self.write_ready(forged, receipt)
                completed = self.frozen_verify(forged)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(
                lambda value: value.update({"advance": None}),
                "Generation 13 recovery child is not the exact TokenArchive dispatch reproof advance",
            )
            rejected(
                lambda value: value["advance"]["promotion"].update({"classification": "CODE"}),
                "TokenArchive dispatch advance receipt differs",
            )
            rejected(lambda value: value.update({"generatedAtUtc": "not-a-time"}), "invalid timestamp")

        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            residuals_path = forged / "campaign-residuals.tsv"
            residuals = campaign._read_tsv(residuals_path)
            target = next(
                row
                for row in residuals
                if row["entityKey"] == campaign.tokenarchive_reproof.ENTITY_KEY
            )
            target["classification"] = "CODE"
            campaign._write_tsv(residuals_path, campaign.RESIDUAL_COLUMNS, residuals)
            ready = json.loads((forged / "campaign.ready.json").read_text(encoding="utf-8"))
            ready["outputs"]["campaign-residuals.tsv"] = {
                **campaign.coverage.file_stamp(residuals_path),
                "path": "campaign-residuals.tsv",
            }
            self.write_ready(forged, ready)
            completed = self.frozen_verify(forged)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("TokenArchive dispatch campaign rows differ", completed.stderr)

        for relative, expected in (
            (Path("campaign.ready.json"), "campaign READY is not a plain single-link file"),
            (Path("campaign-residuals.tsv"), "output has multiple hard links: campaign-residuals.tsv"),
        ):
            with self.subTest(relative=relative.as_posix()):
                with tempfile.TemporaryDirectory() as temporary:
                    forged = Path(temporary) / "forged"
                    shutil.copytree(self.generation, forged)
                    target = forged / relative
                    anchor = Path(temporary) / (relative.name + ".anchor")
                    shutil.copy2(target, anchor)
                    target.unlink()
                    os.link(anchor, target)
                    completed = self.frozen_verify(forged)
                    self.assertNotEqual(0, completed.returncode)
                    self.assertIn(expected, completed.stderr)

    def test_external_authority_receipt_selects_only_canonical_generation14(self) -> None:
        if not self.authority.is_file():
            self.fail(f"required Generation 14 authority receipt is missing: {self.authority}")
        repo = Path(__file__).resolve().parent.parent
        author = repo / "tools/re_tokenarchive_dispatch_campaign_authority.py"
        bootstrap = repo / "tools/re_campaign_frozen_bootstrap.py"
        self.assertEqual(self.AUTHORITY_RECEIPT_BYTES, self.authority.stat().st_size)
        self.assertEqual(self.AUTHORITY_RECEIPT_SHA256, campaign.coverage.sha256_of(self.authority))
        receipt = json.loads(self.authority.read_text(encoding="utf-8"))
        self.assertEqual("bea.re.tokenarchive-dispatch-generation14-authority.v1", receipt["schema"])
        self.assertEqual("READY", receipt["verdict"])
        self.assertEqual("FULL_REPLAY_CAMPAIGN_AUTHORITY", receipt["authorityClass"])
        self.assertEqual("FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY", receipt["replayScope"])
        self.assertEqual(str(self.generation.resolve()), receipt["canonical"]["absolutePath"])
        self.assertEqual(str(self.replica.resolve()), receipt["replica"]["absolutePath"])
        self.assertEqual("REPRODUCTION_ONLY_NOT_AUTHORITY_SELECTOR", receipt["replica"]["role"])
        self.assertEqual(str(self.generation.resolve()), receipt["selectionRule"]["requiredAbsolutePath"])
        self.assertEqual(self.AUTHORITY_READY_SHA256, receipt["selectionRule"]["literalReadySha256ByRoot"])
        self.assertEqual(self.AUTHORITY_REDUCER_ID, receipt["selectionRule"]["requiredReducerId"])
        self.assertEqual(campaign.TOKENARCHIVE_DISPATCH_PARENT_READY_SHA256, receipt["parent"]["readySha256"])
        self.assertEqual(campaign.TOKENARCHIVE_DISPATCH_PROOF_READY_SHA256, receipt["proof"]["readySha256"])
        self.assertEqual(campaign.TOKENARCHIVE_DISPATCH_EXPECTED_GENERATION14_COUNTS, receipt["counts"])
        self.assertEqual(self.OUTPUT_SHA256, {name: stamp["sha256"] for name, stamp in receipt["outputs"].items()})
        self.assertEqual(15, receipt["limitations"]["nextValidGeneration"])
        self.assertFalse(receipt["limitations"]["liveGhidraMutation"])
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, campaign.coverage.sha256_of(author))
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, receipt["author"]["sha256"])
        self.assertEqual(self.AUTHORITY_BOOTSTRAP_SHA256, campaign.coverage.sha256_of(bootstrap))
        self.assertEqual(self.AUTHORITY_BOOTSTRAP_SHA256, receipt["frozenOwners"]["preImportLauncher"]["sha256"])


class CampaignRecoveryGeneration15MissionNativeSetPosTests(unittest.TestCase):
    AUTHORITY_RECEIPT_BYTES = 9769
    AUTHORITY_RECEIPT_SHA256 = (
        "9fc1bf4eadd3ba654b80397c540515dba47022ce5905215851737673dc977ceb"
    )
    AUTHORITY_AUTHOR_SHA256 = (
        "fb2561583c0f6652243932c9088b40481a2ff6918b70fd0eef92170fa310f0ce"
    )
    AUTHORITY_BOOTSTRAP_SHA256 = (
        "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b"
    )
    AUTHORITY_REDUCER_ID = (
        "16ecb8974a7cd229015b2a5e0fd4f445d5f763d79aa2d667462324aa9e4ddfe9"
    )
    AUTHORITY_READY_SHA256 = {
        "generation-15-mission-native-setpos-reproof-v2": (
            "629b32daf62f7c85e4819a024e0ade705be5548960d81cc320b636afa53e58a7"
        ),
        "generation-15-mission-native-setpos-reproof-replica-v2": (
            "3dc9d0f848bc78f1d587030fe95f21283441800f161c599df87e9bec4857c4d1"
        ),
    }
    OUTPUT_SHA256 = {
        "campaign-functions.tsv": "5139617ef08e09bd316bae150dde6cadb499733bdea071df8765df34d69fcead",
        "campaign-residuals.tsv": "6aaa5da3917079de3a172fb24b7de2b3ba99f1bc05ad40c4c427fcaa76d55ab6",
        "campaign-questions.tsv": "f9a88ede7b7930ea32b43456d9c2d301c0078a63cb934752b6e41013b1cd8198",
        "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
        "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
        "campaign-contracts.tsv": "33ee92294f764e2aab8c45329983f02ca02be45c46ce699f6b93cffe87872643",
        "campaign-adjudications.tsv": "512cf71273e9f8e45c55231e6a27a287d8fba4980a54dae45ba1645cdcf31a4b",
        "campaign-supersessions.tsv": "4da539b16248ae9f5abfe5aa61845d9ec96351605060b8b05f16abb7353b008e",
    }

    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        cls.parent = base / "generation-14-tokenarchive-dispatch-reproof-v1"
        cls.generation = base / "generation-15-mission-native-setpos-reproof-v2"
        cls.replica = base / "generation-15-mission-native-setpos-reproof-replica-v2"
        cls.authority = base / "generation-15-mission-native-setpos-reproof-authority.ready.json"
        cls.proof = repo / campaign.MISSION_NATIVE_SETPOS_PROOF_RELATIVE
        if not (cls.parent / "campaign.ready.json").is_file():
            raise unittest.SkipTest("maintainer-local canonical Gen14 prerequisite is unavailable")
        for root, ready_name, label in (
            (cls.proof, "proof.ready.json", "SetPos boundary proof"),
            (cls.generation, "campaign.ready.json", "canonical Generation 15"),
            (cls.replica, "campaign.ready.json", "replicated Generation 15"),
        ):
            if not (root / ready_name).is_file():
                raise AssertionError(f"required {label} is missing: {root}")
        if not cls.authority.is_file():
            raise AssertionError(f"required Generation 15 authority is missing: {cls.authority}")

    @classmethod
    def authority_verify(cls, root: Path) -> subprocess.CompletedProcess:
        expected_ready = cls.AUTHORITY_READY_SHA256.get(root.name)
        if expected_ready is None:
            raise AssertionError(f"root is not an externally selected Gen15 copy: {root}")
        repo = Path(__file__).resolve().parent.parent
        bootstrap = Path(__file__).resolve().parent / "re_campaign_frozen_bootstrap.py"
        environment = os.environ.copy()
        environment["BEA_REPO_ROOT"] = os.fspath(repo)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                os.fspath(Path(os.sys.executable)),
                "-I",
                "-B",
                os.fspath(bootstrap),
                "--campaign",
                os.fspath(root),
                "--mode",
                "full",
                "--expected-ready-sha256",
                expected_ready,
                "--expected-reducer-id",
                cls.AUTHORITY_REDUCER_ID,
            ],
            cwd=repo,
            env=environment,
            capture_output=True,
            text=True,
            timeout=900,
            check=False,
        )

    @staticmethod
    def frozen_verify(root: Path, *, replay: bool = False) -> subprocess.CompletedProcess:
        return CampaignRecoveryGeneration8Tests.frozen_verify(root, replay=replay)

    @staticmethod
    def reducer_files(root: Path) -> dict[str, bytes]:
        return CampaignRecoveryGeneration9Tests.reducer_files(root)

    @staticmethod
    def write_ready(root: Path, receipt: dict) -> None:
        (root / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def test_two_independent_builds_are_deterministic_and_fully_replay(self) -> None:
        for name, digest in self.OUTPUT_SHA256.items():
            self.assertEqual(digest, campaign.coverage.sha256_of(self.generation / name))
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        self.assertEqual(self.reducer_files(self.generation), self.reducer_files(self.replica))
        self.assertEqual(23, len(self.reducer_files(self.generation)))
        normalized = []
        for root in (self.generation, self.replica):
            completed = self.authority_verify(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
            receipt = json.loads((root / "campaign.ready.json").read_text(encoding="utf-8"))
            self.assertEqual(15, receipt["generation"])
            self.assertEqual(
                campaign.MISSION_NATIVE_SETPOS_EXPECTED_GENERATION15_COUNTS,
                receipt["counts"],
            )
            self.assertEqual(campaign.MISSION_NATIVE_SETPOS_ADVANCE_KIND, receipt["advance"]["kind"])
            self.assertEqual(campaign.MISSION_NATIVE_SETPOS_ADVANCE_SCHEMA, receipt["advance"]["schema"])
            self.assertEqual("SP-279860c25156b65d", receipt["advance"]["promotionId"])
            receipt["generatedAtUtc"] = "<generated>"
            for output in receipt["outputs"].values():
                output["lastWriteUtc"] = "<write>"
            normalized.append(receipt)
        self.assertEqual(normalized[0], normalized[1])

    def test_exact_partition_boundary_contract_and_question_delta(self) -> None:
        old_entity = campaign.mission_setpos_reproof.OLD_ENTITY
        old_contract = campaign.mission_setpos_reproof.OLD_CONTRACT
        new_entity = campaign.mission_setpos_reproof.NEW_ENTITY
        new_contract = campaign.mission_setpos_reproof.NEW_CONTRACT
        parent_functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.parent / "campaign-functions.tsv")
        }
        functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.generation / "campaign-functions.tsv")
        }
        self.assertEqual({new_entity}, set(functions) - set(parent_functions))
        self.assertTrue(all(functions[key] == row for key, row in parent_functions.items()))
        self.assertEqual("IScript__SetPos", functions[new_entity]["currentName"])
        self.assertEqual("C1_CANDIDATE_PARTIAL", functions[new_entity]["semanticGrade"])
        self.assertEqual("42", functions[new_entity]["bodyBytes"])

        parent_residuals = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.parent / "campaign-residuals.tsv")
        }
        residuals = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.generation / "campaign-residuals.tsv")
        }
        specimen = campaign.mission_setpos_reproof.SPECIMEN_SHA256
        expected_children = {
            f"TEXT_RESIDUAL:{specimen}:0x00536C61-0x00536C70",
            f"TEXT_RESIDUAL:{specimen}:0x00536C9A-0x00536CA0",
        }
        self.assertEqual({old_entity}, set(parent_residuals) - set(residuals))
        self.assertEqual(expected_children, set(residuals) - set(parent_residuals))
        for key in expected_children:
            self.assertEqual("PADDING", residuals[key]["classification"])
            self.assertEqual("TERMINAL_PADDING", residuals[key]["terminalState"])

        parent_contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-contracts.tsv")
        }
        contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-contracts.tsv")
        }
        self.assertEqual({old_contract}, set(parent_contracts) - set(contracts))
        self.assertEqual(3, len(set(contracts) - set(parent_contracts)))
        self.assertEqual(new_entity, contracts[new_contract]["entityKey"])
        self.assertEqual("CANDIDATE_NEEDS_REFUTER", contracts[new_contract]["contractState"])
        self.assertEqual("UNSCORED", contracts[new_contract]["runtimeVerdict"])

        parent_questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-questions.tsv")
        }
        questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-questions.tsv")
        }
        changed = {
            key for key in parent_questions if questions[key] != parent_questions[key]
        }
        self.assertEqual(
            {
                campaign.mission_setpos_reproof.RESIDUAL_QUESTION,
                campaign.mission_setpos_reproof.CANDIDATE_QUESTION,
            },
            changed,
        )
        self.assertEqual(
            {campaign.mission_setpos_reproof.SUCCESSOR_QUESTION},
            set(questions) - set(parent_questions),
        )
        self.assertTrue(all(questions[key]["state"] == "CLOSED_SURVIVED" for key in changed))
        successor = questions[campaign.mission_setpos_reproof.SUCCESSOR_QUESTION]
        self.assertEqual("OPEN", successor["state"])
        self.assertEqual(campaign.mission_setpos_reproof.CANDIDATE_QUESTION, successor["parentQuestionId"])

        parent_adjudications = {
            row["adjudicationId"]
            for row in campaign._read_tsv(self.parent / "campaign-adjudications.tsv")
        }
        fresh_adjudications = [
            row
            for row in campaign._read_tsv(self.generation / "campaign-adjudications.tsv")
            if row["adjudicationId"] not in parent_adjudications
        ]
        self.assertEqual(
            ["A-78f0343e9f41235c", "A-88a1cc899a6a5975"],
            sorted(row["adjudicationId"] for row in fresh_adjudications),
        )
        self.assertTrue(all(row["semanticPromotionApplied"] == "False" for row in fresh_adjudications))
        self.assertEqual(
            (self.parent / "campaign-scenarios.tsv").read_bytes(),
            (self.generation / "campaign-scenarios.tsv").read_bytes(),
        )
        self.assertEqual(
            (self.parent / "campaign-levers.tsv").read_bytes(),
            (self.generation / "campaign-levers.tsv").read_bytes(),
        )

    def test_frozen_integrity_rejects_metadata_row_and_link_laundering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            original = json.loads((forged / "campaign.ready.json").read_text(encoding="utf-8"))

            def rejected(mutator, expected: str) -> None:
                receipt = json.loads(json.dumps(original))
                mutator(receipt)
                self.write_ready(forged, receipt)
                completed = self.frozen_verify(forged)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(
                lambda value: value.update({"advance": None}),
                "Generation 14 recovery child is not the exact Mission-native SetPos advance",
            )
            rejected(
                lambda value: value["advance"]["function"].update({"runtimeVerdict": "MEASURED"}),
                "Mission-native SetPos advance receipt differs",
            )
            rejected(lambda value: value.update({"generatedAtUtc": "not-a-time"}), "invalid timestamp")

        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            path = forged / "campaign-functions.tsv"
            rows = campaign._read_tsv(path)
            target = next(
                row
                for row in rows
                if row["entityKey"] == campaign.mission_setpos_reproof.NEW_ENTITY
            )
            target["semanticGrade"] = "C2_BOUNDED_RUNTIME"
            campaign._write_tsv(path, campaign.FUNCTION_COLUMNS, rows)
            ready = json.loads((forged / "campaign.ready.json").read_text(encoding="utf-8"))
            ready["outputs"]["campaign-functions.tsv"] = {
                **campaign.coverage.file_stamp(path),
                "path": "campaign-functions.tsv",
            }
            self.write_ready(forged, ready)
            completed = self.frozen_verify(forged)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("Mission-native SetPos campaign rows differ", completed.stderr)

        for relative, expected in (
            (Path("campaign.ready.json"), "campaign READY is not a plain single-link file"),
            (Path("campaign-functions.tsv"), "output has multiple hard links: campaign-functions.tsv"),
        ):
            with self.subTest(relative=relative.as_posix()):
                with tempfile.TemporaryDirectory() as temporary:
                    forged = Path(temporary) / "forged"
                    shutil.copytree(self.generation, forged)
                    target = forged / relative
                    anchor = Path(temporary) / (relative.name + ".anchor")
                    shutil.copy2(target, anchor)
                    target.unlink()
                    os.link(anchor, target)
                    completed = self.frozen_verify(forged)
                    self.assertNotEqual(0, completed.returncode)
                    self.assertIn(expected, completed.stderr)

    def test_external_authority_receipt_selects_only_canonical_generation15(self) -> None:
        repo = Path(__file__).resolve().parent.parent
        author = repo / "tools/re_mission_native_setpos_campaign_authority.py"
        bootstrap = repo / "tools/re_campaign_frozen_bootstrap.py"
        self.assertEqual(self.AUTHORITY_RECEIPT_BYTES, self.authority.stat().st_size)
        self.assertEqual(self.AUTHORITY_RECEIPT_SHA256, campaign.coverage.sha256_of(self.authority))
        receipt = json.loads(self.authority.read_text(encoding="utf-8"))
        self.assertEqual("bea.re.mission-native-setpos-generation15-authority.v1", receipt["schema"])
        self.assertEqual("READY", receipt["verdict"])
        self.assertEqual("FULL_REPLAY_CAMPAIGN_AUTHORITY", receipt["authorityClass"])
        self.assertEqual("FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY", receipt["replayScope"])
        self.assertEqual(str(self.generation.resolve()), receipt["canonical"]["absolutePath"])
        self.assertEqual(str(self.replica.resolve()), receipt["replica"]["absolutePath"])
        self.assertEqual("REPRODUCTION_ONLY_NOT_AUTHORITY_SELECTOR", receipt["replica"]["role"])
        self.assertEqual(str(self.generation.resolve()), receipt["selectionRule"]["requiredAbsolutePath"])
        self.assertEqual(self.AUTHORITY_READY_SHA256, receipt["selectionRule"]["literalReadySha256ByRoot"])
        self.assertEqual(self.AUTHORITY_REDUCER_ID, receipt["selectionRule"]["requiredReducerId"])
        self.assertEqual(campaign.MISSION_NATIVE_SETPOS_PARENT_READY_SHA256, receipt["parent"]["readySha256"])
        self.assertEqual(campaign.MISSION_NATIVE_SETPOS_PROOF_READY_SHA256, receipt["proof"]["readySha256"])
        self.assertEqual(campaign.MISSION_NATIVE_SETPOS_GHIDRA_LIVE_SHA256, receipt["ghidraPromotion"]["liveAuthoritySha256"])
        self.assertEqual(campaign.MISSION_NATIVE_SETPOS_EXPECTED_GENERATION15_COUNTS, receipt["counts"])
        self.assertEqual(self.OUTPUT_SHA256, {name: stamp["sha256"] for name, stamp in receipt["outputs"].items()})
        self.assertEqual("C1_STATIC", receipt["claimBoundary"]["semanticGradeCeiling"])
        self.assertEqual("UNSCORED", receipt["claimBoundary"]["runtimeVerdict"])
        self.assertTrue(receipt["claimBoundary"]["liveGhidraMutation"])
        self.assertEqual(0, receipt["claimBoundary"]["executableBytesChanged"])
        self.assertEqual(16, receipt["limitations"]["nextValidGeneration"])
        self.assertEqual("OPEN", receipt["limitations"]["runtimeVectorValues"])
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, campaign.coverage.sha256_of(author))
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, receipt["author"]["sha256"])
        self.assertEqual(self.AUTHORITY_BOOTSTRAP_SHA256, campaign.coverage.sha256_of(bootstrap))
        self.assertEqual(self.AUTHORITY_BOOTSTRAP_SHA256, receipt["frozenOwners"]["preImportLauncher"]["sha256"])
        for root_name, section in (
            (self.generation.name, "canonicalLiteralPinnedFullReplay"),
            (self.replica.name, "replicaLiteralPinnedFullReplay"),
        ):
            replay = receipt["verification"][section]
            self.assertEqual(0, replay["exitCode"])
            self.assertEqual("CAMPAIGN_VERIFIED", replay["marker"])
            self.assertEqual(
                self.AUTHORITY_READY_SHA256[root_name],
                replay["command"][replay["command"].index("--expected-ready-sha256") + 1],
            )
            self.assertEqual(
                self.AUTHORITY_REDUCER_ID,
                replay["command"][replay["command"].index("--expected-reducer-id") + 1],
            )


class CampaignRecoveryGeneration16MissionNativeSetPosRuntimeTests(unittest.TestCase):
    AUTHORITY_RECEIPT_BYTES = 11420
    AUTHORITY_RECEIPT_SHA256 = (
        "1d04fef865c510cacd4c545999367d88c214b0ffe5a7bc4eac68e50d185a6981"
    )
    AUTHORITY_AUTHOR_BYTES = 21804
    AUTHORITY_AUTHOR_SHA256 = (
        "d48bd7759b7e8bf4bcd26c4e92c100fe221e94dff0f0523752c5a31fda7257a6"
    )
    AUTHORITY_BOOTSTRAP_SHA256 = (
        "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b"
    )
    AUTHORITY_REDUCER_ID = (
        "453fdb4df7233c6d3f8be04a6ba67b3762982bc4513ca4990b46f01141d55db0"
    )
    AUTHORITY_READY_SHA256 = {
        "generation-16-mission-native-setpos-runtime-v1": (
            "97493a76de550f5ae35074e285e39a561d9a323219741a42ac2ff25643cdc880"
        ),
        "generation-16-mission-native-setpos-runtime-replica-v1": (
            "69de7a0fe8f7abe74a345fbccc4abfdbd0cff77d4cae281dab581f6b1afe436f"
        ),
    }
    OUTPUT_SHA256 = {
        "campaign-functions.tsv": "3b18ea14d343b7522085c1147bdc8fe252e8caa9467d17b08ec2902992d77039",
        "campaign-residuals.tsv": "6aaa5da3917079de3a172fb24b7de2b3ba99f1bc05ad40c4c427fcaa76d55ab6",
        "campaign-questions.tsv": "339050838d6b391ff8d7f8037befe26bfb67082fddbb92d3708ab5a8c461e2bc",
        "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
        "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
        "campaign-contracts.tsv": "40fe17bceb5f3365b0076b0f17f38b137e61dfe0cea9a3361d29db3b23f5bdf7",
        "campaign-adjudications.tsv": "ec838904fe3c1563c484c924cd6858f07c93f34a6ec79e907db43d1e99c4247b",
        "campaign-supersessions.tsv": "4da539b16248ae9f5abfe5aa61845d9ec96351605060b8b05f16abb7353b008e",
    }

    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        cls.parent = base / "generation-15-mission-native-setpos-reproof-v2"
        cls.generation = base / "generation-16-mission-native-setpos-runtime-v1"
        cls.replica = base / "generation-16-mission-native-setpos-runtime-replica-v1"
        cls.authority = base / "generation-16-mission-native-setpos-runtime-authority.ready.json"
        cls.proof = repo / campaign.MISSION_NATIVE_SETPOS_RUNTIME_PROOF_RELATIVE
        if not (cls.parent / "campaign.ready.json").is_file():
            raise unittest.SkipTest(
                "maintainer-local canonical Gen15 prerequisite is unavailable"
            )
        for root, ready_name, label in (
            (cls.proof, campaign.mission_setpos_runtime.READY_NAME, "SetPos runtime proof"),
            (cls.generation, "campaign.ready.json", "canonical Generation 16"),
            (cls.replica, "campaign.ready.json", "replicated Generation 16"),
        ):
            if not (root / ready_name).is_file():
                raise AssertionError(f"required {label} is missing: {root}")
        if not cls.authority.is_file():
            raise AssertionError(
                f"required Generation 16 authority is missing: {cls.authority}"
            )

    @classmethod
    def authority_verify(cls, root: Path) -> subprocess.CompletedProcess:
        expected_ready = cls.AUTHORITY_READY_SHA256.get(root.name)
        if expected_ready is None:
            raise AssertionError(f"root is not an externally selected Gen16 copy: {root}")
        repo = Path(__file__).resolve().parent.parent
        bootstrap = Path(__file__).resolve().parent / "re_campaign_frozen_bootstrap.py"
        environment = os.environ.copy()
        environment["BEA_REPO_ROOT"] = os.fspath(repo)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                os.fspath(Path(os.sys.executable)),
                "-I",
                "-B",
                os.fspath(bootstrap),
                "--campaign",
                os.fspath(root),
                "--mode",
                "full",
                "--expected-ready-sha256",
                expected_ready,
                "--expected-reducer-id",
                cls.AUTHORITY_REDUCER_ID,
            ],
            cwd=repo,
            env=environment,
            capture_output=True,
            text=True,
            timeout=1200,
            check=False,
        )

    @staticmethod
    def frozen_verify(root: Path) -> subprocess.CompletedProcess:
        return CampaignRecoveryGeneration8Tests.frozen_verify(root, replay=False)

    @staticmethod
    def reducer_files(root: Path) -> dict[str, bytes]:
        return CampaignRecoveryGeneration9Tests.reducer_files(root)

    @staticmethod
    def write_ready(root: Path, receipt: dict) -> None:
        (root / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def test_two_independent_builds_are_deterministic_and_fully_replay(self) -> None:
        for name, digest in self.OUTPUT_SHA256.items():
            self.assertEqual(digest, campaign.coverage.sha256_of(self.generation / name))
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        self.assertEqual(
            self.reducer_files(self.generation), self.reducer_files(self.replica)
        )
        self.assertEqual(27, len(self.reducer_files(self.generation)))
        normalized = []
        for root in (self.generation, self.replica):
            completed = self.authority_verify(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
            receipt = json.loads(
                (root / "campaign.ready.json").read_text(encoding="utf-8")
            )
            self.assertEqual(16, receipt["generation"])
            self.assertEqual(
                campaign.MISSION_NATIVE_SETPOS_RUNTIME_EXPECTED_GENERATION16_COUNTS,
                receipt["counts"],
            )
            self.assertEqual(
                campaign.MISSION_NATIVE_SETPOS_RUNTIME_ADVANCE_KIND,
                receipt["advance"]["kind"],
            )
            self.assertEqual(
                campaign.MISSION_NATIVE_SETPOS_RUNTIME_ADVANCE_SCHEMA,
                receipt["advance"]["schema"],
            )
            self.assertEqual("SPR-0d5dfdddd2921cf3", receipt["advance"]["observationId"])
            receipt["generatedAtUtc"] = "<generated>"
            for output in receipt["outputs"].values():
                output["lastWriteUtc"] = "<write>"
            normalized.append(receipt)
        self.assertEqual(normalized[0], normalized[1])

    def test_exact_runtime_contract_question_and_rebuild_delta(self) -> None:
        entity = campaign.mission_setpos_runtime.ENTITY_KEY
        contract_id = campaign.mission_setpos_runtime.CONTRACT_ID
        parent_question_id = campaign.mission_setpos_runtime.OPEN_QUESTION_ID
        parent_functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.parent / "campaign-functions.tsv")
        }
        functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.generation / "campaign-functions.tsv")
        }
        changed_functions = {
            key for key in functions if functions[key] != parent_functions[key]
        }
        self.assertEqual({entity}, changed_functions)
        self.assertEqual("C2_BOUNDED_RUNTIME", functions[entity]["semanticGrade"])
        self.assertEqual("BOUNDED_CONTRACT", functions[entity]["resolutionState"])
        self.assertIn(
            "MISSION_NATIVE_SETPOS_RUNTIME_REPLICATED",
            functions[entity]["evidenceStates"].split(";"),
        )

        parent_contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-contracts.tsv")
        }
        contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-contracts.tsv")
        }
        changed_contracts = {
            key for key in contracts if contracts[key] != parent_contracts[key]
        }
        self.assertEqual({contract_id}, changed_contracts)
        contract = contracts[contract_id]
        self.assertEqual("BOUNDED_CONTRACT_ADVANCED", contract["contractState"])
        self.assertEqual("C2_BOUNDED_RUNTIME", contract["semanticGrade"])
        self.assertEqual("MEASURED_BOUNDED_PATH", contract["runtimeVerdict"])
        self.assertEqual("SURVIVED", contract["refuterVerdict"])
        self.assertEqual("PARTIAL_CONTRACT", contract["rebuildState"])
        self.assertIn("InvokePositionNative", contract["rebuildImplementation"])
        self.assertIn(
            campaign.MISSION_NATIVE_SETPOS_RUNTIME_PROOF_READY_SHA256,
            contract["evidenceRefs"],
        )

        parent_questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-questions.tsv")
        }
        questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-questions.tsv")
        }
        self.assertEqual(
            {parent_question_id},
            {key for key in parent_questions if questions[key] != parent_questions[key]},
        )
        successor_ids = set(questions) - set(parent_questions)
        self.assertEqual(
            {"Q-02e7898ea7e64827", "Q-7b98e7f342645af1", "Q-aab3970a82afdd73"},
            successor_ids,
        )
        self.assertEqual("CLOSED_SURVIVED", questions[parent_question_id]["state"])
        for question_id in successor_ids:
            self.assertEqual("OPEN", questions[question_id]["state"])
            self.assertEqual(parent_question_id, questions[question_id]["parentQuestionId"])
            self.assertIn(question_id, contract["questionIds"].split(";"))

        parent_adjudications = {
            row["adjudicationId"]
            for row in campaign._read_tsv(self.parent / "campaign-adjudications.tsv")
        }
        fresh = [
            row
            for row in campaign._read_tsv(
                self.generation / "campaign-adjudications.tsv"
            )
            if row["adjudicationId"] not in parent_adjudications
        ]
        self.assertEqual(["A-16e165488adae1af"], [row["adjudicationId"] for row in fresh])
        self.assertEqual("True", fresh[0]["semanticPromotionApplied"])
        self.assertEqual(parent_question_id, fresh[0]["questionIdsAddressed"])
        for name in ("campaign-residuals.tsv", "campaign-scenarios.tsv", "campaign-levers.tsv", "campaign-supersessions.tsv"):
            self.assertEqual(
                (self.parent / name).read_bytes(),
                (self.generation / name).read_bytes(),
                name,
            )

    def test_frozen_integrity_rejects_metadata_and_row_laundering(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            original = json.loads(
                (forged / "campaign.ready.json").read_text(encoding="utf-8")
            )

            def rejected(mutator, expected: str) -> None:
                receipt = json.loads(json.dumps(original))
                mutator(receipt)
                self.write_ready(forged, receipt)
                completed = self.frozen_verify(forged)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(
                lambda value: value.update({"advance": None}),
                "Generation 15 recovery child is not the exact Mission-native SetPos runtime advance",
            )
            rejected(
                lambda value: value["advance"]["promotion"].update(
                    {"gradeTo": "C1_CANDIDATE_PARTIAL"}
                ),
                "Mission-native SetPos runtime advance receipt differs",
            )
            rejected(
                lambda value: value.update({"generatedAtUtc": "not-a-time"}),
                "invalid timestamp",
            )

        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            path = forged / "campaign-contracts.tsv"
            rows = campaign._read_tsv(path)
            target = next(
                row
                for row in rows
                if row["contractId"] == campaign.mission_setpos_runtime.CONTRACT_ID
            )
            target["writes"] = "forged complete write set"
            campaign._write_tsv(path, campaign.CONTRACT_COLUMNS, rows)
            ready = json.loads(
                (forged / "campaign.ready.json").read_text(encoding="utf-8")
            )
            ready["outputs"]["campaign-contracts.tsv"] = {
                **campaign.coverage.file_stamp(path),
                "path": "campaign-contracts.tsv",
            }
            self.write_ready(forged, ready)
            completed = self.frozen_verify(forged)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("Mission-native SetPos runtime campaign rows differ", completed.stderr)

    def test_external_authority_receipt_selects_only_canonical_generation16(self) -> None:
        repo = Path(__file__).resolve().parent.parent
        author = repo / "tools/re_mission_native_setpos_runtime_campaign_authority.py"
        bootstrap = repo / "tools/re_campaign_frozen_bootstrap.py"
        self.assertEqual(self.AUTHORITY_RECEIPT_BYTES, self.authority.stat().st_size)
        self.assertEqual(
            self.AUTHORITY_RECEIPT_SHA256,
            campaign.coverage.sha256_of(self.authority),
        )
        self.assertEqual(self.AUTHORITY_AUTHOR_BYTES, author.stat().st_size)
        self.assertEqual(
            self.AUTHORITY_AUTHOR_SHA256, campaign.coverage.sha256_of(author)
        )
        receipt = json.loads(self.authority.read_text(encoding="utf-8"))
        self.assertEqual(
            "bea.re.mission-native-setpos-generation16-authority.v1",
            receipt["schema"],
        )
        self.assertEqual("READY", receipt["verdict"])
        self.assertEqual("FULL_REPLAY_CAMPAIGN_AUTHORITY", receipt["authorityClass"])
        self.assertEqual(
            "FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY",
            receipt["replayScope"],
        )
        self.assertEqual(str(self.generation.resolve()), receipt["canonical"]["absolutePath"])
        self.assertEqual(str(self.replica.resolve()), receipt["replica"]["absolutePath"])
        self.assertEqual(
            "REPRODUCTION_ONLY_NOT_AUTHORITY_SELECTOR", receipt["replica"]["role"]
        )
        self.assertEqual(
            str(self.generation.resolve()),
            receipt["selectionRule"]["requiredAbsolutePath"],
        )
        self.assertEqual(
            self.AUTHORITY_READY_SHA256,
            receipt["selectionRule"]["literalReadySha256ByRoot"],
        )
        self.assertEqual(
            self.AUTHORITY_REDUCER_ID,
            receipt["selectionRule"]["requiredReducerId"],
        )
        self.assertEqual(
            campaign.MISSION_NATIVE_SETPOS_RUNTIME_PARENT_READY_SHA256,
            receipt["parent"]["readySha256"],
        )
        self.assertEqual(
            campaign.MISSION_NATIVE_SETPOS_RUNTIME_PARENT_AUTHORITY_SHA256,
            receipt["parent"]["authorityReceiptSha256"],
        )
        self.assertEqual(
            campaign.MISSION_NATIVE_SETPOS_RUNTIME_PROOF_READY_SHA256,
            receipt["proof"]["readySha256"],
        )
        self.assertEqual(
            campaign.MISSION_NATIVE_SETPOS_RUNTIME_EXPECTED_GENERATION16_COUNTS,
            receipt["counts"],
        )
        self.assertEqual(
            self.OUTPUT_SHA256,
            {name: stamp["sha256"] for name, stamp in receipt["outputs"].items()},
        )
        boundary = receipt["claimBoundary"]
        self.assertEqual("C2_BOUNDED_RUNTIME", boundary["semanticGrade"])
        self.assertTrue(boundary["scriptVisiblePositionCopy"])
        self.assertFalse(boundary["completeInternalWriteSet"])
        self.assertFalse(boundary["liveGhidraMutation"])
        self.assertEqual("PARTIAL_CONTRACT", boundary["rebuildState"])
        self.assertEqual(17, receipt["limitations"]["nextValidGeneration"])
        self.assertEqual("OPEN", receipt["limitations"]["internalWriteSet"])
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, receipt["author"]["sha256"])
        self.assertEqual(
            self.AUTHORITY_BOOTSTRAP_SHA256,
            campaign.coverage.sha256_of(bootstrap),
        )
        self.assertEqual(
            self.AUTHORITY_BOOTSTRAP_SHA256,
            receipt["frozenOwners"]["preImportLauncher"]["sha256"],
        )
        self.assertEqual(0, receipt["rebuild"]["focusedParity"]["exitCode"])
        self.assertEqual("Passed!", receipt["rebuild"]["focusedParity"]["marker"])
        for root_name, section in (
            (self.generation.name, "canonicalLiteralPinnedFullReplay"),
            (self.replica.name, "replicaLiteralPinnedFullReplay"),
        ):
            replay = receipt["verification"][section]
            self.assertEqual(0, replay["exitCode"])
            self.assertEqual("CAMPAIGN_VERIFIED", replay["marker"])
            self.assertEqual(
                self.AUTHORITY_READY_SHA256[root_name],
                replay["command"][
                    replay["command"].index("--expected-ready-sha256") + 1
                ],
            )
            self.assertEqual(
                self.AUTHORITY_REDUCER_ID,
                replay["command"][
                    replay["command"].index("--expected-reducer-id") + 1
                ],
            )


class CampaignRecoveryGeneration17LockHitBoundedContractTests(unittest.TestCase):
    AUTHORITY_RECEIPT_BYTES = 9956
    AUTHORITY_RECEIPT_SHA256 = (
        "c37aae056dc2f04d946db69d4e13d276dbc11d1a52976c97657af0a5549b00cb"
    )
    AUTHORITY_AUTHOR_BYTES = 20346
    AUTHORITY_AUTHOR_SHA256 = (
        "dee3d92a93e192ce5cb04b46a0946e10fb056894ce835ad0689b5181bfe5ae1a"
    )
    AUTHORITY_BOOTSTRAP_SHA256 = (
        "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b"
    )
    AUTHORITY_REDUCER_ID = (
        "fbb343d629fa12a641aced04db88b59e5270e1f45990d9d203284302f8761621"
    )
    AUTHORITY_READY_SHA256 = {
        "generation-17-lockhit-bounded-contract-v1": (
            "6d794905d6fc5daea11f99b781cf8eb7740765e749c784d02507d43436b801a2"
        ),
        "generation-17-lockhit-bounded-contract-replica-v1": (
            "dcef22def1e4190fd32366637654587202635c185f0088ca39d883168bba7ba6"
        ),
    }
    OUTPUT_SHA256 = {
        "campaign-functions.tsv": "50970af530be6cf9885de7af33cede59f8ed80f2f98bf6541ec4239a77db1bd2",
        "campaign-residuals.tsv": "6aaa5da3917079de3a172fb24b7de2b3ba99f1bc05ad40c4c427fcaa76d55ab6",
        "campaign-questions.tsv": "e86ead4f97a94182750a522c9cf44d0664108dec3b81678c28be14531213a3b0",
        "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
        "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
        "campaign-contracts.tsv": "166358f44a0e1bad7c29b541d3602fa722f8b57c7b70aee28ace6e247c89e1c1",
        "campaign-adjudications.tsv": "ec23e0831400085e456b386ab190116700de6cae43da4f6bde071df9a8cb4770",
        "campaign-supersessions.tsv": "4da539b16248ae9f5abfe5aa61845d9ec96351605060b8b05f16abb7353b008e",
    }

    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        cls.parent = base / "generation-16-mission-native-setpos-runtime-v1"
        cls.generation = base / "generation-17-lockhit-bounded-contract-v1"
        cls.replica = base / "generation-17-lockhit-bounded-contract-replica-v1"
        cls.authority = base / "generation-17-lockhit-bounded-contract-authority.ready.json"
        cls.proof = repo / campaign.LOCKHIT_BOUNDED_PROOF_RELATIVE
        if not (cls.parent / "campaign.ready.json").is_file():
            raise unittest.SkipTest(
                "maintainer-local canonical Gen16 prerequisite is unavailable"
            )
        for root, ready_name, label in (
            (cls.proof, campaign.lockhit_contract.READY_NAME, "LockHit bounded proof"),
            (cls.generation, "campaign.ready.json", "canonical Generation 17"),
            (cls.replica, "campaign.ready.json", "replicated Generation 17"),
        ):
            if not (root / ready_name).is_file():
                raise AssertionError(f"required {label} is missing: {root}")
        if not cls.authority.is_file():
            raise AssertionError(
                f"required Generation 17 authority is missing: {cls.authority}"
            )

    @classmethod
    def authority_verify(cls, root: Path) -> subprocess.CompletedProcess:
        expected_ready = cls.AUTHORITY_READY_SHA256.get(root.name)
        if expected_ready is None:
            raise AssertionError(f"root is not an externally selected Gen17 copy: {root}")
        repo = Path(__file__).resolve().parent.parent
        bootstrap = Path(__file__).resolve().parent / "re_campaign_frozen_bootstrap.py"
        environment = os.environ.copy()
        environment["BEA_REPO_ROOT"] = os.fspath(repo)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                os.fspath(Path(os.sys.executable)),
                "-I",
                "-B",
                os.fspath(bootstrap),
                "--campaign",
                os.fspath(root),
                "--mode",
                "full",
                "--expected-ready-sha256",
                expected_ready,
                "--expected-reducer-id",
                cls.AUTHORITY_REDUCER_ID,
            ],
            cwd=repo,
            env=environment,
            capture_output=True,
            text=True,
            timeout=1200,
            check=False,
        )

    @staticmethod
    def frozen_verify(root: Path) -> subprocess.CompletedProcess:
        return CampaignRecoveryGeneration8Tests.frozen_verify(root, replay=False)

    @staticmethod
    def reducer_files(root: Path) -> dict[str, bytes]:
        return CampaignRecoveryGeneration9Tests.reducer_files(root)

    @staticmethod
    def write_ready(root: Path, receipt: dict) -> None:
        (root / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def test_two_independent_builds_are_deterministic_and_fully_replay(self) -> None:
        for name, digest in self.OUTPUT_SHA256.items():
            self.assertEqual(digest, campaign.coverage.sha256_of(self.generation / name))
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        self.assertEqual(
            self.reducer_files(self.generation), self.reducer_files(self.replica)
        )
        for root in (self.generation, self.replica):
            completed = self.authority_verify(root)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
        normalized = []
        for root in (self.generation, self.replica):
            receipt = json.loads(
                (root / "campaign.ready.json").read_text(encoding="utf-8")
            )
            self.assertEqual(17, receipt["generation"])
            self.assertEqual(
                campaign.LOCKHIT_BOUNDED_ADVANCE_KIND, receipt["advance"]["kind"]
            )
            self.assertEqual(
                campaign.LOCKHIT_BOUNDED_ADVANCE_SCHEMA,
                receipt["advance"]["schema"],
            )
            self.assertEqual("LHC-997ec4a9b32a80a8", receipt["advance"]["observationId"])
            receipt["generatedAtUtc"] = "<generated>"
            for output in receipt["outputs"].values():
                output["lastWriteUtc"] = "<write>"
            normalized.append(receipt)
        self.assertEqual(normalized[0], normalized[1])

    def test_exact_bounded_contract_delta_preserves_open_paths(self) -> None:
        entity = campaign.lockhit_contract.LOCKHIT_ENTITY
        contract_id = campaign.lockhit_contract.LOCKHIT_CONTRACT
        parent_question_id = campaign.lockhit_contract.LOCKHIT_QUESTION
        parent_functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.parent / "campaign-functions.tsv")
        }
        functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.generation / "campaign-functions.tsv")
        }
        self.assertEqual(
            {entity},
            {key for key in functions if functions[key] != parent_functions[key]},
        )
        self.assertEqual("C2_BOUNDED_RUNTIME", functions[entity]["semanticGrade"])
        self.assertEqual("BOUNDED_CONTRACT", functions[entity]["resolutionState"])

        parent_contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-contracts.tsv")
        }
        contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-contracts.tsv")
        }
        self.assertEqual(
            {contract_id},
            {key for key in contracts if contracts[key] != parent_contracts[key]},
        )
        contract = contracts[contract_id]
        self.assertEqual("C2_BOUNDED_RUNTIME", contract["semanticGrade"])
        self.assertEqual("MEASURED_BOUNDED_PATH", contract["runtimeVerdict"])
        self.assertEqual("SURVIVED", contract["refuterVerdict"])
        self.assertEqual("NOT_READY", contract["rebuildState"])
        self.assertIn("null, not-found, and multi-node behavior remain open", contract["failureModes"])
        self.assertIn(campaign.LOCKHIT_BOUNDED_PROOF_READY_SHA256, contract["evidenceRefs"])

        parent_questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-questions.tsv")
        }
        questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.generation / "campaign-questions.tsv")
        }
        self.assertEqual(
            {parent_question_id},
            {key for key in parent_questions if questions[key] != parent_questions[key]},
        )
        successor_ids = set(questions) - set(parent_questions)
        self.assertEqual(
            {
                "Q-2e152f6c1ad74504",
                "Q-b4838b78fddb5be6",
                "Q-560e644e27958b87",
                "Q-b0230a2ddfa473a1",
            },
            successor_ids,
        )
        self.assertEqual("CLOSED_SURVIVED", questions[parent_question_id]["state"])
        for question_id in successor_ids:
            self.assertEqual("OPEN", questions[question_id]["state"])
            self.assertEqual(parent_question_id, questions[question_id]["parentQuestionId"])
            self.assertIn(question_id, contract["questionIds"].split(";"))

        parent_adjudications = {
            row["adjudicationId"]
            for row in campaign._read_tsv(self.parent / "campaign-adjudications.tsv")
        }
        fresh = [
            row
            for row in campaign._read_tsv(self.generation / "campaign-adjudications.tsv")
            if row["adjudicationId"] not in parent_adjudications
        ]
        self.assertEqual(["A-9d0865b13dd319ef"], [row["adjudicationId"] for row in fresh])
        self.assertEqual("True", fresh[0]["semanticPromotionApplied"])
        for name in (
            "campaign-residuals.tsv",
            "campaign-scenarios.tsv",
            "campaign-levers.tsv",
            "campaign-supersessions.tsv",
        ):
            self.assertEqual(
                (self.parent / name).read_bytes(),
                (self.generation / name).read_bytes(),
                name,
            )

    def test_integrity_and_external_authority_reject_overclaim_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            original = json.loads(
                (forged / "campaign.ready.json").read_text(encoding="utf-8")
            )

            def rejected(mutator, expected: str) -> None:
                receipt = json.loads(json.dumps(original))
                mutator(receipt)
                self.write_ready(forged, receipt)
                completed = self.frozen_verify(forged)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(
                lambda value: value.update({"advance": None}),
                "Generation 16 recovery child is not the exact LockHit bounded-contract advance",
            )
            rejected(
                lambda value: value["advance"].update(
                    {"independentGameplayReplications": 1}
                ),
                "LockHit bounded-contract advance receipt differs",
            )
            rejected(
                lambda value: value.update({"generatedAtUtc": "not-a-time"}),
                "invalid timestamp",
            )

        repo = Path(__file__).resolve().parent.parent
        author = repo / "tools/re_lockhit_bounded_campaign_authority.py"
        bootstrap = repo / "tools/re_campaign_frozen_bootstrap.py"
        self.assertEqual(self.AUTHORITY_RECEIPT_BYTES, self.authority.stat().st_size)
        self.assertEqual(
            self.AUTHORITY_RECEIPT_SHA256, campaign.coverage.sha256_of(self.authority)
        )
        self.assertEqual(self.AUTHORITY_AUTHOR_BYTES, author.stat().st_size)
        self.assertEqual(
            self.AUTHORITY_AUTHOR_SHA256, campaign.coverage.sha256_of(author)
        )
        receipt = json.loads(self.authority.read_text(encoding="utf-8"))
        self.assertEqual("READY", receipt["verdict"])
        self.assertEqual("FULL_REPLAY_CAMPAIGN_AUTHORITY", receipt["authorityClass"])
        self.assertEqual(str(self.generation.resolve()), receipt["canonical"]["absolutePath"])
        self.assertEqual(
            "REPRODUCTION_ONLY_NOT_AUTHORITY_SELECTOR", receipt["replica"]["role"]
        )
        self.assertEqual(
            str(self.generation.resolve()), receipt["selectionRule"]["requiredAbsolutePath"]
        )
        self.assertEqual(
            self.AUTHORITY_READY_SHA256,
            receipt["selectionRule"]["literalReadySha256ByRoot"],
        )
        self.assertEqual(
            self.AUTHORITY_REDUCER_ID, receipt["selectionRule"]["requiredReducerId"]
        )
        self.assertEqual(
            campaign.LOCKHIT_BOUNDED_PARENT_AUTHORITY_SHA256,
            receipt["parent"]["authorityReceiptSha256"],
        )
        self.assertEqual(
            campaign.LOCKHIT_BOUNDED_PROOF_READY_SHA256,
            receipt["proof"]["readySha256"],
        )
        self.assertEqual(self.OUTPUT_SHA256, {
            name: stamp["sha256"] for name, stamp in receipt["outputs"].items()
        })
        boundary = receipt["claimBoundary"]
        self.assertEqual("C2_BOUNDED_RUNTIME", boundary["semanticGrade"])
        self.assertFalse(boundary["independentGameplayReplication"])
        self.assertFalse(boundary["globalFreeHeadDirectlyWatched"])
        self.assertEqual("OPEN", boundary["nullNotFoundMultiNodePaths"])
        self.assertEqual("NOT_READY", boundary["rebuildState"])
        self.assertEqual(18, receipt["limitations"]["nextValidGeneration"])
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, receipt["author"]["sha256"])
        self.assertEqual(
            self.AUTHORITY_BOOTSTRAP_SHA256, campaign.coverage.sha256_of(bootstrap)
        )
        self.assertEqual(
            self.AUTHORITY_BOOTSTRAP_SHA256,
            receipt["frozenOwners"]["preImportLauncher"]["sha256"],
        )
        for root_name, section in (
            (self.generation.name, "canonicalLiteralPinnedFullReplay"),
            (self.replica.name, "replicaLiteralPinnedFullReplay"),
        ):
            replay = receipt["verification"][section]
            self.assertEqual(0, replay["exitCode"])
            self.assertEqual("CAMPAIGN_VERIFIED", replay["marker"])
            self.assertEqual(
                self.AUTHORITY_READY_SHA256[root_name],
                replay["command"][replay["command"].index("--expected-ready-sha256") + 1],
            )


class CampaignRecoveryGeneration18TokenArchiveParserContractTests(unittest.TestCase):
    AUTHORITY_RECEIPT_BYTES = 12742
    AUTHORITY_RECEIPT_SHA256 = (
        "c13dcef4aaae7c95b08bd75a502069a47274e9d577b48b05c57a5f3adcf6b7a6"
    )
    AUTHORITY_AUTHOR_BYTES = 28355
    AUTHORITY_AUTHOR_SHA256 = (
        "4aceb34f5ac6a007f0633c9d8b0a914e449a37f143f58349fdfe08bb7bea3c80"
    )
    AUTHORITY_BOOTSTRAP_BYTES = 17831
    AUTHORITY_BOOTSTRAP_SHA256 = (
        "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b"
    )
    AUTHORITY_REDUCER_ID = (
        "ee8bddfb4cf6f05f768d9e067ea1330753eecbb3f7eb97553dfe6fa4da8bad74"
    )
    AUTHORITY_READY_SHA256 = {
        "generation-18-tokenarchive-parser-contract-v1": (
            "4ae3a7b8dc4baa7cb83125fc8005503499b083fd1944f19bdfb84755f663d97e"
        ),
        "generation-18-tokenarchive-parser-contract-replica-v1": (
            "9267333dc7492e3ffa36cd4dbb771797046dfdbf1782a451b1e8853022efb4d1"
        ),
    }
    OUTPUT_SHA256 = {
        "campaign-functions.tsv": "cfaf73803c360285ecedfda29e7a89c8119d05bbf2d047e124522dedc9256454",
        "campaign-residuals.tsv": "6aaa5da3917079de3a172fb24b7de2b3ba99f1bc05ad40c4c427fcaa76d55ab6",
        "campaign-questions.tsv": "1b0609bada6a4595b8420f15ec3bd4d5c743d79100fa8012bd26cb9be15b3a56",
        "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
        "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
        "campaign-contracts.tsv": "f9a7674757ad85fc7ec8fa3d5dbff1b933b0f950b5b6c323ffe088d3a137752c",
        "campaign-adjudications.tsv": "70a957db451bea6653020cb9829416b363a2f541a357bf6682a12cbc122b7bab",
        "campaign-supersessions.tsv": "4da539b16248ae9f5abfe5aa61845d9ec96351605060b8b05f16abb7353b008e",
    }
    COUNTS = {
        "functions": 8125,
        "residuals": 6118,
        "questions": 15254,
        "scenarios": 72,
        "levers": 915,
        "contracts": 14243,
        "adjudications": 6097,
        "supersessions": 588,
    }
    PROOF_RELATIVE = Path(
        "local-lab/tokenarchive-parser-contract-reproof-20260809-v7"
    )
    PROOF_SCHEMA = "bea.re.tokenarchive-parser-contract-reproof.v7"
    PROOF_READY_SHA256 = (
        "ed2aca4f54a82476a9f1cc1cb7e1a81376fae9b9c6dee22fcf890fe15fbf07bc"
    )
    PROOF_AUTHOR_SHA256 = (
        "b94a2216233fbd0623a14df8e27cbb4d1b66d978da43f8744b0e479d7e9c8ee1"
    )
    ADVANCE_KIND = "STATIC_TOKENARCHIVE_READNEXTTOKEN_PARSER_CONTRACT"
    ADVANCE_SCHEMA = (
        "bea.re.static-tokenarchive-readnexttoken-parser-contract-advance.v1"
    )
    OBSERVATION_ID = "TPC-c23c8c9e0fdbe42c"
    ENTITY = (
        "CODE:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:"
        "VA=0x004f57b0:RANGES=bedc826d01b6a8a1792de76da45537e1b3f6f663051efecc30414377d0efe76b"
    )
    CONTRACT = "C-a1dd659dcb7d74c1"
    PARENT_QUESTION = "Q-f40657bf78b29abb"
    SUCCESSOR_QUESTION = "Q-439e6a926003084e"
    ADJUDICATION = "A-a6a3bc60970e8e72"

    @classmethod
    def setUpClass(cls) -> None:
        repo = Path(__file__).resolve().parent.parent
        base = repo / "local-lab/re-campaign-incident-recovery-20260808-v1"
        cls.repo = repo
        cls.parent = base / "generation-17-lockhit-bounded-contract-v1"
        cls.generation = base / "generation-18-tokenarchive-parser-contract-v1"
        cls.replica = base / "generation-18-tokenarchive-parser-contract-replica-v1"
        cls.authority = base / "generation-18-tokenarchive-parser-contract-authority.ready.json"
        cls.proof = repo / cls.PROOF_RELATIVE
        if not (cls.parent / "campaign.ready.json").is_file():
            raise unittest.SkipTest(
                "maintainer-local canonical Gen17 prerequisite is unavailable"
            )
        for root, ready_name, label in (
            (cls.proof, "proof.ready.json", "TokenArchive v7 proof"),
            (cls.generation, "campaign.ready.json", "canonical Generation 18"),
            (cls.replica, "campaign.ready.json", "replicated Generation 18"),
        ):
            if not (root / ready_name).is_file():
                raise AssertionError(f"required {label} is missing: {root}")
        if not cls.authority.is_file():
            raise AssertionError(
                f"required Generation 18 authority is missing: {cls.authority}"
            )

    @classmethod
    def authority_verify(
        cls, root: Path, *, bootstrap: Path | None = None
    ) -> subprocess.CompletedProcess:
        expected_ready = cls.AUTHORITY_READY_SHA256.get(root.name)
        if expected_ready is None:
            raise AssertionError(
                f"root is not an externally selected Gen18 copy: {root}"
            )
        selected_bootstrap = bootstrap or (
            cls.repo / "tools/re_campaign_frozen_bootstrap.py"
        )
        self_hash = campaign.coverage.sha256_of(selected_bootstrap)
        if (
            selected_bootstrap.stat().st_size != cls.AUTHORITY_BOOTSTRAP_BYTES
            or self_hash != cls.AUTHORITY_BOOTSTRAP_SHA256
        ):
            raise AssertionError("literal-pinned frozen bootstrap differs")
        environment = os.environ.copy()
        environment["BEA_REPO_ROOT"] = os.fspath(cls.repo)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                os.fspath(Path(os.sys.executable)),
                "-I",
                "-B",
                os.fspath(selected_bootstrap),
                "--campaign",
                os.fspath(root),
                "--mode",
                "full",
                "--expected-ready-sha256",
                expected_ready,
                "--expected-reducer-id",
                cls.AUTHORITY_REDUCER_ID,
            ],
            cwd=cls.repo,
            env=environment,
            capture_output=True,
            text=True,
            timeout=1200,
            check=False,
        )

    @staticmethod
    def frozen_verify(root: Path) -> subprocess.CompletedProcess:
        return CampaignRecoveryGeneration8Tests.frozen_verify(root, replay=False)

    @staticmethod
    def reducer_files(root: Path) -> dict[str, bytes]:
        return CampaignRecoveryGeneration9Tests.reducer_files(root)

    @staticmethod
    def write_ready(root: Path, receipt: dict) -> None:
        (root / "campaign.ready.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def test_two_independent_builds_are_deterministic_and_fully_replay(self) -> None:
        for name, digest in self.OUTPUT_SHA256.items():
            self.assertEqual(digest, campaign.coverage.sha256_of(self.generation / name))
            self.assertEqual(
                (self.generation / name).read_bytes(),
                (self.replica / name).read_bytes(),
                name,
            )
        self.assertEqual(
            self.reducer_files(self.generation), self.reducer_files(self.replica)
        )
        self.assertEqual(33, len(self.reducer_files(self.generation)))

        with tempfile.TemporaryDirectory() as temporary:
            tools = Path(temporary) / "tools"
            tools.mkdir()
            copied_bootstrap = tools / "re_campaign_frozen_bootstrap.py"
            shutil.copy2(
                self.repo / "tools/re_campaign_frozen_bootstrap.py",
                copied_bootstrap,
            )
            marker = Path(temporary) / "live-source-poison-imported.txt"
            poison = (
                "from pathlib import Path\n"
                f"Path({os.fspath(marker)!r}).write_text('imported', encoding='utf-8')\n"
                "raise RuntimeError('live source must not be imported')\n"
            )
            (tools / "re_campaign.py").write_text(poison, encoding="utf-8")
            (tools / "re_tokenarchive_parser_contract.py").write_text(
                poison, encoding="utf-8"
            )
            completed = self.authority_verify(
                self.generation, bootstrap=copied_bootstrap
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)
            self.assertFalse(marker.exists())

        completed = self.authority_verify(self.replica)
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("CAMPAIGN_VERIFIED", completed.stdout)

        normalized = []
        for root in (self.generation, self.replica):
            receipt = json.loads(
                (root / "campaign.ready.json").read_text(encoding="utf-8")
            )
            self.assertEqual(18, receipt["generation"])
            self.assertEqual(self.COUNTS, receipt["counts"])
            self.assertEqual(self.ADVANCE_KIND, receipt["advance"]["kind"])
            self.assertEqual(self.ADVANCE_SCHEMA, receipt["advance"]["schema"])
            self.assertEqual(
                self.OBSERVATION_ID, receipt["advance"]["observationId"]
            )
            receipt["generatedAtUtc"] = "<generated>"
            for output in receipt["outputs"].values():
                output["lastWriteUtc"] = "<write>"
            normalized.append(receipt)
        self.assertEqual(normalized[0], normalized[1])

    def test_exact_static_contract_delta_preserves_runtime_unknowns(self) -> None:
        parent_functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(self.parent / "campaign-functions.tsv")
        }
        functions = {
            row["entityKey"]: row
            for row in campaign._read_tsv(
                self.generation / "campaign-functions.tsv"
            )
        }
        self.assertEqual(
            {self.ENTITY},
            {key for key in functions if functions[key] != parent_functions[key]},
        )
        self.assertEqual("C1_CANDIDATE_PARTIAL", functions[self.ENTITY]["semanticGrade"])
        self.assertEqual("CANDIDATE_CONTRACT", functions[self.ENTITY]["resolutionState"])
        self.assertEqual(
            {"OPAQUE": 7902, "C1_CANDIDATE_PARTIAL": 216, "C2_BOUNDED_RUNTIME": 7},
            dict(Counter(row["semanticGrade"] for row in functions.values())),
        )

        parent_contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-contracts.tsv")
        }
        contracts = {
            row["contractId"]: row
            for row in campaign._read_tsv(
                self.generation / "campaign-contracts.tsv"
            )
        }
        self.assertEqual(
            {self.CONTRACT},
            {key for key in contracts if contracts[key] != parent_contracts[key]},
        )
        contract = contracts[self.CONTRACT]
        self.assertEqual("C1_CANDIDATE_PARTIAL", contract["semanticGrade"])
        self.assertEqual("CANDIDATE_NEEDS_REFUTER", contract["contractState"])
        self.assertEqual("UNSCORED", contract["runtimeVerdict"])
        self.assertEqual("UNSCORED", contract["refuterVerdict"])
        self.assertEqual("PARTIAL_CONTRACT", contract["rebuildState"])
        self.assertIn(self.PROOF_READY_SHA256, contract["evidenceRefs"])
        self.assertEqual(
            {self.PARENT_QUESTION, self.SUCCESSOR_QUESTION},
            set(contract["questionIds"].split(";")),
        )

        parent_questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(self.parent / "campaign-questions.tsv")
        }
        questions = {
            row["questionId"]: row
            for row in campaign._read_tsv(
                self.generation / "campaign-questions.tsv"
            )
        }
        self.assertEqual(
            {self.PARENT_QUESTION},
            {
                key
                for key in parent_questions
                if questions[key] != parent_questions[key]
            },
        )
        self.assertEqual({self.SUCCESSOR_QUESTION}, set(questions) - set(parent_questions))
        self.assertEqual("CLOSED_SURVIVED", questions[self.PARENT_QUESTION]["state"])
        self.assertEqual("OPEN", questions[self.SUCCESSOR_QUESTION]["state"])
        self.assertEqual(
            self.PARENT_QUESTION,
            questions[self.SUCCESSOR_QUESTION]["parentQuestionId"],
        )

        parent_adjudications = {
            row["adjudicationId"]
            for row in campaign._read_tsv(
                self.parent / "campaign-adjudications.tsv"
            )
        }
        fresh = [
            row
            for row in campaign._read_tsv(
                self.generation / "campaign-adjudications.tsv"
            )
            if row["adjudicationId"] not in parent_adjudications
        ]
        self.assertEqual([self.ADJUDICATION], [row["adjudicationId"] for row in fresh])
        self.assertEqual("SURVIVED", fresh[0]["refuterVerdict"])
        self.assertEqual("True", fresh[0]["semanticPromotionApplied"])
        self.assertEqual(self.PROOF_SCHEMA, fresh[0]["overlaySchema"])
        for name in (
            "campaign-residuals.tsv",
            "campaign-scenarios.tsv",
            "campaign-levers.tsv",
            "campaign-supersessions.tsv",
        ):
            self.assertEqual(
                (self.parent / name).read_bytes(),
                (self.generation / name).read_bytes(),
                name,
            )

        with (self.proof / "writer-calls.tsv").open(
            encoding="utf-8", newline=""
        ) as stream:
            writer_calls = list(csv.DictReader(stream, delimiter="\t"))
        self.assertEqual(141, len(writer_calls))
        self.assertNotIn("<no_function>", {row["callerName"] for row in writer_calls})
        corrected = {
            row["callVa"]: row["callerName"]
            for row in writer_calls
            if row["callVa"] in {"0x004c25d1", "0x004c4500"}
        }
        self.assertEqual(
            {
                "0x004c25d1": "CPDTimeline__VFunc_7_004c25c0",
                "0x004c4500": "CPDMover__VFunc_7_004c44f0",
            },
            corrected,
        )

    def test_integrity_and_external_authority_reject_overclaim_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            forged = Path(temporary) / "forged"
            shutil.copytree(self.generation, forged)
            original = json.loads(
                (forged / "campaign.ready.json").read_text(encoding="utf-8")
            )

            def rejected(mutator, expected: str) -> None:
                receipt = json.loads(json.dumps(original))
                mutator(receipt)
                self.write_ready(forged, receipt)
                completed = self.frozen_verify(forged)
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(expected, completed.stderr)

            rejected(
                lambda value: value.update({"advance": None}),
                "Generation 18 recovery campaign is not the exact TokenArchive parser-contract advance",
            )
            rejected(
                lambda value: value["advance"].update({"runtimeReplaysProved": 1}),
                "TokenArchive parser-contract advance receipt differs",
            )
            rejected(
                lambda value: value["advance"]["proof"].update(
                    {"root": "local-lab/tokenarchive-parser-contract-reproof-20260809-v1"}
                ),
                "TokenArchive parser-contract advance receipt differs",
            )
            rejected(
                lambda value: value.update({"generatedAtUtc": "not-a-time"}),
                "invalid timestamp",
            )

            self.write_ready(forged, original)
            output = forged / "campaign-functions.tsv"
            anchor = Path(temporary) / "ledger-anchor.tsv"
            anchor.write_bytes(output.read_bytes())
            output.unlink()
            os.link(anchor, output)
            completed = self.frozen_verify(forged)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("multiple hard links", completed.stderr)

        author = self.repo / "tools/re_tokenarchive_parser_campaign_authority.py"
        bootstrap = self.repo / "tools/re_campaign_frozen_bootstrap.py"
        self.assertEqual(self.AUTHORITY_RECEIPT_BYTES, self.authority.stat().st_size)
        self.assertEqual(
            self.AUTHORITY_RECEIPT_SHA256,
            campaign.coverage.sha256_of(self.authority),
        )
        self.assertEqual(self.AUTHORITY_AUTHOR_BYTES, author.stat().st_size)
        self.assertEqual(
            self.AUTHORITY_AUTHOR_SHA256, campaign.coverage.sha256_of(author)
        )
        receipt = json.loads(self.authority.read_text(encoding="utf-8"))
        self.assertEqual("bea.re.tokenarchive-parser-generation18-authority.v1", receipt["schema"])
        self.assertEqual("READY", receipt["verdict"])
        self.assertEqual("FULL_REPLAY_CAMPAIGN_AUTHORITY", receipt["authorityClass"])
        self.assertEqual(
            "FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY",
            receipt["replayScope"],
        )
        self.assertEqual(str(self.generation.resolve()), receipt["canonical"]["absolutePath"])
        self.assertEqual(str(self.replica.resolve()), receipt["replica"]["absolutePath"])
        self.assertEqual(
            "REPRODUCTION_ONLY_NOT_AUTHORITY_SELECTOR", receipt["replica"]["role"]
        )
        self.assertEqual(
            str(self.generation.resolve()),
            receipt["selectionRule"]["requiredAbsolutePath"],
        )
        self.assertEqual(
            self.AUTHORITY_READY_SHA256,
            receipt["selectionRule"]["literalReadySha256ByRoot"],
        )
        self.assertEqual(
            self.AUTHORITY_REDUCER_ID,
            receipt["selectionRule"]["requiredReducerId"],
        )
        self.assertEqual(
            "6d794905d6fc5daea11f99b781cf8eb7740765e749c784d02507d43436b801a2",
            receipt["parent"]["readySha256"],
        )
        self.assertEqual(
            "c37aae056dc2f04d946db69d4e13d276dbc11d1a52976c97657af0a5549b00cb",
            receipt["parent"]["authorityReceiptSha256"],
        )
        self.assertEqual(self.PROOF_READY_SHA256, receipt["proof"]["readySha256"])
        self.assertEqual(self.PROOF_AUTHOR_SHA256, receipt["proof"]["authorSha256"])
        self.assertEqual(
            self.OUTPUT_SHA256,
            {name: stamp["sha256"] for name, stamp in receipt["outputs"].items()},
        )
        boundary = receipt["claimBoundary"]
        self.assertEqual("C1_STATIC", boundary["staticProofGrade"])
        self.assertEqual("C1_CANDIDATE_PARTIAL", boundary["campaignSemanticGrade"])
        self.assertEqual("SURVIVED", boundary["admissionAdjudicationVerdict"])
        self.assertEqual("UNSCORED", boundary["contractRefuterVerdict"])
        self.assertEqual("UNSCORED", boundary["runtimeVerdict"])
        self.assertEqual(0, boundary["runtimeReplays"])
        self.assertEqual("PARTIAL_CONTRACT", boundary["rebuildState"])
        self.assertFalse(boundary["liveGhidraMutation"])
        self.assertEqual(
            {"failed": 0, "passed": 3, "skipped": 0, "total": 3},
            receipt["rebuild"]["focusedParity"]["testCensus"],
        )
        self.assertEqual(19, receipt["limitations"]["nextValidGeneration"])
        self.assertEqual(self.AUTHORITY_AUTHOR_SHA256, receipt["author"]["sha256"])
        self.assertEqual(self.AUTHORITY_BOOTSTRAP_BYTES, bootstrap.stat().st_size)
        self.assertEqual(
            self.AUTHORITY_BOOTSTRAP_SHA256,
            campaign.coverage.sha256_of(bootstrap),
        )
        self.assertEqual(
            self.AUTHORITY_BOOTSTRAP_SHA256,
            receipt["frozenOwners"]["preImportLauncher"]["sha256"],
        )
        self.assertEqual(
            self.PROOF_AUTHOR_SHA256,
            receipt["frozenOwners"]["proof"]["sha256"],
        )
        for root_name, section in (
            (self.generation.name, "canonicalLiteralPinnedFullReplay"),
            (self.replica.name, "replicaLiteralPinnedFullReplay"),
        ):
            replay = receipt["verification"][section]
            self.assertEqual(0, replay["exitCode"])
            self.assertEqual("CAMPAIGN_VERIFIED", replay["marker"])
            self.assertEqual(
                self.AUTHORITY_READY_SHA256[root_name],
                replay["command"][
                    replay["command"].index("--expected-ready-sha256") + 1
                ],
            )
            self.assertEqual(
                self.AUTHORITY_REDUCER_ID,
                replay["command"][
                    replay["command"].index("--expected-reducer-id") + 1
                ],
            )


if __name__ == "__main__":
    raise SystemExit(0 if unittest.main(verbosity=2, exit=False).result.wasSuccessful() else 1)
