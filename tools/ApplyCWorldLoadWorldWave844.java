//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCWorldLoadWorldWave844 extends GhidraScript {
    private static final String ADDRESS = "0x0050b9c0";
    private static final String NAME = "CWorld__LoadWorld";
    private static final String SIGNATURE =
        "bool __thiscall CWorld__LoadWorld(void * this, void * levelName)";
    private static final String CALLING_CONVENTION = "__thiscall";
    private static final String COMMENT =
        "Wave844 static read-back/comment hardening: CWorld__LoadWorld is the main world-load body reached only from CWorld__LoadWorldFile at 0x0050b720. The saved signature is preserved as bool __thiscall CWorld__LoadWorld(void * this, void * levelName); source World.cpp is absent from the current Onslaught snapshot, but source CGame::LoadLevel calls WORLD.Load(aLevel) before player setup, matching this retail world-load role. Retail body evidence: prologue allocates a 0x38cc-byte stack frame and returns with RET 0xc; initializes/tears down world-owned state and calls CWorld__InitLODLists and CWorld__LoadWorldHeader; reads the world buffer through many CDXMemBuffer__Read calls; recursively loads the base world through CWorld__LoadWorldFile when the read world id is present; calls CWorld__LoadScriptEvents, CHeightField__TraceMapLoadRequestAndCheckLoadedFlags, CEngine__LoadAllNamedMeshes, CWorldPhysicsManager__CreateSquad, CWorldPhysicsManager__CreateThingByType, CWorldPhysicsManager__CreateEffect, CWorldPhysicsManager__CreateTrigger, OID__CreateObject, InitThing__CreateThingByType, CWorldMeshList__Add, CInfluenceMapManager__SkipLoad or CInfluenceMapManager__Load, CWaypointManager__LoadWaypoints, and version-gated occupancy helpers. The tail collects script spawn things, and for non-base worlds calls CWorld__SpawnInitialThings, CInfluenceMapManager__Update, CInfluenceMapManager__PropagateDistances, CWorld__ClearOccupancyBitsUsingHeightBands for versions below 0x2f, then either CWorld__ApplyStaticMaskToOccupancyBitplanes or CWorld__RebuildOccupancyGridFromDynamicSet before returning success. Static retail Ghidra evidence only; exact world-buffer schema, concrete stack-local structs, source-body identity, runtime load behavior, BEA patching, and rebuild parity remain deferred.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "cworld-load-world-wave844",
        "wave844-readback-verified",
        "retail-binary-evidence",
        "comment-hardened",
        "signature-readback-verified",
        "cworld",
        "world-load",
        "level-loading",
        "occupancy-finalization",
        "ret0c"
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
            new ParameterImpl("levelName", voidPtr(), currentProgram)
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
            println("DRY: " + ADDRESS + " " + fn.getName()
                + " needsRename=false"
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
            fn.setReturnType(BooleanDataType.dataType, SourceType.USER_DEFINED);
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
