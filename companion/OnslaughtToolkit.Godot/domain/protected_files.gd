# SPDX-License-Identifier: MIT
class_name CompanionSaveFiles
extends Node
## Runs the small in-process C# file adapter off the UI thread.
## GDScript owns save interpretation; the adapter owns protected OS file access.

var _adapter: RefCounted
var _thread: Thread

func _ready() -> void:
	if ClassDB.class_exists("CSharpScript"):
		var adapter_script: Script = load("res://io/ProtectedSaveFiles.cs")
		if adapter_script != null and adapter_script.can_instantiate():
			_adapter = adapter_script.new()

func is_available() -> bool:
	return _adapter != null

func open_career(path: String) -> Dictionary:
	if not is_available():
		return _unavailable()
	return await _run(Callable(_adapter, "OpenCareer").bind(path))

func publish_copy(input: String, identity: String, sha256: String, output: String, prepared: PackedByteArray) -> Dictionary:
	if not is_available():
		return _unavailable()
	# A private byte array crosses the language boundary; no serialized requests.
	return await _run(Callable(_adapter, "PublishCopy").bind(input, identity, sha256, output, prepared.duplicate()), output)

func _unavailable() -> Dictionary:
	return {"ok": false, "message": "Save access is unavailable. Open this project with Godot 4.8 dev6 .NET and build its C# project, or restore the complete exported application."}

func _run(operation: Callable, output: String = "") -> Dictionary:
	if _thread != null:
		return {"ok": false, "message": "A protected file operation is already running."}
	_thread = Thread.new()
	var error := _thread.start(operation)
	if error != OK:
		_thread = null
		return {"ok": false, "message": "The protected file operation could not be started."}
	# Do not pretend a timeout cancels an in-process filesystem transaction.
	# Keep the UI responsive and await its definitive result before allowing edits.
	while _thread.is_alive():
		await get_tree().process_frame
	var response: Variant = _thread.wait_to_finish()
	_thread = null
	if not response is Dictionary or not response.get("ok", null) is bool:
		return {"ok": false, "may_have_output": not output.is_empty(), "output": output,
			"message": "The protected operation did not return a valid result. If publication was requested, a copy may exist; inspect it before use."}
	return response as Dictionary

func _exit_tree() -> void:
	# A normal close cannot abandon a write and falsely announce cancellation.
	if _thread != null:
		_thread.wait_to_finish()
		_thread = null
