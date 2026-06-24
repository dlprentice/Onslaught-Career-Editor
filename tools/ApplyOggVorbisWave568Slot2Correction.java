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

public class ApplyOggVorbisWave568Slot2Correction extends GhidraScript {
    private static final String ADDRESS = "0x00524710";
    private static final String NAME = "COggFileRead__ReadDecodedPcm";
    private static final String COMMENT =
        "Wave568 recovered vtable slot 2 boundary: reads decoded PCM bytes from either an open file stream or an in-memory Ogg buffer. " +
        "It validates input availability, then pushes the first stack argument as the requested byte count and the second stack argument as the output buffer before calling OggVorbisStream__ReadPcmSamples; " +
        "it writes the returned byte count through out_bytes_read and returns 0 or 0x80004005-style failure. Static retail evidence only; exact COM-style contract, buffer ownership, runtime playback behavior, and rebuild parity remain unproven.";
    private static final String[] TAGS = {
        "static-reaudit",
        "ogg-vorbis-wave568",
        "retail-binary-evidence",
        "ogg-file-read",
        "vtable-slot",
        "function-boundary",
        "pcm-decode",
        "boundary-recovered",
        "argument-order-corrected",
        "signature-corrected",
        "comment-hardened"
    };
    private static final String[] PARAM_NAMES = {
        "this",
        "requested_byte_count",
        "out_pcm_bytes",
        "out_bytes_read"
    };
    private static final String[] PARAM_TYPES = {
        "void *",
        "uint",
        "void *",
        "int *"
    };

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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean matches(Function fn) {
        if (!NAME.equals(fn.getName())) {
            return false;
        }
        if (!COMMENT.equals(fn.getComment())) {
            return false;
        }
        Parameter[] params = fn.getParameters();
        if (params.length != PARAM_NAMES.length) {
            return false;
        }
        for (int i = 0; i < PARAM_NAMES.length; i++) {
            if (!PARAM_NAMES[i].equals(params[i].getName())) {
                return false;
            }
            if (!PARAM_TYPES[i].equals(params[i].getDataType().getDisplayName())) {
                return false;
            }
        }
        Set<String> presentTags = tagNames(fn);
        for (String tag : TAGS) {
            if (!presentTags.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private ParameterImpl[] parameters() throws Exception {
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("requested_byte_count", uintType),
            param("out_pcm_bytes", voidPtr),
            param("out_bytes_read", intPtr)
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        Function fn = getFunctionAt(addr(ADDRESS));
        if (fn == null) {
            println("SUMMARY updated=0 skipped=0 would_update=0 missing=1 bad=0");
            throw new IllegalStateException("Function not found at " + ADDRESS);
        }
        if (!NAME.equals(fn.getName())) {
            println("SUMMARY updated=0 skipped=0 would_update=0 missing=0 bad=1");
            throw new IllegalStateException("Unexpected function name at " + ADDRESS + ": " + fn.getName());
        }

        if (dryRun) {
            if (matches(fn)) {
                println("DRY: " + ADDRESS + " already matches corrected slot-2 signature/comment/tags");
                println("SUMMARY updated=0 skipped=1 would_update=0 missing=0 bad=0");
            } else {
                println("DRY: " + ADDRESS + " -> int __thiscall COggFileRead__ReadDecodedPcm(void * this, uint requested_byte_count, void * out_pcm_bytes, int * out_bytes_read)");
                println("SUMMARY updated=0 skipped=0 would_update=1 missing=0 bad=0");
            }
            return;
        }

        fn.setCallingConvention("__thiscall");
        fn.setReturnType(IntegerDataType.dataType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            parameters()
        );
        fn.setComment(COMMENT);
        for (String tag : TAGS) {
            fn.addTag(tag);
        }

        Function readBack = getFunctionAt(addr(ADDRESS));
        if (readBack == null || !matches(readBack)) {
            println("SUMMARY updated=0 skipped=0 would_update=0 missing=0 bad=1");
            throw new IllegalStateException("Read-back mismatch after slot-2 correction");
        }
        println("OK: " + ADDRESS + " " + readBack.getSignature());
        println("SUMMARY updated=1 skipped=0 would_update=0 missing=0 bad=0");
        Thread.sleep(50);
    }
}
