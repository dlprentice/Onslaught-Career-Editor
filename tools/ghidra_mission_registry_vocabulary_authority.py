#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal the 75-row Mission-registry vocabulary scratch ceremony.

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
LANE = REPO / "local-lab/ghidra-mission-registry-vocabulary-20260813-v1"
FORMAL = LANE / "formal"
RUNS = FORMAL / "runs"
SCRATCH = FORMAL / "scratch"
PRE_FUNCTIONS = FORMAL / "pre/functions.tsv"
PRE_PROGRAM = FORMAL / "pre/program.tsv"
READY = FORMAL / "scratch-authority.ready.json"

MANIFEST = REPO / (
    "reverse-engineering/binary-analysis/"
    "mission-script-registry-vocabulary-normalization-2026-08-13.tsv"
)
METADATA = REPO / (
    "reverse-engineering/binary-analysis/"
    "mission-script-registry-vocabulary-normalization-pre-metadata-2026-08-13.tsv"
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
TOOL = REPO / "tools/GhidraApplyMissionRegistryVocabulary.java"
INVENTORY_TOOL = REPO / "tools/ExportFullFunctionInventory.java"

SCHEMA = "bea.ghidra.mission-registry-vocabulary-authority.v1"
TOOL_SCHEMA = "bea.ghidra.mission-registry-vocabulary.v1"
PROGRAM_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
CANONICAL_SHA = "39a9f2f01eb82c9f1924f716cb621dd9d9f680f7c584315e770f7731a0da9992"
PRE_FUNCTION_COUNT = 8_170
INSTRUCTION_COUNT = 549_872
TARGET_COUNT = 75
EMPTY_TAGS_SENTINEL = "<EMPTY>"
PRE_CATALOG = (6_853,
               "351e7234d66db90af13a4f4ecfd3df9e1ed7f6db6b9828f97f0758f8cdeef811",
               "bc7a8ba82155bb7a8f33fbb4ec2ebc15684dffa11b75b212338baf3eca06efd9")
POST_CATALOG = (6_854,
                "074dd7480aebfe46aabe5a48c1429348a814c9b51b0d71d985cbdac6e764603f",
                "a23aa97dca8f2f36646abc90a12363581a4d87610cc897b4c5558a8044bbcd78")

STAMPS = {
    MANIFEST: (7_299, "a30897bbb1c842fa046af62f3dc1f91b7888af162963d01422074f083c513145"),
    METADATA: (22_628, "cc7cc62d64bcd62f6024f2b4ccc66c369426853c638ba90a773d537fd269470b"),
    OWNER: (11_148, "ac26beab94426fff3d30a04490200ce41e125787d5f5ad0784ee37dfd0114e01"),
    REGISTRY: (6_924, "61a44b1a393251bfd32c28a037648968575bfbd55afc1cba8e39bd269a5e1fdd"),
    REGISTRY_REPORT: (22_011, "24592057078f6658889860527ee64a8f4a3fb9bcfff5f98171725c8400d98c46"),
    NAMING: (4_255, "2ed51bc92a265043194426976df8138c009b64058581475de62f398e50ed4381"),
    PROJECTION: (502_664, "19312b424e357ea8a95102927d6464c874c491bdfcb28de82b1175e352fbb5bf"),
    BOUNDARY_REPORT: (4_433, "6753b80ad39c3e535ebbb8985e69f2bcf9282092ac16d27429d32c2f2e53a248"),
    STATIC_CONTRACT_OWNER: (9_113, "c8b599b7cce79beba453a39d78523b616bcf83f45403423872f533086ed761b7"),
    STATIC_CONTRACT_ROWS: (21_608, "86c0c4a0e0d5fe0078cb21f271b4985cb1c4fe89aa035b66215076dfbe784a31"),
    TOOL: (52_561, "bcb34399d628b5c23cee88f96bcf056b530804e93d91288eb4984a514ed066ff"),
    INVENTORY_TOOL: (23_963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"),
    PRE_FUNCTIONS: (7_082_637, "8aa8b4468f463053d25084de86bec2a701ed1064c13f77fd47d16f9dda6cf259"),
    PRE_PROGRAM: (1_267, "cb4c2194e30e074e443779d9b42587072568f104fc76f671d40757af7b106075"),
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
    require(counts == {"DEFAULT54": 54, "MSG5": 5, "CLASS3_16": 16},
            f"cohort partition differs: {counts}")
    payload = ("\n".join(canonical) + "\n").encode()
    require(len(payload) == 4_035 and hashlib.sha256(payload).hexdigest() == CANONICAL_SHA,
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


def validate_static_contract_exclusion(
        manifest: Mapping[str, Mapping[str, str]]) -> dict[str, Any]:
    static_rows = read_tsv(STATIC_CONTRACT_ROWS)
    boundary_rows = read_tsv(REPO / (
        "reverse-engineering/binary-analysis/"
        "mission-script-registry-missing-function-boundaries-2026-08-13.tsv"))
    require(len(static_rows) == len(boundary_rows) == 34,
            "new-boundary static-contract census differs")
    static_join = {(row["registryIndex"], row["command"], row["entry"].lower())
                   for row in static_rows}
    boundary_join = {(row["registryIndex"], row["command"], row["entry"].lower())
                     for row in boundary_rows}
    require(len(static_join) == 34 and static_join == boundary_join,
            "new-boundary static contracts do not join exactly to boundary rows")
    static_addresses = {row["entry"].lower() for row in static_rows}
    require(static_addresses.isdisjoint(manifest),
            "75-row normalization overlaps the separately owned new-34 cohort")
    require({row["grade"] for row in static_rows} == {"C1_CANDIDATE_PARTIAL"} and
            {row["evidenceClass"] for row in static_rows} ==
            {"STATIC_HYPOTHESIS_ONLY"},
            "new-34 static-contract evidence boundary differs")
    return {"rows": 34, "overlapWithNormalization": 0,
            "grade": "C1_CANDIDATE_PARTIAL",
            "evidenceClass": "STATIC_HYPOTHESIS_ONLY",
            "metadataMutationAuthorized": False}


def project_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value.get(key) for key in
            ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")}


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
            source.get("totalBytes") == 186_551_173 and
            source.get("structurallyComplete") is True,
            f"{label} is not the exact synchronized PRE project")
    if expected is not None:
        require(source == expected, f"{label} initial PRE bytes differ from first replica")
    return source, stamp(path)


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
    require(value.get("targets") == {"total": 75, "DEFAULT54": 54,
                                      "MSG5": 5, "CLASS3_16": 16},
            f"{run} target census differs")
    require(value.get("mutation") == {
        "namesChanged": 75, "commentsChanged": 75, "newFunctionComments": 54,
        "tagAssociationsAdded": 130, "tagAssociationsRemoved": 3,
        "tagDefinitionsAdded": 1,
        "boundariesChanged": 0, "abiChanged": 0, "bytesChanged": 0,
        "instructionsChanged": 0, "referencesChanged": 0,
    }, f"{run} mutation boundary differs")
    expected_catalog = POST_CATALOG if state == "POST" else PRE_CATALOG
    catalog = value.get("tagCatalog", {})
    require((catalog.get("count"), catalog.get("definitionsSha256"),
             catalog.get("usageSha256")) == expected_catalog,
            f"{run} tag catalog differs")
    for key, path in (("manifest", MANIFEST), ("preMetadata", METADATA),
                      ("owner", OWNER), ("tool", TOOL)):
        measured = value.get(key, {})
        expected = stamp(path)
        require((measured.get("bytes"), measured.get("sha256")) ==
                (expected["bytes"], expected["sha256"]),
                f"{run} {key} identity differs")
    output = stamp(output_path)
    measured_output = value.get("output", {})
    require((measured_output.get("bytes"), measured_output.get("sha256")) ==
            (output["bytes"], output["sha256"]), f"{run} output stamp differs")
    require(value.get("commitRequested") is (mode == "apply"),
            f"{run} commit-request flag differs")
    require(value.get("nestedEndReturnedCommitted") is False,
            f"{run} nested transaction unexpectedly committed")
    require(value.get("loadedStateVerified") is (mode == "readback"),
            f"{run} loaded-state flag differs")
    require(value.get("registryNamesAreOriginalCppSymbols") is False and
            value.get("behaviorContractsAuthorized") is False and
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
        if state == "POST" and target["cohort"] == "MSG5":
            expected_comment = message_comment(target)
            require(int(row["commentLen"]) == len(expected_comment) and
                    row["commentSha256"] == hashlib.sha256(
                        expected_comment.encode()).hexdigest(),
                    f"{run} MSG5 replacement comment differs at {address}")
    require({row["mode"] for row in rows} == {mode} and
            {row["state"] for row in rows} == {state},
            f"{run} output mode/state differs")
    return {"ready": stamp(ready_path), "output": output, "rows": rows}


def validate_success_log(run: str, marker: str, inventory_expected: bool) -> dict[str, Any]:
    path = RUNS / run / "ghidra.log"
    text = path.read_text(encoding="utf-8", errors="strict")
    require(text.count(marker) == 1, f"{run} success marker count differs")
    require("REPORT SCRIPT ERROR" not in text, f"{run} contains a script error")
    require("GhidraApplyMissionRegistryVocabulary.java" in text,
            f"{run} mutator identity is absent from log")
    if inventory_expected:
        require("ExportFullFunctionInventory.java" in text,
                f"{run} inventory exporter identity is absent from log")
    return stamp(path)


def suffix(row: Mapping[str, str]) -> str:
    common = (
        f"Mission registry vocabulary: slot {row['index']} (record {row['registryRecordVa']}) "
        f"registers this handler as `{row['command']}`. The promoted `{row['proposedName']}` "
        "name is Tier 2 script-facing vocabulary under the project naming convention, not a "
        "recovered C++ symbol and not evidence of this handler's signature, arguments, side "
        "effects, failure behavior, or complete semantics."
    )
    if row["cohort"] == "DEFAULT54":
        extra = ("This function had only a default `FUN_*` label before this metadata "
                 "promotion; no behavior claim is added.")
    elif row["cohort"] == "CLASS3_16":
        extra = (f"The prior label `{row['expectedPreName']}` was a Tier 3 mechanism-facing "
                 "description. Its bounded body/callee observations remain in the pre-existing "
                 "comment and tags where present; this vocabulary rename neither refutes those "
                 "observations nor upgrades them into a behavior contract.")
    else:
        raise AuthorityError(
            f"suffix append is forbidden for MSG5: {row['handlerVa']}")
    return common + "\n\n" + extra


def message_comment(row: Mapping[str, str]) -> str:
    require(row["cohort"] == "MSG5",
            f"message comment requested outside MSG5: {row['handlerVa']}")
    common = (
        f"Mission registry vocabulary: slot {row['index']} (record {row['registryRecordVa']}) "
        f"registers this handler as `{row['command']}`. The promoted `{row['proposedName']}` "
        "name is Tier 2 script-facing vocabulary under the project naming convention, not a "
        "recovered C++ symbol and not evidence of this handler's signature, arguments, side "
        "effects, failure behavior, or complete semantics."
    )
    measured = (
        "Measured row-specific facts: this native obtains localized text, constructs a "
        "seven-argument `CMessage__ctor_base`, and submits the message through "
        "`CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`; queued advancement can reach "
        "`CMessageBox__StartVoiceOrFallbackTextReveal`. "
    )
    facts = {
        "17": ("Constructor argument 1 is fixed global `0x0089C328`; argument 5 is a register "
               "in the optional-audio-reader slot; argument 6 is a register; argument 7 is "
               "literal `0xA`. Argument 1 is the measured `AddMessage` distinction from the "
               "four `*CharMessage*` forms."),
        "28": ("Constructor argument 5 is a register in the optional-audio-reader slot; "
               "argument 6 is literal `0`; argument 7 is literal `0xA`. The measured body/call "
               "layer registers no callback, so the prior callback claim and tag are withdrawn."),
        "36": ("Constructor argument 5 is a register in the optional-audio-reader slot; "
               "argument 6 is a register; argument 7 is literal `0xA`. This body also calls "
               "`CEventManager__GetNextFreeEvent` and `CScheduledEvent__Set`, which establishes "
               "the `Wait` scheduling axis at this layer, not fade; the prior fade claim and "
               "tag are withdrawn."),
        "90": ("Constructor argument 5 is a register in the optional-audio-reader slot; "
               "argument 6 is literal `0`; argument 7 is caller-varied. Argument 7 is the "
               "measured `P` axis; priority remains a plausible mechanism reading, not a "
               "recovered field meaning, so `priority-message` is retained only at that bounded "
               "confidence."),
        "91": ("Constructor arguments 5, 6, and 7 are registers. This body also calls "
               "`CEventManager__GetNextFreeEvent` and `CScheduledEvent__Set`. Argument 6 plus "
               "scheduling establishes the `Wait` axis, while argument 7 is the measured `P` "
               "axis; the fade claim and tag are withdrawn, while `priority-message` and "
               "`scheduled-event-7d1` remain at their bounded structural confidence."),
    }
    require(row["index"] in facts, f"unreviewed MSG5 index: {row['index']}")
    return (common + "\n\n" + measured + facts[row["index"]] + " Complete behavior, "
            "unresolved constructor slots and field meanings, failure paths, and original C++ "
            "identity remain open.")


def post_tags(row: Mapping[str, str], metadata: Mapping[str, str],
              post: bool = True) -> list[str]:
    result = set(metadata["preTags"].split(",")) if metadata["preTags"] else set()
    if not post:
        return sorted(result)
    if row["index"] == "28":
        result.discard("callback-message")
    if row["index"] in {"36", "91"}:
        result.discard("fade-event")
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
        expected_comment = message_comment(row) if row["cohort"] == "MSG5" else None
        expected_comment_len = (len(expected_comment) if expected_comment is not None else
                                int(meta["preCommentLen"]) + len(suffix(row)) +
                                (2 if meta["preCommentPresent"] == "true" else 0))
        require(after["commentPresent"] == "true" and
                int(after["commentLen"]) == expected_comment_len,
                f"POST bounded comment length differs at {address}")
        if expected_comment is not None:
            require(after["commentSha256"] == hashlib.sha256(
                expected_comment.encode()).hexdigest(),
                f"POST MSG5 replacement comment SHA differs at {address}")
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
    require(int(after["symbolsUserDefined"]) - int(before["symbolsUserDefined"]) == 54,
            "user-defined symbol delta differs")
    require(int(before["symbolsDefaultOther"]) - int(after["symbolsDefaultOther"]) == 54,
            "default symbol delta differs")
    require(int(after["comments"]) - int(before["comments"]) == 54,
            "new function-comment delta differs")
    require(after["functions"] == str(PRE_FUNCTION_COUNT) and
            after["instructions"] == str(INSTRUCTION_COUNT),
            "program census differs")
    return {"pre": pre_stamp, "post": post_stamp,
            "changedMetrics": sorted(changed), "newUserSymbols": 54,
            "retiredDefaultSymbols": 54, "newComments": 54}


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


def validate_all() -> dict[str, Any]:
    inputs = {relative(path): require_stamp(path) for path in STAMPS}
    manifest = load_manifest()
    metadata = load_metadata()
    require(manifest.keys() == metadata.keys(), "manifest/PRE metadata addresses differ")
    static_exclusion = validate_static_contract_exclusion(manifest)

    project: dict[str, Any] | None = None
    projects = {}
    for name in ("replica-a", "replica-b", "probe-after-one", "probe-post-inner"):
        project, receipt = validate_initial_copy(SCRATCH / name, project, name)
        projects[name] = receipt

    positive = {}
    for replica in ("replica-a", "replica-b"):
        dry = validate_tool_receipt(f"{replica}-dry", "dry", "PRE")
        apply = validate_tool_receipt(f"{replica}-apply", "apply", "POST")
        readback = validate_tool_receipt(f"{replica}-readback", "readback", "POST")
        dry_log = validate_success_log(
            f"{replica}-dry", "MISSION_REGISTRY_VOCABULARY_DRY_COMPLETE", False)
        apply_log = validate_success_log(
            f"{replica}-apply", "MISSION_REGISTRY_VOCABULARY_APPLY_COMPLETE", False)
        readback_log = validate_success_log(
            f"{replica}-readback", "MISSION_REGISTRY_VOCABULARY_READBACK_COMPLETE", True)
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

    probes = {}
    for name, post_inner in (("probe-after-one", False), ("probe-post-inner", True)):
        log = validate_probe_log(name, post_inner)
        readback = validate_tool_receipt(name + "-readback", "dry", "PRE")
        functions = RUNS / (name + "-readback/functions.tsv")
        program_path = functions.with_name("program.tsv")
        readback_log = validate_success_log(
            name + "-readback", "MISSION_REGISTRY_VOCABULARY_DRY_COMPLETE", True)
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
        "canonicalProjection": {"bytes": 4_035, "sha256": CANONICAL_SHA},
        "new34StaticContractExclusion": static_exclusion,
        "initialScratchCopies": projects,
        "positiveReplicas": positive,
        "postFunctionsReplicasByteIdentical": True,
        "postProgramReplicasByteIdentical": True,
        "functionCollateral": function_delta,
        "programCollateral": program_delta,
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
    print(f"SCRATCH_AUTHORITY_READY targets=75 receipt={relative(READY)} "
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
    print(f"SCRATCH_AUTHORITY_VERIFIED targets=75 receipt_sha256={sha256_file(READY)}")


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
