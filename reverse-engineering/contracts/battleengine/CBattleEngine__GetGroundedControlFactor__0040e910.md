# CBattleEngine__GetImportance

Status: active static contract; former control-factor interpretation corrected
Last updated: 2026-09-26
Summary: retail GetImportance returns 5.0 when on ground and not on an object, otherwise 0.0; source identity and both contact predicates are resolved.
Evidence: MEASURED — fresh static instructions, constants and RTTI; SOURCE — pinned definitions for the identified queries; UNKNOWN — complete-process contact observations and player acceptance.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x0040e910`

## Identity and evidence

The complete body is `[0x0040e910,0x0040e93a)`, 42 bytes, freshly read from the
specimen above: SHA-256 `99f979d0b165369c6ad85f61547994dc791207c6107fdf492506eaf50f0ddc40`.
Pinned Stuart source `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`,
`BattleEngine.cpp:3453-3459`, identifies `CBattleEngine::GetImportance()`.
The RTTI-confirmed CBattleEngine vtable at `0x005d89c4` points here from zero-based
slot 80 (`0x005d8b04`). The second September 26 label cohort saved this identity;
the old filename remains for link stability. It is not a control-input multiplier.

## Executable contract

The receiver arrives in ECX. There are no stack arguments; the body returns its
floating result in x87 ST(0) with a plain `ret`. The saved `__fastcall` prototype
is metadata, not an independent proof of the original C++ declaration.

1. Call receiver vtable slot 67 (`+0x10c`) at `0x0040e915`. In the retail
   CBattleEngine vtable it is `CActor__IsOnGround`, `0x00401f70`.
2. Only if its EAX result is nonzero, call `CActor__IsOnObject`, `0x00401fd0`,
   at `0x0040e921`.
3. Return the float **5.0** from `0x005d85d8` if ground was true and object was
   false. Otherwise return **0.0** from `0x005d856c`.

The contact helpers subtract the object's timestamp at `+0xcc` (ground) or
`+0xd4` (object) from the event-time float at `0x00672fd0`, compare with the
single-precision value at `0x005d8588` (bits `0x3e19999a`, the stored `0.15f`),
and return x87 C0. Ordered comparisons therefore use strict less-than;
masked unordered comparisons also return 1. Pinned `actor.cpp:326-341` and
`actor.h:45-47` support the identities. See the
[third label cohort](../../ghidra/README.md#re-audit-label-corrections-third-cohort--september-26).

This body performs no object writes. Its receiver and virtual-call target must
be valid; there is no null guard. Runtime replacement of the vtable can change
the first predicate and is outside the stated retail-vtable mapping.

## Limits

The earlier factory draft's unresolved virtual target and unknown meaning of
the two numeric results are superseded by the evidence above. This recheck is
static: it does not measure observed target choices, contact timing during
play, or the FPU exception configuration of a complete retail process. A
controlled copied-runtime call/watchpoint recording both contact predicates
and the returned score is the remaining behavioral falsifier.
