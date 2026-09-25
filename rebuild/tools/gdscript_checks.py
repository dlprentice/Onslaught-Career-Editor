#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run the rebuild's GDScript checks against their private golden references.

The goldens are the outputs of the retired C# reference scenes, parity oracle and
--write-reference runs, captured once at the commit named in their manifest and
kept in the canonical lab (several are retail-derived). This tool verifies every
golden against the pinned manifest, copies them into a fresh owned directory
below this checkout's local-data (the checks admit only owned inputs), and runs
each check headless on the pinned standard engine, or on the .NET engine where a
check needs the simulation bridge. It writes nothing outside that directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from godot_host import ENGINE_VERSION, output_directory, print_process_output, run_process  # noqa: E402

PROJECT = ROOT / "rebuild/OnslaughtRebuild.Godot"
STANDARD_VERSION = ENGINE_VERSION.replace(".mono.", ".")
GOLDENS_NAME = "rebuild-goldens-20260925"
GOLDENS_MANIFEST_SHA256 = "fef918e0c5ab9d469cce91b94f4b3bcade7ac34f73ee021109d3db6ebb92cf1e"
GOLD_CAREER = ROOT / "tests_shared/fixtures/gold_career_save.bin"

# Parity groups: (name, script under res://Tests, expected completed groups, timeout).
PARITY = (
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
# Fixture consumers: (name, script, golden fixture) run as `-- <fixture> <report>`.
FIXTURES = (
    ("sun", "Scenes/World/sun_scene_checks.gd", "sun.fixture"),
    ("water", "Scenes/World/water_scene_checks.gd", "water.fixture"),
    ("height-field", "Scenes/World/height_field_checks.gd", "height-field.fixture"),
    ("terrain-appearance", "Scenes/World/terrain_appearance_checks.gd", "terrain-appearance.fixture"),
    ("terrain-compositor", "Scenes/World/terrain_compositor_checks.gd", "terrain-compositor.fixture"),
    ("aquila", "Scenes/Aquila/aquila_scene_checks.gd", "aquila.fixture"),
    ("fixed-function-material", "Scenes/Shared/fixed_function_material_checks.gd", "fixed-function-material.fixture"),
    ("click-law", "Scenes/Frontend/Tests/click_law_checks.gd", "click-law.fixture"),
    ("main-menu-law", "Scenes/Frontend/Tests/main_menu_law_checks.gd", "main-menu-law.fixture"),
    ("audio-reference", "Scenes/Audio/Tests/audio_scene_checks.gd", "audio-reference.json"),
    ("hud-catalog-reference", "Scenes/Hud/Tests/hud_catalog_checks.gd", "hud-catalog-reference.json"),
)
# Standalone checks that take one fresh owned directory.
OWNED_DIRECTORY = (
    "Scenes/Frontend/Tests/briefing_scene_checks.gd", "Scenes/Frontend/Tests/career_name_scene_checks.gd",
    "Scenes/Frontend/Tests/configuration_scene_checks.gd", "Scenes/Frontend/Tests/level_select_scene_checks.gd",
    "Scenes/Frontend/Tests/main_menu_scene_checks.gd", "Scenes/Frontend/Tests/mouse_cursor_scene_checks.gd",
    "Scenes/Frontend/Tests/quit_confirm_scene_checks.gd", "Scenes/Frontend/Tests/click_scene_checks.gd",
    "Scenes/Frontend/Tests/frontend_asset_paths_checks.gd",
)
# Standalone checks with fixed user arguments.
STANDALONE = (
    ("Scenes/Frontend/Tests/debriefing_scene_checks.gd", []), ("Scenes/Frontend/Tests/options_scene_checks.gd", []),
    ("Scenes/Hud/Tests/hud_scene_checks.gd", []), ("Scenes/Pause/Tests/pause_scene_checks.gd", []),
    ("Scenes/Frontend/Tests/frontend_scene_checks.gd", ["--skipfmv"]),
    ("Scenes/Frontend/Tests/loading_scene_checks.gd", []), ("Scenes/World/entity_scene_checks.gd", []),
    ("Scenes/Shared/retail_float32_checks.gd", []), ("Tests/frontend_localization_checks.gd", []),
    ("Tests/frontend_flow_checks.gd", ["--skipfmv"]),
)
GROUPS = ("parity", "fixtures", "laws", "startup", "scenes", "host", "world")
# Engine diagnostics a check provokes on purpose: pause_scene_checks feeds a
# corrupt deflate stream to the AYA reader, and Godot's gzip stream logs it.
EXPECTED_ENGINE_ERRORS = {"pause_scene_checks": ("core/io/stream_peer_gzip.cpp",)}


def canonical_lab() -> Path:
    configured = os.environ.get("BEA_LOCAL_LAB")
    if configured:
        return Path(configured).expanduser().resolve()
    git_file = ROOT / ".git"
    if git_file.is_file():
        # A linked worktree: the canonical lab belongs to the main checkout.
        common = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"],
                                capture_output=True, text=True, check=True).stdout.strip()
        return (Path(common).resolve().parent / "local-lab").resolve()
    return (ROOT / "local-lab").resolve()


def verify_goldens(goldens: Path) -> dict:
    manifest_path = goldens / "manifest.json"
    raw = manifest_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != GOLDENS_MANIFEST_SHA256:
        raise RuntimeError(f"golden manifest is missing or changed: {manifest_path}")
    manifest = json.loads(raw)
    for name, stamp in manifest["files"].items():
        path = goldens / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"golden is missing: {path}")
        data = path.read_bytes()
        if len(data) != stamp["bytes"] or hashlib.sha256(data).hexdigest() != stamp["sha256"]:
            raise RuntimeError(f"golden changed: {path}")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--goldens", type=Path, help=f"golden directory (default: canonical lab {GOLDENS_NAME})")
    parser.add_argument("--output-root", type=Path, help="fresh path below this checkout's local-data")
    parser.add_argument("--group", action="append", choices=GROUPS,
                        help="run only this group; repeatable (world needs a current build:rebuild-godot import)")
    parser.add_argument("--standard-engine", default="godot48")
    parser.add_argument("--dotnet-engine", default="godot48-mono")
    args = parser.parse_args(argv)
    if not sys.platform.startswith("linux"):
        parser.error("this headless gate supports Linux")
    groups = set(args.group or GROUPS)
    output = None
    try:
        standard = shutil.which(args.standard_engine)
        dotnet_engine = shutil.which(args.dotnet_engine)
        if standard is None or ("world" in groups and dotnet_engine is None):
            raise RuntimeError("the pinned standard and .NET Godot 4.8 dev6 engines are required")
        goldens = (args.goldens or canonical_lab() / GOLDENS_NAME).expanduser().resolve()
        manifest = verify_goldens(goldens)
        output = output_directory(ROOT, args.output_root, "test-runs", "gdscript-checks")
        inputs = output / "goldens"
        shutil.copytree(goldens, inputs)
        env = {k: v for k, v in os.environ.items() if k not in ("DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY")}
        for name in ("TMPDIR", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME"):
            path = output / "profile" / name.lower()
            path.mkdir(parents=True, mode=0o700)
            env[name] = str(path)
        env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
        version = run_process([standard, "--headless", "--version"], cwd=ROOT, env=env, timeout=30,
                              capture=True).stdout.strip()
        if version != STANDARD_VERSION:
            raise RuntimeError(f"expected Godot {STANDARD_VERSION}; found {version!r}")
        results: dict[str, dict] = {}

        def run(name: str, engine: str, target: list[str], user: list[str], timeout: float) -> str:
            command = [engine, "--headless", "--audio-driver", "Dummy", "--path", str(PROJECT), *target, "--", *user]
            (output / "logs").mkdir(exist_ok=True)
            log = output / "logs" / f"{name}.log"
            try:
                done = run_process(command, cwd=PROJECT, env=env, timeout=timeout, capture=True)
                text, code = (done.stdout or "") + (done.stderr or ""), 0
            except subprocess.CalledProcessError as error:
                text, code = (error.stdout or "") + (error.stderr or ""), error.returncode
            except subprocess.TimeoutExpired as error:
                text, code = str(error.stdout or "") + str(error.stderr or ""), "timeout"
            log.write_text(text, encoding="utf-8")
            lines = text.splitlines()
            allowed = EXPECTED_ENGINE_ERRORS.get(name, ())
            errors = [line for index, line in enumerate(lines)
                      if (line.startswith(("ERROR:", "SCRIPT ERROR:")) or "Unicode parsing error" in line)
                      and not any(site in " ".join(lines[index:index + 2]) for site in allowed)]
            results[name] = {"exit": code, "engine_errors": len(errors), "log": str(log)}
            print(f"[{'PASS' if code == 0 and not errors else 'FAIL'}] {name}", flush=True)
            return text

        def report_ok(path: Path, groups_expected: list[str] | None = None) -> bool:
            if not path.is_file():
                return False
            report = json.loads(path.read_text(encoding="utf-8"))
            ok = report.get("failure_count", 0) == 0
            if groups_expected is not None:
                ok = ok and report.get("schema") == 1 and report.get("completed") == groups_expected and bool(report.get("counts"))
            return ok

        reports = output / "reports"
        reports.mkdir()
        if "parity" in groups:
            vectors = inputs / "parity-vectors.json"
            for name, script, expected, timeout in PARITY:
                report = reports / f"parity-{name}.json"
                extra = [str(GOLD_CAREER)] if name == "career-save" else []
                run(f"parity-{name}", standard, ["--script", f"res://Tests/{script}"],
                    [str(vectors), str(report), *extra], timeout)
                results[f"parity-{name}"]["report_ok"] = report_ok(report, expected)
        if "fixtures" in groups:
            for name, script, fixture in FIXTURES:
                report = reports / f"{name}.json"
                run(name, standard, ["--script", "res://" + script], [str(inputs / fixture), str(report)], 600)
        if "laws" in groups:
            run("cosf", standard, ["--script", "res://Scenes/Shared/Tests/retail_cosf_checks.gd"],
                [str(inputs / "cosf.fixture"), str(inputs / "click-law.fixture"), str(reports / "cosf.json")], 300)
        if "startup" in groups:
            media = canonical_lab() / "startup-media"
            run("startup", standard, ["--script", "res://Scenes/Frontend/Tests/startup_scene_checks.gd"],
                [f"--startup-media={media}", f"--startup-verified-fixture={inputs / 'startup-verified.fixture'}"], 600)
        if "scenes" in groups:
            for script in OWNED_DIRECTORY:
                owned = output / "owned" / Path(script).stem
                owned.mkdir(parents=True)
                run(Path(script).stem, standard, ["--script", "res://" + script], [str(owned)], 600)
            for script, user in STANDALONE:
                run(Path(script).stem, standard, ["--script", "res://" + script], user, 600)
        if "host" in groups:
            report = reports / "host.json"
            run("host", standard, ["--script", "res://Tests/host_checks.gd"], [str(GOLD_CAREER), str(report)], 120)
            results["host"]["report_ok"] = report_ok(report)
        if "world" in groups:
            text = run("world", dotnet_engine, ["--script", "res://Scenes/World/Tests/world_scene_checks.gd"], [], 900)
            results["world"]["report_ok"] = "WORLD_SCENE_CHECKS:" in text and "passed" in text
        failed = sorted(name for name, result in results.items()
                        if result["exit"] != 0 or result["engine_errors"] or result.get("report_ok") is False)
        summary = {"result": "failed" if failed else "passed", "engine": version,
                   "goldens": manifest["generatedFrom"], "checks": len(results), "failed": failed,
                   "output": str(output)}
        (output / "summary.json").write_text(json.dumps({"summary": summary, "results": results}, indent=2) + "\n",
                                             encoding="utf-8")
        print(json.dumps(summary, indent=2))
        return 1 if failed else 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        if isinstance(error, (subprocess.CalledProcessError, subprocess.TimeoutExpired)):
            print_process_output(error)
        print(f"GDScript checks failed: {error}", file=sys.stderr)
        if output is not None:
            print(f"Owned output: {output}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
