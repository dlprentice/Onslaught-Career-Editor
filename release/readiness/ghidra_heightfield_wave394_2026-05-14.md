# Heightfield Ghidra Correction - 2026-05-14

Status: public-safe evidence

Source branch: `wip/sandbox`

Recorded at: 2026-05-14

## Scope

This wave records a serialized saved-Ghidra metadata correction for five terrain/heightfield and static-shadow sampling helpers:

- `0x0047e8e0` `CHeightField__InitColorGradient`
- `0x0047ea20` `CWorld__GetHeightSamplePacked16`
- `0x0047eb00` `CHeightField__SampleInterpolatedHeight`
- `0x0047eb80` `CStaticShadows__SampleShadowHeightBilinear`
- `0x0047ec60` `CMonitor__SampleHeightfieldNormalAtXY`

It does not mutate `BEA.exe`, launch the game, patch the installed Steam copy, include raw decompile excerpts, or prove runtime gameplay/terrain behavior.

## Private Evidence Policy

Ignored local evidence remains under `subagents/ghidra-static-reaudit/heightfield-wave394/current/`. This report does not include decompiled source excerpts, private absolute paths, screenshots, frame data, copied executables, copied saves, raw private JSON, or Ghidra project files.

## Functions Corrected

| Address | Current saved name | Result | Selected evidence |
| --- | --- | --- | --- |
| `0x0047e8e0` | `CHeightField__InitColorGradient` | PASS | Saved signature hardened to `void __fastcall ... (void * this)`. The body derives heightfield size/mask fields from `+0x1038/+0x103c`, builds the 64-entry color-gradient table rooted at `+0x10d0` from color fields `+0x107c/+0x108c`, and copies fog color triplets from `+0x13c4` to `+0x13d0`. |
| `0x0047ea20` | `CWorld__GetHeightSamplePacked16` | PASS | Saved signature hardened with named packed X/Z parameters. The body samples 16-bit height data via `+0x1028`, uses packed coordinate masks, and includes edge branches around `0x200` and `0xa1ffe`. The older `CWorld` owner label is preserved as provisional caller-ownership evidence, while the body evidence is heightfield-buffer evidence. |
| `0x0047eb00` | `CHeightField__SampleInterpolatedHeight` | PASS | Saved signature hardened with named packed X/Z parameters. The body bilinearly interpolates four signed 16-bit height samples from the `+0x1028` buffer using the 9x9 tile stride. |
| `0x0047eb80` | `CStaticShadows__SampleShadowHeightBilinear` | PASS | Saved calling convention corrected from the older `__thiscall` form to `__fastcall`; read-back now uses the `world_pos` parameter instead of the old `in_EDX` decompiler artifact. The body offsets world X/Z by global terrain-origin constants, samples/interpolates signed height data, scales by `+0x102c`, and returns a flat fallback outside range. |
| `0x0047ec60` | `CMonitor__SampleHeightfieldNormalAtXY` | PASS | Saved signature hardened with named receiver/output/world-position parameters. The body writes an output normal, uses rounded world X/Z samples with `+0x1028` and `+0x102c`, and falls back to upward normal `(0,0,1)` outside the sampled range. The saved `CMonitor` owner remains bounded/provisional. |

## Commands Run

```powershell
py -3 tools\ghidra_heightfield_wave394_probe_test.py
py -3 -m py_compile tools\ghidra_heightfield_wave394_probe.py tools\ghidra_heightfield_wave394_probe_test.py
cmd.exe /c npm run test:ghidra-heightfield-wave394
cmd.exe /c npm run test:ghidra-static-reaudit-queue
py -3 tools\release_curated_manifest.py
py -3 tools\release_curated_manifest.py --check
py -3 tools\release_profile_snapshot.py
py -3 tools\release_profile_snapshot.py --check
cmd.exe /c npm run test:public-allowlist
cmd.exe /c npm run test:md-links
cmd.exe /c npm run test:doc-commands
py -3 tools\docsync_check.py
cmd.exe /c npm run test:repo-hygiene
```

Result: PASS.

Headless dry/apply results:

- Dry run: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply: `updated=5 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply log reported `REPORT: Save succeeded`.

Read-back results:

- `5` metadata rows.
- `5` decompile exports.
- `142` xref rows.
- `5` tag rows.
- `605` instruction rows.

The refreshed queue reports `6027` functions, `1494` commented functions, `4533` commentless functions, `1915` undefined signatures, and `1880` `param_N` signatures. Current confirmation proxies are telemetry only: comment-backed `1494/6027 = 24.79%`; strict clean-signature `1432/6027 = 23.76%`.

Actual live Ghidra project backup verification passed after the saved mutation: copied `BEA.gpr` and `BEA.rep` to `G:\GhidraBackups\BEA_20260514_002613_post_wave394_heightfield_verified` and verified `19` files, `154667911` bytes, and `HashDiffCount=0`.

Release/docs closeout passed: curated manifest selected `2144` files, release profile counts were `R0=2206 R2=0 R3=2 R4=18188`, public allowlist checked `2144` rows, markdown links passed, doc-commands checked `3140` documented package-script references, docsync passed, and repo hygiene passed.

## What Is Proven

- The saved Ghidra project now records hardened signatures, comments, and tags for all five Wave394 targets.
- The saved Ghidra project now records `0x0047eb80` as `double __fastcall CStaticShadows__SampleShadowHeightBilinear(void * this, void * world_pos)`, correcting the prior saved `__thiscall` signature.
- The focused read-back evidence ties the five targets to terrain height buffers, packed height sampling, bilinear shadow height sampling, and terrain-normal sampling.
- The focused proof script validates saved metadata, tags, selected decompile tokens, xref context, instruction tokens, dry/apply summaries, and public overclaim boundaries.

## What Is Not Proven

- This does not prove runtime terrain behavior.
- This does not prove runtime shadow behavior.
- This does not prove exact Stuart-source identity for every target.
- This does not recover concrete class layouts, local variable names, local types, or structure definitions.
- This does not prove complete HeightField, StaticShadows, World, or Monitor coverage.
- This does not mutate or patch `BEA.exe`.
- This does not prove rebuild parity.

## Release Posture

GREEN for public-safe saved-Ghidra metadata correction evidence. It should be treated as static retail-binary evidence and as a correction to stale docs/probes, not as runtime terrain proof or source-final gameplay implementation.
