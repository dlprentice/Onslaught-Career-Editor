# Level 100 opening assets

This directory owns the ignored local released heightfield,
macro/detail/cloud-shadow terrain inputs, cube-25 sky, four close-pine meshes,
two Firing Range target meshes, nine Pulse Cannon/target-destruction
effect textures, 25 exact mission effects, the tutorial music selection, and all
51 English character messages in the accepted Level 100 mission table. The
three shared front-end effects retain the startup lane's `Assets/Frontend` paths. Run
`npm run prepare:rebuild-assets` to materialize the exact supported files from a
user-provided retail installation. The payloads are not tracked in the current
source tree or included in release packages and remain copyright of their
respective rights holders; `rebuild/LICENSE` covers reconstruction code only.

`StaticWorld/level100-static-world.json` is a deterministic ignored manifest
derived from the exact released Level 100 archive. It owns all 33 visible
base-world objects, 24 selected non-tree mesh types, four pine mesh variants,
1,481 pine transforms, 34 mesh/water/imposter textures, their active material
signatures, and their exact hashes. The materializer converts those 28 meshes
and verifies a 62-file retail source set; those generated payloads are not
mirrored in this document.

`../../../OnslaughtRebuild.Core/Assets/Level100/level100-contact-owners.json`
is a separate ignored Core input derived from the supported physics definitions,
mesh archives and Level 100 placements. It retains hash-verified definitions
and deterministic millimetre-quantized projected topology for contact. It is a
locally materialized derivative, remains ignored, and is not a claim of
bit-identical retail collision geometry.

| Local materialized file | Role | SHA-256 |
| --- | --- | --- |
| `../../../OnslaughtRebuild.Core/Assets/Level100/level100-heightfield.hfld.bin` | Exact released `HFLD` chunk embedded in Core and adapted by Godot | `7A4C7C5B9400E2C8D2325CECB5C44701CD8A6E6F8609CBC8BC31D449C0620F5D` |
| `../../../OnslaughtRebuild.Core/Assets/Level100/level100-contact-owners.json` | Hash-verified deterministic contact projection for the 24 static definitions plus Target Tank and Warehouse | `FE5F109526E39231EA3D02898A035DBC7EB842B7B37776EC5EFDA7BA45F138B0` |
| `Source/level100-root-terrain.rgb565.bin` | Exact initial 512x512 root landscape pixels reconstructed from the released Level 100 and base archives | `6EB202F450926097930BEDCA440F0163A1886572981E3C69B4EDF9289A68AE2B` |
| `Source/level100-terrain-hierarchy.bin` | Exact retained sources for the five released logical landscape caches | `541EACD0AA75FAE8BEFB8A3E1505EA52AE6B1F6C1367C15C65D7DD23B7CFE977` |
| `Textures/terrain-detail-00.texture.aya` | Exact released 512×512 DXT1 `mixers%detail00.tga(0)R5G6B5.aya` selected by Level 100 | `7C9C22169D13ED8B7D6AD69286BDB59CC88F9AE3BFB6A9D3A0503D320386BFEF` |
| `Textures/terrain-cloud-shadow.texture.aya` | Exact released 256×256 DXT1 `clouds%shadow.tga(0)A8R8G8B8.aya` loaded by the landscape renderer | `FC7441887E494E4B18F2B16179ED42C17801B128D71E29D653A4E8B792869519` |
| `StaticWorld/Source/level100-water-surface.surf.bin` | Exact released 18,572-byte `SURF` shoreline payload | `C3177354FED3EB5A94DC72DEBF2465C32AB1D931DE79E5E88AC431043D3E917D` |
| `StaticWorld/Textures/water-reflection-00.texture.aya` | Exact released 512×512 DXT1 authored water reflection image | `41117238976776B114B8AF4D1E4FBCCD3AFB90245F46F59B353E83663CAC7B6E` |
| `StaticWorld/Textures/water-caustic-00.texture.aya` | Exact released 64×64 DXT1 caustic stage | `7F34EE7D90CA483893C3ED8B0BF01BDF07B9A0B0F4A48F9DF5FEFD961D796F0A` |
| `StaticWorld/Textures/water-waves.texture.aya` | Exact released 128×128 DXT1 shoreline-wave stage | `6EC848D1F9801BE12F3A6591D6A4F5D5ECF1FC9F21D1A4242E1D681D826AB078` |
| `StaticWorld/Textures/water-sun-blob.texture.aya` | Exact released 128×128 RGBA8 water-sun blob | `5D97F24F514383C928C58C7F333BF489888B6A402004213FFBAAAAD2EF30A53E` |
| `StaticWorld/Textures/water-sun-reflection.texture.aya` | Exact released 64×64 RGBA8 sun-reflection stage | `A65940D6CDFE93F8B8820EFB883FD33166AEC63863ED894673466F3F58527AB4` |
| `Source/m_f_pulsetank_training.msh.aya` | Released Firing Range Target Tank CMSH archive | `9B2CFDCEB86ED700ED924051FBFF13C32DC30BD8F8B948EA1CF8AA9FBFE8B97B` |
| `level100-target-tank.obj` | Static Target Tank geometry and base-material group consumed by Godot | `6D3827B58FE7A4728EFE1EFC6A7CED7A08A0B642891DCB1F18377A4B3D61D244` |
| `Source/m_m_warehouse.msh.aya` | Released Firing Range Warehouse CMSH archive | `61FE5465BD7AFFEDF749AD784209BE02B2E4DD28631E70386C3810302B5F6F15` |
| `level100-target-warehouse.obj` | Static intact Warehouse geometry and base-material groups consumed by Godot | `271ADEFEDCB0942A584014FF51FC7330769AB8FD95BC6EA5987BAC305C60F658` |
| `Textures/target-tank.texture.aya` | Released 512×512 DXT2 Target Tank base texture | `97DDD1E18E45B19E249E91E881D773D80D36768A2CD48F6549A769C2559A7B7E` |
| `Textures/target-warehouse-m001.texture.aya` | Released 512×512 DXT2 Warehouse base texture used by material groups 0 and 1 | `689B184AB8A5D03F33B69E5C35EDCFDFDEC12AA9B4B31F7C74CE5209F6236A49` |
| `Textures/target-warehouse-m002.texture.aya` | Released 512×512 DXT2 Warehouse base texture used by material group 3 | `8FABADBE1C5AF067A740CF05DEBD1C952C628FD5FA3EA92B8202094704B8A20D` |
| `Textures/pulse-bolt-blue-spark.texture.aya` | Exact released 64×64 DXT2 `Particle%Blue Spark 2.tga(0)A4R4G4B4.aya` Pulse Bolt sprite | `B3730B1E9D7713910E0DE4BD0CB0DCFEFCB9CEB8F6402D50681A524ADC0DCB08` |
| `Textures/pulse-bolt-blue-trail.texture.aya` | Exact released 64×64 DXT1 `Particle%Blue Trail.tga(0)R5G6B5.aya` Pulse Bolt trail | `2B4BC5CF8902D7EA8452F1068AC8F11514C8238A733CA33AAD7D6D0667688A63` |
| `Textures/mech-pulse-medium-halo.texture.aya` | Exact released 64×64 DXT1 `Particle%Halo.tga(0)R5G6B5.aya` medium-round halo | `CDE6EFC90DC7958C5BDA425A04486E277BEB85A7F1C33FB9074F369E92D58EDB` |
| `Textures/mech-pulse-medium-energy-trail.texture.aya` | Exact released 64×64 DXT1 `Particle%Energy Trail.tga(0)R5G6B5.aya` medium-round energy core | `64EDDC6B147C67886F41EF4D2BCC2A0606B453B01E4D93B9962F10CC07ABA92E` |
| `Textures/pulse-impact-animated-blob.texture.aya` | Exact released 256×256 DXT2 `alparticle4` impact/smoke animation | `74085B280199E20B765640CFC3E417E6DA0FCBFB25384E129858A32F5DEB995D` |
| `Textures/pulse-impact-shockwave.texture.aya` | Exact released 128×128 DXT1 `1telep` medium Pulse Bolt shockwave | `E92EFC3F5ADFA347E6B50F1E3D20AF4C6800D76853A2126D71237DFEFEEA9F10` |
| `Textures/effect-flash-medium.texture.aya` | Exact released 128×128 DXT1 `sun2` medium impact flash | `D7FBFCB4EDB2167FEDC0A467D4501C9BBC2F6A2852C7873DAEC3953E6F518F5C` |
| `Textures/target-tank-explosion-animated.texture.aya` | Exact released 256×256 DXT1 `alparticle6` medium explosion animation | `3C8FC30AD4923C56C3735CAAB5661A3F176EB661EAA678093870F51DE4204C9E` |
| `Textures/target-tank-explosion-fireball.texture.aya` | Exact released 256×256 DXT2 `fireball` target-destruction layer | `E6C166669E351632A90B41C74782967923C78FC8BE644A1E8948D356806B23ED` |
| `Sky/cube25-cent.texture.aya` | Released 512×512 cube-25 center DXT1 texture | `1AAD6CC8F85B6BB7CCBB8D2C7B0E6AA31722A9ADBDE5A3F19B248430CA83469E` |
| `Sky/cube25-up.texture.aya` | Released 512×512 cube-25 up DXT1 texture | `419E2424BCFD698058D72111FFA7D84FDC9022E03815DB7C0DA28403F4925F3C` |
| `Sky/cube25-right.texture.aya` | Released 512×512 cube-25 right DXT1 texture | `830C9B965C76A4023C2415B7C8924CA32590562C850CC84E92C003E173263D11` |
| `Sky/cube25-down.texture.aya` | Released 512×512 cube-25 down DXT1 texture | `4770829BA631E93FBC33DB2012754DA75A06BFCCC2FB2B36875E92032E22D19D` |
| `Sky/cube25-left.texture.aya` | Released 512×512 cube-25 left DXT1 texture | `D7CBCE30E51473DDC89ED0C44326E598DAC4D2682F64EF20C19237AFD2CEBE14` |
| `Music/tutorial-track-03.ogg` | Released `MUS_TUTORIAL` zero-based track 3, `data/Music/BEA_04(Master).ogg` | `32D3E338964D74F50D0094536C585375F1E14AA2BAE6087487803F3529EAF360` |
| `TutorialAudio/hud_01.ogg` | Released English `data/sounds/english/MessageBox/hud_01.ogg` | `BAE30243A2B5FE3DAE718181AC5B05D766F93D5E25B042FE1B04C71FC9347909` |
| `TutorialAudio/hud_02.ogg` | Released English `data/sounds/english/MessageBox/hud_02.ogg` | `43AE0C306B7935A21D415338348508EABF3A61F8799C0FD0873C89919FB84A35` |
| `TutorialAudio/hud_06.ogg` | Released English `data/sounds/english/MessageBox/hud_06.ogg` | `4ED80A12FA7D2AD07A044F95F94D52455413962B75E7689101DF6907711F3235` |
| `TutorialAudio/tutorial_message_log.ogg` | Released English message-log instruction | `7A03FF8F3FAA4BE4B729E7619055379C62921E2EAEB67FC9711DAC0DFE273F8B` |
| `TutorialAudio/tutorial_technician_01.ogg` | Released English technician status | `4792371453B4402454B922A481EB0968A099EFB13981FF1918AA6177FB6AE151` |
| `TutorialAudio/tutorial_13_mod.ogg` | Released English movement instruction | `7EEE9087F86C00ABE4FEAB115B20E4E2F27A8E6D1ADC7318B1602446A7493E65` |
| `TutorialAudio/tutorial_01.ogg` | Released English Target Zone 1 instruction | `48E40B07A77B5776F817ED8D8FFE1EFF1A978B10480CAB92019077E7B66784A8` |
| `TutorialAudio/tutorial_scanner.ogg` | Released English objective-scanner instruction | `7A9535B1187B6E1FF276CEBC3906EC2102E5D166F381EE674113B4F09C2B3BD2` |
| `TutorialAudio/tutorial_02.ogg` | Released English Firing Range assignment | `FA0533DE72B8D7702B83B709BA631BC8F7A42A5183BABCB147AE653A5D7A2904` |
| `TutorialAudio/tutorial_03.ogg` | Released English weapon-system introduction | `8E3BBD3F680099F7664F473F73837BF3E6D09474B4426677DD6BF27B31177DC2` |
| `TutorialAudio/hud_05.ogg` | Released English current-weapon indicator explanation | `66256D87557946647A51A2E8D49E044BC55AE370C4AD1C8E950B1D884EC082EB` |
| `TutorialAudio/tutorial_pulse_cannon.ogg` | Released English IS-5 Pulse Cannon introduction | `2FDA4A38B4737E03647C03BAC38BFB36E7E6FF16B279007C04616C23857C25F8` |
| `TutorialAudio/tutorial_open_fire.ogg` | Released English Firing Range target instruction | `04A1A65B45F75F4D1E85B0FAB6970125584EFBABE3609D7413E60B569A26D20C` |
| `TutorialAudio/tutorial_pulse_cannon_2.ogg` | Released English Pulse Cannon energy explanation | `F4ECA49F26F61F0369C0D8B770300596695F8A62EC12269A4C9D1CB3F61B13E0` |
| `TutorialAudio/tutorial_vulcan_cannon.ogg` | Released English Vulcan Cannon introduction | `7F483D8F3C876C8E9E8BD52B0369F1C54C39C83C174C0A43D5FB8674C069172C` |
| `TutorialAudio/tutorial_open_fire_2.ogg` | Released English three-truck instruction | `122782139A31FBD777A734E0979F4F0AB8A7308D1154D7215CE2AF13D56E3237` |
| `TutorialAudio/tutorial_vulcan_cannon_2.ogg` | Released English Vulcan ammunition warning | `6F872CA07FCC4F49FFB0CB2536A460411139FE1D77D263198C0F423FCEFA9D90` |
| `TutorialAudio/hud_03.ogg` | Released English energy-gauge explanation | `3D58AB5ABF9715EE4B3C657BF3CA7C0B91C2985382A7D72C948513045669C31E` |
| `TutorialAudio/hud_04.ogg` | Released English armour-gauge explanation | `3B96AA4CF15202D2977D32A04E73715DC1E940E00596D1614ACD47262C86E77D` |
| `TutorialAudio/hud_07.ogg` | Released English battle-line explanation | `8D75F5981ABB9FC494EB77F0A721B38B8EB95083BE9282E67561E4BF18E9A8D4` |
| `TutorialAudio/hud_08.ogg` | Released English `data/sounds/english/MessageBox/hud_08.ogg` | `06E0C641803B25FE157E8FD27420E11BE5972DF3B0DCD80681926577C9B0C361` |
| `TutorialAudio/tutorial_04.ogg` | Released English flight-mode instruction | `78C04E99FF5AE90FB224FA2DFFAE6B3101123D32FE73E3C9EE6B37EC4D6482C6` |
| `TutorialAudio/tutorial_05.ogg` | Released English moving-target instruction | `BD047BD04EEEFEECA91ED1AE3244EB65F8FE26DE33F81BA18BD9505BC4494C58` |
| `TutorialAudio/tutorial_06.ogg` | Released English remote-drone instruction | `D61F834AC1EFE27FF6982D25A401CFC48DD7BFAF03EE38F3BDFADB0D819F11C1` |
| `TutorialAudio/tutorial_07.ogg` | Released English armed-drone instruction | `1D01BB7C56BC582944161B415CFB18518ABBEB211067A0DB62F80D70C587AF7E` |
| `TutorialAudio/tutorial_08.ogg` | Released English return-for-diagnostics instruction | `A7888025D9DB2094DF63145E7D58B53BE5054ABF28C678F727155F6ED282C205` |
| `TutorialAudio/tutorial_09.ogg` | Released English repair-pad instruction | `D306048BB7D1680C4B5E3FD8B7A01F966725C1C4D7E4F9A09B9E9E25DCAE7557` |
| `TutorialAudio/tutorial_10.ogg` | Released English training-abort instruction | `89A881C253C9CBC5227E84E942B0C8C3361B5B6BD2694B61522BD97AF320F5FB` |
| `TutorialAudio/tutorial_11.ogg` | Released English successful-completion line | `C46293FF014967F62D90F870CFE8A8FC228FCC7A0B5ACB7CBE3D203341A39984` |
| `TutorialAudio/tutorial_12.ogg` | Released English Target Zone 3 instruction | `E6CBF2CB4DABCFACEC0479DEE1EEB33ED62E1D3B46BF238B638D75AA55B7A425` |
| `TutorialAudio/tutorial_aborted.ogg` | Released English aborted-completion line | `320B8A1E4619DDEECF94AFD8862E8B90C7EBABA3FFFD5B8976A3D6160497C1B5` |
| `TutorialAudio/tutorial_broke_1.ogg` | Released English Tatiana failure line | `30E2E6652508C7B9BF13BEB2F19CD0ED66CE474D677E946CEEEBD30A905D6696` |
| `TutorialAudio/tutorial_broke_2.ogg` | Released English Kramer failure line | `8E6AF2BD4038B89C72E45C8E86A5B5E32FBA12F50728B82A26223918F6D96315` |
| `TutorialAudio/tutorial_broke_3.ogg` | Released English friendly-fire warning | `57C3C737699B02D96CD2B9CB2E6B5E8D2F513C92B51E3B13B7728F9127BC8D8F` |
| `TutorialAudio/tutorial_dodge_2.ogg` | Released English incoming-missile exercise line | `D88EFF763474BCFF488EBF913B1D8B45900452F34331EF6DB334C589768D66B2` |
| `TutorialAudio/tutorial_dodge_3.ogg` | Released English missile-threat-circle line | `7796DD70479A91C48D027594BBFC1BB6C0206336006657C13C2220185BE5C0A8` |
| `TutorialAudio/tutorial_dodge_bad.ogg` | Released English failed-dodge assessment | `B551C989F66C3C30E048A73F230DBABCF19E588CD93A95B37B5A2654569BCDD5` |
| `TutorialAudio/tutorial_dodge_good.ogg` | Released English successful-dodge assessment | `329D8269262C2F4C25B95A4373AD932F53A09B26003238C9D6AA3D613E98669D` |
| `TutorialAudio/tutorial_dodge_mod.ogg` | Released English dodge-control instruction | `C74568F49114F77CC42426CF029BE35434BF8058F2D05B1D4B6ADB73B124C3A5` |
| `TutorialAudio/tutorial_help_player.ogg` | Released English repair-help line | `287998779062D08030350BFCA83E625AC55D12BB75775D4CC59B1F9E3AFB7B5C` |
| `TutorialAudio/tutorial_landing.ogg` | Released English landing instruction | `07428CE3BFC31603E472BA83AFFD1D355B0C3CABEC24D8AD87E3FE30CC646176` |
| `TutorialAudio/tutorial_strafe.ogg` | Released English flight-strafe instruction | `F6DA37701FFD0DDC9CF2780C80674305459C552FEA3D1F383B65EBC76565DB70` |
| `TutorialAudio/tutorial_throttle_mod.ogg` | Released English throttle instruction | `29D3791D61286318FDEDB4BDC88C267488F647D65996A581FB3DA91B2D2E2EF4` |
| `TutorialAudio/tutorial_technician_02.ogg` | Released English technician line 2 | `196032DDDADBE1CBFE3315635991C02E62B05CAC083A90AD4DFAAEBBAB8EB955` |
| `TutorialAudio/tutorial_technician_03.ogg` | Released English technician line 3 | `952D91A0A416A20487D790DEBCF82DDE357935946FD7E4B69678CBD350D8681C` |
| `TutorialAudio/tutorial_movement.ogg` | Released English movement callout | `79F7DDA58130D4B8E506683F7CF65C9213DFFCA074885DF06AAAA857B0C28340` |
| `TutorialAudio/tutorial_weapon.ogg` | Released English weapon callout | `E1AFE902725A81D9900A1D5BEE65D7FDF47B61AB59246DE7ECADE89F2A9E7B00` |
| `TutorialAudio/tutorial_overheat.ogg` | Released English overheat callout | `34A084751BAFA8320FA0D8B34ED17B6F8FC3F38630B0CAF6528A3287A39B8683` |
| `TutorialAudio/tutorial_ammo.ogg` | Released English ammunition callout | `1A7474FFD1AA2C88A56B60D4F27A77A3FEA348ABF24A17A9F6E3251308AF8769` |
| `TutorialAudio/tutorial_water.ogg` | Released English water callout | `99DC92041FB49BD4B06D0E875B3DED4155E2F4A8BA4AED9B40596CE0012D1151` |
| `TutorialAudio/tutorial_zoom.ogg` | Released English zoom instruction | `D0AADAC588017F5A410358494603F7E052890C93D6B52DDBC61CBE171CB6940B` |
| `SoundEffects/terminal-ammunition-depleted.wav` | Exact HUD ammunition-depleted warning | `F1BD9E787FAA1D32C149340B16AF3D485CD6AD6B46ED09C30C889FC16B5A8DA1` |
| `SoundEffects/terminal-armour-low.wav` | Exact HUD armour-low warning | `6DA6B88ABC77E7E281D338CF45EF35DD2D8AA99CCA578418F6B6F28115D60D61` |
| `SoundEffects/terminal-energy-low.wav` | Exact HUD energy-low warning | `E7BF31D24623F3A37A6D578A52AFAE975A1B6D95DC9BB07A0DD1E1ED9C913F6D` |
| `SoundEffects/terminal-hostile-environment.wav` | Exact HUD hostile-environment warning | `3F841B810AAC4A67221319A0D28F877C5BF1555130AEEC337234E3F304DDF32F` |
| `SoundEffects/terminal-incoming-missile.wav` | Exact HUD incoming-missile warning | `5BF1FB9CFAEF17FC0D62A16D3B37E07C85A5F9FA9F78D7135DC4EE75759ECDF6` |
| `SoundEffects/terminal-incoming-warhead.wav` | Exact HUD incoming-warhead warning | `711297354E61F9A94AD66172646CAEBC7683C9A67066B3FF7793996DD57E918E` |
| `SoundEffects/terminal-micro-missiles-selected.wav` | Exact HUD Micro Missiles callout | `811D18C02399FBE05DF649ADB42732DF9C6C4C3E85F4D9ACAFA1ED3751DB04C1` |
| `SoundEffects/terminal-pulse-cannon-selected.wav` | Exact HUD Pulse Cannon callout | `99A29B4BEAD7CD484547ADBC3954A6F805638E6FCDF95CF70E90B6D5183734DA` |
| `SoundEffects/terminal-vulcan-cannon-selected.wav` | Exact HUD Vulcan Cannon callout | `A742431A169BBA0A92F0241556A79D704626D56E1DC14BB43F41079AA2CE4990` |
| `SoundEffects/terminal-weapon-overheating.wav` | Exact HUD weapon-overheating warning | `F3F9E967708177F52667C872B152362284E0A8BA55B9E6A1137A5B981F44A34D` |
| `SoundEffects/drone-vulcan-fire.wav` | Exact Target Drone `Blaster 2` launch effect | `5E9227999084BD4FB06558B498C86F968C79B8DF87B06D4621336BBC994B577B` |
| `SoundEffects/explosion-small.wav` | Exact shared Pulse-hit and Target Drone `Explosion Small` effect | `28F89761970629118B989B41B5DDA3253FECB431EC479B64D056248BC3E5C1DC` |
| `SoundEffects/facility-explosion-medium.wav` | Exact Level 100 facility medium-building explosion | `F86D23CFA18025BA9D1283E0B10D5BC1F939161465A924140044D3C0A6095D3A` |
| `SoundEffects/aquila-explosion-huge.wav` | Exact Battle Engine destruction effect | `23A85AA8C5543F5BE15F7D8B2279859560F5D417E9475F015A69522DB3C8AED8` |
| `SoundEffects/transport-explosion-large.wav` | Exact U-17 transport destruction effect | `4CE37C52A010E7903A5E7D4073E0647CA790FBFE839FACBBA97AD4D7FE2DE2FD` |
| `SoundEffects/component-explosion.wav` | Exact released component-destruction effect | `C840A5EA48F975ECDB03E82646C369D164282E1AC10B03164923271DA1067DEC` |
| `SoundEffects/explosion-large-debris.wav` | Exact released large-debris explosion | `E5DAEFB4F5DB5738B0CD8CD2619868D090CA4A604642BC05D302C1AFB54980FE` |
| `SoundEffects/explosion-huge-ground-debris.wav` | Exact released huge ground/debris explosion | `5205F38B925EC77A04AAED0501387176D49F0A69B11479127168936E8EBFCDEC` |
| `SoundEffects/trainer-flyby.wav` | Exact Air Trainer Forsetti flyby loop | `838EAC239FC8B53EF89471D433978D7E4AEE0B3F96CEA5D3281F60E2CFA6D2CE` |
| `SoundEffects/transport-flyby.wav` | Exact U-17 bomber/flyby loop | `6317E8056A8B4F657AEFC1319FB8EF512927846DDE8A287498B2C2E852108A1C` |
| `SoundEffects/repair-charging.wav` | Exact repair-pad prefire/charging effect | `9AC76F06602D5432188901DE75DAAA2BB87DD12F46F7DF88D6EDA73BF31632BA` |
| `SoundEffects/repair-full.wav` | Exact repair-pad launch/heal effect | `2725B5298E6FA84C0D96DEEFDF3D1FE7FEFB854CE8512A70441D1F95C395BB1F` |
| `SoundEffects/repair-idle.wav` | Exact repair-pad idle loop | `EC3F2AF86C5281D42923C3AE00FB66222E4E358A5F986FD26C7A43C34406F7D4` |
| `SoundEffects/pulse-cannon-fire.wav` | Exact 44.1 kHz mono PCM decode of `Battle Engine\N_BE_pulse_cannon_fire` | `710FF06DB55BC694EFB8FF7D3A5AB658125E7CA0FE6B4733A805DA98B22B0277` |
| `SoundEffects/target-tank-explosion-medium.wav` | Exact 44.1 kHz mono PCM decode of `Impact\N_I_explosion_medium` | `7228AE049CB0A9877E63671A65E51829443017B2C4981DF90A9C64D2F38B6D9C` |

## Complete Level 100 audio contract

The accepted Level 100 mission/HUD message table contains 51 unique numeric
identifiers. The retained English Ogg files are exactly that set, including both
dodge outcomes, success/aborted and failure branches, friendly-fire/help lines,
`HUD_08`, technician 02/03, and the movement, weapon, overheat, ammunition, and
water callouts; unused alternate tutorial takes are not materialized. The
mission lane's typed `Level100MessageRequested` events own identity, ordering
gates, expected playback ticks, branch selection, and objective progression.
`InteractiveSession` delivers the initial batch and every fixed-step batch once,
in order, through `FrameAdvanceResult`. The audio adapter queues every numeric
event, including duplicates, with the released six-tick inter-message handoff;
none of those mission fields are duplicated in audio state, and the queue never
advances a mission continuation. `CharacterMessagePlayback` exposes only active
message identity and presentation playback position/length for HUD lip and page
synchronization.

Level 100 selects `MUS_TUTORIAL`. Stuart's alphabetically sorted playlist and
zero-based `GetSong` resolve its track index `3` to the fourth entry,
`BEA_04(Master).ogg`. Selection playback repeats the same track at completion.
It uses the separate released music-option curve, continues while sound samples
are paused, and stops at the level-exit boundary.

The shipped `sounds.sfx` version-103 descriptors provide each retained PCM's
effect volume, positive pitch-variance range, loop flag, and language flag.
Stuart's sound manager independently establishes the `0.70` ordinary-effect,
`0.45` HUD, and PC `0.42` radio-message call volumes; random pitch is
`1 + rand() % variance / 100`. `Level100Audio` applies that bounded contract
plus the PC nonlinear master-option curve and externally supplied game-sound
mix. The owner of a fade or duck supplies its current value; the adapter does
not schedule it. Exact DirectSound attenuation remains outside the
reconstruction. The three front-end effects use the startup/menu lane's
canonical ignored paths and hashes rather than a second Level 100 copy.

The released front end exposes only Back, Move, and Select effects. Select is
also the confirm sound that survives the loading transition; there is no
separate loading sample. Gameplay pause freezes all current sound-manager
samples, including any current frontend sample. Frontend/pause-menu cues created
after that pause remain live, and tutorial music continues. Level exit stops all
samples and music, then the frontend owner emits Select when its navigation
transition requires it. This preserves Stuart's `KillAllSamples` then
return/restart cue ordering without making audio own a frontend state.

The copied `default physics.dat` assignments narrow actor audio further:

- Air Trainer owns `Forsetti Fighter Flyby 02`; the U-17 transporter owns
  `Bomber Flyby 03`.
- Target Drone has no engine-sound assignment. Its Vulcan uses `Blaster 2`, its
  destruction uses `Explosion Small`, and both its and the trainer's missile
  launch modes omit a launch sound.
- Both `Forseti Missile` and the player's `Micro Missile` resolve through
  `Micro Missile Hit` to `Explosion Medium`; `MissileImpact` shares that exact
  retained PCM without duplicating an asset.
- Target Tank and Target Truck use `Tank Explosion Medium`; Level 100
  facilities use the medium-building explosion; the Battle Engine uses the
  huge explosion.
- The repair pad owns an idle loop, charging prefire effect, and full/heal
  launch effect.

The adapter exposes `PlayFrontendCue`, numeric `QueueCharacterMessage`,
ordered Aquila-flight and destruction-event consumers, `PlayTerminalCue`,
explicit trainer/transport/repair loop setters, sound/music option inputs,
`SetGameplayMix`, `SetGameplayPaused`, and level-exit stop ownership. Mission,
native flight/weapon, dynamic-actor, impact/destruction, frontend, pause, and
result states remain owned by their source lanes. The active Aquila emitter is
selected by the canonical `Player 1` Battle Engine ActorId and follows its full
three-dimensional registry pose; destruction samples use their typed event
positions. The presentation infers no cue from snapshot deltas and owns no
mission progress, waits, objectives, frontend pages, or pause actions. Retained
warning, Pulse-launch, missile, trainer, transport, repair, and debris cues stay
silent until their canonical source events are integrated.

## Heightfield consumed by the slice

The retained `HFLD` is the smallest exact terrain input used by Core and the client. It
comes from `100_res_PC.aya` → `ERES` → `ENGN` → `MAP!` and contains a
5,084-byte `CHFD` metadata block followed by 663,552 bytes of signed 16-bit
`HFDT` samples. The released loader at `0x0047F750` reads 64×64 tiles of 9×9
samples. The Godot client uses the released 65×65 eight-step lattice for coarse
selections and camera-selected 4/2/1-step tile grids at the `CHFD` scale
`0.0009155832231044769`. It uses the recovered midpoint-error score, projected
distance thresholds, released triangle diagonal, and all 16 edge-stitch index
variants. Eight-step tiles cover every rejected selection so the mesh cannot
develop holes.

The terrain mesh is translated so the authored player-one start
`(288.6875, 243.25, -10)` is the reconstruction origin. BEA's
`(X, Y, Z-down)` coordinates map to Godot `(X, -Z, -Y)`. Steam's sampler at
`0x0047EB80` converts coordinates to 24.8 fixed point and truncates signed
bilinear interpolation after each axis. Core now owns that exact sampler and a
hashed player-ground elevation; Godot consumes the snapshot instead of
independently lifting the player. At the start it produces HFLD unit `-11153`,
ground `-10.211499`, and the copied-retail Battle Engine center
`Z=-12.111499` after the released 1.9-unit center-of-gravity offset. Two later
points on the repeated forward route likewise matched units `-11161` and
`-11469`. The observed route held zero vertical velocity, zero pitch/roll, and
no steep-slope flag, so steep-slope sliding and terrain-aware body tilt remain
unimplemented rather than inferred.

## Terrain appearance and environment consumed by the slice

The materializer retains Steam's five selected `MAPT` sources from mixer set 10:
six indexed materials and palettes at each of widths `16/32/64/128/256`, all
4,096 variable-length `MMAP` material/weight records, and the 512×512 lighting
mask in the released Level 100 archive. It follows the gradient builder at
`0x0047E8E0`, the load tail at
`0x0047F932`, and blend path at `0x0047EFF0`. Before packing RGB565 it also
applies all 30 initially active `SSHD` structure-shadow owners and then processes
all 1,481 `pinesnow` placements through the exact `DMKR` shadow-stamp rules from
`data/resources/base_res_PC.aya`. The exact initial Level 0 result remains
independently verified by its RGB565 hash. The compact ignored hierarchy payload
retains the sources needed to repaint all five logical caches without duplicating
the retail archives.
The released 20-byte terrain vertices contain position plus repeated landscape
coordinates, with no normal or diffuse-color channel; the prelit macro texture
therefore owns the terrain's base illumination and the client does not invent a
separate normal-lighting pass.

The `CHFD` detail selector is `0`, which the released loader formats as
`mixers\detail00.tga`. `CDXLandscape__RenderTerrain` at `0x00545590` maps the
macro texture once across the 512-unit landscape, maps that exact RGB detail
texture once per world unit, and applies it again through the released
quarter-scale one-radian rotation plus `(0.3, 0.3)` offset. In the released
Level 100 render path, the wrapping macro and first detail stages use plain
`D3DTOP_MODULATE`; the cloud-shadow and rotated second-detail stages use
`D3DTOP_MODULATE2X`. The exact cloud-shadow texture repeats every 256 world
units. Its static
increments are `(0.001, 0.0005)` per retail renderer-time unit; an uninterrupted
copied-runtime sample measured `(0.01993, 0.00996)` texture cycles per wall-clock
second, represented as `(0.02, 0.01)` against Godot's seconds-based `TIME`. The
active Steam state uses anisotropic minification for the root cache, but each of
its five logical landscape levels is a separate one-level 512×512 RGB565 cyclic
cache—not a hardware macro mip chain. Their absolute-coordinate spans are
`512/256/128/64/32`. After the released `0.03` camera smoothing, selection uses
the root beyond 128 units, then forward-shifted rings with thresholds
`64/32/16` and shifts `60/28/12`; the innermost ring owns Level 4. The client
repaints the selected cache slots from the retained fixed-point compositor inputs
and passes each vertex's absolute landscape coordinate and logical cache owner to
the material. Exact stateful gamut clipping and bounded patch-pool reuse order
remain unclaimed.

The `CHFD` also selects cube 25 and supplies the fog color/density, sun,
anti-sun and ambient colors, and sun vector. The five exact DXT1 cube textures
use the released formatter order `cent`, `up`, `right`, `down`, `left` and the
20 released sky vertices. The sky is camera-centered and excluded from scene
fog, matching the released no-depth world backdrop rather than treating it as
distant terrain.

This establishes the authored macro material layout, repeating terrain detail,
moving cloud-shadow stage, and environment inputs, not whole-scene pixel parity.
Terrain-damage and other post-load overlay updates, and the separate visible-sun
particle, are not implemented; initial structure and pine shadow stamps are.

## Authored placement consumed by the slice

The released `data/resources/100_res_PC.aya` archive has SHA-256
`ED6350C0E214D00AB1BF6A7BD137FBA3E77D0AFE19A6DC4C0607F56AC037496A`.
Its version-50 `WRES/WRLD/BSWD` base-world stream contains 35 unit records: 33
visible static objects and two nonvisual markers. The materializer preserves
all 33 object definitions, positions, Z values, and yaws in its exact ignored
manifest. The same stream contains 753 `fernsnow` and 1,481 `pinesnow` records;
the Steam loader deliberately skips `fern*`/`bush*` groups, so the client
instantiates only the 1,481 pines. Steam does not explain those trees with one
all-distance billboard owner. The static ownership trace is:

- `CRTTree__Init` at `0x004DD7B0` retains both the selected `pinesnow0..3`
  `CMesh` and a six-view `CImposter`. `CRTTree__VFuncSlot02_BuildRenderOutputs`
  at `0x004DD960` submits the full mesh when squared horizontal camera distance
  is at or below `g_MeshQualityDistance²`, or while the tree is falling. The
  supported image initializes that option-backed global to `30.0`; boot-time
  `CCareer::Load(flag=0)` then applies `defaultoptions.bea` OptionsTail `+0x0C`.
  The installed max-quality snapshot read for this milestone stores `70.0`
  (`0x428C0000`) at file offset `0x26CA`; manifest v7 selects that released
  high-quality value. A separate capability branch can write `45.0`.
- Outside that boundary, `CRTTree__VFuncSlot03_UpdateVisibilityState` at
  `0x004DD850` queues `CDXEngine__RenderImposterBillboardSet` at `0x00543300`.
  That helper emits all six `VIEW` records for the tree, not one chosen card:
  four successive vertical faces at approximately 90-degree rotations and two
  faces tilted by `+π/2` and `+3π/2`. Each half-extent is multiplied by `0.99`.
- After the normal world and global-imposter passes, `CDXTrees__Render` at
  `0x0055AA10` draws a separate fast-tree batch. Its primary card uses one of
  `VIEW` 0..3. The unlabelled CTree virtual target at `0x004F6540` returns
  `(tree_object_address >> 4) & 3`; placement ordinal is not an input. Its
  secondary horizontal card uses `VIEW` 4 and a half-size equal to the selected
  standing frame half-width times `0.7`. That secondary batch is drawn only when
  absolute camera-height versus sampled-ground-height delta exceeds `20.0`.

Both card owners add the mesh's final global-BBOX center to the tree position.
The exact BEA `(X,Y,Z)` centers for `pinesnow0..3` are
`(-.024962962,.000355244,-.886774659)`,
`(.070154905,-.082703590,-.911682606)`,
`(.018942535,-.120034099,-.914225817)`, and
`(.047512651,.026186585,-.814044118)`. The fast primary buffer stores signed
half-width/half-height lanes that the tree shader expands around this center as
a camera-facing vertical card. Its secondary buffer writes a literal X/Y square
at the center's Z. The general imposter helper instead transforms right/up basis
vectors and constructs each face as `center ± right ± up`.

The exact 1024×256 BC2 `Imposters_100` atlas has SHA-256
`7368BA0C586221FF1B1572CEE8F84DE2BF6DB426C005A73A10BAD54A938AD882`.
Every serialized view occupies a 32×32 cell: all V ranges are `[0, 0.125]`,
each U interval below is 0.03125 wide, and the pairs are half-width ×
half-height.

| Mesh | `VIEW` U intervals 0..5 | Half-extents 0..5 |
| --- | --- | --- |
| `pinesnow0` | `[0,.03125]`, `[.03125,.0625]`, `[.0625,.09375]`, `[.09375,.125]`, `[.125,.15625]`, `[.15625,.1875]` | `.783503950×.976928771`, `.699241579×.976928771`, `.783503890×.976928651`, `.699241519×.976928651`, `.783503950×.699241459`, `.783503950×.699241459` |
| `pinesnow1` | `[.375,.40625]`, `[.40625,.4375]`, `[.4375,.46875]`, `[.46875,.5]`, `[.5,.53125]`, `[.53125,.5625]` | `.650126278×.982503712`, `.743201494×.982503653`, `.650126219×.982503593`, `.743201494×.982503653`, `.650126278×.743201435`, `.650126278×.743201435` |
| `pinesnow2` | `[.5625,.59375]`, `[.59375,.625]`, `[.625,.65625]`, `[.65625,.6875]`, `[.6875,.71875]`, `[.71875,.75]` | `.815672159×.995326340`, `.781502008×.995326340`, `.815672100×.995326221`, `.781501949×.995326221`, `.815672159×.781501889`, `.815672159×.781501889` |
| `pinesnow3` | `[.1875,.21875]`, `[.21875,.25]`, `[.25,.28125]`, `[.28125,.3125]`, `[.3125,.34375]`, `[.34375,.375]` | `.899441719×.888172686`, `.889750004×.888172686`, `.899441659×.888172567`, `.889749944×.888172567`, `.899441719×.889749885`, `.899441719×.889749885` |

The close owner uses the ordinary world-object fixed-function path: alpha test
is enabled with reference `8` and greater-or-equal comparison; stage zero uses
linear magnification, anisotropic minification, linear mip filtering, maximum
anisotropy `4`, and LOD bias `-1`. Its vertex lighting is ambient plus
directional sun and opposing anti-sun, followed by base `MODULATE2X` and the
active CHFD fog. The global six-card pass switches min/mag to point while
retaining the restored linear mip filter and alpha reference `8`. `CRTTree`
selects that helper's secondary buffer, whose lighting flag is off and whose
white factor feeds `MODULATE2X` before fog. The fast batch uses point min/mag,
disables mip filtering, and keeps reference `8`. Both atlas paths retain the
default wrap address mode. A copied Steam read found `0x008554FC = 1`, selecting
the fast batch's same unlit white-factor `MODULATE2X` branch before fog.
Independent BC2 decoding found only `0` and `255` alpha in the atlas.

The four close meshes are not cards: their exact converted topology is
`674/499`, `411/270`, `586/396`, and `598/396` vertices/triangles for
`pinesnow0..3`. They select three exact 256×256 BC2 snowy bark/needle textures.
The authored placement data also proves overlap: only 15 pine owners lie inside
the proof profile's 30-unit boundary at player start, while 616 lie inside the
selected 70-unit high-quality boundary. The nearest six form a cluster only
3.51–5.21 units from the start. One retail tree contributes either mesh or
six-face imposter work depending on range, plus the separate fast-card pass;
nearby tree owners can also overlap in the image.

The current slice preserves those owners separately. It renders the exact four
meshes at or inside the manifest's selected 70-unit cutoff and all six fixed
imposter faces outside it, then adds the camera-facing fast standing card for
every placement and the `VIEW`-4 horizontal card only above the strict 20-unit
camera/ground delta. Manifest v7 explicitly pins fast-standing-view
reconstruction phase `0`; the client maps placement ordinal plus that phase
across `VIEW` 0..3 and checks all 1,481 assignments and their
`371/370/370/370` counts. This is a deterministic reconstruction choice, not a
claim about Steam owner identity. Steam's exact tree allocation/view sequence
and the two-bit phase consumed by its address-derived selector remain the
precise unresolved runtime boundary.
The height gate adapts the retained Level 100 HFLD ground sampler for the
released `CStaticShadows` query; exact `CStaticShadows` interpolation has not
been independently equated to that adapter. Falling-tree retention,
`CDXTrees::HideTree`, other user-selected quality distances, and pixel-level
fixed-function/Godot sampler equivalence remain outside this slice.

The 33 static records select 24 mesh types: nearby facilities and turrets,
houses, city/tall buildings, an airfield, docks, hangar, radar, solar pod, and
four iceberg types. Every instance is placed through the common retail
`(X, Y, Z-down)` to Godot mapping. Existing collision remains intentionally
limited to the separately observed Control Tower and Tank Factory envelopes.

The Federation base turret in the supplied comparison is the WRES object named
`Turret 03`, not a Firing Range Target Tank. Its object ordinal is `3`, WRES
thing type is `8` (`CUnitInitThing`), definition is exactly `SAT Turret`, and
its zero-based `default physics.dat` Unit-statement index is `58`. The serialized
behavior child `5` resolves through the released factories to behavior `4` and
`CCannon::Init`. WRES authors position `(252.5, 261.25, -0.0)` with zero
yaw/pitch/roll. Its exact `m_ft_sam.msh.aya` conversion has 16 parts:
`base -> turretbase -> support -> barrel -> Emit01..08`, with `Emit09..12`
parented directly to `base`. The converted vertical bounds are
`-0.22822660952806473..0.7794696986675262`, so the mesh lower edge is
`0.22822660952806473` below its authored pivot.

Stuart's `CThing::Init` clips that authored pivot through `MAP.Collide`, then
through `MAP.GetWaterLevel` for things that cannot go underwater. The Steam
body at `0x004F34A0` follows the same order: the `CCannon` vtable's `+0xB0`
slot returns `1`, the released HFLD sampler is called at `0x0047EB80`, and its
`+0xC4` slot returns `0` before the water comparison against `0x006FBDFC`.
At this X/Y, HFLD unit `-10485` produces terrain Z
`-9.599889755249023`; water Z is `-8.84000015258789`, so the released initial
transform is position `(252.5, 261.25, -9.599889755249023)` with identity
orientation. The client therefore places every object whose definition is
exactly `SAT Turret` with its pivot on that support (Godot Y
`-0.40011024475097656`), preserving the authored lower skirt below terrain.
The other static types retain their existing converted lower-bound clearance;
their individual released grounding relationships are not generalized from
this turret.

Level 100's `HFLD` selects water level `-8.84000015258789`, color `#21213D`,
and texture index zero. The active Steam path renders a 25×25 camera-following
grid with two animated `caustic00` stages, authored `reflection00` imagery, and
the exact `sunreflect`/`sunblob` stages. Steam disables texture stage 3 before
the main grid draw; the released wave operations apply only to the authored
shoreline passes. The sun textures shape an
alpha-tested `#E8E8FF` patch scaled from camera height. The nested `SURF`
payload supplies 514 three-contour records; the client reproduces the first
shore pass and the later unfogged `SRCALPHA`/`ONE` wave pass in released order.
Controlled copied-runtime observation measured the caustic phase at `1` radian
per second and both wave scrolls at `0.06` texture cycles per second. The
optional advanced-water path remained inactive, so this implementation does
not claim dynamic scene reflection/refraction.

The PC renderer uses packed ambient plus directional sun and opposing anti-sun
from `CHFD`. Directional channels are divided by 256 and the base texture stage
uses `MODULATE2X`; the client reproduces that fixed-function equation for the
current static meshes, Aquila exterior, and range targets. It preserves
all six `TEXR` slots and implements the active released DOT3-lighting,
camera-space reflection, and alpha-overlay passes with each texture's serialized
`TEXB` parameters. Released material modes disabled by the live Level 100
renderer remain disabled.

The nearby compared facility is base-world ordinal 1, `Tank Factory`, backed by
`m_fb_tank_factory.msh.aya`. Its four material assignments are exactly
`(0,-,1,-,-,-)`, `(2,-,1,-,-,-)`, `(4,-,3,-,-,-)`, and
`(6,-,5,-,-,-)`: the ordinary base texture is in slot 0, the matching
`meshtex\Chrome3.tga` record is in reflection slot 2, and the other slots are
`0xFFFFFFFF`. Every Chrome3 `TEXB` record has strength
`0.19999998807907104`, zero offset, and unit scale. The valid texels in every
Chrome3 mip are opaque, and all 2,457 facility vertices have diffuse alpha
`255`. `CMeshRenderer__RenderMeshWithLayerPasses` (`0x0054D530`) therefore
rounds `255 * strength` to `51`; the binary initializes the secondary-pass
percentage to `100`, so `CVBufTexture__SetupSecondaryBlend` (`0x00558EF0`)
publishes `D3DRS_TEXTUREFACTOR = 0x33FFFFFF` on this path.

Mode 2 is a later draw of the same geometry, not an emissive texture mixed into
the base draw. It retains stage 0 `COLOROP=MODULATE2X` with
`TEXTURE,DIFFUSE`, stage 0 `ALPHAOP=MODULATE` with `TEXTURE,DIFFUSE`, and then
uses stage 1 `MODULATE` with `CURRENT,TFACTOR`; the white texture-factor RGB
leaves color unchanged while its byte alpha scales source alpha. The framebuffer
blend is `SRCALPHA,INVSRCALPHA`. In normalized notation, the compared facility
therefore uses `Cr=saturate(2*Tchrome.rgb*Dlit.rgb)`,
`Ar=Tchrome.a*Dlit.a*(51/255)`, and
`C=Ar*Cr+(1-Ar)*Cbase`. Texture-stage results saturate to `[0,1]`; the
application-provided factor is exactly 8-bit, while further internal combiner
fractional precision is device-owned rather than encoded by BEA. The client
accordingly quantizes the factor and saturates the operation without inventing
additional byte-rounding steps.

`CVBufTexture__RenderModePass` (`0x005588F0`) selects
`D3DTSS_TCI_CAMERASPACEREFLECTIONVECTOR`, `COUNT2`, and the released matrix
`diag(0.5,-0.5,1,1)` with translation `(0.5,0.5,0)`, producing
`(0.5*R.x+0.5,-0.5*R.y+0.5)` from the per-vertex camera-space reflection
vector. The draw inherits the world stage-0 sampler: wrapping U/V, linear
magnification and mip interpolation, anisotropic minification capped at 4, and
mip LOD bias `-1`. The D3D8 path has no sRGB texture read/write state, so its
texture arithmetic is on encoded channel values; `retail_output` performs only
the transfer required by Godot's active output contract. Released exponential
fog is applied after the texture cascade and before target blending. Applying
that same fog once after the client's source-alpha composition is algebraically
identical for these coplanar passes because both draws share depth, fog factor,
and fog color.

The Core origin is the released player-one start `(288.6875, 243.25)` in the
world's horizontal X/Y plane. The current slice consumes:

| Thing | Relative X/Y | Retail yaw or radius |
| --- | --- | --- |
| Player-one start | `(0, 0)` | yaw `0.509829998` |
| Target Zone 1 | `(-43.1875, 33.5)` | radius `5` |
| Firing Range | `(-69.6875, 72.75)` | radius `5` |
| Target Tank 1 | `(-67.76434, 78.28299)` | yaw `-0.0523363` |
| Target Tank 2 | `(-78.75, 80.0625)` | yaw `-2.1535792` |
| Target Tank 3 | `(-71.875, 84.6875)` | yaw `2.4043305` |
| Target Warehouse | `(-86.3125, 83.5625)` | yaw `-1.9708606` |

One no-input control and two fresh, uninterrupted fixed-yaw forward holds per
facility establish the two route contacts consumed by Core. Steam repeated a
`2.5736`-unit centre separation at the Control Tower while removing inward
velocity and retaining tangent motion, so the walker visibly slid around it.
At the Tank Factory, transient samples reached `8.3586..8.4267` units before
the head-on response settled repeatedly at `8.4333` with zero planar velocity.
Both observations held raw walker state `2`, stable yaw, and the expected
`0.15`-unit released update speed before contact. Core rounds the stable
envelopes to `2.574` and `8.434`; they include the released single-player
BattleEngine radius and are not general building bounds, arbitrary collision,
or destruction behavior.

Two fresh uninterrupted read-only runs repeated Steam's six-second full pan.
`CPlayer__GotoPanView` (`0x004D2C10`) transforms local camera points
`(0,10,-4.3)`, `(5,0,1.3)`, `(0,-9,-1.3)`, and `(0,-2.5,0)` by the stationary
Aquila orientation and passes them to its order-three clamped quadratic spline.
Both runs began at `(283.807220, 251.978271, -16.411499)`, handed off from the
pan camera to the first-person camera after 5.95 seconds, and entered playing
state after six seconds. The presentation consumes that path and keeps the
exterior Aquila visible while the pan camera suppresses the cockpit and HUD.
After the handoff, five uninterrupted read-only samples held the same
first-person `CThingCamera`, position, yaw, and horizontal forward column
`(-0.488029, 0.872827)`.

One idle control and two fresh repetitions at that same start bound vertical
aim without moving the Aquila. Steam stored pitch and its inertial velocity on
the player-one BattleEngine rather than on an independent camera: the first
input was exactly `1/117` radian, coast retained `0.8`, and repeated held-input
endpoints were `+0.5321228` and `-1.0911411..-1.0912496`. Two player-owned
Pulse Cannon rounds then repeated the crosshair-derived unit direction within
`0.00119` per component. These bounds apply to the authored start slope;
terrain-relative limiting, mouse inversion and sensitivity settings other than
the copied Steam `1.5` baseline, auto-aim, and
vertical target collision are not claimed.

`TargetZone1.msl` and `FiringRange.msl` each request a 0.5-second wait before
posting their event. `LevelScript.msl` activates Target Zone 1 first, then makes
the Firing Range the objective after `Reached Target Zone 1`.

## First tutorial handoff

Core tick zero is the observed retail pan start at game time `3.0`. Two fresh,
uninterrupted app-owned Level 100 runs repeated the following message boundaries
within one 50 ms retail sample; the retained intervals are half-open:

| Message | Core ticks |
| --- | --- |
| HUD introduction | `182..351` |
| Threat circle | `357..567` |
| Scanner | `573..756` |
| Message log | `762..926` |
| Technician status | `932..998` |
| Movement controls | `1004..1220` |
| Reach Target Zone 1 | `1226..1387` |
| Objective scanner | `1393..1530` |

The released Battle Engine power flag at offset `0x580` changed from `0` to `1`
at Core tick `1000`; its flight flag at `0x58C` and both initial weapon gates
remained disabled. At tick `1223`, the unique object at Target Zone 1's authored
position changed its `CThing` flags at offset `0x2C` from `0x0002` to `0x0022`,
setting the released objective bit `0x20`. The current slice consumes those
gates, exact English text, and exact voice clips.

Two later uninterrupted runs delivered the same copied `Movement/Left` then
`Forward` input to player one. Target Zone 1's objective flag remained set
until its radius-5 volume overlapped Steam's single-player Battle Engine radius
of `0.4`; the last outside/first inside samples were `5.44/5.29` and
`5.54/5.39` world units. Both runs then atomically cleared Target Zone 1,
marked the Firing Range, and installed message ID `4458134` (`TUTORIAL_02`)
after the same 11 released 20 Hz updates. Core maps that observed dispatch to
16 ticks at 30 Hz. The client uses the exact 5.393900-second English voice,
subtitle, and shipped 16x16 objective marker with the released radar transform.
One clean control and three fresh uninterrupted Firing Range runs then used a
predeclared read-only observer over Steam's objective list, HUD weapon state,
player/weapon gates, and message ID. All three accepted runs repeated the same
sequence: the range objective cleared; the player deactivated; `TUTORIAL_03`,
`HUD_05`, `TUTORIAL_PULSE_CANNON`, `TUTORIAL_OPEN_FIRE`, and
`TUTORIAL_PULSE_CANNON_2` appeared in script order; four exact target pointers
became objectives at Open Fire; and one second later the player and Pulse
Cannon alone reactivated. The copied `Fire` binding changed the live selected
weapon state, independently proving that input reached player one. Runtime
positions and vtables identified three `m_f_pulsetank_training.msh` targets and
one `m_m_warehouse.msh` target at the coordinates above.

The sequence in Core preserves the released script's explicit one- and
two-second pauses, exact Ogg lengths, and the message post-roll/handoff already
established by the opening tutorial. It does not convert variable wall-clock
memory-scan latency into simulation timing. The exact overlap-to-Firing Range
event boundary was not separately sampled, so its 0.5-second dispatch remains
the released script delay rather than a new runtime measurement.

Two fresh app-owned copies isolated the Warehouse with the exact compiled
LevelScript count byte changed from `4` to `1`. Twelve normal direct hits removed
its objective in both runs. Player power then dropped to zero; after the
one-second script pause and exact `tutorial_vulcan_cannon.ogg` duration, Steam
reactivated the player with Pulse disabled and Vulcan enabled while adding three
already-moving Target Truck objectives. Core consumes the weapon/message gate,
not the unmeasured truck paths or Vulcan behavior.

A no-fire control and fresh isolated copied-runtime runs followed each of the
three Target Tank pointers and their player-owned normal rounds. Releasing at
the first active charge bucket (`10`) created definition-speed-`35` projectiles
that moved exactly `1.75` units per released 20 Hz update. Each tank began with
life `6` and no shield; direct mesh hits repeated the exact
`6 → 4.2 → 2.4 → 0.6 → -1.2` sequence, set the destroyed flag, and removed that
target from Steam's objective set on shot four. One separate glancing mesh-part
hit removed `1.0`. The released damage call receives a mesh-part index, so the
differing multiplier is not generalized. Core represents only the demonstrated
direct-hit path: speed `1167` millimetres per 30 Hz tick, `1.8` life per hit,
the retained mesh's rounded `1.45`-unit horizontal bound, and independent
four-hit removal for the three tanks. A same-return capture of released
`CBattleEngine::GetLaunchPosition` resolved cockpit emitter `Gun` index 1 to
`-0.005619` right, `+0.080066` forward, and `+0.259300` up in the live
BattleEngine basis; Core consumes the rounded millimetre transform. The
speed-`35` record in the released physics data names `Mech Pulse Bolt Medium`.
Its five-entry particle descriptor references four unique textures:
Blue Spark 2, Blue Trail, Halo, and Energy Trail. The presentation uses those
exact archives with the descriptor's `0.25`-unit primary sprite radius,
`0.3`-unit halo radius, `0.25`-unit energy-trail radius, and `0.08`-unit trail
start width. The current ribbon spans one Core movement tick; the released
five-point trail history, emitted secondary sprite, pulsation, color ranges,
scrolling, and lifetimes are not yet reproduced.

The exact released `data/ParticleSets/MainSet.par` (SHA-256
`A51FE4419B55E1AF132E31C6B3CD8133C937745D8F4AB691EB5A0D81017DED06`)
names the retained small-impact and medium tank-explosion layers. The
presentation consumes the unambiguous bright sprite animation, scale, and
lifetime values directly. Tank smoke's mode-1 blend cannot yet be reproduced
without an opaque card and is omitted, along with descriptor color ranges,
debris, wreck geometry, and the other subordinate emitters. The three PCM files
currently presented by the Pulse exercise were
decoded from exact `data/sounds/sounds_english_pc.xap` (SHA-256
`658C15E3BAB844D65DD3C07C4AC880F16F741C0EA116F48C603449BBD4DDA8B7`)
records 35, 106, and 102 respectively. Their `PSMP` names, declared decoded
sizes, high-nibble-first IMA-ADPCM framing, and resulting WAV hashes were
validated before retention; Godot validates the PCM envelope again at load.

## Dependency-inverted contact and destruction payload

`level100-contact-owners.json` schema v3 de-duplicates the 33 WRES instance
rows into 24 reusable static definitions and separately retains the Target Tank
and Warehouse definitions. Its 349 parts preserve names, hierarchy links,
float segment-value bits, BBOX metadata, and a deterministic
millimetre-quantized projection of transformed vertices and expanded triangle
strips. BBOX is broadphase metadata only; Core reports actor hits from the
swept-sphere projected-mesh path. The pinned
medium-pulse radius is the released `0x3D8F5C29` float rounded to `70`
millimetres. This is a hash-verified deterministic Core input, not a claim of
bit-identical retail collision geometry.

Contact does not instantiate the retained WRES metadata. Simulation supplies
the canonical registry's stable actor ID, definition/mesh binding, active
state, full pose/basis, velocity, health and lifecycle. The per-actor
destruction component implements the Warehouse's extent-weighted segment
health, `5.0` core multiplier, active-intact initial-subtree sum and strict
`30%` terminal test. Steam's CRT-random child-cascade phase and debris bounce
remain unresolved, so Core emits only typed impact and terminal presentation
effects and supplies no synthetic cascade timing or trajectory.

The presentation consumes the exact facility and target texture-pass signatures
and preserves their mesh-group assignments. Higher-layer references follow the
released mode dispatch rather than being guessed as generic metallic maps. The nine retained
render meshes represent intact facilities and targets. All three Target Tanks
have the bounded damage/deactivation path above plus the retained shot, impact,
and medium-destruction sound and primary particle layers. Two fresh isolated
copied-retail runs required exactly twelve first-bucket direct hits to remove
the 28-segment Warehouse objective, then repeated the released Vulcan handoff.
That fixed-aim observation remains a bounded comparison; Core now contacts the
retained hierarchy through the deterministic projection and applies the
evidenced per-segment health and terminal rules. Godot presents Pulse impacts
and terminal destruction from ordered typed Core events, including events from
intermediate steps in a rendered frame. It does not yet hide detached segments
or present rubble/debris. Unmeasured mesh-part damage multipliers, the three
moving trucks, and Vulcan firing are not implemented. Actor/structure collision,
steep-slope response, facility animation, complete
world population, and complete Level 100 mission behavior are not established by
this slice. Objective markers use the shipped HUD asset; no synthetic target or
world-space beacon geometry is retained.
