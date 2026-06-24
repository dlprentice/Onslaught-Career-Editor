# Shared Private Test Fixtures

- `gold_career_save.bin` is the private maintainer-tree immutable baseline used by C# and Python regression tests.
- It is copied from a real game-generated 10,004-byte save so tests can validate retail save semantics without depending on the private `save-attempts/` tree.
- Public candidates exclude this save-shaped binary payload. Fixture-dependent public test runs should skip those cases until a licensed/generated replacement fixture exists.
- Treat this fixture as read-only. Tests should copy it to temporary `.bes` or `.bea` paths before writing.
