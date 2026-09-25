# SPDX-License-Identifier: MIT
extends Control
## Scene controller. Presentation lives in SaveLab.tscn and the row/theme resources.

const Codec = preload("res://domain/career_save.gd")
const Session = preload("res://domain/save_session.gd")
var _session: SaveSession
var _plan: Dictionary = {}
var _busy := false
var _last_output := ""
@onready var files: CompanionSaveFiles = %SaveFiles

func _ready() -> void:
	get_window().min_size = Vector2i(920, 700)
	get_tree().auto_accept_quit = false
	get_window().close_requested.connect(_close_requested)
	%OpenButton.pressed.connect(func() -> void: %OpenDialog.popup_centered_ratio(0.75))
	%OpenDialog.file_selected.connect(open_career)
	%ChooseOutput.pressed.connect(_choose_output)
	%OutputDialog.file_selected.connect(func(path: String) -> void: %Destination.text = path)
	%CompareButton.pressed.connect(func() -> void: %CompareDialog.popup_centered_ratio(0.75))
	%CompareDialog.file_selected.connect(compare_career)
	%Destination.text_changed.connect(func(_text: String) -> void: _update_actions())
	%WriteCopy.pressed.connect(func() -> void: await write_copy(false))
	%BackupCopy.pressed.connect(func() -> void: await write_copy(true))
	%ReopenCopy.pressed.connect(func() -> void: await open_career(_last_output))
	for row in %Rows.get_children():
		row.selection_changed.connect(_refresh_preview)
	_configure_tree(%Inspector, ["Record", "Stored value", "Interpretation"])
	_configure_tree(%Comparison, ["File offset", "Original byte", "Comparison byte"])
	if not files.is_available():
		_status("Save access is unavailable. Use Godot 4.8 dev6 .NET and build the project, or restore the complete exported app.", true)
	_update_actions()

func _close_requested() -> void:
	if _busy:
		_status("A file operation is still finishing. Wait for its result before closing.")
	else:
		get_tree().quit()

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.ctrl_pressed and event.keycode == KEY_O and not _busy:
		%OpenDialog.popup_centered_ratio(0.75)
		get_viewport().set_input_as_handled()

func _configure_tree(tree: Tree, titles: Array) -> void:
	for column in range(titles.size()):
		tree.set_column_title(column, str(titles[column]))
	tree.set_column_custom_minimum_width(0, 150)

func _status(message: String, failed: bool = false) -> void:
	%Status.text = message
	%Status.modulate = Color(1.0, 0.72, 0.65) if failed else Color.WHITE

func _set_busy(value: bool, message: String = "") -> void:
	_busy = value
	if not message.is_empty():
		_status(message)
	_update_actions()

func _update_actions() -> void:
	var ready := _session != null and not _busy
	%OpenButton.disabled = _busy
	%ChooseOutput.disabled = not ready
	%CompareButton.disabled = not ready
	%Destination.editable = not _busy
	%WriteCopy.disabled = not ready or not _plan.get("ok", false) or %Destination.text.strip_edges().is_empty()
	%BackupCopy.disabled = not ready or %Destination.text.strip_edges().is_empty()
	%ReopenCopy.disabled = _busy or _last_output.is_empty()
	for row in %Rows.get_children():
		row.set_locked(not ready)

func open_career(path: String) -> Dictionary:
	if _busy:
		return {"ok": false, "message": "A file operation is already running."}
	_set_busy(true, "Opening and checking the career…")
	var reply: Dictionary = await files.open_career(path)
	var opened: Dictionary = Session.from_reply(reply)
	if not opened.get("ok", false):
		_set_busy(false)
		_status(str(opened.get("message", "This career could not be opened.")), true)
		return opened
	_session = opened.session
	_plan = {}
	_last_output = ""
	%Destination.text = ""
	%Result.text = "Your original is open. Choose a fresh destination for an edit or an unchanged recovery copy."
	%Comparison.clear()
	%ComparisonSummary.text = "Choose another career to compare with this original."
	var analysis: Dictionary = _session.analysis()
	%SourceDetails.text = "%s\n10,004 bytes  •  Version word 0x%04X  •  %d completed / %d used mission records\nSHA-256  %s\nFile identity  %s" % [_session.path, analysis.version, analysis.completed_nodes, analysis.used_nodes, _session.sha256, _session.identity]
	for row in %Rows.get_children():
		row.set_current(int(analysis.kills[row.category]), int(analysis.packed[row.category]))
	_populate_inspector(analysis)
	_set_busy(false)
	_refresh_preview()
	_status("Career opened and protected snapshot verified. Select edits or make an unchanged recovery copy.")
	return {"ok": true}

func _refresh_preview() -> void:
	if _session == null:
		return
	var selected: Dictionary = {}
	for row in %Rows.get_children():
		if row.selected():
			selected[row.category] = row.target()
	_plan = _session.prepare(selected)
	if not _plan.get("ok", false):
		%Preview.text = str(_plan.get("message", "Choose an edit.")) + "\nAn unchanged recovery copy is available separately."
	else:
		var description: Array[String] = []
		for edit: Dictionary in _plan.selected:
			description.append("%s: %d → %d" % [edit.name, edit.before, edit.after])
		var diffs: Array[String] = []
		for change: Dictionary in _plan.changes:
			diffs.append("0x%04X: %02X → %02X" % [change.offset, change.before, change.after])
		%Preview.text = "%s\n%d changed bytes; length and all unselected bytes preserved.\n%s" % ["   •   ".join(description), _plan.changes.size(), "   ".join(diffs)]
	_update_actions()

func _choose_output() -> void:
	if _session == null or _busy:
		return
	%OutputDialog.current_dir = _session.path.get_base_dir()
	%OutputDialog.current_file = _session.path.get_file().get_basename() + "-copy.bes"
	%OutputDialog.popup_centered_ratio(0.75)

func write_copy(unchanged: bool) -> Dictionary:
	if _busy or _session == null:
		return {"ok": false, "message": "Open a career first."}
	_refresh_preview()
	if not unchanged and not _plan.get("ok", false):
		return _plan
	var destination: String = %Destination.text.strip_edges()
	if destination.is_empty():
		return {"ok": false, "message": "Choose a new destination."}
	var prepared: PackedByteArray = _session.bytes() if unchanged else _plan.bytes.duplicate()
	var changed: int = 0 if unchanged else _plan.changes.size()
	_set_busy(true, "Verifying the original and publishing the separate copy…")
	_last_output = ""
	var reply: Dictionary = await files.publish_copy(_session.path, _session.identity, _session.sha256, destination, prepared)
	reply = _session.verify_publication(reply, prepared)
	if reply.get("ok", false):
		# Read again through the protected interface; no hash-only path reads.
		var reopened: Dictionary = await files.open_career(str(reply.output))
		var result: Dictionary = Session.from_reply(reopened)
		if not result.get("ok", false) or result.session.bytes() != prepared:
			reply = {"ok": false, "may_have_output": true, "output": reply.output,
				"message": "The copy was published but its additional reopen check failed. Inspect it before use."}
		else:
			_last_output = str(reply.output)
			%Result.text = "%s\nReopened and verified: %d changed bytes, 10,004 bytes total. Original identity/content and every unselected byte verified.\nSHA-256  %s" % [_last_output, changed, result.session.sha256]
	_set_busy(false)
	if reply.get("ok", false):
		_status("Unchanged recovery copy reopened and verified." if unchanged else "Edited copy reopened and verified. Your original remains the source.")
	else:
		var failure := str(reply.get("message", "The copy could not be published."))
		if reply.get("may_have_output", false):
			failure += "\nA copy may exist at: " + str(reply.get("output", destination))
		%Result.text = failure
		_status(failure, true)
	await get_tree().process_frame
	get_node("Margin/Layout/Tabs/Save Lab").ensure_control_visible(%Result)
	return reply

func compare_career(path: String) -> Dictionary:
	if _busy or _session == null:
		return {"ok": false, "message": "Open an original first."}
	_set_busy(true, "Opening the comparison career…")
	var reply: Dictionary = await files.open_career(path)
	var opened: Dictionary = Session.from_reply(reply)
	_set_busy(false)
	if not opened.get("ok", false):
		_status(str(opened.get("message", "The comparison could not be opened.")), true)
		return opened
	var other: SaveSession = opened.session
	var comparison: Dictionary = Codec.compare(_session.bytes(), other.bytes())
	%ComparisonSummary.text = "%s\nSHA-256  %s\n%s\nCompared with the original snapshot: %s" % [other.path, other.sha256, "Byte-for-byte identical." if comparison.equal else "%d differing bytes." % comparison.changed_bytes, _session.sha256]
	%Comparison.clear()
	var root: TreeItem = %Comparison.create_item()
	for change: Dictionary in comparison.changes:
		_tree_row(%Comparison, root, "0x%04X" % change.offset, "%02X" % change.before, "%02X" % change.after)
	_status("Comparison complete. Both files were opened read-only.")
	return {"ok": true, "comparison": comparison}

func _tree_row(tree: Tree, parent: TreeItem, title: String, value: String, explanation: String) -> TreeItem:
	var item := tree.create_item(parent)
	item.set_text(0, title)
	item.set_text(1, value)
	item.set_text(2, explanation)
	for column in range(3):
		item.set_tooltip_text(column, item.get_text(column))
	return item

func _populate_inspector(analysis: Dictionary) -> void:
	var tree: Tree = %Inspector
	tree.clear()
	var root := tree.create_item()
	var missions := _tree_row(tree, root, "Mission records", "%d used; %d completed" % [analysis.used_nodes, analysis.completed_nodes], "Unused slots and unknown ranks are retained")
	for record: Dictionary in analysis.nodes:
		if not record.used:
			continue
		_tree_row(tree, missions, "Slot %d · world %d" % [record.index, record.world], "Complete %d · attempts %d" % [record.complete_raw, record.attempts], "%s · raw rank 0x%08X" % [record.rank, record.rank_bits])
	var links := _tree_row(tree, root, "Links", str(analysis.link_census), "Broken and unknown states are not called complete")
	links.collapsed = true
	for record: Dictionary in analysis.links:
		if record.used:
			_tree_row(tree, links, "Slot %d → %d" % [record.index, record.to_node], "0x%08X" % record.state, str(record.label))
	var goodies := _tree_row(tree, root, "Goodies", "300 stored slots", "Slots 233–299 reserved; raw state preserved")
	goodies.collapsed = true
	for record: Dictionary in analysis.goodies:
		_tree_row(tree, goodies, "Slot %d · 0x%04X" % [record.index, record.offset], "0x%08X" % record.state, str(record.label))
	var tech := _tree_row(tree, root, "Tech slots", "32 raw words", "No editable interpretation in this workflow")
	tech.collapsed = true
	for index in range(analysis.tech_slots.size()):
		_tree_row(tree, tech, "Slot %d" % index, "0x%08X" % analysis.tech_slots[index], "Read only")
	_tree_row(tree, root, "Sound / music", "%s / %s" % [analysis.volumes.sound.value, analysis.volumes.music.value], "Stored floats; no runtime range claim")
	_tree_row(tree, root, "Other bytes", "Preserved in full", "Options tail, packed bytes and unknown data are not edited")
