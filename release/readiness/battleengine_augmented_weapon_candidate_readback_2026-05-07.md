# BattleEngine Augmented Weapon Candidate Read-Back - 2026-05-07

Status: public-safe static candidate evidence, not runtime proof or rename-map mutation

## Objective

Add a bounded read-back layer for the source `CBattleEngine::AugmentWeapon()` anchor. The goal is to identify and validate the strongest current retail candidate for augmented-weapon activation without claiming final owner/name/signature correctness or live weapon behavior.

## Discovery

The retail executable contains the ASCII sample token `hud_weapon_augmented` at VA `0x00623540`. A read-only Ghidra xref export found one xref from:

- `0x0040def7` inside function `0x0040de40`
- current Ghidra name: `CMonitor__HandleTargetStateChangeAndHudPrompt`
- reference type: `DATA`

A fresh read-only decompile export for `0x0040de40` contains source-aligned augmented-weapon activation tokens:

- max meter constant `0x41200000` (`10.0f`),
- meter field write at `this + 0x2f8`,
- active flag write at `this + 0x2fc`,
- event-time writes at `this + 0x300` and `this + 0x30c`,
- HUD sample lookup and playback helpers.

A follow-up read-only xref export for `0x0040de40` found the current known call into this candidate from:

- `0x00408582` inside function `0x004081c0`
- current Ghidra name: `CMonitor__Process`
- reference type: `UNCONDITIONAL_CALL`

That caller path is useful evidence, but it also reinforces the owner/name caution: `0x0040de40` should remain a candidate note until a deliberate rename/read-back wave proves the final owner, signature, and source-method identity.

The same caller decompile also contains source-aligned context around the candidate call:

- inactive branch checks the active flag at `this + 0x2fc`,
- threshold branch calls `CMonitor__HandleTargetStateChangeAndHudPrompt(param_1)`,
- active branch decrements the meter at `this + 0x2f8`,
- depletion branch clears both meter and active flag fields.

This improves the behavioral bridge for augmented-weapon activation/depletion. It still does not prove whether the retail compiler inlined, split, or reorganized the source `AugmentWeapon()`, `UnaugmentWeapon()`, and per-frame update-loop methods.

## What Changed

Added:

- `tools/battleengine_augmented_weapon_candidate_readback_probe.py`
- `npm run test:battleengine-augmented-weapon-candidate-readback`

Updated:

- `reverse-engineering/binary-analysis/functions/BattleEngine.cpp/_index.md`
- `lore-book/reverse-engineering/binary-analysis/functions/BattleEngine.cpp/_index.md`
- `release/readiness/release_readiness_checklist.md`

Ignored local evidence stays under:

- `subagents/battleengine-weapon-identity-candidates/current/`

## Validation

Commands:

```powershell
py -3 -m py_compile tools\battleengine_augmented_weapon_candidate_readback_probe.py
npm run test:battleengine-augmented-weapon-candidate-readback
```

Result:

- Python compile check passed.
- Candidate read-back probe passed `4/4` checks.
- Follow-up caller-xref guarded probe passed `5/5` checks.
- Follow-up caller-context guarded probe passed `6/6` checks.

## What This Proves

- The selected source `AugmentWeapon()` body anchors are present.
- Existing source-anchor evidence still classifies augmented weapon behavior as source-only pending retail-binary identity.
- The retail augmented HUD sample string currently xrefs to one candidate function at `0x0040de40`.
- The current candidate decompile contains max-meter, active-flag, event-time, and HUD sample lookup/playback tokens.
- The current known caller into the candidate is `CMonitor__Process`, so owner/name inference remains intentionally unresolved.
- The caller context contains source-aligned threshold-call, meter-decay, and meter/active-reset tokens.

## Not Claimed

- This does not rename `0x0040de40` or apply a Ghidra rename map.
- This does not prove final owner/name/signature correctness for `0x0040de40`.
- This does not prove exact full control-flow identity for every source `AugmentWeapon()` statement.
- This does not prove whether retail code inlined or reorganized source `AugmentWeapon()`, `UnaugmentWeapon()`, and update-loop methods.
- This does not prove shield-damage meter gain or weapon-fired stealth reset identity.
- This does not run `BEA.exe`.
- This does not prove runtime augmented-weapon behavior, HUD audio playback, projectile behavior, or stealth behavior.
- This does not make the repository rebuildable from scratch.

## Privacy

The public report contains addresses, current public Ghidra names, token families, command results, and proof boundaries only. It does not include source excerpts, binaries, private absolute paths, runtime captures, screenshots, frame data, Ghidra project files, raw decompile output, or mutation logs.
