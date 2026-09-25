# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual production CareerName scene in standard headless Godot. The sole
## argument is a fresh owned local-data directory; inputs remain read-only.
const Page = preload("res://Scenes/Frontend/career_name_presentation.gd")
const CareerLabel = preload("res://Scenes/Frontend/career_name_label.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const REQUIRED: Array[String] = ["authored_scene", "production_assets", "display_facts", "name_laws", "editing", "frozen_preview", "publication", "ownership"]
const SOURCES: Array[String] = ["res://Scenes/Frontend/CareerName.tscn", "res://Scenes/Frontend/career_name_presentation.gd",
	"res://Scenes/Frontend/career_name_target.gd", "res://Scenes/Frontend/career_name_arrow.gd",
	"res://Scenes/Frontend/career_name_bracket.gd", "res://Scenes/Frontend/career_name_label.gd",
	"res://Scenes/Frontend/career_name_highlight.gd", "res://Scenes/Frontend/career_name_underlay.gd",
	"res://Scenes/Frontend/quit_confirm_surface.gd", "res://Scenes/Frontend/main_menu_underlay.gd",
	"res://Scenes/Frontend/frontend_atlas_font.gd", "res://Scenes/Frontend/frontend_underlay.gd",
	"res://Scenes/Frontend/FrontendFont13.tres", "res://Scenes/Frontend/FrontendFont22.tres"]
const INPUTS: Array[String] = ["res://Assets/Frontend/level-bracket-01.texture.aya", "res://Assets/Frontend/fe-arrow.texture.aya",
	"res://Assets/Hud/font-13ps.texture.aya", "res://Assets/Hud/font-22.texture.aya",
	"res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb"]
const SECTIONS: Dictionary = {"Background": Rect2(0, 0, 640, 480), "Decoration": Rect2(0, 0, 640, 480),
	"Header": Rect2(191, 65, 394, 32), "List": Rect2(128, 130, 403, 272),
	"Name": Rect2(128, 408, 403, 44), "Navigation": Rect2(9, 437, 622, 41)}
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
	var packed: PackedScene = load("res://Scenes/Frontend/CareerName.tscn")
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
	if _check(view.get("_assets_configured") and view.get("_error") == "", "Standalone native CareerName admits its production assets without C#."):
		_assets(view)
		_done("production_assets")
		_facts(view, stage)
		_done("display_facts")
		_name_laws(view)
		_done("name_laws")
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
	_check(not view.is_node_ready() and not view.is_inside_tree(), "The production scene exposes authored controls before Ready.")
	_check(view.get_rect() == Rect2(0, 0, 640, 480) and view.get_child_count() == 8, "Source stage and eight ordered production sections are authored.")
	for path: String in SECTIONS: _check(view.get_node(path).get_rect() == SECTIONS[path], "Retained per-section canvas frame: " + path)
	_check(view.get_node("VerticalGuide").get_rect() == Rect2(123, 0, 1, 480) and view.get_node("HorizontalGuide").get_rect() == Rect2(0, 180, 640, 1), "The measured crosshair guides are native editable ColorRects.")
	_check(view.get_node("Header/Panel").rectangle == Rect2(191, 69, 394, 21)
		and view.get_node("Header/Title").text == Page.TITLE and view.get_node("Header/Title").glyph_scale == Vector2.ONE
		and view.get_node("Header/Title").source_anchor == Vector2(390, 65), "The title preserves the corrected Font22 scale1 header and anchor.")
	var list_order: Array[String] = ["Border", "Fill", "Guide", "Divider", "ThumbTop", "ThumbBottom", "ThumbLeft", "ThumbRight", "Rows"]
	for index: int in range(list_order.size()): _check(view.get_node("List").get_child(index).name == list_order[index], "Actual list draw order: " + list_order[index])
	_check(view.get_node("List/Rows").get_child_count() == 11, "Eleven real row labels cover the original y+16*1.4 <=400 cutoff.")
	for index: int in range(11):
		var row: Control = view.get_node("List/Rows/Row%02d" % index)
		_check(row.source_anchor == Vector2(132, 137 + index * 24) and row.glyph_scale == Vector2(1.4, 1.4)
			and not row.name_glyphs, "Each list row retains ordinary atlas mapping, source pitch and scale.")
	_check(view.get_node("Name/Label").name_glyphs and view.get_node("Name/Label").text == "BEA 1"
		and view.get_node("Name/Label").source_anchor == Vector2(329.5, 417), "The name field exposes the faithful default and its distinct glyph law.")
	_check(view.get_node("Navigation/Back").rectangle == Rect2(36, 443, -27, 35)
		and view.get_node("Navigation/Forward").rectangle == Rect2(604, 437, 27, 35), "Navigation keeps the signed mirrored rectangle and original independent Y positions.")
	for section: String in SECTIONS:
		for node: Control in view.get_node(section).find_children("*", "Control", true, false):
			_check(node.anchor_right == 1.0 and node.anchor_bottom == 1.0, "Native full-rect anchors couple child geometry to the edited section.")
			if node.get("source_rect") != null: _check(node.source_rect == SECTIONS[section], "Draw pass retains the section source matrix grouping: " + str(node.name))
	for node: Control in view.find_children("*", "Control", true, false):
		_check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE, "Authored control ignores input: " + str(node.name))
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "Every control is inspectable in standard Godot.")


func _assets(view: Page) -> void:
	_check(view.body_font == load("res://Scenes/Frontend/FrontendFont13.tres") and view.title_font == load("res://Scenes/Frontend/FrontendFont22.tres"), "Standalone preview uses shared production Font13/Font22 recipes.")
	var bracket: Texture2D = view.get_node("Decoration/Body").texture
	var arrow: Texture2D = view.get_node("Navigation/Forward").texture
	_check(bracket.source_path == INPUTS[0] and bracket.dimensions == Vector2i(512, 512) and bracket.compression == 1, "Bracket is the original 512x512 DXT2 recipe.")
	_check(arrow.source_path == INPUTS[1] and arrow.dimensions == Vector2i(64, 64) and arrow.compression == 1, "Arrow is the original 64x64 DXT2 recipe.")
	for texture: Texture2D in [bracket, arrow, view.body_font.page, view.title_font.page]:
		_check(texture.ensure_loaded().ok and texture.get_image().get_size() == texture.dimensions, "Private image is read through its public production recipe.")
	var body: AtlasFont = view.body_font.duplicate(true)
	var title: AtlasFont = view.title_font.duplicate(true)
	var frames: Array = view.get_node("Background").get("_frames").slice(0, 1)
	_check(not frames.is_empty(), "The materialized shared FEBack strip supplies real frames.")
	_check(view.configure_assets({}, {"body_font": body, "title_font": title}, frames).ok and view.body_font == body and view.title_font == title, "Host fonts are borrowed by exact resource identity.")
	_check(view.get_node("Background").get("_frames")[0] == frames[0], "The production view borrows the same decoded underlay frame, without a second image.")
	for path: String in ["Name/Label", "List/Rows/Row00", "List/Rows/Row10"]: _check(view.get_node(path).atlas_font == body, "Body label shares the supplied production font: " + path)
	_check(view.get_node("Header/Title").atlas_font == title, "Header shares the supplied production Font22.")
	_check(view.get_node("Decoration/Shadow").texture == bracket and view.get_node("Navigation/Back").texture == arrow, "Each texture's draw passes retain a shared recipe.")
	_check(view.view_snapshot() == _frame() and not view.get("_frame_supplied"), "Standalone opens the frozen faithful BEA1 default with no career discovery.")
	var before: Dictionary = _visual_state(view)
	var malformed: AtlasFont = AtlasFont.new()
	var wrong: AtlasFont = AtlasFont.new()
	wrong.page = PlaceholderTexture2D.new()
	for fonts: Dictionary in [{"body_font": malformed}, {"title_font": malformed}, {"body_font": Resource.new()}, {"title_font": wrong}, {"unowned": body}]:
		_check(not view.configure_assets({}, fonts, frames).ok and _visual_state(view) == before, "Malformed shared font resources are refused before changing live content.")
	for paths: Dictionary in [{1: "route"}, {"bracket": 1}, {"unknown": "route"}]:
		_check(not view.configure_assets(paths, {}, frames).ok and _visual_state(view) == before, "Unowned/malformed routes receive an atomic refusal.")
	_check(not view.configure_assets({}, {}, [Resource.new()]).ok and _visual_state(view) == before, "A non-texture background batch is refused atomically.")


func _facts(view: Page, stage: Node2D) -> void:
	var names: Array[PackedInt32Array] = []
	for index: int in range(14): names.append(Text.units("Career " + str(index)).value)
	var facts: Dictionary = _frame()
	facts.career_names = names
	facts.selected_career_index = 10
	facts.game_name = PackedInt32Array([65, 0, 0xd800, 0xdc00, 161, 191])
	facts.background_seconds = 0.5
	facts.unowned = Resource.new()
	_check(view.set_frame(facts).ok and view.view_snapshot().size() == 5, "One display batch keeps only the five admitted fields, including raw UTF16.")
	for index: int in range(11):
		var row: Control = view.get_node("List/Rows/Row%02d" % index)
		_check(row.displayed_units() == names[index] and row.draws_content()
			and row.drawing_color() == (row.selected_ink if index == 10 else row.ink_color), "Only the admitted row index receives selected ink; first11 rows retain their text.")
	var admitted: Dictionary = view.view_snapshot()
	facts.game_name[0] = 66
	facts.career_names[0][0] = 90
	var returned: Dictionary = view.view_snapshot()
	returned.game_name[0] = 67
	returned.career_names[1][0] = 88
	_check(view.view_snapshot() == admitted and view.get_node("Name/Label").displayed_units() == admitted.game_name, "Nested incoming and returned arrays cannot mutate the admitted raw display facts.")
	var nullable: Dictionary = admitted.duplicate(true)
	nullable.career_names = Array(nullable.career_names)
	nullable.career_names[11] = null
	nullable.selected_career_index = 12
	_check(view.set_frame(nullable).ok and view.view_snapshot().career_names.size() == 14
		and view.view_snapshot().career_names[11] == null, "A null beyond the original visible-row cutoff stays null without being read or normalized.")
	nullable.career_names[11] = Text.units("changed after admission").value
	var nullable_copy: Dictionary = view.view_snapshot()
	nullable_copy.career_names[11] = PackedInt32Array()
	_check(view.view_snapshot().career_names[11] == null, "Detached offscreen nullable rows cannot be replaced through incoming or returned arrays.")
	admitted = view.view_snapshot()
	var before: Dictionary = _visual_state(view)
	var invalids: Array[Dictionary] = [{}, {"career_names": null}, {"career_names": [null]}, {"career_names": ["wrong carrier"]}, {"career_names": [PackedInt32Array([-1])]},
		{"game_name": null}, {"game_name": "BEA 1"}, {"game_name": PackedInt32Array([65536])}, {"selected_career_index": -2},
		{"selected_career_index": 14}, {"selected_career_index": true}, {"selected_career_index": 0.0},
		{"game_name_is_fresh": 1}, {"background_seconds": 0}, {"background_seconds": NAN}, {"background_seconds": INF}]
	for change: Dictionary in invalids:
		var invalid: Dictionary = admitted.duplicate(true)
		if change.is_empty(): invalid.erase("game_name")
		else: invalid.merge(change, true)
		var refused: Dictionary = view.set_frame(invalid)
		_check(not refused.ok and refused.error_type == "InvalidDataException" and _visual_state(view) == before, "Invalid frame data is refused before any display mutation.")
	var cases: Array[Array] = [[Vector2(0, 430), 1], [Vector2(45.5, 477.5), 1], [Vector2(46, 450), 0], [Vector2(20, 478), 0],
		[Vector2(595, 430), 2], [Vector2(639.5, 477.5), 2], [Vector2(640, 450), 0], [Vector2(600, 478), 0],
		[Vector2(128, 408), 2], [Vector2(530.5, 451.5), 2], [Vector2(531, 420), 0], [Vector2(300, 452), 0], [Vector2(150, 140), 0]]
	for edge: Array in [[46.0, 450.0, true, [1, 0, 0]], [595.0, 460.0, true, [0, 2, 2]], [640.0, 460.0, true, [2, 0, 0]],
		[128.0, 420.0, true, [0, 2, 2]], [531.0, 420.0, true, [2, 0, 0]], [408.0, 300.0, false, [0, 2, 2]], [452.0, 300.0, false, [2, 0, 0]]]:
		for neighbor: int in [-1, 0, 1]:
			var boundary: float = _next_float(edge[0], neighbor)
			cases.append([Vector2(boundary, edge[1]) if edge[2] else Vector2(edge[1], boundary), edge[3][neighbor + 1]])
	for external_scale: Vector2 in [Vector2.ONE, Vector2(1.6, 1.6), Vector2(1.5003125, 1.5003125), Vector2(0.975, 1.333)]:
		stage.scale = external_scale
		stage.position = Vector2(37.25, -19.125)
		for pair: Array in cases: _check(view.hit_test(pair[0]) == pair[1], "Navigation/name half-open design targets and neighbors ignore external Stage transforms: " + str(pair[0]))
	stage.scale = Vector2.ONE
	stage.position = Vector2.ZERO
	view.get_node("Navigation/Back").position.x = 600
	_check(view.hit_test(Vector2(620, 460)) == 1, "Edited overlapping arrows retain the original Back-first route.")
	view.get_node("Navigation/Back").position.x = 0
	facts = _frame()
	facts.career_names = [Text.units("one row").value]
	facts.selected_career_index = 0
	facts.game_name_is_fresh = false
	_check(view.set_frame(facts).ok and not view.get_node("Name/Highlight").draws_content(), "Freshness controls only the existing name highlight.")
	for index: int in range(11): _check(view.get_node("List/Rows/Row%02d" % index).draws_content() == (index == 0), "A shorter batch clears stale row draws without replacing authored row controls.")


func _name_laws(view: Page) -> void:
	var raw := PackedInt32Array([65, 0, 161, 191, 0xd800, 0xdc00, 0x2019, 0x2013])
	var mapped := PackedInt32Array([33, 145, 136, 137, 145, 145, 7, 13])
	var widths: PackedInt32Array = view.body_font.glyph_widths()
	var integer_sum: int = 0
	for glyph: int in mapped: integer_sum += widths[glyph] + 1
	var facts: Dictionary = _frame()
	facts.game_name = raw
	_check(view.set_frame(facts).ok and view.get_node("Name/Label").displayed_units() == raw, "NUL and paired/unpaired surrogate units remain raw through the actual scene.")
	var expected: float = F.value(F.value(maxi(0, integer_sum - 1)) * F.value(1.4))
	_check(view.get_node("Name/Label").font_width() == expected, "Centered field uses fallback145, punctuation slots136/137, curly apostrophe7 and en-dash13, then one binary32 scale.")
	_check(view.get_node("Name/Label").drawing_origin() == Vector2(F.value(329.5 - F.value(expected * 0.5)), 417), "Name centering preserves the exact binary32 operation order.")
	var title_widths: PackedInt32Array = view.title_font.glyph_widths()
	var extent: int = 0
	for glyph: int in [33, 145, 137, 136, 145, 145, 7, 13]: extent += title_widths[glyph] + 1
	_check(view.measure_name_extent(raw) == extent, "Host input width uses Font22 and swaps inverted punctuation, without minus1 or scale.")
	_check(view.measure_name_extent(PackedInt32Array()) == 0 and CareerLabel.checked_name_width(PackedInt32Array(), widths, 1.4).value == 0.0, "Empty name has zero display and input extent.")
	var artificial := PackedInt32Array()
	artificial.resize(256)
	artificial.fill(0)
	artificial[33] = 1073741823
	var overflow: Dictionary = CareerLabel.checked_name_width(PackedInt32Array([65, 65]), artificial, 1.4)
	_check(not overflow.ok and overflow.error_type == "OverflowException", "Checked display accumulation refuses Int32 overflow using a bounded metric fixture.")
	_check(CareerLabel.unchecked_name_extent(PackedInt32Array([65, 65]), artificial) == -2147483648, "Input extent preserves unchecked Int32 wrap for the same bounded fixture.")
	# This is the harness-owned duplicate font's transient measured cache, never
	# its private page or recipe. Exercise the real batch refusal without huge text.
	view.body_font.set("_widths", artificial)
	var before: Dictionary = _visual_state(view)
	var overflowing: Dictionary = _frame()
	overflowing.game_name = PackedInt32Array([65, 65])
	var refused: Dictionary = view.set_frame(overflowing)
	_check(not refused.ok and refused.error_type == "OverflowException" and _visual_state(view) == before,
		"Actual production batch refuses checked-width overflow without partially changing labels or facts.")
	view.body_font.set("_widths", widths)
	artificial[33] = 16777216
	var rounded: Dictionary = CareerLabel.checked_name_width(PackedInt32Array([65, 65, 65]), artificial, 1.4)
	_check(rounded.ok and rounded.value == F.value(F.value(50331650) * F.value(1.4)), "Display sum stays integral until the final C# int-to-float conversion and multiplication.")
	_check(not CareerLabel.checked_name_width(raw, PackedInt32Array(), 1.4).ok, "Missing glyph metrics cannot silently replace the width contract.")


func _editing(view: Page) -> void:
	view.position = Vector2(11.5, 7.25)
	view.scale = Vector2(0.9375, 1.0625)
	view.rotation = -0.03125
	var field: Control = view.get_node("Name")
	field.position += Vector2(23.25, -11.5)
	field.size = Vector2(483.6, 55)
	field.rotation = 0.0625
	view.get_node("Header").position += Vector2(5.25, 2.5)
	view.get_node("Header").size = Vector2(413.7, 40)
	view.get_node("List").size = Vector2(443.3, 299.2)
	await process_frame
	for path: String in ["Border", "Fill", "Highlight", "Label"]: _check(view.get_node("Name/" + path).size == field.size, "Name Size edits reach actual draw bounds and the hit target.")
	var point: Vector2 = view.get_transform() * field.get_transform() * field.source_transform() * Vector2(329.5, 430)
	_check(view.hit_test(point) == 2, "Authored page/Name transforms affect the real confirm target in design space.")
	var sibling: Control = view.get_node("Decoration/Shadow")
	var sibling_rect: Rect2 = sibling.get_rect()
	var body: Control = view.get_node("Decoration/Body")
	var original_draw: Transform2D = body.get_global_transform_with_canvas() * body.source_transform()
	body.position = Vector2(7.25, -3.5)
	body.size = Vector2(672, 504)
	body.source_anchor += Vector2(4.5, -2.25)
	await process_frame
	_check(body.get_global_transform_with_canvas() * body.source_transform() != original_draw and sibling.get_rect() == sibling_rect, "One bracket's Position/Size edits change actual drawing without moving its sibling.")
	var label: Control = view.get_node("Name/Label")
	var imported: PackedInt32Array = label.displayed_units()
	label.text = "Enhanced name"
	_check(label.displayed_units() == imported, "Inspector text needs an explicit override before replacing faithful raw name data.")
	var highlight: Control = view.get_node("Name/Highlight")
	var draw_count: Array[int] = [0]
	var on_draw: Callable = func() -> void: draw_count[0] += 1
	highlight.draw.connect(on_draw)
	await process_frame
	var previous: int = draw_count[0]
	label.override_text = true
	label.source_anchor += Vector2(3, 2)
	await process_frame
	await process_frame
	_check(label.displayed_units() == Text.units("Enhanced name").value
		and highlight.drawing_rect().position == label.drawing_origin() + Vector2(-4, -2)
		and highlight.drawing_rect().size.x == F.value(label.font_width() + 8.0), "Enhanced text and source-anchor edits redraw the actual paired highlight.")
	_check(draw_count[0] > previous, "Frozen Inspector changes queue real redraw without a frame/session clock.")
	highlight.draw.disconnect(on_draw)
	view.get_node("List/Rows/Row10").override_text = true
	view.get_node("List/Rows/Row10").text = "Enhanced empty slot"
	_check(view.get_node("List/Rows/Row10").draws_content(), "An explicit override makes an otherwise absent authored row inspectable.")
	var layout: Dictionary = _geometry(view)
	_check(view.set_frame(_frame()).ok and _geometry(view) == layout and sibling.get_rect() == sibling_rect, "Display batches preserve explicit transforms, text switches and sibling geometry.")
	var original_recipe: Texture2D = body.texture
	var original_route: String = original_recipe.source_path
	var frames: Array = view.get_node("Background").get("_frames")
	_check(view.configure_assets({"bracket": ProjectSettings.globalize_path(original_route)}, {}, frames).ok,
		"Explicit alternate recipe routes read the same private input.")
	_check(body.texture != original_recipe and original_recipe.source_path == original_route and body.texture == sibling.texture,
		"Enhanced asset route is a separate shared recipe and cannot mutate the faithful default.")


func _preview(view: Page) -> void:
	var before: Dictionary = view.view_snapshot()
	view.editor_game_name = "Inspect this name"
	_check(Engine.is_editor_hint() or view.view_snapshot() == before, "Frozen preview fields cannot override an active runtime batch.")
	view.editor_career_names = PackedStringArray(["First authored preview", "Second preview"])
	view.editor_selected_career_index = 1
	view.editor_background_seconds = 2.5
	_check(view.show_editor_preview().ok and not view.get("_frame_supplied") and view.view_snapshot().game_name == Text.units("Inspect this name").value,
		"Explicit preview displays the authored facts without taking session ownership.")
	view.editor_game_name_is_fresh = false
	_check(not view.get_node("Name/Highlight").draws_content() and not view.get("_frame_supplied"), "Frozen Inspector freshness updates the production highlight.")
	var frozen: Dictionary = _visual_state(view)
	await process_frame
	await process_frame
	_check(_visual_state(view) == frozen, "Idle engine frames change no facts, geometry or background time.")


func _publication(view: Page) -> void:
	var packed := PackedScene.new()
	_check(packed.pack(view) == OK, "The actually edited production scene packs successfully.")
	var state: SceneState = packed.get_state()
	var visited: Dictionary = {}
	for node: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(node)): _stored(state.get_node_property_value(node, property), visited)
	var path: String = _output.path_join("roundtrip.tscn")
	_check(ResourceSaver.save(packed, path) == OK, "Only the fresh owned roundtrip artifact is written.")
	var source: String = FileAccess.get_file_as_string(path)
	_check(not source.contains("type=\"Image\"") and not source.contains("type=\"ImageTexture\"") and not source.contains("PackedByteArray("), "Public scene serialization excludes private pixels and byte buffers.")
	var reopened: PackedScene = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	_check(reopened != null, "Saved edited production scene reopens.")
	if reopened == null: return
	var copy: Page = reopened.instantiate()
	_check(copy.get_node("Name").get_rect() == view.get_node("Name").get_rect()
		and copy.get_node("Name").rotation == view.get_node("Name").rotation, "Authored Name frame survives before Ready.")
	var original: Control = view.get_node("Decoration/Body")
	var restored: Control = copy.get_node("Decoration/Body")
	_check(restored.offset_left == original.offset_left and restored.offset_top == original.offset_top
		and restored.offset_right == original.offset_right and restored.offset_bottom == original.offset_bottom
		and restored.source_anchor == original.source_anchor, "Per-pass offsets, Size and source anchor survive serialization.")
	_check(copy.get_node("Name/Label").override_text and copy.get_node("Name/Label").text == "Enhanced name"
		and copy.get_node("List/Rows/Row10").override_text, "Explicit text overrides remain inspectable before playing.")
	_check(copy.get_node("Decoration/Body").texture.source_path == original.texture.source_path
		and copy.editor_background_seconds == 2.5, "Enhanced recipe and frozen preview parameters survive publication.")
	view.get_parent().add_child(copy)
	await process_frame
	await process_frame
	_check(copy.get("_assets_configured") and copy.get("_error") == "" and not copy.get("_frame_supplied"), "Reopened scene admits its recipes into a harmless frozen view.")
	_check(_geometry(copy) == _geometry(view) and copy.view_snapshot() == view.view_snapshot(), "Reopened native layout and frozen facts reproduce every edited production component.")
	copy.queue_free()
	copy = null
	await process_frame


func _geometry(view: Page) -> Dictionary:
	var result: Dictionary = {"page_transform": view.get_transform(), "page_size": view.size}
	for node: Control in view.find_children("*", "Control", true, false):
		var state: Dictionary = {"transform": node.get_transform(), "size": node.size, "visible": node.visible}
		for property: String in ["source_rect", "source_anchor", "rectangle", "hit_rect", "glyph_scale", "text", "override_text"]:
			if node.get(property) != null: state[property] = node.get(property)
		result[str(view.get_path_to(node))] = state
	return result


func _visual_state(view: Page) -> Dictionary:
	var result: Dictionary = _geometry(view)
	result.facts = view.view_snapshot()
	result.background = view.get_node("Background").view_snapshot()
	for node: Control in view.find_children("*", "Control", true, false):
		var state: Dictionary = result[str(view.get_path_to(node))]
		if node.has_method("drawing_rect"): state.draw_rect = node.drawing_rect()
		if node.has_method("draws_content"): state.draws = node.draws_content()
		if node.has_method("displayed_units"): state.units = node.displayed_units(); state.origin = node.drawing_origin(); state.ink = node.drawing_color()
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
	for type: String in ["Timer", "AnimationPlayer", "AudioStreamPlayer", "AudioStreamPlayer2D", "AudioStreamPlayer3D", "Camera2D", "Node3D"]:
		_check(view.find_children("*", type, true, false).is_empty(), "Presentation creates no side-effect owner: " + type)
	_check(Input.mouse_mode == pointer, "Editor and runtime view activity leave pointer ownership unchanged.")
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
	print("CAREER_NAME_SCENE_SECTION: ", section)


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
	print("CAREER_NAME_SCENE_CHECKS: ", JSON.stringify(report))
	quit(0 if _failures.is_empty() else 1)


static func _frame() -> Dictionary:
	return {"career_names": [], "selected_career_index": -1, "game_name": PackedInt32Array([66, 69, 65, 32, 49]),
		"game_name_is_fresh": true, "background_seconds": 0.0}


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
