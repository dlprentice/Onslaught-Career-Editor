//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCdxMeshVbCFastVbStripWave650 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cdxmeshvb-cfastvb-strip-wave650",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
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

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0056eb50",
                "CDXMeshVB__SetTriangleStripDebugFlag",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("enabled", intType) },
                "Wave650 CDXMeshVB strip-state hardening: single-argument setter stores the low byte of enabled into DAT_009d0c40. Xrefs from CLandscapeIB__CreateIndexBuffer plus CDXMeshVB static/skeletal build paths show it configures the alternate/debug strip emission branch before batch construction. Static retail decompile/xref evidence only; runtime render output, exact global ownership, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxmeshvb", "strip-state-setter", "debug-strip-flag", "global-009d0c40")
            ),
            new Spec(
                "0x0056eb60",
                "CDXMeshVB__SetEmitDegenerateFlag",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("enabled", intType) },
                "Wave650 CDXMeshVB strip-state hardening: single-argument setter stores enabled into DAT_00656e5c. Shared xrefs from landscape, static mesh, and skeletal mesh index-buffer builders show this flag is part of the strip-batch setup state before CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer runs. Static retail decompile/xref evidence only; exact runtime strip policy, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxmeshvb", "strip-state-setter", "degenerate-strip-flag", "global-00656e5c")
            ),
            new Spec(
                "0x0056eb70",
                "CDXMeshVB__SetWordIndexModeFlag",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("enabled", intType) },
                "Wave650 CDXMeshVB strip-state hardening: single-argument setter stores the low byte of enabled into DAT_00656e60. The strip-batch emitter reads this global when deciding whether to preserve one packed word-index stream or split batches around sentinel entries. Static retail decompile/xref evidence only; exact runtime index-buffer behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxmeshvb", "strip-state-setter", "word-index-mode", "global-00656e60")
            ),
            new Spec(
                "0x0056eb80",
                "CDXMeshVB__SetBatchSplitThreshold",
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("threshold", intType) },
                "Wave650 CDXMeshVB strip-state hardening: single-argument setter stores threshold into DAT_009d0c3c. The adjacent strip-batch construction path uses the same global state block while emitting triangle-strip batches from word-index spans. Static retail decompile/xref evidence only; exact threshold semantics, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxmeshvb", "strip-state-setter", "batch-split-threshold", "global-009d0c3c")
            ),
            new Spec(
                "0x0056eb90",
                "CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("index_words", voidPtr),
                    param("index_word_count", uintType),
                    param("out_batch_records", voidPtr),
                    param("out_batch_count", voidPtr)
                },
                "Wave650 CDXMeshVB strip-batch hardening: cdecl helper normalizes/grows word-index spans, copies the incoming index words, builds strip batches through the CFastVB pipeline, emits either normal strip ranges or the DAT_009d0c40 debug/alternate triangle output, allocates 0x0c-byte batch records, writes the batch-record pointer and 16-bit batch count through the out parameters, then releases local span builders through EH unwind helpers. Static retail decompile/xref evidence only; exact batch-record layout, runtime D3D output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxmeshvb", "strip-batch-build", "index-buffer-emission", "cfastvb-pipeline", "out-batch-records")
            ),
            new Spec(
                "0x0056f260",
                "CFastVB__ReleaseBufferAndResetTriplet_0056f260",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("span", voidPtr) },
                "Wave650 CFastVB span-helper hardening: fastcall helper frees the buffer pointer at span+0x4 through OID__FreeObject_Callback and clears the begin/end/capacity triplet at +0x4/+0x8/+0x0c. Xrefs include strip-batch unwind paths and BuildTriangleStripFromSeedRecord cleanup. Static retail decompile/xref evidence only; exact container type, allocator ownership, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "span-release-reset", "strip-cleanup", "duplicate-helper-0056f260")
            ),
            new Spec(
                "0x0056f280",
                "CFastVB__CountWordElements",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("span", voidPtr) },
                "Wave650 CFastVB word-span hardening: fastcall helper returns zero for an empty begin pointer, otherwise computes (end - begin) >> 1. It is used by CDXMeshVB strip-batch setup and triangle-strip seed construction to size 16-bit index spans. Static retail decompile/xref evidence only; exact span type, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "word-span", "count-elements", "index-word-count")
            ),
            new Spec(
                "0x0056f2a0",
                "CFastVB__InsertWordSpanFilled",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("insert_word_ptr", voidPtr),
                    param("word_count", uintType),
                    param("fill_word_ptr", voidPtr),
                    param("edi_context", voidPtr)
                },
                "Wave650 CFastVB word-span hardening: thiscall insert helper grows or shifts a 16-bit span, inserts word_count copies of the value pointed to by fill_word_ptr at insert_word_ptr, updates the end pointer, and reallocates through OID helpers when capacity is insufficient. Static retail decompile/callsite evidence only; exact container layout, EDI context ownership, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "word-span", "insert-filled", "span-grow")
            ),
            new Spec(
                "0x0056f4b0",
                "CFastVB__CopyWordRangeToBufferAndAdvanceEnd",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("write_ptr", voidPtr),
                    param("src_begin", voidPtr),
                    param("edi_context", voidPtr)
                },
                "Wave650 CFastVB word-span hardening: copies 16-bit words from src_begin up to the span end pointer into write_ptr and advances this+0x8 to the resulting write cursor. The fourth stack value is not consumed by the decompiled body and is retained as the observed call-boundary context. Static retail decompile/callsite evidence only; exact container type, EDI context ownership, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "word-span", "copy-range", "advance-end")
            ),
            new Spec(
                "0x0056f500",
                "CFastVB__InitWordSpanHeader",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("span", voidPtr) },
                "Wave650 CFastVB word-span hardening: fastcall initializer writes the incoming high-byte seed into the first byte and clears the begin/end/capacity triplet at +0x4/+0x8/+0x0c. CDXMeshVB uses it for local strip-batch word-span setup before CFastVB__BuildStripBatchesFromIndexBuffer. Static retail decompile evidence only; exact header semantics, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "word-span", "initializer", "triplet-clear")
            ),
            new Spec(
                "0x0056f520",
                "CFastVB__ReleaseBufferAndResetTriplet_0056f520",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("span", voidPtr) },
                "Wave650 CFastVB span-helper hardening: duplicate fastcall release/reset body frees span+0x4 through OID__FreeObject_Callback and clears +0x4/+0x8/+0x0c. It is kept as a distinct address-suffixed helper because the retail binary contains two equivalent routines with separate call/unwind contexts. Static retail decompile/xref evidence only; exact template/source identity, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "span-release-reset", "duplicate-helper-0056f520", "strip-cleanup")
            ),
            new Spec(
                "0x0056f540",
                "CFastVB__FindEdgeRecord",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {
                    param("edge_buckets", voidPtr),
                    param("vertex_a", intType),
                    param("vertex_b", intType)
                },
                "Wave650 CFastVB adjacency hardening: scans the edge-record bucket chain for either vertex order, following +0x14 and +0x18 links depending on which endpoint matched, and returns the matching edge record or null. Used by BuildTriangleAdjacency and strip-extension helpers. Static retail decompile/xref evidence only; exact edge-record layout, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "triangle-adjacency", "edge-record-lookup", "returns-pointer")
            ),
            new Spec(
                "0x0056f580",
                "CFastVB__ResolveOppositeAdjacencyRecord",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {
                    param("edge_buckets", voidPtr),
                    param("vertex_a", intType),
                    param("vertex_b", intType),
                    param("current_triangle", voidPtr)
                },
                "Wave650 CFastVB adjacency hardening: resolves an edge record for vertex_a/vertex_b, returns null for a missing self-edge, then returns the opposite triangle pointer from the +0x4/+0x8 pair relative to current_triangle. Static retail decompile/xref evidence only; exact triangle/edge layout, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "triangle-adjacency", "opposite-record", "returns-pointer")
            ),
            new Spec(
                "0x0056f5c0",
                "CFastVB__ContainsTriangleTriplet",
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("triangle", voidPtr),
                    param("triangle_span", voidPtr)
                },
                "Wave650 CFastVB adjacency hardening: stdcall predicate walks a dword-pointer span and returns a low-byte true value when it finds a triangle record whose first three dwords match the candidate triangle. Static retail decompile/xref evidence only; boolean width, exact triangle-record layout, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "triangle-adjacency", "triangle-triplet-predicate", "ret-0x8")
            ),
            new Spec(
                "0x0056f620",
                "CFastVB__BuildTriangleAdjacency",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("triangle_record_span", voidPtr),
                    param("edge_buckets", voidPtr),
                    param("max_vertex_index", intType),
                    param("mode_flags", uintType)
                },
                "Wave650 CFastVB adjacency hardening: thiscall builder treats the receiver as the source 16-bit triangle-index span, sizes triangle and edge-bucket spans, creates 0x18-byte triangle records and 0x1c-byte edge records, links opposite triangles through CFastVB__FindEdgeRecord, emits duplicate/non-manifold diagnostics, and appends records to the caller-provided spans for later strip selection. Static retail decompile/xref evidence only; exact record layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "triangle-adjacency", "edge-record-build", "stripify")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad != 0 || stats.missing != 0) {
                throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
            }
        }
    }
}
