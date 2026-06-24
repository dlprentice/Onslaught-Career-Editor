# Advanced Features

## Save File Validation/Integrity Checking

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **`--validate`** | Check save file for common corruption patterns | High | Medium |
| **Node consistency** | Check mLowerLink/mHigherLink point to valid nodes | Medium | Medium |
| **Link consistency** | Check mToNode values are valid | Medium | Low |
| **Goodie state check** | Flag unknown upper-word values (not 0/1/2/3) | Medium | Low |
| **Kill count sanity** | Flag unrealistic values (>65535 would overflow) | Low | Low |
| **Repair mode** | `--repair` to fix common issues automatically | Low | High |

Note: Version stamp check and size validation already done in `analyze_file()`.

**Validation error levels:**
```
FATAL:   Save will not load (size, version)
ERROR:   Save may crash specific levels (bad links, corrupt nodes)
WARNING: Unusual values that may indicate corruption
INFO:    Observations about save state
```

## Automatic Backup Before Patching

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **`--backup`** | Create timestamped backup before patching | High | Low |
| **Auto-backup** | Always backup unless `--no-backup` specified | Medium | Low |
| **Backup location** | `~/.onslaught-backups/` with rotation | Low | Medium |
| **Backup limit** | Keep last N backups, auto-cleanup old | Low | Medium |
| **Restore command** | `--restore BACKUP` to roll back | Medium | Low |

**Backup naming:** `{original_name}_{timestamp}.bes`

## Diff Tool for Comparing Saves

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **Unified diff format** | Standard diff output for version control | Medium | Medium |
| **Interactive diff** | Side-by-side with navigation (curses TUI) | Low | High |
| **Diff profiles** | Only show nodes/links/goodies/kills as needed | Medium | Low |
| **Diff export** | `--diff-export diff.json` for external tools | Low | Low |
| **Historical diff** | Compare against known-good reference saves | Medium | Medium |

## Import/Export Profiles

| Feature | Description | Priority | Effort |
|---------|-------------|----------|--------|
| **Profile export** | `--export-profile profile.json` with current patch settings | Medium | Medium |
| **Profile import** | `--import-profile profile.json` to apply settings | Medium | Low |
| **Preset library** | Built-in profiles: "all-s-rank", "speedrun-ready", "unlock-all" | Low | Low |
| **Share format** | Human-readable JSON/YAML for community sharing | Medium | Low |

**Profile schema:**
```json
{
  "name": "All S-Rank",
  "version": 1,
  "patches": {
    "default_rank": "S",
    "level_ranks": {},
    "kill_counts": {"aircraft": 100, "vehicles": 400},
    "goodies": "OLD",
    "patch_nodes": true,
    "patch_links": true,
    "patch_goodies": true,
    "patch_kills": true
  }
}
```

## Other Ideas

- **Batch processing**: Patch multiple .bes files with same settings
- **Undo support**: Store original bytes that were modified, allow rollback
- **Level name lookup**: Accept `--level-rank "Blackout:S"` instead of numbers
- **Episode presets**: `--episode-rank 2:A` to set all Episode 2 missions

---

*See [status-current.md](status-current.md) for currently implemented features*
