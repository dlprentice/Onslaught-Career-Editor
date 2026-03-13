# Analyzer Enhancements

> Goal: Every field in the save file should be displayable, annotated, and understandable.

## Complete Field Display

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **Full node breakdown** | Show all 16 fields per node (State, mComplete, mLowerLink, mHigherLink, mWorldNumber, mBaseThingsExists[9], mNumAttempts, mRanking) | High | Medium |
| **Per-node hex dump** | `--node N` to hexdump specific node with field annotations | High | Low |
| **mBaseThingsExists decoder** | Show 288 objective bits as named flags where known | Medium | High |
| **Link field details** | Show mLinkType and mToNode for each link, not just completion status | Medium | Low |
| **Goodie state breakdown** | Show raw goodie state values (0/1/2/3) per index and clearly mark reserved entries; optionally show legacy aligned view for debugging | Medium | Low |
| **Tech slot bit viewer** | Show all 32 bits per slot with known bit meanings | Medium | Medium |
| **Reserved-byte decoder** | Attempt to interpret remaining reserved/unmapped bytes with multiple encoding hypotheses | Low | High |

## Annotated Hex Dumps

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **Color-coded hex output** | Different colors for known vs unknown fields (terminal ANSI support) | Medium | Medium |
| **Inline annotations** | `0x3F80` -> `(1.0f, S-rank)` next to raw bytes | High | Low |
| **Offset markers** | Show struct boundaries in hex dumps (e.g., "--- Node 5 Start ---") | High | Low |
| **Encoding hints** | Show both true-view and legacy aligned views (e.g., `0x00000064` true view; `0x00640000` legacy aligned view) | High | Low |
| **Float interpretation** | Auto-detect IEEE-754 floats and display human-readable values | Medium | Low |
| **Export to file** | `--analyze --export analysis.txt` for sharing/diffing | Low | Low |

## Enhanced Comparison Views

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **Semantic diff** | Show "Node 5 rank changed from A to S" instead of just byte offsets | High | Medium |
| **Three-way compare** | Compare patched vs gold vs fresh save simultaneously | Medium | High |
| **Side-by-side node view** | Aligned display of same node from two files | Medium | Medium |
| **Highlight-only mode** | Only show differing fields, skip identical sections | Low | Low |
| **JSON export** | Export analysis as JSON for external tools | Low | Low |

Note: Summary statistics (`--compare` shows byte counts and region summaries) already done.

## Per-Node Detailed Breakdown

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **Level name resolution** | Map mWorldNumber (100, 110, 200...) to level names | High | Medium |
| **Link graph visualization** | ASCII art of mission unlock tree from mLowerLink/mHigherLink | Medium | High |
| **Objective status grid** | 9-cell grid showing mBaseThingsExists[0-8] per node | Medium | Medium |
| **Attempt counter display** | Show mNumAttempts with "organic vs patched" indicator | Low | Low |

Note: Rank decoder is already done (raw float bits in node `mRanking`).

## Reserved/Unmapped Region Visualization

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **Pattern detection** | Flag repeating patterns, all-zero blocks, sentinel values | Medium | Medium |
| **Cross-save patterns** | Compare reserved/unmapped regions across multiple saves to find stable vs dynamic areas | High | High |
| **Known offset labels** | Show true-view offsets for known fields (e.g., volumes at 0x248E/0x2492) and label the dynamic options tail block by relative offsets | Medium | Low |
| ~~**EndLevelData cache map**~~ | ~~Attempt to map 0x24CC-0x26B7 to runtime level completion stats~~ | ~~Low~~ | ~~DISPROVEN Dec 2025: EndLevelData is runtime-only, never saved~~ |
| **Hypothesis testing** | Apply different decodings (alignment, float, ASCII) and display most plausible | Low | Medium |

---

*Historical investigation notes were trimmed from the public lore-book; keep this page focused on the current analyzer backlog and canonical RE docs.*
