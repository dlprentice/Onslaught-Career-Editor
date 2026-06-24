//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCVBufTextureRenderRestoreWave842 extends GhidraScript {
    private static final String ADDRESS = "0x0050ab60";
    private static final String NAME = "CVBufTexture__RenderAndRestoreStateFlag4";
    private static final String SIGNATURE = "void __stdcall CVBufTexture__RenderAndRestoreStateFlag4(void * dynamic_context, int unused_zero_arg, int enable_dynamic_flag_source)";
    private static final String CALLING_CONVENTION = "__stdcall";
    private static final String COMMENT =
        "Wave842 static read-back/signature/comment hardening: CDXEngine__Render callsite 0x0053e77d pushes dynamic_context from [EBP+0x470], a zero middle argument, and zero-extended byte DAT_009c7c56 before calling this wrapper. The body ends with RET 0xc, first calls CVBufTexture__SetStateCacheModeByFlag(1), tests DAT_0089ce54 bit 4 and conditionally calls RenderState__Set0x89_Zero, then loads dynamic_context from stack arg1 into ECX, tests stack arg3 and passes its nonzero result as the third stack flag to CVBufTexture__RenderDynamicUnitPass along with two constant 1 values. It calls CVBufTexture__SetStateCacheModeByFlag(1) again before returning. Static retail Ghidra evidence only; exact source function identity, dynamic-pass parameter semantics, render-state table layout, runtime rendering behavior, BEA patching, and rebuild parity remain deferred.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "cvbuftexture-render-restore-wave842",
        "wave842-readback-verified",
        "retail-binary-evidence",
        "signature-hardened",
        "comment-hardened",
        "cvbuftexture",
        "render-state",
        "dynamic-unit-render",
        "stdcall-ret0c"
    };

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

    private boolean hasTags(Function fn) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : TAGS) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameSignature(Function fn) {
        if (!fn.getName().equals(NAME)) {
            return false;
        }
        if (!fn.getSignature().toString().equals(SIGNATURE)) {
            return false;
        }
        return fn.getCallingConventionName().equals(CALLING_CONVENTION);
    }

    private boolean alreadyApplied(Function fn) {
        String comment = fn.getComment();
        return sameSignature(fn) && COMMENT.equals(comment) && hasTags(fn);
    }

    private ParameterImpl[] parameters() throws Exception {
        return new ParameterImpl[] {
            new ParameterImpl("dynamic_context", voidPtr(), currentProgram),
            new ParameterImpl("unused_zero_arg", IntegerDataType.dataType, currentProgram),
            new ParameterImpl("enable_dynamic_flag_source", IntegerDataType.dataType, currentProgram)
        };
    }

    private void apply(boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            println("MISSING: " + ADDRESS + " " + NAME);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(NAME)) {
            println("BADNAME: " + ADDRESS + " " + fn.getName() + " expected " + NAME);
            stats.bad++;
            return;
        }

        boolean needsSignature = !sameSignature(fn);
        boolean needsComment = !COMMENT.equals(fn.getComment());
        boolean needsTags = !hasTags(fn);
        if (!needsSignature && !needsComment && !needsTags) {
            println("SKIP: " + ADDRESS + " " + NAME + " already current");
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + ADDRESS + " " + NAME
                + " needsSignature=" + needsSignature
                + " needsComment=" + needsComment
                + " needsTags=" + needsTags);
            stats.skipped++;
            if (needsSignature) {
                stats.signatureUpdated++;
            } else if (needsComment || needsTags) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (needsSignature) {
            fn.setCallingConvention(CALLING_CONVENTION);
            fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                parameters()
            );
            stats.signatureUpdated++;
        } else if (needsComment || needsTags) {
            stats.commentOnlyUpdated++;
        }
        if (needsComment) {
            fn.setComment(COMMENT);
        }
        for (String tag : TAGS) {
            fn.addTag(tag);
        }

        Function readback = functionAtEntry(ADDRESS);
        if (readback == null || !alreadyApplied(readback)) {
            println("READBACK_BAD: " + ADDRESS);
            if (readback != null) {
                println("READBACK_GOT: " + readback.getName() + " " + readback.getSignature().toString());
                println("READBACK_CONVENTION: " + readback.getCallingConventionName());
            }
            stats.bad++;
            return;
        }

        println("READBACK_OK: " + ADDRESS + " " + NAME + " " + readback.getSignature().toString());
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
        apply(dryRun, stats);

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
