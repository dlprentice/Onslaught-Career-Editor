#!/usr/bin/env python3
"""Prove bounded CRound slot-0 arm paths and receiver writes from sealed TTD replays."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "bea.re.cround-handle-event-arm-effects-proof.v1"
READY_NAME = "proof.ready.json"
OVERLAY_SCHEMA = "bea.re.runtime-contract-overlay.v1"
ADJUDICATION_SCHEMA = "bea.re.runtime-contract-adjudication.v1"
REFUTER_SUBJECT_SCHEMA = "bea.re.refuter-subject.v1"
CLAIM = "CROUND_SLOT0_SELECTED_ARM_PATHS_AND_RECEIVER_WRITES_C2_BOUNDED"

SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
RUNTIME_SHA256 = "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
ENTITY_KEY = (
    "CODE:" + SPECIMEN_SHA256
    + ":VA=0x004d9910:RANGES=e285cbff91ced5bc10d7ba635f1f46c107615698ebd98d46c299c22bea5666b3"
)
CONTRACT_ID = "C-ff8b9307fccfd0ac"
QUESTION_ID = "Q-43f69708557c9e15"
CURRENT_NAME = "VFuncSlot_00_004d9910"

EVIDENCE_RELATIVE = Path("local-lab/cround-handle-event-arm-effects-20260812-v1")
CAMPAIGN_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-22-cround-handle-event-runtime-v1"
)
CAMPAIGN_READY = (20_759, "a0c8d3fb8d31f36e03b417b179bbe2f2c99f6dd47700e0f0ad2e8fad5feeac90")
CAMPAIGN_REDUCER_ID = "a757bc51cd8302cf0e889c7db72ca58f9d865597b250371444d8c2285537db09"
CAMPAIGN_AUTHORITY = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-22-cround-handle-event-runtime-authority.ready.json"
)
CAMPAIGN_AUTHORITY_STAMP = (
    15_761,
    "86b3fb12b18622dd837eb5e92b9f7ed8ecb7452c125f27bdca9d2fa98efab5b0",
)

ENTRY = 0x004D9910
ARM_ENTRIES = {
    "event4000": 0x004D9A54,
    "event4001": 0x004D997E,
    "event4002": 0x004D995E,
    "event4003": 0x004D9951,
    "default3000": 0x004D9D23,
}

RUNTIME_COLUMNS = [
    "contractId", "entityKey", "entityKind", "entryVa", "currentName",
    "nativeShippedName", "contractState", "semanticGrade", "receiver", "inputs",
    "returns", "writes", "sideEffects", "preconditions", "failureModes",
    "authorVerdict", "runtimeVerdict", "refuterVerdict", "questionIds",
    "evidenceRefs", "cheapestFalsifier", "rebuildOwner", "rebuildImplementation",
    "parityTests", "rebuildState", "remainingUncertainty", "supersedesEntityKeys",
    "lastMeasurementDate", "scopeKind", "payloadSha256", "receiverVtable",
    "observedCallVas", "controlSummary", "runtimeEvidenceSha256", "baseContractId",
    "questionIdsAddressed",
]

TRACE_LEVEL521 = (
    "G:\\bea-ttd\\level521-native-20260802-0018-take4\\"
    "level521-native-20260802-0018-take4.run",
    14_214_496_256,
    "45ab04297f32bb27ac0c80e8ecb0b332e666a9955caea0763a83984affb74ac2",
)
TRACE_LEVEL512 = (
    "G:\\bea-ttd\\level-opening-3m-v1-level512\\"
    "level-opening-3m-v1-level512.run",
    6_031_409_152,
    "3d3a118fe211ead7b1e41055e4150dcff576b6d0cc64879c52d1163beca94808",
)

COVERAGE_SPECS: dict[str, dict[str, Any]] = {
    "default3000": {
        "lane": "default3000-coverage-v1", "trace": TRACE_LEVEL521,
        "from": "0x66C70:0x55", "to": "0x66C70:0x5F9", "exit": 0,
        "quarantined": False, "gap": (158, 158, 0, 0, 0),
        "must_hit": {0xD9910, 0xD9D23, 0x19E0, 0xD8E40, 0x4B370},
        "must_miss": {0xD9A54, 0xD997E, 0xD995E, 0xD9951},
    },
    "event4003": {
        "lane": "event4003-coverage-v2", "trace": TRACE_LEVEL521,
        "from": "0x7021B:0x1AA3", "to": "0x7021B:0x1BCC", "exit": 0,
        "quarantined": False, "gap": (11, 11, 0, 0, 0),
        "must_hit": {0xD9910, 0xD9951, 0xDAC90, 0x4B370},
        "must_miss": {0xD9A54, 0xD997E, 0xD995E, 0xD9D23},
    },
    "event4001": {
        "lane": "event4001-coverage-v2", "trace": TRACE_LEVEL521,
        "from": "0x163B4D:0x2265", "to": "0x163B6F:0x1F0", "exit": 0,
        "quarantined": False, "gap": (7_495, 7_476, 7, 12, 0),
        "must_hit": {0xD9910, 0xD997E, 0xD9F30},
        "must_miss": {0xD9A54, 0xD995E, 0xD9951, 0xD9D23, 0xDB150},
    },
    "event4000Level521": {
        "lane": "event4000-level521-coverage-v2", "trace": TRACE_LEVEL521,
        "from": "0x66DA6:0xEE", "to": "0x66E63:0x25C", "exit": 11,
        "quarantined": True, "gap": (50_198, 50_098, 69, 31, 0),
        "must_hit": {0xD9910, 0xD9A54},
        "must_miss": {0xD997E, 0xD995E, 0xD9951, 0xD9D23},
    },
    "event4000Level512": {
        "lane": "event4000-level512-coverage-v1", "trace": TRACE_LEVEL512,
        "from": "0x18BC3B:0xECB", "to": "0x18BC72:0x37", "exit": 0,
        "quarantined": False, "gap": (8_077, 8_047, 10, 20, 0),
        "must_hit": {0xD9910, 0xD9A54, 0xD9D60, 0xD9F30, 0xCB3D0},
        "must_miss": {0xD997E, 0xD995E, 0xD9951, 0xD9D23, 0x19E0, 0xDAC90, 0xDB150},
    },
}

WRITE_SPECS: dict[str, dict[str, Any]] = {
    "default3000ShardA": {
        "lane": "default3000-writes-exact-shard-a-v1", "trace": TRACE_LEVEL521,
        "receiver": 0x07A38400, "from": "0x66C70:0x55", "to": "0x66C70:0x5F9",
        "events": 34, "pairs": 17, "nontrivial": 0, "breaks": 0, "gap_free": True,
        "writers": ((0x4015E0, 0x4018FA), (0x4019E0, 0x401B4F), (0x4D8E40, 0x4D9905)),
    },
    "default3000ShardB": {
        "lane": "default3000-writes-exact-shard-b-v2", "trace": TRACE_LEVEL521,
        "receiver": 0x07A38400, "from": "0x66C70:0x55", "to": "0x66C70:0x5F9",
        "events": 40, "pairs": 20, "nontrivial": 0, "breaks": 0, "gap_free": True,
        "writers": ((0x4015E0, 0x4018FA), (0x4019E0, 0x401B4F), (0x4D8E40, 0x4D9905)),
    },
    "default3000ShardC": {
        "lane": "default3000-writes-exact-shard-c-v1", "trace": TRACE_LEVEL521,
        "receiver": 0x07A38400, "from": "0x66C70:0x55", "to": "0x66C70:0x5F9",
        "events": 12, "pairs": 6, "nontrivial": 0, "breaks": 0, "gap_free": True,
        "writers": ((0x4015E0, 0x4018FA), (0x4019E0, 0x401B4F), (0x4D8E40, 0x4D9905)),
    },
    "event4003": {
        "lane": "event4003-writes-exact-v1", "trace": TRACE_LEVEL521,
        "receiver": 0x07A0B200, "from": "0x7021B:0x1AA3", "to": "0x7021B:0x1BCC",
        "events": 8, "pairs": 4, "nontrivial": 0, "breaks": 0, "gap_free": True,
        "writers": ((0x4DAC90, 0x4DAFE4),),
    },
    "event4001": {
        "lane": "event4001-writes-exact-v1", "trace": TRACE_LEVEL521,
        "receiver": 0x07A386F0, "from": "0x163B4D:0x2265", "to": "0x163B6F:0x1F0",
        "events": 18, "pairs": 9, "nontrivial": 19, "breaks": 9, "gap_free": False,
        "writers": ((0x4D9910, 0x4D9D46), (0x4D9F30, 0x4DAA03),
                    (0x4F43D0, 0x4F442F), (0x4F4430, 0x4F445D)),
    },
    "event4000Level521": {
        "lane": "event4000-level521-writes-exact-v1", "trace": TRACE_LEVEL521,
        "receiver": 0x07A0A930, "from": "0x66DA6:0xEE", "to": "0x66E63:0x25C",
        "events": 24, "pairs": 12, "nontrivial": 100, "breaks": 8, "gap_free": False,
        "writers": ((0x4D9910, 0x4D9D46), (0x4D9F30, 0x4DAA03), (0x4CB3D0, 0x4CB5B5)),
    },
    "event4000Level512": {
        "lane": "event4000-level512-writes-exact-v3", "trace": TRACE_LEVEL512,
        "receiver": 0x08228A50, "from": "0x18BC3B:0xECB", "to": "0x18BC72:0x37",
        "events": 32, "pairs": 16, "nontrivial": 30, "breaks": 17, "gap_free": False,
        "writers": ((0x4D9910, 0x4D9D46), (0x4D9F30, 0x4DAA03),
                    (0x4CB3D0, 0x4CB5B5), (0x4F3CB0, 0x4F3CDE),
                    (0x404150, 0x404170), (0x4D8AE0, 0x4D8D64)),
    },
}

PINNED_INPUTS: dict[str, tuple[int, str]] = {
    "gap-free-selection.json": (1_562, "5647539e02e7b9431cf40ab67a4e499ee484bdd949ff7880538bd9ad845643f2"),
    "barrier-selection.json": (3_108, "e486aae93113da7f8f663947246bf8798e19ff0d7538ebb67e275e6a173a6e7e"),
    "preregistration.md": (2_650, "10ec91cf25a8a321017436aec65e94898d2e9fa8ac783d185bc2d5a7f9ee9c98"),
    "preregistration-amendment-1.md": (871, "98cd54d1ba23ea6f3b343bd65d3d08f1e73d844f6c884b60abd6927382fd13f7"),
    "preregistration-amendment-2.md": (1_353, "9fedec480af2a816842cff18c071b264b4d4e90be64b4913ed6a8ff9367d2768"),
    "preregistration-amendment-3.md": (1_559, "4536b131537d82ae0c4a4c551073414622e16d6df87698a7372dc1734c8e042d"),
    "preregistration-amendment-4.md": (1_105, "955e1a1a179a3583a31ead2904e03b486a3dfe1b8a5515f6bd3ff1668166850c"),
    "preregistration-amendment-5.md": (682, "ec256e87247f3231e1ebb5fd03dea0757568987e6a11763a9207cbb8a102524a"),
    "preregistration-amendment-6.md": (1_659, "1959335b76492bc960374f34a1be2fe4b36f1a62b77dadc1c46fe78a69916e35"),
    "preregistration-amendment-7.md": (1_091, "ada3091adea51afdf03a46c06629d16956be52c4a81d89830ea36b7da2fb606d"),
    "preregistration-amendment-8.md": (1_701, "64065865d7b9620cde22a3d2c796bd3f47df328f3975e7d873c0be198ae3c7b0"),
    "preregistration-amendment-9.md": (1_939, "35d467dca25e0b5222b08c1033972689c630e147c1ff2729f455c77ac729afef"),
    "preregistration-amendment-10.md": (1_859, "48de5e2d403e37edf84ddf9c2d196f82f59a7ffdf2986d5078f3d20b7c772363"),
    "preregistration-amendment-11.md": (1_943, "a90b24181ca2b5d595d1cc67bf18ce105396e6735923d46f9bb5edb4d450b7e3"),
    "preregistration-amendment-12.md": (1_754, "ae09410eb0781b5822d963bc7bd1b91a477c6ca33af99b7c3358484160b2a175"),
    "preregistration-amendment-13.md": (914, "b0db7277ee6ea178156dc011b52381399024fff1900fea715cd7b7c461da7894"),
    "preregistration-amendment-14.md": (775, "ab7724bcf0391ee4e4cbf2e7c546dde6458d088bfa1405c0b4114e8e210c1cf8"),
    "event4003-coverage-v1-result-freeze.md": (1_048, "9ec017feaebfdcf60478690531e2be1a6594d6d0ddd45c0eb1102dec5ea84777"),
    "event4001-coverage-v1-result-freeze.md": (1_356, "c595166c5ea01736d3bbdda5ed9736ec3705b62d98f8e93688fbd99cd15ef5ef"),
    "event4000-level512-writes-exact-v1-result-freeze.md": (1_391, "0ae3aa648c9d6c498bb1703fb8ef809f17b2eb31bbd5f1cb1e3f8e5ec097dec2"),
    "event4000-level512-writes-exact-v2-result-freeze.md": (1_396, "d5329bab942fe0ebd78b728942b3caf0496b87f8a7bb430f6db949531ea4bdd8"),
    "event4000-level512-writes-exact-v3-result-freeze.md": (1_619, "689f6600fd65aa2ca6c3f11e99b35ec52785fc38d9e339b266940fde08897460"),
    "event4000-level521-writes-exact-v1-result-freeze.md": (1_734, "d84ce466a7eae11e133abeec6685282ba0ff2e1e2f2db67445452be046ff1398"),
}

ACCEPTED_FILE_PINS: dict[str, dict[str, tuple[int, str]]] = {
    "default3000-coverage-v1": {
        "coverage.jsonl": (17_634, "c71b9af5e43b35f4da8772e4220f0f7b8e5b0e1125ed2b17c80e8750bfb48d09"),
        "receipt.json": (6_714, "3157d4347035fd138ca14c65e2e5b17c5e05c0d4a52f9bebb4e68ea2acf0b81f"),
    },
    "event4003-coverage-v2": {
        "coverage.jsonl": (7_924, "4c921c110cd43888f606ad862d8310c103e3891f86a0ee6c336be5a4beff5ddf"),
        "receipt.json": (6_688, "fc5d6c9999d3426ba35044dbf5e81fecb4e21fe1ec8e4d44f0113c41a55b14b5"),
    },
    "event4001-coverage-v2": {
        "coverage.jsonl": (41_937, "e64c8cf0f6f709af1119ea33d74ae6c50e6c68c4a5c5364a393fcef422cb7e11"),
        "receipt.json": (6_711, "d7a516c9bde5f334a96f6c9eb7b6b6a8032f4c92391c4dd1212291c2a833d68b"),
    },
    "event4000-level521-coverage-v2": {
        "coverage.jsonl": (63_436, "322743e82b7f1d6486f73023f562a7de32b61e9289d5e97d2b049e1dbe5d8ab6"),
        "receipt.json": (6_851, "fbba18e9f92a99d62b91920949ba8ebda2a8332d5bbc0443e9e72be080e0b6cc"),
    },
    "event4000-level512-coverage-v1": {
        "coverage.jsonl": (62_258, "c75bea6d082c7eabc820d9dfb10c80333af06b728e8f15796fe34301858b4a1f"),
        "receipt.json": (6_782, "3d274b2232089a6d80b542780ccd2366d02f43bf1472cdf9afc255ca5eedfc36"),
    },
    "default3000-writes-exact-shard-a-v1": {
        "data-writes.jsonl": (55_390, "dfd84009d3f6b4307f5ef1d03c3fb57b74cc473cda9c4245bc80b0938576420a"),
        "receipt.json": (10_777, "595ff23888bc918caf3ab6a3e7c5d8fe87f3e8acf0946634e1aafa736ea6c8df"),
        "manifest.json": (6_957, "27715d2f9fa5d834e1700065e7fe28883ee439a1480c1c3a4f0525371c37a357"),
        "READY": (974, "60dc650c99db002734da83359961280b0efbd1e3422fec809471bf1fd341eb47"),
        "READY_WITNESSED_WRITES": (1_622, "df41b9463a749a72810b82546de7fa4bfeec97c33c0148d38d5c7f87b2ac83c5"),
        "targets.tsv": (382, "95358aeb72e906d360990030bbce7a83b8570e62b866f2e7fc33d3b3f5631192"),
    },
    "default3000-writes-exact-shard-b-v2": {
        "data-writes.jsonl": (61_900, "a401b14ebf977c90b55453f4543e5351ed089f18af9da327b2976ece5c890c26"),
        "receipt.json": (10_777, "d69727f4b7b911db0bb71f09329b0b34175f7b3af2507cbc68de42ef277c1fe3"),
        "manifest.json": (6_957, "ebc96622ed95c59e4b7bef31fcfbc3ffc9adbb457bf31548347d63059cf45eaf"),
        "READY": (974, "cdc9364fab9ca7918e32c5dcaca5aa0967f78d1f0ebce8d4b000326fa4366c0a"),
        "READY_WITNESSED_WRITES": (1_622, "6eb9c6117597038698e3cddde74031cb942e8a848b8907fb5abc27d5172f95de"),
        "targets.tsv": (382, "25316977a4b2c1db7edff28ec1dea66910efafb3ff92e5fa9612002c4fd5b1fd"),
    },
    "default3000-writes-exact-shard-c-v1": {
        "data-writes.jsonl": (20_639, "dfeb761d9090501e45471ea668bf47ed13dd20a6f91b917e71571860be4ebbae"),
        "receipt.json": (10_397, "1d54c80405d6c64fb3a354a15f09894e658cd1ab4ec71e495c4fdb5a25dfa34f"),
        "manifest.json": (6_559, "854ab048cd4e322041d632325de3ddeb65612e13dacccf6d9f47aa538c434564"),
        "READY": (974, "ab50cf71eeab900fa4cb21edeec41480d977df80300db58f8e8d8086bb3ae8a4"),
        "READY_WITNESSED_WRITES": (1_621, "d5009c901a9076abb45a5750092ac375ab95e29ff1c01344b7d9702b240f24b5"),
        "targets.tsv": (167, "51c98548e0183933fd30072b797a40464b8db713c84d076b00428ee1d3e042b4"),
    },
    "event4003-writes-exact-v1": {
        "data-writes.jsonl": (15_492, "11dd7b978b6f12d6477cb23bc5de331fad43d36c6f2568419c1b0160bfaad478"),
        "receipt.json": (10_139, "ff5d6bcfee5ea7ace4e28ea21dd99077dac861f3eabc7ea30d02e2a4ba35c8f3"),
        "manifest.json": (6_360, "2fb5dd8bcbcdbafe1e72e995ac0d831149a08bf67608ad50653c4ee59fa448d4"),
        "READY": (964, "eeac2de44107df7b007ba59b52366e3c02fde1b822ca0bcbe2b8226332f72a4b"),
        "READY_WITNESSED_WRITES": (1_502, "f4e072d14fedddc7f65f314831634f33eea352628a08d0d713312e43743dfd8f"),
        "targets.tsv": (148, "5af11429e82820f97606cd3c3cdc11f56e5172cdd475010203c771d988534f05"),
    },
    "event4001-writes-exact-v1": {
        "data-writes.jsonl": (30_727, "99e9fdd5ddd68c16f54cb864b7b95356ec9b549dcce5c969ffc810afa60c2342"),
        "receipt.json": (10_477, "590fd3a935772ba9e2df1d8d90f73a3af3f5032f67293397462b4509e1840ac5"),
        "manifest.json": (6_626, "b6ccd43d0f1c57dcc060dd904fc524f8831442605681e9723f3bb6851dcf734a"),
        "READY_WITNESSED_WRITES": (1_669, "1cbcdc9d961028554fad407b98d9890c5e738555cd0e9487080cbb9e54319c08"),
        "targets.tsv": (224, "5a388e8a9dbdcbaf4da25f95c0ffe9e3efb91af3a4ea889d0ce0df88687ecf4a"),
    },
    "event4000-level521-writes-exact-v1": {
        "data-writes.jsonl": (40_087, "905fcab1a9ac7c178573615f4afacd6e5c0ca2a220e4af053f5addefb8dc21d9"),
        "receipt.json": (10_628, "063726b959b35e5bce2eb38500e6a7dabbeb41d77ecc7a69c16d3544eb9da49f"),
        "manifest.json": (6_800, "cb3b4a503f3e58f1abdb09bb5a3e11063e997ffee62b28dbb75f11ebf161daca"),
        "READY_WITNESSED_WRITES": (1_627, "c2028f7f7f98c84e8bb41bf503492942b0d3c502672abca89bdcb893f6227b4a"),
        "targets.tsv": (282, "b30c3c8ba343107b5d84f3bf4b5f96c5b21850c6cb2c175f7caaa2ffd4449036"),
    },
    "event4000-level512-writes-exact-v3": {
        "data-writes.jsonl": (49_564, "654bf8c6d0a04897093590ab8f52151d9ac3755ac027c36d46e7b8cbf89d72f4"),
        "receipt.json": (10_757, "62562957381d5d38b1881e2b1fd1fc039910c38b277e9764aaf9db9ae8e6eed1"),
        "manifest.json": (6_889, "af137f294a010250d0f60fc44bb7e8700d8c5075d04961e8509b42679e6a02e9"),
        "READY_WITNESSED_WRITES": (1_789, "63609cbb0d1d22fdb0d53de2b775a793a4307c55614d6f9fb8c29a5ba16ac7db"),
        "targets.tsv": (282, "fb05f454bb127b0a800e179ba81456c0bbd3a69121643e1f16a93a880032fc5b"),
    },
}

REJECTED_FILE_PINS = {
    "event4003-coverage-v1": {
        "coverage.jsonl": (8_065, "be5411d8d7027d3a3bf73f4a3744081c9d31e01ae0335e4696eaa5be5374e095"),
        "receipt.json": (6_714, "3811bdda395ad2de98b41898e592652b99a464161d70358ddde0dc72e729155d"),
    },
    "event4001-coverage-v1": {
        "coverage.jsonl": (41_802, "1dfffe14e2ad93f2da97f89357106f04d0eba229d9dc4fea04364ee52179d509"),
        "receipt.json": (6_700, "fd9ec5ed1e87a929de468cad8b0de867dfaa047a5368fb3eb9b381f243270f06"),
    },
    "event4000-level512-writes-exact-v1": {
        "data-writes.jsonl": (49_518, "ea96fc7f94d2f82b8438c0bcc9cf29758477c2e5f8f88f7b99faa205ae9ff29d"),
        "receipt.json": (10_763, "f39b65465cebcddc906947555a2fe8514733538dfb723b44b7eb4f0f52cab4de"),
        "manifest.json": (6_889, "3624ccd9045125e27dc1924e149ffed52e6a324a35227101c34bdf6000f30aaf"),
        "targets.tsv": (282, "f31f7fa20669e6e564f9e2247cb72debec6c58997d32d17b8cc72f839231609e"),
    },
    "event4000-level512-writes-exact-v2": {
        "data-writes.jsonl": (49_564, "594c14523f54283e5193bb8691551bb569c535d7a547043abd253435a15d8808"),
        "receipt.json": (10_757, "23d6e11d33b60a46f7974d8bcd69a0d8ba3adcefd1a81d13732729a83f9c9499"),
        "manifest.json": (6_889, "141834ae9d35ad72172c584b136ab678df3218ce120d0e3c9af915673761cd05"),
        "READY_WITNESSED_WRITES": (1_789, "ec1903935d01a69f6dec884cbb3f9f82201e636a03318fff3f52580177958638"),
        "targets.tsv": (282, "fb05f454bb127b0a800e179ba81456c0bbd3a69121643e1f16a93a880032fc5b"),
    },
}

REPO_PINS = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2_506_752, SPECIMEN_SHA256),
    "local-lab/safe-copy-bea-pristine/BEA.exe": (2_506_752, RUNTIME_SHA256),
}


class ProofError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def stamp(path: Path, relative_to: Path | None = None) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path}")
    return {
        "path": str(path.resolve() if relative_to is None else path.resolve().relative_to(relative_to.resolve())),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def read_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        require(line.strip(), f"blank JSONL line in {path}:{index}")
        value = json.loads(line)
        require(isinstance(value, dict), f"non-object JSONL row in {path}:{index}")
        result.append(value)
    return result


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        first = handle.readline()
        if first.startswith("# "):
            first = handle.readline()
        return list(csv.DictReader([first, *handle], delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"# {OVERLAY_SCHEMA}\n")
        writer = csv.DictWriter(handle, fieldnames=RUNTIME_COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_int(value: Any) -> int:
    if isinstance(value, int):
        return value
    text = str(value)
    return int(text, 16 if text.lower().startswith("0x") else 10)


def validate_stamp(path: Path, expected: tuple[int, str], label: str) -> dict[str, Any]:
    require(path.is_file(), f"{label} is missing")
    actual = (path.stat().st_size, sha256_file(path))
    require(actual == expected, f"{label} differs")
    return stamp(path)


def validate_trace(receipt: dict[str, Any], expected: tuple[str, int, str], label: str) -> None:
    trace = receipt.get("trace", {})
    require(
        str(trace.get("path", "")).lower() == expected[0].lower()
        and parse_int(trace.get("bytes")) == expected[1]
        and str(trace.get("sha256", "")).lower() == expected[2],
        f"{label} trace identity differs",
    )
    target = receipt.get("target", {})
    require(
        parse_int(target.get("bytes")) == 2_506_752
        and str(target.get("sha256", "")).lower() == RUNTIME_SHA256,
        f"{label} runtime image differs",
    )


def validate_all_pins(root: Path, evidence: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for relative, expected in PINNED_INPUTS.items():
        result[relative] = validate_stamp(evidence / relative, expected, relative)
    for collection_name, collection in (
        ("accepted", ACCEPTED_FILE_PINS), ("rejected", REJECTED_FILE_PINS)
    ):
        for lane, files in collection.items():
            for name, expected in files.items():
                relative = f"{lane}/{name}"
                result[f"{collection_name}:{relative}"] = validate_stamp(
                    evidence / lane / name, expected, relative
                )
    for relative, expected in REPO_PINS.items():
        result[f"repo:{relative}"] = validate_stamp(root / relative, expected, relative)
    return result


def coverage_contains(rows: list[dict[str, Any]], rva: int) -> bool:
    return any(
        row.get("kind") == "range"
        and parse_int(row.get("rva_start")) <= rva < parse_int(row.get("rva_end_exclusive"))
        for row in rows
    )


def validate_coverage(evidence: Path, key: str, spec: dict[str, Any]) -> dict[str, Any]:
    lane = evidence / spec["lane"]
    receipt = read_json(lane / "receipt.json")
    rows = read_jsonl(lane / "coverage.jsonl")
    validate_trace(receipt, spec["trace"], key)
    invocation = receipt.get("invocation", {})
    require(invocation.get("from") == spec["from"] and invocation.get("to") == spec["to"], f"{key} coverage window differs")
    require(receipt.get("exitCode") == spec["exit"] and receipt.get("collectorExitCode") == spec["exit"], f"{key} coverage exit differs")
    require(receipt.get("replayComplete") is True and receipt.get("markerAssertionsPassed") is True and receipt.get("collectorChecksPassed") is True, f"{key} coverage checks failed")
    require(receipt.get("countersQuarantined") is spec["quarantined"], f"{key} counter quarantine differs")
    require({parse_int(value) for value in invocation.get("mustHitRva", [])} == spec["must_hit"], f"{key} hit assertions differ")
    require({parse_int(value) for value in invocation.get("mustMissRva", [])} == spec["must_miss"], f"{key} miss assertions differ")
    require(all(coverage_contains(rows, value) for value in spec["must_hit"]), f"{key} required coverage missing")
    require(not any(coverage_contains(rows, value) for value in spec["must_miss"]), f"{key} forbidden coverage observed")
    gaps = receipt.get("gapSummary", {})
    observed_gap = tuple(parse_int(gaps.get(field)) for field in (
        "total", "kind_no_gap", "kind_context_switch", "kind_unrecorded", "kind_large"
    ))
    require(observed_gap == spec["gap"], f"{key} gap partition differs")
    summaries = [row for row in rows if row.get("kind") == "summary"]
    require(len(summaries) == 1 and summaries[0].get("final_position") == spec["to"], f"{key} coverage summary differs")
    return {
        "lane": spec["lane"], "grade": "GAP_FREE_PATH" if spec["gap"][0] == spec["gap"][1] else "WITNESSED_PATH_WITH_GAP_LEDGER",
        "from": spec["from"], "to": spec["to"], "rangeCount": sum(row.get("kind") == "range" for row in rows),
        "coveredBytes": sum(parse_int(row.get("byte_count")) for row in rows if row.get("kind") == "range"),
        "mustHitRvas": [f"0x{value:X}" for value in sorted(spec["must_hit"])],
        "mustMissRvas": [f"0x{value:X}" for value in sorted(spec["must_miss"])],
        "gapPartition": {"total": spec["gap"][0], "noGap": spec["gap"][1], "contextSwitch": spec["gap"][2], "unrecorded": spec["gap"][3], "large": spec["gap"][4]},
        "receipt": stamp(lane / "receipt.json"), "coverage": stamp(lane / "coverage.jsonl"),
    }


def validate_write_lane(evidence: Path, key: str, spec: dict[str, Any]) -> dict[str, Any]:
    lane = evidence / spec["lane"]
    receipt = read_json(lane / "receipt.json")
    ready = read_json(lane / "READY_WITNESSED_WRITES")
    manifest = read_json(lane / "manifest.json")
    rows = read_jsonl(lane / "data-writes.jsonl")
    targets = read_tsv(lane / "targets.tsv")
    validate_trace(receipt, spec["trace"], key)
    invocation = receipt.get("invocation", {})
    require(invocation.get("from") == spec["from"] and invocation.get("to") == spec["to"], f"{key} write window differs")
    require(tuple(tuple(parse_int(part) for part in value.split(":")) for value in invocation.get("writerBodyRanges", [])) == spec["writers"], f"{key} writer ranges differ")
    data = receipt.get("dataWrites", {})
    require(parse_int(data.get("eventCount")) == spec["events"] and parse_int(data.get("pairCount")) == spec["pairs"] and parse_int(data.get("orphanEventCount")) == 0, f"{key} receipt counts differ")
    grade = receipt.get("witnessedGrade", {})
    require(grade.get("eligible") is True and parse_int(grade.get("eventCount")) == spec["events"] and parse_int(grade.get("pairCount")) == spec["pairs"], f"{key} witnessed grade differs")
    require(parse_int(grade.get("nontrivialGapCount")) == spec["nontrivial"] and parse_int(grade.get("continuityBreakCount")) == spec["breaks"] and grade.get("wouldAlsoBeGapFree") is spec["gap_free"], f"{key} gap grade differs")
    require(ready.get("grade") == "READY_WITNESSED_WRITES" and ready.get("alsoGapFree") is spec["gap_free"], f"{key} witnessed marker differs")
    require((lane / "READY").exists() is spec["gap_free"], f"{key} gap-free READY publication differs")
    require(manifest.get("schemaVersion") == "bea-ttd-data-writes-manifest.v3", f"{key} manifest schema differs")
    require(str(ready.get("receiptSha256", "")).lower() == sha256_file(lane / "receipt.json"), f"{key} marker receipt binding differs")
    require(str(ready.get("dataWritesSha256", "")).lower() == sha256_file(lane / "data-writes.jsonl"), f"{key} marker JSONL binding differs")
    event_rows = [row for row in rows if row.get("kind") == "event"]
    pair_rows = [row for row in rows if row.get("kind") == "pair"]
    target_rows = [row for row in rows if row.get("kind") == "target"]
    summary_rows = [row for row in rows if row.get("kind") == "summary"]
    require(len(event_rows) == spec["events"] and len(pair_rows) == spec["pairs"] and len(summary_rows) == 1, f"{key} independently counted rows differ")
    events_by_index = {parse_int(row["event_index"]): row for row in event_rows}
    normalized: list[dict[str, Any]] = []
    for expected_pair, pair in enumerate(pair_rows):
        require(parse_int(pair.get("pair_index")) == expected_pair and pair.get("checks_passed") is True, f"{key} pair ordering/check differs")
        before = events_by_index[parse_int(pair["overwrite_event_index"])]
        after = events_by_index[parse_int(pair["write_event_index"])]
        require(before.get("event_type") == "Overwrite" and after.get("event_type") == "Write", f"{key} event types differ")
        require(before.get("position") == after.get("position") and before.get("pc") == after.get("pc") and before.get("access_address") == after.get("access_address"), f"{key} pair identity differs")
        pc = parse_int(after["pc"])
        require(any(start <= pc < end for start, end in spec["writers"]), f"{key} writer outside admitted bodies")
        address = parse_int(after["access_address"])
        normalized.append({
            "pairIndex": expected_pair,
            "targetIndex": parse_int(pair["target_index"]),
            "receiverOffset": address - spec["receiver"],
            "address": f"0x{address:08X}",
            "size": parse_int(after["access_size"]),
            "writerPc": f"0x{pc:08X}",
            "position": after["position"],
            "beforeHex": before["observed_memory"]["hex"],
            "afterHex": after["observed_memory"]["hex"],
            "changed": bool(pair.get("changed")),
        })
    target_by_index = {parse_int(row["target_index"]): row for row in target_rows}
    require(len(target_by_index) == len(targets), f"{key} target row count differs")
    for table in targets:
        index = parse_int(table["target_index"])
        row = target_by_index[index]
        require(row.get("evidence_grade") == "WATCHPOINT_CHAIN_CLOSED" and row.get("evidence_checks_passed") is True and row.get("expectations_passed") is True, f"{key} target {index} is not closed")
        require(parse_int(row["address"]) == parse_int(table["address"]) and parse_int(row["size"]) == parse_int(table["size"]), f"{key} target {index} identity differs")
        require(parse_int(row["observed_pair_count"]) == parse_int(table["expected_write_count"]), f"{key} target {index} count differs")
    projection = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "lane": spec["lane"], "grade": "GAP_FREE_EXACT_RECEIVER_WRITES" if spec["gap_free"] else "WITNESSED_EXACT_RECEIVER_WRITES_WITH_GAP_LEDGER",
        "receiver": f"0x{spec['receiver']:08X}", "from": spec["from"], "to": spec["to"],
        "eventCount": spec["events"], "pairCount": spec["pairs"], "targetCount": len(targets),
        "nontrivialGapCount": spec["nontrivial"], "continuityBreakCount": spec["breaks"],
        "writerBodyRanges": [f"0x{start:08X}:0x{end:08X}" for start, end in spec["writers"]],
        "receiverOffsets": sorted({row["receiverOffset"] for row in normalized}),
        "sequence": normalized, "sequenceSha256": sha256_bytes(projection),
        "receipt": stamp(lane / "receipt.json"), "dataWrites": stamp(lane / "data-writes.jsonl"),
        "manifest": stamp(lane / "manifest.json"), "readyWitnessed": stamp(lane / "READY_WITNESSED_WRITES"),
    }


def validate_rejected_controls(evidence: Path) -> dict[str, Any]:
    event4003 = read_json(evidence / "event4003-coverage-v1/receipt.json")
    require(event4003.get("exitCode") == 10 and event4003.get("markerAssertionsPassed") is False and not (evidence / "event4003-coverage-v1/READY").exists(), "event4003 failed control was accepted")
    event4001 = read_json(evidence / "event4001-coverage-v1/receipt.json")
    require(event4001.get("exitCode") == 10 and event4001.get("markerAssertionsPassed") is False and not (evidence / "event4001-coverage-v1/READY").exists(), "event4001 failed control was accepted")
    level512v1 = read_json(evidence / "event4000-level512-writes-exact-v1/receipt.json")
    require(level512v1.get("witnessedWritesEligible") is False and level512v1.get("summary", {}).get("expectations_passed") is False and not (evidence / "event4000-level512-writes-exact-v1/READY_WITNESSED_WRITES").exists(), "Level512 v1 failed control was accepted")
    level512v2 = read_json(evidence / "event4000-level512-writes-exact-v2/receipt.json")
    require(level512v2.get("witnessedWritesEligible") is True and (evidence / "event4000-level512-writes-exact-v2/READY_WITNESSED_WRITES").is_file(), "Level512 v2 machine-pass control differs")
    amendment13 = (evidence / "preregistration-amendment-13.md").read_text(encoding="utf-8")
    amendment14 = (evidence / "preregistration-amendment-14.md").read_text(encoding="utf-8")
    freeze = (evidence / "event4000-level512-writes-exact-v2-result-freeze.md").read_text(encoding="utf-8")
    require(
        "24 events / 12 pairs" in amendment13
        and "16 pairs / 32 events" in amendment14
        and "REJECTED_PREREGISTRATION_CONTRADICTION" in freeze,
        "Level512 v2 analytical rejection chain differs",
    )
    return {
        "count": 4,
        "controls": [
            {"id": "event4003-return-marker-endpoint", "outcome": "failed_as_predicted_by_marker_semantics", "accepted": False},
            {"id": "event4001-wrong-adjacent-callee", "outcome": "falsified_0x004db150_and_selected_0x004d9f30", "accepted": False},
            {"id": "event4000-level512-wrong-count-table", "outcome": "failed_exact_target_expectations", "accepted": False},
            {"id": "event4000-level512-preregistration-contradiction", "outcome": "machine_pass_rejected_until_fresh_corrected_replay", "accepted": False},
        ],
    }


def validate_campaign(root: Path, campaign: Path) -> dict[str, Any]:
    ready_path = campaign / "campaign.ready.json"
    ready_stamp = validate_stamp(ready_path, CAMPAIGN_READY, "Generation 22 READY")
    authority_stamp = validate_stamp(root / CAMPAIGN_AUTHORITY, CAMPAIGN_AUTHORITY_STAMP, "Generation 22 authority")
    ready = read_json(ready_path)
    require(ready.get("generation") == 22 and ready.get("reducer", {}).get("id") == CAMPAIGN_REDUCER_ID, "Generation 22 identity differs")
    contract = next(row for row in read_tsv(campaign / "campaign-contracts.tsv") if row["contractId"] == CONTRACT_ID)
    question = next(row for row in read_tsv(campaign / "campaign-questions.tsv") if row["questionId"] == QUESTION_ID)
    require(contract.get("semanticGrade") == "C2_BOUNDED_RUNTIME" and contract.get("refuterVerdict") == "SURVIVED", "Generation 22 base contract differs")
    require(question.get("state") == "OPEN" and question.get("questionType") == "CROUND_HANDLEEVENT_ARM_EFFECTS_AND_WRITES", "Generation 22 successor differs")
    return {"generation": 22, "ready": ready_stamp, "authority": authority_stamp, "reducerId": CAMPAIGN_REDUCER_ID, "contract": contract, "question": question}


EXPECTED_BOUNDARY = {
    "selectedInvocations": 5,
    "independentTraceSessions": 2,
    "gapFreeInvocations": ["default3000", "event4003"],
    "barrierWitnessedInvocations": ["event4001", "event4000Level521", "event4000Level512"],
    "default3000ExactReceiverWritePairs": 43,
    "event4003ExactReceiverWritePairs": 4,
    "event4001ExactReceiverWritePairs": 9,
    "event4000Level521ExactReceiverWritePairs": 12,
    "event4000Level512ExactReceiverWritePairs": 16,
    "event4000CommonReceiverOffsets": [0x1C, 0x20, 0x24, 0x28, 0x2C, 0x38, 0x7C, 0x80, 0x84, 0x88, 0xE4],
    "event4000UniversalWriteSequenceClaimed": False,
    "externalWritesClaimed": False,
    "fieldMeaningsClaimed": False,
    "event2000EffectsClaimed": False,
    "event4002Observed": False,
    "cmissileStyleReceiverObserved": False,
    "completeArmSemanticsClaimed": False,
    "rebuildState": "PARTIAL_CONTRACT",
}


def derive(root: Path, campaign: Path) -> dict[str, Any]:
    evidence = root / EVIDENCE_RELATIVE
    require(evidence.is_dir(), "arm-effects evidence root is missing")
    inputs = validate_all_pins(root, evidence)
    coverage = {key: validate_coverage(evidence, key, spec) for key, spec in COVERAGE_SPECS.items()}
    writes = {key: validate_write_lane(evidence, key, spec) for key, spec in WRITE_SPECS.items()}
    controls = validate_rejected_controls(evidence)
    frontier = validate_campaign(root, campaign)
    default_pairs = sum(writes[key]["pairCount"] for key in ("default3000ShardA", "default3000ShardB", "default3000ShardC"))
    require(default_pairs == 43, "default3000 shard total differs")
    event4000_l521 = writes["event4000Level521"]
    event4000_l512 = writes["event4000Level512"]
    require(event4000_l521["receiverOffsets"] == event4000_l512["receiverOffsets"] == EXPECTED_BOUNDARY["event4000CommonReceiverOffsets"], "event4000 receiver offset set differs")
    require(event4000_l521["sequenceSha256"] != event4000_l512["sequenceSha256"], "event4000 independent states unexpectedly have one normalized sequence")
    boundary = copy.deepcopy(EXPECTED_BOUNDARY)
    return {
        "schema": SCHEMA, "verdict": "PASS", "claim": CLAIM,
        "specimen": {"sha256": SPECIMEN_SHA256, "role": "PRISTINE_STATIC_AUTHORITY_UNCHANGED"},
        "runtimeImage": {"sha256": RUNTIME_SHA256, "role": "SEALED_TRACE_RUNTIME_IMAGE"},
        "entity": {"entityKey": ENTITY_KEY, "contractId": CONTRACT_ID, "questionId": QUESTION_ID, "currentName": CURRENT_NAME},
        "campaign": frontier,
        "coverage": coverage,
        "writes": writes,
        "controls": controls,
        "crossSession": {
            "event4000CommonReceiverOffsets": boundary["event4000CommonReceiverOffsets"],
            "level521Pairs": 12, "level512Pairs": 16,
            "level521WriterBodies": len(WRITE_SPECS["event4000Level521"]["writers"]),
            "level512WriterBodies": len(WRITE_SPECS["event4000Level512"]["writers"]),
            "normalizedSequencesDiffer": True,
            "interpretation": "common high-level path and receiver location set with state-dependent writer/order divergence",
        },
        "adjudication": {
            "semanticGrade": "C2_BOUNDED_RUNTIME", "contractState": "BOUNDED_CONTRACT_ADVANCED",
            "runtimeVerdict": "MEASURED_SELECTED_ARM_PATHS_AND_EXACT_RECEIVER_WRITES_WITH_GRADE_PER_INVOCATION",
            "questionDisposition": "CLOSE_SELECTED_RECEIVER_WRITE_SCOPE_AND_OPEN_EXTERNAL_EFFECTS_SUCCESSOR",
        },
        "rebuild": {
            "state": "PARTIAL_CONTRACT",
            "implementation": "Level100ActorMechanics.AdvanceActorRounds",
            "scope": "nearest partial round owner; no explicit event queue or sufficient field semantics for a faithful arm implementation",
        },
        "claimBoundary": boundary,
        "limitations": [
            "The exact receiver writes are bounded to five selected invocations in two sealed sessions.",
            "Default/3000 and event 4003 are gap-free; event 4001 and both event-4000 invocations are witnessed-only across fully ledgered continuity barriers.",
            "Receiver watchpoints do not measure external allocation, container, event-manager, or all transitive callee effects.",
            "The event-4000 sessions share 11 receiver offsets but differ in pair count, writer bodies, values, and order; no universal write sequence is claimed.",
            "Event 2000 effects, event 4002, CMissile placement, field meanings, broader populations, source spelling, and direct rebuild parity remain open.",
            "Rejected controls are immutable inputs and contribute no positive evidence.",
            "No game, trace, Ghidra project, executable, or rebuild file was mutated by this proof.",
        ],
        "inputs": inputs,
        "author": stamp(Path(__file__).resolve()),
    }


def selftest(root: Path, campaign: Path) -> dict[str, Any]:
    value = derive(root, campaign)
    attacks: list[str] = []
    mutations = [
        ("universal-event4000", lambda x: x["claimBoundary"].__setitem__("event4000UniversalWriteSequenceClaimed", True)),
        ("external-write-overclaim", lambda x: x["claimBoundary"].__setitem__("externalWritesClaimed", True)),
        ("gapfree-overclaim", lambda x: x["claimBoundary"].__setitem__("gapFreeInvocations", ["default3000", "event4003", "event4001"])),
        ("rebuild-ready-overclaim", lambda x: x["claimBoundary"].__setitem__("rebuildState", "REBUILD_READY")),
    ]
    for label, mutate in mutations:
        changed = copy.deepcopy(value)
        mutate(changed)
        try:
            require(changed["claimBoundary"] == EXPECTED_BOUNDARY, f"{label} rejected")
        except ProofError:
            attacks.append(label)
        else:
            raise ProofError(f"selftest attack accepted: {label}")
    require(len(attacks) == len(mutations), "selftest count differs")
    return {"count": len(attacks), "attacks": attacks}


def validate_saved(saved: dict[str, Any], root: Path, campaign: Path) -> None:
    require(set(saved) == set(derive(root, campaign)) | {"generatedAtUtc", "selftest"}, "proof shape differs")
    timestamp = saved.get("generatedAtUtc")
    require(isinstance(timestamp, str) and timestamp.endswith("Z"), "proof timestamp is not UTC")
    datetime.fromisoformat(timestamp[:-1] + "+00:00")
    stable = dict(saved)
    stable.pop("generatedAtUtc")
    tests = stable.pop("selftest")
    require(tests == selftest(root, campaign), "proof selftest differs")
    require(stable == derive(root, campaign), "proof content differs from rederived evidence")


def build(root: Path, campaign: Path, out: Path) -> Path:
    out = out.resolve()
    require(not out.exists(), f"refusing existing proof root: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        value = derive(root, campaign)
        value["selftest"] = selftest(root, campaign)
        value["generatedAtUtc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        ready = stage / READY_NAME
        ready.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        validate_saved(read_json(ready), root, campaign)
        os.replace(stage, out)
        return out / READY_NAME
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify(root: Path, campaign: Path, proof: Path) -> dict[str, Any]:
    value = read_json(proof / READY_NAME)
    validate_saved(value, root, campaign)
    return value


def relative_artifact(proof_ready: Path, path: Path, role: str) -> dict[str, Any]:
    require(path.is_file(), f"overlay artifact missing: {role}")
    value = stamp(path)
    value["path"] = os.path.relpath(path.resolve(), proof_ready.parent.resolve()).replace("\\", "/")
    value["role"] = role
    return value


def build_overlay(root: Path, campaign: Path, proof: Path, out: Path) -> Path:
    saved = verify(root, campaign, proof)
    require(not out.exists(), f"refusing existing overlay root: {out}")
    base = saved["campaign"]["contract"]
    accepted_lanes = [spec["lane"] for spec in WRITE_SPECS.values()]
    evidence_refs = [str((proof / READY_NAME).resolve()), str((root / EVIDENCE_RELATIVE / "preregistration.md").resolve())]
    row = dict(base)
    row.update({
        "contractState": "RUNTIME_CANDIDATE_NEEDS_REFUTER",
        "semanticGrade": "C2_BOUNDED_RUNTIME",
        "receiver": "five selected strict-CRound receivers in two sealed sessions; one default/3000, one event 4003, one event 4001, and independent Level-521/Level-512 event-4000 states",
        "inputs": "caller-selected event IDs and session-local receiver/event records inherited from the Gen22 call-entry-arm contract; exact windows fixed before replay",
        "returns": "gap-free complete envelopes for default/3000 and event 4003; unique raw returns with complete gap ledgers for event 4001 and both event-4000 paths",
        "writes": "43 default/3000, 4 event-4003, 9 event-4001, 12 Level-521 event-4000, and 16 Level-512 event-4000 exact receiver write pairs; raw widths, before/after bytes, order, and writer PCs are hash-bound",
        "sideEffects": "coverage binds selected arms and observed callees; event-4000 sessions share 11 receiver offsets but have state-dependent pair counts, writer bodies, values, and ordering",
        "preconditions": "five preselected invocations in the named Level-521 and Level-512 recordings; exact receiver watch tables narrowed only after frozen discovery",
        "failureModes": "external writes/effects, field meanings, event 2000, event 4002, CMissile placement, broader receiver states, source spelling, and direct rebuild parity remain open",
        "authorVerdict": "SUPPORTED_BY_HASH_PINNED_COVERAGE_AND_EXACT_RECEIVER_WATCHPOINT_CHAINS_WITH_REJECTED_CONTROLS",
        "runtimeVerdict": "MEASURED_SELECTED_ARM_PATHS_AND_EXACT_RECEIVER_WRITES_WITH_GRADE_PER_INVOCATION",
        "refuterVerdict": "UNSCORED",
        "questionIds": QUESTION_ID,
        "evidenceRefs": ";".join(evidence_refs),
        "cheapestFalsifier": "Independently parse any accepted exact JSONL and find a missing/additional pair, changed receiver-relative offset/value/order/writer, or a gap grade inconsistent with its READY marker.",
        "rebuildOwner": "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs",
        "rebuildImplementation": "Level100ActorMechanics.AdvanceActorRounds (nearest partial owner; no explicit retail event queue)",
        "parityTests": "Level100ActorWeaponTests.ActorArmament_IsCanonicalReplayState (nearest partial state test; no arm-effects parity test)",
        "rebuildState": "PARTIAL_CONTRACT",
        "remainingUncertainty": "external allocation/container/event-manager writes and effects; event 2000; event 4002; CMissile placement; field semantics; broader state populations; source spelling; direct reconstruction parity",
        "lastMeasurementDate": "2026-08-12",
        "scopeKind": "EXISTING_TTD_FIVE_SELECTED_SLOT0_ARM_PATHS_AND_RECEIVER_WRITES",
        "payloadSha256": "",
        "receiverVtable": "0x005de82c",
        "observedCallVas": "0x0044b68a",
        "controlSummary": "four rejected controls: two wrong path assertions, one wrong exact count table, and one mechanically passing but preregistration-contradictory run; none contributes positive evidence",
        "runtimeEvidenceSha256": ";".join(saved["writes"][key]["dataWrites"]["sha256"] for key in WRITE_SPECS),
        "baseContractId": CONTRACT_ID,
        "questionIdsAddressed": QUESTION_ID,
    })
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        ledger = stage / "runtime-contracts.tsv"
        write_tsv(ledger, [row])
        artifacts = [relative_artifact(proof / READY_NAME, Path(__file__).resolve(), "proof-author")]
        artifacts.extend(relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / name, name) for name in PINNED_INPUTS)
        for lane in accepted_lanes:
            artifacts.append(relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / lane / "data-writes.jsonl", f"accepted-write:{lane}"))
        for lane in COVERAGE_SPECS.values():
            artifacts.append(relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / lane["lane"] / "coverage.jsonl", f"accepted-coverage:{lane['lane']}"))
        receipt = {
            "schema": OVERLAY_SCHEMA, "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "sourceCampaign": {"path": str(campaign.resolve()), "ready": stamp(campaign / "campaign.ready.json"), "specimen": read_json(campaign / "campaign.ready.json")["sourceSnapshot"]["specimen"]},
            "inputContract": stamp(proof / READY_NAME), "artifacts": artifacts,
            "authorVerification": {"checks": saved["selftest"], "claimBoundary": saved["claimBoundary"]},
            "count": 1,
            "policy": {"namesAuthorized": False, "ghidraMutationAuthorized": False, "promotionAuthorized": False, "requiresRefuter": True, "maximumImportedGrade": "C2_BOUNDED_RUNTIME", "artifactClaimsParsed": True, "runtimeExecutableRelationValidated": True},
            "output": {**stamp(ledger), "path": ledger.name},
        }
        (stage / "runtime-contracts.ready.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(stage, out)
        return out / "runtime-contracts.ready.json"
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def overlay_subject(overlay: Path) -> dict[str, Any]:
    rows = read_tsv(overlay / "runtime-contracts.tsv")
    require(len(rows) == 1, "overlay row count differs")
    row = rows[0]
    canonical = json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"schema": REFUTER_SUBJECT_SCHEMA, "baseContractId": row["baseContractId"], "entityKey": row["entityKey"], "overlayReadySha256": sha256_file(overlay / "runtime-contracts.ready.json"), "questionIdsAddressed": [value for value in row["questionIdsAddressed"].split(";") if value], "candidateRowSha256": sha256_bytes(canonical)}


def build_finding(root: Path, proof: Path, overlay: Path, out: Path) -> Path:
    saved = read_json(proof / READY_NAME)
    subject = overlay_subject(overlay)
    finding = {
        "schemaVersion": 1, "id": "cround-slot0-selected-arm-receiver-writes-2026-08-12",
        "title": "CRound slot-0 selected arm paths and exact receiver writes",
        "date": "2026-08-12", "lane": "ttd/existing-trace", "author": "recursive RE campaign",
        "sourceNote": str((proof / READY_NAME).resolve()), "findingKind": "instrument-derived",
        "claim": {"statement": "Five selected strict-CRound slot-0 invocations follow the saved arm paths and exact receiver-write sequences, with the saved grade for each window.", "grade": "EXECUTED", "mechanism": ["cround.slot0.selected_arm_receiver_writes"]},
        "scope": {"population": "five preselected invocations in the named Level 521 and Level 512 retained recordings", "covered": "two gap-free and three gap-ledgered invocation windows; 84 exact receiver write pairs across seven non-overlapping exact-watch lanes", "notCovered": ["external allocation/container/event-manager writes or effects", "event 2000", "event 4002", "CMissile receiver placement", "field meanings", "other receiver states", "source spelling and direct rebuild parity"]},
        "rivals": [
            {"id": "rival-uniform-event4000", "statement": "Event 4000 has one uniform receiver-write sequence across the two sessions.", "indistinguishableOn": ["same static arm entry", "same 11 receiver-relative locations"], "discriminator": {"description": "compare normalized pair counts, writer PCs, values, and order across the independently selected sessions", "mechanism": ["cround.slot0.selected_arm_receiver_writes"], "expectedUnderClaim": "state-dependent sequences may differ while their bounded paths remain valid", "expectedUnderRival": "the normalized sequences are identical", "status": "observed", "outcome": "claim", "evidenceRef": ["e-event4000-level521", "e-event4000-level512"]}},
            {"id": "rival-instrument-always-passes", "statement": "The replay/wrapper pipeline accepts wrong marker and count predictions.", "indistinguishableOn": ["accepted positive replays alone"], "discriminator": {"description": "retain and inspect preregistered wrong-path and wrong-count controls", "mechanism": ["cround.slot0.selected_arm_receiver_writes"], "expectedUnderClaim": "wrong predictions fail and publish no admissible positive marker", "expectedUnderRival": "wrong predictions are accepted", "status": "observed", "outcome": "claim", "evidenceRef": ["e-controls"]}},
        ],
        "predictions": [
            {"id": "p-event4000-holdout-path", "statement": "The independent Level-512 event-4000 holdout will traverse the common high-level effect path.", "procedure": "replay the preregistered Level-512 window with exact coverage markers", "expected": "hit slot0, event4000, initialization, effect, and particle bodies; miss other arms and unrelated round helpers", "wouldFalsifyIf": "any required hit is absent or forbidden marker is present", "predictedInAdvance": True, "statedAt": "local-lab/cround-handle-event-arm-effects-20260812-v1/preregistration-amendment-11.md", "result": "match", "observed": "all required and forbidden markers passed", "evidenceRef": ["e-event4000-level512"]},
            {"id": "p-event4000-cross-state-uniformity", "statement": "The Level-512 holdout may falsify cross-session uniform receiver writes without invalidating the bounded path.", "procedure": "freeze broad discovery, preregister exact targets, then compare the corrected fresh replay with Level 521", "expected": "same high-level arm/location set; a different sequence is admissible and must be preserved", "wouldFalsifyIf": "the tool forces a Level-521 sequence or hides a different Level-512 sequence", "predictedInAdvance": True, "statedAt": "local-lab/cround-handle-event-arm-effects-20260812-v1/preregistration-amendment-11.md", "result": "match", "observed": "same 11 offsets, but 12 versus 16 pairs and three versus six writer bodies", "evidenceRef": ["e-event4000-level521", "e-event4000-level512"]},
        ],
        "evidence": [
            {"id": "e-gapfree-arms", "grade": "EXECUTED", "instrument": "hash-pinned TTD coverage and exact data-write replay", "summary": "default/3000 and event4003 complete gap-free paths with 47 exact receiver pairs", "sample": {"n": 2, "units": "selected invocation windows", "independentReplicates": 1, "sessions": 1}, "specimen": {"path": TRACE_LEVEL521[0], "sha256": TRACE_LEVEL521[2]}},
            {"id": "e-event4001", "grade": "EXECUTED", "instrument": "hash-pinned TTD coverage and witnessed-write replay", "summary": "one barrier-crossing event4001 window with nine exact receiver pairs", "sample": {"n": 1, "units": "selected invocation window", "independentReplicates": 1, "sessions": 1}, "specimen": {"path": TRACE_LEVEL521[0], "sha256": TRACE_LEVEL521[2]}},
            {"id": "e-event4000-level521", "grade": "EXECUTED", "instrument": "hash-pinned TTD coverage and witnessed-write replay", "summary": "one Level-521 event4000 window with 12 exact receiver pairs", "sample": {"n": 1, "units": "selected invocation window", "independentReplicates": 1, "sessions": 1}, "specimen": {"path": TRACE_LEVEL521[0], "sha256": TRACE_LEVEL521[2]}},
            {"id": "e-event4000-level512", "grade": "EXECUTED", "instrument": "hash-pinned TTD coverage and witnessed-write replay", "summary": "one independent Level-512 event4000 window with 16 exact receiver pairs", "sample": {"n": 1, "units": "selected invocation window", "independentReplicates": 1, "sessions": 1}, "specimen": {"path": TRACE_LEVEL512[0], "sha256": TRACE_LEVEL512[2]}},
            {"id": "e-controls", "grade": "EXECUTED", "instrument": "same replay/wrapper pipeline with frozen wrong predictions", "summary": "four rejected controls remained excluded from positive evidence", "sample": {"n": 4, "units": "rejected control runs", "independentReplicates": 1, "sessions": 2}},
        ],
        "residuals": [
            {"id": "res-external-effects", "statement": "Receiver watches do not cover external allocation, container, event-manager, or all transitive callee effects.", "mechanism": ["cround.slot0.external_arm_effects"], "blocksClaim": False},
            {"id": "res-unobserved-arms", "statement": "Event 2000 effects and event 4002 remain unmeasured.", "mechanism": ["cround.slot0.unobserved_arm_effects"], "blocksClaim": False},
            {"id": "res-population", "statement": "Other strict-CRound states and CMissile-style receivers remain outside this five-window population.", "mechanism": ["cround.slot0.population"], "blocksClaim": False},
            {"id": "res-semantics", "statement": "Field meanings, source spelling, and direct rebuild parity remain unresolved.", "mechanism": ["cround.slot0.semantic_mapping"], "blocksClaim": False},
        ],
        "poisonControl": {"id": "control-wrong-path-and-count-predictions", "kind": "poison", "description": "wrong return-marker, adjacent-callee, and exact-count predictions plus an analytically contradictory machine pass", "predictedOutcome": "incorrect or contradictory runs remain ineligible for positive admission", "observedOutcome": "all four remained excluded; a fresh corrected Level-512 replay was required", "result": "failed_as_predicted"},
        "overturnedBy": [
            {"id": "kill-independent-reparse", "procedure": "independently parse an accepted exact JSONL and obtain a different pair count, receiver-relative offset, raw value, order, or writer PC", "wouldShow": "the saved bounded receiver-write sequence is wrong", "cost": "one independent JSONL parser"},
            {"id": "kill-independent-replay", "procedure": "replay a hash-pinned selected window with an independent collector and obtain a path or write sequence inconsistent with the saved projection", "wouldShow": "the collector projection is not faithful", "cost": "one retained-trace replay"},
        ],
        "subject": subject,
    }
    require(saved.get("claimBoundary") == EXPECTED_BOUNDARY, "finding proof boundary differs")
    out.parent.mkdir(parents=True, exist_ok=True)
    require(not out.exists(), f"refusing existing finding: {out}")
    out.write_text(json.dumps(finding, indent=2) + "\n", encoding="utf-8")
    return out


def evidence_ref(adjudication: Path, artifact: Path, role: str) -> dict[str, Any]:
    return {"role": role, "path": os.path.relpath(artifact.resolve(), adjudication.parent.resolve()).replace("\\", "/"), "sha256": sha256_file(artifact)}


def build_adjudication(campaign: Path, overlay: Path, finding: Path, result: Path, out: Path) -> Path:
    refuter = read_json(result)
    require(refuter.get("tool") == "tools/probe/refute.py" and refuter.get("verdict") == "SURVIVED", "refuter did not survive")
    require(refuter.get("subject") == overlay_subject(overlay), "refuter subject differs")
    value = {
        "schema": ADJUDICATION_SCHEMA,
        "baseCampaignReadySha256": sha256_file(campaign / "campaign.ready.json"),
        "overlayReadySha256": sha256_file(overlay / "runtime-contracts.ready.json"),
        "decision": {
            "baseContractId": CONTRACT_ID, "questionIdsAddressed": [QUESTION_ID], "refuterVerdict": "SURVIVED",
            "refuterEvidence": [evidence_ref(out, finding, "refuter-finding"), evidence_ref(out, result, "refuter-result")],
            "terminalState": "", "measuredAtUtc": datetime.now(timezone.utc).isoformat(),
            "remainingUncertainty": "Five selected arm paths and exact receiver-write sequences are bounded by per-window grade; external writes/effects, event 2000, event 4002, CMissile placement, field semantics, broader states, source spelling, and direct rebuild parity remain open.",
            "nextQuestions": [
                {"questionType": "CROUND_HANDLEEVENT_EXTERNAL_ARM_EFFECTS", "question": "Which allocation, container, event-manager, and other external writes/effects occur around the five bounded selected arm invocations?", "recommendedInstrument": "TTD_CALLEE_SCOPED_EXTERNAL_WRITE_DISCOVERY_THEN_EXACT_WATCHES", "cheapestFalsifier": "Watch the first external state roots reached by each selected path and find one preregistered external transition.", "requiresElevation": False, "priority": 1, "score": 700.0, "source": "CRound slot-0 arm-effects Gen23 adjudication", "currentOwner": "recursive-re-campaign"},
                {"questionType": "CROUND_HANDLEEVENT_EVENT2000_ARM_EFFECTS", "question": "What exact receiver and external state transitions occur in the observed default-routed event-2000 population?", "recommendedInstrument": "TTD_PRESELECTED_EVENT2000_BRANCH_AND_DATA_WRITE_ENVELOPE", "cheapestFalsifier": "Bind one hash-pinned event-2000 invocation to its receiver writes and exact return grade.", "requiresElevation": False, "priority": 2, "score": 650.0, "source": "CRound slot-0 arm-effects Gen23 adjudication", "currentOwner": "recursive-re-campaign"},
            ],
            "rebuildMapping": {"rebuildOwner": "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs", "rebuildImplementation": "Level100ActorMechanics.AdvanceActorRounds (nearest partial owner; no explicit retail event queue)", "parityTests": "Level100ActorWeaponTests.ActorArmament_IsCanonicalReplayState (nearest partial state test; no arm-effects parity test)", "rebuildState": "PARTIAL_CONTRACT"},
            "supersessions": [],
        },
    }
    require(not out.exists(), f"refusing existing adjudication: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=repository_root())
    parser.add_argument("--campaign", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build"); build_parser.add_argument("--out", type=Path, required=True)
    verify_parser = commands.add_parser("verify"); verify_parser.add_argument("--proof", type=Path, required=True)
    commands.add_parser("selftest")
    overlay_parser = commands.add_parser("overlay"); overlay_parser.add_argument("--proof", type=Path, required=True); overlay_parser.add_argument("--out", type=Path, required=True)
    finding_parser = commands.add_parser("finding"); finding_parser.add_argument("--proof", type=Path, required=True); finding_parser.add_argument("--overlay", type=Path, required=True); finding_parser.add_argument("--out", type=Path, required=True)
    adjudication_parser = commands.add_parser("adjudication"); adjudication_parser.add_argument("--overlay", type=Path, required=True); adjudication_parser.add_argument("--finding", type=Path, required=True); adjudication_parser.add_argument("--result", type=Path, required=True); adjudication_parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    campaign = (args.campaign or root / CAMPAIGN_RELATIVE).resolve()
    try:
        if args.command == "build":
            path = build(root, campaign, args.out); print(f"CROUND_ARM_EFFECTS_PROOF_READY {stamp(path)}")
        elif args.command == "verify":
            value = verify(root, campaign, args.proof.resolve()); print(f"CROUND_ARM_EFFECTS_PROOF_VERIFIED verdict={value['verdict']} pairs=84")
        elif args.command == "selftest":
            value = selftest(root, campaign); print(f"CROUND_ARM_EFFECTS_SELFTEST_OK attacks={value['count']}")
        elif args.command == "overlay":
            path = build_overlay(root, campaign, args.proof.resolve(), args.out.resolve()); print(f"CROUND_ARM_EFFECTS_OVERLAY_READY {stamp(path)}")
        elif args.command == "finding":
            path = build_finding(root, args.proof.resolve(), args.overlay.resolve(), args.out.resolve()); print(f"CROUND_ARM_EFFECTS_FINDING_READY {stamp(path)}")
        else:
            path = build_adjudication(campaign, args.overlay.resolve(), args.finding.resolve(), args.result.resolve(), args.out.resolve()); print(f"CROUND_ARM_EFFECTS_ADJUDICATION_READY {stamp(path)}")
        return 0
    except (ProofError, OSError, ValueError, KeyError) as exc:
        print(f"CROUND_ARM_EFFECTS_REFUSED: {exc}", file=os.sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
