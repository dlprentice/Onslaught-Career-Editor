# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production frontend owner. The authored children are the same pages used by
## the editor and gameplay. Session owns navigation/campaign state; this node
## owns presentation clocks, device events, loading and intro handoff ordering.
## The temporary managed host only marshals its typed events and verified save
## identities. Checked synchronous effects preserve failure and re-entry points.

signal host_state_changed(facts: Dictionary)

const Frontend = preload("res://Client/frontend_session.gd")
const Path = preload("res://Client/frontend_scene_path.gd")
const Pages = preload("res://Scenes/Frontend/frontend_pages.gd")
const Strings = preload("res://Scenes/Frontend/loading_strings.gd")
const Assets = preload("res://Scenes/Frontend/retail_frontend_asset_paths.gd")
const Values = preload("res://Core/retail_career_values.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Click = preload("res://Client/click_to_start_laws.gd")
const CursorQuad = preload("res://Scenes/Frontend/mouse_cursor_quad.gd")
const Startup = preload("res://Scenes/Frontend/startup_sequence.gd")
const Schedule = preload("res://Client/startup_schedule.gd")

enum EditorPreview { CLICK_TO_START, MAIN_MENU, QUIT_CONFIRM, CAREER_NAME,
	LEVEL_SELECT, MISSION_BRIEFING, SELECT_CONFIGURATION, LOADING, OPTIONS, DEBRIEFING }
@export var AssetPaths: Resource = Assets.new()
@export var EditorPage: EditorPreview = EditorPreview.MAIN_MENU:
	set(value):
		EditorPage = value
		if Engine.is_editor_hint() and _initialized:
			var result: Dictionary = set_editor_page()
			if result.ok: result = redraw()
			_report_failure(result)

# Pristine specimen SHA-256 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750,
# VA 0x0051B686: push 0x32 before SetPage(FEP_MAIN). FrontEnd.cpp:563-592,
# 665-675,1291,1431-1438 increment once per Process, first draw count=1.
# The observed retail reveal rate remains unresolved; 50 is a frame count,
# never a duration fitted to a capture. The existing single outgoing-page swap
# remains: visible outgoing Click art is refuted by the measured first frame.
const MAIN_MENU_ENTRY_TRANSITION_FRAMES: int = 50
const LOCALIZATION_PATH: String = "res://Assets/Frontend/english.json"
var _session: Frontend.Session
var _pages: Pages
var _strings: Dictionary = {}
var _fe_back_frames: Array = []
var _stage: Control
var _options_view: Control
var _mouse_cursor: Control
var _intro_cutscene: Control
var _effect_handler: Callable
var _voice_observer: Callable
var _options_settings: Dictionary = {}
var _last_host_facts: Dictionary = {}
var _main_transition_count: int = 0
var _main_transition_time: int = 0
var _animation_seconds: float = 0.0
var _click_pulse_timer: float = 0.0
var _click_page_seconds: float = 0.0
var _fe_back_seconds: float = 0.0
var _last_drawn_screen: int = Frontend.Screen.CLICK_TO_START
var _loading_frames: int = 0
var _initialized: bool = false
var _load_request_raised: bool = false
var _level100_ready: bool = false
var _gameplay_activation_raised: bool = false
var _capture_mouse_cursor_design_position: Variant = null


func set_effect_handler(handler: Callable) -> void:
	_effect_handler = handler


func set_voice_observer(observer: Callable) -> void:
	_voice_observer = observer


func initialize(descriptors: Variant = []) -> Dictionary:
	if _initialized:
		return _failure("The retail frontend is already initialized.")
	if descriptors == null:
		return Values.failure("ArgumentNullException", "Value cannot be null.", "careerDescriptors")
	# A failed retry replaces the Session before localization/asset admission,
	# just as the old owner did. String Dictionary.Add writes are not rolled back.
	_session = null
	var result: Dictionary = Frontend.create(descriptors)
	if not result.ok: return result
	_session = result.value
	result = Strings.admit_incremental(FileAccess.get_file_as_string(LOCALIZATION_PATH), _strings)
	if not result.ok: return result
	var recipe: Resource = load("res://Scenes/Frontend/FrontendUnderlay.tres")
	result = recipe.load_frames(1 if Engine.is_editor_hint() else 2147483647)
	if not result.ok: return _options_result(result)
	if result.missing:
		push_warning("FEBack strip missing at res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb; main underlay uses solid fallback.")
	_fe_back_frames = result.frames
	_pages = Pages.new(self)
	_options_view = get_node("Stage/Options")
	if not Engine.is_editor_hint(): _options_view.set_effect_handler(_dispatch_options_effect)
	result = _pages.configure_options_assets(_fe_back_frames)
	if not result.ok: return result
	result = _apply_options_result(_options_view.configure_host(_describe_host()))
	if not result.ok: return result
	if not Engine.is_editor_hint():
		result = _apply_options_to_host()
		if not result.ok: return result
	result = _pages.configure_remaining(_session, _strings, _fe_back_frames)
	if not result.ok: return result
	_initialized = true
	_publish_host_state()
	return Values.success()


func _ready() -> void:
	if not _initialized:
		var result: Dictionary = initialize([])
		if result.ok and Engine.is_editor_hint(): result = set_editor_page()
		if not result.ok:
			if Engine.is_editor_hint():
				push_warning("Frontend assets unavailable: " + String(result.error))
				set_process(false)
				set_process_input(false)
			else: _report_failure(result)
			return
	_stage = get_node("Stage")
	resized.connect(fit_scene_stage)
	fit_scene_stage()
	if not Engine.is_editor_hint(): set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	z_index = 100
	_mouse_cursor = get_node("MouseCursor")
	_mouse_cursor.visible = not Engine.is_editor_hint()
	if not Engine.is_editor_hint():
		var result: Dictionary = _options_result(_mouse_cursor.configure_live_pointer(self))
		if result.ok: result = _update_mouse_cursor()
		if not result.ok:
			_report_failure(result)
			return
	set_process(not Engine.is_editor_hint())
	set_process_input(not Engine.is_editor_hint())
	_report_failure(redraw())


func _process(delta: float) -> void:
	var result: Dictionary = advance(delta)
	_publish_host_state()
	_report_failure(result)


func advance(delta: float) -> Dictionary:
	if Engine.is_editor_hint(): return Values.success()
	if _session == null: return _failure("The frontend has no initialized Session.")
	# Math.Max(0d, delta) preserves NaN and selects positive zero. min/maxf have
	# different NaN semantics. All these clocks remain binary64.
	var step: float = 0.0 if delta <= 0.0 else delta
	_animation_seconds += step
	if _session.get_screen() == Frontend.Screen.MAIN_MENU and _last_drawn_screen == Frontend.Screen.CLICK_TO_START:
		_main_transition_count = 0
		_main_transition_time = MAIN_MENU_ENTRY_TRANSITION_FRAMES
	if _main_transition_time > 0:
		_main_transition_count = Values.int32(_main_transition_count + 1)
		if _main_transition_count >= _main_transition_time: _main_transition_time = 0
	if _session.get_screen() == Frontend.Screen.CLICK_TO_START:
		if _last_drawn_screen != Frontend.Screen.CLICK_TO_START:
			_click_pulse_timer = 0.0
			_click_page_seconds = 0.0
		_click_page_seconds += step
		_click_pulse_timer = Click.advance(_click_pulse_timer, _click_page_seconds, step)
	elif _session.get_screen() != Frontend.Screen.INTRO_CUTSCENE:
		# FEBack is anchored once on leaving Click, never reset at later pages.
		# RunIntroFMV is outside the retail frontend loop (game.cpp:1336-1345),
		# so its 123.8 s cannot advance this measured underlay phase.
		_fe_back_seconds += step
	_last_drawn_screen = _session.get_screen()
	if _session.get_screen() == Frontend.Screen.LOADING:
		_loading_frames = Values.int32(_loading_frames + 1)
		if not _load_request_raised and _loading_frames >= 2:
			var consumed: Dictionary = _session.consume_level100_launch_request()
			if not consumed.ok: return consumed
			if not consumed.value: return _failure("The Level 100 launch edge was lost.")
			_load_request_raised = true
			var emitted: Dictionary = _dispatch_host({"kind": "level_load_requested"})
			if not emitted.ok: return emitted
		if _level100_ready:
			var intro: Dictionary = _try_begin_level100_intro_cutscene()
			if not intro.ok: return intro
			if not intro.value:
				var completed: Dictionary = Path.try_complete_loading(_session, false, _load_request_raised)
				if not completed.ok: return completed
				if not completed.value:
					return _failure("Level 100 can complete only after its pending launch request is consumed.")
	var activation: Dictionary = _try_raise_gameplay_activation()
	if not activation.ok or activation.value: return activation
	return redraw()


func main_menu_transition() -> float:
	return 1.0 if _main_transition_time <= 0 else minf(1.0, F.value(F.value(_main_transition_count) / F.value(_main_transition_time)))


func _input(event: InputEvent) -> void:
	var result: Dictionary = handle_input(event)
	_publish_host_state()
	_report_failure(result)


func handle_input(event: InputEvent) -> Dictionary:
	if Engine.is_editor_hint(): return Values.success(false)
	if _session == null: return _failure("The frontend has no initialized Session.")
	if _session.get_screen() in [Frontend.Screen.LOADING, Frontend.Screen.INTRO_CUTSCENE, Frontend.Screen.GAMEPLAY]:
		return Values.success(false)
	# FrontEnd.cpp:551-552 drops ButtonPressed throughout FEP_TRANSITION.
	# Render hover is different; its >binary32(0.9) gate is below.
	if _main_transition_time > 0 and not event is InputEventMouseMotion: return Values.success(false)
	var result: Dictionary = Values.success(false)
	if event is InputEventMouseMotion: result = handle_pointer_motion(event.position)
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT: result = handle_pointer_confirm(event.position)
		elif event.button_index == MOUSE_BUTTON_RIGHT: result = handle_pointer_cancel()
	elif event is InputEventKey and event.pressed and not event.echo: result = handle_key(event)
	if result.ok and result.value: get_viewport().set_input_as_handled()
	return result


func handle_pointer_motion(point: Vector2) -> Dictionary:
	var design: Vector2 = to_design_position(point)
	if _session.get_screen() == Frontend.Screen.OPTIONS:
		var moved: Dictionary = _apply_options_result(_options_view.pointer_motion(design))
		return _redraw_handled() if moved.ok and moved.value else moved
	if _session.get_screen() == Frontend.Screen.QUIT_CONFIRM:
		var choice: int = quit_confirm_index_at(design)
		if choice < 0: return Values.success(false)
		return _move_selection(_session.select_quit_confirm_index(choice))
	if _session.get_screen() != Frontend.Screen.MAIN_MENU: return Values.success(false)
	# RetailMainMenuHitTest: pristine 0x004630AC/0x004631EF, threshold word
	# 0x3f666666; cold language hover rect is [119,319) x [248,288).
	if not main_menu_transition() > F.value(0.9): return Values.success(false)
	if design.x >= 119.0 and design.x < 319.0 and design.y >= 248.0 and design.y < 288.0:
		return Values.success(false)
	var index: int = main_menu_index_at(design)
	if index < 0 or not _session.get_items()[index].is_available: return Values.success(false)
	return _move_selection(_session.select_main_index(index))


func handle_pointer_confirm(point: Vector2) -> Dictionary:
	var design: Vector2 = to_design_position(point)
	match _session.get_screen():
		Frontend.Screen.CLICK_TO_START:
			if not Path.accepts_click_to_start_mouse(_session.get_screen(), design.x, design.y): return Values.success(false)
			return _handled(confirm())
		Frontend.Screen.OPTIONS:
			return handle_options_pointer_confirm(design)
		Frontend.Screen.MAIN_MENU:
			var index: int = main_menu_index_at(design)
			var accepted: Dictionary = Path.can_accept_main_menu_row(_session, index)
			if not accepted.ok or not accepted.value: return accepted
			return _select_then_confirm(_session.select_main_index(index))
		Frontend.Screen.QUIT_CONFIRM:
			var choice: int = quit_confirm_index_at(design)
			return Values.success(false) if choice < 0 else _select_then_confirm(_session.select_quit_confirm_index(choice))
		Frontend.Screen.DEV_SELECT:
			return _confirm_page_target(career_name_target_at(design))
		Frontend.Screen.LEVEL_SELECT:
			var target: int = level_select_target_at(design)
			if target == 3:
				var selected: Dictionary = _session.select_world(100)
				if not selected.ok: return selected
				return _handled(confirm())
			if target == 4:
				var selected: Dictionary = _session.select_world(110)
				return _handled(confirm()) if selected.ok and selected.value else selected
			return _confirm_page_target(target)
		Frontend.Screen.DEBRIEFING:
			return _handled(confirm()) if Rect2(0, 0, 640, 480).has_point(design) else Values.success(false)
		Frontend.Screen.MISSION_BRIEFING:
			return _confirm_page_target(briefing_target_at(design))
		Frontend.Screen.SELECT_CONFIGURATION:
			return _confirm_page_target(configuration_target_at(design))
	return Values.success(false)


func handle_pointer_cancel() -> Dictionary:
	return cancel_options() if _session.get_screen() == Frontend.Screen.OPTIONS else Values.success(false)


func _confirm_page_target(target: int) -> Dictionary:
	if target == 1: return _back_page()
	return _handled(confirm()) if target == 2 else Values.success(false)


func _select_then_confirm(selected: Dictionary) -> Dictionary:
	if not selected.ok: return selected
	if selected.value:
		var audio: Dictionary = _audio(Frontend.AudioCue.MOVE)
		if not audio.ok: return audio
	return _handled(confirm())


func _move_selection(selected: Dictionary) -> Dictionary:
	if not selected.ok or not selected.value: return selected
	var audio: Dictionary = _audio(Frontend.AudioCue.MOVE)
	return _redraw_handled() if audio.ok else audio


func handle_key(key: InputEventKey) -> Dictionary:
	if _session.get_screen() == Frontend.Screen.OPTIONS:
		return _apply_options_result(_options_view.handle_key(is_key(key, KEY_UP), is_key(key, KEY_DOWN),
			is_key(key, KEY_LEFT), is_key(key, KEY_RIGHT),
			is_key(key, KEY_ENTER) or is_key(key, KEY_KP_ENTER) or is_key(key, KEY_SPACE), is_key(key, KEY_ESCAPE)))
	if _session.get_screen() == Frontend.Screen.DEV_SELECT and _session.get_career_page_mode() == Frontend.CareerPageMode.NEW:
		if is_key(key, KEY_BACKSPACE):
			var removed: Dictionary = _session.remove_game_name_character()
			if not removed.ok: return removed
			return _redraw_handled() if removed.value else Values.success(true)
		if is_key(key, KEY_LEFT) or is_key(key, KEY_UP) or is_key(key, KEY_RIGHT) or is_key(key, KEY_DOWN):
			var moved: Dictionary = _session.move_game_name_cursor(is_key(key, KEY_RIGHT) or is_key(key, KEY_DOWN))
			return _redraw_handled() if moved.ok else moved
		if is_key(key, KEY_HOME) or is_key(key, KEY_END) or is_key(key, KEY_DELETE): return Values.success(true)
		# Space is text before it is a generic Confirm key. A non-BMP input is
		# consumed without appending; this reproduces the char.MaxValue gate.
		if key.unicode >= 32:
			if key.unicode <= 65535:
				var extent: Dictionary = measure_game_name_extent(_session.get_game_name())
				if not extent.ok: return extent
				var appended: Dictionary = _session.append_game_name_character(key.unicode, extent.value)
				if not appended.ok: return appended
				if appended.value: return _redraw_handled()
			return Values.success(true)
	if _session.get_screen() == Frontend.Screen.QUIT_CONFIRM:
		# 0x0044dd60 YESNO: Up writes Yes=1, Down No=0. Left/Right still
		# follow the Session's ordinary previous/next law.
		if is_key(key, KEY_UP): return _handled(_move_selection(_session.select_quit_confirm_index(1)))
		if is_key(key, KEY_DOWN): return _handled(_move_selection(_session.select_quit_confirm_index(0)))
	if is_key(key, KEY_UP) or is_key(key, KEY_LEFT): return _handled(_move_selection(_session.move_previous()))
	if is_key(key, KEY_DOWN) or is_key(key, KEY_RIGHT): return _handled(_move_selection(_session.move_next()))
	if is_key(key, KEY_ENTER) or is_key(key, KEY_KP_ENTER) or is_key(key, KEY_SPACE):
		if _session.get_screen() == Frontend.Screen.CLICK_TO_START and not Path.accepts_click_to_start_key(_session.get_screen(), scan_code_for(key)):
			return Values.success(true)
		return _handled(confirm())
	if is_key(key, KEY_ESCAPE): return _handled(_back_page())
	return Values.success(false)


func confirm() -> Dictionary:
	var accepted: Dictionary = Path.try_confirm_page(_session, false)
	if not accepted.ok or not accepted.value: return accepted
	if _session.get_screen() == Frontend.Screen.OPTIONS:
		var reset: Dictionary = _apply_options_result(_options_view.reset_menu())
		if not reset.ok: return reset
	var audio: Dictionary = _audio(Frontend.AudioCue.SELECT)
	if not audio.ok: return audio
	var navigation: Dictionary = _handle_navigation_signal(accepted.signal)
	if not navigation.ok: return navigation
	if accepted.signal == Frontend.FrontendSignal.EXIT_REQUESTED:
		var exited: Dictionary = _dispatch_host({"kind": "exit"})
		if not exited.ok: return exited
	return redraw()


func _back_page() -> Dictionary:
	var accepted: Dictionary = Path.try_back_page(_session, false)
	if not accepted.ok or not accepted.value: return accepted
	var audio: Dictionary = _audio(Frontend.AudioCue.BACK)
	if not audio.ok: return audio
	var navigation: Dictionary = _handle_navigation_signal(accepted.signal)
	return _redraw_handled() if navigation.ok else navigation


func _handle_navigation_signal(signal_id: int) -> Dictionary:
	match signal_id:
		Frontend.FrontendSignal.LEVEL_LAUNCH_REQUESTED:
			_load_request_raised = false
			_level100_ready = false
			_gameplay_activation_raised = false
			_loading_frames = 0
			var started: Dictionary = _dispatch_host({"kind": "level_loading_started"})
			return _cursor_mode(Frontend.CursorMode.HIDDEN) if started.ok else started
		Frontend.FrontendSignal.RETURN_TO_MAIN_MENU_REQUESTED:
			var cursor: Dictionary = _cursor_mode(Frontend.CursorMode.CUSTOM)
			return _dispatch_host({"kind": "return_main_menu"}) if cursor.ok else cursor
		Frontend.FrontendSignal.CAREER_LOAD_REQUESTED:
			var selected: Dictionary = _session.consume_selected_career_load_request_index()
			if not selected.ok: return selected
			if selected.value == null: return _failure("CareerLoadRequested did not carry a selected career descriptor.")
			var loaded: Dictionary = _dispatch_host({"kind": "career_selected", "index": selected.value})
			return _cursor_mode(Frontend.CursorMode.CUSTOM) if loaded.ok else loaded
		Frontend.FrontendSignal.PAGE_CHANGED:
			return _cursor_mode(Frontend.CursorMode.CUSTOM)
	return Values.success()


func mark_level100_ready() -> Dictionary:
	if not _load_request_raised or _session.get_screen() != Frontend.Screen.LOADING:
		return _failure("Level 100 was marked ready outside the frontend loading seam.")
	_level100_ready = true
	return Values.success()


func restart_level100() -> Dictionary:
	var origin: int = _session.get_screen()
	var restarted: Dictionary = _session.restart_level100()
	if not restarted.ok: return restarted
	var resumed: Dictionary = _resume_frontend_for_navigation(origin)
	if not resumed.ok: return resumed
	var navigation: Dictionary = _handle_navigation_signal(restarted.value)
	return redraw() if navigation.ok else navigation


func leave_level100_for_main_menu() -> Dictionary:
	var origin: int = _session.get_screen()
	var left: Dictionary = _session.leave_level100_for_main_menu()
	if not left.ok: return left
	var resumed: Dictionary = _resume_frontend_for_navigation(origin)
	if not resumed.ok: return resumed
	var navigation: Dictionary = _handle_navigation_signal(left.value)
	return redraw() if navigation.ok else navigation


func accept_won_handoff(outcome: int, terminal: int) -> Dictionary:
	var origin: int = _session.get_screen()
	var accepted: Dictionary = Path.try_accept_won_handoff(_session, outcome, terminal)
	if not accepted.ok or not accepted.value: return accepted
	var resumed: Dictionary = _resume_frontend_for_navigation(origin)
	if not resumed.ok: return resumed
	var navigation: Dictionary = _handle_navigation_signal(Frontend.FrontendSignal.PAGE_CHANGED)
	if not navigation.ok: return navigation
	var returned: Dictionary = _dispatch_host({"kind": "return_main_menu"})
	return redraw() if returned.ok else returned


func return_unconstructible_launch_to_level_select() -> Dictionary:
	var returned: Dictionary = _session.return_unconstructible_launch_to_level_select()
	if not returned.ok: return returned
	if not returned.value: return _failure("An unconstructible launch can return only after its request was consumed.")
	_load_request_raised = false
	_level100_ready = false
	_loading_frames = 0
	return redraw()


func _resume_frontend_for_navigation(origin: int) -> Dictionary:
	if origin == Frontend.Screen.GAMEPLAY:
		var suspended: Dictionary = _dispatch_host({"kind": "gameplay_suspended"})
		if not suspended.ok: return suspended
	visible = true
	set_process_input(true)
	set_process(true)
	return redraw()


func suspend_for_startup_media() -> Dictionary:
	visible = false
	set_process(false)
	set_process_input(false)
	return Values.success()


func resume_after_startup_media() -> Dictionary:
	_animation_seconds = 0.0
	_click_pulse_timer = 0.0
	_click_page_seconds = 0.0
	visible = true
	set_process(true)
	set_process_input(true)
	return redraw()


func _try_raise_gameplay_activation() -> Dictionary:
	if _session.get_screen() != Frontend.Screen.GAMEPLAY or _gameplay_activation_raised: return Values.success(false)
	_gameplay_activation_raised = true
	visible = false
	set_process_input(false)
	set_process(false)
	var cursor: Dictionary = _cursor_mode(Frontend.CursorMode.CAPTURED)
	return _handled(_dispatch_host({"kind": "gameplay_activated"})) if cursor.ok else cursor


func _try_begin_level100_intro_cutscene() -> Dictionary:
	if not _session.get_level100_intro_cutscene_pending(): return Values.success(false)
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	var suppressed: Dictionary = Schedule.is_suppressed_by_arguments(arguments)
	if not suppressed.ok: return suppressed
	if suppressed.value: return Values.success(false)
	var sequence: Control = load("res://Scenes/Frontend/Startup.tscn").instantiate()
	sequence.name = "Level100IntroCutscene"
	var configured: Dictionary = sequence.configure_from_cache(Startup.resolve_media_root(arguments),
		Startup.Route.SINGLE_CLIP, Schedule.Cue.LEVEL100_INTRO_CUTSCENE,
		Startup.Clock.FIXED_TICK if is_capture_run(arguments) else Startup.Clock.WALL, _voice_observer)
	if not configured.ok:
		sequence.queue_free()
		return _failure(configured.error)
	if sequence.get_scheduled_seconds() <= 0.0:
		var reason: String = sequence.get_media_unavailable_reason()
		push_warning("The Level 100 intro cutscene (data/video/cutscenes/01.vid) is not decoded, so it does not play. Run " +
			"`python ./rebuild/tools/materialize_retail_assets.py --startup-media`. " +
			("The cue had no decoded media." if reason.is_empty() else reason))
		sequence.queue_free()
		return Values.success(false)
	var begun: Dictionary = _session.begin_level100_intro_cutscene()
	if not begun.ok:
		sequence.queue_free()
		return begun
	sequence.completed.connect(_on_intro_finished)
	_intro_cutscene = sequence
	add_child(sequence)
	return _handled(redraw())


func _on_intro_finished() -> void:
	var result: Dictionary = finish_level100_intro_cutscene()
	_publish_host_state()
	_report_failure(result)


func finish_level100_intro_cutscene() -> Dictionary:
	if _session.get_screen() != Frontend.Screen.INTRO_CUTSCENE: return Values.success()
	var completed: Dictionary = Path.try_complete_intro_cutscene(_session, false)
	if not completed.ok or not completed.value: return completed
	if is_instance_valid(_intro_cutscene): _intro_cutscene.queue_free()
	_intro_cutscene = null
	# The child completes after its parent's Process. Activate inside this same
	# callback, before another frame can observe Gameplay without a live world.
	var activation: Dictionary = _try_raise_gameplay_activation()
	return redraw() if activation.ok and not activation.value else activation


func select_main_index(index: int) -> Dictionary:
	var selected: Dictionary = _session.select_main_index(index)
	return redraw() if selected.ok else selected


func select_options_row(index: int) -> Dictionary:
	var selected: Dictionary = _apply_options_result(_options_view.select_row(index))
	return redraw() if selected.ok else selected


func confirm_options() -> Dictionary:
	return _apply_options_result(_options_view.handle_key(false, false, false, false, true, false))


func back_from_options() -> Dictionary:
	return _apply_options_result(_options_view.handle_key(false, false, false, false, false, true))


func cancel_options() -> Dictionary:
	return _apply_options_result(_options_view.pointer_cancel(true))


func handle_options_pointer_confirm(design: Vector2) -> Dictionary:
	return _apply_options_result(_options_view.pointer_confirm(design))


func _apply_options_result(result: Dictionary) -> Dictionary:
	if result.has("settings"): _options_settings = result.settings.duplicate(true)
	# The original host exception token must survive mapping. Effects have
	# already run at their source points and must never be replayed here.
	return _options_result(result)


func _dispatch_options_effect(effect: Dictionary, settings: Dictionary) -> Dictionary:
	_options_settings = settings.duplicate(true)
	match effect.kind:
		"audio": return _audio(effect.cue)
		"apply_settings": return _apply_options_to_host()
		"redraw": return redraw()
		"frontend_back": return _back_page()
	return Values.failure("InvalidDataException", "Unknown native options effect.")


func _apply_options_to_host() -> Dictionary:
	if Engine.is_editor_hint(): return Values.success()
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if _options_settings.v_sync else DisplayServer.VSYNC_DISABLED)
	return _dispatch_host({"kind": "apply_settings"})


static func _describe_host() -> Dictionary:
	var window: Vector2i = DisplayServer.window_get_size()
	var adapter: String = RenderingServer.get_video_adapter_name()
	# Existing admitted device inventory/recommendation gap; no new guessed D3D,
	# sound device, screen mode or binding recommendation is introduced.
	return {"screen_modes": ["%d x %d" % [window.x, window.y]],
		"video_adapters": ["Unknown" if Text.is_null_or_white_space(Text.units(adapter).value) else adapter],
		"anti_aliasing_levels": ["None"], "sound_devices": ["Primary Sound Driver"],
		"recommended_texture_resolution": 0, "recommended_enable32_bit_textures": 2}


func host_snapshot() -> Dictionary:
	return {"screen": Frontend.Screen.CLICK_TO_START if _session == null else _session.get_screen(),
		"launch_world_number": 100 if _session == null else _session.get_consume_launch_world_number(),
		"selected_world_is_constructible": true if _session == null else _session.get_selected_world_is_constructible(),
		"options_settings": _options_settings.duplicate(true)}


func _publish_host_state() -> void:
	if Engine.is_editor_hint(): return
	var facts: Dictionary = host_snapshot()
	if facts == _last_host_facts: return
	_last_host_facts = facts.duplicate(true)
	host_state_changed.emit(facts)


func _dispatch_host(effect: Dictionary) -> Dictionary:
	if Engine.is_editor_hint(): return Values.success()
	_publish_host_state()
	if not _effect_handler.is_valid(): return Values.success()
	var result: Variant = _effect_handler.call(effect, host_snapshot())
	if not result is Dictionary or typeof(result.get("ok")) != TYPE_BOOL:
		return Values.failure("InvalidDataException", "Frontend effect handler returned no completion result.")
	return result


func _audio(cue: int) -> Dictionary:
	return _dispatch_host({"kind": "audio", "cue": cue})


func _cursor_mode(mode: int) -> Dictionary:
	return _dispatch_host({"kind": "cursor_mode", "mode": mode})


func fit_scene_stage() -> void:
	if _stage == null: return
	var pose: Transform2D = CursorQuad.stage_fit(size)
	_stage.position = pose.origin
	_stage.scale = Vector2(pose.x.x, pose.x.x)


func to_design_position(point: Vector2) -> Vector2:
	return CursorQuad.to_design_position(point, size)


func main_menu_index_at(design: Vector2) -> int:
	return -1 if _stage == null else get_node("Stage/MainMenu").hit_test(_stage.get_global_transform_with_canvas() * design)


func quit_confirm_index_at(design: Vector2) -> int:
	return get_node("Stage/QuitConfirm").hit_test(design)


func career_name_target_at(design: Vector2) -> int:
	return get_node("Stage/CareerName").hit_test(design)


func level_select_target_at(design: Vector2) -> int:
	return get_node("Stage/LevelSelect").hit_test(design)


func briefing_target_at(design: Vector2) -> int:
	return get_node("Stage/MissionBriefing").hit_test(design)


func configuration_target_at(design: Vector2) -> int:
	return get_node("Stage/SelectConfiguration").hit_test(design)


func measure_game_name_extent(units: Variant) -> Dictionary:
	if units == null: return Values.failure("ArgumentNullException", "Value cannot be null.", "source")
	return Values.success(get_node("Stage/CareerName").measure_name_extent(units))


func update_career_name_frame() -> Dictionary:
	var page: Control = get_node("Stage/CareerName")
	if not page.visible: return Values.success()
	return _pages._update_career(_session, {"background_seconds": _fe_back_seconds}, Engine.is_editor_hint())


func set_mouse_cursor_design_position_for_capture(point: Variant) -> Dictionary:
	_capture_mouse_cursor_design_position = point
	return _update_mouse_cursor()


func _update_mouse_cursor() -> Dictionary:
	if _mouse_cursor == null or Engine.is_editor_hint(): return Values.success()
	return _options_result(_mouse_cursor.set_frame({"screen": _session.get_screen(),
		"cursor_position": _capture_mouse_cursor_design_position}))


func redraw() -> Dictionary:
	queue_redraw()
	# A load observer can synchronously reject its world and redraw without any
	# further navigation effect. Publish that result now, not on a later settled
	# frame. Unchanged animation frames still emit no cross-language notification.
	_publish_host_state()
	if _stage == null or not _initialized: return Values.success()
	return _pages.redraw(_session, {"transition": main_menu_transition(),
		"animation_seconds": _animation_seconds, "background_seconds": _fe_back_seconds,
		"click_pulse_timer": _click_pulse_timer, "click_page_seconds": _click_page_seconds,
		"loading_frames": _loading_frames, "launch_requested": _load_request_raised, "ready": _level100_ready,
		"cursor_initialized": _mouse_cursor != null, "cursor_position": _capture_mouse_cursor_design_position},
		EditorPage if Engine.is_editor_hint() else -1)


func set_editor_page() -> Dictionary:
	# Frozen in-memory navigation only. No careers, host callback, pointer,
	# playback, original saves or gameplay simulation run in the editor.
	_session = Frontend.create().value
	_click_pulse_timer = 5.0
	_click_page_seconds = 5.0
	_animation_seconds = 0.0
	_fe_back_seconds = 0.0
	_main_transition_count = 0
	_main_transition_time = 0
	if EditorPage in [EditorPreview.CLICK_TO_START, EditorPreview.DEBRIEFING]: return Values.success()
	var result: Dictionary = _session.confirm()
	if not result.ok or EditorPage == EditorPreview.MAIN_MENU: return result
	if EditorPage in [EditorPreview.QUIT_CONFIRM, EditorPreview.OPTIONS]:
		result = _session.select_main_index(6 if EditorPage == EditorPreview.QUIT_CONFIRM else 5)
		return _session.confirm() if result.ok else result
	for page: int in [EditorPreview.CAREER_NAME, EditorPreview.LEVEL_SELECT, EditorPreview.MISSION_BRIEFING,
			EditorPreview.SELECT_CONFIGURATION]:
		result = _session.confirm()
		if not result.ok or EditorPage == page: return result
	return _session.confirm()


static func is_key(event: InputEventKey, key: Key) -> bool:
	return event.physical_keycode == key or event.keycode == key


static func scan_code_for(event: InputEventKey) -> int:
	match event.physical_keycode if event.physical_keycode != KEY_NONE else event.keycode:
		KEY_SPACE: return 0x39
		KEY_ENTER: return 0x1c
		KEY_ESCAPE: return 0x01
		KEY_KP_ENTER: return 0x9c
	return 0


static func is_capture_run(arguments: PackedStringArray) -> bool:
	for argument: String in arguments:
		for prefix: String in ["--capture-dir=", "--capture-plan=", "--capture-size=", "--capture-offsets-ms="]:
			if argument.begins_with(prefix): return true
	return false


func _redraw_handled() -> Dictionary:
	return _handled(redraw())


static func _handled(result: Dictionary) -> Dictionary:
	return Values.success(true) if result.ok else result


static func _options_result(result: Dictionary) -> Dictionary:
	if result.get("ok", false):
		return Values.success(result.get("value", false) == true)
	if result.has("host_exception_id"): return result
	var kind: String = result.get("error_type", "InvalidOperationException")
	if kind not in ["ArgumentOutOfRangeException", "ArgumentNullException", "ArgumentException", "NullReferenceException"]:
		kind = "InvalidOperationException"
	return Values.failure(kind, result.get("error", "Native options operation failed."), result.get("parameter", ""))


static func _failure(message: String) -> Dictionary:
	return Values.failure("InvalidOperationException", message)


static func _report_failure(result: Dictionary) -> void:
	if not result.ok:
		# Stop this engine callback at its failure, while retaining writes already
		# made and leaving later frames eligible, as with the former C# exception.
		push_error("Frontend: " + String(result.get("error_type", "Error")) + ": " + String(result.error))
