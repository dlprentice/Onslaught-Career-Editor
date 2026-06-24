//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyImportThunksWave619 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                boolean updateSignature,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.updateSignature = updateSignature;
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

    private DataType ptr(DataType dataType) {
        return new PointerDataType(dataType);
    }

    private String expectedSignature(Spec spec) {
        if (!spec.updateSignature) {
            return "<existing signature retained>";
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "import-thunks-wave619",
            "retail-binary-evidence",
            "comment-hardened",
            "import-thunk"
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
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
                return;
            }

            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
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
        DataType voidPtr = ptr(voidType);
        DataType voidPtrPtr = ptr(voidPtr);
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = ptr(intType);
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType uintPtr = ptr(uintType);
        DataType charPtr = ptr(CharDataType.dataType);
        DataType floatTriplePtr = ptr(ptr(ptr(FloatDataType.dataType)));

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055d5e0",
                "DirectSoundCreate8",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("pcGuidDevice", voidPtr),
                    param("ppDS8", voidPtrPtr),
                    param("pUnkOuter", voidPtr)
                },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d5e0 jumps through IAT slot 0x005d802c; Windows SDK dsound.h prototype evidence gives DirectSoundCreate8(pcGuidDevice, ppDS8, pUnkOuter). Xrefs include CPCSoundManager__Init and one adjacent non-function callsite. Static retail import-thunk/API evidence only; runtime DirectSound creation, exact COM interface layout, library behavior, BEA patching, and rebuild parity remain unproven.",
                tags("directsound", "windows-sdk-prototype", "iat-005d802c", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d5e6",
                "DirectSoundEnumerateA",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("pDSEnumCallback", voidPtr),
                    param("pContext", voidPtr)
                },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d5e6 jumps through IAT slot 0x005d8028; Windows SDK dsound.h prototype evidence gives DirectSoundEnumerateA(callback, context). Xrefs include CPCSoundManager__Init. Static retail import-thunk/API evidence only; runtime device enumeration, callback target behavior, exact DirectSound object layout, BEA patching, and rebuild parity remain unproven.",
                tags("directsound", "windows-sdk-prototype", "iat-005d8028", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d5ec",
                "AVIStreamWrite",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("pavi", voidPtr),
                    param("lStart", intType),
                    param("lSamples", intType),
                    param("lpBuffer", voidPtr),
                    param("cbBuffer", intType),
                    param("dwFlags", uintType),
                    param("plSampWritten", intPtr),
                    param("plBytesWritten", intPtr)
                },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d5ec jumps through IAT slot 0x005d8018; Windows SDK Vfw.h prototype evidence gives AVIStreamWrite(pavi, start, samples, buffer, bytes, flags, out samples, out bytes). Xrefs include CDXEngine__CaptureAviFrame. Static retail import-thunk/API evidence only; runtime AVI capture, stream ownership, codec behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vfw", "windows-sdk-prototype", "iat-005d8018", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d5f2",
                "uncompress",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("dest", voidPtr),
                    param("destLen", uintPtr),
                    param("source", voidPtr),
                    param("sourceLen", uintType)
                },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d5f2 jumps through IAT slot 0x005d83b8; zlib API prototype evidence is represented with opaque byte buffers and 32-bit unsigned lengths. Xrefs include CDXMemBuffer__InitFromFile, __Skip, __Read, and __ReadLine compressed-read paths. Static retail import-thunk/API evidence only; compressed-file edge cases, zlib version, exact buffer ownership, BEA patching, and rebuild parity remain unproven.",
                tags("zlib", "external-api-prototype", "iat-005d83b8", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d5f8",
                "compress",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("dest", voidPtr),
                    param("destLen", uintPtr),
                    param("source", voidPtr),
                    param("sourceLen", uintType)
                },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d5f8 jumps through IAT slot 0x005d83bc; zlib API prototype evidence is represented with opaque byte buffers and 32-bit unsigned lengths. Xrefs include CDXMemBuffer__WriteBytes and CDXMemBuffer__Close compressed-write paths. Static retail import-thunk/API evidence only; compressed-output edge cases, zlib version, exact buffer ownership, BEA patching, and rebuild parity remain unproven.",
                tags("zlib", "external-api-prototype", "iat-005d83bc", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d5fe",
                "ogg_sync_wrote",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("oy", voidPtr), param("bytes", intType) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d5fe jumps through IAT slot 0x005d8354; libogg API prototype evidence is represented with opaque ogg_sync_state storage and a 32-bit byte count. Xrefs include OggVorbisStream__InitDecoder and OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime Ogg paging, concrete libogg version, exact stream layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d8354", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d604",
                "ogg_sync_buffer",
                true,
                "__cdecl",
                charPtr,
                new ParameterImpl[] { param("oy", voidPtr), param("size", intType) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d604 jumps through IAT slot 0x005d8358; libogg API prototype evidence is represented with opaque ogg_sync_state storage and a 32-bit request size. Xrefs include OggVorbisStream__InitDecoder and OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime Ogg buffer ownership, concrete libogg version, exact stream layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d8358", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d60a",
                "ogg_stream_packetout",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("os", voidPtr), param("op", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d60a jumps through IAT slot 0x005d8368; libogg API prototype evidence is represented with opaque ogg_stream_state and ogg_packet pointers. Xrefs include OggVorbisStream__InitDecoder and OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime Ogg packet flow, concrete libogg version, exact stream layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d8368", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d610",
                "ogg_stream_pagein",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("os", voidPtr), param("og", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d610 jumps through IAT slot 0x005d8360; libogg API prototype evidence is represented with opaque ogg_stream_state and ogg_page pointers. Xrefs include OggVorbisStream__InitDecoder and OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime Ogg page flow, concrete libogg version, exact stream layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d8360", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d616",
                "ogg_stream_init",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("os", voidPtr), param("serialno", intType) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d616 jumps through IAT slot 0x005d8364; libogg API prototype evidence is represented with opaque ogg_stream_state storage and stream serial number. Xrefs include OggVorbisStream__InitDecoder. Static retail import-thunk/API evidence only; runtime Ogg stream initialization, concrete libogg version, exact stream layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d8364", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d61c",
                "ogg_page_serialno",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("og", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d61c jumps through IAT slot 0x005d8370; libogg API prototype evidence is represented with an opaque ogg_page pointer. Xrefs include OggVorbisStream__InitDecoder. Static retail import-thunk/API evidence only; runtime Ogg page parsing, concrete libogg version, exact page layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d8370", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d622",
                "ogg_sync_pageout",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("oy", voidPtr), param("og", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d622 jumps through IAT slot 0x005d8374; libogg API prototype evidence is represented with opaque ogg_sync_state and ogg_page pointers. Xrefs include OggVorbisStream__InitDecoder and OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime Ogg page extraction, concrete libogg version, exact stream layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d8374", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d628",
                "ogg_stream_clear",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("os", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d628 jumps through IAT slot 0x005d8378; libogg API prototype evidence is represented with opaque ogg_stream_state storage. Xrefs include OggVorbisStream__ReadPcmSamples, COggFileRead__dtor_body, and COggFileRead__CloseAndReset. Static retail import-thunk/API evidence only; runtime stream cleanup, concrete libogg version, exact stream layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d8378", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d62e",
                "ogg_sync_clear",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("oy", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d62e jumps through IAT slot 0x005d8350; libogg API prototype evidence is represented with opaque ogg_sync_state storage. Xrefs include OggVorbisStream__ReadPcmSamples and COggFileRead open/close/destructor paths. Static retail import-thunk/API evidence only; runtime sync cleanup, concrete libogg version, exact stream layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d8350", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d634",
                "ogg_page_eos",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("og", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d634 jumps through IAT slot 0x005d836c; libogg API prototype evidence is represented with an opaque ogg_page pointer. Xrefs include OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime end-of-stream handling, concrete libogg version, exact page layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d836c", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d63a",
                "ogg_sync_init",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("oy", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d63a jumps through IAT slot 0x005d835c; libogg API prototype evidence is represented with opaque ogg_sync_state storage. Xrefs include OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime sync initialization, concrete libogg version, exact stream layout, BEA patching, and rebuild parity remain unproven.",
                tags("ogg", "external-api-prototype", "iat-005d835c", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d640",
                "vorbis_block_init",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("v", voidPtr), param("vb", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d640 jumps through IAT slot 0x005d8380; libvorbis API prototype evidence is represented with opaque vorbis_dsp_state and vorbis_block pointers. Xrefs include OggVorbisStream__InitDecoder. Static retail import-thunk/API evidence only; runtime decoder setup, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d8380", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d646",
                "vorbis_synthesis_init",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("v", voidPtr), param("vi", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d646 jumps through IAT slot 0x005d8384; libvorbis API prototype evidence is represented with opaque vorbis_dsp_state and vorbis_info pointers. Xrefs include OggVorbisStream__InitDecoder. Static retail import-thunk/API evidence only; runtime synthesis setup, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d8384", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d64c",
                "vorbis_synthesis_headerin",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("vi", voidPtr), param("vc", voidPtr), param("op", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d64c jumps through IAT slot 0x005d838c; libvorbis API prototype evidence is represented with opaque vorbis_info, vorbis_comment, and ogg_packet pointers. Xrefs include OggVorbisStream__InitDecoder header reads. Static retail import-thunk/API evidence only; runtime header parsing, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d838c", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d652",
                "vorbis_comment_init",
                true,
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("vc", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d652 jumps through IAT slot 0x005d8394; libvorbis API prototype evidence is represented with an opaque vorbis_comment pointer. Xrefs include OggVorbisStream__InitDecoder. Static retail import-thunk/API evidence only; runtime comment allocation, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d8394", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d658",
                "vorbis_info_init",
                true,
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("vi", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d658 jumps through IAT slot 0x005d8398; libvorbis API prototype evidence is represented with an opaque vorbis_info pointer. Xrefs include OggVorbisStream__InitDecoder. Static retail import-thunk/API evidence only; runtime info allocation, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d8398", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d65e",
                "vorbis_info_clear",
                true,
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("vi", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d65e jumps through IAT slot 0x005d8390; libvorbis API prototype evidence is represented with an opaque vorbis_info pointer. Xrefs include OggVorbisStream__ReadPcmSamples, COggFileRead__dtor_body, and COggFileRead__CloseAndReset. Static retail import-thunk/API evidence only; runtime info cleanup, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d8390", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d664",
                "vorbis_comment_clear",
                true,
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("vc", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d664 jumps through IAT slot 0x005d83a0; libvorbis API prototype evidence is represented with an opaque vorbis_comment pointer. Xrefs include OggVorbisStream__ReadPcmSamples, COggFileRead__dtor_body, and COggFileRead__CloseAndReset. Static retail import-thunk/API evidence only; runtime comment cleanup, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d83a0", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d66a",
                "vorbis_dsp_clear",
                true,
                "__cdecl",
                voidType,
                new ParameterImpl[] { param("v", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d66a jumps through IAT slot 0x005d83a4; libvorbis API prototype evidence is represented with an opaque vorbis_dsp_state pointer. Xrefs include OggVorbisStream__ReadPcmSamples, COggFileRead__dtor_body, and COggFileRead__CloseAndReset. Static retail import-thunk/API evidence only; runtime DSP cleanup, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d83a4", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d670",
                "vorbis_block_clear",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("vb", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d670 jumps through IAT slot 0x005d839c; libvorbis API prototype evidence is represented with an opaque vorbis_block pointer. Xrefs include OggVorbisStream__ReadPcmSamples, COggFileRead__dtor_body, and COggFileRead__CloseAndReset. Static retail import-thunk/API evidence only; runtime block cleanup, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d839c", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d676",
                "vorbis_synthesis_read",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("v", voidPtr), param("samples", intType) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d676 jumps through IAT slot 0x005d8388; libvorbis API prototype evidence is represented with opaque vorbis_dsp_state storage and sample count. Xrefs include OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime PCM cursor movement, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d8388", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d67c",
                "vorbis_synthesis_pcmout",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("v", voidPtr), param("pcm", floatTriplePtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d67c jumps through IAT slot 0x005d83ac; libvorbis API prototype evidence is represented with opaque vorbis_dsp_state storage and a float PCM channel pointer output. Xrefs include OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime PCM buffer lifetime, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d83ac", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d682",
                "vorbis_synthesis_blockin",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("v", voidPtr), param("vb", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d682 jumps through IAT slot 0x005d83a8; libvorbis API prototype evidence is represented with opaque vorbis_dsp_state and vorbis_block pointers. Xrefs include OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime synthesis queueing, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d83a8", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d688",
                "vorbis_synthesis",
                true,
                "__cdecl",
                intType,
                new ParameterImpl[] { param("vb", voidPtr), param("op", voidPtr) },
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d688 jumps through IAT slot 0x005d83b0; libvorbis API prototype evidence is represented with opaque vorbis_block and ogg_packet pointers. Xrefs include OggVorbisStream__ReadPcmSamples. Static retail import-thunk/API evidence only; runtime packet synthesis, concrete libvorbis version, exact Vorbis layouts, BEA patching, and rebuild parity remain unproven.",
                tags("vorbis", "external-api-prototype", "iat-005d83b0", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055d68e",
                "VerQueryValueA",
                false,
                "",
                voidType,
                new ParameterImpl[] {},
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d68e jumps through IAT slot 0x005d82e0; existing Ghidra WinAPI signature is retained and matches Windows SDK winver.h VerQueryValueA prototype shape. Xrefs include CLTShell__WinMain version-resource handling. Static retail import-thunk/API evidence only; runtime version-resource contents, exact shell display behavior, BEA patching, and rebuild parity remain unproven.",
                tags("version-api", "windows-sdk-prototype", "iat-005d82e0", "signature-retained", "callsite-verified")
            ),
            new Spec(
                "0x0055d694",
                "GetFileVersionInfoA",
                false,
                "",
                voidType,
                new ParameterImpl[] {},
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d694 jumps through IAT slot 0x005d82dc; existing Ghidra WinAPI signature is retained and matches Windows SDK winver.h GetFileVersionInfoA prototype shape. Xrefs include CLTShell__WinMain version-resource handling. Static retail import-thunk/API evidence only; runtime version-resource contents, exact shell display behavior, BEA patching, and rebuild parity remain unproven.",
                tags("version-api", "windows-sdk-prototype", "iat-005d82dc", "signature-retained", "callsite-verified")
            ),
            new Spec(
                "0x0055d69a",
                "GetFileVersionInfoSizeA",
                false,
                "",
                voidType,
                new ParameterImpl[] {},
                "Wave619 import-thunk hardening: six-byte JMP at 0x0055d69a jumps through IAT slot 0x005d82d8; existing Ghidra WinAPI signature is retained and matches Windows SDK winver.h GetFileVersionInfoSizeA prototype shape. Xrefs include CLTShell__WinMain version-resource handling, and the next instruction at 0x0055d6a0 begins CRT__SehPopExceptionFrameAndJump. Static retail import-thunk/API evidence only; runtime version-resource contents, exact shell display behavior, BEA patching, and rebuild parity remain unproven.",
                tags("version-api", "windows-sdk-prototype", "iat-005d82d8", "signature-retained", "callsite-verified", "island-tail")
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
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad != 0 || stats.missing != 0) {
                throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
            }
        }
    }
}
