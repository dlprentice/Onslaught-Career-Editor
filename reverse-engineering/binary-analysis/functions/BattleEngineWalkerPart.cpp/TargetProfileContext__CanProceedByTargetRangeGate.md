# TargetProfileContext__CanProceedByTargetRangeGate

Status: active static function note
Last updated: 2026-08-19
Source File: none in the pinned GPL drop | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle
106 independently accepted icon trio `539cceea` / `57f4d0ff` /
`78338207` and T3 `53d14122`, then ChargeWeapon map `8a7db5be`
— not redone. Envelope. Did not mill FUN_*. Did not pin
ResetConfiguration. Did not equate this table name to source
`ReadyToCharge`. Did not invent a Core owner.

> Address: `0x0050a080`

## Contract

Incoming-ECX `thiscall`. First insn `mov eax, [ecx+0xa0]`. Two
bare `ret` (`0x0050a09c`, `0x0050a0a2`). Body
`0x0050a080`–`0x0050a0a2` is 35 bytes, SHA-256
`1ba024f1f14e38bee454b5d72c39f2cf64257e446a5bcf2e98fa117df64052f9`.
Capstone: 12 insns, zero `E8`, zero `E9`.

Pinned body:

1. `[ecx+0xa0]==0` returns EAX=1.
2. Else `fld` BSS `0x00672fd0` (already-closed
   `CEventManager` `mTime`) / `fcomp [ecx+0x64]` /
   `test ah, 0x41` / `je` → EAX=1. Else EAX=0.
   Those slots are **not** named here.

Two inbound `.text` `E8`/`E9`: `CALL` at `0x00413d14` inside
already-pinned `CBattleEngineWalkerPart__ChargeWeapon`
`0x00413cf0`; `CALL` at `0x00411c61` inside table-named
`CGeneralVolume__DispatchMode3BurstProgressAndSpawn`
`0x00411bf0`. That table name is counted, not rewritten.
Zero encodings of imm `80 a0 50 00` in the image (not a
vtable slot).

Source architecture (not proof): walker ChargeWeapon
`BattleEngineWalkerPart.cpp:519-559` calls
`weapon->ReadyToCharge()`. Do **not** equate this table
name to that method. `Level100PulseCannonCharge.cs` names
`0x0050A080` as an open ChargeWeapon arm; that is a lead,
not a rename.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented).
See the section below. Do not implement Core from this RE
root.

Cheapest falsifier: file `0x0010a080` is not
`8b 81 a0 00 00 00`, **or** `0x0010a09c` is not `c3`, **or**
`0x0010a0a2` is not `c3`, **or** body SHA-256 is not
`1ba024f1…52f9`, **or** `tools/call_xref_scan.py` on
`0x0050a080` is not exactly `CALL` `0x00411c61` and `CALL`
`0x00413d14`, **or** any encoding of imm `80 a0 50 00`
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `1ba024f1…52f9`. `call_xref_scan` still two CALL.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0xa0]` / `[+0x64]`. Did not equate to `ReadyToCharge`.
Did not invent a Core owner.

Retail entity: ChargeWeapon callee returning EAX 0/1 from
`[+0xa0]` and an `mTime` compare against `[+0x64]`. Existing
increment owner `RetailWeaponCharge.Charge` does **not**
model this gate (`Level100PulseCannonCharge.cs` remarks).

Nearest reconstruction owner: **none added**. L100
playable-training diet — do not implement ReadyToCharge /
store spend / Charged-2 from this envelope.

Siblings: `CBattleEngineWalkerPart__ChargeWeapon`. Next named:
none from this card — reviewer STOP Get* mill;
ResetConfiguration stays unpinned.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0050a080` | `TargetProfileContext__CanProceedByTargetRangeGate` | `8b81a0000000 … 33c0 c3 b801000000 c3` (35 B) | incoming-ECX thiscall; bare ret ×2; 35 B; 0 E8 / 0 E9; 2 inbound CALL. HIGH on ABI, unique inbound pair, `mTime` fcomp. Mapping `PARTIAL_CONTRACT`. **Not** on `[+0xa0]`/`[+0x64]` names, ReadyToCharge rename, or rebuild parity. |
