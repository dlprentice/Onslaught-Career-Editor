//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCTreeWave520 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final boolean createIfMissing;
        final boolean renameAllowed;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags,
                boolean createIfMissing, boolean renameAllowed) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.createIfMissing = createIfMissing;
            this.renameAllowed = renameAllowed;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int created = 0;
        int wouldCreate = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "ctree-wave520",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
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

    private Function createFunctionAt(Spec spec, Address address) throws Exception {
        Function containing = getFunctionContaining(address);
        if (containing != null && !containing.getEntryPoint().equals(address)) {
            throw new IllegalStateException(
                "Address " + spec.address + " is inside existing function " + containing.getName());
        }
        Function fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = getFunctionAt(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        return fn;
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function fn = functionAtEntry(spec.address);
        boolean createdNow = false;

        if (fn == null) {
            if (!spec.createIfMissing) {
                println("MISSING: " + spec.address);
                stats.missing++;
                return;
            }
            if (dryRun) {
                println("DRYCREATE: " + spec.address + " <missing> -> " + expectedSignature(spec));
                stats.wouldCreate++;
                stats.skipped++;
                return;
            }
            fn = createFunctionAt(spec, address);
            createdNow = true;
            stats.created++;
        }

        if (!fn.getName().equals(spec.name)) {
            if (!spec.renameAllowed) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }
            if (dryRun) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.wouldRename++;
                stats.skipped++;
                return;
            }
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }

        boolean updateNeeded = createdNow || needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            stats.skipped++;
            return;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec) +
            (createdNow ? " created" : ""));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004f5f60",
                "CTree__InitFallingTreeData",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("tree_type_matrix", voidPtr),
                    param("scale", floatType),
                    param("impact_vector", voidPtr)
                },
                "Wave520 CTree signature/comment hardening: RET 0x0c plus the CTree__CreateFallingTree callsite show an ECX falling-tree-data object and three stack arguments: a 12-dword tree-type matrix copy, a doubled scale float from the tree virtual slot +0x40 result, and an impact/direction vector pointer. The body mirrors the matrix into current/base/previous matrix slots, clears angle/velocity fields, copies the vector to +0x0c, derives a normalized side/fall axis at +0x1c, stores angular velocity 0x3ca3d70a at +0x08, and returns this. Static retail evidence only; exact structure field names, source body identity, runtime falling-tree physics, BEA patching, and rebuild parity remain unproven.",
                tags("ctree", "falling-tree", "initializer", "matrix-copy"),
                false,
                false
            ),
            new Spec(
                "0x004f63c0",
                "CTree__dtor_base",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave520 CTree name/signature/comment correction: this is the destructor body called by CTree__scalar_deleting_dtor at 0x004bfce0, not the scalar-deleting wrapper itself. The body reinstalls the CTree/CThing-adjacent vtables at this+0 and this+8, frees the falling-tree data pointer at this+0x48 through CDXMemoryManager__Free when present, clears that pointer, and delegates to CThing__dtor_base. Static retail evidence only; destructor completeness, concrete layout, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ctree", "destructor", "falling-tree", "name-corrected"),
                false,
                true
            ),
            new Spec(
                "0x004f6430",
                "CTree__ComputeLodBucket",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave520 CTree signature/comment hardening: CEngine__InitDamageSystem calls this helper. The body dispatches through the render/resource object at this+0x08 virtual slot +0x54 twice, reads resource floats at +0x10 and +0x14, keeps the larger/non-NaN value, multiplies by the scale constant at 0x005d8be8, rounds to a byte, and clamps the result to bucket 6. Static retail evidence only; exact LOD field names, resource object type, runtime tree LOD behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ctree", "lod", "resource-scalar"),
                false,
                false
            ),
            new Spec(
                "0x004f68e0",
                "CTree__VFunc_28_CreateFallingTreeAfterDelay",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("elapsed_time", floatType),
                    param("other_thing", voidPtr),
                    param("unused_arg2", intType),
                    param("unused_arg3", intType)
                },
                "Wave520 recovered CTree vtable boundary: CTree vtable 0x005dd9d8 slot 40 points to 0x004f68e0 and the body returns with RET 0x10. The visible body skips when this+0x48 falling data already exists, decrements the timer/cooldown at this+0x44 by elapsed_time, and when the timer crosses zero computes a normalized vector from this position to other_thing+0x1c before calling CTree__CreateFallingTree. Two trailing stack arguments are not used in the recovered body. Static retail evidence only; exact virtual name, source identity, caller contract, runtime collision/destruction behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ctree", "boundary-recovered", "vtable-slot", "falling-tree", "timer-gate"),
                true,
                false
            ),
            new Spec(
                "0x004f69b0",
                "CTree__CreateFallingTree",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("impact_vector", voidPtr)},
                "Wave520 CTree signature/comment hardening: RET 0x4 and the vtable-slot callers show this plus an impact/direction vector pointer. The body skips if falling-tree data already exists at this+0x48, copies the 0x30-byte tree-type matrix block from DAT_008406b8 using this+0x40 as an index, allocates a 0xc0-byte falling-tree data object from tree.cpp line 0xf0, calls the tree virtual slot +0x40 to derive scale, initializes the data via CTree__InitFallingTreeData, stores it at this+0x48, seeds field +0xbc to -1.0, schedules event 0xbb9 after 0.5 seconds, and immediately calls CTree__UpdateFallingTree. Static retail evidence only; exact source identity, concrete layouts, runtime knockdown behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ctree", "falling-tree", "allocator", "event-scheduled"),
                false,
                false
            ),
            new Spec(
                "0x004f6aa0",
                "CTree__VFunc_27_CreateFallingTreeFromThing",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("other_thing", voidPtr),
                    param("unused_context", intType)
                },
                "Wave520 recovered CTree vtable boundary: CTree vtable 0x005dd9d8 slot 39 points to 0x004f6aa0 and the body returns with RET 0x8. The visible body checks other_thing flags at +0x34, skips when falling-tree data already exists at this+0x48, computes a vector between this position and other_thing+0x1c, applies an alternate distance threshold when flag 0x01000000 is set, normalizes the vector, and calls CTree__CreateFallingTree when the threshold gate passes. The second stack argument is not used in the recovered body. Static retail evidence only; exact virtual name, caller contract, runtime collision/destruction behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ctree", "boundary-recovered", "vtable-slot", "falling-tree", "collision-gate"),
                true,
                false
            ),
            new Spec(
                "0x004f6b80",
                "CTree__UpdateFallingTree",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave520 CTree signature/comment hardening: CTree__CreateFallingTree and the recovered event-handler boundary call this with ECX as the tree object. The body updates the falling-tree data at this+0x48 by copying current to previous matrix slots, tracing downward against the heightfield while velocity is positive, spawning the \"Tree Ground Hit Effect\" particle on sufficiently strong ground impact, damping/reversing velocity on contact, settling to DAT_00672fd0 and scheduling event 0x7d2 when motion falls below the threshold, otherwise integrating angle/velocity, rebuilding the rotation matrix, writing the current matrix, and rescheduling event 3000. Static retail evidence only; exact source identity, concrete layouts, runtime particle/physics behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ctree", "falling-tree", "physics-update", "particle-effect", "event-scheduled"),
                false,
                false
            ),
            new Spec(
                "0x004f7050",
                "CTree__HandleEvent",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("event", voidPtr)},
                "Wave520 recovered CTree vtable boundary: CTree vtable 0x005dd9d8 slot 0 points to 0x004f7050 and the body returns with RET 0x4. The event word at event+0x04 is compared against 3000/3001; the 3000 path calls CTree__UpdateFallingTree, the 3001 path dispatches through the object at this+0x38 with argument -1, and other events delegate to the CThing event handler at 0x004f3730. Static retail evidence only; exact event names, this+0x38 target type, runtime scheduler behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ctree", "boundary-recovered", "vtable-slot", "event-handler", "falling-tree"),
                true,
                false
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
