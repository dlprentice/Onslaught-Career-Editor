# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual production Level Select in standard headless Godot. The one
## argument must be a fresh owned local-data output directory.
const Page = preload("res://Scenes/Frontend/level_select_presentation.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const WorldStrings = preload("res://Core/frontend_world_strings.gd")
const Underlay = preload("res://Scenes/Frontend/frontend_underlay.gd")
const Laws = preload("res://Client/main_menu_laws.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const REQUIRED: Array[String] = ["authored_scene", "production_assets", "display_facts", "graph_geometry", "navigation", "editing", "frozen_preview", "publication", "ownership"]
const SOURCES: Array[String] = ["res://Scenes/Frontend/LevelSelect.tscn", "res://Scenes/Frontend/level_select_presentation.gd",
	"res://Scenes/Frontend/level_select_arc.gd", "res://Scenes/Frontend/level_select_link.gd",
	"res://Scenes/Frontend/LevelSelectRing01.tres", "res://Scenes/Frontend/LevelSelectRing02.tres",
	"res://Scenes/Frontend/career_name_underlay.gd", "res://Scenes/Frontend/main_menu_underlay.gd",
	"res://Scenes/Frontend/frontend_underlay.gd", "res://Scenes/Frontend/FrontendUnderlay.tres",
	"res://Scenes/Frontend/career_name_label.gd", "res://Scenes/Frontend/career_name_bracket.gd",
	"res://Scenes/Frontend/FrontendBracket.tres", "res://Scenes/Frontend/configuration_ring.gd",
	"res://Scenes/Frontend/career_name_arrow.gd", "res://Scenes/Frontend/career_name_target.gd",
	"res://Scenes/Frontend/quit_confirm_surface.gd", "res://Scenes/Frontend/frontend_atlas_font.gd",
	"res://Scenes/Frontend/FrontendFont13.tres", "res://Scenes/Frontend/FrontendFont22.tres",
	"res://Scenes/Frontend/loading_strings.gd", "res://Scenes/Frontend/LoadingStrings.tres",
	"res://Core/frontend_world_strings.gd", "res://Scenes/Frontend/Tests/level_select_scene_checks.gd"]
const INPUTS: Array[String] = ["res://Assets/Frontend/level-bracket-01.texture.aya",
	"res://Assets/Frontend/level-ring-01.texture.aya", "res://Assets/Frontend/level-ring-02.texture.aya",
	"res://Assets/Frontend/fe-arrow.texture.aya", "res://Assets/Hud/font-13ps.texture.aya", "res://Assets/Hud/font-22.texture.aya",
	"res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb", "res://Assets/Frontend/english.json"]
const NODES: Array[Vector2] = [Vector2(148, 320), Vector2(208, 320), Vector2(268, 320), Vector2(328, 290),
	Vector2(328, 350), Vector2(388, 290), Vector2(388, 350), Vector2(448, 290), Vector2(448, 350),
	Vector2(508, 320), Vector2(568, 290), Vector2(568, 350)]
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
	var packed: PackedScene = load("res://Scenes/Frontend/LevelSelect.tscn")
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
	if _check(view.get("_assets_configured") and view.get("_error") == "", "Standalone Level Select admits the same production recipes without C#."):
		_assets(view)
		_done("production_assets")
		_facts(view)
		_done("display_facts")
		_graph_geometry(view)
		_done("graph_geometry")
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
	print("LEVEL_SELECT_SCENE_SECTION: ", section)

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
	print("LEVEL_SELECT_SCENE_CHECKS: ", JSON.stringify(report))
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
	_check(not view.is_node_ready() and not view.is_inside_tree(), "The real Level Select exposes authored controls before Ready.")
	var order: Array[String] = ["Background", "Guides", "SweepArcs", "Graph", "Columns", "Decoration", "Header", "Episode", "LevelName", "Navigation"]
	_check(view.get_rect() == Rect2(0, 0, 640, 480) and view.get_child_count() == order.size(), "The original one-frame page is a complete authored scene.")
	for index: int in range(order.size()): _check(view.get_child(index).name == order[index], "Original pass ordering: " + order[index])
	_check(view.get_node("Graph/Links").get_child_count() == 16 and view.get_node("Graph/Nodes").get_child_count() == 12
		and view.get_node("SweepArcs").get_child_count() == 3, "Graph geometry is sixteen editable links, twelve node groups and three arcs.")
	for node: Control in view.find_children("*", "Control", true, false):
		# Godot resolves full-rect anchors when entering the tree. Before Ready,
		# inspect the actual stored anchors/offsets; verify resolved geometry below.
		_check(node.anchor_right == 1.0 and node.anchor_bottom == 1.0 and _offsets(node) == Vector4.ZERO, "Every pass authors the original full-stage canvas frame: " + str(node.name))
		if node.get("source_rect") != null: _check(node.source_rect == Rect2(0, 0, 640, 480), "Original full-stage source matrix: " + str(node.name))
		_check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE and not node.clip_contents, "Native editor controls leave input to the host and do not clip source art.")
		_check(node.get_script() == null or node.get_script().resource_path.ends_with(".gd"), "All production content opens in standard Godot.")
	for index: int in range(12):
		var outer: Control = view.get_node("Graph/Nodes/Node%02d/Outer" % index)
		_check(outer.source_anchor == NODES[index] and outer.source_size == Vector2.ONE * (80 if index == 0 else 61), "Authored node centers and independent ring sizes retain the measured map.")
	_check(view.get_node("Graph/Nodes").get_child(11).name == "Node00"
		and view.get_node("Graph/Nodes/Node00").get_child(0).name == "Outer"
		and view.get_node("Graph/Nodes/Node00").get_child(1).name == "Inner", "Current outer/inner rings render after all eleven dim rings.")
	_check(view.get_node("Guides/Vertical").rectangle == Rect2(123, 0, 1, 480)
		and view.get_node("Guides/Horizontal").rectangle == Rect2(0, 180, 640, 1), "Crosshair guides remain actual editable production passes.")
	_check(view.get_node("Header/Panel").rectangle == Rect2(191, 69, 394, 21)
		and view.get_node("Header/Panel").ink_color == Color(12.0 / 255.0, 12.0 / 255.0, 24.0 / 255.0), "Level Select keeps its measured opaque header composite.")
	_check(view.get_node("Header/Title").centered and view.get_node("Header/Title").source_anchor == Vector2(390, 65)
		and view.get_node("Header/Title").glyph_scale == Vector2.ONE, "Title preserves the corrected centered Font22 scale 1 law.")
	_check(view.get_node("Episode").text == "Episode 1" and view.get_node("Episode").ink_color == Color.WHITE
		and view.get_node("Episode").source_anchor == Vector2(130, 130.2), "The single capture-transcribed episode literal retains its white tint and fractional origin.")
	_check(view.get_node("LevelName").source_anchor == Vector2(130, 156.8)
		and view.get_node("LevelName").ink_color == Laws.retail_color(0xfdff6f3f), "Selected-name placement and measured tint remain inspectable.")
	_check(view.get_node("Decoration/Body").texture_scale == Vector2(1.25, 1.25)
		and view.get_node("Decoration/Shadow").shadow_scale_boost == 1.05, "Level Select retains its own settled bracket scale 1.25 and shadow multiplier.")
	_check(not view.set_frame(_frame()).ok and view.view_snapshot().is_empty(), "A frame cannot partially bind before asset admission.")


func _assets(view: Page) -> void:
	for node: Control in view.find_children("*", "Control", true, false):
		_check(node.get_rect() == Rect2(0, 0, 640, 480), "Authored anchors resolve to the actual full-stage production canvas frame: " + str(node.name))
	_check(view.body_font == load("res://Scenes/Frontend/FrontendFont13.tres")
		and view.title_font == load("res://Scenes/Frontend/FrontendFont22.tres"), "Preview uses the shared production fonts.")
	var textures: Array[Texture2D] = [view.get_node("Decoration/Body").texture, view.get_node("Graph/Nodes/Node00/Outer").texture,
		view.get_node("Graph/Nodes/Node00/Inner").texture, view.get_node("Navigation/Forward").texture, view.body_font.page, view.title_font.page]
	for index: int in range(textures.size()):
		_check(textures[index].source_path == INPUTS[index] and textures[index].ensure_loaded().ok
			and textures[index].get_image().get_size() == textures[index].dimensions, "Each real private page loads read-only through a public production recipe.")
	_check(textures[0] == load("res://Scenes/Frontend/FrontendBracket.tres")
		and textures[1] == load("res://Scenes/Frontend/LevelSelectRing01.tres")
		and textures[2] == load("res://Scenes/Frontend/LevelSelectRing02.tres"), "Bracket and both ring recipes are the actual shared resources.")
	_check(textures[1].dimensions == Vector2i(64, 64) and textures[1].compression == 1
		and textures[2].dimensions == Vector2i(64, 64) and textures[2].compression == 1, "Both graph rings use their actual 64-square DXT2 payloads.")
	var body: AtlasFont = view.body_font.duplicate(true)
	var title: AtlasFont = view.title_font.duplicate(true)
	var frames: Array = view.get_node("Background").get("_frames").slice(0, 5)
	_check(frames.size() == 5, "The materialized FEBack strip supplies real shared frames.")
	var title_units := PackedInt32Array([65, 0, 0xd800, 0xdc00, 161])
	_check(view.configure_assets({}, {"body_font": body, "title_font": title}, frames, title_units).ok
		and view.body_font == body and view.title_font == title, "Host font recipes and raw admitted title are borrowed without a second owner.")
	_check(view.get_node("Background").get("_frames")[0] == frames[0]
		and view.get_node("Header/Title").displayed_units() == title_units, "Actual drawing shares the host image identity and preserves raw title units.")
	title_units[0] = 90
	_check(view.get_node("Header/Title").displayed_units()[0] == 65, "The title batch is detached from its caller.")
	for path: String in ["Episode", "LevelName", "Columns/One", "Columns/Two", "Columns/Three"]:
		_check(view.get_node(path).atlas_font == body, "Ordinary atlas text shares the admitted body font.")
	_check(view.get_node("Header/Title").atlas_font == title, "The header uses the admitted Font22.")
	for index: int in range(12): _check(view.get_node("Graph/Nodes/Node%02d/Outer" % index).texture == textures[1], "All twelve outer rings borrow the same recipe.")
	_check(view.view_snapshot() == _frame() and not view.get("_frame_supplied"), "Standalone preview uses the normal World100 name with frozen background time.")
	var before: Dictionary = _visual_state(view)
	var missing: AtlasFont = AtlasFont.new()
	var wrong: AtlasFont = AtlasFont.new()
	wrong.page = PlaceholderTexture2D.new()
	for fonts: Dictionary in [{"body_font": missing}, {"title_font": missing}, {"title_font": wrong}, {"body_font": Resource.new()}, {"unowned": body}]:
		_check(not view.configure_assets({}, fonts, frames).ok and _visual_state(view) == before, "Malformed shared fonts refuse before any live content changes.")
	for paths: Dictionary in [{1: "route"}, {"ring_outer": 7}, {"arrow": null}, {"unknown": "route"}]:
		_check(not view.configure_assets(paths, {}, frames).ok and _visual_state(view) == before, "Malformed or unowned asset routes are refused atomically.")
	for invalid: Variant in ["wrong carrier", [], PackedInt32Array(), PackedInt32Array([-1]), PackedInt32Array([65536]), Resource.new()]:
		_check(not view.configure_assets({}, {}, frames, invalid).ok and _visual_state(view) == before, "Invalid host titles leave all admitted content untouched.")
	_check(not view.configure_assets({}, {}, [Resource.new()]).ok and _visual_state(view) == before, "A non-texture background batch is refused atomically.")
	_check(view.configure_assets().ok and view.get_node("Header/Title").displayed_units() == Text.units("SELECT LEVEL").value,
		"Standalone admission reads the pinned real localization receipt and restores the full production strip.")


func _facts(view: Page) -> void:
	var facts: Dictionary = _frame()
	facts.level_name = PackedInt32Array([65, 0, 161, 0xd800, 0xdc00, 0x2019])
	facts.background_seconds = 0.25
	facts.unowned = Resource.new()
	_check(view.set_frame(facts).ok and view.view_snapshot().size() == 2
		and view.get_node("LevelName").displayed_units() == facts.level_name, "Only the two admitted raw name/time facts enter the presentation.")
	var admitted: Dictionary = view.view_snapshot()
	facts.level_name[0] = 90
	var returned: Dictionary = view.view_snapshot()
	returned.level_name[0] = 91
	var displayed: PackedInt32Array = view.get_node("LevelName").displayed_units()
	displayed[0] = 92
	_check(view.view_snapshot() == admitted and view.get_node("LevelName").displayed_units() == admitted.level_name, "Incoming and returned raw text snapshots are detached.")
	var before: Dictionary = _visual_state(view)
	for change: Dictionary in [{}, {"level_name": null}, {"level_name": "text"}, {"level_name": []},
		{"level_name": PackedInt32Array([-1])}, {"level_name": PackedInt32Array([65536])},
		{"background_seconds": 0}, {"background_seconds": null}, {"background_seconds": NAN}, {"background_seconds": INF}, {"background_seconds": -INF}]:
		var invalid: Dictionary = admitted.duplicate(true)
		if change.is_empty(): invalid.erase("level_name")
		else: invalid.merge(change, true)
		var refused: Dictionary = view.set_frame(invalid)
		_check(not refused.ok and refused.error_type == "InvalidDataException" and _visual_state(view) == before, "Invalid raw facts cannot partially mutate name, background phase or authored geometry.")
	var graph: Dictionary = _graph_state(view)
	var world110: Dictionary = _frame()
	world110.level_name = Text.units(WorldStrings.level_name(110)).value
	_check(view.set_frame(world110).ok and view.get_node("LevelName").displayed_units() == world110.level_name
		and _graph_state(view) == graph, "World110 name changes leave the original fixed Node00 highlight and graph unchanged.")
	for seconds: float in [0.0, 0.1, 0.25, 1.0, 19.125, -1.0]:
		world110.background_seconds = seconds
		view.set_frame(world110)
		var background: Dictionary = view.get_node("Background").view_snapshot()
		_check(background.alpha == 1.0 and background.frame == Underlay.frame_index(seconds, background.frame_count)
			and _graph_state(view) == graph, "Only host-supplied FEBack time advances; graph/arc/bracket geometry does not animate.")
	var empty: Dictionary = _frame()
	empty.level_name = PackedInt32Array()
	_check(view.set_frame(empty).ok and view.get_node("LevelName").displayed_units().is_empty(), "An empty selected-name string stays empty.")


func _graph_geometry(view: Page) -> void:
	var graph: Dictionary = view.graph_snapshot()
	_check(graph.arcs.size() == 3 and graph.links.size() == 16 and graph.rings.size() == 13, "Diagnostics describe actual ordered arc/line/ring submissions.")
	for index: int in range(3):
		var arc: Dictionary = graph.arcs[index]
		var offset: float = [0.0, 120.0, 360.0][index]
		_check(arc.center == Vector2(F.value(F.value(365.84) + offset), 320.38)
			and arc.radius == F.value(249.28) and arc.start == F.value(2.5423) and arc.end == F.value(3.7253)
			and arc.points == 96 and arc.width == F.value(1.6) and arc.antialiased, "The arc keeps original binary32 constants, addition order and tessellation.")
	_check(graph.links[0].from == Vector2(175, 320) and graph.links[0].to == Vector2(187, 320)
		and graph.links[1].from == Vector2(229, 320) and graph.links[1].to == Vector2(247, 320), "Horizontal links stop at the measured 27/21 outer radii without crossing empty ring centers.")
	for link: Dictionary in graph.links:
		_check(link.width == F.value(1.6) and link.antialiased and link.ink == Color(49.0 / 255.0, 50.0 / 255.0, 71.0 / 255.0), "Every actual segment retains its measured color, width and antialiasing.")
	for index: int in range(11):
		_check(graph.rings[index].rectangle == Rect2(NODES[index + 1] - Vector2(30.5, 30.5), Vector2(61, 61))
			and graph.rings[index].ink == Laws.retail_color(0x1cffffff), "Dim rings keep ordered measured centers, scale division and tint.")
	_check(graph.rings[11].rectangle == Rect2(108, 280, 80, 80) and graph.rings[12].rectangle == Rect2(117, 289, 62, 62)
		and graph.rings[11].ink == Laws.retail_color(0xfe7f7f7f) and graph.rings[12].ink == graph.rings[11].ink, "Current outer and inner ring rectangles retain original ordering and tint.")
	_check(view.get_node("Decoration/Body").drawing_rect() == Rect2(8, 23, 640, 640)
		and view.get_node("Decoration/Shadow").drawing_rect() == Rect2(-3, 17, 672, 672), "Bracket and shadow retain original multiply-before-centering operation order.")
	graph.arcs[0].center = Vector2.ZERO
	graph.links[0].from = Vector2.ZERO
	graph.rings[0].rectangle = Rect2()
	_check(view.graph_snapshot().arcs[0].center != Vector2.ZERO and view.graph_snapshot().links[0].from == Vector2(175, 320)
		and view.graph_snapshot().rings[0].rectangle.size == Vector2(61, 61), "Graph diagnostics detach their geometry dictionaries; texture resources are intentionally shared.")


func _navigation(view: Page, stage: Node2D) -> void:
	var cases: Array[Array] = [[Vector2(0, 430), 1], [Vector2(47.5, 477.5), 1], [Vector2(48, 450), 0], [Vector2(20, 478), 0],
		[Vector2(595, 430), 2], [Vector2(639.5, 477.5), 2], [Vector2(640, 450), 0], [Vector2(600, 478), 0],
		[Vector2(120, 265), 3], [Vector2(179.5, 324.5), 3], [Vector2(180, 300), 4], [Vector2(150, 325), 0],
		[Vector2(180, 265), 4], [Vector2(239.5, 324.5), 4], [Vector2(240, 300), 0], [Vector2(210, 325), 0],
		[Vector2(268, 320), 0], [Vector2(148, 340), 0]]
	for edge: Array in [[120.0, 300.0, true, [0, 3, 3]], [180.0, 300.0, true, [3, 4, 4]], [240.0, 300.0, true, [4, 0, 0]],
		[265.0, 150.0, false, [0, 3, 3]], [325.0, 150.0, false, [3, 0, 0]],
		[265.0, 210.0, false, [0, 4, 4]], [325.0, 210.0, false, [4, 0, 0]],
		[48.0, 450.0, true, [1, 0, 0]], [595.0, 450.0, true, [0, 2, 2]], [640.0, 450.0, true, [2, 0, 0]]]:
		for neighbor: int in [-1, 0, 1]:
			var value: float = _next_float(edge[0], neighbor)
			cases.append([Vector2(value, edge[1]) if edge[2] else Vector2(edge[1], value), edge[3][neighbor + 1]])
	for external_scale: Vector2 in [Vector2.ONE, Vector2(1.6, 1.6), Vector2(1.5003125, 1.5003125), Vector2(0.975, 1.333)]:
		stage.scale = external_scale
		stage.position = Vector2(37.25, -19.125)
		for pair: Array in cases: _check(view.hit_test(pair[0]) == pair[1], "Original half-open/nextafter targets consume design points without external Stage rounding: " + str(pair[0]))
	stage.scale = Vector2.ONE
	stage.position = Vector2.ZERO
	view.get_node("Navigation/Back").position = Vector2(120, -160)
	_check(view.hit_test(Vector2(140, 300)) == 1, "Authored overlapping navigation preserves original Back priority over node targets.")
	view.get_node("Navigation/Back").position = Vector2.ZERO


func _editing(view: Page) -> void:
	var original: Dictionary = _graph_state(view)
	view.position = Vector2(11.5, 7.25)
	view.scale = Vector2(0.9375, 1.0625)
	view.rotation = -0.03125
	view.size = Vector2(800.2, 540.6)
	await process_frame
	_check(_graph_state(view) == original, "A fractional page Size changes the drawing source matrix without rounding or changing authored source endpoints.")
	var node: Control = view.get_node("Graph/Nodes/Node01")
	var ring: Control = node.get_node("Outer")
	var link: Control = view.get_node("Graph/Links/Link00")
	var sibling: Control = view.get_node("Graph/Links/Link01")
	var sibling_rect: Rect2 = sibling.get_rect()
	var previous: Dictionary = link.drawing_parameters()
	node.position += Vector2(12.25, -7.5)
	node.size *= Vector2(1.1, 0.9)
	node.rotation = 0.015625
	await process_frame
	_check(link.drawing_parameters() != previous and ring.size == node.size, "Editing a real node group's Position/Size/rotation moves its ring and linked endpoints.")
	var target: Control = node.get_node("Target")
	var point: Vector2 = view.get_transform() * view.get_node("Graph").get_transform() * view.get_node("Graph/Nodes").get_transform() * node.get_transform() * target.get_transform() * target.source_transform() * Vector2(210, 295)
	_check(view.hit_test(point) == 4, "The same authored node group moves its offset click region with the visible ring.")
	var draws: Array[int] = [0]
	var on_draw: Callable = func() -> void: draws[0] += 1
	link.draw.connect(on_draw)
	await process_frame
	var count: int = draws[0]
	previous = link.drawing_parameters()
	ring.source_anchor += Vector2(3.5, -2.25)
	await process_frame
	await process_frame
	await process_frame
	_check(draws[0] > count and link.drawing_parameters() != previous, "Changing a frozen ring's source anchor redraws its real connected line without a new host frame.")
	link.draw.disconnect(on_draw)
	var before: Transform2D = link.get_global_transform_with_canvas() * link.source_transform()
	link.position += Vector2(4.5, 2.25)
	link.size *= Vector2(0.9, 1.1)
	_check(link.get_global_transform_with_canvas() * link.source_transform() != before and sibling.get_rect() == sibling_rect,
		"Independent link Position/Size overrides affect actual drawing and leave sibling authored geometry intact.")
	var arc: Control = view.get_node("SweepArcs/Current")
	arc.source_center += Vector2(5.25, -3.5)
	arc.radius = 240.25
	arc.stroke_width = 2.5
	_check(arc.drawing_parameters().radius == 240.25 and arc.drawing_parameters().width == 2.5, "Arc Inspector values feed actual drawing parameters.")
	view.get_node("Header").position += Vector2(4.25, -3.5)
	view.get_node("Header").size *= Vector2(1.025, 1.1)
	var label: Control = view.get_node("LevelName")
	var imported: PackedInt32Array = label.displayed_units()
	label.text = "Enhanced level name"
	_check(label.displayed_units() == imported, "Inspector text does not silently replace imported name facts.")
	label.override_text = true
	view.get_node("Header/Title").text = "Enhanced level header"
	view.get_node("Header/Title").override_text = true
	var geometry: Dictionary = _geometry(view)
	_check(view.set_frame(_frame()).ok and _geometry(view) == geometry and label.displayed_units() == Text.units(label.text).value,
		"Host batches preserve authored graph/layout geometry and explicit enhanced text overrides.")
	var faithful: Texture2D = ring.texture
	var route: String = faithful.source_path
	_check(view.configure_assets({"ring_outer": ProjectSettings.globalize_path(route)}).ok
		and ring.texture != faithful and faithful.source_path == route, "An enhanced private route duplicates only its safe recipe; the faithful shared route remains unchanged.")


func _preview(view: Page) -> void:
	var before: Dictionary = view.view_snapshot()
	view.editor_level_name = "Inspect Level Select"
	_check(Engine.is_editor_hint() or view.view_snapshot() == before, "Frozen Inspector fields cannot replace a live runtime batch.")
	view.editor_background_seconds = 0.25
	_check(view.show_editor_preview().ok and not view.get("_frame_supplied")
		and view.view_snapshot().background_seconds == 0.25, "Explicit preview supplies frozen display facts without a session or clock.")
	view.editor_level_name = "Frozen level name"
	_check(view.view_snapshot().level_name == Text.units(view.editor_level_name).value and not view.get("_frame_supplied"), "Inspector fields refresh the same production view when frozen.")
	var frozen: Dictionary = _visual_state(view)
	await process_frame
	await process_frame
	_check(_visual_state(view) == frozen, "Idle frames change no facts, graph geometry, or FEBack phase.")


func _publication(view: Page) -> void:
	var packed := PackedScene.new()
	_check(packed.pack(view) == OK, "The actually edited Level Select scene packs successfully.")
	var state: SceneState = packed.get_state()
	var visited: Dictionary = {}
	for node: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(node)): _stored(state.get_node_property_value(node, property), visited)
	var path: String = _output.path_join("roundtrip.tscn")
	_check(ResourceSaver.save(packed, path) == OK, "Serialization writes only the fresh owned artifact.")
	var source: String = FileAccess.get_file_as_string(path)
	_check(not source.contains("type=\"Image\"") and not source.contains("type=\"ImageTexture\"") and not source.contains("PackedByteArray("), "Saved production layout and recipes contain no decoded private pixels or strip bytes.")
	var reopened: PackedScene = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	_check(reopened != null, "The saved edited Level Select reopens.")
	if reopened == null: return
	var copy: Page = reopened.instantiate()
	_check(_offsets(copy.get_node("Graph/Nodes/Node01")) == _offsets(view.get_node("Graph/Nodes/Node01"))
		and copy.get_node("Graph/Nodes/Node01").rotation == view.get_node("Graph/Nodes/Node01").rotation, "Edited node Position/Size/rotation survive before Ready.")
	_check(_offsets(copy.get_node("Graph/Links/Link00")) == _offsets(view.get_node("Graph/Links/Link00"))
		and copy.get_node("SweepArcs/Current").radius == 240.25, "Independent line layout and arc source edits survive before Ready.")
	_check(copy.get_node("LevelName").override_text and copy.get_node("LevelName").text == "Enhanced level name", "Explicit enhanced text remains inspectable before play.")
	view.get_parent().add_child(copy)
	await process_frame
	await process_frame
	_check(copy.get("_assets_configured") and copy.get("_error") == "" and not copy.get("_frame_supplied"), "Reopened resources use the same harmless frozen production view.")
	_check(_visual_state(copy) == _visual_state(view), "Reopened layout reproduces edited graph/source geometry, hit targets, names, routes and frozen phase.")
	copy.queue_free()
	copy = null
	await process_frame


func _geometry(view: Page) -> Dictionary:
	var result: Dictionary = {"page_transform": view.get_transform(), "page_size": view.size}
	for node: Control in view.find_children("*", "Control", true, false):
		var state: Dictionary = {"transform": node.get_transform(), "size": node.size, "visible": node.visible}
		for property: String in ["source_rect", "source_anchor", "source_size", "texture_scale", "rectangle", "hit_rect", "glyph_scale", "text", "override_text", "ink_color",
			"source_center", "radius", "start_angle", "end_angle", "point_count", "stroke_width", "antialiased", "graph", "from_node", "to_node", "from_radius", "to_radius"]:
			if node.get(property) != null: state[property] = node.get(property)
		result[str(view.get_path_to(node))] = state
	return result


func _graph_state(view: Page) -> Dictionary:
	var graph: Dictionary = view.graph_snapshot()
	for ring: Dictionary in graph.rings: ring.erase("texture")
	return graph


func _visual_state(view: Page) -> Dictionary:
	var result: Dictionary = _geometry(view)
	result.facts = view.view_snapshot()
	result.graph = _graph_state(view)
	result.background = view.get_node("Background").view_snapshot()
	for node: Control in view.find_children("*", "Control", true, false):
		var state: Dictionary = result[str(view.get_path_to(node))]
		if node.has_method("drawing_rect"): state.draw_rect = node.drawing_rect()
		if node.has_method("displayed_units"): state.units = node.displayed_units(); state.origin = node.drawing_origin(); state.ink = node.drawing_color()
		if node.get("texture") != null and node.texture.get("source_path") != null: state.texture_route = node.texture.source_path
	return result


static func _frame() -> Dictionary:
	return {"level_name": Text.units(WorldStrings.level_name(100)).value, "background_seconds": 0.0}


static func _offsets(control: Control) -> Vector4:
	return Vector4(control.get_offset(SIDE_LEFT), control.get_offset(SIDE_TOP), control.get_offset(SIDE_RIGHT), control.get_offset(SIDE_BOTTOM))
