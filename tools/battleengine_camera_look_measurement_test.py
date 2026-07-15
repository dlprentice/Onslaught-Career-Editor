#!/usr/bin/env python3
"""Unit tests for camera look measurement harness (no live BEA)."""

from __future__ import annotations

import math
import unittest

import battleengine_camera_look_measurement as cam


class CameraLookHarnessTests(unittest.TestCase):
    def test_unwrap_crosses_pi(self) -> None:
        delta = cam.unwrap_delta(math.pi - 0.1, -math.pi + 0.1)
        self.assertAlmostEqual(0.2, delta, places=6)

    def test_orientation_attempt_accepts_and_pair_envelope(self) -> None:
        frequency = 10_000_000
        b1, h1, r1 = cam.synthetic_camera_look_attempt(attempt=1, steady_rate=0.09)
        b2, h2, r2 = cam.synthetic_camera_look_attempt(attempt=2, steady_rate=0.092)
        m1 = cam.analyze_camera_look_attempt(
            attempt=1, baseline=b1, hold=h1, release=r1, frequency=frequency
        )
        m2 = cam.analyze_camera_look_attempt(
            attempt=2, baseline=b2, hold=h2, release=r2, frequency=frequency
        )
        self.assertTrue(m1.accepted)
        self.assertTrue(m2.accepted)
        self.assertGreater(m1.steady_yaw_rate_rad_s, 0.05)
        envelope = cam.materialize_camera_look_pair_envelope(m1, m2)
        self.assertEqual(
            "battleengine-camera-look-rate-scalar-response.v0-scaffold",
            envelope["schemaVersion"],
        )
        self.assertIn(cam.FREE_CAMERA_PATCH_CANARY_NONCLAIM, envelope["nonclaims"])

    def test_rejects_weak_hold_vs_baseline(self) -> None:
        frequency = 10_000_000
        baseline, hold, release = cam.synthetic_camera_look_attempt(
            attempt=1, steady_rate=0.02, baseline_rate=0.015
        )
        with self.assertRaisesRegex(cam.CameraLookError, "dominate baseline"):
            cam.analyze_camera_look_attempt(
                attempt=1,
                baseline=baseline,
                hold=hold,
                release=release,
                frequency=frequency,
            )

    def test_yaw_axis_store_rate_source(self) -> None:
        frequency = 10_000_000
        step = frequency // 100

        def series(phase: str, n: int, axis: float) -> list[cam.LookSample]:
            return [
                cam.LookSample(
                    tick=i * step,
                    phase=phase,
                    yaw_rad=0.0,
                    yaw_axis=axis,
                )
                for i in range(n)
            ]

        metrics = cam.analyze_camera_look_attempt(
            attempt=1,
            baseline=series("baseline", 20, 0.0),
            hold=series("hold", 40, 0.0905),
            release=series("release", 20, 0.0),
            frequency=frequency,
            rate_source="yaw_axis_store",
        )
        self.assertTrue(metrics.accepted)
        self.assertAlmostEqual(0.0905, metrics.steady_yaw_rate_rad_s, places=3)

    def test_yaw_axis_offset_hypothesis_is_explicit(self) -> None:
        self.assertEqual(0x278, cam.BATTLE_ENGINE_YAW_AXIS_OFFSET)


if __name__ == "__main__":
    unittest.main()
