# SPDX-License-Identifier: GPL-3.0-or-later
extends RefCounted
## First Flight launch argument admission, before any media or career files are
## opened. Returns {ok, value:{smoke, report_path, capture_arguments_present,
## skip_startup_media, force_startup_media, record_tape_path}} or an explicit
## ArgumentException. Paths are "" when absent.


static func parse(arguments: PackedStringArray) -> Dictionary:
	var smoke: bool = false
	var capture: bool = false
	var skip: bool = false
	var intro: bool = false
	var report: Variant = null
	var tape: Variant = null
	for argument: String in arguments:
		if argument == "--smoke":
			smoke = true
		elif argument == "--skipfmv":
			skip = true
		elif argument == "--intro":
			intro = true
		elif argument.begins_with("--report="):
			if report != null:
				return _argument("--report may only be specified once.")
			report = argument.substr("--report=".length())
		elif argument.begins_with("--record-tape="):
			if tape != null:
				return _argument("--record-tape may only be specified once.")
			tape = argument.substr("--record-tape=".length())
		elif argument.begins_with("--capture-dir=") or argument.begins_with("--capture-plan=") \
				or argument.begins_with("--capture-size=") or argument.begins_with("--capture-offsets-ms="):
			capture = true
		elif argument.begins_with("--startup-media=") or argument.begins_with("--career-save="):
			pass # Their own adapters own path/content validation and file reads.
		else:
			return _argument("Unknown First Flight argument '%s'." % argument)
	# The host and the capture rig each drive the frontend and request
	# application exit. They cannot own one run simultaneously.
	if smoke and capture:
		return _argument("Smoke mode and capture arguments cannot be used together.")
	if smoke and (report == null or String(report).strip_edges().is_empty() or not is_fully_qualified(report)):
		return _argument("Smoke mode requires an absolute --report path.")
	if tape != null and (not is_fully_qualified(tape) or String(tape).get_extension().to_lower() != "json"):
		return _argument("--record-tape requires an absolute .json path outside career-save and retail storage.")
	return {"ok": true, "value": {"smoke": smoke, "report_path": "" if report == null else report,
		"capture_arguments_present": capture, "skip_startup_media": skip, "force_startup_media": intro,
		"record_tape_path": "" if tape == null else tape}}


## .NET Path.IsPathFullyQualified: rooted at "/" on Linux; a drive root or UNC
## share on Windows.
static func is_fully_qualified(path: String) -> bool:
	if OS.get_name() != "Windows":
		return path.begins_with("/")
	if path.begins_with("\\\\") or path.begins_with("//"):
		return true
	return path.length() >= 3 and path[1] == ":" and (path[2] == "\\" or path[2] == "/") \
		and ((path[0] >= "A" and path[0] <= "Z") or (path[0] >= "a" and path[0] <= "z"))


static func _argument(message: String) -> Dictionary:
	return {"ok": false, "error_type": "ArgumentException", "error": message}
