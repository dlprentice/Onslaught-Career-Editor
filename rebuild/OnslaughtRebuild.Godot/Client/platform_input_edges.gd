# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## PlatformInputEdgeState.cs sparse held/read-once/joy-byte owner. IDs are exact
## host Int32 values, not an invented DirectInput scan layout. Echo messages are
## ignored, preserving the existing adapter policy; retail key repeat and joy
## polling cadence remain unresolved. The host owns routing, pause/focus reset
## boundaries and frame advance. No native input, pointer, clock or Core owner.
## External-ID APIs return explicit {ok,value?} results; capture is detached.

var _held_keys: Dictionary = {}
var _consume_once_keys: Dictionary = {}
var _previous_joy_buttons: Dictionary = {}
var _current_joy_buttons: Dictionary = {}
var _frame_index: int = 0
var _reset_generation: int = 0


func get_frame_index() -> int:
	return _frame_index


func get_reset_generation() -> int:
	return _reset_generation


func observe_key(key_code: Variant, pressed: Variant, echo: Variant) -> Dictionary:
	if not _is_int32(key_code) or not pressed is bool or not echo is bool:
		return _argument("ObserveKey requires an Int32 ID and Boolean pressed/echo flags.")
	if echo:
		return {"ok": true}
	if pressed:
		# Every non-echo press is a discrete observation, even if already held.
		_consume_once_keys[key_code] = 1
		_held_keys[key_code] = 1
	else:
		# Release does not clear the previously latched one-shot press byte.
		_held_keys.erase(key_code)
	return {"ok": true}


func get_held_key(key_code: Variant) -> Dictionary:
	if not _is_int32(key_code):
		return _argument("Held-key ID must be an exact Int32.")
	return {"ok": true, "value": _held_keys.get(key_code, 0)}


func consume_key_once(key_code: Variant) -> Dictionary:
	if not _is_int32(key_code):
		return _argument("Consume-once key ID must be an exact Int32.")
	var value: int = _consume_once_keys.get(key_code, 0)
	_consume_once_keys.erase(key_code)
	return {"ok": true, "value": value}


func observe_joy_button(joypad: Variant, button: Variant, value: Variant) -> Dictionary:
	if not _is_int32(joypad) or not _is_int32(button) or typeof(value) != TYPE_INT or value < 0 or value > 255:
		return _argument("Joypad/button IDs require Int32 and the observed byte requires 0..255.")
	if value == 0:
		if _current_joy_buttons.has(joypad):
			_current_joy_buttons[joypad].erase(button)
			if _current_joy_buttons[joypad].is_empty():
				_current_joy_buttons.erase(joypad)
	else:
		if not _current_joy_buttons.has(joypad):
			_current_joy_buttons[joypad] = {}
		_current_joy_buttons[joypad][button] = value
	return {"ok": true}


func get_previous_joy_button(joypad: Variant, button: Variant) -> Dictionary:
	if not _is_int32(joypad) or not _is_int32(button):
		return _argument("Previous joypad/button IDs require exact Int32 values.")
	return {"ok": true, "value": _joy_byte(_previous_joy_buttons, joypad, button)}


func get_current_joy_button(joypad: Variant, button: Variant) -> Dictionary:
	if not _is_int32(joypad) or not _is_int32(button):
		return _argument("Current joypad/button IDs require exact Int32 values.")
	return {"ok": true, "value": _joy_byte(_current_joy_buttons, joypad, button)}


func is_joy_button_rising(joypad: Variant, button: Variant) -> Dictionary:
	if not _is_int32(joypad) or not _is_int32(button):
		return _argument("Joypad/button IDs require exact Int32 values.")
	return {"ok": true, "value": _joy_byte(_previous_joy_buttons, joypad, button) == 0 and _joy_byte(_current_joy_buttons, joypad, button) != 0}


func is_joy_button_held(joypad: Variant, button: Variant) -> Dictionary:
	if not _is_int32(joypad) or not _is_int32(button):
		return _argument("Joypad/button IDs require exact Int32 values.")
	return {"ok": true, "value": _joy_byte(_current_joy_buttons, joypad, button) != 0}


func is_joy_button_falling(joypad: Variant, button: Variant) -> Dictionary:
	if not _is_int32(joypad) or not _is_int32(button):
		return _argument("Joypad/button IDs require exact Int32 values.")
	return {"ok": true, "value": _joy_byte(_previous_joy_buttons, joypad, button) != 0 and _joy_byte(_current_joy_buttons, joypad, button) == 0}


func advance_frame() -> void:
	_previous_joy_buttons = _current_joy_buttons.duplicate(true)
	# Both owners use unchecked signed Int64 wrap. Keys stay latched until an
	# explicit consume/reset; advancing a host frame does not clear key bytes.
	_frame_index += 1


func reset() -> void:
	_held_keys.clear()
	_consume_once_keys.clear()
	_previous_joy_buttons.clear()
	_current_joy_buttons.clear()
	_reset_generation += 1


func capture() -> Dictionary:
	return {"frame_index": _frame_index, "reset_generation": _reset_generation,
		"held_keys": _capture_keys(_held_keys), "consume_once_keys": _capture_keys(_consume_once_keys),
		"previous_joy_buttons": _capture_joy(_previous_joy_buttons), "current_joy_buttons": _capture_joy(_current_joy_buttons)}


static func _capture_keys(keys: Dictionary) -> Array[Dictionary]:
	var ids: Array = keys.keys()
	ids.sort()
	var result: Array[Dictionary] = []
	for id: int in ids:
		result.append({"key_code": id, "value": keys[id]})
	return result


static func _capture_joy(buttons: Dictionary) -> Array[Dictionary]:
	var pads: Array = buttons.keys()
	pads.sort()
	var result: Array[Dictionary] = []
	for joypad: int in pads:
		var ids: Array = buttons[joypad].keys()
		ids.sort()
		for button: int in ids:
			result.append({"joypad": joypad, "button": button, "value": buttons[joypad][button]})
	return result


static func _joy_byte(buttons: Dictionary, joypad: int, button: int) -> int:
	return buttons[joypad].get(button, 0) if buttons.has(joypad) else 0


static func _is_int32(value: Variant) -> bool:
	return typeof(value) == TYPE_INT and value >= -2147483648 and value <= 2147483647


static func _argument(reason: String) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException", "error": reason}
