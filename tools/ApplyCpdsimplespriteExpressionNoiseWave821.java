//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCpdsimplespriteExpressionNoiseWave821 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cpdsimplesprite-expression-noise-wave821",
            "wave821-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "particle-descriptor",
            "cpdsimplesprite"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        return new Spec[] {
            new Spec(
                "0x004c0c70",
                "CPDSimpleSprite__EvalExpressionNode",
                "__cdecl",
                doubleType,
                new ParameterImpl[] {
                    param("base_value", floatType),
                    param("post_scale_node", voidPtr),
                    param("pre_scale_node", voidPtr),
                    param("pre_offset_node", voidPtr),
                    param("post_offset_node", voidPtr),
                    param("operator_id", intType),
                    param("output_mode", intType),
                    param("time_scale", floatType)
                },
                "Wave821 static read-back/signature hardening: cdecl CPDSimpleSprite expression-node evaluator returns its scalar in x87 ST0 and callers/self-recursive sites push eight stack args then clean 0x20. The body combines four scalar/node pairs, optionally dispatches nested CPDSimpleSprite__EvaluateExpressionRecursive at node+0x88 through the FPU bridge, and supports observed operator cases including square, exp-style x87 f2xm1/fscale, sin, cos, reciprocal, ln2-scale, and rand jitter before output clamp/wrap-style handling. Xrefs include recursive calls from 0x004c0d2c/0x004c0ddf/0x004c0f3a/0x004c0fec plus no-function-at-pointer render/deserialization blocks. Static retail Ghidra evidence only; exact expression-node layout, exact operator names, runtime particle rendering behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("expression-evaluator", "x87-return", "recursive")
            ),
            new Spec(
                "0x004c7db0",
                "CPDSimpleSprite__InitNoiseTableOnce",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave821 static read-back/signature hardening: no-argument one-shot CPDSimpleSprite noise-table initializer. The DAT_0082b398 byte gates initialization, the body clears the 0x400-dword DAT_0082a358 table, fills a wrapped 32x32 float grid by halving the step size from 0x20 with _rand-driven midpoint/diamond-style blends, then normalizes by the maximum absolute table value when it exceeds the near-zero threshold. Direct xrefs include CPDSimpleSprite__ProcessAndRenderSpriteList at 0x004c5d5e, CPDSimpleSprite__VFunc_23_004c8040 at 0x004c8043, and an orphaned later render block at 0x004c900c. Static retail Ghidra evidence only; exact procedural-noise source algorithm, runtime particle rendering behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("noise-table", "one-shot-initializer", "render-helper")
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
        if (!fn.getSignature().getReturnType().isEquivalent(spec.returnType)) {
            return false;
        }
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (!fn.getParameter(i).getName().equals(spec.parameters[i].getName())) {
                return false;
            }
            if (!fn.getParameter(i).getDataType().isEquivalent(spec.parameters[i].getDataType())) {
                return false;
            }
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
        if (!fn.getName().equals(spec.expectedName)) {
            if (dryRun) {
                println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.expectedName);
                stats.wouldRename++;
            } else {
                fn.setName(spec.expectedName, SourceType.USER_DEFINED);
                println("RENAMED: " + spec.address + " " + spec.expectedName);
                stats.renamed++;
            }
        }

        boolean signatureOk = sameSignature(fn, spec);
        boolean commentOk = spec.comment.equals(fn.getComment());
        boolean tagsOk = hasTags(fn, spec.tags);
        if (signatureOk && commentOk && tagsOk) {
            println("SKIP: " + spec.address + " " + spec.expectedName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY_UPDATE: " + spec.address + " " + spec.expectedName
                + " signature_ok=" + signatureOk + " comment_ok=" + commentOk + " tags_ok=" + tagsOk);
            if (!signatureOk) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.skipped++;
            return;
        }

        if (!signatureOk) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        } else {
            stats.commentOnlyUpdated++;
        }
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        if (!sameSignature(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getSignature());
            stats.bad++;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            stats.bad++;
        }
        if (!hasTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            stats.bad++;
        }
        if (stats.bad == 0) {
            println("READBACK_OK: " + spec.address + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0] : "dry";
        boolean dryRun = isDryRun(mode);
        println("ApplyCpdsimplespriteExpressionNoiseWave821 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
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
