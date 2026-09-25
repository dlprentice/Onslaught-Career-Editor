# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Two required args: oracle JSON and owned report path. Optional explicit
## --startup-batch-fixture=ABS plus --startup-media=ABS compare the production
## adapter with an existing object-free batch saved by the retained C# provider.
## This check never creates assets, fixtures, or cache files.

const Batch = preload("res://Client/startup_media_batch.gd")
const Media = preload("res://Client/startup_media_index.gd")
const Playback = preload("res://Scenes/Frontend/startup_sequence.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var completed: Array[String] = []


func _initialize() -> void:
	call_deferred("run_checks")


func check(category: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[category] = int(counts.get(category, 0)) + 1
	if actual != expected:
		failures.append({"category": category, "name": name, "actual": actual, "expected": expected})


func run_checks() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 2:
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	check("fixture", "object", parsed is Dictionary, true)
	if parsed is Dictionary:
		var vectors_done: bool = _run_vectors(_integers(parsed.get("startup_media_batch")))
		var private_done: bool = _run_private(args)
		if vectors_done and private_done:
			completed.append("startup_media_batch")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"failures": failures, "completed": completed}
	var output := FileAccess.open(args[1], FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print(JSON.stringify({"failure_count": failures.size(), "counts": counts, "first_failures": failures.slice(0, 5)}))
	quit(0 if failures.is_empty() and completed == ["startup_media_batch"] else 1)


func _run_vectors(vectors: Variant) -> bool:
	check("fixture", "batch_object", vectors is Dictionary, true)
	if not vectors is Dictionary:
		return false
	check("fixture", "schema", vectors.get("schema"), 1)
	check("fixture", "platform", vectors.get("platform"), "Windows" if OS.get_name() == "Windows" else "Unix")
	var paths: Variant = vectors.get("paths")
	if not paths is Array or paths.is_empty():
		check("fixture", "nonempty_paths", false, true)
		return false
	var current_directory := PackedInt32Array(vectors.current_directory_units)
	for row: Dictionary in paths:
		var input: Variant = null if row.path_units == null else PackedInt32Array(row.path_units)
		check("full_path", row.name, _path_shape(Batch.get_full_path(input, current_directory)), row.result)
		# Exercise the real process CWD as well; the oracle host must share it.
		check("process_full_path", row.name, _path_shape(Batch.get_full_path(input)), row.result)
	var empty: Dictionary = Batch.load_verified_media_batch(null)
	check("batch", "missing_cache", _shape(empty), {"ok": true, "value": vectors.empty_batch})
	for invalid: Variant in [false, 1, [], PackedInt32Array([-1])]:
		check("admission", "invalid_path_" + str(invalid), Batch.get_full_path(invalid).get("error_type"), "ArgumentException")
	return _run_playback(vectors.get("playback"))


func _run_playback(fixture: Variant) -> bool:
	check("playback_fixture", "dictionary", fixture is Dictionary, true)
	if not fixture is Dictionary:
		return false
	var files: Variant = fixture.get("files")
	check("playback_fixture", "files_array", files is Array, true)
	if not files is Array or files.size() != 3:
		check("playback_fixture", "three_color_controls", false, true)
		return false
	var names: Array[String] = []
	var wanted_paths: Array[String] = []
	for row: Dictionary in files:
		names.append(row.name)
		wanted_paths.append(row.path)
		check("playback_read_only", row.name + ":before", _shape(Media.compute_file_sha256(row.path)),
			{"ok": true, "value": row.sha256})
	check("playback_fixture", "named_controls", names, ["literal_backslash_red", "normalized_alias_blue", "regular_green"])
	check("playback_fixture", "distinct_path_identity", files[0].path != files[1].path, true)
	check("playback_fixture", "literal_and_alias_relation", String(files[0].path).replace("\\", "/"), files[1].path)
	check("playback_fixture", "distinct_pixel_identity", files[0].rgba != files[1].rgba, true)
	check("playback_fixture", "distinct_byte_identity", files[0].bytes_hex != files[1].bytes_hex, true)
	for row: Dictionary in files:
		var bytes: Dictionary = Playback._read_media_bytes(row.path)
		check("playback_bytes", row.name + ":read", bytes.get("ok"), true)
		if bytes.get("ok") == true:
			check("playback_bytes", row.name + ":exact", bytes.get("value"), String(row.bytes_hex).hex_decode())
		var image := Image.new()
		var decoded: Error = Playback._load_png(image, row.path)
		check("playback_png", row.name + ":decode", decoded, OK)
		if decoded == OK:
			check("playback_png", row.name + ":width", image.get_width(), 1)
			check("playback_png", row.name + ":height", image.get_height(), 1)
			var pixel: Color = image.get_pixel(0, 0)
			check("playback_png", row.name + ":selected_pixel", [pixel.r8, pixel.g8, pixel.b8, pixel.a8], row.rgba)
	for row: Dictionary in files:
		check("playback_read_only", row.name + ":after", _shape(Media.compute_file_sha256(row.path)),
			{"ok": true, "value": row.sha256})
	var actual_paths: Array[String] = []
	_collect_files(fixture.root, actual_paths)
	actual_paths.sort()
	wanted_paths.sort()
	check("playback_read_only", "no_new_or_removed_files", actual_paths, wanted_paths)
	return true


func _collect_files(path: String, result: Array[String]) -> void:
	for name: String in DirAccess.get_files_at(path):
		result.append(path.path_join(name))
	for name: String in DirAccess.get_directories_at(path):
		_collect_files(path.path_join(name), result)


func _run_private(args: PackedStringArray) -> bool:
	var fixture: String = ""
	var media_root: String = ""
	for argument: String in args.slice(2):
		if argument.begins_with("--startup-batch-fixture="):
			fixture = argument.substr("--startup-batch-fixture=".length())
		elif argument.begins_with("--startup-media="):
			media_root = argument.substr("--startup-media=".length())
		else:
			check("private_fixture", "known_argument", argument, "supported private-batch option")
			return false
	if fixture.is_empty() and media_root.is_empty():
		return true
	if fixture.is_empty() or media_root.is_empty():
		check("private_fixture", "explicit_paths", false, true)
		return false
	var before: String = FileAccess.get_sha256(fixture)
	var file := FileAccess.open(fixture, FileAccess.READ)
	if file == null:
		check("private_fixture", "readable", false, true)
		return false
	var expected: Variant = file.get_var(false)
	file.close()
	check("private_fixture", "object_free_dictionary", expected is Dictionary, true)
	if not expected is Dictionary:
		return false
	check("private_fixture", "schema", expected.get("schema"), Batch.SCHEMA)
	var result: Dictionary = Batch.load_verified_media_batch(media_root)
	check("private_fixture", "batch_admitted", result.get("ok"), true)
	if result.get("ok") != true:
		check("private_fixture", "batch_error", result, "verified production batch")
		return false
	var actual: Dictionary = result.value
	check("private_fixture", "exact_dictionary", actual == expected, true)
	check("private_fixture", "field_order", actual.keys(), expected.keys())
	for group: String in ["clips", "audio", "frame_paths"]:
		check("private_fixture", group + "_cue_order", actual[group].keys(), expected[group].keys())
	for cue: Variant in expected.frame_paths:
		var paths: Variant = actual.frame_paths.get(cue)
		var wanted: Variant = expected.frame_paths[cue]
		check("private_fixture", "frame_array_type_" + str(cue), typeof(paths), typeof(wanted))
		if typeof(paths) != typeof(wanted):
			continue
		check("private_fixture", "frame_count_" + str(cue), paths.size(), wanted.size())
		for frame: int in range(mini(paths.size(), wanted.size())):
			check("private_frame_path", "%s:%s" % [cue, frame], paths[frame], wanted[frame])
	check("private_fixture", "fixture_unchanged", FileAccess.get_sha256(fixture), before)
	return true


static func _shape(result: Dictionary) -> Dictionary:
	if typeof(result.get("ok")) != TYPE_BOOL:
		return {"invalid_result": true}
	return {"ok": true, "value": result.get("value")} if result.ok else {"ok": false, "error_type": result.get("error_type")}


static func _path_shape(result: Dictionary) -> Dictionary:
	if result.get("ok") == true:
		var units: Dictionary = Media.text_units(result.get("value"))
		return {"ok": true, "value_units": Array(units.value)} if units.ok else _shape(units)
	return _shape(result)


func _integers(value: Variant) -> Variant:
	if typeof(value) == TYPE_FLOAT:
		if not is_finite(value) or abs(value) > 9007199254740991.0 or floor(value) != value:
			check("fixture", "exact_integer", value, "exact integer")
			return value
		return int(value)
	if value is Array:
		var result: Array = []
		for item: Variant in value:
			result.append(_integers(item))
		return result
	if value is Dictionary:
		var result: Dictionary = {}
		for key: Variant in value:
			result[key] = _integers(value[key])
		return result
	return value
