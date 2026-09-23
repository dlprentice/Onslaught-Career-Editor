# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production SELECT CONFIGURATION from RetailFrontendFlow at 7474445c.
## Geometry/font/tint receipts: local-lab/retail-reference-pristine/
## select-configuration/06-select-configuration-640x480.png. The corrected
## 2026-07-26 no-skipfmv comparison localized the difference to the live unit
## window: the landscape is static and this page has no video background.
## The live unit model, mode icons, star sprites, Forseti emblem and header
## endcaps remain absent. English mode/title fallbacks are not localization.
## Session selection, input, launch/audio and time remain entirely with the host.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const FIELDS: Dictionary = {"unit_name": "Unit/Name", "walker_primary": "Walker/Primary",
	"walker_secondary": "Walker/Secondary", "jet_primary": "Jet/Primary", "jet_secondary": "Jet/Secondary"}
const TITLE: String = "SELECT CONFIGURATION"
const WALKER_TITLE: String = "Walker Mode"
const JET_TITLE: String = "Jet Mode"
@export var body_font: AtlasFont:
	set(value): body_font = value; _bind_fonts()
@export var title_font: AtlasFont:
	set(value): title_font = value; _bind_fonts()
@export var editor_unit_name: String = "BE:A Unit-00 'Prototype'":
	set(value): editor_unit_name = value; _refresh_preview()
@export var editor_walker_primary: String = "Pulse Cannon":
	set(value): editor_walker_primary = value; _refresh_preview()
@export var editor_walker_secondary: String = "Vulcan Cannon":
	set(value): editor_walker_secondary = value; _refresh_preview()
@export var editor_jet_primary: String = "Vulcan Cannon":
	set(value): editor_jet_primary = value; _refresh_preview()
@export var editor_jet_secondary: String = "Micro Missiles":
	set(value): editor_jet_secondary = value; _refresh_preview()
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
			return _failure("Configuration accepts only rock/ring/arrow string routes.")
	for key: Variant in fonts:
		if not key is String or key not in ["body_font", "title_font"] or not fonts[key] is AtlasFont:
			return _failure("Configuration accepts only shared body_font/title_font recipes.")
	var body: AtlasFont = fonts.get("body_font", body_font)
	var title: AtlasFont = fonts.get("title_font", title_font)
	for font: AtlasFont in [body, title]:
		if font == null or font.page == null or not font.page.has_method("ensure_loaded") or not font.page.get("source_path") is String:
			return _failure("Configuration font requires its production page recipe.")
		var loaded: Dictionary = font.ensure_loaded()
		if not loaded.ok: return loaded
	var textures: Dictionary = {}
	for pair: Array in [["rock", "Background/Rock"], ["ring", "Background/Ring"], ["arrow", "Navigation/Forward"]]:
		var loaded: Dictionary = _texture_recipe(get_node(pair[1]).texture, paths.get(pair[0]))
		if not loaded.ok: return loaded
		textures[pair[0]] = loaded.value
	# Admission is complete before modifying any of the authored draw controls.
	body_font = body
	title_font = title
	get_node("Background/Rock").texture = textures.rock
	get_node("Background/Ring").texture = textures.ring
	for path: String in ["Navigation/Back", "Navigation/Forward"]: get_node(path).texture = textures.arrow
	for pair: Array in [["Header/Title", TITLE], ["Walker/Title", WALKER_TITLE], ["Jet/Title", JET_TITLE]]:
		get_node(pair[0]).bind(Text.units(pair[1]).value)
	_assets_configured = true
	_error = ""
	_bind_fonts()
	return {"ok": true}


func set_frame(facts: Dictionary) -> Dictionary:
	var admitted: Dictionary = {}
	for key: String in FIELDS:
		if not facts.get(key) is PackedInt32Array: return _failure("Configuration requires raw UTF-16 field: " + key)
		var parsed: Dictionary = Text.units(facts[key])
		if not parsed.ok: return _failure(parsed.error)
		admitted[key] = parsed.value
	if not _assets_configured: return _failure("Configuration assets have not been admitted.")
	# Unknown facts, including Object/Resource references, never enter storage.
	_facts = admitted
	_frame_supplied = true
	for key: String in FIELDS: get_node(FIELDS[key]).bind(admitted[key])
	return {"ok": true}


func hit_test(design_point: Vector2) -> int:
	if get_node("Navigation/Back").contains_design_point(design_point, self): return 1
	if get_node("Navigation/Forward").contains_design_point(design_point, self): return 2
	return 0


func show_editor_preview() -> Dictionary:
	var facts: Dictionary = {}
	for key: String in FIELDS: facts[key] = Text.units(get("editor_" + key)).value
	var result: Dictionary = set_frame(facts)
	if result.ok: _frame_supplied = false
	return result


func view_snapshot() -> Dictionary:
	return _facts.duplicate(true)


func _refresh_preview() -> void:
	if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied): show_editor_preview()


func _bind_fonts() -> void:
	if not is_node_ready(): return
	for path: String in ["Header/Title", "Unit/Name"]: get_node(path).atlas_font = title_font
	for section: String in ["Walker", "Jet"]:
		for part: String in ["Title", "Primary", "Secondary"]: get_node(section + "/" + part).atlas_font = body_font


static func _texture_recipe(source: Texture2D, route: Variant) -> Dictionary:
	if source == null or not source.has_method("ensure_loaded") or not source.get("source_path") is String:
		return _failure("Configuration texture requires its production page recipe.")
	var texture: Texture2D = source
	if route != null and route != source.get("source_path"):
		texture = source.duplicate(true)
		texture.set("source_path", route)
	var loaded: Dictionary = texture.call("ensure_loaded")
	return {"ok": true, "value": texture} if loaded.ok else loaded


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
