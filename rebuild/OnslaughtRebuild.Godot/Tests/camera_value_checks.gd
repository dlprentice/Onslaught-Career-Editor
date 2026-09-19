# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Camera = preload("res://Core/camera_laws.gd")
const Viewpoint = preload("res://Core/engine_viewpoint.gd")
var counts: Dictionary = {}
var failures: Array[Dictionary] = []
var completed: Array[String] = []


func _initialize() -> void:
	_run.call_deferred()


func _check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func _shape(result: Dictionary) -> Dictionary:
	return {"ok": true, "value": result.get("value")} if result.get("ok") == true \
		else {"ok": false, "error_type": result.get("error_type")}


func _decode(value: Variant) -> Variant:
	if typeof(value) == TYPE_FLOAT:
		if value != floor(value) or value < -2147483648 or value > 4294967295:
			_check("transport", "exact word", false, true)
		return int(value)
	if value is Array:
		var decoded: Array = []
		for item: Variant in value:
			decoded.append(_decode(item))
		return decoded
	if value is Dictionary:
		var decoded: Dictionary = {}
		for key: String in value:
			decoded[key] = _decode(value[key])
			if key == "camera_identity" and decoded[key] != null:
				decoded[key] = PackedInt32Array(decoded[key])
		return decoded
	return value


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if not parsed is Dictionary or not parsed.get("cameraValues") is Dictionary:
		push_error("Missing camera-value oracle.")
		quit(2)
		return
	var data: Dictionary = _decode(parsed.cameraValues)
	for row: Dictionary in data.aspect:
		_check("aspect", str(row.multiplayer), Camera.aspect_ratio(row.multiplayer), {"ok": true, "bits": row.bits})
	for wrong: Variant in [0, 1, null, "false"]:
		_check("admission", "Boolean aspect", Camera.aspect_ratio(wrong).ok, false)
	completed.append("aspect")
	var zoom := Camera.MovieZoom.new()
	_check("movie", "constructor", zoom.snapshot(), {"time_bits": 0xc0000000, "zoom_bits": 0x3f800000, "old_zoom_bits": 0x3f800000})
	for index: int in range(data.movie.size()):
		var row: Dictionary = data.movie[index]
		_check("movie", str(index) + " result", zoom.get_zoom(row.time_bits, row.fov_bits), {"ok": true, "bits": row.result})
		_check("movie", str(index) + " state", zoom.snapshot(), row.state)
	var before: Dictionary = zoom.snapshot()
	for wrong: Variant in [null, false, 1.0, -1, 4294967296, "1"]:
		_check("admission", "bad movie time", zoom.get_zoom(wrong, null).ok, false)
		if wrong != null:
			_check("admission", "bad movie FOV", zoom.get_zoom(0, wrong).ok, false)
		_check("ownership", "bad movie input unchanged", zoom.snapshot(), before)
	completed.append("movie")
	for case_index: int in range(data.viewpoints.size()):
		var case: Dictionary = data.viewpoints[case_index]
		var state: Viewpoint.State = Viewpoint.create(case.near_plane_bits, case.far_plane_bits).value
		_check("viewpoint", str(case_index) + " initial", state.snapshot(), case.initial)
		_check("hash", str(case_index) + " initial", state.compute_hash(), {"ok": true, "hex": case.initial_hash})
		for step: int in range(case.operations.size()):
			var row: Dictionary = case.operations[step]
			var result: Dictionary
			match row.name:
				"get": result = state.get_slot(row.index)
				"update": result = state.update_slot(row.index, row.value)
				"select": result = state.select_slot(row.index)
				"reset":
					state.reset()
					result = {"ok": true}
				_:
					_check("operation", "known", row.name, "supported operation")
					continue
			var name: String = "%d:%d:%s" % [case_index, step, row.name]
			_check("viewpoint", name + " result", _shape(result), row.result)
			_check("viewpoint", name + " state", state.snapshot(), row.state)
			_check("hash", name, state.compute_hash(), {"ok": true, "hex": row.hash})
	completed.append("viewpoint")
	_check_ownership()
	completed.append("ownership")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"failures": failures, "completed": completed}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"counts": counts, "failure_count": failures.size(), "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() and completed.size() == 4 else 1)


func _check_ownership() -> void:
	for wrong: Variant in [null, true, 1.0, -1, 4294967296, "1"]:
		_check("admission", "near type", Viewpoint.create(wrong, 0).ok, false)
		_check("admission", "far type", Viewpoint.create(0, wrong).ok, false)
	var state: Viewpoint.State = Viewpoint.create(0x3dcccccd, 0x442f0000).value
	var value: Dictionary = {"camera_identity": PackedInt32Array([65, 0, 0xd800]), "player_thing_identity": 7,
		"viewport": {"width": 640, "height": 480, "x": 0, "y": 0, "min_depth_bits": 0, "max_depth_bits": 0x3f800000}}
	_check("ownership", "update admitted", state.update_slot(0, value).ok, true)
	state.select_slot(0)
	var wanted: Dictionary = state.snapshot()
	value.viewport.width = 1
	value.camera_identity = PackedInt32Array([66])
	var detached: Dictionary = state.get_slot(0).value
	detached.viewport.width = 2
	detached.camera_identity[0] = 67
	state.selected_snapshot().current_viewport.width = 3
	state.snapshot().slots.clear()
	_check("ownership", "all returned/source containers detached", state.snapshot(), wanted)
	for wrong: Variant in [null, {}, {"camera_identity": null, "player_thing_identity": null},
		{"camera_identity": [], "player_thing_identity": null, "viewport": null},
		{"camera_identity": null, "player_thing_identity": true, "viewport": null},
		{"camera_identity": null, "player_thing_identity": 0, "viewport": {}}]:
		_check("admission", "bad slot record", state.update_slot(0, wrong).ok, false)
		_check("ownership", "bad record leaves state", state.snapshot(), wanted)
	for wrong: Variant in [null, true, 0.0, "0", -1, 2]:
		_check("admission", "slot carrier", state.select_slot(wrong).ok, false)
		_check("ownership", "bad index leaves state", state.snapshot(), wanted)
