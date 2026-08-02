#!/usr/bin/env python3
"""Locate the gitignored `local-lab/` tree and import the proven readers from it.

This project deliberately keeps retail-derived material and the measurement
tooling that reads it outside version control, so a fresh clone has none of it.
The probe authoring tool therefore does not vendor a copy of the container codec
or the bytecode grammar -- it *imports* them, so there is exactly one definition
of each and no chance of a silently divergent second parser.

Imported from `local-lab/`:
    aya_roundtrip        container codec (inflate/deflate), already proven to
                         round-trip by PROBE-CONTAINER-EXPERIMENT-2026-08-02
    msl/script_parse     the compiled-MissionScript grammar, written to the VM's
                         own readers and shown capable of failing by
                         msl/mutation_test.py (10 mutations x 7 levels, 0 survivors)
    msl/bea_aya          independent chunk walker

Resolution order for the lab root:
    1. the `lab` argument
    2. $BEA_LOCAL_LAB
    3. <repo root>/local-lab            (repo root = two levels above tools/probe)
    4. any ancestor directory containing a `local-lab/`
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_CACHE: dict[str, object] = {}


class LabNotFound(RuntimeError):
    pass


def find_lab(lab: str | os.PathLike | None = None) -> Path:
    """Return the local-lab root, or raise LabNotFound with actionable text."""
    tried: list[str] = []

    def ok(p: Path) -> bool:
        return (p / "aya_roundtrip.py").is_file() and (p / "msl" / "script_parse.py").is_file()

    candidates: list[Path] = []
    if lab:
        candidates.append(Path(lab))
    env = os.environ.get("BEA_LOCAL_LAB")
    if env:
        candidates.append(Path(env))
    here = Path(__file__).resolve()
    for anc in [here.parents[2]] + list(here.parents):
        candidates.append(anc / "local-lab")

    seen = set()
    for c in candidates:
        c = Path(c).expanduser()
        try:
            c = c.resolve()
        except OSError:
            continue
        if c in seen:
            continue
        seen.add(c)
        tried.append(str(c))
        if ok(c):
            return c

    raise LabNotFound(
        "could not locate local-lab (needs aya_roundtrip.py and msl/script_parse.py).\n"
        "Set BEA_LOCAL_LAB to the lab root. Tried:\n  " + "\n  ".join(tried)
    )


def load(lab: str | os.PathLike | None = None):
    """Import and return (lab_root, aya_roundtrip, script_parse, bea_aya)."""
    root = find_lab(lab)
    key = str(root)
    if key in _CACHE:
        return _CACHE[key]  # type: ignore[return-value]

    for p in (str(root), str(root / "msl")):
        if p not in sys.path:
            sys.path.insert(0, p)

    import aya_roundtrip  # noqa: E402
    import script_parse  # noqa: E402
    import bea_aya  # noqa: E402

    got = (root, aya_roundtrip, script_parse, bea_aya)
    _CACHE[key] = got
    return got
