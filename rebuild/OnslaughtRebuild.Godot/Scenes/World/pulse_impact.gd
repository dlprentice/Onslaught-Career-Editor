# SPDX-License-Identifier: GPL-3.0-or-later
extends Node3D
## Existing pulse-impact reconstruction from FirstFlightWorldView at b8c1a220.
## Authored meshes and shared texture recipes are the production visuals. The
## frozen preview is its time-zero pose, before the first random atlas callback;
## scene loading/inspection consumes no RNG and starts no timer or tween.
const F = preload("res://Scenes/Shared/retail_float32.gd")
const ARTWORK = preload("res://Scenes/World/PulseShockwaveTexture.tres")
const FRAME_ADVANCES: int = 14
const ATLAS_CELLS: int = 15
const COLUMNS: int = 4
const ROWS: int = 4
var _started: bool = false


## The shockwave remains the second original effect-texture admission. Blob
## and flash are admitted by their existing shared destruction recipes.
static func admit_artwork() -> Dictionary:
	var loaded: Dictionary = ARTWORK.ensure_loaded()
	if not loaded.ok:
		return {"ok": false, "error_type": "InvalidDataException", "error": loaded.error}
	return {"ok": true}


func start(global_seconds: float) -> Dictionary:
	if Engine.is_editor_hint():
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Editor pulse-impact animation is disabled."}
	if _started or not is_inside_tree():
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Pulse impact requires one explicit runtime start."}
	var seconds: float = F.value(global_seconds)
	_started = true
	# Keep CreateTimedEffect's timer start before any animation is created.
	var lifetime: Timer = get_node("Lifetime")
	lifetime.timeout.connect(queue_free)
	lifetime.start()
	var blob: MeshInstance3D = _layer("BlueAnimatedBlob")
	_animate_blob(blob)
	# Preserve the reconstruction's 1.07f, not a newly calculated .75/.7 ratio.
	_animate_scale(blob, 1.0, F.value(1.07), 1.0)
	var flash: MeshInstance3D = _layer("FlashMedium")
	_animate_scale(flash, 1.0, 0.0, 0.3)
	var sphere: MeshInstance3D = _layer("PulseBlastSphere")
	_animate_blast(sphere, seconds)
	return {"ok": true}


func _layer(path: String) -> MeshInstance3D:
	var sprite: MeshInstance3D = get_node(path)
	# Geometry/texture recipes remain shared. Each effect owns the material
	# captured by its UV/colour callbacks, even if a later override is installed.
	sprite.material_override = sprite.material_override.duplicate(false)
	return sprite


func _animate_blob(sprite: MeshInstance3D) -> void:
	var material: StandardMaterial3D = sprite.material_override
	var start_frame: int = randi() % ATLAS_CELLS
	var atlas: Tween = create_tween()
	var interval: float = 1.0 / FRAME_ADVANCES
	for step: int in range(FRAME_ADVANCES + 1):
		var frame: int = (start_frame + step) % ATLAS_CELLS
		# The first random cell was a callback too, never an eager assignment.
		atlas.tween_callback(_set_cell.bind(material, frame))
		if step < FRAME_ADVANCES:
			atlas.tween_interval(interval)


func _animate_scale(sprite: Node3D, start_scale: float, end_scale: float, duration: float) -> void:
	sprite.scale = Vector3.ONE * F.value(start_scale)
	sprite.create_tween().tween_property(sprite, "scale", Vector3.ONE * F.value(end_scale), duration)


func _animate_blast(sphere: MeshInstance3D, global_seconds: float) -> void:
	var material: StandardMaterial3D = sphere.material_override
	var initial_v: float = initial_scroll(global_seconds)
	_apply_blast(0.0, sphere, material, initial_v)
	# Root-bound method tween captures the original sphere/material and scroll.
	create_tween().tween_method(_apply_blast.bind(sphere, material, initial_v), 0.0, 1.0, 0.5)


static func initial_scroll(global_seconds: float) -> float:
	var value: float = F.value(-2.0 * F.value(global_seconds))
	# Existing water.gd's C# Mathf.PosMod law: store the Single remainder,
	# conditionally add the positive modulus, and retain negative zero.
	var remainder: float = F.value(fmod(value, 1.0))
	return F.value(remainder + 1.0) if remainder < 0.0 else remainder


static func blast_values(initial_v: float, normalized_age: float) -> Dictionary:
	# Callable.From<float> converted the tween's age to Single before all math.
	var age: float = F.value(normalized_age)
	# As in hud_presentation.gd, this calls the native float sine overload;
	# scalar GDScript sin followed by a cast is not MathF.Sin parity.
	var sine: float = Vector2.from_angle(age).y
	var radius: float = F.value(F.value(F.value(0.6) * sine) + F.value(0.4))
	var size: float = F.value(radius / 0.5)
	var scroll: float = F.value(F.value(initial_v) - age)
	# Colors.White.Lerp(Colors.Black, age): three 1 -> 0 channels, while
	# alpha interpolates 1 -> 1. Keep the actual operations for nonfinite ages.
	var channel: float = F.value(1.0 + F.value(F.value(0.0 - 1.0) * age))
	var alpha: float = F.value(1.0 + F.value(F.value(1.0 - 1.0) * age))
	return {"scale": Vector3.ONE * size, "uv_offset": Vector3(0.0, scroll, 0.0),
		"color": Color(channel, channel, channel, alpha)}


func _apply_blast(normalized_age: float, sphere: MeshInstance3D, material: StandardMaterial3D, initial_v: float) -> void:
	var values: Dictionary = blast_values(initial_v, normalized_age)
	sphere.scale = values.scale
	material.uv1_offset = values.uv_offset
	material.albedo_color = values.color


func _set_cell(material: StandardMaterial3D, cell: int) -> void:
	material.uv1_offset = Vector3(float(cell % COLUMNS) / COLUMNS, float(cell / COLUMNS) / ROWS, 0.0)
