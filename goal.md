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

Establish a trustworthy Sol Ultra baseline before broad source movement:

1. account for and preserve abandoned worktrees and campaign branches;
2. align active coordination policy with the current review model;
3. replace historical current-state batons with concise current truth;
4. map canonical, derived, generated, historical, archived, and local-only
   surfaces;
5. define a fast contributor path that remains distinct from exhaustive
   release/public-boundary signoff.

This slice is repository and coordination hardening. It does not claim fresh
runtime, gameplay, visual, patch-behavior, Ghidra read-back, or rebuild proof.

## Verified Starting Point

- Public release `v1.0.9` remains the latest published unsigned portable WinUI
  ZIP. It includes the friendly root layout, SHA-256 sidecar, and 949-document
  offline Lore pack.
- Before this slice, local `main`, `origin/main`, and live remote
  `refs/heads/main` matched at `9f577b81ccaf0dc20a2f4da18ee1da938def1827`
  with divergence `0 0`.
- Git reports one registered worktree. Seven Codex Desktop worktree entries
  were empty zero-byte shells with no Git metadata or linked conversations and
  were removed on 2026-07-11.
- Sixty-one historical `campaign/*` and `codex/*` branch tips were preserved
  in a verified local Git bundle before branch cleanup. Twenty-four otherwise
  unreachable commits and all three stashes were also preserved. Both bundles
  passed `git bundle verify` and a disposable restore drill. Four
  `backup/*` refs remain separate and outside every deletion list.
- The repository currently has 19,389 tracked files, including 13,385 under
  `reverse-engineering/`, 2,614 under `tools/`, and 1,710 under
  `release/`.
- Root `package.json` currently exposes 1,494 scripts, including 1,472 test
  scripts and 840 Ghidra wave scripts. This is retained as evidence of the
  contributor-workflow problem, not accepted as the desired interface.
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
clean-room rebuild architecture, and holistic normal/adversarial review.

The required external Cursor/Grok lane is currently degraded:

- `CONSULT_UNAVAILABLE:cursor-grok-normal-adversarial`
- Windows `cursor-agent` rejects the required sandbox because that sandbox is
  unavailable on Windows.
- WSL has the client but cannot fetch the model catalog without separate
  authentication.
- No unsafe non-sandbox or credential-copy fallback is allowed.

Focused Codex-owned review covers the current non-release, non-runtime,
non-destructive slice. The degraded lane must be reported at acceptance.

## Current Slice Acceptance

- Empty Codex worktree shells are removed without losing source.
- Campaign branch tips are preserved before ordinary branch-name cleanup.
- Ordinary campaign branch names remain in place until this baseline commit is
  accepted; no backup ref, stash, archive ref, object pruning, or Git GC is part
  of this slice.
- Active model and consult policy names `gpt-5.6-sol`/`ultra` and
  `grok-4.5-fast-xhigh`, with one envelope per substantive objective rather
  than recursive per-operation ceremony.
- `goal.md`, developer state, documentation state, and RE state are concise
  current batons.
- Generated WinUI automation snapshots are ignored as intended.
- Relevant JSON, docs, mirror, hygiene, payload, and repository gates pass.
- The verified slice is committed, pushed, and remote parity is confirmed.

## Next Slices

1. Publish the authority map and an archive-free first-hour contributor path.
2. Introduce a small, discoverable quick-check interface while retaining
   exhaustive signoff gates.
3. Simplify the PR template and clarify sanitized toolkit UI evidence versus
   prohibited proprietary game captures.
4. Add a shared guarded/atomic filesystem transaction, close save/options alias
   writes, and bind asset catalogs to a declared trusted export root.
5. Apply the prioritized WinUI first-user and accessibility fixes, then
   validate and expand patches/mods only behind evidence-backed safety gates.
6. Define the sealed evidence/provenance firewall, then build a deterministic
   headless simulation kernel and runnable primitive 3D vertical slice under
   the accurate provenance label.
7. Run deep evidence-based RE and Lore quality passes before expanding claims.

## Stop Conditions

- Main or a target file changes incompatibly during a slice.
- Unique historical work cannot be preserved before cleanup.
- A change would add hard payloads or expose private paths or secrets.
- Runtime, Ghidra, release, or destructive work lacks its separate authority,
  lease, evidence, or rollback plan.
- A security or correctness gate fails and cannot be bounded or fixed.
