# External-table gap function-boundary preparation

Date: 2026-08-13

Status: reviewed structural preparation; no Ghidra or current function-census
mutation.

Verdict: **SUPPORTED AS 79 DISTINCT FUNCTION-BOUNDARY CANDIDATES PENDING THE
NORMAL SCRATCH-ADMISSION GATE.** The 51 current
`EXTERNAL_TABLE_TARGET_CANDIDATE` gaps are fully dispositioned: 46 contain 78
pairwise-disjoint callable starts, while five are fragments of existing
functions or shared blocks. One adjacent IJG callback adds the 79th start.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
comparison PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

Evidence: **MEASURED** — the 79-row boundary ledger is
[`external-table-gap-function-boundaries-2026-08-13.tsv`](external-table-gap-function-boundaries-2026-08-13.tsv),
30,020 bytes, SHA-256
`4293ebb936639299301985f128728b127ca60014693871a981d2324d47f2044f`.
The complete 51-row input disposition is
[`external-table-gap-dispositions-2026-08-13.tsv`](external-table-gap-dispositions-2026-08-13.tsv),
4,606 bytes, SHA-256
`282400a5d3e9ac315ce730319ec0e62468f2547a13b5f2b4d5e4784b8411344c`.
Its `<NONE>` sentinel preserves the five empty callable-start sets without
trailing-field ambiguity; the sealed source table is 4,576 bytes, SHA-256
`8cbef787a9fd26cb5c1634577d059c455f075974507975a50a0898f6436f952f`.

The machine-local analysis owner is
`local-lab/external-table-gap-sweep-20260813-v1/REPORT.md`, 12,061 bytes,
SHA-256
`af321b296dbe6b36d361b2f77e54b2eb6814df5e24ae1f8f0d12b60437d55aa5`.
Its independently replayed candidate, disposition, provider, and promotion
outputs have SHA-256 values `d3d68cf7...5707f`, `8cbef787...952f`,
`dfdfaabf...647b`, and `09e5a732...93a`. The bounded tracked-projection receipt
is `local-lab/external-table-gap-tracked-prep-20260813-v1/tracked-prep.ready.json`,
989 bytes, SHA-256
`a687d113f4892ffa170ebcac5330cb422d07502f5adc6f3849bdaa161f85f575`.

## Exact result

The 79 proposed bodies total 9,234 bytes and 3,319 instructions. They have:

- zero overlap with one another;
- zero overlap with all 8,287 saved body ranges belonging to the current
  8,170-function Ghidra inventory;
- a complete normalized PC-demo twin for every row: 45 globally unique body
  matches, 33 equal-delta matches bracketed by mapped neighbors, and one
  initializer-slot match;
- complete half-open body ranges and pristine-byte hashes in the ledger.

If all 79 pass the separate Ghidra admission gate, the saved-function lower
bound becomes 8,249. This report does **not** make that census change.

| Preparation rank | Rows | Meaning |
|---|---:|---|
| P0 | 12 | ten exact D3DX public-body joins, one D3DX N-patch lineage join, and one IJG v6b source-contract join |
| P1 | 20 | 18 vtable/descriptor callbacks and two bounded structural CRT helpers |
| P2 | 47 | conservative boundary-only initializers and D3DX dispatch entries |

Independent review corrected one source-lane overreach without changing this
partition. `0x0058862e` is a five-vtable shared scalar-deleting wrapper for the
YUV/packed-pixel codec family, not a `CFile` destructor. Its callee has the same
13-instruction shape as official `CCodecYUV::~CCodecYUV`; the provider PDB has
five class aliases on the family vtable and ten scalar/vector-deleting public
aliases for those same five classes on the shared wrapper body, matching the
five BEA table references. The tracked ledger therefore uses
`D3DX_COMPAT__CCodecYUVFamily__SharedScalarDeletingDtor` and treats the sealed
source promotion spelling as superseded evidence, not authority.

The ten exact D3DX bodies are unique post-hotpatch matches to official
D3DX9-v24 DLL/PDB publics. Their names are compatibility-qualified; they do
not establish BEA's original linker symbols or the precise D3DX version linked
by the game. `0x005762dd` also has the independently reviewed portable
[`D3DXVec4Cross` boundary receipt](d3dx-vec4cross-crossbuild-boundary-2026-08-13.md)
and must consume that existing proof rather than be promoted twice.

`0x00588d63..0x00589094` is a 817-byte, 315-instruction
`D3DX_COMPAT__c_D3DXPSGPTessellateNPatch` candidate. Its immediately preceding
saved helper is an exact 157-byte copy of D3DX's PDB-named
`CalculateEdgeControlPoint`; the two N-patch variants call that helper six
times and return with `ret 0x20`.

`0x0059f170..0x0059f25c` is a 236-byte, 105-instruction
`LIBJPEG6B__write_tables_only` candidate. Its callback-table slot, emitted
marker sequence, exact demo twin, and official IJG v6b `jcmarker.c` contract
agree. This is a provider-qualified private-source identity, not a BEA-authored
symbol claim.

## Five rows that are not new functions

The disposition ledger prevents table-like bytes from manufacturing false
entries:

| Gap | Disposition |
|---|---|
| `0x00417347..0x00417390` | continuation of the preceding `CBuilding` virtual body |
| `0x0045004b..0x00450090` | continuation of `CFEPBEConfig__UpdateTransitionTimers` |
| `0x0046001d..0x00460050` | continuation of `CFEPGoodies__TransitionNotification` |
| `0x004c4145..0x004c41e4` | omitted middle range of `CPDTrail__VFunc_19_004c4100` |
| `0x00561453..0x00561530` | x87 dispatch/shared-tail blocks reached from existing `__trandisp2` |

The first four rows need body-range correction, not new functions. The x87
row contains valid internal table targets whose inherited FPU/frame state
prevents treating them as independent ABI entries.

## Admission boundary

The ledger is a preparation manifest, not a mutator authority. Before any
canonical Ghidra change, a target-specific or reusable manifest runner must
still reproduce:

1. the exact retail specimen, 79 entries, body ranges, bytes, instructions,
   and demo-normalized twins;
2. zero target overlap and exact equality of every current non-target function
   row;
3. two isolated positive replicas, separate readbacks, rollback and
   post-inner compensation controls, and external-output containment controls;
4. a recoverable PRE backup, one bounded live apply, separate live readback,
   POST backup, and exact live/tracked/backup equality;
5. compatibility-qualified names only where the provider join is explicitly
   present; P2 rows remain conservative until stronger identity evidence
   exists.

No function, name, signature, comment, tag, body range, grade, generation,
runtime contract, or rebuild behavior changes merely by tracking this
preparation. Any body mismatch, overlap, demo mismatch, provider conflict, or
non-target collateral falsifies the affected admission row.
