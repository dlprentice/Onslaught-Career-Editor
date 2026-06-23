# Goodies Packed Script Probe - 2026-05-07

Status: public-safe static RE probe, not runtime proof

## Objective

Narrow the Goodies 71-73 reachability question by checking whether the installed loose mission scripts or top-level packed AYA resource archives contain literal `GetGoodieState(...)` / `SetGoodieState(...)` calls for the script indices that would map to save Goodies 71-73.

Goodies 71-73 correspond to 1-based script indices 72-74.

## Inputs

- Installed loose mission-script corpus under the local Battle Engine Aquila install.
- Installed top-level packed resource archives under the local Battle Engine Aquila install.
- `tools/goodies_script_corpus_probe.py --scan-packed-resources --require-root --check`.

Raw installed paths and generated JSON remain private/ignored under `subagents/`.

## Result

The probe passed.

```text
mission-script Goodie calls: files=733 calls=32 indices=51,53,68,69,70,71 target72to74=0
packed resource Goodie calls: archives=301 inflateErrors=0 tokenFiles=0 calls=0 target72to74=0
```

The generated report uses sanitized root labels (`<script-root>` and `<resource-root>`) and contains no absolute private install path.

## What This Proves

- The checked installed loose mission-script corpus has no literal Goodie state API call for script indices 72-74.
- The checked installed top-level packed AYA resource archives inflate cleanly through the current archive inflater.
- The checked installed top-level packed AYA resource archives have no literal `GetGoodieState(...)` or `SetGoodieState(...)` calls.
- The checked installed top-level packed AYA resource archives have no broad text-token Goodie hits in inflated payloads.

## What This Narrows

This closes the narrow packed-resource text-divergence concern for literal Goodie state API calls in the checked installed corpus.

Goodies 71-73 remain best described as:

```text
real shipped texture-only rows with source/static unlock and instruction support, exported previews, no known normal wall-coordinate route, no literal installed loose-script or packed-resource Goodie state calls targeting script indices 72-74, and still-unproven hidden/non-grid runtime reachability.
```

## Not Claimed

- This is not runtime proof.
- This does not launch `BEA.exe`.
- This does not prove Goodies 71-73 are unreachable.
- This does not inspect compiled, bytecode, indirect, runtime-generated, debugger-only, or non-MSL binary paths.
- This does not replace copied-profile runtime proof.
- This does not authorize mutation of the installed game, original executable, or original saves.

## Next Step

The remaining Goodies 71-73 question is now hidden/non-grid runtime reachability or a binary-only/developer direct-selection path. Use the copied-profile-only plan in `release/readiness/goodies_71_73_hidden_runtime_proof_plan_2026-05-07.md` when runtime proof is explicitly started.
