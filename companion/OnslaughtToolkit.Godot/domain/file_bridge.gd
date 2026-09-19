# SPDX-License-Identifier: MIT
class_name CompanionFileBridge
extends Node
## Explicit OS safety boundary. No save parsing or unchecked save writes here.
## Requests and save bytes travel over pipes, never shell commands or argv.

const REQUEST_TIMEOUT_MS := 15000
var _thread: Thread
var _pid := -1

func executable_path() -> String:
	if OS.has_environment("ONSLAUGHT_FILE_BRIDGE"):
		return OS.get_environment("ONSLAUGHT_FILE_BRIDGE")
	if OS.has_feature("editor"):
		var marker := "res://.godot/companion_bridge_path.txt"
		if FileAccess.file_exists(marker):
			return FileAccess.get_file_as_string(marker).strip_edges()
	var name := "OnslaughtToolkit.FileBridge.exe" if OS.get_name() == "Windows" else "OnslaughtToolkit.FileBridge"
	return OS.get_executable_path().get_base_dir().path_join("file-bridge").path_join(name)

func is_available() -> bool:
	return FileAccess.file_exists(executable_path())

func transact(request: Dictionary) -> Dictionary:
	if _thread != null:
		return {"ok": false, "message": "A protected file operation is already running."}
	if not is_available():
		return {"ok": false, "message": "The packaged file-safety helper is missing. Build the companion or restore its file-bridge folder. Save operations are unavailable."}
	var process := OS.execute_with_pipe(executable_path(), [], true)
	if process.is_empty():
		return {"ok": false, "message": "The file-safety helper could not start. No save operation was requested."}
	_pid = int(process.pid)
	_thread = Thread.new()
	var error := _thread.start(_exchange.bind(process.stdio, request))
	if error != OK:
		OS.kill(_pid)
		_thread = null
		_pid = -1
		return {"ok": false, "message": "The protected file operation could not be started."}
	var started := Time.get_ticks_msec()
	var timed_out := false
	while _thread.is_alive():
		if not timed_out and Time.get_ticks_msec() - started > REQUEST_TIMEOUT_MS:
			timed_out = true
			OS.kill(_pid)
		await get_tree().process_frame
	var response: String = str(_thread.wait_to_finish())
	_thread = null
	# One bounded request per helper. Reap/terminate only this owned child.
	if OS.is_process_running(_pid):
		OS.kill(_pid)
	_pid = -1
	var parser := JSON.new()
	var parsed := parser.parse(response)
	var decoded: Variant = parser.data if parsed == OK else null
	if timed_out or not decoded is Dictionary or decoded.get("protocol", 0) != 1:
		return {"ok": false, "may_have_output": request.get("op", "") == "publish",
			"output": request.get("output", ""),
			"message": "The file-safety helper did not finish with a valid receipt. If publication was requested, a copy may exist; inspect it before use."}
	return decoded as Dictionary

func _exchange(pipe: FileAccess, request: Dictionary) -> String:
	pipe.store_line(JSON.stringify(request))
	return pipe.get_line()

func _exit_tree() -> void:
	if _pid > 0 and OS.is_process_running(_pid):
		OS.kill(_pid)
	if _thread != null:
		_thread.wait_to_finish()
		_thread = null
