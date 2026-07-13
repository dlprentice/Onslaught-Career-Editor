# Ghidra Full Re-Audit Recovery And Revalidation

Status: read-only recovery, semantic revalidation, retention audit, and process
hardening complete; live correction application requires a separate exclusive
mutation lease
Date: 2026-07-13
Evidence class: static Ghidra metadata, structure, decompilation, references,
instructions, source-alignment evidence, and read-only backup verification

## Closeout Truth

The deleted Cursor campaign was not simply accepted from its summary. Its two
trusted endpoints were freshly exported, compared by address, and then reviewed
semantically in the required targeted order. The endpoint comparison proves a
stable `6,411`-address inventory and exactly `459` exported metadata changes:

- `343` comment-only;
- `114` rename plus comment; and
- `2` rename-only.

All `116` rendered-signature differences normalize to the function-name change.
There are zero structured prototype-key changes, zero complete function-body
range or body-address-count changes, and zero inline, thunk, or thunk-target
attribute changes between the trusted endpoints. This does not mean every
property in the Ghidra store was compared: tags, local variables, and unrelated
symbol or datatype state are outside the `459`-address exported delta.

Fresh read-only evidence was then used to decide whether the changed names and
comments were actually justified. The review did find mistakes. It found no net
endpoint prototype or function-body change and no surviving evidence that
Cursor introduced one; incomplete historical rows cannot exclude a transient
change that was later reverted.

| Review set | Reviewed | Accepted | Correction required | Unresolved |
| --- | ---: | ---: | ---: | ---: |
| Cursor metadata delta | 459 | 388 | 71 | 0 |
| Strongest recovered-conflict set | 112 | 98 | 14 | 0 |
| Identified research set | 9 | 7 | 2 | 0 |
| Rebuild/runtime-critical set | 20 | 10 | 10 | 0 |

The conflict row classifies recovered narratives. Four of its `14`
correction-required findings have their proposed fields fully covered by the
Cursor-delta pack, one has a
more exact targeted correction that explicitly supersedes the Cursor record,
and the other nine are targeted-only current-comment corrections. The two packs
cover `92` unique correction addresses and are deliberately separate:

- `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json`
  contain `71` records: `18` name corrections and `68` comment corrections,
  with overlap between those fields. These are corrections to Cursor changes.
- `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`
  contains `22` records: `10` recovered-conflict comment corrections, `2`
  research corrections, and `10` critical-function corrections. Across that
  pack are `8` name corrections, `22` comment corrections, and `9` rendered
  signature strings. Eight signature strings change only owner/name and
  parameter-name rendering; only `0x0050b9c0` proposes a structured prototype
  correction. These findings are inherited, conflict-set, research-set, or
  critical-function debt and must not be blamed on the Cursor delta. At
  duplicate address `0x00481060`, the targeted record is authoritative; a
  future mutation preflight must reject ambiguous duplicate ordering and apply
  that superseding record.

Neither manifest authorizes mutation. The live Ghidra project remained
read-only throughout this lane. Applying the accepted corrections requires a
bounded exclusive mutation lease, followed by a new complete recursive backup
and read-only verification receipt.

The eight rendering-only signature rows must not be implemented by blindly
parsing whole signature strings; apply the owner/name and parameter-label scope
that their classification permits. `0x0050b9c0` is different: its prototype
change needs an explicit prototype-mutation lease, a dry-run expected calling
convention/type/storage/purge key, and exact post-write prototype read-back.
Until that exists, the pack's global prototype/boundary authorization remains
false.

## Recovered Review Boundary

The deleted campaign ledger was not fully recovered. The preserved direct-child
recovery establishes the original paper-trail boundary requested for this
closeout:

- `4,326` addresses had one unambiguous exact recovered review row;
- `54` addresses had conflicting recovered variants; and
- `2,031` addresses had no reconstructable row-level narrative.

Recursive transcript recovery improved the evidence without changing that
historical fact. The strongest balanced, data-only pass uses JSON decoding and
`ast.literal_eval`; recovered text is never executed. It establishes:

- `6,215` addresses with one unambiguous exact recovered review row;
- `112` addresses with conflicting recovered variants; and
- `84` addresses with no reconstructable exact row.

Those three strongest sets are disjoint and cover all `6,411` addresses. The
strongest `112`-address conflict set contains all `54` conflicts from the
original direct-child pass. The
surviving aggregate identified nine research findings. Eight have exact
recovered rows. `0x005be628 HResultToString` is identified only by its surviving
shard summary, so its deleted exact verdict remains unrecovered. A later bounded
read-only decompile and call-site review resolved the current semantic question;
it did not recreate the deleted row. Missing or conflicting historical verdicts
were never invented, and this closeout does not claim full ledger recovery.

## Semantic Findings

The `459`-address review used fresh metadata, tags, incoming references,
`38,471` function-body instruction rows, `459` successful decompiles, and
baseline counterparts for every rename. The correction pack records each
address, current and corrected metadata, bounded rationale, and affected docs.
Representative errors include decompiler-expanded jump thunks, wrong owner or
subsystem names, wrong return or ABI wording, stale comments, incorrect
Direct3D constants, JPEG compressor semantics, and raw register/stack-flow
mistakes.

The follow-on targeted pass resolved all nine research addresses and all twenty
selected rebuild/runtime-critical functions. Important current corrections
include:

- `0x00406560` is `CBattleEngine__HandleLocks`, not a projectile helper;
- `0x004081c0` is `CBattleEngine__Move`;
- the JetPart movement cluster at `0x00410c50`, `0x00411630`, `0x00411aa0`,
  `0x00411b70`, and `0x00412900` belongs to JetPart movement behavior;
- `0x00412ad0` is `CBattleEngineWalkerPart__UpdateWalkCycle`;
- `0x0057457a` receives its wrapper input in `EAX`, which the callee copies to
  `ESI`; `ESI` is not a second implicit input;
- `0x005be628 HResultToString` has `21` real direct calls, not `22`; and
- `0x0050b9c0 CWorld__LoadWorld` has three explicit stack arguments after
  `this`, in the order `mem_buffer`, `is_base_world`, and
  `initialize_world_state`, matching its raw prologue and `RET 0x0c`.

These targeted corrections expose inherited metadata debt even though the two
trusted endpoint prototypes and boundaries compare equal. They do not turn the
static evidence into runtime behavior proof.

## Backup And Retention Verification

The trusted endpoint directory labels are
`BEA_20260703-152228Z_live_project_backup_verified` and
`BEA_20260713-031607Z_post_cursor_full_reaudit_absorbed`. Both endpoints and
all ten full-sized Wave 10 through Wave 19 intermediate backups remain
preserved. Each of the twelve meaningful backups passed a copied-store gate:

1. recursively copy the `.gpr` file and complete `.rep` store;
2. verify stable per-relative-file size and SHA-256 equality;
3. open `/BEA.exe` read-only with analysis disabled in the disposable copy; and
4. verify zero post-open content drift.

The two endpoint probes additionally bound the opened program to the canonical
retail imported-program MD5 `3b456964020070efe696d2cc09464a55`.
The current live project pair is `19` files and `177,015,687` bytes and matches
the trusted post-campaign endpoint at every relative path, size, and SHA-256.
The surviving Cursor transcript project remains preserved pending explicit
transcript-extraction acceptance.

The campaign also left `22` non-recoverable project shells. Before deletion,
their exact absolute paths, file inventories, byte counts, hashes, absence of
meaningful `.rep` data, `BEA.exe` non-exposure classification, and intended
backup root were recorded in ignored local manifest
`retention-deletion-manifest-20260713.json` (schema v2, SHA-256
`cd2d37f3500476b603000a89fc8c210c542cf0869a426e930741e0b424e89be8`).
The original v1 bytes remain preserved beside a semantics-correction receipt;
v2 fixes ambiguous legacy-inventory and program-exposure labels without
changing the shell inventory or deletion record.
Together they
contained `33` files and `1,804` bytes. Ten shells gained owner-only
`project.prp` scaffolding totaling `1,640` bytes during the proof that Ghidra
could not expose `/BEA.exe`; their original shell payload was only `164` bytes.
Only those proven shells and one exact empty Cursor worktree husk were removed.
No meaningful space was reclaimed. The live project, trusted endpoints,
full-sized intermediates, recovery overlay, and transcripts were excluded from
cleanup.

## Durable Backup Process

`tools/ghidra_project_backup.py` is the
supported focused backup/verification path. It refuses incomplete stores,
reparse points, existing destinations, unstable source reads, and receipt
overwrites. It stages a same-parent partial copy, verifies the `.gpr` plus the
recursive `.rep` content, performs the disposable read-only program-open probe,
rehashes source and copy, writes a detailed local-only receipt to an
operator-selected path disjoint from the source and scratch roots, and removes
only its own verified scratch path. `tools/GhidraProjectOpenProbe.java`
provides the read-only open and optional imported-program MD5 check.

This process replaces file-count or top-level-copy assumptions. A `.gpr` file
without its meaningful recursive `.rep` store is not a backup.
After the path, receipt, and timeout hardening, the trusted final endpoint was
verified again: `19` files, `177,015,687` bytes, zero copy differences,
canonical imported-program MD5 match, successful read-only open, stable source
and copy, and empty scratch after cleanup. The ignored receipt SHA-256 is
`3b9002dc0eb04fa843a69105b90ad18fa01b2a682c3110e0780356117583f9b3`.

## Documentation Reconciliation

The accepted decisions were applied in one batch. Every Markdown document named
by either correction manifest now carries a current semantic-revalidation
notice, while current authority maps and function pages were directly corrected
where they expressed the stale claim. Required lore mirrors were updated in the
same batch. The deterministic reconciliation check reports `481` impacted
tracked Markdown documents and zero missing or stale notices.

Four manifest references are intentionally outside this lane: two read-only
reference-source files, one private inventory TSV, and a primary-owned
`.codex/state` file. The integration owner should record the closeout and the
pending live-correction lease in canonical state; this worker did not edit the
primary-owned state batons.

Exact proposed state-baton delta for the integration owner:

- mark the deleted full re-audit campaign absorbed and independently reviewed
  in read-only mode;
- record `71` Cursor-delta plus `22` targeted records with one superseding
  overlap, for `92` unique correction addresses and zero unresolved Phase A
  verdicts;
- keep live correction open behind an exclusive lease, with targeted
  `0x00481060` precedence and a separate structured-prototype gate for
  `0x0050b9c0`; and
- retain the ignored recovery overlay and Cursor transcript project until
  branch integration is acknowledged.

## Claim Boundary

This closeout establishes static Ghidra project state, backup survivability,
and the quality of recovered and newly performed semantic review. It is not
copied-runtime causality, gameplay proof, visual proof, patch behavior, strict
clean-room proof, rebuild parity, or no-noticeable-difference parity. It also
does not claim that the deleted ledger was fully recovered or that the proposed
corrections have already been applied to the live Ghidra database. The snapshot
comparison proves net endpoint state, not the absence of a transient mutation
that left no surviving evidence.
