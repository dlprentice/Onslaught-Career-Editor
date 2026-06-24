//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyParticleManagerWave463 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
        int renamed = 0;
        int wouldRename = 0;
        int missing = 0;
        int bad = 0;
    }

    private boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "particle-manager-wave463",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            String expectedSignature = expectedSignature(spec);
            if (!actualSignature.equals(expectedSignature)) {
                throw new IllegalStateException(
                    "Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature
                );
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> actualTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
                }
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getName() + " -> " + actualSignature);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004cae50",
                "CParticle__Destroy",
                "__fastcall",
                voidType,
                "Wave463 correction: Destroys/recycles one particle node, freeing the observed +0x88 resource block after the optional particle-set vfunc +0x38 guard and unlinking from the active list or owner handle at +0x58. Static retail-binary evidence only; runtime particle behavior, exact layout, source identity, and rebuild parity remain unproven.",
                tags("particle-node", "resource-free", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("particle", voidPtr)
                }
            ),
            new Spec(
                "0x004caed0",
                "CParticleManager__SetParticleResource",
                "__thiscall",
                boolType,
                "Wave463 correction: Replaces the particle +0x88 resource block with an OID__AllocObject allocation of resource_size bytes after freeing any existing block through the same vfunc +0x38 guard used by CParticle__Destroy. Static retail-binary evidence only; exact owner/layout/source identity and runtime behavior remain unproven.",
                tags("particle-resource", "allocation", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("resource_size", intType)
                }
            ),
            new Spec(
                "0x004caf60",
                "CParticleManager__CleanupHandles",
                "__cdecl",
                voidType,
                "Wave463 correction: Walks the global effect-handle chain at DAT_0082b3e4, advances handle state +0xb4 from 1->2 or 2->3, and frees handles whose activity flag +0xa4 is clear. Static retail-binary evidence only; runtime particle behavior, exact handle layout, source identity, and rebuild parity remain unproven.",
                tags("effect-handle", "cleanup", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {}
            ),
            new Spec(
                "0x004cb0e0",
                "CParticleManager__Init",
                "__fastcall",
                voidPtr,
                "Wave463 correction: Initializes one particle manager by allocating a 0x200-entry particle pool, constructing 0xd8-byte particle nodes, linking the free list through +0x68, inserting the manager into DAT_009c63f4, and incrementing DAT_0082b3ec. Static retail-binary evidence only; runtime pool behavior, exact layout, source identity, and rebuild parity remain unproven.",
                tags("particle-pool", "manager-init", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("manager", voidPtr)
                }
            ),
            new Spec(
                "0x004cb1b0",
                "CParticleManager__Shutdown",
                "__fastcall",
                voidType,
                "Wave463 correction: Shuts down one particle manager by destroying the 0xd8-byte particle array with callback cleanup, freeing the backing allocation, recursively releasing the next manager pointer, and decrementing DAT_0082b3ec. Static retail-binary evidence only; destructor completeness, exact layout, source identity, and runtime behavior remain unproven.",
                tags("particle-pool", "manager-shutdown", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("manager", voidPtr)
                }
            ),
            new Spec(
                "0x004cb210",
                "CParticleManager__Update",
                "__thiscall",
                intType,
                "Wave463 correction: Per-frame manager update clamps/stores delta time, clears handle activity/backlinks, updates active particles, dispatches render-node callbacks, prunes dead particles, clears stale manager owner links, and calls CParticleManager__CleanupHandles. Static retail-binary evidence only; runtime particle behavior, exact layout, source identity, and rebuild parity remain unproven.",
                tags("manager-update", "particle-update", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delta_time", floatType),
                    param("update_context", intType)
                }
            ),
            new Spec(
                "0x004cb300",
                "CParticleManager__InterpolatePositions",
                "__cdecl",
                voidType,
                "Wave463 correction: Interpolates global effect-handle positions by walking DAT_0082b3e8, copying position directly for the 10000.0 sentinel case or blending current/previous coordinates by DAT_008a9e44. Static retail-binary evidence only; render interpolation behavior, exact handle layout, source identity, and rebuild parity remain unproven.",
                tags("effect-handle", "interpolation", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {}
            ),
            new Spec(
                "0x004cb3d0",
                "CParticleManager__CreateEffect",
                "__stdcall",
                voidType,
                "Wave463 correction: Creates a particle effect unless particles are globally disabled, allocating a particle, writing spawn vector fields at +0x38..+0x44, optionally allocating a 0xb8 effect handle, linking DAT_0082b3e4, and storing looping/high-priority handle flags. Static retail-binary evidence only; exact parameter contract, runtime effect behavior, source identity, and rebuild parity remain unproven.",
                tags("effect-create", "effect-handle", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("manager", voidPtr),
                    param("out_handle_slot", voidPtr),
                    param("spawn_x", floatType),
                    param("spawn_y", floatType),
                    param("spawn_z", floatType),
                    param("spawn_w", floatType),
                    param("looping_flag", intType),
                    param("force_allocate", intType)
                }
            ),
            new Spec(
                "0x004cb5c0",
                "CParticleManager__AllocateParticle",
                "__thiscall",
                voidPtr,
                "Wave463 correction: Allocates or recycles a particle node from the manager free list, creates another manager pool when capacity allows, applies effect-type LOD skip thresholds, initializes node transform/state fields, links the particle set, and dispatches the particle-set vfunc +0x24 initializer. Static retail-binary evidence only; runtime LOD behavior, exact layout, source identity, and rebuild parity remain unproven.",
                tags("particle-pool", "lod-threshold", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("particle_set", voidPtr),
                    param("force_allocate", intType)
                }
            ),
            new Spec(
                "0x004cb920",
                "CParticleManager__UpdateParticleAndRecycleIfDead",
                "__thiscall",
                voidType,
                "Wave463 correction: Updates one particle's lifetime and position, refreshes attached handle activity/backlink fields, applies the observed death-flag logic, dispatches particle-set vfunc +0x28, and recycles dead particles to the manager free list. Static retail-binary evidence only; runtime particle behavior, exact layout, source identity, and rebuild parity remain unproven.",
                tags("particle-update", "particle-recycle", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("particle", voidPtr),
                    param("unused_context", intType)
                }
            ),
            new Spec(
                "0x004cba30",
                "CParticleManager__ProjectPointToTerrainWithRadiusClamp",
                "__stdcall",
                intType,
                "Wave463 correction: Samples static-shadow terrain height for a vec4-like point and, when sampled height is below point.z + radius, copies the point to out_pos and clamps out_pos.z to height - radius. Static retail-binary evidence only; runtime terrain interaction, exact vector layout, source identity, and rebuild parity remain unproven.",
                tags("terrain-projection", "shadow-height", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("world_pos", voidPtr),
                    param("radius", floatType),
                    param("out_pos", voidPtr)
                }
            ),
            new Spec(
                "0x004cba90",
                "CParticleManager__ComputeMinCameraDistanceSqForParticle",
                "__stdcall",
                doubleType,
                "Wave463 correction: Computes camera-distance-squared for one particle, using camera 0/1 in multiplayer with a large fallback and the active single-player camera otherwise, with attached-handle offset added when +0x58 is present. Static retail-binary evidence only; runtime camera behavior, exact particle layout, source identity, and rebuild parity remain unproven.",
                tags("camera-distance", "particle-lod", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("particle", voidPtr)
                }
            ),
            new Spec(
                "0x004cbca0",
                "CParticleManager__UpdateParticles",
                "__cdecl",
                voidType,
                "Wave463 correction: Walks an active particle list, refreshes attached handle state/backlinks, dispatches handle-state vfunc +0x54 for state 2, decrements lifetime, integrates position by global delta time, and optionally sets death flags under DAT_009c63fc. Static retail-binary evidence only; runtime particle behavior, exact layout, source identity, and rebuild parity remain unproven.",
                tags("particle-update", "active-list", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("active_head", voidPtr)
                }
            ),
            new Spec(
                "0x004cbe30",
                "CParticleManager__PruneDeadParticles",
                "__fastcall",
                intType,
                "Wave463 correction: Walks the manager active list, recounts live particles at manager +0x1c, unlinks death-flagged particles, calls CParticle__Destroy, recycles nodes to the free list at manager +0x8, and returns whether any live particle was observed. Static retail-binary evidence only; runtime particle behavior, exact layout, source identity, and rebuild parity remain unproven.",
                tags("particle-prune", "particle-recycle", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("manager", voidPtr)
                }
            ),
            new Spec(
                "0x004cbff0",
                "CParticleManager__DestroyParticleList",
                "__fastcall",
                voidType,
                "Wave463 correction: Destroys every node in a head-linked particle list by repeatedly reading the current head, preserving the next pointer, and dispatching the node vfunc slot 0 with delete flag 1. Static retail-binary evidence only; runtime destructor behavior, exact node layout, source identity, and rebuild parity remain unproven.",
                tags("particle-list", "destructor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("list_head_ptr", voidPtr)
                }
            ),
            new Spec(
                "0x004cc020",
                "CParticleSet__CreateByType",
                "__thiscall",
                voidPtr,
                "Wave463 correction: Creates/inserts a particle-set record by sorted name lookup and type id, allocates type-specific object sizes, calls CParticleSet__Init, installs the observed particle-set vtables, seeds type-default fields, copies the name, and updates DAT_0082b450. Static retail-binary evidence only; exact type names, source identity, runtime particle behavior, and rebuild parity remain unproven.",
                tags("particle-set", "factory", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("set_name", charPtr),
                    param("type_id", intType),
                    param("context", voidPtr)
                }
            ),
            new Spec(
                "0x004cc850",
                "CParticleSet__Init",
                "__fastcall",
                voidType,
                "Wave463 correction: Base particle-set initializer clears observed state fields at +0x3c/+0x40/+0x48/+0x50/+0x54 and installs the base particle-set vtable pointer. Static retail-binary evidence only; exact class layout, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("particle-set", "initializer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("particle_set", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                break;
            }
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave463 apply had missing/bad targets");
        }
    }
}
