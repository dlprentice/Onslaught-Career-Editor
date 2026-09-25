# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Synthetic checks for the actual frontend localization owner. Like the
## existing Loading checks, emits one bounded console report; no asset reads,
## output writes, scene creation, input, clock, save or session owner is needed.
const Strings = preload("res://Scenes/Frontend/loading_strings.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const WorldStrings = preload("res://Core/frontend_world_strings.gd")
const KEYS: Array[String] = ["newGame", "continueGame", "loadGame", "multiplayer", "goodies", "options", "quit", "selectLevel", "level100", "loading"]
const ENUM_NAMES: Array[String] = ["NewGame", "ContinueGame", "LoadGame", "Multiplayer", "Goodies", "Options", "Quit"]
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	_check_identity_order()
	_check_partial_writes()
	_check_retries()
	_check_duplicates_and_utf16()
	_check_atomic_contracts()
	print("FRONTEND_LOCALIZATION_CHECKS: ", JSON.stringify({"schema": 1, "checks": _checks,
		"failure_count": _failures.size(), "failures": _failures, "completed": _completed}))
	quit(0 if _failures.is_empty() and _completed.size() == 5 else 1)


func _check_identity_order() -> void:
	var source: String = _source()
	for sample: Dictionary in [
		{"source": "", "type": "InvalidDataException", "message": "Released frontend localization is missing: synthetic-receipt.json"},
		{"source": "{", "type": "JsonReaderException"},
		{"source": "[]", "type": "InvalidOperationException"},
		{"source": "null", "type": "InvalidOperationException"},
		{"source": "{}", "type": "KeyNotFoundException", "message": "Missing property: schema"},
		{"source": '{"schema":7}', "type": "InvalidOperationException"},
		{"source": '{"schema":null}', "type": "InvalidDataException"},
		{"source": '{"schema":"wrong","culture":7}', "type": "InvalidDataException"},
		{"source": '{"schema":"onslaught.frontend-strings.v1"}', "type": "KeyNotFoundException", "message": "Missing property: culture"},
		{"source": '{"schema":"onslaught.frontend-strings.v1","culture":7}', "type": "InvalidOperationException"},
		{"source": '{"schema":"onslaught.frontend-strings.v1","culture":"wrong"}', "type": "InvalidDataException"},
		{"source": '{"schema":"onslaught.frontend-strings.v1","culture":"en"}', "type": "KeyNotFoundException", "message": "Missing property: sourceSha256"},
		{"source": '{"schema":"onslaught.frontend-strings.v1","culture":"en","sourceSha256":7}', "type": "InvalidOperationException"},
		{"source": '{"schema":"onslaught.frontend-strings.v1","culture":"en","sourceSha256":"wrong"}', "type": "InvalidDataException"}]:
		var table: Dictionary = {"sentinel": PackedInt32Array([71])}
		var before: Dictionary = table.duplicate(true)
		var result: Dictionary = Strings.admit_incremental(sample.source, table, "synthetic-receipt.json")
		_error(result, sample.type, "Identity/source admission stops at the original first error.")
		if sample.has("message"): _check(result.get("error") == sample.message, "Identity/source error identifies its original path/property.")
		_check(table == before, "Identity/source refusal has no table writes.")
	var missing: Dictionary = _document()
	missing.erase("strings")
	var table: Dictionary = {}
	var absent: Dictionary = Strings.admit_incremental(JSON.stringify(missing), table)
	_error(absent, "KeyNotFoundException", "The strings member is required after successful identity admission.")
	_check(absent.error == "Missing property: strings" and table.is_empty(), "Missing strings fails before the first menu write.")
	for invalid: Variant in [null, 7, true, [], "strings"]:
		var document: Dictionary = _document()
		document.strings = invalid
		var refused: Dictionary = Strings.admit_incremental(JSON.stringify(document), table)
		_error(refused, "InvalidOperationException", "GetProperty on a non-object strings value retains its original failure.")
		_check(table.is_empty(), "Wrong strings type has no partial menu writes.")
	_check(Strings.admit_incremental(source, table).ok and table.size() == 10, "The complete synthetic receipt is admitted after clean refusals.")
	_done("identity_and_error_order")


func _check_partial_writes() -> void:
	var values: Dictionary = _values()
	for index: int in range(KEYS.size()):
		var missing_values: Dictionary = values.duplicate(true)
		missing_values.erase(KEYS[index])
		var table: Dictionary = {"sentinel": PackedInt32Array([71])}
		var result: Dictionary = Strings.admit_incremental(_source(missing_values), table)
		_error(result, "KeyNotFoundException", "A missing required value fails at its source position.")
		_check(result.get("error") == "Missing property: " + KEYS[index], "Missing-value failure names the reached key.")
		_check(table == _prefix(index, {"sentinel": PackedInt32Array([71])}), "Only preceding localization writes survive a missing value.")
		for invalid: Variant in [null, ""]:
			var empty_values: Dictionary = values.duplicate(true)
			empty_values[KEYS[index]] = invalid
			var partial: Dictionary = {}
			var refused: Dictionary = Strings.admit_incremental(_source(empty_values), partial)
			_error(refused, "InvalidDataException", "Null/empty required text fails before assigning its field.")
			_check(refused.error == "Released frontend localization is missing '" + KEYS[index] + "'."
				and partial == _prefix(index), "Null/empty refusal retains precisely the preceding source writes.")
	var previous: Dictionary = {"selectLevel": Text.units("Previous select").value,
		"level100": Text.units("Previous level").value, "loading": Text.units("Previous loading").value}
	var wrong: Dictionary = _values()
	wrong.level100 = "Wrong world row"
	var mismatch: Dictionary = Strings.admit_incremental(_source(wrong), previous)
	_error(mismatch, "InvalidDataException", "The selected-world receipt mismatch still fails.")
	_check(mismatch.error == "english.json level100 row diverged from the decoded world-strings table.", "Mismatch retains its existing diagnostic.")
	_check(previous.level100 == Text.units("Wrong world row").value and previous.selectLevel == Text.units("Select").value
		and previous.loading == Text.units("Previous loading").value and previous.size() == 10,
		"level100 assignment happens before comparison, after selectLevel and before loading.")
	var overwrite: Dictionary = {"selectLevel": PackedInt32Array([1]), "level100": PackedInt32Array([2]), "loading": PackedInt32Array([3])}
	_check(Strings.admit_incremental(_source(), overwrite).ok and overwrite == _prefix(10),
		"The three standalone fields overwrite previous values instead of using menu Add semantics.")
	_done("partial_writes")


func _check_retries() -> void:
	var missing: Dictionary = _values()
	missing.erase("loadGame")
	var table: Dictionary = {}
	_error(Strings.admit_incremental(_source(missing), table), "KeyNotFoundException", "First load can fail after two successful menu writes.")
	var before: Dictionary = table.duplicate(true)
	var retry: Dictionary = Strings.admit_incremental(_source(), table)
	_error(retry, "ArgumentException", "A repaired receipt retry encounters the existing first menu key.")
	_check(retry.error == "An item with the same key has already been added. Key: NewGame" and not retry.has("parameter"),
		"Duplicate Add preserves its enum key diagnostic and null ParamName.")
	_check(table == before, "A retry neither clears nor overwrites prior partial progress.")
	for invalid: Variant in [null, "", 7]:
		var values: Dictionary = _values()
		values.newGame = invalid
		var result: Dictionary = Strings.admit_incremental(_source(values), table)
		_error(result, "InvalidOperationException" if invalid is int else "InvalidDataException", "Retry validates the newly read first value before its duplicate check.")
		_check(table == before, "Invalid replacement values cannot mutate the existing key.")
	var missing_first: Dictionary = _values()
	missing_first.erase("newGame")
	_error(Strings.admit_incremental(_source(missing_first), table), "KeyNotFoundException", "Missing first property wins over the existing key on retry.")
	_check(table == before, "Missing first property preserves the partial table.")
	for index: int in range(ENUM_NAMES.size()):
		var existing: Dictionary = {KEYS[index]: PackedInt32Array([88])}
		var duplicate: Dictionary = Strings.admit_incremental(_source(), existing)
		_error(duplicate, "ArgumentException", "Every original menu Dictionary.Add refuses an existing enum key.")
		_check(duplicate.error == "An item with the same key has already been added. Key: " + ENUM_NAMES[index]
			and not duplicate.has("parameter"), "Each duplicate reports its original enum spelling without a parameter.")
		_check(existing == _prefix(index, {KEYS[index]: PackedInt32Array([88])}), "Later duplicate refusal keeps earlier new writes and the original duplicate value.")
	_done("retry_and_add_order")


func _check_duplicates_and_utf16() -> void:
	var source: String = _source()
	var table: Dictionary = {}
	var duplicate_new: String = source.replace('"newGame":"New"', '"newGame":"Ignored","newGame":"New"')
	_check(Strings.admit_incremental(duplicate_new, table).ok and table.newGame == Text.units("New").value,
		"JsonDocument GetProperty last-member semantics differ from duplicate destination Add semantics.")
	table = {}
	var duplicate_schema: String = source.replace('"schema":', '"schema":"ignored","schema":')
	_check(Strings.admit_incremental(duplicate_schema, table).ok, "The last identity member also wins before comparison.")
	table = {}
	var trailing_schema: String = source.trim_suffix("}") + ',"schema":"wrong"}'
	_error(Strings.admit_incremental(trailing_schema, table), "InvalidDataException", "A final wrong identity member supersedes an earlier valid one.")
	_check(table.is_empty(), "The final identity refusal precedes every menu write.")
	var last_strings: String = source.trim_suffix("}") + ',"strings":{}}'
	var strings_refusal: Dictionary = Strings.admit_incremental(last_strings, table)
	_error(strings_refusal, "KeyNotFoundException", "The last strings object is the one read.")
	_check(strings_refusal.error == "Missing property: newGame" and table.is_empty(), "Earlier complete strings do not supply fields absent from the last object.")
	var raw: String = source.replace('"newGame":"New"', '"newGame":"\\ufeffA\\u0000B\\ud83d\\ude80"')
	_check(Strings.admit_incremental(raw, table).ok
		and table.newGame == PackedInt32Array([0xfeff, 65, 0, 66, 0xd83d, 0xde80]), "Incremental writes preserve BOM, embedded NUL and non-BMP UTF-16 units.")
	for escaped: String in ["\\ud800", "\\udfff"]:
		table = {}
		var malformed: String = source.replace('"newGame":"New"', '"newGame":"' + escaped + '"')
		_error(Strings.admit_incremental(malformed, table), "InvalidOperationException", "Reached unpaired-surrogate text fails at GetString decoding.")
		_check(table.is_empty(), "Undecodable text is not assigned to the first menu field.")
	table = {}
	var ignored: String = source.trim_suffix("}") + ',"unread":"\\ud800"}'
	_check(Strings.admit_incremental(ignored, table).ok, "An unread JSON string does not gain an eager Unicode decoding boundary.")
	var returned: Dictionary = Strings.admit_incremental(source, {})
	returned.value.newGame[0] = 88
	var independent: Dictionary = {}
	_check(Strings.admit_incremental(source, independent).ok and independent.newGame == Text.units("New").value,
		"Admitted arrays come from each parsed receipt, without retained static table state.")
	_done("json_duplicates_and_utf16")


func _check_atomic_contracts() -> void:
	var source: String = _source()
	var atomic: Dictionary = Strings.admit_table(source)
	_check(atomic.ok and atomic.value == _prefix(10), "The unchanged atomic table admission still exposes all ten raw values.")
	var caption: Dictionary = Strings.admit_source(source)
	_check(caption.ok and caption.value == Text.units("Loading").value, "The unchanged caption API returns its detached raw text only.")
	var menu: Dictionary = Strings.admit_menu_rows(source)
	var expected: Array[PackedInt32Array] = []
	for index: int in range(7): expected.append(Text.units(_values()[KEYS[index]]).value)
	_check(menu.ok and menu.value == expected, "The unchanged menu-row API preserves original row ordering.")
	var wrong: Dictionary = _values()
	wrong.level100 = "Wrong world row"
	for rejected: Dictionary in [Strings.admit_table(_source(wrong)), Strings.admit_source(_source(wrong)), Strings.admit_menu_rows(_source(wrong))]:
		_error(rejected, "InvalidDataException", "The atomic APIs retain their world-row refusal.")
		_check(not rejected.has("value"), "Atomic failures never expose a partial table or caption.")
	var table: Dictionary = {}
	var incremental: Dictionary = Strings.admit_incremental(source, table)
	_check(incremental.ok and incremental.value == atomic.value, "Successful incremental content matches the existing atomic admission.")
	incremental.value.erase("loading")
	_check(not table.has("loading"), "The incremental result identifies the caller's actual table, not a second owner.")
	atomic.value.newGame[0] = 88
	caption.value[0] = 88
	menu.value[0][0] = 88
	_check(Strings.admit_table(source).value.newGame == Text.units("New").value
		and Strings.admit_source(source).value == Text.units("Loading").value
		and Strings.admit_menu_rows(source).value[0] == Text.units("New").value,
		"Atomic returned table, caption and rows remain detached across later calls.")
	_done("unchanged_atomic_contracts")


func _values() -> Dictionary:
	return {"newGame": "New", "continueGame": "Continue", "loadGame": "Load", "multiplayer": "Multi",
		"goodies": "Goodies", "options": "Options", "quit": "Quit", "selectLevel": "Select",
		"level100": WorldStrings.level_name(100), "loading": "Loading"}


func _document(values: Dictionary = {}) -> Dictionary:
	return {"schema": "onslaught.frontend-strings.v1", "culture": "en", "sourceSha256": Strings.SOURCE_SHA256,
		"strings": _values() if values.is_empty() else values}


func _source(values: Dictionary = {}) -> String:
	return JSON.stringify(_document(values))


func _prefix(count: int, initial: Dictionary = {}) -> Dictionary:
	var expected: Dictionary = initial.duplicate(true)
	var values: Dictionary = _values()
	for index: int in range(count): expected[KEYS[index]] = Text.units(values[KEYS[index]]).value
	return expected


func _error(result: Dictionary, kind: String, message: String) -> void:
	_check(not result.get("ok", false) and result.get("error_type") == kind, message)


func _check(condition: bool, message: String) -> void:
	_checks += 1
	if not condition:
		_failures.append(message)
		push_error(message)


func _done(group: String) -> void:
	_completed.append(group)
	print("FRONTEND_LOCALIZATION_SECTION: ", group)
