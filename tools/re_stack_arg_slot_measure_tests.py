#!/usr/bin/env python3
"""Self-tests for re_stack_arg_slot_measure.py.

The instrument's job is to be a SECOND witness for the ABI cleanup axis, so a
version of it that cannot fail would be worse than none: it would launder one
assertion into two. Most of what follows is therefore falsification.

Three kinds of test:

  SYNTHETIC — hand-assembled bodies whose right answer is known by construction,
  including the exact shapes that broke the path-oblivious predecessor: an
  aligned EBP frame, a mid-block argument forward, a scratch area under
  `and esp, -16`, EBP genuinely used as a data pointer, and a rejoin whose two
  paths carry different stack depths.

  SPECIMEN — measurements against the pristine `74154bfa...` BEA.exe, including
  the eleven `CFastVB__DispatchOp_*` bodies whose "EBP over-read" was the known
  corroborator misfire, and the `_alloca_probe` frames whose stack the model has
  to get from EAX.

  CONTROL — the negative and sensitivity probes: non-instruction-boundary VAs,
  a corrupted RET immediate that must NOT move the measure (independence), and a
  corrupted `sub esp, imm` that MUST move it (non-vacuity).

Specimen tests skip cleanly when the pristine file or the body index is absent,
so this file still runs on a fresh clone; the synthetic and control tests over
synthetic bodies do not skip.
"""
from __future__ import annotations

import json
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import re_stack_arg_slot_measure as M  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SPECIMEN = (
    REPO
    / "local-lab"
    / "pristine-verification-2026-07-26"
    / "pristine-target"
    / "BEA.exe"
)

# The body index this campaign already produced (RET ground truth for all 8,329
# declared bodies). Env override keeps the tests runnable from another lane.
import os  # noqa: E402

BODY_INDEX = Path(
    os.environ.get(
        "BEA_BODY_INDEX",
        str(Path(os.environ.get("TEMP", "/tmp")) / "byte_truth.json"),
    )
)


# ------------------------------------------------------------------ synthetic


IMAGE_BASE = 0x00400000
CODE_VA = 0x00401000


def synth(code: bytes) -> M.Specimen:
    """A minimal PE whose single section holds `code` at CODE_VA.

    Built by hand rather than by copying the specimen so a synthetic test can
    never accidentally measure real bytes.
    """
    section_raw = 0x400
    data = bytearray(section_raw + max(len(code), 0x200))
    e_lfanew = 0x80
    struct.pack_into("<I", data, 0x3C, e_lfanew)
    data[e_lfanew : e_lfanew + 4] = b"PE\0\0"
    struct.pack_into("<H", data, e_lfanew + 6, 1)  # NumberOfSections
    struct.pack_into("<H", data, e_lfanew + 20, 0xE0)  # SizeOfOptionalHeader
    struct.pack_into("<I", data, e_lfanew + 24 + 28, IMAGE_BASE)
    sec = e_lfanew + 24 + 0xE0
    data[sec : sec + 8] = b".text\0\0\0"
    struct.pack_into(
        "<IIII", data, sec + 8, 0x1000, CODE_VA - IMAGE_BASE, len(data) - section_raw, section_raw
    )
    data[section_raw : section_raw + len(code)] = code
    return M.Specimen(bytes(data))


def measure(code: bytes, **kw) -> dict:
    spec = synth(code)
    return M.measure_body(spec, CODE_VA, [(CODE_VA, CODE_VA + len(code))], **kw)


class Synthetic(unittest.TestCase):
    def test_standard_ebp_frame_two_args(self):
        # push ebp; mov ebp,esp; mov eax,[ebp+8]; mov ecx,[ebp+0xc]; pop ebp; ret 8
        code = bytes.fromhex("55" "8bec" "8b4508" "8b4d0c" "5d" "c20800")
        r = measure(code)
        self.assertEqual("DETERMINATE", r["status"])
        self.assertEqual("EBP_STANDARD", r["frame"])
        self.assertEqual(-4, r["frame_ebp_offset"])
        self.assertEqual([0, 1], r["arg_slots_touched"])
        self.assertEqual(8, r["arg_bytes_min"])
        self.assertIs(True, r["ret_delta_ok"])

    def test_esp_frame_reads_argument_past_the_reservation(self):
        # sub esp,0x10 ; mov eax,[esp+0x14] ; add esp,0x10 ; ret 4
        # entry-relative 0x14-0x10 = +4 -> slot 0
        code = bytes.fromhex("83ec10" "8b442414" "83c410" "c20400")
        r = measure(code)
        self.assertEqual("ESP_ONLY", r["frame"])
        self.assertEqual([0], r["arg_slots_touched"])
        self.assertEqual(4, r["arg_bytes_min"])

    def test_aligned_ebp_frame_is_not_an_over_read(self):
        """The exact `CFastVB__DispatchOp_*` shape that produced slot 71.

        sub esp,0x10c ; mov ebp,esp ; and esp,-16 ; mov ecx,[ebp+0x124] ;
        mov esp,ebp ; add esp,0x10c ; ret 24

        `[ebp+0x124]` is entry-relative +0x18: slot 5, 24 bytes. Assuming
        `[ebp+8]` is slot 0 gives slot 71 and 288 bytes, which is the misfire.
        """
        code = bytes.fromhex(
            "81ec0c010000" "8bec" "83e4f0" "8b8d24010000" "8be5" "81c40c010000" "c21800"
        )
        r = measure(code)
        self.assertEqual("DETERMINATE", r["status"])
        self.assertEqual("EBP_ALIGNED", r["frame"])
        self.assertEqual(-0x10C, r["frame_ebp_offset"])
        self.assertEqual(5, r["max_slot_touched"])
        self.assertEqual(24, r["arg_bytes_min"])
        self.assertNotEqual(71, r["max_slot_touched"])

    def test_scratch_under_alignment_is_never_an_argument(self):
        """Reads below an `and esp,-16` boundary are locals, and must not count."""
        # sub esp,0x40 ; mov ebp,esp ; and esp,-16 ; mov eax,[esp] ;
        # mov ecx,[esp+0x20] ; mov esp,ebp ; add esp,0x40 ; ret
        code = bytes.fromhex(
            "83ec40" "8bec" "83e4f0" "8b0424" "8b4c2420" "8be5" "83c440" "c3"
        )
        r = measure(code)
        self.assertEqual("DETERMINATE", r["status"])
        self.assertEqual(-1, r["max_slot_touched"])
        self.assertEqual(0, r["arg_bytes_min"])

    def test_ebp_as_a_data_pointer_is_refused(self):
        """A real non-frame EBP must not be read as an argument frame.

        This is the failure mode the 11 flagged rows were BELIEVED to have. They
        did not, but the detector still has to exist.
        """
        # push ebp; mov ebp,[eax]; mov ecx,[ebp+0x10]; pop ebp; ret
        code = bytes.fromhex("55" "8b28" "8b4d10" "5d" "c3")
        r = measure(code)
        self.assertEqual("DETERMINATE", r["status"])
        self.assertEqual(-1, r["max_slot_touched"], "data-pointer EBP counted as a frame")
        self.assertEqual(0, r["arg_bytes_min"])

    def test_mid_block_argument_forward_is_path_correct(self):
        """`push [esp+8]` at a shifted delta must resolve to the right slot.

        push ebx           ; delta -4
        push dword [esp+8] ; entry-relative 8-4 = +4 -> slot 0
        call <unresolved>  ; ESP unknown afterwards
        """
        code = bytes.fromhex("53" "ff742408" "e800000000" "c3")
        r = measure(code)
        self.assertEqual([0], r["arg_slots_touched"])
        self.assertEqual(4, r["arg_bytes_min"])
        # the call had no resolver, so the tail is unknown, not invented
        self.assertEqual(1, r["unresolved_calls"])

    def test_path_oblivious_answer_is_not_produced(self):
        """A block reached only at a deeper delta, read at the shallow one, lies.

        sub esp,8            ; -8
        jmp L                ;
        (unreached filler)
        L: mov eax,[esp+0xc] ; entry-relative 0xc-8 = +4 -> slot 0
        add esp,8 ; ret

        A linear sweep that carried `sub esp,8` past the jump and then read
        `[esp+0xc]` at delta 0 would report entry-relative 0xc, slot 2.
        """
        code = bytes.fromhex("83ec08" "eb02" "9090" "8b44240c" "83c408" "c3")
        r = measure(code)
        self.assertEqual([0], r["arg_slots_touched"])
        self.assertNotIn(2, r["arg_slots_touched"])

    def test_rejoin_with_two_different_depths_is_reported_not_averaged(self):
        code = bytes.fromhex(
            # 0: je +3   (to the push-free path)
            "7401"
            # 2: push eax     (delta -4 on the taken-through path)
            "50"
            # 3: mov eax,[esp+4]
            "8b442404"
            # 7: ret
            "c3"
        )
        r = measure(code)
        self.assertEqual("UNDETERMINED", r["status"])
        self.assertEqual("REJOIN_CONFLICT", r["reason"])
        self.assertTrue(r["rejoin_conflicts"], "conflict was not reported")
        self.assertEqual(0, r["arg_bytes_min"], "a conflicted body still produced a number")

    def test_tail_dispatch_reports_no_local_cleanup(self):
        # mov eax,[esp+4] ; jmp <outside the declared body>
        code = bytes.fromhex("8b442404" "e9f0ffff00")
        r = measure(code)
        self.assertEqual("NONE_TAIL_DISPATCH", r["local_cleanup"])
        self.assertIsNone(r["ret_delta_ok"], "a body with no RET claimed a RET oracle verdict")

    def test_ret_at_a_nonzero_depth_is_refused(self):
        """The internal oracle: `push eax; ret` returns with ESP displaced."""
        code = bytes.fromhex("8b442408" "50" "c3")
        r = measure(code)
        self.assertEqual("UNDETERMINED", r["status"])
        self.assertEqual("RET_DELTA_INCONSISTENT", r["reason"])
        self.assertEqual(0, r["arg_bytes_min"])

    def test_entry_off_an_instruction_boundary_is_refused(self):
        code = bytes.fromhex("55" "8bec" "8b4508" "5d" "c3")
        spec = synth(code)
        r = M.measure_body(spec, CODE_VA + 1, [(CODE_VA, CODE_VA + len(code))])
        self.assertEqual("UNDETERMINED", r["status"])

    def test_alloca_probe_moves_the_frame_by_eax(self):
        """Without the probe the whole frame is off by the allocation size.

        Lay the probe's real bytes at a second VA and call it, then read what
        should be argument slot 0 through the post-probe ESP.
        """
        probe = bytes.fromhex(
            "51" "3d00100000" "8d4c2408" "7214"
            "81e900100000" "2d00100000" "8501" "3d00100000" "73ec"
            "2bc8" "8bc4" "8501" "8be1" "8b08" "8b4004" "50" "c3"
        )
        # mov eax,0x2000 ; call probe ; mov ecx,[esp+0x2004] ; add esp,0x2000 ; ret
        head = bytes.fromhex("b800200000") + b"\xe8" + struct.pack("<i", 0x40) + bytes.fromhex(
            "8b8c2404200000" "81c400200000" "c3"
        )
        code = head + b"\x90" * (0x45 - len(head)) + probe
        spec = synth(code)
        probe_va = CODE_VA + 0x45
        bodies = {
            CODE_VA: {"ranges": [(CODE_VA, CODE_VA + len(head))], "ret_imms": [0], "name": "sub"},
            probe_va: {
                "ranges": [(probe_va, probe_va + len(probe))],
                "ret_imms": [0],
                "name": "probe",
            },
        }
        self.assertIn(probe_va, M.find_stack_probes(spec, bodies), "probe not found by bytes")
        resolver, diag = M.build_cleanup_resolver(spec, bodies)
        r = M.measure_body(spec, CODE_VA, bodies[CODE_VA]["ranges"], resolver)
        self.assertEqual("DETERMINATE", r["status"])
        self.assertEqual(0, r["max_slot_touched"], f"probe frame mis-anchored: {r}")
        self.assertIs(True, r["ret_delta_ok"])

    def test_jump_table_targets_are_followed_and_the_table_terminates(self):
        # cmp eax,1 ; ja +5 ; jmp [eax*4+table] ; <arm0> mov ecx,[esp+4]; ret
        #                                          <arm1> ret
        table_va = CODE_VA + 0x20
        code = bytearray(b"\xcc" * 0x30)
        code[0:3] = bytes.fromhex("83f801")  # cmp eax,1
        code[3:5] = bytes.fromhex("770c")  # ja +12 -> 0x11
        code[5:12] = bytes.fromhex("ff2485") + struct.pack("<I", table_va)
        code[12:17] = bytes.fromhex("8b4c2404") + b"\xc3"  # arm0 at +12
        code[17:18] = b"\xc3"  # arm1 at +17 (the `ja` target)
        code[0x20:0x28] = struct.pack("<II", CODE_VA + 12, CODE_VA + 17)
        code[0x28:0x2C] = struct.pack("<I", 0xCCCCCCCC)
        spec = synth(bytes(code))
        r = M.measure_body(spec, CODE_VA, [(CODE_VA, CODE_VA + 0x20)])
        self.assertEqual("DETERMINATE", r["status"])
        self.assertEqual([0], r["arg_slots_touched"], "jump-table arm not reached")
        self.assertIn("JMP_TABLE", r["terminators"])

    def test_int_stub_does_not_fall_through(self):
        """`add esp,N; int 6` arms of a table must not join the next arm."""
        code = bytes.fromhex("83ec08" "83c408" "cd06" "8b442404" "c3")
        r = measure(code)
        # the `int 6` terminates, so `mov eax,[esp+4]` is unreached, not merged
        self.assertEqual("DETERMINATE", r["status"])
        self.assertEqual([], r["arg_slots_touched"])
        self.assertGreater(r["unreached_bytes"], 0)


class CallerSide(unittest.TestCase):
    def test_add_esp_after_the_call_is_read_exactly(self):
        target = CODE_VA + 0x20
        code = bytearray(b"\x90" * 0x30)
        code[0:2] = bytes.fromhex("6a01")  # push 1
        code[2:4] = bytes.fromhex("6a02")  # push 2
        code[4:9] = b"\xe8" + struct.pack("<i", target - (CODE_VA + 9))
        code[9:12] = bytes.fromhex("83c408")  # add esp,8
        code[12:13] = b"\xc3"
        code[0x20:0x21] = b"\xc3"
        spec = synth(bytes(code))
        bodies = {
            CODE_VA: {"ranges": [(CODE_VA, CODE_VA + 13)], "ret_imms": [0], "name": "caller"},
            target: {"ranges": [(target, target + 1)], "ret_imms": [0], "name": "callee"},
        }
        sites = M.collect_call_sites(spec, bodies)
        self.assertIn(target, sites)
        self.assertEqual(1, len(sites[target]))
        self.assertEqual(8, sites[target][0]["add_esp"])
        self.assertEqual(8, sites[target][0]["push_run"])
        w = M.caller_witness(sites[target])
        self.assertEqual("CALLER_CLEANUP_ADD_ESP", w["witness_kind"])
        self.assertEqual(8, w["witness"])

    def test_push_run_stops_at_the_previous_call(self):
        """An earlier call's arguments must not be counted for a later call."""
        target = CODE_VA + 0x30
        code = bytearray(b"\x90" * 0x40)
        code[0:2] = bytes.fromhex("6a01")
        code[2:7] = b"\xe8" + struct.pack("<i", target - (CODE_VA + 7))
        code[7:9] = bytes.fromhex("6a02")
        code[9:14] = b"\xe8" + struct.pack("<i", target - (CODE_VA + 14))
        code[14:15] = b"\xc3"
        code[0x30:0x31] = b"\xc3"
        spec = synth(bytes(code))
        bodies = {
            CODE_VA: {"ranges": [(CODE_VA, CODE_VA + 15)], "ret_imms": [0], "name": "caller"},
            target: {"ranges": [(target, target + 1)], "ret_imms": [0], "name": "callee"},
        }
        sites = M.collect_call_sites(spec, bodies)
        runs = sorted(s["push_run"] for s in sites[target])
        self.assertEqual([4, 4], runs, f"push run leaked across a call: {sites[target]}")

    def test_disagreeing_call_sites_are_flagged_not_averaged(self):
        sites = [
            {"caller": "0x1", "site": "0x1", "add_esp": 8, "push_run": 8, "push_run_clean": True},
            {"caller": "0x2", "site": "0x2", "add_esp": 12, "push_run": 12, "push_run_clean": True},
        ]
        w = M.caller_witness(sites)
        self.assertTrue(w["conflict"])
        self.assertIsNone(w["witness"])
        self.assertEqual("CALLER_CLEANUP_CONFLICT", w["witness_kind"])

    def test_an_e8_byte_inside_an_immediate_is_not_a_call_site(self):
        """Boundary validation. `mov eax, 0x9090e8` embeds an E8 byte.

        A reducer in this campaign once scanned for the first E8 BYTE with no
        boundary check; this asserts the call index does not repeat that.
        """
        code = bytes.fromhex("b8e8909000") + b"\xc3"
        spec = synth(code)
        bodies = {CODE_VA: {"ranges": [(CODE_VA, CODE_VA + len(code))], "ret_imms": [0], "name": "x"}}
        sites = M.collect_call_sites(spec, bodies)
        self.assertEqual({}, dict(sites))


class Controls(unittest.TestCase):
    """Negative and sensitivity controls over synthetic bodies."""

    def test_random_bytes_are_mostly_refused_and_never_silently_accepted(self):
        import random

        rng = random.Random(20260817)
        accepted = 0
        n = 2000
        for _ in range(n):
            code = bytes(rng.randrange(256) for _ in range(48))
            r = measure(code)
            if (
                r["status"] == "DETERMINATE"
                and r["arg_bytes_min"] > 0
                and r["ret_delta_ok"] is True
            ):
                accepted += 1
        # Random bytes are not code; the RET-depth oracle plus the delta lattice
        # must keep the accept rate low. This is a measured ceiling, not zero:
        # 48 random bytes CAN decode to a valid balanced stub.
        self.assertLess(accepted / n, 0.05, f"{accepted}/{n} random bodies accepted")

    def test_corrupting_the_ret_immediate_does_not_move_the_measure(self):
        code = bytes.fromhex("55" "8bec" "8b4508" "8b4d0c" "5d" "c20800")
        base = measure(code)
        alt = measure(code[:-2] + bytes.fromhex("4400"))  # ret 0x44
        self.assertEqual(base["arg_bytes_min"], alt["arg_bytes_min"])
        self.assertEqual(base["status"], alt["status"])

    def test_corrupting_the_frame_does_move_the_measure(self):
        # sub esp,0x10 ; mov eax,[esp+0x14] ; add esp,0x10 ; ret
        code = bytes.fromhex("83ec10" "8b442414" "83c410" "c3")
        base = measure(code)
        self.assertEqual(4, base["arg_bytes_min"])
        # widen the reservation to 0x14: [esp+0x14] is now entry-relative 0
        alt = measure(bytes.fromhex("83ec14" "8b442414" "83c414" "c3"))
        self.assertNotEqual(base["arg_bytes_min"], alt["arg_bytes_min"])
        self.assertEqual(0, alt["arg_bytes_min"])


def _load_specimen_fixtures():
    if not SPECIMEN.is_file() or not BODY_INDEX.is_file():
        return None, None
    spec = M.Specimen.load(SPECIMEN)
    bodies = M.load_bodies(BODY_INDEX)
    return spec, bodies


@unittest.skipUnless(
    SPECIMEN.is_file() and BODY_INDEX.is_file(),
    f"needs {SPECIMEN} and a body index (BEA_BODY_INDEX env var)",
)
class AgainstTheSpecimen(unittest.TestCase):
    spec = None
    bodies = None
    resolver = None

    @classmethod
    def setUpClass(cls):
        cls.spec, cls.bodies = _load_specimen_fixtures()
        cls.md = M._decoder()
        cls.resolver, cls.diag = M.build_cleanup_resolver(cls.spec, cls.bodies, cls.md)

    def m(self, va):
        # `cls.resolver` is a plain function held in a CLASS attribute, so reading
        # it as `self.resolver` binds it and silently prepends `self` — the call
        # then arrives as resolve(self, va, state) and every specimen-backed test
        # errors with "takes 2 positional arguments but 3 were given". Read it off
        # the class to get the function itself.
        resolver = type(self).__dict__.get("resolver") or AgainstTheSpecimen.__dict__["resolver"]
        return M.measure_body(self.spec, va, self.bodies[va]["ranges"], resolver, self.md)

    def test_specimen_identity_and_section_mapping(self):
        self.assertEqual(M.PRISTINE_SHA256, self.spec.sha256)
        self.assertEqual(0x00400000, self.spec.image_base)
        # the campaign's flat rule, re-derived from the headers rather than trusted
        self.assertTrue(self.spec.flat_mapping_holds_for(".text"))
        self.assertTrue(self.spec.flat_mapping_holds_for(".rdata"))
        self.assertTrue(self.spec.flat_mapping_holds_for(".data"))
        self.assertFalse(self.spec.flat_mapping_holds_for(".rsrc"))
        # .data raw ends at VA 0x00661000; beyond that is BSS with no bytes
        self.assertIsNotNone(self.spec.offset(0x00660FFC))
        self.assertIsNone(self.spec.offset(0x00661004))

    def test_the_eleven_dispatchop_over_reads_now_match_their_ret(self):
        """The known corroborator misfire, resolved rather than excused.

        Every one of these was reported as an EBP over-read; every one is an
        aligned EBP frame whose argument extent equals its RET immediate.
        """
        misfires = [
            0x005A3A40,
            0x005A3CA0,
            0x005A3F00,
            0x005A4160,
            0x005A4480,
            0x005A4ECF,
            0x005A5BD7,
            0x005A5F28,
            0x005A6013,
            0x005A923F,
            0x005AA5C0,
        ]
        for va in misfires:
            with self.subTest(va=f"0x{va:08x}"):
                r = self.m(va)
                self.assertEqual("DETERMINATE", r["status"])
                self.assertEqual("EBP_ALIGNED", r["frame"])
                self.assertEqual(
                    self.bodies[va]["ret_imms"],
                    [r["arg_bytes_min"]],
                    f"aligned frame still disagrees with RET: {r}",
                )

    def test_the_alloca_probe_is_found_by_its_bytes(self):
        probes = M.find_stack_probes(self.spec, self.bodies)
        self.assertIn(0x0055DEF0, probes)

    def test_alloca_probe_callers_measure_a_sane_frame(self):
        """Six cohort bodies produced fictional slots before EAX was tracked."""
        for va, expect in (
            (0x0042B840, 12),
            (0x00465710, 40),
            (0x00503EF0, 8),
            (0x0051C280, 8),
            (0x00527990, 12),
        ):
            with self.subTest(va=f"0x{va:08x}"):
                r = self.m(va)
                self.assertEqual("DETERMINATE", r["status"])
                self.assertEqual(expect, r["arg_bytes_min"])
                self.assertLess(r["arg_bytes_min"], 256, "fictional slot survived")

    def test_the_seh_prolog_trampoline_is_refused(self):
        """`push eax; ret` returns with ESP displaced: no honest slot exists."""
        r = self.m(0x005D06F0)
        self.assertEqual("UNDETERMINED", r["status"])
        self.assertEqual("RET_DELTA_INCONSISTENT", r["reason"])

    def test_a_mid_function_fragment_is_refused(self):
        """0x004acde0 is declared as a function but is the tail of a larger one.

        It opens reading `[esp+0x40]` with EBX already live and closes with
        `pop edi/esi/ebp/ebx; add esp,0xb8; ret 0x10`, an epilogue for a
        prologue outside the declared range. Its RET immediate therefore belongs
        to the enclosing function, not to this entity.
        """
        r = self.m(0x004ACDE0)
        self.assertEqual("UNDETERMINED", r["status"])
        self.assertEqual("RET_DELTA_INCONSISTENT", r["reason"])

    def test_agreement_with_the_prior_ebp_only_corroborator(self):
        """Positive control. 252 EBP frames; disagreement must be explained.

        The only permitted disagreements are the eleven aligned-EBP DispatchOp
        bodies (the prior measure assumed `[ebp+8]` was slot 0) and bodies this
        instrument refuses outright.
        """
        prior_path = BODY_INDEX.parent / "frame_corr.json"
        if not prior_path.is_file():
            self.skipTest("prior frame_corr.json not available")
        prior = json.loads(prior_path.read_text(encoding="utf-8"))
        allowed = {
            0x005A3A40,
            0x005A3CA0,
            0x005A3F00,
            0x005A4160,
            0x005A4480,
            0x005A4ECF,
            0x005A5BD7,
            0x005A5F28,
            0x005A6013,
            0x005A923F,
            0x005AA5C0,
        }
        agree = 0
        unexplained = []
        for addr, rec in prior.items():
            if not rec.get("ebp_frame"):
                continue
            va = int(addr, 16)
            r = self.m(va)
            old = (rec["max_arg_slot_read"] + 1) * 4 if rec["max_arg_slot_read"] >= 0 else 0
            if r["status"] != "DETERMINATE":
                continue  # refusal is an explanation, and is counted separately
            if old == r["arg_bytes_min"]:
                agree += 1
            elif va not in allowed:
                unexplained.append((addr, old, r["arg_bytes_min"], r["frame"]))
        self.assertEqual([], unexplained, "unexplained disagreement with the prior measure")
        self.assertGreaterEqual(agree, 230)

    def test_no_cohort_body_reports_an_absurd_argument_extent(self):
        """A ceiling, because the failures this replaces all looked like this.

        The predecessor reported slot 2513 and slot 71. Nothing in the shipped
        image passes 64 dwords of stack arguments; anything that claims to is a
        broken frame, and must come back UNDETERMINED instead.
        """
        worst = []
        for va in list(self.bodies)[:2000]:
            r = self.m(va)
            if r["status"] == "DETERMINATE" and r["max_slot_touched"] > 64:
                worst.append((f"0x{va:08x}", r["max_slot_touched"]))
        self.assertEqual([], worst)

    def test_corrupting_ret_immediates_over_real_bodies_moves_nothing(self):
        addrs = list(self.bodies)[:400]
        out = M.negative_control_corrupt_ret(self.spec, self.bodies, addrs, self.md)
        self.assertGreater(out["checked"], 20, "control was vacuous")
        self.assertEqual(0, out["moved"], out["moved_examples"])

    def test_corrupting_real_frames_does_move_the_measure(self):
        addrs = list(self.bodies)[:400]
        out = M.sensitivity_control_corrupt_frame(self.spec, self.bodies, addrs, self.md)
        self.assertGreater(out["checked"], 10, "control was vacuous")
        self.assertGreater(out["moved"], 0, "the measure ignores the frame it claims to read")


if __name__ == "__main__":
    unittest.main(verbosity=2)
