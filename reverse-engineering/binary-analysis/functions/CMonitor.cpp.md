# CMonitor / CSPtrSet function map

Status: active static function map
Last updated: 2026-08-17
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
| `0x00401040` | `CMonitor__AddDeletionEvent` | `6aff 68260f5d00 64a100000000 50 64892500000000 51 57 8bf9 8b4704 85c0 753f 56 6a18 68802b6200 6a5e 6a10 b9f03d9c00 e86a801400 8bf0 … 8bce e8b1470e00 … 897704 … 8b442418 8b4f04 50 e8d4490e00 … c20400` | Installs an SEH frame (second slot `0x005d0f26`, whose bytes form a jump thunk `mov eax,0x00619de0; jmp`). If `[this+4]` is null it lazily allocates **0x18** bytes via `CDXMemoryManager__Alloc` (this = the global manager `0x009c3df0`, `__FILE__` `0x00622b80` = `Monitor.h`, line `0x5e` = 94), runs `CSPtrSet__Init` (`0x004e5840`) on it, and stores it at `[this+4]`; then `mov ecx,[this+4]; push arg; call CSPtrSet__AddToHead` (`0x004e5a80`) and `ret 4`. HIGH: one lazy 0x18-byte `CSPtrSet` per monitor, at field `+4`, holding the passed argument. |
| `0x0042d9b0` | `CMonitor__DeleteDeletionEvent` | `8b4904 85c9 740a 8b442404 50 e80f820b00 c20400` | If `[this+4]` is non-null, `CSPtrSet__Remove` (`0x004e5bd0`) the argument; `ret 4`. HIGH: the symmetric pair to `AddDeletionEvent`, same field and argument shape. |
| `0x00466120` | `CMonitor__ctor` | `8bc1 c7400400000000 c700d4925d00 c3` | Zeroes `[this+4]` (the deletion-event set) and installs the vtable `0x005d92d4`. HIGH. |
| `0x00419a20` | `CMonitor__scalar_deleting_dtor` | `56 8bf1 e818120a00 f644240801 740b 56 b9f03d9c00 e8e6f71200 8bc6 5e c20400` | Calls `CMonitor__Shutdown` (`0x004bac40`), then if the `flags & 1` deleting flag is set frees `this` through `CDXMemoryManager__Free` (manager `0x009c3df0`); `ret 4`. HIGH. |
| `0x004e5840` | `CSPtrSet__Init` | `8bc1 33c9 8908 894804 89480c c3` | Zeroes `+0` (head), `+4` (tail), and `+0xC` (count) — the 0x18-byte object a monitor allocates. HIGH. |

## Family roster (named in live Ghidra, not yet byte-mapped here)

`CMonitor__UpdateSoundEventPlaybackForReader` (`0x00409950`),
`CMonitor__ToggleAttachedObjectFlag300` (`0x0040e840`),
`CMonitor__UpdateTrackedList_59C` (`0x0040e940`),
`CMonitor__FlushTrackedList_1D4` (`0x0040eb50`),
`CMonitor__UpdateTrackedList_620` (`0x0040ebf0`),
`CMonitor__ClearCurrentTrackedEntryFlag60` (`0x00414010`),
`CMonitor__Shutdown_Thunk` (`0x0046dbc0`),
`CMonitor__Shutdown` (`0x004bac40`),
`CMonitor__Shutdown_Core` (`0x004bacb0`),
`CMonitor__SampleHeightfieldNormalAtXY` (`0x0047ec60`),
`CMonitor__SpawnParticleEffectFromIndexedListInHeightBand` (`0x004ef120`),
`CMonitor__UpdateTrackedRenderPair` (`0x005078f0`).

## Callers (direct `E8` rel32, whole-image scan)

| Target | Call site | Owner |
| --- | --- | --- |
| `AddDeletionEvent` | `0x0040102a` | `CGenericActiveReader__SetReader` — the `CActiveReader<CMonitor>` re-point path |
| `AddDeletionEvent` | `0x00418f39` | `CThing3rdPersonCamera__ctor` |
| `AddDeletionEvent` | `0x00538a85` | `CScriptEventNB__RegisterEventListener` |
| `DeleteDeletionEvent` | `0x0042d94d` | `CController__dtor` |
| `DeleteDeletionEvent` | `0x004d69c5` | `CRadarWarningReceiver__Update` |
| `DeleteDeletionEvent` | `0x0053880b` | `CScriptEventNB__ClearListenerEntry` |

So listener registration adds a deletion event into the monitor's `+4` set,
clearing or destruction removes one, and `CActiveReader::SetReader` re-points
the old target — the lifecycle behind the event manager's `mToCall` readers.
`CSPtrSet__AddToHead` itself has 72 direct call sites and is the shared
workhorse list for these pointer sets.

## Open questions (cheapest falsifier first)

- The exact meaning of the argument pushed into `CSPtrSet__AddToHead` (the
  `ret 4` dword): a retained-trace probe of `RegisterEventListener` →
  `AddDeletionEvent` would name it.
- The vtable `0x005d92d4`'s RTTI descriptor and the monitor's derived classes
  (the `CMonitor` subclasses among the 59 vftable-cohort65 classes).
- `CSPtrSet` node ownership: `CSPtrSet__ClearAnyDynamicCreatedNodes` at
  `0x004e5990` separates dynamic from static nodes — which pool owns each.
