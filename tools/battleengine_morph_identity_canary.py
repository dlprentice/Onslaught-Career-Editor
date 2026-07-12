#!/usr/bin/env python3
"""Private CDB command rendering and public-safe morph canary materialization."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import struct
from typing import Any, Iterable, Mapping


CANONICAL_SIZE = 2_506_752
CANONICAL_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
P0_GLOBAL_RVA = 0x004A9D3C
PROBE_RVAS = {
    "playerTransformAction": 0x000D3110,
    "battleEngineMorph": 0x0000A580,
    "battleEngineMove": 0x000081C0,
    "jetPartMove": 0x00010C50,
}
RUN_ROLES = ("noInputControl", "positiveTransform", "positiveRepeat")
EXPECTED_EVENTS = (
    "playerTransformAction",
    "battleEngineMorph",
    "battleEngineMove",
    "jetPartMove",
)
PUBLIC_SCHEMA = "winui-original-binary-battleengine-morph-identity-canary.v1"
PRIVATE_RUN_SCHEMA = "winui-original-binary-battleengine-morph-identity-canary-private-run.v1"
TOOL_VERSION = "1"
FINGERPRINT_SIZE = 8
TEMPLATE_SHA256 = "243099789e37cd60769af2760882114d20b313a620d3d2ce0383d04208a40959"

DEFAULT_TEMPLATE = (
    Path(__file__).resolve().parent
    / "runtime-probes"
    / "battleengine-morph-identity-canary.cdb.tmpl"
)

_IMAGE_SCN_MEM_EXECUTE = 0x20000000
_IMAGE_REL_BASED_HIGHLOW = 3
_HEX_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_RAW_U32 = re.compile(r"0x[0-9a-f]{8}\Z")
_PLACEHOLDER = re.compile(r"{{([A-Z][A-Z0-9_]*)}}")
_EVENT_LINE = re.compile(
    r"MORPH_CANARY_EVENT event=(?P<event>[A-Za-z][A-Za-z0-9]*) "
    r"identityEqual=(?P<equal>[01]) rawStateU32=(?P<state>0x[0-9A-Fa-f]{8})\Z"
)


@dataclass(frozen=True)
class ProbeFingerprint:
    event: str
    rva: int
    size: int
    sha256: str
    relocation_overlap: bool


@dataclass(frozen=True)
class RenderedCommand:
    text: str
    sha256: str
    template_sha256: str
    executable_sha256: str
    fingerprint_size: int
    targets: tuple[ProbeFingerprint, ...]


@dataclass(frozen=True)
class _Section:
    virtual_address: int
    virtual_size: int
    raw_offset: int
    raw_size: int
    characteristics: int


class Pe32Image:
    """Minimal PE32 section mapper and HIGHLOW relocation reader."""

    def __init__(self, data: bytes):
        self.data = data
        self.sections: tuple[_Section, ...]
        self.highlow_relocations: frozenset[int]
        self._parse()

    def _parse(self) -> None:
        if len(self.data) < 0x40 or self.data[:2] != b"MZ":
            raise ValueError("invalid DOS header")
        pe_offset = _unpack_from("<I", self.data, 0x3C, "DOS header")[0]
        if pe_offset + 24 > len(self.data) or self.data[pe_offset : pe_offset + 4] != b"PE\0\0":
            raise ValueError("invalid PE signature")
        file_header = pe_offset + 4
        _, section_count, _, _, _, optional_size, _ = _unpack_from(
            "<HHIIIHH", self.data, file_header, "PE file header"
        )
        optional = file_header + 20
        if optional + optional_size > len(self.data) or optional_size < 96:
            raise ValueError("truncated PE optional header")
        magic = _unpack_from("<H", self.data, optional, "PE optional header")[0]
        if magic != 0x010B:
            raise ValueError("image is not PE32")
        directory_count = _unpack_from("<I", self.data, optional + 92, "PE data directories")[0]
        section_table = optional + optional_size
        if section_table + section_count * 40 > len(self.data):
            raise ValueError("truncated PE section table")

        sections: list[_Section] = []
        for index in range(section_count):
            values = _unpack_from(
                "<8sIIIIIIHHI",
                self.data,
                section_table + index * 40,
                "PE section header",
            )
            sections.append(
                _Section(
                    virtual_address=values[2],
                    virtual_size=values[1],
                    raw_offset=values[4],
                    raw_size=values[3],
                    characteristics=values[9],
                )
            )
        self.sections = tuple(sections)

        relocations: set[int] = set()
        if directory_count > 5 and optional_size >= 96 + 6 * 8:
            reloc_rva, reloc_size = _unpack_from(
                "<II", self.data, optional + 96 + 5 * 8, "base relocation directory"
            )
            if reloc_rva or reloc_size:
                if not reloc_rva or reloc_size < 8:
                    raise ValueError("invalid base relocation directory")
                raw = self._map_rva(reloc_rva, reloc_size, require_executable=False)
                end = raw + reloc_size
                cursor = raw
                while cursor < end:
                    page_rva, block_size = _unpack_from(
                        "<II", self.data, cursor, "base relocation block"
                    )
                    if block_size < 8 or block_size % 2 or cursor + block_size > end:
                        raise ValueError("invalid base relocation block")
                    for entry_offset in range(cursor + 8, cursor + block_size, 2):
                        entry = _unpack_from(
                            "<H", self.data, entry_offset, "base relocation entry"
                        )[0]
                        relocation_type = entry >> 12
                        if relocation_type == _IMAGE_REL_BASED_HIGHLOW:
                            relocations.add(page_rva + (entry & 0x0FFF))
                    cursor += block_size
        self.highlow_relocations = frozenset(relocations)

    def _map_rva(self, rva: int, size: int, *, require_executable: bool) -> int:
        if rva < 0 or size <= 0:
            raise ValueError("invalid RVA range")
        for section in self.sections:
            mapped_size = max(section.virtual_size, section.raw_size)
            if not (section.virtual_address <= rva and rva + size <= section.virtual_address + mapped_size):
                continue
            if require_executable and not (section.characteristics & _IMAGE_SCN_MEM_EXECUTE):
                raise ValueError(f"RVA 0x{rva:08x} is not in an executable section")
            delta = rva - section.virtual_address
            if delta + size > section.raw_size:
                raise ValueError(f"RVA 0x{rva:08x} has truncated section data")
            raw = section.raw_offset + delta
            if raw + size > len(self.data):
                raise ValueError(f"RVA 0x{rva:08x} has truncated file data")
            return raw
        qualifier = "executable section" if require_executable else "section"
        raise ValueError(f"RVA 0x{rva:08x} is outside every {qualifier}")

    def executable_bytes(self, rva: int, size: int) -> bytes:
        raw = self._map_rva(rva, size, require_executable=True)
        return self.data[raw : raw + size]

    def overlaps_highlow_relocation(self, rva: int, size: int) -> bool:
        end = rva + size
        return any(reloc_rva < end and reloc_rva + 4 > rva for reloc_rva in self.highlow_relocations)


def _unpack_from(format_string: str, data: bytes, offset: int, label: str) -> tuple[Any, ...]:
    size = struct.calcsize(format_string)
    if offset < 0 or offset + size > len(data):
        raise ValueError(f"truncated {label}")
    return struct.unpack_from(format_string, data, offset)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_bytes(path: str | Path, label: str) -> bytes:
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise ValueError(f"could not read {label}: {exc}") from exc


def _require_canonical(data: bytes) -> str:
    if len(data) != CANONICAL_SIZE:
        raise ValueError(f"canonical executable size mismatch: {len(data)} != {CANONICAL_SIZE}")
    digest = _sha256(data)
    if digest != CANONICAL_SHA256:
        raise ValueError("canonical executable SHA-256 mismatch")
    return digest


def _load_template(template: str | Path) -> tuple[str, str]:
    candidate = _read_bytes(template, "CDB template")
    canonical = _read_bytes(DEFAULT_TEMPLATE, "tracked CDB template")
    if _sha256(canonical) != TEMPLATE_SHA256 or candidate != canonical:
        raise ValueError("CDB template drift detected")
    try:
        text = candidate.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("CDB template must be ASCII") from exc
    placeholders = _PLACEHOLDER.findall(text)
    if set(placeholders) != {"FINGERPRINT_CONDITION", "ARM_INPUT_BREAKPOINT"} or len(placeholders) != 2:
        raise ValueError("CDB template placeholders do not match the locked protocol")
    return text, _sha256(candidate)


def _rva(rva: int) -> str:
    return f"BEA+0x{rva:08x}"


def _event_command(
    event: str, identity: str, object_expression: str, register: str, breakpoint_id: int
) -> str:
    return (
        f'ba{breakpoint_id} e1 /1 {_rva(PROBE_RVAS[event])} ".printf '
        f'\\"MORPH_CANARY_EVENT event={event} identityEqual=%d '
        f'rawStateU32=0x%08x\\n\\", ({identity}), poi({object_expression}+0x260); '
        f'r @{register}=1; gc"'
    )


def _arm_input_breakpoint() -> str:
    hardware_commands = (
        _event_command("battleEngineMorph", "@ecx==@$t3", "@$t3", "$t0", 0),
        _event_command("battleEngineMove", "@ecx==@$t3", "@$t3", "$t1", 1),
        _event_command("jetPartMove", "poi(@ecx+0x18)==@$t3", "@$t3", "$t2", 2),
    )
    hardware = "; ".join(
        part for breakpoint_id, command in enumerate(hardware_commands) for part in (command, f"bd {breakpoint_id}")
    )
    input_breakpoint = (
        f"ba3 e1 {_rva(PROBE_RVAS['playerTransformAction'])} \""
        f".if ((poi(@esp+0x4)==0x21) && (@ecx==poi({_rva(P0_GLOBAL_RVA)}))) {{ "
        f"bc 3; r @$t3=poi(@ecx+0x1c); .printf \\\"MORPH_CANARY_EVENT "
        f"event=playerTransformAction identityEqual=1 rawStateU32=0x%08x\\n\\\", "
        f"poi(@$t3+0x260); be 0 1 2; g }} .else {{ gc }}\""
    )
    return f"{hardware}; {input_breakpoint}"


def render_private_command(executable: str | Path, template: str | Path) -> RenderedCommand:
    executable_bytes = _read_bytes(executable, "executable")
    executable_sha256 = _require_canonical(executable_bytes)
    image = Pe32Image(executable_bytes)
    template_text, template_sha256 = _load_template(template)

    targets: list[ProbeFingerprint] = []
    conditions: list[str] = []
    for event in EXPECTED_EVENTS:
        rva = PROBE_RVAS[event]
        region = image.executable_bytes(rva, FINGERPRINT_SIZE)
        overlap = image.overlaps_highlow_relocation(rva, FINGERPRINT_SIZE)
        if overlap:
            raise ValueError(f"fingerprint for {event} overlaps a HIGHLOW relocation")
        targets.append(
            ProbeFingerprint(
                event=event,
                rva=rva,
                size=FINGERPRINT_SIZE,
                sha256=_sha256(region),
                relocation_overlap=overlap,
            )
        )
        conditions.extend(
            f"by({_rva(rva + offset)})==0x{value:02x}" for offset, value in enumerate(region)
        )

    rendered_text = template_text.replace(
        "{{FINGERPRINT_CONDITION}}", " && ".join(conditions)
    ).replace("{{ARM_INPUT_BREAKPOINT}}", _arm_input_breakpoint())
    if "{{" in rendered_text or "}}" in rendered_text:
        raise ValueError("unresolved CDB template placeholder")
    rendered_bytes = rendered_text.encode("ascii")
    return RenderedCommand(
        text=rendered_text,
        sha256=_sha256(rendered_bytes),
        template_sha256=template_sha256,
        executable_sha256=executable_sha256,
        fingerprint_size=FINGERPRINT_SIZE,
        targets=tuple(targets),
    )


def validate_private_command(
    path: str | Path, executable: str | Path, template: str | Path
) -> RenderedCommand:
    rendered = render_private_command(executable, template)
    actual = _read_bytes(path, "generated command")
    expected = rendered.text.encode("ascii")
    if actual != expected or _sha256(actual) != rendered.sha256:
        raise ValueError("generated command drift detected")
    return rendered


_PRIVATE_RUN_KEYS = {
    "schema",
    "executablePath",
    "templatePath",
    "commandPath",
    "receiptSha256",
    "commandSha256",
    "templateSha256",
    "executableSha256",
    "fingerprints",
    "sourceUnchanged",
    "copyUnchanged",
    "cleanup",
}
_FINGERPRINT_KEYS = {"event", "rva", "length", "sha256"}
_CLEANUP_KEYS = {
    "keysReleased",
    "cdbDetached",
    "managedProcessStopped",
    "ownedProcessCount",
}
_PUBLIC_RUN_KEYS = {
    "role",
    "receiptSha256",
    "rawCaptureSha256",
    "commandSha256",
    "templateSha256",
    "executableSha256",
    "fingerprints",
    "eventCounts",
    "events",
    "sourceUnchanged",
    "copyUnchanged",
    "cleanup",
}
_EVENT_KEYS = {"event", "ordinal", "identityEqual", "rawStateU32"}
_MATRIX_KEYS = {"schema", "toolVersion", "specimen", "runs"}
_SPECIMEN_KEYS = {"size", "sha256"}


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be an object")
    return value


def _require_exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ValueError(
            f"{label} keys mismatch: missing={sorted(expected - actual)} extra={sorted(actual - expected)}"
        )


def _require_digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _HEX_SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _require_bool(value: Any, label: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{label} must be a boolean")
    return value


def _require_nonnegative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value


def _read_json_object(path: str | Path, label: str) -> dict[str, Any]:
    raw = _read_bytes(path, label)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid UTF-8 JSON") from exc
    return _require_object(value, label)


def _validate_fingerprints(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) != len(EXPECTED_EVENTS):
        raise ValueError(f"{label} must contain the four expected fingerprint regions")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        fingerprint = _require_object(item, f"{label}[{index}]")
        _require_exact_keys(fingerprint, _FINGERPRINT_KEYS, f"{label}[{index}]")
        event = EXPECTED_EVENTS[index]
        if fingerprint["event"] != event:
            raise ValueError(f"{label} event order mismatch")
        if type(fingerprint["rva"]) is not int or fingerprint["rva"] != PROBE_RVAS[event]:
            raise ValueError(f"{label} RVA mismatch for {event}")
        if type(fingerprint["length"]) is not int or fingerprint["length"] != FINGERPRINT_SIZE:
            raise ValueError(f"{label} region length mismatch for {event}")
        _require_digest(fingerprint["sha256"], f"{label} SHA-256 for {event}")
        result.append(dict(fingerprint))
    return result


def _validate_cleanup(value: Any, label: str, *, require_success: bool) -> dict[str, Any]:
    cleanup = _require_object(value, label)
    _require_exact_keys(cleanup, _CLEANUP_KEYS, label)
    keys_released = _require_bool(cleanup["keysReleased"], f"{label}.keysReleased")
    cdb_detached = _require_bool(cleanup["cdbDetached"], f"{label}.cdbDetached")
    process_stopped = _require_bool(
        cleanup["managedProcessStopped"], f"{label}.managedProcessStopped"
    )
    owned_count = _require_nonnegative_int(cleanup["ownedProcessCount"], f"{label}.ownedProcessCount")
    if require_success and not (keys_released and cdb_detached and process_stopped and owned_count == 0):
        raise ValueError(f"{label} does not record successful terminal cleanup")
    return dict(cleanup)


def _parse_events(cdb_log: str | Path) -> tuple[list[dict[str, Any]], str]:
    raw = _read_bytes(cdb_log, "raw CDB capture")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("raw CDB capture must be ASCII") from exc
    lines = [line.strip() for line in text.splitlines()]
    if any("MORPH_CANARY_CODE_MISMATCH" in line for line in lines):
        raise ValueError("raw CDB capture contains MORPH_CANARY_CODE_MISMATCH")
    for marker in ("MORPH_CANARY_BEGIN", "MORPH_CANARY_READY"):
        if lines.count(marker) != 1:
            raise ValueError(f"raw CDB capture must contain exactly one {marker} marker")
    begin_index = lines.index("MORPH_CANARY_BEGIN")
    ready_index = lines.index("MORPH_CANARY_READY")
    if begin_index >= ready_index:
        raise ValueError("MORPH_CANARY_BEGIN must appear before MORPH_CANARY_READY")
    events: list[dict[str, Any]] = []
    for line_index, line in enumerate(lines):
        if not line.startswith("MORPH_CANARY_EVENT"):
            continue
        if line_index < ready_index:
            raise ValueError("raw CDB capture contains an event before MORPH_CANARY_READY")
        match = _EVENT_LINE.fullmatch(line)
        if match is None:
            raise ValueError("malformed morph canary event line")
        event = match.group("event")
        if event not in EXPECTED_EVENTS:
            raise ValueError(f"unexpected morph canary event: {event}")
        events.append(
            {
                "event": event,
                "ordinal": len(events),
                "identityEqual": match.group("equal") == "1",
                "rawStateU32": match.group("state").lower(),
            }
        )
    return events, _sha256(raw)


def materialize_run(live_artifact: str | Path, cdb_log: str | Path, role: str) -> dict[str, Any]:
    if role not in RUN_ROLES:
        raise ValueError(f"invalid run role: {role}")
    artifact = _read_json_object(live_artifact, "private live artifact")
    _require_exact_keys(artifact, _PRIVATE_RUN_KEYS, "private live artifact")
    if artifact["schema"] != PRIVATE_RUN_SCHEMA:
        raise ValueError("private live artifact schema mismatch")
    for key in ("executablePath", "templatePath", "commandPath"):
        if not isinstance(artifact[key], str) or not artifact[key]:
            raise ValueError(f"private live artifact {key} must be a non-empty path")
    rendered = validate_private_command(
        artifact["commandPath"], artifact["executablePath"], artifact["templatePath"]
    )
    fingerprints = _validate_fingerprints(artifact["fingerprints"], "private fingerprints")
    receipt = _require_digest(artifact["receiptSha256"], "receiptSha256")
    command = _require_digest(artifact["commandSha256"], "commandSha256")
    template = _require_digest(artifact["templateSha256"], "templateSha256")
    if template != TEMPLATE_SHA256:
        raise ValueError("private live artifact template SHA-256 does not match the locked template")
    executable = _require_digest(artifact["executableSha256"], "executableSha256")
    if executable != CANONICAL_SHA256:
        raise ValueError("private live artifact executable SHA-256 is not canonical")
    expected_fingerprints = [
        {
            "event": target.event,
            "rva": target.rva,
            "length": target.size,
            "sha256": target.sha256,
        }
        for target in rendered.targets
    ]
    if command != rendered.sha256:
        raise ValueError("private live artifact command SHA-256 does not match the rendered command")
    if template != rendered.template_sha256:
        raise ValueError("private live artifact template SHA-256 does not match the rendered command")
    if executable != rendered.executable_sha256:
        raise ValueError("private live artifact executable SHA-256 does not match the rendered command")
    if fingerprints != expected_fingerprints:
        raise ValueError("private live artifact fingerprints do not match the canonical executable")
    source_unchanged = _require_bool(artifact["sourceUnchanged"], "sourceUnchanged")
    copy_unchanged = _require_bool(artifact["copyUnchanged"], "copyUnchanged")
    cleanup = _validate_cleanup(artifact["cleanup"], "private cleanup", require_success=False)
    events, raw_capture = _parse_events(cdb_log)
    counts = Counter(event["event"] for event in events)
    result = {
        "role": role,
        "receiptSha256": receipt,
        "rawCaptureSha256": raw_capture,
        "commandSha256": command,
        "templateSha256": template,
        "executableSha256": executable,
        "fingerprints": fingerprints,
        "eventCounts": {event: counts[event] for event in EXPECTED_EVENTS},
        "events": events,
        "sourceUnchanged": source_unchanged,
        "copyUnchanged": copy_unchanged,
        "cleanup": cleanup,
    }
    _validate_public_run(result, RUN_ROLES.index(role))
    return result


def materialize_matrix(runs: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    run_list = [dict(run) for run in runs]
    payload = {
        "schema": PUBLIC_SCHEMA,
        "toolVersion": TOOL_VERSION,
        "specimen": {"size": CANONICAL_SIZE, "sha256": CANONICAL_SHA256},
        "runs": run_list,
    }
    validate_public_matrix(payload)
    return payload


def _validate_public_run(run: Any, index: int) -> None:
    label = f"runs[{index}]"
    value = _require_object(run, label)
    _require_exact_keys(value, _PUBLIC_RUN_KEYS, label)
    if value["role"] != RUN_ROLES[index]:
        raise ValueError("public matrix run roles are missing or reordered")
    for key in (
        "receiptSha256",
        "rawCaptureSha256",
        "commandSha256",
        "templateSha256",
        "executableSha256",
    ):
        _require_digest(value[key], f"{label}.{key}")
    if value["templateSha256"] != TEMPLATE_SHA256:
        raise ValueError(f"{label} template SHA-256 does not match the locked template")
    if value["executableSha256"] != CANONICAL_SHA256:
        raise ValueError(f"{label} executable SHA-256 is not canonical")
    _validate_fingerprints(value["fingerprints"], f"{label}.fingerprints")
    counts = _require_object(value["eventCounts"], f"{label}.eventCounts")
    _require_exact_keys(counts, set(EXPECTED_EVENTS), f"{label}.eventCounts")
    for event in EXPECTED_EVENTS:
        _require_nonnegative_int(counts[event], f"{label}.eventCounts.{event}")
    if not isinstance(value["events"], list):
        raise ValueError(f"{label}.events must be an array")
    observed_counts: Counter[str] = Counter()
    observed_order: list[str] = []
    for ordinal, item in enumerate(value["events"]):
        event = _require_object(item, f"{label}.events[{ordinal}]")
        _require_exact_keys(event, _EVENT_KEYS, f"{label}.events[{ordinal}]")
        if event["event"] not in EXPECTED_EVENTS:
            raise ValueError(f"{label} contains an unexpected event")
        if type(event["ordinal"]) is not int or event["ordinal"] != ordinal:
            raise ValueError(f"{label} event ordinal mismatch")
        _require_bool(event["identityEqual"], f"{label}.events[{ordinal}].identityEqual")
        if not isinstance(event["rawStateU32"], str) or not _RAW_U32.fullmatch(event["rawStateU32"]):
            raise ValueError(f"{label} rawStateU32 must be lowercase 8-digit hex")
        observed_counts[event["event"]] += 1
        observed_order.append(event["event"])
    if dict(observed_counts) != {event: counts[event] for event in EXPECTED_EVENTS if counts[event]}:
        raise ValueError(f"{label} event counts do not match the event array")
    source_unchanged = _require_bool(value["sourceUnchanged"], f"{label}.sourceUnchanged")
    copy_unchanged = _require_bool(value["copyUnchanged"], f"{label}.copyUnchanged")
    _validate_cleanup(value["cleanup"], f"{label}.cleanup", require_success=True)
    if not source_unchanged or not copy_unchanged:
        raise ValueError(f"{label} source/copy integrity is not unchanged")
    if value["role"] == "noInputControl":
        if observed_order or any(counts.values()):
            raise ValueError("no-input control contains transform-chain events")
    else:
        if tuple(observed_order) != EXPECTED_EVENTS or any(counts[event] != 1 for event in EXPECTED_EVENTS):
            raise ValueError(f"{label} positive event order/count mismatch")
        if not all(event["identityEqual"] for event in value["events"]):
            raise ValueError(f"{label} contains an intra-run identity mismatch")


def validate_public_matrix(payload: Any) -> None:
    matrix = _require_object(payload, "public matrix")
    _require_exact_keys(matrix, _MATRIX_KEYS, "public matrix")
    if matrix["schema"] != PUBLIC_SCHEMA:
        raise ValueError("public matrix schema mismatch")
    if matrix["toolVersion"] != TOOL_VERSION:
        raise ValueError("public matrix tool version mismatch")
    specimen = _require_object(matrix["specimen"], "public matrix specimen")
    _require_exact_keys(specimen, _SPECIMEN_KEYS, "public matrix specimen")
    if type(specimen["size"]) is not int or specimen["size"] != CANONICAL_SIZE:
        raise ValueError("public matrix canonical specimen size mismatch")
    if specimen["sha256"] != CANONICAL_SHA256:
        raise ValueError("public matrix canonical specimen SHA-256 mismatch")
    runs = matrix["runs"]
    if not isinstance(runs, list) or len(runs) != len(RUN_ROLES):
        raise ValueError("public matrix must contain exactly three runs")
    for index, run in enumerate(runs):
        _validate_public_run(run, index)
    receipts = [run["receiptSha256"] for run in runs]
    if len(set(receipts)) != len(receipts):
        raise ValueError("public matrix receipts must be distinct across runs")
    captures = [run["rawCaptureSha256"] for run in runs]
    if len(set(captures)) != len(captures):
        raise ValueError("public matrix raw capture digests must be distinct across runs")
    for key in ("commandSha256", "templateSha256", "executableSha256", "fingerprints"):
        if any(run[key] != runs[0][key] for run in runs[1:]):
            raise ValueError(f"public matrix {key} values must be identical across runs")


def _check_matrix(path: str | Path) -> None:
    validate_public_matrix(_read_json_object(path, "public matrix"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="validate a sanitized public matrix")
    check.add_argument("--matrix", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.command == "check":
        _check_matrix(args.matrix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
