# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends CanvasLayer

const AyaTexture = preload("res://Scenes/Shared/retail_aya_texture.gd")
const BitmapFont = preload("res://Scenes/Shared/retail_bitmap_font.gd")
const BitmapLabel = preload("res://Scenes/Shared/retail_bitmap_label.gd")
const F32 = preload("res://Scenes/Shared/retail_float32.gd")

const NATIVE_WIDTH: float = 640.0
const NATIVE_HEIGHT: float = 480.0
# Exact binary32 constants retained from the production C# presentation. Scalar
# animation calculations explicitly round at the original float stores; this
# scene owns no gameplay clock, input loop, or menu state machine.
const FADE_SECONDS: float = 0.40000000596046448
const CIRCLE_GROW_SECONDS: float = 0.20000000298023224
const PANEL_SIZE_FACTOR: float = 1.1000000238418579
const CIRCLE_INITIAL_SCALE: float = 0.10000000149011612
const CIRCLE_FINAL_SCALE: float = 1.2000000476837158
const ITEM_ROW_HEIGHT: float = 20.0
const PANEL_TITLE_BAND: float = 32.0
const PANEL_WIDTH_PADDING: float = 16.0
const PANEL_MINIMUM_SIZE: float = 64.0
const PANEL_CORNER_SIZE: float = 32.0
const NORMAL_COLOR := Color(214.0 / 255.0, 214.0 / 255.0, 214.0 / 255.0, 1.0)
const SELECTED_COLOR := Color(1.0, 204.0 / 255.0, 0.0, 1.0)
const DISABLED_COLOR := Color(80.0 / 255.0, 80.0 / 255.0, 80.0 / 255.0, 80.0 / 255.0)
const TITLE_COLOR := Color(80.0 / 255.0, 80.0 / 255.0, 80.0 / 255.0, 1.0)
const PANEL_TINT := Color(0.0, 0.0, 0.0, 192.0 / 255.0)

# Retained provenance, not a new retail measurement: CPauseMenu__Render
# (0x004d11d0) draws its active root range and optional prompt; Retry/Quit in
# CPauseMenu__ButtonPressed (0x004d0810) leave that range index at zero. Only the
# prompt has panel_flag=1 (CMenuItemRangeVariant__Init, centre 320,320).
# CMenuItemRange__Render (0x004a4810) calls CMessageLog__RenderPanelFrame
# (0x004b9010) for that flag; PauseMenu__Init (0x004cde60) leaves root unframed.
# Previous renderer's scalar specimen: lab BEA.exe, SHA-256
# e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4.
# .rdata: 005dc240=1.1 size, 005d85ec=0.5 centring, 005dc568=160 alpha,
# 005db2b8=32 corner, 005dbb50=0.0625 edge stretch over the 16px blank.
# Call-site alpha 1.2 produces ROUND(1.2*160)=192, over pure black.

@export var preview_confirmation: bool = false:
    set(value):
        preview_confirmation = value
        if Engine.is_editor_hint() and _bound:
            _apply_editor_preview()

var input_ready: bool:
    get:
        return not Engine.is_editor_hint() and _bound and _assets_loaded and _has_snapshot and \
            _surface.visible and not is_closing and _opening_seconds >= FADE_SECONDS
var is_closing: bool = false
var assets_loaded: bool:
    get:
        return _assets_loaded

var _surface: Control
var _native: Control
var _overlay: TextureRect
var _circle_01: TextureRect
var _circle_02: TextureRect
var _root_range: Control
var _confirmation_range: Control
var _frame: Control
var _root_title: BitmapLabel
var _confirmation_title: BitmapLabel
var _root_rows: Array[BitmapLabel] = []
var _confirmation_rows: Array[BitmapLabel] = []
var _bound: bool = false
var _assets_loaded: bool = false
var _asset_error: String = ""
var _opening_seconds: float = 0.0
var _closing_seconds: float = 0.0
var _has_snapshot: bool = false
var _snapshot: Dictionary = {}

func _ready() -> void:
    set_process(false)
    set_process_input(false)
    set_process_unhandled_input(false)
    if not _bind_scene():
        return
    _load_presentation_assets()
    _surface.resized.connect(_apply_visual_state)
    if Engine.is_editor_hint():
        _apply_editor_preview()
    else:
        reset_panel()

func _get_configuration_warnings() -> PackedStringArray:
    if _asset_error.is_empty():
        return PackedStringArray()
    return PackedStringArray(["Pause assets are unavailable. Use the supported private-asset preparation route. " + _asset_error])

# A snapshot is data only. The existing Client model remains the sole owner of
# selection, confirmation, enabled actions and lifecycle. The scene never
# handles a device event or advances that model.
func set_snapshot(snapshot: Dictionary) -> bool:
    if Engine.is_editor_hint():
        return false
    if not _valid_snapshot(snapshot):
        push_error("Pause presentation received an invalid menu snapshot.")
        return false
    _snapshot = snapshot.duplicate(true)
    _has_snapshot = true
    _apply_visual_state()
    return true

func _valid_snapshot(snapshot: Dictionary) -> bool:
    if not snapshot.has_all(["page", "selected_index", "underlying_root_selection", "root_entries", "entries"]):
        return false
    if not snapshot.page is int or snapshot.page < 0 or snapshot.page > 2 or \
            not snapshot.selected_index is int or not snapshot.underlying_root_selection is int:
        return false
    if not snapshot.root_entries is Array or not snapshot.entries is Array or snapshot.root_entries.size() != 8:
        return false
    var expected_entries: int = 8 if snapshot.page == 0 else 2
    if snapshot.entries.size() != expected_entries or snapshot.selected_index < 0 or \
            snapshot.selected_index >= expected_entries or snapshot.underlying_root_selection < 0 or \
            snapshot.underlying_root_selection >= 8:
        return false
    for entries: Array in [snapshot.root_entries, snapshot.entries]:
        for entry: Variant in entries:
            if not entry is Dictionary or not entry.has_all(["label", "enabled"]) or \
                    not entry.label is String or not entry.enabled is bool:
                return false
    return true

func _bind_scene() -> bool:
    if _bound:
        return true
    _surface = get_node("Surface")
    _native = get_node("Surface/Native")
    _overlay = get_node("Surface/Overlay")
    _circle_01 = get_node("Surface/Native/Circle01")
    _circle_02 = get_node("Surface/Native/Circle02")
    _root_range = get_node("Surface/Native/RootRange")
    _confirmation_range = get_node("Surface/Native/ConfirmationRange")
    _frame = _confirmation_range.get_node("Frame")
    _root_title = _root_range.get_node("Title")
    _confirmation_title = _confirmation_range.get_node("Title")
    for row: Node in _root_range.get_node("Rows").get_children():
        _root_rows.append(row as BitmapLabel)
    for row: Node in _confirmation_range.get_node("Rows").get_children():
        _confirmation_rows.append(row as BitmapLabel)
    if _root_rows.size() != 8 or _confirmation_rows.size() != 2 or _root_rows.has(null) or _confirmation_rows.has(null):
        push_error("Pause scene rows do not match the retained menu contract.")
        return false
    _bound = true
    return true

func _load_presentation_assets() -> void:
    if _assets_loaded:
        return
    var loader := AyaTexture.new()
    var blank: Texture2D = loader.load_texture("res://Assets/PauseMenu/blank.texture.aya", 16, 16, AyaTexture.Compression.DXT1)
    if not _accept_asset(blank, loader):
        return
    var circle_01: Texture2D = loader.load_texture("res://Assets/PauseMenu/circle-01.texture.aya", 256, 256)
    if not _accept_asset(circle_01, loader):
        return
    var circle_02: Texture2D = loader.load_texture("res://Assets/PauseMenu/circle-02.texture.aya", 256, 256)
    if not _accept_asset(circle_02, loader):
        return
    var corner: Texture2D = loader.load_texture("res://Assets/PauseMenu/endcurve.texture.aya", 32, 32)
    if not _accept_asset(corner, loader):
        return
    var normal_atlas: Texture2D = loader.load_texture("res://Assets/Hud/font-22.texture.aya", 512, 512, AyaTexture.Compression.RGBA8)
    if not _accept_asset(normal_atlas, loader):
        return
    var small_atlas: Texture2D = loader.load_texture("res://Assets/Hud/font-13ps.texture.aya", 256, 256, AyaTexture.Compression.RGBA8)
    if not _accept_asset(small_atlas, loader):
        return
    _overlay.texture = blank
    _circle_01.texture = circle_01
    _circle_02.texture = circle_02
    for cell: TextureRect in _frame.get_children():
        cell.texture = corner if String(cell.name).begins_with("Corner") else blank
        cell.self_modulate = PANEL_TINT
    var normal_font := BitmapFont.new(normal_atlas, 32)
    var small_font := BitmapFont.new(small_atlas, 16)
    _root_title.set_bitmap_font(normal_font)
    _confirmation_title.set_bitmap_font(normal_font)
    for row: BitmapLabel in _root_rows + _confirmation_rows:
        row.set_bitmap_font(small_font)
    _assets_loaded = true
    _asset_error = ""
    update_configuration_warnings()

func _accept_asset(texture: Texture2D, loader: AyaTexture) -> bool:
    if texture != null:
        return true
    # Keep the authored tree inspectable if private inputs are absent, without
    # substituting approximate visuals or accepting invisible runtime input.
    _asset_error = loader.error_message
    update_configuration_warnings()
    if not Engine.is_editor_hint():
        push_error(_asset_error)
    return false

func _apply_editor_preview() -> void:
    # Frozen presentation data, deliberately no Client or gameplay model. The
    # scene's authored labels and rectangles are the production preview source.
    var root_entries: Array = []
    for index: int in range(_root_rows.size()):
        root_entries.append({"label": _root_rows[index].text, "enabled": index == 0 or index >= 6})
    var confirmation_entries: Array = []
    for row: BitmapLabel in _confirmation_rows:
        confirmation_entries.append({"label": row.text, "enabled": true})
    _snapshot = {
        "page": 1 if preview_confirmation else 0,
        "selected_index": 0,
        "underlying_root_selection": 6 if preview_confirmation else 0,
        "root_entries": root_entries,
        "entries": confirmation_entries if preview_confirmation else root_entries,
    }
    _has_snapshot = true
    _surface.visible = true
    is_closing = false
    _opening_seconds = FADE_SECONDS
    _closing_seconds = 0.0
    _apply_visual_state()

func open_panel() -> void:
    if Engine.is_editor_hint() or not _bound or not _has_snapshot:
        return
    _surface.visible = true
    is_closing = false
    _opening_seconds = 0.0
    _closing_seconds = 0.0
    _apply_visual_state()

func close_panel() -> void:
    if Engine.is_editor_hint() or not _bound or not _surface.visible:
        return
    is_closing = true
    _closing_seconds = 0.0
    _apply_visual_state()

func reset_panel() -> void:
    if Engine.is_editor_hint() or not _bound:
        return
    _surface.visible = false
    is_closing = false
    _opening_seconds = 0.0
    _closing_seconds = 0.0

func advance_animation(delta: float) -> void:
    if Engine.is_editor_hint() or not _bound or not _surface.visible or not is_finite(delta) or delta <= 0.0:
        return
    if is_closing:
        _closing_seconds = F32.value(_closing_seconds + F32.value(delta))
        if _closing_seconds >= FADE_SECONDS:
            reset_panel()
    else:
        _opening_seconds = minf(F32.value(_opening_seconds + F32.value(delta)), FADE_SECONDS)
    _apply_visual_state()

# Returns an enabled row only; the bridge asks the authoritative Client model
# whether that row changes selection. Authored rectangles own the hit regions.
func point_at(viewport_position: Vector2) -> int:
    if not input_ready or _surface.size.y <= 0.0:
        return -1
    var factor: float = F32.value(_surface.size.y / NATIVE_HEIGHT)
    var offset: float = F32.value(F32.value(_surface.size.x - F32.value(NATIVE_WIDTH * factor)) * 0.5)
    var native := Vector2(F32.value(F32.value(viewport_position.x - offset) / factor), F32.value(viewport_position.y / factor))
    if native.x < 0.0 or native.x > NATIVE_WIDTH:
        return -1
    var rows: Array[BitmapLabel] = _root_rows if _snapshot.page == 0 else _confirmation_rows
    for index: int in range(rows.size()):
        var top: float = rows[index].position.y
        if native.y >= top and native.y < F32.value(top + rows[index].size.y):
            return index if _snapshot.entries[index].enabled else -1
    return -1

func _apply_visual_state() -> void:
    if not _bound or not _has_snapshot or not _surface.visible or _surface.size.x <= 0.0 or _surface.size.y <= 0.0:
        return
    var factor: float = F32.value(_surface.size.y / NATIVE_HEIGHT)
    _native.position = Vector2(F32.value(F32.value(_surface.size.x - F32.value(NATIVE_WIDTH * factor)) * 0.5), 0.0)
    _native.scale = Vector2.ONE * factor
    var transition: float = maxf(0.0, F32.value(FADE_SECONDS - _closing_seconds)) if is_closing else _opening_seconds
    var overlay_alpha: float = clampf(F32.value(F32.round_even(F32.value(transition * 480.0)) / 255.0), 0.0, F32.value(192.0 / 255.0))
    _overlay.self_modulate = Color(16.0 / 255.0, 16.0 / 255.0, 16.0 / 255.0, overlay_alpha)
    var circle_scale: float = F32.value(CIRCLE_INITIAL_SCALE + F32.value(F32.value(transition * 5.0) * PANEL_SIZE_FACTOR)) if transition < CIRCLE_GROW_SECONDS else CIRCLE_FINAL_SCALE
    var rotation_amount: float = 0.0 if transition < CIRCLE_GROW_SECONDS else F32.value(clampf(transition, CIRCLE_GROW_SECONDS, FADE_SECONDS) - CIRCLE_GROW_SECONDS)
    _circle_01.scale = Vector2.ONE * circle_scale
    _circle_02.scale = _circle_01.scale
    _circle_01.rotation = -rotation_amount
    _circle_02.rotation = rotation_amount
    _root_range.visible = transition >= FADE_SECONDS
    var confirmation: bool = _snapshot.page != 0
    _confirmation_range.visible = _root_range.visible and confirmation
    _apply_menu_range(_root_title, _root_rows, "PAUSED", _snapshot.root_entries,
        _snapshot.underlying_root_selection if confirmation else _snapshot.selected_index)
    if confirmation:
        _apply_menu_range(_confirmation_title, _confirmation_rows, "Are you sure?", _snapshot.entries, _snapshot.selected_index)
        _arrange_panel_frame("Are you sure?", _snapshot.entries)

func _apply_menu_range(title: BitmapLabel, rows: Array[BitmapLabel], title_text: String,
        entries: Array, selected_index: int) -> void:
    title.text = title_text
    title.text_color = TITLE_COLOR
    title.shadow = false
    for index: int in range(entries.size()):
        rows[index].text = entries[index].label
        rows[index].text_color = DISABLED_COLOR if not entries[index].enabled else SELECTED_COLOR if index == selected_index else NORMAL_COLOR
        rows[index].shadow = true

func _arrange_panel_frame(title: String, entries: Array) -> void:
    var widest: float = _confirmation_title.measure(title)
    var item_heights: float = 0.0
    for entry: Dictionary in entries:
        widest = maxf(widest, _confirmation_rows[0].measure(entry.label))
        item_heights = F32.value(item_heights + ITEM_ROW_HEIGHT)
    var raw_width: float = F32.value(F32.value(widest + PANEL_WIDTH_PADDING) * PANEL_SIZE_FACTOR)
    var raw_height: float = F32.value(F32.value(PANEL_TITLE_BAND + item_heights) * PANEL_SIZE_FACTOR)
    var left: float = F32.round_even(F32.value(320.0 - F32.value(raw_width * 0.5)))
    var top: float = F32.round_even(F32.value(320.0 - F32.value(raw_height * 0.5)))
    var width: float = maxf(PANEL_MINIMUM_SIZE, F32.round_even(raw_width))
    var height: float = maxf(PANEL_MINIMUM_SIZE, F32.round_even(raw_height))
    var inner_width: float = width - PANEL_CORNER_SIZE * 2.0
    var inner_height: float = height - PANEL_CORNER_SIZE * 2.0
    var right: float = left + width - PANEL_CORNER_SIZE
    var bottom: float = top + height - PANEL_CORNER_SIZE
    _set_panel_cell("CornerTopLeft", left, top, PANEL_CORNER_SIZE, PANEL_CORNER_SIZE)
    _set_panel_cell("CornerTopRight", right, top, PANEL_CORNER_SIZE, PANEL_CORNER_SIZE)
    _set_panel_cell("CornerBottomRight", right, bottom, PANEL_CORNER_SIZE, PANEL_CORNER_SIZE)
    _set_panel_cell("CornerBottomLeft", left, bottom, PANEL_CORNER_SIZE, PANEL_CORNER_SIZE)
    _set_panel_cell("Top", left + PANEL_CORNER_SIZE, top, inner_width, PANEL_CORNER_SIZE)
    _set_panel_cell("Bottom", left + PANEL_CORNER_SIZE, bottom, inner_width, PANEL_CORNER_SIZE)
    _set_panel_cell("Left", left, top + PANEL_CORNER_SIZE, PANEL_CORNER_SIZE, inner_height)
    _set_panel_cell("Right", right, top + PANEL_CORNER_SIZE, PANEL_CORNER_SIZE, inner_height)
    _set_panel_cell("Center", left + PANEL_CORNER_SIZE, top + PANEL_CORNER_SIZE, inner_width, inner_height)

func _set_panel_cell(cell_name: String, x: float, y: float, width: float, height: float) -> void:
    var cell: TextureRect = _frame.get_node(cell_name)
    cell.position = Vector2(x, y)
    cell.size = Vector2(maxf(0.0, width), maxf(0.0, height))
    cell.visible = width > 0.0 and height > 0.0
