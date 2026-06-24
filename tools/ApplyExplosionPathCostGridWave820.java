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

public class ApplyExplosionPathCostGridWave820 extends GhidraScript {
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
            "explosion-path-cost-grid-wave820",
            "wave820-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean sameDataType(DataType a, DataType b) {
        if (a == null || b == null) {
            return a == b;
        }
        return a.getName().equals(b.getName()) || a.isEquivalent(b);
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        Parameter[] actualParams = fn.getParameters();
        if (actualParams.length != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < actualParams.length; i++) {
            Parameter actual = actualParams[i];
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

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            ok = false;
        }
        if (!sameSignature(fn, spec)) {
            println("BADSIG: " + spec.address + " actual=" + fn.getSignature());
            ok = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            ok = false;
        }
        if (!hasAllTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            ok = false;
        }
        if (!ok) {
            stats.bad++;
        }
        return ok;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            stats.bad++;
            return;
        }

        boolean needsSignature = !sameSignature(fn, spec);
        boolean needsCommentOrTags = !spec.comment.equals(fn.getComment()) || !hasAllTags(fn, spec.tags);

        if (needsSignature) {
            stats.signatureUpdated++;
        }
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }

        if (!needsSignature && !needsCommentOrTags) {
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName()
                + " needsRename=false"
                + " needsSignature=" + needsSignature
                + " needsCommentOrTags=" + needsCommentOrTags);
            stats.skipped++;
            return;
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
        }
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            println("READBACK_MISSING: " + spec.address);
            stats.bad++;
            return;
        }
        if (readBackMatches(readBack, spec, stats)) {
            println("OK: " + spec.address + " " + readBack.getName() + " " + readBack.getSignature());
            stats.updated++;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }
        println("ApplyExplosionPathCostGridWave820 mode=" + (dryRun ? "dry" : "apply"));

        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004bc2e0",
                "CExplosionInitThing__ClearCostGridBoundsAndBuildPath",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("start_x", floatType),
                    param("start_y", floatType),
                    param("start_z_lane", floatType),
                    param("start_w_lane", floatType),
                    param("goal_x", floatType),
                    param("goal_y", floatType),
                    param("goal_z_lane", floatType),
                    param("goal_w_lane", floatType),
                    param("search_flags", intType),
                    param("path_state", voidPtr)
                },
                "Wave820 static read-back/signature hardening: thiscall wrapper uses this/ECX as the occupancy bitplane base and RET 0x28 confirms ten stack dwords. External xrefs from CMechGuide__VFunc_03_UpdateGuidanceState_004a0bc0, CInfantryGuide__UpdateGuidanceState_0048a570, CSquadNormal__Process, and an orphaned block pass two 16-byte vector lanes, a flag, and path state. The body clears the DAT_00809dc0 256x256 cost grid sub-rectangle bounded by DAT_00829dc4/DAT_00829dc8/DAT_00630ab4/DAT_00630ab8 to 0xffff, resets those bounds, then forwards the stack shape plus this/ECX bitplane base to CExplosionInitThing__BuildGridPathWithFallbackSearch. Static retail Ghidra evidence only; exact vector semantics, flag meaning, path-state layout, runtime guidance/pathing behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("explosion-init", "pathing", "cost-grid", "abi-corrected", "guidance")
            ),
            new Spec(
                "0x004be1d0",
                "CExplosionInitThing__BuildGridPathWithFallbackSearch",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("start_x", floatType),
                    param("start_y", floatType),
                    param("start_z_lane", floatType),
                    param("start_w_lane", floatType),
                    param("goal_x", floatType),
                    param("goal_y", floatType),
                    param("goal_z_lane", floatType),
                    param("goal_w_lane", floatType),
                    param("bitplane_base", voidPtr),
                    param("search_flags", intType),
                    param("path_state", voidPtr)
                },
                "Wave820 static read-back/signature hardening: cdecl helper is called by 0x004bc2e0 and the caller cleans 0x2c stack bytes. The body rounds the x/y lanes from two by-value 16-byte vectors into 0..255 grid coordinates, stores bitplane_base in DAT_00809db8, initializes path_state count/capacity fields, accepts a direct segment when CExplosionInitThing__IsGridSegmentBlocked returns clear, otherwise finds nearest set bits, seeds DAT_00809db4/DAT_00809db0 and DAT_00829dc0/DAT_00809dbc globals, calls CExplosionInitThing__SelectNextPathStepDirection, optionally CExplosionInitThing__FindNearestVisitedGridCell, traces by CExplosionInitThing__StepToLowestCostNeighbor8, grows path arrays through CDXMemoryManager__ReAlloc, and prunes with CExplosionInitThing__SimplifyGridPathByLineOfSight. Static retail Ghidra evidence only; exact vector semantics, search flag meaning, path-state layout, runtime guidance/pathing behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("explosion-init", "pathing", "cost-grid", "fallback-search", "abi-corrected")
            ),
            new Spec(
                "0x004be420",
                "CExplosionInitThing__SelectNextPathStepDirection",
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave820 static read-back/signature hardening: no-argument cdecl helper marks the current DAT_00829dc0/DAT_00809dbc grid cell in the DAT_00809dc0 cost grid, compares against the DAT_00809db4/DAT_00809db0 goal grid coordinate, prioritizes cardinal movement by the larger axis delta, tests the DAT_00809db8 occupancy bitplane directly or through the four CanStep* helpers, then dispatches through PTR_LAB_004be94c to update the selected direction. Static retail Ghidra evidence only; exact direction table semantics, runtime guidance/pathing behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("explosion-init", "pathing", "cost-grid", "direction-select")
            ),
            new Spec(
                "0x004be9b0",
                "CExplosionInitThing__CanStepNorthFromCurrent",
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave820 static read-back/signature hardening: no-argument cdecl predicate checks whether the row above current DAT_00829dc0 is in bounds, the corresponding DAT_00809dc0 cost-grid cell is unvisited (-1), and the DAT_00809db8 packed occupancy bit for DAT_00809dbc is set; returns 1 when north is open and 0 otherwise. Static retail Ghidra evidence only; runtime guidance/pathing behavior and exact source-body identity remain deferred.",
                tags("explosion-init", "pathing", "cost-grid", "north-step")
            ),
            new Spec(
                "0x004bea10",
                "CExplosionInitThing__CanStepWestFromCurrent",
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave820 static read-back/signature hardening: no-argument cdecl predicate checks whether the column left of current DAT_00809dbc is in bounds, the corresponding DAT_00809dc0 cost-grid cell is unvisited (-1), and the DAT_00809db8 packed occupancy bit for DAT_00829dc0 is set; returns 1 when west is open and 0 otherwise. Static retail Ghidra evidence only; runtime guidance/pathing behavior and exact source-body identity remain deferred.",
                tags("explosion-init", "pathing", "cost-grid", "west-step")
            ),
            new Spec(
                "0x004bea70",
                "CExplosionInitThing__CanStepSouthFromCurrent",
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave820 static read-back/signature hardening: no-argument cdecl predicate checks whether the row below current DAT_00829dc0 is in bounds, the corresponding DAT_00809dc0 cost-grid cell is unvisited (-1), and the DAT_00809db8 packed occupancy bit for DAT_00809dbc is set; returns 1 when south is open and 0 otherwise. Static retail Ghidra evidence only; runtime guidance/pathing behavior and exact source-body identity remain deferred.",
                tags("explosion-init", "pathing", "cost-grid", "south-step")
            ),
            new Spec(
                "0x004bead0",
                "CExplosionInitThing__CanStepEastFromCurrent",
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave820 static read-back/signature hardening: no-argument cdecl predicate checks whether the column right of current DAT_00809dbc is in bounds, the corresponding DAT_00809dc0 cost-grid cell is unvisited (-1), and the DAT_00809db8 packed occupancy bit for DAT_00829dc0 is set; returns 1 when east is open and 0 otherwise. Static retail Ghidra evidence only; runtime guidance/pathing behavior and exact source-body identity remain deferred.",
                tags("explosion-init", "pathing", "cost-grid", "east-step")
            ),
            new Spec(
                "0x004beb30",
                "CExplosionInitThing__FindNearestVisitedGridCell",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave820 static read-back/signature hardening: no-argument cdecl fallback scans expanding rings around DAT_00809db4/DAT_00809db0 in the DAT_00809dc0 256x256 cost grid until it finds a cell that is not -1, then mutates DAT_00809db4/DAT_00809db0 to that reachable grid coordinate. It is called only by CExplosionInitThing__BuildGridPathWithFallbackSearch after CExplosionInitThing__SelectNextPathStepDirection fails. Static retail Ghidra evidence only; exact fallback policy, runtime guidance/pathing behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("explosion-init", "pathing", "cost-grid", "fallback-nearest")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
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

        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave820 apply encountered missing/bad rows");
        }
    }
}
