# CUnit__TriggerEffect

> Address: 0x004fe030 | Source label: Unit.cpp | Binary: BEA.exe

## Status

- **Named in Ghidra:** Yes
- **Signature Set:** Yes, Wave528
- **Verified vs Source:** No direct source body match found in the current `references/Onslaught/` snapshot

## Purpose

Wave528 corrected the older damage-effect description. Current retail evidence shows a compact trigger/message helper, not the broad health-state sound/particle routine previously described here.

The body accepts one explicit `trigger_context` argument after ECX, checks trigger/profile state through `trigger_context+0x138`, gates through `CBattleEngine__IsWeaponModeCompatibleWithMountState`, chooses Tara/Billy/default pilot text IDs, allocates a `CMessage`, and queues it through the global message box when present.

## Signature

```c
void __thiscall CUnit__TriggerEffect(void * this, void * trigger_context);
```

## Evidence

- `RET 0x4` proves one explicit stack argument after ECX.
- The body uses `trigger_context`, `trigger_context+0x138`, `this+0x164 -> +0x120`, and cooldown/state field `+0x240`.
- Decompile read-back includes `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, `CMessage`, and pilot-text selection tokens including `Tara_Fighter`.
- Wave528 artifacts live under `subagents/ghidra-static-reaudit/wave528-unit-warspite-command-004fe030/`.

## Boundaries

This is static retail Ghidra evidence only. Exact trigger semantics, message text mapping, runtime UI behavior, concrete Unit/profile layouts, local names/types, source-body identity, BEA patching, and rebuild parity remain unproven.

## Related Functions

- `CBattleEngine__IsWeaponModeCompatibleWithMountState`
- `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`
- `CMessage__ctor_base`
