//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyCFastVBVertexCacheScoringWave653 extends GhidraScript {
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
            "cfastvb-vertex-cache-scoring-wave653",
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
        DataType charType = CharDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005721f0",
                "CFastVB__SeedVertexCacheFromTriangleRefs",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("vertex_cache", voidPtr),
                    param("strip_batch", voidPtr)
                },
                "Wave653 CFastVB vertex-cache/scoring hardening: stdcall helper walks a strip_batch triangle-reference span and seeds the fixed vertex_cache by inserting each triangle's three vertex ids at the front when absent. Xrefs from CFastVB__MergeAndOrderStripBatches use it before overlap scoring. Static retail decompile/xref evidence only; exact cache/span layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "vertex-cache", "strip-batch", "batch-ordering", "ret-0x8")
            ),
            new Spec(
                "0x00572310",
                "CFastVB__SeedVertexCacheFromTriangle",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("vertex_cache", voidPtr),
                    param("triangle", voidPtr)
                },
                "Wave653 CFastVB vertex-cache/scoring hardening: corrected the stale CDXTexture owner label; the only current xref is from CFastVB__MergeAndOrderStripBatches_Impl_00570dd0, and the body inserts triangle's three vertex ids at the front of vertex_cache when each is absent. Static retail decompile/xref evidence only; exact cache/triangle layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CDXTexture__InsertUniqueTripletAtFront" },
                tags("cfastvb", "vertex-cache", "triangle-cache-seed", "stale-owner-corrected", "ret-0x8")
            ),
            new Spec(
                "0x005723c0",
                "CFastVB__ComputeAverageVertexOverlapScore_005723c0",
                "__stdcall",
                doubleType,
                new ParameterImpl[] {
                    param("vertex_cache", voidPtr),
                    param("strip_batch", voidPtr)
                },
                "Wave653 CFastVB vertex-cache/scoring hardening: stdcall scoring helper counts how many vertices from each triangle in strip_batch already appear in vertex_cache, then returns the average overlap score. CFastVB__MergeAndOrderStripBatches uses this score while choosing the next strip batch. Static retail decompile/xref evidence only; exact cache/span layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "vertex-cache", "overlap-score", "batch-ordering", "address-suffixed-helper")
            ),
            new Spec(
                "0x00572490",
                "CFastVB__CountTriangleVerticesInSet_00572490",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("vertex_cache", voidPtr),
                    param("triangle", voidPtr)
                },
                "Wave653 CFastVB vertex-cache/scoring hardening: stdcall helper counts how many of triangle's three vertex ids are present in vertex_cache. CFastVB__MergeAndOrderStripBatches_Impl_00570dd0 uses it to pick the best triangle from a temporary batch. Static retail decompile/xref evidence only; exact cache/triangle layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "vertex-cache", "triangle-score", "batch-ordering", "address-suffixed-helper")
            ),
            new Spec(
                "0x00572500",
                "CFastVB__CountResolvedOppositeEdges",
                "__stdcall",
                charType,
                new ParameterImpl[] {
                    param("triangle", voidPtr),
                    param("edge_buckets", voidPtr)
                },
                "Wave653 CFastVB vertex-cache/scoring hardening: stdcall helper probes all three triangle edges with CFastVB__ResolveOppositeAdjacencyRecord and returns a small count of resolved opposite adjacency records. CFastVB__MergeAndOrderStripBatches uses the count while ranking candidate batches. Static retail decompile/xref evidence only; exact edge/triangle layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "edge-resolution-score", "triangle-adjacency", "batch-ordering", "ret-0x8")
            ),
            new Spec(
                "0x00572570",
                "CFastVB__ComputeAverageUnresolvedEdgesPerBatch",
                "__stdcall",
                doubleType,
                new ParameterImpl[] {
                    param("candidate_bucket", voidPtr)
                },
                "Wave653 CFastVB vertex-cache/scoring hardening: stdcall helper walks a candidate_bucket span, subtracts each child candidate's resolved count field from its triangle-reference count, and returns the average unresolved-edge score. CFastVB__GenerateStripCandidatesFromAdjacency uses it to choose the primary candidate bucket. Static retail decompile/xref evidence only; exact candidate/span layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "candidate-bucket", "unresolved-edge-score", "strip-generation", "ret-0x4")
            ),
            new Spec(
                "0x005725e0",
                "CFastVB__GenerateStripCandidatesFromAdjacency",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_candidate_span", voidPtr),
                    param("triangle_record_span", voidPtr),
                    param("edge_buckets", voidPtr),
                    param("seed_bucket_limit", intType),
                    param("edi_context", voidPtr)
                },
                "Wave653 CFastVB vertex-cache/scoring hardening: thiscall generator allocates seed candidate buckets from triangle_record_span and edge_buckets, builds strip candidates, expands linked candidates through CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0, scores buckets with CFastVB__ComputeAverageUnresolvedEdgesPerBatch, and initializes parent links into out_candidate_span. Static retail decompile/xref evidence only; exact candidate/span/tree layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-generation", "candidate-bucket", "triangle-adjacency", "vertex-cache-scoring")
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
        if (!dryRun && (stats.bad != 0 || stats.missing != 0)) {
            throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
