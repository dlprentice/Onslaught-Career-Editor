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
| `0x0048b660` | `CInfluenceMapManager_T3_0048b660` | `83ec18 8d442404 56 8b742420 6a02 50 8bce e8face0b00 8b442408 25ffff0000 83e800 0f84b6000000 48 0f8537010000 …` | Reads a 16-bit selector (`and eax,0xffff`) after a two-byte fetch, then dispatches on 0 and 1 into distinct parse arms. MEDIUM: a tagged reader/parser; the tag meanings and the arms need a second witness. |
| `0x0048b7d0` | `CInfluenceMapManager_T3_0048b7d0` | `515356 8bf1 57 8b4608 85c0 894610 7404 8b00 eb02 33c0 85c0 8bc8 7420 6a01 e8bd0b0000 8b4610 8b4004 …` | Moves the `+0x08` list head into the `+0x10` cursor, then iterates calling a per-element routine with argument 1 and advancing through `+0x04` links. MEDIUM: a list sweep with a per-node call; the callee and the stop condition remain open. |
| `0x0048b8e0` | `CInfluenceMapManager_T3_0048b8e0` | `83ec30 53 8d5908 55 894c2410 56 8bcb e82cb4f7ff 33ed 3bc5 743a be9f860100 8bcb 89a89c000000 …` | Calls the `+0x08` init helper, then writes the influence defaults: zeroes `+0x9C/+0xA0/+0xA4/+0xA8/+0xB8` and seeds the `0x1869F` (100000) pair — the same shape as `ResetInfluence`. HIGH: a second initializer of the influence state; its extra prologue work remains open. |
| `0x0048bf70` | `CInfluenceMapManager_T3_0048bf70` | `515657 8bf9 8b5718 8d4f18 85d2 7404 8b32 … d94604 d82504865d00 d95604 d81d6c855d00 dfe0 f6c441 7515 …` | Walks the `+0x18` list; per node subtracts the constant at `0x005d8604` from the float at `+0x04` and compares against `0x005d856c` with the `C0|C3` mask (`test ah,0x41`). HIGH: an influence-decay pass using the same threshold `CalculateInfluence` compares against; the decay unit remains open. |
| `0x0048c000` | `CInfluenceMapManager_T3_0048c000` | `6aff 68b92f5d00 64a100000000 … 68a6010000 894c2414 681cd66200 6a20 6a0c b9f03d9c00 e8aad00b00 …` | SEH prologue with the `InfluenceMap.cpp` `__FILE__`/`__LINE__` block, then allocates **422** bytes (`0x1A6`) from pool `0x009c3df0`. HIGH: a constructor allocating a 422-byte influence-map node from the shared pool; the object layout beyond the allocation remains open. |

## Open questions (cheapest falsifier first)

- The 100000 seed in `ResetInfluence` and the two handled event ids (1000/1001)
  — a retained-trace field-write probe at `+0x9C`/`+0xAC` and an event-call
  probe through `0x0048c120` would name them.
- The decay constant at `0x005d8604` (subtracted per node in `0x0048bf70`)
  and the shared threshold at `0x005d856c` — read both floats and pin a focused
  parity test of one decay step against the influence accumulator.
- The `Load` content format — the large 0x3F0-byte frame and the init helper at
  the `+0x08` list are the next static targets.
- Virtual slot 1's allocation counterpart for `FreeObjectIfPresent`'s free loop.
