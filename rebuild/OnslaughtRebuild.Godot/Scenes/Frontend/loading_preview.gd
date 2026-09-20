# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Resource
## Explicit frozen host facts for editing. These never start or advance a load.
## The current admitted presenter has no progress-fill law: its bar stays fixed.
@export var loading_frames: int = 0:
	set(value):
		loading_frames = value
		emit_changed()
@export var launch_requested: bool = false:
	set(value):
		launch_requested = value
		emit_changed()
@export var ready: bool = false:
	set(value):
		ready = value
		emit_changed()


func snapshot() -> Dictionary:
	return {"loading_frames": loading_frames, "launch_requested": launch_requested, "ready": ready}
