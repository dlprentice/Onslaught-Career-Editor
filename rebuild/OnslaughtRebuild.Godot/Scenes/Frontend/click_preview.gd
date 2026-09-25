# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## Frozen display facts. Editing this resource never advances CFEPIntro.
@export var pulse_timer: float = 5.0:
	set(value):
		pulse_timer = value
		emit_changed()
@export var page_seconds: float = 5.0:
	set(value):
		page_seconds = value
		emit_changed()


func snapshot() -> Dictionary:
	return {"pulse_timer": pulse_timer, "page_seconds": page_seconds}
