#!/usr/bin/env python3
"""Hard-payload safety check for the public-primary repo.

The public repository is now the working repository. Raw RE notes, scratch
exports, state docs, and proof reports are allowed. This check only rejects
actual copied game/runtime payload roots, build outputs, and obvious secret
files. It is intentionally not a portable-app ZIP manifest and should not reject
compact non-secret state batons, agent reports, `.codex` project history, or
readiness summaries merely because a portable/export profile excludes them from
the packaged artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
SELF_REL = "tools/public_allowlist_safety_check.py"

DENY_ROOTS = (
    ".vs/",
    "GameProfiles/",
    "Ghidra/",
    "PatchBench/",
    "game/",
    "ghidra-local/",
    "local-game/",
    "local-ghidra/",
    "local-lab/",
    "local-media/",
    "local-rom-input/",
    "local-proofs/",
    "local-saves/",
    "mcps/",
    "media/",
    "save-attempts/",
)

DENY_CONTAINS = (
    "/bin/",
    "/obj/",
    "/TestResults/",
    "/__pycache__/",
    ".rep/",
    "/.rep/",
    "/secrets/",
    "/credentials/",
    "/.codex/auth/",
    "/.codex/cache/",
    "/.codex/logs/",
    "/.codex/sessions/",
    "/.codex/tmp/",
)

DENY_EXACT = {
}

ALLOW_EXACT_SHA256 = {
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Textures/be-tex-a.texture.aya": "86f9f54ae97ba4e3782c65909d1d93b86566228b1132829ebb93816eb5a4705b",
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Textures/be-tex-b.texture.aya": "ea01431a4023abd517daf5a27066eb7edf706100fb3991566726fb4530490b60",
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Textures/bluegun-light.texture.aya": "85858e7809a974b74f3db5a169e081fc9dd506558f1ca99fa47c7832d8552fc5",
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Textures/cockpit.texture.aya": "c62d0c668226f056db7455c8a5a8fa7d55ab7621ade1e58392d6aaad3c00f0cc",
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Source/m_cockpit2.msh.aya": "008b9292c59a5564ba3696f65d5bd51030d3e57250bc792d9d2b7f01292cdd4a",
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Source/m_f_be1.msh.aya": "d4c8fa752229af4111b31efa5ff5928c892736faa6a807915412767f3cd3c6b2",
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Source/m_f_be2.msh.aya": "35aada1313c3cbb796ba75db071321035f7005096da7c148a7514944f4772b4c",
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/aquila-jet.obj": "92a3495e278884b63649e114eddb7373b04af2aa92aab25c3f7184dd1140d821",
    "rebuild/OnslaughtRebuild.Godot/Assets/Aquila/aquila-walker-cockpit.obj": "0e81a2b48ab2202620b3c0dccd08fe2ffbd76b5d668318d21f0ff72551dd5bd9",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/bar-line.texture.aya": "16796e3a8acfec3529e03c29afbefbe28c92ffccd5b05574f992e8f31976704d",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/battleline-outline.texture.aya": "b1c097b29dd81e2a0493f72a157ccd5ad249b5abf758224c75df4f93973d0405",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/circle-darkener.texture.aya": "7bd18594757165dcdd8dadb618ea99eb500ed105dbe2d6a6f66bbcbc31c323a3",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/circle-mask.texture.aya": "14d809f9b45f5153f82fa1f80152690b554710d83f91b8cbe203de5cf18a9dfa",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/compass-objective-marker.texture.aya": "e24fca83de34646a7328c313e7b89ac02c6bc4b04a69a74bf3ee81b3d57283df",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/crosshair-dot.texture.aya": "19e1b35b885a36230e5a1d47a9910164b0ca177746649a15c146cefca29651dd",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/crosshair-primary.texture.aya": "310dae2f7dd976f6cc724604737726885aff96ab6bc507e41f90dca60d134b17",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/crosshair-secondary.texture.aya": "7b078344e64d1e78ef64a8e21bdd3787e059b628c6a442634e9d13ba7d3a0487",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/font-13ps.texture.aya": "7acc088b75e729cbdc2782e239a7d18ba0ec409e1bc890109aa1020f5ee81dc0",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/message-noise.texture.aya": "f5c43c330394db9eb7c1e782f3f30fe847de01d7ce9335d2c7f9fd24babb1825",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/objective-inner-centre.texture.aya": "fc42774e8c4f4534b65009807bfdb333443a9f5202c6a2c59dff0dddbed4f55b",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/objective-inner-left.texture.aya": "70030aace505e8e3d7f56dde0b9c6a929f3d2c61912fc03ac816746b6d8a96bd",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/objective-inner-right.texture.aya": "7c85b0293fc7a524978a21e7cdc06b1dd3308e9a595aadca054b51cd9a6aa113",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/objective-left.texture.aya": "0ae835780d1af6c01f0272a50afda141abca70eaa5c23d74e7fc3968b6d9194f",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/objective-right.texture.aya": "581f10446db76ece7aa7044b4c02f0431a79a7d606225d5c69a412c17f85078b",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/radar-outline.texture.aya": "507d465248f7321f2332413b2c6f461f3b3c45d87c52d86c38c43104043d7dc7",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/radio-north.texture.aya": "e5dfd8db4dd73e9aeeffbb009fca68d889572c996987bce365b0b5b4d0a7ed85",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/radio-view.texture.aya": "888d5a70ab812e23f75db76ab2ed71cd2cce04191ee282d525c86e337cc01778",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/scanner-blob-small.texture.aya": "d7e9d287536f23e67bf35f678ec75d1a349353ae1d9d00b87ce09f6bd03641e4",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/tatiana-portrait.texture.aya": "34d451a6fc31e399b99032230413a60f146b41a0fea65e61561a37d8ec757cfd",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/technician-portrait.texture.aya": "c4c1b11f4ddfb960afc1c1d2a04020fadf997795eccf651c07314141652f9603",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/weapon-fill.texture.aya": "e639910d70ae10b044423cd5025c300c61cb8a9b5765890fd1a011c7d4499c0d",
    "rebuild/OnslaughtRebuild.Godot/Assets/Hud/weapon-outline.texture.aya": "2e2da786db82c8fd76de36d8d71fe744ddddd364247467cba1bfb9a95e52d62b",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Sky/cube25-cent.texture.aya": "1aad6cc8f85b6bb7ccbb8d2c7b0e6aa31722a9adbde5a3f19b248430ca83469e",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Sky/cube25-down.texture.aya": "4770829ba631e93fbc33db2012754da75a06bfccc2fb2b36875e92032e22d19d",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Sky/cube25-left.texture.aya": "d7cbce30e51473ddc89ed0c44326e598dac4d2682f64ef20c19237afd2cebe14",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Sky/cube25-right.texture.aya": "830c9b965c76a4023c2415b7c8924ca32590562c850cc84e92c003e173263d11",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Sky/cube25-up.texture.aya": "419e2424bcfd698058d72111ffa7d84fdc9022e03815db7c0da28403f4925f3c",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/SoundEffects/pulse-cannon-fire.wav": "710ff06db55bc694efb8ff7d3a5ab658125e7ca0fe6b4733a805da98b22b0277",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/SoundEffects/pulse-impact-small.wav": "3296b13938928f54847a29e17307e7875e9933f8fd6381bf0dfcd260cd6fc131",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/SoundEffects/target-tank-explosion-medium.wav": "7228ae049cb0a9877e63671a65e51829443017b2c4981df90a9c64d2f38b6d9c",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/effect-flash-medium.texture.aya": "d7fbfcb4edb2167fedc0a467d4501c9bbc2f6a2852c7873daec3953e6f518f5c",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/facility-hanger-bits.texture.aya": "8e73098eaeb3c961b7cd63c3fbdf2338b22efbe191bf956034db9a69e71c041a",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/facility-hanger-more-bits-lit.texture.aya": "f04b96e9e2a121f74729f63194b01fac58384b150f476b5e03d17b03b6dcc6e3",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/facility-hanger-top-01.texture.aya": "54adeb37d60fbc8209dbb75eb61fd39898b3f07e808e05c408dc740ff4647fd4",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/facility-hanger-top-02.texture.aya": "e09455015cc79439aa33c5fb6b4a70b75de9f2d5392aa7cd08bbf42d8fc6f78f",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/facility-health-pad.texture.aya": "4cb425f9ead9aeea065f73b69f5bb1dd0f659522a6b656e69c3f3ae0325a2543",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/mech-pulse-medium-energy-trail.texture.aya": "64eddc6b147c67886f41ef4d2bcc2a0606b453b01e4d93b9962f10cc07aba92e",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/mech-pulse-medium-halo.texture.aya": "cde6efc90dc7958c5bda425a04486e277beb85a7f1c33fb9074f369e92d58edb",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/pulse-bolt-blue-spark.texture.aya": "b3730b1e9d7713910e0de4bd0cb0dcfefcb9ceb8f6402d50681a524adc0dcb08",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/pulse-bolt-blue-trail.texture.aya": "2b4bc5cf8902d7ea8452f1068ac8f11514c8238a733ca33aad7d6d0667688a63",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/pulse-impact-animated-blob.texture.aya": "74085b280199e20b765640cfc3e417e6da0fcbfb25384e129858a32f5deb995d",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/pulse-impact-shockwave.texture.aya": "e92efc3f5adfa347e6b50f1e3d20af4c6800d76853a2126d71237dfefeea9f10",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/target-tank.texture.aya": "97ddd1e18e45b19e249e91e881d773d80d36768a2cd48f6549a769c2559a7b7e",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/target-tank-explosion-animated.texture.aya": "3c8fc30ad4923c56c3735caab5661a3f176eb661eaa678093870f51de4204c9e",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/target-tank-explosion-fireball.texture.aya": "e6c166669e351632a90b41c74782967923c78fc8be644a1e8948d356806b23ed",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/target-warehouse-m001.texture.aya": "689b184ab8a5d03f33b69e5c35edcfdfdec12aa9b4b31f7c74ce5209f6236a49",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/target-warehouse-m002.texture.aya": "8fabadbe1c5af067a740cf05debd1c952c628fd5fa3ea92b8202094704b8a20d",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/terrain-detail-00.texture.aya": "7c9c22169d13ed8b7d6ad69286bdb59cc88f9ae3bfb6a9d3a0503d320386bfef",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/turret-blaster-primary.texture.aya": "8eefb3a268f1e54b9db83e92d9a64bf5d800631a04a87c1c141080f9791f28f3",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/turret-pulse-primary.texture.aya": "ccf2896ad3991755c4f5a8330fe16b89e9c6d719537c4f72ff4805ff176c3ece",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Textures/turret-sam-shared.texture.aya": "a1fe2d7531676d38e874c48819aca69ed62955886f2efe9ad0046d85d1cb18fc",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source/m_fb_health_pad.msh.aya": "4ec6cb1d589c866acfa292232ca4f850967faea899c2f082329bff78e647ab44",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source/m_fb_research.msh.aya": "37ff4fb289e28d1be5b0421bfe0f4b659694166152c4af874d230e767002f0f1",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source/m_f_pulsetank_training.msh.aya": "9b2cfdceb86ed700ed924051fbff13c32dc30bd8f8b948ea1cf8aa9fbfe8b97b",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source/m_fb_control_tower.msh.aya": "86af67e09dc2fd21c7023acd53ebcb4171f3bf396f836da85ecfdda516588d91",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source/m_fb_tank_factory.msh.aya": "a507afda7b5c6b6b8bed275d442a53b28043bb9d5b65f9ea5bd6f5ff754bf6de",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source/m_m_warehouse.msh.aya": "61fe5465bd7affedf749ad784209be02b2e4dd28631e70386c3810302b5f6f15",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source/m_ft_blaster.msh.aya": "9833cd459e00b1c2068f9db6be34ee0e6a3f2d0b01d780946a338d5682abb4cb",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source/m_ft_pulse.msh.aya": "1cc399936cdd171c44297dcbc6ef2ff2e187319de707d0f4c564e338a9770b9c",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source/m_ft_sam.msh.aya": "9a82f27454863c19c05a8cdedcc99cc05300aed75b8e54467a980c94bf5ba4a2",
    "rebuild/OnslaughtRebuild.Core/Assets/Level100/level100-heightfield.hfld.bin": "7a4c7c5b9400e2c8d2325cecb5c44701cd8a6e6f8609cbc8bc31d449c0620f5d",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/level100-control-tower.obj": "9a2b9c287bff21dd7e3b560ee36cc7d7cafb99399b3003bf2e81a832fbd6f6ba",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/level100-blaster-turret.obj": "2498f1d19fbe3afb3520a1b8316e00e381566b4b710abb923468125848f17df9",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/level100-health-pad.obj": "ae988ed04713970174340d891580b11b6d8005ac7dc2e6b53289468a0b3cca31",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/level100-pulse-turret.obj": "2c0c3eeee9b13fba7f32f8751920d4eb1dc2ebaa8301520ce74c0637d886ef68",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/level100-research-building.obj": "ae989a8dbc9a2c7897e92e07b23a14d9b8908430bdb549eb6d43dd20a11a4394",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/level100-sat-turret.obj": "a91921220b71255da098a0c578d320e7c2632dc3b9b74c8ff27b464cb74acc60",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/level100-tank-factory.obj": "895813a6d8fd6938934957e934f23b58ec5c059e6ce8f8f9472bc4438b49d53c",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/level100-target-tank.obj": "6d3827b58fe7a4728efe1efc6a7ced7a08a0b642891dcb1f18377a4b3d61d244",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/level100-target-warehouse.obj": "271adefedcb0942a584014ff51fc7330769ab8fd95bc6ea5987bac305c60f658",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/hud_01.ogg": "bae30243a2b5fe3dae718181ac5b05d766f93d5e25b042fe1b04c71fc9347909",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/hud_02.ogg": "43ae0c306b7935a21d415338348508eabf3a61f8799c0fd0873c89919fb84a35",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/hud_05.ogg": "66256d87557946647a51a2e8d49e044bc55ae370c4ad1c8e950b1d884ec082eb",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/hud_06.ogg": "4ed80a12fa7d2ad07a044f95f94d52455413962b75e7689101df6907711f3235",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/tutorial_01.ogg": "48e40b07a77b5776f817ed8d8ffe1eff1a978b10480cab92019077e7b66784a8",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/tutorial_02.ogg": "fa0533de72b8d7702b83b709ba631bc8f7a42a5183babcb147ae653a5d7a2904",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/tutorial_03.ogg": "8e3bbd3f680099f7664f473f73837bf3e6d09474b4426677dd6bf27b31177dc2",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/tutorial_13_mod.ogg": "7eee9087f86c00abe4feab115b20e4e2f27a8e6d1adc7318b1602446a7493e65",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/tutorial_message_log.ogg": "7a03ff8f3faa4be4b729e7619055379c62921e2eaeb67fc9711dac0dfe273f8b",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/tutorial_open_fire.ogg": "04a1a65b45f75f4d1e85b0fab6970125584efbabe3609d7413e60b569a26d20c",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/tutorial_pulse_cannon.ogg": "2fda4a38b4737e03647c03bac38bfb36e7e6ff16b279007c04616c23857c25f8",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/tutorial_pulse_cannon_2.ogg": "f4eca49f26f61f0369c0d8b770300596695f8a62ec12269a4c9d1cb3f61b13e0",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/tutorial_scanner.ogg": "7a9535b1187b6e1ff276cebc3906ec2102e5d166f381ee674113b4f09c2b3bd2",
    "rebuild/OnslaughtRebuild.Godot/Assets/Level100/TutorialAudio/tutorial_technician_01.ogg": "4792371453b4402454b922a481eb0968a099efb13981ff1918aa6177fb6ae151",
    "references/AYAResourceExtractor/BoxWithTextures.fbx": "37526ffde1d48016fa8a2a05c5dfeb3cd0a30a8ab402ccce60a7f44addf8eed2",
    "tests_shared/fixtures/gold_career_save.bin": "0c17e47db9d666e9b26ef88d43d0a25e7cbfbf4f88c8005cc748965050e506fb",
}

ALLOW_EXACT = set(ALLOW_EXACT_SHA256)

REVIEWED_GHIDRA_ROOT = "reverse-engineering/ghidra/"
REVIEWED_GHIDRA_SUFFIXES = {".bak", ".dat", ".gbf", ".prp"}

ALLOW_CDB_SCRIPT_PREFIXES: tuple[str, ...] = ()

DENY_SUFFIXES = (
    ".7z",
    ".aac",
    ".appx",
    ".appxbundle",
    ".avi",
    ".aya",
    ".bak",
    ".bea",
    ".bes",
    ".bik",
    ".bmp",
    ".bytes",
    ".cab",
    ".cue",
    ".crt",
    ".dat",
    ".db",
    ".dds",
    ".dll",
    ".dmp",
    ".etl",
    ".exe",
    ".fbx",
    ".flac",
    ".gbf",
    ".gdt",
    ".gpr",
    ".gif",
    ".gz",
    ".gzf",
    ".html",
    ".htm",
    ".img",
    ".iso",
    ".jpeg",
    ".jpg",
    ".key",
    ".log",
    ".mso",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".msi",
    ".msix",
    ".msixbundle",
    ".ogg",
    ".pem",
    ".pfx",
    ".pdf",
    ".pdb",
    ".png",
    ".pyo",
    ".pyc",
    ".raw",
    ".rar",
    ".sav",
    ".sqlite",
    ".tar",
    ".tga",
    ".trx",
    ".vid",
    ".wav",
    ".webp",
    ".wma",
    ".xml",
    ".zip",
)

MAX_UNREVIEWED_FILE_BYTES = 5 * 1024 * 1024
MAGIC_SCAN_BYTES = 4096

TEXT_SUFFIXES = {
    ".cmd",
    ".cs",
    ".css",
    ".html",
    ".java",
    ".json",
    ".jsonl",
    ".jsonc",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".ts",
    ".tsx",
    ".tsv",
    ".txt",
    ".xml",
    ".xaml",
    ".yml",
    ".yaml",
}

TEXT_DENY_PATTERNS = (
    ("deny-private-key-block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("deny-openai-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("deny-github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("deny-github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b")),
    ("deny-aws-access-key", re.compile(r"\bA(?:KIA|SIA)[A-Z0-9]{16}\b")),
    ("deny-stripe-key", re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{20,}\b")),
    ("deny-cloudflare-token", re.compile(r"\b(?:CF_API_TOKEN|CLOUDFLARE_API_TOKEN)\s*[:=]\s*[A-Za-z0-9_-]{20,}\b")),
    ("deny-huggingface-token", re.compile(r"\bhf_[A-Za-z0-9]{20,}\b")),
    ("deny-sentry-dsn", re.compile(r"https://[A-Fa-f0-9]{16,}@[A-Za-z0-9.-]+/\d+")),
    ("deny-npm-token", re.compile(r"\bnpm_[A-Za-z0-9]{20,}\b")),
    ("deny-supabase-jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b")),
    ("deny-discord-token", re.compile(r"\b(?:mfa\.)?[A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,}\b")),
)

TEXT_ALLOW_EXACT = {
    "tools/public_allowlist_safety_check.py",
}

PAYLOAD_TEXT_ALLOW_EXACT: set[str] = set()

CDB_PROMPT_RE = re.compile(r"(?m)^\s*\d+:\d+>\s+")
REGISTER_DUMP_RE = re.compile(
    r"(?im)\b(?:eax|ebx|ecx|edx|esi|edi|eip|esp|rax|rbx|rcx|rdx|rsi|rdi|rip|rsp)=[0-9a-f`]{4,}\b"
)
STACK_TRACE_RE = re.compile(r"(?im)^\s*(?:ChildEBP|Child-SP|RetAddr)\s+")
DATA_IMAGE_RE = re.compile(r"data:image/(?:png|jpeg|jpg|gif|webp|bmp);base64,", re.IGNORECASE)
EMBEDDED_PNG_RE = re.compile(r"(?:\\x89PNG|iVBORw0KGgo)", re.IGNORECASE)
EMBEDDED_JPEG_RE = re.compile(r"(?:\\xff\\xd8\\xff|/9j/4AAQSkZJRgABAQ)", re.IGNORECASE)
BASE64_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/=]{512,}(?![A-Za-z0-9+/=])")

MAGIC_DENY_SIGNATURES = (
    ("deny-magic-executable", b"MZ"),
    ("deny-magic-zip-archive", b"PK\x03\x04"),
    ("deny-magic-7z-archive", b"7z\xbc\xaf\x27\x1c"),
    ("deny-magic-rar-archive", b"Rar!\x1a\x07"),
    ("deny-magic-msi-ole-package", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"),
    ("deny-magic-cab-archive", b"MSCF"),
    ("deny-magic-pdb-symbols", b"Microsoft C/C++"),
    ("deny-magic-png-image", b"\x89PNG\r\n\x1a\n"),
    ("deny-magic-jpeg-image", b"\xff\xd8\xff"),
    ("deny-magic-gif-image", b"GIF8"),
    ("deny-magic-webp-image", b"RIFF"),
    ("deny-magic-ogg-audio", b"OggS"),
    ("deny-magic-bink-video", b"BIK"),
    ("deny-magic-sqlite-db", b"SQLite format 3\x00"),
)

@dataclass(frozen=True)
class Finding:
    path: str
    label: str
    detail: str


def normalize(path: str) -> str:
    return path.replace("\\", "/")


def public_candidate_files(root: Path, *, include_submodules: bool = False) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git executable was not found for public candidate enumeration") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else str(exc.stderr)
        raise RuntimeError(f"git ls-files failed for public candidate enumeration: {stderr.strip()}") from exc
    paths = [
        path
        for item in result.stdout.decode("utf-8", errors="replace").split("\0")
        if (path := normalize(item)) and (root / path).exists()
    ]
    if include_submodules:
        paths.extend(submodule_candidate_files(root))
    return sorted(set(paths))


def payload_root_files(root: Path) -> list[str]:
    if not root.is_dir():
        raise RuntimeError(f"payload root is not a directory: {root}")

    paths: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError as exc:
            raise RuntimeError(f"payload root enumeration escaped root: {path}") from exc
        if relative.startswith(".git/"):
            continue
        paths.append(normalize(relative))
    return sorted(set(paths))


def submodule_paths(root: Path) -> list[str]:
    gitmodules = root / ".gitmodules"
    if not gitmodules.is_file():
        return []
    try:
        result = subprocess.run(
            ["git", "config", "--file", str(gitmodules), "--get-regexp", r"^submodule\..*\.path$"],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("git executable was not found for .gitmodules parsing") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f".gitmodules could not be parsed: {exc.stderr.strip()}") from exc
    paths: list[str] = []
    for line in result.stdout.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            paths.append(normalize(parts[1].strip()))
    return sorted(paths)


def submodule_candidate_files(root: Path) -> list[str]:
    paths: list[str] = []
    for submodule_path in submodule_paths(root):
        full_path = root / submodule_path
        if not full_path.is_dir():
            continue
        try:
            result = subprocess.run(
                ["git", "ls-files", "-z"],
                cwd=full_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(f"git executable was not found while scanning submodule {submodule_path}") from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else str(exc.stderr)
            raise RuntimeError(f"submodule {submodule_path} could not be scanned: {stderr.strip()}") from exc
        for item in result.stdout.decode("utf-8", errors="replace").split("\0"):
            if not item:
                continue
            paths.append(f"{submodule_path}/{normalize(item)}")
    return sorted(paths)


def submodule_scan_findings(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        paths = submodule_paths(root)
    except RuntimeError as exc:
        return [Finding(".gitmodules", "deny-unreadable-submodule-map", str(exc))]
    for submodule_path in paths:
        full_path = root / submodule_path
        if not full_path.is_dir():
            findings.append(Finding(submodule_path, "deny-missing-submodule-scan", "declared submodule directory is absent"))
            continue
        try:
            subprocess.run(
                ["git", "ls-files", "-z"],
                cwd=full_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            findings.append(Finding(submodule_path, "deny-unreadable-submodule-scan", str(exc)))
    return findings


def is_text_file(path: str) -> bool:
    return Path(path).suffix.lower() in TEXT_SUFFIXES


def is_text_candidate(path: str) -> bool:
    """Compatibility helper used by release accounting scripts."""
    return is_text_file(path)


def is_reviewed_payload(path: str) -> bool:
    if path == f"{REVIEWED_GHIDRA_ROOT}BEA.gpr":
        return True
    if not path.startswith(f"{REVIEWED_GHIDRA_ROOT}BEA.rep/"):
        return False
    return Path(path).suffix.lower() in REVIEWED_GHIDRA_SUFFIXES or Path(path).name == "projectState"


def path_findings(path: str) -> list[Finding]:
    if path in ALLOW_EXACT or is_reviewed_payload(path):
        return []
    findings: list[Finding] = []
    lower = path.lower()
    name = Path(path).name.lower()
    if lower.startswith(".codex/"):
        findings.append(Finding(path, "deny-codex-runtime-subtree", path))
    if path in DENY_EXACT:
        findings.append(Finding(path, "deny-exact", path))
    if name == ".env" or name.startswith(".env."):
        findings.append(Finding(path, "deny-env-file", name))
    if lower.startswith(tuple(prefix.lower() for prefix in DENY_ROOTS)):
        findings.append(Finding(path, "deny-root", path.split("/", 1)[0]))
    if any(token.lower() in lower for token in DENY_CONTAINS):
        findings.append(Finding(path, "deny-generated-or-private-path", path))
    if lower.endswith(".cdb.txt") and not any(lower.startswith(prefix.lower()) for prefix in ALLOW_CDB_SCRIPT_PREFIXES):
        findings.append(Finding(path, "deny-raw-cdb-text-transcript", ".cdb.txt"))
    if lower.endswith(".txt") and "cdb" in name and "log" in name:
        findings.append(Finding(path, "deny-raw-cdb-text-transcript", name))
    if lower.endswith(DENY_SUFFIXES):
        findings.append(Finding(path, "deny-binary-or-private-suffix", Path(path).suffix.lower()))
    return findings


def size_findings(root: Path, path: str) -> list[Finding]:
    full_path = root / path
    if full_path.is_dir():
        return []
    try:
        size = full_path.stat().st_size
    except OSError as exc:
        return [Finding(path, "stat-error", str(exc))]
    if path in ALLOW_EXACT_SHA256 or is_reviewed_payload(path):
        return []
    if size > MAX_UNREVIEWED_FILE_BYTES:
        return [Finding(path, "deny-large-unreviewed-file", str(size))]
    return []


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def exact_allow_hash_findings(root: Path, path: str) -> list[Finding]:
    expected = ALLOW_EXACT_SHA256.get(path)
    if expected is None:
        return []
    full_path = root / path
    try:
        actual = sha256_file(full_path)
    except OSError as exc:
        return [Finding(path, "exact-allow-hash-read-error", str(exc))]
    if actual.lower() != expected.lower():
        return [Finding(path, "exact-allow-hash-mismatch", actual)]
    return []


def magic_findings(root: Path, path: str) -> list[Finding]:
    if path in ALLOW_EXACT_SHA256 or is_text_file(path) or is_reviewed_payload(path):
        return []
    full_path = root / path
    if full_path.is_dir():
        return []
    try:
        prefix = full_path.read_bytes()[:MAGIC_SCAN_BYTES]
    except OSError as exc:
        return [Finding(path, "read-error", str(exc))]
    findings: list[Finding] = []
    for label, signature in MAGIC_DENY_SIGNATURES:
        offset = prefix.find(signature)
        if offset >= 0:
            if label == "deny-magic-webp-image" and (len(prefix) < offset + 12 or prefix[offset + 8 : offset + 12] != b"WEBP"):
                findings.append(Finding(path, "deny-magic-riff-media", "RIFF"))
            else:
                findings.append(Finding(path, label, f"offset={offset} signature={signature.hex()}"))
            break
    return findings


def text_binary_findings(root: Path, path: str) -> list[Finding]:
    if path == SELF_REL or path in TEXT_ALLOW_EXACT or not is_text_file(path):
        return []
    full_path = root / path
    try:
        prefix = full_path.read_bytes()[:MAGIC_SCAN_BYTES]
    except OSError as exc:
        return [Finding(path, "read-error", str(exc))]
    if b"\x00" in prefix:
        return [Finding(path, "deny-nul-byte-in-text-file", "NUL byte")]
    control_count = sum(1 for byte in prefix if byte < 32 and byte not in {9, 10, 13})
    if prefix and control_count / len(prefix) > 0.05:
        return [Finding(path, "deny-control-byte-heavy-text-file", f"{control_count}/{len(prefix)}")]
    return []


def content_signature_findings(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    if path in PAYLOAD_TEXT_ALLOW_EXACT:
        return findings
    cdb_prompt_count = len(CDB_PROMPT_RE.findall(text))
    register_count = len(REGISTER_DUMP_RE.findall(text))
    stack_trace_count = len(STACK_TRACE_RE.findall(text))
    if cdb_prompt_count >= 3 or (cdb_prompt_count >= 1 and (register_count >= 4 or stack_trace_count >= 1)):
        findings.append(
            Finding(
                path,
                "deny-raw-debugger-transcript-content",
                f"cdbPrompts={cdb_prompt_count} registerRows={register_count} stackRows={stack_trace_count}",
            )
        )
    if DATA_IMAGE_RE.search(text):
        findings.append(Finding(path, "deny-data-image-url", "data:image/*;base64"))
    if EMBEDDED_PNG_RE.search(text):
        findings.append(Finding(path, "deny-embedded-png-header", "png header/base64 marker"))
    if EMBEDDED_JPEG_RE.search(text):
        findings.append(Finding(path, "deny-embedded-jpeg-header", "jpeg header/base64 marker"))
    for match in BASE64_TOKEN_RE.finditer(text):
        token = match.group(0)
        if "0x" in token.lower():
            continue
        if "+" not in token and "/" not in token and "=" not in token:
            continue
        snippet = token[:117] + "..." if len(token) > 120 else token
        findings.append(Finding(path, "deny-large-base64-blob", snippet))
        break
    return findings


def text_findings(root: Path, path: str) -> list[Finding]:
    if path == SELF_REL or path in TEXT_ALLOW_EXACT:
        return []
    if not is_text_file(path):
        return []
    full_path = root / path
    try:
        text = full_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [Finding(path, "read-error", str(exc))]

    findings: list[Finding] = []
    for label, pattern in TEXT_DENY_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = match.group(0).replace("\n", "\\n")
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            findings.append(Finding(path, label, snippet))
    findings.extend(content_signature_findings(path, text))
    return findings


def find_text_payload_errors(path: str, text: str, require_private_text_guard: bool = False) -> list[str]:
    """Compatibility helper used by release accounting scripts."""
    if path == SELF_REL or path in TEXT_ALLOW_EXACT:
        return []
    if not is_text_candidate(path):
        return []

    errors: list[str] = []
    for label, pattern in TEXT_DENY_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = match.group(0).replace("\n", "\\n")
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            errors.append(f"{label} in {path}: {snippet}")
    for finding in content_signature_findings(path, text):
        errors.append(f"{finding.label} in {path}: {finding.detail}")
    return errors


def check_repo(root: Path, *, include_submodules: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    try:
        paths = public_candidate_files(root, include_submodules=include_submodules)
    except RuntimeError as exc:
        return [Finding(".", "deny-public-candidate-enumeration-failed", str(exc))]
    if not paths:
        return [Finding(".", "deny-empty-public-candidate-set", "git candidate enumeration returned zero files")]
    if include_submodules:
        findings.extend(submodule_scan_findings(root))
    for path in paths:
        findings.extend(path_findings(path))
        findings.extend(exact_allow_hash_findings(root, path))
        findings.extend(size_findings(root, path))
        findings.extend(magic_findings(root, path))
        findings.extend(text_binary_findings(root, path))
        findings.extend(text_findings(root, path))
    return findings


def check_payload_root(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        paths = payload_root_files(root)
    except RuntimeError as exc:
        return [Finding(".", "deny-public-candidate-enumeration-failed", str(exc))]
    if not paths:
        return [Finding(".", "deny-empty-public-candidate-set", "payload-root enumeration returned zero files")]
    for path in paths:
        findings.extend(path_findings(path))
        findings.extend(exact_allow_hash_findings(root, path))
        findings.extend(size_findings(root, path))
        findings.extend(magic_findings(root, path))
        findings.extend(text_binary_findings(root, path))
        findings.extend(text_findings(root, path))
    return findings


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        openai_fixture = "sk" + "-" + "not-a-real-fixture-value"
        generic_secret_fixture = "sk" + "-" + "thisfixturehasenoughcharacters000000"
        github_fixture = "ghp" + "_" + "thisfixturehasenoughcharacters000000"
        stripe_fixture = "sk" + "_" + "live" + "_" + "thisfixturehasenoughcharacters000000"
        hf_fixture = "hf" + "_" + "thisfixturehasenoughcharacters000000"
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        (root / "game").mkdir()
        (root / "game" / "BEA.exe").write_bytes(b"not ok")
        (root / "media").mkdir()
        (root / "media" / "music.ogg").write_bytes(b"not ok")
        (root / "save-attempts").mkdir()
        (root / "save-attempts" / "slot.bes").write_bytes(b"not ok")
        (root / "local-rom-input").mkdir()
        (root / "local-rom-input" / "payload.txt").write_text("local-only payload root\n", encoding="utf-8")
        (root / "frame.webp").write_bytes(b"not ok")
        (root / "installer.msix").write_bytes(b"not ok")
        (root / "symbols.pdb").write_bytes(b"Microsoft C/C++ MSF 7.00\r\n\x1aDS\0\0\0")
        (root / "package.msi").write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1not ok")
        (root / "cabinet.cab").write_bytes(b"MSCFnot ok")
        (root / "archive.7z").write_bytes(b"not ok")
        (root / "slot.sav").write_bytes(b"not ok")
        (root / "manual.pdf").write_bytes(b"not ok")
        (root / "screenshot.png").write_bytes(b"\x89PNG\r\n\x1a\nnot ok")
        (root / "disguised-note.md").write_bytes(b"\x89PNG\r\n\x1a\nnot ok")
        (root / "padded-disguised-note.md").write_bytes((b"x" * 40) + b"\x89PNG\r\n\x1a\nnot ok")
        (root / "nul-note.md").write_bytes(b"text before\x00payload")
        (root / "manual.html").write_text("<html>not ok</html>\n", encoding="utf-8")
        (root / "manual.xml").write_text("<xml>not ok</xml>\n", encoding="utf-8")
        (root / "local.rep").mkdir()
        (root / "local.rep" / "project.db").write_bytes(b"not ok")
        canonical_ghidra = root / "reverse-engineering" / "ghidra" / "BEA.rep" / "idata"
        canonical_ghidra.mkdir(parents=True)
        (canonical_ghidra / "database.gbf").write_bytes(b"reviewed canonical database fixture")
        (root / "reverse-engineering" / "ghidra" / "BEA.exe").write_bytes(b"not reviewed")
        (root / ".codex" / "custom").mkdir(parents=True)
        (root / ".codex" / "custom" / "instructions.md").write_text("not public\n", encoding="utf-8")
        (root / ".codex" / "sessions").mkdir(parents=True)
        (root / ".codex" / "sessions" / "session.jsonl").write_text("not ok\n", encoding="utf-8")
        (root / "archive" / "electron-workbench" / "packages" / "ui").mkdir(parents=True)
        (root / "archive" / "electron-workbench" / "packages" / "ui" / "index.html").write_text("<div>allowed app shell</div>\n", encoding="utf-8")
        (root / "references" / "AYAResourceExtractor").mkdir(parents=True)
        (root / "references" / "AYAResourceExtractor" / "BoxWithTextures.fbx").write_bytes(b"allowed non-BEA extractor fixture")
        (root / "big.md").write_bytes(b"x" * (MAX_UNREVIEWED_FILE_BYTES + 1))
        (root / "tests_shared" / "fixtures").mkdir(parents=True)
        (root / "tests_shared" / "fixtures" / "gold_career_save.bin").write_bytes(b"allowed regression fixture")
        (root / ".env").write_text(f"OPENAI_API_KEY={openai_fixture}\n", encoding="utf-8")
        (root / "docs.md").write_text("Raw RE notes may mention local paths and field names.\n", encoding="utf-8")
        (root / "token-note.md").write_text(
            f"Accidental token example {generic_secret_fixture}\n",
            encoding="utf-8",
        )
        (root / "inline-image.md").write_text(
            "Accidental inline image data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB\n",
            encoding="utf-8",
        )
        (root / "blob-note.md").write_text(
            "Accidental blob " + ("A" * 260) + "/" + ("B" * 260) + "\n",
            encoding="utf-8",
        )
        (root / "raw-debugger-summary.md").write_text(
            "0:000> r\n"
            "eax=00000001 ebx=00000002 ecx=00000003 edx=00000004 esi=00000005 edi=00000006 eip=00401000 esp=0019ff00\n",
            encoding="utf-8",
        )
        (root / "raw-debugger-events.jsonl").write_text(
            '{"line":"0:000> r eax=00000001 ebx=00000002 ecx=00000003 edx=00000004 eip=00401000"}\n',
            encoding="utf-8",
        )
        (root / "subagents" / "runtime").mkdir(parents=True)
        (root / "subagents" / "runtime" / "raw-session.cdb.txt").write_text(
            "0:000> g\nraw debugger transcript fixture\n",
            encoding="utf-8",
        )
        (root / "release" / "readiness").mkdir(parents=True)
        (root / "release" / "readiness" / "session-cdb-log.txt").write_text(
            "raw cdb log fixture\n",
            encoding="utf-8",
        )
        (root / "tools" / "runtime-probes").mkdir(parents=True)
        (root / "tools" / "runtime-probes" / "allowed-observer.cdb.txt").write_text(
            ".echo command script fixture\nvertarget\ng\n",
            encoding="utf-8",
        )
        (root / "github-token-note.md").write_text(
            f"Accidental token example {github_fixture}\n",
            encoding="utf-8",
        )
        (root / "stripe-token-note.md").write_text(
            f"Accidental token example {stripe_fixture}\n",
            encoding="utf-8",
        )
        (root / "hf-token-note.md").write_text(
            f"Accidental token example {hf_fixture}\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        findings = check_repo(root)
        labels = {finding.label for finding in findings}
        required = {
            "deny-root",
            "deny-codex-runtime-subtree",
            "deny-generated-or-private-path",
            "deny-binary-or-private-suffix",
            "deny-env-file",
            "deny-large-unreviewed-file",
            "deny-magic-png-image",
            "deny-magic-pdb-symbols",
            "deny-magic-msi-ole-package",
            "deny-magic-cab-archive",
            "deny-nul-byte-in-text-file",
            "deny-data-image-url",
            "deny-embedded-png-header",
            "deny-raw-debugger-transcript-content",
            "exact-allow-hash-mismatch",
            "deny-openai-key",
            "deny-github-token",
            "deny-stripe-key",
            "deny-huggingface-token",
            "deny-raw-cdb-text-transcript",
        }
        missing = sorted(required - labels)
        if missing:
            print("Public payload safety self-test: FAIL")
            print(f"- missing expected labels: {', '.join(missing)}")
            print(f"- findings: {findings!r}")
            return 1
        if any(finding.path == "tests_shared/fixtures/gold_career_save.bin" for finding in findings):
            if not any(
                finding.path == "tests_shared/fixtures/gold_career_save.bin" and finding.label == "exact-allow-hash-mismatch"
                for finding in findings
            ):
                print("Public payload safety self-test: FAIL")
                print("- gold fixture exception was rejected for a reason other than hash mismatch")
                print(f"- findings: {findings!r}")
                return 1
        if any(finding.path == "references/AYAResourceExtractor/BoxWithTextures.fbx" for finding in findings):
            if not any(
                finding.path == "references/AYAResourceExtractor/BoxWithTextures.fbx"
                and finding.label == "exact-allow-hash-mismatch"
                for finding in findings
            ):
                print("Public payload safety self-test: FAIL")
                print("- AYAResourceExtractor fixture fbx was rejected for a reason other than hash mismatch")
                print(f"- findings: {findings!r}")
                return 1
        if not any(finding.path == "tools/runtime-probes/allowed-observer.cdb.txt" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- tracked CDB command scripts were not rejected")
            print(f"- findings: {findings!r}")
            return 1
        canonical_findings = [
            finding
            for finding in findings
            if finding.path.startswith("reverse-engineering/ghidra/")
            and finding.path != "reverse-engineering/ghidra/BEA.exe"
        ]
        if canonical_findings:
            print("Public payload safety self-test: FAIL")
            print("- canonical Ghidra project owner was rejected")
            print(f"- findings: {findings!r}")
            return 1
        if not any(finding.path == "reverse-engineering/ghidra/BEA.exe" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- standalone executable inside the Ghidra owner was not rejected")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        (root / "Game").mkdir()
        (root / "Game" / "payload.txt").write_text("case variant root\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        findings = check_repo(root)
        if not any(finding.label == "deny-root" and finding.path == "Game/payload.txt" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- case-variant game root was not rejected")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        non_repo = Path(tmp)
        findings = check_repo(non_repo)
        if not any(finding.label == "deny-public-candidate-enumeration-failed" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- non-git root did not fail closed")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        payload_root = Path(tmp)
        (payload_root / "README.MD").write_text("# OK\n", encoding="utf-8")
        (payload_root / "game").mkdir()
        (payload_root / "game" / "BEA.exe").write_bytes(b"not ok")
        findings = check_payload_root(payload_root)
        if not any(finding.label == "deny-root" and finding.path == "game/BEA.exe" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- payload-root mode did not reject game root")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / ".gitmodules").write_text("[submodule \"broken\"\n\tpath = broken\n", encoding="utf-8")
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        findings = check_repo(root, include_submodules=True)
        if not any(finding.label == "deny-public-candidate-enumeration-failed" for finding in findings):
            print("Public payload safety self-test: FAIL")
            print("- malformed .gitmodules did not fail closed")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / ".gitmodules").write_text(
            '[submodule "missing"]\n\tpath = references/missing\n\turl = ../missing.git\n',
            encoding="utf-8",
        )
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        findings = check_repo(root, include_submodules=True)
        if not any(
            finding.label == "deny-missing-submodule-scan"
            and finding.path == "references/missing"
            for finding in findings
        ):
            print("Public payload safety self-test: FAIL")
            print("- missing declared submodule did not fail closed")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        submodule = root / "references" / "payload-fixture"
        submodule.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=submodule, check=True)
        (submodule / "game").mkdir()
        (submodule / "game" / "BEA.exe").write_bytes(b"not ok")
        subprocess.run(["git", "add", "."], cwd=submodule, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Payload Fixture",
                "-c",
                "user.email=payload-fixture@example.invalid",
                "commit",
                "-q",
                "-m",
                "payload fixture",
            ],
            cwd=submodule,
            check=True,
        )
        (root / ".gitmodules").write_text(
            '[submodule "payload-fixture"]\n'
            "\tpath = references/payload-fixture\n"
            "\turl = ../payload-fixture.git\n",
            encoding="utf-8",
        )
        (root / "README.MD").write_text("# OK\n", encoding="utf-8")
        subprocess.run(
            ["git", "-c", "advice.addEmbeddedRepo=false", "add", "."],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        findings = check_repo(root, include_submodules=True)
        if not any(
            finding.path == "references/payload-fixture/game/BEA.exe"
            for finding in findings
        ):
            print("Public payload safety self-test: FAIL")
            print("- initialized submodule hard payload was not rejected")
            print(f"- findings: {findings!r}")
            return 1
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        (root / "game").mkdir()
        (root / "game" / "BEA.exe").write_bytes(b"root payload")
        submodule = root / "references" / "clean-fixture"
        submodule.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=submodule, check=True)
        (submodule / "README.MD").write_text("# Clean fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=submodule, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Clean Fixture",
                "-c",
                "user.email=clean-fixture@example.invalid",
                "commit",
                "-q",
                "-m",
                "clean fixture",
            ],
            cwd=submodule,
            check=True,
        )
        (root / ".gitmodules").write_text(
            '[submodule "clean-fixture"]\n'
            "\tpath = references/clean-fixture\n"
            "\turl = ../clean-fixture.git\n",
            encoding="utf-8",
        )
        (root / "README.MD").write_text("# Root fixture\n", encoding="utf-8")
        subprocess.run(
            ["git", "-c", "advice.addEmbeddedRepo=false", "add", "."],
            cwd=root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        root_findings = set(check_repo(root))
        combined_findings = set(check_repo(root, include_submodules=True))
        if not root_findings or not root_findings.issubset(combined_findings):
            print("Public payload safety self-test: FAIL")
            print("- root findings changed when submodule scanning was enabled")
            print(f"- root findings: {sorted(root_findings, key=lambda item: item.path)!r}")
            print(f"- combined findings: {sorted(combined_findings, key=lambda item: item.path)!r}")
            return 1
    print("Public payload safety self-test: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run built-in fixture tests.")
    parser.add_argument("--include-submodules", action="store_true", help="Also scan initialized submodule tracked files with parent hard-payload rules.")
    parser.add_argument("--require-private-text-guard", action="store_true", help="Accepted for compatibility; denylist text guards are built in.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--payload-root", type=Path, help="Scan an already materialized non-git payload/export tree by walking files under this root.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = (args.payload_root or args.repo_root).resolve()
    findings = check_payload_root(root) if args.payload_root else check_repo(root, include_submodules=args.include_submodules)
    if findings:
        print("Public payload safety check: FAIL")
        for finding in findings[:200]:
            print(f"- {finding.path}: {finding.label}: {finding.detail}")
        if len(findings) > 200:
            print(f"- ... ({len(findings) - 200} more)")
        return 1

    print("Public payload safety check: PASS")
    count = len(payload_root_files(root)) if args.payload_root else len(public_candidate_files(root, include_submodules=args.include_submodules))
    print(f"Public candidate files checked: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
