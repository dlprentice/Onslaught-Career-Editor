# CInfluenceMap / CInfluenceMapManager function map

Status: active static function map
Last updated: 2026-08-17
Source File: `C:\dev\ONSLAUGHT2\InfluenceMap.cpp` (named by the shipped image at `0x0062d61c`, and by the SEH `__FILE__` pointer `0x005d2f94` in `Load`) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — every byte below was re-read from the pristine specimen at
file offset VA − 0x400000. The CInfluenceNode map (`CInfluenceNode.cpp.md`)
covers the node class itself; this page covers the map/manager around it.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048b010` | `CInfluenceMapManager__Load` | `6aff 68942f5d00 64a100000000 … 81ecf0030000 53555657 8bf9 897c2438 8d6f08 8bcde8e1bcf7ff …` | SEH prologue whose `__FILE__`/`__LINE__` block points at `0x005d2f94` (`C:\dev\ONSLAUGHT2\InfluenceMap.cpp`), then a 0x3F0-byte local frame; initializes the manager list at `this+0x08` through a bounded init helper. HIGH on the shape and file identity; the loaded content and its format remain open. |
| `0x0048afb0` | `CInfluenceMap__FreeObjectIfPresent` | `53 8bd9 56 57 8d7b08 8b07 85c0 894708 7417 8b30 … 8b06 8bce ff5008 ebe0 8d7b18 …` | Walks the object list head at `this+0x08`, re-links the successor, calls each element's virtual slot 1 (`call [eax+8]` — the destructor thunk), and repeats; a second list at `this+0x18` follows. HIGH that it frees list elements via their virtual destructor; the allocation side of slot 1 remains open. |
| `0x0048b620` | `CInfluenceMap__ResetInfluence` | `33c0 89819c000000 8981a0000000 8981a4000000 8981a8000000 8981b8000000 b89f860100 8981ac000000 8981b0000000 …` | Zeroes the accumulator fields at `+0x9C`, `+0xA0`, `+0xA4`, `+0xA8`, `+0xB8` and seeds `+0xAC` and `+0xB0` with `0x1869F` (100000). HIGH: this is the reset counterpart of `CalculateInfluence`'s `+0x9C`/`+0xA4` sum; the 100000 seed's unit and meaning remain open. |
| `0x0048c120` | `CInfluenceMap__VFunc_0_0048c120` | `8b442404 5356 8bd9 0fbf4004 2de8030000 0f847d010000 48 0f848a000000 48 0f8578010000 8b5318 8d4b18 …` | Reads the int16 event id at `arg+0x04` and dispatches on `id−1000` and `id−1001`, operating on the list at `this+0x18`; slot 0 of the vtable. MEDIUM: it is a two-event handler over the influence lists; the event semantics and the other arms need a second witness. |

## Open questions (cheapest falsifier first)

- The 100000 seed in `ResetInfluence` and the two handled event ids (1000/1001)
  — a retained-trace field-write probe at `+0x9C`/`+0xAC` and an event-call
  probe through `0x0048c120` would name them.
- The `Load` content format — the large 0x3F0-byte frame and the init helper at
  the `+0x08` list are the next static targets.
- Virtual slot 1's allocation counterpart for `FreeObjectIfPresent`'s free loop.
