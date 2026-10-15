# Particle-set text contract (`*.par`)

Status: active format contract — all shipped text rows and retail token grammar
accounted for; simulation/render behavior remains partial
Date: 2026-08-22
Verdict: the complete shipped token grammar, 1,479 descriptors, factory, and
loader VAs are bounded; simulation/render semantics remain partial.
Evidence: MEASURED — all three mirror-index rows, pristine retail parser tables,
factory/RTTI chains, and current bounded rebuild parser/tests.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Population

All three files are CRLF-oriented 8-bit text beginning with
`ParticleSystemEd_File_(C)2000_Lost_Toys_Ltd` and file version 1.0:

| File | Bytes | Lines | Descriptors | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `Frontend.par` | 28,702 | 1,125 | 65 | `01a4c73d7cfc666b4a367736fabd1d91bf3459ed1c538b6ca77f70c069cf8bc6` |
| `MainSet.par` | 685,194 | 25,931 | 1,405 | `a51fe4419b55e1af132e31c6b3cd8133c937745d8f4ab691eb5a0d81017ded06` |
| `ModelViewer.par` | 3,465 | 130 | 9 | `32d85d1f0400f46a45078d49c695967cde60ed572053059fd6246227162115a9` |
| **Total** | **717,361** | **27,186** | **1,479** | |

All declared descriptor counts match, all 1,479 descriptor names are unique,
and the mirror observer reports byte-identical parse/re-emit for each file.

## File and descriptor grammar

The retail token reader is line-oriented and case-sensitive. It reads at most
999 bytes into a 1,000-byte global buffer, recognizes 124 exact token names, and
dispatches one of six successful value shapes plus failure:

| Parse shape | Token names | Value contract |
| --- | ---: | --- |
| marker/no value | 2 | file signature and descriptor separator |
| direct integer | 47 | `%d` conversion |
| direct float | 19 | `%f` conversion |
| raw remainder string | 3 | preserves spaces after token name |
| reference name | 16 | deferred object-name binding |
| float + optional reference | 37 | float plus deferred optional name |

The ordered file begins with signature/version and
`Num_Particle_Descriptors`. Each descriptor supplies
`Particle_Descriptor_Type`, `Particle_Descriptor_Name`, then type-specific
fields. Duplicate keys are legal and order-sensitive (for example timeline
entries), so a parser must retain an ordered field list rather than a dictionary.

Exact parser/resolver behavior and the 10,000-entry deferred-reference workspace
are documented in
[`tokenarchive-semantics-2026-08-11.md`](../binary-analysis/tokenarchive-semantics-2026-08-11.md).

## Descriptor types

| Type | Retail RTTI class | Shipped rows | Slot-6 loader VA |
| ---: | --- | ---: | ---: |
| 1 | `CPDSimpleSprite` | 405 | `0x004C05C0` |
| 2 | `CPDEmitter` | 338 | `0x004C1810` |
| 3 | `CPDModifier` | 0 (dormant) | `0x004C20C0` |
| 4 | `CPDSelector` | 40 | `0x004C2130` |
| 5 | `CPDColourRange` | 97 | `0x004C2300` |
| 6 | `CPDTimeline` | 258 | `0x004C24C0` |
| 7 | `CPDShape` | 77 | `0x004C2B70` |
| 8 | `CPDTrail` | 100 | `0x004C3120` |
| 9 | `CPDMover` | 14 | `0x004C4420` |
| 10 | `CPDFunction` | 46 | `0x004C4840` |
| 11 | `CPDMesh` | 13 | `0x004C4B00` |
| 12 | `CPDFoR` | 24 | `0x004C5330` |
| 13 | `CPDPMesh` | 67 | `0x004C5730` |

The shipped corpus instantiates twelve types; type 3 is a proved factory case
but absent from all three files.

## Retail reader anchors

| VA | Identity | Boundary |
| --- | --- | --- |
| `0x004F57B0` | `CTokenArchive__ReadNextToken` | 124-name lookup and seven-arm parse dispatch. |
| `0x004F5BA0` | `CTokenArchive__ResolveReferences` | Case-insensitive deferred-reference resolution and cleanup. |
| `0x004CC020` | `CParticleSet__CreateByType` | Thirteen-case factory/RTTI chain. |
| `0x004CD7F0` | `CParticleSet__LoadFromArchive` | Validates header tokens, creates descriptors, dispatches loader, resolves references. |
| `0x004CDA60` | `CParticleSet__LoadParticleSetFile` | Selects MainSet/Frontend, opens the buffer, calls archive loader. |

The current owned parser is
[`rebuild/OnslaughtRebuild.Client/ParticleSetFile.cs`](../../rebuild/OnslaughtRebuild.Client/ParticleSetFile.cs)
with focused tests in
[`ParticleSetTests.cs`](../../rebuild/OnslaughtRebuild.Client.Tests/ParticleSetTests.cs).
This is a bounded reconstruction owner, not proof of complete visual parity.

## Known asymmetry

`Velocity_Randomness` is parsed by retail as a direct float even though the
compiled formatter uses float-plus-reference shape. All 338 shipped uses avoid a
named modifier (336 explicit `NONE`, two with no suffix), masking the stale-slot
defect. Preserve this as released behavior rather than “fixing” it silently in a
parity path.

## Open questions and falsifiers

- Map every field to simulation/render semantics and consumer state, especially
  Frontend/ModelViewer-only records and PMesh geometry.
- Trace one descriptor of each instantiated type through creation, update, and
  render; text parse success is not effect parity.
- Bound malformed numerics, >999-byte lines, allocation failure, duplicate
  names, and the 10,000-reference ceiling using disposable copies.
- Test the token-32 named-modifier edge only in a copied profile; do not edit the
  pristine files.
- PB* CMSH tags may relate to baked particle geometry, but similarity is only a
  hypothesis until a byte/consumer join proves it.

## Claim boundary

The complete shipped textual grammar, descriptor census, factory identities,
loader VAs, and reference mechanics are bounded. Malformed-input causality,
complete field semantics, simulation, rendering, and full parity remain open.
