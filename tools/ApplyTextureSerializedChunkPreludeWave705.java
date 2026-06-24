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

public class ApplyTextureSerializedChunkPreludeWave705 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final boolean updateSignature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, boolean updateSignature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.updateSignature = updateSignature;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] signatureTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "texture-serialized-chunk-prelude-wave705",
            "wave705-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "texture-serialized-chunk-prelude-wave705",
            "wave705-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only"
        }, extras);
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
        if (!spec.updateSignature) {
            return true;
        }
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

    private String expectedSignature(Spec spec) {
        if (!spec.updateSignature) {
            return "<comment/tag-only; saved signature intentionally unchanged>";
        }
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
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsSignature = spec.updateSignature && !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                if (!spec.updateSignature) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
            }
            else {
                stats.commentOnlyUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + expectedSignature(spec));
            Thread.sleep(75);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType uintPtr = new PointerDataType(UnsignedIntegerDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x0059902a",
                "CDXTexture__RegisterSerializedChunk",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave705 static read-back: hidden-ECX serialized-chunk registry helper validates pointer/length input, handles the 0xffffffff string-length sentinel, deduplicates existing flag-bit-1 records by byte length/content, allocates a 0x14 record, copies or adopts chunk bytes based on flag bit 0, aligns the stream cursor unless flag bit 2 is set, appends through the tail link at +0xc, and writes an optional output offset. Signature intentionally left unchanged because Ghidra reports unknown calling convention with locked storage. Static metadata only; exact chunk-builder layout, flag enum, ownership policy, parser/source identity, runtime texture behavior, and rebuild parity remain unproven.",
                commentOnlyTags("serialized-chunk", "chunk-registry", "dedupe", "hidden-ecx", "locked-storage", "tranche-head")
            ),
            new Spec(
                "0x00599161",
                "CTexture__ComputeDebugChunkDwordCount",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("chunk_builder", voidPtr) },
                true,
                "Wave705 static read-back: computes the serialized debug chunk dword count as ((chunk_builder + 4 byte_count + 3) >> 2) + 2, matching the 0xfffe debug-chunk header plus aligned payload storage used by the adjacent serializer. Static metadata only; exact builder layout, chunk format ownership, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("serialized-chunk", "debug-chunk", "dword-count", "fastcall-param-named")
            ),
            new Spec(
                "0x0059916d",
                "CTexture__SerializeDebugChunkSymbolRecords",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_chunk_dwords", uintPtr),
                    param("max_dword_count", uintType)
                },
                true,
                "Wave705 static read-back: serializes chunk-builder records into an output dword buffer by deriving or validating the required dword count, writing the 0xfffe chunk header and first builder dword, copying record bytes from the +0x8 list, and filling alignment/trailing padding with 0xab/0xabababab. RET 0x8 evidence removes the unused phantom decompiler parameter. Static metadata only; exact record schema, output contract, parser/source identity, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("serialized-chunk", "debug-chunk", "symbol-records", "padding", "phantom-param-removed")
            ),
            new Spec(
                "0x00599258",
                "CFastVB__ComputeNodeSpanAndStride",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("node_tree", voidPtr),
                    param("out_span", uintPtr),
                    param("out_stride", uintPtr)
                },
                true,
                "Wave705 static read-back: recursively computes node-tree span and stride for node kinds 8, 7, and 1; kind 8 uses mode 0/1 scalar width or mode 2 span/stride fields, kind 7 multiplies child stride by +0x14, and kind 1 walks a chained child tree while accumulating span and max stride. A null out_stride uses a local fallback. Static metadata only; exact node-type enum, field schema, runtime vertex-buffer behavior, and rebuild parity remain unproven.",
                signatureTags("node-tree", "span-stride", "recursive", "stdcall-params-named")
            ),
            new Spec(
                "0x0059930d",
                "CTexture__ValidateConstantRegisterDeclarationType",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("match_template_words32", voidPtr),
                    param("register_decl", voidPtr),
                    param("out_component_count", uintPtr)
                },
                true,
                "Wave705 static read-back: copies an eight-dword match template, points the match key at register_decl + 2, calls CFastVB__SelectBestNodeTreeMatch, computes the declaration node span/stride, and validates bool/int constant-register declarations, appending diagnostics 0xb54 or 0xb55 when the node type does not match bool-only or int3/int4 expectations. RET 0xc evidence removes the unused phantom decompiler parameter. Static metadata only; exact declaration layout, token enum, selected-node ABI, runtime shader/texture behavior, and rebuild parity remain unproven.",
                signatureTags("constant-register", "node-tree", "diagnostic", "phantom-param-removed")
            ),
            new Spec(
                "0x00599406",
                "CDXTexture__SerializeFloatGridChunk",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("chunk_builder", voidPtr),
                    param("row_count", uintType),
                    param("column_count", uintType),
                    param("value_source", voidPtr),
                    param("out_chunk_offset", uintPtr)
                },
                true,
                "Wave705 static read-back: serializes a float-grid chunk by unwrapping kind 0xc sources to +0x20, requiring a kind-1 value node chain, allocating row_count * 16 bytes, zero-filling the temporary buffer, copying float values or narrowing double payloads, registering chunk kind 6 through CDXTexture__RegisterSerializedChunk, and freeing the temporary buffer. RET 0x14 evidence restores the fifth stack argument as out_chunk_offset. Static metadata only; exact value-node layout, chunk kind enum, runtime texture behavior, and rebuild parity remain unproven.",
                signatureTags("serialized-chunk", "float-grid", "chunk-kind-6", "ret-0x14", "arity-restored")
            ),
            new Spec(
                "0x005994c4",
                "CDXTexture__ProcessTextureChunkAndEmitBindings",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave705 static read-back: locked-storage texture binding emitter classifies float/bool/int token globals versus raw chunks, selects a node tree, computes span/stride, binds constant-register suffixes up to 8191 into the output record, optionally serializes a float-grid chunk and node tree bitstream, registers the final binding chunk, and writes output header fields at +4/+6/+8. Signature intentionally left unchanged because Ghidra reports unknown calling convention with locked storage. Static metadata only; exact stack ABI, token enum, binding record layout, runtime shader/texture behavior, and rebuild parity remain unproven.",
                commentOnlyTags("texture-binding", "constant-register", "serialized-chunk", "hidden-stack", "locked-storage", "tranche-tail")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        println("ApplyTextureSerializedChunkPreludeWave705 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
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
    }
}
