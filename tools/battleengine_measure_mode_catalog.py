#!/usr/bin/env python3
"""Catalog of rebuild-grade measure modes and their harness modules.

Keeps next-slice agents from re-inventing wiring when resuming the campaign.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MeasureModeRow:
    mode: str
    vehicle: str
    analysis_module: str
    live_status: str
    notes: str


MEASURE_MODE_CATALOG: tuple[MeasureModeRow, ...] = (
    MeasureModeRow(
        mode="forward",
        vehicle="walker|jet",
        analysis_module="battleengine_walker_trajectory_sampler",
        live_status="dual-accepted",
        notes="WalkerSpeedPerTick=100; JetSpeedPerTick=381",
    ),
    MeasureModeRow(
        mode="turn",
        vehicle="walker",
        analysis_module="battleengine_turn_yaw_measurement",
        live_status="dual-accepted",
        notes="WalkerLookYawRateMilliRadPerTick=3; Core LookX wired",
    ),
    MeasureModeRow(
        mode="strafe",
        vehicle="walker",
        analysis_module="battleengine_strafe_measurement",
        live_status="dual-accepted",
        notes="WalkerStrafeSpeedPerTick=101",
    ),
    MeasureModeRow(
        mode="transform",
        vehicle="walker→jet",
        analysis_module="battleengine_transform_timing_measurement",
        live_status="dual-accepted",
        notes="MorphToJetSettleTicks=148",
    ),
    MeasureModeRow(
        mode="energy",
        vehicle="jet",
        analysis_module="battleengine_energy_scaffold",
        live_status="dual-accepted energy-p02",
        notes="BE+0xFC; JetEnergyDrainPerTick=17; walker regen still provisional",
    ),
)


def catalog_as_dicts() -> list[dict[str, str]]:
    return [
        {
            "mode": row.mode,
            "vehicle": row.vehicle,
            "analysisModule": row.analysis_module,
            "liveStatus": row.live_status,
            "notes": row.notes,
        }
        for row in MEASURE_MODE_CATALOG
    ]


def mode_names() -> frozenset[str]:
    return frozenset(row.mode for row in MEASURE_MODE_CATALOG)


# Offline-only harnesses (not yet pair-runner measure modes).
OFFLINE_HARNESS_ROWS: tuple[MeasureModeRow, ...] = (
    MeasureModeRow(
        mode="coast",
        vehicle="walker|jet release",
        analysis_module="battleengine_coast_friction_measurement",
        live_status="scaffold; live dual-accept pending",
        notes="Release half-life; may reuse forward release series",
    ),
    MeasureModeRow(
        mode="camera-look",
        vehicle="walker look / camera",
        analysis_module="battleengine_camera_look_measurement",
        live_status="scaffold; free-cam not Core authority",
        notes="Body LookX already dual-accepted via turn; camera presentation open",
    ),
    MeasureModeRow(
        mode="fire-cooldown",
        vehicle="fire hold",
        analysis_module="battleengine_fire_cooldown_scaffold",
        live_status="scaffold; energy-drop edges ready",
        notes="Needs fire input path; BE+0xFC drops preferred",
    ),
    MeasureModeRow(
        mode="projectile-speed",
        vehicle="projectile entity",
        analysis_module="battleengine_projectile_speed_scaffold",
        live_status="scaffold; entity tracking pending",
        notes="Pair envelope ready; Core ProjectileSpeedPerTick provisional",
    ),
    MeasureModeRow(
        mode="shield-rate",
        vehicle="walker",
        analysis_module="battleengine_shield_scaffold",
        live_status="scaffold+offset BE+0x100; live pending",
        notes="Paired with energy BE+0xFC",
    ),
)


def offline_harness_dicts() -> list[dict[str, str]]:
    return [
        {
            "mode": row.mode,
            "vehicle": row.vehicle,
            "analysisModule": row.analysis_module,
            "liveStatus": row.live_status,
            "notes": row.notes,
        }
        for row in OFFLINE_HARNESS_ROWS
    ]


def full_catalog_report() -> dict[str, object]:
    return {
        "liveMeasureModes": catalog_as_dicts(),
        "offlineHarnesses": offline_harness_dicts(),
    }


if __name__ == "__main__":
    import json
    import sys

    json.dump(full_catalog_report(), sys.stdout, indent=2)
    sys.stdout.write("\n")
