# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure injected-time schedule port of Godot/RetailStartupSchedule.cs.
## Factories return {ok, value: Schedule} or {ok:false, error_type, error}.
## A Schedule owns no clock, node, input, filesystem or playback state. Calling
## sample in any order cannot advance it. The host still owns abort/skip input.

enum Cue { LOST_TOYS_LOGO = 0, OPENING_MONTAGE = 1, SPLASH = 2, LEVEL100_INTRO_CUTSCENE = 3 }
enum FrameKind { BLACK = 0, VIDEO = 1, SPLASH = 2, FINISHED = 3 }

const INTER_CLIP_BLACK_SECONDS: float = 0.0
const SPLASH_FADE_IN_SECONDS: float = 1.5
const SPLASH_HOLD_SECONDS: float = 3.0
const _CLIP_FIELDS: Array[String] = ["frame_count", "fps_numerator", "fps_denominator", "width", "height"]


class Schedule extends RefCounted:
	var _beats: Array[Dictionary]
	var _missing: Array[int]
	var _total_seconds: float

	func _init(beats: Array[Dictionary], missing: Array[int], total_seconds: float) -> void:
		_beats = beats
		_missing = missing
		_total_seconds = total_seconds


	func get_total_seconds() -> float:
		return _total_seconds


	func get_missing_cues() -> Array[int]:
		return _missing.duplicate()


	func is_empty() -> bool:
		# Retain the C# count test, including a zero-duration Black beat when
		# both map keys exist but their nonpositive FrameCounts omit the videos.
		return _beats.is_empty()


	## Success value: {kind, cue:int|null, frame_index, alpha, beat_seconds}.
	## C# admits every double, including infinities/NaN; do not add a finite gate.
	func sample(elapsed_seconds: Variant) -> Dictionary:
		if typeof(elapsed_seconds) != TYPE_FLOAT and typeof(elapsed_seconds) != TYPE_INT:
			return {"ok": false, "error_type": "ArgumentException", "error": "elapsed seconds must be numeric"}
		var time: float = float(elapsed_seconds)
		# Math.Max(0d, elapsed) propagates NaN and selects +0 for negative zero.
		if time <= 0.0:
			time = 0.0
		if time >= _total_seconds:
			return _frame(FrameKind.FINISHED, null, 0, 0.0, 0.0)
		for beat: Dictionary in _beats:
			if time >= beat.start_seconds + beat.duration_seconds:
				continue
			var local: float = time - beat.start_seconds
			match int(beat.kind):
				FrameKind.VIDEO:
					var index: int = _unchecked_int32(floor(local * beat.frames_per_second))
					index = clampi(index, 0, int(beat.frame_count) - 1)
					return _frame(FrameKind.VIDEO, beat.cue, index, 1.0, local)
				FrameKind.SPLASH:
					var alpha: float = 1.0
					if beat.fade_in:
						alpha = local / beat.duration_seconds
						# Math.Clamp propagates NaN. Only this output is stored as
						# float32; all cue boundaries and local times stay binary64.
						if alpha < 0.0:
							alpha = 0.0
						elif alpha > 1.0:
							alpha = 1.0
						var bytes := PackedByteArray()
						bytes.resize(4)
						bytes.encode_float(0, alpha)
						alpha = bytes.decode_float(0)
					return _frame(FrameKind.SPLASH, beat.cue, 0, alpha, local)
				_:
					return _frame(FrameKind.BLACK, null, 0, 0.0, local)
		return _frame(FrameKind.FINISHED, null, 0, 0.0, 0.0)


	static func _frame(kind: int, cue: Variant, index: int, alpha: float, local: float) -> Dictionary:
		return {"ok": true, "value": {"kind": kind, "cue": cue, "frame_index": index,
			"alpha": alpha, "beat_seconds": local}}


	static func _unchecked_int32(value: float) -> int:
		# C# net8's unchecked x64 conversion yields INT_MIN for a nonfinite or
		# out-of-range double. Sampling immediately clamps that to frame zero.
		# The oracle covers this existing behavior; no new media admission is added.
		if not is_finite(value) or value < -2147483648.0 or value >= 2147483648.0:
			return -2147483648
		return int(value)


## clips is keyed by integer Cue. Each value contains the five signed-int32
## fields in _CLIP_FIELDS. Rates/dimensions retain the source's admission:
## only FrameCount<=0 makes a decoded cue absent; media-index checks live above.
static func create(clips: Variant, splash_present: Variant) -> Dictionary:
	var admitted: Dictionary = _admit_clips(clips)
	if not admitted.ok:
		return admitted
	if typeof(splash_present) != TYPE_BOOL:
		return _failure("ArgumentException", "splash presence must be boolean")
	return _build_chain(admitted.value, true, splash_present)


static func for_single_clip(cue: Variant, clips: Variant) -> Dictionary:
	var admitted: Dictionary = _admit_clips(clips)
	if not admitted.ok:
		return admitted
	if not _is_int32(cue):
		return _failure("ArgumentException", "cue must be a signed-int32 enum value")
	var beats: Array[Dictionary] = []
	var missing: Array[int] = []
	var total: float = _append_video(int(cue), admitted.value, 0.0, beats, missing)
	return {"ok": true, "value": Schedule.new(beats, missing, total)}


static func for_attract_restart(clips: Variant) -> Dictionary:
	var admitted: Dictionary = _admit_clips(clips)
	if not admitted.ok:
		return admitted
	return _build_chain(admitted.value, false, false)


## The source's --intro override is checked only after examining every argument.
## A null list/element therefore still fails even if --intro was seen earlier.
static func is_suppressed_by_arguments(arguments: Variant) -> Dictionary:
	if arguments == null:
		return _failure("ArgumentNullException", "arguments must not be null")
	if typeof(arguments) != TYPE_ARRAY and typeof(arguments) != TYPE_PACKED_STRING_ARRAY:
		return _failure("ArgumentException", "arguments must be an array of strings")
	var forced: bool = false
	var suppressed: bool = false
	for argument: Variant in arguments:
		if argument == null:
			return _failure("NullReferenceException", "argument must not be null")
		if typeof(argument) != TYPE_STRING:
			return _failure("ArgumentException", "argument must be a string")
		var text: String = argument
		if text == "--intro":
			forced = true
		elif text == "--skipfmv" or text == "--smoke" or text.begins_with("--capture-dir=") \
				or text.begins_with("--capture-plan=") or text.begins_with("--capture-size=") \
				or text.begins_with("--capture-offsets-ms="):
			suppressed = true
	return {"ok": true, "value": not forced and suppressed}


static func clip_timing(clip: Variant) -> Dictionary:
	var admitted: Dictionary = _admit_clip(clip)
	if not admitted.ok:
		return admitted
	return {"ok": true, "value": _timing(admitted.value)}


static func _build_chain(clips: Dictionary, with_splash: bool, splash_present: bool) -> Dictionary:
	var beats: Array[Dictionary] = []
	var missing: Array[int] = []
	var cursor: float = _append_video(Cue.LOST_TOYS_LOGO, clips, 0.0, beats, missing)
	if clips.has(Cue.LOST_TOYS_LOGO) and clips.has(Cue.OPENING_MONTAGE):
		beats.append(_beat(FrameKind.BLACK, null, cursor, INTER_CLIP_BLACK_SECONDS, false, 0.0, 0))
		cursor += INTER_CLIP_BLACK_SECONDS
	cursor = _append_video(Cue.OPENING_MONTAGE, clips, cursor, beats, missing)
	if with_splash:
		if splash_present:
			beats.append(_beat(FrameKind.SPLASH, Cue.SPLASH, cursor, SPLASH_FADE_IN_SECONDS, true, 0.0, 0))
			cursor += SPLASH_FADE_IN_SECONDS
			beats.append(_beat(FrameKind.SPLASH, Cue.SPLASH, cursor, SPLASH_HOLD_SECONDS, false, 0.0, 0))
			cursor += SPLASH_HOLD_SECONDS
		else:
			missing.append(Cue.SPLASH)
	return {"ok": true, "value": Schedule.new(beats, missing, cursor)}


static func _append_video(cue: int, clips: Dictionary, cursor: float,
		beats: Array[Dictionary], missing: Array[int]) -> float:
	if not clips.has(cue) or int(clips[cue].frame_count) <= 0:
		missing.append(cue)
		return cursor
	var clip: Dictionary = clips[cue]
	var timing: Dictionary = _timing(clip)
	beats.append(_beat(FrameKind.VIDEO, cue, cursor, timing.duration_seconds,
		false, timing.frames_per_second, clip.frame_count))
	return cursor + timing.duration_seconds


static func _beat(kind: int, cue: Variant, start: float, duration: float,
		fade_in: bool, rate: float, count: int) -> Dictionary:
	return {"kind": kind, "cue": cue, "start_seconds": start, "duration_seconds": duration,
		"fade_in": fade_in, "frames_per_second": rate, "frame_count": count}


static func _timing(clip: Dictionary) -> Dictionary:
	# C# multiplies two int fields before the double division. Preserve its
	# unchecked int32 wrap instead of silently widening that intermediate.
	var product: int = (int(clip.frame_count) * int(clip.fps_denominator)) & 0xffffffff
	if product > 0x7fffffff:
		product -= 0x100000000
	return {"frames_per_second": _divide_ieee(float(clip.fps_numerator), float(clip.fps_denominator)),
		"duration_seconds": _divide_ieee(float(product), float(clip.fps_numerator))}


static func _divide_ieee(numerator: float, denominator: float) -> float:
	# GDScript reports a division-by-zero error; the C# double operation returns
	# IEEE infinity/NaN. Reproduce that value without an engine diagnostic.
	if denominator != 0.0:
		return numerator / denominator
	if numerator == 0.0:
		return NAN
	return -INF if numerator < 0.0 else INF


static func _admit_clips(value: Variant) -> Dictionary:
	if value == null:
		return _failure("ArgumentNullException", "clips must not be null")
	if typeof(value) != TYPE_DICTIONARY:
		return _failure("ArgumentException", "clips must be a dictionary keyed by cue")
	var source: Dictionary = value
	var clips: Dictionary = {}
	for cue: Variant in source:
		if not _is_int32(cue):
			return _failure("ArgumentException", "clip key must be a signed-int32 enum value")
		var admitted: Dictionary = _admit_clip(source[cue])
		if not admitted.ok:
			return admitted
		clips[int(cue)] = admitted.value
	return {"ok": true, "value": clips}


static func _admit_clip(value: Variant) -> Dictionary:
	if typeof(value) != TYPE_DICTIONARY:
		return _failure("ArgumentException", "clip must contain its five int32 fields")
	var source: Dictionary = value
	var clip: Dictionary = {}
	for field: String in _CLIP_FIELDS:
		if not source.has(field) or not _is_int32(source[field]):
			return _failure("ArgumentException", "clip field must be a signed-int32 integer: " + field)
		clip[field] = int(source[field])
	return {"ok": true, "value": clip}


static func _is_int32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}
