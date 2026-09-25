# SPDX-License-Identifier: MIT
@tool
extends HBoxContainer
## One editable scene instance per category; checked rows alone enter a plan.

signal selection_changed
@export var category: int = 0
@export var label_text: String = "Aircraft":
	set(value):
		label_text = value
		if is_node_ready():
			%Category.text = value
var current := 0

func _ready() -> void:
	%Category.text = label_text
	if not Engine.is_editor_hint():
		%Selected.toggled.connect(func(_value: bool) -> void: selection_changed.emit())
		%Target.value_changed.connect(func(_value: float) -> void: selection_changed.emit())

func set_current(value: int, packed: int) -> void:
	current = value
	%Current.text = str(value)
	%Packed.text = "0x%02X kept" % packed
	%Selected.set_pressed_no_signal(false)
	%Target.set_value_no_signal(value)

func set_locked(locked: bool) -> void:
	%Selected.disabled = locked
	%Target.editable = not locked

func selected() -> bool:
	return %Selected.button_pressed

func target() -> int:
	return int(%Target.value)
