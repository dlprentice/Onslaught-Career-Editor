# PC/Xbox D3DX three-body current reconciliation

Date: 2026-08-14

Status: reviewed dated static reconciliation; one admitted-body semantic
refinement and two exact boundaries require current-geometry re-grounding
before a separate Ghidra admission ceremony.

Evidence: **MEASURED** — exact pristine PC bodies, exact Issue-7 byte copies,
later-Xbox single-range function boundaries, symbolic x87 formulas, the dated
8,280-function body ownership, loose-instruction coverage, and entry references.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
Issue-7 `bea.xbe`, SHA-256
`70eaed62abb7cd568e59f9a9a50e798ef67815fd72a02a1f881bf2bf68df027b`;
Issue-11 `bea.xbe`, SHA-256
`ac07835e4b8cf38312e672cb7dc17f28a732abbc05a5e4f1760aaa78a5377ed9`;
US-retail `default.xbe`, SHA-256
`e8adc9d6940ae1a5fa9fac0fe28e398bfffd01758c2740a536b930c37c83985b`.

Verdict: **THREE COMPLETE D3DX-COMPATIBLE PC BODIES REPRODUCED; ONE IS
ALREADY ADMITTED AND TWO REMAIN STRUCTURALLY UNADMITTED.** The sealed cohort
contains 357 bytes / 129 instructions. The dated 8,280-function evidence already
owns `0x00576b4d..0x00576bba` exactly. The other two bodies remain 248 bytes /
92 instructions of contiguous loose code with no overlap against any of the
8,400 then-current body ranges. This finding changes no Ghidra project or census.

## Current settlement

The machine-readable result is
[`d3dx-gap-cohort-current-reconciliation-2026-08-14.tsv`](d3dx-gap-cohort-current-reconciliation-2026-08-14.tsv),
1,651 bytes, SHA-256
`8d6149eed095426e59a1769b5d78b3fbce645027e6a0786f8b429907ca1931ac`.

| PC range | Body | Static identity | Current disposition |
|---|---:|---|---|
| `0x00576b4d..0x00576bba` | 109 B / 37 insns | `D3DXMatrixTranspose`-compatible | exact current one-range function `FUN_00576b4d`; semantic refinement only |
| `0x00595fc9..0x00596028` | 95 B / 35 insns | `D3DXVec3TransformNormal`-compatible | fully decoded loose body; not a saved function |
| `0x00596028..0x005960c1` | 153 B / 57 insns | `D3DXVec4Transform`-compatible | fully decoded loose body; not a saved function |

The first row consumes the existing
[external-table boundary](external-table-gap-function-boundaries-2026-08-13.md)
and its completed 79-function live promotion. Its exact body hash is
`82f8b720...ec110`, and its one current range is byte-for-byte identical. The
current gap-reference export deliberately omits targets that are already
functions, so the ledger shows zero *current gap* references; the dated
external-table owner retains the defined-data pointer at `0x006570e4`.

The second and third rows lie inside the current
`0x00595f09..0x005960c1` `LOOSE_INSTRUCTIONS_ONLY` gap. They cover 35 and 57
contiguous instruction rows respectively, with no holes or body overlap.
`CFastVB__InitMathDispatchTable` references their entries from `0x0059636f`
and `0x00596345`, `0x00596357`, `0x0059637d`. Those references support entry
status; they do not by themselves authorize creating functions in Ghidra.

If a later isolated scratch/apply/readback ceremony admits only those two
bodies, the structural projection would move from 8,280 functions / 8,400
ranges / 1,794,212 owned `.text` bytes to 8,282 / 8,402 / 1,794,460. The
remaining unowned total would become 134,657 bytes, or 93.019759818% owned.
These are prospective arithmetic values, not the current census.

## Cross-build boundary proof

Each PC body has an exact Issue-7 copy and an exact later-Xbox `D3DX` copy in
both Issue-11 and US retail. Issue-7 supplies bytes only. The Issue-11 and US
inventories independently place a one-range function entry at each later copy:

| PC entry | Issue-7 exact copy | Issue-11 function | US-retail function |
|---|---:|---:|---:|
| `0x00576b4d` | `0x001ae8a7` | `0x001beaa7` | `0x001bea07` |
| `0x00595fc9` | `0x001ae4aa` | `0x001be6aa` | `0x001be60a` |
| `0x00596028` | `0x001ae744` | `0x001be944` | `0x001be8a4` |

The compatibility identities are also formula-bound. The first routine copies
all 16 floats from a 4x4 input matrix into transposed output positions. The
second multiplies `(x,y,z,0)` by a 4x4 matrix and writes three floats. The third
multiplies a four-float vector by a 4x4 matrix and writes four floats. All three
return the output pointer and use callee cleanup matching their two- or
three-argument contracts. These observations match Microsoft's documented
[`D3DXMatrixTranspose`](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dxmatrixtranspose),
[`D3DXVec3TransformNormal`](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dxvec3transformnormal),
and
[`D3DXVec4Transform`](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dxvec4transform)
contracts.

## Reproduction

The retained cross-build package is
`local-lab/d3dx-gap-cohort-current8280-20260814-v1`. Its original sealed
manifest is 3,437 bytes, SHA-256
`c493202f367fdcd4e11059dc731f2588646e6e122fbcc3690bb39bcfb1719400`;
the cross-build receipt is 7,545 bytes, SHA-256
`0865a4ed4669426ad0cc347044910ff7caed9da413e4e95d22f187a82faf9e88`.
The current-state reducer first replays that sealed proof, then exact-requires
the current name projection, 8,400 body ranges, loose instructions, inbound
references, and two byte-identical ownership/gap-accounting replicas.

The current reducer is 16,310 bytes, SHA-256
`eaf1d610a04c3908b9bd99142752a6e15e13dbc6bcb24efe31323cca8d99154e`.
Its 8,382-byte receipt has SHA-256
`ce3e210427a5675e3ab37ad112f3dea1fd5433e178746888fc0a479ef08a59fa`
and records `ghidraMutation=false`. Two saved verifies from distinct working
directories reproduced:

```text
D3DX_GAP_CURRENT_VERIFIED sealed=3 admitted=1 missing=2 missingBytes=248
```

## Claim boundary

Promoted here:

- three complete PC boundaries and exact named cross-build coordinates;
- exact body sizes, instruction counts, hashes, formulas, cleanup, and
  output-pointer behavior;
- compatibility-scoped D3DX semantic classifications;
- the current one-admitted/two-missing disposition.

Not promoted here:

- an original linker, private C++, or precise upstream-version symbol;
- a name, signature, comment, tag, grade, or new Ghidra function;
- Issue-7 function boundaries;
- runtime reachability, dispatch selection, numerical corner-case parity,
  source equivalence, or rebuild behavior.

The two missing bodies require the normal isolated scratch validation,
recoverable backup, dry-run/apply/readback, rollback and containment controls,
independent review, and a separately authorized live promotion. This finding
left its then-current structural census at exactly 8,280. The live/tracked
project has since advanced independently to 8,304 functions; the two candidate
bodies must be rechecked against that exact geometry before any promotion.
