#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify and seal the 2026-08-14 HUD route demotion live promotion.

The verifier is read-only with one exception: ``seal`` creates the aggregate
JSON receipt.  It never launches Ghidra.  Every load-bearing fact is
re-measured from the retained ceremony artifacts and the current project
trees; a single mismatch fails closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LANE = REPO / "local-lab/ghidra-hud-route-demotion-20260814-v1"
LIVE = Path("C:/Users/david/Ghidra/Projects")
PRE_BACKUP = Path("D:/BEA-Ghidra-Backups/2026-08-14-hud-route-demotion-pre-live")
POST_BACKUP = Path("D:/BEA-Ghidra-Backups/2026-08-14-hud-route-demotion-post-live")
TRACKED = REPO / "reverse-engineering/ghidra"

SCHEMA = "bea.ghidra.hud-route-demotion-live-authority.v1"
TARGETS = {
    "0x00483530": ("CHud__RenderControllerSlotStatusPanel", "CHud__RoutePanel_T0_00483530"),
    "0x004858d0": (
        "CHud__RenderObjectiveProgressGaugeAndHeadingNeedle",
        "CHud__RoutePanel_T3_004858d0",
    ),
    "0x00485d50": ("CHud__RenderObjectiveStatusPanel", "CHud__RoutePanel_T4_00485d50"),
    "0x00486940": ("CHud__RenderObjectiveSlotFillPanel", "CHud__RoutePanel_T5_00486940"),
}
MUTATION = {
    "namesChanged": 4,
    "displayedSignaturesChanged": 4,
    "commentsChanged": 4,
    "tagSetsChanged": 4,
    "boundariesChanged": 0,
    "bytesChanged": 0,
    "instructionsChanged": 0,
    "dataUnitsChanged": 0,
    "referencesChanged": 0,
}
PROGRAM = {
    "name": "BEA.exe",
    "md5": "3b456964020070efe696d2cc09464a55",
    "sha256": "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
    "functions": 8329,
    "instructions": 551143,
}


class AuthorityError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuthorityError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path) -> dict:
    require(path.is_file(), f"artifact is absent: {path}")
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuthorityError(f"{path} is not valid UTF-8 JSON") from exc
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def project_files(root: Path) -> dict[str, str]:
    import ghidra_project_backup as backup

    manifest = backup.build_manifest(root, "BEA")
    return {row.relative_path: row.sha256 for row in manifest.files}


def check_receipts() -> dict:
    artifacts: dict[str, dict] = {}
    scratch = load_json(LANE / "scratch-authority.ready.json")
    require(
        scratch.get("schema") == "bea.ghidra.hud-route-demotion-scratch-authority.v1",
        "scratch authority schema differs",
    )
    artifacts["scratchAuthority"] = {
        "path": "local-lab/ghidra-hud-route-demotion-20260814-v1/scratch-authority.ready.json",
        **stamp(LANE / "scratch-authority.ready.json"),
    }
    require(scratch.get("mutation") == MUTATION, "scratch mutation summary differs")
    require(scratch.get("program") == PROGRAM, "scratch program identity differs")

    for phase, state in (("live-dry", "PRE"), ("live-apply", "POST"),
                         ("live-readback", "POST")):
        receipt = load_json(LANE / f"runs/{phase}/targets.ready.json")
        require(receipt.get("schema") == "bea.ghidra.hud-route-demotion.v1",
                f"{phase} receipt schema differs")
        require(receipt.get("mode") in phase and receipt.get("state") == state,
                f"{phase} mode/state differs")
        require(receipt.get("mutation") == MUTATION, f"{phase} mutation summary differs")
        require(receipt.get("program") == PROGRAM, f"{phase} program identity differs")
        require(receipt.get("targets") == 4, f"{phase} target census differs")
        require(receipt.get("commitRequested") == (phase == "live-apply"),
                f"{phase} commit flag differs")
        require(receipt.get("nestedEndReturnedCommitted") is False,
                f"{phase} nested-commit flag differs")
        require(receipt.get("loadedStateVerified") == (phase == "live-readback"),
                f"{phase} loaded-state flag differs")
        require(receipt.get("liveMutationAuthorized") is False,
                f"{phase} claim boundary differs")
        artifacts[phase] = {
            "path": f"local-lab/ghidra-hud-route-demotion-20260814-v1/runs/{phase}/targets.ready.json",
            **stamp(LANE / f"runs/{phase}/targets.ready.json"),
        }
        artifacts[f"{phase}-table"] = {
            "path": f"local-lab/ghidra-hud-route-demotion-20260814-v1/runs/{phase}/targets.tsv",
            **stamp(LANE / f"runs/{phase}/targets.tsv"),
        }
    return artifacts


def check_tables() -> None:
    def rows(name: str) -> dict[str, dict[str, str]]:
        table: dict[str, dict[str, str]] = {}
        for line in (LANE / f"runs/{name}/targets.tsv").read_text(
                encoding="utf-8").splitlines()[1:]:
            cells = line.split("\t")
            table[cells[0]] = {
                "mode": cells[1], "state": cells[2], "name": cells[3],
            }
        require(len(table) == 4, f"{name} row count differs")
        return table

    dry = rows("live-dry")
    apply_rows = rows("live-apply")
    readback = rows("live-readback")
    for address, (pre_name, post_name) in TARGETS.items():
        require(dry[address]["state"] == "PRE" and dry[address]["name"] == pre_name,
                f"{address} dry PRE row differs")
        for table in (apply_rows, readback):
            require(table[address]["state"] == "POST"
                    and table[address]["name"] == post_name,
                    f"{address} POST row differs")
    replica_apply = (LANE / "runs/replica-a-apply/targets.tsv").read_bytes()
    require(replica_apply == (LANE / "runs/live-apply/targets.tsv").read_bytes(),
            "live apply table differs from scratch replica")
    require((LANE / "runs/replica-a-readback/targets.tsv").read_bytes()
            == (LANE / "runs/live-readback/targets.tsv").read_bytes(),
            "live readback table differs from scratch replica")


def check_inventory() -> dict:
    diff = load_json(LANE / "runs/live-readback/inventory-diff.json")
    counts = diff["counts"]
    require(counts["created"] == 0 and counts["destroyed"] == 0,
            "function census moved")
    require(counts["boundsChanged"] == 0, "function bounds moved")
    require(counts["namesChanged"] == 4 and counts["signaturesChanged"] == 4,
            "live delta differs from four-name demotion")
    dangerous = diff["dangerous"]
    require(dangerous["gradedDestroyedCount"] == 0
            and dangerous["gradedDemotedCount"] == 0
            and dangerous["gradedBoundsMovedCount"] == 0,
            "dangerous collateral reported")
    renamed = {row["address"].lower(): row for row in dangerous["gradedFunctionsRenamed"]}
    require(set(renamed) == set(TARGETS), "renamed target set differs")
    for address, (pre_name, post_name) in TARGETS.items():
        require(renamed[address]["before"] == pre_name
                and renamed[address]["after"] == post_name,
                f"{address} rename transition differs")

    pre_program = {}
    for line in (LANE / "pre-readback/program.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        key, value = line.split("\t", 1)
        pre_program[key] = value
    post_program = {}
    for line in (LANE / "runs/live-readback/program.tsv").read_text(
            encoding="utf-8").splitlines()[1:]:
        key, value = line.split("\t", 1)
        post_program[key] = value
    changed = {key for key in pre_program if pre_program[key] != post_program[key]}
    require(changed == {"commentsSha256"}, f"program changed metrics differ: {sorted(changed)}")
    for key in ("functions", "instructions", "memorySha256", "references",
                "definedData", "symbolsUserDefined", "comments"):
        require(pre_program[key] == post_program[key], f"program metric {key} moved")
    return {
        "changedMetrics": ["commentsSha256"],
        "namesChanged": 4,
        "nonTargetsByteIdentical": counts["before"] - 4,
    }


def check_project_trees() -> dict:
    live = project_files(LIVE)
    tracked = project_files(TRACKED)
    post = load_json(POST_BACKUP / "backup_manifest.json")["destination"]["files"]
    post_map = {row["relative_path"]: row["sha256"] for row in post}
    require(len(live) == len(tracked) == len(post_map) == 19,
            "project file census differs")
    require(live == tracked, "live and tracked project trees differ")
    require(live == post_map, "live and POST backup project trees differ")
    pre = load_json(PRE_BACKUP / "backup_manifest.json")["destination"]["files"]
    pre_map = {row["relative_path"]: row["sha256"] for row in pre}
    changed = {key for key in live
               if key in pre_map and live[key] != pre_map[key]}
    removed = sorted(set(pre_map) - set(live))
    added = sorted(set(live) - set(pre_map))
    require(removed == ["BEA.rep/idata/00/~00000000.db/db.18617.gbf"],
            f"unexpected removed files: {removed}")
    require(added == ["BEA.rep/idata/00/~00000000.db/db.18619.gbf"],
            f"unexpected added files: {added}")
    require(len(changed) == 0,
            f"unexpected in-place file changes: {sorted(changed)}")
    return {
        "fileCount": 19,
        "liveTrackedPostByteIdentical": True,
        "dbAdvanced": "db.18618 -> db.18619 (one checkpoint pair swap)",
        "db18619Sha256": live["BEA.rep/idata/00/~00000000.db/db.18619.gbf"],
    }


def check_projection() -> dict:
    projection = LANE / "ghidra-function-name-table-2026-08-14.tsv"
    text = projection.read_text(encoding="utf-8")
    by_address: dict[str, str] = {}
    for line in text.splitlines():
        cells = line.split("\t")
        if len(cells) < 2 or cells[0] == "address":
            continue
        by_address[cells[0].lower()] = cells[1]
    require(len(by_address) == 8329, "projection row census differs")
    for address, (_, post_name) in TARGETS.items():
        require(by_address.get(address) == post_name,
                f"projection row {address} differs")
    for _, (pre_name, _) in TARGETS.items():
        require(pre_name not in by_address.values(), f"stale name survives: {pre_name}")
    return {"path": "local-lab/ghidra-hud-route-demotion-20260814-v1/"
            "ghidra-function-name-table-2026-08-14.tsv",
            **stamp(projection)}


def check_restore_probes() -> dict:
    pre_probe = load_json(LANE / "pre-backup-restore.ready.json")
    post_probe = load_json(LANE / "post-backup-restore.ready.json")
    tracked_probe = load_json(LANE / "tracked-snapshot-restore.ready.json")
    result = {}
    for label, value in (("pre", pre_probe), ("post", post_probe),
                         ("tracked", tracked_probe)):
        opened = value.get("readonlyOpen") or {}
        require(opened.get("opened") is True and opened.get("exitCode") == 0
                and value.get("sourceStable") is not False
                and (opened.get("postOpenComparison") or {}).get("matches") is True,
                f"{label} restore probe did not pass")
        result[label] = {
            "path": f"local-lab/ghidra-hud-route-demotion-20260814-v1/"
                    f"{label}-backup-restore.ready.json"
            if label != "tracked"
            else "local-lab/ghidra-hud-route-demotion-20260814-v1/"
                 "tracked-snapshot-restore.ready.json",
            **stamp(LANE / f"{label}-backup-restore.ready.json"
                    if label != "tracked"
                    else LANE / "tracked-snapshot-restore.ready.json"),
        }
    return result


def git_head() -> str:
    output = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True,
        check=True,
    )
    return output.stdout.strip()


def verify() -> dict:
    artifacts = check_receipts()
    check_tables()
    inventory = check_inventory()
    trees = check_project_trees()
    projection = check_projection()
    probes = check_restore_probes()
    return {
        "schema": SCHEMA,
        "verifiedAtUtc": datetime.now(timezone.utc).isoformat(),
        "gitHead": git_head(),
        "targets": {address: {"preName": pre, "postName": post}
                    for address, (pre, post) in TARGETS.items()},
        "program": PROGRAM,
        "mutation": MUTATION,
        "artifacts": artifacts,
        "inventory": inventory,
        "projectTrees": trees,
        "projection": projection,
        "restoreProbes": probes,
        "claimBoundary": [
            "Metadata-only live promotion: four descriptive names demoted to neutral",
            "Tier-3 placeholders with measured-fact comments and corrected tag sets.",
            "No original C++ symbol was recovered; no boundary, instruction, program byte,",
            "data unit, reference, ABI field, or non-target function row changed.",
            "No runtime behavior, source identity, campaign generation, or rebuild",
            "parity is claimed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("verify", "seal"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(REPO / "tools"))
    receipt = verify()
    output = Path(args.output)
    if args.mode == "seal":
        require(not output.exists(), f"refusing to overwrite: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(f"SEALED {output} bytes={output.stat().st_size} "
              f"sha256={sha256_file(output)}")
    else:
        existing = load_json(output)
        require(existing.get("schema") == SCHEMA, "existing receipt schema differs")
        for key in ("targets", "program", "mutation", "inventory", "projectTrees"):
            require(existing.get(key) == receipt.get(key),
                    f"sealed receipt disagrees with current state: {key}")
        print(f"VERIFIED {output}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AuthorityError as error:
        print(f"AUTHORITY_FAIL {error}", file=sys.stderr)
        sys.exit(1)
