# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Differential execution of production pure Options modules. Only this harness
## reads the explicit oracle path and writes the explicit task-owned report.

const Options = preload("res://Client/options_menu.gd")
const Controller = preload("res://Client/options_controller.gd")
const Laws = preload("res://Client/options_laws.gd")
const V = preload("res://Core/retail_career_values.gd")
var failures: Array[Dictionary] = []
var counts: Dictionary = {}
var completed: Array[String] = []


func _initialize() -> void:
	call_deferred("run_checks")


func check(group: String, name: String, actual: Variant, expected: Variant) -> void:
	counts[group] = int(counts.get(group, 0)) + 1
	if actual != expected:
		failures.append({"group": group, "name": name, "actual": actual, "expected": expected})


func normalize(value: Variant) -> Variant:
	if typeof(value) == TYPE_FLOAT:
		if not is_finite(value) or value != floor(value) or value < -2147483648.0 or value > 4294967295.0:
			check("fixture", "exact integer/IEEE word transport", value, "Int32/UInt32 word")
		return int(value)
	if value is Array:
		var result: Array = []
		for item: Variant in value:
			result.append(normalize(item))
		return result
	if value is Dictionary:
		var result: Dictionary = {}
		for key: String in value:
			result[key] = normalize(value[key])
		return result
	return value


func plain(value: Variant) -> Variant:
	if typeof(value) == TYPE_PACKED_INT32_ARRAY:
		return Array(value)
	if value is Array:
		var result: Array = []
		for item: Variant in value:
			result.append(plain(item))
		return result
	if value is Dictionary:
		if value.has("ok"):
			return {"ok": true, "value": plain(value.get("value"))} if value.ok else \
				{"ok": false, "error_type": value.error_type, "parameter": value.get("parameter", "")}
		var result: Dictionary = {}
		for key: String in value:
			result[key] = plain(value[key])
		return result
	return value


func from_word(word: int) -> float:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_u32(0, word)
	return bytes.decode_float(0)


func host_facts(value: Variant) -> Variant:
	if value == null:
		return null
	var result: Dictionary = value.duplicate(true)
	for name: String in ["screen_modes", "video_adapters", "anti_aliasing_levels", "sound_devices"]:
		if result[name] != null:
			for index: int in range(result[name].size()):
				if result[name][index] != null:
					result[name][index] = PackedInt32Array(result[name][index])
	return result


func row_words(row: Dictionary) -> Dictionary:
	var result: Dictionary = row.duplicate(true)
	result.height = V.float32_word(result.height)
	return result


func state(menu: Options.Menu) -> Dictionary:
	var result: Dictionary = menu.snapshot()
	for name: String in ["sound_volume", "music_volume", "mouse_sensitivity"]:
		result.settings[name] = V.float32_word(result.settings[name])
	var pages: Array = []
	for page: Array in result.pages:
		var values: Array = []
		for row: Dictionary in page:
			values.append({"current_index": row.current_index, "committed_index": row.committed_index})
		pages.append(values)
	result.pages = pages
	if result.rows.ok:
		for index: int in range(result.rows.value.size()):
			result.rows.value[index] = row_words(result.rows.value[index])
	if result.selected_row.ok:
		result.selected_row.value = row_words(result.selected_row.value)
	for name: String in ["page_height", "first_row_top"]:
		if result[name].ok:
			result[name].value = V.float32_word(result[name].value)
	return plain(result)


func numeric(operation: String, a: Array) -> Dictionary:
	var value: Variant
	match operation:
		"mouse_index": value = Laws.mouse_sensitivity_index(from_word(a[0]))
		"volume_index": value = Laws.volume_index(from_word(a[0]))
		"mouse_value": value = V.float32_word(Laws.mouse_sensitivity_value(a[0]))
		"volume_value": value = V.float32_word(Laws.volume_value(a[0]))
		"pulse_channel": value = Laws.pulse_channel(from_word(a[0]))
		"pulse_color": value = Laws.pulse_packed_color(a[0], from_word(a[1]))
		"integer_half": value = Laws.integer_half(a[0])
		"dropdown_width": value = Laws.dropdown_width(a[0])
		"panel_width": value = V.float32_word(Laws.dropdown_panel_width(a[0]))
		"item_x": value = V.float32_word(Laws.menu_item_dest_x(from_word(a[0]), a[1]))
		"item_scale": value = V.float32_word(Laws.menu_item_scale(from_word(a[0]), a[1]))
		"icon_x": value = V.float32_word(Laws.menu_icon_dest_x(from_word(a[0]), a[1]))
		"icon_scale": value = V.float32_word(Laws.menu_icon_scale(from_word(a[0]), a[1]))
		"hit_right": value = V.float32_word(Laws.dropdown_hit_right(from_word(a[0]), a[1]))
		"dropdown_x": value = V.float32_word(Laws.dropdown_dest_x(from_word(a[0]), a[1]))
		"dropdown_scale": value = V.float32_word(Laws.dropdown_scale(from_word(a[0]), a[1]))
		"value_x": value = V.float32_word(Laws.dropdown_value_x(from_word(a[0])))
		"list_x": value = V.float32_word(Laws.dropdown_list_x(from_word(a[0])))
		"panel_y": value = V.float32_word(Laws.dropdown_panel_y(from_word(a[0]), a[1], a[2]))
		"list_scale": value = V.float32_word(Laws.dropdown_list_scale(a[0], a[1]))
		"list_y": value = V.float32_word(Laws.dropdown_list_y(from_word(a[0]), a[1], a[2], a[3]))
		"hit_bottom": value = V.float32_word(Laws.dropdown_hit_bottom(from_word(a[0]), a[1], a[2], a[3]))
		"contains": value = Laws.dropdown_contains(from_word(a[0]), from_word(a[1]), from_word(a[2]), from_word(a[3]), a[4], a[5])
		"list_color": value = Laws.dropdown_list_color(a[0], a[1])
		"row_is_pending": value = Laws.dropdown_row_is_pending(a[0], a[1])
		"hit_index": value = Laws.dropdown_index_after_hit(a[0], a[1], a[2])
		"cancel_index": value = Laws.index_after_cancel(a[0], a[1], a[2])
		"applies_live": value = Laws.dropdown_applies_live(a[0], a[1], a[2])
		"helper_nonzero": value = Laws.cancel_helper_nonzero(a[0], a[1])
		"cancel_applies": value = Laws.cancel_applies(a[0], a[1])
		"should_pulse": value = Laws.should_pulse(a[0])
		"click_sound_applies": value = Laws.dropdown_click_sound_applies(a[0])
		"expand_after_click": value = Laws.dropdown_expand_after_click(a[0], a[1])
		"expand_after_cancel": value = Laws.expand_after_cancel(a[0], a[1])
		"menu_color": value = Laws.menu_packed_color(a[0], a[1], a[2])
		_: return V.failure("InvalidOperationException", "Unknown numeric fixture operation.")
	return V.success(value)


func execute(menu: Options.Menu, controller: RefCounted, step: Dictionary) -> Dictionary:
	var a: int = step.get("a", 0)
	match step.operation:
		"enter": return menu.enter(a)
		"reset": return menu.reset()
		"move": return menu.move_selection(a)
		"hover": return menu.hover(a)
		"hover_state": return menu.hover_state(a)
		"cancel": return menu.cancel_expanded()
		"adjust": return menu.adjust(a)
		"confirm": return menu.confirm()
		"back": return menu.back()
		"apply": return menu.apply_page()
		"sync": return menu.sync_from_settings()
		"select": return menu.select_state(a)
		"top":
			var result: Dictionary = menu.row_top(a)
			return V.success(V.float32_word(result.value)) if result.ok else result
		"at": return menu.row_at(from_word(step.value))
		"label": return menu.row_state_label(a, step.b)
		"set":
			var value: Variant = from_word(step.value) if step.setting in ["sound_volume", "music_volume", "mouse_sensitivity"] else step.value
			return menu.set_setting(step.setting, value)
		"controller_key":
			var mask: int = step.mask
			return controller.key_matches((mask & 1) != 0, (mask & 2) != 0, (mask & 4) != 0, (mask & 8) != 0, (mask & 16) != 0, (mask & 32) != 0)
		"controller_motion": return controller.pointer_motion(from_word(step.x), from_word(step.y), from_word(step.width))
		"controller_click": return controller.pointer_confirm(from_word(step.x), from_word(step.y), from_word(step.width))
		"controller_cancel": return controller.pointer_cancel(step.mask != 0)
	return V.failure("InvalidOperationException", "Unknown state fixture operation.")


func scenarios(group: String, fixtures: Array) -> void:
	for fixture: Dictionary in fixtures:
		var created: Dictionary = Options.create(host_facts(fixture.host))
		check(group, fixture.name + ":create", created.ok, true)
		if not created.ok:
			continue
		var menu: Options.Menu = created.value
		var controller: RefCounted = Controller.new(menu)
		check(group, fixture.name + ":initial", state(menu), fixture.initial)
		for index: int in range(fixture.steps.size()):
			var step: Dictionary = fixture.steps[index]
			var name: String = fixture.name + ":" + str(index) + ":" + step.operation
			var result: Dictionary = execute(menu, controller, step)
			check(group, name + ":result", plain(result), step.expected)
			if step.has("effects"):
				check(group, name + ":ordered host effects", result.get("effects"), step.effects)
			check(group, name + ":state", state(menu), step.snapshot)


func ownership() -> void:
	var host: Dictionary = {"screen_modes": ["First", "Second"], "video_adapters": ["Adapter"],
		"anti_aliasing_levels": ["None"], "sound_devices": ["Sound"],
		"recommended_texture_resolution": 0, "recommended_enable32_bit_textures": 2}
	var menu: Options.Menu = Options.create(host).value
	menu.enter(Options.Page.VIDEO)
	var before: Dictionary = state(menu)
	host.screen_modes[0] = "Changed source facts"
	var read: Dictionary = menu.get_rows()
	read.value[2].states[0][0] = 0
	read.value[2].current_index = 2
	var settings: Dictionary = menu.get_settings()
	settings.sound_volume = 0.0
	var capture: Dictionary = menu.snapshot()
	capture.pages[0][0].current_index = 99
	var bindings: Array[Dictionary] = menu.get_bindings()
	bindings[0].label = "Changed display"
	check("ownership", "host, rows, settings, snapshot and binding reads are detached", state(menu), before)
	for entry: Array in [["sound_volume", "not a number"], ["v_sync", 1], ["sound_quality", 2147483648], ["absent", 0]]:
		check("ownership", "invalid setting transport rejects", menu.set_setting(entry[0], entry[1]).ok, false)
		check("ownership", "invalid setting leaves state", state(menu), before)
	for method: String in ["enter", "move_selection", "hover", "hover_state", "adjust", "select_state", "row_top"]:
		check("ownership", method + ":Int32 admission", menu.call(method, 2147483648).ok, false)
		check("ownership", method + ":admission precedes writes", state(menu), before)
	var controller: RefCounted = Controller.new(menu)
	var effects: Dictionary = controller.key_matches(false, true, false, false, false, false)
	if not effects.effects.is_empty():
		effects.effects[0].kind = "changed"
	check("ownership", "returned controller effects are detached", controller.key_matches(false, true, false, false, false, false).effects[0].kind, "audio")
	for invalid: Variant in [false, [], {}, {"screen_modes": 2}]:
		check("ownership", "invalid host admission", Options.create(invalid).ok, false)


func run_checks() -> void:
	var arguments: PackedStringArray = OS.get_cmdline_user_args()
	if arguments.size() != 2:
		printerr("options_checks requires oracle JSON and an owned report path")
		quit(2)
		return
	var document: Variant = JSON.parse_string(FileAccess.get_file_as_string(arguments[0]))
	if not document is Dictionary or not document.has("options"):
		printerr("Options fixtures are missing")
		quit(2)
		return
	var data: Dictionary = normalize(document.options)
	var constants: Dictionary = {"row_height": V.float32_word(Options.ROW_HEIGHT),
		"bindings_row_height": V.float32_word(Options.BINDINGS_ROW_HEIGHT), "joystick_row_height": V.float32_word(Options.JOYSTICK_ROW_HEIGHT),
		"range_origin_y": V.float32_word(Options.RANGE_ORIGIN_Y), "range_top_inset": V.float32_word(Options.RANGE_TOP_INSET),
		"mouse_sensitivity_step": V.float32_word(Options.MOUSE_SENSITIVITY_STEP), "mouse_sensitivity_max_value": Options.MOUSE_SENSITIVITY_MAX_VALUE,
		"default_mouse_sensitivity": V.float32_word(Options.DEFAULT_MOUSE_SENSITIVITY), "volume_max_value": Options.VOLUME_MAX_VALUE,
		"value_row_seed_bias": V.float32_word(Options.VALUE_ROW_SEED_BIAS)}
	check("numeric", "source constants", constants, data.constants)
	for index: int in range(data.numeric.size()):
		var row: Dictionary = data.numeric[index]
		check("numeric", str(index) + ":" + row.operation, plain(numeric(row.operation, row.input)), row.expected)
	completed.append("numeric")
	scenarios("state", data.scenarios)
	completed.append("state")
	scenarios("controller", data.controllers)
	for fixture: Dictionary in data.bindings:
		var menu: Options.Menu = Options.create().value
		for pair: Array in [["invert_y_walker_player1", 1], ["invert_y_walker_player2", 2],
			["invert_y_flight_player1", 4], ["invert_y_flight_player2", 8]]:
			menu.set_setting(pair[0], (fixture.flags & pair[1]) != 0)
		check("controller", "shared binding table:" + str(fixture.flags), menu.get_bindings(), fixture.expected)
	completed.append("controller")
	ownership()
	completed.append("ownership")
	var report: Dictionary = {"schema": 1, "failure_count": failures.size(), "failures": failures,
		"counts": counts, "completed": completed, "fixtures": {"numeric": data.numeric.size(), "state_scenarios": data.scenarios.size(),
			"controller_scenarios": data.controllers.size(), "binding_states": data.bindings.size()}}
	var output: FileAccess = FileAccess.open(arguments[1], FileAccess.WRITE)
	if output == null:
		printerr("Cannot open requested owned report path")
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t") + "\n")
	output.close()
	print("options_checks: ", counts, " failures=", failures.size(), " completed=", completed, " fixtures=", report.fixtures)
	quit(0 if failures.is_empty() and completed.size() == 4 else 1)
