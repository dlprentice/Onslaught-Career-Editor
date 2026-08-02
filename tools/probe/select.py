#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Choose the next probe from the coverage ledger instead of from a hunch.

WHY THIS EXISTS
---------------
Probe selection was the last manual step in the discovery loop. A human read a
dark-region table, formed an opinion about what might reach it, and wrote a
manifest. That is fine for three probes and hopeless for a hundred, and it is
where a campaign quietly stops being driven by measurement.

This stage reads a `tools/re_coverage_ledger.py` snapshot and produces a ranked
worklist: which dark region is worth the most, what lever might reach it, what
that lever costs, and -- the part that makes it falsifiable -- what result would
prove the lever does not work.

WHAT THE FIRST READING CHANGED
------------------------------
The campaign was planned on the premise that `.text` is dark because the opening
minutes never exercise combat, AI, damage and destruction. Against the
2026-08-02 base snapshot (69 coverage indexes, 66 levels) that premise does not
survive its own numbers:

    RENDER          321,340 dark bytes   52.0% of never-entered dark
    UNCLASSIFIED     73,269               11.8%
    EH_ERROR_PATH    47,579                7.7%
    COMBAT_AI        35,060                5.7%
    CRT_EH_FUNCLET   19,820                3.2%

Combat is a twentieth of the never-entered mass. Two render families alone --
`CFastVB` at 88.5% dark and `CDXTexture` at 80.5% -- are 183,579 bytes, five
times all of COMBAT_AI. And they stayed dark across all 66 shipped levels, which
means shipped content does not reach them: the lever is content the game
supports and the game's own assets never use, not more gameplay.

A LEVER IS A HYPOTHESIS, NOT A FACT
-----------------------------------
Every entry in the catalogue below carries a confidence and a falsifier. That
the engine negotiates render methods at startup is OBSERVED, in
`setuphistory.txt`. That `CFastVB` branches on the negotiated method is NOT
observed -- it is the reason to run the probe. A selector that stated levers as
facts would be handing the campaign a list of conclusions to confirm, which is
the failure this whole loop was built to prevent.

THE COST SPLIT IS LOAD-BEARING
------------------------------
Coverage is measured from TTD execution indexes, and TTD recording needs an
elevated window this agent must never raise on its own. So a probe that can be
JUDGED BY COVERAGE needs the maintainer, while a probe judged by its own
artefacts -- a console-written file, a survival, a fault -- does not. The
worklist separates them, because a campaign that cannot tell the two apart
either idles waiting for a human or reports behavioural results as coverage.

Usage
-----
    py -3 tools/probe/select.py --snapshot local-lab/re-ledger/<snap>
    py -3 tools/probe/select.py --snapshot DIR --top 20 --no-ttd
    py -3 tools/probe/select.py --snapshot DIR --json-out worklist.json
    py -3 tools/probe/select.py --self-check
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import pathlib
import sys
from typing import Any, Optional, Sequence


ROOT = pathlib.Path(__file__).resolve().parents[2]


@dataclasses.dataclass(frozen=True)
class Lever:
    """One way of reaching code that has never executed.

    ``confidence`` is about REACHABILITY, not about any claim the probe would
    then support:

        OBSERVED   this lever has already been seen to change what executes.
        PLAUSIBLE  the mechanism is observed; that it reaches THIS family is not.
        SPECULATIVE the mechanism itself is inferred.
        NONE       no lever is known. Saying so is the useful output.
    """

    id: str
    reach_classes: tuple[str, ...]
    families: tuple[str, ...]
    mechanism: str
    evidence: str
    falsifier: str
    confidence: str
    needs_ttd: bool
    needs_elevation: bool
    note: str = ""


# The catalogue. Ordered most specific first; the first match wins.
LEVERS: tuple[Lever, ...] = (
    Lever(
        id="unreachable-by-probing",
        reach_classes=("CRT_EH_FUNCLET", "EH_ERROR_PATH"),
        families=("(eh-funclet)",),
        mechanism=(
            "C++ exception unwind funclets and allocation/IO error paths. These "
            "run when something throws or a syscall fails, not when the player "
            "does anything."
        ),
        evidence=(
            "ledger-families.tsv: (eh-funclet) is 1,179 functions and 19,019 "
            "bytes at 100.0% dark across all 69 indexes; the single largest "
            "dark region, 0x005be628 (46,657 bytes), is HResultToString"
        ),
        falsifier=(
            "if any content probe lights up eh-funclet bytes, this "
            "classification is wrong and these should be ranked normally"
        ),
        confidence="OBSERVED",
        needs_ttd=True,
        needs_elevation=True,
        note=(
            "67,399 dark bytes -- 10.9% of never-entered mass -- that no "
            "gameplay probe will ever reach. Counting it in a reachable target "
            "makes the ceiling look further away than it is."
        ),
    ),
    Lever(
        id="render-method-sweep",
        reach_classes=("RENDER",),
        families=("CStaticShadows", "CDXMeshVB", "CPolyBucket"),
        mechanism=(
            "The engine negotiates render methods at startup and caches the "
            "accepted set. Forcing a different accepted method selects a "
            "different implementation in the same family."
        ),
        evidence=(
            "local-lab/safe-copy-bea-pristine/setuphistory.txt logs "
            "'RM: First-time attempt at sun_method:1 starting' then "
            "'RM: Accepting sun_method:1', and likewise water_method:2, "
            "self_illumination_method:1, battleline_method:2, shadow_method:3"
        ),
        falsifier=(
            "run the same level under two different accepted method sets and "
            "diff the coverage indexes: if the dark bytes in these families do "
            "not move, the families do not branch on the negotiated method"
        ),
        confidence="PLAUSIBLE",
        needs_ttd=True,
        needs_elevation=True,
    ),
    Lever(
        id="authored-asset-format",
        reach_classes=("RENDER",),
        families=("CDXTexture", "CTexture", "CFastVB", "CMesh", "CMeshPart"),
        mechanism=(
            "Decode and pack paths for formats the engine supports and the "
            "shipped assets never use. The probe authors an archive containing "
            "such an asset and loads it."
        ),
        evidence=(
            "these families stayed dark across all 66 shipped levels, so "
            "shipped content does not reach them; the dark symbols name the "
            "formats outright -- CDXTexture__DecodePngPassRowsAndPostprocess, "
            "CDXTexture__InflateStream_ProcessZlibState, "
            "CFastVB__PackTexels_Dither_Bits16_16_16_16"
        ),
        falsifier=(
            "author an asset in the named format, load it, and diff coverage: "
            "no movement means the engine does not take that path at load time "
            "(or rejects the asset before reaching it, which the receipt's "
            "level-load line distinguishes)"
        ),
        confidence="PLAUSIBLE",
        needs_ttd=True,
        needs_elevation=True,
        note=(
            "the largest addressable prize on the board: CFastVB 97,295 dark "
            "bytes at 88.5%, CDXTexture 86,284 at 80.5%"
        ),
    ),
    Lever(
        id="script-native-scenario",
        reach_classes=("COMBAT_AI", "WORLD_SIM", "SCRIPT_VM"),
        families=(),
        mechanism=(
            "An authored MissionScript spliced into a level archive, driving "
            "the 144 script natives -- SpawnThing, damage, destruction -- into "
            "a scenario the shipped scripts never set up."
        ),
        evidence=(
            "tools/probe/probe_author.py authors content-anchored splices and "
            "the loop proved one end to end at 9b445b93; a script object has no "
            "size or offset field, so splicing is concatenation plus a "
            "scriptCount bump"
        ),
        falsifier=(
            "the spliced script's own Echo/MemStats side effect does not appear "
            "in the scratch tree, which means the VM never ran it"
        ),
        confidence="PLAUSIBLE",
        needs_ttd=True,
        needs_elevation=True,
        note=(
            "35,060 dark COMBAT_AI bytes: real, and a twentieth of what the "
            "render lane is worth. Worth doing, not worth doing first."
        ),
    ),
    Lever(
        id="console-command",
        reach_classes=("CONSOLE", "EDITOR_DEBUG"),
        families=(),
        mechanism=(
            "A console command placed in autoexec.con, which the level-load "
            "path reads and executes."
        ),
        evidence=(
            "measured 2026-08-02: four console commands executed from "
            "autoexec.con when launched with -level; three earlier arms "
            "launched without -level, sat in the frontend, and never read the "
            "file at all"
        ),
        falsifier=(
            "the command's artefact does not appear in the scratch tree while "
            "setuphistory.txt does log the level load"
        ),
        confidence="OBSERVED",
        needs_ttd=False,
        needs_elevation=False,
        note=(
            "the only lever that needs no elevation, which is why it is the "
            "one that runs unattended -- but it is judged by artefacts, not by "
            "coverage."
        ),
    ),
    Lever(
        id="frontend-navigation",
        reach_classes=("FRONTEND", "MULTIPLAYER", "INPUT"),
        families=("CFEPMultiplayerStart",),
        mechanism=(
            "Frontend screens the coverage campaign never opened, reached by "
            "driving the menus."
        ),
        evidence=(
            "the 69 indexes are level-load and in-level captures plus three "
            "frontend/startup/options traces; CFEPMultiplayerStart is 72.2% "
            "dark, which is a screen nobody navigated to"
        ),
        falsifier=(
            "open the screen under capture and diff: no movement means the "
            "screen's code is not in this family"
        ),
        confidence="PLAUSIBLE",
        needs_ttd=True,
        needs_elevation=True,
        note="needs synthetic input, so it needs the machine to be unattended.",
    ),
)

NO_LEVER = Lever(
    id="no-known-lever",
    reach_classes=(),
    families=(),
    mechanism="Nothing in the catalogue is known to reach this code.",
    evidence="",
    falsifier=(
        "not applicable: there is no probe to falsify. This entry is a request "
        "for a new instrument, not a candidate."
    ),
    confidence="NONE",
    needs_ttd=True,
    needs_elevation=True,
)


def choose_lever(region: dict[str, str]) -> Lever:
    """First match wins: family before reach class, catalogue order otherwise."""

    families = region.get("topFamilies", "")
    reach = region.get("topReachClass", "")
    for lever in LEVERS:
        if lever.families and any(f"{name}(" in families for name in lever.families):
            return lever
    for lever in LEVERS:
        if reach in lever.reach_classes:
            return lever
    return NO_LEVER


def score_region(region: dict[str, str]) -> dict[str, Any]:
    """Rank by dark bytes, weighted by how cheap the region is to identify.

    ``inCallersObserved`` is the ledger's adjacency signal: the count of
    distinct OBSERVED bodies that call into this region. A dark body called
    from code we have already watched execute is far cheaper to identify than
    an island, because the call site tells you what it is for.

    The weight is deliberately mild -- x1.0 to x2.0 -- rather than a ranking by
    adjacency alone. Adjacency makes a region cheap to UNDERSTAND; it does not
    make it likely a probe REACHES it, and those are different questions that a
    single aggressive score would silently merge.
    """

    dark = int(region["darkBytes"])
    in_observed = int(region["inCallersObserved"])
    in_total = max(int(region["inCallersTotal"]), 1)
    adjacency = in_observed / in_total
    lever = choose_lever(region)
    reachable = lever.id != "unreachable-by-probing" and lever.confidence != "NONE"
    return {
        "startVa": region["startVa"],
        "endVa": region["endVa"],
        "darkBytes": dark,
        "funcCount": int(region["funcCount"]),
        "namedCount": int(region["namedCount"]),
        "reachClass": region["topReachClass"],
        "families": region["topFamilies"],
        "largestFunc": region["largestFunc"],
        "largestFuncBytes": int(region["largestFuncBytes"]),
        "inCallersObserved": in_observed,
        "adjacency": round(adjacency, 3),
        "score": round(dark * (1.0 + adjacency), 1),
        "lever": lever.id,
        "leverConfidence": lever.confidence,
        "needsTtd": lever.needs_ttd,
        "needsElevation": lever.needs_elevation,
        "reachableByProbing": reachable,
        "falsifier": lever.falsifier,
    }


def load_dark_regions(snapshot: pathlib.Path) -> list[dict[str, str]]:
    path = snapshot / "ledger-dark.tsv"
    if not path.is_file():
        raise SystemExit(
            f"no ledger-dark.tsv under {snapshot}. Build a snapshot first:\n"
            f"  py -3 tools/re_coverage_ledger.py build --out {snapshot}"
        )
    with path.open(encoding="utf-8") as handle:
        rows = [line for line in handle if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


def build_worklist(
    snapshot: pathlib.Path, top: int = 25, exclude_ttd: bool = False
) -> dict[str, Any]:
    regions = load_dark_regions(snapshot)
    scored = [score_region(r) for r in regions]

    total_dark = sum(r["darkBytes"] for r in scored)
    unreachable = sum(
        r["darkBytes"] for r in scored if r["lever"] == "unreachable-by-probing"
    )
    no_lever = sum(r["darkBytes"] for r in scored if r["leverConfidence"] == "NONE")
    addressable = total_dark - unreachable - no_lever

    candidates = [r for r in scored if r["reachableByProbing"]]
    if exclude_ttd:
        candidates = [r for r in candidates if not r["needsTtd"]]
    candidates.sort(key=lambda r: -r["score"])

    by_lever: dict[str, dict[str, Any]] = {}
    for row in scored:
        entry = by_lever.setdefault(
            row["lever"],
            {
                "lever": row["lever"],
                "confidence": row["leverConfidence"],
                "needsTtd": row["needsTtd"],
                "needsElevation": row["needsElevation"],
                "regions": 0,
                "darkBytes": 0,
            },
        )
        entry["regions"] += 1
        entry["darkBytes"] += row["darkBytes"]

    return {
        "tool": "tools/probe/select.py",
        "snapshot": str(snapshot),
        "regionCount": len(scored),
        "darkBytesInRegions": total_dark,
        "unreachableByProbing": unreachable,
        "noKnownLever": no_lever,
        "addressableDarkBytes": addressable,
        "byLever": sorted(by_lever.values(), key=lambda e: -e["darkBytes"]),
        "worklist": candidates[:top],
        "excludedTtdLevers": exclude_ttd,
    }


def render(worklist: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    total = worklist["darkBytesInRegions"]

    def pct(value: int) -> str:
        return f"{100.0 * value / total:.1f}%" if total else "-"

    add(f"snapshot  {worklist['snapshot']}")
    add(f"regions   {worklist['regionCount']}, "
        f"{total:,} dark bytes in never-entered bodies")
    add("")
    add(f"  unreachable by probing   {worklist['unreachableByProbing']:>9,}  "
        f"{pct(worklist['unreachableByProbing'])}   exception unwind and error "
        "paths")
    add(f"  no known lever           {worklist['noKnownLever']:>9,}  "
        f"{pct(worklist['noKnownLever'])}   needs a new instrument")
    add(f"  ADDRESSABLE              {worklist['addressableDarkBytes']:>9,}  "
        f"{pct(worklist['addressableDarkBytes'])}")
    add("")
    add("BY LEVER")
    add("")
    for entry in worklist["byLever"]:
        cost = (
            "TTD + elevation (needs the maintainer)"
            if entry["needsElevation"]
            else "unattended, no elevation"
        )
        add(f"  {entry['lever']:<26} {entry['darkBytes']:>9,} bytes  "
            f"{entry['regions']:>4} regions  {entry['confidence']:<11} {cost}")
    add("")
    add(f"WORKLIST (top {len(worklist['worklist'])} by dark bytes x adjacency)")
    add("")
    for index, row in enumerate(worklist["worklist"], 1):
        add(f"{index:>3}. {row['startVa']}  {row['darkBytes']:>7,} bytes  "
            f"{row['funcCount']:>4} funcs  adjacency {row['adjacency']:.2f}")
        add(f"     {row['reachClass']}  {row['families'][:80]}")
        add(f"     largest: {row['largestFunc'][:70]} "
            f"({row['largestFuncBytes']:,} bytes)")
        add(f"     lever: {row['lever']} [{row['leverConfidence']}]"
            + ("  NEEDS TTD + ELEVATION" if row["needsElevation"] else "  unattended"))
        add("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Self-check
# ---------------------------------------------------------------------------


def self_check() -> int:
    """The selector must be capable of saying 'I do not know'.

    A catalogue that matches everything is a catalogue that has stopped
    distinguishing, and it would rank a region it cannot reach exactly as
    highly as one it can.
    """

    print("self-check: the selector must be able to abstain")
    print("=" * 62)
    failures = 0

    unknown = choose_lever(
        {"topReachClass": "SOMETHING_NOBODY_CLASSIFIED", "topFamilies": "CZzz(3)"}
    )
    print(f"unknown class -> {unknown.id}")
    if unknown.id != "no-known-lever":
        print("FAILED: the catalogue matched a class it has never seen.")
        failures += 1

    funclet = choose_lever(
        {"topReachClass": "CRT_EH_FUNCLET", "topFamilies": "(eh-funclet)(1179)"}
    )
    print(f"eh-funclet -> {funclet.id} (reachable="
          f"{funclet.id != 'unreachable-by-probing'})")
    if funclet.id != "unreachable-by-probing":
        print("FAILED: unwind funclets were offered as a probe target.")
        failures += 1

    texture = choose_lever(
        {"topReachClass": "RENDER", "topFamilies": "CDXTexture(44); CTexture(3)"}
    )
    print(f"CDXTexture -> {texture.id}")
    if texture.id != "authored-asset-format":
        print(f"FAILED: expected authored-asset-format, got {texture.id}.")
        failures += 1

    # Every lever must carry a falsifier, or the worklist is a list of
    # conclusions rather than a list of tests.
    for lever in LEVERS:
        if len(lever.falsifier) < 40:
            print(f"FAILED: lever {lever.id} has no real falsifier.")
            failures += 1
        if lever.confidence not in ("OBSERVED", "PLAUSIBLE", "SPECULATIVE", "NONE"):
            print(f"FAILED: lever {lever.id} has confidence "
                  f"{lever.confidence!r}.")
            failures += 1
    print(f"every lever carries a falsifier and a confidence: {failures == 0}")

    # Adjacency must move the ranking, or the weight is decoration.
    base = {
        "startVa": "0x1", "endVa": "0x2", "darkBytes": "1000", "funcCount": "1",
        "namedCount": "1", "topReachClass": "RENDER", "topFamilies": "CMesh(1)",
        "largestFunc": "f", "largestFuncBytes": "1000", "inCallersTotal": "10",
    }
    island = score_region({**base, "inCallersObserved": "0"})
    connected = score_region({**base, "inCallersObserved": "10"})
    print(f"adjacency changes the score: {island['score']} -> "
          f"{connected['score']}")
    if not connected["score"] > island["score"]:
        print("FAILED: adjacency is not affecting the ranking at all.")
        failures += 1

    print("=" * 62)
    print("all self-checks held" if not failures else f"{failures} FAILED")
    return 1 if failures else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--snapshot", type=pathlib.Path)
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument(
        "--no-ttd",
        action="store_true",
        help="only levers that run unattended without elevation",
    )
    parser.add_argument("--json-out", type=pathlib.Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)

    if args.self_check:
        return self_check()
    if not args.snapshot:
        parser.error("--snapshot is required unless --self-check is given")

    worklist = build_worklist(args.snapshot, args.top, args.no_ttd)
    print(render(worklist))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(worklist, indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
