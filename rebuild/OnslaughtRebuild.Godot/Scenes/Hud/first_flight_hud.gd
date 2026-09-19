# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends CanvasLayer
## Standard-engine production HUD. Scene Controls own layout and blend order;
## a single detached drawing snapshot enters here. No simulation/input/audio.
const Assets = preload("res://Scenes/Hud/hud_assets.gd")
const Part = preload("res://Scenes/Hud/hud_part.gd")
const BaseDraw = preload("res://Scenes/Hud/hud_base_draw.gd")
const GlowDraw = preload("res://Scenes/Hud/hud_glow_draw.gd")
const TextDraw = preload("res://Scenes/Hud/hud_text_draw.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const MessagePanel = preload("res://Client/message_panel.gd")
const Model = preload("res://Client/hud_presentation.gd")
const Simulation = preload("res://Core/simulation_constants.gd")
const Timing = preload("res://Core/mission_timing.gd")
const BATCH_SCHEMA: String = "onslaught-hud-drawing-snapshot.v1"
@export var show_editor_illustration: bool = true:
	set(value):
		show_editor_illustration = value
		if Engine.is_editor_hint() and is_node_ready():
			if value:
				show_illustration()
			else:
				$Surface.hide()
var ready_for_snapshot: bool = false
var error_message: String = ""
var _assets: Assets
var _base: BaseDraw
var _glow: GlowDraw
var _text: TextDraw
var _state: Dictionary = {}
var _parts: Array[Part] = []
var _model: Model
var _catalog: Dictionary = {}
var _constants: Dictionary = {}


## Production defaults stay with the native simulation definitions. They are
## not exported Inspector overrides and editor entry still refuses a live model.
func configure_for_gameplay(authored_allegiance: Variant, catalog: Variant) -> Dictionary:
	return configure_model(authored_allegiance, catalog, {
		"maximum_energy": Simulation.MAXIMUM_ENERGY, "maximum_hull": Simulation.MAXIMUM_HULL,
		"ticks_per_second": Simulation.TICKS_PER_SECOND,
		"damage_flash_lifetime_ticks": Simulation.LEVEL100_DAMAGE_FLASH_LIFETIME_TICKS,
		"message_box_allowed_tick": Timing.MESSAGE_BOX_ALLOWED_TICK})


## The temporary host passes one verified catalog batch and authored allegiance.
## This is an injected trust boundary, not a second manifest parser. The editor
## illustration never calls this route and never creates a live model.
func configure_model(authored_allegiance: Variant, catalog: Variant, constants: Variant) -> Dictionary:
	if Engine.is_editor_hint():
		return _failure("Editor illustration cannot initialize a live HUD model.")
	if typeof(authored_allegiance) != TYPE_DICTIONARY or typeof(catalog) != TYPE_DICTIONARY or catalog.get("schema") != "onslaught-hud-verified-catalog.v1":
		return _failure("HUD requires the verified catalog and authored allegiance batch.")
	if not _matches(constants, {"maximum_energy": "positive", "maximum_hull": "positive", "ticks_per_second": "positive", "damage_flash_lifetime_ticks": "positive", "message_box_allowed_tick": "int"}):
		return _failure("HUD requires the exact source-owned frame constants.")
	for key: String in ["messages", "help", "terminal"]:
		if typeof(catalog.get(key)) != TYPE_DICTIONARY:
			return _failure("Verified HUD catalog lacks " + key + ".")
	for key: Variant in authored_allegiance:
		if typeof(key) != TYPE_STRING or not _matches(authored_allegiance[key], "int"):
			return _failure("Authored HUD allegiance is not a String/Int32 table.")
	if catalog.messages.size() != 51 or catalog.help.size() != 6:
		return _failure("Verified HUD catalog has the wrong message/help extent.")
	for table: Dictionary in [catalog.messages, catalog.help]:
		for key: Variant in table:
			if not _matches(key, "int") or not _matches(table[key], "text"):
				return _failure("Verified HUD text table is malformed.")
	if not _matches(catalog.terminal, {"victory": "text", "defeat": "text", "tutorial_broken": "text", "player_death": "text", "water": "text"}):
		return _failure("Verified HUD terminal text is malformed.")
	_model = Model.new(authored_allegiance)
	_catalog = catalog.duplicate(true)
	_constants = constants.duplicate(true)
	return {"ok": true}

func consume_events(events: Variant) -> Dictionary:
	return _failure("HUD model has not been configured.") if _model == null else _model.consume(events)

## One coarse Core-facts update. Model projection, schedule lookup, type-on,
## portrait/noise phase and terminal fade now all have a single native owner.
func update_from_facts(facts: Variant, frame: Variant) -> Dictionary:
	if _model == null:
		return _failure("HUD model has not been configured.")
	var projected: Dictionary = _model.project(facts)
	if not projected.ok:
		return projected
	var hud: Dictionary = projected.value
	var batch: Dictionary = _constants.duplicate(true)
	batch.schema = BATCH_SCHEMA
	batch.frame = frame
	batch.hud = hud
	var delivery: Variant = hud.active_message
	if delivery != null and not _catalog.messages.has(delivery.message_id):
		return _with_delivery_ids(_failure("Released HUD catalog has no message %d." % int(delivery.message_id)), hud)
	batch.message = null if delivery == null else {"text": _catalog.messages[delivery.message_id]}
	batch.speaker = null if delivery == null else delivery.speaker
	var entry: Variant = Model.active_at(hud.delivered_messages, int(facts.mission.tick))
	var available: bool = entry != null and delivery != null and delivery.message_id == entry.delivery.message_id
	var elapsed: float = 0.0
	var length: float = 0.0
	if available:
		elapsed = float(clampi(_int32(int(facts.mission.tick) - int(entry.start_tick)), 0, int(entry.duration_ticks))) / float(_constants.ticks_per_second)
		length = float(entry.duration_ticks) / float(_constants.ticks_per_second)
	batch.playback = {"is_available": available, "position_seconds": elapsed, "length_seconds": length, "playing": available}
	batch.portrait_pose = portrait_pose(int(delivery.message_id), elapsed) if available else null
	var noise_elapsed: float = 0.0 if entry == null else float(clampi(_int32(int(facts.mission.tick) - int(entry.start_tick)), 0, int(entry.duration_ticks))) / float(_constants.ticks_per_second)
	batch.noise_phase = 0 if entry == null else noise_phase(int(entry.delivery.message_id), noise_elapsed)
	batch.socket = Model.select_lower_right_socket(Model.message_box_holds_active_message(hud.delivered_messages, int(facts.mission.tick)), int(hud.battle_line.influence_map))
	var help_texts: Array = []
	for prompt: int in hud.active_help:
		if not _catalog.help.has(prompt):
			return _with_delivery_ids(_failure("Released HUD catalog has no help prompt %d." % prompt), hud)
		help_texts.append(_catalog.help[prompt])
	batch.help_texts = help_texts
	batch.terminal_title = ""
	batch.terminal_reason = ""
	if hud.terminal.visible:
		if int(hud.terminal.outcome) not in [1, 2]:
			return _with_delivery_ids(_failure("Visible HUD terminal has no terminal outcome."), hud)
		batch.terminal_title = _catalog.terminal.victory if int(hud.terminal.outcome) == 1 else _catalog.terminal.defeat
		if int(hud.terminal.outcome) == 2:
			var reasons: Dictionary = {1: "tutorial_broken", 2: "player_death", 3: "water"}
			if not reasons.has(hud.terminal.failure_reason):
				return _with_delivery_ids(_failure("HUD loss has no released failure string."), hud)
			batch.terminal_reason = _catalog.terminal[reasons[hud.terminal.failure_reason]]
	var updated: Dictionary = set_snapshot(batch)
	if not updated.ok:
		return _with_delivery_ids(updated, hud)
	return {"ok": true, "value": presentation_info()}

static func _with_delivery_ids(result: Dictionary, hud: Dictionary) -> Dictionary:
	# The former C# owner published delivered IDs immediately after Project,
	# before a missing catalog row could fail. Keep that observable prefix even
	# when the previous visible drawing snapshot remains intact.
	var output: Dictionary = result.duplicate(true)
	var ids := PackedInt32Array()
	for delivery: Dictionary in hud.delivered_messages:
		ids.append(delivery.message_id)
	output.delivered_message_ids = ids
	return output

func presentation_info() -> Dictionary:
	if _state.is_empty():
		return {}
	var hud: Dictionary = _state.hud
	var ids := PackedInt32Array()
	for delivery: Dictionary in hud.delivered_messages:
		ids.append(delivery.message_id)
	return {"objective_count": hud.objectives.size(), "delivered_message_count": hud.delivered_messages.size(),
		"delivered_help_count": hud.delivered_help.size(), "delivered_message_ids": ids,
		"energy": _state.frame.energy, "shield": _state.frame.shield, "health": _state.frame.hull,
		"battle_line_available": hud.battle_line.has_influence_values and hud.battle_line.influence_permille.size() == Model.influence_nodes().size(),
		"socket": _state.socket, "playback_available": _state.playback.is_available,
		"playing": _state.playback.get("playing", false), "playback_position": _state.playback.position_seconds,
		"playback_length": _state.playback.get("length_seconds", 0.0)}

static func _int32(value: int) -> int:
	return ((value + 2147483648) & 0xffffffff) - 2147483648

## Existing deterministic reconstruction phases, not a newly claimed retail RNG.
## Actual portrait pose weights and the 20Hz timer interval remain unchanged.
static func _multiply_u32(left: int, right: int) -> int:
	# Each intermediate is below 2^48. The original uint product wraps at 32
	# bits; negative signed message IDs must not first overflow signed64.
	var word: int = left & 0xffffffff
	var factor: int = right & 0xffffffff
	return (((word & 0xffff) * factor) + ((((word >> 16) * factor) & 0xffff) << 16)) & 0xffffffff

static func portrait_pose(message_id: int, elapsed_seconds: float) -> int:
	var frame_index: int = maxi(0, int(floor(elapsed_seconds / 0.05)))
	var value: int = _multiply_u32(message_id, 0x9e3779b9) ^ _multiply_u32(frame_index, 0x85ebca6b)
	value ^= value >> 16
	var weighted: int = value % 100
	return 0 if weighted < 8 else 1 if weighted < 20 else 2 if weighted < 60 else 3

static func noise_phase(message_id: int, elapsed_seconds: float) -> int:
	var frame_index: int = maxi(0, int(floor(elapsed_seconds / 0.05)))
	var value: int = _multiply_u32(message_id, 0xc2b2ae35) ^ _multiply_u32(frame_index, 0x27d4eb2f)
	value ^= value >> 15
	return value % 16

func _get_configuration_warnings() -> PackedStringArray:
	return PackedStringArray([error_message]) if not error_message.is_empty() else PackedStringArray()

func _ready() -> void:
	var result: Dictionary = initialize()
	if not result.ok:
		$Surface.hide()
		return
	if Engine.is_editor_hint() and show_editor_illustration:
		show_illustration()
	elif _state.is_empty():
		$Surface.hide()

func initialize() -> Dictionary:
	if ready_for_snapshot:
		return {"ok": true}
	var loaded := Assets.new()
	var result: Dictionary = loaded.initialize()
	if not result.ok:
		error_message = result.error
		update_configuration_warnings()
		return result
	var parts: Array[Part] = []
	for node: Node in find_children("*", "Control", true, false):
		if node is Part:
			parts.append(node)
		elif node is TextureRect and node.texture != null and node.texture.has_method("ensure_loaded"):
			var admitted: Dictionary = node.texture.ensure_loaded()
			if not admitted.ok:
				return admitted
	if parts.size() != 22:
		return {"ok": false, "error": "HUD scene must retain its 22 authored drawing parts."}
	_assets = loaded
	_parts = parts
	_base = BaseDraw.new()
	_glow = GlowDraw.new()
	_text = TextDraw.new()
	ready_for_snapshot = true
	error_message = ""
	$Surface.hide()
	update_configuration_warnings()
	return {"ok": true}

func set_snapshot(batch: Variant) -> Dictionary:
	var admitted: Dictionary = _admit(batch)
	if not admitted.ok:
		return admitted
	var result: Dictionary = initialize()
	if not result.ok:
		return result
	var next: Dictionary = batch.duplicate(true)
	var message_window: Array = []
	if next.message != null:
		var wrapped: Dictionary = MessagePanel.wrap(next.message.text)
		if not wrapped.ok:
			return wrapped
		var revealed: Dictionary = MessagePanel.revealed_characters(next.playback.position_seconds) if next.playback.is_available else MessagePanel.source_length(wrapped.value)
		if not revealed.ok:
			return revealed
		var window: Dictionary = MessagePanel.window(wrapped.value, revealed.value)
		if not window.ok:
			return window
		message_window = window.value
	next.message_window = message_window
	var terminal: Dictionary = next.hud.terminal
	var prior: Dictionary = _state.get("hud", {}).get("terminal", {"visible": false})
	var entering: bool = terminal.visible and (not prior.visible or prior.get("outcome") != terminal.outcome or prior.get("failure_reason") != terminal.failure_reason)
	next.terminal_darkener_alpha = mini(0xa0, (0 if entering else int(_state.get("terminal_darkener_alpha", 0))) + 0x10) if terminal.visible else 0
	_state = next
	_base.bind(_assets, _state)
	_glow.bind(_assets, _state)
	_text.bind(_assets, _state)
	$Surface.show()
	for part: Part in _parts:
		part.queue_redraw()
	return {"ok": true}

func draw_part(part: Part) -> void:
	if not ready_for_snapshot or _state.is_empty():
		return
	if int(part.part) <= 8:
		_base.render(part)
	elif int(part.part) <= 17:
		_glow.render(part)
	else:
		_text.render(part)

func snapshot() -> Dictionary:
	return _state.duplicate(true)

func show_illustration() -> void:
	# The same production path and real pages, frozen with full gauges. These
	# source-pinned display values are an explicit editor illustration, not a
	# fabricated mission, actor, delivery, threat or input state.
	if not Engine.is_editor_hint():
		return
	var result: Dictionary = set_snapshot(illustration_snapshot())
	if not result.ok:
		error_message = result.error
		update_configuration_warnings()

static func illustration_snapshot() -> Dictionary:
	return {"schema": BATCH_SCHEMA, "frame": {"tick": 0, "energy": 8000, "shield": 8000, "hull": 20000,
		"facing_yaw_micro_rad": 0, "player_position": {"x": 0, "z": 0}, "mission_tick": 121},
		"maximum_energy": 8000, "maximum_hull": 20000, "ticks_per_second": 20,
		"damage_flash_lifetime_ticks": 40, "message_box_allowed_tick": 121,
		"hud": {"weapon": {"selected_weapon": null, "pulse_cannon_enabled": false, "vulcan_cannon_enabled": false,
			"selection_panel_visible": null, "selection_slot": null, "pulse_heat_permille": null, "vulcan_ammo": null,
			"charge_permille": null, "pulse_cannon_overheated": null},
			"contacts": [], "objectives": [], "threats": [], "damage_flashes": [], "target": null,
			"active_message": null, "emphasized_parts": [], "delivered_messages": [], "active_help": [], "delivered_help": [],
			"battle_line": {"has_influence_values": false, "influence_permille": [], "influence_map": 0},
			"terminal": {"visible": false, "outcome": 0, "failure_reason": 0, "ticks_remaining": 0}},
		"socket": 0, "message": null, "speaker": null, "portrait_pose": null, "noise_phase": 0,
		"playback": {"is_available": false, "position_seconds": 0.0}, "help_texts": [], "terminal_title": "", "terminal_reason": ""}

static func _admit(batch: Variant) -> Dictionary:
	if typeof(batch) != TYPE_DICTIONARY or batch.get("schema") != BATCH_SCHEMA:
		return _failure("The HUD drawing snapshot schema is missing or unsupported.")
	var schema: Dictionary = {"frame": {"tick": "int", "energy": "int", "shield": "int", "hull": "int",
		"facing_yaw_micro_rad": "int", "player_position": {"x": "int", "z": "int"}, "mission_tick": "int"},
		"maximum_energy": "positive", "maximum_hull": "positive", "ticks_per_second": "positive",
		"damage_flash_lifetime_ticks": "positive", "message_box_allowed_tick": "int",
		"socket": "int", "speaker": "?int", "portrait_pose": "?int", "noise_phase": "int",
		"message": "message", "playback": {"is_available": "bool", "position_seconds": "number"},
		"help_texts": ["text"], "terminal_title": "text", "terminal_reason": "text",
		"hud": {"weapon": {"selected_weapon": "?int", "pulse_cannon_enabled": "bool", "vulcan_cannon_enabled": "bool",
			"selection_panel_visible": "?bool", "selection_slot": "?int", "pulse_heat_permille": "?int", "vulcan_ammo": "?int",
			"charge_permille": "?int", "pulse_cannon_overheated": "?bool"},
			"contacts": [{"id": "int", "position": {"x": "int", "z": "int"}, "velocity": {"x": "int", "z": "int"},
				"allegiance": "int", "size": "int", "is_objective": "bool", "on_scanner": "bool"}],
			"objectives": [{"actor_id": "int", "thing_name": "text", "position_millimeters": {"x": "int", "y": "int", "z": "int"}}],
			"threats": [{"relative_yaw_micro_rad": "int", "ticks_remaining": "int"}],
			"damage_flashes": [{"relative_yaw_micro_rad": "int", "ticks_remaining": "int"}],
			"target": "target", "emphasized_parts": ["int"], "delivered_messages": "array", "delivered_help": ["int"],
			"battle_line": {"has_influence_values": "bool", "influence_permille": ["int"], "influence_map": "int"},
			"terminal": {"visible": "bool", "outcome": "int", "failure_reason": "int", "ticks_remaining": "int"}}}
	if not _matches(batch, schema):
		return _failure("The HUD snapshot fields do not match the drawing contract.")
	if int(batch.ticks_per_second) < 5 or int(batch.socket) < 0 or int(batch.socket) > 3 or int(batch.noise_phase) < 0:
		return _failure("HUD cadence, socket or noise phase is outside its supported range.")
	if batch.portrait_pose != null and (int(batch.portrait_pose) < 0 or int(batch.portrait_pose) > 3):
		return _failure("A HUD portrait pose must be between zero and three.")
	if batch.hud.terminal.visible and int(batch.hud.terminal.outcome) not in [1, 2]:
		return _failure("A visible terminal overlay requires a terminal outcome.")
	return {"ok": true}

static func _matches(value: Variant, shape: Variant) -> bool:
	if typeof(shape) == TYPE_DICTIONARY:
		if typeof(value) != TYPE_DICTIONARY:
			return false
		for key: String in shape:
			if not value.has(key) or not _matches(value[key], shape[key]):
				return false
		return true
	if typeof(shape) == TYPE_ARRAY:
		if typeof(value) != TYPE_ARRAY and typeof(value) != TYPE_PACKED_INT32_ARRAY:
			return false
		for item: Variant in value:
			if not _matches(item, shape[0]):
				return false
		return true
	match String(shape):
		"int", "positive", "?int":
			return (value == null and shape == "?int") or (typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647 and (shape != "positive" or value > 0))
		"bool", "?bool": return typeof(value) == TYPE_BOOL or (value == null and shape == "?bool")
		"number": return (typeof(value) == TYPE_FLOAT or typeof(value) == TYPE_INT) and is_finite(float(value))
		"text": return Text.units(value).ok and value != null
		"array": return typeof(value) == TYPE_ARRAY
		"message": return value == null or _matches(value, {"text": "text"})
		"target": return value == null or _matches(value, {"contact_id": "int", "hull_permille": "int", "predicted_position": {"x": "int", "z": "int"}, "lock_permille": "int"})
	return false

static func _failure(message: String) -> Dictionary:
	return {"ok": false, "error": message}
