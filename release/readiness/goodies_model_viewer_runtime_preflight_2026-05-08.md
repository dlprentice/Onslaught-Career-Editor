# Goodies Model-Viewer Runtime Preflight - 2026-05-08

Status: public-safe preflight evidence, not runtime proof
Date: 2026-05-08
Branch: `wip/sandbox`

## Purpose

This pass adds a machine-checkable guard for the future copied-profile Goodies model-viewer runtime proof. The guard verifies that the runtime proof plan, prerequisite public-safe evidence, runtime helper scripts, CDB observer command files, npm guard scripts, and curated release accounting are present before a live run is attempted.

No game runtime was launched, no debugger was attached, no Ghidra project was opened, no installed game file was read for mutation, and no original `BEA.exe` or save file was changed.

## Commands

```powershell
py -3 tools\goodies_model_viewer_runtime_preflight_test.py
npm run test:goodies-model-viewer-runtime-preflight
```

Result: PASS.

Important output summary:

```text
Ran 3 tests in 0.049s
OK

PASS runtime_proof_plan: release/readiness/goodies_model_viewer_runtime_proof_plan_2026-05-08.md exists.
PASS runtime_safety_boundary: Plan records copied-profile, no-original-mutation, no-runtime-launch, private-evidence, and cleanup boundaries.
PASS required_evidence_files: Found 4 required file(s).
PASS runtime_helper_files: Found 7 required file(s).
PASS runtime_observer_files: Found 2 required file(s).
PASS required_npm_scripts: Found 4 required npm script(s).
PASS release_manifest_entry: Runtime proof plan is explicitly included in the curated manifest.
PASS: Goodies model-viewer runtime proof preflight is ready.
```

## What Changed

- `tools/goodies_model_viewer_runtime_preflight.py` checks the copied-profile runtime proof readiness posture without launching BEA.
- `tools/goodies_model_viewer_runtime_preflight_test.py` covers the complete fixture, missing observer-file failure, and missing copied-profile safety wording failure.
- `package.json` exposes `npm run test:goodies-model-viewer-runtime-preflight`.
- The runtime proof plan now includes machine-checkable wording for installed-game mutation, original `BEA.exe`, and final no-BEA-process cleanup.

## What This Proves

- The future live model-viewer proof has a repeatable preflight before runtime work starts.
- The proof plan remains safety-scoped to copied profiles, copied executables, ignored/private evidence, and final process cleanup.
- The required static/read-back evidence files and runtime helper/observer files are present.
- The runtime proof plan remains explicitly included in the curated release manifest.

## What This Does Not Prove

- Live in-game Goodies model-viewer playback.
- Native WinUI textured/material/animated model rendering.
- Camera, lighting, skeleton, animation, material, or rebuild parity.
- Any runtime behavior beyond preflight readiness.

## Privacy / Release Safety

This evidence is public-safe. It does not include private paths, binaries, save files, screenshots, frame captures, CDB logs, Ghidra project data, or copied runtime artifacts.

## Recommended Next Step

When runtime work resumes, run the preflight plus the existing static/read-back guards, then perform one copied-profile model-viewer proof with private captures/logs under ignored paths and a final process cleanup check.
