#!/usr/bin/env python3
"""Derive a promotion-safe function-entry cohort from exact .text residuals.

This owner joins three independently useful boundaries that otherwise cannot
advance one another safely:

* a frozen campaign generation supplies exact residual/question/contract keys;
* an independently reproduced static cohort supplies entry/body/lineage proof;
* a later disposable-Ghidra proof may consume only the canonical address list.

The output assigns no names and closes no semantic contract.  It proves only
that each selected entry is instruction-present, fully observed, byte-exact,
and equal to one unsuperseded campaign residual with one open structural
question and one nonterminal contract.  Anything less clean is quarantined.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any


SCHEMA = "bea.re.crt-text-residual-boundary-targets.v2"
CAMPAIGN_SCHEMA = "bea.re.campaign.v5"
CAMPAIGN_REDUCER_SCHEMA = "bea.re.campaign-reducer.v1"
COHORT_SCHEMA = "bea.re.crt-recursive-cohort.v1"
CANARY_REFUTATION_SCHEMA = "bea.re.ghidra-crt-canary-refutation.v1"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
SOURCE_CAMPAIGN_READY_SHA256 = "dd86b8999d9810c31d88e9a66fc41a4f71e46e601ac3e91ada99902907215c69"
PROGRESS_CAMPAIGN_READY_SHA256 = "5bddceb51c131d9c3a1ac634fd0672d0e9999b7ccab3f65dd2b33b4a68947cde"
COHORT_READY_SHA256 = "59b64f11ce4e9d0a8f994c15a438c4a5f98e8dcb40626a55f1c451e843f2628b"
EXPECTED_DIRECT_ENTRIES = 537
EXPECTED_CLEAN_ENTRIES = 521
EXPECTED_CLEAN_BYTES = 58_167
EXPECTED_BATCH_ENTRIES = 520
EXPECTED_BATCH_BYTES = 58_157
EXPECTED_QUARANTINED_ENTRIES = 16
THUNK_CANARY_ADDRESS = "0x00542710"
OUTPUTS = (
    "boundary-owner.py",
    "batch-targets.txt",
    "boundary-targets.tsv",
    "refuted-targets.tsv",
    "quarantined-targets.tsv",
)
CAMPAIGN_OUTPUTS = (
    "campaign-functions.tsv",
    "campaign-residuals.tsv",
    "campaign-questions.tsv",
    "campaign-scenarios.tsv",
    "campaign-levers.tsv",
    "campaign-contracts.tsv",
    "campaign-adjudications.tsv",
    "campaign-supersessions.tsv",
)
TARGET_COLUMNS = (
    "address",
    "endExclusive",
    "bytes",
    "bytesSha256",
    "cohort",
    "residualEntityKey",
    "questionId",
    "contractId",
    "lineageKinds",
    "promotionLane",
)
QUARANTINE_COLUMNS = (
    "address",
    "endExclusive",
    "bytes",
    "cohort",
    "reason",
    "overlappingResiduals",
)
REFUTED_COLUMNS = (
    "address",
    "originalEndExclusive",
    "originalBytes",
    "originalBytesSha256",
    "verdict",
    "observedRanges",
    "observedBytes",
    "observedRangeDigest",
    "observedInstructionCount",
    "refutationReadySha256",
    "nextQuestion",
    "nextInstrument",
)

def discover_repo_root() -> Path:
    """Find the repository when this owner is run from tools/ or a frozen bundle."""
    starts = (Path(__file__).resolve().parent, Path.cwd().resolve())
    visited: set[Path] = set()
    for start in starts:
        for candidate in (start, *start.parents):
            if candidate in visited:
                continue
            visited.add(candidate)
            if (
                (candidate / "README.MD").is_file()
                and (candidate / "tools" / "re_text_residual_boundary.py").is_file()
                and (candidate / "local-lab").is_dir()
            ):
                return candidate
    raise RuntimeError("cannot locate the Onslaught Toolkit repository root")


ROOT = discover_repo_root()


class BoundaryError(ValueError):
    """Raised when an evidence boundary does not reproduce exactly."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BoundaryError(message)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stamp(path: Path, *, root: Path = ROOT) -> dict[str, Any]:
    require(path.is_file(), f"missing artifact: {path}")
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise BoundaryError(f"artifact is outside the repository: {path}") from exc
    return {
        "path": relative,
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def resolve_repo_path(value: object, label: str) -> Path:
    require(isinstance(value, str) and bool(value.strip()), f"{label} has no path")
    raw = Path(str(value))
    path = raw if raw.is_absolute() else ROOT / raw
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise BoundaryError(f"{label} escapes the repository: {value}") from exc
    return resolved


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BoundaryError(f"cannot read {label}: {path}: {exc}") from exc
    require(isinstance(value, dict), f"{label} root is not an object")
    return value


def read_tsv(
    path: Path,
    label: str,
    *,
    leading_comment: str | None = None,
) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            lines = list(stream)
            if leading_comment is not None:
                require(bool(lines), f"{label} is empty")
                require(
                    lines[0].rstrip("\r\n") == leading_comment,
                    f"{label} schema comment drift",
                )
                lines = lines[1:]
            require(
                not any(line.startswith("#") for line in lines),
                f"{label} contains an unexpected comment row",
            )
            reader = csv.DictReader(lines, delimiter="\t")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise BoundaryError(f"cannot read {label}: {path}: {exc}") from exc
    require(reader.fieldnames is not None, f"{label} has no header")
    require(all(None not in row for row in rows), f"{label} has a malformed row")
    return rows


def render_tsv(columns: tuple[str, ...], rows: list[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=list(columns),
        delimiter="\t",
        lineterminator="\n",
        extrasaction="ignore",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column, "") for column in columns})
    return stream.getvalue().encode("utf-8")


def write_tsv(path: Path, columns: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    path.write_bytes(render_tsv(columns, rows))


def render_addresses(rows: list[dict[str, Any]]) -> bytes:
    return "".join(f"{row['address']}\n" for row in rows).encode("ascii")


def canonical_address(value: str, label: str) -> str:
    require(re.fullmatch(r"0x[0-9a-fA-F]{8}", value) is not None, f"{label} is not a VA")
    return f"0x{int(value, 16):08x}"


def integer(value: object, label: str) -> int:
    try:
        result = int(str(value))
    except (TypeError, ValueError) as exc:
        raise BoundaryError(f"{label} is not an integer: {value!r}") from exc
    return result


def validate_stamp(path: Path, expected: object, label: str) -> dict[str, Any]:
    require(isinstance(expected, dict), f"{label} has no stamp")
    actual = stamp(path)
    require(
        actual["bytes"] == expected.get("bytes")
        and actual["sha256"] == expected.get("sha256"),
        f"{label} has changed",
    )
    return actual


def validate_reducer_tree(campaign: Path, ready: dict[str, Any]) -> None:
    reducer = ready.get("reducer")
    require(isinstance(reducer, dict), "campaign has no reducer manifest")
    require(reducer.get("schema") == CAMPAIGN_REDUCER_SCHEMA, "campaign reducer schema drift")
    files = reducer.get("files")
    require(isinstance(files, list) and bool(files), "campaign reducer manifest is empty")
    expected: set[str] = set()
    canonical: list[dict[str, Any]] = []
    for row in files:
        require(
            isinstance(row, dict)
            and set(row) == {"role", "path", "bytes", "sha256"},
            "campaign reducer stamp is malformed",
        )
        relative = str(row["path"])
        require(
            relative.startswith("_reducer/")
            and relative not in expected
            and not Path(relative).is_absolute()
            and ".." not in Path(relative).parts,
            f"unsafe/duplicate reducer path: {relative}",
        )
        expected.add(relative)
        path = campaign / Path(relative)
        require(not path.is_symlink(), f"reducer contains a symlink: {relative}")
        validate_stamp(path, row, f"campaign reducer {relative}")
        canonical.append(row)
    actual = {
        path.relative_to(campaign).as_posix()
        for path in (campaign / "_reducer").rglob("*")
        if path.is_file()
    }
    require(actual == expected, "campaign reducer tree contains unmanifested or missing files")
    digest_material = "".join(
        f"{row['role']}\t{row['sha256']}\t{row['bytes']}\t{row['path']}\n"
        for row in sorted(canonical, key=lambda item: str(item["path"]))
    ).encode("utf-8")
    require(sha256_bytes(digest_material) == reducer.get("id"), "campaign reducer ID drift")


def replay_campaign(campaign: Path) -> dict[str, Any]:
    ready_path = campaign / "campaign.ready.json"
    ready = read_json(ready_path, "campaign READY")
    require(ready.get("schema") == CAMPAIGN_SCHEMA, "unsupported campaign schema")
    outputs = ready.get("outputs")
    require(isinstance(outputs, dict) and set(outputs) == set(CAMPAIGN_OUTPUTS), "campaign outputs drift")
    for name in CAMPAIGN_OUTPUTS:
        validate_stamp(campaign / name, outputs[name], f"campaign output {name}")
    validate_reducer_tree(campaign, ready)
    entry = campaign / str(ready["reducer"].get("entry", ""))
    require(entry.is_file(), "campaign reducer entry is missing")
    bootstrap = (
        "import runpy,sys;from pathlib import Path;"
        "p=Path(sys.argv[1]).resolve();sys.path.insert(0,str(p.parent));"
        "sys.argv=[str(p),*sys.argv[2:]];runpy.run_path(str(p),run_name='__main__')"
    )
    environment = dict(os.environ)
    environment["BEA_REPO_ROOT"] = str(ROOT.resolve())
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            bootstrap,
            str(entry.resolve()),
            "verify",
            "--campaign",
            str(campaign.resolve()),
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    require(
        completed.returncode == 0
        and not completed.stderr.strip()
        and completed.stdout.startswith("CAMPAIGN_VERIFIED "),
        "campaign frozen replay failed: "
        f"exit={completed.returncode} stdout={completed.stdout[-300:]!r} "
        f"stderr={completed.stderr[-300:]!r}",
    )
    return ready


def campaign_indices(campaign: Path) -> dict[str, Any]:
    kwargs = {"leading_comment": f"# {CAMPAIGN_SCHEMA}"}
    residuals = read_tsv(campaign / "campaign-residuals.tsv", "campaign residuals", **kwargs)
    questions = read_tsv(campaign / "campaign-questions.tsv", "campaign questions", **kwargs)
    contracts = read_tsv(campaign / "campaign-contracts.tsv", "campaign contracts", **kwargs)
    functions = read_tsv(campaign / "campaign-functions.tsv", "campaign functions", **kwargs)
    supersessions = read_tsv(
        campaign / "campaign-supersessions.tsv",
        "campaign supersessions",
        **kwargs,
    )
    residual_by_span: dict[tuple[str, str], dict[str, str]] = {}
    for row in residuals:
        key = (
            canonical_address(row["startVa"], "residual start"),
            canonical_address(row["endVa"], "residual end"),
        )
        require(key not in residual_by_span, f"duplicate residual span: {key}")
        residual_by_span[key] = row
    questions_by_entity: dict[str, list[dict[str, str]]] = {}
    for row in questions:
        questions_by_entity.setdefault(row["entityKey"], []).append(row)
    contracts_by_entity: dict[str, list[dict[str, str]]] = {}
    for row in contracts:
        contracts_by_entity.setdefault(row["entityKey"], []).append(row)
    function_entries = {
        canonical_address(row["entryVa"], "function entry") for row in functions
    }
    superseded_old_vas: set[str] = set()
    for row in supersessions:
        old_key = row.get("oldEntityKey", "")
        matches = re.findall(r"VA=(0X[0-9A-Fa-f]{8}|0x[0-9A-Fa-f]{8})", old_key)
        require(len(matches) == 1, f"supersession oldEntityKey has no unique VA: {old_key}")
        superseded_old_vas.add(canonical_address(matches[0].replace("0X", "0x"), "superseded old VA"))
    return {
        "residuals": residuals,
        "residualBySpan": residual_by_span,
        "questionsByEntity": questions_by_entity,
        "contractsByEntity": contracts_by_entity,
        "functionEntries": function_entries,
        "supersededOld": {row.get("oldEntityKey", "") for row in supersessions},
        "supersededOldVas": superseded_old_vas,
    }


def pe_sections(specimen: bytes) -> tuple[int, list[tuple[int, int, int, int]]]:
    require(specimen[:2] == b"MZ", "specimen lacks MZ signature")
    pe_offset = struct.unpack_from("<I", specimen, 0x3C)[0]
    require(specimen[pe_offset : pe_offset + 4] == b"PE\0\0", "specimen lacks PE signature")
    section_count = struct.unpack_from("<H", specimen, pe_offset + 6)[0]
    optional_size = struct.unpack_from("<H", specimen, pe_offset + 20)[0]
    optional = pe_offset + 24
    image_base = struct.unpack_from("<I", specimen, optional + 28)[0]
    table = optional + optional_size
    sections = []
    for index in range(section_count):
        offset = table + index * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
            "<IIII", specimen, offset + 8
        )
        sections.append((virtual_address, virtual_size, raw_pointer, raw_size))
    return image_base, sections


def specimen_body(
    specimen: bytes,
    image_base: int,
    sections: list[tuple[int, int, int, int]],
    start: int,
    end: int,
) -> bytes:
    require(image_base <= start < end, "body lies below the image")
    rva = start - image_base
    length = end - start
    for virtual_address, virtual_size, raw_pointer, raw_size in sections:
        extent = max(virtual_size, raw_size)
        if virtual_address <= rva and rva + length <= virtual_address + extent:
            raw = raw_pointer + (rva - virtual_address)
            require(raw + length <= raw_pointer + raw_size, "body lies outside raw section bytes")
            return specimen[raw : raw + length]
    raise BoundaryError(f"body 0x{start:08x}..0x{end:08x} is outside PE sections")


def overlapping_residuals(
    residuals: list[dict[str, str]], start: int, end: int
) -> list[dict[str, str]]:
    rows = []
    for row in residuals:
        row_start = int(row["startVa"], 16)
        row_end = int(row["endVa"], 16)
        if max(start, row_start) < min(end, row_end):
            rows.append(row)
    return rows


def single_open_lineage(
    indices: dict[str, Any], residual: dict[str, str], label: str
) -> tuple[dict[str, str], dict[str, str]]:
    entity = residual["entityKey"]
    questions = [
        row
        for row in indices["questionsByEntity"].get(entity, [])
        if row.get("state") == "OPEN"
    ]
    contracts = [
        row
        for row in indices["contractsByEntity"].get(entity, [])
        if not row.get("contractState", "").startswith("TERMINAL_")
    ]
    require(len(questions) == 1, f"{label} residual does not have one open question")
    require(len(contracts) == 1, f"{label} residual does not have one nonterminal contract")
    question = questions[0]
    contract = contracts[0]
    require(
        question.get("questionType") == "EXECUTED_TEXT_BOUNDARY"
        and question.get("entityKey") == entity
        and residual.get("questionIds") == question.get("questionId"),
        f"{label} residual question lineage drift",
    )
    require(
        contract.get("entityKind") == "TEXT_RESIDUAL"
        and contract.get("entityKey") == entity
        and contract.get("questionIds") == question.get("questionId"),
        f"{label} residual contract lineage drift",
    )
    require(entity not in indices["supersededOld"], f"{label} residual was already superseded")
    return question, contract


def validate_cohort(ready_path: Path) -> tuple[dict[str, Any], dict[str, Path], dict[str, Any]]:
    require(sha256_file(ready_path) == COHORT_READY_SHA256, "CRT cohort READY is not the pinned derivation")
    ready = read_json(ready_path, "CRT cohort READY")
    require(ready.get("schema") == COHORT_SCHEMA and ready.get("status") == "READY", "CRT cohort is not READY")
    require(
        ready.get("specimen", {}).get("sha256") == SPECIMEN_SHA256,
        "CRT cohort names another specimen",
    )
    require(
        ready.get("counts", {}).get("directlyCreatable") == EXPECTED_DIRECT_ENTRIES,
        "CRT direct-entry count drift",
    )
    artifact_specs = ready.get("artifacts")
    require(isinstance(artifact_specs, dict), "CRT READY has no artifact manifest")
    required = (
        "direct537-addresses.txt",
        "direct537-bodies.tsv",
        "body-projection-details.tsv",
        "entry-lineage.tsv",
        "closure-frontier.tsv",
    )
    paths: dict[str, Path] = {}
    stamps: dict[str, Any] = {}
    for name in required:
        path = ready_path.parent / name
        spec = artifact_specs.get(name)
        validate_stamp(path, spec, f"CRT artifact {name}")
        paths[name] = path
        stamps[name] = stamp(path)
    implementation = ready.get("implementation", {}).get("derive_crt_cohort.py")
    derive_path = ready_path.parent / "derive_crt_cohort.py"
    validate_stamp(derive_path, implementation, "CRT derivation implementation")
    allowed_files = {ready_path.name, *artifact_specs.keys(), *ready.get("implementation", {}).keys()}
    actual_files: set[str] = set()
    for path in ready_path.parent.rglob("*"):
        require(not path.is_symlink(), f"CRT cohort tree contains a symlink: {path}")
        if path.is_file():
            actual_files.add(path.relative_to(ready_path.parent).as_posix())
    require(actual_files == allowed_files, "CRT cohort tree contains unmanifested or missing files")
    completed = subprocess.run(
        [sys.executable, "-I", "-B", str(derive_path), "--verify-only"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    try:
        verifier_result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise BoundaryError("CRT cohort verifier did not emit one JSON result") from exc
    expected_verifier = {
        "artifactCount": 25,
        "discrepancies": [],
        "hardFixpoint": 547,
        "mode": "verify-only",
        "outputDir": str(ready_path.parent.resolve()),
        "status": "READY",
        "weakTailCandidates": 2,
    }
    require(
        completed.returncode == 0
        and not completed.stderr.strip()
        and verifier_result == expected_verifier,
        "CRT cohort verifier failed: "
        f"exit={completed.returncode} stdout={completed.stdout[-300:]!r} "
        f"stderr={completed.stderr[-300:]!r}",
    )
    verifier = {
        "command": ["python", "-I", "-B", stamp(derive_path)["path"], "--verify-only"],
        "exitCode": completed.returncode,
        "stdoutSha256": sha256_bytes(completed.stdout.encode("utf-8")),
        "result": verifier_result,
    }
    return ready, paths, {"artifacts": stamps, "verifier": verifier}


def validate_canary_refutation(ready_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    ready = read_json(ready_path, "CRT canary refutation READY")
    require(
        ready.get("schema") == CANARY_REFUTATION_SCHEMA
        and ready.get("status") == "READY"
        and ready.get("verdict") == "REFUTED_EXACT_ONE_RESIDUAL_BODY",
        "CRT canary refutation verdict drift",
    )
    require(
        ready.get("program", {}).get("specimen", {}).get("sha256") == SPECIMEN_SHA256,
        "CRT canary refutation names another specimen",
    )
    preregistration = ready.get("preregistration", {})
    observation = ready.get("manualObservation", {})
    checks = ready.get("checks", {})
    require(
        preregistration.get("target", {}).get("address") == THUNK_CANARY_ADDRESS
        and preregistration.get("expectedBody", {}).get("bytes") == 10
        and observation.get("observedBody", {}).get("bytes") == 32
        and observation.get("observedBody", {}).get("ranges")
        == [["0x00542710", "0x0054271a"], ["0x00542720", "0x00542736"]]
        and observation.get("tailEntryAbsent") is True
        and observation.get("tailContainedBy") == THUNK_CANARY_ADDRESS
        and checks.get("originalExactBodyClaimRefuted") is True
        and checks.get("entryHypothesisRefuted") is False
        and checks.get("learnedTwoRangeBodyAuthorized") is False
        and checks.get("batch520Authorized") is False
        and ready.get("batchGate") == "BLOCKED_PENDING_NEW_TWO_RANGE_CANARY_AUTHORITY",
        "CRT canary refutation boundary drift",
    )
    tool_spec = ready.get("tool")
    require(isinstance(tool_spec, dict), "CRT canary refutation has no frozen tool")
    tool_path = ready_path.parent / str(tool_spec.get("path", ""))
    validate_stamp(tool_path, tool_spec, "CRT canary refutation tool")
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(tool_path.resolve()),
            "--verify-ready",
            str(ready_path.resolve()),
            "--no-live-readback",
        ],
        cwd=ready_path.parent / "work",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    ready_sha = sha256_file(ready_path)
    expected_prefix = (
        "GHIDRA_CRT_CANARY_REFUTATION_VERIFIED "
        "verdict=REFUTED_EXACT_ONE_RESIDUAL_BODY before=7595 after=7596 "
        "expectedBodyBytes=10 observedBodyBytes=32 "
        f"readySha256={ready_sha}"
    )
    require(
        completed.returncode == 0
        and not completed.stderr.strip()
        and completed.stdout.strip() == expected_prefix,
        "CRT canary frozen verifier failed: "
        f"exit={completed.returncode} stdout={completed.stdout[-300:]!r} "
        f"stderr={completed.stderr[-300:]!r}",
    )
    validation = {
        "ready": stamp(ready_path),
        "tool": stamp(tool_path),
        "verifier": {
            "command": [
                "python", "-I", "-B", stamp(tool_path)["path"],
                "--verify-ready", stamp(ready_path)["path"], "--no-live-readback",
            ],
            "exitCode": 0,
            "stdoutSha256": sha256_bytes(completed.stdout.encode("utf-8")),
        },
        "verdict": ready["verdict"],
        "batchGate": ready["batchGate"],
    }
    return ready, validation


def validate_coverage_lineage(
    cohort_ready: dict[str, Any],
    source_snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Bind the cohort to the campaign's underlying immutable ledger graph.

    The campaign embeds the ledger files, while the independently authored CRT
    receipt embeds the ledger READY wrapper. Comparing wrapper hashes is both
    impossible and weaker than reproducing the files that wrapper attests.
    """

    ledger_ready_spec = cohort_ready.get("inputs", {}).get("ledgerReady")
    require(isinstance(ledger_ready_spec, dict), "CRT cohort has no ledger READY input")
    ledger_ready_path = resolve_repo_path(ledger_ready_spec.get("path"), "CRT ledger READY")
    actual_ready = validate_stamp(ledger_ready_path, ledger_ready_spec, "CRT ledger READY")
    ledger_ready = read_json(ledger_ready_path, "coverage ledger READY")
    require(
        ledger_ready.get("schema") == "bea.re.coverage-ledger-ready.v1",
        "coverage ledger READY schema drift",
    )
    ledger_files = ledger_ready.get("files")
    snapshot_files = source_snapshot.get("files")
    require(
        isinstance(ledger_files, dict)
        and isinstance(snapshot_files, dict)
        and set(ledger_files) == set(snapshot_files),
        "CRT ledger and campaign snapshot file sets differ",
    )
    for name in sorted(ledger_files):
        ledger_stamp = ledger_files[name]
        snapshot_stamp = snapshot_files[name]
        require(
            isinstance(ledger_stamp, dict)
            and isinstance(snapshot_stamp, dict)
            and ledger_stamp.get("bytes") == snapshot_stamp.get("bytes")
            and ledger_stamp.get("sha256") == snapshot_stamp.get("sha256"),
            f"CRT ledger and campaign snapshot differ at {name}",
        )
    cohort_inputs = cohort_ready.get("inputs", {})
    for input_name, file_name in (
        ("ledgerSummary", "ledger-summary.json"),
        ("ledgerUnmapped", "ledger-unmapped.tsv"),
    ):
        input_stamp = cohort_inputs.get(input_name)
        source_stamp = snapshot_files[file_name]
        require(
            isinstance(input_stamp, dict)
            and input_stamp.get("bytes") == source_stamp.get("bytes")
            and input_stamp.get("sha256") == source_stamp.get("sha256"),
            f"CRT {input_name} and campaign snapshot differ",
        )
    body_ranges = cohort_inputs.get("bodyRanges")
    snapshot_body_ranges = source_snapshot.get("parityGraph", {}).get("bodyRanges")
    require(
        isinstance(body_ranges, dict)
        and isinstance(snapshot_body_ranges, dict)
        and body_ranges.get("bytes") == snapshot_body_ranges.get("bytes")
        and body_ranges.get("sha256") == snapshot_body_ranges.get("sha256"),
        "CRT body ranges and campaign parity graph differ",
    )
    return {
        "ready": actual_ready,
        "fileSet": {
            name: {
                "bytes": ledger_files[name]["bytes"],
                "sha256": ledger_files[name]["sha256"],
            }
            for name in sorted(ledger_files)
        },
    }


def derive(
    source_campaign: Path,
    progress_campaign: Path,
    cohort_ready_path: Path,
    canary_refutation_ready_path: Path,
) -> dict[str, Any]:
    require(source_campaign.resolve() != progress_campaign.resolve(), "source and progress campaigns must differ")
    require(
        sha256_file(source_campaign / "campaign.ready.json") == SOURCE_CAMPAIGN_READY_SHA256,
        "structural source campaign READY is not pinned generation zero",
    )
    require(
        sha256_file(progress_campaign / "campaign.ready.json") == PROGRESS_CAMPAIGN_READY_SHA256,
        "progress campaign READY is not pinned generation five",
    )
    source_ready = replay_campaign(source_campaign)
    progress_ready = replay_campaign(progress_campaign)
    require(
        source_ready.get("generation") == 0
        and source_ready.get("parentCampaign") is None,
        "structural source campaign is not a self-contained generation zero",
    )
    require(
        integer(progress_ready.get("generation"), "progress generation")
        > integer(source_ready.get("generation"), "source generation"),
        "progress campaign does not advance the structural source",
    )
    require(
        source_ready.get("sourceSnapshot") == progress_ready.get("sourceSnapshot"),
        "source and progress campaigns do not share the exact structural snapshot",
    )
    specimen_spec = source_ready.get("sourceSnapshot", {}).get("specimen", {})
    require(specimen_spec.get("sha256") == SPECIMEN_SHA256, "campaign names another specimen")
    cohort_ready, cohort_paths, cohort_validation = validate_cohort(cohort_ready_path)
    canary_refutation_ready, canary_refutation_validation = validate_canary_refutation(
        canary_refutation_ready_path
    )
    coverage_lineage = validate_coverage_lineage(
        cohort_ready,
        source_ready.get("sourceSnapshot", {}),
    )

    source = campaign_indices(source_campaign)
    progress = campaign_indices(progress_campaign)
    bodies = read_tsv(cohort_paths["direct537-bodies.tsv"], "direct CRT bodies")
    details = read_tsv(cohort_paths["body-projection-details.tsv"], "CRT body details")
    lineage = read_tsv(cohort_paths["entry-lineage.tsv"], "CRT entry lineage")
    closure_frontier = read_tsv(cohort_paths["closure-frontier.tsv"], "CRT closure frontier")
    detail_by_entry = {canonical_address(row["entry"], "detail entry"): row for row in details}
    lineage_by_entry: dict[str, list[dict[str, str]]] = {}
    for row in lineage:
        lineage_by_entry.setdefault(canonical_address(row["entry"], "lineage entry"), []).append(row)
    addresses = [
        canonical_address(value, "direct address")
        for value in cohort_paths["direct537-addresses.txt"].read_text(encoding="ascii").splitlines()
    ]
    body_addresses = [canonical_address(row["entry"], "body entry") for row in bodies]
    require(
        len(addresses) == EXPECTED_DIRECT_ENTRIES
        and addresses == sorted(addresses, key=lambda value: int(value, 16))
        and len(addresses) == len(set(addresses))
        and body_addresses == addresses,
        "direct CRT address/body lists are not canonical and identical",
    )

    specimen_path = resolve_repo_path(
        cohort_ready.get("inputs", {}).get("specimen", {}).get("path"),
        "CRT specimen",
    )
    validate_stamp(specimen_path, cohort_ready["inputs"]["specimen"], "CRT specimen")
    specimen = specimen_path.read_bytes()
    require(sha256_bytes(specimen) == SPECIMEN_SHA256, "pristine specimen drift")
    image_base, sections = pe_sections(specimen)

    targets: list[dict[str, Any]] = []
    quarantined: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    for body, address in zip(bodies, addresses):
        end_address = canonical_address(body["endExclusive"], "body end")
        start = int(address, 16)
        end = int(end_address, 16)
        length = integer(body["length"], "body length")
        require(end - start == length and length > 0, f"body extent drift at {address}")
        body_bytes = specimen_body(specimen, image_base, sections, start, end)
        require(sha256_bytes(body_bytes) == body["bytesSha256"], f"body hash drift at {address}")
        detail = detail_by_entry.get(address)
        require(detail is not None, f"missing body details at {address}")
        require(
            detail.get("strength") == "HARD"
            and detail.get("listingState") == "INSTRUCTION_PRESENT"
            and integer(detail.get("length"), "detail length") == length
            and detail.get("bytesSha256") == body["bytesSha256"],
            f"body detail policy drift at {address}",
        )
        lineage_rows = lineage_by_entry.get(address, [])
        require(bool(lineage_rows), f"missing entry lineage at {address}")
        source_residual = source["residualBySpan"].get((address, end_address))
        progress_residual = progress["residualBySpan"].get((address, end_address))
        if source_residual is None or progress_residual is None:
            overlaps = overlapping_residuals(progress["residuals"], start, end)
            if len(overlaps) == 1:
                overlap_start = int(overlaps[0]["startVa"], 16)
                overlap_end = int(overlaps[0]["endVa"], 16)
                reason = (
                    "BODY_IS_STRICT_SUBRANGE_OF_RESIDUAL"
                    if overlap_start <= start and end <= overlap_end
                    else "BODY_PARTIALLY_OVERLAPS_RESIDUAL"
                )
            elif len(overlaps) > 1:
                reason = "BODY_CROSSES_RESIDUALS"
            else:
                reason = "NO_EXACT_RESIDUAL"
            quarantined.append(
                {
                    "address": address,
                    "endExclusive": end_address,
                    "bytes": length,
                    "cohort": body["cohort"],
                    "reason": reason,
                    "overlappingResiduals": ";".join(row["entityKey"] for row in overlaps),
                }
            )
            continue
        require(
            source_residual["entityKey"] == progress_residual["entityKey"],
            f"residual identity changed across campaigns at {address}",
        )
        for label, residual in (("source", source_residual), ("progress", progress_residual)):
            require(
                integer(residual["bytes"], f"{label} residual bytes") == length
                and integer(residual["observedBytes"], f"{label} observed bytes") == length
                and residual.get("observationState") == "EXECUTED"
                and residual.get("classification") == "CODE_CANDIDATE"
                and residual.get("terminalState") == "OPEN_CODE_BOUNDARY",
                f"{label} residual is not a fully observed open code boundary at {address}",
            )
        require(
            integer(detail.get("observedBytes"), "detail observed bytes") == length,
            f"static projection is not fully observed at {address}",
        )
        source_question, source_contract = single_open_lineage(source, source_residual, "source")
        progress_question, progress_contract = single_open_lineage(progress, progress_residual, "progress")
        require(
            source_question["questionId"] == progress_question["questionId"]
            and source_contract["contractId"] == progress_contract["contractId"],
            f"question/contract lineage changed across campaigns at {address}",
        )
        require(
            address not in source["functionEntries"] and address not in progress["functionEntries"],
            f"target already has a campaign function at {address}",
        )
        require(
            address not in source["supersededOldVas"]
            and address not in progress["supersededOldVas"],
            f"target address was already superseded at {address}",
        )
        lineage_rows = sorted(
            lineage_rows,
            key=lambda row: (
                row.get("evidenceKind", ""),
                row.get("sourceVa", ""),
                row.get("sourceOrdinal", ""),
            ),
        )
        target = {
            "address": address,
            "endExclusive": end_address,
            "bytes": length,
            "bytesSha256": body["bytesSha256"],
            "cohort": body["cohort"],
            "residualEntityKey": progress_residual["entityKey"],
            "questionId": progress_question["questionId"],
            "contractId": progress_contract["contractId"],
            "lineage": lineage_rows,
        }
        targets.append(target)
        manifest_rows.append(
            {
                **target,
                "lineageKinds": ";".join(sorted({row["evidenceKind"] for row in lineage_rows})),
                "promotionLane": (
                    "ISOLATED_THUNK_CANARY"
                    if address == THUNK_CANARY_ADDRESS
                    else "BATCH_AFTER_CANARY"
                ),
            }
        )

    require(len(targets) == EXPECTED_CLEAN_ENTRIES, "clean target count drift")
    require(sum(row["bytes"] for row in targets) == EXPECTED_CLEAN_BYTES, "clean target byte total drift")
    require(len(quarantined) == EXPECTED_QUARANTINED_ENTRIES, "quarantine count drift")
    require(
        [row["address"] for row in targets]
        == sorted((row["address"] for row in targets), key=lambda value: int(value, 16)),
        "clean targets are not numerically sorted",
    )
    for left, right in zip(targets, targets[1:]):
        require(int(left["endExclusive"], 16) <= int(right["address"], 16), "target bodies overlap")
    canary_targets = [row for row in targets if row["address"] == THUNK_CANARY_ADDRESS]
    batch_targets = [row for row in targets if row["address"] != THUNK_CANARY_ADDRESS]
    require(
        len(canary_targets) == 1
        and canary_targets[0]["bytes"] == EXPECTED_CLEAN_BYTES - EXPECTED_BATCH_BYTES,
        "isolated thunk canary drift",
    )
    require(
        len(batch_targets) == EXPECTED_BATCH_ENTRIES
        and sum(row["bytes"] for row in batch_targets) == EXPECTED_BATCH_BYTES,
        "batch-safe target cohort drift",
    )
    weak_sources = {
        canonical_address(row["sourceEntry"], "closure weak source")
        for row in closure_frontier
        if row.get("disposition") == "WEAK_TAIL_CANDIDATE"
    }
    require(
        not weak_sources.intersection(row["address"] for row in batch_targets),
        "batch target owns a weak-tail closure edge",
    )

    cohort_counts: dict[str, dict[str, int]] = {}
    for row in targets:
        entry = cohort_counts.setdefault(row["cohort"], {"entries": 0, "bytes": 0})
        entry["entries"] += 1
        entry["bytes"] += row["bytes"]
    batch_cohort_counts: dict[str, dict[str, int]] = {}
    for row in batch_targets:
        entry = batch_cohort_counts.setdefault(row["cohort"], {"entries": 0, "bytes": 0})
        entry["entries"] += 1
        entry["bytes"] += row["bytes"]
    ledger_summary_path = resolve_repo_path(
        cohort_ready.get("inputs", {}).get("ledgerSummary", {}).get("path"),
        "CRT ledger summary",
    )
    validate_stamp(
        ledger_summary_path,
        cohort_ready["inputs"]["ledgerSummary"],
        "CRT ledger summary",
    )
    ledger_summary = read_json(ledger_summary_path, "coverage ledger summary")
    text_bytes = integer(ledger_summary.get("bytes", {}).get("textTotal"), "text bytes")
    body_union = integer(ledger_summary.get("bytes", {}).get("namedBodyUnion"), "body union")
    executed_unmapped = integer(
        ledger_summary.get("bytes", {}).get("executedButUnmapped"),
        "executed-unmapped bytes",
    )
    progress_counts = progress_ready.get("counts", {})
    projection = {
        "baselineFunctions": integer(progress_counts.get("functions"), "campaign functions"),
        "projectedFunctions": integer(progress_counts.get("functions"), "campaign functions") + len(batch_targets),
        "baselineResiduals": integer(progress_counts.get("residuals"), "campaign residuals"),
        "projectedResiduals": integer(progress_counts.get("residuals"), "campaign residuals") - len(batch_targets),
        "baselineBodyUnionBytes": body_union,
        "projectedBodyUnionBytes": body_union + EXPECTED_BATCH_BYTES,
        "projectedBodyUnionPct": round((body_union + EXPECTED_BATCH_BYTES) * 100 / text_bytes, 8),
        "baselineExecutedUnmappedBytes": executed_unmapped,
        "projectedExecutedUnmappedBytes": executed_unmapped - EXPECTED_BATCH_BYTES,
        "hard547EntryFractionPct": round(len(batch_targets) * 100 / 547, 8),
        "hard547ByteFractionPct": round(EXPECTED_BATCH_BYTES * 100 / 59_759, 8),
        "direct537EntryFractionPct": round(len(batch_targets) * 100 / EXPECTED_DIRECT_ENTRIES, 8),
        "boundary": "Projection only; the refuted original canary blocks batch authority until a fresh prospective two-range canary proof survives.",
    }
    require(
        projection["projectedFunctions"] == 8115
        and projection["projectedResiduals"] == 6098
        and projection["projectedExecutedUnmappedBytes"] == 5922,
        "known batch-520 projection drift",
    )
    refuted_target = {
        "address": THUNK_CANARY_ADDRESS,
        "originalEndExclusive": canary_targets[0]["endExclusive"],
        "originalBytes": canary_targets[0]["bytes"],
        "originalBytesSha256": canary_targets[0]["bytesSha256"],
        "verdict": canary_refutation_ready["verdict"],
        "observedRanges": "0x00542710-0x0054271a;0x00542720-0x00542736",
        "observedBytes": 32,
        "observedRangeDigest": canary_refutation_ready["manualObservation"]["observedBody"]["rangeDigest"],
        "observedInstructionCount": 9,
        "refutationReadySha256": canary_refutation_validation["ready"]["sha256"],
        "nextQuestion": "Does a fresh post40 clone reproduce this natural two-range body exactly?",
        "nextInstrument": "CreateFunctionsFromBoundaryManifest probe/apply on two fresh scratch clones",
    }
    batch_manifest_rows = [
        {
            **row,
            "promotionLane": "BLOCKED_PENDING_TWO_RANGE_CANARY_AUTHORITY",
        }
        for row in manifest_rows
        if row["address"] != THUNK_CANARY_ADDRESS
    ]
    return {
        "sourceCampaignReady": source_ready,
        "progressCampaignReady": progress_ready,
        "cohortReady": cohort_ready,
        "cohortValidation": cohort_validation,
        "canaryRefutationReady": canary_refutation_ready,
        "canaryRefutationValidation": canary_refutation_validation,
        "coverageLineage": coverage_lineage,
        "specimen": stamp(specimen_path),
        "ledgerSummary": stamp(ledger_summary_path),
        "batchTargets": batch_targets,
        "manifestRows": batch_manifest_rows,
        "refutedTargets": [refuted_target],
        "quarantined": quarantined,
        "batchCohortCounts": batch_cohort_counts,
        "projection": projection,
    }


def selection_policy() -> dict[str, Any]:
    return {
        "sourceSet": "CRT_DIRECT537_INSTRUCTION_PRESENT",
        "bodyEqualsOneResidual": True,
        "fullyObserved": True,
        "openQuestionCount": 1,
        "nonterminalContractCount": 1,
        "alreadySupersededAllowed": False,
        "semanticNamesAuthorized": False,
        "requiresElevation": False,
        "batchRequiresTerminalCanaryAdjudication": True,
        "canaryAdjudication": "REFUTED_ORIGINAL_ONE_RESIDUAL_BODY",
        "batchAuthorized": False,
    }


def claim_boundary() -> list[str]:
    return [
        "Every one of the 520 selected addresses is a hard, instruction-present consumed-pointer/direct-call entry whose byte-exact projected body equals one fully executed campaign residual.",
        "Each selected residual retains exactly one open structural question and one nonterminal opaque contract; this boundary assigns no semantic name and closes no behavior contract.",
        "Address 0x00542710 is excluded: its preregistered ten-byte body was refuted when Ghidra naturally inferred a 32-byte, two-range body containing 0x00542720.",
        "The learned two-range canary body remains a new hypothesis. Until a fresh prospective replicated proof survives, this 520-entry list is a derived cohort and not mutation authority.",
        "The 16 non-exact structural cases and all disassembly/weak candidates remain quarantined.",
        "Function/residual/count projections are preregistered expectations, not Ghidra or campaign facts until scratch/live readback and a fresh ledger reproduce them.",
    ]


def build_receipt(
    source_campaign: Path,
    progress_campaign: Path,
    cohort_ready_path: Path,
    canary_refutation_ready_path: Path,
    out: Path,
) -> dict[str, Any]:
    derived = derive(
        source_campaign,
        progress_campaign,
        cohort_ready_path,
        canary_refutation_ready_path,
    )
    if out.exists():
        raise BoundaryError(f"refusing existing destination: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        (stage / "boundary-owner.py").write_bytes(Path(__file__).resolve().read_bytes())
        batch_path = stage / "batch-targets.txt"
        batch_path.write_bytes(render_addresses(derived["batchTargets"]))
        write_tsv(stage / "boundary-targets.tsv", TARGET_COLUMNS, derived["manifestRows"])
        write_tsv(stage / "refuted-targets.tsv", REFUTED_COLUMNS, derived["refutedTargets"])
        write_tsv(
            stage / "quarantined-targets.tsv",
            QUARANTINE_COLUMNS,
            derived["quarantined"],
        )
        receipt = {
            "schema": SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "tool": stamp(stage / "boundary-owner.py", root=stage),
            "sourceCampaign": {
                "path": source_campaign.resolve().relative_to(ROOT).as_posix(),
                "ready": stamp(source_campaign / "campaign.ready.json"),
                "generation": derived["sourceCampaignReady"]["generation"],
                "reducerId": derived["sourceCampaignReady"]["reducer"]["id"],
            },
            "progressCampaign": {
                "path": progress_campaign.resolve().relative_to(ROOT).as_posix(),
                "ready": stamp(progress_campaign / "campaign.ready.json"),
                "generation": derived["progressCampaignReady"]["generation"],
                "reducerId": derived["progressCampaignReady"]["reducer"]["id"],
            },
            "cohort": {
                "ready": stamp(cohort_ready_path),
                **derived["cohortValidation"],
            },
            "canaryRefutation": derived["canaryRefutationValidation"],
            "coverageLineage": derived["coverageLineage"],
            "specimen": derived["specimen"],
            "ledgerSummary": derived["ledgerSummary"],
            "selection": selection_policy(),
            "count": len(derived["batchTargets"]),
            "bytes": sum(row["bytes"] for row in derived["batchTargets"]),
            "cohortCounts": derived["batchCohortCounts"],
            "targets": derived["batchTargets"],
            "refutedCount": len(derived["refutedTargets"]),
            "refutedTargets": derived["refutedTargets"],
            "quarantineCount": len(derived["quarantined"]),
            "projection": derived["projection"],
            "outputs": {
                name: stamp(stage / name, root=stage) for name in OUTPUTS
            },
            "claimBoundary": claim_boundary(),
        }
        ready_path = stage / "boundary-targets.ready.json"
        ready_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(stage, out)
        return receipt
    except Exception:
        for path in sorted(stage.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        stage.rmdir()
        raise


def verify_bundle(out: Path) -> dict[str, Any]:
    ready_path = out / "boundary-targets.ready.json"
    ready = read_json(ready_path, "text-residual boundary READY")
    expected_keys = {
        "schema",
        "generatedAtUtc",
        "tool",
        "sourceCampaign",
        "progressCampaign",
        "cohort",
        "canaryRefutation",
        "coverageLineage",
        "specimen",
        "ledgerSummary",
        "selection",
        "count",
        "bytes",
        "cohortCounts",
        "targets",
        "refutedCount",
        "refutedTargets",
        "quarantineCount",
        "projection",
        "outputs",
        "claimBoundary",
    }
    require(ready.get("schema") == SCHEMA and set(ready) == expected_keys, "boundary READY schema/fields drift")
    generated_at = ready.get("generatedAtUtc")
    try:
        generated_time = datetime.fromisoformat(str(generated_at))
    except (TypeError, ValueError) as exc:
        raise BoundaryError("boundary generatedAtUtc is not an ISO timestamp") from exc
    require(
        isinstance(generated_at, str)
        and generated_time.tzinfo is not None
        and generated_time.utcoffset() is not None,
        "boundary generatedAtUtc has no timezone",
    )
    expected_tree = {"boundary-targets.ready.json", *OUTPUTS}
    actual_tree: set[str] = set()
    for path in out.rglob("*"):
        require(not path.is_symlink(), f"boundary bundle contains a symlink: {path}")
        if path.is_file():
            actual_tree.add(path.relative_to(out).as_posix())
    require(actual_tree == expected_tree, "boundary bundle contains unmanifested or missing files")
    frozen_tool = out / "boundary-owner.py"
    validate_stamp(frozen_tool, ready.get("tool"), "boundary tool")
    require(
        sha256_file(Path(__file__).resolve()) == sha256_file(frozen_tool),
        "execute the exact frozen boundary owner recorded by READY",
    )
    outputs = ready.get("outputs")
    require(isinstance(outputs, dict) and set(outputs) == set(OUTPUTS), "boundary output manifest drift")
    for name in OUTPUTS:
        expected = outputs[name]
        actual = {
            "path": name,
            "bytes": (out / name).stat().st_size if (out / name).is_file() else -1,
            "sha256": sha256_file(out / name) if (out / name).is_file() else "",
        }
        require(actual == expected, f"boundary output changed: {name}")
    source_spec = ready.get("sourceCampaign")
    progress_spec = ready.get("progressCampaign")
    cohort_spec = ready.get("cohort")
    canary_spec = ready.get("canaryRefutation")
    require(isinstance(source_spec, dict) and isinstance(progress_spec, dict), "campaign envelopes missing")
    require(isinstance(cohort_spec, dict), "cohort envelope missing")
    require(isinstance(canary_spec, dict), "canary refutation envelope missing")
    source_campaign = resolve_repo_path(source_spec.get("path"), "source campaign")
    progress_campaign = resolve_repo_path(progress_spec.get("path"), "progress campaign")
    cohort_ready_path = resolve_repo_path(cohort_spec.get("ready", {}).get("path"), "cohort READY")
    canary_refutation_ready_path = resolve_repo_path(
        canary_spec.get("ready", {}).get("path"),
        "canary refutation READY",
    )
    validate_stamp(source_campaign / "campaign.ready.json", source_spec.get("ready"), "source campaign READY")
    validate_stamp(progress_campaign / "campaign.ready.json", progress_spec.get("ready"), "progress campaign READY")
    validate_stamp(cohort_ready_path, cohort_spec.get("ready"), "cohort READY")
    validate_stamp(
        canary_refutation_ready_path,
        canary_spec.get("ready"),
        "canary refutation READY",
    )
    derived = derive(
        source_campaign,
        progress_campaign,
        cohort_ready_path,
        canary_refutation_ready_path,
    )
    expected_source = {
        "path": source_campaign.resolve().relative_to(ROOT).as_posix(),
        "ready": stamp(source_campaign / "campaign.ready.json"),
        "generation": derived["sourceCampaignReady"]["generation"],
        "reducerId": derived["sourceCampaignReady"]["reducer"]["id"],
    }
    expected_progress = {
        "path": progress_campaign.resolve().relative_to(ROOT).as_posix(),
        "ready": stamp(progress_campaign / "campaign.ready.json"),
        "generation": derived["progressCampaignReady"]["generation"],
        "reducerId": derived["progressCampaignReady"]["reducer"]["id"],
    }
    expected_cohort = {
        "ready": stamp(cohort_ready_path),
        **derived["cohortValidation"],
    }
    expected_canary = derived["canaryRefutationValidation"]
    require(source_spec == expected_source, "source campaign envelope does not rederive")
    require(progress_spec == expected_progress, "progress campaign envelope does not rederive")
    require(cohort_spec == expected_cohort, "cohort validation envelope does not rederive")
    require(canary_spec == expected_canary, "canary refutation envelope does not rederive")
    require(ready.get("specimen") == derived["specimen"], "specimen envelope does not rederive")
    require(
        ready.get("ledgerSummary") == derived["ledgerSummary"],
        "ledger summary envelope does not rederive",
    )
    require(ready.get("selection") == selection_policy(), "selection policy drift")
    require(ready.get("claimBoundary") == claim_boundary(), "claim boundary drift")
    require(ready.get("targets") == derived["batchTargets"], "boundary targets do not rederive")
    require(ready.get("count") == len(derived["batchTargets"]), "boundary count drift")
    require(ready.get("bytes") == sum(row["bytes"] for row in derived["batchTargets"]), "boundary byte count drift")
    require(ready.get("cohortCounts") == derived["batchCohortCounts"], "boundary cohort counts drift")
    require(ready.get("coverageLineage") == derived["coverageLineage"], "coverage lineage drift")
    require(ready.get("refutedCount") == len(derived["refutedTargets"]), "refuted count drift")
    require(ready.get("refutedTargets") == derived["refutedTargets"], "refuted targets drift")
    require(ready.get("quarantineCount") == len(derived["quarantined"]), "boundary quarantine count drift")
    require(ready.get("projection") == derived["projection"], "boundary projection drift")
    require(
        (out / "batch-targets.txt").read_bytes() == render_addresses(derived["batchTargets"]),
        "batch address list does not match targets",
    )
    require(
        (out / "boundary-targets.tsv").read_bytes()
        == render_tsv(TARGET_COLUMNS, derived["manifestRows"]),
        "boundary manifest bytes do not rederive",
    )
    require(
        (out / "refuted-targets.tsv").read_bytes()
        == render_tsv(REFUTED_COLUMNS, derived["refutedTargets"]),
        "refuted manifest bytes do not rederive",
    )
    require(
        (out / "quarantined-targets.tsv").read_bytes()
        == render_tsv(QUARANTINE_COLUMNS, derived["quarantined"]),
        "boundary quarantine bytes do not rederive",
    )
    return {
        "count": len(derived["batchTargets"]),
        "bytes": sum(row["bytes"] for row in derived["batchTargets"]),
        "refuted": len(derived["refutedTargets"]),
        "quarantined": len(derived["quarantined"]),
        "ready": stamp(ready_path),
        "projection": derived["projection"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    write = commands.add_parser("write")
    write.add_argument("--source-campaign", type=Path, required=True)
    write.add_argument("--progress-campaign", type=Path, required=True)
    write.add_argument("--cohort-ready", type=Path, required=True)
    write.add_argument("--canary-refutation-ready", type=Path, required=True)
    write.add_argument("--out", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--bundle", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "write":
            receipt = build_receipt(
                args.source_campaign.resolve(),
                args.progress_campaign.resolve(),
                args.cohort_ready.resolve(),
                args.canary_refutation_ready.resolve(),
                args.out.resolve(),
            )
            verified = verify_bundle(args.out.resolve())
            print(
                "TEXT_RESIDUAL_BOUNDARY_READY "
                f"count={receipt['count']} bytes={receipt['bytes']} "
                f"refuted={receipt['refutedCount']} "
                f"readySha256={verified['ready']['sha256']}"
            )
        else:
            verified = verify_bundle(args.bundle.resolve())
            print(
                "TEXT_RESIDUAL_BOUNDARY_VERIFIED "
                f"count={verified['count']} bytes={verified['bytes']} "
                f"refuted={verified['refuted']} "
                f"quarantined={verified['quarantined']} "
                f"readySha256={verified['ready']['sha256']}"
            )
        return 0
    except (BoundaryError, OSError, UnicodeError, ValueError) as exc:
        print(f"REFUSED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
