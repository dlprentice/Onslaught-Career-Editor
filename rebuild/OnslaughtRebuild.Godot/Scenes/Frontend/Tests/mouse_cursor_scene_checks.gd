# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Actual native cursor checks in standard headless Godot only. Sole argument:
## fresh owned local-data directory; production assets remain read-only.
const Page = preload("res://Scenes/Frontend/mouse_cursor_presentation.gd")
const Quad = preload("res://Scenes/Frontend/mouse_cursor_quad.gd")
const Session = preload("res://Client/frontend_session.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const REQUIRED: Array[String] = ["authored_scene", "lazy_assets", "display_facts", "missing_retry", "live_source", "editing", "publication", "ownership"]
const SOURCES: Array[String] = ["res://Scenes/Frontend/MouseCursor.tscn", "res://Scenes/Frontend/MouseCursorTexture.tres",
	"res://Scenes/Frontend/mouse_cursor_presentation.gd", "res://Scenes/Frontend/mouse_cursor_quad.gd",
	"res://Scenes/Frontend/mouse_cursor_texture.gd", "res://Scenes/Frontend/quit_confirm_surface.gd",
	"res://Scenes/Shared/retail_texture_page.gd", "res://Scenes/Shared/retail_aya_texture.gd",
	"res://Client/frontend_session.gd", "res://Scenes/Frontend/Tests/mouse_cursor_scene_checks.gd"]
const INPUTS: Array[String] = ["res://Assets/Frontend/mouse-cursor.texture.aya"]
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
	for name: String in ["report.json", "roundtrip.tscn", "late-cursor.texture.aya"]:
		if directory.is_link(name) or FileAccess.file_exists(_output.path_join(name)) or DirAccess.dir_exists_absolute(_output.path_join(name)): quit(2); return
	create_timer(70).timeout.connect(func() -> void:
		if not _finished: _failures.append("Harness timeout before completion."); _finish())
	for path: String in SOURCES: _source_hashes[path] = FileAccess.get_sha256(path)
	for path: String in INPUTS: _input_hashes[path] = FileAccess.get_sha256(path)
	var pointer: int = Input.mouse_mode
	var packed: PackedScene = load("res://Scenes/Frontend/MouseCursor.tscn")
	var view: Page = packed.instantiate()
	_authored(view)
	_done("authored_scene")
	var viewport := SubViewport.new()
	viewport.size = Vector2i(1024, 768)
	viewport.disable_3d = true
	root.add_child(viewport)
	var stage := Node2D.new()
	stage.z_index = 100
	viewport.add_child(stage)
	_check(view.configure_assets().ok and view.set_frame(_frame(Session.Screen.LOADING)).ok, "Host may configure a hidden screen before Ready without loading the texture.")
	stage.add_child(view)
	await process_frame
	await process_frame
	await _assets(view)
	_done("lazy_assets")
	_facts(view)
	_done("display_facts")
	await _missing_retry(view)
	_done("missing_retry")
	await _live_source(view, viewport)
	_done("live_source")
	await _editing(view, stage)
	_done("editing")
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
	print("MOUSE_CURSOR_SCENE_SECTION: ", section)

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
	print("MOUSE_CURSOR_SCENE_CHECKS: ", JSON.stringify(report))
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
	var quad: Control = view.get_node("Quad")
	_check(not view.is_inside_tree() and not view.is_node_ready() and view.get_child_count() == 1, "Reusable cursor has a real authored Quad before Ready.")
	_check(view.get_rect() == Rect2(0, 0, 640, 480) and view.z_index == 2 and view.z_as_relative, "Cursor authors the full stage frame and last-draw relative Z layer.")
	_check(quad.quad_size == Vector2(32, 32) and quad.region == Rect2(0, 0, 124, 124)
		and quad.source_offset == Vector2.ZERO and quad.ink_color == Color.WHITE, "Measured quad, UV extent, zero hotspot and plain-white modulation are inspectable.")
	_check(quad.source_rect == Rect2(0, 0, 640, 480) and quad.anchor_right == 1.0 and quad.anchor_bottom == 1.0,
		"Actual drawing keeps the full-stage source frame and normal editable anchors.")
	_check(quad.texture.get("_decoded") == null and not quad.texture.get("_attempted"), "Loading the scene/recipe does not decode a cursor image.")
	_check(view.editor_screen == Session.Screen.CLICK_TO_START and view.editor_cursor_position == Vector2.ZERO,
		"Frozen standalone defaults use the measured unmoved ClickToStart position.")
	_check(not view.set_frame(_frame()).ok and not view.configure_live_pointer(null).ok, "Unconfigured asset/live-pointer calls refuse without side effects.")
	for node: Control in [view, quad]:
		_check(node.mouse_filter == Control.MOUSE_FILTER_IGNORE and not node.clip_contents, "Cursor content cannot consume host input or clip its out-of-bounds quad.")
		_check(node.get_script().resource_path.ends_with(".gd"), "The actual cursor opens in standard Godot.")


func _assets(view: Page) -> void:
	var quad: Control = view.get_node("Quad")
	var texture: Texture2D = quad.texture
	_check(texture == load("res://Scenes/Frontend/MouseCursorTexture.tres")
		and texture.source_path == INPUTS[0] and texture.dimensions == Vector2i(128, 128) and texture.compression == 1,
		"The production cursor uses its shared 128-square DXT2 recipe.")
	_check(texture.get("_decoded") == null and not texture.get("_attempted") and not quad.draws_content(), "Loading/hidden frames neither draw nor decode the optional sprite.")
	view.set_frame(_frame(Session.Screen.MAIN_MENU, Vector2(618, 450)))
	_check(texture.get("_decoded") == null and not texture.get("_attempted"), "set_frame only queues drawing; asset admission remains lazy.")
	await process_frame
	await process_frame
	_check(texture.get("_decoded") != null and texture.get("_attempted"), "The first eligible draw loads the actual curated page.")
	var image: Image = texture.get_image()
	_check(image.get_size() == Vector2i(128, 128) and image.get_format() == Image.FORMAT_RGBA8
		and image.get_mipmap_count() == 7, "All eight DDS levels survive the required RGBA8 upload conversion.")
	_check(FileAccess.get_sha256(INPUTS[0]) == "366021def699de220ad018c40250eefaccaab356c6c5d93fe0aa1b7f5302354c", "The selected materialized AYA matches the measured cursor specimen identity.")
	_check(quad.drawing_rect() == Rect2(618, 450, 32, 32), "The posted stage point is an unclamped top-left; the quad may extend beyond640x480.")
	var decoded: Texture2D = texture.get("_decoded")
	view.set_frame(_frame(Session.Screen.MAIN_MENU, Vector2(320.125, 240.25)))
	await process_frame
	await process_frame
	_check(texture.get("_decoded") == decoded, "Later frames retain one decoded production image.")
	var before: Dictionary = _state(view)
	for paths: Dictionary in [{1: "route"}, {"cursor": null}, {"cursor": 1}, {"unknown": "route"}]:
		_check(not view.configure_assets(paths).ok and _state(view) == before, "Malformed/unowned route batches refuse without replacing the admitted cursor.")


func _facts(view: Page) -> void:
	var quad: Control = view.get_node("Quad")
	for screen: int in range(12):
		var expected: bool = screen < 9
		_check(Page.accepts_screen(screen) == expected and view.set_frame(_frame(screen)).ok
			and quad.draws_content() == expected and quad.visible == expected, "Exact interactive versus Loading/IntroCutscene/Gameplay exclusion law: " + str(screen))
	for screen: int in [-2147483648, -1, 12, 2147483647]:
		_check(Page.accepts_screen(screen) and view.set_frame(_frame(screen)).ok and quad.draws_content(), "Unknown signed enum values retain the original exclusion predicate.")
	var facts: Dictionary = _frame(Session.Screen.MAIN_MENU, Vector2(-100.25, 900.5))
	facts.unowned = Resource.new()
	_check(view.set_frame(facts).ok and view.view_snapshot().size() == 2 and quad.drawing_rect().position == facts.cursor_position,
		"Only screen and stage position survive; negative and out-of-client positions stay unclamped.")
	var admitted: Dictionary = view.view_snapshot()
	facts.cursor_position = Vector2.ZERO
	var returned: Dictionary = view.view_snapshot()
	returned.screen = 9
	_check(view.view_snapshot() == admitted, "Caller and returned fact dictionaries cannot mutate displayed facts.")
	var before: Dictionary = _state(view)
	for change: Dictionary in [{}, {"screen": true}, {"screen": 1.0}, {"screen": 2147483648}, {"cursor_position": Vector2i.ZERO}, {"cursor_position": []}, {"cursor_position": null}]:
		var invalid: Dictionary = admitted.duplicate(true)
		if change.is_empty(): invalid.erase("cursor_position")
		else: invalid.merge(change, true)
		_check(not view.set_frame(invalid).ok and _state(view) == before, "Invalid facts or unconfigured live mode refuse atomically.")


func _missing_retry(view: Page) -> void:
	var quad: Control = view.get_node("Quad")
	var faithful: Texture2D = quad.texture
	var path: String = _output.path_join("late-cursor.texture.aya")
	_check(view.configure_assets({"cursor": path}).ok and quad.texture != faithful and faithful.source_path == INPUTS[0],
		"An owned alternate route changes only its public recipe and does not preload it.")
	view.set_frame(_frame(Session.Screen.MAIN_MENU))
	await process_frame
	await process_frame
	_check(quad.texture.get("_decoded") == null and not quad.texture.get("_attempted") and not quad.draw_snapshot().drawn,
		"A missing optional page leaves no negative decode cache and emits no error or placeholder.")
	var directory := DirAccess.open(_output)
	_check(directory.create_link(ProjectSettings.globalize_path(INPUTS[0]), "late-cursor.texture.aya") == OK,
		"Late arrival is simulated by an owned link to the unchanged production input, without copying retail bytes.")
	view.set_frame(_frame(Session.Screen.MAIN_MENU, Vector2(25, 50)))
	await process_frame
	await process_frame
	_check(quad.texture.get("_decoded") != null and quad.draw_snapshot().drawn and quad.draw_snapshot().position == Vector2(25, 50),
		"A later eligible draw retries and loads the newly available page.")
	var decoded: Texture2D = quad.texture.get("_decoded")
	_check(directory.remove("late-cursor.texture.aya") == OK, "Only the harness-owned retry link is removed; the source stays present.")
	quad.queue_redraw()
	await process_frame
	await process_frame
	_check(quad.texture.get("_decoded") == decoded and quad.draw_snapshot().drawn, "An already loaded cursor remains cached even if its route later disappears.")
	_check(view.configure_assets({"cursor": INPUTS[0]}).ok, "The production route is restored for subsequent editor/publication checks.")


func _live_source(view: Page, viewport: SubViewport) -> void:
	var fit: Transform2D = Quad.stage_fit(Vector2(801, 601))
	_check(fit.x == Vector2(1.251562476158142, 0) and fit.y == Vector2(0, 1.251562476158142) and fit.origin == Vector2(0, 0.125), "Fractional viewport fit preserves the unsnapped draw offset.")
	var source := Control.new()
	source.size = Vector2(801, 601)
	source.position = Vector2(17.25, -8.5)
	source.mouse_filter = Control.MOUSE_FILTER_IGNORE
	viewport.add_child(source)
	var quad: Control = view.get_node("Quad")
	_check(view.configure_live_pointer(source).ok and not source.is_processing_input() and not source.is_processing_unhandled_input(),
		"Runtime host opt-in borrows the source without changing input ownership.")
	_check(view.set_frame(_frame(Session.Screen.MAIN_MENU, null)).ok, "Only explicit runtime source configuration admits live null position.")
	await process_frame
	await process_frame
	var expected: Vector2 = Quad.to_design_position(source.get_local_mouse_position(), source.size)
	_check(quad.draw_snapshot().drawn and quad.draw_snapshot().live and quad.draw_snapshot().position == expected,
		"The actual headless draw samples its owned source and applies the retained design conversion.")
	for fixture: Array in [[Vector2(1024, 768), Vector2(832, 400), Vector2(520, 250)],
		[Vector2(801, 601), Vector2(520, 250), Vector2(415.48065185546875, 199.6504364013672)],
		[Vector2(960, 600), Vector2(800.125, 550.25), Vector2(576.0999755859375, 440.20001220703125)],
		[Vector2.ZERO, Vector2(123, 456), Vector2.ZERO]]:
		_check(Quad.to_design_position(fixture[1], fixture[0]) == fixture[2], "Original explicit binary32 design-position fixture: " + str(fixture[0]))
	view.set_frame(_frame(Session.Screen.MAIN_MENU, Vector2(33.25, 44.5)))
	await process_frame
	await process_frame
	_check(not quad.draw_snapshot().live and quad.draw_snapshot().position == Vector2(33.25, 44.5), "Deterministic capture coordinates override an available live source.")
	source.queue_free()
	source = null
	await process_frame
	_check(not quad.can_read_live_pointer() and not view.set_frame(_frame(Session.Screen.MAIN_MENU, null)).ok,
		"The borrowed WeakRef does not keep a freed source alive or invent a replacement owner.")


func _editing(view: Page, stage: Node2D) -> void:
	var quad: Control = view.get_node("Quad")
	stage.scale = Vector2(1.2515625, 1.2515625)
	stage.position = Vector2(0, 0.125)
	_check(view.z_index + stage.z_index == 102, "Authored cursor layer remains above the host-like Z100 reflection layer.")
	var before: Transform2D = quad.get_global_transform_with_canvas() * quad.source_transform()
	view.position = Vector2(7.25, -3.5)
	view.size = Vector2(704, 432)
	view.rotation = 0.015625
	quad.position = Vector2(2.5, -1.25)
	quad.size *= Vector2(0.95, 1.05)
	quad.source_offset = Vector2(3.25, 4.5)
	quad.quad_size = Vector2(40, 36)
	quad.region = Rect2(1, 2, 120, 119)
	quad.ink_color = Color(0.8, 0.9, 1, 0.75)
	_check(quad.get_global_transform_with_canvas() * quad.source_transform() != before, "Ordinary authored Position/Size/rotation affect the real production draw mapping.")
	var geometry: Dictionary = _geometry(view)
	_check(view.set_frame(_frame(Session.Screen.MAIN_MENU, Vector2(100.125, 200.25))).ok and _geometry(view) == geometry
		and quad.drawing_rect() == Rect2(103.375, 204.75, 40, 36), "Host facts preserve deliberate geometry/source/tint edits and their actual drawing effect.")
	var facts: Dictionary = view.view_snapshot()
	view.editor_cursor_position = Vector2(320, 240)
	_check(view.view_snapshot() == facts, "Frozen Inspector position cannot replace an active runtime batch.")
	_check(view.show_editor_preview().ok and not view.get("_frame_supplied") and view.view_snapshot().cursor_position == Vector2(320, 240),
		"Explicit editor preview supplies frozen coordinates without a live source.")
	view.editor_cursor_position = Vector2(300.25, 200.125)
	_check(view.view_snapshot().cursor_position == view.editor_cursor_position and not view.get("_frame_supplied"), "Frozen Inspector edits redraw the same production definition.")
	await process_frame
	await process_frame
	var frozen: Dictionary = _state(view)
	await process_frame
	await process_frame
	_check(_state(view) == frozen, "Idle frames do not advance facts, pointer ownership or cursor coordinates.")


func _publication(view: Page) -> void:
	var packed := PackedScene.new()
	_check(packed.pack(view) == OK, "The actually edited cursor packs into a reusable scene.")
	var state: SceneState = packed.get_state()
	var visited: Dictionary = {}
	for node: int in range(state.get_node_count()):
		for property: int in range(state.get_node_property_count(node)): _stored(state.get_node_property_value(node, property), visited)
	var path: String = _output.path_join("roundtrip.tscn")
	_check(ResourceSaver.save(packed, path) == OK, "Only the fresh owned roundtrip artifact is written.")
	var saved: String = FileAccess.get_file_as_string(path)
	_check(not saved.contains("type=\"Image\"") and not saved.contains("type=\"ImageTexture\"") and not saved.contains("PackedByteArray(")
		and not saved.contains("WeakRef") and not saved.contains("_pointer_source"), "Neither decoded retail pixels nor live pointer sources enter public serialization.")
	var reopened: PackedScene = ResourceLoader.load(path, "PackedScene", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	var copy: Page = reopened.instantiate()
	_check(copy.get_node("Quad").quad_size == Vector2(40, 36) and copy.get_node("Quad").region == Rect2(1, 2, 120, 119)
		and not copy.get_node("Quad").can_read_live_pointer(), "Actual edited quad/source values are inspectable before Ready, with no retained live source.")
	view.get_parent().add_child(copy)
	await process_frame
	await process_frame
	_check(copy.get("_assets_configured") and not copy.get("_frame_supplied") and _state(copy) == _state(view),
		"Reopening preserves real edited drawing geometry, route and harmless frozen preview.")
	copy.queue_free()
	copy = null
	await process_frame


func _geometry(view: Page) -> Dictionary:
	var quad: Control = view.get_node("Quad")
	return {"page_transform": view.get_transform(), "page_size": view.size, "quad_transform": quad.get_transform(), "quad_size": quad.size,
		"source_rect": quad.source_rect, "source_offset": quad.source_offset, "draw_size": quad.quad_size, "region": quad.region, "ink": quad.ink_color}


func _state(view: Page) -> Dictionary:
	var state: Dictionary = _geometry(view)
	var quad: Control = view.get_node("Quad")
	state.facts = view.view_snapshot()
	state.rectangle = quad.drawing_rect()
	state.visible = quad.visible
	state.route = quad.texture.source_path
	state.draw = quad.draw_snapshot()
	return state


static func _frame(screen: int = Session.Screen.CLICK_TO_START, position: Variant = Vector2.ZERO) -> Dictionary:
	return {"screen": screen, "cursor_position": position}
