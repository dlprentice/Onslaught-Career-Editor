# CBattleEngineWalkerPart__GetCurrentWeapon

Status: active static function contract
Last updated: 2026-09-27
Summary: selected-weapon lookup can mutate the list cursor and repair the selected index; index zero falls through to list enumeration when no augmented or primary weapon is returned.
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: `BEA.exe.original.backup` (pristine; identity below)

Address: `0x00414030`. Pristine specimen:
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Complete body `[00414030,004140c6)`: 150 bytes, SHA-256
`be9c716b45e42511a087ee08591c8f0362b7bf5fed57f42a52b5a3f152f08405`.

The September 27 pass freshly decoded the complete body and related callers,
and compared pinned `BattleEngineWalkerPart.cpp:609–641` at source commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. Constructor and main-player
receiver evidence identify this class independently of the saved label.
This replaces the August 19 note's intentionally unnamed-field description;
its historical campaign grades are not a present runtime-acceptance claim.

## Selection and side effects

1. Read selected index at walker `+0x10`. At index zero, return augmented
   weapon `+0x1c` if main `+0x2fc` and that pointer are nonzero; otherwise
   return primary `+0x18` if present. These returns do not test weapon `+0x9c`.
2. Otherwise enumerate the offset-zero list, starting at index one if a
   primary exists and zero if it does not. **Index zero without a returned
   augmented/primary weapon also reaches this enumeration.** A null item ends
   traversal. Return the item whose enumeration index matches selection.
3. On failure, reset selected index to zero, then return primary or the first
   list item, or null. This fallback does not repeat the augmented check.

The walk writes the iterator at walker `+0x08`; selection repair occurs at
`00414099`. Early augmented/primary returns bypass the walk, so the precise
mutation depends on the path. Neither this getter nor a wrapper calling it is
unconditionally pure. It returns a pointer in EAX with an incoming ECX receiver
and no stack arguments. All three normal exits use bare RET.

The [weapon-store contract](../../../game-mechanics/battle-engine-weapon-stores.md#september-27-walker-recheck)
places selection alongside weapon switching and firing admission. Private
complete-body and caller evidence is in
`local-data/test-runs/re-audit-20260926/walker/identity-leads-v2.json` and
`callers-v1.json`; the corrected 25-row comments are recorded in
[the Ghidra audit](../../../ghidra/README.md#re-audit-verified-walker-records--september-27).

## Limits

This is static instruction/source/caller evidence, not a gameplay run. Valid
list nodes and profile/object lifetimes are premises; corrupt or cyclic lists
are not made safe by this function. `Weapon.cpp/.h` are absent from the partial
source, so no complete weapon layout is inferred. A useful falsifier is an
isolated original-body run on copied lists covering index zero without a
primary, invalid indices, null items and augmented activation, checking both
EAX and the cursor/index writes. Current rebuild implementation was not inspected.

## Isolated original-code check — September 27

The [selection/store probe](../../../game-mechanics/battle-engine-weapon-stores.md#isolated-selection-and-admission--september-27)
now executes this unchanged body together with its actual selector on authored
memory. Its 90 cases across four bodies and four altered-copy controls check
EAX, expected cursor/index changes, all other authored bytes, preserved
registers, stack balance and explicit x87 modes. This adds isolated execution
evidence to the static analysis; it does not establish real gameplay, device
input or current settings. The remaining safety/lifetime limits above stand.
