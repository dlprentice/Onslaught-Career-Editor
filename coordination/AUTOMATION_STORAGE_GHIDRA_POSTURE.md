# Automation, Storage, Ghidra, And Proof Posture

Status: optional coordination posture
Last updated: 2026-07-15

Use this document for recurring automation, storage retention, live Ghidra, or
bulky proof work. It preserves safety and evidence rules; it does not replace
the standing campaign authority or fresh-authorization boundaries in
`goal.policy.md`.

## Current Automation Posture

The historical high-throughput standing-wave launcher and Ghidra, storage,
validation, and heartbeat sentinels remain stopped. The durable `/goal` is not
one of those background automations: its normal operating model is one root-led
slice at a time in the active task.

Root may deliberately restart a bounded automation when it has a specific
objective, owner, write/resource scope, validation, stop rule, and cleanup
path. Merely resuming the reconstruction goal does not restart old schedulers,
sentinels, or persistent worker lanes.

## Storage Posture

- New bulky proof output and backup-producing Ghidra work uses an explicitly
  selected ignored/app-owned local root or configured scratch/backup root.
- Exact volumes, local paths, manifests, payload names, and deletion logs stay
  ignored/local.
- Historical drive strings are provenance only and are never implicit active
  configuration.
- A missing or unhealthy scratch root causes root to choose another exact safe
  ignored root or skip that slice. Never fall back silently.
- Scratch is not the only durable copy of source, active claim-bearing
  summaries, release assets, or current backup decisions.

Normal cleanup may remove only invocation-owned disposable output. Deleting,
moving, pruning, compressing, or overwriting ambiguous or irreplaceable proof,
Ghidra projects/backups, user payloads, or broad storage families is genuinely
destructive and needs fresh maintainer authority.

## Optional Storage Sentinel

If root explicitly restarts a storage sentinel, it remains read-only unless a
separate bounded cleanup action is both covered by normal cleanup and tied to
invocation-owned output. A pass should verify a concrete posture item or report
the exact absence of safe useful work; status churn is not advancement.

Useful read-only checks include configured-root availability, backup-summary
freshness, storage-pressure classification, retained-evidence coverage, and
tracked policy drift. Do not expose exact private roots or raw manifests in
tracked state.

## Proof Evidence Retention

Prefer tracked public-safe artifacts that future contributors can audit:

- compact proof summaries and accepted behavior contracts;
- validators, checkers, scripts, and schemas;
- sanitized JSON/JSONL/TSV ledgers;
- reproduction and arm-gate descriptions; and
- non-sensitive hashes or proof labels.

Raw runtime bundles, screenshots, frame dumps, debugger logs, copied-game
output, full Ghidra stores, and raw private manifests remain ignored/local.
They do not become release inputs or durable public evidence merely because an
automation produced them.

## Optional High-Throughput Automation

An explicitly restarted automation advances small bounded slices; it does not
weaken authority, identity, payload, evidence, validation, or cleanup rules.
Each cycle names:

- the question and primary artifact;
- write/resource ownership;
- evidence class and non-claims;
- proportional independent review when consequence or uncertainty warrants;
- validation and stop conditions; and
- the root-owned integration/state action.

The cycle returns a verified advancement, an exact blocker, or no accepted
change. Logs, rereads, status updates, and passing unrelated gates are not
advancement. The current root remains the final acceptance and integration
owner. Other roles may advise or prepare reconciliation but gain root authority
only through explicit baton succession and the handoff checks in
`goal.policy.md`.

Automation stops on repository/base drift, contested ownership, unknown
processes, target ambiguity, validation failure, missing safe storage, or an
operation that requires spending or genuinely destructive authority.

## Ghidra And Headless Gates

Read-only tracked-export analysis needs no local project claim. Live Ghidra
inspection or mutation is serialized through the active root operation or an
exclusive `live-ghidra-project` resource claim when concurrent work is active.
Standing campaign authority covers live inspection, mutation, save, and read-
back; the following execution gates still apply.

Before a mutation batch:

- identify the exact project/program and ensure no unknown user owns it;
- select an ignored backup root;
- back up the complete `.gpr` marker plus recursive `.rep` store with
  `tools/ghidra_project_backup.py`;
- verify per-relative-file hashes and a disposable read-only program open with
  `tools/GhidraProjectOpenProbe.java`;
- dry-run the intended script/rows and reject bad, missing, locked, ambiguous,
  or mismatched targets; and
- identify the exact rollback endpoint.

During mutation:

- serialize write and read-back per address/data item;
- record every attempted mutation in the applicable local/public-safe ledger;
- stop at the first apply or read-back mismatch;
- preserve the failed state and attempt receipt; and
- never touch the installed game or original executable bytes.

After a successful batch:

- save/checkpoint deliberately;
- restart/read back when the claim requires persistence proof;
- create and verify a new complete backup with the same hash and disposable-
  open checks; and
- update public docs only to the read-back evidence actually obtained.

Restoration is serialized recovery. Close project users, preserve the failed
pair, restore the complete verified pair, repeat hashes/read-only open, and
confirm restart read-back before resuming. If restoration would overwrite an
ambiguous or irreplaceable state rather than an invocation-owned failed copy,
it is genuinely destructive and needs fresh authority.

Rendered signature strings are not blanket prototype authority. Structured
prototype changes require exact calling-convention/type/storage/purge
expectations and exact prototype-key read-back. Headless apply fails closed on
bad rows, missing targets, lock contention, backup failure, drift, or unclear
ownership.

## Standing And Fresh Authority

The standing campaign authority in `goal.policy.md` covers copied-runtime
observation/mutation, live Ghidra work, normal cleanup, version control,
release/publication, and project-scoped external actions. It removes repeated
human baton requests but not exact target identity, resource serialization,
backups, gates, attempt caps, rollback, or cleanup.

Spending and genuinely destructive operations beyond normal cleanup require
fresh maintainer authority. The installed Steam game and original `BEA.exe`
remain immutable, and proprietary evidence remains local.

## Review Posture

Root selects independent review according to consequence, uncertainty, breadth,
and claim risk. Normal/adversarial review and sanitized external consults are
useful for broad policy, live mutation, destructive recovery, release claims,
or disputed evidence, but fixed role counts and empty consult placeholders are
not acceptance criteria.

Review is advisory. Root resolves material findings and owns final scope,
safety, state, publication, and acceptance. External briefs contain no secrets,
credentials, local private paths, hard payloads, raw evidence, active IDs, or
action-bearing material.

## Advancement Versus Hygiene

Real advancement changes a bounded capability, behavior contract, checker,
workflow, static/runtime evidence map, rebuild truth, or durable operating
policy and verifies that result. Hygiene-only checks are useful when they clear
a named blocker or protect active evidence, but they are not automatically an
advancement.

Do not promote clean storage, passing validation, static closure, automation
cadence, or review volume into runtime, visual, gameplay, release, rebuild, or
parity proof.
