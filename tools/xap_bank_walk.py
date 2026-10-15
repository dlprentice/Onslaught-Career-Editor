#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Walk the PC sample banks (data/sounds/sounds_<language>_pc.xap) with the layout in
reverse-engineering/asset-formats/xap-sample-bank.md, decode every sample, and prove the layout accounts for every byte.

Each bank must end exactly where its last sample ends. Every sample's 4-bit IMA ADPCM data is decoded to 16-bit
mono PCM; the report counts samples, names and decoded seconds per bank (at the game's 44,100 Hz), and pins the banks
with a manifest digest (SHA-256 over sorted "name sha256" lines). With --pcm-digests it also prints one SHA-256 per
decoded sample and one over each bank's decoded PCM in order, for comparison with another decoder. The install is only read.

Run:  python ./tools/xap_bank_walk.py --game GAME_FOLDER    (or set BEA_GAME to the game folder)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import struct
import sys
from pathlib import Path

SAMPLE_RATE = 44_100
NAME_BYTES = 64

# The IMA ADPCM tables (public reference values).
INDEX_TABLE = (-1, -1, -1, -1, 2, 4, 6, 8, -1, -1, -1, -1, 2, 4, 6, 8)
STEP_TABLE = (
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97, 107,
    118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963,
    1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358, 5894,
    6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794,
    32767,
)


class BankError(ValueError):
    pass


def decode_ima(data: bytes, samples: int) -> bytes:
    """IMA ADPCM, four bits per sample, the high nibble of each byte first, from a zero prediction and step index."""
    out = bytearray(2 * samples)
    predicted, index = 0, 0
    for n in range(samples):
        byte = data[n >> 1]
        code = (byte >> 4) & 0xF if n % 2 == 0 else byte & 0xF
        step = STEP_TABLE[index]
        difference = step >> 3
        if code & 4:
            difference += step
        if code & 2:
            difference += step >> 1
        if code & 1:
            difference += step >> 2
        predicted = predicted - difference if code & 8 else predicted + difference
        predicted = max(-32768, min(32767, predicted))
        index = max(0, min(88, index + INDEX_TABLE[code]))
        struct.pack_into("<h", out, 2 * n, predicted)
    return bytes(out)


def read_bank(data: bytes) -> tuple[str, list[tuple[str, int, bytes]]]:
    """The bank's four-byte magic and its samples as (name, PCM byte size, ADPCM bytes)."""
    if len(data) < 8:
        raise BankError("the bank is shorter than its header")
    magic = data[:4].decode("latin-1")
    (count,) = struct.unpack_from("<i", data, 4)
    if count < 0:
        raise BankError("negative sample count")
    position, samples = 8, []
    for number in range(count):
        if position + 4 + NAME_BYTES + 4 > len(data):
            raise BankError(f"sample {number} runs past the end of the bank")
        position += 4  # the per-sample tag "PSMP", which the loader reads and does not check
        name = data[position:position + NAME_BYTES].split(b"\0", 1)[0].decode("latin-1")
        position += NAME_BYTES
        (size,) = struct.unpack_from("<I", data, position)
        position += 4
        packed = (size + 3) // 4
        if position + packed > len(data):
            raise BankError(f"sample {name!r} runs past the end of the bank")
        samples.append((name, size, data[position:position + packed]))
        position += packed
    if position != len(data):
        raise BankError(f"the bank's samples end at byte {position} of {len(data)}")
    return magic, samples


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", type=Path, default=os.environ.get("BEA_GAME"), help="the game folder, only read (default $BEA_GAME)")
    parser.add_argument("--pcm-digests", action="store_true", help="print a SHA-256 of every decoded sample")
    args = parser.parse_args(argv)
    if args.game is None:
        parser.error("name the game folder with --game or BEA_GAME")
    banks = sorted((Path(args.game) / "data/sounds").glob("*.xap"))
    if not banks:
        print(f"no sample banks under {args.game}", file=sys.stderr)
        return 2
    digest, failures = hashlib.sha256(), []
    for path in banks:
        raw = path.read_bytes()
        digest.update(f"{path.name} {hashlib.sha256(raw).hexdigest()}\n".encode())
        try:
            magic, samples = read_bank(raw)
        except BankError as error:
            failures.append(f"{path.name}: {error}")
            continue
        odd = sum(1 for _, size, _ in samples if size % 2)
        seconds = sum(size // 2 for _, size, _ in samples) / SAMPLE_RATE
        names = {name.lower() for name, _, _ in samples}
        print(f"XAP_BANK {path.name}: magic {magic!r}, {len(samples)} samples, {len(names)} distinct names, "
              f"{seconds:.1f} s of audio, {odd} odd PCM sizes")
        if args.pcm_digests:
            whole = hashlib.sha256()
            for name, size, packed in samples:
                pcm = decode_ima(packed, size // 2)
                whole.update(pcm)
                print(f"  PCM {path.name} {name} {hashlib.sha256(pcm).hexdigest()}")
            print(f"PCM_BANK {path.name} {whole.hexdigest()}")
    print(f"XAP_WALK: {len(banks) - len(failures)} of {len(banks)} banks parse to their exact end; manifest {digest.hexdigest()}")
    for failure in failures:
        print("FAIL " + failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
