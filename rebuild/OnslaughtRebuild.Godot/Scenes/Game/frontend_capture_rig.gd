# SPDX-License-Identifier: GPL-3.0-or-later
extends Node
## Deterministic screenshot capture for the bounded released frontend path and
## the Level 100 opening gameplay timeline, so parity claims cite pixels rather
## than code paths. Presentation-layer only: it reads back the viewport, writes
## PNGs and follows the engine frame clock, none of which Core may touch.
##
## Launch with --fixed-fps so one _process call is one logical frame; shots are
## keyed to frame ordinals, never wall-clock time, so a plan yields identical
## framing across runs on one build. Retail references are 640x480 (the released
## frontend composes at 4:3); the rig records the size it saw so a mismatched
## run cannot be compared silently.
##
## Plans: startup (13 frontend shots at absolute frames), gameplay (the Level 100
## timeline at the level offsets of local-lab/retail-reference-pristine/
## level100-gameplay/), mainmenu (a dense FEP_MAIN sweep) and options.

signal completed

const Frontend = preload("res://Client/frontend_session.gd")
const LaunchOptions = preload("res://Client/launch_options.gd")

## CD3DApplication__Init seeds 640x480; every retail reference capture is 640x480.
const NATIVE_WIDTH: int = 640
const NATIVE_HEIGHT: int = 480
## The --fixed-fps value the capture scripts use: one _process is 1/60 s.
const CAPTURE_FRAMES_PER_SECOND: int = 60
## The reconstruction's opening pan (6 * 30 ticks at 30 Hz); a label, not a schedule.
const OPENING_PAN_MS: int = 6_000
## 60 fps * 20 s; the scripted traversal reaches gameplay near frame 490.
const GAMEPLAY_ARM_DEADLINE_FRAME: int = 1_200
## The confirm at frame 128 is applied after the frontend's own _process, so
## FEP_MAIN is first drawn on the following frame.
const MAIN_MENU_ENTRY_FRAME: int = 129
## Every third engine frame: 20 Hz against the underlay's 30 fps video.
const MAIN_MENU_SWEEP_STRIDE: int = 3
## 129 + 8 s at 60 fps covers the 7,027 ms retail burst with margin.
const MAIN_MENU_SWEEP_LAST_FRAME: int = 129 + 480
## Retail simulation facts recorded in the gameplay manifest.
const SIMULATION_TICKS_PER_SECOND: int = 20
const RETAIL_BASE_TICKS_PER_SECOND: int = 20

const STARTUP_PLAN: Array = [
	[12, "01-click-early", Frontend.Screen.CLICK_TO_START],
	[120, "02-click-settled", Frontend.Screen.CLICK_TO_START],
	[132, "03-main-menu-entry", Frontend.Screen.MAIN_MENU],
	[240, "04-main-menu-settled", Frontend.Screen.MAIN_MENU],
	[252, "05-dev-select-entry", Frontend.Screen.DEV_SELECT],
	[300, "06-dev-select-settled", Frontend.Screen.DEV_SELECT],
	[312, "07-level-select", Frontend.Screen.LEVEL_SELECT],
	[360, "08-level-select-settled", Frontend.Screen.LEVEL_SELECT],
	# SELECT LEVEL leads to MISSION BRIEFING and SELECT CONFIGURATION before
	# loading; each has a pristine 640x480 reference frame from 2026-07-25.
	[372, "09-mission-briefing-entry", Frontend.Screen.MISSION_BRIEFING],
	[420, "10-mission-briefing-settled", Frontend.Screen.MISSION_BRIEFING],
	[432, "11-select-configuration-entry", Frontend.Screen.SELECT_CONFIGURATION],
	[480, "12-select-configuration-settled", Frontend.Screen.SELECT_CONFIGURATION],
	# Loading is short-lived: sample the frame immediately after the confirm.
	[489, "13-loading-handoff", Frontend.Screen.LOADING],
]

## FEP_OPTIONS and its three subpages, one settled shot each, compared with
## local-lab/retail-captures-options-pause-2026-07-27/. The last shot asserts
## that two Backs from the Video subpage land on FEP_MAIN.
const OPTIONS_PLAN: Array = [
	[220, "fep-options-root", Frontend.Screen.OPTIONS],
	[280, "fep-options-controller", Frontend.Screen.OPTIONS],
	[400, "fep-options-sound", Frontend.Screen.OPTIONS],
	[520, "fep-options-video", Frontend.Screen.OPTIONS],
	[600, "fep-options-exit-to-main", Frontend.Screen.MAIN_MENU],
]

const OPTIONS_STEPS: Array = [
	[128, "confirm"], [200, "main-select=5"], [204, "confirm"],
	[240, "options-select=0"], [244, "options-confirm"], [320, "options-back"],
	[360, "options-select=1"], [364, "options-confirm"], [440, "options-back"],
	[480, "options-select=2"], [484, "options-confirm"], [560, "options-back"],
	[580, "options-back"],
]

const STARTUP_STEPS: Array = [
	[128, "confirm"], # click-to-start -> main menu
	[248, "confirm"], # New Game -> FEP_DEVSELECT
	[308, "confirm"], # CHOOSE GAME NAME -> level select
	[368, "confirm"], # Level 100 -> mission briefing
	[428, "confirm"], # mission briefing -> select configuration
	[488, "confirm"], # select configuration -> loading
]

const SCREEN_NAMES: Array[String] = ["ClickToStart", "MainMenu", "QuitConfirm", "DevSelect", "Options",
	"Debriefing", "LevelSelect", "MissionBriefing", "SelectConfiguration", "Loading", "IntroCutscene", "Gameplay"]

var _frontend: Control
var _output_directory: String = ""
var _plan_name: String = ""
var _capture_width: int = NATIVE_WIDTH
var _capture_height: int = NATIVE_HEIGHT
var _requested_offsets_ms: Array[int] = []
var _shots: Array[Dictionary] = []
var _steps: Array[Dictionary] = []
var _written: Array[Dictionary] = []
var _frame: int = -1
var _shot_cursor: int = 0
var _step_cursor: int = 0
var _pending_label: Variant = null
var _finished: bool = false
var _planned_shots: int = 0
var _gameplay_zero_frame: Variant = null
var _boundary: Variant = null
var _dropped_offsets_ms: Array[int] = []
var _connected: bool = false


## Returns {ok, value: rig or null}. Capture mode starts only with --capture-dir.
static func try_create(arguments: PackedStringArray, frontend: Control) -> Dictionary:
	var directory: String = ""
	var plan: String = "startup"
	var width: int = NATIVE_WIDTH
	var height: int = NATIVE_HEIGHT
	var offsets: Array[int] = []
	for argument: String in arguments:
		if argument.begins_with("--capture-dir="):
			directory = argument.substr("--capture-dir=".length())
		elif argument.begins_with("--capture-plan="):
			plan = argument.substr("--capture-plan=".length())
		elif argument.begins_with("--capture-offsets-ms="):
			# Sample at retail's realised offsets instead of the nominal grid.
			var parsed: Array[int] = []
			for raw: String in argument.substr("--capture-offsets-ms=".length()).split(",", false):
				var token: String = raw.strip_edges()
				if token.is_empty():
					continue
				if not token.is_valid_int() or int(token) < 0:
					return _argument("Malformed --capture-offsets-ms entry '%s'. Expected non-negative whole milliseconds." % token)
				parsed.append(int(token))
			parsed.sort()
			offsets = []
			for value: int in parsed:
				if offsets.is_empty() or offsets[-1] != value:
					offsets.append(value)
			if offsets.is_empty():
				return _argument("--capture-offsets-ms listed no offsets.")
		elif argument.begins_with("--capture-size="):
			var parts: PackedStringArray = argument.substr("--capture-size=".length()).split("x")
			if parts.size() != 2 or not parts[0].is_valid_int() or not parts[1].is_valid_int() \
					or int(parts[0]) <= 0 or int(parts[1]) <= 0:
				return _argument("Malformed --capture-size in '%s'. Expected WIDTHxHEIGHT, e.g. 640x480." % argument)
			width = int(parts[0])
			height = int(parts[1])
	if directory.strip_edges().is_empty():
		return {"ok": true, "value": null}
	if not LaunchOptions.is_fully_qualified(directory):
		return _argument("Capture mode requires an absolute --capture-dir path.")
	if plan not in ["startup", "gameplay", "mainmenu", "options"]:
		return _argument("Unknown capture plan '%s'. Known plans: startup, gameplay, mainmenu, options." % plan)
	var rig: Node = (load("res://Scenes/Game/frontend_capture_rig.gd") as GDScript).new()
	rig.name = "FrontendCaptureRig"
	rig._frontend = frontend
	rig._output_directory = directory
	rig._plan_name = plan
	rig._capture_width = width
	rig._capture_height = height
	rig._requested_offsets_ms = offsets
	return {"ok": true, "value": rig}


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(_output_directory)
	_apply_native_capture_viewport()
	if _plan_name == "gameplay":
		# Shots are relative to t0, the first drawn gameplay frame, which is
		# observed rather than predicted; only the traversal is scheduled now.
		_planned_shots = _gameplay_offsets_ms().size()
	elif _plan_name == "mainmenu":
		# A dense sweep: the underlay is a 30 fps video, so the phase must be
		# measured (best-matching sweep frame per retail frame), not assumed.
		# Labels are milliseconds after FEP_MAIN is first drawn.
		var frame: int = MAIN_MENU_ENTRY_FRAME
		while frame <= MAIN_MENU_SWEEP_LAST_FRAME:
			var offset_ms: int = int(roundf((frame - MAIN_MENU_ENTRY_FRAME) * 1000.0 / 60.0))
			_shots.append(_shot(frame, "mainmenu-t%06dms" % offset_ms, Frontend.Screen.MAIN_MENU, null, null))
			frame += MAIN_MENU_SWEEP_STRIDE
		_planned_shots = _shots.size()
	elif _plan_name == "options":
		# Keep the custom cursor outside every scored ink band so the live mouse
		# cannot become a nondeterministic input.
		_report(_frontend.set_mouse_cursor_design_position_for_capture(Vector2.ZERO))
		for row: Array in OPTIONS_PLAN:
			_shots.append(_shot(row[0], row[1], row[2], null, null))
		_planned_shots = _shots.size()
	else:
		for row: Array in STARTUP_PLAN:
			_shots.append(_shot(row[0], row[1], row[2], null, null))
		_planned_shots = _shots.size()
	# The gameplay plan reuses the proven startup traversal; mainmenu takes only
	# the first confirm so it stays on FEP_MAIN for the whole sweep.
	for row: Array in (OPTIONS_STEPS if _plan_name == "options" else STARTUP_STEPS):
		if _plan_name == "mainmenu" and row[0] > STARTUP_STEPS[0][0]:
			break
		_steps.append({"frame": row[0], "action": row[1]})
	_shots.sort_custom(func(left: Dictionary, right: Dictionary) -> bool: return left.frame < right.frame)
	_steps.sort_custom(func(left: Dictionary, right: Dictionary) -> bool: return left.frame < right.frame)
	# frame_post_draw fires after rasterization, the only point at which viewport
	# readback returns the frame _process just staged. A bound method, released
	# at exit: never a lambda on a RenderingServer frame signal.
	RenderingServer.frame_post_draw.connect(_on_frame_post_draw)
	_connected = true


func _exit_tree() -> void:
	if _connected:
		RenderingServer.frame_post_draw.disconnect(_on_frame_post_draw)
		_connected = false


## Forces a 1:1 native composition for the capture run only; the shipped window
## contract in project.godot is unchanged. At exactly 640x480 the frontend's
## letterbox scale is 1.0, so every drawn pixel maps to one output pixel.
func _apply_native_capture_viewport() -> void:
	var window: Window = get_window()
	window.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	window.content_scale_aspect = Window.CONTENT_SCALE_ASPECT_IGNORE
	window.size = Vector2i(_capture_width, _capture_height)


func _process(_delta: float) -> void:
	if _finished:
		return
	_frame += 1
	while _step_cursor < _steps.size() and _steps[_step_cursor].frame == _frame:
		_apply_action(_steps[_step_cursor].action)
		_step_cursor += 1
	if _plan_name == "gameplay" and _gameplay_zero_frame == null:
		_arm_gameplay_timeline()
		if _finished:
			return
	if _shot_cursor < _shots.size() and _shots[_shot_cursor].frame == _frame:
		_pending_label = _shots[_shot_cursor].label


## t0 is the first drawn frame on which the frontend has left Loading: the flow
## hides itself and hands off to gameplay in the same _process, and this rig
## processes after it, so this is the first frame that rasterizes the level.
func _arm_gameplay_timeline() -> void:
	var screen: int = _frontend.host_snapshot().screen
	if screen != Frontend.Screen.GAMEPLAY:
		if _frame >= GAMEPLAY_ARM_DEADLINE_FRAME:
			_finish_with_boundary("The frontend never reached Gameplay. It was on %s at frame %d (deadline %d). No in-level frame was captured."
				% [SCREEN_NAMES[screen], _frame, GAMEPLAY_ARM_DEADLINE_FRAME])
		return
	_gameplay_zero_frame = _frame
	var last_frame: int = -2147483648
	for offset_ms: int in _gameplay_offsets_ms():
		var frame: int = _frame + frame_for_offset_ms(offset_ms)
		if frame == last_frame:
			# Two offsets within one engine frame are the same frame; drop and
			# report the duplicate instead of presenting one frame as two samples.
			_dropped_offsets_ms.append(offset_ms)
			continue
		last_frame = frame
		_shots.append(_shot(frame, "level100-t%06dms" % offset_ms, Frontend.Screen.GAMEPLAY, offset_ms,
			"opening-pan" if offset_ms < OPENING_PAN_MS else "settled-playing-camera"))
	_shots.sort_custom(func(left: Dictionary, right: Dictionary) -> bool: return left.frame < right.frame)
	_planned_shots = _shots.size()


## Nominal retail offsets: opening-pan-run1 0..16000 ms every 250 ms and
## hud-timeline-run1 17000..42000 ms every 1000 ms (91 samples), unless the
## caller supplied retail's realised offsets.
func _gameplay_offsets_ms() -> Array[int]:
	if not _requested_offsets_ms.is_empty():
		return _requested_offsets_ms
	var offsets: Array[int] = []
	for offset: int in range(0, 16_001, 250):
		offsets.append(offset)
	for offset: int in range(17_000, 42_001, 1_000):
		offsets.append(offset)
	return offsets


## frame = round(offset_ms * 60 / 1000); exact for every multiple of 250 ms, and
## an arbitrary millisecond rounds to the nearest engine frame (at most 8.34 ms).
@warning_ignore("integer_division")
static func frame_for_offset_ms(offset_ms: int) -> int:
	return (offset_ms * CAPTURE_FRAMES_PER_SECOND + 500) / 1_000


func _apply_action(action: String) -> void:
	match action:
		"confirm":
			_report(_frontend.confirm())
		"options-confirm":
			_report(_frontend.confirm_options())
		"options-back":
			_report(_frontend.back_from_options())
		_:
			if action.begins_with("main-select="):
				_report(_frontend.select_main_index(int(action.substr("main-select=".length()))))
			elif action.begins_with("options-select="):
				_report(_frontend.select_options_row(int(action.substr("options-select=".length()))))
			else:
				push_error("Unknown capture action '%s'." % action)


func _on_frame_post_draw() -> void:
	if _pending_label == null:
		return
	var label: String = _pending_label
	_pending_label = null
	var shot: Dictionary = _shots[_shot_cursor]
	_shot_cursor += 1
	var image: Image = get_viewport().get_texture().get_image()
	var path: String = _output_directory.path_join(label + ".png")
	var error: Error = image.save_png(path)
	var actual: int = _frontend.host_snapshot().screen
	var record: Dictionary = {"label": label, "frame": shot.frame, "path": path,
		"width": image.get_width(), "height": image.get_height(),
		"expectedScreen": null if shot.expect_screen == null else SCREEN_NAMES[shot.expect_screen],
		"actualScreen": SCREEN_NAMES[actual],
		# A shot on the wrong screen is not evidence; record the disagreement.
		"screenMatched": shot.expect_screen == null or shot.expect_screen == actual,
		"saveError": null if error == OK else error_string(error)}
	if shot.level_offset_ms != null:
		# Mirrors local-lab/retail-reference-pristine/level100-gameplay/manifest.json.
		var offset_ms: int = shot.level_offset_ms
		record["file"] = label + ".png"
		record["levelOffsetMs"] = offset_ms
		record["phase"] = shot.phase
		record["widthxheight"] = "%dx%d" % [image.get_width(), image.get_height()]
		record["simulationTick"] = offset_ms * 2 / 100.0
		record["engineFrameFromZero"] = frame_for_offset_ms(offset_ms)
		record["meanRGB"] = _mean_rgb(image, error)
		record["sha256"] = FileAccess.get_sha256(path) if error == OK else null
	_written.append(record)
	if _shot_cursor >= _shots.size():
		_finished = true
		_write_manifest()
		completed.emit()


## Whole-frame mean RGB, computed after the PNG is written on a converted copy.
static func _mean_rgb(image: Image, save_error: Error) -> Variant:
	if save_error != OK:
		return null
	image.convert(Image.FORMAT_RGB8)
	var data: PackedByteArray = image.get_data()
	@warning_ignore("integer_division")
	var pixels: int = data.size() / 3
	if pixels == 0:
		return null
	var sums: Array[int] = [0, 0, 0]
	var index: int = 0
	while index + 2 < data.size():
		sums[0] += data[index]
		sums[1] += data[index + 1]
		sums[2] += data[index + 2]
		index += 3
	return [_round_tenths_even(float(sums[0]) / pixels), _round_tenths_even(float(sums[1]) / pixels),
		_round_tenths_even(float(sums[2]) / pixels)]


## .NET Math.Round(value, 1): scale, round half to even, unscale.
static func _round_tenths_even(value: float) -> float:
	var scaled: float = value * 10.0
	var lower: float = floorf(scaled)
	var fraction: float = scaled - lower
	var rounded: float = lower + 1.0 if fraction > 0.5 else lower
	if fraction == 0.5 and fmod(lower, 2.0) != 0.0:
		rounded = lower + 1.0
	return rounded / 10.0


## Ends the run early and records why; a missing frame is never invented.
func _finish_with_boundary(reason: String) -> void:
	_boundary = reason
	_finished = true
	_pending_label = null
	_write_manifest()
	completed.emit()


func _write_manifest() -> void:
	var size: Vector2 = get_viewport().get_visible_rect().size
	var manifest: Dictionary = {"schema": "onslaught-frontend-capture.v2", "plan": _plan_name,
		"engineVersion": Engine.get_version_info().string, "viewportWidth": size.x, "viewportHeight": size.y,
		"retailReferenceSize": "640x480", "plannedShots": _planned_shots, "capturedShots": _written.size(),
		"boundary": _boundary, "shots": _written}
	if _plan_name == "gameplay":
		manifest["captureFramesPerSecond"] = CAPTURE_FRAMES_PER_SECOND
		manifest["simulationTicksPerSecond"] = SIMULATION_TICKS_PER_SECOND
		manifest["retailBaseTicksPerSecond"] = RETAIL_BASE_TICKS_PER_SECOND
		manifest["openingPanMs"] = OPENING_PAN_MS
		manifest["gameplayZeroFrame"] = _gameplay_zero_frame
		manifest["offsetSource"] = "nominal-grid" if _requested_offsets_ms.is_empty() else "--capture-offsets-ms"
		manifest["droppedOffsetsMs"] = _dropped_offsets_ms
		manifest["t0Definition"] = "first drawn frame on which RetailFrontendFlow has left Loading " \
			+ "(structural equivalent of retail's 'first client frame whose mean " \
			+ "left the loading signature 107,115,125')"
		manifest["referenceSet"] = "local-lab/retail-reference-pristine/level100-gameplay/manifest.json"
	var file := FileAccess.open(_output_directory.path_join("capture-manifest.json"), FileAccess.WRITE)
	if file == null:
		push_error("Could not write the capture manifest: " + error_string(FileAccess.get_open_error()))
		return
	file.store_string(JSON.stringify(manifest, "  ", false))
	file.close()


static func _shot(frame: int, label: String, expect_screen: Variant, level_offset_ms: Variant, phase: Variant) -> Dictionary:
	return {"frame": frame, "label": label, "expect_screen": expect_screen, "level_offset_ms": level_offset_ms, "phase": phase}


static func _report(result: Dictionary) -> void:
	if not result.ok:
		push_error("Capture action failed: %s: %s" % [result.get("error_type", "Error"), result.get("error", "")])


static func _argument(message: String) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException", "error": message}
