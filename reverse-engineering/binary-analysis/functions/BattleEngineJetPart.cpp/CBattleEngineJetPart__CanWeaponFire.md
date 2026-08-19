# CBattleEngineJetPart__CanWeaponFire

Status: active static function note
Last updated: 2026-08-19
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
100 accepted through ChargeWeapon `9bde6c3a` — not redone. Walker
CanWeaponFire `0x00414630` is already `REBUILD_READY` — not
redone. Envelope. Did not mill FUN_*. Did not implement lock
sets. Did not edit `rebuild/**`.

> Address: `0x00412570`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [ecx]`. Live `ecx`
is this. Three bare `ret` (`0x004125a8`, `0x004125f0`,
`0x0041260b`). Body `0x00412570`–`0x0041260b` is 156 bytes,
SHA-256
`9f8837975c5296a90944f7569c15085b9def257ae518fe9210ca0b3c89c52b3b`.
Capstone: 56 insns, zero `E8`, zero `E9`. The displacement
`9c 00 00 00` occurs **zero** times in this body.

Pinned body:

1. Counted list walk on `[ecx]` / `[ecx+8]` until the index
   matches `[ecx+0x10]`. Same shape JetPart GetWeaponCharge
   already counts. Empty / miss returns EAX=0.
2. Store/heat/overheat walk on `[ecx+0x18]`. `fcomp` 0.0f at
   `0x005d856c`. EAX=1 on the two success `ret`s. Those slots
   are **not** named here. There is **no** `[+0x9c]` active
   gate.

One inbound `.text` `E8`/`E9`: `CALL` at `0x004065bb` inside
already-pinned `CBattleEngine__HandleLocks` `0x00406560`. Zero
encodings of imm `70 25 41 00` in the image (not a vtable slot).

Source architecture (not proof):
`CBattleEngineJetPart::CanWeaponFire`
`BattleEngineJetPart.cpp:936-958`. Source has no `IsActive()`
test. Retail matches that: zero `9c 00 00 00`. Walker source
`BattleEngineWalkerPart.cpp:936-961` has `IsActive()`; that
already-`REBUILD_READY` body is not rewritten.

Rebuild mapping: `PARTIAL_CONTRACT` (named, existing Core owner
counted). See the section below. Do not implement Core from this
RE root. Do not raise the walker `REBUILD_READY` row.

Cheapest falsifier: file `0x00012570` is not `8b 01`, **or**
`0x0001260b` is not `c3`, **or** body SHA-256 is not
`9f883797…2b3b`, **or** the body contains `9c 00 00 00`, **or**
`tools/call_xref_scan.py` on `0x00412570` is not exactly one
`CALL` at `0x004065bb`, **or** any encoding of imm `70 25 41 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `9f883797…2b3b`. `9c 00 00 00` still absent.
`call_xref_scan` still one CALL. Did not open Ghidra. Did not
edit `rebuild/**`. Existing Core owner
`RetailWeaponFireGate.CanWeaponFire` is counted, not rewritten.
Existing walker `REBUILD_READY` is not raised.

Retail entity: jet-part CanWeaponFire from already-pinned
HandleLocks. Stuart architecture (not proof):
`BattleEngineJetPart.cpp:936-958`.

Nearest reconstruction owner: existing
`RetailWeaponFireGate.CanWeaponFire`. Not a new owner. L100
card `t_aa5586e5` is on a playable training-path diet — do not
implement from this mapping until that lane names the arm.

Siblings: `CBattleEngineWalkerPart__CanWeaponFire` (already
`REBUILD_READY`, not redone) /
`CBattleEngineJetPart__GetWeaponCharge`. Next named:
`CBattleEngineWalkerPart__GetWeaponAmmoPercentage` `0x00414410`
(no 2026-08-19 PE envelope; OPAQUE).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00412570` | `CBattleEngineJetPart__CanWeaponFire` | `8b01 … c3` (156 B; zero `9c000000`) | incoming-ECX thiscall; bare ret ×3; 156 B; 0 E8 / 0 E9; 1 inbound CALL. HIGH on ABI, inlined list walk, absent `[+0x9c]`, unique inbound. Mapping `PARTIAL_CONTRACT` onto existing Core owner. **Not** on store-slot names, walker rewrite, or a new Core owner. |
