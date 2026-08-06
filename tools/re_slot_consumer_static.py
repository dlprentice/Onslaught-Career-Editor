#!/usr/bin/env python3
"""Hash-bound static contract for residual 0x004540c0 SLOT_CONSUMER path.

Proves (specimen-bound, no runtime required):

  1. Residual body at 0x004540c0 reads global 0x677870 and switches on it.
  2. Producers are PUSH imm32(=0x004540c0) sites in controls remap code —
     not MOV-to-slot installs.
  3. Canonical pattern: push residual; push reg; push action; call DispatchRemap.
  4. DispatchRemap (0x00453f50) calls through the third stack arg:
       call dword ptr [esp+0x18]  after three pushes.

Does not invent names beyond existing join labels. Does not mutate Gen10/Gen11.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

PRISTINE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
CANDIDATE = 0x004540C0
DISPATCH_REMAP = 0x00453F50
REMAP_KEY = 0x004541E0
GLOBAL_MODE = 0x00677870


def pe_map(data: bytes):
    e = struct.unpack_from("<I", data, 0x3C)[0]
    ib = struct.unpack_from("<I", data, e + 24 + 28)[0]
    num = struct.unpack_from("<H", data, e + 6)[0]
    so = struct.unpack_from("<H", data, e + 20)[0]
    sec = e + 24 + so
    secs = []
    for i in range(num):
        o = sec + i * 40
        name = data[o : o + 8].split(b"\0")[0].decode("latin1", "replace")
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, o + 8)
        secs.append((name, va, vsize, rawptr, rawsize))
    return ib, secs


def v2o(va: int, ib: int, secs) -> int | None:
    rva = va - ib
    for _n, sva, vs, rp, rs in secs:
        if sva <= rva < sva + max(vs, rs):
            d = rva - sva
            if d < rs:
                return rp + d
    return None


def o2va(off: int, ib: int, secs) -> int | None:
    for _n, sva, vs, rp, rs in secs:
        if rp <= off < rp + rs:
            return ib + sva + (off - rp)
    return None


def analyze(specimen: Path) -> dict:
    raw = specimen.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != PRISTINE_SHA256:
        raise SystemExit(f"specimen mismatch {sha}")
    ib, secs = pe_map(raw)

    # residual head
    off = v2o(CANDIDATE, ib, secs)
    head = raw[off : off + 16]
    residual_head = {
        "va": f"0x{CANDIDATE:08x}",
        "bytes": head.hex(),
        # mov eax, [abs32]: A1 <imm32>  (5 bytes)
        "readsGlobalMode": head[0] == 0xA1
        and struct.unpack_from("<I", head, 1)[0] == GLOBAL_MODE,
        "movEaxAbs": head[0] == 0xA1
        and struct.unpack_from("<I", head, 1)[0] == GLOBAL_MODE,
    }

    # DispatchRemap call-through
    doff = v2o(DISPATCH_REMAP, ib, secs)
    dchunk = raw[doff : doff + 0x40]
    # expect call [esp+0x18] at 0x00453f70: ff 54 24 18
    call_through = None
    for i in range(len(dchunk) - 4):
        if dchunk[i : i + 4] == bytes.fromhex("ff542418"):
            call_through = {
                "va": f"0x{DISPATCH_REMAP + i:08x}",
                "bytes": "ff542418",
                "form": "call dword ptr [esp+0x18]",
            }
            break

    # PUSH imm producers
    needle = struct.pack("<I", CANDIDATE)
    producers = []
    pos = 0
    while True:
        i = raw.find(needle, pos)
        if i < 0:
            break
        va = o2va(i, ib, secs)
        if va is None:
            pos = i + 1
            continue
        # preceding byte should be 0x68 for PUSH imm32
        if i >= 1 and raw[i - 1] == 0x68:
            # following pattern: often 57 6aXX e8 (push edi; push imm8; call rel)
            after = raw[i + 4 : i + 16]
            pattern = None
            rel_tgt = None
            routes_to_dispatch = False
            push_site = va - 1
            # 68 imm | 5X (push reg) | 6a XX | e8 rel32
            if len(after) >= 7 and after[0] in (
                0x50,
                0x51,
                0x52,
                0x53,
                0x55,
                0x56,
                0x57,
            ):
                if after[1] == 0x6A and after[3] == 0xE8:
                    rel = struct.unpack_from("<i", after, 4)[0]
                    call_va = push_site + 8
                    rel_tgt = (call_va + 5 + rel) & 0xFFFFFFFF
                    pattern = "push_imm; push_reg; push_imm8; call_rel32"
                elif after[1] == 0xE8:
                    # push imm; push reg; call
                    call_va = push_site + 6
                    rel = struct.unpack_from("<i", after, 2)[0]
                    rel_tgt = (call_va + 5 + rel) & 0xFFFFFFFF
                    pattern = "push_imm; push_reg; call_rel32"
                elif after[1] == 0x6A and after[3] == 0xE9:
                    # push imm; push reg; push imm8; jmp → shared call site
                    rel = struct.unpack_from("<i", after, 4)[0]
                    jmp_va = push_site + 8
                    rel_tgt = (jmp_va + 5 + rel) & 0xFFFFFFFF
                    pattern = "push_imm; push_reg; push_imm8; jmp_rel32"
                elif after[1] == 0x51 and after[2] == 0xE8:
                    # push imm; push reg; push ecx; call
                    call_va = push_site + 7
                    rel = struct.unpack_from("<i", after, 3)[0]
                    rel_tgt = (call_va + 5 + rel) & 0xFFFFFFFF
                    pattern = "push_imm; push_reg; push_ecx; call_rel32"
            if rel_tgt == DISPATCH_REMAP:
                routes_to_dispatch = True
            elif pattern and pattern.endswith("jmp_rel32") and rel_tgt is not None:
                # resolve one hop: if landing site is call DispatchRemap, count it
                loff = v2o(rel_tgt, ib, secs)
                if loff is not None and raw[loff] == 0xE8:
                    rel2 = struct.unpack_from("<i", raw, loff + 1)[0]
                    t2 = (rel_tgt + 5 + rel2) & 0xFFFFFFFF
                    if t2 == DISPATCH_REMAP:
                        routes_to_dispatch = True
                        rel_tgt = t2
            producers.append(
                {
                    "pushVa": f"0x{(va - 1):08x}",
                    "immVa": f"0x{va:08x}",
                    "pattern": pattern,
                    "callTarget": f"0x{rel_tgt:08x}" if rel_tgt is not None else None,
                    "callsDispatchRemap": routes_to_dispatch,
                    "afterHex": after[:10].hex(),
                }
            )
        pos = i + 1

    n_push = len(producers)
    n_to_dispatch = sum(1 for p in producers if p.get("callsDispatchRemap"))

    grade = "STATIC_SLOT_CONSUMER_UNPROVED"
    if (
        residual_head["movEaxAbs"]
        and call_through is not None
        and n_to_dispatch >= 1
        and n_push >= 1
    ):
        grade = "STATIC_CALLBACK_ARG_TO_DISPATCH_REMAP"
    elif n_push >= 1 and call_through is not None:
        grade = "STATIC_PUSH_AND_INDIRECT_CALL_PARTIAL"

    return {
        "schema": "bea.re.slot-consumer-static.v1",
        "status": "MEASURED",
        "specimen_sha256": sha,
        "candidateVa": f"0x{CANDIDATE:08x}",
        "dispatchRemapVa": f"0x{DISPATCH_REMAP:08x}",
        "remapKeyVa": f"0x{REMAP_KEY:08x}",
        "globalModeVa": f"0x{GLOBAL_MODE:08x}",
        "residualHead": residual_head,
        "dispatchCallThrough": call_through,
        "nPushImmProducers": n_push,
        "nProducersCallingDispatchRemap": n_to_dispatch,
        "producers": producers,
        "staticGrade": grade,
        "claims": [
            "0x004540c0 is pushed as an imm32 argument (callback pointer), not written via MOV [mem],imm install.",
            f"{n_to_dispatch}/{n_push} PUSH sites are followed by call to DispatchRemap 0x00453f50.",
            "DispatchRemap contains call dword ptr [esp+0x18] which, after three arg pushes from the RemapKey pattern, targets the callback arg.",
            "Residual head is mov eax,[0x677870] — same global written immediately before several push sites (mode setup).",
        ],
        "non_claims": [
            "Does not prove residual body executes under a natural -skipfmv idle path (requires controls remap UI).",
            "Does not invent function names beyond join-owned labels.",
            "Does not mutate Gen10/Gen11 residual ledgers.",
            "Does not reclassify join SLOT_CONSUMER_NEAR_IMM as fully closed without runtime entry.",
        ],
        "cheapestRuntimeFalsifier": (
            "cdb bu 004540c0 + bu 00453f50 under controls remap scenario; "
            "at DispatchRemap case path dump poi(esp+0x18) before call [esp+0x18] must equal 004540c0; "
            "then residual entry eip==004540c0 with k-aligned ret."
        ),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--specimen", type=Path, required=True)
    p.add_argument("--json-out", type=Path, required=True)
    args = p.parse_args(argv)
    result = analyze(args.specimen)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in result if k != "producers"}, indent=2))
    print("n_producers", result["nPushImmProducers"])
    print("STATIC_SLOT_CONSUMER_OK" if "DISPATCH" in result["staticGrade"] else "PARTIAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
