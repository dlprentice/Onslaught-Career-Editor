# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual production component in standard headless Godot. One argument:
## a fresh owned local-data output directory. No game input or quit operation.
const Page = preload("res://Scenes/Frontend/quit_confirm_presentation.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const REQUIRED: Array[String] = ["authored_scene", "production_assets", "choice_facts", "editing", "frozen_preview", "publication", "ownership"]
const SOURCES: Array[String] = ["res://Scenes/Frontend/QuitConfirm.tscn", "res://Scenes/Frontend/quit_confirm_presentation.gd",
	"res://Scenes/Frontend/quit_confirm_surface.gd", "res://Scenes/Frontend/quit_confirm_label.gd",
	"res://Scenes/Frontend/quit_confirm_highlight.gd", "res://Scenes/Frontend/quit_confirm_row.gd",
	"res://Scenes/Frontend/frontend_atlas_font.gd", "res://Scenes/Frontend/FrontendFont13.tres", "res://Scenes/Frontend/FrontendFont22.tres"]
const INPUTS: Array[String] = ["res://Assets/PauseMenu/blank.texture.aya", "res://Assets/Hud/font-13ps.texture.aya", "res://Assets/Hud/font-22.texture.aya"]
var _checks: int = 0
var _failures: Array[String] = []
var _completed: Array[String] = []
var _source_hashes: Dictionary = {}
var _input_hashes: Dictionary = {}
var _output: String = ""
var _finished: bool = false


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if DisplayServer.get_name() != "headless" or args.size() != 1 or not _owned_directory(args[0]): quit(2); return
	_output = args[0]
	var directory := DirAccess.open(_output)
	if directory == null: quit(2); return
	for name: String in ["report.json", "roundtrip.tscn"]:
		if directory.is_link(name) or FileAccess.file_exists(_output.path_join(name)) or DirAccess.dir_exists_absolute(_output.path_join(name)): quit(2); return
	create_timer(60).timeout.connect(func() -> void:
		if not _finished: _failures.append("Harness timeout before completion."); _finish())
	for path: String in SOURCES: _source_hashes[path] = FileAccess.get_sha256(path)
	for path: String in INPUTS: _input_hashes[path] = FileAccess.get_sha256(path)
	var pointer: int = Input.mouse_mode
	var packed: PackedScene = load("res://Scenes/Frontend/QuitConfirm.tscn")
	var view: Page = packed.instantiate()
	_authored(view)
	_done("authored_scene")
	var viewport := SubViewport.new()
	viewport.size = Vector2i(960, 720)
	viewport.disable_3d = true
	root.add_child(viewport)
	var stage := Node2D.new()
	viewport.add_child(stage)
	stage.add_child(view)
	await process_frame
	await process_frame
	if _check(view.get("_assets_configured") and view.get("_error") == "", "The standalone native page admits its production assets without C#."):
		_assets(view)
		_done("production_assets")
		_facts(view, stage)
		_done("choice_facts")
		await _editing(view)
		_done("editing")
		await _preview(view)
		_done("frozen_preview")
		await _publication(view)
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
	_finish()


func _authored(view: Page) -> void:
	_check(not view.is_node_ready() and not view.is_inside_tree(), "The actual scene exposes authored content before Ready.")
	_check(view.get_rect() == Rect2(0, 0, 640, 480) and view.get_child_count() == 1, "The production page owns its source stage and real dialog.")
	var dialog: Control = view.get_node("Dialog")
	_check(dialog.get_rect() == Rect2(110, 170, 420, 160), "The retained Dialog canvas frame remains authored.")
	var order: Array[String] = ["Panel", "BorderTop", "BorderBottom", "BorderLeft", "BorderRight", "Prompt", "Yes", "No"]
	_check(dialog.get_child_count() == order.size(), "The native tree exposes each panel, edge, prompt and choice.")
	for index: int in range(order.size()): _check(dialog.get_child(index).name == order[index], "Retained draw order: " + order[index])
	_check(view.get_node("Dialog/Panel").rectangle == Rect2(120, 170, 400, 140), "Panel width/center remain pinned; the existing 140px height remains reconstruction.")
	var borders: Dictionary = {"BorderTop": Rect2(120, 170, 400, 2), "BorderBottom": Rect2(120, 308, 400, 2), "BorderLeft": Rect2(120, 170, 2, 140), "BorderRight": Rect2(518, 170, 2, 140)}
	for path: String in borders:
		_check(view.get_node("Dialog/" + path).rectangle == borders[path] and view.get_node("Dialog/" + path).texture == null, "Four real rectangle passes retain the 2px edge law: " + path)
		_check(view.get_node("Dialog/" + path).ink_color == Color(253.0 / 255.0, 253.0 / 255.0, 253.0 / 255.0), "Border retains packed-color MODULATE2X.")
	_check(view.get_node("Dialog/Panel").ink_color == Color(0, 0, 0, 175.0 / 255.0), "Blank panel retains its original alpha.")
	_check(view.get_node("Dialog/Prompt").text == Page.PROMPT and view.get_node("Dialog/Prompt").source_anchor == Vector2(320, 178), "English prompt and source anchor remain explicit; localization is not invented.")
	for pair: Array in [["Yes", 194], ["No", 226]]:
		var row: Control = view.get_node("Dialog/" + pair[0])
		_check(row.get_child_count() == 2 and row.get_child(0).name == "Highlight" and row.get_child(1).name == "Label", "Each selection panel precedes its own text.")
		_check(row.hit_rect == Rect2(120, pair[1], 400, 32), "Choice hit target retains its full half-open width.")
		_check(row.get_node("Label").text == pair[0] and row.get_node("Label").source_anchor == Vector2(320, pair[1]), "Choice remains the existing English label and line pitch.")
		_check(row.get_node("Highlight").highlight_padding == 4.0 and row.get_node("Highlight").row_height == 32.0
			and row.get_node("Highlight").ink_color == Color(127.0 / 255.0, 1, 127.0 / 255.0, 175.0 / 255.0), "Choice retains the 4px pad, 32px row and original highlight tint.")
	for node: Control in view.find_children("*", "Control", true, false):
		_check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE, "Authored control ignores input: " + str(node.name))
		if node != dialog:
			_check(node.anchor_left == 0.0 and node.anchor_top == 0.0 and node.anchor_right == 1.0 and node.anchor_bottom == 1.0, "Full-rect native anchors couple actual child layout to its editable owner.")
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "Every component is inspectable in standard Godot.")


func _assets(view: Page) -> void:
	_check(view.body_font == load("res://Scenes/Frontend/FrontendFont13.tres") and view.choice_font == load("res://Scenes/Frontend/FrontendFont22.tres"), "Standalone preview uses the shared production font recipes.")
	var blank: Texture2D = view.get_node("Dialog/Panel").texture
	_check(blank.source_path == INPUTS[0] and blank.dimensions == Vector2i(16, 16) and blank.compression == 0, "Panel uses the production pause blank, 16x16 DXT1.")
	for font: AtlasFont in [view.body_font, view.choice_font]:
		_check(font.ensure_loaded().ok and font.glyph_widths().size() == 256 and not font.system_font, "Real production atlas supplies its admitted glyph metrics.")
	for texture: Texture2D in [blank, view.body_font.page, view.choice_font.page]:
		_check(texture.ensure_loaded().ok and texture.get_image().get_size() == texture.dimensions, "Actual private image is available through its public recipe.")
	var body: AtlasFont = view.body_font.duplicate(true)
	var choice: AtlasFont = view.choice_font.duplicate(true)
	_check(view.configure_assets({}, body, choice).ok and view.body_font == body and view.choice_font == choice, "Host-supplied font resources are reused by exact identity.")
	_check(view.get_node("Dialog/Prompt").atlas_font == body and view.get_node("Dialog/Yes/Label").atlas_font == choice and view.get_node("Dialog/No/Label").atlas_font == choice, "All labels bind the same admitted resources supplied by the host.")
	_check(view.get_node("Dialog/Yes/Highlight").texture == blank and view.get_node("Dialog/No/Highlight").texture == blank, "Panel and both highlights share one blank page.")
	_check(view.view_snapshot() == {"selected_index": 0} and not view.get("_frame_supplied"), "Opening defaults to the frozen No selection.")
	var before: Dictionary = _visual_state(view)
	var malformed: AtlasFont = AtlasFont.new()
	var wrong_page: AtlasFont = AtlasFont.new()
	wrong_page.page = PlaceholderTexture2D.new()
	for pair: Array in [[malformed, choice], [body, malformed], [Resource.new(), choice], [wrong_page, choice]]:
		var result: Dictionary = view.configure_assets({}, pair[0], pair[1])
		_check(not result.ok and result.error_type == "InvalidDataException" and _visual_state(view) == before, "Missing atlas pages or wrong shared resource types return an atomic refusal.")
	for invalid: Dictionary in [{1: "path"}, {"blank": 1}, {"unowned": "path"}]:
		_check(not view.configure_assets(invalid).ok and _visual_state(view) == before, "Malformed or unowned route fields are refused before binding.")


func _facts(view: Page, stage: Node2D) -> void:
	for selected: int in [1, 0]:
		_check(view.set_frame({"selected_index": selected}).ok, "The host provides only its selected index.")
		_check(view.get_node("Dialog/Yes/Highlight").is_selected() == (selected == 1) and view.get_node("Dialog/No/Highlight").is_selected() == (selected == 0), "Exactly the original No0/Yes1 choice receives its highlight.")
	var incoming: Dictionary = {"selected_index": 1, "unowned": Resource.new()}
	_check(view.set_frame(incoming).ok and view.view_snapshot() == {"selected_index": 1}, "Unknown Resource-valued fields never enter stored facts.")
	incoming.selected_index = 0
	var returned: Dictionary = view.view_snapshot()
	returned.selected_index = 0
	_check(view.view_snapshot() == {"selected_index": 1}, "Incoming and returned snapshots cannot mutate selection.")
	var before: Dictionary = _visual_state(view)
	for invalid: Dictionary in [{}, {"selected_index": -1}, {"selected_index": 2}, {"selected_index": 2147483648}, {"selected_index": true}, {"selected_index": 1.0}, {"selected_index": "1"}, {"selected_index": null}]:
		var result: Dictionary = view.set_frame(invalid)
		_check(not result.ok and result.error_type == "InvalidDataException", "Malformed selection receives an explicit refusal.")
		_check(view.view_snapshot() == {"selected_index": 1} and _visual_state(view) == before, "Refused selection cannot partially change either choice.")
	for pair: Array in [[Vector2(120, 194), 1], [Vector2(519.5, 225.5), 1], [Vector2(120, 226), 0], [Vector2(519.5, 257.5), 0],
		[Vector2(520, 210), -1], [Vector2(119.5, 210), -1], [Vector2(320, 193.5), -1], [Vector2(320, 258), -1]]:
		_check(view.hit_test(pair[0]) == pair[1], "Default choice hit law retains full-width half-open boundaries: " + str(pair[0]))
	var boundary_cases: Array[Array] = []
	for row: Array in [[210.0, 1], [250.0, 0]]:
		for side: Array in [[120.0, [-1, row[1], row[1]]], [520.0, [row[1], -1, -1]]]:
			for neighbor: int in [-1, 0, 1]:
				boundary_cases.append([Vector2(_next_float(side[0], neighbor), row[0]), side[1][neighbor + 1]])
	for edge: Array in [[194.0, [-1, 1, 1]], [226.0, [1, 0, 0]], [258.0, [0, -1, -1]]]:
		for neighbor: int in [-1, 0, 1]:
			boundary_cases.append([Vector2(320, _next_float(edge[0], neighbor)), edge[1][neighbor + 1]])
	boundary_cases.append([Vector2(120, 194), 1])
	boundary_cases.append([Vector2(520, 250), -1])
	for scale_value: Vector2 in [Vector2.ONE, Vector2(1.6, 1.6), Vector2(1.5003125, 1.5003125), Vector2(0.975, 0.975), Vector2(2.13125, 1.333)]:
		stage.scale = scale_value
		stage.position = Vector2(37.25, -19.125)
		for pair: Array in boundary_cases:
			_check(view.hit_test(pair[0]) == pair[1], "External Stage transforms leave the supplied design-space boundary/neighbor unchanged: %s at scale %s." % [pair[0], scale_value])
	stage.scale = Vector2.ONE
	stage.position = Vector2.ZERO
	view.get_node("Dialog/No").position.y = -32
	_check(view.hit_test(Vector2(320, 210)) == 0, "Deliberately overlapping edited targets retain the original No-first hit order.")
	view.get_node("Dialog/No").position.y = 0


func _editing(view: Page) -> void:
	view.position = Vector2(11.5, 7.25)
	view.scale = Vector2(0.9375, 1.0625)
	view.rotation = -0.03125
	var dialog: Control = view.get_node("Dialog")
	dialog.position += Vector2(23.25, -11.5)
	dialog.size = Vector2(504, 200)
	dialog.rotation = 0.125
	await process_frame
	for path: String in ["Panel", "Prompt", "Yes", "No", "Yes/Highlight", "Yes/Label", "No/Highlight", "No/Label"]:
		_check(view.get_node("Dialog/" + path).size == dialog.size, "Dialog Size edits reach real production child draw geometry: " + path)
	var yes: Control = view.get_node("Dialog/Yes")
	var no: Control = view.get_node("Dialog/No")
	var no_geometry: Rect2 = no.get_rect()
	yes.position = Vector2(14.5, 6.25)
	yes.size = Vector2(420, 176)
	yes.rotation = -0.0625
	await process_frame
	var label: Control = yes.get_node("Label")
	var highlight: Control = yes.get_node("Highlight")
	_check(label.size == yes.size and highlight.size == yes.size and no.get_rect() == no_geometry, "One row's edited Size changes its actual label/highlight without replacing its sibling's layout.")
	var source_center := Vector2(320, 210)
	var ratio: Vector2 = yes.size / yes.source_rect.size
	var design_point: Vector2 = view.get_transform() * dialog.get_transform() * yes.get_transform() * ((source_center - yes.source_rect.position) * ratio)
	_check(view.hit_test(design_point) == 1, "Design-space hit testing follows authored page/Dialog/row transforms and the same source scaling as drawing.")
	var actual: Vector2 = label.get_global_transform_with_canvas() * label.source_transform() * label.drawing_origin()
	var expected: Vector2 = yes.get_global_transform_with_canvas() * ((label.drawing_origin() - yes.source_rect.position) * ratio)
	_check(actual.is_equal_approx(expected), "Actual label geometry and the edited hit target share one source-space mapping.")
	var imported: PackedInt32Array = label.displayed_units()
	label.text = "Enhanced Yes"
	_check(label.displayed_units() == imported, "Inspector text alone cannot silently replace the retained English fallback.")
	var draw_count: Array[int] = [0]
	var on_draw: Callable = func() -> void: draw_count[0] += 1
	highlight.draw.connect(on_draw)
	await process_frame
	var before: int = draw_count[0]
	label.override_text = true
	await process_frame
	await process_frame
	_check(label.displayed_units() == Text.units("Enhanced Yes").value and highlight.drawing_rect().size.x == label.font_width() + 8.0, "Explicit enhanced text updates the actual centered label and its highlight width.")
	_check(draw_count[0] > before, "Frozen text edits redraw the highlight through a change signal, without polling.")
	highlight.draw.disconnect(on_draw)
	label.source_anchor += Vector2(3, 2)
	_check(highlight.drawing_rect().position == label.drawing_origin() - Vector2(4, 0), "An edited source anchor also moves the paired highlight.")
	var layout: Dictionary = _visual_state(view)
	view.set_frame({"selected_index": 0})
	view.set_frame({"selected_index": 1})
	_check(_visual_state(view) == layout, "Choice batches preserve every edited transform, source rectangle, label and draw bound.")
	var blank: Texture2D = view.get_node("Dialog/Panel").texture
	var original_route: String = blank.source_path
	_check(view.configure_assets({"blank": ProjectSettings.globalize_path(original_route)}, view.body_font, view.choice_font).ok, "An explicit alternate route reads the same private blank input.")
	_check(blank.source_path == original_route and view.get_node("Dialog/Panel").texture != blank, "An enhanced route gets its own recipe without mutating the faithful shared one.")
	_check(view.get_node("Dialog/Yes/Highlight").texture == view.get_node("Dialog/Panel").texture, "Route override remains shared by the actual production passes.")


func _preview(view: Page) -> void:
	view.editor_selected_index = 0
	_check(view.view_snapshot() == {"selected_index": 1}, "Frozen Inspector selection cannot override an active runtime batch.")
	_check(view.show_editor_preview().ok and view.view_snapshot() == {"selected_index": 0} and not view.get("_frame_supplied"), "Explicit preview displays the authored No selection harmlessly.")
	view.editor_selected_index = 1
	_check(view.view_snapshot() == {"selected_index": 1} and not view.get("_frame_supplied"), "Frozen Inspector selection refreshes the production page.")
	var frozen: Dictionary = _visual_state(view)
	await process_frame
	await process_frame
	_check(_visual_state(view) == frozen, "Frames do not advance any selection, geometry or session time.")


func _publication(view: Page) -> void:
	var packed := PackedScene.new()
	_check(packed.pack(view) == OK, "The actual configured and edited page remains packable.")
	var state: SceneState = packed.get_state()
	var visited: Dictionary = {}
	for node: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(node)):
			_stored(state.get_node_property_value(node, property), visited)
	var path: String = _output.path_join("roundtrip.tscn")
	_check(ResourceSaver.save(packed, path) == OK, "Serialization writes only this fresh owned artifact.")
	var source: String = FileAccess.get_file_as_string(path)
	_check(not source.contains("type=\"Image\"") and not source.contains("type=\"ImageTexture\"") and not source.contains("PackedByteArray("), "Saved scenes contain public recipes and layout, not decoded private pixels.")
	var reopened: PackedScene = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	_check(reopened != null, "The saved production scene can reopen.")
	if reopened == null: return
	var copy: Page = reopened.instantiate()
	_check(copy.get_node("Dialog").get_rect() == view.get_node("Dialog").get_rect()
		and copy.get_node("Dialog").rotation == view.get_node("Dialog").rotation, "Reopening retains the actual edited Dialog transform.")
	for name: String in ["Yes", "No"]:
		var restored: Control = copy.get_node("Dialog/" + name)
		var original: Control = view.get_node("Dialog/" + name)
		_check(restored.offset_left == original.offset_left and restored.offset_top == original.offset_top
			and restored.offset_right == original.offset_right and restored.offset_bottom == original.offset_bottom
			and restored.rotation == original.rotation, "Reopening retains authored row offsets/rotation before native anchor layout runs.")
	_check(copy.get_node("Dialog/Yes/Label").override_text and copy.get_node("Dialog/Yes/Label").text == "Enhanced Yes"
		and copy.get_node("Dialog/Yes/Label").source_anchor == Vector2(323, 196), "The enabled text and source-anchor override remain inspectable before Ready.")
	_check(copy.get_node("Dialog/Panel").texture.source_path == view.get_node("Dialog/Panel").texture.source_path
		and copy.editor_selected_index == 1, "Explicit resource route and authored frozen selection survive reopening.")
	view.get_parent().add_child(copy)
	await process_frame
	await process_frame
	_check(copy.get("_assets_configured") and copy.get("_error") == "" and not copy.get("_frame_supplied"), "Reopened recipes admit into the same harmless frozen production component.")
	_check(_visual_state(copy) == _visual_state(view), "After native anchor layout and asset admission, the reopened page reproduces every edited draw/hit owner and selection.")
	copy.queue_free()
	copy = null
	await process_frame


func _visual_state(view: Page) -> Dictionary:
	var result: Dictionary = {"facts": view.view_snapshot()}
	for node: Control in view.find_children("*", "Control", true, false):
		var state: Dictionary = {"transform": node.get_transform(), "size": node.size, "visible": node.visible}
		if node.has_method("drawing_rect"): state.rectangle = node.drawing_rect()
		if node.has_method("is_selected"): state.selected = node.is_selected()
		if node.has_method("displayed_units"): state.text = node.displayed_units(); state.origin = node.drawing_origin()
		result[str(view.get_path_to(node))] = state
	return result


func _stored(value: Variant, visited: Dictionary) -> void:
	if value is Resource:
		if visited.has(value.get_instance_id()): return
		visited[value.get_instance_id()] = true
		_check(not value is Image and not value is ImageTexture, "Serialized resource graph excludes decoded private images.")
		for property: Dictionary in value.get_property_list():
			if (int(property.usage) & PROPERTY_USAGE_STORAGE) != 0: _stored(value.get(property.name), visited)
	elif value is PackedByteArray:
		_check(false, "Serialized resource graph must not contain private byte buffers.")
	elif value is Array:
		for item: Variant in value: _stored(item, visited)
	elif value is Dictionary:
		for key: Variant in value: _stored(value[key], visited)


func _ownership(view: Page, pointer: int) -> void:
	for node: Node in [view] + view.find_children("*", "", true, false):
		_check(not node.is_processing() and not node.is_physics_processing() and not node.is_processing_input()
			and not node.is_processing_unhandled_input(), "Presentation does not own input or a simulation/frame clock: " + str(node.name))
	for type: String in ["Timer", "AnimationPlayer", "AudioStreamPlayer", "AudioStreamPlayer2D", "AudioStreamPlayer3D", "Camera2D", "Node3D"]:
		_check(view.find_children("*", type, true, false).is_empty(), "Presentation does not create a side-effect owner: " + type)
	_check(Input.mouse_mode == pointer, "Component activity preserves pointer ownership.")
	for path: String in _source_hashes: _check(_source_hashes[path].length() == 64 and FileAccess.get_sha256(path) == _source_hashes[path], "Checked source remains frozen: " + path)
	for path: String in _input_hashes: _check(_input_hashes[path].length() == 64 and FileAccess.get_sha256(path) == _input_hashes[path], "Production input remains read-only: " + path)


func _check(condition: bool, message: String) -> bool:
	_checks += 1
	if not condition:
		_failures.append(message)
		if _failures.size() <= 15: push_error(message)
	return condition


func _done(section: String) -> void:
	_completed.append(section)
	print("QUIT_CONFIRM_SCENE_SECTION: ", section)


func _finish() -> void:
	if _finished: return
	_finished = true
	for section: String in REQUIRED:
		if not _completed.has(section): _failures.append("Incomplete section: " + section)
	var report: Dictionary = {"schema": 1, "checks": _checks, "failure_count": _failures.size(), "failures": _failures,
		"completed": _completed, "editor": Engine.is_editor_hint(), "source_sha256": _source_hashes, "input_sha256": _input_hashes}
	var file := FileAccess.open(_output.path_join("report.json"), FileAccess.WRITE)
	if file == null: quit(2); return
	file.store_string(JSON.stringify(report, "  "))
	file.close()
	print("QUIT_CONFIRM_SCENE_CHECKS: ", JSON.stringify(report))
	quit(0 if _failures.is_empty() else 1)


static func _owned_directory(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or not path.begins_with(owned + "/"): return false
	var directory := DirAccess.open(owned)
	if directory == null: return false
	for part: String in path.trim_prefix(owned + "/").split("/", false):
		if directory.is_link(part) or directory.change_dir(part) != OK: return false
	return true


static func _next_float(value: float, direction: int) -> float:
	# Boundary inputs here are positive finite binary32 values.
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	bytes.encode_u32(0, bytes.decode_u32(0) + direction)
	return bytes.decode_float(0)
