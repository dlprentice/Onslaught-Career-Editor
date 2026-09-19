# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Port of Client/RetailMusicPolicy.cs: deterministic state above one platform
## stream. Source Music.h:48-106 / Music.cpp:111-573 and existing measured PC
## differences retain Ogg, null-to-random assignment, and ToEven volume stores.
## No discovery, decoder clocks, device callbacks or audio nodes live here.

const Audio = preload("res://Client/audio_catalog.gd")
const F32 = preload("res://Core/retail_float24.gd")
const Text = preload("res://Core/canonical_json_string.gd")
const AUTHORED_DEFAULT_VOLUME_WORD: int = 0x3f666666 # 0.9f.
const FULL_VOLUME: int = 127
const FADE_STEP: int = 5
const PLAYLIST_EXTENSION: String = "ogg"
enum Selection { FRONTEND = 0, TUTORIAL = 2 }
enum PlayType { SINGLE, LINEAR, RANDOM, SELECTION }
enum ActionKind { SET_VOLUME, STOP, PLAY }

var _configured_volume: float
var _set_volume: int
var _current_volume: int = FULL_VOLUME
var _target_volume: int = FULL_VOLUME
var _is_playing: bool = false
var _play_type: int = PlayType.LINEAR
var _current_track_identity: Variant = null
var _queued_track_identity: Variant = null
var _selection: Variant = null
var _selection_track_identity: Variant = null


func _init() -> void:
	_configured_volume = F32.read_word(AUTHORED_DEFAULT_VOLUME_WORD)
	_set_volume = Audio.round_volume(_configured_volume)


func set_configured_volume(value: Variant) -> Dictionary:
	var admitted: Dictionary = Audio.bounded_option(value, "value", "Music")
	if not admitted.ok:
		return admitted
	_configured_volume = admitted.value
	_set_volume = Audio.round_volume(_configured_volume)
	return {"ok": true}


static func track_index(selection: Variant) -> Dictionary:
	if not Audio.is_int32(selection):
		return _argument("selection", "Selection must be a signed Int32.")
	match selection:
		Selection.FRONTEND:
			return {"ok": true, "value": 8}
		Selection.TUTORIAL:
			return {"ok": true, "value": 3}
	return {"ok": false, "error_type": "ArgumentOutOfRangeException", "parameter": "selection",
		"error": "Specified argument was out of the range of valid values."}


func play_selection(selection: Variant, track_identity: Variant, fade: Variant = false) -> Dictionary:
	if not Audio.is_int32(selection) or typeof(fade) != TYPE_BOOL:
		return _argument("selection/fade", "Selection must be Int32 and fade must be Boolean.")
	var text: Dictionary = Text.units(track_identity)
	if not text.ok:
		return _argument("trackIdentity", "Track identity requires nullable UTF-16 text.")
	var track: Variant = text.value
	if _is_playing and fade:
		if track != _current_track_identity:
			_queued_track_identity = track
			_target_volume = 0
		return _actions([])
	# C# accepts every represented enum value here; TrackIndex is the separate
	# admission point. Its nonnullable string annotation also does not forbid a
	# runtime null, so do not replace null with an invented path or refusal.
	_play_type = PlayType.SELECTION
	_selection = selection
	_selection_track_identity = track
	return _actions(_start_track(track))


func play_from_list(requested_track_identity: Variant, random_track_identity: Variant, fade: Variant = true) -> Dictionary:
	if typeof(fade) != TYPE_BOOL:
		return _argument("fade", "Fade must be Boolean.")
	var requested: Dictionary = Text.units(requested_track_identity)
	var random: Dictionary = Text.units(random_track_identity)
	if not requested.ok or not random.ok:
		return _argument("requestedTrackIdentity/randomTrackIdentity", "Track identities require nullable UTF-16 text.")
	if _is_playing and fade:
		if requested.value != _current_track_identity:
			_queued_track_identity = requested.value
			_target_volume = 0
		return _actions([])
	var track: Variant
	if requested.value == null:
		# Released assignment, not a comparison. Mutation intentionally precedes
		# the missing-random exception, including when a previous stream is live.
		_play_type = PlayType.RANDOM
		_selection = null
		_selection_track_identity = null
		if random.value == null:
			return {"ok": false, "error_type": "ArgumentNullException", "parameter": "randomTrackIdentity",
				"error": "Value cannot be null."}
		track = random.value
	else:
		track = requested.value
	return _actions(_start_track(track))


func advance_fade_step() -> Dictionary:
	if not _is_playing:
		return _actions([])
	if absi(_current_volume - _target_volume) < 10:
		_current_volume = _target_volume
	if _current_volume < _target_volume:
		_current_volume += FADE_STEP
	if _current_volume > _target_volume:
		_current_volume -= FADE_STEP
	var actions: Array[Dictionary] = [_action(ActionKind.SET_VOLUME, null, _current_volume)]
	if _current_volume == 0 and _queued_track_identity != null:
		var queued: Variant = _queued_track_identity
		_queued_track_identity = null
		actions.append_array(_start_track(queued))
		return _actions(actions)
	if _current_volume == _target_volume:
		_target_volume = _set_volume
	return _actions(actions)


func handle_track_finished() -> Dictionary:
	if not _is_playing or _play_type != PlayType.SELECTION or _selection == null or _selection_track_identity == null:
		return _actions([])
	return _actions(_start_track(_selection_track_identity))


func kill() -> Dictionary:
	var actions: Array[Dictionary] = []
	if _is_playing:
		actions.append(_action(ActionKind.STOP, null, 0))
	_is_playing = false
	_play_type = PlayType.LINEAR
	_current_track_identity = null
	_queued_track_identity = null
	_selection = null
	_selection_track_identity = null
	_current_volume = _set_volume
	_target_volume = _set_volume
	return _actions(actions)


func reset() -> Dictionary:
	var result: Dictionary = kill()
	_configured_volume = F32.read_word(AUTHORED_DEFAULT_VOLUME_WORD)
	_set_volume = Audio.round_volume(_configured_volume)
	_current_volume = FULL_VOLUME
	_target_volume = FULL_VOLUME
	return result


func snapshot() -> Dictionary:
	return {"configured_volume": _configured_volume, "set_volume": _set_volume,
		"current_volume": _current_volume, "target_volume": _target_volume, "is_playing": _is_playing,
		"play_type": _play_type, "current_track_identity": _copy_text(_current_track_identity),
		"queued_track_identity": _copy_text(_queued_track_identity), "selection": _selection,
		"selection_track_identity": _copy_text(_selection_track_identity)}


func _start_track(track_identity: Variant) -> Array[Dictionary]:
	var actions: Array[Dictionary] = []
	if _is_playing:
		actions.append(_action(ActionKind.STOP, null, 0))
	_current_volume = _set_volume
	_target_volume = _set_volume
	_current_track_identity = _copy_text(track_identity)
	_queued_track_identity = null
	_is_playing = true
	actions.append(_action(ActionKind.SET_VOLUME, null, _current_volume))
	actions.append(_action(ActionKind.PLAY, track_identity, 0))
	return actions


static func _action(kind: int, track: Variant, volume: int) -> Dictionary:
	return {"kind": kind, "track_identity": _copy_text(track), "volume": volume}


static func _copy_text(value: Variant) -> Variant:
	return null if value == null else value.duplicate()


static func _actions(value: Array) -> Dictionary:
	return {"ok": true, "value": value}


static func _argument(parameter: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException", "parameter": parameter, "error": message}
