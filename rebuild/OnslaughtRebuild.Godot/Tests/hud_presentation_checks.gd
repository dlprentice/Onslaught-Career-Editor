# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree

const Hud = preload("res://Client/hud_presentation.gd")
const Float32 = preload("res://Core/retail_float24.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var _completed: PackedStringArray = []


func _initialize() -> void:
	_run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _check_result(name: String, actual: Dictionary, expected: Dictionary) -> void:
	_check("state", name + " result admission", actual.get("ok"), expected.ok)
	if expected.ok and expected.has("value"):
		_check("state", name + " detached projection", actual.get("value"), expected.value)
	elif not expected.ok:
		_check("state_errors", name + " error class", actual.get("error_type"), expected.error_type)
		_check("state_errors", name + " no successful value", actual.has("value"), false)
		_check("state_errors", name + " diagnostic", str(actual.get("error", "")).is_empty(), false)


func _scanner_checks(rows: Array, trig_rows: Array) -> void:
	_check("trig", "nonempty direct MathF fixtures", not trig_rows.is_empty(), true)
	for row: Dictionary in trig_rows:
		var axes: Vector2 = Hud.scanner_sine_cosine(Float32.read_word(row.input_word))
		var actual: Dictionary = {"cosine_word": Float32.store_word(axes.x), "sine_word": Float32.store_word(axes.y)}
		_check("trig", row.name + " direct binary32 trig words", actual, row.expected)
	_check("scanner", "nonempty fixtures", not rows.is_empty(), true)
	for row: Dictionary in rows:
		var dx: float = Float32.read_word(row.words[0])
		var dz: float = Float32.read_word(row.words[1])
		var yaw: float = Float32.read_word(row.words[2])
		var result: Dictionary
		match row.operation:
			"contact": result = Hud.scanner_place(dx, dz, yaw)
			"objective": result = Hud.scanner_place_objective(dx, dz, yaw)
			"design": result = Hud.scanner_place_in_design_space(dx, dz, yaw)
			_: _check("scanner", "unknown operation", row.operation, "contact/objective/design"); continue
		var actual: Dictionary = {"offset_x_word": Float32.store_word(result.offset_x),
			"offset_y_word": Float32.store_word(result.offset_y), "alpha": result.alpha,
			"drawn": result.drawn, "clamped": result.clamped}
		_check("scanner", row.name + " exact binary32 words and flags", actual, row.expected)
	_completed.append("scanner")


func _schedule_checks(rows: Array) -> void:
	_check("schedule", "nonempty fixtures", not rows.is_empty(), true)
	for row: Dictionary in rows:
		var before: Array = row.deliveries.duplicate(true)
		var display: Array[int] = []
		var visible: Array[int] = []
		for delivery: Dictionary in row.deliveries:
			display.append(Hud.display_ticks(delivery))
			visible.append(Hud.visible_ticks(delivery))
		_check("schedule", row.name + " duration", display, row.display)
		_check("schedule", row.name + " visible duration", visible, row.visible)
		var active: Variant = Hud.active_at(row.deliveries, row.tick)
		_check("schedule", row.name + " first active", active, row.active)
		_check("schedule", row.name + " socket hold", Hud.message_box_holds_active_message(row.deliveries, row.tick), row.holds)
		if active != null:
			active.delivery.message_id = -999
		_check("schedule", row.name + " detached delivery", row.deliveries, before)
	_completed.append("schedule")


func _state_checks(rows: Array) -> void:
	_check("state", "nonempty scenarios", not rows.is_empty(), true)
	for row: Dictionary in rows:
		var state = Hud.new(row.authored)
		var step_index: int = 0
		for step: Dictionary in row.steps:
			var result: Dictionary
			var before: Dictionary = step.duplicate(true)
			match step.operation:
				"consume": result = state.consume(step.events)
				"project": result = state.project(step.facts, step.playback)
				_: _check("state", "unknown operation", step.operation, "consume/project"); continue
			_check_result(row.name + "/" + str(step_index), result, step.expected)
			_check("state", row.name + "/" + str(step_index) + " immutable inputs", step, before)
			step_index += 1
	_completed.append("state")


func _definition_checks(oracle: Dictionary) -> void:
	_check("definitions", "authored node records", Hud.influence_nodes(), oracle.nodes)
	_check("definitions", "authored ordered link records", Hud.influence_links(), oracle.links)
	var actual: Dictionary = {"scale_word": Hud.SCANNER_SCALE_WORD, "fade_word": Hud.SCANNER_FADE_WORD,
		"centre_x_word": Float32.store_word(Hud.SCANNER_CENTRE_X), "centre_y_word": Float32.store_word(Hud.SCANNER_CENTRE_Y),
		"damage_ticks": Hud.DAMAGE_FLASH_LIFETIME_TICKS, "clear_lead_ticks": Hud.MESSAGE_TEXT_CLEAR_LEAD_TICKS,
		"advance_ticks": Hud.MESSAGE_ADVANCE_DELAY_TICKS}
	_check("definitions", "existing constants", actual, oracle.constants)
	for row: Dictionary in oracle.socket:
		_check("definitions", "socket %s/%s" % [row.holds, row.influence], Hud.select_lower_right_socket(row.holds, row.influence), row.expected)
	for row: Dictionary in oracle.tints:
		_check("definitions", "allegiance tint " + str(row.allegiance), Hud.scanner_tint_rgb(row.allegiance), row.expected)
	var nodes: Array[Dictionary] = Hud.influence_nodes()
	nodes[0].position.x = 999
	nodes.clear()
	var links: Array[Dictionary] = Hud.influence_links()
	links[0].first_node_id = 999
	links.clear()
	_check("definitions", "detached nodes", Hud.influence_nodes(), oracle.nodes)
	_check("definitions", "detached links", Hud.influence_links(), oracle.links)
	_completed.append("definitions")


func _admission_and_detachment_checks(original: Dictionary) -> void:
	var facts: Dictionary = original.duplicate(true)
	var authored: Dictionary = {"friendly": 0}
	var state = Hud.new(authored)
	authored.friendly = 1
	facts.tick = 10
	facts.mission.tick = 10
	facts.actors = [{"actor_id": 42, "name": "Unit", "definition_identity": "friendly", "active": true,
		"is_objective": true, "lifecycle": 0, "has_trigger": false, "position": {"x": 100, "y": 200, "z": 300},
		"velocity": {"x": 1, "y": 2, "z": 3}}]
	var events: Array = [{"kind": "message", "tick": 10, "speaker_id": 919601, "message_id": 123,
		"script_waits_for_duration": true, "expected_playback_ticks": 20}, {"kind": "help", "tick": 10, "help_message_id": 1197607}]
	_check("detachment", "consume admitted", state.consume(events), {"ok": true})
	events[0].message_id = -1
	var result: Dictionary = state.project(facts)
	_check("detachment", "project admitted", result.get("ok"), true)
	if not result.get("ok", false):
		return
	var expected: Dictionary = result.value.duplicate(true)
	_check("detachment", "authored map was detached on construction", result.value.contacts[0].allegiance, 0)
	_check("detachment", "events were detached on consumption", result.value.active_message.message_id, 123)
	result.value.active_message.message_id = 777
	result.value.delivered_messages[0].message_id = 888
	result.value.delivered_help.clear()
	result.value.objectives[0].position_millimeters.x = 999
	result.value.contacts[0].position.x = 999
	result.value.battle_line.influence_permille[0] = 0
	var retained: Dictionary = state.state_snapshot()
	retained.delivered_messages[0].message_id = 999
	retained.delivered_help.clear()
	_check("detachment", "all returned state and projection copies detached", state.project(facts).value, expected)
	var stable: Dictionary = state.state_snapshot()
	for bad: Variant in [false, 1, 1.5, [], {}, {"tick": 1}]:
		var rejected: Dictionary = state.project(bad)
		_check("admission", "invalid snapshot carrier", rejected.get("error_type"), "ArgumentException")
		_check("admission", "invalid snapshot has no result", rejected.has("value"), false)
	for bad: Variant in [null, false, "10", 10.0, -2147483649, 2147483648]:
		var malformed: Dictionary = facts.duplicate(true)
		malformed.tick = bad
		var rejected: Dictionary = state.project(malformed)
		_check("admission", "exact Int32 scalar admission " + str(bad), rejected.get("error_type"), "ArgumentException")
		_check("admission", "bad scalar has no result", rejected.has("value"), false)
	for field: String in ["actors", "commanded_allegiances", "damage_flashes"]:
		var malformed: Dictionary = facts.duplicate(true)
		malformed[field] = [null]
		_check("admission", "null " + field + " element", state.project(malformed).get("error_type"), "ArgumentException")
	_check("admission", "structural failures do not mutate state", state.state_snapshot(), stable)
	for bad: Variant in [false, 1, "events", {}, [1], [{}], [{"kind": "message"}], [{"kind": "help"}]]:
		var rejected: Dictionary = state.consume(bad)
		_check("admission", "invalid event carrier", rejected.get("error_type"), "ArgumentException")
		_check("admission", "invalid event cannot imply success", rejected.has("value"), false)
	for bad: Variant in [false, 1, [], {1: 0}, {"key": 1.0}, {"key": 2147483648}]:
		var invalid_state = Hud.new(bad)
		_check("admission", "invalid allegiance map blocks consume", invalid_state.consume([]).get("error_type"), "ArgumentException")
		_check("admission", "invalid allegiance map blocks project", invalid_state.project(facts).get("error_type"), "ArgumentException")
	_check("admission", "valid call remains usable after rejected calls", state.project(facts).value, expected)
	_completed.append("admission")


func _decode_fixture(value: Variant) -> Variant:
	# The fixture JSON numbers carry exact integers through binary64. This is
	# fixture transport only; production rejects floating-point Int32 facts.
	if value is Dictionary:
		var result: Dictionary = {}
		for key: String in value:
			result[key] = _decode_fixture(value[key])
		return result
	if value is Array:
		var result: Array = []
		for item: Variant in value:
			result.append(_decode_fixture(item))
		return result
	if typeof(value) == TYPE_FLOAT and is_finite(value) and value == floor(value) and value >= -2147483648 and value <= 4294967295:
		return int(value)
	return value


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2 or not args[1].is_absolute_path() or FileAccess.file_exists(args[1]):
		push_error("HUD checks need an existing oracle and a new absolute task-owned report path.")
		quit(2)
		return
	var input: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not input is Dictionary or not input.get("hudPresentation") is Dictionary:
		push_error("Missing hudPresentation oracle object.")
		quit(2)
		return
	var oracle: Dictionary = _decode_fixture(input.hudPresentation)
	for key: String in ["scanner", "trig", "socket", "schedules", "scenarios", "nodes", "links", "tints"]:
		if not oracle.get(key) is Array:
			push_error("Missing HUD fixture list " + key)
			quit(2)
			return
	_scanner_checks(oracle.scanner, oracle.trig)
	_schedule_checks(oracle.schedules)
	_state_checks(oracle.scenarios)
	_definition_checks(oracle)
	_admission_and_detachment_checks(oracle.scenarios[0].steps[0].facts)
	# An aborted GDScript helper can return to its caller. Required completion
	# markers prevent any such runtime failure from producing a passing report.
	for section: String in ["scanner", "schedule", "state", "definitions", "admission"]:
		_check("completion", section + " returned", _completed.has(section), true)
	var report: Dictionary = {"schema": 1, "counts": counts, "failure_count": failures.size(), "failures": failures,
		"completed": ["hud_presentation"] if _completed.size() == 5 else []}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)
