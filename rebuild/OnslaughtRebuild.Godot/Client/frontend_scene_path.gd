# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Session-facing production predicates from RetailFrontendScenePath.cs. The
## scene owns device events and startup visibility; this pure adapter owns no
## duplicate screen, selection, campaign or option-menu state.

const Frontend = preload("res://Client/frontend_session.gd")
const Values = preload("res://Core/retail_career_values.gd")


static func accepts_click_to_start_mouse(screen: int, _x: float, _y: float) -> bool:
	# RetailClickToStartInput.AcceptsMouseAt deliberately ignores coordinates:
	# the backend supplied the window rectangle, not a page-local glyph box.
	return screen == Frontend.Screen.CLICK_TO_START


static func accepts_click_to_start_key(screen: int, dik: int) -> bool:
	return screen == Frontend.Screen.CLICK_TO_START and dik in [0x1c, 0x39]


static func can_accept_main_menu_row(session: Frontend.Session, index: int) -> Dictionary:
	if session == null:
		return _missing_session()
	var rows: Array[Dictionary] = session.get_items()
	return Values.success(session.get_screen() == Frontend.Screen.MAIN_MENU \
		and index >= 0 and index < rows.size() and rows[index].is_available)


static func try_confirm_page(session: Frontend.Session, startup_media_active: bool) -> Dictionary:
	if session == null:
		return _missing_session()
	if startup_media_active or session.get_screen() not in [Frontend.Screen.CLICK_TO_START,
		Frontend.Screen.MAIN_MENU, Frontend.Screen.QUIT_CONFIRM, Frontend.Screen.DEV_SELECT,
		Frontend.Screen.DEBRIEFING, Frontend.Screen.LEVEL_SELECT,
		Frontend.Screen.MISSION_BRIEFING, Frontend.Screen.SELECT_CONFIGURATION]:
		return _navigation(false, Frontend.FrontendSignal.NONE)
	var result: Dictionary = session.confirm()
	if not result.ok:
		return result
	return _navigation(result.value != Frontend.FrontendSignal.NONE, result.value)


static func try_back_page(session: Frontend.Session, startup_media_active: bool) -> Dictionary:
	if session == null:
		return _missing_session()
	if startup_media_active or session.get_screen() not in [Frontend.Screen.QUIT_CONFIRM,
		Frontend.Screen.DEV_SELECT, Frontend.Screen.OPTIONS, Frontend.Screen.DEBRIEFING,
		Frontend.Screen.SELECT_CONFIGURATION, Frontend.Screen.MISSION_BRIEFING,
		Frontend.Screen.LEVEL_SELECT]:
		return _navigation(false, Frontend.FrontendSignal.NONE)
	var result: Dictionary = session.back()
	if not result.ok:
		return result
	return _navigation(result.value != Frontend.FrontendSignal.NONE, result.value)


static func try_complete_loading(session: Frontend.Session, startup_media_active: bool, launch_consumed: bool) -> Dictionary:
	if session == null:
		return _missing_session()
	if startup_media_active or not launch_consumed or session.get_screen() != Frontend.Screen.LOADING:
		return Values.success(false)
	var result: Dictionary = session.complete_level100_load()
	return Values.success(session.get_screen() == Frontend.Screen.GAMEPLAY) if result.ok else result


static func try_complete_intro_cutscene(session: Frontend.Session, startup_media_active: bool) -> Dictionary:
	if session == null:
		return _missing_session()
	if startup_media_active or session.get_screen() != Frontend.Screen.INTRO_CUTSCENE:
		return Values.success(false)
	var result: Dictionary = session.complete_level100_intro_cutscene()
	return Values.success(session.get_screen() == Frontend.Screen.GAMEPLAY) if result.ok else result


static func try_accept_won_handoff(session: Frontend.Session, outcome: int, terminal_state: int) -> Dictionary:
	if session == null:
		return _missing_session()
	var result: Dictionary = session.try_accept_won_handoff(outcome, terminal_state)
	return Values.success(result.value and session.get_screen() == Frontend.Screen.DEBRIEFING) if result.ok else result


static func _missing_session() -> Dictionary:
	return Values.failure("ArgumentNullException", "Frontend session must not be null.", "session")


static func _navigation(accepted: bool, signal_id: int) -> Dictionary:
	return {"ok": true, "value": accepted, "signal": signal_id}
