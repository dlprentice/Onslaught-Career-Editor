# CBattleEngineJetPart__WhereIsCurrentWeaponAttached

Status: active static function contract; former icon-name identity corrected
Last updated: 2026-09-27
Summary: returns a weapon attachment-selection integer, not an icon-string pointer.
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: `BEA.exe.original.backup` (pristine; identity below)

Address: `0x00412520`. Complete body: 72 bytes, SHA-256
`3053b7d98d38fd9a580dc128da23cf05caf962d611b61a7653ad9212987c6ca6`. Source comparison: `BattleEngineJetPart.cpp:927–932`.

Pristine specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Pinned source commit: `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.

The September 27 complete-body/caller review disproves the earlier icon-string
identity. The legacy filename is retained for existing links; the title and
address below identify the actual method. Earlier envelope/campaign grades
are not runtime acceptance.

## Contract

The selected-weapon list walk is inlined. On a matching item, load profile
`+0xa4` and return its integer `+0x38`; empty/missing selection returns
zero. Enumeration writes the list cursor at `+0x08`. EAX carries the full
32-bit result; ECX is the receiver, with no stack arguments and bare RET
on both exits. No complete list-lifetime or malformed-profile safety is implied.

The wrapper at `0040c590` tail-jumps here through main `+0x57c`;
HUD `00485ed9` consumes the result as 0/1/2 positions. The actual jet icon
getter is `004124d0`, returning profile `+0x04`. Its caller `0040a001`
joins the string-consuming continuation at `0040a006`.

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
