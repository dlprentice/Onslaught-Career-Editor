# PC demo/retail MissionScript opcode-factory lineage

Status: complete, bounded cross-build closure
Last updated: 2026-08-11
Evidence: MEASURED — exact specimen hashes, independently mapped caller and
callee pairs, complete body-relative x86-32 decode, raw and normalized byte
comparison, both 27-entry jump tables, and strict RTTI/vtable identities;
UNKNOWN — runtime opcode execution, allocator/global contents, original source
identity, and reconstruction parity.
Verdict: retail `0x0052D3D0 CAsmInstruction__SpawnFromOpcode` and demo
`0x0052DAC0` implement the same bounded static factory contract. The row that
the first whole-function census left `not_compared` is an instruction-accounting
false negative, not an edition-specific MissionScript change. This closes one
of the ten remaining address-mapped bodies; nine CRT/FPU bodies remain.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, 2,510,848 bytes, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

The machine-readable 27-case result is
[`pc-demo-retail-asm-instruction-lineage-2026-08-11.tsv`](pc-demo-retail-asm-instruction-lineage-2026-08-11.tsv),
4,632 bytes, SHA-256
`3236f485b68bf6533bf0994471e45738eb611f3c573ceb95db780e99bc1ffc29`.
The ignored reproducer is
`local-lab/pc-demo-retail-asm-instruction-lineage-20260811-v1/analyze.py`,
24,587 bytes, SHA-256
`c32465044c1106993ff4a8cc337184337a5e1b30eec1f499fe36df279ff32d21`;
its result receipt has SHA-256
`20ddccbd6d7725b1658a1199df9dda252b01cd2ae582d541f3892d6fa18123bd`.

## Why the original map abstained

The tracked address map correctly selected demo `0x0052DAC0` through one
corresponding direct caller, but retained
`UNANIMOUS_DIRECT_TRANSFER_CHANGED_BODY`, `body_normalized_equal=false`, and
`not_compared` byte fields. Its input Ghidra body has 1,297 bytes and 401
instruction rows. Those rows do not form one gapless linear stream around the
last opcode case: the raw bytes at retail `0x0052D8BD` encode the final vtable
store, while the export resumes inside that immediate at `0x0052D8C0`.

Fresh decode starts at each mapped entry and consumes every byte through the
return at retail `0x0052D8E0` / demo `0x0052DFD0`. Each body is 1,297 bytes and
400 gapless linear instructions. The comparison is exact at every relative
instruction boundary:

| Measurement | Result |
| --- | ---: |
| Relative instruction offsets, sizes, and mnemonics | 400 / 400 equal |
| Normalized-different instructions | 0 |
| Raw-different instructions | 113 |
| Raw-different bytes | 182 |
| Retail raw body SHA-256 | `8327fd561db15c9174e14402f81d6929951821c50a115a983af1b02d7bee84a3` |
| Demo raw body SHA-256 | `38f3c9339926e9241d5d851929a29959f2c9f61aa9c2657e1f2aeaeb3d3ab0d6` |
| Shared normalized SHA-256 | `ecd3d9f764fdecdd634675297991582a3730d47c349ead4211287191f16eef3c` |

Normalization masks only Capstone-reported encoded immediate and displacement
spans. All 182 raw differences are therefore relocated code, jump-table,
source-string, allocator/global, vtable, or diagnostic operands; no opcode,
prefix, ModRM/SIB byte, instruction length, or control-flow shape changes.

## Factory contract preserved in both builds

The caller pair is retail `0x00538EC0 CMissionScriptObjectCode__ctor` and demo
`0x005394D0`. Both call the mapped factory once at relative offset `+0x7E`.
Inside the factory, both builds:

1. call the mapped `CDXMemBuffer__Read` pair at relative offset `+0x0E` to read
   one four-byte attribute;
2. accept serialized opcodes `0x00..0x1A` and dispatch through 27 unique table
   targets with the same relative target sequence;
3. allocate 12 bytes through the mapped `CDXMemoryManager__Alloc` pair, using
   allocation type `0x1A`, source path
   `C:\dev\ONSLAUGHT2\MissionScript\AsmInstruction.cpp`, and consecutive source
   lines 87 through 113;
4. on allocation success, store the read attribute at instruction offset
   `+0x04`, install the opcode-specific vtable, and return the allocated
   pointer;
5. take a shared null-return path when allocation fails; and
6. for an opcode above `0x1A`, call the mapped `CConsole__Printf` pair with the
   identical shipped diagnostic `FATAL ERROR: uknown instruction in spawn`,
   then return null.

The relative jump-target table has SHA-256
`79fee89f5b9bda3d33e9d9ddcad6287ee024adabff5ea54355228ca2c1cb7fed`.
The three direct callee bodies are independently address-mapped and
normalized-identical:

| Role | Retail | Demo |
| --- | --- | --- |
| Attribute read | `0x00548570 CDXMemBuffer__Read` | `0x00548C00` |
| Allocation | `0x005490E0 CDXMemoryManager__Alloc` | `0x00549770` |
| Unknown-opcode diagnostic | `0x00441740 CConsole__Printf` | `0x004417A0` |

## All 27 instruction classes now have strict identities

Every vtable installed by the factory belongs to one strict MSVC RTTI class in
both specimens, and each paired vtable has three corresponding slots. Slot 0
is the executor entry. All 27 executor selections map cross-build with zero
normalized differences; there are 26 unique executor pairs because `NOP` and
`LABEL` share the same no-op body.

This resolves the eight placeholders retained by the earlier static schema:

| Opcode | Strict RTTI class | Retail slot-0 executor | Demo slot-0 executor |
| ---: | --- | --- | --- |
| `0x06` | `CInstructionOP_POP` | `0x0052E2F0` | `0x0052E910` |
| `0x0E` | `CInstructionOP_REMOVE_TOP` | `0x0052E320` | `0x0052E940` |
| `0x12` | `CInstructionOP_JMPNE` | `0x0052E990` | `0x0052EFB0` |
| `0x14` | `CInstructionOP_JMP` | `0x0052E9B0` | `0x0052EFD0` |
| `0x15` | `CInstructionOP_GETTOP` | `0x0052E9C0` | `0x0052EFE0` |
| `0x16` | `CInstructionOP_POINTER` | `0x0052EA10` | `0x0052F030` |
| `0x19` | `CInstructionOP_CALLLOCAL` | `0x0052EC40` | `0x0052F260` |
| `0x1A` | `CInstructionOP_PUSHPC` | `0x0052E0A0` | `0x0052E6C0` |

The class and executor identities are proven static facts. Their names do not
by themselves prove each executor's complete runtime stack effect, so the
schema keeps those eight behaviors explicitly open.

## Boundary and next use

This result proves the factory's static input read, opcode range and order,
allocation arguments, instruction attribute offset, class selection, direct
callee pairing, visible failure branches, and diagnostic string for the two named
specimens. It does not prove allocator or console-global contents, hidden ABI,
runtime MissionScript execution, original source equivalence, malformed-buffer
behavior outside the visible paths, or rebuild parity.

The first map remains immutable evidence of why its method abstained. This
lineage report is the narrower second-pass closure. The remaining
address-mapped queue is now the coherent nine-function CRT/FPU cohort and
should be attacked with x87/control-word semantics rather than another generic
normalized-signature pass.
