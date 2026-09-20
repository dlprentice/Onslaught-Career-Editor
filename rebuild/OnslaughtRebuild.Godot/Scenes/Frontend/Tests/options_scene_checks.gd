# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual Options scene checks. Optional captures use the caller's isolated
## display and an existing owned output directory; this never starts a display.
const OptionsView = preload("res://Scenes/Frontend/options_presentation.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Options = preload("res://Client/options_menu.gd")
const Laws = preload("res://Client/options_laws.gd")
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _capture_dir: String = ""


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--options-scene-capture-dir="):
			_capture_dir = argument.trim_prefix("--options-scene-capture-dir=")
			var owned: String = ProjectSettings.globalize_path("res://../../local-data/").simplify_path().trim_suffix("/") + "/"
			if not _check(_capture_dir.is_absolute_path() and _capture_dir.simplify_path().begins_with(owned) and DirAccess.dir_exists_absolute(_capture_dir), "Capture output must exist under this worktree's local-data."):
				quit(1)
				return
			if not _check(DisplayServer.get_name() != "headless", "Capture requires the caller's isolated rendered display."):
				quit(1)
				return
	var pointer_before: int = Input.mouse_mode
	var packed: PackedScene = load("res://Scenes/Frontend/Options.tscn")
	var view: OptionsView = packed.instantiate()
	var page_counts: Array[int] = [4, 8, 14, 9]
	var first_tops: Array[float] = [245.0, 106.0, 145.0, 195.0]
	_check(view.get_node("Pages").get_child_count() == 4, "Four authored pages exist before Ready.")
	for page: int in range(4):
		var node: Control = view.get_node("Pages/" + OptionsView.PAGE_NAMES[page])
		_check(node.get_child_count() == page_counts[page], "Authored row inventory matches page %d." % page)
		_check(node.get_child(0).position.y == first_tops[page], "Source row origin matches page %d." % page)
		for index: int in range(node.get_child_count()):
			_check(node.get_child(index).row_index == index, "Authored row identity is sequential.")
	for node: Node in view.find_children("*", "Control", true, false):
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "Authored Options controls load in the standard engine.")
		_check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE, "Scene does not capture pointer events independently.")
	_check(view.get_node("Pages/Controller/Bindings/Grid").get_child_count() == 22, "Bindings are 22 authored row controls.")
	_check(view.get_node("Pages/Controller/MouseSensitivity/Bar/Segments").get_child_count() == 20, "Mouse bar has 20 editable native segments.")
	_check(view.get_node("Pages/Sound/SoundVolume/Bar/Segments").get_child_count() == 10, "Volume bar has 10 editable native segments.")
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640, 480)
	viewport.disable_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	viewport.add_child(view)
	await process_frame
	await process_frame
	_check(view.get("_last_error") == "", "Production Options assets initialize.")
	_check(not view.is_processing() and not view.is_processing_input() and not view.is_processing_unhandled_input(), "Only the host drives time and input.")
	_check(view.body_font.glyph_widths().size() == 256 and view.title_font.glyph_widths().size() == 256, "Both production fonts retain the full atlas slot range.")
	_check(view.body_font.page.get_image().get_width() == 256 and view.title_font.page.get_image().get_width() == 512, "Same production atlases are available to native rows and the retained frontend.")
	_check(view.get_node("Underlay/Clear").color == Color(31.0 / 255.0, 31.0 / 255.0, 63.0 / 255.0, 1.0), "Options keeps the measured clear term.")
	_check(view.get_node("Underlay/Darkener").color == Color(0.0, 0.0, 0.0, 62.0 / 255.0), "Options keeps the independent 62/255 darkener.")
	_check(view.get_node("Underlay/Video").texture != null, "A real FEBack composite frame is visible.")
	_done("authored_scene")

	view.reset_menu()
	view.set_frame(0.25, 0.0)
	await _capture(viewport, "options-root.png")
	view.select_row(3)
	var credits: Dictionary = _key(view, "confirm")
	_check(credits.effects.is_empty() and credits.page == 0, "Unimplemented Credits remains a silent no-op.")
	view.select_row(0)
	var entered: Dictionary = _key(view, "confirm")
	_check(_effects(entered) == ["audio:1", "apply_settings", "redraw"] and entered.page == 1, "Entering Controller preserves ordered effects.")
	_check(view.view_snapshot().settings.mouse_sensitivity == 7.0, "Raw authored mouse setting is not replaced by its bar projection.")
	_check(view.view_snapshot().rows.value[0].current_index == 2, "Mouse seed bias projects to the original index.")
	var moved: Dictionary = _key(view, "right")
	_check(moved.settings.mouse_sensitivity == 12.0 and _effects(moved) == ["audio:0", "apply_settings", "redraw"], "Live bar adjustment commits and notifies in order.")
	var grid: Node = view.get_node("Pages/Controller/Bindings/Grid")
	_check(grid.get_node("Binding01/Slot0").displayed_units() == AtlasFont.units("On"), "Invert-Y display preserves the opposite-label law.")
	_check(grid.get_node("Binding18/Slot1").displayed_units() == AtlasFont.units("Key ;"), "Shared binding labels reach authored controls.")
	await _capture(viewport, "options-controller.png")
	_key(view, "back")
	view.select_row(2)
	_key(view, "confirm")
	view.select_row(7)
	_key(view, "right")
	_check(view.view_snapshot().is_expanded and not view.view_snapshot().settings.v_sync, "VSync remains deferred while its pending value changes.")
	_key(view, "confirm")
	_check(not view.view_snapshot().is_expanded and view.view_snapshot().has_pending_changes.value, "Closing an OnApply dropdown retains pending state.")
	view.set_frame(0.125, 0.0)
	var pulse: Color = view.get_node("Pages/Video/VSync/Caption").get("_tint")
	_check(pulse == preload("res://Scenes/Frontend/options_row.gd").retail_color(Laws.pulse_packed_color(true, 0.125)), "Pending dropdown uses the exact packed pulse law.")
	view.select_row(12)
	var applied: Dictionary = _key(view, "confirm")
	_check(applied.settings.v_sync and not view.view_snapshot().has_pending_changes.value, "Apply commits the pending video setting.")
	view.select_row(7)
	_key(view, "left")
	var cancelled: Dictionary = view.pointer_cancel(true)
	_check(cancelled.ok and _effects(cancelled) == ["audio:2", "redraw"], "Right cancel only emits Back/redraw.")
	_check(view.view_snapshot().rows.value[7].current_index == 1 and view.view_snapshot().settings.v_sync, "Right cancel restores the committed index.")
	_key(view, "left")
	_key(view, "back")
	_check(not view.view_snapshot().is_expanded and view.view_snapshot().rows.value[7].current_index == 0, "Back closes without applying or reverting the expanded value.")
	_check(view.view_snapshot().settings.v_sync, "Back does not apply a deferred setting.")
	await _capture(viewport, "options-video.png")
	_key(view, "back")
	view.select_row(1)
	_key(view, "confirm")
	view.select_row(1)
	var clicked: Dictionary = view.pointer_confirm(Vector2(0.0, 196.0))
	_check(_effects(clicked) == ["audio:0", "audio:0", "apply_settings", "redraw"], "Clicking an unselected value bar preserves hover and adjustment effects.")
	_check(clicked.effect_settings.size() == 4 and clicked.effect_settings[0].sound_volume == F32(0.8)
		and clicked.effect_settings[1].sound_volume == F32(0.7) and clicked.settings.sound_volume == F32(0.7),
		"Coarse host handoff retains settings observed before and after the adjustment.")
	view.select_row(4)
	_key(view, "confirm")
	var entry: Control = view.get_node("Dropdown/Entries/State01")
	var hover: Dictionary = view.pointer_motion(entry.position + Vector2(1, 1))
	_check(hover.ok and _effects(hover) == ["audio:0"], "Dropdown hover changes current state with Move only.")
	_check(view.view_snapshot().settings.sound_quality == 0, "Hovered sound quality remains uncommitted.")
	var panel: ColorRect = view.get_node("Dropdown/Panel")
	_check(panel.position == Vector2(321, Laws.dropdown_panel_y(275, 3, 16)) and panel.size.y == 48, "Popup retains panel position and unscaled height.")
	var width: float = view.body_font.measure("Sound quality:")
	_check(not view.pointer_motion(Vector2(323 + width, entry.position.y + 1)).value, "Expanded hover keeps the exclusive label-width right edge.")
	var closed: Dictionary = view.pointer_confirm(Vector2(620, 420))
	_check(closed.ok and not view.view_snapshot().is_expanded and view.view_snapshot().settings.sound_quality == 0, "Outside click closes through Confirm while preserving OnApply timing.")
	view.select_row(7)
	_key(view, "confirm")
	_check(view.view_snapshot().settings.sound_quality == 1, "Sound Apply commits its pending row.")
	view.set_frame(0.25, 0.0)
	await _capture(viewport, "options-sound.png")
	_key(view, "back")
	_check(_effects(_key(view, "back")) == ["frontend_back"], "Root Back requests the existing frontend owner.")
	_done("controller_and_settings")

	# Injected user-action effects stop at the source failure point and permit
	# synchronous observer reentry without overwriting the outer result journal.
	view.reset_menu()
	view.select_row(1)
	_key(view, "confirm")
	view.select_row(1)
	var volume_before: float = view.view_snapshot().settings.sound_volume
	var observer_calls: Array[Dictionary] = []
	view.set_effect_handler(func(effect: Dictionary, settings: Dictionary) -> Dictionary:
		observer_calls.append({"effect": effect.duplicate(true), "settings": settings.duplicate(true)})
		return {"ok": false, "error_type": "IOException", "error": "synthetic observer failure"})
	var failed: Dictionary = view.pointer_confirm(Vector2(639.0, 196.0))
	_check(not failed.ok and failed.error_type == "IOException" and observer_calls.size() == 1,
		"Observer failure aborts after the first source effect.")
	_check(view.view_snapshot().selected_index == 0 and failed.settings.sound_volume == volume_before,
		"Observer failure keeps hover selection but prevents the later adjustment.")
	view.set_effect_handler(Callable())
	view.select_row(1)
	var reentered: Array[bool] = [false]
	var inner_results: Array[Dictionary] = []
	view.set_effect_handler(func(effect: Dictionary, _settings: Dictionary) -> Dictionary:
		if effect.kind == "audio" and not reentered[0]:
			reentered[0] = true
			inner_results.append(view.handle_key(false, false, false, true, false, false))
		return {"ok": true})
	var outer: Dictionary = view.pointer_confirm(Vector2(639.0, 196.0))
	_check(outer.ok and reentered[0] and inner_results.size() == 1 and inner_results[0].ok,
		"Synchronous nested action succeeds through the same sole controller.")
	_check(_effects(outer) == ["audio:0", "audio:0", "apply_settings", "redraw"]
		and _effects(inner_results[0]) == ["audio:0", "apply_settings", "redraw"],
		"Nested and outer effect journals remain separate.")
	view.set_effect_handler(Callable())
	_done("observer_failure_and_reentry")

	var host: Dictionary = {"screen_modes": ["640 x 480"], "video_adapters": [PackedInt32Array([65, 0, 66, 0xd83d, 0xde80])], "anti_aliasing_levels": ["None"], "sound_devices": ["Primary Sound Driver"], "recommended_texture_resolution": 0, "recommended_enable32_bit_textures": 2}
	_check(view.configure_host(host).ok, "Verified host facts are admitted once.")
	host.video_adapters[0][0] = 90
	view.select_row(2)
	_key(view, "confirm")
	_check(view.get_node("Pages/Video/Adapter/Value").displayed_units() == PackedInt32Array([65, 0, 66, 0xd83d, 0xde80]), "Raw host labels retain NUL and both surrogate units without aliasing.")
	var snapshot: Dictionary = view.view_snapshot()
	snapshot.settings.sound_volume = 0.0
	_check(view.view_snapshot().settings.sound_volume != 0.0, "Detached snapshot mutation cannot change the menu.")
	_check(not view.configure_host({}).ok and view.view_snapshot().page == 2, "Invalid host admission does not replace the live owner.")
	_check_font()
	_done("text_and_ownership")

	var edited: Control = view.get_node("Pages/Video/ShadowDetail")
	var original: Vector2 = edited.position
	edited.position += Vector2(10, 5)
	view.set_frame(0.5, 0.0)
	_check(edited.position == original + Vector2(10, 5) and edited.source_rect.position.y == original.y, "Time updates preserve authored layout and separate source geometry.")
	if Engine.is_editor_hint():
		view.editor_page = 3
		view.editor_selected_row = 4
		view.editor_expanded = true
		_check(view.get_node("Pages/Sound").visible and view.get_node("Dropdown").visible, "Inspector preview opens the same production dropdown.")
		_check(not view.is_processing() and not view.is_processing_input(), "Inspector editing never activates a clock or input owner.")
	var roundtrip := PackedScene.new()
	_check(roundtrip.pack(view) == OK, "Options production scene can be repacked.")
	var state: SceneState = roundtrip.get_state()
	for index: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(index)):
			_stored(state.get_node_property_value(index, property), {})
	var reloaded: OptionsView = roundtrip.instantiate()
	viewport.add_child(reloaded)
	await process_frame
	_check(reloaded.get_node("Pages/Video/ShadowDetail").position == edited.position, "Scene roundtrip preserves the authored row edit.")
	_check(view.find_children("*", "AudioStreamPlayer", true, false).is_empty() and view.find_children("*", "Camera3D", true, false).is_empty(), "Options creates no gameplay or playback owner.")
	_check(Input.mouse_mode == pointer_before, "Scene activity leaves pointer mode unchanged.")
	reloaded.queue_free()
	view.queue_free()
	viewport.queue_free()
	await process_frame
	await process_frame
	_done("editor_and_publication")
	print("OPTIONS_SCENE_CHECKS: ", JSON.stringify({"schema": 1, "checks": _checks, "failure_count": _failures.size(), "failures": _failures, "completed": _completed, "editor": Engine.is_editor_hint()}))
	quit(0 if _failures.is_empty() else 1)


func _check_font() -> void:
	var image := Image.create_empty(256, 256, false, Image.FORMAT_RGBA8)
	image.set_pixel(16 + 13, 0, Color(1, 1, 1, 16.0 / 255.0))
	var widths: PackedInt32Array = AtlasFont.measure_widths(image, 16, 16)
	_check(widths[0] == 8 and widths[1] == 2, "Font scan preserves space width and strict alpha cutoff.")
	image.set_pixel(16 + 13, 0, Color(1, 1, 1, 17.0 / 255.0))
	image.set_pixel(32 + 14, 15, Color.WHITE)
	widths = AtlasFont.measure_widths(image, 16, 16)
	_check(widths[1] == 15 and widths[2] == 2, "Font scan keeps right bearing and excludes the last cell row.")
	_check(AtlasFont.glyph_index(287) == 255 and AtlasFont.glyph_index(288) == 31 and AtlasFont.glyph_index(0) == 31, "Frontend keeps 256 slots and exact fallback admission.")
	var font := AtlasFont.new()
	font.page = ImageTexture.create_from_image(image)
	_check(font.measure(PackedInt32Array([65, 0, 0xd800, 0xdc00])) == 11.0, "Measurement retains every UTF-16 code unit, including NUL.")
	_check(font.measure("") == 0.0, "Empty labels have zero extent.")


func _key(view: OptionsView, action: String) -> Dictionary:
	var result: Dictionary = view.handle_key(action == "up", action == "down", action == "left", action == "right", action == "confirm", action == "back")
	_check(result.ok, "Native input operation succeeds: " + action)
	return result


func _effects(result: Dictionary) -> Array[String]:
	var effects: Array[String] = []
	for effect: Dictionary in result.effects:
		effects.append(effect.kind + (":" + str(effect.cue) if effect.kind == "audio" else ""))
	return effects


func F32(value: float) -> float:
	return PackedFloat32Array([value])[0]


func _stored(value: Variant, visited: Dictionary) -> void:
	if value is Resource:
		if visited.has(value.get_instance_id()):
			return
		visited[value.get_instance_id()] = true
		_check(not value is Image and not value is ImageTexture, "Public scene storage cannot embed private pixels.")
		for property: Dictionary in value.get_property_list():
			if (int(property.usage) & PROPERTY_USAGE_STORAGE) != 0:
				_stored(value.get(property.name), visited)
	elif value is Array:
		for item: Variant in value:
			_stored(item, visited)
	elif value is Dictionary:
		for key: Variant in value:
			_stored(value[key], visited)


func _capture(viewport: SubViewport, filename: String) -> void:
	if _capture_dir.is_empty():
		return
	var destination: String = _capture_dir.path_join(filename)
	if not _check(not FileAccess.file_exists(destination), "Capture refuses overwriting an existing result."):
		return
	await RenderingServer.frame_post_draw
	_check(viewport.get_texture().get_image().save_png(destination) == OK, "Owned Options capture saved.")


func _check(condition: bool, message: String) -> bool:
	_checks += 1
	if not condition:
		_failures.append(message)
		push_error(message)
	return condition


func _done(section: String) -> void:
	_completed.append(section)
	print("OPTIONS_SCENE_SECTION: ", section)
