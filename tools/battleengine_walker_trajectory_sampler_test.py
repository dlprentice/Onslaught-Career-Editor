#!/usr/bin/env python3
"""Synthetic tests for the scalar walker-forward trajectory sampler."""

from __future__ import annotations

import copy
import math
from pathlib import Path
import struct
import unittest

import battleengine_walker_trajectory_sampler as sampler
import battleengine_walker_trajectory_schema as schema


class FakeMemory:
    def __init__(self) -> None:
        self.values: dict[tuple[int, int], bytes] = {}
        self.short: tuple[int, int] | None = None
        self.read_overrides: list[dict[tuple[int, int], bytes]] = []
        self.read_count = 0
        self.key_sequences: dict[tuple[int, int], list[bytes]] = {}
        self.key_read_counts: dict[tuple[int, int], int] = {}

    def put_u32(self, address: int, value: int) -> None:
        self.values[(address, 4)] = struct.pack("<I", value)

    def put_u8(self, address: int, value: int) -> None:
        self.values[(address, 1)] = struct.pack("<B", value)

    def put_f32x3(self, address: int, values: tuple[float, float, float]) -> None:
        self.values[(address, 12)] = struct.pack("<3f", *values)

    def put_f32(self, address: int, value: float) -> None:
        self.values[(address, 4)] = struct.pack("<f", value)

    def read(self, address: int, size: int) -> bytes:
        self.read_count += 1
        key = (address, size)
        if key in self.key_sequences:
            index = self.key_read_counts.get(key, 0)
            self.key_read_counts[key] = index + 1
            values = self.key_sequences[key]
            return values[min(index, len(values) - 1)]
        if self.short == key:
            return self.values[key][:-1]
        if self.read_overrides:
            override = self.read_overrides.pop(0)
            if key in override:
                return override[key]
        return self.values[key]


def coherent_memory(*, module_base: int = 0x10000000) -> tuple[FakeMemory, int]:
    memory = FakeMemory()
    p0 = 0x20000000
    battle_engine = 0x30000000
    walker = 0x40000000
    memory.put_u32(module_base + sampler.P0_GLOBAL_RVA, p0)
    memory.put_u32(p0 + sampler.PLAYER_BATTLE_ENGINE_OFFSET, battle_engine)
    memory.put_u32(battle_engine + sampler.BATTLE_ENGINE_WALKER_OFFSET, walker)
    memory.put_u32(walker + sampler.WALKER_MAIN_PART_OFFSET, battle_engine)
    memory.put_u32(battle_engine + sampler.BATTLE_ENGINE_STATE_OFFSET, sampler.WALKER_STATE_RAW)
    memory.put_f32x3(battle_engine + sampler.BATTLE_ENGINE_POSITION_OFFSET, (1.0, 2.0, 3.0))
    memory.put_f32x3(battle_engine + sampler.BATTLE_ENGINE_VELOCITY_OFFSET, (0.0, 0.0, 0.0))
    memory.put_f32(walker + sampler.WALKER_CONTROL_OFFSET, 0.0)
    memory.put_u32(module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_LEVEL_OFFSET, 850)
    memory.put_u32(module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_PLAYER_COUNT_OFFSET, 2)
    memory.put_u8(module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_HORIZONTAL_SPLIT_OFFSET, 1)
    memory.put_u32(module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_P1_OFFSET, 0x21000000)
    return memory, module_base


def latency(lower: int = 20, upper: int = 30) -> sampler.LatencyInterval:
    return sampler.LatencyInterval(lower_ms=lower, upper_ms=upper)


def metrics(
    *,
    attempt: int,
    steady_speed: float = 100.0,
    response: sampler.LatencyInterval | None = None,
    release: sampler.LatencyInterval | None = None,
    baseline_b95: float = 1.0,
    baseline_endpoint: float = 1.0,
    slope: float = 2.0,
    normalized: tuple[float, float, float, float] = (0.25, 0.50, 0.80, 0.98),
) -> sampler.AttemptMetrics:
    return sampler.AttemptMetrics(
        attempt=attempt,
        accepted=True,
        receipt_sha256=f"{attempt}" * 64,
        run_digest=f"{attempt + 2}" * 64,
        sample_counts={"baseline": 50, "hold": 75, "release": 75},
        steady_speed=steady_speed,
        baseline_b95_speed=baseline_b95,
        baseline_endpoint_displacement=baseline_endpoint,
        response_threshold=max(5 * baseline_b95, 0.10 * steady_speed),
        response_latency=response or latency(),
        release_latency=release or latency(30, 40),
        steady_slope=slope,
        normalized_response={
            "100ms": normalized[0],
            "200ms": normalized[1],
            "350ms": normalized[2],
            "500ms": normalized[3],
        },
        velocity_hold_to_baseline_ratio=8.0,
        receipt_revalidated=True,
        foreground_maintained=True,
        key_up_confirmed=True,
        cleanup_confirmed=True,
    )


class CoherentReadTests(unittest.TestCase):
    def test_cgame_readiness_layout_has_exact_tracked_bounded_provenance(self) -> None:
        self.assertEqual(
            (
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
            ),
            sampler.C_GAME_READINESS_PROVENANCE,
        )
        provenance_text = repr(sampler.C_GAME_READINESS_PROVENANCE)
        self.assertNotIn("complete CGame layout", provenance_text)
        self.assertNotIn("runtime multiplayer behavior", provenance_text)
        root = Path(__file__).resolve().parents[1]
        for claim, sources in sampler.C_GAME_READINESS_PROVENANCE:
            with self.subTest(claim=claim):
                for relative_path, exact_token in sources:
                    tracked_text = (root / relative_path).read_text(encoding="utf-8")
                    self.assertIn(exact_token, tracked_text)

    def test_cgame_readiness_layout_is_inline_and_p0_member_closes_identity(self) -> None:
        self.assertEqual(
            sampler.P0_GLOBAL_RVA,
            sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_P0_OFFSET,
        )

    def test_readiness_classifies_exact_null_hop_without_paths_or_addresses(self) -> None:
        for hop in ("p0", "p1", "battleEngine", "walker", "backpointer"):
            with self.subTest(hop=hop):
                memory, module_base = coherent_memory()
                p0 = struct.unpack("<I", memory.values[(module_base + sampler.P0_GLOBAL_RVA, 4)])[0]
                battle_engine = struct.unpack("<I", memory.values[(p0 + sampler.PLAYER_BATTLE_ENGINE_OFFSET, 4)])[0]
                walker = struct.unpack("<I", memory.values[(battle_engine + sampler.BATTLE_ENGINE_WALKER_OFFSET, 4)])[0]
                address = {
                    "p0": module_base + sampler.P0_GLOBAL_RVA,
                    "p1": module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_P1_OFFSET,
                    "battleEngine": p0 + sampler.PLAYER_BATTLE_ENGINE_OFFSET,
                    "walker": battle_engine + sampler.BATTLE_ENGINE_WALKER_OFFSET,
                    "backpointer": walker + sampler.WALKER_MAIN_PART_OFFSET,
                }[hop]
                memory.put_u32(address, 0)
                with self.assertRaises(sampler.RuntimeNotReady) as caught:
                    sampler.read_readiness_probe(memory, module_base)
                self.assertEqual(hop, caught.exception.hop)
                diagnostic = str(caught.exception)
                self.assertNotIn("0x", diagnostic)
                self.assertNotIn("\\", diagnostic)

    def test_readiness_accepts_only_locked_level_player_state_and_control(self) -> None:
        memory, module_base = coherent_memory()
        ready = sampler.read_readiness_probe(memory, module_base)
        self.assertEqual((850, 2, 1, sampler.WALKER_STATE_RAW, sampler.NEUTRAL_CONTROL_RAW), (
            ready.level, ready.player_count, ready.horizontal_split,
            ready.state_raw, ready.control_raw,
        ))
        for field, address, value in (
            ("level", module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_LEVEL_OFFSET, 849),
            ("playerCount", module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_PLAYER_COUNT_OFFSET, 1),
            ("horizontalSplit", module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_HORIZONTAL_SPLIT_OFFSET, 0),
            ("state", 0x30000000 + sampler.BATTLE_ENGINE_STATE_OFFSET, 3),
            ("control", 0x40000000 + sampler.WALKER_CONTROL_OFFSET, sampler.FORWARD_CONTROL_RAW),
        ):
            with self.subTest(field=field):
                candidate, candidate_base = coherent_memory(module_base=module_base)
                if field == "horizontalSplit":
                    candidate.put_u8(address, value)
                else:
                    candidate.put_u32(address, value)
                with self.assertRaises(sampler.RuntimeNotReady) as caught:
                    sampler.read_readiness_probe(candidate, candidate_base)
                self.assertEqual(field, caught.exception.field)

    def test_readiness_rejects_misaligned_equal_and_drifting_player_identities(self) -> None:
        for slot_offset in (sampler.C_GAME_P0_OFFSET, sampler.C_GAME_P1_OFFSET):
            with self.subTest(misaligned=slot_offset):
                memory, module_base = coherent_memory()
                address = module_base + sampler.C_GAME_OBJECT_RVA + slot_offset
                memory.put_u32(address, 0x21000002)
                with self.assertRaisesRegex(sampler.SampleError, "aligned") as caught:
                    sampler.read_readiness_probe(memory, module_base)
                self.assertNotIn("0x", str(caught.exception))

        memory, module_base = coherent_memory()
        memory.put_u32(
            module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_P1_OFFSET,
            0x20000000,
        )
        with self.assertRaisesRegex(sampler.SampleError, "distinct") as caught:
            sampler.read_readiness_probe(memory, module_base)
        self.assertNotIn("0x", str(caught.exception))

        for slot_offset, values in (
            (sampler.C_GAME_P0_OFFSET, [0x20000000] * 5 + [0x22000000]),
            (sampler.C_GAME_P1_OFFSET, [0x21000000, 0x22000000]),
        ):
            with self.subTest(drift=slot_offset):
                memory, module_base = coherent_memory()
                key = (module_base + sampler.C_GAME_OBJECT_RVA + slot_offset, 4)
                memory.key_sequences[key] = [struct.pack("<I", value) for value in values]
                with self.assertRaisesRegex(sampler.SampleError, "changed") as caught:
                    sampler.read_readiness_probe(memory, module_base)
                self.assertNotIn("0x", str(caught.exception))

        memory, module_base = coherent_memory()
        split_key = (
            module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_HORIZONTAL_SPLIT_OFFSET,
            1,
        )
        memory.key_sequences[split_key] = [struct.pack("<B", 1), struct.pack("<B", 0)]
        with self.assertRaisesRegex(sampler.SampleError, "changed") as caught:
            sampler.read_readiness_probe(memory, module_base)
        self.assertNotIn("0x", str(caught.exception))

    def test_established_runtime_chain_nulls_are_fatal_not_retryable(self) -> None:
        for hop in ("p0", "battleEngine", "walker", "backpointer"):
            with self.subTest(hop=hop):
                memory, module_base = coherent_memory()
                p0 = struct.unpack("<I", memory.values[(module_base + sampler.P0_GLOBAL_RVA, 4)])[0]
                battle_engine = struct.unpack(
                    "<I", memory.values[(p0 + sampler.PLAYER_BATTLE_ENGINE_OFFSET, 4)]
                )[0]
                walker = struct.unpack(
                    "<I", memory.values[(battle_engine + sampler.BATTLE_ENGINE_WALKER_OFFSET, 4)]
                )[0]
                address, established = {
                    "p0": (module_base + sampler.P0_GLOBAL_RVA, p0),
                    "battleEngine": (p0 + sampler.PLAYER_BATTLE_ENGINE_OFFSET, battle_engine),
                    "walker": (battle_engine + sampler.BATTLE_ENGINE_WALKER_OFFSET, walker),
                    "backpointer": (walker + sampler.WALKER_MAIN_PART_OFFSET, battle_engine),
                }[hop]
                memory.key_sequences[(address, 4)] = [
                    struct.pack("<I", established),
                    struct.pack("<I", established),
                    struct.pack("<I", 0),
                ]
                with self.assertRaises(sampler.SampleError) as caught:
                    sampler.read_coherent_sample(
                        memory, module_base, tick=0, phase="readiness", slot=0
                    )
                self.assertNotIsInstance(caught.exception, sampler.RuntimeNotReady)
                self.assertIn("null", str(caught.exception))

        memory, module_base = coherent_memory()
        p1_address = module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_P1_OFFSET
        memory.key_sequences[(p1_address, 4)] = [
            struct.pack("<I", 0x21000000),
            struct.pack("<I", 0),
        ]
        with self.assertRaises(sampler.SampleError) as caught:
            sampler.read_readiness_probe(memory, module_base)
        self.assertNotIsInstance(caught.exception, sampler.RuntimeNotReady)
        self.assertIn("null", str(caught.exception))

    def test_identity_drift_wins_over_stable_state_not_ready(self) -> None:
        for field in ("horizontalSplit", "p1"):
            with self.subTest(field=field):
                memory, module_base = coherent_memory()
                memory.put_u32(
                    0x30000000 + sampler.BATTLE_ENGINE_STATE_OFFSET,
                    sampler.WALKER_STATE_RAW + 1,
                )
                if field == "horizontalSplit":
                    address = (
                        module_base
                        + sampler.C_GAME_OBJECT_RVA
                        + sampler.C_GAME_HORIZONTAL_SPLIT_OFFSET
                    )
                    memory.key_sequences[(address, 1)] = [
                        struct.pack("<B", 1),
                        struct.pack("<B", 0),
                    ]
                else:
                    address = module_base + sampler.C_GAME_OBJECT_RVA + sampler.C_GAME_P1_OFFSET
                    memory.key_sequences[(address, 4)] = [
                        struct.pack("<I", 0x21000000),
                        struct.pack("<I", 0x22000000),
                    ]
                with self.assertRaisesRegex(sampler.SampleError, "changed") as caught:
                    sampler.read_readiness_probe(memory, module_base)
                self.assertNotIsInstance(caught.exception, sampler.RuntimeNotReady)

    def test_reads_exact_aligned_chain_and_scalar_payload(self) -> None:
        memory, module_base = coherent_memory()

        sample = sampler.read_coherent_sample(memory, module_base, tick=123, phase="baseline", slot=0)

        self.assertEqual((1.0, 2.0, 3.0), sample.position)
        self.assertEqual((0.0, 0.0, 0.0), sample.velocity)
        self.assertEqual(sampler.WALKER_STATE_RAW, sample.state_raw)
        self.assertEqual(sampler.NEUTRAL_CONTROL_RAW, sample.control_raw)
        self.assertNotIn("basis", sample.__dataclass_fields__)
        self.assertNotIn("grounded", sample.__dataclass_fields__)

    def test_rejects_short_misaligned_overflow_and_null_reads(self) -> None:
        memory, module_base = coherent_memory()
        p0 = struct.unpack("<I", memory.values[(module_base + sampler.P0_GLOBAL_RVA, 4)])[0]
        battle_engine = struct.unpack("<I", memory.values[(p0 + sampler.PLAYER_BATTLE_ENGINE_OFFSET, 4)])[0]
        memory.short = (battle_engine + sampler.BATTLE_ENGINE_POSITION_OFFSET, 12)
        with self.assertRaisesRegex(sampler.SampleError, "short read"):
            sampler.read_coherent_sample(memory, module_base, tick=1, phase="baseline", slot=0)

        with self.assertRaisesRegex(sampler.SampleError, "aligned"):
            sampler.read_coherent_sample(memory, module_base + 1, tick=1, phase="baseline", slot=0)

        memory, module_base = coherent_memory(module_base=0xFFFFF000)
        with self.assertRaisesRegex(sampler.SampleError, "overflow"):
            sampler.read_coherent_sample(memory, module_base, tick=1, phase="baseline", slot=0)

        memory, module_base = coherent_memory()
        memory.put_u32(module_base + sampler.P0_GLOBAL_RVA, 0)
        with self.assertRaisesRegex(sampler.SampleError, "null"):
            sampler.read_coherent_sample(memory, module_base, tick=1, phase="baseline", slot=0)

    def test_rejects_wrong_backpointer_state_and_nonfinite_vectors(self) -> None:
        memory, module_base = coherent_memory()
        p0 = struct.unpack("<I", memory.values[(module_base + sampler.P0_GLOBAL_RVA, 4)])[0]
        battle_engine = struct.unpack("<I", memory.values[(p0 + sampler.PLAYER_BATTLE_ENGINE_OFFSET, 4)])[0]
        walker = struct.unpack("<I", memory.values[(battle_engine + sampler.BATTLE_ENGINE_WALKER_OFFSET, 4)])[0]
        memory.put_u32(walker + sampler.WALKER_MAIN_PART_OFFSET, 0x50000000)
        with self.assertRaisesRegex(sampler.SampleError, "backpointer"):
            sampler.read_coherent_sample(memory, module_base, tick=1, phase="baseline", slot=0)

        memory, module_base = coherent_memory()
        p0 = struct.unpack("<I", memory.values[(module_base + sampler.P0_GLOBAL_RVA, 4)])[0]
        battle_engine = struct.unpack("<I", memory.values[(p0 + sampler.PLAYER_BATTLE_ENGINE_OFFSET, 4)])[0]
        memory.put_u32(battle_engine + sampler.BATTLE_ENGINE_STATE_OFFSET, 3)
        with self.assertRaisesRegex(sampler.SampleError, "walker state"):
            sampler.read_coherent_sample(memory, module_base, tick=1, phase="baseline", slot=0)

        memory, module_base = coherent_memory()
        p0 = struct.unpack("<I", memory.values[(module_base + sampler.P0_GLOBAL_RVA, 4)])[0]
        battle_engine = struct.unpack("<I", memory.values[(p0 + sampler.PLAYER_BATTLE_ENGINE_OFFSET, 4)])[0]
        memory.put_f32x3(battle_engine + sampler.BATTLE_ENGINE_POSITION_OFFSET, (math.nan, 0.0, 0.0))
        with self.assertRaisesRegex(sampler.SampleError, "finite"):
            sampler.read_coherent_sample(memory, module_base, tick=1, phase="baseline", slot=0)

    def test_rejects_torn_payload_after_three_pairs(self) -> None:
        memory, module_base = coherent_memory()
        p0 = struct.unpack("<I", memory.values[(module_base + sampler.P0_GLOBAL_RVA, 4)])[0]
        battle_engine = struct.unpack("<I", memory.values[(p0 + sampler.PLAYER_BATTLE_ENGINE_OFFSET, 4)])[0]
        position_key = (battle_engine + sampler.BATTLE_ENGINE_POSITION_OFFSET, 12)
        first = memory.values[position_key]
        second = struct.pack("<3f", 2.0, 2.0, 3.0)
        # Two 12-read acquisitions per pair; position is read index 5 in each.
        for _ in range(sampler.MAX_COHERENCE_PAIRS):
            pair = [{} for _ in range(24)]
            pair[5] = {position_key: first}
            pair[17] = {position_key: second}
            memory.read_overrides.extend(pair)
        with self.assertRaisesRegex(sampler.SampleError, "torn"):
            sampler.read_coherent_sample(memory, module_base, tick=1, phase="baseline", slot=0)


class ReceiptAndScheduleTests(unittest.TestCase):
    def test_receipt_guard_rejects_identity_module_window_and_path_drift(self) -> None:
        expected = sampler.ReceiptIdentity.synthetic()
        for field, value in (
            ("receipt_sha256", "0" * 64),
            ("process_id", expected.process_id + 1),
            ("started_at_utc", "2000-01-01T00:00:00Z"),
            ("executable_sha256", "0" * 64),
            ("module_path", "C:/other/BEA.exe"),
            ("module_base", expected.module_base + 0x1000),
            ("module_size", expected.module_size + 1),
            ("window_handle", expected.window_handle + 1),
            ("window_process_id", expected.process_id + 1),
            ("manifest_sha256", "0" * 64),
            ("launch_arguments", ("-level", "100")),
        ):
            with self.subTest(field=field):
                actual = sampler.replace_receipt(expected, **{field: value})
                with self.assertRaisesRegex(sampler.AttemptError, "receipt"):
                    sampler.require_receipt_match(expected, actual)

        escaped = sampler.replace_receipt(expected, artifact_path="C:/private/outside/raw.json")
        with self.assertRaisesRegex(sampler.AttemptError, "path"):
            sampler.require_receipt_match(expected, escaped)

        reparsed = sampler.replace_receipt(expected, path_is_reparse=True)
        with self.assertRaisesRegex(sampler.AttemptError, "reparse"):
            sampler.require_receipt_match(expected, reparsed)

        traversal = sampler.replace_receipt(
            expected,
            artifact_path="C:/synthetic/role/private/../../outside/raw.json",
        )
        with self.assertRaisesRegex(sampler.AttemptError, "path"):
            sampler.require_receipt_match(expected, traversal)

        different_in_root = sampler.replace_receipt(
            expected,
            artifact_path="C:/synthetic/role/private/other.json",
        )
        with self.assertRaisesRegex(sampler.AttemptError, "receipt"):
            sampler.require_receipt_match(expected, different_in_root)

    def test_schedule_rejects_jitter_gaps_nonmonotonic_and_undersampling(self) -> None:
        ticks = sampler.synthetic_schedule_ticks()
        sampler.validate_schedule(ticks, frequency=10_000_000)
        shifted_origin = {
            phase: [tick + 123_456_789 for tick in rows]
            for phase, rows in ticks.items()
        }
        sampler.validate_schedule(shifted_origin, frequency=10_000_000)
        odd_frequency = 3_579_545
        sampler.validate_schedule(
            sampler.synthetic_schedule_ticks(frequency=odd_frequency), frequency=odd_frequency
        )

        # Full-length sequential slots tolerate multi-cadence lateness (live RPM):
        # shift a suffix so ticks stay monotonic while one gap is ~25 ms.
        late_but_full = copy.deepcopy(ticks)
        for index in range(5, len(late_but_full["hold"])):
            late_but_full["hold"][index] += 250_000  # +25 ms from hold slot 5
        late_but_full["release"] = [tick + 250_000 for tick in late_but_full["release"]]
        sampler.validate_schedule(late_but_full, frequency=10_000_000)

        # Gap over 250 ms still fails on the live declared-slot path.
        huge_gap = copy.deepcopy(ticks)
        for index in range(5, len(huge_gap["hold"])):
            huge_gap["hold"][index] += 3_000_000  # +300 ms
        huge_gap["release"] = [tick + 3_000_000 for tick in huge_gap["release"]]
        with self.assertRaisesRegex(sampler.AttemptError, "gap|250"):
            sampler.validate_schedule(huge_gap, frequency=10_000_000)

        # Partial traces still use the absolute cadence grid / gap rules.
        partial = copy.deepcopy(ticks)
        partial["hold"] = partial["hold"][:72]
        partial["hold"][4] += 150_000
        with self.assertRaisesRegex(sampler.AttemptError, "jitter|gap|window|slot"):
            sampler.validate_schedule(partial, frequency=10_000_000)

        gap = copy.deepcopy(ticks)
        del gap["hold"][10:12]
        with self.assertRaisesRegex(
            sampler.AttemptError, "consecutive|gap|boundary|window|slot|jitter"
        ):
            sampler.validate_schedule(gap, frequency=10_000_000)

        short = copy.deepcopy(ticks)
        short["release"] = short["release"][:71]
        with self.assertRaisesRegex(sampler.AttemptError, "undersampled"):
            sampler.validate_schedule(short, frequency=10_000_000)

        backwards = copy.deepcopy(ticks)
        backwards["baseline"][10] = backwards["baseline"][9] - 1
        with self.assertRaisesRegex(sampler.AttemptError, "monotonic"):
            sampler.validate_schedule(backwards, frequency=10_000_000)

        shifted_phase = copy.deepcopy(ticks)
        shifted_phase["hold"] = [tick + 5_000_000 for tick in shifted_phase["hold"]]
        with self.assertRaisesRegex(
            sampler.AttemptError, "window|boundary|slot|jitter|gap|50|monotonic"
        ):
            sampler.validate_schedule(shifted_phase, frequency=10_000_000)

        overrun = copy.deepcopy(ticks)
        overrun["release"].append(overrun["release"][-1] + 100_000)
        with self.assertRaisesRegex(sampler.AttemptError, "window|count|slot"):
            sampler.validate_schedule(overrun, frequency=10_000_000)


class AttemptAnalysisTests(unittest.TestCase):
    def test_accepts_scalar_response_and_builds_sample_bounded_intervals(self) -> None:
        trace = sampler.synthetic_attempt_trace(attempt=1)

        result = sampler.analyze_attempt(trace)

        self.assertTrue(result.accepted)
        self.assertEqual({"baseline": 50, "hold": 75, "release": 75}, result.sample_counts)
        self.assertEqual(0, result.response_latency.upper_ms % 10)
        self.assertLessEqual(result.response_latency.lower_ms, result.response_latency.upper_ms)
        self.assertLessEqual(result.release_latency.lower_ms, result.release_latency.upper_ms)
        self.assertLessEqual(abs(result.steady_slope), 0.10 * result.steady_speed)
        self.assertGreater(result.steady_speed, 50.0)

    def test_accepts_source_shaped_20hz_staircase_despite_100hz_polling(self) -> None:
        """Regression: per-update velocity at ~20 Hz must not look like zero steady speed."""

        trace = sampler.synthetic_attempt_trace(attempt=1)
        hold = trace.samples["hold"]
        adjacent_zeros = 0
        for previous, current in zip(hold, hold[1:]):
            elapsed = (current.tick - previous.tick) / trace.frequency
            adjacent = sampler._distance(current.position, previous.position) / elapsed
            if adjacent <= 1e-9:
                adjacent_zeros += 1
        self.assertGreaterEqual(adjacent_zeros, 40)

        result = sampler.analyze_attempt(trace)
        self.assertTrue(result.accepted)
        self.assertAlmostEqual(100.0, result.steady_speed, delta=15.0)
        self.assertGreater(result.velocity_hold_to_baseline_ratio, 5.0)

    def test_rejects_continuous_100hz_units_per_second_velocity_model(self) -> None:
        """Old continuous fixture (pos+=speed*dt, velocity=speed) must not pass."""

        ticks = sampler.synthetic_schedule_ticks()
        position = 0.0
        samples: dict[str, list[sampler.RawSample]] = {phase: [] for phase in sampler.PHASE_TARGETS}
        for phase in ("baseline", "hold", "release"):
            for slot, tick in enumerate(ticks[phase]):
                if phase == "baseline":
                    speed = 0.0
                    control = sampler.NEUTRAL_CONTROL_RAW
                elif phase == "hold":
                    speed = 0.0 if slot < 2 else (min(100.0, (slot - 1) * (100.0 / 48.0)) if slot < 50 else 100.0)
                    control = sampler.FORWARD_CONTROL_RAW
                else:
                    speed = max(0.0, 100.0 - slot * (100.0 / 48.0))
                    control = sampler.NEUTRAL_CONTROL_RAW
                position += speed * (sampler.CADENCE_MS / 1000.0)
                samples[phase].append(
                    sampler.RawSample(
                        tick=tick,
                        phase=phase,
                        slot=slot,
                        position=(position, 0.0, 0.0),
                        velocity=(speed, 0.0, 0.0),
                        state_raw=sampler.WALKER_STATE_RAW,
                        control_raw=control,
                    )
                )
        trace = sampler.AttemptTrace(
            attempt=1,
            receipt_sha256="1" * 64,
            run_digest="3" * 64,
            frequency=sampler.FREQUENCY_FIXTURE,
            samples=samples,
            down_bracket=(ticks["hold"][0] - 1000, ticks["hold"][0]),
            up_bracket=(ticks["release"][0] - 1000, ticks["release"][0]),
            integrity=sampler.AttemptIntegrity(
                receipt_revalidated=True,
                foreground_maintained=True,
                key_down_confirmed=True,
                key_up_confirmed=True,
                interference_detected=False,
                cleanup_confirmed=True,
            ),
        )
        with self.assertRaisesRegex(sampler.AttemptError, "velocity|update period"):
            sampler.analyze_attempt(trace)

    def test_rejects_drift_missing_control_response_slope_and_release(self) -> None:
        cases = {
            "baseline drift": {"baseline_drift": True},
            "control": {"missing_control": True},
            "response": {"missing_response": True},
            "slope": {"unstable_steady": True},
            "release": {"missing_release": True},
            "velocity": {"weak_velocity": True},
        }
        for message, kwargs in cases.items():
            with self.subTest(message=message), self.assertRaisesRegex(sampler.AttemptError, message):
                sampler.analyze_attempt(sampler.synthetic_attempt_trace(attempt=1, **kwargs))

    def test_rejects_forged_trace_state_phase_slot_bracket_and_velocity(self) -> None:
        mutations = []

        wrong_state = sampler.synthetic_attempt_trace(attempt=1)
        wrong_state.samples["hold"][10] = sampler.replace_sample(
            wrong_state.samples["hold"][10], state_raw=3
        )
        mutations.append(("walker state", wrong_state))

        wrong_phase = sampler.synthetic_attempt_trace(attempt=1)
        wrong_phase.samples["hold"][10] = sampler.replace_sample(
            wrong_phase.samples["hold"][10], phase="release"
        )
        mutations.append(("phase", wrong_phase))

        wrong_slot = sampler.synthetic_attempt_trace(attempt=1)
        wrong_slot.samples["hold"][10] = sampler.replace_sample(
            wrong_slot.samples["hold"][10], slot=99
        )
        mutations.append(("slot", wrong_slot))

        contradictory_control = sampler.synthetic_attempt_trace(attempt=1)
        for index in range(len(contradictory_control.samples["hold"])):
            contradictory_control.samples["hold"][index] = sampler.replace_sample(
                contradictory_control.samples["hold"][index],
                control_raw=sampler.NEUTRAL_CONTROL_RAW,
            )
        mutations.append(("control", contradictory_control))

        nonfinite = sampler.synthetic_attempt_trace(attempt=1)
        nonfinite.samples["hold"][20] = sampler.replace_sample(
            nonfinite.samples["hold"][20], position=(math.nan, 0.0, 0.0)
        )
        mutations.append(("finite", nonfinite))

        reversed_bracket = sampler.synthetic_attempt_trace(attempt=1)
        reversed_bracket.down_bracket = (reversed_bracket.down_bracket[1], reversed_bracket.down_bracket[0])
        mutations.append(("bracket", reversed_bracket))

        unrelated_bracket = sampler.synthetic_attempt_trace(attempt=1)
        unrelated_bracket.up_bracket = (0, 1)
        mutations.append(("boundary", unrelated_bracket))

        overwide_bracket = sampler.synthetic_attempt_trace(attempt=1)
        phase_start = overwide_bracket.samples["hold"][0].tick
        step = sampler.cadence_step_qpc(overwide_bracket.frequency)
        # Wider than schedule_max_gap_qpc (~250 ms / 25 cadences).
        overwide_bracket.down_bracket = (phase_start - 30 * step, phase_start - 29 * step)
        mutations.append(("boundary", overwide_bracket))

        contradictory_velocity = sampler.synthetic_attempt_trace(attempt=1, contradictory_velocity=True)
        mutations.append(("velocity", contradictory_velocity))

        acceleration_velocity = sampler.synthetic_attempt_trace(attempt=1)
        for index in range(2, 30):
            acceleration_velocity.samples["hold"][index] = sampler.replace_sample(
                acceleration_velocity.samples["hold"][index], velocity=(100.0, 0.0, 0.0)
            )
        mutations.append(("velocity", acceleration_velocity))

        release_velocity = sampler.synthetic_attempt_trace(attempt=1)
        for index, row in enumerate(release_velocity.samples["release"]):
            release_velocity.samples["release"][index] = sampler.replace_sample(
                row, velocity=(100.0, 0.0, 0.0)
            )
        mutations.append(("velocity", release_velocity))

        for message, trace in mutations:
            with self.subTest(message=message), self.assertRaisesRegex(sampler.AttemptError, message):
                sampler.analyze_attempt(trace)

    def test_input_session_fails_closed_on_focus_key_up_interference_and_cleanup(self) -> None:
        for field, message in (
            ("foreground_maintained", "foreground"),
            ("key_down_confirmed", "key-down"),
            ("key_up_confirmed", "key-up"),
            ("interference_detected", "interference"),
            ("cleanup_confirmed", "cleanup"),
            ("receipt_revalidated", "receipt"),
        ):
            trace = sampler.synthetic_attempt_trace(attempt=1)
            setattr(trace.integrity, field, False if field != "interference_detected" else True)
            with self.subTest(field=field), self.assertRaisesRegex(sampler.AttemptError, message):
                sampler.analyze_attempt(trace)

    def test_owned_q_window_always_attempts_key_up_when_body_fails(self) -> None:
        events: list[str] = []

        class Input:
            def key_down(self) -> bool:
                events.append("down")
                return True

            def key_up(self) -> bool:
                events.append("up")
                return True

        class Guard:
            def revalidate_receipt(self) -> bool:
                events.append("receipt")
                return True

            def foreground_matches(self) -> bool:
                events.append("foreground")
                return True

            def interference_detected(self) -> bool:
                return False

        ticks = iter((100, 101, 200, 201))

        def fail_body() -> None:
            raise RuntimeError("synthetic body failure")

        with self.assertRaisesRegex(RuntimeError, "synthetic body failure"):
            sampler.execute_owned_q_window(Guard(), Input(), lambda: next(ticks), [fail_body])
        self.assertEqual("up", events[-1])

    def test_owned_q_window_keys_up_on_preflight_and_batch_guard_failure(self) -> None:
        class Input:
            def __init__(self) -> None:
                self.events: list[str] = []

            def key_down(self) -> bool:
                self.events.append("down")
                return True

            def key_up(self) -> bool:
                self.events.append("up")
                return True

        class Guard:
            def __init__(self, fail_call: int) -> None:
                self.calls = 0
                self.fail_call = fail_call

            def revalidate_receipt(self) -> bool:
                self.calls += 1
                return self.calls != self.fail_call

            def foreground_matches(self) -> bool:
                return True

            def interference_detected(self) -> bool:
                return False

        for fail_call in (1, 3):
            q_input = Input()
            ticks = iter(range(100, 110))
            with self.subTest(fail_call=fail_call), self.assertRaisesRegex(
                sampler.AttemptError, "receipt"
            ):
                sampler.execute_owned_q_window(
                    Guard(fail_call), q_input, lambda: next(ticks), [lambda: "batch"]
                )
            self.assertEqual("up", q_input.events[-1])

    def test_owned_q_window_success_cleanup_failures_and_combined_context(self) -> None:
        class Guard:
            def revalidate_receipt(self) -> bool:
                return True

            def foreground_matches(self) -> bool:
                return True

            def interference_detected(self) -> bool:
                return False

        class Input:
            def __init__(self, *, up: bool = True) -> None:
                self.up = up
                self.events: list[str] = []

            def key_down(self) -> bool:
                self.events.append("down")
                return True

            def key_up(self) -> bool:
                self.events.append("up")
                return self.up

        result = sampler.execute_owned_q_window(
            Guard(), Input(), iter((10, 11, 20, 21)).__next__, [lambda: "a", lambda: "b"]
        )
        self.assertEqual(("a", "b"), result.value)
        self.assertEqual((10, 11), result.down_bracket)
        self.assertEqual((20, 21), result.up_bracket)

        with self.assertRaisesRegex(sampler.AttemptError, "key-up"):
            sampler.execute_owned_q_window(
                Guard(), Input(up=False), iter((10, 11, 20, 21)).__next__, [lambda: None]
            )

        q_input = Input()
        clock_calls = iter((10, 11, RuntimeError("clock cleanup"), 21))

        def failing_cleanup_clock() -> int:
            value = next(clock_calls)
            if isinstance(value, BaseException):
                raise value
            return value

        with self.assertRaisesRegex(sampler.AttemptError, "timestamp"):
            sampler.execute_owned_q_window(Guard(), q_input, failing_cleanup_clock, [lambda: None])
        self.assertEqual("up", q_input.events[-1])

        def fail_body() -> None:
            raise RuntimeError("primary batch failure")

        with self.assertRaisesRegex(sampler.AttemptError, "primary batch failure"):
            sampler.execute_owned_q_window(
                Guard(), Input(up=False), iter((10, 11, 20, 21)).__next__, [fail_body]
            )


class PairAndSchemaTests(unittest.TestCase):
    def test_two_fresh_accepted_attempts_produce_exact_envelope(self) -> None:
        first = metrics(attempt=1, steady_speed=100.0)
        second = metrics(attempt=2, steady_speed=106.0, response=latency(20, 40), release=latency(40, 60))

        projection = sampler.materialize_pair([first, second])

        schema.validate_public_projection(projection)
        self.assertEqual("battleengine-walker-forward-scalar-response.v2", projection["schemaVersion"])
        self.assertEqual(
            {
                "position": "retail-world-coordinate-unit",
                "speed": "retail-world-coordinate-units-per-second",
                "speedSlope": "retail-world-coordinate-units-per-second-squared",
                "latency": "milliseconds",
                "ratio": "unitless",
            },
            projection["metricUnits"],
        )
        self.assertIn(
            "No scalar, including a unitless ratio, authorizes deterministic-Core behavior.",
            projection["nonclaims"],
        )
        self.assertIn(
            "No conversion from QPC seconds or milliseconds to deterministic-Core ticks is established.",
            projection["nonclaims"],
        )
        self.assertEqual(95.0, projection["envelope"]["steadySpeed"]["lower"])
        self.assertEqual(111.3, projection["envelope"]["steadySpeed"]["upper"])
        self.assertEqual({"lower": 20, "upper": 40}, projection["envelope"]["responseLatencyMs"])
        self.assertEqual({"lower": 30, "upper": 60}, projection["envelope"]["releaseLatencyMs"])
        serialized = str(projection)
        self.assertNotIn("C:/", serialized)
        self.assertNotIn("0x30000000", serialized)

    def test_requires_two_valid_fresh_attempts_and_rejects_third(self) -> None:
        valid1 = metrics(attempt=1)
        valid2 = metrics(attempt=2)
        invalid1 = sampler.replace_metrics(valid1, accepted=False)
        invalid2 = sampler.replace_metrics(valid2, accepted=False)
        for attempts in ([valid1], [invalid1, valid2], [valid1, invalid2], [invalid1, invalid2]):
            with self.subTest(count=len(attempts)), self.assertRaisesRegex(sampler.AttemptError, "two accepted"):
                sampler.materialize_pair(attempts)
        with self.assertRaisesRegex(sampler.AttemptError, "third"):
            sampler.materialize_pair([valid1, valid2, metrics(attempt=3)])
        duplicate = sampler.replace_metrics(valid2, receipt_sha256=valid1.receipt_sha256)
        with self.assertRaisesRegex(sampler.AttemptError, "fresh"):
            sampler.materialize_pair([valid1, duplicate])
        duplicate_run = sampler.replace_metrics(valid2, run_digest=valid1.run_digest)
        with self.assertRaisesRegex(sampler.AttemptError, "fresh"):
            sampler.materialize_pair([valid1, duplicate_run])
        with self.assertRaisesRegex(sampler.AttemptError, "order"):
            sampler.materialize_pair([valid2, valid1])
        with self.assertRaisesRegex(sampler.AttemptError, "steady"):
            sampler.materialize_pair([sampler.replace_metrics(valid1, steady_speed=0.0), valid2])
        bad_nodes = sampler.replace_metrics(valid2, normalized_response={"100ms": 0.2})
        with self.assertRaisesRegex(sampler.AttemptError, "nodes"):
            sampler.materialize_pair([valid1, bad_nodes])
        for malformed in (
            sampler.replace_metrics(valid2, steady_speed="fast"),
            sampler.replace_metrics(valid2, normalized_response=None),
        ):
            with self.subTest(malformed=malformed), self.assertRaisesRegex(
                sampler.AttemptError, "metric|nodes"
            ):
                sampler.materialize_pair([valid1, malformed])
        inverted = sampler.replace_metrics(valid2, response_latency=latency(40, 20))
        with self.assertRaisesRegex(sampler.AttemptError, "latency"):
            sampler.materialize_pair([valid1, inverted])

    def test_rejects_unstable_two_run_pair(self) -> None:
        cases = (
            metrics(attempt=2, steady_speed=120.0),
            metrics(attempt=2, response=latency(60, 70)),
            metrics(attempt=2, release=latency(100, 110)),
            metrics(attempt=2, normalized=(0.50, 0.50, 0.80, 0.98)),
        )
        for second in cases:
            with self.subTest(second=second), self.assertRaisesRegex(sampler.AttemptError, "stable"):
                sampler.materialize_pair([metrics(attempt=1), second])

    def test_public_schema_rejects_private_keys_and_path_like_values(self) -> None:
        projection = sampler.materialize_pair([metrics(attempt=1), metrics(attempt=2)])
        for key, value in (
            ("path", "private"),
            ("pid", 42),
            ("pointer", "0x30000000"),
            ("hwnd", "0x1234"),
            ("moduleBase", "0x10000000"),
            ("rawSamples", []),
            ("log", "raw.log"),
        ):
            leaked = copy.deepcopy(projection)
            leaked["attempts"][0][key] = value
            with self.subTest(key=key), self.assertRaises(schema.SchemaError):
                schema.validate_public_projection(leaked)

        leaked = copy.deepcopy(projection)
        leaked["nonclaims"][0] = str(Path("C:/private/runtime/raw.json"))
        with self.assertRaisesRegex(schema.SchemaError, "path-like"):
            schema.validate_public_projection(leaked)

        leaked = copy.deepcopy(projection)
        leaked["nonclaims"][0] = "/home/user/raw.json"
        with self.assertRaisesRegex(schema.SchemaError, "path-like"):
            schema.validate_public_projection(leaked)

        for replacement in (
            ["parity complete"],
            ["C:private.txt", "raw.log", "PID 1234 at 0x30000000"],
            projection["nonclaims"][:-1],
        ):
            leaked = copy.deepcopy(projection)
            leaked["nonclaims"] = replacement
            with self.subTest(replacement=replacement), self.assertRaisesRegex(
                schema.SchemaError, "nonclaims"
            ):
                schema.validate_public_projection(leaked)

    def test_public_schema_recomputes_timing_and_envelope_contract(self) -> None:
        projection = sampler.materialize_pair([metrics(attempt=1), metrics(attempt=2)])
        mutations = []

        missing_units = copy.deepcopy(projection)
        self.assertIn("metricUnits", missing_units)
        del missing_units["metricUnits"]
        mutations.append(("exact keys", missing_units))

        forged_units = copy.deepcopy(projection)
        forged_units["metricUnits"]["speed"] = "meters-per-second"
        mutations.append(("metric units", forged_units))

        off_cadence = copy.deepcopy(projection)
        off_cadence["attempts"][0]["metrics"]["responseLatencyMs"] = {"lower": 7, "upper": 19}
        mutations.append(("cadence", off_cadence))

        too_long = copy.deepcopy(projection)
        too_long["attempts"][0]["metrics"]["releaseLatencyMs"] = {"lower": 740, "upper": 760}
        mutations.append(("duration", too_long))

        too_many = copy.deepcopy(projection)
        too_many["attempts"][0]["sampleCounts"]["hold"] = 76
        mutations.append(("count", too_many))

        forged_envelope = copy.deepcopy(projection)
        forged_envelope["envelope"]["steadySpeed"]["upper"] += 1.0
        mutations.append(("envelope", forged_envelope))

        for message, payload in mutations:
            with self.subTest(message=message), self.assertRaisesRegex(schema.SchemaError, message):
                schema.validate_public_projection(payload)


if __name__ == "__main__":
    unittest.main(verbosity=2)
