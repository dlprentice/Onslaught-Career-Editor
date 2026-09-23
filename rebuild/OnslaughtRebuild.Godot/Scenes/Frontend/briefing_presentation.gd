# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production MISSION BRIEFING from RetailFrontendFlow at 51477f62. Geometry,
## Font22 name scale (0.70,1), line ceiling 286/pitch 16/empty-line gap 10 retain
## local-lab/retail-reference-pristine/mission-briefing/05-mission-briefing-640x480.png.
## Its English fallback transcription was corroborated against glyph advances;
## english.dat later supplied the authored sentences (nine-slot language pool).
## The executable source chooses that fallback whenever the supplied list is
## empty, despite its old comment saying an empty session should draw nothing.
## Preserve that behavior without inventing localization or discovery policy.
## Missing inset: PC_100_exact.vid is 201x149 at (380,177), 396 frames at 25 fps.
## Its -skipfmv black rectangle is not retail output. No black placeholder,
## decoder, playback clock, missing header endcaps or Forseti emblem is added.
## Host owns session, input, navigation, save access, audio and all time.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const BodyText = preload("res://Scenes/Frontend/briefing_body.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const WorldStrings = preload("res://Core/frontend_world_strings.gd")
const TITLE: String = "MISSION BRIEFING"
@export var body_font: AtlasFont:
	set(value): body_font = value; _bind_fonts()
@export var title_font: AtlasFont:
	set(value): title_font = value; _bind_fonts()
@export var editor_level_name: String = WorldStrings.level_name(100):
	set(value): editor_level_name = value; _refresh_preview()
@export var editor_paragraphs: PackedStringArray = PackedStringArray(WorldStrings.briefing(100)):
	set(value): editor_paragraphs = value; _refresh_preview()
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


func configure_assets(paths: Dictionary = {}, fonts: Dictionary = {}) -> Dictionary:
	for key: Variant in paths:
		if not key is String or key not in ["rock", "ring", "arrow"] or not paths[key] is String:
			return _failure("Briefing accepts only rock/ring/arrow string routes.")
	for key: Variant in fonts:
		if not key is String or key not in ["body_font", "title_font"] or not fonts[key] is AtlasFont:
			return _failure("Briefing accepts only shared body_font/title_font recipes.")
	var body: AtlasFont = fonts.get("body_font", body_font)
	var title: AtlasFont = fonts.get("title_font", title_font)
	for font: AtlasFont in [body, title]:
		if font == null or font.page == null or not font.page.has_method("ensure_loaded") or not font.page.get("source_path") is String:
			return _failure("Briefing font requires its production page recipe.")
		var loaded: Dictionary = font.ensure_loaded()
		if not loaded.ok: return loaded
	var textures: Dictionary = {}
	for pair: Array in [["rock", "Background/Rock"], ["ring", "Background/Ring"], ["arrow", "Navigation/Forward"]]:
		var loaded: Dictionary = _texture_recipe(get_node(pair[1]).texture, paths.get(pair[0]))
		if not loaded.ok: return loaded
		textures[pair[0]] = loaded.value
	body_font = body
	title_font = title
	get_node("Background/Rock").texture = textures.rock
	get_node("Background/Ring").texture = textures.ring
	for path: String in ["Navigation/Back", "Navigation/Forward"]: get_node(path).texture = textures.arrow
	get_node("Header/Title").bind(Text.units(TITLE).value)
	_assets_configured = true
	_error = ""
	_bind_fonts()
	return {"ok": true}


func set_frame(facts: Dictionary) -> Dictionary:
	var name: Dictionary = _raw_units(facts.get("level_name"))
	if not name.ok: return name
	if not facts.get("paragraphs") is Array: return _failure("Briefing paragraphs require an array of raw UTF-16 text.")
	var paragraphs: Array[PackedInt32Array] = []
	for paragraph: Variant in facts.paragraphs:
		var parsed: Dictionary = _raw_units(paragraph)
		if not parsed.ok: return parsed
		paragraphs.append(parsed.value)
	if not _assets_configured: return _failure("Briefing assets have not been admitted.")
	_facts = {"level_name": name.value, "paragraphs": paragraphs}
	_frame_supplied = true
	get_node("LevelName/Text").bind(name.value)
	var displayed: Array[PackedInt32Array] = paragraphs
	if paragraphs.is_empty():
		displayed = []
		for line: String in BodyText.FALLBACK: displayed.append(Text.units(line).value)
	get_node("Body/Text").bind(displayed)
	return {"ok": true}


func hit_test(design_point: Vector2) -> int:
	if get_node("Navigation/Back").contains_design_point(design_point, self): return 1
	if get_node("Navigation/Forward").contains_design_point(design_point, self): return 2
	return 0


func show_editor_preview() -> Dictionary:
	var paragraphs: Array[PackedInt32Array] = []
	for paragraph: String in editor_paragraphs: paragraphs.append(Text.units(paragraph).value)
	var result: Dictionary = set_frame({"level_name": Text.units(editor_level_name).value, "paragraphs": paragraphs})
	if result.ok: _frame_supplied = false
	return result


func view_snapshot() -> Dictionary:
	return _facts.duplicate(true)


func _refresh_preview() -> void:
	if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied): show_editor_preview()


func _bind_fonts() -> void:
	if not is_node_ready(): return
	for path: String in ["Header/Title", "LevelName/Text"]: get_node(path).atlas_font = title_font
	get_node("Body/Text").atlas_font = body_font


static func _texture_recipe(source: Texture2D, route: Variant) -> Dictionary:
	if source == null or not source.has_method("ensure_loaded") or not source.get("source_path") is String:
		return _failure("Briefing texture requires its production page recipe.")
	var texture: Texture2D = source
	if route != null and route != source.get("source_path"):
		texture = source.duplicate(true)
		texture.set("source_path", route)
	var loaded: Dictionary = texture.call("ensure_loaded")
	return {"ok": true, "value": texture} if loaded.ok else loaded


static func _raw_units(value: Variant) -> Dictionary:
	if not value is PackedInt32Array: return _failure("Briefing text requires raw PackedInt32Array UTF-16 units.")
	var parsed: Dictionary = Text.units(value)
	return parsed if parsed.ok else _failure(parsed.error)


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
