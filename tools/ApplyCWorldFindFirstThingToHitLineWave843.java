//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.Undefined4DataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCWorldFindFirstThingToHitLineWave843 extends GhidraScript {
    private static final String ADDRESS = "0x0050b030";
    private static final String OLD_NAME = "OID__TraceLineAndSelectBestTargetHit";
    private static final String NAME = "CWorld__FindFirstThingToHitLine";
    private static final String SIGNATURE =
        "int __thiscall CWorld__FindFirstThingToHitLine(void * this, undefined4 line_00, undefined4 line_04, undefined4 line_08, undefined4 line_0c, undefined4 line_10, undefined4 line_14, undefined4 line_18, undefined4 line_1c, undefined4 line_20, undefined4 line_24, undefined4 line_28, undefined4 line_2c, undefined4 line_30, void * ignored_owner, void * hit_result, int stop_on_first_valid_hit, int child_trace_mode, int collision_mode, uint reject_flags, int heightfield_trace_flags, uint required_thing_flags)";
    private static final String CALLING_CONVENTION = "__thiscall";
    private static final String COMMENT =
        "Wave843 static read-back/signature/comment hardening: renamed from OID__TraceLineAndSelectBestTargetHit to CWorld__FindFirstThingToHitLine. Source callsites in BattleEngine.cpp and DXEngine.cpp use WORLD.FindFirstThingToHitLine(...), retail callsites load ECX with DAT_00855090 before CALL 0x0050b030, and prior CWorld docs identify DAT_00855090 as the CWorld singleton. The body ends with RET 0x54, matching a 0x34-byte by-value CLine-style stack copy plus eight explicit stack fields after ECX. The function initializes hit_result status/distance, traces terrain through CHeightField__TraceLineAgainstHeightfield, walks CMapWho__GetFirstEntryWithinLine/CMapWho__GetNextEntryWithinLine, skips ignored_owner/reject_flags and required_thing_flags mismatches, filters via CThing__GetPersistentCollisionSeekingThing, selects the nearest accepted thing hit, writes hit_result object/subhit/status/distance with status 3 for thing hits, and can return early when stop_on_first_valid_hit is nonzero. The 0x34-byte line copy is kept as line_00..line_30 until the concrete CLine datatype is proven. Static retail Ghidra evidence only; exact CLine/CWorldLineColReport layout, enum names, runtime collision/targeting behavior, BEA patching, and rebuild parity remain deferred.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "cworld-find-first-thing-to-hit-line-wave843",
        "wave843-readback-verified",
        "retail-binary-evidence",
        "signature-hardened",
        "comment-hardened",
        "rename-applied",
        "cworld",
        "line-trace",
        "mapwho",
        "heightfield",
        "thiscall-ret54"
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

    private ParameterImpl lineParam(String name) throws Exception {
        return new ParameterImpl(name, Undefined4DataType.dataType, currentProgram);
    }

    private ParameterImpl intParam(String name) throws Exception {
        return new ParameterImpl(name, IntegerDataType.dataType, currentProgram);
    }

    private ParameterImpl uintParam(String name) throws Exception {
        return new ParameterImpl(name, UnsignedIntegerDataType.dataType, currentProgram);
    }

    private ParameterImpl[] parameters() throws Exception {
        return new ParameterImpl[] {
            lineParam("line_00"),
            lineParam("line_04"),
            lineParam("line_08"),
            lineParam("line_0c"),
            lineParam("line_10"),
            lineParam("line_14"),
            lineParam("line_18"),
            lineParam("line_1c"),
            lineParam("line_20"),
            lineParam("line_24"),
            lineParam("line_28"),
            lineParam("line_2c"),
            lineParam("line_30"),
            new ParameterImpl("ignored_owner", voidPtr(), currentProgram),
            new ParameterImpl("hit_result", voidPtr(), currentProgram),
            intParam("stop_on_first_valid_hit"),
            intParam("child_trace_mode"),
            intParam("collision_mode"),
            uintParam("reject_flags"),
            intParam("heightfield_trace_flags"),
            uintParam("required_thing_flags")
        };
    }

    private void apply(boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            println("MISSING: " + ADDRESS + " " + NAME);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(NAME) && !fn.getName().equals(OLD_NAME)) {
            println("BADNAME: " + ADDRESS + " " + fn.getName() + " expected " + OLD_NAME + " or " + NAME);
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(NAME);
        boolean needsSignature = !sameSignature(fn);
        boolean needsComment = !COMMENT.equals(fn.getComment());
        boolean needsTags = !hasTags(fn);
        if (!needsRename && !needsSignature && !needsComment && !needsTags) {
            println("SKIP: " + ADDRESS + " " + NAME + " already current");
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + ADDRESS + " " + fn.getName()
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
            fn.setName(NAME, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsSignature) {
            fn.setCallingConvention(CALLING_CONVENTION);
            fn.setReturnType(IntegerDataType.dataType, SourceType.USER_DEFINED);
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
