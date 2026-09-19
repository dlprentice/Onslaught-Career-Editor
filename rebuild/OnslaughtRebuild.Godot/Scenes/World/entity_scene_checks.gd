# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
const Owner = preload("res://Scenes/World/world_entities.gd")
const Scene = preload("res://Scenes/World/EntityPresentation.tscn")
const Target = preload("res://Client/target_presentation.gd")
const Float32 = preload("res://Core/retail_float24.gd")
var _checks: int = 0
var _failures: PackedStringArray = []
var _completed: bool = false


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	create_timer(20.0).timeout.connect(func() -> void:
		if not _completed:
			push_error("ENTITY_SCENE_CHECKS aborted before completion")
			quit(1))
	var pointer: int = Input.mouse_mode
	var world := Node3D.new()
	root.add_child(world)
	var camera := Camera3D.new()
	camera.position = Vector3(4.0, 2.0, 8.0)
	world.add_child(camera)
	var owner: Owner = Scene.instantiate()
	world.add_child(owner)
	_check(owner.get_node("Definitions/PulseBolt/PulseBoltSprite").mesh is QuadMesh, "Authored pulse geometry exists before configuration")
	_check(owner.get_node("Definitions/PulseBolt/PulseBoltHalo").mesh.size == Vector2(0.6, 0.6), "Authored halo size")
	_check(owner.get_node("Definitions/PulseBolt/PulseBoltEnergyTrail").mesh.radial_segments == 20, "Authored energy cylinder")
	_check(owner.get_node("Definitions/MuzzleFlash/PulseCannonMuzzleFlash").mesh.size == Vector2(0.6, 0.6), "Authored muzzle radius-to-side law")
	_check(owner.get_node("Definitions/MuzzleFlash/Lifetime").is_stopped(), "Opening the scene starts no effect timer")
	_check(not owner.diagnostic_snapshot().configured, "Opening the scene creates no live frame owner")
	var assets: Array = []
	for binding: Dictionary in Target.rendered_bindings():
		binding.mesh = BoxMesh.new()
		assets.append(binding)
	if Engine.is_editor_hint():
		_check(not owner.configure(world, camera, assets, []).ok, "Editor refuses live configuration")
		_check(not owner.render_frame(_batch([], []), _stage).ok, "Editor refuses render activity")
		_check(not owner.get_node("Definitions/MuzzleFlash").start().ok, "Editor refuses effect autoplay")
	else:
		var result: Variant = _runtime(owner, world, camera, assets)
		_check(result == true, "Every runtime section reached its completion marker")
	_check(Input.mouse_mode == pointer, "Scene never changes pointer ownership")
	world.free()
	await process_frame
	if Engine.is_editor_hint():
		await create_timer(1.0).timeout
		while EditorInterface.get_resource_filesystem().is_scanning():
			await process_frame
		await create_timer(0.25).timeout
	_completed = true
	if _failures.is_empty():
		print("ENTITY_SCENE_CHECKS: %d passed; native authored templates, identity, trails, explicit lifecycle and no editor activity." % _checks)
		quit(0)
	else:
		for failure: String in _failures: push_error(failure)
		quit(1)


func _runtime(owner: Owner, world: Node3D, camera: Camera3D, assets: Array) -> bool:
	_check(owner.configure(world, camera, assets, []).ok, "Explicit runtime configuration")
	_check(not owner.configure(world, camera, assets, []).ok, "Configuration has one owner")
	var image := Image.create(2, 2, false, Image.FORMAT_RGBA8)
	image.fill(Color(0.25, 0.5, 0.75, 1.0))
	var texture := ImageTexture.create_from_image(image)
	_check(owner.bind_textures({"spark": texture, "halo": texture, "energy": texture,
		"pulse_trail": texture, "vulcan_trail": texture, "muzzle": texture}).ok, "Explicit production texture binding")
	var targets: Array = []
	for index: int in range(6): targets.append(_target(index, index + 1))
	var projectiles: Array = [_projectile(11, 1, 116), _projectile(12, 2, 18), _projectile(13, 3, 20)]
	var frame: Dictionary = _batch(targets, projectiles)
	frame.pending_muzzles = 1
	var stage_count: Array[int] = [0]
	var callback: Callable = func(feet: Array) -> Dictionary:
		stage_count[0] += 1
		_check(feet.size() == 4, "Aquila receives one four-foot batch")
		_check(world.get_node_or_null("RetailLevel100TargetActor1") == null, "Aquila stage precedes actor creation")
		_check(world.get_node_or_null("RetailPulseBolt11") == null, "Aquila stage precedes projectile creation")
		return {"ok": true}
	var result: Dictionary = owner.render_frame(frame, callback)
	_check(result.ok and result.target_count == 6 and result.projectile_count == 3 and result.pending_muzzles == 0, "One native frame creates six actors and three kinds")
	_check(stage_count[0] == 1, "One callback per frame")
	var pulse: Node3D = world.get_node("RetailPulseBolt11")
	_check(pulse.get_node("PulseBoltSprite").material_override.albedo_texture == texture, "Cloned gameplay template preserves its actual bound texture")
	_check(pulse.get_node("PulseBoltHalo").mesh == owner.get_node("Definitions/PulseBolt/PulseBoltHalo").mesh, "Gameplay uses the same authored halo geometry")
	_check(pulse.get_node("ProjectileTrail").mesh.surface_get_array_len(0) == 10, "Pulse retains five trail points")
	_check(world.get_node("RetailVulcanBullet12/ProjectileTrail").mesh.surface_get_array_len(0) == 6, "Vulcan retains three trail points")
	_check(not world.get_node("RetailVulcanBullet13/ProjectileTrail").visible, "One-point new trail is hidden")
	var muzzle: Node3D = world.get_node("PulseCannonMuzzleFlash11")
	_check(muzzle.get_index() > pulse.get_index(), "Muzzle is spawned after its projectile")
	_check(not muzzle.get_node("Lifetime").is_stopped(), "Only explicit runtime spawn starts the muzzle")
	_check(muzzle.get_node("Lifetime").wait_time == 0.5, "Muzzle retains ten-turn lifetime")
	_check(muzzle.get_node("PulseCannonMuzzleFlash").material_override.uv1_offset == Vector3(0.25, 0.0, 0.0), "Muzzle starts at atlas cell one")
	_check(muzzle.get_node("PulseCannonMuzzleFlash").material_override != owner.get_node("Definitions/MuzzleFlash/PulseCannonMuzzleFlash").material_override, "Muzzle UV animation owns a detached material")
	var retained: Node3D = world.get_node("RetailLevel100TargetActor1")
	var empty: Dictionary = _batch([], [])
	empty.pending_muzzles = 3
	result = owner.render_frame(empty, _stage)
	_check(result.ok and result.target_count == 6 and result.projectile_count == 0 and result.pending_muzzles == 0, "Absent actors remain; absent projectiles retire; unmatched events clear")
	_check(world.get_node("RetailLevel100TargetActor1") == retained, "Actor omission preserves existing node")
	_check(pulse.is_queued_for_deletion(), "Projectile retirement queues the actual node")
	var hidden: Dictionary = _target(0, 1)
	hidden.is_active = false
	result = owner.render_frame(_batch([hidden], []), _stage)
	_check(result.ok and result.target_count == 5 and not retained.visible, "Explicit inactive target hides the same scene instance")
	var changed: Dictionary = _target(1, 1)
	result = owner.render_frame(_batch([changed], []), _stage)
	_check(not result.ok and result.error_type == "InvalidDataException", "Existing actor binding mutation fails closed")
	result = owner.render_frame(_batch([], [_projectile(99, 4, 20)]), _stage)
	_check(not result.ok and result.error_type == "InvalidDataException" and world.get_node_or_null("RetailPulseBolt99") == null, "Unsupported projectile never receives a guessed visual")
	var aborted: Dictionary = _batch([_target(0, 800)], [_projectile(800, 1, 120)])
	result = owner.render_frame(aborted, func(_feet: Array) -> Dictionary: return {"ok": false, "error_type": "TestAbort", "error": "stop"})
	_check(not result.ok and result.error_type == "TestAbort", "Host callback failure is returned")
	_check(world.get_node_or_null("RetailLevel100TargetActor800") == null and world.get_node_or_null("RetailPulseBolt800") == null, "Aborted Aquila stage performs no later frame mutation")
	return true


func _stage(_feet: Array) -> Dictionary:
	return {"ok": true}


func _check(value: bool, message: String) -> void:
	_checks += 1
	if not value: _failures.append(message)


static func _batch(targets: Array, projectiles: Array) -> Dictionary:
	var zero: Dictionary = {"x_bits": 0, "y_bits": 0, "z_bits": 0}
	return {"alpha_bits": 0x3f000000, "same_snapshot": false, "previous_feet": null,
		"current_feet": [zero.duplicate(), zero.duplicate(), zero.duplicate(), zero.duplicate()],
		"previous_targets": [], "current_targets": targets, "previous_projectiles": [],
		"current_projectiles": projectiles, "pending_muzzles": 0}


static func _target(binding_index: int, id: int) -> Dictionary:
	var binding: Dictionary = Target.rendered_bindings()[binding_index]
	return {"actor_id": id, "definition_name": binding.definition_name, "mesh_binding": binding.mesh_binding, "is_active": true,
		"pose": {"position_millimeters": {"x": id * 1000, "y": 2000, "z": 3000},
		"basis_float_bits": {"row0_x": 0x3f800000, "row0_y": 0, "row0_z": 0,
			"row1_x": 0, "row1_y": 0x3f800000, "row1_z": 0, "row2_x": 0, "row2_y": 0, "row2_z": 0x3f800000}}}


static func _projectile(id: int, kind: int, remaining: int) -> Dictionary:
	return {"id": id, "kind": kind, "x": 4000, "z": 8000, "elevation": 2000,
		"velocity_x": 100, "velocity_z": -250, "vertical_velocity": 20, "remaining_ticks": remaining}
