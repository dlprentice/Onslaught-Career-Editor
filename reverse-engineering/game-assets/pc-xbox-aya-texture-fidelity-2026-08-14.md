# PC and USA Xbox AYA textures preserve dimensions in 18,579 pairs; 33 drop one top mip

Status: active measured texture-layout and stored-block finding
Date: 2026-08-14
Verdict: GO for the bounded PC/USA-Xbox `TEXT` population. Every one of the
18,612 paired occurrences passed complete nested geometry validation and joined
to an installed PC DDS frame. Those occurrences contain 18,669 frame rows.
Xbox keeps PC dimensions and mip topology for 18,579 texture occurrences,
which expand to 18,636 frame rows; 33 one-frame occurrences each drop exactly
one top mip. Xbox also stores 25 measured sky-cube faces uncompressed and has
11,332 conservative full-chain exact block matches. Using the serialized PC
`CTEX` source-format field to resolve eight duplicate loose-DDS names raises
that exact count to 11,762. These are stored-byte findings, not decoded-pixel
or visual-quality claims.
Evidence: MEASURED -- final retained `run-e` and `run-f` are byte-identical
complete replays through `tools/aya_texture_fidelity_census.py`. The bounded profile
pins the frozen geometry, whole Xbox ZIP, both PC DDS shelf manifests,
`ResourceAccumulator.cpp`, PC archive count, and load-bearing metrics. It
reopens the 68 of 301 PC resources that own paired `TEXT`, requires their
strict envelopes, and validates each inflated raw archive hash against the
frozen geometry. It does not bind the stored/compressed byte identity of all
301 PC resource archives.

## Bound inputs and sealed receipts

The census consumes the frozen v3 cross-platform geometry rather than changing
its schema or outputs. The paired population spans 68 PC resources; it reopens
those archives and their 68 Xbox ZIP members, then independently validates
every paired nested texture owner. Retail bytes and raw rows remain ignored
under `local-lab/`.

| Identity | Value |
| --- | --- |
| Frozen geometry rows / paired `TEXT` rows | 47,657 / 18,612 |
| Geometry SHA-256 | `2462f7453fb3b3ec252a0ab4e8f0f08891c3e6338b585e910f289d0a6edd8165` |
| Xbox ZIP length / SHA-256 | 1,943,296,611 / `7a83dcc73fecfc701306bcaf78c96f55c4ecd47ef5d1ab10e9e20766a25281ae` |
| `ResourceAccumulator.cpp` SHA-256 | `4f78480aeb6caae9854295ae09a9b322a7a83264da3f3e19a95723505414f1b2` |
| PC `dxtntextures` shelf | 800 files: 212 DXT1, 588 DXT2 |
| PC `dxtntextures` canonical-manifest SHA-256 | `2746bfad722edf964f5abc6ac0094b9987d2d8cb615df7748cebc555cb67e410` |
| PC `textures` shelf | 47 files: 38 A1R5G5B5, 9 A8R8G8B8; five selected `mustbe_` files |
| PC `textures` canonical-manifest SHA-256 | `7a524b05321fcf8aefce4254fa2982e9040a1dbe1e2c22ad409a61fdbb1c865d` |
| Census tool SHA-256 | `2099cd4a19047e9a663e8dd78822603e95ed23669a81fc329f6963534943d185` |

The final retained evidence is
`local-lab/aya-texture-fidelity-census-20260814-v1/run-e` and `run-f` under
that same root. They produced the same five files byte-for-byte. Runs `run-a`
through `run-d` are superseded by the final DDS-manifest pinning and
source-qualified Xbox-variant grouping; they are not evidence for this report.

| Local output | Bytes | SHA-256 |
| --- | ---: | --- |
| `aya-texture-fidelity-summary.json` | 31,447 | `ea23a7ac3ff6ce750ff103174f7959ce83755e132445fca8d2d0dfb7d5c13e1e` |
| `aya-texture-fidelity-occurrences.tsv` | 1,905,792 | `bfcd8273f04458b46a10f9f643218e1c02ce7d56e8a4b10f5d08491e346de724` |
| `aya-texture-fidelity-frames.tsv` | 7,521,704 | `a19030533874f8329ab08ef3bef7e49e492b1be30fc5508d2e58a0494ba149b9` |
| `aya-texture-fidelity-mips.tsv` | 13,333,133 | `f49b822e44cbb550be26477ca0c628a0f04b0a3d713a1d465454d60f8b3b6393` |
| `aya-texture-fidelity-variants.tsv` | 117,383 | `d3c612db4338900ee1fb92cddb2c2c1e1a79c9a3c3b3423d611e775cb28e70fe` |

The five selected `mustbe_` names are
`frontend\v2\fe_white_ring.tga`, `hud\v2\battleenginemarker.tga`,
`shadowblob.tga`, `sunblob.tga`, and `sunreflect.tga`. The scanner validates
all 847 loose DDS files, selects 600 source-format/frame keys used by the
paired population, and refuses undeclared bytes in every inflated DDS.

## Complete nested geometry

Each top-level `TEXT` payload is exactly one `DXTX` owner. Its first child is
one `CTEX` with a measured 344-byte body; the serialized name is at payload
offset `0x18`, width at `0xbc`, height at `0xc0`, frame count at `0x148`, and
format code at `0x154`. Exactly that many `TFRM` children follow.

On PC, each `TFRM` body is exactly its four-byte mip count; the corresponding
stored mip bytes live in the loose DDS. On Xbox, the count is followed by
exactly that many `TMIP` children. Every `TMIP` length equals the extent
inferred as `max(1, width >> level)` by `max(1, height >> level)` and its
measured format geometry: codes 3 and 4 use four bytes per pixel, code 6 uses
eight-byte DXT blocks, and code 7 uses 16-byte DXT-compatible blocks. Nothing
here establishes the exact Xbox enum spelling for code 7.

The PC field at `CTEX+0x154` is a source-format request, not necessarily the
loose DDS storage layout. The measured source requests are codes 1--5
(`A1R5G5B5`, `A4R4G4B4`, `X8R8G8B8`, `A8R8G8B8`, and `R5G6B5`). The scanner
parses the actual DDS header separately. Stored bytes are compared only for the
proved equal-layout pairs PC DXT1/Xbox code 6, PC DXT2/Xbox code 7, and PC
A8R8G8B8/Xbox code 4.

## Measured population

The 18,612 occurrences cover 589 logical names, 592 unqualified
logical-name/frame identities, and 600 identities after preserving the PC
`CTEX` source-format code. Their 18,669 occurrence frames divide as follows:

| PC stored form -> Xbox code | Frames |
| --- | ---: |
| A8R8G8B8 -> 4 | 265 |
| DXT1 -> 3 | 25 |
| DXT1 -> 6 | 6,205 |
| DXT2 -> 6 | 4,077 |
| DXT2 -> 7 | 8,097 |

For code 7, 1,166 complete mip chains contain at least one extent whose length
distinguishes 16-byte block geometry from a simple `width * height` layout; all
levels in the other 6,931 chains are length-ambiguous between those formulas.
Every row still passes the measured 16-byte-block chain. That validates
geometry, not an enum name.

| Comparison class | CTEX-selected | Conservative |
| --- | ---: | ---: |
| Exact, comparable, full topology | 11,762 | 11,332 |
| Different, comparable, full topology | 2,797 | 2,765 |
| Different storage layout, including 25 shifted rows | 4,102 | 4,102 |
| Exact after one-top-mip alignment | 6 | 6 |
| Different after one-top-mip alignment | 2 | 2 |
| Duplicate source variant unresolved | 0 | 462 |

“Exact” means every aligned stored mip byte is equal; it does not mean decoded
pixels were compared. The conservative 11,332 result is the historical
basename-only lower bound. A basename-only selector now either returns that
explicit population or refuses; it never silently chooses the first file.
The classification is storage-layout-first: 25 of the 33 shifted frame rows
are included in `Different storage layout`; the remaining eight are the six
shifted exact and two shifted different comparable rows shown separately.

Eight logical frame identities each have exactly two loose candidates, source
codes 2 and 5:

- `particle\alparticle4.tga`, `blood.tga`, `blue spark 2.tga`, `fireball.tga`,
  `particles.tga`, `small puff.tga`, and `smoke trail.tga` have a DXT2-stored
  code-2 candidate and a DXT1-stored code-5 candidate.
- `particle\muspell bullet.tga` has DXT1 storage in both candidates.

Across occurrences, 462 code-2/code-7 rows select the first seven DXT2 files,
66 code-2/code-6 rows select the `muspell bullet` DXT1 file, and 529
code-5/code-6 rows select the DXT1 alternatives. PC `CTEX` source code 2
(`A4R4G4B4` source request) therefore selects the DXT2-stored loose DDS for the
462-row population, comparable to Xbox code 7's measured 16-byte block
geometry. It does not make the DDS layout `A4R4G4B4`, nor prove an Xbox DXT2
enum. The CTEX-selected result gains 378 exact rows from the seven code-7
groups and 52 from `muspell bullet`, explaining the exact 430-row increase.

## Mips, sky, and cross-resource variants

Xbox dimensions and mip topology equal PC for 18,579 texture occurrences,
which contribute 18,636 frame rows. The remaining 33 occurrences contribute
33 frame rows and all drop exactly one top mip, spanning 13 names in 16
resources. They include eight occurrences each of `f_ventura02` and `be_texb`,
six of `a8_fb_hangermorebits_lit`, two of `a8_warspite-page1`, and one each of
nine other names. The released resource builder explicitly budgets Xbox texture RAM,
drops the largest eligible texture first, and gives `meshtex\be_texb.tga` an
early-drop special case in
`references/Onslaught/ResourceAccumulator.cpp:389-470`, specifically
`:433-441`. This source explains a builder mechanism; the serialized census
establishes which retail rows changed.

The 25 DXT1-to-code-3 rows are exactly five sky-cube faces in each of resources
331, 332, 710, 741, and 742. Source identifies the cube names at
`ResourceAccumulator.cpp:208-228`, then conditionally disables their
compression when the Xbox texture budget permits at `:472-496`. The census
proves 32-bit Xbox storage geometry for these rows, not decoded color parity or
better visual quality.

Xbox payload hashes vary across resources for 357 of 600 source-qualified frame
identities. The deterministic variants table preserves the PC `CTEX` code,
resource count, and complete distinct-hash set: 243 identities have one Xbox
payload variant, 334 have two, 20 have three, and three have four. The
per-frame table retains each exact resource-to-hash assignment. Across 18,669
source-identity/resource groups, none has two payload variants within one
resource; the earlier unqualified grouping had incorrectly merged the eight
code-2/code-5 particle pairs. This prevents either source variant or one
resource's bytes from being treated as a universal Xbox texture oracle.

## Limits and next falsifiers

1. Decode the three comparable storage pairs independently and compare a
   canonical pixel representation; current equality is raw stored-block
   equality only.
2. Identify Xbox format code 7 from a target header or serializer source before
   assigning an exact enum spelling. Geometry alone is insufficient.
3. Explain the 33 one-mip rows against the resource builder's per-level budget
   inputs; source establishes the algorithm, not each budget value.
4. Investigate the 2,797 CTEX-selected comparable-but-different rows and the
   357 cross-resource variant identities by authored source and resource role.

The reusable census and synthetic tests contain no retail bytes. No live
Ghidra operation contributed to this finding.
