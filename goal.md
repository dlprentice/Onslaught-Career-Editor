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

Establish the rebuild provenance firewall and deliver the first runnable
RE-informed original-code vertical slice:

Existing guidance, architecture notes, and process ceremony are reviewable
project artifacts, not authority to preserve earlier agent choices. Rewrite or
remove constraints that are stale, redundant, unsupported, or misaligned with
the product; retain evidence-backed safety, provenance, legal, and user-authority
boundaries while improving how they are implemented.

1. inventory the current rebuild/source-reference prototypes and choose one
   bounded path rather than creating another parallel lane;
2. document the evidence/provenance firewall that distinguishes the current
   RE-informed implementation from a separately staffed sealed-spec clean-room
   path;
3. define a deterministic headless simulation contract with replayable inputs,
   state transitions, and hashes;
4. expose a small runnable visual experience that uses original project code and
   non-proprietary placeholder/generated assets; and
5. add contributor commands, tests, run instructions, and bounded non-claims so
   the result is something a maintainer can actually launch and inspect.

The preceding WinUI first-use/accessibility slice is accepted locally. True
first run now prioritizes game-folder setup without blocking manual Save Lab
files and preserves a remembered folder when its drive is temporarily unavailable;
shell status/focus ownership, Level 1 headings, compact source actions,
launch/admin preset truth, and lazy Media VLC initialization have native UIA
and visual evidence. No installed-game mutation, release, signing, gameplay
parity, online readiness, or clean-room implementation claim was created.

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
no commit blockers. Codex root retained edit, validation, state, commit, push,
and final acceptance ownership.

## Current Slice Acceptance

- The repo has one explicit provenance/firewall contract for RE-informed work
  and a separately staffable sealed-spec clean-room path.
- A documented command launches a runnable original-code vertical slice without
  requiring proprietary game payloads.
- A deterministic headless test replays the same input sequence to the same
  rolling trace and final-state hashes and fails on contract drift.
- The visual slice has bounded input, update, camera/render, reset, and exit
  behavior plus native screenshot/runtime evidence.
- Contributor docs/state name what is implemented, what evidence informed it,
  and what remains unproven; they do not claim gameplay/rebuild parity.
- Focused tests, broad quick checks, payload boundaries, normal/adversarial
  review, and a verified push pass before advancing.

## Next Slices

1. Complete the rebuild evidence firewall, deterministic kernel, and runnable
   RE-informed vertical slice.
2. Validate and expand patches/mods only behind evidence-backed copy/runtime
   safety gates, including the remaining launch-attestation/accounting gaps.
3. Run deep evidence-based RE and Lore quality passes, generated front-door
   indexing, and stale-claim cleanup before expanding claims or publishing.

## Stop Conditions

- Main or a target file changes incompatibly during a slice.
- Unique historical work cannot be preserved before cleanup.
- A change would add hard payloads or expose private paths or secrets.
- Runtime, Ghidra, release, or destructive work lacks its separate authority,
  lease, evidence, or rollback plan.
- A security or correctness gate fails and cannot be bounded or fixed.
