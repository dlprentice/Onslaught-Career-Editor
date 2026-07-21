#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Materialize the exact retail inputs consumed by the current rebuild slice.

The current source tree and release packages do not include these files. This
bounded recipe reads a user-provided Battle Engine Aquila installation,
verifies the supported Steam data, and writes only the known Level 100/Aquila
assets to ignored paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import struct
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GODOT_ASSETS = Path("rebuild/OnslaughtRebuild.Godot/Assets")
CORE_ASSETS = Path("rebuild/OnslaughtRebuild.Core/Assets")
LEVEL_ARCHIVE = "data/resources/100_res_PC.aya"
LEVEL_ARCHIVE_SHA256 = "ed6350c0e214d00ab1bf6a7bd137fba3e77d0afe19a6dc4c0607f56ac037496a"
SOUND_BANK = "data/sounds/sounds_english_pc.xap"
SOUND_BANK_SHA256 = "658c15e3bab844d65dd3c07c4ac880f16f741c0ea116f48c603449bbd4dda8b7"
STATIC_WORLD_ROOT = GODOT_ASSETS / "Level100/StaticWorld"
STATIC_WORLD_MANIFEST = STATIC_WORLD_ROOT / "level100-static-world.json"
STATIC_WORLD_MANIFEST_SHA256 = "acb4ffa4532340af9584614e66ec43af9993570cfc0a34deb00f58d1d41b3b71"
STATIC_WORLD_SOURCE_AGGREGATE_SHA256 = (
    "e3ab5a6c48143365bfbecf716effc5508e7be3d7b8a37d66c827b0994c5cf08a"
)
WATER_SURFACE_RESOURCE = STATIC_WORLD_ROOT / "Source/level100-water-surface.surf.bin"
WATER_SURFACE_SHA256 = "c3177354fed3eb5a94dc72debf2465c32ab1d931de79e5e88ac431043d3e917d"
WATER_TEXTURES = (
    (
        "water-reflection-00",
        "data/resources/dxtntextures/mixers%reflection00.tga(0)X8R8G8B8.aya",
        "41117238976776b114b8af4d1e4fbccd3afb90245f46f59b353e83663cac7b6e",
    ),
    (
        "water-caustic-00",
        "data/resources/dxtntextures/mixers%caustic00.tga(0)A8R8G8B8.aya",
        "7f34ee7d90ca483893c3ed8b0bf01bdf07b9a0b0f4a48f9df5fefd961d796f0a",
    ),
    (
        "water-waves",
        "data/resources/dxtntextures/mixers%waves.tga(0)R5G6B5.aya",
        "6ec848d1f9801be12f3a6591d6a4f5d5ecf1fc9f21d1a4242e1d681d826ab078",
    ),
    (
        "water-sun-blob",
        "data/resources/textures/mustbe_sunblob.tga(0)A8R8G8B8.aya",
        "5d97f24f514383c928c58c7f333bf489888b6a402004213ffbaaaad2ef30a53e",
    ),
    (
        "water-sun-reflection",
        "data/resources/textures/mustbe_sunreflect.tga(0)A8R8G8B8.aya",
        "a65940d6cdfe93f8b8820efb883fd33166aec63863ed894673466f3f58527ab4",
    ),
)


# Released physics-definition name -> exact loose mesh selected by Level 100.
STATIC_MESH_BY_DEFINITION = {
    "Control Tower": "fb_control_tower",
    "Forseti Pulse Tank Factory": "fb_tank_factory",
    "Forseti Repair Pad": "fb_health_pad",
    "SAT Turret": "ft_sam",
    "Iceberg 1": "iceberg1",
    "Iceberg 2": "iceberg2",
    "Iceberg 3": "iceberg3",
    "Iceberg 4": "iceberg4",
    "Blaster Turret": "ft_blaster",
    "Pulse Turret": "ft_pulse",
    "Forseti Research Building": "fb_research",
    "Forseti Building 1": "FB_House_Type_A",
    "Forseti Building 2": "FB_House_Type_B",
    "Forseti Building 3": "FB_House_Type_C",
    "Forseti Solar Pod": "FB_Solar_Pod",
    "Forseti Radar Station": "FB_radar_station",
    "Forseti Light Fighter Airfield": "fb_aircraft_factory",
    "Forseti Docks": "FB_Docks",
    "Hangar": "fb_hangar",
    "Forseti Tall Building 1": "F_buildtall1",
    "Forseti Tall Building 3": "F_buildtall3",
    "Forseti City Building 1": "f-city1",
    "Forseti City Building 2": "f-city2",
    "Forseti City Building 3": "f-city3",
}
STATIC_MESH_KEYS = tuple(dict.fromkeys(STATIC_MESH_BY_DEFINITION.values())) + tuple(
    f"pinesnow{variant}" for variant in range(4)
)


# Destination, released-install source, exact supported SHA-256.
DIRECT_ASSETS = (
    (GODOT_ASSETS / "Aquila/Source/m_cockpit2.msh.aya", "data/resources/meshes/m_cockpit2.msh.aya", "008b9292c59a5564ba3696f65d5bd51030d3e57250bc792d9d2b7f01292cdd4a"),
    (GODOT_ASSETS / "Aquila/Source/m_f_be1.msh.aya", "data/resources/meshes/m_f_be1.msh.aya", "d4c8fa752229af4111b31efa5ff5928c892736faa6a807915412767f3cd3c6b2"),
    (GODOT_ASSETS / "Aquila/Source/m_f_be2.msh.aya", "data/resources/meshes/m_f_be2.msh.aya", "35aada1313c3cbb796ba75db071321035f7005096da7c148a7514944f4772b4c"),
    (GODOT_ASSETS / "Aquila/Textures/be-tex-a.texture.aya", "data/resources/dxtntextures/meshtex%BE_texA.tga(0)A1R5G5B5.aya", "86f9f54ae97ba4e3782c65909d1d93b86566228b1132829ebb93816eb5a4705b"),
    (GODOT_ASSETS / "Aquila/Textures/be-tex-b.texture.aya", "data/resources/dxtntextures/meshtex%BE_texB.tga(0)A1R5G5B5.aya", "ea01431a4023abd517daf5a27066eb7edf706100fb3991566726fb4530490b60"),
    (GODOT_ASSETS / "Aquila/Textures/bluegun-light.texture.aya", "data/resources/dxtntextures/meshtex%A8_bluegunlight_LIT.tga(0)A8R8G8B8.aya", "85858e7809a974b74f3db5a169e081fc9dd506558f1ca99fa47c7832d8552fc5"),
    (GODOT_ASSETS / "Aquila/Textures/cockpit.texture.aya", "data/resources/dxtntextures/meshtex%cockpit.tga(0)A1R5G5B5.aya", "c62d0c668226f056db7455c8a5a8fa7d55ab7621ade1e58392d6aaad3c00f0cc"),
    (GODOT_ASSETS / "Hud/bar-line.texture.aya", "data/resources/dxtntextures/hud%v2%BarLine.tga(0)X8R8G8B8.aya", "16796e3a8acfec3529e03c29afbefbe28c92ffccd5b05574f992e8f31976704d"),
    (GODOT_ASSETS / "Hud/battleline-outline.texture.aya", "data/resources/dxtntextures/hud%v2%BattleLineOutline.tga(0)X8R8G8B8.aya", "b1c097b29dd81e2a0493f72a157ccd5ad249b5abf758224c75df4f93973d0405"),
    (GODOT_ASSETS / "Hud/circle-darkener.texture.aya", "data/resources/dxtntextures/hud%v2%CircleDarkener.tga(0)A8R8G8B8.aya", "7bd18594757165dcdd8dadb618ea99eb500ed105dbe2d6a6f66bbcbc31c323a3"),
    (GODOT_ASSETS / "Hud/circle-mask.texture.aya", "data/resources/dxtntextures/hud%v2%CircleMask.tga(0)A8R8G8B8.aya", "14d809f9b45f5153f82fa1f80152690b554710d83f91b8cbe203de5cf18a9dfa"),
    (GODOT_ASSETS / "Hud/compass-objective-marker.texture.aya", "data/resources/dxtntextures/hud%v2%CompassObjectiveMarker.tga(0)A8R8G8B8.aya", "e24fca83de34646a7328c313e7b89ac02c6bc4b04a69a74bf3ee81b3d57283df"),
    (GODOT_ASSETS / "Hud/crosshair-dot.texture.aya", "data/resources/dxtntextures/hud%v3%hud_crosshair_dot.tga(0)A8R8G8B8.aya", "19e1b35b885a36230e5a1d47a9910164b0ca177746649a15c146cefca29651dd"),
    (GODOT_ASSETS / "Hud/crosshair-primary.texture.aya", "data/resources/dxtntextures/hud%v3%hud_crosshair_primary.tga(0)A8R8G8B8.aya", "310dae2f7dd976f6cc724604737726885aff96ab6bc507e41f90dca60d134b17"),
    (GODOT_ASSETS / "Hud/crosshair-secondary.texture.aya", "data/resources/dxtntextures/hud%v3%hud_crosshair_secondary.tga(0)A8R8G8B8.aya", "7b078344e64d1e78ef64a8e21bdd3787e059b628c6a442634e9d13ba7d3a0487"),
    (GODOT_ASSETS / "Hud/font-13ps.texture.aya", "data/resources/textures/mustbe_Font13PS.tga(0)A8R8G8B8.aya", "7acc088b75e729cbdc2782e239a7d18ba0ec409e1bc890109aa1020f5ee81dc0"),
    (GODOT_ASSETS / "Hud/message-noise.texture.aya", "data/resources/dxtntextures/MessageBox%noisebig.tga(0)X8R8G8B8.aya", "f5c43c330394db9eb7c1e782f3f30fe847de01d7ce9335d2c7f9fd24babb1825"),
    (GODOT_ASSETS / "Hud/objective-inner-centre.texture.aya", "data/resources/dxtntextures/hud%v2%ObjectiveInnerCentre.tga(0)A8R8G8B8.aya", "fc42774e8c4f4534b65009807bfdb333443a9f5202c6a2c59dff0dddbed4f55b"),
    (GODOT_ASSETS / "Hud/objective-inner-left.texture.aya", "data/resources/dxtntextures/hud%v2%ObjectiveInnerLeft.tga(0)A8R8G8B8.aya", "70030aace505e8e3d7f56dde0b9c6a929f3d2c61912fc03ac816746b6d8a96bd"),
    (GODOT_ASSETS / "Hud/objective-inner-right.texture.aya", "data/resources/dxtntextures/hud%v2%ObjectiveInnerRight.tga(0)A8R8G8B8.aya", "7c85b0293fc7a524978a21e7cdc06b1dd3308e9a595aadca054b51cd9a6aa113"),
    (GODOT_ASSETS / "Hud/objective-left.texture.aya", "data/resources/dxtntextures/hud%v2%ObjectiveLeft.tga(0)A8R8G8B8.aya", "0ae835780d1af6c01f0272a50afda141abca70eaa5c23d74e7fc3968b6d9194f"),
    (GODOT_ASSETS / "Hud/objective-right.texture.aya", "data/resources/dxtntextures/hud%v2%ObjectiveRight.tga(0)A8R8G8B8.aya", "581f10446db76ece7aa7044b4c02f0431a79a7d606225d5c69a412c17f85078b"),
    (GODOT_ASSETS / "Hud/radar-outline.texture.aya", "data/resources/dxtntextures/hud%v2%RadarOutline.tga(0)X8R8G8B8.aya", "507d465248f7321f2332413b2c6f461f3b3c45d87c52d86c38c43104043d7dc7"),
    (GODOT_ASSETS / "Hud/radio-north.texture.aya", "data/resources/dxtntextures/hud%v2%RadioNorth.tga(0)A8R8G8B8.aya", "e5dfd8db4dd73e9aeeffbb009fca68d889572c996987bce365b0b5b4d0a7ed85"),
    (GODOT_ASSETS / "Hud/radio-view.texture.aya", "data/resources/dxtntextures/hud%v2%RadioView.tga(0)A8R8G8B8.aya", "888d5a70ab812e23f75db76ab2ed71cd2cce04191ee282d525c86e337cc01778"),
    (GODOT_ASSETS / "Hud/scanner-blob-small.texture.aya", "data/resources/dxtntextures/hud%ScannerBlobSmall.tga(0)A8R8G8B8.aya", "d7e9d287536f23e67bf35f678ec75d1a349353ae1d9d00b87ce09f6bd03641e4"),
    (GODOT_ASSETS / "Hud/tatiana-portrait-oo.texture.aya", "data/resources/dxtntextures/MessageBox%tat_oo.tga(0)A8R8G8B8.aya", "39f40088069a8c68584a5a0cda9e5ae7d4e4e5a248a12f0d0a240b8d3668621e"),
    (GODOT_ASSETS / "Hud/tatiana-portrait-ee.texture.aya", "data/resources/dxtntextures/MessageBox%tat_ee.tga(0)A8R8G8B8.aya", "4a4a17b72bbafae2b324e3a0a1c847226a288feaa7c4273c45aa2de8aea3f99a"),
    (GODOT_ASSETS / "Hud/tatiana-portrait-mm.texture.aya", "data/resources/dxtntextures/MessageBox%tat_mm.tga(0)A8R8G8B8.aya", "802d8e22d8d304e12589a547f22ac2f2d5771b96aea47306b3b2bbf752730de5"),
    (GODOT_ASSETS / "Hud/tatiana-portrait.texture.aya", "data/resources/dxtntextures/MessageBox%tat_aa.tga(0)A8R8G8B8.aya", "34d451a6fc31e399b99032230413a60f146b41a0fea65e61561a37d8ec757cfd"),
    (GODOT_ASSETS / "Hud/technician-portrait-oo.texture.aya", "data/resources/dxtntextures/MessageBox%technic_oo.tga(0)A8R8G8B8.aya", "b28a3818b8ef37decfd8779d7acae74c657b5d510edd2332587864f2a1e58a2c"),
    (GODOT_ASSETS / "Hud/technician-portrait-ee.texture.aya", "data/resources/dxtntextures/MessageBox%technic_ee.tga(0)A8R8G8B8.aya", "05326c603e8c9224c5bab488a32ab9e9e19ca5b3fb424bc700af97ae71c2527f"),
    (GODOT_ASSETS / "Hud/technician-portrait-mm.texture.aya", "data/resources/dxtntextures/MessageBox%technic_mm.tga(0)A8R8G8B8.aya", "263a2c107d6463a717ddef20cc113cadfb585bd8ecbb1db479f049843dcf3636"),
    (GODOT_ASSETS / "Hud/technician-portrait.texture.aya", "data/resources/dxtntextures/MessageBox%technic_aa.tga(0)A8R8G8B8.aya", "c4c1b11f4ddfb960afc1c1d2a04020fadf997795eccf651c07314141652f9603"),
    (GODOT_ASSETS / "Hud/weapon-fill.texture.aya", "data/resources/dxtntextures/hud%v2%WeaponFill.tga(0)A8R8G8B8.aya", "e639910d70ae10b044423cd5025c300c61cb8a9b5765890fd1a011c7d4499c0d"),
    (GODOT_ASSETS / "Hud/weapon-outline.texture.aya", "data/resources/dxtntextures/hud%v2%WeaponOutline.tga(0)X8R8G8B8.aya", "2e2da786db82c8fd76de36d8d71fe744ddddd364247467cba1bfb9a95e52d62b"),
    (GODOT_ASSETS / "Level100/Sky/cube25-cent.texture.aya", "data/resources/dxtntextures/cubes%cube25_cent.tga(0)X8R8G8B8.aya", "1aad6cc8f85b6bb7ccbb8d2c7b0e6aa31722a9adbde5a3f19b248430ca83469e"),
    (GODOT_ASSETS / "Level100/Sky/cube25-down.texture.aya", "data/resources/dxtntextures/cubes%cube25_down.tga(0)X8R8G8B8.aya", "4770829ba631e93fbc33db2012754da75a06bfccc2fb2b36875e92032e22d19d"),
    (GODOT_ASSETS / "Level100/Sky/cube25-left.texture.aya", "data/resources/dxtntextures/cubes%cube25_left.tga(0)X8R8G8B8.aya", "d7cbce30e51473ddc89ed0c44326e598dac4d2682f64ef20c19237afd2cebe14"),
    (GODOT_ASSETS / "Level100/Sky/cube25-right.texture.aya", "data/resources/dxtntextures/cubes%cube25_right.tga(0)X8R8G8B8.aya", "830c9b965c76a4023c2415b7c8924ca32590562c850cc84e92c003e173263d11"),
    (GODOT_ASSETS / "Level100/Sky/cube25-up.texture.aya", "data/resources/dxtntextures/cubes%cube25_up.tga(0)X8R8G8B8.aya", "419e2424bcfd698058d72111ffa7d84fdc9022e03815db7c0da28403f4925f3c"),
    (GODOT_ASSETS / "Level100/Source/m_f_pulsetank_training.msh.aya", "data/resources/meshes/m_f_pulsetank_training.msh.aya", "9b2cfdceb86ed700ed924051fbff13c32dc30bd8f8b948ea1cf8aa9fbfe8b97b"),
    (GODOT_ASSETS / "Level100/Source/m_m_warehouse.msh.aya", "data/resources/meshes/m_m_warehouse.msh.aya", "61fe5465bd7affedf749ad784209be02b2e4dd28631e70386c3810302b5f6f15"),
    (GODOT_ASSETS / "Level100/Textures/effect-flash-medium.texture.aya", "data/resources/dxtntextures/Particle%sun2.tga(0)R5G6B5.aya", "d7fbfcb4edb2167fedc0a467d4501c9bbc2f6a2852c7873daec3953e6f518f5c"),
    (GODOT_ASSETS / "Level100/Textures/mech-pulse-medium-energy-trail.texture.aya", "data/resources/dxtntextures/Particle%Energy Trail.tga(0)R5G6B5.aya", "64eddc6b147c67886f41ef4d2bcc2a0606b453b01e4d93b9962f10cc07aba92e"),
    (GODOT_ASSETS / "Level100/Textures/mech-pulse-medium-halo.texture.aya", "data/resources/dxtntextures/Particle%Halo.tga(0)R5G6B5.aya", "cde6efc90dc7958c5bda425a04486e277beb85a7f1c33fb9074f369e92d58edb"),
    (GODOT_ASSETS / "Level100/Textures/pulse-bolt-blue-spark.texture.aya", "data/resources/dxtntextures/Particle%Blue Spark 2.tga(0)A4R4G4B4.aya", "b3730b1e9d7713910e0de4bd0cb0dcfefcb9ceb8f6402d50681a524adc0dcb08"),
    (GODOT_ASSETS / "Level100/Textures/pulse-bolt-blue-trail.texture.aya", "data/resources/dxtntextures/Particle%Blue Trail.tga(0)R5G6B5.aya", "2b4bc5cf8902d7ea8452f1068ac8f11514c8238a733ca33aad7d6d0667688a63"),
    (GODOT_ASSETS / "Level100/Textures/pulse-impact-animated-blob.texture.aya", "data/resources/dxtntextures/Particle%alparticle4.tga(0)A4R4G4B4.aya", "74085b280199e20b765640cfc3e417e6da0fcbfb25384e129858a32f5deb995d"),
    (GODOT_ASSETS / "Level100/Textures/pulse-impact-shockwave.texture.aya", "data/resources/dxtntextures/Particle%1telep.tga(0)R5G6B5.aya", "e92efc3f5adfa347e6b50f1e3d20af4c6800d76853a2126d71237dfefeea9f10"),
    (GODOT_ASSETS / "Level100/Textures/target-tank-explosion-animated.texture.aya", "data/resources/dxtntextures/Particle%alparticle6.tga(0)R5G6B5.aya", "3c8fc30ad4923c56c3735caab5661a3f176eb661eaa678093870f51de4204c9e"),
    (GODOT_ASSETS / "Level100/Textures/target-tank-explosion-fireball.texture.aya", "data/resources/dxtntextures/Particle%fireball.tga(0)A4R4G4B4.aya", "e6c166669e351632a90b41c74782967923c78fc8be644a1e8948d356806b23ed"),
    (GODOT_ASSETS / "Level100/Textures/target-tank.texture.aya", "data/resources/dxtntextures/meshtex%f_pulsetank_training.tga(0)A1R5G5B5.aya", "97ddd1e18e45b19e249e91e881d773d80d36768a2cd48f6549a769c2559a7b7e"),
    (GODOT_ASSETS / "Level100/Textures/target-warehouse-m001.texture.aya", "data/resources/dxtntextures/meshtex%M_001.tga(0)A1R5G5B5.aya", "689b184ab8a5d03f33b69e5c35edcfdfdec12aa9b4b31f7c74ce5209f6236a49"),
    (GODOT_ASSETS / "Level100/Textures/target-warehouse-m002.texture.aya", "data/resources/dxtntextures/meshtex%M_002.tga(0)A1R5G5B5.aya", "8fabadbe1c5af067a740cf05debd1c952c628fd5fa3ea92b8202094704b8a20d"),
    (GODOT_ASSETS / "Level100/Textures/material-overlay-a8trust5.texture.aya", "data/resources/dxtntextures/meshtex%a8trust5.tga(0)A8R8G8B8.aya", "4ccde973f9741c110a82f350e102f1a12c566ff3d3b1b4f5426f2bbf536be843"),
    (GODOT_ASSETS / "Level100/Textures/terrain-cloud-shadow.texture.aya", "data/resources/dxtntextures/clouds%shadow.tga(0)A8R8G8B8.aya", "fc7441887e494e4b18f2b16179ed42c17801b128d71e29d653a4e8b792869519"),
    (GODOT_ASSETS / "Level100/Textures/terrain-detail-00.texture.aya", "data/resources/dxtntextures/mixers%detail00.tga(0)R5G6B5.aya", "7c9c22169d13ed8b7d6ad69286bdb59cc88f9ae3bfb6a9d3a0503d320386bfef"),
    (GODOT_ASSETS / "Level100/TutorialAudio/hud_01.ogg", "data/sounds/english/MessageBox/hud_01.ogg", "bae30243a2b5fe3dae718181ac5b05d766f93d5e25b042fe1b04c71fc9347909"),
    (GODOT_ASSETS / "Level100/TutorialAudio/hud_02.ogg", "data/sounds/english/MessageBox/hud_02.ogg", "43ae0c306b7935a21d415338348508eabf3a61f8799c0fd0873c89919fb84a35"),
    (GODOT_ASSETS / "Level100/TutorialAudio/hud_05.ogg", "data/sounds/english/MessageBox/hud_05.ogg", "66256d87557946647a51a2e8d49e044bc55ae370c4ad1c8e950b1d884ec082eb"),
    (GODOT_ASSETS / "Level100/TutorialAudio/hud_06.ogg", "data/sounds/english/MessageBox/hud_06.ogg", "4ed80a12fa7d2ad07a044f95f94d52455413962b75e7689101df6907711f3235"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_01.ogg", "data/sounds/english/MessageBox/tutorial_01.ogg", "48e40b07a77b5776f817ed8d8ffe1eff1a978b10480cab92019077e7b66784a8"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_02.ogg", "data/sounds/english/MessageBox/tutorial_02.ogg", "fa0533de72b8d7702b83b709ba631bc8f7a42a5183babcb147ae653a5d7a2904"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_03.ogg", "data/sounds/english/MessageBox/tutorial_03.ogg", "8e3bbd3f680099f7664f473f73837bf3e6d09474b4426677dd6bf27b31177dc2"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_13_mod.ogg", "data/sounds/english/MessageBox/tutorial_13_mod.ogg", "7eee9087f86c00abe4feab115b20e4e2f27a8e6d1adc7318b1602446a7493e65"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_message_log.ogg", "data/sounds/english/MessageBox/tutorial_message_log.ogg", "7a03ff8f3faa4be4b729e7619055379c62921e2eaeb67fc9711dac0dfe273f8b"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_open_fire.ogg", "data/sounds/english/MessageBox/tutorial_open_fire.ogg", "04a1a65b45f75f4d1e85b0fab6970125584efbabe3609d7413e60b569a26d20c"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_open_fire_2.ogg", "data/sounds/english/MessageBox/tutorial_open_fire_2.ogg", "122782139a31fbd777a734e0979f4f0ab8a7308d1154d7215ce2af13d56e3237"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_pulse_cannon.ogg", "data/sounds/english/MessageBox/tutorial_pulse_cannon.ogg", "2fda4a38b4737e03647c03bac38bfb36e7e6ff16b279007c04616c23857c25f8"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_pulse_cannon_2.ogg", "data/sounds/english/MessageBox/tutorial_pulse_cannon_2.ogg", "f4eca49f26f61f0369c0d8b770300596695f8a62ec12269a4c9d1cb3f61b13e0"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_scanner.ogg", "data/sounds/english/MessageBox/tutorial_scanner.ogg", "7a9535b1187b6e1ff276cebc3906ec2102e5d166f381ee674113b4f09c2b3bd2"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_technician_01.ogg", "data/sounds/english/MessageBox/tutorial_technician_01.ogg", "4792371453b4402454b922a481eb0968a099efb13981ff1918aa6177fb6ae151"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_vulcan_cannon.ogg", "data/sounds/english/MessageBox/tutorial_vulcan_cannon.ogg", "7f483d8f3c876c8e9e8bd52b0369f1c54c39c83c174c0a43d5fb8674c069172c"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_vulcan_cannon_2.ogg", "data/sounds/english/MessageBox/tutorial_vulcan_cannon_2.ogg", "6f872ca07fcc4f49ffb0cb2536a460411139fe1d77d263198c0f423fcefa9d90"),
)


CHUNKS = (
    (CORE_ASSETS / "Level100/level100-heightfield.hfld.bin", b"HFLD", 668660, "7a4c7c5b9400e2c8d2325cecb5c44701cd8a6e6f8609cbc8bc31d449c0620f5d"),
    (GODOT_ASSETS / "Level100/Source/level100-mixer-set-10.mapt.bin", b"MAPT", 399468, "c21576ae7ea75fa800ab4117c1479aeb70359a1acc84edd9508895eb339612f1"),
    (GODOT_ASSETS / "Level100/Source/level100-mixer-map.mmap.bin", b"MMAP", 877597, "45045d248e27366080614c1ad26fc9e711bc9656f4f79210eac63d2a20938361"),
)


# Destination, source AYA destination above, hierarchy frame, exact OBJ SHA-256.
MESHES = (
    (GODOT_ASSETS / "Level100/level100-target-tank.obj", GODOT_ASSETS / "Level100/Source/m_f_pulsetank_training.msh.aya", None, "3a67f2bf49c9505855f73259d8d5829a7e0d1a0aed0f5a8802e82c4cf2c5df9f"),
    (GODOT_ASSETS / "Level100/level100-target-warehouse.obj", GODOT_ASSETS / "Level100/Source/m_m_warehouse.msh.aya", None, "3883b651a9963813a4ab9982460425910be5d7f8f7edce15ade475cf6d8eb5ce"),
)


# Destination, zero-based XAP record, exact record name, exact WAV SHA-256.
SOUNDS = (
    (GODOT_ASSETS / "Aquila/SoundEffects/engine-inflight.wav", 23, "Battle Engine\\N_BE_engine_inflight", "0e6eb03aa2c2991c0e59c3483956b1c608a79700e0de179c855491cff548ac04"),
    (GODOT_ASSETS / "Aquila/SoundEffects/engine-takeoff.wav", 25, "Battle Engine\\N_BE_engine_takeoff", "3698a4419c000ab982cbc92c6553ac2639272fb85930df52a26528b232f00798"),
    (GODOT_ASSETS / "Level100/SoundEffects/pulse-cannon-fire.wav", 35, "Battle Engine\\N_BE_pulse_cannon_fire", "710ff06db55bc694efb8ff7d3a5ab658125e7ca0fe6b4733a805da98b22b0277"),
    (GODOT_ASSETS / "Level100/SoundEffects/target-tank-explosion-medium.wav", 102, "Impact\\N_I_explosion_medium", "7228ae049cb0a9877e63671a65e51829443017b2c4981df90a9c64d2f38b6d9c"),
    (GODOT_ASSETS / "Level100/SoundEffects/pulse-impact-small.wav", 105, "Impact\\N_I_explosion_small", "3296b13938928f54847a29e17307e7875e9933f8fd6381bf0dfcd260cd6fc131"),
)


IMA_STEP_TABLE = (
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31,
    34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97, 107, 118, 130,
    143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449,
    494, 544, 598, 658, 724, 796, 876, 963, 1060, 1166, 1282, 1411,
    1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660,
    4026, 4428, 4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493,
    10442, 11487, 12635, 13899, 15289, 16818, 18500, 20350, 22385,
    24623, 27086, 29794, 32767,
)
IMA_INDEX_TABLE = (-1, -1, -1, -1, 2, 4, 6, 8)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_exact(path: Path, expected_hash: str) -> bytes:
    try:
        data = path.read_bytes()
    except OSError as error:
        raise RuntimeError(f"required retail input is unavailable: {path}") from error
    actual = _sha256(data)
    if actual != expected_hash:
        raise RuntimeError(f"unsupported retail input: {path} (SHA-256 {actual})")
    return data


def _fixed_outputs() -> tuple[tuple[Path, str], ...]:
    direct = tuple((path, expected) for path, _, expected in DIRECT_ASSETS)
    chunks = tuple((path, expected) for path, _, _, expected in CHUNKS)
    meshes = tuple((path, expected) for path, _, _, expected in MESHES)
    sounds = tuple((path, expected) for path, _, _, expected in SOUNDS)
    return direct + chunks + meshes + sounds


def _resource_relative(resource_path: str) -> Path:
    prefix = "res://Assets/Level100/StaticWorld/"
    if not resource_path.startswith(prefix):
        raise RuntimeError(f"static-world resource escaped its owner: {resource_path}")
    suffix = resource_path[len("res://") :]
    relative = Path("rebuild/OnslaughtRebuild.Godot") / Path(suffix)
    if ".." in relative.parts:
        raise RuntimeError(f"static-world resource has an invalid path: {resource_path}")
    return relative


def _static_world_outputs(root: Path) -> tuple[tuple[Path, str], ...]:
    manifest_path = root / STATIC_WORLD_MANIFEST
    manifest_bytes = manifest_path.read_bytes()
    manifest_hash = _sha256(manifest_bytes)
    if manifest_hash != STATIC_WORLD_MANIFEST_SHA256:
        raise RuntimeError(
            f"static-world manifest does not reproduce exactly (SHA-256 {manifest_hash})"
        )
    manifest = json.loads(manifest_bytes)
    if (
        manifest.get("schema") != "onslaught.level100-static-world.v4"
        or manifest.get("sourceArchiveSha256") != LEVEL_ARCHIVE_SHA256
        or manifest.get("sourceAggregateSha256") != STATIC_WORLD_SOURCE_AGGREGATE_SHA256
        or manifest.get("unitRecordCount") != 35
        or manifest.get("visibleObjectCount") != 33
        or manifest.get("suppressedFernCount") != 753
        or manifest.get("pineInstanceCount") != 1481
        or len(manifest.get("objects", ())) != 33
        or len(manifest.get("pines", ())) != 1481
        or len(manifest.get("meshes", {})) != 28
        or len(manifest.get("textures", {})) != 33
        or manifest.get("textures", {})
        .get("meshtex-a8-fb-hangermorebits-lit", {})
        .get("blendTextureAlpha")
        is not True
        or sum(
            item.get("blendTextureAlpha") is True
            for item in manifest.get("textures", {}).values()
        )
        != 1
        or manifest.get("water", {}).get("surfaceSha256") != WATER_SURFACE_SHA256
    ):
        raise RuntimeError("static-world manifest has unexpected identity or counts")

    outputs: list[tuple[Path, str]] = [
        (STATIC_WORLD_MANIFEST, STATIC_WORLD_MANIFEST_SHA256)
    ]
    for collection in (manifest["meshes"], manifest["textures"]):
        for item in collection.values():
            outputs.append((_resource_relative(item["resourcePath"]), item["sha256"]))
    outputs.append(
        (
            _resource_relative(manifest["water"]["surfaceResourcePath"]),
            manifest["water"]["surfaceSha256"],
        )
    )
    if len(outputs) != 63 or len({path for path, _ in outputs}) != len(outputs):
        raise RuntimeError("static-world manifest has duplicate or missing outputs")
    return tuple(outputs)


def _all_outputs(root: Path) -> tuple[tuple[Path, str], ...]:
    return _fixed_outputs() + _static_world_outputs(root)


def _outputs_ready() -> bool:
    try:
        for relative, expected in _all_outputs(ROOT):
            path = ROOT / relative
            if _sha256(path.read_bytes()) != expected:
                return False
        return True
    except (KeyError, OSError, RuntimeError, TypeError, ValueError):
        return False


def _steam_roots() -> list[Path]:
    roots: list[Path] = []
    try:
        import winreg

        for hive, key_name, value_name in (
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
        ):
            try:
                with winreg.OpenKey(hive, key_name) as key:
                    roots.append(Path(winreg.QueryValueEx(key, value_name)[0]))
            except OSError:
                pass
    except ImportError:
        pass

    roots.extend((Path(r"C:\Program Files (x86)\Steam"), Path(r"C:\Program Files\Steam")))
    libraries: list[Path] = []
    for root in roots:
        libraries.append(root)
        vdf = root / "steamapps/libraryfolders.vdf"
        try:
            text = vdf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        libraries.extend(Path(value.replace("\\\\", "\\")) for value in re.findall(r'"path"\s+"([^"]+)"', text))
    return libraries


def _game_candidates(explicit: Path | None) -> list[Path]:
    if explicit is not None:
        return [explicit]

    candidates: list[Path] = []
    for library in _steam_roots():
        candidates.append(library / "steamapps/common/Battle Engine Aquila")
    candidates.extend(
        Path(path)
        for path in (
            r"D:\Steam\steamapps\common\Battle Engine Aquila",
            r"D:\SteamLibrary\steamapps\common\Battle Engine Aquila",
            r"E:\Steam\steamapps\common\Battle Engine Aquila",
            r"E:\SteamLibrary\steamapps\common\Battle Engine Aquila",
        )
    )
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = os.path.normcase(os.path.abspath(candidate))
        if key not in seen:
            seen.add(key)
            unique.append(Path(key))
    return unique


def _resolve_game_root(explicit: Path | None) -> Path:
    for candidate in _game_candidates(explicit):
        if (candidate / "BEA.exe").is_file() and (candidate / LEVEL_ARCHIVE).is_file() and (candidate / SOUND_BANK).is_file():
            return candidate
    if explicit is not None:
        raise RuntimeError(f"not a complete Battle Engine Aquila installation: {explicit}")
    raise RuntimeError("Battle Engine Aquila was not detected; pass --game-root with your retail installation")


def _extract_chunk(raw: bytes, tag: bytes, expected_size: int, expected_hash: str) -> bytes:
    matches: list[bytes] = []
    cursor = 0
    while True:
        offset = raw.find(tag, cursor)
        if offset < 0:
            break
        cursor = offset + 1
        if offset + 8 > len(raw):
            continue
        declared = struct.unpack_from("<I", raw, offset + 4)[0]
        end = offset + 8 + declared
        if end > len(raw) or end - offset != expected_size:
            continue
        candidate = raw[offset:end]
        if _sha256(candidate) == expected_hash:
            matches.append(candidate)
    if len(matches) != 1:
        raise RuntimeError(f"expected one exact {tag.decode('ascii')} chunk, found {len(matches)}")
    return matches[0]


def _chunk_payload(data: bytes, wanted_tag: bytes) -> bytes:
    matches: list[bytes] = []
    offset = 0
    while offset < len(data):
        if offset + 8 > len(data):
            raise RuntimeError("Level 100 contains a truncated world chunk")
        size = struct.unpack_from("<I", data, offset + 4)[0]
        end = offset + 8 + size
        if end > len(data):
            raise RuntimeError("Level 100 contains an overrun world chunk")
        if data[offset : offset + 4] == wanted_tag:
            matches.append(data[offset + 8 : end])
        offset = end
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one {wanted_tag.decode('ascii')} world chunk, found {len(matches)}"
        )
    return matches[0]


class _WorldReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.position = 0

    def _take(self, size: int) -> bytes:
        end = self.position + size
        if size < 0 or end > len(self.data):
            raise RuntimeError("Level 100 base-world data is truncated")
        value = self.data[self.position : end]
        self.position = end
        return value

    def uint8(self) -> int:
        return self._take(1)[0]

    def uint16(self) -> int:
        return struct.unpack("<H", self._take(2))[0]

    def int32(self) -> int:
        return struct.unpack("<i", self._take(4))[0]

    def single(self) -> float:
        value = struct.unpack("<f", self._take(4))[0]
        if not math.isfinite(value):
            raise RuntimeError("Level 100 base-world data contains a non-finite value")
        return value

    def string8(self) -> str:
        return self._take(self.uint8()).decode("ascii")

    def c_string(self) -> str:
        end = self.data.find(b"\0", self.position)
        if end < 0:
            raise RuntimeError("Level 100 base-world data has an unterminated string")
        value = self.data[self.position : end].decode("ascii")
        self.position = end + 1
        return value


def _parse_static_world(raw_level: bytes) -> tuple[list[dict[str, object]], list[list[float | int]], int]:
    bswd = _chunk_payload(_chunk_payload(_chunk_payload(raw_level, b"WRES"), b"WRLD"), b"BSWD")
    reader = _WorldReader(bswd)
    if (
        reader.uint16() != 50
        or tuple(reader.int32() for _ in range(3)) != (3, 42, 1)
        or reader.int32() != 1
        or reader.string8() != "Paladin Prototype"
        or tuple(reader.int32() for _ in range(4)) != (1, 0, 0, 0)
        or tuple(reader.int32() for _ in range(4)) != (-1, 0, 1, 0)
        or reader.uint16() != 35
    ):
        raise RuntimeError("Level 100 base-world header is not the supported version-50 layout")

    objects: list[dict[str, object]] = []
    for ordinal in range(35):
        thing_type = reader.int32()
        position = [reader.single() for _ in range(3)]
        yaw_pitch_roll = [reader.single() for _ in range(3)]
        for _ in range(3):
            reader.int32()
        reader.c_string()
        name = reader.c_string()
        reader.c_string()
        reader.int32()
        reader.int32()

        definition = ""
        if thing_type in (8, 35):
            definition = reader.string8()
            reader.int32()
        elif thing_type != 37:
            raise RuntimeError(f"unsupported Level 100 base-world thing type {thing_type}")

        if thing_type == 37:
            continue
        mesh_key = STATIC_MESH_BY_DEFINITION.get(definition)
        if mesh_key is None:
            raise RuntimeError(f"unmapped Level 100 physics definition: {definition}")
        objects.append(
            {
                "definition": definition,
                "mesh": mesh_key,
                "name": name or definition,
                "ordinal": ordinal,
                "retailPosition": position,
                "yaw": yaw_pitch_roll[0],
            }
        )

    if reader.uint16() != 0 or reader.int32() != 2:
        raise RuntimeError("Level 100 tree groups are not the supported explicit layout")
    groups: dict[str, list[list[float | int]]] = {}
    for _ in range(2):
        group_name = reader.string8()
        count = reader.int32()
        if count < 0 or count > 4096 or group_name in groups:
            raise RuntimeError("Level 100 has invalid explicit tree metadata")
        instances: list[list[float | int]] = []
        for _ in range(count):
            x = reader.single()
            y = reader.single()
            variant = reader.int32()
            if variant not in range(4):
                raise RuntimeError("Level 100 has an unsupported tree variant")
            instances.append([x, y, variant])
        groups[group_name] = instances

    ferns = groups.get("fernsnow")
    pines = groups.get("pinesnow")
    if (
        len(objects) != 33
        or ferns is None
        or len(ferns) != 753
        or pines is None
        or len(pines) != 1481
        or reader.position != 29_549
    ):
        raise RuntimeError("Level 100 base-world object/tree counts do not reproduce")
    return objects, pines, len(ferns)


def _slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not result:
        raise RuntimeError("retail asset name did not produce a safe local name")
    return result


def _texture_key(texture_ref: str) -> str:
    name = texture_ref.replace("/", "\\").rsplit("\\", 1)[-1]
    if name.lower().endswith(".tga"):
        name = name[:-4]
    return _slug(name)


def _material_surface_name(texture_indices: tuple[int, int, int, int, int, int]) -> str:
    return "layers-" + "-".join(f"{value:08x}" for value in texture_indices)


def _texture_pass_metadata(raw: bytes) -> tuple[float, float, float, float, float]:
    if len(raw) != 20:
        raise RuntimeError("mesh texture metadata has an unexpected length")
    values = struct.unpack("<5f", raw)
    opacity, offset_u, offset_v, scale_u, scale_v = values
    if (
        not all(math.isfinite(value) for value in values)
        or opacity < 0.0
        or opacity > 1.0
        or scale_u < 0.0
        or scale_v < 0.0
        or scale_u > 100.0
        or scale_v > 100.0
    ):
        raise RuntimeError("mesh texture metadata is outside the supported retail envelope")
    return opacity, offset_u, offset_v, scale_u, scale_v


def _texture_blend_alpha_flags(raw_level: bytes) -> dict[str, bool]:
    """Read the released CTexture +0xB4 mode from Level 100's DXTX records."""
    marker = b"DXTX\x6c\x01\x00\x00CTEX\x58\x01\x00\x00"
    flags: dict[str, bool] = {}
    record_count = 0
    offset = 0
    while True:
        offset = raw_level.find(marker, offset)
        if offset < 0:
            break
        payload_start = offset + len(marker)
        payload_end = payload_start + 344
        if payload_end > len(raw_level):
            raise RuntimeError("Level 100 has a truncated CTexture record")
        payload = raw_level[payload_start:payload_end]
        name_bytes = payload[8:72].split(b"\0", 1)[0]
        try:
            name = name_bytes.decode("ascii")
        except UnicodeDecodeError as error:
            raise RuntimeError("Level 100 has a non-ASCII CTexture name") from error
        normalized = name.replace("/", "\\").strip().lower()
        raw_flag = struct.unpack_from("<I", payload, 0xB4)[0]
        if not normalized or raw_flag not in (0, 1):
            raise RuntimeError("Level 100 has an unsupported CTexture record")
        flag = raw_flag == 1
        previous = flags.setdefault(normalized, flag)
        if previous != flag:
            raise RuntimeError(f"Level 100 CTexture mode disagrees for {name}")
        record_count += 1
        offset = payload_end

    if (
        record_count != 273
        or len(flags) != 265
        or {name for name, enabled in flags.items() if enabled}
        != {"meshtex\\a8_fb_hangermorebits_lit.tga"}
    ):
        raise RuntimeError("Level 100 CTexture modes do not match the released archive")
    return flags


def _dds_metadata(source: bytes, inflate_aya_bytes) -> tuple[int, int, str]:
    dds = inflate_aya_bytes(source)
    if len(dds) < 128 or dds[:4] != b"DDS ":
        raise RuntimeError("static-world texture is not an AYA-wrapped DDS image")
    height = struct.unpack_from("<I", dds, 12)[0]
    width = struct.unpack_from("<I", dds, 16)[0]
    fourcc = dds[84:88]
    compression = {b"DXT1": "Dxt1", b"DXT2": "Dxt2"}.get(fourcc)
    if (
        compression is None
        and fourcc == b"\0\0\0\0"
        and struct.unpack_from("<I", dds, 80)[0] == 0x41
        and struct.unpack_from("<I", dds, 88)[0] == 32
        and struct.unpack_from("<IIII", dds, 92)
        == (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    ):
        compression = "Rgba8"
    if compression is None or width not in (64, 128, 256, 512) or height != width:
        raise RuntimeError("static-world texture has unsupported dimensions or compression")
    return width, height, compression


def _source_aggregate(source_data: dict[Path, bytes]) -> str:
    rows = [
        f"{path.as_posix()}|{len(data)}|{_sha256(data)}"
        for path, data in source_data.items()
    ]
    rows.sort(key=str.casefold)
    return _sha256(("\n".join(rows) + "\n").encode("utf-8"))


def _materialize_static_world(
    game_root: Path,
    raw_level: bytes,
    stage: Path,
) -> tuple[tuple[Path, str], ...]:
    tools_root = ROOT / "tools"
    rebuild_tools = ROOT / "rebuild/tools"
    sys.path.insert(0, str(tools_root))
    sys.path.insert(0, str(rebuild_tools))
    from aya_archive_inventory import build_asset_resolver, inflate_aya_bytes
    from cmsh_static_preview import convert_aya_bytes, inflate_aya, parse_cmsh_stream

    objects, pines, fern_count = _parse_static_world(raw_level)
    texture_blend_flags = _texture_blend_alpha_flags(raw_level)
    resolver = build_asset_resolver(game_root / "data/resources")
    source_data: dict[Path, bytes] = {}
    texture_blend_by_source: dict[Path, bool] = {}
    mesh_inputs: dict[
        str,
        tuple[
            Path,
            bytes,
            dict[str, tuple[tuple[Path, float, float, float, float, float] | None, ...]],
        ],
    ] = {}

    for mesh_key in STATIC_MESH_KEYS:
        matches = resolver.mesh_index.get(f"{mesh_key}.msh".lower(), [])
        if len(matches) != 1:
            raise RuntimeError(f"expected one exact loose mesh for {mesh_key}, found {len(matches)}")
        source_path = Path(matches[0])
        relative = source_path.relative_to(game_root)
        data = source_path.read_bytes()
        parsed = parse_cmsh_stream(inflate_aya(data))
        signatures = sorted(
            {group.raw_texr_u32 for part in parsed.parts for group in part.groups}
        )
        referenced_indices = sorted(
            {
                texture_index
                for signature in signatures
                for texture_index in signature
                if texture_index != 0xFFFFFFFF
            }
        )
        texture_source_by_index: dict[int, Path] = {}
        for texture_index in referenced_indices:
            if texture_index >= len(parsed.textures):
                raise RuntimeError(f"{mesh_key} has an unresolved material texture")
            texture_ref = parsed.textures[texture_index].name
            normalized_ref = texture_ref.lstrip("?").replace("/", "\\").strip().lower()
            texture_matches = resolver.texture_index.get(normalized_ref, [])
            if len(texture_matches) != 1:
                raise RuntimeError(
                    f"expected one exact texture for {mesh_key} {texture_ref}, found {len(texture_matches)}"
                )
            texture_path = Path(texture_matches[0])
            texture_relative = texture_path.relative_to(game_root)
            texture_data = texture_path.read_bytes()
            source_data.setdefault(texture_relative, texture_data)
            if source_data[texture_relative] != texture_data:
                raise RuntimeError("static-world texture changed during materialization")
            if normalized_ref not in texture_blend_flags:
                raise RuntimeError(
                    f"Level 100 has no CTexture mode for {texture_ref}"
                )
            blend_flag = texture_blend_flags[normalized_ref]
            previous_blend = texture_blend_by_source.setdefault(
                texture_relative,
                blend_flag,
            )
            if previous_blend != blend_flag:
                raise RuntimeError(
                    f"Level 100 CTexture mode disagrees for {texture_ref}"
                )
            texture_source_by_index[texture_index] = texture_relative

        materials: dict[
            str,
            tuple[tuple[Path, float, float, float, float, float] | None, ...],
        ] = {}
        for signature in signatures:
            if signature[0] == 0xFFFFFFFF:
                raise RuntimeError(f"{mesh_key} has no base material texture")
            layers: list[tuple[Path, float, float, float, float, float] | None] = []
            for texture_index in signature:
                if texture_index == 0xFFFFFFFF:
                    layers.append(None)
                    continue
                metadata = _texture_pass_metadata(
                    parsed.textures[texture_index].raw_texb_metadata
                )
                layers.append((texture_source_by_index[texture_index], *metadata))
            materials[_material_surface_name(signature)] = tuple(layers)
        source_data[relative] = data
        mesh_inputs[mesh_key] = (relative, data, materials)

    water_sources: dict[str, Path] = {}
    for key, source_name, expected_hash in WATER_TEXTURES:
        source = Path(source_name)
        source_data[source] = _read_exact(game_root / source, expected_hash)
        water_sources[key] = source
    if len(source_data) != 61:
        raise RuntimeError(f"static-world source set has {len(source_data)} files instead of 61")
    aggregate = _source_aggregate(source_data)
    if aggregate != STATIC_WORLD_SOURCE_AGGREGATE_SHA256:
        raise RuntimeError(f"unsupported static-world source set (aggregate SHA-256 {aggregate})")

    texture_records: dict[str, dict[str, object]] = {}
    texture_key_by_source: dict[Path, str] = {}
    outputs: list[tuple[Path, str]] = []
    texture_sources = {
        layer[0]
        for _, _, materials in mesh_inputs.values()
        for layers in materials.values()
        for layer in layers
        if layer is not None
    }
    texture_sources.update(water_sources.values())
    for source in sorted(texture_sources, key=lambda value: value.as_posix().casefold()):
        water_key = next(
            (key for key, value in water_sources.items() if value == source),
            None,
        )
        key = water_key or _texture_key(source.name.split("(0)", 1)[0])
        if key in texture_records:
            raise RuntimeError(f"static-world texture key is not unique: {key}")
        data = source_data[source]
        width, height, compression = _dds_metadata(data, inflate_aya_bytes)
        destination = STATIC_WORLD_ROOT / "Textures" / f"{key}.texture.aya"
        resource_path = f"res://Assets/Level100/StaticWorld/Textures/{key}.texture.aya"
        target = stage / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        output_hash = _sha256(data)
        outputs.append((destination, output_hash))
        texture_key_by_source[source] = key
        texture_records[key] = {
            "blendTextureAlpha": texture_blend_by_source.get(source, False),
            "compression": compression,
            "height": height,
            "resourcePath": resource_path,
            "sha256": output_hash,
            "sourcePath": source.as_posix(),
            "width": width,
        }

    mesh_records: dict[str, dict[str, object]] = {}
    for mesh_key in STATIC_MESH_KEYS:
        source, data, materials = mesh_inputs[mesh_key]
        obj = convert_aya_bytes(
            data,
            include_vertex_attributes=True,
            include_material_layer_groups=True,
        )
        vertex_z = [
            float(line.split()[3])
            for line in obj.decode("utf-8").splitlines()
            if line.startswith("v ")
        ]
        if not vertex_z or not all(math.isfinite(value) for value in vertex_z):
            raise RuntimeError(f"static-world mesh {mesh_key} has invalid converted bounds")
        slug = _slug(mesh_key)
        destination = STATIC_WORLD_ROOT / "Meshes" / f"{slug}.obj"
        resource_path = f"res://Assets/Level100/StaticWorld/Meshes/{slug}.obj"
        target = stage / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(obj)
        output_hash = _sha256(obj)
        outputs.append((destination, output_hash))
        mesh_records[mesh_key] = {
            "baseClearance": -min(vertex_z),
            "materials": {
                surface: {
                    "layers": [
                        None
                        if layer is None
                        else {
                            "offset": [layer[2], layer[3]],
                            "opacity": layer[1],
                            "scale": [layer[4], layer[5]],
                            "texture": texture_key_by_source[layer[0]],
                        }
                        for layer in layers
                    ]
                }
                for surface, layers in sorted(materials.items())
            },
            "resourcePath": resource_path,
            "sha256": output_hash,
            "sourcePath": source.as_posix(),
        }

    hfld = _extract_chunk(
        raw_level,
        b"HFLD",
        668660,
        "7a4c7c5b9400e2c8d2325cecb5c44701cd8a6e6f8609cbc8bc31d449c0620f5d",
    )
    water_level_bits = struct.unpack_from("<I", hfld, 16 + 0x1034)[0]
    water_texture_index = hfld[16 + 0x1095]
    if water_level_bits != 0xC10D70A4 or water_texture_index != 0:
        raise RuntimeError("Level 100 water selection does not match the released HFLD")

    water_surface = _extract_chunk(
        raw_level,
        b"SURF",
        18_572,
        WATER_SURFACE_SHA256,
    )
    water_surface_target = stage / WATER_SURFACE_RESOURCE
    water_surface_target.parent.mkdir(parents=True, exist_ok=True)
    water_surface_target.write_bytes(water_surface)
    outputs.append((WATER_SURFACE_RESOURCE, WATER_SURFACE_SHA256))

    manifest = {
        "meshes": mesh_records,
        "objects": objects,
        "pineInstanceCount": len(pines),
        "pines": pines,
        "schema": "onslaught.level100-static-world.v4",
        "sourceAggregateSha256": aggregate,
        "sourceArchiveSha256": LEVEL_ARCHIVE_SHA256,
        "suppressedFernCount": fern_count,
        "textures": texture_records,
        "unitRecordCount": 35,
        "visibleObjectCount": len(objects),
        "water": {
            "causticTexture": "water-caustic-00",
            "level": struct.unpack("<f", struct.pack("<I", water_level_bits))[0],
            "reflectionTexture": "water-reflection-00",
            "sunBlobTexture": "water-sun-blob",
            "sunReflectionTexture": "water-sun-reflection",
            "surfaceResourcePath": (
                "res://Assets/Level100/StaticWorld/Source/"
                "level100-water-surface.surf.bin"
            ),
            "surfaceSha256": WATER_SURFACE_SHA256,
            "textureIndex": water_texture_index,
            "wavesTexture": "water-waves",
        },
    }
    manifest_bytes = (
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    manifest_hash = _sha256(manifest_bytes)
    if manifest_hash != STATIC_WORLD_MANIFEST_SHA256:
        raise RuntimeError(
            f"static-world manifest did not reproduce exactly (SHA-256 {manifest_hash})"
        )
    manifest_target = stage / STATIC_WORLD_MANIFEST
    manifest_target.parent.mkdir(parents=True, exist_ok=True)
    manifest_target.write_bytes(manifest_bytes)
    outputs.append((STATIC_WORLD_MANIFEST, manifest_hash))
    return tuple(outputs)


def _xap_records(data: bytes) -> list[tuple[str, int, bytes]]:
    if len(data) < 8 or data[:4] != b"PCXP":
        raise RuntimeError("unsupported English XAP framing")
    count = struct.unpack_from("<I", data, 4)[0]
    if count != 164:
        raise RuntimeError(f"unsupported English XAP record count: {count}")
    records: list[tuple[str, int, bytes]] = []
    offset = 8
    for index in range(count):
        if offset + 72 > len(data) or data[offset : offset + 4] != b"PSMP":
            raise RuntimeError(f"unsupported PSMP framing at record {index}")
        name = data[offset + 4 : offset + 68].split(b"\0", 1)[0].decode("ascii")
        decoded_size = struct.unpack_from("<I", data, offset + 68)[0]
        packed_size = (decoded_size + 3) // 4
        end = offset + 72 + packed_size
        if end > len(data):
            raise RuntimeError(f"truncated PSMP record {index}")
        records.append((name, decoded_size, data[offset + 72 : end]))
        offset = end
    if offset != len(data):
        raise RuntimeError("unexpected trailing English XAP data")
    return records


def _decode_ima_high_nibble_first(packed: bytes, decoded_size: int) -> bytes:
    predictor = 0
    step_index = 0
    output = bytearray()
    for value in packed:
        for nibble in (value >> 4, value & 0x0F):
            step = IMA_STEP_TABLE[step_index]
            delta = step >> 3
            if nibble & 1:
                delta += step >> 2
            if nibble & 2:
                delta += step >> 1
            if nibble & 4:
                delta += step
            predictor += -delta if nibble & 8 else delta
            predictor = max(-32768, min(32767, predictor))
            step_index = max(0, min(88, step_index + IMA_INDEX_TABLE[nibble & 7]))
            output.extend(struct.pack("<h", predictor))
    if len(output) < decoded_size:
        raise RuntimeError("decoded PSMP output is shorter than declared")
    return bytes(output[:decoded_size])


def _pcm_wav(pcm: bytes) -> bytes:
    return (
        b"RIFF"
        + struct.pack("<I", 36 + len(pcm))
        + b"WAVEfmt "
        + struct.pack("<IHHIIHH", 16, 1, 1, 44100, 88200, 2, 16)
        + b"data"
        + struct.pack("<I", len(pcm))
        + pcm
    )


def _materialize(game_root: Path, stage: Path) -> tuple[tuple[Path, str], ...]:
    source_data: dict[Path, bytes] = {}
    for destination, source, expected in DIRECT_ASSETS:
        data = _read_exact(game_root / source, expected)
        source_data[destination] = data
        target = stage / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    level_archive = _read_exact(game_root / LEVEL_ARCHIVE, LEVEL_ARCHIVE_SHA256)
    tools_root = ROOT / "tools"
    sys.path.insert(0, str(tools_root))
    from aya_archive_inventory import inflate_aya_bytes

    raw_level = inflate_aya_bytes(level_archive)
    for destination, tag, expected_size, expected in CHUNKS:
        data = _extract_chunk(raw_level, tag, expected_size, expected)
        target = stage / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    rebuild_tools = ROOT / "rebuild/tools"
    sys.path.insert(0, str(rebuild_tools))
    from cmsh_static_preview import convert_aya_bytes

    for destination, source_destination, frame, expected in MESHES:
        data = convert_aya_bytes(
            source_data[source_destination],
            include_vertex_attributes=True,
            include_material_layer_groups=True,
            hierarchy_frame=frame,
        )
        if _sha256(data) != expected:
            raise RuntimeError(f"derived mesh did not reproduce exactly: {destination}")
        target = stage / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    bank = _read_exact(game_root / SOUND_BANK, SOUND_BANK_SHA256)
    records = _xap_records(bank)
    for destination, record_index, expected_name, expected in SOUNDS:
        name, decoded_size, packed = records[record_index]
        if name != expected_name:
            raise RuntimeError(f"unexpected PSMP name at record {record_index}: {name}")
        data = _pcm_wav(_decode_ima_high_nibble_first(packed, decoded_size))
        if _sha256(data) != expected:
            raise RuntimeError(f"decoded sound did not reproduce exactly: {destination}")
        target = stage / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    static_world_outputs = _materialize_static_world(game_root, raw_level, stage)
    all_outputs = _fixed_outputs() + static_world_outputs
    for relative, expected in all_outputs:
        if _sha256((stage / relative).read_bytes()) != expected:
            raise RuntimeError(f"staged retail asset failed final verification: {relative}")
    return all_outputs


def _publish(stage: Path, outputs: tuple[tuple[Path, str], ...]) -> None:
    for relative, expected in outputs:
        source = stage / relative
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(f".{destination.name}.materializing")
        try:
            shutil.copyfile(source, temporary)
            if _sha256(temporary.read_bytes()) != expected:
                raise RuntimeError(f"publication verification failed: {relative}")
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize the exact retail assets used by the rebuild")
    parser.add_argument("--game-root", type=Path, help="Battle Engine Aquila retail installation root")
    parser.add_argument("--force", action="store_true", help="reverify source data and regenerate every asset")
    args = parser.parse_args()

    if not args.force and args.game_root is None and _outputs_ready():
        print(f"retail rebuild assets ready: {len(_all_outputs(ROOT))} exact files")
        return 0

    try:
        game_root = _resolve_game_root(args.game_root)
        work_root = ROOT / "local-lab/rebuild-godot"
        work_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="materialize-retail-", dir=work_root) as temporary:
            stage = Path(temporary)
            outputs = _materialize(game_root, stage)
            _publish(stage, outputs)
        if not _outputs_ready():
            raise RuntimeError("published retail assets failed final verification")
    except (OSError, RuntimeError, UnicodeError, ValueError) as error:
        print(f"retail asset materialization failed: {error}", file=sys.stderr)
        return 2

    print(f"retail rebuild assets materialized: {len(_all_outputs(ROOT))} exact files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
