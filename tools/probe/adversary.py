#!/usr/bin/env python3
"""The adversary half of the refutation stage: brief it, merge it, audit it.

`refute.py` is mechanical. It can see that a residual and a discriminator name
the same mechanism STRING; it cannot see that two different strings are the same
question. That gap needs a reader, and a reader with a specific job: kill the
claim. This module is the harness around that reader.

Three things it does, all callable from an unattended loop:

  --brief FINDING            render ADVERSARY-PROMPT.md against a finding, with
                             the finding embedded and the admissibility report
                             already run, ready to hand to a refuting agent.

  --merge FINDING --attack A the refuter returns an attack report; this folds
                             its proposed rivals and residuals back into the
                             finding so refute.py can re-adjudicate. That is what
                             makes the loop close: a named rival with no observed
                             discriminator turns a SURVIVED into an UNSCORED, and
                             the loop then has to go and make the observation.

  --audit --ledger L         the check on the checker.

Why the audit exists
--------------------
A refuter that never kills anything is not a refuter, it is a rubber stamp, and
a rubber stamp is worse than no stage at all because it launders confidence. So
the kill rate is tracked and the stage reports on ITSELF:

    kill rate below the floor    ADVERSARY_SUSPECT - it is rubber-stamping
    kill rate above the ceiling  ADVERSARY_SUSPECT - it kills everything, which
                                 is equally uninformative and usually means the
                                 rules are miscalibrated, not that every finding
                                 is bad
    UNSCORED share too high      LOOP_NOT_OBSERVING - the discovery half is
                                 producing claims it never tests. This is a
                                 different disease and it needs a different fix,
                                 so it gets its own name.
    a rule that has never fired  reported. Not a failure - a rule can be
                                 correct and simply unexercised - but a rule
                                 that has never fired across hundreds of
                                 adjudications is a rule nobody has proven can.
                                 refute_tests.py proves each one can fire; this
                                 reports whether real work ever made it.

Both bounds are checked only once the window holds enough adjudications, because
a kill rate over three findings is noise.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import refute  # noqa: E402

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "ADVERSARY-PROMPT.md"
# The prompt file carries this repository's documentation header, which is for
# readers of the repo and not for the refuter. Everything above the marker is
# stripped so the brief starts on its first real instruction.
PROMPT_MARKER = "<!-- PROMPT BEGINS -->"

KILLING_VERDICTS = {refute.REFUTED, refute.INADMISSIBLE}

DEFAULT_WINDOW = 25
DEFAULT_MIN_ADJUDICATIONS = 10
DEFAULT_KILL_FLOOR = 0.20
DEFAULT_KILL_CEILING = 0.95
DEFAULT_UNSCORED_CEILING = 0.80

ATTACK_NAMES = ["RIVAL", "NON_DISCRIMINATING_EVIDENCE",
                "RESIDUAL_TOUCHES_DISCRIMINATOR", "SAMPLE", "INSTRUMENT",
                "SCOPE_CREEP"]

ATTACK_REPORT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "onslaught://probe/attack-report-1.json",
    "type": "object",
    "required": ["findingId", "adversary", "attacks", "conclusion"],
    "properties": {
        "findingId": {"type": "string", "minLength": 3},
        "adversary": {"type": "string", "minLength": 2,
                      "description": "who or what ran the attack"},
        "conclusion": {"enum": ["KILL", "WEAKEN", "NO_FINDING", "NOT_RUN"]},
        "proposedWeakening": {
            "type": "string",
            "description": "required when any attack returns WEAKEN: the "
                           "narrower claim that would survive"},
        "attacks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["attack", "verdict", "statement"],
                "properties": {
                    "attack": {"enum": ATTACK_NAMES},
                    "verdict": {"enum": ["KILL", "WEAKEN", "NO_FINDING",
                                         "NOT_RUN"]},
                    "statement": {"type": "string", "minLength": 8},
                    "cite": {"type": "string"},
                    "proposedRival": {"type": "object"},
                    "proposedResidual": {"type": "object"},
                },
            },
        },
    },
}


# ---------------------------------------------------------------------------
# Brief
# ---------------------------------------------------------------------------

def render_brief(finding: dict, report: dict) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    if PROMPT_MARKER in template:
        template = template.split(PROMPT_MARKER, 1)[1].lstrip("\n")
    claim = finding.get("claim") or {}
    substitutions = {
        "FINDING_ID": str(finding.get("id")),
        "CLAIM": str(claim.get("statement")),
        "CLAIM_GRADE": str(claim.get("grade")),
        "FINDING_KIND": str(finding.get("findingKind")),
        "SOURCE_NOTE": str(finding.get("sourceNote") or "(none)"),
        "FINDING_JSON": json.dumps(finding, indent=2),
        "REFUTE_REPORT": refute.render(report),
        "ATTACK_REPORT_SCHEMA": json.dumps(example_attack_report(finding), indent=2),
    }
    for key, value in substitutions.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def example_attack_report(finding: dict) -> dict:
    """The shape the refuter must return, spelled out rather than described.

    A schema in prose gets paraphrased; a filled-in example gets copied.
    """
    return {
        "findingId": finding.get("id"),
        "adversary": "<model or agent id>",
        "attacks": [
            {"attack": "RIVAL",
             "verdict": "KILL | WEAKEN | NO_FINDING | NOT_RUN",
             "statement": "what you found",
             "cite": "file:line, VA, capture id, or offset",
             "proposedRival": {
                 "id": "rival-<slug>",
                 "statement": "the competing explanation",
                 "indistinguishableOn": [
                     "every observation in the record that is true under both"],
                 "discriminator": {
                     "description": "the observation whose outcome differs",
                     "mechanism": ["subsystem.part"],
                     "expectedUnderClaim": "",
                     "expectedUnderRival": "",
                     "status": "not_observed",
                     "outcome": "none",
                     "evidenceRef": []}}},
            *({"attack": name,
               "verdict": "KILL | WEAKEN | NO_FINDING | NOT_RUN",
               "statement": "",
               "cite": ""} for name in ATTACK_NAMES[1:]),
        ],
        "proposedWeakening": "required if any verdict is WEAKEN",
        "conclusion": "KILL | WEAKEN | NO_FINDING",
    }


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def merge_attack(finding: dict, attack_report: dict) -> tuple[dict, list[str]]:
    """Fold the refuter's proposals into the finding. Returns (merged, notes).

    Nothing is dropped and nothing is auto-resolved. A merged rival arrives with
    `status: not_observed` unless the refuter observed it, which is exactly what
    should happen: naming a live rival you have not eliminated moves the finding
    to UNSCORED and sends the loop to make the observation. That is the stage
    doing its job, not a defect.
    """
    merged = json.loads(json.dumps(finding))
    notes: list[str] = []

    existing_rivals = {r.get("id") for r in merged.get("rivals", [])}
    existing_residuals = {r.get("id") for r in merged.get("residuals", [])}

    for attack in attack_report.get("attacks", []):
        rival = attack.get("proposedRival")
        if rival:
            if rival.get("id") in existing_rivals:
                notes.append(f"rival {rival['id']} already present, not merged")
            else:
                merged.setdefault("rivals", []).append(rival)
                existing_rivals.add(rival.get("id"))
                notes.append(f"merged rival {rival.get('id')} from "
                             f"{attack.get('attack')}")
        residual = attack.get("proposedResidual")
        if residual:
            if residual.get("id") in existing_residuals:
                notes.append(f"residual {residual['id']} already present")
            else:
                merged.setdefault("residuals", []).append(residual)
                existing_residuals.add(residual.get("id"))
                notes.append(f"merged residual {residual.get('id')} from "
                             f"{attack.get('attack')}")

    provenance = merged.setdefault("_attacks", [])
    provenance.append({
        "adversary": attack_report.get("adversary"),
        "conclusion": attack_report.get("conclusion"),
        "proposedWeakening": attack_report.get("proposedWeakening"),
        "verdicts": {a.get("attack"): a.get("verdict")
                     for a in attack_report.get("attacks", [])},
    })
    return merged, notes


def validate_attack_report(attack_report: dict) -> list[str]:
    errors = refute.validate(attack_report, ATTACK_REPORT_SCHEMA)
    seen = {a.get("attack") for a in attack_report.get("attacks", [])}
    missing = [name for name in ATTACK_NAMES if name not in seen]
    if missing:
        errors.append(
            f"attack report omits {missing}: every attack must be present, and "
            "one you did not run is NOT_RUN, never NO_FINDING")
    if any(a.get("verdict") == "WEAKEN" for a in attack_report.get("attacks", [])):
        if not refute.norm(attack_report.get("proposedWeakening")):
            errors.append(
                "an attack returned WEAKEN but proposedWeakening is empty: name "
                "the narrower claim that would survive")
    return errors


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def read_ledger(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def audit(rows: list[dict], *, window: int = DEFAULT_WINDOW,
          minimum: int = DEFAULT_MIN_ADJUDICATIONS,
          floor: float = DEFAULT_KILL_FLOOR,
          ceiling: float = DEFAULT_KILL_CEILING,
          unscored_ceiling: float = DEFAULT_UNSCORED_CEILING) -> dict:
    adjudications = [r for r in rows if r.get("kind", "adjudication") == "adjudication"]
    recent = adjudications[-window:]
    counts = Counter(r.get("verdict") for r in recent)
    total = len(recent)
    killed = sum(counts[v] for v in KILLING_VERDICTS)
    unscored = counts[refute.UNSCORED]

    fired = Counter()
    for row in adjudications:
        fired.update(row.get("rulesFired", []))
    all_rules = [entry["id"] for entry in refute.RULES]

    # The kill rate is computed over the SCORED adjudications only. An UNSCORED
    # verdict is not the refuter declining to kill - it is the record never
    # having been testable, and folding those into the denominator would make a
    # loop that observes nothing look like a rubber stamp. Those are different
    # diseases with different fixes, so they get different names.
    scored = total - unscored

    result = {
        "windowSize": window,
        "adjudicationsInWindow": total,
        "adjudicationsScored": scored,
        "adjudicationsTotal": len(adjudications),
        "verdictCounts": dict(counts),
        "killRate": round(killed / scored, 4) if scored else None,
        "killRateOverAll": round(killed / total, 4) if total else None,
        "unscoredRate": round(unscored / total, 4) if total else None,
        "killFloor": floor,
        "killCeiling": ceiling,
        "unscoredCeiling": unscored_ceiling,
        "ruleFireCounts": {rule: fired.get(rule, 0) for rule in all_rules},
        "rulesNeverFired": [rule for rule in all_rules if not fired.get(rule)],
        "status": "OK",
        "reasons": [],
    }

    if total < minimum:
        result["status"] = "INSUFFICIENT_DATA"
        result["reasons"].append(
            f"only {total} adjudication(s) in the window; a kill rate needs at "
            f"least {minimum} before it means anything")
        return result

    if unscored / total > unscored_ceiling:
        # Checked FIRST and short-circuiting, because with almost nothing
        # testable the kill rate carries no information about the refuter.
        result["status"] = "LOOP_NOT_OBSERVING"
        result["reasons"].append(
            f"{unscored / total:.0%} of adjudications are UNSCORED: the "
            "discovery half is producing claims it never tests. This is not an "
            "adversary problem - the loop needs to go and observe.")
        result["reasons"].append(
            f"kill rate not judged: only {scored} of {total} adjudications in "
            "the window were testable at all")
        return result

    if scored < minimum:
        result["status"] = "INSUFFICIENT_DATA"
        result["reasons"].append(
            f"only {scored} scored adjudication(s) in the window; a kill rate "
            f"needs at least {minimum} before it means anything")
        return result

    rate = killed / scored
    if rate < floor:
        result["status"] = "ADVERSARY_SUSPECT"
        result["reasons"].append(
            f"kill rate {rate:.0%} is below the floor of {floor:.0%}: the stage "
            "is passing nearly everything, which is what a rubber stamp looks "
            "like from the outside")
    elif rate > ceiling:
        result["status"] = "ADVERSARY_SUSPECT"
        result["reasons"].append(
            f"kill rate {rate:.0%} is above the ceiling of {ceiling:.0%}: the "
            "stage is killing nearly everything, which carries as little "
            "information as passing everything and usually means the rules are "
            "miscalibrated")
    return result


def render_audit(result: dict) -> str:
    lines = [f"adjudications : {result['adjudicationsInWindow']} in window "
             f"(of {result['adjudicationsTotal']} total), "
             f"{result['adjudicationsScored']} scored",
             f"verdicts      : {result['verdictCounts']}"]
    if result["killRate"] is not None:
        lines.append(f"kill rate     : {result['killRate']:.0%} of scored "
                     f"(floor {result['killFloor']:.0%}, "
                     f"ceiling {result['killCeiling']:.0%})")
        lines.append(f"unscored rate : {result['unscoredRate']:.0%} "
                     f"(ceiling {result['unscoredCeiling']:.0%})")
    never = result["rulesNeverFired"]
    if never:
        lines.append(f"never fired   : {len(never)} rule(s) - {', '.join(never)}")
        lines.append("                (not a failure; refute_tests.py proves each "
                     "one CAN fire)")
    lines.append("")
    for reason in result["reasons"]:
        lines.append(f"  ! {reason}")
    lines.append("")
    lines.append(f"AUDIT: {result['status']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--brief", type=Path, metavar="FINDING",
                        help="render the adversary brief for a finding")
    parser.add_argument("--merge", type=Path, metavar="FINDING",
                        help="fold an attack report back into a finding")
    parser.add_argument("--attack", type=Path, metavar="ATTACK_REPORT")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--ledger", type=Path, default=refute.DEFAULT_LEDGER)
    parser.add_argument("--record-attack", type=Path, metavar="ATTACK_REPORT",
                        help="append an attack report's conclusion to the ledger")
    parser.add_argument("-o", "--out", type=Path)
    parser.add_argument("--window", type=int, default=DEFAULT_WINDOW)
    parser.add_argument("--min-adjudications", type=int,
                        default=DEFAULT_MIN_ADJUDICATIONS)
    parser.add_argument("--kill-floor", type=float, default=DEFAULT_KILL_FLOOR)
    parser.add_argument("--kill-ceiling", type=float, default=DEFAULT_KILL_CEILING)
    parser.add_argument("--schema", action="store_true",
                        help="print the attack report schema and exit")
    arguments = parser.parse_args(argv)

    if arguments.schema:
        print(json.dumps(ATTACK_REPORT_SCHEMA, indent=2))
        return 0

    if arguments.brief:
        finding = json.loads(arguments.brief.read_text(encoding="utf-8"))
        report = refute.adjudicate(finding)
        text = render_brief(finding, report)
        if arguments.out:
            arguments.out.parent.mkdir(parents=True, exist_ok=True)
            arguments.out.write_text(text, encoding="utf-8")
        else:
            print(text)
        return 0

    if arguments.merge:
        if not arguments.attack:
            parser.error("--merge needs --attack")
        finding = json.loads(arguments.merge.read_text(encoding="utf-8"))
        attack_report = json.loads(arguments.attack.read_text(encoding="utf-8"))
        errors = validate_attack_report(attack_report)
        if errors:
            for error in errors:
                print(f"attack report rejected: {error}", file=sys.stderr)
            return 4
        merged, notes = merge_attack(finding, attack_report)
        for note in notes:
            print(f"  {note}", file=sys.stderr)
        payload = json.dumps(merged, indent=2)
        if arguments.out:
            arguments.out.parent.mkdir(parents=True, exist_ok=True)
            arguments.out.write_text(payload, encoding="utf-8")
            print(f"merged -> {arguments.out}", file=sys.stderr)
        else:
            print(payload)
        return 0

    if arguments.record_attack:
        attack_report = json.loads(
            arguments.record_attack.read_text(encoding="utf-8"))
        arguments.ledger.parent.mkdir(parents=True, exist_ok=True)
        with arguments.ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "kind": "attack",
                "findingId": attack_report.get("findingId"),
                "adversary": attack_report.get("adversary"),
                "conclusion": attack_report.get("conclusion"),
                "verdicts": {a.get("attack"): a.get("verdict")
                             for a in attack_report.get("attacks", [])},
            }) + "\n")
        return 0

    if arguments.audit:
        rows = read_ledger(arguments.ledger)
        result = audit(rows, window=arguments.window,
                       minimum=arguments.min_adjudications,
                       floor=arguments.kill_floor, ceiling=arguments.kill_ceiling)
        result["ledger"] = str(arguments.ledger)
        print(render_audit(result))
        if arguments.out:
            arguments.out.parent.mkdir(parents=True, exist_ok=True)
            arguments.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        # INSUFFICIENT_DATA is not a pass. A loop that treats "we have not
        # measured the refuter yet" as "the refuter is fine" is the same
        # substitution this whole stage exists to prevent.
        return 0 if result["status"] == "OK" else 1

    parser.error("one of --brief, --merge, --record-attack, --audit or --schema")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
