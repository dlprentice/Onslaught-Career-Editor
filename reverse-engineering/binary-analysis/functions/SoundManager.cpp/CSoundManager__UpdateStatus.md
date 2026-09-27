# CSoundManager__UpdateStatus

Status: active — static identity and bounded processing order rechecked
Last updated: 2026-09-27
Summary: sound updates continue selectively while paused or frozen; the member receiver is rechecked and device behavior remains open.

> Address: `0x004e1b20` | Source: `references/Onslaught/SoundManager.cpp:1224–1411`

The complete body in pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
supports the source identity through camera snapshots, event sorting, backend
globals, two clock calls, event processing and final deferred-update completion.
The pinned source at `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` is a structural
comparison, not proof that retail follows every source branch.

The September 27 instruction recheck establishes these boundaries:

- Paused event field `+0x84` suppresses time advancement at `004e1c4d` and
  the pitch/fade/owner block at `004e1dff`. The latter jump rejoins at
  `004e221a`: playing byte `+8` and a signed nonnegative channel still permit
  backend `UpdateSound` at `004e222b`. Pinned source nests that call inside
  its unpaused branch.
- A separate owner-clear path for stopped events with stored time greater
  than five precedes the pause gate. Pausing therefore does not prohibit
  every owner operation. End-time and loop processing also remain reachable.
- Manager frozen field `+0x1c` gates position refresh at `004e1c5f` and final
  recycling at `004e22e8`. It does not suppress the whole update, sorting,
  clocks, debug processing or backend updates.
- The updater saves the next link before recycling the current event and
  finishes with `UpdatesDone` at `004e2338`.

Complete-body evidence and review are in
`local-data/test-runs/re-audit-20260926/sound/identity-evidence-v4.json`; the
[shared sound note](../../csoundmanager-shared-semantics-2026-08-11.md#september-27-sound-family-identity-and-documentation-recheck)
owns the related source differences. The earlier note's caller attribution to
`CGame__MainLoop` at `0046eee0` was not rechecked in this pass.

The later [sound-interface cohort](../../../ghidra/README.md#re-audit-sound-interfaces--september-27)
normalizes its saved explicit-ECX fastcall receiver to automatic thiscall.
The body uses incoming ECX as its manager; the complete FrontEnd caller supplies
SOUND at `00466c14` before call `00466c19`, without stack arguments. Void and
purge zero are preserved. Exact numerical edge cases, callback-safe traversal,
actual device results and audible pause behavior remain open. A controlled
copied-instance update with paused/frozen combinations and intercepted backend
calls is the next inexpensive falsifier; it would still not prove audible parity.

> Source File: SoundManager.cpp | Binary: BEA.exe
