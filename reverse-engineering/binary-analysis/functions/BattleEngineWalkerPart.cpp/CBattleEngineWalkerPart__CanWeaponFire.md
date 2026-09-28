# CBattleEngineWalkerPart__CanWeaponFire

Status: active static function contract
Last updated: 2026-09-27
Summary: this is the selected active weapon's store-admission gate, separate from reload readiness; its heat and ammo comparisons differ for unordered operands.
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: `BEA.exe.original.backup` (pristine; identity below)

Address: `0x00414630`. Pristine specimen:
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Complete body `[00414630,004146a9)`: 121 bytes / 37 instructions, SHA-256
`32e7211754b16a53331446a4e944518f50e1dacfd5a3846ca572a5db32dff029`.

The September 27 pass freshly decoded the complete body and its caller,
comparing pinned `BattleEngineWalkerPart.cpp:936–961` at source commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. This replaces the August 19
unnamed-field account. Historical campaign grades do not establish current
rebuild or retail runtime acceptance.

## Admission

The function calls GetCurrentWeapon, returning zero if selection is null or
weapon active DWORD `+0x9c` is zero. The selected profile's `+0x24` supplies
the store index. For finite comparison operands:

- Nonzero heat flag at main `+0x55c + 4*index`: require the current store at
  main `+0x52c + 4*index` to be below capacity at configuration
  `+0x88 + 4*index`, and overheat DWORD at main `+0x544 + 4*index` to be zero.
- Zero heat flag: require the current store to be strictly positive.

It does not compare store against the next shot's consumption. Both success
paths write full EAX=1; refusal writes full EAX=0. Incoming receiver is ECX,
there are no stack arguments, and the three exits use bare RET. Keep the
full-DWORD Boolean interface rather than an AL-only Boolean annotation.

At `00414673`, the heat path tests only x87 C0 (`TEST AH,1`), so a masked
unordered comparison passes its comparison test; zero overheat is still needed.
The ammo path tests C0/C3 (`TEST AH,41h` at `00414699`) and refuses unordered.
These are instruction-level distinctions, not measured NaN behavior in retail.
Do not silently replace both predicates with a supposedly equivalent comparison.

HandleLocks calls this gate at `004065db`, then separately calls weapon
ReadyToFire at `00406817`. This function therefore does not establish reload,
charge or projectile readiness by itself. Calling GetCurrentWeapon may change
its list cursor or selected index, as [that contract](CBattleEngineWalkerPart__GetCurrentWeapon.md)
records.

The [weapon-store contract](../../../game-mechanics/battle-engine-weapon-stores.md#september-27-walker-recheck)
and [Ghidra audit](../../../ghidra/README.md#re-audit-verified-walker-records--september-27)
record scope and evidence. Private complete bodies and caller witnesses are in
`local-data/test-runs/re-audit-20260926/walker/`.

## Limits

Source/body agreement establishes this bounded identity and branch structure;
complete Weapon layout, helper behavior, valid store indices and live firing
cadence remain separate. A useful falsifier is a confined original-body probe
with selection intercepted, covering inactive/null, finite threshold values,
overheated heat stores and masked unordered operands, checking full EAX and
preservation of authored memory. The bounded isolated probe below now exercises those cases; full retail execution remains separate.

## Isolated original-code check — September 27

The [selection/store probe](../../../game-mechanics/battle-engine-weapon-stores.md#isolated-selection-and-admission--september-27)
now executes this unchanged body together with its actual selector on authored
memory. Its 90 cases across four bodies and four altered-copy controls check
EAX, expected cursor/index changes, all other authored bytes, preserved
registers, stack balance and explicit x87 modes. This adds isolated execution
evidence to the static analysis; it does not establish real gameplay, device
input or current settings. The remaining safety/lifetime limits above stand.
