# Validation

Status: active — the gate-selection table
Last updated: 2026-11-11 (the frozen rebuild copy was cut; the rows for it and for the moved parser were rewritten)
Summary: choosing the smallest evidence that proves the contract you changed.
[`package.json`](package.json) owns the commands.

Validation is proportional to the contract changed. The commands below are options, not a required sequence.

Documentation and safety gates use the [public prerequisites](README.MD#build-and-run), including initialized
pinned source-reference submodules for full scans; they need no retail installation, private lab or Godot.
Authored Python suites have [separate package requirements](tools/README.md#python-prerequisites).

Linux is the active development and native Godot host. Companion build, runtime test, run and export
commands use the public pinned toolchain setup in the
[Companion build guide](companion/OnslaughtToolkit.Godot/README.md#build-test-capture-run-and-export). No private installer is required.
Automated captures additionally require an optional machine-specific offscreen wrapper; it is not part of public setup.
`npm test` runs the companion's
C# contract suite (career codec, media inventory, protected adapter, publication races
and the code-built interface) and its launcher tests without opening a window. `npm run build` and
`npm run dev` build/run the Godot .NET companion. The latter opens a window.
`npm run test:companion-tools` uses fake tools on Linux and needs no shared installation.
The rebuild application is gated in [onslaught-godot](https://github.com/dlprentice/onslaught-godot); retained Python
support-code checks here do not establish rebuild parity. Source and headless tests
alone do not establish native input, audio, focus or full tutorial behavior.

Dated receipts of earlier checks are in [`VALIDATION-HISTORY.md`](VALIDATION-HISTORY.md). They record what ran
on their dates and are not instructions. A link ending in `VALIDATION.md#<section>` in the frozen copies refers to the
section of the same name in `VALIDATION-HISTORY.md`.

| Change | Focused evidence |
| --- | --- |
| Documentation or deletion only | `git diff --check`, `npm run test:docs` (link check with its self-test, then headers), and, when a generator's output changed, that generator's `--check` (the catalogue row below gives the pattern). The full link scan needs initialized pinned public source references; no retail data is needed |
| A new or edited tracked `.md` header | `npm run test:doc-headers`, which is also inside `test:docs`. The contract is [`DOCUMENTATION.md`](DOCUMENTATION.md); the backlog of pre-standard documents is `tools/doc_header_backlog.txt` and may only shrink |
| Companion (C# built in code) and its file safety | With the public pinned toolchain (`python tools/companion_toolchain.py setup`), `npm run test:companion-godot` runs `companion/OnslaughtToolkit.Godot/Tests/CompanionTestRunner.cs` on owned copies of the tracked real-save fixture: codec contracts, independent byte diffs, protected round trips, changed/conflicting sources and links, publication races and the code-built interface's real controls. `test:companion-tools` separately checks pins, the code-only policy, staging and export boundaries with fake tools |
| Public payload/provenance boundary | `npm run test:safety` |
| The Godot rebuild application | Developed, built and gated in [onslaught-godot](https://github.com/dlprentice/onslaught-godot). Local `rebuild/` is a pointer page: the frozen copy that stood there was removed on 2026-11-11 (tag `archive/20261111-rebuild-frozen-copy`) and its application is not built or gated here |
| The CMSH parser and its data under `tools/` | `test:tools` runs `cmsh_static_preview_tests.py`, `check_region_overlap_tests.py`, `score_frontend_capture_tests.py` and `check_region_overlap.py`; many Toolkit format tools import the parser. `particle_set_walk_tests.py` and `physics_values_decode_tests.py` compare their tables with the C# reader copies in `tools/godot_reader_fixtures/` and fail, not skip, when a copy is missing. These checks do not run the rebuild application or establish its parity |
| Godot toolchain or native behavior | `test:godot-host` checks launcher routing/process cleanup with fake tools. With the public pinned toolchain, `build:companion-godot` refuses GDScript, saved resources and multi-node scenes, then builds the C# companion; `export:companion-godot` produces normal Godot .NET Linux/Windows exports after `python tools/companion_toolchain.py setup --with-templates`. Builds are headless |
| Catalogue or editor Python reference | The affected authored suite, such as `python tools/content_catalog_tests.py`, `python tools/world_resources_encode_tests.py`, `python tools/level_editor_vectors_tests.py` or `python tools/msl_compile_tests.py`; check changed generated C# vectors/tables with the owning generator's `--check`. These need no retail install; [Python package requirements](tools/README.md#python-prerequisites) and schema skips still apply. Retail catalogue, world and compiler comparisons are separate [tools](tools/README.md#editor-references-and-generators); C# changes also owe the Companion runtime gate |
| Tools | The affected `tools/<name>_tests.py`; `npm run test:tools` runs every registered suite (`worldheaders_decode --self-test` needs the retail `worldheaders.dat`). Its self-test fails for any `*_tests.py` that is neither registered nor excluded with a reason in `tools/run_tool_tests.py`, so a new test file cannot fall outside it. Among the suites it runs are `dds_census`, `mission_script_inspect`, `worldheaders_decode`, the skinning and matrix contracts, `battle_engine_config_decode`, `gltf_pose_check`, `goodie_resource_walk`, `xap_bank_walk`, `safe_generated_output` and the extractor source audit. A suite that cannot run (a Windows-only one on another host, or the audit when the `AYAResourceExtractor` or `Onslaught` submodule is not initialised: `git submodule update --init --recursive`) is a named SKIP in the summary, never a pass. A suite that runs is reported as passed even when some of its tests skipped themselves (tests that need the retail data or a specimen skip one by one); read each suite's own skip lines before citing the summary as evidence for a retail claim. The companion and Godot host suites run under their own npm scripts. |
| Game documentation claim | New findings belong in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation). Cite the decompilation's function, capture, byte comparison or source line; never paste decompiler output. The local `reverse-engineering/` notes are frozen references |
