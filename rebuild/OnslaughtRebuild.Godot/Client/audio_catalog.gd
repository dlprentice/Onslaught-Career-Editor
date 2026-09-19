# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Production recipes and arithmetic from Level100AudioCatalog.cs. Identities
## refer to the existing private materializer outputs; this module opens none.
## Every C# float operation stores binary32, including the ordered Fade product.
## DirectSound attenuation, spatial early-out and PC pitch ceiling remain
## explicit laws; they do not claim Godot device-volume or audible parity.

const F32 = preload("res://Core/retail_float24.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const HudCatalog = preload("res://Client/hud_catalog.gd")
const RETAIL_HOSTILE_ENVIRONMENT_QUIET_TICKS: int = 100 # 5 * released 20 Hz.
const RETAIL_RADIO_MESSAGE_VOLUME_WORD: int = 0x3ed70a3d # 0.42f, PC branch.
const RETAIL_HUD_MESSAGE_VOLUME_WORD: int = 0x3ee66666 # 0.45f.
const RETAIL_DEFAULT_EFFECT_VOLUME_WORD: int = 0x3f333333 # 0.70f.
const RETAIL_WEAPON_LAUNCH_VOLUME_WORD: int = 0x3f000000 # 0.50f.
const RETAIL_FAR_SOUND_UNITS: float = 50.0
const RETAIL_UNTRACKED_SOURCE_VOLUME: int = 127
const RETAIL_LISTENER_SOURCE_VOLUME: int = 100
const RETAIL_UNFADED_SUB_VOLUME: float = 1.0
const RETAIL_FLIGHT_LOOP_FADE_STEP_WORD: int = 0x3ca3d70a # 0.02f.

enum EffectCue { AQUILA_STRAFE, AQUILA_HYDRAULICS, AQUILA_INCOMING_MISSILE,
	AQUILA_TARGET_LOCKED, AQUILA_TARGET_ACQUIRED, PULSE_CANNON_FIRE, VULCAN_CANNON_FIRE,
	MICRO_MISSILE_FIRE, DRONE_VULCAN_FIRE, PULSE_IMPACT, MISSILE_IMPACT,
	TARGET_OR_TRAINER_DESTROYED, DRONE_DESTROYED, FACILITY_DESTROYED, AQUILA_DESTROYED,
	TRANSPORT_DESTROYED, COMPONENT_DEBRIS_DESTROYED, LARGE_DEBRIS_DESTROYED,
	HUGE_GROUND_DEBRIS_DESTROYED, REPAIR_CHARGING, REPAIR_FULL }
enum TerminalCue { AMMUNITION_DEPLETED, ARMOUR_LOW, ENERGY_LOW, HOSTILE_ENVIRONMENT,
	INCOMING_MISSILE, INCOMING_WARHEAD, MICRO_MISSILES_SELECTED, PULSE_CANNON_SELECTED,
	VULCAN_CANNON_SELECTED, WEAPON_OVERHEATING }
enum WarningState { NORMAL, ENERGY_LOW, HULL_CRITICAL }
enum TransitionCue { TAKEOFF, IN_FLIGHT, LANDING }
enum ActorLoopCue { AIR_TRAINER, TRANSPORT, REPAIR_PAD_IDLE }

# Rows: resource path, sounds.sfx record, SAMPLE-PATH identity, caller float
# word, record gain float word, pitch variance, looping. These are provenance
# identities, not substitutes for retail's DISPLAY-NAME lookup.
const FRONTEND: Dictionary = {
	"Back": ["res://Assets/Frontend/SoundEffects/back.wav", 43, "Front End\\N_FE_back", 0x3f333333, 0x3f051eb8, 0, false],
	"Move": ["res://Assets/Frontend/SoundEffects/move.wav", 44, "Front End\\N_FE_move", 0x3f333333, 0x3efae148, 0, false],
	"Select": ["res://Assets/Frontend/SoundEffects/select.wav", 45, "Front End\\N_FE_select", 0x3f333333, 0x3f051eb8, 0, false],
}
const EFFECTS: Array = [
	["res://Assets/Aquila/SoundEffects/strafe.wav", 21, "Battle Engine\\N_BE_dash", 0x3f4ccccd, 0x3f800000, 10, false],
	["res://Assets/Aquila/SoundEffects/hydraulics.wav", 32, "Battle Engine\\N_BE_hydraulics_02", 0x3ee66666, 0x3ecccccd, 0, false],
	["res://Assets/Aquila/SoundEffects/incoming-missile.wav", 33, "Battle Engine\\N_BE_incoming_missile", 0x3ee66666, 0x3f4ccccd, 5, false],
	["res://Assets/Aquila/SoundEffects/target-locked.wav", 30, "Battle Engine\\N_BE_homing_missile_lock", 0x3ee66666, 0x3f4ccccd, 0, false],
	["res://Assets/Aquila/SoundEffects/target-acquired.wav", 31, "Battle Engine\\N_BE_homing_missile_target", 0x3ee66666, 0x3f4ccccd, 0, false],
	# Weapon-launch evidence retained from the C# owner: pristine specimen
	# local-lab/safe-copy-bea-pristine/BEA.exe.original.backup, SHA-256
	# 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750;
	# body 0x005069f0 pushes 0.5f at 0x00506a6b and 0x00506a8a.
	["res://Assets/Level100/SoundEffects/pulse-cannon-fire.wav", 37, "Battle Engine\\N_BE_pulse_cannon_fire", 0x3f000000, 0x3f266666, 5, false],
	["res://Assets/Aquila/SoundEffects/vulcan-cannon-fire.wav", 42, "Battle Engine\\N_BE_vulcan_cannon_fire", 0x3f000000, 0x3f400000, 7, false],
	# Retain the established gaps: neither Micro Missile nor Drone Vulcan has a
	# current producer or a demonstrated route through that weapon-launch body.
	["res://Assets/Aquila/SoundEffects/micro-missile-fire.wav", 34, "Battle Engine\\N_BE_micro_missiles_fire", 0x3f333333, 0x3f4ccccd, 15, false],
	# Drone selection of Blaster 2 record 155 versus same-sample Blaster 1 record
	# 156 is unresolved; preserve the current 155 / volume 60 / variance 10 recipe.
	["res://Assets/Level100/SoundEffects/drone-vulcan-fire.wav", 155, "Weapons\\N_WP_blaster_02", 0x3f333333, 0x3f19999a, 10, false],
	["res://Assets/Level100/SoundEffects/explosion-small.wav", 108, "Impact\\N_I_explosion_small_debris", 0x3f333333, 0x3f333333, 20, false],
	["res://Assets/Level100/SoundEffects/target-tank-explosion-medium.wav", 104, "Impact\\N_I_explosion_medium", 0x3f333333, 0x3f333333, 30, false],
	["res://Assets/Level100/SoundEffects/target-tank-explosion-medium.wav", 104, "Impact\\N_I_explosion_medium", 0x3f333333, 0x3f333333, 30, false],
	["res://Assets/Level100/SoundEffects/explosion-small.wav", 108, "Impact\\N_I_explosion_small_debris", 0x3f333333, 0x3f333333, 20, false],
	["res://Assets/Level100/SoundEffects/facility-explosion-medium.wav", 105, "Impact\\N_I_explosion_medium_ricochet", 0x3f333333, 0x3f333333, 30, false],
	["res://Assets/Level100/SoundEffects/aquila-explosion-huge.wav", 109, "Impact\\N_I_explosion_vbig", 0x3f333333, 0x3f333333, 30, false],
	["res://Assets/Level100/SoundEffects/transport-explosion-large.wav", 96, "Impact\\N_I_explosion_big", 0x3f333333, 0x3f333333, 30, false],
	["res://Assets/Level100/SoundEffects/component-explosion.wav", 95, "Impact\\N_I_explosion2", 0x3f333333, 0x3f333333, 30, false],
	["res://Assets/Level100/SoundEffects/explosion-large-debris.wav", 97, "Impact\\N_I_explosion_big_debris", 0x3f333333, 0x3f333333, 30, false],
	["res://Assets/Level100/SoundEffects/explosion-huge-ground-debris.wav", 110, "Impact\\N_I_explosion_vbig_debris", 0x3f333333, 0x3f333333, 30, false],
	["res://Assets/Level100/SoundEffects/repair-charging.wav", 7, "Atmospheres\\N_A_health_pod_charging", 0x3f333333, 0x3f4ccccd, 0, false],
	["res://Assets/Level100/SoundEffects/repair-full.wav", 8, "Atmospheres\\N_A_health_pod_full", 0x3f333333, 0x3f4ccccd, 0, false],
]
const TERMINALS: Array = [
	["ammunition-depleted", 46, "HUD\\N_HUD_Ammunition_Depleted"], ["armour-low", 48, "HUD\\N_HUD_Armour_Low"],
	["energy-low", 53, "HUD\\N_HUD_Energy_Low"], ["hostile-environment", 57, "HUD\\N_HUD_Hostile_Environment"],
	["incoming-missile", 58, "HUD\\N_HUD_Incoming_Missile"], ["incoming-warhead", 59, "HUD\\N_HUD_Incoming_Warhead"],
	["micro-missiles-selected", 60, "HUD\\N_HUD_Micro_Missiles"], ["pulse-cannon-selected", 62, "HUD\\N_HUD_Pulse_Cannon"],
	["vulcan-cannon-selected", 72, "HUD\\N_HUD_Vulcan_Cannon"], ["weapon-overheating", 75, "HUD\\N_HUD_Weapon_Overheating"],
]
const TRANSITIONS: Array = [
	["res://Assets/Aquila/SoundEffects/engine-takeoff.wav", 26, "Battle Engine\\N_BE_engine_takeoff", 0x3ecccccd, 0x3f800000, 0, false],
	["res://Assets/Aquila/SoundEffects/engine-inflight.wav", 24, "Battle Engine\\N_BE_engine_inflight", 0x3f000000, 0x3f800000, 0, true],
	["res://Assets/Aquila/SoundEffects/engine-land.wav", 25, "Battle Engine\\N_BE_engine_land", 0x3ecccccd, 0x3f800000, 0, false],
]
const WARNINGS: Dictionary = {
	1: ["res://Assets/Aquila/SoundEffects/energy-low.wav", 23, "Battle Engine\\N_BE_energy_low", 0x3f333333, 0x3f800000, 0, true],
	2: ["res://Assets/Aquila/SoundEffects/energy-critical.wav", 22, "Battle Engine\\N_BE_energy_critical", 0x3f333333, 0x3f800000, 0, true],
}
const ACTOR_LOOPS: Array = [
	["res://Assets/Level100/SoundEffects/trainer-flyby.wav", 121, "Vehicles\\N_V_F_fighter_flyby", 0x3f333333, 0x3ee66666, 15, true],
	["res://Assets/Level100/SoundEffects/transport-flyby.wav", 129, "Vehicles\\N_V_bomber_flyby", 0x3f333333, 0x3ecccccd, 15, true],
	["res://Assets/Level100/SoundEffects/repair-idle.wav", 9, "Atmospheres\\N_A_health_pod_on", 0x3f333333, 0x3f000000, 0, true],
]


static func character_messages() -> Array[Dictionary]:
	return HudCatalog.character_message_specs()


static func get_character_message(message_id: Variant) -> Dictionary:
	if not is_int32(message_id):
		return _host_type("messageId", "a signed Int32")
	for row: Dictionary in character_messages():
		if row.message_id == message_id:
			return _ok(row)
	return _range("messageId", "The mission requested a character message outside the accepted Level 100 set.")


static func get_frontend(cue_name: Variant) -> Dictionary:
	var text: Dictionary = Text.units(cue_name)
	if not text.ok:
		return _host_type("cueName", "nullable UTF-16 text")
	for name: String in FRONTEND:
		if Text.equals_text(text.value, name):
			return _ok(_recipe(FRONTEND[name]))
	return _range("cueName")


static func get_effect(cue: Variant) -> Dictionary:
	return _array_recipe(EFFECTS, cue)


static func get_terminal(cue: Variant) -> Dictionary:
	if not is_int32(cue):
		return _host_type("cue", "a signed Int32")
	if cue < 0 or cue >= TERMINALS.size():
		return _range("cue")
	var row: Array = TERMINALS[cue]
	return _ok(_recipe(["res://Assets/Level100/SoundEffects/terminal-%s.wav" % row[0], row[1], row[2],
		RETAIL_HUD_MESSAGE_VOLUME_WORD, 0x3f800000, 0, false]))


static func get_aquila_transition(cue: Variant) -> Dictionary:
	return _array_recipe(TRANSITIONS, cue)


static func get_aquila_warning(state: Variant) -> Dictionary:
	if not is_int32(state):
		return _host_type("state", "a signed Int32")
	return _ok(_recipe(WARNINGS[state])) if WARNINGS.has(state) else _range("state")


static func get_actor_loop(cue: Variant) -> Dictionary:
	return _array_recipe(ACTOR_LOOPS, cue)


static func tutorial_music() -> Dictionary:
	return {"resource_path": "res://Assets/Level100/Music/tutorial-track-03.ogg", "retail_selection": "MUS_TUTORIAL",
		"retail_track_index": 3, "retail_source_name": "data/Music/BEA_04(Master).ogg"}


static func frontend_music() -> Dictionary:
	# Released normal (non-playable-demo) MUS_FRONTEND -> zero-based index 8 of
	# the alphabetic BEA_01..10 Ogg playlist; see existing C# catalog evidence.
	return {"resource_path": "res://Assets/Frontend/Music/frontend-track-08.ogg", "retail_selection": "MUS_FRONTEND",
		"retail_track_index": 8, "retail_source_name": "data/Music/BEA_09(Master).ogg"}


static func observe_hostile_environment_contact(current_tick: Variant, previous_contact_tick: Variant) -> Dictionary:
	if not is_int32(current_tick) or not is_int32(previous_contact_tick):
		return _host_type("currentTick/previousContactTick", "signed Int32 ticks")
	if current_tick < previous_contact_tick:
		var error: Dictionary = _range("currentTick", "Hostile-environment contacts must remain tick ordered.")
		error.previous_contact_tick = previous_contact_tick
		return error
	# The C# long subtraction must not wrap at the signed Int32 endpoints.
	return {"ok": true, "value": current_tick - previous_contact_tick > RETAIL_HOSTILE_ENVIRONMENT_QUIET_TICKS,
		"previous_contact_tick": current_tick}


static func to_retail_sound_master_volume(option_value: Variant) -> Dictionary:
	return bounded_option(option_value, "optionValue", "Audio")


static func to_retail_music_set_volume(option_value: Variant) -> Dictionary:
	var value: Dictionary = bounded_option(option_value, "optionValue", "Audio")
	return _ok(round_volume(value.value)) if value.ok else value


static func advance_retail_flight_loop_sub_volume(current: Variant, target: Variant, signed_step: Variant) -> Dictionary:
	for value: Variant in [current, target, signed_step]:
		if not _is_number(value):
			return _host_type("current/target/signedStep", "binary32 numbers")
	var now: float = _f32(current)
	var goal: float = _f32(target)
	var step: float = _f32(signed_step)
	if not is_finite(now) or not is_finite(goal) or now < 0.0 or now > 1.0 or goal < 0.0 or goal > 1.0 \
			or absf(step) != F32.read_word(RETAIL_FLIGHT_LOOP_FADE_STEP_WORD):
		return _range("current", "Flight-loop fades require bounded subvolumes and the exact signed retail step.")
	var next: float = _f32(now + step)
	var crossed: bool = next > goal if step > 0.0 else next < goal
	return {"ok": true, "value": goal if crossed else next, "crossed_target": crossed}


static func retail_source_volume_for_distance(distance_units: Variant) -> Dictionary:
	if not _is_number(distance_units):
		return _host_type("distanceUnits", "a binary32 number")
	var volume: float = _f32(RETAIL_FAR_SOUND_UNITS - _f32(distance_units))
	if volume > RETAIL_FAR_SOUND_UNITS:
		volume = RETAIL_FAR_SOUND_UNITS
	if volume < 0.0:
		volume = 0.0
	return _ok(_unchecked_float_int32(_f32(_f32(volume * 100.0) / RETAIL_FAR_SOUND_UNITS)))


static func retail_refuses_non_looping_start(distance_units: Variant) -> Dictionary:
	if not _is_number(distance_units):
		return _host_type("distanceUnits", "a binary32 number")
	return _ok(_f32(distance_units) >= RETAIL_FAR_SOUND_UNITS)


static func retail_fade_millibels(source_volume: Variant, event_volume: Variant, sub_volume: Variant,
		master_mix: Variant, type_master_mix: Variant) -> Dictionary:
	if not is_int32(source_volume):
		return _host_type("sourceVolume", "a signed Int32")
	for value: Variant in [event_volume, sub_volume, master_mix, type_master_mix]:
		if not _is_number(value):
			return _host_type("eventVolume/subVolume/masterMix/typeMasterMix", "binary32 numbers")
	# Source SoundManager.cpp:760-793 truncates after this left-associated
	# product, before integer scale/plateau/halving. Do not reorder multiplies.
	var product: float = _f32(source_volume)
	for value: Variant in [event_volume, sub_volume, master_mix, type_master_mix]:
		product = _f32(product * _f32(value))
	var volume: int = _i32(_unchecked_float_int32(product) * 200)
	if volume > 10000:
		volume = 10000
	@warning_ignore("integer_division")
	var half: int = _i32(volume - 10000) / 2
	return _ok(maxi(half, -10000))


static func retail_pc_shaped_millibels(millibels: Variant) -> Dictionary:
	if not is_int32(millibels):
		return _host_type("millibels", "a signed Int32")
	# pcsoundmanager.cpp:405-410 triples the slope below -4000 millibels.
	return _ok(_i32(millibels + ((millibels + 4000) * 2)) if millibels < -4000 else millibels)


static func retail_volume_db(source_volume: Variant, event_volume: Variant, sub_volume: Variant,
		master_mix: Variant, type_master_mix: Variant) -> Dictionary:
	var faded: Dictionary = retail_fade_millibels(source_volume, event_volume, sub_volume, master_mix, type_master_mix)
	if not faded.ok:
		return faded
	var shaped: Dictionary = retail_pc_shaped_millibels(faded.value)
	return _ok(_f32(_f32(shaped.value) / 100.0))


static func retail_pc_pitch_multiplier(desired_pitch_multiplier: Variant) -> Dictionary:
	if not _is_number(desired_pitch_multiplier):
		return _host_type("desiredPitchMultiplier", "a binary32 number")
	var value: float = _f32(desired_pitch_multiplier)
	return _ok(1.0 if value > 1.0 else value)


## Raw-word entry point preserves even a signaling-NaN payload when the original
## one-sided comparison passes it through. A native double carrier necessarily
## quiets signaling NaN during float promotion, so bit-level callers use this.
static func retail_pc_pitch_multiplier_word(word: Variant) -> Dictionary:
	if typeof(word) != TYPE_INT or word < 0 or word > 0xffffffff:
		return _host_type("word", "an unsigned binary32 word")
	return _ok(0x3f800000 if F32.read_word(word) > 1.0 else word)


## Shared option admission/rounding for music_policy; caller-owned parameter
## spelling is retained in failures. C# float argument conversion precedes checks.
static func bounded_option(value: Variant, parameter: String, category: String) -> Dictionary:
	if not _is_number(value):
		return _host_type(parameter, "a binary32 number")
	var stored: float = _f32(value)
	if not is_finite(stored) or stored < 0.0 or stored > 1.0:
		return _range(parameter, category + " option values must be finite and between zero and one.")
	return _ok(stored)


static func round_volume(value: float) -> int:
	# Call only after bounded_option admission: this checked C# cast has range
	# [0,127]. GDScript round() is ties-away, so spell MathF.Round(ToEven) here.
	var scaled: float = _f32(value * 127.0)
	var lower: float = floor(scaled)
	var remainder: float = scaled - lower
	return int(lower + 1.0) if remainder > 0.5 or (remainder == 0.5 and (int(lower) & 1) != 0) else int(lower)


static func is_int32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


static func _array_recipe(rows: Array, cue: Variant) -> Dictionary:
	if not is_int32(cue):
		return _host_type("cue", "a signed Int32")
	return _ok(_recipe(rows[cue])) if cue >= 0 and cue < rows.size() else _range("cue")


static func _recipe(row: Array) -> Dictionary:
	return {"resource_path": row[0], "retail_sound_record": row[1], "retail_effect_name": row[2],
		"linear_volume": _f32(F32.read_word(row[3]) * F32.read_word(row[4])),
		"pitch_variance_percent": row[5], "looping": row[6]}


static func _unchecked_float_int32(value: float) -> int:
	# Existing net8.0 Linux/x64 C# conversion: truncation, with INT_MIN for
	# nonfinite/out-of-range values. Differential vectors include those edges;
	# this is a migration contract, not an additional retail input claim.
	if not is_finite(value) or value < -2147483648.0 or value >= 2147483648.0:
		return -2147483648
	return int(value)


static func _i32(value: int) -> int:
	var word: int = value & 0xffffffff
	return word - 0x100000000 if word >= 0x80000000 else word


static func _is_number(value: Variant) -> bool:
	return typeof(value) in [TYPE_INT, TYPE_FLOAT]


static func _f32(value: float) -> float:
	return F32.store_float32(value)


static func _ok(value: Variant) -> Dictionary:
	return {"ok": true, "value": value}


static func _range(parameter: String, message: String = "Specified argument was out of the range of valid values.") -> Dictionary:
	return {"ok": false, "error_type": "ArgumentOutOfRangeException", "parameter": parameter, "error": message}


static func _host_type(parameter: String, wanted: String) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException", "parameter": parameter, "error": parameter + " requires " + wanted + "."}
