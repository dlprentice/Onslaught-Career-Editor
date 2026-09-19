# SPDX-License-Identifier: MIT
extends RefCounted
## Direct Godot .NET adapter checks on fresh, invocation-owned copies only.
## This suite tests filesystem identity/publication. Career semantics belong to
## test_career_save.gd; the adapter deliberately does not interpret save fields.

const ProtectedFiles = preload("res://io/ProtectedSaveFiles.cs")


static func run(original: PackedByteArray, output_dir: String) -> Array[String]:
	var failures: Array[String] = []
	if original.size() != 10004:
		return ["Protected file tests require bytes from an owned real 10,004-byte baseline."]
	var root: String = output_dir.path_join("protected-files")
	if DirAccess.dir_exists_absolute(root) or FileAccess.file_exists(root):
		return ["Protected file tests require a fresh invocation-owned output directory."]
	if DirAccess.make_dir_recursive_absolute(root) != OK:
		return ["Could not create the owned protected-file test directory."]
	var adapter: RefCounted = ProtectedFiles.new()
	var original_hash: String = _hash(original)

	var roundtrip: Dictionary = _fixture(root, "roundtrip", original, failures)
	var snapshot: Dictionary = _open(adapter, roundtrip.input)
	_check(snapshot.get("ok", false), "Direct adapter opens the owned baseline.", failures)
	if not snapshot.get("ok", false):
		failures.append("Protected baseline open failed: " + str(snapshot.get("message", "No receipt.")))
		return failures
	_check(snapshot.bytes == original and snapshot.size == 10004 and snapshot.sha256 == original_hash, "Open returns exact bytes, size and independently calculated SHA-256.", failures)
	_check(not str(snapshot.identity).is_empty(), "Open returns physical file identity.", failures)
	var copied: Dictionary = _publish(adapter, roundtrip, snapshot, original)
	_check(copied.get("ok", false) and copied.get("verified", false) and copied.get("original_verified", false), "Unchanged copy has explicit publication and original verification.", failures)
	var reopened: Dictionary = _open(adapter, roundtrip.output)
	_check(reopened.get("ok", false) and reopened.get("bytes", PackedByteArray()) == original, "Unchanged output reopens byte-for-byte identical.", failures)
	_check(reopened.get("identity", "") != snapshot.identity, "The recovery copy has its own physical identity.", failures)
	_check(DirAccess.get_files_at(roundtrip.output_dir).size() == 1, "Successful publication leaves only the requested named copy.", failures)
	_original_unchanged(roundtrip, original, failures)

	var edited: Dictionary = _fixture(root, "edited", original, failures)
	var prepared: PackedByteArray = original.duplicate()
	# Independent literal layout and three-byte arithmetic; no call to CareerSave.
	const START: int = 0x2406
	var target: int = ((int(original[START]) | (int(original[START + 1]) << 8) | (int(original[START + 2]) << 16)) + 123457) & 0xFFFFFF
	for index: int in range(3):
		prepared[START + index] = (target >> (index * 8)) & 0xFF
	snapshot = _open(adapter, edited.input)
	var written: Dictionary = _publish(adapter, edited, snapshot, prepared)
	_check(written.get("ok", false), "Direct adapter publishes the independently prepared edit.", failures)
	var actual: PackedByteArray = FileAccess.get_file_as_bytes(edited.output)
	_check(actual.size() == original.size() and actual == prepared, "Published output has exact prepared bytes and original length.", failures)
	if actual.size() == original.size():
		var valid_diff: bool = true
		for offset: int in range(original.size()):
			if (offset < START or offset >= START + 3) and actual[offset] != original[offset]:
				valid_diff = false
		var intended: int = int(actual[START]) | (int(actual[START + 1]) << 8) | (int(actual[START + 2]) << 16)
		_check(valid_diff and intended == target, "Independent diff preserves every unknown/unselected byte, including the packed high byte.", failures)
	_check(written.get("bytes", PackedByteArray()) == prepared and written.get("sha256", "") == _hash(prepared), "Publication receipt contains exact output bytes and independent SHA-256.", failures)
	_original_unchanged(edited, original, failures)

	var malformed: Dictionary = _fixture(root, "malformed", original, failures)
	snapshot = _open(adapter, malformed.input)
	var too_long: PackedByteArray = original.duplicate()
	too_long.append(0)
	for bytes: PackedByteArray in [PackedByteArray(), original.slice(0, 10003), too_long]:
		_refusal(_publish(adapter, malformed, snapshot, bytes), "Incorrect prepared length", failures)
	for bad_hash: String in ["", "0", "z".repeat(64), "0".repeat(64)]:
		var bad_snapshot: Dictionary = snapshot.duplicate(true)
		bad_snapshot.sha256 = bad_hash
		_refusal(_publish(adapter, malformed, bad_snapshot, original), "Malformed or incorrect source hash", failures)
	var no_identity: Dictionary = snapshot.duplicate(true)
	no_identity.identity = ""
	_refusal(_publish(adapter, malformed, no_identity, original), "Missing source identity", failures)
	_check(DirAccess.get_files_at(malformed.output_dir).is_empty(), "Invalid publication arguments create no named output.", failures)
	_original_unchanged(malformed, original, failures)
	_write_owned(malformed.input, original.slice(0, 10003), failures)
	_refusal(_open(adapter, malformed.input), "Truncated source", failures)
	_write_owned(root.path_join("unsupported.bin"), original, failures)
	for path: String in ["", "relative.bes", malformed.input + " ", root.path_join("unsupported.bin")]:
		_refusal(_open(adapter, path), "Invalid source path", failures)

	var changed: Dictionary = _fixture(root, "changed-source", original, failures)
	snapshot = _open(adapter, changed.input)
	var changed_bytes: PackedByteArray = original.duplicate()
	changed_bytes[changed_bytes.size() - 1] ^= 1
	_write_owned(changed.input, changed_bytes, failures)
	_refusal(_publish(adapter, changed, snapshot, original), "Changed source content", failures)
	_check(not FileAccess.file_exists(changed.output) and FileAccess.get_file_as_bytes(changed.input) == changed_bytes, "Changed-source refusal preserves the changed source and publishes nothing.", failures)

	var replaced: Dictionary = _fixture(root, "replaced-source", original, failures)
	snapshot = _open(adapter, replaced.input)
	var displaced: String = replaced.root.path_join("displaced.bes")
	var moved: Error = DirAccess.rename_absolute(replaced.input, displaced)
	_check(moved == OK, "Owned source moved aside for physical identity test.", failures)
	if moved == OK:
		_write_owned(replaced.input, original, failures)
		_refusal(_publish(adapter, replaced, snapshot, original), "Same bytes under a new physical source identity", failures)
		_check(not FileAccess.file_exists(replaced.output) and FileAccess.get_file_as_bytes(displaced) == original, "Identity refusal leaves both owned source generations intact.", failures)
		_original_unchanged(replaced, original, failures)

	var conflict: Dictionary = _fixture(root, "conflicting-output", original, failures)
	snapshot = _open(adapter, conflict.input)
	_write_owned(conflict.output, changed_bytes, failures)
	_refusal(_publish(adapter, conflict, snapshot, original), "Existing destination", failures)
	_check(FileAccess.get_file_as_bytes(conflict.output) == changed_bytes, "The conflicting destination is never replaced.", failures)
	var same_path: Dictionary = conflict.duplicate()
	same_path.output = conflict.input
	_refusal(_publish(adapter, same_path, snapshot, original), "Source as destination", failures)
	var missing_folder: Dictionary = conflict.duplicate()
	missing_folder.output = conflict.root.path_join("missing/copy.bes")
	_refusal(_publish(adapter, missing_folder, snapshot, original), "Missing destination parent", failures)
	_check(not DirAccess.dir_exists_absolute(conflict.root.path_join("missing")), "Publication does not create an unapproved output folder.", failures)
	_original_unchanged(conflict, original, failures)

	var game: Dictionary = _fixture(root, "game-tree", original, failures)
	snapshot = _open(adapter, game.input)
	_write_owned(game.output_dir.path_join("BEA.exe"), "Owned test marker; not an executable.".to_utf8_buffer(), failures)
	_check(DirAccess.make_dir_absolute(game.output_dir.path_join("data")) == OK, "Owned game-tree shape created.", failures)
	_refusal(_publish(adapter, game, snapshot, original), "Game-tree destination", failures)
	_check(not FileAccess.file_exists(game.output), "Game-tree refusal creates no save.", failures)
	_original_unchanged(game, original, failures)

	if OS.get_name() == "Linux":
		_linux_aliases(adapter, root, original, failures)
	return failures


static func _linux_aliases(adapter: RefCounted, root: String, original: PackedByteArray, failures: Array[String]) -> void:
	var links: Dictionary = _fixture(root, "symlinks", original, failures)
	var snapshot: Dictionary = _open(adapter, links.input)
	var directory: DirAccess = DirAccess.open(links.root)
	_check(directory.create_link(links.input, "source-link.bes") == OK, "Owned source symlink created.", failures)
	_refusal(_open(adapter, links.root.path_join("source-link.bes")), "Linked source", failures)
	_check(directory.create_link(links.output_dir, "output-link") == OK, "Owned output-parent symlink created.", failures)
	var linked_output: Dictionary = links.duplicate()
	linked_output.output = links.root.path_join("output-link/copy.bes")
	_refusal(_publish(adapter, linked_output, snapshot, original), "Linked output parent", failures)
	_check(DirAccess.get_files_at(links.output_dir).is_empty(), "Linked-parent refusal creates no output.", failures)
	var dangling: String = links.root.path_join("absent-target.bes")
	var output_directory: DirAccess = DirAccess.open(links.output_dir)
	_check(output_directory.create_link(dangling, "copy.bes") == OK, "Owned dangling output symlink created.", failures)
	_refusal(_publish(adapter, links, snapshot, original), "Dangling destination symlink", failures)
	_check(output_directory.is_link("copy.bes") and not FileAccess.file_exists(dangling), "Dangling destination link survives and its target is not created.", failures)
	_original_unchanged(links, original, failures)

	var hard: Dictionary = _fixture(root, "hardlinks", original, failures)
	snapshot = _open(adapter, hard.input)
	var alias: String = hard.root.path_join("alias.bes")
	# Linux-only test setup. Explicit absolute executable and argv; no shell.
	var command_output: Array = []
	var exit_code: int = OS.execute("/usr/bin/ln", PackedStringArray(["--", hard.input, alias]), command_output, true)
	_check(exit_code == 0, "Owned hardlink fixture created with /usr/bin/ln.", failures)
	if exit_code == 0:
		_refusal(_open(adapter, alias), "Hardlinked source before open", failures)
		_refusal(_publish(adapter, hard, snapshot, original), "Hardlink added after source open", failures)
		_check(not FileAccess.file_exists(hard.output) and FileAccess.get_file_as_bytes(alias) == original, "Hardlink refusal leaves alias bytes unchanged and publishes nothing.", failures)
	_original_unchanged(hard, original, failures)


static func _fixture(root: String, name: String, original: PackedByteArray, failures: Array[String]) -> Dictionary:
	var owned: String = root.path_join(name)
	var output: String = owned.path_join("output")
	_check(DirAccess.make_dir_recursive_absolute(output) == OK, "Owned case directory created: " + name, failures)
	var input: String = owned.path_join("original.bes")
	_write_owned(input, original, failures)
	return {"root": owned, "input": input, "output_dir": output, "output": output.path_join("copy.bes")}


static func _write_owned(path: String, bytes: PackedByteArray, failures: Array[String]) -> void:
	var file: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		failures.append("Could not write invocation-owned test fixture: " + path)
		return
	file.store_buffer(bytes)
	file.close()


static func _open(adapter: RefCounted, path: String) -> Dictionary:
	return adapter.call("OpenCareer", path)


static func _publish(adapter: RefCounted, fixture: Dictionary, snapshot: Dictionary, prepared: PackedByteArray) -> Dictionary:
	return adapter.call("PublishCopy", fixture.input, str(snapshot.get("identity", "")), str(snapshot.get("sha256", "")), fixture.output, prepared)


static func _hash(bytes: PackedByteArray) -> String:
	var hashing: HashingContext = HashingContext.new()
	hashing.start(HashingContext.HASH_SHA256)
	hashing.update(bytes)
	return hashing.finish().hex_encode().to_upper()


static func _original_unchanged(fixture: Dictionary, original: PackedByteArray, failures: Array[String]) -> void:
	_check(FileAccess.get_file_as_bytes(fixture.input) == original, "Original remains byte-identical: " + str(fixture.root.get_file()), failures)


static func _refusal(reply: Dictionary, context: String, failures: Array[String]) -> void:
	_check(not reply.get("ok", true) and not reply.get("verified", false), context + " is refused without a success receipt.", failures)
	_check(not reply.get("may_have_output", true), context + " is rejected before publication.", failures)


static func _check(condition: bool, message: String, failures: Array[String]) -> void:
	if not condition:
		failures.append(message)
