# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production Main Menu presentation. The host retains navigation, input/event
## order, transition counts and both elapsed clocks; this scene owns only their
## displayed result. Its frozen editor fixture never creates a session.
const Laws = preload("res://Client/main_menu_laws.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const Values = preload("res://Core/retail_career_values.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Underlay = preload("res://Scenes/Frontend/frontend_underlay.gd")
const Strings = preload("res://Scenes/Frontend/loading_strings.gd")
const Frozen = preload("res://Scenes/Frontend/main_menu_preview.gd")
@export var font: AtlasFont
@export var strings: Strings
@export var language_flags: Array[Texture2D] = []
@export var menu_icons: Array[Texture2D] = []
@export var editor_preview: Frozen:
	set(value):
		if editor_preview != null and editor_preview.changed.is_connected(_preview_changed):
			editor_preview.changed.disconnect(_preview_changed)
		editor_preview = value
		if editor_preview != null:
			editor_preview.changed.connect(_preview_changed)
		if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied):
			show_editor_preview()
var _facts: Dictionary = {}
var _labels: Array[PackedInt32Array] = []
var _frame_supplied: bool = false
var _assets_configured: bool = false
var _error: String = ""


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	if not _assets_configured:
		var result: Dictionary = configure_assets({})
		if not result.ok:
			_error = result.error
			if not Engine.is_editor_hint(): push_error(_error)
			return
	if not _frame_supplied:
		show_editor_preview()
	get_node("TitleLogo/Body").item_rect_changed.connect(_refresh_reflection)
	_refresh_reflection()


## Asset paths use the same Frontend/<name> keys as RetailFrontendAssetPaths.
## Admitted labels/fonts/underlay are shared once with the temporary host bridge.
func configure_assets(paths: Dictionary, shared_font: AtlasFont = null,
		shared_underlay: Underlay = null, admitted_labels: Variant = null) -> Dictionary:
	for key: Variant in paths:
		if not key is String or not paths[key] is String:
			return _failure("Main Menu asset routes require string paths.")
	var labels: Dictionary
	if admitted_labels == null:
		if strings == null: return _failure("Main Menu is missing its localization receipt.")
		labels = strings.load_menu_rows()
	else:
		labels = _admit_labels(admitted_labels)
	if not labels.ok: return labels
	var selected_font: AtlasFont = shared_font if shared_font != null else font
	if selected_font == null: return _failure("Main Menu is missing its Font13 recipe.")
	var loaded: Dictionary = selected_font.ensure_loaded()
	if not loaded.ok: return loaded
	if language_flags.size() != 5 or menu_icons.size() != 7:
		return _failure("Main Menu requires five flag recipes and seven icon recipes.")
	var next_flags: Array[Texture2D] = []
	var next_icons: Array[Texture2D] = []
	var names: Array[String] = ["Flags/flag-uk", "Flags/flag-fr", "Flags/flag-gr", "Flags/flag-it", "Flags/flag-sp"]
	for index: int in range(5):
		loaded = _load_texture(language_flags[index], "Frontend/" + names[index], paths)
		if not loaded.ok: return loaded
		next_flags.append(loaded.value)
	names = ["Icons/new-game", "Icons/continue-game", "Icons/load-game", "Icons/multiplayer", "Icons/goodies", "Icons/options", "Icons/quit"]
	for index: int in range(7):
		loaded = _load_texture(menu_icons[index], "Frontend/" + names[index], paths)
		if not loaded.ok: return loaded
		next_icons.append(loaded.value)
	var textures: Dictionary = {}
	for pair: Array in [
		["forseti-writing-large", "Writing/Tile0"], ["fe-arrow", "Language/LeftChevron"],
		["title-text-box", "Selector"], ["title-bracket-01", "Decoration/Left/Body"],
		["title-bracket-02", "Decoration/LeftTwin/Body"], ["symbol-bracket-01", "Decoration/Right/Body"],
		["symbol-bracket-02", "Decoration/RightTwin/Body"], ["title-logo", "TitleLogo/Body"],
		["reflection-map", "Reflection"]]:
		var recipe: Texture2D = get_node(pair[1]).reflection if pair[0] == "reflection-map" else get_node(pair[1]).texture
		loaded = _load_texture(recipe, "Frontend/" + pair[0], paths)
		if not loaded.ok: return loaded
		textures[pair[0]] = loaded.value
	loaded = get_node("Background").configure(shared_underlay)
	if not loaded.ok: return loaded
	font = selected_font
	_labels = labels.value
	language_flags = next_flags
	menu_icons = next_icons
	for index: int in range(3): get_node("Writing/Tile%d" % index).texture = textures["forseti-writing-large"]
	for part: String in ["LeftChevron", "RightChevron"]: get_node("Language/" + part).texture = textures["fe-arrow"]
	get_node("Selector").texture = textures["title-text-box"]
	for pair: Array in [["Left", "title-bracket-01"], ["LeftTwin", "title-bracket-02"],
		["Right", "symbol-bracket-01"], ["RightTwin", "symbol-bracket-02"]]:
		for part: String in ["Shadow", "Body"]: get_node("Decoration/" + pair[0] + "/" + part).texture = textures[pair[1]]
	for path: String in ["TitleLogo/Body", "TitleLogo/ShadowMotion/Shadow"]: get_node(path).texture = textures["title-logo"]
	get_node("Reflection").configure_textures(textures["title-logo"], textures["reflection-map"])
	get_node("Version").bind(Laws.VERSION_TEXT, font)
	_assets_configured = true
	_error = ""
	return {"ok": true}


func set_frame(facts: Dictionary) -> Dictionary:
	for key: String in ["transition", "animation_seconds", "background_seconds"]:
		if not facts.has(key) or not facts[key] is float:
			return _failure("Main Menu requires a floating-point host fact: " + key)
	for key: String in ["selected_index", "language"]:
		if not facts.has(key) or not Values.is_int32(facts[key]):
			return _failure("Main Menu requires a signed32 host fact: " + key)
	if facts.selected_index < 0 or facts.selected_index >= 7:
		return _failure("Main Menu selected index must identify one of the seven rows.")
	if not facts.has("reflection_visible") or not facts.reflection_visible is bool:
		return _failure("Main Menu requires the host's reflection visibility.")
	if not facts.has("rows") or not facts.rows is Array or facts.rows.size() != 7:
		return _failure("Main Menu requires the seven ordered row facts.")
	var rows: Array[Dictionary] = []
	for row: Variant in facts.rows:
		if not row is Dictionary or not row.has("text") or not row.has("available") or not row.available is bool:
			return _failure("Each Main Menu row requires UTF-16 text and Boolean availability.")
		var units: Dictionary = Text.units(row.text)
		if not units.ok or units.value == null:
			return _failure("Main Menu row text requires non-null UTF-16 units.")
		rows.append({"text": units.value, "available": row.available})
	if not _assets_configured: return _failure("Main Menu assets have not been admitted.")
	_facts = facts.duplicate(true)
	_facts.rows = rows
	_facts.transition = F.value(facts.transition)
	_frame_supplied = true
	var transition: float = _facts.transition
	var fade: float = Laws.page_fade(transition)
	var icon_fade: float = Laws.icon_fade(transition)
	get_node("Background").set_frame(transition, facts.background_seconds)
	for index: int in range(3): get_node("Writing/Tile%d" % index).set_fade(fade)
	get_node("Language/Flag").texture = language_flags[clampi(facts.language, 0, 4)]
	for path: String in ["Flag", "LeftChevron", "RightChevron"]: get_node("Language/" + path).set_fade(fade)
	# Existing image-initial blink counter/timer are 0/0, so both arrows draw.
	var selected: int = facts.selected_index
	get_node("Selector").set_selection(Laws.selector_rect(selected, font.measure(rows[selected].text)), icon_fade)
	for index: int in range(7):
		var label: Control = get_node(Laws.ROW_NAMES[index])
		label.bind(rows[index].text, font)
		var tint: Color = Laws.retail_color(Laws.label_color(index == selected, rows[index].available))
		label.set_tint(Color(tint, F.value(tint.a * fade)))
		label.visible = not fade <= 0.0
	var shadow: PackedFloat64Array = Laws.shadow_offset(facts.animation_seconds)
	var offset := Vector2(shadow[0], shadow[1])
	var left_offset := Vector2(shadow[0], shadow[0])
	var decorations: Array[Dictionary] = [Laws.left_decor(transition), Laws.left_twin(transition),
		Laws.right_decor(transition), Laws.right_twin(transition)]
	var names: Array[String] = ["Left", "LeftTwin", "Right", "RightTwin"]
	for index: int in range(4):
		var owner: Control = get_node("Decoration/" + names[index])
		var state: Dictionary = decorations[index]
		owner.visible = state.draw and not state.alpha <= 0.0
		owner.get_node("Shadow").set_motion(F.value(state.scale * F.value(1.05)), state.rotation, state.alpha, left_offset if index < 2 else offset)
		owner.get_node("Body").set_motion(state.scale, state.rotation, state.alpha, Vector2.ZERO)
	var icon: Texture2D = menu_icons[selected]
	get_node("SelectedIcon/Body").texture = icon
	get_node("SelectedIcon/ShadowMotion/Shadow").texture = icon
	get_node("SelectedIcon/Body").set_fade(icon_fade, null if rows[selected].available else Laws.retail_color(Laws.UNAVAILABLE))
	get_node("SelectedIcon/ShadowMotion/Shadow").set_fade(icon_fade)
	get_node("SelectedIcon/ShadowMotion").position = offset
	get_node("TitleLogo/ShadowMotion").position = offset
	get_node("TitleLogo/Body").set_fade(1.0)
	get_node("TitleLogo/ShadowMotion/Shadow").set_fade(1.0)
	var version_tint: Color = Laws.retail_color(Laws.VERSION)
	get_node("Version").set_tint(Color(version_tint, F.value(version_tint.a * fade)))
	get_node("Version").visible = not fade <= 0.0
	_refresh_reflection()
	return {"ok": true}


func hit_test(canvas_point: Vector2) -> int:
	for index: int in range(7):
		var row: Control = get_node(Laws.ROW_NAMES[index])
		var local: Vector2 = row.get_global_transform_with_canvas().affine_inverse() * canvas_point
		if Rect2(Vector2.ZERO, row.size).has_point(local): return index
	return -1


func show_editor_preview() -> Dictionary:
	if editor_preview == null: return _failure("Main Menu is missing its frozen preview.")
	if _labels.size() != 7: return _failure("Main Menu editor labels are not admitted.")
	var facts: Dictionary = editor_preview.snapshot()
	if facts.available.size() != 7: return _failure("Main Menu preview requires seven availability flags.")
	var rows: Array[Dictionary] = []
	for index: int in range(7): rows.append({"text": _labels[index].duplicate(), "available": facts.available[index]})
	facts.erase("available")
	facts.rows = rows
	var result: Dictionary = set_frame(facts)
	_frame_supplied = false
	return result


func view_snapshot() -> Dictionary:
	return _facts.duplicate(true)


func _preview_changed() -> void:
	if is_node_ready() and (Engine.is_editor_hint() or not _frame_supplied): show_editor_preview()


func _refresh_reflection() -> void:
	if _facts.is_empty() or not _assets_configured or not is_inside_tree(): return
	var sheen: Node2D = get_node("Reflection")
	sheen.visible = _facts.reflection_visible
	if sheen.visible: sheen.set_frame(_facts.background_seconds, get_node("TitleLogo/Body"))


static func _load_texture(recipe: Texture2D, key: String, paths: Dictionary) -> Dictionary:
	if recipe == null or not recipe.has_method("ensure_loaded"):
		return _failure("Main Menu is missing its production texture recipe: " + key)
	# Default scene references share their exact admitted page. A deliberate
	# host route override gets a private recipe instead of changing the shared one.
	var texture: Texture2D = recipe
	if paths.has(key) and paths[key] != recipe.get("source_path"):
		texture = recipe.duplicate(true)
		texture.set("source_path", paths[key])
	var result: Dictionary = texture.call("ensure_loaded")
	return {"ok": true, "value": texture} if result.ok else result


static func _admit_labels(value: Variant) -> Dictionary:
	if not value is Array or value.size() != 7:
		return _failure("Main Menu requires seven admitted labels in retail order.")
	var labels: Array[PackedInt32Array] = []
	for label: Variant in value:
		var result: Dictionary = Text.units(label)
		if not result.ok or result.value == null or result.value.is_empty():
			return _failure("Main Menu labels require nonempty UTF-16 units.")
		labels.append(result.value)
	return {"ok": true, "value": labels}


static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error_type": "InvalidDataException", "error": message}
