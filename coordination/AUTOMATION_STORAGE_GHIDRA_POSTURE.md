# Automation, Storage, Ghidra, And Proof Posture

Status: active coordination posture
Last updated: 2026-07-03

Use this document before assigning, accepting, or integrating coordinated work
that touches recurring automation, storage retention, Ghidra/headless work, or
runtime/static proof evidence. It supplements the path/resource/report contracts
in this directory and does not authorize product-source edits, hard-payload
commits, release actions, installed-game mutation, original `BEA.exe` mutation,
or live Ghidra mutation by itself.

## Active Storage Posture

- The current maintainer-local scratch/backup posture uses a configured
  removable scratch/backup root for new backup-producing Ghidra work and bulky
  temporary proof output when it is mounted, writable, and explicitly selected
  by the responsible lane. Expected top-level families are backup, scratch,
  proof, and cleanup-manifest roots under that configured root, with exact
  subpaths recorded only in ignored maintainer-local manifests.
- Exact drive letters, roots, volume identifiers, local cleanup manifests,
  free-space dumps, raw proof roots, and per-run artifact paths stay in ignored
  local policy/manifests or campaign reports, not tracked docs.
- Historical backup/archive drive strings in old wave evidence are provenance
  only. Do not treat a legacy drive root as the live backup target, a required
  runtime dependency, or a fallback to hard-code in tools.
- If the configured scratch/backup root is missing or unhealthy, stop and
  record the blocker or choose another explicit local/app-owned ignored root
  for that run. Do not silently fall back to legacy archive roots.
- The scratch root is not the only durable copy of source, release assets,
  active claim-bearing summaries, or current live-project backup decisions.

## Storage Sentinel

The restored storage/Ghidra sentinel is a recurring posture check, expected
every two hours during active campaigns. It is a safety and routing loop, not a
deletion authority.

The sentinel should:

- check that the configured scratch/backup posture is still mounted, writable,
  and not drifting back to legacy archive roots;
- perform at least one concrete read-only or conservative action, such as root
  availability inspection, lease review, backup-summary freshness check,
  storage-pressure classification, or tracked posture-drift scan;
- classify storage pressure at a summary level and report only sanitized
  conclusions in tracked state or docs;
- confirm that backup/proof material needing retention has a current summary,
  checker, ledger, recreation note, or retained replacement decision;
- flag stale raw bundles, duplicate scratch, or cleanup candidates for a human
  or integration-owner decision;
- keep exact local roots, raw manifests, private payload names, proof paths,
  and deletion command logs out of tracked docs.

Every storage sentinel pass must produce exactly one primary deliverable:

- `ADVANCEMENT`: a concrete storage-support result such as verified backup
  freshness/read-back evidence, mounted/writable configured-root posture
  confirmation, retained replacement or summary decision for a proof family,
  cleanup blocker classification, or non-destructive scratch setup that unblocks
  a named active RE/proof lane; or
- `BLOCKED_NO_CONCRETE_WORK_AVAILABLE_<yyyymmdd-hhmm>`: a quiet blocker record
  naming checked roots, relevant open slices or blockers, why no safe work was
  available, the next eligible concrete action, and `retry_after` no later than
  24 hours.

The sentinel must not:

- delete, prune, move, compress, or rewrite proof/Ghidra material without
  explicit user authority, a candidate-specific local manifest, and a retained
  replacement or public-safe summary decision;
- mutate live Ghidra projects, copied executables, installed game folders, or
  original `BEA.exe`;
- promote runtime/static/rebuild claims from storage observations alone.

## Proof Evidence Retention

Prefer tracked, public-safe evidence that future contributors can audit without
private payloads:

- compact proof summaries and readiness notes;
- validators, checkers, scripts, and schemas;
- JSON/JSONL/TSV ledgers that omit raw payloads and private roots;
- reproduction steps and arm-gate descriptions;
- hashes or backup IDs only when they do not reveal local private paths.

Raw runtime proof bundles, screenshots, frame dumps, CDB logs, copied-game
output, full Ghidra project stores, and raw private manifests are temporary
local evidence unless a separate reviewed policy says otherwise. They may be
regenerated for a bounded future proof lane; they should not become permanent
tracked evidence or assumed release inputs.

## High-Throughput Automation

Restored standing-wave and Ghidra/RE automation may advance bounded work several
times per day when authority, leases, and clean state are clear. High throughput
means smaller, sharper slices with faster integration, not weaker gates.

Each automation or worker cycle must close with exactly one primary deliverable:

- `ADVANCEMENT`: an accepted bounded artifact or state/policy/RE/proof/tooling
  delta under a named evidence class; or
- `BLOCKED_<root-cause-slug>_<yyyymmdd-hhmm>`: a blocker with `code`,
  `evidence`, `prior_attempt`, `owner`, `next_action`, `retry_after` no later
  than 24 hours, and `duplicate_check`.

Activity, logs, re-reading, status updates, broad planning, and validation gates
are secondary. They do not count as advancement unless they directly remove a
named blocker and name the next real advancement slice. A producing lane cannot
self-accept terminal success; acceptance must come from a distinct reviewer,
integration owner, acceptance owner, or human gate.

Each nontrivial automated slice should name:

- the bounded question it answers;
- the files and resources it owns;
- the proof class it may claim and the proof classes it does not claim;
- required consult/review lanes, including adversarial review when risk is not
  trivial;
- exact validation commands or a bounded reason they could not run;
- integration-owner state/doc updates if canonical batons are under lease.
- closeout markers:
  `ADVANCEMENT`, `PRIMARY_DELIVERABLE`, `ACCEPTED_BY`, `CONSULTS_USED`,
  `SAFETY`, and `GOAL_DELTA`.

Automation should stop rather than widen scope when branches, worktrees,
resource leases, local roots, validation results, or authority boundaries are
unclear.

## Nontrivial Operation Trigger

Treat an operation as nontrivial when it is more than a typo-only change or a
pure read with no durable effect. Nontrivial work includes:

- product, source, test, tooling, docs, state, or policy work beyond typo fixes;
- RE maps, Ghidra, headless, proof, storage, release, runtime, account, or
  spend work;
- disputed, high-collision, broad, cross-slice, or claim-promoting work;
- any work that could alter public posture, evidence accounting, authority,
  cleanup, release readiness, user-facing claims, or future automation.

Lane expectations:

- Chief heartbeat: coordinate one owner, slice, current gate, next deliverable,
  and handoff per material update. Status-only loops are not deliverables.
- Standing-wave launcher: start or advance one bounded public-safe slice with a
  named artifact, evidence class, acceptance criteria, and wall-time cap.
- Ghidra/RE sentinel: ship a measurable static/RE delta such as function/xref
  mapping, type/structure evidence, sidecar map, checker, or proof-plan update.
  Renames, rescans, and empty comments are not sufficient by themselves.
- Validation/drift sentinel: clear one blocker that is blocking another lane,
  with the blocked lane, artifact, and failing gate named.
- Storage/Ghidra sentinel: perform the two-hour storage-support result above,
  read-only unless separate cleanup/mutation authority exists.

## Ghidra And Headless Gates

Read-only Ghidra/headless work may inspect tracked exports, local Ghidra
read-back, xrefs, instructions, decompile rows, and static ledgers when the
assignment has a `live-ghidra-project` lease or is explicitly offline against
tracked exports. Read-only static review can advance documentation only to the
evidence class it actually checked.

Mutation is a separate gate. A Ghidra mutation lane requires:

- explicit mutation authority and an exclusive `live-ghidra-project` lease;
- a current backup plan to the active ignored scratch/backup root or another
  explicit local/app-owned ignored root;
- dry-run or probe evidence before apply when a script can mutate the project;
- serialized write/read-back per address or data item;
- ledger and attempt-log updates for every attempted mutation;
- explicit save/checkpoint discipline and read-back after restart when needed;
- public docs updated only after read-back confirms the intended state.

Headless apply mode must fail closed on bad rows, missing targets, lock
contention, dry-run mismatches, absent backups, or unclear ownership. It must
not touch installed game files or original executable bytes.

## Structured Authority Baton

Runtime proof, live Ghidra mutation, destructive cleanup, release,
external-account action, and spend require a structured authority baton before
execution. The baton may live in `goal.md`, a local campaign record, or another
explicit coordinator/integration-owner assignment, but it must be available
before the action starts.

The baton must name:

- action family;
- allowed commands and forbidden commands;
- required path and resource leases;
- proof/storage root policy;
- validation gates;
- cleanup or rollback steps;
- expiration or review deadline;
- spend cap and payment-method handle when money is in scope.

Without that baton, the only allowed work is read-only planning, blocker
reporting, or consult preparation.

## Consult Posture

Nontrivial automation, storage deletion/retention, Ghidra mutation, public
claim promotion, release posture, and broad collaboration-policy work require
bounded consult evidence or an explicit `CONSULT_UNAVAILABLE` record for each
missing lane. Required lanes are Codex normal, Codex adversarial, Cursor
Agent `composer-2.5-fast` normal, Cursor Agent `composer-2.5-fast`
adversarial, Grok Build normal, and Grok Build adversarial. Consults are
advisory; Codex root or the integration owner remains responsible for final
scope, safety, state reconciliation, and acceptance. Unresolved adversarial
blockers prevent terminal success unless the coordinator or integration owner
records a specific override rationale.

Each `CONSULT_UNAVAILABLE` record must include the exact tool, command, model,
authentication, usage-limit, or safety-boundary reason and the Codex-root
verification or coordinator/integration-owner override used to continue.

Prepared consult lanes for this posture class:

| Lane | Normal brief focus | Adversarial brief focus |
| --- | --- | --- |
| Codex | Check whether the patch makes the storage/Ghidra/proof posture durable, concise, and consistent with repo contracts. | Attack for hidden authority expansion, state/write conflicts, hard-payload leakage, stale legacy-drive reliance, weak proof-class separation, and missing validation. |
| Cursor Agent `composer-2.5-fast` | Review docs for practical contributor clarity and collision risk in coordinated campaigns. | Attack for ambiguous ownership, unsafe automation shortcuts, overbroad cleanup language, or claims that exceed evidence. |
| Grok Build | Review the policy as an outside lane for operational blind spots and missing stop conditions. | Attack for unsafe deletion, mutation, proof-retention, external-tool, or campaign-control assumptions. |

Consult briefs must not include secrets, `.env` values, auth/session/cache/log
material, raw local manifests, exact local proof roots, hard payloads, copied
executables, screenshots/frame dumps, raw CDB logs, full Ghidra project paths,
customer/private data, active thread IDs, or raw campaign reports.

External consult packets should be whitelist-based: public goals, redacted
status, allowed public files, forbidden context, non-secret task summary, claim
boundary, requested output, and stop rule. Record lane outcome summaries and
tool failures; do not paste raw external prompts or raw logs into tracked docs.

## Advancement Versus Hygiene

Real project advancement requires an accepted, bounded artifact or change that
moves a specific capability, proof plan, static contract, checker, user
workflow, or durable policy forward under a named evidence class and updates
the relevant docs or state after validation.

Hygiene-only checks are still useful, but they are not enough to claim
advancement by themselves. Examples include:

- running repo hygiene, docs, link, or JSON parse gates without a resulting
  accepted source/docs/proof change;
- storage inventory without a retained summary, deletion decision, or restored
  headroom result;
- automation heartbeats that only observe status;
- mirror refresh or baton wording that does not change the next executable
  slice, claim boundary, or validation posture.

Hygiene/status/re-read/gate-only work may be reported as `ADVANCEMENT` only
when it removes a named blocker and names the next advancement slice.

If a slice is hygiene-only, report it as hygiene-only. Do not promote static
closure, clean validation, storage headroom, or automation cadence into runtime,
visual, gameplay, release, rebuild, or no-noticeable-difference proof.
