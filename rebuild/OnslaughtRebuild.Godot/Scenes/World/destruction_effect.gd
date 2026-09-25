# SPDX-License-Identifier: GPL-3.0-or-later
extends Node3D
## Existing tank, drone and facility layers from FirstFlightWorldView at
## 673b630a. These authored scenes preserve that reconstruction's presentation;
## unresolved emitter multiplicity, placement, velocity and colour laws remain
## unresolved. Opening a scene starts no timer, tween, input or random draw.
const F = preload("res://Scenes/Shared/retail_float32.gd")
const TexturePage = preload("res://Scenes/Shared/retail_texture_page.gd")
const ARTWORK: Dictionary = {
	"animated_blob": preload("res://Scenes/World/EffectAnimatedBlobTexture.tres"),
	"flash_medium": preload("res://Scenes/World/EffectFlashMediumTexture.tres"),
	"explosion_animated": preload("res://Scenes/World/EffectExplosionAnimatedTexture.tres"),
	"fireball": preload("res://Scenes/World/EffectFireballTexture.tres"),
}
const COLUMNS: int = 4
const ROWS: int = 4
const TICKS_PER_SECOND: int = 20
@export_group("Imported Retained Profile")
## Identifies the matching authored hierarchy, not an enhanced-effect override.
@export_enum("tank", "drone", "facility") var profile: String = "tank"
var _started: bool = false


## Admit exactly one shared recipe so the host retains the original texture
## load order. Temporary C# consumers receive this same recipe, not another
## decoded texture or a second decoder. Private pixels remain transient.
static func admit_artwork(texture_id: String) -> Dictionary:
	if not ARTWORK.has(texture_id):
		return {"ok": false, "error_type": "ArgumentException", "error": "Unknown destruction texture identity: " + texture_id}
	var recipe: TexturePage = ARTWORK[texture_id]
	var loaded: Dictionary = recipe.ensure_loaded()
	if not loaded.ok:
		return {"ok": false, "error_type": "InvalidDataException", "error": loaded.error}
	return {"ok": true, "value": recipe}


func start() -> Dictionary:
	if Engine.is_editor_hint():
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Editor destruction animation is disabled."}
	if _started or not is_inside_tree():
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Destruction requires one explicit runtime start."}
	if profile not in ["tank", "drone", "facility"]:
		return {"ok": false, "error_type": "ArgumentException", "error": "Unknown retained destruction profile."}
	_started = true
	# The original CreateTimedEffect started the timer before any layer tween.
	# Root disposal remains the timer's job, including same-time final callbacks.
	var lifetime: Timer = get_node("Lifetime")
	lifetime.timeout.connect(queue_free)
	lifetime.start()
	match profile:
		"tank": _start_tank()
		"drone": _start_drone()
		"facility": _start_facility()
	return {"ok": true}


func _start_tank() -> void:
	# Tank Explosion Medium's Time-0 Flash: radius 5 -> 0, Life 5 turns.
	var flash: MeshInstance3D = _layer("TargetTankFlash")
	_animate_scale(flash, 1.0, 0.0, 0.25)
	# Explosion Anim Sprite Medium begins at Time 5, not immediately.
	var explosion: MeshInstance3D = _layer("ExplosionAnimatedSprite")
	_animate_tank_delayed(explosion)
	# Fire Sprite Damped 2 consumes exactly one global random start, after
	# both delayed-explosion tweens exist; cells 12..15 remain unused.
	var fireball: MeshInstance3D = _layer("ExplosionFireball")
	_animate_looping_fireball(fireball, 30)
	_animate_scale(fireball, 1.0, 0.5, 1.5)


func _start_drone() -> void:
	# Drone Explosion Effect's direct Time-0 Flash and the existing single
	# representative Fire Sprite Damped 2. Debris/emitter multiplicity,
	# placement, velocity and colour evolution remain open.
	var flash: MeshInstance3D = _layer("DroneFlash")
	_animate_scale(flash, 1.0, 0.0, 0.25)
	var fireball: MeshInstance3D = _layer("DroneFireball")
	_animate_looping_fireball(fireball, 30)
	_animate_scale(fireball, 1.0, 0.5, 1.5)


func _start_facility() -> void:
	# Muspell Building Explosion Effect: direct Flash Building, one retained
	# Fire Sprite Damped Long and the Building Smoke Emitter's single retained
	# Smoke Sprite Anim Large Building. No new emitter or Fade_Col/Life_Pct law.
	var flash: MeshInstance3D = _layer("FacilityFlash")
	_animate_scale(flash, 1.0, 0.0, 0.3)
	var fireball: MeshInstance3D = _layer("FacilityFireball")
	_animate_looping_fireball(fireball, 60)
	_animate_scale(fireball, 1.0, 4.0, 3.0)
	var smoke: MeshInstance3D = _layer("FacilitySmoke")
	# This second global draw follows the fireball atlas and scale setup.
	_animate_facility_smoke(smoke)
	_animate_scale(smoke, 1.0, F.value(2.0 / 3.0), 15.0)


func _layer(path: String) -> MeshInstance3D:
	var sprite: MeshInstance3D = get_node(path)
	# Duplicate only the material. Authored geometry and the admitted private
	# texture recipe stay shared; simultaneous effects own independent UV state.
	sprite.material_override = sprite.material_override.duplicate(false)
	return sprite


func _animate_tank_delayed(sprite: MeshInstance3D) -> void:
	const START_CELL: int = 0
	const END_CELL: int = 7
	const CELLS_PER_TURN: float = 0.7
	const LIFE_SECONDS: float = 0.5
	var start_delay: float = 5.0 / TICKS_PER_SECOND
	var interval: float = 1.0 / (CELLS_PER_TURN * TICKS_PER_SECOND)
	var material: StandardMaterial3D = sprite.material_override
	_set_cell(material, START_CELL)
	sprite.visible = false
	sprite.scale = Vector3.ONE
	# Both delayed tweens belong to the root, as in the retained C# owner.
	var atlas: Tween = create_tween()
	atlas.tween_interval(start_delay)
	atlas.tween_callback(_set_visible.bind(sprite, true))
	for cell: int in range(START_CELL + 1, END_CELL + 1):
		atlas.tween_interval(interval)
		atlas.tween_callback(_set_cell.bind(material, cell))
	var scaling: Tween = create_tween()
	scaling.tween_interval(start_delay)
	# Both C# operands were Single before division: rounding only the quotient
	# of binary64 1.3/1.5 would change the final scale by one Single ULP.
	var final_scale: float = F.value(F.value(1.3) / F.value(1.5))
	scaling.tween_property(sprite, "scale", Vector3.ONE * final_scale, LIFE_SECONDS)
	scaling.tween_callback(_set_visible.bind(sprite, false))


func _animate_looping_fireball(sprite: MeshInstance3D, life_turns: int) -> void:
	const START_CELL: int = 0
	const END_CELL: int = 11
	const CELLS_PER_TURN: float = 0.5
	var cell_count: int = END_CELL - START_CELL + 1
	var initial_cell: int = START_CELL + (randi() % cell_count)
	# Intervals and turn multiplication remain binary64, as in the C# doubles.
	var interval: float = 1.0 / (CELLS_PER_TURN * TICKS_PER_SECOND)
	var advances: int = int(life_turns * CELLS_PER_TURN)
	var material: StandardMaterial3D = sprite.material_override
	_set_cell(material, initial_cell)
	var atlas: Tween = create_tween()
	for step: int in range(1, advances + 1):
		var cell: int = START_CELL + ((initial_cell - START_CELL + step) % cell_count)
		atlas.tween_interval(interval)
		atlas.tween_callback(_set_cell.bind(material, cell))
	atlas.tween_callback(_set_visible.bind(sprite, false))


func _animate_facility_smoke(sprite: MeshInstance3D) -> void:
	const START_CELL: int = 0
	const END_CELL: int = 14
	const LIFE_TURNS: int = 300
	const CELLS_PER_TURN: float = 0.5
	var cell_count: int = END_CELL - START_CELL + 1
	var initial_cell: int = START_CELL + (randi() % cell_count)
	var interval: float = 1.0 / (CELLS_PER_TURN * TICKS_PER_SECOND)
	var advances: int = int(LIFE_TURNS * CELLS_PER_TURN)
	var material: StandardMaterial3D = sprite.material_override
	_set_cell(material, initial_cell)
	var atlas: Tween = create_tween()
	for step: int in range(1, advances + 1):
		var cell: int = START_CELL + ((initial_cell - START_CELL + step) % cell_count)
		atlas.tween_interval(interval)
		atlas.tween_callback(_set_cell.bind(material, cell))
	# Unlike the fireball, the retained smoke helper added no final hide callback.


func _animate_scale(sprite: Node3D, start_scale: float, end_scale: float, duration: float) -> void:
	sprite.scale = Vector3.ONE * F.value(start_scale)
	# Ordinary scale tweens belong to the child, not the root atlas owner.
	sprite.create_tween().tween_property(sprite, "scale", Vector3.ONE * F.value(end_scale), duration)


func _set_cell(material: StandardMaterial3D, cell: int) -> void:
	# Callbacks capture the original material and cell, not a later node lookup.
	material.uv1_offset = Vector3(float(cell % COLUMNS) / COLUMNS, float(cell / COLUMNS) / ROWS, 0.0)


func _set_visible(sprite: Node3D, value: bool) -> void:
	# Likewise keep the original node if the authored hierarchy is later moved.
	sprite.visible = value
