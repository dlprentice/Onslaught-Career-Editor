# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## The production frame controller (world_presentation.gd) in the real imported
## Level 100 world, against the retained 1bb29345 C# controller arithmetic that
## WorldPresentationChecks.cs carried until its retirement, ported below as an
## explicit Single-precision oracle: player position/attitude, the ten-metre
## reset, Aquila transition clocks and shape, camera size/pose/half-pixel
## offset, sky follow, particle clock, weapon muzzle queue, failure order and
## partial frames, nonfinite transition math and a disposed scenery setter.
## The camera and viewpoint laws themselves are pinned by the camera parity
## goldens; here a second owner proves the controller's composition.
## Needs the .NET engine (the simulation bridge) and a current import:
##   godot48-mono --headless --audio-driver Dummy --path <project> --script res://Tests/world_presentation_checks.gd
const Import = preload("res://Scenes/World/level100_scene_import.gd")
const StaticWorld = preload("res://Scenes/World/level100_static_world.gd")
const Presentation = preload("res://Scenes/World/world_presentation.gd")
const CameraState = preload("res://Client/world_camera.gd")
const Attached = preload("res://Client/attached_pan_camera.gd")
const Viewpoint = preload("res://Client/level100_engine_viewpoint.gd")
const Interpolation = preload("res://Client/render_interpolation.gd")
const F = preload("res://Scenes/Shared/retail_float32.gd")
const Words = preload("res://Core/retail_float24.gd")
const BRIDGE_SCRIPT_PATH: String = "res://Bridge/SimulationBridge.cs"
const SIMULATION_SEED: int = 0x4F4E534C
const SCALE_BITS: int = 0x3a83126f # 0.001f
const WALKER: int = 0
const JET: int = 1
const NONE: int = 0
const WALKER_TO_JET: int = 1
const JET_TO_WALKER: int = 2
const I32_MIN: int = -2147483648
const I32_MAX: int = 2147483647

var _checks: int = 0
var _failure: String = ""
var _completed: Array[String] = []
var _viewport: SubViewport
var _world: Node3D
var _owner: Node
var _oracle: Oracle


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var manifest: Dictionary = StaticWorld.load_manifest_bytes()
	var bridge: RefCounted = (load(BRIDGE_SCRIPT_PATH) as Script).new()
	if not _check(manifest.ok and bridge.Start(SIMULATION_SEED, manifest.value).ok, "The Level 100 simulation starts."):
		return _finish()
	var source_hash: String = bridge.GetStateHash().value
	var pointer: int = Input.mouse_mode
	if not _check(Import.verify_current_import(bridge).ok, "The prepared private world matches its receipt."):
		return _finish()
	_viewport = SubViewport.new()
	_viewport.size = Vector2i(640, 480)
	_viewport.own_world_3d = true
	_viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	root.add_child(_viewport)
	_world = (load(Import.PRODUCTION_SCENE_PATH) as PackedScene).instantiate()
	_owner = _world.get_node("WorldPresentation")
	var entities: Node = _world.get_node("EntityPresentation")
	var poses: Array = [Pose.capture(_world), Pose.capture(_world.get_node("PlayerVisual")),
		Pose.capture(_world.get_node("PlayerVisual/BodyPivot")), Pose.capture(_world.get_node("RetailOpeningAndFirstPersonCamera"))]
	var authored_player: Transform3D = poses[1].transform
	_check(_owner.get("_camera_state") == null and not _owner.is_processing() and not _owner.is_processing_input(),
		"The authored world controller is passive before explicit initialization.")
	_viewport.add_child(_world)
	await process_frame
	_check(_owner.get("_camera_state") == null and (_world.get_node("PlayerVisual") as Node3D).transform == authored_player,
		"Tree entry starts no second simulation and keeps the authored pose.")
	var initialized: Dictionary = _world.initialize(bridge)
	if not _check(initialized.ok, "The production world binds: " + String(initialized.get("error", ""))):
		return _finish()
	var config: Dictionary = bridge.WorldConfigFacts().value
	var basis: Dictionary = bridge.WorldFrameFacts(0.0, 0.0).value.current
	_oracle = Oracle.new(_world, _viewport, poses, config)
	_oracle.render(basis, basis, true, 0.0, 0.0, 480.0)
	var camera_owner: Object = _owner.get("_camera_state")
	_check(camera_owner is Object and _owner.get("_entities") == entities,
		"The authored controller borrows the entity component and owns one camera state.")
	_compare("initialization")
	_done("authored_owner_and_initialization")

	var prior: Dictionary = basis
	var tick: int = 1
	for row: Array in [[WALKER, NONE, -1.0], [WALKER, WALKER_TO_JET, 0.0], [WALKER, WALKER_TO_JET, _next_down(0.05)],
			[WALKER, WALKER_TO_JET, F.value(F.value(0.05) - _next_down(0.05))], [WALKER, WALKER_TO_JET, 0.05], [JET, NONE, 1.05],
			[JET, NONE, 0.1], [JET, JET_TO_WALKER, 0.0], [JET, JET_TO_WALKER, 1.2], [JET, JET_TO_WALKER, 0.05],
			[WALKER, NONE, 0.0], [WALKER, WALKER_TO_JET, 0.05], [JET, JET_TO_WALKER, 0.05], [WALKER, NONE, 0.0]]:
		var current: Dictionary = _with(basis, {"tick": tick, "opening_ticks_remaining": maxi(0, 120 - tick),
			"mode": row[0], "transition": row[1], "facing_yaw_micro_rad": basis.facing_yaw_micro_rad + tick * 37000,
			"facing_pitch_micro_rad": tick * -9001, "body_roll_micro_rad": tick * 7003})
		_render_pair(prior, current, false, 0.375, F.value(row[2]), "row %d" % tick)
		prior = current
		tick += 1
	# The strict ten-metre reset and the reference/count gates are old source
	# decisions, not reconstructed from the native controller.
	for distance: int in [10_000, 10_001]:
		var shifted: Dictionary = _with(_shift(basis, distance), {"tick": tick, "opening_ticks_remaining": 0})
		tick += 1
		_render_pair(basis, shifted, false, 0.25, 0.0, "shift %d" % distance)
		prior = shifted
	_render_pair(prior, prior, true, 0.5, 0.0, "same snapshot")
	_render_pair(_with(prior, {"feet": []}), prior, false, 0.5, 0.0, "previous feet absent")
	var reset: Dictionary = _with(_shift(prior, 25_000), {"tick": tick})
	tick += 1
	_render_pair(_with(prior, {"feet": null}), reset, false, 0.5, 0.0, "reset skips previous feet")
	var boundary: Dictionary = _with(basis, {"tick": tick, "opening_ticks_remaining": 0,
		"player_position": {"x": I32_MIN, "z": I32_MAX}, "player_elevation_millimeters": I32_MIN,
		"facing_yaw_micro_rad": I32_MAX, "facing_pitch_micro_rad": I32_MIN, "body_roll_micro_rad": I32_MAX})
	tick += 1
	_render_pair(boundary, boundary, true, 0.0, 0.0, "Int32 boundary")
	_viewport.size = Vector2i(801, 601)
	prior = _with(basis, {"tick": 1, "opening_ticks_remaining": 119, "mode": JET, "zoom_permille": 400})
	_render_pair(reset, prior, false, 1.0, 0.0, "tick reset and resize")
	_check(_owner.get("_camera_state") == camera_owner and _owner.get("_entities") == entities,
		"Tick reset and projection resize retain the original owners.")
	_done("player_aquila_camera_and_gates")

	_partial_failure(prior)
	_done("partial_failure_and_detached_facts")
	_collection_failures(prior)
	_done("deferred_projection_and_projectile_failure_boundary")
	_nonfinite_transition(prior)
	_done("isolated_nonfinite_transition_math")
	# The disposed-scenery frame follows the camera rows' own history.
	var last_camera_frame: Dictionary = _camera_owner(basis)
	_done("camera_owner_attachment_and_tree_lifecycle")
	_disposed_scenery(last_camera_frame)
	_done("disposed_scenery_exception_and_partial_frame")
	_check(bridge.GetStateHash().value == source_hash and Input.mouse_mode == pointer,
		"Presentation leaves the deterministic source state and pointer ownership unchanged.")
	_oracle.free_nodes()
	_viewport.queue_free()
	await process_frame
	_finish()


func _render_pair(previous: Dictionary, current: Dictionary, same: bool, alpha: float, delta: float, label: String) -> void:
	var before: Dictionary = current.duplicate(true)
	var expected: Dictionary = _oracle.render(previous, current, same, alpha, delta, float(_viewport.size.y))
	var actual: Dictionary = _render(previous, current, same, alpha, delta)
	_check(expected.ok and actual.ok, label + ": both controllers render: " + str(expected.get("error", "")) + " " + str(actual.get("error", "")))
	_compare(label)
	_check(current == before, label + ": rendering never writes the supplied snapshot facts.")


func _partial_failure(basis: Dictionary) -> void:
	_check(_owner.queue_weapon_events([1, 1]).ok, "Pulse fire events queue muzzles.")
	_check(_owner.host_snapshot().pending_muzzles == 2, "Each pulse fire event adds one native pending muzzle regardless of volley size.")
	var bad: Dictionary = _with(_shift(basis, 2000), {"tick": basis.tick + 1, "feet": basis.feet.slice(0, 3)})
	var before_camera: String = _owner.get("_camera_state").camera_hash().hex
	var expected: Dictionary = _oracle.render(basis, bad, false, 0.5, 0.125, float(_viewport.size.y))
	var actual: Dictionary = _render(basis, bad, false, 0.5, 0.125)
	_check(not expected.ok and expected.error_type == "InvalidDataException", "Retained foot-count failure.")
	_check(not actual.ok and actual.error_type == "InvalidDataException" and actual.error == expected.error,
		"The native controller refuses at the original foot stage.")
	_compare("partial frame")
	var partial: Dictionary = _owner.host_snapshot()
	_check(partial.pending_muzzles == 2 and _owner.get("_camera_state").camera_hash().hex == before_camera,
		"Failed feet leave pending muzzles and camera untouched after particle/player mutation.")
	partial.pending_muzzles = 999
	partial.particle_seconds_bits = 0
	partial.show_hud = not _oracle.show_hud
	var detached: Dictionary = _owner.host_snapshot()
	_check(detached.pending_muzzles == 2 and detached.particle_seconds_bits == Words.store_word(_oracle.particle_seconds),
		"Host facts are detached observations of the one native owner.")
	_render_pair(basis, _with(basis, {"tick": bad.tick + 1}), false, 0.5, 0.0, "recovered")
	_check(_owner.host_snapshot().pending_muzzles == 0, "A later successful frame consumes the preserved muzzle queue.")


func _collection_failures(basis: Dictionary) -> void:
	var moved: Dictionary = _with(_shift(basis, 3000), {"tick": basis.tick + 10,
		"facing_yaw_micro_rad": basis.facing_yaw_micro_rad + 210000, "mode": WALKER, "transition": WALKER_TO_JET})
	for foot: Dictionary in moved.feet:
		foot.lift_millimeters += 125
	var projection_failure: Dictionary = {"ok": false, "error_type": "InvalidDataException",
		"error": "Level 100 target definition name is missing.", "host_exception_id": 0}
	var invalid_target: Dictionary = _with(moved, {"targets": projection_failure})
	var null_projectile: Dictionary = _with(moved, {"projectiles": [null]})
	var invalid_foot_and_target: Dictionary = _with(invalid_target, {})
	invalid_foot_and_target.feet[0].id = 99
	_check(_owner.queue_weapon_events([1]).ok, "One pulse muzzle is queued before the collection failures.")
	for case: Array in [["current computed target projection", basis, invalid_target, "InvalidDataException", projection_failure.error],
			["previous computed target projection", invalid_target, moved, "InvalidDataException", projection_failure.error],
			["current null projectile row", basis, null_projectile, "NullReferenceException", ""],
			["previous null projectile row", null_projectile, moved, "NullReferenceException", ""],
			["target failure precedes previous projectile failure", null_projectile, invalid_target, "InvalidDataException", projection_failure.error],
			["pure feet failure precedes computed target failure", basis, invalid_foot_and_target, "InvalidDataException", "Core exposed unknown Aquila foot 99."]]:
		var label: String = case[0]
		var camera: RefCounted = _owner.get("_camera_state")
		var before_camera: String = camera.camera_hash().hex
		var before_viewpoint: String = camera.viewpoint_hash().hex
		var before_player: Transform3D = (_world.get_node("PlayerVisual") as Node3D).transform
		var expected: Dictionary = _oracle.render(case[1], case[2], false, 0.375, 0.125, float(_viewport.size.y))
		_check(not expected.ok and expected.error_type == case[3] and (String(case[4]).is_empty() or expected.error == case[4]),
			label + ": the retained controller reaches the intended failure.")
		var actual: Dictionary = _render(case[1], case[2], false, 0.375, 0.125)
		_check(not actual.ok and actual.error_type == case[3], label + ": the exact failure type survives.")
		if case[3] == "InvalidDataException":
			_check(actual.error == case[4], label + ": the original projection or foot message is retained.")
		_compare(label)
		_check(camera.camera_hash().hex == before_camera and camera.viewpoint_hash().hex == before_viewpoint,
			label + ": collection admission happens before camera-state and viewpoint writes.")
		_check(_owner.host_snapshot().pending_muzzles == 1,
			label + ": failed collection transport never reaches the entity callback or consumes a muzzle.")
		if label == "current computed target projection":
			_check((_world.get_node("PlayerVisual") as Node3D).transform != before_player,
				"Deferred target failure follows the player transform writes.")
	_render_pair(basis, _with(basis, {"tick": moved.tick + 1}), false, 0.375, 0.0, "after collection failures")
	_check(_owner.host_snapshot().pending_muzzles == 0, "A later successful frame consumes the preserved muzzle.")


# The transition stage itself, so nonfinite deltas never reach terrain, water
# or a camera/player geometry setter.
func _nonfinite_transition(basis: Dictionary) -> void:
	for row: Array in [[WALKER, WALKER_TO_JET, _single(0xffc00000)], [WALKER, WALKER_TO_JET, 0.0], [JET, JET_TO_WALKER, INF],
			[WALKER, NONE, -INF], [WALKER, WALKER_TO_JET, -0.0], [WALKER, WALKER_TO_JET, _single(0x7f7fffff)]]:
		var facts: Dictionary = {"mode": row[0], "transition": row[1]}
		_oracle.transition(facts, row[2])
		var result: Dictionary = _owner.call("_update_aquila_transition_presentation", facts, row[2])
		_check(result.ok, "Nonfinite transition math completes: %s" % [row])
		_compare_transition("nonfinite %s" % [row])


# CameraBridgeChecks' contracts: the composed owner is lazy and word-exact for
# every depth word, refuses in the original order, ignores a malformed previous
# frame when the current frame repeats, matches Player 1 by its exact eight
# UTF-16 units, and survives the world leaving and re-entering the tree.
func _camera_owner(basis: Dictionary) -> Dictionary:
	for word: int in [0, 0x80000000, 1, 0x80000001, 0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000,
			0x7fc00000, 0xffc00001, 0x7f800001, 0xff800001]:
		var owner: RefCounted = CameraState.new()
		_check(owner.camera_hash().get("error_type") == "InvalidOperationException", "An unconfigured camera owner refuses reads.")
		_check(owner.configure(120, 1, word, word).ok, "Configuration admits raw depth word %08x." % word)
		var engine: RefCounted = Viewpoint.create(word, word).value
		_check(owner.selected_snapshot().value == engine.selected_snapshot() and owner.viewpoint_hash().hex == engine.compute_hash().hex,
			"Raw depth word %08x survives the composed owner." % word)
		_check(owner.current_snapshot().get("error_type") == "InvalidOperationException", "The camera starts without an event frame.")
		_check(owner.sample_and_bind(0xffc00000).get("error_type") == "ArgumentOutOfRangeException", "A NaN alpha is refused before the missing frame.")
		_check(owner.sample_and_bind(0).get("error_type") == "InvalidOperationException", "A valid sample requires an event frame.")
		_check(owner.configure(120, 1, word, word).get("error_type") == "InvalidOperationException", "The owner configures once.")
	var owner: RefCounted = CameraState.new()
	owner.configure(120, 1, Words.store_word(0.1), Words.store_word(700.0))
	var reference: RefCounted = Attached.create(120, 1).value
	var engine: RefCounted = Viewpoint.create(Words.store_word(0.1), Words.store_word(700.0)).value
	var previous: Dictionary = basis
	for index: int in 16:
		var current: Dictionary = _with(basis, {"tick": index + 1, "opening_ticks_remaining": 119 - index,
			"facing_yaw_micro_rad": Oracle.wrap_i32(I32_MAX - index * 100000001), "facing_pitch_micro_rad": I32_MIN + index,
			"body_roll_micro_rad": -1000000 * index, "player_position": {"x": I32_MIN if index == 0 else I32_MAX - index, "z": I32_MIN},
			"player_elevation_millimeters": I32_MAX - index})
		owner.advance(previous, current)
		reference.advance(previous, current)
		_check(owner.camera_hash().hex == Attached.compute_hash(reference.current_snapshot().value).hex,
			"Int32 boundary facts keep exact camera hashes through the composed owner.")
		for alpha: float in [-0.0, 0.25, 0.5, 1.0]:
			var bound: Dictionary = owner.sample_and_bind(Words.store_word(alpha)).value
			var expected: Dictionary = reference.sample(Words.store_word(alpha)).value
			_check(bound.camera == expected and bound.viewpoint == engine.bind(expected).value
				and owner.viewpoint_hash().hex == engine.compute_hash().hex, "Sampling and slot binding share one operation.")
		previous = current
	var before: String = owner.camera_hash().hex
	owner.advance(_with(previous, {"actors": null, "opening_ticks_remaining": I32_MIN}), previous)
	_check(owner.camera_hash().hex == before, "A repeated current frame ignores a malformed previous frame.")
	_check(owner.advance(null, previous).get("error_type") == "ArgumentNullException", "A null previous frame is refused even for a repeat.")
	_check(owner.sample_and_bind(0x3f800001).get("error_type") == "ArgumentOutOfRangeException", "An alpha above one is refused.")
	_check(owner.camera_hash().hex == before, "Refused samples and frames preserve the camera state.")
	var player: PackedInt32Array = PackedInt32Array([80, 108, 97, 121, 101, 114, 32, 49])
	var renamed: Array = []
	for actor: Dictionary in basis.actors:
		var row: Dictionary = actor.duplicate(true)
		if PackedInt32Array(row.name) == player:
			var units: PackedInt32Array = player.duplicate()
			units.append_array(PackedInt32Array([0, 105, 103, 110, 111, 114, 101, 100, 0xD800]))
			row.name = units
		renamed.append(row)
	var not_player: Dictionary = _with(basis, {"tick": 119, "opening_ticks_remaining": 1, "actors": renamed})
	owner.advance(previous, not_player)
	reference.advance(previous, not_player)
	_check(owner.camera_hash().hex == Attached.compute_hash(reference.current_snapshot().value).hex
		and owner.current_snapshot().value.current_frame.attached_thing == null,
		"A name that only begins with Player 1 never attaches the camera: exact eight-unit equality.")
	_check(owner.sample_and_bind(Words.store_word(1.0)).value.camera == reference.sample(Words.store_word(1.0)).value,
		"The unattached sample matches the direct owner.")

	# The production consumer through handoff, detachment and a teleport.
	previous = basis
	for row: Array in [[1, 119, 100, 1000, true, WALKER], [60, 60, 200, 900, true, WALKER], [118, 2, 300, 800, true, WALKER],
			[119, 1, 400, 600, true, WALKER], [120, 0, 500, 400, true, JET], [121, 0, 25_000, 700, true, JET],
			[122, 0, 25_100, 800, false, JET], [123, 0, 25_200, 900, true, WALKER], [1, 119, 0, 1000, true, WALKER]]:
		var actors: Array = []
		for actor: Dictionary in basis.actors:
			if row[4] or PackedInt32Array(actor.name) != player:
				actors.append(actor.duplicate(true))
		var current: Dictionary = _with(basis, {"tick": row[0], "opening_ticks_remaining": row[1],
			"player_position": {"x": basis.player_position.x + row[2], "z": basis.player_position.z},
			"facing_yaw_micro_rad": basis.facing_yaw_micro_rad + 11000 * row[0], "facing_pitch_micro_rad": row[0] * 230,
			"body_roll_micro_rad": row[0] * -170, "zoom_permille": row[3], "mode": row[5], "transition": NONE, "actors": actors})
		for alpha: float in [0.0, 0.5, 1.0]:
			_render_pair(previous, current, false, alpha, 0.0, "camera row %d alpha %s" % [row[0], alpha])
		previous = current
	var retained: String = _owner.get("_camera_state").camera_hash().hex
	var camera: Camera3D = _world.get_node("RetailOpeningAndFirstPersonCamera")
	_viewport.remove_child(_world)
	_check(_owner.get("_camera_state").camera_hash().hex == retained, "Leaving the tree keeps the camera lifecycle.")
	_viewport.add_child(_world)
	_check(_owner.get("_camera_state").camera_hash().hex == retained and _world.get_node("RetailOpeningAndFirstPersonCamera") == camera,
		"Re-entering the tree keeps the same camera state and the authored Camera3D.")
	return previous


func _disposed_scenery(basis: Dictionary) -> void:
	var scenery: RefCounted = _owner.get("_scenery")
	var bindings: Array = scenery.get("_bindings")
	var before: Dictionary = scenery.host_snapshot()
	var shown: PackedInt32Array = before.shown_frames
	var fps: int = before.frames_per_second
	var lap: int = 1
	var selected: int = -1
	var selected_loop: int = 0
	var selected_node: MeshInstance3D = null
	for index: int in bindings.size():
		var mesh: Dictionary = bindings[index].mesh
		var loop: int = mesh.loop_frame_count
		if loop > 0:
			var a: int = lap
			var b: int = loop
			while b != 0:
				var remainder: int = a % b
				a = b
				b = remainder
			@warning_ignore("integer_division")
			lap = lap / a * loop
		if selected < 0 and loop > 1 and mesh.playback == 0:
			selected = index
			selected_loop = loop
			selected_node = bindings[index].node
	if not _check(selected >= 0 and selected_node != null, "The production scenery includes a borrowed looping mesh."):
		return
	var delta: float = _single(0x3d50e560) # 0.051f
	var bytes := PackedByteArray()
	bytes.resize(8)
	bytes.encode_s64(0, before.elapsed_seconds_bits)
	var elapsed: float = bytes.decode_double(0) + delta
	var period: float = float(lap) / float(fps)
	if period > 0.0 and elapsed >= period:
		elapsed = fmod(elapsed, period)
	var frame: int = 0
	var frames: float = floor(elapsed * fps)
	if is_finite(elapsed) and elapsed > 0.0 and frames > 0.0:
		frame = int(frames) % selected_loop
	_check(frame != shown[selected], "The disposal probe selects a different frame, so it cannot pass by skipping the setter.")
	selected_node.free()
	var current: Dictionary = _with(basis, {"tick": basis.tick + 20, "mode": WALKER, "transition": NONE})
	var expected: Dictionary = _oracle.render(basis, current, false, 0.25, delta, float(_viewport.size.y))
	var actual: Dictionary = _render(basis, current, false, 0.25, delta)
	_check(expected.ok and not actual.ok and actual.error_type == "ObjectDisposedException",
		"The scenery setter's exact ObjectDisposedException follows every earlier frame stage.")
	_compare("disposed scenery")
	var after: Dictionary = scenery.host_snapshot()
	bytes.encode_double(0, elapsed)
	_check(after.elapsed_seconds_bits == bytes.decode_s64(0) and after.shown_frames[selected] == frame,
		"The failed scenery setter keeps the double clock and shown-frame writes.")
	for index: int in range(selected + 1, shown.size()):
		_check(after.shown_frames[index] == shown[index], "A failed scenery setter leaves later binding frames unchanged.")


func _compare(label: String) -> void:
	_compare_transform(_world.get_node("PlayerVisual").transform, _oracle.player.transform, label + " player")
	_compare_transform(_world.get_node("PlayerVisual/BodyPivot").transform, _oracle.body.transform, label + " body")
	var camera: Camera3D = _world.get_node("RetailOpeningAndFirstPersonCamera")
	_compare_transform(camera.transform, _oracle.camera.transform, label + " camera")
	_check(Words.store_word(camera.size) == Words.store_word(_oracle.camera.size) and camera.frustum_offset == _oracle.camera.frustum_offset
		and Words.store_word(camera.near) == Words.store_word(_oracle.camera.near) and Words.store_word(camera.far) == Words.store_word(_oracle.camera.far),
		label + ": projection size, raw depths and half-pixel offset retain the C# operation order.")
	_compare_vector((_world.get_node("RetailLevel100KempyCube25") as Node3D).position, _oracle.camera.position, label + " sky follows camera")
	var camera_state: RefCounted = _owner.get("_camera_state")
	_check(camera_state.camera_hash().hex == _oracle.camera_state.camera_hash().hex
		and camera_state.viewpoint_hash().hex == _oracle.camera_state.viewpoint_hash().hex,
		label + ": the controller composes the camera and viewpoint owners exactly.")
	var facts: Dictionary = _owner.host_snapshot()
	_check(facts.particle_seconds_bits == Words.store_word(_oracle.particle_seconds) and facts.show_hud == _oracle.show_hud
		and facts.opening_pan == _oracle.opening_pan, label + ": native clocks and display gates match the retained controller.")
	_check(_world.show_hud == facts.show_hud and _world.opening_pan_active == facts.opening_pan
		and _world.presentation_facts().target_visual_count == facts.target_count,
		label + ": the world root exposes detached gates and counts, not another presentation owner.")
	_compare_tree(_world.get_node("PlayerVisual/BodyPivot/RetailAquilaWalker"), _oracle.walker, label)
	_compare_transition(label)


func _compare_transition(label: String) -> void:
	_check(Words.store_word(_owner.get("_walker_to_jet_visual_elapsed")) == Words.store_word(_oracle.walker_elapsed)
		and Words.store_word(_owner.get("_jet_to_walker_visual_elapsed")) == Words.store_word(_oracle.jet_elapsed),
		label + ": Aquila transition clocks retain exact Single words.")
	_check(_owner.get("_previous_transition") == _oracle.previous_transition and _owner.get("_previous_mode") == _oracle.previous_mode,
		label + ": transition edge memory matches the retained controller.")
	_compare_tree(_owner.get("_jet"), _oracle.jet, label)
	_compare_tree(_owner.get("_cockpit"), _oracle.cockpit, label)


func _compare_tree(actual: Node3D, expected: Node3D, label: String) -> void:
	_compare_transform(actual.transform, expected.transform, label + " " + String(actual.name))
	_check(actual.visible == expected.visible, label + ": Aquila visibility retains the source gate: " + String(actual.name))
	for child: Node in expected.get_children():
		if child is Node3D:
			_compare_tree(actual.get_node(NodePath(String(child.name))), child, label)


func _compare_transform(actual: Transform3D, expected: Transform3D, label: String) -> void:
	_compare_vector(actual.origin, expected.origin, label + " origin")
	_compare_vector(actual.basis.x, expected.basis.x, label + " X")
	_compare_vector(actual.basis.y, expected.basis.y, label + " Y")
	_compare_vector(actual.basis.z, expected.basis.z, label + " Z")


func _compare_vector(actual: Vector3, expected: Vector3, label: String) -> void:
	for axis: int in 3:
		_check(Words.store_word(actual[axis]) == Words.store_word(expected[axis]),
			"%s[%d]: %08x != %08x" % [label, axis, Words.store_word(actual[axis]), Words.store_word(expected[axis])])


# The production root's render path without the bridge: the controller frame,
# then the root's detached gates and its projection-failure token mapping.
func _render(previous: Dictionary, current: Dictionary, same: bool, alpha: float, delta: float) -> Dictionary:
	var batch: Dictionary = _batch(previous, current, same, alpha, delta)
	return _world._presentation_result(_owner.render_frame(batch), batch)


static func _batch(previous: Dictionary, current: Dictionary, same: bool, alpha: float, delta: float) -> Dictionary:
	return {"previous": previous, "current": current, "same_snapshot": same,
		"alpha_bits": Words.store_word(alpha), "delta_bits": Words.store_word(delta)}


static func _with(source: Dictionary, overrides: Dictionary) -> Dictionary:
	var copy: Dictionary = source.duplicate(true)
	for key: Variant in overrides:
		copy[key] = overrides[key]
	return copy


static func _shift(source: Dictionary, x: int) -> Dictionary:
	var copy: Dictionary = source.duplicate(true)
	copy.player_position.x += x
	for foot: Dictionary in copy.feet:
		foot.x += x
	return copy


static func _single(bits: int) -> float:
	return Words.read_word(bits)


static func _next_down(value: float) -> float:
	return Words.read_word(Words.store_word(F.value(value)) - 1)


func _check(condition: bool, message: String) -> bool:
	if not _failure.is_empty():
		return false
	if not condition:
		_failure = message
		return false
	_checks += 1
	return true


func _done(group: String) -> void:
	if _failure.is_empty():
		_completed.append(group)


func _finish() -> void:
	if not _failure.is_empty():
		push_error("WORLD_PRESENTATION_CHECKS failed after %d checks: %s" % [_checks, _failure])
		quit(1)
		return
	print("WORLD_PRESENTATION_CHECKS: %d passed; completed=%s; retained controller arithmetic, production native owners." % [_checks, ",".join(_completed)])
	quit(0)


## A node's packed state, applied to the oracle's own nodes so both controllers
## start from the same authored pose (a serialized rotation can carry a scale
## one ULP below one).
class Pose extends RefCounted:
	var transform: Transform3D
	var rotation_order: int
	var top_level: bool
	var disable_scale: bool

	static func capture(node: Node3D) -> Pose:
		var pose := Pose.new()
		pose.transform = node.transform
		pose.rotation_order = node.rotation_order
		pose.top_level = node.top_level
		pose.disable_scale = node.is_scale_disabled()
		return pose

	func apply(node: Node3D) -> void:
		node.rotation_order = rotation_order
		node.top_level = top_level
		node.set_disable_scale(disable_scale)
		node.transform = transform


## The retained 1bb29345 FirstFlightWorldView controller arithmetic (Single
## stores, .NET Min/Max and LerpAngle), on duplicated Aquila leaves.
class Oracle extends RefCounted:
	var root := Node3D.new()
	var player := Node3D.new()
	var body := Node3D.new()
	var camera := Camera3D.new()
	var walker: Node3D
	var jet: Node3D
	var cockpit: Node3D
	var camera_state: RefCounted = CameraState.new()
	var particle_seconds: float = 0.0
	var walker_elapsed: float = INF
	var jet_elapsed: float = INF
	var previous_transition: int = 0
	var previous_mode: int = 0
	var show_hud: bool = false
	var opening_pan: bool = false

	func _init(world: Node3D, viewport: SubViewport, poses: Array, config: Dictionary) -> void:
		camera.near = 0.1
		camera.far = 700.0
		camera.projection = Camera3D.PROJECTION_FRUSTUM
		camera.current = false
		poses[0].apply(root)
		poses[1].apply(player)
		poses[2].apply(body)
		poses[3].apply(camera)
		walker = _leaf(world.get_node("PlayerVisual/BodyPivot/RetailAquilaWalker"))
		jet = _leaf(world.get_node("PlayerVisual/BodyPivot/RetailAquilaJet"))
		cockpit = _leaf(world.get_node("RetailOpeningAndFirstPersonCamera/RetailAquilaCockpit"))
		viewport.add_child(root)
		root.add_child(player)
		player.add_child(body)
		root.add_child(camera)
		body.add_child(walker)
		body.add_child(jet)
		camera.add_child(cockpit)
		camera_state.configure(config.pan_duration_ticks, config.control_view_handoff_lead_ticks,
			Words.store_word(0.1), Words.store_word(700.0))

	static func _leaf(original: Node3D) -> Node3D:
		var leaf: Node3D = original.duplicate()
		leaf.configure_prepared(null, true, false)
		return leaf

	func free_nodes() -> void:
		if is_instance_valid(root):
			root.free()

	func render(previous: Dictionary, current: Dictionary, same: bool, alpha: float, delta: float, height: float) -> Dictionary:
		particle_seconds = F.value(particle_seconds + dotnet_max(delta, 0.0))
		var before: Vector3 = to_player_world(previous)
		var after: Vector3 = to_player_world(current)
		var reset_jump: bool = distance_squared(after - before) > 100.0
		player.position = after if reset_jump else lerp_vector(before, after, alpha)
		var yaw: float = lerp_angle_single(micro(previous.facing_yaw_micro_rad), micro(current.facing_yaw_micro_rad), alpha)
		var pitch: float = lerp_single(micro(previous.facing_pitch_micro_rad), micro(current.facing_pitch_micro_rad), alpha)
		var roll: float = lerp_angle_single(micro(previous.body_roll_micro_rad), micro(current.body_roll_micro_rad), alpha)
		player.rotation = Vector3(0.0, yaw, 0.0)
		body.rotation = Vector3(-pitch, 0.0, -roll) if current.mode == JET and current.transition == NONE else Vector3.ZERO
		var contacts: Dictionary = to_foot_offsets(current)
		if not contacts.ok: return contacts
		var prior: Variant = null
		if not reset_jump and not same:
			if previous.feet == null: return failure("NullReferenceException", "")
			if previous.feet.size() == current.feet.size():
				var converted: Dictionary = to_foot_offsets(previous)
				if not converted.ok: return converted
				prior = converted.value
		var admitted: Dictionary = admit_transport(previous, current, same)
		if not admitted.ok: return admitted
		var feet: Array = contacts.value
		if prior != null:
			for index: int in feet.size():
				var value: Dictionary = Interpolation.interpolate_position(words(prior[index]), words(feet[index]),
					Words.store_word(alpha), Words.store_word(3.0))
				feet[index] = vector(value.value)
		var inverse: Basis = Presentation._inverse_yaw_basis(yaw).value
		var local: Array[Vector3] = []
		for contact: Vector3 in feet:
			local.append(Vector3(Presentation._sum3(inverse.x.x, contact.x, inverse.y.x, contact.y, inverse.z.x, contact.z),
				Presentation._sum3(inverse.x.y, contact.x, inverse.y.y, contact.y, inverse.z.y, contact.z),
				Presentation._sum3(inverse.x.z, contact.x, inverse.y.z, contact.y, inverse.z.z, contact.z)))
		var posed: Dictionary = walker.set_ground_contact_pose(local)
		if not posed.ok: return posed
		transition(current, delta)
		camera_state.advance(previous, current)
		var sampled: Dictionary = camera_state.sample_and_bind(Words.store_word(alpha))
		if not sampled.ok: return sampled
		var view: Dictionary = sampled.value.camera
		var selected: Dictionary = sampled.value.viewpoint
		show_hud = view.hud_visible
		opening_pan = view.opening_pan_active
		var showing_jet: bool = is_finite(walker_elapsed) or is_finite(jet_elapsed) or current.transition != NONE or current.mode == JET
		walker.visible = not show_hud and not showing_jet
		jet.visible = not show_hud and showing_jet
		cockpit.visible = show_hud
		body.position = Vector3.UP * F.value(1900.0 * Words.read_word(SCALE_BITS)) if showing_jet else Vector3.ZERO
		camera.size = F.value(F.value(F.value(2.0 * Words.read_word(selected.near_plane_bits)) * 0.75) * Words.read_word(view.zoom_bits))
		camera.position = vector(view.pose.position)
		camera.look_at(camera.position + vector(view.pose.forward), vector(view.pose.up))
		if height > 0.0:
			var offset: float = F.value(F.value(camera.size / height) * 0.5)
			camera.frustum_offset = Vector2(-offset, offset)
		return {"ok": true}

	func transition(snapshot: Dictionary, delta: float) -> void:
		var walker_started: bool = snapshot.transition == WALKER_TO_JET and previous_transition != WALKER_TO_JET
		var jet_started: bool = snapshot.transition == JET_TO_WALKER and previous_transition != JET_TO_WALKER
		var returned: bool = snapshot.transition == NONE and snapshot.mode == WALKER \
			and (previous_transition != NONE or previous_mode == JET)
		if walker_started:
			walker_elapsed = 0.0
			jet_elapsed = INF
		elif jet_started:
			walker_elapsed = INF
			jet_elapsed = 0.0
		elif returned:
			walker_elapsed = INF
			jet_elapsed = INF
		if is_finite(walker_elapsed):
			walker_elapsed = dotnet_min(F.value(walker_elapsed + dotnet_max(0.0, delta)), 1.25)
			jet.set_virtual_frame(F.value(25.0 + mini(floor_to_int(F.value(walker_elapsed * 20.0)), 25)))
			if walker_elapsed < Words.read_word(0x3f933333): # 23f / 20f
				cockpit.set_virtual_frame(F.value(27.0 + mini(floor_to_int(F.value(walker_elapsed * 20.0)), 22)))
			else:
				cockpit.set_virtual_frame(0.0)
			if walker_elapsed >= 1.25:
				jet.set_virtual_frame(0.0)
				walker_elapsed = INF
		elif is_finite(jet_elapsed):
			jet_elapsed = dotnet_min(F.value(jet_elapsed + dotnet_max(0.0, delta)), 1.25)
			jet.set_virtual_frame(float(mini(floor_to_int(F.value(jet_elapsed * 20.0)), 25)))
			cockpit.set_virtual_frame(F.value(1.0 + mini(floor_to_int(F.value(jet_elapsed * 20.0)), 24)))
			if jet_elapsed >= Words.read_word(0x3f99999a): # 24f / 20f
				cockpit.set_virtual_frame(25.0)
			if jet_elapsed >= 1.25:
				jet.set_virtual_frame(25.0)
				jet_elapsed = INF
		elif snapshot.mode == JET:
			jet.set_virtual_frame(0.0)
			cockpit.set_virtual_frame(0.0)
		else:
			jet.set_virtual_frame(25.0)
			cockpit.set_virtual_frame(25.0)
		previous_transition = snapshot.transition
		previous_mode = snapshot.mode

	# 1bb29345 AdmitOriginalCollectionTransport: both computed target
	# projections, then both projectile arrays' identities.
	static func admit_transport(previous: Dictionary, current: Dictionary, same: bool) -> Dictionary:
		for targets: Variant in ([current.targets] if same else [previous.targets, current.targets]):
			if targets is Dictionary and targets.get("ok") == false:
				return failure(targets.error_type, targets.error)
		for projectiles: Variant in ([current.projectiles] if same else [previous.projectiles, current.projectiles]):
			for projectile: Variant in projectiles:
				if projectile == null:
					return failure("NullReferenceException", "")
		return {"ok": true}

	static func to_player_world(snapshot: Dictionary) -> Vector3:
		var scale: float = Words.read_word(SCALE_BITS)
		var x: float = F.value(F.value(snapshot.player_position.x) * scale)
		var z: float = F.value(F.value(snapshot.player_position.z) * scale)
		return Vector3(x, F.value(F.value(wrap_i32(snapshot.player_elevation_millimeters - 1900)) * scale), -z)

	static func to_foot_offsets(snapshot: Dictionary) -> Dictionary:
		if snapshot.feet.size() != 4:
			return failure("InvalidDataException", "Core did not expose four Aquila foot contacts.")
		var scale: float = Words.read_word(SCALE_BITS)
		var contacts: Array = [Vector3.ZERO, Vector3.ZERO, Vector3.ZERO, Vector3.ZERO]
		for foot: Dictionary in snapshot.feet:
			if foot.id < 0 or foot.id >= 4:
				return failure("InvalidDataException", "Core exposed unknown Aquila foot %d." % foot.id)
			contacts[foot.id] = Vector3(F.value(F.value(wrap_i32(foot.x - snapshot.player_position.x)) * scale),
				F.value(F.value(wrap_i32(wrap_i32(foot.ground_elevation_millimeters + foot.lift_millimeters) - snapshot.player_ground_elevation_millimeters)) * scale),
				F.value(F.value(wrap_i32(-wrap_i32(foot.z - snapshot.player_position.z))) * scale))
		return {"ok": true, "value": contacts}

	static func micro(value: int) -> float:
		return F.value(F.value(value) / 1000000.0)

	static func distance_squared(d: Vector3) -> float:
		return F.value(F.value(F.value(d.x * d.x) + F.value(d.y * d.y)) + F.value(d.z * d.z))

	static func lerp_single(from: float, to: float, weight: float) -> float:
		return F.value(from + F.value(F.value(to - from) * weight))

	static func lerp_vector(from: Vector3, to: Vector3, weight: float) -> Vector3:
		return Vector3(lerp_single(from.x, to.x, weight), lerp_single(from.y, to.y, weight), lerp_single(from.z, to.z, weight))

	# Godot C# Mathf.LerpAngle over AngleDifference, with Single tau.
	static func lerp_angle_single(from: float, to: float, weight: float) -> float:
		var tau: float = Words.read_word(0x40c90fdb)
		var difference: float = F.value(fmod(F.value(to - from), tau))
		var angle: float = F.value(F.value(fmod(F.value(2.0 * difference), tau)) - difference)
		return F.value(from + F.value(angle * weight))

	# .NET Math.Max/Min(float, float), IEEE 754:2019 maximum/minimum: the NaN
	# operand itself propagates; equal values prefer +0 / -0.
	static func dotnet_max(x: float, y: float) -> float:
		if x != y:
			if not is_nan(x):
				return x if y < x else y
			return x
		return x if signbit(y) else y

	static func dotnet_min(x: float, y: float) -> float:
		if x != y:
			if not is_nan(x):
				return x if x < y else y
			return x
		return x if signbit(x) else y

	static func signbit(value: float) -> bool:
		return (Words.store_word(value) & 0x80000000) != 0

	# GodotSharp Mathf.FloorToInt on the pinned .NET runtime saturates; NaN is 0.
	static func floor_to_int(value: float) -> int:
		if is_nan(value): return 0
		if value >= 2147483647.0: return I32_MAX
		if value <= -2147483648.0: return I32_MIN
		return int(floor(value))

	static func wrap_i32(value: int) -> int:
		var low: int = value & 0xffffffff
		return low - 0x100000000 if low >= 0x80000000 else low

	static func words(value: Vector3) -> Dictionary:
		return {"x_bits": Words.store_word(value.x), "y_bits": Words.store_word(value.y), "z_bits": Words.store_word(value.z)}

	static func vector(value: Dictionary) -> Vector3:
		return Vector3(Words.read_word(value.x_bits), Words.read_word(value.y_bits), Words.read_word(value.z_bits))

	static func failure(type: String, message: String) -> Dictionary:
		return {"ok": false, "error_type": type, "error": message}
