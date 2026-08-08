#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Publish or check the tracked view of one externally pinned campaign authority.

The register is a convenience projection, never a campaign selector.  A caller
must name the exact campaign root, READY digest, reducer identity, and output—or
name the single ``current_re_authority`` pointer in ``developer_state.json``.
The frozen reducer completes a full campaign replay before any rows are read.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
BOOTSTRAP = TOOLS / "re_campaign_frozen_bootstrap.py"
SCHEMA = "bea.re.evidence-register.v2"
HEADER_COLUMNS = (
    "entryVa",
    "name",
    "grade",
    "resolution",
    "contractState",
    "evidence",
    "generation",
    "readySha256",
)


class ExportError(RuntimeError):
    """The requested register source is not an exact replay authority."""


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ExportError(f"{label} is not an object")
    return value


def resolve_state(path: Path) -> tuple[Path, Path, str, str]:
    state = mapping(json.loads(path.read_text(encoding="utf-8")), "developer state")
    authority = mapping(state.get("current_re_authority"), "current_re_authority")
    required = {
        "campaignPath",
        "readySha256",
        "reducerId",
        "evidenceRegisterPath",
    }
    if not required <= set(authority):
        raise ExportError("current_re_authority is missing exact register routing fields")
    campaign_root = Path(str(authority["campaignPath"]))
    output = Path(str(authority["evidenceRegisterPath"]))
    if not campaign_root.is_absolute():
        campaign_root = REPO / campaign_root
    if not output.is_absolute():
        output = REPO / output
    return (
        campaign_root,
        output,
        str(authority["readySha256"]),
        str(authority["reducerId"]),
    )


def verify_full_replay(
    campaign_root: Path, expected_ready_sha256: str, expected_reducer_id: str
) -> None:
    environment = os.environ.copy()
    environment["BEA_REPO_ROOT"] = os.fspath(REPO)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [
            os.fspath(Path(sys.executable)),
            "-I",
            "-B",
            os.fspath(BOOTSTRAP),
            "--campaign",
            os.fspath(campaign_root),
            "--mode",
            "full",
            "--expected-ready-sha256",
            expected_ready_sha256,
            "--expected-reducer-id",
            expected_reducer_id,
        ],
        cwd=REPO,
        env=environment,
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    if completed.returncode != 0 or "CAMPAIGN_VERIFIED" not in completed.stdout:
        detail = (completed.stderr or completed.stdout).strip()
        raise ExportError(f"frozen full replay refused register source: {detail}")


def read_functions(path: Path) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as handle:
        marker = handle.readline().rstrip("\r\n")
        if marker != "# bea.re.campaign.v5":
            raise ExportError("campaign function ledger schema differs")
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {
        "entityKey",
        "entryVa",
        "currentName",
        "semanticGrade",
        "resolutionState",
        "campaignState",
        "evidenceStates",
    }
    if not rows or not required <= set(rows[0]):
        raise ExportError("campaign function ledger shape differs")
    if len({row["entityKey"] for row in rows}) != len(rows):
        raise ExportError("campaign function ledger has duplicate entity identities")
    return rows


def build(
    campaign_root: Path,
    *,
    expected_ready_sha256: str,
    expected_reducer_id: str,
) -> dict[str, object]:
    campaign_root = Path(os.path.abspath(campaign_root))
    ready_path = campaign_root / "campaign.ready.json"
    if not ready_path.is_file():
        raise ExportError(f"campaign READY is missing: {ready_path}")
    actual_ready_sha256 = sha256_path(ready_path)
    if actual_ready_sha256 != expected_ready_sha256:
        raise ExportError("campaign READY differs from the externally pinned identity")
    receipt = mapping(json.loads(ready_path.read_text(encoding="utf-8")), "campaign READY")
    embedded_ready = receipt.get("readySha256")
    if embedded_ready is not None and embedded_ready != actual_ready_sha256:
        raise ExportError("campaign READY self-identity disagrees with its actual bytes")
    reducer = mapping(receipt.get("reducer"), "campaign reducer")
    if reducer.get("id") != expected_reducer_id:
        raise ExportError("campaign reducer differs from the externally pinned identity")
    verify_full_replay(campaign_root, actual_ready_sha256, expected_reducer_id)

    generation = receipt.get("generation")
    generated_at = receipt.get("generatedAtUtc")
    if not isinstance(generation, int) or generation < 0:
        raise ExportError("campaign generation is invalid")
    if not isinstance(generated_at, str) or "T" not in generated_at:
        raise ExportError("campaign READY generatedAtUtc is invalid")
    advance = receipt.get("advance")
    lineage_id = (
        str(advance.get("branchId"))
        if isinstance(advance, dict) and advance.get("branchId")
        else "historical-main"
    )
    functions = read_functions(campaign_root / "campaign-functions.tsv")
    rows: list[dict[str, str]] = []
    for function in functions:
        rows.append(
            {
                "entryVa": function["entryVa"],
                "name": function["currentName"],
                "grade": function["semanticGrade"],
                "resolution": function["resolutionState"],
                "contractState": function["campaignState"],
                "evidence": function["evidenceStates"],
                "generation": str(generation),
                "readySha256": actual_ready_sha256,
            }
        )
    rows.sort(key=lambda row: row["entryVa"])
    return {
        "rows": rows,
        "generation": generation,
        "generatedAtUtc": generated_at,
        "readySha256": actual_ready_sha256,
        "reducerId": expected_reducer_id,
        "lineageId": lineage_id,
        "authorityClass": "FULL_CAMPAIGN_REPLAY_AUTHORITY",
    }


def render(result: dict[str, object]) -> str:
    lines = [
        f"# {SCHEMA}",
        f"# generatedAtUtc: {result['generatedAtUtc']}",
        f"# generation: {result['generation']}",
        f"# readySha256: {result['readySha256']}",
        f"# reducerId: {result['reducerId']}",
        f"# lineageId: {result['lineageId']}",
        f"# authorityClass: {result['authorityClass']}",
        "# Deterministic tracked projection of the externally pinned campaign authority.",
        "# Regenerate or check with tools/re_evidence_register_export.py; never select",
        "# campaign authority from this projection itself.",
        "\t".join(HEADER_COLUMNS),
    ]
    for row in result["rows"]:
        assert isinstance(row, dict)
        lines.append(
            "\t".join(
                str(row[column]).replace("\t", " ").replace("\r", " ").replace("\n", " ")
                for column in HEADER_COLUMNS
            )
        )
    return "\n".join(lines) + "\n"


def atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".partial", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def check_state_header(state_path: Path, output: Path) -> None:
    state = mapping(json.loads(state_path.read_text(encoding="utf-8")), "developer state")
    authority = mapping(state.get("current_re_authority"), "current_re_authority")
    expected = {
        "schema": SCHEMA,
        "generation": str(authority.get("generation", "")),
        "readySha256": str(authority.get("readySha256", "")),
        "reducerId": str(authority.get("reducerId", "")),
        "lineageId": str(authority.get("lineageId", "")),
        "authorityClass": "FULL_CAMPAIGN_REPLAY_AUTHORITY",
    }
    if not output.is_file():
        raise ExportError(f"tracked evidence register is missing: {output}")
    observed: dict[str, str] = {}
    with open(output, "r", encoding="utf-8") as handle:
        first = handle.readline().rstrip("\r\n")
        observed["schema"] = first[2:] if first.startswith("# ") else ""
        for line in handle:
            if not line.startswith("# "):
                break
            payload = line[2:].rstrip("\r\n")
            if ": " in payload:
                key, value = payload.split(": ", 1)
                observed[key] = value
    if any(not value for value in expected.values()) or any(
        observed.get(key) != value for key, value in expected.items()
    ):
        raise ExportError(
            "tracked evidence-register header does not match current_re_authority"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--campaign", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--expected-ready-sha256")
    parser.add_argument("--expected-reducer-id")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-header-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.check_header_only:
            if args.state is None or args.check or any(
                value is not None
                for value in (
                    args.campaign,
                    args.out,
                    args.expected_ready_sha256,
                    args.expected_reducer_id,
                )
            ):
                raise ExportError(
                    "--check-header-only requires only --state"
                )
            _campaign_root, output, _ready_sha256, _reducer_id = resolve_state(
                args.state
            )
            check_state_header(args.state, output)
            print(f"EVIDENCE_REGISTER_HEADER_CURRENT path={output}")
            return 0
        if args.state is not None:
            if any(
                value is not None
                for value in (
                    args.campaign,
                    args.out,
                    args.expected_ready_sha256,
                    args.expected_reducer_id,
                )
            ):
                raise ExportError("--state cannot be combined with direct authority arguments")
            campaign_root, output, ready_sha256, reducer_id = resolve_state(args.state)
        else:
            if not all(
                (
                    args.campaign,
                    args.out,
                    args.expected_ready_sha256,
                    args.expected_reducer_id,
                )
            ):
                raise ExportError(
                    "explicit --campaign, --out, --expected-ready-sha256, and "
                    "--expected-reducer-id are required"
                )
            campaign_root = args.campaign
            output = args.out
            ready_sha256 = args.expected_ready_sha256
            reducer_id = args.expected_reducer_id
        result = build(
            campaign_root,
            expected_ready_sha256=str(ready_sha256),
            expected_reducer_id=str(reducer_id),
        )
        rendered = render(result)
        if args.check:
            if not output.is_file() or output.read_bytes() != rendered.encode("utf-8"):
                raise ExportError(f"tracked evidence register is stale or missing: {output}")
            print(f"EVIDENCE_REGISTER_CURRENT rows={len(result['rows'])} path={output}")
            return 0
        atomic_write(output, rendered)
        print(f"EVIDENCE_REGISTER_READY rows={len(result['rows'])} path={output}")
        return 0
    except (ExportError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"EVIDENCE_REGISTER_REFUSED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
