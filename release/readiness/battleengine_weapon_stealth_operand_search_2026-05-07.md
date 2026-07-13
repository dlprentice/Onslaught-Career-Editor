# BattleEngine Weapon-Fired Stealth Operand Search - 2026-05-07

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe read-only operand-token triage, not retail identity proof

> **Current name correction (2026-07-12):** references below to
> `CMonitor__Process` at `0x004081c0` now mean `CBattleEngine__Move`. This owner
> correction does not promote the weapon-fire/stealth behavior to runtime proof.

## Objective

Narrow the remaining `weapon_fire_breaks_stealth` source-only anchor without mutating the installed game, the original `BEA.exe`, or the Ghidra project.

This pass asks a smaller static question: do current Ghidra instruction operands expose an obvious weapon/fire/projectile function touching the currently suspected stealth-adjacent object fields?

## Inputs

- Stuart source anchor: `references/Onslaught/BattleEngine.cpp`
- Read-only Ghidra script: `tools/ExportInstructionsByOperandToken.java`
- Probe: `tools/battleengine_weapon_stealth_operand_search_probe.py`
- Ignored operand export: `subagents/battleengine-weapon-fired-stealth-candidate/current/operand-search/stealth-field-instructions.tsv`

The operand export searched for:

- `0x4ac`
- `0x5d4`
- `0x5d8`
- `0x5dc`

These offsets came from prior cloak/stealth candidate work. They cover the current best static latch and stealth-adjacent interpolation fields, but they are not final source-field identities.

## Commands

```powershell
wsl bash -lc "cd [maintainer-private-checkout] && tools/run_ghidra_headless_postscript.sh ExportInstructionsByOperandToken.java subagents/battleengine-weapon-fired-stealth-candidate/current/operand-search/stealth_tokens.txt subagents/battleengine-weapon-fired-stealth-candidate/current/operand-search/stealth-field-instructions.tsv"
py -3 -m py_compile tools\battleengine_weapon_stealth_operand_search_probe.py
npm run test:battleengine-weapon-stealth-operand-search
```

## Result

```text
BattleEngine weapon-fired stealth operand search
Status: pass
Rows total: 377
Object-offset rows: 64
Weapon-like object-offset rows: 0
```

The headless run scanned `544726` instructions and wrote `377` matching operand-token rows. The known GhydraMCP manifest warnings appeared again; this was a read-only export and raw output stayed ignored under `subagents/`.

## What This Proves

- The source `CBattleEngine::WeaponFired(...)` anchor still clears stealth after either jet or walker weapon fire reports success.
- Current Ghidra operand-token export can find stealth-adjacent object-offset references for the suspected latch/interpolation fields.
- The expected object-offset references are in init/process/latch context, including `CBattleEngine__Init`, `CMonitor__Process`, and `CGeneralVolume__Update4ACLatchFromHeightAndA0`.
- The current object-offset scan found `0` weapon/fire/projectile function rows for the stealth-adjacent offsets.

## What This Does Not Prove

- This does not prove absence of a retail weapon-fired stealth reset implementation.
- This does not prove exact Steam retail function body identity for `CBattleEngine::WeaponFired`.
- This does not prove whether Steam retail removed, inlined, reorganized, or changed the source behavior.
- This does not prove runtime stealth behavior after firing a weapon.
- This does not mutate Ghidra, apply a rename map, patch `BEA.exe`, or run the game.
- This does not make the repository rebuildable from scratch.

## Outcome

`weapon_fire_breaks_stealth` remains source-only in aggregate source-to-binary gap accounting. The useful new fact is narrower: a full instruction-operand scan over the best current stealth-adjacent fields did not reveal an obvious weapon/fire/projectile function candidate.

Future work should either use a different static signal, such as xrefs from weapon part fire paths and weapon object callbacks, or move to a copied-profile runtime probe that observes whether firing while cloaked actually clears stealth in the Steam retail build.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses already present in repo evidence, command summaries, and counts only. It does not include binaries, private absolute paths, source excerpts, runtime captures, screenshots, frame data, copied executables, or Ghidra mutation logs.
