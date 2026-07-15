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
        live_status="sampler-wired; dual-accept pending",
        notes="BE+0xFC hypothesis; --measure energy --vehicle jet",
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
