# CBattleEngine__StartLock

> Source File: `references/Onslaught/BattleEngine.cpp` | Binary: BEA.exe (the Ghidra database's specimen, SHA-256 `74154bfa…`)
> Address: `0x00406fc0`
> Status: source identity promoted in Ghidra 2026-08-04; 2026-08-19 byte contract added
> Last updated: 2026-08-19
> The **filename** is retained at the withdrawn name so historical links and
> exports remain resolvable. A filename here is a research label, not a claim.

## Name corrections — 2026-07-28

Superseded in place against `ghidra-function-name-table-2026-07-27.tsv`, the
2026-07-27 headless export of the live maintainer Ghidra project. The evidence
grade, and the limits of what a corrected name does and does not establish, are
stated once at [the area index](../_index.md#the-name-corrections-of-2026-07-28).

| Address | Superseded label | 2026-07-28 intermediate label (historical) | Correction |
| --- | --- | --- | --- |
| `0x00406fc0` | `CBattleEngine__AddProjectile` | `CBattleEngine__AddTrackedActiveReader` | same class; suffix re-read |

## Source-identity promotion — 2026-08-04

The later backed-up, scratch-reproduced, independently refuted and separately
read-back target-lock promotion supersedes the July descriptive label with
`CBattleEngine__StartLock`, without changing this function's range. Its live
promotion READY is
`local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/promotion/promotion.ready.json`,
SHA-256
`77f635e552b7a2dd8425af012204f8172eadcb1de8ecdb02a30e2c12ff9b9945`.
This proves the bounded source-method identity and saved metadata, not all-path
runtime behavior or rebuild parity.

Three places carried the withdrawn label until 2026-07-28: the H1, the
`Saved Ghidra name` line below, and the function name inside the saved-signature
block. All three now read the current name. **Nothing else changed** — the
lock-entry interpretation, the argument shape, the boundaries and the contract
link were already written against the lock reading and are unaffected by the
rename.

### The rename and this note's source candidate do not conflict — and neither is settled

Recorded rather than smoothed over, because a reader could otherwise take the new
Ghidra label as having displaced the source candidate.

- **MEASURED (database):** the current 2026-08-12 export names `0x00406fc0`
  `CBattleEngine__StartLock`.
- **SOURCE:** `references/Onslaught/BattleEngine.h:142` declares
  `void CBattleEngine::StartLock(CUnit*, float, BOOL=FALSE)` and
  `references/Onslaught/BattleEngine.cpp:801` defines it. Its body, at
  `BattleEngine.cpp:806-824`, performs the five steps this note's
  "Current Static Interpretation" already lists, in the same order: reject a
  dying unit, scan `mLocks` for a duplicate, `new CLockInfo()`, store
  start/finish/direct-lock, `mLocks.Append(info)`. The declared argument list
  matches the saved signature below argument for argument. The Ghidra label
  describes the same act — the appended `CLockInfo` holds a reader set by
  `SetReader` — in different words.
- **MEASURED:** the later target-lock proof completed the bounded byte,
  call-graph, source, scratch, refuter, and promotion join for this identity.

---

## Status

- Saved Ghidra name: `CBattleEngine__StartLock` (after the intermediate July
  label `CBattleEngine__AddTrackedActiveReader`)
- Current static semantic role: lock-entry creation, not projectile spawning
- Source identity: `CBattleEngine::StartLock`
- Source identity status: bounded and promoted; complete runtime behavior remains open
- Runtime behavior proof: not established

## Saved Signature

```c
void __thiscall CBattleEngine__StartLock(
    void * this,
    void * target,
    float lockTime,
    int directLockFlag);
```

The parameter names above describe the current address-bound call shape. They
do not accept the stronger source method identity.

## Current Static Interpretation

The reviewed `CBattleEngine__HandleLocks` body calls `0x00406fc0` four times
with a candidate target, a lock-time value, and a direct-lock flag. The helper
then:

1. rejects a candidate carrying the checked inactive/dying-style flag;
2. scans the tracked set at BattleEngine `+0x294` to avoid duplicates;
3. allocates one `0x14`-byte entry when no duplicate exists;
4. stores current and finish-time values plus the direct-lock flag; and
5. appends the entry to the tracked set.

This structure aligns with pinned-source `CBattleEngine::StartLock`. The old
projectile interpretation resulted from the superseded
`CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` name at `0x00406560`.
Neither the caller nor this helper is current evidence of projectile emission.

## Contract

The bounded machine-readable contract is
[`battleengine-target-acquisition-static-contract-v1`](../../../game-mechanics/battleengine-target-acquisition-static-contract-v1.md).
It records `0x00406fc0` as a saved dependent name whose lock-entry role is
statically supported while the exact source name remains hypothesis-only.

## Boundaries

- No Ghidra rename or mutation is performed by this note.
- Exact `CLockInfo`, `CUnit`, BattleEngine, timestamp, flag, and set layouts are
  not established.
- The checked flag is not promoted to an exact retail field name.
- Lock timing, target choice, projectile emission, weapon firing, gameplay
  effects, and rebuild behavior remain unproven.
- No BEA launch, executable mutation, debugger action, or runtime observation
  occurred.

## 2026-08-19 byte contract

Independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Cycle 90
accepted `6544fb6f` lock-trio mapping — not redone. Name-correction
history above is not rewritten. The v1 acquisition contract's
hypothesis-only source-name line is not rewritten.

Incoming-ECX `thiscall`. First insn `push ebx`. One `ret 0xc`
(`0x00407058`). Body `0x00406fc0`–`0x0040705a` is 155 bytes, SHA-256
`bed3568af6e5d031d1be9c4a0aa339ccd06bf3b5877094fc385757937780d21f`.
Three `E8`, zero `E9`. Neighbour table `CBattleEngine__FireLock`
starts at `0x00407060` after five `nop`s and is not rewritten.
Preceding table `CBattleEngine__SelectNearestForwardTargetFromGlobalSet`
ends at `0x00406fba` and is not rewritten.

The body, with `ebx = [esp+8]` after the `push ebx`:

1. `test byte [ebx+0x2c], 4` / `jne` epilogue. No null check.
2. Walk the set at `this+0x294` (`lea edi, [ecx+0x294]`). For each
   live node: `cmp [node], ebx`. Match jumps to the same epilogue
   (duplicate reject). `esi` stays 0 through this walk.
3. `push 0x332` / `push 0x006230bc` / `push 0x15` / `push 0x14` /
   `mov ecx, 0x009c3df0` / `E8` `CDXMemoryManager__Alloc`
   `0x005490e0`. File `0x002230bc` is
   `C:\dev\ONSLAUGHT2\BattleEngine.cpp`. Size `0x14`. If EAX != 0:
   `[eax]=0`, `[eax+0xc]=0`, `esi=eax`.
4. `push ebx` / `mov ecx, esi` / `E8` `CGenericActiveReader__SetReader`
   `0x00401000`.
5. `fld [0x00672fd0]` / `fst [esi+4]` / `fadd` the lock-time stack
   slot / `fstp [esi+8]`. Store the third stack arg at `[esi+0x10]`.
   `0x00672fd0` is BSS (not in the 2,506,752-byte image); the
   campaign already closed it as `CEventManager` `mTime`.
6. `push esi` / `mov ecx, edi` / `E8` `CSPtrSet__AddToTail`
   `0x004e5b20`.

Those field names, `Append` versus `AddToTail`, `MEMTYPE`, and the
callee bodies are **not** this proof.

Four inbound `.text` `E8`/`E9`, all inside table
`CBattleEngine__HandleLocks` `0x00406560`–`0x00406d12`:
`0x004068d9`, `0x00406a51`, `0x00406aae`, `0x00406d06`. Each site
pushes a flag, a float, and a unit pointer, then `mov ecx` to the
BattleEngine. Two sites push `1`, one pushes `0`, one pushes `ebp`.
Zero encodings of imm `c0 6f 40 00` in the image.

Source architecture (not proof): `CBattleEngine::StartLock`
`references/Onslaught/BattleEngine.cpp:801-825` and
`CLockInfo` at `BattleEngine.h:48-62`. `IsDying` is `mFlags &
TF_DYING` with `TF_DYING = 4` (`thing.h:45`). Retail inlines the
ctor zeros and the `mTime` / lock-time / flag stores.

Rebuild mapping: `PARTIAL_CONTRACT` (named, not implemented). See
the section below. Do not implement Core from this RE root.

Cheapest falsifier: file `0x00006fc0` is not `53`, **or**
`0x00006fc7` is not `f6 43 2c 04`, **or** `0x00007017` is not
`6a 14`, **or** `0x0000701e` is not `e8 bd 20 14 00`, **or**
`0x00007031` is not `e8 ca 9f ff ff`, **or** `0x00007050` is not
`e8 cb ea 0d 00`, **or** `0x00007058` is not `c2 0c 00`, **or**
body SHA-256 is not `bed3568a…d21f`, **or**
`tools/call_xref_scan.py` on `0x00406fc0` is not exactly those
four `CALL`s, **or** a fifth `.text` `E8`/`E9` to this entry
exists.

## Rebuild mapping — 2026-08-19

Grade: `PARTIAL_CONTRACT`. Not `REBUILD_READY`. Independently
re-read official+twin `74154bfa` this wake (2506752 equal). Body
SHA-256 still `bed3568a…d21f`. `call_xref_scan` still four `CALL`s
inside HandleLocks. Cycle 90 accepted the trio map. Did not open
Ghidra. Did not edit `rebuild/**`.

Retail entity: player `CBattleEngine` lock-set insert. Producer of
the `+0x294` occupancy FireLock / GetCurrentTarget walk. Stuart
architecture (not proof): `BattleEngine.cpp:801-825`.

Nearest reconstruction owner: **none**. Core has no lock-set type
and no `+0x294` insert. `Simulation.TryFire` is the FireLock
spawn owner, not this producer.

Not the owner: Godot `Level100EffectCue.AquilaTargetLocked` is the
homing-missile lock sound. HUD README: target-lock layers stay
absent.

Focused test: none. L100 card `t_aa5586e5` is on a playable
training-path diet — do not implement lock sets from this mapping
until that lane names the arm.

Siblings: `CBattleEngine__FireLock` /
`CBattleEngine__DisplayLock` /
`CBattleEngine__GetCurrentTarget` in this folder. Next named of
the 2026-08-04 five-row lock cohort: `CBattleEngine__LockHit`
`0x00407140`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00406fc0` | `CBattleEngine__StartLock` | `53 8b5c2408 56 57 f6432c04 … e8bd201400 … e8ca9fffff … e8cbea0d00 … c20c00` (155 B) | incoming-ECX thiscall; ret 0xc ×1; 155 B; 3 E8 Alloc + SetReader + AddToTail / 0 E9; 4 inbound HandleLocks. HIGH on ABI, dying-byte `+0x2c` bit 2, `+0x294` duplicate walk, `0x14` alloc, `mTime`+lock-time stores, unique four-site inbound. Mapping `PARTIAL_CONTRACT`; no Core owner. **Not** on field names, `MEMTYPE`, or rebuild parity. |
