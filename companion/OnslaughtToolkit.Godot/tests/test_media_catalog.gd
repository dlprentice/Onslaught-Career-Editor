# SPDX-License-Identifier: MIT
extends RefCounted
## The parent passes an invocation-owned output directory. Fixtures are tiny,
## original byte headers, never retail assets or valid game-save replacements.

const Catalog = preload("res://domain/media_catalog.gd")


static func run(root: String) -> Array[String]:
	var failures: Array[String] = []
	var fixture: String = root.path_join("media-catalog-fixtures")
	if DirAccess.dir_exists_absolute(fixture) or FileAccess.file_exists(fixture):
		return ["Media catalog tests require a fresh invocation-owned output directory."]
	if DirAccess.make_dir_recursive_absolute(fixture.path_join("nested")) != OK:
		return ["Media catalog test folders could not be created."]
	DirAccess.make_dir_recursive_absolute(fixture.path_join("empty"))
	var empty: Dictionary = _scan(fixture.path_join("empty"))
	_check(empty.ok and empty.complete and empty.items.is_empty(), "Empty folder returns an honest empty list.", failures)
	var missing: Dictionary = _scan(fixture.path_join("missing"))
	_check(not missing.ok and not missing.complete and missing.items.is_empty(), "Missing folder is refused, not reported as empty.", failures)
	var headers: Dictionary = {
		"music.OGG": "4f67675300020000", "sound.wav": "524946460000000057415645",
		"voice.mp3": "494433040000", "movie.bik": "42494b69",
		"cutscene.vid": "56494400", "image.png": "89504e470d0a1a0a",
		"photo.jpg": "ffd8ffe0", "empty.bmp": "", "nested/frame.tga": "000002",
		"not-media.bin": "00010203"
	}
	for name: String in headers:
		var file: FileAccess = FileAccess.open(fixture.path_join(name), FileAccess.WRITE)
		if file == null:
			failures.append("Could not create owned media fixture: " + name)
			return failures
		file.store_buffer(str(headers[name]).hex_decode())
		file.close()
	var full: Dictionary = _scan(fixture)
	_check(full.ok and full.complete and full.items.size() == 9, "Known media extensions are inventoried; unrelated files are omitted.", failures)
	var by_path: Dictionary = {}
	for item: Dictionary in full.items:
		by_path[item.relative_path] = item
		_check(item.support == "Metadata only" and item.size == str(headers[item.relative_path]).hex_decode().size(), "Reported sizes and metadata-only support are accurate.", failures)
	_check(by_path.has("nested/frame.tga") and by_path.has("music.OGG"), "Nested relative paths and uppercase extensions are supported.", failures)
	_check(by_path.get("empty.bmp", {}).get("size", -1) == 0, "A zero-length file is not mistaken for a size read failure.", failures)
	_check(by_path.get("movie.bik", {}).get("format", "") == "Bink" and by_path.get("cutscene.vid", {}).get("format", "") == "VID", "Container names remain separate from playback claims.", failures)
	var shallow: Dictionary = _scan(fixture, 0)
	_check(not shallow.complete and shallow.depth_skips >= 1 and shallow.items.size() == 8, "Depth cap marks the list incomplete and skips nested media.", failures)
	var capped: Dictionary = _scan(fixture, 8, 1)
	_check(not capped.complete and capped.items.size() == 1, "Media item cap is enforced and reported.", failures)
	var entry_capped: Dictionary = _scan(fixture, 8, 5000, 1)
	_check(not entry_capped.complete and entry_capped.entries == 1, "Nonmedia and folder traversal is also bounded by an entry limit.", failures)
	var cancelled: CompanionMediaCatalog = Catalog.new()
	cancelled.begin(fixture)
	cancelled.step(1)
	cancelled.cancel()
	var cancelled_result: Dictionary = cancelled.result()
	_check(cancelled_result.done and cancelled_result.cancelled and not cancelled_result.complete, "Cancellation finishes with an explicitly incomplete result.", failures)
	if OS.get_name() == "Linux":
		var directory: DirAccess = DirAccess.open(fixture)
		var file_link: Error = directory.create_link(fixture.path_join("music.OGG"), "linked.ogg")
		var folder_link: Error = directory.create_link(fixture.path_join("nested"), "linked-folder")
		_check(file_link == OK and folder_link == OK, "Owned Linux symlink fixtures can be created.", failures)
		var linked: Dictionary = _scan(fixture)
		_check(linked.skipped_links == 2 and linked.items.size() == 9, "Linked files and folders are skipped without duplicate entries.", failures)
		var root_link: Dictionary = _scan(fixture.path_join("linked-folder"))
		_check(not root_link.ok and root_link.items.is_empty(), "Selecting a linked root is refused.", failures)
	for name: String in headers:
		_check(FileAccess.get_file_as_bytes(fixture.path_join(name)) == str(headers[name]).hex_decode(), "Scanning left owned fixture bytes unchanged: " + name, failures)
	return failures


static func _scan(root: String, depth: int = 8, items: int = 5000, entries: int = 30000) -> Dictionary:
	var scanner: CompanionMediaCatalog = Catalog.new()
	scanner.begin(root, depth, items, entries)
	var batches: int = 0
	while not scanner.done and batches < 10000:
		scanner.step(4)
		batches += 1
	if not scanner.done:
		scanner.cancel()
	return scanner.result()


static func _check(condition: bool, message: String, failures: Array[String]) -> void:
	if not condition:
		failures.append(message)
