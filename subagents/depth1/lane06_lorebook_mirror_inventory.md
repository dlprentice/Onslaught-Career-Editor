## Summary
- `lore-book/` is a curated reader-facing wrapper around canonical docs, with two lore-book-only entrypoints: `lore-book/BOOK.md` and `lore-book/Start-Here.md`.
- Mirror roots are:
  - `lore-book/lore/**` <-> `lore/**` (14 vs 14 files)
  - `lore-book/roadmap/**` <-> `roadmap/**` (16 vs 16 files)
  - `lore-book/reverse-engineering/**` <-> `reverse-engineering/**` for canonical docs, with `binary-analysis/scratch/**` intentionally partial by policy.
- Non-scratch canonical RE docs are mirrored; the large count delta is scratch-only (`reverse-engineering/binary-analysis/scratch`: 12,317 canonical files vs 15 mirrored files).
- Byte-compare on mirrored pairs found 10 intentional divergences (curated ordering and relative-link depth fixes), not broad drift.

## Structure
- `lore-book/BOOK.md`
  - Curated ToC for Lore Browser reading order.
  - Pulls content from mirrored `lore/`, `reverse-engineering/`, and `roadmap/` subtrees.
- `lore-book/Start-Here.md`
  - Reader onboarding and suggested pathways; explicitly says raw engineering structure remains under copied `lore-book/` directories.
- `lore-book/lore/`
  - Mirror of canonical lore corpus (`_index.md`, `LORE-INDEX.md`, and topic docs).
- `lore-book/reverse-engineering/`
  - Mirror of RE docs (`save-file`, `game-mechanics`, `game-assets`, `source-code`, `project-meta`, `binary-analysis`).
  - Includes `binary-analysis/functions/**` corpus mirror.
  - Includes only a narrow explicit subset of `binary-analysis/scratch/**`.
- `lore-book/roadmap/`
  - Mirror of canonical roadmap docs, with lore-book-specific curation in indexing/navigation text.

## Mirror Map
| Mirror path root | Canonical source root | Current parity shape | Likely parity-sensitive paths |
|---|---|---|---|
| `lore-book/lore/**` | `lore/**` | Full file-count parity (14/14). | `lore-book/lore/_index.md` (relative link-depth adjustment to `AGENTS.md`). |
| `lore-book/roadmap/**` | `roadmap/**` | Full file-count parity (16/16), but curated text/order can intentionally differ. | `lore-book/roadmap/ROADMAP-INDEX.md`, `lore-book/roadmap/agent-workflow.md` (book-nav and canonical-operator-link framing). |
| `lore-book/reverse-engineering/**` (non-scratch) | `reverse-engineering/**` (non-scratch) | Canonical docs mirrored; no non-scratch missing files detected. | `_index.md` files with relative-link depth differences: `save-file/_index.md`, `game-mechanics/_index.md`, `game-assets/_index.md`, `project-meta/_index.md`, plus `binary-analysis/README.md`. |
| `lore-book/reverse-engineering/binary-analysis/functions/**` | `reverse-engineering/binary-analysis/functions/**` | File-count parity (361/361). | `.../text.cpp/CText__GetStringById.md`, `.../text.cpp/CText__GetAudioNameById.md` (tool-link depth differs). |
| `lore-book/reverse-engineering/binary-analysis/scratch/**` | `reverse-engineering/binary-analysis/scratch/**` | Intentionally partial mirror (15 vs 12,317). | `lore-book/.../scratch/program_2026-03-01/**` subset is mirrored; all other scratch waves remain canonical-only unless explicitly requested. |
| `lore-book/BOOK.md`, `lore-book/Start-Here.md` | none (lore-book-only curation layer) | No canonical peer by design. | Both are navigation-control points that can drift from canonical document evolution. |

## Drift Risk Areas
- Curated index drift risk:
  - `lore-book/BOOK.md` and `lore-book/Start-Here.md` are hand-curated reading flows; they can lag when canonical docs are added/renamed/reordered.
- Intentional divergence files (watchlist):
  - `lore-book/lore/_index.md`
  - `lore-book/reverse-engineering/binary-analysis/README.md`
  - `lore-book/reverse-engineering/game-assets/_index.md`
  - `lore-book/reverse-engineering/game-mechanics/_index.md`
  - `lore-book/reverse-engineering/project-meta/_index.md`
  - `lore-book/reverse-engineering/save-file/_index.md`
  - `lore-book/reverse-engineering/binary-analysis/functions/text.cpp/CText__GetStringById.md`
  - `lore-book/reverse-engineering/binary-analysis/functions/text.cpp/CText__GetAudioNameById.md`
  - `lore-book/roadmap/ROADMAP-INDEX.md`
  - `lore-book/roadmap/agent-workflow.md`
- Scratch asymmetry risk:
  - Consumers treating lore-book as a complete RE mirror may miss canonical operational artifacts under `reverse-engineering/binary-analysis/scratch/**`.
- High-churn operational doc risk (if mirrored for app browsing):
  - `function_mutation_attempt_log.jsonl`, `function_mutation_ledger.jsonl`, `function_mutation_tracking_state.json`, `MCP-MUTATION-BACKLOG.md` are update-heavy and parity-sensitive.
