#!/usr/bin/env python3
"""Produce timestamped CDB evidence logs for future music audible proof.

This producer does not launch BEA, attach CDB, tail a live process, capture
audio, or claim audible output. It converts an explicit trusted observation
ledger into a timestamped CDB evidence log and validates that the log can feed
the existing music CDB timeline sidecar.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_music_audible_output_materializer as materializer


SCHEMA = "winui-safe-copy-timestamped-cdb-log.v1"
OBSERVATION_SCHEMA = "winui-safe-copy-timestamped-cdb-log-observations.v1"
TIMESTAMP_SOURCE = "trusted-tail-wrapper-observation-ledger"
REPARSE_POINT_ATTRIBUTE = 0x400
ROLES = {"cleanBaseline", "stagedPositive"}
NON_CLAIMS = [
    "not audible-output proof",
    "not a BEA launch",
    "not a CDB attach",
    "not a loopback capture",
    "not online proof",
    "not gameplay parity",
    "not rebuild parity",
    "not no-noticeable-difference parity",
]


class TimestampedCdbLogProducerError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TimestampedCdbLogProducerError(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"Missing JSON input: {path}")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(payload, dict), f"JSON input must be an object: {path}")
    return payload


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def lexical_candidates(path: Path) -> list[Path]:
    absolute = Path(os.path.abspath(path))
    if not absolute.parts:
        return []
    current = Path(absolute.anchor)
    candidates = [current]
    for part in absolute.parts[1:]:
        current = current / part
        candidates.append(current)
    return candidates


def validate_no_reparse_lexical(path: Path) -> None:
    for candidate in lexical_candidates(path):
        try:
            stats = candidate.lstat()
        except FileNotFoundError:
            continue
        if candidate.is_symlink():
            raise TimestampedCdbLogProducerError(f"Refusing symlinked CDB timestamp producer path: {candidate}")
        attrs = getattr(stats, "st_file_attributes", 0)
        if attrs & REPARSE_POINT_ATTRIBUTE:
            raise TimestampedCdbLogProducerError(f"Refusing reparse-point CDB timestamp producer path: {candidate}")


def parse_utc(value: Any, label: str) -> dt.datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} must be a UTC Z timestamp.")
    try:
        parsed = dt.datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise TimestampedCdbLogProducerError(f"{label} is not a valid UTC timestamp.") from exc
    return parsed.astimezone(dt.timezone.utc)


def format_utc(value: dt.datetime) -> str:
    value = value.astimezone(dt.timezone.utc)
    if value.microsecond:
        text = value.isoformat(timespec="milliseconds")
    else:
        text = value.isoformat(timespec="seconds")
    return text.replace("+00:00", "Z")


def validate_role(role: str) -> None:
    require(role in ROLES, f"Role must be one of: {', '.join(sorted(ROLES))}.")


def validate_no_symlink_or_reparse(path: Path) -> None:
    validate_no_reparse_lexical(path)
    try:
        materializer.validate_no_symlink_or_reparse(path)
    except materializer.MaterializerError as exc:
        raise TimestampedCdbLogProducerError(str(exc)) from exc


def validate_output_paths(
    *,
    timestamped_log_output: Path,
    receipt_output: Path,
    allowed_output_root: Path,
    allow_overwrite: bool,
) -> None:
    allowed_output_root.mkdir(parents=True, exist_ok=True)
    validate_no_symlink_or_reparse(allowed_output_root)
    validate_no_symlink_or_reparse(timestamped_log_output.parent)
    validate_no_symlink_or_reparse(receipt_output.parent)
    require(is_relative_to(timestamped_log_output, allowed_output_root), "Timestamped CDB log output must stay under the allowed output root.")
    require(is_relative_to(receipt_output, allowed_output_root), "Timestamped CDB log receipt must stay under the allowed output root.")
    require(timestamped_log_output.suffix.lower() == ".log", "Timestamped CDB log output must end in .log.")
    require(receipt_output.suffix.lower() == ".json", "Timestamped CDB log receipt must end in .json.")
    require(timestamped_log_output.resolve() != receipt_output.resolve(), "Timestamped log and receipt outputs must be different files.")
    require(not timestamped_log_output.exists() or allow_overwrite, "Timestamped CDB log output already exists; use --allow-overwrite.")
    require(not receipt_output.exists() or allow_overwrite, "Timestamped CDB receipt already exists; use --allow-overwrite.")


def validate_raw_log(raw_cdb_log: Path) -> list[str]:
    require(raw_cdb_log.is_file(), "Raw CDB log is missing.")
    validate_no_symlink_or_reparse(raw_cdb_log)
    lines = raw_cdb_log.read_text(encoding="utf-8", errors="replace").splitlines()
    require(lines, "Raw CDB log is empty.")
    for index, line in enumerate(lines):
        try:
            has_timestamp = materializer.parse_timestamped_line(line) is not None
        except materializer.MaterializerError as exc:
            raise TimestampedCdbLogProducerError(str(exc)) from exc
        require(not has_timestamp, f"Raw CDB log line {index} is already timestamped.")
    return lines


def validate_observation_ledger(
    *,
    ledger: dict[str, Any],
    raw_log: Path,
    raw_lines: list[str],
    role: str,
) -> list[dict[str, Any]]:
    require(ledger.get("schemaVersion") == OBSERVATION_SCHEMA, "Timestamp observation ledger schema changed.")
    require(ledger.get("role") == role, "Timestamp observation ledger role mismatch.")
    require(ledger.get("timestampSource") == TIMESTAMP_SOURCE, "Timestamp observation ledger source changed.")
    require(str(ledger.get("rawCdbLogSha256", "")).lower() == sha256_file(raw_log), "Timestamp observation ledger is not bound to the raw CDB log.")
    observations = ledger.get("observations")
    require(isinstance(observations, list) and observations, "Timestamp observation rows are missing.")

    parsed_rows: list[dict[str, Any]] = []
    seen_indexes: set[int] = set()
    previous_at: dt.datetime | None = None
    for row_index, row in enumerate(observations):
        require(isinstance(row, dict), f"Observation row {row_index} must be an object.")
        line_index = row.get("lineIndex")
        require(isinstance(line_index, int), f"Observation row {row_index} lineIndex must be an integer.")
        require(0 <= line_index < len(raw_lines), f"Observation row {row_index} lineIndex is outside the raw CDB log.")
        require(line_index not in seen_indexes, f"Duplicate timestamp observation for raw CDB line {line_index}.")
        seen_indexes.add(line_index)
        expected_hash = sha256_text(raw_lines[line_index])
        require(str(row.get("lineSha256", "")).lower() == expected_hash, f"Observation row {row_index} does not match raw CDB line hash.")
        observed_at = parse_utc(row.get("observedAtUtc"), f"observations[{row_index}].observedAtUtc")
        if previous_at is not None:
            require(observed_at >= previous_at, "Timestamp observation rows must be nondecreasing.")
        previous_at = observed_at
        parsed_rows.append({"lineIndex": line_index, "observedAt": observed_at, "rawLine": raw_lines[line_index]})
    return parsed_rows


def build_timestamped_lines(rows: list[dict[str, Any]]) -> list[str]:
    return [f"{format_utc(row['observedAt'])} {row['rawLine']}" for row in sorted(rows, key=lambda item: item["lineIndex"])]


def parse_timestamped_log_text(timestamped_text: str, temp_parent: Path) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".log", dir=temp_parent, delete=False) as handle:
        temp_path = Path(handle.name)
        handle.write(timestamped_text)
    try:
        return materializer.parse_cdb_log(temp_path)
    except materializer.MaterializerError as exc:
        raise TimestampedCdbLogProducerError(str(exc)) from exc
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def receipt_payload(
    *,
    role: str,
    raw_cdb_log: Path,
    timestamped_log_output: Path,
    parsed: dict[str, Any],
    timestamped_line_count: int,
    raw_line_count: int,
) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA,
        "role": role,
        "timestampSource": TIMESTAMP_SOURCE,
        "cdbLogTimestamped": True,
        "runtimeAudibleOutputProof": False,
        "rawCdbLogSha256": sha256_file(raw_cdb_log),
        "timestampedCdbLogSha256": sha256_file(timestamped_log_output),
        "cdbLogSha256": sha256_file(timestamped_log_output),
        "rawLineCount": raw_line_count,
        "timestampedLineCount": timestamped_line_count,
        "decodeWindowStartUtc": format_utc(parsed["firstEvidenceAt"]),
        "decodeWindowEndUtc": format_utc(parsed["lastEvidenceAt"]),
        "cdbEvidenceRowCounts": {
            "gameMusicRows": parsed["gameMusicRows"],
            "playSelectionRows": parsed["playSelectionRows"],
            "asyncKickRows": parsed["asyncKickRows"],
            "oggOpenRows": parsed["oggOpenRows"],
            "oggReadRows": parsed["oggReadRows"],
        },
        "claimBoundary": "Timestamped CDB evidence log producer only; not runtime audible-output proof.",
        "nonClaims": NON_CLAIMS,
    }


def validate_receipt(payload: dict[str, Any], *, timestamped_log: Path | None = None) -> dict[str, Any]:
    require(payload.get("schemaVersion") == SCHEMA, "Timestamped CDB log receipt schema changed.")
    role = str(payload.get("role", ""))
    validate_role(role)
    require(payload.get("timestampSource") == TIMESTAMP_SOURCE, "Timestamped CDB log receipt source changed.")
    require(payload.get("cdbLogTimestamped") is True, "Receipt must assert timestamped CDB log output.")
    require(payload.get("runtimeAudibleOutputProof") is False, "Receipt must not claim runtime audible-output proof.")
    for key in ("rawCdbLogSha256", "timestampedCdbLogSha256", "cdbLogSha256"):
        value = str(payload.get(key, ""))
        require(bool(re.fullmatch(r"[0-9a-fA-F]{64}", value)), f"{key} must be a SHA-256 hex string.")
    require(payload.get("timestampedCdbLogSha256") == payload.get("cdbLogSha256"), "cdbLogSha256 must bind the timestamped evidence log.")
    if timestamped_log is not None:
        require(sha256_file(timestamped_log) == payload.get("timestampedCdbLogSha256"), "Receipt is not bound to the timestamped CDB log.")
    require(isinstance(payload.get("rawLineCount"), int) and payload["rawLineCount"] > 0, "rawLineCount must be positive.")
    require(isinstance(payload.get("timestampedLineCount"), int) and payload["timestampedLineCount"] > 0, "timestampedLineCount must be positive.")
    start = parse_utc(payload.get("decodeWindowStartUtc"), "decodeWindowStartUtc")
    end = parse_utc(payload.get("decodeWindowEndUtc"), "decodeWindowEndUtc")
    require(start <= end, "Receipt decode window is inverted.")
    return {
        "schemaVersion": SCHEMA,
        "role": role,
        "cdbLogTimestamped": True,
        "runtimeAudibleOutputProof": False,
        "timestampedLineCount": payload["timestampedLineCount"],
    }


def build_timestamped_log_from_paths(
    *,
    raw_cdb_log: Path,
    observation_ledger: Path,
    timestamped_log_output: Path,
    receipt_output: Path,
    allowed_output_root: Path,
    role: str,
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    validate_role(role)
    validate_output_paths(
        timestamped_log_output=timestamped_log_output,
        receipt_output=receipt_output,
        allowed_output_root=allowed_output_root,
        allow_overwrite=allow_overwrite,
    )
    raw_lines = validate_raw_log(raw_cdb_log)
    require(timestamped_log_output.resolve() != raw_cdb_log.resolve(), "Timestamped CDB log output must not overwrite the raw CDB log.")
    require(receipt_output.resolve() != raw_cdb_log.resolve(), "Timestamped CDB receipt must not overwrite the raw CDB log.")
    require(receipt_output.resolve() != observation_ledger.resolve(), "Timestamped CDB receipt must not overwrite the observation ledger.")
    validate_no_symlink_or_reparse(observation_ledger)
    observed_rows = validate_observation_ledger(
        ledger=read_json(observation_ledger),
        raw_log=raw_cdb_log,
        raw_lines=raw_lines,
        role=role,
    )
    timestamped_text = "\n".join(build_timestamped_lines(observed_rows)) + "\n"
    parsed = parse_timestamped_log_text(timestamped_text, allowed_output_root)

    write_text(timestamped_log_output, timestamped_text)
    payload = receipt_payload(
        role=role,
        raw_cdb_log=raw_cdb_log,
        timestamped_log_output=timestamped_log_output,
        parsed=parsed,
        timestamped_line_count=len(observed_rows),
        raw_line_count=len(raw_lines),
    )
    write_json(receipt_output, payload)
    validate_receipt(payload, timestamped_log=timestamped_log_output)
    return payload


def self_test() -> None:
    import winui_safe_copy_music_audible_output_materializer_test as fixtures

    with tempfile.TemporaryDirectory(prefix="timestamped-cdb-log-producer-") as temp_dir:
        root = Path(temp_dir)
        raw_log = root / "clean" / "windbg.log"
        raw_log.parent.mkdir(parents=True)
        raw_log.write_text(fixtures.untimestamped_log_text(), encoding="utf-8")
        raw_lines = raw_log.read_text(encoding="utf-8").splitlines()
        base = dt.datetime(2026, 6, 24, 1, 2, 3, tzinfo=dt.timezone.utc)
        ledger = {
            "schemaVersion": OBSERVATION_SCHEMA,
            "role": "cleanBaseline",
            "timestampSource": TIMESTAMP_SOURCE,
            "rawCdbLogSha256": sha256_file(raw_log),
            "observations": [
                {
                    "lineIndex": index,
                    "lineSha256": sha256_text(line),
                    "observedAtUtc": format_utc(base + dt.timedelta(milliseconds=index * 100)),
                }
                for index, line in enumerate(raw_lines)
            ],
        }
        ledger_path = root / "clean" / "timestamp-ledger.json"
        write_json(ledger_path, ledger)
        summary = build_timestamped_log_from_paths(
            raw_cdb_log=raw_log,
            observation_ledger=ledger_path,
            timestamped_log_output=root / "out" / "clean" / "windbg.timestamped.log",
            receipt_output=root / "out" / "clean" / "timestamped-cdb-log-receipt.json",
            allowed_output_root=root / "out",
            role="cleanBaseline",
        )
        validate_receipt(summary, timestamped_log=root / "out" / "clean" / "windbg.timestamped.log")


def sanitize_error_message(message: str) -> str:
    return materializer.sanitize_error_message(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-cdb-log", type=Path)
    parser.add_argument("--observation-ledger", type=Path)
    parser.add_argument("--timestamped-log-output", type=Path)
    parser.add_argument("--receipt-output", type=Path)
    parser.add_argument("--allowed-output-root", type=Path)
    parser.add_argument("--role", default="")
    parser.add_argument("--check-receipt", type=Path)
    parser.add_argument("--timestamped-log", type=Path)
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI safe-copy music timestamped CDB log producer self-test: PASS")
            return 0
        if args.check_receipt:
            payload = read_json(args.check_receipt)
            print(json.dumps(validate_receipt(payload, timestamped_log=args.timestamped_log), indent=2, sort_keys=True))
            return 0
        require(args.raw_cdb_log is not None, "Provide --raw-cdb-log.")
        require(args.observation_ledger is not None, "Provide --observation-ledger.")
        require(args.timestamped_log_output is not None, "Provide --timestamped-log-output.")
        require(args.receipt_output is not None, "Provide --receipt-output.")
        require(args.allowed_output_root is not None, "Provide --allowed-output-root.")
        require(bool(args.role), "Provide --role.")
        payload = build_timestamped_log_from_paths(
            raw_cdb_log=args.raw_cdb_log,
            observation_ledger=args.observation_ledger,
            timestamped_log_output=args.timestamped_log_output,
            receipt_output=args.receipt_output,
            allowed_output_root=args.allowed_output_root,
            role=args.role,
            allow_overwrite=args.allow_overwrite,
        )
        print(json.dumps(validate_receipt(payload, timestamped_log=args.timestamped_log_output), indent=2, sort_keys=True))
        return 0
    except (TimestampedCdbLogProducerError, materializer.MaterializerError) as exc:
        print(f"WinUI safe-copy music timestamped CDB log producer: FAIL: {sanitize_error_message(str(exc))}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
