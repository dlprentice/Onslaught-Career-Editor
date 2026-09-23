# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends RefCounted
## Page binding/configuration and redraw from RetailFrontendFlow's presentation
## partials at 02cc3dfb. The caller owns its one Session, clocks, Options effects,
## loading handoff and pointer-source initialization. This helper only supplies
## display batches to the same authored scenes used by editor previews.

const Frontend = preload("res://Client/frontend_session.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const Values = preload("res://Core/retail_career_values.gd")
const MENU_KEYS: Array[String] = ["newGame", "continueGame", "loadGame", "multiplayer", "goodies", "options", "quit"]
const EDITOR_MAIN_MENU: int = 1
const EDITOR_DEBRIEFING: int = 9
const STAGE_ROUTES: Array = [["rock", "Frontend", "Backgrounds/rock"],
	["ring", "Frontend", "level-bracket-02"], ["arrow", "Frontend", "fe-arrow"]]

var _root: Control
var _stage: Control
var _options: Control
var _click: Control
var _main: Control
var _quit: Control
var _career: Control
var _level: Control
var _briefing: Control
var _configuration: Control
var _loading: Control
var _debriefing: Control
var _menu_labels: Dictionary = {}
var _loading_caption: PackedInt32Array = PackedInt32Array()


func _init(frontend_root: Control) -> void:
	_root = frontend_root
	_stage = _root.get_node("Stage") as Control


## Root installs its effect handler first, then calls this, then configures the
## Options host/settings before configure_remaining. Do not move those effects
## after the remaining asset reads: their existing failure/reentry order matters.
func configure_options_assets(frames: Array) -> Dictionary:
	_options = _root.get_node("Stage/Options") as Control
	var paths: Dictionary = _paths([["body_font", "Hud", "font-13ps"], ["title_font", "Hud", "font-22"],
		["system_font", "Frontend", "system-font"], ["bracket", "Frontend", "level-bracket-01"],
		["arrow", "Frontend", "fe-arrow"]])
	if not paths.ok: return paths
	return _options_result(_options.configure_assets(paths.value, frames))


## strings is the caller's already-admitted localization table, with the original
## JSON keys and raw UTF-16 values. Keep route admission sequential, preserving
## successful earlier page work if a later page refuses its assets.
func configure_remaining(session: Frontend.Session, strings: Dictionary, frames: Array) -> Dictionary:
	var result: Dictionary = _configure_click()
	if not result.ok: return result
	result = _configure_main(session, strings)
	if not result.ok: return result
	result = _configure_quit()
	if not result.ok: return result
	result = _configure_career(frames)
	if not result.ok: return result
	result = _configure_level(strings, frames)
	if not result.ok: return result
	result = _configure_briefing()
	if not result.ok: return result
	result = _configure_configuration()
	if not result.ok: return result
	result = _configure_loading(strings)
	if not result.ok: return result
	return _configure_debriefing(frames)


func _configure_click() -> Dictionary:
	_click = _root.get_node("Stage/ClickToStart") as Control
	var paths: Dictionary = _paths([["splash", "Frontend", "Backgrounds/click-to-start"],
		["slide", "Frontend", "click-slide"], ["title", "Frontend", "title-logo"]], true)
	if not paths.ok: return paths
	return _page_result(_click.configure_assets(paths.value, _options.body_font), "Click page")


func _configure_main(session: Frontend.Session, strings: Dictionary) -> Dictionary:
	_main = _root.get_node("Stage/MainMenu") as Control
	var routes: Array = []
	for name: String in ["forseti-writing-large", "fe-arrow", "title-text-box", "title-bracket-01", "title-bracket-02",
			"symbol-bracket-01", "symbol-bracket-02", "title-logo", "reflection-map",
			"Flags/flag-uk", "Flags/flag-fr", "Flags/flag-gr", "Flags/flag-it", "Flags/flag-sp",
			"Icons/new-game", "Icons/continue-game", "Icons/load-game", "Icons/multiplayer",
			"Icons/goodies", "Icons/options", "Icons/quit"]:
		routes.append(["Frontend/" + name, "Frontend", name])
	var paths: Dictionary = _paths(routes, true)
	if not paths.ok: return paths
	var labels: Array = []
	for item: Dictionary in session.get_items():
		var units: PackedInt32Array = strings[MENU_KEYS[item.kind]].duplicate()
		_menu_labels[item.kind] = units
		labels.append(units)
	var underlay: Resource = load("res://Scenes/Frontend/FrontendUnderlay.tres")
	return _page_result(_main.configure_assets(paths.value, _options.body_font, underlay, labels), "Main Menu")


func _configure_quit() -> Dictionary:
	_quit = _root.get_node("Stage/QuitConfirm") as Control
	var paths: Dictionary = _paths([["blank", "PauseMenu", "blank"]])
	if not paths.ok: return paths
	return _page_result(_quit.configure_assets(paths.value, _options.body_font, _options.title_font), "quit confirmation")


func _configure_career(frames: Array) -> Dictionary:
	_career = _root.get_node("Stage/CareerName") as Control
	var paths: Dictionary = _paths([["bracket", "Frontend", "level-bracket-01"], ["arrow", "Frontend", "fe-arrow"]])
	if not paths.ok: return paths
	return _page_result(_career.configure_assets(paths.value, _fonts(), frames), "career-name presentation")


func _configure_level(strings: Dictionary, frames: Array) -> Dictionary:
	_level = _root.get_node("Stage/LevelSelect") as Control
	var paths: Dictionary = _paths([["bracket", "Frontend", "level-bracket-01"],
		["ring_outer", "Frontend", "level-ring-01"], ["ring_inner", "Frontend", "level-ring-02"],
		["arrow", "Frontend", "fe-arrow"]])
	if not paths.ok: return paths
	return _page_result(_level.configure_assets(paths.value, _fonts(), frames, strings.selectLevel), "level-select presentation")


func _configure_briefing() -> Dictionary:
	_briefing = _root.get_node("Stage/MissionBriefing") as Control
	var paths: Dictionary = _paths(STAGE_ROUTES)
	if not paths.ok: return paths
	return _page_result(_briefing.configure_assets(paths.value, _fonts()), "briefing presentation")


func _configure_configuration() -> Dictionary:
	_configuration = _root.get_node("Stage/SelectConfiguration") as Control
	var paths: Dictionary = _paths(STAGE_ROUTES)
	if not paths.ok: return paths
	return _page_result(_configuration.configure_assets(paths.value, _fonts()), "configuration presentation")


func _configure_loading(strings: Dictionary) -> Dictionary:
	_loading = _root.get_node("Stage/Loading") as Control
	_loading_caption = strings.loading.duplicate()
	var paths: Dictionary = _paths([["background", "Frontend", "loading-screen"]], true)
	if not paths.ok: return paths
	return _loading_result(_loading.configure_assets(paths.value, _options.title_font, _loading_caption), true)


func _configure_debriefing(frames: Array) -> Dictionary:
	_debriefing = _root.get_node("Stage/Debriefing") as Control
	var paths: Dictionary = _paths([["metal_ring", "Frontend", "Debriefing/metal-ring-transition"],
		["writing", "Frontend", "forseti-writing-large"], ["symbol_bracket", "Frontend", "symbol-bracket-01"],
		["grade_a", "Frontend", "Debriefing/ranking-a"], ["grade_b", "Frontend", "Debriefing/ranking-b"],
		["grade_c", "Frontend", "Debriefing/ranking-c"], ["grade_d", "Frontend", "Debriefing/ranking-d"],
		["grade_e", "Frontend", "Debriefing/ranking-e"], ["grade_s", "Frontend", "Debriefing/ranking-s"]], true)
	if not paths.ok: return paths
	return _debriefing_result(_debriefing.configure_assets(paths.value, _fonts(), frames))


## Original host clocks/facts: transition, animation_seconds, background_seconds,
## click_pulse_timer, click_page_seconds, loading_frames, launch_requested, ready.
## Cursor is last, and only after root has configured its live source. A supplied
## Vector2 remains an explicit capture position; null means the configured live
## source. No clock advances and no navigation or input operation occurs here.
## editor_page=-1 is runtime; editor enum values 0..9 use frozen page fixtures.
func redraw(session: Frontend.Session, facts: Dictionary, editor_page: int = -1) -> Dictionary:
	var editor: bool = editor_page >= 0
	# This fixture is display data, never a fabricated Won/session transition.
	var screen: int = Frontend.Screen.DEBRIEFING if editor_page == EDITOR_DEBRIEFING else session.get_screen()
	for child: Node in _stage.get_children():
		if not child is Control: continue
		match String(child.name):
			"MainMenu": child.visible = screen in [Frontend.Screen.MAIN_MENU, Frontend.Screen.QUIT_CONFIRM]
			"ClickToStart": child.visible = screen == Frontend.Screen.CLICK_TO_START
			"QuitConfirm": child.visible = screen == Frontend.Screen.QUIT_CONFIRM
			"CareerName": child.visible = screen == Frontend.Screen.DEV_SELECT
			"LevelSelect": child.visible = screen == Frontend.Screen.LEVEL_SELECT
			"MissionBriefing": child.visible = screen == Frontend.Screen.MISSION_BRIEFING
			"SelectConfiguration": child.visible = screen == Frontend.Screen.SELECT_CONFIGURATION
			"Loading": child.visible = screen == Frontend.Screen.LOADING
			"Options": child.visible = screen == Frontend.Screen.OPTIONS
			"Debriefing": child.visible = screen == Frontend.Screen.DEBRIEFING
			_: child.visible = false
	# Preserve the managed redraw order, including the Main Menu backdrop before
	# Quit and Click after the later static pages. Do not eagerly snapshot Session:
	# nullable career data is read only when its page is actually visible.
	var result: Dictionary
	if _main != null and _main.visible:
		result = _update_main(session, facts, editor_page)
		if not result.ok: return result
	if _quit != null and _quit.visible:
		result = _page_result(_quit.show_editor_preview() if editor else
			_quit.set_frame({"selected_index": session.get_selected_quit_confirm_index()}), "quit confirmation")
		if not result.ok: return result
	if _career != null and _career.visible:
		result = _update_career(session, facts, editor)
		if not result.ok: return result
	if _level != null and _level.visible:
		result = _page_result(_level.show_editor_preview() if editor else _level.set_frame({
			"level_name": Text.units(session.get_selected_level_name()).value,
			"background_seconds": facts.background_seconds}), "level-select presentation")
		if not result.ok: return result
	if _briefing != null and _briefing.visible:
		result = _update_briefing(session, editor)
		if not result.ok: return result
	if _configuration != null and _configuration.visible:
		result = _update_configuration(session, editor)
		if not result.ok: return result
	if _click != null and _click.visible:
		result = _page_result(_click.show_editor_preview() if editor else _click.set_frame({
			"pulse_timer": facts.click_pulse_timer, "page_seconds": facts.click_page_seconds}), "Click page")
		if not result.ok: return result
	if _options != null and _options.visible:
		_options.set_frame(facts.animation_seconds, facts.background_seconds)
	if _loading != null and _loading.visible:
		result = _loading_result(_loading.show_editor_progress() if editor else _loading.set_frame({
			"loading_frames": facts.loading_frames, "launch_requested": facts.launch_requested,
			"ready": facts.ready}, _loading_caption))
		if not result.ok: return result
	if _debriefing != null and _debriefing.visible:
		result = _update_debriefing(session, facts, editor)
		if not result.ok: return result
	if not editor and facts.get("cursor_initialized", false):
		return _options_result(_root.get_node("MouseCursor").set_frame({
			"screen": session.get_screen(), "cursor_position": facts.cursor_position}))
	return Values.success()


func _update_main(session: Frontend.Session, facts: Dictionary, editor_page: int) -> Dictionary:
	if editor_page == EDITOR_MAIN_MENU:
		return _page_result(_main.show_editor_preview(), "Main Menu")
	var rows: Array = []
	for item: Dictionary in session.get_items():
		rows.append({"text": _menu_labels[item.kind], "available": item.is_available})
	# An editor Quit fixture uses this real backdrop batch, not Main's frozen
	# preview, so its reflection remains suppressed just as in a runtime Quit.
	return _page_result(_main.set_frame({"transition": facts.transition,
		"animation_seconds": facts.animation_seconds, "background_seconds": facts.background_seconds,
		"selected_index": session.get_selected_main_index(), "language": session.get_language(),
		"rows": rows, "reflection_visible": session.get_screen() == Frontend.Screen.MAIN_MENU}), "Main Menu")


func _update_career(session: Frontend.Session, facts: Dictionary, editor: bool) -> Dictionary:
	if editor: return _page_result(_career.show_editor_preview(), "career-name presentation")
	var names: Array = session.get_career_names()
	var selected: int = session.get_selected_career_index()
	var game_name: Variant = session.get_game_name()
	# Original GameName.Select(...) fails before the page's set_frame. Preserve
	# that visible-only failure, while leaving all offscreen null names untouched.
	if game_name == null:
		return Values.failure("ArgumentNullException", "Value cannot be null.", "source")
	return _page_result(_career.set_frame({"career_names": names, "selected_career_index": selected,
		"game_name": game_name, "game_name_is_fresh": session.get_game_name_is_fresh(),
		"background_seconds": facts.background_seconds}), "career-name presentation")


func _update_briefing(session: Frontend.Session, editor: bool) -> Dictionary:
	if editor: return _page_result(_briefing.show_editor_preview(), "briefing presentation")
	var paragraphs: Array = []
	for paragraph: String in session.get_selected_briefing_body(): paragraphs.append(Text.units(paragraph).value)
	return _page_result(_briefing.set_frame({"level_name": Text.units(session.get_selected_level_name()).value,
		"paragraphs": paragraphs}), "briefing presentation")


func _update_configuration(session: Frontend.Session, editor: bool) -> Dictionary:
	if editor: return _page_result(_configuration.show_editor_preview(), "configuration presentation")
	var configuration: Dictionary = session.get_selected_configuration()
	return _page_result(_configuration.set_frame({"unit_name": Text.units(configuration.display_name).value,
		"walker_primary": Text.units(configuration.walker_primary.display_name).value,
		"walker_secondary": Text.units(configuration.walker_secondary.display_name).value,
		"jet_primary": Text.units(configuration.jet_primary.display_name).value,
		"jet_secondary": Text.units(configuration.jet_secondary.display_name).value}), "configuration presentation")


func _update_debriefing(session: Frontend.Session, facts: Dictionary, editor: bool) -> Dictionary:
	if editor: return _debriefing_result(_debriefing.show_editor_projection())
	var projection: Variant = session.get_debriefing()
	if projection == null:
		return Values.failure("InvalidOperationException", "The debriefing screen has no END_LEVEL_DATA projection.")
	var level_name: PackedInt32Array = Text.units(session.get_selected_level_name()).value
	# The native view already compares/caches its admitted projection. Removing
	# the managed UTF-16 transport cache does not introduce another state owner.
	return _debriefing_result(_debriefing.set_frame({"world_finished": projection.world_finished,
		"mission_status": projection.mission_status, "primary_objectives": projection.primary_objectives,
		"secondary_objectives": projection.secondary_objectives, "grade_byte": projection.grade_byte,
		"new_goodie_count": projection.new_goodie_count, "first_goodie": projection.first_goodie},
		level_name, facts.background_seconds))


func _fonts() -> Dictionary:
	return {"body_font": _options.body_font, "title_font": _options.title_font}


func _paths(routes: Array, overrides_only: bool = false) -> Dictionary:
	var paths: Dictionary = {}
	for route: Array in routes:
		var result: Dictionary = _texture_path(route[1], route[2])
		if not result.ok: return result
		if not overrides_only or result.value != "res://Assets/Frontend/" + route[2] + ".texture.aya":
			paths[route[0]] = result.value
	return Values.success(paths)


func _texture_path(folder: String, name: String) -> Dictionary:
	# Preserve the checked asset-path bridge boundary without a managed roundtrip.
	# An Options settings observer can replace the root recipe during startup.
	# Each later route must read that current property at its original use point.
	var asset_paths: Resource = _root.get("AssetPaths")
	if asset_paths == null:
		return Values.failure("NullReferenceException", "Object reference not set to an instance of an object.")
	if not asset_paths.has_method("texture_path_units"):
		return Values.failure("InvalidDataException", "The frontend asset-path resource has no checked resolver.")
	var returned: Variant = asset_paths.texture_path_units(Text.units(folder).value, Text.units(name).value)
	if not returned is Dictionary:
		return Values.failure("InvalidDataException", "The frontend asset-path resolver returned no result.")
	if typeof(returned.get("ok")) != TYPE_BOOL:
		return Values.failure("InvalidDataException", "The frontend asset-path resolver returned no completion flag.")
	if not returned.ok:
		var kind: String = returned.get("error_type", "InvalidDataException")
		if kind == "ArgumentOutOfRangeException":
			return Values.failure(kind, "Specified argument was out of the range of valid values.", "folder")
		return Values.failure(kind if kind in ["NullReferenceException", "ArgumentException"] else "InvalidDataException",
			returned.get("error", "Native frontend asset-path resolution failed."), returned.get("parameter", ""))
	if not returned.get("value") is PackedInt32Array:
		return Values.failure("InvalidDataException", "The frontend asset path is missing its UTF-16 units.")
	for unit: int in returned.value:
		if unit < 0 or unit > 65535:
			return Values.failure("InvalidDataException", "The frontend asset path contains an invalid UTF-16 unit.")
	var converted: Dictionary = Text.native_string(returned.value)
	if not converted.ok: return Values.failure("InvalidDataException", converted.error)
	return converted


static func _page_result(returned: Variant, page: String) -> Dictionary:
	if not returned is Dictionary:
		return Values.failure("InvalidDataException", "Native " + page + " returned no completion result.")
	if returned.get("ok", false): return Values.success()
	return Values.failure("InvalidDataException", returned.get("error", "Native " + page + " failed."))


static func _options_result(returned: Dictionary) -> Dictionary:
	if returned.get("ok", false): return Values.success()
	var kind: String = returned.get("error_type", "InvalidOperationException")
	if kind not in ["ArgumentOutOfRangeException", "ArgumentNullException", "ArgumentException", "NullReferenceException"]:
		kind = "InvalidOperationException"
	return Values.failure(kind, returned.get("error", "Native options operation failed."), returned.get("parameter", ""))


static func _loading_result(returned: Dictionary, configuring_assets: bool = false) -> Dictionary:
	if returned.get("ok", false): return Values.success()
	var kind: String = "InvalidDataException" if configuring_assets or returned.get("error_type") == "InvalidDataException" else "InvalidOperationException"
	return Values.failure(kind, returned.get("error", "Native Loading failed."))


static func _debriefing_result(returned: Dictionary) -> Dictionary:
	if returned.get("ok", false): return Values.success()
	var kind: String = "InvalidDataException" if returned.get("error_type") == "InvalidDataException" else "InvalidOperationException"
	return Values.failure(kind, returned.get("error", "Native debriefing failed."))
