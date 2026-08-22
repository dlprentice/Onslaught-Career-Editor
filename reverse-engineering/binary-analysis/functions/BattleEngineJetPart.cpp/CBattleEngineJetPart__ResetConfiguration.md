# CBattleEngineJetPart__ResetConfiguration

> Address: `0x00412650`

Status: active static function note
Last updated: 2026-08-22
Source File: `references/Onslaught/BattleEngineJetPart.cpp` | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-22 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` with
`tools/disasm_va.py` (whole body, every branch target walked), xrefs by
`tools/call_xref_scan.py`, vtable/set words read straight out of the image
bytes. The Ghidra database was not opened. Supersedes the envelope-only
version of this note (address/signature/xref stub): the byte contract below is
new this wake. Did not mill any `FUN_*`. Did not invent field names beyond the
pinned-source members they mirror. Did not invent a Core owner.

> Address: `0x00412650`

## Contract (byte-exact)

Incoming-ECX `thiscall`, zero stack args, bare `ret`. Body
`0x00412650`–`0x00412799` inclusive, **330 bytes**, SHA-256
`e26aade4c68d52fa2dcbaf1314c8529574178678c419779654f7f69da1b8c9aa`.
Capstone-aligned: exactly **three** rel32 `E8`, **zero** `E9`
(`e8` bytes at `0x004126b9`/`0x00412705` are displacement bytes of
`mov ecx, dword ptr [0x8553e8]`, not instructions). Prologue
`83 ec 10 53 56 57 8b f9 89 7c 24 0c 33 db …`. `ebx` is the zero
register for the whole body. `edi` = `this`, spilled at `[esp+0x10]`.

**Phase 1 — drain `mWeapons` (`0x0041265e`).**
`eax = [this+0x00]`; copy it to `[this+0x08]` (the set's iterator/cursor
field — retail keeps them mirrored during manual walks); null exits the loop.
Else `esi = [eax]` (the node's payload = the `CWeapon*`); null payload also
exits. Then `push esi; mov ecx, this; call 0x004e5bd0`
(`CSPtrSet__Remove`) and `mov eax,[esi]; push 1; mov ecx,esi;
call [eax+4]` — the virtual **deleting** destructor (slot 1, flags=1)
on the weapon. Loop.

**Phase 2 — walk the configuration jet-weapon name list
(`0x00412680`).**
`ecx = [this+0x18]` (`mMainPart`); `eax = [main+0x4b0]`
(`mConfiguration`, the offset `RetailWeaponStores` already pins);
`list = config + 0x50` = the `SPtrSet<char*> mJetWeapons` member
(`BattleEngineDataManager.h:27`; walker twin uses `+0x40` =
`mWalkerWeapons` at `0x00414717`, same `First()` shape). Retail inlines
`GenericSPtrSet::First()` (`SPtrSet.h:40`): `ecx = [eax+0x50]` is
**`mFirst` = `[list+0]`** (`0x00412695`), mirrored to the iterator slot
`[list+8]` (`0x0041269d`), then `payload = ecx ? [ecx] : 0`
(`0x004126a2`/`0x004126a6`). Seeding from `[list+8]` instead would be
`Next()` semantics and would start a rebuild from a dirty iterator;
null payload → jump to the exit at
`0x00412790` (`[this+0x10] = 0; ret`) — an empty list still resets
the current-weapon index.

**Phase 3 — resolve the name to an integer by walking the world weapon set
(`0x004126b0`).**
`ebp = [payload]` — the payload is `char**`; `[payload]` is the weapon
**name string**, and null name sits out to the spawn with `or eax,-1`.
Then a linear walk of the world's weapon-pointer set at **`0x008553e8`**
(a different set from the script-object sets at `0x00855090/b0/c0`;
same node layout: `[set]` = first node, `[node]` = item word the
comparator dereferences, `[node+4]` = next, live cursor mirrored at
`[set+8]`): inline MSVC `strcmp` (two bytes/iteration,
`sbb eax,eax / sbb eax,-1`) of the configuration name against
`[weapon+0x00]` — each entry's first dword is its `char*` name.
Equality (`eax == 0`) jumps to `0x00412771`: `eax = edi` — the walk's
incremented match counter — `edi` is restored from the spill, and control
falls into the spawn pushes. Exhaustion without equality falls through
`0x00412721`-shaped tail to `or eax, 0xffffffff` (index `-1`).

**Phase 4 — spawn, init, append (`0x00412725`).**
`push -1; push eax; call 0x50f6d0; add esp, 8` —
`CWorldPhysicsManager__CreateWeaponByIndex` (current table label; sealed
static receipt row `function-c1-closure-2026-08-11.tsv:4191`,
`SEALED_STATIC_RECEIPT`, boundary `0x0050f6d0`–`0x0050f797`). The
second stack argument is the resolved integer; the constant **`-1`**
("miss") is what both ResetConfiguration twins push when the name walk
found no prior weapon, and `0x004f8842` is the image's counter-example
that pushes two computed dwords. Result in `esi`; null → skip to the
advance at `0x00412754`. Non-null:
`[esp+0x14] = [this+0x18]` (`init.mAttachedTo = mMainPart`,
matching source line 993) and
`call [weapon-vtable+0xc] (weapon, &init)` — slot 3, `CWeapon::Init`
taking the 16-byte stack `CInitEquipment` whose `mAttachedTo` field is
at `+0x14` of the argument block. Then
`push esi; mov ecx, this; call 0x004e5b20` (`CSPtrSet__AddToTail`)
onto the part's own set.

**Phase 5 — advance (`0x00412754`).**
`cursor = [list+8]; next = [cursor+4]; [list+8] = next` (null →
`ecx = 0`); while non-zero, jump back to `0x004126b1` — the name-match
phase for the next name, *not* the list seed. When exhausted:
`[this+0x10] = 0` (`mCurrentWeapon = 0`, matching source line 1001),
pop `ebp/edi/esi/ebx`, `ret`. The empty-list exit at `0x00412790` is
identical minus the `ebp` pop (the prologue pushed `ebp` only after that
branch splits).

HIGH on ABI, phase structure, field offsets, callee identities, and both
spawn-argument constants. MEDIUM_STATIC on the *meaning* of the spawn's
integer argument (see divergence below) — the constants themselves are
measured.

## Callers and callees

Inbound `.text` rel32: **exactly two CALLs**
(`tools/call_xref_scan.py`):

| Site | Enclosing | Arm |
| --- | --- | --- |
| `0x00410268` | `CBattleEngineJetPart__ctor` `0x00410210` (`ret 0x4`) | constructor tail; `[esi+0x18] = arg` (mainPart) stored at `0x00410239`, immediately before |
| `0x0040c695` | `CBattleEngine__UpdateConfiguration` `0x0040c650` (`ret`, sealed row tsv:229) | jet arm, guarded by `mov ecx,[esi+0x57c]; test ecx,ecx; je` (`0x0040c682`–`0x0040c693`); the sibling walker arm `0x0040c6a4` calls `CBattleEngineWalkerPart__ResetConfiguration` `0x004146b0` |

Zero `E9` inbound; **zero imm32 encodings** of `0x00412650` anywhere in
the image — this is not a vtable slot.

Callees: `CSPtrSet__Remove` `0x004e5bd0`;
`CWorldPhysicsManager__CreateWeaponByIndex` `0x0050f6d0`;
`CSPtrSet__AddToTail` `0x004e5b20`; plus the per-weapon virtual
deleting destructor and virtual slot-3 `Init` dispatches. The spawn's own
ctor chain installs vptr `0x005dfc94` after a transient `0x005d8824`
(`[0x005dfc94] = 0x00506930` = `CWeapon__HandleFireBurstEvent`,
re-read from the image this wake; corroborated by W008 plate
`ghidra-fullpass-findings/W008/adversarial/B08.md:231`) — i.e. the spawned
object is the `CWeapon` family.

## Source agreement and divergences

Anchor: `references/Onslaught/BattleEngineJetPart.cpp:977-1002`
(`ResetConfiguration`), called from `UpdateConfiguration`
(`BattleEngine.cpp:2918`) and the ctor (`BattleEngineJetPart.cpp:46`).

Agrees with the source on everything structural: drain-and-delete the
mounted set; iterate `mMainPart->mConfiguration->mJetWeapons`; build an
`CInitEquipment` with `mAttachedTo = mMainPart`; `weapon->Init(init)`
only on a successful spawn; `Append` to `mWeapons`; `mCurrentWeapon = 0`
even when the new list is empty.

Two honest divergences:

1. **The spawn call is not `SpawnWeapon(char*, ULONG)` at this site.**
   Source line 991 reads
   `UPhysicsManager::SpawnWeapon(*weaponName, THING_TYPE_EVERYTHING)`.
   Retail instead resolves the name to an **integer** first (phase 3's
   world-set walk) and calls with `(resolvedInt, -1)` — or `(-1, -1)`
   when the walk misses. The same shape appears at the walker twin
   (`0x004147a7/aa`, `0x00414885/8a`) and the sealed label itself says
   "ByIndex". Whatever `THING_TYPE_EVERYTHING` becomes happens inside
   `0x0050f6d0`'s ctor chain, not here; no type argument is visible at
   this call site. The sealed label's "index" reading fits the bytes;
   its runtime semantics stay unproven.
2. **Retail mirrors the set cursor while draining** (`[this+0x08]`
   written each iteration where the source writes nothing visible).
   Behaviorally equal for `GenericSPtrSet::First()` (`SPtrSet.h:40`
   reads `mFirst`; `:37` is `RemoveAll()`), so this is bookkeeping, not
   a behavior difference — recorded because a rebuild copying the
   source verbatim would not reproduce the stores.

Minor shape note: the jet has **no** primary/augmented-weapon phase; the
walker twin continues past its list walk into `config+0x60`/`+0x64`
(`mPrimaryWeapon`/`mAugWeapon`) at `0x00414807`–`0x0041496d` — see
[`../BattleEngineWalkerPart.cpp/CBattleEngineWalkerPart__ResetConfiguration.md`](../BattleEngineWalkerPart.cpp/CBattleEngineWalkerPart__ResetConfiguration.md).

## Field map pinned by this body

| Offset | Meaning | Anchor |
| --- | --- | --- |
| `this+0x00` | `mWeapons.mFirst` | drain loop `0x0041265e` |
| `node+0x04` | `SPtrSetNode::mNext` | advance `0x00412763` |
| `this+0x08` | `mWeapons.mIterator` (mirror kept warm) | `0x00412662` |
| `this+0x10` | `mCurrentWeapon` | `0x00412785` / `0x00412790` |
| `this+0x18` | `mMainPart` | `0x00412680` (also ctor store `mov [esi+0x18], eax` at `0x00410239`; `0x00410229` is `push edi`) |
| `main+0x4b0` | `mConfiguration` | `0x0041268f` (matches `RetailWeaponStores`) |
| `config+0x40` / `+0x50` | `mWalkerWeapons` / `mJetWeapons` `SPtrSet`s | walker `0x00414717`, jet `0x00412695` |
| `config+0x60` / `+0x64` | `mPrimaryWeapon` / `mAugWeapon` name ptrs | walker twin `0x00414810/15` (not re-derived further) |
| `0x008553e8` | the world's weapon-pointer set (distinct from `0x00855090/b0/c0`) | `0x4126b7` load / `0x412703` reload |
| `set+0x08` | live walk cursor of the world weapon set (mirrored at `0x4126c3`/`0x412712`) | `0x004126c3` |
| `weapon+0x00` | `char*` name used for the world-set match (comparator loads it at `0x4126d2`) | comparator `0x4126da` |

## Rebuild mapping

Nearest reconstruction owner: **none added.** `RetailWeaponSelection.cs`
(`RetailMountedWeapon`, `RetailWeaponCycle`) and `RetailWeaponStores.cs`
model selection and readouts over an *already-mounted* set; nothing in
Core yet models mounting. This contract is the mount law a future owner
needs: configuration name list × weapon factory → ordered mounted set +
`currentIndex = 0`, with the drain-before-rebuild rule on configuration
change and the current-weapon reset even on empty. Per lane rules no Core
file was edited from this RE root; the focused-test step is deferred until
an owner exists to pin (documented here rather than silently skipped).

## Cheapest falsifier

Any one of:

- File offset `0x00012650` is not `83 ec 10 53 56 57 8b f9`, or the body
  SHA-256 is not `e26aade4…c9aa` (330 bytes ending `83 c4 10 c3`).
- `tools/call_xref_scan.py 0x00412650` returns anything but exactly
  `{CALL 0x00410268, CALL 0x0040c695}`.
- Any imm32 encoding of `f0 26 41 00` exists in the image.
- Disassembly shows a fourth capstone-aligned `E8`, any `E9`, or a call
  target other than `{0x004e5bd0, 0x0050f6d0, 0x004e5b20}`.
- `[0x005dfc94]` in the specimen is not `0x00506930`.

## Receipts

- 2026-08-22 — pristine specimen
  `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
  verified before reading. Tools: `tools/disasm_va.py` (full body +
  callees `0x50f6d0`/`0x505e00`/`0x4e5b20`/`0x4146b0`),
  `tools/call_xref_scan.py` (`0x412650`, `0x50f6d0`, `0x4e5b20`),
  direct byte reads for the vtable words and the body hash.
- Reviewer round-1 receipt (2026-08-22): Phase-2 seed rewritten as the
  inlined `First()` it is (`mFirst = [list+0]` at `0x00412695`, mirror
  at `0x0041269d`, payload conditional at `0x004126a2/a6`) — the
  earlier "cursor = [list+8]" prose described `Next()` semantics; ctor
  store cite finished at `0x00410239`; guard and line-cite shapes made
  instruction-exact. Walker spawn push windows re-read this pass:
  `or eax,-1` begins at `0x004147a7` (the earlier `0x004147a5` was a
  mid-instruction window), `6a ff 50 e8` at `0x004147aa`.
- Corroboration (not duplicated): W001 fullpass plate
  `ghidra-fullpass-findings/W001/primary/A11.md:182-193` — verdict ok,
  same boundary `0x00412650 → RET 0x00412799` (134 instr), same callers
  and callee triple. This note's deltas over that plate: the phase-3
  world-set walk at `0x008553e8`, the `(resolvedInt, -1)` spawn
  argument shape shared with the walker twin, the `[this+0x08]` cursor
  mirror, and the empty-list-exit `ebp` asymmetry.
- 2026-08-22 (second wake) — **independent re-verification pass**, fresh
  read of the same pristine specimen (hash re-checked before reading).
  Re-measured with raw byte reads + `tools/disasm_va.py` full 134-instruction
  listing + `tools/call_xref_scan.py`: specimen hash, body hash/prologue/tail,
  exactly three call targets `{0x004e5bd0, 0x0050f6d0, 0x004e5b20}`, zero
  `E9`, zero imm32 self-references, `[0x005dfc94] = 0x00506930`,
  both caller sites and their guards (`test [esi+0x57c]` jet arm,
  walker twin call at `0x0040c6a4`), phase bytes at every cited anchor
  (cursor mirror, `or eax,-1` null-name path, match-counter exit
  `mov eax,edi`, advance jump to `0x004126b1`, both exits), walker-twin
  offsets `+0x40`/`+0x60`, spawn push shapes at `0x004147a5`/`0x00414883`
  (`83 c8 ff / 6a ff / 50`), source anchors
  `BattleEngineJetPart.cpp:977-1002/46, BattleEngine.cpp:2918,
  BattleEngineDataManager.h:27, SPtrSet.h:37`, sealed row tsv:4191, and
  plate citations A11.md:182-193 + B08.md:225-235. All confirmed.
  Three wording corrections applied this wake: stray `e8` displacement
  bytes are at `0x004126b9`/`0x00412705` (was ba/06); ctor's
  `[esi+0x18] = arg` store is at `0x00410239` (0x00410229 is `push edi`);
  field-map rows for the world-set load/reload sites and the weapon-name
  load made instruction-precise. No claim of substance changed.
