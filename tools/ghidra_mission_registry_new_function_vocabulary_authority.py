#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal the 34-row new-function MissionScript vocabulary scratch ceremony.

This owner never opens or mutates Ghidra.  It validates already-produced
scratch receipts, full inventories, replica provenance, and adverse controls.
The resulting receipt explicitly stops before any live-project operation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


REPO = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()
LANE = REPO / "local-lab/ghidra-mission-registry-new34-vocabulary-20260813-v1"
BASELINE = LANE / "baseline"
RUNS = LANE / "runs"
SCRATCH = LANE / "scratch"
PRE_FUNCTIONS = LANE / "pre/functions.tsv"
PRE_PROGRAM = LANE / "pre/program.tsv"
READY = LANE / "scratch-authority.ready.json"
EXTERNAL_PROBE_ROOT = REPO.parent / "bea-mission-new34-external-path-probe"

MANIFEST = REPO / (
    "reverse-engineering/binary-analysis/"
    "mission-script-registry-new-function-vocabulary-normalization-2026-08-13.tsv"
)
METADATA = REPO / (
    "reverse-engineering/binary-analysis/"
    "mission-script-registry-new-function-vocabulary-normalization-pre-metadata-2026-08-13.tsv"
)
OWNER = MANIFEST.with_suffix(".md")
REGISTRY = REPO / (
    "reverse-engineering/binary-analysis/mission-script-command-registry-2026-08-12.tsv"
)
REGISTRY_REPORT = REGISTRY.with_suffix(".md")
NAMING = REPO / (
    "reverse-engineering/binary-analysis/function-naming-convention-2026-08-12.md"
)
PROJECTION = REPO / (
    "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-13.tsv"
)
BOUNDARY_REPORT = REPO / (
    "reverse-engineering/binary-analysis/"
    "mission-script-registry-boundary-live-promotion-2026-08-13.md"
)
STATIC_CONTRACT_OWNER = REPO / (
    "reverse-engineering/binary-analysis/"
    "mission-script-registry-new-function-static-contracts-2026-08-13.md"
)
STATIC_CONTRACT_ROWS = STATIC_CONTRACT_OWNER.with_suffix(".tsv")
BOUNDARY_MANIFEST = REPO / (
    "reverse-engineering/binary-analysis/"
    "mission-script-registry-missing-function-boundaries-2026-08-13.tsv"
)
LIVE75_REPORT = REPO / (
    "reverse-engineering/binary-analysis/"
    "mission-script-registry-vocabulary-live-promotion-2026-08-13.md"
)
TOOL = REPO / "tools/GhidraApplyMissionRegistryNewFunctionVocabulary.java"
INVENTORY_TOOL = REPO / "tools/ExportFullFunctionInventory.java"
BACKUP_TOOL = REPO / "tools/ghidra_project_backup.py"
OPEN_PROBE = REPO / "tools/GhidraProjectOpenProbe.java"
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)
APPLICATION_PROPERTIES = ANALYZE_HEADLESS.parent.parent / "Ghidra/application.properties"

SCHEMA = "bea.ghidra.mission-registry-new-function-vocabulary-authority.v1"
TOOL_SCHEMA = "bea.ghidra.mission-registry-new-function-vocabulary.v1"
PROGRAM_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
CANONICAL_SHA = "cc769cb0b83aec0105d365e77f0702adcc1024914453b0f5615c8d7d1b333ce9"
PRE_FUNCTION_COUNT = 8_170
INSTRUCTION_COUNT = 549_872
TARGET_COUNT = 34
EMPTY_TAGS_SENTINEL = "<EMPTY>"
PRE_CATALOG = (6_854,
               "074dd7480aebfe46aabe5a48c1429348a814c9b51b0d71d985cbdac6e764603f",
               "0ac85baaf38153328266bf4c54178f44ad871f273dabba03dfd13aaf4ded1a97")
POST_CATALOG = (6_854,
                "074dd7480aebfe46aabe5a48c1429348a814c9b51b0d71d985cbdac6e764603f",
                "0cbec4d3c190f2df8be5a3bd67ceeeaa419d3d5d9b20602b7ff9e400ade12971")

STAMPS = {
    MANIFEST: (3_417, "6154fb4bd4ae398b02d783fb50cd18381c1d224e2ac4c6f9dc1d26abb4d1ddc1"),
    METADATA: (8_060, "cd4f6b4d4614870c12356ebce8702760d9e885e60eaf230ecd4316b06e61164f"),
    OWNER: (7_412, "b9f03fd35b57cbc054b35851ec5d442bd5c30a2b403047bd99d36e1771c621f1"),
    REGISTRY: (6_924, "61a44b1a393251bfd32c28a037648968575bfbd55afc1cba8e39bd269a5e1fdd"),
    REGISTRY_REPORT: (22_464, "337ee300b0a55eaeb4c4a66669621a2a1937b72bd8ac2bb373508d3a005ab34a"),
    NAMING: (4_255, "2ed51bc92a265043194426976df8138c009b64058581475de62f398e50ed4381"),
    PROJECTION: (502_854, "515170759dda2686db408d25296362275f8913f7be42b6f0536b986c591786ee"),
    BOUNDARY_REPORT: (4_433, "6753b80ad39c3e535ebbb8985e69f2bcf9282092ac16d27429d32c2f2e53a248"),
    STATIC_CONTRACT_OWNER: (9_113, "c8b599b7cce79beba453a39d78523b616bcf83f45403423872f533086ed761b7"),
    STATIC_CONTRACT_ROWS: (21_608, "86c0c4a0e0d5fe0078cb21f271b4985cb1c4fe89aa035b66215076dfbe784a31"),
    BOUNDARY_MANIFEST: (7_264, "e53fd6f4c44ab7f91779e0673e91ae3701514c486594cc733025334fe6289a42"),
    LIVE75_REPORT: (6_675, "0408c6e67171213cf4fbb510806137420f2194cca2d8a6c3790e7584c7507c32"),
    TOOL: (51_090, "ab238cefbdbcc1fa343f0e27f9daecea84ca127da6baca3383c3ffc926d9f388"),
    INVENTORY_TOOL: (23_963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"),
    BACKUP_TOOL: (27_502, "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58"),
    OPEN_PROBE: (3_452, "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab"),
    ANALYZE_HEADLESS: (2_930, "dd7b9d17d32ed70a71df82a43a21cdaed6c4ce67064e30f8642c149f81c2ae07"),
    APPLICATION_PROPERTIES: (659, "80890f309379ef60ecbb376a95448bd79e874145544ffcfabb5ba1835ac8a2cf"),
    PRE_FUNCTIONS: (7_086_736, "8eded18abddfc0726517f2a88c7f4b2df15ff0cd13d3b70a5ca7ebd5a7afea5b"),
    PRE_PROGRAM: (1_267, "a3c505c34b7ba26dec7088d9ee22e0f9c13365ae979be1ffc8f52301e1f368c1"),
}

ALLOWED_TARGET_FIELDS = {
    "name", "nameLen", "nameSha256", "fqname", "fqnameLen", "fqnameSha256",
    "nameSource", "signature", "signatureLen", "signatureSha256",
    "commentPresent", "commentLen", "commentSha256",
    "tagCount", "tagsSha256", "tags",
}


class AuthorityError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuthorityError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO).as_posix()
    except ValueError:
        return str(resolved)


def require_repo_path_claim(value: Any, expected: Path, label: str) -> str:
    require(isinstance(value, str) and value, f"{label} path is absent")
    expected_relative = relative(expected)
    require(not Path(expected_relative).is_absolute(),
            f"{label} expected path is outside repository: {expected}")
    normalized = value.replace("\\", "/")
    require(not Path(value).is_absolute(), f"{label} path is not repository-relative")
    require(normalized == expected_relative,
            f"{label} repo-relative path differs: {normalized}")
    return expected_relative


def stamp(path: Path) -> dict[str, Any]:
    path = path.resolve()
    require(path.is_file(), f"required file is absent: {path}")
    stat = path.stat()
    require(not path.is_symlink(), f"file is a symlink: {path}")
    require(not (getattr(stat, "st_file_attributes", 0) & 0x400),
            f"file is a reparse point: {path}")
    require(stat.st_nlink == 1, f"file is not single-link: {path}")
    return {"path": relative(path), "bytes": stat.st_size,
            "sha256": sha256_file(path)}


def require_stamp(path: Path) -> dict[str, Any]:
    actual = stamp(path)
    require((actual["bytes"], actual["sha256"]) == STAMPS[path],
            f"immutable input differs: {actual}")
    return actual


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise AuthorityError(f"invalid JSON at {path}: {exc}") from exc


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def parse_utc(value: Any, label: str) -> None:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} is not UTC")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"{label} is malformed") from exc


def load_manifest() -> dict[str, dict[str, str]]:
    rows = read_tsv(MANIFEST)
    require(len(rows) == TARGET_COUNT, "manifest row count differs")
    result = {row["handlerVa"].lower(): row for row in rows}
    require(len(result) == TARGET_COUNT, "manifest handler addresses are not unique")
    require(len({row["index"] for row in rows}) == TARGET_COUNT,
            "manifest registry indices are not unique")
    require(len({row["proposedName"] for row in rows}) == TARGET_COUNT,
            "manifest proposed names are not unique")
    counts: dict[str, int] = {}
    canonical = []
    for row in rows:
        counts[row["cohort"]] = counts.get(row["cohort"], 0) + 1
        require(row["proposedName"] == "IScript__" + row["command"],
                f"proposed registry name differs at {row['handlerVa']}")
        canonical.append("\t".join((row["index"], row["handlerVa"],
                                     row["expectedPreName"], row["proposedName"])))
    require(counts == {"NEW34_STATIC_C1": 34},
            f"cohort partition differs: {counts}")
    payload = ("\n".join(canonical) + "\n").encode()
    require(len(payload) == 1_684 and hashlib.sha256(payload).hexdigest() == CANONICAL_SHA,
            "canonical projection differs")
    return result


def load_metadata() -> dict[str, dict[str, str]]:
    rows = read_tsv(METADATA)
    for row in rows:
        serialized = row["preTags"]
        require(serialized != "", "PRE tag field must use explicit empty sentinel")
        if serialized == EMPTY_TAGS_SENTINEL:
            require(row["preTagCount"] == "0" and
                    row["preTagsSha256"] == hashlib.sha256(b"").hexdigest(),
                    f"empty PRE tag sentinel metadata differs at {row['handlerVa']}")
            row["preTags"] = ""
        else:
            require(EMPTY_TAGS_SENTINEL not in serialized.split(","),
                    f"PRE tag sentinel used as a tag at {row['handlerVa']}")
            require(row["preTagCount"] != "0",
                    f"empty PRE tag set lacks sentinel at {row['handlerVa']}")
    result = {row["handlerVa"].lower(): row for row in rows}
    require(len(rows) == len(result) == TARGET_COUNT, "PRE metadata row count differs")
    return result


def validate_static_contract_join(
        manifest: Mapping[str, Mapping[str, str]]) -> dict[str, Any]:
    static_rows = read_tsv(STATIC_CONTRACT_ROWS)
    boundary_rows = read_tsv(BOUNDARY_MANIFEST)
    registry_rows = read_tsv(REGISTRY)
    require(len(static_rows) == len(boundary_rows) == 34,
            "new-boundary static-contract census differs")
    manifest_join = {(row["index"], row["command"], row["handlerVa"].lower())
                     for row in manifest.values()}
    static_join = {(row["registryIndex"], row["command"], row["entry"].lower())
                   for row in static_rows}
    boundary_join = {(row["registryIndex"], row["command"], row["entry"].lower())
                     for row in boundary_rows}
    require(len(manifest_join) == len(static_join) == len(boundary_join) == 34 and
            manifest_join == static_join == boundary_join,
            "manifest, boundary, and static-contract registry triples do not join exactly")
    manifest_boundaries = {
        (row["index"], row["command"], row["registryRecordVa"].lower(),
         row["handlerVa"].lower(), row["expectedPreName"])
        for row in manifest.values()
    }
    boundary_full = {
        (row["registryIndex"], row["command"], row["recordVa"].lower(),
         row["entry"].lower(), row["expectedDefaultName"])
        for row in boundary_rows
    }
    require(len(manifest_boundaries) == len(boundary_full) == 34 and
            manifest_boundaries == boundary_full,
            "manifest does not exactly preserve boundary records/default names")
    registry_by_index = {row["index"]: row for row in registry_rows}
    require(len(registry_by_index) == len(registry_rows) == 144,
            "shipped registry index census differs")
    for index, command, entry in manifest_join:
        registry = registry_by_index.get(index)
        require(registry is not None and registry["command"] == command and
                registry["handlerVa"].lower() == entry and
                registry["isFunctionEntry"] == "False" and
                registry["currentGhidraName"] == "",
                f"manifest differs from shipped registry at index {index}")
    require({row["grade"] for row in static_rows} == {"C1_CANDIDATE_PARTIAL"} and
            {row["evidenceClass"] for row in static_rows} ==
            {"STATIC_HYPOTHESIS_ONLY"},
            "new-34 static-contract evidence boundary differs")
    return {"rows": 34, "exactManifestJoin": True,
            "exactRegistryTripleJoin": True,
            "registryRowsWerePreBoundaryNonEntries": True,
            "exactBoundaryRecordAndDefaultNameJoin": True,
            "grade": "C1_CANDIDATE_PARTIAL",
            "evidenceClass": "STATIC_HYPOTHESIS_ONLY",
            "runtimeBehaviorAuthorized": False,
            "reconstructionParityAuthorized": False}


def project_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value.get(key) for key in
            ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")}


def plain_project(root: Path) -> dict[str, Any]:
    root = Path(os.path.abspath(root))
    require(root.is_dir(), f"project root is absent: {root}")
    files: list[dict[str, Any]] = []
    total = 0
    for path in [root, *root.rglob("*")]:
        stat = path.lstat()
        require(not path.is_symlink(), f"project contains symlink: {path}")
        require(not (getattr(stat, "st_file_attributes", 0) & 0x400),
                f"project contains reparse point: {path}")
        if not path.is_file() or path.name == "backup_manifest.json":
            continue
        relpath = path.relative_to(root).as_posix()
        if relpath != "BEA.gpr" and not relpath.startswith("BEA.rep/"):
            continue
        require(stat.st_nlink == 1, f"project contains linked file: {path}")
        files.append({"relative_path": relpath, "sha256": sha256_file(path),
                      "size": stat.st_size})
        total += stat.st_size
    files.sort(key=lambda row: row["relative_path"])
    return {"projectName": "BEA", "fileCount": len(files), "totalBytes": total,
            "structurallyComplete": any(row["relative_path"] == "BEA.gpr" for row in files)
            and any(row["relative_path"].startswith("BEA.rep/") for row in files),
            "files": files}


def validate_baseline_restore() -> dict[str, Any]:
    baseline = load_json(BASELINE / "backup_manifest.json")
    restore_path = LANE / "baseline-restore.ready.json"
    restore = load_json(restore_path)
    source = project_fields(baseline.get("destination", {}))
    require(baseline.get("schemaVersion") == "onslaught-ghidra-project-backup.v2" and
            baseline.get("sourceStable") is True and
            baseline.get("copyComparison", {}).get("matches") is True and
            source == project_fields(baseline.get("source", {})) == plain_project(BASELINE),
            "baseline backup is not a stable exact copy")
    require(restore.get("schemaVersion") == "onslaught-ghidra-project-backup.v2" and
            restore.get("sourceStable") is True and
            source == project_fields(restore.get("source", {})),
            "baseline restore project identity differs")
    require(restore.get("copyComparison", {}).get("matches") is True,
            "baseline restore comparison failed")
    readonly = restore.get("readonlyOpen", {})
    require(readonly.get("opened") is True and readonly.get("contentStable") is True and
            readonly.get("observedFunctionCount") == 8_394 and
            readonly.get("observedProgramMd5") == PROGRAM_MD5 and
            readonly.get("observedProgramSha256") == PROGRAM_SHA,
            "baseline restore read-only open differs")
    probe = Path(str(restore.get("probeCopy", ""))).resolve()
    try:
        probe.relative_to((LANE / "restore-probe").resolve())
    except ValueError as exc:
        raise AuthorityError("baseline restore probe escapes its lane") from exc
    require(plain_project(probe) == source,
            "retained baseline restore probe bytes differ")
    log_claim = readonly.get("probeLog", {})
    log = restore_path.with_name(str(log_claim.get("path", "")))
    actual_log = stamp(log)
    require((log_claim.get("bytes"), log_claim.get("sha256")) ==
            (actual_log["bytes"], actual_log["sha256"]),
            "baseline restore probe log differs")
    return {"baseline": stamp(BASELINE / "backup_manifest.json"),
            "restore": stamp(restore_path), "restoreLog": actual_log,
            "project": source, "retainedProbeByteIdentical": True,
            "readOnlyOpenVerified": True}


def validate_initial_copy(root: Path, expected: Mapping[str, Any] | None,
                          label: str) -> tuple[dict[str, Any], dict[str, Any]]:
    path = root / "backup_manifest.json"
    value = load_json(path)
    require(value.get("sourceStable") is True, f"{label} source was unstable")
    require(value.get("copyComparison", {}).get("matches") is True,
            f"{label} copy comparison failed")
    source = project_fields(value.get("source", {}))
    destination = project_fields(value.get("destination", {}))
    require(source == destination, f"{label} source/destination inventories differ")
    require(source.get("projectName") == "BEA" and source.get("fileCount") == 19 and
            source.get("totalBytes") == 186_747_781 and
            source.get("structurallyComplete") is True,
            f"{label} is not the exact synchronized PRE project")
    if expected is not None:
        require(source == expected, f"{label} initial PRE bytes differ from first replica")
    return source, stamp(path)


def validate_post_backup() -> dict[str, Any]:
    backup_path = LANE / "post-backup/backup_manifest.json"
    restore_path = LANE / "post-backup-restore.ready.json"
    backup = load_json(backup_path)
    require(backup.get("schemaVersion") == "onslaught-ghidra-project-backup.v2" and
            backup.get("sourceStable") is True and
            backup.get("copyComparison", {}).get("matches") is True,
            "POST backup is not a stable exact copy")
    project = project_fields(backup.get("destination", {}))
    require(project == project_fields(backup.get("source", {})) ==
            plain_project(LANE / "post-backup"),
            "POST backup bytes differ from its receipt")
    require(project.get("fileCount") == 19 and
            project.get("totalBytes") == 186_813_317,
            "POST backup project census differs")
    db = next((row for row in project["files"] if
               row["relative_path"].endswith("/db.18611.gbf")), None)
    require(db == {"relative_path": "BEA.rep/idata/00/~00000000.db/db.18611.gbf",
                   "sha256": "0885a97d2e3b43699efb9fba66088122b1d16b4f5045a28b40e0bb8a08fc895e",
                   "size": 68_288_512}, "POST backup db.18611 identity differs")

    restore = load_json(restore_path)
    require(restore.get("schemaVersion") == "onslaught-ghidra-project-backup.v2" and
            restore.get("sourceStable") is True and
            restore.get("copyComparison", {}).get("matches") is True and
            project_fields(restore.get("source", {})) == project,
            "POST restore copy differs")
    opened = restore.get("readonlyOpen", {})
    require(opened.get("opened") is True and opened.get("contentStable") is True and
            opened.get("exitCode") == 0 and
            opened.get("postOpenComparison", {}).get("matches") is True and
            opened.get("observedFunctionCount") == 8_394 and
            opened.get("observedProgramMd5") == PROGRAM_MD5 and
            opened.get("observedProgramSha256") == PROGRAM_SHA,
            "POST restore read-only open differs")
    probe = Path(str(restore.get("probeCopy", ""))).resolve()
    try:
        probe.relative_to((LANE / "post-restore-probe").resolve())
    except ValueError as exc:
        raise AuthorityError("POST restore probe escapes its lane") from exc
    require(plain_project(probe) == project,
            "retained POST restore probe bytes differ")
    log_claim = opened.get("probeLog", {})
    log = restore_path.with_name(str(log_claim.get("path", "")))
    actual_log = stamp(log)
    require((log_claim.get("bytes"), log_claim.get("sha256")) ==
            (actual_log["bytes"], actual_log["sha256"]),
            "POST restore probe log differs")
    return {"backup": stamp(backup_path), "restore": stamp(restore_path),
            "restoreLog": actual_log, "project": project,
            "retainedProbeByteIdentical": True, "readOnlyOpenVerified": True}


def validate_tool_receipt(run: str, mode: str, state: str) -> dict[str, Any]:
    directory = RUNS / run
    ready_path = directory / "vocabulary.ready.json"
    output_path = directory / "vocabulary.tsv"
    value = load_json(ready_path)
    parse_utc(value.get("completedAtUtc"), f"{run} completedAtUtc")
    require(value.get("schema") == TOOL_SCHEMA and value.get("mode") == mode and
            value.get("state") == state, f"{run} identity differs")
    program = value.get("program", {})
    require(program == {"name": "BEA.exe", "md5": PROGRAM_MD5,
                        "sha256": PROGRAM_SHA, "functions": PRE_FUNCTION_COUNT,
                        "instructions": INSTRUCTION_COUNT},
            f"{run} program identity differs")
    require(value.get("targets") == {"total": 34, "NEW34_STATIC_C1": 34},
            f"{run} target census differs")
    require(value.get("mutation") == {
        "namesChanged": 34, "commentsChanged": 34, "newFunctionComments": 34,
        "tagAssociationsAdded": 68, "tagAssociationsRemoved": 0,
        "tagDefinitionsAdded": 0,
        "boundariesChanged": 0, "abiChanged": 0, "bytesChanged": 0,
        "instructionsChanged": 0, "referencesChanged": 0,
    }, f"{run} mutation boundary differs")
    expected_catalog = POST_CATALOG if state == "POST" else PRE_CATALOG
    catalog = value.get("tagCatalog", {})
    require((catalog.get("count"), catalog.get("definitionsSha256"),
             catalog.get("usageSha256")) == expected_catalog,
            f"{run} tag catalog differs")
    for key, path in (("manifest", MANIFEST), ("preMetadata", METADATA),
                      ("staticContracts", STATIC_CONTRACT_ROWS),
                      ("owner", OWNER), ("tool", TOOL)):
        measured = value.get(key, {})
        expected = stamp(path)
        require_repo_path_claim(measured.get("path"), path, f"{run} {key}")
        require((measured.get("bytes"), measured.get("sha256")) ==
                (expected["bytes"], expected["sha256"]),
                f"{run} {key} identity differs")
    output = stamp(output_path)
    measured_output = value.get("output", {})
    require_repo_path_claim(measured_output.get("path"), output_path,
                            f"{run} output")
    require((measured_output.get("bytes"), measured_output.get("sha256")) ==
            (output["bytes"], output["sha256"]), f"{run} output stamp differs")
    require(value.get("commitRequested") is (mode == "apply"),
            f"{run} commit-request flag differs")
    require(value.get("nestedEndReturnedCommitted") is False,
            f"{run} nested transaction unexpectedly committed")
    require(value.get("loadedStateVerified") is (mode == "readback"),
            f"{run} loaded-state flag differs")
    require(value.get("registryNamesAreOriginalCppSymbols") is False and
            value.get("runtimeBehaviorAuthorized") is False and
            value.get("reconstructionParityAuthorized") is False and
            value.get("liveMutationAuthorized") is False,
            f"{run} claim boundary differs")
    rows = read_tsv(output_path)
    require(len(rows) == TARGET_COUNT, f"{run} output row count differs")
    by_address = {row["handlerVa"].lower(): row for row in rows}
    require(len(by_address) == TARGET_COUNT, f"{run} output handlers are not unique")
    manifest = load_manifest()
    metadata = load_metadata()
    require(by_address.keys() == manifest.keys(), f"{run} output handlers differ")
    for address, row in by_address.items():
        target = manifest[address]
        require(row["index"] == target["index"] and row["cohort"] == target["cohort"],
                f"{run} output target identity differs at {address}")
        expected_name = target["proposedName"] if state == "POST" else target["expectedPreName"]
        expected_source = "USER_DEFINED" if state == "POST" else target["expectedNameSource"]
        require(row["name"] == expected_name and row["nameSource"] == expected_source,
                f"{run} output name differs at {address}")
        expected_tags = post_tags(target, metadata[address], state == "POST")
        actual_tags = [] if not row["tags"] else row["tags"].split(",")
        require(actual_tags == expected_tags and
                int(row["tagCount"]) == len(expected_tags),
                f"{run} output tags differ at {address}")
        if state == "POST":
            expected_comment = post_comment(target)
            require(int(row["commentLen"]) == len(expected_comment) and
                    row["commentSha256"] == hashlib.sha256(
                        expected_comment.encode()).hexdigest(),
                    f"{run} bounded comment differs at {address}")
    require({row["mode"] for row in rows} == {mode} and
            {row["state"] for row in rows} == {state},
            f"{run} output mode/state differs")
    return {"ready": stamp(ready_path), "output": output, "rows": rows}


def validate_success_log(run: str, marker: str, inventory_expected: bool) -> dict[str, Any]:
    path = RUNS / run / "ghidra.log"
    text = path.read_text(encoding="utf-8", errors="strict")
    require(text.count(marker) == 1, f"{run} success marker count differs")
    require("REPORT SCRIPT ERROR" not in text, f"{run} contains a script error")
    require("GhidraApplyMissionRegistryNewFunctionVocabulary.java" in text,
            f"{run} mutator identity is absent from log")
    if inventory_expected:
        require("ExportFullFunctionInventory.java" in text,
                f"{run} inventory exporter identity is absent from log")
    return stamp(path)


def contract_rows() -> dict[str, dict[str, str]]:
    rows = read_tsv(STATIC_CONTRACT_ROWS)
    result = {row["entry"].lower(): row for row in rows}
    require(len(rows) == len(result) == TARGET_COUNT,
            "static-contract address set differs")
    return result


def post_comment(row: Mapping[str, str]) -> str:
    contract = contract_rows()[row["handlerVa"].lower()]
    return (
        f"Mission registry vocabulary: slot {row['index']} (record {row['registryRecordVa']}) "
        f"registers this handler as `{row['command']}`. The promoted `{row['proposedName']}` "
        "name is Tier 2 script-facing vocabulary under the project naming convention, not a "
        "recovered C++ symbol or evidence of this handler's ABI, runtime behavior, or complete "
        f"semantics.\n\nStatic envelope (`{contract['grade']}` / "
        f"`{contract['evidenceClass']}`; registry-label relation "
        f"`{contract['labelRelation']}`): {contract['staticContract']}\n\n"
        f"Visible failure/no-op boundary: {contract['visibleFailureOrNoOp']}\n\n"
        f"Remaining unknowns: {contract['remainingUnknown']}\n\n"
        f"Cheapest falsifier: {contract['cheapestFalsifier']} No runtime reachability, "
        "causal behavior, source equivalence, or reconstruction parity is admitted by this "
        "metadata promotion."
    )


def post_tags(row: Mapping[str, str], metadata: Mapping[str, str],
              post: bool = True) -> list[str]:
    result = set(metadata["preTags"].split(",")) if metadata["preTags"] else set()
    if not post:
        return sorted(result)
    result.update({"script-command-registry", "tier2-script-facing-name"})
    return sorted(result)


def inventory(path: Path) -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    rows = read_tsv(path)
    result = {row["address"].lower(): row for row in rows}
    require(len(rows) == len(result) == PRE_FUNCTION_COUNT,
            f"function inventory count differs: {path}")
    return result, stamp(path)


def program(path: Path) -> tuple[dict[str, str], dict[str, Any]]:
    rows = read_tsv(path)
    result = {row["metric"]: row["value"] for row in rows}
    require(len(rows) == len(result), f"program inventory has duplicate metrics: {path}")
    return result, stamp(path)


def compare_inventories(pre_path: Path, post_path: Path,
                        manifest: Mapping[str, Mapping[str, str]],
                        metadata: Mapping[str, Mapping[str, str]]) -> dict[str, Any]:
    pre, pre_stamp = inventory(pre_path)
    post, post_stamp = inventory(post_path)
    require(pre.keys() == post.keys(), "function address set differs")
    target_set = set(manifest)
    require(target_set <= pre.keys(), "manifest target is absent from PRE inventory")
    non_target_differences = []
    target_fields: set[str] = set()
    for address in sorted(pre):
        if address not in target_set:
            if pre[address] != post[address]:
                non_target_differences.append(address)
            continue
        before, after = pre[address], post[address]
        row, meta = manifest[address], metadata[address]
        changed = {key for key in before if before[key] != after[key]}
        require(changed <= ALLOWED_TARGET_FIELDS,
                f"forbidden target fields changed at {address}: {sorted(changed)}")
        require({"name", "signature", "commentSha256", "tags"} <= changed,
                f"required target metadata did not change at {address}: {sorted(changed)}")
        target_fields.update(changed)
        require(before["name"] == row["expectedPreName"] and
                before["nameSource"] == row["expectedNameSource"],
                f"PRE name identity differs at {address}")
        require(after["name"] == after["fqname"] == row["proposedName"] and
                after["nameSource"] == "USER_DEFINED", f"POST name differs at {address}")
        require(after["signature"] == before["signature"].replace(
            row["expectedPreName"], row["proposedName"], 1),
            f"rendered signature changed beyond the function name at {address}")
        require(before["commentPresent"].lower() == meta["preCommentPresent"] and
                before["commentLen"] == meta["preCommentLen"] and
                before["commentSha256"] == meta["preCommentSha256"],
                f"PRE comment metadata differs at {address}")
        expected_comment = post_comment(row)
        require(after["commentPresent"] == "true" and
                int(after["commentLen"]) == len(expected_comment) and
                after["commentSha256"] == hashlib.sha256(
                    expected_comment.encode()).hexdigest(),
                f"POST bounded comment length differs at {address}")
        expected_tags = post_tags(row, meta)
        require(before["tags"] == meta["preTags"] and
                before["tagCount"] == meta["preTagCount"] and
                before["tagsSha256"] == meta["preTagsSha256"],
                f"PRE tag metadata differs at {address}")
        require(after["tags"].split(",") == expected_tags and
                int(after["tagCount"]) == len(expected_tags),
                f"POST tag set differs at {address}")
    require(not non_target_differences,
            f"non-target inventory rows changed: {non_target_differences[:8]}")
    return {"pre": pre_stamp, "post": post_stamp, "targets": TARGET_COUNT,
            "nonTargetsByteIdentical": PRE_FUNCTION_COUNT - TARGET_COUNT,
            "changedTargetFields": sorted(target_fields)}


def compare_programs(pre_path: Path, post_path: Path) -> dict[str, Any]:
    before, pre_stamp = program(pre_path)
    after, post_stamp = program(post_path)
    require(before.keys() == after.keys(), "program metric keys differ")
    changed = {key for key in before if before[key] != after[key]}
    require(changed == {"symbolsUserDefined", "symbolsDefaultOther", "comments",
                        "commentsSha256"}, f"program collateral differs: {sorted(changed)}")
    require(int(after["symbolsUserDefined"]) - int(before["symbolsUserDefined"]) == 34,
            "user-defined symbol delta differs")
    require(int(before["symbolsDefaultOther"]) - int(after["symbolsDefaultOther"]) == 34,
            "default symbol delta differs")
    require(int(after["comments"]) - int(before["comments"]) == 34,
            "new function-comment delta differs")
    require(after["functions"] == str(PRE_FUNCTION_COUNT) and
            after["instructions"] == str(INSTRUCTION_COUNT),
            "program census differs")
    return {"pre": pre_stamp, "post": post_stamp,
            "changedMetrics": sorted(changed), "newUserSymbols": 34,
            "retiredDefaultSymbols": 34, "newComments": 34}


def compare_vocabulary(pre_rows: list[dict[str, str]],
                       post_rows: list[dict[str, str]], label: str) -> None:
    before = {row["handlerVa"].lower(): row for row in pre_rows}
    after = {row["handlerVa"].lower(): row for row in post_rows}
    require(before.keys() == after.keys() and len(before) == TARGET_COUNT,
            f"{label} vocabulary address set differs")
    stable = {"index", "handlerVa", "cohort", "invariantSha256", "abiSha256",
              "repeatableCommentSha256"}
    for address in before:
        require(all(before[address][key] == after[address][key] for key in stable),
                f"{label} invariant vocabulary field differs at {address}")


def crosscheck_vocabulary_inventory(rows: list[dict[str, str]], inventory_path: Path,
                                    label: str) -> None:
    functions, _ = inventory(inventory_path)
    for row in rows:
        address = row["handlerVa"].lower()
        function = functions[address]
        for output_key, inventory_key in (("name", "name"), ("nameSource", "nameSource"),
                                           ("commentLen", "commentLen"),
                                           ("commentSha256", "commentSha256"),
                                           ("repeatableCommentSha256",
                                            "repeatableCommentSha256"),
                                           ("tagCount", "tagCount"), ("tags", "tags")):
            require(row[output_key] == function[inventory_key],
                    f"{label} differs from full inventory at {address}: {output_key}")


def validate_probe_log(run: str, post_inner: bool) -> dict[str, Any]:
    path = RUNS / run / "ghidra.log"
    text = path.read_text(encoding="utf-8", errors="strict")
    require("REPORT SCRIPT ERROR" in text, f"{run} did not fail closed")
    if post_inner:
        for marker in ("COMPENSATING_PRE_RESTORE_COMPLETE",
                       "FORCED_POST_INNER_FAILURE nested_commit_requested=true pre_restored=true",
                       "outer_rollback_required=false recovery=COMPENSATING_PRE_RESTORE_VERIFIED"):
            require(marker in text, f"{run} missing marker: {marker}")
    else:
        for marker in ("FORCED_AFTER_ONE_FAILURE", "outer_rollback_required=true",
                       "recovery=SEPARATE_EXACT_PRE_READBACK_REQUIRED"):
            require(marker in text, f"{run} missing marker: {marker}")
    require(not (RUNS / run / "vocabulary.tsv").exists() and
            not (RUNS / run / "vocabulary.ready.json").exists(),
            f"{run} published success artifacts")
    return stamp(path)


def validate_external_path_controls(expected_project: Mapping[str, Any]) -> dict[str, Any]:
    external_output = EXTERNAL_PROBE_ROOT / "external-output.tsv"
    external_ready = EXTERNAL_PROBE_ROOT / "external-ready.json"
    require(EXTERNAL_PROBE_ROOT.is_dir(), "external-path probe directory is absent")
    require(not external_output.exists() and not external_ready.exists(),
            "external-path probe published an external artifact")

    controls: dict[str, Any] = {}
    cases = {
        "externalOutput": ("probe-external-output", (
            RUNS / "probe-external-output/vocabulary.ready.json",
        )),
        "externalReady": ("probe-external-ready", (
            RUNS / "probe-external-ready/vocabulary.tsv",
        )),
    }
    for label, (name, internal_artifacts) in cases.items():
        log = RUNS / name / "ghidra.log"
        text = log.read_text(encoding="utf-8", errors="replace")
        require("REPORT: Processing project file: /BEA.exe" in text and
                "REPORT SCRIPT ERROR" in text and
                "path is outside supplied repository root" in text,
                f"{name} did not exercise external-path rejection")
        require("MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_PREFLIGHT_OK" not in text and
                "MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_MUTATION_TAINTED" not in text and
                "MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_APPLY_COMPLETE" not in text,
                f"{name} crossed the PRE-validation/transaction boundary")
        require(all(not path.exists() for path in internal_artifacts),
                f"{name} published an internal success artifact")
        controls[label] = {"log": stamp(log), "publishedArtifacts": 0,
                           "rejectedBeforePreValidation": True,
                           "rejectedBeforeTransaction": True}

    readback = validate_tool_receipt("probe-external-readback", "dry", "PRE")
    functions = RUNS / "probe-external-readback/functions.tsv"
    program_path = functions.with_name("program.tsv")
    readback_log = validate_success_log(
        "probe-external-readback",
        "MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_DRY_COMPLETE", True)
    require((functions.stat().st_size, sha256_file(functions)) == STAMPS[PRE_FUNCTIONS] and
            (program_path.stat().st_size, sha256_file(program_path)) == STAMPS[PRE_PROGRAM],
            "external-path controls did not preserve exact PRE inventory")
    return {
        "copyManifest": validate_initial_copy(
            SCRATCH / "probe-external", expected_project, "external-path probe copy")[1],
        "controls": controls,
        "separatePreReadback": {k: v for k, v in readback.items() if k != "rows"},
        "readbackLog": readback_log,
        "functions": stamp(functions), "program": stamp(program_path),
        "exactPreInventoryRestored": True,
    }


def validate_all() -> dict[str, Any]:
    inputs = {relative(path): require_stamp(path) for path in STAMPS}
    manifest = load_manifest()
    metadata = load_metadata()
    require(manifest.keys() == metadata.keys(), "manifest/PRE metadata addresses differ")
    static_join = validate_static_contract_join(manifest)

    restore = validate_baseline_restore()
    project: dict[str, Any] | None = restore["project"]
    projects = {}
    for name in ("replica-a", "replica-b", "probe-after-one", "probe-post-inner"):
        project, receipt = validate_initial_copy(SCRATCH / name, project, name)
        projects[name] = receipt

    external_controls = validate_external_path_controls(project)

    positive = {}
    for replica in ("replica-a", "replica-b"):
        dry = validate_tool_receipt(f"{replica}-dry", "dry", "PRE")
        apply = validate_tool_receipt(f"{replica}-apply", "apply", "POST")
        readback = validate_tool_receipt(f"{replica}-readback", "readback", "POST")
        dry_log = validate_success_log(
            f"{replica}-dry",
            "MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_DRY_COMPLETE", False)
        apply_log = validate_success_log(
            f"{replica}-apply",
            "MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_APPLY_COMPLETE", False)
        readback_log = validate_success_log(
            f"{replica}-readback",
            "MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_READBACK_COMPLETE", True)
        compare_vocabulary(dry["rows"], apply["rows"], replica + " apply")
        compare_vocabulary(dry["rows"], readback["rows"], replica + " readback")
        crosscheck_vocabulary_inventory(dry["rows"], PRE_FUNCTIONS, replica + " dry")
        post_functions = RUNS / f"{replica}-readback/functions.tsv"
        crosscheck_vocabulary_inventory(apply["rows"], post_functions,
                                        replica + " apply")
        crosscheck_vocabulary_inventory(readback["rows"], post_functions,
                                        replica + " readback")
        positive[replica] = {"dry": {k: v for k, v in dry.items() if k != "rows"},
                             "apply": {k: v for k, v in apply.items() if k != "rows"},
                             "readback": {k: v for k, v in readback.items() if k != "rows"},
                             "logs": {"dry": dry_log, "apply": apply_log,
                                      "readback": readback_log}}

    a_functions = RUNS / "replica-a-readback/functions.tsv"
    b_functions = RUNS / "replica-b-readback/functions.tsv"
    a_program = a_functions.with_name("program.tsv")
    b_program = b_functions.with_name("program.tsv")
    require(a_functions.read_bytes() == b_functions.read_bytes(),
            "positive replica function inventories differ")
    require(a_program.read_bytes() == b_program.read_bytes(),
            "positive replica program inventories differ")
    function_delta = compare_inventories(PRE_FUNCTIONS, a_functions, manifest, metadata)
    program_delta = compare_programs(PRE_PROGRAM, a_program)
    post_backup = validate_post_backup()

    probes = {}
    for name, post_inner in (("probe-after-one", False), ("probe-post-inner", True)):
        log = validate_probe_log(name, post_inner)
        readback = validate_tool_receipt(name + "-readback", "dry", "PRE")
        functions = RUNS / (name + "-readback/functions.tsv")
        program_path = functions.with_name("program.tsv")
        readback_log = validate_success_log(
            name + "-readback",
            "MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_DRY_COMPLETE", True)
        crosscheck_vocabulary_inventory(readback["rows"], functions,
                                        name + " restored PRE readback")
        require((functions.stat().st_size, sha256_file(functions)) == STAMPS[PRE_FUNCTIONS],
                f"{name} function PRE was not restored exactly")
        require((program_path.stat().st_size, sha256_file(program_path)) == STAMPS[PRE_PROGRAM],
                f"{name} program PRE was not restored exactly")
        probes[name] = {"adverseLog": log,
                        "readbackLog": readback_log,
                        "readback": {k: v for k, v in readback.items() if k != "rows"},
                        "functions": stamp(functions), "program": stamp(program_path)}

    return {
        "inputs": inputs,
        "canonicalProjection": {"bytes": 1_684, "sha256": CANONICAL_SHA},
        "new34StaticContractJoin": static_join,
        "baselineRestore": restore,
        "initialScratchCopies": projects,
        "positiveReplicas": positive,
        "postFunctionsReplicasByteIdentical": True,
        "postProgramReplicasByteIdentical": True,
        "functionCollateral": function_delta,
        "programCollateral": program_delta,
        "postBackupRestore": post_backup,
        "preTransactionPathControls": external_controls,
        "adverseControls": probes,
    }


def atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    require(not path.exists(), f"receipt already exists: {path}")
    handle, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def seal() -> None:
    evidence = validate_all()
    value = {
        "schema": SCHEMA,
        "completedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authorityTool": stamp(SCRIPT),
        "verdict": "SCRATCH_AUTHORITY_READY_LIVE_FORBIDDEN",
        "evidence": evidence,
        "liveGhidraMutated": False,
        "trackedGhidraMutated": False,
        "liveMutationAuthorized": False,
        "nextRequiredPhase": "independent integration review before any live ceremony",
    }
    atomic_json(READY, value)
    print(f"SCRATCH_AUTHORITY_READY targets=34 receipt={relative(READY)} "
          f"sha256={sha256_file(READY)}")


def verify() -> None:
    value = load_json(READY)
    require(value.get("schema") == SCHEMA, "authority receipt schema differs")
    parse_utc(value.get("completedAtUtc"), "authority completedAtUtc")
    tool = stamp(SCRIPT)
    measured = value.get("authorityTool", {})
    require((measured.get("bytes"), measured.get("sha256")) ==
            (tool["bytes"], tool["sha256"]), "authority tool identity differs")
    require(value.get("verdict") == "SCRATCH_AUTHORITY_READY_LIVE_FORBIDDEN" and
            value.get("liveGhidraMutated") is False and
            value.get("trackedGhidraMutated") is False and
            value.get("liveMutationAuthorized") is False,
            "authority receipt claim boundary differs")
    require(value.get("evidence") == validate_all(), "authority evidence no longer reproduces")
    print(f"SCRATCH_AUTHORITY_VERIFIED targets=34 receipt_sha256={sha256_file(READY)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("seal", "verify"))
    args = parser.parse_args()
    if args.command == "seal":
        seal()
    else:
        verify()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuthorityError as exc:
        print(f"AUTHORITY_REJECTED: {exc}")
        raise SystemExit(1)
