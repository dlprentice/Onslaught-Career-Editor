# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Production Options: one pure menu/controller and authored native Controls.
## No input polling, independent clock, audio, device writes or filesystem writes.
## The host forwards input edges and consumes ordered effects at one boundary.
const Options = preload("res://Client/options_menu.gd")
const Controller = preload("res://Client/options_controller.gd")
const Laws = preload("res://Client/options_laws.gd")
const Bindings = preload("res://Client/retail_control_bindings.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const BitmapLabel = preload("res://Scenes/Frontend/frontend_bitmap_label.gd")
const OptionRow = preload("res://Scenes/Frontend/options_row.gd")
const Underlay = preload("res://Scenes/Frontend/frontend_underlay.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const PAGE_NAMES: Array[String] = ["Root", "Controller", "Video", "Sound"]
const TITLES: Array[String] = ["OPTIONS", "Controller Options", "Video Options", "Sound Options"]

@export var body_font: AtlasFont
@export var title_font: AtlasFont
@export var bindings_font: AtlasFont
@export var underlay: Underlay
@export_enum("Root", "Controller", "Video", "Sound") var editor_page: int = 0:
	set(value):
		editor_page = value
		if Engine.is_editor_hint() and is_node_ready():
			_preview()
@export_range(0, 13, 1) var editor_selected_row: int = 0:
	set(value):
		editor_selected_row = value
		if Engine.is_editor_hint() and is_node_ready():
			_preview()
@export var editor_expanded: bool = false:
	set(value):
		editor_expanded = value
		if Engine.is_editor_hint() and is_node_ready():
			_preview()

var _menu: Options.Menu
var _effect_handler: Callable
var _controller: Controller
var _seconds: float = 0.0
var _frames: Array = []
var _assets_configured: bool = false
var _host_configured: bool = false
var _last_error: String = ""


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	_ensure_menu()
	if not _assets_configured:
		var loaded: Dictionary = configure_assets({})
		if not loaded.ok:
			_last_error = loaded.error
			if not Engine.is_editor_hint():
				push_error(_last_error)
	if Engine.is_editor_hint():
		_preview()
	else:
		_refresh()
	set_frame(0.0, 0.0)


func _ensure_menu() -> void:
	if _menu == null:
		_menu = Options.create().value
		_controller = Controller.new(_menu, _effect_handler)


func set_effect_handler(handler: Callable) -> void:
	_effect_handler = handler
	if _controller != null:
		_controller.set_effect_handler(handler)


## One initialization batch. Device enumeration remains with the host adapter.
func configure_host(host: Dictionary) -> Dictionary:
	var created: Dictionary = Options.create(host)
	if not created.ok:
		return created
	_menu = created.value
	_controller = Controller.new(_menu, _effect_handler)
	_host_configured = true
	_refresh()
	return _finish({"ok": true, "value": true, "effects": []})


## Public recipes only. Each instance gets its own recipes so editor overrides
## or retry initialization cannot mutate another view's private asset routing.
func configure_assets(paths: Dictionary, shared_frames: Array = []) -> Dictionary:
	for key: String in paths:
		if not paths[key] is String:
			return {"ok": false, "error": "Options asset paths require strings."}
	body_font = _font_recipe(body_font, paths.get("body_font", ""))
	title_font = _font_recipe(title_font, paths.get("title_font", ""))
	bindings_font = _font_recipe(bindings_font, paths.get("system_font", ""))
	for font: AtlasFont in [body_font, title_font, bindings_font]:
		if font == null:
			return {"ok": false, "error": "Options scene has no authored font recipe."}
		var loaded: Dictionary = font.ensure_loaded()
		if not loaded.ok:
			return loaded
	var bracket: Texture2D = get_node("Chrome/Bracket").texture.duplicate(true)
	if paths.has("bracket"):
		bracket.set("source_path", paths.bracket)
	get_node("Chrome/Bracket").texture = bracket
	get_node("Chrome/BracketShadow").texture = bracket
	var arrow: AtlasTexture = get_node("BackArrow").texture.duplicate(true)
	if paths.has("arrow"):
		arrow.atlas.set("source_path", paths.arrow)
	for texture: Texture2D in [bracket, arrow.atlas]:
		var loaded: Dictionary = texture.ensure_loaded()
		if not loaded.ok:
			return loaded
	get_node("BackArrow").texture = arrow
	for page: Node in get_node("Pages").get_children():
		for row: Node in page.get_children():
			if row.has_node("Bar"):
				row.get_node("Bar/LeftArrow").texture = arrow
				row.get_node("Bar/RightArrow").texture = arrow
	_frames = shared_frames.duplicate()
	if _frames.is_empty() and underlay != null:
		# Standalone editor is frozen on a real first frame; live hosts inject
		# their shared production batch and retain the one frontend clock.
		var loaded: Dictionary = underlay.load_frames(1)
		if not loaded.ok:
			return loaded
		_frames = loaded.frames
	_assets_configured = true
	_ensure_menu()
	_refresh()
	return {"ok": true}


static func _font_recipe(source: AtlasFont, path: String) -> AtlasFont:
	if source == null:
		return null
	var result: AtlasFont = source.duplicate(true)
	if not path.is_empty():
		result.page.set("source_path", path)
	return result


func font_widths(title: bool) -> PackedInt32Array:
	return (title_font if title else body_font).glyph_widths()


func font_texture(title: bool) -> Texture2D:
	var page: Texture2D = (title_font if title else body_font).page
	# Batch bridge hands the retained renderer the same decoded page. Its
	# per-glyph draws stay native engine calls, with no GDScript callback.
	return page.call("_texture") if page.has_method("_texture") else page


func view_snapshot() -> Dictionary:
	_ensure_menu()
	return _menu.snapshot()


func reset_menu() -> Dictionary:
	_ensure_menu()
	return _finish(_with_effects(_menu.reset()))


func select_row(index: int) -> Dictionary:
	_ensure_menu()
	return _finish(_with_effects(_menu.hover(index)))


func handle_key(up: bool, down: bool, left: bool, right: bool, confirm: bool, back: bool) -> Dictionary:
	_ensure_menu()
	return _finish(_controller.key_matches(up, down, left, right, confirm, back))


func pointer_motion(point: Vector2) -> Dictionary:
	_ensure_menu()
	return _finish(_controller.pointer_motion(point.x, point.y, _input_label_width(point.y)))


func pointer_confirm(point: Vector2) -> Dictionary:
	_ensure_menu()
	return _finish(_controller.pointer_confirm(point.x, point.y, _input_label_width(point.y)))


func pointer_cancel(right_down: bool) -> Dictionary:
	_ensure_menu()
	return _finish(_controller.pointer_cancel(right_down))


func _input_label_width(y: float) -> float:
	var row: Dictionary
	if _menu.is_expanded():
		row = _menu.get_selected_row()
	else:
		var at: Dictionary = _menu.row_at(y)
		var rows: Dictionary = _menu.get_rows()
		if not at.ok or at.value < 0 or not rows.ok:
			return 0.0
		row = {"ok": true, "value": rows.value[at.value]}
	return body_font.measure(row.value.label) if row.ok and body_font != null else 0.0


func _finish(result: Dictionary) -> Dictionary:
	_refresh()
	var detached: Dictionary = result.duplicate(true)
	# Refresh after every operation, including a source-ordered partial failure.
	detached.settings = _menu.get_settings()
	detached.page = _menu.get_page()
	return detached


static func _with_effects(result: Dictionary) -> Dictionary:
	var value: Dictionary = result.duplicate(true)
	value.effects = []
	return value


func set_frame(animation_seconds: float, underlay_seconds: float) -> void:
	_seconds = F.value(animation_seconds)
	if _menu == null:
		return
	var page: int = _menu.get_page()
	if page < 0 or page >= PAGE_NAMES.size():
		return
	for row: OptionRow in get_node("Pages/" + PAGE_NAMES[page]).get_children():
		row.update_time(_seconds)
	var video: TextureRect = get_node("Underlay/Video")
	video.texture = null if _frames.is_empty() else _frames[Underlay.frame_index(underlay_seconds, _frames.size())]


func _preview() -> void:
	_ensure_menu()
	_menu.enter(editor_page)
	_menu.hover(editor_selected_row)
	var selected: Dictionary = _menu.get_selected_row()
	if editor_expanded and selected.ok and selected.value.kind == Options.RowKind.DROPDOWN:
		_menu.confirm()
	_refresh()
	set_frame(0.0, 0.0)


func _refresh() -> void:
	if _menu == null or not has_node("Pages") or body_font == null:
		return
	var page: int = _menu.get_page()
	for index: int in range(PAGE_NAMES.size()):
		get_node("Pages/" + PAGE_NAMES[index]).visible = page == index
	if page < 0 or page >= PAGE_NAMES.size():
		return
	get_node("Chrome/Title").bind(TITLES[page], title_font)
	var rows: Dictionary = _menu.get_rows()
	var pending: Dictionary = _menu.has_pending_changes()
	if not rows.ok or not pending.ok:
		return
	var controls: Array[Node] = get_node("Pages/" + PAGE_NAMES[page]).get_children()
	for row: OptionRow in controls:
		var index: int = row.row_index
		row.bind(rows.value[index], body_font, index == _menu.get_selected_index(), pending.value, _seconds)
	var grid: Node = get_node("Pages/Controller/Bindings/Grid")
	var bindings: Array[Dictionary] = _menu.get_bindings()
	for index: int in range(bindings.size()):
		var row: Dictionary = bindings[index]
		var node: Node = grid.get_node("Binding%02d" % index)
		node.visible = row.kind != Bindings.RowKind.SPACER
		if row.kind == Bindings.RowKind.SPACER:
			continue
		node.get_node("Action").bind(row.label, bindings_font)
		node.get_node("Slot0").bind(row.slot0, bindings_font)
		node.get_node("Slot1").bind(row.slot1, bindings_font)
	_refresh_popup(rows.value)


func _refresh_popup(rows: Array) -> void:
	var popup: Control = get_node("Dropdown")
	popup.visible = _menu.is_expanded()
	var entries: Control = popup.get_node("Entries")
	for child: Node in entries.get_children():
		entries.remove_child(child)
		child.queue_free()
	if not _menu.is_expanded():
		return
	var index: int = _menu.get_selected_index()
	var selected: Dictionary = rows[index]
	if selected.states == null or selected.states.is_empty():
		popup.visible = false
		return
	var count: int = selected.states.size()
	var top: float = _menu.row_top(index).value
	var widest: float = 0.0
	for state: int in range(count):
		var value: Dictionary = _menu.row_state_label(index, state)
		if not value.ok:
			_last_error = value.error
			return
		widest = maxf(widest, body_font.measure(value.value))
		var label: BitmapLabel = BitmapLabel.new()
		label.name = "State%02d" % state
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		label.position = Vector2(Laws.dropdown_list_x(319.0), Laws.dropdown_list_y(top, count, 16, state))
		label.size = Vector2(320.0, 16.0)
		label.bind(value.value, body_font)
		label.set_tint(OptionRow.retail_color(Laws.dropdown_list_color(state, selected.current_index)))
		entries.add_child(label)
	var panel: ColorRect = popup.get_node("Panel")
	panel.position = Vector2(Laws.dropdown_value_x(319.0), Laws.dropdown_panel_y(top, count, 16))
	panel.size = Vector2(Laws.dropdown_panel_width(int(widest)), count * 16)
