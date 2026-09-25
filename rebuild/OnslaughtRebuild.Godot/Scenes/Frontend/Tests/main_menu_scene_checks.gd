# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Standard Godot, actual production page; one fresh owned output directory.
## These checks prove authored content and frozen editing, not rendered parity.
const MenuPage = preload("res://Scenes/Frontend/main_menu_presentation.gd")
const Laws = preload("res://Client/main_menu_laws.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const REQUIRED: Array[String] = ["authored_scene", "production_assets", "frame_batches", "facts", "editing", "redraw", "preview", "reflection_pose", "publication", "ownership"]
const SECTIONS: Array[String] = ["Background", "VerticalGuide", "HorizontalGuide", "Writing", "Language", "Selector", "NewGame", "ContinueGame", "LoadGame", "Multiplayer", "Goodies", "Options", "Quit", "Decoration", "SelectedIcon", "Version", "TitleLogo", "Reflection"]
const SOURCES: Array[String] = ["res://Scenes/Frontend/MainMenu.tscn", "res://Scenes/Frontend/main_menu_presentation.gd",
	"res://Scenes/Frontend/main_menu_label.gd", "res://Scenes/Frontend/main_menu_rotated_image.gd", "res://Scenes/Frontend/main_menu_selector.gd",
	"res://Scenes/Frontend/main_menu_texture.gd", "res://Scenes/Frontend/main_menu_underlay.gd", "res://Scenes/Frontend/main_menu_preview.gd",
	"res://Scenes/Frontend/main_menu_reflection.gd", "res://Scenes/Frontend/main_menu_reflection.gdshader",
	"res://Scenes/Frontend/loading_strings.gd", "res://Scenes/Frontend/frontend_bitmap_label.gd", "res://Scenes/Frontend/frontend_atlas_font.gd",
	"res://Scenes/Frontend/frontend_underlay.gd", "res://Scenes/Shared/retail_texture_page.gd", "res://Client/main_menu_laws.gd"]
const RECIPES: Array[Dictionary] = [
	{"node": "Writing/Tile0", "name": "forseti-writing-large", "size": Vector2i(128, 512), "compression": 1},
	{"node": "Language/LeftChevron", "name": "fe-arrow", "size": Vector2i(64, 64), "compression": 1},
	{"node": "Selector", "name": "title-text-box", "size": Vector2i(256, 32), "compression": 1},
	{"node": "Decoration/Left/Body", "name": "title-bracket-01", "size": Vector2i(256, 256), "compression": 1},
	{"node": "Decoration/LeftTwin/Body", "name": "title-bracket-02", "size": Vector2i(256, 256), "compression": 1},
	{"node": "Decoration/Right/Body", "name": "symbol-bracket-01", "size": Vector2i(128, 128), "compression": 1},
	{"node": "Decoration/RightTwin/Body", "name": "symbol-bracket-02", "size": Vector2i(128, 128), "compression": 1},
	{"node": "TitleLogo/Body", "name": "title-logo", "size": Vector2i(512, 256), "compression": 1}]
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _source_hashes: Dictionary = {}
var _input_hashes: Dictionary = {}
var _asset_images: Array[Dictionary] = []
var _output: String = ""
var _finished: bool = false


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if DisplayServer.get_name() != "headless" or args.size() != 1 or not _owned_directory(args[0]):
		quit(2); return
	_output = args[0]
	var output_directory := DirAccess.open(_output)
	if output_directory == null: quit(2); return
	for name: String in ["report.json", "roundtrip.tscn"]:
		if output_directory.is_link(name) or FileAccess.file_exists(_output.path_join(name)) or DirAccess.dir_exists_absolute(_output.path_join(name)):
			quit(2); return
	create_timer(80).timeout.connect(func() -> void:
		if not _finished: _failures.append("Harness timeout before completion."); _finish())
	var pointer: int = Input.mouse_mode
	for path: String in SOURCES: _source_hashes[path] = FileAccess.get_sha256(path)
	var packed: PackedScene = load("res://Scenes/Frontend/MainMenu.tscn")
	var view: MenuPage = packed.instantiate()
	_authored(view)
	_done("authored_scene")
	for recipe: Resource in _recipes(view):
		var path: String = recipe.source_path
		_input_hashes[path] = FileAccess.get_sha256(path)
	_input_hashes[view.strings.source_path] = FileAccess.get_sha256(view.strings.source_path)
	var underlay_path: String = view.get_node("Background").recipe.source_path
	_input_hashes[underlay_path] = FileAccess.get_sha256(underlay_path)
	var viewport := SubViewport.new()
	viewport.size = Vector2i(640, 480)
	viewport.disable_3d = true
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var stage := Node2D.new()
	viewport.add_child(stage)
	stage.add_child(view)
	await process_frame
	await process_frame
	if _check(view.get("_assets_configured") and view.get("_error") == "", "Actual production resources admit without a host or C# session."):
		_assets(view)
		_done("production_assets")
		_batches(view)
		_done("frame_batches")
		_facts(view)
		_done("facts")
		_editing(view)
		_done("editing")
		await _redraw(view)
		_done("redraw")
		_preview(view)
		_done("preview")
		await _reflection_pose(view, stage)
		_done("reflection_pose")
		var frozen: Dictionary = view.view_snapshot()
		await process_frame
		await process_frame
		_check(view.view_snapshot() == frozen, "Frames never advance frozen display facts.")
		_publication(view)
		_done("publication")
		_ownership(view, pointer)
		_done("ownership")
	viewport.queue_free()
	view = null
	stage = null
	viewport = null
	packed = null
	await process_frame
	await process_frame
	if Engine.is_editor_hint():
		while EditorInterface.get_resource_filesystem().is_scanning(): await process_frame
		await create_timer(0.25).timeout
	_finish()


func _authored(view: MenuPage) -> void:
	_check(not view.is_inside_tree() and not view.is_node_ready(), "Meaningful content exists before entering the tree or Ready.")
	_check(view.get_child_count() == SECTIONS.size() and view.get_rect() == Rect2(0, 0, 640, 480), "The source 640x480 stage contains every authored production section.")
	for index: int in range(SECTIONS.size()):
		_check(view.get_child(index).name == SECTIONS[index], "Authored submit order: " + SECTIONS[index])
	for index: int in range(7):
		var row: Control = view.get_node(Laws.ROW_NAMES[index])
		_check(row.get_rect() == Rect2(99, 294 + index * 20, 240, 20) and row.source_rect == row.get_rect(), "A real editable row retains the separate half-open hit rectangle: " + row.name)
		_check(row.source_anchor == Vector2(219, 296 + index * 20) and row.atlas_font == view.font and not row.override_text and not row.text.is_empty(), "Each row exposes its faithful source anchor, atlas and explicit enhanced-text switch.")
	for group: String in ["Left", "LeftTwin", "Right", "RightTwin"]:
		var owner: Control = view.get_node("Decoration/" + group)
		_check(owner.get_child_count() == 2 and owner.get_child(0).name == "Shadow" and owner.get_child(1).name == "Body", "Decoration shadow and body are real separately inspectable passes: " + group)
		for image: Control in owner.get_children():
			_check(image.position == Vector2.ZERO and image.size == Vector2(440, 210) and image.source_rect == Rect2(120, 240, 440, 210), "Decoration pass shares the authored source frame before Ready: " + group + "/" + image.name)
	for recipe: Dictionary in RECIPES:
		_check_recipe(view.get_node(recipe.node).texture, "res://Assets/Frontend/" + recipe.name + ".texture.aya", recipe.size, recipe.compression)
	_check_recipe(view.get_node("Reflection").reflection, "res://Assets/Frontend/reflection-map.texture.aya", Vector2i(512, 128), 0)
	var flags: Array[String] = ["uk", "fr", "gr", "it", "sp"]
	var icons: Array[String] = ["new-game", "continue-game", "load-game", "multiplayer", "goodies", "options", "quit"]
	_check(view.language_flags.size() == 5 and view.menu_icons.size() == 7, "Every language and selected-row image recipe is authored.")
	for index: int in range(5): _check_recipe(view.language_flags[index], "res://Assets/Frontend/Flags/flag-" + flags[index] + ".texture.aya", Vector2i(128, 128), 0)
	for index: int in range(7): _check_recipe(view.menu_icons[index], "res://Assets/Frontend/Icons/" + icons[index] + ".texture.aya", Vector2i(128, 128), 1)
	for node: Node in [view] + view.find_children("*", "", true, false):
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "Standard Godot can inspect every authored node: " + str(node.name))
		if node is Control: _check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE, "Presentation controls leave input with the host.")


func _check_recipe(recipe: Texture2D, path: String, dimensions: Vector2i, compression: int) -> void:
	_check(recipe != null and recipe.get_script().resource_path == "res://Scenes/Shared/retail_texture_page.gd", "A native resource recipe exists before Ready: " + path)
	_check(recipe.source_path == path and recipe.dimensions == dimensions and recipe.compression == compression, "Production asset identity is authored: " + path)


func _recipes(view: MenuPage) -> Array[Resource]:
	var recipes: Array[Resource] = [view.font.page, view.get_node("Reflection").reflection]
	for recipe: Dictionary in RECIPES: recipes.append(view.get_node(recipe.node).texture)
	for recipe: Texture2D in view.language_flags + view.menu_icons: recipes.append(recipe)
	return recipes


func _assets(view: MenuPage) -> void:
	_check(view.font == load("res://Scenes/Frontend/FrontendFont13.tres") and not view.font.system_font and view.font.glyph_widths().size() == 256, "Main Menu shares the production Font13 atlas and metrics.")
	_check(view.get_node("Background").recipe == load("res://Scenes/Frontend/FrontendUnderlay.tres"), "The real underlay recipe is shared with other frontend pages.")
	var title: Texture2D = load("res://Scenes/Frontend/ClickTitle.tres")
	_check(view.get_node("TitleLogo/Body").texture == title and view.get_node("TitleLogo/ShadowMotion/Shadow").texture == title and view.get_node("Reflection").texture == title, "Click, title shadow/body and reflection share the exact production title page.")
	for index: int in range(3): _check(view.get_node("Writing/Tile%d" % index).texture == view.get_node("Writing/Tile0").texture, "Writing passes share one admitted page.")
	_check(view.get_node("Language/LeftChevron").texture == view.get_node("Language/RightChevron").texture, "Chevron passes share one admitted page.")
	for group: String in ["Left", "LeftTwin", "Right", "RightTwin"]:
		_check(view.get_node("Decoration/" + group + "/Shadow").texture == view.get_node("Decoration/" + group + "/Body").texture, "Decoration passes share one admitted page.")
	for recipe: Resource in _recipes(view):
		_check(recipe.ensure_loaded().ok, "Production recipe admits: " + recipe.source_path)
		var image: Image = recipe.get_image()
		_check(image.get_size() == recipe.dimensions and not image.is_empty(), "The actual full-size production image is available: " + recipe.source_path)
		_asset_images.append({"source": recipe.source_path, "width": image.get_width(), "height": image.get_height(), "format": image.get_format(), "bytes": image.get_data().size()})
	_check(not view.get("_frame_supplied") and view.view_snapshot().selected_index == 0 and view.view_snapshot().transition == 1.0, "Opening displays frozen authored facts without starting a session.")


func _batches(view: MenuPage) -> void:
	var facts: Dictionary = view.view_snapshot()
	for index: int in range(7):
		facts.selected_index = index
		facts.language = index - 1
		facts.transition = 0.875 if index % 2 == 0 else 1.0
		facts.animation_seconds = float(index) * 0.25
		facts.background_seconds = float(index) / 30.0
		facts.reflection_visible = index != 6
		_check(view.set_frame(facts).ok, "One coarse batch supplies display facts for every selection.")
		_check(view.get_node("Language/Flag").texture == view.language_flags[clampi(facts.language, 0, 4)], "Language recipe selection retains its clamp.")
		_check(view.get_node("SelectedIcon/Body").texture == view.menu_icons[index] and view.get_node("SelectedIcon/ShadowMotion/Shadow").texture == view.menu_icons[index], "Both icon passes use the selected production recipe.")
		_check(view.get_node("Selector").drawing_rect() == Laws.selector_rect(index, view.font.measure(facts.rows[index].text)), "Selector consumes imported text metrics in source order.")
		_check(view.get_node("Reflection").visible == facts.reflection_visible, "The host alone supplies reflection visibility, including Quit backdrop suppression.")
		var row: Control = view.get_node(Laws.ROW_NAMES[index])
		_check(row.displayed_units() == facts.rows[index].text, "The displayed label binds admitted raw UTF-16 units.")
		_check(view.hit_test(row.get_global_transform_with_canvas() * Vector2.ZERO) == index, "Authored row left/top boundary is included.")
		_check(view.hit_test(row.get_global_transform_with_canvas() * Vector2(row.size.x, 1)) == -1, "Authored row right boundary is excluded.")


func _facts(view: MenuPage) -> void:
	var facts: Dictionary = view.view_snapshot()
	facts.rows[0].text = PackedInt32Array([0, 65, 0xd800, 0xdc00, 0xffff])
	facts.unowned_resource = Resource.new()
	_check(view.set_frame(facts).ok, "A valid batch admits raw UTF-16 while ignoring unknown host fields.")
	var expected: Dictionary = view.view_snapshot()
	_check(expected.size() == 7 and not expected.has("unowned_resource"), "Only admitted display fields enter snapshots; arbitrary Resource identities do not escape.")
	facts.rows[0].text[0] = 99
	facts.rows[0].available = not facts.rows[0].available
	var returned: Dictionary = view.view_snapshot()
	returned.rows[0].text[1] = 99
	returned.rows[1].available = not returned.rows[1].available
	_check(view.view_snapshot() == expected, "Inputs and returned nested row snapshots are detached.")
	var visual: Dictionary = _visual_state(view)
	var invalid: Array[Dictionary] = [{}]
	for pair: Array in [["transition", 1], ["animation_seconds", "1"], ["background_seconds", null], ["selected_index", -1], ["selected_index", 7], ["language", true], ["reflection_visible", 1], ["rows", []]]:
		var candidate: Dictionary = expected.duplicate(true)
		candidate[pair[0]] = pair[1]
		invalid.append(candidate)
	for pair: Array in [["text", null], ["text", PackedInt32Array([-1])], ["available", 1]]:
		var candidate: Dictionary = expected.duplicate(true)
		candidate.rows[6][pair[0]] = pair[1]
		invalid.append(candidate)
	for candidate: Dictionary in invalid:
		var result: Dictionary = view.set_frame(candidate)
		_check(not result.ok and result.error_type == "InvalidDataException", "Malformed facts fail before a partial display update.")
		_check(view.view_snapshot() == expected and _visual_state(view) == visual, "Refusal retains both detached facts and the actual display.")
	for paths: Dictionary in [{1: "path"}, {"Frontend/title-logo": 1}]:
		_check(not view.configure_assets(paths).ok and view.view_snapshot() == expected, "Malformed route carriers are refused before mutation.")
	_check(view.show_editor_preview().ok, "Raw-unit probe returns to the harmless authored preview.")


func _editing(view: MenuPage) -> void:
	var row: Control = view.get_node("Quit")
	row.position = Vector2(450, 100)
	row.size = Vector2(120, 30)
	row.rotation = 0.125
	row.scale = Vector2(1.25, 0.75)
	row.source_anchor += Vector2(3, 4)
	row.text = "Enhanced quit"
	var imported: PackedInt32Array = row.displayed_units()
	_check(not row.override_text and imported != Text.units(row.text).value, "Editing text alone cannot replace the imported faithful label.")
	row.override_text = true
	_check(row.displayed_units() == Text.units(row.text).value, "Explicit enhanced text is visible on the production row.")
	var geometry: Transform2D = row.get_transform()
	var facts: Dictionary = view.view_snapshot()
	facts.selected_index = 6
	facts.transition = 1.0
	view.set_frame(facts)
	_check(row.get_transform() == geometry and row.position == Vector2(450, 100) and row.size == Vector2(120, 30) and row.source_anchor == Vector2(222, 420), "Runtime display facts retain actual edited geometry and source anchor.")
	_check(view.hit_test(row.get_global_transform_with_canvas() * Vector2(60, 15)) == 6, "Hit testing follows the edited production control's full transform.")
	_check(view.get_node("Selector").drawing_rect() == Laws.selector_rect(6, view.font.measure(imported)), "Enhanced text does not silently replace the imported selector-width law.")
	var image: Control = view.get_node("Decoration/Left/Body")
	var before: Transform2D = image.drawing_transform()
	image.source_anchor += Vector2(11, 7)
	_check(image.drawing_transform().origin == before.origin + Vector2(11, 7), "Frozen anchor edits immediately change production draw geometry without another host batch.")
	var sibling: Control = view.get_node("Decoration/Left/Shadow")
	var sibling_geometry: Rect2 = sibling.get_rect()
	var sibling_source: Rect2 = sibling.source_rect
	var source_frame: Rect2 = image.source_rect
	var corners: Array[Vector2] = [image.drawing_rect().position, image.drawing_rect().end]
	var original_points: Array[Vector2] = []
	for corner: Vector2 in corners: original_points.append(image.get_transform() * image.drawing_transform() * corner)
	image.position = Vector2(7.25, -11.5)
	for index: int in range(corners.size()):
		_check((image.get_transform() * image.drawing_transform() * corners[index]).is_equal_approx(original_points[index] + image.position), "Editing one pass's Position moves its actual draw corner without a frame refresh.")
	image.size = Vector2(550, 157.5)
	for index: int in range(corners.size()):
		var expected: Vector2 = image.position + original_points[index] * Vector2(1.25, 0.75)
		_check((image.get_transform() * image.drawing_transform() * corners[index]).is_equal_approx(expected), "Editing one pass's Size rescales actual draw geometry inside its unchanged source frame.")
	for transition: float in [0.125, 0.55, 1.0]:
		facts.transition = transition
		_check(view.set_frame(facts).ok and image.position == Vector2(7.25, -11.5) and image.size == Vector2(550, 157.5) and image.source_rect == source_frame, "Display batches preserve deliberate per-pass Position/Size while retaining faithful source geometry.")
		_check(sibling.get_rect() == sibling_geometry and sibling.source_rect == sibling_source, "Editing one decoration pass never changes its sibling's authored geometry.")
	for index: int in range(corners.size()):
		_check((image.get_transform() * image.drawing_transform() * corners[index]).is_equal_approx(image.position + original_points[index] * Vector2(1.25, 0.75)), "Returning to the same display facts retains the edited pass's actual draw corners.")
	var recipe: Texture2D = image.texture.duplicate(true)
	recipe.source_path = ProjectSettings.globalize_path(recipe.source_path)
	_check(recipe.ensure_loaded().ok, "A deliberate recipe override can read the same admitted private input through its absolute route.")
	image.texture = recipe
	_check(image.texture != view.get_node("Decoration/Left/Shadow").texture and image.texture.source_path.is_absolute_path(), "Enhanced recipe edits remain separate from the shared faithful recipe.")


func _redraw(view: MenuPage) -> void:
	var image: Control = view.get_node("Decoration/Left/Body")
	var selector: Control = view.get_node("Selector")
	var underlay: Control = view.get_node("Background")
	await _redraw_on_edit(image, func() -> void: image.source_anchor += Vector2(1, 2), "Rotated source anchor")
	await _redraw_on_edit(image, func() -> void: image.source_rect.position += Vector2(2, 3), "Rotated source rectangle")
	await _redraw_on_edit(image, func() -> void: image.source_size += Vector2(8, 4), "Rotated source dimensions")
	await _redraw_on_edit(image, func() -> void: image.ink_color = Color(0.5, 0.75, 1, 0.5), "Rotated ink")
	await _redraw_on_edit(selector, func() -> void: selector.source_rect.position += Vector2(3, 2), "Selector source rectangle")
	await _redraw_on_edit(selector, func() -> void: selector.ink_color = Color(0.25, 0.5, 0.75, 0.5), "Selector ink")
	await _redraw_on_edit(underlay, func() -> void: underlay.source_rect.position += Vector2(1, 2), "Underlay source rectangle")
	for control: Control in [image, selector]:
		var old: Texture2D = control.texture
		var replacement: Texture2D = old.duplicate(true)
		await _redraw_on_edit(control, func() -> void: control.texture = replacement, "Custom image recipe replacement")
		_check(not old.changed.is_connected(control.queue_redraw) and replacement.changed.is_connected(control.queue_redraw), "Replacing a custom image recipe transfers its redraw subscription.")
		await _redraw_on_edit(control, func() -> void: replacement.emit_changed(), "Custom image recipe change")


func _redraw_on_edit(control: Control, edit: Callable, message: String) -> void:
	var count: Array[int] = [0]
	var on_draw: Callable = func() -> void: count[0] += 1
	control.draw.connect(on_draw)
	await process_frame
	await process_frame
	var before: int = count[0]
	edit.call()
	await process_frame
	await process_frame
	_check(count[0] > before, message + " queues a real draw while the scene clock is inactive.")
	control.draw.disconnect(on_draw)


func _preview(view: MenuPage) -> void:
	var incoming: Dictionary = view.view_snapshot()
	view.editor_preview = view.editor_preview.duplicate(true)
	view.editor_preview.selected_index = 4
	view.editor_preview.animation_seconds = 2.5
	_check(view.view_snapshot().selected_index == (4 if Engine.is_editor_hint() else incoming.selected_index), "Inspector preview changes respect an active runtime host batch.")
	_check(view.show_editor_preview().ok and not view.get("_frame_supplied"), "Explicit frozen preview releases host facts without starting gameplay.")
	view.editor_preview.selected_index = 5
	view.editor_preview.reflection_visible = false
	_check(view.view_snapshot().selected_index == 5 and not view.get_node("Reflection").visible, "Frozen resource changes refresh the actual production page.")
	var previous: Resource = view.editor_preview
	view.editor_preview = previous.duplicate(true)
	var expected: Dictionary = view.view_snapshot()
	previous.selected_index = 1
	_check(view.view_snapshot() == expected, "Replacing the preview disconnects the previous resource.")


func _reflection_pose(view: MenuPage, stage: Node2D) -> void:
	view.editor_preview.reflection_visible = true
	_check(view.show_editor_preview().ok, "Reflection pose checks use authored frozen facts.")
	var frozen: Dictionary = view.view_snapshot()
	var sheen: Node2D = view.get_node("Reflection")
	var wrapper: Control = view.get_node("TitleLogo")
	var title: Control = view.get_node("TitleLogo/Body")
	var scroll: float = sheen.view_snapshot().scroll
	_check(sheen.top_level and not sheen.z_as_relative, "Reflection retains the canvas-root submission path.")
	var edits: Array[Callable] = [
		func() -> void: stage.position = Vector2(23.5, -12.25),
		func() -> void: stage.scale = Vector2(0.9771, 1.0187),
		func() -> void: wrapper.position = Vector2(13.25, -7.5),
		func() -> void: wrapper.scale = Vector2(0.9375, 1.0625),
		func() -> void: wrapper.rotation = 0.17,
		func() -> void: title.position += Vector2(17.25, 9.75),
		func() -> void: title.size += Vector2(48.5, 23.25),
		func() -> void: title.rotation = -0.125]
	for index: int in range(edits.size()):
		edits[index].call()
		await process_frame
		await process_frame
		var actual_first: Vector2 = sheen.get_global_transform() * Vector2(64, 2)
		var actual_last: Vector2 = sheen.get_global_transform() * Vector2(576, 258)
		var expected_first: Vector2 = title.get_global_transform() * Vector2.ZERO
		var expected_last: Vector2 = title.get_global_transform() * title.size
		_check(actual_first.is_equal_approx(expected_first) and actual_last.is_equal_approx(expected_last), "Frozen ancestor/title edit %d moves both reflection bounds with the actual title." % index)
		_check(view.view_snapshot() == frozen and not view.get("_frame_supplied") and sheen.view_snapshot().scroll == scroll, "Transform notifications refresh the reflection without another host batch or elapsed clock.")
	view.hide()
	await process_frame
	_check(not sheen.is_visible_in_tree(), "A top-level reflection follows hidden page ancestry.")
	view.show()
	await process_frame
	_check(sheen.is_visible_in_tree(), "Showing the page restores its admitted reflection.")
	view.editor_preview.reflection_visible = false
	await process_frame
	view.hide()
	view.show()
	await process_frame
	_check(not sheen.visible and not sheen.is_visible_in_tree(), "Page visibility never overrides the source reflection suppression used by Quit.")
	view.editor_preview.reflection_visible = true
	await process_frame
	stage.z_index = 96
	view.z_index = 4
	var cursor := Node2D.new()
	cursor.z_as_relative = false
	cursor.z_index = 102
	stage.get_parent().add_child(cursor)
	var before_batch: Dictionary = view.view_snapshot()
	_check(view.set_frame(before_batch).ok and view.view_snapshot() == before_batch, "Z-layer refresh reuses the same display facts without advancing time.")
	_check(sheen.z_index == 100 and not sheen.z_as_relative and sheen.z_index < cursor.z_index, "Effective ancestor Z100 remains below the host cursor at Z102.")
	cursor.queue_free()
	for property: Dictionary in sheen.get_property_list():
		if property.name in ["position", "rotation", "scale", "skew", "z_index"]:
			_check((int(property.usage) & PROPERTY_USAGE_STORAGE) == 0, "Derived reflection pose/layer is not a new authored baseline: " + property.name)


func _publication(view: MenuPage) -> void:
	var packed := PackedScene.new()
	_check(packed.pack(view) == OK, "The actual configured and edited production page packs.")
	var state: SceneState = packed.get_state()
	var visited: Dictionary = {}
	for index: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(index)):
			_stored(state.get_node_property_value(index, property), visited)
			if str(state.get_node_path(index)) == "Reflection":
				_check(str(state.get_node_property_name(index, property)) not in ["position", "rotation", "scale", "skew", "z_index"], "Packed reflection excludes transient pose/layer properties.")
	var path: String = _output.path_join("roundtrip.tscn")
	_check(ResourceSaver.save(packed, path) == OK, "Serialization uses only a fresh owned test artifact.")
	var source: String = FileAccess.get_file_as_string(path)
	_check(not source.contains("type=\"Image\"") and not source.contains("type=\"ImageTexture\"") and not source.contains("PackedByteArray("), "Public scene serialization contains recipes and layout, never private pixels.")
	var loaded: PackedScene = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	_check(loaded != null, "The saved production scene reopens.")
	if loaded == null: return
	var copy: MenuPage = loaded.instantiate()
	_check(not copy.is_node_ready() and copy.get_child_count() == SECTIONS.size(), "Reopened content remains inspectable before Ready.")
	for node: Control in view.find_children("*", "Control", true, false):
		var restored: Control = copy.get_node(view.get_path_to(node))
		_check(restored.get_rect() == node.get_rect() and restored.rotation == node.rotation and restored.scale == node.scale, "Edited production geometry survives reopening: " + str(view.get_path_to(node)))
	for pair: Array in [["Quit", "text"], ["Quit", "override_text"], ["Quit", "source_anchor"], ["Decoration/Left/Body", "source_anchor"],
		["Decoration/Left/Body", "source_rect"], ["Decoration/Left/Body", "source_size"], ["Decoration/Left/Body", "ink_color"],
		["Selector", "source_rect"], ["Selector", "ink_color"], ["Background", "source_rect"]]:
		_check(copy.get_node(pair[0]).get(pair[1]) == view.get_node(pair[0]).get(pair[1]), "Actual exported edit survives: " + pair[0] + "/" + pair[1])
	_check(copy.get_node("Quit").displayed_units() == Text.units("Enhanced quit").value, "The enhanced label is inspectable immediately after reopening.")
	_check(copy.get_node("Decoration/Left/Body").texture.source_path == view.get_node("Decoration/Left/Body").texture.source_path, "The explicit recipe route edit survives reopening.")
	_check(copy.get_node("Decoration/Left/Body").position == Vector2(7.25, -11.5) and copy.get_node("Decoration/Left/Body").size == Vector2(550, 157.5)
		and copy.get_node("Decoration/Left/Shadow").get_rect() == Rect2(0, 0, 440, 210), "Reopened decoration retains edited per-pass Position/Size and the sibling's untouched authored frame.")
	_check(copy.editor_preview.snapshot() == view.editor_preview.snapshot(), "The authored frozen preview resource survives reopening.")
	var restored_sheen: Node2D = copy.get_node("Reflection")
	_check(restored_sheen.transform == Transform2D.IDENTITY and restored_sheen.z_index == 0
		and restored_sheen.top_level and not restored_sheen.z_as_relative, "Reopening restores authored submission mode with no serialized derived pose or effective Z.")
	copy.free()


func _stored(value: Variant, visited: Dictionary) -> void:
	if value is Resource:
		if visited.has(value.get_instance_id()): return
		visited[value.get_instance_id()] = true
		_check(not value is Image and not value is ImageTexture, "Serialized resource graph excludes private decoded images.")
		for property: Dictionary in value.get_property_list():
			if (int(property.usage) & PROPERTY_USAGE_STORAGE) != 0: _stored(value.get(property.name), visited)
	elif value is PackedByteArray:
		_check(false, "Serialized resource graph must not contain private byte buffers.")
	elif value is Array:
		for item: Variant in value: _stored(item, visited)
	elif value is Dictionary:
		for key: Variant in value: _stored(value[key], visited)


func _ownership(view: MenuPage, pointer: int) -> void:
	for node: Node in [view] + view.find_children("*", "", true, false):
		_check(not node.is_processing() and not node.is_physics_processing() and not node.is_processing_input()
			and not node.is_processing_unhandled_input(), "No presentation node owns input, simulation or a frame clock: " + str(node.name))
	for type: String in ["Timer", "AnimationPlayer", "AudioStreamPlayer", "AudioStreamPlayer2D", "AudioStreamPlayer3D", "Node3D", "Camera2D"]:
		_check(view.find_children("*", type, true, false).is_empty(), "No gameplay or side-effect owner: " + type)
	_check(Input.mouse_mode == pointer, "Scene and editor activity preserve pointer ownership.")
	for path: String in _input_hashes: _check(FileAccess.get_sha256(path) == _input_hashes[path], "Production input remains read-only: " + path)
	for path: String in _source_hashes: _check(FileAccess.get_sha256(path) == _source_hashes[path], "Checked production code remains frozen for this receipt: " + path)


func _visual_state(view: MenuPage) -> Dictionary:
	var result: Dictionary = {}
	for node: CanvasItem in view.find_children("*", "CanvasItem", true, false):
		var facts: Dictionary = {"transform": node.get_transform(), "visible": node.visible, "modulate": node.modulate, "self_modulate": node.self_modulate}
		if node.has_method("drawing_rect"): facts.drawing_rect = node.drawing_rect()
		if node.has_method("drawing_transform"): facts.drawing_transform = node.drawing_transform()
		if node.has_method("displayed_units"): facts.text = node.displayed_units()
		if node.has_method("view_snapshot"): facts.snapshot = node.view_snapshot()
		result[str(view.get_path_to(node))] = facts
	return result


func _check(condition: bool, message: String) -> bool:
	_checks += 1
	if not condition:
		_failures.append(message)
		if _failures.size() <= 15: push_error(message)
	return condition


func _done(section: String) -> void:
	_completed.append(section)
	print("MAIN_MENU_SCENE_SECTION: ", section)


func _finish() -> void:
	if _finished: return
	_finished = true
	for section: String in REQUIRED:
		if not _completed.has(section): _failures.append("Incomplete section: " + section)
	var report: Dictionary = {"schema": 1, "checks": _checks, "failure_count": _failures.size(), "failures": _failures,
		"completed": _completed, "editor": Engine.is_editor_hint(), "source_sha256": _source_hashes, "input_sha256": _input_hashes, "asset_images": _asset_images}
	var file := FileAccess.open(_output.path_join("report.json"), FileAccess.WRITE)
	if file == null: quit(2); return
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("MAIN_MENU_SCENE_CHECKS: ", JSON.stringify(report))
	quit(0 if _failures.is_empty() else 1)


static func _owned_directory(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or not path.begins_with(owned + "/"): return false
	var directory := DirAccess.open(owned)
	if directory == null: return false
	for part: String in path.trim_prefix(owned + "/").split("/", false):
		if directory.is_link(part) or directory.change_dir(part) != OK: return false
	return true
