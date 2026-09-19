# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Actual Startup.tscn playback owner. Runtime accepts one batch from the
## verified media provider, never a JSON manifest. Editor preview is one frozen,
## read-only image and is not admission of the movie inventory or its audio.

signal completed

const Schedule = preload("res://Client/startup_schedule.gd")
const MediaBatch = preload("res://Client/startup_media_batch.gd")
const MediaIndex = preload("res://Client/startup_media_index.gd")
const F32 = preload("res://Scenes/Shared/retail_float32.gd")
enum Route { COLD = 0, ATTRACT = 1, SINGLE_CLIP = 2 }
enum Clock { FIXED_TICK = 0, WALL = 1 }
const VERIFIED_BATCH_SCHEMA: String = "onslaught-startup-verified-batch.v1"
const PREVIEW_MANIFEST_SCHEMA: String = "onslaught-startup-media.v4"
const CUE_NAMES: Array[String] = ["LostToysLogo", "OpeningMontage", "Splash", "Level100IntroCutscene"]

@export_enum("Lost Toys logo:0", "Opening montage:1", "Splash:2", "Level 100 intro:3")
var editor_cue: int = Schedule.Cue.SPLASH:
	set(value):
		editor_cue = value
		if Engine.is_editor_hint() and is_node_ready():
			_show_editor_still()

var _stage: Control
var _video_surface: TextureRect
var _splash_fade: Control
var _splash_surface: TextureRect
var _authored_voice: AudioStreamPlayer
var _voice: AudioStreamPlayer
var _voice_started: Callable
var _voice_cue: Variant = null
var _video_buffers: Array[ImageTexture] = [null, null]
var _presented_buffer: int = 0
var _resident_cue: int = -1
var _resident_index: int = -1
var _splash_texture: ImageTexture
var _media: Dictionary = {}
var _schedule: Schedule.Schedule
var _clock: int = Clock.WALL
var _elapsed_seconds: float = 0.0
var _aborted: bool = false
var _completed: bool = false
var _initialized: bool = false
var _editor_problem: String = ""


## Production admission stays in GDScript and runs once before the node enters
## the scene tree. Editing/F6 cannot trigger a cache scan or playback.
func configure_from_cache(media_root: Variant, route: int, cue: int, clock: int,
		voice_started: Callable = Callable()) -> Dictionary:
	if _initialized:
		return _failure("The startup sequence is already initialized.")
	if Engine.is_editor_hint():
		return _failure("The editor preview does not initialize playback.")
	var loaded: Dictionary = MediaBatch.load_verified_media_batch(media_root)
	if not loaded.ok:
		return loaded
	return configure_verified_media(loaded.value, route, cue, clock, voice_started)


## The caller must obtain this batch through the verified media index. Shape
## checks prevent malformed bridge data; they do not replace byte admission.
## Failure is explicit and leaves this node uninitialized, including in release.
func configure_verified_media(batch: Dictionary, route: int, cue: int, clock: int,
		voice_started: Callable = Callable()) -> Dictionary:
	if _initialized:
		return _failure("The startup sequence is already initialized.")
	if Engine.is_editor_hint():
		return _failure("The editor preview does not initialize playback.")
	if route < Route.COLD or route > Route.SINGLE_CLIP:
		return _failure("Unknown startup route.")
	var admitted: Dictionary = _admit_batch_shape(batch)
	if not admitted.ok:
		return admitted
	var media: Dictionary = admitted.value
	if clock == Clock.WALL and not media.audio.is_empty() and not voice_started.is_valid():
		return _failure("Wall-clock audio requires its playback-retirement observer.")
	var splash: ImageTexture = null
	if route == Route.COLD and not String(media.splash_path).is_empty():
		splash = _load_image_texture(media.splash_path)
	var made: Dictionary
	match route:
		Route.COLD: made = Schedule.create(media.clips, splash != null)
		Route.ATTRACT: made = Schedule.for_attract_restart(media.clips)
		_: made = Schedule.for_single_clip(cue, media.clips)
	if not made.ok:
		return made
	_media = media
	_schedule = made.value
	_clock = clock
	_voice_started = voice_started
	_splash_texture = splash
	_initialized = true
	return {"ok": true}


func is_initialized() -> bool:
	return _initialized


func get_scheduled_seconds() -> float:
	return _schedule.get_total_seconds() if _schedule != null else 0.0


func get_missing_cues() -> Array[int]:
	return _schedule.get_missing_cues() if _schedule != null else []


func get_media_unavailable_reason() -> String:
	return String(_media.get("unavailable", ""))


func abort_for_harness() -> void:
	if not Engine.is_editor_hint():
		_aborted = true


func _ready() -> void:
	_stage = get_node("Stage")
	_video_surface = get_node("Stage/Video")
	_splash_fade = get_node("Stage/SplashFade")
	_splash_surface = get_node("Stage/SplashFade/Splash")
	_authored_voice = get_node("RetailFmvVoice")
	resized.connect(_fit_stage)
	_fit_stage()
	if Engine.is_editor_hint():
		set_process(false)
		set_process_input(false)
		_show_editor_still()
		return
	if not _initialized:
		# F6 on this authored component cannot start a game or admit private
		# media. The host must supply the verified batch before adding it.
		set_process(false)
		set_process_input(false)
		push_warning("Initialize the startup scene with verified media before adding it to the tree.")
		return
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	z_index = 200
	if _schedule.is_empty():
		if not get_media_unavailable_reason().is_empty():
			push_warning("Startup media unavailable, so splash and intro FMV are absent: " + get_media_unavailable_reason())
		_finish()
		return
	if _clock == Clock.WALL and not _media.audio.is_empty():
		_voice = _authored_voice
	_present(_schedule.sample(_elapsed_seconds).value)


func _process(delta: float) -> void:
	if Engine.is_editor_hint() or not _initialized or _completed:
		return
	# Math.Max(0d, delta) preserves NaN and selects positive zero.
	var step: float = delta
	if step <= 0.0:
		step = 0.0
	_elapsed_seconds += 1.0 / 60.0 if _clock == Clock.FIXED_TICK else step
	if _aborted or _elapsed_seconds >= _schedule.get_total_seconds():
		_finish()
		return
	var frame: Dictionary = _schedule.sample(_elapsed_seconds).value
	# Start audio before the corresponding video is presented, exactly once
	# per cue, with the original float32 beat-local seek.
	_update_voice_track(frame)
	_present(frame)


func _input(event: InputEvent) -> void:
	if Engine.is_editor_hint() or not _initialized or _completed:
		return
	if not accepts_skip_event(event):
		return
	_aborted = true
	get_viewport().set_input_as_handled()


## CFMV::ReceiveButtonAction 0x004656E0 and backend latches 0x0053F2EB;
## same four default DIK rows and three mouse buttons as RetailFmvSkip.cs.
## Use logical keycode, not physical_keycode. Key echo, releases and pad input
## do not abort; one accepted event skips the entire remaining sequence.
static func accepts_skip_event(event: InputEvent) -> bool:
	if event is InputEventMouseButton:
		return event.pressed and event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_MIDDLE, MOUSE_BUTTON_RIGHT]
	if event is InputEventKey:
		return event.pressed and not event.echo and event.keycode in [KEY_SPACE, KEY_ENTER, KEY_ESCAPE, KEY_KP_ENTER]
	return false


func _exit_tree() -> void:
	_stop_voice_track()


func _fit_stage() -> void:
	if _stage == null:
		return
	# C# stored each arithmetic stage as float32; the layout is still the
	# native authored surface, with only its common letterbox transform here.
	var scale_value: float = minf(F32.value(size.x / 640.0), F32.value(size.y / 480.0))
	_stage.position = Vector2(
		F32.value(F32.value(size.x - F32.value(640.0 * scale_value)) * 0.5),
		F32.value(F32.value(size.y - F32.value(480.0 * scale_value)) * 0.5))
	_stage.scale = Vector2(scale_value, scale_value)


func _present(frame: Dictionary) -> void:
	_video_surface.visible = false
	_splash_fade.visible = false
	if frame.kind == Schedule.FrameKind.SPLASH:
		_splash_surface.texture = _splash_texture
		_splash_fade.modulate = Color(1.0, 1.0, 1.0, frame.alpha)
		_splash_fade.visible = _splash_texture != null
	elif frame.kind == Schedule.FrameKind.VIDEO and frame.cue != null \
			and _ensure_frame_resident(int(frame.cue), int(frame.frame_index)):
		_video_surface.texture = _video_buffers[_presented_buffer]
		_video_surface.visible = true
	# Position, Size and self_modulate belong to the actual editable controls.


func _ensure_frame_resident(cue: int, frame_index: int) -> bool:
	if _resident_cue == cue and _resident_index == frame_index and _video_buffers[_presented_buffer] != null:
		return true
	if not _media.frame_paths.has(cue) or frame_index < 0 or frame_index >= _media.frame_paths[cue].size():
		push_warning("Startup media %d frame %d has no admitted path." % [cue, frame_index])
		return false
	var path: String = _media.frame_paths[cue][frame_index]
	var image := Image.new()
	if _load_png(image, path) != OK:
		push_warning("Startup media %d frame %d unreadable at %s." % [cue, frame_index, path])
		return false
	var target: int = ((frame_index % 2) + 2) % 2
	var buffer: ImageTexture = _video_buffers[target]
	if buffer == null or buffer.get_width() != image.get_width() or buffer.get_height() != image.get_height():
		_video_buffers[target] = ImageTexture.create_from_image(image)
	else:
		buffer.update(image)
	_presented_buffer = target
	_resident_cue = cue
	_resident_index = frame_index
	return true


func _update_voice_track(frame: Dictionary) -> void:
	if not is_instance_valid(_voice):
		return
	if frame.kind != Schedule.FrameKind.VIDEO or frame.cue == null or not _media.audio.has(frame.cue):
		_stop_voice_track()
		return
	var cue: int = frame.cue
	if _voice_cue == cue:
		return
	_stop_voice_track()
	var track: Dictionary = _media.audio[cue]
	var read: Dictionary = _read_media_bytes(track.path)
	if not read.ok:
		push_warning("Startup media %d audio track unreadable at %s." % [cue, track.path])
		return
	var wave: PackedByteArray = read.value
	if wave.size() <= 44:
		return
	# The verified provider admitted a canonical 44-byte-header PCM s16 WAV.
	# This reads its unchanged payload, without a second decoder/admission law.
	var stream := AudioStreamWAV.new()
	stream.format = AudioStreamWAV.FORMAT_16_BITS
	stream.mix_rate = track.sample_rate
	stream.stereo = int(track.channels) == 2
	stream.data = wave.slice(44)
	stream.loop_mode = AudioStreamWAV.LOOP_DISABLED
	_voice.stream = stream
	_voice.play(F32.value(frame.beat_seconds))
	_voice_started.call(_voice)
	_voice_cue = cue


func _stop_voice_track() -> void:
	_voice_cue = null
	if is_instance_valid(_voice):
		_voice.stop()
		_voice.stream = null


func _finish() -> void:
	if _completed:
		return
	_completed = true
	visible = false
	set_process(false)
	set_process_input(false)
	# Audio and frame residency end before the host gets completion, including
	# abort; the host may start gameplay audio synchronously in that callback.
	_stop_voice_track()
	_video_surface.texture = null
	_splash_surface.texture = null
	_video_buffers[0] = null
	_video_buffers[1] = null
	_splash_texture = null
	_resident_cue = -1
	_resident_index = -1
	completed.emit()


static func _load_image_texture(path: String) -> ImageTexture:
	var image := Image.new()
	if _load_png(image, path) != OK:
		push_warning("Startup splash unreadable at " + path)
		return null
	return ImageTexture.create_from_image(image)


static func _read_media_bytes(path: String) -> Dictionary:
	if OS.get_name() != "Windows" and path.contains("\\"):
		return MediaIndex.read_file_bytes_exact(path)
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(path)
	return {"ok": true, "value": bytes} if FileAccess.get_open_error() == OK \
		else _failure("Cannot read startup media bytes.")


static func _load_png(image: Image, path: String) -> Error:
	if OS.get_name() == "Windows" or not path.contains("\\"):
		return image.load(path)
	# The verifier admits literal Unix filenames. Godot's path loader replaces
	# backslashes with '/', so use its same PNG decoder on the exact bytes.
	var read: Dictionary = _read_media_bytes(path)
	return image.load_png_from_buffer(read.value) if read.ok else ERR_CANT_OPEN


static func _admit_batch_shape(batch: Dictionary) -> Dictionary:
	if batch.get("schema") != VERIFIED_BATCH_SCHEMA:
		return _failure("Startup playback requires a verified media batch.")
	for field: String in ["clips", "frame_paths", "audio"]:
		if typeof(batch.get(field)) != TYPE_DICTIONARY:
			return _failure("Missing startup batch dictionary: " + field)
	for field: String in ["splash_path", "unavailable"]:
		if typeof(batch.get(field)) != TYPE_STRING:
			return _failure("Missing startup batch string: " + field)
	var clips: Dictionary = batch.clips
	var paths: Dictionary = batch.frame_paths
	for cue: Variant in clips:
		if typeof(cue) != TYPE_INT or cue < -2147483648 or cue > 2147483647:
			return _failure("Startup batch cue must be int32.")
		var timing: Dictionary = Schedule.clip_timing(clips[cue])
		if not timing.ok:
			return timing
		if not paths.has(cue) or (typeof(paths[cue]) != TYPE_PACKED_STRING_ARRAY and typeof(paths[cue]) != TYPE_ARRAY):
			return _failure("Startup batch is missing admitted frame paths.")
		if paths[cue].size() != int(clips[cue].frame_count):
			return _failure("Startup batch frame count differs from its admitted paths.")
		for path: Variant in paths[cue]:
			if typeof(path) != TYPE_STRING or String(path).is_empty():
				return _failure("Startup frame path must be a nonempty string.")
	for cue: Variant in batch.audio:
		if not clips.has(cue) or typeof(batch.audio[cue]) != TYPE_DICTIONARY:
			return _failure("Startup audio must belong to an admitted clip.")
		var track: Dictionary = batch.audio[cue]
		if typeof(track.get("path")) != TYPE_STRING or String(track.path).is_empty() \
				or typeof(track.get("sample_rate")) != TYPE_INT or typeof(track.get("channels")) != TYPE_INT:
			return _failure("Startup audio batch is incomplete.")
	return {"ok": true, "value": batch.duplicate(true)}


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidOperationException", "error": message}


func _get_configuration_warnings() -> PackedStringArray:
	return PackedStringArray([_editor_problem]) if not _editor_problem.is_empty() else PackedStringArray()


func _show_editor_still() -> void:
	# Never initialize the schedule, voice, input or callbacks from the editor.
	_video_surface.visible = false
	_splash_fade.visible = false
	_video_surface.texture = null
	_splash_surface.texture = null
	_editor_problem = ""
	var selected: Dictionary = _editor_image_path()
	if not selected.ok:
		_editor_problem = selected.error
	else:
		var texture: ImageTexture = _load_image_texture(selected.value)
		if texture == null:
			_editor_problem = "The selected decoded startup image is unavailable."
		elif editor_cue == Schedule.Cue.SPLASH:
			_splash_surface.texture = texture
			_splash_fade.modulate = Color.WHITE
			_splash_fade.visible = true
		else:
			_video_surface.texture = texture
			_video_surface.visible = true
	update_configuration_warnings()


func _editor_image_path() -> Dictionary:
	var media_root: String = resolve_media_root(OS.get_cmdline_user_args())
	if media_root.strip_edges().is_empty():
		return _failure("Set BEA_LOCAL_LAB or ONSLAUGHT_STARTUP_MEDIA to inspect decoded startup media.")
	var manifest_path: String = media_root.path_join("startup-media.json")
	var text: String = FileAccess.get_file_as_string(manifest_path)
	if FileAccess.get_open_error() != OK:
		return _failure("The startup preview manifest is unreadable: " + manifest_path)
	var parser := JSON.new()
	if parser.parse(text) != OK or typeof(parser.data) != TYPE_DICTIONARY:
		return _failure("The startup preview manifest is malformed.")
	var manifest: Dictionary = parser.data
	if manifest.get("schema") != PREVIEW_MANIFEST_SCHEMA:
		return _failure("Startup media manifest has an unsupported schema.")
	if editor_cue < 0 or editor_cue >= CUE_NAMES.size():
		return _failure("Unknown startup preview cue.")
	var group: Variant = manifest.get("stills" if editor_cue == Schedule.Cue.SPLASH else "clips")
	if typeof(group) != TYPE_DICTIONARY or typeof(group.get(CUE_NAMES[editor_cue])) != TYPE_DICTIONARY:
		return _failure("The selected startup preview cue is unavailable.")
	var record: Dictionary = group[CUE_NAMES[editor_cue]]
	var raw_path: Variant = record.get("path" if editor_cue == Schedule.Cue.SPLASH else "framePathFormat")
	if typeof(raw_path) != TYPE_STRING:
		return _failure("The startup preview image path is missing.")
	var relative: String = raw_path
	if editor_cue != Schedule.Cue.SPLASH:
		if relative.count("{0:D5}") != 1:
			return _failure("Unsupported startup preview frame naming.")
		relative = relative.replace("{0:D5}", "00001")
	# Preview is deliberately a smaller read-only operation than movie
	# admission, but its selected image must remain inside the selected cache.
	if relative.is_absolute_path() or relative.contains("\\") or relative.contains("{") or relative.contains("}"):
		return _failure("Startup image routing must stay inside its selected media cache.")
	var directory: String = ProjectSettings.globalize_path(media_root).simplify_path().trim_suffix("/") + "/"
	var path: String = directory.path_join(relative).simplify_path()
	if not path.begins_with(directory):
		return _failure("Startup image routing must stay inside its selected media cache.")
	return {"ok": true, "value": path}


static func resolve_media_root(arguments: PackedStringArray) -> String:
	for argument: String in arguments:
		if argument.begins_with("--startup-media="):
			return argument.substr("--startup-media=".length())
	var configured: String = OS.get_environment("ONSLAUGHT_STARTUP_MEDIA")
	if not configured.strip_edges().is_empty():
		return configured
	var canonical_lab: String = OS.get_environment("BEA_LOCAL_LAB")
	if not canonical_lab.strip_edges().is_empty():
		return canonical_lab.path_join("startup-media")
	var local: String = OS.get_environment("LOCALAPPDATA")
	return "" if local.strip_edges().is_empty() else local.path_join("OnslaughtToolkit/startup-media")
