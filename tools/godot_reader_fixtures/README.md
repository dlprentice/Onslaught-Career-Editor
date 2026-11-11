# C# reader fixtures

Status: active — reference copies that two tool tests read, not built or run here
Last updated: 2026-11-11 (created when the frozen rebuild copy was cut from this repository)
Summary: five C# source files from onslaught-godot, kept so that `tools/particle_set_walk_tests.py` and
`tools/physics_values_decode_tests.py` can still check their tables against the readers those tables were taken from.

The files are byte-identical to the copies the frozen `rebuild/` folder held, which in turn are byte-identical to the
files at onslaught-godot commit `403cf01051030f2f26f6acb3c12a401bc642f16e` (2026-10-21). That equality was checked by
Git blob identity: each file here has the same blob hash as `rebuild/OnslaughtRebuild.Parity/...` had, and the same
blob appears at that commit in <https://github.com/dlprentice/onslaught-godot>. onslaught-godot has since changed one
comment line in each file, so its current files differ from these by that line only.

| File here | Path in onslaught-godot |
| --- | --- |
| `TokenArchive.cs` | `rebuild/OnslaughtRebuild.Parity/Particles/TokenArchive.cs` |
| `ParticleDescriptors.cs` | `rebuild/OnslaughtRebuild.Parity/Particles/ParticleDescriptors.cs` |
| `ParticleSet.cs` | `rebuild/OnslaughtRebuild.Parity/Particles/ParticleSet.cs` |
| `PhysicsRegistry.cs` | `rebuild/OnslaughtRebuild.Parity/Physics/PhysicsRegistry.cs` |
| `PhysicsRegistry.Families.cs` | `rebuild/OnslaughtRebuild.Parity/Physics/PhysicsRegistry.Families.cs` |

Each file keeps its own `SPDX-License-Identifier: GPL-3.0-only` line, and the credit and provenance for the code they
adapt is recorded per unit in onslaught-godot's `rebuild/PROVENANCE.md`. Nothing here is compiled: the tests read the
files as text and compare the token names, value identifiers and read sequences with the Python tables in
`tools/particle_set_walk.py` and `tools/physics_values_decode.py`.

To refresh a fixture, copy the file from a newer onslaught-godot commit, name that commit above, and run
`python tools/particle_set_walk_tests.py` and `python tools/physics_values_decode_tests.py`. A table that no longer
matches fails the test; it is not skipped.
