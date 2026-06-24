# Goodies Frontend Selection Static Review - 2026-05-07

Status: public-safe static RE review, not runtime proof

## Objective

Record the current static front-end selection evidence for Goodies 71-73 before any copied-profile runtime proof.

This review answers one narrow question:

```text
Does the recovered retail frontend selection path expose a normal coordinate route to Goodies 71-73?
```

## Inputs

- Existing ignored Ghidra decompile exports under `subagents/goodies-71-73-ghidra-readback/current/`.
- `tools/goodies_ghidra_readback_probe.py --check`.
- Existing source/catalog evidence summarized in the Goodies quick reference.

Raw decompile exports and generated JSON remain ignored/private under `subagents/`.

## Static Review Result

`tools/goodies_ghidra_readback_probe.py --check` passed:

- Functions: 6/6 passing.
- Instruction contexts: 8/8 passing.
- Unlock read-back: PASS.
- Field map: PASS.
- Selection target constants: PASS, hits=0.

## What This Proves

- `get_goodie_number` returns the normal visible coordinate ranges for:
  - 66-70,
  - 74-77,
  - 201-232,
  - 78-200.
- The normal wall coordinate mapper leaves 71-73 without a known visible coordinate.
- `CFEPGoodies__ButtonPressed`, `CFEPGoodies__Process`, and `CFEPGoodies__LoadingGoodyPoll` still flow selected rows through `get_goodie_number(mCX, mCY)`.
- Those selected-path handlers currently contain no direct `0x47`, `0x48`, or `0x49` target constants.
- `CFEPGoodies__StartLoadingGoody` still has an image/content bucket that would handle 71-73 if a hidden path selected those ids.
- `CCareer__UpdateGoodieStates` read-back includes Goodie 71-73 pointer constants, matching source unlock logic.

## Current Interpretation

Goodies 71-73 are still best classified as real shipped texture-only Goodies with static unlock/type support and no known normal wall-coordinate selection path.

This narrows the next runtime question:

```text
If copied-save state forces 71-73 to visible states, does runtime wall navigation, cheat/display override behavior, or another hidden/developer path expose them?
```

## Not Claimed

- This is not runtime proof.
- This does not launch BEA.
- This does not prove Goodies 71-73 are unreachable.
- This does not rule out packed/runtime script divergence.
- This does not rule out hidden/developer/direct-selection paths outside the currently recovered frontend coordinate route.

## Next Step

Use the copied-profile proof plan in `release/readiness/goodies_71_73_hidden_runtime_proof_plan_2026-05-07.md` when ready for runtime work. Use copied profiles, a copied executable, ignored/private captures, the targeted copied-save setup helper, and a final process-stop check.
