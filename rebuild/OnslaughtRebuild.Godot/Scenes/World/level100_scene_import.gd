# SPDX-License-Identifier: GPL-3.0-or-later
extends Node
## Explicit offline import of the private Level 100 production scene, run by
## the build (ImportLevel100.tscn -- --prepare-level100-scene). Never an editor
## tool and never a game session. Converted resources stay in ignored Assets.
## A receipt pins the code identity, the actor manifest, every written file and
## the texture inputs; gameplay refuses a scene that no longer matches it.

const World = preload("res://Scenes/World/level100_world.gd")
const StaticWorld = preload("res://Scenes/World/level100_static_world.gd")

const DIRECTORY_PATH: String = "res://Assets/Level100/Scenes"
const RECEIPT_PATH: String = DIRECTORY_PATH + "/import.json"
const PRODUCTION_SCENE_PATH: String = DIRECTORY_PATH + "/Level100.tscn"
const BRIDGE_SCRIPT_PATH: String = "res://Bridge/SimulationBridge.cs"
const SIMULATION_SEED: int = 0x4F4E534C
const COMPONENTS: Array = [["PlayerVisual/BodyPivot/RetailAquilaWalker", "AquilaWalker.tscn"],
	["PlayerVisual/BodyPivot/RetailAquilaJet", "AquilaJet.tscn"],
	["RetailOpeningAndFirstPersonCamera/RetailAquilaCockpit", "AquilaCockpit.tscn"],
	["RetailLevel100StaticWorld", "StaticWorld.tscn"]]
## Public production inputs that participate in the private bake; generated
## Assets never do.
const SOURCE_DIRECTORIES: Array[String] = ["Client", "Core", "Scenes/Shared", "Scenes/World", "Scenes/Aquila"]
const SOURCE_EXTENSIONS: Array[String] = ["gd", "gdshader", "gdshaderinc", "tscn", "tres"]
## Original adapters stay in the GPL tree and separately licensed numerical
## implementations outside it; their selected source participates too.
const COMPAT_SOURCES: Array = [["../../tools/godot_compat/invariant_int32_format.gd", "RuntimeDependencies/DotNetInvariantInt32Format.gd"],
	["../../tools/godot_compat/arm_cosf.gd", "RuntimeDependencies/ArmCosf.gd"]]

var _saved_resources: Dictionary = {}
var _planned_resources: Array = []
var _written_files: Array[String] = []
var _previous_files: Dictionary = {}


func _ready() -> void:
	if Engine.is_editor_hint():
		return
	if not OS.get_cmdline_user_args().has("--prepare-level100-scene"):
		print("Use npm run build:rebuild-godot to prepare the private Level 100 production scene.")
		get_tree().quit()
		return
	var result: Dictionary = _prepare()
	if not result.ok:
		push_error("Level 100 scene import failed: %s: %s" % [result.get("error_type", "Error"), result.get("error", "")])
		get_tree().quit(1)
		return
	print(result.message)
	get_tree().quit()


func _prepare() -> Dictionary:
	if not OS.get_environment("ONSLAUGHT_TERRAIN_PROBE").strip_edges().is_empty():
		return _failure("InvalidOperationException", "A diagnostic terrain probe cannot be baked into faithful production assets.")
	var local: Dictionary = require_local_output(DIRECTORY_PATH)
	if not local.ok:
		return local
	var bridge: RefCounted = (load(BRIDGE_SCRIPT_PATH) as Script).new()
	var identity: Dictionary = current_code_identity(bridge)
	if not identity.ok:
		return identity
	var receipt: Dictionary = try_read_receipt()
	if not receipt.ok:
		return receipt
	if receipt.value != null:
		var files: Dictionary = verify_files(receipt.value)
		if not files.ok:
			return files
		if receipt.value.CodeIdentity == identity.value.code and receipt.value.ActorManifest == identity.value.actor_manifest:
			var inputs: Dictionary = verify_inputs(receipt.value.get("Inputs"))
			if not inputs.ok:
				return inputs
			return {"ok": true, "message": "Level 100 production scenes are current."}
	else:
		var directory: String = ProjectSettings.globalize_path(DIRECTORY_PATH)
		if DirAccess.dir_exists_absolute(directory) and not (DirAccess.get_files_at(directory).is_empty()
				and DirAccess.get_directories_at(directory).is_empty()):
			return _invalid("Scene output exists without an import receipt. Preserve it separately before importing.")
	var imported: Dictionary = _import(receipt.value, bridge, identity.value)
	if not imported.ok:
		return imported
	var verified: Dictionary = verify_current_import(bridge)
	if not verified.ok:
		return verified
	return {"ok": true, "message": "Level 100 production scenes imported and verified: " + PRODUCTION_SCENE_PATH}


## The receipt, file and input checks gameplay runs before instantiating the
## private scene.
static func verify_current_import(bridge: RefCounted) -> Dictionary:
	var receipt: Dictionary = try_read_receipt()
	if not receipt.ok:
		return receipt
	if receipt.value == null:
		return _invalid("Level 100 production scene is missing. Run npm run build:rebuild-godot.")
	var identity: Dictionary = current_code_identity(bridge)
	if not identity.ok:
		return identity
	if receipt.value.CodeIdentity != identity.value.code or receipt.value.ActorManifest != identity.value.actor_manifest:
		return _invalid("Level 100 production scenes are stale. Run npm run build:rebuild-godot.")
	var files: Dictionary = verify_files(receipt.value)
	if not files.ok:
		return files
	return verify_inputs(receipt.value.get("Inputs"))


## SHA-256 over the managed build identities the bake reads through the bridge
## (Core, Client, Godot bridge) and every public native production input.
static func current_code_identity(bridge: RefCounted) -> Dictionary:
	var config: Dictionary = bridge.WorldConfigFacts()
	if not config.ok:
		return config
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(String(config.value.assembly_identity).hex_decode())
	var native: Dictionary = native_source_identity(ProjectSettings.globalize_path("res://"))
	if not native.ok:
		return native
	context.update(native.value.hex_decode())
	return {"ok": true, "value": {"code": context.finish().hex_encode().to_upper(),
		"actor_manifest": config.value.actor_manifest_sha256}}


static func native_source_identity(project_directory: String) -> Dictionary:
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	var relatives: Array[String] = []
	for directory: String in SOURCE_DIRECTORIES:
		_collect_sources(project_directory, directory, relatives)
	relatives.sort_custom(func(left: String, right: String) -> bool: return _ordinal_less(left, right))
	for relative: String in relatives:
		context.update(_terminated(relative))
		context.update(_sha256_bytes(project_directory.path_join(relative)))
	for pair: Array in COMPAT_SOURCES:
		var relative: String = pair[1] if FileAccess.file_exists(project_directory.path_join(pair[1])) else pair[0]
		var path: String = project_directory.path_join(relative).simplify_path()
		if not FileAccess.file_exists(path):
			return _invalid("A selected numerical adapter source is missing: " + relative)
		context.update(_terminated(relative))
		context.update(_sha256_bytes(path))
	return {"ok": true, "value": context.finish().hex_encode().to_upper()}


static func _collect_sources(project_directory: String, relative_directory: String, into: Array[String]) -> void:
	var absolute: String = project_directory.path_join(relative_directory)
	for file: String in DirAccess.get_files_at(absolute):
		if file.get_extension() in SOURCE_EXTENSIONS:
			into.append(relative_directory + "/" + file)
	for child: String in DirAccess.get_directories_at(absolute):
		_collect_sources(project_directory, relative_directory + "/" + child, into)


## .NET StringComparer.Ordinal over UTF-16 units; these paths are ASCII.
static func _ordinal_less(left: String, right: String) -> bool:
	var count: int = mini(left.length(), right.length())
	for index: int in range(count):
		var a: int = left.unicode_at(index)
		var b: int = right.unicode_at(index)
		if a != b:
			return a < b
	return left.length() < right.length()


static func try_read_receipt() -> Dictionary:
	var local: Dictionary = require_local_output(RECEIPT_PATH)
	if not local.ok:
		return local
	var path: String = ProjectSettings.globalize_path(RECEIPT_PATH)
	if not FileAccess.file_exists(path):
		return {"ok": true, "value": null}
	var json := JSON.new()
	if json.parse(FileAccess.get_file_as_string(path)) != OK or not json.data is Dictionary \
			or not json.data.get("Files") is Array or typeof(json.data.get("CodeIdentity")) != TYPE_STRING \
			or typeof(json.data.get("ActorManifest")) != TYPE_STRING:
		return _invalid("Invalid Level 100 import receipt.")
	return {"ok": true, "value": json.data}


static func verify_files(receipt: Dictionary) -> Dictionary:
	var files: Array = receipt.Files
	var has_scene: bool = files.any(func(file: Variant) -> bool: return file is Dictionary and file.get("Name") == "Level100.tscn")
	if files.is_empty() or not has_scene:
		return _invalid("Incomplete Level 100 import receipt.")
	for file: Variant in files:
		if not file is Dictionary or typeof(file.get("Name")) != TYPE_STRING or typeof(file.get("Sha256")) != TYPE_STRING \
				or String(file.Name).get_file() != file.Name or String(file.Name).is_empty():
			return _invalid("Invalid imported resource name.")
		var resource_path: String = DIRECTORY_PATH + "/" + file.Name
		var local: Dictionary = require_local_output(resource_path)
		if not local.ok:
			return local
		var path: String = ProjectSettings.globalize_path(resource_path)
		if not FileAccess.file_exists(path) or _hash(path) != file.Sha256:
			return _invalid("Imported faithful resource changed: %s. Preserve deliberate edits separately; the faithful runtime does not silently adopt overrides." % file.Name)
	return {"ok": true}


## The texture recipes stay external when their materials are saved, so their
## private source bytes are dependencies of the packed world.
static func verify_inputs(inputs: Variant, project_directory: String = "") -> Dictionary:
	if not inputs is Array or inputs.is_empty():
		return _invalid("Incomplete Level 100 texture input receipt. Rebuild the private production scene.")
	var seen: Dictionary = {}
	for input: Variant in inputs:
		if not input is Dictionary or typeof(input.get("ResourcePath")) != TYPE_STRING or typeof(input.get("Sha256")) != TYPE_STRING:
			return _invalid("Incomplete Level 100 texture input receipt. Rebuild the private production scene.")
		seen[input.ResourcePath] = true
	if seen.size() != inputs.size():
		return _invalid("Incomplete Level 100 texture input receipt. Rebuild the private production scene.")
	for input: Dictionary in inputs:
		var path: Dictionary = _input_path(input.ResourcePath, project_directory)
		if not path.ok:
			return path
		var digest: String = input.Sha256
		if digest.length() != 64 or not digest.is_valid_hex_number() or not FileAccess.file_exists(path.value) \
				or _hash(path.value) != digest.to_upper():
			return _invalid("Imported faithful texture input is missing or changed: %s. Restore the admitted materialization before running the private scene." % input.ResourcePath)
	return {"ok": true}


## Materialized inputs may use the documented canonical-lab links and are read
## in place; the no-link rule applies only to generated outputs.
static func _input_path(resource_path: String, project_directory: String = "") -> Dictionary:
	if not resource_path.begins_with("res://Assets/") or resource_path.contains("\\"):
		return _invalid("Invalid Level 100 texture input path.")
	for segment: String in resource_path.substr(6).split("/"):
		if segment in ["", ".", ".."]:
			return _invalid("Invalid Level 100 texture input path.")
	var project: String = ProjectSettings.globalize_path("res://") if project_directory.is_empty() else project_directory
	return {"ok": true, "value": project.path_join(resource_path.substr(6))}


## Generated outputs must stay inside the project and never follow a link.
static func require_local_output(resource_path: String) -> Dictionary:
	var project: String = ProjectSettings.globalize_path("res://").trim_suffix("/")
	var path: String = ProjectSettings.globalize_path(resource_path).trim_suffix("/")
	while not path.is_empty() and path != project and path != "/":
		var parent: String = path.get_base_dir()
		var dir := DirAccess.open(parent)
		if dir != null and dir.is_link(path.get_file()):
			return _invalid("Generated scene output must not follow a file or directory link: " + path)
		path = parent
	if path != project:
		return _invalid("Scene output escaped the project.")
	return {"ok": true}


func _import(previous: Variant, bridge: RefCounted, identity: Dictionary) -> Dictionary:
	_previous_files = {}
	for file: Dictionary in ([] if previous == null else previous.Files):
		_previous_files[file.Name] = file.Sha256
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(DIRECTORY_PATH))
	var manifest: Dictionary = StaticWorld.load_manifest_bytes()
	if not manifest.ok:
		return manifest
	var started: Dictionary = bridge.Start(SIMULATION_SEED, manifest.value)
	if not started.ok:
		return started
	var world: Node3D = World.new()
	add_child(world)
	var built: Dictionary = world.build_imported_scene(bridge)
	if not built.ok:
		world.free()
		return built
	world.add_imported_actor_resources()
	var inputs: Dictionary = capture_texture_inputs(world)
	if not inputs.ok:
		world.free()
		return inputs
	world.set_meta("source", "Faithful imported Level 100; generated by the production import recipe")
	world.set_meta("simulation_owner", "C# Core; scene transforms never become simulation inputs")
	world.set_meta("actor_manifest_sha256", identity.actor_manifest)
	(world.get_node("RetailLevel100HeightField") as MeshInstance3D).mesh.resource_local_to_scene = true
	_plan_node_resources(world)
	# A valid older receipt owns only its listed files. Check the complete new
	# destination set before replacing even the first owned output.
	var names: Array[String] = []
	for planned: Array in _planned_resources:
		names.append(planned[1])
	for component: Array in COMPONENTS:
		names.append(component[1])
	names.append("Level100.tscn")
	var owned: Dictionary = verify_output_ownership(DIRECTORY_PATH, _previous_files, names)
	if not owned.ok:
		world.free()
		return owned
	for planned: Array in _planned_resources:
		var resource: Resource = planned[0]
		var name: String = planned[1]
		if resource is Material:
			resource.resource_local_to_scene = true
		owned = verify_output_ownership(DIRECTORY_PATH, _previous_files, [name])
		if not owned.ok:
			world.free()
			return owned
		var saved: Error = ResourceSaver.save(resource, DIRECTORY_PATH + "/" + name,
			ResourceSaver.FLAG_COMPRESS | ResourceSaver.FLAG_CHANGE_PATH)
		if saved != OK:
			world.free()
			return _failure("IOException", "Could not save %s: %s" % [name, error_string(saved)])
		# Preserve child-before-parent order and external references.
		resource.take_over_path(DIRECTORY_PATH + "/" + name)
		_written_files.append(name)
	# Gameplay loads these packed components through Level100.tscn; the editor
	# can open each on its own without any runtime bootstrap.
	for component: Array in COMPONENTS:
		var replaced: Dictionary = _replace_with_component(world.get_node(component[0]), component[1])
		if not replaced.ok:
			world.free()
			return replaced
	_own_children(world, world)
	var scene: Dictionary = _save_scene(world, "Level100.tscn")
	if not scene.ok:
		world.free()
		return scene
	var written: Array[String] = []
	for name: String in _written_files:
		if not written.has(name):
			written.append(name)
	written.sort_custom(func(left: String, right: String) -> bool: return _ordinal_less(left, right))
	var files: Array = []
	for name: String in written:
		files.append({"Name": name, "Sha256": _hash(ProjectSettings.globalize_path(DIRECTORY_PATH + "/" + name))})
	var receipt: Dictionary = {"CodeIdentity": identity.code, "ActorManifest": identity.actor_manifest, "Files": files,
		"Inputs": inputs.value}
	var file := FileAccess.open(ProjectSettings.globalize_path(RECEIPT_PATH), FileAccess.WRITE)
	if file == null:
		world.free()
		return _failure("IOException", "Could not write the Level 100 import receipt.")
	file.store_string(JSON.stringify(receipt, "  ", false) + "\n")
	file.close()
	# Retire only this importer's obsolete, unchanged generated files. An
	# editor modification or an unrelated file is never a cleanup target.
	for old_name: String in _previous_files:
		if _written_files.has(old_name):
			continue
		var resource_path: String = DIRECTORY_PATH + "/" + old_name
		var local: Dictionary = require_local_output(resource_path)
		if not local.ok:
			world.free()
			return local
		var path: String = ProjectSettings.globalize_path(resource_path)
		if FileAccess.file_exists(path) and _hash(path) == _previous_files[old_name]:
			DirAccess.remove_absolute(path)
	world.free()
	return {"ok": true}


static func capture_texture_inputs(world: Node) -> Dictionary:
	var paths: Dictionary = {}
	for component: String in ["PlayerVisual/BodyPivot/RetailAquilaWalker", "PlayerVisual/BodyPivot/RetailAquilaJet",
			"RetailOpeningAndFirstPersonCamera/RetailAquilaCockpit"]:
		var bindings: Dictionary = world.get_node(component).texture_bindings()
		for texture: Variant in bindings.values():
			paths[String(texture.get("source_path"))] = true
	var ordered: Array[String] = []
	for path: String in paths:
		ordered.append(path)
	ordered.sort_custom(func(left: String, right: String) -> bool: return _ordinal_less(left, right))
	var inputs: Array = []
	for resource_path: String in ordered:
		var path: Dictionary = _input_path(resource_path)
		if not path.ok:
			return path
		inputs.append({"ResourcePath": resource_path, "Sha256": _hash(path.value)})
	return {"ok": true, "value": inputs}


static func verify_output_ownership(directory_path: String, previous_files: Dictionary, names: Array) -> Dictionary:
	for name: String in names:
		var resource_path: String = directory_path + "/" + name
		var local: Dictionary = require_local_output(resource_path)
		if not local.ok:
			return local
		var path: String = ProjectSettings.globalize_path(resource_path)
		if DirAccess.dir_exists_absolute(path) or (FileAccess.file_exists(path)
				and (not previous_files.has(name) or _hash(path) != previous_files[name])):
			return _invalid("Scene import would replace an unowned or changed output: %s. Preserve it separately before importing." % name)
	return {"ok": true}


func _replace_with_component(node: Node3D, name: String) -> Dictionary:
	var parent: Node = node.get_parent()
	var index: int = node.get_index()
	_own_children(node, node)
	var saved: Dictionary = _save_scene(node, name)
	if not saved.ok:
		return saved
	var component: PackedScene = ResourceLoader.load(DIRECTORY_PATH + "/" + name, "", ResourceLoader.CACHE_MODE_IGNORE)
	var instance: Node3D = component.instantiate()
	parent.remove_child(node)
	parent.add_child(instance)
	parent.move_child(instance, index)
	node.free()
	return {"ok": true}


## Keep nested production instances rather than flattened duplicate trees.
static func _own_children(node: Node, owner_node: Node) -> void:
	for child: Node in node.get_children():
		child.owner = owner_node
		if child.scene_file_path.is_empty():
			_own_children(child, owner_node)


func _save_scene(root: Node, name: String) -> Dictionary:
	var scene := PackedScene.new()
	var packed: Error = scene.pack(root)
	if packed != OK:
		return _failure("IOException", "Could not pack %s: %s" % [name, error_string(packed)])
	var owned: Dictionary = verify_output_ownership(DIRECTORY_PATH, _previous_files, [name])
	if not owned.ok:
		return owned
	var saved: Error = ResourceSaver.save(scene, DIRECTORY_PATH + "/" + name)
	if saved != OK:
		return _failure("IOException", "Could not save %s: %s" % [name, error_string(saved)])
	_written_files.append(name)
	return {"ok": true}


func _plan_node_resources(node: Node) -> void:
	for property: Dictionary in node.get_property_list():
		if (property.usage & PROPERTY_USAGE_STORAGE) != 0:
			_plan_variant(node.get(property.name))
	for child: Node in node.get_children():
		_plan_node_resources(child)


func _plan_variant(value: Variant) -> void:
	if value is Resource:
		var resource: Resource = value
		# ImageTexture owns its Image payload; externalizing that property makes
		# a broken external index in 4.8 dev6's binary saver, so pixels stay
		# embedded in their private Texture2D resource.
		if resource is Image:
			return
		var id: int = resource.get_instance_id()
		if _saved_resources.has(id):
			return
		_saved_resources[id] = true
		if not resource.resource_path.is_empty() and not resource.resource_path.contains("::"):
			return
		for property: Dictionary in resource.get_property_list():
			if (property.usage & PROPERTY_USAGE_STORAGE) != 0:
				_plan_variant(resource.get(property.name))
		_planned_resources.append([resource, "%04d_%s.res" % [_planned_resources.size(), resource.get_class()]])
	elif value is Array:
		for item: Variant in value:
			_plan_variant(item)
	elif value is Dictionary:
		for item: Variant in value.values():
			_plan_variant(item)


## The UTF-8 path followed by one zero byte (a Godot String cannot hold NUL).
static func _terminated(relative: String) -> PackedByteArray:
	var bytes: PackedByteArray = relative.to_utf8_buffer()
	bytes.append(0)
	return bytes


static func _hash(path: String) -> String:
	return FileAccess.get_sha256(path).to_upper()


static func _sha256_bytes(path: String) -> PackedByteArray:
	return FileAccess.get_sha256(path).hex_decode()


static func _failure(kind: String, message: String) -> Dictionary:
	return {"ok": false, "error_type": kind, "error": message}


static func _invalid(message: String) -> Dictionary:
	return _failure("InvalidDataException", message)
