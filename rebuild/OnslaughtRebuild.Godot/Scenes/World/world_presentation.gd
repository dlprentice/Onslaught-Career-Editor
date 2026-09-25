# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Node
## Explicit production frame controller, ported from FirstFlightWorldView at
## 1bb29345. Core supplies snapshots; the existing native components alone own
## their presentation state. This node never processes, samples input, starts
## gameplay, loads assets, or configures itself when opened in the editor.
##
## Render order is part of the contract: clock/player, feet and collection
## transport, Aquila/camera state, entities using the prior camera node, then
## camera/sky/sun/projection, terrain, appearance, water and scenery. Checked
## failures carry the already-mutated host facts; they never roll state back.
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Words = preload("res://Core/retail_float24.gd")
const CameraState = preload("res://Client/world_camera.gd")
const UNIT_SCALE_BITS: int = 0x3a83126f # .001f
const TAU_BITS: int = 0x40c90fdb # Mathf's Single tau, not binary64 TAU.
const COCKPIT_WALK_TO_FLY_BITS: int = 0x3f933333 # 23f / 20f
const COCKPIT_FLY_TO_WALK_BITS: int = 0x3f99999a # 24f / 20f
const PULSE_CANNON_POD: int = 1
const COUNT_FIELDS: Array[String] = ["target_count", "projectile_count", "target_surface_count",
	"terrain_vertex_count", "terrain_triangle_count"]

var _configured: bool = false
var _world: Node3D
var _player: Node3D
var _body: Node3D
var _walker: Node3D
var _jet: Node3D
var _cockpit: Node3D
var _camera: Camera3D
var _sky: Node3D
var _sun: Node3D
var _terrain: RefCounted
var _appearance: RefCounted
var _entities: Node
var _water: Node3D
var _scenery: RefCounted
var _camera_state: RefCounted
var _walker_height_mm: int = 1900
var _particle_presentation_seconds: float = 0.0
var _pending_muzzles: int = 0
var _walker_to_jet_visual_elapsed: float = INF
var _jet_to_walker_visual_elapsed: float = INF
var _previous_transition: int = 0
var _previous_mode: int = 0
var _show_hud: bool = false
var _opening_pan: bool = false
var _target_count: int = 0
var _projectile_count: int = 0
var _target_surface_count: int = 0
var _terrain_vertex_count: int = 0
var _terrain_triangle_count: int = 0


## References are borrowed from the already-admitted production world. Exactly
## one camera owner is created here, never during scene loading or editor use.
func configure(bindings: Variant, config: Variant) -> Dictionary:
	if Engine.is_editor_hint() or _configured:
		return _failed(_failure("InvalidOperationException", "World presentation requires one explicit runtime configuration."))
	if not bindings is Dictionary or not config is Dictionary:
		return _failed(_failure("ArgumentException", "World presentation requires bindings and configuration records."))
	for key: String in ["world", "player", "body", "walker", "jet", "cockpit", "sky", "sun", "water"]:
		if not bindings.get(key) is Node3D or not is_instance_valid(bindings[key]):
			return _failed(_failure("ArgumentException", "World presentation requires a live Node3D binding: " + key))
	if not bindings.get("camera") is Camera3D or not is_instance_valid(bindings.camera) \
			or not bindings.get("entities") is Node or not is_instance_valid(bindings.entities):
		return _failed(_failure("ArgumentException", "World presentation requires its camera and entity owner."))
	for key: String in ["terrain", "appearance", "scenery"]:
		if not bindings.get(key) is RefCounted or not is_instance_valid(bindings[key]):
			return _failed(_failure("ArgumentException", "World presentation requires its native owner: " + key))
	for key: String in ["pan_duration_ticks", "control_view_handoff_lead_ticks", "walker_height_mm"]:
		if not _is_i32(config.get(key)):
			return _failed(_failure("ArgumentException", "World configuration requires Int32 " + key + "."))
	for key: String in COUNT_FIELDS:
		if not _is_i32(config.get(key)):
			return _failed(_failure("ArgumentException", "World configuration requires Int32 " + key + "."))
	if not _is_word(config.get("near_bits")) or not _is_word(config.get("far_bits")):
		return _failed(_failure("ArgumentException", "World projection requires raw Single near/far words."))
	var camera_state: RefCounted = CameraState.new()
	var camera_result: Dictionary = _checked(camera_state.configure(config.pan_duration_ticks,
		config.control_view_handoff_lead_ticks, config.near_bits, config.far_bits), "camera")
	if not camera_result.ok:
		return _failed(_camera_error(camera_result))
	_world = bindings.world
	_player = bindings.player
	_body = bindings.body
	_walker = bindings.walker
	_jet = bindings.jet
	_cockpit = bindings.cockpit
	_camera = bindings.camera
	_sky = bindings.sky
	_sun = bindings.sun
	_terrain = bindings.terrain
	_appearance = bindings.appearance
	_entities = bindings.entities
	_water = bindings.water
	_scenery = bindings.scenery
	_camera_state = camera_state
	_walker_height_mm = config.walker_height_mm
	_target_count = config.target_count
	_projectile_count = config.projectile_count
	_target_surface_count = config.target_surface_count
	_terrain_vertex_count = config.terrain_vertex_count
	_terrain_triangle_count = config.terrain_triangle_count
	_configured = true
	return _success()


## alpha/delta are raw Single words, not newly clamped presentation values.
## Nullable snapshot members are admitted only when the old renderer read them.
func render_frame(batch: Variant) -> Dictionary:
	if Engine.is_editor_hint() or not _configured:
		return _failed(_failure("InvalidOperationException", "World presentation is inactive."))
	if not batch is Dictionary or not batch.has_all(["previous", "current", "same_snapshot", "alpha_bits", "delta_bits"]) \
			or typeof(batch.same_snapshot) != TYPE_BOOL or not _is_word(batch.alpha_bits) or not _is_word(batch.delta_bits):
		return _failed(_failure("ArgumentException", "World render requires the complete raw snapshot pair and Single words."))
	var alpha: float = Words.read_word(batch.alpha_bits)
	var frame_delta: float = Words.read_word(batch.delta_bits)
	_particle_presentation_seconds = F.value(_particle_presentation_seconds + _max_single(frame_delta, 0.0))
	var previous_position: Dictionary = _to_player_world(batch.previous)
	if not previous_position.ok: return _failed(previous_position)
	var current_position: Dictionary = _to_player_world(batch.current)
	if not current_position.ok: return _failed(current_position)
	var previous: Dictionary = batch.previous
	var current: Dictionary = batch.current
	var before: Vector3 = previous_position.value
	var after: Vector3 = current_position.value
	var reset_jump: bool = _distance_squared(before, after) > 100.0
	if not is_instance_valid(_player): return _failed(_disposed("player"))
	_player.position = after if reset_jump else _lerp_vector(before, after, alpha)
	for snapshot: Dictionary in [previous, current]:
		for key: String in ["facing_yaw_micro_rad", "facing_pitch_micro_rad", "body_roll_micro_rad"]:
			if not _is_i32(snapshot.get(key)):
				return _failed(_failure("ArgumentException", "World attitude requires Int32 " + key + "."))
	var previous_yaw: float = F.value(F.value(previous.facing_yaw_micro_rad) / 1000000.0)
	var current_yaw: float = F.value(F.value(current.facing_yaw_micro_rad) / 1000000.0)
	var player_yaw: float = _lerp_angle(previous_yaw, current_yaw, alpha)
	var previous_pitch: float = F.value(F.value(previous.facing_pitch_micro_rad) / 1000000.0)
	var current_pitch: float = F.value(F.value(current.facing_pitch_micro_rad) / 1000000.0)
	var player_pitch: float = _lerp_single(previous_pitch, current_pitch, alpha)
	var previous_roll: float = F.value(F.value(previous.body_roll_micro_rad) / 1000000.0)
	var current_roll: float = F.value(F.value(current.body_roll_micro_rad) / 1000000.0)
	var player_roll: float = _lerp_angle(previous_roll, current_roll, alpha)
	_player.rotation = Vector3(0.0, player_yaw, 0.0)
	if not _is_i32(current.get("mode")) or not _is_i32(current.get("transition")):
		return _failed(_failure("ArgumentException", "World mode and transition require exact integer carriers."))
	if not is_instance_valid(_body): return _failed(_disposed("body"))
	_body.rotation = Vector3(-player_pitch, 0.0, -player_roll) if current.mode == 1 and current.transition == 0 else Vector3.ZERO
	var entity_batch: Dictionary = _entity_frame_facts(previous, current, batch.same_snapshot, batch.alpha_bits, reset_jump)
	if not entity_batch.ok: return _failed(entity_batch)
	# This callback stays entirely native and exists only for this synchronous
	# frame. It keeps the existing entity owner's foot-before-Aquila boundary.
	var stage: Dictionary = {"camera": {}, "viewpoint": {}, "failure": {}}
	var callback: Callable = _aquila_stage.bind(previous, current, player_yaw, frame_delta, batch.alpha_bits, stage)
	var rendered: Dictionary = _call_checked(_entities, "render_frame", [entity_batch.value, callback], "entity presentation")
	if rendered.has("pending_muzzles"):
		if not _is_i32(rendered.pending_muzzles):
			return _failed(_failure("OverflowException", "Native muzzle count exceeds Int32."))
		_pending_muzzles = rendered.pending_muzzles
	if not stage.failure.is_empty(): return _failed(stage.failure)
	if not rendered.ok: return _failed(_entity_error(rendered))
	for field: String in ["target_count", "projectile_count", "target_surface_count"]:
		if not _is_i32(rendered.get(field)):
			return _failed(_failure("OverflowException", "Native entity count requires Int32 " + field + "."))
	_target_count = rendered.target_count
	_projectile_count = rendered.projectile_count
	_target_surface_count = rendered.target_surface_count
	var camera_snapshot: Dictionary = stage.camera
	var selected_viewpoint: Dictionary = stage.viewpoint
	if not is_instance_valid(_camera): return _failed(_disposed("camera"))
	# CDXEngine projection uses the fixed 0.75 tangent, not viewport aspect:
	# SetProjectionMatrix 0x00550b10 / Render 0x0053e670 / CCamera 0x0041b070.
	# See player-camera-attach-and-mesh-hfov-2026-07-26.md (binary-analysis).
	_camera.size = F.value(F.value(F.value(2.0 * Words.read_word(selected_viewpoint.near_plane_bits)) * 0.75) * Words.read_word(camera_snapshot.zoom_bits))
	var moved: Dictionary = _update_camera(camera_snapshot)
	if not moved.ok: return _failed(moved)
	var terrain: Dictionary = _call_checked(_terrain, "update", [_camera.global_position, -_camera.global_transform.basis.z], "terrain")
	if not terrain.ok: return _failed(_remap(terrain, [], "InvalidDataException"))
	if not _is_i32(terrain.get("vertex_count")) or not _is_i32(terrain.get("triangle_count")) or not terrain.has("selections"):
		return _failed(_failure("InvalidOperationException", "Native terrain returned incomplete geometry counts."))
	# The geometry and these facts survive a later appearance-cache refusal.
	_terrain_vertex_count = terrain.vertex_count
	_terrain_triangle_count = terrain.triangle_count
	var appearance: Dictionary = _call_checked(_appearance, "update_heightfield", [terrain.selections, frame_delta], "terrain appearance")
	if not appearance.ok:
		return _failed(_remap(appearance, ["IndexOutOfRangeException", "NullReferenceException", "ArgumentException", "InvalidOperationException"], "InvalidDataException"))
	var water: Dictionary = _call_checked(_water, "update_camera", [_camera.global_position, frame_delta], "water")
	if not water.ok: return _failed(_remap(water, [], "InvalidDataException"))
	var scenery: Dictionary = _call_checked(_scenery, "update", [frame_delta], "scenery")
	if not scenery.ok: return _failed(scenery)
	return _success()


## Event order and the old unchecked Int32 counter remain observable when a
## later null event refuses a batch. Other byte-valued weapons do not add flashes.
func queue_weapon_events(events: Variant) -> Dictionary:
	if Engine.is_editor_hint() or not _configured:
		return _failed(_failure("InvalidOperationException", "World presentation is inactive."))
	if events == null:
		return _failed(_failure("ArgumentNullException", "Value cannot be null.", "events"))
	if not events is Array:
		return _failed(_failure("ArgumentException", "Weapon events require an ordered Array."))
	for weapon: Variant in events:
		if weapon == null: return _failed(_null_reference())
		if not weapon is int or weapon < 0 or weapon > 255:
			return _failed(_failure("ArgumentException", "Weapon identity requires its byte-valued enum carrier."))
		if weapon == PULSE_CANNON_POD:
			_pending_muzzles = _wrap_i32(_pending_muzzles + 1)
	return _success()


func host_snapshot() -> Dictionary:
	return {"particle_seconds_bits": Words.store_word(_particle_presentation_seconds),
		"pending_muzzles": _pending_muzzles, "show_hud": _show_hud, "opening_pan": _opening_pan,
		"target_count": _target_count, "projectile_count": _projectile_count,
		"target_surface_count": _target_surface_count, "terrain_vertex_count": _terrain_vertex_count,
		"terrain_triangle_count": _terrain_triangle_count}


func update_pixel_centre_offset() -> Dictionary:
	if Engine.is_editor_hint() or not _configured:
		return _failed(_failure("InvalidOperationException", "World presentation is inactive."))
	var result: Dictionary = apply_pixel_centre_offset(_world, _camera)
	return _success() if result.ok else _failed(result)


## One law serves import/bind initialization and each rendered frame. The
## measured Direct3D 9 +0.5 pixel down/right correction belongs to projection,
## not a shader or resampled frame. See terrain-spatial-dispersion-negative-
## 2026-07-26.md section 3; that evidence does not establish a new camera law.
static func apply_pixel_centre_offset(world: Variant, camera: Variant) -> Dictionary:
	if Engine.is_editor_hint():
		return _failure("InvalidOperationException", "Editor projection mutation is disabled.")
	if not world is Node or not is_instance_valid(world) or not camera is Camera3D or not is_instance_valid(camera):
		return _failure("ArgumentException", "Pixel-centre correction requires the live world and camera.")
	var viewport: Viewport = world.get_viewport()
	var height: float = 0.0 if viewport == null else viewport.get_visible_rect().size.y
	if height <= 0.0: return {"ok": true}
	var units_per_pixel: float = F.value(camera.size / height)
	var offset: float = F.value(units_per_pixel * 0.5)
	# FrustumOffset moves the window opposite to the image; screen Y is down.
	camera.frustum_offset = Vector2(-offset, offset)
	return {"ok": true}


func _entity_frame_facts(previous: Dictionary, current: Dictionary, same: bool, alpha_bits: int, reset_jump: bool) -> Dictionary:
	var current_feet: Dictionary = _to_foot_offsets(current)
	if not current_feet.ok: return current_feet
	var previous_feet: Variant = null
	if not reset_jump and not same:
		if previous.get("feet") == null: return _null_reference()
		if not previous.feet is Array: return _failure("ArgumentException", "Previous feet require their ordered Array.")
		if previous.feet.size() == current.feet.size():
			var converted: Dictionary = _to_foot_offsets(previous)
			if not converted.ok: return converted
			previous_feet = converted.value
	var batch: Dictionary = {"alpha_bits": alpha_bits, "same_snapshot": same,
		"current_feet": current_feet.value, "previous_feet": previous_feet,
		"pending_muzzles": _pending_muzzles}
	# Targets can be the old Core property's deferred checked failure, including
	# its call-local managed exception token. Do not inspect or normalize it early.
	for field: String in ["previous_targets", "current_targets", "previous_projectiles", "current_projectiles"]:
		var old: bool = field.begins_with("previous_")
		if old and same:
			batch[field] = []
			continue
		var key: String = "targets" if field.ends_with("targets") else "projectiles"
		var items: Variant = previous.get(key) if old else current.get(key)
		if key == "targets" and items is Dictionary and items.get("ok") == false:
			return items.duplicate(true)
		if items == null: return _null_reference()
		if not items is Array: return _failure("ArgumentException", "World " + key + " require their ordered Array.")
		if key == "projectiles":
			# The old projectile transport dereferenced each row here; null actor
			# rows instead reached projection after the Aquila callback.
			for item: Variant in items:
				if item == null: return _null_reference()
		batch[field] = items
	return {"ok": true, "value": batch}


func _aquila_stage(contacts: Array, previous: Dictionary, current: Dictionary, yaw: float,
		frame_delta: float, alpha_bits: int, stage: Dictionary) -> Dictionary:
	var result: Dictionary = _apply_walker_pose(contacts, yaw)
	if result.ok: result = _update_aquila_transition_presentation(current, frame_delta)
	if result.ok: result = _camera_error(_call_checked(_camera_state, "advance", [previous, current], "camera"))
	if result.ok:
		result = _camera_error(_call_checked(_camera_state, "sample_and_bind", [alpha_bits], "camera"))
		if result.ok:
			stage.camera = result.value.camera
			stage.viewpoint = result.value.viewpoint
			_show_hud = stage.camera.hud_visible
			_opening_pan = stage.camera.opening_pan_active
			result = _update_player_shape(current, _show_hud)
	if not result.ok: stage.failure = result
	return result


func _update_player_shape(snapshot: Dictionary, attached_view: bool) -> Dictionary:
	var showing_jet: bool = is_finite(_walker_to_jet_visual_elapsed) or is_finite(_jet_to_walker_visual_elapsed) \
		or snapshot.transition != 0 or snapshot.mode == 1
	if not is_instance_valid(_walker): return _disposed("walker")
	_walker.visible = not attached_view and not showing_jet
	if not is_instance_valid(_jet): return _disposed("jet")
	_jet.visible = not attached_view and showing_jet
	if not is_instance_valid(_cockpit): return _disposed("cockpit")
	_cockpit.visible = attached_view
	if not is_instance_valid(_body): return _disposed("body")
	_body.position = Vector3.UP * F.value(F.value(_walker_height_mm) * Words.read_word(UNIT_SCALE_BITS)) if showing_jet else Vector3.ZERO
	return {"ok": true}


func _update_aquila_transition_presentation(snapshot: Dictionary, frame_delta: float) -> Dictionary:
	var delta: float = F.value(frame_delta)
	if not _is_i32(snapshot.get("mode")) or not _is_i32(snapshot.get("transition")):
		return _failure("ArgumentException", "Aquila mode and transition require exact integer carriers.")
	var walker_started: bool = snapshot.transition == 1 and _previous_transition != 1
	var jet_started: bool = snapshot.transition == 2 and _previous_transition != 2
	var returned_to_walker: bool = snapshot.transition == 0 and snapshot.mode == 0 \
		and (_previous_transition != 0 or _previous_mode == 1)
	if walker_started:
		_walker_to_jet_visual_elapsed = 0.0
		_jet_to_walker_visual_elapsed = INF
	elif jet_started:
		_walker_to_jet_visual_elapsed = INF
		_jet_to_walker_visual_elapsed = 0.0
	elif returned_to_walker:
		_walker_to_jet_visual_elapsed = INF
		_jet_to_walker_visual_elapsed = INF
	var result: Dictionary
	if is_finite(_walker_to_jet_visual_elapsed):
		_walker_to_jet_visual_elapsed = _min_single(F.value(_walker_to_jet_visual_elapsed + _max_single(0.0, delta)), 1.25)
		var jet_step: int = mini(_floor_to_i32(F.value(_walker_to_jet_visual_elapsed * 20.0)), 25)
		result = _set_virtual_frame(_jet, F.value(25.0 + F.value(jet_step)))
		if not result.ok: return result
		# Steam begins cockpit current=1/24 (virtual 27), external jet current=0
		# (virtual 25). Keep the independently admitted sequence lengths/rates.
		if _walker_to_jet_visual_elapsed < Words.read_word(COCKPIT_WALK_TO_FLY_BITS):
			var cockpit_step: int = mini(_floor_to_i32(F.value(_walker_to_jet_visual_elapsed * 20.0)), 22)
			result = _set_virtual_frame(_cockpit, F.value(27.0 + F.value(cockpit_step)))
		else:
			result = _set_virtual_frame(_cockpit, 0.0)
		if not result.ok: return result
		if _walker_to_jet_visual_elapsed >= 1.25:
			result = _set_virtual_frame(_jet, 0.0)
			if not result.ok: return result
			_walker_to_jet_visual_elapsed = INF
	elif is_finite(_jet_to_walker_visual_elapsed):
		_jet_to_walker_visual_elapsed = _min_single(F.value(_jet_to_walker_visual_elapsed + _max_single(0.0, delta)), 1.25)
		var jet_step: int = mini(_floor_to_i32(F.value(_jet_to_walker_visual_elapsed * 20.0)), 25)
		result = _set_virtual_frame(_jet, F.value(jet_step))
		if not result.ok: return result
		var cockpit_step: int = mini(_floor_to_i32(F.value(_jet_to_walker_visual_elapsed * 20.0)), 24)
		result = _set_virtual_frame(_cockpit, F.value(1.0 + F.value(cockpit_step)))
		if not result.ok: return result
		if _jet_to_walker_visual_elapsed >= Words.read_word(COCKPIT_FLY_TO_WALK_BITS):
			result = _set_virtual_frame(_cockpit, 25.0)
			if not result.ok: return result
		if _jet_to_walker_visual_elapsed >= 1.25:
			result = _set_virtual_frame(_jet, 25.0)
			if not result.ok: return result
			_jet_to_walker_visual_elapsed = INF
	elif snapshot.mode == 1:
		result = _set_virtual_frame(_jet, 0.0)
		if not result.ok: return result
		result = _set_virtual_frame(_cockpit, 0.0)
		if not result.ok: return result
	else:
		result = _set_virtual_frame(_jet, 25.0)
		if not result.ok: return result
		result = _set_virtual_frame(_cockpit, 25.0)
		if not result.ok: return result
	_previous_transition = snapshot.transition
	_previous_mode = snapshot.mode
	return {"ok": true}


func _set_virtual_frame(owner: Node3D, frame: float) -> Dictionary:
	return _aquila_error(_call_checked(owner, "set_virtual_frame", [frame], "Aquila"))


func _apply_walker_pose(contacts: Array, yaw: float) -> Dictionary:
	if contacts.size() != 4: return _failure("InvalidDataException", "Native Aquila contacts are incomplete.")
	var inverse: Dictionary = _inverse_yaw_basis(yaw)
	if not inverse.ok: return inverse
	var basis: Basis = inverse.value
	var local: Array[Vector3] = []
	for contact: Variant in contacts:
		if not contact is Dictionary or not _is_word(contact.get("x_bits")) or not _is_word(contact.get("y_bits")) or not _is_word(contact.get("z_bits")):
			return _failure("InvalidOperationException", "Native Aquila contact is missing its Single words.")
		var value: Vector3 = _vector(contact)
		local.append(Vector3(_sum3(basis.x.x, value.x, basis.y.x, value.y, basis.z.x, value.z),
			_sum3(basis.x.y, value.x, basis.y.y, value.y, basis.z.y, value.z),
			_sum3(basis.x.z, value.x, basis.y.z, value.y, basis.z.z, value.z)))
	return _aquila_error(_call_checked(_walker, "set_ground_contact_pose", [local], "Aquila"), "contactsInPlayerSpace")


func _update_camera(snapshot: Dictionary) -> Dictionary:
	_camera.position = _vector(snapshot.pose.position)
	var forward: Vector3 = _vector(snapshot.pose.forward)
	var up: Vector3 = _vector(snapshot.pose.up)
	# Preserve the existing local position supplied to global look_at. Trails
	# already used the previous node pose before this stage.
	_camera.look_at(_camera.position + forward, up)
	if not is_instance_valid(_sky): return _disposed("sky")
	_sky.position = _camera.position
	var sun: Dictionary = _call_checked(_sun, "update_camera", [_camera.position], "sun")
	if not sun.ok: return _remap(sun, [], "InvalidDataException")
	return apply_pixel_centre_offset(_world, _camera)


func _to_player_world(snapshot: Variant) -> Dictionary:
	if snapshot == null: return _null_reference()
	if not snapshot is Dictionary or not snapshot.get("player_position") is Dictionary:
		return _failure("ArgumentException", "Player position requires its Int32 record.")
	var position: Dictionary = snapshot.player_position
	if not _is_i32(position.get("x")) or not _is_i32(position.get("z")) or not _is_i32(snapshot.get("player_elevation_millimeters")):
		return _failure("ArgumentException", "Player position/elevation require Int32 fields.")
	var scale: float = Words.read_word(UNIT_SCALE_BITS)
	var x: float = F.value(F.value(position.x) * scale)
	var z: float = F.value(F.value(position.z) * scale)
	return {"ok": true, "value": Vector3(x, F.value(F.value(_wrap_i32(snapshot.player_elevation_millimeters - _walker_height_mm)) * scale), -z)}


static func _to_foot_offsets(snapshot: Dictionary) -> Dictionary:
	var feet: Variant = snapshot.get("feet")
	if feet == null: return _null_reference()
	if not feet is Array: return _failure("ArgumentException", "Aquila feet require their ordered Array.")
	if feet.size() != 4: return _failure("InvalidDataException", "Core did not expose four Aquila foot contacts.")
	var contacts: Array[Dictionary] = []
	for index: int in range(4): contacts.append(_vector_words(Vector3.ZERO))
	var scale: float = Words.read_word(UNIT_SCALE_BITS)
	for foot: Variant in feet:
		if foot == null: return _null_reference()
		if not foot is Dictionary or not _is_i32(foot.get("id")):
			return _failure("ArgumentException", "Aquila foot identity requires Int32.")
		if foot.id < 0 or foot.id >= contacts.size():
			return _failure("InvalidDataException", "Core exposed unknown Aquila foot %d." % foot.id)
		for key: String in ["x", "z", "ground_elevation_millimeters", "lift_millimeters"]:
			if not _is_i32(foot.get(key)): return _failure("ArgumentException", "Aquila foot requires Int32 " + key + ".")
		if not snapshot.get("player_position") is Dictionary or not _is_i32(snapshot.player_position.get("x")) \
				or not _is_i32(snapshot.player_position.get("z")) or not _is_i32(snapshot.get("player_ground_elevation_millimeters")):
			return _failure("ArgumentException", "Aquila foot offsets require the Int32 player ground position.")
		var x: int = _wrap_i32(foot.x - snapshot.player_position.x)
		var y: int = _wrap_i32(_wrap_i32(foot.ground_elevation_millimeters + foot.lift_millimeters) - snapshot.player_ground_elevation_millimeters)
		var z: int = _wrap_i32(-_wrap_i32(foot.z - snapshot.player_position.z))
		contacts[foot.id] = _vector_words(Vector3(F.value(F.value(x) * scale), F.value(F.value(y) * scale), F.value(F.value(z) * scale)))
	return {"ok": true, "value": contacts}


## Only the existing Y-axis Basis(...).Inverse() use is expanded here. Keep
## every Single product/sum, including zero terms and the adjugate division;
## substituting transpose/negative yaw changes finite rounding and NaN words.
static func _inverse_yaw_basis(yaw: float) -> Dictionary:
	var trig: Vector2 = Vector2.from_angle(F.value(yaw))
	var cosine: float = trig.x
	var sine: float = trig.y
	var zero_t: float = F.value(0.0 * F.value(1.0 - cosine))
	var zero_s: float = F.value(0.0 * sine)
	var diagonal: float = F.value(0.0 + F.value(cosine * 1.0))
	var m00: float = diagonal
	var m01: float = F.value(zero_t - zero_s)
	var m02: float = F.value(zero_t + F.value(1.0 * sine))
	var m10: float = F.value(zero_t + zero_s)
	var m11: float = F.value(1.0 + F.value(cosine * 0.0))
	var m12: float = F.value(zero_t - zero_s)
	var m20: float = F.value(zero_t - F.value(1.0 * sine))
	var m21: float = F.value(zero_t + zero_s)
	var m22: float = diagonal
	var c00: float = _minor(m11, m22, m12, m21)
	var c10: float = _minor(m12, m20, m10, m22)
	var c20: float = _minor(m10, m21, m11, m20)
	var determinant: float = _sum3(m00, c00, m01, c10, m02, c20)
	if determinant == 0.0:
		return _failure("InvalidOperationException", "Matrix determinant is zero and cannot be inverted.")
	var reciprocal: float = F.value(1.0 / determinant)
	return {"ok": true, "value": Basis(
		Vector3(F.value(c00 * reciprocal), F.value(c10 * reciprocal), F.value(c20 * reciprocal)),
		Vector3(F.value(_minor(m02, m21, m01, m22) * reciprocal), F.value(_minor(m00, m22, m02, m20) * reciprocal), F.value(_minor(m01, m20, m00, m21) * reciprocal)),
		Vector3(F.value(_minor(m01, m12, m02, m11) * reciprocal), F.value(_minor(m02, m10, m00, m12) * reciprocal), F.value(_minor(m00, m11, m01, m10) * reciprocal)))}


static func _minor(a: float, b: float, c: float, d: float) -> float:
	return F.value(F.value(a * b) - F.value(c * d))


static func _sum3(ax: float, bx: float, ay: float, by: float, az: float, bz: float) -> float:
	return F.value(F.value(F.value(ax * bx) + F.value(ay * by)) + F.value(az * bz))


static func _distance_squared(before: Vector3, after: Vector3) -> float:
	var x: float = F.value(before.x - after.x)
	var y: float = F.value(before.y - after.y)
	var z: float = F.value(before.z - after.z)
	return _sum3(x, x, y, y, z, z)


static func _lerp_vector(before: Vector3, after: Vector3, alpha: float) -> Vector3:
	return Vector3(_lerp_single(before.x, after.x, alpha), _lerp_single(before.y, after.y, alpha), _lerp_single(before.z, after.z, alpha))


static func _lerp_single(before: float, after: float, alpha: float) -> float:
	return F.value(before + F.value(F.value(after - before) * alpha))


static func _lerp_angle(before: float, after: float, alpha: float) -> float:
	# Mathf.AngleDifference uses signed remainder twice; fposmod/lerp_angle's
	# different half-turn branch is not the source operation.
	var tau: float = Words.read_word(TAU_BITS)
	var difference: float = F.value(fmod(F.value(after - before), tau))
	var angle: float = F.value(F.value(fmod(F.value(2.0 * difference), tau)) - difference)
	return F.value(before + F.value(angle * alpha))


static func _max_single(left: float, right: float) -> float:
	if is_nan(left): return left
	if is_nan(right): return right
	if left != right: return left if left > right else right
	return right if (Words.store_word(right) & 0x80000000) == 0 else left


static func _min_single(left: float, right: float) -> float:
	if is_nan(left): return left
	if is_nan(right): return right
	if left != right: return left if left < right else right
	return right if (Words.store_word(right) & 0x80000000) != 0 else left


static func _floor_to_i32(value: float) -> int:
	# Current GodotSharp/.NET admission, also pinned by the Aquila leaf oracle.
	if is_nan(value): return 0
	if value >= 2147483647.0: return 2147483647
	if value <= -2147483648.0: return -2147483648
	return int(floor(value))


static func _wrap_i32(value: int) -> int:
	var low: int = value & 0xffffffff
	return low - 0x100000000 if low >= 0x80000000 else low


static func _is_i32(value: Variant) -> bool:
	return value is int and value >= -2147483648 and value <= 2147483647


static func _is_word(value: Variant) -> bool:
	return value is int and value >= 0 and value <= 0xffffffff


static func _vector(value: Dictionary) -> Vector3:
	return Vector3(Words.read_word(value.x_bits), Words.read_word(value.y_bits), Words.read_word(value.z_bits))


static func _vector_words(value: Vector3) -> Dictionary:
	return {"x_bits": Words.store_word(value.x), "y_bits": Words.store_word(value.y), "z_bits": Words.store_word(value.z)}


static func _call_checked(owner: Object, method: StringName, arguments: Array, label: String) -> Dictionary:
	if not is_instance_valid(owner): return _disposed(label)
	if not owner.has_method(method): return _failure("InvalidOperationException", "Native " + label + " lacks its production operation " + str(method) + ".")
	return _checked(owner.callv(method, arguments), label)


static func _checked(value: Variant, label: String) -> Dictionary:
	if not value is Dictionary or typeof(value.get("ok")) != TYPE_BOOL:
		return _failure("InvalidOperationException", "Native " + label + " aborted without a completion result.")
	if not value.ok and (not value.get("error_type") is String or not value.get("error") is String):
		return _failure("InvalidOperationException", "Native " + label + " returned an incomplete failure.")
	return value


static func _camera_error(result: Dictionary) -> Dictionary:
	return _remap(result, ["ArgumentNullException", "ArgumentOutOfRangeException", "ArgumentException", "OverflowException"], "InvalidOperationException", true)


static func _entity_error(result: Dictionary) -> Dictionary:
	return _remap(result, ["InvalidDataException", "ArgumentOutOfRangeException", "ArgumentNullException", "ArgumentException"], "InvalidOperationException")


static func _aquila_error(result: Dictionary, parameter: String = "") -> Dictionary:
	if result.ok: return result
	var mapped: Dictionary = _remap(result, ["ArgumentNullException", "ArgumentException", "IndexOutOfRangeException", "InvalidOperationException"], "InvalidDataException")
	var suffix: String = " (Parameter '" + parameter + "')"
	if not parameter.is_empty() and str(mapped.error).ends_with(suffix) and mapped.error_type in ["ArgumentNullException", "ArgumentException"]:
		mapped.error = str(mapped.error).trim_suffix(suffix)
		mapped.parameter = parameter
	return mapped


static func _remap(result: Dictionary, preserved: Array, otherwise: String, retain_parameter: bool = false) -> Dictionary:
	if result.ok: return result
	var mapped: Dictionary = result.duplicate(true)
	if not mapped.error_type in preserved: mapped.error_type = otherwise
	if not retain_parameter: mapped.erase("parameter")
	return mapped


static func _disposed(label: String) -> Dictionary:
	return _failure("ObjectDisposedException", "The world presentation " + label + " has been disposed.")


static func _null_reference() -> Dictionary:
	return _failure("NullReferenceException", "Object reference not set to an instance of an object.")


static func _failure(kind: String, message: String, parameter: String = "") -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message, "parameter": parameter}


func _failed(error: Dictionary) -> Dictionary:
	var result: Dictionary = error.duplicate(true)
	result.merge(host_snapshot(), true)
	return result


func _success() -> Dictionary:
	var result: Dictionary = host_snapshot()
	result.ok = true
	return result
