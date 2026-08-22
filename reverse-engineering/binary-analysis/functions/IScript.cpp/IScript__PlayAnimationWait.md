# IScript__PlayAnimationWait

> Address: `0x005351D0`

Status: active static function note
Last updated: 2026-08-22
Source File: none — absent from `references/Onslaught/`; the wait/VM
mechanics this native shares are pinned map-level in
[`../IScript.cpp.md`](../IScript.cpp.md) ("Wait helpers")
Binary: BEA.exe pristine specimen
`C:/Users/david/source/Onslaught-Career-Editor/local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 54, registered as `PlayAnimationWait`: three
arguments (animation name, two byte flags); resolves the attached
thing's mesh, looks up the animation by name, plays it via thing
`vtable[+0xf0]`, then installs a full CVM snapshot at `[IScript+0x38]`
and stops the VM — resume is
`IScript__RestoreSavedStateAndGotoInstruction` when the animation
finishes. 24 authored sites across 9 files.
Evidence: MEASURED — independently read 2026-08-22 from the pristine
specimen (SHA-256 above, verified before reading): capstone whole-body
disassembly, raw byte reads (body hash), image-wide imm32 census,
descriptor walk, whole-`.text` rel32 xref scan, authored `.msl` recount
(`local-lab/famJ_playanim.py`). No `FUN_*` milled.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`
(in the main tree), SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding

Corpus TSV row 54 is `PlayAnimationWait` / `0x005351D0` / empty
name-table cell / 24 sites; confirmed this wake. Registration:

- Handler immediate: `bd d0 51 53 00` (`mov ebp, 0x005351d0`) — the
  single image-wide imm32 sits at VA `0x00531252`. Zero rel32 inbound.
- Descriptor: the stride-paired cells follow the Family D block; the
  name string `"PlayAnimationWait\0"` exists in `.rdata` (its storing
  instruction is register-carried in that block and not individually
  isolated — honest gap, same note as SetVelocity).

## Contract (byte-exact)

Body `0x005351d0`–`0x0053532e` inclusive through the complete final
`ret 0xc`, **351 bytes**, SHA-256
`a29cdae9ecac3553a7189611df2bc5bda1f605d17f1878d9503ccb7218171765`.

```
005351d8  mov esi, [thing+0x30]           ; mesh carrier
005351db  mov eax, [thing+0x74]           ; mMissionScript back-pointer
005351de  test eax,eax; je warn           ; null or not-this-script:
005351e2  cmp eax, ebx; je ok             ;   "FATAL ERROR: Called
warn:     CConsole__Printf(0x0064fb64)    ;    PlayAnimWait on the non
                                          ;    base script object"
                                          ;   then CONTINUES
005351f8  test esi,esi; je exit           ; no mesh -> silent exit
00535204  call [mesh-vtable+0x24]         ; mesh object -> edi
          ; (replaces any prior [this+0x38]: CSPtrSet__Remove + delete)
00535238  call [args0-vtable+0x38]        ; animation name -> eax
0053523e  call 0x004aa630                 ; CMesh__FindAnimationIndexByName
00535243  args1 via [vtable+0x3c] &0xff   ; flag 1
0053525f  args2 via [vtable+0x3c] &0xff   ; flag 2
0053526c  call [thing-vtable+0xf0]        ; PlayAnimation(idx, f1, f2)
00535272  alloc 0x228 via 0x5490e0 (__FILE__ 0x64fa40, line 0x396)
          ... IListener/CMonitor/CVM construction dance ...
005352bd  rep movsd 0x81 dwords           ; operand stack + depth
          ... six-dword interpreter tail (+0x210..+0x224) ...
00535309  mov dword ptr [eax], 0x005e4f1c ; CVM vptr
00535313  call 0x004e5b20                 ; CSPtrSet__AddToTail(this+0x28)
0053531c  mov dword ptr [0x0089c800], 1   ; stop the singleton VM
00535326  mov [ebx+0x38], esi             ; install snapshot
exit:     ret 0xc
```

The snapshot construction from `0x00535292` onward is exactly the
shared Wait-helper dance documented in
[`../IScript.cpp.md`](../IScript.cpp.md) (0x228 CVM, IListener→CMonitor→CVM
vtable sequence, `rep movsd 0x81`, six-dword tail copied **before** the
live stop store, `CSPtrSet__AddToTail` on `+0x28`, `[0x0089c800]=1`,
install at `[this+0x38]`). This note adds the per-native facts only.

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `[thing+0x30]` | mesh carrier (null → silent exit) | `0x005351d8`, `0x005351f8` |
| `[thing+0x74]` | `mMissionScript` self-check (mismatch → FATAL print, continue) | `0x005351db`–`0x005351f5` |
| `0x004AA630` | `CMesh__FindAnimationIndexByName(name)` | `0x0053523e` |
| thing `vtable[+0xf0]` | PlayAnimation slot 60 `(idx, flag1, flag2)` | `0x0053526c` |
| `[IScript+0x38]` | installed CVM snapshot (prior replaced with Remove+delete) | `0x00535211`–`0x0053522c`, `0x00535326` |
| resume | `IScript__RestoreSavedStateAndGotoInstruction` on anim finish | map-level, CLOSED |

Authored ABI witness: `PlayAnimationWait("closing", TRUE, FALSE)` —
the two flags are byte-masked ints through `vtable[+0x3c]`; their
authored meaning (loop/restart-class semantics) stays open.

## Callers

Zero rel32 inbound; dispatch-table-only. Authored recount this wake:
**24 active sites in 9 files** (hive bosses ×14, MainGun ×6, GillMArm
×2, rocketbase, Vent). Matches corpus TSV.

## Pinned-source status

Absent from the pinned source.

## Rebuild mapping

No Core owner yet. When one lands: play-by-name + VM-suspend with
completion-callback resume; the non-base-script FATAL-and-continue
behavior is part of the observable contract. Focused test deferred
until that owner exists.

## Cheapest falsifier

Any one of:

- Body SHA-256 over `0x005351d0`–`0x0053532e` is not
  `a29cdae9…171765`, or the alloc size leaves 0x228 / line token 0x396.
- A second image-wide imm32 of `0x005351d0`, or any rel32 inbound.
- The snapshot vptr sequence leaves
  `0x005e4f2c → 0x005d92d4 → 0x005e4f1c`.

## Receipts

- 2026-08-22 — pristine specimen (main tree
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`), SHA-256
  verified before reading. Tools: capstone body disassembly, raw byte
  reads, imm32/rel32 censuses, descriptor walk, authored `.msl` recount
  (`local-lab/famJ_playanim.py`).
- Cross-reference: [`../IScript.cpp.md`](../IScript.cpp.md) Wait helpers
  (shared mechanics owner).
