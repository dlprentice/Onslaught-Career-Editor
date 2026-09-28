# CBattleEngineJetPart__FireWeapon

Status: active static function note
Last updated: 2026-09-27
Summary: Jet FireWeapon identity, selection and active-flag admission re-derived from the complete retail body and its actual caller.
Source File: `references/Onslaught/BattleEngineJetPart.cpp:647-656` at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. | Binary: BEA.exe.original.backup, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x00411b90`

The complete 91-byte body ends at `0x00411bea`; raw-byte SHA-256
`f8ce1178b5554b2311bae865577544f76e684d7296201525bfb28b3f8b686168`.
Its 38 instructions and the main FireWeapon tail at `0x00409f6a`, which loads
Jet from main `+0x57c`, establish the source identity. The live name now replaces
`CGeneralVolume__DispatchSelectedBurstPreset`; the old note remains a qualified
lead in the plate comment. The August note's prohibition on identifying this
as Jet FireWeapon is superseded by this complete-body/caller recheck.

The member receives Jet in ECX, has no stack argument and returns void with a
bare `RET`. Its former explicit-ECX fastcall annotation is now automatic
thiscall; EDX is initialized internally, not an incoming argument.

1. Read main from Jet `+0x18` and clear main `+0x588` before selecting a weapon.
2. Walk the weapon list to the selected index at Jet `+0x10`, updating its shared
   cursor at `+0x08`. A missing selection returns without calling Fire.
3. Test the selected weapon's full active DWORD at `+0x9c`. Zero returns.
4. Pass the selected weapon in ECX to `CWeapon__Fire` at `0x00506010`.

This gate is distinct from the store predicate: a successful
`CBattleEngineJetPart__CheckWeaponFiring` result alone does not prove that a
shot will be admitted. See the [weapon-store contract](../../../game-mechanics/battle-engine-weapon-stores.md#september-27-jet-recheck).
The implementation of Fire's downstream effects is outside this function note.

Evidence: MEASURED — the [nine-row manifest](../../../../tools/cohort-specs/jet-helper-identities-20260927.manifest.tsv),
complete bodies and actual caller packet under `local-data/test-runs/re-audit-20260926/jet/`,
and promotion/readback receipts under `local-lab/ghidra-first-training-20260907-v1/re-audit-20260926/jet-helper-identities/`.
These are static identity/interface findings. No execution of this helper or
whole-game acceptance is claimed. Cheapest falsifier: the pinned body bytes,
caller receiver load, active gate or exact callee differs in the selected specimen.
