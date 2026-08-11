# PC demo/retail credits and hard-coded localization lineage

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — exact contiguous bodies from the pinned executables,
complete x86 decode, all hard-coded credits writes, both credits row helpers,
all five 249-entry localization dispatch tables, the demo-only auxiliary table,
and resolved returned strings; UNKNOWN — credits row rendering/filtering,
runtime-populated binding-label contents, external language-file contents, and
whether the localized fatal path is reached in normal play.
Verdict: both initially changed bodies are now accounted for logically. The
demo inserts 25 credits rows without changing or reordering any of retail's 222
rows. Its hard-coded localization changes only error ID 183 from a DirectX 8
message to DirectX 9 in all five languages. The extra demo American-English
dispatch table is an exact 249-target alias of ordinary English.

Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
paired PC demo `BEA.exe`, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

Exact sizes:

- pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
  `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
- PC demo `BEA.exe`, 2,510,848 bytes, SHA-256
  `d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

The function-level result is
[`pc-demo-retail-credits-localization-lineage-2026-08-11.tsv`](pc-demo-retail-credits-localization-lineage-2026-08-11.tsv),
762 bytes, SHA-256
`1f2921a22a6884816c65d69a0252c2913a2f4e6b6288711f53b998eae76042bb`.
The exact inserted credits rows and five localized text changes are retained in
[`pc-demo-retail-credits-demo-insert-2026-08-11.tsv`](pc-demo-retail-credits-demo-insert-2026-08-11.tsv)
and
[`pc-demo-retail-localization-deltas-2026-08-11.tsv`](pc-demo-retail-localization-deltas-2026-08-11.tsv).

## Credits table

`CCredits::BuildDefaultEntries` is retail `0x00518BF0–0x00519FE4`
(5,109 bytes / 986 instructions; raw body SHA-256
`ffd876bc48a6b6bbc7c362a27e2046755b32fef765aceda9985de3fcd02963d7`)
and demo `0x00518C90–0x0051A2C4` (5,685 bytes / 1,095 instructions;
`d2340c8a710274c6ed955ef2b76ca57a834b9b0cbbd053d963394deb160c1d87`).
Both bodies are straight-line initializers: their only instruction forms are
constant/register setup, row stores, pushes, calls to the two row helpers, and
the terminal register restores/return.

The paired helper bodies preserve the exact 16-byte row forms:

- localized row: `{section, text_id, 0, style}`;
- literal row: `{section, -1, text_pointer, style}`.

Evaluating every direct store and helper call recovers 222 retail rows at
`0x00896CA8–0x00897A87` and 247 demo rows at
`0x00897F68–0x00898ED7`. A logical sequence comparison has one and only one
edit: demo rows 92–116 are inserted before the row corresponding to retail
index 92. Every retail row before and after that point is otherwise present in
the same order with the same section, row kind, value, and style. Both tables
retain the final `{3, 0, 0, 3}` row.

The 25-row demo insertion contains eleven numeric rows and fourteen literal
name rows:

`Kevin Hoekman`, `Fadi Awed`, `Andrew Simpson`, `Ron Duke`, `Jill Griffin`,
`Richard Lowenthal`, `Betsi Shepherd`, `Linda Duttenhaver`, `Candice Uyloan`,
`Thom Dohner`, `Mike Bell`, `Ken Sepulveda`, `Dave Worle`, and
`Dawn & Brittany`.

All eleven numeric rows use section 1 and text ID 0; one uses style 0 and ten
use style 1. The binary proves those values, but it does not by itself prove
whether the renderer treats them as headings, spacing, or another credits
control. The names are therefore retained without invented job titles. The
existing PC-version programming/test rows are present in both builds and are
not part of this insertion.

The canonical logical row hashes are
`0b415da05bb630da3c1b626a72f596e358150068fdb53bc02a67851395af54df`
(retail) and
`5d3df7561513706dfd69410ca36bcaf2e2d2ef9c35476ce89326f582f254c0db`
(demo).

## Hard-coded PC localization

`Localization::GetStringById` is retail `0x00524830–0x00526097`
(6,248 bytes / 2,061 instructions; raw body SHA-256
`9ca8630f096477241c5055d9429f0c97c6fbea41cc48bf6b90807e7178a29004`)
and demo `0x00524B40–0x005263CD` (6,286 bytes / 2,069 instructions;
`e124508cde93c0960f72afecbb9f7cfc8d5411a12ba9184d43f7486273c5d383`).

The ordinary dispatch surface is five languages × IDs 0–248 = 1,245 slots
per build. The comparison follows each primary jump-table entry, the common
fallback dispatch used by PC key/control labels, and the terminal return stub.
Six IDs (`58`, `63`, `68`, `71`, `77`, and `80`) intentionally return one
runtime-populated wide buffer in every language; retail `0x00677D78` and demo
`0x00679038` are the paired storage locations rather than file-backed strings.

Exactly five primary slots differ: ID 183 in English, French, German, Spanish,
and Italian. Each retail string says DirectX 8 (or version 8 or later), while
the paired demo string says DirectX 9. The other 1,240 primary slots resolve to
the same text or the paired runtime buffer. This is a changed diagnostic and a
useful build-lineage signal; it does not alone prove which DirectX capability
actually fails before the message is selected.

The demo adds three instructions at entry to read its American-English flag and
select a second ID table at `0x005267C8`. That table's 249 code targets are
exactly equal, dword for dword, to the ordinary demo English table at
`0x005263E4`. It therefore adds policy structure but no hard-coded string
difference in this executable. `CText::Init` can still select a separate
`american.DAT`; this result does not claim that external language data is
identical.

The primary logical mapping hashes are
`ca6393d96a260b98adbb0b1cb5c0212fdb3222fcd2ebdc9d503216b876651cb9`
(retail) and
`e9c2d33ed1d82db07482a5a8f5a69c56a967f4241df33eee28337d72d2832434`
(demo). Their difference is fully represented by the five ID-183 rows.

## Campaign consequence and boundary

These are semantic closures, not another static relabeling pass. They reduce
the original 65-entry address-mapped changed/incompletely-bounded queue from 52
to 50 after the previously recovered startup, FMV, frontend, shell, and
text-core groups.

The ignored reproducer is
`local-lab/pc-demo-retail-credits-localization-20260811-v1/`. It pins both
specimen hashes, rejects incomplete body decodes, statically evaluates every
credits write, resolves every localization dispatch target, requires the exact
single credits insertion and five ID-183 deltas, and requires the demo American
table to equal English target-for-target.

Still open are the credits renderer's section/style interpretation, which of
the inserted section-1 numeric rows are visibly emitted in the demo, contents
written to the shared runtime binding-label buffer, external `.DAT` language
files, and runtime presentation/error-path parity.
