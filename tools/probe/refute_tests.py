#!/usr/bin/env python3
"""Self-tests for the refutation stage.

The central test is not "does the checker pass a good finding". It is
`SkinWeightFixture`, which feeds the stage the REAL 2026-07-31 skin-weight
record - the one that was byte-verified, corpus-reproduced, predicted in advance
and wrong - and asserts the stage would have stopped it.

The second-most important is `MutationTests`, which takes the finding that
SURVIVES and perturbs exactly one field per rule, asserting the verdict changes
every time. A checker that cannot fail is the defect this whole stage exists to
prevent, so 15 rules get 15 mutations and 0 survivors. `test_every_rule_has_a_
mutation` makes that mandatory: add a rule without a mutation and this suite goes
red.

Run:  python tools/probe/refute_tests.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import adversary  # noqa: E402
import refute  # noqa: E402

FIXTURES = HERE / "fixtures"
AS_WRITTEN = FIXTURES / "skin-weight-2026-07-31-as-written.json"
EXECUTED_LAW = FIXTURES / "skin-weight-2026-07-31-executed-law.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fired_rules(report: dict) -> set[str]:
    """Rules that actually fired. BLOCKED entries are not fires - they are the
    rules that could not be evaluated because the schema failed first."""
    return {entry["rule"] for entry in report["rulesFired"]
            if entry["severity"] != "BLOCKED"}


# The rival that existed on 2026-07-31 and was never written down. The note
# itself named the shader's final combine as unresolved, so this alternative was
# available to its author on the day - it did not need the capture to be
# imagined, only to be settled.
EXECUTED_LAW_RIVAL = {
    "id": "rival-executed-asymmetric",
    "statement": "The shader does not decode multiplicity: it computes T[s0]*p, "
                 "overwrites it, and doubles slot 1, so the executed weights are "
                 "(0, 2/3, 1/3) on (slot0, slot1, slot2).",
    "indistinguishableOn": [
        "file 0x1DC680 = 1/3f",
        "the single fsub at VA 0x004B0390",
        "the four diag(1/3) immediates forming a 4x4 diagonal",
        "zero BAA or XYY across all 944 shipped two-bone vertices",
        "the AAA and AAB patterns, on which the two laws are identical",
    ],
    "discriminator": {
        "description": "the destination registers of the linked shader's second "
                       "dp4 block, and the registers the accumulator is seeded from",
        "mechanism": ["shader.final_combine"],
        "expectedUnderClaim": "each of the three blocks contributes exactly once "
                              "and the sum carries the palette's 1/3 scale",
        "expectedUnderRival": "block 2 overwrites r0 and the accumulator seeds "
                              "with add r1, r0, r0, so block 1 is dead and slot 1 "
                              "is doubled",
        "status": "not_observed",
        "outcome": "none",
        "evidenceRef": [],
    },
}


def steelman(blocking: bool) -> dict:
    """The 2026-07-31 record written as honestly as it could have been.

    The author is given the benefit of every doubt: the rival is named, and it is
    named correctly. The only thing that varies is whether the note's own
    residual about the shader's final combine - the mechanism that separates the
    two laws - is marked as blocking the claim or waved through as it actually
    was.
    """
    finding = load(AS_WRITTEN)
    finding["rivals"] = [deepcopy(EXECUTED_LAW_RIVAL)]
    for residual in finding["residuals"]:
        if residual["id"] == "res-final-combine":
            residual["blocksClaim"] = blocking
    return finding


class SkinWeightFixture(unittest.TestCase):
    """The 2026-07-31 case. This is the specification."""

    def test_the_record_as_actually_written_is_inadmissible(self) -> None:
        report = refute.adjudicate(load(AS_WRITTEN))

        self.assertEqual(refute.INADMISSIBLE, report["verdict"])
        self.assertEqual(2, report["exitCode"])
        self.assertIn("R05_RIVALS_STATED", fired_rules(report))

        message = next(e["message"] for e in report["rulesFired"]
                       if e["rule"] == "R05_RIVALS_STATED")
        self.assertIn("no rivals stated", message)

    def test_it_fails_for_the_right_reason_and_only_that_reason(self) -> None:
        # Every byte fact in the note is true, every prediction was stated in
        # advance and matched, the corpus census is real, the specimen and its
        # hash are named, and it even carries the overturning test that killed
        # it. All of those rules PASS. If this stage rejected the record for
        # sloppy paperwork it would be learning the wrong lesson.
        report = refute.adjudicate(load(AS_WRITTEN))
        passed = set(report["rulesPassed"])
        for rule in ("R01_SCHEMA", "R03_PREDICTION_IN_ADVANCE",
                     "R04_PREDICTION_COULD_FAIL", "R10_SCOPE_AND_SAMPLE",
                     "R11_SPECIMEN_NAMED", "R13_OVERTURN_TEST",
                     "R14_PREDICTIONS_RESOLVED"):
            self.assertIn(rule, passed, f"{rule} should have passed")

        # Exactly two rules fire, and both say the same thing: nothing in this
        # record ever chose between the claim and an alternative.
        self.assertEqual({"R05_RIVALS_STATED", "R09_GRADE_CEILING"},
                         fired_rules(report))

    def test_the_shader_combine_residual_is_caught_once_the_rival_is_named(self) -> None:
        # R08 is the transcription of the actual failure: the note's residual
        # said the final-combine opcodes "do not decode cleanly, and are not
        # load-bearing for the law", and the final combine was the ONLY thing
        # separating the two laws.
        report = refute.adjudicate(steelman(blocking=False))

        self.assertEqual(refute.INADMISSIBLE, report["verdict"])
        self.assertIn("R08_RESIDUAL_TOUCHES_DISCRIMINATOR", fired_rules(report))
        message = next(e["message"] for e in report["rulesFired"]
                       if e["rule"] == "R08_RESIDUAL_TOUCHES_DISCRIMINATOR")
        self.assertIn("res-final-combine", message)
        self.assertIn("shader.final_combine", message)

    def test_marking_that_residual_blocking_yields_unscored_not_survived(self) -> None:
        # The honest spelling. The author knows the shader decides, and has not
        # read the shader. That is UNSCORED - go and look - and it is emphatically
        # not a pass.
        report = refute.adjudicate(steelman(blocking=True))

        self.assertEqual(refute.UNSCORED, report["verdict"])
        self.assertEqual(3, report["exitCode"])
        self.assertIn("R07_DISCRIMINATOR_OBSERVED", fired_rules(report))
        message = next(e["message"] for e in report["rulesFired"]
                       if e["rule"] == "R07_DISCRIMINATOR_OBSERVED")
        self.assertIn("not observed", message)

    def test_no_honest_spelling_of_the_2026_07_31_claim_reaches_survived(self) -> None:
        # The property that matters most. Not "this particular JSON is rejected"
        # but "the claim cannot be dressed up to get through".
        for name, finding in (("as written", load(AS_WRITTEN)),
                              ("rival named, residual waved through",
                               steelman(blocking=False)),
                              ("rival named, residual blocking",
                               steelman(blocking=True))):
            with self.subTest(spelling=name):
                report = refute.adjudicate(finding)
                self.assertNotEqual(refute.SURVIVED, report["verdict"])
                self.assertNotEqual(0, report["exitCode"])

    def test_the_superseding_finding_survives(self) -> None:
        # A checker that rejects the wrong finding is worthless if it also
        # rejects the right one.
        report = refute.adjudicate(load(EXECUTED_LAW))

        self.assertEqual(refute.SURVIVED, report["verdict"], report["rulesFired"])
        self.assertEqual(0, report["exitCode"])
        self.assertEqual(len(refute.CHECKS), len(report["rulesPassed"]))

    def test_the_survival_record_says_how_it_survived(self) -> None:
        survival = refute.adjudicate(load(EXECUTED_LAW))["survival"]

        self.assertEqual("EXECUTED", survival["evidenceGradeCeiling"])
        self.assertEqual("e-shader", survival["gradeSetBy"])
        # The thinnest point, not the sum: both discriminators were replicated
        # twice or more, so 2 is the honest number.
        self.assertEqual(2, survival["independentReplicates"])
        self.assertEqual({"rival-multiplicity", "rival-cpu-skinning"},
                         {r["rival"] for r in survival["rivalsEliminated"]})
        self.assertTrue(survival["stillOverturnedBy"])
        self.assertTrue(survival["scopeNotCovered"])

        # The byte re-read matched, and it is recorded as corroboration only.
        # It must not appear in the chain that set the grade - that separation
        # is the 2026-07-31 lesson expressed in a data structure.
        self.assertIn("e-bytes", survival["corroboratingEvidence"])
        self.assertNotIn("e-bytes", survival["discriminatingEvidence"])


class UnscoredIsNotAPass(unittest.TestCase):
    """"I found no problem" and "I was unable to look" must never render alike."""

    def test_a_prediction_that_was_not_run_is_unscored(self) -> None:
        finding = load(EXECUTED_LAW)
        finding["predictions"][0]["result"] = "not_run"
        report = refute.adjudicate(finding)

        self.assertEqual(refute.UNSCORED, report["verdict"])
        self.assertNotEqual(report["exitCode"], refute.EXIT_CODE[refute.SURVIVED])

    def test_an_inconclusive_prediction_is_unscored(self) -> None:
        finding = load(EXECUTED_LAW)
        finding["predictions"][0]["result"] = "inconclusive"
        self.assertEqual(refute.UNSCORED, refute.adjudicate(finding)["verdict"])

    def test_a_prediction_that_mismatched_refutes(self) -> None:
        finding = load(EXECUTED_LAW)
        finding["predictions"][0]["result"] = "mismatch"
        report = refute.adjudicate(finding)

        self.assertEqual(refute.REFUTED, report["verdict"])
        self.assertEqual(1, report["exitCode"])

    def test_an_unobservable_discriminator_is_unscored_not_survived(self) -> None:
        finding = load(EXECUTED_LAW)
        finding["rivals"][0]["discriminator"]["status"] = "unobservable"
        finding["rivals"][0]["discriminator"]["outcome"] = "none"
        report = refute.adjudicate(finding)

        self.assertEqual(refute.UNSCORED, report["verdict"])
        self.assertIn("R07_DISCRIMINATOR_OBSERVED", fired_rules(report))

    def test_the_four_verdicts_have_four_distinct_exit_codes(self) -> None:
        self.assertEqual(4, len(set(refute.EXIT_CODE.values())))
        self.assertEqual(0, refute.EXIT_CODE[refute.SURVIVED])
        for verdict in (refute.REFUTED, refute.INADMISSIBLE, refute.UNSCORED):
            self.assertNotEqual(0, refute.EXIT_CODE[verdict])


# ---------------------------------------------------------------------------
# Mutation tests: prove every rule can fail.
# ---------------------------------------------------------------------------

def _drop_claim(f: dict) -> None:
    del f["claim"]


def _no_predictions(f: dict) -> None:
    f["predictions"] = []


def _all_posthoc(f: dict) -> None:
    for prediction in f["predictions"]:
        prediction["predictedInAdvance"] = False


def _falsifier_is_filler(f: dict) -> None:
    f["predictions"][0]["wouldFalsifyIf"] = "n/a"


def _no_rivals(f: dict) -> None:
    f["rivals"] = []


def _discriminator_does_not_discriminate(f: dict) -> None:
    disc = f["rivals"][0]["discriminator"]
    disc["expectedUnderRival"] = disc["expectedUnderClaim"]


def _discriminator_not_observed(f: dict) -> None:
    f["rivals"][0]["discriminator"]["status"] = "not_observed"
    f["rivals"][0]["discriminator"]["outcome"] = "none"


def _residual_waves_away_a_discriminator(f: dict) -> None:
    # Exactly the 2026-07-31 move, applied to the finding that got it right.
    f["residuals"].append({
        "id": "res-combine-not-load-bearing",
        "statement": "the exact final-combine opcodes do not decode cleanly, and "
                     "are not load-bearing for the law",
        "mechanism": ["shader.final_combine"],
        "blocksClaim": False,
    })


def _overclaim_the_grade(f: dict) -> None:
    # The discriminating shader read is downgraded to reasoning; the claim still
    # says EXECUTED.
    for item in f["evidence"]:
        if item["id"] == "e-shader":
            item["grade"] = "INFERRED"


def _no_exclusions(f: dict) -> None:
    f["scope"]["notCovered"] = []


def _specimen_without_hash(f: dict) -> None:
    for item in f["evidence"]:
        if item["id"] == "e-bytes":
            item["specimen"].pop("sha256")


def _control_did_not_fail(f: dict) -> None:
    f["poisonControl"]["result"] = "did_not_fail"


def _nothing_could_overturn_it(f: dict) -> None:
    f["overturnedBy"] = []


def _prediction_mismatched(f: dict) -> None:
    f["predictions"][0]["result"] = "mismatch"


def _rival_won(f: dict) -> None:
    f["rivals"][0]["discriminator"]["outcome"] = "rival"


# One mutation per rule. The value is (mutator, expected verdict).
MUTATIONS: dict[str, tuple] = {
    "R01_SCHEMA": (_drop_claim, refute.INADMISSIBLE),
    "R02_PREDICTION_PRESENT": (_no_predictions, refute.INADMISSIBLE),
    "R03_PREDICTION_IN_ADVANCE": (_all_posthoc, refute.INADMISSIBLE),
    "R04_PREDICTION_COULD_FAIL": (_falsifier_is_filler, refute.INADMISSIBLE),
    "R05_RIVALS_STATED": (_no_rivals, refute.INADMISSIBLE),
    "R06_DISCRIMINATOR_DISTINGUISHES": (_discriminator_does_not_discriminate,
                                        refute.INADMISSIBLE),
    "R07_DISCRIMINATOR_OBSERVED": (_discriminator_not_observed, refute.UNSCORED),
    "R08_RESIDUAL_TOUCHES_DISCRIMINATOR": (_residual_waves_away_a_discriminator,
                                           refute.INADMISSIBLE),
    "R09_GRADE_CEILING": (_overclaim_the_grade, refute.INADMISSIBLE),
    "R10_SCOPE_AND_SAMPLE": (_no_exclusions, refute.INADMISSIBLE),
    "R11_SPECIMEN_NAMED": (_specimen_without_hash, refute.INADMISSIBLE),
    "R12_CONTROL_CAN_FAIL": (_control_did_not_fail, refute.UNSCORED),
    "R13_OVERTURN_TEST": (_nothing_could_overturn_it, refute.INADMISSIBLE),
    "R14_PREDICTIONS_RESOLVED": (_prediction_mismatched, refute.REFUTED),
    "R15_RIVAL_ELIMINATED": (_rival_won, refute.REFUTED),
}


class MutationTests(unittest.TestCase):
    """Zero survivors. Every rule is load-bearing on a record that otherwise
    passes, which is the only way to know the rule is capable of firing."""

    def test_every_rule_has_a_mutation(self) -> None:
        # Adding a rule without a falsification for it makes this suite red.
        self.assertEqual({entry["id"] for entry in refute.RULES},
                         set(MUTATIONS))

    def test_the_base_record_survives_unmutated(self) -> None:
        # If the base did not survive, every mutation below would "pass"
        # vacuously and the whole class would be theatre.
        self.assertEqual(refute.SURVIVED,
                         refute.adjudicate(load(EXECUTED_LAW))["verdict"])

    def test_no_mutation_survives(self) -> None:
        survivors = []
        for rule_id, (mutate, expected) in sorted(MUTATIONS.items()):
            with self.subTest(rule=rule_id):
                finding = load(EXECUTED_LAW)
                mutate(finding)
                report = refute.adjudicate(finding)

                if report["verdict"] == refute.SURVIVED:
                    survivors.append(rule_id)
                self.assertEqual(expected, report["verdict"],
                                 f"{rule_id}: {report['rulesFired']}")
                self.assertIn(rule_id, fired_rules(report),
                              f"{rule_id} did not fire on its own mutation")
        self.assertEqual([], survivors)


class EveryRuleIsLoadBearing(unittest.TestCase):
    """One level up: prove the CHECKER can fail, not only the findings.

    `MutationTests` shows each mutation is caught. That is still compatible with
    a rule being dead weight, if some other rule happens to catch the same
    mutation. So here each rule is neutered in turn - replaced with a stub that
    can never fire - and its own mutation is re-adjudicated. If the verdict does
    not change, that rule contributes nothing and its passing tells us nothing.
    This is the project's own standing question ("is this check capable of
    failing?") asked about the checker itself.
    """

    class neutered:
        """Context manager: swap one rule for a stub that never fires."""

        def __init__(self, rule_id: str) -> None:
            self.rule_id = rule_id
            self.index = next(i for i, check in enumerate(refute.CHECKS)
                              if check.rule_id == rule_id)

        def __enter__(self):
            self.original = refute.CHECKS[self.index]

            def stub(finding, cfg):
                return []
            stub.rule_id = self.rule_id
            stub.default_severity = self.original.default_severity
            refute.CHECKS[self.index] = stub
            return self

        def __exit__(self, *_) -> None:
            refute.CHECKS[self.index] = self.original

    def test_neutering_any_rule_changes_the_verdict_on_its_own_mutation(self) -> None:
        dead_weight = []
        for rule_id, (mutate, expected) in sorted(MUTATIONS.items()):
            with self.subTest(rule=rule_id):
                finding = load(EXECUTED_LAW)
                mutate(finding)

                with self.neutered(rule_id):
                    without = refute.adjudicate(finding)

                self.assertNotIn(rule_id, fired_rules(without))
                if without["verdict"] == expected:
                    dead_weight.append(rule_id)
                self.assertNotEqual(
                    expected, without["verdict"],
                    f"{rule_id} is not load-bearing: its own mutation still "
                    f"scores {expected} with the rule switched off")
        self.assertEqual([], dead_weight)

    def test_the_stub_harness_itself_works(self) -> None:
        # If `neutered` silently did nothing, the test above would pass for the
        # wrong reason on every rule that is caught twice.
        finding = load(EXECUTED_LAW)
        _no_rivals(finding)
        self.assertIn("R05_RIVALS_STATED",
                      fired_rules(refute.adjudicate(finding)))
        with self.neutered("R05_RIVALS_STATED"):
            self.assertNotIn("R05_RIVALS_STATED",
                             fired_rules(refute.adjudicate(finding)))
        self.assertIn("R05_RIVALS_STATED",
                      fired_rules(refute.adjudicate(finding)))


class VerdictPrecedence(unittest.TestCase):

    def test_a_mismatch_refutes_even_an_otherwise_inadmissible_record(self) -> None:
        # REFUTED outranks INADMISSIBLE deliberately: a recorded mismatch is
        # decisive and points the safe way.
        finding = load(EXECUTED_LAW)
        _prediction_mismatched(finding)
        _no_rivals(finding)
        report = refute.adjudicate(finding)

        self.assertEqual(refute.REFUTED, report["verdict"])
        self.assertIn("R05_RIVALS_STATED", fired_rules(report))

    def test_inadmissible_outranks_unscored(self) -> None:
        finding = load(EXECUTED_LAW)
        _discriminator_not_observed(finding)   # UNSCORED
        _nothing_could_overturn_it(finding)    # INADMISSIBLE
        self.assertEqual(refute.INADMISSIBLE,
                         refute.adjudicate(finding)["verdict"])

    def test_a_schema_failure_blocks_rather_than_passes_the_other_rules(self) -> None:
        finding = load(EXECUTED_LAW)
        _drop_claim(finding)
        report = refute.adjudicate(finding)

        self.assertEqual([], report["rulesPassed"],
                         "no rule may report a pass it did not evaluate")
        blocked = {e["rule"] for e in report["rulesFired"]
                   if e["severity"] == "BLOCKED"}
        self.assertEqual(len(refute.CHECKS) - 1, len(blocked))

    def test_a_malformed_record_does_not_crash_the_loop(self) -> None:
        for garbage in ([], "not a finding", 7, {}):
            with self.subTest(garbage=garbage):
                report = refute.adjudicate(garbage)
                self.assertEqual(refute.INADMISSIBLE, report["verdict"])


class SchemaValidator(unittest.TestCase):
    """The validator drives R01 from finding_schema.json, so it has to work."""

    def test_it_rejects_what_it_should(self) -> None:
        schema = refute.load_schema()
        cases = [
            ({}, "missing required field"),
            ({"schemaVersion": 2}, "must be 1"),
        ]
        for instance, expected in cases:
            with self.subTest(instance=instance):
                errors = " ".join(refute.validate(instance, schema))
                self.assertIn(expected, errors)

    def test_a_boolean_is_not_an_integer(self) -> None:
        errors = refute.validate(True, {"type": "integer"})
        self.assertTrue(errors)

    def test_enum_and_minlength_are_enforced(self) -> None:
        self.assertTrue(refute.validate("PROBABLY", {"enum": ["EXECUTED"]}))
        self.assertTrue(refute.validate("   ", {"type": "string", "minLength": 3}))
        self.assertEqual([], refute.validate("abcd", {"type": "string",
                                                      "minLength": 3}))

    def test_the_shipped_fixtures_validate(self) -> None:
        schema = refute.load_schema()
        for path in sorted(FIXTURES.glob("*.json")):
            with self.subTest(fixture=path.name):
                self.assertEqual([], refute.validate(load(path), schema))


class AdversaryAudit(unittest.TestCase):
    """The check on the checker."""

    @staticmethod
    def ledger(verdicts: list[str], rules: list[str] | None = None) -> list[dict]:
        return [{"kind": "adjudication", "findingId": f"f{i}", "verdict": v,
                 "rulesFired": rules or []}
                for i, v in enumerate(verdicts)]

    def test_a_refuter_that_kills_nothing_is_flagged(self) -> None:
        result = adversary.audit(self.ledger([refute.SURVIVED] * 20))
        self.assertEqual("ADVERSARY_SUSPECT", result["status"])
        self.assertEqual(0.0, result["killRate"])
        self.assertIn("rubber stamp", " ".join(result["reasons"]))

    def test_a_refuter_that_kills_everything_is_also_flagged(self) -> None:
        result = adversary.audit(self.ledger([refute.REFUTED] * 20))
        self.assertEqual("ADVERSARY_SUSPECT", result["status"])
        self.assertEqual(1.0, result["killRate"])
        self.assertIn("miscalibrated", " ".join(result["reasons"]))

    def test_a_healthy_mix_passes(self) -> None:
        verdicts = ([refute.SURVIVED] * 12 + [refute.REFUTED] * 4
                    + [refute.INADMISSIBLE] * 3 + [refute.UNSCORED])
        result = adversary.audit(self.ledger(verdicts))
        self.assertEqual("OK", result["status"], result["reasons"])

    def test_a_loop_that_never_observes_gets_its_own_diagnosis(self) -> None:
        verdicts = [refute.UNSCORED] * 17 + [refute.REFUTED] * 3
        result = adversary.audit(self.ledger(verdicts))
        self.assertEqual("LOOP_NOT_OBSERVING", result["status"])
        self.assertIn("never tests", " ".join(result["reasons"]))

    def test_too_little_data_is_not_a_pass(self) -> None:
        result = adversary.audit(self.ledger([refute.SURVIVED] * 3))
        self.assertEqual("INSUFFICIENT_DATA", result["status"])

    def test_it_reports_rules_that_have_never_fired(self) -> None:
        result = adversary.audit(
            self.ledger([refute.REFUTED] * 20, rules=["R14_PREDICTIONS_RESOLVED"]))
        self.assertNotIn("R14_PREDICTIONS_RESOLVED", result["rulesNeverFired"])
        self.assertIn("R05_RIVALS_STATED", result["rulesNeverFired"])

    def test_the_audit_exits_non_zero_unless_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            path.write_text(
                "\n".join(json.dumps(r)
                          for r in self.ledger([refute.SURVIVED] * 20)),
                encoding="utf-8")
            code = adversary.main(["--audit", "--ledger", str(path)])
            self.assertEqual(1, code)


class AttackReportAndMerge(unittest.TestCase):
    """The loop closes here: an attack becomes a rival becomes a verdict."""

    @staticmethod
    def full_report(finding_id: str, **overrides) -> dict:
        report = {
            "findingId": finding_id,
            "adversary": "test-refuter",
            "attacks": [{"attack": name, "verdict": "NO_FINDING",
                         "statement": "nothing found on this axis"}
                        for name in adversary.ATTACK_NAMES],
            "conclusion": "NO_FINDING",
        }
        report.update(overrides)
        return report

    def test_an_attack_report_missing_an_axis_is_rejected(self) -> None:
        report = self.full_report("fixture-finding-id")
        report["attacks"] = report["attacks"][:3]
        errors = adversary.validate_attack_report(report)
        self.assertTrue(any("omits" in e for e in errors), errors)

    def test_weaken_without_a_narrower_claim_is_rejected(self) -> None:
        report = self.full_report("fixture-finding-id")
        report["attacks"][0]["verdict"] = "WEAKEN"
        errors = adversary.validate_attack_report(report)
        self.assertTrue(any("proposedWeakening" in e for e in errors), errors)

    def test_a_complete_report_is_accepted(self) -> None:
        self.assertEqual([],
                         adversary.validate_attack_report(self.full_report("fixture-finding-id")))

    def test_merging_an_unobserved_rival_turns_survived_into_unscored(self) -> None:
        # This is the whole point of the stage as a LOOP. The refuter names a
        # rival it has not eliminated; the finding stops being promotable and
        # the loop is now told exactly which observation to go and make.
        finding = load(EXECUTED_LAW)
        self.assertEqual(refute.SURVIVED, refute.adjudicate(finding)["verdict"])

        report = self.full_report(finding["id"], conclusion="WEAKEN",
                                  proposedWeakening="only for the two Sentinel "
                                                    "tentacle meshes in level 800")
        report["attacks"][0].update({
            "verdict": "WEAKEN",
            "statement": "the five infantry meshes were never observed drawn; "
                         "they may link a different palette base",
            "proposedRival": {
                "id": "rival-infantry-different-palette",
                "statement": "The infantry path binds a different palette base, "
                             "so the executed weights differ for those meshes.",
                "indistinguishableOn": [
                    "everything observed in level 800, which contains no infantry"],
                "discriminator": {
                    "description": "the palette base register in a shader linked "
                                   "for an infantry draw",
                    "mechanism": ["shader.palette_base"],
                    "expectedUnderClaim": "c10, the same base as the tentacles",
                    "expectedUnderRival": "some base other than c10",
                    "status": "not_observed",
                    "outcome": "none",
                    "evidenceRef": []}}})

        merged, notes = adversary.merge_attack(finding, report)
        self.assertTrue(any("merged rival" in n for n in notes))

        after = refute.adjudicate(merged)
        self.assertEqual(refute.UNSCORED, after["verdict"])
        self.assertIn("R07_DISCRIMINATOR_OBSERVED", fired_rules(after))
        self.assertIn("rival-infantry-different-palette",
                      " ".join(e["message"] for e in after["rulesFired"]))

    def test_merging_is_idempotent(self) -> None:
        finding = load(EXECUTED_LAW)
        report = self.full_report(finding["id"])
        report["attacks"][0]["proposedRival"] = deepcopy(finding["rivals"][0])
        merged, notes = adversary.merge_attack(finding, report)
        self.assertEqual(len(finding["rivals"]), len(merged["rivals"]))
        self.assertTrue(any("already present" in n for n in notes))

    def test_the_brief_renders_with_no_placeholders_left(self) -> None:
        finding = load(AS_WRITTEN)
        brief = adversary.render_brief(finding, refute.adjudicate(finding))
        self.assertNotIn("{{", brief)
        self.assertIn(finding["id"], brief)
        # The repository documentation header is for readers of the repo, not
        # for the refuter, and must not reach the brief.
        self.assertNotIn(adversary.PROMPT_MARKER, brief)
        self.assertNotIn("Last updated:", brief)
        self.assertTrue(brief.startswith("You are the REFUTER"), brief[:80])
        self.assertIn("R05_RIVALS_STATED", brief)
        for name in adversary.ATTACK_NAMES:
            self.assertIn(name, brief)


class CommandLine(unittest.TestCase):
    """A caller that ignores the JSON still cannot ignore the verdict."""

    def run_tool(self, tool: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(HERE / tool), *args],
                              capture_output=True, text=True, check=False)

    def test_exit_codes_match_the_verdicts(self) -> None:
        for path, expected in ((AS_WRITTEN, 2), (EXECUTED_LAW, 0)):
            with self.subTest(fixture=path.name):
                done = self.run_tool("refute.py", str(path))
                self.assertEqual(expected, done.returncode, done.stdout)

    def test_the_template_is_itself_a_valid_shape(self) -> None:
        done = self.run_tool("refute.py", "--template")
        self.assertEqual(0, done.returncode)
        template = json.loads(done.stdout)
        # The template must PARSE against the schema but must NOT be admissible:
        # a blank finding that sailed through would be the worst possible
        # default.
        self.assertEqual([], refute.validate(template, refute.load_schema()))
        self.assertNotEqual(refute.SURVIVED,
                            refute.adjudicate(template)["verdict"])

    def test_explain_lists_every_rule(self) -> None:
        done = self.run_tool("refute.py", "--explain")
        self.assertEqual(0, done.returncode)
        for entry in refute.RULES:
            self.assertIn(entry["id"], done.stdout)

    def test_the_ledger_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "probe" / "ledger.jsonl"
            for path in (AS_WRITTEN, EXECUTED_LAW):
                self.run_tool("refute.py", str(path), "--quiet",
                              "--ledger", str(ledger))
            rows = adversary.read_ledger(ledger)
            self.assertEqual([refute.INADMISSIBLE, refute.SURVIVED],
                             [r["verdict"] for r in rows])
            self.assertIn("R05_RIVALS_STATED", rows[0]["rulesFired"])

    def test_a_bad_path_is_an_error_not_a_verdict(self) -> None:
        done = self.run_tool("refute.py", str(HERE / "no-such-finding.json"))
        self.assertEqual(4, done.returncode)


def main() -> int:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite(
        loader.loadTestsFromTestCase(case) for case in (
            SkinWeightFixture, UnscoredIsNotAPass, MutationTests,
            EveryRuleIsLoadBearing, VerdictPrecedence, SchemaValidator,
            AdversaryAudit,
            AttackReportAndMerge, CommandLine))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
