# CBattleEngine__IsWalkerGroundedOrCollision

Status: active static contract; contact callees re-derived from retail bytes
Last updated: 2026-09-26
Summary: mode-2 gate followed by short-circuit ground-or-object contact; the previous unknown virtual slot and timestamp predicate are resolved.
Evidence: MEASURED — fresh static instructions, constants and RTTI; SOURCE — pinned definitions for the identified queries; UNKNOWN — complete-process contact observations and player acceptance.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x004080f0`

## Identity and evidence

Complete body `[0x004080f0,0x0040811e)`, 46 bytes, freshly read from the specimen
above: SHA-256 `bf5f42c464845bdf82baa577478cd6ec96e4de51eb260e11f117834a5f3873af`.
The current Ghidra name is a descriptive label; this review does not recover an
original source spelling for this small function.

## Executable contract

The object pointer arrives in ECX. No stack arguments are consumed; return is
the full EAX value 0 or 1 with a plain `ret`. The saved `bool __fastcall`
declaration is retained metadata, not proof of the source-level ABI.

1. Read the dword at receiver `+0x260`. If it is not 2, return 0 without calling
   either contact predicate.
2. Call zero-based vtable slot 67 (`+0x10c`) at `0x004080fe`. The retail
   CBattleEngine vtable `0x005d89c4` resolves it to `CActor__IsOnGround`,
   `0x00401f70`.
3. If ground returned nonzero, return 1 immediately. Otherwise call
   `CActor__IsOnObject`, `0x00401fd0`, at `0x0040810a`, and return whether its
   EAX result is nonzero.

Ground and object contact use elapsed time since the object's timestamps at
`+0xcc` and `+0xd4`, respectively, against the event-time float at `0x00672fd0`.
Both compare with stored `0.15f` at `0x005d8588` and return x87 C0: strict
less-than for ordered comparisons, also true for a masked unordered comparison.
Pinned Stuart source `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`,
`actor.cpp:326-341` and `actor.h:45-47`, distinguishes the virtual ground query
from the non-virtual object query. The
[third label cohort](../../ghidra/README.md#re-audit-label-corrections-third-cohort--september-26)
records their exact identities and limits.

There are no object writes in this function. A valid receiver is required even
for the mode gate: the first object read precedes any virtual dispatch, and
there is no null check. Runtime replacement of the vtable is outside the
stated retail-vtable mapping.

## Limits

The old draft's unknown `+0x10c` target and unidentified `+0xd4` helper are
resolved statically. The physical contacts and event timestamps during real
play remain runtime observations to collect. A copied-runtime trace of the
mode, timestamps, executed short-circuit branch and return value can falsify
the composed behavior. This review does not claim player-input acceptance.
