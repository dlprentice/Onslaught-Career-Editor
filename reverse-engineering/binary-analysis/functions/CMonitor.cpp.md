# CMonitor / CSPtrSet function map

Status: active static function map
Last updated: 2026-08-18 (SetReader + wrapper pool Initialise 40000 / teardown)
Source File: `C:\dev\ONSLAUGHT2\Monitor.h` (SEH `__FILE__` pointer `0x00622b80`
read out of `AddDeletionEvent`) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — every byte below was re-read from the pristine specimen at
file offset VA − 0x400000. Function names are the live Ghidra name table
(`db.18627` lineage); the byte-level contracts here are independent of the
names.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00401000` | `CGenericActiveReader__SetReader` | `56 8bf1 57 8b7c240c 8b06 3bf8 7421 85c0 740f 8b4004 85c0 7408 56 8bc8 e8af4b0e00 85ff 893e 7408 56 8bcf e811000000 5f 5e c20400` at file offset `0x00001000` | `ret 4`. `this` is a one-dword `CGenericActiveReader` whose `[this+0]` is `mToRead`. `edi = arg` (new `CMonitor*`). If `arg == [this]` return. If old `mToRead` and `[mToRead+4]` (the deletion set) are live, `CSPtrSet__Remove` (`0x004e5bd0`) the **reader cell** (`push esi`) from that set — it does **not** call `DeleteDeletionEvent`. Then `[this] = arg`. If `arg != 0`, `push esi; ecx = arg; call AddDeletionEvent` (`0x00401040`). HIGH. 164 direct `E8`. Script assign uses this on `CThingPtr+4` (`0x0052f440`). |
| `0x00401040` | `CMonitor__AddDeletionEvent` | `6aff 68260f5d00 64a100000000 50 64892500000000 51 57 8bf9 8b4704 85c0 753f 56 6a18 68802b6200 6a5e 6a10 b9f03d9c00 e86a801400 8bf0 … 8bce e8b1470e00 … 897704 … 8b442418 8b4f04 50 e8d4490e00 … c20400` | Installs an SEH frame (second slot `0x005d0f26`). If `[this+4]` is null it lazily allocates **0x18** bytes via `CDXMemoryManager__Alloc` (manager `0x009c3df0`, `__FILE__` `0x00622b80` = `Monitor.h`, line `0x5e` = 94), runs `CSPtrSet__Init` (`0x004e5840`), stores it at `[this+4]`; then `CSPtrSet__AddToHead` (`0x004e5a80`) the stack arg and `ret 4`. HIGH: one lazy 0x18-byte `CSPtrSet` per monitor at `+4`. The arg is the pointer stored as the wrapper-node payload; Shutdown writes `dword [arg] = 0`. |
| `0x0042d9b0` | `CMonitor__DeleteDeletionEvent` | `8b4904 85c9 740a 8b442404 50 e80f820b00 c20400` | If `[this+4]` is non-null, `CSPtrSet__Remove` (`0x004e5bd0`) the argument; `ret 4`. HIGH: the named pair to `AddDeletionEvent`. `SetReader` and `CThingPtrDataType` dtor **inline** the same `Remove` and do not call this. |
| `0x00466120` | `CMonitor__ctor` | `8bc1 c7400400000000 c700d4925d00 c3` | Zeroes `[this+4]` (the deletion-event set) and installs the vtable `0x005d92d4`. HIGH. |
| `0x00419a20` | `CMonitor__scalar_deleting_dtor` | `56 8bf1 e818120a00 f644240801 740b 56 b9f03d9c00 e8e6f71200 8bc6 5e c20400` | Calls `CMonitor__Shutdown` (`0x004bac40`), then if the `flags & 1` deleting flag is set frees `this` through `CDXMemoryManager__Free` (manager `0x009c3df0`); `ret 4`. HIGH. |
| `0x004bac40` | `CMonitor__Shutdown` | `56 8bf1 57 8b4604 c706d4925d00 85c0 7453 8b08 85c9 894808 7404 8b01 eb02 33c0 85c0 7420 c70000000000 … e88e45f7ff 57 b9f03d9c00 e883e50800 c7460400000000 5f 5e c3` | Installs base vtable `0x005d92d4`. If `[this+4]` is live, walks the set (`cursor` at `set+8`) and for each wrapper does `mov dword [payload], 0` — `payload = [node+0]` is the `AddDeletionEvent` arg. Then `CSPtrSet__Clear` (`0x0042f220`, a `jmp` to `0x004e5c60`), `CDXMemoryManager__Free` the 0x18-byte set, `[this+4]=0`. HIGH. This is `ToReadDied` for a reader cell (`[reader] = mToRead = 0`) and a null of `node[0]` for a listener node. |
| `0x004bacb0` | `CMonitor__Shutdown_Core` | `56 57 8bf9 8b4704 85c0 7453 8b08 … c70000000000 … e82445f7ff 56 b9f03d9c00 e819e50800 c7470400000000 5f 5e c3` | Same death-walk / Clear / Free / `[this+4]=0` as `Shutdown`, but does **not** install the base vtable. HIGH. Used by subclasses that have already swapped the vptr. |
| `0x004e5840` | `CSPtrSet__Init` | `8bc1 33c9 8908 894804 89480c c3` | Zeroes `+0` (head), `+4` (tail), and `+0xC` (count) — the 0x18-byte object a monitor allocates. HIGH. |
| `0x004e5a80` | `CSPtrSet__AddToHead` | `a134d18300 56 85c0 8bf1 7512 … 6a08 b9f03d9c00 e8e6350600 8b16 8b4c2408 895004 8908 8b560c 8906` | `ret 4`. Recycles an 8-byte wrapper from free-list `0x0083d130` or `Alloc`s 8 (`SPtrSet.cpp:0xb7`). `[node+4] = old head`; `[node+0] = arg`; `[set+0] = node`. HIGH: the deletion set stores **wrappers**, not the arg itself. |
| `0x004e5c60` | `CSPtrSet__Clear` | `8b410c 33d2 3bc2 7421 8b4104 3bc2 740b 56 8b3530d18300 897004 5e 8b01 a330d18300 8911 895104 89510c c3` at file offset `0x000e5c60` | Zero-arg `ret`. If `count` (`+0xc`) is 0, return. Else splice the live chain onto free-list `0x0083d130` (`[tail+4] = old_free` when tail live; `[0x0083d130] = old head`) and zero `+0` / `+4` / `+0xc`. Does **not** call `CDXMemoryManager__Free` per node. HIGH. `0x0042f220` is a 5-byte `jmp` to this body (same table name); CMonitor death-walk calls the thunk. |
| `0x004e5990` | `CSPtrSet__ClearAnyDynamicCreatedNodes` | `56 8b3530d18300 57 33ff 85f6 7444 8b0d34d18300 8bc6 8b7604 3bc1 7211 8b1538d18300 8d14d1 3bc2 7304 8bf8 eb20 85ff 7405 897704 eb06 893530d18300 50 b9f03d9c00 e848380600 … c3` | Zero-arg `ret` (cdecl). Walks free-list `0x0083d130`. Pool is `[0x0083d134, 0x0083d134 + 0x0083d138*8)`. In-range nodes stay; out-of-range nodes are unlinked and `CDXMemoryManager__Free`d. HIGH. Sole `E8` is `CGame__Shutdown` `0x0046c9e9`. These are the overflow wrappers AddToHead allocs after the "creating nodes dynamicaly" warning (`0x00632774`). |
| `0x004e59f0` | `CSPtrSet__Initialise` | `a134d18300 85c0 7413 6850276300 … 8b742408 6889000000 6830276300 8d04f500000000 6a4c 50 b9f03d9c00 e8b1360600 8bd6 a334d18300 … 891538d18300 … 890d30d18300 … c3` | `cdecl`, one arg = slot count. If `[0x0083d134]` already set, print `Warning: Initilise SptrSet twice` (`0x00632750`) and `ret`. Else `Alloc(count*8)` (`SPtrSet.cpp:0x89`, pool `0x4c`), `[0x0083d134]=base`, `[0x0083d138]=count`, `[0x0083d130]=base`, then chain `[slot_i+4]=slot_{i+1}` and last next=0. HIGH. Sole `E8` is `CLTShell__InitializeRuntimeAndLoadCoreResources` `0x004efb58` with `push 0x9c40` (40000 slots, 320000 bytes). |
| `0x004e5910` | `CSPtrSet__Shutdown` | `8b0d30d18300 85c9 7441 8b1534d18300 57 8bc1 8b4904 3bc2 890d30d18300 720d 8b3d38d18300 8d3cfa 3bc7 7217 50 … e8d8380600 … 52 … e8b4380600 c70534d1830000000000 c70530d1830000000000 c3` | Zero-arg. Walks the free list: overflow nodes `Free`d, in-pool nodes skipped; then `Free`s the pool block and zeroes `0x0083d134` / `0x0083d130`. HIGH. Sole image ref is `JMP` `0x004f01ec` inside `CLTShell__ShutdownRuntimeAndReleaseResources`. |

## Family roster (named in live Ghidra, not yet byte-mapped here)

`CMonitor__UpdateSoundEventPlaybackForReader` (`0x00409950`),
`CMonitor__ToggleAttachedObjectFlag300` (`0x0040e840`),
`CMonitor__UpdateTrackedList_59C` (`0x0040e940`),
`CMonitor__FlushTrackedList_1D4` (`0x0040eb50`),
`CMonitor__UpdateTrackedList_620` (`0x0040ebf0`),
`CMonitor__ClearCurrentTrackedEntryFlag60` (`0x00414010`),
`CMonitor__Shutdown_Thunk` (`0x0046dbc0`),
`CMonitor__SampleHeightfieldNormalAtXY` (`0x0047ec60`),
`CMonitor__SpawnParticleEffectFromIndexedListInHeightBand` (`0x004ef120`),
`CMonitor__UpdateTrackedRenderPair` (`0x005078f0`).

## Callers (direct `E8` rel32, whole-image scan)

| Target | Call site | Pushes | Owner |
| --- | --- | --- | --- |
| `AddDeletionEvent` | `0x0040102a` | `esi` = the reader cell (`this` of SetReader) | `CGenericActiveReader__SetReader` |
| `AddDeletionEvent` | `0x00418f39` | `eax` = `[this+4]` reader cell; `ecx` = ctor arg | `CThing3rdPersonCamera__ctor` (CActiveReader ctor shape: `[cell]=to_read` then Add) |
| `AddDeletionEvent` | `0x00538a85` | `edi` = 0x11-byte listener node (`node[0]=listener`); `ecx` = listener | `CScriptEventNB__RegisterEventListener` |
| `DeleteDeletionEvent` | `0x0042d94d` | | `CController__dtor` |
| `DeleteDeletionEvent` | `0x004d69c5` | | `CRadarWarningReceiver__Update` |
| `DeleteDeletionEvent` | `0x0053880b` | the listener node | `CScriptEventNB__ClearListenerEntry` |
| `SetReader` | `0x0052f440` | `eax` = `rhs->vtable[+0x40]()` (thing*); `ecx` = `&CThingPtr+4` | `CThingPtrDataType__Print` (table name; body is assign) |

`SetReader` itself has 164 direct `E8` sites (engine-wide `CActiveReader` re-points). The three `AddDeletionEvent` sites are the only ones; the `RegisterEventListener` hit-path inlines the lazy-alloc + `AddToHead` and does not `E8` `0x00401040`.

So the `+4` set is the lifecycle behind both `CActiveReader` watches and named-event listener nodes: register with `AddToHead`, clear with `Remove` / `DeleteDeletionEvent`, and on monitor death zero the payload's first dword then free the set. `CSPtrSet__AddToHead` has 72 direct call sites and is the shared workhorse list.

## Script assign (`CThingPtr+4` is the reader)

Independently re-read 2026-08-18 from specimen `74154bfa…`.
`CThingPtrDataType` vtable `0x005e4df8[+0x14] = 0x0052f430` (table name Print):

```
esi = this
call [rhs->vtable+0x40]     ; thing*
push eax
lea ecx, [esi+4]            ; embedded CGenericActiveReader
call 0x00401000             ; SetReader
ret 4
```

`CThingPtrDataType` dtor `0x0052f570` inlines the same unlink (`[this+4]` is `mToRead`; `push &this+4`; `CSPtrSet__Remove([mToRead+4], reader)`) and does not call `DeleteDeletionEvent`. Clone `0x0052f470` writes `[clone+4] = [src+4]` and, if the thing has no set yet, lazy-allocs the 0x18-byte `CSPtrSet` (`MissionScript\..\Monitor.h` `0x0064ccb0`, line 94) then `AddToHead`s the clone's reader cell — the same Monitor.h:94 pattern, not an `E8` to `AddDeletionEvent`.

Pinned GPL `references/Onslaught/activereader.cpp` names the architecture
(`RemoveDeletionEvent(this)` / `AddDeletionEvent(this)` / `ToReadDied`
`{ mToRead = NULL }`) and is **not** the retail proof. Retail `SetReader`
inlines `CSPtrSet__Remove` instead of calling `DeleteDeletionEvent`.

## Open questions (cheapest falsifier first)

- CLOSED 2026-08-18 — the `AddDeletionEvent` `ret 4` dword is the pointer
  stored as `CSPtrSet` wrapper payload. Shutdown/Shutdown_Core write
  `dword [payload] = 0`. Measured identities: (1) `CGenericActiveReader*`
  (`SetReader`, camera ctor) so `mToRead` is cleared; (2) the 0x11-byte
  listener node (`RegisterEventListener` miss path) so `node[0]` (the
  listener) is cleared. No runtime probe required.
- The vtable `0x005d92d4`'s RTTI descriptor: CLOSED — COLOC `0x0060cbe0` at
  `0x005d92d0` (`vtable-4`) → TD `0x00622bd8` = `.?AVCMonitor@@`, with bases
  `CMonitor` and `IListener` (`.?AVIListener@@`). Script-cluster subclasses
  named by the same walk: `CEventFunction`, `IScript`, `CVM`,
  `CPostEventData`, `CScriptEventNB` (see `CScriptEventNB.cpp.md`). The
  vftable-cohort65 subclass census is CLOSED: of the 59 unique classes,
  exactly five derive from `CMonitor` (`CAnimation`, `CFearGrid`,
  `CHLCollisionDetector`, `CMessageBox`, `IScript`); the other 54 do not.
  Independently re-walked 2026-08-18 against pristine `74154bfa…` (every
  census.tsv `col_ptr` → COL → TD → CHD → BaseClassArray; 59/59 agree;
  receipt `local-lab/hermes-kanban-campaign-2026-08-18/cmonitor-census/`).
  A child's full-image count of 167 proper subclasses was **not** re-counted
  here.
- `CSPtrSet` 8-byte wrapper ownership: CLOSED 2026-08-18.
  `CSPtrSet__Initialise` (`0x004e59f0`) is the only writer of pool
  base `0x0083d134` / count `0x0083d138`. Sole `E8`:
  `CLTShell__InitializeRuntimeAndLoadCoreResources` `0x004efb58`
  pushes `0x9c40` (40000). `AddToHead` recycles `0x0083d130` or
  allocs 8 (`SPtrSet.cpp:0xb7`, increments `0x0083d13c`, prints
  `0x00632774`). `Clear` (`0x004e5c60`) returns the chain to that
  free list. `ClearAnyDynamicCreatedNodes` (`0x004e5990`) `Free`s
  overflow nodes — sole caller `CGame__Shutdown` `0x0046c9e9`.
  `CSPtrSet__Shutdown` (`0x004e5910`) `Free`s overflow + the pool
  block; `JMP` from `CLTShell__ShutdownRuntimeAndReleaseResources`.
  CMonitor death-walk `Free`s only the 0x18-byte set.
