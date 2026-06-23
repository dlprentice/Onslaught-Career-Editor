# Ghidra MemoryManager Tail / CDXMemoryManager Wave439 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra name/signature/comment/tag correction

## Summary

Wave439 extended the MemoryManager correction through thirteen tail and wrapper targets. The pass corrected stale `CDXEngine`, generic `CMemoryManager`, and `OID` owner labels into source-parity `CMemoryHeap`, `CMemoryManager`, `CMemoryBlock`, and `CDXMemoryManager` names where static retail evidence and Stuart source agree.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004a1390` | `CMemoryHeap__ctor` | Called by `CDXMemoryManager__ctor` for the default, dump, thing, and sound heap members; creates the retail heap mutex/HANDLE at `+0x8bc`. |
| `0x004a1570` | `CMemoryHeap__FreeTiny` | Checks `mem` against the tiny heap range at `+0x8c0..+0x8c8` and pushes the 16-byte block onto the `+0x8c4` tiny free chain. |
| `0x004a1f60` | `CMemoryHeap__OutputStats` | Formats per-heap memory statistics, builds `data\Memory\<filename>`, and writes through `CDXMemBuffer`. |
| `0x004a2190` | `CMemoryHeap__PrintStats` | Emits per-heap statistics through the debug font path used by `CDXMemoryManager__PrintStats`. |
| `0x004a2460` | `CMemoryHeap__LogStats` | Logs nonzero per-type heap statistics through console/trace output. |
| `0x004a2660` | `CMemoryHeap__DumpMap` | Serializes heap block-map data and validates block sentinels before writing the dump buffer. |
| `0x004a2a20` | `CMemoryManager__FlagAsBaseSet` | Iterates heap blocks and marks allocated entries with the base-set bit. |
| `0x004a2a80` | `CMemoryManager__DumpMemory` | Builds numbered memory-dump filenames under `MemoryDumps` and dispatches `CMemoryHeap__DumpMap`. |
| `0x004a2ff0` | `CMemoryBlock__SetBaseSet` | Sets or clears bit 1 in the memory-block size/flag field. |
| `0x00548d70` | `CDXMemoryManager__ctor` | Constructs the DX memory manager wrapper, invokes `CMemoryHeap__ctor`, and initializes 129 memory-type name slots. |
| `0x00549220` | `CDXMemoryManager__Free` | Frees through `CMemoryHeap__FreeTiny` when possible, otherwise falls back to `CMemoryHeap__Free`; this is not OID object freeing. |
| `0x00549290` | `CDXMemoryManager__PrintStats` | Iterates heaps and dispatches `CMemoryHeap__PrintStats` with heap numbering. |
| `0x005492b0` | `CDXMemoryManager__OutputStats` | Iterates heaps and dispatches `CMemoryHeap__OutputStats` for the supplied filename. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| Headless `ApplyMemoryManagerWave439.java` dry/apply/verify | PASS | Dry found `13` targets with `would_rename=13`; apply reported `updated=13`, `renamed=13`, `missing=0`, `bad=0`; verify dry reported `updated=0`, `skipped=13`, `would_rename=0`, `missing=0`, `bad=0`. |
| Post-apply metadata/tag/xref/instruction/decompile read-back | PASS | Verified `13` metadata rows, `13` tag rows, `887` xref rows, `585` instruction rows, and `13` target decompile exports. |
| `py -3 -m py_compile tools\ghidra_memorymanager_wave439_probe.py tools\ghidra_memorymanager_wave439_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_memorymanager_wave439_probe_test.py` | PASS | Focused tests passed `4/4`. |
| `py -3 tools\ghidra_memorymanager_wave439_probe.py --check --json` | PASS | Focused probe returned `status: PASS` for all `13` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1831` commented functions, `4224` commentless functions, `1787` undefined signatures, and `1740` `param_N` signatures. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1831`
- Commentless function objects: `4224`
- `undefined` signatures: `1787`
- Signatures still using `param_N`: `1740`

Telemetry-only proxies are comment-backed `1831/6055 = 30.24%` and strict clean-signature `1769/6055 = 29.22%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime allocation/dump behavior; exact concrete `CMemoryHeap` / `CMemoryBlock` / `CDXMemoryManager` layouts beyond observed offsets; exact local variable names/types; exact Steam-vs-source mutex lifetime; exact destructor/tag-list cleanup ownership for adjacent helpers; full `MemoryManager.cpp` coverage; source-to-retail rebuild parity; BEA launch behavior; game patching; or runtime gameplay behavior.
