#!/usr/bin/env python3
"""Platform-neutral scalar walker-forward trajectory sampling and analysis."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import math
from pathlib import PureWindowsPath
import statistics
import struct
from typing import Callable, Mapping, Protocol, Sequence

import battleengine_walker_trajectory_schema as public_schema


P0_GLOBAL_RVA = 0x004A9D3C
# These are narrow, compositional evidence anchors rather than a claim that the
# complete CGame layout is known.  Wave405's retail caller passes
# &DAT_008a9a98 as the CGame receiver, proving inline object storage rather than
# a pointer-global interpretation.  Wave406 identifies current-level at the
# receiver's +0x2a0.  The accepted Level-850 CGame__Render observer reads
# split mode and P0/P1 from that same receiver at +0x38/+0x29c/+0x2a4/+0x2a8,
# and its checker-backed contract accepted players=2, level=850, split=1, and
# distinct nonzero player identities.  Keeping
# the tracked identifiers here makes those exact, bounded premises auditable.
C_GAME_READINESS_PROVENANCE = (
    (
        "inlineCGameReceiver",
        ((
            "release/readiness/ghidra_cgame_draw_game_stuff_wave405_2026-05-14.md",
            "CGame__DrawGameStuff(&DAT_008a9a98)",
        ),),
    ),
    (
        "currentLevelOffset2A0",
        ((
            "release/readiness/ghidra_cgame_is_multiplayer_wave406_2026-05-14.md",
            "CGame+0x2a0",
        ),),
    ),
    (
        "playerCountOffset29C",
        (
            (
                "tools/runtime-probes/local-multiplayer-level850-input-state-delta-observer.cdb.txt",
                "poi(@ecx+0x29c)",
            ),
            (
                "release/readiness/local_multiplayer_static_runtime_contract_2026-06-17.md",
                "players=2",
            ),
        ),
    ),
    (
        "playerZeroOffset2A4",
        (
            (
                "tools/runtime-probes/local-multiplayer-level850-input-state-delta-observer.cdb.txt",
                "poi(@ecx+0x2a4)",
            ),
            (
                "release/readiness/local_multiplayer_static_runtime_contract_2026-06-17.md",
                "distinct nonzero `p0=",
            ),
        ),
    ),
    (
        "horizontalSplitOffset38",
        (
            (
                "tools/runtime-probes/local-multiplayer-level850-input-state-delta-observer.cdb.txt",
                "by(@ecx+0x38)",
            ),
            (
                "release/readiness/local_multiplayer_static_runtime_contract_2026-06-17.md",
                "horizSplit=1",
            ),
        ),
    ),
    (
        "playerOneOffset2A8",
        (
            (
                "tools/runtime-probes/local-multiplayer-level850-input-state-delta-observer.cdb.txt",
                "poi(@ecx+0x2a8)",
            ),
            (
                "release/readiness/local_multiplayer_static_runtime_contract_2026-06-17.md",
                "and `p1=",
            ),
        ),
    ),
)
C_GAME_OBJECT_RVA = 0x004A9A98
C_GAME_HORIZONTAL_SPLIT_OFFSET = 0x38
C_GAME_PLAYER_COUNT_OFFSET = 0x29C
C_GAME_LEVEL_OFFSET = 0x2A0
C_GAME_P0_OFFSET = 0x2A4
C_GAME_P1_OFFSET = 0x2A8
if C_GAME_OBJECT_RVA + C_GAME_P0_OFFSET != P0_GLOBAL_RVA:
    raise RuntimeError("accepted inline CGame/P0 layout identity drifted")
PLAYER_BATTLE_ENGINE_OFFSET = 0x1C
BATTLE_ENGINE_WALKER_OFFSET = 0x578
WALKER_MAIN_PART_OFFSET = 0x20
BATTLE_ENGINE_STATE_OFFSET = 0x260
BATTLE_ENGINE_POSITION_OFFSET = 0x1C
BATTLE_ENGINE_VELOCITY_OFFSET = 0x7C
WALKER_CONTROL_OFFSET = 0x40
WALKER_STATE_RAW = 0x00000002
NEUTRAL_CONTROL_RAW = 0x00000000
FORWARD_CONTROL_RAW = 0xBF800000
MAX_COHERENCE_PAIRS = 3
CADENCE_MS = 10
FREQUENCY_FIXTURE = 10_000_000
PHASE_TARGETS = {"baseline": 50, "hold": 75, "release": 75}
PHASE_MINIMUMS = {"baseline": 48, "hold": 72, "release": 72}
NODE_TIMES_MS = (100, 200, 350, 500)


class SampleError(ValueError):
    pass


class RuntimeNotReady(SampleError):
    """An exact path-free runtime state that may be retried before baseline."""

    def __init__(self, *, hop: str | None = None, field: str | None = None) -> None:
        if (hop is None) == (field is None):
            raise ValueError("exactly one readiness hop or field is required")
        self.hop = hop
        self.field = field
        super().__init__(
            f"null runtime {hop} hop is not ready" if hop is not None
            else f"runtime not ready at {field} field"
        )


class AttemptError(ValueError):
    pass


class MemoryReader(Protocol):
    def read(self, address: int, size: int) -> bytes: ...


class QInput(Protocol):
    def key_down(self) -> bool: ...
    def key_up(self) -> bool: ...


class RuntimeGuard(Protocol):
    def revalidate_receipt(self) -> bool: ...
    def foreground_matches(self) -> bool: ...
    def interference_detected(self) -> bool: ...


@dataclass(frozen=True)
class RawSample:
    tick: int
    phase: str
    slot: int
    position: tuple[float, float, float]
    velocity: tuple[float, float, float]
    state_raw: int
    control_raw: int


@dataclass(frozen=True)
class ReadinessProbe:
    level: int
    player_count: int
    horizontal_split: int
    state_raw: int
    control_raw: int


@dataclass(frozen=True)
class LatencyInterval:
    lower_ms: int
    upper_ms: int


@dataclass(frozen=True)
class InputWindowResult:
    value: object
    down_bracket: tuple[int, int]
    up_bracket: tuple[int, int]


@dataclass
class AttemptIntegrity:
    receipt_revalidated: bool = True
    foreground_maintained: bool = True
    key_down_confirmed: bool = True
    key_up_confirmed: bool = True
    interference_detected: bool = False
    cleanup_confirmed: bool = True


@dataclass
class AttemptTrace:
    attempt: int
    receipt_sha256: str
    run_digest: str
    frequency: int
    samples: dict[str, list[RawSample]]
    down_bracket: tuple[int, int]
    up_bracket: tuple[int, int]
    integrity: AttemptIntegrity = field(default_factory=AttemptIntegrity)


@dataclass(frozen=True)
class AttemptMetrics:
    attempt: int
    accepted: bool
    receipt_sha256: str
    run_digest: str
    sample_counts: dict[str, int]
    steady_speed: float
    baseline_b95_speed: float
    baseline_endpoint_displacement: float
    response_threshold: float
    response_latency: LatencyInterval
    release_latency: LatencyInterval
    steady_slope: float
    normalized_response: dict[str, float]
    velocity_hold_to_baseline_ratio: float
    receipt_revalidated: bool
    foreground_maintained: bool
    key_up_confirmed: bool
    cleanup_confirmed: bool


@dataclass(frozen=True)
class ReceiptIdentity:
    receipt_sha256: str
    process_id: int
    started_at_utc: str
    executable_sha256: str
    module_path: str
    module_base: int
    module_size: int
    window_handle: int
    window_process_id: int
    manifest_sha256: str
    launch_arguments: tuple[str, ...]
    artifact_root: str
    artifact_path: str
    path_is_reparse: bool = False

    @staticmethod
    def synthetic() -> "ReceiptIdentity":
        return ReceiptIdentity(
            receipt_sha256="a" * 64,
            process_id=4242,
            started_at_utc="2026-07-13T12:00:00Z",
            executable_sha256="b" * 64,
            module_path="C:/synthetic/role/BEA.exe",
            module_base=0x10000000,
            module_size=0x260000,
            window_handle=0x1234,
            window_process_id=4242,
            manifest_sha256="c" * 64,
            launch_arguments=("-skipfmv", "-level", "850", "-configuration", "2"),
            artifact_root="C:/synthetic/role",
            artifact_path="C:/synthetic/role/private/trace.json",
        )


def replace_receipt(value: ReceiptIdentity, **changes: object) -> ReceiptIdentity:
    return replace(value, **changes)


def replace_metrics(value: AttemptMetrics, **changes: object) -> AttemptMetrics:
    return replace(value, **changes)


def replace_sample(value: RawSample, **changes: object) -> RawSample:
    return replace(value, **changes)


def _under(path: str, root: str) -> bool:
    child_path = PureWindowsPath(path)
    root_path = PureWindowsPath(root)
    if not child_path.is_absolute() or not root_path.is_absolute():
        return False
    if any(part in (".", "..") for part in (*child_path.parts, *root_path.parts)):
        return False
    child = tuple(part.casefold() for part in child_path.parts)
    parent = tuple(part.casefold() for part in root_path.parts)
    return len(child) > len(parent) and child[:len(parent)] == parent


def require_receipt_match(expected: ReceiptIdentity, actual: ReceiptIdentity) -> None:
    if actual.path_is_reparse:
        raise AttemptError("receipt path is reparse routed")
    if not _under(actual.artifact_path, actual.artifact_root):
        raise AttemptError("receipt artifact path escaped its root")
    fields = (
        "receipt_sha256", "process_id", "started_at_utc", "executable_sha256",
        "module_path", "module_base", "module_size", "window_handle",
        "window_process_id", "manifest_sha256", "launch_arguments", "artifact_root",
        "artifact_path",
    )
    if any(getattr(expected, name) != getattr(actual, name) for name in fields):
        raise AttemptError("receipt identity mismatch")


def _checked_address(base: int, offset: int, size: int) -> int:
    if base <= 0 or base & 3:
        raise SampleError("read base must be nonzero and 4-byte aligned")
    address = base + offset
    if address > 0xFFFFFFFF or address + size - 1 > 0xFFFFFFFF:
        raise SampleError("read address overflow")
    if address & 3:
        raise SampleError("read address must be 4-byte aligned")
    return address


def _read_exact(reader: MemoryReader, address: int, size: int) -> bytes:
    if address & 3:
        raise SampleError("read address must be 4-byte aligned")
    value = reader.read(address, size)
    if len(value) != size:
        raise SampleError(f"short read: expected {size}, found {len(value)}")
    return value


def _read_u32(reader: MemoryReader, base: int, offset: int, *, hop: str | None = None) -> int:
    address = _checked_address(base, offset, 4)
    value = struct.unpack("<I", _read_exact(reader, address, 4))[0]
    if value == 0:
        if hop is not None:
            raise RuntimeNotReady(hop=hop)
        raise SampleError("null pointer in runtime chain")
    if value & 3:
        raise SampleError("runtime pointer must be 4-byte aligned")
    return value


def _acquire(
    reader: MemoryReader,
    module_base: int,
    *,
    retryable_hops: frozenset[str],
) -> tuple[tuple[int, int, int], bytes]:
    def first_pointer(base: int, offset: int, hop: str) -> int:
        return _read_u32(
            reader,
            base,
            offset,
            hop=hop if hop in retryable_hops else None,
        )

    p0 = first_pointer(module_base, P0_GLOBAL_RVA, "p0")
    battle_engine = first_pointer(p0, PLAYER_BATTLE_ENGINE_OFFSET, "battleEngine")
    walker = first_pointer(battle_engine, BATTLE_ENGINE_WALKER_OFFSET, "walker")
    backpointer = first_pointer(walker, WALKER_MAIN_PART_OFFSET, "backpointer")
    if backpointer != battle_engine:
        raise SampleError("WalkerPart backpointer does not match BattleEngine")
    state = _read_exact(reader, _checked_address(battle_engine, BATTLE_ENGINE_STATE_OFFSET, 4), 4)
    position = _read_exact(reader, _checked_address(battle_engine, BATTLE_ENGINE_POSITION_OFFSET, 12), 12)
    velocity = _read_exact(reader, _checked_address(battle_engine, BATTLE_ENGINE_VELOCITY_OFFSET, 12), 12)
    control = _read_exact(reader, _checked_address(walker, WALKER_CONTROL_OFFSET, 4), 4)
    p0_after = _read_u32(reader, module_base, P0_GLOBAL_RVA)
    battle_engine_after = _read_u32(reader, p0_after, PLAYER_BATTLE_ENGINE_OFFSET)
    walker_after = _read_u32(reader, battle_engine_after, BATTLE_ENGINE_WALKER_OFFSET)
    backpointer_after = _read_u32(reader, walker_after, WALKER_MAIN_PART_OFFSET)
    if (p0, battle_engine, walker) != (p0_after, battle_engine_after, walker_after):
        raise SampleError("runtime pointer chain changed during acquisition")
    if backpointer_after != battle_engine:
        raise SampleError("WalkerPart backpointer changed during acquisition")
    return (p0, battle_engine, walker), state + position + velocity + control


def read_coherent_sample(
    reader: MemoryReader,
    module_base: int,
    *,
    tick: int,
    phase: str,
    slot: int,
    retryable_hops: frozenset[str] = frozenset(
        {"p0", "battleEngine", "walker", "backpointer"}
    ),
    require_walker_state: bool = True,
) -> RawSample:
    _checked_address(module_base, P0_GLOBAL_RVA, 4)
    first_retryable_hops = retryable_hops
    for _ in range(MAX_COHERENCE_PAIRS):
        first_chain, first = _acquire(
            reader,
            module_base,
            retryable_hops=first_retryable_hops,
        )
        first_retryable_hops = frozenset()
        second_chain, second = _acquire(
            reader,
            module_base,
            retryable_hops=frozenset(),
        )
        if first_chain != second_chain or first != second:
            continue
        state_raw = struct.unpack_from("<I", first, 0)[0]
        if require_walker_state and state_raw != WALKER_STATE_RAW:
            raise SampleError("raw walker state gate mismatch")
        position = struct.unpack_from("<3f", first, 4)
        velocity = struct.unpack_from("<3f", first, 16)
        control_raw = struct.unpack_from("<I", first, 28)[0]
        if not all(math.isfinite(value) for value in (*position, *velocity)):
            raise SampleError("position and velocity values must be finite")
        control = struct.unpack_from("<f", first, 28)[0]
        if not math.isfinite(control):
            raise SampleError("control value must be finite")
        return RawSample(tick, phase, slot, position, velocity, state_raw, control_raw)
    raise SampleError("torn runtime sample after three coherence pairs")


def read_readiness_probe(reader: MemoryReader, module_base: int) -> ReadinessProbe:
    """Read the exact retryable Level-850 walker readiness fields coherently."""
    game = _checked_address(module_base, C_GAME_OBJECT_RVA, 4)
    first_level = struct.unpack(
        "<I", _read_exact(reader, _checked_address(game, C_GAME_LEVEL_OFFSET, 4), 4)
    )[0]
    first_players = struct.unpack(
        "<I", _read_exact(reader, _checked_address(game, C_GAME_PLAYER_COUNT_OFFSET, 4), 4)
    )[0]
    first_split = struct.unpack(
        "<B", _read_exact(reader, _checked_address(game, C_GAME_HORIZONTAL_SPLIT_OFFSET, 1), 1)
    )[0]
    if first_level != 850 or first_players != 2 or first_split != 1:
        second_level = struct.unpack(
            "<I", _read_exact(reader, _checked_address(game, C_GAME_LEVEL_OFFSET, 4), 4)
        )[0]
        second_players = struct.unpack(
            "<I", _read_exact(reader, _checked_address(game, C_GAME_PLAYER_COUNT_OFFSET, 4), 4)
        )[0]
        second_split = struct.unpack(
            "<B", _read_exact(reader, _checked_address(game, C_GAME_HORIZONTAL_SPLIT_OFFSET, 1), 1)
        )[0]
        if (first_level, first_players, first_split) != (
            second_level, second_players, second_split,
        ):
            raise SampleError("runtime readiness fields changed during acquisition")
        if first_level != 850:
            raise RuntimeNotReady(field="level")
        if first_players != 2:
            raise RuntimeNotReady(field="playerCount")
        raise RuntimeNotReady(field="horizontalSplit")
    first_p0 = _read_u32(reader, game, C_GAME_P0_OFFSET, hop="p0")
    first_p1 = _read_u32(reader, game, C_GAME_P1_OFFSET, hop="p1")
    if first_p0 == first_p1:
        raise SampleError("runtime player identities must be distinct")
    try:
        sample = read_coherent_sample(
            reader,
            module_base,
            tick=0,
            phase="readiness",
            slot=0,
            retryable_hops=frozenset({"battleEngine", "walker", "backpointer"}),
            require_walker_state=False,
        )
    except SampleError:
        raise
    second_level = struct.unpack(
        "<I", _read_exact(reader, _checked_address(game, C_GAME_LEVEL_OFFSET, 4), 4)
    )[0]
    second_players = struct.unpack(
        "<I", _read_exact(reader, _checked_address(game, C_GAME_PLAYER_COUNT_OFFSET, 4), 4)
    )[0]
    second_split = struct.unpack(
        "<B", _read_exact(reader, _checked_address(game, C_GAME_HORIZONTAL_SPLIT_OFFSET, 1), 1)
    )[0]
    second_p0 = _read_u32(reader, game, C_GAME_P0_OFFSET)
    second_p1 = _read_u32(reader, game, C_GAME_P1_OFFSET)
    if (first_level, first_players, first_split, first_p0, first_p1) != (
        second_level, second_players, second_split, second_p0, second_p1,
    ):
        raise SampleError("runtime readiness fields changed during acquisition")
    if second_p0 == second_p1:
        raise SampleError("runtime player identities must be distinct")
    if sample.state_raw != WALKER_STATE_RAW:
        raise RuntimeNotReady(field="state")
    if sample.control_raw != NEUTRAL_CONTROL_RAW:
        raise RuntimeNotReady(field="control")
    return ReadinessProbe(
        first_level, first_players, first_split, sample.state_raw, sample.control_raw,
    )


def synthetic_schedule_ticks(*, frequency: int = FREQUENCY_FIXTURE) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    global_slot = 0
    for phase in ("baseline", "hold", "release"):
        count = PHASE_TARGETS[phase]
        result[phase] = [
            round((global_slot + index) * frequency * CADENCE_MS / 1000)
            for index in range(count)
        ]
        global_slot += count
    return result


def validate_schedule(ticks: Mapping[str, Sequence[int]], *, frequency: int) -> None:
    if frequency <= 0:
        raise AttemptError("QPC frequency must be positive")
    if set(ticks) != set(PHASE_TARGETS):
        raise AttemptError("schedule phase set mismatch")
    baseline_rows = list(ticks["baseline"])
    if not baseline_rows:
        raise AttemptError("baseline phase undersampled")
    origin = baseline_rows[0]
    step = frequency * CADENCE_MS / 1000.0
    tolerance = frequency * 0.005
    starts = {
        "baseline": origin,
        "hold": origin + PHASE_TARGETS["baseline"] * step,
        "release": origin + (PHASE_TARGETS["baseline"] + PHASE_TARGETS["hold"]) * step,
    }
    previous_tick: int | None = None
    for phase in ("baseline", "hold", "release"):
        rows = list(ticks[phase])
        if len(rows) < PHASE_MINIMUMS[phase]:
            raise AttemptError(f"{phase} phase undersampled")
        if len(rows) > PHASE_TARGETS[phase]:
            raise AttemptError(f"{phase} phase sample count exceeds its window")
        previous_slot: int | None = None
        for tick in rows:
            slot = round((tick - starts[phase]) / step)
            if slot < 0 or slot >= PHASE_TARGETS[phase]:
                raise AttemptError(f"{phase} sample falls outside its declared window")
            expected = starts[phase] + slot * step
            if abs(tick - expected) > tolerance:
                raise AttemptError("schedule jitter exceeded 5 ms")
            if previous_tick is not None and tick <= previous_tick:
                raise AttemptError("schedule timestamps must be monotonic")
            if previous_slot is not None and slot <= previous_slot:
                raise AttemptError("schedule jitter produced a duplicate or reversed slot")
            if previous_slot is not None and slot - previous_slot > 2:
                raise AttemptError("schedule has consecutive misses or a gap over 20 ms")
            previous_slot = slot
            previous_tick = tick
        if round((rows[0] - starts[phase]) / step) != 0:
            raise AttemptError(f"{phase} phase boundary start is missing")
        if round((rows[-1] - starts[phase]) / step) != PHASE_TARGETS[phase] - 1:
            raise AttemptError(f"{phase} phase boundary end is missing")


def _distance(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _percentile(values: Sequence[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, math.ceil(percentile * len(ordered)) - 1))
    return ordered[index]


def _phase_speeds(samples: Sequence[RawSample], frequency: int) -> list[tuple[RawSample, float]]:
    result: list[tuple[RawSample, float]] = []
    for previous, current in zip(samples, samples[1:]):
        elapsed = (current.tick - previous.tick) / frequency
        if elapsed <= 0:
            raise AttemptError("sample time must be monotonic")
        result.append((current, _distance(current.position, previous.position) / elapsed))
    return result


def _round_interval(
    previous_tick: int,
    qualifying_tick: int,
    bracket: tuple[int, int],
    frequency: int,
) -> LatencyInterval:
    before, after = bracket
    lower = (previous_tick - after) * 1000.0 / frequency
    upper = (qualifying_tick - before) * 1000.0 / frequency
    if lower < 0 or upper < lower:
        raise AttemptError("latency bracket is inconsistent with sampled timestamps")
    return LatencyInterval(
        int(math.floor(lower / CADENCE_MS) * CADENCE_MS),
        int(math.ceil(upper / CADENCE_MS) * CADENCE_MS),
    )


def _first_three(
    rows: Sequence[tuple[RawSample, float]],
    predicate,
    bracket: tuple[int, int],
    frequency: int,
) -> LatencyInterval:
    for index in range(len(rows) - 2):
        if all(predicate(rows[index + offset][1]) for offset in range(3)):
            previous_tick = rows[index - 1][0].tick if index else bracket[1]
            return _round_interval(previous_tick, rows[index][0].tick, bracket, frequency)
    raise AttemptError("response threshold was not sustained")


def _slope(rows: Sequence[tuple[RawSample, float]], frequency: int) -> float:
    times = [(row.tick - rows[0][0].tick) / frequency for row, _ in rows]
    values = [speed for _, speed in rows]
    mean_t = statistics.fmean(times)
    mean_v = statistics.fmean(values)
    denominator = sum((value - mean_t) ** 2 for value in times)
    if denominator == 0:
        return 0.0
    return sum((time - mean_t) * (value - mean_v) for time, value in zip(times, values)) / denominator


def _require_integrity(integrity: AttemptIntegrity) -> None:
    if not integrity.receipt_revalidated:
        raise AttemptError("receipt revalidation failed")
    if not integrity.foreground_maintained:
        raise AttemptError("foreground window changed")
    if not integrity.key_down_confirmed:
        raise AttemptError("key-down was not confirmed")
    if not integrity.key_up_confirmed:
        raise AttemptError("key-up finally was not confirmed")
    if integrity.interference_detected:
        raise AttemptError("operator interference detected")
    if not integrity.cleanup_confirmed:
        raise AttemptError("cleanup and census were not confirmed")


def _require_runtime_guard(guard: RuntimeGuard) -> None:
    if not guard.revalidate_receipt():
        raise AttemptError("receipt revalidation failed")
    if not guard.foreground_matches():
        raise AttemptError("foreground window identity changed")
    if guard.interference_detected():
        raise AttemptError("operator interference detected")


def execute_owned_q_window(
    guard: RuntimeGuard,
    q_input: QInput,
    monotonic_tick: Callable[[], int],
    sampling_batches: Sequence[Callable[[], object]],
) -> InputWindowResult:
    """Bracket an owned Q press while failing closed on identity or focus drift.

    Receipt, foreground, and interference state are revalidated before and
    after every supplied batch. Key-up is attempted even if preflight,
    key-down, timestamping, validation, or a sampling batch fails.
    """

    down_before: int | None = None
    down_after: int | None = None
    up_before: int | None = None
    up_after: int | None = None
    key_up_confirmed = False
    primary_error: BaseException | None = None
    timestamp_error: BaseException | None = None
    values: list[object] = []
    try:
        _require_runtime_guard(guard)
        down_before = monotonic_tick()
        if not q_input.key_down():
            raise AttemptError("key-down was not confirmed")
        down_after = monotonic_tick()
        if down_after < down_before:
            raise AttemptError("monotonic clock moved backwards around key-down")
        _require_runtime_guard(guard)
        for batch in sampling_batches:
            _require_runtime_guard(guard)
            values.append(batch())
            _require_runtime_guard(guard)
    except BaseException as exc:
        primary_error = exc
    finally:
        try:
            up_before = monotonic_tick()
        except BaseException as exc:
            timestamp_error = exc
        try:
            try:
                key_up_confirmed = q_input.key_up()
            except BaseException as exc:
                timestamp_error = timestamp_error or exc
        finally:
            try:
                up_after = monotonic_tick()
            except BaseException as exc:
                timestamp_error = timestamp_error or exc
    if timestamp_error is not None or not key_up_confirmed:
        cleanup_message = (
            "key-up cleanup timestamp or send failed"
            if timestamp_error is not None
            else "key-up finally was not confirmed"
        )
        if primary_error is not None:
            cleanup_message += (
                f" after primary {type(primary_error).__name__}: {primary_error}"
            )
        raise AttemptError(cleanup_message) from (primary_error or timestamp_error)
    if primary_error is not None:
        raise primary_error
    if down_before is None or down_after is None or up_before is None or up_after is None:
        raise AttemptError("input timestamp bracket was not completed")
    if up_before < down_after or up_after < up_before:
        raise AttemptError("monotonic clock moved backwards around key-up")
    _require_runtime_guard(guard)
    return InputWindowResult(tuple(values), (down_before, down_after), (up_before, up_after))


def _validate_trace_rows(trace: AttemptTrace) -> None:
    origin = trace.samples["baseline"][0].tick
    step = trace.frequency * CADENCE_MS / 1000.0
    starts = {
        "baseline": origin,
        "hold": origin + PHASE_TARGETS["baseline"] * step,
        "release": origin + (PHASE_TARGETS["baseline"] + PHASE_TARGETS["hold"]) * step,
    }
    for phase in ("baseline", "hold", "release"):
        for row in trace.samples[phase]:
            if row.phase != phase:
                raise AttemptError("sample phase label does not match its phase")
            expected_slot = round((row.tick - starts[phase]) / step)
            if row.slot != expected_slot:
                raise AttemptError("sample slot does not match its monotonic timestamp")
            if row.state_raw != WALKER_STATE_RAW:
                raise AttemptError("sample walker state gate mismatch")
            if not all(math.isfinite(value) for value in (*row.position, *row.velocity)):
                raise AttemptError("sample position and velocity must be finite")


def _validate_input_bracket(
    bracket: tuple[int, int], phase_start: int, frequency: int, label: str
) -> None:
    before, after = bracket
    step = frequency * CADENCE_MS // 1000
    if before > after:
        raise AttemptError(f"{label} bracket is reversed")
    if after > phase_start or phase_start - before > step:
        raise AttemptError(f"{label} bracket is not bound to the phase boundary")
    if after - before > step:
        raise AttemptError(f"{label} bracket exceeds one sampling cadence")


def analyze_attempt(trace: AttemptTrace) -> AttemptMetrics:
    _require_integrity(trace.integrity)
    validate_schedule({phase: [row.tick for row in rows] for phase, rows in trace.samples.items()}, frequency=trace.frequency)
    baseline = trace.samples["baseline"]
    hold = trace.samples["hold"]
    release = trace.samples["release"]
    _validate_trace_rows(trace)
    _validate_input_bracket(trace.down_bracket, hold[0].tick, trace.frequency, "key-down")
    _validate_input_bracket(trace.up_bracket, release[0].tick, trace.frequency, "key-up")
    if any(row.control_raw != NEUTRAL_CONTROL_RAW for row in baseline):
        raise AttemptError("baseline control field was not neutral")
    if any(row.control_raw != FORWARD_CONTROL_RAW for row in hold):
        raise AttemptError("control field did not prove Q walker-forward state")
    if any(row.control_raw != NEUTRAL_CONTROL_RAW for row in release):
        raise AttemptError("release control field did not return to neutral")

    baseline_speeds = _phase_speeds(baseline, trace.frequency)
    hold_speeds = _phase_speeds(hold, trace.frequency)
    release_speeds = _phase_speeds(release, trace.frequency)
    steady_rows = hold_speeds[-25:]
    if len(steady_rows) < 24:
        raise AttemptError("steady window undersampled")
    steady_speed = statistics.median(speed for _, speed in steady_rows)
    if steady_speed <= 0:
        raise AttemptError("response steady speed is not positive")
    baseline_values = [speed for _, speed in baseline_speeds]
    b95 = _percentile(baseline_values, 0.95)
    endpoint = _distance(baseline[0].position, baseline[-1].position)
    if b95 > 0.05 * steady_speed or endpoint > 0.05 * steady_speed * 0.500:
        raise AttemptError("baseline drift exceeded the predeclared bound")
    hold_displacement = _distance(hold[0].position, hold[-1].position)
    if hold_displacement <= 20 * endpoint:
        raise AttemptError("response displacement did not dominate baseline drift")
    threshold = max(5 * b95, 0.10 * steady_speed)
    response_latency = _first_three(hold_speeds, lambda speed: speed >= threshold, trace.down_bracket, trace.frequency)
    try:
        release_latency = _first_three(release_speeds, lambda speed: speed < threshold, trace.up_bracket, trace.frequency)
    except AttemptError as exc:
        raise AttemptError("release response did not settle within 750 ms") from exc
    slope = _slope(steady_rows, trace.frequency)
    if abs(slope) > 0.10 * steady_speed:
        raise AttemptError("steady slope exceeded the predeclared bound")
    baseline_velocity = statistics.median(math.sqrt(sum(value * value for value in row.velocity)) for row in baseline)
    hold_velocity = statistics.median(math.sqrt(sum(value * value for value in row.velocity)) for row in hold)
    ratio = hold_velocity / max(baseline_velocity, 1e-9)
    if ratio <= 5.0:
        raise AttemptError("velocity hold-to-baseline ratio did not exceed five")
    for phase_rows in (hold_speeds, release_speeds):
        for row, position_speed in phase_rows:
            velocity_speed = math.sqrt(sum(value * value for value in row.velocity))
            tolerance = max(0.05 * steady_speed, 0.10 * position_speed)
            if abs(velocity_speed - position_speed) > tolerance:
                raise AttemptError("velocity does not corroborate position-derived response")
    steady_velocity = statistics.median(
        math.sqrt(sum(value * value for value in row.velocity)) for row, _ in steady_rows
    )
    if abs(steady_velocity - steady_speed) > 0.10 * steady_speed:
        raise AttemptError("velocity does not corroborate position-derived steady speed")

    down_tick = trace.down_bracket[1]
    nodes: dict[str, float] = {}
    for milliseconds in NODE_TIMES_MS:
        center = down_tick + round(trace.frequency * milliseconds / 1000)
        radius = round(trace.frequency * 0.020)
        values = [speed for row, speed in hold_speeds if abs(row.tick - center) <= radius]
        if not values:
            raise AttemptError(f"normalized response node {milliseconds}ms is empty")
        nodes[f"{milliseconds}ms"] = statistics.median(values) / steady_speed

    return AttemptMetrics(
        attempt=trace.attempt,
        accepted=True,
        receipt_sha256=trace.receipt_sha256,
        run_digest=trace.run_digest,
        sample_counts={phase: len(rows) for phase, rows in trace.samples.items()},
        steady_speed=steady_speed,
        baseline_b95_speed=b95,
        baseline_endpoint_displacement=endpoint,
        response_threshold=threshold,
        response_latency=response_latency,
        release_latency=release_latency,
        steady_slope=slope,
        normalized_response=nodes,
        velocity_hold_to_baseline_ratio=ratio,
        receipt_revalidated=True,
        foreground_maintained=True,
        key_up_confirmed=True,
        cleanup_confirmed=True,
    )


def _range(lower: float | int, upper: float | int) -> dict[str, float | int]:
    return {"lower": lower, "upper": upper}


def _attempt_projection(value: AttemptMetrics) -> dict[str, object]:
    return {
        "attempt": value.attempt,
        "receiptSha256": value.receipt_sha256,
        "runDigest": value.run_digest,
        "sampleCounts": value.sample_counts,
        "metrics": {
            "steadySpeed": value.steady_speed,
            "baselineB95Speed": value.baseline_b95_speed,
            "baselineEndpointDisplacement": value.baseline_endpoint_displacement,
            "responseThreshold": value.response_threshold,
            "responseLatencyMs": _range(value.response_latency.lower_ms, value.response_latency.upper_ms),
            "releaseLatencyMs": _range(value.release_latency.lower_ms, value.release_latency.upper_ms),
            "steadySlope": value.steady_slope,
            "normalizedResponse": value.normalized_response,
            "velocityHoldToBaselineRatio": value.velocity_hold_to_baseline_ratio,
        },
        "integrity": {
            "receiptRevalidated": value.receipt_revalidated,
            "foregroundMaintained": value.foreground_maintained,
            "keyUpConfirmed": value.key_up_confirmed,
            "cleanupConfirmed": value.cleanup_confirmed,
        },
    }


def _is_finite_number(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _validate_pair_candidate(value: AttemptMetrics) -> None:
    numeric_fields = (
        value.steady_speed,
        value.baseline_b95_speed,
        value.baseline_endpoint_displacement,
        value.response_threshold,
        value.steady_slope,
        value.velocity_hold_to_baseline_ratio,
    )
    if not all(_is_finite_number(item) for item in numeric_fields):
        raise AttemptError("attempt metric values must be finite numbers")
    if value.steady_speed <= 0:
        raise AttemptError("attempt steady speed must be finite and positive")
    if not isinstance(value.normalized_response, dict):
        raise AttemptError("attempt normalized response nodes must be an object")
    if set(value.normalized_response) != public_schema.NODE_KEYS:
        raise AttemptError("attempt normalized response nodes must match the exact node set")
    if not all(_is_finite_number(item) for item in value.normalized_response.values()):
        raise AttemptError("attempt normalized response nodes must be finite")
    for label, interval in (
        ("response", value.response_latency), ("release", value.release_latency)
    ):
        if not isinstance(interval, LatencyInterval):
            raise AttemptError(f"attempt {label} latency must be a bounded interval")
        lower, upper = interval.lower_ms, interval.upper_ms
        if (
            isinstance(lower, bool)
            or isinstance(upper, bool)
            or not isinstance(lower, int)
            or not isinstance(upper, int)
            or lower < 0
            or lower > upper
            or upper > 750
            or lower % CADENCE_MS
            or upper % CADENCE_MS
        ):
            raise AttemptError(f"attempt {label} latency violates cadence or duration bounds")


def materialize_pair(attempts: Sequence[AttemptMetrics]) -> dict[str, object]:
    if len(attempts) > 2:
        raise AttemptError("a third attempt is forbidden")
    if len(attempts) != 2 or any(not row.accepted for row in attempts):
        raise AttemptError("two accepted attempts are required")
    first, second = attempts
    if (first.attempt, second.attempt) != (1, 2):
        raise AttemptError("attempt order must be 1 then 2")
    if first.receipt_sha256 == second.receipt_sha256 or first.run_digest == second.run_digest:
        raise AttemptError("attempt identities are not fresh")
    for row in attempts:
        _validate_pair_candidate(row)
    relative_speed = abs(first.steady_speed - second.steady_speed) / min(first.steady_speed, second.steady_speed)
    response_union = max(first.response_latency.upper_ms, second.response_latency.upper_ms) - min(first.response_latency.lower_ms, second.response_latency.lower_ms)
    release_union = max(first.release_latency.upper_ms, second.release_latency.upper_ms) - min(first.release_latency.lower_ms, second.release_latency.lower_ms)
    node_delta = max(abs(first.normalized_response[key] - second.normalized_response[key]) for key in first.normalized_response)
    if relative_speed > 0.10 or response_union > 30 or release_union > 50 or node_delta > 0.10:
        raise AttemptError("two-run pair is not stable enough for an envelope")

    nodes = {
        key: _range(
            max(0.0, min(first.normalized_response[key], second.normalized_response[key]) - 0.05),
            max(first.normalized_response[key], second.normalized_response[key]) + 0.05,
        )
        for key in first.normalized_response
    }
    projection: dict[str, object] = {
        "schemaVersion": public_schema.PUBLIC_SCHEMA,
        "status": public_schema.PUBLIC_STATUS,
        "claim": public_schema.PUBLIC_CLAIM,
        "sampling": {
            "clock": "query-performance-counter",
            "cadenceMs": 10,
            "baselineMs": 500,
            "holdMs": 750,
            "releaseMs": 750,
            "timingPrecisionMs": 10,
        },
        "attempts": [_attempt_projection(first), _attempt_projection(second)],
        "envelope": {
            "steadySpeed": _range(
                round(0.95 * min(first.steady_speed, second.steady_speed), 12),
                round(1.05 * max(first.steady_speed, second.steady_speed), 12),
            ),
            "responseLatencyMs": _range(min(first.response_latency.lower_ms, second.response_latency.lower_ms), max(first.response_latency.upper_ms, second.response_latency.upper_ms)),
            "releaseLatencyMs": _range(min(first.release_latency.lower_ms, second.release_latency.lower_ms), max(first.release_latency.upper_ms, second.release_latency.upper_ms)),
            "normalizedResponse": nodes,
            "steadySlope": _range(min(first.steady_slope, second.steady_slope) - 0.02, max(first.steady_slope, second.steady_slope) + 0.02),
        },
        "nonclaims": list(public_schema.PUBLIC_NONCLAIMS),
    }
    public_schema.validate_public_projection(projection)
    return projection


def synthetic_attempt_trace(
    *,
    attempt: int,
    baseline_drift: bool = False,
    missing_control: bool = False,
    missing_response: bool = False,
    unstable_steady: bool = False,
    missing_release: bool = False,
    weak_velocity: bool = False,
    contradictory_velocity: bool = False,
) -> AttemptTrace:
    ticks = synthetic_schedule_ticks()
    position = 0.0
    samples: dict[str, list[RawSample]] = {phase: [] for phase in PHASE_TARGETS}
    for phase in ("baseline", "hold", "release"):
        for slot, tick in enumerate(ticks[phase]):
            if phase == "baseline":
                speed = 10.0 if baseline_drift else 0.0
                control = NEUTRAL_CONTROL_RAW
            elif phase == "hold":
                if missing_response:
                    speed = 0.0
                elif slot < 2:
                    speed = 0.0
                elif slot < 50:
                    speed = min(100.0, (slot - 1) * (100.0 / 48.0))
                else:
                    speed = 100.0 + ((slot - 50) * 2.0 if unstable_steady else 0.0)
                control = NEUTRAL_CONTROL_RAW if missing_control else FORWARD_CONTROL_RAW
            else:
                speed = 100.0 if missing_release else max(0.0, 100.0 - slot * 20.0)
                control = NEUTRAL_CONTROL_RAW
            position += speed * (CADENCE_MS / 1000.0)
            velocity_value = 0.0 if weak_velocity else speed * (2.0 if contradictory_velocity else 1.0)
            samples[phase].append(
                RawSample(
                    tick=tick,
                    phase=phase,
                    slot=slot,
                    position=(position, 0.0, 0.0),
                    velocity=(velocity_value, 0.0, 0.0),
                    state_raw=WALKER_STATE_RAW,
                    control_raw=control,
                )
            )
    down = (ticks["hold"][0] - 1000, ticks["hold"][0])
    up = (ticks["release"][0] - 1000, ticks["release"][0])
    return AttemptTrace(
        attempt=attempt,
        receipt_sha256=f"{attempt}" * 64,
        run_digest=f"{attempt + 2}" * 64,
        frequency=FREQUENCY_FIXTURE,
        samples=samples,
        down_bracket=down,
        up_bracket=up,
    )
