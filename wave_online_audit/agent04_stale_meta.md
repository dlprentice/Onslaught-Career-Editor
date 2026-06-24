# Stale Ghidra/GhydraMCP Metadata Audit (Excluding reverse-engineering/binary-analysis/**)

Scope: Markdown files in repo, excluding `reverse-engineering/binary-analysis/**` as requested. Focused on stale Ghidra/GhydraMCP version strings, localhost vs gateway rules, and hotspot-banned signature/create assertions.

## Findings (Actionable)

### 1) Stale version string
- `lore-book/reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:954`
  - **Issue:** Footer says `Tools: Ghidra 11.x + GhydraMCP (port 8193)`.
  - **Why stale:** Current repo-wide references are Ghidra `12.0.3` and GhydraMCP `v2.2.0-rc.2`.
  - **Recommended fix:** Update the footer to match current workstation versions (e.g., `Ghidra 12.0.3 + GhydraMCP v2.2.0-rc.2`), or make it date-stamped and version-agnostic (e.g., `Tools: Ghidra 12.x + GhydraMCP (port 8193)`, with a date).

## No Issues Found

### Localhost vs gateway rules
- No stale guidance found outside the excluded directory. Existing localhost examples are either negative examples (`MCP_LIMITATIONS.md`, `AGENTS.md`) or apply to non-Ghidra MCP servers (`MCP_DEBUGGING_OPTIONS.md`).

### Hotspot-banned signature/create assertions
- No docs outside the excluded directory assert MCP signature/creation operations on hotspot-banned addresses (e.g., `0x0042b500`, `0x0042b800`, `0x00419d40..`, `0x0051c090..`). The active hotspot guidance already lives in `AGENTS.md` and `MCP_LIMITATIONS.md`.
