//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
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

public class ApplyWavReadWave537 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final String[] allowedExistingNames;
        final boolean createIfMissing;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags,
                String[] allowedExistingNames, boolean createIfMissing) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.allowedExistingNames = allowedExistingNames;
            this.createIfMissing = createIfMissing;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int created = 0;
        int wouldCreate = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "wavread-wave537",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
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
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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

    private Function createFunctionAt(Spec spec, Address address) throws Exception {
        Function containing = getFunctionContaining(address);
        if (containing != null && !containing.getEntryPoint().equals(address)) {
            throw new IllegalStateException(
                "Address " + spec.address + " is inside existing function " + containing.getName());
        }
        Function fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = getFunctionAt(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        return fn;
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
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function fn = functionAtEntry(spec.address);
        boolean createdNow = false;

        if (fn == null) {
            if (!spec.createIfMissing) {
                println("MISSING: " + spec.address);
                stats.missing++;
                return;
            }
            if (dryRun) {
                println("DRYCREATE: " + spec.address + " <missing> -> " + expectedSignature(spec));
                stats.wouldCreate++;
                stats.skipped++;
                return;
            }
            fn = createFunctionAt(spec, address);
            createdNow = true;
            stats.created++;
        }

        if (!allowedName(spec, fn.getName())) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        boolean update = createdNow || needsUpdate(fn, spec);
        if (dryRun) {
            if (needsRename) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.wouldRename++;
            } else {
                println((update ? "DRY: " : "SKIP: ") + spec.address + " " + expectedSignature(spec));
            }
            stats.skipped++;
            return;
        }
        if (!update) {
            println("SKIP: " + spec.address + " already current");
            stats.skipped++;
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
        println("OK: " + spec.address + " " + functionAtEntry(spec.address).getSignature() +
            (createdNow ? " created" : ""));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType voidPtrPtr = new PointerDataType(voidPtr);
        DataType byteType = ByteDataType.dataType;
        DataType bytePtr = new PointerDataType(byteType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType uintPtr = new PointerDataType(uintType);
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00505210",
                "WavRead__ReadMMIO",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("hmmio", voidPtr),
                    param("riff_chunk", voidPtr),
                    param("wave_format_out", voidPtrPtr)
                },
                "Wave537 WavRead signature/comment hardening: cdecl stack use and the mmioDescend/mmioRead/mmioAscend sequence identify the DirectX-style RIFF/WAVE fmt parser. The body validates RIFF/WAVE/fmt tokens, allocates WAVEFORMATEX storage from wavread.cpp line 0x3d/0x4b provenance, copies the fixed 16-byte header plus optional extension bytes, writes the WAVEFORMATEX pointer through wave_format_out, and frees it on late failure. Static retail evidence only; exact SDK source identity, runtime WAV acceptance behavior, allocator ownership, and rebuild parity remain unproven.",
                tags("wavread", "riff-wave", "mmio", "format-parser"),
                new String[] {},
                false
            ),
            new Spec(
                "0x005053d0",
                "WavRead__WaveReadFile",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("hmmio", voidPtr),
                    param("byte_count", uintType),
                    param("out_buffer", bytePtr),
                    param("data_chunk", voidPtr),
                    param("bytes_read_out", uintPtr)
                },
                "Wave537 WavRead signature/comment hardening: cdecl stack use and the mmioGetInfo/mmioAdvance/mmioSetInfo sequence identify the buffered data reader. The body clamps byte_count to data_chunk+0x04 remaining bytes, decrements that remaining count, copies bytes into out_buffer, advances the MMIO buffer when exhausted, writes the actual byte count through bytes_read_out, and returns 0 or E_FAIL. Static retail evidence only; runtime sample decoding, concrete MMCKINFO layout naming, and rebuild parity remain unproven.",
                tags("wavread", "mmio", "data-reader", "buffer-copy"),
                new String[] {},
                false
            ),
            new Spec(
                "0x005054a0",
                "CWaveSoundRead__Constructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave537 CWaveSoundRead boundary/signature hardening: register-only constructor installs vtable 0x005dfc4c and clears the WAVEFORMATEX pointer at this+0x04. Static retail evidence only; concrete object layout, exact source identity, runtime audio behavior, and rebuild parity remain unproven.",
                tags("wavread", "constructor", "vtable-readback"),
                new String[] {},
                false
            ),
            new Spec(
                "0x005054b0",
                "CWaveSoundRead__HasFormat",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave537 CWaveSoundRead vtable-boundary recovery: vtable 0x005dfc4c slot 4 points here. The register-only helper returns whether the WAVEFORMATEX pointer at this+0x04 is non-null. Static retail evidence only; method name is behavior-derived and exact source identity, runtime use, and rebuild parity remain unproven.",
                tags("wavread", "created-function", "vtable-readback", "format-state"),
                new String[] {},
                true
            ),
            new Spec(
                "0x005054c0",
                "CWaveSoundRead__GetSampleRate",
                "__fastcall",
                uintType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave537 CWaveSoundRead vtable-boundary recovery: vtable 0x005dfc4c slot 5 points here. The register-only helper returns the dword at WAVEFORMATEX+0x04 from the format pointer at this+0x04, matching the nSamplesPerSec field for PCM WAVEFORMATEX. Static retail evidence only; runtime caller expectations, null-format behavior, and rebuild parity remain unproven.",
                tags("wavread", "created-function", "vtable-readback", "format-field"),
                new String[] {},
                true
            ),
            new Spec(
                "0x005054d0",
                "CWaveSoundRead__GetChannelCount",
                "__fastcall",
                uintType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave537 CWaveSoundRead vtable-boundary recovery: vtable 0x005dfc4c slot 6 points here. The register-only helper zero-extends the word at WAVEFORMATEX+0x02 from the format pointer at this+0x04, matching the nChannels field. Static retail evidence only; runtime caller expectations, null-format behavior, and rebuild parity remain unproven.",
                tags("wavread", "created-function", "vtable-readback", "format-field"),
                new String[] {},
                true
            ),
            new Spec(
                "0x005054e0",
                "CWaveSoundRead__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("delete_flags", byteType)},
                "Wave537 CWaveSoundRead rename/signature/comment hardening: vtable 0x005dfc4c slot 0 points here, RET 0x4 proves one stack delete_flags byte after ECX this, and the body calls CWaveSoundRead__Close before optionally freeing this through the global CDXMemoryManager when bit 0 is set. Static retail evidence only; allocator ownership, exact source identity, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("wavread", "destructor", "scalar-deleting-destructor", "renamed", "vtable-readback"),
                new String[] {"CWaveSoundRead__Destructor"},
                false
            ),
            new Spec(
                "0x00505500",
                "CWaveSoundRead__Close",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave537 CWaveSoundRead signature/comment hardening: register-only close helper installs the concrete vtable, closes the HMMIO handle at this+0x08 through the mmio close import, frees the WAVEFORMATEX pointer at this+0x04 when present, clears that pointer, then restores the base vtable 0x005dfc6c. Static retail evidence only; handle validity behavior, exact exception-unwind semantics, source identity, and rebuild parity remain unproven.",
                tags("wavread", "close", "mmio", "vtable-transition"),
                new String[] {},
                false
            ),
            new Spec(
                "0x00505570",
                "CWaveSoundRead__BaseConstructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave537 CWaveSoundRead signature/comment hardening: register-only base constructor installs base vtable 0x005dfc6c. Vtable read-back shows the base table has a scalar-deleting destructor followed by purecall slots. Static retail evidence only; base class source identity, concrete layout, and rebuild parity remain unproven.",
                tags("wavread", "constructor", "base-vtable", "vtable-readback"),
                new String[] {},
                false
            ),
            new Spec(
                "0x00505580",
                "CWaveSoundRead__BaseScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("delete_flags", byteType)},
                "Wave537 CWaveSoundRead vtable-boundary recovery: base vtable 0x005dfc6c slot 0 points here. RET 0x4 and the delete_flags bit test identify a base scalar deleting destructor wrapper that restores vtable 0x005dfc6c, optionally frees this through the global CDXMemoryManager, and returns this. Static retail evidence only; base-class ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("wavread", "created-function", "destructor", "scalar-deleting-destructor", "base-vtable", "vtable-readback"),
                new String[] {},
                true
            ),
            new Spec(
                "0x005055b0",
                "CWaveSoundRead__Open",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("filename", charPtr)},
                "Wave537 CWaveSoundRead signature/comment hardening: RET 0x4 proves one filename stack argument after ECX this. The body frees any prior WAVEFORMATEX pointer, copies the filename through the rotating temp-buffer helper, opens the file with mmioOpenA mode 0x10000, parses RIFF/WAVE/fmt through WavRead__ReadMMIO, stores the HMMIO handle at this+0x08, seeks to the RIFF data offset plus 4, and descends into the data chunk at this+0x0c. Static retail evidence only; runtime file-path behavior, supported WAV variants, and rebuild parity remain unproven.",
                tags("wavread", "open", "mmio", "riff-wave", "vtable-readback"),
                new String[] {},
                false
            ),
            new Spec(
                "0x00505680",
                "CWaveSoundRead__Read",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("byte_count", uintType),
                    param("out_buffer", bytePtr),
                    param("bytes_read_out", uintPtr)
                },
                "Wave537 CWaveSoundRead vtable-boundary recovery: vtable 0x005dfc4c slot 2 points here and RET 0x0c proves three stack arguments after ECX this. The wrapper forwards this+0x08 HMMIO, byte_count, out_buffer, this+0x0c data chunk, and bytes_read_out into WavRead__WaveReadFile. Static retail evidence only; runtime sample-read behavior, source identity, and rebuild parity remain unproven.",
                tags("wavread", "created-function", "read-wrapper", "mmio", "vtable-readback"),
                new String[] {},
                true
            ),
            new Spec(
                "0x005056b0",
                "CWaveSoundRead__CloseHandle",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave537 CWaveSoundRead vtable-boundary recovery: vtable 0x005dfc4c slot 3 points here. The register-only helper calls the mmio close import for the HMMIO handle at this+0x08 with flags 0, then returns 0 without freeing the WAVEFORMATEX pointer. Static retail evidence only; behavior-derived method name, runtime caller contract, source identity, and rebuild parity remain unproven.",
                tags("wavread", "created-function", "mmio", "handle-close", "vtable-readback"),
                new String[] {},
                true
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " created=" + stats.created + " would_create=" + stats.wouldCreate +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave537 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
