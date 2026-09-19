# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Exact canonical StateHasher.cs schemas 42..48. This is a serializer, never a
## simulation or restore owner. Input mirrors the consumed C# record properties
## in snake_case; ActorId is an Int32, vectors/bases are named-word Dictionaries,
## and ordered collections are Arrays. Every consumed nullable property must be
## present, with null distinct from empty. Extra, unhashed properties are ignored.
## Strings accept String or raw PackedInt32Array UTF-16; BinaryWriter's replacement
## of malformed pairs and embedded NUL bytes is retained. Integers never coerce
## floats, and raw float words keep the signed/unsigned type of their C# owner.

const Writer = preload("res://Core/canonical_binary_writer.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const Float32 = preload("res://Core/retail_float24.gd")
const MAGIC: String = "ONSLAUGHT-REBUILD-STATE"
const BASIS_KEYS: Array[String] = ["row0_x", "row0_y", "row0_z", "row1_x", "row1_y", "row1_z", "row2_x", "row2_y", "row2_z"]
const WEAPON_KEYS: Array[String] = ["pulse_charge_bits", "pulse_ready_at_time_bits", "twin_vulcan_ready_at_time_bits", "mech_vulcan_ready_at_time_bits", "missile_pod_ready_at_time_bits"]


static func get_canonical_bytes(snapshot: Variant) -> Dictionary:
	if snapshot == null:
		return {"ok": false, "error_type": "ArgumentNullException", "error": "state must not be null."}
	var encoder := Encoder.new()
	if not encoder.write_world(snapshot):
		encoder.fail("Canonical snapshot serialization did not complete.")
	if not encoder.error.is_empty():
		return {"ok": false, "error_type": encoder.error_type, "error": encoder.error}
	var result: Dictionary = encoder.writer.finish()
	if not result.ok:
		return {"ok": false, "error_type": "ArgumentException", "error": result.error}
	return {"ok": true, "bytes": result.bytes, "schema": encoder.schema}


static func compute_hex(snapshot: Variant) -> Dictionary:
	var encoded: Dictionary = get_canonical_bytes(snapshot)
	if not encoded.ok:
		return encoded
	var hasher := HashingContext.new()
	if hasher.start(HashingContext.HASH_SHA256) != OK or hasher.update(encoded.bytes) != OK:
		return {"ok": false, "error_type": "InvalidOperationException", "error": "Cannot hash canonical bytes."}
	return {"ok": true, "hex": hasher.finish().hex_encode(), "schema": encoded.schema}


class Encoder extends RefCounted:
	var writer = Writer.new()
	var error: String = ""
	var error_type: String = "ArgumentException"
	var schema: int = 0
	var _plane: bool = false
	var _exit: bool = false
	var _shutdown: bool = false
	var _clock: bool = false
	var _weapon: bool = false
	var _world: bool = false

	func fail(reason: String, type: String = "ArgumentException") -> bool:
		if error.is_empty():
			error = reason
			error_type = type
		return false

	func section(completed: bool) -> bool:
		# A GDScript helper aborted by the engine returns false. It cannot be
		# mistaken for a successful partial serialization by its caller.
		return completed or fail("A canonical snapshot section did not complete.")

	func field(record: Dictionary, key: String) -> Variant:
		if not record.has(key):
			fail("Missing required snapshot field: " + key)
			return null
		return record[key]

	func record(value: Variant, label: String) -> Dictionary:
		if not value is Dictionary:
			fail(label + " must be a Dictionary.")
			return {}
		return value

	func child(parent: Dictionary, key: String) -> Dictionary:
		return record(field(parent, key), key)

	func array(parent: Dictionary, key: String) -> Array:
		var value: Variant = field(parent, key)
		if not value is Array:
			fail(key + " must be an Array.")
			return []
		return value

	func number(parent: Dictionary, key: String, kind: String = "i32") -> int:
		var value: Variant = field(parent, key)
		if typeof(value) != TYPE_INT:
			fail(key + " must be an exact " + kind + ", without numeric coercion.")
			return 0
		var valid: bool = true
		match kind:
			"i8": valid = value >= -128 and value <= 127
			"u8": valid = value >= 0 and value <= 255
			"i16": valid = value >= -32768 and value <= 32767
			"u16": valid = value >= 0 and value <= 65535
			"i32": valid = value >= -2147483648 and value <= 2147483647
			"u32": valid = value >= 0 and value <= 4294967295
			"i64": pass
			_: valid = false
		if not valid:
			fail(key + " is outside " + kind + ".")
			return 0
		return value

	func boolean(parent: Dictionary, key: String) -> bool:
		var value: Variant = field(parent, key)
		if not value is bool:
			fail(key + " must be a Boolean.")
			return false
		return value

	func emit(parent: Dictionary, key: String, kind: String = "i32") -> bool:
		if not error.is_empty():
			return false
		if kind == "bool":
			var value: bool = boolean(parent, key)
			return error.is_empty() and writer.write_bool(value)
		if kind == "text":
			var value: Variant = field(parent, key)
			if not error.is_empty():
				return false
			if not writer.write_string(value):
				return fail("Invalid BinaryWriter string: " + key)
			return true
		var value: int = number(parent, key, kind)
		if not error.is_empty():
			return false
		match kind:
			"i8": return writer.write_i8(value)
			"u8": return writer.write_u8(value)
			"i16": return writer.write_i16(value)
			"u16": return writer.write_u16(value)
			"i32": return writer.write_i32(value)
			"u32": return writer.write_u32(value)
			"i64": return writer.write_i64(value)
		return fail("Unknown canonical primitive.")

	func fields(parent: Dictionary, keys: Array, kind: String = "i32") -> bool:
		for key: String in keys:
			if not emit(parent, key, kind):
				return false
		return error.is_empty()

	func nullable(parent: Dictionary, key: String, kind: String) -> bool:
		var value: Variant = field(parent, key)
		if not error.is_empty():
			return false
		writer.write_bool(value != null)
		return true if value == null else emit(parent, key, kind)

	func vector(parent: Dictionary, key: String, three: bool = true) -> bool:
		return fields(child(parent, key), ["x", "y", "z"] if three else ["x", "z"])

	func basis(parent: Dictionary, key: String) -> bool:
		return fields(child(parent, key), BASIS_KEYS)

	func counted(parent: Dictionary, key: String) -> Array:
		var values: Array = array(parent, key)
		writer.write_i32(values.size())
		return values

	func ordered(parent: Dictionary, key: String, keys: Array, kinds: Array = []) -> Array:
		# LINQ OrderBy is stable. Explicit source-index ties preserve that law;
		# Godot's unstable sort cannot silently reorder equal-key records.
		var values: Array = array(parent, key)
		var decorated: Array = []
		for index: int in range(values.size()):
			var value: Dictionary = record(values[index], key)
			var sort_keys: Array[int] = []
			for offset: int in range(keys.size()):
				sort_keys.append(number(value, keys[offset], "i32" if kinds.is_empty() else kinds[offset]))
			decorated.append([value, sort_keys, index])
		if not error.is_empty():
			return []
		decorated.sort_custom(func(a: Array, b: Array) -> bool:
			for offset: int in range(a[1].size()):
				if a[1][offset] != b[1][offset]:
					return a[1][offset] < b[1][offset]
			return a[2] < b[2])
		var result: Array = []
		for item: Array in decorated:
			result.append(item[0])
		return result

	func select_schema(state: Dictionary) -> bool:
		var registry: Dictionary = child(state, "level100_actors")
		var mechanics: Dictionary = child(state, "level100_actor_mechanics")
		var mission: Dictionary = child(state, "level100_mission")
		var raw: Array[int] = []
		for item: Variant in array(registry, "base_states"):
			var entry: Dictionary = record(item, "base_state")
			var base: Dictionary = child(entry, "state")
			var plane: Variant = field(base, "retail_plane")
			var poses: Variant = field(base, "retail_poses")
			var motion: Variant = field(base, "retail_motion")
			if plane == null and (poses != null or motion != null):
				return fail("Incomplete retail construction has no admitted hash schema.", "NotSupportedException")
			if plane != null:
				raw.append(number(entry, "actor_id"))
		raw.sort()
		var events: Variant = field(mechanics, "plane_events")
		var guided: Array[int] = []
		var exits: Array[int] = []
		for item: Variant in array(mechanics, "actors"):
			var actor: Dictionary = record(item, "mechanics_actor")
			if field(actor, "plane_guide") != null:
				guided.append(number(actor, "actor_id"))
			if field(actor, "plane_spawner_exit") != null:
				exits.append(number(actor, "actor_id"))
		guided.sort()
		exits.sort()
		_plane = not raw.is_empty() or events != null or not guided.is_empty() or not exits.is_empty()
		var expected_exits: Array[int] = []
		var dying_shutdown: bool = false
		for item: Variant in array(registry, "actors"):
			var actor: Dictionary = record(item, "actor")
			var id: int = number(actor, "actor_id")
			if field(actor, "spawn_owner_id") != null and raw.has(id):
				expected_exits.append(id)
			if number(actor, "lifecycle") == 3:
				dying_shutdown = true
		expected_exits.sort()
		if expected_exits != exits:
			return fail("Spawned aircraft exit ownership is incomplete.")
		_exit = not expected_exits.is_empty()
		if _plane and number(mission, "world_number") != 100:
			return fail("Raw Plane motion does not admit incomplete world construction.", "NotSupportedException")
		var event_frame: int = number(state, "retail_event_frame_count", "u32")
		if _plane:
			if raw != guided or events == null:
				return fail("Aircraft pose, guide and event clock ownership is incomplete.")
			if number(record(events, "plane_events"), "frame_count", "u32") != event_frame:
				return fail("Aircraft pose, guide and event clock ownership is incomplete.")
		_shutdown = _plane or not array(child(state, "level100_destruction"), "pending_shutdowns").is_empty() or dying_shutdown
		_clock = _shutdown or event_frame != (number(mission, "tick") & 0xffffffff)
		var weapons: Dictionary = child(state, "level100_player_weapon_state")
		_weapon = _clock
		for index: int in range(WEAPON_KEYS.size()):
			if number(weapons, WEAPON_KEYS[index], "u32") != (0 if index == 0 else 0xc3480000):
				_weapon = true
		_world = _weapon or number(mission, "world_number") != 100
		for item: Variant in array(mission, "secondary_objectives"):
			var objective: Dictionary = record(item, "secondary_objective")
			if number(objective, "text_id") != 0 or number(objective, "status") != 0:
				_world = true
		schema = 48 if _exit else 47 if _plane else 46 if _shutdown else 45 if _clock else 44 if _weapon else 43 if _world else 42
		return error.is_empty()

	func write_world(value: Variant) -> bool:
		var state: Dictionary = record(value, "state")
		if not select_schema(state):
			return false
		writer.write_bytes(MAGIC.to_ascii_buffer())
		writer.write_i32(schema)
		emit(state, "tick")
		if _clock: emit(state, "retail_event_frame_count", "u32")
		emit(state, "seed", "u32")
		section(progress(child(state, "initial_level100_tutorial_progress")))
		fields(state, ["mode", "transition"])
		section(vector(state, "player_position", false))
		section(vector(state, "player_velocity", false))
		fields(state, ["player_ground_elevation_millimeters", "player_ground_delta_millimeters", "player_elevation_millimeters", "player_vertical_velocity_millimeters_per_tick"])
		fields(state, ["player_on_ground", "player_in_water", "player_water_failure", "player_on_steep_slope", "landing_jets_active"], "bool")
		emit(state, "ground_impact_speed_millimeters_per_tick")
		for item: Variant in counted(state, "aquila_flight_event_log"):
			var event: Dictionary = record(item, "flight_event")
			emit(event, "tick"); emit(event, "kind", "u16")
			fields(event, ["mode", "transition"]); emit(event, "weapon", "u8")
		fields(state, ["facing_x", "facing_z"], "i8")
		fields(state, ["facing_yaw_micro_rad", "walker_yaw_velocity_micro_rad_per_tick", "facing_pitch_micro_rad", "walker_pitch_velocity_micro_rad_per_tick", "body_roll_micro_rad", "roll_velocity_micro_rad_per_tick", "walker_last_move_x_permille", "walker_last_move_z_permille", "walker_last_hard_left_tick", "walker_last_hard_right_tick", "walker_last_hard_forward_tick", "walker_last_hard_backward_tick", "walker_dash_ticks_remaining", "walker_sound_travel_millimeters", "walker_sound_rollover_count", "energy", "shield", "hull", "augment_charge"])
		emit(state, "augment_active", "bool")
		for item: Variant in counted(state, "level100_player_damage_events"):
			var damage: Dictionary = record(item, "player_damage")
			emit(damage, "tick"); emit(damage, "source", "u8")
			fields(damage, ["incoming_damage_milli_life", "shield_absorbed_milli_life", "life_damage_milli_life"])
			emit(damage, "requests_death", "bool")
		for item: Variant in counted(state, "level100_damage_flashes"):
			fields(record(item, "damage_flash"), ["relative_yaw_micro_rad", "start_tick"])
		emit(state, "transform_ticks_remaining")
		fields(state, ["walker_to_jet_uses_takeoff_lift", "walker_to_jet_lift_applied"], "bool")
		fields(state, ["ticks_since_ground_contact", "jet_ticks_since_transform", "jet_strafe_ticks_remaining", "jet_strafe_acceleration_remainder", "jet_energy_drain_remainder_micro_retail", "jet_thruster_permille", "jet_grounded_slow_ticks", "jet_stall_ticks", "fire_cooldown_ticks_remaining", "twin_vulcan_reload_ticks_remaining"])
		if _weapon: fields(child(state, "level100_player_weapon_state"), WEAPON_KEYS, "u32")
		emit(state, "level100_opening_ticks_remaining")
		fields(state, ["level100_player_active", "level100_flight_enabled", "level100_pulse_cannon_enabled", "level100_vulcan_cannon_enabled", "level100_mech_vulcan_cannon_enabled", "level100_missile_pod_enabled"], "bool")
		fields(state, ["level100_walker_selected_weapon", "level100_jet_selected_weapon", "zoom_permille", "desired_zoom_permille", "level100_hud_emphasis_mask"])
		section(mission(child(state, "level100_mission")))
		section(mission_events(array(state, "level100_mission_events")))
		section(actor_registry(child(state, "level100_actors")))
		section(destruction(child(state, "level100_destruction"), array(state, "level100_destruction_events")))
		if _shutdown:
			for item: Variant in counted(child(state, "level100_destruction"), "pending_shutdowns"):
				var pending: Dictionary = record(item, "pending_shutdown")
				emit(pending, "actor_id")
				fields(pending, ["admission_frame", "delivery_frame", "due_time_bits"], "u32")
		for item: Variant in counted(state, "level100_weapon_fire_events"):
			var event: Dictionary = record(item, "weapon_fire_event")
			emit(event, "tick"); emit(event, "weapon", "u8"); emit(event, "round_count")
		section(actor_scripts(child(state, "level100_actor_scripts")))
		section(actor_commands(array(state, "level100_actor_script_commands")))
		section(actor_mechanics(child(state, "level100_actor_mechanics")))
		emit(state, "next_projectile_id")
		var projectiles: Array = ordered(state, "projectiles", ["id"])
		writer.write_i32(projectiles.size())
		for projectile: Dictionary in projectiles:
			emit(projectile, "id"); emit(projectile, "kind", "u8")
			section(vector(projectile, "position", false)); section(vector(projectile, "velocity", false))
			fields(projectile, ["elevation_millimeters", "vertical_velocity_millimeters_per_tick", "remaining_ticks"])
		var feet: Array = ordered(state, "walker_feet", ["id"])
		writer.write_i32(feet.size())
		for foot: Dictionary in feet:
			emit(foot, "id"); section(vector(foot, "position", false))
			fields(foot, ["ground_elevation_millimeters", "phase_thirds", "lift_millimeters"])
		return error.is_empty()

	func progress(value: Dictionary) -> bool:
		return fields(value, ["introduction", "pulse_cannon", "vulcan_cannon", "status_bars"], "bool")

	func locals(values: Array) -> bool:
		writer.write_i32(values.size())
		for item: Variant in values:
			var local: Dictionary = record(item, "local")
			emit(local, "ordinal"); emit(local, "name", "text")
			section(script_value(child(local, "value")))
		return error.is_empty()

	func queued(values: Array) -> bool:
		writer.write_i32(values.size())
		for item: Variant in values:
			var event: Dictionary = record(item, "queued_event")
			emit(event, "sequence", "i64"); emit(event, "event_name", "text")
		return error.is_empty()

	func mission(value: Dictionary) -> bool:
		emit(value, "tick"); emit(value, "program_sha256", "text")
		if _world: emit(value, "world_number")
		fields(value, ["initializer_ran", "is_running"], "bool")
		emit(value, "next_sequence", "i64")
		section(execution(child(value, "active_execution")))
		section(locals(array(value, "locals"))); section(queued(array(value, "event_queue")))
		for item: Variant in counted(value, "continuations"):
			var continuation: Dictionary = record(item, "mission_continuation")
			emit(continuation, "sequence", "i64")
			fields(continuation, ["due_tick", "wait_kind", "wait_argument"])
			section(execution(child(continuation, "execution")))
		fields(value, ["outcome", "terminal_state", "failure_reason", "failure_text_id", "terminal_ticks_remaining", "initial_player_health", "latest_player_health", "observed_player_health"])
		fields(value, ["player_active", "flight_mode_enabled"], "bool")
		fields(value, ["pulse_cannon_availability", "twin_vulcan_availability", "mech_vulcan_availability", "missile_pod_availability"])
		nullable(value, "navigation_objective", "text")
		fields(value, ["evaded", "aborted"], "bool")
		fields(value, ["friendly_building_hits", "score_delta"])
		section(progress(child(value, "tutorial_progress")))
		for item: Variant in counted(value, "primary_objectives"):
			fields(record(item, "primary_objective"), ["objective", "text_id", "status"])
		if _world:
			for item: Variant in counted(value, "secondary_objectives"):
				fields(record(item, "secondary_objective"), ["index", "text_id", "status"])
		section(mission_events(array(value, "pending_events")))
		emit(value, "message_clear_tick")
		section(mission_events(array(value, "pending_messages")))
		emit(value, "message_box_allowed_tick")
		return error.is_empty()

	func mission_events(values: Array) -> bool:
		writer.write_i32(values.size())
		for raw: Variant in values:
			var item: Dictionary = record(raw, "mission_event")
			var tag: int = number(item, "event_type", "u8")
			if tag not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14, 15, 16, 17, 18]:
				return fail("Unknown Level 100 mission event.", "InvalidOperationException")
			writer.write_u8(tag); emit(item, "tick")
			match tag:
				1:
					fields(item, ["speaker_id", "message_id"])
					emit(item, "script_waits_for_duration", "bool"); emit(item, "expected_playback_ticks")
				2:
					emit(item, "part_id"); emit(item, "emphasized", "bool")
				3: emit(item, "active", "bool")
				4: emit(item, "enabled", "bool")
				5:
					emit(item, "weapon"); emit(item, "enabled", "bool")
				6: nullable(item, "thing_name", "text")
				7: fields(item, ["actor_id", "command"])
				8:
					emit(item, "owner_actor_id")
					fields(item, ["definition_name", "spawner_name"], "text")
					emit(item, "count"); emit(item, "script_name", "text")
				9: emit(item, "event_name", "text")
				13: emit(item, "help_message_id")
				14: fields(item, ["delta", "total_delta"])
				15: emit(item, "slot")
				16: fields(item, ["objective", "text_id", "status"])
				17: fields(item, ["outcome", "failure_reason", "failure_text_id"])
				18: emit(item, "state")
		return error.is_empty()

	func execution(value: Dictionary) -> bool:
		nullable(value, "event_name", "text")
		fields(value, ["instruction_pointer", "flags", "saved_stack_size"])
		emit(value, "abort", "bool")
		var context: Variant = field(value, "call_context")
		writer.write_bool(context != null)
		if context != null: section(script_value(record(context, "call_context")))
		for item: Variant in counted(value, "stack"):
			section(script_value(record(item, "stack_value")))
		for item: Variant in counted(value, "call_frames"):
			if not writer.write_i32(item): fail("A call-frame pointer must be Int32.")
		return error.is_empty()

	func script_value(value: Dictionary) -> bool:
		fields(value, ["type", "scalar", "component_y", "component_z"])
		nullable(value, "text", "text")
		return error.is_empty()

	func actor_scripts(value: Dictionary) -> bool:
		emit(value, "tick"); emit(value, "next_sequence", "i64"); emit(value, "player_in_jet_mode", "bool")
		for raw: Variant in counted(value, "instances"):
			var item: Dictionary = record(raw, "script_instance")
			nullable(item, "actor_id", "i32")
			fields(item, ["program_name", "program_sha256"], "text"); emit(item, "initialized", "bool")
			section(locals(array(item, "locals"))); section(execution(child(item, "active_execution")))
			section(queued(array(item, "queued_events")))
			for pending: Variant in counted(item, "continuations"):
				var continuation: Dictionary = record(pending, "actor_continuation")
				emit(continuation, "sequence", "i64"); nullable(continuation, "due_tick", "i32")
				emit(continuation, "wait_kind"); nullable(continuation, "wait_argument", "text")
				section(execution(child(continuation, "execution")))
		for raw: Variant in counted(value, "pending_posted_events"):
			var item: Dictionary = record(raw, "posted_event")
			emit(item, "sequence", "i64"); emit(item, "tick")
			nullable(item, "actor_id", "i32"); emit(item, "event_name", "text")
		section(actor_commands(array(value, "pending_commands")))
		return error.is_empty()

	func actor_commands(values: Array) -> bool:
		writer.write_i32(values.size())
		for raw: Variant in values:
			var item: Dictionary = record(raw, "actor_command")
			emit(item, "sequence", "i64"); emit(item, "tick"); nullable(item, "actor_id", "i32")
			emit(item, "kind"); nullable(item, "target_actor_id", "i32"); nullable(item, "argument", "text"); emit(item, "scalar")
		return error.is_empty()

	func actor_mechanics(value: Dictionary) -> bool:
		emit(value, "last_consumed_command_sequence", "i64")
		var actors: Array = ordered(value, "actors", ["actor_id"])
		writer.write_i32(actors.size())
		for item: Dictionary in actors:
			fields(item, ["actor_id", "ai_state", "allegiance"]); emit(item, "has_allegiance_override", "bool")
			emit(item, "intent"); nullable(item, "target_actor_id", "i32"); nullable(item, "waypoint_path", "text")
			fields(item, ["waypoint_point_index", "waypoint_command_scalar"]); emit(item, "wait_for_waypoint_completion", "bool")
			emit(item, "ground_full_guide_base_tick_phase")
			if _plane:
				var guide: Variant = field(item, "plane_guide")
				writer.write_bool(guide != null)
				if guide != null:
					var data: Dictionary = record(guide, "plane_guide")
					section(vector(data, "destination"))
					fields(data, ["mode", "clearance_float_bits", "clearance_cell_x", "clearance_cell_y", "controller_state", "speed_mode"])
			if _exit:
				var exit_data: Variant = field(item, "plane_spawner_exit")
				writer.write_bool(exit_data != null)
				if exit_data != null:
					var data: Dictionary = record(exit_data, "plane_spawner_exit")
					nullable(data, "spawning_owner_id", "i32"); nullable(data, "collision_ignored_actor_id", "i32")
					fields(data, ["attachment_tag", "selector", "deadline_float_bits"]); emit(data, "script_control_resumed", "bool")
		fields(value, ["released_random_seed", "next_actor_round_id"])
		var weapons: Array = ordered(value, "actor_weapons", ["actor_id", "weapon"])
		writer.write_i32(weapons.size())
		for weapon: Dictionary in weapons:
			fields(weapon, ["actor_id", "weapon", "reload_base_ticks_remaining", "burst_shots_remaining", "burst_delay_base_ticks_remaining"])
		var rounds: Array = ordered(value, "actor_rounds", ["id"])
		writer.write_i32(rounds.size())
		for item: Dictionary in rounds:
			fields(item, ["id", "owner_actor_id", "target_actor_id", "kind"])
			section(vector(item, "position_millimeters"))
			fields(item, ["yaw_micro_radians", "pitch_micro_radians", "remaining_base_ticks", "elapsed_base_ticks"])
			emit(item, "locked", "bool")
		if _plane: section(aircraft_events(child(value, "plane_events")))
		return error.is_empty()

	func aircraft_events(value: Dictionary) -> bool:
		emit(value, "float24_arithmetic", "bool")
		fields(value, ["time_bits", "frame_count"], "u32")
		fields(value, ["current_buffer_num", "ready_to_flush_buffer", "live_events"])
		fields(value, ["total_processed", "processed_this_update"], "u32")
		emit(value, "valid", "bool"); emit(value, "free_list")
		for raw: Variant in counted(value, "slots"):
			var item: Dictionary = record(raw, "event_slot")
			fields(item, ["handle", "next_free"]); emit(item, "event_num", "i16")
			fields(item, ["listener", "data"]); emit(item, "time_bits", "u32"); emit(item, "reuse", "bool")
		for raw: Variant in counted(value, "lanes"):
			var lane: Dictionary = record(raw, "event_lane")
			emit(lane, "lane_index")
			for handle: Variant in counted(lane, "handles"):
				if not writer.write_i32(handle): fail("An event handle must be Int32.")
		for handle: Variant in counted(value, "overflow"):
			if not writer.write_i32(handle): fail("An overflow handle must be Int32.")
		return error.is_empty()

	func actor_registry(value: Dictionary) -> bool:
		emit(value, "definition_set_identity_sha256", "text"); emit(value, "next_actor_id"); emit(value, "next_fact_sequence", "i64")
		var actors: Array = ordered(value, "actors", ["actor_id"])
		writer.write_i32(actors.size())
		for actor: Dictionary in actors:
			emit(actor, "actor_id"); fields(actor, ["definition_identity", "name"], "text")
			for key: String in ["definition_name", "script_name", "mesh_binding"]: nullable(actor, key, "text")
			emit(actor, "thing_type_mask", "u32"); nullable(actor, "spawn_owner_id", "i32"); nullable(actor, "spawner_name", "text")
			fields(actor, ["is_static", "active", "is_objective"], "bool"); fields(actor, ["lifecycle", "health"])
			var pose: Dictionary = child(actor, "pose")
			section(vector(pose, "position_millimeters")); section(basis(pose, "basis_float_bits"))
			section(vector(pose, "linear_velocity_millimeters_per_tick")); section(vector(pose, "angular_velocity_micro_radians_per_tick"))
			fields(actor, ["target_group", "target_ordinal"]); nullable(actor, "trigger", "i32")
			emit(actor, "trigger_entered", "bool"); nullable(actor, "trigger_entry_jet_mode_state", "i32")
			emit(actor, "trigger_event_dispatched", "bool")
		var bases: Array = ordered(value, "base_states", ["actor_id"])
		writer.write_i32(bases.size())
		for item: Dictionary in bases:
			var base: Dictionary = child(item, "state")
			emit(item, "actor_id"); emit(base, "flags", "u16")
			for key: String in ["current_pose", "old_pose"]:
				var pose: Dictionary = child(base, key)
				section(vector(pose, "position_millimeters")); section(basis(pose, "basis_float_bits"))
			section(vector(base, "velocity")); section(vector(base, "angular_velocity"))
			emit(base, "thing_type_mask", "u32")
			fields(base, ["last_time_on_ground_float_bits", "last_time_in_water_float_bits", "last_time_on_object_float_bits"])
			if _plane:
				var raw_plane: Variant = field(base, "retail_plane")
				writer.write_bool(raw_plane != null)
				if raw_plane != null:
					var matching: Array = actors.filter(func(actor: Dictionary) -> bool: return actor.actor_id == item.actor_id)
					if matching.size() != 1:
						return fail("Raw Plane hashing requires exactly one matching actor.", "InvalidOperationException")
					var actor: Dictionary = matching[0]
					if not text_is(field(actor, "definition_name"), "Air Trainer") and not text_is(field(actor, "definition_name"), "Target Drone"):
						return fail("Raw Plane hashing requires an admitted aircraft definition.", "NotSupportedException")
					if not validate_plane(base, actor): return false
					var poses: Dictionary = child(base, "retail_poses")
					for key: String in ["current", "old"]:
						var pose: Dictionary = child(poses, key)
						section(vector(pose, "position_float_bits")); section(basis(pose, "basis_float_bits"))
					fields(child(base, "retail_motion"), ["last_move_time_float_bits", "move_countdown"])
					var plane: Dictionary = record(raw_plane, "retail_plane")
					for key: String in ["velocity", "drive", "current_euler", "desired_euler", "euler_rates"]: section(vector(plane, key))
					emit(plane, "bank_flag_float_bits")
		var facts: Array = ordered(value, "pending_facts", ["sequence"], ["i64"])
		writer.write_i32(facts.size())
		for fact: Dictionary in facts:
			emit(fact, "sequence", "i64"); fields(fact, ["kind", "actor_id"])
			nullable(fact, "other_actor_id", "i32"); emit(fact, "other_thing_type_mask", "u32")
		return error.is_empty()

	func destruction(value: Dictionary, events: Array) -> bool:
		var actors: Array = ordered(value, "actors", ["actor_id"])
		writer.write_i32(actors.size())
		for item: Dictionary in actors:
			emit(item, "actor_id"); emit(item, "definition_name", "text"); emit(item, "current_life_bits", "u32")
			fields(item, ["terminal", "below_half_reported"], "bool")
			var initial: Array = array(item, "initial_health_bits")
			var current: Array = array(item, "current_health_bits")
			var activity: Array = array(item, "part_activity")
			if initial.size() != current.size() or initial.size() != activity.size():
				return fail("A Level 100 destruction snapshot changed part shape.", "InvalidDataException")
			writer.write_i32(initial.size())
			for index: int in range(initial.size()):
				if not writer.write_u32(initial[index]) or not writer.write_u32(current[index]) or not writer.write_u8(activity[index]):
					return fail("Destruction part words require UInt32 health and byte activity.")
		writer.write_i32(events.size())
		for raw: Variant in events:
			var item: Dictionary = record(raw, "destruction_event")
			fields(item, ["kind", "effect_kind"], "u8"); fields(item, ["actor_id", "part_index"])
			emit(item, "remaining_health_bits", "u32"); section(vector(item, "position"))
		return error.is_empty()

	func text_is(value: Variant, expected: String) -> bool:
		if value == null: return false
		var actual: Dictionary = Text.units(value)
		if not actual.ok: return fail("Invalid aircraft definition text.")
		return actual.value == Text.units(expected).value

	func finite_vector(value: Dictionary, keys: Array) -> bool:
		for key: String in keys:
			var bits: int = number(value, key)
			if (bits & 0x7f800000) == 0x7f800000: return false
		return error.is_empty()

	func millimeters(value: float) -> int:
		# Math.Round(..., AwayFromZero), followed by the checked Int32 cast.
		# Split off the integral part first: adding 0.5 can itself round an
		# immediately-below-half input onto an integer before the test.
		var rounded: float = floor(value) if value >= 0.0 else ceil(value)
		var fraction: float = value - rounded
		if fraction >= 0.5: rounded += 1.0
		elif fraction <= -0.5: rounded -= 1.0
		if not is_finite(rounded) or rounded < -2147483648.0 or rounded > 2147483647.0:
			fail("Raw compatibility projection overflows Int32.", "OverflowException")
			return 0
		return int(rounded)

	func project_position(value: Dictionary) -> Dictionary:
		return {"x": millimeters((Float32.read_word(number(value, "x")) - 288.6875) * 1000.0),
			"y": millimeters((-10.0 - Float32.read_word(number(value, "z"))) * 1000.0),
			"z": millimeters((Float32.read_word(number(value, "y")) - 243.25) * 1000.0)}

	func negate_word(value: int) -> int:
		var word: int = (value ^ 0x80000000) & 0xffffffff
		return word - 0x100000000 if word >= 0x80000000 else word

	func project_basis(value: Dictionary) -> Dictionary:
		return {"row0_x": number(value, "row0_x"), "row0_y": negate_word(number(value, "row0_z")), "row0_z": number(value, "row0_y"),
			"row1_x": negate_word(number(value, "row2_x")), "row1_y": number(value, "row2_z"), "row1_z": negate_word(number(value, "row2_y")),
			"row2_x": number(value, "row1_x"), "row2_y": negate_word(number(value, "row1_z")), "row2_z": number(value, "row1_y")}

	func validate_plane(base: Dictionary, actor: Dictionary) -> bool:
		if field(base, "retail_poses") == null or field(base, "retail_motion") == null:
			return fail("Plane motion requires complete Actor poses and movement state.")
		var poses: Dictionary = child(base, "retail_poses")
		for key: String in ["current", "old"]:
			var pose: Dictionary = child(poses, key)
			if not finite_vector(child(pose, "position_float_bits"), ["x", "y", "z"]):
				return fail("Retail position must contain finite float words.")
			project_position(child(pose, "position_float_bits"))
			if not error.is_empty(): return false
			if not finite_vector(child(pose, "basis_float_bits"), BASIS_KEYS):
				return fail("Retail basis must contain finite float words.")
		var plane: Dictionary = child(base, "retail_plane")
		for key: String in ["velocity", "drive", "current_euler", "desired_euler", "euler_rates"]:
			if not finite_vector(child(plane, key), ["x", "y", "z"]):
				return fail("Plane motion requires finite words.")
		var rates: Dictionary = child(plane, "euler_rates")
		for key: String in ["x", "y", "z"]:
			if Float32.read_word(number(rates, key)) < 0.0: return fail("Plane rates must be nonnegative.")
		if number(plane, "bank_flag_float_bits") not in [0, 0x3f800000]:
			return fail("Plane bank flag must be a Boolean float word.")
		var motion: Dictionary = child(base, "retail_motion")
		if not finite_vector(motion, ["last_move_time_float_bits"]):
			return fail("Plane event time must be finite.", "ArgumentOutOfRangeException")
		if number(motion, "move_countdown") < 0: return fail("Plane move countdown must be nonnegative.")
		for key: String in ["current", "old"]:
			var raw: Dictionary = child(poses, key)
			var compat: Dictionary = child(base, key + "_pose")
			if project_position(child(raw, "position_float_bits")) != field(compat, "position_millimeters") or project_basis(child(raw, "basis_float_bits")) != field(compat, "basis_float_bits"):
				return fail("Plane compatibility poses disagree with retained raw state.")
		var velocity: Dictionary = child(plane, "velocity")
		var projected_velocity: Dictionary = {"x": millimeters(Float32.read_word(number(velocity, "x")) * 1000.0),
			"y": millimeters(-Float32.read_word(number(velocity, "z")) * 1000.0), "z": millimeters(Float32.read_word(number(velocity, "y")) * 1000.0)}
		if not error.is_empty(): return false
		if projected_velocity != field(base, "velocity"): return fail("Plane compatibility velocity disagrees with raw state.")
		if (number(base, "flags", "u16") & ~0x17) != 0 or (number(base, "thing_type_mask", "u32") & 0x80000003) != 0x80000003:
			return fail("Thing/Actor base-state flags or lineage violate the source contract.")
		if not finite_vector(child(child(base, "current_pose"), "basis_float_bits"), BASIS_KEYS) or not finite_vector(child(child(base, "old_pose"), "basis_float_bits"), BASIS_KEYS) or not finite_vector(base, ["last_time_on_ground_float_bits", "last_time_in_water_float_bits", "last_time_on_object_float_bits"]):
			return fail("Thing/Actor base state requires finite contact and basis words.")
		var actor_pose: Dictionary = child(actor, "pose")
		var current: Dictionary = child(base, "current_pose")
		if field(actor_pose, "position_millimeters") != field(current, "position_millimeters") or field(actor_pose, "basis_float_bits") != field(current, "basis_float_bits") or field(actor_pose, "linear_velocity_millimeters_per_tick") != field(base, "velocity") or field(actor_pose, "angular_velocity_micro_radians_per_tick") != field(base, "angular_velocity"):
			return fail("Aircraft projection conflicts with its raw owner.")
		return error.is_empty()
