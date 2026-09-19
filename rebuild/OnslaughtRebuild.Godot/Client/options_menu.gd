# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure RetailOptionsMenu.cs port. Host lists are already enumerated facts;
## settings and pages own no device, file, input, audio, window or simulation.
## Every fallible operation returns {ok,value} or the original exception type.
## Settings writes are explicit, typed and do not implicitly Sync or Apply.
## Display reads are detached. Injected labels use raw UTF-16, retaining NUL.

const V = preload("res://Core/retail_career_values.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const Laws = preload("res://Client/options_laws.gd")

enum Page { ROOT = 0, CONTROLLER = 1, VIDEO = 2, SOUND = 3 }
enum RowKind { PAGE_LINK = 0, ACTION = 1, VALUE_BAR = 2, DROPDOWN = 3, STATUS = 4, BINDINGS = 5 }
enum Timing { LIVE = 0, ON_ROW_CLOSE = 1, ON_APPLY = 2 }
enum Action { NONE = 0, APPLY = 1, BACK = 2, CREDITS = 3 }
enum OptionsSignal { NONE = 0, PAGE_CHANGED = 1, VALUE_CHANGED = 2, APPLIED = 3, CLOSED = 4 }

const ROW_HEIGHT: float = 20.0
const BINDINGS_ROW_HEIGHT: float = 230.0
const JOYSTICK_ROW_HEIGHT: float = 17.0
const RANGE_ORIGIN_Y: float = 300.0
const RANGE_TOP_INSET: float = 15.0
const MOUSE_SENSITIVITY_STEP: float = 3.0
const MOUSE_SENSITIVITY_MAX_VALUE: int = 20
const DEFAULT_MOUSE_SENSITIVITY: float = 7.0
const VOLUME_MAX_VALUE: int = 10
const VALUE_ROW_SEED_BIAS: float = 0.48


class Menu extends RefCounted:
	const V = preload("res://Core/retail_career_values.gd")
	const F = preload("res://Scenes/Shared/retail_float32.gd")
	const Laws = preload("res://Client/options_laws.gd")
	const Text = preload("res://Core/canonical_json_string.gd")
	const Bindings = preload("res://Client/retail_control_bindings.gd")
	var _host: Dictionary
	var _settings: Dictionary = {
		"sound_volume": F.value(0.8), "music_volume": F.value(0.9), "mouse_sensitivity": 7.0,
		"controller_configuration": 1, "invert_y_walker_player1": false, "invert_y_walker_player2": false,
		"invert_y_flight_player1": false, "invert_y_flight_player2": false, "overall_detail": 0,
		"shadow_detail": 0, "geometry_detail": 1, "trilinear_mipmapping": true, "v_sync": false,
		"landscape_resolution": 3, "texture_resolution": -1, "enable32_bit_textures": -1,
		"swap_speakers": false, "hardware_sound": false, "sound_quality": 0, "sound_method3_d": 0}
	var _pages: Array = []
	var _page: int = Page.ROOT
	var _selected_index: int = 0
	var _expanded: bool = false

	func _init(host: Dictionary) -> void:
		_host = host.duplicate(true)
		_pages = [_build_root(), _build_controller(), _build_video(), _build_sound()]
		sync_from_settings()


	func get_page() -> int:
		return _page


	func get_selected_index() -> int:
		return _selected_index


	func is_expanded() -> bool:
		return _expanded


	func get_host() -> Dictionary:
		return _host.duplicate(true)


	func get_settings() -> Dictionary:
		return _settings.duplicate(true)


	func set_setting(name: String, value: Variant) -> Dictionary:
		if not _settings.has(name):
			return V.failure("ArgumentException", "Unknown options setting.", "name")
		var current: Variant = _settings[name]
		if typeof(current) == TYPE_BOOL:
			if not value is bool:
				return V.failure("ArgumentException", "Boolean setting requires a Boolean.", "value")
		elif typeof(current) == TYPE_INT:
			if not V.is_int32(value):
				return V.failure("ArgumentException", "Integer setting requires Int32.", "value")
		else:
			if typeof(value) not in [TYPE_FLOAT, TYPE_INT]:
				return V.failure("ArgumentException", "Float setting requires a number.", "value")
			value = F.value(value)
		_settings[name] = value
		return V.success()


	func get_rows() -> Dictionary:
		var result: Dictionary = _rows()
		if not result.ok:
			return result
		var rows: Array[Dictionary] = []
		for row: Dictionary in result.value:
			rows.append(_row_view(row))
		return V.success(rows)


	func get_selected_row() -> Dictionary:
		var result: Dictionary = _selected()
		return V.success(_row_view(result.value)) if result.ok else result


	func has_pending_changes() -> Dictionary:
		var rows: Dictionary = _rows()
		if not rows.ok:
			return rows
		for row: Dictionary in rows.value:
			if row.timing == Timing.ON_APPLY and row.current_index != row.committed_index:
				return V.success(true)
		return V.success(false)


	func page_height() -> Dictionary:
		var rows: Dictionary = _rows()
		if not rows.ok:
			return rows
		var total: float = 0.0
		for row: Dictionary in rows.value:
			total = F.value(total + row.height)
		return V.success(total)


	func first_row_top() -> Dictionary:
		var height: Dictionary = page_height()
		return V.success(F.value(F.value(300.0 - F.value(height.value * 0.5)) - 15.0)) if height.ok else height


	func row_top(index: Variant) -> Dictionary:
		if not V.is_int32(index):
			return V.failure("ArgumentException", "Row index requires Int32.", "index")
		var top: Dictionary = first_row_top()
		if not top.ok:
			return top
		var rows: Array = _pages[_page]
		var y: float = top.value
		var i: int = 0
		while i < index:
			if i >= rows.size():
				return _index_error()
			y = F.value(y + rows[i].height)
			i += 1
		return V.success(y)


	func row_at(design_y: float) -> Dictionary:
		var top: Dictionary = first_row_top()
		if not top.ok:
			return top
		var y: float = top.value
		design_y = F.value(design_y)
		var rows: Array = _pages[_page]
		for i: int in range(rows.size()):
			var bottom: float = F.value(y + rows[i].height)
			if design_y >= y and design_y < bottom:
				return V.success(i)
			y = bottom
		return V.success(-1)


	func row_state_label(row_index: Variant, state_index: Variant) -> Dictionary:
		if not V.is_int32(row_index) or not V.is_int32(state_index):
			return V.failure("ArgumentException", "Label indices require Int32.", "index")
		var rows: Dictionary = _rows()
		if not rows.ok:
			return rows
		if row_index < 0 or row_index >= rows.value.size():
			return _index_error()
		return _state_label(rows.value[row_index], state_index)


	func enter(page: Variant) -> Dictionary:
		if not V.is_int32(page):
			return V.failure("ArgumentException", "Options page requires Int32.", "page")
		_page = page
		_expanded = false
		sync_from_settings()
		_selected_index = 0
		# An undefined enum value fails here, after the original writes and sync.
		return _ensure_selectable()


	func reset() -> Dictionary:
		_page = Page.ROOT
		_expanded = false
		_selected_index = 0
		sync_from_settings()
		return _ensure_selectable()


	func move_selection(direction: Variant) -> Dictionary:
		if not V.is_int32(direction):
			return V.failure("ArgumentException", "Direction requires Int32.", "direction")
		if direction == 0:
			return V.success(false)
		var rows: Dictionary = _rows()
		if not rows.ok:
			return rows
		if _expanded:
			return _adjust_expanded(signi(direction))
		var candidate: int = _selected_index
		var count: int = rows.value.size()
		for _attempt: int in range(count):
			candidate = V.int32(candidate + signi(direction))
			if candidate < 0 or candidate >= count:
				if count < 3:
					return V.success(false)
				candidate = V.int32(candidate + count) % count
			if _selectable(rows.value[candidate]):
				var moved: bool = candidate != _selected_index
				_selected_index = candidate
				return V.success(moved)
		return V.success(false)


	func hover(index: Variant) -> Dictionary:
		if not V.is_int32(index):
			return V.failure("ArgumentException", "Hover index requires Int32.", "index")
		var rows: Dictionary = _rows()
		if not rows.ok:
			return rows
		if _expanded or index < 0 or index >= rows.value.size() or not _selectable(rows.value[index]):
			return V.success(false)
		var moved: bool = index != _selected_index
		_selected_index = index
		return V.success(moved)


	func hover_state(index: Variant) -> Dictionary:
		if not V.is_int32(index):
			return V.failure("ArgumentException", "State index requires Int32.", "index")
		if not _expanded:
			return V.success(false)
		var selected: Dictionary = _selected()
		if not selected.ok:
			return selected
		var row: Dictionary = selected.value
		if index < 0:
			return V.success(false)
		if row.states == null:
			return _null_states()
		if index >= row.states.size() or index == row.current_index:
			return V.success(false)
		row.current_index = Laws.dropdown_index_after_hit(row.current_index, index, true)
		return V.success(true)


	func cancel_expanded() -> Dictionary:
		if not _expanded:
			return V.success(false)
		var selected: Dictionary = _selected()
		if not selected.ok:
			return selected
		var row: Dictionary = selected.value
		row.current_index = Laws.index_after_cancel(row.current_index, row.committed_index, true)
		_expanded = Laws.expand_after_cancel(_expanded, true)
		return V.success(true)


	func adjust(direction: Variant) -> Dictionary:
		if not V.is_int32(direction):
			return V.failure("ArgumentException", "Direction requires Int32.", "direction")
		if direction == 0:
			return V.success(false)
		var selected: Dictionary = _selected()
		if not selected.ok:
			return selected
		var row: Dictionary = selected.value
		if row.kind == RowKind.DROPDOWN:
			_expanded = true
			return _adjust_expanded(signi(direction))
		if row.kind != RowKind.VALUE_BAR:
			return V.success(false)
		var next: int = V.int32(row.current_index + signi(direction))
		if next < 0 or next > row.max_value:
			return V.success(false)
		row.current_index = next
		row.committed_index = next
		_apply_row(row)
		return V.success(true)


	func confirm() -> Dictionary:
		var selected: Dictionary = _selected()
		if not selected.ok:
			return selected
		var row: Dictionary = selected.value
		if _expanded:
			_expanded = false
			if row.timing == Timing.ON_ROW_CLOSE and row.current_index != row.committed_index:
				row.committed_index = row.current_index
				_apply_row(row)
			return V.success(OptionsSignal.VALUE_CHANGED)
		if row.kind == RowKind.PAGE_LINK:
			var entered: Dictionary = enter(row.target_page)
			return V.success(OptionsSignal.PAGE_CHANGED) if entered.ok else entered
		if row.kind == RowKind.DROPDOWN:
			_expanded = true
			return V.success(OptionsSignal.VALUE_CHANGED)
		if row.kind == RowKind.ACTION:
			if row.action == Action.APPLY:
				var applied: Dictionary = apply_page()
				return V.success(OptionsSignal.APPLIED) if applied.ok else applied
			if row.action == Action.BACK:
				return back()
		return V.success(OptionsSignal.NONE)


	func back() -> Dictionary:
		if _expanded:
			_expanded = false
			return V.success(OptionsSignal.VALUE_CHANGED)
		if _page == Page.ROOT:
			return V.success(OptionsSignal.CLOSED)
		var entered: Dictionary = enter(Page.ROOT)
		return V.success(OptionsSignal.PAGE_CHANGED) if entered.ok else entered


	func apply_page() -> Dictionary:
		var rows: Dictionary = _rows()
		if not rows.ok:
			return rows
		for row: Dictionary in rows.value:
			if row.current_index != row.committed_index:
				row.committed_index = row.current_index
				_apply_row(row)
		return V.success()


	func sync_from_settings() -> Dictionary:
		for page: Array in _pages:
			for row: Dictionary in page:
				var index: int = _read_row(row)
				row.current_index = index
				row.committed_index = index
		return V.success()


	func select_state(index: Variant) -> Dictionary:
		if not V.is_int32(index):
			return V.failure("ArgumentException", "State index requires Int32.", "index")
		var selected: Dictionary = _selected()
		if not selected.ok:
			return selected
		var row: Dictionary = selected.value
		if not _expanded or index < 0:
			return V.success(false)
		if row.states == null:
			return _null_states()
		if index >= row.states.size() or index == row.current_index:
			return V.success(false)
		return _adjust_expanded(V.int32(index - row.current_index))


	func get_bindings() -> Array[Dictionary]:
		var result: Array[Dictionary] = Bindings.rows()
		for row: Dictionary in result:
			if row.kind == Bindings.RowKind.INVERT_WALKER:
				row.slot0 = Bindings.invert_y_label(_settings.invert_y_walker_player1).value
				row.slot1 = Bindings.invert_y_label(_settings.invert_y_walker_player2).value
			elif row.kind == Bindings.RowKind.INVERT_FLIGHT:
				row.slot0 = Bindings.invert_y_label(_settings.invert_y_flight_player1).value
				row.slot1 = Bindings.invert_y_label(_settings.invert_y_flight_player2).value
		return result


	func snapshot() -> Dictionary:
		var pages: Array = []
		for source: Array in _pages:
			var page: Array[Dictionary] = []
			for row: Dictionary in source:
				page.append(_row_view(row))
			pages.append(page)
		return {"page": _page, "selected_index": _selected_index, "is_expanded": _expanded,
			"settings": get_settings(), "pages": pages, "rows": get_rows(), "selected_row": get_selected_row(),
			"has_pending_changes": has_pending_changes(), "page_height": page_height(), "first_row_top": first_row_top()}


	func _rows() -> Dictionary:
		return V.success(_pages[_page]) if _page >= 0 and _page < 4 else \
			V.failure("InvalidOperationException", "Unsupported options page %s." % _page)


	func _selected() -> Dictionary:
		var rows: Dictionary = _rows()
		if not rows.ok:
			return rows
		return V.success(rows.value[_selected_index]) if _selected_index >= 0 and _selected_index < rows.value.size() else _index_error()


	func _ensure_selectable() -> Dictionary:
		var selected: Dictionary = _selected()
		if not selected.ok:
			return selected
		if not _selectable(selected.value):
			var moved: Dictionary = move_selection(1)
			if not moved.ok:
				return moved
		return V.success()


	func _adjust_expanded(step: int) -> Dictionary:
		var selected: Dictionary = _selected()
		if not selected.ok:
			return selected
		var row: Dictionary = selected.value
		if row.states == null:
			return _null_states()
		if row.states.is_empty():
			return V.failure("ArgumentException", "Clamp minimum exceeds maximum.")
		var next: int = clampi(V.int32(row.current_index + step), 0, row.states.size() - 1)
		if next == row.current_index:
			return V.success(false)
		row.current_index = next
		if row.timing == Timing.LIVE:
			row.committed_index = next
			_apply_row(row)
		return V.success(true)


	func _read_row(row: Dictionary) -> int:
		if row.setting.is_empty():
			return row.current_index
		var value: Variant = _settings[row.setting]
		if row.setting == "mouse_sensitivity":
			return Laws.mouse_sensitivity_index(value)
		if row.setting in ["sound_volume", "music_volume"]:
			return Laws.volume_index(value)
		if typeof(value) == TYPE_BOOL:
			return 1 if value else 0
		if row.setting in ["texture_resolution", "enable32_bit_textures"] and value < 0:
			return row.recommended_index
		return value


	func _apply_row(row: Dictionary) -> void:
		if row.setting.is_empty():
			return
		var value: Variant = row.committed_index
		if row.setting == "mouse_sensitivity":
			value = Laws.mouse_sensitivity_value(value)
		elif row.setting in ["sound_volume", "music_volume"]:
			value = Laws.volume_value(value)
		elif typeof(_settings[row.setting]) == TYPE_BOOL:
			value = value != 0
		_settings[row.setting] = value


	static func _selectable(row: Dictionary) -> bool:
		return row.kind not in [RowKind.BINDINGS, RowKind.STATUS]


	static func _index_error() -> Dictionary:
		return V.failure("ArgumentOutOfRangeException", "Options row index is outside the list.", "index")


	static func _null_states() -> Dictionary:
		return V.failure("NullReferenceException", "Options state list is null.")


	static func _state_label(row: Dictionary, index: int) -> Dictionary:
		if row.states == null:
			return _null_states()
		if row.states.is_empty():
			return V.success(PackedInt32Array())
		var clamped: int = clampi(index, 0, row.states.size() - 1)
		var value: Variant = row.recommended_states[clamped] if clamped == row.recommended_index \
			and row.recommended_states.size() == row.states.size() else row.states[clamped]
		return V.success(null if value == null else value.duplicate())


	static func _row_view(row: Dictionary) -> Dictionary:
		var result: Dictionary = row.duplicate(true)
		result.erase("setting")
		result.is_selectable = _selectable(row)
		result.current_state = _state_label(row, row.current_index)
		return result


	static func _text_list(values: Array) -> Array:
		var result: Array = []
		for value: String in values:
			result.append(Text.units(value).value)
		return result


	static func _row(kind: int, label: String, states: Variant = [], timing: int = Timing.LIVE,
			setting: String = "", height: float = 20.0, action: int = Action.NONE,
			target: int = Page.ROOT, max_value: int = 0, recommended: int = -1,
			recommended_states: Array = []) -> Dictionary:
		return {"kind": kind, "label": label, "states": null if states == null else states.duplicate(true),
			"timing": timing, "height": height, "target_page": target, "action": action,
			"max_value": max_value, "current_index": 0, "committed_index": 0,
			"recommended_index": recommended, "recommended_states": recommended_states.duplicate(true), "setting": setting}


	static func _drop(label: String, states: Array, timing: int, setting: String) -> Dictionary:
		return _row(RowKind.DROPDOWN, label, _text_list(states), timing, setting)


	static func _build_root() -> Array[Dictionary]:
		return [_row(RowKind.PAGE_LINK, "Controller Options", [], Timing.LIVE, "", 20.0, Action.NONE, Page.CONTROLLER),
			_row(RowKind.PAGE_LINK, "Sound Options", [], Timing.LIVE, "", 20.0, Action.NONE, Page.SOUND),
			_row(RowKind.PAGE_LINK, "Video Options", [], Timing.LIVE, "", 20.0, Action.NONE, Page.VIDEO),
			_row(RowKind.ACTION, "Credits", [], Timing.LIVE, "", 20.0, Action.CREDITS)]


	static func _build_controller() -> Array[Dictionary]:
		return [_row(RowKind.VALUE_BAR, "Mouse sensitivity:", [], Timing.LIVE, "mouse_sensitivity", 20.0, Action.NONE, Page.ROOT, 20),
			_drop("Configuration:", ["Custom", "WASD + mouse"], Timing.ON_ROW_CLOSE, "controller_configuration"),
			_row(RowKind.BINDINGS, "", [], Timing.LIVE, "", 230.0),
			_row(RowKind.STATUS, "Joystick 1: Not present", [], Timing.LIVE, "", 17.0),
			_row(RowKind.STATUS, "Joystick 2: Not present", [], Timing.LIVE, "", 17.0),
			_row(RowKind.STATUS, "Joystick 3: Not present", [], Timing.LIVE, "", 17.0),
			_row(RowKind.STATUS, "Joystick 4: Not present", [], Timing.LIVE, "", 17.0),
			_row(RowKind.ACTION, "Back", [], Timing.LIVE, "", 20.0, Action.BACK)]


	func _build_video() -> Array[Dictionary]:
		return [_drop("Extra graphical features:", ["Not available"], Timing.ON_APPLY, ""),
			_drop("Overall Detail level:", ["Custom", "Lowest", "Medium", "High"], Timing.ON_ROW_CLOSE, "overall_detail"),
			_row(RowKind.DROPDOWN, "Screen mode:", _host.screen_modes, Timing.ON_APPLY),
			_drop("Shadow detail:", ["Low", "Medium", "High"], Timing.ON_ROW_CLOSE, "shadow_detail"),
			_drop("Geometry detail:", ["Low", "Medium", "High"], Timing.ON_ROW_CLOSE, "geometry_detail"),
			_drop("Trilinear mipmapping:", ["No", "Yes"], Timing.ON_ROW_CLOSE, "trilinear_mipmapping"),
			_row(RowKind.DROPDOWN, "Video adapter:", _host.video_adapters, Timing.ON_APPLY),
			_drop("VSync:", ["No", "Yes"], Timing.ON_APPLY, "v_sync"),
			_drop("Landscape resolution:", ["Lowest", "Low", "Medium", "High"], Timing.ON_ROW_CLOSE, "landscape_resolution"),
			_row(RowKind.DROPDOWN, "Texture Resolution:", _text_list(["High", "Medium", "Low"]), Timing.ON_APPLY,
				"texture_resolution", 20.0, Action.NONE, Page.ROOT, 0, _host.recommended_texture_resolution,
				_text_list(["High (Recommended)", "Medium (Recommended)", "Low (Recommended)"])),
			_row(RowKind.DROPDOWN, "Enable 32 bit textures:", _text_list(["No", "Only Where Obvious", "Yes"]), Timing.ON_APPLY,
				"enable32_bit_textures", 20.0, Action.NONE, Page.ROOT, 0, _host.recommended_enable32_bit_textures,
				_text_list(["No (Recommended)", "Only Where Obvious (Recommended)", "Yes (Recommended)"])),
			_row(RowKind.DROPDOWN, "Full-screen anti-aliasing level:", _host.anti_aliasing_levels, Timing.ON_APPLY),
			_row(RowKind.ACTION, "Apply", [], Timing.LIVE, "", 20.0, Action.APPLY),
			_row(RowKind.ACTION, "Back", [], Timing.LIVE, "", 20.0, Action.BACK)]


	func _build_sound() -> Array[Dictionary]:
		return [_row(RowKind.VALUE_BAR, "Sound Volume", [], Timing.LIVE, "sound_volume", 20.0, Action.NONE, Page.ROOT, 10),
			_row(RowKind.VALUE_BAR, "Music Volume", [], Timing.LIVE, "music_volume", 20.0, Action.NONE, Page.ROOT, 10),
			_drop("Swap left/right speakers:", ["No", "Yes"], Timing.ON_ROW_CLOSE, "swap_speakers"),
			_drop("3D Sound hardware acceleration:", ["No", "Yes"], Timing.ON_APPLY, "hardware_sound"),
			_drop("Sound quality:", ["High (44 Khz, 16 bit)", "Medium (22 Khz, 16 bit)", "Low (11 Khz, 8 bit)"], Timing.ON_APPLY, "sound_quality"),
			_row(RowKind.DROPDOWN, "Select Sound Device:", _host.sound_devices, Timing.ON_APPLY),
			_drop("3D Sound Quality:", ["High ('Full HRTF')", "Medium ('Light HRTF')", "Low (Left/Right panning)"], Timing.ON_APPLY, "sound_method3_d"),
			_row(RowKind.ACTION, "Apply", [], Timing.LIVE, "", 20.0, Action.APPLY),
			_row(RowKind.ACTION, "Back", [], Timing.LIVE, "", 20.0, Action.BACK)]


static func create(host: Variant = null) -> Dictionary:
	if host == null:
		host = {"screen_modes": ["640 x 480"], "video_adapters": ["Unknown"], "anti_aliasing_levels": ["None"],
			"sound_devices": ["No sound device available"], "recommended_texture_resolution": 0, "recommended_enable32_bit_textures": 2}
	if not host is Dictionary:
		return V.failure("ArgumentException", "Host facts require a dictionary.", "host")
	var admitted: Dictionary = {}
	for name: String in ["screen_modes", "video_adapters", "anti_aliasing_levels", "sound_devices"]:
		if not host.has(name) or (host[name] != null and not host[name] is Array):
			return V.failure("ArgumentException", "Host state lists require arrays or null.", name)
		if host[name] == null:
			admitted[name] = null
			continue
		admitted[name] = []
		for value: Variant in host[name]:
			var text: Dictionary = Text.units(value)
			if not text.ok:
				return text
			admitted[name].append(text.value)
	for name: String in ["recommended_texture_resolution", "recommended_enable32_bit_textures"]:
		if not V.is_int32(host.get(name)):
			return V.failure("ArgumentException", "Recommendation requires an Int32.", name)
		admitted[name] = host[name]
	return V.success(Menu.new(admitted))
