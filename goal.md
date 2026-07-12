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

Audit and harden the patch/mod contract, then close one evidence-backed gap:

Existing guidance, architecture notes, and process ceremony are reviewable
project artifacts, not authority to preserve earlier agent choices. Rewrite or
remove constraints that are stale, redundant, unsupported, or misaligned with
the product; retain evidence-backed safety, provenance, legal, and user-authority
boundaries while improving how they are implemented.

1. account for all 29 rows in `patches/catalog/patches.v2.json`, including
   visible/hidden status, stability, exact original/patched bytes, dependencies,
   conflicts, clean-executable identity, evidence references, and proof class;
2. cross-check `safe-copy-profiles.v1.json`, AppCore planning/apply/verify logic,
   WinUI copy, and `patches/README.md` against that machine-readable truth;
3. add deterministic checks for orphaned or invalid dependency/conflict graphs,
   hidden companion misuse, profile expansion, and copied-target-only policy;
4. use the audit to select one bounded high-value unverified patch/mod or
   launch-attestation/accounting gap, then improve it test-first without
   broadening runtime claims; and
5. rewrite or remove any stale policy, label, or ceremony discovered along the
   path instead of preserving earlier agent choices by default.

The rebuild provenance/Core/First Flight slice is accepted at `0ed4e706`. The
source-only Godot 4.7 client is playable without retail payloads, and its exact
curated candidate passed standalone build/test, payload, docs, notices, and
hygiene gates. This is RE-informed original code, not retail parity or a strict
clean-room claim. No installed-game mutation, release, signing, Host/Join, or
online-ready claim was created.

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

## Current Slice Acceptance

- A reproducible audit accounts for all 29 patch rows and every profile key,
  dependency, conflict, hidden companion, exact byte span, and evidence class.
- Catalog/AppCore checks fail closed on invalid graphs, hidden direct selection,
  unverified clean-executable identity, byte mismatch, or non-copied targets.
- User-facing labels distinguish bytes-checked stability, runtime evidence, and
  unproven/experimental behavior without converting one class into another.
- One high-value gap selected from the audit receives a bounded implementation
  and regression test, or a well-formed blocker with the missing evidence and
  next executable action.
- Contributor docs/state describe the resulting patch/mod truth without
  gameplay, online, compatibility, or safety overclaims.
- Focused tests, broad quick checks, payload boundaries, normal/adversarial
  review, and a verified push pass before advancing.

## Next Slices

1. Audit and harden the 29-row patch/profile contract, then close one bounded
   evidence-backed patch/mod or launch-attestation gap.
2. Run deep evidence-based RE and Lore quality passes, generated front-door
   indexing, and stale-claim cleanup before expanding claims or publishing.
3. Extend the original-code rebuild in small deterministic vertical slices
   while preserving the separate sealed-spec clean-room option.

## Stop Conditions

- Main or a target file changes incompatibly during a slice.
- Unique historical work cannot be preserved before cleanup.
- A change would add hard payloads or expose private paths or secrets.
- Runtime, Ghidra, release, or destructive work lacks its separate authority,
  lease, evidence, or rollback plan.
- A security or correctness gate fails and cannot be bounded or fixed.
