//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
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

public class ApplyMeshOptimizationWave458 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedCurrentName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String expectedCurrentName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.expectedCurrentName = expectedCurrentName;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            Function containing = getFunctionContaining(entry);
            if (containing != null && containing.getEntryPoint().equals(entry)) {
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
            "mesh-optimization-wave458",
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
            String currentName = fn.getName();
            if (!currentName.equals(spec.expectedCurrentName) && !currentName.equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
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

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!expectedSignature(spec).equals(readBack.getSignature().toString())) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(5000);
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
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004bae70",
                "CMeshPart__CanOptimizePart_Strict",
                "CMeshPart__CanOptimizePart_Strict",
                "__cdecl",
                intType,
                "Wave458 signature/comment hardening: cdecl predicate called by CMesh__OptimizeParts for one CMeshPart pointer. Checks parent-mesh animation/protected-token conditions including wheel/body/axle, buggy CORE/x1, turret/barrel, door, mech, tentacle, and barrel-spinner cases; returns 0 to block strict part removal/optimization. Runtime optimization behavior, exact CMesh/CMeshPart layouts, source identity, and rebuild parity remain unproven.",
                tags("mesh", "mesh-part", "optimization", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("part", voidPtr) }
            ),
            new Spec(
                "0x004bb040",
                "CMeshPart__CanMergeInOptimizePass",
                "CMeshPart__CanMergeInOptimizePass",
                "__cdecl",
                intType,
                "Wave458 signature/comment hardening: cdecl predicate called by CMesh__OptimizeParts for one CMeshPart pointer during merge eligibility checks. Mirrors the strict protected-token filters, uses the merge-specific buggy CORE/x1 gate, and preserves observed shared true-return helper paths for several protected cases. Runtime merge behavior, exact CMesh/CMeshPart layouts, source identity, and rebuild parity remain unproven.",
                tags("mesh", "mesh-part", "optimization", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("part", voidPtr) }
            ),
            new Spec(
                "0x004bb210",
                "CMesh__HasSpecialOptimizationConstraints",
                "CMesh__HasSpecialOptimizationConstraints",
                "__cdecl",
                boolType,
                "Wave458 signature/comment hardening: cdecl predicate called by CMesh__OptimizeParts with the mesh pointer. Returns true when mesh-wide protected animation/name constraints are present, including wheel motion, the repeated 0x623074 animation-token checks, nmidoutcyl child names, and tentacle-bone constraints, which can prevent leaf part removal. Runtime optimization behavior, exact CMesh layout, source identity, and rebuild parity remain unproven.",
                tags("mesh", "optimization", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("mesh", voidPtr) }
            ),
            new Spec(
                "0x004bbcd0",
                "CNamedMesh__VFunc_09_004bbcd0",
                "CNamedMesh__VFunc_09_004bbcd0",
                "__thiscall",
                voidType,
                "Wave458 comment/tag hardening only: CNamedMesh vtable slot 9 uses an EAX-carried init pointer that ordinary Ghidra thiscall storage does not represent cleanly. Static evidence writes init+0x64 to this+0xe0, forces init flags/state, calls CActor__Init, sets a STAND-like animation through CMesh__FindAnimationIndexByName, snapshots this+0x1c..0x28 into DAT_00807528..34, conditionally schedules event 3000, and adds this to world occupancy/static-shadow tracking. Runtime NamedMesh behavior, exact layout/source identity, and rebuild parity remain unproven.",
                tags("named-mesh", "actor-init", "occupancy", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr), param("param_1", voidPtr), param("param_2", voidPtr) }
            ),
            new Spec(
                "0x004bc050",
                "CNamedMesh__VFunc_02_004bc050",
                "CNamedMesh__VFunc02_RemoveFromOccupancyAndForward",
                "__fastcall",
                voidType,
                "Wave458 rename/signature/comment hardening: CNamedMesh vtable slot 2 removes this from world occupancy through CWorld__RemoveUnitFromOccupancyGrid_Thunk, then forwards to VFuncSlot_02_004f41b0. Xrefs include CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh and vtable 0x005dd5f0 slot 2. Runtime NamedMesh cleanup behavior, exact layout/source identity, and rebuild parity remain unproven.",
                tags("named-mesh", "occupancy", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] { param("this", voidPtr) }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0 would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
