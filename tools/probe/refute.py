#!/usr/bin/env python3
"""The refutation stage: decide whether a probe finding may be promoted.

Why this exists
---------------
On 2026-07-31 the skin-weight law was derived, byte-verified against the
pristine specimen (`74154bfa...`), independently reproduced over all 3,203
shipped skinned vertices, and written up with a stated-in-advance prediction
table in which every row came back MATCH. It was wrong. The executed law is
`p' = 2*T[s1]*p + 1*T[s2]*p` - weights (0, 2/3, 1/3) - and the note's
"weight = multiplicity/3" disagrees with it on 25.3 % of all skinned vertices.
Only a live capture caught it, hours later.

Nothing in that note was false. Every byte fact in it still stands. The defect
was that the byte facts were true under BOTH laws, because the 1/3 lives in the
palette either way, and the one place the two laws differ - the shader's final
combine - was listed in the note's own Residual section as unresolved and "not
load-bearing for the law". The author confirmed real facts and then accepted an
inference those facts did not license.

Automated discovery without automated falsification produces confident garbage
at scale. This stage is the falsification half. A discovery loop runs every
finding through it and may promote ONLY what exits 0.

What it enforces, in one paragraph
----------------------------------
A finding is not admissible unless it names at least one live RIVAL explanation,
and for each rival a DISCRIMINATOR - an observation whose outcome differs under
the claim and under the rival. Evidence that both explanations predict is not
evidence for either. Every test the finding ran must have had its result written
down BEFORE the run, and must name the concrete outcome that would have killed
the claim. Every residual carries a `blocksClaim` flag, and a residual that
names the same mechanism as a discriminator may not be waved through as
non-blocking - that single rule is a direct transcription of the 2026-07-31
failure.

The four verdicts, and why UNSCORED is one of them
--------------------------------------------------
    REFUTED       a prediction came back mismatch, or a discriminator landed on
                  the rival's side. The claim is dead. This is a GOOD outcome.
    INADMISSIBLE  the record cannot be judged: no rival, no falsifier, a
                  discriminator that does not discriminate, a residual that
                  contradicts its own non-blocking flag. Not a finding yet.
    UNSCORED      admissible, and a required observation WAS NOT MADE. The
                  discriminator was not observed, a prediction was not run, the
                  instrument never demonstrated it can produce a negative.
    SURVIVED      admissible, every prediction resolved, every rival eliminated
                  by an observed discriminator, control arm behaved.

UNSCORED exists because "I found no problem" and "I was unable to look" are the
same sentence from a model. `tools/score_frontend_capture.py` already returns
UNSCORED rather than PASS when its reference set is absent, for exactly this
reason, and its docstring is the canonical statement of the rule. This tool
follows that precedent and hardens it in one place: score_frontend_capture exits
0 on UNSCORED because a human reads its output. Here the caller is an
unattended loop that promotes on exit 0, so UNSCORED exits NON-ZERO. A loop must
never be able to mistake an unmade observation for a survived claim.

    exit 0  SURVIVED       may be promoted
    exit 1  REFUTED        kill it
    exit 2  INADMISSIBLE   send it back to the author
    exit 3  UNSCORED       go and make the observation
    exit 4  usage/IO error

How a claim survived is recorded, not merely that it did
--------------------------------------------------------
A SURVIVED verdict carries a `survival` block: the evidence grade ceiling and
which evidence set it, the summed sample size and independent replicate count of
the discriminating chain, every rival with the observation that eliminated it,
and the `stillOverturnedBy` list copied forward verbatim. A survival with n=1,
replicates=1 and grade INFERRED is a survival, and it says so.

Structure comes from finding_schema.json
----------------------------------------
The schema file is the single source of truth for fields and enums; this module
loads it and drives R01 from it rather than restating the field list. Cardinality
rules that carry a diagnosis ("you stated no rival") are named rules here instead
of `minItems` there, so the report tells the author which rule fired.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SCHEMA_PATH = HERE / "finding_schema.json"
FIXTURES = HERE / "fixtures"
DEFAULT_LEDGER = REPO_ROOT / "local-lab" / "probe" / "refutation-ledger.jsonl"

SURVIVED = "SURVIVED"
REFUTED = "REFUTED"
INADMISSIBLE = "INADMISSIBLE"
UNSCORED = "UNSCORED"

EXIT_CODE = {SURVIVED: 0, REFUTED: 1, INADMISSIBLE: 2, UNSCORED: 3}

# REFUTED outranks INADMISSIBLE deliberately. A self-reported mismatch is
# decisive and it points the safe way (the claim dies); admissibility is about
# whether something may be PROMOTED, and a dead claim is not going to be.
PRECEDENCE = [REFUTED, INADMISSIBLE, UNSCORED]

# Strongest first, for display and for tie-breaks.
GRADES = ["EXECUTED", "MEASURED_STATIC", "CORPUS", "DERIVED", "INFERRED", "ASSERTED"]

# Comparison is by TIER, not by list position. MEASURED_STATIC and CORPUS are
# both direct observation of shipped bytes and neither is weaker than the other;
# ranking them would make the grade-ceiling rule fire on noise. What the rule
# must catch is a claim graded as OBSERVED whose discriminating step was only
# reasoned - tier 0/1 against tier 2/3/4. That is the 2026-07-31 shape.
GRADE_TIER = {"EXECUTED": 0, "MEASURED_STATIC": 1, "CORPUS": 1,
              "DERIVED": 2, "INFERRED": 3, "ASSERTED": 4}


def grade_rank(grade: str) -> tuple[int, int]:
    return (GRADE_TIER.get(grade, 99), GRADES.index(grade) if grade in GRADES else 99)

# Strings people write when they have no falsifier but need the field filled in.
EMPTY_FALSIFIERS = {
    "", "n/a", "na", "none", "nothing", "unknown", "tbd", "-", "?",
    "nothing would", "no test", "not applicable",
}


def norm(text: Any) -> str:
    """Whitespace-collapsed, lowercased, terminal-punctuation-stripped."""
    return re.sub(r"\s+", " ", str(text or "")).strip().rstrip(".;,").lower()


# ---------------------------------------------------------------------------
# A very small JSON Schema subset, so this tool has no third-party dependency.
# Supported: type, required, properties, items, enum, const, minItems,
# minLength, minimum. That is exactly what finding_schema.json uses, and
# unsupported keywords are ignored rather than silently "passed".
# ---------------------------------------------------------------------------

TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "number": (int, float),
    "integer": int,
}


def validate(instance: Any, schema: dict, where: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        python_type = TYPES[expected]
        # bool is a subclass of int in Python; an integer field must not accept True.
        if expected in ("integer", "number") and isinstance(instance, bool):
            return [f"{where}: expected {expected}, got boolean"]
        if not isinstance(instance, python_type):
            return [f"{where}: expected {expected}, got {type(instance).__name__}"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{where}: must be {schema['const']!r}, got {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{where}: {instance!r} is not one of {schema['enum']}")
    if "minLength" in schema and isinstance(instance, str):
        if len(instance.strip()) < schema["minLength"]:
            errors.append(
                f"{where}: needs at least {schema['minLength']} characters, "
                f"got {len(instance.strip())}")
    if "minimum" in schema and isinstance(instance, (int, float)):
        if instance < schema["minimum"]:
            errors.append(f"{where}: must be >= {schema['minimum']}, got {instance}")
    if "minItems" in schema and isinstance(instance, list):
        if len(instance) < schema["minItems"]:
            errors.append(
                f"{where}: needs at least {schema['minItems']} item(s), "
                f"got {len(instance)}")

    if isinstance(instance, dict):
        for name in schema.get("required", []):
            if name not in instance:
                errors.append(f"{where}: missing required field '{name}'")
        for name, subschema in schema.get("properties", {}).items():
            if name in instance:
                errors.extend(validate(instance[name], subschema, f"{where}.{name}"))
    if isinstance(instance, list) and "items" in schema:
        for index, item in enumerate(instance):
            errors.extend(validate(item, schema["items"], f"{where}[{index}]"))
    return errors


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Admissibility rules. Each returns a list of (severity, message) pairs.
# ---------------------------------------------------------------------------

RULES: list[dict[str, str]] = []


def rule(rule_id: str, severity: str, headline: str):
    def register(function):
        RULES.append({"id": rule_id, "severity": severity, "headline": headline,
                      "doc": (function.__doc__ or "").strip()})
        function.rule_id = rule_id
        function.default_severity = severity
        return function
    return register


def live_rivals(finding: dict) -> list[dict]:
    return [r for r in finding.get("rivals", []) if not r.get("strawman")]


def advance_predictions(finding: dict) -> list[dict]:
    return [p for p in finding.get("predictions", [])
            if p.get("predictedInAdvance") is True and norm(p.get("statedAt"))]


def evidence_by_id(finding: dict) -> dict[str, dict]:
    return {e.get("id"): e for e in finding.get("evidence", []) if e.get("id")}


def unique(items: Iterable[str]) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


def discriminating_chain(finding: dict) -> list[str]:
    """Evidence ids that actually CHOSE between the claim and a rival.

    Only evidence behind an OBSERVED rival discriminator qualifies. A prediction
    that came back match is corroboration, not discrimination - that distinction
    is the entire lesson of 2026-07-31, where five predictions matched and every
    one of them was equally true under the rival law. Corroboration must never
    raise a claim's grade.
    """
    refs: list[str] = []
    for rival in live_rivals(finding):
        disc = rival.get("discriminator") or {}
        if disc.get("status") == "observed":
            refs.extend(disc.get("evidenceRef", []) or [])
    return unique(refs)


def corroborating_chain(finding: dict) -> list[str]:
    """Evidence behind predictions that resolved. Reported, never load-bearing."""
    refs: list[str] = []
    for prediction in finding.get("predictions", []):
        if prediction.get("result") in ("match", "mismatch"):
            refs.extend(prediction.get("evidenceRef", []) or [])
    return unique(refs)


@rule("R01_SCHEMA", INADMISSIBLE, "record validates against finding_schema.json")
def r01_schema(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """Structure and enums come from the schema file, not from this module."""
    return [(INADMISSIBLE, message) for message in validate(finding, cfg["schema"])]


@rule("R02_PREDICTION_PRESENT", INADMISSIBLE, "at least one test was run")
def r02_prediction_present(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """A finding with no test is an opinion."""
    if not finding.get("predictions"):
        return [(INADMISSIBLE, "no predictions: nothing was tested")]
    return []


@rule("R03_PREDICTION_IN_ADVANCE", INADMISSIBLE,
      "at least one prediction was written down before the run")
def r03_in_advance(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """A result explained after the fact is not a prediction. `statedAt` must
    name where it was written down - a commit, a note, a timestamp."""
    predictions = finding.get("predictions", [])
    if not predictions:
        return []
    if not advance_predictions(finding):
        posthoc = ", ".join(p.get("id", "?") for p in predictions)
        return [(INADMISSIBLE,
                 "every prediction is post-hoc or has no statedAt "
                 f"({posthoc}): nothing was predicted in advance")]
    return []


@rule("R04_PREDICTION_COULD_FAIL", INADMISSIBLE,
      "every prediction names an outcome that would have killed the claim")
def r04_could_fail(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """`wouldFalsifyIf` must be a real, distinct outcome. A falsifier equal to
    the expectation, or a filler like 'n/a', means the test cannot fail."""
    problems = []
    for prediction in finding.get("predictions", []):
        pid = prediction.get("id", "?")
        falsifier = norm(prediction.get("wouldFalsifyIf"))
        if falsifier in EMPTY_FALSIFIERS:
            problems.append((INADMISSIBLE,
                             f"prediction {pid}: wouldFalsifyIf is empty or filler "
                             f"({prediction.get('wouldFalsifyIf')!r})"))
        elif falsifier == norm(prediction.get("expected")):
            problems.append((INADMISSIBLE,
                             f"prediction {pid}: wouldFalsifyIf is identical to "
                             "expected, so no outcome could have failed it"))
    return problems


@rule("R05_RIVALS_STATED", INADMISSIBLE,
      "at least one live competing explanation is named")
def r05_rivals(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """THE 2026-07-31 RULE. The skin-weight note named no alternative to
    'weight = multiplicity/3', so nothing in it was ever asked to choose between
    that law and the (0, 2/3, 1/3) law the GPU actually executes."""
    rivals = finding.get("rivals", [])
    if not rivals:
        return [(INADMISSIBLE,
                 "no rivals stated: the record never asks what else would "
                 "produce this same evidence")]
    if not live_rivals(finding):
        return [(INADMISSIBLE,
                 f"all {len(rivals)} rival(s) are flagged strawman: no live "
                 "alternative was considered")]
    claim = norm((finding.get("claim") or {}).get("statement"))
    return [(INADMISSIBLE,
             f"rival {r.get('id', '?')}: restates the claim rather than "
             "opposing it")
            for r in live_rivals(finding) if norm(r.get("statement")) == claim]


@rule("R06_DISCRIMINATOR_DISTINGUISHES", INADMISSIBLE,
      "each rival's discriminator predicts different things under claim and rival")
def r06_discriminates(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """The shape that beat us: evidence that is REAL but does not CHOOSE. If the
    claim and the rival predict the same observation, observing it is not
    evidence for either, however carefully it was measured."""
    problems = []
    for rival in live_rivals(finding):
        disc = rival.get("discriminator") or {}
        under_claim = norm(disc.get("expectedUnderClaim"))
        under_rival = norm(disc.get("expectedUnderRival"))
        if under_claim and under_claim == under_rival:
            problems.append((INADMISSIBLE,
                             f"rival {rival.get('id', '?')}: discriminator predicts "
                             f"the same outcome ({disc.get('expectedUnderClaim')!r}) "
                             "under both - it does not discriminate"))
        indistinguishable = {norm(x) for x in disc.get("mechanism", [])} & {
            norm(x) for x in rival.get("indistinguishableOn", [])}
        if indistinguishable:
            problems.append((INADMISSIBLE,
                             f"rival {rival.get('id', '?')}: the discriminator's "
                             "mechanism is also listed under indistinguishableOn "
                             f"({sorted(indistinguishable)})"))
    return problems


@rule("R07_DISCRIMINATOR_OBSERVED", UNSCORED,
      "each discriminating observation was actually made")
def r07_observed(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """Naming the right test and not running it is UNSCORED, never SURVIVED.
    This is where a correctly-steelmanned 2026-07-31 record lands: it knew the
    shader's final combine would decide, and it had not read the shader."""
    problems = []
    for rival in live_rivals(finding):
        disc = rival.get("discriminator") or {}
        status = disc.get("status")
        rid = rival.get("id", "?")
        if status == "observed":
            if not (disc.get("evidenceRef") or []):
                problems.append((UNSCORED,
                                 f"rival {rid}: discriminator claims status "
                                 "'observed' but references no evidence"))
        elif status == "unobservable":
            problems.append((UNSCORED,
                             f"rival {rid}: discriminator is declared "
                             "unobservable - the claim cannot be separated from "
                             "this rival by any observation offered"))
        else:
            problems.append((UNSCORED,
                             f"rival {rid}: discriminator not observed "
                             f"(status={status!r}) - {disc.get('description', '')}"))
    return problems


@rule("R08_RESIDUAL_TOUCHES_DISCRIMINATOR", INADMISSIBLE,
      "no residual waves away a mechanism a discriminator depends on")
def r08_residual(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """THE OTHER 2026-07-31 RULE, and the exact smell to catch. The note's own
    Residual section said the shader's final-combine opcodes 'do not decode
    cleanly, and are not load-bearing for the law'. The final combine was the
    ONLY thing that separated the two laws. A residual whose mechanism is also a
    discriminator's mechanism cannot be marked blocksClaim=false."""
    discriminator_mechanisms: dict[str, list[str]] = {}
    for rival in live_rivals(finding):
        disc = rival.get("discriminator") or {}
        for mechanism in disc.get("mechanism", []):
            discriminator_mechanisms.setdefault(norm(mechanism), []).append(
                rival.get("id", "?"))
    problems = []
    for residual in finding.get("residuals", []):
        if residual.get("blocksClaim") is not False:
            continue
        for mechanism in residual.get("mechanism", []):
            owners = discriminator_mechanisms.get(norm(mechanism))
            if owners:
                problems.append((INADMISSIBLE,
                                 f"residual {residual.get('id', '?')} is marked "
                                 f"blocksClaim=false but names mechanism "
                                 f"'{mechanism}', which rival(s) "
                                 f"{sorted(set(owners))} depend on to be "
                                 "discriminated"))
    return problems


@rule("R09_GRADE_CEILING", INADMISSIBLE,
      "the claim is not graded above its own discriminating evidence")
def r09_grade(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """The 2026-07-31 headline read MEASURED. Its byte reads were measured; the
    step from those bytes to the weight law was inferred, and that step is the
    one that was wrong. A claim inherits the WEAKEST grade in the chain that
    actually chose between it and its rivals."""
    claim_grade = (finding.get("claim") or {}).get("grade")
    if claim_grade not in GRADES:
        return []
    known = evidence_by_id(finding)
    missing = [ref for ref in discriminating_chain(finding) + corroborating_chain(finding)
               if ref not in known]
    if missing:
        return [(INADMISSIBLE,
                 f"evidenceRef names no evidence record: {sorted(missing)}")]
    chain = discriminating_chain(finding)
    if not chain:
        return [(UNSCORED,
                 "grade ceiling unverifiable: no OBSERVED discriminator "
                 "references any evidence, so nothing here chose this claim over "
                 "an alternative. Matching predictions do not set the grade.")]
    weakest_id = max(chain, key=lambda ref: grade_rank(known[ref]["grade"]))
    weakest = known[weakest_id]["grade"]
    if grade_rank(claim_grade)[0] < grade_rank(weakest)[0]:
        return [(INADMISSIBLE,
                 f"claim is graded {claim_grade} but the weakest evidence in its "
                 f"discriminating chain is {weakest} (evidence '{weakest_id}'): "
                 f"the strongest honest grade is {weakest}")]
    return []


@rule("R10_SCOPE_AND_SAMPLE", INADMISSIBLE,
      "the population, the coverage and the exclusions are all stated")
def r10_scope(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """'Shipped PMS2 carries no weight arrays - spot-checked on m_mgrunt only'
    was a real line in the superseded note. An empty notCovered list on a claim
    that ranges over a population says the author did not look for an exclusion."""
    problems: list[tuple[str, str]] = []
    scope = finding.get("scope") or {}
    if not scope.get("notCovered"):
        problems.append((INADMISSIBLE,
                         "scope.notCovered is empty: name what this claim does "
                         "NOT cover, or say why nothing is excluded"))
    for item in finding.get("evidence", []):
        sample = item.get("sample") or {}
        if not isinstance(sample.get("n"), int) or sample.get("n") < 1:
            problems.append((INADMISSIBLE,
                             f"evidence {item.get('id', '?')}: sample.n must be "
                             f"at least 1, got {sample.get('n')!r}"))
    known = evidence_by_id(finding)
    chain = [ref for ref in discriminating_chain(finding) if ref in known]
    if chain:
        total = sum(int((known[ref].get("sample") or {}).get("n", 0)) for ref in chain)
        if total < cfg["min_sample_n"]:
            problems.append((UNSCORED,
                             f"discriminating sample is n={total}, below the "
                             f"floor of {cfg['min_sample_n']}"))
    return problems


def weakest_grade(known: dict[str, dict], chain: list[str]) -> tuple[str | None, str | None]:
    if not chain:
        return None, None
    weakest_id = max(chain, key=lambda ref: grade_rank(known[ref]["grade"]))
    return known[weakest_id]["grade"], weakest_id


@rule("R11_SPECIMEN_NAMED", INADMISSIBLE,
      "byte evidence names its specimen file and hash")
def r11_specimen(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """Standing project rule: read byte evidence from a pristine specimen, and
    name the specimen file and hash in every byte finding."""
    problems = []
    for item in finding.get("evidence", []):
        specimen = item.get("specimen") or {}
        eid = item.get("id", "?")
        if item.get("grade") == "MEASURED_STATIC" and not specimen:
            problems.append((INADMISSIBLE,
                             f"evidence {eid} is MEASURED_STATIC but names no "
                             "specimen"))
            continue
        if specimen.get("path") and not norm(specimen.get("sha256")):
            problems.append((INADMISSIBLE,
                             f"evidence {eid}: specimen '{specimen['path']}' has "
                             "no sha256"))
    return problems


@rule("R12_CONTROL_CAN_FAIL", UNSCORED,
      "an instrument-derived finding proves its instrument can report a negative")
def r12_control(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """Ask whether a check is CAPABLE of failing before trusting that it passed.
    An instrument that reports clean no matter what is indistinguishable from a
    clean result, so a probe we built owes a control arm that produced the
    negative outcome it was designed to produce."""
    if finding.get("findingKind") != "instrument-derived":
        return []
    control = finding.get("poisonControl")
    if not control:
        return [(UNSCORED,
                 "instrument-derived finding with no poisonControl: the "
                 "instrument was never shown capable of a negative result")]
    result = control.get("result")
    if result == "failed_as_predicted":
        return []
    if result == "did_not_fail":
        return [(UNSCORED,
                 f"control '{control.get('id', '?')}' did not produce its "
                 "predicted negative: the instrument is blind, so its clean "
                 "readings mean nothing")]
    return [(UNSCORED,
             f"control '{control.get('id', '?')}' was not run")]


@rule("R13_OVERTURN_TEST", INADMISSIBLE,
      "a not-yet-run test that would kill the claim is named")
def r13_overturn(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """A claim no future observation could overturn is not a finding. The
    superseded note did carry this section, and it was right: its stated
    overturning test is precisely the capture that killed it hours later."""
    if not finding.get("overturnedBy"):
        return [(INADMISSIBLE,
                 "overturnedBy is empty: name a test that could still kill this")]
    return []


@rule("R16_NO_UNFILLED_PLACEHOLDERS", INADMISSIBLE,
      "no judgement-bearing field is still an unedited placeholder")
def r16_placeholders(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """A half-edited skeleton must not be scored as a finding.

    ``tools/probe/compare.py`` emits a finding pre-filled with everything the
    receipts measure and leaves the rivals, the discriminator and the
    predictions as explicit TODO text. Measured 2026-08-01: R05_RIVALS_STATED
    and R06_DISCRIMINATOR_DISTINGUISHES both PASS on that template, because a
    rival whose statement reads 'TODO: name a competing explanation' is a
    non-empty string, and two different TODO sentences are two different
    strings. The record was still caught -- by R07 and R14, which need an
    observation nobody can fake -- but two of the rules that exist to demand a
    real rival were agreeing with a placeholder.

    An author who fills in the predictions and leaves the rivals would slip
    exactly through that gap. This rule closes it: the marker is mechanical, so
    the check is mechanical.
    """

    hits: list[tuple[str, str]] = []

    def scan(node, path: str) -> None:
        if isinstance(node, str):
            if "TODO" in node:
                hits.append(
                    (INADMISSIBLE,
                     f"{path} is still a placeholder: {node[:70]!r}")
                )
        elif isinstance(node, dict):
            for key, value in node.items():
                scan(value, f"{path}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                scan(value, f"{path}[{index}]")

    # The residual that SAYS the record is an unedited skeleton is allowed to
    # say so -- it is the skeleton being honest about itself, and deleting the
    # word from it would make the record less true, not more.
    for key, value in finding.items():
        if key == "residuals":
            for index, residual in enumerate(value or ()):
                if residual.get("id") == "skeleton-not-edited":
                    continue
                scan(residual, f"$.residuals[{index}]")
            continue
        scan(value, f"${'.' + key}")
    return hits[:12]


@rule("R14_PREDICTIONS_RESOLVED", REFUTED,
      "every prediction has a recorded result, and none came back mismatch")
def r14_results(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """A mismatch refutes. A not_run or inconclusive is UNSCORED - a listed test
    that was not run is the loudest possible 'I was unable to look'."""
    problems = []
    for prediction in finding.get("predictions", []):
        pid = prediction.get("id", "?")
        result = prediction.get("result")
        if result == "mismatch":
            problems.append((REFUTED,
                             f"prediction {pid} MISMATCHED: expected "
                             f"{prediction.get('expected')!r}, observed "
                             f"{prediction.get('observed')!r}"))
        elif result in ("not_run", "inconclusive"):
            problems.append((UNSCORED,
                             f"prediction {pid} result is {result!r}"))
    return problems


@rule("R15_RIVAL_ELIMINATED", REFUTED,
      "no observed discriminator landed on a rival's side")
def r15_rival_outcome(finding: dict, cfg: dict) -> list[tuple[str, str]]:
    """If the discriminating observation matches the rival's prediction, the
    rival won. That is the stage working."""
    problems = []
    for rival in live_rivals(finding):
        disc = rival.get("discriminator") or {}
        if disc.get("status") != "observed":
            continue  # R07 owns the not-observed case.
        rid = rival.get("id", "?")
        outcome = disc.get("outcome")
        if outcome == "rival":
            problems.append((REFUTED,
                             f"rival {rid} WON its discriminator: observed "
                             f"{disc.get('expectedUnderRival')!r}, which is the "
                             "rival's prediction, not the claim's"))
        elif outcome == "ambiguous":
            problems.append((UNSCORED,
                             f"rival {rid}: discriminator was observed but the "
                             "outcome is ambiguous"))
        elif outcome == "none":
            problems.append((UNSCORED,
                             f"rival {rid}: discriminator status is 'observed' "
                             "but outcome is 'none'"))
    return problems


# REGISTERING A RULE IS NOT RUNNING IT.  The @rule decorator only adds an entry
# to RULES, which is what the ledger and the audit read; a rule missing from
# THIS list is listed everywhere, reported as "never fired", and silently never
# evaluated. Measured 2026-08-01, when R16 was added and the adjudicator went on
# reporting "11/15 rules" without it. The count assertion below is the guard.
CHECKS = [r01_schema, r02_prediction_present, r03_in_advance, r04_could_fail,
          r05_rivals, r06_discriminates, r07_observed, r08_residual, r09_grade,
          r10_scope, r11_specimen, r12_control, r13_overturn,
          r16_placeholders, r14_results, r15_rival_outcome]

_registered = {entry["id"] for entry in RULES}
_dispatched = {check.rule_id for check in CHECKS}
if _registered != _dispatched:  # pragma: no cover - import-time structural guard
    raise SystemExit(
        "refute.py is misconfigured: rules registered but never dispatched: "
        f"{sorted(_registered - _dispatched)}; dispatched but not registered: "
        f"{sorted(_dispatched - _registered)}. A rule in RULES and not in "
        "CHECKS is reported to the reader and never evaluated."
    )


# ---------------------------------------------------------------------------
# Adjudication
# ---------------------------------------------------------------------------

def survival_record(finding: dict) -> dict:
    """HOW it survived, not merely that it did."""
    known = evidence_by_id(finding)
    chain = [ref for ref in discriminating_chain(finding) if ref in known]
    corroborating = [ref for ref in corroborating_chain(finding)
                     if ref in known and ref not in chain]
    ceiling, set_by = weakest_grade(known, chain)
    samples = [(known[ref].get("sample") or {}) for ref in chain]
    return {
        "evidenceGradeCeiling": ceiling,
        "gradeSetBy": set_by,
        "discriminatingEvidence": chain,
        "corroboratingEvidence": corroborating,
        "sampleN": sum(int(s.get("n", 0)) for s in samples),
        "sampleBreakdown": [
            {"evidence": ref,
             "grade": known[ref]["grade"],
             "n": (known[ref].get("sample") or {}).get("n"),
             "units": (known[ref].get("sample") or {}).get("units"),
             "independentReplicates":
                 (known[ref].get("sample") or {}).get("independentReplicates")}
            for ref in chain],
        # The MINIMUM, not the sum. One discriminator replicated three times and
        # another observed once means the claim rests on one observation at its
        # thinnest point, and that is the number worth quoting.
        "independentReplicates": (min((int(s.get("independentReplicates", 1))
                                       for s in samples), default=0)),
        "predictionsResolved": sum(1 for p in finding.get("predictions", [])
                                   if p.get("result") in ("match", "mismatch")),
        "predictionsInAdvance": len(advance_predictions(finding)),
        "rivalsEliminated": [
            {"rival": r.get("id"),
             "statement": r.get("statement"),
             "eliminatedBy": (r.get("discriminator") or {}).get("description"),
             "observed": (r.get("discriminator") or {}).get("expectedUnderClaim"),
             "evidenceRef": (r.get("discriminator") or {}).get("evidenceRef", [])}
            for r in live_rivals(finding)],
        "openResiduals": [{"id": x.get("id"), "statement": x.get("statement"),
                           "blocksClaim": x.get("blocksClaim")}
                          for x in finding.get("residuals", [])],
        "stillOverturnedBy": finding.get("overturnedBy", []),
        "scopeNotCovered": (finding.get("scope") or {}).get("notCovered", []),
    }


def adjudicate(finding: dict, *, min_sample_n: int = 1,
               schema: dict | None = None) -> dict:
    cfg = {"schema": schema or load_schema(), "min_sample_n": min_sample_n}
    fired: list[dict] = []
    passed: list[str] = []

    schema_failed = False
    for check in CHECKS:
        if schema_failed and check is not r01_schema:
            # Downstream rules index into fields the schema just said are absent
            # or the wrong type. Reporting "no rivals stated" for a record that
            # is not even an object would be noise, so they are reported as
            # blocked rather than silently passed - never as passes.
            fired.append({"rule": check.rule_id, "severity": "BLOCKED",
                          "message": "not evaluated: R01_SCHEMA failed"})
            continue
        try:
            problems = check(finding, cfg)
        except Exception as error:  # a malformed record must not crash the loop
            problems = [(INADMISSIBLE,
                         f"rule raised {type(error).__name__}: {error}")]
        if problems:
            for severity, message in problems:
                fired.append({"rule": check.rule_id, "severity": severity,
                              "message": message})
            if check is r01_schema:
                schema_failed = True
        else:
            passed.append(check.rule_id)

    severities = {entry["severity"] for entry in fired}
    verdict = SURVIVED
    for candidate in PRECEDENCE:
        if candidate in severities:
            verdict = candidate
            break

    report = {
        "tool": "tools/probe/refute.py",
        "schemaVersion": finding.get("schemaVersion") if isinstance(finding, dict) else None,
        "findingId": finding.get("id") if isinstance(finding, dict) else None,
        "claim": (finding.get("claim") or {}).get("statement")
        if isinstance(finding, dict) else None,
        "verdict": verdict,
        "exitCode": EXIT_CODE[verdict],
        "rulesPassed": passed,
        "rulesFired": fired,
        "minSampleN": min_sample_n,
    }
    if isinstance(finding, dict) and "subject" in finding:
        report["subject"] = finding["subject"]
    if isinstance(finding, dict) and not schema_failed:
        report["survival"] = survival_record(finding)
        if verdict != SURVIVED:
            # The block is still emitted, because "how far did it get" is what
            # the author needs, but it is renamed so nobody quotes it as proof.
            report["survival"]["note"] = (
                f"verdict is {verdict}; this is the state of the record, not a "
                "survival")
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def render(report: dict) -> str:
    lines = [f"finding : {report.get('findingId')}",
             f"claim   : {report.get('claim')}", ""]
    for entry in report["rulesFired"]:
        lines.append(f"  {entry['severity']:<13} {entry['rule']:<32} "
                     f"{entry['message']}")
    if report["rulesFired"]:
        lines.append("")
    lines.append(f"  passed: {len(report['rulesPassed'])}/"
                 f"{len(CHECKS)} rules"
                 + (f" ({', '.join(report['rulesPassed'])})"
                    if report["rulesPassed"] else ""))
    survival = report.get("survival")
    if survival and report["verdict"] == SURVIVED:
        lines += [
            "",
            "SURVIVAL RECORD",
            f"  evidence grade ceiling : {survival['evidenceGradeCeiling']} "
            f"(set by '{survival['gradeSetBy']}')",
            f"  discriminating sample  : n={survival['sampleN']} total, "
            f"{survival['independentReplicates']} independent replicate(s) at "
            "the thinnest point",
        ]
        for item in survival["sampleBreakdown"]:
            lines.append(f"    - {item['evidence']}: {item['grade']}, "
                         f"n={item['n']} {item['units']}, "
                         f"{item['independentReplicates']} replicate(s)")
        lines += [
            f"  predictions in advance : {survival['predictionsInAdvance']}, "
            f"{survival['predictionsResolved']} resolved (corroboration only - "
            "these did not set the grade)",
            "  rivals eliminated      :",
        ]
        for item in survival["rivalsEliminated"]:
            lines.append(f"    - {item['rival']}: {item['eliminatedBy']}")
        lines.append("  would still overturn it:")
        for item in survival["stillOverturnedBy"]:
            lines.append(f"    - {item.get('id')}: {item.get('wouldShow')}")
        if survival["scopeNotCovered"]:
            lines.append("  NOT covered            :")
            for item in survival["scopeNotCovered"]:
                lines.append(f"    - {item}")
    lines += ["", f"VERDICT: {report['verdict']}  (exit {report['exitCode']})"]
    return "\n".join(lines)


def append_ledger(path: Path, report: dict, finding: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"kind": "adjudication",
           "findingId": report.get("findingId"),
           "verdict": report["verdict"],
           "date": finding.get("date") if isinstance(finding, dict) else None,
           "lane": finding.get("lane") if isinstance(finding, dict) else None,
           "rulesFired": sorted({e["rule"] for e in report["rulesFired"]})}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")


TEMPLATE = {
    "schemaVersion": 1,
    "id": "kebab-case-slug",
    "title": "One line. What is being claimed.",
    "date": "2026-08-02",
    "lane": "probe",
    "author": "",
    "sourceNote": "local-lab/....md",
    "findingKind": "instrument-derived",
    "claim": {
        "statement": "ONE assertion. If it needs an 'and', it is two findings.",
        "grade": "INFERRED",
        "mechanism": ["subsystem.part"],
    },
    "scope": {
        "population": "what the claim ranges over",
        "covered": "how much of it the evidence touched",
        "notCovered": ["name at least one exclusion"],
    },
    "rivals": [{
        "id": "rival-1",
        "statement": "The other explanation that produces this same evidence.",
        "indistinguishableOn": ["observations true under both"],
        "discriminator": {
            "description": "the observation whose outcome differs",
            "mechanism": ["subsystem.part"],
            "expectedUnderClaim": "what you would see if the claim holds",
            "expectedUnderRival": "what you would see if the rival holds",
            "status": "not_observed",
            "outcome": "none",
            "evidenceRef": [],
        },
    }],
    "predictions": [{
        "id": "p1",
        "statement": "what this test asserts, in one line",
        "procedure": "reproducible steps",
        "expected": "the outcome written down BEFORE the run",
        "wouldFalsifyIf": "the concrete outcome that kills the claim",
        "predictedInAdvance": True,
        "statedAt": "commit/note/timestamp where this was written down",
        "result": "not_run",
        "observed": "",
        "evidenceRef": ["e1"],
    }],
    "evidence": [{
        "id": "e1",
        "grade": "MEASURED_STATIC",
        "instrument": "tools/....py",
        "summary": "",
        "sample": {"n": 1, "units": "records", "independentReplicates": 1,
                   "sessions": 1},
        "specimen": {"path": "local-lab/safe-copy-bea-pristine/"
                             "BEA.exe.original.backup", "sha256": "74154BFA..."},
    }],
    "residuals": [{
        "id": "res-1",
        "statement": "what is still unresolved",
        "mechanism": ["subsystem.part"],
        "blocksClaim": True,
    }],
    "poisonControl": {
        "id": "control-1",
        "kind": "poison",
        "description": "an arm that SHOULD produce a negative outcome",
        "predictedOutcome": "what the control must produce for the instrument "
                            "to be capable of a negative at all",
        "observedOutcome": "",
        "result": "not_run",
    },
    "overturnedBy": [{
        "id": "kill-1",
        "procedure": "a test not yet run that would end this claim",
        "wouldShow": "what its result would demonstrate",
        "cost": "",
    }],
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("finding", nargs="?", type=Path,
                        help="a finding record JSON file")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--ledger", type=Path, nargs="?", const=DEFAULT_LEDGER,
                        help="append this adjudication to a refutation ledger "
                             f"(default {DEFAULT_LEDGER})")
    parser.add_argument("--min-sample-n", type=int, default=1,
                        help="floor on the summed discriminating sample size")
    parser.add_argument("--template", action="store_true",
                        help="print a blank finding record and exit")
    parser.add_argument("--explain", action="store_true",
                        help="print the admissibility rules and exit")
    parser.add_argument("--quiet", action="store_true")
    arguments = parser.parse_args(argv)

    if arguments.template:
        print(json.dumps(TEMPLATE, indent=2))
        return 0

    if arguments.explain:
        print("Admissibility rules. Severity is the WORST verdict the rule can "
              "produce.\n")
        for entry in RULES:
            print(f"{entry['id']:<32} {entry['severity']:<13} {entry['headline']}")
            for line in entry["doc"].splitlines():
                print(f"    {line.strip()}")
            print()
        print("Verdict precedence: " + " > ".join(PRECEDENCE + [SURVIVED]))
        print("Exit codes: " + ", ".join(f"{v}={k}" for k, v in EXIT_CODE.items()))
        return 0

    if not arguments.finding:
        parser.error("a finding record is required (or --template / --explain)")

    try:
        finding = json.loads(arguments.finding.read_text(encoding="utf-8"))
    except OSError as error:
        print(f"cannot read {arguments.finding}: {error}", file=sys.stderr)
        return 4
    except json.JSONDecodeError as error:
        print(f"{arguments.finding} is not valid JSON: {error}", file=sys.stderr)
        return 4

    report = adjudicate(finding, min_sample_n=arguments.min_sample_n)
    report["source"] = str(arguments.finding)

    if not arguments.quiet:
        print(render(report))
    if arguments.json_out:
        arguments.json_out.parent.mkdir(parents=True, exist_ok=True)
        arguments.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if arguments.ledger:
        append_ledger(arguments.ledger, report, finding)
    return report["exitCode"]


if __name__ == "__main__":
    raise SystemExit(main())
