# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Control
## Reusable production row. The node's layout is authored; only its value,
## selected tint and private content offset are updated from the one menu.
const Options = preload("res://Client/options_menu.gd")
const Laws = preload("res://Client/options_laws.gd")
const BitmapLabel = preload("res://Scenes/Frontend/frontend_bitmap_label.gd")
const AtlasFont = preload("res://Scenes/Frontend/frontend_atlas_font.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
@export var row_index: int = 0
@export var source_rect: Rect2 = Rect2(0.0, 0.0, 640.0, 20.0)
var _row: Dictionary = {}
var _selected: bool = false
var _pending: bool = false
var _seconds: float = 0.0


func bind(row: Dictionary, font: AtlasFont, selected: bool, pending: bool, seconds: float) -> void:
	_row = row.duplicate(true)
	_selected = selected
	_pending = pending
	_seconds = seconds
	var caption: BitmapLabel = get_node_or_null("Caption")
	if caption != null:
		caption.bind(row.label, font)
	var value: BitmapLabel = get_node_or_null("Value")
	if value != null:
		value.bind(row.current_state.value if row.current_state.ok else "", font)
	if row.kind == Options.RowKind.VALUE_BAR:
		var label_width: float = font.measure(row.label)
		var total: float = F.value(F.value(label_width + 6.0) + 103.0)
		var left: float = floor(F.value(320.0 - F.value(total * 0.5)))
		caption.set_content_offset(Vector2(left, 0.0))
		get_node("Bar").position.x = F.value(F.value(left + label_width) + 6.0)
		for index: int in range(row.max_value):
			get_node("Bar/Segments/Segment%02d" % index).color = Color(0.0, 160.0 / 255.0, 0.0, 1.0) \
				if index < row.current_index else Color(80.0 / 255.0, 80.0 / 255.0, 80.0 / 255.0, 1.0)
	update_time(seconds)


func update_time(seconds: float) -> void:
	_seconds = F.value(seconds)
	if _row.is_empty():
		return
	var packed: int = Laws.menu_base_color(_selected, true)
	if _row.kind == Options.RowKind.DROPDOWN and Laws.dropdown_row_is_pending(_row.committed_index, _row.current_index):
		packed = Laws.pulse_packed_color(true, _seconds)
	elif _row.action == Options.Action.APPLY and _pending:
		packed = Laws.menu_packed_color(_selected, true, Laws.pulse_packed_color(true, _seconds))
	if _row.kind == Options.RowKind.STATUS:
		packed = 0x50505050
	for name: String in ["Caption", "Value"]:
		var label: BitmapLabel = get_node_or_null(name)
		if label != null:
			label.set_tint(retail_color(packed))


static func retail_color(argb: int) -> Color:
	return Color(F.value(mini(255, (((argb >> 16) & 255) * 255) >> 7) / 255.0),
		F.value(mini(255, (((argb >> 8) & 255) * 255) >> 7) / 255.0),
		F.value(mini(255, ((argb & 255) * 255) >> 7) / 255.0), F.value(((argb >> 24) & 255) / 255.0))
