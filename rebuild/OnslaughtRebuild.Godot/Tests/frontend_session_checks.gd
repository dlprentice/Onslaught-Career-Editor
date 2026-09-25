# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Differential runner for the actual pure frontend/career owners. Fixtures
## contain public/synthetic descriptors and the tracked gold save's already-read
## projection. Only this test entrance reads/writes its explicit owned paths.

const Frontend = preload("res://Client/frontend_session.gd")
const Values = preload("res://Core/retail_career_values.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var completed: Array[String] = []


func _initialize() -> void:
	call_deferred("run_checks")


func check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func normalize(value: Variant) -> Variant:
	if typeof(value) == TYPE_FLOAT:
		check("fixture", "integer transport", is_finite(value) and value == floor(value)
			and value >= -2147483648.0 and value <= 4294967295.0, true)
		return int(value)
	if typeof(value) == TYPE_ARRAY:
		var result: Array = []
		for item: Variant in value:
			result.append(normalize(item))
		return result
	if typeof(value) == TYPE_DICTIONARY:
		var result: Dictionary = {}
		for key: String in value:
			result[key] = normalize(value[key])
		return result
	return value


func plain(value: Variant) -> Variant:
	if typeof(value) == TYPE_PACKED_INT32_ARRAY:
		return Array(value)
	if typeof(value) == TYPE_ARRAY:
		var result: Array = []
		for item: Variant in value:
			result.append(plain(item))
		return result
	if typeof(value) == TYPE_DICTIONARY:
		var result: Dictionary = {}
		for key: String in value:
			result[key] = plain(value[key])
		return result
	return value


func descriptors(value: Variant) -> Variant:
	if value == null:
		return null
	var result: Array = []
	for item: Variant in value:
		if item == null:
			result.append(null)
			continue
		var descriptor: Dictionary = item.duplicate(true)
		if descriptor.name != null:
			descriptor.name = PackedInt32Array(descriptor.name)
		result.append(descriptor)
	return result


func state(session: RefCounted) -> Dictionary:
	var value: Dictionary = session.snapshot()
	for node: Dictionary in value.career.nodes:
		node.ranking_word = Values.float32_word(node.ranking)
		node.erase("ranking")
	return plain(value)


func compare_result(group: String, name: String, actual: Dictionary, expected: Dictionary) -> void:
	check(group, name + ":ok", actual.get("ok"), expected.ok)
	if actual.get("ok", false) and expected.ok:
		check(group, name + ":value", plain(actual.get("value")), expected.get("value"))
	elif not actual.get("ok", false) and not expected.ok:
		check(group, name + ":type", actual.get("error_type"), expected.error_type)
		check(group, name + ":parameter", actual.get("parameter", ""), expected.parameter)


func execute(session: RefCounted, operation: String, first: int, second: int) -> Dictionary:
	match operation:
		"confirm": return session.confirm()
		"back": return session.back()
		"previous": return session.move_previous()
		"next": return session.move_next()
		"select_main": return session.select_main_index(first)
		"select_quit": return session.select_quit_confirm_index(first)
		"select_career": return session.select_career_index(first)
		"select_configuration": return session.select_configuration_index(first)
		"select_world": return session.select_world(first)
		"append": return session.append_game_name_character(first, second)
		"cursor": return session.move_game_name_cursor(first != 0)
		"remove": return session.remove_game_name_character()
		"consume_launch": return session.consume_level100_launch_request()
		"consume_career": return session.consume_selected_career_load_request()
		"complete_load": return session.complete_level100_load()
		"begin_intro": return session.begin_level100_intro_cutscene()
		"complete_intro": return session.complete_level100_intro_cutscene()
		"restart": return session.restart_level100()
		"leave": return session.leave_level100_for_main_menu()
		"won": return session.try_accept_won_handoff(first, second)
		"return_unconstructible": return session.return_unconstructible_launch_to_level_select()
		"node_world": return session.get_career().nodes().at(first).set_field("world_number", second)
		"node_complete": return session.get_career().nodes().at(first).set_field("complete", second)
		"node_rank":
			var bytes := PackedByteArray()
			bytes.resize(4)
			bytes.encode_s32(0, second)
			return session.get_career().nodes().at(first).set_field("ranking", bytes.decode_float(0))
		"append_null_link":
			session.get_career().append_link(null)
			return Values.success()
		_:
			check("fixture", "known operation:" + operation, false, true)
			return Values.failure("TestFixtureError", "Unknown operation.")


func check_ownership() -> void:
	var supplied: Array = [{"slot_number": null, "name": PackedInt32Array([65, 0, 66]),
		"career": {"suggested_world_number": 100, "selectable_world_numbers": [100]}}]
	var result: Dictionary = Frontend.create(supplied)
	check("ownership", "created", result.ok, true)
	if not result.ok:
		return
	var session: RefCounted = result.value
	var initial: Dictionary = state(session)
	supplied[0].name[0] = 99
	supplied[0].career.selectable_world_numbers.append(110)
	supplied.clear()
	check("ownership", "constructor input detached", state(session), initial)
	var snapshot: Dictionary = session.snapshot()
	snapshot.game_name[0] = 77
	snapshot.career.nodes[0].complete = 1
	snapshot.career.goodies[0] = 3
	snapshot.career_descriptors[0].name[0] = 88
	snapshot.career_names[0][0] = 99
	snapshot.items[0].is_available = false
	snapshot.selected_configuration.walker_primary.display_name = "changed"
	session.get_career_names().clear()
	session.get_items().clear()
	var returned: Array = session.get_career_descriptors()
	returned[0].career.selectable_world_numbers.append(110)
	returned[0].name[0] = 0
	returned.clear()
	check("ownership", "snapshot and getters detached", state(session), initial)
	session.confirm()
	session.confirm()
	session.select_career_index(0)
	session.move_game_name_cursor(true)
	session.remove_game_name_character()
	check("ownership", "editing copied UTF16 does not change descriptor", plain(session.get_career_names()), [[65, 0, 66]])
	var game_name: Variant = session.get_game_name()
	if game_name != null and not game_name.is_empty():
		game_name[0] = 90
	check("ownership", "game name getter detached", plain(session.get_game_name()), [65, 0])
	var admitted_career: RefCounted = session.get_career()
	admitted_career.nodes().at(0).set_field("num_attempts", 27)
	check("ownership", "single live campaign owner", session.snapshot().career.nodes[0].num_attempts, 27)
	completed.append("ownership")


func check_transport() -> void:
	for invalid: Variant in [1, "careers", {}, [null], [{"slot_number": 2147483648, "name": "X", "career": null}],
		[{"slot_number": null, "name": PackedInt32Array([65536]), "career": null}],
		[{"slot_number": 0, "name": "X", "career": {"suggested_world_number": 100, "selectable_world_numbers": [2147483648]}}]]:
		check("transport", "malformed descriptor fails explicitly", Frontend.create(invalid).ok, false)
	var session: RefCounted = Frontend.create().value
	session.confirm()
	session.confirm()
	var before: Dictionary = state(session)
	for pair: Array in [[-1, 0], [65536, 0], [65, 2147483648]]:
		check("transport", "char/int32 width rejects before mutation", session.append_game_name_character(pair[0], pair[1]).ok, false)
		check("transport", "invalid transport leaves state", state(session), before)
	completed.append("transport")


func run_checks() -> void:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.size() != 2:
		printerr("frontend_session_checks requires oracle JSON and an owned report path")
		quit(2)
		return
	var document: Variant = JSON.parse_string(FileAccess.get_file_as_string(arguments[0]))
	if not document is Dictionary or not document.has("frontend_session"):
		printerr("frontend_session fixtures are missing")
		quit(2)
		return
	var data: Dictionary = normalize(document.frontend_session)
	for entry: Array in [["screen", Frontend.Screen], ["signal", Frontend.FrontendSignal],
		["career_page_mode", Frontend.CareerPageMode], ["audio_cue", Frontend.AudioCue],
		["language", Frontend.Language], ["cursor_mode", Frontend.CursorMode], ["menu_kind", Frontend.MenuKind]]:
		check("constants", entry[0], entry[1].values(), data.enums[entry[0]])
	check("constants", "source has exactly five language IDs", Frontend.Language.size(), 5)
	completed.append("constants")
	check("glyphs", "all UTF16 code units", data.glyphs.size(), 65536)
	for row: Array in data.glyphs:
		check("glyphs", "accept:" + str(row[0]), Frontend.game_name_glyph_index(row[0]), row[1])
		check("glyphs", "small:" + str(row[0]), Frontend.game_name_render_glyph_index(row[0], false), row[2])
		check("glyphs", "font0:" + str(row[0]), Frontend.game_name_render_glyph_index(row[0], true), row[3])
	completed.append("glyphs")
	for row: Dictionary in data.constructors:
		var result: Dictionary = Frontend.create(descriptors(row.descriptors))
		if result.ok:
			compare_result("constructors", row.name, Values.success(state(result.value)), row.expected)
		else:
			compare_result("constructors", row.name, result, row.expected)
	completed.append("constructors")
	for scenario: Dictionary in data.scenarios:
		var created: Dictionary = Frontend.create(descriptors(scenario.descriptors))
		check("transitions", scenario.name + ":create", created.ok, true)
		if not created.ok:
			continue
		var session: RefCounted = created.value
		check("transitions", scenario.name + ":initial", state(session), scenario.initial)
		for index: int in range(scenario.steps.size()):
			var step: Dictionary = scenario.steps[index]
			var name: String = scenario.name + ":" + str(index) + ":" + step.op
			compare_result("transitions", name, execute(session, step.op, step.first, step.second), step.expected)
			check("transitions", name + ":state", state(session), step.after)
	completed.append("transitions")
	check_ownership()
	check_transport()
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "failures": failures,
		"counts": counts, "completed": completed}
	var output: FileAccess = FileAccess.open(arguments[1], FileAccess.WRITE)
	if output == null:
		printerr("Cannot open the requested owned report path")
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t") + "\n")
	output.close()
	print("frontend_session_checks: ", counts, " failures=", failures.size(), " completed=", completed)
	quit(0 if failures.is_empty() and completed.size() == 6 else 1)
