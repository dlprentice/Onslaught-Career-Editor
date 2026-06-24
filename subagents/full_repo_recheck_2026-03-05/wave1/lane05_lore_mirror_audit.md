# Lane 05 Lore Mirror Audit

Date: 2026-03-05
Scope: `lore-book` mirrors and Lore Browser content structure.
Method: read-only audit of canonical lore indexes, curated `BOOK.md` / `Start-Here.md`, and Lore Browser tree/search loading code.

## Overall

Mirror sync looks healthy for the core `lore/` set. The bigger problems are curation and discoverability: the Lore Browser treats `BOOK.md` as the authoritative ingest list, so documents omitted from that TOC quietly fall out of the left tree and browser search even when the mirrored files are present and canonically indexed.

## Confirmed Passes

- `PASS | lore/_index.md:9 | lore-book/lore/_index.md:9 | The lore mirror policy is explicit: only relative-link/path normalization is allowed to differ.`
- `PASS | lore/_index.md:17 | lore/_index.md:29 | lore-book/lore/_index.md:17 | lore-book/lore/_index.md:29 | The canonical lore chapter set is mirrored cleanly; the only observed lore-side content drift was the allowed `_index.md` mirror note/link-depth rewrite.`
- `PASS | lore-book/BOOK.md:3 | lore-book/Start-Here.md:5 | The book has a coherent narrative top-level shape (world -> studio/preservation -> deep dives -> appendices) rather than a raw filesystem dump.`

## Findings

- `HIGH | Views/LoreBrowserView.xaml.cs:329 | Views/LoreBrowserView.xaml.cs:447 | Views/LoreBrowserView.xaml.cs:1165 | lore-book/Start-Here.md:14 | lore-book/Start-Here.md:34 | When BOOK mode is active, the browser only ingests docs named in BOOK.md. That means omitted files are absent from the left tree and from content search, which conflicts with Start Here's promise that users can still "browse the copied directories under lore-book/". In practice, users can only reach omitted docs through links embedded in already-listed pages.`
- `HIGH | lore/_index.md:29 | lore/discord-archive-extract-2026-03.md:1 | lore-book/BOOK.md:14 | lore-book/BOOK.md:23 | lore-book/Start-Here.md:21 | lore-book/Start-Here.md:24 | The new Discord archive extract is canonical, high-signal preservation content, but it is missing from the curated reading order and suggested paths. Because BOOK drives ingestion, this provenance page is effectively buried despite being one of the newest and most preservation-critical lore artifacts.`
- `MEDIUM | lore-book/reverse-engineering/RE-INDEX.md:60 | lore-book/reverse-engineering/RE-INDEX.md:77 | lore-book/reverse-engineering/binary-analysis/_index.md:19 | lore-book/reverse-engineering/binary-analysis/_index.md:32 | lore-book/BOOK.md:41 | lore-book/BOOK.md:49 | The Binary Analysis appendix underrepresents the current summary/status layer. Canonical indexes surface high-signal overview docs such as capture-menu behavior, deep-validation status, display modernization plan, documentation audit, and semantic audit, but the curated tree exposes only a narrow subset. Users browsing from the left tree get an incomplete picture of current RE state unless they manually drill through index pages.`
- `MEDIUM | lore-book/Start-Here.md:5 | lore-book/BOOK.md:64 | lore-book/BOOK.md:69 | lore-book/BOOK.md:70 | lore-book/BOOK.md:85 | lore-book/roadmap/ROADMAP-INDEX.md:29 | lore-book/roadmap/ROADMAP-INDEX.md:43 | The curated book mixes reader-facing material with operator/internal artifacts. Examples: "Source Code Request List for Stuart" and "Agent Workflow" are promoted directly in the primary tree, while some more current project-facing docs called out in the canonical roadmap index (for example the release allowlist profile) are not. This weakens the stated "organized for reading" intent by mixing audience types without a clear boundary.`
- `LOW | lore-book/Start-Here.md:21 | lore-book/Start-Here.md:24 | lore-book/lore/_index.md:33 | lore-book/lore/_index.md:70 | Start Here is thinner than the actual lore index. The lore index provides strong topic-based anchor navigation, but Start Here advertises only a few linear paths. New users landing on Start Here miss preservation/provenance-oriented entry points and the richer topical shortcuts already available one click deeper.`

## Priority Actions

1. Add omitted high-signal docs to `lore-book/BOOK.md` when they should be first-class browser content. Minimum obvious candidate: `lore/discord-archive-extract-2026-03.md`.
2. Decide whether BOOK should be a curated subset or the browser's complete corpus. If it stays curated, the UI copy in `Start-Here.md` should stop implying raw-directory browse/search completeness.
3. Split the tree more intentionally by audience. A clean boundary such as `Lore`, `Preservation`, `Technical Appendix`, and `Project/Internal` would reduce the current mixing of reader-facing chapters with operator workflow docs.
4. Revisit the Binary Analysis appendix curation so the left tree includes a few high-value summary/status docs, not just deep technical indices and selected analyses.

## Audit Conclusion

This lane did not find a broad lore mirror failure. The main risk is user-facing curation drift: the files exist, the canonical indexes know about them, but the Lore Browser's BOOK-driven ingest model hides some of the highest-signal material and muddles audience boundaries in the curated tree.
