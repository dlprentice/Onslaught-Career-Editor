//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyRTBuildingRTMeshWave496 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String oldName,
                String newName,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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
            .append(spec.newName)
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

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        String currentName = fn.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + currentName + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }
        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName + " :: " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            return;
        }
        if (renameNeeded) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
            stats.renamed++;
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
        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "rtbuilding-rtmesh-wave496",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004db850",
                "CRTBuilding__Destructor",
                "CRTBuilding__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave496 signature/comment hardening: register-only receiver resets the CRTBuilding vtable to 0x005de9c0, decrements the referenced mesh/resource counter at this+0x54 -> +0x170 when present, clears this+0x54, then chains into CRTMesh__Destructor. Static retail evidence only; exact source virtual name, concrete CRTBuilding/CRTMesh layout, runtime render-building behavior, and rebuild parity remain unproven.",
                tags("rtbuilding", "rtmesh", "destructor", "vtable-referenced")
            ),
            new Spec(
                "0x004db8d0",
                "CRTBuilding__VFunc_00_004db8d0",
                "CRTBuilding__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                },
                "Wave496 name/signature/comment correction: CRTBuilding vtable 0x005de9c0 slot 0 points here. The body calls CRTBuilding__Destructor(this), frees this through CDXMemoryManager__Free(&DAT_009c3df0, this) when flags bit 0 is set, and returns this. Static retail evidence only; exact source virtual name, allocator ownership boundaries, runtime render-building behavior, and rebuild parity remain unproven.",
                tags("rtbuilding", "scalar-deleting-destructor", "vtable-slot-0", "name-corrected")
            ),
            new Spec(
                "0x004dba40",
                "CRTBuilding__VFunc_10_004dba40",
                "CRTBuilding__VFuncSlot10_PickRandomLinkedEntry",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave496 name/signature/comment correction: CRTBuilding vtable 0x005de9c0 slot 10 points here. The register-only helper returns null when this+0x58 count is zero, otherwise chooses rand() % count, walks the linked entries rooted at this+0x54 through each entry+0x08 next pointer, and returns the selected entry or the last reachable entry. Static retail evidence only; exact source virtual name, concrete list element layout, runtime render-building behavior, and rebuild parity remain unproven.",
                tags("rtbuilding", "vtable-slot-10", "name-corrected", "linked-list", "random-selection")
            ),
            new Spec(
                "0x004dc370",
                "CRTMesh__Init",
                "CRTMesh__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init", voidPtr)
                },
                "Wave496 signature/comment hardening: CRTMesh vtable 0x005deb1c slot 1 points here and CRTBuilding initialization reaches it at 0x004db8f9. The body initializes the CRenderThing base, one-time registers cg_forceobjectimposters/cg_imposterfade*/cg_meshlod*/cg_snowlayerenable console variables, resolves or falls back to a CMesh, allocates mesh-pose arrays from meshpose.h, builds underscore-prefixed material effect arrays, optionally creates an imposter, and stores linked-list/imposter/effect state. Static retail evidence only; exact source virtual name, concrete init/pose/effect layouts, runtime RTMesh rendering behavior, and rebuild parity remain unproven.",
                tags("rtmesh", "init", "vtable-slot-1", "console-vars", "mesh-pose", "imposter", "particle-effects")
            ),
            new Spec(
                "0x004dc950",
                "CRTMesh__Destructor",
                "CRTMesh__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave496 signature/comment hardening: register-only receiver resets the CRTMesh vtable to 0x005deb1c, unlinks this from global RTMesh list globals DAT_0083cd5c/DAT_0083cd60 through this+0x44/+0x48, clears/removes active particle effect handles, frees pose data through CRTMesh__FreePoseData, releases imposter/effect arrays, decrements the mesh reference counter at mesh+0x170, and then restores the CRenderThing vtable before deleting the owned base resource. Static retail evidence only; exact source virtual name, concrete CRTMesh layout, runtime rendering/effect behavior, and rebuild parity remain unproven.",
                tags("rtmesh", "destructor", "linked-list", "particle-effects", "resource-free")
            ),
            new Spec(
                "0x004dcb00",
                "CRTMesh__FreePoseData",
                "CRTMesh__FreePoseData",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("poseData", voidPtr)
                },
                "Wave496 signature/comment hardening: register-only poseData helper frees four owned pointer fields at +0x00/+0x04/+0x08/+0x0c through CDXMemoryManager__Free(&DAT_009c3df0, ...), nulling each slot after release. Static retail evidence only; exact meshpose structure layout, caller ownership boundaries, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("rtmesh", "mesh-pose", "resource-free")
            ),
            new Spec(
                "0x004dcb70",
                "CRTMesh__ScalarDeletingDestructor",
                "CRTMesh__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                },
                "Wave496 signature/comment hardening: CRTMesh vtable 0x005deb1c slot 0 points here. The body calls CRTMesh__Destructor(this), frees this through CDXMemoryManager__Free(&DAT_009c3df0, this) when flags bit 0 is set, and returns this. Static retail evidence only; exact source virtual name, allocator ownership boundaries, runtime RTMesh behavior, and rebuild parity remain unproven.",
                tags("rtmesh", "scalar-deleting-destructor", "vtable-slot-0")
            ),
            new Spec(
                "0x004dd0c0",
                "CRTMesh__CleanupAllEffects",
                "CRTMesh__CleanupAllEffects",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave496 signature/comment hardening: static no-argument cleanup iterates the global RTMesh list starting at DAT_0083cd5c and preserving DAT_0083cd60, removes every non-null effect handle in each mesh's effect array at +0x30 using ParticleEffectLink__SetHandleStateAndClear, CParticleManager__RemoveFromGlobalList, and CDXMemoryManager__Free, clears the handle slots, and unlinks each processed mesh's +0x44/+0x48 fields. Static retail evidence only; exact source name, concrete list/effect layouts, runtime render-loop behavior, and rebuild parity remain unproven.",
                tags("rtmesh", "static-helper", "linked-list", "particle-effects", "resource-free")
            ),
            new Spec(
                "0x004dd6b0",
                "CRTMesh__SetQualityLevel",
                "CRTMesh__SetQualityLevel",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("qualityLevel", intType)
                },
                "Wave496 signature/comment hardening: static quality setter accepts levels 0, 1, and 2, writes the mesh distance/LOD globals including g_MeshQualityDistance, g_MeshLodBias, _g_MeshQualityScaleFactor, and g_MeshQualityLodTable, and updates the rounded CVar value. The observed constants select low/medium/high distance and bias presets. Static retail evidence only; exact UI option mapping, runtime visual behavior, and rebuild parity remain unproven.",
                tags("rtmesh", "static-helper", "quality-level", "lod")
            ),
            new Spec(
                "0x004dd770",
                "CRTMesh__GetQualityLevel",
                "CRTMesh__GetQualityLevel",
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave496 signature/comment hardening: static no-argument getter reads g_MeshQualityDistance and returns 0 below the low threshold, 1 at or below the medium threshold, otherwise 2. Callers include PauseMenu/CPauseMenu quality UI paths and the CTreeDetail setter boundary. Static retail evidence only; exact UI option mapping, runtime visual behavior, and rebuild parity remain unproven.",
                tags("rtmesh", "static-helper", "quality-level", "lod")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=0 would_create=0" +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave496 apply had missing/bad rows");
        }
    }
}
