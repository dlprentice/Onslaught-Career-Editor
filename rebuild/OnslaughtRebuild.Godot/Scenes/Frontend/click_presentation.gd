# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production CFEPIntro layers. Their authored Controls and outer transforms
## remain editable; only named Motion children consume the host's time facts.
## No input, timer, idle/attract transition or audio owner is created here.
const Laws = preload("res://Client/click_to_start_laws.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Frozen = preload("res://Scenes/Frontend/click_preview.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const PROMPT_PARTS: Array[String] = ["BottomLeft", "BottomRight", "TopLeft", "TopRight", "Body"]
const TITLE_PARTS: Array[String] = ["BottomRight", "BottomLeft", "TopRight", "TopLeft", "Body"]
@export var font: AtlasFont
@export var editor_preview: Frozen:
	set(value):
		if editor_preview != null and editor_preview.changed.is_connected(_preview_changed):
			editor_preview.changed.disconnect(_preview_changed)
		editor_preview = value
		if editor_preview != null:
			editor_preview.changed.connect(_preview_changed)
		if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied):
			show_editor_preview()
@export var override_prompt: bool = false:
	set(value):
		override_prompt = value
		_refresh_prompt()
@export var prompt: String = "Click to start":
	set(value):
		prompt = value
		_refresh_prompt()
var _facts: Dictionary = {}
var _frame_supplied: bool = false
var _assets_configured: bool = false
var _error: String = ""


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	if not _assets_configured:
		var admitted: Dictionary = configure_assets({})
		if not admitted.ok:
			_error = admitted.error
			if not Engine.is_editor_hint(): push_error(_error)
			return
	if not _frame_supplied:
		show_editor_preview()


func configure_assets(paths: Dictionary, shared_font: AtlasFont = null) -> Dictionary:
	for key: Variant in paths:
		if not key is String or not paths[key] is String:
			return _failure("Click asset routes require string paths.")
	var dependency: Dictionary = Laws.Cosine.dependency_info()
	if not dependency.ok: return dependency
	var next_font: AtlasFont = shared_font if shared_font != null else font
	if next_font == null:
		return _failure("Click page is missing its font13 recipe.")
	var result: Dictionary = next_font.ensure_loaded()
	if not result.ok: return result
	var textures: Dictionary = {}
	for pair: Array in [["splash", "Splash/Motion/Image"], ["slide", "Slide/Shadow/Motion/Image"], ["title", "Title/Body/Motion/Image"]]:
		var texture: Texture2D = get_node(pair[1]).texture
		if texture == null: return _failure("Click page is missing its " + pair[0] + " texture.")
		if texture.has_method("ensure_loaded"):
			# Click and Main Menu reference one production title recipe. Only
			# a deliberate route override needs a separate mutable resource.
			if paths.has(pair[0]) and paths[pair[0]] != texture.get("source_path"):
				texture = texture.duplicate(true)
				texture.set("source_path", paths[pair[0]])
			result = texture.call("ensure_loaded")
			if not result.ok: return result
		textures[pair[0]] = texture
	font = next_font
	get_node("Splash/Motion/Image").texture = textures.splash
	for part: String in ["Shadow", "Body"]:
		get_node("Slide/" + part + "/Motion/Image").texture = textures.slide
	for part: String in TITLE_PARTS:
		get_node("Title/" + part + "/Motion/Image").texture = textures.title
	get_node("TitleFlash/Motion/Image").texture = textures.title
	_assets_configured = true
	_refresh_prompt()
	return {"ok": true}


func set_frame(facts: Dictionary) -> Dictionary:
	for key: String in ["pulse_timer", "page_seconds"]:
		if not facts.has(key) or not facts[key] is float:
			return _failure("Click page requires binary64 host fact: " + key)
	_facts = facts.duplicate(true)
	_frame_supplied = true
	var timer: float = facts.pulse_timer
	var seconds: float = facts.page_seconds
	var splash: Node2D = get_node("Splash/Motion")
	splash.get_node("Image").set_motion(Vector2(F.value(Laws.splash_x(timer) - 320.0),
		F.value(Laws.splash_y(timer) - 240.0)), Laws.splash_scale(timer))
	get_node("Prompt").visible = Laws.prompt_visible(timer)
	for part: String in ["Shadow", "Body"]:
		get_node("Slide/" + part + "/Motion/Image").set_motion(Vector2(-Laws.slide_offset(timer), 0.0), 1.0)
	get_node("Title").visible = Laws.title_visible(seconds)
	if Laws.title_visible(seconds):
		for index: int in range(TITLE_PARTS.size()):
			get_node("Title/" + TITLE_PARTS[index] + "/Motion/Image").set_motion(Vector2.ZERO,
				Laws.title_scale(seconds), _color(Laws.title_outline_color(seconds) if index < 4 else Laws.title_body_color(seconds)))
	get_node("TitleFlash").visible = Laws.sixth_visible(seconds)
	if Laws.sixth_visible(seconds):
		get_node("TitleFlash/Motion/Image").set_motion(Vector2.ZERO,
			Laws.sixth_scale(seconds), _color(Laws.sixth_color(seconds)))
	return {"ok": true}


func show_editor_preview() -> Dictionary:
	if editor_preview == null: return _failure("Click page is missing its frozen preview.")
	var result: Dictionary = set_frame(editor_preview.snapshot())
	_frame_supplied = false
	return result


func _preview_changed() -> void:
	if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied):
		show_editor_preview()


func _refresh_prompt() -> void:
	if not _assets_configured or not has_node("Prompt"): return
	var value: String = prompt if override_prompt else Laws.PROMPT
	var width: int = int(font.measure(value))
	for index: int in range(PROMPT_PARTS.size()):
		var part: Node2D = get_node("Prompt/" + PROMPT_PARTS[index] + "/Motion")
		part.get_node("Text").set_content_offset(Vector2(F.value(320.0 - F.value(F.value(width) * 0.5)), 0.0))
		part.get_node("Text").bind(value, font)


func view_snapshot() -> Dictionary:
	return _facts.duplicate(true)


static func _color(value: int) -> Color:
	return Color(float((value >> 16) & 255) / 255.0, float((value >> 8) & 255) / 255.0,
		float(value & 255) / 255.0, float((value >> 24) & 255) / 255.0)


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
