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

public class ApplyInflateUtilityHeadWave731 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
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

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "inflate-utility-head-wave731",
            "wave731-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "inflate-utility-head"
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
            boolean needsSignature = !signatureMatches(fn, spec);
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
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                SourceType.USER_DEFINED, spec.parameters);
            if (needsSignature) {
                stats.signatureUpdated++;
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

        return new Spec[] {
            new Spec(
                "0x005b1e16",
                "CDXTexture__InflateBuildFixedHuffmanTables",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("inflate_stream", voidPtr),
                    param("state_callback", voidPtr),
                    param("window_size_bytes", uintType)
                },
                "Wave731 static read-back: allocates and initializes inflate fixed-Huffman/window state through the stream allocator callbacks. RET 0xc caller CDXTexture__InflateInitStateFromHeader passes inflate_stream, state_callback, and window_size_bytes; the helper allocates a 0x40-byte state, a 0x5a0-byte fixed Huffman table, and a window buffer sized by window_size_bytes, stores the state callback at +0x38, sets the window end at +0x2c, calls CDXTexture__ResetDecodeWindowState, and returns the state pointer or null. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact z_stream layout, inflate-state layout, callback ABI, runtime inflate behavior, BEA patching, and rebuild parity remain unproven.",
                tags("tranche-head", "fixed-huffman-tables", "inflate-state-allocation", "ret-0xc")
            ),
            new Spec(
                "0x005b1e94",
                "CDXTexture__InflateProcessBlockHeader",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("inflate_state", voidPtr),
                    param("inflate_stream", voidPtr),
                    param("status_code", intType)
                },
                "Wave731 static read-back: zlib inflate block-state machine used by CDXTexture__InflateStream_ProcessZlibState. RET 0xc caller passes inflate_state, inflate_stream, and a status/flush code, then consumes the returned EAX zlib-style status; the helper reads input and bit-buffer state, dispatches stored, fixed-Huffman, and dynamic-Huffman block paths, builds bit-length/literal-distance trees, invokes output-window flush/codes-state helpers, writes stream error messages such as \"invalid block type\" and \"too many length or distance symbols\", and narrows the prior caller extraout_EAX uncertainty for this helper to an int status return. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact z_stream layout, inflate-state layout, downstream helper ABIs, runtime inflate behavior, BEA patching, and rebuild parity remain unproven.",
                tags("inflate-block-state-machine", "dynamic-huffman", "stored-fixed-dynamic-blocks", "ret-0xc")
            ),
            new Spec(
                "0x005b25e0",
                "CDXTexture__CloseAsyncDecodeHandles",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("inflate_state", voidPtr),
                    param("inflate_stream", voidPtr)
                },
                "Wave731 static read-back: releases inflate/window allocations during async decode cleanup. RET 0x8 caller CDXTexture__FinishAsyncDecodeJob passes inflate_state and inflate_stream; the helper resets decode-window state, frees the window buffer at inflate_state +0x28, frees the fixed/dynamic table buffer at +0x24, frees the inflate_state object through the stream free callback and opaque pointer, then returns 0. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact allocator ownership, inflate-state layout, cleanup ordering side effects, runtime decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("inflate-state-release", "async-decode-cleanup", "ret-0x8")
            ),
            new Spec(
                "0x005b2613",
                "CDXTexture__Adler32_Update",
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("adler", uintType),
                    param("source_buffer", voidPtr),
                    param("byte_count", uintType)
                },
                "Wave731 static read-back: Adler-32 checksum update helper referenced by inflate initialization. RET 0xc inputs are adler, source_buffer, and byte_count; null source returns the initial checksum 1, non-null input updates s1/s2 over chunks capped at 0x15b0 bytes, uses an unrolled 16-byte loop, reduces both accumulators modulo 0xfff1, and returns the packed checksum. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact zlib source identity, runtime checksum behavior, BEA patching, and rebuild parity remain unproven.",
                tags("adler32", "zlib-checksum", "mod-0xfff1", "ret-0xc")
            ),
            new Spec(
                "0x005b272e",
                "CDXTexture__InflateDefaultAllocCallback",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("opaque", voidPtr),
                    param("item_count", uintType),
                    param("item_size", uintType)
                },
                "Wave731 static read-back: default inflate allocator callback installed by CDXTexture__InflateInitStateFromHeader. RET 0xc inputs are opaque, item_count, and item_size; opaque is unused, the helper multiplies item_count by item_size, calls GetProcessHeap, allocates with HeapAlloc flag 8, and returns the allocated pointer in EAX. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact allocator ownership/lifetime, overflow behavior, runtime heap behavior, BEA patching, and rebuild parity remain unproven.",
                tags("tranche-tail", "inflate-allocator-callback", "heapalloc", "ret-0xc")
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

        println("ApplyInflateUtilityHeadWave731 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave731 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
