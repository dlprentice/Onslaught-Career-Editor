#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Materialize the exact retail inputs consumed by the current rebuild slice.

The current source tree and release packages do not include these files. This
bounded recipe reads a user-provided Battle Engine Aquila installation,
verifies the supported Steam data, and writes only the known frontend,
Level 100, and Aquila assets to ignored paths.
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
LEVEL100_SCRIPT_ROOT = CORE_ASSETS / "Level100/Scripts"
LEVEL100_SCRIPT_OBJECTS = (
    ("AirborneDrone1", 920, "7209f0752e4715d1b3dbd9d102cda997f65b3d4ff38a37a5c382d4bb5f364f28"),
    ("AirborneDrone2", 952, "6491cb323adb7758176c0afce12ec8d84e025323bdc4014f1f452c881102ed17"),
    ("AirTrainer", 625, "9549f63b5bd964dfafb1cd002685144311db2e53b01d79b8a1be47d68f0da9d7"),
    ("BattleEngine", 990, "b68d9e176051f6fec4fb84d344c51998047cf635a40dd56cc87c30ec1156ab26"),
    ("Facilities", 564, "3f19d9cb84a06a898aea98cf2236301f4b81739c874a018093ca8f1e3a9b6ed2"),
    ("FiringRange", 913, "8b05629d4a350005322333c1442e068f3f50707e65ab810c665c82f34bd7a7c9"),
    ("Flyby", 394, "20039756aba7f0b79a5f9bccc3c45f6b17a0e6ec27e05b406f4c40c3254e1444"),
    ("Hangar", 3419, "f5d42f5c58e9874d97965971b7e2a7cdede12a039eaf3ab699965da61568d073"),
    ("LevelScript", 20586, "73eb349b9c4b5c5d7294b2183cd4d4aebe024c5d3c8cda9be685bd1463ed6fb1"),
    ("Setup", 2402, "986e2b60afa62df15c9ad52fc04538a8eab8473a4eab46fc1844e67d7a85d1e0"),
    ("StaticTarget", 1011, "6670ab8cf964b037fb29f4feff19790a1e15c9fc45504e71fc259eadda9e8a54"),
    ("StaticTarget2", 1016, "28281145def2cdd0576b4ab9c6cb9e47f36c37f59397b3a941f46b15f334b8c3"),
    ("TankFactory", 3790, "44577134d213c3e8362fcedfe8344cbc3ac1346623f89408a16d32d685703892"),
    ("TargetTank1", 1278, "50839be04b6d72e29ecf6b1519c43baa9f826cda3d3c1bd0ebe56eedc292d305"),
    ("TargetTank2", 739, "331a5ecdf7122014d3eb70827f30b348ba2d8c80a58971c4764d040b4da7dc09"),
    ("TargetTruck1", 1299, "cca2f36f70d0751e62cf5a66e4fc23a12a2f77d98f9eb8579f28d8625e72ebbb"),
    ("TargetTruck2", 1299, "7c00c14b9de87873f21848cd28696a331cf0b5902548988030ef3192c438a2b6"),
    ("TargetTruck3", 1299, "8b864edfa626bbb9f45e06c6cc73b71d6b68c3ae41469fc4cd61a453d0386c52"),
    ("TargetZone1", 969, "50269961be899b4f50025300ff1af8bb220437b36f9e8bce1cd2806e7617d56c"),
    ("TargetZone2", 1092, "8a4b727dcf0f9e249c7c1ab0155326004356f0ad5dd84f226148db794a884af3"),
    ("TargetZone3", 1118, "222c44814482a69ff716b785d01a0bc7b508f19fc60774f2067db5d8bd1ca90d"),
    ("TargetZone4", 1092, "026a70263ede8daaed00d324dbe13160bcb4882a10e10f7bfe384f62896b2e8f"),
    ("Transporter", 408, "15cf230e674d80bb92fecefc4f16c708d3c969c02aa1384c4142de47dbf35a5f"),
    ("Turret", 835, "462614eaa5222bd3be759d4b8d0217d695c3afbbf36e334fbdc256a906797c71"),
    ("Weather", 540, "369ca18aba315a853404779b931d45bed0d692d5bad38536a41c4d4706650ce4"),
)
LEVEL100_SCRIPT_SHA256 = {name: sha256 for name, _, sha256 in LEVEL100_SCRIPT_OBJECTS}
BASE_ARCHIVE = "data/resources/base_res_PC.aya"
BASE_ARCHIVE_SHA256 = "0ee8530874425cac759834872f5941bc4be086c40ce6b70553b5c6b539802883"
SOUND_BANK = "data/sounds/sounds_english_pc.xap"
SOUND_BANK_SHA256 = "658c15e3bab844d65dd3c07c4ac880f16f741c0ea116f48c603449bbd4dda8b7"
PHYSICS_DEFINITIONS = "data/default physics.dat"
PHYSICS_DEFINITIONS_SHA256 = (
    "e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14"
)
ENGLISH_LANGUAGE_TABLE = "data/language/english.dat"
ENGLISH_LANGUAGE_TABLE_SHA256 = (
    "789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a"
)
LEVEL100_MISSION_DATA_ROOT = GODOT_ASSETS / "Level100/MissionData"
LEVEL100_LEVEL_SCRIPT = LEVEL100_MISSION_DATA_ROOT / "LevelScript.msl"
LEVEL100_LEVEL_SCRIPT_SHA256 = (
    "d51f8864564b5bde872092ec822df5af49daac16563f500719135f1a8c6c04a4"
)
LEVEL100_ENGLISH_SOURCE = LEVEL100_MISSION_DATA_ROOT / "English.txt"
LEVEL100_ENGLISH_SOURCE_SHA256 = (
    "ee48f3bed1c3c872ccc975146318aa0b5da3df88bff6b0a60671f0d23f9ce478"
)
LEVEL100_TEXT_STF = LEVEL100_MISSION_DATA_ROOT / "text.stf"
LEVEL100_TEXT_STF_SHA256 = (
    "fd318d6c2304eb8ffcfa718357c1715aadad69915f39851b19f442d8263b56ae"
)
LEVEL100_ENGLISH_DAT = LEVEL100_MISSION_DATA_ROOT / "english.dat"
LEVEL100_ENGLISH_DAT_SHA256 = ENGLISH_LANGUAGE_TABLE_SHA256
LEVEL100_HUD_MANIFEST = LEVEL100_MISSION_DATA_ROOT / "level100-hud-events.json"
LEVEL100_HUD_MANIFEST_SHA256 = (
    "3e1992bc9d8ac8033f23a8f5894eddba60279a4a8348b1a319f28ee9c5b7b6d7"
)
FRONTEND_LOCALIZATION = GODOT_ASSETS / "Frontend/english.json"
FRONTEND_LOCALIZATION_SHA256 = (
    "b27d7b1b3f8cd8aa22b664cacf7c87a8b0907c7dea4c4f07dff8da763dbb70f3"
)
ROOT_TERRAIN_TEXTURE = (
    GODOT_ASSETS / "Level100/Source/level100-root-terrain.rgb565.bin"
)
# Exact initial root texture produced by the released compositor reconstructed
# below. The materializer refuses to publish if those pixels do not reproduce.
ROOT_TERRAIN_TEXTURE_SHA256 = (
    "6eb202f450926097930bedca440f0163a1886572981e3c69b4edf9289a68ae2b"
)
TERRAIN_HIERARCHY_SOURCE = (
    GODOT_ASSETS / "Level100/Source/level100-terrain-hierarchy.bin"
)
# Compact runtime source for the five released 512x512 logical landscape
# caches. This contains only the exact indexed MAPT levels and the Level 100
# mixer/lighting/shadow records needed to rebuild camera-local cache tiles.
TERRAIN_HIERARCHY_SOURCE_SHA256 = (
    "541eacd0aa75fae8befb8a3e1505ea52ae6b1f6c1367c15c65d7dd23b7cfe977"
)

LANDSCAPE_MAP_TEXTURES = (
    # Logical cache level, source width, framed MAPT size, exact framed hash.
    (0, 16, 7_788, "04aa2a1630e427a2916c5d3a4ba2be676d5b575022f559de1753d2101727b711"),
    (1, 32, 12_396, "cf7ed8810bd323d404c88e66bcc6789dc30b1179b4270551cd04423022c2ef77"),
    (2, 64, 30_828, "ec9d2f0dbaff2189610a98aa4aac5845463bff55db4b9919b1ee1b94facd269f"),
    (3, 128, 104_556, "dc29acbb0941515080e55c2679de84fc4604f59eed4294a28f471dfeed9b5edb"),
    (4, 256, 399_468, "c21576ae7ea75fa800ab4117c1479aeb70359a1acc84edd9508895eb339612f1"),
)
STATIC_WORLD_ROOT = GODOT_ASSETS / "Level100/StaticWorld"
STATIC_WORLD_MANIFEST = STATIC_WORLD_ROOT / "level100-static-world.json"
STATIC_WORLD_MANIFEST_SHA256 = "084954c97502001d5868348ac9db4e79d86f3dd8f72e3435e87fa43ff0141117"
STATIC_WORLD_SOURCE_AGGREGATE_SHA256 = (
    "67015b3f37422e18116b84b6245958509e847f09d27f696145ae88fb88fb3f2c"
)
LEVEL100_CONTACT_ASSET = (
    CORE_ASSETS / "Level100/level100-contact-owners.json"
)
LEVEL100_CONTACT_ASSET_SHA256 = (
    "fe5f109526e39231ea3d02898a035dbc7eb842b7b37776ec5efda7ba45f138b0"
)
# Aggregate of the 24 collision-bearing facility meshes only. The accepted
# static-world aggregate above additionally owns the four tree meshes.
LEVEL100_CONTACT_SOURCE_AGGREGATE_SHA256 = (
    "8d85c9bfbe366c815e00d3900d8d29b71a33bef7a60cddfce9ed6ac558e06b4c"
)
PINE_IMPOSTER_TEXTURE = (
    "data/resources/dxtntextures/Imposters_100(0)A1R5G5B5.aya",
    "7368ba0c586221ff1b1572cee8f84de2bf6db426c005a73a10bad54a938ad882",
)
# The bounded high-quality reconstruction profile selects the released value
# persisted at defaultoptions.bea OptionsTail +0x0C (file offset 0x26CA).
PINE_MESH_QUALITY_DISTANCE = 70.0
# Steam's fast standing view is address-derived, but the exact runtime owner
# sequence and phase are unresolved. This reconstruction-owned phase makes the
# four-view assignment deterministic without inferring a retail heap identity.
PINE_FAST_STANDING_VIEW_PHASE = 0
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
PINE_MESH_KEYS = tuple(f"pinesnow{variant}" for variant in range(4))
STATIC_MESH_KEYS = tuple(dict.fromkeys(STATIC_MESH_BY_DEFINITION.values())) + PINE_MESH_KEYS
PINE_MESH_SHA256 = (
    "d428a6ed49d460a5729c357618c3837e399e7d265ae6127899cd1911eb7a0481",
    "51984637f702b0215f0bd841977d8c9602201fb9f8392f7b110e285cde1ed102",
    "d717735ac741f7267b746546feebece60e7515048c0fdf46586c79e85c4087eb",
    "f9f5031421b5c9913a2f8865cabe31feb25e692e0c33934e1a537ab675793b3a",
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
    (LEVEL100_LEVEL_SCRIPT, "data/MissionScripts/level100/LevelScript.msl", LEVEL100_LEVEL_SCRIPT_SHA256),
    (LEVEL100_ENGLISH_SOURCE, "data/MissionScripts/level100/English.txt", LEVEL100_ENGLISH_SOURCE_SHA256),
    (LEVEL100_TEXT_STF, "data/MissionScripts/text/text.stf", LEVEL100_TEXT_STF_SHA256),
    (LEVEL100_ENGLISH_DAT, ENGLISH_LANGUAGE_TABLE, LEVEL100_ENGLISH_DAT_SHA256),
    (GODOT_ASSETS / "Hud/bar-line.texture.aya", "data/resources/dxtntextures/hud%v2%BarLine.tga(0)X8R8G8B8.aya", "16796e3a8acfec3529e03c29afbefbe28c92ffccd5b05574f992e8f31976704d"),
    (GODOT_ASSETS / "Hud/battleline-marker.texture.aya", "data/resources/dxtntextures/hud%marker.tga(0)A8R8G8B8.aya", "ab14538237bdd38486add4f5e9f38cfca0069496ceee5faf1268e50eab319be7"),
    (GODOT_ASSETS / "Hud/battleline-outline.texture.aya", "data/resources/dxtntextures/hud%v2%BattleLineOutline.tga(0)X8R8G8B8.aya", "b1c097b29dd81e2a0493f72a157ccd5ad249b5abf758224c75df4f93973d0405"),
    (GODOT_ASSETS / "Hud/circle-darkener.texture.aya", "data/resources/dxtntextures/hud%v2%CircleDarkener.tga(0)A8R8G8B8.aya", "7bd18594757165dcdd8dadb618ea99eb500ed105dbe2d6a6f66bbcbc31c323a3"),
    (GODOT_ASSETS / "Hud/circle-mask.texture.aya", "data/resources/dxtntextures/hud%v2%CircleMask.tga(0)A8R8G8B8.aya", "14d809f9b45f5153f82fa1f80152690b554710d83f91b8cbe203de5cf18a9dfa"),
    (GODOT_ASSETS / "Hud/compass-objective-marker.texture.aya", "data/resources/dxtntextures/hud%v2%CompassObjectiveMarker.tga(0)A8R8G8B8.aya", "e24fca83de34646a7328c313e7b89ac02c6bc4b04a69a74bf3ee81b3d57283df"),
    (GODOT_ASSETS / "Hud/crosshair-dot.texture.aya", "data/resources/dxtntextures/hud%v3%hud_crosshair_dot.tga(0)A8R8G8B8.aya", "19e1b35b885a36230e5a1d47a9910164b0ca177746649a15c146cefca29651dd"),
    (GODOT_ASSETS / "Hud/crosshair-enemy.texture.aya", "data/resources/dxtntextures/hud%Crosshair Enemy.tga(0)A8R8G8B8.aya", "6a5c0d6dc22ea911ba783e630b5f623ab027ff45da094c5816263f7b87db98ea"),
    (GODOT_ASSETS / "Hud/crosshair-friend.texture.aya", "data/resources/dxtntextures/hud%Crosshair Friend.tga(0)A8R8G8B8.aya", "75b827ac9560846ad85904032249f707d84a74a432d3b732116f0e89a3621895"),
    (GODOT_ASSETS / "Hud/crosshair-outline.texture.aya", "data/resources/dxtntextures/hud%Crosshair Outline.tga(0)A8R8G8B8.aya", "1e27b9771f3d0416c07eff9aede6863ca6f081386c86259f635e3d9a02ade5b2"),
    (GODOT_ASSETS / "Hud/crosshair-predictor.texture.aya", "data/resources/dxtntextures/hud%Crosshair Predictor.tga(0)A8R8G8B8.aya", "519b30e4edee809d3fe660ccb866feeea2ace4485b75373c98293afb6e730aa5"),
    (GODOT_ASSETS / "Hud/crosshair-primary.texture.aya", "data/resources/dxtntextures/hud%v3%hud_crosshair_primary.tga(0)A8R8G8B8.aya", "310dae2f7dd976f6cc724604737726885aff96ab6bc507e41f90dca60d134b17"),
    (GODOT_ASSETS / "Hud/crosshair-secondary.texture.aya", "data/resources/dxtntextures/hud%v3%hud_crosshair_secondary.tga(0)A8R8G8B8.aya", "7b078344e64d1e78ef64a8e21bdd3787e059b628c6a442634e9d13ba7d3a0487"),
    (GODOT_ASSETS / "Hud/damage-flash.texture.aya", "data/resources/dxtntextures/hud%v2%DamageFlash.tga(0)X8R8G8B8.aya", "8a25ec2e0ba8e66d86217684125d2e245dae3eddeb327ee2a7b144e2b45391c0"),
    (GODOT_ASSETS / "Hud/dial.raw", "data/Dial.raw", "2c57b657b92cd8bd73ca8c8986e8ce60aaffb065fdde09940053a2dd6d59671c"),
    (GODOT_ASSETS / "Hud/font-13ps.texture.aya", "data/resources/textures/mustbe_Font13PS.tga(0)A8R8G8B8.aya", "7acc088b75e729cbdc2782e239a7d18ba0ec409e1bc890109aa1020f5ee81dc0"),
    (GODOT_ASSETS / "Hud/font-22.texture.aya", "data/resources/textures/mustbe_font22.512.tga(0)A8R8G8B8.aya", "acc8dbdd60839c0f9686250025672cf9c370530114bc44910df09be487b247c6"),
    (GODOT_ASSETS / "Hud/guns-darken.texture.aya", "data/resources/dxtntextures/hud%v2%GunsDarken.tga(0)A8R8G8B8.aya", "0054e526a0980c5f89fc1271e7d34cfb551fc2567f6259f0be11d63100ab12b1"),
    (GODOT_ASSETS / "Hud/guns-front.texture.aya", "data/resources/dxtntextures/hud%v2%GunsFront.tga(0)X8R8G8B8.aya", "4ce73b693e83c01812ebca6ddd64edcfbebd4f85720ab7f5b87e425c9ece1a06"),
    (GODOT_ASSETS / "Hud/guns-outline.texture.aya", "data/resources/dxtntextures/hud%v2%GunsOutline.tga(0)X8R8G8B8.aya", "e80dc5fb51a2c29dc696d85b3bea036c427261d1bbe8f1db14a531fba996cffd"),
    (GODOT_ASSETS / "Hud/guns-side.texture.aya", "data/resources/dxtntextures/hud%v2%GunsSide.tga(0)X8R8G8B8.aya", "52d46b47d26d6c779fe8a7e0e77dc13f6bcf91849869ea9ec81c3fa190164594"),
    (GODOT_ASSETS / "Hud/guns-top.texture.aya", "data/resources/dxtntextures/hud%v2%GunsTop.tga(0)X8R8G8B8.aya", "d8b09af12efad59e9a25b91930bf9b8215f028c4e766eacc815c073a5e63304f"),
    (GODOT_ASSETS / "Hud/kramer-portrait-oo.texture.aya", "data/resources/dxtntextures/MessageBox%FC_Kramer_oo.tga(0)A8R8G8B8.aya", "f4887e775c5ebcac182b5caabae0c11ffe3fab8aa32ff14ddcd9ce33d1bd50b3"),
    (GODOT_ASSETS / "Hud/kramer-portrait-ee.texture.aya", "data/resources/dxtntextures/MessageBox%FC_Kramer_ee.tga(0)A8R8G8B8.aya", "0b34a213a25e0ebc48a74f8cf73cf27bbb817f4cdffbc79cd294a7d2858b9bde"),
    (GODOT_ASSETS / "Hud/kramer-portrait-mm.texture.aya", "data/resources/dxtntextures/MessageBox%FC_Kramer_mm.tga(0)A8R8G8B8.aya", "69ed961309997f300be094b6ba899d182b91c145fbf07f80fc2e0f8c8d149689"),
    (GODOT_ASSETS / "Hud/kramer-portrait.texture.aya", "data/resources/dxtntextures/MessageBox%FC_Kramer_aa.tga(0)A8R8G8B8.aya", "c6fe448e1d88e52c8abc0ad96c386b774b8d979ab07eb6ff2a4cbf069e99106b"),
    (GODOT_ASSETS / "Hud/message-noise.texture.aya", "data/resources/dxtntextures/MessageBox%noisebig.tga(0)X8R8G8B8.aya", "f5c43c330394db9eb7c1e782f3f30fe847de01d7ce9335d2c7f9fd24babb1825"),
    (GODOT_ASSETS / "Hud/objective-inner-centre.texture.aya", "data/resources/dxtntextures/hud%v2%ObjectiveInnerCentre.tga(0)A8R8G8B8.aya", "fc42774e8c4f4534b65009807bfdb333443a9f5202c6a2c59dff0dddbed4f55b"),
    (GODOT_ASSETS / "Hud/objective-inner-left.texture.aya", "data/resources/dxtntextures/hud%v2%ObjectiveInnerLeft.tga(0)A8R8G8B8.aya", "70030aace505e8e3d7f56dde0b9c6a929f3d2c61912fc03ac816746b6d8a96bd"),
    (GODOT_ASSETS / "Hud/objective-inner-right.texture.aya", "data/resources/dxtntextures/hud%v2%ObjectiveInnerRight.tga(0)A8R8G8B8.aya", "7c85b0293fc7a524978a21e7cdc06b1dd3308e9a595aadca054b51cd9a6aa113"),
    (GODOT_ASSETS / "Hud/objective-left.texture.aya", "data/resources/dxtntextures/hud%v2%ObjectiveLeft.tga(0)A8R8G8B8.aya", "0ae835780d1af6c01f0272a50afda141abca70eaa5c23d74e7fc3968b6d9194f"),
    (GODOT_ASSETS / "Hud/objective-right.texture.aya", "data/resources/dxtntextures/hud%v2%ObjectiveRight.tga(0)A8R8G8B8.aya", "581f10446db76ece7aa7044b4c02f0431a79a7d606225d5c69a412c17f85078b"),
    (GODOT_ASSETS / "Hud/radar-outline.texture.aya", "data/resources/dxtntextures/hud%v2%RadarOutline.tga(0)X8R8G8B8.aya", "507d465248f7321f2332413b2c6f461f3b3c45d87c52d86c38c43104043d7dc7"),
    (GODOT_ASSETS / "Hud/radio-north.texture.aya", "data/resources/dxtntextures/hud%v2%RadioNorth.tga(0)A8R8G8B8.aya", "e5dfd8db4dd73e9aeeffbb009fca68d889572c996987bce365b0b5b4d0a7ed85"),
    (GODOT_ASSETS / "Hud/radio-view.texture.aya", "data/resources/dxtntextures/hud%v2%RadioView.tga(0)A8R8G8B8.aya", "888d5a70ab812e23f75db76ab2ed71cd2cce04191ee282d525c86e337cc01778"),
    (GODOT_ASSETS / "Hud/scanner-blob-medium.texture.aya", "data/resources/dxtntextures/hud%ScannerBlobMedium.tga(0)A8R8G8B8.aya", "b7f9d3d0b6a2c80933673514b8d032589b1de2e4c60bcc362df39e6244d71853"),
    (GODOT_ASSETS / "Hud/scanner-blob-large.texture.aya", "data/resources/dxtntextures/hud%ScannerBlobLarge.tga(0)A8R8G8B8.aya", "791327844e9700103afad1572de3b4426e48088ed958033b227e256ffbed4152"),
    (GODOT_ASSETS / "Hud/scanner-blob-repair-pad.texture.aya", "data/resources/dxtntextures/hud%ScannerBlobRepairPad.tga(0)A8R8G8B8.aya", "bddf99cbdd816a5ecd32e04e01a1f2db356202b64015426e3aff446268ec6469"),
    (GODOT_ASSETS / "Hud/scanner-blob-small.texture.aya", "data/resources/dxtntextures/hud%ScannerBlobSmall.tga(0)A8R8G8B8.aya", "d7e9d287536f23e67bf35f678ec75d1a349353ae1d9d00b87ce09f6bd03641e4"),
    (GODOT_ASSETS / "Hud/screen-marker.texture.aya", "data/resources/dxtntextures/hud%v3%ScreenMarker.tga(0)X8R8G8B8.aya", "c5ec9c34386546a327a0e7188156e9a6b0259feda301320c111b1b7062c30a49"),
    (GODOT_ASSETS / "Hud/tatiana-portrait-oo.texture.aya", "data/resources/dxtntextures/MessageBox%tat_oo.tga(0)A8R8G8B8.aya", "39f40088069a8c68584a5a0cda9e5ae7d4e4e5a248a12f0d0a240b8d3668621e"),
    (GODOT_ASSETS / "Hud/tatiana-portrait-ee.texture.aya", "data/resources/dxtntextures/MessageBox%tat_ee.tga(0)A8R8G8B8.aya", "4a4a17b72bbafae2b324e3a0a1c847226a288feaa7c4273c45aa2de8aea3f99a"),
    (GODOT_ASSETS / "Hud/tatiana-portrait-mm.texture.aya", "data/resources/dxtntextures/MessageBox%tat_mm.tga(0)A8R8G8B8.aya", "802d8e22d8d304e12589a547f22ac2f2d5771b96aea47306b3b2bbf752730de5"),
    (GODOT_ASSETS / "Hud/tatiana-portrait.texture.aya", "data/resources/dxtntextures/MessageBox%tat_aa.tga(0)A8R8G8B8.aya", "34d451a6fc31e399b99032230413a60f146b41a0fea65e61561a37d8ec757cfd"),
    (GODOT_ASSETS / "Hud/technician-portrait-oo.texture.aya", "data/resources/dxtntextures/MessageBox%technic_oo.tga(0)A8R8G8B8.aya", "b28a3818b8ef37decfd8779d7acae74c657b5d510edd2332587864f2a1e58a2c"),
    (GODOT_ASSETS / "Hud/technician-portrait-ee.texture.aya", "data/resources/dxtntextures/MessageBox%technic_ee.tga(0)A8R8G8B8.aya", "05326c603e8c9224c5bab488a32ab9e9e19ca5b3fb424bc700af97ae71c2527f"),
    (GODOT_ASSETS / "Hud/technician-portrait-mm.texture.aya", "data/resources/dxtntextures/MessageBox%technic_mm.tga(0)A8R8G8B8.aya", "263a2c107d6463a717ddef20cc113cadfb585bd8ecbb1db479f049843dcf3636"),
    (GODOT_ASSETS / "Hud/technician-portrait.texture.aya", "data/resources/dxtntextures/MessageBox%technic_aa.tga(0)A8R8G8B8.aya", "c4c1b11f4ddfb960afc1c1d2a04020fadf997795eccf651c07314141652f9603"),
    (GODOT_ASSETS / "Hud/target-sighted.texture.aya", "data/resources/dxtntextures/hud%v3%hud_target_sighted.tga(0)A8R8G8B8.aya", "6caafcdc20228617b86bd7f4010e718e1d681ee52b0e904d73e6f16369bcaa88"),
    (GODOT_ASSETS / "Hud/threat-flash.texture.aya", "data/resources/dxtntextures/hud%v2%ThreatFlash.tga(0)X8R8G8B8.aya", "43f5fb70d318f4969f43147c225a399d233edcea577592f14876ac542bd57f50"),
    (GODOT_ASSETS / "Hud/weapon-fill.texture.aya", "data/resources/dxtntextures/hud%v2%WeaponFill.tga(0)A8R8G8B8.aya", "e639910d70ae10b044423cd5025c300c61cb8a9b5765890fd1a011c7d4499c0d"),
    (GODOT_ASSETS / "Hud/weapon-plasma-cannon.texture.aya", "data/resources/dxtntextures/hud%Weapon Plasma Cannon.tga(0)A8R8G8B8.aya", "d5165347be203c17f302250ae20e83ae5b9525938b15ca8c6aceb0d4392f06df"),
    (GODOT_ASSETS / "Hud/weapon-vulcan-cannon.texture.aya", "data/resources/dxtntextures/hud%Weapon Vulcan Cannon.tga(0)A8R8G8B8.aya", "20d3c6d31b2815af0b0a7de5aa993164d911ac527205b40892f19f07ee34f3b8"),
    (GODOT_ASSETS / "Hud/weapon-outline.texture.aya", "data/resources/dxtntextures/hud%v2%WeaponOutline.tga(0)X8R8G8B8.aya", "2e2da786db82c8fd76de36d8d71fe744ddddd364247467cba1bfb9a95e52d62b"),
    (GODOT_ASSETS / "Hud/offscreen-arrow.texture.aya", "data/resources/dxtntextures/hud%v3%offscreenarrow.tga(0)A8R8G8B8.aya", "8bbf5f0898a7796668e8a1a2bc6393c077b14beb7623585856709bdd937d35d2"),
    (GODOT_ASSETS / "PauseMenu/blank.texture.aya", "data/resources/dxtntextures/FrontEnd%v2%FE_Blank.tga(0)A8R8G8B8.aya", "01d55e16e994dec02191e6f62adcb5a82a1f0ca3b5629e489c9e5c82884fe7e9"),
    (GODOT_ASSETS / "PauseMenu/circle-01.texture.aya", "data/resources/dxtntextures/pausemenu%pause_circle01.tga(0)A8R8G8B8.aya", "01622d0e442aef1ccd5d5971cad5b4c06d2b15d1980dd07a1ddf95a7bc7472c7"),
    (GODOT_ASSETS / "PauseMenu/circle-02.texture.aya", "data/resources/dxtntextures/pausemenu%pause_circle02.tga(0)A8R8G8B8.aya", "4cd5e553a8a093d3a895f3639136fb6548267371c28914b00d3ccbb3c153516f"),
    (GODOT_ASSETS / "Level100/Sky/cube25-cent.texture.aya", "data/resources/dxtntextures/cubes%cube25_cent.tga(0)X8R8G8B8.aya", "1aad6cc8f85b6bb7ccbb8d2c7b0e6aa31722a9adbde5a3f19b248430ca83469e"),
    (GODOT_ASSETS / "Level100/Sky/cube25-down.texture.aya", "data/resources/dxtntextures/cubes%cube25_down.tga(0)X8R8G8B8.aya", "4770829ba631e93fbc33db2012754da75a06bfccc2fb2b36875e92032e22d19d"),
    (GODOT_ASSETS / "Level100/Sky/cube25-left.texture.aya", "data/resources/dxtntextures/cubes%cube25_left.tga(0)X8R8G8B8.aya", "d7cbce30e51473ddc89ed0c44326e598dac4d2682f64ef20c19237afd2cebe14"),
    (GODOT_ASSETS / "Level100/Sky/cube25-right.texture.aya", "data/resources/dxtntextures/cubes%cube25_right.tga(0)X8R8G8B8.aya", "830c9b965c76a4023c2415b7c8924ca32590562c850cc84e92c003e173263d11"),
    (GODOT_ASSETS / "Level100/Sky/cube25-up.texture.aya", "data/resources/dxtntextures/cubes%cube25_up.tga(0)X8R8G8B8.aya", "419e2424bcfd698058d72111ffa7d84fdc9022e03815db7c0da28403f4925f3c"),
    (GODOT_ASSETS / "Level100/Source/m_f_pulsetank_training.msh.aya", "data/resources/meshes/m_f_pulsetank_training.msh.aya", "9b2cfdceb86ed700ed924051fbff13c32dc30bd8f8b948ea1cf8aa9fbfe8b97b"),
    (GODOT_ASSETS / "Level100/Source/m_f_truck_training.msh.aya", "data/resources/meshes/m_f_truck_training.msh.aya", "3bd92ce93d0619b7c4b0dd158680641fbab6cd88580a68c6ef34e5f22f7596c5"),
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
    (GODOT_ASSETS / "Level100/Textures/target-truck.texture.aya", "data/resources/dxtntextures/meshtex%f_truck_training.tga(0)A1R5G5B5.aya", "ab4125242321de4963c51c9b22f63c951a33c22e874d8f039fa2c61a109f5e81"),
    (GODOT_ASSETS / "Level100/Textures/target-warehouse-m001.texture.aya", "data/resources/dxtntextures/meshtex%M_001.tga(0)A1R5G5B5.aya", "689b184ab8a5d03f33b69e5c35edcfdfdec12aa9b4b31f7c74ce5209f6236a49"),
    (GODOT_ASSETS / "Level100/Textures/target-warehouse-m002.texture.aya", "data/resources/dxtntextures/meshtex%M_002.tga(0)A1R5G5B5.aya", "8fabadbe1c5af067a740cf05debd1c952c628fd5fa3ea92b8202094704b8a20d"),
    (GODOT_ASSETS / "Level100/Textures/material-overlay-a8trust5.texture.aya", "data/resources/dxtntextures/meshtex%a8trust5.tga(0)A8R8G8B8.aya", "4ccde973f9741c110a82f350e102f1a12c566ff3d3b1b4f5426f2bbf536be843"),
    (GODOT_ASSETS / "Level100/Textures/terrain-cloud-shadow.texture.aya", "data/resources/dxtntextures/clouds%shadow.tga(0)A8R8G8B8.aya", "fc7441887e494e4b18f2b16179ed42c17801b128d71e29d653a4e8b792869519"),
    (GODOT_ASSETS / "Level100/Textures/terrain-detail-00.texture.aya", "data/resources/dxtntextures/mixers%detail00.tga(0)R5G6B5.aya", "7c9c22169d13ed8b7d6ad69286bdb59cc88f9ae3bfb6a9d3a0503d320386bfef"),
    (GODOT_ASSETS / "Level100/Music/tutorial-track-03.ogg", "data/Music/BEA_04(Master).ogg", "32d3e338964d74f50d0094536c585375f1e14aa2bae6087487803f3529eaf360"),
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
    (GODOT_ASSETS / "Level100/TutorialAudio/hud_03.ogg", "data/sounds/english/MessageBox/hud_03.ogg", "3d58ab5abf9715ee4b3c657bf3ca7c0b91c2985382a7d72c948513045669c31e"),
    (GODOT_ASSETS / "Level100/TutorialAudio/hud_04.ogg", "data/sounds/english/MessageBox/hud_04.ogg", "3b96aa4cf15202d2977d32a04e73715dc1e940e00596d1614acd47262c86e77d"),
    (GODOT_ASSETS / "Level100/TutorialAudio/hud_07.ogg", "data/sounds/english/MessageBox/hud_07.ogg", "8d75f5981abb9fc494eb77f0a721b38b8eb95083be9282e67561e4bf18e9a8d4"),
    (GODOT_ASSETS / "Level100/TutorialAudio/hud_08.ogg", "data/sounds/english/MessageBox/hud_08.ogg", "06e0c641803b25fe157e8fd27420e11be5972df3b0dcd80681926577c9b0c361"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_04.ogg", "data/sounds/english/MessageBox/tutorial_04.ogg", "78c04e99ff5ae90fb224fa2dffae6b3101123d32fe73e3c9ee6b37ec4d6482c6"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_05.ogg", "data/sounds/english/MessageBox/tutorial_05.ogg", "bd047bd04eeefeeca91ed1ae3244eb65f8fe26de33f81ba18bd9505bc4494c58"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_06.ogg", "data/sounds/english/MessageBox/tutorial_06.ogg", "d61f834ac1efe27ff6982d25a401cfc48dd7bfaf03ee38f3bdfadb0d819f11c1"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_07.ogg", "data/sounds/english/MessageBox/tutorial_07.ogg", "1d01bb7c56bc582944161b415cfb18518abbeb211067a0db62f80d70c587af7e"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_08.ogg", "data/sounds/english/MessageBox/tutorial_08.ogg", "a7888025d9db2094df63145e7d58b53be5054abf28c678f727155f6ed282c205"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_09.ogg", "data/sounds/english/MessageBox/tutorial_09.ogg", "d306048bb7d1680c4b5e3fd8b7a01f966725c1c4d7e4f9a09b9e9e25dcae7557"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_10.ogg", "data/sounds/english/MessageBox/tutorial_10.ogg", "89a881c253c9cbc5227e84e942b0c8c3361b5b6bd2694b61522bd97af320f5fb"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_11.ogg", "data/sounds/english/MessageBox/tutorial_11.ogg", "c46293ff014967f62d90f870cfe8a8fc228fcc7a0b5acb7cbe3d203341a39984"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_12.ogg", "data/sounds/english/MessageBox/tutorial_12.ogg", "e6cbf2cb4dabcfacec0479dee1eeb33ed62e1d3b46bf238b638d75aa55b7a425"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_aborted.ogg", "data/sounds/english/MessageBox/tutorial_aborted.ogg", "320b8a1e4619ddeecf94afd8862e8b90c7ebaba3fffd5b8976a3d6160497c1b5"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_broke_1.ogg", "data/sounds/english/MessageBox/tutorial_broke_1.ogg", "30e2e6652508c7b9bf13beb2f19cd0ed66ce474d677e946ceeebd30a905d6696"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_broke_2.ogg", "data/sounds/english/MessageBox/tutorial_broke_2.ogg", "8e6af2bd4038b89c72e45c8e86a5b5e32fba12f50728b82a26223918f6d96315"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_broke_3.ogg", "data/sounds/english/MessageBox/tutorial_broke_3.ogg", "57c3c737699b02d96cd2b9cb2e6b5e8d2f513c92b51e3b13b7728f9127bc8d8f"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_dodge_2.ogg", "data/sounds/english/MessageBox/tutorial_dodge_2.ogg", "d88eff763474bcff488ebf913b1d8b45900452f34331ef6db334c589768d66b2"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_dodge_3.ogg", "data/sounds/english/MessageBox/tutorial_dodge_3.ogg", "7796dd70479a91c48d027594bbfc1bb6c0206336006657c13c2220185be5c0a8"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_dodge_bad.ogg", "data/sounds/english/MessageBox/tutorial_dodge_bad.ogg", "b551c989f66c3c30e048a73f230dbabcf19e588cd93a95b37b5a2654569bcdd5"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_dodge_good.ogg", "data/sounds/english/MessageBox/tutorial_dodge_good.ogg", "329d8269262c2f4c25b95a4373ad932f53a09b26003238c9d6aa3d613e98669d"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_dodge_mod.ogg", "data/sounds/english/MessageBox/tutorial_dodge_mod.ogg", "c74568f49114f77cc42426cf029be35434bf8058f2d05b1d4b6adb73b124c3a5"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_help_player.ogg", "data/sounds/english/MessageBox/tutorial_help_player.ogg", "287998779062d08030350bfca83e625ac55d12bb75775d4cc59b1f9e3afb7b5c"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_landing.ogg", "data/sounds/english/MessageBox/tutorial_landing.ogg", "07428ce3bfc31603e472ba83affd1d355b0c3cabec24d8ad87e3fe30cc646176"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_strafe.ogg", "data/sounds/english/MessageBox/tutorial_strafe.ogg", "f6da37701ffd0ddc9cf2780c80674305459c552fea3d1f383b65ebc76565db70"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_throttle_mod.ogg", "data/sounds/english/MessageBox/tutorial_throttle_mod.ogg", "29d3791d61286318fdedb4bdc88c267488f647d65996a581fb3da91b2d2e2ef4"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_technician_02.ogg", "data/sounds/english/MessageBox/tutorial_technician_02.ogg", "196032dddadbe1cbfe3315635991c02e62b05cac083a90ad4dfaaebbab8eb955"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_technician_03.ogg", "data/sounds/english/MessageBox/tutorial_technician_03.ogg", "952d91a0a416a20487d790debcf82dde357935946fd7e4b69678cbd350d8681c"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_movement.ogg", "data/sounds/english/MessageBox/tutorial_movement.ogg", "79f7dda58130d4b8e506683f7cf65c9213dffca074885df06aaaa857b0c28340"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_weapon.ogg", "data/sounds/english/MessageBox/tutorial_weapon.ogg", "e1afe902725a81d9900a1d5bee65d7fdf47b61ab59246de7ecade89f2a9e7b00"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_overheat.ogg", "data/sounds/english/MessageBox/tutorial_overheat.ogg", "34a084751bafa8320fa0d8b34ed17b6f8fc3f38630b0caf6528a3287a39b8683"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_ammo.ogg", "data/sounds/english/MessageBox/tutorial_ammo.ogg", "1a7474ffd1aa2c88a56b60d4f27a77a3fea348abf24a17a9f6e3251308af8769"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_water.ogg", "data/sounds/english/MessageBox/tutorial_water.ogg", "99dc92041fb49bd4b06d0e875b3ded4155e2f4a8ba4aed9b40596ce0012d1151"),
    (GODOT_ASSETS / "Level100/TutorialAudio/tutorial_zoom.ogg", "data/sounds/english/MessageBox/tutorial_zoom.ogg", "d0aadac588017f5a410358494603f7e052890c93d6b52ddbc61cbe171cb6940b"),
)


# Small exact released frontend surface used by the startup -> Level 100 path.
FRONTEND_ASSETS = (
    (GODOT_ASSETS / "Frontend/Backgrounds/click-to-start.texture.aya", "data/resources/dxtntextures/FrontEnd%v2%fe_splash1.tga(0)A8R8G8B8.aya", "46ab45168875b5b686e3534b3f66ab65b5a5b5512f697e5a98b03dd12708731a"),
    (GODOT_ASSETS / "Frontend/Backgrounds/rock.texture.aya", "data/resources/dxtntextures/FrontEnd%v2%FE_Rock_Background.tga(0)A8R8G8B8.aya", "89213b441332f060acdb3e55aa28c290fa0e530983c16a57b8ce1a7413e9e86d"),
    (GODOT_ASSETS / "Frontend/title-logo.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_Title2.tga(0)A8R8G8B8.aya", "5ae9b300836d27bd13462a53e3455b649bb46bf8f48c8c326fd8f4f0c18c7ec7"),
    (GODOT_ASSETS / "Frontend/title-bracket-01.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_bracket01.tga(0)A8R8G8B8.aya", "679b5fa6220b3eb54aeef1d970890c35be5df264530226f5d08b22a63ad75064"),
    (GODOT_ASSETS / "Frontend/title-bracket-02.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_bracket02.tga(0)A8R8G8B8.aya", "79f05e8c64b6e25f038c5b7c37ddadfd31ee9376e92fc5da505b6c427ed9c74f"),
    (GODOT_ASSETS / "Frontend/title-text-box.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_text_box.tga(0)A8R8G8B8.aya", "c007742e1fe9b93e988d198f8a2a4e741e546843fd36218d9015ab2ee6627b9c"),
    (GODOT_ASSETS / "Frontend/symbol-bracket-01.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_symbol_bracket01.tga(0)A8R8G8B8.aya", "3243e641e9ad45cd8b80c4abebaa1e6f73b5ed774e0b4dba1afbcbbaf81a49a8"),
    (GODOT_ASSETS / "Frontend/symbol-bracket-02.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_symbol_bracket02.tga(0)A8R8G8B8.aya", "92739af94bec154d898afb5e59432694a789bb3f2c37242eb65272684daeb687"),
    (GODOT_ASSETS / "Frontend/Icons/new-game.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_nav_symbol_newgame01.tga(0)A8R8G8B8.aya", "d3ff62fbc8193e15bf250c82088f5088b17c667277dbb5fff92f2980cc3deb70"),
    (GODOT_ASSETS / "Frontend/Icons/continue-game.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_nav_symbol_continuegame01.tga(0)A8R8.aya", "83c9fa4d7e786ae4353d1f639c75b007bc0c65f1412b447d68967d9e5b4cca0e"),
    (GODOT_ASSETS / "Frontend/Icons/load-game.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_nav_symbol_loadgame01.tga(0)A8R8G8B8.aya", "9d1bb0d9efc450fc2bce244e01a2975468f07cf785bf6854a5bc9495fffdc001"),
    (GODOT_ASSETS / "Frontend/Icons/multiplayer.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_nav_symbol_multiplayer01.tga(0)A8R8G.aya", "8a7d7dba563b153b314e04daaad4ffa2d0969b65a0603de043027eaf5b4df031"),
    (GODOT_ASSETS / "Frontend/Icons/goodies.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_nav_symbol_goodies01.tga(0)A8R8G8B8.aya", "efa9ec1d2317e3cdf2ed9a90cc8b6cb391e6ed1099740ddaeb2c808b49f33358"),
    (GODOT_ASSETS / "Frontend/Icons/options.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_nav_symbol_options01.tga(0)A8R8G8B8.aya", "0824d66acec9dad5037be8bfc2b863201f94404d21795eac4fad82d8c4da2aba"),
    (GODOT_ASSETS / "Frontend/Icons/quit.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_BEA_title_nav_symbol_quitgame01.tga(0)A8R8G8B8.aya", "7096f573ff30302b5d5dad8f56ebd633e51f2bd70613d5349b974dada17b7a93"),
    (GODOT_ASSETS / "Frontend/level-bracket-01.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_select_level_bracket01.tga(0)A8R8G8B8.aya", "560db1621169c1b5787fc9c4691f4bede1af292674f84d4d43be11ca05166aa5"),
    (GODOT_ASSETS / "Frontend/level-bracket-02.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_select_level_bracket02.tga(0)A8R8G8B8.aya", "7ad21e2a6e64f61998f7a43e92fe92d69ac013b169fd8107b648b1fa69877b27"),
    (GODOT_ASSETS / "Frontend/level-ring-01.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_select_level_ring_bracket01.tga(0)A8R8G8B8.aya", "687eaf0945b701b622bdebde805e88cac394734a4b4420155379993ef9f74e1c"),
    (GODOT_ASSETS / "Frontend/level-ring-02.texture.aya", "data/resources/dxtntextures/FrontEnd%v3%FE_select_level_ring_bracket02.tga(0)A8R8G8B8.aya", "620900d34c153e722b6d78a9fbecab2d69b8e81abcdbda084b0f90eb96142dff"),
    (GODOT_ASSETS / "Frontend/title-font.texture.aya", "data/resources/textures/mustbe_TitleFont.tga(0)A8R8G8B8.aya", "1941e28a5665665fb7f8f733e7a4854c60def33e1d4f1cb9caa979bc204d0707"),
    (GODOT_ASSETS / "Frontend/loading-screen.texture.aya", "data/resources/dxtntextures/LoadingScreen.tga(0)X8R8G8B8.aya", "e4ad32fee41a31477e97d4f6f0b280f33c360756e3aba27bf23746038443fc2c"),
)


FRONTEND_TEXT_IDS = {
    "newGame": 0x00E39AD3,
    "continueGame": 0x1B749178,
    "loadGame": 0x01BE0271,
    "multiplayer": 0x0794B06E,
    "goodies": 0x007C113D,
    "options": 0x008251DC,
    "quit": 0x00141D4A,
    "selectLevel": 0x0E89F10A,
    "level100": 0x28672C3F,
    "loading": 0x003848A7,
}


CHUNKS = (
    (CORE_ASSETS / "Level100/level100-heightfield.hfld.bin", b"HFLD", 668660, "7a4c7c5b9400e2c8d2325cecb5c44701cd8a6e6f8609cbc8bc31d449c0620f5d"),
)


# Destination, source AYA destination above, hierarchy frame, exact OBJ SHA-256.
MESHES = (
    (GODOT_ASSETS / "Level100/level100-target-tank.obj", GODOT_ASSETS / "Level100/Source/m_f_pulsetank_training.msh.aya", None, "3a67f2bf49c9505855f73259d8d5829a7e0d1a0aed0f5a8802e82c4cf2c5df9f"),
    (GODOT_ASSETS / "Level100/level100-target-truck.obj", GODOT_ASSETS / "Level100/Source/m_f_truck_training.msh.aya", None, "76ef7ed7e78d39bf9606cb47b630ca4e10d1773cab38008bbee35b935544581d"),
    (GODOT_ASSETS / "Level100/level100-target-warehouse.obj", GODOT_ASSETS / "Level100/Source/m_m_warehouse.msh.aya", None, "3883b651a9963813a4ab9982460425910be5d7f8f7edce15ade475cf6d8eb5ce"),
)


# Destination, zero-based XAP record, exact record name, exact WAV SHA-256.
SOUNDS = (
    (GODOT_ASSETS / "Aquila/SoundEffects/strafe.wav", 20, "Battle Engine\\N_BE_dash", "8f22e6201b2fe8ac003d7d07c635f26a1b99277791f5262447f0400c747ecab1"),
    (GODOT_ASSETS / "Aquila/SoundEffects/energy-critical.wav", 21, "Battle Engine\\N_BE_energy_critical", "600776048d576d88839cf134372e38d739671de30ad27fbec880c0ce3a09cf18"),
    (GODOT_ASSETS / "Aquila/SoundEffects/energy-low.wav", 22, "Battle Engine\\N_BE_energy_low", "6f1434fbae6a2373a7c5fda5d921a5c61bb3006ab2a8eeb47245e1f11d55c70d"),
    (GODOT_ASSETS / "Aquila/SoundEffects/engine-inflight.wav", 23, "Battle Engine\\N_BE_engine_inflight", "0e6eb03aa2c2991c0e59c3483956b1c608a79700e0de179c855491cff548ac04"),
    (GODOT_ASSETS / "Aquila/SoundEffects/engine-land.wav", 24, "Battle Engine\\N_BE_engine_land", "07a03b5af4980d0d2e7c16bb5de833365483237cb4c83ff83b78d9aab61fbb36"),
    (GODOT_ASSETS / "Aquila/SoundEffects/engine-takeoff.wav", 25, "Battle Engine\\N_BE_engine_takeoff", "3698a4419c000ab982cbc92c6553ac2639272fb85930df52a26528b232f00798"),
    (GODOT_ASSETS / "Aquila/SoundEffects/target-locked.wav", 29, "Battle Engine\\N_BE_homing_missile_lock", "32bef3c615361b472c5b36d8952b6ca0d03bda74cdf8f9617d1e99b17d08d6d6"),
    (GODOT_ASSETS / "Aquila/SoundEffects/target-acquired.wav", 30, "Battle Engine\\N_BE_homing_missile_target", "3b0542a1df0541a3e19ec108d4c2e198556bfd406aba2f386e85b803ca04d5bc"),
    (GODOT_ASSETS / "Aquila/SoundEffects/hydraulics.wav", 31, "Battle Engine\\N_BE_hydraulics_02", "f02c11c62abb998ea35d38ede180aaf9b4ccaeaaae8f76e017e239a65570bf21"),
    (GODOT_ASSETS / "Aquila/SoundEffects/incoming-missile.wav", 32, "Battle Engine\\N_BE_incoming_missile", "7f00ce0cf622fdc65ca0ae3f06c7e68f093453db35486552b56715a71b9dcd0d"),
    (GODOT_ASSETS / "Aquila/SoundEffects/micro-missile-fire.wav", 33, "Battle Engine\\N_BE_micro_missiles_fire", "1c381c693cccfae6c8759a5bf417587af4f43845ccff827e25ea388df9a34f20"),
    (GODOT_ASSETS / "Aquila/SoundEffects/vulcan-cannon-fire.wav", 40, "Battle Engine\\N_BE_vulcan_cannon_fire", "bed47939fe924bf5d9a5ba273f9f61d6269813749ea43aca7db8c2bc1152078d"),
    (GODOT_ASSETS / "Frontend/SoundEffects/back.wav", 41, "Front End\\N_FE_back", "133b78e813c6b393be4dba1d263f69513958b0ab827d6603f952d6e0a82ba02b"),
    (GODOT_ASSETS / "Frontend/SoundEffects/move.wav", 42, "Front End\\N_FE_move", "76b2458e9c5854daf7237ea81b4f288ae09963bc10e7651e81e858fdb68ce83b"),
    (GODOT_ASSETS / "Frontend/SoundEffects/select.wav", 43, "Front End\\N_FE_select", "f84144c80405fe9f745b8cf4bd352d7fa4f8c0a8ba481c770c2c7c0a9053ade1"),
    (GODOT_ASSETS / "Level100/SoundEffects/terminal-ammunition-depleted.wav", 44, "HUD\\N_HUD_Ammunition_Depleted", "f1bd9e787faa1d32c149340b16af3d485cd6ad6b46ed09c30c889fc16b5a8da1"),
    (GODOT_ASSETS / "Level100/SoundEffects/terminal-armour-low.wav", 46, "HUD\\N_HUD_Armour_Low", "6da6b88abc77e7e281d338cf45ef35dd2d8aa99cca578418f6b6f28115d60d61"),
    (GODOT_ASSETS / "Level100/SoundEffects/terminal-energy-low.wav", 51, "HUD\\N_HUD_Energy_Low", "e7bf31d24623f3a37a6d578a52afae975a1b6d95dc9bb07a0dd1e1ed9c913f6d"),
    (GODOT_ASSETS / "Level100/SoundEffects/terminal-hostile-environment.wav", 55, "HUD\\N_HUD_Hostile_Environment", "3f841b810aac4a67221319a0d28f877c5bf1555130aeec337234e3f304ddf32f"),
    (GODOT_ASSETS / "Level100/SoundEffects/terminal-incoming-missile.wav", 56, "HUD\\N_HUD_Incoming_Missile", "5bf1fb9cfaef17fc0d62a16d3b37e07c85a5f9fa9f78d7135dc4ee75759ecdf6"),
    (GODOT_ASSETS / "Level100/SoundEffects/terminal-incoming-warhead.wav", 57, "HUD\\N_HUD_Incoming_Warhead", "711297354e61f9a94ad66172646caebc7683c9a67066b3ff7793996dd57e918e"),
    (GODOT_ASSETS / "Level100/SoundEffects/terminal-micro-missiles-selected.wav", 58, "HUD\\N_HUD_Micro_Missiles", "811d18c02399fbe05df649adb42732df9c6c4c3e85f4d9acafa1ed3751db04c1"),
    (GODOT_ASSETS / "Level100/SoundEffects/terminal-pulse-cannon-selected.wav", 60, "HUD\\N_HUD_Pulse_Cannon", "99a29b4bead7cd484547adbc3954a6f805638e6fcdf95cf70e90b6d5183734da"),
    (GODOT_ASSETS / "Level100/SoundEffects/terminal-vulcan-cannon-selected.wav", 70, "HUD\\N_HUD_Vulcan_Cannon", "a742431a169bba0a92f0241556a79d704626d56e1dc14bb43f41079aa2ce4990"),
    (GODOT_ASSETS / "Level100/SoundEffects/terminal-weapon-overheating.wav", 73, "HUD\\N_HUD_Weapon_Overheating", "f3f9e967708177f52667c872b152362284e0a8ba55b9e6a1137a5b981f44a34d"),
    (GODOT_ASSETS / "Level100/SoundEffects/component-explosion.wav", 93, "Impact\\N_I_explosion2", "c840a5ea48f975ecdb03e82646c369d164282e1ac10b03164923271da1067dec"),
    (GODOT_ASSETS / "Level100/SoundEffects/transport-explosion-large.wav", 94, "Impact\\N_I_explosion_big", "4ce37c52a010e7903a5e7d4073e0647ca790fbfe839facbba97ad4d7fe2de2fd"),
    (GODOT_ASSETS / "Level100/SoundEffects/explosion-large-debris.wav", 95, "Impact\\N_I_explosion_big_debris", "e5daefb4f5db5738b0cd8cd2619868d090ca4a604642bc05d302c1afb54980fe"),
    (GODOT_ASSETS / "Level100/SoundEffects/pulse-cannon-fire.wav", 35, "Battle Engine\\N_BE_pulse_cannon_fire", "710ff06db55bc694efb8ff7d3a5ab658125e7ca0fe6b4733a805da98b22b0277"),
    (GODOT_ASSETS / "Level100/SoundEffects/target-tank-explosion-medium.wav", 102, "Impact\\N_I_explosion_medium", "7228ae049cb0a9877e63671a65e51829443017b2c4981df90a9c64d2f38b6d9c"),
    (GODOT_ASSETS / "Level100/SoundEffects/pulse-impact-small.wav", 105, "Impact\\N_I_explosion_small", "3296b13938928f54847a29e17307e7875e9933f8fd6381bf0dfcd260cd6fc131"),
    (GODOT_ASSETS / "Frontend/SoundEffects/back.wav", 41, "Front End\\N_FE_back", "133b78e813c6b393be4dba1d263f69513958b0ab827d6603f952d6e0a82ba02b"),
    (GODOT_ASSETS / "Frontend/SoundEffects/move.wav", 42, "Front End\\N_FE_move", "76b2458e9c5854daf7237ea81b4f288ae09963bc10e7651e81e858fdb68ce83b"),
    (GODOT_ASSETS / "Frontend/SoundEffects/select.wav", 43, "Front End\\N_FE_select", "f84144c80405fe9f745b8cf4bd352d7fa4f8c0a8ba481c770c2c7c0a9053ade1"),
    (GODOT_ASSETS / "Level100/SoundEffects/facility-explosion-medium.wav", 103, "Impact\\N_I_explosion_medium_ricochet", "f86d23cfa18025ba9d1283e0b10d5bc1f939161465a924140044d3c0a6095d3a"),
    (GODOT_ASSETS / "Level100/SoundEffects/explosion-small.wav", 106, "Impact\\N_I_explosion_small_debris", "28f89761970629118b989b41b5dda3253fecb431ec479b64d056248bc3e5c1dc"),
    (GODOT_ASSETS / "Level100/SoundEffects/aquila-explosion-huge.wav", 107, "Impact\\N_I_explosion_vbig", "23a85aa8c5543f5be15f7d8b2279859560f5d417e9475f015a69522db3c8aed8"),
    (GODOT_ASSETS / "Level100/SoundEffects/explosion-huge-ground-debris.wav", 108, "Impact\\N_I_explosion_vbig_debris", "5205f38b925ec77a04aaed0501387176d49f0a69b11479127168936e8ebfcdec"),
    (GODOT_ASSETS / "Level100/SoundEffects/trainer-flyby.wav", 119, "Vehicles\\N_V_F_fighter_flyby", "838eac239fc8b53ef89471d433978d7e4aee0b3f96cea5d3281f60e2cfa6d2ce"),
    (GODOT_ASSETS / "Level100/SoundEffects/transport-flyby.wav", 126, "Vehicles\\N_V_bomber_flyby", "6317e8056a8b4f657aefc1319fb8ef512927846dde8a287498b2c2e852108a1c"),
    (GODOT_ASSETS / "Level100/SoundEffects/drone-vulcan-fire.wav", 150, "Weapons\\N_WP_blaster_02", "5e9227999084bd4fb06558b498c86f968c79b8df87b06d4621336bbc994b577b"),
    (GODOT_ASSETS / "Level100/SoundEffects/repair-charging.wav", 7, "Atmospheres\\N_A_health_pod_charging", "9ac76f06602d5432188901de75daaa2bb87dd12f46f7df88d6eda73bf31632ba"),
    (GODOT_ASSETS / "Level100/SoundEffects/repair-full.wav", 8, "Atmospheres\\N_A_health_pod_full", "2725b5298e6fa84c0d96deefdf3d1fe7fefb854ce8512a70441d1f95c395bb1f"),
    (GODOT_ASSETS / "Level100/SoundEffects/repair-idle.wav", 9, "Atmospheres\\N_A_health_pod_on", "ec3f2af86c5281d42923c3ae00fb66222e4e358a5f986fd26c7a43c34406f7d4"),
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


def _physics_records(data: bytes) -> dict[tuple[int, str], dict[int, bytes]]:
    if len(data) < 6 or struct.unpack_from("<H", data, 0)[0] != 0x12:
        raise RuntimeError("unsupported physics-definition framing")
    offset = 2
    records: dict[tuple[int, str], dict[int, bytes]] = {}
    record_count = 0
    while struct.unpack_from("<i", data, offset)[0] != -1:
        record_type, _declared_size = struct.unpack_from("<II", data, offset)
        offset += 8
        name_end = data.index(0, offset)
        name = data[offset:name_end].decode("ascii")
        offset = name_end + 1
        fields: dict[int, bytes] = {}
        while True:
            field_id, size = struct.unpack_from("<II", data, offset)
            offset += 8
            value = data[offset : offset + size]
            offset += size
            marker = struct.unpack_from("<i", data, offset)[0]
            offset += 4
            fields[field_id] = value
            if marker == -1:
                break
            if marker != 0:
                raise RuntimeError(
                    f"physics record has an invalid continuation: {name}"
                )
        records[(record_type, name)] = fields
        record_count += 1
    if offset + 4 != len(data) or record_count != 777:
        raise RuntimeError("physics-definition record count changed")
    return records


def _definition_string(fields: dict[int, bytes], field_id: int) -> str:
    value = fields[field_id]
    if not value or value[-1] != 0:
        raise RuntimeError(f"physics string field {field_id} is not terminated")
    return value[:-1].decode("ascii")


def _level100_actor_motion_definitions(
    physics: dict[tuple[int, str], dict[int, bytes]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for definition_name, expected_life_bits in (
        ("Target Tank", 0x40C00000),
        ("Target Truck", 0x40400000),
    ):
        fields = physics[(1, definition_name)]
        if (
            fields.get(1) != struct.pack("<I", 0x40600000)
            or fields.get(3) != struct.pack("<I", expected_life_bits)
            or fields.get(5) != struct.pack("<I", 0x3D567750)
            or fields.get(8) != struct.pack("<i", 3)
        ):
            raise RuntimeError(
                f"Level 100 {definition_name} ground-motion fields changed"
            )
        rows.append(
            {
                "arrivalRadiusMillimeters": 2_000,
                "authoredOrder": len(rows),
                "behaviorInternalId": 2,
                "behaviorSerializedType": 3,
                "definitionName": definition_name,
                "fullGuideBaseTicks": 4,
                "coreGroundOriginOffsetMillimeters": 100,
                "maximumSpeedFloatBits": struct.unpack("<i", fields[1])[0],
                "maximumTurnRadiansPerBaseTickFloatBits": struct.unpack(
                    "<i", fields[5]
                )[0],
                "motionClass": "GroundVehicle",
                "steamClassVtableAddress": 0x005E297C,
            }
        )

    for definition_name in ("Air Trainer", "Target Drone"):
        fields = physics[(1, definition_name)]
        if fields.get(8) != struct.pack("<i", 9):
            raise RuntimeError(
                f"Level 100 {definition_name} plane behavior changed"
            )
        rows.append(
            {
                "arrivalRadiusMillimeters": 5_000,
                "authoredOrder": len(rows),
                "behaviorInternalId": 8,
                "behaviorSerializedType": 9,
                "definitionName": definition_name,
                "fullGuideBaseTicks": None,
                "coreGroundOriginOffsetMillimeters": None,
                "maximumSpeedFloatBits": None,
                "maximumTurnRadiansPerBaseTickFloatBits": None,
                "motionClass": "Plane",
                "steamClassVtableAddress": 0x005E1930,
            }
        )

    transporter_name = "U-17 Highside Transporter"
    transporter_fields = physics[(1, transporter_name)]
    if transporter_fields.get(8) != struct.pack("<i", 12):
        raise RuntimeError("Level 100 transporter dropship behavior changed")
    rows.append(
        {
            "arrivalRadiusMillimeters": 8_000,
            "authoredOrder": len(rows),
            "behaviorInternalId": 12,
            "behaviorSerializedType": 12,
            "definitionName": transporter_name,
            "fullGuideBaseTicks": None,
            "coreGroundOriginOffsetMillimeters": None,
            "maximumSpeedFloatBits": None,
            "maximumTurnRadiansPerBaseTickFloatBits": None,
            "motionClass": "Dropship",
            "steamClassVtableAddress": 0x005E1DD8,
        }
    )
    return rows


def _materialize_level100_hud_manifest(stage: Path) -> str:
    level_script_path = stage / LEVEL100_LEVEL_SCRIPT
    english_source_path = stage / LEVEL100_ENGLISH_SOURCE
    text_stf_path = stage / LEVEL100_TEXT_STF
    english_dat_path = stage / LEVEL100_ENGLISH_DAT

    level_script = level_script_path.read_text(encoding="windows-1252")
    english_source = english_source_path.read_text(encoding="windows-1252")
    text_stf = text_stf_path.read_text(encoding="windows-1252")

    speaker_by_token = {
        "P_TATIANA": "Tatiana",
        "P_TECHNICIAN": "Technician",
        "P_KRAMER": "Kramer",
    }
    play_events: list[dict[str, object]] = []
    current_highlight = "None"
    for line in level_script.splitlines():
        highlight_match = re.search(r"\bHighlightHudPart\s*\(\s*(\w+)\s*\)", line)
        if highlight_match:
            current_highlight = highlight_match.group(1)

        play_match = re.search(
            r"\bPlayCharMessage(Wait)?\s*\(\s*(\w+)\s*,\s*(\w+)",
            line,
        )
        if play_match:
            wait_token, speaker_token, symbol = play_match.groups()
            if speaker_token not in speaker_by_token:
                raise RuntimeError(
                    f"Level 100 script uses an unsupported HUD speaker: {speaker_token}"
                )
            play_events.append(
                {
                    "highlightSymbol": current_highlight,
                    "speaker": speaker_by_token[speaker_token],
                    "symbol": symbol,
                    "waitsForCompletion": wait_token is not None,
                }
            )

        unhighlight_match = re.search(
            r"\bUnHighlightHudPart\s*\(\s*(\w+)\s*\)",
            line,
        )
        if unhighlight_match:
            if current_highlight != unhighlight_match.group(1):
                raise RuntimeError("Level 100 script unhighlights a different HUD part")
            current_highlight = "None"

    if current_highlight != "None":
        raise RuntimeError("Level 100 script leaves a HUD highlight active")
    play_symbols = {str(event["symbol"]) for event in play_events}
    if len(play_events) != 45 or len(play_symbols) != 43:
        raise RuntimeError(
            "Level 100 PlayCharMessage event identity changed: "
            f"{len(play_events)} calls/{len(play_symbols)} messages"
        )

    english_message_symbols: list[str] = []
    seen_english_message_symbols: set[str] = set()
    for match in re.finditer(
        r"^\[([^\]]+)\]\s*//\s*\w+\s*$",
        english_source,
        re.MULTILINE,
    ):
        symbol = match.group(1)
        if symbol in seen_english_message_symbols:
            raise RuntimeError(f"Level 100 English source repeats a message: {symbol}")
        seen_english_message_symbols.add(symbol)
        english_message_symbols.append(symbol)
    if len(english_message_symbols) != 51:
        raise RuntimeError(
            "Level 100 English callback-message count changed: "
            f"{len(english_message_symbols)}"
        )

    modified_symbols = {
        symbol.removesuffix("_MOD"): symbol
        for symbol in play_symbols
        if symbol.endswith("_MOD")
    }
    message_symbols = [
        modified_symbols.get(symbol, symbol) for symbol in english_message_symbols
    ]
    if len(message_symbols) != 51 or len(set(message_symbols)) != 51:
        raise RuntimeError(
            f"Level 100 released HUD-message union changed: {len(message_symbols)}"
        )
    if not play_symbols.issubset(message_symbols):
        raise RuntimeError("Level 100 English callback order omits a played message")

    symbol_to_signed_id: dict[str, int] = {}
    for line in text_stf.splitlines():
        match = re.match(r"^#define\s+(\S+)\s+(-?\d+)\s*$", line.strip())
        if not match:
            continue
        symbol, raw_value = match.groups()
        value = int(raw_value, 10)
        if symbol in symbol_to_signed_id and symbol_to_signed_id[symbol] != value:
            raise RuntimeError(f"text.stf changes a symbol ID: {symbol}")
        symbol_to_signed_id[symbol] = value

    tools_root = ROOT / "tools"
    if str(tools_root) not in sys.path:
        sys.path.insert(0, str(tools_root))
    from language_dat_decode import entry_record, parse_lang_dat

    language = parse_lang_dat(english_dat_path)
    english_dat = english_dat_path.read_bytes()
    entries_by_id = {entry.text_id: entry for entry in language.entries}

    def native_record(symbol: str) -> tuple[int, dict[str, object]]:
        try:
            signed_id = symbol_to_signed_id[symbol]
            entry = entries_by_id[signed_id & 0xFFFFFFFF]
        except KeyError as error:
            raise RuntimeError(
                f"released text data is missing Level 100 symbol: {symbol}"
            ) from error
        return signed_id, entry_record(language, english_dat, entry)

    messages: list[dict[str, object]] = []
    for symbol in message_symbols:
        signed_id, native = native_record(symbol)
        audio = native["audio"]
        text = native["text"]
        if not isinstance(audio, str) or not audio or Path(audio).name != audio:
            raise RuntimeError(
                f"released Level 100 message has invalid audio identity: {symbol}"
            )
        if not isinstance(text, str) or not text:
            raise RuntimeError(
                f"released Level 100 message has no native text: {symbol}"
            )
        audio_file = f"{audio.lower()}.ogg"
        if not (
            stage / GODOT_ASSETS / "Level100/TutorialAudio" / audio_file
        ).is_file():
            raise RuntimeError(
                f"released Level 100 message audio is not materialized: {audio_file}"
            )
        messages.append(
            {
                "audioFile": audio_file,
                "symbol": symbol,
                "text": text,
                "textId": signed_id,
            }
        )

    native_play_events: list[dict[str, object]] = []
    for event_index, event in enumerate(play_events):
        symbol = str(event["symbol"])
        signed_id, _ = native_record(symbol)
        native_play_events.append(
            {
                "eventIndex": event_index,
                "highlightSymbol": event["highlightSymbol"],
                "speaker": event["speaker"],
                "symbol": symbol,
                "textId": signed_id,
                "waitsForCompletion": event["waitsForCompletion"],
            }
        )

    help_symbols = re.findall(r"\bAddHelpMessage\s*\(\s*(\w+)\s*\)", level_script)
    if len(help_symbols) != 6 or len(set(help_symbols)) != 6:
        raise RuntimeError(
            f"Level 100 help-message count changed: {len(help_symbols)}"
        )
    help_messages: list[dict[str, object]] = []
    for symbol in help_symbols:
        signed_id, native = native_record(symbol)
        text = native["text"]
        if not isinstance(text, str) or not text:
            raise RuntimeError(
                f"released Level 100 help message has no native text: {symbol}"
            )
        help_messages.append(
            {"symbol": symbol, "text": text, "textId": signed_id}
        )

    terminal_strings: dict[str, dict[str, object]] = {}
    for key, symbol in (
        ("missionComplete", "IG_MISSION_COMPLETE"),
        ("retry", "GI_RETRY"),
        ("back", "GI_BACK"),
        ("tutorialBroken", "LOSE_TUTORIAL_BROKE"),
        ("playerDeath", "GAME_OVER_DEATH"),
        ("water", "GAME_OVER_WATER"),
    ):
        signed_id, native = native_record(symbol)
        text = native["text"]
        if not isinstance(text, str) or not text:
            raise RuntimeError(
                f"released terminal string has no native text: {symbol}"
            )
        terminal_strings[key] = {
            "symbol": symbol,
            "text": text,
            "textId": signed_id,
        }

    payload = {
        "help": help_messages,
        "messages": messages,
        "playCharEvents": native_play_events,
        "schemaVersion": "onslaught.level100-hud-events.v3",
        "sources": {
            "englishDatSha256": _sha256(english_dat),
            "englishSourceSha256": _sha256(english_source_path.read_bytes()),
            "levelScriptSha256": _sha256(level_script_path.read_bytes()),
            "textStfSha256": _sha256(text_stf_path.read_bytes()),
        },
        "terminalStrings": terminal_strings,
    }
    data = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    manifest_hash = _sha256(data)
    target = stage / LEVEL100_HUD_MANIFEST
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return manifest_hash


def _fixed_outputs() -> tuple[tuple[Path, str], ...]:
    direct = tuple(
        (path, expected) for path, _, expected in DIRECT_ASSETS + FRONTEND_ASSETS
    )
    chunks = tuple((path, expected) for path, _, _, expected in CHUNKS)
    derived = (
        (ROOT_TERRAIN_TEXTURE, ROOT_TERRAIN_TEXTURE_SHA256),
        (TERRAIN_HIERARCHY_SOURCE, TERRAIN_HIERARCHY_SOURCE_SHA256),
        *(
            (LEVEL100_SCRIPT_ROOT / f"level100-{name}.mso.bin", expected)
            for name, _, expected in LEVEL100_SCRIPT_OBJECTS
        ),
        (FRONTEND_LOCALIZATION, FRONTEND_LOCALIZATION_SHA256),
        (LEVEL100_HUD_MANIFEST, LEVEL100_HUD_MANIFEST_SHA256),
    )
    meshes = tuple((path, expected) for path, _, _, expected in MESHES)
    sounds = tuple((path, expected) for path, _, _, expected in SOUNDS)
    return direct + chunks + derived + meshes + sounds


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
        manifest.get("schema") != "onslaught.level100-static-world.v13"
        or manifest.get("sourceArchiveSha256") != LEVEL_ARCHIVE_SHA256
        or manifest.get("physicsSourceSha256") != PHYSICS_DEFINITIONS_SHA256
        or manifest.get("sourceAggregateSha256") != STATIC_WORLD_SOURCE_AGGREGATE_SHA256
        or manifest.get("unitRecordCount") != 35
        or manifest.get("visibleObjectCount") != 33
        or manifest.get("suppressedFernCount") != 753
        or manifest.get("pineInstanceCount") != 1481
        or len(manifest.get("objects", ())) != 33
        or len(manifest.get("actorDefinitions", ())) != 44
        or len(manifest.get("spawnDefinitions", ())) != 10
        or [
            (
                row.get("definitionName"),
                row.get("motionClass"),
                row.get("behaviorInternalId"),
                row.get("steamClassVtableAddress"),
                row.get("arrivalRadiusMillimeters"),
            )
            for row in manifest.get("motionDefinitions", ())
        ]
        != [
            ("Target Tank", "GroundVehicle", 2, 0x005E297C, 2_000),
            ("Target Truck", "GroundVehicle", 2, 0x005E297C, 2_000),
            ("Air Trainer", "Plane", 8, 0x005E1930, 5_000),
            ("Target Drone", "Plane", 8, 0x005E1930, 5_000),
            ("U-17 Highside Transporter", "Dropship", 12, 0x005E1DD8, 8_000),
        ]
        or [
            path.get("name") for path in manifest.get("waypointPaths", ())
        ]
        != [
            "Flyby Path",
            "Target Truck Path 3",
            "Target Truck Path 2",
            "Target Truck Path 1",
            "Transporter Path",
            "Target Tank Path 2",
            "Target Tank Path 1",
            "Drone Path 1",
        ]
        or len(manifest.get("pines", ())) != 1481
        or len(manifest.get("meshes", {})) != 28
        or len(manifest.get("textures", {})) != 34
        or manifest.get("pineBillboards", {}).get("texture")
        != "pine-imposters-100"
        or manifest.get("pineBillboards", {}).get("meshQualityDistance")
        != PINE_MESH_QUALITY_DISTANCE
        or manifest.get("pineBillboards", {}).get("fastStandingViewPhase")
        != PINE_FAST_STANDING_VIEW_PHASE
        or len(manifest.get("pineBillboards", {}).get("variants", ())) != 4
        or any(
            len(variant.get("centerOffset", ())) != 3
            or len(variant.get("views", ())) != 6
            for variant in manifest.get("pineBillboards", {}).get("variants", ())
        )
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
    outputs.append((LEVEL100_CONTACT_ASSET, LEVEL100_CONTACT_ASSET_SHA256))
    if len(outputs) != 65 or len({path for path, _ in outputs}) != len(outputs):
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
        if (
            (candidate / "BEA.exe").is_file()
            and (candidate / LEVEL_ARCHIVE).is_file()
            and (candidate / BASE_ARCHIVE).is_file()
            and (candidate / SOUND_BANK).is_file()
        ):
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


def _chunk_records(data: bytes) -> list[tuple[bytes, bytes]]:
    records: list[tuple[bytes, bytes]] = []
    offset = 0
    while offset < len(data):
        if offset + 8 > len(data):
            raise RuntimeError("retail data contains a truncated chunk")
        size = struct.unpack_from("<I", data, offset + 4)[0]
        end = offset + 8 + size
        if end > len(data):
            raise RuntimeError("retail data contains an overrun chunk")
        records.append((data[offset : offset + 4], data[offset + 8 : end]))
        offset = end
    return records


def _chunk_payload(data: bytes, wanted_tag: bytes) -> bytes:
    matches = [payload for tag, payload in _chunk_records(data) if tag == wanted_tag]
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

    def string32(self) -> str:
        size = self.int32()
        if size < 0 or size > 1_048_576:
            raise RuntimeError("Level 100 world data has an invalid string length")
        return self._take(size).decode("ascii")

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
        mesh_number = reader.int32()
        allegiance = reader.int32()
        target = reader.int32()
        script = reader.c_string()
        name = reader.c_string()
        spawn_script = reader.c_string()
        active = reader.int32()
        attach_scripts = reader.int32()

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
                "active": active != 0,
                "allegiance": allegiance,
                "attachScripts": attach_scripts != 0,
                "mesh": mesh_key,
                "meshNumber": mesh_number,
                "name": name or definition,
                "ordinal": ordinal,
                "retailOrientation": yaw_pitch_roll,
                "retailPosition": position,
                "script": script,
                "spawnScript": spawn_script,
                "target": target,
                "thingType": thing_type,
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


LEVEL100_SCRIPT_NAMES = tuple(item[0] for item in LEVEL100_SCRIPT_OBJECTS)


def _skip_level100_script_value(reader: _WorldReader) -> None:
    value_type = reader.int32()
    if value_type == 0:
        return
    if value_type in (1, 2, 4, 5):
        reader.int32()
        return
    if value_type == 3:
        reader.string32()
        return
    if value_type == 6:
        for _ in range(3):
            reader.int32()
        return
    raise RuntimeError(f"Level 100 script object has unsupported value type {value_type}")


def _skip_level100_script_object(reader: _WorldReader) -> tuple[str, int]:
    name = reader.string32()
    instruction_count = reader.int32()
    if instruction_count < 0 or instruction_count > 20_000:
        raise RuntimeError("Level 100 script object has an invalid instruction count")
    reader._take(instruction_count * 8)
    reader._take(13 * 4)
    symbol_count = reader.int32()
    if symbol_count < 0 or symbol_count > 4_096:
        raise RuntimeError("Level 100 script object has an invalid symbol count")
    for ordinal in range(symbol_count):
        reader.string32()
        _skip_level100_script_value(reader)
        reader.int32()
        if reader.int32() != ordinal or reader.int32() != 1:
            raise RuntimeError("Level 100 script object has invalid symbol metadata")
    if reader.int32() != symbol_count:
        raise RuntimeError("Level 100 script object has an invalid symbol trailer")
    event_count = reader.int32()
    if event_count < 0 or event_count > 256:
        raise RuntimeError("Level 100 script object has an invalid event count")
    for _ in range(event_count):
        reader.int32()
        if reader.int32() != 1:
            raise RuntimeError("Level 100 script event parameter count changed")
        reader.int32()
    if reader.int32() != 0 or reader.int32() not in (0, 1):
        raise RuntimeError("Level 100 script object has an invalid trailer")
    payload_end = reader.position
    if reader._take(10) != b"end_script":
        raise RuntimeError("Level 100 script object end marker changed")
    return name, payload_end


def _parse_level_world_scripts(
    raw_level: bytes,
) -> tuple[_WorldReader, dict[str, bytes]]:
    rlwd = _chunk_payload(_chunk_payload(_chunk_payload(raw_level, b"WRES"), b"WRLD"), b"RLWD")
    reader = _WorldReader(rlwd)
    if (
        reader.uint16() != 50
        or tuple(reader.int32() for _ in range(3)) != (3, 41, 100)
        or reader.int32() != 1
        or reader.string8() != "Aquila Prototype"
        or tuple(reader.int32() for _ in range(4)) != (0, 0, 0, 0)
        or reader.int32() != 1
        or reader.int32() != len(LEVEL100_SCRIPT_NAMES)
    ):
        raise RuntimeError("Level 100 level-world header is not the supported version-50 layout")
    scripts: dict[str, bytes] = {}
    for expected_name, expected_size, expected_hash in LEVEL100_SCRIPT_OBJECTS:
        start = reader.position
        name, payload_end = _skip_level100_script_object(reader)
        payload = rlwd[start:payload_end]
        if (
            name != expected_name
            or len(payload) != expected_size
            or _sha256(payload) != expected_hash
            or name in scripts
        ):
            raise RuntimeError(
                f"Level 100 compiled script {expected_name} changed "
                f"(name={name!r}, size={len(payload)}, SHA-256={_sha256(payload)})"
            )
        scripts[name] = payload
    return reader, scripts


def _parse_level_world_actors_and_waypoints(
    raw_level: bytes,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    reader, _ = _parse_level_world_scripts(raw_level)
    if reader.int32() != 1 or reader.int32() != 0 or reader.uint16() != 45:
        raise RuntimeError("Level 100 initial-actor header changed")

    actors: list[dict[str, object]] = []
    for ordinal in range(45):
        thing_type = reader.int32()
        position = [reader.single() for _ in range(3)]
        orientation = [reader.single() for _ in range(3)]
        mesh_number = reader.int32()
        allegiance = reader.int32()
        target = reader.int32()
        script = reader.c_string()
        name = reader.c_string()
        spawn_script = reader.c_string()
        active = reader.int32()
        attach_scripts = reader.int32()
        definition = ""
        radius: float | None = None
        if thing_type in (8, 35):
            definition = reader.string8()
            if reader.int32() != -1:
                raise RuntimeError("Level 100 level-world unit definition trailer changed")
        elif thing_type == 15:
            reader.int32()
            reader.int32()
        elif thing_type == 36:
            radius = reader.single()
        elif thing_type not in (18, 27, 37):
            raise RuntimeError(f"unsupported Level 100 level-world thing type {thing_type}")
        actors.append(
            {
                "active": active != 0,
                "allegiance": allegiance,
                "attachScripts": attach_scripts != 0,
                "definition": definition,
                "meshNumber": mesh_number,
                "name": name,
                "ordinal": ordinal,
                "radius": radius,
                "retailOrientation": orientation,
                "retailPosition": position,
                "script": script,
                "spawnScript": spawn_script,
                "target": target,
                "thingType": thing_type,
            }
        )
    if reader.uint16() != 0 or reader.int32() != 2:
        raise RuntimeError("Level 100 initial-actor records did not end at the tree groups")

    for expected_name, expected_count in (("fernsnow", 753), ("pinesnow", 1_481)):
        name = reader.string8()
        count = reader.int32()
        if name != expected_name or count != expected_count:
            raise RuntimeError("Level 100 level-world tree groups changed")
        for _ in range(count):
            reader.single()
            reader.single()
            reader.int32()

    if reader.uint16() != 1 or reader.int32() != 121:
        raise RuntimeError("Level 100 waypoint node table changed")
    waypoint_nodes = [
        tuple(reader.single() for _ in range(4))
        for _ in range(121)
    ]

    edge_count = reader.int32()
    if edge_count != 198:
        raise RuntimeError("Level 100 waypoint edge table changed")
    for _ in range(edge_count):
        start = reader.int32()
        end = reader.int32()
        enabled = reader.int32()
        if start not in range(len(waypoint_nodes)) or end not in range(len(waypoint_nodes)):
            raise RuntimeError("Level 100 waypoint edge refers to an invalid node")
        if enabled != 1:
            raise RuntimeError("Level 100 waypoint edge state changed")

    path_count = reader.uint16()
    if path_count != 8:
        raise RuntimeError("Level 100 named waypoint path count changed")
    waypoint_paths: list[dict[str, object]] = []
    for _ in range(path_count):
        name = reader.string8()
        node_count = reader.int32()
        if node_count <= 0 or node_count > len(waypoint_nodes):
            raise RuntimeError(f"Level 100 waypoint path {name!r} has an invalid node count")
        points: list[dict[str, object]] = []
        for _ in range(node_count):
            node_index = reader.uint16()
            if node_index >= len(waypoint_nodes):
                raise RuntimeError(
                    f"Level 100 waypoint path {name!r} refers to an invalid node"
                )
            components = waypoint_nodes[node_index]
            points.append(
                {
                    "positionMillimeters": [
                        _round_away_from_zero(
                            (components[0] - LEVEL100_PLAYER_START_X) * 1_000.0
                        ),
                        _round_away_from_zero(components[2] * 1_000.0),
                        _round_away_from_zero(
                            (components[1] - LEVEL100_PLAYER_START_Y) * 1_000.0
                        ),
                    ],
                    "nodeIndex": node_index,
                    "retailComponentsFloatBits": [
                        _float_bits(component) for component in components
                    ],
                }
            )
        waypoint_paths.append({"name": name, "points": points})

    expected_paths = {
        "Flyby Path": (43, 42, 41),
        "Target Truck Path 3": (36, 35, 34, 33),
        "Target Truck Path 2": (32, 31, 30, 29),
        "Target Truck Path 1": (25, 26, 27, 28),
        "Transporter Path": (44, 22, 23),
        "Target Tank Path 2": (38, 37, 8, 10, 24),
        "Target Tank Path 1": (18, 6, 7),
        "Drone Path 1": (1, 2, 3, 4),
    }
    actual_paths = {
        str(path["name"]): tuple(
            int(point["nodeIndex"]) for point in path["points"]
        )
        for path in waypoint_paths
    }
    if actual_paths != expected_paths:
        raise RuntimeError("Level 100 named waypoint paths changed")
    return actors, waypoint_paths


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


PINE_CENTER_BITS = {
    0: (0xBCCC7F20, 0x39BA4000, 0xBF6303AA),
    1: (0x3D8FAD60, 0xBDA96080, 0xBF696408),
    2: (0x3C9B2D60, 0xBDF5D470, 0xBF6A0AB4),
    3: (0x3D429CA0, 0x3CD68540, 0xBF506532),
}


def _pine_imposter_views(raw_level: bytes) -> list[list[list[float]]]:
    outer = _chunk_payload(raw_level, b"IMPS")
    if len(outer) != 10_208:
        raise RuntimeError("Level 100 has an unexpected outer IMPS envelope")
    payload = _chunk_payload(outer, b"IMPS")
    if len(payload) != 10_200 or payload.count(b"Imposters_100\0") != 1:
        raise RuntimeError("Level 100 does not select the expected imposter atlas")

    views: list[list[list[float]]] = []
    for variant in range(4):
        name = f"pinesnow{variant}.MSH".encode("ascii")
        name_offset = payload.find(name)
        if name_offset < 0 or payload.find(name, name_offset + 1) >= 0:
            raise RuntimeError(f"Level 100 has an ambiguous {name.decode()} imposter")
        record_offset = payload.rfind(b"IMPT", 0, name_offset)
        if record_offset < 0:
            raise RuntimeError(f"Level 100 has no IMPT owner for {name.decode()}")
        record_size = struct.unpack_from("<I", payload, record_offset + 4)[0]
        record_end = record_offset + 8 + record_size
        if record_size != 248 or not (record_offset < name_offset < record_end):
            raise RuntimeError(f"Level 100 has an invalid {name.decode()} IMPT record")
        view_offset = payload.find(b"VIEW", name_offset, record_end)
        if (
            view_offset < 0
            or payload.find(b"VIEW", view_offset + 1, record_end) >= 0
            or struct.unpack_from("<I", payload, view_offset + 4)[0] != 144
            or view_offset + 152 != record_end
        ):
            raise RuntimeError(f"Level 100 has invalid {name.decode()} VIEW data")
        view_payload = payload[view_offset + 8 : record_end]
        all_views = [
            list(struct.unpack_from("<6f", view_payload, index * 24))
            for index in range(6)
        ]
        if any(
            len(view) != 6
            or not all(math.isfinite(value) for value in view)
            or not (0.0 <= view[0] < view[1] <= 1.0)
            or not (0.0 <= view[2] < view[3] <= 1.0)
            or view[4] <= 0.0
            or view[5] <= 0.0
            for view in all_views
        ):
            raise RuntimeError(f"Level 100 {name.decode()} imposter views are invalid")
        views.append(all_views)
    return views


def _pine_global_center(source: bytes, inflate_aya, variant: int) -> list[float]:
    inflated = inflate_aya(source)
    outer_offset = len(inflated) - 56
    inner_offset = outer_offset + 8
    if (
        outer_offset < 0
        or inflated[outer_offset : outer_offset + 4] != b"BBOX"
        or struct.unpack_from("<I", inflated, outer_offset + 4)[0] != 48
        or inflated[inner_offset : inner_offset + 4] != b"BBOX"
        or struct.unpack_from("<I", inflated, inner_offset + 4)[0] != 40
        or inner_offset + 48 != len(inflated)
    ):
        raise RuntimeError(f"pinesnow{variant} has no exact final global BBOX")
    center_bits = struct.unpack_from("<3I", inflated, inner_offset + 8)
    if center_bits != PINE_CENTER_BITS[variant]:
        raise RuntimeError(f"pinesnow{variant} global BBOX center changed")
    return list(struct.unpack("<3f", struct.pack("<3I", *center_bits)))


LEVEL100_PLAYER_START_X = 288.6875
LEVEL100_PLAYER_START_Y = 243.25

LEVEL100_SETUP_SCRIPT_BINDINGS = {
    "Tank Factory": "TankFactory",
    "Airfield": "Hangar",
    "Turret 01": "Turret",
    "Turret 02": "Turret",
    "Turret 03": "Turret",
    "Turret 04": "Turret",
    "Radar Station": "Facilities",
    "Forseti Research Building 1": "Facilities",
    "Health Pad": "Facilities",
    "Control Tower": "Facilities",
}


def _round_away_from_zero(value: float) -> int:
    if not math.isfinite(value):
        raise RuntimeError("Level 100 actor data contains a non-finite value")
    return math.floor(value + 0.5) if value >= 0 else math.ceil(value - 0.5)


def _float_bits(value: float) -> int:
    return struct.unpack("<i", struct.pack("<f", value))[0]


def _normalize_angle(value: float) -> float:
    while value > math.pi:
        value -= math.tau
    while value < -math.pi:
        value += math.tau
    return value


def _actor_pose(
    retail_position: list[float] | tuple[float, float, float],
    retail_orientation: list[float] | tuple[float, float, float],
    retail_basis: list[list[float]] | tuple[tuple[float, float, float], ...] | None = None,
) -> dict[str, list[int]]:
    basis = retail_basis or _retail_basis(retail_orientation)
    core_basis = _change_basis_retail_to_core(basis)
    return {
        "angularVelocityMicroRadiansPerTick": [0, 0, 0],
        "basisFloatBits": [
            _float_bits(component) for row in core_basis for component in row
        ],
        "linearVelocityMillimetersPerTick": [0, 0, 0],
        "positionMillimeters": [
            _round_away_from_zero((retail_position[0] - LEVEL100_PLAYER_START_X) * 1_000.0),
            _round_away_from_zero(retail_position[2] * 1_000.0),
            _round_away_from_zero((retail_position[1] - LEVEL100_PLAYER_START_Y) * 1_000.0),
        ],
    }


def _retail_basis(
    retail_orientation: list[float] | tuple[float, float, float],
) -> list[list[float]]:
    yaw, pitch, roll = retail_orientation
    # Every authored Level 100 actor uses yaw only. Preserve that released
    # contract explicitly rather than inventing an unobserved Euler order.
    if pitch != 0.0 or roll != 0.0:
        raise RuntimeError("Level 100 authored actor uses an unresolved pitch/roll basis")
    cosine = math.cos(yaw)
    sine = math.sin(yaw)
    return [[cosine, -sine, 0.0], [sine, cosine, 0.0], [0.0, 0.0, 1.0]]


def _matrix_multiply(left, right) -> list[list[float]]:
    return [
        [sum(left[row][axis] * right[axis][column] for axis in range(3))
         for column in range(3)]
        for row in range(3)
    ]


def _matrix_vector(matrix, vector) -> list[float]:
    return [sum(matrix[row][axis] * vector[axis] for axis in range(3)) for row in range(3)]


def _change_basis_retail_to_core(retail_basis) -> list[list[float]]:
    # Core axes are retail X,Z,Y. The permutation is its own inverse.
    permutation = [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]
    return _matrix_multiply(_matrix_multiply(permutation, retail_basis), permutation)


def _authored_transform(position, orientation) -> dict[str, list[int]]:
    basis = _retail_basis(orientation)
    return {
        "retailBasisFloatBits": [
            _float_bits(component) for row in basis for component in row
        ],
        "retailEulerFloatBits": [_float_bits(component) for component in orientation],
        "retailPositionFloatBits": [_float_bits(component) for component in position],
    }


def _mesh_emitters(inflated: bytes, parsed) -> dict[str, dict[str, object]]:
    offset = inflated.find(b"CEMT")
    if offset < 0 or offset + 12 > len(inflated):
        return {}
    size = struct.unpack_from("<I", inflated, offset + 4)[0]
    end = offset + 8 + size
    if end > len(inflated):
        raise RuntimeError("Level 100 mesh has a truncated CEMT payload")
    cursor = offset + 8
    record_size = struct.unpack_from("<I", inflated, cursor)[0]
    cursor += 4
    if record_size != 336 or (size - 4) % (record_size + 4) != 0:
        raise RuntimeError("Level 100 mesh has an unsupported CEMT layout")
    result: dict[str, dict[str, object]] = {}
    for _ in range((size - 4) // (record_size + 4)):
        record = inflated[cursor : cursor + record_size]
        part_index = struct.unpack_from("<I", inflated, cursor + record_size)[0]
        cursor += record_size + 4
        if part_index >= len(parsed.parts):
            raise RuntimeError("Level 100 CEMT refers to an invalid mesh part")
        name = record[76:332].split(b"\0", 1)[0].decode("ascii")
        if not name.startswith("Spawner"):
            continue
        if name in result:
            raise RuntimeError(f"Level 100 mesh has duplicate emitter {name}")
        transform = parsed.parts[part_index].transform
        result[name] = {
            "basis": transform.rows,
            "partOrdinal": part_index,
            "position": transform.position,
        }
    if cursor != end:
        raise RuntimeError("Level 100 CEMT payload did not reproduce")
    return result


def _spawn_pose(
    owner: dict[str, object],
    emitter: dict[str, object],
) -> dict[str, list[int]]:
    owner_position = owner["retailPosition"]
    owner_orientation = owner["retailOrientation"]
    local_position = emitter["position"]
    local_basis = emitter["basis"]
    if not isinstance(owner_position, list) or not isinstance(owner_orientation, list):
        raise RuntimeError("Level 100 spawn owner has invalid authored transform data")
    owner_basis = _retail_basis(owner_orientation)
    world_basis = _matrix_multiply(owner_basis, local_basis)
    translated = _matrix_vector(owner_basis, local_position)
    world_position = [
        owner_position[axis] + translated[axis] for axis in range(3)
    ]
    world_yaw = math.atan2(world_basis[1][0], world_basis[0][0])
    return _actor_pose(
        world_position,
        [_normalize_angle(world_yaw), 0.0, 0.0],
        world_basis,
    )


def _build_actor_definition_set(
    objects: list[dict[str, object]],
    level_actors: list[dict[str, object]],
    emitters_by_mesh: dict[str, dict[str, dict[str, object]]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    actor_definitions: list[dict[str, object]] = []

    def add_actor(
        *,
        identity: str,
        name: str,
        definition_name: str | None,
        script_name: str | None,
        mesh_binding: str | None,
        is_static: bool,
        active: bool,
        health: int,
        authored_transform: dict[str, list[int]],
        pose: dict[str, list[int]],
        thing_type_mask: int = 0,
        target_group: str = "None",
        target_ordinal: int = 0,
        trigger: str | None = None,
    ) -> None:
        actor_definitions.append(
            {
                "active": active,
                "authoredOrder": len(actor_definitions),
                "authoredTransform": authored_transform,
                "definitionIdentity": identity,
                "definitionName": definition_name,
                "initialHealth": health,
                "initialPose": pose,
                "isStatic": is_static,
                "meshBinding": mesh_binding,
                "name": name,
                "scriptName": script_name,
                "thingTypeMask": thing_type_mask,
                "targetGroup": target_group,
                "targetOrdinal": target_ordinal,
                "trigger": trigger,
            }
        )

    static_by_name: dict[str, dict[str, object]] = {}
    for item in objects:
        name = str(item["name"])
        if name in LEVEL100_SETUP_SCRIPT_BINDINGS and name in static_by_name:
            raise RuntimeError(f"Level 100 has duplicate mission actor name {name}")
        static_by_name[name] = item
        add_actor(
            identity=f"wres:bswd:{int(item['ordinal']):04d}",
            name=name,
            definition_name=str(item["definition"]),
            # The released Setup program assigns these scripts at runtime.
            script_name=str(item["script"]) or None,
            mesh_binding=str(item["mesh"]),
            is_static=True,
            active=bool(item["active"]),
            health=0,
            authored_transform=_authored_transform(
                item["retailPosition"], item["retailOrientation"]
            ),
            pose=_actor_pose(item["retailPosition"], item["retailOrientation"]),
        )

    trigger_by_name = {
        "Target Zone 1": "TargetZone1",
        "Firing Range": "FiringRange",
        "Target Zone 2": "TargetZone2",
        "Target Zone 3": "TargetZone3",
        "Target Zone 4": "TargetZone4",
    }
    target_by_record = {
        9: ("Target Tank 2", "m_f_pulsetank_training.msh.aya", "StaticTargets", 2, 6_000),
        11: ("Target Warehouse", "m_m_warehouse.msh.aya", "StaticTargets", 4, 50_000),
        12: ("Target Tank 3", "m_f_pulsetank_training.msh.aya", "StaticTargets", 3, 6_000),
        # The authored actor is the distinct Flyby instance. Airfield later spawns
        # the AirTrainer mission actor through SpawnerB.
        40: ("Air Trainer", "m_FA_F24_training.msh.aya", "None", 0, 0),
    }
    physical_actor_ordinals = {
        0, 9, 11, 12, 13, 14, 15, 16, 19, 21, 40,
    }
    for item in level_actors:
        ordinal = int(item["ordinal"])
        if ordinal not in physical_actor_ordinals:
            continue
        serialized_name = str(item["name"])
        if ordinal == 0:
            name = "Player 1"
            definition_name = "BattleEngine"
            mesh_binding = "m_f_be1.msh.aya"
        elif ordinal in target_by_record:
            name, mesh_binding, _, _, _ = target_by_record[ordinal]
            definition_name = str(item["definition"])
        elif serialized_name:
            name = serialized_name
            definition_name = str(item["definition"]) or {
                36: "General Volume",
            }.get(int(item["thingType"]), f"Level Actor Type {item['thingType']}")
            mesh_binding = None
        else:
            name = {21: "Transporter"}.get(ordinal, f"Level Actor {ordinal:02d}")
            definition_name = str(item["definition"]) or {
                15: "BattleEngine",
            }.get(int(item["thingType"]), f"Level Actor Type {item['thingType']}")
            mesh_binding = None

        if ordinal == 21:
            mesh_binding = "m_f_lifter.msh.aya"

        target_group = "None"
        target_ordinal = 0
        health = 0
        if ordinal in target_by_record:
            _, _, target_group, target_ordinal, health = target_by_record[ordinal]
        trigger = trigger_by_name.get(serialized_name)
        if trigger is not None:
            if item["thingType"] != 36 or item["radius"] != 5.0:
                raise RuntimeError(f"Level 100 trigger {serialized_name} changed")

        add_actor(
            identity=f"wres:rlwd:{ordinal:04d}",
            name=name,
            definition_name=definition_name,
            script_name=str(item["script"]) or None,
            mesh_binding=mesh_binding,
            is_static=int(item["thingType"]) not in (8, 15),
            active=bool(item["active"]),
            health=health,
            authored_transform=_authored_transform(
                item["retailPosition"], item["retailOrientation"]
            ),
            pose=_actor_pose(item["retailPosition"], item["retailOrientation"]),
            thing_type_mask=8 if ordinal == 0 else 0,
            target_group=target_group,
            target_ordinal=target_ordinal,
            trigger=trigger,
        )

    if len(actor_definitions) != 44:
        raise RuntimeError(
            f"Level 100 actor definition set has {len(actor_definitions)} actors instead of 44"
        )

    owner_identity = {
        "Tank Factory": "wres:bswd:0001",
        "Airfield": "wres:bswd:0023",
    }
    spawn_rows = (
        ("Tank Factory", "Target Tank", "SpawnerA", "TargetTank1", "m_f_pulsetank_training.msh.aya", "StaticTargets", 1, 4),
        ("Tank Factory", "Target Truck", "SpawnerA", "TargetTruck1", "m_f_truck_training.msh.aya", "TargetTrucks", 1, 3),
        ("Tank Factory", "Target Truck", "SpawnerA", "TargetTruck2", "m_f_truck_training.msh.aya", "TargetTrucks", 2, 3),
        ("Tank Factory", "Target Truck", "SpawnerA", "TargetTruck3", "m_f_truck_training.msh.aya", "TargetTrucks", 3, 3),
        ("Tank Factory", "Target Tank", "SpawnerA", "TargetTank2", "m_f_pulsetank_training.msh.aya", "MovingTargets", 0, 6),
        ("Tank Factory", "Target Truck", "SpawnerA", "TargetTank2", "m_f_truck_training.msh.aya", "MovingTargets", 0, 6),
        ("Airfield", "Air Trainer", "SpawnerB", "AirTrainer", "m_FA_F24_training.msh.aya", "AirTrainer", 1, 1),
        ("Airfield", "Target Drone", "SpawnerB", "AirborneDrone1", "m_FA_F24_training.msh.aya", "AirborneTargets1", 0, 3),
        ("Airfield", "Target Drone", "SpawnerA", "AirborneDrone2", "m_FA_F24_training.msh.aya", "AirborneTargets2", 0, 6),
        ("Airfield", "Target Drone", "SpawnerB", "AirborneDrone2", "m_FA_F24_training.msh.aya", "AirborneTargets2", 0, 6),
    )
    spawn_definitions: list[dict[str, object]] = []
    for (
        owner_name,
        definition_name,
        spawner_name,
        script_name,
        mesh_binding,
        target_group,
        fixed_ordinal,
        maximum_group_actors,
    ) in spawn_rows:
        owner = static_by_name[owner_name]
        emitter = emitters_by_mesh[str(owner["mesh"])][spawner_name]
        local_position = emitter["position"]
        local_basis = emitter["basis"]
        spawn_definitions.append(
            {
                "active": True,
                "authoredEmitterTransform": {
                    "localBasisFloatBits": [
                        _float_bits(component)
                        for row in local_basis
                        for component in row
                    ],
                    "localPositionFloatBits": [
                        _float_bits(component) for component in local_position
                    ],
                },
                "authoredOrder": len(spawn_definitions),
                "definitionIdentity": (
                    f"spawn:{owner_name}:{definition_name}:{spawner_name}:{script_name}"
                ),
                "definitionName": definition_name,
                "fixedTargetOrdinal": fixed_ordinal,
                "initialHealth": (
                    6_000
                    if definition_name == "Target Tank"
                    else 3_000
                    if definition_name == "Target Truck"
                    else 0
                ),
                "initialPose": _spawn_pose(owner, emitter),
                "maximumGroupActors": maximum_group_actors,
                "meshBinding": mesh_binding,
                "ownerDefinitionIdentity": owner_identity[owner_name],
                "scriptName": script_name,
                "spawnerName": spawner_name,
                "targetGroup": target_group,
                "thingTypeMask": 0,
            }
        )
    return actor_definitions, spawn_definitions


def _round_scaled_away(value: float, scale: int) -> int:
    scaled = value * scale
    return math.floor(scaled + 0.5) if scaled >= 0 else math.ceil(scaled - 0.5)


def _contact_part_records(parsed) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for index, part in enumerate(parsed.parts):
        rows = part.transform.rows
        local = part.bounding_box.center
        if (
            part.bounding_box.valid not in {0, 1}
            or not all(
                math.isfinite(value)
                for value in (
                    *local,
                    *part.bounding_box.half_extents,
                    part.bounding_box.radius,
                )
            )
            or any(value < 0 for value in part.bounding_box.half_extents)
            or part.bounding_box.radius < 0
        ):
            raise RuntimeError(f"mesh part {part.name} has an invalid collision BBOX")
        center = [
            sum(rows[axis][component] * local[component] for component in range(3))
            + part.transform.position[axis]
            for axis in range(3)
        ]
        vertices: list[int] = []
        for vertex in part.vertices:
            position = vertex.position
            transformed = [
                sum(rows[axis][component] * position[component] for component in range(3))
                + part.transform.position[axis]
                for axis in range(3)
            ]
            if not all(math.isfinite(value) for value in transformed):
                raise RuntimeError(
                    f"mesh part {part.name} has a non-finite contact vertex"
                )
            vertices.extend(
                _round_scaled_away(value, 1_000) for value in transformed
            )

        triangles: list[int] = []
        for group in part.groups:
            indices = group.indices
            for ordinal in range(len(indices) - 2):
                if ordinal % 2 == 0:
                    a, b, c = indices[ordinal : ordinal + 3]
                else:
                    b, a, c = indices[ordinal : ordinal + 3]
                if len({a, b, c}) == 3:
                    triangles.extend((a, b, c))

        half_extents = [
            math.ceil(value * 1_000.0)
            for value in part.bounding_box.half_extents
        ]
        segment_value = max(part.bounding_box.half_extents)
        records.append(
            {
                "centerMillimeters": [
                    _round_scaled_away(value, 1_000) for value in center
                ],
                "collidable": (
                    part.bounding_box.valid == 1
                    and all(value > 0 for value in half_extents)
                    and bool(part.vertices)
                ),
                "halfExtentsMillimeters": half_extents,
                "index": index,
                "name": part.name,
                "orientationPartsPerMillion": [
                    _round_scaled_away(value, 1_000_000)
                    for row in rows
                    for value in row
                ],
                "parent": -1 if part.parent is None else part.parent,
                "reference": -1 if part.reference is None else part.reference,
                "segmentValueBits": struct.unpack(
                    "<I", struct.pack("<f", segment_value)
                )[0],
                "triangles": triangles,
                "type": part.part_type,
                "verticesMillimeters": vertices,
            }
        )
    return records


def _level100_contact_asset(
    objects: list[dict[str, object]],
    mesh_inputs: dict[str, tuple[Path, bytes, dict]],
    mesh_records: dict[str, dict[str, object]],
    parse_cmsh_stream,
    inflate_aya,
    game_root: Path,
) -> bytes:
    contact_mesh_keys = set(STATIC_MESH_BY_DEFINITION.values())
    parsed_static = {
        mesh_key: parse_cmsh_stream(inflate_aya(source[1]))
        for mesh_key, source in mesh_inputs.items()
        if mesh_key in contact_mesh_keys
    }
    instances: list[dict[str, object]] = []
    for world_object in sorted(objects, key=lambda item: int(item["ordinal"])):
        mesh_key = str(world_object["mesh"])
        position = world_object["retailPosition"]
        yaw_pitch_roll = world_object["retailOrientation"]
        instances.append(
            {
                "authoredElevationMillimeters": _round_scaled_away(
                    -10.0 - float(position[2]),
                    1_000,
                ),
                "baseClearanceMillimeters": (
                    0
                    if world_object["definition"] == "SAT Turret"
                    else _round_scaled_away(
                        float(mesh_records[mesh_key]["baseClearance"]),
                        1_000,
                    )
                ),
                "definition": world_object["definition"],
                "id": world_object["ordinal"],
                "name": world_object["name"],
                "positionMillimeters": [
                    _round_scaled_away(float(position[0]) - 288.6875, 1_000),
                    _round_scaled_away(float(position[1]) - 243.25, 1_000),
                ],
                "retailPositionBits": [
                    struct.unpack("<I", struct.pack("<f", float(value)))[0]
                    for value in position
                ],
                "retailYawPitchRollBits": [
                    struct.unpack("<I", struct.pack("<f", float(value)))[0]
                    for value in yaw_pitch_roll
                ],
                "rootMode": "authored-terrain-water",
            }
        )

    definitions = [
        {
            "definition": definition,
            "mesh": mesh_key,
            "parts": _contact_part_records(parsed_static[mesh_key]),
        }
        for definition, mesh_key in STATIC_MESH_BY_DEFINITION.items()
    ]

    physics = _physics_records(
        _read_exact(game_root / PHYSICS_DEFINITIONS, PHYSICS_DEFINITIONS_SHA256)
    )
    direct_hashes = {
        Path(source_name).name.casefold(): expected_hash
        for _, source_name, expected_hash in DIRECT_ASSETS
    }
    target_definitions: list[dict[str, object]] = []
    target_source_hashes: dict[str, str] = {}
    for definition in ("Target Tank", "Warehouse"):
        fields = physics[(1, definition)]
        mesh_name = _definition_string(fields, 9)
        if not mesh_name.casefold().endswith(".msh"):
            mesh_name += ".msh"
        source_name = f"m_{mesh_name}.aya"
        expected_hash = direct_hashes.get(source_name.casefold())
        if expected_hash is None:
            raise RuntimeError(
                f"Level 100 target definition has no retained mesh: {definition}"
            )
        source = _read_exact(
            game_root / "data/resources/meshes" / source_name,
            expected_hash,
        )
        parsed = parse_cmsh_stream(inflate_aya(source))
        destruction_fields = physics[(6, _definition_string(fields, 10))]
        particle_descriptor = _definition_string(destruction_fields, 2)
        if any(
            _definition_string(destruction_fields, field_id) != particle_descriptor
            for field_id in (5, 6, 7)
        ):
            raise RuntimeError(
                f"Level 100 target destruction variants diverged: {definition}"
            )
        target_definitions.append(
            {
                "definition": definition,
                "destructionParticleDescriptor": particle_descriptor,
                "destructionPhysicsDefinition": _definition_string(fields, 10),
                "destructionSoundDescriptor": _definition_string(
                    destruction_fields, 10
                ),
                "maximumLifeBits": struct.unpack("<I", fields[3])[0],
                "mesh": source_name,
                "parts": _contact_part_records(parsed),
            }
        )
        target_source_hashes[definition] = expected_hash

    round_fields = physics[(4, "Mech Pulse Bolt Medium")]
    hit_fields = physics[(6, _definition_string(round_fields, 9))]
    hit_particle_descriptor = _definition_string(hit_fields, 2)
    if (
        round_fields[12] != struct.pack("<I", 0x3D8F5C29)
        or any(
            _definition_string(hit_fields, field_id) != hit_particle_descriptor
            for field_id in (5, 6, 7)
        )
    ):
        raise RuntimeError("Level 100 medium pulse contact contract changed")

    document = {
        "definitionCount": len(definitions),
        "definitions": definitions,
        "instanceCount": len(instances),
        "instances": instances,
        "partCount": (
            sum(len(row["parts"]) for row in definitions)
            + sum(len(row["parts"]) for row in target_definitions)
        ),
        "pulseRound": {
            "impactParticleDescriptor": hit_particle_descriptor,
            "impactPhysicsDefinition": _definition_string(round_fields, 9),
            "impactSoundDescriptor": _definition_string(hit_fields, 10),
            "radiusMillimeters": _round_scaled_away(
                struct.unpack("<f", round_fields[12])[0], 1_000
            ),
        },
        "schema": "onslaught.level100-contact-owners.v3",
        "staticMeshCount": len(parsed_static),
        "staticSourceAggregateSha256": (
            LEVEL100_CONTACT_SOURCE_AGGREGATE_SHA256
        ),
        "targetDefinitionCount": len(target_definitions),
        "targetDefinitions": target_definitions,
        "targetSourceSha256": target_source_hashes,
    }
    return (
        json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


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
    level_actors, waypoint_paths = _parse_level_world_actors_and_waypoints(raw_level)
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
    emitters_by_mesh: dict[str, dict[str, dict[str, object]]] = {}

    for mesh_key in STATIC_MESH_KEYS:
        matches = resolver.mesh_index.get(f"{mesh_key}.msh".lower(), [])
        if len(matches) != 1:
            raise RuntimeError(f"expected one exact loose mesh for {mesh_key}, found {len(matches)}")
        source_path = Path(matches[0])
        relative = source_path.relative_to(game_root)
        if mesh_key in PINE_MESH_KEYS:
            data = _read_exact(
                source_path,
                PINE_MESH_SHA256[PINE_MESH_KEYS.index(mesh_key)],
            )
        else:
            data = source_path.read_bytes()
        inflated = inflate_aya(data)
        parsed = parse_cmsh_stream(inflated)
        if mesh_key in ("fb_tank_factory", "fb_aircraft_factory"):
            emitters_by_mesh[mesh_key] = _mesh_emitters(inflated, parsed)
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

    if (
        set(emitters_by_mesh) != {"fb_tank_factory", "fb_aircraft_factory"}
        or set(emitters_by_mesh["fb_tank_factory"]) != {"SpawnerA", "SpawnerB"}
        or set(emitters_by_mesh["fb_aircraft_factory"]) != {"SpawnerA", "SpawnerB"}
    ):
        raise RuntimeError("Level 100 authored spawner emitters changed")
    actor_definitions, spawn_definitions = _build_actor_definition_set(
        objects,
        level_actors,
        emitters_by_mesh,
    )
    physics = _physics_records(
        _read_exact(
            game_root / PHYSICS_DEFINITIONS,
            PHYSICS_DEFINITIONS_SHA256,
        )
    )
    motion_definitions = _level100_actor_motion_definitions(physics)

    pine_views = _pine_imposter_views(raw_level)
    pine_centers = [
        _pine_global_center(mesh_inputs[mesh_key][1], inflate_aya, variant)
        for variant, mesh_key in enumerate(PINE_MESH_KEYS)
    ]
    pine_atlas_source = Path(PINE_IMPOSTER_TEXTURE[0])
    pine_atlas_data = _read_exact(
        game_root / pine_atlas_source,
        PINE_IMPOSTER_TEXTURE[1],
    )
    source_data[pine_atlas_source] = pine_atlas_data

    water_sources: dict[str, Path] = {}
    for key, source_name, expected_hash in WATER_TEXTURES:
        source = Path(source_name)
        source_data[source] = _read_exact(game_root / source, expected_hash)
        water_sources[key] = source
    if len(source_data) != 62:
        raise RuntimeError(f"static-world source set has {len(source_data)} files instead of 62")
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

    pine_atlas_key = "pine-imposters-100"
    pine_atlas_destination = (
        STATIC_WORLD_ROOT / "Textures/pine-imposters-100.texture.aya"
    )
    pine_atlas_resource_path = (
        "res://Assets/Level100/StaticWorld/Textures/"
        "pine-imposters-100.texture.aya"
    )
    pine_atlas_target = stage / pine_atlas_destination
    pine_atlas_target.parent.mkdir(parents=True, exist_ok=True)
    pine_atlas_target.write_bytes(pine_atlas_data)
    outputs.append((pine_atlas_destination, PINE_IMPOSTER_TEXTURE[1]))
    texture_records[pine_atlas_key] = {
        "blendTextureAlpha": False,
        "compression": "Dxt2",
        "height": 256,
        "resourcePath": pine_atlas_resource_path,
        "sha256": PINE_IMPOSTER_TEXTURE[1],
        "sourcePath": pine_atlas_source.as_posix(),
        "width": 1024,
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
        "actorDefinitionProvenance": {
            "baseWorld": "100_res_PC.aya WRES/WRLD/BSWD v50 records 0..34",
            "compiledScripts": "100_res_PC.aya WRES/WRLD/RLWD ordered Level 100 object code",
            "levelWorld": "100_res_PC.aya WRES/WRLD/RLWD v50 initial actors 0..44",
            "motionDefinitions": "exact default physics.dat Unit fields plus canonical Steam class/radius dispatch",
            "spawnerTransforms": "exact CEMT named emitter part transforms from the released Tank Factory and Airfield meshes",
            "startupSpawn": "TankFactory compiled initializer plus exact SpawnerA CEMT transform; no settled target pose is pre-seeded",
        },
        "actorDefinitions": actor_definitions,
        "motionDefinitions": motion_definitions,
        "meshes": mesh_records,
        "objects": objects,
        "pineBillboards": {
            "fastStandingViewPhase": PINE_FAST_STANDING_VIEW_PHASE,
            "meshQualityDistance": PINE_MESH_QUALITY_DISTANCE,
            "texture": pine_atlas_key,
            "variants": [
                {
                    "centerOffset": pine_centers[variant],
                    "views": pine_views[variant],
                }
                for variant in range(4)
            ],
        },
        "pineInstanceCount": len(pines),
        "pines": pines,
        "schema": "onslaught.level100-static-world.v13",
        "sourceAggregateSha256": aggregate,
        "sourceArchiveSha256": LEVEL_ARCHIVE_SHA256,
        "physicsSourceSha256": PHYSICS_DEFINITIONS_SHA256,
        "suppressedFernCount": fern_count,
        "textures": texture_records,
        "unitRecordCount": 35,
        "visibleObjectCount": len(objects),
        "spawnDefinitions": spawn_definitions,
        "waypointPaths": waypoint_paths,
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

    contact_asset = _level100_contact_asset(
        objects,
        mesh_inputs,
        mesh_records,
        parse_cmsh_stream,
        inflate_aya,
        game_root,
    )
    contact_hash = _sha256(contact_asset)
    if contact_hash != LEVEL100_CONTACT_ASSET_SHA256:
        raise RuntimeError(
            "Level 100 contact owners did not reproduce exactly "
            f"(SHA-256 {contact_hash})"
        )
    contact_target = stage / LEVEL100_CONTACT_ASSET
    contact_target.parent.mkdir(parents=True, exist_ok=True)
    contact_target.write_bytes(contact_asset)
    outputs.append((LEVEL100_CONTACT_ASSET, contact_hash))
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


def _frontend_localization_bytes(data: bytes) -> bytes:
    if (
        len(data) < 16
        or struct.unpack_from("<I", data, 0)[0] != 0xFFFFFFBB
        or struct.unpack_from("<I", data, 4)[0] != 3
    ):
        raise RuntimeError("unsupported English language-table framing")

    count = struct.unpack_from("<I", data, 8)[0]
    if count != 2571:
        raise RuntimeError(f"unsupported English language-table count: {count}")

    entries_offset = 12
    text_pool_offset = entries_offset + count * 12 + 4
    if text_pool_offset > len(data):
        raise RuntimeError("truncated English language-table entries")

    offsets: dict[int, int] = {}
    wanted_ids = set(FRONTEND_TEXT_IDS.values())
    for index in range(count):
        entry_offset = entries_offset + index * 12
        text_id, text_offset_words = struct.unpack_from("<II", data, entry_offset)
        if text_id in wanted_ids:
            if text_id in offsets:
                raise RuntimeError(f"duplicate frontend text ID 0x{text_id:08X}")
            offsets[text_id] = text_offset_words

    if set(offsets) != wanted_ids:
        missing = wanted_ids - set(offsets)
        raise RuntimeError(
            "English language table is missing frontend text IDs: "
            + ", ".join(f"0x{text_id:08X}" for text_id in sorted(missing))
        )

    strings: dict[str, str] = {}
    for key, text_id in FRONTEND_TEXT_IDS.items():
        position = text_pool_offset + offsets[text_id] * 2
        code_units: list[int] = []
        for _ in range(8192):
            if position + 2 > len(data):
                raise RuntimeError(f"truncated frontend text ID 0x{text_id:08X}")
            code_unit = struct.unpack_from("<H", data, position)[0]
            position += 2
            if code_unit == 0:
                break
            code_units.append(code_unit)
        else:
            raise RuntimeError(f"unterminated frontend text ID 0x{text_id:08X}")
        strings[key] = struct.pack(f"<{len(code_units)}H", *code_units).decode("utf-16le")

    document = {
        "culture": "en",
        "schema": "onslaught.frontend-strings.v1",
        "sourceSha256": ENGLISH_LANGUAGE_TABLE_SHA256,
        "strings": strings,
    }
    output = (
        json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    actual = _sha256(output)
    if actual != FRONTEND_LOCALIZATION_SHA256:
        raise RuntimeError(
            "frontend localization did not reproduce exactly "
            f"(SHA-256 {actual})"
        )
    return output


def _require_chunk(source: bytes, offset: int, tag: bytes, payload_size: int) -> int:
    if (
        offset < 0
        or offset + 8 > len(source)
        or source[offset : offset + 4] != tag
        or struct.unpack_from("<I", source, offset + 4)[0] != payload_size
        or offset + 8 + payload_size > len(source)
    ):
        raise RuntimeError(f"Level 100 has invalid {tag.decode('ascii')} framing")
    return offset + 8


def _parse_map_texture(
    raw_level: bytes,
    width: int,
    framed_size: int,
    expected_hash: str,
) -> tuple[bytes, tuple[int, ...]]:
    source = _extract_chunk(raw_level, b"MAPT", framed_size, expected_hash)
    _require_chunk(source, 0, b"MAPT", len(source) - 8)
    cmtx = _require_chunk(source, 8, b"CMTX", 76)
    if (
        struct.unpack_from("<I", source, cmtx)[0] != 0xDEAD
        or struct.unpack_from("<I", source, cmtx + 8)[0] != 0xDEAD
        or struct.unpack_from("<iii", source, cmtx + 0x10)
        != (width * width, 6, width)
    ):
        raise RuntimeError(f"Level 100 {width}x{width} MAPT metadata changed")

    data_header = cmtx + 76
    data_size = width * width * 6
    data_offset = _require_chunk(source, data_header, b"DATA", data_size)
    palette_header = data_offset + data_size
    palette_offset = _require_chunk(source, palette_header, b"PALT", 6_144)
    if palette_offset + 6_144 != len(source):
        raise RuntimeError("Level 100 root MAPT has trailing data")
    return source[data_offset : data_offset + data_size], struct.unpack_from(
        "<1536I", source, palette_offset
    )


def _parse_root_map_texture(raw_level: bytes) -> tuple[bytes, tuple[int, ...]]:
    _, width, framed_size, expected_hash = LANDSCAPE_MAP_TEXTURES[0]
    return _parse_map_texture(raw_level, width, framed_size, expected_hash)


def _parse_landscape_map_textures(
    raw_level: bytes,
) -> tuple[tuple[int, bytes, tuple[int, ...]], ...]:
    result: list[tuple[int, bytes, tuple[int, ...]]] = []
    for logical_level, width, framed_size, expected_hash in LANDSCAPE_MAP_TEXTURES:
        data, palettes = _parse_map_texture(
            raw_level,
            width,
            framed_size,
            expected_hash,
        )
        if logical_level != int(math.log2(width // 16)):
            raise RuntimeError("landscape MAPT logical-level ordering changed")
        result.append((width, data, palettes))
    return tuple(result)


def _parse_root_mixer_map(
    raw_level: bytes,
) -> tuple[list[tuple[tuple[int, ...], bytes]], bytes]:
    source = _extract_chunk(
        raw_level,
        b"MMAP",
        877_597,
        "45045d248e27366080614c1ad26fc9e711bc9656f4f79210eac63d2a20938361",
    )
    _require_chunk(source, 0, b"MMAP", len(source) - 8)
    cells: list[tuple[tuple[int, ...], bytes]] = []
    position = 8
    for cell_index in range(64 * 64):
        if position + 8 > len(source) or source[position : position + 4] != b"MCEL":
            raise RuntimeError(f"Level 100 MMAP cell {cell_index} is not framed")
        cell_size = struct.unpack_from("<I", source, position + 4)[0]
        cell_payload = _require_chunk(
            source,
            position,
            b"MCEL",
            cell_size,
        )
        record = _require_chunk(source, cell_payload, b"CMCL", 20)
        layer_count = struct.unpack_from("<i", source, record)[0]
        if (
            layer_count not in range(1, 6)
            or struct.unpack_from("<I", source, record + 4)[0] != 0xDEAD
        ):
            raise RuntimeError(f"Level 100 MMAP cell {cell_index} is invalid")
        material_ids = struct.unpack_from(f"<{layer_count}H", source, record + 8)
        if any(material_id >= 6 for material_id in material_ids):
            raise RuntimeError(f"Level 100 MMAP cell {cell_index} selects an invalid material")
        weights_header = record + 20
        weights_size = layer_count * 81
        weights = _require_chunk(source, weights_header, b"MXRS", weights_size)
        if cell_size != 36 + weights_size:
            raise RuntimeError(f"Level 100 MMAP cell {cell_index} has an invalid envelope")
        cells.append((material_ids, source[weights : weights + weights_size]))
        position += 8 + cell_size

    shade_offset = _require_chunk(source, position, b"MSHD", 512 * 512)
    if shade_offset + (512 * 512) != len(source):
        raise RuntimeError("Level 100 MMAP has trailing data")
    shade = source[shade_offset:]
    if any(value > 63 for value in shade):
        raise RuntimeError("Level 100 MMAP contains an invalid shade index")
    return cells, shade


def _static_shadow_cells(
    raw_level: bytes,
) -> tuple[bytes, tuple[bytes | None, ...]]:
    source = _extract_chunk(
        raw_level,
        b"SSHD",
        483_608,
        "d64b2d1503a59ab8aec15bcc92a3736bf23b6104ed0b557d1710f06dd74a5c0a",
    )
    shds = _chunk_payload(source[8:], b"SHDS")
    children = _chunk_records(shds)
    if (
        len(children) != 2
        or children[0][0] != b"DATA"
        or len(children[0][1]) != 4
        or children[1][0] != b"SDAT"
    ):
        raise RuntimeError("Level 100 SSHD has an unexpected envelope")
    owner_count = struct.unpack_from("<I", children[0][1])[0]
    owners = _chunk_records(children[1][1])
    if owner_count != 30 or len(owners) != owner_count or any(tag != b"CSSD" for tag, _ in owners):
        raise RuntimeError("Level 100 SSHD owner count changed")

    grid: list[bytearray | None] = [None] * (64 * 64)
    part_count = 0
    active_part_count = 0
    populated_cell_count = 0
    for _, owner in owners:
        if len(owner) < 24:
            raise RuntimeError("Level 100 CSSD is truncated")
        expected_parts = struct.unpack_from("<I", owner, 16)[0]
        parts = _chunk_records(owner[24:])
        if len(parts) != expected_parts or any(tag != b"SSPT" for tag, _ in parts):
            raise RuntimeError("Level 100 CSSD part count changed")
        part_count += len(parts)
        for _, part in parts:
            if len(part) < 20:
                raise RuntimeError("Level 100 SSPT is truncated")
            min_x, min_y, width, height, has_map = struct.unpack_from("<iiiii", part)
            if has_map not in (0, 1):
                raise RuntimeError(
                    "Level 100 SSPT metadata is invalid: "
                    f"{min_x},{min_y},{width},{height},{has_map}"
                )
            if has_map == 0:
                if len(part) != 20:
                    raise RuntimeError("Level 100 empty SSPT has trailing data")
                continue
            if width <= 0 or height <= 0:
                raise RuntimeError("Level 100 mapped SSPT has an invalid extent")
            active_part_count += 1
            smap = _chunk_payload(part[20:], b"SMAP")
            cursor = 0
            for local_y in range(height):
                for local_x in range(width):
                    if cursor + 4 > len(smap):
                        raise RuntimeError("Level 100 SMAP is truncated")
                    present = struct.unpack_from("<I", smap, cursor)[0]
                    cursor += 4
                    if present not in (0, 1):
                        raise RuntimeError("Level 100 SMAP has an invalid cell flag")
                    if present == 0:
                        continue
                    if cursor + 512 > len(smap):
                        raise RuntimeError("Level 100 SMAP bitmap is truncated")
                    bits = smap[cursor : cursor + 512]
                    cursor += 512
                    cell_x = min_x + local_x
                    cell_y = min_y + local_y
                    if not (0 <= cell_x < 64 and 0 <= cell_y < 64):
                        raise RuntimeError("Level 100 SMAP cell escaped the terrain")
                    grid_index = (cell_x * 64) + cell_y
                    destination = grid[grid_index]
                    if destination is None:
                        destination = bytearray(512)
                        grid[grid_index] = destination
                    for index, value in enumerate(bits):
                        destination[index] |= value
                    populated_cell_count += 1
            if cursor != len(smap):
                raise RuntimeError("Level 100 SMAP has trailing data")

    if (part_count, active_part_count, populated_cell_count) != (335, 275, 910):
        raise RuntimeError("Level 100 SSHD coverage changed")
    result = bytearray(512 * 512)
    for cell_y in range(64):
        for cell_x in range(64):
            bits = grid[(cell_x * 64) + cell_y]
            if bits is None:
                continue
            for local_y in range(8):
                source_y = local_y * 8
                for local_x in range(8):
                    source_x = local_x * 8
                    source_bit = (source_y * 64) + source_x
                    if bits[source_bit >> 3] & (1 << (source_bit & 7)):
                        target_x = (cell_x * 8) + local_x
                        target_y = (cell_y * 8) + local_y
                        result[(target_y * 512) + target_x] = 1
    if (
        sum(result) != 5_051
        or _sha256(result)
        != "0c67274b69599bf3832e6bc9e988a6436151c1a495aef720081c724f4111c03b"
    ):
        raise RuntimeError("Level 100 root static-shadow mask did not reproduce")
    return bytes(result), tuple(
        bytes(cell) if cell is not None else None for cell in grid
    )


def _static_shadow_mask(raw_level: bytes) -> bytes:
    return _static_shadow_cells(raw_level)[0]


def _lighting_gradient(sun_color: int, ambient_color: int) -> list[tuple[int, int, int]]:
    red_base = (((ambient_color >> 16) & 0xFF) << 8) // (((sun_color >> 16) & 0xFE) + 1)
    green_base = (ambient_color & 0xFF00) // (((sun_color >> 8) & 0xFE) + 1)
    blue_base = ((ambient_color & 0xFF) << 8) // ((sun_color & 0xFE) + 1)
    red = red_base << 8
    green = green_base << 8
    blue = blue_base << 8
    result: list[tuple[int, int, int]] = []
    for _ in range(64):
        red_value = min(((red >> 8) << 16) * 2, 0x00F80000) & 0x00F80000
        green_value = min(((green >> 8) << 11) * 2, 0x0007E000) & 0x0007E000
        blue_value = min(((blue >> 3) & 0xFFFFFFE0) * 2, 0x00001F00) & 0x00001F00
        result.append((red_value, green_value, blue_value))
        red += (255 - red_base) * 4
        green += (255 - green_base) * 4
        blue += (255 - blue_base) * 4
    return result


def _signed32(value: int) -> int:
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def _pine_shadow_source(
    raw_level: bytes,
    raw_base: bytes,
) -> tuple[bytes, tuple[tuple[int, int, int], ...]]:
    dmkr = _extract_chunk(
        raw_base,
        b"DMKR",
        5_473,
        "c9c9d88dbf4248e967616fdd0d4a59b8528251e13daf16b14b974582e94fb7f1",
    )[8:]
    if len(dmkr) != 5_465 or struct.unpack_from("<I", dmkr)[0] != 6:
        raise RuntimeError("base DMKR metadata changed")
    alpha = dmkr[4:]
    _, pines, _ = _parse_static_world(raw_level)
    views = _pine_imposter_views(raw_level)
    descriptors: list[tuple[int, int, int]] = []
    last_x = 0.0
    last_y = 0.0
    for x_value, y_value, variant_value in pines:
        variant = int(variant_value)
        x = _f32(_f32(float(x_value)) - _f32(0.4))
        y = _f32(_f32(float(y_value)) + _f32(0.1))
        delta_x = _f32(x - last_x)
        delta_y = _f32(y - last_y)
        distance_squared = _f32(_f32(delta_x * delta_x) + _f32(delta_y * delta_y))
        if distance_squared < _f32(0.01):
            continue
        last_x = x
        last_y = y
        metric = max(views[variant][0][4], views[variant][0][5])
        bucket = min(int(round(_f32(_f32(metric) * _f32(6.0)))), 6)
        high_size = 1 << bucket
        center_x = int(round(_f32(x * _f32(16.0))))
        center_y = int(round(_f32(y * _f32(16.0))))
        top_x = center_x - (high_size >> 1)
        top_y = center_y - (high_size >> 1)
        cell_x = top_x >> 7
        cell_y = top_y >> 7
        if not (0 <= cell_x < 64 and 0 <= cell_y < 64):
            continue
        level = bucket - 4
        if level <= 0:
            continue
        descriptors.append((top_x >> 4, top_y >> 4, level))
    return alpha, tuple(descriptors)


def _apply_pine_shadows(
    pixels: list[int],
    raw_level: bytes,
    raw_base: bytes,
) -> None:
    alpha, descriptors = _pine_shadow_source(raw_level, raw_base)
    level_offsets = (0, 1, 5, 21, 85, 341, 1_365)

    for top_x, top_y, level in reversed(descriptors):
        dimension = 1 << level
        source_offset = level_offsets[level]
        for source_y in range(dimension):
            target_y = top_y + source_y
            if not 0 <= target_y < 512:
                continue
            for source_x in range(dimension):
                target_x = top_x + source_x
                if not 0 <= target_x < 512:
                    continue
                amount = alpha[source_offset + (source_y * dimension) + source_x]
                if amount >= 32:
                    continue
                target_index = (target_y * 512) + target_x
                destination = pixels[target_index]
                pair = ((destination << 16) | destination) & 0x07E0F81F
                scaled = ((pair * amount) >> 5) & 0x07E0F81F
                pixels[target_index] = ((scaled >> 16) + scaled) & 0xFFFF


def _render_root_terrain(raw_level: bytes, raw_base: bytes, height_field: bytes) -> bytes:
    map_data, palettes = _parse_root_map_texture(raw_level)
    cells, shade = _parse_root_mixer_map(raw_level)
    static_shadow = _static_shadow_mask(raw_level)
    chfd = _require_chunk(height_field, 8, b"CHFD", 5_084)
    if height_field[chfd + 0x1030] != 10 or height_field[chfd + 0x1094] != 0:
        raise RuntimeError("Level 100 no longer selects mixer set 10 and detail texture 00")
    sun_color = struct.unpack_from("<I", height_field, chfd + 0x107C)[0]
    ambient_color = struct.unpack_from("<I", height_field, chfd + 0x108C)[0]
    gradient = _lighting_gradient(sun_color, ambient_color)
    pixels = [0] * (512 * 512)

    for y in range(512):
        for x in range(512):
            tile_x = x // 8
            tile_y = y // 8
            local_x = x & 7
            local_y = y & 7
            cell_index = (tile_y * 64) + tile_x
            material_ids, weights = cells[cell_index]
            source_x = local_x + (8 if cell_index & 1 else 0)
            source_y = local_y + (8 if cell_index & 0x40 else 0)
            texel = (source_y * 16) + source_x
            palette_index = map_data[texel]
            color = palettes[palette_index]
            for layer, material_id in enumerate(material_ids):
                palette_index = map_data[(material_id * 256) + texel]
                candidate = palettes[(material_id * 256) + palette_index]
                weight = struct.unpack("b", bytes((weights[(layer * 81) + (local_y * 9) + local_x],)))[0]
                candidate = (candidate + ((weight << 24) & 0xFFFFFFFF)) & 0xFFFFFFFF
                difference = _signed32(candidate - color)
                if difference > 0x1FFFFFFF:
                    color = candidate
                elif difference >= 0:
                    blend = difference >> 26
                    color = (
                        (((color & 0x00F8F8FF) * (7 - blend) +
                          (candidate & 0x00F8F8FF) * blend) >> 3)
                        + (candidate & 0xFF000000)
                    ) & 0xFFFFFFFF

            red = color & 0xFF
            green = (color >> 8) & 0xFF
            blue = (color >> 16) & 0xFF
            shade_x = min(x + 1, 511)
            shade_y = min(y + 1, 511)
            shade_index = shade[(shade_y * 512) + shade_x]
            shade_index >>= static_shadow[(y * 512) + x]
            light_red, light_green, light_blue = gradient[shade_index]
            pixels[(y * 512) + x] = (
                ((green * light_green & 0x07E00000) +
                 (blue * light_blue & 0x001F0000) +
                 (red * light_red & 0xF8000000)) >> 16
            ) & 0xFFFF

    _apply_pine_shadows(pixels, raw_level, raw_base)
    return struct.pack("<262144H", *pixels)


def _render_terrain_hierarchy_source(raw_level: bytes, raw_base: bytes) -> bytes:
    maps = _parse_landscape_map_textures(raw_level)
    cells, shade = _parse_root_mixer_map(raw_level)
    _, shadow_cells = _static_shadow_cells(raw_level)
    pine_alpha, pine_descriptors = _pine_shadow_source(raw_level, raw_base)
    if (
        len(cells) != 4_096
        or len(shade) != 512 * 512
        or sum(shadow is not None for shadow in shadow_cells) != 211
        or len(pine_alpha) != 5_461
        or len(pine_descriptors) != 1_481
    ):
        raise RuntimeError("Level 100 terrain hierarchy source counts changed")

    output = bytearray(b"LTH1")
    output.extend(struct.pack("<II", 1, len(maps)))
    for width, data, palettes in maps:
        output.extend(struct.pack("<II", width, len(data)))
        output.extend(data)
        output.extend(struct.pack("<I", len(palettes)))
        output.extend(struct.pack(f"<{len(palettes)}I", *palettes))

    output.extend(struct.pack("<I", len(cells)))
    for material_ids, weights in cells:
        output.append(len(material_ids))
        output.extend(bytes(material_ids))
        output.extend(weights)

    output.extend(struct.pack("<I", len(shade)))
    output.extend(shade)

    populated_shadows: list[tuple[int, bytes]] = []
    for tile_y in range(64):
        for tile_x in range(64):
            shadow = shadow_cells[(tile_x * 64) + tile_y]
            if shadow is not None:
                populated_shadows.append(((tile_y * 64) + tile_x, shadow))
    output.extend(struct.pack("<I", len(populated_shadows)))
    for tile_index, shadow in populated_shadows:
        output.extend(struct.pack("<H", tile_index))
        output.extend(shadow)

    output.extend(struct.pack("<I", len(pine_alpha)))
    output.extend(pine_alpha)
    output.extend(struct.pack("<I", len(pine_descriptors)))
    for top_x, top_y, level in pine_descriptors:
        output.extend(struct.pack("<hhB", top_x, top_y, level))
    return bytes(output)


def _materialize(game_root: Path, stage: Path) -> tuple[tuple[Path, str], ...]:
    source_data: dict[Path, bytes] = {}
    for destination, source, expected in DIRECT_ASSETS + FRONTEND_ASSETS:
        data = _read_exact(game_root / source, expected)
        source_data[destination] = data
        target = stage / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    english_table = _read_exact(
        game_root / ENGLISH_LANGUAGE_TABLE,
        ENGLISH_LANGUAGE_TABLE_SHA256,
    )
    frontend_localization = _frontend_localization_bytes(english_table)
    frontend_localization_target = stage / FRONTEND_LOCALIZATION
    frontend_localization_target.parent.mkdir(parents=True, exist_ok=True)
    frontend_localization_target.write_bytes(frontend_localization)
    hud_manifest_hash = _materialize_level100_hud_manifest(stage)
    if hud_manifest_hash != LEVEL100_HUD_MANIFEST_SHA256:
        raise RuntimeError(
            "Level 100 HUD manifest did not reproduce exactly "
            f"(SHA-256 {hud_manifest_hash})"
        )

    level_archive = _read_exact(game_root / LEVEL_ARCHIVE, LEVEL_ARCHIVE_SHA256)
    tools_root = ROOT / "tools"
    sys.path.insert(0, str(tools_root))
    from aya_archive_inventory import inflate_aya_bytes

    raw_level = inflate_aya_bytes(level_archive)
    _, scripts = _parse_level_world_scripts(raw_level)
    for name, payload in scripts.items():
        script_target = stage / LEVEL100_SCRIPT_ROOT / f"level100-{name}.mso.bin"
        script_target.parent.mkdir(parents=True, exist_ok=True)
        script_target.write_bytes(payload)

    chunk_data: dict[bytes, bytes] = {}
    for destination, tag, expected_size, expected in CHUNKS:
        data = _extract_chunk(raw_level, tag, expected_size, expected)
        chunk_data[tag] = data
        target = stage / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    base_archive = _read_exact(game_root / BASE_ARCHIVE, BASE_ARCHIVE_SHA256)
    raw_base = inflate_aya_bytes(base_archive)
    root_terrain = _render_root_terrain(raw_level, raw_base, chunk_data[b"HFLD"])
    root_terrain_hash = _sha256(root_terrain)
    if root_terrain_hash != ROOT_TERRAIN_TEXTURE_SHA256:
        raise RuntimeError(
            "Level 100 root terrain did not reproduce exactly "
            f"(SHA-256 {root_terrain_hash})"
        )
    root_terrain_target = stage / ROOT_TERRAIN_TEXTURE
    root_terrain_target.parent.mkdir(parents=True, exist_ok=True)
    root_terrain_target.write_bytes(root_terrain)

    terrain_hierarchy = _render_terrain_hierarchy_source(raw_level, raw_base)
    terrain_hierarchy_hash = _sha256(terrain_hierarchy)
    if terrain_hierarchy_hash != TERRAIN_HIERARCHY_SOURCE_SHA256:
        raise RuntimeError(
            "Level 100 terrain hierarchy did not reproduce exactly "
            f"(SHA-256 {terrain_hierarchy_hash})"
        )
    terrain_hierarchy_target = stage / TERRAIN_HIERARCHY_SOURCE
    terrain_hierarchy_target.parent.mkdir(parents=True, exist_ok=True)
    terrain_hierarchy_target.write_bytes(terrain_hierarchy)

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
