# Retail save format

This directory documents the observed fixed 10,004-byte (`0x2714`) `.bes`
career format used by the supported retail/Steam specimen. AppCore starts from
a real baseline, preserves unknown bytes and file size, and writes only fields
selected by the user.

## Documents

| Document | Owner |
| --- | --- |
| [`save-format.md`](save-format.md) | Authoritative file layout and preservation rules |
| [`struct-layouts.md`](struct-layouts.md) | Career node, link, and Goodie structures |
| [`career-graph.md`](career-graph.md) | Campaign graph semantics |
| [`career-links.md`](career-links.md) | Link index and world mapping |
| [`career-unlock-recipes.md`](career-unlock-recipes.md) | Evidence-backed unlock edits |
| [`grade-system.md`](grade-system.md) | Ranking floats and grade calculation |
| [`goodies-system.md`](goodies-system.md) | Displayable Goodie slots and states |
| [`kill-tracking.md`](kill-tracking.md) | Lower-24-bit counters and metadata preservation |

## Quick layout

```text
0x0000  version word 0x4BD1 (uint16)
0x0002  CCareer fixed copy (0x24BC bytes)
0x0006  CCareerNode[100]
0x1906  CCareerNodeLink[200]
0x1F46  CGoodie[300]
0x23F6  five packed kill-counter dwords
0x240A  mSlots[32]
0x248A  career/options scalar fields
0x24BE  16 observed options entries (0x20 bytes each)
0x26BE  0x56-byte options tail
0x2714  end of supported file
```

Integers are little-endian dwords beginning at offsets where
`file_offset % 4 == 2`; floats are raw IEEE-754. Options entries and the tail are
applied by the retail boot path for `defaultoptions.bea`, but skipped by the
career-load path. Preserve them unless intentionally editing that format.

Static retail evidence is summarized in
[`../binary-analysis/save-options-static-review-2026-05-26.md`](../binary-analysis/save-options-static-review-2026-05-26.md).
Stuart's source informs structures and logic but is not the retail on-disk
authority.
