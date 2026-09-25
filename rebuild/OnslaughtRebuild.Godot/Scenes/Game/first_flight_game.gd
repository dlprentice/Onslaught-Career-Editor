# SPDX-License-Identifier: GPL-3.0-or-later
extends Node3D
## The First Flight host: the root of Main.tscn. It owns the Level 100 session
## lifecycle, frontend handoffs, device input, the authentic pause menu, the
## cursor policy, startup and attract media, smoke and capture runs and quit.
## The simulation itself stays in the C# Core behind Bridge/SimulationBridge.cs;
## real-time input adaptation lives in Client/interactive_session.gd.
##
## Every native owner returns {ok, ...} results. A failed step ends the current
## engine callback with an error, the way the former C# exception did.

signal frontend_audio_cue_requested(cue: int)

const InteractiveSession = preload("res://Client/interactive_session.gd")
const InteractiveInput = preload("res://Client/interactive_input.gd")
const PlatformInput = preload("res://Client/platform_input_edges.gd")
const PauseModel = preload("res://Client/pause_menu.gd")
const Frontend = preload("res://Client/frontend_session.gd")
const Schedule = preload("res://Client/startup_schedule.gd")
const Click = preload("res://Client/click_to_start_laws.gd")
const HudCatalog = preload("res://Client/hud_catalog.gd")
const LaunchOptions = preload("res://Client/launch_options.gd")
const SmokeScenario = preload("res://Client/smoke_scenario.gd")
const CareerSelections = preload("res://Client/career_selections.gd")
const Startup = preload("res://Scenes/Frontend/startup_sequence.gd")
const CaptureRig = preload("res://Scenes/Game/frontend_capture_rig.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")

const SIMULATION_SEED: int = 0x4F4E534C
const SMOKE_FRAME_ELAPSED_TICKS: int = 500_000
const DOTNET_TICKS_PER_SECOND: float = 10_000_000.0
## Input.get_axis is binary32; the dead zone is the binary32 0.01f.
const AXIS_DEAD_ZONE: float = 0.009999999776482582
const BRIDGE_SCRIPT_PATH: String = "res://Bridge/SimulationBridge.cs"
const MANIFEST_PATH: String = "res://Assets/Level100/StaticWorld/level100-static-world.json"
const MANIFEST_MAXIMUM_BYTES: int = 512_000
const WORLD_SCENE_PATH: String = "res://Assets/Level100/Scenes/Level100.tscn"
const AUDIO_SCENE_PATH: String = "res://Scenes/Audio/Level100Audio.tscn"
const HUD_SCENE_PATH: String = "res://Scenes/Hud/FirstFlightHud.tscn"
const PAUSE_SCENE_PATH: String = "res://Scenes/Pause/PauseMenu.tscn"
const STARTUP_SCENE_PATH: String = "res://Scenes/Frontend/Startup.tscn"

const MOVE_FORWARD: StringName = &"first_flight_move_forward"
const MOVE_BACKWARD: StringName = &"first_flight_move_backward"
const MOVE_LEFT: StringName = &"first_flight_move_left"
const MOVE_RIGHT: StringName = &"first_flight_move_right"
const LOOK_LEFT: StringName = &"first_flight_look_left"
const LOOK_RIGHT: StringName = &"first_flight_look_right"
const LOOK_UP: StringName = &"first_flight_look_up"
const LOOK_DOWN: StringName = &"first_flight_look_down"
const FIRE: StringName = &"first_flight_fire"
const TOGGLE_MODE: StringName = &"first_flight_toggle_mode"
const LANDING_JETS: StringName = &"first_flight_landing_jets"
const RESET: StringName = &"first_flight_reset"
const ALL_ACTIONS: Array[StringName] = [MOVE_FORWARD, MOVE_BACKWARD, MOVE_LEFT, MOVE_RIGHT, LOOK_LEFT,
	LOOK_RIGHT, LOOK_UP, LOOK_DOWN, FIRE, TOGGLE_MODE, LANDING_JETS, RESET]

const SCREEN_NAMES: Array[String] = ["ClickToStart", "MainMenu", "QuitConfirm", "DevSelect", "Options",
	"Debriefing", "LevelSelect", "MissionBriefing", "SelectConfiguration", "Loading", "IntroCutscene", "Gameplay"]
const CURSOR_NAMES: Array[String] = ["Custom", "Visible", "Hidden", "Captured"]
const AUDIO_CUE_NAMES: Array[String] = ["Move", "Select", "Back"]

enum SmokePhase { COLD_FRONTEND, INITIAL_GAMEPLAY, AWAITING_RETRY_GAMEPLAY, RETRY_GAMEPLAY, RETURNED_TO_MAIN_MENU }


## Weak references to every audio playback start, including tracks replaced just
## before quit, so quit can wait for the mixer to release them. They neither own
## the playback nor change its audible lifetime.
class PlaybackRetirement extends RefCounted:
	var _pending: Array[WeakRef] = []

	func observe(player: Node) -> void:
		if (player is AudioStreamPlayer or player is AudioStreamPlayer3D) and player.has_stream_playback():
			pending_count()
			_pending.append(weakref(player.get_stream_playback()))

	func pending_count() -> int:
		for index: int in range(_pending.size() - 1, -1, -1):
			if _pending[index].get_ref() == null:
				_pending.remove_at(index)
		return _pending.size()

	func dispose() -> void:
		_pending.clear()


var _session: RefCounted = null
var _bridge: RefCounted = null
var _platform_input: RefCounted = null
var _pause_menu: RefCounted = PauseModel.new()
var _audio_retirement := PlaybackRetirement.new()
var _quit_exit_code: Variant = null
var _audio_shutdown_deadline_ms: int = 0
var _audio: Node3D = null
var _world: Node3D = null
var _hud: CanvasLayer = null
var _hud_info: Dictionary = {}
var _hud_delivered_ids: Array[int] = []
var _pause_view: CanvasLayer = null
var _hud_text_catalog: Dictionary = {}
var _frontend: Control = null
var _frontend_initialization_error: Dictionary = {}
var _career_descriptors: Array[Dictionary] = []
var _selected_career: Variant = null
var _frame_events: Dictionary = {}
var _level100_world_created: bool = false
var _gameplay_active: bool = false
var _pause_exit_audio_completed: bool = false
var _smoke_mode: bool = false
var _capture_mode: bool = false
var _capture_arguments_present: bool = false
var _skip_startup_media: bool = false
var _force_startup_media: bool = false
var _startup_sequence: Control = null
var _click_to_start_page_seconds: float = 0.0
var _smoke_completing: bool = false
var _window_has_focus: bool = false
var _focus_loss_handler_input_cleared: bool = false
var _focus_loss_handler_neutral_rearmed: bool = false
var _smoke_saw_click_to_start: bool = false
var _smoke_saw_main_menu: bool = false
var _smoke_saw_dev_select: bool = false
var _smoke_saw_level_select: bool = false
var _smoke_saw_mission_briefing: bool = false
var _smoke_saw_select_configuration: bool = false
var _smoke_saw_loading: bool = false
var _smoke_saw_gameplay: bool = false
var _smoke_cursor_custom_at_frontend: bool = false
var _smoke_cursor_hidden_at_loading: bool = false
var _smoke_cursor_policy_applied_at_gameplay: bool = false
var _smoke_window_focused_at_gameplay: bool = false
var _smoke_gameplay_cursor_policy: Array[String] = []
var _smoke_audio_queued_speaker_ids: Array[int] = []
var _smoke_audio_queued_message_ids: Array[int] = []
var _smoke_voice_started_message_ids: Array[int] = []
var _smoke_voice_last_observed_message_id: Variant = null
var _smoke_voice_playback_consistent: bool = true
var _smoke_cursor_released_on_focus_loss: bool = false
var _smoke_cursor_recaptured_on_focus_gain: bool = false
var _smoke_retry_requested: bool = false
var _smoke_retry_gameplay_activated: bool = false
var _smoke_retry_session_fresh: bool = false
var _smoke_return_requested: bool = false
var _smoke_returned_to_main_menu: bool = false
var _smoke_world_released_at_main_menu: bool = false
var _smoke_cursor_custom_at_main_menu: bool = false
var _smoke_report_path: String = ""
## Explicit --record-tape=<path> only; recording happens only when the operator
## names a destination. "" means no request, or the request was fulfilled.
var _record_tape_path: String = ""
var _tape_recording: bool = false
var _requested_cursor_mode: int = Frontend.CursorMode.CUSTOM
var _smoke_phase: int = SmokePhase.COLD_FRONTEND
var _smoke_report: Dictionary = {}


func _enter_tree() -> void:
	# The production frontend is authored in Main.tscn. Initialize its data
	# before its own _ready, without moving gameplay into an editor tool.
	_frontend = get_node("RetailStartupFrontend")
	_frontend.set_effect_handler(_dispatch_frontend_effect)
	_frontend.set_voice_observer(_observe_playback)
	var selections: Dictionary = CareerSelections.read_explicit_selections(OS.get_cmdline_user_args())
	if not selections.ok:
		_frontend_initialization_error = selections
		return
	_career_descriptors = selections.value
	var initialized: Dictionary = _frontend.initialize(_career_descriptors)
	if not initialized.ok:
		_frontend_initialization_error = initialized


func _ready() -> void:
	get_tree().auto_accept_quit = false
	var started: Dictionary = _initialize_host()
	if not started.ok:
		set_process(false)
		push_error("Level 100 opening slice failed to initialize: " + String(started.get("error", "")))
		_request_quit(4)


func _initialize_host() -> Dictionary:
	if not _frontend_initialization_error.is_empty():
		return _frontend_initialization_error
	_configure_input_map()
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	var options: Dictionary = LaunchOptions.parse(arguments)
	if not options.ok:
		return options
	_smoke_mode = options.value.smoke
	_smoke_report_path = options.value.report_path
	_capture_arguments_present = options.value.capture_arguments_present
	_skip_startup_media = options.value.skip_startup_media
	_force_startup_media = options.value.force_startup_media
	_record_tape_path = options.value.record_tape_path
	var window: Window = get_window()
	window.title = "Onslaught Rebuild - Battle Engine Aquila"
	_window_has_focus = window.has_focus()
	_audio = (load(AUDIO_SCENE_PATH) as PackedScene).instantiate()
	_audio.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(_audio)
	var configured: Dictionary = _audio.configure(_observe_playback)
	if not configured.ok:
		return configured
	var catalog: Dictionary = HudCatalog.load_verified_text_batch()
	if not catalog.ok:
		return catalog
	_hud_text_catalog = catalog.value
	_apply_frontend_cursor_mode(Frontend.CursorMode.CUSTOM)
	var rig: Dictionary = CaptureRig.try_create(arguments, _frontend)
	if not rig.ok:
		return rig
	if rig.value != null:
		# The gameplay capture plan holds the level for 42 s of engine time.
		# Suppress the OS cursor capture so the run cannot steal the operator's
		# pointer; the cursor is not in the viewport texture, so no captured
		# pixel changes, and the requested mode still tracks the released policy.
		_capture_mode = true
		rig.value.completed.connect(_on_capture_completed)
		add_child(rig.value)
	return _start_retail_startup_media()


## Pause integration seam: the frontend enters Loading and the host replaces its
## one Level 100 session and world when requested.
func restart_level100() -> Dictionary:
	var frontend: Dictionary = _require_level100_frontend()
	return _frontend.restart_level100() if frontend.ok else frontend


## Pause integration seam for Exit Level: returns to the frontend shell and
## never quits the application.
func leave_level100_for_main_menu() -> Dictionary:
	var frontend: Dictionary = _require_level100_frontend()
	return _frontend.leave_level100_for_main_menu() if frontend.ok else frontend


func selected_career() -> Variant:
	return _selected_career


func _process(delta: float) -> void:
	if _quit_exit_code != null:
		var pending: int = _audio_retirement.pending_count()
		if pending == 0:
			get_tree().quit(_quit_exit_code)
		elif Time.get_ticks_msec() >= _audio_shutdown_deadline_ms:
			push_error("Audio shutdown timed out with %d playback objects still alive." % pending)
			get_tree().quit(4 if _quit_exit_code == 0 else _quit_exit_code)
		return
	if _level100_world_created:
		_pause_view.advance_animation(delta)
	if _smoke_mode and not _gameplay_active:
		_report(_drive_smoke_frontend(), "First Flight smoke frontend")
		return
	if not _gameplay_active:
		_report(_advance_attract_idle(delta), "Attract restart")
		return
	if _smoke_mode and _smoke_phase == SmokePhase.RETRY_GAMEPLAY:
		_report(_finish_smoke_retry_and_return(), "First Flight smoke return")
		return
	if _smoke_completing:
		return
	if _session.is_paused():
		return
	_report(_advance_gameplay_frame(delta), "Level 100 frame")


func _advance_gameplay_frame(delta: float) -> Dictionary:
	if _smoke_mode:
		var tick: Dictionary = _bridge.GetTick()
		if not tick.ok:
			return tick
		var scripted: Dictionary = SmokeScenario.input_for_tick(tick.value)
		if not scripted.ok:
			return scripted
		_apply_synthetic_input(scripted.value)
	var observed: Dictionary = _session.observe_input(_sample_input())
	if not observed.ok:
		return observed
	var elapsed_ticks: int = SMOKE_FRAME_ELAPSED_TICKS if _smoke_mode \
		else maxi(0, int(roundf(delta * DOTNET_TICKS_PER_SECOND)))
	var advanced: Dictionary = _session.advance_frame_ticks(elapsed_ticks)
	if not advanced.ok:
		return advanced
	var consumed: Dictionary = _consume_frame_events()
	if not consumed.ok:
		return consumed
	var rendered: Dictionary = _world.RenderFromBridge(_bridge, advanced.value.interpolation_alpha, delta)
	if not rendered.ok:
		return rendered
	var hud: Dictionary = _update_hud()
	if not hud.ok:
		return hud
	_hud.visible = rendered.show_hud
	if not _smoke_mode:
		var handoff: Dictionary = _try_accept_won_frontend_handoff()
		if not handoff.ok:
			return handoff
	if _smoke_mode:
		_sample_smoke_voice_progress()
		var control: Dictionary = _bridge.ControlFacts()
		if not control.ok:
			return control
		if control.value.tick >= SmokeScenario.DURATION_TICKS:
			_smoke_completing = true
			var probe: Dictionary = _run_focus_loss_handler_smoke_probe()
			if not probe.ok:
				return probe
			var report: Dictionary = _capture_smoke_report()
			if not report.ok:
				return report
			_smoke_report = report.value
			var restarted: Dictionary = restart_level100()
			if not restarted.ok:
				return restarted
			_smoke_retry_requested = _frontend_screen() == Frontend.Screen.LOADING
			_smoke_cursor_hidden_at_loading = _smoke_cursor_hidden_at_loading \
				and _requested_cursor_mode == Frontend.CursorMode.HIDDEN
			_smoke_phase = SmokePhase.AWAITING_RETRY_GAMEPLAY
	return {"ok": true}


func _input(event: InputEvent) -> void:
	if _smoke_mode or not _gameplay_active:
		return
	_report(_handle_gameplay_input(event), "Level 100 input")


func _handle_gameplay_input(event: InputEvent) -> Dictionary:
	var observed: Dictionary = _observe_platform_input_event(event)
	if not observed.ok:
		return observed
	var authentic_pause_pressed: bool = false
	if event is InputEventKey and event.pressed and not event.echo and _is_key(event, KEY_ESCAPE):
		var consumed: Dictionary = _platform_input.consume_key_once(_platform_key_code(event))
		if not consumed.ok:
			return consumed
		authentic_pause_pressed = consumed.value != 0
	if not authentic_pause_pressed and event is InputEventJoypadButton and event.pressed \
			and event.button_index == JOY_BUTTON_START:
		var rising: Dictionary = _platform_input.is_joy_button_rising(event.device, event.button_index)
		if not rising.ok:
			return rising
		authentic_pause_pressed = rising.value
	if authentic_pause_pressed:
		var handled: Dictionary = {"ok": true}
		if _pause_menu.is_open():
			if _pause_view.input_ready:
				handled = _forward_frontend_audio_cue(Frontend.AudioCue.BACK)
				if handled.ok:
					handled = _handle_pause_action(_pause_menu.cancel())
				if handled.ok:
					handled = _refresh_pause_view()
		elif not _pause_view.is_closing:
			handled = _open_authentic_pause_menu()
		get_viewport().set_input_as_handled()
		return handled
	if _pause_menu.is_open():
		var pause_input: Dictionary = _handle_authentic_pause_input(event)
		if pause_input.ok and pause_input.value:
			get_viewport().set_input_as_handled()
		return pause_input
	if _session.is_paused():
		return {"ok": true}
	if event is InputEventMouseMotion:
		var control: Dictionary = _bridge.ControlFacts()
		if not control.ok:
			return control
		if control.value.transition_none:
			var delta_x: int = _to_milli_pixels(event.screen_relative.x)
			var delta_y: int = _to_milli_pixels(event.screen_relative.y)
			if delta_x != 0 or delta_y != 0:
				return _session.queue_pointer_motion_milli_pixels(delta_x, delta_y)
		return {"ok": true}
	if event is InputEventMouseButton and event.pressed:
		# The shipped PC binding row 12 primary slot is mouse code 2: the middle
		# button in the zero-based table whose codes 3/4 are the wheel below. Its
		# secondary keyboard slot, scan code 0x27 (Semicolon), is handled with
		# the key edges below.
		if event.button_index == MOUSE_BUTTON_MIDDLE:
			_session.queue_change_weapon()
			get_viewport().set_input_as_handled()
			return {"ok": true}
		if event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_session.queue_zoom_in()
			get_viewport().set_input_as_handled()
			return {"ok": true}
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_session.queue_zoom_out()
			get_viewport().set_input_as_handled()
			return {"ok": true}
	# The shipped controller table maps BUTTON_MECH_FIRE_GUN_POD as
	# BUTTON_RELEASE. Queue the falling edge so a press and release between two
	# fixed-step samples is not lost; the sampled levels derive the same edge
	# and the pending flag coalesces both paths.
	if event is InputEventKey and not event.pressed and not event.echo and _is_key(event, KEY_SPACE):
		_session.queue_fire_pulse()
		return {"ok": true}
	if not event is InputEventKey or not event.pressed or event.echo:
		return {"ok": true}
	var once: Dictionary = _platform_input.consume_key_once(_platform_key_code(event))
	if not once.ok or once.value == 0:
		return once
	var toggle_pressed: bool = event.is_action_pressed(TOGGLE_MODE) or _is_key(event, KEY_Q)
	var reset_pressed: bool = event.is_action_pressed(RESET) or _is_key(event, KEY_R)
	if _is_key(event, KEY_SEMICOLON):
		_session.queue_change_weapon()
	var pulses: Array[Dictionary] = []
	if _is_key(event, KEY_W) or _is_key(event, KEY_UP):
		pulses.append(_session.queue_movement_pulse(0, 1))
	if _is_key(event, KEY_S) or _is_key(event, KEY_DOWN):
		pulses.append(_session.queue_movement_pulse(0, -1))
	if _is_key(event, KEY_A) or _is_key(event, KEY_LEFT):
		pulses.append(_session.queue_movement_pulse(-1, 0))
	if _is_key(event, KEY_D) or _is_key(event, KEY_RIGHT):
		pulses.append(_session.queue_movement_pulse(1, 0))
	for pulse: Dictionary in pulses:
		if not pulse.ok:
			return pulse
	# BUTTON_SKIP_PANNING (0x3a): the shipped 47-row binding table
	# (OptionsEntries__InitDefaultSingleBindingsTable, 0x00514210) gives it four
	# hard-wired KEY_ONCE rows at indices 22-25, DIK 0x39/0x1c/0x01/0x9c: Space,
	# Enter, Escape, Numpad Enter. Escape is deliberately excluded: it is also
	# BUTTON_PAUSE (row 34), BUTTON_FRONTEND_MENU_BACK (17) and
	# BUTTON_SKIP_CUTSCENE (20), and which consumer a press reaches depends on
	# retail's consume-and-clear GetKeyOnce (references/Onslaught/ltshell.h:292;
	# retail 0x00515980). Binding-table order is unresolved, so the established
	# pause-first route consumes the byte above. Core ignores this action outside
	# the opening pan (references/Onslaught/Player.cpp:311).
	if _is_key(event, KEY_SPACE) or _is_key(event, KEY_ENTER) or _is_key(event, KEY_KP_ENTER):
		_session.queue_skip_panning()
	if toggle_pressed:
		_session.queue_toggle_mode()
	if reset_pressed:
		_session.queue_reset()
	return {"ok": true}


## Returns {ok, value: handled}.
func _handle_authentic_pause_input(event: InputEvent) -> Dictionary:
	if not _pause_view.input_ready:
		return {"ok": true, "value": false}
	if event is InputEventMouseMotion:
		var hovered: Dictionary = _try_point_pause_at(event.position)
		if not hovered.ok:
			return hovered
		if hovered.value and hovered.moved:
			var cue: Dictionary = _forward_frontend_audio_cue(Frontend.AudioCue.MOVE)
			if not cue.ok:
				return cue
		return {"ok": true, "value": true}
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			return _handled(_move_pause_selection(-1))
		if event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			return _handled(_move_pause_selection(1))
		if event.button_index == MOUSE_BUTTON_LEFT:
			var pointed: Dictionary = _try_point_pause_at(event.position)
			if not pointed.ok:
				return pointed
			if pointed.value:
				if pointed.moved:
					var cue: Dictionary = _forward_frontend_audio_cue(Frontend.AudioCue.MOVE)
					if not cue.ok:
						return cue
				return _handled(_activate_pause_selection())
		return {"ok": true, "value": false}
	if event is InputEventJoypadButton and event.pressed:
		match event.button_index:
			JOY_BUTTON_DPAD_UP:
				return _handled(_move_pause_selection(-1))
			JOY_BUTTON_DPAD_DOWN:
				return _handled(_move_pause_selection(1))
			JOY_BUTTON_A:
				return _handled(_activate_pause_selection())
			JOY_BUTTON_B:
				var cue: Dictionary = _forward_frontend_audio_cue(Frontend.AudioCue.BACK)
				if cue.ok:
					cue = _handle_pause_action(_pause_menu.cancel())
				if cue.ok:
					cue = _refresh_pause_view()
				return _handled(cue)
		return {"ok": true, "value": false}
	if not event is InputEventKey or not event.pressed or event.echo:
		return {"ok": true, "value": false}
	if _is_key(event, KEY_UP):
		return _handled(_move_pause_selection(-1))
	if _is_key(event, KEY_DOWN):
		return _handled(_move_pause_selection(1))
	if _is_key(event, KEY_ENTER) or _is_key(event, KEY_KP_ENTER) or _is_key(event, KEY_SPACE):
		return _handled(_activate_pause_selection())
	return {"ok": true, "value": false}


## Returns {ok, value: pointed at an enabled row, moved}.
func _try_point_pause_at(viewport_position: Vector2) -> Dictionary:
	var index: int = _pause_view.point_at(viewport_position)
	var entries: Array[Dictionary] = _pause_menu.get_entries()
	if index < 0 or index >= entries.size() or not entries[index].enabled:
		return {"ok": true, "value": false, "moved": false}
	var moved: bool = _pause_menu.hover(index)
	if moved:
		var refreshed: Dictionary = _refresh_pause_view()
		if not refreshed.ok:
			return refreshed
	return {"ok": true, "value": true, "moved": moved}


func _move_pause_selection(direction: int) -> Dictionary:
	if _pause_menu.move_selection(direction):
		var cue: Dictionary = _forward_frontend_audio_cue(Frontend.AudioCue.MOVE)
		return _refresh_pause_view() if cue.ok else cue
	return {"ok": true}


func _activate_pause_selection() -> Dictionary:
	var action: int = _pause_menu.activate_selected()
	if action != PauseModel.Action.RETRY_LEVEL and action != PauseModel.Action.RETURN_TO_FRONTEND:
		var cue: Dictionary = _forward_frontend_audio_cue(Frontend.AudioCue.SELECT)
		if not cue.ok:
			return cue
	var handled: Dictionary = _handle_pause_action(action)
	return _refresh_pause_view() if handled.ok else handled


func _open_authentic_pause_menu() -> Dictionary:
	_pause_menu.open()
	_session.set_authentic_menu_paused(true)
	var paused: Dictionary = _audio.set_gameplay_paused(true)
	if not paused.ok:
		return paused
	var refreshed: Dictionary = _refresh_pause_view()
	if not refreshed.ok:
		return refreshed
	_pause_view.open_panel()
	_update_gameplay_cursor_mode()
	return {"ok": true}


func _handle_pause_action(action: int) -> Dictionary:
	match action:
		PauseModel.Action.NONE:
			return {"ok": true}
		PauseModel.Action.RESUME:
			return _resume_from_authentic_pause()
		PauseModel.Action.RETRY_LEVEL:
			var exited: Dictionary = _complete_pause_exit_audio()
			if not exited.ok:
				return exited
			var closed: Dictionary = _close_authentic_pause_for_lifecycle()
			return restart_level100() if closed.ok else closed
		PauseModel.Action.RETURN_TO_FRONTEND:
			var exited: Dictionary = _complete_pause_exit_audio()
			if not exited.ok:
				return exited
			var closed: Dictionary = _close_authentic_pause_for_lifecycle()
			return leave_level100_for_main_menu() if closed.ok else closed
	return {"ok": false, "error_type": "InvalidOperationException", "error": "Unsupported pause action %d." % action}


func _complete_pause_exit_audio() -> Dictionary:
	var stopped: Dictionary = _audio.stop_for_level_exit(true)
	if not stopped.ok:
		return stopped
	_pause_exit_audio_completed = true
	frontend_audio_cue_requested.emit(Frontend.AudioCue.SELECT)
	return {"ok": true}


func _resume_from_authentic_pause() -> Dictionary:
	_session.set_authentic_menu_paused(false)
	var control: Dictionary = _bridge.ControlFacts()
	if not control.ok:
		return control
	var paused: Dictionary = _audio.set_gameplay_paused(control.value.gameplay_paused)
	if not paused.ok:
		return paused
	_pause_view.close_panel()
	_update_gameplay_cursor_mode()
	return {"ok": true}


func _close_authentic_pause_for_lifecycle() -> Dictionary:
	_pause_menu.reset()
	_session.set_authentic_menu_paused(false)
	var paused: Dictionary = _audio.set_gameplay_paused(false)
	if not paused.ok:
		return paused
	_pause_view.reset_panel()
	return {"ok": true}


func _refresh_pause_view() -> Dictionary:
	if not _pause_view.set_snapshot(_pause_menu.view_snapshot()):
		return {"ok": false, "error_type": "InvalidDataException",
			"error": "The pause presentation rejected the Client menu snapshot."}
	return {"ok": true}


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		_request_quit(0)
		return
	if _quit_exit_code != null:
		return
	if what == NOTIFICATION_WM_WINDOW_FOCUS_OUT:
		_window_has_focus = false
		if _gameplay_active and (not _smoke_mode or _smoke_completing):
			_session.suspend_input_until_released()
			_update_gameplay_cursor_mode()
			_smoke_cursor_released_on_focus_loss = _requested_cursor_mode == Frontend.CursorMode.VISIBLE
	elif what == NOTIFICATION_WM_WINDOW_FOCUS_IN:
		_window_has_focus = true
		if _gameplay_active:
			_update_gameplay_cursor_mode()
			_smoke_cursor_recaptured_on_focus_gain = _requested_cursor_mode == Frontend.CursorMode.CAPTURED


func _request_quit(exit_code: int) -> void:
	if _quit_exit_code != null:
		if exit_code != 0:
			_quit_exit_code = exit_code
		return
	_quit_exit_code = exit_code
	_audio_shutdown_deadline_ms = Time.get_ticks_msec() + 5_000
	_gameplay_active = false
	set_process_input(false)
	# Freeze producers before stopping audio. Ordinary frames continue only for
	# this root's retirement check and Godot's mixer/main-thread cleanup.
	for child: Node in get_children():
		_freeze_for_quit(child)
	if is_instance_valid(_audio):
		# The owned 3D players are queued for deletion too: a play issued before
		# its first physics frame holds a pending-start reference even after stop.
		_report(_audio.stop_level100_audio(), "Audio shutdown")
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_process(true)


static func _freeze_for_quit(node: Node) -> void:
	node.process_mode = Node.PROCESS_MODE_DISABLED
	if node is AudioStreamPlayer or node is AudioStreamPlayer3D:
		node.stop()
		node.stream = null
	for child: Node in node.get_children():
		_freeze_for_quit(child)


func _exit_tree() -> void:
	_report(_persist_recorded_tape_if_requested(), "Recorded command tape")
	# Also covers a native owner created before world loading failed.
	_release_platform_input()
	if is_instance_valid(_frontend):
		_frontend.set_effect_handler(Callable())
		_frontend.set_voice_observer(Callable())
	_frontend = null
	if _tape_recording and _bridge != null:
		_bridge.DiscardRecording()
	_tape_recording = false
	_audio_retirement.dispose()
	_pause_menu = null
	if not _smoke_mode:
		_apply_frontend_cursor_mode(Frontend.CursorMode.VISIBLE)
	_release_synthetic_input()


static func _configure_input_map() -> void:
	_ensure_key_action(MOVE_FORWARD, KEY_W)
	_ensure_key_action(MOVE_FORWARD, KEY_UP)
	_ensure_key_action(MOVE_BACKWARD, KEY_S)
	_ensure_key_action(MOVE_BACKWARD, KEY_DOWN)
	_ensure_key_action(MOVE_LEFT, KEY_A)
	_ensure_key_action(MOVE_LEFT, KEY_LEFT)
	_ensure_key_action(MOVE_RIGHT, KEY_D)
	_ensure_key_action(MOVE_RIGHT, KEY_RIGHT)
	_ensure_unbound_action(LOOK_LEFT)
	_ensure_unbound_action(LOOK_RIGHT)
	_ensure_unbound_action(LOOK_UP)
	_ensure_unbound_action(LOOK_DOWN)
	_ensure_key_action(FIRE, KEY_SPACE)
	_ensure_key_action(TOGGLE_MODE, KEY_Q)
	_ensure_key_action(LANDING_JETS, KEY_SHIFT)
	_ensure_key_action(RESET, KEY_R)


static func _ensure_key_action(action: StringName, key: Key) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action, 0.2)
	var physical_mapped: bool = false
	for input: InputEvent in InputMap.action_get_events(action):
		if input is InputEventKey and input.physical_keycode == key:
			physical_mapped = true
	if not physical_mapped:
		var physical := InputEventKey.new()
		physical.physical_keycode = key
		InputMap.action_add_event(action, physical)
	var logical_mapped: bool = false
	for input: InputEvent in InputMap.action_get_events(action):
		if input is InputEventKey and input.keycode == key:
			logical_mapped = true
	if not logical_mapped:
		var logical := InputEventKey.new()
		logical.keycode = key
		InputMap.action_add_event(action, logical)


static func _ensure_unbound_action(action: StringName) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action, 0.2)
	InputMap.action_erase_events(action)


static func _is_key(input: InputEventKey, key: Key) -> bool:
	return input.physical_keycode == key or input.keycode == key


func _observe_platform_input_event(event: InputEvent) -> Dictionary:
	if event is InputEventKey:
		return _platform_input.observe_key(_platform_key_code(event), event.pressed, event.echo)
	if event is InputEventJoypadButton:
		return _platform_input.observe_joy_button(event.device, event.button_index, 255 if event.pressed else 0)
	return {"ok": true}


static func _platform_key_code(input: InputEventKey) -> int:
	return input.physical_keycode if input.physical_keycode != KEY_NONE else input.keycode


static func _sample_input() -> Dictionary:
	return {"move_x": _quantize_axis(Input.get_axis(MOVE_LEFT, MOVE_RIGHT)),
		"move_z": _quantize_axis(Input.get_axis(MOVE_BACKWARD, MOVE_FORWARD)),
		"fire_held": Input.is_action_pressed(FIRE), "toggle_mode_held": Input.is_action_pressed(TOGGLE_MODE),
		"reset_held": Input.is_action_pressed(RESET),
		"look_x": _quantize_axis(Input.get_axis(LOOK_LEFT, LOOK_RIGHT)),
		"look_y": _quantize_axis(Input.get_axis(LOOK_UP, LOOK_DOWN)),
		"landing_jets_held": Input.is_action_pressed(LANDING_JETS)}


static func _quantize_axis(value: float) -> int:
	if value > AXIS_DEAD_ZONE:
		return 1
	if value < -AXIS_DEAD_ZONE:
		return -1
	return 0


## Binary32 product, rounded half away from zero, clamped to one million.
static func _to_milli_pixels(value: float) -> int:
	return int(clampf(roundf(F.value(value * 1_000.0)), -1_000_000.0, 1_000_000.0))


func _create_level100_world() -> Dictionary:
	if _level100_world_created:
		return {"ok": false, "error_type": "InvalidOperationException", "error": "The Level 100 world is already created."}
	var verified: Dictionary = _bridge.VerifyWorldImport()
	if not verified.ok:
		return verified
	_world = (ResourceLoader.load(WORLD_SCENE_PATH) as PackedScene).instantiate()
	add_child(_world)
	var initialized: Dictionary = _world.InitializeFromBridge(_bridge)
	if not initialized.ok:
		return initialized
	var binding: Dictionary = _bridge.AquilaBinding()
	if not binding.ok:
		return binding
	var bound: Dictionary = _audio.bind_aquila(binding.value.actor_id, binding.value.actors)
	if not bound.ok:
		return bound
	var hud: Dictionary = _create_hud()
	if not hud.ok:
		return hud
	add_child(_hud)
	var updated: Dictionary = _update_hud()
	if not updated.ok:
		return updated
	_hud.visible = initialized.show_hud
	_pause_view = (load(PAUSE_SCENE_PATH) as PackedScene).instantiate()
	var refreshed: Dictionary = _refresh_pause_view()
	if not refreshed.ok:
		return refreshed
	add_child(_pause_view)
	refreshed = _refresh_pause_view()
	if not refreshed.ok:
		return refreshed
	var advanced: Dictionary = _session.advance_frame_ticks(0)
	if not advanced.ok:
		return advanced
	var consumed: Dictionary = _consume_frame_events()
	if not consumed.ok:
		return consumed
	updated = _update_hud()
	if not updated.ok:
		return updated
	_level100_world_created = true
	return {"ok": true}


func _create_hud() -> Dictionary:
	var manifest: Dictionary = _read_manifest_bytes()
	if not manifest.ok:
		return manifest
	var allegiance: Dictionary = _bridge.DecodeAuthoredAllegiance(manifest.value)
	if not allegiance.ok:
		return allegiance
	_hud = (load(HUD_SCENE_PATH) as PackedScene).instantiate()
	_hud_info = {}
	_hud_delivered_ids = []
	var configured: Dictionary = _hud.configure_for_gameplay(allegiance.value, _hud_text_catalog)
	if not configured.ok:
		return {"ok": false, "error_type": "InvalidDataException", "error": configured.error}
	var initialized: Dictionary = _hud.initialize()
	if not initialized.ok:
		return {"ok": false, "error_type": "InvalidDataException", "error": initialized.error}
	return {"ok": true}


## Core mission ticks own reveal, pose and noise, so the HUD never follows the
## audio mixer; fixed-fps captures stay deterministic.
func _update_hud() -> Dictionary:
	var frame: Dictionary = _bridge.HudFrame()
	if not frame.ok:
		return frame
	var result: Dictionary = _hud.update_from_facts(frame.value.facts, frame.value.frame)
	if result.has("delivered_message_ids"):
		_hud_delivered_ids = _int_list(result.delivered_message_ids)
	if not result.ok:
		return {"ok": false, "error_type": "InvalidDataException", "error": result.error}
	_hud_info = result.value
	_hud_delivered_ids = _int_list(_hud_info.delivered_message_ids)
	return {"ok": true}


func _load_level100_from_frontend() -> void:
	var loaded: Dictionary = _try_load_level100_from_frontend()
	if not loaded.ok:
		set_process(false)
		push_error("Level 100 failed to load from the frontend: " + String(loaded.get("error", "")))
		_request_quit(4)


func _try_load_level100_from_frontend() -> Dictionary:
	if is_instance_valid(_frontend) and not _frontend.host_snapshot().selected_world_is_constructible:
		# World 110 and every later node is selectable after a Won update, but
		# this reconstruction still has only a Level 100 session owner. Do not
		# silently construct 100 in its place.
		var returned: Dictionary = _frontend.return_unconstructible_launch_to_level_select()
		if not returned.ok:
			return returned
		return _audio.start_frontend_music()
	if _level100_world_created:
		var destroyed: Dictionary = _destroy_level100_world()
		if not destroyed.ok:
			return destroyed
	var created: Dictionary = _create_session()
	if not created.ok:
		return created
	var recording: Dictionary = _enable_recording_if_requested()
	if not recording.ok:
		return recording
	var reapplied: Dictionary = _reapply_options_settings()
	if not reapplied.ok:
		return reapplied
	var world: Dictionary = _create_level100_world()
	if not world.ok:
		return world
	return _frontend.mark_level100_ready()


func _try_accept_won_frontend_handoff() -> Dictionary:
	var control: Dictionary = _bridge.ControlFacts()
	if not control.ok:
		return control
	if not control.value.frontend_handoff_ready or not is_instance_valid(_frontend):
		return {"ok": true}
	return _frontend.accept_won_handoff(control.value.mission_outcome, control.value.mission_terminal_state)


## CGame::RunLevel stops the frontend track in the call stack that enters
## loading (game.cpp:1584-1586, retail 0x0046e240). Waiting for the load request
## would leave two rendered loading frames playing MUS_FRONTEND.
func _stop_frontend_music_for_level_entry() -> Dictionary:
	return _audio.stop_music()


func _activate_frontend_gameplay() -> Dictionary:
	if not _level100_world_created:
		push_error("The frontend tried to activate gameplay before Level 100 was ready.")
		_request_quit(4)
		return {"ok": true}
	var music: Dictionary = _audio.start_tutorial_music()
	if not music.ok:
		return music
	_gameplay_active = true
	_update_gameplay_cursor_mode()
	if not _smoke_mode:
		return {"ok": true}
	if _smoke_phase == SmokePhase.COLD_FRONTEND:
		_smoke_saw_gameplay = true
		_capture_smoke_gameplay_cursor_policy()
		_smoke_phase = SmokePhase.INITIAL_GAMEPLAY
	elif _smoke_phase == SmokePhase.AWAITING_RETRY_GAMEPLAY:
		_smoke_retry_gameplay_activated = true
		var tick: Dictionary = _bridge.GetTick()
		_smoke_retry_session_fresh = tick.ok and tick.value == 0 \
			and _session.metrics().total_steps == 0 and _level100_world_created
		_smoke_phase = SmokePhase.RETRY_GAMEPLAY
	return {"ok": true}


## Host window focus is not evidence about the rebuild: Godot cannot capture an
## unfocused window. What is decidable is the released policy over every
## (focus, pause) pair, evaluated through the product's own cursor update, and
## that activation applied it to whatever focus the host had. The observed focus
## is reported for honesty and never asserted.
func _capture_smoke_gameplay_cursor_policy() -> void:
	var actual_focus: bool = _window_has_focus
	_smoke_window_focused_at_gameplay = actual_focus
	_smoke_cursor_policy_applied_at_gameplay = _requested_cursor_mode == \
		(Frontend.CursorMode.CAPTURED if actual_focus and not _session.is_paused() else Frontend.CursorMode.VISIBLE)
	var policy: Array[String] = []
	for pair: Array in [[true, false], [true, true], [false, false], [false, true]]:
		_window_has_focus = pair[0]
		_session.set_authentic_menu_paused(pair[1])
		_update_gameplay_cursor_mode()
		policy.append(CURSOR_NAMES[_requested_cursor_mode])
	_session.set_authentic_menu_paused(false)
	_window_has_focus = actual_focus
	_update_gameplay_cursor_mode()
	_smoke_gameplay_cursor_policy = policy


## Mixer playback advances in wall-clock time, so which message is audible at a
## tick is a race. What holds on every sample is that the voice adapter starts
## Core-requested messages in Core order without inventing or reordering any.
func _sample_smoke_voice_progress() -> void:
	var playback: Dictionary = _audio.character_message_playback()
	var audible: Variant = playback.active_message_id if playback.playing else null
	if audible != null and audible != _smoke_voice_last_observed_message_id:
		_smoke_voice_started_message_ids.append(audible)
	_smoke_voice_last_observed_message_id = audible
	var audible_implies_identified: bool = not playback.playing or (playback.active_message_id != null \
		and playback.active_speaker_id != null and playback.length_seconds > 0.0 \
		and playback.position_seconds >= 0.0 and playback.position_seconds <= playback.length_seconds)
	var active_message_was_requested: bool = playback.active_message_id == null \
		or _hud_delivered_ids.has(playback.active_message_id)
	_smoke_voice_playback_consistent = _smoke_voice_playback_consistent and audible_implies_identified \
		and active_message_was_requested and not playback.paused


func _suspend_frontend_gameplay() -> Dictionary:
	if _level100_world_created and _session.is_authentic_menu_paused():
		var closed: Dictionary = _close_authentic_pause_for_lifecycle()
		if not closed.ok:
			return closed
	_gameplay_active = false
	if _session != null:
		_session.release_all_input()
	return {"ok": true}


func _release_level100_for_main_menu() -> Dictionary:
	var suspended: Dictionary = _suspend_frontend_gameplay()
	if not suspended.ok:
		return suspended
	var destroyed: Dictionary = _destroy_level100_world()
	if not destroyed.ok:
		return destroyed
	# Retail restores MUS_FRONTEND whenever the frontend takes the screen back
	# (CFEPMain::Process 0x00462640, CFEPGoodies::Process 0x0045d7e0). The exact
	# post-level path is not established; without this the menu returns silent.
	return _audio.start_frontend_music()


func _destroy_level100_world() -> Dictionary:
	if not _level100_world_created:
		return {"ok": true}
	var persisted: Dictionary = _persist_recorded_tape_if_requested()
	if not persisted.ok:
		return persisted
	_world.visible = false
	_hud.visible = false
	_pause_view.visible = false
	_pause_menu.reset()
	_session.set_authentic_menu_paused(false)
	var paused: Dictionary = _audio.set_gameplay_paused(false)
	if not paused.ok:
		return paused
	if not _pause_exit_audio_completed:
		var stopped: Dictionary = _audio.stop_level100_audio()
		if not stopped.ok:
			return stopped
	_pause_exit_audio_completed = false
	_world.queue_free()
	_hud.queue_free()
	_pause_view.queue_free()
	_level100_world_created = false
	_release_platform_input()
	_session = null
	_bridge = null
	return {"ok": true}


func _create_session() -> Dictionary:
	if _platform_input != null:
		return {"ok": false, "error_type": "InvalidOperationException",
			"error": "Release the previous platform input owner before creating a session."}
	var manifest: Dictionary = _read_manifest_bytes()
	if not manifest.ok:
		return manifest
	var bridge: RefCounted = (load(BRIDGE_SCRIPT_PATH) as Script).new()
	var input: RefCounted = PlatformInput.new()
	# The session borrows this one input owner. Host events, pause and focus
	# resets, and host-frame advances keep their existing order.
	var session: RefCounted = InteractiveSession.new(bridge, input)
	var started: Dictionary = session.start(SIMULATION_SEED, manifest.value)
	if not started.ok:
		return started
	_bridge = bridge
	_session = session
	_platform_input = input
	return {"ok": true}


func _release_platform_input() -> void:
	_platform_input = null


## The verified static-world manifest: Core's actor definitions and the HUD's
## authored allegiance are both decoded from these exact bytes by the bridge.
static func _read_manifest_bytes() -> Dictionary:
	var bytes: PackedByteArray = FileAccess.get_file_as_bytes(MANIFEST_PATH)
	if bytes.is_empty() or bytes.size() > MANIFEST_MAXIMUM_BYTES:
		return {"ok": false, "error_type": "InvalidDataException",
			"error": "The locally materialized Level 100 static-world manifest is missing or changed."}
	return {"ok": true, "value": bytes}


## With --record-tape, the session feeds its exact consumed per-tick input
## (post-quantise look permille, merged pulses, consumed edges) into the Core
## recorder from the first gameplay tick, with the resulting live state hashes.
func _enable_recording_if_requested() -> Dictionary:
	if _record_tape_path.is_empty():
		return {"ok": true}
	var enabled: Dictionary = _bridge.EnableRecording()
	if enabled.ok:
		_tape_recording = true
	return enabled


## Session-end persistence: once per finalized session, the Core writes the
## tape to the named path with create-new semantics. A failure is loud and
## nothing is ever overwritten or silently dropped.
func _persist_recorded_tape_if_requested() -> Dictionary:
	if _record_tape_path.is_empty() or not _tape_recording or _session == null:
		return {"ok": true}
	var persisted: Dictionary = _bridge.PersistRecordedTape(_record_tape_path)
	if not persisted.ok:
		return persisted
	_tape_recording = false
	if not persisted.value:
		# The wire contract requires at least one tick; a session that ended
		# before its first step has nothing replayable to finalize.
		return {"ok": true}
	print("Recorded command tape written to " + _record_tape_path)
	# Exactly once per explicit request: retry and return flows must not arm a
	# second recorder that could only collide with the create-new path.
	_record_tape_path = ""
	return {"ok": true}


func _require_level100_frontend() -> Dictionary:
	if not is_instance_valid(_frontend) or _frontend_screen() != Frontend.Screen.GAMEPLAY:
		return {"ok": false, "error_type": "InvalidOperationException",
			"error": "A Level 100 restart or Main Menu return requires active gameplay."}
	return {"ok": true}


func _frontend_screen() -> int:
	return _frontend.host_snapshot().screen


func _drive_smoke_frontend() -> Dictionary:
	if not is_instance_valid(_frontend):
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Smoke requires the normal retail frontend."}
	var screen: int = _frontend_screen()
	if _smoke_phase == SmokePhase.COLD_FRONTEND:
		match screen:
			Frontend.Screen.CLICK_TO_START:
				_smoke_saw_click_to_start = true
				_smoke_cursor_custom_at_frontend = _requested_cursor_mode == Frontend.CursorMode.CUSTOM
				return _frontend.confirm()
			Frontend.Screen.MAIN_MENU, Frontend.Screen.DEV_SELECT, Frontend.Screen.LEVEL_SELECT, \
					Frontend.Screen.MISSION_BRIEFING, Frontend.Screen.SELECT_CONFIGURATION:
				# Briefing and configuration are traversed, not asserted: their
				# parity is measured by pixel capture, not by the simulation.
				match screen:
					Frontend.Screen.MAIN_MENU: _smoke_saw_main_menu = true
					Frontend.Screen.DEV_SELECT: _smoke_saw_dev_select = true
					Frontend.Screen.LEVEL_SELECT: _smoke_saw_level_select = true
					Frontend.Screen.MISSION_BRIEFING: _smoke_saw_mission_briefing = true
					Frontend.Screen.SELECT_CONFIGURATION: _smoke_saw_select_configuration = true
				_smoke_cursor_custom_at_frontend = _smoke_cursor_custom_at_frontend \
					and _requested_cursor_mode == Frontend.CursorMode.CUSTOM
				return _frontend.confirm()
			Frontend.Screen.LOADING:
				_smoke_saw_loading = true
				_smoke_cursor_hidden_at_loading = _requested_cursor_mode == Frontend.CursorMode.HIDDEN
				return {"ok": true}
			Frontend.Screen.INTRO_CUTSCENE:
				# Retail's level intro FMV (references/Onslaught/game.cpp:1336-1345).
				# --smoke suppresses it like -skipfmv; --smoke --intro waits it out.
				return {"ok": true}
		return {"ok": false, "error_type": "InvalidOperationException",
			"error": "Cold frontend smoke reached unexpected state %s." % SCREEN_NAMES[screen]}
	if _smoke_phase == SmokePhase.AWAITING_RETRY_GAMEPLAY:
		if screen != Frontend.Screen.LOADING:
			return {"ok": false, "error_type": "InvalidOperationException",
				"error": "Retry smoke reached unexpected state %s." % SCREEN_NAMES[screen]}
		_smoke_cursor_hidden_at_loading = _smoke_cursor_hidden_at_loading \
			and _requested_cursor_mode == Frontend.CursorMode.HIDDEN
	return {"ok": true}


func _finish_smoke_retry_and_return() -> Dictionary:
	_smoke_return_requested = true
	var left: Dictionary = leave_level100_for_main_menu()
	if not left.ok:
		return left
	_smoke_returned_to_main_menu = _frontend_screen() == Frontend.Screen.MAIN_MENU
	_smoke_world_released_at_main_menu = not _level100_world_created
	_smoke_cursor_custom_at_main_menu = _requested_cursor_mode == Frontend.CursorMode.CUSTOM
	_smoke_phase = SmokePhase.RETURNED_TO_MAIN_MENU
	_complete_smoke.call_deferred()
	return {"ok": true}


func _apply_frontend_cursor_mode(mode: int) -> void:
	_requested_cursor_mode = mode
	if _smoke_mode or _capture_mode:
		return
	match mode:
		Frontend.CursorMode.CUSTOM, Frontend.CursorMode.HIDDEN:
			Input.mouse_mode = Input.MOUSE_MODE_HIDDEN
		Frontend.CursorMode.VISIBLE:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		Frontend.CursorMode.CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _update_gameplay_cursor_mode() -> void:
	_apply_frontend_cursor_mode(Frontend.CursorMode.VISIBLE if not _window_has_focus or _session.is_paused()
		else Frontend.CursorMode.CAPTURED)


## The options rows that have a consumer. Both volume rows hand the raw slider
## value to the audio owner (released PC behavior diverges from the retained
## curves: sound stores the float, music stores round(volume * 127) and keeps
## the raw career/slider float; device math and audible parity are unknown).
## Mouse sensitivity reaches the session's pointer axis, where 7.0 reproduces
## 91/3000. Every other row is presented and remembered but has no owner yet.
func _apply_options_settings(settings: Dictionary) -> Dictionary:
	if _audio != null:
		var sound: Dictionary = _audio.set_master_sound_option(F.value(settings.sound_volume))
		if not sound.ok:
			return sound
		var music: Dictionary = _audio.set_music_option(F.value(settings.music_volume))
		if not music.ok:
			return music
	# The session is created per level load; a frontend change made before one
	# exists is picked up by _reapply_options_settings.
	if _session != null:
		return _session.set_mouse_sensitivity(F.value(settings.mouse_sensitivity))
	return {"ok": true}


func _reapply_options_settings() -> Dictionary:
	if not is_instance_valid(_frontend):
		return {"ok": true}
	return _apply_options_settings(_frontend.host_snapshot().options_settings)


func _forward_frontend_audio_cue(cue: int) -> Dictionary:
	var played: Dictionary = _audio.play_frontend_cue(AUDIO_CUE_NAMES[cue])
	if not played.ok:
		return played
	frontend_audio_cue_requested.emit(cue)
	return {"ok": true}


static func _apply_synthetic_input(input: Dictionary) -> void:
	_set_synthetic_action(MOVE_LEFT, input.move_x < 0)
	_set_synthetic_action(MOVE_RIGHT, input.move_x > 0)
	_set_synthetic_action(MOVE_BACKWARD, input.move_z < 0)
	_set_synthetic_action(MOVE_FORWARD, input.move_z > 0)
	_set_synthetic_action(LOOK_LEFT, input.look_x < 0)
	_set_synthetic_action(LOOK_RIGHT, input.look_x > 0)
	_set_synthetic_action(LOOK_UP, input.look_y < 0)
	_set_synthetic_action(LOOK_DOWN, input.look_y > 0)
	_set_synthetic_action(FIRE, input.fire_held)
	_set_synthetic_action(TOGGLE_MODE, input.toggle_mode_held)
	_set_synthetic_action(RESET, input.reset_held)


static func _set_synthetic_action(action: StringName, pressed: bool) -> void:
	if pressed:
		Input.action_press(action)
	else:
		Input.action_release(action)


static func _release_synthetic_input() -> void:
	for action: StringName in ALL_ACTIONS:
		Input.action_release(action)


## One ordered Core batch per frame for the native audio owner. Its fixed host
## phases preserve the HUD and world interleavings: mission events reach the HUD
## before audio queues messages, weapon visuals keep their slot, and world
## destruction precedes its audio cues.
func _consume_frame_events() -> Dictionary:
	# The host never advances a paused session, so every frame delivers.
	var taken: Dictionary = _bridge.TakeFrameFacts(true)
	if not taken.ok:
		return taken
	_frame_events = taken.value
	var result: Dictionary = _audio.consume_frame(_frame_events.audio, _interleave_frame_phase)
	_frame_events = {}
	return result


func _interleave_frame_phase(phase: int) -> Dictionary:
	match phase:
		0:
			return _consume_level100_mission_events(_frame_events.mission_events)
		1:
			return _world.ConsumeWeaponFireFacts(_frame_events.weapon_events)
		2:
			return _world.ConsumeDestructionFacts(_frame_events.destruction_events, _frame_events.tick)
	return {"ok": false, "error_type": "InvalidOperationException", "error": "Unknown native audio host phase %d." % phase}


func _consume_level100_mission_events(events: Array) -> Dictionary:
	var consumed: Dictionary = _hud.consume_events(events)
	if not consumed.ok:
		return {"ok": false, "error_type": "InvalidDataException", "error": consumed.error}
	for event: Dictionary in events:
		# Recorded on the audio-forwarding path, so it cross-checks the HUD
		# delivery path rather than restating it. Both are Core-event ordered.
		if event.kind == "message" and _smoke_mode and _smoke_report.is_empty():
			_smoke_audio_queued_speaker_ids.append(event.speaker_id)
			_smoke_audio_queued_message_ids.append(event.message_id)
	return {"ok": true}


func _run_focus_loss_handler_smoke_probe() -> Dictionary:
	var held: Dictionary = InteractiveInput.create(1, 1, true, true, true).value
	for step: Dictionary in [_session.observe_input(held), _session.queue_movement_pulse(-1, -1),
			_session.queue_look_pulse(-1, -1), _session.queue_pointer_motion_milli_pixels(-10_000, 10_000)]:
		if not step.ok:
			return step
	_session.queue_fire_pulse()
	_notification(NOTIFICATION_WM_WINDOW_FOCUS_OUT)
	for step: Dictionary in [_session.observe_input(held), _session.queue_movement_pulse(1, 0),
			_session.queue_look_pulse(1, 0), _session.queue_pointer_motion_milli_pixels(10_000, -10_000)]:
		if not step.ok:
			return step
	_session.queue_fire_pulse()
	_session.queue_toggle_mode()
	_session.queue_reset()
	_focus_loss_handler_input_cleared = _session.input_suspended_until_released() \
		and not _session.has_held_or_pending_input()
	_release_synthetic_input()
	var idle: Dictionary = _session.observe_input(InteractiveInput.idle())
	if not idle.ok:
		return idle
	_session.queue_fire_pulse()
	_focus_loss_handler_neutral_rearmed = not _session.input_suspended_until_released() \
		and _session.has_held_or_pending_input()
	_session.release_all_input()
	_notification(NOTIFICATION_WM_WINDOW_FOCUS_IN)
	return {"ok": true}


## Runs retail's cold-start media (the Lost Toys logo movie, the opening montage
## and the splash card) ahead of the interactive frontend. Capture and smoke runs
## suppress it exactly as retail's -skipfmv does: every retail reference frame
## was captured with -skipfmv, and the 13 pinned startup shots begin at
## click-to-start on engine frame 12. The deterministic schedule and media index
## are checked directly, and --intro forces the sequence on for a human or rig.
func _start_retail_startup_media() -> Dictionary:
	# CGame::GetIntroFMV (game.cpp:1103-1119) is one retail flag; the schedule
	# owner decides it so --skipfmv, --smoke, capture and --intro cannot drift
	# from the level-cutscene gate in frontend_flow.gd.
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	var suppressed: Dictionary = Schedule.is_suppressed_by_arguments(arguments)
	if not suppressed.ok:
		return suppressed
	if suppressed.value:
		return _start_frontend_music_after_startup_media()
	var sequence: Control = (load(STARTUP_SCENE_PATH) as PackedScene).instantiate()
	sequence.name = "RetailStartupSequence"
	# A capture run is deterministic by contract, so the sequence advances on
	# the tick rather than on a delta the host could jitter.
	var configured: Dictionary = _configure_startup_sequence(sequence, Startup.Route.COLD, arguments)
	if not configured.ok:
		sequence.free()
		return configured
	if sequence.get_scheduled_seconds() <= 0.0:
		# Nothing was decoded. Do not hold a black screen, and never draw a
		# stand-in for missing footage.
		var reason: String = sequence.get_media_unavailable_reason()
		push_warning("Startup media is absent, so splash and intro FMV do not play. "
			+ ("No cue had decoded media." if reason.is_empty() else reason))
		sequence.queue_free()
		return _start_frontend_music_after_startup_media()
	# The frontend must not tick or draw underneath: its click-to-start pulse
	# timer starts when the page is first shown.
	var suspended: Dictionary = _frontend.suspend_for_startup_media()
	if not suspended.ok:
		sequence.free()
		return suspended
	sequence.completed.connect(_finish_retail_startup_media)
	_startup_sequence = sequence
	add_child(sequence)
	return {"ok": true}


func _configure_startup_sequence(sequence: Control, route: int, arguments: PackedStringArray) -> Dictionary:
	# A repeated initialization rejects before rereading any input.
	if sequence.is_initialized():
		return {"ok": false, "error_type": "InvalidOperationException", "error": "The startup sequence is already initialized."}
	var configured: Dictionary = sequence.configure_from_cache(Startup.resolve_media_root(arguments), route,
		Schedule.Cue.SPLASH, Startup.Clock.FIXED_TICK if _capture_arguments_present else Startup.Clock.WALL,
		_observe_playback)
	if not configured.ok:
		return {"ok": false, "error_type": "InvalidOperationException", "error": configured.error}
	return {"ok": true}


func _finish_retail_startup_media() -> void:
	_report(_start_frontend_music_after_startup_media(), "Frontend music")
	if is_instance_valid(_frontend):
		_report(_frontend.resume_after_startup_media(), "Frontend resume")
	if is_instance_valid(_startup_sequence):
		_startup_sequence.queue_free()
	_startup_sequence = null
	_click_to_start_page_seconds = 0.0


## CLTShell::RunFrontEndAndGameLoop attract restart: after click-to-start writes
## -3 the shell replays ltlogo and openingfmv, and Init(FEE_FROM_ATTRACT) lands
## on FEP_INTRO again. Smoke and capture stay off this path because their plans
## are frame-counted; that suppression is ours, not retail's. No fade is drawn.
func _advance_attract_idle(delta: float) -> Dictionary:
	if _startup_sequence != null or not is_instance_valid(_frontend):
		return {"ok": true}
	if _smoke_mode or _capture_mode or _capture_arguments_present:
		return {"ok": true}
	if _frontend_screen() != Frontend.Screen.CLICK_TO_START:
		_click_to_start_page_seconds = 0.0
		return {"ok": true}
	_click_to_start_page_seconds += maxf(0.0, delta)
	if not Click.idle_result_due(_click_to_start_page_seconds):
		return {"ok": true}
	_click_to_start_page_seconds = 0.0
	return _start_attract_restart_media()


func _start_attract_restart_media() -> Dictionary:
	if _startup_sequence != null:
		return {"ok": true}
	if _skip_startup_media and not _force_startup_media:
		# -skipfmv is retail's cold-start/level-intro gate; whether it also
		# swallows this loop's movies is unmeasured, so no black re-init.
		return {"ok": true}
	var sequence: Control = (load(STARTUP_SCENE_PATH) as PackedScene).instantiate()
	sequence.name = "RetailAttractRestart"
	var configured: Dictionary = _configure_startup_sequence(sequence, Startup.Route.ATTRACT, OS.get_cmdline_user_args())
	if not configured.ok:
		sequence.free()
		return configured
	if sequence.get_scheduled_seconds() <= 0.0:
		sequence.queue_free()
		return {"ok": true}
	var suspended: Dictionary = _frontend.suspend_for_startup_media()
	if not suspended.ok:
		sequence.free()
		return suspended
	sequence.completed.connect(_finish_retail_startup_media)
	_startup_sequence = sequence
	add_child(sequence)
	return {"ok": true}


## CFrontEnd::Init starts MUS_FRONTEND for the interactive frontend
## (FrontEnd.cpp:332-333). The startup movies carry their own authored audio,
## which is not decoded yet; silence beats playing the frontend bed over them.
func _start_frontend_music_after_startup_media() -> Dictionary:
	return _audio.start_frontend_music()


func _capture_smoke_report() -> Dictionary:
	var facts: Dictionary = _bridge.SmokeFacts()
	if not facts.ok:
		return facts
	var world: Dictionary = _world.PresentationFacts()
	var core: Dictionary = facts.value
	var metrics: Dictionary = _session.metrics()
	var playback: Dictionary = _audio.character_message_playback()
	# Key order is the report's field order.
	return {"ok": true, "value": {
		"schemaVersion": "onslaught-first-flight-smoke.v17",
		"engineVersion": Engine.get_version_info().string,
		"exitReason": "smoke-complete",
		"tick": core.tick,
		"stateHash": core.state_hash,
		"targetsDestroyed": core.targets_destroyed,
		"mode": core.mode,
		"level100OpeningTicksRemaining": core.level100_opening_ticks_remaining,
		"level100MissionTick": core.level100_mission_tick,
		"level100MissionOutcome": core.level100_mission_outcome,
		"level100TerminalState": core.level100_terminal_state,
		# Wall-clock, not tick-derived: the mixer advances in real time while
		# --fixed-fps drives the simulation as fast as the host allows. Bound it
		# against the delivered ids; never pin it.
		"level100PlayingMessageId": playback.active_message_id,
		"level100DeliveredMessageIds": _hud_delivered_ids.duplicate(),
		"level100AudioQueuedMessageIds": _smoke_audio_queued_message_ids.duplicate(),
		"level100AudioQueuedSpeakerIds": _smoke_audio_queued_speaker_ids.duplicate(),
		# An ordered prefix of the delivered ids whose length is host-dependent
		# but whose content is not.
		"level100VoiceStartedMessageIds": _smoke_voice_started_message_ids.duplicate(),
		"level100VoicePlaybackConsistent": _smoke_voice_playback_consistent,
		"level100PlayerControlEnabled": core.level100_player_control_enabled,
		"level100FlightEnabled": core.level100_flight_enabled,
		"level100PulseCannonEnabled": core.level100_pulse_cannon_enabled,
		"level100VulcanCannonEnabled": core.level100_vulcan_cannon_enabled,
		"level100FiringRangeTargetsActive": core.level100_firing_range_targets_active,
		"level100CurrentWeaponHighlighted": core.level100_current_weapon_highlighted,
		# Mixer state at this tick; false is legal in the message handoff gap.
		"tutorialVoicePlaying": _audio.tutorial_voice_playing(),
		"totalSteps": metrics.total_steps,
		"toggleEdgesConsumed": metrics.toggle_edges_consumed,
		"resetEdgesConsumed": metrics.reset_edges_consumed,
		"resetGeneration": metrics.reset_generation,
		"fireHeldTicksSampled": metrics.fire_held_ticks_sampled,
		"firePulseEdgesConsumed": metrics.fire_pulse_edges_consumed,
		"movementPulseEdgesConsumed": metrics.movement_pulse_edges_consumed,
		"cappedFrameCount": metrics.capped_frame_count,
		"droppedElapsedTicks": metrics.dropped_elapsed_ticks,
		"playerVisualPresent": world.player_visual_present,
		"retailAquilaMeshesPresent": world.retail_aquila_meshes_present,
		"retailAquilaSurfaceCount": world.retail_aquila_surface_count,
		"retailAquilaPartCount": world.retail_aquila_part_count,
		"retailAquilaAnimatedPartCount": world.retail_aquila_animated_part_count,
		"retailAquilaStandingClearance": world.retail_aquila_standing_clearance,
		"retailCockpitSurfaceCount": world.retail_cockpit_surface_count,
		"level100PlayerStartRelativeHeight": world.level100_player_start_relative_height,
		"retailLevel100StaticObjectCount": world.retail_level100_static_object_count,
		"retailLevel100StaticObjectSurfaceCount": world.retail_level100_static_object_surface_count,
		"retailLevel100PineCount": world.retail_level100_pine_count,
		"retailLevel100WaterPresent": world.retail_level100_water_present,
		"retailLevel100WaterGridVertexCount": world.retail_level100_water_grid_vertex_count,
		"retailLevel100WaterGridTriangleCount": world.retail_level100_water_grid_triangle_count,
		"retailLevel100ShorelineTriangleCount": world.retail_level100_shoreline_triangle_count,
		"retailLevel100TargetSurfaceCount": world.retail_level100_target_surface_count,
		"level100ObjectiveMarkerCount": int(_hud_info.get("objective_count", 0)),
		"level100DeliveredMessageCount": int(_hud_info.get("delivered_message_count", 0)),
		"level100DeliveredHelpCount": int(_hud_info.get("delivered_help_count", 0)),
		# Mixer-derived and additionally false whenever the mixer trails the
		# script past the HUD's active delivery. Reported, never pinned.
		"level100MessagePlaybackAvailable": _hud_info.get("playback_available", false) == true,
		"level100MessagePlaying": _hud_info.get("playing", false) == true,
		"retailLevel100TerrainVertexCount": world.retail_level100_terrain_vertex_count,
		"retailLevel100TerrainTriangleCount": world.retail_level100_terrain_triangle_count,
		"retailLevel100SkySurfaceCount": world.retail_level100_sky_surface_count,
		"targetVisualCount": world.target_visual_count,
		"openingPanActive": world.opening_pan_active,
		"hudVisible": world.show_hud,
		"hudReady": _hud.ready_for_snapshot,
		"focusLossHandlerInputCleared": _focus_loss_handler_input_cleared,
		"focusLossHandlerNeutralRearmed": _focus_loss_handler_neutral_rearmed,
	}}


func _complete_smoke() -> void:
	var completed: Dictionary = _write_smoke_report()
	if not completed.ok:
		push_error("First Flight smoke failed: " + String(completed.error))
		_request_quit(4)
		return
	_request_quit(0)


func _write_smoke_report() -> Dictionary:
	if _smoke_report.is_empty():
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Smoke gameplay evidence was not captured."}
	var report: Dictionary = _smoke_report
	report["coldClickToStart"] = _smoke_saw_click_to_start
	report["coldMainMenu"] = _smoke_saw_main_menu
	report["coldDevSelect"] = _smoke_saw_dev_select
	report["coldLevelSelect"] = _smoke_saw_level_select
	report["coldMissionBriefing"] = _smoke_saw_mission_briefing
	report["coldSelectConfiguration"] = _smoke_saw_select_configuration
	report["coldLoading"] = _smoke_saw_loading
	report["coldGameplay"] = _smoke_saw_gameplay
	report["cursorPolicyCustomAtFrontend"] = _smoke_cursor_custom_at_frontend
	report["cursorPolicyHiddenAtLoading"] = _smoke_cursor_hidden_at_loading
	report["gameplayCursorPolicy"] = _smoke_gameplay_cursor_policy.duplicate()
	report["cursorPolicyAppliedAtGameplay"] = _smoke_cursor_policy_applied_at_gameplay
	# Host desktop state: reported so a reader can see it, never asserted.
	report["windowFocusedAtGameplay"] = _smoke_window_focused_at_gameplay
	report["focusLossCursorPolicyVisible"] = _smoke_cursor_released_on_focus_loss
	report["focusGainCursorPolicyCaptured"] = _smoke_cursor_recaptured_on_focus_gain
	report["retryRequested"] = _smoke_retry_requested
	report["retryGameplayActivated"] = _smoke_retry_gameplay_activated
	report["retrySessionFresh"] = _smoke_retry_session_fresh
	report["returnToMainMenuRequested"] = _smoke_return_requested
	report["returnedToMainMenu"] = _smoke_returned_to_main_menu
	report["worldReleasedAtMainMenu"] = _smoke_world_released_at_main_menu
	report["mainMenuCursorPolicyCustom"] = _smoke_cursor_custom_at_main_menu
	report["finalFrontendScreen"] = SCREEN_NAMES[_frontend_screen()] if is_instance_valid(_frontend) else ""
	var text: String = JSON.stringify(report, "  ", false) + "\n"
	# Create-new and flushed to disk: the report path is never overwritten.
	var bridge: RefCounted = (load(BRIDGE_SCRIPT_PATH) as Script).new()
	return bridge.WriteNewFileDurably(_smoke_report_path, text.to_utf8_buffer())


func _dispatch_frontend_effect(effect: Dictionary, facts: Dictionary) -> Dictionary:
	match effect.get("kind"):
		"audio":
			return _forward_frontend_audio_cue(effect.cue)
		"apply_settings":
			return _apply_options_settings(facts.options_settings)
		"level_loading_started":
			return _stop_frontend_music_for_level_entry()
		"level_load_requested":
			_load_level100_from_frontend()
			return {"ok": true}
		"gameplay_activated":
			return _activate_frontend_gameplay()
		"gameplay_suspended":
			return _suspend_frontend_gameplay()
		"return_main_menu":
			return _release_level100_for_main_menu()
		"exit":
			_request_quit(0)
			return {"ok": true}
		"cursor_mode":
			_apply_frontend_cursor_mode(effect.mode)
			return {"ok": true}
		"career_selected":
			var index: int = effect.index
			if index < 0 or index >= _career_descriptors.size():
				return {"ok": false, "error_type": "InvalidDataException",
					"error": "The native frontend selected an unknown career descriptor."}
			_selected_career = _career_descriptors[index]
			return {"ok": true}
	return {"ok": false, "error_type": "InvalidDataException", "error": "Unknown native frontend effect."}


func _observe_playback(player: Node) -> void:
	_audio_retirement.observe(player)


func _on_capture_completed() -> void:
	_request_quit(0)


static func _handled(result: Dictionary) -> Dictionary:
	return {"ok": true, "value": true} if result.ok else result


static func _int_list(values: Variant) -> Array[int]:
	var result: Array[int] = []
	for value: Variant in values:
		result.append(int(value))
	return result


static func _report(result: Dictionary, context: String) -> void:
	if not result.ok:
		push_error("%s: %s: %s" % [context, result.get("error_type", "Error"), result.get("error", "")])
