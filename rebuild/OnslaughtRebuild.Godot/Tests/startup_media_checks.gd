# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Read-only comparisons against synthetic files owned by the oracle invocation.
## Never resolves the canonical cache or materializes a retail asset.
const Media = preload("res://Client/startup_media_index.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var completed: Array[String] = []
var _visits: Array = []
var _exists_mode: String = "real"


func _initialize() -> void:
	call_deferred("run_checks")


func check(category: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[category] = int(counts.get(category, 0)) + 1
	if actual != expected:
		failures.append({"category": category, "name": name, "actual": actual, "expected": expected})


func run_checks() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	check("fixture", "object", parsed is Dictionary, true)
	if parsed is Dictionary:
		if _run_fixtures(_integers(parsed.get("startup_media"))):
			completed.append("startup_media")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"failures": failures, "completed": completed}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify({"failure_count": failures.size(), "counts": counts, "first_failures": failures.slice(0, 5)}))
	quit(0 if failures.is_empty() and completed == ["startup_media"] else 1)


func _run_fixtures(vectors: Variant) -> bool:
	check("fixture", "media_object", vectors is Dictionary, true)
	if not vectors is Dictionary:
		return false
	check("fixture", "schema", vectors.get("schema"), 1)
	var cases: Variant = vectors.get("cases")
	var files: Variant = vectors.get("files")
	if not cases is Array or not files is Array:
		check("fixture", "collections", false, true)
		return false
	check("fixture", "nonempty_cases", not cases.is_empty(), true)
	check("fixture", "nonempty_files", not files.is_empty(), true)
	if cases.is_empty() or files.is_empty():
		return false
	for row: Dictionary in files:
		check("read_only", row.path + ":before", _shape(Media.compute_file_sha256(row.path)), {"ok": true, "value": row.sha256})
		if OS.get_name() != "Windows" and String(row.path).contains("\\"):
			var read: Dictionary = Media.read_file_bytes_exact(row.path)
			check("exact_read_bytes", row.path + ":admitted", read.get("ok"), true)
			if read.get("ok") == true:
				var digest := HashingContext.new()
				digest.start(HashingContext.HASH_SHA256)
				digest.update(read.value)
				check("exact_read_bytes", row.path + ":identity", digest.finish().hex_encode().to_upper(), row.sha256)
	var finished: int = 0
	for row: Dictionary in cases:
		var success: bool = _run_case(row)
		check("fixture", row.name + ":completed", success, true)
		if success:
			finished += 1
	for row: Dictionary in files:
		check("read_only", row.path + ":after", _shape(Media.compute_file_sha256(row.path)), {"ok": true, "value": row.sha256})
	var expected_files: Array[String] = []
	for row: Dictionary in files:
		expected_files.append(row.path)
	expected_files.sort()
	var actual_files: Array[String] = []
	_collect_files(vectors.root, actual_files)
	actual_files.sort()
	check("read_only", "no_new_or_removed_files", actual_files, expected_files)
	var transport_finished: bool = _check_transport(vectors.root)
	return finished == cases.size() and transport_finished


func _run_case(row: Dictionary) -> bool:
	_exists_mode = row.exists_mode
	_visits.clear()
	var input_root: Variant = null if row.root_units == null else PackedInt32Array(row.root_units)
	var result: Dictionary = Media.load_index(input_root, null if _exists_mode == "null" else _file_exists, _raw_file_exists)
	var actual: Dictionary
	if result.get("ok") == true:
		actual = {"ok": true, "value": _state(result.value)}
	else:
		actual = _shape(result)
	check("load", row.name, actual, row.expected)
	check("file_exists_order", row.name, _visits, row.visits)
	if _exists_mode == "real":
		var native: Dictionary = Media.load_cache(input_root)
		var native_state: Dictionary = {"ok": true, "value": _state(native.value)} if native.get("ok") == true else _shape(native)
		check("native_file_exists", row.name, native_state, row.expected)
	if result.get("ok") == true and row.expected.ok:
		var index: RefCounted = result.value
		for frame: Dictionary in row.frames:
			check("frame_path", "%s:%s:%s" % [row.name, frame.cue, frame.frame],
				_path_shape(index.frame_relative_path(frame.cue, frame.frame)), frame.result)
		for audio: Dictionary in row.audio:
			check("audio_path", "%s:%s" % [row.name, audio.cue], _path_shape(index.audio_relative_path(audio.cue)), audio.result)
		var before: Dictionary = _state(index)
		var clips: Dictionary = index.clips()
		var tracks: Dictionary = index.clip_audio()
		for cue: int in clips:
			clips[cue].frame_count = -1
		for cue: int in tracks:
			tracks[cue].sample_rate = -1
		check("value_isolation", row.name, _state(index), before)
	return true


func _file_exists(path: String) -> Variant:
	return _observe_exists(Media.text_units(path).value)


func _raw_file_exists(path: PackedInt32Array) -> Variant:
	return _observe_exists(path)


func _observe_exists(path: PackedInt32Array) -> Variant:
	_visits.append(Array(path))
	if _exists_mode == "none":
		return false
	if path.has(0):
		if _exists_mode == "nul_true":
			return true
		if _exists_mode == "nul_io":
			return {"ok": false, "error_type": "IOException", "error": "fixture IO"}
		if _exists_mode == "nul_argument":
			return {"ok": false, "error_type": "ArgumentException", "error": "fixture argument"}
	if _exists_mode == "manifest_io" and _ends_with(path, "startup-media.json"):
		return {"ok": false, "error_type": "IOException", "error": "fixture IO"}
	if _find_units(path, "frames/") >= 0 or _find_units(path, "frames\\") >= 0:
		if _exists_mode == "frame_io":
			return {"ok": false, "error_type": "IOException", "error": "fixture IO"}
		if _exists_mode == "frame_argument":
			return {"ok": false, "error_type": "ArgumentException", "error": "fixture argument"}
	if _exists_mode == "audio_io" and _ends_with(path, "voice.wav"):
		return {"ok": false, "error_type": "IOException", "error": "fixture IO"}
	if path.has(0):
		return false # File.Exists never hands an embedded NUL to the OS.
	var text: Dictionary = Media.text_from_units(path)
	if not text.ok or typeof(text.value) != TYPE_STRING:
		return {"ok": false, "error_type": "FixtureError", "error": "Unexpected raw path in synthetic fixture callback."}
	var result: Dictionary = Media.file_exists_exact(text.value)
	return result.value if result.ok else result


static func _state(index: RefCounted) -> Dictionary:
	var clips: Array[Dictionary] = []
	var source: Dictionary = index.clips()
	for cue: int in source:
		var row: Dictionary = source[cue]
		row.cue = cue
		clips.append(row)
	var tracks: Array[Dictionary] = []
	source = index.clip_audio()
	for cue: int in source:
		var row: Dictionary = source[cue]
		row.cue = cue
		tracks.append(row)
	return {"root_units": Array(Media.text_units(index.root_path()).value), "has_splash": index.has_splash(),
		"splash_relative_units": null if index.splash_relative_path() == null else Array(Media.text_units(index.splash_relative_path()).value),
		"unavailable": _unavailable(index.unavailable()), "unavailable_identity_units": _unavailable_identity(index.unavailable()),
		"clips": clips, "audio": tracks}


static func _unavailable(value: Variant) -> Variant:
	if value == null:
		return null
	var text: PackedInt32Array = Media.text_units(value).value
	if _find_units(text, "No startup media cache") == 0:
		return "no_root"
	if _find_units(text, "No startup media index") == 0:
		return "missing"
	if _find_units(text, " is unreadable:") >= 0:
		return "unreadable"
	if _find_units(text, " is not schema ") >= 0:
		return "schema"
	if _find_units(text, " listed no usable ") >= 0:
		return "empty"
	return "unknown"


static func _unavailable_identity(value: Variant) -> Variant:
	if value == null:
		return null
	var units: PackedInt32Array = Media.text_units(value).value
	var marker: String = " is unreadable:"
	var at: int = _find_units(units, marker)
	return Array(units if at < 0 else units.slice(0, at + marker.length()))


static func _find_units(source: PackedInt32Array, needle: String) -> int:
	var target: PackedInt32Array = Media.text_units(needle).value
	for start: int in range(source.size() - target.size() + 1):
		if source.slice(start, start + target.size()) == target:
			return start
	return -1


static func _ends_with(source: PackedInt32Array, needle: String) -> bool:
	var target: PackedInt32Array = Media.text_units(needle).value
	return source.size() >= target.size() and source.slice(source.size() - target.size()) == target


static func _path_shape(result: Dictionary) -> Dictionary:
	if result.get("ok") == true:
		var units: Dictionary = Media.text_units(result.get("value"))
		return {"ok": true, "value_units": Array(units.value)} if units.ok else _shape(units)
	return _shape(result)


func _check_transport(owned_root: String) -> bool:
	var raw: PackedInt32Array = Media.text_units(owned_root).value
	raw.append(0)
	raw.append_array(PackedInt32Array([115, 117, 102, 102, 105, 120]))
	check("raw_text", "round_trip_nul", Media.text_units(Media.text_from_units(raw).value).value, raw)
	var bom_text := PackedInt32Array([0xfeff, 120])
	check("raw_text", "leading_feff_is_text", Media.text_units(Media.text_from_units(bom_text).value).value, bom_text)
	for value: Variant in [false, 1, [], PackedInt32Array([-1]), PackedInt32Array([65536])]:
		check("raw_text", "invalid_units_" + str(value), Media.text_units(value).get("error_type"), "ArgumentException")
	_visits.clear()
	_exists_mode = "real"
	var missing_callback: Dictionary = Media.load_index(raw, _file_exists)
	check("raw_text", "custom_raw_callback_required", missing_callback.get("error_type"), "RawPathCallbackRequired")
	check("raw_text", "no_truncated_callback", _visits, [])
	check("raw_text", "raw_callback_path_units", missing_callback.get("path_units"),
		Media.text_units(Media.combine_path(raw, "startup-media.json")).value)
	check("raw_text", "null_callback_precedes_bad_root", Media.load_index(123, null).get("error_type"), "ArgumentNullException")
	check("raw_text", "invalid_root", Media.load_index(123, _file_exists).get("error_type"), "ArgumentException")
	return true


static func _shape(result: Dictionary) -> Dictionary:
	if typeof(result.get("ok")) != TYPE_BOOL:
		return {"invalid_operation_result": true}
	if result.ok:
		return {"ok": true, "value": result.get("value")}
	return {"ok": false, "error_type": result.get("error_type")}


func _integers(value: Variant) -> Variant:
	if typeof(value) == TYPE_FLOAT:
		if not is_finite(value) or abs(value) > 9007199254740991.0 or floor(value) != value:
			check("fixture", "exact_integer", value, "exact integer")
			return value
		return int(value)
	if value is Array:
		var array: Array = []
		for item: Variant in value:
			array.append(_integers(item))
		return array
	if value is Dictionary:
		var dictionary: Dictionary = {}
		for key: Variant in value:
			dictionary[key] = _integers(value[key])
		return dictionary
	return value


func _collect_files(path: String, output: Array[String]) -> void:
	for name: String in DirAccess.get_files_at(path):
		output.append(path.path_join(name))
	for name: String in DirAccess.get_directories_at(path):
		_collect_files(path.path_join(name), output)
