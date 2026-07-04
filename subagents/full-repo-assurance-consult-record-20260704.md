# Full-Repo Assurance Consult Record - 2026-07-04

Status: current-policy consult coverage passed; closed as COMPLETE_PUSHED_WITH_NOTES

## Scope

This record covers the bounded full-repo assurance wave for public-boundary,
release-accounting, consult-policy, ZIP-overlay denylist, documentation,
state-hygiene, maintainer-local scratch/backup posture, and legacy local-storage
cleanup follow-through.

This wave did not claim runtime proof, release publication, Ghidra mutation or
read-back, generated rebuild output, gameplay behavior, online behavior,
installed-game mutation, original `BEA.exe` mutation, or raw SMART-attribute
verification.

## Sanitized Context

External consult context was limited to bounded, non-secret summaries and diff
surfaces. It excluded secrets, `.env` values, tokens, cookies, auth/session
files, sensitive logs, local databases, runtime config, smoke credentials,
payment/customer data, raw local proof artifacts, raw CDB logs,
screenshots/frame dumps, full Ghidra databases/backups, active skill/config
templates, planner/audit/goal-authority scripts, production/provider authority,
live deletion commands, and unredacted local storage manifests.

The working scratch convention for this wave is maintainer-local scratch on the
current Onslaught scratch volume, with historical local drive labels and exact
private paths redacted from tracked public surfaces.

## Consult Matrix

- Codex normal/specialist: ACCEPT after follow-up.
- Codex adversarial: ACCEPT after follow-up; prior standalone backup-volume
  leakage concern was cleared.
- Cursor Agent `composer-2.5-fast` normal: ACCEPT_WITH_NOTES; findings accepted.
- Cursor Agent `composer-2.5-fast` adversarial: BLOCK on stale/local-path and
  consult-evidence concerns before follow-up fixes; blocking findings accepted
  and remediated.
- Grok Build normal: ACCEPT_WITH_NOTES after compact git-initialized sanitized
  context retry; no remaining blocker.
- Grok Build adversarial: NO BLOCK after compact git-initialized sanitized
  context retry; recommendations treated as non-blocking precision notes.

No Gemini, Cursor Gemini, Opus, Cursor Opus, Grok Composer, or unknown external
model was used or required for this wave.

## Accepted Findings

- Replace stale Gemini/Opus consult requirements with the current mandatory
  stack: Codex normal/adversarial, Cursor Composer 2.5 Fast normal/adversarial,
  and Grok Build normal/adversarial.
- Remove exact maintainer-local paths and stale drive topology from public docs,
  state batons, release/readiness surfaces, RE/lore mirrors, and machine-readable
  ledgers.
- Treat Ghidra headless CLI as the current primary automation posture, with
  GhydraMCP documented as optional/inactive historical context only.
- Require explicit `GHIDRA_HOME` and `GHIDRA_PROJECT_DIR` for headless wrapper
  scripts instead of hidden local defaults.
- Extend repo text hygiene coverage for JSONL, Java, patch, and CSV surfaces and
  add generalized maintainer-local root, backup-volume, GhydraMCP/runtime-proof,
  private-checkout, and stale-consult-stack rules.
- Keep ZIP/lore packaging denylist coverage aligned with local overlay payload
  boundaries.
- Record local storage cleanup truth separately from repo claims and avoid raw
  SMART-attribute claims because only OS-visible disk health was available.

## Rejected Or Bounded Findings

- External agents did not receive authority to edit files, commit, push, delete
  storage, deploy, mutate production, handle secrets, or final-accept the wave.
  Codex root remains the acceptance owner.
- Grok emitted local git ownership warnings in the sanitized scratch context, but
  the compact retry still returned substantive normal and adversarial reports;
  this was treated as a non-blocking tooling warning, not a failed consult.
- Raw SMART verification is not claimed. Windows OS-visible health providers
  reported healthy/OK, while raw SMART tooling/provider access was unavailable.

## Unresolved Dissent

None known after final Codex follow-up and Grok retry.

## Terminal Closeout

- Commit, push, and post-push ref verification are performed by the coordinator
  closeout; the exact final commit and remote-ref parity are recorded in the
  coordinator final response because the pushed commit cannot embed its own final
  hash.
- No release publication or runtime mutation is authorized by this record.
