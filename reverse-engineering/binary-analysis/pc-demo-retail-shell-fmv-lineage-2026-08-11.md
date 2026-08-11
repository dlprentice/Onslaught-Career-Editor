# PC demo/retail shell and FMV lineage

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — three complete reachable shell bodies in the exact PC demo
and pristine retail executable, one complete demo-only helper, mapped direct
calls, literal media/debug strings, and read-only demo filesystem inventory;
UNKNOWN — successful playback of two absent promotional files, media output,
and the original symbol for the demo-only helper.
Verdict: the demo factors startup-movie policy into a separate helper and adds
the `publisher` clip to every startup/attract sequence. Its frontend loop adds
the same clip when attract mode restarts, while its shutdown requests one of
two language-selected `BEA_promo` movies. Retail keeps its startup sequence
inline, omits the publisher insertion from attract restart, and begins shutdown
directly with common resource teardown.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, 2,510,848 bytes, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

The machine-readable result is
[`pc-demo-retail-shell-fmv-lineage-2026-08-11.tsv`](pc-demo-retail-shell-fmv-lineage-2026-08-11.tsv).
It is 2,121 bytes with SHA-256
`665dc49c70aa21d202970d53b55f64676dc5a5c79f24449ccb4eab6b1ca66bf6`.
The three retail bodies total 2,259 bytes / 600 instructions; the paired demo
bodies total 1,990 bytes / 517 instructions. Body hashes and exact extents are
retained in the table. This closes three more of the original 65 changed or
incompletely bounded body rows: eleven are now semantically bounded and 54
remain.

## Complete-body recovery

The demo bodies were recovered with a reachable-control-flow decoder bounded
by the next independently mapped entry. As a refutation check, the same decoder
reproduced all three retail Ghidra bodies exactly:

| Function | Retail | Demo |
| --- | ---: | ---: |
| `CLTShell::InitializeRuntimeAndLoadCoreResources` | 1,468 B / 384 instructions | 1,120 B / 273 instructions |
| `CLTShell::ShutdownRuntimeAndReleaseResources` | 273 B / 60 instructions | 325 B / 77 instructions |
| `CLTShell::RunFrontEndAndGameLoop` | 518 B / 156 instructions | 545 B / 167 instructions |

All six bodies are contiguous from entry through their last reachable byte.
This avoids treating the unmapped code between demo initialization and the next
mapped function as padding or as part of the initializer.

## Demo-only startup helper

Demo initialization `0x004EFAA0` performs the shared platform, controller,
FMV, sound/music, splash, text, font, resource, mesh, texture, physics, and
memory-base setup. Where retail `0x004EFB10` implements the startup/attract
movie branches inline, the demo calls an otherwise unmapped function at
`0x004EFF00` and then resumes the common resource path.

The helper is independently bounded:

| Property | Value |
| --- | --- |
| Extent | `0x004EFF00–0x004F00F3` |
| Body | 500 bytes / 164 instructions |
| SHA-256 | `c5a0b9349c998d05d92d3f881b8ca90dcae96082dc3a9363d0b6af7e44201ace` |
| Callsite | demo initializer `0x004EFCF9` |

The first argument is formed by `SETNE` from demo global `0x0066438C`; the
corresponding retail inline branch reads `0x006630CC`. The helper's own
`"we're in attract mode"` branch fixes that value as the attract-path
predicate. The second call argument is constant `1` and is forwarded into one
explicit playback-parameter position; its higher-level name remains open.

The helper has three exact paths:

- attract: `publisher`, `ltlogo`, optional
  `TWIMTBP_GefFX_640x480_Audio`, then `openingfmv`;
- ordinary first sequence: `copyright`, `publisher`, `atari`, `lostlogo`, then
  `introntsc`;
- alternate first sequence: `publisher`, `ltlogo`, optional
  `TWIMTBP_GefFX_640x480_Audio`, then `openingfmv`.

Every `publisher` operand reaches paired demo
`CFMV::PlayFullscreenWithLoadingGate @ 0x00465680`. Retail's inline equivalents
contain the same surrounding product movies but no `publisher` operand. The
extracted demo contains `BattleEngine/EXE/publisher.vid`, 1,432,996 bytes,
SHA-256
`c251f4be8ab7f2ac5d4f6b952ca44d0cf5aadd7552ad61725420009a6f0e79ba`.

This helper is a bounded semantic identity, not a recovered original symbol or
proof that the source compiler emitted it under a particular name.

## Attract restart adds the same publisher clip

Retail `CLTShell::RunFrontEndAndGameLoop @ 0x004F0330` and demo
`0x004F0390` otherwise retain the same frontend/game result loop, stress-test
route, splash ownership, memory-stat calls, and attract restart sequence. Demo
inserts eleven instructions at `0x004F04DA–0x004F04F4`:

1. submit `ltlogo` through the full-screen wrapper;
2. stop the remaining sequence when that call returns nonzero.

The normalized alignment places demo's preceding `publisher` call at
`0x004F04CC` against retail's first `ltlogo` call. Read with the inserted block,
the exact demo order is therefore `publisher` then `ltlogo`, followed by the
shared optional NVIDIA movie and `openingfmv`. Retail starts directly with
`ltlogo`.

The helper contains three `publisher` references and this loop contains the
fourth, reproducing all four executable references reported by the earlier
FMV/startup census.

## Demo-only shutdown promotion

Demo `CLTShell::ShutdownRuntimeAndReleaseResources @ 0x004F0110` prepends a
17-instruction block to the shared teardown body. When its initialized
playable-demo global `0x00633B1C` is nonzero, it reads the demo
American-English global `0x0083EC50` and selects:

| American-English state | Movie name |
| --- | --- |
| Nonzero | `BEA_promo1` |
| Zero | `BEA_promo2` |

The selected name is passed once to the full-screen wrapper. The body then
falls through to the same ordered cleanup as retail: definition lists, loading
state, text, resources, mesh/texture handles, optional music/sound, fonts,
console, rendering globals, event/damage state, and pointer-set shutdown.
Retail `0x004F00E0` begins directly at that common tail.

Neither `BEA_promo1` nor `BEA_promo2` is present as a file in the read-only
extracted demo tree. That negative is kept explicit: the executable request is
proven, but successful playback from this distributed demo package is not.
Archive indirection or an unavailable distribution companion remains possible.

## Boundary and next use

The recovered claims are complete body identity, factoring, call order, literal
movie names, edition gates, and common lifecycle tails. They do not prove video
frames, codec behavior, device timing, why the promotional files are absent,
or source equivalence.

The practical result is another coherent reduction of the changed-body queue,
not a reclassification of the 8,021 bodies already normalized-identical. The
next pass should continue with a different related cluster among the remaining
54 changed bodies or use platform executables to address the 50 retail entries
still lacking a demo address.
