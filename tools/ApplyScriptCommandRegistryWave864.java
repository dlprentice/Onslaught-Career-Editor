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

public class ApplyScriptCommandRegistryWave864 extends GhidraScript {
    private static final String ADDRESS = "0x0052ff30";
    private static final String NAME = "ScriptCommandRegistry__InitBuiltins";
    private static final String SIGNATURE = "void __cdecl ScriptCommandRegistry__InitBuiltins(void)";
    private static final String CALLING_CONVENTION = "__cdecl";
    private static final String COMMENT =
        "Wave864 static read-back/signature/comment hardening: no-argument MissionScript built-in command registry initializer reached from the adjacent 0x0052ff20 xref row. The function body writes 144 contiguous 0x40-byte command descriptor records from 0x0064ce50 through 0x0064f210; name-field assignments run from s_FollowWaypointWait_0064fa14 to s_IsOverWater_0064f234 and include PostEvent, PlaySample, GetThingRef, GetVectorLength/Magnitude, Goto3PointPanCamera, SetGoodieState, SetSlotSave, SetStealth, and ToggleCockpit. Handler fields include named IScript handlers such as IScript__ScheduleEvent, IScript__IsFriendly, IScript__PlaySound, IScript__Create3PointPanCamera, IScript__SetGoodieState, and IScript__SetSlotSave plus many still-anonymous LAB handlers. Static retail Ghidra metadata/decompile/xref evidence only; exact descriptor schema, full command semantics, runtime MissionScript dispatch/argument behavior, source identity, BEA patching, and rebuild parity remain unproven.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "script-command-registry-wave864",
        "wave864-readback-verified",
        "retail-binary-evidence",
        "signature-hardened",
        "comment-hardened",
        "important-connective-infrastructure",
        "mission-script",
        "command-registry",
        "iscript",
        "registry-initializer"
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

    private Set<String> currentTags(Function fn) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        return actual;
    }

    private boolean hasTags(Function fn) {
        Set<String> actual = currentTags(fn);
        for (String tag : TAGS) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameSignature(Function fn) {
        return fn.getName().equals(NAME)
            && fn.getSignature().toString().equals(SIGNATURE)
            && fn.getCallingConventionName().equals(CALLING_CONVENTION);
    }

    private boolean alreadyApplied(Function fn) {
        return sameSignature(fn) && COMMENT.equals(fn.getComment()) && hasTags(fn);
    }

    private void apply(boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            println("MISSING: " + ADDRESS + " " + NAME);
            stats.missing++;
            stats.bad++;
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
            println("SKIP_OK: " + ADDRESS + " " + NAME + " already current");
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY_UPDATE: " + ADDRESS + " " + NAME
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
            if (!currentTags(fn).contains(tag)) {
                fn.addTag(tag);
            }
        }

        Function readback = functionAtEntry(ADDRESS);
        if (readback == null || !alreadyApplied(readback)) {
            println("READBACK_BAD: " + ADDRESS);
            if (readback != null) {
                println("READBACK_GOT: " + readback.getName() + " " + readback.getSignature().toString() + " convention=" + readback.getCallingConventionName());
            }
            stats.bad++;
            return;
        }

        println("READBACK_OK: " + ADDRESS + " " + NAME + " " + readback.getSignature().toString() + " convention=" + readback.getCallingConventionName());
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
