# Disposition of the 34 excluded .data pointer slots (vftable-cohort65)

Status: active finding — terminal disposition of the excluded cohort rows
Last updated: 2026-08-17
Evidence: MEASURED — every slot's 4-byte pointer and its `slot-4` anchor were
re-read from the pristine specimen with `tools/pe_read_va.py`; the table
consumers were named by whole-image operand scans (`tools/operand_scan.py`)
joined to the current `ghidra-function-name-table-2026-08-17.tsv`. Input rows
are the 34 `.data` members of
`local-lab/ghidra-cohort-framework/receipts/vftable-cohort-draft-manifest.tsv`
(the 99-row untyped pointer cohort).
Verdict: CLOSED — none of the 34 slots is a vtable. All 34 hold `.text`
function pointers belonging to five CRT or engine-owned function-pointer
tables; the vftable-cohort65 exclusion (their `slot-4` anchors fail the COL
walk) was correct, and the failure mode is now understood: `slot-4` is the
previous table entry's function pointer, never a Complete Object Locator.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Disposition groups

| Slots | Table base (length) | Consumer | Identity |
| --- | --- | --- | --- |
| `0x006222a0`, `0x006222a4`, `0x006225b4` | `0x00622004` (706) | CRT init-range walk (no direct address reference) | CRT dynamic-initializer array members |
| `0x006532ec`, `0x006532f0` | `0x006532e8` (3) | `CRT__RunStaticInitRangesWithOptionalCallback` (`0x0055dd7b` reads slot 0) | CRT static-init range/callback table; slots 1–2 point at `CTexture__NodePayloadNoOp` (`0x0059877e`) |
| `0x00653d38`, `0x00653d44` | singleton hook slots | `CRT__SetLocaleCategory` (`call [esi+0x653d38]` at `0x00565b81`); `0x00653d44` unreferenced | CRT locale hook slots defaulting to `CRT__ReturnZero` (`0x0056c05c`) |
| 15 slots `0x00656f38`–`0x00656fe4` | `0x00656f30` (46) | `CFastVB__InitDispatchTableByCpuFeature` (`mov edi/ebx, 0x656f30` at `0x00589280`/`0x005892b1`) | CFastVB CPU-feature dispatch table |
| 12 slots `0x0065700c`–`0x00657048` | `0x00656fec` (24) | `CTexture__InterpolateVec2CubicNormalized_Dispatch` (`call [0x656fec]` at `0x00575bf5`) | CTexture interpolation dispatch table |

The full 34-row table is tracked at
[`data34-slot-disposition-2026-08-17.tsv`](data34-slot-disposition-2026-08-17.tsv).

## Why the COL walk failed

The vftable-cohort65 gate reads the dword at `slot-4` as a Complete Object
Locator pointer, then `COLOC+0x0C` as the type descriptor and `TD+0x08` as the
mangled name. For every one of these 34 rows `slot-4` is the preceding table
entry — another `.text` function pointer — so the walk reads code bytes as a
COLOC and produces no class name. That is a correct refusal, not lost typing:
these are homogeneous function-pointer tables, and no class-identity label
belongs on them through this verb.

## Follow-up value

- The 15 `CFastVB` rows and 12 `CTexture` rows are real dispatch entries whose
  owning tables are now named; if rebuild parity later needs the individual
  fast-path or interpolation functions, the table membership is the anchor for
  a future naming cohort — not `SET_DATA_POINTER` vtable typing.
- The three CRT-init rows and four CRT hook rows are CRT machinery with no
  independent naming value; they stay structural rows.
