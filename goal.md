# Active Goal

Status: ACTIVE
Last updated: 2026-07-12
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

Crosswalk the released Steam binary, Stuart's in-house PC source, the existing
AYA exporter, and the rebuild into one evidence hierarchy, then implement one
recognizable evidence-backed rebuild behavior slice.

The work can proceed in parallel, but evidence promotion is sequential:
source suggests ownership and architecture; the Steam binary and bounded
runtime observations decide released behavior; exporter tests decide format
coverage; the rebuild consumes only an accepted behavior specification and
feeds ambiguities back to RE instead of promoting its own assumptions.

1. inventory `references/Onslaught` and `references/AYAResourceExtractor` at
   their pinned commits, including remote/fork provenance, license, build/test
   posture, supported formats, and known gaps;
2. choose one recognizable gameplay subsystem and crosswalk source owners,
   Steam binary functions/data, tracked decompilation, runtime evidence, asset
   dependencies, and rebuild-facing behavior fields;
3. re-review that binary call-chain cluster under a measured quality rubric
   separating name/owner, prototype/type, semantics, provenance, and runtime
   confidence; live Ghidra mutation still requires a separate baton;
4. exercise and improve the exporter against public/synthetic fixtures and
   explicitly authorized ignored local inputs, recording supported and missing
   mesh, material, texture, animation, archive, and conversion behavior; and
5. freeze one public-safe behavior contract with evidence references, measured
   constants, tolerances, and non-claims, then implement it in deterministic
   Core plus the Godot adapter with headless and native acceptance evidence.

Do not expand the generic First Flight arena as a substitute for fidelity. The
target is one small authentic behavior slice whose provenance and differences
from retail are inspectable.

## Verified Starting Point

- Public release `v1.0.9` remains the latest published unsigned portable WinUI
  ZIP. It includes the friendly root layout, SHA-256 sidecar, and 949-document
  offline Lore pack.
- The 29-row patch/profile contract is machine-accounted at 20 visible options
  (9 stable, 11 experimental), 9 hidden companions, 17 dependency edges, and
  118 conflict edges. AppCore binds mutations to exact pinned catalog rows,
  publishes backup/checksum/apply/restore files atomically, and restores
  damaged or truncated copies only from an integrity- and provenance-verified
  full-file backup. The Python patch helper remains a lab surface.
- The Sol Ultra baseline was committed and pushed at
  `5a7bacecac5e813804355d68a8e51973100e0331`; local `main`, `origin/main`, and
  live remote `refs/heads/main` matched with divergence `0 0`.
- The contributor authority and quick-check advancement was committed and
  pushed at `798c339505fb85cc782abbd4b07df81e143c2284`; `npm test` is now the
  normal active-product baseline.
- The deterministic rebuild Core was accepted and pushed at
  `3cc382e8fa206c3a3f885f9dec4dedd2297b9f97`. The playable First Flight client
  was accepted in source at `0ed4e706753c350ae1ec835d6dd466feddd587c7`;
  its 721-selected/726-materialized plain candidate passed the standalone test
  suite, payload/inventory, 463-file/138-link Markdown, 74-package notices, and
  718-file hygiene/line-ending gates.
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
- The WinUI first-use/accessibility closeout passed a zero-warning solution
  build, `npm test` (1,307 AppCore tests; 136 WinUI tests plus 2 expected
  private-catalog skips), twelve explicit Home state/route cases, shell accessibility,
  restored-Video lazy-VLC, compact Patch Bench interaction, real read-only
  audio/video playback, and the 11-screen visual smoke. Full Markdown links,
  notices, public allowlist/hard-payload, and repository hygiene gates passed.

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
review. The WinUI slice received Codex normal/adversarial review whose two
concrete edge-case blockers were fixed with native regressions; independent
Cursor/Grok normal and adversarial closeout reviews then returned `ACCEPT` with
no commit blockers. First Flight received Codex and bounded Cursor/Grok normal
and adversarial review; the final Codex adversarial follow-up accepted the
suspended-root Job Object ownership model and explicitly heuristic visual-
evidence boundary. Codex root retained edit, validation, state, commit, push,
and final acceptance ownership.

The patch-contract slice received Codex and bounded Cursor/Grok normal and
adversarial review. Review challenges produced pinned-catalog membership,
known-transition attestation, transitive window-pair planning, sidecar-link
guards, case-consistent graph semantics, diagnostic-evidence separation, and
atomic damaged-copy recovery regressions. The accepted residual is no sandbox
claim against an already malicious process running as the same Windows user.

## Current Slice Acceptance

- Both reference submodules have a reproducible provenance, license, build,
  test, and capability inventory at their pinned commits.
- One subsystem crosswalk distinguishes source suggestion, Steam static proof,
  runtime proof, exporter support, rebuild implementation, and unresolved
  disagreement at function/data-field granularity.
- The reviewed binary cluster has measured quality scores and no unsupported
  whole-binary or fully-reversed claim.
- Exporter coverage has executable fixtures/checks and either closes one real
  format gap or records a bounded blocker with the missing input/evidence.
- One recognizable rebuild behavior is implemented from an accepted public-safe
  contract with deterministic headless tests and native visual/input evidence.
- No proprietary payload, full Ghidra store, original-game mutation, generic
  parity claim, or implementation-room assumption enters Git.
- Focused and broad-enough gates, normal/adversarial review, state/docs, and a
  verified push pass before advancing.

## Next Slices

1. Crosswalk the Steam binary, Stuart source, exporter, and rebuild; ship one
   authentic evidence-backed behavior slice.
2. Run the deep Lore editorial/provenance pass and generated contributor
   front-door indexing in parallel where it does not compete for RE evidence.
3. Continue subsystem-by-subsystem binary re-review and rebuild fidelity work
   while preserving the separate sealed-spec clean-room option.

## Stop Conditions

- Main or a target file changes incompatibly during a slice.
- Unique historical work cannot be preserved before cleanup.
- A change would add hard payloads or expose private paths or secrets.
- Runtime, Ghidra, release, or destructive work lacks its separate authority,
  lease, evidence, or rollback plan.
- A security or correctness gate fails and cannot be bounded or fixed.
