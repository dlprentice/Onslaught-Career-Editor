//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCUnitSmoothEulerWave836 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedSignature, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedSignature = expectedSignature;
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
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private DataType floatPtr() {
        return new PointerDataType(FloatDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cunit-smooth-euler-wave836",
            "wave836-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "cunit",
            "unit-motion",
            "euler-smoothing",
            "matrix-build",
            "vtable-slot"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = voidPtr();
        DataType floatPtr = floatPtr();

        return new Spec[] {
            new Spec(
                "0x004fa4b0",
                "CUnit__SmoothEulerTowardTargetAndBuildMatrix",
                "void __thiscall CUnit__SmoothEulerTowardTargetAndBuildMatrix(void * this, float * current_euler_xyz, float * target_euler_xyz, float * max_step_xyz, float * out_matrix3x4)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("this", voidPtr, currentProgram),
                    new ParameterImpl("current_euler_xyz", floatPtr, currentProgram),
                    new ParameterImpl("target_euler_xyz", floatPtr, currentProgram),
                    new ParameterImpl("max_step_xyz", floatPtr, currentProgram),
                    new ParameterImpl("out_matrix3x4", floatPtr, currentProgram)
                },
                "Wave836 static read-back/signature/comment hardening: CUnit__SmoothEulerTowardTargetAndBuildMatrix is important shared CUnit motion/orientation infrastructure with lower direct source-body evidence density, not low-importance code. RET 0x10 at 0x004fa7fc plus the direct caller stub at 0x00428c15-0x00428c21 prove four explicit stack arguments after ECX: current_euler_xyz, target_euler_xyz, max_step_xyz, and out_matrix3x4. Thirty DATA slots at 0x005d8af8/0x005d8fe8/0x005dd8bc/0x005dfacc/0x005dfe70/0x005e00c0/0x005e0310/0x005e0564/0x005e07b8/0x005e0a14/0x005e0c64/0x005e0ec0/0x005e1114/0x005e1370/0x005e15c4/0x005e1814/0x005e1a64/0x005e1cb8/0x005e1f0c/0x005e216c/0x005e23c0/0x005e2610/0x005e2860/0x005e2ab0/0x005e2d00/0x005e2f54/0x005e31a8/0x005e3408/0x005e3658/0x005e38ac point at this body. Observed static behavior calls vfunc +0x60 on this for a frame-scale/time scalar, smooths current Euler x/y/z toward target Euler x/y/z using per-axis max-step input and constants at 0x005d85c0/0x005d85dc/0x005d85e0/0x005d85e4/0x005d85e8, wraps the angle axes across the +/- pi-like boundary, computes sin/cos terms, and copies twelve floats into out_matrix3x4. Static retail Ghidra evidence only; exact Unit.cpp source-body identity, exact angle units, exact matrix row/column convention, concrete CUnit layout, runtime motion/orientation behavior, BEA patching, and rebuild parity remain deferred.",
                tags("angle-wrap", "orientation-matrix", "shared-vtable-target", "cunitai-callsite")
            )
        };
    }

    private boolean hasTags(Function fn, String[] expected) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.expectedName)) {
            return false;
        }
        if (!fn.getSignature().toString().equals(spec.expectedSignature)) {
            return false;
        }
        if (!fn.getSignature().getReturnType().isEquivalent(spec.returnType)) {
            return false;
        }
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        return true;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.expectedName);
        boolean needsSignature = !sameSignature(fn, spec);
        boolean needsComment = fn.getComment() == null || !fn.getComment().equals(spec.comment);
        boolean needsTags = !hasTags(fn, spec.tags);

        if (!needsRename && !needsSignature && !needsComment && !needsTags) {
            println("SKIP: " + spec.address + " already matches " + spec.expectedName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.expectedName
                + " needsRename=" + needsRename
                + " needsSignature=" + needsSignature
                + " needsComment=" + needsComment
                + " needsTags=" + needsTags);
            stats.skipped++;
            if (needsRename) {
                stats.wouldRename++;
            }
            if (needsSignature) {
                stats.signatureUpdated++;
            } else if (needsComment || needsTags) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (needsRename) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsSignature) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        } else if (needsComment || needsTags) {
            stats.commentOnlyUpdated++;
        }
        if (needsComment) {
            fn.setComment(spec.comment);
        }
        for (String tagName : spec.tags) {
            fn.addTag(tagName);
        }

        Function readBack = functionAtEntry(spec.address);
        if (readBack == null || !sameSignature(readBack, spec) || readBack.getComment() == null
                || !readBack.getComment().equals(spec.comment) || !hasTags(readBack, spec.tags)) {
            println("BAD: readback mismatch at " + spec.address + " expected " + spec.expectedSignature);
            if (readBack != null) {
                println("BAD: got name=" + readBack.getName() + " signature=" + readBack.getSignature().toString());
            }
            stats.bad++;
            return;
        }

        println("READBACK_OK: " + spec.address + " " + readBack.getName() + " " + readBack.getSignature().toString());
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
            Thread.sleep(100);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
