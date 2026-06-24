# Lane 07 - Release Docs / Commands Audit

## Scope
- `README.RELEASE.md`
- `RELEASE_SCOPE_AND_TEST_COMMANDS.md`
- `release/readiness/*`
- roadmap release artifacts
- top-level capability/release-facing docs
- release tooling fact-check (`tools/release_package.sh`, `tools/release_curated_manifest.py`, `tools/release_profile_snapshot.py`)

## Summary
The underlying release scripts are mostly coherent. The main problems are stale generated release artifacts and one public-facing roadmap index that still links to files the curated manifest excludes.

## Findings

### 1. High - `public_candidate_allowlist.tsv` is stale and currently contradicts the curated manifest/redaction policy
The curated manifest explicitly excludes operational/internal docs such as the mutation backlog, documentation audit, and maintainer-only release-profile docs, but the generated public allowlist still includes them as `R0_ALLOW`.

Evidence:
- `release/readiness/public_candidate_allowlist.tsv:65` includes `lore-book/reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`
- `release/readiness/public_candidate_allowlist.tsv:71` includes `lore-book/reverse-engineering/binary-analysis/documentation-audit.md`
- `release/readiness/public_candidate_allowlist.tsv:508` includes `lore-book/roadmap/release-allowlist-profile.md`
- `release/readiness/public_candidate_allowlist.tsv:565` includes `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`
- `release/readiness/public_candidate_allowlist.tsv:571` includes `reverse-engineering/binary-analysis/documentation-audit.md`
- `release/readiness/public_candidate_allowlist.tsv:1008` includes `roadmap/release-allowlist-profile.md`
- `release/readiness/curated_release_manifest.json:73` excludes `roadmap/release-allowlist-profile.md`
- `release/readiness/curated_release_manifest.json:75` excludes `reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md`
- `release/readiness/curated_release_manifest.json:77` excludes `reverse-engineering/binary-analysis/documentation-audit.md`
- `release/readiness/curated_release_manifest.json:98` excludes `roadmap/release-allowlist-classification.tsv`
- `release/readiness/release_readiness_checklist.md:16` says the allowlist must be curated/manifest-derived, not raw inventory

Impact:
- A maintainer relying on the current allowlist could ship internal/ops-sensitive docs that policy says should stay out.
- Any doc that calls this allowlist authoritative is only true after regeneration/check passes.

### 2. High - release snapshot artifacts are stale/internally inconsistent with the current classification code
The generated release-profile/classification artifacts do not reflect the current `release_profile_snapshot.py` deny rules and manifest patterns.

Evidence:
- `tools/release_profile_snapshot.py:24`-`34` denies exact paths including `AGENTS.md`, `USER_SANITY_CHECK.md`, and the Ghydra MCP runbook pair
- `roadmap/release-allowlist-classification.tsv:7` still marks `AGENTS.md` as `R0_ALLOW`
- `roadmap/release-allowlist-classification.tsv:35` still marks `README.RELEASE.md` as a normal allow file
- `roadmap/release-allowlist-classification.tsv:5960` still marks `lore-book/reverse-engineering/binary-analysis/ghydra-mcp-runbook.md` as `R0_ALLOW`
- `roadmap/release-allowlist-classification.tsv:6516` still marks `reverse-engineering/binary-analysis/ghydra-mcp-runbook.md` as `R0_ALLOW`
- `roadmap/release-allowlist-classification.tsv:5587`, `6143` still mark both mutation-backlog docs as `R0_ALLOW`
- `roadmap/release-allowlist-classification.tsv:5594`, `6150` still mark both documentation-audit docs as `R0_ALLOW`
- `roadmap/release-allowlist-classification.tsv:5982`, `18840` still mark semantic-audit docs as `R0_ALLOW`
- `release/readiness/curated_release_manifest.json:31` includes `tests_shared/**`
- `roadmap/release-allowlist-profile.md:16`-`50` lists curated include patterns but omits `tests_shared/**`

Additional note:
- `release/readiness/private_only_inventory.tsv` contains `setuphistory.txt` and the literal `|` deny entry (`release/readiness/private_only_inventory.tsv:5545`, `5631`), but search found no row for `AGENTS.md` or `USER_SANITY_CHECK.md`, which should be present if the snapshot artifacts were current with `tools/release_profile_snapshot.py:24`-`34`.

Impact:
- The roadmap/readiness artifacts cannot currently be trusted as a faithful picture of release scope.
- This is a release-go/no-go problem because these are the maintainer-facing inventory documents.

### 3. Medium - `roadmap/ROADMAP-INDEX.md` links to release artifacts that the curated public candidate excludes
The roadmap index is itself included in the public candidate, but it still advertises maintainer-only release artifacts that the manifest/redaction policy explicitly excludes.

Evidence:
- `roadmap/ROADMAP-INDEX.md:46` links `release-allowlist-profile.md`
- `roadmap/ROADMAP-INDEX.md:47` links `release-allowlist-classification.tsv`
- `release/readiness/curated_release_manifest.json:73` excludes `roadmap/release-allowlist-profile.md`
- `release/readiness/curated_release_manifest.json:98` excludes `roadmap/release-allowlist-classification.tsv`
- `release/readiness/redaction_notes.md:24` flags `roadmap/release-allowlist-profile.md` as a hard exclusion

Impact:
- In the curated public repo, this produces broken/maintainer-only links from an otherwise shipped roadmap index.
- It also muddies the public/private boundary for release-maintenance docs.

### 4. Medium - `README.MD` still reads like a prebuilt-exe distribution even though the current release model is curated-source-first
The root README tells users to run `Onslaught - Career Editor.exe` directly, but the curated manifest excludes `*.exe` and the release notes say the public release model is the source repo layout.

Evidence:
- `README.MD:56`-`69` tells users to run `Onslaught - Career Editor.exe` and shows CLI examples using the executable name directly
- `README.RELEASE.md:21`-`29` says the current release model is a curated public repo that users clone/download and build/run from that layout
- `release/readiness/curated_release_manifest.json:58` excludes `**/*.exe`

Impact:
- Public readers may expect a checked-in binary that will not exist in the curated repo.
- The README should either default to `dotnet run` / build-from-source instructions or clearly gate the `.exe` examples behind “after local build.”

### 5. Low - the literal `|` deny entry appears in release-facing artifacts without explanation
A raw `|` path is present in the deny lists and then surfaces in generated release artifacts. It may be real repo debris, but as currently written it reads like a manifest mistake.

Evidence:
- `tools/release_package.sh:48` lists `|` under `DENY_EXACT`
- `tools/release_profile_snapshot.py:33` lists `|` under `DENY_EXACT`
- `release/readiness/redaction_notes.md:42` lists `|` as a hard exclusion
- `roadmap/release-allowlist-profile.md:65` lists `|` under hard exclusions
- `release/readiness/private_only_inventory.tsv:5631` contains a row for `|`

Impact:
- This is mostly cosmetic, but it lowers confidence in the release docs and can confuse reviewers about whether the deny policy is intentional or corrupted.

## Net Assessment
- Release tooling logic: mostly sound.
- Release-facing generated artifacts: not fully in sync with current policy.
- Public/private boundary docs: close, but not yet clean enough to trust without regeneration and link cleanup.
