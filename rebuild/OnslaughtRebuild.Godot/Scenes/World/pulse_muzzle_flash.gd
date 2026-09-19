# SPDX-License-Identifier: GPL-3.0-or-later
extends Node3D
## Production muzzle scene. Merely instantiating/opening it never starts time.
## The authored radius .3 becomes the .6 quad in PulseMuzzleFlash.tscn; cells
## 1..15 are PlayOnce at 1.4 cells per released 20 Hz turn, Life 10 turns.
const START_CELL: int = 1
const END_CELL: int = 15
const COLUMNS: int = 4
const ROWS: int = 4
const CELLS_PER_TURN: float = 1.4
const TICKS_PER_SECOND: int = 20
var _started: bool = false


func start() -> Dictionary:
	if Engine.is_editor_hint():
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Editor muzzle animation is disabled."}
	if _started or not is_inside_tree():
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Muzzle requires one explicit runtime start."}
	_started = true
	var lifetime: Timer = get_node("Lifetime")
	lifetime.timeout.connect(queue_free)
	lifetime.start()
	var flash: MeshInstance3D = get_node("PulseCannonMuzzleFlash")
	# Each live flash owns its animated UV state; the authored template and
	# other simultaneous flashes retain their own materials.
	flash.material_override = flash.material_override.duplicate()
	_set_cell(START_CELL)
	var atlas: Tween = create_tween()
	var interval: float = 1.0 / (CELLS_PER_TURN * TICKS_PER_SECOND)
	for cell: int in range(START_CELL + 1, END_CELL + 1):
		atlas.tween_interval(interval)
		atlas.tween_callback(_set_cell.bind(cell))
	flash.scale = Vector3.ONE
	flash.create_tween().tween_property(flash, "scale", Vector3.ONE * 5.0, 0.5)
	return {"ok": true}


func _set_cell(cell: int) -> void:
	var flash: MeshInstance3D = get_node("PulseCannonMuzzleFlash")
	var material: StandardMaterial3D = flash.material_override
	material.uv1_offset = Vector3(float(cell % COLUMNS) / COLUMNS, float(cell / COLUMNS) / ROWS, 0.0)
