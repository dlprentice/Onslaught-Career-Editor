#!/usr/bin/env python3
"""Tests for the probe authoring tool.

THE POINT OF THIS FILE is not that the checks pass. It is that each check is
shown to be CAPABLE OF FAILING. A guard that cannot fail is worse than no guard,
because it is trusted. So every guarded behaviour here is tested twice:

    check(...)      the thing must work / must refuse
    falsify(...)    the thing it guards is deliberately broken, and the guard
                    MUST catch it. If the sabotage sails through, the test is
                    declared vacuous and the suite fails.

Run:
    python tools/probe/test_probe_author.py [--lab <local-lab>] [--keep]

Exit 0 = all checks passed AND every guard was proven falsifiable.
Exit 1 = a check failed, or a guard turned out to be vacuous.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bea_lab  # noqa: E402
import mission_script_emitter as mse  # noqa: E402
import probe_author as pa  # noqa: E402

RESULTS: list[tuple[str, str, str]] = []  # (status, name, detail)

PILOT_PROGRAM = [
    {"op": "let", "name": "target", "native": "GetThingRef",
     "args": [{"string": "Turret 01"}]},
    {"op": "call", "target": "target", "native": "SetVulnerable",
     "args": [{"bool": True}]},
    {"op": "call", "target": "target", "native": "SetHealth",
     "args": [{"float": 0.001}]},
    {"op": "call", "native": "Pause", "args": [{"float": 1.0}]},
    {"op": "call", "target": "target", "native": "Damage",
     "args": [{"float": 1000.0}]},
]


# --------------------------------------------------------------------------- #
# harness
# --------------------------------------------------------------------------- #
def check(name: str, fn) -> bool:
    try:
        detail = fn() or ""
        RESULTS.append(("PASS", name, str(detail)))
        return True
    except Exception as exc:  # noqa: BLE001
        RESULTS.append(("FAIL", name, f"{type(exc).__name__}: {exc}"))
        if os.environ.get("PROBE_TEST_TRACE"):
            traceback.print_exc()
        return False


def refuses(name: str, exc_type, fn) -> bool:
    """The tool must REFUSE. Anything else -- success, or the wrong error -- fails."""
    try:
        fn()
    except exc_type as exc:
        RESULTS.append(("PASS", name, f"refused: {str(exc).splitlines()[0][:110]}"))
        return True
    except Exception as exc:  # noqa: BLE001
        RESULTS.append(("FAIL", name, f"wrong error {type(exc).__name__}: {exc}"))
        return False
    RESULTS.append(("FAIL", name, "did NOT refuse"))
    return False


def falsify(name: str, fn) -> bool:
    """Sabotage something a guard protects; the guard must notice.

    `fn` performs the sabotage and is expected to raise. If it does not, the
    guard it targets is vacuous and this is reported as VACUOUS (a failure).
    """
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        RESULTS.append(("PROVEN", name, f"caught by {type(exc).__name__}: "
                                        f"{str(exc).splitlines()[0][:100]}"))
        return True
    RESULTS.append(("VACUOUS", name, "sabotage was NOT caught -- the guard proves nothing"))
    return False


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
class Fix:
    def __init__(self, lab: str | None, workdir: Path):
        self.lab_root = bea_lab.find_lab(lab)
        self.lab = str(self.lab_root)
        self.res = self.lab_root / "safe-copy-bea-pristine" / "data" / "Resources"
        self.src = str(self.res / "905_res_PC.aya")
        self.src100 = str(self.res / "100_res_PC.aya")
        self.specimen = self.lab_root / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
        self.work = workdir
        self.out = workdir / "out"
        self.out.mkdir(parents=True, exist_ok=True)
        self.profile_cache = str(workdir / "native-profile.json")
        self.n = 0

    def name(self, stem: str) -> str:
        self.n += 1
        return f"{stem}{self.n:03d}"

    def author(self, intents, **kw):
        kw.setdefault("lab", self.lab)
        kw.setdefault("corpus", str(self.res))
        kw.setdefault("profile_cache", self.profile_cache)
        kw.setdefault("force", True)
        name = kw.pop("name", self.name("t"))
        poison = kw.pop("poison", None)
        if poison:
            kw["control_arms"] = {"poison": poison}
        return pa.author_arms(kw.pop("src", self.src), self.out, intents, name=name, **kw)

    def sym(self, archive_path: str, script: str, symbol: str, world="RLWD"):
        a = pa.Archive(archive_path, lab=self.lab)
        s = a.world(world).script(script)
        return pa._symbol(s, symbol)

    def instr(self, archive_path: str, script: str, i: int, world="RLWD"):
        a = pa.Archive(archive_path, lab=self.lab)
        return a.world(world).script(script)["instructions"][i]


def sha_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #
def t_identity(f: Fix) -> None:
    """An authoring run with no intents must reproduce the payload exactly."""
    def run():
        m = f.author([], name="identity")["probe"]
        assert m["output"]["inflated_sha256"] == m["source"]["inflated_sha256"], \
            "identity build changed the payload"
        assert m["verification"]["changed_bytes"] == 0
        return f"inflated sha unchanged ({m['source']['inflated_bytes']} B)"
    check("identity build reproduces the payload byte for byte", run)

    # ... and the comparison is not vacuous: a real edit must break it.
    def sabotage():
        m = f.author([{"op": "set-constant", "script": "LapTimer",
                       "symbol": "data31536", "value": 9.0}], name="identity_sab")["probe"]
        assert m["output"]["inflated_sha256"] == m["source"]["inflated_sha256"], \
            "an edited archive still hashes equal to the source"
    falsify("...and an edited archive does NOT hash equal (identity check is real)", sabotage)


def t_set_constant(f: Fix) -> None:
    """The proven case: retarget a Pause duration."""
    state = {}

    def run():
        before = f.sym(f.src, "LapTimer", "data31536")
        assert abs(before["value"] - 0.05) < 1e-9, f"source constant is {before['value']}"
        m = f.author([{"op": "set-constant", "script": "LapTimer", "symbol": "data31536",
                       "value": 2.0, "why": "Pause duration 0.05 -> 2.0 s"}],
                     name="const")["probe"]
        state["m"] = m
        after = f.sym(m["output"]["path"], "LapTimer", "data31536")
        assert abs(after["value"] - 2.0) < 1e-6, f"output constant is {after['value']}"
        e = m["edits"][0]
        assert e["length"] == 4 and m["verification"]["changed_bytes"] == 4, m["verification"]
        assert e["expect_hex"] == "cd cc 4c 3d", e["expect_hex"]
        assert m["verification"]["ranges_within_edits"]
        return f"0.05 -> 2.0 at inflated {e['offset']}, exactly 4 bytes changed"
    check("set-constant retargets a Pause duration and nothing else", run)

    # The read-back assertion must be able to fail: edit a DIFFERENT symbol and
    # the same assertion must not hold.
    def sabotage():
        m = f.author([{"op": "set-constant", "script": "LapTimer", "symbol": "data31533",
                       "value": 0}], name="const_sab")["probe"]
        after = f.sym(m["output"]["path"], "LapTimer", "data31536")
        assert abs(after["value"] - 2.0) < 1e-6, \
            f"data31536 reads {after['value']}, not 2.0 -- the read-back check discriminates"
    falsify("...and the read-back check fails when a different symbol is edited", sabotage)

    def sabotage2():
        """A one-byte-off offset must not silently produce a valid float 2.0."""
        m = state["m"]
        e = m["edits"][0]
        pa.author(f.src, f.out / "const_off.aya",
                  [{"op": "raw", "offset": e["offset"] + 1,
                    "expect": bytes.fromhex(e["expect_hex"].replace(" ", "")).hex(),
                    "new": bytes.fromhex(e["new_hex"].replace(" ", "")).hex()}],
                  lab=f.lab, force=True)
    falsify("...and the anchor refuses the same write shifted by one byte", sabotage2)


def t_set_script_trace(f: Fix) -> None:
    """The durable intent owns the now-runtime-proven trailerA trace lever."""
    def run():
        before = pa.Archive(f.src100, lab=f.lab).world("RLWD").script("Setup")
        assert before["instr_count"] == 138 and before["trailer"] == [0, 1]
        m = f.author(
            [{"op": "set-script-trace", "script": "Setup", "value": 1}],
            src=f.src100,
            name="script_trace",
        )["probe"]
        after = pa.Archive(m["output"]["path"], lab=f.lab).world("RLWD").script("Setup")
        assert after["instr_count"] == 138 and after["trailer"] == [1, 1]
        edit = m["edits"][0]
        assert edit["kind"] == "set-script-trace"
        assert edit["offset"] == 3681592
        assert edit["expect_hex"] == "00 00 00 00"
        assert edit["new_hex"] == "01 00 00 00"
        assert edit["scriptOrdinal"] == 9
        assert edit["objectField"] == "CScriptObjectCode+0x60"
        assert m["verification"]["changed_bytes"] == 1
        assert "RUNS AND TRACES" in m["prediction"]
        assert any("value-0/value-2 controls" in row for row in m["unproven"])
        return "Setup trailerA 0 -> 1 at inflated 3681592; one changed byte; trailerB preserved"
    check("set-script-trace enables the exact serialized VM trace field", run)

    def value_two():
        m = f.author(
            [{"op": "set-script-trace", "script": "Setup", "value": 2}],
            src=f.src100,
            name="script_trace_value2",
        )["probe"]
        trailer = pa.Archive(m["output"]["path"], lab=f.lab).world("RLWD").script("Setup")["trailer"]
        assert trailer == [2, 1]
        assert "WITHOUT VM TRACE LINES" in m["prediction"]
        return "exact-comparison control reparses as trailer [2, 1]"
    check("set-script-trace authors the exact-value-two negative control", value_two)

    refuses(
        "set-script-trace refuses values outside the measured 0/1/2 domain",
        pa.IntentError,
        lambda: f.author(
            [{"op": "set-script-trace", "script": "Setup", "value": 3}],
            src=f.src100,
            name="script_trace_bad_value",
        ),
    )
    refuses(
        "set-script-trace refuses an identity write",
        pa.IntentError,
        lambda: f.author(
            [{"op": "set-script-trace", "script": "Setup", "value": 0}],
            src=f.src100,
            name="script_trace_identity",
        ),
    )

    def sabotage_readback():
        archive = pa.Archive(f.src100, lab=f.lab)
        world = archive.world("RLWD")
        setup = world.script("Setup")
        trailer_b = world.abs(setup["end"] - 4)
        m = f.author(
            [{"op": "raw", "offset": trailer_b, "expect": "01000000", "new": "02000000"}],
            src=f.src100,
            name="script_trace_wrong_dword",
        )["probe"]
        trailer = pa.Archive(m["output"]["path"], lab=f.lab).world("RLWD").script("Setup")["trailer"]
        assert trailer == [1, 1], f"wrong dword leaves trace field disabled: {trailer}"
    falsify("...and the trailerA read-back test rejects a trailerB edit", sabotage_readback)


def t_anchor_guard(f: Fix) -> None:
    """The central safety property: a stated-bytes mismatch REFUSES the write."""
    off = pa.Archive(f.src, lab=f.lab).world("RLWD")
    s = off.script("LapTimer")
    ioff = off.abs(s["instr_off"])
    real = struct.pack("<ii", *s["instructions"][0])

    refuses("anchor guard refuses a write whose expected bytes are wrong",
            pa.AnchorMismatch,
            lambda: pa.author(f.src, f.out / "anchor_bad.aya",
                              [{"op": "raw", "offset": ioff,
                                "expect": b"\xde\xad\xbe\xef".hex(),
                                "new": b"\x00\x00\x00\x00".hex()}],
                              lab=f.lab, force=True))

    refuses("anchor guard refuses a range that runs off the end of the payload",
            pa.AnchorMismatch,
            lambda: pa.author(f.src, f.out / "anchor_oob.aya",
                              [{"op": "raw", "offset": 10 ** 9,
                                "expect": b"\x00\x00\x00\x00".hex(),
                                "new": b"\x01\x00\x00\x00".hex()}],
                              lab=f.lab, force=True))

    # The refusal must not be unconditional: the identical write with the CORRECT
    # expected bytes has to go through, or "it refused" means nothing.
    def run():
        m = pa.author(f.src, f.out / "anchor_ok.aya",
                      [{"op": "raw", "offset": ioff, "expect": real.hex(), "new": real.hex(),
                        "why": "no-op write with correct anchor"}],
                      lab=f.lab, force=True)
        assert m["verification"]["changed_bytes"] == 0
        return "correct anchor accepted (refusal is conditional, not blanket)"
    check("...and the SAME write with correct expected bytes is accepted", run)

    # There must be no bare-offset API at all.
    def no_bare_offset():
        pa.Edit(ioff, b"", b"", "raw", "bare offset")
    falsify("...and an Edit with no expected bytes is rejected at construction", no_bare_offset)


def t_overlap(f: Fix) -> None:
    w = pa.Archive(f.src, lab=f.lab).world("RLWD")
    s = w.script("LapTimer")
    ioff = w.abs(s["instr_off"])
    a = struct.pack("<ii", *s["instructions"][0])
    b = struct.pack("<i", s["instructions"][0][1])

    refuses("overlapping edits are refused", pa.ProbeError,
            lambda: pa.author(f.src, f.out / "overlap.aya",
                              [{"op": "raw", "offset": ioff, "expect": a.hex(), "new": a.hex()},
                               {"op": "raw", "offset": ioff + 4, "expect": b.hex(),
                                "new": b.hex()}],
                              lab=f.lab, force=True))

    def run():
        pa.author(f.src, f.out / "nooverlap.aya",
                  [{"op": "raw", "offset": ioff, "expect": a.hex(), "new": a.hex()},
                   {"op": "raw", "offset": ioff + 8, "expect":
                    struct.pack("<ii", *s["instructions"][1]).hex(),
                    "new": struct.pack("<ii", *s["instructions"][1]).hex()}],
                  lab=f.lab, force=True)
        return "adjacent non-overlapping edits accepted"
    check("...and non-overlapping edits are accepted", run)


def t_retarget_call(f: Fix) -> None:
    """Point a CALL somewhere we want to observe, without unbalancing the stack."""
    def run():
        m = f.author([{"op": "retarget-call", "script": "LapTimer", "instruction": 13,
                       "native": "AddHelpMessage"}], name="retarget")["probe"]
        op, arg = f.instr(m["output"]["path"], "LapTimer", 13)
        idx, argc, hi = pa.decode_call(arg)
        nat = pa.load_natives(f.lab_root)
        assert op == pa.OP_CALL, f"opcode became {op:#04x}"
        assert nat[idx] == "AddHelpMessage", f"resolves to {nat.get(idx)}"
        src_op, src_arg = f.instr(f.src, "LapTimer", 13)
        _, s_argc, s_hi = pa.decode_call(src_arg)
        assert (argc, bool(hi)) == (s_argc, bool(s_hi)), "arity or return discipline moved"
        assert m["verification"]["changed_bytes"] == 1, m["verification"]
        return (f"PostEvent -> AddHelpMessage, argc={argc} void, "
                f"{m['verification']['changed_bytes']} byte changed")
    check("retarget-call repoints a native and preserves arity/return", run)

    refuses("retarget-call refuses a native with a different observed arity",
            pa.IntentError,
            lambda: f.author([{"op": "retarget-call", "script": "LapTimer", "instruction": 13,
                               "native": "CreatePosition"}], name="retarget_arity"))

    refuses("retarget-call refuses a native never called by any shipped script",
            pa.IntentError,
            lambda: f.author([{"op": "retarget-call", "script": "LapTimer", "instruction": 13,
                               "native": "SetGravity"}], name="retarget_unprofiled"))

    refuses("retarget-call refuses an instruction that is not a CALL",
            pa.IntentError,
            lambda: f.author([{"op": "retarget-call", "script": "LapTimer", "instruction": 0,
                               "native": "AddHelpMessage"}], name="retarget_notcall"))

    # Prove the arity guard is reading real data, not refusing everything: the
    # rejected native really does have a different profile in the corpus.
    def run2():
        prof = pa.get_profile(str(f.res), f.profile_cache, lab=f.lab)
        assert list(prof["by_name"]["AddHelpMessage"]["profiles"]) == ["1/0"]
        assert list(prof["by_name"]["CreatePosition"]["profiles"]) == ["3/1"]
        assert "SetGravity" not in prof["by_name"]
        multi = [k for k, v in prof["by_name"].items() if len(v["profiles"]) > 1]
        assert not multi, f"natives with ambiguous profiles: {multi}"
        return (f"{prof['natives_called']} natives, each with exactly one (argc/returns) "
                f"profile over {prof['world_chunks']} world chunks")
    check("...and the arity guard is backed by a single profile per native", run2)


def t_poison(f: Fix) -> None:
    """The poison control -- an arm that should die, and differs only by that."""
    def run():
        res = f.author(
            [{"op": "set-constant", "script": "LapTimer", "symbol": "data31536", "value": 2.0},
             {"op": "retarget-call", "script": "LapTimer", "instruction": 13,
              "native": "AddHelpMessage"}],
            poison=[{"op": "poison-opcode", "script": "LapTimer", "instruction": 13}],
            name="arms")
        probe, poison = res["probe"], res["poison"]
        v = poison["verification"]
        assert v["differs_from_probe_only_by_this_arm"] is True
        assert v["probe_vs_arm_changed_bytes"] == 1, v
        assert poison["source"]["sha256"] == probe["output"]["sha256"], \
            "poison must be derived from the probe archive, not from retail"
        assert poison["prediction"].startswith("DIES"), poison["prediction"]
        assert probe["prediction"].startswith("RUNS"), probe["prediction"]
        p_op, _ = f.instr(probe["output"]["path"], "LapTimer", 13)
        x_op, _ = f.instr(poison["output"]["path"], "LapTimer", 13)
        assert p_op in pa.VALID_OPCODES, f"probe opcode {p_op:#04x} is not valid"
        assert x_op not in pa.VALID_OPCODES, f"poison opcode {x_op:#04x} IS valid -- won't die"
        return (f"probe op {p_op:#04x} valid, poison op {x_op:#04x} invalid; "
                f"arms differ by {v['probe_vs_arm_changed_bytes']} byte")
    check("poison arm differs from the probe in exactly one intended byte", run)

    refuses("poison refuses an opcode inside the accepted range (would not die)",
            pa.IntentError,
            lambda: f.author([], poison=[{"op": "poison-opcode", "script": "LapTimer",
                                          "instruction": 13, "opcode": 0x17}],
                             name="poison_valid"))

    refuses("poison-datatype refuses a type tag CreateFromType accepts",
            pa.IntentError,
            lambda: f.author([], poison=[{"op": "poison-datatype", "script": "LapTimer",
                                          "symbol": "data31536", "tag": 2}],
                             name="poison_validtag"))

    def run2():
        res = f.author([], poison=[{"op": "poison-datatype", "script": "LapTimer",
                                    "symbol": "data31536", "tag": 9}], name="poison_dt")
        e = res["poison"]["edits"][0]
        assert e["old_tag"] == 2 and e["new_tag"] == 9
        return f"type tag 2 -> 9 at inflated {e['offset']}"
    check("poison-datatype writes an unknown tag at the symbol's tag dword", run2)

    def run3():
        """The null control: an edit the engine provably cannot see."""
        res = f.author([], poison=[{"op": "null-control", "script": "LapTimer"}],
                       name="nullctl")
        e = res["poison"]["edits"][0]
        assert e["length"] == 10 and e["expect_hex"] == pa.SENTINEL.hex(" ")
        out = pa.Archive(res["poison"]["output"]["path"], lab=f.lab)
        s = out.world("RLWD").script("LapTimer")
        assert s["sentinel"] != pa.SENTINEL, "sentinel was not actually corrupted"
        assert res["poison"]["prediction"].startswith("NO OBSERVABLE"), \
            res["poison"]["prediction"]
        return "sentinel corrupted; engine reads and discards it, so this predicts no change"
    check("null-control corrupts the sentinel the engine cannot detect", run3)

    def run4():
        """A poison and a null control predict opposite outcomes, so each needs
        its own archive -- one file carrying both would be uninterpretable."""
        res = f.author(
            [{"op": "set-constant", "script": "LapTimer", "symbol": "data31536", "value": 2.0}],
            control_arms={
                "poison-opcode": [{"op": "poison-opcode", "script": "LapTimer",
                                   "instruction": 13}],
                "null-control": [{"op": "null-control", "script": "LapTimer"}],
            },
            name="threearm")
        assert set(res) == {"probe", "poison-opcode", "null-control"}, set(res)
        paths = {k: v["output"]["path"] for k, v in res.items()}
        assert len(set(paths.values())) == 3, "arms share an output file"
        preds = {k: v["prediction"].split(":")[0] for k, v in res.items()}
        assert preds == {"probe": "RUNS", "poison-opcode": "DIES",
                         "null-control": "NO OBSERVABLE DIFFERENCE from the probe arm. The "
                                         "engine reads the sentinel into a stack local it "
                                         "never examines. If this arm behaves differently, our "
                                         "model of the format is wrong."}, preds
        for k, m in res.items():
            if k == "probe":
                continue
            assert m["verification"]["differs_from_probe_only_by_this_arm"]
        return "3 distinct archives: probe (RUNS), poison-opcode (DIES), null-control (no change)"
    check("each control arm is a separate archive with its own prediction", run4)

    # The post-edit gate INVERTS for framing-breaking arms. Prove the inversion is
    # a real gate: a "poison" that fails to desynchronise must be refused, because
    # an arm that should die and does not proves nothing.
    def sabotage_desync():
        orig = pa.intent_poison_datatype

        def noop(world, spec):
            edits, splice = orig(world, spec)
            e = edits[0]
            return [pa.Edit(e.offset, e.expect, e.expect, e.kind,
                            "sabotaged: writes the tag back unchanged")], splice
        pa.intent_poison_datatype = noop
        try:
            f.author([], poison=[{"op": "poison-datatype", "script": "LapTimer",
                                  "symbol": "data31536", "tag": 9}], name="poison_nodesync")
        finally:
            pa.intent_poison_datatype = orig
    falsify("...and a poison-datatype that fails to desynchronise is refused", sabotage_desync)

    def sabotage_sentinel():
        orig = pa.intent_null_control

        def noop(world, spec):
            edits, splice = orig(world, spec)
            e = edits[0]
            return [pa.Edit(e.offset, e.expect, e.expect, e.kind,
                            "sabotaged: writes the sentinel back unchanged")], splice
        pa.intent_null_control = noop
        try:
            f.author([], poison=[{"op": "null-control", "script": "LapTimer"}],
                     name="null_nobreak")
        finally:
            pa.intent_null_control = orig
    falsify("...and a null-control that breaks no sentinel is refused", sabotage_sentinel)

    def sabotage_extra_sentinel():
        """Breaking MORE sentinels than intended must also be caught."""
        w = pa.Archive(f.src, lab=f.lab).world("RLWD")
        offs = [w.abs(s["sentinel_off"]) for s in w.scripts[:2]]
        pa.author(f.src, f.out / "two_sentinels.aya",
                  [{"op": "raw", "offset": o, "expect": pa.SENTINEL.hex(),
                    "new": b"XXXXXXXXXX".hex()} for o in offs],
                  lab=f.lab, force=True)
    falsify("...and breaking a sentinel without declaring it is refused",
            sabotage_extra_sentinel)

    # The "arms differ only by the poison" property must be capable of failing.
    def sabotage():
        res = f.author([{"op": "set-constant", "script": "LapTimer", "symbol": "data31536",
                         "value": 2.0}], name="arms_sab")
        probe = res["probe"]["output"]["path"]
        # a second, unrelated build stands in for a contaminated poison arm
        other = f.author([{"op": "set-constant", "script": "LapTimer", "symbol": "data31536",
                           "value": 3.0},
                          {"op": "set-constant", "script": "LapTimer", "symbol": "data31533",
                           "value": 0}], name="arms_sab2")["probe"]["output"]["path"]
        _, aya, _, _ = bea_lab.load(f.lab)
        _, a, _ = aya.read_aya(probe)
        _, b, _ = aya.read_aya(other)
        got = pa.diff_ranges(a, b)
        want = [(res["probe"]["edits"][0]["offset"],
                 res["probe"]["edits"][0]["offset"] + 4)]
        assert all(any(lo >= o and hi <= h for o, h in want) for lo, hi in got), \
            f"arms differ outside the declared edit: {got}"
    falsify("...and that property fails when the arms differ elsewhere", sabotage)


def t_framing_gate(f: Fix) -> None:
    """A desynchronising edit must be caught BEFORE anything is written."""
    w = pa.Archive(f.src, lab=f.lab).world("RLWD")
    s = w.script("LapTimer")
    sym = pa._symbol(s, "data31535")            # the 'Timer Pulse' string
    prefix_off = w.abs(sym["value_off"])        # its string32 length prefix
    chars_off = prefix_off + 4
    old_len = struct.pack("<i", sym["value_len"])
    bad_len = struct.pack("<i", sym["value_len"] + 1)
    out = f.out / "desync.aya"

    refuses("a same-length edit that desynchronises the grammar is refused",
            pa.FramingError,
            lambda: pa.author(f.src, out,
                              [{"op": "raw", "offset": prefix_off, "expect": old_len.hex(),
                                "new": bad_len.hex(),
                                "why": "bump a string32 length prefix by one"}],
                              lab=f.lab, force=True))

    def not_written():
        assert not out.exists(), "a refused build still wrote its output file"
        return "no output file was produced by the refused build"
    check("...and the refused build wrote no output file", not_written)

    # The framing gate must not be refusing everything: an edit of the same size,
    # in the same string, that does NOT desynchronise has to pass.
    def run():
        old_c = w.payload[sym["value_off"] + 4 : sym["value_off"] + 5]
        m = pa.author(f.src, f.out / "nodesync.aya",
                      [{"op": "raw", "offset": chars_off, "expect": old_c.hex(),
                        "new": b"X".hex(), "why": "one character inside the string"}],
                      lab=f.lab, force=True)
        assert m["verification"]["output_sentinels"]["RLWD"] == "14/14"
        return "a non-desynchronising same-size edit at the same site is accepted"
    check("...and a non-desynchronising edit at the same site is accepted", run)


def t_length_change(f: Fix) -> None:
    refuses("a length-changing edit is refused without explicit authorisation",
            pa.LengthChangeRefused,
            lambda: f.author([{"op": "set-constant", "script": "LapTimer",
                               "symbol": "data31535", "value": "MUCH LONGER STRING"}],
                             name="lc_no"))

    def run():
        m = f.author([{"op": "set-constant", "script": "LapTimer", "symbol": "data31535",
                       "value": "HEARTBEAT PING FROM PROBE"}],
                     allow_length_change=True, name="lc_yes")["probe"]
        delta = m["output"]["inflated_bytes"] - m["source"]["inflated_bytes"]
        assert delta == m["splice"]["delta"] == 14, (delta, m["splice"])
        tags = [e["tag"] for e in m["edits"] if e["kind"] == "chunk-size"]
        assert tags == ["WRES", "WRLD", "RLWD"], tags
        after = f.sym(m["output"]["path"], "LapTimer", "data31535")
        assert after["value"] == "HEARTBEAT PING FROM PROBE", after["value"]
        assert m["verification"]["output_sentinels"]["RLWD"] == "14/14"
        assert m["unproven"], "a length-changing build must declare what is unproven"
        return f"+14 B, chunk sizes {tags} fixed, 14/14 sentinels, string reads back"
    check("length-changing string edit fixes all three chunk sizes and re-parses", run)

    # Prove the chunk-size fixups are load-bearing: skip them and the post-edit
    # framing gate must catch it.
    def sabotage():
        orig = pa.size_fixups
        pa.size_fixups = lambda inflated, splice: []
        try:
            f.author([{"op": "set-constant", "script": "LapTimer", "symbol": "data31535",
                       "value": "HEARTBEAT PING FROM PROBE"}],
                     allow_length_change=True, name="lc_nofix")
        finally:
            pa.size_fixups = orig
    falsify("...and omitting the chunk-size fixups is caught by the framing gate", sabotage)


def t_splice(f: Fix) -> None:
    def run():
        m = f.author([{"op": "splice-script", "donor_archive": f.src100,
                       "donor_script": "Weather", "as_name": "ProbeWeather"}],
                     allow_length_change=True, name="splice")["probe"]
        assert m["world"]["script_count_before"] == 14
        assert m["world"]["script_count_after"] == 15
        out = pa.Archive(m["output"]["path"], lab=f.lab).world("RLWD")
        good, total = out.sentinels_ok()
        assert (good, total) == (15, 15), (good, total)
        assert "ProbeWeather" in out.by_name
        # nothing existing may move or change
        src = pa.Archive(f.src, lab=f.lab).world("RLWD")
        for a, b in zip(src.scripts, out.scripts):
            assert a["name"] == b["name"], f"{a['name']} became {b['name']}"
            assert a["record_start"] == b["record_start"], f"{a['name']} moved"
        spliced = out.by_name["ProbeWeather"]
        donor = pa.Archive(f.src100, lab=f.lab).world("RLWD").script("Weather")
        assert spliced["instr_count"] == donor["instr_count"]
        assert spliced["instructions"] == donor["instructions"], "instruction stream changed"
        return (f"14 -> 15 scripts, 15/15 sentinels, {donor['instr_count']} donor "
                "instructions identical, no existing record moved")
    check("splice-script appends a cross-archive donor without renumbering anything", run)

    refuses("splice-script refuses a donor name that already exists",
            pa.IntentError,
            lambda: f.author([{"op": "splice-script", "donor_script": "LapTimer"}],
                             allow_length_change=True, name="splice_dup"))

    # Prove the scriptCount bump is load-bearing.
    def sabotage():
        orig = pa.intent_splice_script
        pa.intent_splice_script = lambda world, spec, lab=None: ([], orig(world, spec, lab=lab)[1])
        try:
            f.author([{"op": "splice-script", "donor_archive": f.src100,
                       "donor_script": "Weather", "as_name": "ProbeWeather2"}],
                     allow_length_change=True, name="splice_nobump")
        finally:
            pa.intent_splice_script = orig
    falsify("...and omitting the scriptCount bump is caught", sabotage)


def t_replace_script(f: Fix) -> None:
    """The bounded emitter replaces Setup in the same slot and nothing else."""
    state = {}

    def run():
        intent = {"op": "replace-script", "script": "Setup", "program": PILOT_PROGRAM,
                  "why": "single-target damage-chain pilot"}
        m = f.author([intent], src=f.src100, allow_length_change=True,
                     name="damage_pilot")["probe"]
        state["manifest"] = m
        before = pa.Archive(f.src100, lab=f.lab).world("RLWD")
        after = pa.Archive(m["output"]["path"], lab=f.lab).world("RLWD")
        assert before.script_count == after.script_count == 25
        assert [s["name"] for s in before.scripts] == [s["name"] for s in after.scripts]
        setup_ordinal = [s["name"] for s in before.scripts].index("Setup")
        assert setup_ordinal == m["splice"]["scriptOrdinal"]

        unchanged = 0
        for ordinal, (a, b) in enumerate(zip(before.scripts, after.scripts)):
            old = before.payload[a["record_start"]:a["record_end"]]
            new = after.payload[b["record_start"]:b["record_end"]]
            if ordinal == setup_ordinal:
                assert old != new
            else:
                assert old == new, f"non-target script changed: {a['name']}"
                unchanged += 1
        assert unchanged == 24

        setup = after.script("Setup")
        assert setup["event_table"] == [1] + [-1] * 12
        assert setup["trailer"] == [0, 1]
        assert setup["event_count"] == 0
        want_instructions = [
            (0x17, -1),
            (0x05, 3), (0x18, 0x1010E), (0x15, 0), (0x0E, -1),
            (0x05, 0), (0x16, -1), (0x05, 5), (0x18, 0x120), (0x0E, -1),
            (0x05, 0), (0x16, -1), (0x05, 7), (0x18, 0x12E), (0x0E, -1),
            (0x05, 9), (0x18, 0x104), (0x0E, -1),
            (0x05, 0), (0x16, -1), (0x05, 11), (0x18, 0x145), (0x0E, -1),
            (0x17, -1),
        ]
        assert setup["instructions"] == want_instructions, setup["instructions"]
        syms = setup["symtab"]["symbols"]
        assert [(syms[i]["type"], syms[i]["value"]) for i in (3, 5, 7, 9, 11)] == [
            (3, "Turret 01"), (4, 1), (2, struct.unpack("<f", struct.pack("<f", 0.001))[0]),
            (2, 1.0), (2, 1000.0),
        ]

        # Independent compiler-template witnesses from retail bytecode.  These
        # checks can fail if our six-opcode reading or statement lowering drifts.
        shipped_setup = before.script("Setup")["instructions"]
        assert [op for op, _ in shipped_setup[1:5]] == [0x05, 0x18, 0x15, 0x0E]
        assert [op for op, _ in shipped_setup[34:39]] == [0x05, 0x16, 0x05, 0x18, 0x0E]
        weather = before.script("Weather")["instructions"]
        assert any(
            [op for op, _ in weather[i:i + 3]] == [0x05, 0x18, 0x0E]
            and pa.decode_call(weather[i + 1][1])[0] == 4
            for i in range(len(weather) - 2)
        ), "retail Weather has no PUSH/CALL Pause/REMOVE_TOP template"

        v = m["verification"]
        assert v["replacementScriptOrderPreserved"]
        assert v["replacementTargetOrdinalPreserved"]
        assert v["replacementRecordReadbackExact"]
        assert v["replacementNonTargetRecordsIdentical"] == 24
        assert m["splice"]["emitter"]["nativeTable"]["sha256"] == mse.NATIVE_TABLE_SHA256
        assert m["unproven"], "generated bytecode must remain explicitly unproven until runtime"
        verified = pa.verify_manifest(m["manifest_path"], lab=f.lab)
        assert verified["ok"], verified
        assert verified["checks"]["splice_anchor_still_present_in_source"]
        assert verified["checks"]["splice_insert_present_in_output"]
        return (f"Setup stayed at ordinal {setup_ordinal}; 25 scripts, 24/24 non-target records "
                f"identical, {len(want_instructions)} emitted instructions parsed back")
    check("replace-script emits the damage pilot in Setup's existing slot", run)

    refuses("replace-script is gated behind explicit length-change authorisation",
            pa.LengthChangeRefused,
            lambda: f.author([{"op": "replace-script", "script": "Setup",
                               "program": PILOT_PROGRAM}],
                             src=f.src100, name="replace_no_auth"))

    bad_bool = json.loads(json.dumps(PILOT_PROGRAM))
    bad_bool[1]["args"] = [{"bool": 1}]
    refuses("the emitter refuses an implicit integer-as-bool recipe",
            pa.IntentError,
            lambda: f.author([{"op": "replace-script", "script": "Setup",
                               "program": bad_bool}], src=f.src100,
                             allow_length_change=True, name="replace_bad_bool"))

    bad_flow = json.loads(json.dumps(PILOT_PROGRAM))
    bad_flow[0] = {"op": "if", "condition": {"bool": True}}
    refuses("the bounded emitter refuses invented control flow",
            pa.IntentError,
            lambda: f.author([{"op": "replace-script", "script": "Setup",
                               "program": bad_flow}], src=f.src100,
                             allow_length_change=True, name="replace_bad_flow"))

    uninitialised = [PILOT_PROGRAM[1], PILOT_PROGRAM[0]]
    refuses("the emitter refuses a target used before its value exists",
            pa.IntentError,
            lambda: f.author([{"op": "replace-script", "script": "Setup",
                               "program": uninitialised}], src=f.src100,
                             allow_length_change=True, name="replace_uninitialised"))

    def sabotage_name_guard():
        original = pa.mse.emit_record_from_lab
        def wrong_name(*args, **kwargs):
            emitted = original(*args, **kwargs)
            record = emitted.record[:4] + b"Other" + emitted.record[9:]
            return mse.EmittedRecord(record, emitted.instructions, emitted.symbols, emitted.metadata)
        pa.mse.emit_record_from_lab = wrong_name
        try:
            f.author([{"op": "replace-script", "script": "Setup",
                       "program": PILOT_PROGRAM}], src=f.src100,
                     allow_length_change=True, name="replace_wrong_name")
        finally:
            pa.mse.emit_record_from_lab = original
    falsify("...and changing the emitted record name is caught before write", sabotage_name_guard)

    def sabotage_splice_verify():
        m = json.loads(json.dumps(state["manifest"]))
        m["splice"]["insert_sha256"] = "0" * 64
        path = f.out / "bad-splice-hash.manifest.json"
        path.write_text(json.dumps(m), encoding="utf-8")
        result = pa.verify_manifest(path, lab=f.lab)
        assert result["ok"], "verify accepted a false inserted-record hash"
    falsify("...and verify checks the complete inserted record, not only the archive hash",
            sabotage_splice_verify)

    def sabotage_chunk_size_source_anchor():
        """Re-hash a source with one wrong size field; only the edit anchor can catch it."""
        m = json.loads(json.dumps(state["manifest"]))
        size_edit = next(edit for edit in m["edits"] if edit["kind"] == "chunk-size")
        _root, aya, _sp, _ba = bea_lab.load(f.lab)
        _raw, inflated, blocks = aya.read_aya(m["source"]["path"])
        changed = bytearray(inflated)
        changed[size_edit["offset"]] ^= 1
        bad_source = f.out / "wrong-chunk-size-source.aya"
        aya.write_aya(str(bad_source), bytes(changed), [row[1] for row in blocks])
        bad_raw, bad_inflated, bad_blocks = aya.read_aya(str(bad_source))
        m["source"].update({
            "path": str(bad_source),
            "sha256": pa.sha256(bad_raw),
            "bytes": len(bad_raw),
            "inflated_sha256": pa.sha256(bad_inflated),
            "inflated_bytes": len(bad_inflated),
            "blocks": [row[1] for row in bad_blocks],
        })
        manifest = f.out / "wrong-chunk-size-source.manifest.json"
        manifest.write_text(json.dumps(m), encoding="utf-8")
        result = pa.verify_manifest(manifest, lab=f.lab)
        assert result["checks"]["source_sha256"]
        assert result["checks"]["source_inflated_sha256"]
        assert result["ok"], "verify ignored a changed source chunk-size anchor"
    falsify("...and verify authenticates chunk-size source anchors after re-hashing",
            sabotage_chunk_size_source_anchor)

    def tampered_signature_table():
        lab = f.work / "tampered-lab"
        dst = lab / mse.NATIVE_TABLE_REL
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(Path(f.lab) / mse.NATIVE_TABLE_REL, dst)
        raw = bytearray(dst.read_bytes())
        raw[len(raw) // 2] ^= 1
        dst.write_bytes(raw)
        mse.load_native_table(lab)
    falsify("...and a changed native signature table is rejected by its SHA-256 pin",
            tampered_signature_table)


def t_unexercised_types(f: Fix) -> None:
    def run():
        assert 5 not in pa.WRITABLE_TAGS and 6 not in pa.WRITABLE_TAGS, \
            "tags 5 and 6 are never exercised by shipped data (spec S9.4)"
        return "tags 5 and 6 are not writable -- the gap is respected, not guessed across"
    check("unexercised type tags 5 and 6 are refused by construction", run)

    refuses("set-constant refuses a type-0 symbol (no value bytes in the stream)",
            pa.IntentError,
            lambda: f.author([{"op": "set-constant", "script": "LapTimer",
                               "symbol": "lapping", "value": 1}], name="tag0"))

    refuses("set-constant refuses an unknown symbol name",
            pa.IntentError,
            lambda: f.author([{"op": "set-constant", "script": "LapTimer",
                               "symbol": "nosuchsymbol", "value": 1}], name="nosym"))

    refuses("an unknown script name is refused",
            pa.IntentError,
            lambda: f.author([{"op": "set-constant", "script": "NoSuchScript",
                               "symbol": "x", "value": 1}], name="noscript"))


def t_path_guard(f: Fix) -> None:
    refuses("refuses to write into the pristine specimen tree",
            pa.ProbeError,
            lambda: pa.author(f.src, f.res / "999_probe.aya", [], lab=f.lab, force=True))

    refuses("refuses to overwrite the source archive",
            pa.ProbeError,
            lambda: pa.author(f.src, f.src, [], lab=f.lab, force=True))

    refuses("refuses to write into an existing output without force",
            pa.ProbeError,
            lambda: pa.author(f.src, f.out / "identity.aya", [], lab=f.lab, force=False))


def t_verify(f: Fix) -> None:
    state = {}

    def run():
        m = f.author([{"op": "set-constant", "script": "LapTimer", "symbol": "data31536",
                       "value": 4.0}], name="verifyme")["probe"]
        state["m"] = m
        r = pa.verify_manifest(m["manifest_path"], lab=f.lab)
        assert r["ok"], r
        return "manifest re-verified from disk: source, anchors, output, blocks"
    check("verify re-checks an authored archive against its manifest", run)

    def sabotage():
        """Tamper with the output; verify must notice."""
        m = state["m"]
        tampered = Path(f.out) / "tampered.aya"
        shutil.copy(m["output"]["path"], tampered)
        b = bytearray(tampered.read_bytes())
        b[len(b) // 2] ^= 0xFF
        tampered.write_bytes(bytes(b))
        m2 = dict(m)
        m2["output"] = dict(m["output"], path=str(tampered))
        p2 = Path(f.out) / "tampered.manifest.json"
        p2.write_text(json.dumps(m2), encoding="utf-8")
        r = pa.verify_manifest(p2, lab=f.lab)
        assert r["ok"], f"verify reported FAILED on the tampered archive: {r.get('error', '')}"
    falsify("...and verify reports failure on a tampered archive", sabotage)

    def sabotage2():
        """Point a manifest at a DIFFERENT source; the anchors must stop matching."""
        m = dict(state["m"])
        m["source"] = dict(m["source"], path=f.src100)
        p2 = Path(f.out) / "wrongsrc.manifest.json"
        p2.write_text(json.dumps(m), encoding="utf-8")
        r = pa.verify_manifest(p2, lab=f.lab)
        assert r["ok"], "verify passed a manifest pointing at the wrong source archive"
    falsify("...and verify fails when the manifest names the wrong source", sabotage2)


def t_no_collateral(f: Fix, before: dict) -> None:
    def run():
        for p, h in before.items():
            assert sha_file(p) == h, f"{p} CHANGED during the test run"
        return f"{len(before)} protected files unchanged (specimen + source archives)"
    check("the specimen and every source archive are byte-identical after the run", run)


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab")
    ap.add_argument("--keep", action="store_true", help="keep the work directory")
    a = ap.parse_args()

    work = Path(tempfile.mkdtemp(prefix="probe_test_"))
    try:
        f = Fix(a.lab, work)
    except bea_lab.LabNotFound as exc:
        print(f"LabNotFound: {exc}", file=sys.stderr)
        return 3

    protected = {str(f.specimen): sha_file(f.specimen),
                 f.src: sha_file(f.src),
                 f.src100: sha_file(f.src100)}

    print(f"lab      {f.lab}")
    print(f"source   {f.src}")
    print(f"workdir  {work}\n")

    for t in (t_identity, t_set_constant, t_set_script_trace, t_anchor_guard, t_overlap, t_retarget_call,
              t_poison, t_framing_gate, t_length_change, t_splice, t_replace_script,
              t_unexercised_types, t_path_guard, t_verify):
        t(f)
    t_no_collateral(f, protected)

    width = max(len(n) for _, n, _ in RESULTS)
    for status, name, detail in RESULTS:
        print(f"  {status:<8} {name:<{width}}  {detail}")

    npass = sum(1 for s, _, _ in RESULTS if s == "PASS")
    nproven = sum(1 for s, _, _ in RESULTS if s == "PROVEN")
    nfail = sum(1 for s, _, _ in RESULTS if s == "FAIL")
    nvac = sum(1 for s, _, _ in RESULTS if s == "VACUOUS")
    print(f"\n  {npass} checks passed, {nproven} guards proven falsifiable, "
          f"{nfail} failed, {nvac} vacuous")

    if not a.keep:
        shutil.rmtree(work, ignore_errors=True)
    else:
        print(f"  work kept at {work}")
    return 0 if (nfail == 0 and nvac == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
