# BattleEngine Projectile Helper Stealth Scan - 2026-05-08

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe read-only decompile triage, not retail identity proof

## Objective

Narrow the remaining `weapon_fire_breaks_stealth` source-only anchor without mutating the installed game, the original `BEA.exe`, or the Ghidra project.

This pass asks a smaller static question: does the already named retail helper `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` contain source-style stealth reset writes, or is that helper only target/projectile context for the broader weapon-fire investigation?

## Inputs

- Stuart source anchor: `references/Onslaught/BattleEngine.cpp`
- Existing ignored read-only decompile export: `subagents/battleengine-helper-ghidra-readback/current/decompile/00406560_CBattleEngine__UpdateAutoTargetSetAndFireProjectiles.c`
- Existing ignored decompile index: `subagents/battleengine-helper-ghidra-readback/current/decompile/index.tsv`
- Probe: `tools/battleengine_projectile_helper_stealth_scan_probe.py`
- Probe test: `tools/battleengine_projectile_helper_stealth_scan_probe_test.py`

The probe checks the current helper decompile for target-entry resolution, target filtering, tracked-set removal, forward-target selection, projectile emission, the known `0.01` stealth-style targeting context, and source-style writes to the current stealth-adjacent offsets `0x4ac`, `0x5d4`, `0x5d8`, and `0x5dc`.

## Commands

```powershell
py -3 tools\battleengine_projectile_helper_stealth_scan_probe_test.py
py -3 tools\battleengine_projectile_helper_stealth_scan_probe.py --check
py -3 -m py_compile tools\battleengine_projectile_helper_stealth_scan_probe.py tools\battleengine_projectile_helper_stealth_scan_probe_test.py
cmd.exe /c npm run test:battleengine-projectile-helper-stealth-scan
```

## Result

```text
BattleEngine projectile helper stealth scan probe
Status: PASS
Classification: projectile-targeting-helper-no-stealth-reset-observed
Stealth write tokens observed: 0
```

The ignored JSON report is written to `subagents/battleengine-projectile-helper-stealth-scan/current/projectile-helper-stealth-scan.json`.

## What This Proves

- The source `CBattleEngine::WeaponFired(...)` anchor still clears stealth after either jet or walker weapon fire reports success.
- The current `0x00406560` retail decompile still contains target-entry resolution, target filtering, tracked-set removal, forward-target selection, and `CBattleEngine__AddProjectile` call-chain evidence.
- The current `0x00406560` retail decompile still contains the known `0.01` stealth-style target-range context token.
- No source-style writes to the currently tracked stealth-adjacent offsets `0x4ac`, `0x5d4`, `0x5d8`, or `0x5dc` were observed inside the current `0x00406560` decompile.

## What This Does Not Prove

- This does not identify the exact retail `CBattleEngine::WeaponFired` implementation.
- This does not prove retail weapon fire never clears stealth.
- The stealth reset may still live in a wrapper, callback, inlined part method, runtime-only path, or a field identity not covered by the current offset set.
- This does not prove runtime cloak activation, target-lock behavior, or weapon-fire decloak behavior.
- This does not mutate Ghidra, apply a rename map, patch `BEA.exe`, or run the game.
- This does not make the repository rebuildable from scratch.

## Outcome

`weapon_fire_breaks_stealth` remains source-only in aggregate source-to-binary gap accounting. The useful new fact is narrower: the current strongest target/projectile helper is not the source-style stealth reset body, even though it remains important targeting/projectile context for the broader weapon-fire investigation.

Future work should continue from either weapon object callback identity or copied-profile runtime proof with a verified cloak-active baseline.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses already present in repo evidence, function names, token labels, command summaries, and counts only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, or Ghidra mutation logs.
