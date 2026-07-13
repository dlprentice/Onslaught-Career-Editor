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

    def put_u32(self, address: int, value: int) -> None:
        self.values[(address, 4)] = struct.pack("<I", value)

    def put_f32x3(self, address: int, values: tuple[float, float, float]) -> None:
        self.values[(address, 12)] = struct.pack("<3f", *values)

    def put_f32(self, address: int, value: float) -> None:
        self.values[(address, 4)] = struct.pack("<f", value)

    def read(self, address: int, size: int) -> bytes:
        self.read_count += 1
        key = (address, size)
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

        jitter = copy.deepcopy(ticks)
        jitter["hold"][4] += 60_000
        with self.assertRaisesRegex(sampler.AttemptError, "jitter"):
            sampler.validate_schedule(jitter, frequency=10_000_000)

        gap = copy.deepcopy(ticks)
        del gap["hold"][10:12]
        with self.assertRaisesRegex(sampler.AttemptError, "consecutive|gap"):
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
        with self.assertRaisesRegex(sampler.AttemptError, "window|boundary|slot"):
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
        contradictory_control.samples["hold"][20] = sampler.replace_sample(
            contradictory_control.samples["hold"][20], control_raw=sampler.NEUTRAL_CONTROL_RAW
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
        step = overwide_bracket.frequency * sampler.CADENCE_MS // 1000
        overwide_bracket.down_bracket = (phase_start - 2 * step, phase_start - step)
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
