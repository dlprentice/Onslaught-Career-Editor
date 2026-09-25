# SPDX-License-Identifier: MIT
extends VBoxContainer
## The editable scene owns every control; this script only manages scan progress.

const Catalog = preload("res://domain/media_catalog.gd")
var _catalog: CompanionMediaCatalog
var _busy: bool = false
var _folder: String = ""
var _tree_root: TreeItem


func _ready() -> void:
	%ChooseFolder.pressed.connect(func() -> void: %FolderDialog.popup_centered_ratio(0.75))
	%FolderDialog.dir_selected.connect(browse_folder)
	%Rescan.pressed.connect(func() -> void: await browse_folder(_folder))
	%CancelScan.pressed.connect(_cancel_scan)
	%MediaFiles.item_selected.connect(_show_selection)
	var titles: PackedStringArray = ["Filename", "Kind", "Format", "Bytes", "Relative path"]
	for index: int in range(titles.size()):
		%MediaFiles.set_column_title(index, titles[index])
	%MediaFiles.set_column_custom_minimum_width(0, 190)
	%MediaFiles.set_column_custom_minimum_width(1, 120)
	%MediaFiles.set_column_custom_minimum_width(2, 95)
	%MediaFiles.set_column_custom_minimum_width(3, 90)
	%MediaFiles.set_column_custom_minimum_width(4, 220)
	%MediaFiles.set_column_expand(3, false)
	_update_actions()


func browse_folder(path: String) -> Dictionary:
	if _busy:
		return {"ok": false, "message": "A media scan is already running."}
	_busy = true
	_catalog = Catalog.new()
	%MediaFiles.clear()
	_tree_root = %MediaFiles.create_item()
	%FileDetails.text = "Select a file to inspect its metadata. Files are identified by extension; contents are not decoded or validated."
	var progress: Dictionary = _catalog.begin(path)
	_folder = str(progress.root)
	%FolderPath.text = _folder
	_update_actions()
	%ScanSummary.text = str(progress.message)
	while not _catalog.done:
		progress = _catalog.step(64)
		for entry: Dictionary in progress.items:
			_append_row(entry)
		%ScanSummary.text = str(progress.message)
		await get_tree().process_frame
		if not is_inside_tree():
			_catalog.cancel()
			return _catalog.result()
	var final: Dictionary = _catalog.result()
	%ScanSummary.text = str(final.message)
	if final.issue_count > 0:
		%FileDetails.text = "Some entries could not be listed:\n" + "\n".join(final.issues)
	_busy = false
	_update_actions()
	return final


func _append_row(entry: Dictionary) -> void:
	var row: TreeItem = %MediaFiles.create_item(_tree_root)
	row.set_text(0, str(entry.name))
	row.set_text(1, str(entry.kind))
	row.set_text(2, str(entry.format))
	row.set_text(3, str(entry.size) if entry.size >= 0 else "Unknown")
	row.set_text(4, str(entry.relative_path))
	row.set_metadata(0, entry)
	row.set_tooltip_text(0, str(entry.relative_path))
	row.set_tooltip_text(2, "Filename extension only; contents have not been validated.")


func _show_selection() -> void:
	var selected: TreeItem = %MediaFiles.get_selected()
	if selected == null:
		return
	var entry: Dictionary = selected.get_metadata(0)
	var size_text: String = "%d bytes" % entry.size if entry.size >= 0 else "Size unavailable"
	%FileDetails.text = "%s\n%s  •  %s  •  %s\n%s\nMetadata only. The extension names a possible format; no playback or content validation is implied." % [entry.name, entry.kind, entry.format, size_text, entry.relative_path]


func _cancel_scan() -> void:
	if _catalog != null:
		_catalog.cancel()
	%CancelScan.disabled = true


func _update_actions() -> void:
	%ChooseFolder.disabled = _busy
	%Rescan.disabled = _busy or _folder.is_empty()
	%CancelScan.disabled = not _busy


func _exit_tree() -> void:
	if _catalog != null:
		_catalog.cancel()
