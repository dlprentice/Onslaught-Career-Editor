# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure port of Client/RetailFrontendSession.cs. Explicit preload; no global
## class cache, scenes, device input, storage discovery, save writes or clocks.
## create() returns {ok,value:Session}. State-changing methods return {ok,value}
## or an explicit original exception type, preserving writes before failure.
## Names are raw UTF-16 PackedInt32Array values, including null/malformed names.

const Values = preload("res://Core/retail_career_values.gd")
const Text = preload("res://Core/canonical_json_string.gd")

enum Screen { CLICK_TO_START = 0, MAIN_MENU = 1, QUIT_CONFIRM = 2, DEV_SELECT = 3,
	OPTIONS = 4, DEBRIEFING = 5, LEVEL_SELECT = 6, MISSION_BRIEFING = 7,
	SELECT_CONFIGURATION = 8, LOADING = 9, INTRO_CUTSCENE = 10, GAMEPLAY = 11 }
enum FrontendSignal { NONE = 0, PAGE_CHANGED = 1, UNAVAILABLE = 2, CAREER_LOAD_REQUESTED = 3,
	LEVEL_LAUNCH_REQUESTED = 4, RETURN_TO_MAIN_MENU_REQUESTED = 5, EXIT_REQUESTED = 6 }
enum CareerPageMode { NEW = 0, LOAD = 1 }
enum AudioCue { MOVE = 0, SELECT = 1, BACK = 2 }
enum Language { ENGLISH = 0, FRENCH = 1, GERMAN = 2, ITALIAN = 3, SPANISH = 4 }
enum CursorMode { CUSTOM = 0, VISIBLE = 1, HIDDEN = 2, CAPTURED = 3 }
enum MenuKind { NEW_GAME = 0, CONTINUE_GAME = 1, LOAD_GAME = 2, MULTIPLAYER = 3, GOODIES = 4, OPTIONS = 5, QUIT = 6 }

const DEFAULT_GAME_NAME: String = "BEA 1"
const MAX_GAME_NAME_LENGTH: int = 31
const GAME_NAME_WIDTH_LIMIT: int = 384
const EXTENDED_NAME_GLYPHS: String = "áàâäçéèêëíìîïóòôöœñúùûüÁÀÄÂÇÉÈÍÌÑÓÒÖÜÚÙŒ¡¿©®™«»ºª\u001fßÊËÎÏÔÛ┐┌"
const CONFIGURATIONS: Array[Dictionary] = [{"catalog_record_index": 3,
	"authored_name": "Aquila Prototype", "display_name": "BE:A Unit-00 'Prototype'",
	"walker_primary": {"authored_name": "Pulse Cannon Pod", "display_name": "Pulse Cannon"},
	"walker_secondary": {"authored_name": "Mech Twin Vulcan Cannon", "display_name": "Vulcan Cannon"},
	"jet_primary": {"authored_name": "Mech Vulcan Cannon", "display_name": "Vulcan Cannon"},
	"jet_secondary": {"authored_name": "Missile Pod", "display_name": "Micro Missiles"}}]


class Session extends RefCounted:
	const Values = preload("res://Core/retail_career_values.gd")
	const Text = preload("res://Core/canonical_json_string.gd")
	const Campaign = preload("res://Core/retail_career_campaign.gd")
	const WorldStrings = preload("res://Core/frontend_world_strings.gd")
	var _screen: int = Screen.CLICK_TO_START
	var _selected_world_number: int = 100
	var _selected_main_index: int = 0
	var _selected_quit_confirm_index: int = 0
	var _selected_configuration_index: int = 0
	var _unavailable_selection: Variant = null
	var _career_page_mode: int = CareerPageMode.NEW
	var _selected_career_index: int = -1
	var _career_descriptors: Array[Dictionary] = []
	var _career_names: Array = []
	var _game_name: Variant = PackedInt32Array([66, 69, 65, 32, 49])
	var _game_name_cursor: int = 5
	var _game_name_is_fresh: bool = true
	var _level100_launch_pending: bool = false
	var _level100_intro_cutscene_pending: bool = true
	var _active_loaded_career: Variant = null
	# The request stores its original supplied ordinal. This retains exact
	# descriptor identity for the verified host read owner, including duplicate
	# records, without copying original save bytes into this presentation model.
	var _selected_career_load_request_index: int = -1
	var _debriefing: Variant = null
	var _career: Campaign.Campaign = Campaign.create_cold_training_slice()

	func _init(descriptors: Array[Dictionary]) -> void:
		_career_descriptors = descriptors.duplicate(true)
		for descriptor: Dictionary in _career_descriptors:
			_career_names.append(descriptor.name)


	func get_screen() -> int:
		return _screen


	func get_selected_world_number() -> int:
		return _selected_world_number


	func get_selected_level_name() -> String:
		var name: Variant = WorldStrings.level_name(_selected_world_number)
		return "" if name == null else name


	func get_selected_briefing_body() -> Array[String]:
		return WorldStrings.briefing(_selected_world_number)


	func get_debriefing() -> Variant:
		return null if _debriefing == null else _debriefing.duplicate(true)


	func get_selected_main_index() -> int:
		return _selected_main_index


	func get_language() -> int:
		# Source has an English initializer and no public language mutation API.
		return Language.ENGLISH


	func get_selected_quit_confirm_index() -> int:
		return _selected_quit_confirm_index


	func get_items() -> Array[Dictionary]:
		var result: Array[Dictionary] = []
		for kind: int in range(7):
			result.append({"kind": kind, "is_available": kind != MenuKind.CONTINUE_GAME})
		return result


	func get_selected_main_item() -> Dictionary:
		return get_items()[_selected_main_index]


	func get_configuration_count() -> int:
		return CONFIGURATIONS.size()


	func get_selected_configuration_index() -> int:
		return _selected_configuration_index


	func get_selected_configuration() -> Dictionary:
		return CONFIGURATIONS[_selected_configuration_index].duplicate(true)


	func get_unavailable_selection() -> Variant:
		return _unavailable_selection


	func get_career_descriptors() -> Array[Dictionary]:
		return _career_descriptors.duplicate(true)


	func get_career_names() -> Array:
		return _career_names.duplicate(true)


	func get_career_page_mode() -> int:
		return _career_page_mode


	func get_selected_career_index() -> int:
		return _selected_career_index


	func get_game_name() -> Variant:
		return null if _game_name == null else _game_name.duplicate()


	func get_game_name_cursor() -> int:
		return _game_name_cursor


	func get_game_name_is_fresh() -> bool:
		return _game_name_is_fresh


	func get_career() -> Campaign.Campaign:
		return _career


	func get_consume_launch_world_number() -> int:
		# This C# property reads the value; it does not consume a second request.
		return _selected_world_number


	func get_selected_world_is_constructible() -> bool:
		return _selected_world_number == 100


	func get_level100_intro_cutscene_pending() -> bool:
		return _level100_intro_cutscene_pending


	func snapshot() -> Dictionary:
		return {"screen": _screen, "selected_world_number": _selected_world_number,
			"selected_level_name": get_selected_level_name(), "selected_briefing_body": get_selected_briefing_body(),
			"debriefing": get_debriefing(), "selected_main_index": _selected_main_index,
			"language": get_language(), "selected_quit_confirm_index": _selected_quit_confirm_index,
			"selected_main_item": get_selected_main_item(), "items": get_items(),
			"configuration_count": get_configuration_count(), "selected_configuration_index": _selected_configuration_index,
			"selected_configuration": get_selected_configuration(), "unavailable_selection": _unavailable_selection,
			"career_descriptors": get_career_descriptors(), "career_names": get_career_names(),
			"career_page_mode": _career_page_mode, "selected_career_index": _selected_career_index,
			"game_name": get_game_name(), "game_name_cursor": _game_name_cursor,
			"game_name_is_fresh": _game_name_is_fresh, "career": _career.snapshot(),
			"consume_launch_world_number": _selected_world_number,
			"selected_world_is_constructible": get_selected_world_is_constructible(),
			"level100_intro_cutscene_pending": _level100_intro_cutscene_pending}


	func select_career_index(index: int) -> Dictionary:
		if _screen != Screen.DEV_SELECT or index < 0 or index >= _career_names.size() or index == _selected_career_index:
			return Values.success(false)
		_selected_career_index = index
		_game_name = null if _career_names[index] == null else _career_names[index].duplicate()
		# A caller-created C# record may carry Name=null. Selection/index/name
		# have already changed when its Length dereference fails.
		if _game_name == null:
			return Values.failure("NullReferenceException", "Selected career name is null.")
		_game_name_cursor = mini(_game_name.size(), 31)
		_game_name_is_fresh = true
		return Values.success(true)


	static func game_name_glyph_index(character: int) -> int:
		var mapped: int = 39 if character == 0x2019 else (45 if character == 0x2013 else character)
		if mapped in [36, 64, 91, 92, 93, 94, 95, 123, 124, 125, 126, 127]:
			return -1
		if mapped >= 32 and mapped <= 127:
			return mapped - 32
		if mapped == 31:
			return -1
		for index: int in range(EXTENDED_NAME_GLYPHS.length()):
			if EXTENDED_NAME_GLYPHS.unicode_at(index) == mapped:
				return index + 96
		return -1


	static func game_name_render_glyph_index(character: int, swap_inverted_punctuation: bool) -> int:
		var mapped: int = character
		if swap_inverted_punctuation:
			if character == 161:
				mapped = 191
			elif character == 191:
				mapped = 161
		var glyph: int = game_name_glyph_index(mapped)
		return 145 if glyph < 0 else glyph


	func append_game_name_character(character: int, current_text_width: int) -> Dictionary:
		if character < 0 or character > 65535 or not Values.is_int32(current_text_width):
			return Values.failure("ArgumentException", "A character is one UTF-16 unit and width is int32.")
		if _screen != Screen.DEV_SELECT or _career_page_mode != CareerPageMode.NEW or game_name_glyph_index(character) < 0:
			return Values.success(false)
		if _game_name == null:
			return Values.failure("NullReferenceException", "Game name is null.")
		if _game_name.size() >= 31:
			return Values.success(false)
		if _game_name_is_fresh:
			_game_name = PackedInt32Array()
			_game_name_cursor = 0
			_game_name_is_fresh = false
			current_text_width = 0
		if current_text_width >= 384:
			return Values.success(false)
		_game_name.insert(_game_name_cursor, character)
		_game_name_cursor += 1
		return Values.success(true)


	func move_game_name_cursor(right: bool) -> Dictionary:
		if _screen != Screen.DEV_SELECT or _career_page_mode != CareerPageMode.NEW:
			return Values.success(false)
		var changed: bool = _game_name_is_fresh
		_game_name_is_fresh = false
		if _game_name == null:
			return Values.failure("NullReferenceException", "Game name is null.")
		var next: int = clampi(_game_name_cursor + (1 if right else -1), 0, mini(_game_name.size(), 31))
		changed = changed or next != _game_name_cursor
		_game_name_cursor = next
		return Values.success(changed)


	func remove_game_name_character() -> Dictionary:
		if _screen != Screen.DEV_SELECT or _career_page_mode != CareerPageMode.NEW:
			return Values.success(false)
		if _game_name_is_fresh:
			_game_name = PackedInt32Array()
			_game_name_cursor = 0
			_game_name_is_fresh = false
			return Values.success(true)
		if _game_name_cursor == 0:
			return Values.success(false)
		# C# evaluates --cursor before invoking Remove on a possibly null name.
		_game_name_cursor -= 1
		if _game_name == null:
			return Values.failure("NullReferenceException", "Game name is null.")
		_game_name.remove_at(_game_name_cursor)
		return Values.success(true)


	func _reset_game_name() -> void:
		_game_name = PackedInt32Array([66, 69, 65, 32, 49])
		_game_name_cursor = 5
		_game_name_is_fresh = true


	func _seed_game_name() -> void:
		var suffix: int = 1
		while suffix < 4096 and _career_names.has(Text.units("BEA " + str(suffix)).value):
			suffix += 1
		_game_name = Text.units("BEA " + str(suffix)).value
		_game_name_cursor = mini(_game_name.size(), 31)
		_game_name_is_fresh = true


	func move_previous() -> Dictionary:
		if _screen == Screen.QUIT_CONFIRM:
			if _selected_quit_confirm_index == 0:
				return Values.success(false)
			_selected_quit_confirm_index = 0
			return Values.success(true)
		if _screen == Screen.DEV_SELECT:
			return select_career_index(_selected_career_index - 1)
		if _screen == Screen.SELECT_CONFIGURATION:
			return select_configuration_index(_selected_configuration_index - 1)
		if _screen != Screen.MAIN_MENU or _selected_main_index == 0:
			return Values.success(false)
		_selected_main_index -= 1
		_unavailable_selection = null
		return Values.success(true)


	func move_next() -> Dictionary:
		if _screen == Screen.QUIT_CONFIRM:
			if _selected_quit_confirm_index == 1:
				return Values.success(false)
			_selected_quit_confirm_index = 1
			return Values.success(true)
		if _screen == Screen.DEV_SELECT:
			return select_career_index(_selected_career_index + 1)
		if _screen == Screen.SELECT_CONFIGURATION:
			return select_configuration_index(_selected_configuration_index + 1)
		if _screen != Screen.MAIN_MENU or _selected_main_index == 6:
			return Values.success(false)
		_selected_main_index += 1
		_unavailable_selection = null
		return Values.success(true)


	func select_main_index(index: int) -> Dictionary:
		if _screen != Screen.MAIN_MENU or index < 0 or index >= 7 or index == _selected_main_index:
			return Values.success(false)
		_selected_main_index = index
		_unavailable_selection = null
		return Values.success(true)


	func select_quit_confirm_index(index: int) -> Dictionary:
		if _screen != Screen.QUIT_CONFIRM or index < 0 or index > 1 or index == _selected_quit_confirm_index:
			return Values.success(false)
		_selected_quit_confirm_index = index
		return Values.success(true)


	func select_configuration_index(index: int) -> Dictionary:
		if _screen != Screen.SELECT_CONFIGURATION or index < 0 or index >= CONFIGURATIONS.size() or index == _selected_configuration_index:
			return Values.success(false)
		_selected_configuration_index = index
		return Values.success(true)


	func select_world(world_number: int) -> Dictionary:
		# Source computes selectability before checking the current page or world.
		var selectable: Dictionary
		if _active_loaded_career != null:
			if _active_loaded_career.career == null:
				return Values.failure("NullReferenceException", "Selected career is null.")
			selectable = Values.success(_active_loaded_career.career.selectable_world_numbers.has(world_number))
		else:
			selectable = _career.is_world_selectable(world_number)
		if not selectable.ok:
			return selectable
		if _screen != Screen.LEVEL_SELECT or world_number == _selected_world_number or not selectable.value:
			return Values.success(false)
		_selected_world_number = world_number
		return Values.success(true)


	func confirm() -> Dictionary:
		_unavailable_selection = null
		match _screen:
			Screen.CLICK_TO_START:
				_screen = Screen.MAIN_MENU
				_selected_main_index = 0
				return Values.success(FrontendSignal.PAGE_CHANGED)
			Screen.MAIN_MENU:
				if not get_selected_main_item().is_available:
					_unavailable_selection = _selected_main_index
					return Values.success(FrontendSignal.UNAVAILABLE)
				match _selected_main_index:
					MenuKind.NEW_GAME:
						_screen = Screen.DEV_SELECT
						_career_page_mode = CareerPageMode.NEW
						_active_loaded_career = null
						_selected_career_load_request_index = -1
						_selected_world_number = 100
						_selected_career_index = -1
						_seed_game_name()
						return Values.success(FrontendSignal.PAGE_CHANGED)
					MenuKind.LOAD_GAME:
						_screen = Screen.DEV_SELECT
						_career_page_mode = CareerPageMode.LOAD
						_active_loaded_career = null
						_selected_career_load_request_index = -1
						_selected_career_index = -1
						_reset_game_name()
						return Values.success(FrontendSignal.PAGE_CHANGED)
					MenuKind.QUIT:
						_screen = Screen.QUIT_CONFIRM
						_selected_quit_confirm_index = 0
						return Values.success(FrontendSignal.PAGE_CHANGED)
					MenuKind.OPTIONS:
						_screen = Screen.OPTIONS
						return Values.success(FrontendSignal.PAGE_CHANGED)
			Screen.QUIT_CONFIRM:
				if _selected_quit_confirm_index == 0:
					_screen = Screen.MAIN_MENU
					return Values.success(FrontendSignal.PAGE_CHANGED)
				return Values.success(FrontendSignal.EXIT_REQUESTED)
			Screen.DEV_SELECT:
				if _career_page_mode == CareerPageMode.LOAD:
					if _selected_career_index < 0:
						_unavailable_selection = MenuKind.LOAD_GAME
						return Values.success(FrontendSignal.UNAVAILABLE)
					_active_loaded_career = _career_descriptors[_selected_career_index]
					_selected_career_load_request_index = _selected_career_index
					if _active_loaded_career.career == null:
						return Values.failure("NullReferenceException", "Selected career is null.")
					_selected_world_number = _active_loaded_career.career.suggested_world_number
					_screen = Screen.LEVEL_SELECT
					return Values.success(FrontendSignal.CAREER_LOAD_REQUESTED)
				_screen = Screen.LEVEL_SELECT
				return Values.success(FrontendSignal.PAGE_CHANGED)
			Screen.LEVEL_SELECT:
				_screen = Screen.MISSION_BRIEFING
				return Values.success(FrontendSignal.PAGE_CHANGED)
			Screen.DEBRIEFING:
				_debriefing = null
				_screen = Screen.LEVEL_SELECT
				return Values.success(FrontendSignal.PAGE_CHANGED)
			Screen.MISSION_BRIEFING:
				_selected_configuration_index = 0
				_screen = Screen.SELECT_CONFIGURATION
				return Values.success(FrontendSignal.PAGE_CHANGED)
			Screen.SELECT_CONFIGURATION:
				_screen = Screen.LOADING
				_level100_launch_pending = true
				return Values.success(FrontendSignal.LEVEL_LAUNCH_REQUESTED)
		return Values.success(FrontendSignal.NONE)


	func back() -> Dictionary:
		_unavailable_selection = null
		match _screen:
			Screen.QUIT_CONFIRM, Screen.OPTIONS:
				_screen = Screen.MAIN_MENU
			Screen.DEV_SELECT:
				_screen = Screen.MAIN_MENU
				_career_page_mode = CareerPageMode.NEW
				_active_loaded_career = null
				_selected_career_load_request_index = -1
				_selected_career_index = -1
				_reset_game_name()
			Screen.SELECT_CONFIGURATION:
				_screen = Screen.MISSION_BRIEFING
			Screen.MISSION_BRIEFING:
				_screen = Screen.LEVEL_SELECT
			Screen.DEBRIEFING:
				_debriefing = null
				_screen = Screen.LEVEL_SELECT
			Screen.LEVEL_SELECT:
				_screen = Screen.DEV_SELECT
			_:
				return Values.success(FrontendSignal.NONE)
		return Values.success(FrontendSignal.PAGE_CHANGED)


	func consume_level100_launch_request() -> Dictionary:
		if not _level100_launch_pending:
			return Values.success(false)
		_level100_launch_pending = false
		return Values.success(true)


	func consume_selected_career_load_request() -> Dictionary:
		var request: Dictionary = consume_selected_career_load_request_index()
		return Values.success(null if request.value == null else _career_descriptors[request.value].duplicate(true))


	## Same consume edge, represented by the caller's original descriptor ordinal.
	## The bridge uses this to return the exact verified C# save object; it never
	## guesses identity by matching names, slots, serialized bytes or current row.
	func consume_selected_career_load_request_index() -> Dictionary:
		var index: int = _selected_career_load_request_index
		_selected_career_load_request_index = -1
		return Values.success(null if index < 0 else index)


	func complete_level100_load() -> Dictionary:
		if _screen != Screen.LOADING or _level100_launch_pending:
			return Values.failure("InvalidOperationException", "Level 100 can complete only after its pending launch request is consumed.")
		_level100_intro_cutscene_pending = false
		_screen = Screen.GAMEPLAY
		return Values.success()


	func begin_level100_intro_cutscene() -> Dictionary:
		if _screen != Screen.LOADING or _level100_launch_pending:
			return Values.failure("InvalidOperationException", "The intro cutscene can begin only after Level 100 has loaded.")
		if not _level100_intro_cutscene_pending:
			return Values.failure("InvalidOperationException", "Retail plays a level's intro cutscene only on the first time round.")
		_level100_intro_cutscene_pending = false
		_screen = Screen.INTRO_CUTSCENE
		return Values.success()


	func complete_level100_intro_cutscene() -> Dictionary:
		if _screen != Screen.INTRO_CUTSCENE:
			return Values.failure("InvalidOperationException", "There is no intro cutscene to complete.")
		_screen = Screen.GAMEPLAY
		return Values.success()


	func restart_level100() -> Dictionary:
		if _screen != Screen.GAMEPLAY:
			return Values.failure("InvalidOperationException", "RestartLevel100 requires an active Level 100 lifecycle.")
		_screen = Screen.LOADING
		_level100_launch_pending = true
		return Values.success(FrontendSignal.LEVEL_LAUNCH_REQUESTED)


	func leave_level100_for_main_menu() -> Dictionary:
		if _screen != Screen.GAMEPLAY:
			return Values.failure("InvalidOperationException", "LeaveLevel100ForMainMenu requires an active Level 100 lifecycle.")
		_selected_main_index = 0
		_selected_quit_confirm_index = 0
		_unavailable_selection = null
		_selected_career_index = -1
		_career_page_mode = CareerPageMode.NEW
		_active_loaded_career = null
		_selected_career_load_request_index = -1
		_selected_configuration_index = 0
		_debriefing = null
		_reset_game_name()
		_level100_launch_pending = false
		_level100_intro_cutscene_pending = true
		_screen = Screen.MAIN_MENU
		return Values.success(FrontendSignal.RETURN_TO_MAIN_MENU_REQUESTED)


	func try_accept_won_handoff(outcome: int, terminal_state: int) -> Dictionary:
		if _screen != Screen.GAMEPLAY or outcome != 1 or terminal_state != 2:
			return Values.success(false)
		var end_level: Dictionary = Values.for_level100_won()
		var updated: Dictionary = _career.apply_update(end_level)
		if not updated.ok:
			return updated
		# C# evaluates these read-and-clear arguments left to right before From.
		var new_goodies: int = _career.counters().get_and_reset_goodie_new_count()
		var first_goodie: int = _career.counters().get_and_reset_first_goodie()
		var projection: Dictionary = Values.debriefing(end_level, new_goodies, first_goodie)
		if not projection.ok:
			return projection
		_debriefing = projection.value
		_level100_launch_pending = false
		_selected_configuration_index = 0
		_level100_intro_cutscene_pending = true
		_screen = Screen.DEBRIEFING
		return Values.success(true)


	func return_unconstructible_launch_to_level_select() -> Dictionary:
		if _screen != Screen.LOADING or _level100_launch_pending:
			return Values.success(false)
		_level100_intro_cutscene_pending = true
		_screen = Screen.LEVEL_SELECT
		return Values.success(true)


## Descriptors are already-read facts: slot_number:int32|null, name:String or
## raw UTF-16|null, career:null or {suggested_world_number:int32,
## selectable_world_numbers:Array[int32]}. Original bytes/verified storage handles
## remain with the caller's safe read owner, indexed in this same supplied order.
static func create(career_descriptors: Variant = null) -> Dictionary:
	if career_descriptors != null and typeof(career_descriptors) != TYPE_ARRAY:
		return Values.failure("ArgumentException", "Career descriptors require an array.", "careerDescriptors")
	var descriptors: Array[Dictionary] = []
	if career_descriptors != null:
		for descriptor: Variant in career_descriptors:
			if descriptor == null:
				return Values.failure("NullReferenceException", "A career descriptor is null.")
			if not descriptor is Dictionary or not descriptor.has_all(["slot_number", "name", "career"]):
				return Values.failure("ArgumentException", "Career descriptor fields are missing.", "careerDescriptors")
			if descriptor.slot_number != null and not Values.is_int32(descriptor.slot_number):
				return Values.failure("ArgumentException", "Career slot requires nullable int32.", "slot_number")
			var name: Dictionary = Text.units(descriptor.name)
			if not name.ok:
				return name
			var career: Variant = null
			if descriptor.career != null:
				if not descriptor.career is Dictionary or not Values.is_int32(descriptor.career.get("suggested_world_number")):
					return Values.failure("ArgumentException", "Read career projection requires an int32 suggested world.", "career")
				var worlds: Dictionary = Values.words(descriptor.career.get("selectable_world_numbers"), -1, "selectable_world_numbers")
				if not worlds.ok:
					return worlds
				career = {"suggested_world_number": descriptor.career.suggested_world_number,
					"selectable_world_numbers": worlds.value}
			descriptors.append({"slot_number": descriptor.slot_number, "name": name.value, "career": career})
	return Values.success(Session.new(descriptors))


static func game_name_glyph_index(character: int) -> int:
	return Session.game_name_glyph_index(character)


static func game_name_render_glyph_index(character: int, swap_inverted_punctuation: bool) -> int:
	return Session.game_name_render_glyph_index(character, swap_inverted_punctuation)
