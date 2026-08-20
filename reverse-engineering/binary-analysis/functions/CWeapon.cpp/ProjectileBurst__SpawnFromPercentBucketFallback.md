# ProjectileBurst__SpawnFromPercentBucketFallback

Status: active static function note
Last updated: 2026-08-19
Source File: none in the pinned GPL drop | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. This
wake already landed jet fire/charge siblings `0b5f9914` /
`5a5c8d43` — not redone. Envelope, not a 160-instruction walk.
Did not mill FUN_*. Did not mill Get*. Did not equate ReadyToCharge.
Did not invent a Core owner.

> Address: `0x00506010`

## Contract

Incoming-ECX `thiscall`. First insn `sub esp, 8`. `esi = ecx`.
Two bare `ret` (`0x005060fd`, `0x005061e8`). Body
`0x00506010`–`0x005061e8` is 473 bytes, SHA-256
`efb720554c82dfd422f09345bace1e456791fbed0351803c44b11884f725ccbe`.
Capstone: 160 insns, 6 `E8`, zero `E9`, 5 unique rel32 targets.
Raw `0xE8` byte count is 7 because `shr eax, 0x1f` encodes
`c1 e8 1f`. Raw `0xE9` byte count is 1 because `imul ecx`
encodes `f7 e9`. Neighbour table
`CWeapon__DoesTargetMaskMatchDistanceProfile` starts at
`0x005061f0` after a 7-byte `nop` pad and is not rewritten.

Pinned prologue, with `esi = ecx`:

1. `mov eax, 0x51eb851f`. `fld [esi+0x60]` / `fistp` /
   `[esi+0x60]=0`. Same `[+0x60]` live-charge slot
   `RetailWeaponCharge` already counts as the LoseCharge
   store. **Not** named here.
2. Signed `/100` via that magic into `[esi+0x68]`. `ebx =
   [[esi+0xa4] + edx*4 + 0xc]`. Same record/`+0xc`
   five-dword charge-level table ChargeWeapon already walks.
   Those slots are **not** named here.
3. Two `E8` already-named `CSPtrSet__First` `0x00406d20`
   via BSS `0x008553ec`. Counted, not contracted.
4. Counted, not contracted: `E8`
   `ProjectileBurst__ResolvePresetByPercentBucketFallback`
   `0x00509e90`; `E8`
   `ProjectileBurst__SpawnFromCurrentPreset` `0x005069f0`;
   `E8` `CSoundManager__PlayEffect` `0x004e1940`; `E8`
   already-closed `CEventManager__AddEvent_AtTime`
   `0x0044b370`. Success `ret` loads EAX=1.

Ten inbound `.text` `E8`/`E9` (6 already inside pinned
fire/charge bodies; 4 counted, not rewritten):

- `CALL` `0x00411be4` already-pinned
  `CGeneralVolume__DispatchSelectedBurstPreset`
- `CALL` `0x00411e0f` / `0x00411e5b` already-pinned
  `CGeneralVolume__DispatchMode3BurstProgressAndSpawn`
- `JMP` `0x00413ce2` already-pinned
  `CBattleEngineWalkerPart__FireWeapon`
- `CALL` `0x00413d5f` / `0x00413e9a` already-pinned
  `CBattleEngineWalkerPart__ChargeWeapon`
- `CALL` `0x0044e093` table
  `CFenrir__ProjectileBurstCallerBoundary_0044e020`
- `CALL` `0x004ded11` table `CSentinel__UpdateFlamethrowers`
- `CALL` `0x004f4bd6` table
  `CThunderHead__UpdateAimYawThunderheadFlamethrowerBurstAndPickup_004f4920`
- `CALL` `0x004fc0b7` table
  `CUnit__TrySpawnOrFinalizeAttachedUnit`

Zero encodings of imm `10 60 50 00` in the image (not a vtable
slot). Those four non-BattleEngine table names are counted, not
rewritten.

Source architecture: none. `CWeapon` is absent from the pinned
GPL drop. Do **not** invent a source method name.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00106010` is not `83 ec 08`, **or**
`0x00106015` is not `8b f1`, **or** `0x00106017` is not
`b8 1f 85 eb 51`, **or** `0x0010602a` is not
`c7 46 60 00 00 00 00`, **or** `0x001061e8` is not `c3`, **or**
body SHA-256 is not `efb72055…ccbe`, **or**
`tools/call_xref_scan.py` on `0x00506010` is not exactly those
ten sites, **or** any encoding of imm `10 60 50 00` exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `efb72055…ccbe`. `call_xref_scan` still ten sites.
Did not open Ghidra. Did not edit `rebuild/**`. Did not name
`[+0x60]` / `[+0x68]` / `[+0xa4]`. Did not walk
`0x005069f0` / `0x00509e90`. Did not implement ReadyToCharge.

Retail entity: shared weapon fire/burst-start helper. Existing
Core comments in `Level100ActorWeaponRuntime.cs` /
`SimulationConstants.cs` already cite this VA for actor-weapon
cadence. **None added.** L100 playable-training diet — do not
implement from this envelope.

Siblings: already-pinned jet/walker FireWeapon and ChargeWeapon
tails. Next named:
`CWeapon__AdvanceChargeProgressIfAnySlotAssigned` `0x005068f0`
(ChargeWeapon increment; no 2026-08-19 PE envelope).

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00506010` | `ProjectileBurst__SpawnFromPercentBucketFallback` | `83ec08 53568bf1 b81f85eb51 … b801000000 5b83c408c3` (473 B) | incoming-ECX thiscall; bare ret ×2; 473 B; 6 E8 / 0 E9 / 5 unique E8; 10 inbound. HIGH on ABI, `[+0x60]=0`, `/100` magic, unique ten-site xref. Mapping `PARTIAL_CONTRACT`. **Not** on callee identities, the four non-BEA caller names, or rebuild parity. |
