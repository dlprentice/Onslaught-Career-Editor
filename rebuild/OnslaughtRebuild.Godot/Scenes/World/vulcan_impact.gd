# SPDX-License-Identifier: GPL-3.0-or-later
extends Node3D
## The existing direct spark from FirstFlightWorldView at cb2c5b4a. Shipped
## Mech Bullet Hit Unit Effect schedules Spark Anim Sprite at Time 0:
## alparticle2.tga, additive, Radius .3 -> 1, Life 5 released 20 Hz turns,
## Texture_Size 2, PlayOnce cells 11..15 at .8 cells/turn. The two sibling
## emitter branches remain unresolved; this scene does not invent them.
## Opening/instantiating it keeps the authored cell-11 preview frozen. Only
## an explicit runtime start begins time; this effect consumes no RNG.
const F = preload("res://Scenes/Shared/retail_float32.gd")
const ARTWORK = preload("res://Scenes/World/VulcanImpactTexture.tres")
const START_CELL: int = 11
const END_CELL: int = 15
const COLUMNS: int = 4
const ROWS: int = 4
const CELLS_PER_TURN: float = 0.8
const TICKS_PER_SECOND: int = 20
var _started: bool = false


## The host calls this at the original third effect-texture admission stage.
## Admission and drawing share this public recipe, never a second decoder or
## serialized private image. The recipe owns its transient decoded pixels.
static func admit_artwork() -> Dictionary:
	var loaded: Dictionary = ARTWORK.ensure_loaded()
	if not loaded.ok:
		return {"ok": false, "error_type": "InvalidDataException", "error": loaded.error}
	return {"ok": true}


func start() -> Dictionary:
	if Engine.is_editor_hint():
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Editor Vulcan impact animation is disabled."}
	if _started or not is_inside_tree():
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Vulcan impact requires one explicit runtime start."}
	_started = true
	# CreateTimedEffect started this timer before either animation existed.
	# Its final timeout coincides with cell 15; preserve the separate owners.
	var lifetime: Timer = get_node("Lifetime")
	lifetime.timeout.connect(queue_free)
	lifetime.start()
	var spark: MeshInstance3D = get_node("VulcanImpactSpark")
	# UV animation is private to this instance; the texture stays shared.
	var material: StandardMaterial3D = spark.material_override.duplicate(false)
	spark.material_override = material
	_set_cell(material, START_CELL)
	var atlas: Tween = create_tween()
	# C# used double here, so retain binary64 until Godot's tween consumes it.
	var interval: float = 1.0 / (CELLS_PER_TURN * TICKS_PER_SECOND)
	for cell: int in range(START_CELL + 1, END_CELL + 1):
		atlas.tween_interval(interval)
		# The old closure captured the material, not a child lookup. Keep that
		# target even if the mesh is removed or its override is replaced.
		atlas.tween_callback(_set_cell.bind(material, cell))
	spark.scale = Vector3.ONE
	# The original end value was 10f / 3f before Vector3 multiplication.
	spark.create_tween().tween_property(spark, "scale", Vector3.ONE * F.value(10.0 / 3.0), 0.25)
	return {"ok": true}


func _set_cell(material: StandardMaterial3D, cell: int) -> void:
	material.uv1_offset = Vector3(float(cell % COLUMNS) / COLUMNS, float(cell / COLUMNS) / ROWS, 0.0)
