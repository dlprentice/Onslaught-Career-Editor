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

public class ApplyAlignedWindowPreludeWave730 extends GhidraScript {
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
            "aligned-window-prelude-wave730",
            "wave730-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "aligned-window-prelude"
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
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x005b1c00",
                "CDXTexture__AllocAligned16",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("allocator_owner", voidPtr),
                    param("requested_size_bytes", uintType)
                },
                "Wave730 static read-back: aligned allocation callback used by the decode allocator helpers. RET 0x8 callers push allocator_owner and requested_size_bytes, the helper calls malloc(requested_size_bytes + 0x10), returns a 16-byte-aligned payload pointer in EAX, and stores the base-pointer byte delta at aligned_payload - 1 for CDXTexture__FreeAligned16. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact allocator-owner layout, lifetime policy, failure semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("tranche-head", "aligned-allocator", "decode-allocator-callback", "ret-0x8")
            ),
            new Spec(
                "0x005b1c30",
                "CDXTexture__FreeAligned16",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("allocator_owner", voidPtr),
                    param("aligned_payload", voidPtr),
                    param("tracked_size_bytes", uintType)
                },
                "Wave730 static read-back: aligned free callback paired with CDXTexture__AllocAligned16. RET 0xc callers pass allocator_owner, aligned_payload, and tracked_size_bytes; the helper uses the aligned payload argument, reads the byte delta from aligned_payload - 1, subtracts it to recover the original malloc base pointer, and frees that base through CRT__FreeBase. The tracked byte count is part of the callback ABI and is accounted by callers. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact allocator-owner layout, ownership/lifetime semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("aligned-free", "decode-allocator-callback", "ret-0xc")
            ),
            new Spec(
                "0x005b1c50",
                "CDXTexture__GetBufferTailAvailable",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("allocator_owner", voidPtr),
                    param("row_count_hint", intType),
                    param("minimum_chunk_bytes", intType),
                    param("committed_size_bytes", intType)
                },
                "Wave730 static read-back: byte-budget helper used by the row-allocation prelude before host I/O callbacks are installed. RET 0x10 caller context at 0x0059bf5a pushes allocator_owner, row_count_hint, minimum_chunk_bytes, and committed_size_bytes; the helper reads the decode allocator state at allocator_owner +4, loads the budget/cap field at state +0x2c, and returns budget_or_cap - committed_size_bytes. The two middle arguments are part of the caller ABI but unused by this helper. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact row-batch schema, budget semantics, allocator-state layout, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("budget-tail-helper", "row-allocation-prelude", "ret-0x10")
            ),
            new Spec(
                "0x005b1d50",
                "CDXTexture__InitHostIoCallbacks",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_context", voidPtr),
                    param("host_io_callbacks", voidPtr),
                    param("window_size_bytes", uintType)
                },
                "Wave730 static read-back: initializes host I/O callback state for decode-window spill paths. RET 0xc caller context at 0x0059bfb1/0x0059c027 passes decode_context, a callback table, and window_size_bytes; the helper opens a temporary binary stream through CRT__TmpFile_OpenUniqueBinaryStream, stores the handle at callback table +0xc, reports error code 0x3f through the decode_context callback on failure, then installs the read/write/close helper entries at 0x005b1c70, 0x005b1cd0, and 0x005b1d30. The third argument is part of the setup ABI but unused by this helper. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact callback table layout, temp-file policy, error surface, runtime decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("host-io-callbacks", "temporary-stream", "decode-window", "ret-0xc")
            ),
            new Spec(
                "0x005b1da0",
                "CDXTexture__GetDefaultDecodeBudgetBytes",
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave730 static read-back: no-argument helper returning the default decode allocator budget value 1000000. The value is consumed by CDXTexture__InitDecodeAllocatorVtable before aligned allocation of the 0x54-byte allocator state. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact budget policy, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("default-decode-budget", "allocator-budget", "constant-return")
            ),
            new Spec(
                "0x005b1db0",
                "CDXTexture__ResetDecodeWindowState",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("inflate_state", voidPtr),
                    param("host_io_state", voidPtr),
                    param("previous_cookie_out", voidPtr)
                },
                "Wave730 static read-back: resets the inflate/decode output-window state before or after streaming decode work. RET 0xc callers include async-decode begin, fixed-Huffman table setup, async handle close, and zlib stream processing; the helper optionally writes inflate_state +0x3c to previous_cookie_out, releases modes 4/5 through host_io_state +0x24, releases mode 6 through CDXTexture__InvokeReleaseCallback, resets output pointers at +0x30/+0x34 to the base at +0x28, clears state/bit accumulator fields, and optionally invokes the state callback at +0x38 to refresh the cookie at +0x3c and host_io_state +0x30. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact inflate-state layout, callback ABI, mode enum, runtime zlib/decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("tranche-tail", "decode-window-reset", "inflate-state", "ret-0xc")
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

        println("ApplyAlignedWindowPreludeWave730 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave730 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
