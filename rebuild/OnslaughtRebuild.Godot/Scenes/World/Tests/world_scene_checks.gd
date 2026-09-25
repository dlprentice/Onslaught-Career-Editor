# SPDX-License-Identifier: GPL-3.0-or-later
extends SceneTree
## Round-trips the actual private production world without a game host or an
## input owner: import identity and stale-bake refusal, receipt ownership,
## authored content before binding, a lossless geometry/material/texture
## round-trip against a fresh import recipe, explicit binding, the selected
## snapshot poses, retry isolation and unchanged simulation hashes.
## Needs the .NET editor (the simulation bridge) and the prepared scene:
##   godot48-mono --headless --audio-driver Dummy --path <project> --script res://Scenes/World/Tests/world_scene_checks.gd

const Import = preload("res://Scenes/World/level100_scene_import.gd")
const World = preload("res://Scenes/World/level100_world.gd")
const StaticWorld = preload("res://Scenes/World/level100_static_world.gd")
const InteractiveSession = preload("res://Client/interactive_session.gd")
const PlatformInput = preload("res://Client/platform_input_edges.gd")
const SmokeScenario = preload("res://Client/smoke_scenario.gd")
const BRIDGE_SCRIPT_PATH: String = "res://Bridge/SimulationBridge.cs"
const SIMULATION_SEED: int = 0x4F4E534C
const UNPLAYED_TRAILS: Array[String] = ["EntityPresentation/Definitions/PulseBolt/ProjectileTrail",
	"EntityPresentation/Definitions/VulcanBullet/ProjectileTrail"]

var _checks: int = 0
var _failure: String = ""
var _compared_materials: Dictionary = {}
var _compared_textures: Dictionary = {}


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	_check_native_import_identity()
	_check_import_output_ownership()
	if _failure.is_empty():
		_check_world()
	if not _failure.is_empty():
		push_error("WORLD_SCENE_CHECKS failed after %d checks: %s" % [_checks, _failure])
		quit(1)
		return
	print("WORLD_SCENE_CHECKS: %d passed; authored content, geometry round-trip, bindings, selected snapshot poses, retry isolation and unchanged simulation hashes." % _checks)
	quit()


func _check(condition: bool, message: String) -> bool:
	if not _failure.is_empty():
		return false
	if not condition:
		_failure = message
		return false
	_checks += 1
	return true


func _check_world() -> void:
	var manifest: Dictionary = StaticWorld.load_manifest_bytes()
	if not _check(manifest.ok, "The verified static-world manifest is materialized."):
		return
	var bridge: RefCounted = (load(BRIDGE_SCRIPT_PATH) as Script).new()
	var session: RefCounted = InteractiveSession.new(bridge, PlatformInput.new())
	if not _check(session.start(SIMULATION_SEED, manifest.value).ok, "The Level 100 simulation starts."):
		return
	var pointer: int = Input.mouse_mode
	var initial_hash: String = bridge.GetStateHash().value
	var verified: Dictionary = Import.verify_current_import(bridge)
	if not _check(verified.ok, "The prepared private world matches its receipt: " + String(verified.get("error", ""))):
		return
	var production: Node3D = (load(Import.PRODUCTION_SCENE_PATH) as PackedScene).instantiate()
	var presentation: Node = production.get_node("WorldPresentation")
	_check(presentation.get_script().resource_path == "res://Scenes/World/world_presentation.gd",
		"The imported scene contains the actual native world presentation owner.")
	_check(presentation.get("_camera_state") == null and not presentation.is_processing()
		and not presentation.is_processing_input(),
		"Inspecting the authored world does not initialize a camera, clock or input owner.")
	var authored: Array[Node] = _descendants(production)
	_check(authored.size() > 200, "World has an inspectable hierarchy before initialization.")
	var meshes: int = 0
	for node: Node in authored:
		if node is MeshInstance3D and node.mesh != null:
			meshes += 1
	_check(meshes > 70, "Terrain, objects and Aquila already have production geometry.")
	for child: Node in production.get_children():
		if child is Node3D and String(child.name).begins_with("RetailLevel100TargetActor"):
			_check(child.get_node("Geometry").mesh != null, "Packed actor overrides preserve geometry.")
	_check(is_equal_approx((production.get_node("RetailOpeningAndFirstPersonCamera") as Camera3D).far, 700.0),
		"Camera projection is authored in the production scene.")
	for pair: Array in [["PlayerVisual/BodyPivot/RetailAquilaWalker", "walker"], ["PlayerVisual/BodyPivot/RetailAquilaJet", "jet"],
			["RetailOpeningAndFirstPersonCamera/RetailAquilaCockpit", "cockpit"]]:
		var aquila: Node3D = production.get_node(pair[0])
		_check(aquila.get_script().resource_path == "res://Scenes/Aquila/aquila_model.gd",
			"Imported Aquila uses the production native component: " + pair[1])
		_check(aquila.get("profile") == pair[1] and aquila.has_method("configure_prepared"),
			"Imported Aquila keeps its authored profile and native binding entry: " + pair[1])
		_check(aquila.get("_asset") == null, "Aquila inspection does not start its runtime animation owner: " + pair[1])
	var terrain: Mesh = (production.get_node("RetailLevel100HeightField") as MeshInstance3D).mesh
	var count_before: int = authored.size()
	root.add_child(production)
	var recipe: Node3D = World.new()
	root.add_child(recipe)
	var built: Dictionary = recipe.build_imported_scene(bridge)
	if not _check(built.ok, "A fresh import recipe builds: " + String(built.get("error", ""))):
		return
	var inputs: Dictionary = Import.capture_texture_inputs(recipe)
	_check(inputs.ok and inputs.value.size() == 5,
		"The three Aquila profiles share five actual private texture input dependencies.")
	# Check the frozen editor resources before binding refreshes the terrain's
	# runtime texture cache; a runtime refresh would hide a broken saved texture.
	_compare(recipe, production, true, false)
	_compared_materials.clear()
	_compared_textures.clear()
	var initialized: Dictionary = production.initialize(bridge)
	if not _check(initialized.ok, "The production scene binds: " + String(initialized.get("error", ""))):
		return
	_check(production.get_node("WorldPresentation") == presentation and presentation.get("_camera_state") is Object,
		"Explicit binding configures the authored native owner without replacing it.")
	_check(_descendants(production).size() == count_before, "Binding does not build a second world.")
	_check((production.get_node("RetailLevel100HeightField") as MeshInstance3D).mesh == terrain,
		"Runtime LOD updates the same authored terrain resource.")
	_check(bridge.GetStateHash().value == initial_hash, "Scene binding cannot change deterministic state.")
	_compare(recipe, production, true, true)
	for tick: int in [180, 1_000, 1_100]:
		while bridge.GetTick().value < tick:
			session.observe_input(SmokeScenario.input_for_tick(bridge.GetTick().value).value)
			session.advance_frame_ticks(500_000)
		var before: String = bridge.GetStateHash().value
		_check(recipe.render(0.5, 0.05).ok, "The recipe renders the selected snapshot pair.")
		_check(production.render(0.5, 0.05).ok, "The production scene renders the selected snapshot pair.")
		_compare(recipe, production, false, true)
		_check(bridge.GetStateHash().value == before, "Rendering leaves the snapshot hash unchanged.")
	var retry: Node3D = (load(Import.PRODUCTION_SCENE_PATH) as PackedScene).instantiate()
	var live_material: Material = (production.get_node("RetailLevel100HeightField") as MeshInstance3D).material_override
	var retry_material: Material = (retry.get_node("RetailLevel100HeightField") as MeshInstance3D).material_override
	_check(live_material != retry_material, "Retry owns independent animated materials.")
	_check((retry.get_node("RetailLevel100HeightField") as MeshInstance3D).mesh != terrain,
		"Retry owns independent terrain LOD geometry.")
	retry.free()
	_check(Input.mouse_mode == pointer, "Import/binding/render checks never acquire the pointer.")
	_check(Import.verify_current_import(bridge).ok, "The private world still matches its receipt.")
	recipe.queue_free()
	production.queue_free()
	await process_frame


func _check_native_import_identity() -> void:
	# Synthetic files in this invocation's owned profile; the production source
	# and private assets are never edited to exercise stale-import refusal.
	var owner_dir: String = ProjectSettings.globalize_path("user://").path_join("native-import-identity")
	var project: String = owner_dir.path_join("rebuild/Godot")
	var dependencies: String = owner_dir.path_join("tools/godot_compat")
	DirAccess.make_dir_recursive_absolute(dependencies)
	for name: String in ["invariant_int32_format.gd", "arm_cosf.gd"]:
		_write(dependencies.path_join(name), "extends RefCounted\n")
	for relative: String in ["Client", "Core", "Scenes/Shared", "Scenes/World", "Scenes/Aquila", "Assets"]:
		DirAccess.make_dir_recursive_absolute(project.path_join(relative))
	var script: String = project.path_join("Scenes/World/source.gd")
	_write(script, "extends Node\nconst VALUE = 1\n")
	var before: String = _identity(project)
	_write(project.path_join("Assets/generated.tscn"), "private output is not an input")
	_write(project.path_join("Scenes/World/source.gd.uid"), "editor identity only")
	_check(before == _identity(project), "Generated output and UID metadata cannot stale the import.")
	_write(script, "extends Node\nconst VALUE = 2\n")
	var edited: String = _identity(project)
	_check(before != edited, "A native script edit invalidates the private bake without a managed rebuild.")
	var resource: String = project.path_join("Scenes/Shared/recipe.tres")
	_write(resource, "[gd_resource type=\"Resource\" format=3]\n")
	var with_resource: String = _identity(project)
	_check(edited != with_resource, "Adding a native resource invalidates the private bake.")
	DirAccess.rename_absolute(resource, project.path_join("Scenes/Shared/renamed.tres"))
	var renamed: String = _identity(project)
	_check(with_resource != renamed, "Native resource path identity participates in the import.")
	_write(project.path_join("Scenes/World/water.gdshader"), "shader_type spatial;\n")
	var with_shader: String = _identity(project)
	_check(renamed != with_shader, "External native shader source participates in the import.")
	_write(project.path_join("Scenes/World/water.gdshaderinc"), "float wave = 1.0;\n")
	_check(with_shader != _identity(project), "External shader includes participate in the import.")
	var before_aquila: String = _identity(project)
	var aquila: String = project.path_join("Scenes/Aquila/Walker.tscn")
	_write(aquila, "[gd_scene format=3]\n")
	var with_aquila: String = _identity(project)
	_check(before_aquila != with_aquila, "Adding an Aquila template invalidates the private bake.")
	_append(aquila, "[node name=\"Walker\" type=\"Node3D\"]\n")
	_check(with_aquila != _identity(project), "Editing an Aquila template invalidates the private bake.")
	for pair: Array in [["invariant_int32_format.gd", "DotNetInvariantInt32Format.gd"], ["arm_cosf.gd", "ArmCosf.gd"]]:
		var before_dependency: String = _identity(project)
		var external: String = dependencies.path_join(pair[0])
		_append(external, "const VALUE = 2\n")
		var after_dependency: String = _identity(project)
		_check(before_dependency != after_dependency, "Selected external dependency content invalidates the bake: " + pair[0])
		DirAccess.make_dir_recursive_absolute(project.path_join("RuntimeDependencies"))
		var packaged: String = project.path_join("RuntimeDependencies").path_join(pair[1])
		DirAccess.copy_absolute(external, packaged)
		var after_packaging: String = _identity(project)
		_check(after_dependency != after_packaging, "Dependency routing participates even with identical bytes: " + pair[0])
		_append(external, "# inactive source checkout path\n")
		_check(after_packaging == _identity(project), "Only the selected dependency route affects the bake: " + pair[0])
		_append(packaged, "const VALUE_2 = 3\n")
		_check(after_packaging != _identity(project), "Selected packaged dependency content invalidates the bake: " + pair[0])
		DirAccess.remove_absolute(packaged)
		DirAccess.remove_absolute(external)
		_check(not Import.native_source_identity(project).ok, "A missing selected dependency cannot certify the bake: " + pair[0])
		_write(external, "extends RefCounted\n")
	_check_texture_input_receipt(project, owner_dir)


func _check_texture_input_receipt(project: String, owner_dir: String) -> void:
	var resource_path: String = "res://Assets/recipe.texture.aya"
	var path: String = project.path_join("Assets/recipe.texture.aya")
	var bytes := PackedByteArray([1, 2, 3, 4])
	var context := HashingContext.new()
	context.start(HashingContext.HASH_SHA256)
	context.update(bytes)
	var digest: String = context.finish().hex_encode().to_upper()
	var input: Dictionary = {"ResourcePath": resource_path, "Sha256": digest}
	_write_bytes(path, bytes)
	_check(Import.verify_inputs([input], project).ok, "Unchanged recipe input bytes certify the saved world.")
	_write_bytes(path, PackedByteArray([4, 3, 2, 1]))
	_refused([input], project, "Same-size changed recipe bytes invalidate the world before binding.")
	DirAccess.remove_absolute(path)
	_refused([input], project, "A missing recipe input cannot certify the saved world.")
	_write_bytes(path, bytes)
	_refused(null, project, "An old receipt without private input identities requires a rebuild.")
	_refused([], project, "An empty private-input list cannot certify the world.")
	_refused([input, input], project, "Duplicate input entries cannot hide an incomplete receipt.")
	_refused([{"ResourcePath": resource_path, "Sha256": "not a hash"}], project, "Malformed input hashes are refused.")
	for invalid: String in ["res://Assets/../recipe", "res://Assets//recipe", "res://Assets/", "user://recipe", "res://Assets\\recipe"]:
		_refused([{"ResourcePath": invalid, "Sha256": digest}], project, "Input paths must name normalized private assets: " + invalid)
	var target: String = owner_dir.path_join("shared-recipe-input")
	var link: String = project.path_join("Assets/shared.texture.aya")
	_write_bytes(target, bytes)
	if FileAccess.file_exists(link):
		DirAccess.remove_absolute(link)
	var linked: Error = DirAccess.open(project.path_join("Assets")).create_link(target, link)
	if _check(linked == OK, "The synthetic canonical-lab link is created."):
		_check(Import.verify_inputs([{"ResourcePath": "res://Assets/shared.texture.aya", "Sha256": digest}], project).ok
			and FileAccess.get_file_as_bytes(target) == bytes,
			"Canonical-lab input links are read in place without modifying their targets.")


func _refused(inputs: Variant, project: String, message: String) -> void:
	_check(not Import.verify_inputs(inputs, project).ok, message)


func _check_import_output_ownership() -> void:
	var resource_directory: String = Import.DIRECTORY_PATH + "/ownership-check-%x%x" % [randi(), Time.get_ticks_usec()]
	var directory: String = ProjectSettings.globalize_path(resource_directory)
	DirAccess.make_dir_recursive_absolute(directory)
	var files: Array[String] = ["0000_Mesh.res", "0211_ShaderMaterial.res", "AquilaWalker.tscn", "changed.res", "notes.txt"]
	for name: String in files:
		_write(directory.path_join(name), "Keep " + name)
	DirAccess.make_dir_recursive_absolute(directory.path_join("StaticWorld.tscn"))
	var before: Dictionary = {}
	for name: String in files:
		before[name] = FileAccess.get_sha256(directory.path_join(name)).to_upper()
	var owned: Dictionary = {"0000_Mesh.res": before["0000_Mesh.res"], "changed.res": "stale hash"}
	for collision: String in ["0211_ShaderMaterial.res", "AquilaWalker.tscn", "changed.res", "StaticWorld.tscn"]:
		var result: Dictionary = Import.verify_output_ownership(resource_directory, owned, ["0000_Mesh.res", "new.res", collision])
		_check(not result.ok, "Import refuses an unowned, edited or directory destination: " + collision)
		_check(files.all(func(name: String) -> bool: return FileAccess.get_sha256(directory.path_join(name)).to_upper() == before[name]),
			"Preflight refusal leaves every output unchanged.")
		_check(not FileAccess.file_exists(directory.path_join("new.res")), "Preflight does not publish partial output.")
	_check(Import.verify_output_ownership(resource_directory, owned, ["0000_Mesh.res", "new.res"]).ok,
		"Owned and new destinations are admitted.")
	_check(files.all(func(name: String) -> bool: return FileAccess.get_sha256(directory.path_join(name)).to_upper() == before[name]),
		"Unrelated noncolliding private files are preserved.")
	# Only this check's uniquely named fixture directory is disposable.
	for name: String in files:
		DirAccess.remove_absolute(directory.path_join(name))
	DirAccess.remove_absolute(directory.path_join("StaticWorld.tscn"))
	DirAccess.remove_absolute(directory)


func _compare(recipe: Node3D, production: Node3D, compare_geometry: bool, compare_bindings: bool) -> void:
	for expected: Node in _descendants(recipe):
		var path: NodePath = recipe.get_path_to(expected)
		var actual: Node = production.get_node_or_null(path)
		if not _check(actual != null, "Saved scene contains production node %s" % path):
			return
		if expected is Node3D and actual is Node3D:
			_check(expected.transform.is_equal_approx(actual.transform), "Retained presentation transform at %s" % path)
			_check(expected.visible == actual.visible, "Retained visibility at %s" % path)
		if compare_geometry and expected is MeshInstance3D and actual is MeshInstance3D:
			# Projectile trail templates acquire vertices only from real samples.
			if expected.mesh == null and String(path) in UNPLAYED_TRAILS:
				_check(actual.mesh == null, "Unplayed trail template retains its empty history at %s" % path)
				_compare_material(expected.material_override, actual.material_override, path)
				continue
			if not _check(expected.mesh != null and actual.mesh != null, "Mesh retained at %s" % path):
				return
			_check(expected.mesh.get_surface_count() == actual.mesh.get_surface_count(), "Surface count at %s" % path)
			_compare_material(expected.material_override, actual.material_override, path)
			for surface: int in range(expected.mesh.get_surface_count()):
				_compare_material(expected.mesh.surface_get_material(surface), actual.mesh.surface_get_material(surface), path)
				var source: Array = expected.mesh.surface_get_arrays(surface)
				var loaded: Array = actual.mesh.surface_get_arrays(surface)
				_check(source[Mesh.ARRAY_VERTEX] == loaded[Mesh.ARRAY_VERTEX], "Lossless vertex round-trip at %s" % path)
				_check(source[Mesh.ARRAY_INDEX] == loaded[Mesh.ARRAY_INDEX], "Lossless index round-trip at %s" % path)
		if expected is MultiMeshInstance3D and actual is MultiMeshInstance3D:
			var forest: MultiMesh = expected.multimesh
			var other: MultiMesh = actual.multimesh
			_check(forest.instance_count == other.instance_count, "Pine instance count at %s" % path)
			if compare_geometry:
				_check(forest.mesh.get_surface_count() == other.mesh.get_surface_count(), "Pine surface count at %s" % path)
				_compare_material(expected.material_override, actual.material_override, path)
				for surface: int in range(forest.mesh.get_surface_count()):
					_compare_material(forest.mesh.surface_get_material(surface), other.mesh.surface_get_material(surface), path)
			for index: int in range(forest.instance_count):
				_check(forest.get_instance_transform(index).is_equal_approx(other.get_instance_transform(index)),
					"Pine placement at %s" % path)
		if not _failure.is_empty():
			return
	if not compare_bindings:
		return
	var left: Dictionary = recipe.presentation_facts()
	var right: Dictionary = production.presentation_facts()
	_check(left.retail_level100_static_object_surface_count == right.retail_level100_static_object_surface_count,
		"Static hierarchy surface totals agree.")
	_check(left.retail_level100_target_surface_count == right.retail_level100_target_surface_count, "Actor surface totals agree.")
	_check(left.show_hud == right.show_hud and left.opening_pan_active == right.opening_pan_active,
		"Camera state and HUD gate agree.")


func _compare_material(expected: Material, actual: Material, path: NodePath) -> void:
	_check((expected == null) == (actual == null), "Material retained at %s" % path)
	if expected == null or actual == null:
		return
	var key: String = "%d:%d" % [expected.get_instance_id(), actual.get_instance_id()]
	if _compared_materials.has(key):
		return
	_compared_materials[key] = true
	for property: Dictionary in expected.get_property_list():
		if (property.usage & PROPERTY_USAGE_STORAGE) == 0:
			continue
		var texture: Variant = expected.get(property.name)
		if not texture is Texture2D:
			continue
		var loaded: Variant = actual.get(property.name)
		_check(loaded is Texture2D, "Material texture retained at %s:%s" % [path, property.name])
		if not loaded is Texture2D:
			continue
		var pair: String = "%d:%d" % [texture.get_instance_id(), loaded.get_instance_id()]
		if _compared_textures.has(pair):
			continue
		_compared_textures[pair] = true
		var original: Image = texture.get_image()
		var copy: Image = loaded.get_image()
		_check(original != null and copy != null, "Private texture pixels survived serialization.")
		if original != null and copy != null:
			_check(original.get_size() == copy.get_size() and original.get_format() == copy.get_format(),
				"Private texture dimensions/format retained.")
			_check(original.get_data() == copy.get_data(), "Lossless private texture round-trip.")


static func _descendants(node: Node) -> Array[Node]:
	var result: Array[Node] = []
	for child: Node in node.get_children():
		result.append(child)
		result.append_array(_descendants(child))
	return result


static func _identity(project: String) -> String:
	var identity: Dictionary = Import.native_source_identity(project)
	return identity.value if identity.ok else ""


static func _write(path: String, text: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string(text)
	file.close()


static func _append(path: String, text: String) -> void:
	var file := FileAccess.open(path, FileAccess.READ_WRITE)
	file.seek_end()
	file.store_string(text)
	file.close()


static func _write_bytes(path: String, bytes: PackedByteArray) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_buffer(bytes)
	file.close()
