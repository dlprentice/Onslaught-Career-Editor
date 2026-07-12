# Rebuild Contributor Rules

Status: active for `rebuild/`
Last updated: 2026-07-12

This subtree is the RE-informed original-code rebuild lane. It is separate from
the MIT-licensed toolkit and is licensed under GPL-3.0-or-later; see
`rebuild/LICENSE` and `rebuild/PROVENANCE.md`.

- Do not describe this subtree as a strict clean-room implementation.
- Do not copy source text, headers, symbols, comments, assets, binaries, or
  generated payloads from `references/Onslaught`, `BEA.exe`, Ghidra output, or
  the installed game into rebuild source.
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
- Pin Godot with a tracked manifest containing the official archive URL, exact
  length and SHA-256, expected runtime identity, and a complete extracted-file
  inventory. Every setup/build/run/smoke path must verify the cache; never trust
  an ambient Godot install or silently repair an unexpected extracted tree.
- Normal setup must accept only the exact tracked manifest and fixed per-user
  cache root. Reject reparse-point cache paths, retain the setup lock through
  consumers, and hold verified files against write/delete until the consumer
  exits. Do not claim isolation from an already malicious same-user process.
- Safe extraction must reject traversal, absolute or escaping paths,
  case-insensitive duplicates, links, missing files, and extra files. Downloads
  must use the allowlisted HTTPS origin, bounded redirects, a staging file, and
  exact length/hash checks before installation.
- Keep proprietary game files optional and outside this subtree. The baseline
  rebuild must build, test, and run without them.
- The final-state hash proves canonical continuation state and the rolling
  trace hash proves one complete input/post-step history. Screenshots prove
  only that a client rendered a bounded frame; none proves game parity.
- Native smoke acceptance requires state/report validation, semantic
  HUD/player/sentry/world anchors at default and minimum viewports, bounded
  process ownership, and clean exit. A screenshot or same-process report alone
  is not an acceptance artifact. A direct notification-handler probe is not an
  OS focus-transition proof.
- Add focused tests for every simulation behavior change and update both
  independent goldens only when the contract change is intentional and
  reviewed.
- A reviewed golden change updates three explicit loci together:
  `scenarios/first-flight.v1.json`, the constants in `ReplayTests.cs`, and the
  independent constants in `HeadlessApplication.cs`. Generate candidate hashes
  with an explicit tape plus `--no-verify`; the normal built-in run must then
  verify both values and report `headless-built-in-golden`.
- Run `npm run test:rebuild` for ordinary changes. Run
  `npm run test:rebuild-godot-smoke` when native Godot behavior, rendering,
  input, or launch scripts change; use `-Offline` on the underlying PowerShell
  script when acceptance must prove cache-only operation.
