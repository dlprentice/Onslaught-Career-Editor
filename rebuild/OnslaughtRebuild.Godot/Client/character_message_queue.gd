# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## Ordered duplicate-preserving queue from Level100AudioCatalog.cs. Admission
## resolves the same 51-message catalog before mutating the queue; speaker IDs
## are represented Int32 values, without an invented known-speaker restriction.

const Catalog = preload("res://Client/audio_catalog.gd")
var _messages: Array[Dictionary] = []


func count() -> int:
	return _messages.size()


func enqueue(speaker_id: Variant, message_id: Variant) -> Dictionary:
	if not Catalog.is_int32(speaker_id):
		return {"ok": false, "error_type": "ArgumentException", "parameter": "speakerId",
			"error": "Speaker ID must be a signed Int32."}
	var message: Dictionary = Catalog.get_character_message(message_id)
	if not message.ok:
		return message
	_messages.append({"speaker_id": speaker_id, "audio": message.value.duplicate(true)})
	return {"ok": true}


func try_dequeue() -> Dictionary:
	if _messages.is_empty():
		# Queue<T>.TryDequeue assigns the default value-type record on failure.
		return {"ok": true, "found": false, "value": {"speaker_id": 0, "audio": {
			"message_id": 0, "symbol": null, "audio_stem": null, "resource_path": null}}}
	var message: Dictionary = _messages.pop_front()
	return {"ok": true, "found": true, "value": message.duplicate(true)}


func clear() -> Dictionary:
	_messages.clear()
	return {"ok": true}
