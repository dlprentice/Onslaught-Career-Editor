# Lane 04 RE Docs Audit

Date: 2026-03-05
Scope: canonical `reverse-engineering/**` docs, excluding scratch-noise review.
Mode: read-only audit; no tracked-file edits.

## Summary

Findings: 6 total
- 1 high
- 1 medium-high
- 3 medium
- 1 low

Core retail-backed save/options findings are largely consistent across `RE-INDEX.md`, `save-file/*`, and `game-mechanics/*`. Remaining drift is concentrated in summary pages and release-facing/project-meta material.

## Findings

### 1. High: release-facing privacy/legal risk in canonical project-meta docs
Files:
- `reverse-engineering/project-meta/attribution.md:19-25`
- `reverse-engineering/project-meta/attribution.md:47`
- `reverse-engineering/project-meta/attribution.md:198`
- `reverse-engineering/project-meta/_index.md:20-24`
- `reverse-engineering/project-meta/_index.md:37`

Issue:
- Canonical docs expose personal contact vectors and subjective commentary, including LinkedIn/Discord/Facebook references, a direct email address, a Discord invite, and a personal-attitude note (`"little passion"`).
- The legal note at `attribution.md:198` also makes a strong ownership claim (`assets defaulted to Crown (UK)`) without source framing.

Why it matters:
- This is the largest release-facing risk in the RE corpus.
- It mixes technical attribution with personal/contact/legal material that is unnecessary for most readers and hard to justify in a public-facing canonical index.

Recommendation:
- Split private contact/legal triage into private-only notes.
- Keep canonical attribution limited to role, contribution, and source-backed public facts.
- Reword legal status as unresolved/legal-review-needed unless a cited source is included.

### 2. Medium-high: `god-mode.md` implies two `g_bGodModeEnabled` storages where the docs elsewhere describe one field
Files:
- `reverse-engineering/game-mechanics/god-mode.md:24-35`
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:702`

Issue:
- `god-mode.md` says the persisted CCareer field at file `0x2496` and a runtime global at `0x00662ab4` should not be confused.
- `GHIDRA-REFERENCE.md:702` documents `0x00662ab4` as `CCareer +0x2494` / file `0x2496`, i.e. the in-memory address of the same field.

Why it matters:
- This creates avoidable symbol/field confusion in a doc that is supposed to close earlier god-mode mislabeling.
- Future RE or app work could incorrectly treat one field as two separate variables.

Recommendation:
- Rephrase as: same field, different representations (`file offset 0x2496` vs in-memory address `0x00662ab4`).

### 3. Medium: stale top-level binary-analysis summary still points readers at “god mode offsets”
File:
- `reverse-engineering/binary-analysis/README.md:64`

Issue:
- The summary row for `CCareer__Blank` still says `Career blank/init (graph reset), god mode offsets`.
- Current retail-backed docs say the former `mIsGod[]` save offsets were misidentified and are now mapped as invert-Y/reserved fields, with only `0x2496` retained as the cheat-gated persisted toggle state.

Why it matters:
- This is a high-visibility summary page and contradicts the corrected Steam mapping.

Recommendation:
- Replace with wording aligned to current mapping, e.g. `Career blank/init and post-0x248A defaults/mapped option fields` or equivalent.

### 4. Medium: internal-build statement in `save-format.md` is easy to misread as retail-backed persistence
File:
- `reverse-engineering/save-file/save-format.md:74-78`

Issue:
- The Stuart-message bullet list includes `God mode Boolean stored in career class`.
- It sits inside the canonical retail save-format doc, but the line itself is not explicitly labeled as internal/source-only even though later sections document the Steam correction.

Why it matters:
- Readers skimming the page can walk away with the wrong takeaway before reaching the retail-specific correction later in the document.

Recommendation:
- Add an immediate qualifier on that bullet that it is internal/source context, not a confirmed Steam on-disk field layout.

### 5. Medium: canonical evidence table depends on scratch artifacts
File:
- `reverse-engineering/binary-analysis/high-impact-subsystem-contracts.md:21-23`
- `reverse-engineering/binary-analysis/high-impact-subsystem-contracts.md:26-31`

Issue:
- Multiple evidence cells cite `scratch/program_2026-03-01/phase5_signature_readback/index.tsv`.

Why it matters:
- Scratch paths are operational artifacts, not stable canonical evidence anchors.
- If scratch cleanup or curated release packaging excludes those paths, the canonical doc keeps claims whose proof trail is no longer packaged.

Recommendation:
- Promote read-back summaries into canonical docs or a stable appendix outside `scratch/`.
- Keep scratch references as optional provenance, not primary evidence.

### 6. Low: several canonical docs link to repo-private operational file `/AGENTS.md`
Files:
- `reverse-engineering/save-file/_index.md:60`
- `reverse-engineering/game-mechanics/_index.md:58`
- `reverse-engineering/game-assets/_index.md:56`
- `reverse-engineering/project-meta/_index.md:36`
- `reverse-engineering/binary-analysis/README.md:95`

Issue:
- Canonical RE docs use absolute-root links to `/AGENTS.md`.

Why it matters:
- These links are brittle outside the full private repo layout.
- They also pull internal operational guidance into public-facing doc navigation.

Recommendation:
- Remove these from release-facing `See Also` sections, or replace them with canonical RE/roadmap docs that are intended to ship.

## Non-findings

Areas that looked current in this pass:
- True-dword-view vs legacy aligned-view save semantics
- `defaultoptions.bea` / `.bes` load-path distinctions
- Options entries as control bindings plus `0x56` tail snapshot
- Retail mapping of `0x249A..0x24BA` away from legacy `mIsGod[]` assumptions
