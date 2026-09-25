#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compare production GDScript with the existing C# and native fixtures.

This is a temporary migration oracle, not a second simulation or asset pipeline.
Every invocation owns its logs, profiles, oracle build and vector data. Godot is
always the pinned standard edition, headless, with no desktop connection.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from godot_host import ENGINE_VERSION, output_directory, print_process_output, run_process

STANDARD_VERSION = ENGINE_VERSION.replace(".mono.", ".")
CHECKS = (
    ("numerics", "numerics_checks.gd", ["arithmetic", "euler", "rng", "wide", "binary"], 60),
    ("pause-model", "pause_model_checks.gd", ["pause_model"], 30),
    ("strict-json", "strict_json_checks.gd", ["strict_json"], 30),
    ("startup-schedule", "startup_schedule_checks.gd", ["startup_schedule"], 30),
    ("chunk-reader", "chunk_reader_checks.gd", ["chunk_reader"], 30),
    ("event-scheduler", "event_scheduler_checks.gd", ["event_scheduler"], 60),
    ("invariant-format", "invariant_format_checks.gd", ["invariant_format"], 30),
    ("replay-hash", "replay_hash_checks.gd", ["replay_hash"], 60),
    ("startup-media", "startup_media_checks.gd", ["startup_media"], 60),
    ("command-tape", "command_tape_checks.gd", ["json", "validation", "inputs", "strings", "readers", "boundary"], 60),
    ("message-panel", "message_panel_checks.gd", ["wrap_window", "reveal", "boundary"], 30),
    ("hud-presentation", "hud_presentation_checks.gd", ["hud_presentation"], 30),
    ("startup-media-batch", "startup_media_batch_checks.gd", ["startup_media_batch"], 30),
    ("state-hash", "state_hash_checks.gd", ["state_hash"], 60),
    ("retail-career", "retail_career_checks.gd", ["numeric", "objectives", "campaign", "world_strings", "ownership"], 60),
    ("client-input", "input_checks.gd", ["client_input"], 30),
    ("camera-values", "camera_value_checks.gd", ["aspect", "movie", "viewpoint", "ownership"], 30),
    ("frontend-session", "frontend_session_checks.gd", ["constants", "glyphs", "constructors", "transitions", "ownership", "transport"], 60),
    ("career-save", "career_save_checks.gd", ["reader", "ownership", "read_only"], 30),
    ("attached-camera", "attached_camera_checks.gd", ["attached_camera"], 60),
    ("control-response", "control_response_checks.gd", ["control_response"], 30),
    ("audio-policy", "audio_policy_checks.gd", ["audio_policy"], 60),
    ("mission-timing", "mission_timing_checks.gd", ["mission_timing"], 30),
    ("render-interpolation", "render_interpolation_checks.gd", ["render_interpolation"], 60),
    ("options", "options_checks.gd", ["numeric", "state", "controller", "ownership"], 60),
    ("invariant-number", "invariant_number_checks.gd", ["invariant_number"], 90),
    ("particle-set", "particle_set_checks.gd", ["cases", "contracts", "corpus", "ownership"], 90),
    ("particle-effects", "particle_effect_checks.gd", ["particle_effects"], 90),
    ("terrain", "terrain_checks.gd", ["terrain"], 90),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", default="godot48", help="pinned standard Godot executable")
    parser.add_argument("--output-root", type=Path, help="fresh path inside this checkout's local-data")
    parser.add_argument("--check", action="append", choices=[name for name, *_ in CHECKS],
                        help="run only this comparison group; may be repeated (default: all)")
    args = parser.parse_args(argv)
    if not sys.platform.startswith("linux"):
        parser.error("this headless migration gate currently supports Linux")
    output = None
    try:
        engine = shutil.which(args.engine)
        dotnet = shutil.which("dotnet")
        if engine is None or dotnet is None:
            raise RuntimeError("The standard Godot 4.8 dev6 engine and dotnet comparison tool are required")
        output = output_directory(ROOT, args.output_root, "test-runs", "gdscript-parity")
        env = os.environ.copy()
        for name in ("DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY"):
            env.pop(name, None)
        for name, child in (("TMPDIR", "tmp"), ("XDG_DATA_HOME", "data"),
                            ("XDG_CONFIG_HOME", "config"), ("XDG_CACHE_HOME", "cache")):
            directory = output / child
            directory.mkdir(mode=0o700)
            env[name] = str(directory)
        env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"

        def run(command: list[str], name: str, timeout: float, *, cwd: Path = ROOT) -> str:
            try:
                completed = run_process(command, cwd=cwd, env=env, timeout=timeout, capture=True)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
                data = error.output or ""
                errors = error.stderr or ""
                if isinstance(data, bytes):
                    data = data.decode("utf-8", errors="replace")
                if isinstance(errors, bytes):
                    errors = errors.decode("utf-8", errors="replace")
                (output / name).write_text(data + errors, encoding="utf-8")
                raise
            text = (completed.stdout or "") + (completed.stderr or "")
            (output / name).write_text(text, encoding="utf-8")
            return text

        version = run([engine, "--headless", "--version"], "engine.log", 15).strip()
        if version != STANDARD_VERSION:
            raise RuntimeError(f"Expected {STANDARD_VERSION}; found {version!r}")
        oracle = output / "oracle"
        oracle.mkdir()
        project = ET.Element("Project", Sdk="Microsoft.NET.Sdk")
        properties = ET.SubElement(project, "PropertyGroup")
        for name, value in (("OutputType", "Exe"), ("TargetFramework", "net8.0"),
                            ("ImplicitUsings", "enable"), ("Nullable", "enable"),
                            ("NuGetAudit", "false")):
            ET.SubElement(properties, name).text = value
        items = ET.SubElement(project, "ItemGroup")
        ET.SubElement(items, "ProjectReference", Include=str(ROOT / "rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptParityOracle.cs"))
        for helper in ("GdscriptJsonOracle.cs", "GdscriptStartupScheduleOracle.cs", "GdscriptChunkReaderOracle.cs", "GdscriptEventSchedulerOracle.cs", "GdscriptInvariantFormatOracle.cs", "GdscriptReplayOracle.cs", "GdscriptStartupMediaOracle.cs", "GdscriptCommandTapeOracle.cs", "GdscriptMessagePanelOracle.cs", "GdscriptHudPresentationOracle.cs", "GdscriptStartupMediaBatchOracle.cs", "GdscriptStateHashOracle.cs", "GdscriptRetailCareerOracle.cs", "GdscriptInputOracle.cs", "GdscriptCameraOracle.cs", "GdscriptFrontendSessionOracle.cs"):
            ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport" / helper))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/OnslaughtRebuild.Godot/RetailStartupMediaIndex.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/OnslaughtRebuild.Godot/Level100MessagePlaybackState.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/OnslaughtRebuild.Godot/Level100HudPresentation.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/OnslaughtRebuild.Godot/Level100MessageSchedule.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptCareerSaveOracle.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptAttachedCameraOracle.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptControlResponseOracle.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptAudioPolicyOracle.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/OnslaughtRebuild.Godot/Level100AudioCatalog.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptMissionTimingOracle.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptRenderInterpolationOracle.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptOptionsOracle.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptInvariantNumberOracle.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptParticleSetOracle.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptParticleEffectOracle.cs"))
        ET.SubElement(items, "Compile", Include=str(ROOT / "rebuild/TestSupport/GdscriptTerrainOracle.cs"))
        project_path = oracle / "Oracle.csproj"
        ET.ElementTree(project).write(project_path, encoding="unicode")
        vectors = output / "vectors.json"
        run([dotnet, "run", "--project", str(project_path), "--artifacts-path", str(output / "build"),
             "--disable-build-servers", "--", str(vectors),
             str(ROOT / "rebuild/scenarios/first-flight.v1.json"),
             str(ROOT / "tests_shared/fixtures/gold_career_save.bin")], "oracle.log", 180,
             cwd=ROOT / "rebuild/OnslaughtRebuild.Godot")
        reports = {}
        for name, script, groups, timeout in CHECKS:
            if args.check and name not in args.check:
                continue
            report_path = output / f"{name}.json"
            extra = [str(ROOT / "tests_shared/fixtures/gold_career_save.bin")] if name == "career-save" else []
            diagnostics = run([engine, "--headless", "--audio-driver", "Dummy", "--path",
                str(ROOT / "rebuild/OnslaughtRebuild.Godot"), "--script",
                f"res://Tests/{script}", "--", str(vectors), str(report_path), *extra], f"{name}.log", timeout)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if any(marker in diagnostics for marker in ("ERROR:", "Unicode parsing error")) \
                    or report.get("schema") != 1 or report.get("failure_count") != 0 \
                    or report.get("completed") != groups or not report.get("counts"):
                raise RuntimeError(f"{name} parity gate did not complete successfully")
            reports[name] = report["counts"]
        print(json.dumps({"result": "passed", "engine": version, "checks": reports,
                          "output": str(output)}, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        if isinstance(error, (subprocess.CalledProcessError, subprocess.TimeoutExpired)):
            print_process_output(error)
        print(f"GDScript parity failed: {error}", file=sys.stderr)
        if output is not None:
            print(f"Owned output: {output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
