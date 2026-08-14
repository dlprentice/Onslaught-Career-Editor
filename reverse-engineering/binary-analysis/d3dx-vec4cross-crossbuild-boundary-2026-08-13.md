# PC D3DX four-vector-cross helper boundary

Status: active, bounded static recovery
Date: 2026-08-13
Evidence: MEASURED — exact pristine PC/Issue-7/Issue-11/US-retail body
bytes, exact x86 decode, a PC defined-data entry pointer, and independent
Issue-11 and US-retail single-range `D3DX` function inventories; UNKNOWN —
original linker symbol, runtime call provenance, and rebuild parity
Verdict: PC `0x005762dd..0x005763cd` is one complete 240-byte / 97-instruction
function body. Its four-argument arithmetic and `D3DX` section lineage support
a D3DXVec4Cross-compatible classification, not an original symbol claim.
Specimen: pristine PC `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
Issue-7 `bea.xbe`, SHA-256
`70eaed62abb7cd568e59f9a9a50e798ef67815fd72a02a1f881bf2bf68df027b`;
Issue-11 `bea.xbe`, SHA-256
`ac07835e4b8cf38312e672cb7dc17f28a732abbc05a5e4f1760aaa78a5377ed9`;
US-retail `default.xbe`, SHA-256
`e8adc9d6940ae1a5fa9fac0fe28e398bfffd01758c2740a536b930c37c83985b`.

This resolves one concrete part of the current PC `.text` residual
`0x0057629d..0x005763da`. It does not change a Ghidra project and does not
assert an original linker or C++ symbol.

## Result

The pristine PC bytes at `0x005762dd..0x005763cd` are one complete body:

- 240 bytes and 97 exactly decoded x86 instructions;
- prologue at `0x005762dd`;
- terminal `RET 0x10` at `0x005763ca..0x005763cd`;
- body SHA-256
  `a2e2615025549008476a59cac24f5cf251b89d617ed71c3cf38dafb396767df3`;
- one defined-data pointer at `0x00657090` targets the entry.

The same 240 bytes occur exactly in every Xbox specimen, twice per image:

| Build | `.text` copy | `D3DX` copy | Boundary state |
| --- | ---: | ---: | --- |
| Issue-7 | `0x0004ea8a..0x0004eb7a` | `0x001afd71..0x001afe61` | exact body copies; no Issue-7 function boundary inferred |
| Issue-11 | `0x0004fcba..0x0004fdaa` | `0x001bff71..0x001c0061` | `D3DX` copy is a current one-range Ghidra function: 240 bytes / 97 instructions |
| US retail | `0x0004fcba..0x0004fdaa` | `0x001bfed1..0x001bffc1` | `D3DX` copy is a current one-range Ghidra function: 240 bytes / 97 instructions |

All seven PC/Xbox copies have the same body hash. The two later Xbox `D3DX`
inventories independently place the function entry at the first byte and the
next function boundary immediately after the final return. This upgrades the
PC subrange from a merely prologue-like code envelope to a specimen-bound
function boundary.

## Semantic limit

The body takes four stack arguments, treats the last three as four-float input
vectors, writes four float results through the first argument, and returns
with `RET 0x10`. Its determinant/cross-product arithmetic and the two later
copies' `D3DX` section ownership match
[Microsoft's four-argument `D3DXVec4Cross` contract](https://learn.microsoft.com/zh-cn/windows/win32/direct3d9/d3dxvec4cross).
The supported label is therefore **D3DXVec4Cross-compatible helper**. This is a
behavioral/section classification, not proof that Microsoft or the game linked
this address with that original symbol name.

## Reproduction receipt

The checkout-portable ignored receipt is
`local-lab/xbox-pc-sparse-oracle-20260813-v1/d3dx-vec4cross-crossbuild.portable-v4.ready.json`,
4,459 bytes, SHA-256
`f0ef1245b37df33282e929ccd624f0d1ef74a0e219ae4b8d7976120995c0fc3e`.
It reanalyzes the named specimens rather than trusting saved verdict booleans.
The seven-row output is 2,491 bytes, SHA-256
`ce666e062ecb4dd59b17ae6a78821ae6edf83c8ad2596656a75fcfe08525b5fe`.
The active receipt contains repository-relative evidence paths and records
`ghidraMutation=false` and `retailBytesWritten=false`.

The receipt requires repository head
`619120fcd2a5fa822a28058883ca57a1e1b26c05` as an ancestor and pins every
load-bearing input, so unrelated descendant commits do not make verification
self-expire. With the four specimen locations supplied through the documented
environment variables, the exact verification command is:

```powershell
py -3 local-lab/xbox-pc-sparse-oracle-20260813-v1/seal_d3dx_vec4cross_portable.py verify
```

The exact-head v3 receipt, the earlier portable receipt at `6f1aa3d8`, and the
older non-portable receipt remain preserved as lineage; none is the current
compatibility authority.

## Promotion boundary

Promoted:

- PC function boundary `0x005762dd..0x005763cd`;
- exact seven-copy body identity across the named specimens;
- the two later Xbox `D3DX` single-range function boundaries;
- the PC data-pointer target at `0x00657090`;
- the compatibility-scoped D3DX four-vector-cross classification.

Not promoted:

- an original linker/C++ symbol;
- ownership of the other residual bytes at
  `0x0057629d..0x005762dd` or `0x005763cd..0x005763da`;
- Issue-7 Ghidra boundaries;
- source equivalence, call provenance, runtime behavior, or rebuild parity.
