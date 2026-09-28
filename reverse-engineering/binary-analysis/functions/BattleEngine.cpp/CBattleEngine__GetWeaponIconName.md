# CBattleEngine__WhereIsCurrentWeaponAttached

Status: active static function contract; former icon-name identity corrected
Last updated: 2026-09-27
Summary: returns a weapon attachment-selection integer, not an icon-string pointer.
Source File: `references/Onslaught/BattleEngine.cpp` | Binary: `BEA.exe.original.backup` (pristine; identity below)

Address: `0x0040c590`. Complete body: 31 bytes, SHA-256
`18717f5f74c69008fbbbf099bf0b6cfaabce053ed82103dd7ba34d533a9ac914`. Source comparison: `BattleEngine.cpp:2855–2860`.

Pristine specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Pinned source commit: `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.

The September 27 complete-body/caller review disproves the earlier icon-string
identity. The legacy filename is retained for existing links; the title and
address below identify the actual method. Earlier envelope/campaign grades
are not runtime acceptance.

## Contract

At mode `+0x260 == 3`, replace ECX with jet part `+0x57c` and tail-jump to
`00412520`. Otherwise replace ECX with walker part `+0x578` and tail-jump
to `00414610`. This wrapper has no stack arguments and no local RET;
both targets return an integer in EAX with bare RET.

HUD call `00485ed9` consumes the result as integer values 0, 1 and 2,
branching at `00485ede–00485ee7` to distinct display positions. This is
independent evidence for attachment selection, beyond a similar source
wrapper shape. It performs no enum-range check. The correct source method
is WhereIsCurrentWeaponAttached, not the neighboring GetWeaponIconName.

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
