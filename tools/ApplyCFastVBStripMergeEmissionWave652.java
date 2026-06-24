//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplyCFastVBStripMergeEmissionWave652 extends GhidraScript {
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
            "cfastvb-strip-merge-emission-wave652",
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
        DataType boolType = BooleanDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00570cb0",
                "CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0",
                "__stdcall",
                boolType,
                new ParameterImpl[] {
                    param("triangle_record_span", voidPtr),
                    param("edge_buckets", voidPtr),
                    param("candidate_root", voidPtr),
                    param("out_edge_pick", voidPtr)
                },
                "Wave652 CFastVB strip merge/emission hardening: stdcall helper walks an edge bucket selected from candidate_root side state, checks adjacent triangle ownership through CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90, and writes the selected triangle, edge record, and side flag to out_edge_pick. Static retail decompile/xref evidence only; exact candidate/edge layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-candidate-selection", "edge-chain-walk", "out-edge-pick", "address-suffixed-helper")
            ),
            new Spec(
                "0x00570dd0",
                "CFastVB__MergeAndOrderStripBatches_Impl_00570dd0",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("candidate_batch_span", voidPtr),
                    param("overflow_batch_span", voidPtr),
                    param("output_batch_span", voidPtr),
                    param("edi_context", voidPtr)
                },
                "Wave652 CFastVB strip merge/emission hardening: internal thiscall helper appends overflow and output batch spans, splits oversized candidate batches through a temporary triangle list, scores candidates with CFastVB__CountTriangleVerticesInSet_00572490, and emits reordered dword references into output_batch_span. Static retail decompile/xref evidence only; exact batch/container layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-merge-order", "internal-helper", "candidate-batches", "vertex-cache", "address-suffixed-helper")
            ),
            new Spec(
                "0x00571060",
                "CFastVB__IsEven",
                "__stdcall",
                boolType,
                new ParameterImpl[] {
                    param("value", uintType)
                },
                "Wave652 CFastVB strip merge/emission hardening: tiny stdcall parity helper returns whether value is even and is used by CFastVB__EmitTriangleStripIndexBuffer while deciding whether a strip bridge needs an extra index. Static retail decompile/xref evidence only; exact compiler provenance, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "parity-helper", "strip-emission-helper", "ret-0x4")
            ),
            new Spec(
                "0x00571080",
                "CFastVB__IsDirectedEdgeInTriangle",
                "__stdcall",
                boolType,
                new ParameterImpl[] {
                    param("triangle", voidPtr),
                    param("edge_start", intType),
                    param("edge_end", intType)
                },
                "Wave652 CFastVB strip merge/emission hardening: stdcall predicate checks whether triangle's ordered vertex triplet contains the directed edge edge_start->edge_end across the first, second, or wraparound edge. Xrefs from strip emission and merge/order use it to orient strip output. Static retail decompile/xref evidence only; exact triangle layout, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "directed-edge", "triangle-compare", "strip-emission-helper", "ret-0xc")
            ),
            new Spec(
                "0x005710d0",
                "CFastVB__EmitTriangleStripIndexBuffer",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("strip_batch_span", voidPtr),
                    param("out_index_span", voidPtr),
                    param("emit_continuity_flag", intType),
                    param("out_separator_count", voidPtr)
                },
                "Wave652 CFastVB strip merge/emission hardening: stdcall emitter walks selected strip batches, orients adjacent triangles with vertex-set/shared-edge helpers, appends dword indices into out_index_span, inserts 0xffffffff restart separators when continuity is disabled, and updates out_separator_count. Static retail decompile/xref evidence only; exact output container layout, runtime D3D index buffer behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-emission", "index-buffer-emission", "separator-count", "triangle-compare")
            ),
            new Spec(
                "0x00571870",
                "CFastVB__HasDuplicateTriangleIndices32",
                "__cdecl",
                boolType,
                new ParameterImpl[] {
                    param("triangle", voidPtr)
                },
                "Wave652 CFastVB strip merge/emission hardening: cdecl predicate checks a 32-bit triangle triplet for any duplicate vertex index and is used by adjacency, emission, and merge/order paths to filter degenerate triangles. Static retail decompile/xref evidence only; exact triangle layout, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "duplicate-indices", "triangle-compare", "dword-indices", "cdecl")
            ),
            new Spec(
                "0x00571890",
                "CFastVB__HasDuplicateTriangleIndices16",
                "__stdcall",
                boolType,
                new ParameterImpl[] {
                    param("index_a", intType),
                    param("index_b", intType),
                    param("index_c", intType)
                },
                "Wave652 CFastVB strip merge/emission hardening: stdcall predicate compares the low 16-bit forms of three supplied indices and returns true when any pair matches; CFastVB__BuildTriangleAdjacency uses it as a degenerate-triangle guard. Static retail decompile/xref evidence only; exact source-level argument widths, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "duplicate-indices", "triangle-compare", "word-indices", "ret-0xc")
            ),
            new Spec(
                "0x005718c0",
                "CFastVB__MergeAndOrderStripBatches",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("candidate_batch_span", voidPtr),
                    param("ordered_batch_span", voidPtr),
                    param("edge_buckets", voidPtr),
                    param("output_batch_span", voidPtr),
                    param("edi_context", voidPtr)
                },
                "Wave652 CFastVB strip merge/emission hardening: public thiscall merge/order helper splits oversized strip batches by this+0x10/this+0x14, filters duplicate 32-bit triangle rows, delegates the internal merge pass to CFastVB__MergeAndOrderStripBatches_Impl_00570dd0, and then selects batch order using edge-resolution and vertex-cache scoring. Static retail decompile/xref evidence only; exact CFastVB/container layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-merge-order", "batch-splitting", "vertex-cache", "candidate-batches")
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
