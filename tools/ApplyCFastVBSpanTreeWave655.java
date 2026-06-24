//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyCFastVBSpanTreeWave655 extends GhidraScript {
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
            "cfastvb-span-tree-wave655",
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
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00572f00",
                "CFastVB__InitDwordSpanBuilderState_00572f00",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_flag", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: thiscall initializer copies one byte from source_flag into the span-builder state, clears begin/current/end pointer slots at +0x04/+0x08/+0x0c, and ignores the trailing context argument. Static retail decompile/xref evidence only; exact STL/vector type identity, runtime strip quality, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "span-builder", "dword-span", "address-suffixed-helper")
            ),
            new Spec(
                "0x00572f20",
                "CFastVB__AppendDwordRangeToSpanBuilder_00572f20",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("dest_cursor", voidPtr),
                    param("range_cursor", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: thiscall append helper copies dwords from range_cursor up to the span-builder current pointer at this+0x08 into dest_cursor, then stores the advanced cursor back at this+0x08. Xrefs are from triangle-adjacency and strip-batch merge paths. Static retail evidence only; concrete span layout and runtime behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "span-builder", "dword-copy", "triangle-adjacency", "address-suffixed-helper")
            ),
            new Spec(
                "0x00572f50",
                "CFastVB__CopyDwordRange",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("range_start", voidPtr),
                    param("range_end", voidPtr),
                    param("dest_or_null", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: stdcall dword range copy walks [range_start, range_end) in 4-byte steps and copies each dword when dest_or_null is non-null. Used by triangle adjacency, strip-index emission, candidate insertion, and grow-insert helpers. Static retail decompile/xref evidence only; concrete container layout and runtime strip output remain unproven.",
                new String[] {},
                tags("cfastvb", "dword-copy", "span-copy", "strip-pipeline", "ret-0xc")
            ),
            new Spec(
                "0x00572f80",
                "CFastVB__GetWordCapacity",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("span_state", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: fastcall helper returns zero for an unallocated word span, otherwise returns (end - begin) / 2 using fields at +0x04 and +0x0c. CFastVB__BuildStripBatchesFromIndexBuffer uses it as capacity evidence. Static retail evidence only; exact vector type and runtime behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "word-span", "capacity", "strip-pipeline")
            ),
            new Spec(
                "0x00572fa0",
                "CFastVB__InsertWordAndGrow",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("insert_at", voidPtr),
                    param("value_ptr", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: thiscall word-span insert helper shifts existing 16-bit elements when capacity remains, otherwise allocates a larger buffer, copies the prefix/value/suffix, invokes the cleanup callback for the old span, frees old storage, updates begin/current/end fields, and returns the inserted element pointer. Static retail evidence only; exact vector type, allocator ownership, runtime strip quality, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "word-span", "insert-grow", "allocation", "strip-pipeline")
            ),
            new Spec(
                "0x00573140",
                "CFastVB__CopyWordRange",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("range_start", voidPtr),
                    param("range_end", voidPtr),
                    param("dest_or_null", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: stdcall word range copy walks [range_start, range_end) in 2-byte steps and copies each word when dest_or_null is non-null. Used by strip-batch building and word-span grow-insert paths. Static retail decompile/xref evidence only; concrete container layout and runtime output remain unproven.",
                new String[] {},
                tags("cfastvb", "word-span", "word-copy", "strip-pipeline", "ret-0xc")
            ),
            new Spec(
                "0x00573170",
                "CFastVB__InsertDwordAndGrow",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("insert_at", voidPtr),
                    param("value_ptr", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: thiscall dword-span insert helper shifts existing 32-bit elements when capacity remains, otherwise allocates a larger buffer, copies prefix/value/suffix, runs the cleanup callback for the old span, frees old storage, updates begin/current/end fields, and returns the inserted element pointer. Xrefs are from strip construction and batch merge paths. Static retail evidence only; exact span layout and runtime strip behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "dword-span", "insert-grow", "allocation", "strip-pipeline")
            ),
            new Spec(
                "0x00573310",
                "CFastVB__CountDwordsFromPointerSpan",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("span_state", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: fastcall helper returns zero for an unallocated dword span, otherwise returns (current - begin) / 4 using fields at +0x04 and +0x08. Used by adjacency, strip-index emission, candidate insertion, and dword grow-insert callers. Static retail evidence only; exact container type and runtime behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "dword-span", "span-count", "strip-pipeline")
            ),
            new Spec(
                "0x00573330",
                "CFastVB__GetTreeRootNode_00573330",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_node_slot", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: thiscall tree helper writes the root node from the header stored at this+0x04 into out_node_slot. Xrefs are from candidate-generation cleanup and CTexture tree-destruction cleanup. Static retail evidence only; exact tree owner/template identity and runtime behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "red-black-tree", "tree-root", "shared-sentinel", "address-suffixed-helper")
            ),
            new Spec(
                "0x00573340",
                "CFastVB__InsertNodeIntoRBTreeWithHint_00573340",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_insert_result", voidPtr),
                    param("key_ptr", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: thiscall uint-key red-black-tree insert helper searches by key_ptr, allocates/inserts a 0x14-byte node through the shared sentinel DAT_009d0c44 when insertion is allowed, writes the inserted/existing node and inserted flag to out_insert_result, and runs insert-fixup rotations/recolors. Static retail evidence only; exact owner/template identity, concrete node layout, runtime strip behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "red-black-tree", "insert-node", "uint-key", "shared-sentinel", "address-suffixed-helper")
            ),
            new Spec(
                "0x00573560",
                "CFastVB__EraseNodeRangeFromRBTree_00573560",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_next_slot", voidPtr),
                    param("first_node", voidPtr),
                    param("last_node", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: thiscall erase-range helper either clears the full sentinel-backed tree or iterates from first_node to last_node, destroys subtrees when needed, calls CTexture__EraseNodeFromTree for each erased node, and writes the next iterator node to out_next_slot. Static retail evidence only; exact tree owner/template identity, node payload ownership, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cfastvb", "red-black-tree", "erase-range", "shared-sentinel", "address-suffixed-helper")
            ),
            new Spec(
                "0x00573630",
                "RBTree__FindLowerBoundByUIntKey",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_node_slot", voidPtr),
                    param("key_ptr", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: thiscall lower-bound helper walks the sentinel-backed uint-key red-black tree, tracks the first node whose key is not less than key_ptr, and writes either that node or the header sentinel to out_node_slot. Current xref is from strip-candidate generation. Static retail evidence only; exact owner/template identity and runtime behavior remain unproven.",
                new String[] {},
                tags("red-black-tree", "lower-bound", "uint-key", "shared-sentinel", "strip-generation")
            ),
            new Spec(
                "0x005736a0",
                "MemCopyU16Elements",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("dest_or_null", voidPtr),
                    param("element_count", intType),
                    param("value_ptr", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: retained-name stdcall helper writes the same 16-bit value from value_ptr into dest_or_null for element_count slots, advancing the destination by two bytes and skipping writes when the destination is null. Static retail decompile/xref evidence only; helper naming provenance and runtime behavior remain unproven.",
                new String[] {},
                tags("word-span", "fill-helper", "ret-0xc", "retained-name")
            ),
            new Spec(
                "0x005736d0",
                "CFastVB__InsertDwordSpanFilled",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("insert_at", voidPtr),
                    param("element_count", intType),
                    param("value_ptr", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: thiscall dword-span fill-insert helper inserts element_count copies of the dword referenced by value_ptr, shifting in-place when capacity allows or allocating a larger buffer and copying prefix/fill/suffix when growth is required. Xrefs are from strip-index emission, adjacency, merge, candidate generation, and parent-link initialization. Static retail evidence only; exact span layout and runtime strip behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "dword-span", "fill-insert", "allocation", "strip-pipeline")
            ),
            new Spec(
                "0x00573d00",
                "RBTree__InitUIntKeyTreeWithSharedSentinel",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("tree_state", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: fastcall initializer creates or reuses the shared sentinel DAT_009d0c44, increments the sentinel refcount, allocates a 0x14-byte header node, stores it at tree_state+0x04, clears the count at +0x0c, and initializes header root/min/max links. Static retail evidence only; exact tree owner/template identity and runtime behavior remain unproven.",
                new String[] {},
                tags("red-black-tree", "init-tree", "uint-key", "shared-sentinel", "strip-generation")
            ),
            new Spec(
                "0x00573ff0",
                "CFastVB__FillDwordSpanWithValue_00573ff0",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("dest_or_null", voidPtr),
                    param("element_count", intType),
                    param("value_ptr", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: stdcall fill helper writes the dword referenced by value_ptr into dest_or_null for element_count slots, advancing by four bytes and skipping writes when the destination is null. Used by adjacency, strip emission, candidate insertion, and dword grow-insert callers. Static retail evidence only; concrete container layout and runtime output remain unproven.",
                new String[] {},
                tags("cfastvb", "dword-span", "fill-helper", "strip-pipeline", "address-suffixed-helper")
            ),
            new Spec(
                "0x00574020",
                "CFastVB__RBTreeRotateLeft_00574020",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("pivot_node", voidPtr),
                    param("unused_context", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: thiscall red-black-tree left-rotation helper pivots pivot_node's right child up, updates parent/root/header links, and preserves DAT_009d0c44 child checks. Xrefs are from CFastVB__InsertNodeIntoRBTreeWithHint_00573340 insert-fixup paths. Static retail evidence only; exact tree owner/template identity and runtime behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "red-black-tree", "left-rotate", "insert-fixup", "shared-sentinel", "address-suffixed-helper")
            ),
            new Spec(
                "0x005741d0",
                "CFastVB__CopyWordRange_Strict",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("range_start", voidPtr),
                    param("range_end", voidPtr),
                    param("dest", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: cdecl strict word copy walks [range_start, range_end) in 2-byte steps and unconditionally copies each word to dest. Xrefs are from strip-batch building. Static retail evidence only; exact span type and runtime behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "word-span", "strict-copy", "strip-pipeline")
            ),
            new Spec(
                "0x00574200",
                "CFastVB__CopyDwordRange_Strict",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("range_start", voidPtr),
                    param("range_end", voidPtr),
                    param("dest", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: cdecl strict dword copy walks [range_start, range_end) in 4-byte steps and unconditionally copies each dword to dest. Current xref is from CFastVB__MergeAndOrderStripBatches. Static retail evidence only; exact span type and runtime behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "dword-span", "strict-copy", "strip-pipeline")
            ),
            new Spec(
                "0x00574230",
                "CFastVB__AssignDwordIfDestNotNull",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("dest_or_null", voidPtr),
                    param("source_value", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: cdecl assignment helper copies one dword from source_value to dest_or_null when the destination pointer is non-null. Xrefs are from dword grow-insert, tree insert, CTexture tree insert, and strip-index emission paths. Static retail evidence only; exact helper provenance and runtime behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "dword-copy", "assign-if-dest", "strip-pipeline")
            ),
            new Spec(
                "0x00574250",
                "CFastVB__AssignWordIfDestNotNull",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("dest_or_null", voidPtr),
                    param("source_value", voidPtr)
                },
                "Wave655 CFastVB span/tree utility hardening: cdecl assignment helper copies one word from source_value to dest_or_null when the destination pointer is non-null. Current xrefs are from word-span grow-insert paths. Static retail evidence only; exact helper provenance and runtime behavior remain unproven.",
                new String[] {},
                tags("cfastvb", "word-copy", "assign-if-dest", "strip-pipeline")
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
