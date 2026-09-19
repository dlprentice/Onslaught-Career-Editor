# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Pure port of Level100HudPresentation.cs and the tick lookup in
## Level100MessageSchedule.cs. Their source/evidence qualifications still apply:
## influence uses equal actor contributions, with smoothing not yet recovered;
## the scanner's additional retail unit flags are not represented by Core;
## portrait RNG/target/weapon meter facts are NOT inferred here. The three-tick
## text clear lead is the existing bounded measurement, not a new recovered law.
##
## consume/project admit a narrow, snake_case Core fact projection and return
## explicit results. No presentation node, audio clock, filesystem or physics is
## consulted. State and successful projection results are detached copies.

const Float32 = preload("res://Core/retail_float24.gd")

const FRIENDLY: int = 0
const ENEMY: int = 1
const NEUTRAL: int = 2
const CONTACT_MEDIUM: int = 1
const INFLUENCE_UNKNOWN: int = 0
const INFLUENCE_EMPTY: int = 1
const INFLUENCE_POPULATED: int = 2
const SOCKET_INDETERMINATE: int = 0
const SOCKET_PORTRAIT_AND_NOISE: int = 1
const SOCKET_INFLUENCE_OVERLAY: int = 2
const SOCKET_FORSETI_ICON: int = 3
const SCANNER_CENTRE_X: float = 68.0
const SCANNER_CENTRE_Y: float = 417.0
const SCANNER_CLAMP_RADIUS: float = 46.0
const SCANNER_CULL_RADIUS_SQUARED: float = 8464.0
# Raw float32 words avoid an implicit binary64 constant-folding contract.
const SCANNER_SCALE_WORD: int = 0x3ed55555 # 40f / 96f
const SCANNER_FADE_WORD: int = 0x3cb21643 # 0.021739131f
const FRIENDLY_TINT_RGB: int = 0x5050af
const FRIENDLY_HIGHLIGHT_ADD: int = 0x404050
const ENEMY_TINT_RGB: int = 0xaf0808
const ENEMY_HIGHLIGHT_ADD: int = 0x504848
const NEUTRAL_TINT_RGB: int = 0x606060
const NEUTRAL_HIGHLIGHT_ADD: int = 0x101010
const OBJECTIVE_TINT_RGB: int = 0xffff00
const DAMAGE_FLASH_LIFETIME_TICKS: int = 40
const MESSAGE_TEXT_CLEAR_LEAD_TICKS: int = 3
const MESSAGE_ADVANCE_DELAY_TICKS: int = 4
const TICKS_PER_SECOND: int = 20
const _SPEAKERS: Array[int] = [919601, 1508464, 10565784]
const _HELP_PROMPTS: Array[int] = [1197607, 8268984, 17186000, 31505972, 2302408, 488286858]
const _NODE_COORDINATES: Array = [
	[-3688, 83750], [-30688, 59750], [-70688, 51750], [-95688, -42250],
	[-99688, -3250], [-109688, 30750], [-66688, 16750], [-77688, 84750],
	[-38688, 94750], [33313, 69750], [-688, 48750], [33813, 21250], [-13188, 12250],
]
const _LINK_ENDPOINTS: Array = [
	[0, 9], [0, 10], [0, 1], [10, 1], [1, 8], [1, 7], [1, 2], [2, 5],
	[2, 6], [12, 2], [2, 7], [10, 9], [10, 11], [12, 11], [11, 9],
	[10, 12], [6, 12], [8, 7], [6, 5], [6, 4], [5, 4], [4, 3],
]

var _authored_allegiance: Dictionary = {}
var _delivered_messages: Array[Dictionary] = []
var _delivered_help: Array[int] = []
var _last_projected_mission_tick: int = -2147483648
var _initialization_error: String = ""


func _init(authored_allegiance_by_definition: Variant = null) -> void:
	if authored_allegiance_by_definition == null:
		return
	if not authored_allegiance_by_definition is Dictionary:
		_initialization_error = "Authored allegiance must be a Dictionary of String to Int32, or null."
		return
	for key: Variant in authored_allegiance_by_definition:
		if not key is String or not _is_int32(authored_allegiance_by_definition[key]):
			_initialization_error = "Authored allegiance requires String keys and exact Int32 values."
			return
	_authored_allegiance = authored_allegiance_by_definition.duplicate(true)


func consume(events: Variant) -> Dictionary:
	if not _initialization_error.is_empty():
		return _failure("ArgumentException", _initialization_error)
	if events == null:
		return _failure("ArgumentNullException", "events must not be null.")
	if not events is Array:
		return _failure("ArgumentException", "events must be an Array.")
	for event: Variant in events:
		# The managed switch ignores null and every unrelated event subtype.
		if event == null:
			continue
		if not event is Dictionary or not event.get("kind") is String:
			return _failure("ArgumentException", "An event requires a String kind.")
		if event.kind == "message":
			if not _has_int32_fields(event, ["tick", "speaker_id", "message_id", "expected_playback_ticks"]) or not event.get("script_waits_for_duration") is bool:
				return _failure("ArgumentException", "A message event requires its exact Int32 and Boolean fields.")
			if not _SPEAKERS.has(event.speaker_id):
				return _failure("InvalidDataException", "Released Level 100 speaker ID %d is unsupported." % event.speaker_id)
			_delivered_messages.append({"tick": event.tick, "speaker": event.speaker_id,
				"message_id": event.message_id, "script_waits_for_duration": event.script_waits_for_duration,
				"expected_playback_ticks": event.expected_playback_ticks})
		elif event.kind == "help":
			if not _has_int32_fields(event, ["tick", "help_message_id"]):
				return _failure("ArgumentException", "A help event requires exact Int32 fields.")
			if not _HELP_PROMPTS.has(event.help_message_id):
				return _failure("InvalidDataException", "Released Level 100 help ID %d is unsupported." % event.help_message_id)
			_delivered_help.append(event.help_message_id)
	# Like C#, a rejected later event preserves the already consumed prefix.
	return {"ok": true}


func project(facts: Variant, _ignored_playback: Variant = null) -> Dictionary:
	if not _initialization_error.is_empty():
		return _failure("ArgumentException", _initialization_error)
	if facts == null:
		return _failure("ArgumentNullException", "snapshot must not be null.")
	var admission: String = _facts_error(facts)
	if not admission.is_empty():
		return _failure("ArgumentException", admission)
	var snapshot: Dictionary = facts
	var mission: Dictionary = snapshot.mission
	var objectives: Array[Dictionary] = []
	for actor: Dictionary in snapshot.actors:
		if actor.active and actor.is_objective and actor.lifecycle != 2:
			objectives.append({"actor_id": actor.actor_id, "thing_name": actor.name,
				"position_millimeters": actor.position.duplicate(true)})
	if mission.tick < _last_projected_mission_tick:
		_delivered_messages.clear()
		_delivered_help.clear()
	_last_projected_mission_tick = mission.tick
	var active_entry: Variant = active_at(_delivered_messages, mission.tick)
	# Mode/failure errors deliberately occur after the mission restart handling,
	# at the same semantic point as the managed projection.
	if snapshot.mode != 0 and snapshot.mode != 1:
		return _failure("ArgumentOutOfRangeException", "Mode is not Walker or Jet.")
	var mission_weapon: int = snapshot.walker_selected_weapon if snapshot.mode == 0 else snapshot.jet_selected_weapon
	var selected_weapon: Variant = null
	if mission_weapon == 1:
		selected_weapon = 1
	elif mission_weapon == 2 or mission_weapon == 3:
		selected_weapon = 2
	var terminal_ticks: int = mission.terminal_ticks_remaining
	if mission.outcome == 2:
		if terminal_ticks < 0:
			return _failure("ArgumentOutOfRangeException", "TerminalTicksRemaining must be nonnegative for a loss.")
		if mission.failure_reason < 1 or mission.failure_reason > 3:
			return _failure("ArgumentOutOfRangeException", "FailureReason has no retained terminal duration.")
		var delay: int = 0 if mission.failure_reason == 1 else 260
		terminal_ticks = clampi(_int32(terminal_ticks - delay), 0, 40)
	var emphasized: Array[int] = []
	for part: int in range(6):
		if (snapshot.hud_emphasis_mask & (1 << part)) != 0:
			emphasized.append(part)
	var commands: Dictionary = _commanded_allegiances(snapshot.commanded_allegiances)
	var result: Dictionary = {
		"weapon": {"selected_weapon": selected_weapon,
			"pulse_cannon_enabled": mission.pulse_cannon_availability == 2,
			"vulcan_cannon_enabled": mission.twin_vulcan_availability == 2 or mission.mech_vulcan_availability == 2,
			"selection_panel_visible": null, "selection_slot": null, "pulse_heat_permille": null,
			"vulcan_ammo": null, "charge_permille": null, "pulse_cannon_overheated": null},
		"contacts": _project_contacts(snapshot, commands), "objectives": objectives,
		"threats": [], "damage_flashes": _project_damage_flashes(snapshot), "target": null,
		"active_message": null if active_entry == null else active_entry.delivery,
		"emphasized_parts": emphasized, "delivered_messages": _delivered_messages.duplicate(true),
		"active_help": [], "delivered_help": _delivered_help.duplicate(),
		"battle_line": _project_battle_line(snapshot, commands),
		"terminal": {"visible": mission.outcome != 0 and terminal_ticks > 0,
			"outcome": mission.outcome, "failure_reason": mission.failure_reason, "ticks_remaining": terminal_ticks},
	}
	return {"ok": true, "value": result}


func state_snapshot() -> Dictionary:
	return {"last_projected_mission_tick": _last_projected_mission_tick,
		"delivered_messages": _delivered_messages.duplicate(true), "delivered_help": _delivered_help.duplicate()}


static func scanner_tint_rgb(allegiance: int) -> int:
	return FRIENDLY_TINT_RGB if allegiance == FRIENDLY else ENEMY_TINT_RGB if allegiance == ENEMY else NEUTRAL_TINT_RGB


static func scanner_place(delta_x: float, delta_z: float, yaw_radians: float) -> Dictionary:
	return _scanner(delta_x, delta_z, yaw_radians, false)


static func scanner_place_objective(delta_x: float, delta_z: float, yaw_radians: float) -> Dictionary:
	return _scanner(delta_x, delta_z, yaw_radians, true)


static func scanner_place_in_design_space(delta_x: float, delta_z: float, yaw_radians: float) -> Dictionary:
	var result: Dictionary = scanner_place(delta_x, delta_z, yaw_radians)
	if result.drawn:
		result.offset_x = _f32(SCANNER_CENTRE_X + result.offset_x)
		result.offset_y = _f32(SCANNER_CENTRE_Y + result.offset_y)
	return result


static func scanner_sine_cosine(angle: float) -> Vector2:
	# The pinned single-precision engine routes Vector2.from_angle through
	# Math::cos/sin(real_t), selecting the native float overload. GDScript's
	# scalar sin/cos first compute a double; casting afterward differs from
	# MathF on some inputs. Direct bit fixtures gate this engine math boundary.
	# Vector2 stores cosine in x and sine in y; no scene/physics owner is used.
	return Vector2.from_angle(_f32(angle))


static func select_lower_right_socket(holds_active_message: bool, influence_map: int) -> int:
	if holds_active_message:
		return SOCKET_PORTRAIT_AND_NOISE
	return SOCKET_INFLUENCE_OVERLAY if influence_map == INFLUENCE_POPULATED else SOCKET_FORSETI_ICON if influence_map == INFLUENCE_EMPTY else SOCKET_INDETERMINATE


static func influence_nodes() -> Array[Dictionary]:
	var nodes: Array[Dictionary] = []
	for index: int in range(_NODE_COORDINATES.size()):
		nodes.append({"id": index, "position": {"x": _NODE_COORDINATES[index][0], "z": _NODE_COORDINATES[index][1]}, "radius_millimeters": 10000})
	return nodes


static func influence_links() -> Array[Dictionary]:
	var links: Array[Dictionary] = []
	for pair: Array in _LINK_ENDPOINTS:
		links.append({"first_node_id": pair[0], "second_node_id": pair[1]})
	return links


## These schedule helpers consume the admitted delivery records returned by this
## model. The list remains in arrival order; an overlap selects its first entry.
static func display_ticks(delivery: Dictionary) -> int:
	return maxi(1, delivery.expected_playback_ticks)


static func visible_ticks(delivery: Dictionary) -> int:
	return maxi(1, _int32(display_ticks(delivery) - MESSAGE_TEXT_CLEAR_LEAD_TICKS))


static func active_at(deliveries: Array, tick: int) -> Variant:
	for delivery: Dictionary in deliveries:
		if tick >= delivery.tick and tick < _int32(delivery.tick + visible_ticks(delivery)):
			return {"delivery": delivery.duplicate(true), "start_tick": delivery.tick, "duration_ticks": display_ticks(delivery)}
	return null


static func message_box_holds_active_message(deliveries: Array, tick: int) -> bool:
	for delivery: Dictionary in deliveries:
		if tick >= delivery.tick and tick < _int32(delivery.tick + visible_ticks(delivery)):
			return true
		var end: int = _int32(delivery.tick + display_ticks(delivery))
		if tick >= end and tick < _int32(end + MESSAGE_ADVANCE_DELAY_TICKS):
			return true
	return false


static func _scanner(delta_x: float, delta_z: float, yaw_radians: float, objective: bool) -> Dictionary:
	# Explicit binary32 stores at every C# float operation. These are NOT the
	# extended-exponent float24 operations used by deterministic simulation.
	var dx: float = _f32(delta_x)
	var dz: float = _f32(delta_z)
	var yaw: float = _f32(yaw_radians)
	var scale_per_unit: float = Float32.read_word(SCANNER_SCALE_WORD)
	var angle_axes: Vector2 = scanner_sine_cosine(-yaw)
	var sine: float = _f32(angle_axes.y * scale_per_unit)
	var cosine: float = _f32(angle_axes.x * scale_per_unit)
	var rx: float = _f32(_f32(dx * cosine) - _f32(dz * sine))
	var ry: float = _f32(_f32(dx * sine) + _f32(dz * cosine))
	var radius_squared: float = _f32(_f32(rx * rx) + _f32(ry * ry))
	if not objective and not radius_squared < SCANNER_CULL_RADIUS_SQUARED:
		return {"offset_x": 0.0, "offset_y": 0.0, "alpha": 0, "drawn": false, "clamped": false}
	var radius: float = _f32(sqrt(radius_squared))
	# Managed IEEE division gives +infinity at a zero radius. GDScript must not
	# invoke its divide-by-zero error path, which could abort only this helper.
	var radial_scale: float = INF if radius == 0.0 else _f32(SCANNER_CLAMP_RADIUS / radius)
	var clamped: bool = radial_scale < 1.0
	var alpha: int = 255
	if clamped:
		rx = _f32(rx * radial_scale)
		ry = _f32(ry * radial_scale)
		if not objective:
			var fade: float = _f32(1.0 - _f32(_f32(radius - SCANNER_CLAMP_RADIUS) * Float32.read_word(SCANNER_FADE_WORD)))
			alpha = clampi(_round_even(_f32(fade * 255.0)), 0, 255)
	return {"offset_x": rx, "offset_y": -ry, "alpha": alpha, "drawn": true, "clamped": clamped}


func _project_contacts(snapshot: Dictionary, commands: Dictionary) -> Array[Dictionary]:
	var contacts: Array[Dictionary] = []
	var yaw: float = _f32(_f32(snapshot.facing_yaw_micro_rad) / 1000000.0)
	for actor: Dictionary in snapshot.actors:
		if not actor.active or actor.lifecycle == 2 or actor.has_trigger or actor.name == "Player 1":
			continue
		# The C# Int32 coordinate subtraction wraps BEFORE conversion to float.
		var dx: float = _f32(_f32(_int32(actor.position.x - snapshot.player_position.x)) / 1000.0)
		var dz: float = _f32(_f32(_int32(actor.position.z - snapshot.player_position.z)) / 1000.0)
		var placement: Dictionary = scanner_place(dx, dz, yaw)
		contacts.append({"id": actor.actor_id, "position": {"x": actor.position.x, "z": actor.position.z},
			"velocity": {"x": actor.velocity.x, "z": actor.velocity.z},
			"allegiance": _resolve_allegiance(actor, commands), "size": CONTACT_MEDIUM,
			"is_objective": actor.is_objective, "on_scanner": placement.drawn})
	return contacts


static func _project_damage_flashes(snapshot: Dictionary) -> Array[Dictionary]:
	var flashes: Array[Dictionary] = []
	for flash: Dictionary in snapshot.damage_flashes:
		var remaining: int = _int32(DAMAGE_FLASH_LIFETIME_TICKS - _int32(snapshot.tick - flash.start_tick))
		if remaining > 0:
			flashes.append({"relative_yaw_micro_rad": flash.relative_yaw_micro_rad, "ticks_remaining": remaining})
	return flashes


func _project_battle_line(snapshot: Dictionary, commands: Dictionary) -> Dictionary:
	var friendly: Array[int] = []
	var enemy: Array[int] = []
	friendly.resize(_NODE_COORDINATES.size())
	enemy.resize(_NODE_COORDINATES.size())
	friendly.fill(0)
	enemy.fill(0)
	for index: int in range(_NODE_COORDINATES.size()):
		for actor: Dictionary in snapshot.actors:
			if not actor.active or actor.lifecycle == 2 or actor.has_trigger:
				continue
			# Int64 multiplication/addition intentionally retains C# unchecked
			# wrap at extreme Int32 positions; no floating-distance substitute.
			var dx: int = actor.position.x - _NODE_COORDINATES[index][0]
			var dz: int = actor.position.z - _NODE_COORDINATES[index][1]
			if dx * dx + dz * dz > 100000000:
				continue
			var allegiance: int = _resolve_allegiance(actor, commands)
			if allegiance == FRIENDLY:
				friendly[index] = _int32(friendly[index] + 1)
			elif allegiance == ENEMY:
				enemy[index] = _int32(enemy[index] + 1)
	var influence: Array[int] = []
	for index: int in range(_NODE_COORDINATES.size()):
		var total: int = _int32(friendly[index] + enemy[index])
		if total > 0:
			var numerator: int = _int32(_int32(friendly[index] - enemy[index]) * 1000)
			@warning_ignore("integer_division")
			var ratio: int = numerator / total
			influence.append(_int16(ratio))
			continue
		var neighbor_friendly: int = 0
		var neighbor_enemy: int = 0
		for link: Array in _LINK_ENDPOINTS:
			var neighbor: int = link[1] if link[0] == index else link[0] if link[1] == index else -1
			if neighbor >= 0:
				neighbor_friendly = _int32(neighbor_friendly + friendly[neighbor])
				neighbor_enemy = _int32(neighbor_enemy + enemy[neighbor])
		influence.append(-1000 if neighbor_enemy > neighbor_friendly else 1000)
	return {"has_influence_values": true, "influence_permille": influence, "influence_map": INFLUENCE_POPULATED}


func _resolve_allegiance(actor: Dictionary, commands: Dictionary) -> int:
	var allegiance: int = commands.get(actor.actor_id, _authored_allegiance.get(actor.definition_identity, NEUTRAL))
	return allegiance if allegiance >= FRIENDLY and allegiance <= NEUTRAL else NEUTRAL


static func _commanded_allegiances(actors: Array) -> Dictionary:
	var result: Dictionary = {}
	for actor: Dictionary in actors:
		if actor.has_override:
			result[actor.actor_id] = actor.allegiance
	return result


static func _facts_error(facts: Variant) -> String:
	if not facts is Dictionary:
		return "snapshot must be a Dictionary."
	if not _has_int32_fields(facts, ["tick", "facing_yaw_micro_rad", "mode", "walker_selected_weapon", "jet_selected_weapon", "hud_emphasis_mask"]):
		return "snapshot requires exact Int32 scalar facts."
	if not _vector_is_int32(facts.get("player_position"), false):
		return "player_position requires Int32 x and z."
	var mission: Variant = facts.get("mission")
	if not mission is Dictionary or not _has_int32_fields(mission, ["tick", "pulse_cannon_availability", "twin_vulcan_availability", "mech_vulcan_availability", "outcome", "failure_reason", "terminal_ticks_remaining"]):
		return "mission requires its exact Int32 facts."
	for key: String in ["actors", "commanded_allegiances", "damage_flashes"]:
		if not facts.get(key) is Array:
			return key + " must be an Array."
	for actor: Variant in facts.actors:
		if not actor is Dictionary or not _has_int32_fields(actor, ["actor_id", "lifecycle"]):
			return "An actor requires exact Int32 identity and lifecycle."
		if not actor.get("name") is String or not actor.get("definition_identity") is String:
			return "An actor requires String name and definition_identity."
		for key: String in ["active", "is_objective", "has_trigger"]:
			if not actor.get(key) is bool:
				return "An actor requires a Boolean " + key + "."
		if not _vector_is_int32(actor.get("position"), true) or not _vector_is_int32(actor.get("velocity"), true):
			return "An actor requires Int32 x/y/z position and velocity."
	for command: Variant in facts.commanded_allegiances:
		if not command is Dictionary or not _has_int32_fields(command, ["actor_id", "allegiance"]) or not command.get("has_override") is bool:
			return "A commanded allegiance requires Int32 identity/allegiance and a Boolean override."
	for flash: Variant in facts.damage_flashes:
		if not flash is Dictionary or not _has_int32_fields(flash, ["relative_yaw_micro_rad", "start_tick"]):
			return "A damage flash requires exact Int32 yaw and start tick."
	return ""


static func _vector_is_int32(value: Variant, three_dimensions: bool) -> bool:
	return value is Dictionary and _has_int32_fields(value, ["x", "y", "z"] if three_dimensions else ["x", "z"])


static func _has_int32_fields(record: Dictionary, fields: Array) -> bool:
	for key: String in fields:
		if not _is_int32(record.get(key)):
			return false
	return true


static func _is_int32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


static func _int32(value: int) -> int:
	var word: int = value & 0xffffffff
	return word - 0x100000000 if word >= 0x80000000 else word


static func _int16(value: int) -> int:
	var word: int = value & 0xffff
	return word - 0x10000 if word >= 0x8000 else word


static func _f32(value: float) -> float:
	return Float32.store_float32(value)


static func _round_even(value: float) -> int:
	var lower: float = floor(value)
	var fraction: float = value - lower
	return int(lower + 1.0) if fraction > 0.5 or (fraction == 0.5 and (int(lower) & 1) != 0) else int(lower)


static func _failure(error_type: String, reason: String) -> Dictionary:
	return {"ok": false, "error_type": error_type, "error": reason}
