//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyWorldOccupancyBitplanesWave819 extends GhidraScript {
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
            "world-occupancy-bitplanes-wave819",
            "wave819-readback-verified",
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
        println("ApplyWorldOccupancyBitplanesWave819 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004bc2d0",
                "CWorld__ClearDynamicOccupancySet",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave819 static read-back/signature hardening: clears the dynamic world-occupancy object set at DAT_00809588 by tail-jumping into CSPtrSet__Clear at 0x004e5c60. The only direct xref is CWorld__ReleaseSubObject_AndMaybeFree at 0x0050d683. Static retail Ghidra evidence only; exact global field identity, runtime occupancy behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("world", "occupancy", "dynamic-set", "tailcall", "csptrset")
            ),
            new Spec(
                "0x004bc8d0",
                "CWorld__ClearOccupancyBitsUsingHeightBands",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave819 static read-back/signature hardening: CWorld__LoadWorld calls this no-argument world-grid pass at 0x0050d456. The body scans a 0x1ff by 0x1ff heightfield region, samples packed height through CHeightField__GetHeightSamplePacked16(&DAT_006fadc8), samples normals through CMonitor__SampleHeightfieldNormalAtXY, compares against thresholds stored after the DAT_00855290/DAT_00855294/DAT_00855298 occupancy bitplanes, and clears center/cross-neighbor bits through CWorld__SetOrClearOccupancyBit. Static retail Ghidra evidence only; exact terrain/bitplane layout, runtime pathing behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("world", "occupancy", "heightfield", "bitplane", "load-world")
            ),
            new Spec(
                "0x004bcbf0",
                "CWorld__ApplyStaticMaskToOccupancyBitplanes",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave819 static read-back/signature hardening: CWorld__LoadWorld calls this no-argument occupancy-mask pass at 0x0050d473. The body scans the static mask at DAT_00807580 and clears matching packed bits across DAT_00855290, DAT_00855294, and DAT_00855298, then marks DAT_00809598 = 1. Static retail Ghidra evidence only; exact global field names/layout, runtime pathing behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("world", "occupancy", "static-mask", "bitplane", "load-world")
            ),
            new Spec(
                "0x004bcd60",
                "CWorld__RebuildOccupancyGridFromDynamicSet",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave819 static read-back/signature hardening: CWorld__LoadWorld calls this no-argument rebuild pass at 0x0050d47a. The body resets the static occupancy mask at DAT_00807580, iterates dynamic objects from DAT_00809588 via CSPtrSet__First/CSPtrSet__Next, queries object radius/centre data, samples DAT_006fadc8 height values, tests optional collision/volume callbacks, clears static-mask bits through CWorld__SetOrClearOccupancyBit, clears DAT_00855290/DAT_00855294/DAT_00855298 center/cross-neighbor bits through CWorld__ClearCrossNeighborsInBitplane or CWorld__SetOrClearOccupancyBit, and marks DAT_00809598 = 1. Static retail Ghidra evidence only; exact dynamic-object/collision layouts, runtime pathing behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("world", "occupancy", "dynamic-set", "bitplane", "load-world")
            ),
            new Spec(
                "0x004bdff0",
                "CWorld__SkipLegacyOccupancyChunk",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem_buffer", voidPtr)
                },
                "Wave819 static read-back/signature hardening: CWorld__LoadWorld calls this legacy occupancy-chunk skipper three times at 0x0050d331, 0x0050d33d, and 0x0050d349 after loading ECX from DAT_00855290, DAT_00855294, or DAT_00855298 and pushing the CDXMemBuffer pointer in EBP. The callee reads a 4-byte chunk mode via CDXMemBuffer__Read(mem_buffer, &local_4, 4), skips 0x8000 one-byte records for mode 1 or 0x2000 one-byte records for mode 2, and exits with RET 0x4; the observed body does not consume the ECX bitplane pointer beyond the thiscall ABI. Static retail Ghidra evidence only; exact legacy chunk schema, runtime load behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("world", "occupancy", "legacy-chunk", "cdxmem-buffer", "abi-corrected")
            ),
            new Spec(
                "0x004be170",
                "CWorld__ReadOccupancyChunkHeader",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("mem_buffer", voidPtr)
                },
                "Wave819 static read-back/signature hardening: CWorld__LoadWorld calls this header reader at 0x0050d386 by pushing the CDXMemBuffer pointer in EBP and cleaning one stack argument with ADD ESP, 0x4. The body reads five 4-byte fields through CDXMemBuffer__Read and leaves the observed header locals on the caller/load stack before returning with plain RET. Static retail Ghidra evidence only; exact field names/schema, runtime load behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("world", "occupancy", "chunk-header", "cdxmem-buffer", "abi-corrected")
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
            throw new RuntimeException("Wave819 apply encountered missing/bad rows");
        }
    }
}
