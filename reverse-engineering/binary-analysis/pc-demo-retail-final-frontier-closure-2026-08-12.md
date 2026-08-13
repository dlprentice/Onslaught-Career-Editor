# PC demo/retail final function frontier closure

Status: complete for its dated 8,136-function population; current census larger
Last updated: 2026-08-13
Evidence: MEASURED — exact specimen hashes, complete body and boundary decode,
mapped caller/callee sequences, paired string and code-pointer operands, a
complete MSVC `FuncInfo` census, ordered code/metadata neighbors, and an
independent replay; SOURCE — pinned `game.cpp` lifecycle and controls-screen
ownership; UNKNOWN — runtime execution, exact original source/compiler
revision, and reconstruction parity.
Verdict: all four rows left by the exact-fingerprint checkpoint now have a
defensible terminal state. Three have bounded demo entries and semantic
lineage; the fourth is a retail-only compiler-EH cleanup package whose parent
block and metadata are absent from the demo. The complete 8,136-function retail
inventory is now partitioned as 8,119 normalized-identical demo bodies, 16
bounded semantic divergences, and one proven retail-only compiler package, with
zero address-unresolved rows. Exactly 8,135 retail functions have demo entries.
The 34 Mission-registry boundaries promoted on 2026-08-13 are outside this
sealed map, so this partition must not be projected over the current
8,170-function retail census; those 34 demo counterparts remain open.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, 2,510,848 bytes, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

The tracked machine-readable result is
[`pc-demo-retail-final-frontier-closure-2026-08-12.tsv`](pc-demo-retail-final-frontier-closure-2026-08-12.tsv),
four rows, 3,005 bytes, SHA-256
`8a58b2a2c81fdc99aa8f191bf2944eb728aa0d0ac91035cc5009986867094bd9`.

## Acceptance gate

The prior
[exact-fingerprint checkpoint](pc-demo-retail-exact-fingerprint-closure-2026-08-11.md)
left three edition-divergent bodies and one compiler-generic unwind body. This
pass did not weaken the exact-body rule. It changed instruments and required
different evidence for each class.

A divergent demo entry was accepted only when:

1. mapped lower and upper neighbors bound one unclaimed entry and its complete
   terminal body, including any owned jump table;
2. complete retail and demo bodies decode gaplessly;
3. mapped direct-call order, paired literal operands, and corresponding callers
   identify the same semantic owner rather than merely a nearby function;
4. every material instruction-block difference has a bounded source/dataflow
   explanation; and
5. the proposed addresses remain one-to-one with all 8,132 prior mappings.

A no-counterpart result required positive absence evidence: an exhaustive
candidate check, ordered mapped packages on both sides, exact removal size,
parent ownership, and an independently reproduced metadata census. Mere failure
to find a body was not accepted.

The three mapped bodies contain 2,337 retail bytes / 631 instructions and 2,027
demo bytes / 566 instructions. Their direct-call spines contain 86 retail and
74 demo calls; every demo call aligns in order, and mapped `CGame::RunLevel`
reproduces all 26 direct targets after the three additions. The final arithmetic
is exact:

| Cross-build terminal state | Before | Added | After |
| --- | ---: | ---: | ---: |
| Normalized-identical bodies | 8,119 | 0 | 8,119 |
| Bounded semantic divergences | 13 | 3 | 16 |
| Proven retail-only compiler packages | 0 | 1 | 1 |
| Address-unresolved rows | 4 | -4 | 0 |
| Retail functions with demo entries | 8,132 | 3 | 8,135 |
| Complete retail inventory | 8,136 | 0 | 8,136 |

`8,119 + 16 + 1 = 8,136`.

## Three bounded demo entries

### `con_fmv_play`: `0x004655D0 -> 0x00465600`

The mapped `CFMV` carrier pair `0x004656B0 -> 0x00465700` pushes the proposed
handler pointer at the same body offset. Both handlers carry the sole paired
`"Syntax : fmv_play <filename>\n"` reference and the same three mapped direct
calls. Their mapped neighbors, terminal returns, and intervening padding bound
the complete bodies at 110 retail bytes / 41 instructions and 120 demo bytes /
42 instructions.

Forty-one normalized instruction tokens align. The only inserted demo
instruction writes `1` to demo `CFMV+0x10` before the shared non-interactive
playback path. The earlier
[FMV/startup lineage](pc-demo-retail-fmv-startup-lineage-2026-08-11.md)
independently fixes demo `CFMV+0x10` as the per-playback `can_skip` field and
proves that retail removed that field while shifting the DirectX backend
subobject into its place. The handler therefore has a bounded edition
difference, not an unexplained constant mismatch.

### `CGame::ShutdownRestartLoop`: `0x0046CA70 -> 0x0046CAA0`

The candidate lies between mapped `CGame::Shutdown` and
`CGame::LoadResources`, carries the paired
`"Freeing Up Level Resources..."` operand, and preserves all 33 mapped direct
calls in exact order. Mapped `CGame::RunLevel` calls retail `0x0046CA70` three
times at the same semantic positions where demo `RunLevel` calls
`0x0046CAA0`.

The complete bodies are 696 retail bytes / 182 instructions and 679 demo bytes
/ 179 instructions. Retail alone contains the eight-instruction prelude that,
when quit code 4 and playable-demo state are both active, sets the temporary
controls/loading flag. Both builds retain the later quit-code loading call and
the same ordered teardown spine. This matches the ownership and ordering in
`references/Onslaught/game.cpp:530` without treating that source as exact
retail revision identity.

### `CGame::RestartLoopRunLevel`: `0x0046DC30 -> 0x0046DC40`

The candidate lies between mapped `CGame::PlayMusicForCurrentLevel` and
`CGame::RunLevel`. Both bodies carry the paired `Post Load %d`,
`dumptimerecords`, command-description, and `autoexec.con` operands. Demo's 38
direct calls form an exact ordered subsequence of retail's 50, including two
calls to the newly paired shutdown body. `CGame::RunLevel` calls the proposed
entries at the same position in its otherwise exact 26-target direct-call
sequence.

The complete function body is 1,531 retail bytes / 408 instructions and 1,228
demo bytes / 345 instructions, followed in the demo by a verified four-entry
indexed jump table. Of the demo stream, 329 normalized instruction tokens align
with retail. The single material deletion is retail's 64-instruction inline
wait-for-start controls-screen block from the source region beginning at
`game.cpp:1283`. Its exact twelve direct calls are loading-range/render,
controller handoff, clock/process polling, inactivity testing, and local-object
cleanup. Demo omits that block while preserving the level load, post-load,
intro, startup script, pre-run, music, main loop, end-data, sound, atmospherics,
texture-pool, player, and camera spine.

## Why `Unwind@005D2930` is retail-only

The 11-byte retail body is a two-instruction cleanup funclet that forms ECX as
`EBP-0x114` and jumps to the local cleanup target. Shape alone produced 59 demo
candidates; all 59 are already claimed by other one-to-one retail mappings.
That negative is not the terminal proof.

The terminal proof is the surrounding compiler package:

- retail `RestartLoopRunLevel` begins with an FS:[0] exception registration and
  pushes handler stub `0x005D293B`; demo `0x0046DC40` begins directly with a
  `0x100`-byte local frame and contains no FS:[0] setup;
- retail `FuncInfo 0x0061B6F8` has one unwind-map action,
  `0x005D2930`; the complete retail census contains 506 valid records while
  demo contains 505;
- the uniquely mapped retail records immediately around it are
  `0x0061B6C8` and `0x0061B720`; their demo twins are
  `0x0061C6C8` and `0x0061C6F8`, and those demo records are exactly adjacent;
- mapped code entries `0x005D2909 -> 0x005D3009` and
  `0x005D2950 -> 0x005D3030` enclose a span that is exactly `0x20` bytes shorter
  in the demo; retail's missing span is precisely the 11-byte action, 10-byte
  handler stub, and 11 bytes of padding; and
- the parent-level difference is the same controls-screen local and cleanup
  block independently removed by the body/call alignment above.

This proves a retail-only compiler-generated cleanup package tied to the
retail-only inline controls wait. It does not prove a universal compiler rule,
runtime exception delivery, or that no higher-level controls experience exists
elsewhere in the demo.

## Reproduction and limits

The ignored analyzer package is
`local-lab/pc-demo-retail-final-frontier-20260812-v1/`. Its resolver is 31,698
bytes, SHA-256
`fdc42f88f4073af184540d3752850984d7e92649241a9cb3104de73491f1e6e0`;
its 7,846-byte result receipt has SHA-256
`e3d6d6c11491cc6cf381a53834d9d24f0a2eb5d17025ecc9b1a2f420f0a31fd9`.

The independently implemented replay is
`local-lab/pc-demo-retail-final-frontier-verify-20260812-v1/verify.py`, 19,219
bytes, SHA-256
`9727ddcadbef15ce2f367cace68b3f5c2da1bfbd84efab2add51f59a13af0744`.
Its 1,800-byte receipt has SHA-256
`1ef64360d469d8fe3f933c9ae241e168e1f9915985523b1ae75257ad7c6fe8fa`
and verdict `PASS`.

This closure made no live or tracked Ghidra mutation and no rebuild change. It
closes the specimen-specific address frontier; it does not promote runtime
causality, prove exact source/compiler identity, or establish Godot parity.
