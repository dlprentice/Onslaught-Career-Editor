#!/usr/bin/env python3
"""Print rebuild-grade scalar contract status for campaign resumes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MECH = ROOT / "reverse-engineering" / "game-mechanics"

ROWS = (
    ("walker-forward", "walker-forward-scalar-response-v2.json", "dual-accepted"),
    ("jet-forward", "jet-forward-scalar-response-v1.json", "dual-accepted"),
    ("walker-turn-yaw", "walker-turn-yaw-scalar-response-v1.json", "dual-accepted"),
    ("walker-strafe", "walker-strafe-lateral-scalar-response-v1.json", "dual-accepted"),
    ("transform-morph", "walker-transform-morph-timing-v1.json", "dual-accepted"),
    ("energy-rate", "jet-energy-drain-scalar-response-v1.json", "dual-accepted"),
    ("shield-rate", None, "scaffold+offset; live pending"),
    ("fire-cooldown", None, "scaffold; live pending"),
    ("projectile-speed", None, "scaffold; live pending"),
    ("coast-friction", None, "scaffold; live pending"),
    ("camera-look", None, "scaffold; live pending"),
)


def main() -> int:
    out: list[dict[str, object]] = []
    for name, contract, status in ROWS:
        row: dict[str, object] = {"name": name, "status": status}
        if contract:
            path = MECH / contract
            row["contract"] = contract
            row["present"] = path.is_file()
            if path.is_file():
                data = json.loads(path.read_text(encoding="utf-8"))
                row["schemaVersion"] = data.get("schemaVersion")
        out.append(row)
    try:
        import battleengine_measure_mode_catalog as modes

        offline = modes.offline_harness_dicts()
    except Exception:
        offline = []
    json.dump({"scalars": out, "offlineHarnesses": offline}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    missing = [r for r in out if r.get("present") is False]
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
