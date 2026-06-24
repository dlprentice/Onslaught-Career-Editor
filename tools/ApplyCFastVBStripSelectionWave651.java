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

public class ApplyCFastVBStripSelectionWave651 extends GhidraScript {
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
            "cfastvb-strip-selection-wave651",
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
                "0x0056fce0",
                "CFastVB__SelectTriangleWithMaxOpenEdges",
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("triangle_record_span", voidPtr),
                    param("edge_buckets", voidPtr)
                },
                "Wave651 CFastVB strip-selection hardening: stdcall helper scans a span of triangle-record pointers, counts unresolved/open edges by calling CFastVB__ResolveOppositeAdjacencyRecord for each triangle side, returns the index with the highest open-edge count, and returns 0xffffffff when no open-edge candidate exists. Static retail decompile/xref evidence only; exact strip-quality heuristic, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-selection", "open-edge-count", "returns-index", "ret-0x8")
            ),
            new Spec(
                "0x0056fdc0",
                "CFastVB__SelectNextStripTriangle",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("triangle_record_span", voidPtr),
                    param("edge_buckets", voidPtr),
                    param("edi_context", voidPtr)
                },
                "Wave651 CFastVB strip-selection hardening: thiscall helper chooses the next unclaimed triangle record from triangle_record_span, optionally seeds from CFastVB__SelectTriangleWithMaxOpenEdges when this+0x1c is armed, advances the floating selector field at this+0x18, and returns the selected triangle pointer or null. Static retail decompile/callsite evidence only; exact randomized selection policy, receiver layout, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-selection", "next-triangle", "open-edge-seed", "returns-pointer")
            ),
            new Spec(
                "0x0056fe70",
                "CFastVB__AreTriangleVertexSetsEquivalent",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("triangle_a", voidPtr),
                    param("triangle_b", voidPtr)
                },
                "Wave651 CFastVB strip-selection hardening: cdecl predicate checks whether all three vertices from triangle_b appear in triangle_a regardless of order. Callers in CFastVB__EmitTriangleStripIndexBuffer and CFastVB__MergeAndOrderStripBatches use the return value as a match/rotation cue; boolean exactness is not overclaimed because the false path retains decompiler-carried vertex values. Static retail decompile/xref evidence only; exact return convention, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "triangle-compare", "vertex-set-equivalence", "strip-emission-helper")
            ),
            new Spec(
                "0x0056fec0",
                "CFastVB__GetSharedVerticesBetweenTriangles",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("triangle_a", voidPtr),
                    param("triangle_b", voidPtr),
                    param("out_shared_a", voidPtr),
                    param("out_shared_b", voidPtr)
                },
                "Wave651 CFastVB strip-selection hardening: cdecl helper initializes both out slots to 0xffffffff, walks triangle_b's three vertices against triangle_a, stores the first shared vertex in out_shared_a, and stores the second shared vertex in out_shared_b when present. Xrefs from strip emission and merge/order logic use it to orient adjacent triangle output. Static retail decompile/xref evidence only; exact triangle-record type, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "triangle-compare", "shared-vertices", "out-parameters")
            ),
            new Spec(
                "0x0056ff40",
                "CFastVB__TriangleListContainsVertexTriplet_0056ff40",
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("triangle_list_span", voidPtr),
                    param("triangle", voidPtr)
                },
                "Wave651 CFastVB strip-selection hardening: stdcall predicate walks a span of triangle-record pointers and tracks whether the candidate triangle's three vertex ids appear across the list; it returns low-byte false when all three are already represented and low-byte true while another expansion candidate is still allowed. Static retail decompile/xref evidence only; exact boolean width, address-suffixed source identity, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "triangle-compare", "triangle-list-membership", "ret-0x8", "address-suffixed-helper")
            ),
            new Spec(
                "0x00570000",
                "CFastVB__BuildTriangleStripFromSeedRecord",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("edge_buckets", voidPtr),
                    param("generation_context", intType)
                },
                "Wave651 CFastVB strip-selection hardening: thiscall builder starts from a seed triangle/candidate record, grows forward and reverse 16-bit strip word spans through adjacency records, stamps selected triangle owner fields, may allocate synthetic 0x18-byte bridge records, and appends candidate batches through CFastVB__InsertStripCandidatesIntoBuffer_005708a0. The trailing generation_context is retained for the observed ABI but is not consumed by the current decompile. Static retail decompile/callsite evidence only; exact record layouts, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-builder", "seed-triangle", "adjacency-walk", "candidate-batches")
            ),
            new Spec(
                "0x00570870",
                "CFastVB__StampRecordOwnerFields",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("triangle_record", voidPtr),
                    param("edi_context", voidPtr)
                },
                "Wave651 CFastVB strip-selection hardening: thiscall helper stamps owner/group fields on a triangle record from this+0x1c and this+0x20, writing either the +0x0c/+0x14 negative-owner form or the +0x10/+0x14 nonnegative-owner form. The EDI context is retained for call-boundary consistency and is not consumed by the current body. Static retail decompile/xref evidence only; exact record layout, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "triangle-record", "owner-field-stamp", "candidate-batches")
            ),
            new Spec(
                "0x005708a0",
                "CFastVB__InsertStripCandidatesIntoBuffer_005708a0",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("primary_candidate_span", voidPtr),
                    param("secondary_candidate_span", voidPtr),
                    param("edi_context", voidPtr)
                },
                "Wave651 CFastVB strip-selection hardening: thiscall helper inserts secondary strip candidates in reverse order into this+0x0c, then grows/shifts the main pointer buffer at this+0x10/+0x14/+0x18 while inserting primary candidates. The trailing EDI context is retained for observed callsites and allocator helper calls. Static retail decompile/xref evidence only; exact container layout, address-suffixed source identity, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-candidate-buffer", "pointer-span-grow", "address-suffixed-helper")
            ),
            new Spec(
                "0x00570a90",
                "CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("triangle_record", voidPtr),
                    param("edge_buckets", voidPtr),
                    param("edi_context", voidPtr)
                },
                "Wave651 CFastVB strip-selection hardening: thiscall predicate probes all three edges of triangle_record through CFastVB__FindEdgeRecord and returns a low-byte true value when either adjacent face is already stamped with this object's current owner/group id. The EDI context is retained for the observed call boundary. Static retail decompile/xref evidence only; exact pivot semantics, address-suffixed source identity, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-candidate-selection", "adjacent-face-owner-check", "address-suffixed-helper")
            ),
            new Spec(
                "0x00570be0",
                "CFastVB__InitializeCandidateParentLinks_00570be0",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_candidate_span", voidPtr),
                    param("selected_candidate_bucket", voidPtr)
                },
                "Wave651 CFastVB strip-selection hardening: stdcall helper walks selected_candidate_bucket, resets each candidate root's +0x20 parent field to 0xffffffff, appends the root pointer to out_candidate_span, then stamps child triangle records from the root's +0x10/+0x14 span with the root owner/group fields. Static retail decompile/xref evidence only; exact candidate-bucket layout, address-suffixed source identity, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "strip-candidate-links", "parent-link-initializer", "ret-0x8", "address-suffixed-helper")
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
