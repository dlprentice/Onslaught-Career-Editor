# SPDX-License-Identifier: MIT
class_name CompanionMediaCatalog
extends RefCounted
## Read-only filename/size inventory. No payloads are loaded or imported.
## Call step() in bounded batches and yield between them in a scene controller.
## Link checks are metadata observations, not a transaction/identity guarantee.

const DEFAULT_DEPTH: int = 8
const DEFAULT_ITEMS: int = 5000
const DEFAULT_ENTRIES: int = 30000
const FORMATS: Dictionary = {
	"ogg": ["Audio/container", "Ogg"], "wav": ["Audio", "WAVE"],
	"mp3": ["Audio", "MPEG audio"], "flac": ["Audio", "FLAC"],
	"bik": ["Video", "Bink"], "vid": ["Video/container", "VID"],
	"ogv": ["Video", "Ogg video"], "webm": ["Video", "WebM"],
	"mp4": ["Video/container", "MP4"], "avi": ["Video/container", "AVI"],
	"png": ["Image", "PNG"], "jpg": ["Image", "JPEG"],
	"jpeg": ["Image", "JPEG"], "bmp": ["Image", "BMP"],
	"tga": ["Image", "TGA"], "dds": ["Image", "DDS"],
	"webp": ["Image", "WebP"], "gif": ["Image", "GIF"],
	"tif": ["Image", "TIFF"], "tiff": ["Image", "TIFF"]
}

var done: bool = true
var _ok: bool = false
var _complete: bool = false
var _cancelled: bool = false
var _root: String = ""
var _items: Array[Dictionary] = []
var _issues: Array[String] = []
var _pending: Array[Dictionary] = []
var _current: DirAccess
var _relative: String = ""
var _depth: int = 0
var _max_depth: int = DEFAULT_DEPTH
var _max_items: int = DEFAULT_ITEMS
var _max_entries: int = DEFAULT_ENTRIES
var _entries: int = 0
var _directories: int = 0
var _skipped_links: int = 0
var _other_files: int = 0
var _depth_skips: int = 0
var _issue_count: int = 0


func begin(root: String, max_depth: int = DEFAULT_DEPTH, max_items: int = DEFAULT_ITEMS, max_entries: int = DEFAULT_ENTRIES) -> Dictionary:
	_close_current()
	done = true
	_ok = false
	_complete = false
	_cancelled = false
	_items.clear()
	_issues.clear()
	_pending.clear()
	_entries = 0
	_directories = 0
	_skipped_links = 0
	_other_files = 0
	_depth_skips = 0
	_issue_count = 0
	_root = root.replace("\\", "/").simplify_path()
	if root.strip_edges().is_empty() or not _root.is_absolute_path() or _root.contains("://") or _root.begins_with("//"):
		_issue("Choose an existing local folder using its absolute path.")
		return result()
	if max_depth < 0 or max_depth > DEFAULT_DEPTH or max_items < 1 or max_items > DEFAULT_ITEMS or max_entries < 1 or max_entries > DEFAULT_ENTRIES:
		_issue("The requested scan limits are outside the supported bounds.")
		return result()
	_max_depth = max_depth
	_max_items = max_items
	_max_entries = max_entries
	if _has_link_component(_root):
		_issue("Choose the actual folder. A linked folder or linked parent is not scanned.")
		return result()
	if not DirAccess.dir_exists_absolute(_root):
		_issue("That folder is missing or cannot be accessed. Choose it again.")
		return result()
	_ok = true
	_complete = true
	done = false
	_pending.append({"relative": "", "depth": 0})
	return _progress([])


func step(budget: int = 64) -> Dictionary:
	var added: Array[Dictionary] = []
	if done:
		return _progress(added)
	# A caller cannot accidentally turn one batch into an unbounded scan.
	for _operation: int in range(clampi(budget, 1, 256)):
		if _current == null:
			if not _open_next():
				if _pending.is_empty():
					done = true
					break
				continue
		if _entries >= _max_entries:
			_stop_at_limit("The %d-entry scan limit was reached. Choose a smaller folder to see the remainder." % _max_entries)
			break
		var name: String = _current.get_next()
		if name.is_empty():
			_close_current()
			continue
		_entries += 1
		if _current.is_link(name):
			_skipped_links += 1
			continue
		var relative: String = name if _relative.is_empty() else _relative.path_join(name)
		var path: String = _root.path_join(relative)
		if _current.current_is_dir():
			if _depth >= _max_depth:
				_depth_skips += 1
				_complete = false
			else:
				_pending.append({"relative": relative, "depth": _depth + 1})
			continue
		var extension: String = name.get_extension().to_lower()
		if not FORMATS.has(extension):
			_other_files += 1
			continue
		if _items.size() >= _max_items:
			_stop_at_limit("The %d-media-item limit was reached. Choose a smaller folder to see the remainder." % _max_items)
			break
		# get_size is a metadata operation; neither files nor codecs are opened.
		var size: int = FileAccess.get_size(path)
		if size < 0:
			_issue("Could not read the size of %s." % relative)
		var format: Array = FORMATS[extension]
		var item: Dictionary = {
			"name": name, "relative_path": relative, "size": size,
			"kind": str(format[0]), "format": str(format[1]), "extension": extension,
			"support": "Metadata only", "classification": "Filename extension; contents not validated"
		}
		_items.append(item)
		added.append(item)
	return _progress(added)


func cancel() -> void:
	if done:
		return
	_cancelled = true
	_complete = false
	done = true
	_close_current()
	_pending.clear()


func result() -> Dictionary:
	var snapshot: Dictionary = _progress(_items.duplicate(true))
	snapshot["issues"] = _issues.duplicate()
	return snapshot


func _progress(items: Array) -> Dictionary:
	var message: String
	if not _ok:
		message = _issues[0] if not _issues.is_empty() else "Choose a folder to inspect."
	elif not done:
		message = "Scanning… %d media files found in %d examined entries." % [_items.size(), _entries]
	elif _cancelled:
		message = "Scan cancelled. Showing %d files found so far; the list is incomplete." % _items.size()
	elif not _complete:
		message = "Partial list: %d media files found. " % _items.size()
		if _depth_skips > 0:
			message += "%d folders were beyond the depth limit of %d. " % [_depth_skips, _max_depth]
		if not _issues.is_empty():
			message += _issues[0]
	else:
		message = "%d media files found. " % _items.size() if not _items.is_empty() else "No listed media file types were found. "
		message += "%d linked entries skipped; %d other files omitted." % [_skipped_links, _other_files]
	return {
		"ok": _ok, "done": done, "complete": done and _complete, "cancelled": _cancelled,
		"root": _root, "items": items, "count": _items.size(), "entries": _entries,
		"directories": _directories, "skipped_links": _skipped_links, "other_files": _other_files,
		"depth_skips": _depth_skips, "issue_count": _issue_count, "message": message
	}


func _open_next() -> bool:
	if _pending.is_empty():
		return false
	var next: Dictionary = _pending.pop_back()
	_relative = next.relative
	_depth = next.depth
	var path: String = _root if _relative.is_empty() else _root.path_join(_relative)
	if _has_link_component(path):
		_skipped_links += 1
		return false
	_current = DirAccess.open(path)
	if _current == null:
		_issue("Could not read folder %s." % ("(selected folder)" if _relative.is_empty() else _relative))
		return false
	_current.include_hidden = true
	_current.include_navigational = false
	if _current.list_dir_begin() != OK:
		_issue("Could not enumerate folder %s." % ("(selected folder)" if _relative.is_empty() else _relative))
		_close_current()
		return false
	_directories += 1
	return true


func _close_current() -> void:
	if _current != null:
		_current.list_dir_end()
		_current = null


func _stop_at_limit(message: String) -> void:
	_issue(message)
	done = true
	_close_current()
	_pending.clear()


func _issue(message: String) -> void:
	_complete = false
	_issue_count += 1
	if _issues.size() < 20:
		_issues.append(message)


static func _has_link_component(path: String) -> bool:
	var prefix: String = "/" if path.begins_with("/") else path.substr(0, 3)
	var directory: DirAccess = DirAccess.open(prefix)
	if directory == null:
		return false
	var current_path: String = prefix
	for component: String in path.trim_prefix(prefix).split("/", false):
		if directory.is_link(component):
			return true
		current_path = current_path.path_join(component)
		directory = DirAccess.open(current_path)
		if directory == null:
			return false
	return false
