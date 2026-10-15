# Public Save And Options Overview

Status: public-safe overview
Last updated: 2026-06-22

Battle Engine Aquila `.bes` saves and `defaultoptions.bea` files are fixed-size
binary buffers. Public code changes must preserve unknown bytes and operate on
copies.

## Rules

- Do not synthesize `.bes` files from scratch.
- Start from a real baseline save/options file.
- Preserve file size, padding, reserved bytes, and unknown regions unless the
  task is explicitly investigating those bytes.
- Use true-view offsets from the quick reference, not shifted aligned-view
  guesses.
- Keep public PRs free of real saves and private game data.

## Useful References

- [Save Structs](quick-reference/save-structs.md)
- [Save Ranks](quick-reference/save-ranks.md)
- [Save Goodies](quick-reference/save-goodies.md)
- [Save Kills](quick-reference/save-kills.md)
