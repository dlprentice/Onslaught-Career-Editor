#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prepare, reproduce, and seal the 24-function JPEG live ceremony.

The authority itself never launches Ghidra and never mutates the live or
tracked project. ``preflight`` hashes the exact PRE state and reproduces the
retained scratch package. ``check-live`` proves a separately authorized live
save while tracked must remain PRE. ``seal`` has one write: create-new
publication of a portable receipt after a separately authorized tracked
refresh, read-only restore, projection, and body-accounting export. ``verify``
reproduces that saved receipt.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_jpeg_callback_boundary_scratch_authority as scratch  # noqa: E402
import ghidra_project_backup as project_backup  # noqa: E402
import re_ghidra_name_projection as name_projection  # noqa: E402


SCHEMA = "bea.ghidra.jpeg-callback-boundary-live-authority.v2"
POLICY = "PREPARATION_ONLY"
BASE_COMMIT = "07417cadd227ab8d91bd2d1ab90554bd64fc3cf5"
PROGRAM_NAME = "BEA.exe"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)
PRE_TOTAL_FUNCTIONS = 8504
POST_TOTAL_FUNCTIONS = 8528

TARGETS = 24
BODY_BYTES = 14817
BODY_RANGES = 38
EXTERNAL_INSTRUCTIONS = 4497
CFG_EDGES = 4745
PRE_FUNCTIONS = 8280
POST_FUNCTIONS = 8304
PRE_RANGES = 8396
POST_RANGES = 8434
PRE_OWNED = 1795470
POST_OWNED = 1810287
PRE_INSTRUCTIONS = 551014
POST_INSTRUCTIONS = 551055
PRE_REFERENCES = 234478
POST_REFERENCES = 234467
TEXT_START = 0x00401000
TEXT_END = 0x005D7F9D
TEXT_BYTES = TEXT_END - TEXT_START

PRE_PROJECT = {
    "fileCount": 19,
    "totalBytes": 186977157,
    "canonicalInventorySha256":
        "cda0938c1a266fbe1751a8b0bf175b90c63b296f21fc9631b5bade1ecf93e541",
}
DB_18613 = (
    68337664,
    "615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe",
)
DB_18614 = (
    68337664,
    "d7f0011ea337f58b710415d5664e73d91ca9f1f61e20a836278d3e71b71b2865",
)
PRE_OLD_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18613.gbf"
PRE_STABLE_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18614.gbf"
POST_ROLLING_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18615.gbf"

MANIFEST_REL = (
    "reverse-engineering/binary-analysis/"
    "jpeg-ijg-callback-function-boundaries-2026-08-14.tsv"
)
PROJECTION_REL = (
    "reverse-engineering/binary-analysis/"
    "ghidra-function-name-table-2026-08-13.tsv"
)
LIVE_LANE_REL = (
    "local-lab/ghidra-jpeg24-boundary-live-promotion-20260814-v2"
)
AUTHORITY_RECEIPT_REL = (
    "local-lab/ghidra-jpeg24-boundary-live-authority-20260814-v2/"
    "live-promotion.ready.json"
)
PREP_LANE_REL = (
    "local-lab/ghidra-jpeg24-boundary-live-prep-db18614-v2"
)
SCRATCH_LANE_REL = (
    "local-lab/ghidra-jpeg24-boundary-current-scratch-20260814-v1"
)
SCRATCH_RECEIPT_REL = f"{SCRATCH_LANE_REL}/scratch-authority.ready.json"
PRE_ACCOUNTING_REL = f"{PREP_LANE_REL}/static/pre-body-ranges.tsv"
DIAGNOSTIC_ADDRESSES_REL = f"{SCRATCH_LANE_REL}/inputs/diagnostic-addresses.txt"
PROJECTION_SOURCE = f"{LIVE_LANE_REL}/runs/live-readback/functions.tsv"

PRE_FUNCTIONS_STAMP = (
    7161943,
    "d2ff1e8e7bd91454fff9822fb7ecc8e624525fa5c6cbc9dcfe06f4e0212b750d",
)
PRE_PROGRAM_STAMP = (
    1267,
    "b389487a65d6271329703c9e3ec9186b7261aa871a154c31179322780e1c132e",
)
POST_FUNCTIONS_STAMP = (
    7177776,
    "bceedfa2eec573ee95e42a703d6f3a552c4718115fa540f3eaca492322f9a173",
)
POST_PROGRAM_STAMP = (
    1267,
    "bcb364f619559879e815f8d95f5551ba10d9be0467023bd006ee1246b0f9b40f",
)
PRE_PROJECTION_STAMP = (
    508239,
    "267210a78248f58da6bca1b4d11ee7b1812481602413e8bcac2fb4e4b4c4cb84",
)
POST_PROJECTION_STAMP = (
    509334,
    "5dd0d1145c2cf25004bd50208c624d9bf4f9c2fe0e4d307ac6c7ca88e8a5dfbc",
)
PRE_BODY_RANGES_STAMP = (
    1197803,
    "495f1a86490e7b2646d2a0a6cd86bf6e4cdb071d5932b7d65ded1377621582e2",
)
POST_BODY_RANGES_STAMP = (
    1202661,
    "8e3640bfb280b6ce93a62db885183aa2239d1e74841685316b0117518eb63aaa",
)
POST_DIRECT_CALLS_STAMP = (
    1396670,
    "e2c3e2d0ace69d13b4bffa4d12690e60f6cf0cc50d2ff846cdc37ace680a756f",
)
POST_GRAPH_RECEIPT_STAMP = (
    767,
    "bc3047480f43cbd31b762854eb9a0fc0e2b79564786a935c0c874fc589fb3d04",
)
SCRATCH_RECEIPT_STAMP = (
    7077,
    "573c550c7197e15cc098ff0dd09ce55467c7bae95ca2ec4efcf9e045e0954b63",
)
SCRATCH_TREE = {
    "fileCount": 258,
    "totalBytes": 1013137450,
    "sha256":
        "7c3df3b029b3f175a41bbbf698c1b47dfd5f18c02f7616494794225f3dc2058c",
    "canonicalization": "sha256<TAB>bytes<TAB>relative-posix-path<LF>, path order",
}
PREP_TREE = {
    "fileCount": 94,
    "totalBytes": 410373323,
    "sha256":
        "6a25263ce240c1311bc857b57937f37ad652a94859efb853c4d40e9bc8ef22f0",
    "canonicalization": "sha256<TAB>bytes<TAB>relative-posix-path<LF>, path order",
}

BOUNDARY_STAMPS = {
    "dry": (
        9972,
        "5ba3201c0b852d485434701b768257e404c9fc963a3349f5f3855528662d3ac3",
    ),
    "apply": (
        12745,
        "2864f5c2085b395fcc8270f490c706cb245f299e58a6d3d62998fcc5c4ddfb7f",
    ),
    "readback": (
        12769,
        "956426b50f1997227828958e38399ba1106bbfdb36f4503c769338a387fffdfb",
    ),
}
PRE_LISTING_STAMP = (
    946,
    "aeddd26c2ebd4845436335263c5d620dbc8c1a242d9d96bcfb78a2ef8581ca98",
)
POST_LISTING_STAMP = (
    955,
    "55944e2cc03902c8f99d273aaa51ca98f1bfdedbe129bf18ad4441d21c6e0271",
)

EXPECTED_REPO_INPUTS = {
    MANIFEST_REL: (
        15295,
        "6253c29d77e6676f2843ca8adf3d9c52b4b4fa86f088f6086ea00b90dde89fd6",
    ),
    "tools/GhidraApplyJpegCallbackBoundaries.java": (
        61032,
        "16b8fbf6e4ffdab716b5359e8610c77b83bb6a32b6e2ac7d98e34efbe500c480",
    ),
    "tools/GhidraApplyJpegCallbackBoundariesV2.java": (
        61045,
        "dcb2e8e92b6b877ae6c6e1f5839c298e48f0fd4a649a568d228b657af7c420dc",
    ),
    "tools/ExportFullFunctionInventory.java": (
        23963,
        "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197",
    ),
    "tools/ExportParityLabGraph.java": (
        17663,
        "e91e26c428f593e3fd49f755fcc8551dd685ce41825fe180966be49594cbbec9",
    ),
    "tools/ghidra_inventory_diff.py": (
        9622,
        "b4956fbf9c9125cfdd7b7810cdc15f298fef8a081a880f82d6231a6dcbb25460",
    ),
    "tools/ghidra_project_backup.py": (
        27502,
        "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58",
    ),
    "tools/GhidraProjectOpenProbe.java": (
        3452,
        "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab",
    ),
    "tools/DiagnoseAddressListingState.java": (
        3956,
        "183394907659e7810c77a9720e1899fd8a6296e6e86673495d68a2764edefe69",
    ),
    "tools/ghidra_jpeg_callback_boundary_scratch_authority.py": (
        43589,
        "18be45ed7343627fb4a8652605df72516ba6ae77788c0d271f47827e7e967b4e",
    ),
    "tools/re_ghidra_name_projection.py": (
        6139,
        "d13d5f4d3b20cbd1e1baf24cd924d454c6c07b0bbf5517834c4089357f14ecdb",
    ),
}

RUN_LAYOUT = {
    "dry": "live-pre-readback",
    "apply": "live-apply",
    "readback": "live-readback",
}

POST_BODY_ROWS = {
    "0x005abb00": (
        ("0x005abb00", "0x005abb9c", "0x005abb9d", "157",
         "42948ba6ed793d570e9606cf1ff75b94236628f2bbf6c58ef015538442c212ee"),
        ("0x005abba0", "0x005abc3c", "0x005abc3d", "157",
         "8f35f5f732688baf7b3e86e69e618c6d52d93205e00b8b0c8ac44385ce061c1f"),
        ("0x005abc40", "0x005abd94", "0x005abd95", "341",
         "ce4d757667d45ea224c4527cadc5bbf9eae22be5913645240a26e52ae7ac8332"),
    ),
    "0x005abda0": (
        ("0x005abda0", "0x005abda4", "0x005abda5", "5",
         "5fed5afb29946811bf02359627a94bc01d08d31b779528feaadde3866af9c855"),
    ),
    "0x005abdb0": (
        ("0x005abdb0", "0x005abdd8", "0x005abdd9", "41",
         "b13b57f64d69e06f608191ba4e733ba0ba0812617c1b42865c4acc4d3a69113c"),
        ("0x005abde0", "0x005abe2c", "0x005abe2d", "77",
         "83f706da86faf250f9ca65f3d4b6d1baf3533992d2a4291be08e8f3080a2f19e"),
        ("0x005abe30", "0x005abe6c", "0x005abe6d", "61",
         "e8054e234acd78bd1bf1f2600e018e7a130802026b56638c197bb32d2d1f1021"),
        ("0x005abe70", "0x005abfe1", "0x005abfe2", "370",
         "e97d2bb5baeba5b8430040219d1e2b45c98cb2c46e5619d75d7619dafab8f348"),
    ),
    "0x005abff0": (
        ("0x005abff0", "0x005ac17f", "0x005ac180", "400",
         "e3448552c4bffe1e8296580b5ca9963c9be975685638433d340f26ec6bf2208e"),
    ),
    "0x005ad820": (
        ("0x005ad820", "0x005ada56", "0x005ada57", "567",
         "fca873d1b2cd895067572925bccfab766de64803599bea5bd93b00a4c1293466"),
    ),
    "0x005ada60": (
        ("0x005ada60", "0x005adb52", "0x005adb53", "243",
         "46bc91c30447852013a1ed73f34fef190f688cd6910fb3763666c539903030a6"),
    ),
    "0x005adb60": (
        ("0x005adb60", "0x005adc2c", "0x005adc2d", "205",
         "89abe97f15ecb09cb2db3acf1f6d3132ab29f78740c1b5e6fd5eec6f083a46ee"),
        ("0x005adc30", "0x005ade49", "0x005ade4a", "538",
         "019f64194eedb5ab9dd72b04f52b5ac628d81ff58b6a5a6765c9275bad674470"),
        ("0x005ade50", "0x005adf45", "0x005adf46", "246",
         "a0147a71ac84ff2b3db381a186995aa48489bed3d30a3777b2cff2d2ec2fc1c9"),
    ),
    "0x005adf50": (
        ("0x005adf50", "0x005ae189", "0x005ae18a", "570",
         "d6026c1bab80114ab77a05b87cd1e987a2823fc801dc9413846327665c1bfdca"),
    ),
    "0x005b2b90": (
        ("0x005b2b90", "0x005b2bfc", "0x005b2bfd", "109",
         "ae4db82ec8a0ad47f6ea5bbee67bfbea9adffe5c134cee60f96e3030c90e1efe"),
        ("0x005b2c00", "0x005b2d9d", "0x005b2d9e", "414",
         "6a1d278bcecb052d26472bc930de7cb6754817d5739f171f264c7bd512d13efb"),
    ),
    "0x005b2da0": (
        ("0x005b2da0", "0x005b2f07", "0x005b2f08", "360",
         "57b9d02829580f48bd21506073bd3d753b62d0edc359c31dce09bc1966bf8a8b"),
        ("0x005b2f10", "0x005b2fb3", "0x005b2fb4", "164",
         "657f3c25dc4dd656d13fb38176e8b1e7a9ed244d1eb9f449c39fd62c85bc5b21"),
    ),
    "0x005b2fc0": (
        ("0x005b2fc0", "0x005b307b", "0x005b307c", "188",
         "157a1dd4c79ae6a91ecb4a7c2745c297b56185a44a7b1740589f310078b65873"),
    ),
    "0x005b4ed0": (
        ("0x005b4ed0", "0x005b51f8", "0x005b51f9", "809",
         "febbe28638e1a0482a303770ce2fd4609f453cc984ddf6d890b66553e7250958"),
        ("0x005b5200", "0x005b536b", "0x005b536c", "364",
         "f4a9dfd779c6dd338db758e870d32fb8f7c8057361d24432e97bf51c2f651977"),
    ),
    "0x005b5370": (
        ("0x005b5370", "0x005b5404", "0x005b5405", "149",
         "f5aef078dc12691a0143d5ac809d462b7b153a260d588d61e614f66e26105e30"),
        ("0x005b5410", "0x005b5b78", "0x005b5b79", "1897",
         "fa00d9d45ad2be682107ab30e2cd3bb6641fd989797b9bad85b4b6a4178e099d"),
    ),
    "0x005b5c30": (
        ("0x005b5c30", "0x005b5c73", "0x005b5c74", "68",
         "920cb13672a24dbd280526bfb16d6e842316d41cf90af8e503d7418d7a55f419"),
    ),
    "0x005b5c80": (
        ("0x005b5c80", "0x005b5e0c", "0x005b5e0d", "397",
         "85d79f452f2f0a49792bce440f6825668ceb5aad0e7a3a595b197e786c858243"),
        ("0x005b5e10", "0x005b5e87", "0x005b5e88", "120",
         "1616ebbea056840e6dcc755ced77566bf8baacaff36578b4946c59833da30a02"),
    ),
    "0x005b5e90": (
        ("0x005b5e90", "0x005b6094", "0x005b6095", "517",
         "af9bc8398946e40482455e2012013d31dccd2c5f1aaf635389f4cccf34f3881b"),
    ),
    "0x005b6800": (
        ("0x005b6800", "0x005b6a85", "0x005b6a86", "646",
         "dafa1afd702c5a85511d2d1185658f58d56e1b0755d98228edeb48a0ee5d21b8"),
    ),
    "0x005b6a90": (
        ("0x005b6a90", "0x005b6c20", "0x005b6c21", "401",
         "963b4f71beb1a0a08771f3a52c6c576d0a67a6a49c40b2bdfe6e8699970d6247"),
    ),
    "0x005bc580": (
        ("0x005bc580", "0x005bcc32", "0x005bcc33", "1715",
         "c0e7af8d7fb1f7568e9f648c527b21307ce475f9b9b7c3c129e977bdbb6a3f1c"),
    ),
    "0x005bcc40": (
        ("0x005bcc40", "0x005bce0f", "0x005bce10", "464",
         "bf1e5b2bac3e7447e89ff10da2cb9b59a6c344564d9ea3fbdf492c487b0a3240"),
    ),
    "0x005bce10": (
        ("0x005bce10", "0x005bce54", "0x005bce55", "69",
         "0c24fd7fa574b75c70bf51e891324d828e06dcad2cab844a237277a28ae5df6e"),
    ),
    "0x005bdb70": (
        ("0x005bdb70", "0x005bdd95", "0x005bdd96", "550",
         "86244aee2612683328e3ee47f3c51734bf6152c78bfd8b040bd3aa0982788065"),
    ),
    "0x005bdda0": (
        ("0x005bdda0", "0x005bdff5", "0x005bdff6", "598",
         "898f95f4ff4d332945e24ce50f302a1c7f2d1b6da2015b60bf193737499a496d"),
    ),
    "0x005be000": (
        ("0x005be000", "0x005be017", "0x005be018", "24",
         "e0e290b5a57ad601c560b1a6549e89ecbe2053932352065897030dcd34e3543a"),
        ("0x005be020", "0x005be1b8", "0x005be1b9", "409",
         "9e84937eda666e204b33dc8c9a7bda5c6a9526aabbbd55821f4fb989f18458db"),
        ("0x005be1c0", "0x005be356", "0x005be357", "407",
         "e1c957077cc9e3030a82bcdccb236e278238d0a55ea8c801caba631c614d0c39"),
    ),
}

CLAIMS = (
    "The retained 258-file JPEG scratch tree and exact sealed receipt reproduce two saved positive replicas, separate readbacks, adverse controls, exact PRE recovery, and two path-containment refusals.",
    "Two fresh disposable db.18614 replicas preserve every current PRE function row and reproduce byte-identical semantic POST inventories, listings, projections, and body-accounting exports.",
    "Live and tracked were exact byte-identical db.18614 PRE projects before any ceremony artifact existed.",
    "The completed ceremony contains exactly one writable live apply between read-only PRE and separate read-only POST runs.",
    "All 8,280 PRE function rows remain byte-identical; the exact 24-entry manifest adds 38 pairwise-disjoint default-metadata body ranges and 14,817 owned bytes.",
    "The byte at 0x005B6900 is neither data nor a function entry and is owned only as the final byte of MOVZX 0F B6 00 beginning at 0x005B68FE inside FUN_005b6800.",
    "The only physical project transition is db.18613 removal and db.18615 addition while db.18614 and every other common file remain exact.",
    "PRE and POST off-volume backups reopen read-only; tracked remains PRE through POST recovery, then tracked POST and its retained restore equal live POST byte-for-byte.",
    "The tracked 8,304-row projection and exact 1,810,287-byte body accounting are refreshed mechanically from the proved POST state.",
    "No name, signature, comment, tag, data, byte, behavior, runtime, or reconstruction claim is authorized by this structural promotion.",
)


class AuthorityError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuthorityError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path, role: str) -> dict[str, Any]:
    require(path.is_file(), f"missing {role}: {path}")
    return {"role": role, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def verify_stamp(path: Path, expected: tuple[int, str], role: str) -> dict[str, Any]:
    measured = stamp(path, role)
    require(
        (measured["bytes"], measured["sha256"]) == expected,
        f"{role} stamp differs",
    )
    return measured


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file(), f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise AuthorityError(f"invalid {label}: {path}") from exc
    require(isinstance(value, dict), f"{label} is not an object")
    return value


def parse_utc(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"{label} UTC timestamp") from exc
    return parsed


def mtime_utc(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_path(path: Path) -> Path:
    return Path(os.path.abspath(path)).resolve(strict=False)


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def require_disjoint(first: Path, second: Path, label: str) -> None:
    require(not is_within(first, second) and not is_within(second, first), label)


def exact_directory_entries(
    root: Path,
    *,
    expected_files: Iterable[str],
    expected_directories: Iterable[str],
    label: str,
) -> None:
    require(root.is_dir(), f"missing {label}: {root}")
    require(not project_backup.is_reparse(root), f"unsafe {label}: {root}")
    files: set[str] = set()
    directories: set[str] = set()
    for entry in root.iterdir():
        require(not project_backup.is_reparse(entry), f"unsafe {label} entry: {entry}")
        if entry.is_file():
            files.add(entry.name)
        elif entry.is_dir():
            directories.add(entry.name)
        else:
            raise AuthorityError(f"unsupported {label} entry: {entry}")
    require(files == set(expected_files), f"{label} file set differs: {sorted(files)}")
    require(
        directories == set(expected_directories),
        f"{label} directory set differs: {sorted(directories)}",
    )


def ensure_portable(value: Any, label: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            ensure_portable(child, f"{label}.{key}")
    elif isinstance(value, list) or isinstance(value, tuple):
        for index, child in enumerate(value):
            ensure_portable(child, f"{label}[{index}]")
    elif isinstance(value, str):
        require(not re.match(r"^[A-Za-z]:[\\/]", value), f"absolute path leaked at {label}")
        require(not value.startswith("\\\\"), f"UNC path leaked at {label}")
        require(not value.startswith("/"), f"absolute POSIX path leaked at {label}")


def tree_identity(root: Path) -> dict[str, Any]:
    require(root.is_dir(), f"missing scratch tree: {root}")
    rows: list[tuple[str, int, str]] = []
    count = 0
    total = 0
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        require(not project_backup.is_reparse(path), f"scratch tree reparse entry: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative == "scratch-authority.ready.json":
            continue
        file_digest = sha256_file(path)
        rows.append((file_digest, path.stat().st_size, relative))
        count += 1
        total += path.stat().st_size
    canonical = b"".join(
        f"{digest}\t{size}\t{relative}\n".encode("utf-8")
        for digest, size, relative in rows
    )
    return {
        "fileCount": count,
        "totalBytes": total,
        "sha256": hashlib.sha256(canonical).hexdigest(),
        "canonicalization": SCRATCH_TREE["canonicalization"],
    }


def project_value(root: Path) -> dict[str, Any]:
    try:
        manifest = project_backup.build_manifest(root, "BEA")
    except project_backup.BackupError as exc:
        raise AuthorityError(str(exc)) from exc
    files = [row.to_json() for row in manifest.files]
    return {
        "projectName": "BEA",
        "fileCount": len(files),
        "totalBytes": sum(int(row["size"]) for row in files),
        "structurallyComplete": manifest.structurally_complete,
        "files": files,
    }


def project_without_root(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value.get(key)
        for key in ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")
    }


def project_digest(value: Mapping[str, Any]) -> str:
    rows = list(value.get("files", []))
    paths = [str(row["relative_path"]) for row in rows]
    require(paths == sorted(paths), "project rows are not relative-path ordered")
    raw = "".join(
        f"{row['sha256']}\t{row['size']}\t{row['relative_path']}\n"
        for row in rows
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def project_summary(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fileCount": value.get("fileCount"),
        "totalBytes": value.get("totalBytes"),
        "canonicalInventorySha256": project_digest(value),
        "canonicalization":
            "sha256<TAB>bytes<TAB>relative-posix-path<LF>, relative-path order",
    }


def project_file_map(value: Mapping[str, Any]) -> dict[str, tuple[int, str]]:
    return {
        str(row["relative_path"]): (int(row["size"]), str(row["sha256"]))
        for row in value.get("files", [])
    }


def require_same_project(
    left: Mapping[str, Any], right: Mapping[str, Any], label: str
) -> None:
    require(project_without_root(left) == project_without_root(right), f"{label} differs")


def require_pre_project(value: Mapping[str, Any], label: str) -> None:
    require(value.get("projectName") == "BEA", f"{label} project name")
    require(value.get("structurallyComplete") is True, f"{label} completeness")
    summary = project_summary(value)
    for key, expected in PRE_PROJECT.items():
        require(summary.get(key) == expected, f"{label} {key} differs")
    files = project_file_map(value)
    require(files.get(PRE_OLD_DB_PATH) == DB_18613, f"{label} db.18613 identity")
    require(files.get(PRE_STABLE_DB_PATH) == DB_18614, f"{label} db.18614 identity")
    require(POST_ROLLING_DB_PATH not in files, f"{label} unexpectedly contains db.18615")


def validate_post_transition(
    pre: Mapping[str, Any], post: Mapping[str, Any], label: str
) -> dict[str, Any]:
    require(post.get("projectName") == "BEA", f"{label} project name")
    require(post.get("structurallyComplete") is True, f"{label} completeness")
    require(post.get("fileCount") == PRE_PROJECT["fileCount"], f"{label} file count")
    before = project_file_map(pre)
    after = project_file_map(post)
    removed = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    changed = sorted(
        path for path in set(before) & set(after) if before[path] != after[path]
    )
    require(removed == [PRE_OLD_DB_PATH], f"{label} removed paths")
    require(added == [POST_ROLLING_DB_PATH], f"{label} added paths")
    require(changed == [], f"{label} changed common files")
    require(after.get(PRE_STABLE_DB_PATH) == DB_18614, f"{label} stable db.18614")
    rolling = after.get(POST_ROLLING_DB_PATH)
    require(rolling is not None and rolling[0] > 0, f"{label} rolling db.18615")
    return {
        "removed": removed,
        "added": added,
        "changedCommonFiles": changed,
        "byteDelta": int(post["totalBytes"]) - int(pre["totalBytes"]),
        "stableDatabase": {
            "path": PRE_STABLE_DB_PATH,
            "bytes": DB_18614[0],
            "sha256": DB_18614[1],
        },
        "rollingDatabase": {
            "path": POST_ROLLING_DB_PATH,
            "bytes": rolling[0],
            "sha256": rolling[1],
        },
    }


@dataclass(frozen=True)
class Config:
    repo: Path
    scratch_repo: Path
    live_project: Path
    live_lane: Path
    pre_backup: Path
    post_backup: Path
    output: Path | None

    @property
    def tracked_project(self) -> Path:
        return self.repo / "reverse-engineering/ghidra"

    @property
    def projection(self) -> Path:
        return self.repo / PROJECTION_REL

    @property
    def scratch_lane(self) -> Path:
        return self.scratch_repo / SCRATCH_LANE_REL

    @property
    def scratch_receipt(self) -> Path:
        return self.scratch_repo / SCRATCH_RECEIPT_REL

    @property
    def prep_lane(self) -> Path:
        return self.repo / PREP_LANE_REL

    @property
    def pre_accounting(self) -> Path:
        return self.repo / PRE_ACCOUNTING_REL


def validate_layout(config: Config) -> None:
    require(config.repo.is_dir(), "repository root is missing")
    require(config.scratch_repo.is_dir(), "scratch repository root is missing")
    require(config.live_project.is_dir(), "live project root is missing")
    require(config.tracked_project.is_dir(), "tracked project root is missing")
    require(
        clean_path(config.live_lane) == clean_path(config.repo / LIVE_LANE_REL),
        "live lane is not the canonical current-repository path",
    )
    roots = [
        config.live_project,
        config.tracked_project,
        config.scratch_lane,
        config.prep_lane,
        config.live_lane,
        config.pre_backup,
        config.post_backup,
    ]
    for index, left in enumerate(roots):
        for right in roots[index + 1:]:
            require_disjoint(clean_path(left), clean_path(right), "project/evidence roots overlap")


def validate_repo_inputs(config: Config) -> dict[str, Any]:
    ledger: dict[str, Any] = {}
    for relative, expected in EXPECTED_REPO_INPUTS.items():
        ledger[relative] = verify_stamp(config.repo / relative, expected, relative)
    imported = {
        "authority-import/ghidra_project_backup.py": Path(project_backup.__file__).resolve(),
        "authority-import/ghidra_jpeg_callback_boundary_scratch_authority.py":
            Path(scratch.__file__).resolve(),
        "authority-import/re_ghidra_name_projection.py": Path(name_projection.__file__).resolve(),
    }
    expected = {
        "authority-import/ghidra_project_backup.py":
            EXPECTED_REPO_INPUTS["tools/ghidra_project_backup.py"],
        "authority-import/ghidra_jpeg_callback_boundary_scratch_authority.py":
            EXPECTED_REPO_INPUTS[
                "tools/ghidra_jpeg_callback_boundary_scratch_authority.py"
            ],
        "authority-import/re_ghidra_name_projection.py":
            EXPECTED_REPO_INPUTS["tools/re_ghidra_name_projection.py"],
    }
    for role, path in imported.items():
        ledger[role] = verify_stamp(path, expected[role], role)
    return ledger


def load_targets(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    require(len(rows) == TARGETS and all(None not in row for row in rows), "target manifest")
    entries = [str(row["retail_va"]).lower() for row in rows]
    require(entries == sorted(entries) and len(set(entries)) == TARGETS, "target order")
    require(set(entries) == set(POST_BODY_ROWS), "target set")
    require(sum(int(row["body_bytes"]) for row in rows) == BODY_BYTES, "body bytes")
    require(sum(int(row["body_range_count"]) for row in rows) == BODY_RANGES,
            "body range count")
    require(sum(int(row["instruction_count"]) for row in rows) == EXTERNAL_INSTRUCTIONS,
            "external instruction count")
    require(sum(int(row["cfg_edge_count"]) for row in rows) == CFG_EDGES,
            "CFG edge count")
    require(all(row["identity_grade"] == "EXACT_IJG_V6B_SOURCE_ALGORITHM"
                for row in rows), "provider identity grade")
    require(all(row["current_8280_body_overlap_bytes"] == "0"
                and row["pairwise_overlap_bytes"] == "0" for row in rows),
            "target overlap contract")
    for row in rows:
        address = row["retail_va"].lower()
        expected_ranges = POST_BODY_ROWS[address]
        require(
            ";".join(f"{start}-{end}" for start, _maximum, end, _size, _digest
                     in expected_ranges) == row["body_ranges"].lower()
            and len(expected_ranges) == int(row["body_range_count"])
            and sum(int(item[3]) for item in expected_ranges) == int(row["body_bytes"]),
            f"target body-accounting envelope at {address}",
        )
    correction = next(row for row in rows if row["retail_va"].lower() == "0x005b6800")
    require(
        correction["body_ranges"].lower() == "0x005b6800-0x005b6a86"
        and correction["body_bytes"] == "646"
        and correction["body_sha256"]
        == "dafa1afd702c5a85511d2d1185658f58d56e1b0755d98228edeb48a0ee5d21b8"
        and correction["provider_identity"]
        == "LIBJPEG6B__h2v2_smooth_downsample",
        "0x005B6800 correction contract",
    )
    return [{str(key): str(value) for key, value in row.items()} for row in rows]


def validate_scratch(config: Config) -> dict[str, Any]:
    measured_tree = tree_identity(config.scratch_lane)
    require(measured_tree == SCRATCH_TREE, "retained full scratch tree identity differs")
    receipt = verify_stamp(
        config.scratch_receipt, SCRATCH_RECEIPT_STAMP, "scratch/authority receipt"
    )
    tool = config.scratch_repo / "tools/ghidra_jpeg_callback_boundary_scratch_authority.py"
    verify_stamp(
        tool,
        EXPECTED_REPO_INPUTS["tools/ghidra_jpeg_callback_boundary_scratch_authority.py"],
        "scratch/authority tool",
    )
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(tool), "verify"],
        cwd=config.scratch_repo,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=900,
    )
    require(result.returncode == 0, f"scratch authority verify failed: {result.stderr.strip()}")
    require(
        result.stdout.count(
            "JPEG_CALLBACK_SCRATCH_AUTHORITY_VERIFIED targets=24 functions=8304"
        ) == 1,
        "scratch authority sentinel",
    )
    recorded = load_json(config.scratch_receipt, "scratch authority receipt")
    require(recorded.get("schemaVersion") == scratch.SCHEMA, "scratch schema")
    require(recorded.get("verdict") == "SCRATCH_READY_LIVE_FORBIDDEN", "scratch verdict")
    require(recorded.get("artifactTree") == {
        "fileCount": SCRATCH_TREE["fileCount"],
        "totalBytes": SCRATCH_TREE["totalBytes"],
        "sha256": SCRATCH_TREE["sha256"],
    }, "scratch recorded tree")
    require(recorded.get("summary") == {
        "adverseControls": 2,
        "bodyBytes": BODY_BYTES,
        "bodyRanges": BODY_RANGES,
        "cfgEdges": CFG_EDGES,
        "current8280OverlapBytes": 0,
        "demoNormalizedTwins": TARGETS,
        "demoRawTwins": 14,
        "externalInstructions": EXTERNAL_INSTRUCTIONS,
        "externalPathPreflights": 2,
        "ghidraBodyInstructions": EXTERNAL_INSTRUCTIONS,
        "instructionDelta": POST_INSTRUCTIONS - PRE_INSTRUCTIONS,
        "pairwiseOverlapBytes": 0,
        "postFunctions": POST_FUNCTIONS,
        "preFunctions": PRE_FUNCTIONS,
        "preservedPreFunctionRows": PRE_FUNCTIONS,
        "readonlyRestoreProofs": 1,
        "referenceDelta": POST_REFERENCES - PRE_REFERENCES,
        "replicas": 2,
        "targets": TARGETS,
    }, "scratch summary")
    require(recorded.get("correction") == {
        "bodyBytes": 646,
        "bodySha256":
            "dafa1afd702c5a85511d2d1185658f58d56e1b0755d98228edeb48a0ee5d21b8",
        "containingInstruction": "0x005B68FE-0x005B6901",
        "containingInstructionBytes": "0fb600",
        "fixedPointAddress": "0x005B6900",
        "fixedPointIsData": False,
        "fixedPointIsFunctionEntry": False,
        "functionEndExclusive": "0x005B6A86",
        "functionEntry": "0x005B6800",
    }, "scratch correction")
    require(recorded.get("liveMutationAuthorized") is False
            and recorded.get("trackedGhidraMutationAuthorized") is False,
            "scratch mutation boundary")
    diagnostic = verify_stamp(
        config.scratch_repo / DIAGNOSTIC_ADDRESSES_REL,
        (88, "e0c3f01b6fcea1c9fe0de328c7850a7c29e9f7aae59cd4ef9549bf013c917aa9"),
        "scratch/diagnostic addresses",
    )
    return {
        "receipt": receipt,
        "fullTree": measured_tree,
        "semanticVerifyRebuilt": True,
        "targets": TARGETS,
        "bodyRanges": BODY_RANGES,
        "bodyBytes": BODY_BYTES,
        "preservedPreFunctionRows": PRE_FUNCTIONS,
        "positiveReplicas": 2,
        "savedReadbacks": 2,
        "adverseControls": 2,
        "containmentRefusals": 2,
        "backupReadOnlyOpen": True,
        "diagnosticAddresses": diagnostic,
    }


def validate_preparation_receipt(
    config: Config, replica: str, mode: str
) -> dict[str, Any]:
    relative = f"formal-{replica}/{mode}"
    root = config.prep_lane / relative
    receipt = load_json(root / "boundaries.ready.json", f"preparation {relative}")
    require(set(receipt) == {
        "schemaVersion", "completedAtUtc", "mode", "tool", "manifest", "output",
        "program", "counts", "explicitBodySetsAuthorized",
        "fixedPointAddressIsFunctionEntry", "fixedPointAddressIsData",
        "fixedPointInstructionOwner", "postCountsPinned", "namesAuthorized",
        "metadataAuthorized", "separateReadbackRequired",
    }, f"preparation {relative} receipt field set")
    require(receipt.get("schemaVersion") == "bea.ghidra.jpeg-callback-boundaries.v2",
            f"preparation {relative} schema")
    require(receipt.get("mode") == mode, f"preparation {relative} mode")
    parse_utc(receipt.get("completedAtUtc"), f"preparation {relative} completion")
    require(receipt.get("tool") == {
        "path": "tools/GhidraApplyJpegCallbackBoundariesV2.java",
        "bytes": EXPECTED_REPO_INPUTS["tools/GhidraApplyJpegCallbackBoundariesV2.java"][0],
        "sha256": EXPECTED_REPO_INPUTS["tools/GhidraApplyJpegCallbackBoundariesV2.java"][1],
    }, f"preparation {relative} tool")
    require(receipt.get("manifest") == {
        "path": MANIFEST_REL,
        "bytes": EXPECTED_REPO_INPUTS[MANIFEST_REL][0],
        "sha256": EXPECTED_REPO_INPUTS[MANIFEST_REL][1],
    }, f"preparation {relative} manifest")
    boundary = verify_stamp(
        root / "boundaries.tsv", BOUNDARY_STAMPS[mode],
        f"preparation {relative} boundaries",
    )
    require(receipt.get("output") == {
        "path": f"{PREP_LANE_REL}/{relative}/boundaries.tsv",
        "bytes": boundary["bytes"], "sha256": boundary["sha256"],
    }, f"preparation {relative} output")
    require(receipt.get("program") == {
        "name": PROGRAM_NAME, "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256,
    }, f"preparation {relative} program")
    before_functions = POST_FUNCTIONS if mode == "readback" else PRE_FUNCTIONS
    before_instructions = POST_INSTRUCTIONS if mode == "readback" else PRE_INSTRUCTIONS
    after_functions = POST_FUNCTIONS if mode != "dry" else PRE_FUNCTIONS
    after_instructions = POST_INSTRUCTIONS if mode != "dry" else PRE_INSTRUCTIONS
    require(receipt.get("counts") == {
        "targets": TARGETS,
        "externalInstructions": EXTERNAL_INSTRUCTIONS,
        "ghidraBodyInstructions": EXTERNAL_INSTRUCTIONS,
        "functionsBefore": before_functions,
        "functionsAfter": after_functions,
        "instructionsBefore": before_instructions,
        "instructionsAfter": after_instructions,
    }, f"preparation {relative} counts")
    require(receipt.get("explicitBodySetsAuthorized") is True
            and receipt.get("fixedPointAddressIsFunctionEntry") is False
            and receipt.get("fixedPointAddressIsData") is False
            and receipt.get("fixedPointInstructionOwner") == "0x005b68fe"
            and receipt.get("postCountsPinned") is True
            and receipt.get("namesAuthorized") is False
            and receipt.get("metadataAuthorized") is False
            and receipt.get("separateReadbackRequired") is (mode != "readback"),
            f"preparation {relative} policy")
    scratch.verify_boundaries(
        root / "boundaries.tsv", mode, load_targets(config.repo / MANIFEST_REL)
    )
    return stamp(
        root / "boundaries.ready.json",
        f"{PREP_LANE_REL}/{relative}/boundaries.ready.json",
    )


def validate_preparation_replicas(config: Config) -> dict[str, Any]:
    require(config.prep_lane.is_dir(), "current-state preparation lane is missing")
    measured_tree = tree_identity(config.prep_lane)
    require(measured_tree == PREP_TREE, "current-state preparation tree differs")
    verify_stamp(
        config.prep_lane / "static/manifest.tsv",
        EXPECTED_REPO_INPUTS[MANIFEST_REL], "preparation manifest copy",
    )
    tracked_v2 = config.repo / "tools/GhidraApplyJpegCallbackBoundariesV2.java"
    frozen_v2 = config.prep_lane / "static/GhidraApplyJpegCallbackBoundariesV2.java"
    verify_stamp(
        frozen_v2,
        EXPECTED_REPO_INPUTS["tools/GhidraApplyJpegCallbackBoundariesV2.java"],
        "preparation mutator copy",
    )
    require(frozen_v2.read_bytes() == tracked_v2.read_bytes(),
            "tracked/preparation v2 mutator differs")
    verify_stamp(
        config.prep_lane / "static/diagnostic-addresses.txt",
        (88, "e0c3f01b6fcea1c9fe0de328c7850a7c29e9f7aae59cd4ef9549bf013c917aa9"),
        "preparation diagnostic addresses",
    )
    verify_stamp(
        config.prep_lane / "static/pre-body-ranges.tsv",
        PRE_BODY_RANGES_STAMP, "preparation PRE body ranges",
    )

    deterministic = (
        "dry/functions.tsv", "dry/program.tsv", "dry/boundaries.tsv",
        "dry/listing-state.tsv", "apply/boundaries.tsv",
        "readback/functions.tsv", "readback/program.tsv",
        "readback/boundaries.tsv", "readback/listing-state.tsv",
        "accounting/body-ranges.tsv", "accounting/direct-calls.tsv",
        "accounting/parity-graph.ready.json", "projection.tsv",
    )
    replicas: dict[str, Any] = {}
    raw: dict[str, dict[str, bytes]] = {}
    for replica in ("a", "b"):
        root = config.prep_lane / f"formal-{replica}"
        project_root = config.prep_lane / f"formal-{replica}-project"
        backup = load_json(
            project_root / "backup_manifest.json",
            f"preparation {replica} source-copy manifest",
        )
        require(backup.get("schemaVersion") == project_backup.SCHEMA_VERSION,
                f"preparation {replica} backup schema")
        require(backup.get("sourceStable") is True, f"preparation {replica} source stability")
        require(backup.get("copyComparison", {}).get("matches") is True,
                f"preparation {replica} source-copy comparison")
        source = backup.get("source", {})
        destination = backup.get("destination", {})
        require_pre_project(source, f"preparation {replica} source PRE")
        require_pre_project(destination, f"preparation {replica} copied PRE")

        receipts = {
            mode: validate_preparation_receipt(config, replica, mode)
            for mode in ("dry", "apply", "readback")
        }
        verify_stamp(root / "dry/functions.tsv", PRE_FUNCTIONS_STAMP,
                     f"preparation {replica} PRE functions")
        verify_stamp(root / "dry/program.tsv", PRE_PROGRAM_STAMP,
                     f"preparation {replica} PRE program")
        verify_stamp(root / "dry/listing-state.tsv", PRE_LISTING_STAMP,
                     f"preparation {replica} PRE listing")
        scratch.verify_listing(root / "dry/listing-state.tsv", False)
        verify_stamp(root / "readback/functions.tsv", POST_FUNCTIONS_STAMP,
                     f"preparation {replica} POST functions")
        verify_stamp(root / "readback/program.tsv", POST_PROGRAM_STAMP,
                     f"preparation {replica} POST program")
        verify_stamp(root / "readback/listing-state.tsv", POST_LISTING_STAMP,
                     f"preparation {replica} POST listing")
        scratch.verify_listing(root / "readback/listing-state.tsv", True)
        for mode in ("dry", "apply", "readback"):
            validate_run_log(root / mode / "ghidra.log", mode)
        scratch.verify_diff(root / "inventory-diff.json", TARGETS)
        verify_stamp(root / "accounting/body-ranges.tsv", POST_BODY_RANGES_STAMP,
                     f"preparation {replica} POST body ranges")
        verify_stamp(root / "accounting/direct-calls.tsv", POST_DIRECT_CALLS_STAMP,
                     f"preparation {replica} POST direct calls")
        graph_stamp = verify_stamp(
            root / "accounting/parity-graph.ready.json", POST_GRAPH_RECEIPT_STAMP,
            f"preparation {replica} graph receipt",
        )
        graph = load_json(
            root / "accounting/parity-graph.ready.json",
            f"preparation {replica} graph receipt",
        )
        require(graph.get("bodyRanges", {}).get("functionCount") == POST_FUNCTIONS
                and graph.get("bodyRanges", {}).get("rangeCount") == POST_RANGES
                and graph.get("bodyRanges", {}).get("sha256") == POST_BODY_RANGES_STAMP[1]
                and graph.get("directCalls", {}).get("directEdgeCount") == 14584
                and graph.get("directCalls", {}).get("directCallSiteCount") == 27229
                and graph.get("directCalls", {}).get("sha256") == POST_DIRECT_CALLS_STAMP[1],
                f"preparation {replica} graph counts")
        verify_stamp(root / "projection.tsv", POST_PROJECTION_STAMP,
                     f"preparation {replica} POST projection")
        post = project_value(project_root)
        transition = validate_post_transition(destination, post,
                                              f"preparation {replica} POST transition")
        raw[replica] = {relative: (root / relative).read_bytes()
                        for relative in deterministic}
        replicas[replica] = {
            "sourceCopyManifest": stamp(
                project_root / "backup_manifest.json",
                f"{PREP_LANE_REL}/formal-{replica}-project/backup_manifest.json",
            ),
            "receipts": receipts,
            "postTransition": transition,
            "graphReceipt": graph_stamp,
        }
    for relative in deterministic:
        require(raw["a"][relative] == raw["b"][relative],
                f"preparation replicas differ: {relative}")
    return {
        "fullTree": measured_tree,
        "replicas": replicas,
        "semanticOutputsByteIdentical": True,
        "preFunctions": PRE_FUNCTIONS,
        "postFunctions": POST_FUNCTIONS,
        "postRanges": POST_RANGES,
        "postOwnedBytes": POST_OWNED,
        "physicalRollingDatabaseIdentityPinned": False,
    }


def prospective_projection(config: Config) -> dict[str, Any]:
    inventory = config.prep_lane / "formal-a/readback/functions.tsv"
    verify_stamp(inventory, POST_FUNCTIONS_STAMP, "current preparation POST functions")
    raw = name_projection.projection_bytes(
        inventory,
        expected_inventory_sha256=POST_FUNCTIONS_STAMP[1],
        source_label=PROJECTION_SOURCE,
        projection_date="2026-08-14",
        specimen_sha256=PROGRAM_SHA256,
    )
    measured = (len(raw), hashlib.sha256(raw).hexdigest())
    require(measured == POST_PROJECTION_STAMP, "prospective projection identity")
    for replica in ("a", "b"):
        materialized = config.prep_lane / f"formal-{replica}/projection.tsv"
        require(materialized.read_bytes() == raw,
                f"prospective projection differs from preparation {replica}")
    rows = sum(1 for line in raw.splitlines() if line and not line.startswith(b"#")) - 1
    require(rows == POST_FUNCTIONS, "prospective projection row count")
    return {"rows": rows, "bytes": measured[0], "sha256": measured[1],
            "materialized": False}


def prospective_body_accounting(config: Config) -> dict[str, Any]:
    raw = config.pre_accounting.read_bytes()
    require(raw.endswith(b"\n") and b"\r" not in raw, "PRE body accounting framing")
    lines = raw.decode("utf-8").splitlines()
    comments: list[str] = []
    while lines and lines[0].startswith("#"):
        comments.append(lines.pop(0))
    require(lines, "PRE body accounting header")
    header = lines.pop(0)
    fields = header.split("\t")
    require(fields == [
        "functionAddress", "functionName", "rangeOrdinal", "rangeMin", "rangeMax",
        "rangeEndExclusive", "rangeBytes", "rangeSha256",
    ], "PRE body accounting fields")
    rows = [dict(zip(fields, line.split("\t"), strict=True)) for line in lines]
    require(len(rows) == PRE_RANGES
            and len({row["functionAddress"].lower() for row in rows}) == PRE_FUNCTIONS,
            "PRE body accounting population")
    require(sum(int(row["rangeBytes"]) for row in rows) == PRE_OWNED,
            "PRE body accounting ownership")
    require(not set(POST_BODY_ROWS) & {row["functionAddress"].lower() for row in rows},
            "JPEG target already present in PRE accounting")
    for address, ranges in POST_BODY_ROWS.items():
        for ordinal, (start, maximum, end, size, digest) in enumerate(ranges, 1):
            rows.append({
                "functionAddress": address,
                "functionName": "FUN_" + address[2:],
                "rangeOrdinal": str(ordinal),
                "rangeMin": start,
                "rangeMax": maximum,
                "rangeEndExclusive": end,
                "rangeBytes": size,
                "rangeSha256": digest,
            })
    rows.sort(key=lambda row: (int(row["functionAddress"], 16),
                               int(row["rangeOrdinal"])))
    output = ("\n".join(comments + [header] + [
        "\t".join(row[field] for field in fields) for row in rows
    ]) + "\n").encode("utf-8")
    measured = (len(output), hashlib.sha256(output).hexdigest())
    require(measured == POST_BODY_RANGES_STAMP,
            "prospective POST body-accounting identity")
    require(len(rows) == POST_RANGES
            and len({row["functionAddress"].lower() for row in rows}) == POST_FUNCTIONS,
            "prospective POST body-accounting population")
    require(sum(int(row["rangeBytes"]) for row in rows) == POST_OWNED,
            "prospective POST body-accounting ownership")
    for replica in ("a", "b"):
        materialized = config.prep_lane / f"formal-{replica}/accounting/body-ranges.tsv"
        require(materialized.read_bytes() == output,
                f"prospective body accounting differs from preparation {replica}")
    return {
        "functions": POST_FUNCTIONS,
        "ranges": POST_RANGES,
        "ownedBytes": POST_OWNED,
        "uncoveredBytes": TEXT_BYTES - POST_OWNED,
        "bytes": measured[0],
        "sha256": measured[1],
        "materialized": False,
    }


def preflight(config: Config) -> dict[str, Any]:
    validate_layout(config)
    repo_inputs = validate_repo_inputs(config)
    targets = load_targets(config.repo / MANIFEST_REL)
    scratch_result = validate_scratch(config)
    preparation = validate_preparation_replicas(config)
    require(not config.live_lane.exists(), "canonical live lane already exists")
    require(not config.pre_backup.exists(), "PRE backup destination already exists")
    require(not config.post_backup.exists(), "POST backup destination already exists")
    authority_root = config.repo / Path(AUTHORITY_RECEIPT_REL).parent
    require(not authority_root.exists(), "canonical authority root already exists")

    live_before = project_value(config.live_project)
    tracked = project_value(config.tracked_project)
    live_after = project_value(config.live_project)
    require_pre_project(live_before, "live PRE first read")
    require_pre_project(live_after, "live PRE second read")
    require_pre_project(tracked, "tracked PRE")
    require_same_project(live_before, live_after, "live PRE stability")
    require_same_project(live_before, tracked, "live/tracked PRE")
    projection = verify_stamp(config.projection, PRE_PROJECTION_STAMP, PROJECTION_REL)
    accounting = verify_stamp(
        config.pre_accounting, PRE_BODY_RANGES_STAMP, "evidence/PRE body ranges"
    )
    post_projection = prospective_projection(config)
    post_accounting = prospective_body_accounting(config)
    return {
        "baseCommit": BASE_COMMIT,
        "policy": POLICY,
        "repositoryInputs": repo_inputs,
        "targets": len(targets),
        "scratchAuthority": scratch_result,
        "currentStatePreparation": preparation,
        "livePre": project_summary(live_before),
        "trackedPre": project_summary(tracked),
        "liveStableAcrossTwoReads": True,
        "liveEqualsTracked": True,
        "preProjection": projection,
        "preBodyAccounting": accounting,
        "prospectivePostProjection": post_projection,
        "prospectivePostBodyAccounting": post_accounting,
        "futureCeremonyArtifactsPresent": False,
        "futureMutationAuthorized": False,
        "blocker": "FUTURE_CEREMONY_ARTIFACTS_DO_NOT_EXIST",
        "verdict": "PREPARATION_READY_MUTATION_NOT_AUTHORIZED",
    }


@dataclass(frozen=True)
class RawTable:
    fields: tuple[str, ...]
    order: tuple[str, ...]
    rows: Mapping[str, Mapping[str, str]]
    raw_rows: Mapping[str, bytes]


def raw_tsv(path: Path, key: str) -> RawTable:
    raw = path.read_bytes()
    require(raw.endswith(b"\n") and b"\r" not in raw, f"{path} must be LF-only")
    lines = raw.splitlines()
    require(lines, f"empty TSV: {path}")
    while lines and lines[0].startswith(b"#"):
        lines.pop(0)
    require(lines, f"headerless TSV: {path}")
    try:
        fields = tuple(lines[0].decode("utf-8").split("\t"))
        text = b"\n".join(lines).decode("utf-8")
    except UnicodeError as exc:
        raise AuthorityError(f"invalid UTF-8 TSV: {path}") from exc
    require(key in fields and len(fields) == len(set(fields)), f"bad TSV header: {path}")
    rows: dict[str, Mapping[str, str]] = {}
    raw_rows: dict[str, bytes] = {}
    order: list[str] = []
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    for number, (row, raw_line) in enumerate(zip(reader, lines[1:]), start=2):
        value = str(row.get(key) or "").lower()
        require(value and value not in rows and None not in row,
                f"bad {key} at {path}:{number}")
        rows[value] = dict(row)
        raw_rows[value] = raw_line
        order.append(value)
    require(len(order) == len(lines) - 1, f"TSV parse incomplete: {path}")
    return RawTable(fields, tuple(order), rows, raw_rows)


def validate_function_delta(config: Config) -> dict[str, Any]:
    before_path = config.live_lane / "runs/live-pre-readback/functions.tsv"
    after_path = config.live_lane / "runs/live-readback/functions.tsv"
    verify_stamp(before_path, PRE_FUNCTIONS_STAMP, "live PRE functions")
    verify_stamp(after_path, POST_FUNCTIONS_STAMP, "live POST functions")
    prepared_before = config.prep_lane / "formal-a/dry/functions.tsv"
    prepared_after = config.prep_lane / "formal-a/readback/functions.tsv"
    require(before_path.read_bytes() == prepared_before.read_bytes(),
            "live/preparation PRE functions")
    require(after_path.read_bytes() == prepared_after.read_bytes(),
            "live/preparation POST functions")
    before = raw_tsv(before_path, "address")
    after = raw_tsv(after_path, "address")
    require(before.fields == after.fields, "function headers differ")
    require(len(before.order) == PRE_FUNCTIONS and len(after.order) == POST_FUNCTIONS,
            "function population differs")
    require(set(before.rows) <= set(after.rows), "PRE function address destroyed")
    for address, raw in before.raw_rows.items():
        require(after.raw_rows.get(address) == raw, f"PRE row changed at {address}")
    targets = {row["retail_va"].lower(): row
               for row in load_targets(config.repo / MANIFEST_REL)}
    created = set(after.rows) - set(before.rows)
    require(created == set(targets), "POST-only function set differs")
    for address, manifest in targets.items():
        row = after.rows[address]
        require(row["name"] == "FUN_" + address[2:]
                and row["nameSource"] == "DEFAULT", f"target metadata at {address}")
        require(int(row["bodyBytes"]) == int(manifest["body_bytes"]),
                f"target body bytes at {address}")
        require(int(row["bodyRanges"]) == int(manifest["body_range_count"]),
                f"target body ranges at {address}")
        require(int(row["instrCount"]) == int(manifest["instruction_count"]),
                f"target instructions at {address}")
    return {
        "pre": stamp(before_path, "live-lane/runs/live-pre-readback/functions.tsv"),
        "post": stamp(after_path, "live-lane/runs/live-readback/functions.tsv"),
        "unchangedRowsExact": PRE_FUNCTIONS,
        "changedRowsExact": 0,
        "createdAddresses": sorted(created),
        "created": TARGETS,
        "destroyed": 0,
    }


def read_metrics(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    require(rows and all(None not in row for row in rows), f"invalid metrics: {path}")
    result: dict[str, str] = {}
    for row in rows:
        key = str(row["metric"])
        require(key not in result, f"duplicate metric: {key}")
        result[key] = str(row["value"])
    return result


def validate_program_delta(config: Config) -> dict[str, Any]:
    before_path = config.live_lane / "runs/live-pre-readback/program.tsv"
    after_path = config.live_lane / "runs/live-readback/program.tsv"
    verify_stamp(before_path, PRE_PROGRAM_STAMP, "live PRE program")
    verify_stamp(after_path, POST_PROGRAM_STAMP, "live POST program")
    require(
        before_path.read_bytes()
        == (config.prep_lane / "formal-a/dry/program.tsv").read_bytes(),
        "live/preparation PRE program",
    )
    require(
        after_path.read_bytes()
        == (config.prep_lane / "formal-a/readback/program.tsv").read_bytes(),
        "live/preparation POST program",
    )
    before = read_metrics(before_path)
    after = read_metrics(after_path)
    require(set(before) == set(after), "program metric set differs")
    changed = {key for key in before if before[key] != after[key]}
    expected = {
        "functions", "instructions", "instructionLayoutSha256", "undefinedData",
        "symbolsDefaultOther", "references", "referencesSha256",
    }
    require(changed == expected, f"program changed metrics differ: {sorted(changed)}")
    require(before["functions"] == str(PRE_FUNCTIONS)
            and after["functions"] == str(POST_FUNCTIONS), "program function count")
    return {
        "pre": stamp(before_path, "live-lane/runs/live-pre-readback/program.tsv"),
        "post": stamp(after_path, "live-lane/runs/live-readback/program.tsv"),
        "changedMetrics": sorted(changed),
        "functions": {"before": PRE_FUNCTIONS, "after": POST_FUNCTIONS},
        "instructions": {"before": PRE_INSTRUCTIONS, "after": POST_INSTRUCTIONS},
        "references": {"before": PRE_REFERENCES, "after": POST_REFERENCES},
        "memoryUnchanged": before["memorySha256"] == after["memorySha256"],
        "definedDataUnchanged": before["definedDataSha256"] == after["definedDataSha256"],
        "storedNonFunctionSymbolsUnchanged":
            before["nonFunctionSymbolsSha256"] == after["nonFunctionSymbolsSha256"],
        "commentsUnchanged": before["commentsSha256"] == after["commentsSha256"],
    }


def validate_inventory_diff(config: Config) -> dict[str, Any]:
    path = config.live_lane / "runs/live-readback/inventory-diff.json"
    scratch.verify_diff(path, TARGETS)
    value = load_json(path, "live inventory diff")
    expected_counts = {
        "after": POST_FUNCTIONS, "before": PRE_FUNCTIONS, "boundsChanged": 0,
        "callingConvChanged": 0, "created": TARGETS, "destroyed": 0,
        "instrCountChanged": 0, "namesChanged": 0, "noReturnChanged": 0,
        "paramCountChanged": 0, "returnTypeChanged": 0,
        "sigSourceChanged": 0, "signaturesChanged": 0, "thunkFlagChanged": 0,
    }
    require(value.get("counts") == expected_counts, "inventory-diff counts")
    changes = value.get("changesByField", {})
    for field in changes:
        require(changes.get(field) == [], f"inventory-diff {field} changed")
    dangerous = value.get("dangerous", {})
    for key in ("gradedBoundsMovedCount", "gradedDemotedCount",
                "gradedDestroyedCount", "gradedRenamedCount"):
        require(dangerous.get(key) == 0, f"inventory-diff {key}")
    manifest = {row["retail_va"].lower(): row
                for row in load_targets(config.repo / MANIFEST_REL)}
    created = value.get("created", [])
    require({row.get("address") for row in created} == set(manifest),
            "inventory-diff created set")
    for row in created:
        expected = manifest[row["address"]]
        require(row == {
            "address": row["address"],
            "name": "FUN_" + row["address"][2:],
            "bodyBytes": expected["body_bytes"],
            "instrCount": expected["instruction_count"],
            "nameSource": "DEFAULT",
        }, f"inventory-diff created row {row.get('address')}")
    require(value.get("destroyed") == [], "inventory-diff destroyed set")
    return stamp(path, "live-lane/runs/live-readback/inventory-diff.json")


def validate_low_level_receipt(
    config: Config, run_name: str, mode: str
) -> datetime:
    root = config.live_lane / "runs" / run_name
    result_path = root / "boundaries.tsv"
    receipt = load_json(root / "boundaries.ready.json", f"{run_name} receipt")
    ensure_portable(receipt, f"{run_name} receipt")
    require(set(receipt) == {
        "schemaVersion", "completedAtUtc", "mode", "tool", "manifest", "output",
        "program", "counts", "explicitBodySetsAuthorized",
        "fixedPointAddressIsFunctionEntry", "fixedPointAddressIsData",
        "fixedPointInstructionOwner", "postCountsPinned", "namesAuthorized",
        "metadataAuthorized", "separateReadbackRequired",
    }, f"{run_name} receipt field set")
    require(receipt.get("schemaVersion") == "bea.ghidra.jpeg-callback-boundaries.v2",
            f"{run_name} schema")
    require(receipt.get("mode") == mode, f"{run_name} mode")
    require(receipt.get("manifest") == {
        "path": MANIFEST_REL, "bytes": EXPECTED_REPO_INPUTS[MANIFEST_REL][0],
        "sha256": EXPECTED_REPO_INPUTS[MANIFEST_REL][1],
    }, f"{run_name} manifest")
    require(receipt.get("tool") == {
        "path": "tools/GhidraApplyJpegCallbackBoundariesV2.java",
        "bytes": EXPECTED_REPO_INPUTS["tools/GhidraApplyJpegCallbackBoundariesV2.java"][0],
        "sha256": EXPECTED_REPO_INPUTS["tools/GhidraApplyJpegCallbackBoundariesV2.java"][1],
    }, f"{run_name} tool")
    measured = verify_stamp(result_path, BOUNDARY_STAMPS[mode], f"{run_name} boundaries")
    require(receipt.get("output") == {
        "path": f"{LIVE_LANE_REL}/runs/{run_name}/boundaries.tsv",
        "bytes": measured["bytes"], "sha256": measured["sha256"],
    }, f"{run_name} output")
    require(receipt.get("program") == {
        "name": PROGRAM_NAME, "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256,
    }, f"{run_name} program")
    before_functions = POST_FUNCTIONS if mode == "readback" else PRE_FUNCTIONS
    before_instructions = POST_INSTRUCTIONS if mode == "readback" else PRE_INSTRUCTIONS
    after_functions = POST_FUNCTIONS if mode != "dry" else PRE_FUNCTIONS
    after_instructions = POST_INSTRUCTIONS if mode != "dry" else PRE_INSTRUCTIONS
    require(receipt.get("counts") == {
        "targets": TARGETS,
        "externalInstructions": EXTERNAL_INSTRUCTIONS,
        "ghidraBodyInstructions": EXTERNAL_INSTRUCTIONS,
        "functionsBefore": before_functions,
        "functionsAfter": after_functions,
        "instructionsBefore": before_instructions,
        "instructionsAfter": after_instructions,
    }, f"{run_name} counts")
    require(receipt.get("explicitBodySetsAuthorized") is True,
            f"{run_name} body-set scope")
    require(receipt.get("fixedPointAddressIsFunctionEntry") is False
            and receipt.get("fixedPointAddressIsData") is False
            and receipt.get("fixedPointInstructionOwner") == "0x005b68fe",
            f"{run_name} fixed-point contract")
    require(receipt.get("postCountsPinned") is True, f"{run_name} post pins")
    require(receipt.get("namesAuthorized") is False
            and receipt.get("metadataAuthorized") is False,
            f"{run_name} metadata boundary")
    require(receipt.get("separateReadbackRequired") is (mode != "readback"),
            f"{run_name} readback policy")
    prepared_run = {
        "dry": "formal-a/dry/boundaries.tsv",
        "apply": "formal-a/apply/boundaries.tsv",
        "readback": "formal-a/readback/boundaries.tsv",
    }[mode]
    require(result_path.read_bytes() == (config.prep_lane / prepared_run).read_bytes(),
            f"{run_name} differs from current preparation {mode}")
    scratch.verify_boundaries(
        result_path, mode, load_targets(config.repo / MANIFEST_REL)
    )
    return parse_utc(receipt.get("completedAtUtc"), f"{run_name} completedAtUtc")


def validate_run_log(path: Path, mode: str) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="strict")
    require(text.count(f"JPEG_CALLBACK_BOUNDARIES_OK mode={mode}") == 1,
            f"{path.parent.name} success marker")
    for marker in (
        "REPORT SCRIPT ERROR", "JPEG_CALLBACK_BOUNDARIES_FAIL",
        "JPEG_CALLBACK_BOUNDARIES_MUTATION_TAINTED", "Exception", "Traceback",
    ):
        require(marker not in text, f"{path.parent.name} error marker: {marker}")
    saves = text.count("Save succeeded for processed file: /BEA.exe")
    read_only = text.count("Processing read-only project file: /BEA.exe")
    writable = len(re.findall(r"Processing project file: /BEA\.exe", text))
    if mode == "apply":
        require((saves, read_only, writable) == (1, 0, 1), f"{path.parent.name} apply shape")
    else:
        require((saves, read_only, writable) == (0, 1, 0), f"{path.parent.name} read-only shape")
    diagnostics = text.count("DiagnoseAddressListingState complete: rows=8 out=")
    require(diagnostics == (1 if mode in {"dry", "readback"} else 0),
            f"{path.parent.name} diagnostic shape")
    return {"successfulSaves": saves, "readOnlyOpens": read_only,
            "writableOpens": writable, "diagnosticExports": diagnostics}


def validate_runs(config: Config) -> tuple[dict[str, Any], dict[str, datetime]]:
    exact_directory_entries(
        config.live_lane / "runs",
        expected_files=(), expected_directories=RUN_LAYOUT.values(), label="live runs root",
    )
    summaries: dict[str, Any] = {}
    times: dict[str, datetime] = {}
    saves = 0
    for mode, run_name in RUN_LAYOUT.items():
        root = config.live_lane / "runs" / run_name
        expected = {"boundaries.tsv", "boundaries.ready.json", "ghidra.log"}
        if mode in {"dry", "readback"}:
            expected |= {"functions.tsv", "program.tsv", "listing-state.tsv"}
        if mode == "readback":
            expected.add("inventory-diff.json")
        exact_directory_entries(
            root, expected_files=expected, expected_directories=(), label=f"run {run_name}"
        )
        times[f"live.{mode}.receipt"] = validate_low_level_receipt(config, run_name, mode)
        shape = validate_run_log(root / "ghidra.log", mode)
        saves += shape["successfulSaves"]
        times[f"live.{mode}.complete"] = max(mtime_utc(path) for path in root.iterdir())
        summaries[mode] = {
            "receipt": stamp(root / "boundaries.ready.json", f"live-lane/runs/{run_name}/boundaries.ready.json"),
            "boundaries": stamp(root / "boundaries.tsv", f"live-lane/runs/{run_name}/boundaries.tsv"),
            "log": stamp(root / "ghidra.log", f"live-lane/runs/{run_name}/ghidra.log"),
            "processShape": shape,
        }
        if mode in {"dry", "readback"}:
            listing = root / "listing-state.tsv"
            expected_listing = PRE_LISTING_STAMP if mode == "dry" else POST_LISTING_STAMP
            verify_stamp(listing, expected_listing, f"{run_name} listing state")
            scratch.verify_listing(listing, mode == "readback")
            summaries[mode]["listingState"] = stamp(
                listing, f"live-lane/runs/{run_name}/listing-state.tsv"
            )
    require(saves == 1, "live lane does not contain exactly one successful save")
    summaries["functionDelta"] = validate_function_delta(config)
    summaries["programDelta"] = validate_program_delta(config)
    summaries["inventoryDiff"] = validate_inventory_diff(config)
    summaries["successfulLiveSaves"] = saves
    return summaries, times


def manifest_value(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value.get(key)
        for key in ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")
    }


def require_exact_comparison(value: Mapping[str, Any], label: str) -> None:
    require(value == {
        "extra": [],
        "extraCount": 0,
        "hashDiffCount": 0,
        "hashDifferences": [],
        "matches": True,
        "missing": [],
        "missingCount": 0,
        "sizeDiffCount": 0,
        "sizeDifferences": [],
    }, f"{label} comparison")


def validate_inspect(
    path: Path, expected_root: Path, expected: Mapping[str, Any], label: str
) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(manifest_value(value.get("manifest", {})) == project_without_root(expected),
            f"{label} manifest")
    require(clean_path(Path(value["manifest"].get("root", ""))) == clean_path(expected_root),
            f"{label} root")
    return parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")


def validate_backup_manifest(
    path: Path,
    expected: Mapping[str, Any],
    source_root: Path,
    destination_root: Path,
    label: str,
) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(value.get("sourceStable") is True, f"{label} source stability")
    require_exact_comparison(value.get("copyComparison", {}), f"{label} copy")
    require(manifest_value(value.get("source", {})) == project_without_root(expected),
            f"{label} source")
    require(manifest_value(value.get("destination", {})) == project_without_root(expected),
            f"{label} destination")
    require(
        clean_path(Path(value.get("source", {}).get("root", "")))
        == clean_path(source_root),
        f"{label} source root",
    )
    require(
        clean_path(Path(value.get("destination", {}).get("root", "")))
        == clean_path(destination_root),
        f"{label} destination root",
    )
    require(value.get("readonlyOpen") is None, f"{label} unexpectedly opened Ghidra")
    return parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")


def validate_restore_execution_paths(
    config: Config,
    value: Mapping[str, Any],
    retained_probe: Path,
    source_root: Path,
    label: str,
) -> None:
    require(
        clean_path(Path(value.get("source", {}).get("root", "")))
        == clean_path(source_root),
        f"{label} source root",
    )
    require(
        clean_path(Path(value.get("probeCopy", ""))) == clean_path(retained_probe),
        f"{label} probe-copy path",
    )
    expected_command = project_backup.build_open_command(
        ANALYZE_HEADLESS,
        retained_probe,
        "BEA",
        PROGRAM_NAME,
        config.repo / "tools",
        PROGRAM_MD5,
        PROGRAM_SHA256,
    )
    require(
        value.get("readonlyOpen", {}).get("commandArgv") == expected_command,
        f"{label} read-only command",
    )


def validate_restore(
    config: Config,
    receipt_name: str,
    probe_root_name: str,
    source_root: Path,
    expected: Mapping[str, Any],
    expected_total_functions: int,
    label: str,
) -> tuple[dict[str, Any], datetime]:
    path = config.live_lane / receipt_name
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(value.get("sourceStable") is True, f"{label} source stability")
    require(value.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
            f"{label} probe retention")
    require(manifest_value(value.get("source", {})) == project_without_root(expected),
            f"{label} source")
    require_exact_comparison(value.get("copyComparison", {}), f"{label} copy")
    opened = value.get("readonlyOpen", {})
    require(opened.get("opened") is True and opened.get("contentStable") is True,
            f"{label} read-only open")
    require(opened.get("exitCode") == 0
            and opened.get("observedFunctionCount") == expected_total_functions,
            f"{label} open result")
    require(opened.get("expectedProgramMd5") == PROGRAM_MD5
            and opened.get("expectedProgramSha256") == PROGRAM_SHA256
            and opened.get("observedProgramName") == PROGRAM_NAME
            and opened.get("observedProgramMd5") == PROGRAM_MD5
            and opened.get("observedProgramSha256") == PROGRAM_SHA256,
            f"{label} program identity")
    require_exact_comparison(opened.get("postOpenComparison", {}), f"{label} post-open")
    log = opened.get("probeLog", {})
    log_path = config.live_lane / receipt_name.replace(".json", ".open-probe.log")
    require(log.get("path") == log_path.name, f"{label} probe-log path")
    measured_log = stamp(log_path, f"live-lane/{log_path.name}")
    require((log.get("bytes"), log.get("sha256"))
            == (measured_log["bytes"], measured_log["sha256"]), f"{label} probe log")
    text = log_path.read_text(encoding="utf-8", errors="strict")
    sentinel = (
        f"GHIDRA_PROJECT_OPEN_PROBE_OK program={PROGRAM_NAME} md5={PROGRAM_MD5} "
        f"sha256={PROGRAM_SHA256} functions={expected_total_functions}"
    )
    require(text.count(sentinel) == 1, f"{label} exact success sentinel")
    require(text.count("Processing read-only project file: /BEA.exe") == 1,
            f"{label} read-only process marker")
    for marker in project_backup.GHIDRA_OPEN_ERROR_MARKERS:
        require(marker not in text, f"{label} error marker: {marker}")
    expected_probe_root = clean_path(config.live_lane / probe_root_name)
    entries = list(expected_probe_root.iterdir()) if expected_probe_root.is_dir() else []
    require(len(entries) == 1 and entries[0].is_dir()
            and not project_backup.is_reparse(expected_probe_root)
            and not project_backup.is_reparse(entries[0]),
            f"{label} retained probe topology")
    probe = clean_path(entries[0])
    validate_restore_execution_paths(config, value, probe, source_root, label)
    require_same_project(project_value(probe), expected, f"{label} retained probe")
    retained_manifest = probe / "backup_manifest.json"
    validate_backup_manifest(
        retained_manifest,
        expected,
        source_root,
        probe,
        f"{label} retained manifest",
    )
    return {
        "receipt": stamp(path, f"live-lane/{receipt_name}"),
        "probeLog": measured_log,
        "source": project_summary(expected),
        "retainedProbeEqualsSource": True,
        "retainedManifest": stamp(
            retained_manifest,
            f"live-lane/{probe_root_name}/retained/backup_manifest.json",
        ),
        "readOnlyOpen": True,
    }, parse_utc(value.get("verifiedAtUtc"), f"{label} verifiedAtUtc")


def validate_projects(
    config: Config, *, require_tracked_post: bool
) -> tuple[dict[str, Any], dict[str, datetime]]:
    times: dict[str, datetime] = {}
    pre = project_value(config.pre_backup)
    require_pre_project(pre, "PRE backup")
    live = project_value(config.live_project)
    transition = validate_post_transition(pre, live, "live POST")
    post_backup = project_value(config.post_backup)
    require_same_project(post_backup, live, "POST backup/live POST")
    tracked = project_value(config.tracked_project)
    if require_tracked_post:
        require_same_project(tracked, live, "tracked/live POST")
    else:
        require_pre_project(tracked, "tracked still PRE")

    times["live.pre.inspect"] = validate_inspect(
        config.live_lane / "live-pre-inspect.json", config.live_project, pre,
        "live PRE inspect",
    )
    times["tracked.pre.inspect"] = validate_inspect(
        config.live_lane / "tracked-pre-inspect.json", config.tracked_project, pre,
        "tracked PRE inspect",
    )
    times["live.beforeApply.inspect"] = validate_inspect(
        config.live_lane / "live-before-apply-inspect.json", config.live_project, pre,
        "live before-apply inspect",
    )
    times["live.post.inspect"] = validate_inspect(
        config.live_lane / "live-post-inspect.json", config.live_project, live,
        "live POST inspect",
    )
    times["tracked.stillPre.inspect"] = validate_inspect(
        config.live_lane / "tracked-still-pre-inspect.json", config.tracked_project, pre,
        "tracked still-PRE inspect",
    )
    times["pre.backup.created"] = validate_backup_manifest(
        config.pre_backup / "backup_manifest.json",
        pre,
        config.live_project,
        config.pre_backup,
        "PRE backup manifest",
    )
    times["post.backup.created"] = validate_backup_manifest(
        config.post_backup / "backup_manifest.json",
        live,
        config.live_project,
        config.post_backup,
        "POST backup manifest",
    )
    pre_restore, times["pre.restore.verified"] = validate_restore(
        config, "pre-backup-restore.ready.json", "pre-backup-restore-probe",
        config.pre_backup, pre, PRE_TOTAL_FUNCTIONS, "PRE restore",
    )
    post_restore, times["post.restore.verified"] = validate_restore(
        config, "post-backup-restore.ready.json", "post-backup-restore-probe",
        config.post_backup, live, POST_TOTAL_FUNCTIONS, "POST restore",
    )
    restores: dict[str, Any] = {"pre": pre_restore, "post": post_restore}
    if require_tracked_post:
        times["tracked.post.inspect"] = validate_inspect(
            config.live_lane / "tracked-post-inspect.json", config.tracked_project, live,
            "tracked POST inspect",
        )
        tracked_restore, times["tracked.restore.verified"] = validate_restore(
            config, "tracked-post-restore.ready.json", "tracked-post-restore-probe",
            config.tracked_project, live, POST_TOTAL_FUNCTIONS, "tracked POST restore",
        )
        restores["trackedPost"] = tracked_restore
    return {
        "pre": project_summary(pre),
        "post": project_summary(live),
        "liveEqualsPostBackup": True,
        "trackedState": "POST_EXACT" if require_tracked_post else "PRE_UNCHANGED",
        "trackedStillPreAfterPostRecovery": True,
        "rollingDelta": transition,
        "restores": restores,
        "backupReceipts": {
            "pre": stamp(config.pre_backup / "backup_manifest.json",
                         "pre-backup/backup_manifest.json"),
            "post": stamp(config.post_backup / "backup_manifest.json",
                          "post-backup/backup_manifest.json"),
        },
    }, times


def parse_body_rows(path: Path) -> tuple[list[bytes], list[dict[str, str]]]:
    raw = path.read_bytes()
    require(raw.endswith(b"\n") and b"\r" not in raw, "body ranges LF framing")
    lines = raw.splitlines()
    comments: list[bytes] = []
    while lines and lines[0].startswith(b"#"):
        comments.append(lines.pop(0))
    require(lines, "body ranges header")
    text = b"\n".join(lines).decode("utf-8")
    rows = list(csv.DictReader(text.splitlines(), delimiter="\t"))
    require(all(None not in row for row in rows), "body ranges malformed row")
    return comments, [{str(k): str(v) for k, v in row.items()} for row in rows]


def validate_body_accounting(config: Config) -> tuple[dict[str, Any], datetime]:
    root = config.live_lane / "tracked-post-accounting"
    exact_directory_entries(
        root,
        expected_files=("body-ranges.tsv", "direct-calls.tsv", "parity-graph.ready.json", "ghidra.log"),
        expected_directories=(), label="tracked POST accounting",
    )
    body = root / "body-ranges.tsv"
    verify_stamp(body, POST_BODY_RANGES_STAMP, "tracked POST body ranges")
    receipt = load_json(root / "parity-graph.ready.json", "tracked POST parity graph")
    require(receipt.get("schemaVersion") == "bea-ghidra-parity-graph-receipt.v2",
            "parity graph schema")
    program = receipt.get("program", {})
    require(program.get("executableMd5") == PROGRAM_MD5
            and program.get("imageBase") == "0x00400000"
            and program.get("language") == "x86:LE:32:default"
            and program.get("compilerSpec") == "windows", "parity graph program")
    measured_body = stamp(body, "live-lane/tracked-post-accounting/body-ranges.tsv")
    require(receipt.get("bodyRanges") == {
        "file": "body-ranges.tsv", "bytes": measured_body["bytes"],
        "sha256": measured_body["sha256"], "functionCount": POST_FUNCTIONS,
        "rangeCount": POST_RANGES,
    }, "parity graph body receipt")
    calls = stamp(root / "direct-calls.tsv",
                  "live-lane/tracked-post-accounting/direct-calls.tsv")
    call_receipt = receipt.get("directCalls", {})
    require(call_receipt.get("file") == "direct-calls.tsv"
            and (call_receipt.get("bytes"), call_receipt.get("sha256"))
            == (calls["bytes"], calls["sha256"]), "parity graph calls receipt")

    _, pre_rows = parse_body_rows(config.pre_accounting)
    _, post_rows = parse_body_rows(body)
    pre_by_function: dict[str, list[dict[str, str]]] = {}
    post_by_function: dict[str, list[dict[str, str]]] = {}
    for row in pre_rows:
        pre_by_function.setdefault(row["functionAddress"].lower(), []).append(row)
    for row in post_rows:
        post_by_function.setdefault(row["functionAddress"].lower(), []).append(row)
    require(set(pre_by_function) <= set(post_by_function), "PRE body function destroyed")
    require(set(post_by_function) - set(pre_by_function) == set(POST_BODY_ROWS),
            "POST-only body function set")
    require(len(post_by_function) == POST_FUNCTIONS and len(post_rows) == POST_RANGES,
            "body population")
    for address in pre_by_function:
        require(pre_by_function[address] == post_by_function[address],
                f"non-target body rows changed at {address}")
    manifest = {
        row["retail_va"].lower(): row
        for row in load_targets(config.repo / MANIFEST_REL)
    }
    for address, expected_rows in POST_BODY_ROWS.items():
        actual = post_by_function[address]
        require(len(actual) == len(expected_rows), f"body range count at {address}")
        require(all(row["functionName"] == "FUN_" + address[2:] for row in actual),
                f"body name at {address}")
        for ordinal, (row, expected) in enumerate(zip(actual, expected_rows), 1):
            require(row["rangeOrdinal"] == str(ordinal), f"body ordinal at {address}")
            measured = (
                row["rangeMin"], row["rangeMax"], row["rangeEndExclusive"],
                row["rangeBytes"], row["rangeSha256"],
            )
            require(measured == expected, f"body range identity at {address}:{ordinal}")
        require(sum(int(row["rangeBytes"]) for row in actual)
                == int(manifest[address]["body_bytes"]),
                f"manifest/body accounting bytes at {address}")
    intervals = sorted(
        (int(row["rangeMin"], 16), int(row["rangeEndExclusive"], 16))
        for row in post_rows
    )
    require(all(TEXT_START <= start < end <= TEXT_END for start, end in intervals),
            "body interval outside virtual text")
    require(all(left[1] <= right[0] for left, right in zip(intervals, intervals[1:])),
            "overlapping body intervals")
    owned = sum(end - start for start, end in intervals)
    require(owned == POST_OWNED, "POST body ownership")
    fixed_point_owners = [
        row for row in post_rows
        if int(row["rangeMin"], 16) <= 0x005B6900
        < int(row["rangeEndExclusive"], 16)
    ]
    require(len(fixed_point_owners) == 1
            and fixed_point_owners[0]["functionAddress"].lower() == "0x005b6800",
            "0x005B6900 body ownership")
    log = root / "ghidra.log"
    text = log.read_text(encoding="utf-8", errors="strict")
    require(text.count(f"PARITY_GRAPH_OK functions={POST_FUNCTIONS} ranges={POST_RANGES}") == 1,
            "accounting success marker")
    require(text.count("Processing read-only project file: /BEA.exe") == 1
            and "Save succeeded for processed file" not in text
            and "REPORT SCRIPT ERROR" not in text, "accounting read-only shape")
    complete = max(mtime_utc(path) for path in root.iterdir())
    return {
        "bodyRanges": measured_body,
        "parityGraphReceipt": stamp(root / "parity-graph.ready.json",
                                    "live-lane/tracked-post-accounting/parity-graph.ready.json"),
        "directCalls": calls,
        "log": stamp(log, "live-lane/tracked-post-accounting/ghidra.log"),
        "functions": POST_FUNCTIONS,
        "ranges": POST_RANGES,
        "ownedBytes": owned,
        "uncoveredBytes": TEXT_BYTES - owned,
        "ownedPercent": owned * 100.0 / TEXT_BYTES,
        "preservedPreFunctionRows": PRE_FUNCTIONS,
        "createdFunctionRowsExact": TARGETS,
        "bodyRangeDelta": BODY_RANGES,
        "ownedByteDelta": BODY_BYTES,
        "overlapBytes": 0,
    }, complete


def validate_projection(config: Config) -> tuple[dict[str, Any], datetime]:
    inventory = config.live_lane / "runs/live-readback/functions.tsv"
    retained = config.live_lane / "ghidra-function-name-table-2026-08-13.tsv"
    expected = name_projection.projection_bytes(
        inventory,
        expected_inventory_sha256=POST_FUNCTIONS_STAMP[1],
        source_label=PROJECTION_SOURCE,
        projection_date="2026-08-14",
        specimen_sha256=PROGRAM_SHA256,
    )
    require((len(expected), hashlib.sha256(expected).hexdigest()) == POST_PROJECTION_STAMP,
            "mechanical projection identity")
    require(retained.read_bytes() == expected, "retained projection is not mechanical")
    require(config.projection.read_bytes() == expected, "tracked projection is not mechanical")
    rows = sum(1 for line in expected.splitlines() if line and not line.startswith(b"#")) - 1
    require(rows == POST_FUNCTIONS, "projection row count")
    return {
        "rows": rows,
        "bytes": len(expected),
        "sha256": hashlib.sha256(expected).hexdigest(),
        "sourceInventory": stamp(inventory, "live-lane/runs/live-readback/functions.tsv"),
        "retained": stamp(retained, "live-lane/ghidra-function-name-table-2026-08-13.tsv"),
        "tracked": stamp(config.projection, PROJECTION_REL),
        "sourceLabel": PROJECTION_SOURCE,
    }, min(mtime_utc(retained), mtime_utc(config.projection))


def require_before(events: Mapping[str, datetime], left: str, right: str) -> None:
    require(events[left] < events[right], f"chronology does not advance: {left} -> {right}")


def validate_chronology(
    project_times: Mapping[str, datetime], run_times: Mapping[str, datetime],
    projection_time: datetime | None = None,
    accounting_time: datetime | None = None,
) -> list[dict[str, str]]:
    events = {**project_times, **run_times}
    edges = [
        ("live.pre.inspect", "pre.backup.created"),
        ("tracked.pre.inspect", "pre.backup.created"),
        ("pre.backup.created", "pre.restore.verified"),
        ("pre.restore.verified", "live.dry.receipt"),
        ("live.dry.receipt", "live.dry.complete"),
        ("live.dry.complete", "live.beforeApply.inspect"),
        ("live.beforeApply.inspect", "live.apply.receipt"),
        ("live.apply.receipt", "live.apply.complete"),
        ("live.apply.complete", "live.readback.receipt"),
        ("live.readback.receipt", "live.readback.complete"),
        ("live.readback.complete", "live.post.inspect"),
        ("live.post.inspect", "post.backup.created"),
        ("post.backup.created", "post.restore.verified"),
        ("post.restore.verified", "tracked.stillPre.inspect"),
    ]
    if projection_time is not None and accounting_time is not None:
        events["projection.complete"] = projection_time
        events["accounting.complete"] = accounting_time
        edges.extend([
            ("tracked.stillPre.inspect", "tracked.post.inspect"),
            ("tracked.post.inspect", "tracked.restore.verified"),
            ("tracked.restore.verified", "projection.complete"),
            ("tracked.restore.verified", "accounting.complete"),
        ])
    for left, right in edges:
        require_before(events, left, right)
    return [
        {"event": name, "atUtc": utc_text(events[name])}
        for name in sorted(events, key=lambda item: (events[item], item))
    ]


def expected_live_lane_topology(final: bool) -> tuple[set[str], set[str]]:
    files = {
        "live-pre-inspect.json", "tracked-pre-inspect.json",
        "pre-backup-restore.ready.json", "pre-backup-restore.ready.open-probe.log",
        "live-before-apply-inspect.json", "live-post-inspect.json",
        "post-backup-restore.ready.json", "post-backup-restore.ready.open-probe.log",
        "tracked-still-pre-inspect.json",
    }
    directories = {
        "static", "runs", "pre-backup-restore-probe", "post-backup-restore-probe",
    }
    if final:
        files |= {
            "tracked-post-inspect.json", "tracked-post-restore.ready.json",
            "tracked-post-restore.ready.open-probe.log",
            "ghidra-function-name-table-2026-08-13.tsv",
        }
        directories |= {"tracked-post-restore-probe", "tracked-post-accounting"}
    return files, directories


def validate_live_lane_topology(config: Config, *, final: bool) -> None:
    files, directories = expected_live_lane_topology(final)
    exact_directory_entries(
        config.live_lane, expected_files=files, expected_directories=directories,
        label="live evidence root",
    )
    exact_directory_entries(
        config.live_lane / "static", expected_files=(), expected_directories=("final-a",),
        label="live static root",
    )
    exact_directory_entries(
        config.live_lane / "static/final-a",
        expected_files=("jpeg-boundaries.tsv", "diagnostic-addresses.txt"),
        expected_directories=(),
        label="live manifest root",
    )
    verify_stamp(
        config.live_lane / "static/final-a/jpeg-boundaries.tsv",
        EXPECTED_REPO_INPUTS[MANIFEST_REL], "live manifest copy",
    )
    verify_stamp(
        config.live_lane / "static/final-a/diagnostic-addresses.txt",
        (88, "e0c3f01b6fcea1c9fe0de328c7850a7c29e9f7aae59cd4ef9549bf013c917aa9"),
        "live diagnostic-address copy",
    )


def validate_small_artifact_set(config: Config, *, final: bool) -> dict[str, Any]:
    validate_live_lane_topology(config, final=final)
    relative = [
        "live-pre-inspect.json", "tracked-pre-inspect.json",
        "pre-backup-restore.ready.json", "pre-backup-restore.ready.open-probe.log",
        "live-before-apply-inspect.json", "live-post-inspect.json",
        "post-backup-restore.ready.json", "post-backup-restore.ready.open-probe.log",
        "tracked-still-pre-inspect.json", "static/final-a/jpeg-boundaries.tsv",
        "static/final-a/diagnostic-addresses.txt",
    ]
    if final:
        relative += [
            "tracked-post-inspect.json", "tracked-post-restore.ready.json",
            "tracked-post-restore.ready.open-probe.log",
            "ghidra-function-name-table-2026-08-13.tsv",
            "tracked-post-accounting/body-ranges.tsv",
            "tracked-post-accounting/direct-calls.tsv",
            "tracked-post-accounting/parity-graph.ready.json",
            "tracked-post-accounting/ghidra.log",
        ]
    ledger = {
        name: stamp(config.live_lane / name, f"live-lane/{name}") for name in relative
    }
    for mode, run_name in RUN_LAYOUT.items():
        names = ["boundaries.ready.json", "boundaries.tsv", "ghidra.log"]
        if mode in {"dry", "readback"}:
            names += ["functions.tsv", "program.tsv", "listing-state.tsv"]
        if mode == "readback":
            names.append("inventory-diff.json")
        for name in names:
            role = f"runs/{run_name}/{name}"
            ledger[role] = stamp(config.live_lane / role, f"live-lane/{role}")
    return ledger


def build_live_phase(config: Config) -> dict[str, Any]:
    validate_layout(config)
    repo_inputs = validate_repo_inputs(config)
    scratch_result = validate_scratch(config)
    preparation = validate_preparation_replicas(config)
    load_targets(config.repo / MANIFEST_REL)
    projects, project_times = validate_projects(config, require_tracked_post=False)
    runs, run_times = validate_runs(config)
    chronology = validate_chronology(project_times, run_times)
    value = {
        "baseCommit": BASE_COMMIT,
        "policy": POLICY,
        "artifactLedger": {
            "repository": repo_inputs,
            "liveLane": validate_small_artifact_set(config, final=False),
        },
        "scratchAuthority": scratch_result,
        "currentStatePreparation": preparation,
        "projectsAndRecovery": projects,
        "liveRun": runs,
        "chronology": chronology,
        "trackedGhidraMutationPerformed": False,
        "futureMutationAuthorized": False,
        "verdict": "LIVE_PHASE_REPRODUCED_TRACKED_STILL_PRE",
    }
    ensure_portable(value)
    return value


def build_final(config: Config) -> dict[str, Any]:
    validate_layout(config)
    repo_inputs = validate_repo_inputs(config)
    scratch_result = validate_scratch(config)
    preparation = validate_preparation_replicas(config)
    load_targets(config.repo / MANIFEST_REL)
    projects, project_times = validate_projects(config, require_tracked_post=True)
    runs, run_times = validate_runs(config)
    projection, projection_time = validate_projection(config)
    accounting, accounting_time = validate_body_accounting(config)
    chronology = validate_chronology(
        project_times, run_times, projection_time, accounting_time
    )
    value = {
        "baseCommit": BASE_COMMIT,
        "policy": POLICY,
        "artifactLedger": {
            "repository": repo_inputs,
            "liveLane": validate_small_artifact_set(config, final=True),
        },
        "scratchAuthority": scratch_result,
        "currentStatePreparation": preparation,
        "projectsAndRecovery": projects,
        "liveRun": runs,
        "projection": projection,
        "bodyAccounting": accounting,
        "chronology": chronology,
        "claims": list(CLAIMS),
        "verdict": "LIVE_PROMOTION_REPRODUCED",
    }
    ensure_portable(value)
    return value


def validate_output(config: Config, *, sealing: bool) -> None:
    require(config.output is not None, "aggregate output is required")
    output = clean_path(config.output)
    require(output == clean_path(config.repo / AUTHORITY_RECEIPT_REL),
            "aggregate receipt must use the canonical authority path")
    for root in (
        config.live_lane, config.scratch_lane, config.prep_lane, config.live_project,
        config.pre_backup, config.post_backup, config.tracked_project,
    ):
        require(not is_within(output, clean_path(root)),
                "aggregate receipt overlaps an evidence or project root")
    if not sealing:
        require(output.is_file(), "saved aggregate receipt is absent")
        return
    require(not output.exists(), "refusing to overwrite aggregate receipt")
    require(is_within(output, clean_path(config.repo / "local-lab")),
            "aggregate receipt must be under local-lab")
    ignored = subprocess.run(
        ["git", "-C", str(config.repo), "check-ignore", "-q", "--", str(output)],
        check=False, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
    )
    require(ignored.returncode == 0, "aggregate receipt path is not Git-ignored")


def atomic_new_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.exists(), f"refusing to overwrite existing receipt: {path}")
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".partial", dir=path.parent
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def seal(config: Config) -> None:
    validate_output(config, sealing=True)
    value = {
        "schemaVersion": SCHEMA,
        "completedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authorityTool": stamp(
            Path(__file__).resolve(),
            "tools/ghidra_jpeg_callback_boundary_live_authority.py",
        ),
        "evidence": build_final(config),
        "policy": POLICY,
        "ghidraOpenedByAuthority": False,
        "liveGhidraMutatedByAuthority": False,
        "trackedGhidraMutatedByAuthority": False,
        "futureMutationAuthorized": False,
    }
    ensure_portable(value)
    assert config.output is not None
    atomic_new_json(config.output, value)
    print(
        "JPEG_CALLBACK_BOUNDARY_LIVE_AUTHORITY_READY "
        f"receipt_sha256={sha256_file(config.output)} functions={POST_FUNCTIONS} "
        f"ranges={POST_RANGES} gain={BODY_BYTES}"
    )


def verify(config: Config) -> None:
    validate_output(config, sealing=False)
    assert config.output is not None
    recorded = load_json(config.output, "aggregate authority receipt")
    require(recorded.get("schemaVersion") == SCHEMA, "aggregate schema")
    parse_utc(recorded.get("completedAtUtc"), "aggregate completedAtUtc")
    require(recorded.get("authorityTool") == stamp(
        Path(__file__).resolve(),
        "tools/ghidra_jpeg_callback_boundary_live_authority.py",
    ), "aggregate authority-tool binding")
    require(recorded.get("policy") == POLICY, "aggregate policy")
    require(recorded.get("ghidraOpenedByAuthority") is False
            and recorded.get("liveGhidraMutatedByAuthority") is False
            and recorded.get("trackedGhidraMutatedByAuthority") is False
            and recorded.get("futureMutationAuthorized") is False,
            "aggregate mutation boundary")
    require(recorded.get("evidence") == build_final(config),
            "aggregate evidence differs")
    ensure_portable(recorded)
    print(
        "JPEG_CALLBACK_BOUNDARY_LIVE_AUTHORITY_VERIFIED "
        f"receipt_sha256={sha256_file(config.output)} functions={POST_FUNCTIONS} "
        f"ranges={POST_RANGES} gain={BODY_BYTES}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "check-live", "seal", "verify"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--scratch-repo", type=Path, required=True)
    parser.add_argument("--live-project", type=Path, required=True)
    parser.add_argument("--live-lane", type=Path, required=True)
    parser.add_argument("--pre-backup", type=Path, required=True)
    parser.add_argument("--post-backup", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = Config(
        *(clean_path(value) for value in (
            args.repo, args.scratch_repo, args.live_project, args.live_lane,
            args.pre_backup, args.post_backup,
        )),
        clean_path(args.output) if args.output is not None else None,
    )
    if args.command == "preflight":
        require(config.output is None, "preflight does not accept --output")
        result = preflight(config)
        print(
            "JPEG_CALLBACK_BOUNDARY_LIVE_PREPARATION_READY "
            f"pre_project_sha256={result['livePre']['canonicalInventorySha256']} "
            f"scratch_receipt_sha256={SCRATCH_RECEIPT_STAMP[1]} "
            "live_equals_tracked=true db=db.18614.gbf "
            "policy=PREPARATION_ONLY mutation_authorized=false "
            "blocker=future_ceremony_artifacts_absent"
        )
    elif args.command == "check-live":
        require(config.output is None, "check-live does not accept --output")
        result = build_live_phase(config)
        print(
            "JPEG_CALLBACK_BOUNDARY_LIVE_PHASE_VERIFIED "
            f"post_functions={POST_FUNCTIONS} post_ranges={POST_RANGES} "
            f"verdict={result['verdict']} tracked_mutation_authorized=false"
        )
    elif args.command == "seal":
        seal(config)
    else:
        verify(config)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        AuthorityError,
        OSError,
        UnicodeError,
        subprocess.SubprocessError,
        project_backup.BackupError,
        name_projection.ProjectionError,
        scratch.AuthorityError,
    ) as exc:
        print(f"JPEG_CALLBACK_BOUNDARY_LIVE_AUTHORITY_REFUSED reason={exc}", file=sys.stderr)
        raise SystemExit(1)
