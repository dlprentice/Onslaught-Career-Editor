# D3DX9 exact-public current-name corrections

Date: 2026-08-13

Status: reviewed static correction candidate; no Ghidra, function-census, or
campaign-generation mutation.

Verdict: **C1 static correction candidate for 16 current names; no Ghidra
mutation in this pass.** Sixteen saved names are contradicted by full-body byte
identity at the same official public symbol in every pinned x86 D3DX9 release
from 24 through 31. Three other addresses remain alias-ambiguous and are not
proposed for renaming.

Specimen: pristine PC retail `BEA.exe.original.backup`, 2,506,752 bytes,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Evidence: **MEASURED** — the exact local oracle is retained at
`local-lab/d3dx9-exact-public-oracle-20260813-v1/oracle.ready.json`, 52,489
bytes, SHA-256
`3964d0b7da8eb1dab7d711642c4e98f5709f0194f009ebc40de976daf24604d4`.
The 20,360-byte reducer has SHA-256
`d92dde71556be20f5fe1d550ad26bc84ea56ac0fb9f2cfca68b96ea37ecddf88`;
its 13,256-byte independent verifier has SHA-256
`d2f2dc7c27d4725ddb2cc6f93aa5e51bc3ef2670b19e8f7db8b392169e24e0cc`.
The reducer reproduced the saved result byte-for-byte on a second invocation.
The verifier, which does not import the reducer, independently reparsed every
PE, PDB public table, BEA body, and current name; rebuilt the complete 24-row /
21-address partition; and reproduced exactly 16 corrections, three ambiguous
addresses, and two already-correct names.

## Inputs

The current 8,170-row name projection is 503,177 bytes, SHA-256
`d61f9866d9dbf67bae817a710d50a1a136b7c2156ec6eb7f862d82dea70f26fd`.
The exact-body export is 1,183,469 bytes, SHA-256
`6703b759ac18528d61c4ad6f646f0fd6933eaf2a8892617f3ecc24b0ef8e0aae`;
8,103 owners are single-range and eligible for this exact-byte join.

The local reducer pins each installed 32-bit D3DX DLL and the matching stripped
Microsoft Symbol Server PDB. Every DLL's RSDS GUID and age exactly match its PDB;
all PDBs have age 1. The full input identities are in the retained local result.

| D3DX | DLL bytes | DLL SHA-256 | PDB GUID | PDB bytes | PDB SHA-256 |
|---:|---:|---|---|---:|---|
| 24 | 2,222,800 | `94ec67763f67932dd4273ef5cc12889a5cef090ffea3ee78a80c7b530272b1b5` | `bb9432b1-c5e2-42cc-baae-b6a11270b9d3` | 977,920 | `bff589a372c88503294ecf43c740f1d5eadb2c97c544a7f035e1fb5976759602` |
| 25 | 2,337,488 | `4c54df27ce84d21b2924e64ff79b13e7876ce85d8e0c9c1d0abd8da73888187a` | `af2a5af4-8737-4921-890c-ffcab87e3656` | 1,043,456 | `f875d34105440c62a641bb0776151c23b97530c12c97542a6012ff651dbd2b52` |
| 26 | 2,297,552 | `8ea96fe01c3c86a36fcb3795ae03eb12034003e335ef475571efaeda17c5bc78` | `2dd10123-2563-4475-85db-86f543fcf5f7` | 1,551,360 | `4130263f1253272969383740a41dc0492cbe92e106ca55b28702580622494d16` |
| 27 | 2,319,568 | `a70d571cd675c97c9eeb4a234dba1d667ffb54ec3bb14defb36b3e2f605ae257` | `33fa0454-51d6-46d0-badb-fc8595851e2b` | 1,567,744 | `b4e700c23f7f5dd27bc36bd27185d7a25ae42edfdb2bbfbd551f8ff6fd0a95cb` |
| 28 | 2,323,664 | `f3e391b5f1c1f9637cabf2b812b6f5d65e4776c89d779f506f6b643cc563176d` | `ef18a217-fc40-4827-a09e-59e7d65f55af` | 1,575,936 | `d6f8b594f05466d957ba946ba4a8989ad5c84b90c0ecb3f259fdcfc7b3fbaed6` |
| 29 | 2,332,368 | `c5e21c18f8c79bc517da59e3192c39ea73bdcaf85867628187f6b3cca07dd21f` | `a0d23c0c-3ed5-42dd-b5f2-66176092f74f` | 1,575,936 | `05ab0d7f2c82b7526972b25f0bbaf12dea599b906be1b159dfaf0695d891771c` |
| 30 | 2,388,176 | `5edeed79f2359527a55b8189cfa8b9b121cd608d44eead905a0f3436938ad532` | `ac45bb29-e731-4d18-b875-94c43e57d394` | 1,625,088 | `8849ed24cf5079c00f77bd9b4c9d2b7a4f46039ff1e81cf8a1f54efcc8fa2097` |
| 31 | 2,414,360 | `e2065619fe6eb0034833b1dc0369deb4a6edc3110e38a1132eeafcf430c578a5` | `b9c15618-b8da-4280-bfd3-5afd97f57b2e` | 1,649,664 | `d97190cd746c6b19df61d88298d6d754ae3229936110783b4fda22eff20b7fb1` |

## Result

The reducer found 24 exact public rows at 21 BEA addresses. Eighteen addresses
have one public identity; two simply confirm already-correct `__allmul` and
`__aullshr` names. The remaining 16 are the correction set in the
[machine-readable ledger](d3dx9-exact-public-name-corrections-2026-08-13.tsv).

The most consequential corrections are structural, not cosmetic:

- six short functions previously attributed to BEA texture/parser state are
  exact D3DX constructors in the `D3DXTex`, `D3DXCore`, and `D3DXShader`
  namespaces;
- nine FastVB/dispatch hypotheses are exact AMD/x3d D3DX math routines; and
- `0x005d06f0` is the conventional `__EH_prolog`, not a no-op initializer.

The three excluded addresses are intentionally unresolved:

- `0x004d5e20` is the same 16-byte public body for both
  `D3DXMesh::CBone::CBone()` and `D3DXCore::CStringStack::CStringStack()`;
- `0x005a38c0` and `0x005a3980` each carry both
  `AMDSSE_D3DXPlaneTransformArray` and `AMDSSE_D3DXVec4TransformArray`
  aliases. Plane and four-vector layouts make the shared implementation
  plausible, but the exact public table does not select one source spelling.

## Method

For each current single-range BEA body of at least 16 bytes, the reducer:

1. re-reads and rehashes the exact body from the pristine PE;
2. requires a full raw-byte match beginning at an executable public-symbol
   address in pinned `d3dx9_24.dll`;
3. joins by that exact public spelling to versions 25 through 31; and
4. requires the full body to remain byte-identical at the joined public address
   in every version.

This is deliberately stronger than a mnemonic, shape, or nearby-string match.
Short bodies are still admitted only because the exact official public identity
repeats across eight separately pinned DLL/PDB pairs. Multiple public aliases
remain visible rather than being collapsed.

## Boundaries

- The proposed labels are provider-qualified evidence names. They do not claim
  that BEA retained those literal linker symbols.
- This result proves full-body static identity for the listed builds. It does
  not prove runtime reachability, caller intent, exact BEA source spelling, or
  Godot parity.
- It does not grade or rename the three alias-ambiguous addresses.
- It does not change the 8,170-function structural census, current Ghidra
  project, tracked projection, Generation 23, or the pending Generation 24.
- Any Ghidra promotion remains a separate backed-up scratch/apply/readback
  ceremony with exact non-target collateral checks.

The cheapest falsifier is one byte mismatch in any full body, a DLL/PDB
GUID-age mismatch, failure to reproduce one joined public spelling in all eight
versions, or a collision between a proposed provider-qualified label and the
current 8,170-name projection.
