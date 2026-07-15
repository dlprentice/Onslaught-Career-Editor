#!/usr/bin/env python3
"""Tests for shield rate scaffold."""

from __future__ import annotations

import inspect
import math
import unittest

import battleengine_shield_scaffold as shield


def pair_identity_kwargs() -> dict[str, str]:
    return {
        "first_receipt_sha256": "1" * 64,
        "second_receipt_sha256": "2" * 64,
        "first_run_digest": "3" * 64,
        "second_run_digest": "4" * 64,
    }


class ShieldScaffoldTests(unittest.TestCase):
    def test_shield_sample_carries_paired_energy(self) -> None:
        self.assertEqual(
            ["tick", "shield", "energy"],
            list(inspect.signature(shield.ShieldSample).parameters),
        )

    def test_metrics_expose_energy_correlation(self) -> None:
        self.assertEqual(
            [
                "attempt",
                "accepted",
                "steady_rate_per_sec",
                "steady_energy_rate_per_sec",
                "paired_active_edge_fraction",
                "relative_rate_delta",
                "sample_count",
            ],
            list(inspect.signature(shield.ShieldRateMetrics).parameters),
        )

    def test_synthetic_series_can_vary_energy_independently(self) -> None:
        self.assertEqual(
            [
                "start",
                "rate_per_sec",
                "energy_start",
                "energy_rate_per_sec",
                "n",
                "frequency",
            ],
            list(inspect.signature(shield.synthetic_shield_series).parameters),
        )

    def test_regen(self) -> None:
        samples = shield.synthetic_shield_series(rate_per_sec=2.0)
        m = shield.analyze_shield_rate(
            attempt=1, samples=samples, frequency=10_000_000, expect_positive=True
        )
        self.assertTrue(m.accepted)
        self.assertGreater(m.steady_rate_per_sec, 1.0)
        self.assertGreater(m.steady_energy_rate_per_sec, 1.0)
        self.assertEqual(1.0, m.paired_active_edge_fraction)
        self.assertAlmostEqual(0.0, m.relative_rate_delta)

    def test_rejects_drain_when_expecting_regen(self) -> None:
        samples = shield.synthetic_shield_series(rate_per_sec=-1.0)
        with self.assertRaisesRegex(shield.ShieldScaffoldError, "direction reversed"):
            shield.analyze_shield_rate(
                attempt=1,
                samples=samples,
                frequency=10_000_000,
                expect_positive=True,
            )

    def test_accepts_paired_drain_when_negative_is_expected(self) -> None:
        metrics = shield.analyze_shield_rate(
            attempt=1,
            samples=shield.synthetic_shield_series(rate_per_sec=-2.0),
            frequency=10_000_000,
            expect_positive=False,
        )
        self.assertLess(metrics.steady_rate_per_sec, 0.0)
        self.assertLess(metrics.steady_energy_rate_per_sec, 0.0)

    def test_rejects_shield_regen_when_energy_is_static(self) -> None:
        samples = shield.synthetic_shield_series(
            rate_per_sec=2.0,
            energy_rate_per_sec=0.0,
        )
        with self.assertRaisesRegex(shield.ShieldScaffoldError, "energy.*track"):
            shield.analyze_shield_rate(
                attempt=1,
                samples=samples,
                frequency=10_000_000,
                expect_positive=True,
            )

    def test_rejects_opposite_energy_direction(self) -> None:
        samples = shield.synthetic_shield_series(
            rate_per_sec=2.0,
            energy_rate_per_sec=-2.0,
        )
        with self.assertRaisesRegex(shield.ShieldScaffoldError, "direction reversed"):
            shield.analyze_shield_rate(
                attempt=1,
                samples=samples,
                frequency=10_000_000,
                expect_positive=True,
            )

    def test_rejects_excessive_energy_shield_rate_delta(self) -> None:
        samples = shield.synthetic_shield_series(
            rate_per_sec=2.0,
            energy_rate_per_sec=4.0,
        )
        with self.assertRaisesRegex(shield.ShieldScaffoldError, "rate correlation"):
            shield.analyze_shield_rate(
                attempt=1,
                samples=samples,
                frequency=10_000_000,
                expect_positive=True,
            )

    def test_rejects_energy_only_edges_outside_the_shield_mirror(self) -> None:
        frequency = 10_000_000
        step = frequency // 100
        shield_value = 50.0
        energy_value = 50.0
        samples = []
        for index in range(40):
            samples.append(
                shield.ShieldSample(
                    tick=index * step,
                    shield=shield_value,
                    energy=energy_value,
                )
            )
            energy_value += 0.01
            if index % 5 == 0:
                shield_value += 0.01
        with self.assertRaisesRegex(shield.ShieldScaffoldError, "track enough"):
            shield.analyze_shield_rate(
                attempt=1,
                samples=samples,
                frequency=frequency,
                expect_positive=True,
            )

    def test_rejects_material_wrong_direction_disturbance_during_regen(self) -> None:
        frequency = 10_000_000
        step = frequency // 100
        for disturbed_field in ("shield", "energy"):
            shield_value = 50.0
            energy_value = 50.0
            samples = []
            for index in range(40):
                samples.append(
                    shield.ShieldSample(
                        tick=index * step,
                        shield=shield_value,
                        energy=energy_value,
                    )
                )
                if index < 7 and disturbed_field == "shield":
                    shield_value -= 1.0
                elif index < 7:
                    energy_value -= 1.0
                else:
                    shield_value += 0.02
                    energy_value += 0.02
            with self.subTest(disturbed_field=disturbed_field), self.assertRaisesRegex(
                shield.ShieldScaffoldError,
                "direction reversed",
            ):
                shield.analyze_shield_rate(
                    attempt=1,
                    samples=samples,
                    frequency=frequency,
                    expect_positive=True,
                )

    def test_rejects_nonfinite_paired_samples(self) -> None:
        for field in ("shield", "energy"):
            samples = shield.synthetic_shield_series(rate_per_sec=2.0)
            first = samples[0]
            samples[0] = shield.ShieldSample(
                tick=first.tick,
                shield=math.nan if field == "shield" else first.shield,
                energy=math.nan if field == "energy" else first.energy,
            )
            with self.subTest(field=field), self.assertRaisesRegex(
                shield.ShieldScaffoldError, "finite"
            ):
                shield.analyze_shield_rate(
                    attempt=1,
                    samples=samples,
                    frequency=10_000_000,
                    expect_positive=True,
                )

    def test_rejects_nonmonotonic_ticks(self) -> None:
        samples = shield.synthetic_shield_series(rate_per_sec=2.0)
        samples[1] = shield.ShieldSample(
            tick=samples[0].tick,
            shield=samples[1].shield,
            energy=samples[1].energy,
        )
        with self.assertRaisesRegex(shield.ShieldScaffoldError, "non-monotonic"):
            shield.analyze_shield_rate(
                attempt=1,
                samples=samples,
                frequency=10_000_000,
                expect_positive=True,
            )

    def test_pair_envelope(self) -> None:
        frequency = 10_000_000
        m1 = shield.analyze_shield_rate(
            attempt=1,
            samples=shield.synthetic_shield_series(rate_per_sec=2.0),
            frequency=frequency,
        )
        m2 = shield.analyze_shield_rate(
            attempt=2,
            samples=shield.synthetic_shield_series(rate_per_sec=2.1),
            frequency=frequency,
        )
        envelope = shield.materialize_shield_pair_envelope(
            m1,
            m2,
            **pair_identity_kwargs(),
        )
        self.assertEqual(
            "battleengine-shield-rate-scalar-response.v0-scaffold",
            envelope["schemaVersion"],
        )
        self.assertEqual(
            {
                "steadyShieldRatePerSec",
                "steadyEnergyRatePerSec",
                "pairedActiveEdgeFraction",
                "rateRelativeDelta",
            },
            set(envelope["envelope"]),
        )
        self.assertGreater(
            envelope["envelope"]["pairedActiveEdgeFraction"]["lower"],
            0.79,
        )
        self.assertLessEqual(
            envelope["envelope"]["rateRelativeDelta"]["upper"],
            0.25,
        )
        self.assertEqual("0x100", envelope["offsetHypothesis"]["battleEngineShields"])

    def test_pair_envelope_rejects_unstable(self) -> None:
        frequency = 10_000_000
        m1 = shield.analyze_shield_rate(
            attempt=1,
            samples=shield.synthetic_shield_series(rate_per_sec=1.0),
            frequency=frequency,
        )
        m2 = shield.analyze_shield_rate(
            attempt=2,
            samples=shield.synthetic_shield_series(rate_per_sec=3.0),
            frequency=frequency,
        )
        with self.assertRaisesRegex(shield.ShieldScaffoldError, "not stable"):
            shield.materialize_shield_pair_envelope(
                m1,
                m2,
                **pair_identity_kwargs(),
            )

    def test_pair_envelope_rejects_unstable_energy_rates(self) -> None:
        frequency = 10_000_000
        m1 = shield.analyze_shield_rate(
            attempt=1,
            samples=shield.synthetic_shield_series(
                rate_per_sec=1.0,
                energy_rate_per_sec=0.8,
            ),
            frequency=frequency,
        )
        m2 = shield.analyze_shield_rate(
            attempt=2,
            samples=shield.synthetic_shield_series(
                rate_per_sec=1.2,
                energy_rate_per_sec=1.5,
            ),
            frequency=frequency,
        )
        with self.assertRaisesRegex(shield.ShieldScaffoldError, "energy rates not stable"):
            shield.materialize_shield_pair_envelope(
                m1,
                m2,
                **pair_identity_kwargs(),
            )

    def test_pair_envelope_requires_attempts_one_and_two(self) -> None:
        metrics = shield.analyze_shield_rate(
            attempt=1,
            samples=shield.synthetic_shield_series(rate_per_sec=1.0),
            frequency=10_000_000,
        )
        with self.assertRaisesRegex(shield.ShieldScaffoldError, "order"):
            shield.materialize_shield_pair_envelope(
                metrics,
                metrics,
                **pair_identity_kwargs(),
            )

    def test_pair_envelope_requires_fresh_receipt_and_run_identities(self) -> None:
        first = shield.analyze_shield_rate(
            attempt=1,
            samples=shield.synthetic_shield_series(rate_per_sec=1.0),
            frequency=10_000_000,
        )
        second = shield.analyze_shield_rate(
            attempt=2,
            samples=shield.synthetic_shield_series(rate_per_sec=1.0),
            frequency=10_000_000,
        )
        identities = pair_identity_kwargs()
        for duplicate_key, source_key in (
            ("second_receipt_sha256", "first_receipt_sha256"),
            ("second_run_digest", "first_run_digest"),
        ):
            duplicate = dict(identities)
            duplicate[duplicate_key] = duplicate[source_key]
            with self.subTest(duplicate_key=duplicate_key), self.assertRaisesRegex(
                shield.ShieldScaffoldError,
                "identities are not fresh",
            ):
                shield.materialize_shield_pair_envelope(
                    first,
                    second,
                    **duplicate,
                )


if __name__ == "__main__":
    unittest.main()
