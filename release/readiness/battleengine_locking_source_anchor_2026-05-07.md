# BattleEngine Locking Source Anchor - 2026-05-07

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe source/static bridge evidence; not runtime behavior proof

## Current Disposition

The reviewed 2026-07-13 correction establishes retail-static
`0x00406560 CBattleEngine__HandleLocks`. The helpers at `0x00406da0` and
`0x00406fc0` retain their address-bound saved names and roles;
`CBattleEngine::GetClosestLockableUnit` and `CBattleEngine::StartLock` remain
pinned-source hypotheses, not accepted retail names. The current bounded
contract is
[`battleengine-target-acquisition-static-contract-v1`](../../reverse-engineering/game-mechanics/battleengine-target-acquisition-static-contract-v1.md).

## Objective

Extend BattleEngine rebuild-coverage with a source-backed target-locking behavior anchor.

## What Changed

`tools/battleengine_logic_coverage_probe.py` now checks `target_lock_modes_and_stealth_range` in `references/Onslaught/BattleEngine.cpp`.

The anchor covers:

- `CBattleEngine::HandleLocks()`,
- weapon readiness before acquiring new locks,
- max-lock limiting,
- direct, proximity, and sequence lock modes,
- direct-lock start calls,
- target stealth reducing effective lock range.

`tools/battleengine_source_binary_gap_probe.py` originally classified the new
anchor as source-only pending retail-binary identity. That classification is
historical for `0x00406560`: the reviewed correction now establishes the
`CBattleEngine__HandleLocks` retail-static identity. It does not establish the
exact source identity of the two dependent helpers or any runtime behavior.

## Validation

Commands:

```powershell
npm run test:battleengine-logic-coverage
npm run test:battleengine-source-binary-gap
npm run test:battleengine-targeting-source-readback-bridge
npm run test:battleengine-target-acquisition-static-contract
```

Current results after later source/read-back bridge and gap-accounting refinement:

- BattleEngine logic coverage: source anchors `17/17`, doc anchors `3/3`.
- BattleEngine source-to-binary gap: source anchors `17/17`, source-only
  pending binary identity `1`, composite partial-retail rows `16`; among those
  rows, `15` retain the generic pending-exact-identity status and target locking
  records accepted `0x00406560 CBattleEngine__HandleLocks` retail-static root
  identity with dependent helper/source-stealth hypotheses still pending.
- Targeting source/read-back bridge: checked `6/6` current source, reviewed-correction, function-note, and static-contract anchors.

This is a bounded static bridge, not runtime proof. The accepted identity is
`0x00406560 CBattleEngine__HandleLocks`; the exact source identities of the
`0x00406da0` candidate helper and `0x00406fc0` lock-entry helper remain
hypotheses.

## Not Claimed

- This does not prove the exact source identities of the two dependent helpers.
- This bridge validation performs no new Ghidra mutation or live read-back.
- This is not runtime targeting proof.
- This does not prove target locking behavior in a live copied profile.
- Static helper structure does not prove source expressions as retail behavior.
- This does not make the repository rebuildable from scratch.
