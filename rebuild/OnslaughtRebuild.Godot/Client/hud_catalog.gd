# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## SHA-admitted production catalog, ported from Level100HudAssetCatalog.cs.
## The fixed whole-file identity is checked before parsing; there is deliberately
## no alternate hash or unchecked manifest entry point. Strings remain UTF-16
## units through lookup and HUD handoff, including embedded NUL/surrogate units.

const Strict = preload("res://Core/strict_json.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const RESOURCE_PATH: String = "res://Assets/Level100/MissionData/level100-hud-events.json"
const EXPECTED_SHA256: String = "af0b389df897ab8f1404edf35280f3eac10e53ad0c064457f4df97b6ff4335d1"
const EXPECTED_SCHEMA: String = "onslaught.level100-hud-events.v4"
const EXPECTED_LEVEL_SCRIPT_SHA256: String = "d51f8864564b5bde872092ec822df5af49daac16563f500719135f1a8c6c04a4"
const EXPECTED_ENGLISH_SOURCE_SHA256: String = "ee48f3bed1c3c872ccc975146318aa0b5da3df88bff6b0a60671f0d23f9ce478"
const EXPECTED_TEXT_STF_SHA256: String = "fd318d6c2304eb8ffcfa718357c1715aadad69915f39851b19f442d8263b56ae"
const EXPECTED_ENGLISH_DAT_SHA256: String = "789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a"

# ID/symbol/audio-stem order from GPL Level100AudioCatalog.CharacterMessages.
# This shared identity table is intentionally independent of audio playback;
# character_message_specs() is the detached entry point for its eventual port.
const CHARACTER_ROWS: Array = [
	[292562, "HUD_01", "hud_01"],
	[293386, "HUD_02", "hud_02"],
	[296682, "HUD_06", "hud_06"],
	[-1575499396, "TUTORIAL_MESSAGE_LOG", "tutorial_message_log"],
	[-257967449, "TUTORIAL_TECHNICIAN_01", "tutorial_technician_01"],
	[82987417, "TUTORIAL_13_MOD", "tutorial_13_mod"],
	[4422830, "TUTORIAL_01", "tutorial_01"],
	[175347826, "TUTORIAL_SCANNER", "tutorial_scanner"],
	[4458134, "TUTORIAL_02", "tutorial_02"],
	[4493438, "TUTORIAL_03", "tutorial_03"],
	[295858, "HUD_05", "hud_05"],
	[1339691000, "TUTORIAL_PULSE_CANNON", "tutorial_pulse_cannon"],
	[669198996, "TUTORIAL_OPEN_FIRE", "tutorial_open_fire"],
	[-1715818922, "TUTORIAL_PULSE_CANNON_2", "tutorial_pulse_cannon_2"],
	[-1616775312, "TUTORIAL_VULCAN_CANNON", "tutorial_vulcan_cannon"],
	[-1860407443, "TUTORIAL_OPEN_FIRE_2", "tutorial_open_fire_2"],
	[864965454, "TUTORIAL_VULCAN_CANNON_2", "tutorial_vulcan_cannon_2"],
	[294210, "HUD_03", "hud_03"],
	[295034, "HUD_04", "hud_04"],
	[297506, "HUD_07", "hud_07"],
	[298330, "HUD_08", "hud_08"],
	[4564046, "TUTORIAL_05", "tutorial_05"],
	[22775962, "TUTORIAL_ZOOM", "tutorial_zoom"],
	[667656903, "TUTORIAL_DODGE_MOD", "tutorial_dodge_mod"],
	[150647733, "TUTORIAL_DODGE_2", "tutorial_dodge_2"],
	[151778876, "TUTORIAL_DODGE_3", "tutorial_dodge_3"],
	[1326027769, "TUTORIAL_DODGE_GOOD", "tutorial_dodge_good"],
	[623538785, "TUTORIAL_DODGE_BAD", "tutorial_dodge_bad"],
	[4528742, "TUTORIAL_04", "tutorial_04"],
	[165861931, "TUTORIAL_LANDING", "tutorial_landing"],
	[4599350, "TUTORIAL_06", "tutorial_06"],
	[1062059777, "TUTORIAL_THROTTLE_MOD", "tutorial_throttle_mod"],
	[4475837, "TUTORIAL_12", "tutorial_12"],
	[4705262, "TUTORIAL_09", "tutorial_09"],
	[4634654, "TUTORIAL_07", "tutorial_07"],
	[80260569, "TUTORIAL_STRAFE", "tutorial_strafe"],
	[4669958, "TUTORIAL_08", "tutorial_08"],
	[4440532, "TUTORIAL_11", "tutorial_11"],
	[162342028, "TUTORIAL_ABORTED", "tutorial_aborted"],
	[150940633, "TUTORIAL_BROKE_1", "tutorial_broke_1"],
	[152071864, "TUTORIAL_BROKE_2", "tutorial_broke_2"],
	[153203095, "TUTORIAL_BROKE_3", "tutorial_broke_3"],
	[-1455850811, "TUTORIAL_HELP_PLAYER", "tutorial_help_player"],
	[4405227, "TUTORIAL_10", "tutorial_10"],
	[-185551049, "TUTORIAL_TECHNICIAN_02", "tutorial_technician_02"],
	[-113134649, "TUTORIAL_TECHNICIAN_03", "tutorial_technician_03"],
	[361225970, "TUTORIAL_MOVEMENT", "tutorial_movement"],
	[88347039, "TUTORIAL_WEAPON", "tutorial_weapon"],
	[346044574, "TUTORIAL_OVERHEAT", "tutorial_overheat"],
	[22391142, "TUTORIAL_AMMO", "tutorial_ammo"],
	[44677289, "TUTORIAL_WATER", "tutorial_water"],
]
# Exact released enums from Level100HudPresentation.cs; values are text IDs.
const HELP_PROMPTS: Dictionary = {"Fire": 1197607, "ZoomIn": 8268984, "ZoomOut": 17186000,
	"Transform": 31505972, "RetroThrusters": 2302408, "WeaponSelect": 488286858}
const SPEAKERS: Dictionary = {"Tatiana": 1508464, "Technician": 10565784, "Kramer": 919601}
const HIGHLIGHTS: Dictionary = {"None": null, "HUD_COMPASS": 2, "HUD_RADAR": 4,
	"HUD_ENERGY_BAR": 1, "HUD_HEALTH_BAR": 0, "HUD_CURRENT_WEAPON": 5, "HUD_BATTLE_LINE_MAP": 3}
const TERMINAL_ROWS: Array = [
	["victory", 8959659, "FETX_VICTORY"], ["defeat", 4141956, "FETX_DEFEAT"],
	["missionComplete", 1036010335, "IG_MISSION_COMPLETE"], ["retry", 830889, "GI_RETRY"],
	["back", 457178, "GI_BACK"], ["tutorialBroken", 1110345999, "LOSE_TUTORIAL_BROKE"],
	["playerDeath", 54406750, "GAME_OVER_DEATH"], ["water", 57310275, "GAME_OVER_WATER"],
]
const TERMINAL_KEYS: Array[String] = ["victory", "defeat", "mission_complete", "retry", "back",
	"tutorial_broken", "player_death", "water"]


class Catalog extends RefCounted:
	var _messages: Dictionary
	var _help: Dictionary
	var _terminal: Dictionary

	func _init(messages: Dictionary, help: Dictionary, terminal: Dictionary) -> void:
		_messages = messages.duplicate(true)
		_help = help.duplicate(true)
		_terminal = terminal.duplicate(true)

	## Success is {ok:true,found:bool,value:definition|null}; missing is not an error.
	func try_get(message_id: Variant) -> Dictionary:
		if not _is_int32(message_id):
			return _invalid_id("message_id")
		return {"ok": true, "found": _messages.has(message_id),
			"value": _messages[message_id].duplicate(true) if _messages.has(message_id) else null}

	func get_required_message(message_id: Variant) -> Dictionary:
		if not _is_int32(message_id):
			return _invalid_id("message_id")
		return {"ok": true, "value": _messages[message_id].duplicate(true)} if _messages.has(message_id) else {
			"ok": false, "error_type": "InvalidDataException",
			"error": "Mission delivered an unknown Level 100 message ID: %d" % message_id}

	func get_required_help(prompt: Variant) -> Dictionary:
		if not _is_int32(prompt):
			return _invalid_id("prompt")
		return {"ok": true, "value": _help[prompt].duplicate(true)} if _help.has(prompt) else {
			"ok": false, "error_type": "InvalidDataException",
			"error": "Core delivered an unknown Level 100 help ID: %d" % prompt}

	func get_failure_reason(reason: Variant) -> Dictionary:
		if not _is_int32(reason):
			return _invalid_id("reason")
		var names: Dictionary = {1: "tutorial_broken", 2: "player_death", 3: "water"}
		if names.has(reason):
			return {"ok": true, "value": _terminal[names[reason]].duplicate()}
		return {"ok": false, "error_type": "InvalidDataException",
			"error": "Level 100 loss has no released failure string for %s." % ("None" if reason == 0 else str(reason))}

	func message_definitions() -> Dictionary:
		return _messages.duplicate(true)

	func help_definitions() -> Dictionary:
		return _help.duplicate(true)

	func terminal_strings() -> Dictionary:
		return _terminal.duplicate(true)

	## Same production handoff schema as the temporary FirstFlightHud C# bridge.
	func verified_text_batch() -> Dictionary:
		var messages: Dictionary = {}
		var help: Dictionary = {}
		var terminal: Dictionary = {}
		for identity: int in _messages:
			messages[identity] = _messages[identity].text.duplicate()
		for identity: int in _help:
			help[identity] = _help[identity].text.duplicate()
		for key: String in ["victory", "defeat", "tutorial_broken", "player_death", "water"]:
			terminal[key] = _terminal[key].duplicate()
		return {"schema": "onslaught-hud-verified-catalog.v1", "messages": messages, "help": help, "terminal": terminal}

	static func _is_int32(value: Variant) -> bool:
		return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647

	static func _invalid_id(parameter: String) -> Dictionary:
		return {"ok": false, "error_type": "ArgumentException", "parameter": parameter,
			"error": parameter + " must be a signed Int32."}


static func character_message_specs() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for row: Array in CHARACTER_ROWS:
		result.append({"message_id": row[0], "symbol": Text.units(row[1]).value,
			"audio_stem": Text.units(row[2]).value,
			"resource_path": Text.units("res://Assets/Level100/TutorialAudio/%s.ogg" % row[2]).value})
	return result


## An alternate read location must contain the same pinned bytes. It does not
## change the identity/error contract and never prepares or repairs assets.
static func load_catalog(resource_path: String = RESOURCE_PATH) -> Dictionary:
	if not FileAccess.file_exists(resource_path):
		return load_bytes(PackedByteArray())
	return load_bytes(FileAccess.get_file_as_bytes(resource_path))


## Boot admits the manifest once, then hands the same detached text batch to
## the gameplay scene. This small entry point also serves the temporary host
## bridge; it does not expose a second catalog owner or relax file admission.
static func load_verified_text_batch() -> Dictionary:
	var loaded: Dictionary = load_catalog()
	if not loaded.ok:
		return loaded
	return {"ok": true, "value": loaded.value.verified_text_batch()}


static func load_bytes(data: PackedByteArray) -> Dictionary:
	if data.is_empty():
		return _failure("Released Level 100 HUD event manifest is missing: " + RESOURCE_PATH)
	var digest := HashingContext.new()
	if digest.start(HashingContext.HASH_SHA256) != OK or digest.update(data) != OK:
		return {"ok": false, "error_type": "IOException", "error": "Could not hash the HUD event manifest."}
	var actual_hash: String = digest.finish().hex_encode()
	if actual_hash != EXPECTED_SHA256:
		return _failure("Released Level 100 HUD event manifest has unexpected SHA-256: " + actual_hash)
	# JsonSerializer keeps the last duplicate property; the pinned file itself
	# has no duplicates. No lossy Godot JSON/String conversion enters this path.
	var decoded: Dictionary = Strict.parse_bytes(data, false)
	if not decoded.ok:
		return {"ok": false, "error_type": "JsonException", "error": decoded.error}
	var manifest: Strict.Value = decoded.value
	if manifest.kind == "null":
		return _failure("Released Level 100 HUD event manifest is invalid JSON.")
	var admitted: Dictionary = _identity(manifest)
	if not admitted.ok:
		return admitted
	var messages: Dictionary = {}
	for row: Strict.Value in manifest.member("messages").items:
		var definition: Dictionary = _definition(row, false)
		if not definition.ok:
			return definition
		var identity: int = definition.value.message_id
		if messages.has(identity):
			return _duplicate(identity)
		messages[identity] = definition.value
	var message_ids: Array = []
	for row: Array in CHARACTER_ROWS:
		message_ids.append(row[0])
	if not _same_ids(messages, message_ids):
		return _failure("Released Level 100 HUD events do not exactly cover the audio message IDs.")
	var events: Array[Strict.Value] = manifest.member("playCharEvents").items
	for index: int in range(events.size()):
		admitted = _play_event(events[index], index, messages)
		if not admitted.ok:
			return admitted
	var help: Dictionary = {}
	for row: Strict.Value in manifest.member("help").items:
		var definition: Dictionary = _definition(row, true)
		if not definition.ok:
			return definition
		var identity: int = definition.value.prompt
		if help.has(identity):
			return _duplicate(identity)
		help[identity] = definition.value
	if not _same_ids(help, HELP_PROMPTS.values()):
		return _failure("Released Level 100 HUD events do not exactly cover the Core help IDs.")
	var terminal: Dictionary = {}
	var terminal_object: Strict.Value = manifest.member("terminalStrings")
	for index: int in range(TERMINAL_ROWS.size()):
		var expected: Array = TERMINAL_ROWS[index]
		var row: Strict.Value = null if terminal_object == null else terminal_object.member(expected[0])
		var identity: Dictionary = _integer(row, "textId")
		if not identity.ok:
			return identity
		if identity.value != expected[1] or not _matches(null if row == null else row.member("symbol"), expected[2]):
			return _failure("Released terminal string %s has an unexpected identity." % expected[2])
		var text: Dictionary = _require_text(row.member("text"), "native terminal text for " + String(expected[2]))
		if not text.ok:
			return text
		terminal[TERMINAL_KEYS[index]] = text.value
	return {"ok": true, "value": Catalog.new(messages, help, terminal)}


static func _identity(manifest: Strict.Value) -> Dictionary:
	var sources: Strict.Value = manifest.member("sources")
	if manifest.kind != "object" or not _matches(manifest.member("schemaVersion"), EXPECTED_SCHEMA) \
			or not _array_size(manifest.member("messages"), 51) \
			or not _array_size(manifest.member("playCharEvents"), 45) \
			or not _array_size(manifest.member("help"), 6) or sources == null \
			or not _matches(sources.member("levelScriptSha256"), EXPECTED_LEVEL_SCRIPT_SHA256) \
			or not _matches(sources.member("englishSourceSha256"), EXPECTED_ENGLISH_SOURCE_SHA256) \
			or not _matches(sources.member("textStfSha256"), EXPECTED_TEXT_STF_SHA256) \
			or not _matches(sources.member("englishDatSha256"), EXPECTED_ENGLISH_DAT_SHA256):
		return _failure("Released Level 100 HUD event manifest has unexpected identity or counts.")
	return {"ok": true}


static func _definition(row: Strict.Value, is_help: bool) -> Dictionary:
	var identity: Dictionary = _integer(row, "textId")
	if not identity.ok:
		return identity
	var symbol: Dictionary = _require_text(row.member("symbol"), "help symbol" if is_help else "message symbol")
	if not symbol.ok:
		return symbol
	var audio: Dictionary = {"ok": true}
	if not is_help:
		audio = _require_text(row.member("audioFile"), "audio file")
		if not audio.ok:
			return audio
		var units: PackedInt32Array = audio.value
		# Path.GetFileName recognizes slash on Unix and both slash forms plus
		# volume separators on Windows. Do not normalize literal Unix backslashes.
		if units.has(47) or (OS.get_name() == "Windows" and (units.has(92) or units.has(58))) \
				or units.size() < 4 or units.slice(units.size() - 4) != PackedInt32Array([46, 111, 103, 103]):
			return _failure("Released Level 100 HUD event has an invalid audio file: " + _display(units))
	var text: Dictionary = _require_text(row.member("text"),
		("native help text for " if is_help else "native text for ") + _display(symbol.value))
	if not text.ok:
		return text
	var result: Dictionary = {"symbol": symbol.value, "text": text.value}
	result["prompt" if is_help else "message_id"] = identity.value
	if not is_help:
		result.audio_file = audio.value
	return {"ok": true, "value": result}


static func _play_event(row: Strict.Value, index: int, messages: Dictionary) -> Dictionary:
	var identity: Dictionary = _integer(row, "textId")
	var event_index: Dictionary = _integer(row, "eventIndex")
	if not identity.ok:
		return identity
	if not event_index.ok:
		return event_index
	var symbol: Dictionary = _require_text(row.member("symbol"), "PlayCharMessage symbol")
	if not symbol.ok:
		return symbol
	if event_index.value != index or not messages.has(identity.value) or messages[identity.value].symbol != symbol.value:
		return _failure("Released Level 100 PlayCharMessage events have unexpected order or identity.")
	var speaker: Strict.Value = row.member("speaker")
	if not _known_name(speaker, SPEAKERS):
		return _failure("Released Level 100 HUD event has an unknown speaker: " + _display_value(speaker))
	var highlight: Strict.Value = row.member("highlightSymbol")
	if not _known_name(highlight, HIGHLIGHTS):
		return _failure("Released Level 100 HUD event has an unknown highlight owner: " + _display_value(highlight))
	# The original deserializer admits this bool but the catalog does not use
	# it to change the simulation's event timing or completion policy.
	var waits: Strict.Value = row.member("waitsForCompletion")
	if waits != null and waits.kind != "boolean":
		return {"ok": false, "error_type": "JsonException", "error": "waitsForCompletion requires a boolean."}
	return {"ok": true}


static func _require_text(value: Strict.Value, field: String) -> Dictionary:
	if value == null or value.kind == "null" or (value.kind == "string" and Text.is_null_or_white_space(value.string_units)):
		return _failure("Released Level 100 HUD event has no %s." % field)
	if value.kind != "string":
		return {"ok": false, "error_type": "JsonException", "error": "A HUD text field requires a JSON string."}
	return {"ok": true, "value": value.string_units.duplicate()}


static func _integer(row: Strict.Value, key: String) -> Dictionary:
	var value: Strict.Value = null if row == null else row.member(key)
	if value == null:
		return {"ok": true, "value": 0}
	var admitted: Dictionary = value.as_int32()
	return admitted if admitted.ok else {"ok": false, "error_type": "JsonException", "error": admitted.error}


static func _matches(value: Strict.Value, expected: String) -> bool:
	return value != null and value.kind == "string" and Text.equals_text(value.string_units, expected)


static func _array_size(value: Strict.Value, expected: int) -> bool:
	return value != null and value.kind == "array" and value.items.size() == expected


static func _known_name(value: Strict.Value, names: Dictionary) -> bool:
	for name: String in names:
		if _matches(value, name):
			return true
	return false


static func _same_ids(values: Dictionary, expected: Array) -> bool:
	if values.size() != expected.size():
		return false
	for identity: int in expected:
		if not values.has(identity):
			return false
	return true


static func _display(value: PackedInt32Array) -> String:
	var native: Dictionary = Text.native_string(value)
	# Only diagnostics use this conversion. Definitions and published HUD text
	# always retain their raw units; no display fallback is used as an identity.
	return native.value if native.ok else "<UTF-16 units: %s>" % value


static func _display_value(value: Strict.Value) -> String:
	return "" if value == null or value.kind == "null" else _display(value.string_units)


static func _duplicate(identity: int) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException",
		"error": "An item with the same key has already been added. Key: %d" % identity}


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
