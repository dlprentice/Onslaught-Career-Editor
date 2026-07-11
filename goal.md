# Active Goal

Status: ACTIVE
Last updated: 2026-07-11
Policy: `goal.policy.md`

## Objective

Turn Onslaught Toolkit into a high-quality preservation, modding, and rebuild
project that is pleasant for contributors to understand and change. Improve
repository structure, contributor workflow, WinUI usability, patch/mod
correctness, reverse-engineering quality, Lore quality, and runnable
RE-informed original-code rebuild capability without overstating evidence or
publishing proprietary game payloads. Preserve a separately staffed sealed-spec
clean-room path as a future option rather than a current claim.

## Current Slice

Improve WinUI first-use clarity and accessibility using the existing visual
language and native runtime evidence:

1. make missing game-folder setup the clear first action on a true first run;
2. keep launch-preset selection truthful when debug-trace arguments change;
3. clear stale live-region status and restore useful focus on cached navigation;
4. fix the compact-width clipping in safe-copy executable selection;
5. add semantic Level 1 page headings and consistent arrival focus; and
6. repeat native visual and UI Automation checks in an isolated run so incidental
   desktop input cannot contaminate acceptance evidence.

The preceding filesystem-safety slice is accepted. Save/options writes, asset
catalog discovery, package materialization, downstream package outputs, Python
generated-output tools, and the C# AYA export harness now use bounded roots,
held identities, guarded final writes, and hostile-path tests. The remaining
same-user boundary is explicit: after final bytes leave delete-pending
quarantine, another process with the same account authority may copy or create
a byte-identical hardlink, just as it can after publication. No nonfinal bytes
or writes to pre-existing source/game identities are accepted. This creates no
release, gameplay, visual-parity, online, Ghidra read-back, or rebuild proof.

## Verified Starting Point

- Public release `v1.0.9` remains the latest published unsigned portable WinUI
  ZIP. It includes the friendly root layout, SHA-256 sidecar, and 949-document
  offline Lore pack.
- The Sol Ultra baseline was committed and pushed at
  `5a7bacecac5e813804355d68a8e51973100e0331`; local `main`, `origin/main`, and
  live remote `refs/heads/main` matched with divergence `0 0`.
- The contributor authority and quick-check advancement was committed and
  pushed at `798c339505fb85cc782abbd4b07df81e143c2284`; `npm test` is now the
  normal active-product baseline.
- Git reports one registered worktree. Seven Codex Desktop worktree entries
  were empty zero-byte shells with no Git metadata or linked conversations and
  were removed on 2026-07-11.
- Sixty-one historical `campaign/*` and `codex/*` branch tips were preserved
  in a verified local Git bundle before branch cleanup. Twenty-four otherwise
  unreachable commits and all three stashes were also preserved. Both bundles
  passed `git bundle verify` and a disposable restore drill. Four
  `backup/*` refs remain separate and outside every deletion list. After the
  pushed baseline was accepted, the 61 obsolete local branch names were
  removed; no backup ref, stash, archive ref, object, or Git GC was touched.
- The repository currently has 19,389 tracked files, including 13,385 under
  `reverse-engineering/`, 2,614 under `tools/`, and 1,710 under
  `release/`.
- Before this slice, root `package.json` exposed 1,494 scripts, including 1,472
  test scripts and 840 Ghidra wave scripts, with no default `npm test`. The
  history remains, but contributors now get one explicit quick-check entry.
- Baseline checks passed on 2026-07-11:
  - `git diff --check`
  - state JSON parsing
  - `npm run test:doc-commands`
  - `npm run test:repo-hygiene`
  - `npm run test:hard-payload-safety`
  - `npm run test:public-allowlist`

The exhaustive hygiene and payload gates each scan roughly the entire tracked
tree and took about two to four minutes locally. They remain valuable signoff
gates, but they are not an ergonomic default for every small contribution.

## Authority And Boundaries

The user authorized source, documentation, test, tooling, and local cleanup
work plus verified commits and pushes for this campaign.

- Keep the installed game and original `BEA.exe` read-only.
- Patch and runtime workflows use copied targets or app-owned roots.
- Do not commit proprietary game payloads, copied executables, arbitrary saves,
  extracted assets, screenshots/frame dumps, raw debugger logs, full Ghidra
  databases, secrets, build output, or generated package output.
- Release publication, signing, installer/MSIX/Store work, live Ghidra
  mutation, and destructive private-payload cleanup are separate decisions.
- Static accounting is not runtime proof. Source naming is not retail behavior
  proof. A clean-room plan is not a runnable rebuild.
- Because the current maintainers and agents have read GPL-licensed source and
  detailed decompilation material, implementation is described as an
  RE-informed original-code prototype unless a separately staffed,
  sealed-spec implementation process and license review support a stronger
  clean-room claim.

## Review Envelope

This campaign uses Codex root and Codex-owned normal/adversarial lanes on
`gpt-5.6-sol`/`ultra`. The current broad audit covers repository DX, branch
archaeology, WinUI UX, patch/mod safety, binary RE quality, Lore quality,
rebuild provenance/architecture, and holistic normal/adversarial review.

The external Cursor/Grok lane is available through bounded, non-secret,
read-only `cursor-agent --model grok-4.5-fast-xhigh` consults. The completed
filesystem slice received normal and adversarial Cursor/Grok review, focused
follow-ups on challenged assumptions, and separate Codex normal/adversarial
review. Codex root retained edit, validation, state, commit, push, and final
acceptance ownership.

## Current Slice Acceptance

- A true no-game first run presents setup as the primary next action and does
  not make Save Lab appear usable before its prerequisites exist.
- Launch-preset selection reflects the complete effective argument state,
  including debug-trace changes.
- Cached navigation does not announce stale status or retain focus in an
  off-screen control.
- The safe-copy executable source action remains readable and operable at the
  supported compact width.
- Principal pages expose one semantic Level 1 heading and a predictable focus
  destination after navigation.
- Focused logic tests, zero-warning WinUI build, native visual/UIA checks,
  AppCore/WinUI suites, docs/state checks, and payload boundaries pass before
  the next push.

## Next Slices

1. Complete the prioritized WinUI first-user and accessibility fixes, then
   validate and expand patches/mods only behind evidence-backed safety gates.
2. Define the sealed evidence/provenance firewall, then build a deterministic
   headless simulation kernel and runnable primitive 3D vertical slice under
   the accurate provenance label.
3. Run deep evidence-based RE and Lore quality passes before expanding claims.

## Stop Conditions

- Main or a target file changes incompatibly during a slice.
- Unique historical work cannot be preserved before cleanup.
- A change would add hard payloads or expose private paths or secrets.
- Runtime, Ghidra, release, or destructive work lacks its separate authority,
  lease, evidence, or rollback plan.
- A security or correctness gate fails and cannot be bounded or fixed.
