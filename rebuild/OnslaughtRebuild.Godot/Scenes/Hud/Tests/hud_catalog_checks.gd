# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Args: absolute reference.variant, absolute report.json, optional
## --write-reference (first .NET run only). Both paths must be in this worktree's
## owned local-data; writes refuse existing files and linked parent directories.
## The standard engine repeats the same actual catalog comparison from that
## object-free private fixture. No manifest copies, input writes, UI, or audio.

const HudCatalog = preload("res://Client/hud_catalog.gd")
var _failures: Array[String] = []
var _counts: Dictionary = {}
var _completed: Array[String] = []
var _report_path: String = ""


func _initialize() -> void:
	call_deferred("_run")


func _check(category: String, name: String, actual: Variant, expected: Variant) -> bool:
	_counts[category] = int(_counts.get(category, 0)) + 1
	if actual != expected:
		# Private text is compared in memory, never echoed into engine logs.
		_failures.append(category + ":" + name)
		return false
	return true


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 2 or args.size() > 3 or (args.size() == 3 and args[2] != "--write-reference"):
		print("HUD_CATALOG_CHECKS: expected reference.variant, report.json, and optional --write-reference.")
		quit(2)
		return
	var writing: bool = args.size() == 3
	if not _owned_path(args[0]) or not _owned_path(args[1]) or args[0] == args[1] \
			or FileAccess.file_exists(args[1]) or (writing and FileAccess.file_exists(args[0])):
		print("HUD_CATALOG_CHECKS: outputs must be fresh files under the worktree's owned local-data.")
		quit(2)
		return
	_report_path = args[1]
	var reference: Dictionary = _reference(args[0], writing)
	if reference.is_empty():
		_finish()
		return
	if not _check("fixture", "schema", reference.get("schema"), 1):
		_finish()
		return
	var before: PackedByteArray = FileAccess.get_file_as_bytes(HudCatalog.RESOURCE_PATH)
	_check("read_only", "manifest_present", not before.is_empty(), true)
	var read_result: Dictionary = HudCatalog.load_catalog()
	var bytes_result: Dictionary = HudCatalog.load_bytes(before)
	if not _check("admission", "read_pinned_manifest", read_result.get("ok"), true) \
			or not _check("admission", "admit_pinned_bytes", bytes_result.get("ok"), true):
		_finish()
		return
	var catalog: HudCatalog.Catalog = read_result.value
	var byte_catalog: HudCatalog.Catalog = bytes_result.value
	_check("admission", "read_and_bytes_same", catalog.verified_text_batch(), byte_catalog.verified_text_batch())
	_check("identity", "pins", {"ResourcePath": HudCatalog.RESOURCE_PATH, "ExpectedSha256": HudCatalog.EXPECTED_SHA256,
		"ExpectedSchema": HudCatalog.EXPECTED_SCHEMA, "ExpectedLevelScriptSha256": HudCatalog.EXPECTED_LEVEL_SCRIPT_SHA256,
		"ExpectedEnglishSourceSha256": HudCatalog.EXPECTED_ENGLISH_SOURCE_SHA256,
		"ExpectedTextStfSha256": HudCatalog.EXPECTED_TEXT_STF_SHA256,
		"ExpectedEnglishDatSha256": HudCatalog.EXPECTED_ENGLISH_DAT_SHA256}, reference.pins)
	_check("identity", "input_sha256", _sha256(before), reference.manifest_sha256)
	_check("identity", "fixed_sha256", reference.manifest_sha256, HudCatalog.EXPECTED_SHA256)
	_check("identity", "51_messages", reference.messages.size(), 51)
	_check("identity", "six_help", reference.help.size(), 6)
	_check("identity", "eight_terminal_strings", reference.terminal.size(), 8)
	_check("identity", "51_character_specs", reference.character_specs.size(), 51)
	_check("definitions", "all_messages_raw_utf16", catalog.message_definitions(), reference.messages)
	_check("definitions", "all_help_raw_utf16", catalog.help_definitions(), reference.help)
	_check("definitions", "all_terminal_raw_utf16", catalog.terminal_strings(), reference.terminal)
	_check("definitions", "audio_identity_and_order", HudCatalog.character_message_specs(), reference.character_specs)
	_check("definitions", "production_text_batch", catalog.verified_text_batch(), reference.batch)
	_check("definitions", "production_boot_admission", HudCatalog.load_verified_text_batch(), {"ok": true, "value": reference.batch})
	for identity: int in reference.messages:
		var row: Dictionary = catalog.get_required_message(identity)
		_check("message_records", str(identity), row, {"ok": true, "value": reference.messages[identity]})
		for key: String in ["symbol", "audio_file", "text"]:
			_check("raw_text", str(identity) + ":" + key, typeof(row.value[key]), TYPE_PACKED_INT32_ARRAY)
	for identity: int in reference.help:
		_check("help_records", str(identity), catalog.get_required_help(identity), {"ok": true, "value": reference.help[identity]})
	for row: Dictionary in reference.message_lookups:
		_check("try_lookup", str(row.id), catalog.try_get(row.id), row.try_result)
		_check("required_lookup", str(row.id), catalog.get_required_message(row.id), row.required_result)
	for row: Dictionary in reference.help_lookups:
		_check("help_lookup", str(row.id), catalog.get_required_help(row.id), row.result)
	for row: Dictionary in reference.failure_lookups:
		_check("failure_lookup", str(row.id), catalog.get_failure_reason(row.id), row.result)
	_check("fixture", "message_lookup_extent", reference.message_lookups.size(), 56)
	_check("fixture", "help_lookup_extent", reference.help_lookups.size(), 11)
	_check("fixture", "failure_lookup_extent", reference.failure_lookups.size(), 8)
	_completed.append("definitions")
	_rejections(before, reference.rejected_hashes)
	_completed.append("rejections")
	_detachment(catalog, reference)
	_completed.append("detachment")
	_check("read_only", "manifest_unchanged", FileAccess.get_file_as_bytes(HudCatalog.RESOURCE_PATH), before)
	_completed.append("read_only")
	_finish()


func _rejections(original: PackedByteArray, rejected_hashes: Dictionary) -> void:
	var missing_result: Dictionary = {"ok": false, "error_type": "InvalidDataException",
		"error": "Released Level 100 HUD event manifest is missing: " + HudCatalog.RESOURCE_PATH}
	_check("admission", "empty_bytes", HudCatalog.load_bytes(PackedByteArray()), missing_result)
	var absent: String = _report_path + ".missing-manifest"
	if _check("admission", "missing_probe_is_absent", FileAccess.file_exists(absent), false):
		_check("admission", "missing_file", HudCatalog.load_catalog(absent), missing_result)
	var whitespace: PackedByteArray = original.duplicate()
	whitespace.append(10)
	var changed: PackedByteArray = original.duplicate()
	changed[0] ^= 1
	var inputs: Dictionary = {"empty_object": "{}".to_utf8_buffer(), "null": "null".to_utf8_buffer(),
		"malformed": '{"schemaVersion":'.to_utf8_buffer(), "whitespace_only_change": whitespace,
		"one_byte_corruption": changed}
	_check("fixture", "rejected_hash_extent", rejected_hashes.size(), inputs.size())
	for name: String in inputs:
		_check("admission", name, HudCatalog.load_bytes(inputs[name]), {
			"ok": false, "error_type": "InvalidDataException",
			"error": "Released Level 100 HUD event manifest has unexpected SHA-256: " + String(rejected_hashes[name])})
	var loaded: Dictionary = HudCatalog.load_bytes(original)
	if not _check("admission", "original_still_admitted", loaded.get("ok"), true):
		return
	var catalog: HudCatalog.Catalog = loaded.value
	var invalids: Array = [null, true, false, 1.0, "1", [], {}, -2147483649, 2147483648]
	for index: int in range(invalids.size()):
		_check("host_types", "try:" + str(index), catalog.try_get(invalids[index]).get("error_type"), "ArgumentException")
		_check("host_types", "message:" + str(index), catalog.get_required_message(invalids[index]).get("error_type"), "ArgumentException")
		_check("host_types", "help:" + str(index), catalog.get_required_help(invalids[index]).get("error_type"), "ArgumentException")
		_check("host_types", "failure:" + str(index), catalog.get_failure_reason(invalids[index]).get("error_type"), "ArgumentException")


func _detachment(catalog: HudCatalog.Catalog, reference: Dictionary) -> void:
	var identity: int = reference.character_specs[0].message_id
	var lookup: Dictionary = catalog.get_required_message(identity)
	var text: PackedInt32Array = lookup.value.text
	text[0] ^= 1
	lookup.value.text = text
	_check("detachment", "message_lookup", catalog.get_required_message(identity).value, reference.messages[identity])
	var messages: Dictionary = catalog.message_definitions()
	messages[identity].symbol = PackedInt32Array([0])
	messages.clear()
	_check("detachment", "message_table", catalog.message_definitions(), reference.messages)
	var help: Dictionary = catalog.help_definitions()
	help.clear()
	_check("detachment", "help_table", catalog.help_definitions(), reference.help)
	var terminal: Dictionary = catalog.terminal_strings()
	terminal.victory = PackedInt32Array([0])
	_check("detachment", "terminal_table", catalog.terminal_strings(), reference.terminal)
	var batch: Dictionary = catalog.verified_text_batch()
	batch.messages.clear()
	batch.terminal.defeat = PackedInt32Array([0])
	_check("detachment", "production_batch", catalog.verified_text_batch(), reference.batch)
	var specs: Array[Dictionary] = HudCatalog.character_message_specs()
	specs[0].message_id = 0
	specs[0].symbol = PackedInt32Array([0])
	specs.clear()
	_check("detachment", "character_specs", HudCatalog.character_message_specs(), reference.character_specs)


func _reference(path: String, writing: bool) -> Dictionary:
	if writing:
		if not _check("fixture", "dotnet_reference_host", ClassDB.class_exists("CSharpScript"), true):
			return {}
		var script: Script = load("res://Scenes/Hud/Tests/HudCatalogReference.cs")
		if not _check("fixture", "reference_script", script != null, true):
			return {}
		var adapter: RefCounted = script.new()
		var result: Dictionary = adapter.call("LoadReference")
		if not _check("fixture", "reference_load", result.get("ok"), true):
			return {}
		var output := FileAccess.open(path, FileAccess.WRITE)
		if not _check("fixture", "reference_create", output != null, true):
			return {}
		output.store_var(result.value, false)
		output.close()
		return result.value
	if not _check("fixture", "reference_exists", FileAccess.file_exists(path), true):
		return {}
	var input := FileAccess.open(path, FileAccess.READ)
	if not _check("fixture", "reference_open", input != null, true):
		return {}
	var value: Variant = input.get_var(false)
	input.close()
	if not _check("fixture", "reference_dictionary", typeof(value), TYPE_DICTIONARY):
		return {}
	return value


func _owned_path(path: String) -> bool:
	var owned: String = ProjectSettings.globalize_path("res://../../local-data").simplify_path().trim_suffix("/")
	if not path.is_absolute_path() or path != path.simplify_path() or path.contains("\\") \
			or not path.begins_with(owned + "/") or path.get_file().is_empty():
		return false
	var owner_parent := DirAccess.open(owned.get_base_dir())
	if owner_parent == null or owner_parent.is_link(owned.get_file()):
		return false
	var directory := DirAccess.open(owned)
	if directory == null:
		return false
	var relative: String = path.trim_prefix(owned + "/")
	var segments: PackedStringArray = relative.split("/", false)
	for index: int in range(segments.size()):
		if directory.is_link(segments[index]):
			return false
		if index + 1 < segments.size() and directory.change_dir(segments[index]) != OK:
			return false
	return true


func _sha256(data: PackedByteArray) -> String:
	var context := HashingContext.new()
	if context.start(HashingContext.HASH_SHA256) != OK or context.update(data) != OK:
		return ""
	return context.finish().hex_encode()


func _finish() -> void:
	var required: Array[String] = ["definitions", "rejections", "detachment", "read_only"]
	var report: Dictionary = {"schema": 1, "failure_count": _failures.size(), "counts": _counts,
		"failures": _failures, "completed": _completed}
	var output := FileAccess.open(_report_path, FileAccess.WRITE)
	if output == null:
		quit(2)
		return
	output.store_string(JSON.stringify(report, "\t"))
	output.close()
	print("HUD_CATALOG_CHECKS: " + JSON.stringify(report))
	quit(0 if _failures.is_empty() and _completed == required else 1)
