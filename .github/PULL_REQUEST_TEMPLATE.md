# Summary

What changed, why, and which modder, preservation or contributor problem it solves.

## Scope

Areas affected:

- [ ] Content Catalogue / Content Inventory
- [ ] Format decoders / World / MSL / Mod tools
- [ ] Lore and documentation

Changes to Onslaught CE belong in [onslaught-ce](https://github.com/dlprentice/onslaught-ce); decompilation work belongs in [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp); game documentation belongs in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation); Godot rebuild work belongs in [onslaught-godot](https://github.com/dlprentice/onslaught-godot).

Main paths changed:

Out of scope:

## Validation

Validation run (exact local commands and results):

Validation intentionally skipped (relevant commands and reason):

## Safety And Claims

- [ ] I license this contribution under the same terms as the paths it changes
      (inbound = outbound, `CONTRIBUTING.md`): code/schemas GPL-3.0-only, docs/tables/lore CC BY-SA 4.0.
- [ ] No proprietary game assets, executables, generated retail catalogues/inventories, arbitrary saves,
      raw debugger logs, secrets, unredacted private paths or machine identifiers were added.
- [ ] Tools treat retail installations as read-only and write outputs only outside the game tree via
      `tools/safe_generated_output.py` (or stdout).
- [ ] Any new `*_tests.py` suite is registered in `tools/run_tool_tests.py`.
- [ ] No hosted CI/release automation was added.

## State And Risks

Documentation state update (for example `CURRENT_CAPABILITIES.md`, `tools/README.md`, `PROJECT-INDEX.md`, or `none`):

Remaining risks or follow-ups:
