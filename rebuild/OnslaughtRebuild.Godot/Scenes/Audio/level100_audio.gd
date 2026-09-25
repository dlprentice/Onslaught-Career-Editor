# SPDX-License-Identifier: GPL-3.0-or-later
@tool
extends Node3D
## Level100Audio.cs production port. Core supplies ordered facts/events; this
## scene owns stream selection, presentation cadence/mix and player lifetimes.
## Editor inspection never configures playback, reads audio, or captures input.
## Known gap retained: the 0.3 s message handoff starts at voice Finished, not
## retail text-reveal completion. No decoder/device/audible parity is claimed.

const Catalog = preload("res://Client/audio_catalog.gd")
const MusicPolicy = preload("res://Client/music_policy.gd")
const MessageQueue = preload("res://Client/character_message_queue.gd")
const F32 = preload("res://Core/retail_float24.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const StreamRecipe = preload("res://Scenes/Audio/retail_audio_stream.gd")
const Player2D = preload("res://Scenes/Audio/retail_audio_player.gd")
const Player3D = preload("res://Scenes/Audio/retail_spatial_player.gd")
const ONE_SHOT = preload("res://Scenes/Audio/OneShot2D.tscn")
const SPATIAL = preload("res://Scenes/Audio/SpatialVoice.tscn")
const SOUND_UPDATE_SECONDS: float = 1.0 / 20.0
const CHARACTER_VOICE_LEAD_SECONDS: float = 0.2
const CHARACTER_HANDOFF_SECONDS: float = 0.3
const SOUND_OPTION_WORD: int = 0x3f4ccccd # Career.cpp:173, authored 0.8f.
const LOOP_PATHS: Dictionary = {"flight": "Attachments/Aquila/FlightLoop", "warning": "Attachments/Aquila/WarningLoop",
	"trainer": "Attachments/AirTrainer/Loop", "transport": "Attachments/Transport/Loop", "repair": "Attachments/RepairPad/Loop"}
const EFFECT_NAMES: Array[String] = ["AquilaStrafe", "AquilaHydraulics", "AquilaIncomingMissile", "AquilaTargetLocked",
	"AquilaTargetAcquired", "PulseCannonFire", "VulcanCannonFire", "MicroMissileFire", "DroneVulcanFire", "PulseImpact",
	"MissileImpact", "TargetOrTrainerDestroyed", "DroneDestroyed", "FacilityDestroyed", "AquilaDestroyed", "TransportDestroyed",
	"ComponentDebrisDestroyed", "LargeDebrisDestroyed", "HugeGroundDebrisDestroyed", "RepairCharging", "RepairFull"]
@export var frontend_music_recipe: StreamRecipe
@export var tutorial_music_recipe: StreamRecipe
@export var hull_warning_recipe: StreamRecipe
var error_message: String = ""
var _initialized: bool = false
var _exiting: bool = false
var _observer: Callable
var _voice: Player2D
var _music: Player2D
var _music_policy := MusicPolicy.new()
var _queue := MessageQueue.new()
var _recipes: Dictionary = {}
var _loop_players: Dictionary = {}
var _loop_homes: Dictionary = {}
var _live_loops: Dictionary = {}
var _spatial_volumes: Dictionary = {}
var _terminal_volumes: Dictionary = {}
var _frontend_volumes: Dictionary = {}
var _gameplay_shots: Array[Player3D] = []
var _terminal_shots: Array[Player2D] = []
var _frontend_shots: Array[Player2D] = []
var _aquila: Node3D
var _aquila_actor_id: Variant = null
var _warning_state: int = 0
var _warning_loop_state: int = 0
var _fades: Dictionary = {"flight": {"sub": 0.0, "target": 0.0, "step": 0.0, "accumulator": 0.0},
	"warning": {"sub": 0.0, "target": 0.0, "step": 0.0, "accumulator": 0.0}}
var _music_accumulator: float = 0.0
var _sound_master: float = F32.read_word(SOUND_OPTION_WORD)
var _gameplay_mix: float = 1.0
var _paused: bool = false
var _mission_start_tick: Variant = null
var _last_hostile_contact: int = 0
var _active_speaker: Variant = null
var _active_message: Variant = null
var _active_length: float = 0.0
var _voice_lead: float = 0.0
var _handoff: float = 0.0


func _validate_property(property: Dictionary) -> void:
	if property.name in ["frontend_music_recipe", "tutorial_music_recipe", "hull_warning_recipe"]:
		property.usage = int(property.usage) | PROPERTY_USAGE_READ_ONLY


func _ready() -> void:
	set_process(false)
	_voice = $CharacterVoice
	_music = $Music
	for key: String in LOOP_PATHS:
		var player: Player3D = get_node(LOOP_PATHS[key])
		_loop_players[key] = player
		_loop_homes[key] = player.get_parent()
		_remember_recipe(player.stream_recipe)
	for recipe: StreamRecipe in [frontend_music_recipe, tutorial_music_recipe, hull_warning_recipe]:
		_remember_recipe(recipe)
	if Engine.is_editor_hint():
		return
	_voice.finished.connect(_begin_handoff)
	_music.finished.connect(_music_finished)
	_voice.volume_db = _mixed_db(F32.read_word(Catalog.RETAIL_RADIO_MESSAGE_VOLUME_WORD), true, 100)
	_set_music_volume(_music_policy.snapshot().current_volume)


func configure(playback_started: Callable) -> Dictionary:
	if Engine.is_editor_hint() or not is_node_ready() or _initialized:
		return _failure("Audio configuration requires a ready runtime scene and may occur once.")
	if not playback_started.is_valid():
		return _failure("Every playback start requires the shared retirement observer.")
	var recipes: Dictionary = _validate_authored_recipes()
	if not recipes.ok:
		return recipes
	_observer = playback_started
	_initialized = true
	set_process(true)
	return _ok()


func _process(delta: float) -> void:
	var result: Dictionary = advance(delta)
	if not result.ok:
		error_message = result.error
		set_process(false)
		push_error(error_message)


## Explicit cadence entrance lets the same runtime component receive bounded
## dummy-driver checks without inventing a second audio scheduler.
func advance(delta: float) -> Dictionary:
	if not _initialized or Engine.is_editor_hint():
		return _failure("Audio is not configured for runtime.")
	var result: Dictionary = _advance_music(delta)
	if not result.ok or _paused:
		return result
	for key: String in ["flight", "warning"]:
		result = _advance_fade(key, delta)
		if not result.ok:
			return result
	_update_spatial_attenuation()
	if not is_finite(delta) or delta <= 0.0:
		return _ok()
	if _voice_lead > 0.0:
		_voice_lead -= delta
		if _voice_lead <= 0.0:
			_voice_lead = 0.0
			return _start_next_message()
		return _ok()
	if _handoff > 0.0:
		_handoff -= delta
		if _handoff <= 0.0:
			_handoff = 0.0
			_voice_lead = CHARACTER_VOICE_LEAD_SECONDS
	return _ok()


func character_message_playback() -> Dictionary:
	var playing: bool = _active_message != null and is_instance_valid(_voice) and _voice.playing
	return {"active_speaker_id": _active_speaker, "active_message_id": _active_message,
		"position_seconds": clampf(_voice.get_playback_position(), 0.0, _active_length) if playing else 0.0,
		"length_seconds": _active_length, "playing": playing, "paused": playing and _voice.stream_paused}


func tutorial_voice_playing() -> bool:
	var state: Dictionary = character_message_playback()
	return state.playing and not state.paused


func tutorial_music_playing() -> bool:
	return _music_playing(Catalog.tutorial_music())


func frontend_music_playing() -> bool:
	return _music_playing(Catalog.frontend_music())


func start_tutorial_music() -> Dictionary:
	return _play_music(MusicPolicy.Selection.TUTORIAL, Catalog.tutorial_music())


func start_frontend_music() -> Dictionary:
	return _play_music(MusicPolicy.Selection.FRONTEND, Catalog.frontend_music())


func stop_music() -> Dictionary:
	var result: Dictionary = _apply_music(_music_policy.kill())
	_music_accumulator = 0.0
	return result


func _play_music(selection: int, recipe: Dictionary) -> Dictionary:
	if not _initialized:
		return _failure("Audio is not configured for runtime.")
	return _ok() if _music_playing(recipe) else _apply_music(_music_policy.play_selection(selection, recipe.resource_path))


func _music_playing(recipe: Dictionary) -> bool:
	var state: Dictionary = _music_policy.snapshot()
	return is_instance_valid(_music) and _music.playing and state.is_playing and Text.equals_text(state.current_track_identity, recipe.resource_path)


func _music_finished() -> void:
	_record(_apply_music(_music_policy.handle_track_finished()))


func _advance_music(delta: float) -> Dictionary:
	if not is_finite(delta) or delta <= 0.0 or not _music_policy.snapshot().is_playing:
		return _ok()
	_music_accumulator += delta
	while _music_accumulator >= SOUND_UPDATE_SECONDS and _music_policy.snapshot().is_playing:
		_music_accumulator -= SOUND_UPDATE_SECONDS
		var result: Dictionary = _apply_music(_music_policy.advance_fade_step())
		if not result.ok:
			return result
	return _ok()


func _apply_music(result: Dictionary) -> Dictionary:
	if not result.ok:
		return result
	for action: Dictionary in result.value:
		match action.kind:
			MusicPolicy.ActionKind.SET_VOLUME:
				_set_music_volume(action.volume)
			MusicPolicy.ActionKind.STOP:
				_music.stop()
				_music.stream = null
			MusicPolicy.ActionKind.PLAY:
				var recipe: StreamRecipe
				if Text.equals_text(action.track_identity, Catalog.tutorial_music().resource_path):
					recipe = tutorial_music_recipe
				elif Text.equals_text(action.track_identity, Catalog.frontend_music().resource_path):
					recipe = frontend_music_recipe
				else:
					return _failure("The Level 100 adapter received an unowned music identity.")
				var loaded: Dictionary = recipe.load_stream()
				if not loaded.ok:
					return loaded
				_music.stream_recipe = recipe
				_music.stream = loaded.value
				_music.play()
				_observer.call(_music)
	return _ok()


func bind_aquila(actor_id: int, actors: Array) -> Dictionary:
	if not _initialized or not Catalog.is_int32(actor_id):
		return _failure("Aquila binding requires a configured runtime and a Core Int32 identity.")
	if _aquila_actor_id == actor_id and is_instance_valid(_aquila):
		return update_aquila_pose(actors)
	stop_aquila_flight_loop()
	_stop_warning_loop()
	_warning_state = 0
	_release_aquila_binding()
	_aquila_actor_id = actor_id
	_aquila = Node3D.new()
	_aquila.name = "RetailAquilaAudioActor%d" % actor_id
	$Attachments/Aquila.add_child(_aquila)
	return update_aquila_pose(actors)


func update_aquila_pose(actors: Array) -> Dictionary:
	if _aquila_actor_id == null or not is_instance_valid(_aquila):
		return _failure("The Level 100 Aquila audio owner is not bound.")
	for value: Variant in actors:
		if value is not Dictionary or not Catalog.is_int32(value.get("actor_id")):
			return _failure("Actor facts require Int32 identities.", "ArgumentException")
		var actor: Dictionary = value
		if actor.get("actor_id") == _aquila_actor_id:
			if not _int_position(actor.get("position_mm")):
				return _failure("Actor position requires the Core Int32 millimeter facts.")
			_aquila.position = sim_world(actor.position_mm)
			return _ok()
	return _failure("Level 100 audio actor %d is absent from the native registry." % _aquila_actor_id, "InvalidDataException")


## One detached Core batch, preserving FirstFlightGame's audio ordering. Actor
## entries are {actor_id,position_mm:{x,y,z}}; destruction positions are the
## distinct Level100Vector3 retail axes, converted only at their consumer.
func consume_frame(facts: Dictionary, interleave: Callable = Callable()) -> Dictionary:
	# Validate the host representation only; represented value admission stays
	# at each ordered consumer so earlier effects survive a later rejection.
	for name: String in ["actors", "messages", "flight_events", "weapon_events", "destruction_events"]:
		if facts.get(name) is not Array:
			return _failure("Audio frame requires ordered Array facts: " + name, "ArgumentException")
	for name: String in ["warning_state", "simulation_tick", "mission_tick"]:
		if not Catalog.is_int32(facts.get(name)):
			return _failure("Audio frame requires Int32 facts: " + name, "ArgumentException")
	for name: String in ["thruster_fraction", "gameplay_mix"]:
		if typeof(facts.get(name)) not in [TYPE_INT, TYPE_FLOAT]:
			return _failure("Audio frame requires binary32 facts: " + name, "ArgumentException")
	if typeof(facts.get("gameplay_paused")) != TYPE_BOOL:
		return _failure("Audio frame requires a Boolean pause fact.", "ArgumentException")
	var result: Dictionary = update_aquila_pose(facts.actors)
	if not result.ok:
		return result
	result = set_aquila_warning_state(facts.warning_state)
	if not result.ok:
		return result
	result = _interleave(interleave, 0) # Host HUD events, before audio queue admission.
	if not result.ok:
		return result
	for value: Variant in facts.messages:
		if value is not Dictionary or not Catalog.is_int32(value.get("speaker_id")) or not Catalog.is_int32(value.get("message_id")):
			return _failure("Message facts require Core Int32 identities.", "ArgumentException")
		var message: Dictionary = value
		result = queue_character_message(message.speaker_id, message.message_id)
		if not result.ok:
			return result
	result = consume_aquila_flight_events(facts.flight_events, facts.simulation_tick, facts.mission_tick)
	if not result.ok:
		return result
	result = consume_weapon_fire_events(facts.weapon_events)
	if not result.ok:
		return result
	result = _interleave(interleave, 1) # World weapon visuals retain their old slot.
	if not result.ok:
		return result
	result = set_aquila_flight_pitch(facts.thruster_fraction)
	if not result.ok:
		return result
	result = _interleave(interleave, 2) # World destruction precedes its audio cues.
	if not result.ok:
		return result
	result = consume_destruction_events(facts.destruction_events)
	if not result.ok:
		return result
	result = set_gameplay_mix(facts.gameplay_mix)
	if not result.ok:
		return result
	return set_gameplay_paused(facts.gameplay_paused)


## Temporary C# world/HUD ownership makes these three fixed batch boundaries
## necessary. No callbacks occur per actor or event, and a failed host phase
## aborts before later audio mutations, preserving the previous host order.
static func _interleave(callback: Callable, phase: int) -> Dictionary:
	if not callback.is_valid():
		return _ok()
	var result: Variant = callback.call(phase)
	if result is Dictionary and typeof(result.get("ok")) == TYPE_BOOL:
		return result
	return _failure("Audio host phase did not return an explicit result.")


func consume_aquila_flight_events(events: Array, simulation_tick: int, mission_tick: int) -> Dictionary:
	if not Catalog.is_int32(simulation_tick) or not Catalog.is_int32(mission_tick):
		return _failure("Mission clocks require signed Int32 facts.", "ArgumentException")
	if mission_tick < 0 or mission_tick > simulation_tick:
		return _failure("missionTick is outside the current simulation clock.", "ArgumentOutOfRangeException")
	var start: int = simulation_tick - mission_tick
	if start < -2147483648 or start > 2147483647:
		return _failure("Mission start tick overflows Int32.", "OverflowException")
	if _mission_start_tick != start:
		_mission_start_tick = start
		_last_hostile_contact = start
	for value: Variant in events:
		if value is not Dictionary or not Catalog.is_int32(value.get("kind")) or not Catalog.is_int32(value.get("tick")) or not Catalog.is_int32(value.get("mode")):
			return _failure("Flight events require Core kind, tick and mode integers.", "ArgumentException")
		var event: Dictionary = value
		var result: Dictionary = _ok()
		match event.kind:
			2: result = play_aquila_transition(0)
			4: result = play_aquila_transition(2)
			8:
				if event.mode == 1:
					result = play_aquila_transition(1)
				elif event.mode == 0:
					_fade_out_flight()
			2048: result = play_on_aquila(Catalog.EffectCue.AQUILA_HYDRAULICS)
			4096: result = play_on_aquila(Catalog.EffectCue.AQUILA_STRAFE)
			64:
				result = Catalog.observe_hostile_environment_contact(event.tick, _last_hostile_contact)
				if result.ok:
					_last_hostile_contact = result.previous_contact_tick
					if result.value:
						result = play_terminal_cue(Catalog.TerminalCue.HOSTILE_ENVIRONMENT)
		if not result.ok:
			return result
	return _ok()


func consume_weapon_fire_events(events: Array) -> Dictionary:
	for value: Variant in events:
		if value is not Dictionary or not Catalog.is_int32(value.get("weapon")):
			return _failure("Weapon events require Core weapon integers.", "ArgumentException")
		var event: Dictionary = value
		var cue: int
		match event.weapon:
			1: cue = Catalog.EffectCue.PULSE_CANNON_FIRE
			2, 3: cue = Catalog.EffectCue.VULCAN_CANNON_FIRE
			_: return _failure("Core released an unknown Level 100 player weapon.", "InvalidDataException")
		# One report per release, irrespective of volley RoundCount.
		var result: Dictionary = play_on_aquila(cue)
		if not result.ok:
			return result
	return _ok()


func consume_destruction_events(events: Array) -> Dictionary:
	for value: Variant in events:
		if value is not Dictionary or not Catalog.is_int32(value.get("effect_kind")) or not _int_position(value.get("position")):
			return _failure("Destruction events require Core effect and Int32 position facts.", "ArgumentException")
		var event: Dictionary = value
		var cue: int
		match event.effect_kind:
			0, 5: continue # Mech Bullet Hit/Vulcan has no released sample.
			1: cue = Catalog.EffectCue.PULSE_IMPACT
			2: cue = Catalog.EffectCue.TARGET_OR_TRAINER_DESTROYED
			3: cue = Catalog.EffectCue.FACILITY_DESTROYED
			4: cue = Catalog.EffectCue.DRONE_DESTROYED
			_: return _failure("Core exposed unknown Level 100 destruction effect.", "InvalidDataException")
		var spec: Dictionary = Catalog.get_effect(cue)
		var result: Dictionary = _play_spatial("Retail" + EFFECT_NAMES[cue], spec.value, retail_world(event.position), $WorldSamples)
		if not result.ok:
			return result
	return _ok()


func play_aquila_transition(cue: int) -> Dictionary:
	if not is_instance_valid(_aquila):
		return _failure("The Level 100 Aquila audio owner is not bound.")
	match cue:
		0:
			var result: Dictionary = _play_spatial("RetailAquilaTakeoff", Catalog.get_aquila_transition(cue).value, Vector3.ZERO, _aquila)
			return _fade_in_flight() if result.ok else result
		1: return _fade_in_flight()
		2:
			_fade_out_flight()
			return _play_spatial("RetailAquilaLanding", Catalog.get_aquila_transition(cue).value, Vector3.ZERO, _aquila)
	return _failure("Unknown Aquila transition cue.", "ArgumentOutOfRangeException")


func play_on_aquila(cue: int) -> Dictionary:
	if cue not in [0, 1, 2, 3, 4, 5, 6, 7]:
		return _failure("This Level 100 event is not owned by the Aquila.", "ArgumentOutOfRangeException")
	if not is_instance_valid(_aquila):
		return _failure("The Level 100 Aquila audio owner is not bound.")
	return _play_spatial("Retail" + EFFECT_NAMES[cue], Catalog.get_effect(cue).value, Vector3.ZERO, _aquila)


func set_aquila_flight_pitch(value: float) -> Dictionary:
	var admitted: Dictionary = Catalog.bounded_option(value, "thrusterFraction", "Audio")
	if not admitted.ok:
		return admitted
	if _loop_playing("flight"):
		_live_loops.flight.pitch_scale = Catalog.retail_pc_pitch_multiplier(_f32(1.0 + _f32(admitted.value * 0.25))).value
	return _ok()


func set_aquila_warning_state(state: int) -> Dictionary:
	if _warning_state == state and _loop_playing("warning"):
		return _ok()
	_warning_state = state
	if state == 0:
		if _loop_playing("warning"):
			_fades.warning.target = 0.0
			_fades.warning.step = -F32.read_word(Catalog.RETAIL_FLIGHT_LOOP_FADE_STEP_WORD)
		return _ok()
	# A returning identical condition does not reverse its active recovery tail.
	if _loop_playing("warning") and _warning_loop_state == state:
		return _ok()
	_stop_warning_loop()
	if not is_instance_valid(_aquila):
		return _failure("The Level 100 Aquila audio owner is not bound.")
	var spec: Dictionary = Catalog.get_aquila_warning(state)
	if not spec.ok:
		return spec
	var result: Dictionary = _set_loop("warning", _aquila,
		"RetailAquilaEnergyLowLoop" if state == 1 else "RetailAquilaHullCriticalLoop", spec.value, true)
	if not result.ok:
		return result
	_fades.warning = {"sub": 1.0, "target": 1.0, "step": 0.0, "accumulator": 0.0}
	_warning_loop_state = state
	return _ok()


func play_repair_charging(owner_node: Node3D) -> Dictionary:
	return _play_spatial("RetailRepairPadCharging", Catalog.get_effect(Catalog.EffectCue.REPAIR_CHARGING).value, Vector3.ZERO, owner_node)


func play_repair_full(owner_node: Node3D) -> Dictionary:
	return _play_spatial("RetailRepairPadFull", Catalog.get_effect(Catalog.EffectCue.REPAIR_FULL).value, Vector3.ZERO, owner_node)


func set_repair_pad_idle(owner_node: Node3D, active: bool) -> Dictionary:
	return _set_loop("repair", owner_node, "RetailRepairPadIdleLoop", Catalog.get_actor_loop(2).value, active)


func set_trainer_flying(owner_node: Node3D, active: bool) -> Dictionary:
	return _set_loop("trainer", owner_node, "RetailAirTrainerFlybyLoop", Catalog.get_actor_loop(0).value, active)


func set_transport_flying(owner_node: Node3D, active: bool) -> Dictionary:
	return _set_loop("transport", owner_node, "RetailTransportFlybyLoop", Catalog.get_actor_loop(1).value, active)


func play_terminal_cue(cue: int) -> Dictionary:
	var spec: Dictionary = Catalog.get_terminal(cue)
	var names: Array[String] = ["AmmunitionDepleted", "ArmourLow", "EnergyLow", "HostileEnvironment", "IncomingMissile",
		"IncomingWarhead", "MicroMissilesSelected", "PulseCannonSelected", "VulcanCannonSelected", "WeaponOverheating"]
	return _play_2d("RetailTerminal" + names[cue], spec.value, true) if spec.ok else spec


func play_frontend_cue(cue: Variant) -> Dictionary:
	var units: Dictionary = Text.units(cue)
	if not units.ok or Text.is_null_or_white_space(units.value):
		return _failure("Frontend cue requires nonempty text.", "ArgumentException")
	var spec: Dictionary = Catalog.get_frontend(cue)
	return _play_2d("RetailFrontend" + Text.native_string(cue).value, spec.value, false) if spec.ok else spec


func queue_character_message(speaker_id: int, message_id: int) -> Dictionary:
	if not _initialized:
		return _failure("Audio is not configured for runtime.")
	var result: Dictionary = _queue.enqueue(speaker_id, message_id)
	if result.ok and not _voice.playing and _handoff <= 0.0 and _voice_lead <= 0.0:
		_voice_lead = CHARACTER_VOICE_LEAD_SECONDS
	return result


func stop_character_messages() -> Dictionary:
	_queue.clear()
	_active_speaker = null
	_active_message = null
	_active_length = 0.0
	_voice_lead = 0.0
	_handoff = 0.0
	if is_instance_valid(_voice):
		_voice.stop()
		_voice.stream = null
	return _ok()


func set_master_sound_option(value: float) -> Dictionary:
	var admitted: Dictionary = Catalog.to_retail_sound_master_volume(value)
	if not admitted.ok:
		return admitted
	_sound_master = admitted.value
	_apply_mix()
	return _ok()


func set_music_option(value: float) -> Dictionary:
	return _music_policy.set_configured_volume(value)


func set_gameplay_mix(value: float) -> Dictionary:
	var admitted: Dictionary = Catalog.bounded_option(value, "linearMix", "Audio mix")
	if not admitted.ok:
		return admitted
	_gameplay_mix = admitted.value
	_apply_mix()
	return _ok()


func set_gameplay_paused(value: bool) -> Dictionary:
	if _paused == value:
		return _ok()
	_paused = value
	if is_instance_valid(_voice):
		_voice.stream_paused = value and _voice.playing
	for list: Array in [_terminal_shots, _frontend_shots, _gameplay_shots]:
		for player: Node in list:
			if is_instance_valid(player):
				player.stream_paused = value
	for key: String in _live_loops:
		if _loop_playing(key):
			_live_loops[key].stream_paused = value
	# Existing frontend cues pause; new pause-menu cues remain live. Music does
	# not belong to CSoundManager's sample pause domain.
	return _ok()


func stop_gameplay_samples() -> Dictionary:
	stop_character_messages()
	_stop_shots(_terminal_shots)
	_terminal_volumes.clear()
	_stop_shots(_gameplay_shots)
	_spatial_volumes.clear()
	stop_aquila_flight_loop()
	_stop_warning_loop()
	for key: String in ["trainer", "transport", "repair"]:
		_stop_loop(key)
	_mission_start_tick = null
	_last_hostile_contact = 0
	_warning_state = 0
	_gameplay_mix = 1.0
	_paused = false
	return _ok()


func stop_all_samples() -> Dictionary:
	stop_gameplay_samples()
	_stop_shots(_frontend_shots)
	_frontend_volumes.clear()
	return _ok()


func stop_level100_audio() -> Dictionary:
	stop_all_samples()
	var result: Dictionary = stop_music()
	_release_aquila_binding()
	return result


func stop_for_level_exit(play_frontend_select: bool) -> Dictionary:
	var result: Dictionary = stop_level100_audio()
	return play_frontend_cue("Select") if result.ok and play_frontend_select else result


func _exit_tree() -> void:
	_exiting = true
	if _initialized and not Engine.is_editor_hint():
		stop_level100_audio()


func _play_2d(player_name: String, spec: Dictionary, gameplay: bool) -> Dictionary:
	if not _initialized:
		return _failure("Audio is not configured for runtime.")
	var recipe: StreamRecipe = _recipe(spec.resource_path, false, StreamRecipe.Codec.PCM_WAV)
	var loaded: Dictionary = recipe.load_stream()
	if not loaded.ok:
		return loaded
	var player: Player2D = ONE_SHOT.instantiate()
	player.name = player_name
	player.stream_recipe = recipe
	player.stream = loaded.value
	player.volume_db = _mixed_db(spec.linear_volume, gameplay, 100 if gameplay else 127)
	player.pitch_scale = _pitch_for(spec)
	player.finished.connect(_release_2d.bind(player, gameplay))
	if gameplay:
		_terminal_shots.append(player)
		_terminal_volumes[player] = spec.linear_volume
		$TerminalSamples.add_child(player)
	else:
		_frontend_shots.append(player)
		_frontend_volumes[player] = spec.linear_volume
		$FrontendSamples.add_child(player)
	player.play()
	_observer.call(player)
	if gameplay:
		player.stream_paused = _paused
	return _ok()


func _play_spatial(player_name: String, spec: Dictionary, position_value: Vector3, parent_node: Node3D) -> Dictionary:
	if not _initialized or parent_node == null:
		return _failure("Spatial audio requires a configured scene and explicit owner.")
	if spec.looping:
		return _failure("Looping cue '%s' requires a specific owner." % player_name)
	var recipe: StreamRecipe = _recipe(spec.resource_path, false, StreamRecipe.Codec.PCM_WAV)
	var loaded: Dictionary = recipe.load_stream()
	if not loaded.ok:
		return loaded
	var player: Player3D = SPATIAL.instantiate()
	player.name = player_name
	player.stream_recipe = recipe
	player.stream = loaded.value
	player.position = position_value
	player.pitch_scale = _pitch_for(spec) # Even a far-start refusal consumes this draw.
	parent_node.add_child(player)
	var distance: float = _distance(player)
	if Catalog.retail_refuses_non_looping_start(distance).value:
		player.queue_free()
		return _ok()
	player.volume_db = _spatial_db(spec.linear_volume, distance)
	player.finished.connect(_release_spatial.bind(player))
	_gameplay_shots.append(player)
	_spatial_volumes[player] = spec.linear_volume
	player.play()
	_observer.call(player)
	player.stream_paused = _paused
	return _ok()


func _set_loop(key: String, owner_node: Node3D, player_name: String, spec: Dictionary,
		active: bool, initial_sub: float = 1.0) -> Dictionary:
	if owner_node == null:
		return _failure("Loop owner must not be null.", "ArgumentNullException")
	if not active:
		_stop_loop(key)
		return _ok()
	if _loop_playing(key) and _live_loops[key].get_parent() == owner_node:
		return _ok()
	_stop_loop(key)
	if not _initialized or not spec.looping:
		return _failure("A configured looping cue is required for actor state.")
	var recipe: StreamRecipe = _recipe(spec.resource_path, true, StreamRecipe.Codec.PCM_WAV)
	var loaded: Dictionary = recipe.load_stream()
	if not loaded.ok:
		return loaded
	var player: Player3D = _loop_players[key]
	# Authored role names stay stable when a stopped player returns home.
	player.set_meta("current_retail_cue", player_name)
	player.stream_recipe = recipe
	player.stream = loaded.value
	player.pitch_scale = _pitch_for(spec)
	_spatial_volumes[player] = spec.linear_volume
	if player.get_parent() != owner_node:
		player.reparent(owner_node, false)
	player.position = Vector3.ZERO
	_live_loops[key] = player
	player.volume_db = _spatial_db(spec.linear_volume, _distance(player), initial_sub)
	player.play()
	_observer.call(player)
	player.stream_paused = _paused
	return _ok()


func _fade_in_flight() -> Dictionary:
	var continuing: bool = _loop_playing("flight") and _live_loops.flight.get_parent() == _aquila
	var spec: Dictionary = Catalog.get_aquila_transition(1).value
	var result: Dictionary = _set_loop("flight", _aquila, "RetailAquilaInFlightLoop", spec, true, 0.0)
	if not result.ok:
		return result
	if not continuing:
		_fades.flight.sub = 0.0
		_fades.flight.accumulator = 0.0
	_fades.flight.target = 1.0
	_fades.flight.step = F32.read_word(Catalog.RETAIL_FLIGHT_LOOP_FADE_STEP_WORD)
	_apply_loop_volume("flight", spec.linear_volume)
	return _ok()


func _fade_out_flight() -> void:
	if _loop_playing("flight"):
		_fades.flight.target = 0.0
		_fades.flight.step = -F32.read_word(Catalog.RETAIL_FLIGHT_LOOP_FADE_STEP_WORD)


func _advance_fade(key: String, delta: float) -> Dictionary:
	var fade: Dictionary = _fades[key]
	if not is_finite(delta) or delta <= 0.0 or not _loop_playing(key) or fade.step == 0.0:
		return _ok()
	fade.accumulator += delta
	while fade.accumulator >= SOUND_UPDATE_SECONDS and fade.step != 0.0:
		fade.accumulator -= SOUND_UPDATE_SECONDS
		var result: Dictionary = Catalog.advance_retail_flight_loop_sub_volume(fade.sub, fade.target, fade.step)
		if not result.ok:
			return result
		fade.sub = result.value
		if result.crossed_target:
			fade.step = 0.0
			fade.accumulator = 0.0
			if fade.target == 0.0:
				if key == "flight":
					stop_aquila_flight_loop()
				else:
					_stop_warning_loop()
				return _ok()
	if _live_loops.has(key) and _spatial_volumes.has(_live_loops[key]):
		_apply_loop_volume(key, _spatial_volumes[_live_loops[key]])
	return _ok()


func stop_aquila_flight_loop() -> Dictionary:
	_stop_loop("flight")
	_fades.flight = {"sub": 0.0, "target": 0.0, "step": 0.0, "accumulator": 0.0}
	return _ok()


func _stop_warning_loop() -> void:
	_stop_loop("warning")
	_fades.warning = {"sub": 0.0, "target": 0.0, "step": 0.0, "accumulator": 0.0}
	_warning_loop_state = 0


func _stop_loop(key: String) -> void:
	if not _live_loops.has(key):
		return
	var player: Player3D = _live_loops[key]
	_spatial_volumes.erase(player)
	if is_instance_valid(player):
		player.stop()
		player.stream = null
		if not _exiting and player.get_parent() != _loop_homes[key] and is_instance_valid(_loop_homes[key]):
			player.reparent(_loop_homes[key], false)
	_live_loops.erase(key)


func _loop_playing(key: String) -> bool:
	return _live_loops.has(key) and is_instance_valid(_live_loops[key]) and _live_loops[key].playing


func _apply_loop_volume(key: String, base_volume: float) -> void:
	if _live_loops.has(key):
		var player: Player3D = _live_loops[key]
		if is_instance_valid(player) and player.is_inside_tree():
			player.volume_db = _spatial_db(base_volume, _distance(player), _fades[key].sub)


func _begin_handoff() -> void:
	_active_message = null
	_active_speaker = null
	_active_length = 0.0
	_voice.stream = null
	if _queue.count() > 0:
		_handoff = CHARACTER_HANDOFF_SECONDS


func _start_next_message() -> Dictionary:
	_voice_lead = 0.0
	var queued: Dictionary = _queue.try_dequeue()
	if not queued.found:
		_active_speaker = null
		_active_message = null
		_active_length = 0.0
		_voice.stream = null
		return _ok()
	var message: Dictionary = queued.value.audio
	var path: Dictionary = Text.native_string(message.resource_path)
	if not path.ok:
		return path
	var recipe: StreamRecipe = _recipe(path.value, false, StreamRecipe.Codec.OGG)
	var loaded: Dictionary = recipe.load_stream()
	if not loaded.ok:
		return loaded
	_active_speaker = queued.value.speaker_id
	_active_message = message.message_id
	_active_length = loaded.value.get_length()
	_voice.stream_recipe = recipe
	_voice.stream = loaded.value
	_voice.volume_db = _mixed_db(F32.read_word(Catalog.RETAIL_RADIO_MESSAGE_VOLUME_WORD), true, 100)
	_voice.play()
	_observer.call(_voice)
	_voice.stream_paused = _paused
	return _ok()


func _remember_recipe(recipe: StreamRecipe) -> void:
	if recipe != null:
		_recipes["%d:%d:%s" % [recipe.codec, int(recipe.looping), recipe.source_path]] = recipe


func _validate_authored_recipes() -> Dictionary:
	var expected: Array = [
		[frontend_music_recipe, Catalog.frontend_music().resource_path, StreamRecipe.Codec.OGG, false],
		[tutorial_music_recipe, Catalog.tutorial_music().resource_path, StreamRecipe.Codec.OGG, false],
		[hull_warning_recipe, Catalog.get_aquila_warning(2).value.resource_path, StreamRecipe.Codec.PCM_WAV, true]]
	for key: String in LOOP_PATHS:
		var spec: Dictionary
		match key:
			"flight": spec = Catalog.get_aquila_transition(1).value
			"warning": spec = Catalog.get_aquila_warning(1).value
			"trainer": spec = Catalog.get_actor_loop(0).value
			"transport": spec = Catalog.get_actor_loop(1).value
			_: spec = Catalog.get_actor_loop(2).value
		expected.append([_loop_players[key].stream_recipe, spec.resource_path, StreamRecipe.Codec.PCM_WAV, true])
	for row: Array in expected:
		var recipe: StreamRecipe = row[0]
		if recipe == null or recipe.source_path != row[1] or recipe.codec != row[2] or recipe.looping != row[3]:
			return _failure("Authored audio recipes must preserve the admitted production identities.")
	return _ok()


func _recipe(path: String, looping: bool, codec: int) -> StreamRecipe:
	var key: String = "%d:%d:%s" % [codec, int(looping), path]
	if not _recipes.has(key):
		var recipe := StreamRecipe.new()
		recipe.source_path = path
		recipe.codec = codec
		recipe.looping = looping
		_recipes[key] = recipe
	return _recipes[key]


func _apply_mix() -> void:
	if is_instance_valid(_voice):
		_voice.volume_db = _mixed_db(F32.read_word(Catalog.RETAIL_RADIO_MESSAGE_VOLUME_WORD), true, 100)
	_update_spatial_attenuation()
	for player: Player2D in _terminal_volumes:
		if is_instance_valid(player):
			player.volume_db = _mixed_db(_terminal_volumes[player], true, 100)
	for player: Player2D in _frontend_volumes:
		if is_instance_valid(player):
			player.volume_db = _mixed_db(_frontend_volumes[player], false, 127)


func _update_spatial_attenuation() -> void:
	for player: Player3D in _spatial_volumes:
		if is_instance_valid(player) and player.is_inside_tree():
			var sub: float = 1.0
			if _live_loops.get("flight") == player:
				sub = _fades.flight.sub
			elif _live_loops.get("warning") == player:
				sub = _fades.warning.sub
			player.volume_db = _spatial_db(_spatial_volumes[player], _distance(player), sub)


func _mixed_db(base: float, gameplay: bool, source: int) -> float:
	return Catalog.retail_volume_db(source, base, 1.0, _sound_master, _gameplay_mix if gameplay else 1.0).value


func _spatial_db(base: float, distance: float, sub: float = 1.0) -> float:
	return Catalog.retail_volume_db(Catalog.retail_source_volume_for_distance(distance).value, base, sub, _sound_master, _gameplay_mix).value


func _distance(emitter: Node3D) -> float:
	var camera: Camera3D = get_viewport().get_camera_3d() if get_viewport() != null else null
	return emitter.global_position.distance_to(camera.global_position if camera != null else Vector3.ZERO)


func _set_music_volume(volume: int) -> void:
	# Use the owned player's native float setter: Godot's float logarithm and
	# multiplication match Mathf.LinearToDb(float). GDScript linear_to_db/log
	# use double intermediates and differ at two of the 128 reachable gains.
	# This device boundary remains separate from retail's sample-volume law.
	if volume <= 0:
		_music.volume_db = -80.0
	else:
		_music.volume_linear = _f32(float(volume) / 127.0)


static func _pitch_for(spec: Dictionary) -> float:
	var desired: float = 1.0
	if spec.pitch_variance_percent != 0:
		desired = _f32(1.0 + _f32(float(randi() % int(spec.pitch_variance_percent)) / 100.0))
	return Catalog.retail_pc_pitch_multiplier(desired).value


func _release_spatial(player: Player3D) -> void:
	_gameplay_shots.erase(player)
	_spatial_volumes.erase(player)
	player.queue_free()


func _release_2d(player: Player2D, gameplay: bool) -> void:
	if gameplay:
		_terminal_shots.erase(player)
		_terminal_volumes.erase(player)
	else:
		_frontend_shots.erase(player)
		_frontend_volumes.erase(player)
	player.queue_free()


static func _stop_shots(players: Array) -> void:
	for player: Node in players:
		if is_instance_valid(player):
			player.stop()
			player.queue_free()
	players.clear()


func _release_aquila_binding() -> void:
	if not _exiting and is_instance_valid(_aquila):
		_aquila.queue_free()
	_aquila = null
	_aquila_actor_id = null


static func sim_world(position_mm: Dictionary) -> Vector3:
	var scale: float = F32.read_word(0x3a83126f)
	return Vector3(_f32(_f32(position_mm.x) * scale), _f32(_f32(position_mm.y) * scale),
		_f32(_f32(_i32(-int(position_mm.z))) * scale))


static func retail_world(position_mm: Dictionary) -> Vector3:
	var scale: float = F32.read_word(0x3a83126f)
	return Vector3(_f32(_f32(position_mm.x) * scale), _f32(_f32(_i32(-int(position_mm.z))) * scale),
		_f32(_f32(_i32(-int(position_mm.y))) * scale))


static func _i32(value: int) -> int:
	var word: int = value & 0xffffffff
	return word - 0x100000000 if word >= 0x80000000 else word


static func _int_position(value: Variant) -> bool:
	return value is Dictionary and Catalog.is_int32(value.get("x")) and Catalog.is_int32(value.get("y")) and Catalog.is_int32(value.get("z"))


func inspection_snapshot() -> Dictionary:
	return {"initialized": _initialized, "queued_messages": _queue.count(), "playback": character_message_playback(),
		"music": _music_policy.snapshot(), "music_accumulator": _music_accumulator, "voice_lead": _voice_lead, "handoff": _handoff,
		"sound_master": _sound_master, "gameplay_mix": _gameplay_mix, "paused": _paused,
		"warning_state": _warning_state, "warning_loop_state": _warning_loop_state, "fades": _fades.duplicate(true),
		"aquila_actor_id": _aquila_actor_id, "mission_start_tick": _mission_start_tick, "last_hostile_contact": _last_hostile_contact,
		"gameplay_shots": _gameplay_shots.size(), "terminal_shots": _terminal_shots.size(), "frontend_shots": _frontend_shots.size(),
		"live_loops": _live_loops.keys().duplicate()}


func _record(result: Dictionary) -> void:
	if not result.ok:
		error_message = result.error
		set_process(false)
		push_error(error_message)


static func _f32(value: float) -> float:
	return F32.store_float32(value)


static func _ok() -> Dictionary:
	return {"ok": true}


static func _failure(message: String, kind: String = "InvalidOperationException") -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}
