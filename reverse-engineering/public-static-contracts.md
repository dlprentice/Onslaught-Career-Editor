# Public Static Contracts Overview

Status: public-safe overview
Last updated: 2026-06-22

The private maintainer database has complete static function-quality closure for
the loaded Steam retail `BEA.exe` and a completed post-100 current-risk static
re-audit. Public contributors should treat that as a static-contract foundation,
not as a runtime or rebuild-parity claim.

## Public Claim Boundary

Static contracts can support:

- naming, subsystem ownership, and source-to-binary reasoning
- patch planning against copied executables
- save/options and asset/tooling contracts
- clean-room rebuild planning

Static contracts do not prove:

- live gameplay behavior
- exact memory layouts in every runtime context
- patch behavior after mutation
- visual output
- online play
- rebuild parity
- no-noticeable-difference parity

## Contributor Rule

If implementation or runtime evidence contradicts a static claim, do not paper
over it in user-facing wording. File a focused issue or maintainer note with the
function/path, evidence, and non-claim boundary.
