# SPDX-License-Identifier: GPL-3.0-or-later
@tool
class_name RetailBitmapText
extends Control

const BitmapFont = preload("res://Scenes/Shared/retail_bitmap_font.gd")

@export_multiline var text: String = "":
    set(value):
        text = value
        queue_redraw()
@export var text_color: Color = Color.WHITE:
    set(value):
        text_color = value
        queue_redraw()
@export var shadow: bool = false:
    set(value):
        shadow = value
        queue_redraw()

var _font: BitmapFont

func set_bitmap_font(font: BitmapFont) -> void:
    _font = font
    queue_redraw()

func measure(value: String) -> float:
    return _font.measure(value) if _font != null else 0.0

func measure_units(code_units: PackedInt32Array) -> float:
    return _font.measure_units(code_units) if _font != null else 0.0

func _notification(what: int) -> void:
    if what == NOTIFICATION_RESIZED:
        queue_redraw()

func _draw() -> void:
    if _font != null:
        _font.draw_centered(self, text, size.x * 0.5, 0.0, text_color, shadow)
