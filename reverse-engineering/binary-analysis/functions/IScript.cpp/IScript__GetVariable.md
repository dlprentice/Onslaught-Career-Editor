# IScript__GetVariable

> Address: `0x005362a0`

Status: active static function note
Last updated: 2026-08-24 (HUD getter static-site vs overlay-pass wording)
Source File: none — `GetVariable` / `GetWorldTextSlotTimerValue` are absent
from `references/Onslaught/` (checked 2026-08-22) | Binary: BEA.exe pristine
specimen `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Mission-native 81, registered as `GetVariable`, is the read
twin of natives 76–78. It does **not** look up a script variable or a
text id. The wrapper evaluates one integer slot index, calls
`CWorld__GetWorldTextSlotTimerValue` on world `0x00855090`, and boxes
the returned float as a `CFloatDataType`. The getter indexes the
four-slot SoA by `slot*4` and, when `state[slot]==3`, returns
`max(0, time[slot] − g_time)`; otherwise it returns the stored time
absolute. No shipped mission calls the wrapper (corpus
`DORMANT_CANDIDATE` 0/0). The only other callers are twenty sites
inside `CHud__RoutePanel_T0_00483530`, which walks `esi = 0..3`.
Evidence: MEASURED — independently read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` (SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
verified before reading) with `tools/disasm_va.py` (whole bodies),
raw byte reads (body hashes, imm32 census, string table, float
constants), and `tools/call_xref_scan.py`. No `FUN_*` milled; no Core
owner invented.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Headline finding (name vs. behavior)

`mission-native-corpus-coverage-2026-08-15.tsv` row 81 is
`GetVariable` / `0x005362A0` /
`IScript__GetWorldTextSlotTimerValue` / 0 authored sites / 0 levels /
`DORMANT_CANDIDATE`. The 2026-08-17 name table's current saved symbol
is `IScript__GetVariable` (the older `GetWorldTextSlotTimerValue`
label is the callee, not the wrapper). Those rows are confirmed this
wake, plus one correction to the implied reading:

- The **name** is retail-authentic: `.rdata` at `0x0064f610` is the
  ASCII run `GetVariable\0GetEnergy\0\0\0Shutdown\0…` continuing the
  descending-corpus-index layout already pinned for natives 76–78
  (`ShutdownVariable 0x64f634` · `SetVariable 0x64f648` ·
  `InitVariable 0x64f654` sit immediately above).
- The **registration block binds that name to this handler**:
  `mov ebp, 0x005362a0` at VA `0x00531c9c` / file `0x131c9c`
  (`bd a0 62 53 00`), then
  `mov dword ptr [0x64e260], 0x64f610` at VA `0x00531ca1` / file
  `0x131ca1` (bytes `c7 05 60 e2 64 00 10 f6 64 00`, name immediate
  at `0x00531ca7`), then `mov [0x64e290], ebp` at `0x00531cab`.
  Exactly one image-wide imm32 of `0x005362a0`. Name↔handler binding
  is image-internal.
- The **behavior** is a slot-index timer read, not a variable map
  and not a text-id lookup. `SetVariable` (77) matches slots by
  stored text id; `GetVariable` (81) passes the evaluated integer
  straight into `[ecx + index*4 + disp]`. Implementing 81 as
  `map[name]` or `map[textId]` would be false to the shipped game.
  Implementing it as "the HUD's clock" would also be false: the
  wrapper is dormant in every authored mission; the HUD panel calls
  the **callee**, not this wrapper.

Sibling write/update/clear family:
[`IScript__InitVariable_SetVariable_ShutdownVariable.md`](IScript__InitVariable_SetVariable_ShutdownVariable.md).

## Contract (byte-exact)

### Native 81 `GetVariable(slotIndexExpr) → float` — `0x005362a0`, 142 bytes

Body `0x005362a0`–`0x0053632d` inclusive through both `ret 0xc`
terminators, SHA-256
`e62e22b2d2c23d78fb324c554de37d4cdb3a5dc62be766ada28101cbc215b45c`.
Two `E8` (`CDXMemoryManager__Alloc` `0x005490e0` at `0x005362ca`;
`CWorld__GetWorldTextSlotTimerValue` `0x0050d760` at `0x005362f0`).
Zero `E9`. Incoming `ecx` is unused (SEH `push ecx` only). One
computed call: element `vtable[+0x30]`. Neighbor: two `nop` then
already-pinned native 78 at `0x00536330`.

1. MSVC SEH prologue (`push -1; push 0x005d70d9; fs:[0]`), `push ecx`,
   `push esi`.
2. `push 0x5d3` (1491) / `push 0x0064fa40`
   (`C:\dev\ONSLAUGHT2\MissionScript\IScript.cpp`) / `push 0x18` /
   `push 8` / `mov ecx, 0x009c3df0` / `call 0x005490e0` — 8-byte
   `CDXMemoryManager__Alloc`. `esi = eax`.
3. Alloc-fail (`esi == 0`): `[out_result] = 0`; teardown; `ret 0xc`
   at `0x0053632b`.
4. `eax = [esp+0x18]` (arg0 = script args / `vm`); `ecx = [eax]`;
   `call [vtable+0x30]` — **integer** evaluation of element 1.
5. `push eax; mov ecx, 0x00855090; call 0x0050d760` — getter
   `(world, slotIndex)`.
6. `eax = [esp+0x20]` (arg2 = `out_result`);
   `[esi] = 0x005e4ea4` (`CFloatDataType` vtable, already pinned in
   `ghidra-functions.md` datatype table id 2); `fstp [esi+4]`;
   `[eax] = esi`.
7. Teardown (`fs:[0]` restore, `add esp, 0x10`); `ret 0xc` at
   `0x00536313`.

Argument order: only element 1 is consumed. The dispatcher's 3-dword
frame still ends `ret 0xc`. The boxed result is a float even though
the input getter is the integer `+0x30` slot.

### Callee `CWorld__GetWorldTextSlotTimerValue(slot)` — `0x0050d760`, 61 bytes

Body `0x0050d760`–`0x0050d79c` inclusive through both `ret 4`
terminators, SHA-256
`7c21d7e5e946164e3540be2e713df9bf88f4b5213e9ff4ec9c248043dd11370c`.
Zero `E8` / zero `E9`. Neighbor: three `nop` then already-pinned
`CWorld__ClearWorldTextSlot` at `0x0050d7a0`.

```
eax = [esp+4]                          ; slot index, not a text id
cmp dword [ecx + eax*4 + 0x20c], 3     ; state[slot]
jne absolute                           ; 0x0050d793
fld dword [ecx + eax*4 + 0x23c]        ; time[slot]
fsub dword [0x00672fd0]                ; minus g_time
fcom dword [0x005d856c]                ; 0.0f (image dword 0)
fnstsw ax; test ah, 1                  ; C0 = remaining < 0
je return_st0                          ; 0x0050d79a, keep remaining
fstp st(0); fld dword [0x005d856c]     ; clamp to 0.0f
ret 4                                  ; 0x0050d790
absolute:
fld dword [ecx + eax*4 + 0x23c]
ret 4                                  ; 0x0050d79a
```

No occupancy test and no bounds check. `slot >= 4` indexes the next
SoA group (id words begin at `this+0x21c`).

This is the same `state==3` bit-pattern the 76–78 note already
attributed to `UpdateWorldTextSlotTiming`'s relative arm
(`new = g_time + a` stored at `+0x23c`, secondary write skipped).
The getter is the inverse: remaining = stored deadline − now,
floored at 0. When `state != 3` the stored dword is returned
unchanged. Time units are whatever `0x00672fd0` carries (existing
notes treat it as the global `mTime`); this wake did not re-derive
that identity.

SoA layout confirmed by the getter's `*4` indexing plus Clear's
already-pinned 4-iteration `add eax, 4` walk (state at `+0x20c`,
id compared at `+0x10` from each state word = `+0x21c` group):

| Group | World offset | Getter use |
| --- | --- | --- |
| state[0..3] | `+0x20c` | `== 3` selects remaining-time arm |
| id[0..3] | `+0x21c` | unused here; Clear/Update match by it |
| string[0..3] | `+0x22c` | unused here; HUD reads via `ebx+0x855070` |
| primary time[0..3] | `+0x23c` | returned (absolute or remaining) |
| secondary time[0..3] | `+0x24c` | unused here; HUD `ebx` walks this group |
| default[0..3] | `+0x25c` | HUD loop bound (`cmp ebx, 0x25c`) |

HIGH on wrapper bytes, ABI, both `E8` targets, `0x00855090`,
`vtable[+0x30]`, boxed `CFloatDataType` store, getter bytes, SoA
`*4` addressing, `state==3` remaining-time clamp against
`0x00672fd0` / `0.0f`, and the 21-site inbound set. Not claimed:
authored names of states other than the integer 3 test, time units,
or what a `slot >= 4` caller would mean.

## HUD drain — `CHud__RoutePanel_T0_00483530` at `0x00483530`

`tools/call_xref_scan.py` on `0x0050d760`: **21** `E8`, zero `E9`.
One is the wrapper at `0x005362f0`. The other twenty all sit inside
this panel (`0x00483530`–`0x00484321`, plain `ret`, sole inbound
`E8` at `0x00487b8a`). Former descriptive name
`CHud__RenderControllerSlotStatusPanel` was demoted 2026-08-14
([`hud-route-name-demotion-live-promotion-2026-08-14.md`](../../hud-route-name-demotion-live-promotion-2026-08-14.md));
current table name is `CHud__RoutePanel_T0_00483530`. This wake does
not rename it and does not claim on-screen layout.

Timer-read loop (HIGH on control, not on HUD field names):

1. `lea edi, [this+0x64]; xor esi, esi; mov ebx, 0x24c` at
   `0x00483954`–`5d`.
2. Every getter site in the loop is `push esi` / `mov ecx, 0x855090`
   / `call 0x50d760` (some arms park an `idiv` remainder with an
   extra `push edx` that the `ret 4` leaves for a later `sprintf`).
3. Loop tail at `0x004842df`–`f4`: `add ebx, 4; inc esi; add edi, 0xc;
   cmp ebx, 0x25c`. Four iterations, `esi ∈ {0,1,2,3}`.
4. `[ebx + 0x855050]` with `ebx=0x24c` is `world+0x20c` (state[0]):
   `0x855050 + 0x24c = 0x85529c = 0x855090 + 0x20c`. The same
   addressing gives string[0] at `[ebx+0x855070]` and secondary
   time[0] at `[ebx+0x855090]`.
5. Format switch at `0x00483a2f`–`43`:
   `eax = [ebx+0x855050]; dec eax; cmp eax, 5; ja default;
   jmp [eax*4 + 0x00484324]`. Discriminator is `state[slot] − 1`,
   cases 0..5 = states 1..6. Jump table:
   `{0x00483a4a, 0x00483db9, 0x00483c05, 0x00483be2, 0x00483e64,
   0x00483cbd}`. Measured format immediates include `0x006245cc`
   (`%d`), `0x0062d324` (`%d (%d)`), `0x0062d348` (`%d%`),
   `0x0062d33c` (`%d%d:%d%d`), `0x0062d318` (`(%d)`). State-enum
   names are not claimed.
6. HUD also compares `state[slot]` to 3 directly (`cmp [ebx+0x855050], 3`
   at `0x004839e4`), the same sentinel the getter uses.

The 76–78 note left "who drains the slots for display" open. The
drain is this panel. Twenty static `E8` sites to the getter sit
inside it; the measured loop is four iterations (`esi = 0..3`)
with an exclusive state-1..6 switch (`ja` default). That twenty is
a static site count, not a dynamic per-pass call count: one overlay
pass cannot execute all twenty sites because the switch is exclusive.
This note does not invent an exact dynamic count or an occupancy
law. The Mission-native wrapper is not on that path.

## Callers

Zero rel32 inbound to `0x005362a0`. Twenty-one rel32 inbound to
`0x0050d760` (list above). Wrapper reachability is the registration
immediate only, consistent with a dormant command-index handler.

## Pinned-source status

`grep` of `GetVariable` / `GetWorldTextSlotTimerValue` over
`references/Onslaught/` returns nothing. No source anchor; no
divergence-from-source section. Shape authority is the image. The
allocator / `__FILE__` / line-1491 triple matches the already-tracked
`pc-native-source-coordinates-2026-08-12.tsv` row for this VA.

## Field map pinned by these bodies

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `vm+0x00` | expression-stack element 1 (slot index) | `0x005362df` |
| element `vtable[+0x30]` | integer evaluation | `0x005362e7` |
| `0x00855090` | world object used as getter `this` | `0x005362eb` |
| `0x0050d760` | slot-index timer reader | call at `0x005362f0` |
| result vptr `0x005e4ea4` | `CFloatDataType` | `0x005362f9` |
| result `+0x04` | boxed float | `fstp` at `0x005362ff` |
| world `+0x20c + slot*4` | `state[slot]` | getter `0x0050d764` |
| world `+0x23c + slot*4` | `time[slot]` | getter `0x0050d76e` / `0x0050d793` |
| `0x00672fd0` | subtracted now-time on the state-3 arm | `0x0050d775` |
| `0x005d856c` | `0.0f` clamp constant | `0x0050d77b` / `0x0050d78a` |

## Rebuild mapping

Nearest reconstruction owner: **none added.** Core still has no
world-text / message-slot model (`grep WorldText|TextSlot|GetVariable`
over `rebuild/OnslaughtRebuild.Core` → nothing).
`Level100ActorScriptCommandKind` is the closed set
`FollowWaypoint … Damage` — no member for native 81, and Level 100's
program never issues it (corpus 0/0). A future owner that reconstructs
another level's program needs, on top of the 76–78 four-slot store:

- a slot-index reader (0..3) returning a float;
- `state==3` → remaining time floored at 0, else the stored time;
- a HUD overlay pass that polls all four slots each frame and
  formats from `state[slot]`, **not** a script opcode.

Implementing 81 as a named-variable get, or wiring the HUD through
the dormant wrapper, would be wrong. Per lane rules no Core file was
edited; the focused-test step is deferred until such an owner exists.

Corpus note (not self-applied — the TSV is outside this lane): row 81
should point at this note; the command name `GetVariable` stays
(retail-authentic); any future `currentGhidraName` should remain the
wrapper `IScript__GetVariable`, with the callee kept as
`CWorld__GetWorldTextSlotTimerValue`.

## Cheapest falsifier

Any one of:

- Body SHA-256 mismatch: wrapper 142 B `e62e22b2…c215b45c`; getter
  61 B `7c21d7e5…dd11370c` — or either body ending other than
  `ret 0xc` / `ret 4`.
- `tools/disasm_va.py` shows a getter target other than `0x0050d760`,
  an `ecx` immediate other than `0x00855090`, an evaluation slot
  other than `+0x30`, a result vptr other than `0x005e4ea4`, or a
  getter compare other than `[this+eax*4+0x20c]` vs `3`.
- The string at `0x0064f610` is not `GetVariable`, or the
  registration pair `0x00531c9c` / `0x00531ca1` moves apart.
- `tools/call_xref_scan.py` on `0x005362a0` returns any rel32
  caller, or on `0x0050d760` returns a count other than 21.
- HUD loop tail loses `inc esi` / `add ebx, 4` / `cmp ebx, 0x25c`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading (2,506,752 B,
  `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
  Tools: `tools/disasm_va.py` (wrapper `0x005362a0` through neighbor
  `0x00536330`; getter through Clear at `0x0050d7a0`; HUD entry,
  `xor esi,esi` seed, switch, loop tail), raw byte reads (both body
  hashes; `.rdata` window at `0x0064f610`; registration window
  `0x00531c9c`–`0x00531cb1`; float `0x005d856c` = `0.0`;
  `0x005d8568` = `1.0` used only as HUD compare, not by the getter;
  imm32 census: exactly one `0x005362a0`), and
  `tools/call_xref_scan.py` (0 wrapper callers; 21 getter callers).
- Coverage corpus cross-reference: TSV row 81 re-read this wake
  (`GetVariable`, `0x005362A0`, 0/0, `DORMANT_CANDIDATE`). Current
  saved wrapper name from
  `ghidra-function-name-table-2026-08-17.tsv` is
  `IScript__GetVariable`; callee row is
  `CWorld__GetWorldTextSlotTimerValue` `0x0050d760`–`0x0050d79c`;
  HUD row is `CHud__RoutePanel_T0_00483530` `0x00483530`–`0x00484321`.
- W008 plates A11/B11 remain corroboration for the getter name and
  the 20+1 inbound split; this wake re-derived the getter
  instruction-by-instruction from the image, so the slot-index /
  remaining-time contract is no longer plate-only.
- Completes the open "who drains the slots" item from the 76–78
  note. Does not reopen that note's wrapper bytes.
- 2026-08-24 — wording correction (t_e5a87f71 / historical review
  ordinal 512, t_fa3f4c3e / aa4f3b50): retracts "twenty times per
  overlay pass" as a dynamic-frequency claim. The twenty `E8` sites
  remain the static inbound count already proved by
  `call_xref_scan.py`; the four-iteration `esi = 0..3` loop and
  exclusive state-1..6 switch are unchanged. No new specimen read,
  no invented dynamic count, no occupancy law.
