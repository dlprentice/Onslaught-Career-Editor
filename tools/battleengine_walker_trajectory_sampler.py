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
# Source/Steam-static hypothesis for actor integration (CLOCK_TICK / GAME_FR).
# Polling stays at CADENCE_MS; this window is only for position-derived speed and
# per-update velocity corroboration. It is not a retail tick proof.
PHYSICS_TICK_MS = 50
PHYSICS_TICK_SECONDS = PHYSICS_TICK_MS / 1000.0
POSITION_EDGE_EPSILON = 1e-6
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


def cadence_step_qpc(frequency: int) -> int:
    """Integer QPC counts per CADENCE_MS. Matches the live collector's step."""
    if frequency <= 0:
        raise AttemptError("QPC frequency must be positive")
    return max(1, round(frequency * CADENCE_MS / 1000))


def schedule_jitter_tolerance_qpc(frequency: int) -> int:
    """Tolerance for absolute-grid checks on synthetic / non-full traces."""
    step = cadence_step_qpc(frequency)
    twelve_ms = max(1, round(frequency * 0.012))
    return max(step // 2, twelve_ms)


def schedule_max_gap_qpc(frequency: int) -> int:
    """Max allowed inter-sample gap on the live declared-slot path (~250 ms).

    Foreground re-attach and receipt revalidation can exceed 50 ms between
    samples without invalidating the scalar motion envelope.
    """
    return max(cadence_step_qpc(frequency) * 25, round(frequency * 0.250))


def synthetic_schedule_ticks(*, frequency: int = FREQUENCY_FIXTURE) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    step = cadence_step_qpc(frequency)
    global_slot = 0
    for phase in ("baseline", "hold", "release"):
        count = PHASE_TARGETS[phase]
        result[phase] = [global_slot * step + index * step for index in range(count)]
        global_slot += count
    return result


def validate_schedule(
    ticks: Mapping[str, Sequence[int]],
    *,
    frequency: int,
    declared_slots: Mapping[str, Sequence[int]] | None = None,
) -> None:
    """Validate sampling timestamps for analysis.

    Live collector path: full-length phases with sequential declared slots 0..N-1
    only require monotonic ticks and bounded inter-sample gaps. Absolute alignment
    to a 10 ms grid is not required because coherent ReadProcessMemory can cost
    more than one cadence and cascade past any tight absolute tolerance.

    Synthetic / partial traces without declared full slots still use the integer
    cadence grid with a 12 ms absolute tolerance.
    """
    if frequency <= 0:
        raise AttemptError("QPC frequency must be positive")
    if set(ticks) != set(PHASE_TARGETS):
        raise AttemptError("schedule phase set mismatch")
    baseline_rows = list(ticks["baseline"])
    if not baseline_rows:
        raise AttemptError("baseline phase undersampled")
    origin = baseline_rows[0]
    step = cadence_step_qpc(frequency)
    tolerance = schedule_jitter_tolerance_qpc(frequency)
    max_gap = schedule_max_gap_qpc(frequency)
    phase_offsets = {
        "baseline": 0,
        "hold": PHASE_TARGETS["baseline"],
        "release": PHASE_TARGETS["baseline"] + PHASE_TARGETS["hold"],
    }
    previous_tick: int | None = None
    for phase in ("baseline", "hold", "release"):
        rows = list(ticks[phase])
        if len(rows) < PHASE_MINIMUMS[phase]:
            raise AttemptError(f"{phase} phase undersampled")
        if len(rows) > PHASE_TARGETS[phase]:
            raise AttemptError(f"{phase} phase sample count exceeds its window")
        if declared_slots is not None:
            slots = list(declared_slots[phase])
            if len(slots) != len(rows):
                raise AttemptError(f"{phase} declared slot count mismatch")
        elif len(rows) == PHASE_TARGETS[phase]:
            slots = list(range(len(rows)))
        else:
            phase_start = origin + phase_offsets[phase] * step
            slots = [int(round((tick - phase_start) / step)) for tick in rows]

        use_live_declared_path = (
            len(rows) == PHASE_TARGETS[phase]
            and slots == list(range(len(rows)))
        )
        # Phase-local gap checks only. Live external Q handshakes insert multi-
        # second gaps between baseline/hold/release without invalidating samples.
        previous_slot: int | None = None
        previous_phase_tick: int | None = None
        for tick, slot in zip(rows, slots):
            if slot < 0 or slot >= PHASE_TARGETS[phase]:
                raise AttemptError(f"{phase} sample slot falls outside its declared window")
            if previous_tick is not None and tick <= previous_tick:
                raise AttemptError("schedule timestamps must be monotonic")
            if previous_slot is not None and slot <= previous_slot:
                raise AttemptError("schedule jitter produced a duplicate or reversed slot")
            if use_live_declared_path:
                if previous_phase_tick is not None and (tick - previous_phase_tick) > max_gap:
                    raise AttemptError(
                        f"schedule has consecutive misses or a gap over {int(max_gap * 1000 / frequency)} ms"
                    )
            else:
                expected = origin + (phase_offsets[phase] + slot) * step
                if abs(tick - expected) > tolerance:
                    raise AttemptError("schedule jitter exceeded 12 ms")
                if previous_slot is not None and slot - previous_slot > 2:
                    raise AttemptError("schedule has consecutive misses or a gap over 20 ms")
            previous_slot = slot
            previous_tick = tick
            previous_phase_tick = tick
        if slots[0] != 0:
            raise AttemptError(f"{phase} phase boundary start is missing")
        if slots[-1] != PHASE_TARGETS[phase] - 1 and len(rows) == PHASE_TARGETS[phase]:
            raise AttemptError(f"{phase} phase boundary end is missing")
        if len(rows) < PHASE_TARGETS[phase] and slots[-1] < PHASE_MINIMUMS[phase] - 1:
            raise AttemptError(f"{phase} phase boundary end is missing")


def _distance(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _vector_magnitude(values: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in values))


def _percentile(values: Sequence[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, math.ceil(percentile * len(ordered)) - 1))
    return ordered[index]


def _phase_speeds(
    samples: Sequence[RawSample],
    frequency: int,
    *,
    window_ms: int = PHYSICS_TICK_MS,
) -> list[tuple[RawSample, float]]:
    """Wall-clock speed from position change over a fixed poll lag.

    Adjacent 10 ms samples of per-update integrated motion are mostly zero with
    occasional spikes. A lag matching the source physics tick recovers
    units/second without treating the poll rate as the simulation rate.
    """

    if window_ms <= 0:
        raise AttemptError("speed window must be positive")
    lag = max(1, window_ms // CADENCE_MS)
    result: list[tuple[RawSample, float]] = []
    for index in range(lag, len(samples)):
        previous = samples[index - lag]
        current = samples[index]
        elapsed = (current.tick - previous.tick) / frequency
        if elapsed <= 0:
            raise AttemptError("sample time must be monotonic")
        result.append((current, _distance(current.position, previous.position) / elapsed))
    return result


def _position_update_edges(
    samples: Sequence[RawSample],
    frequency: int,
) -> list[tuple[RawSample, float, float]]:
    """Return (sample, per-update displacement, wall elapsed) at position edges."""

    edges: list[tuple[RawSample, float, float]] = []
    for previous, current in zip(samples, samples[1:]):
        elapsed = (current.tick - previous.tick) / frequency
        if elapsed <= 0:
            raise AttemptError("sample time must be monotonic")
        displacement = _distance(current.position, previous.position)
        if displacement <= POSITION_EDGE_EPSILON:
            continue
        edges.append((current, displacement, elapsed))
    return edges


def _median_inter_edge_seconds(
    edges: Sequence[tuple[RawSample, float, float]],
    frequency: int,
) -> float:
    """Infer update period from observed position edges; fall back to hypothesis."""

    if len(edges) < 2:
        return PHYSICS_TICK_SECONDS
    periods = [
        (current.tick - previous.tick) / frequency
        for (previous, _d0, _e0), (current, _d1, _e1) in zip(edges, edges[1:])
    ]
    period = statistics.median(periods)
    if period <= 0:
        raise AttemptError("update edge period must be positive")
    # Keep the hypothesis only as a sanity band; do not require exact 50 ms.
    if period < 0.5 * PHYSICS_TICK_SECONDS or period > 2.0 * PHYSICS_TICK_SECONDS:
        raise AttemptError("inferred update period is outside the accepted hypothesis band")
    return period


def _corroborate_velocity_with_updates(
    samples: Sequence[RawSample],
    frequency: int,
    *,
    steady_speed: float,
    update_period_seconds: float,
) -> None:
    """Treat actor velocity as displacement per simulation update."""

    edges = _position_update_edges(samples, frequency)
    for row, displacement, _elapsed in edges:
        velocity_step = _vector_magnitude(row.velocity)
        tolerance = max(
            0.05 * max(steady_speed * update_period_seconds, 1e-6),
            0.10 * displacement,
        )
        if abs(velocity_step - displacement) > tolerance:
            raise AttemptError("velocity does not corroborate position-derived response")


def _corroborate_velocity_with_windowed_speeds(
    phase_speeds: Sequence[tuple[RawSample, float]],
    *,
    steady_speed: float,
    update_period_seconds: float,
) -> None:
    """Corroborate velocity against windowed wall speed without false edge transitions.

    Compare only when both signals are active. Separately, a fully settled tail
    must not keep advertising hold-scale per-update velocity.
    """

    if update_period_seconds <= 0:
        raise AttemptError("update period must be positive")
    active = 0.10 * steady_speed
    for row, position_speed in phase_speeds:
        velocity_as_speed = _vector_magnitude(row.velocity) / update_period_seconds
        if position_speed >= active and velocity_as_speed >= active:
            tolerance = max(0.05 * steady_speed, 0.15 * position_speed)
            if abs(velocity_as_speed - position_speed) > tolerance:
                raise AttemptError("velocity does not corroborate position-derived response")
    if len(phase_speeds) < 9:
        return
    tail = phase_speeds[-(len(phase_speeds) // 3) :]
    if not all(speed < active for _, speed in tail):
        return
    for row, _speed in tail:
        if _vector_magnitude(row.velocity) / update_period_seconds > 0.50 * steady_speed:
            raise AttemptError("velocity does not corroborate position-derived response")


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
    max_gap = schedule_max_gap_qpc(trace.frequency)
    for phase in ("baseline", "hold", "release"):
        previous_tick: int | None = None
        previous_slot: int | None = None
        for row in trace.samples[phase]:
            if row.phase != phase:
                raise AttemptError("sample phase label does not match its phase")
            if row.slot < 0 or row.slot >= PHASE_TARGETS[phase]:
                raise AttemptError(f"{phase} sample slot falls outside its declared window")
            if previous_slot is not None and row.slot <= previous_slot:
                raise AttemptError("sample slot does not match its monotonic timestamp")
            if previous_tick is not None and row.tick <= previous_tick:
                raise AttemptError("sample slot does not match its monotonic timestamp")
            if previous_tick is not None and (row.tick - previous_tick) > max_gap:
                raise AttemptError("sample slot does not match its monotonic timestamp")
            if row.state_raw != WALKER_STATE_RAW:
                raise AttemptError("sample walker state gate mismatch")
            if not all(math.isfinite(value) for value in (*row.position, *row.velocity)):
                raise AttemptError("sample position and velocity must be finite")
            previous_tick = row.tick
            previous_slot = row.slot


def _validate_input_bracket(
    bracket: tuple[int, int], phase_start: int, frequency: int, label: str
) -> None:
    before, after = bracket
    # Live path revalidates receipt/identity around Q edges; that plus SendInput
    # can exceed one 10 ms cadence without invalidating the phase association.
    bind = schedule_max_gap_qpc(frequency)
    if before > after:
        raise AttemptError(f"{label} bracket is reversed")
    if after > phase_start or phase_start - before > bind:
        raise AttemptError(f"{label} bracket is not bound to the phase boundary")
    if after - before > bind:
        raise AttemptError(f"{label} bracket exceeds one sampling cadence")


def analyze_attempt(trace: AttemptTrace) -> AttemptMetrics:
    _require_integrity(trace.integrity)
    validate_schedule(
        {phase: [row.tick for row in rows] for phase, rows in trace.samples.items()},
        frequency=trace.frequency,
        declared_slots={
            phase: [row.slot for row in rows] for phase, rows in trace.samples.items()
        },
    )
    baseline = trace.samples["baseline"]
    hold = trace.samples["hold"]
    release = trace.samples["release"]
    _validate_trace_rows(trace)
    _validate_input_bracket(trace.down_bracket, hold[0].tick, trace.frequency, "key-down")
    _validate_input_bracket(trace.up_bracket, release[0].tick, trace.frequency, "key-up")
    if any(row.control_raw != NEUTRAL_CONTROL_RAW for row in baseline):
        raise AttemptError("baseline control field was not neutral")
    # Live Q response is not instantaneous: early hold samples may still be
    # neutral, and early release samples may still be forward. Require a
    # sustained forward window that matches the speed steady-state window.
    forward_hold = [row for row in hold if row.control_raw == FORWARD_CONTROL_RAW]
    if len(forward_hold) < 24:
        seen = sorted({int(row.control_raw) for row in hold})
        raise AttemptError(
            "control field did not prove Q walker-forward state; "
            f"forward_count={len(forward_hold)} hold_controls={seen}"
        )
    steady_controls = hold[-25:] if len(hold) >= 25 else hold
    if sum(1 for row in steady_controls if row.control_raw == FORWARD_CONTROL_RAW) < 20:
        seen = sorted({int(row.control_raw) for row in steady_controls})
        raise AttemptError(
            "control field did not prove Q walker-forward state; "
            f"steady_forward_controls={seen}"
        )
    release_tail = release[-25:] if len(release) >= 25 else release
    if sum(1 for row in release_tail if row.control_raw == NEUTRAL_CONTROL_RAW) < 20:
        seen = sorted({int(row.control_raw) for row in release_tail})
        raise AttemptError(
            f"release control field did not return to neutral; release_tail_controls={seen}"
        )

    baseline_speeds = _phase_speeds(baseline, trace.frequency)
    hold_speeds = _phase_speeds(hold, trace.frequency)
    release_speeds = _phase_speeds(release, trace.frequency)
    if len(hold_speeds) < 24:
        raise AttemptError("steady window undersampled")
    steady_rows = hold_speeds[-25:] if len(hold_speeds) >= 25 else hold_speeds
    if len(steady_rows) < 24:
        raise AttemptError("steady window undersampled")
    steady_speed = statistics.median(speed for _, speed in steady_rows)
    if steady_speed <= 0:
        raise AttemptError("response steady speed is not positive")
    baseline_values = [speed for _, speed in baseline_speeds]
    b95 = _percentile(baseline_values, 0.95) if baseline_values else 0.0
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
    baseline_velocity = statistics.median(_vector_magnitude(row.velocity) for row in baseline)
    hold_velocity = statistics.median(_vector_magnitude(row.velocity) for row in hold)
    ratio = hold_velocity / max(baseline_velocity, 1e-9)
    if ratio <= 5.0:
        raise AttemptError("velocity hold-to-baseline ratio did not exceed five")
    hold_edges = _position_update_edges(hold, trace.frequency)
    if not hold_edges:
        raise AttemptError("velocity does not corroborate position-derived response")
    update_period = _median_inter_edge_seconds(hold_edges, trace.frequency)
    _corroborate_velocity_with_updates(
        hold, trace.frequency, steady_speed=steady_speed, update_period_seconds=update_period
    )
    _corroborate_velocity_with_updates(
        release, trace.frequency, steady_speed=steady_speed, update_period_seconds=update_period
    )
    _corroborate_velocity_with_windowed_speeds(
        hold_speeds, steady_speed=steady_speed, update_period_seconds=update_period
    )
    _corroborate_velocity_with_windowed_speeds(
        release_speeds, steady_speed=steady_speed, update_period_seconds=update_period
    )
    # Quiet release tails may have no final edges after settling; require that any
    # observed edges still match, and that the steady hold edges match wall speed.
    steady_velocity_step = statistics.median(
        _vector_magnitude(row.velocity) for row, _displacement, _elapsed in hold_edges[-5:]
    )
    steady_velocity = steady_velocity_step / update_period
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
        "metricUnits": dict(public_schema.PUBLIC_METRIC_UNITS),
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
    """Build a source-shaped ~20 Hz integrated trajectory polled at CADENCE_MS.

    Actor velocity is displacement per physics update (`position += velocity`),
    not units/second. Wall-clock speed is recovered by the tick-aware analyzer.
    """

    ticks = synthetic_schedule_ticks()
    position = 0.0
    samples: dict[str, list[RawSample]] = {phase: [] for phase in PHASE_TARGETS}
    samples_per_tick = max(1, PHYSICS_TICK_MS // CADENCE_MS)
    global_slot = 0
    velocity_step = 0.0
    for phase in ("baseline", "hold", "release"):
        for slot, tick in enumerate(ticks[phase]):
            if phase == "baseline":
                wall_speed = 10.0 if baseline_drift else 0.0
                control = NEUTRAL_CONTROL_RAW
            elif phase == "hold":
                if missing_response:
                    wall_speed = 0.0
                elif slot < 2:
                    wall_speed = 0.0
                elif slot < 50:
                    wall_speed = min(100.0, (slot - 1) * (100.0 / 48.0))
                else:
                    wall_speed = 100.0 + ((slot - 50) * 2.0 if unstable_steady else 0.0)
                control = NEUTRAL_CONTROL_RAW if missing_control else FORWARD_CONTROL_RAW
            else:
                # Decay across multiple physics ticks so release edges exist and
                # settled-velocity forgeries remain detectable.
                wall_speed = 100.0 if missing_release else max(0.0, 100.0 - slot * (100.0 / 48.0))
                control = NEUTRAL_CONTROL_RAW
            # Integrate only on physics-tick boundaries (source-shaped staircase).
            if global_slot % samples_per_tick == 0:
                velocity_step = wall_speed * PHYSICS_TICK_SECONDS
                position += velocity_step
            stored_velocity = 0.0 if weak_velocity else velocity_step * (2.0 if contradictory_velocity else 1.0)
            samples[phase].append(
                RawSample(
                    tick=tick,
                    phase=phase,
                    slot=slot,
                    position=(position, 0.0, 0.0),
                    velocity=(stored_velocity, 0.0, 0.0),
                    state_raw=WALKER_STATE_RAW,
                    control_raw=control,
                )
            )
            global_slot += 1
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
        integrity=AttemptIntegrity(
            receipt_revalidated=True,
            foreground_maintained=True,
            key_down_confirmed=True,
            key_up_confirmed=True,
            interference_detected=False,
            cleanup_confirmed=True,
        ),
    )
