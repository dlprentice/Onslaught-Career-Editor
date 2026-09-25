# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Exact port of the already tracked Core/RetailFrontendWorldStrings.cs data.
## Existing provenance: materializer Assets/Frontend/english-worlds.json
## (ffe3d3f8…5408), decoded from english.dat (789ecff6…371a). This conversion
## reads only that admitted source; it neither opens retail inputs nor borrows
## text for empty/unknown worlds. English only, as the existing owner.

const _LEVEL_NAMES: Dictionary = {
	100: "1.00 - Training Level",
	110: "1.10 - Blackout",
	200: "2.00 - Interception",
	211: "2.11 - Assault On Apollo",
	212: "2.12 - Assault On Apollo (Evo)",
	221: "2.21 - Escort Duty",
	222: "2.22 - Escort Duty (Evo)",
	231: "2.31 - Counterstrike",
	232: "2.32 - Counterstrike (Evo)",
	300: "3.00 - Liberation of Russo",
	311: "3.11 - Muspell Counterattack",
	312: "3.12 - Muspell Counterattack (Evo)",
	321: "3.21 - The Wake Of The Venturer",
	322: "3.22 - The Wake Of The Venturer (Evo)",
	331: "3.31 - Thunderhead!",
	332: "3.32 - Thunderhead! (Evo)",
	400: "4.00 - Beach Head",
	411: "4.11 - Weathering The Storm",
	412: "4.12 - Weathering The Storm (Evo)",
	421: "4.21 - Naval Ambush",
	422: "4.22 - Naval Ambush (Evo)",
	431: "4.31 - Battle For Yenya",
	432: "4.32 - Battle For Yenya (Evo)",
	500: "5.00 - Split second",
	511: "5.11 - Death From Above",
	512: "5.12 - Silent Running",
	521: "5.21 - Versus The Hive",
	522: "5.22 - Versus The Hive (Evo)",
	523: "5.23 - Enter The Gill-M",
	524: "5.24 - Enter The Gill-M (Evo)",
	600: "6.00 - Back to Castellian",
	611: "6.11 - Castellian Assault",
	612: "6.12 - Castellian Assault (Evo)",
	621: "6.21 - Air Raid",
	622: "6.22 - Air Raid (Evo)",
	700: "7.00 - Crushing Blow",
	710: "7.10 - Blinding The Enemy",
	720: "7.20 - Rescue Attempt",
	731: "7.31 - Assault Force Fenrir",
	732: "7.32 - Assault Force Fenrir (Evo)",
	741: "7.41 - The Fall Of The Fenrir",
	742: "7.42 - The Fall Of The Fenrir (Evo)",
	800: "8.00 - The Sentinel Awakes",
}

const _BRIEFINGS: Dictionary = {
	100: [
		"Tatiana will take you through the basics of piloting Battle Engine Aquila. This will cover everything from basic movement in both Walker and Jet modes as well as Weapons use.",
		"Listen to her advice and try to keep Colonel Kramer happy.",
	],
	110: [
		"Communications with the mainland have been lost. Numerous enemy contacts are heading towards the facilities on RI-04.",
		"Defend the base and prevent the invasion force from taking over the island. Ensure that the Battle Engine is protected at all times.",
	],
	200: [
		"The transports taking the Battle Engine to a firebase on Apollo have run into an enemy fighter ambush. Meanwhile, an invasion force has set down on Apollo itself.",
		"Protect the transport convoy then help the firebase defences deal with the enemy threat.",
	],
	211: [
		"Muspell forces have launched a major offensive in an effort to take the Apollo firebase.",
		"Protect the four main base buildings and try to hold out until air support can arrive. Help the air support with any remaining invaders.",
	],
	212: [
		"Muspell forces have launched a major offensive in an effort to take the Apollo firebase.",
		"Protect the four main base buildings and try to hold out until air support can arrive. Help the air support with any remaining invaders.",
	],
	221: [
		"A convoy of civilian transport ships is being escorted by the support frigate Marshall away from the island of Apollo.",
		"Ensure that the convoy successfully reaches its destination.",
	],
	222: [
		"A convoy of civilian transport ships is being escorted by the support frigate Marshall away from the island of Apollo.",
		"Ensure that the convoy successfully reaches its destination.",
	],
	231: [
		"The aircarrier Venturer has been deployed in a final attempt to clear the island of Apollo of all Muspell forces.",
		"Assist the Venturer in destroying all enemy forces.",
	],
	232: [
		"The Aircarrier Venturer has been deployed in a final attempt to clear the island of Apollo of all Muspell forces.",
		"Assist the Venturer in destroying all enemy forces.",
	],
	300: [
		"Muspell forces have all but taken the island of Russo. An enemy outpost has been established as a precursor to an assault that will destroy the final Forseti base.",
		"Destroy the Muspell outpost to delay the offensive. Ensure that the base survives.",
	],
	311: [
		"After the destruction of the outpost, a Muspell counter offensive has been launched. Perimeter patrols have already engaged the enemy.",
		"Help the Forseti forces defend the base structures and keep the enemy units at bay until reinforcements arrive. You must hold at all costs!",
	],
	312: [
		"After the destruction of the outpost, a Muspell counter-offensive has been launched. Perimeter patrols have already engaged the enemy.",
		"Help the Forseti forces defend the base structures and keep the enemy units at bay until reinforcements arrive. You must hold at all costs!",
	],
	321: [
		"The final push for the liberation of Russo has begun. The Venturer has arrived to assist the ground forces as they push towards the enemy stronghold.",
		"This is a straight fight. Help the Forseti units reclaim the island. Drive the Muspell scum back into the sea!",
	],
	322: [
		"The final push for the liberation of Russo has begun. The Venturer has arrived to assist the ground forces as they push towards the enemy stronghold.",
		"This is a straight fight. Help the Forseti units reclaim the island. Drive the Muspell scum back into the sea!",
	],
	331: [
		"The aircarrier Venturer is en route to the task force just off the shore of Yenya. Strange radar readings have been detected on a nearby island and the Venturer is about to take a closer look.",
		"Accompany the Venturer.",
	],
	332: [
		"The aircarrier Venturer is en route to the task force just off the shore of Yenya. Strange radar readings have been detected on a nearby island and the Venturer is about to take a closer look.",
		"Accompany the Venturer.",
	],
	400: [
		"Forseti forces are attempting to establish a beach head on Yenya. Three Turtle landing craft are on their way to the designated landing zone.",
		"Clear the landing zones of obstacles then aid the Forseti forces as they try to clear the local defences.",
	],
	411: [
		"With the beachhead established, the Forseti units are attempting to hold their position until reinforcements can arrive for the main push.",
		"Help defend the landing zones. They must be clear of enemy forces for the reinforcements to be able to land.",
	],
	412: [
		"With the beachhead established, the Forseti units are attempting to hold their position until reinforcements can arrive for the main push.",
		"Help defend the landing zones. They must be clear of enemy forces for the reinforcements to be able to land.",
	],
	421: [
		"A naval re-supply route has come under threat from Muspell warships. The Marshall is en route but the Air Force and Wild Cards have been deployed in the mean time.",
		"Protect the supply transports. This supply lane must not be closed!",
	],
	422: [
		"A naval re-supply route has come under threat from Muspell warships. The Marshall is en route but the Air Force and Wild Cards have been deployed in the meantime.",
		"Protect the supply transports. This supply lane must not be closed!",
	],
	431: [
		"Thanks to your actions keeping the supply lanes open, Forseti units are arriving in droves on Yenya. The remaining Muspell forces have already been engaged.",
		"Assist the Forseti forces with the liberation attempt.",
	],
	432: [
		"Thanks to your actions keeping the supply lanes open, Forseti units are arriving in droves on Yenya. The remaining Muspell forces have already been engaged.",
		"Assist the Forseti forces with the liberation attempt.",
	],
	500: [
		"A large Muspell naval facility has been located. Intelligence reports that they are preparing to launch a large attack submarine. We are also getting reports about other strange structures on the island.",
		"If the submarine makes it to open ocean, it could strike anywhere at anytime. Destroy the naval base before this can happen.",
	],
	511: [
		"The satellite strike has devastated much of the island. Taking advantage of the situation, a small Muspell assault force has launched another offensive.",
		"Make contact with the survivors and re-group before launching a counter-offensive and destroy the enemy base.",
	],
	512: [
		"The attack submarine continues to pound the city of Tyr on Forseti Minor. Civilian casualties are rising dramatically. Billy has managed to get you and the Battle Engine to Forseti Minor.",
		"Take out the Submarine before it causes any more damage! You'll have to deal with Kramer later...",
	],
	521: [
		"The signals controlling the strike satellite have been traced to the island of Nautilus. A Forseti task force has been dispatched to clear the island.",
		"Assist with the assault. That control station must be destroyed before the satellite is ready to fire again!",
	],
	522: [
		"The signals controlling the strike satellite have been traced to the island of Nautilus. A Forseti task force has been dispatched to clear the island.",
		"Assist with the assault. That control station must be destroyed before the satellite is ready to fire again!",
	],
	523: [
		"The damaged attack submarine has made it to a Muspell base on the island of Nautilus. A Forseti task force has been dispatched to clear the island.",
		"Now's your chance to destroy the Submarine once and for all. Help the assault force deal with the rest of the island.",
	],
	524: [
		"The damaged attack submarine has made it to a Muspell base on the island of Nautilus. A Forseti task force has been dispatched to clear the island.",
		"Now's your chance to destroy the submarine once and for all. Help the assault force deal with the rest of the island.",
	],
	600: [
		"Tara, on advanced patrol ahead of the Marshall, has run into trouble. Communication has been lost with her fighter.",
		"Locate Tara and provide support if required.",
	],
	611: [
		"In preparation for a major air offensive, the air defences surrounding the enemy base must be destroyed. The Wild Cards have been selected for this task.",
		"Destroy at least 75% of the enemy air defences.",
		"Note that Tara's location is still unknown. We believe she could be being held in any of the enemy structures. These structures should remain unharmed, just to be sure.",
	],
	612: [
		"In preparation for a major air offensive, the air defences surrounding the enemy base must be destroyed. The Wild Cards have been selected for this task.",
		"Destroy at least 75% of the enemy air defences.",
		"Note that Tara's location is still unknown. We believe she could be being held in any of the enemy structures. These structures should remain unharmed, just to be sure.",
	],
	621: [
		"With no air defences, the enemy base is vulnerable. A major bomber force is en route to destroy the base.",
		"Protect the bombers from enemy fighter defences and help the clean up crews with any remaining ground units.",
		"Our sources indicate that Tara has been moved to a different island. Rest assured; we WILL get her back.",
	],
	622: [
		"With no air defences, the enemy base is vulnerable. A major bomber force is en route to destroy the base.",
		"Protect the bombers from enemy fighter defences and help the clean-up crews with any remaining ground units.",
		"Our sources indicate that Tara has been moved to a different island. Rest assured; we WILL get her back.",
	],
	700: [
		"Muspell forces have been massing on the neutral island of Kensor. This has given them a great staging area for raids into Forseti territory.",
		"Eliminate all enemy forces from this island.",
	],
	710: [
		"Information gathered from the staging area on Kensor has revealed the location of the Muspell Interrogation Centre to be on Iron Isle. Iron Isle is aptly named and it's very well defended.",
		"Destroy the radar emplacements and the radar control centre.",
	],
	720: [
		"Thanks to your efforts in the previous mission, the forces on Kensor were unable to detect our landing force's approach until it was too late.",
		"Destroy all enemy forces but ensure that the Interrogation Centre is unharmed. Remember: Those are our boys in there.",
	],
	731: [
		"Advanced scouts report that the enemy aircarrier, Fenrir, has assembled a large force and is heading this way.",
		"Defend the island and newly established base from the attack. Force the Fenrir to withdraw.",
	],
	732: [
		"Advanced scouts report that the enemy aircarrier, Fenrir, has assembled a large force and is heading this way.",
		"Defend the island and newly established base from the attack. Force the Fenrir to withdraw.",
	],
	741: [
		"It looks like this might be it. The Fenrir has turned tail and is retreating. This is our chance to put an end to this war once and for all.",
		"Destroy the Fenrir and avenge Tara's death!",
	],
	742: [
		"It looks like this might be it. The Fenrir has turned tail and is retreating. This is our chance to put an end to this war once and for all.",
		"Destroy the Fenrir.",
	],
	800: [
		"Surt's escape pod is heading towards a remote island.",
		"Track down and kill General Surt.",
	],
}


static func level_name(world_number: int) -> Variant:
	return _LEVEL_NAMES.get(world_number)


static func briefing(world_number: int) -> Array[String]:
	var result: Array[String] = []
	result.assign(_BRIEFINGS.get(world_number, []))
	return result


static func level_names() -> Dictionary:
	return _LEVEL_NAMES.duplicate()


static func briefings() -> Dictionary:
	return _BRIEFINGS.duplicate(true)
