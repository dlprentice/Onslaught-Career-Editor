# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends "res://Scenes/Frontend/main_menu_underlay.gd"
## Career retains the existing settled underlay. No transition duration has
## been evidenced; only the host-supplied FEBack time chooses a shared frame.


func prepare_frames(shared_frames: Array) -> Dictionary:
	for frame: Variant in shared_frames:
		if not frame is Texture2D:
			return {"ok": false, "error_type": "InvalidDataException", "error": "Career underlay frames must be textures."}
	if not shared_frames.is_empty(): return {"ok": true, "frames": shared_frames.duplicate(), "missing": false}
	if recipe == null: return {"ok": false, "error_type": "InvalidDataException", "error": "Career underlay needs its production recipe."}
	return recipe.load_frames(1 if Engine.is_editor_hint() else 2147483647)


func bind_frames(frames: Array) -> void:
	_frames = frames.duplicate()
	queue_redraw()


func source_transform() -> Transform2D:
	var ratio: Vector2 = size / source_rect.size
	return Transform2D(Vector2(ratio.x, 0.0), Vector2(0.0, ratio.y), -source_rect.position * ratio)
