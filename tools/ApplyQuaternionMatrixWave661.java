//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyQuaternionMatrixWave661 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
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

    private Function functionAtEntry(String addressText) {
        Function fn = getFunctionAt(toAddr(addressText));
        if (fn == null) {
            Function containing = getFunctionContaining(toAddr(addressText));
            if (containing != null && containing.getEntryPoint().equals(toAddr(addressText))) {
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
            "quaternion-matrix-wave661",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened"
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
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
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                println("BAD: " + spec.address + " unexpected existing name " + fn.getName());
                stats.bad++;
                return;
            }
            if (!needsUpdate(fn, spec)) {
                println("SKIP: " + spec.address + " " + fn.getSignature());
                stats.skipped++;
                return;
            }

            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean signatureNeeded = !signatureMatches(fn, spec);
            if (dryRun) {
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (signatureNeeded) {
                    stats.signatureUpdated++;
                }
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (signatureNeeded) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
                stats.signatureUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + fn.getSignature());
        } catch (Exception ex) {
            println("BAD: " + spec.address + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
            stats.bad++;
        }
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

    private Spec[] buildSpecs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x00577a0a",
                "Math__BuildQuaternionFromEulerAngles_Dispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", voidPtr),
                    param("angle_x", floatType),
                    param("angle_y", floatType),
                    param("angle_z", floatType)
                },
                "Wave661 quaternion/matrix correction: runtime dispatch-table slot 25 at 0x00656f94 initializes the CPU-selected table, repacks out_quaternion_xyzw plus three Euler-angle operands, then calls the active implementation. This corrects the earlier Wave660 matrix wording: the paired source/default slot 25 at 0x006570b4 points to 0x00577a3e, which writes four quaternion-like floats, not a 4x4 matrix. Static retail decompile/instruction/dispatch-table evidence only; exact angle units, quaternion convention, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                new String[] { "Math__BuildEulerRotationMatrix4x4_Dispatch" },
                tags("dispatch-table", "quaternion", "euler", "wave660-correction")
            ),
            new Spec(
                "0x00577a38",
                "Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", voidPtr),
                    param("angle_x", floatType),
                    param("angle_y", floatType),
                    param("angle_z", floatType)
                },
                "Wave661 quaternion/matrix correction: pure jump thunk to runtime dispatch-table slot 25 at 0x00656f94, sharing the BuildQuaternionFromEulerAngles call contract with the initialized dispatcher at 0x00577a0a. This corrects the earlier Wave660 matrix wording. Static retail decompile/instruction/dispatch-table evidence only; exact angle units, quaternion convention, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                new String[] { "Math__BuildEulerRotationMatrix4x4_Dispatch_Thunk" },
                tags("dispatch-table", "quaternion", "euler", "jump-thunk", "wave660-correction")
            ),
            new Spec(
                "0x00577a3e",
                "Math__BuildQuaternionFromEulerAngles",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", voidPtr),
                    param("angle_x", floatType),
                    param("angle_y", floatType),
                    param("angle_z", floatType)
                },
                "Wave661 quaternion/matrix correction: source/default dispatch-table slot 25 at 0x006570b4 points here; the body uses repeated FSINCOS operations over three angles scaled by 0x005e72d4 and writes four float lanes at out_quaternion_xyzw+0x00..0x0c before RET 0x10. This corrects the earlier Wave660 matrix wording. Static retail decompile/instruction/dispatch-table evidence only; exact angle units, quaternion convention, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                new String[] { "Math__BuildEulerRotationMatrix4x4" },
                tags("source-dispatch-table", "quaternion", "euler", "wave660-correction")
            ),
            new Spec(
                "0x00579184",
                "CFastVB__NormalizeQuaternionCopy",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", voidPtr),
                    param("input_quaternion_xyzw", voidPtr)
                },
                "Wave661 quaternion/matrix continuation: source/default dispatch-table slot 8 at 0x00657070 points here. The body measures four quaternion lanes, uses Math__IsFloatDiffOutsideTolerance against 1.0, preserves an already-normalized non-alias input by copy, writes zeroes for near-zero length, or scales four lanes by reciprocal sqrt. Static retail decompile/instruction/dispatch-table evidence only; exact quaternion convention, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("source-dispatch-table", "quaternion", "normalize")
            ),
            new Spec(
                "0x0057923a",
                "Math__BuildMatrix4x4FromEulerAngles",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_x", floatType),
                    param("angle_y", floatType),
                    param("angle_z", floatType)
                },
                "Wave661 quaternion/matrix continuation: source/default dispatch-table slot 40 at 0x006570f0 points here. The body builds a four-float quaternion local through Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk, then forwards it to Math__BuildQuaternionRotationMatrix_Dispatch_Thunk to fill out_matrix4x4 and returns out_matrix4x4. Static retail decompile/instruction/dispatch-table evidence only; exact angle units, matrix layout, quaternion convention, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CTexture__DispatchMatrixOp00656f94_WithPostOp" },
                tags("source-dispatch-table", "matrix4x4", "quaternion", "euler", "wave660-correction")
            ),
            new Spec(
                "0x00579527",
                "Math__BuildProjectiveMatrix4x4FromPlane",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("plane_vec4", voidPtr)
                },
                "Wave661 quaternion/matrix continuation: source/default dispatch-table slot 27 at 0x006570bc points here. The body calls the slot-21 vector-normalization dispatch helper, combines the normalized plane/vector terms with plane_vec4 lanes, and writes a 4x4 projective matrix pattern. Static retail decompile/instruction/dispatch-table evidence only; exact plane equation convention, slot-21 fourth-lane behavior, matrix layout, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CTexture__BuildProjectiveMatrixFromPlane" },
                tags("source-dispatch-table", "matrix4x4", "projective", "plane")
            ),
            new Spec(
                "0x00579601",
                "Math__BuildMatrix4x4FromQuaternion",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("input_quaternion_xyzw", voidPtr)
                },
                "Wave661 quaternion/matrix continuation: source/default dispatch-table slot 28 at 0x006570c0 points here. The body normalizes/copies quaternion input through the slot-21 dispatch helper into a four-float local, then writes a 4x4 matrix using constants 0x005e9338 and 0x005e6a34 before RET 0x8. Static retail decompile/instruction/dispatch-table evidence only; exact quaternion convention, slot-21 fourth-lane behavior, matrix layout, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                new String[] { "Math__BuildMatrixFromQuaternion" },
                tags("source-dispatch-table", "matrix4x4", "quaternion")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }
        println("MODE: " + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : buildSpecs()) {
            applySpec(spec, dryRun, stats);
            if (monitor.isCancelled()) {
                break;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
