//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCChunkReaderResourceReviewWave983 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType, ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
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

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName()).append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        return fn.getSignature().toString().equals(expectedSignature(spec));
    }

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
            ok = false;
        }
        if (!signatureMatches(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + expectedSignature(spec) + " actual=" + fn.getSignature());
            ok = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            ok = false;
        }
        if (!hasAllTags(fn, spec)) {
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
            println("MISSING: " + spec.address + " " + spec.name);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
            stats.bad++;
            return;
        }

        boolean needsSignature = !signatureMatches(fn, spec);
        boolean needsCommentOrTags = !spec.comment.equals(fn.getComment()) || !hasAllTags(fn, spec);

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
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec)
                + " needsRename=false"
                + " needsSignature=" + needsSignature
                + " needsCommentOrTags=" + needsCommentOrTags);
            stats.skipped++;
            return;
        }

        if (needsSignature) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.params);
        }
        if (needsCommentOrTags) {
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
        }
        if (readBackMatches(fn, spec, stats)) {
            println("APPLY_OK: " + spec.address + " " + spec.name + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        String[] tags = new String[] {
            "static-reaudit",
            "cchunkreader-resource-review-wave983",
            "wave983-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "source-parity-reviewed",
            "chunk-reader",
            "resource-io"
        };

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004237d0",
                "CChunkReader__ctor",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave983 CChunkReader resource review: source-backed constructor from chunker.cpp creates the read-side tagged-chunk cursor by allocating a 0x134-byte CDXMemBuffer/CMEMBUFFER, storing it at this+0x4, setting mOwnFile at this+0xc, and returning this. Static retail Ghidra/source evidence only; exact structure layout, runtime archive IO behavior, BEA patching, and rebuild parity remain unproven.",
                tags
            ),
            new Spec(
                "0x00423840",
                "CChunkReader__dtor_base",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave983 CChunkReader resource review: source-backed destructor-base frees the owned CDXMemBuffer/CMEMBUFFER only when mOwnFile and File are set, then clears File. Static retail Ghidra/source evidence only; exact allocator ownership, runtime archive IO behavior, BEA patching, and rebuild parity remain unproven.",
                tags
            ),
            new Spec(
                "0x00423870",
                "CChunkReader__OpenExistingBuffer",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("existingBuffer", voidPtr) },
                "Wave983 CChunkReader resource review: source-backed Open(CMEMBUFFER*) helper resets Size and ReadSinceChunk, drops any owned buffer, marks mOwnFile false, stores existingBuffer at this+0x4, and returns it. Static retail Ghidra/source evidence only; exact buffer layout, runtime archive IO behavior, BEA patching, and rebuild parity remain unproven.",
                tags
            ),
            new Spec(
                "0x004238c0",
                "CChunkReader__OpenFile",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("filename", charPtr) },
                "Wave983 CChunkReader resource review: source-backed Open(char*) helper resets Size and ReadSinceChunk, opens the owned CDXMemBuffer through CDXMemBuffer__InitFromFile(File, filename, MEMTYPE_MEMBUFFER, true, 0), and returns File or null. Static retail Ghidra/source evidence only; runtime filesystem/resource IO behavior, BEA patching, and rebuild parity remain unproven.",
                tags
            ),
            new Spec(
                "0x00423900",
                "CChunkReader__Close",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave983 CChunkReader resource review: source-backed Close wrapper calls the active File->Close path and normalizes success to 0 or failure to -1. Static retail Ghidra/source evidence only; runtime file-handle behavior, exact buffer layout, BEA patching, and rebuild parity remain unproven.",
                tags
            ),
            new Spec(
                "0x00423910",
                "CChunkReader__GetNext",
                "__fastcall",
                uintType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave983 CChunkReader resource review: source-backed GetNext helper resets ReadSinceChunk, reads a 4-byte chunk id and 4-byte Size through CDXMemBuffer__Read, and returns the chunk id or 0 on short read. This is the shared tagged-chunk header cursor, not CMeshPart-specific. Static retail Ghidra/source evidence only; runtime archive parsing, exact schema coverage, BEA patching, and rebuild parity remain unproven.",
                tags
            ),
            new Spec(
                "0x00423960",
                "CChunkReader__Read",
                "__thiscall",
                boolType,
                new ParameterImpl[] { param("this", voidPtr), param("outBuffer", voidPtr), param("size", intType), param("count", intType) },
                "Wave983 CChunkReader resource review: source-backed Read helper increments ReadSinceChunk by size*count, reads that byte count through CDXMemBuffer__Read, and returns whether the full payload was read. Static retail Ghidra/source evidence only; runtime payload semantics, exact schema coverage, BEA patching, and rebuild parity remain unproven.",
                tags
            ),
            new Spec(
                "0x00423990",
                "CChunkReader__Skip",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave983 CChunkReader resource review: source-backed Skip helper computes Size-ReadSinceChunk, advances ReadSinceChunk to Size, and skips the remaining bytes through CDXMemBuffer__Skip(File, remaining). Static retail Ghidra/source evidence only; runtime unknown-chunk behavior, exact archive schema coverage, BEA patching, and rebuild parity remain unproven.",
                tags
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
            throw new IllegalStateException("Wave983 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            currentProgram.flushEvents();
        }
    }
}
