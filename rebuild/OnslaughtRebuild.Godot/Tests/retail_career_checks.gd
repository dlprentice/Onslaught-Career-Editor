# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Standard-engine differential runner. Only this test entrance owns IO; the
## campaign modules have no filesystem, nodes, clock, process or input owner.

const Career = preload("res://Core/retail_career_campaign.gd")
const Values = preload("res://Core/retail_career_values.gd")
const WorldStrings = preload("res://Core/frontend_world_strings.gd")
const Text = preload("res://Core/canonical_json_string.gd")
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


func float_from_word(word: int) -> float:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_u32(0, word)
	return bytes.decode_float(0)


func end_level(row: Dictionary) -> Dictionary:
	var result: Dictionary = row.duplicate(true)
	result.ranking = float_from_word(result.ranking_word)
	result.erase("ranking_word")
	return result


func state(career: RefCounted) -> Dictionary:
	var result: Dictionary = career.snapshot()
	for node: Dictionary in result.nodes:
		node.ranking_word = Values.float32_word(node.ranking)
		node.erase("ranking")
	return result


func compare_result(group: String, name: String, actual: Dictionary, expected: Dictionary) -> void:
	check(group, name + ":ok", actual.get("ok"), expected.ok)
	if actual.get("ok", false) and expected.ok:
		check(group, name + ":value", actual.get("value"), expected.get("value"))
	elif not actual.get("ok", false) and not expected.ok:
		check(group, name + ":type", actual.get("error_type"), expected.error_type)
		check(group, name + ":parameter", actual.get("parameter", ""), expected.parameter)


func execute(career: RefCounted, operation: String, args: Dictionary) -> Dictionary:
	match operation:
		"apply": return career.apply_update(end_level(args))
		"recalc": return career.recalc_links(args.world, args.secondary, args.bases)
		"add_node":
			var result: Dictionary = career.nodes().add(args.world, args.complete)
			return Values.success() if result.ok else result
		"set_node":
			return career.nodes().at(args.index).set_field(args.field,
				float_from_word(args.value) if args.field == "ranking" else args.value)
		"blank_node":
			career.nodes().at(args.index).blank()
		"set_base":
			var node: RefCounted = career.nodes().at(args.index)
			var result: Dictionary = node.set_base_thing_exist_to(args.offset, args.value)
			return node.does_base_thing_exist(args.offset) if result.ok else result
		"set_link": return career.get_link(args.index).set_field(args.field, args.value)
		"append_link_reference": career.append_link(career.get_link(args.index))
		"append_null_link": career.append_link(null)
		"set_slot":
			career.slots().set_slot(args.slot, args.value)
			return Values.success(career.slots().get_slot(args.slot))
		"copy_slots": return career.slots().copy_words(args.words)
		"update_kills": return career.counters().update_things_killed(args.world, args.words)
		"set_goodie": return career.goodies().set_state(args.index, args.value)
		"new_goodie": return career.goodies().set_new_if_not_done(args.index)
		"set_latch": return career.counters().set_latch(args.field, args.value)
		"read_latch":
			return Values.success(career.counters().get_and_reset_goodie_new_count() if args.field == "new_goodie_count"
				else career.counters().get_and_reset_first_goodie())
		"grade": return career.nodes().grade_byte_for_world(args.world)
		"selectable": return career.is_world_selectable(args.world)
		_:
			check("fixture", "known operation:" + operation, false, true)
			return Values.failure("TestFixtureError", "Unknown operation.")
	return Values.success()


func run_checks() -> void:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.size() != 2:
		printerr("retail_career_checks requires oracle JSON and an owned output report path")
		quit(2)
		return
	var document: Variant = JSON.parse_string(FileAccess.get_file_as_string(arguments[0]))
	if not document is Dictionary or not document.has("retail_career"):
		printerr("retail_career fixtures are missing")
		quit(2)
		return
	var data: Dictionary = normalize(document.retail_career)
	for row: Dictionary in data.grades:
		check("numeric", "ranking:" + str(row.word), Values.grade_byte_from_ranking(float_from_word(row.word)), row.expected)
	for row: Dictionary in data.grade_compare:
		check("numeric", "signed-byte:" + str(row.held) + ":" + str(row.required),
			Values.grade_is_at_least(row.held, row.required), row.expected)
	completed.append("numeric")
	for row: Dictionary in data.objectives:
		compare_result("objectives", row.name, Values.secondary_verdict(row.statuses), row.expected)
	for row: Dictionary in data.debriefings:
		compare_result("objectives", row.name, Values.debriefing(end_level(row.input), row.count, row.first), row.expected)
	var won: Dictionary = Values.for_level100_won()
	won.ranking_word = Values.float32_word(won.ranking)
	won.erase("ranking")
	check("objectives", "unchanged Won snapshot", won, data.won_snapshot)
	completed.append("objectives")
	for scenario: Dictionary in data.scenarios:
		var career: RefCounted = Career.create_cold_training_slice() if scenario.cold else Career.Campaign.new()
		for index: int in range(scenario.steps.size()):
			var step: Dictionary = scenario.steps[index]
			var name: String = scenario.name + ":" + str(index) + ":" + step.op
			compare_result("campaign", name, execute(career, step.op, step.args), step.expected)
			check("campaign", name + ":state", state(career), step.after)
	completed.append("campaign")
	check("world_strings", "released graph", Career.world_nodes(), data.graph)
	for row: Dictionary in data.graph_queries:
		check("world_strings", "later:" + str(row.current) + ":" + str(row.dies),
			Career.is_world_later(row.current, row.dies), row.expected)
	for row: Dictionary in data.strings:
		var raw: Variant = Text.units(WorldStrings.level_name(row.world)).value
		check("world_strings", "name:" + str(row.world), null if raw == null else Array(raw), row.level_name)
		var lines: Array = []
		for line: String in WorldStrings.briefing(row.world):
			lines.append(Array(Text.units(line).value))
		check("world_strings", "briefing:" + str(row.world), lines, row.briefing)
	completed.append("world_strings")
	var owner: RefCounted = Career.create_cold_training_slice()
	var before: Dictionary = owner.snapshot()
	var changed: Dictionary = owner.snapshot()
	changed.nodes[0].complete = 99
	changed.nodes[0].base_words[0] = 0
	changed.links[0].link_type = 1
	changed.counters.killed_things[0] = 77
	changed.slots[0] = -1
	changed.goodies[0] = 2
	owner.links().clear()
	owner.nodes().nodes().clear()
	owner.slots().words().clear()
	owner.goodies().states().clear()
	check("ownership", "all returned value containers detached", owner.snapshot(), before)
	var malformed: Dictionary = owner.nodes().at(0).set_field("complete", 2147483648)
	check("ownership", "explicit signed width error", malformed.ok, false)
	check("ownership", "bad signed width leaves state", owner.snapshot(), before)
	var names: Dictionary = WorldStrings.level_names()
	names[100] = "changed"
	WorldStrings.briefing(100).clear()
	check("ownership", "authored table detached", WorldStrings.level_name(100), "1.00 - Training Level")
	check("ownership", "briefing retained", WorldStrings.briefing(100).size(), 2)
	completed.append("ownership")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(),
		"failures": failures, "counts": counts, "completed": completed}
	var output: FileAccess = FileAccess.open(arguments[1], FileAccess.WRITE)
	if output == null:
		printerr("Cannot open the requested owned report path")
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t") + "\n")
	output.close()
	print("retail_career_checks: ", counts, " failures=", failures.size(), " completed=", completed)
	quit(0 if failures.is_empty() and completed.size() == 5 else 1)
