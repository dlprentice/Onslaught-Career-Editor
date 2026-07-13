# Lore Editorial And Provenance Audit

Status: approved design and active editorial audit
Last updated: 2026-07-13

## Purpose And Boundary

This audit defines the first bounded editorial-quality and provenance slice for
the offline Lore corpus. It treats the packaged document count as an archive
measurement, not as evidence that every document is current, curated, verified,
or cleared for redistribution.

The generated inventory described below reports deterministic editorial triage
signals only. Quotation metrics, source-risk terms, freshness markers, external
domains, and canonical/projection divergence are not automated legal, rights,
safety, or historical conclusions. Generated artifacts must not reproduce source
excerpts, raw Discord or private-dump text, private paths, or long copyrighted
quotations.

The first slice does not rewrite Lore claims, synchronize divergent prose,
change the Lore pack schema, change WinUI behavior, or edit canonical goal or
state files. Safer mirror divergences remain intact until a human-reviewed
canonical decision.

## Corpus Taxonomy

The tracked `lore-book/` Markdown/TXT input currently contains 955 packable
documents. The published v1.0.9 count of 949 remains a release-snapshot fact;
it is not the current source-tree count.

| Taxonomy family | Documents | Editorial role |
| --- | ---: | --- |
| Binary analysis | 765 | Technical RE archive and proof history |
| Game assets | 86 | Asset-format, extraction, and proof material |
| Source code | 24 | Reference-source architecture and provenance notes |
| Roadmap | 23 | Plans, status, and historical work queues |
| Narrative Lore | 15 | Reader-facing game, studio, people, and preservation articles |
| Quick reference | 14 | Condensed technical lookup material |
| Save files | 10 | Save-format and career-system documentation |
| Project meta | 6 | Attribution, community, and repository context |
| Game mechanics | 4 | Released-game mechanic notes |
| Lore front doors | 3 | Book, start page, and capability entry point |
| Other top-level RE | 5 | RE index and public technical contracts |

The archive is therefore dominated by technical material: 765 of 955 documents
are under `reverse-engineering/binary-analysis/`. Reader navigation should not
present archive breadth as narrative editorial depth.

## Provenance And Rights Risk Matrix

| Evidence class | Typical examples | Editorial use | Triage risk |
| --- | --- | --- | --- |
| First-party current | Official storefront or publisher page; current repository implementation and tests | Preferred for current factual claims | Facts can change; quotation and trademark rights remain separate |
| First-party historical | Archived Lost Toys pages; developer-authored post-mortem | Strong historical evidence when date and context are retained | Archive availability does not grant redistribution rights |
| Public testimony | Named developer interview, public post, or public repository statement | Attribute as testimony and distinguish recollection from independently verified fact | Context, date, and public availability must be reviewable |
| Secondary source | Wikipedia, MobyGames, Metacritic, press coverage | Corroboration or discovery lead | Prefer a primary source for consequential or unstable claims |
| Community testimony | Public community discussion, preservation observation, Discord-derived extract | Label as recollection, report, or observation | Raw source may be unavailable or semi-private; do not imply independent verification |
| Project RE evidence | Static analysis, copied-runtime summary, test, or accepted behavior contract | State the exact evidence class and non-claims | Static, runtime, patch, visual, and rebuild evidence are not interchangeable |
| Proprietary/private input | Manual, game payload, private dump, local asset, raw proof bundle | Public-safe metadata or bounded summary only | Do not redistribute or expose private paths or source payloads |

The matrix guides human review. It does not decide copyright, permission,
privacy, historical truth, or release safety.

## Current And Stale Truth Findings

1. The current tracked packable count is 955. References to 949 are accurate
   only when explicitly scoped to the published v1.0.9 package.
2. Seven of the 15 canonical `lore/*.md` documents differ from their
   `lore-book/lore/` projections, but `tools/docsync_policy.json` does not
   currently validate this projection family.
3. Some projection differences replace named Discord/private-source framing
   with safer public wording. Canonical precedence and public-safe wording are
   consequently inconsistent. Automatic synchronization would be unsafe.
4. `lore/discord-archive-extract-2026-03.md` cites line locations in retired raw
   dumps. It is a provenance-preserving project extract, but its citations are
   not independently resolvable from the public repository.
5. Several narrative documents contain extensive block quotations from
   magazines or interviews. `lore/development-history.md` has 51 block-quoted
   lines and needs human quotation/redistribution review before it can be called
   editorially cleared.
6. The Steam review count recorded in `lore/reference-materials.md` is clearly
   labeled as a 2024 snapshot. On 2026-07-13, the official Steam page showed
   91% positive from 134 Steam-purchaser reviews, illustrating why unstable
   counts need dates rather than silent replacement.
7. The official PlayStation Store and PlayStation Blog confirm the PS4/PS5
   release on 2025-05-20. GOG continues to list the Windows release.

Primary public checks:

- Steam: <https://store.steampowered.com/app/1346400/Battle_Engine_Aquila/>
- GOG: <https://www.gog.com/en/game/battle_engine_aquila>
- PlayStation Store: <https://store.playstation.com/en-us/concept/10013168>
- PlayStation Blog: <https://blog.playstation.com/2025/05/14/playstation-plus-game-catalog-for-may-sand-land-soul-hackers-2-five-nights-at-freddys-help-wanted-battlefield-v-and-more/>

## Generated-Canonical Strategy

Canonical prose remains in `lore/`, `reverse-engineering/`, and `roadmap/`.
`lore-book/` remains a protected projection and packaging source, not a second
authority. The first generator produces a repository-relative inventory with:

- a stable taxonomy family derived from the tracked path;
- the declared or structurally implied canonical source, where one exists;
- canonical/projection content hashes and a parity result;
- explicit status and last-updated markers found near the document header;
- the last Git commit date for freshness triage;
- bounded counts and labels for quotation, source-risk, and external-domain
  signals; and
- no document body, matching excerpt, local absolute path, or legal conclusion.

`lore/corpus-taxonomy.v1.json` is the human-reviewed policy input.
`lore/generated/corpus-inventory.v1.json` is a deterministic projection. Check
mode compares the expected JSON bytes with the tracked file and fails on drift.

Claim-level provenance is a later curated layer for the small reader-facing
surface. It should not be inferred for all 955 documents from keywords.

## Prioritized Editorial Slices

1. Generate the corpus inventory and detect projection drift without copying
   source prose.
2. Human-review the seven divergent narrative projection pairs and define the
   exact safe transformation or canonical wording for each.
3. Add claim-level provenance to the highest-risk narrative documents,
   beginning with development history, reference materials, team roster, and
   cut-content claims.
4. Replace or shorten extensive third-party quotations while preserving
   attribution and historical meaning.
5. Generate distinct navigation for narrative reading, current technical
   reference, and historical campaign evidence.
6. Consider pack-level classifications only in a separate AppCore/WinUI-owned
   slice; do not couple that product change to this editorial inventory.

## First Slice Implementation Plan

The approved first slice has four file families:

1. `tools/lore_corpus_inventory.py` and
   `tools/lore_corpus_inventory_test.py`: tested generator and check mode.
2. `lore/corpus-taxonomy.v1.json`: schema, path-family rules, signal labels,
   and explicit non-conclusion language.
3. `lore/generated/corpus-inventory.v1.json`: deterministic generated output.
4. This audit: taxonomy, risk matrix, truth findings, strategy, and priorities.

Test-driven sequence:

1. Write failing tests for path taxonomy, source-safe signal output,
   canonical/projection parity, and deterministic check-mode drift detection.
2. Implement only the generator behavior required by those tests.
3. Generate and check the tracked inventory.
4. Run focused tests, docsync, current-doc command/link validation,
   hard-payload safety, and `git diff --check`.
5. Obtain normal and adversarial Codex review plus bounded sanitized external
   normal and adversarial consults before acceptance.

## Acceptance And Non-Claims

The slice is accepted only when regeneration is deterministic, tests prove no
source excerpts or absolute paths enter the inventory, divergent prose remains
unchanged, focused and proportionate gates pass, and independent review has no
unresolved blocker.

It does not establish that the corpus is legally cleared, historically
complete, fully current, safe for every release channel, or editorially reviewed
document by document.
