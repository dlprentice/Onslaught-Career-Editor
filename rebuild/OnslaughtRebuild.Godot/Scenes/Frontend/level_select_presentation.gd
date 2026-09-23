# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production FEP_LEVEL_SELECT from RetailFrontendFlow at 51477f62. The released
## source omits FEPLevelSelect.cpp. Geometry is the retained reconstruction of
## local-lab/retail-reference-pristine/select-level/04-select-level-640x480.png;
## the title's later Font22 scale 1 correction remains in the retained reference.
## Episode 1 is a capture transcription with no resolved localization ID.
## Missing Forseti emblem/writing, header endcaps and amber current-node disc
## stay undrawn. The three measured arcs are not identified retail sprites.
## RetailLevelSelectFsub148/Later148 admit the existing settled node graph;
## the other window/scaled-local evidence does not define destination or fade.
## SlidingBorders' standard-page settled scale remains 1.25 with shadow * 1.05.
## There is no new transition, graph animation, career/input/audio/save owner.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Strings = preload("res://Scenes/Frontend/loading_strings.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const WorldStrings = preload("res://Core/frontend_world_strings.gd")
const EPISODE: String = "Episode 1"
@export var body_font: AtlasFont:
	set(value): body_font = value; _bind_fonts()
@export var title_font: AtlasFont:
	set(value): title_font = value; _bind_fonts()
@export var strings: Strings
@export var editor_level_name: String = WorldStrings.level_name(100):
	set(value): editor_level_name = value; _refresh_preview()
@export var editor_background_seconds: float = 0.0:
	set(value): editor_background_seconds = value; _refresh_preview()
var _facts: Dictionary = {}
var _frame_supplied: bool = false
var _assets_configured: bool = false
var _error: String = ""


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	if not _assets_configured:
		var admitted: Dictionary = configure_assets()
		if not admitted.ok:
			_error = admitted.error
			if not Engine.is_editor_hint(): push_error(_error)
			return
	_bind_fonts()
	if not _frame_supplied: show_editor_preview()


func configure_assets(paths: Dictionary = {}, fonts: Dictionary = {}, shared_frames: Array = [], title_units: Variant = null) -> Dictionary:
	for key: Variant in paths:
		if not key is String or key not in ["bracket", "ring_outer", "ring_inner", "arrow"] or not paths[key] is String:
			return _failure("Level Select accepts only bracket/ring_outer/ring_inner/arrow string routes.")
	for key: Variant in fonts:
		if not key is String or key not in ["body_font", "title_font"] or not fonts[key] is AtlasFont:
			return _failure("Level Select accepts only shared body_font/title_font recipes.")
	var caption: Dictionary
	if title_units == null:
		if strings == null: return _failure("Level Select requires its frontend localization receipt.")
		var table: Dictionary = Strings.admit_table(FileAccess.get_file_as_string(strings.source_path), strings.source_path)
		if not table.ok: return table
		caption = {"ok": true, "value": table.value.selectLevel}
	else:
		caption = _raw_units(title_units)
		if not caption.ok: return caption
		if caption.value.is_empty(): return _failure("Level Select title must not be empty.")
	var body: AtlasFont = fonts.get("body_font", body_font)
	var title: AtlasFont = fonts.get("title_font", title_font)
	for font: AtlasFont in [body, title]:
		if font == null or font.page == null or not font.page.has_method("ensure_loaded") or not font.page.get("source_path") is String:
			return _failure("Level Select font requires its production page recipe.")
		var loaded: Dictionary = font.ensure_loaded()
		if not loaded.ok: return loaded
	var textures: Dictionary = {}
	for pair: Array in [["bracket", "Decoration/Body"], ["ring_outer", "Graph/Nodes/Node00/Outer"],
		["ring_inner", "Graph/Nodes/Node00/Inner"], ["arrow", "Navigation/Forward"]]:
		var loaded: Dictionary = _texture_recipe(get_node(pair[1]).texture, paths.get(pair[0]))
		if not loaded.ok: return loaded
		textures[pair[0]] = loaded.value
	var background: Dictionary = get_node("Background").prepare_frames(shared_frames)
	if not background.ok: return background
	# Admit the whole batch before changing any displayed content or identities.
	body_font = body
	title_font = title
	for path: String in ["Decoration/Shadow", "Decoration/Body"]: get_node(path).texture = textures.bracket
	for index: int in range(12): get_node("Graph/Nodes/Node%02d/Outer" % index).texture = textures.ring_outer
	get_node("Graph/Nodes/Node00/Inner").texture = textures.ring_inner
	for path: String in ["Navigation/Back", "Navigation/Forward"]: get_node(path).texture = textures.arrow
	get_node("Background").bind_frames(background.frames)
	get_node("Header/Title").bind(caption.value)
	get_node("Episode").bind(Text.units(EPISODE).value)
	for pair: Array in [["One", "1"], ["Two", "2"], ["Three", "3"]]: get_node("Columns/" + pair[0]).bind(Text.units(pair[1]).value)
	_assets_configured = true
	_error = ""
	_bind_fonts()
	return {"ok": true, "missing_background": background.missing}


func set_frame(facts: Dictionary) -> Dictionary:
	var name: Dictionary = _raw_units(facts.get("level_name"))
	if not name.ok: return name
	if typeof(facts.get("background_seconds")) != TYPE_FLOAT or not is_finite(facts.background_seconds):
		return _failure("Level Select background time requires a finite floating-point value.")
	if not _assets_configured: return _failure("Level Select assets have not been admitted.")
	# Only admitted display facts survive; unknown Objects/Resources never do.
	_facts = {"level_name": name.value, "background_seconds": facts.background_seconds}
	_frame_supplied = true
	get_node("LevelName").bind(name.value)
	get_node("Background").set_frame(1.0, facts.background_seconds)
	# Existing renderer always highlights node zero, even for World 110's name.
	return {"ok": true}


func hit_test(design_point: Vector2) -> int:
	if get_node("Navigation/Back").contains_design_point(design_point, self): return 1
	if get_node("Navigation/Forward").contains_design_point(design_point, self): return 2
	# These measured host targets are deliberately offset above the ring centers.
	# Availability and subsequent confirmation remain the host session's concern.
	if get_node("Graph/Nodes/Node00/Target").contains_design_point(design_point, self): return 3
	if get_node("Graph/Nodes/Node01/Target").contains_design_point(design_point, self): return 4
	return 0


func show_editor_preview() -> Dictionary:
	var result: Dictionary = set_frame({"level_name": Text.units(editor_level_name).value, "background_seconds": editor_background_seconds})
	if result.ok: _frame_supplied = false
	return result


func view_snapshot() -> Dictionary:
	return _facts.duplicate(true)


func graph_snapshot() -> Dictionary:
	var arcs: Array[Dictionary] = []
	for child: Control in get_node("SweepArcs").get_children(): arcs.append(child.drawing_parameters())
	var links: Array[Dictionary] = []
	for child: Control in get_node("Graph/Links").get_children(): links.append(child.drawing_parameters())
	var rings: Array[Dictionary] = []
	# Traverse the actual authored submission order: dim 1..11, outer 0, inner 0.
	for node: Control in get_node("Graph/Nodes").get_children():
		for ring: Control in node.get_children():
			if ring.has_method("drawing_rect"):
				rings.append({"rectangle": ring.drawing_rect(), "ink": ring.ink_color, "texture": ring.texture})
	return {"arcs": arcs, "links": links, "rings": rings}


func _refresh_preview() -> void:
	if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied): show_editor_preview()


func _bind_fonts() -> void:
	if not is_node_ready(): return
	get_node("Header/Title").atlas_font = title_font
	for path: String in ["Episode", "LevelName", "Columns/One", "Columns/Two", "Columns/Three"]: get_node(path).atlas_font = body_font


static func _texture_recipe(source: Texture2D, route: Variant) -> Dictionary:
	if source == null or not source.has_method("ensure_loaded") or not source.get("source_path") is String:
		return _failure("Level Select texture requires its production page recipe.")
	var texture: Texture2D = source
	if route != null and route != source.get("source_path"):
		texture = source.duplicate(true)
		texture.set("source_path", route)
	var loaded: Dictionary = texture.call("ensure_loaded")
	return {"ok": true, "value": texture} if loaded.ok else loaded


static func _raw_units(value: Variant) -> Dictionary:
	if not value is PackedInt32Array: return _failure("Level Select text requires raw PackedInt32Array UTF-16 units.")
	var parsed: Dictionary = Text.units(value)
	return parsed if parsed.ok else _failure(parsed.error)


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
