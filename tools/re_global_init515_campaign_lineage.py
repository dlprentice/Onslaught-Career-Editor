#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Freeze the exact generation-5 TEXT_RESIDUAL -> CODE lineage for the 515 cohort."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
from typing import Iterable, Mapping, Sequence


SCHEMA = "bea.re.global-init515-campaign-lineage.v1"
STATUS = "READY"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
FORMAL_READY_SHA256 = "0fa28300606f55d96e9e4c4168501c39d8eee25823033042d89339ae58d40729"
CAMPAIGN_READY_SHA256 = "5bddceb51c131d9c3a1ac634fd0672d0e9999b7ccab3f65dd2b33b4a68947cde"
ADMISSIBLE_SHA256 = "d9b919ee08d9d8becaa10ce2e248c604730fc7cbb97989da1e8e4d632d4e1abd"
QUARANTINE_SHA256 = "8128ffc1244cc2f0a8fcb15261359006a505b71c8fca9e9d910139c9669bea17"
POST_FUNCTIONS_SHA256 = "2e25b287ad5521780286f6b30e92172c84ab4f1e92ac933581593cc0f6cfc542"
TARGET_SET_SHA256 = "73bb797ee4d76da87c348b2908ac684cf06f7fcc4eecae9b9a67985bb5f2d6f9"
EXPECTED_LINEAGE_BYTES = 291_324
EXPECTED_LINEAGE_SHA256 = "bd66c5f88f5b4d93c95a5e57f97fb0159ebf4ceef969e5809d5fd0e95c773bf1"

FORMAL_SOURCE_NAMES = {
    "inputs/formal-proof.ready.json": "proof.ready.json",
    "inputs/admissible515.tsv": "inputs/admissible515.tsv",
    "inputs/listing-quarantine5.tsv": "inputs/listing-quarantine5.tsv",
    "inputs/post-functions.tsv": "runs/replica-a-apply-reopened/functions.tsv",
}
CAMPAIGN_FILES = (
    "campaign.ready.json",
    "campaign-functions.tsv",
    "campaign-residuals.tsv",
    "campaign-questions.tsv",
    "campaign-scenarios.tsv",
    "campaign-levers.tsv",
    "campaign-contracts.tsv",
    "campaign-adjudications.tsv",
    "campaign-supersessions.tsv",
)
CAMPAIGN_SOURCE_NAMES = {f"inputs/generation5-{name}": name for name in CAMPAIGN_FILES}
NATIVE_INPUT_NAME = "inputs/generation5-native-handlers.tsv"
INPUT_NAMES = tuple((*FORMAL_SOURCE_NAMES, *CAMPAIGN_SOURCE_NAMES, NATIVE_INPUT_NAME))
OUTPUT_NAMES = ("lineage-owner.py", "lineage515.tsv")
LINEAGE_COLUMNS = (
    "entry",
    "expectedRanges",
    "expectedBodyBytes",
    "expectedRangeDigest",
    "expectedBodyRangeSetSha256",
    "expectedInstructionCount",
    "oldResidualEntityKey",
    "oldQuestionId",
    "oldContractId",
    "expectedNewEntityKey",
    "expectedNewName",
    "expectedNewNameClass",
    "expectedNewQuestionType",
    "expectedNewQuestionId",
    "expectedNewContractId",
    "expectedSupersessionId",
)
CLAIM_BOUNDARY = (
    "This lineage binds 515 complete generation-5 TEXT_RESIDUAL entities to the exact functions created by the formal scratch proof; it authorizes boundary supersession only.",
    "Every old residual, question, and C0 contract remains open and UNSCORED before promotion; no semantic name, ABI, behavior, return, side effect, failure mode, or rebuild readiness is inferred.",
    "The five listing-repair quarantines are exact and disjoint and cannot enter by count-preserving substitution.",
    "A post-live campaign may consume this mapping only after a fresh coverage reseed proves each old residual disappeared and each exact new CODE entity appeared; the mapping itself does not authorize a live Ghidra write.",
)


class LineageError(ValueError):
    """A frozen lineage boundary failed closed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LineageError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def render_tsv(columns: Sequence[str], rows: Iterable[Mapping[str, object]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(columns), delimiter="\t", lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    for row in rows:
        require(set(row) == set(columns), "lineage TSV columns differ")
        values = {column: str(row[column]) for column in columns}
        require(not any(any(char in value for char in "\t\r\n") for value in values.values()), "lineage TSV cell contains framing characters")
        writer.writerow(values)
    return output.getvalue().encode("utf-8")


def parse_tsv(data: bytes, label: str) -> list[dict[str, str]]:
    try:
        lines = [line for line in data.decode("utf-8").splitlines() if line and not line.startswith("#")]
    except UnicodeError as exc:
        raise LineageError(f"{label} is not UTF-8: {exc}") from exc
    require(lines, f"{label} has no TSV rows")
    reader = csv.DictReader(lines, delimiter="\t")
    require(reader.fieldnames is not None and len(reader.fieldnames) == len(set(reader.fieldnames)), f"{label} header differs")
    rows = list(reader)
    require(all(None not in row for row in rows), f"{label} has malformed rows")
    return rows


def is_linklike(path: Path) -> bool:
    if path.is_symlink():
        return True
    junction = getattr(path, "is_junction", None)
    if junction is not None and junction():
        return True
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def stamp_bytes(name: str, data: bytes) -> dict[str, object]:
    return {"path": name, "bytes": len(data), "sha256": sha256_bytes(data)}


def parse_json(data: bytes, label: str) -> dict:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise LineageError(f"{label} is invalid JSON: {exc}") from exc
    require(isinstance(value, dict), f"{label} root is not an object")
    return value


def unique_map(rows: Sequence[Mapping[str, str]], key: str, label: str) -> dict[str, Mapping[str, str]]:
    result = {}
    for row in rows:
        value = row.get(key, "")
        require(value and value not in result, f"{label} has missing or duplicate {key}")
        result[value] = row
    return result


def canonical_range_set_sha256(start_va: int, end_va: int) -> str:
    ranges = [(start_va - 0x00400000, end_va - 0x00400000)]
    payload = json.dumps(ranges, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def function_name_class(name: str) -> str:
    if name.startswith("FUN_"):
        return "FUN"
    if name.startswith("VFuncSlot_"):
        return "VFUNC_SLOT"
    if name.startswith("thunk_") or name.startswith("_thunk"):
        return "THUNK"
    if name.startswith("SharedVFunc__"):
        return "SHARED_STUB"
    if len(name) >= 9 and name[-9] == "_" and all(char in "0123456789abcdefABCDEF" for char in name[-8:]):
        return "ADDR_SUFFIXED"
    return "NAMED"


def validate_input_receipts(inputs: Mapping[str, bytes]) -> tuple[dict, dict]:
    require(set(inputs) == set(INPUT_NAMES), "frozen input names differ")
    require(sha256_bytes(inputs["inputs/formal-proof.ready.json"]) == FORMAL_READY_SHA256, "formal proof READY differs")
    require(sha256_bytes(inputs["inputs/admissible515.tsv"]) == ADMISSIBLE_SHA256, "admissible515 input differs")
    require(sha256_bytes(inputs["inputs/listing-quarantine5.tsv"]) == QUARANTINE_SHA256, "quarantine input differs")
    require(sha256_bytes(inputs["inputs/post-functions.tsv"]) == POST_FUNCTIONS_SHA256, "formal post-functions input differs")
    require(sha256_bytes(inputs["inputs/generation5-campaign.ready.json"]) == CAMPAIGN_READY_SHA256, "generation-5 READY differs")
    formal = parse_json(inputs["inputs/formal-proof.ready.json"], "formal proof READY")
    campaign = parse_json(inputs["inputs/generation5-campaign.ready.json"], "generation-5 READY")
    require(formal.get("schema") == "bea.re.ghidra-global-init-admissible515-proof.v1" and formal.get("verdict") == "SURVIVED", "formal proof verdict/schema differs")
    require(campaign.get("schema") == "bea.re.campaign.v5" and campaign.get("counts") == {
        "functions": 7595,
        "residuals": 6618,
        "questions": 15222,
        "scenarios": 72,
        "levers": 913,
        "contracts": 14213,
        "adjudications": 2,
        "supersessions": 40,
    }, "generation-5 schema/counts differ")
    formal_artifacts = {item.get("path"): item for item in formal.get("artifacts", {}).get("items", [])}
    for source, expected_hash in (
        ("inputs/admissible515.tsv", ADMISSIBLE_SHA256),
        ("inputs/listing-quarantine5.tsv", QUARANTINE_SHA256),
        ("runs/replica-a-apply-reopened/functions.tsv", POST_FUNCTIONS_SHA256),
    ):
        require(formal_artifacts.get(source, {}).get("sha256") == expected_hash, f"formal proof does not bind {source}")
    outputs = campaign.get("outputs", {})
    for name in CAMPAIGN_FILES[1:]:
        frozen_name = f"inputs/generation5-{name}"
        stamp = outputs.get(name)
        require(isinstance(stamp, dict), f"generation-5 READY omits {name}")
        require(len(inputs[frozen_name]) == stamp.get("bytes") and sha256_bytes(inputs[frozen_name]) == stamp.get("sha256"), f"generation-5 ledger differs: {name}")
    native_stamp = campaign.get("sourceSnapshot", {}).get("files", {}).get("ledger-native-handlers.tsv")
    require(
        isinstance(native_stamp, dict)
        and len(inputs[NATIVE_INPUT_NAME]) == native_stamp.get("bytes")
        and sha256_bytes(inputs[NATIVE_INPUT_NAME]) == native_stamp.get("sha256"),
        "generation-5 native-handler ledger differs",
    )
    require(campaign.get("sourceSnapshot", {}).get("specimen", {}).get("sha256") == SPECIMEN_SHA256, "generation-5 specimen differs")
    return formal, campaign


def derive_rows(inputs: Mapping[str, bytes]) -> tuple[list[dict[str, str]], dict[str, object]]:
    _formal, _campaign_ready = validate_input_receipts(inputs)
    manifest = parse_tsv(inputs["inputs/admissible515.tsv"], "admissible515")
    quarantine = parse_tsv(inputs["inputs/listing-quarantine5.tsv"], "quarantine5")
    post_functions = parse_tsv(inputs["inputs/post-functions.tsv"], "formal post-functions")
    functions = parse_tsv(inputs["inputs/generation5-campaign-functions.tsv"], "generation-5 functions")
    residuals = parse_tsv(inputs["inputs/generation5-campaign-residuals.tsv"], "generation-5 residuals")
    questions = parse_tsv(inputs["inputs/generation5-campaign-questions.tsv"], "generation-5 questions")
    contracts = parse_tsv(inputs["inputs/generation5-campaign-contracts.tsv"], "generation-5 contracts")
    adjudications = parse_tsv(inputs["inputs/generation5-campaign-adjudications.tsv"], "generation-5 adjudications")
    supersessions = parse_tsv(inputs["inputs/generation5-campaign-supersessions.tsv"], "generation-5 supersessions")
    native_handlers = parse_tsv(inputs[NATIVE_INPUT_NAME], "generation-5 native handlers")

    require(len(manifest) == 515 and len(quarantine) == 5 and len(post_functions) == 8110, "formal cohort counts differ")
    require(len(adjudications) == 2 and len(supersessions) == 40, "generation-5 lineage-control counts differ")
    by_post = unique_map(post_functions, "address", "formal post-functions")
    by_function_entry = unique_map(functions, "entryVa", "generation-5 functions")
    by_residual = unique_map(residuals, "entityKey", "generation-5 residuals")
    by_question = unique_map(questions, "questionId", "generation-5 questions")
    by_contract = unique_map(contracts, "contractId", "generation-5 contracts")
    superseded_old = {row["oldEntityKey"] for row in supersessions}
    quarantine_entries = {int(row["entry"], 16) for row in quarantine}
    native_entries = {int(row["handlerVa"], 16) for row in native_handlers}

    entries = [int(row["entry"], 16) for row in manifest]
    require(len(entries) == len(set(entries)) and entries == sorted(entries), "admissible entries are not exact, unique, and sorted")
    require(sha256_text("\n".join(f"0x{entry:08x}" for entry in entries) + "\n") == TARGET_SET_SHA256, "admissible target-set digest differs")
    require(not (set(entries) & quarantine_entries), "quarantine leaked into admissible targets")
    require(not (set(entries) & native_entries), "Mission-native handler leaked into the residual cohort")

    lineage = []
    total_bytes = 0
    total_instructions = 0
    prior_end = None
    for manifest_row in manifest:
        entry = int(manifest_row["entry"], 16)
        parts = manifest_row["expectedRanges"].split("-")
        require(len(parts) == 2, f"manifest range framing differs at {entry:#x}")
        start, end = (int(value, 16) for value in parts)
        require(start == entry and start < end, f"manifest range differs at {entry:#x}")
        require(prior_end is None or prior_end < start, f"manifest ranges overlap or touch at {entry:#x}")
        prior_end = end
        expected_bytes = int(manifest_row["expectedBodyBytes"])
        expected_instructions = int(manifest_row["expectedInstructionCount"])
        require(end - start == expected_bytes, f"manifest byte span differs at {entry:#x}")
        forbidden_entries = [
            int(value, 16)
            for value in manifest_row["forbiddenEntries"].split(";")
            if value
        ]
        require(
            len(forbidden_entries) == len(set(forbidden_entries))
            and all(start < value < end and value not in entries for value in forbidden_entries),
            f"admissible row has invalid interior forbidden entries at {entry:#x}",
        )

        residual_key = manifest_row["residualEntityKeys"]
        old_question_id = manifest_row["questionIds"]
        old_contract_id = manifest_row["contractIds"]
        require(";" not in residual_key + old_question_id + old_contract_id, f"manifest lineage is not 1:1:1 at {entry:#x}")
        residual = by_residual.get(residual_key)
        question = by_question.get(old_question_id)
        contract = by_contract.get(old_contract_id)
        require(residual is not None and question is not None and contract is not None, f"generation-5 lineage is missing at {entry:#x}")
        require(
            residual.get("startVa", "").lower() == f"0x{start:08x}"
            and residual.get("endVa", "").lower() == f"0x{end:08x}"
            and residual.get("bytes") == str(expected_bytes)
            and residual.get("observedBytes") == str(expected_bytes)
            and residual.get("observationState") == "EXECUTED"
            and residual.get("classification") == "CODE_CANDIDATE"
            and residual.get("classificationVerdict") == "MEASURED_EXECUTION"
            and residual.get("terminalState") == "OPEN_CODE_BOUNDARY"
            and residual.get("campaignState") == "OPEN_EXECUTED_RESIDUAL"
            and residual.get("questionIds") == old_question_id
            and residual_key not in superseded_old,
            f"generation-5 residual state differs at {entry:#x}",
        )
        require(
            question.get("entityKey") == residual_key
            and question.get("questionType") == "EXECUTED_TEXT_BOUNDARY"
            and question.get("state") == "OPEN"
            and question.get("lastOutcome") == "UNSCORED",
            f"generation-5 question state differs at {entry:#x}",
        )
        require(
            contract.get("entityKey") == residual_key
            and contract.get("entityKind") == "TEXT_RESIDUAL"
            and contract.get("entryVa", "").lower() == f"0x{entry:08x}"
            and contract.get("contractState") == "OPEN_CLASSIFICATION"
            and contract.get("semanticGrade") == "C0_OPAQUE"
            and contract.get("authorVerdict") == "UNSCORED"
            and contract.get("runtimeVerdict") == "EXECUTED_BYTES_MEASURED"
            and contract.get("refuterVerdict") == "UNSCORED"
            and contract.get("questionIds") == old_question_id
            and not contract.get("supersedesEntityKeys"),
            f"generation-5 contract state differs at {entry:#x}",
        )
        require(f"0x{entry:08x}" not in by_function_entry, f"target already has a generation-5 function at {entry:#x}")

        post = by_post.get(f"0x{entry:08x}")
        require(post is not None, f"formal post-function is missing at {entry:#x}")
        require(
            post.get("bodyMin", "").lower() == f"0x{start:08x}"
            and post.get("bodyMax", "").lower() == f"0x{end - 1:08x}"
            and post.get("bodyRanges") == "1"
            and post.get("bodyBytes") == str(expected_bytes)
            and post.get("bodyDigest") == manifest_row["expectedRangeDigest"]
            and post.get("instrCount") == str(expected_instructions)
            and post.get("isThunk") == manifest_row["expectedIsThunk"]
            and post.get("thunkTarget", "").lower() == manifest_row["expectedThunkTarget"].lower(),
            f"formal post-function differs from the manifest at {entry:#x}",
        )
        range_set = canonical_range_set_sha256(start, end)
        new_entity = f"CODE:{SPECIMEN_SHA256}:VA=0x{entry:08x}:RANGES={range_set}"
        name = post["name"]
        name_class = function_name_class(name)
        question_type = "EXECUTED_FUNCTION_IDENTITY" if name_class in {"FUN", "VFUNC_SLOT"} else "EXECUTED_FUNCTION_CONTRACT"
        new_question_id = f"Q-{sha256_text(question_type + '|' + new_entity)[:16]}"
        new_contract_id = f"C-{sha256_text(new_entity)[:16]}"
        supersession_id = f"S-{sha256_text(residual_key + '|' + new_entity)[:16]}"
        lineage.append({
            "entry": f"0x{entry:08x}",
            "expectedRanges": manifest_row["expectedRanges"],
            "expectedBodyBytes": str(expected_bytes),
            "expectedRangeDigest": manifest_row["expectedRangeDigest"],
            "expectedBodyRangeSetSha256": range_set,
            "expectedInstructionCount": str(expected_instructions),
            "oldResidualEntityKey": residual_key,
            "oldQuestionId": old_question_id,
            "oldContractId": old_contract_id,
            "expectedNewEntityKey": new_entity,
            "expectedNewName": name,
            "expectedNewNameClass": name_class,
            "expectedNewQuestionType": question_type,
            "expectedNewQuestionId": new_question_id,
            "expectedNewContractId": new_contract_id,
            "expectedSupersessionId": supersession_id,
        })
        total_bytes += expected_bytes
        total_instructions += expected_instructions

    require(total_bytes == 57_182 and total_instructions == 10_602, "lineage byte/instruction totals differ")
    require(len({row["expectedNewEntityKey"] for row in lineage}) == 515, "new function identities are not unique")
    require(len({row["expectedNewQuestionId"] for row in lineage}) == 515, "new question identities are not unique")
    require(len({row["expectedNewContractId"] for row in lineage}) == 515, "new contract identities are not unique")
    require(len({row["expectedSupersessionId"] for row in lineage}) == 515, "new supersession identities are not unique")
    current_entities = {row["entityKey"] for row in functions} | set(by_residual)
    current_question_ids = set(by_question)
    current_contract_ids = set(by_contract)
    require(not ({row["expectedNewEntityKey"] for row in lineage} & current_entities), "new function identity collides with generation 5")
    require(not ({row["expectedNewQuestionId"] for row in lineage} & current_question_ids), "new question identity collides with generation 5")
    require(not ({row["expectedNewContractId"] for row in lineage} & current_contract_ids), "new contract identity collides with generation 5")
    name_classes = {name: sum(row["expectedNewNameClass"] == name for row in lineage) for name in {row["expectedNewNameClass"] for row in lineage}}
    question_types = {name: sum(row["expectedNewQuestionType"] == name for row in lineage) for name in {row["expectedNewQuestionType"] for row in lineage}}
    require(name_classes == {"FUN": 513, "NAMED": 2}, "formal post name-class split differs")
    require(question_types == {"EXECUTED_FUNCTION_IDENTITY": 513, "EXECUTED_FUNCTION_CONTRACT": 2}, "new question-type split differs")
    summary = {
        "rows": 515,
        "bodyBytes": total_bytes,
        "instructions": total_instructions,
        "fullyObservedBodyBytes": total_bytes,
        "quarantinedEntries": 5,
        "nameClasses": name_classes,
        "newQuestionTypes": question_types,
        "expectedDelta": {
            "functions": 515,
            "residuals": -515,
            "questions": 0,
            "contracts": 0,
            "supersessions": 515,
            "adjudications": 0,
        },
    }
    return lineage, summary


def derive(inputs: Mapping[str, bytes]) -> tuple[bytes, dict[str, object]]:
    rows, summary = derive_rows(inputs)
    rendered = render_tsv(LINEAGE_COLUMNS, rows)
    require(len(rendered) == EXPECTED_LINEAGE_BYTES, "independent prospective lineage byte count differs")
    require(sha256_bytes(rendered) == EXPECTED_LINEAGE_SHA256, "independent prospective lineage rendering differs")
    return rendered, summary


def load_external_inputs(formal: Path, campaign: Path) -> dict[str, bytes]:
    require(formal.is_dir() and not is_linklike(formal), "formal input is not one plain directory")
    require(campaign.is_dir() and not is_linklike(campaign), "campaign input is not one plain directory")
    result = {}
    for frozen_name, source_name in FORMAL_SOURCE_NAMES.items():
        path = formal / source_name
        require(path.is_file() and not is_linklike(path), f"formal input is not one plain file: {source_name}")
        result[frozen_name] = path.read_bytes()
    for frozen_name, source_name in CAMPAIGN_SOURCE_NAMES.items():
        path = campaign / source_name
        require(path.is_file() and not is_linklike(path), f"campaign input is not one plain file: {source_name}")
        result[frozen_name] = path.read_bytes()
    campaign_ready = parse_json(result["inputs/generation5-campaign.ready.json"], "generation-5 READY")
    native_spec = campaign_ready.get("sourceSnapshot", {}).get("files", {}).get("ledger-native-handlers.tsv", {})
    native_path = Path(str(native_spec.get("path", "")))
    if not native_path.is_absolute():
        native_path = Path(__file__).resolve().parents[1] / native_path
    native_path = native_path.resolve()
    require(native_path.is_file() and not is_linklike(native_path), "generation-5 native-handler input is not one plain file")
    result[NATIVE_INPUT_NAME] = native_path.read_bytes()
    validate_input_receipts(result)
    return result


def expected_ready(inputs: Mapping[str, bytes], outputs: Mapping[str, bytes], summary: Mapping[str, object]) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "specimenSha256": SPECIMEN_SHA256,
        "formalProofReadySha256": FORMAL_READY_SHA256,
        "generation5ReadySha256": CAMPAIGN_READY_SHA256,
        "targetSetSha256": TARGET_SET_SHA256,
        "summary": summary,
        "inputs": {name: stamp_bytes(name, inputs[name]) for name in INPUT_NAMES},
        "outputs": {name: stamp_bytes(name, outputs[name]) for name in OUTPUT_NAMES},
        "claimBoundary": list(CLAIM_BOUNDARY),
    }


def validate_bundle_tree(bundle: Path) -> None:
    require(bundle.is_dir() and not is_linklike(bundle), "bundle is not one plain directory or is a reparse point")
    expected_root = {"READY.json", "inputs", *OUTPUT_NAMES}
    actual_root = {path.name for path in bundle.iterdir()}
    require(actual_root == expected_root, f"bundle members differ: {sorted(actual_root ^ expected_root)}")
    for name in {"READY.json", *OUTPUT_NAMES}:
        require((bundle / name).is_file() and not is_linklike(bundle / name), f"bundle output is not one plain file: {name}")
    input_root = bundle / "inputs"
    require(input_root.is_dir() and not is_linklike(input_root), "bundle inputs is not one plain directory")
    expected_inputs = {Path(name).name for name in INPUT_NAMES}
    actual_inputs = {path.name for path in input_root.iterdir()}
    require(actual_inputs == expected_inputs, f"bundle input members differ: {sorted(actual_inputs ^ expected_inputs)}")
    for name in expected_inputs:
        require((input_root / name).is_file() and not is_linklike(input_root / name), f"bundle input is not one plain file: {name}")


def read_bundle_inputs(bundle: Path) -> dict[str, bytes]:
    return {name: (bundle / name).read_bytes() for name in INPUT_NAMES}


def output_bytes(owner: Path, inputs: Mapping[str, bytes]) -> tuple[dict[str, bytes], dict[str, object]]:
    lineage, summary = derive(inputs)
    return {"lineage-owner.py": owner.read_bytes(), "lineage515.tsv": lineage}, summary


def verify(bundle: Path) -> dict[str, object]:
    validate_bundle_tree(bundle)
    owner = Path(__file__).resolve()
    require((bundle / "lineage-owner.py").read_bytes() == owner.read_bytes(), "frozen owner differs from executing owner")
    raw_ready = (bundle / "READY.json").read_bytes()
    ready = parse_json(raw_ready, "lineage READY")
    require(raw_ready == canonical_json(ready), "lineage READY is not canonical JSON")
    inputs = read_bundle_inputs(bundle)
    outputs, summary = output_bytes(owner, inputs)
    require(ready == expected_ready(inputs, outputs, summary), "lineage READY semantics differ")
    for name, content in outputs.items():
        require((bundle / name).read_bytes() == content, f"derived output differs: {name}")
    return {"schema": SCHEMA, "status": STATUS, "readySha256": sha256_file(bundle / "READY.json"), "summary": summary}


def build(formal: Path, campaign: Path, out: Path) -> dict[str, object]:
    require(not out.exists() and out.parent.is_dir(), "output must be a new child of an existing directory")
    owner = Path(__file__).resolve()
    inputs = load_external_inputs(formal, campaign)
    outputs, summary = output_bytes(owner, inputs)
    ready = expected_ready(inputs, outputs, summary)
    staging = Path(tempfile.mkdtemp(prefix=f".{out.name}-", dir=out.parent))
    try:
        (staging / "inputs").mkdir()
        for name, content in inputs.items():
            (staging / name).write_bytes(content)
        for name, content in outputs.items():
            (staging / name).write_bytes(content)
        (staging / "READY.json").write_bytes(canonical_json(ready))
        verify(staging)
        os.rename(staging, out)
        return ready
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subs = result.add_subparsers(dest="command", required=True)
    build_parser = subs.add_parser("build")
    build_parser.add_argument("--formal", required=True, type=Path)
    build_parser.add_argument("--campaign", required=True, type=Path)
    build_parser.add_argument("--out", required=True, type=Path)
    verify_parser = subs.add_parser("verify")
    verify_parser.add_argument("--bundle", required=True, type=Path)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "build":
            ready = build(args.formal.resolve(), args.campaign.resolve(), args.out.resolve())
            result = {"schema": SCHEMA, "status": STATUS, "out": str(args.out.resolve()), "summary": ready["summary"]}
        else:
            result = verify(args.bundle.resolve())
        print(json.dumps(result, sort_keys=True))
    except (LineageError, OSError, ValueError, KeyError) as exc:
        print(f"UNSCORED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
