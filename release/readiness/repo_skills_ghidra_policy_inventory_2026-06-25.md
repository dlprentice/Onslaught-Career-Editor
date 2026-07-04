# Repo Skills And Ghidra Policy Inventory - 2026-06-25

Status: accepted public-primary policy inventory

## Scope

This slice inventoried repo-specific Codex skill material and the local Ghidra
project distribution posture for the public-primary repo. It did not move,
copy, publish, link, mutate, or package full Ghidra projects, game payloads,
copied executables, saves/options payloads, raw proof bundles, secrets, runtime
caches, or release artifacts.

## Inventory

- Public repo `.codex/` tracks only compact goals/state Markdown batons.
- Public repo has no tracked `SKILL.md`, `skills/`, or `.codex/skills/` tree.
- Former private repo has the same tracked `.codex/goals` and `.codex/state`
  shape for this purpose; no private-only repo skill tree was found.
- Relevant repo-specific maintainer-local Codex skills reviewed under
  `[maintainer-local-codex-skills]` were: `aya-assets`, `bea-binary-re`,
  `bes-career-save`, and `onslaught-engine-source`.
- Those local skills are routing conveniences over tracked repo docs/tools; they
  are not public clone prerequisites.
- Maintainer-local live Ghidra project remains:
  `[maintainer-local-ghidra-project-root]\BEA.gpr` with store
  `[maintainer-local-ghidra-project-root]\BEA.rep\`.

## Decision

Keep active Codex skills user-local for now. Make the public repo durable by
recording their routing in normal tracked docs instead of copying runtime-owned
skill files into `.codex/skills`.

Keep full Ghidra project databases and backups local/ignored. Track
deterministic Ghidra exports, scripts, rename maps, ledgers, hashes,
Markdown/JSON/TSV summaries, and compact proof summaries when useful.

## Consult Review

- Specialist read-only consult: found no tracked public or private repo skill
  tree and recommended documenting skill routing in `LOCAL_LAB_OVERLAY.md` and
  `tools/README.md`.
- Adversarial security review: blocked public Ghidra DB distribution,
  repo-local `.codex/skills`/runtime-cache publication, and hardlink-style
  payload distribution. It accepted tracked `.codex/goals` and `.codex/state`
  Markdown as non-secret project batons.

Accepted findings were applied. No rejected blocking consult findings remain.

## Validation Run

Closeout validation passed:

```powershell
git ls-files .codex
# PASS: only .codex/goals/*.md and .codex/state/*.md are tracked.

git ls-files | rg "(^|/)SKILL\.md$|(^|/)skills/"
# PASS: no tracked SKILL.md, skills/, or .codex/skills/ paths.

git check-ignore -v game\BEA.exe local-ghidra\GhidraBackups local-proofs\OnslaughtRuntimeProofArchive .codex\skills\bea-binary-re\SKILL.md
# PASS: game/, local-ghidra/, local-proofs/, and .codex/skills/ are ignored.

npm run test:hard-payload-safety
# PASS: public payload safety check, 19313 public candidate files checked.

npm run test:public-allowlist
# PASS: hard-payload safety, submodule payload safety, and public-primary migration inventory.
# Migration inventory at validation time: private tracked paths 24839, public tracked paths 19313,
# accepted private-only hard-payload/scratch paths 5557.

npm run test:md-links
# PASS: 3623 Markdown files scanned, 6125 local links checked.

npm run test:repo-hygiene
# PASS: repo text hygiene, line-ending tests, and 18465 explicit text files checked.
```

No app ZIP release is required for this policy/docs-only slice.
