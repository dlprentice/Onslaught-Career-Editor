# Rebuild Contributor Rules

Status: active for `rebuild/`
Last updated: 2026-07-11

This subtree is the RE-informed original-code rebuild lane. It is separate from
the MIT-licensed toolkit and is licensed under GPL-3.0-or-later; see
`rebuild/LICENSE` and `rebuild/PROVENANCE.md`.

- Do not describe this subtree as a strict clean-room implementation.
- Do not copy source text, headers, symbols, comments, assets, binaries, or
  generated payloads from `references/Onslaught`, `BEA.exe`, Ghidra output, or
  the installed game into rebuild source.
- Keep `OnslaughtRebuild.Core` deterministic, fixed-step, integer-based, and
  free of Godot, WinUI, filesystem, clock, process, network, and GPU APIs.
- Treat render clients as adapters over Core snapshots. They do not own or
  mutate simulation truth.
- Keep proprietary game files optional and outside this subtree. The baseline
  rebuild must build, test, and run without them.
- The final-state hash proves canonical continuation state and the rolling
  trace hash proves one complete input/post-step history. Screenshots prove
  only that a client rendered a bounded frame; none proves game parity.
- Add focused tests for every simulation behavior change and update both
  independent goldens only when the contract change is intentional and
  reviewed.
- A reviewed golden change updates three explicit loci together:
  `scenarios/first-flight.v1.json`, the constants in `ReplayTests.cs`, and the
  independent constants in `HeadlessApplication.cs`. Generate candidate hashes
  with an explicit tape plus `--no-verify`; the normal built-in run must then
  verify both values and report `headless-built-in-golden`.
