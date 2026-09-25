# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Pause = preload("res://Client/pause_menu.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}


func _initialize() -> void:
	call_deferred("run_checks")


func check(category: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[category] = int(counts.get(category, 0)) + 1
	if actual != expected:
		failures.append({"category": category, "name": name, "actual": actual, "expected": expected})


func state(model: RefCounted) -> Dictionary:
	return {"is_open": model.is_open(), "page": model.get_page(),
		"selected_index": model.get_selected_index(), "underlying_root_selection": model.get_underlying_root_selection(),
		"entries": model.get_entries(), "root_entries": model.get_root_entries()}


func expected_state(json: Dictionary) -> Dictionary:
	# Godot JSON decodes every numeric token as float. These fixture fields are
	# C# int32 values; admit exact integer values before comparing typed state.
	var result: Dictionary = json.duplicate(true)
	for field: String in ["page", "selected_index", "underlying_root_selection"]:
		check("fixture", field, float(result[field]) == float(int(result[field])), true)
		result[field] = int(result[field])
	for field: String in ["entries", "root_entries"]:
		for entry: Dictionary in result[field]:
			check("fixture", "entry_id", float(entry.id) == float(int(entry.id)), true)
			entry.id = int(entry.id)
	return result


func run_checks() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var vectors: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var rows: Array = vectors.get("pause", [])
	check("admission", "nonempty_fixture", not rows.is_empty(), true)
	var model = Pause.new()
	for index: int in range(rows.size()):
		var row: Dictionary = rows[index]
		var expected: Dictionary = expected_state(row.state)
		var returned: Variant = null
		var before: Dictionary = state(model)
		var saved_before: Dictionary = before.duplicate(true)
		if row.operation == "move_selection" or row.operation == "hover":
			returned = model.call(row.operation, int(row.argument))
		else:
			returned = model.call(row.operation)
		check("return", str(index), returned, row.returned)
		check("state", str(index), state(model), expected)
		check("snapshot", str(index) + ":retained", before, saved_before)
		var snapshot: Dictionary = model.view_snapshot()
		check("view", str(index) + ":page", snapshot.page, int(row.state.page))
		check("view", str(index) + ":selected", snapshot.selected_index, int(row.state.selected_index))
		check("view", str(index) + ":root_selection", snapshot.underlying_root_selection, int(row.state.underlying_root_selection))
		check("view", str(index) + ":rows", snapshot.entries.size(), row.state.entries.size())
		for entry_index: int in range(snapshot.entries.size()):
			check("view", str(index) + ":entry:" + str(entry_index), snapshot.entries[entry_index],
				{"label": row.state.entries[entry_index].label, "enabled": row.state.entries[entry_index].enabled})
		# Mutating a returned view cannot alter either the model or its next view.
		snapshot.entries[0].label = "edited snapshot"
		snapshot.root_entries[0].enabled = false
		check("snapshot", str(index) + ":detached", state(model), expected)
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"failures": failures, "completed": ["pause_model"]}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify({"failure_count": failures.size(), "counts": counts, "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)
