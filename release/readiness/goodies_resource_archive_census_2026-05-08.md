# Goodies Resource Archive Census - 2026-05-08

## Scope

This pass added a public-safe probe that reads the user's local PC install as read-only source material, inflates every shipped `goodie_*_res_PC.aya` resource archive, and parses only high-level `GDIE -> GDAT` metadata.

Raw generated JSON remains ignored/private under:

```text
subagents/goodies-resource-archive-census/current/goodies-resource-archive-census.json
```

## Command

```powershell
npm run test:goodies-resource-archive-census
```

Result: PASS

Important output:

```text
PASS: wrote subagents/goodies-resource-archive-census/current/goodies-resource-archive-census.json
Goodie archives parsed: 232 / 233 displayable slots
Missing displayable archive slots: [232]
GDAT content-kind counts: 0=149, 1=45, 2=33, 3=5
```

## Public-Safe Summary

The probe strips absolute paths and raw asset names. It records only archive indices, top-level chunk tags, `GDIE` / `GDAT` sizes, and the first two `GDAT` dwords: embedded Goodie index and static content-kind discriminator.

Expected conditions:

| Check | Result |
| --- | --- |
| Goodie archives parsed | 232 |
| Displayable Goodie slots | 233 |
| Missing displayable archive slots | 232 only |
| Parse errors | 0 |
| Archive index / embedded `GDAT` index mismatches | 0 |
| Required top-level tags present | yes: `LVLR`, `TARG`, `AYAD`, `GDIE` |
| Unknown `GDAT` content-kind values | 0 |

Static `GDAT` content-kind counts:

| Kind byte | Interpreted content family | Count |
| ---: | --- | ---: |
| 0 | Texture/artwork | 149 |
| 1 | Model/gallery | 45 |
| 2 | Video/cutscene | 33 |
| 3 | Level/metadata | 5 |

## What This Proves

- The Goodies archive corpus is present in the installed PC game resources, not only in source-tree samples.
- The shipped archive count is 232 for 233 displayable Goodie slots; displayable slot 232 has no matching `goodie_232_res_PC.aya` archive in this install.
- Every parsed archive contains the expected high-level resource wrapper tags and a `GDIE -> GDAT` metadata row.
- The embedded `GDAT` Goodie index matches the archive index for every parsed archive.
- The low-level static content-kind counts independently line up with the current generated catalog families: artwork, model/gallery, video/cutscene, and level/metadata.
- The 33 archive-backed video/cutscene rows are expected to differ from the generated catalog's 34 video Goodies because catalog row 232 is a synthetic handoff to cutscene 33 with no matching `goodie_232_res_PC.aya` archive.

## What This Does Not Prove

- It does not extract assets.
- It does not launch or inspect the running game.
- It does not prove runtime Goodies wall reachability, unlock behavior, animation, or model-viewer behavior.
- It does not prove final textured/animated WinUI model viewing.
- It does not permit committing raw archives, extracted assets, raw catalog content, screenshots, frames, or private proof JSON.

## Follow-Up

Use this census as the lowest-level provenance guard for future Goodies work. The next runtime question remains copied-profile Goodies wall reachability and runtime model-viewer behavior, especially around hidden shipped artwork rows and the missing archive for displayable slot 232.
