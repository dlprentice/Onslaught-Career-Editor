# CUnit__ApplyRandomDestructibleDamageBurst

> Address: `0x004F9430`

Status: active static function note
Last updated: 2026-08-22
Source File: none — `Unit.cpp` is absent from `references/Onslaught/`
(checked 2026-08-22) | Binary: BEA.exe pristine specimen
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: the unit-side bridge for Mission native `HalfDestroy`. A live
segments controller at `[unit+0x178]` receives the controller-owned random
segment burst; otherwise the unit's life at `+0xf8` is divided by a random
1.5-based denominator. The two paths are exclusive and both return directly.
Evidence: MEASURED — pristine SHA verified before complete capstone body
decode and hash, raw float reads, whole-`.text` rel32 scan, image-wide imm32
census, direct-callee reads, and the complete Mission-native caller window.
No `FUN_*` was used as a first gate; no rebuild owner changed.

## Contract (byte-exact)

Body `0x004f9430`–`0x004f9481` inclusive through the complete plain `ret`,
**82 bytes / 26 instructions**, SHA-256
`593dc455cb5a86bc861db640c00c0259f015fa717191b9c4c5d274d7f6328a46`.
It saves ESI and one scratch dword, has **2 direct `E8`, 0 `E9`**, and both
conditional branches stay inside the body. Signature shape is
`void __thiscall ...(CUnit *unit)`: ECX is saved as ESI, no stack arguments
are read, and both exits use plain `ret`.

## Stage law (byte-exact)

1. **Segmented-unit dispatch** (`0x004f9434`–`0x004f9445`): load
   `[unit+0x178]`. When non-null, pass it as ECX to
   `CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold`
   `0x00444160`, then return. This arm never reaches the unit-life write.
2. **Ordinary-unit fallback** (`0x004f9446`–`0x004f9481`): call
   `Random__NextLCGAbs 0x004de8d0` on global RNG `[0x008a9d9c]`. The
   callee's complete body returns the absolute value of its next state, so
   the caller's `and 0x8000ffff` plus signed-negative fixup leaves the low
   16-bit remainder `r` in the non-negative range.
3. Convert `r` to x87 float, multiply by raw constant
   `[0x005d8d4c] = 00 00 c0 37 = 2.288818359375e-05f`, then add
   `[0x005d8bd8] = 00 00 c0 3f = 1.5f`.
4. Store `[unit+0xf8] = [unit+0xf8] / (1.5f + r *
   2.288818359375e-05f)`, then return. This direct life rewrite does not
   call the shared slot-40 damage boundary, consume shields, or schedule a
   death callback.

The current function name's “DamageBurst” is a saved research label. The
byte contract above is the proved operation; no source name is inferred for
the exact random distribution.

## Direct callees

| Site | Callee / role |
| --- | --- |
| `0x004f943e` | `CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold 0x00444160` |
| `0x004f944c` | `Random__NextLCGAbs 0x004de8d0` |

The segmented callee's unique-pointer dedupe, per-segment random draws, slot-5
eligibility, `100000.0f` damage call, and below-half latch are already pinned
in its own note and are not restated as new evidence here.

## Caller and census

Exactly **one** inbound rel32 image-wide and zero imm32 sites:
`IScript__HalfDestroy 0x00534370` calls at `0x00534379`.
That complete caller is **17 bytes / 5 instructions**, SHA-256
`4ae820da83b6bbc3eaf02a4dc078af50ad91470dba21117cdf509b6030f89dc2`:
it loads the attached thing from `[IScript+0x10]`, tests thing-type bit
`0x10` at `[thing+0x34]`, calls this body only when the bit is set, then
returns `ret 0xc`. Registry dispatch is the caller's only image-wide imm32;
there is no second native or ordinary rel32 caller.

## Field and constant map

| Offset / value | Static role | Anchor |
| --- | --- | --- |
| `[unit+0x178]` | optional destroyable-segments controller | dispatch at `0x004f9434` |
| `[unit+0xf8]` | ordinary-unit life value rewritten by fallback | `fdivr` / `fstp` |
| `[0x008a9d9c]` | RNG object | `0x004f9446` |
| `0x005d8d4c` | fallback random scale, `2.288818359375e-05f` | `0x004f9467` |
| `0x005d8bd8` | fallback denominator base, `1.5f` | `0x004f946d` |

## Pinned-source and rebuild status

No `Unit.cpp` source body survives in the pinned drop. The rebuild has no
per-part segment controller or this native's ordinary-unit random life
rewrite, so no Core behavior or focused test was invented. A future owner
must preserve the controller-first exclusive branch and the fallback's direct
life division rather than routing both through shared damage.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x004f9430`–`0x004f9481` is not
  `593dc455…28a46`, or either exit stops using plain `ret`.
- The body has an inbound rel32 other than `0x00534379`, or any image-wide
  imm32 of `0x004f9430` appears.
- The controller load leaves `[unit+0x178]`, or the live-controller arm no
  longer calls `0x00444160` and returns before the life write.
- Either float constant changes, or the terminal store leaves `[unit+0xf8]`.

## Receipts

- 2026-08-22 — official pristine specimen above, SHA verified before
  reading. Complete target/caller disassemblies, raw hashes, direct calls,
  rel32/imm32 censuses, `Random__NextLCGAbs` return polarity, and both float
  constants reproduced with the read-only PE/capstone probe.
- Related contracts:
  [`../DestructableSegmentsController.cpp/CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold.md`](../DestructableSegmentsController.cpp/CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold.md),
  [`CUnit__ApplyDamage.md`](CUnit__ApplyDamage.md).
