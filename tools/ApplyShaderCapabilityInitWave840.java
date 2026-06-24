//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyShaderCapabilityInitWave840 extends GhidraScript {
    private static final String ADDRESS = "0x005016b0";
    private static final String NAME = "InitShaderCapabilityFlagsAndCVar";
    private static final String SIGNATURE = "void __cdecl InitShaderCapabilityFlagsAndCVar(void)";
    private static final String CALLING_CONVENTION = "__cdecl";
    private static final String COMMENT =
        "Wave840 static read-back/signature/comment hardening: global no-argument shader capability initializer called once from 0x005155b1 in PCPlatform__Init after the \"Initting shaders\" log. When device/caps global DAT_00888c8c is non-zero, it calls the Direct3D device vtable +0x1c path with a stack D3DCAPS-like buffer and updates DAT_00854e6c from the dword at stack +0xc4 compared against 0xfffe0101. When DAT_0063c108 indicates vertex shaders are enabled, it invokes the console/CVar owner vfunc +0x14 for DAT_00854e10 and registers cg_forcevertexshaders with description string s_Should_vertex_shaders_be_used_wh_0063ce00, flags/value 3, and backing byte DAT_00854e6d through CConsole__RegisterVariable. Static retail Ghidra evidence only; exact Direct3D caps field identity, exact CVar schema, runtime hardware/driver behavior, runtime shader enablement, BEA patching, and rebuild parity remain deferred.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "shader-capability-init-wave840",
        "wave840-readback-verified",
        "retail-binary-evidence",
        "signature-hardened",
        "comment-hardened",
        "pc-platform",
        "vertex-shader",
        "direct3d",
        "cvar"
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
        if (!fn.getCallingConventionName().equals(CALLING_CONVENTION)) {
            return false;
        }
        return true;
    }

    private boolean alreadyApplied(Function fn) {
        String comment = fn.getComment();
        return sameSignature(fn) && COMMENT.equals(comment) && hasTags(fn);
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
                new ParameterImpl[0]
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
