# Rebuild Contributor Rules

Status: active for `rebuild/`
Last updated: 2026-07-12

This subtree is the RE-informed original-code rebuild lane. It is separate from
the MIT-licensed toolkit and is licensed under GPL-3.0-or-later; see
`rebuild/LICENSE` and `rebuild/PROVENANCE.md`. Read `rebuild/README.md` for the
current architecture, commands, toolchain, input, and golden-hash contracts.

- Do not describe this subtree as a strict clean-room implementation.
- A future strict clean-room lane requires separately staffed specification,
  implementation, and acceptance roles. The current source-exposed team and
  implementation cannot be relabeled as that lane.
- Do not copy source text, headers, symbols, comments, assets, binaries, or
  generated payloads from `references/Onslaught`, `BEA.exe`, Ghidra output, or
  the installed game into rebuild source.
- Retail-derived behavior enters through an accepted public-safe contract that
  labels source hypotheses, Steam static evidence, copied-runtime measurement,
  constants/tolerances, and non-claims. The rebuild cannot validate retail
  truth by agreeing with itself.
- Keep `OnslaughtRebuild.Core` deterministic, fixed-step, integer-based, and
  free of Godot, WinUI, filesystem, clock, process, network, and GPU APIs.
- Keep real-time accumulation and input edge/pulse handling in
  `OnslaughtRebuild.Client`; it may schedule Core steps but may not contain
  presentation or engine dependencies.
- Treat render clients as adapters over Core snapshots. They do not own or
  mutate simulation truth.
- Keep the Godot project out of `OnslaughtRebuild.slnx`; ordinary deterministic
  tests must not download an engine, open a window, or require a GPU. Use
  `OnslaughtRebuild.Visual.slnx` and the scripts under `rebuild/tools/` for the
  native client.
- The pinned-manifest/cache/download/extraction contract in `rebuild/README.md`,
  `rebuild/toolchains/`, `rebuild/tools/`, and their tests is normative for
  toolchain changes: verify the exact official archive and extracted inventory,
  reject unsafe paths/links/duplicates, preserve lock and held-file guarantees,
  and never trust an ambient engine. This is integrity hardening, not a sandbox
  against a malicious same-user process.
- Keep proprietary game files optional and outside this subtree. The baseline
  rebuild must build, test, and run without them.
- The final-state hash proves canonical continuation state and the rolling
  trace hash proves one complete input/post-step history. Screenshots prove
  only that a client rendered a bounded frame; none proves game parity.
- Native smoke acceptance requires validated state/report evidence, semantic
  rendered anchors at supported viewports, bounded process ownership, and clean
  exit. A screenshot or same-process report alone is not an acceptance artifact.
- Add focused tests for every simulation behavior change and update both
  independent goldens only when the contract change is intentional and
  reviewed.
- A reviewed golden change updates the packaged scenario and both independent
  test/headless constants together. Generate candidates only with an explicit
  tape plus `--no-verify`; the normal built-in run must then verify both values.
- Run `npm run test:rebuild` for ordinary changes. Run
  `npm run test:rebuild-godot-smoke` when native Godot behavior, rendering,
  input, or launch scripts change; use `-Offline` on the underlying PowerShell
  script when acceptance must prove cache-only operation.
