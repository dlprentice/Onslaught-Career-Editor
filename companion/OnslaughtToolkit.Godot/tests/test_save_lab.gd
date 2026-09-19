# SPDX-License-Identifier: MIT
extends SceneTree
## Executed scene + protected process workflow, exclusively on runner-owned copies.

const Codec = preload("res://domain/career_save.gd")
const Session = preload("res://domain/save_session.gd")
const DomainTests = preload("res://tests/test_career_save.gd")
const MediaTests = preload("res://tests/test_media_catalog.gd")
var failures: Array[String] = []
var output_dir := ""

func _initialize() -> void:
	_run.call_deferred()

func check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
		printerr("FAIL: " + message)

func _run() -> void:
	var fixture := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--fixture="):
			fixture = arg.trim_prefix("--fixture=")
		if arg.begins_with("--output-dir="):
			output_dir = arg.trim_prefix("--output-dir=")
	if fixture.is_empty() or output_dir.is_empty():
		printerr("Owned --fixture and --output-dir are required.")
		quit(2)
		return
	var original := FileAccess.get_file_as_bytes(fixture)
	check(original.size() == 10004, "runner supplied owned real career baseline")
	if original.size() != 10004:
		quit(1)
		return
	failures.append_array(DomainTests.run(original))
	failures.append_array(MediaTests.run(output_dir))
	var scene = load("res://SaveLab.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	check(scene.get_node("%Rows").get_child_count() == 5, "five scene-authored editable rows")
	check(scene.get_node("%WriteCopy").disabled, "writing unavailable before open")
	for name in ["OpenDialog", "OutputDialog", "CompareDialog"]:
		var dialog: FileDialog = scene.get_node("%" + name)
		check(not dialog.deleting_enabled and not dialog.folder_creation_enabled, "file dialog has no mutation actions")
	var opened: Dictionary = await scene.open_career(fixture)
	check(opened.get("ok", false), "native scene opens protected real fixture")
	if not opened.get("ok", false):
		printerr(opened.get("message", "open failed"))
		scene.queue_free()
		await process_frame
		quit(1)
		return
	var leaked: PackedByteArray = scene._session.bytes()
	leaked[12] ^= 1
	check(scene._session.bytes() == original, "session bytes are not exposed for mutation")
	# An explicit unchanged copy exercises byte-for-byte round trip and reopen.
	var recovery := output_dir.path_join("recovery.bes")
	scene.get_node("%Destination").text = recovery
	var backup: Dictionary = await scene.write_copy(true)
	check(backup.get("ok", false), "unchanged copy publishes and reopens")
	check(FileAccess.get_file_as_bytes(recovery) == original, "round trip preserves every byte")
	# Drive real row controls. Preview must not write, and only two categories change.
	var rows: VBoxContainer = scene.get_node("%Rows")
	for index in [0, 4]:
		rows.get_child(index).get_node("%Target").value = 123456 + index
		rows.get_child(index).get_node("%Selected").button_pressed = true
	var edited := output_dir.path_join("edited.bes")
	scene.get_node("%Destination").text = edited
	check(not FileAccess.file_exists(edited), "preview does not write")
	check(not scene.get_node("%WriteCopy").disabled, "valid explicit preview enables write")
	var written: Dictionary = await scene.write_copy(false)
	check(written.get("ok", false), "selected edit publishes and reopens")
	var actual := FileAccess.get_file_as_bytes(edited)
	check(actual.size() == original.size(), "edited length preserved")
	if actual.size() == original.size():
		# Independent literal layout assertion, not a call to the codec under test.
		for offset in range(original.size()):
			var allowed := (offset >= 0x23F6 and offset < 0x23F9) or (offset >= 0x2406 and offset < 0x2409)
			if not allowed and actual[offset] != original[offset]:
				check(false, "unselected byte changed at %d" % offset)
		check((actual.decode_u32(0x23F6) & 0xFFFFFF) == 123456, "aircraft intended count independently read")
		check((actual.decode_u32(0x2406) & 0xFFFFFF) == 123460, "mech intended count independently read")
	check(FileAccess.get_file_as_bytes(fixture) == original, "original unchanged after publication")
	var compared: Dictionary = await scene.compare_career(edited)
	check(compared.get("ok", false) and compared.comparison.changed_bytes > 0, "native byte comparison reports output difference")
	var duplicate: Dictionary = await scene.write_copy(false)
	check(not duplicate.get("ok", false), "existing output refused")
	check(FileAccess.get_file_as_bytes(edited) == actual, "conflicting output is unchanged")
	check(scene.get_node("%ReopenCopy").disabled, "failed publication cannot offer stale successful result")
	# Malformed bytes are read safely but refused by the GDScript domain.
	var malformed := original.duplicate()
	malformed[0] ^= 1
	_write_owned("malformed.bes", malformed)
	var refused: Dictionary = await scene.open_career(output_dir.path_join("malformed.bes"))
	check(not refused.get("ok", false), "malformed version refused by native scene")
	check(scene._session.path == fixture, "failed open keeps clearly displayed original session")
	# Source contents changed since open: refuse and leave destination absent.
	var changed := original.duplicate()
	changed[changed.size() - 1] ^= 1
	_write_path(fixture, changed)
	var refused_output := output_dir.path_join("source-changed.bes")
	scene.get_node("%Destination").text = refused_output
	refused = await scene.write_copy(false)
	check(not refused.get("ok", false), "source change refused")
	check(not FileAccess.file_exists(refused_output), "source refusal publishes nothing")
	_write_path(fixture, original)
	# No helper means unavailable, never a fallback to FileAccess writes.
	var helper := OS.get_environment("ONSLAUGHT_FILE_BRIDGE")
	OS.set_environment("ONSLAUGHT_FILE_BRIDGE", output_dir.path_join("absent-helper"))
	refused = await scene.write_copy(false)
	check(not refused.get("ok", false), "missing safety helper fails closed")
	check(not FileAccess.file_exists(refused_output), "missing helper writes nothing")
	if OS.get_name() == "Linux":
		var malformed_helper := output_dir.path_join("malformed-receipt-helper")
		var helper_file := FileAccess.open(malformed_helper, FileAccess.WRITE)
		helper_file.store_string("#!/bin/sh\nIFS= read -r line\nprintf 'not-json\\n'\n")
		helper_file.close()
		check(FileAccess.set_unix_permissions(malformed_helper, 448) == OK, "test receipt helper executable")
		OS.set_environment("ONSLAUGHT_FILE_BRIDGE", malformed_helper)
		refused = await scene.write_copy(false)
		check(not refused.get("ok", false) and refused.get("may_have_output", false), "invalid publication receipt retains uncertainty")
		check(scene.get_node("%ReopenCopy").disabled, "invalid receipt cannot offer a verified result")
	OS.set_environment("ONSLAUGHT_FILE_BRIDGE", helper)
	check(FileAccess.get_file_as_bytes(fixture) == original, "owned fixture restored after adversarial scenario")
	scene.queue_free()
	await process_frame
	for failure in failures:
		printerr(failure)
	print("NATIVE_SAVE_LAB: " + str(failures.size()) + " failures; byte domain, real scene, protected round trip, selected diff, comparison and fail-closed cases executed.")
	quit(0 if failures.is_empty() else 1)

func _write_owned(name: String, bytes: PackedByteArray) -> void:
	_write_path(output_dir.path_join(name), bytes)

func _write_path(path: String, bytes: PackedByteArray) -> void:
	# Test-only mutation of a runner-owned fixture or fresh unique output.
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_buffer(bytes)
	file.close()
