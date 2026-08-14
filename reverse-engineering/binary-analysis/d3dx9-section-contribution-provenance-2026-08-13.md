# D3DX9 section-contribution provenance

Date: 2026-08-13

Status: reviewed provider-object provenance candidate; no Ghidra,
function-census, or campaign-generation mutation.

Verdict: **MEASURED PROVIDER-OBJECT PROVENANCE FOR 50 SAVED BODIES; EIGHT
OTHER EXACT MATCHES REMAIN EXPLICITLY NON-UNIQUE OR VERSION-BOUNDED.** Official
stripped Microsoft D3DX9 PDBs retain section-contribution records even where no
public symbol names a body. Exact BEA body matches can therefore be attributed
to a provider object-file family without inventing a private function name.

Specimen: pristine PC retail `BEA.exe.original.backup`, 2,506,752 bytes,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Evidence: **MEASURED** — the machine-local oracle is
`local-lab/d3dx9-section-contribution-oracle-20260813-v1/oracle.ready.json`,
219,771 bytes, SHA-256
`435d696446992cfd22137dd3a2468c2ce48337282bcd9a4ec7ff163de1cad12b`.
Its 10,466-byte reducer has SHA-256
`2e48ddba1edf845c92f91a6a71d0318671f60bcfa00bd9fe10374b7e71c057ed`
and reproduced the saved oracle byte-for-byte. The compact 58-row projection is
[`d3dx9-section-contribution-provenance-2026-08-13.tsv`](d3dx9-section-contribution-provenance-2026-08-13.tsv),
15,343 bytes, SHA-256
`249d6103bd1113235dcbd2b12bbdd22d963fbdf6ed94a9bf298310bd7d0ff1f6`.
Its machine-local preparation receipt is
`local-lab/d3dx9-section-contribution-tracked-prep-20260813-v1/tracked-prep.ready.json`,
493 bytes, SHA-256
`e1c28dc7fbe5a4f9e7f0d32955c08b703d6f18718d6cee2380f09fb537dbff03`.

The oracle consumes the same dated 2026-08-13 body-range and name owners as the
reviewed [exact-public correction](d3dx9-exact-public-name-corrections-2026-08-13.md):
1,183,469-byte body export SHA-256 `6703b759...e0aae` and 503,177-byte
name projection SHA-256 `d61f9866...f26fd`. All eight DLL/PDB identities and
matching GUID/age pairs are pinned there and repeated in the local oracle.

## Result

The official PDB contribution tables contain 8,845, 9,409, 9,510, 9,595,
9,613, 9,633, 9,991, and 10,085 records in releases 24 through 31. Of 8,103
then-current single-range BEA body owners, 6,644 meet the reducer's
at-least-16-byte admission floor. Raw exact comparison of those eligible bodies
finds:

- 58 BEA addresses in releases 24 through 29;
- 54 of those addresses still raw-exact in releases 30 and 31;
- 50 bodies attributed to one stable object basename in all eight releases;
- two all-release bodies whose single object owner changes by release;
- two all-release bodies covered by the same pair of aliasing object
  contributions in every release; and
- four PNG bodies exact only in releases 24 through 29.

| Disposition | Rows | Meaning |
|---|---:|---|
| `STABLE_SINGLE_OBJECT_ALL_EIGHT` | 50 | exact body lies in one same-basename contribution in every release |
| `VERSION_DEPENDENT_OBJECT_ALL_EIGHT` | 2 | exact body persists, but the contributing object basename changes |
| `STABLE_MULTI_OBJECT_ALIAS_ALL_EIGHT` | 2 | exact body is covered by the same two aliasing object families |
| `EXACT_V24_TO_V29_ONLY` | 4 | exact provider body disappears or changes in releases 30 and 31 |

The stable 50 materially improve library separation. They include 11
`d3dxmath.obj` bodies, four each from `ctokenize.obj` and `x3d_matx.obj`, three
each from `cblt.obj` and `clock.obj`, two from `d3dxmathx86.obj`, and individual
bodies from D3DX texture/parser, shader, PNG, JPEG, zlib, DXTC, and CRT objects.
Examples include:

| BEA VA | Current saved name | Stable provider object |
|---|---|---|
| `0x0057d0ee` | `CWaypointManager__BoxBlurPackedColorRows_Scalar` | `cblt.obj` |
| `0x0057d244` | `CDXTexture__Downsample2x2Average32` | `cblt.obj` |
| `0x005809de` | `CFastVB__ShutdownActiveProfile` | `clock.obj` |
| `0x0058c396` | `CTexture__InitBufferCursorRange` | `ctokenize.obj` |
| `0x00590da0` | `CTexture__DrainParserWorkQueue` | `jdapistd.obj` |
| `0x00593f8a` | `CDXTexture__PngApplyRowTransformLuts` | `pngrtran.obj` |
| `0x005961d0` | `CDXTexture__MultiplyMatrix4x4_InPlaceSafe` | `d3dxmathx86.obj` |
| `0x005987b2` | `CTexture__AppendNodeAtTail_Link0c` | `cnode.obj` |
| `0x005aba90` | `CDXTexture__SelectNextScanTableForProgress` | `jdcoefct.obj` |
| `0x005b2613` | `CDXTexture__Adler32_Update` | `adler32.obj` |
| `0x005bcfa0` | `CDXTexture__InflateCodesState_Create` | `infcodes.obj` |

These rows show why provider provenance matters: a plausible local behavior
description can still be attached to the wrong engine subsystem or authoring
unit. The object evidence supports library/source-family correction, but it
does not by itself supply the private function spelling.

## Eight deliberately non-unique rows

- `0x004d5e20` alternates between `cstack.obj` and `createmesh.obj`; its exact
  public-table ambiguity remains unresolved.
- `0x00588cc6` alternates between `psgpmesh.obj` and `btri.obj`; the
  contribution evidence does not select a stable provider object.
- `0x005a38c0` and `0x005a3980` are covered by both `d3dxplane.obj` and
  `d3dxvec4.obj` in every release, matching their dual official aliases.
- `0x00593753`, `0x00594836`, `0x00595030`, and `0x0059ce20` map to stable PNG
  objects only through release 29; they are not promoted to all-eight evidence.

## Claim boundary

Section contributions are provider build records, not BEA's missing linker
map. An exact body inside a stable contribution establishes a strong
provider-object/source-family identity, but not:

- the private function's original spelling;
- which upstream D3DX release BEA linked;
- runtime reachability, caller intent, or all semantic corner cases;
- ABI details beyond the already saved body; or
- reconstruction parity.

This pass changes no function name, comment, tag, grade, boundary, Ghidra
project, generation, or rebuild behavior. Rows that also have an exact official
public are owned by the separate 16-row correction ledger. Remaining rows need
a distinct reviewed naming/classification cohort; no object basename should be
blindly converted into a function name.
