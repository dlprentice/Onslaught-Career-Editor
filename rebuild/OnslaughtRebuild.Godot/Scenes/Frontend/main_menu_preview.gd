# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## Frozen display facts; these never advance a session, counter, RNG or clock.
@export_range(0.0, 1.0) var transition: float = 1.0:
	set(value): transition = value; emit_changed()
@export var animation_seconds: float = 0.0:
	set(value): animation_seconds = value; emit_changed()
@export var background_seconds: float = 0.0:
	set(value): background_seconds = value; emit_changed()
@export_range(0, 6) var selected_index: int = 0:
	set(value): selected_index = value; emit_changed()
@export_enum("English", "French", "German", "Italian", "Spanish") var language: int = 0:
	set(value): language = value; emit_changed()
@export var available: Array[bool] = [true, false, true, true, true, true, true]:
	set(value): available = value; emit_changed()
@export var reflection_visible: bool = true:
	set(value): reflection_visible = value; emit_changed()


func snapshot() -> Dictionary:
	return {"transition": transition, "animation_seconds": animation_seconds,
		"background_seconds": background_seconds, "selected_index": selected_index,
		"language": language, "available": available.duplicate(), "reflection_visible": reflection_visible}
