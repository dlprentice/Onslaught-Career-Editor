#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build and verify an exact source/compiled/runtime Mission logger census.

The dormant retail logger can transport Mission values, but source presence,
compiled CALL presence, and runtime handler coverage are different evidence.
This owner preserves those layers separately, binds every canonical input by
content, and emits three explicit level-ranking heuristics rather than one
ambiguous "harvest" score.
"""

from __future__ import annotations

import argparse
import capstone
from capstone.x86 import X86_INS_CALL, X86_INS_PUSH, X86_OP_IMM, X86_OP_MEM, X86_OP_REG
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import stat
import struct
import sys
import tempfile
from typing import Iterable, Sequence
import warnings


SCHEMA = "bea.re.msl-logger-census.v2"
READY_SCHEMA = "bea.re.msl-logger-census-ready.v2"
COVERAGE_READY_SCHEMA = "bea.re.coverage-ledger-ready.v1"
PARITY_READY_SCHEMA = "bea-ghidra-parity-graph-receipt.v2"
STATUS = "READY"

EXPECTED_SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EXPECTED_SPECIMEN_MD5 = "3b456964020070efe696d2cc09464a55"
EXPECTED_CORPUS_MANIFEST_SHA256 = "7e3de28072993db743ca888e5b8cd6d82552c5db32c25f8ef4eb83387f6b3d60"
EXPECTED_CORPUS_FILES = 733
EXPECTED_NATIVE_TABLE_SHA256 = "ca4c0f64efe86f7a48c0469988d6ae67d17dfc132358b9096d28f47cb894f61e"
EXPECTED_COVERAGE_READY_SHA256 = "4d16b3a8aeb7b001f8c1bf6bcd4e6b31bcc6b00105e45e1e556cf8c2e30e83b6"
EXPECTED_COVERAGE_SUMMARY_SHA256 = "dbdf4daeae0294685f7b330eff334402570b667e777cc48e1532d83e8e5aeb67"
EXPECTED_COVERAGE_NATIVE_SHA256 = "163d2842df4e808fcbe3744b075a1b2b905f7c6412af35ca68bfd32fdc74c220"
EXPECTED_COVERAGE_SET_SHA256 = "74c2dfee06fcbf6ad538d155d91087b70c10e5b7c9ac507dac40cf3a00d599b4"
EXPECTED_RUNTIME_TARGET_SHA256 = "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
EXPECTED_RESOURCE_MANIFEST_SHA256 = "4614a9a5b33b018879d7a14da83cb6229cf66280572001e051082dea522365a4"
EXPECTED_RESOURCE_ARCHIVES = 301
EXPECTED_COMPILED_PROFILE_SHA256 = "b1e0643d5e76d3aad7e82ca68cb5bd1e5f8e984cab5a988981b79fbc6604edd4"
EXPECTED_COMPILED_WORLDS = 115
EXPECTED_COMPILED_CALLS = 9236
EXPECTED_COMPILED_NATIVES = 108
EXPECTED_PARITY_READY_SHA256 = "2954adf2702d195e1a4adb59cb759afea8e9037628d5dbdce04ca34dd1da6fb1"
EXPECTED_BODY_RANGES_SHA256 = "a863f0447d80b2dc069387d91be893673e01b6cb2d1feddab6a123bde4f11c5a"
EXPECTED_DIRECT_CALLS_SHA256 = "42d1bb60ab631289c47afefda1a12a601e4549b47c868022ac12ea14bdade8e0"
EXPECTED_PRINT_BODY_SHA256 = "60606dd5ad10ccd7d43cbe3c45f19ec9a6098527f1c165e00d27903c662fa9fd"
CAPSTONE_VERSION = "5.0.7"
CONSOLE_PRINTF_VA = 0x00441740
DORMANT_LOGGER_RECEIVER_VA = 0x0066F580
SETUPHISTORY_RECEIVER_VA = 0x0066EB90
EXPECTED_CONSOLE_RAW_CALLS = 380
EXPECTED_CONSOLE_MAPPED_CALLS = 377
EXPECTED_CONSOLE_MAPPED_CALLERS = 175
EXPECTED_DORMANT_RECEIVER_CALLS = 253
EXPECTED_SETUPHISTORY_RECEIVER_CALLS = 127
UNMAPPED_CONSOLE_SITES = {
    0x004F22FA: {
        "decodeStart": 0x004F22E8, "candidateOwnerAddress": 0x004F21F0,
        "candidateOwnerName": "CText__Init", "formatVa": 0x00632DF4,
        "format": "ERROR: Can't open text file %s",
    },
    0x005351F0: {
        "decodeStart": 0x005351D0, "candidateOwnerAddress": 0x005351D0,
        "candidateOwnerName": "PlayAnimationWait", "formatVa": 0x0064FB64,
        "format": "FATAL ERROR: Called PlayAnimWait on the non base script object",
    },
    0x00536BA9: {
        "decodeStart": 0x00536B70, "candidateOwnerAddress": 0x00536B70,
        "candidateOwnerName": "SpawnParticle", "formatVa": 0x0064FD04,
        "format": "Can't find particle effect %s",
    },
}

COVERAGE_FILES = (
    "ledger-summary.json", "ledger-functions.tsv", "ledger-dark.tsv",
    "ledger-gaps.tsv", "ledger-unmapped.tsv", "ledger-native-handlers.tsv",
    "ledger-families.tsv",
)
PARSER_PINS = {
    "tools/probe/probe_author.py": "4bd5046a280fa94bde46982e4b1bc8de3d3079875ddad50a1a668f550caa44fe",
    "tools/probe/bea_lab.py": "d820238ab4ab623234f5d878d8b9e7b2d3b330e7a2f3d540b7f1589f4d9785d0",
    "tools/probe/mission_script_emitter.py": "9866a1e007c6da08af57b19c568ac36f0f9314d4da64c52d035c6cf07af6d964",
    "local-lab/aya_roundtrip.py": "0b4194c98dcd5929ad8978758c011255c62344d3d6d9706d8c633640adb294b9",
    "local-lab/msl/script_parse.py": "a53288ba9ee20d22df6dcfe5b063899dd24305354025409ac6ca5d36858d7899",
    "local-lab/msl/bea_aya.py": "ac6700ddd675b2cdb49a324d9a9e70046e339b3793dfd5a0293c091d283b0a2a",
}

OUTPUTS = (
    "msl-logger-census-owner.py", "corpus-files.tsv", "resource-archives.tsv",
    "native-calls.tsv", "print-calls.tsv", "compiled-native-profile.tsv",
    "native-summary.tsv", "level-summary.tsv", "print-dispatch-static.json",
    "console-printf-callsites.tsv", "console-printf-mapped-callers.tsv",
    "census-summary.json",
)
CORPUS_COLUMNS = ("relativePath", "levelKey", "bytes", "sha256")
RESOURCE_COLUMNS = ("relativePath", "levelKey", "bytes", "sha256")
CALL_COLUMNS = (
    "callKey", "relativePath", "levelKey", "line", "column", "scopeKind",
    "scopeName", "nativeIndex", "nativeName", "handlerVa", "argumentKind",
    "argumentText", "argumentBytes", "argumentSha256",
)
PRINT_COLUMNS = (
    "callKey", "relativePath", "levelKey", "line", "column", "scopeKind",
    "scopeName", "argumentKind", "literalValueJson", "argumentText",
    "argumentBytes", "argumentSha256",
)
COMPILED_COLUMNS = (
    "nativeIndex", "nativeName", "compiledCallCount", "compiledArchiveCount",
    "compiledLevelArchiveCount", "callProfilesJson",
)
NATIVE_COLUMNS = (
    "nativeIndex", "nativeName", "handlerVa", "sourceCallCount", "sourceFileCount",
    "sourceLevelCount", "compiledCallCount", "compiledArchiveCount",
    "compiledLevelArchiveCount", "initCallCount", "gamePlayingCallCount",
    "eventCallCount", "actorHandlerCallCount", "topLevelCallCount",
    "coverageObserved", "sourcePresenceCoverageClass",
    "compiledPresenceCoverageClass",
)
LEVEL_COLUMNS = (
    "levelKey", "runnableArchive", "resourceArchive", "resourceArchiveSha256",
    "fileCount", "sourceNativeCallCount", "sourceDistinctNativeCount",
    "compiledNativeCallCount", "compiledDistinctNativeCount",
    "compiledFrontierNativeCount", "compiledFrontierCallCount", "printCallCount",
    "literalPrintCount", "expressionPrintCount", "initPrintCount",
    "gamePlayingPrintCount", "eventPrintCount", "actorHandlerPrintCount",
    "topLevelPrintCount", "stockEarlyExpressionPrintCount",
    "stockEarlyLiteralPrintCount", "initExpressionPrintCount", "stockObservabilityWindow",
    "stockObservabilityRank", "stimulusExpressionPrintCount",
    "stimulusLiteralPrintCount", "authoredStimulusWindow",
    "authoredStimulusRank", "nativeCoverageRank",
)
MAPPED_CALLER_COLUMNS = ("callerAddress", "callerName", "callSiteCount")
CALLSITE_COLUMNS = (
    "callSiteVa", "receiverPushVa", "receiverVa", "receiverChannel",
    "mappingState", "mappedCallerAddress", "mappedCallerName", "rangeOrdinal",
    "candidateOwnerAddress", "candidateOwnerName", "formatPushVa",
    "formatOperandKind", "formatOperandText", "formatImmediateVa", "formatString",
)

IDENT_START = re.compile(r"[A-Za-z_]")
IDENT_CONTINUE = re.compile(r"[A-Za-z0-9_]")
LEVEL_RE = re.compile(r"(?i)^level(\d{3})$")
ARCHIVE_LEVEL_RE = re.compile(r"(?i)^(\d{3})_res_PC\.aya$")


class CensusError(ValueError):
    """An input or published bundle violates the census contract."""


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    start: int
    end: int
    line: int
    column: int


@dataclass(frozen=True)
class Scope:
    kind: str
    name: str
    first_token: int
    last_token: int


@dataclass(frozen=True)
class Inputs:
    repo: Path
    evidence_repo: Path
    msl_root: Path
    resources: Path
    native_table: Path
    coverage_ledger: Path
    specimen: Path
    parity_ready: Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_equal(label: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise CensusError(f"{label} mismatch: got {actual!r}, expected {expected!r}")


def validate_corpus_pin(manifest_sha256: str, file_count: int) -> None:
    """Reject same-count source drift; counts are never an identity."""
    require_equal("source corpus file count", file_count, EXPECTED_CORPUS_FILES)
    require_equal("source corpus manifest pin", manifest_sha256, EXPECTED_CORPUS_MANIFEST_SHA256)


def validate_compiled_pins(identity: dict[str, object]) -> None:
    """Reject archive/profile drift even when aggregate counts are unchanged."""
    require_equal("resource archive count", identity["archiveCount"], EXPECTED_RESOURCE_ARCHIVES)
    require_equal("resource manifest pin", identity["resourceManifestSha256"], EXPECTED_RESOURCE_MANIFEST_SHA256)
    require_equal("compiled world count", identity["worldChunkCount"], EXPECTED_COMPILED_WORLDS)
    require_equal("compiled CALL count", identity["compiledCallCount"], EXPECTED_COMPILED_CALLS)
    require_equal("compiled used native count", identity["compiledUsedNatives"], EXPECTED_COMPILED_NATIVES)
    require_equal("compiled profile pin", identity["compiledProfileSha256"], EXPECTED_COMPILED_PROFILE_SHA256)


def find_repo(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / "developer_state.json").is_file() and (candidate / "tools").is_dir():
            return candidate
    raise CensusError(f"repository root not found above {start}")


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def is_linklike(path: Path) -> bool:
    """Identify symlinks, junctions, and other Windows reparse points."""
    if path.is_symlink():
        return True
    junction = getattr(path, "is_junction", None)
    if junction is not None and junction():
        return True
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def validate_bundle_tree(bundle: Path) -> None:
    if not bundle.is_dir() or is_linklike(bundle):
        raise CensusError(f"bundle is not a plain directory or is a reparse point: {bundle}")
    actual_names = {path.name for path in bundle.iterdir()}
    expected_names = set(OUTPUTS) | {"READY.json"}
    if actual_names != expected_names:
        raise CensusError(
            f"bundle members differ: missing={sorted(expected_names - actual_names)} "
            f"extra={sorted(actual_names - expected_names)}"
        )
    for path in bundle.iterdir():
        if not path.is_file() or is_linklike(path):
            raise CensusError(f"bundle member is not a plain file: {path.name}")


def render_tsv(columns: Sequence[str], rows: Iterable[dict[str, object]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer, fieldnames=list(columns), delimiter="\t", lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column, "") for column in columns})
    return buffer.getvalue().encode("utf-8")


def lex_msl(text: str, source: str = "<memory>") -> list[Token]:
    """Return code tokens, excluding comments and string contents."""
    tokens: list[Token] = []
    index = 0
    line = 1
    column = 1

    def advance(character: str) -> None:
        nonlocal line, column
        if character == "\n":
            line, column = line + 1, 1
        else:
            column += 1

    while index < len(text):
        character = text[index]
        if character.isspace():
            advance(character); index += 1; continue
        if text.startswith("//", index):
            while index < len(text) and text[index] != "\n":
                advance(text[index]); index += 1
            continue
        if text.startswith("/*", index):
            start_line, start_column = line, column
            advance("/"); advance("*"); index += 2
            while index < len(text) and not text.startswith("*/", index):
                advance(text[index]); index += 1
            if index >= len(text):
                raise CensusError(f"{source}:{start_line}:{start_column}: unterminated block comment")
            advance("*"); advance("/"); index += 2; continue
        start, start_line, start_column = index, line, column
        if character == '"':
            advance(character); index += 1; escaped = False
            while index < len(text):
                current = text[index]
                if not escaped and current == '"':
                    advance(current); index += 1
                    tokens.append(Token("string", text[start:index], start, index, start_line, start_column))
                    break
                if not escaped and current in "\r\n":
                    raise CensusError(f"{source}:{start_line}:{start_column}: newline in string literal")
                escaped = current == "\\" and not escaped
                if current != "\\": escaped = False
                advance(current); index += 1
            else:
                raise CensusError(f"{source}:{start_line}:{start_column}: unterminated string literal")
            continue
        if IDENT_START.match(character):
            index += 1; advance(character)
            while index < len(text) and IDENT_CONTINUE.match(text[index]):
                advance(text[index]); index += 1
            tokens.append(Token("identifier", text[start:index], start, index, start_line, start_column)); continue
        if character.isdigit() or (character == "." and index + 1 < len(text) and text[index + 1].isdigit()):
            if character == "0" and index + 1 < len(text) and text[index + 1] in "xX":
                advance(text[index]); advance(text[index + 1]); index += 2
                while index < len(text) and (text[index].isdigit() or text[index].lower() in "abcdef" or text[index] == "_"):
                    advance(text[index]); index += 1
            else:
                if character == ".": advance(character); index += 1
                while index < len(text) and (text[index].isdigit() or text[index] == "_"):
                    advance(text[index]); index += 1
                if index < len(text) and text[index] == ".":
                    advance(text[index]); index += 1
                    while index < len(text) and (text[index].isdigit() or text[index] == "_"):
                        advance(text[index]); index += 1
                if index < len(text) and text[index] in "eE":
                    advance(text[index]); index += 1
                    if index < len(text) and text[index] in "+-": advance(text[index]); index += 1
                    exponent_start = index
                    while index < len(text) and (text[index].isdigit() or text[index] == "_"):
                        advance(text[index]); index += 1
                    if index == exponent_start:
                        raise CensusError(f"{source}:{start_line}:{start_column}: malformed numeric exponent")
            tokens.append(Token("number", text[start:index], start, index, start_line, start_column)); continue
        index += 1; advance(character)
        tokens.append(Token("symbol", character, start, index, start_line, start_column))
    return tokens


def matching_token(tokens: Sequence[Token], start: int, opening: str, closing: str) -> int:
    if start >= len(tokens) or tokens[start].value != opening:
        raise CensusError(f"expected {opening!r} at token {start}")
    depth = 0
    for index in range(start, len(tokens)):
        if tokens[index].value == opening: depth += 1
        elif tokens[index].value == closing:
            depth -= 1
            if depth == 0: return index
    raise CensusError(f"unmatched {opening!r} at line {tokens[start].line}")


def discover_scopes(tokens: Sequence[Token]) -> list[Scope]:
    depths: list[int] = []
    depth = 0
    for token in tokens:
        depths.append(depth)
        if token.value == "{": depth += 1
        elif token.value == "}":
            depth -= 1
            if depth < 0: raise CensusError(f"unmatched closing brace at line {token.line}")
    if depth: raise CensusError("unmatched opening brace")
    scopes: list[Scope] = []
    for index, token in enumerate(tokens):
        if token.kind != "identifier" or depths[index] != 0: continue
        if index + 1 >= len(tokens) or tokens[index + 1].value != "(": continue
        close_paren = matching_token(tokens, index + 1, "(", ")")
        if close_paren + 1 >= len(tokens) or tokens[close_paren + 1].value != "{": continue
        close_brace = matching_token(tokens, close_paren + 1, "{", "}")
        if token.value.casefold() == "init": kind, name = "init", "init"
        elif token.value.casefold() == "event":
            arguments = tokens[index + 2:close_paren]
            kind = "event"
            name = arguments[0].value[1:-1] if len(arguments) == 1 and arguments[0].kind == "string" else "<expression>"
        else: kind, name = "actor-handler", token.value
        scopes.append(Scope(kind, name, close_paren + 2, close_brace - 1))
    return scopes


def scope_for(index: int, scopes: Sequence[Scope]) -> tuple[str, str]:
    for scope in scopes:
        if scope.first_token <= index <= scope.last_token: return scope.kind, scope.name
    return "top-level", "<top-level>"


def level_key(relative_path: str) -> str:
    first = relative_path.replace("\\", "/").split("/", 1)[0]
    match = LEVEL_RE.fullmatch(first)
    return match.group(1) if match else "ROOT"


def decode_string_literal(raw: str) -> str:
    body = raw[1:-1]
    output: list[str] = []
    replacements = {"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\"}
    index = 0
    while index < len(body):
        if body[index] == "\\" and index + 1 < len(body):
            following = body[index + 1]
            output.append(replacements.get(following, "\\" + following)); index += 2
        else: output.append(body[index]); index += 1
    return "".join(output)


def parse_file_calls(text: str, relative_path: str, registry_by_name: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    tokens = lex_msl(text, relative_path)
    scopes = discover_scopes(tokens)
    rows: list[dict[str, object]] = []
    for index, token in enumerate(tokens[:-1]):
        native = registry_by_name.get(token.value)
        if native is None or tokens[index + 1].value != "(": continue
        close = matching_token(tokens, index + 1, "(", ")")
        argument = text[tokens[index + 1].end:tokens[close].start].strip()
        argument_tokens = tokens[index + 2:close]
        if len(argument_tokens) == 1 and argument_tokens[0].kind == "string":
            argument_kind = "literal-string"; literal = decode_string_literal(argument_tokens[0].value)
        elif not argument_tokens: argument_kind, literal = "empty", ""
        else: argument_kind, literal = "expression", ""
        scope_kind, scope_name = scope_for(index, scopes)
        native_index = int(native["index"])
        encoded = argument.encode("utf-8")
        rows.append({
            "callKey": f"msl:{relative_path}:{token.line}:{token.column}:{native_index}",
            "relativePath": relative_path, "levelKey": level_key(relative_path),
            "line": token.line, "column": token.column, "scopeKind": scope_kind,
            "scopeName": scope_name, "nativeIndex": native_index, "nativeName": token.value,
            "handlerVa": f"0x{int(native['handler']):08x}", "argumentKind": argument_kind,
            "literalValueJson": json.dumps(literal, ensure_ascii=False) if argument_kind == "literal-string" else "",
            "argumentText": argument, "argumentBytes": len(encoded), "argumentSha256": sha256_bytes(encoded),
        })
    return rows


def load_registry(path: Path) -> list[dict[str, object]]:
    try: raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CensusError(f"invalid native registry {path}: {error}") from error
    if not isinstance(raw, list) or len(raw) != 144:
        raise CensusError("native registry must contain exactly 144 rows")
    rows: list[dict[str, object]] = []
    names: set[str] = set()
    for expected, row in enumerate(raw):
        if not isinstance(row, dict) or row.get("i") != expected or not isinstance(row.get("name"), str) or not isinstance(row.get("handler"), int):
            raise CensusError(f"native registry row {expected} has invalid index/name/handler")
        name = str(row["name"])
        if name in names: raise CensusError(f"duplicate native name {name}")
        names.add(name)
        rows.append({"index": expected, "name": name, "handler": int(row["handler"])})
    return rows


def read_native_coverage(path: Path, registry: Sequence[dict[str, object]]) -> dict[int, bool]:
    lines = path.read_text(encoding="utf-8").splitlines()
    reader = csv.DictReader(io.StringIO("\n".join(line for line in lines if not line.startswith("#")) + "\n"), delimiter="\t")
    required = {"index", "handlerVa", "shippedName", "observed"}
    if reader.fieldnames is None or not required.issubset(reader.fieldnames):
        raise CensusError(f"coverage ledger has wrong header: {reader.fieldnames}")
    observed: dict[int, bool] = {}
    for source in reader:
        index = int(source["index"])
        if index < 0 or index >= len(registry): raise CensusError(f"coverage ledger index out of range: {index}")
        native = registry[index]
        if source["shippedName"] != native["name"] or int(source["handlerVa"], 16) != native["handler"]:
            raise CensusError(f"coverage/native registry mismatch at row {index}")
        if source["observed"] not in {"True", "False"}: raise CensusError(f"invalid observed value at row {index}")
        if index in observed: raise CensusError(f"duplicate coverage row {index}")
        observed[index] = source["observed"] == "True"
    if set(observed) != set(range(144)): raise CensusError("coverage ledger does not contain exactly indexes 0..143")
    return observed


def coverage_identity(ledger_dir: Path, *, enforce_pins: bool = True) -> dict[str, object]:
    ready_path = ledger_dir / "ledger.ready.json"
    try: ready = json.loads(ready_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error: raise CensusError(f"invalid coverage READY: {error}") from error
    require_equal("coverage READY schema", ready.get("schema"), COVERAGE_READY_SCHEMA)
    files = ready.get("files")
    if not isinstance(files, dict) or set(files) != set(COVERAGE_FILES):
        raise CensusError("coverage READY does not name the exact seven-file ledger set")
    for name in COVERAGE_FILES:
        path = ledger_dir / name
        expected = files.get(name)
        if not path.is_file() or path.is_symlink() or not isinstance(expected, dict):
            raise CensusError(f"coverage output missing or non-plain: {name}")
        require_equal(f"coverage portable path {name}", expected.get("path"), name)
        require_equal(f"coverage bytes {name}", path.stat().st_size, expected.get("bytes"))
        require_equal(f"coverage sha256 {name}", sha256_file(path), expected.get("sha256"))
    summary_path = ledger_dir / "ledger-summary.json"
    native_path = ledger_dir / "ledger-native-handlers.tsv"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    require_equal("coverage index count", summary.get("denominators", {}).get("coverageIndexCount"), 72)
    specimen = summary.get("inputs", {}).get("specimen", {})
    require_equal("coverage pristine specimen", str(specimen.get("sha256", "")).casefold(), EXPECTED_SPECIMEN_SHA256)
    coverage_set = summary.get("denominators", {}).get("coverageSetSha256")
    targets = {
        str(row.get("receipt", {}).get("targetSha256", "")).casefold()
        for row in summary.get("sources", []) if row.get("receipt", {}).get("targetSha256")
    }
    if len(targets) != 1: raise CensusError(f"coverage sources do not share one runtime target: {sorted(targets)}")
    identity = {
        "readySha256": sha256_file(ready_path), "summarySha256": sha256_file(summary_path),
        "nativeHandlersSha256": sha256_file(native_path), "coverageIndexCount": 72,
        "coverageSetSha256": coverage_set, "specimenSha256": specimen["sha256"],
        "runtimeTargetSha256": next(iter(targets)), "publishedFiles": len(files),
    }
    if enforce_pins:
        require_equal("coverage READY pin", identity["readySha256"], EXPECTED_COVERAGE_READY_SHA256)
        require_equal("coverage summary pin", identity["summarySha256"], EXPECTED_COVERAGE_SUMMARY_SHA256)
        require_equal("coverage native pin", identity["nativeHandlersSha256"], EXPECTED_COVERAGE_NATIVE_SHA256)
        require_equal("coverage set pin", str(coverage_set).casefold(), EXPECTED_COVERAGE_SET_SHA256)
        require_equal("coverage runtime target pin", identity["runtimeTargetSha256"], EXPECTED_RUNTIME_TARGET_SHA256)
    return identity


def _pin_parser_dependencies(inputs: Inputs) -> dict[str, dict[str, object]]:
    identities: dict[str, dict[str, object]] = {}
    for relative, expected in PARSER_PINS.items():
        path = inputs.evidence_repo / relative
        if not path.is_file() or path.is_symlink(): raise CensusError(f"compiled parser dependency missing/non-plain: {relative}")
        actual = sha256_file(path)
        require_equal(f"compiled parser dependency {relative}", actual, expected)
        identities[relative] = {"bytes": path.stat().st_size, "sha256": actual}
    return identities


def compiled_profile(
    inputs: Inputs, registry: Sequence[dict[str, object]], *, enforce_pins: bool = True,
) -> tuple[bytes, bytes, dict[int, dict[str, object]], dict[str, Counter[int]], dict[str, object], dict[str, dict[str, object]]]:
    parser_identities = _pin_parser_dependencies(inputs) if enforce_pins else {}
    probe_dir = inputs.evidence_repo / "tools/probe"
    if str(probe_dir) not in sys.path: sys.path.insert(0, str(probe_dir))
    try: probe = importlib.import_module("probe_author")
    except Exception as error: raise CensusError(f"cannot import compiled Mission owner: {error}") from error
    try: _lab, _aya, script_parse, bea_aya = probe.bea_lab.load(inputs.evidence_repo / "local-lab")
    except Exception as error: raise CensusError(f"cannot load compiled Mission readers: {error}") from error

    archives = sorted(inputs.resources.glob("*_res_PC.aya"), key=lambda item: item.name.casefold())
    if not archives: raise CensusError(f"no *_res_PC.aya under {inputs.resources}")
    folded: set[str] = set()
    resource_rows: list[dict[str, object]] = []
    archive_identity: dict[str, dict[str, object]] = {}
    profiles: dict[int, Counter[str]] = {index: Counter() for index in range(144)}
    native_archives: dict[int, set[str]] = defaultdict(set)
    native_levels: dict[int, set[str]] = defaultdict(set)
    level_calls: dict[str, Counter[int]] = defaultdict(Counter)
    world_chunks = 0
    total_calls = 0
    for path in archives:
        folded_name = path.name.casefold()
        if folded_name in folded: raise CensusError(f"case-folded resource collision: {path.name}")
        folded.add(folded_name)
        if path.is_symlink(): raise CensusError(f"symlinked resource archive refused: {path}")
        data = path.read_bytes()
        match = ARCHIVE_LEVEL_RE.fullmatch(path.name)
        key = match.group(1) if match else ""
        digest = sha256_bytes(data)
        resource_rows.append({"relativePath": path.name, "levelKey": key, "bytes": len(data), "sha256": digest})
        if key:
            archive_identity[key] = {"name": path.name, "bytes": len(data), "sha256": digest}
        try:
            # The pinned legacy reader uses ``open(...).read()`` without a
            # context manager; its temporary handle is released immediately,
            # but CPython reports that implementation detail under unittest's
            # ResourceWarning filter.  Keep using the authenticated reader and
            # suppress only that known warning at its call boundary.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ResourceWarning)
                inflated = bea_aya.inflate_aya(str(path))
        except Exception as error: raise CensusError(f"cannot inflate {path.name}: {error}") from error
        for tag in probe.WORLD_TAGS:
            try: chain = probe.find_chunk_path(inflated, b"WRES", b"WRLD", tag)
            except probe.FramingError: continue
            try: parsed = script_parse.parse_world(inflated[chain[-1].body:chain[-1].end])
            except Exception as error: raise CensusError(f"cannot parse {path.name}/{tag!r}: {error}") from error
            world_chunks += 1
            for script in parsed["table"]["scripts"]:
                for opcode, operand in script["instructions"]:
                    if opcode != probe.OP_CALL: continue
                    index, argc, return_word = probe.decode_call(operand)
                    if index >= len(registry): raise CensusError(f"compiled CALL index out of registry: {index}")
                    profiles[index][f"{argc}/{1 if return_word else 0}"] += 1
                    native_archives[index].add(path.name)
                    if key:
                        native_levels[index].add(key)
                        level_calls[key][index] += 1
                    total_calls += 1
    resource_bytes = render_tsv(RESOURCE_COLUMNS, resource_rows)
    profile_rows: list[dict[str, object]] = []
    by_native: dict[int, dict[str, object]] = {}
    for index, native in enumerate(registry):
        calls = sum(profiles[index].values())
        row = {
            "nativeIndex": index, "nativeName": native["name"], "compiledCallCount": calls,
            "compiledArchiveCount": len(native_archives[index]),
            "compiledLevelArchiveCount": len(native_levels[index]),
            "callProfilesJson": json.dumps(dict(sorted(profiles[index].items())), sort_keys=True, separators=(",", ":")),
        }
        profile_rows.append(row); by_native[index] = row
    profile_bytes = render_tsv(COMPILED_COLUMNS, profile_rows)
    identity = {
        "archiveCount": len(archives), "numericLevelArchiveCount": len(archive_identity),
        "worldChunkCount": world_chunks, "compiledCallCount": total_calls,
        "compiledUsedNatives": sum(bool(profiles[index]) for index in range(144)),
        "resourceManifestSha256": sha256_bytes(resource_bytes),
        "compiledProfileSha256": sha256_bytes(profile_bytes), "parserDependencies": parser_identities,
    }
    if enforce_pins:
        validate_compiled_pins(identity)
    return resource_bytes, profile_bytes, by_native, level_calls, identity, archive_identity


def _tsv_reader(path: Path) -> csv.DictReader:
    lines = path.read_text(encoding="utf-8").splitlines()
    return csv.DictReader(io.StringIO("\n".join(line for line in lines if not line.startswith("#")) + "\n"), delimiter="\t")


def _pe_offset(image: bytes, virtual_address: int) -> int:
    if image[:2] != b"MZ": raise CensusError("specimen lacks MZ header")
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    if image[pe:pe + 4] != b"PE\0\0": raise CensusError("specimen lacks PE header")
    sections = struct.unpack_from("<H", image, pe + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe + 20)[0]
    image_base = struct.unpack_from("<I", image, pe + 24 + 28)[0]
    rva = virtual_address - image_base
    first = pe + 24 + optional_size
    for index in range(sections):
        row = first + index * 40
        virtual_size, virtual_rva, raw_size, raw_pointer = struct.unpack_from("<IIII", image, row + 8)
        if virtual_rva <= rva < virtual_rva + max(virtual_size, raw_size):
            return raw_pointer + rva - virtual_rva
    raise CensusError(f"VA 0x{virtual_address:08x} is outside specimen sections")


def _read_c_string(image: bytes, virtual_address: int) -> str:
    start = _pe_offset(image, virtual_address)
    end = image.find(b"\0", start)
    if end < 0: raise CensusError(f"unterminated C string at 0x{virtual_address:08x}")
    return image[start:end].decode("ascii")


def _pe_text_layout(image: bytes) -> tuple[int, int, int, int]:
    """Return (.text VA, raw pointer, virtual size, raw size)."""
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    sections = struct.unpack_from("<H", image, pe + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe + 20)[0]
    image_base = struct.unpack_from("<I", image, pe + 24 + 28)[0]
    first = pe + 24 + optional_size
    for index in range(sections):
        row = first + index * 40
        name = image[row:row + 8].rstrip(b"\0")
        virtual_size, virtual_rva, raw_size, raw_pointer = struct.unpack_from("<IIII", image, row + 8)
        if name == b".text":
            return image_base + virtual_rva, raw_pointer, virtual_size, raw_size
    raise CensusError("specimen has no .text section")


def console_callsite_census(image: bytes, body_rows: Sequence[dict[str, str]]) -> list[dict[str, object]]:
    """Enumerate every pristine rel32 call to CConsole__Printf and its receiver.

    The Ghidra parity graph intentionally aggregates only calls lying inside
    exported function ranges.  This independent raw-byte denominator scans all
    of virtual .text, then uses Capstone only to recover the final receiver PUSH
    and the preceding format PUSH.  The three calls outside exported ranges use
    exact, preregistered decode starts and remain labelled unmapped.
    """
    require_equal("Capstone version", capstone.__version__, CAPSTONE_VERSION)
    text_va, text_raw, text_virtual_size, text_raw_size = _pe_text_layout(image)
    require_equal(".text VA", text_va, 0x00401000)
    require_equal(".text raw pointer", text_raw, 0x1000)
    require_equal(".text virtual size", text_virtual_size, 0x1D6F9D)
    require_equal(".text raw size", text_raw_size, 0x1D7000)
    raw_sites: list[int] = []
    for offset in range(text_raw, text_raw + text_virtual_size - 4):
        if image[offset] != 0xE8:
            continue
        site = text_va + offset - text_raw
        target = site + 5 + struct.unpack_from("<i", image, offset + 1)[0]
        if target == CONSOLE_PRINTF_VA:
            raw_sites.append(site)
    require_equal("raw CConsole__Printf rel32 call count", len(raw_sites), EXPECTED_CONSOLE_RAW_CALLS)

    ranges: list[tuple[int, int, dict[str, str]]] = []
    for row in body_rows:
        ranges.append((int(row["rangeMin"], 16), int(row["rangeEndExclusive"], 16), row))
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True
    output: list[dict[str, object]] = []
    for site in raw_sites:
        owners = [row for start, end, row in ranges if start <= site and site + 5 <= end]
        if len(owners) > 1:
            raise CensusError(f"console call 0x{site:08x} belongs to multiple Ghidra ranges")
        if owners:
            owner = owners[0]
            decode_start = int(owner["rangeMin"], 16)
            mapping_state = "GHIDRA_MAPPED"
            mapped_address, mapped_name, ordinal = owner["functionAddress"].casefold(), owner["functionName"], owner["rangeOrdinal"]
            candidate_address = candidate_name = ""
            unmapped = None
        else:
            unmapped = UNMAPPED_CONSOLE_SITES.get(site)
            if unmapped is None:
                raise CensusError(f"unregistered unmapped console call 0x{site:08x}")
            decode_start = int(unmapped["decodeStart"])
            mapping_state = "GHIDRA_UNMAPPED"
            mapped_address = mapped_name = ordinal = ""
            candidate_address = f"0x{int(unmapped['candidateOwnerAddress']):08x}"
            candidate_name = str(unmapped["candidateOwnerName"])
        decode_end = _pe_offset(image, site) + 5
        instructions = list(decoder.disasm(image[_pe_offset(image, decode_start):decode_end], decode_start))
        calls = [instruction for instruction in instructions if instruction.address == site]
        if len(calls) != 1 or calls[0].id != X86_INS_CALL or calls[0].size != 5:
            raise CensusError(f"Capstone did not recover rel32 call at 0x{site:08x}")
        pushes = [instruction for instruction in instructions if instruction.address < site and instruction.id == X86_INS_PUSH]
        if len(pushes) < 2:
            raise CensusError(f"console call 0x{site:08x} lacks receiver/format PUSH pair")
        format_push, receiver_push = pushes[-2], pushes[-1]
        if len(receiver_push.operands) != 1 or receiver_push.operands[0].type != X86_OP_IMM:
            raise CensusError(f"console call 0x{site:08x} receiver PUSH is not immediate")
        receiver = receiver_push.operands[0].imm & 0xFFFFFFFF
        if receiver == DORMANT_LOGGER_RECEIVER_VA:
            channel = "DORMANT_LOGGER_RECEIVER"
        elif receiver == SETUPHISTORY_RECEIVER_VA:
            channel = "SETUPHISTORY_RECEIVER"
        else:
            raise CensusError(f"console call 0x{site:08x} has unknown receiver 0x{receiver:08x}")
        if len(format_push.operands) != 1:
            raise CensusError(f"console call 0x{site:08x} format PUSH has unexpected operands")
        operand = format_push.operands[0]
        if operand.type == X86_OP_IMM:
            format_kind = "IMMEDIATE"
            format_immediate = operand.imm & 0xFFFFFFFF
            format_immediate_text = f"0x{format_immediate:08x}"
            format_string = _read_c_string(image, format_immediate)
        elif operand.type == X86_OP_REG:
            format_kind, format_immediate_text, format_string = "REGISTER", "", ""
        elif operand.type == X86_OP_MEM:
            format_kind, format_immediate_text, format_string = "MEMORY", "", ""
        else:
            raise CensusError(f"console call 0x{site:08x} format PUSH has unsupported operand type")
        if unmapped is not None:
            require_equal(f"unmapped format pointer 0x{site:08x}", format_immediate_text, f"0x{int(unmapped['formatVa']):08x}")
            require_equal(f"unmapped format string 0x{site:08x}", format_string, unmapped["format"])
            require_equal(f"unmapped receiver 0x{site:08x}", receiver, DORMANT_LOGGER_RECEIVER_VA)
        output.append({
            "callSiteVa": f"0x{site:08x}", "receiverPushVa": f"0x{receiver_push.address:08x}",
            "receiverVa": f"0x{receiver:08x}", "receiverChannel": channel,
            "mappingState": mapping_state, "mappedCallerAddress": mapped_address,
            "mappedCallerName": mapped_name, "rangeOrdinal": ordinal,
            "candidateOwnerAddress": candidate_address, "candidateOwnerName": candidate_name,
            "formatPushVa": f"0x{format_push.address:08x}", "formatOperandKind": format_kind,
            "formatOperandText": format_push.op_str, "formatImmediateVa": format_immediate_text,
            "formatString": format_string,
        })
    partitions = Counter((str(row["receiverChannel"]), str(row["mappingState"])) for row in output)
    require_equal("dormant receiver mapped calls", partitions[("DORMANT_LOGGER_RECEIVER", "GHIDRA_MAPPED")], 250)
    require_equal("dormant receiver unmapped calls", partitions[("DORMANT_LOGGER_RECEIVER", "GHIDRA_UNMAPPED")], 3)
    require_equal("setuphistory receiver mapped calls", partitions[("SETUPHISTORY_RECEIVER", "GHIDRA_MAPPED")], 127)
    require_equal("setuphistory receiver unmapped calls", partitions[("SETUPHISTORY_RECEIVER", "GHIDRA_UNMAPPED")], 0)
    require_equal("unmapped console call sites", {int(str(row["callSiteVa"]), 16) for row in output if row["mappingState"] == "GHIDRA_UNMAPPED"}, set(UNMAPPED_CONSOLE_SITES))
    return output


def static_logger_evidence(inputs: Inputs, *, enforce_pins: bool = True) -> tuple[bytes, bytes, bytes, dict[str, object]]:
    specimen = inputs.specimen.read_bytes()
    if enforce_pins:
        require_equal("pristine specimen sha256", sha256_bytes(specimen), EXPECTED_SPECIMEN_SHA256)
        require_equal("pristine specimen md5", hashlib.md5(specimen).hexdigest(), EXPECTED_SPECIMEN_MD5)
        require_equal("parity READY pin", sha256_file(inputs.parity_ready), EXPECTED_PARITY_READY_SHA256)
    ready = json.loads(inputs.parity_ready.read_text(encoding="utf-8"))
    require_equal("parity READY schema", ready.get("schemaVersion"), PARITY_READY_SCHEMA)
    require_equal("parity executable MD5", str(ready.get("program", {}).get("executableMd5", "")).casefold(), EXPECTED_SPECIMEN_MD5)
    require_equal("parity image base", ready.get("program", {}).get("imageBase"), "0x00400000")
    body_fact, direct_fact = ready.get("bodyRanges", {}), ready.get("directCalls", {})
    if body_fact.get("file") != "after-body-ranges.tsv" or direct_fact.get("file") != "after-direct-calls.tsv":
        raise CensusError("parity READY names unexpected graph siblings")
    body_path = inputs.parity_ready.parent / "after-body-ranges.tsv"
    direct_path = inputs.parity_ready.parent / "after-direct-calls.tsv"
    for label, path, fact, pin in (
        ("body ranges", body_path, body_fact, EXPECTED_BODY_RANGES_SHA256),
        ("direct calls", direct_path, direct_fact, EXPECTED_DIRECT_CALLS_SHA256),
    ):
        if not path.is_file() or path.is_symlink(): raise CensusError(f"{label} missing/non-plain")
        require_equal(f"{label} bytes", path.stat().st_size, fact.get("bytes"))
        require_equal(f"{label} receipt hash", sha256_file(path), fact.get("sha256"))
        if enforce_pins: require_equal(f"{label} pin", sha256_file(path), pin)

    body_rows = list(_tsv_reader(body_path))
    print_ranges = [row for row in body_rows if row["functionAddress"].casefold() == "0x00537ad0"]
    if len(print_ranges) != 1: raise CensusError(f"Print handler has {len(print_ranges)} exact Ghidra ranges")
    print_range = print_ranges[0]
    require_equal("Print range start", print_range["rangeMin"].casefold(), "0x00537ad0")
    require_equal("Print range end", print_range["rangeEndExclusive"].casefold(), "0x00537c28")
    require_equal("Print range bytes", int(print_range["rangeBytes"]), 344)
    require_equal("Print range hash", print_range["rangeSha256"].casefold(), EXPECTED_PRINT_BODY_SHA256)
    start, end = _pe_offset(specimen, 0x00537AD0), _pe_offset(specimen, 0x00537C28)
    require_equal("Print pristine body hash", sha256_bytes(specimen[start:end]), EXPECTED_PRINT_BODY_SHA256)

    table_start = _pe_offset(specimen, 0x00537C28)
    jump_targets = list(struct.unpack_from("<6I", specimen, table_start))
    expected_targets = [0x00537AF2, 0x00537B13, 0x00537B76, 0x00537B39, 0x00537B97, 0x00537BB8]
    require_equal("Print six-type jump table", jump_targets, expected_targets)
    types = [
        (1, "integer", 0x00537AF2, [(0x00537AFB, 0x006245CC, "%d")]),
        (2, "float", 0x00537B13, [(0x00537B21, 0x00625098, "%f")]),
        (3, "string", 0x00537B76, [(0x00537B7F, 0x006245D8, "%s")]),
        (4, "boolean", 0x00537B39, [(0x00537B45, 0x0064FD9C, "TRUE"), (0x00537B5E, 0x0064FD94, "FALSE")]),
        (5, "thing-reference", 0x00537B97, [(0x00537BA0, 0x0064FD8C, "%08x")]),
        (6, "position", 0x00537BB8, [(0x00537BF7, 0x0064FD6C, "x = %.4f, y = %.4f, z = %.4f")]),
    ]
    type_rows: list[dict[str, object]] = []
    for type_id, name, target, strings in types:
        string_rows: list[dict[str, object]] = []
        for reference, address, value in strings:
            require_equal(f"Print static string 0x{address:08x}", _read_c_string(specimen, address), value)
            require_equal(
                f"Print pointer at 0x{reference:08x}",
                struct.unpack_from("<I", specimen, _pe_offset(specimen, reference))[0],
                address,
            )
            string_rows.append({"referenceVa": f"0x{reference:08x}", "stringAddress": f"0x{address:08x}", "value": value})
        type_rows.append({"typeId": type_id, "typeName": name, "dispatchTargetVa": f"0x{target:08x}", "staticStrings": string_rows})
    require_equal("Print unknown-type string", _read_c_string(specimen, 0x0064FD5C), "unknown type")
    require_equal(
        "Print unknown-type pointer",
        struct.unpack_from("<I", specimen, _pe_offset(specimen, 0x00537C10))[0],
        0x0064FD5C,
    )
    dispatch = {
        "schema": "bea.re.mission-print-static-dispatch.v1", "status": STATUS,
        "evidenceGrade": "STATIC_EXACT_BYTES", "handlerVa": "0x00537ad0",
        "handlerRangeEndExclusive": "0x00537c28", "handlerBodySha256": EXPECTED_PRINT_BODY_SHA256,
        "jumpTableVa": "0x00537c28", "types": type_rows,
        "default": {"referenceVa": "0x00537c10", "staticStringAddress": "0x0064fd5c", "staticString": "unknown type"},
        "readingRule": "Exact pristine bytes prove six formatter dispatch arms; this output does not claim each arm was exercised at runtime.",
    }

    callsites = console_callsite_census(specimen, body_rows)
    callers: list[dict[str, object]] = []
    for row in _tsv_reader(direct_path):
        if row["calleeAddress"].casefold() == "0x00441740":
            if row["edgeKind"] != "STATIC_DIRECT": raise CensusError("console formatter edge is not STATIC_DIRECT")
            callers.append({"callerAddress": row["callerAddress"].casefold(), "callerName": row["callerName"], "callSiteCount": int(row["callSiteCount"])})
    callers.sort(key=lambda row: int(str(row["callerAddress"]), 16))
    require_equal("Ghidra-mapped console formatter callers", len(callers), EXPECTED_CONSOLE_MAPPED_CALLERS)
    require_equal("Ghidra-mapped console formatter call sites", sum(int(row["callSiteCount"]) for row in callers), EXPECTED_CONSOLE_MAPPED_CALLS)
    raw_mapped = Counter(
        (str(row["mappedCallerAddress"]), str(row["mappedCallerName"]))
        for row in callsites if row["mappingState"] == "GHIDRA_MAPPED"
    )
    graph_mapped = {
        (str(row["callerAddress"]), str(row["callerName"])): int(row["callSiteCount"])
        for row in callers
    }
    require_equal("raw/Ghidra mapped console call aggregation", dict(raw_mapped), graph_mapped)
    channels = Counter(str(row["receiverChannel"]) for row in callsites)
    require_equal("dormant logger receiver calls", channels["DORMANT_LOGGER_RECEIVER"], EXPECTED_DORMANT_RECEIVER_CALLS)
    require_equal("setuphistory receiver calls", channels["SETUPHISTORY_RECEIVER"], EXPECTED_SETUPHISTORY_RECEIVER_CALLS)
    caller_bytes = render_tsv(MAPPED_CALLER_COLUMNS, callers)
    callsite_bytes = render_tsv(CALLSITE_COLUMNS, callsites)
    identity = {
        "specimenSha256": EXPECTED_SPECIMEN_SHA256, "parityReadySha256": sha256_file(inputs.parity_ready),
        "bodyRangesSha256": sha256_file(body_path), "directCallsSha256": sha256_file(direct_path),
        "consolePrintfVa": "0x00441740", "rawRel32CallSiteCount": len(callsites),
        "ghidraMappedCallerCount": len(callers),
        "ghidraMappedCallSiteCount": sum(int(row["callSiteCount"]) for row in callers),
        "ghidraUnmappedCallSiteCount": sum(row["mappingState"] == "GHIDRA_UNMAPPED" for row in callsites),
        "dormantLoggerReceiverVa": "0x0066f580",
        "dormantLoggerReceiverCallSiteCount": channels["DORMANT_LOGGER_RECEIVER"],
        "dormantLoggerMappedCallSiteCount": sum(row["receiverChannel"] == "DORMANT_LOGGER_RECEIVER" and row["mappingState"] == "GHIDRA_MAPPED" for row in callsites),
        "dormantLoggerUnmappedCallSiteCount": sum(row["receiverChannel"] == "DORMANT_LOGGER_RECEIVER" and row["mappingState"] == "GHIDRA_UNMAPPED" for row in callsites),
        "setupHistoryReceiverVa": "0x0066eb90",
        "setupHistoryReceiverCallSiteCount": channels["SETUPHISTORY_RECEIVER"],
        "decoder": {"name": "capstone", "version": CAPSTONE_VERSION, "arch": "x86", "mode": 32},
        "claimClass": "PRISTINE_REL32_RECEIVER_CENSUS_WITH_GHIDRA_MAPPING",
    }
    return canonical_json(dispatch), callsite_bytes, caller_bytes, identity


def classify_presence(present: bool, observed: bool, prefix: str) -> str:
    return f"{prefix}_{'PRESENT' if present else 'ABSENT'}_{'OBSERVED' if observed else 'UNOBSERVED'}"


def _assign_ranks(rows: list[dict[str, object]]) -> None:
    stock = sorted(
        (row for row in rows if row["runnableArchive"] == "True" and int(row["stockEarlyExpressionPrintCount"]) + int(row["stockEarlyLiteralPrintCount"]) > 0),
        key=lambda row: (-int(row["stockEarlyExpressionPrintCount"]), -int(row["initExpressionPrintCount"]), -int(row["stockEarlyLiteralPrintCount"]), str(row["levelKey"])),
    )
    stimulus = sorted(
        (row for row in rows if row["runnableArchive"] == "True" and int(row["stimulusExpressionPrintCount"]) + int(row["stimulusLiteralPrintCount"]) > 0),
        key=lambda row: (-int(row["stimulusExpressionPrintCount"]), -int(row["stimulusLiteralPrintCount"]), str(row["levelKey"])),
    )
    native = sorted(
        (row for row in rows if row["runnableArchive"] == "True" and int(row["compiledFrontierNativeCount"]) > 0),
        key=lambda row: (-int(row["compiledFrontierNativeCount"]), -int(row["compiledFrontierCallCount"]), str(row["levelKey"])),
    )
    for rank, row in enumerate(stock, 1): row["stockObservabilityRank"] = rank
    for rank, row in enumerate(stimulus, 1): row["authoredStimulusRank"] = rank
    for rank, row in enumerate(native, 1): row["nativeCoverageRank"] = rank


def analyze(inputs: Inputs, *, enforce_pins: bool = True) -> tuple[dict[str, bytes], dict[str, object]]:
    if enforce_pins:
        require_equal("native table pin", sha256_file(inputs.native_table), EXPECTED_NATIVE_TABLE_SHA256)
    registry = load_registry(inputs.native_table)
    registry_by_name = {str(row["name"]): row for row in registry}
    coverage = read_native_coverage(inputs.coverage_ledger / "ledger-native-handlers.tsv", registry)
    coverage_input = coverage_identity(inputs.coverage_ledger, enforce_pins=enforce_pins)

    corpus_rows: list[dict[str, object]] = []
    calls: list[dict[str, object]] = []
    files = sorted(inputs.msl_root.rglob("*.msl"), key=lambda item: item.relative_to(inputs.msl_root).as_posix().casefold())
    if not files: raise CensusError(f"no .msl files found under {inputs.msl_root}")
    folded: set[str] = set()
    for path in files:
        if path.is_symlink(): raise CensusError(f"symlinked corpus member refused: {path}")
        relative = path.relative_to(inputs.msl_root).as_posix()
        if relative.casefold() in folded: raise CensusError(f"case-folded corpus collision: {relative}")
        folded.add(relative.casefold())
        data = path.read_bytes()
        try: text = data.decode("utf-8-sig")
        except UnicodeDecodeError as error: raise CensusError(f"{relative}: not UTF-8/ASCII: {error}") from error
        corpus_rows.append({"relativePath": relative, "levelKey": level_key(relative), "bytes": len(data), "sha256": sha256_bytes(data)})
        calls.extend(parse_file_calls(text, relative, registry_by_name))
    calls.sort(key=lambda row: (str(row["relativePath"]).casefold(), int(row["line"]), int(row["column"]), int(row["nativeIndex"])))
    corpus_bytes = render_tsv(CORPUS_COLUMNS, corpus_rows)
    if enforce_pins:
        validate_corpus_pin(sha256_bytes(corpus_bytes), len(corpus_rows))

    resource_bytes, profile_bytes, compiled_by_native, compiled_by_level, resource_input, archive_identity = compiled_profile(
        inputs, registry, enforce_pins=enforce_pins,
    )
    dispatch_bytes, callsite_bytes, mapped_caller_bytes, static_input = static_logger_evidence(inputs, enforce_pins=enforce_pins)
    print_rows = [row for row in calls if row["nativeName"] == "Print"]
    calls_by_native: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in calls: calls_by_native[int(row["nativeIndex"])].append(row)

    native_rows: list[dict[str, object]] = []
    for native in registry:
        index = int(native["index"])
        rows = calls_by_native[index]
        source_present = bool(rows)
        compiled_calls = int(compiled_by_native[index]["compiledCallCount"])
        observed = coverage[index]
        native_rows.append({
            "nativeIndex": index, "nativeName": native["name"], "handlerVa": f"0x{int(native['handler']):08x}",
            "sourceCallCount": len(rows), "sourceFileCount": len({str(row["relativePath"]) for row in rows}),
            "sourceLevelCount": len({str(row["levelKey"]) for row in rows} - {"ROOT"}),
            "compiledCallCount": compiled_calls, "compiledArchiveCount": compiled_by_native[index]["compiledArchiveCount"],
            "compiledLevelArchiveCount": compiled_by_native[index]["compiledLevelArchiveCount"],
            "initCallCount": sum(row["scopeKind"] == "init" for row in rows),
            "gamePlayingCallCount": sum(row["scopeKind"] == "event" and str(row["scopeName"]).casefold() == "game playing" for row in rows),
            "eventCallCount": sum(row["scopeKind"] == "event" for row in rows),
            "actorHandlerCallCount": sum(row["scopeKind"] == "actor-handler" for row in rows),
            "topLevelCallCount": sum(row["scopeKind"] == "top-level" for row in rows),
            "coverageObserved": str(observed),
            "sourcePresenceCoverageClass": classify_presence(source_present, observed, "SOURCE"),
            "compiledPresenceCoverageClass": classify_presence(compiled_calls > 0, observed, "COMPILED"),
        })

    files_by_level: dict[str, set[str]] = defaultdict(set)
    calls_by_level: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in corpus_rows: files_by_level[str(row["levelKey"])].add(str(row["relativePath"]))
    for row in calls: calls_by_level[str(row["levelKey"])].append(row)
    level_rows: list[dict[str, object]] = []
    for key in sorted(files_by_level, key=lambda value: (value == "ROOT", value)):
        rows = calls_by_level[key]
        prints = [row for row in rows if row["nativeName"] == "Print"]
        compiled = compiled_by_level.get(key, Counter()) if key != "ROOT" else Counter()
        frontier = {index for index, count in compiled.items() if count and not coverage[index]}
        init_expression = sum(row["scopeKind"] == "init" and row["argumentKind"] == "expression" for row in prints)
        init_literal = sum(row["scopeKind"] == "init" and row["argumentKind"] == "literal-string" for row in prints)
        game_expression = sum(row["scopeKind"] == "event" and str(row["scopeName"]).casefold() == "game playing" and row["argumentKind"] == "expression" for row in prints)
        game_literal = sum(row["scopeKind"] == "event" and str(row["scopeName"]).casefold() == "game playing" and row["argumentKind"] == "literal-string" for row in prints)
        stimulus_expression = sum(
            row["argumentKind"] == "expression" and (
                (row["scopeKind"] == "event" and str(row["scopeName"]).casefold() != "game playing") or row["scopeKind"] == "actor-handler"
            ) for row in prints
        )
        stimulus_literal = sum(
            row["argumentKind"] == "literal-string" and (
                (row["scopeKind"] == "event" and str(row["scopeName"]).casefold() != "game playing") or row["scopeKind"] == "actor-handler"
            ) for row in prints
        )
        if init_expression: stock_window = "INIT_EXPRESSION"
        elif game_expression: stock_window = "GAME_PLAYING_EXPRESSION"
        elif init_literal or game_literal: stock_window = "EARLY_LITERAL_MARKER_ONLY"
        else: stock_window = "NONE"
        event_stimulus = any(row["scopeKind"] == "event" and str(row["scopeName"]).casefold() != "game playing" for row in prints)
        actor_stimulus = any(row["scopeKind"] == "actor-handler" for row in prints)
        if stimulus_expression and event_stimulus: stimulus_window = "EVENT_STIMULUS_EXPRESSION"
        elif stimulus_expression and actor_stimulus: stimulus_window = "ACTOR_STIMULUS_EXPRESSION"
        elif stimulus_literal: stimulus_window = "STIMULUS_LITERAL_MARKER_ONLY"
        else: stimulus_window = "NONE"
        archive = archive_identity.get(key)
        level_rows.append({
            "levelKey": key, "runnableArchive": str(bool(archive)),
            "resourceArchive": archive["name"] if archive else "", "resourceArchiveSha256": archive["sha256"] if archive else "",
            "fileCount": len(files_by_level[key]), "sourceNativeCallCount": len(rows),
            "sourceDistinctNativeCount": len({int(row["nativeIndex"]) for row in rows}),
            "compiledNativeCallCount": sum(compiled.values()), "compiledDistinctNativeCount": len(compiled),
            "compiledFrontierNativeCount": len(frontier), "compiledFrontierCallCount": sum(compiled[index] for index in frontier),
            "printCallCount": len(prints), "literalPrintCount": sum(row["argumentKind"] == "literal-string" for row in prints),
            "expressionPrintCount": sum(row["argumentKind"] == "expression" for row in prints),
            "initPrintCount": sum(row["scopeKind"] == "init" for row in prints),
            "gamePlayingPrintCount": sum(row["scopeKind"] == "event" and str(row["scopeName"]).casefold() == "game playing" for row in prints),
            "eventPrintCount": sum(row["scopeKind"] == "event" for row in prints),
            "actorHandlerPrintCount": sum(row["scopeKind"] == "actor-handler" for row in prints),
            "topLevelPrintCount": sum(row["scopeKind"] == "top-level" for row in prints),
            "stockEarlyExpressionPrintCount": init_expression + game_expression,
            "stockEarlyLiteralPrintCount": init_literal + game_literal,
            "initExpressionPrintCount": init_expression, "stockObservabilityWindow": stock_window,
            "stockObservabilityRank": 0, "stimulusExpressionPrintCount": stimulus_expression,
            "stimulusLiteralPrintCount": stimulus_literal, "authoredStimulusWindow": stimulus_window,
            "authoredStimulusRank": 0, "nativeCoverageRank": 0,
        })
    _assign_ranks(level_rows)
    level_rows.sort(key=lambda row: (str(row["levelKey"]) == "ROOT", str(row["levelKey"])))

    call_bytes = render_tsv(CALL_COLUMNS, calls)
    print_bytes = render_tsv(PRINT_COLUMNS, print_rows)
    native_bytes = render_tsv(NATIVE_COLUMNS, native_rows)
    level_bytes = render_tsv(LEVEL_COLUMNS, level_rows)
    source_dispositions = Counter(str(row["sourcePresenceCoverageClass"]) for row in native_rows)
    compiled_dispositions = Counter(str(row["compiledPresenceCoverageClass"]) for row in native_rows)
    source_only = [str(row["nativeName"]) for row in native_rows if int(row["sourceCallCount"]) and not int(row["compiledCallCount"])]
    summary = {
        "schema": SCHEMA, "status": STATUS,
        "readingRules": [
            "Source presence proves a shipped .msl call site, not compiled presence or runtime execution.",
            "Compiled presence proves a CALL in the authenticated shipped resource archives, not runtime execution.",
            "Coverage observed proves handler bytes executed in the frozen 72-index corpus; unobserved is non-observation.",
            "Print is a Mission-value transport only on a disposable binary whose logger gate is enabled.",
            "argumentText is the exact source slice inside parentheses after removing only leading/trailing whitespace; its UTF-8 bytes are hashed.",
            "stockObservabilityRank orders runnable levels by early expression Print count, init expression count, early literal markers, then level key; it does not prove those declarations execute.",
            "authoredStimulusRank orders runnable levels by non-startup event/actor expression Prints, literal markers, then level key; stimulus is required.",
            "nativeCoverageRank orders runnable levels by compiled unobserved-native diversity, compiled frontier CALL count, then level key; it is a static targeting heuristic, not coverage yield already achieved.",
            "A pristine-byte rel32 scan finds 380 direct CConsole__Printf calls; the parity graph accounts for only the 377 calls inside 175 exported Ghidra functions and omits three executable call sites.",
            "Receiver partitioning is exact for the pristine bytes: 253 calls push dormant logger receiver 0x0066F580 (250 mapped plus three unmapped), while 127 mapped calls push the separate setuphistory receiver 0x0066EB90.",
            "The one-byte dormant logger gate concerns the 0x0066F580 receiver family; it must not be described as newly exposing the 127 setuphistory calls.",
            "All console-call counts are static call-site evidence, not runtime-observed execution.",
        ],
        "counts": {
            "corpusFiles": len(corpus_rows), "levelDirectories": len(files_by_level) - (1 if "ROOT" in files_by_level else 0),
            "runnableLevelDirectories": sum(row["runnableArchive"] == "True" for row in level_rows if row["levelKey"] != "ROOT"),
            "unrunnableLevelDirectories": sum(row["runnableArchive"] == "False" for row in level_rows if row["levelKey"] != "ROOT"),
            "resourceArchives": resource_input["archiveCount"], "compiledWorldChunks": resource_input["worldChunkCount"],
            "nativeRegistryRows": len(registry), "sourceNativeCalls": len(calls), "compiledNativeCalls": resource_input["compiledCallCount"],
            "sourcePresentNatives": sum(bool(calls_by_native[index]) for index in range(144)),
            "sourceAbsentNatives": sum(not calls_by_native[index] for index in range(144)),
            "compiledPresentNatives": sum(int(compiled_by_native[index]["compiledCallCount"]) > 0 for index in range(144)),
            "compiledAbsentNatives": sum(int(compiled_by_native[index]["compiledCallCount"]) == 0 for index in range(144)),
            "sourceOnlyNatives": source_only, "printSourceCalls": len(print_rows),
            "printCompiledCalls": int(compiled_by_native[next(i for i, row in enumerate(registry) if row["name"] == "Print")]["compiledCallCount"]),
            "printFiles": len({row["relativePath"] for row in print_rows}),
            "printLevelDirectories": len({row["levelKey"] for row in print_rows if row["levelKey"] != "ROOT"}),
            "literalPrintCalls": sum(row["argumentKind"] == "literal-string" for row in print_rows),
            "expressionPrintCalls": sum(row["argumentKind"] == "expression" for row in print_rows),
            "initPrintCalls": sum(row["scopeKind"] == "init" for row in print_rows),
            "eventPrintCalls": sum(row["scopeKind"] == "event" for row in print_rows),
            "actorHandlerPrintCalls": sum(row["scopeKind"] == "actor-handler" for row in print_rows),
            "topLevelPrintCalls": sum(row["scopeKind"] == "top-level" for row in print_rows),
            "sourcePresenceCoverageClasses": dict(sorted(source_dispositions.items())),
            "compiledPresenceCoverageClasses": dict(sorted(compiled_dispositions.items())),
        },
        "inputs": {
            "sourceCorpus": {"treeManifestSha256": sha256_bytes(corpus_bytes), "fileCount": len(corpus_rows)},
            "nativeTable": {"sha256": sha256_file(inputs.native_table), "rows": len(registry)},
            "compiledResources": resource_input, "coverageLedger": coverage_input,
            "staticLoggerEvidence": static_input,
        },
    }
    outputs = {
        "corpus-files.tsv": corpus_bytes, "resource-archives.tsv": resource_bytes,
        "native-calls.tsv": call_bytes, "print-calls.tsv": print_bytes,
        "compiled-native-profile.tsv": profile_bytes, "native-summary.tsv": native_bytes,
        "level-summary.tsv": level_bytes, "print-dispatch-static.json": dispatch_bytes,
        "console-printf-callsites.tsv": callsite_bytes,
        "console-printf-mapped-callers.tsv": mapped_caller_bytes,
        "census-summary.json": canonical_json(summary),
    }
    return outputs, summary


def canonical_inputs(repo: Path) -> Inputs:
    # External path topology is deliberately not an authority: every consumed
    # corpus, parser, ledger, project export, and specimen fact is content-pinned.
    evidence = Path(os.environ.get("BEA_MSL_LOGGER_EVIDENCE_REPO", str(repo))).absolute()
    lab = evidence / "local-lab"
    parity = lab / "ghidra-recursive-campaign-2026-08-02/observed40-evidence-8124/after-parity-graph.ready.json"
    return Inputs(
        repo=repo.resolve(), evidence_repo=evidence,
        msl_root=lab / "safe-copy-bea-pristine/data/MissionScripts",
        resources=lab / "safe-copy-bea-pristine/data/Resources",
        native_table=lab / "scenario-primitives-2026-08-02/native_table.json",
        coverage_ledger=lab / "re-ledger/coverage-ledger-2026-08-02-observed40-exact-v4-ready",
        specimen=lab / "safe-copy-bea-pristine/BEA.exe.original.backup",
        parity_ready=parity,
    )


def expected_ready(owner: bytes, outputs: dict[str, bytes], summary: dict[str, object]) -> dict[str, object]:
    all_outputs = {"msl-logger-census-owner.py": owner, **outputs}
    return {
        "schema": READY_SCHEMA, "status": STATUS, "ownerSha256": sha256_bytes(owner),
        "censusSchema": summary["schema"], "counts": summary["counts"], "inputs": summary["inputs"],
        "outputs": {name: {"bytes": len(data), "sha256": sha256_bytes(data)} for name, data in sorted(all_outputs.items())},
    }


def build_bundle(out: Path, owner_path: Path) -> dict[str, object]:
    if owner_path.resolve() != Path(__file__).resolve():
        raise CensusError("build owner must be the verifier being executed")
    if out.exists(): raise CensusError(f"output already exists: {out}")
    repo = find_repo(owner_path.parent)
    owner = owner_path.read_bytes()
    outputs, summary = analyze(canonical_inputs(repo), enforce_pins=True)
    ready = expected_ready(owner, outputs, summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{out.name}-", dir=out.parent))
    try:
        (staging / "msl-logger-census-owner.py").write_bytes(owner)
        for name, data in outputs.items(): (staging / name).write_bytes(data)
        (staging / "READY.json").write_bytes(canonical_json(ready))
        verify_bundle(staging, owner_path)
        staging.replace(out)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True); raise
    return ready


def verify_bundle(bundle: Path, owner_path: Path) -> dict[str, object]:
    if owner_path.resolve() != Path(__file__).resolve():
        raise CensusError("verify owner must be the verifier being executed")
    validate_bundle_tree(bundle)
    try:
        ready_bytes = (bundle / "READY.json").read_bytes()
        published = json.loads(ready_bytes.decode("utf-8"))
    except (OSError, json.JSONDecodeError) as error: raise CensusError(f"invalid READY.json: {error}") from error
    if ready_bytes != canonical_json(published):
        raise CensusError("READY.json is not canonical JSON")
    repo = find_repo(owner_path.parent)
    owner = owner_path.read_bytes()
    if (bundle / "msl-logger-census-owner.py").read_bytes() != owner:
        raise CensusError("frozen owner differs from the verifier being executed")
    outputs, summary = analyze(canonical_inputs(repo), enforce_pins=True)
    expected = expected_ready(owner, outputs, summary)
    if published != expected: raise CensusError("READY semantics differ from a fresh canonical derivation")
    for name, data in {"msl-logger-census-owner.py": owner, **outputs}.items():
        if (bundle / name).read_bytes() != data: raise CensusError(f"published output differs from fresh derivation: {name}")
    return expected


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build"); build_parser.add_argument("--out", required=True, type=Path)
    verify_parser = subparsers.add_parser("verify"); verify_parser.add_argument("--bundle", required=True, type=Path)
    arguments = parser.parse_args(argv)
    owner_path = Path(__file__).resolve()
    try:
        result = build_bundle(arguments.out.resolve(), owner_path) if arguments.command == "build" else verify_bundle(arguments.bundle.absolute(), owner_path)
    except (CensusError, OSError) as error:
        print(f"REFUSED: {error}", file=sys.stderr); return 2
    print(
        f"{result['status']}: {result['counts']['corpusFiles']} source files, "
        f"{result['counts']['sourceNativeCalls']} source calls, "
        f"{result['counts']['compiledNativeCalls']} compiled calls"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
