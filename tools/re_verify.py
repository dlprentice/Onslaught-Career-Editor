"""Mechanically verify every Ghidra-exported function against the pristine binary.

Rationale
---------
The 533-file findings tree costs a great deal of agent time and its factual layer
was measured at 99.93% correct - which means agents were, overwhelmingly, spending
their effort re-confirming things a script can confirm for free and in full.

This tool does the provable part exhaustively and cheaply, so agent time can be
spent only where judgement is actually required: names, semantics, and conflicts.

What is PROVABLE here (and is checked for 100% of functions):
  * every exported instruction's bytes match the binary at its address
  * the recorded function entry is the lowest address in its body
  * bodies are contiguous, and do not overlap other function bodies
  * every address lies inside .text
  * inventory and per-wave metadata agree on the name of each function

What is NOT provable here, and is deliberately not asserted:
  * whether a NAME is correct. That is graded separately by re_name_oracle.py.
    A function can pass every check in this file and still be called something
    entirely invented.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"


def load_sections(data: bytes):
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\0\0":
        raise SystemExit("not a PE image")
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    optsz = struct.unpack_from("<H", data, pe + 20)[0]
    imgbase = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    off = pe + 24 + optsz
    secs = []
    for i in range(nsec):
        b = data[off + i * 40: off + (i + 1) * 40]
        name = b[0:8].rstrip(b"\0").decode()
        vsz, rva, rsz, rptr = struct.unpack_from("<IIII", b, 8)
        secs.append((name, imgbase + rva, vsz, rptr, rsz))
    return imgbase, secs


def make_reader(data: bytes, secs):
    def read(va: int, n: int):
        for _name, base, vsz, rptr, rsz in secs:
            if base <= va < base + max(vsz, rsz):
                off = rptr + (va - base)
                if off + n <= len(data):
                    return data[off:off + n]
        return None
    return read


def section_of(secs, va: int):
    for name, base, vsz, rptr, rsz in secs:
        if base <= va < base + max(vsz, rsz):
            return name
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--binary", type=Path, required=True)
    ap.add_argument("--exports", type=Path, required=True, help="dir containing W*/instructions.tsv")
    ap.add_argument("--inventory", type=Path, required=True, help="functions-all.tsv")
    ap.add_argument("--out-tsv", type=Path)
    ap.add_argument("--out-json", type=Path)
    ap.add_argument("--max-report", type=int, default=25)
    args = ap.parse_args(argv)

    import hashlib
    data = args.binary.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != PRISTINE_SHA256:
        print(
            f"REFUSED: binary sha256 {digest} is not the pristine specimen.\n"
            "The Ghidra database was built from pristine BEA.exe; verifying exports\n"
            "against any other build compares two different programs.",
            file=sys.stderr,
        )
        return 2

    _imgbase, secs = load_sections(data)
    read = make_reader(data, secs)

    # --- inventory ----------------------------------------------------------
    inventory: dict[int, str] = {}
    with args.inventory.open(encoding="utf-8") as fh:
        next(fh, None)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2 and parts[0].startswith("0x"):
                inventory[int(parts[0], 16)] = parts[1]

    # --- exported instructions ---------------------------------------------
    bodies: dict[int, list[tuple[int, bytes]]] = defaultdict(list)
    meta_names: dict[int, set[str]] = defaultdict(set)
    rows = 0
    for tsv in sorted(args.exports.glob("W*/instructions.tsv")):
        with tsv.open(encoding="utf-8") as fh:
            header = next(fh, "").rstrip("\n").split("\t")
            try:
                i_fe = header.index("function_entry")
                i_fn = header.index("function_name")
                i_ia = header.index("instruction_addr")
                i_by = header.index("bytes")
            except ValueError:
                print(f"skipping {tsv}: unexpected header", file=sys.stderr)
                continue
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) <= max(i_fe, i_fn, i_ia, i_by):
                    continue
                entry = int(p[i_fe], 16)
                addr = int(p[i_ia], 16)
                raw = bytes.fromhex(p[i_by].replace(" ", ""))
                bodies[entry].append((addr, raw))
                meta_names[entry].add(p[i_fn])
                rows += 1

    # --- per-function verification -----------------------------------------
    results = []
    for entry in sorted(set(inventory) | set(bodies)):
        inv_name = inventory.get(entry)
        body = sorted(bodies.get(entry, []))
        problems: list[str] = []
        notes: list[str] = []

        if not body:
            problems.append("no-exported-body")
        if inv_name is None:
            problems.append("not-in-inventory")

        names = meta_names.get(entry, set())
        if inv_name and names and inv_name not in names:
            problems.append(f"name-disagreement({inv_name}!={'|'.join(sorted(names))})")

        mismatched = 0
        outside = 0
        for addr, raw in body:
            if section_of(secs, addr) != ".text":
                outside += 1
            actual = read(addr, len(raw))
            if actual is None or actual != raw:
                mismatched += 1
        if mismatched:
            problems.append(f"byte-mismatch({mismatched})")
        if outside:
            problems.append(f"outside-text({outside})")

        if body:
            if body[0][0] != entry:
                problems.append(f"entry-not-lowest({body[0][0]:#010x})")
            # A gap between consecutive instructions is only interesting if it
            # contains something other than alignment padding. MSVC pads with 0xCC
            # (and occasionally 0x90) between basic blocks and around jump tables,
            # and Ghidra's body ranges legitimately skip that. Reporting padded gaps
            # as defects buries the handful of gaps that hide real bytes.
            padded_gaps = 0
            live_gaps = 0
            for (a, raw), (b, _) in zip(body, body[1:]):
                end_a = a + len(raw)
                if end_a == b:
                    continue
                if end_a > b:
                    live_gaps += 1  # instructions overlap each other: never benign
                    continue
                filler = read(end_a, b - end_a) or b""
                if filler and all(byte in (0xCC, 0x90, 0x00) for byte in filler):
                    padded_gaps += 1
                else:
                    live_gaps += 1
            if live_gaps:
                problems.append(f"gap-with-content({live_gaps})")
            if padded_gaps:
                notes.append(f"padded-gap({padded_gaps})")

        end = (body[-1][0] + len(body[-1][1])) if body else entry
        results.append({
            "address": f"{entry:#010x}",
            "name": inv_name or (sorted(names)[0] if names else ""),
            "instructions": len(body),
            "start": f"{entry:#010x}",
            "end": f"{end:#010x}",
            "size": end - entry,
            "status": "OK" if not problems else "PROBLEM",
            "problems": problems,
            "notes": notes,
        })

    # --- overlap detection (cross-function, needs the whole set) -----------
    spans = sorted(
        ((int(r["start"], 16), int(r["end"], 16), r) for r in results if r["instructions"]),
        key=lambda t: t[0],
    )
    overlaps = 0
    for (s1, e1, r1), (s2, _e2, r2) in zip(spans, spans[1:]):
        if e1 > s2:
            overlaps += 1
            for r in (r1, r2):
                r["status"] = "PROBLEM"
                r["problems"].append(f"overlap({r1['address']}..{r2['address']})")

    ok = sum(1 for r in results if r["status"] == "OK")
    bad = len(results) - ok
    print(f"binary            : {args.binary}  sha256 OK")
    print(f"exported rows     : {rows}")
    print(f"functions checked : {len(results)}")
    print(f"  OK              : {ok}")
    print(f"  PROBLEM         : {bad}")
    print(f"  overlaps        : {overlaps}")

    if bad:
        print(f"\nfirst {min(bad, args.max_report)} problems:")
        shown = 0
        for r in results:
            if r["status"] != "PROBLEM":
                continue
            print(f"  {r['address']}  {r['name'][:52]:<52} {'; '.join(r['problems'])}")
            shown += 1
            if shown >= args.max_report:
                break

    if args.out_tsv:
        args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
        with args.out_tsv.open("w", encoding="utf-8", newline="") as fh:
            fh.write("address\tname\tinstructions\tstart\tend\tsize\tstatus\tproblems\tnotes\n")
            for r in results:
                fh.write(
                    f"{r['address']}\t{r['name']}\t{r['instructions']}\t{r['start']}\t"
                    f"{r['end']}\t{r['size']}\t{r['status']}\t{';'.join(r['problems'])}\t"
                    f"{';'.join(r['notes'])}\n"
                )
        print(f"\nledger: {args.out_tsv}")

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(
            json.dumps({"rows": rows, "functions": len(results), "ok": ok,
                        "problem": bad, "overlaps": overlaps, "results": results}, indent=1),
            encoding="utf-8",
        )

    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
