# CStart__Init

> Address: `0x004eae10`

Status: partial static contract; terrain-height prefix carried, remainder open
Last updated: 2026-08-30
Source File: none — the `CStart` implementation is absent from the pinned GPL
drop; placement below `game.cpp/` is organizational only | Binary: BEA.exe
pristine specimen, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: Initializes a released player-start object. The full 266-byte body is
bounded, but only its 37-byte terrain-height prefix is semantically admitted:
sample the heightfield, compare the sampled height strictly below serialized Z,
then sample again and store that second result only on the clamp arm.
Evidence: MEASURED — exact pristine bytes, independent disassembly, the
hash-pinned world-110 HFLD, and a deterministic Core owner with a focused
second-call mutation discriminator.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752
bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Exact boundary

`CStart__Init` occupies half-open range `[0x004eae10, 0x004eaf1a)`, 266 bytes.
The raw body SHA-256 is
`67ada0c7c363cd7f8ee3a059c198f568b687739f020a352b0ba6c2a37357934d`;
the retained Ghidra range digest is
`75eebfc7ade590e2fc349ea2b155b1ab15e4e24ccaee42adef38555756452e0d`.

This admission owns only `[0x004eae27, 0x004eae4c)`, 37 bytes, SHA-256
`f4efe7633c1f4ea75ca937ec0479eb1c72cd273812c15c31100991cd0844fe6a`.
It includes the store through `0x004eae4b`. Bytes `0x004eae4c..0x004eae4e`
prepare the next call and are outside this contract; `CComplexThing__Init`
begins at `0x004eae4f`.

## Admitted prefix

| Address | Released operation |
| --- | --- |
| `0x004eae27` | pass the start's XY to the global heightfield owner |
| `0x004eae2e` | call the sampler at `0x0047eb80` |
| `0x004eae33` | compare the sampled float with serialized `[edi+0x0c]` |
| `0x004eae36..0x004eae3b` | take the clamp arm only when sampled height is strictly lower |
| `0x004eae3d..0x004eae44` | pass the same XY and call the sampler a second time |
| `0x004eae49` | store the second sample to `[edi+0x0c]` |

The sampler at `[0x0047eb80, 0x0047ec54)` is 212 bytes, raw SHA-256
`cc26a2010da70cfa51d84f256ec1ec759a15e5a1fb3adc717b7a84bda073ea63`
and retained range digest
`9f504a26a74f77dcefbb386ad35c3f09994e07c772b626d986d5c11a6b08506f`.
Its already-carried Core owner is `Level100Terrain.SampleHeightUnitsAtFixed`.

For world 110, the exact authored start XY `(264.75, 258.8125)` converts to
24.8 fixed `(67,776, 66,256)`. The hash-pinned 668,660-byte HFLD
`fd4d076a2926fbc473b7d364703bdbc0c8a0f7a638b0ab71b6f319374da033c2`
returns `-10,485` units. With scale bits `0x3a7003c0`, both released samples
produce `0xc1199926` (`-9.599889755249023`). That is strictly below authored
negative-zero Z, so the second sample becomes the final Z.

## Rebuild mapping

`RetailWorldPlayerStartHeightClamp.Apply` accepts only an already-admitted
player-start resolution and the hash-pinned world-110 terrain. Its immutable
result retains authored raw fields and records every sample. Production callers
cannot inject a sampler; an internal friend-test seam exists only to prove that
the clamp arm really samples twice and stores the distinct second result.

The owner does not construct `CStart`, call `CComplexThing__Init`, allocate or
return a Battle Engine, assign a player, mutate a session, or claim any semantics
after `0x004eae4b`. Its fixed-coordinate conversion is admitted only for the
publicly obtainable exact world-110 authored and released fallback positions;
arbitrary-coordinate generalization remains open.

## Cheapest falsifier

Any of the following rejects this carried prefix:

- the pristine prefix digest differs from `f4efe763…fe6a`;
- equality takes the clamp arm rather than falling through;
- the clamp arm samples once or stores the first sample instead of a second;
- either sample receives XY other than `(67,776, 66,256)` for the exact row;
- world-110 final Z differs from `0xc1199926` under the pinned HFLD;
- the rebuild owner crosses into the setup at `0x004eae4c` or the
  `CComplexThing__Init` call at `0x004eae4f`.

The measured comparison-inversion receipt is
`local-lab/rebuild-world110-player-start-height-clamp-mutation-kill-20260830/RECEIPT.md`,
SHA-256
`9acb79d7a5e092725c1767358eb1d574853531b6caea0aa5ef30a752c6e03c40`.
It is external machine-local evidence under `~/ProjectData/Onslaught/`, not
portable repository content.

The remainder of `CStart__Init`, `GetPlayerObject`, post-load list walking,
Battle Engine/player construction, assignment, and playable world-110 session
ownership remain separate open contracts.
