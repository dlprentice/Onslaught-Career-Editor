#!/usr/bin/env python3
"""Dump a PE image's export table (and machine type) as TSV.

Used by build.ps1 both to verify the proxy's export list against the live
system d3d9.dll and to prove the built DLL is PE32 i386.

Usage: pe_exports.py <path-to-pe>
Output: first line "#machine=<hex> magic=<hex> dll=<name>", then one row per
export: "<ordinal>\t<name-or-empty>\t<rva-hex>\t<forwarder-or-empty>".
"""

import struct
import sys


def sections(d, opt, optsz, nsec):
    out = []
    base = opt + optsz
    for i in range(nsec):
        b = base + i * 40
        name = d[b:b + 8].rstrip(b"\0").decode("latin-1")
        vsz, va, rsz, ptr = struct.unpack_from("<IIII", d, b + 8)
        out.append((va, max(vsz, rsz), ptr, name))
    return out


def dump(path):
    d = open(path, "rb").read()
    e_lfanew = struct.unpack_from("<I", d, 0x3C)[0]
    if d[e_lfanew:e_lfanew + 4] != b"PE\0\0":
        raise SystemExit("not a PE image: %s" % path)
    coff = e_lfanew + 4
    machine, nsec = struct.unpack_from("<HH", d, coff)
    optsz = struct.unpack_from("<H", d, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from("<H", d, opt)[0]
    ddoff = opt + (96 if magic == 0x10B else 112)
    exp_rva, exp_size = struct.unpack_from("<II", d, ddoff)
    secs = sections(d, opt, optsz, nsec)

    def r2o(rva):
        for va, sz, ptr, _ in secs:
            if va <= rva < va + sz:
                return ptr + (rva - va)
        raise SystemExit("rva 0x%X outside every section in %s" % (rva, path))

    if not exp_rva:
        print("#machine=%04x magic=%03x dll=" % (machine, magic))
        return

    eo = r2o(exp_rva)
    (_chars, _ts, _mj, _mn, name_rva, ord_base, n_func, n_name,
     func_rva, name_tbl, ord_tbl) = struct.unpack_from("<IIHHIIIIIII", d, eo)
    dll = d[r2o(name_rva):].split(b"\0")[0].decode("latin-1")
    print("#machine=%04x magic=%03x dll=%s" % (machine, magic, dll))

    names = {}
    for i in range(n_name):
        nr = struct.unpack_from("<I", d, r2o(name_tbl) + 4 * i)[0]
        o = struct.unpack_from("<H", d, r2o(ord_tbl) + 2 * i)[0]
        names[o] = d[r2o(nr):].split(b"\0")[0].decode("latin-1")

    for i in range(n_func):
        f = struct.unpack_from("<I", d, r2o(func_rva) + 4 * i)[0]
        if not f:
            continue
        fwd = ""
        if exp_rva <= f < exp_rva + exp_size:
            fwd = d[r2o(f):].split(b"\0")[0].decode("latin-1")
        print("%d\t%s\t0x%X\t%s" % (ord_base + i, names.get(i, ""), f, fwd))


if __name__ == "__main__":
    dump(sys.argv[1])
