# CBattleEngineWalkerPart__WhereIsCurrentWeaponAttached

Status: active static function contract; former icon-name identity corrected
Last updated: 2026-09-27
Summary: returns a weapon attachment-selection integer, not an icon-string pointer.
Source File: `references/Onslaught/BattleEngineWalkerPart.cpp` | Binary: `BEA.exe.original.backup` (pristine; identity below)

Address: `0x00414610`. Complete body: 22 bytes, SHA-256
`87e35fb4741f402649e7605d13cb3bd37786e63e8d5b93fd51ca482d3fcfaedc`. Source comparison: `BattleEngineWalkerPart.cpp:927–932`.

Pristine specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Pinned source commit: `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.

The September 27 complete-body/caller review disproves the earlier icon-string
identity. The legacy filename is retained for existing links; the title and
address below identify the actual method. Earlier envelope/campaign grades
are not runtime acceptance.

## Contract

Call GetCurrentWeapon at `00414030`. Null selection returns zero. Otherwise
load the selected weapon's profile at `+0xa4`, then return its integer field
`+0x38` in EAX. Both exits use bare RET; ECX is the receiver and there are
no stack arguments. Selection can mutate the list cursor/index through
the getter; this is not an unconditionally pure query.

The wrapper at `0040c590` tail-jumps here through main `+0x578`;
HUD `00485ed9` consumes the result as 0/1/2 positions. The actual walker
icon getter is `004145f0`, whose return comes from profile `+0x04`.
Its caller `00409ff4` joins a string-consuming continuation at `0040a006`.

The body, callers and source were compared directly; full Weapon layout and
all valid authored attachment values are not established by this pass.
`Weapon.cpp/.h` are absent from the pinned source. No HUD, input, Godot or
retail gameplay run occurred. A cheap falsifier is an isolated original-body
probe with different profile `+0x38` values and a distinct sentinel pointer at
`+0x04`, checking EAX and selection side effects; do not dereference the integer
as a string.

Private evidence: `local-data/test-runs/re-audit-20260926/walker/`, particularly
`neighbor-bodies-v1.json` and `neighbor-callers-v1.json`. Exact mutation and
recovery scope: [helper audit](../../../ghidra/README.md#re-audit-walker-helper-identities-and-interfaces--september-27).

## Isolated original-code check — September 27

The [selection/store probe](../../../game-mechanics/battle-engine-weapon-stores.md#isolated-selection-and-admission--september-27)
now executes this unchanged body together with its actual selector on authored
memory. Its 90 cases across four bodies and four altered-copy controls check
EAX, expected cursor/index changes, all other authored bytes, preserved
registers, stack balance and explicit x87 modes. This adds isolated execution
evidence to the static analysis; it does not establish real gameplay, device
input or current settings. The remaining safety/lifetime limits above stand.
