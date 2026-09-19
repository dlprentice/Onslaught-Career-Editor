# SPDX-License-Identifier: GPL-3.0-or-later
extends Node
## Production actor/projectile owner. There is no process/input callback and
## opening this component never changes the world. The host submits one raw
## snapshot pair per rendered frame, with one temporary Aquila callback between
## foot interpolation and actors/projectiles, retaining the old issue order.
## Core remains the sole simulation owner. Absence does not retire an actor in
## the current renderer; projectiles, in contrast, retire when absent.
const Float32 = preload("res://Core/retail_float24.gd")
const Target = preload("res://Client/target_presentation.gd")
const Interpolation = preload("res://Client/render_interpolation.gd")
const Muzzle = preload("res://Scenes/World/pulse_muzzle_flash.gd")
const ActorScene = preload("res://Scenes/World/ActorPresentation.tscn")
const PULSE_TRAIL_WIDTH_BITS: int = 0x3da3d70a # .08f
const VULCAN_TRAIL_WIDTH_BITS: int = 0x3ca3d70a # .02f
const FOOT_TELEPORT_BITS: int = 0x40400000 # 3f
const UNITS_TO_METERS_BITS: int = 0x3a83126f # .001f
const PULSE_LIFETIME: int = 120
var _world: Node3D
var _camera: Camera3D
var _assets: Array[Dictionary] = []
var _targets: Dictionary = {}
var _projectiles: Dictionary = {}
var _trails: Dictionary = {}
var _configured: bool = false
var _pending_muzzles: int = 0


## assets are the same six admitted production meshes used by imported actors.
## Existing imported actor instances are rebound, never regenerated on startup.
func configure(world: Node3D, camera: Camera3D, assets: Array, initial_targets: Array) -> Dictionary:
	if Engine.is_editor_hint() or _configured or world == null or camera == null:
		return Target.failure("InvalidOperationException", "Entity presentation requires one explicit runtime configuration.")
	_world = world
	_camera = camera
	for item: Variant in assets:
		var binding: Dictionary = Target.binding(item)
		if not binding.ok: return binding
		if not item.get("mesh") is Mesh:
			return Target.failure("ArgumentException", "Each actor binding requires its production Mesh.")
		_assets.append({"definition_name": binding.value.definition_name, "mesh_binding": binding.value.mesh_binding, "mesh": item.mesh})
	for item: Variant in initial_targets:
		var projected: Dictionary = Target.project(item)
		if not projected.ok: return projected
		var descriptor: Dictionary = projected.value
		var existing: Node3D = _world.get_node_or_null("RetailLevel100TargetActor%d" % descriptor.actor_id)
		if existing != null:
			if _targets.has(descriptor.actor_id):
				return Target.failure("ArgumentException", "Duplicate imported actor identity.")
			_targets[descriptor.actor_id] = {"root": existing, "definition_name": descriptor.definition_name, "mesh_binding": descriptor.mesh_binding}
	_configured = true
	return _result()


## Called by the explicit private importer, not by editor preview. Materials,
## sizes and transforms stay authored in the production template scenes.
func bind_textures(textures: Dictionary) -> Dictionary:
	if Engine.is_editor_hint():
		return Target.failure("InvalidOperationException", "Editor texture mutation is disabled.")
	var paths: Dictionary = {"spark": "PulseBolt/PulseBoltSprite", "halo": "PulseBolt/PulseBoltHalo",
		"energy": "PulseBolt/PulseBoltEnergyTrail", "pulse_trail": "PulseBolt/ProjectileTrail",
		"vulcan_trail": "VulcanBullet/ProjectileTrail", "muzzle": "MuzzleFlash/PulseCannonMuzzleFlash"}
	for key: String in paths:
		if not textures.get(key) is Texture2D:
			return Target.failure("ArgumentException", "Missing production texture: " + key)
	for key: String in paths:
		var visual: MeshInstance3D = get_node("Definitions/" + str(paths[key]))
		var material: StandardMaterial3D = visual.material_override
		material.albedo_texture = textures[key]
		if key != "muzzle": material.emission_texture = textures[key]
	return {"ok": true}


## batch: alpha_bits, same_snapshot, current_feet (four raw vectors),
## previous_feet (four raw vectors or null after existing reset/count gates),
## previous_targets/current_targets (Core facts), previous_projectiles/
## current_projectiles (Int32 facts), pending_muzzles. No defaults manufacture
## missing Core facts. The callback returns {ok:bool}; failure stops this frame.
func render_frame(batch: Dictionary, aquila_stage: Callable) -> Dictionary:
	if Engine.is_editor_hint() or not _configured:
		return Target.failure("InvalidOperationException", "Entity presentation is inactive.")
	if not Target.word(batch.get("alpha_bits")) or typeof(batch.get("same_snapshot")) != TYPE_BOOL \
			or not Target.i32(batch.get("pending_muzzles")) or not aquila_stage.is_valid():
		return Target.failure("ArgumentException", "Incomplete entity frame boundary.")
	for field: String in ["previous_targets", "current_targets", "previous_projectiles", "current_projectiles"]:
		if not batch.get(field) is Array:
			return Target.failure("ArgumentException", "Entity frame requires " + field + ".")
	_pending_muzzles = batch.pending_muzzles
	var feet: Dictionary = _interpolate_feet(batch)
	if not feet.ok: return _failed(feet)
	var stage: Variant = aquila_stage.call(feet.value)
	if not stage is Dictionary or not stage.get("ok", false):
		return _failed(stage if stage is Dictionary else Target.failure("InvalidOperationException", "Aquila stage aborted without a result."))
	var actors: Dictionary = _update_targets(batch)
	if not actors.ok: return _failed(actors)
	var projectiles: Dictionary = _update_projectiles(batch)
	if not projectiles.ok: return _failed(projectiles)
	return _result()


func _interpolate_feet(batch: Dictionary) -> Dictionary:
	if not batch.get("current_feet") is Array or batch.current_feet.size() != 4 or not batch.has("previous_feet"):
		return Target.failure("InvalidDataException", "Core did not expose four Aquila foot contacts.")
	if batch.previous_feet != null and (not batch.previous_feet is Array or batch.previous_feet.size() != 4):
		return Target.failure("InvalidDataException", "Previous Aquila foot contacts are incomplete.")
	var result: Array[Dictionary] = []
	for index: int in range(4):
		var contact: Dictionary = Target.admit_vector(batch.current_feet[index]) if batch.previous_feet == null else \
			Interpolation.interpolate_position(batch.previous_feet[index], batch.current_feet[index], batch.alpha_bits, FOOT_TELEPORT_BITS)
		if not contact.ok: return contact
		result.append(contact.value)
	return {"ok": true, "value": result}


func _update_targets(batch: Dictionary) -> Dictionary:
	var previous: Dictionary = {}
	if not batch.same_snapshot:
		for item: Variant in batch.previous_targets:
			var projected: Dictionary = Target.project(item)
			if not projected.ok: return projected
			previous[projected.value.actor_id] = projected.value # Last duplicate wins, as in the host dictionary.
	for item: Variant in batch.current_targets:
		var projected: Dictionary = Target.project(item)
		if not projected.ok: return projected
		var current: Dictionary = projected.value
		if not _targets.has(current.actor_id):
			var created: Dictionary = _add_target(current)
			if not created.ok: return created
		var visual: Dictionary = _targets[current.actor_id]
		if visual.definition_name != current.definition_name or visual.mesh_binding != current.mesh_binding:
			return Target.failure("InvalidDataException", "Core changed the canonical binding for Level 100 actor %d." % current.actor_id)
		var rendered: Dictionary = Interpolation.interpolate_target(previous.get(current.actor_id), current, batch.alpha_bits)
		if not rendered.ok: return rendered
		visual.root.transform = _transform(rendered.value)
		visual.root.visible = current.visible
	return {"ok": true}


func _add_target(descriptor: Dictionary) -> Dictionary:
	var mesh: Mesh
	for entry: Dictionary in _assets:
		if entry.definition_name == descriptor.definition_name and entry.mesh_binding == descriptor.mesh_binding:
			mesh = entry.mesh
			break
	if mesh == null:
		return Target.failure("InvalidDataException", "No production mesh for Level 100 actor %d." % descriptor.actor_id)
	var root: Node3D = ActorScene.instantiate()
	root.name = "RetailLevel100TargetActor%d" % descriptor.actor_id
	root.transform = _transform(descriptor)
	root.visible = descriptor.visible
	root.get_node("Geometry").mesh = mesh
	root.set_meta("actor_id", descriptor.actor_id)
	# These six admitted asset names contain no invalid Unicode/NUL. Identity
	# comparisons above retain their exact raw UTF-16 rather than String coercion.
	root.set_meta("definition", _binding_string(descriptor.definition_name))
	root.set_meta("mesh_binding", _binding_string(descriptor.mesh_binding))
	_world.add_child(root)
	_world.set_editable_instance(root, true)
	_targets[descriptor.actor_id] = {"root": root, "definition_name": descriptor.definition_name, "mesh_binding": descriptor.mesh_binding}
	return {"ok": true}


func _update_projectiles(batch: Dictionary) -> Dictionary:
	var previous: Dictionary = {}
	if not batch.same_snapshot:
		for item: Variant in batch.previous_projectiles:
			var admitted: Dictionary = _projectile_facts(item)
			if not admitted.ok: return admitted
			previous[item.id] = _projectile_state(item, _projectile_position(item))
	var active: Dictionary = {}
	for item: Variant in batch.current_projectiles:
		var admitted: Dictionary = _projectile_facts(item)
		if not admitted.ok: return admitted
		active[item.id] = true
		if not _projectiles.has(item.id):
			if not Interpolation.uses_authored_trail(item.kind).value:
				return Target.failure("InvalidDataException", "Core exposed unsupported Level 100 projectile kind %d." % item.kind)
			var template: Node3D = get_node("Definitions/PulseBolt" if item.kind == 1 else "Definitions/VulcanBullet")
			var created_visual: Node3D = template.duplicate()
			created_visual.name = ("RetailPulseBolt%d" if item.kind == 1 else "RetailVulcanBullet%d") % item.id
			_world.add_child(created_visual)
			_projectiles[item.id] = created_visual
			var created_history: Dictionary = Interpolation.create_trail_history(Interpolation.authored_point_count(item.kind).value, Interpolation.authored_lifetime_ticks(item.kind).value)
			if not created_history.ok: return created_history
			_trails[item.id] = created_history.value
			if item.kind == 1 and _pending_muzzles > 0:
				var muzzle: Dictionary = _spawn_muzzle(_launch_position(item), item.id)
				if not muzzle.ok: return muzzle
				_pending_muzzles = _i32(_pending_muzzles - 1)
		var visual: Node3D = _projectiles[item.id]
		var position: Dictionary = _projectile_position(item)
		var rendered: Dictionary = Interpolation.interpolate_projectile(previous.get(item.id),
			_projectile_state(item, _spawn_position(item)), _projectile_state(item, position), batch.alpha_bits)
		if not rendered.ok: return rendered
		visual.position = _vector(rendered.value.position)
		var direction: Vector3 = _vector(rendered.value.direction)
		if not direction.is_zero_approx():
			# Preserve the existing local-position target passed to global look_at.
			visual.look_at(visual.position + direction.normalized(), Vector3.UP)
		var history: Interpolation.TrailHistory = _trails[item.id]
		var advanced: Dictionary = history.advance(position, _trail_velocity(item), item.remaining_ticks)
		if not advanced.ok: return advanced
		var points: Dictionary = history.with_rendered_head(rendered.value.position)
		if not points.ok: return points
		# An already-live kind mutation retains its original node/history, as the
		# old owner did. An unknown kind fails here instead of silently changing it.
		if item.kind != 1 and item.kind != 2 and item.kind != 3:
			return Target.failure("ArgumentOutOfRangeException", "Unknown projectile trail kind.", "kind")
		_update_trail(visual.get_node("ProjectileTrail"), points.value, visual.global_transform.affine_inverse(),
			Float32.read_word(PULSE_TRAIL_WIDTH_BITS if item.kind == 1 else VULCAN_TRAIL_WIDTH_BITS))
	_pending_muzzles = 0 # Unmatched pulse events never leak into a later spawn.
	for id: int in _projectiles.keys():
		if not active.has(id):
			_projectiles[id].queue_free()
			_projectiles.erase(id)
			_trails.erase(id)
	return {"ok": true}


func _spawn_muzzle(position: Dictionary, id: int) -> Dictionary:
	var template: Node3D = get_node("Definitions/MuzzleFlash")
	var flash: Muzzle = template.duplicate()
	flash.name = "PulseCannonMuzzleFlash%d" % id
	flash.position = _vector(position)
	_world.add_child(flash)
	return flash.start()


func _update_trail(trail: MeshInstance3D, points: Array, world_to_projectile: Transform3D, width: float) -> void:
	if points.size() < 2:
		trail.visible = false
		return
	var surface := SurfaceTool.new()
	surface.begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	var half_width: float = Float32.store_float32(width * 0.5)
	for index: int in range(points.size()):
		var point: Vector3 = _world.to_global(_vector(points[index]))
		var neighbour: Vector3 = _world.to_global(_vector(points[index + 1] if index + 1 < points.size() else points[index - 1]))
		var direction: Vector3 = neighbour - point if index + 1 < points.size() else point - neighbour
		if direction.is_zero_approx(): direction = Vector3.FORWARD
		var side: Vector3 = direction.cross(_camera.global_position - point)
		if side.is_zero_approx(): side = direction.cross(Vector3.UP)
		if side.is_zero_approx(): side = Vector3.RIGHT
		side = side.normalized() * half_width
		var u: float = Float32.store_float32(float(index) / float(points.size() - 1))
		surface.set_uv(Vector2(u, 0.0))
		surface.add_vertex(world_to_projectile * (point - side))
		surface.set_uv(Vector2(u, 1.0))
		surface.add_vertex(world_to_projectile * (point + side))
	trail.mesh = surface.commit()
	trail.visible = true


func _result() -> Dictionary:
	var visible: int = 0
	var surfaces: int = 0
	for item: Dictionary in _targets.values():
		if item.root.visible: visible += 1
		for child: Node in item.root.get_children():
			if child is MeshInstance3D and child.mesh != null: surfaces += child.mesh.get_surface_count()
	return {"ok": true, "pending_muzzles": _pending_muzzles, "target_count": visible,
		"projectile_count": _projectiles.size(), "target_surface_count": surfaces}


func _failed(error: Dictionary) -> Dictionary:
	var result: Dictionary = error.duplicate(true)
	result.pending_muzzles = _pending_muzzles
	return result


## Explicit diagnostic only; live rendering returns counts, not per-object data.
func diagnostic_snapshot() -> Dictionary:
	var result: Dictionary = {"configured": _configured, "targets": {}, "projectiles": {}, "trails": {}}
	for id: int in _targets:
		result.targets[id] = {"transform": _targets[id].root.transform, "visible": _targets[id].root.visible}
	for id: int in _projectiles:
		result.projectiles[id] = _projectiles[id].transform
		result.trails[id] = _trails[id].snapshot()
	return result


static func _projectile_facts(value: Variant) -> Dictionary:
	if not value is Dictionary:
		return Target.failure("ArgumentException", "Projectile requires Core facts.")
	for key: String in ["id", "x", "z", "elevation", "velocity_x", "velocity_z", "vertical_velocity", "remaining_ticks"]:
		if not Target.i32(value.get(key)): return Target.failure("ArgumentException", "Projectile requires Int32 " + key + ".")
	if typeof(value.get("kind")) != TYPE_INT or value.kind < 0 or value.kind > 255:
		return Target.failure("ArgumentException", "Projectile requires its UInt8 kind.")
	return {"ok": true}


static func _projectile_position(item: Dictionary) -> Dictionary:
	return _millimeters(item.x, item.elevation, _i32(-item.z))


static func _spawn_position(item: Dictionary) -> Dictionary:
	return _millimeters(_i32(item.x - item.velocity_x), _i32(item.elevation - item.vertical_velocity), _i32(-_i32(item.z - item.velocity_z)))


static func _launch_position(item: Dictionary) -> Dictionary:
	var elapsed: int = _i32(PULSE_LIFETIME - item.remaining_ticks)
	return _millimeters(_i32(item.x - _i32(item.velocity_x * elapsed)), _i32(item.elevation - _i32(item.vertical_velocity * elapsed)), _i32(-_i32(item.z - _i32(item.velocity_z * elapsed))))


static func _trail_velocity(item: Dictionary) -> Dictionary:
	return _millimeters(item.velocity_x, item.vertical_velocity, _i32(-item.velocity_z))


static func _projectile_state(item: Dictionary, position: Dictionary) -> Dictionary:
	return {"position": position, "direction": {"x_bits": Float32.store_word(item.velocity_x), "y_bits": Float32.store_word(item.vertical_velocity), "z_bits": Float32.store_word(_i32(-item.velocity_z))}}


static func _millimeters(x: int, y: int, z: int) -> Dictionary:
	var scale: float = Float32.read_word(UNITS_TO_METERS_BITS)
	return {"x_bits": Float32.store_word(Float32.store_float32(x) * scale), "y_bits": Float32.store_word(Float32.store_float32(y) * scale), "z_bits": Float32.store_word(Float32.store_float32(z) * scale)}


static func _i32(value: int) -> int:
	var low: int = value & 0xffffffff
	return low - 0x100000000 if low >= 0x80000000 else low


static func _vector(value: Dictionary) -> Vector3:
	return Vector3(Float32.read_word(value.x_bits), Float32.read_word(value.y_bits), Float32.read_word(value.z_bits))


static func _transform(value: Dictionary) -> Transform3D:
	return Transform3D(Basis(_vector(value.basis.x_axis), _vector(value.basis.y_axis), _vector(value.basis.z_axis)), _vector(value.position))


static func _binding_string(value: PackedInt32Array) -> String:
	var text: String = ""
	for unit: int in value: text += String.chr(unit)
	return text
