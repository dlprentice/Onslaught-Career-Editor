# AYAResourceExtractor published a real CMSH decoder, but not original game source

Status: active source/history/removed-release audit; format claims remain bounded by
current corpus and retail evidence
Date: 2026-08-22
Verdict: **Stuart intentionally published the extractor implementation and its
reverse-engineered format assumptions. Nothing in the removed release proves
that original Battle Engine Aquila source was published. No extra named
type/member/resource/string/import format surface was found in the removed
release, and the binaries predate two surviving-source fixes. Behavioral
equivalence is not established: no source-build IL comparison was made, and 47
mixed-mode native/non-IL bodies remain semantically uninspected.
Current AYA/CMSH tools already corroborate or supersede most extractor claims.
The remaining actionable gaps are skinning/blending, PB-family payloads, TEXR
layer semantics, and a few explicitly unproved labels—not a missing secret
binary parser.**
Evidence: SOURCE + CORPUS-MEASURED + BINARY-METADATA — complete read of every
first-party source/project/history entry at AYA fork commit
`53b10b083b59cfd7e72849c15bec8b608eaf8a23`, upstream commit
`4e04952a200e29040a68fc8648e835f9a7d608d1`, all seven removed release blobs at
initial commit `801f3ba8166405a472f97f4909b5ee4ff3ed633e`, deterministic PE/ECMA-335
metadata and IL-body hashing without loading an entry point, deterministic FBX
parsing from the surviving source, and a complete 92-row crosswalk to current
owners.
Source specimens: AYA tree `8641b14865756c354a22c458bc83fc649231d279`;
upstream tree `c59837bde3fd196bc8897c97bf53437366788bed`;
Onslaught tree `7a8d0a83257ff7a2e9831455eca576ade11decbd` at
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.

No removed executable was launched. No retail asset, binary, or extracted
payload is tracked by this audit. Removed blobs were materialized only under the
ignored `local-lab/hermes-kanban-campaign-2026-08-22/aya-extractor-audit/`
workspace, hashed, inspected as data, and left untracked.

## Plain answers

| Question | Answer |
| --- | --- |
| Was source intentionally published? | **Yes.** Commit `801f3ba` added the solution, first-party source, third-party source, template, and release artifacts together. The later README explicitly points readers to the solution and describes the C#/C/C++ components (`references/AYAResourceExtractor/README.md:12-24`). |
| Is original game code proved? | **No.** The extractor uses independently named C# readers and exporter code. The pinned Onslaught drop contains none of the 29 AYA/CMSH asset fourcc tokens. Its generic chunk reader, Direct3D enums, triangle-strip use, and `meshtex\\` names are architectural/contextual corroboration, not textual or binary proof that extractor code came from an in-house game owner. |
| Do removed binaries contain extra implementation knowledge? | **No extra named type/member/resource/string/import format surface was identified.** The main DLL's 19 type definitions, 67 release IL bodies, and sole empty `.resources` manifest map by name/signature to surviving source or compiler/SDK generation; the native EXE is a .NET apphost with no CLR metadata. This is not behavior-equivalence proof: source-built IL was not compared, and the mixed-mode DLLs retain 47 native/non-IL bodies whose semantics were not inspected. Build-path/PDB strings are the only affirmative unpublished metadata found. |
| Are there new actionable format facts? | **No new released-format field is established solely by the binaries.** The audit identifies two contradicted claims (`CMVB+264` is group count, not root texture count; DXT2 is not the shelf's only DDS FourCC), three corpus-absent tags/formulas (`CCUS`, `BONW`, `BONS`), several unproved labels, and legacy lookup/export limits that should not be promoted. |

The machine-readable owner is
[`aya-resource-extractor-contract.tsv`](aya-resource-extractor-contract.tsv).
Its six classifications are intentionally disjoint:

- `EXTRACTOR_ONLY`: published source assumption with no present corpus support;
- `CURRENTLY_CORROBORATED`: same bounded claim in current measured owners;
- `CURRENT_TOOL_STRONGER`: current tooling validates a stricter or richer
  contract;
- `CONTRADICTED`: current evidence rejects the extractor's label;
- `EXPORT_CONVENTION_ONLY`: FBX/PNG/UI behavior, not serialized or retail
  semantics;
- `UNKNOWN`: plausible label or causal story without enough evidence.

## Pins, history, and publication intent

The public history contains ten commits. Only four stages change what this
audit can conclude:

| Commit | Date | Effect |
| --- | --- | --- |
| `7c3d47c67c89c450850da7e1ac66a7ac043b161f` | 2023-05-22 12:03:43 +01:00 | Added repository support and a placeholder root MIT text. |
| `801f3ba8166405a472f97f4909b5ee4ff3ed633e` | 2023-05-22 12:03:46 +01:00 | Added all source/projects, `BoxWithTextures.fbx`, and the seven release artifacts. Initial tree: `3dae0f60f8821b5240677f0f946dfd9c3ad4dba5`. |
| `e4bf31d96f0281a394d03272353d1960098a8a1e` through `1e2459a8a7614c975cf37a93a8b7e3ed7a20bbd9` | 2023-05-22 | Added/expanded the README into an explicit source and limitations description. |
| `e7c6f371c39331e1062dc09091fa95adc55457e6` | 2023-05-22 12:13:54 +01:00 | Removed the EXE, four DLLs, and two runtime JSON files. Removal tree: `9dc21993bd2464f6f0e109547193c72864f290cd`. |
| `8d9880e48534f4c9d8d2c87ba836c20e9c65f441` | 2023-05-22 13:49:11 +01:00 | Removed non-working Any CPU/x64 solution configurations and added the Visual Studio fallback path for `BoxWithTextures.fbx`. |
| `4e04952a200e29040a68fc8648e835f9a7d608d1` | 2023-05-22 13:49:13 +01:00 | Stuart's surviving upstream tip. |
| `53b10b083b59cfd7e72849c15bec8b608eaf8a23` | 2026-07-13 | Fork-only fix: rectangular DDS copy count changed from `height*height*4` to checked `width*height*4`; no parser change. |

All first-party parser files were already present in `801f3ba`. After that
initial publication, no CMSH parsing method changed. The only first-party
runtime source change was the template-path fallback in
`FbxModelExporter.Export` (`references/AYAResourceExtractor/Code/AyaResourceExtractor/FbxModelExporter.cs:8-20`).
The fork delta changes only
`Code/DDSTextureUncompress/DDSTextureUncompress.cpp`. This history supports
intentional publication of the source tree. It does not establish why the
release binaries were removed 608 seconds (10 minutes 8 seconds) later.

## Exact source inventory and provenance boundaries

The tracked fork contains **73 files** and **28,842 physical text lines**; the
binary FBX template contributes no line count. “Function” below means a lexical
source function definition, not a one-target linker symbol count. The local
function census used Tree-sitter C/C++ plus a C# declaration scan twice; both
normalized outputs had SHA-256
`8c78dbfeb1083aef445a728407bb2f33df489cb14aa16a614b84e52bb627f065`.
The tracked audit independently pins every first-party declaration and refuses
denominator drift.

| Component | Files | Physical lines | Function definitions | Provenance/license boundary |
| --- | ---: | ---: | ---: | --- |
| First-party executable source | 13 | 1,565 | 40 | 9 handwritten C# files (1,181 lines), 2 generated C# files (287), and 2 C++/CLI bridge files (97). Root MIT text exists but still says `[year] [fullname]` (`LICENSE.txt:1-4`). |
| First-party project/resource support | 11 | 619 | 0 | Three C# project variants, solution, resx/settings/launch data, and the two native project/filter pairs. |
| Bundled zlib 1.2.13 | 28 | 23,581 | 158 across 26 C/H files | Jean-loup Gailly/Mark Adler zlib terms are retained in `Code/ZLib/zlib.h:1-29`; two Visual C++ project files are separate support. |
| DDSReader / FreeImage-derived | 2 | 739 | 21 | `DDSreader.h:1-6` and `DDSReader.cpp:1-13` attribute Juho Peltonen, say GPL3, and identify FreeImage `PluginDDS.cpp` derivation; the embedded FreeImage header names Volker Gärtner and Sherman Wilcox (`DDSReader.cpp:16-35`). The referenced component `license.txt` is absent. |
| Hamish Milne FBX C# | 14 | 1,854 | 54 across 13 C# files | Attribution exists only in the root README (`README.md:16-22`); the `Code/Fbx` tree has no component license file or source header. |
| Template/top-level docs | 3 | 58 | 0 | `BoxWithTextures.fbx`, README, and placeholder root MIT text. |
| Repository support | 2 | 426 | 0 | `.gitattributes` and `.gitignore`. |

The first-party **40-routine denominator** is:

- `AyaFileUncompressor` 1;
- `AyaMatrix` 1;
- `AyaModelExtractor` 1;
- `AyaModelImporter` 15;
- `AyaTextureExtractor` 1;
- `FbxModelExporter` 2;
- `Log` 4;
- `MainForm` 10;
- `Program` 1;
- generated `MainForm.Designer` 2;
- the DDS and zlib C++/CLI bridges 1 each.

`AyaVector`, `AyaVertex`, `AyaIndexType`, `AyaModel`, and generated `Settings`
add data/properties but no explicitly written routine. The tracked
[`tools/aya_extractor_source_audit.py`](../../tools/aya_extractor_source_audit.py)
resolves the pinned source trees with `git ls-tree` and reads their canonical
object bytes with `git cat-file --batch`. Inventory byte counts, SHA-256 values,
Git blob identities, physical-line counts, and declaration scans therefore all
derive from the same committed blobs rather than LF/CRLF checkout
materialization. It checks each declaration name and line, every tracked file's
unique category, both submodule pins, every contract reference, all 92 claim
IDs, and zero unclassified rows.

### License conclusion

The components must remain separate. The placeholder root MIT file cannot be
used as evidence that the zlib, DDSReader/FreeImage, or FBX components were
relicensed. The exact redistribution follow-up is to recover and pin the
DDSReader GPL3/FreeImage license chain and the Hamish Milne FBX source license;
this audit makes no legal conclusion beyond the missing notices.

## What the first-party code actually publishes

The extractor publicly exposes a coherent reverse-engineered implementation,
not just format names:

- the PC AYA member envelope (`u32le compressed length` plus zlib member,
  repeated to EOF), with the author's unproved 1 MiB engine-limit explanation
  and fixed 1 MiB/4 MiB implementation buffers
  (`AyaFileUncompressor.cs:7-20,36-87`);
- the CMSH root offsets, 300-byte mesh name, texture and part counts, CMST and
  MSHT/TEXB ordering (`AyaModelImporter.cs:11-38,136-178`);
- current/base part transforms, hierarchy/count fields, fixed 32-byte part
  names, and the optional record order (`AyaModelImporter.cs:186-399`);
- all named part tags required by the brief, including the corpus-absent
  `BONW`/`BONS` formulas and opaque-length handling for `PBKT`/`CPOS`/`CORI`;
- direct geometry ownership and REFR repeated-part expansion;
- CMVB group/stride/FVF/topology fields, MMPT declarations, u16 IBUF, first-group
  VBUF ownership, 36/48-byte vertex forms, and six TEXR IDs
  (`AyaModelImporter.cs:403-514`);
- base-transform application, strip parity/degenerate removal, FBX Z/V sign
  flips, and static flattening;
- the two-suffix texture lookup and PNG conversion path; and
- admitted limitations: wrong-looking normals, no multitexture blend, one
  static object, no bone/animation export, incomplete model coverage, PC-only
  operation, and untested Steam equivalence (`README.md:14-35`).

The 92-row contract classifies **23 currently corroborated**, **39 current-tool
stronger**, **19 export-only**, **6 unknown**, **3 extractor-only**, and **2
contradicted** claims. Every first-party parsing/export assumption identified in
all 40 routines has a row; no row is unclassified.

### Important crosswalk outcomes

1. **Outer AYA framing is confirmed, not newly discovered.** Current corpus
   work accounts for all 1,361 PC envelopes and 1,725 zlib members. The observed
   364 full 1 MiB members support a writer chunking policy, not the comment's
   causal claim that BEA could only handle 1 MiB
   ([`aya-container.md`](../asset-formats/aya-container.md):30-62).
2. **CMSH root, tags, hierarchy, reference, rigid geometry, and six TEXR IDs are
   already stronger.** The current parser frames all 367 measured streams,
   emits 366, and byte-round-trips all 367 while retaining opaque bytes
   ([`cmsh-mesh.md`](../asset-formats/cmsh-mesh.md):17-103,141-159).
3. **Skinning has advanced beyond the extractor.** The three stride-48 words are
   matrix-palette slots (`BONE index * 3`), not unnamed “bone weighting”; the
   combination/weight and bind rule remain open
   ([`cmsh-animation-usage.md`](../asset-formats/cmsh-animation-usage.md):104-125).
4. **CPOS/CORI are no longer generic unknowns.** They are bounded derived
   model-space caches indexed by virtual frame. Exact bitwise regeneration is
   not claimed.
5. **Two extractor claims are contradicted.** The byte at `CMVB+264` is a
   material group count, not the independent CMSH root texture count. The
   README's DXT2-only storage statement also overgeneralizes: the measured
   800-file shelf has 212 DXT1 and 588 DXT2 DDS files.
6. **`CCUS`, `BONW`, and `BONS` remain extractor-only.** None occurs in the
   complete measured CMSH tag census. A marker branch or skip formula is not a
   reason to add parser support without a hash-pinned specimen or writer/consumer.
7. **Several comments remain hypotheses.** TEXB's first 20 bytes are not proved
   “used region and scale”; serialized skipped words are not proved pointers;
   repeated BBOX is not proved an exporter bug; and the guncrab memory-saving
   story is an example, not universal ownership evidence.
8. **Legacy texture lookup is incomplete.** The extractor tries only
   `A1R5G5B5` then `A8R8G8B8`; the measured shelf has five source-format suffixes.
   Current shelf indexing is stronger than manufacturing two-name precedence.

## Removed release artifacts

### Exact Git and byte identities

The artifacts below are recoverable from `801f3ba` and deleted by `e7c6f37`.
Blob IDs are Git SHA-1 object identities; SHA-256 is over recovered bytes.

| Path | Git blob | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `AYAResourceExtractor.deps.json` | `34cf9fd88e70f4c32d0f56a2af290b3d283179d5` | 1,193 | `135815df5105b50c8eef77270dbb886930814418232b07b34b35b14d876096fb` |
| `AYAResourceExtractor.dll` | `b934825660bb2ec58143201d242a6922065ea2cc` | 27,648 | `a596120c30ff07f93f9239ec9c96fa93cafa5d45726f88c84de926b4f28b2699` |
| `AYAResourceExtractor.exe` | `b543274ff4876fc17c7ec6fc278c51110e2d4921` | 115,200 | `570acacefff4609fcbac8e4083dafa695ea8d6f97385b5b6bf499ac3b3219bf4` |
| `AYAResourceExtractor.runtimeconfig.json` | `54681bc90512a9391d322966541b25b4cdb80b1a` | 355 | `4c8a73c525364eac6cbe64191bc633ed1fc8c59db376660474f6834ce0b23800` |
| `DDSTextureUncompress.dll` | `6a98777df5c17acddb761cda4fd5bf7a6afd5fe8` | 90,112 | `4f921c54a987685ed5479bba2568156f61a3fefb0a25dc6c986c1a27db39e4e1` |
| `Fbx.dll` | `af38865f3b11bb0d58b8b0e737d559443953670b` | 30,208 | `62b8f32411a93c4a50f61a548d75188d4ab76a2f05f748b4b9d5770b9cb03236` |
| `ZLibWrapper.dll` | `49b8400fa4f5ad33a7b90ed60de078d0f691aead` | 105,472 | `a5143510cec10efbcda75a4a5853065e3370f85be70fb0e261187ce433bcb540` |

The dependency manifest names only the four project assemblies. The runtime
manifest targets .NET 6 and Microsoft.WindowsDesktop.App 6.0. No package,
resource, or private game dependency is hidden in either JSON.

### Managed metadata and release IL inventory (not source-build equivalence)

The metadata reader used `System.Reflection.PortableExecutable` and
`System.Reflection.Metadata`; it did not reflection-load or execute target
code. It recorded every type/member/signature, embedded resource identity,
method RVA, and SHA-256 of every available IL body. Two normalized runs were
byte-identical at SHA-256
`f0603f94c05dcf380611b5dd22282b5896b96fce64b28c15a0b301bcf6e9860c`.

Those fingerprints identify release bodies only. No source-built assembly IL
fingerprints were generated, so name/signature/resource correspondence does not
prove behavioral identity. In addition, the two mixed-mode wrappers contain 47
native/non-IL bodies (28 plus 19) that this metadata-only audit did not
semantically compare.

| Assembly | ECMA-335 result | Source comparison |
| --- | --- | --- |
| `AYAResourceExtractor.dll` | 19 type definitions; 67 method definitions; 67 release IL fingerprints; one 180-byte `AYAResourceExtractor.MainForm.resources` manifest with **zero entries**. | Fourteen application/source types match the C# tree by name/signature. `ApplicationConfiguration` is generated by the WinForms SDK; three nullable/embedded attribute types and `<Module>` are compiler artifacts. Constructors and property accessors account for binary methods beyond the 40 explicit source declarations. No extra public/internal named type or resource was found; body equivalence was not tested against a source build. |
| `Fbx.dll` | 29 type definitions; 111 methods; 103 release IL fingerprints; eight no-body delegate methods; no resources. | All named `Fbx.*` types/methods map by name/signature to the 13 surviving source files. Remaining types are compiler-generated delegates, closures, attributes, and static-array details. No extra named FBX type/resource or embedded template was found; body equivalence was not tested against a source build. |
| `DDSTextureUncompress.dll` | Mixed-mode PE/CLR: 462 type definitions, 274 methods, 244 IL fingerprints, 28 native/non-IL bodies, no resources. | The only application-facing managed type is `DDSTextureUncompress` with `Uncompress` and a constructor. The named metadata surface is C++/CLI/CRT/std machinery plus that wrapper, and the DLL predates the fork's rectangular-copy fix. The 28 native/non-IL bodies were not semantically compared, so hidden body-level differences cannot be excluded. |
| `ZLibWrapper.dll` | Mixed-mode PE/CLR: 543 type definitions, 179 methods, 158 IL fingerprints, 19 native/non-IL bodies, no resources. | The only application-facing managed type is `UnCompressFile` with `Uncompress` and a constructor. The named metadata surface is zlib/C++/CLI/runtime machinery plus that wrapper. The 19 native/non-IL bodies were not semantically compared, so hidden body-level differences cannot be excluded. |

The removed main DLL predates `8d9880e`; its string/IL surface has only the
direct `BoxWithTextures.fbx` lookup and lacks the later
`..\..\..\..\..\BoxWithTextures.fbx` Visual Studio fallback. This is a
surviving-source improvement, not binary-only knowledge.

### Native EXE and PE metadata

`AYAResourceExtractor.exe` has no CLR directory and no exports. Its imports and
strings are the expected .NET apphost surface (`hostfxr_main*`, registry/runtime
lookup, ShellExecute/MessageBox) plus `AYAResourceExtractor.dll`. It contains no
managed type/member/resource table and no AYA/CMSH token. The three other DLLs
have no exports; the two mixed-mode wrappers import normal CLR/C++ runtime
surfaces.

The binaries do reveal deterministic/build-machine path strings such as
`C:\dev\AYAResourceExtractor\Code\AyaResourceExtractor\obj\Release\net6.0-windows\AYAResourceExtractor.pdb`
and corresponding Fbx/wrapper PDB paths. Those paths identify the build tree;
no PDB was committed, and the strings add no format field or algorithm.

## `BoxWithTextures.fbx` is generic exporter scaffolding

The tracked template is 59,196 bytes, FBX 7.4 binary, SHA-256
`37526ffde1d48016fa8a2a05c5dfeb3cd0a30a8ab402ccce60a7f44addf8eed2`.
A source-built `Code/Fbx` reader produced byte-identical normalized reports on
two runs (SHA-256
`1148ed9b82fd428eeb1b9b92715ef17052372b655749a8e350a6749ad066847f`).
It contains:

- one `Geometry::Cube` and one `Model::Cube`;
- 24 `Material` objects named `Material1` through `Material24`;
- 24 generic `Texture::base_color_texture` objects;
- 24 `Video` placeholders pointing to `default1.png` through `default24.png`;
- eight cube vertices at ±1, six quad polygons, 24 polygon indices, generic UVs
  and normals;
- Blender 3.5 stable FBX IO metadata, `/foobar.fbx`, and a build path to
  `C:\dev\AYAResourceExtractor\Blender\24MaterialsOnBox.blend`.

No `Battle Engine Aquila`, CMSH tag, `.aya`, `.msh`, `.tga`, `meshtex`, game
resource name, retail payload, or extracted texture is present. The template is
generic placeholder scaffolding. Its 24-object ordering explains the exporter's
hard-coded node offsets and material ceiling; it does not establish a game
format limit.

## Comparison with Stuart's Onslaught drop

The tracked audit searched every text file at exact Onslaught pin
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb` for 29 extractor asset tags.
Every exact-word count is zero:

`CMSH CMST MSHT TEXB MESP CMSP CHLD PRNT NMIC BBOX CCUS CAMD VHFM HORI HPOS HFOV BONE BONW BONS PBKT CPOS CORI REFR PMVB CMVB MMPT IBUF VBUF TEXR`.

The drop does contain related but non-distinctive architecture:

- `CChunkReader::GetNext` reads four tag bytes and four size bytes, while
  `Read` bounds reads against that size (`references/Onslaught/chunker.cpp:151-195`);
- ten source lines contain literal `meshtex\\` paths, including default mesh
  textures (`references/Onslaught/DXEngine.cpp:207-218`), but there are zero
  `meshtex%` and zero `dxtntextures` strings;
- Direct3D `A1R5G5B5`/`A8R8G8B8`, FVF, and triangle-strip identifiers occur in
  ordinary renderer code (`references/Onslaught/DXEngine.cpp:510-524`);
- the resource builder/reader uses target-specific `.aya` resource names and
  the same generic `CChunkReader` architecture
  (`references/Onslaught/ResourceAccumulator.cpp:200-210,800-850`).

These facts show that the extractor decoded a format consistent with the same
engine lineage. They do **not** show copied in-house mesh code: the distinctive
CMSH vocabulary is absent, the extractor's names/control flow differ, and the
shared terms are ordinary engine/D3D/resource identifiers.

The provenance claim could be strengthened only by one of the following:

1. an authenticated missing mesh/texture loader source file containing the same
   distinctive tag order, offsets, and branch structure;
2. a matching original PDB/source-index record that ties extractor routines to
   an in-house source owner;
3. a byte/IL/native fingerprint demonstrating shared non-library code rather
   than common zlib/D3D/FBX machinery; or
4. a primary statement from the author identifying the source of the recovered
   layouts.

Absent that evidence, the strongest defensible conclusion is “independent or
unproven reverse engineering informed by the same game's files,” not “original
game code published.”

## Prioritized follow-up defects

Only actual gaps survive this audit:

1. **P1 — skinning/blending:** recover how the three matrix-palette slots combine,
   their weights, bind matrices, and the exact skeletal runtime consumer. The
   extractor adds no hidden answer.
2. **P2 — TEXR layers:** close slot positions/blend rules beyond the bounded
   slot-zero diffuse route and `0xFFFFFFFF` sentinel before claiming material
   parity.
3. **P2 — PB family:** join one exact PBKT/PB* instance to its retail consumer;
   the extractor only skips PBKT by length.
4. **P2 — component provenance:** recover/pin the missing DDSReader/FreeImage
   license chain and the Hamish Milne FBX license before redistribution. Keep
   root MIT, zlib, DDS/FreeImage, and FBX terms separate.
5. **P3 — disputed labels:** trace TEXB's first 20 bytes, `CMSP+0xB4` aFrames,
   NMIC, and skipped serialized words to exact consumers. Do not promote
   “scale/region,” “pointer,” or “BBOX bug” labels meanwhile.
6. **P3 — topology/normals:** close remaining FVF/topology combinations and one
   rendered winding/normal falsifier; the README symptom is not a decoded rule.
7. **P3 — legacy texture resolution:** if the legacy harness becomes a product
   surface, replace two-suffix-only lookup with measured shelf indexing and add
   output-name collision checks. Current research tooling already supersedes it.

No follow-up is warranted merely to add `CCUS`/`BONW`/`BONS`, copy the 1 MiB/4
MiB buffers, recreate the 1,000-part or 24-material limits, or preserve the
extractor's pointer/bug guesses.

## Reproduction and gates

Tracked deterministic audit:

```powershell
py -3 tools/aya_extractor_source_audit.py `
  --out local-lab/hermes-kanban-campaign-2026-08-22/aya-extractor-audit/source-audit.json
py -3 tools/aya_extractor_source_audit_tests.py
```

The canonical-blob source report was generated twice and compared
byte-for-byte, then reproduced from clean LF and CRLF source materializations;
all outputs were 30,173 bytes with SHA-256
`a1dc799b5854db1d5011a39a360d7e553883d0d66dfc46d3893aa31417988dad`.
It records 73/73 categorized files, 40/40 first-party routines, 92/92 contract
rows, zero unclassified assumptions, both exact pins, and zero Onslaught hits
for every extractor format token.

Ignored bounded receipts include:

- `source-audit.json` / `source-audit-second.json`;
- `function-inventory.json`;
- `managed-metadata.json` / `managed-metadata-second.json`;
- `pe-inventory.json` / `pe-inventory-second.json`;
- `fbx-template.json` / `fbx-template-second.json`; and
- recovered blobs under `removed-release/`.

The removed blobs themselves must never be added or redistributed.

## Claim boundary

This audit proves what the public repository and removed release metadata
contain. It does not prove author intent behind binary deletion, original game
source authorship, Steam build identity, runtime rendering, malformed-input
behavior, full material semantics, animation scheduling, skinning weights,
license approval, or general parity. Current corpus/runtime owners continue to
outrank extractor guesses.
