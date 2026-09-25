# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Standard-Godot checks of the actual production scene. One argument: a
## fresh owned local-data directory. No device input or gameplay is started.
const Page = preload("res://Scenes/Frontend/configuration_presentation.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const REQUIRED: Array[String] = ["authored_scene", "production_assets", "display_facts", "navigation", "editing", "frozen_preview", "publication", "ownership"]
const SOURCES: Array[String] = ["res://Scenes/Frontend/SelectConfiguration.tscn", "res://Scenes/Frontend/configuration_presentation.gd",
	"res://Scenes/Frontend/configuration_rock.gd", "res://Scenes/Frontend/configuration_ring.gd",
	"res://Scenes/Frontend/ConfigurationRock.tres", "res://Scenes/Frontend/ConfigurationRing.tres",
	"res://Scenes/Frontend/career_name_label.gd", "res://Scenes/Frontend/career_name_arrow.gd",
	"res://Scenes/Frontend/career_name_target.gd", "res://Scenes/Frontend/quit_confirm_surface.gd",
	"res://Scenes/Frontend/frontend_atlas_font.gd", "res://Scenes/Frontend/FrontendFont13.tres", "res://Scenes/Frontend/FrontendFont22.tres"]
const INPUTS: Array[String] = ["res://Assets/Frontend/Backgrounds/rock.texture.aya", "res://Assets/Frontend/level-bracket-02.texture.aya",
	"res://Assets/Frontend/fe-arrow.texture.aya", "res://Assets/Hud/font-13ps.texture.aya", "res://Assets/Hud/font-22.texture.aya"]
const SECTIONS: Dictionary = {"Background": Rect2(0, 0, 640, 480), "Header": Rect2(191, 65, 394, 32),
	"Unit": Rect2(260.5, 99.5, 320, 32), "Walker": Rect2(280, 210, 305, 48), "Jet": Rect2(280, 274, 305, 48), "Navigation": Rect2(9, 438, 623, 36)}
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
	create_timer(70).timeout.connect(func() -> void:
		if not _finished: _failures.append("Harness timeout before completion."); _finish())
	for path: String in SOURCES: _source_hashes[path] = FileAccess.get_sha256(path)
	for path: String in INPUTS: _input_hashes[path] = FileAccess.get_sha256(path)
	var pointer: int = Input.mouse_mode
	var packed: PackedScene = load("res://Scenes/Frontend/SelectConfiguration.tscn")
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
	if _check(view.get("_assets_configured") and view.get("_error") == "", "Standalone Configuration admits the same production recipes without C#."):
		_assets(view)
		_done("production_assets")
		_facts(view)
		_done("display_facts")
		_navigation(view, stage)
		_done("navigation")
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
	_check(not view.is_node_ready() and not view.is_inside_tree(), "The actual production scene exposes its UI before Ready.")
	_check(view.get_rect() == Rect2(0, 0, 640, 480) and view.get_child_count() == 6, "The page has six real authored source sections.")
	var index: int = 0
	for section: String in SECTIONS:
		var control: Control = view.get_node(section)
		_check(control.get_rect() == SECTIONS[section] and view.get_child(index) == control, "Original section layout and draw order: " + section)
		index += 1
		for child: Control in control.get_children():
			_check(child.source_rect == SECTIONS[section] and child.anchor_right == 1.0 and child.anchor_bottom == 1.0,
				"Each draw pass preserves the section source matrix and editable native anchors: " + section + "/" + str(child.name))
	_check(view.get_node("Background").get_child(0).name == "Rock" and view.get_node("Background").get_child(1).name == "Ring", "Rock precedes the measured annulus, with no video/underlay owner.")
	_check(view.get_node("Background/Rock").source_anchor == Vector2(-70, -80) and view.get_node("Background/Rock").texture_scale == Vector2(1.25, 1.25), "Rock keeps the measured origin and scale.")
	_check(view.get_node("Background/Rock").ink_color == Color(179.0 / 255.0, 179.0 / 255.0, 243.0 / 255.0), "Rock keeps packed0xff5a5a7a through original MODULATE2X.")
	_check(view.get_node("Background/Ring").source_anchor == Vector2(267, 221) and view.get_node("Background/Ring").source_size == Vector2(990, 990), "Ring keeps the measured center and dimensions.")
	_check(view.get_node("Background/Ring").ink_color == Color(1.257, 0.960, 0.777, 1) and view.get_node("Background/Ring").ink_color.r > 1.0,
		"The measured ring red gain above1 remains unclamped.")
	_check(view.get_node("Header/Panel").rectangle == Rect2(191, 69, 394, 21) and view.get_node("Header/Panel").ink_color == Color(0, 0, 0, 0.5),
		"Textured stage uses the original black half-alpha header overlay.")
	_check(view.get_node("Header/Title").text == Page.TITLE and view.get_node("Header/Title").centered
		and view.get_node("Header/Title").source_anchor == Vector2(390, 65), "The real Font22 header retains its centered source origin.")
	_check(view.get_node("Unit/Name").source_anchor == Vector2(260.5, 99.5) and not view.get_node("Unit/Name").centered, "Unit title preserves its left-aligned fractional source position.")
	for section: String in ["Walker", "Jet"]:
		for row: int in range(3):
			var child: Control = view.get_node(section).get_child(row)
			_check(child.name == ["Title", "Primary", "Secondary"][row]
				and child.source_anchor == Vector2(280, (210 if section == "Walker" else 274) + row * 16), "Mode title and weapon rows retain pitch16 and draw order.")
			_check(child.glyph_scale == Vector2.ONE and not child.name_glyphs and child.shadow,
				"Configuration text uses ordinary production atlas mapping and per-glyph shadow/body ordering.")
		_check(view.get_node(section + "/Title").ink_color == Color(247.0 / 255.0, 215.0 / 255.0, 61.0 / 255.0), "Mode title keeps packed0xff7c6c1f amber.")
	_check(view.get_node("Navigation/Back").rectangle == Rect2(9, 438, -28, 36)
		and view.get_node("Navigation/Forward").rectangle == Rect2(604, 437, 28, 36), "The two signed arrow rectangles retain their distinct original origins.")
	for node: Control in view.find_children("*", "Control", true, false):
		_check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE, "Authored control ignores input: " + str(node.name))
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "Scene content is inspectable with standard Godot.")


func _assets(view: Page) -> void:
	_check(view.body_font == load("res://Scenes/Frontend/FrontendFont13.tres") and view.title_font == load("res://Scenes/Frontend/FrontendFont22.tres"), "Standalone view uses the shared production Font13/Font22 recipes.")
	var rock: Texture2D = view.get_node("Background/Rock").texture
	var ring: Texture2D = view.get_node("Background/Ring").texture
	var arrow: Texture2D = view.get_node("Navigation/Forward").texture
	for item: Array in [[rock, INPUTS[0], Vector2i(1024, 512), 0], [ring, INPUTS[1], Vector2i(512, 512), 1], [arrow, INPUTS[2], Vector2i(64, 64), 1]]:
		_check(item[0].source_path == item[1] and item[0].dimensions == item[2] and item[0].compression == item[3], "Texture recipe retains its measured page geometry and compression.")
	for texture: Texture2D in [rock, ring, arrow, view.body_font.page, view.title_font.page]:
		_check(texture.ensure_loaded().ok and texture.get_image().get_size() == texture.dimensions, "Actual private input is read through the same public production recipe.")
	_check(view.get_node("Background/Rock").drawing_rect() == Rect2(-70, -80, 1280, 640)
		and view.get_node("Background/Ring").drawing_rect() == Rect2(-228, -274, 990, 990), "Loaded production dimensions produce the exact default source quads.")
	var body: AtlasFont = view.body_font.duplicate(true)
	var title: AtlasFont = view.title_font.duplicate(true)
	_check(view.configure_assets({}, {"body_font": body, "title_font": title}).ok and view.body_font == body and view.title_font == title, "Host fonts are reused by exact resource identity.")
	for path: String in ["Header/Title", "Unit/Name"]: _check(view.get_node(path).atlas_font == title, "Font22 is the actual production resource for: " + path)
	for section: String in ["Walker", "Jet"]:
		for part: String in ["Title", "Primary", "Secondary"]: _check(view.get_node(section + "/" + part).atlas_font == body, "Font13 is the actual production resource for each mode/weapon row.")
	_check(view.get_node("Navigation/Back").texture == arrow, "Both navigation passes share one decoded arrow recipe.")
	_check(view.view_snapshot() == _frame() and not view.get("_frame_supplied"), "Opening the standalone scene shows the faithful frozen Prototype display facts.")
	var before: Dictionary = _visual_state(view)
	var missing: AtlasFont = AtlasFont.new()
	var wrong: AtlasFont = AtlasFont.new()
	wrong.page = PlaceholderTexture2D.new()
	for fonts: Dictionary in [{"body_font": missing}, {"title_font": missing}, {"body_font": Resource.new()}, {"title_font": wrong}, {"unexpected": body}]:
		_check(not view.configure_assets({}, fonts).ok and _visual_state(view) == before, "Malformed font resource batches are refused atomically.")
	for paths: Dictionary in [{1: "route"}, {"rock": 3}, {"ring": null}, {"unowned": "route"}]:
		_check(not view.configure_assets(paths).ok and _visual_state(view) == before, "Malformed or unowned asset routes are refused before changing the scene.")


func _facts(view: Page) -> void:
	var facts: Dictionary = _frame()
	facts.unit_name = PackedInt32Array([65, 0, 0xd800, 161, 0xdc00, 0x2019])
	facts.walker_primary = PackedInt32Array()
	facts.jet_secondary = PackedInt32Array([90, 0, 65535])
	facts.unowned = Resource.new()
	_check(view.set_frame(facts).ok and view.view_snapshot().size() == 5, "One host batch stores only the five admitted raw text fields.")
	for field: String in Page.FIELDS: _check(view.get_node(Page.FIELDS[field]).displayed_units() == facts[field], "Raw UTF16 reaches the real production label without String normalization: " + field)
	var before: Dictionary = view.view_snapshot()
	facts.unit_name[0] = 66
	var returned: Dictionary = view.view_snapshot()
	returned.jet_secondary[0] = 88
	_check(view.view_snapshot() == before and view.get_node("Unit/Name").displayed_units() == before.unit_name, "Incoming/returned arrays and unknown resources cannot mutate the detached view facts.")
	var title_widths: PackedInt32Array = view.title_font.glyph_widths()
	var width: float = 0.0
	# Ordinary atlas mapping is ASCII-32 within32..287 and fallback31 outside,
	# deliberately different from CareerName's special name glyph map.
	for glyph: int in [33, 31, 31, 129, 31, 31]: width = F.value(width + F.value(title_widths[glyph] + 1))
	_check(view.get_node("Unit/Name").font_width() == maxf(0.0, F.value(width - 1.0)), "Configuration retains ordinary atlas width/fallback law for NUL, surrogates and punctuation.")
	_check(view.get_node("Walker/Primary").displayed_units().is_empty() and view.get_node("Walker/Primary").font_width() == 0.0, "An explicitly empty weapon label stays empty.")
	var visual: Dictionary = _visual_state(view)
	for field: String in Page.FIELDS:
		var absent: Dictionary = before.duplicate(true)
		absent.erase(field)
		_check(not view.set_frame(absent).ok and _visual_state(view) == visual, "A missing text field cannot partially update a configuration batch.")
		for invalid: Variant in [null, "wrong carrier", [65], 7, true, Resource.new(), PackedInt32Array([-1]), PackedInt32Array([65536])]:
			var malformed: Dictionary = before.duplicate(true)
			malformed[field] = invalid
			var result: Dictionary = view.set_frame(malformed)
			_check(not result.ok and result.error_type == "InvalidDataException" and _visual_state(view) == visual, "Strict malformed text refusal preserves every admitted label and authored property.")


func _navigation(view: Page, stage: Node2D) -> void:
	var cases: Array[Array] = [[Vector2(0, 430), 1], [Vector2(47.5, 477.5), 1], [Vector2(48, 450), 0], [Vector2(20, 478), 0],
		[Vector2(595, 430), 2], [Vector2(639.5, 477.5), 2], [Vector2(640, 450), 0], [Vector2(600, 478), 0],
		[Vector2(280, 210), 0], [Vector2(400, 430), 0]]
	for edge: Array in [[48.0, 450.0, true, [1, 0, 0]], [595.0, 450.0, true, [0, 2, 2]], [640.0, 450.0, true, [2, 0, 0]],
		[430.0, 20.0, false, [0, 1, 1]], [478.0, 20.0, false, [1, 0, 0]], [430.0, 620.0, false, [0, 2, 2]], [478.0, 620.0, false, [2, 0, 0]]]:
		for neighbor: int in [-1, 0, 1]:
			var value: float = _next_float(edge[0], neighbor)
			cases.append([Vector2(value, edge[1]) if edge[2] else Vector2(edge[1], value), edge[3][neighbor + 1]])
	for external_scale: Vector2 in [Vector2.ONE, Vector2(1.6, 1.6), Vector2(1.5003125, 1.5003125), Vector2(0.975, 1.333)]:
		stage.scale = external_scale
		stage.position = Vector2(37.25, -19.125)
		for pair: Array in cases: _check(view.hit_test(pair[0]) == pair[1], "Original half-open targets and nextafter neighbors ignore external Stage transforms: " + str(pair[0]))
	stage.scale = Vector2.ONE
	stage.position = Vector2.ZERO
	view.get_node("Navigation/Back").position.x = 600
	_check(view.hit_test(Vector2(620, 450)) == 1, "Edited overlapping arrows retain original Back priority.")
	view.get_node("Navigation/Back").position.x = 0


func _editing(view: Page) -> void:
	view.position = Vector2(11.5, 7.25)
	view.scale = Vector2(0.9375, 1.0625)
	view.rotation = -0.03125
	var nav: Control = view.get_node("Navigation")
	nav.position += Vector2(7.25, -12.5)
	nav.size = Vector2(654.15, 45)
	nav.rotation = 0.0625
	view.get_node("Header").position += Vector2(5.25, 2.5)
	view.get_node("Header").size = Vector2(413.7, 40)
	view.get_node("Unit").position += Vector2(-4.25, 3.5)
	view.get_node("Unit").size = Vector2(352, 40)
	view.get_node("Walker").position += Vector2(9.5, -4.25)
	view.get_node("Walker").size = Vector2(335.5, 52.8)
	await process_frame
	for section: String in ["Header", "Unit", "Walker", "Navigation"]:
		for child: Control in view.get_node(section).get_children(): _check(child.size == view.get_node(section).size, "Section Size edits reach actual draw bounds: " + section + "/" + str(child.name))
	var back: Control = view.get_node("Navigation/Back")
	var forward: Control = view.get_node("Navigation/Forward")
	var forward_rect: Rect2 = forward.get_rect()
	back.position = Vector2(12.5, -3.25)
	back.size = Vector2(591.85, 39.6)
	back.rotation = -0.03125
	await process_frame
	var point: Vector2 = view.get_transform() * nav.get_transform() * back.get_transform() * back.source_transform() * Vector2(20, 450)
	_check(view.hit_test(point) == 1 and forward.get_rect() == forward_rect, "One arrow's edited Position/Size/rotation changes its real design-space hit without replacing its sibling.")
	var rock: Control = view.get_node("Background/Rock")
	var ring: Control = view.get_node("Background/Ring")
	var rock_rect: Rect2 = rock.get_rect()
	var original: Transform2D = ring.get_global_transform_with_canvas() * ring.source_transform()
	ring.position = Vector2(4.25, -2.5)
	ring.size = Vector2(672, 504)
	ring.source_anchor += Vector2(3.5, -1.25)
	ring.source_size = Vector2(997.3, 983.7)
	rock.texture_scale = Vector2(1.375, 1.125)
	await process_frame
	var sx: float = F.value(ring.source_size.x / 512.0)
	var sy: float = F.value(ring.source_size.y / 512.0)
	var width: float = F.value(512.0 * sx)
	var height: float = F.value(512.0 * sy)
	_check(ring.drawing_rect() == Rect2(F.value(ring.source_anchor.x - F.value(width * 0.5)), F.value(ring.source_anchor.y - F.value(height * 0.5)), width, height),
		"Edited ring dimensions preserve divide, multiply, half and subtraction binary32 stores.")
	_check(ring.get_global_transform_with_canvas() * ring.source_transform() != original and rock.get_rect() == rock_rect
		and rock.drawing_rect() == Rect2(-70, -80, 1408, 576), "Independent background pass edits affect actual quads without overwriting sibling layout.")
	var label: Control = view.get_node("Walker/Primary")
	var imported: PackedInt32Array = label.displayed_units()
	label.text = "Enhanced primary"
	_check(label.displayed_units() == imported, "Inspector text needs an explicit override before replacing faithful configuration text.")
	var draws: Array[int] = [0]
	var on_draw: Callable = func() -> void: draws[0] += 1
	label.draw.connect(on_draw)
	await process_frame
	var before: int = draws[0]
	label.override_text = true
	label.source_anchor += Vector2(2.25, -1.5)
	await process_frame
	await process_frame
	_check(label.displayed_units() == Text.units("Enhanced primary").value and draws[0] > before,
		"Frozen enhanced text and source-anchor edits queue a real production redraw without advancing time.")
	label.draw.disconnect(on_draw)
	view.get_node("Header/Title").text = "Enhanced configuration"
	view.get_node("Header/Title").override_text = true
	var geometry: Dictionary = _geometry(view)
	_check(view.set_frame(_frame()).ok and _geometry(view) == geometry and forward.get_rect() == forward_rect,
		"Display batches preserve every authored section/pass transform, source bound and explicit text override.")
	var faithful: Texture2D = rock.texture
	var route: String = faithful.source_path
	_check(view.configure_assets({"rock": ProjectSettings.globalize_path(route)}).ok, "An explicit alternate asset route reads the same private production input.")
	_check(rock.texture != faithful and faithful.source_path == route, "An enhanced recipe cannot mutate the shared faithful route.")


func _preview(view: Page) -> void:
	var before: Dictionary = view.view_snapshot()
	view.editor_unit_name = "Inspect the unit name"
	_check(Engine.is_editor_hint() or view.view_snapshot() == before, "Frozen Inspector fields do not override a live runtime batch.")
	view.editor_jet_secondary = "Inspect secondary"
	_check(view.show_editor_preview().ok and not view.get("_frame_supplied")
		and view.view_snapshot().unit_name == Text.units("Inspect the unit name").value, "Explicit preview displays authored facts without a session owner.")
	view.editor_walker_secondary = "Frozen secondary"
	_check(view.get_node("Walker/Secondary").displayed_units() == Text.units("Frozen secondary").value
		and not view.get("_frame_supplied"), "Frozen Inspector edits update the actual production labels.")
	var frozen: Dictionary = _visual_state(view)
	await process_frame
	await process_frame
	_check(_visual_state(view) == frozen, "Idle frames change neither scene content nor configuration facts.")


func _publication(view: Page) -> void:
	var packed := PackedScene.new()
	_check(packed.pack(view) == OK, "Actually edited production scene packs successfully.")
	var state: SceneState = packed.get_state()
	var visited: Dictionary = {}
	for node: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(node)): _stored(state.get_node_property_value(node, property), visited)
	var path: String = _output.path_join("roundtrip.tscn")
	_check(ResourceSaver.save(packed, path) == OK, "Only the fresh owned roundtrip artifact is written.")
	var source: String = FileAccess.get_file_as_string(path)
	_check(not source.contains("type=\"Image\"") and not source.contains("type=\"ImageTexture\"") and not source.contains("PackedByteArray("), "Public serialization contains recipes and layout, never private pixels.")
	var reopened: PackedScene = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	_check(reopened != null, "The saved edited production scene reopens.")
	if reopened == null: return
	var copy: Page = reopened.instantiate()
	_check(copy.get_node("Navigation").get_rect() == view.get_node("Navigation").get_rect()
		and copy.get_node("Unit").get_rect() == view.get_node("Unit").get_rect(), "Edited section frames remain inspectable before Ready.")
	for path_name: String in ["Background/Ring", "Navigation/Back"]:
		var original: Control = view.get_node(path_name)
		var restored: Control = copy.get_node(path_name)
		_check(restored.offset_left == original.offset_left and restored.offset_top == original.offset_top
			and restored.offset_right == original.offset_right and restored.offset_bottom == original.offset_bottom
			and restored.rotation == original.rotation, "Per-pass Position/Size/rotation survives native anchor serialization.")
	_check(copy.get_node("Walker/Primary").override_text and copy.get_node("Walker/Primary").text == "Enhanced primary"
		and copy.get_node("Header/Title").override_text, "Explicit text overrides survive before playing.")
	_check(copy.get_node("Background/Rock").texture.source_path == view.get_node("Background/Rock").texture.source_path
		and copy.get_node("Background/Ring").ink_color.r > 1.0, "Enhanced recipe routes and the above1 measured gain survive publication.")
	view.get_parent().add_child(copy)
	await process_frame
	await process_frame
	_check(copy.get("_assets_configured") and copy.get("_error") == "" and not copy.get("_frame_supplied"), "Reopened scene admits the same harmless production view.")
	_check(_visual_state(copy) == _visual_state(view), "Reopened native layout reproduces all edited drawing bounds, labels, resources and frozen facts.")
	copy.queue_free()
	copy = null
	await process_frame


func _geometry(view: Page) -> Dictionary:
	var result: Dictionary = {"page_transform": view.get_transform(), "page_size": view.size}
	for node: Control in view.find_children("*", "Control", true, false):
		var state: Dictionary = {"transform": node.get_transform(), "size": node.size, "visible": node.visible}
		for property: String in ["source_rect", "source_anchor", "source_size", "texture_scale", "rectangle", "hit_rect", "glyph_scale", "text", "override_text", "ink_color"]:
			if node.get(property) != null: state[property] = node.get(property)
		result[str(view.get_path_to(node))] = state
	return result


func _visual_state(view: Page) -> Dictionary:
	var result: Dictionary = _geometry(view)
	result.facts = view.view_snapshot()
	for node: Control in view.find_children("*", "Control", true, false):
		var state: Dictionary = result[str(view.get_path_to(node))]
		if node.has_method("drawing_rect"): state.draw_rect = node.drawing_rect()
		if node.has_method("displayed_units"): state.units = node.displayed_units(); state.origin = node.drawing_origin(); state.ink = node.drawing_color()
		if node.get("texture") != null and node.texture.get("source_path") != null: state.texture_route = node.texture.source_path
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
			and not node.is_processing_unhandled_input(), "Presentation owns no input or simulation/frame clock: " + str(node.name))
	for type: String in ["Timer", "AnimationPlayer", "AudioStreamPlayer", "AudioStreamPlayer2D", "AudioStreamPlayer3D", "VideoStreamPlayer", "Camera2D", "Node3D"]:
		_check(view.find_children("*", type, true, false).is_empty(), "Missing media/model content and side-effect owners remain absent: " + type)
	_check(Input.mouse_mode == pointer, "Scene activity preserves pointer ownership.")
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
	print("CONFIGURATION_SCENE_SECTION: ", section)


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
	print("CONFIGURATION_SCENE_CHECKS: ", JSON.stringify(report))
	quit(0 if _failures.is_empty() else 1)


static func _frame() -> Dictionary:
	return {"unit_name": Text.units("BE:A Unit-00 'Prototype'").value, "walker_primary": Text.units("Pulse Cannon").value,
		"walker_secondary": Text.units("Vulcan Cannon").value, "jet_primary": Text.units("Vulcan Cannon").value, "jet_secondary": Text.units("Micro Missiles").value}


static func _owned_directory(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or not path.begins_with(owned + "/"): return false
	var directory := DirAccess.open(owned)
	if directory == null: return false
	for part: String in path.trim_prefix(owned + "/").split("/", false):
		if directory.is_link(part) or directory.change_dir(part) != OK: return false
	return true


static func _next_float(value: float, direction: int) -> float:
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	bytes.encode_u32(0, bytes.decode_u32(0) + direction)
	return bytes.decode_float(0)
