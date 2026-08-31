#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compare probe receipts across arms, and emit the finding skeleton.

WHY THIS EXISTS
---------------
Every real inference the discovery loop has produced came from putting two
receipts side by side -- and so did every mistake. The proof run on 2026-08-02
inferred an archive rejection from a single launch that exited early, and a
second launch of the SAME archive then ran to the deadline. One sample of a
process whose exit code is not stable is not a measurement, and reading it as
one is the single most repeatable error in this project's history.

This stage does the side-by-side mechanically, and it enforces the one rule that
the manual version kept forgetting:

    A DIFFERENCE BETWEEN ARMS IS ONLY REAL IF IT EXCEEDS THE SPREAD WITHIN THEM.

An arm with n=1 has no measurable spread, so it can support no difference at
all. That is not a statistical nicety here; it is a transcription of the exact
run that misled us.

WHAT IT REFUSES TO CONCLUDE
---------------------------
  * Anything from an arm with fewer than two replicates. Reported, never
    concluded from.
  * Anything from a run that never reached level load. A game that died at
    sound init because the CWD was wrong tells you nothing about the payload,
    and it exits early and looks exactly like a rejection.
  * Anything from an arm set whose poison control behaved like its treatment.
    If the arm that SHOULD fail did whatever the arm under test did, the
    instrument did not discriminate and neither arm means anything.
  * Anything from a faulted run, unless the probe asked for the fault. The
    harness's fault gate already vetoes these; this stage counts them.

THE SKELETON IS DELIBERATELY INCOMPLETE
---------------------------------------
``--emit-finding`` writes a finding record pre-filled with everything that can
be MEASURED from receipts -- sample sizes, replicate counts, arm statistics,
specimen hashes, the poison control's behaviour -- and leaves every field that
requires judgement as an explicit ``TODO`` marker.

That is not laziness. A generator that auto-filled rivals and discriminators
would be handing the refuter its own boilerplate to score, and the refuter would
score it consistently, and the loop would promote findings on the strength of a
template. An unedited skeleton MUST be found INADMISSIBLE -- `--self-check`
asserts exactly that, and it is the only reason to trust anything this file
emits.

Usage
-----
    python ./tools/probe/compare.py --runs local-lab/probe-runs
    python ./tools/probe/compare.py --runs DIR --json-out compare.json
    python ./tools/probe/compare.py --runs DIR --emit-finding draft.json \
        --claim "..." --claim-id my-finding-2026-08-02
    python ./tools/probe/compare.py --self-check

Exit code: 0 when the comparison is sound, 1 when it is not usable as
evidence (poison control misbehaved, or every arm is unreplicated), 2 on a
refusal (bad inputs).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics
import sys
from typing import Any, Iterable, Optional, Sequence


ROOT = pathlib.Path(__file__).resolve().parents[2]

# A trailing replicate marker on a probe name.  ``blast-door-r3`` and
# ``blast-door-rep3`` both belong to arm ``blast-door``.  Naming a replicate is
# how an arm gets its n without a second manifest field to forget to set.
_REPLICATE_SUFFIX = re.compile(r"-(?:r|rep|run)(\d+)$", re.IGNORECASE)

# Substrings that mark an arm as the poison control.  A poison arm is one that
# SHOULD produce the negative outcome; if it does not, the instrument did not
# discriminate and no arm in the set means anything.
_POISON_MARKERS = ("poison", "control-negative", "should-fail")

# Below this many replicates an arm cannot support a difference claim.  Two is
# the floor, not the target: two runs establish that a spread exists, not what
# it is.
MIN_REPLICATES = 2

# The largest within-arm decision-time spread measured on BYTE-IDENTICAL inputs
# inside a single session: campaign 02's losecmd arm, 2.757 s over three runs.
# Any narrower "noise floor" is an artefact of a lucky-tight sample.
MEASURED_DECISION_TIME_NOISE_SECONDS = 2.757


class CompareError(Exception):
    """A refusal.  Carries the reason verbatim."""


# ---------------------------------------------------------------------------
# Loading receipts
# ---------------------------------------------------------------------------


def arm_of(probe_name: str, declared: Optional[str] = None) -> tuple[str, Optional[int]]:
    """Split a probe name into (arm, replicate index)."""

    if declared:
        return declared, None
    match = _REPLICATE_SUFFIX.search(probe_name)
    if match:
        return probe_name[: match.start()], int(match.group(1))
    return probe_name, None


def load_receipts(run_dir: pathlib.Path) -> list[dict[str, Any]]:
    """Read every ``receipt.json`` under ``run_dir``, newest run last.

    A receipt that will not parse is a refusal, not a skip.  Silently dropping
    one would change an arm's n without changing anything a reader can see.
    """

    if not run_dir.is_dir():
        raise CompareError(f"run directory does not exist: {run_dir}")
    receipts: list[dict[str, Any]] = []
    for path in sorted(run_dir.glob("*/receipt.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CompareError(f"{path}: not valid JSON: {exc}") from exc
        raw["_receiptPath"] = str(path)
        receipts.append(raw)
    if not receipts:
        raise CompareError(
            f"no receipts under {run_dir}. This stage compares runs; it cannot "
            "manufacture one."
        )
    return receipts


# ---------------------------------------------------------------------------
# Per-arm statistics
# ---------------------------------------------------------------------------


def oracle_signature(oracle: dict[str, Any], settle: Any = 0) -> str:
    """A shape string for an oracle, so incomparable arms can be refused.

    Two arms are comparable on decision time only if they asked the same KIND
    of question with the same settle window. The path an oracle names may
    differ -- one arm looks for baseline.txt and another for lose_after.txt --
    because that is the variable under test. What may not differ is whether one
    of them was waiting for a deadline while the other was waiting for a file.
    """

    kind = oracle.get("kind", "?")
    if kind in ("all", "any"):
        inner = ",".join(sorted(oracle_signature(sub) for sub in oracle.get("of", ())))
        body = f"{kind}({inner})"
    else:
        body = kind
    try:
        settle_value = float(settle or 0)
    except (TypeError, ValueError):
        settle_value = 0.0
    return f"{body}+settle{settle_value:g}"


def _spread(values: Sequence[float]) -> dict[str, Any]:
    if not values:
        return {"n": 0, "min": None, "max": None, "median": None, "spread": None}
    return {
        "n": len(values),
        "min": round(min(values), 3),
        "max": round(max(values), 3),
        "median": round(statistics.median(values), 3),
        "spread": round(max(values) - min(values), 3),
        "stdev": round(statistics.stdev(values), 3) if len(values) > 1 else None,
    }


def summarise_arm(name: str, receipts: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Everything measurable about one arm, with its denominator attached."""

    n = len(receipts)
    # NOT "lifetime". This is the time until the ORACLE DECIDED, and the same
    # receipt's processAliveAtDecision often proves the process outlived it by
    # a wide margin. Calling it lifetime invited exactly one wrong comparison:
    # a fileAppears arm deciding at 4s against a survives arm deciding at its
    # 30s deadline reads as a 26-second difference in which nothing about the
    # two processes differed at all. settleSeconds adds itself to this number
    # too. Hence oracle_signature below, and the refusal to difference across
    # different signatures.
    decisions = [
        float(r.get("oracle", {}).get("elapsedSeconds", 0.0))
        for r in receipts
        if r.get("oracle", {}).get("elapsedSeconds") is not None
    ]
    exit_codes = [r.get("oracle", {}).get("exitCode") for r in receipts]
    self_exited = [code is not None for code in exit_codes]
    faulted = [bool(r.get("faultGate", {}).get("triggered")) for r in receipts]
    vetoed = [bool(r.get("faultGate", {}).get("vetoed")) for r in receipts]
    level_loaded = [
        bool(r.get("diagnosis", {}).get("levelLoadLogged")) for r in receipts
    ]
    verdicts = [r.get("verdict", "UNKNOWN") for r in receipts]
    distinct_verdicts = sorted(set(verdicts))

    # A run that never reached level load is not evidence about the payload.
    # It is counted separately and excluded from the usable denominator, because
    # a CWD failure exits early and is indistinguishable from a rejection.
    usable = sum(1 for ok in level_loaded if ok)

    return {
        "arm": name,
        "n": n,
        "replicated": n >= MIN_REPLICATES,
        "receipts": [r["_receiptPath"] for r in receipts],
        "probeNames": sorted({r.get("probe", {}).get("name", "?") for r in receipts}),
        "verdicts": {v: verdicts.count(v) for v in distinct_verdicts},
        "verdictStable": len(distinct_verdicts) == 1,
        "exitCodes": exit_codes,
        "distinctExitCodes": sorted(
            {c for c in exit_codes if c is not None}
        ),
        "selfExitRate": round(sum(self_exited) / n, 3) if n else None,
        "faultRate": round(sum(faulted) / n, 3) if n else None,
        "vetoedCount": sum(vetoed),
        "levelLoadRate": round(sum(level_loaded) / n, 3) if n else None,
        "usableRuns": usable,
        "erroredRuns": verdicts.count("ERROR"),
        "oracleDecisionSeconds": _spread(decisions),
        "oracleSignature": sorted(
            {oracle_signature(r.get("probe", {}).get("oracle", {}),
                              r.get("oracle", {}).get("settleSeconds", 0))
             for r in receipts}
        ),
        "isPoison": any(marker in name.lower() for marker in _POISON_MARKERS),
        "stagedPayloads": sorted(
            {
                entry.get("sha256", "")
                for r in receipts
                for entry in r.get("staging", {}).get("stagedFiles", ())
            }
            - {""}
        ),
    }


def group_arms(
    receipts: Iterable[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for receipt in receipts:
        probe_name = receipt.get("probe", {}).get("name", "?")
        arm, _ = arm_of(probe_name, receipt.get("probe", {}).get("arm"))
        grouped.setdefault(arm, []).append(receipt)
    return grouped


# ---------------------------------------------------------------------------
# Cross-arm comparison -- the rule this whole file exists for
# ---------------------------------------------------------------------------


def compare_pair(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Is the difference between two arms bigger than the noise inside them?

    THE RULE.  A lifetime difference counts only when the gap between the arms'
    medians exceeds the WIDER of their two internal spreads. Anything smaller is
    inside the noise the proof run already demonstrated, where the same archive
    launched twice gave two different answers.

    This is deliberately a coarse rule rather than a significance test. With
    n=2 or n=3 -- which is what a probe campaign can actually afford at 62x
    slowdown -- a p-value would be theatre. 'Bigger than the observed spread' is
    something a reader can check by looking at the numbers.
    """

    notes: list[str] = []
    blocked = False

    for arm in (a, b):
        if not arm["replicated"]:
            notes.append(
                f"{arm['arm']} has n={arm['n']}: no spread can be measured, so "
                "no difference involving it is supportable"
            )
            blocked = True
        if arm["usableRuns"] == 0:
            notes.append(
                f"{arm['arm']}: not one run reached level load -- these runs are "
                "about the launch, not the payload"
            )
            blocked = True
        elif arm["usableRuns"] < arm["n"]:
            notes.append(
                f"{arm['arm']}: only {arm['usableRuns']}/{arm['n']} runs reached "
                "level load; the rest are not evidence about the payload"
            )
        if len(arm["stagedPayloads"]) > 1:
            notes.append(
                f"{arm['arm']} groups {len(arm['stagedPayloads'])} DIFFERENT "
                "staged payloads under one arm name. The -rN suffix reads as "
                "'replicate' to the grouper and as 'revision' to a human, and "
                "these runs are not replicates of each other"
            )
            blocked = True
        if len(arm["oracleSignature"]) > 1:
            notes.append(
                f"{arm['arm']} mixes oracle shapes {arm['oracleSignature']}; "
                "its own replicates were not asked the same question"
            )
            blocked = True

    # DIFFERENT QUESTIONS ARE NOT A DIFFERENT ANSWER. elapsedSeconds is the
    # time until the oracle decided, so an arm that waits for a file and an arm
    # that waits out a deadline differ by the whole deadline even when the two
    # processes behaved identically. Verified: a 25.99s "difference" against a
    # 0.02s spread, in which nothing about either run differed.
    if a["oracleSignature"] != b["oracleSignature"]:
        notes.append(
            f"{a['arm']} and {b['arm']} declared different oracle shapes "
            f"({a['oracleSignature']} vs {b['oracleSignature']}). Their decision "
            "times measure different questions and cannot be differenced"
        )
        blocked = True

    life_a = a["oracleDecisionSeconds"]
    life_b = b["oracleDecisionSeconds"]
    lifetime_verdict = "UNKNOWN"
    gap = None
    noise = None
    if life_a["median"] is not None and life_b["median"] is not None:
        gap = round(abs(life_a["median"] - life_b["median"]), 3)
        noise = round(max(life_a["spread"] or 0.0, life_b["spread"] or 0.0), 3)
        if blocked:
            lifetime_verdict = "NOT SUPPORTABLE"
        elif gap > noise:
            lifetime_verdict = "DIFFERENT"
            notes.append(
                f"oracle decided at medians differ by {gap}s, which exceeds the widest "
                f"within-arm spread ({noise}s)"
            )
        else:
            lifetime_verdict = "INDISTINGUISHABLE"
            notes.append(
                f"oracle decided at medians differ by {gap}s, which does NOT exceed the "
                f"within-arm spread ({noise}s) -- this is noise, not a result"
            )

    verdict_differs = (
        a["verdictStable"]
        and b["verdictStable"]
        and set(a["verdicts"]) != set(b["verdicts"])
    )
    if not a["verdictStable"] or not b["verdictStable"]:
        notes.append(
            "at least one arm gave different verdicts on identical inputs; its "
            "own replicates disagree, so it cannot be compared to anything"
        )
        # This used to be a note and nothing else, so the sentence "it cannot be
        # compared to anything" was printed and then the comparison proceeded.
        blocked = True

    return {
        "armA": a["arm"],
        "armB": b["arm"],
        "lifetimeGapSeconds": gap,
        "withinArmNoiseSeconds": noise,
        "lifetimeVerdict": lifetime_verdict,
        "verdictsDiffer": verdict_differs and not blocked,
        "supportable": not blocked,
        "notes": notes,
    }


def check_poison(arms: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """The instrument has to be able to produce a negative, or nothing counts.

    A poison arm that PASSES means the oracle agreed with an input built to be
    rejected -- the check cannot fail, and a check that cannot fail proves
    nothing about the arms that passed beside it.
    """

    poisons = [a for a in arms if a["isPoison"]]
    treatments = [a for a in arms if not a["isPoison"]]
    notes: list[str] = []
    if not poisons:
        return {
            "present": False,
            "sound": False,
            "poisonArms": [],
            "problems": ["no poison control in this arm set"],
            "notes": [],
            "detail": (
                "NO POISON CONTROL in this arm set. Without an arm that should "
                "fail, a clean result is indistinguishable from an instrument "
                "that cannot report failure."
            ),
        }

    problems: list[str] = []
    for poison in poisons:
        # STEP 1 -- IS THE POISON ARM ITSELF VALID? Everything after this
        # depends on the answer, and an invalid control cannot be rescued by
        # turning out to differ from the treatment.
        invalid: list[str] = []
        if poison["erroredRuns"]:
            invalid.append(
                f"{poison['erroredRuns']}/{poison['n']} of its runs ERRORED "
                "before reaching the engine; a payload that never ran is not a "
                "negative result"
            )
        if not poison["replicated"]:
            invalid.append(
                f"n={poison['n']}: a control that ran once has not been shown "
                "to behave"
            )
        if poison["usableRuns"] < poison["n"]:
            invalid.append(
                f"only {poison['usableRuns']}/{poison['n']} of its runs reached "
                "level load, so the rest never tested the payload at all"
            )
        if poison["faultRate"]:
            invalid.append(
                f"it faulted in {poison['faultRate']:.0%} of runs; a control "
                "that crashes is not showing that the oracle can report a "
                "negative, only that the engine can fall over"
            )
        if not poison["verdictStable"]:
            invalid.append(
                f"its own replicates disagree: {sorted(poison['verdicts'])}"
            )
        if set(poison["verdicts"]) != {"FAIL"}:
            invalid.append(
                f"its verdicts are {sorted(poison['verdicts'])}; a control is "
                "sound only when it FAILS, and neither PASS nor UNKNOWN is a "
                "failure"
            )
        if invalid:
            problems.append(
                f"{poison['arm']} is not a usable poison control: "
                + "; ".join(invalid)
            )
            continue

        # STEP 2 -- ONLY NOW may a shared verdict be excused by a difference.
        #
        # This branch exists because campaign 03's landscape arm and its poison
        # arm both reported FAIL for opposite reasons, and calling that
        # "separates nothing" would have discarded the strongest result of the
        # night. An adversarial pass then found eight ways the branch as first
        # written certified a BROKEN control as sound: a poison arm that reached
        # level load in 1 run of 3, a treatment that hung once, a 0.5 s gap
        # between two lucky-tight triples, and two arms that had asked entirely
        # different questions.
        #
        # The rule that survived: the difference must be evidence about the
        # TREATMENT, measured against a control already proven healthy in step
        # 1, on arms that asked the same question. A control's own brokenness is
        # never evidence that the instrument discriminates.
        for treatment in treatments:
            if not (
                treatment["verdictStable"]
                and poison["verdictStable"]
                and set(treatment["verdicts"]) == set(poison["verdicts"])
            ):
                continue
            if poison["oracleSignature"] != treatment["oracleSignature"]:
                problems.append(
                    f"{poison['arm']} (poison) and {treatment['arm']} "
                    f"(treatment) share the verdict "
                    f"{sorted(poison['verdicts'])} and asked DIFFERENT "
                    f"questions ({poison['oracleSignature']} vs "
                    f"{treatment['oracleSignature']}). A control only controls "
                    "for the thing it was run alongside"
                )
                continue
            if not treatment["replicated"]:
                problems.append(
                    f"{treatment['arm']} shares the verdict "
                    f"{sorted(poison['verdicts'])} with the poison arm and has "
                    f"n={treatment['n']}: nothing about it can be distinguished "
                    "from anything"
                )
                continue

            differences: list[str] = []

            # A RATE STRICTLY BETWEEN 0 AND 1 IS THE ARM DISAGREEING WITH
            # ITSELF, and that is instability rather than evidence -- the same
            # rule that governs verdicts, applied to the rates. Campaign 03's
            # landscape arm faulted in 3 runs of 3; one flaky crash in three
            # would have been indistinguishable from the engine having a bad
            # afternoon, and counting it would let any flake certify any
            # control.
            def _consistent(rate):
                return rate in (0.0, 1.0)

            for label, key in (("fault rate", "faultRate"),
                               ("self-exit rate", "selfExitRate")):
                p_rate, t_rate = poison[key], treatment[key]
                if p_rate == t_rate:
                    continue
                if not (_consistent(p_rate) and _consistent(t_rate)):
                    notes.append(
                        f"{treatment['arm']} and {poison['arm']} differ on "
                        f"{label} ({p_rate} vs {t_rate}) but at least one arm "
                        "is inconsistent with itself across its own replicates; "
                        "not counted as discrimination"
                    )
                    continue
                differences.append(f"{label} {p_rate} vs {t_rate}")
            if treatment["usableRuns"] < treatment["n"]:
                # NOT counted as discrimination: a treatment that failed to
                # load is the treatment being broken, which is the same error
                # as the control being broken, pointed the other way.
                notes.append(
                    f"{treatment['arm']} reached level load in only "
                    f"{treatment['usableRuns']}/{treatment['n']} runs; that is "
                    "not counted as discrimination"
                )
            p_time = poison["oracleDecisionSeconds"]
            t_time = treatment["oracleDecisionSeconds"]
            if p_time["median"] is not None and t_time["median"] is not None:
                gap = abs(p_time["median"] - t_time["median"])
                # The floor matters as much as the spreads. Two lucky-tight
                # triples can each show a 0.04 s spread and still sit 0.5 s
                # apart for no reason, and the measured within-arm spread on
                # BYTE-IDENTICAL inputs in one session has been as wide as
                # 2.757 s.
                noise = max(
                    p_time["spread"] or 0.0,
                    t_time["spread"] or 0.0,
                    MEASURED_DECISION_TIME_NOISE_SECONDS,
                )
                if gap > noise:
                    differences.append(
                        f"decision-time medians {p_time['median']}s vs "
                        f"{t_time['median']}s, gap {gap:.3f}s beyond the "
                        f"{noise:.3f}s noise floor"
                    )
            if differences:
                notes.append(
                    f"{poison['arm']} (poison) and {treatment['arm']} "
                    f"(treatment) share the verdict "
                    f"{sorted(poison['verdicts'])} but are distinguishable on: "
                    + "; ".join(differences)
                    + ". The instrument separated them; the verdict label did "
                    "not."
                )
            else:
                problems.append(
                    f"{poison['arm']} (poison) and {treatment['arm']} "
                    f"(treatment) produced the same verdict "
                    f"{sorted(poison['verdicts'])} and differ on NO measured "
                    "dimension -- this arm set separates nothing"
                )
    return {
        "present": True,
        "sound": not problems,
        "poisonArms": [p["arm"] for p in poisons],
        "problems": problems,
        "notes": notes,
        "detail": (
            "the poison control produced the negative outcome it was built for"
            + ("; " + "; ".join(notes) if notes else "")
            if not problems
            else "; ".join(problems)
        ),
    }


def build_report(receipts: Sequence[dict[str, Any]]) -> dict[str, Any]:
    grouped = group_arms(receipts)
    arms = [summarise_arm(name, group) for name, group in sorted(grouped.items())]
    pairs = []
    for i, a in enumerate(arms):
        for b in arms[i + 1 :]:
            pairs.append(compare_pair(a, b))
    poison = check_poison(arms)

    replicated = [a for a in arms if a["replicated"]]
    usable = bool(replicated) and poison["sound"]

    return {
        "tool": "tools/probe/compare.py",
        "armCount": len(arms),
        "receiptCount": len(receipts),
        "arms": arms,
        "pairs": pairs,
        "poisonControl": poison,
        "usableAsEvidence": usable,
        "whyNot": (
            []
            if usable
            else (
                ([] if replicated else ["no arm has 2 or more replicates"])
                + ([] if poison["sound"] else [poison["detail"]])
            )
        ),
    }


# ---------------------------------------------------------------------------
# The finding skeleton
# ---------------------------------------------------------------------------

# The placeholders are long, explicit sentences rather than the bare string
# "TODO" for one reason that took a failed self-check to learn: a skeleton whose
# fields are too short is rejected by the schema rule, and a schema rejection
# BLOCKS every substantive rule in the refuter from running at all. The
# generator then looks guarded when in fact nothing about rivals, discriminators
# or predictions was ever evaluated. A skeleton must be well-formed enough to be
# JUDGED, and then judged and rejected on the merits.
TODO = "TODO"
TODO_RIVAL = (
    "TODO: name a competing explanation that the same evidence would also "
    "produce. If none exists, the evidence does not discriminate."
)
TODO_DISCRIMINATOR = (
    "TODO: name one observation whose outcome differs under the claim and "
    "under the rival."
)
TODO_EXPECTED_CLAIM = "TODO: what this observation shows if the claim is true."
TODO_EXPECTED_RIVAL = "TODO: what it shows if the rival is true instead."
TODO_PREDICTION = (
    "TODO: state a test that was run, with its result written down first."
)
TODO_PROCEDURE = (
    "TODO: a procedure reproducible enough for someone else to run the same "
    "thing."
)
TODO_FALSIFIER = (
    "TODO: the concrete outcome that would have killed this claim."
)
TODO_POPULATION = "TODO: what the claim ranges over."
TODO_MECHANISM = "todo.unspecified"


def emit_finding_skeleton(
    report: dict[str, Any],
    claim_id: str,
    claim_statement: str,
    date: str,
) -> dict[str, Any]:
    """Fill in what receipts measure; leave every judgement as a TODO.

    What is filled: sample sizes, replicate counts, instruments, arm statistics,
    the poison control's behaviour, and the residuals the comparison itself
    found. What is NOT filled: the rival explanations, the discriminator, and
    the predictions. Those are the fields that decide whether a claim is true,
    and a template cannot supply them -- if it could, the refuter would be
    scoring the template.
    """

    arms = report["arms"]
    total_runs = sum(a["n"] for a in arms)
    usable_runs = sum(a["usableRuns"] for a in arms)
    sessions = len(arms)

    residuals: list[dict[str, Any]] = []
    for arm in arms:
        if not arm["replicated"]:
            residuals.append(
                {
                    "id": f"unreplicated-{arm['arm']}",
                    "statement": (
                        f"arm {arm['arm']} has n={arm['n']}; a single launch's "
                        "exit code and lifetime are not stable in this engine"
                    ),
                    "mechanism": ["probe.replication"],
                    "blocksClaim": True,
                }
            )
        if not arm["verdictStable"]:
            residuals.append(
                {
                    "id": f"unstable-{arm['arm']}",
                    "statement": (
                        f"arm {arm['arm']} produced verdicts "
                        f"{sorted(arm['verdicts'])} on identical inputs"
                    ),
                    "mechanism": ["probe.replication"],
                    "blocksClaim": True,
                }
            )
        if arm["usableRuns"] < arm["n"]:
            residuals.append(
                {
                    "id": f"launch-not-payload-{arm['arm']}",
                    "statement": (
                        f"{arm['n'] - arm['usableRuns']}/{arm['n']} runs in arm "
                        f"{arm['arm']} never logged level load, so they are "
                        "evidence about the launch and not about the payload"
                    ),
                    "mechanism": ["probe.launch"],
                    "blocksClaim": True,
                }
            )
    for arm in arms:
        if len(arm["stagedPayloads"]) > 1:
            residuals.append(
                {
                    "id": f"mixed-payloads-{arm['arm']}",
                    "statement": (
                        f"arm {arm['arm']} groups {len(arm['stagedPayloads'])} "
                        "DIFFERENT staged payloads under one arm name; its runs "
                        "are not replicates of each other and its sample size "
                        "does not mean what it says"
                    ),
                    "mechanism": ["probe.replication"],
                    "blocksClaim": True,
                }
            )
        if len(arm["oracleSignature"]) > 1:
            residuals.append(
                {
                    "id": f"mixed-oracles-{arm['arm']}",
                    "statement": (
                        f"arm {arm['arm']} mixes oracle shapes "
                        f"{arm['oracleSignature']}; its replicates were not "
                        "asked the same question"
                    ),
                    "mechanism": ["probe.oracle"],
                    "blocksClaim": True,
                }
            )

    # THE CROSS-ARM BLOCKERS. The docstring promised "the residuals the
    # comparison itself found" and then only ever read per-arm conditions, so
    # every reason compare_pair refused a comparison was dropped before the
    # record was written.
    for pair in report.get("pairs", ()):
        if pair.get("supportable"):
            continue
        residuals.append(
            {
                "id": f"not-comparable-{pair['armA']}-vs-{pair['armB']}",
                "statement": (
                    f"{pair['armA']} and {pair['armB']} cannot be compared: "
                    + "; ".join(pair.get("notes", ())) or "no reason recorded"
                ),
                "mechanism": ["probe.comparison"],
                "blocksClaim": True,
            }
        )

    if not report["poisonControl"]["sound"]:
        residuals.append(
            {
                "id": "poison-control-unsound",
                "statement": report["poisonControl"]["detail"],
                "mechanism": ["probe.control"],
                "blocksClaim": True,
            }
        )
    residuals.append(
        {
            "id": "skeleton-not-edited",
            "statement": (
                "this record was emitted by tools/probe/compare.py and its "
                "rivals, discriminator and predictions are still TODO "
                "placeholders; it states what was measured and nothing about "
                "what it means"
            ),
            "mechanism": ["probe.finding"],
            "blocksClaim": True,
        }
    )

    return {
        "schemaVersion": 1,
        "id": claim_id,
        "title": claim_statement[:120],
        "date": date,
        "lane": "reverse-engineering",
        "author": "tools/probe/compare.py (skeleton -- unedited)",
        "sourceNote": TODO,
        "findingKind": "instrument-derived",
        "claim": {
            "statement": claim_statement,
            "grade": "EXECUTED",
            "mechanism": [TODO_MECHANISM],
        },
        "scope": {
            "population": TODO_POPULATION,
            "covered": (
                f"{usable_runs} runs that reached level load, out of "
                f"{total_runs} launched, across {sessions} arms"
            ),
            "notCovered": [
                "TODO: name the exclusions. An empty list is itself a claim."
            ],
        },
        "rivals": [
            {
                "id": "rival-1",
                "statement": TODO_RIVAL,
                "indistinguishableOn": [
                    "TODO: the observations that are true under both."
                ],
                "discriminator": {
                    "description": TODO_DISCRIMINATOR,
                    "mechanism": [TODO_MECHANISM],
                    "expectedUnderClaim": TODO_EXPECTED_CLAIM,
                    "expectedUnderRival": TODO_EXPECTED_RIVAL,
                    "status": "not_observed",
                    "outcome": "none",
                },
            }
        ],
        "predictions": [
            {
                "id": "prediction-1",
                "statement": TODO_PREDICTION,
                "procedure": TODO_PROCEDURE,
                "expected": "TODO: what the procedure should produce.",
                "wouldFalsifyIf": TODO_FALSIFIER,
                "predictedInAdvance": False,
                "result": "not_run",
            }
        ],
        "overturnedBy": [
            {
                "id": "overturn-1",
                "procedure": (
                    "TODO: a test not yet run that would kill this claim."
                ),
                "wouldShow": "TODO: the outcome that would kill it.",
            }
        ],
        "evidence": [
            {
                "id": f"arm-{arm['arm']}",
                "grade": "EXECUTED",
                "instrument": "tools/probe/probe_harness.py",
                "summary": (
                    f"n={arm['n']}, verdicts {arm['verdicts']}, "
                    f"self-exit rate {arm['selfExitRate']}, "
                    f"fault rate {arm['faultRate']}, "
                    f"level-load rate {arm['levelLoadRate']}, "
                    f"oracle decided at median {arm['oracleDecisionSeconds']['median']}s "
                    f"spread {arm['oracleDecisionSeconds']['spread']}s"
                ),
                # INDEPENDENCE IS A JUDGEMENT, NOT A COUNT. Writing n into
                # independentReplicates asserts the runs were replicates of each
                # other -- the exact thing compare_pair refuses when an arm
                # groups two different staged payloads, and refute.py prints it
                # in the survival record as "N independent replicate(s) at the
                # thinnest point". It is claimed only when the arm carries at
                # most one distinct payload; otherwise it drops to 1 and the
                # residual below says why.
                "sample": {
                    "n": arm["n"],
                    "units": "probe runs",
                    "independentReplicates": (
                        arm["n"] if len(arm["stagedPayloads"]) <= 1 else 1
                    ),
                    # Not measured: no receipt records a session. One arm is one
                    # invocation of the harness, so this is the honest floor
                    # rather than a count of anything.
                    "sessions": 1,
                },
            }
            for arm in arms
        ],
        "residuals": residuals,
        # THE ONE JUDGEMENT-BEARING FIELD THIS TOOL MAY FILL IN, because it is
        # not a judgement: whether the poison arm produced its negative is a
        # measured fact sitting in the receipts. It is top-level, not nested --
        # measured on the first self-check, where a nested one was invisible to
        # R12 and the skeleton was scored as having no control at all.
        "poisonControl": {
            "id": "poison-arm",
            "kind": "poison",
            "description": report["poisonControl"]["detail"][:800],
            "predictedOutcome": (
                "the poison arm produces the negative outcome; if it does not, "
                "the instrument cannot report failure and no arm beside it "
                "means anything"
            ),
            "observedOutcome": ", ".join(
                f"{arm['arm']}: {arm['verdicts']}"
                for arm in report["arms"]
                if arm["isPoison"]
            )
            or "no poison arm was present in this run set",
            "result": (
                "failed_as_predicted"
                if report["poisonControl"]["sound"]
                else (
                    "did_not_fail"
                    if report["poisonControl"]["present"]
                    else "not_run"
                )
            ),
        },
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render(report: dict[str, Any]) -> str:
    lines: list[str] = []
    add = lines.append
    add(f"{report['receiptCount']} receipts, {report['armCount']} arms")
    add("")
    for arm in report["arms"]:
        tag = "  [POISON]" if arm["isPoison"] else ""
        add(f"ARM {arm['arm']}{tag}")
        add(f"  n                 {arm['n']}"
            + ("" if arm["replicated"] else "   <-- UNREPLICATED, concludes nothing"))
        add(f"  verdicts          {arm['verdicts']}"
            + ("" if arm["verdictStable"] else "   <-- replicates DISAGREE"))
        add(f"  self-exit rate    {arm['selfExitRate']}")
        add(f"  fault rate        {arm['faultRate']}  (vetoed {arm['vetoedCount']})")
        add(f"  level-load rate   {arm['levelLoadRate']}  "
            f"({arm['usableRuns']}/{arm['n']} usable)")
        life = arm["oracleDecisionSeconds"]
        add(f"  oracle decided at median {life['median']}s  "
            f"min {life['min']}s  max {life['max']}s  spread {life['spread']}s")
        add(f"  exit codes        {arm['exitCodes']}")
        add("")

    add("CROSS-ARM")
    add("")
    if not report["pairs"]:
        add("  only one arm: nothing to compare it to")
    for pair in report["pairs"]:
        add(f"  {pair['armA']}  vs  {pair['armB']}: {pair['lifetimeVerdict']}")
        for note in pair["notes"]:
            add(f"    - {note}")
    add("")

    poison = report["poisonControl"]
    add(f"POISON CONTROL: {'sound' if poison['sound'] else 'UNSOUND'}")
    add(f"  {poison['detail']}")
    add("")
    add(f"USABLE AS EVIDENCE: {report['usableAsEvidence']}")
    for reason in report["whyNot"]:
        add(f"  - {reason}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Self-check: the skeleton must not be admissible
# ---------------------------------------------------------------------------


def self_check() -> int:
    """Prove the generator cannot manufacture a promotable finding.

    Emits a skeleton from a synthetic clean report and runs the real refuter
    over it. If the refuter promotes an unedited template, this stage is a
    finding factory and must not be used.
    """

    import subprocess
    import tempfile

    print("self-check: an unedited skeleton must NOT be promotable")
    print("=" * 62)
    failures = 0

    fake_arms = [
        {
            "arm": "treatment",
            "n": 3,
            "replicated": True,
            "receipts": [],
            "probeNames": ["treatment"],
            "verdicts": {"PASS": 3},
            "verdictStable": True,
            "exitCodes": [0, 0, 0],
            "distinctExitCodes": [0],
            "selfExitRate": 1.0,
            "faultRate": 0.0,
            "vetoedCount": 0,
            "levelLoadRate": 1.0,
            "usableRuns": 3,
            "erroredRuns": 0,
            "oracleSignature": ["processExit+settle0"],
            "oracleDecisionSeconds": _spread([10.0, 10.1, 10.2]),
            "isPoison": False,
            "stagedPayloads": [],
        },
        {
            "arm": "poison",
            "n": 3,
            "replicated": True,
            "receipts": [],
            "probeNames": ["poison"],
            "verdicts": {"FAIL": 3},
            "verdictStable": True,
            "exitCodes": [0, 0, 0],
            "distinctExitCodes": [0],
            "selfExitRate": 1.0,
            "faultRate": 0.0,
            "vetoedCount": 0,
            "levelLoadRate": 1.0,
            "usableRuns": 3,
            "erroredRuns": 0,
            "oracleSignature": ["processExit+settle0"],
            "oracleDecisionSeconds": _spread([2.0, 2.1, 2.2]),
            "isPoison": True,
            "stagedPayloads": [],
        },
    ]
    report = {
        "tool": "tools/probe/compare.py",
        "armCount": 2,
        "receiptCount": 6,
        "arms": fake_arms,
        "pairs": [compare_pair(fake_arms[0], fake_arms[1])],
        "poisonControl": check_poison(fake_arms),
        "usableAsEvidence": True,
        "whyNot": [],
    }
    skeleton = emit_finding_skeleton(
        report, "self-check-skeleton", "A synthetic claim.", "2026-08-02"
    )

    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "skeleton.json"
        path.write_text(json.dumps(skeleton, indent=2), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "probe" / "refute.py"),
             str(path)],
            capture_output=True,
            text=True,
        )

    output = result.stdout or result.stderr
    promoted = result.returncode == 0
    print(f"refuter exit code: {result.returncode} "
          f"({'PROMOTED' if promoted else 'not promoted'})")
    for line in output.strip().splitlines():
        if line.strip().startswith(("INADMISSIBLE", "UNSCORED", "REFUTED",
                                    "BLOCKED", "VERDICT", "passed:")):
            print(f"  {line.strip()}")
    print("=" * 62)
    if promoted:
        print(
            "FAILED: the refuter promoted an unedited template. This generator "
            "is a finding factory; do not use it."
        )
        return 1

    # NOT ENOUGH THAT IT FAILED -- IT HAS TO FAIL FOR THE RIGHT REASON.
    # Measured on the first run of this self-check: the skeleton was malformed,
    # R01_SCHEMA rejected it, and every substantive rule was BLOCKED and never
    # ran. The check reported "not promoted" and proved nothing whatever about
    # whether an empty rival or an unobserved discriminator would be caught.
    if "R01_SCHEMA" in output and "not evaluated" in output:
        print(
            "FAILED: the skeleton was rejected by the SCHEMA rule, which blocks "
            "every substantive rule from running. That proves the template is "
            "malformed, not that the refuter would catch an unedited one. Fix "
            "the skeleton's shape so it is well-formed enough to be judged."
        )
        return 1
    substantive = [
        rule
        for rule in ("R05_RIVALS_STATED", "R06_DISCRIMINATOR_DISTINGUISHES",
                     "R07_DISCRIMINATOR_OBSERVED", "R14_PREDICTIONS_RESOLVED",
                     "R15_RIVAL_ELIMINATED", "R04_PREDICTION_COULD_FAIL",
                     "R03_PREDICTION_IN_ADVANCE")
        if any(
            rule in line
            and line.strip().startswith(("INADMISSIBLE", "UNSCORED", "REFUTED"))
            for line in output.splitlines()
        )
    ]
    print(f"killed by substantive rules: {substantive or 'NONE'}")
    if not substantive:
        print(
            "FAILED: nothing substantive rejected the skeleton. It was not "
            "promoted, but no rule about rivals, discriminators or predictions "
            "is what stopped it."
        )
        return 1

    # And the poison-control check itself has to be capable of firing.
    unsound = check_poison(
        [
            {**fake_arms[0]},
            {**fake_arms[1], "verdicts": {"PASS": 3}},
        ]
    )
    print(f"poison-check can fire: {not unsound['sound']}")
    if unsound["sound"]:
        print("FAILED: a poison arm that PASSED was reported as sound.")
        return 1

    # A difference inside the noise must not be reported as a difference.
    noisy_a = {**fake_arms[0], "oracleDecisionSeconds": _spread([10.0, 20.0])}
    noisy_b = {**fake_arms[1], "oracleDecisionSeconds": _spread([12.0, 22.0])}
    noisy = compare_pair(noisy_a, noisy_b)
    print(f"noise is not called a difference: "
          f"{noisy['lifetimeVerdict'] == 'INDISTINGUISHABLE'}")
    if noisy["lifetimeVerdict"] != "INDISTINGUISHABLE":
        print(f"FAILED: reported {noisy['lifetimeVerdict']} for a 2s gap inside "
              "a 10s spread.")
        return 1

    # ...and a real difference must still be reported.
    clean_a = {**fake_arms[0], "oracleDecisionSeconds": _spread([10.0, 10.1])}
    clean_b = {**fake_arms[1], "oracleDecisionSeconds": _spread([60.0, 60.2])}
    clean = compare_pair(clean_a, clean_b)
    print(f"a real difference is still reported: "
          f"{clean['lifetimeVerdict'] == 'DIFFERENT'}")
    if clean["lifetimeVerdict"] != "DIFFERENT":
        print(f"FAILED: reported {clean['lifetimeVerdict']} for a 50s gap "
              "inside a 0.2s spread -- the rule is now vacuous.")
        return 1

    # An unreplicated arm must block, whatever the gap looks like.
    single = compare_pair(
        {**clean_a, "n": 1, "replicated": False},
        clean_b,
    )
    print(f"n=1 blocks a conclusion: {not single['supportable']}")
    if single["supportable"]:
        print("FAILED: an arm with one run was allowed to support a difference.")
        return 1

    # A poison arm whose every run ERRORED never reached the engine. It used to
    # be scored 'failed_as_predicted', and that string goes into the one
    # judgement-bearing field the skeleton generator may fill.
    errored_poison = check_poison(
        [
            fake_arms[0],
            {**fake_arms[1], "verdicts": {"ERROR": 3}, "erroredRuns": 3},
        ]
    )
    print(f"an ERRORed poison arm is not a sound control: "
          f"{not errored_poison['sound']}")
    if errored_poison["sound"]:
        print("FAILED: a poison arm that never ran was called a control.")
        return 1

    # An arm that waits for a file and an arm that waits out a deadline differ
    # by the whole deadline even when the two processes behaved identically.
    cross = compare_pair(
        {**clean_a, "oracleSignature": ["fileAppears+settle0"]},
        {**clean_b, "oracleSignature": ["survives+settle0"]},
    )
    print(f"different oracle shapes cannot be differenced: "
          f"{not cross['supportable']}")
    if cross["supportable"]:
        print("FAILED: two arms asking different questions were differenced.")
        return 1

    # -rN reads as 'replicate' to the grouper and 'revision' to a human.
    merged = compare_pair(
        {**clean_a, "stagedPayloads": ["aa" * 32, "bb" * 32]}, clean_b
    )
    print(f"two payloads under one arm name blocks: {not merged['supportable']}")
    if merged["supportable"]:
        print("FAILED: two different payloads were treated as replicates.")
        return 1

    # THE EIGHT WAYS A BROKEN CONTROL WAS CERTIFIED SOUND.
    #
    # The "distinguishable on" branch was added because campaign 03's landscape
    # and poison arms both reported FAIL for opposite reasons. An adversarial
    # pass then constructed eight arm sets in which that branch waved through a
    # control that proved nothing -- and every one of them ended in
    # `failed_as_predicted` reaching refute.py's R12, the single rule the whole
    # poison apparatus exists to feed. Each is now a test.
    def _arm(name, **over):
        base = {
            "arm": name, "n": 3, "replicated": True, "receipts": [],
            "probeNames": [name], "verdicts": {"FAIL": 3}, "verdictStable": True,
            "exitCodes": [1, 1, 1], "distinctExitCodes": [1],
            "selfExitRate": 1.0, "faultRate": 0.0, "vetoedCount": 0,
            "levelLoadRate": 1.0, "usableRuns": 3, "erroredRuns": 0,
            "oracleSignature": ["processExit+settle0"],
            "oracleDecisionSeconds": _spread([13.0, 13.02, 13.04]),
            "isPoison": False, "stagedPayloads": [],
        }
        base.update(over)
        return base

    broken_controls = [
        ("poison loaded 1 level in 3",
         _arm("poison", isPoison=True, usableRuns=1, levelLoadRate=0.333),
         _arm("treatment")),

        ("half a second between two lucky-tight triples",
         _arm("poison", isPoison=True,
              oracleDecisionSeconds=_spread([13.0, 13.02, 13.04])),
         _arm("treatment",
              oracleDecisionSeconds=_spread([13.5, 13.52, 13.54]))),
        ("the two arms asked different questions",
         _arm("poison", isPoison=True,
              oracleSignature=["fileAppears+settle0"],
              oracleDecisionSeconds=_spread([4.0, 4.01, 4.02])),
         _arm("treatment", oracleSignature=["survives+settle0"],
              oracleDecisionSeconds=_spread([30.0, 30.01, 30.02]))),
        ("treatment ran once",
         _arm("poison", isPoison=True),
         _arm("treatment", n=1, replicated=False,
              oracleDecisionSeconds=_spread([13.5]))),
        ("poison verdicts are UNKNOWN, not FAIL",
         _arm("poison", isPoison=True, verdicts={"UNKNOWN": 3}),
         _arm("treatment", verdicts={"UNKNOWN": 3})),
        ("the POISON arm is the one that crashed",
         _arm("poison", isPoison=True, faultRate=1.0, vetoedCount=3),
         _arm("treatment")),
        ("one flaky crash in three treatment runs",
         _arm("poison", isPoison=True),
         _arm("treatment", faultRate=0.333, vetoedCount=1)),
    ]
    for label, poison_arm, treatment_arm in broken_controls:
        verdict = check_poison([treatment_arm, poison_arm])
        ok = not verdict["sound"]
        print(f"broken control refused -- {label}: {ok}")
        if not ok:
            print(f"FAILED: a control proving nothing was certified sound "
                  f"({label}).")
            failures += 1

    # An arm whose own replicates disagree may not be compared to anything.
    # This is where the "treatment hung once" case actually belongs: the poison
    # control is healthy and genuinely failed as designed, so check_poison is
    # right to allow it -- the defect is that compare_pair printed "cannot be
    # compared to anything" and then compared it.
    unstable = compare_pair(
        _arm("stable"),
        _arm("flaky", verdicts={"FAIL": 2, "UNKNOWN": 1}, verdictStable=False),
    )
    print(f"an arm whose replicates disagree blocks: "
          f"{not unstable['supportable']}")
    if unstable["supportable"]:
        print("FAILED: an arm that gave two different verdicts on identical "
              "inputs was compared to another arm anyway.")
        failures += 1

    # ...and the real campaign-03 shape must still be allowed through, or the
    # fix has simply restored the false negative it replaced.
    real = check_poison([
        _arm("landscape", faultRate=1.0, vetoedCount=3,
             oracleDecisionSeconds=_spread([11.028, 11.03, 11.03])),
        _arm("poison-c3", isPoison=True,
             oracleDecisionSeconds=_spread([12.281, 12.53, 12.53])),
    ])
    print(f"the real campaign-03 pair is still separated: {real['sound']}")
    if not real["sound"]:
        print("FAILED: the treatment crashing 3/3 against a clean control is "
              "the strongest separation there is, and it was rejected.")
        failures += 1

    if failures:
        print(f"\n{failures} FAILED")
        return 1
    print("\nall self-checks held")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=pathlib.Path, help="probe-run directory")
    parser.add_argument("--json-out", type=pathlib.Path)
    parser.add_argument("--emit-finding", type=pathlib.Path)
    parser.add_argument("--claim", default="TODO: state the one assertion.")
    parser.add_argument("--claim-id", default="TODO-claim-id")
    parser.add_argument("--date", default="2026-08-02")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)

    if args.self_check:
        return self_check()
    if not args.runs:
        parser.error("--runs is required unless --self-check is given")

    try:
        receipts = load_receipts(args.runs)
        report = build_report(receipts)
    except CompareError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    print(render(report))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {args.json_out}")

    if args.emit_finding:
        skeleton = emit_finding_skeleton(
            report, args.claim_id, args.claim, args.date
        )
        args.emit_finding.parent.mkdir(parents=True, exist_ok=True)
        args.emit_finding.write_text(
            json.dumps(skeleton, indent=2) + "\n", encoding="utf-8"
        )
        print(f"wrote {args.emit_finding}")
        print(
            "This skeleton is NOT a finding. Its rivals, discriminator and "
            "predictions are TODO, and the refuter will find it INADMISSIBLE "
            "until a human replaces them."
        )

    return 0 if report["usableAsEvidence"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
