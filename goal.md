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

Close the release-blocking filesystem authority gaps found by the normal and
adversarial safety audit:

1. commit save and options output through a shared guarded atomic transaction;
2. reject in-place, hardlink, symlink, junction, device, network, alternate-data-
   stream, wrong-extension, and installed-game-tree output targets;
3. keep generated safe-copy control editing available only inside its separately
   verified app-owned profile root;
4. bind asset catalogs and sidecar discovery to one declared export root; and
5. revalidate catalog sources, package destinations, manifests, and sidecars at
   materialization time before copying.

The save/options advancement is accepted after iterative normal and adversarial
review closed trusted-root, directory-creation, physical-alias, staging, and
final-entry race findings. The trusted asset-root and materialization
advancement remains active and is still a release blocker. This slice creates
no release, gameplay, visual, online, Ghidra read-back, or rebuild proof.

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

- Save and options outputs default to an app-owned output folder and retain
  strict `.bes` / `.bea` type boundaries without creating directories during
  path calculation.
- Every save/options writer protects all source identities, stages a unique
- Installed-game-shaped output trees and lexical, reparse, hardlink, reserved-
  device, `SUBST`, mapped-drive, and network aliases fail closed after physical
  final-path resolution; held ancestor handles prevent directory replacement.
- Verified generated safe-copy edits require a minted capability for the
  canonical app-owned `GameProfiles` root rather than a trusted path string.
- Asset catalog lookup no longer searches arbitrary ancestors or the current
  working directory, and resolved sources remain inside one trusted export root.
- Package materialization revalidates source and destination identity before
  every copy and cannot escape through reparse or hardlink aliases.
- Focused hostile-path tests, full AppCore/WinUI tests, patch/safe-copy gates,
  docs/state checks, and public payload boundaries pass before each push.

## Next Slices

1. Finish the trusted asset-root and package-materialization half of the active
   filesystem safety slice.
2. Apply the prioritized WinUI first-user and accessibility fixes, then
   validate and expand patches/mods only behind evidence-backed safety gates.
3. Define the sealed evidence/provenance firewall, then build a deterministic
   headless simulation kernel and runnable primitive 3D vertical slice under
   the accurate provenance label.
4. Run deep evidence-based RE and Lore quality passes before expanding claims.

## Stop Conditions

- Main or a target file changes incompatibly during a slice.
- Unique historical work cannot be preserved before cleanup.
- A change would add hard payloads or expose private paths or secrets.
- Runtime, Ghidra, release, or destructive work lacks its separate authority,
  lease, evidence, or rollback plan.
- A security or correctness gate fails and cannot be bounded or fixed.
