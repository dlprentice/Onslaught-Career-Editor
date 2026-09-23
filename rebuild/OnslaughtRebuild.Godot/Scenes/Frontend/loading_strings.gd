# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## Read-only frontend string receipt, matching the existing LoadLocalization
## admission before exposing Loading's caption. Raw UTF-16 is kept intact.
const StrictJson = preload("res://Core/strict_json.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const WorldStrings = preload("res://Core/frontend_world_strings.gd")
const SOURCE_SHA256: String = "789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a"
const REQUIRED_KEYS: Array[String] = ["newGame", "continueGame", "loadGame", "multiplayer", "goodies", "options", "quit", "selectLevel", "level100", "loading"]
const MENU_ENUM_NAMES: Array[String] = ["NewGame", "ContinueGame", "LoadGame", "Multiplayer", "Goodies", "Options", "Quit"]
@export_file("*.json") var source_path: String = "res://Assets/Frontend/english.json"


func load_caption() -> Dictionary:
	return admit_source(FileAccess.get_file_as_string(source_path), source_path)


static func admit_source(source: String, path: String = "res://Assets/Frontend/english.json") -> Dictionary:
	var admitted: Dictionary = admit_table(source, path)
	return {"ok": true, "value": admitted.value.loading.duplicate()} if admitted.ok else admitted


func load_menu_rows() -> Dictionary:
	return admit_menu_rows(FileAccess.get_file_as_string(source_path), source_path)


static func admit_menu_rows(source: String, path: String = "res://Assets/Frontend/english.json") -> Dictionary:
	var admitted: Dictionary = admit_table(source, path)
	if not admitted.ok:
		return admitted
	var rows: Array[PackedInt32Array] = []
	for key: String in ["newGame", "continueGame", "loadGame", "multiplayer", "goodies", "options", "quit"]:
		rows.append(admitted.value[key].duplicate())
	return {"ok": true, "value": rows}


## Shared admission keeps LoadLocalization's original property/error order.
## Each caller receives detached raw units, including embedded NUL.
static func admit_table(source: String, path: String = "res://Assets/Frontend/english.json") -> Dictionary:
	if source.is_empty():
		return _failure("InvalidDataException", "Released frontend localization is missing: " + path)
	# JsonDocument keeps duplicate members and GetProperty takes the last one.
	var parsed: Dictionary = StrictJson.parse_bytes(source.to_utf8_buffer(), false)
	if not parsed.ok:
		return _failure("JsonReaderException", parsed.error)
	var root: StrictJson.Value = parsed.value
	for pair: Array in [["schema", "onslaught.frontend-strings.v1"], ["culture", "en"], ["sourceSha256", SOURCE_SHA256]]:
		var identity: Dictionary = _string_property(root, pair[0])
		if not identity.ok:
			return identity
		if identity.value != Text.units(pair[1]).value:
			return _failure("InvalidDataException", "Released frontend localization has unexpected identity.")
	var strings: StrictJson.Value = root.member("strings")
	if strings == null:
		return _failure("KeyNotFoundException", "Missing property: strings")
	var table: Dictionary = {}
	for key: String in REQUIRED_KEYS:
		var value: Dictionary = _string_property(strings, key)
		if not value.ok:
			return value
		if value.value == null or value.value.is_empty():
			return _failure("InvalidDataException", "Released frontend localization is missing '" + key + "'.")
		if key == "level100" and value.value != Text.units(WorldStrings.level_name(100)).value:
			return _failure("InvalidDataException", "english.json level100 row diverged from the decoded world-strings table.")
		table[key] = value.value.duplicate()
	return {"ok": true, "value": table}


## The root's original LoadLocalization mutates seven Dictionary.Add entries,
## then three separate fields. Unlike atomic admit_table above, failed startup
## keeps all preceding writes; a retry validates each new value before trying
## to add its existing menu key. The supplied table remains the caller's owner.
static func admit_incremental(source: String, table: Dictionary, path: String = "res://Assets/Frontend/english.json") -> Dictionary:
	if source.is_empty():
		return _failure("InvalidDataException", "Released frontend localization is missing: " + path)
	var parsed: Dictionary = StrictJson.parse_bytes(source.to_utf8_buffer(), false)
	if not parsed.ok:
		return _failure("JsonReaderException", parsed.error)
	var root: StrictJson.Value = parsed.value
	# The original || identity expression stops at the first failed comparison.
	for pair: Array in [["schema", "onslaught.frontend-strings.v1"], ["culture", "en"], ["sourceSha256", SOURCE_SHA256]]:
		var identity: Dictionary = _string_property(root, pair[0])
		if not identity.ok: return identity
		if identity.value != Text.units(pair[1]).value:
			return _failure("InvalidDataException", "Released frontend localization has unexpected identity.")
	var strings: StrictJson.Value = root.member("strings")
	if strings == null:
		return _failure("KeyNotFoundException", "Missing property: strings")
	for index: int in range(REQUIRED_KEYS.size()):
		var key: String = REQUIRED_KEYS[index]
		var value: Dictionary = _string_property(strings, key)
		if not value.ok: return value
		if value.value == null or value.value.is_empty():
			return _failure("InvalidDataException", "Released frontend localization is missing '" + key + "'.")
		if index < MENU_ENUM_NAMES.size() and table.has(key):
			# .NET 8 Dictionary.TryInsert/ThrowHelper.GetAddingDuplicateWithKeyArgumentException
			# uses new ArgumentException(message), with no parameter name. The key
			# is the original RetailFrontendMenuItemKind enum, not this JSON key.
			return _failure("ArgumentException", "An item with the same key has already been added. Key: " + MENU_ENUM_NAMES[index])
		table[key] = value.value.duplicate()
		# Assignment precedes this comparison in the source; even the rejected
		# level100 text remains observable, while the loading field is untouched.
		if key == "level100" and value.value != Text.units(WorldStrings.level_name(100)).value:
			return _failure("InvalidDataException", "english.json level100 row diverged from the decoded world-strings table.")
	return {"ok": true, "value": table}


static func _string_property(owner: StrictJson.Value, key: String) -> Dictionary:
	if owner.kind != "object":
		return _failure("InvalidOperationException", "JSON property owner is not an object.")
	var value: StrictJson.Value = owner.member(key)
	if value == null:
		return _failure("KeyNotFoundException", "Missing property: " + key)
	if value.kind == "null":
		return {"ok": true, "value": null}
	var decoded: Dictionary = value.utf8_bytes()
	if not decoded.ok:
		return _failure("InvalidOperationException", decoded.error)
	return {"ok": true, "value": value.string_units.duplicate()}


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}
