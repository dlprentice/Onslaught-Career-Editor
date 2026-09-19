# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure pause state, ported from OnslaughtRebuild.Client/Level100PauseMenu.cs.
## Callers preload this script explicitly. It owns no scene, input, timing,
## audio, settings or gameplay state. Rows without an integrated owner remain
## visible but disabled, as in the C# contract.

enum Page {
	ROOT = 0,
	CONFIRM_RETRY = 1,
	CONFIRM_QUIT = 2,
}

enum Action {
	NONE = 0,
	RESUME = 1,
	RETRY_LEVEL = 2,
	RETURN_TO_FRONTEND = 3,
}

enum EntryId {
	CONTINUE = 0,
	MESSAGE_LOG = 1,
	BRIEFING = 2,
	CONTROLLER_OPTIONS = 3,
	SOUND_OPTIONS = 4,
	VIDEO_OPTIONS = 5,
	RETRY = 6,
	QUIT = 7,
	NO = 8,
	YES = 9,
}

var _is_open: bool = false
var _page: Page = Page.ROOT
var _selected_index: int = 0
var _root_selection: int = 0
var _return_root_selection: int = 0


func is_open() -> bool:
	return _is_open


func get_page() -> Page:
	return _page


func get_selected_index() -> int:
	return _selected_index


func get_underlying_root_selection() -> int:
	return _return_root_selection


## Entry arrays and their dictionaries are newly allocated on every call.
func get_entries() -> Array[Dictionary]:
	return _build_entries(_page)


func get_root_entries() -> Array[Dictionary]:
	return _build_entries(Page.ROOT)


## Presentation receives detached row values, not a second live state owner.
## The view owns its fade/visibility; is_open() remains the host's state gate.
func view_snapshot() -> Dictionary:
	return {
		"page": _page,
		"selected_index": _selected_index,
		"underlying_root_selection": _return_root_selection,
		"root_entries": _view_entries(get_root_entries()),
		"entries": _view_entries(get_entries()),
	}


func open() -> void:
	if _is_open:
		_ensure_enabled_selection()
		return
	_is_open = true
	_page = Page.ROOT
	_selected_index = 0
	_root_selection = 0
	_return_root_selection = 0


func reset() -> void:
	_is_open = false
	_page = Page.ROOT
	_selected_index = 0
	_root_selection = 0
	_return_root_selection = 0


func move_selection(direction: int) -> bool:
	if not _is_open or direction == 0:
		return false
	var entries: Array[Dictionary] = get_entries()
	var step: int = 1 if direction > 0 else -1
	var candidate: int = _selected_index
	for _attempt: int in range(entries.size()):
		candidate = (candidate + step + entries.size()) % entries.size()
		if entries[candidate]["enabled"]:
			var moved: bool = candidate != _selected_index
			_set_selection(candidate)
			return moved
	return false


func hover(index: int) -> bool:
	var entries: Array[Dictionary] = get_entries()
	if not _is_open or index < 0 or index >= entries.size() or not entries[index]["enabled"]:
		return false
	var moved: bool = index != _selected_index
	_set_selection(index)
	return moved


func activate_selected() -> Action:
	if not _is_open:
		return Action.NONE
	var entry: Dictionary = get_entries()[_selected_index]
	if not entry["enabled"]:
		return Action.NONE
	match entry["id"]:
		EntryId.CONTINUE:
			return _close(Action.RESUME)
		EntryId.RETRY:
			_enter_confirmation(Page.CONFIRM_RETRY)
		EntryId.QUIT:
			_enter_confirmation(Page.CONFIRM_QUIT)
		EntryId.NO:
			_return_to_root()
		EntryId.YES:
			if _page == Page.CONFIRM_RETRY:
				return _close(Action.RETRY_LEVEL)
			if _page == Page.CONFIRM_QUIT:
				return _close(Action.RETURN_TO_FRONTEND)
	return Action.NONE


func cancel() -> Action:
	if not _is_open:
		return Action.NONE
	if _page == Page.ROOT:
		return _close(Action.RESUME)
	_return_to_root()
	return Action.NONE


func _enter_confirmation(page: Page) -> void:
	_return_root_selection = _root_selection
	_page = page
	_selected_index = 0


func _return_to_root() -> void:
	_page = Page.ROOT
	_selected_index = _return_root_selection
	_root_selection = _selected_index
	_ensure_enabled_selection()


func _close(action: Action) -> Action:
	# Closing preserves page and selection. Only a later open/reset resets them.
	_is_open = false
	return action


func _set_selection(index: int) -> void:
	_selected_index = index
	if _page == Page.ROOT:
		_root_selection = index


func _ensure_enabled_selection() -> void:
	if not _is_open or get_entries()[_selected_index]["enabled"]:
		return
	move_selection(1)


func _build_entries(page: Page) -> Array[Dictionary]:
	if page == Page.ROOT:
		return [
			_entry(EntryId.CONTINUE, "Continue"),
			_entry(EntryId.MESSAGE_LOG, "Message Log", false),
			_entry(EntryId.BRIEFING, "Briefing", false),
			_entry(EntryId.CONTROLLER_OPTIONS, "Controller Options", false),
			_entry(EntryId.SOUND_OPTIONS, "Sound Options", false),
			_entry(EntryId.VIDEO_OPTIONS, "Video Options", false),
			_entry(EntryId.RETRY, "Retry"),
			_entry(EntryId.QUIT, "Quit"),
		]
	# Both confirmation pages have the same retained safe-default row order.
	# _page is private state and its only writers use the three enum members.
	return [_entry(EntryId.NO, "No"), _entry(EntryId.YES, "Yes")]


static func _entry(id: EntryId, label: String, enabled: bool = true) -> Dictionary:
	return {"id": id, "label": label, "enabled": enabled}


static func _view_entries(entries: Array[Dictionary]) -> Array[Dictionary]:
	var rows: Array[Dictionary] = []
	for entry: Dictionary in entries:
		rows.append({"label": entry["label"], "enabled": entry["enabled"]})
	return rows
