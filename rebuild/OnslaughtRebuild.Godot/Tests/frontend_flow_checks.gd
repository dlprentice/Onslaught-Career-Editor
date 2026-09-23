# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual native root checks against RetailFrontendFlow at 02cc3dfb: process
## counts/input gates, media-route precedence and failed initialization writes.
## No gameplay world, synthetic Won, media launch or filesystem writes.
const Frontend = preload("res://Client/frontend_session.gd")
const Startup = preload("res://Scenes/Frontend/startup_sequence.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Text = preload("res://Core/canonical_json_string.gd")
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _parity_gaps: Array[Dictionary] = []


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	if not OS.get_cmdline_user_args().has("--skipfmv") or Engine.is_editor_hint():
		printerr("frontend_flow_checks requires standard headless runtime with --skipfmv")
		quit(2)
		return
	var pointer: int = Input.mouse_mode
	_check_media_routes()
	_check_failed_initialization()
	await _check_native_timing()
	_check(Input.mouse_mode == pointer, "The native harness never changes pointer mode.")
	print("FRONTEND_FLOW_CHECKS: ", JSON.stringify({"schema": 1, "checks": _checks,
		"failure_count": _failures.size(), "failures": _failures, "completed": _completed,
		"parity_gaps": _parity_gaps}))
	quit(0 if _failures.is_empty() and _completed.size() == 3 else 1)


func _check_media_routes() -> void:
	var saved: Dictionary = {}
	for name: String in ["ONSLAUGHT_STARTUP_MEDIA", "BEA_LOCAL_LAB", "LOCALAPPDATA"]:
		saved[name] = {"exists": OS.has_environment(name), "value": OS.get_environment(name)}
		OS.unset_environment(name)
	_check(Startup.resolve_media_root([]) == "", "No configured media owner resolves to an empty route.")
	OS.set_environment("ONSLAUGHT_STARTUP_MEDIA", "/chosen")
	OS.set_environment("BEA_LOCAL_LAB", "/canonical//")
	OS.set_environment("LOCALAPPDATA", "/local//")
	_check(Startup.resolve_media_root(["--startup-media=first", "--startup-media=second"]) == "first", "The first exact media argument wins.")
	_check(Startup.resolve_media_root(["--startup-media=", "--startup-media=second"]) == "", "An explicit empty first argument suppresses environment fallback.")
	_check(Startup.resolve_media_root(["--startup-media"]) == "/chosen", "An argument without equals is ignored; ONSLAUGHT wins over both fallback owners.")
	OS.set_environment("ONSLAUGHT_STARTUP_MEDIA", String.chr(0xa0))
	_check(Startup.resolve_media_root([]) == "/canonical//startup-media", "NBSP is .NET whitespace; canonical lab and repeated separators survive.")
	OS.set_environment("ONSLAUGHT_STARTUP_MEDIA", String.chr(0xfeff))
	var bom: String = String.chr(0xfeff)
	_check(not Text.is_null_or_white_space(Text.units(bom).value), "BOM is not .NET whitespace.")
	_check(Startup.resolve_media_root(["--startup-media=" + bom]) == bom
		and Startup.resolve_media_root(["--startup-media=" + bom + "route"]) == bom + "route",
		"Explicit prefixed media arguments retain a leading BOM, including a BOM-only value.")
	var observed: String = Startup.resolve_media_root([])
	if observed != bom:
		# Keep the original .NET expectation visible: this is an engine API gap,
		# not equivalent routing. Pinned Linux OS.get_environment strips the BOM.
		_parity_gaps.append({"boundary": "environment_leading_bom", "expected_utf8": Array(bom.to_utf8_buffer()),
			"observed_utf8": Array(observed.to_utf8_buffer())})
	OS.set_environment("ONSLAUGHT_STARTUP_MEDIA", "  selected  ")
	_check(Startup.resolve_media_root([]) == "  selected  ", "Nonempty configured media paths are not trimmed.")
	OS.set_environment("ONSLAUGHT_STARTUP_MEDIA", " \t\n")
	OS.set_environment("BEA_LOCAL_LAB", String.chr(0xa0))
	_check(Startup.resolve_media_root([]) == "/local//OnslaughtToolkit/startup-media", "LOCALAPPDATA follows two whitespace-only higher priorities without normalizing separators.")
	if OS.get_name() != "Windows":
		OS.set_environment("BEA_LOCAL_LAB", "lab\\literal\\")
		_check(Startup.resolve_media_root([]) == "lab\\literal\\/startup-media", "Unix Path.Combine keeps a literal trailing backslash and adds its slash.")
		OS.unset_environment("BEA_LOCAL_LAB")
		OS.set_environment("LOCALAPPDATA", "local\\literal\\")
		_check(Startup.resolve_media_root([]) == "local\\literal\\/OnslaughtToolkit/startup-media", "Both LOCALAPPDATA combines preserve literal Unix backslashes.")
	OS.unset_environment("BEA_LOCAL_LAB")
	OS.set_environment("LOCALAPPDATA", String.chr(0xa0))
	_check(Startup.resolve_media_root([]) == "", "Whitespace-only LOCALAPPDATA does not invent a media root.")
	for name: String in saved:
		if saved[name].exists: OS.set_environment(name, saved[name].value)
		else: OS.unset_environment(name)
	for name: String in saved:
		_check(OS.has_environment(name) == saved[name].exists and OS.get_environment(name) == saved[name].value,
			"Process-local media environment is restored before production initialization.")
	_done("media_root_precedence")


func _check_failed_initialization() -> void:
	var view: Control = load("res://Scenes/Frontend/Frontend.tscn").instantiate()
	var assets: Resource = view.AssetPaths
	var effects: Array[String] = []
	view.set_effect_handler(func(effect: Dictionary, _facts: Dictionary) -> Dictionary:
		effects.append(effect.kind)
		if effect.kind == "apply_settings": view.AssetPaths = null
		return {"ok": true})
	var failed: Dictionary = view.initialize([])
	_check(not failed.ok and failed.error_type == "NullReferenceException", "An Options callback can null AssetPaths before the next Click route is resolved.")
	_check(effects == ["apply_settings"] and not view.get("_initialized"), "The first failed initialization stops after the existing settings effect.")
	_check(view.get_node("Stage/Options").get("_host_configured")
		and not view.get_node("Stage/ClickToStart").get("_assets_configured"), "Options host setup survives while Click assets have not been configured.")
	var strings: Dictionary = view.get("_strings").duplicate(true)
	var settings: Dictionary = view.host_snapshot().options_settings
	_check(strings.size() == 10 and not settings.is_empty(), "Localization and Options settings written before the callback remain observable.")
	var first_session: RefCounted = view.get("_session")
	view.AssetPaths = assets
	var retry: Dictionary = view.initialize([])
	_check(not retry.ok and retry.error_type == "ArgumentException"
		and retry.error == "An item with the same key has already been added. Key: NewGame", "Retry encounters the original first Dictionary.Add duplicate before asset setup.")
	_check(view.get("_session") != first_session and view.get("_strings") == strings
		and view.host_snapshot().options_settings == settings and effects.size() == 1,
		"Retry replaces only its Session before refusing localization; prior strings/settings/effects are preserved.")
	view.set_effect_handler(Callable())
	view.free()
	_done("initialization_failure_and_retry")


func _check_native_timing() -> void:
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640, 480)
	viewport.disable_3d = true
	root.add_child(viewport)
	var view: Control = load("res://Scenes/Frontend/Frontend.tscn").instantiate()
	var notifications: Array[int] = [0]
	view.host_state_changed.connect(func(_facts: Dictionary) -> void: notifications[0] += 1)
	view.set_mouse_cursor_design_position_for_capture(Vector2.ZERO)
	viewport.add_child(view)
	view.set_process(false)
	view.set_process_input(false)
	_check(view.get_script().resource_path == "res://Scenes/Frontend/frontend_flow.gd"
		and view.get("_session") is Frontend.Session and view.get("_initialized"), "The real production scene owns its native Session in standard Godot.")
	var session: Frontend.Session = view.get("_session")
	_check(view.advance(1.0).ok and view.get("_click_page_seconds") == 1.0 and view.get("_click_pulse_timer") == 0.0,
		"Click's timer remains zero at exactly one second.")
	_check(view.advance(-7.0).ok and view.get("_animation_seconds") == 1.0 and view.get("_click_page_seconds") == 1.0,
		"Negative delta does not advance either binary64 clock.")
	var seed: float = PackedByteArray([0xac, 0xc5, 0x27, 0x37]).decode_float(0)
	_check(view.advance(0.125).ok and view.get("_click_page_seconds") == 1.125
		and view.get("_click_pulse_timer") == seed + 0.25 and view.get("_fe_back_seconds") == 0.0,
		"Crossing one second seeds the measured binary32 value before adding twice the binary64 step.")
	_check(view.confirm().ok and session.get_screen() == Frontend.Screen.MAIN_MENU, "The same Session leaves Click through the checked production command.")
	var row: Control = view.get_node("Stage/MainMenu/LoadGame")
	var point: Vector2 = view.get_global_transform_with_canvas().affine_inverse() * (row.get_global_transform_with_canvas() * (row.size * 0.5))
	_check(view.main_menu_index_at(point) == 2, "Motion fixture hits the authored available Load Game row.")
	var key := InputEventKey.new()
	key.pressed = true
	key.keycode = KEY_DOWN
	var button := InputEventMouseButton.new()
	button.pressed = true
	button.button_index = MOUSE_BUTTON_LEFT
	button.position = point
	var motion := InputEventMouseMotion.new()
	motion.position = point
	var all_swallowed: bool = true
	var all_advanced: bool = true
	for frame: int in range(1, 51):
		all_advanced = view.advance(0.0).ok and all_advanced
		if frame == 1:
			_check(view.get("_main_transition_count") == 1 and view.get("_main_transition_time") == 50
				and view.get_node("Stage/MainMenu").view_snapshot().transition == F.value(1.0 / 50.0), "The first Process draw carries count one, not zero.")
		if frame < 50:
			for event: InputEvent in [key, button]:
				var result: Dictionary = view.handle_input(event)
				all_swallowed = result.ok and not result.value and all_swallowed
		if frame == 45:
			var blocked: Dictionary = view.handle_input(motion)
			_check(blocked.ok and not blocked.value and session.get_selected_main_index() == 0,
				"Motion at exactly binary32 0.9 remains blocked.")
		if frame == 46:
			var accepted: Dictionary = view.handle_input(motion)
			_check(accepted.ok and accepted.value and session.get_selected_main_index() == 2,
				"Motion above binary32 0.9 selects its row before button presses are admitted.")
		if frame == 49: _check(view.get("_main_transition_time") == 50, "Transition remains active through Process call 49.")
	_check(all_advanced and all_swallowed and view.get("_main_transition_count") == 50
		and view.get("_main_transition_time") == 0 and view.main_menu_transition() == 1.0,
		"Exactly 50 Process calls complete transition; keys and mouse buttons were swallowed throughout the preceding 49.")
	_check(view.handle_input(key).value and session.get_selected_main_index() == 3, "The first settled key reaches normal navigation.")
	var published: int = notifications[0]
	for unused: int in range(5): view._process(0.125)
	_check(notifications[0] == published and view.get("_fe_back_seconds") == 0.625
		and view.get("_click_page_seconds") == 1.125 and view.get("_session") == session,
		"Settled animation advances its shared background without host-state notifications, Click clock changes or another Session.")
	viewport.queue_free()
	await process_frame
	await process_frame
	_done("native_owner_clocks_and_input")


func _check(condition: bool, message: String) -> void:
	_checks += 1
	if not condition:
		_failures.append(message)
		push_error(message)


func _done(group: String) -> void:
	_completed.append(group)
	print("FRONTEND_FLOW_SECTION: ", group)
