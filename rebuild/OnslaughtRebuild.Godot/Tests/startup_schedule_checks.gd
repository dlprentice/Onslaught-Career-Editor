# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Pure model differential checks; arguments are an oracle JSON and owned report
## path. Neither the production module nor this test reads any private media.

const Startup = preload("res://Client/startup_schedule.gd")
const CLIP_FIELDS: Array[String] = ["frame_count", "fps_numerator", "fps_denominator", "width", "height"]
var failures: Array[Dictionary] = []
var counts: Dictionary = {}


func _initialize() -> void:
	call_deferred("run_checks")


func check(category: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[category] = int(counts.get(category, 0)) + 1
	if actual != expected:
		failures.append({"category": category, "name": name, "actual": actual, "expected": expected})


func double_word(value: float) -> String:
	if is_nan(value):
		return "nan"
	var bytes := PackedByteArray()
	bytes.resize(8)
	bytes.encode_double(0, value)
	return bytes.hex_encode()


func single_word(value: float) -> String:
	if is_nan(value):
		return "nan"
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	return bytes.hex_encode()


func decode_double(word: String) -> float:
	return NAN if word == "nan" else word.hex_decode().decode_double(0)


func fixture_int(value: Variant, name: String) -> int:
	# JSON number tokens are binary64 in Godot. Admit the exact C# int32 range
	# before converting; fixture decoding never defines production admission.
	check("fixture", name, typeof(value) == TYPE_FLOAT or typeof(value) == TYPE_INT, true)
	var number: float = float(value)
	check("fixture", name + ":int32", is_finite(number) and number >= -2147483648.0 \
		and number <= 2147483647.0 and number == float(int(number)), true)
	return int(number)


func fixture_clip(row: Dictionary) -> Dictionary:
	var clip: Dictionary = {}
	for field: String in CLIP_FIELDS:
		clip[field] = fixture_int(row[field], field)
	return clip


func fixture_clips(rows: Array) -> Dictionary:
	var clips: Dictionary = {}
	for row: Dictionary in rows:
		clips[fixture_int(row.cue, "cue")] = fixture_clip(row)
	return clips


func fixture_frame(row: Dictionary) -> Dictionary:
	return {"kind": fixture_int(row.kind, "kind"),
		"cue": null if row.cue == null else fixture_int(row.cue, "cue"),
		"frame_index": fixture_int(row.frame_index, "frame_index"),
		"alpha": row.alpha, "beat_seconds": row.beat_seconds}


func frame_words(frame: Dictionary) -> Dictionary:
	return {"kind": frame.kind, "cue": frame.cue, "frame_index": frame.frame_index,
		"alpha": single_word(frame.alpha), "beat_seconds": double_word(frame.beat_seconds)}


func construct(mode: String, clips: Variant, splash: bool = false, cue: int = 3) -> Dictionary:
	match mode:
		"cold": return Startup.create(clips, splash)
		"single": return Startup.for_single_clip(cue, clips)
		"attract": return Startup.for_attract_restart(clips)
	return {"ok": false, "error_type": "UnknownFixtureMode", "error": mode}


func check_schedules(rows: Array) -> void:
	check("fixture", "nonempty_schedules", not rows.is_empty(), true)
	for row: Dictionary in rows:
		var clips: Dictionary = fixture_clips(row.clips)
		var created: Dictionary = construct(row.mode, clips, row.splash_present, fixture_int(row.cue, "single cue"))
		check("construction", row.name, created.ok, true)
		if not created.ok:
			continue
		var schedule: Startup.Schedule = created.value
		var missing: Array[int] = []
		for cue: Variant in row.missing_cues:
			missing.append(fixture_int(cue, "missing cue"))
		check("metadata", row.name + ":total", double_word(schedule.get_total_seconds()), row.total_seconds)
		check("metadata", row.name + ":missing", schedule.get_missing_cues(), missing)
		check("metadata", row.name + ":empty", schedule.is_empty(), row.is_empty)
		var detached_missing: Array[int] = schedule.get_missing_cues()
		detached_missing.append(999)
		check("isolation", row.name + ":missing", schedule.get_missing_cues(), missing)
		# C# stores each value-type clip's timing while constructing its beats.
		# Later changes to the caller's map/records must not change the schedule.
		for cue: Variant in clips:
			clips[cue].frame_count = 1
			clips[cue].fps_numerator = 1
		clips.clear()
		for index: int in range(row.samples.size()):
			var sample_row: Dictionary = row.samples[index]
			var expected: Dictionary = fixture_frame(sample_row.frame)
			var elapsed: float = decode_double(sample_row.elapsed)
			var sampled: Dictionary = schedule.sample(elapsed)
			var name: String = row.name + ":" + str(index)
			check("sample_admission", name, sampled.ok, true)
			if not sampled.ok:
				continue
			check("frame_words", name, frame_words(sampled.value), expected)
			sampled.value.kind = -1
			sampled.value.frame_index = 999
			check("pure_detached_sample", name, frame_words(schedule.sample(elapsed).value), expected)
		check("metadata", row.name + ":total_after_samples", double_word(schedule.get_total_seconds()), row.total_seconds)
		check("metadata", row.name + ":missing_after_samples", schedule.get_missing_cues(), missing)


func check_arguments(rows: Array) -> void:
	check("fixture", "nonempty_arguments", not rows.is_empty(), true)
	for row: Dictionary in rows:
		var result: Dictionary = Startup.is_suppressed_by_arguments(row.arguments)
		check("arguments", row.name + ":admission", result.ok, row.ok)
		if result.ok and row.ok:
			check("arguments", row.name, result.value, row.value)
			var packed := PackedStringArray()
			for argument: String in row.arguments:
				packed.append(argument)
			check("arguments", row.name + ":packed", Startup.is_suppressed_by_arguments(packed).value, row.value)
		elif not result.ok and not row.ok:
			check("arguments", row.name + ":error", result.error_type, row.error_type)


func check_clip_timings(rows: Array) -> void:
	check("fixture", "nonempty_clip_timings", not rows.is_empty(), true)
	for index: int in range(rows.size()):
		var row: Dictionary = rows[index]
		var result: Dictionary = Startup.clip_timing(fixture_clip(row.clip))
		check("clip_timing", str(index) + ":admission", result.ok, true)
		if result.ok:
			check("clip_timing", str(index) + ":fps", double_word(result.value.frames_per_second), row.frames_per_second)
			check("clip_timing", str(index) + ":duration", double_word(result.value.duration_seconds), row.duration_seconds)


func check_admission(rows: Array) -> void:
	for row: Dictionary in rows:
		var result: Dictionary = construct(row.mode, null)
		check("admission", row.mode + ":null_clips", result.ok, false)
		check("admission", row.mode + ":exception_type", result.get("error_type"), row.error_type)
	for invalid: Variant in [[], "clips", 0, false]:
		check("admission", "invalid_clip_map", Startup.create(invalid, false).ok, false)
	for invalid: Variant in [0, 1.0, "true", null]:
		check("admission", "invalid_splash_presence", Startup.create({}, invalid).ok, false)
	for invalid: Variant in [0.0, "0", null, true, 2147483648, -2147483649]:
		check("admission", "invalid_single_cue", Startup.for_single_clip(invalid, {}).ok, false)
	var clip: Dictionary = {"frame_count": 229, "fps_numerator": 25, "fps_denominator": 1, "width": 480, "height": 300}
	for field: String in CLIP_FIELDS:
		var incomplete: Dictionary = clip.duplicate(true)
		incomplete.erase(field)
		check("admission", "missing:" + field, Startup.clip_timing(incomplete).ok, false)
		for invalid: Variant in [1.0, null, "1", true, 2147483648, -2147483649]:
			var changed: Dictionary = clip.duplicate(true)
			changed[field] = invalid
			check("admission", "typed_int32:" + field, Startup.clip_timing(changed).ok, false)
	for invalid: Variant in [null, [], "clip", 0]:
		check("admission", "invalid_clip", Startup.clip_timing(invalid).ok, false)
	for invalid: Variant in [false, "--intro", 7, [false], [1]]:
		check("admission", "invalid_arguments", Startup.is_suppressed_by_arguments(invalid).ok, false)
	var schedule: Startup.Schedule = Startup.create({}, true).value
	var before: Dictionary = frame_words(schedule.sample(0.0).value)
	for invalid: Variant in [null, "0", true, [], {}]:
		check("admission", "invalid_elapsed", schedule.sample(invalid).ok, false)
		check("admission", "invalid_elapsed_keeps_schedule", frame_words(schedule.sample(0.0).value), before)
	check("admission", "null_clips_precede_invalid_splash", Startup.create(null, "invalid").error_type, "ArgumentNullException")


func run_checks() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() != 2:
		quit(2)
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	if typeof(parsed) != TYPE_DICTIONARY or not parsed.has("startup"):
		quit(2)
		return
	var vectors: Dictionary = parsed.startup
	var constants: Dictionary = vectors.constants
	check("constants", "black", double_word(Startup.INTER_CLIP_BLACK_SECONDS), constants.inter_clip_black_seconds)
	check("constants", "fade", double_word(Startup.SPLASH_FADE_IN_SECONDS), constants.splash_fade_in_seconds)
	check("constants", "hold", double_word(Startup.SPLASH_HOLD_SECONDS), constants.splash_hold_seconds)
	var cues: Array[int] = []
	for cue: Variant in constants.cue_ids:
		cues.append(fixture_int(cue, "cue enum"))
	check("constants", "cue_ids", Startup.Cue.values(), cues)
	var kinds: Array[int] = []
	for kind: Variant in constants.frame_kind_ids:
		kinds.append(fixture_int(kind, "frame enum"))
	check("constants", "frame_kind_ids", Startup.FrameKind.values(), kinds)
	check_schedules(vectors.schedules)
	check_arguments(vectors.arguments)
	check_clip_timings(vectors.clip_timings)
	check_admission(vectors.construction_errors)
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "counts": counts,
		"failures": failures, "completed": ["startup_schedule"]}
	var file := FileAccess.open(args[1], FileAccess.WRITE)
	if file == null:
		quit(2)
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print(JSON.stringify({"failure_count": failures.size(), "counts": counts, "first_failures": failures.slice(0, 3)}))
	quit(0 if failures.is_empty() else 1)
