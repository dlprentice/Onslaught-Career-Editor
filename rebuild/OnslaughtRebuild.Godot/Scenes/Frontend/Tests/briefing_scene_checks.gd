# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual production Mission Briefing in standard headless Godot. The one
## argument must be a fresh owned local-data output directory.
const Page = preload("res://Scenes/Frontend/briefing_presentation.gd")
const BodyText = preload("res://Scenes/Frontend/briefing_body.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const WorldStrings = preload("res://Core/frontend_world_strings.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const REQUIRED: Array[String] = ["authored_scene", "production_assets", "display_facts", "wrap_law", "navigation", "editing", "frozen_preview", "publication", "ownership"]
const SOURCES: Array[String] = ["res://Scenes/Frontend/MissionBriefing.tscn", "res://Scenes/Frontend/briefing_presentation.gd",
	"res://Scenes/Frontend/briefing_body.gd", "res://Scenes/Frontend/configuration_rock.gd", "res://Scenes/Frontend/configuration_ring.gd",
	"res://Scenes/Frontend/ConfigurationRock.tres", "res://Scenes/Frontend/ConfigurationRing.tres",
	"res://Scenes/Frontend/career_name_label.gd", "res://Scenes/Frontend/career_name_arrow.gd",
	"res://Scenes/Frontend/career_name_target.gd", "res://Scenes/Frontend/quit_confirm_surface.gd",
	"res://Scenes/Frontend/frontend_atlas_font.gd", "res://Scenes/Frontend/FrontendFont13.tres", "res://Scenes/Frontend/FrontendFont22.tres",
	"res://Core/frontend_world_strings.gd"]
const INPUTS: Array[String] = ["res://Assets/Frontend/Backgrounds/rock.texture.aya", "res://Assets/Frontend/level-bracket-02.texture.aya",
	"res://Assets/Frontend/fe-arrow.texture.aya", "res://Assets/Hud/font-13ps.texture.aya", "res://Assets/Hud/font-22.texture.aya"]
const SECTIONS: Dictionary = {"Background": Rect2(0, 0, 640, 480), "Header": Rect2(191, 65, 394, 32),
	"LevelName": Rect2(178.5, 118, 407, 32), "Body": Rect2(80, 163.5, 505, 122.5), "Navigation": Rect2(9, 438, 623, 36)}
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
	var packed: PackedScene = load("res://Scenes/Frontend/MissionBriefing.tscn")
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
	if _check(view.get("_assets_configured") and view.get("_error") == "", "Standalone Briefing admits the same production recipes without C#."):
		_assets(view)
		_done("production_assets")
		_facts(view)
		_done("display_facts")
		_wrap_law(view)
		_done("wrap_law")
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

func _geometry(view: Page) -> Dictionary:
	var result: Dictionary = {"page_transform": view.get_transform(), "page_size": view.size}
	for node: Control in view.find_children("*", "Control", true, false):
		var state: Dictionary = {"transform": node.get_transform(), "size": node.size, "visible": node.visible}
		for property: String in ["source_rect", "source_anchor", "source_size", "texture_scale", "rectangle", "hit_rect", "glyph_scale", "text", "override_text", "ink_color", "wrap_ceiling", "line_pitch", "paragraph_gap", "paragraphs", "override_paragraphs"]:
			if node.get(property) != null: state[property] = node.get(property)
		result[str(view.get_path_to(node))] = state
	return result

func _visual_state(view: Page) -> Dictionary:
	var result: Dictionary = _geometry(view)
	result.facts = view.view_snapshot()
	for node: Control in view.find_children("*", "Control", true, false):
		var state: Dictionary = result[str(view.get_path_to(node))]
		if node.has_method("drawing_rect"): state.draw_rect = node.drawing_rect()
		if node.has_method("displayed_paragraphs"): state.paragraphs = node.displayed_paragraphs(); state.lines = node.layout_snapshot()
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
	print("BRIEFING_SCENE_SECTION: ", section)

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
	print("BRIEFING_SCENE_CHECKS: ", JSON.stringify(report))
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
	var bytes := PackedByteArray()
	bytes.resize(4)
	bytes.encode_float(0, value)
	bytes.encode_u32(0, bytes.decode_u32(0) + direction)
	return bytes.decode_float(0)


func _authored(view: Page) -> void:
	_check(not view.is_node_ready() and not view.is_inside_tree(), "The real production scene exposes its content before Ready.")
	_check(view.get_rect() == Rect2(0, 0, 640, 480) and view.get_child_count() == 5, "Briefing has five authored production sections.")
	var index: int = 0
	for section: String in SECTIONS:
		var control: Control = view.get_node(section)
		_check(control.get_rect() == SECTIONS[section] and view.get_child(index) == control, "Original section canvas frame and order: " + section)
		index += 1
		for child: Control in control.get_children():
			_check(child.source_rect == SECTIONS[section] and child.anchor_right == 1.0 and child.anchor_bottom == 1.0,
				"Draw pass retains the source matrix and real editable anchors: " + section + "/" + str(child.name))
	_check(view.get_node("Header/Title").text == "MISSION BRIEFING" and view.get_node("Header/Panel").ink_color == Color(0, 0, 0, 0.5), "The authored header is the retained half-alpha overlay and English title.")
	var name: Control = view.get_node("LevelName/Text")
	_check(view.editor_level_name == WorldStrings.level_name(100) and view.editor_paragraphs == PackedStringArray(WorldStrings.briefing(100))
		and name.source_anchor == Vector2(178.5, 118)
		and name.glyph_scale == Vector2(0.70, 1) and not name.name_glyphs, "The real level label preserves fractional placement and the measured nonuniform Font22 scale.")
	var body: Control = view.get_node("Body/Text")
	_check(body.source_anchor == Vector2(80, 163.5) and body.wrap_ceiling == 286.0 and body.line_pitch == 16.0 and body.paragraph_gap == 10.0,
		"The authored body exposes independent source origin, width ceiling, pitch and blank-line gap.")
	_check(body.ink_color == Color(251.0 / 255.0, 221.0 / 255.0, 95.0 / 255.0)
		and body.paragraphs == PackedStringArray(_fallback()), "Body tint and all nine original fallback entries remain inspectable before play.")
	_check(not view.set_frame(_frame()).ok and view.view_snapshot().is_empty(), "A batch before asset admission cannot partially bind the scene.")
	for node: Control in view.find_children("*", "Control", true, false):
		_check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE and not node.clip_contents, "Production controls preserve host input and allow the original out-of-frame text drawing.")
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "All presentation controls work in standard Godot.")


func _assets(view: Page) -> void:
	_check(view.body_font == load("res://Scenes/Frontend/FrontendFont13.tres") and view.title_font == load("res://Scenes/Frontend/FrontendFont22.tres"), "Preview uses the same production fonts as gameplay.")
	_check(view.get_node("Background/Rock").texture == load("res://Scenes/Frontend/ConfigurationRock.tres")
		and view.get_node("Background/Ring").texture == load("res://Scenes/Frontend/ConfigurationRing.tres"), "Briefing reuses the actual Configuration background recipes by identity.")
	var textures: Array[Texture2D] = [view.get_node("Background/Rock").texture, view.get_node("Background/Ring").texture,
		view.get_node("Navigation/Forward").texture, view.body_font.page, view.title_font.page]
	for index: int in range(textures.size()):
		_check(textures[index].source_path == INPUTS[index] and textures[index].ensure_loaded().ok
			and textures[index].get_image().get_size() == textures[index].dimensions, "Private production image is read through its shared public recipe.")
	_check(view.get_node("Background/Rock").drawing_rect() == Rect2(-70, -80, 1280, 640)
		and view.get_node("Background/Ring").drawing_rect() == Rect2(-228, -274, 990, 990), "Shared stage retains exact original source quads.")
	var body: AtlasFont = view.body_font.duplicate(true)
	var title: AtlasFont = view.title_font.duplicate(true)
	_check(view.configure_assets({}, {"body_font": body, "title_font": title}).ok and view.body_font == body and view.title_font == title, "Host-supplied fonts are borrowed by exact identity.")
	_check(view.get_node("Body/Text").atlas_font == body and view.get_node("Header/Title").atlas_font == title
		and view.get_node("LevelName/Text").atlas_font == title, "Actual text drawing and wrap metrics use the supplied resources.")
	_check(view.view_snapshot() == _frame() and not view.get("_frame_supplied"), "Standalone preview uses the normal world100 name/paragraphs from the existing pure data owner.")
	var before: Dictionary = _visual_state(view)
	var missing: AtlasFont = AtlasFont.new()
	var wrong: AtlasFont = AtlasFont.new()
	wrong.page = PlaceholderTexture2D.new()
	for fonts: Dictionary in [{"body_font": missing}, {"title_font": missing}, {"body_font": Resource.new()}, {"title_font": wrong}, {"unknown": body}]:
		_check(not view.configure_assets({}, fonts).ok and _visual_state(view) == before, "Malformed font batches refuse before altering the live scene.")
	for paths: Dictionary in [{1: "route"}, {"rock": null}, {"arrow": 7}, {"unowned": "route"}]:
		_check(not view.configure_assets(paths).ok and _visual_state(view) == before, "Malformed or unowned asset routes receive an atomic refusal.")


func _facts(view: Page) -> void:
	var facts: Dictionary = _frame([PackedInt32Array([65, 0, 9, 160, 0xd800, 10, 0xdc00, 32, 66]), PackedInt32Array()])
	facts.level_name = PackedInt32Array([65, 0, 161, 0xd800, 0xdc00, 0x2019])
	facts.unowned = Resource.new()
	_check(view.set_frame(facts).ok and view.view_snapshot().size() == 2, "One display batch retains only detached raw supplied name and paragraphs.")
	_check(view.get_node("LevelName/Text").displayed_units() == facts.level_name
		and view.get_node("Body/Text").displayed_paragraphs() == facts.paragraphs, "NUL, surrogates, tab, NBSP and newline remain raw UTF-16 in actual text components.")
	var admitted: Dictionary = view.view_snapshot()
	facts.level_name[0] = 66
	facts.paragraphs[0][0] = 90
	var returned: Dictionary = view.view_snapshot()
	returned.paragraphs[0][0] = 88
	returned.level_name[0] = 67
	var body: Control = view.get_node("Body/Text")
	var displayed: Array = body.displayed_paragraphs()
	displayed[0][0] = 89
	var lines: Array = body.wrap_lines()
	lines[0][0] = 70
	var layout: Array = body.layout_snapshot()
	layout[0].units[0] = 71
	layout[0].origin = Vector2.ZERO
	_check(view.view_snapshot() == admitted and body.displayed_paragraphs() == admitted.paragraphs
		and body.wrap_lines()[0] == admitted.paragraphs[0] and body.layout_snapshot()[0].origin == Vector2(80, 163.5),
		"Incoming facts, snapshots and layout diagnostics are detached from the production view.")
	var before: Dictionary = _visual_state(view)
	for change: Dictionary in [{}, {"level_name": null}, {"level_name": "wrong carrier"}, {"level_name": PackedInt32Array([-1])},
		{"level_name": PackedInt32Array([65536])}, {"paragraphs": null}, {"paragraphs": PackedStringArray(["text"])},
		{"paragraphs": [null]}, {"paragraphs": [Resource.new()]}, {"paragraphs": ["wrong carrier"]},
		{"paragraphs": [PackedInt32Array([-1])]}, {"paragraphs": [PackedInt32Array([65536])]}]:
		var invalid: Dictionary = admitted.duplicate(true)
		if change.is_empty(): invalid.erase("paragraphs")
		else: invalid.merge(change, true)
		var refused: Dictionary = view.set_frame(invalid)
		_check(not refused.ok and refused.error_type == "InvalidDataException" and _visual_state(view) == before,
			"Malformed raw facts are refused before any label, line or source geometry changes.")


func _wrap_law(view: Page) -> void:
	var body: Control = view.get_node("Body/Text")
	_check(view.set_frame(_frame([])).ok and view.view_snapshot().paragraphs.is_empty()
		and body.displayed_paragraphs() == _units(_fallback()) and body.wrap_lines() == _units(_fallback()),
		"An empty supplied Array selects all nine existing fallback entries while stored facts remain empty.")
	var layout: Array = body.layout_snapshot()
	var ys: Array[float] = [163.5, 179.5, 195.5, 211.5, 227.5, 243.5, 259.5, 269.5, 285.5]
	for index: int in range(ys.size()):
		_check(layout[index].origin == Vector2(80, ys[index]) and layout[index].draw == (index != 6), "Fallback drawing preserves pitch16 and exactly one explicit gap10.")
	var world100: Array[PackedInt32Array] = _units(WorldStrings.briefing(100))
	_check(view.set_frame(_frame(world100)).ok, "The authored world100 paragraphs are admitted independently of the fallback.")
	var expected: Array[String] = _fallback()
	expected.remove_at(6)
	_check(body.wrap_lines() == _units(expected) and body.layout_snapshot()[6].origin.y == 259.5,
		"Two nonempty authored paragraphs wrap to eight lines without inventing the fallback's extra gap.")
	for fixture: Array in [[[""], [""]], [["", ""], ["", ""]], [[" ", "   "], []], [["First", "Second"], ["First", "Second"]],
		[["First", "", "Second"], ["First", "", "Second"]], [["  A  B  "], ["A  B  "]], [["A   B"], ["A   B"]]]:
		_check(view.set_frame(_frame(_units(fixture[0]))).ok and body.wrap_lines() == _units(fixture[1]), "Explicit blank/all-space/repeated/trailing-space fixture retains original Split behavior: " + str(fixture[0]))
	view.set_frame(_frame(_units(["First", "", "Second"])))
	_check(body.layout_snapshot()[2].origin.y == 189.5, "Only an explicit blank wrapped line adds a ten-pixel gap.")
	var raw := PackedInt32Array([65, 0, 9, 160, 0xd800, 10, 0xdc00, 32, 66])
	view.set_frame(_frame([raw]))
	_check(body.wrap_lines() == [raw], "Tab, NBSP and newline are glyphs inside a word, not extra wrapping separators.")
	var long_word: String = "W".repeat(40)
	_check(view.body_font.measure(Text.units(long_word).value) > 286.0, "The bounded long-word fixture really exceeds the production ceiling.")
	view.set_frame(_frame(_units([long_word + " A"])))
	_check(body.wrap_lines() == _units([long_word, "A"]), "An oversized word remains whole; only its following word breaks.")
	# Only this harness-owned font duplicate's transient metric cache changes.
	# No private input or recipe is written, and the real scene exercises the law.
	var widths: PackedInt32Array = view.body_font.glyph_widths()
	var boundary := PackedInt32Array()
	boundary.resize(256)
	boundary.fill(0)
	boundary[33] = 142
	view.body_font.set("_widths", boundary)
	for fixture: Array in [["A A", ["A A"]], ["A AB", ["A", "AB"]], ["A A ", ["A A"]], ["A  A", ["A ", "A"]]]:
		view.set_frame(_frame(_units([fixture[0]])))
		_check(body.wrap_lines() == _units(fixture[1]), "Width286 fits, width287 breaks, and empty space tokens retain their exact effect: " + fixture[0])
	view.body_font.set("_widths", widths)
	view.set_frame(_frame(_units(WorldStrings.briefing(110))))
	_check(body.displayed_paragraphs() == _units(WorldStrings.briefing(110)) and body.wrap_lines() != _units(_fallback()), "Existing World110 text stays its own display data without adding a gameplay route.")


func _editing(view: Page) -> void:
	view.position = Vector2(11.5, 7.25)
	view.scale = Vector2(0.9375, 1.0625)
	view.rotation = -0.03125
	var body: Control = view.get_node("Body/Text")
	var lines: Array = body.wrap_lines()
	var before: Transform2D = body.get_global_transform_with_canvas() * body.source_transform()
	view.get_node("Body").size = Vector2(353.5, 171.5)
	view.get_node("Body").position += Vector2(7.25, -9.5)
	view.get_node("Body").rotation = 0.0625
	view.get_node("Header").size = Vector2(413.7, 40)
	view.get_node("LevelName").position += Vector2(4.25, 2.5)
	view.get_node("LevelName").size = Vector2(427.35, 40)
	await process_frame
	_check(body.size == view.get_node("Body").size and body.wrap_lines() == lines and body.wrap_ceiling == 286.0,
		"Edited Body Size changes actual drawing geometry without silently changing the measured wrap ceiling or lines.")
	_check(body.get_global_transform_with_canvas() * body.source_transform() != before, "Body Position/Size/rotation affect the actual production source mapping.")
	for section: String in ["Header", "LevelName"]:
		for child: Control in view.get_node(section).get_children(): _check(child.size == view.get_node(section).size, "Edited section Size reaches its real production labels.")
	var nav: Control = view.get_node("Navigation")
	nav.position += Vector2(3.25, -5.5)
	nav.size = Vector2(654.15, 45)
	nav.rotation = -0.0625
	await process_frame
	var back: Control = view.get_node("Navigation/Back")
	var point: Vector2 = view.get_transform() * nav.get_transform() * back.get_transform() * back.source_transform() * Vector2(20, 450)
	_check(view.hit_test(point) == 1, "Authored page/navigation transforms affect actual design-space hits without a Stage roundtrip.")
	var imported: Array = body.displayed_paragraphs()
	body.paragraphs = PackedStringArray(["Enhanced paragraph", "", "Second enhanced paragraph"])
	_check(body.displayed_paragraphs() == imported, "Inspector body text needs an explicit override before replacing the faithful raw paragraphs.")
	var draws: Array[int] = [0]
	var on_draw: Callable = func() -> void: draws[0] += 1
	body.draw.connect(on_draw)
	await process_frame
	var count: int = draws[0]
	body.override_paragraphs = true
	body.source_anchor += Vector2(2.25, -1.5)
	body.line_pitch = 18.0
	await process_frame
	await process_frame
	_check(body.displayed_paragraphs() == _units(body.paragraphs) and draws[0] > count
		and body.layout_snapshot()[1].origin.y == F.value(body.source_anchor.y + 18.0), "Explicit enhanced body/source edits redraw the real layout without any timer or session frame.")
	body.draw.disconnect(on_draw)
	view.get_node("LevelName/Text").text = "Enhanced level name"
	view.get_node("LevelName/Text").override_text = true
	var geometry: Dictionary = _geometry(view)
	_check(view.set_frame(_frame()).ok and _geometry(view) == geometry and body.displayed_paragraphs() == _units(body.paragraphs), "Host batches preserve all deliberate authoring changes and explicit body/name overrides.")
	var faithful: Texture2D = view.get_node("Background/Rock").texture
	var route: String = faithful.source_path
	_check(view.configure_assets({"rock": ProjectSettings.globalize_path(route)}).ok
		and view.get_node("Background/Rock").texture != faithful and faithful.source_path == route, "An enhanced private route uses its own recipe without changing the shared faithful resource.")


func _preview(view: Page) -> void:
	var before: Dictionary = view.view_snapshot()
	view.editor_level_name = "Inspect briefing"
	_check(Engine.is_editor_hint() or view.view_snapshot() == before, "Frozen Inspector fields cannot override a live runtime display batch.")
	view.editor_paragraphs = PackedStringArray(["First frozen paragraph", "Second frozen paragraph"])
	_check(view.show_editor_preview().ok and not view.get("_frame_supplied") and view.view_snapshot().paragraphs == _units(view.editor_paragraphs), "Explicit preview admits its own harmless frozen facts.")
	view.editor_level_name = "Frozen level name"
	_check(view.view_snapshot().level_name == Text.units("Frozen level name").value and not view.get("_frame_supplied"), "Inspector changes refresh the same production view when frozen.")
	var frozen: Dictionary = _visual_state(view)
	await process_frame
	await process_frame
	_check(_visual_state(view) == frozen, "Idle engine frames change no facts, line origins or authored geometry.")


func _publication(view: Page) -> void:
	var packed := PackedScene.new()
	_check(packed.pack(view) == OK, "The actually edited production scene packs successfully.")
	var state: SceneState = packed.get_state()
	var visited: Dictionary = {}
	for node: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(node)): _stored(state.get_node_property_value(node, property), visited)
	var path: String = _output.path_join("roundtrip.tscn")
	_check(ResourceSaver.save(packed, path) == OK, "Serialization writes only the fresh owned artifact.")
	var source: String = FileAccess.get_file_as_string(path)
	_check(not source.contains("type=\"Image\"") and not source.contains("type=\"ImageTexture\"") and not source.contains("PackedByteArray("), "Published layout/recipes contain no private pixel payloads.")
	var reopened: PackedScene = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	_check(reopened != null, "The saved edited production scene reopens.")
	if reopened == null: return
	var copy: Page = reopened.instantiate()
	_check(copy.get_node("Body").get_rect() == view.get_node("Body").get_rect()
		and copy.get_node("Body").rotation == view.get_node("Body").rotation, "Body Position/Size/rotation survive before Ready.")
	_check(copy.get_node("Body/Text").override_paragraphs and copy.get_node("Body/Text").paragraphs == view.get_node("Body/Text").paragraphs
		and copy.get_node("Body/Text").line_pitch == 18.0, "Explicit enhanced body text and layout survive serialization.")
	_check(copy.get_node("LevelName/Text").override_text and copy.get_node("LevelName/Text").text == "Enhanced level name", "Enhanced name remains inspectable before playing.")
	view.get_parent().add_child(copy)
	await process_frame
	await process_frame
	_check(copy.get("_assets_configured") and copy.get("_error") == "" and not copy.get("_frame_supplied"), "Reopened production recipes admit into the same harmless frozen view.")
	_check(_visual_state(copy) == _visual_state(view), "Reopened native layout reproduces all edited quads, name, body lines and frozen facts.")
	copy.queue_free()
	copy = null
	await process_frame


static func _frame(paragraphs: Variant = null) -> Dictionary:
	return {"level_name": Text.units(WorldStrings.level_name(100)).value,
		"paragraphs": _units(WorldStrings.briefing(100)) if paragraphs == null else paragraphs.duplicate(true)}


static func _units(values: Variant) -> Array[PackedInt32Array]:
	var result: Array[PackedInt32Array] = []
	for value: String in values: result.append(Text.units(value).value)
	return result


static func _fallback() -> Array[String]:
	return ["Tatiana will take you through the", "basics of piloting Battle Engine",
		"Aquila. This will cover everything", "from basic movement in both", "Walker and Jet modes as well as", "Weapons use.", "",
		"Listen to her advice and try to", "keep Colonel Kramer happy."]
