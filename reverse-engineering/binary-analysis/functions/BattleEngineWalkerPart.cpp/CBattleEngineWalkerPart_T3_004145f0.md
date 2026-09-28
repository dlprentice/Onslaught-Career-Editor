# CBattleEngineWalkerPart__GetWeaponIconName

Status: active function contract; earlier structural name superseded
Last updated: 2026-09-27
Summary: returns the selected weapon profile's icon-string pointer, separate from its integer attachment position.
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: `BEA.exe.original.backup` (pristine; identity below)

Address: `0x004145f0`. Complete body: 22 bytes, SHA-256
`2f1b7220588b07e4bf8773d559532154fba97fc66072e7e8c611976f198b70ae`.
Pristine specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source `BattleEngineWalkerPart.cpp:918–924` is pinned at
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`. The legacy filename retains links;
its former label is not current identity authority.

## Contract

The complete body calls GetCurrentWeapon at `00414030`. If selection is null,
return null; otherwise load its profile at weapon `+0xa4`, then return profile
`+0x04` in EAX. ECX is the walker receiver, with no stack arguments and bare
RET on both exits. The corrected return annotation is `char *`, replacing `int`;
physical EAX transport is unchanged.

Selection can mutate its list cursor and repair its selected index, as the
[selector contract](CBattleEngineWalkerPart__GetCurrentWeapon.md) records.
The isolated selection/store probe includes thirteen calls to this unmodified
body, checking exact raw pointer transport, all authored memory, registers and
stack balance. It does not dereference the pointer or establish string lifetime.

## Caller evidence

The main ChangeWeapon body `[00409f70,0040a555)` selects walker `+0x578`
through call `00409ff4`, or jet `+0x57c` through `0040a001` when mode
`+0x260 == 3`. The join `0040a006` guards null, adds seven to the pointer
at `0040a010`, then compares pointed bytes, including the Vulcan Cannon
suffix. This independently identifies string transport and matches
`BattleEngine.cpp:1987–1994`. The main source icon wrapper (`2837–2843`)
is inlined at this observed caller; no additional standalone function boundary
is established. Profile `+0x38` instead supplies the attachment integer.

The two-body [identity cohort](../../../ghidra/README.md#re-audit-weapon-icon-identities--september-27)
records exact names/interfaces, preservation, readback and recovery. Complete
pristine bodies/caller evidence is retained under
`local-data/test-runs/re-audit-20260926/walker/neighbor-callers-v1.json`.
The [isolated probe](../../../game-mechanics/battle-engine-weapon-stores.md#isolated-selection-and-admission--september-27)
records which original bodies actually executed.

## Limits

Valid receiver/list/profile memory is a premise. The missing Weapon source
headers prevent a complete layout claim; raw pointer transport does not prove
its content, lifetime or rendered output. No player input, HUD rendering or
retail gameplay acceptance is claimed. A copied-runtime observation of the
selected pointer and rendered icon is the remaining presentation falsifier.
