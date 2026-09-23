# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Atlas label in its section's original draw frame. Imported UTF-16 stays raw;
## Inspector text replaces it only through the explicit enhanced-text switch.
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const Session = preload("res://Client/frontend_session.gd")
const Values = preload("res://Core/retail_career_values.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
signal content_changed
@export var atlas_font: AtlasFont:
	set(value): atlas_font = value; _refresh()
@export_multiline var text: String = "":
	set(value): text = value; _refresh()
@export var override_text: bool = false:
	set(value): override_text = value; _refresh()
@export var source_rect: Rect2 = Rect2(128, 130, 403, 272):
	set(value): source_rect = value; _refresh()
@export var source_anchor: Vector2 = Vector2(132, 137):
	set(value): source_anchor = value; _refresh()
@export var centered: bool = false:
	set(value): centered = value; _refresh()
@export var glyph_scale: Vector2 = Vector2(1.4, 1.4):
	set(value): glyph_scale = value; _refresh()
@export var name_glyphs: bool = false:
	set(value): name_glyphs = value; _refresh()
@export var ink_color: Color = Color(127.0 / 255.0, 127.0 / 255.0, 127.0 / 255.0):
	set(value): ink_color = value; queue_redraw()
@export var selected_ink: Color = Color(253.0 / 255.0, 253.0 / 255.0, 253.0 / 255.0):
	set(value): selected_ink = value; queue_redraw()
@export var shadow: bool = true:
	set(value): shadow = value; queue_redraw()
var _imported: Variant = null
var _present: bool = true
var _selected: bool = false


func _ready() -> void:
	set_process(false)
	set_process_input(false)
	set_process_unhandled_input(false)
	resized.connect(queue_redraw)


func bind(value: PackedInt32Array, present: bool = true, selected: bool = false) -> void:
	_imported = value.duplicate()
	_present = present
	_selected = selected
	_refresh()


func displayed_units() -> PackedInt32Array:
	return AtlasFont.units(text) if override_text or _imported == null else _imported.duplicate()


func draws_content() -> bool:
	return _present or override_text


func drawing_color() -> Color:
	return selected_ink if _selected else ink_color


func font_width_result(value: PackedInt32Array) -> Dictionary:
	if atlas_font == null: return Values.failure("InvalidDataException", "Career label has no font recipe.")
	if name_glyphs: return checked_name_width(value, atlas_font.glyph_widths(), glyph_scale.x)
	return Values.success(atlas_font.measure(value, glyph_scale.x))


func font_width() -> float:
	var result: Dictionary = font_width_result(displayed_units())
	return result.value if result.ok else 0.0


func drawing_origin() -> Vector2:
	return Vector2(F.value(source_anchor.x - F.value(font_width() * 0.5)), source_anchor.y) if centered else source_anchor


func source_transform() -> Transform2D:
	var ratio: Vector2 = size / source_rect.size
	return Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio)


func _refresh() -> void:
	queue_redraw()
	content_changed.emit()


func _draw() -> void:
	if not draws_content() or atlas_font == null or source_rect.size.x <= 0.0 or source_rect.size.y <= 0.0: return
	var width: Dictionary = font_width_result(displayed_units())
	if not width.ok: return
	draw_set_transform_matrix(source_transform())
	if not name_glyphs:
		atlas_font.draw_run(self, displayed_units(), drawing_origin(), drawing_color(), shadow, glyph_scale)
		return
	# Unlike the list, the editable name uses GameNameRenderGlyphIndex(false).
	# Keep C#'s glyph-by-glyph binary32 stores and shadow/body submission order.
	var widths: PackedInt32Array = atlas_font.glyph_widths()
	var origin: Vector2 = drawing_origin()
	var x: float = origin.x
	var tint: Color = drawing_color()
	for code: int in displayed_units():
		var glyph: int = Session.game_name_render_glyph_index(code, false)
		var cell: Vector2i = atlas_font.cell_size
		var region := Rect2((glyph % atlas_font.columns) * cell.x, (glyph / atlas_font.columns) * cell.y, widths[glyph], cell.y)
		var dest := Rect2(x, origin.y, F.value(widths[glyph] * glyph_scale.x), F.value(cell.y * glyph_scale.y))
		if shadow:
			draw_texture_rect_region(atlas_font.page, dest, region, Color(0, 0, 0, tint.a))
			draw_texture_rect_region(atlas_font.page, Rect2(dest.position - Vector2.ONE, dest.size), region, tint)
		else:
			draw_texture_rect_region(atlas_font.page, dest, region, tint)
		x = F.value(x + F.value(dest.size.x + glyph_scale.x))


static func checked_name_width(raw: PackedInt32Array, widths: PackedInt32Array, scale_x: float) -> Dictionary:
	if widths.size() != 256: return Values.failure("InvalidDataException", "Career name needs 256 glyph widths.")
	var total: int = 0
	for code: int in raw:
		var glyph: int = Session.game_name_render_glyph_index(code, false)
		# LINQ Sum checks the accumulator; the original selector's width+1 and
		# the final subtraction remain ordinary unchecked Int32 expressions.
		var next: int = total + Values.int32(widths[glyph] + 1)
		if not Values.is_int32(next): return Values.failure("OverflowException", "Career name glyph sum exceeds Int32.")
		total = next
	return Values.success(F.value(F.value(maxi(0, Values.int32(total - 1))) * F.value(scale_x)))


static func unchecked_name_extent(raw: PackedInt32Array, widths: PackedInt32Array) -> int:
	var total: int = 0
	for code: int in raw:
		total = Values.int32(total + widths[Session.game_name_render_glyph_index(code, true)] + 1)
	return total
