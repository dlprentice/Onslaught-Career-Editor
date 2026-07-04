# Depth4 Lane 02 Lore/Canonical Mirror Closure Plan

Date: 2026-03-04
Owner lane: 2/10
Synthesis source files:
- `subagents/depth1/lane06_lorebook_mirror_inventory.md`
- `subagents/depth2/lane02_lore_mirror_contradictions.md`
- `subagents/depth3/lane02_lore_fixcards.md`

## Closure Target
Bring `lore-book/lore/*.md` into deterministic parity with canonical `lore/*.md` using lane-2 fix cards:
- `A0_KEEP_EXACT` for 13 files
- `A1_KEEP_DEPTH_ADJUSTED_AGENTS_LINK` for `lore/_index.md` only

Guardrail from findings: after closure, allowed non-identical lore pair count must be exactly `1`, and it must be `_index.md` with only the `AGENTS.md` relative-path depth delta.

## Exact File Sync Order
Run from repo root (`redacted-private-source`) in this exact sequence.

```bash
set -euo pipefail

cp lore/LORE-INDEX.md lore-book/lore/LORE-INDEX.md
cp lore/_index.md lore-book/lore/_index.md
sed -i 's|\[AGENTS.md\](../AGENTS.md)|[AGENTS.md](../../AGENTS.md)|' lore-book/lore/_index.md
cp lore/battle-engine-tech.md lore-book/lore/battle-engine-tech.md
cp lore/characters.md lore-book/lore/characters.md
cp lore/community-preservation.md lore-book/lore/community-preservation.md
cp lore/cut-content-secrets.md lore-book/lore/cut-content-secrets.md
cp lore/development-history.md lore-book/lore/development-history.md
cp lore/game-overview.md lore-book/lore/game-overview.md
cp lore/lost-toys-history.md lore-book/lore/lost-toys-history.md
cp lore/reception-legacy.md lore-book/lore/reception-legacy.md
cp lore/reference-materials.md lore-book/lore/reference-materials.md
cp lore/team-roster.md lore-book/lore/team-roster.md
cp lore/technical-deep-dive.md lore-book/lore/technical-deep-dive.md
cp lore/world-lore.md lore-book/lore/world-lore.md
```

## Verification Commands
Run all commands below after sync; closure is complete only if all checks pass.

### 1. Presence and cardinality parity (14 canonical, 14 mirror)
```bash
test "$(find lore -maxdepth 1 -type f -name '*.md' | wc -l)" -eq 14
test "$(find lore-book/lore -maxdepth 1 -type f -name '*.md' | wc -l)" -eq 14
```

### 2. Pairwise parity summary must show 13 `MATCH` and only `_index.md` as `DIFF`
```bash
for f in $(find lore -maxdepth 1 -type f -name '*.md' | sort); do
  b="$(basename "$f")"
  m="lore-book/lore/$b"
  if cmp -s "$f" "$m"; then
    echo "MATCH $b"
  else
    echo "DIFF  $b"
  fi
done | tee /tmp/lane02_lore_cmp.txt

test "$(rg -c '^MATCH ' /tmp/lane02_lore_cmp.txt)" -eq 13
test "$(rg -c '^DIFF ' /tmp/lane02_lore_cmp.txt)" -eq 1
test "$(rg -c '^DIFF  _index.md$' /tmp/lane02_lore_cmp.txt)" -eq 1
```

### 3. `_index.md` allowed delta verification (AGENTS link depth only)
```bash
rg -n '^> - \[AGENTS.md\]\(\.\./AGENTS.md\) - Project overview and technical reference$' lore/_index.md
rg -n '^> - \[AGENTS.md\]\(\.\./\.\./AGENTS.md\) - Project overview and technical reference$' lore-book/lore/_index.md

diff -u lore/_index.md lore-book/lore/_index.md | tee /tmp/lane02_lore_index.diff || true

{ diff -u lore/_index.md lore-book/lore/_index.md || true; } \
  | rg -n '^[+-]' \
  | rg -v '^\d+:(---|\+\+\+) ' \
  | tee /tmp/lane02_lore_index_changes.txt

test "$(wc -l < /tmp/lane02_lore_index_changes.txt)" -eq 2
rg -n '^\d+:-> - \[AGENTS.md\]\(\.\./AGENTS.md\) - Project overview and technical reference$' /tmp/lane02_lore_index_changes.txt
rg -n '^\d+:\+> - \[AGENTS.md\]\(\.\./\.\./AGENTS.md\) - Project overview and technical reference$' /tmp/lane02_lore_index_changes.txt
```

## Closure Exit Criteria
- All 14 mirror targets exist.
- 13 lore file pairs are byte-identical (`A0`).
- Exactly 1 lore file pair differs: `_index.md`.
- `_index.md` diff is exactly one line rewrite from `../AGENTS.md` to `../../AGENTS.md` and nothing else.
