# Shared Test Fixtures

- `gold_career_save.bin` is the public-safe immutable baseline used by C# and Python regression tests.
- It is copied from a real game-generated 10,004-byte save so tests can validate retail save semantics without depending on the private `save-attempts/` tree.
- Treat this fixture as read-only. Tests should copy it to temporary `.bes` or `.bea` paths before writing.
