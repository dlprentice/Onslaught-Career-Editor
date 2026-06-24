//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyPlatformChunkerTimerSignatureCorrection extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
            this.parameters = parameters;
        }
    }

    private static boolean isDryRun(String mode) {
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

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.callingConvention).append(" ").append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            return false;
        }

        if (needsRename) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
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
        println("OK: " + spec.address + " " + spec.name + " -> " + fn.getSignature().toString());
        return needsRename;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00423510", "CCarverGuide__AcquireNearestTargetReader", "__fastcall", voidType,
                "Name/signature correction: CarverGuide-specific nearest-target reader refresh. Clears the active reader at +0x2c, scans mapwho around owner +0x18 with the wider 45.0-radius constant, and accepts the nearest candidate through the Carver-specific flagged-entry threshold. Exact CarverGuide layout, source identity, runtime targeting behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CCylinder__AcquireNearestTargetReader"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00423650", "CFrameTimer__ctor", "__fastcall", voidPtr,
                "Name/signature correction: CFrameTimer constructor/init called from PCPlatform__Init after a 0x38-byte allocation; queries performance-counter frequency into +0x18, falls back to 1000 ticks/sec, stores float frequency at +0x0, and returns this. The CFrameTimer source body is absent from the current source snapshot; concrete layout, runtime timing behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"PCPlatform__ReadPerformanceFrequency"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00423680", "CFrameTimer__Start", "__thiscall", voidType,
                "Name/signature correction: CFrameTimer Start-style helper called from PCPlatform__Init with source-parity 1.0f; records the frame scale/reciprocal, computes the tick budget from saved frequency, and captures the initial QPC/timeGetTime baseline. Exact CFrameTimer source body, field names, runtime timing behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"PCPlatform__InitTimerFromPerfCounter"},
                new ParameterImpl[] {param("this", voidPtr), param("frameScale", floatType)}),
            new Spec("0x00423720", "CFrameTimer__Frame", "__fastcall", voidType,
                "Name/signature correction: CFrameTimer per-frame update called from PCPlatform__DeviceFlip; samples QPC/timeGetTime, stores elapsed ticks, smooths the FPS/frame-scale field, and refreshes reciprocal frame timing. Exact CFrameTimer layout, runtime timing behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"Platform__UpdateHighResTimerDeltaAndScale"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004237d0", "CChunkReader__ctor", "__fastcall", voidPtr,
                "Name/signature correction: CChunkReader constructor from chunker.cpp; allocates a 0x134-byte CDXMemBuffer/CMEMBUFFER, constructs it, stores it at +0x4, sets mOwnFile at +0xc, and returns this. Concrete layout, runtime resource IO behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CChunker__Create"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00423840", "CChunkReader__dtor_base", "__fastcall", voidType,
                "Name/signature correction: CChunkReader destructor-base behavior; if mOwnFile and File are set, destroys/frees the CDXMemBuffer and clears File. Exact allocator ownership, runtime resource IO behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CChunkerStream__DestroyOwnedChunkerIfPresent"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00423870", "CChunkReader__OpenExistingBuffer", "__thiscall", voidPtr,
                "Name/signature correction: CChunkReader::Open(CMEMBUFFER*) source-parity helper; resets Size and ReadSinceChunk, drops any owned File, marks mOwnFile false, stores existingBuffer at +0x4, and returns it. Runtime resource IO behavior, concrete layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CResourceAccumulator__ResetChunkerSlotAndAssignSource"},
                new ParameterImpl[] {param("this", voidPtr), param("existingBuffer", voidPtr)}),
            new Spec("0x004238c0", "CChunkReader__OpenFile", "__thiscall", voidPtr,
                "Name/signature correction: CChunkReader::Open(char*) source-parity helper; resets Size/ReadSinceChunk, calls CDXMemBuffer__InitFromFile(File, filename, MEMTYPE_MEMBUFFER, true, 0), and returns File or null. Runtime file IO behavior, concrete layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CChunkerStream__OpenReadAndGetChunker"},
                new ParameterImpl[] {param("this", voidPtr), param("filename", charPtr)}),
            new Spec("0x00423900", "CChunkReader__Close", "__fastcall", intType,
                "Name/signature correction: CChunkReader::Close wrapper around File->Close(); returns 0 on successful close and -1 on failure. Runtime file IO behavior, concrete layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CChunkerStream__CloseDXMemBuffer_Status0OrMinus1"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00423910", "CChunkReader__GetNext", "__fastcall", uintType,
                "Name/signature correction: CChunkReader::GetNext source-parity helper; resets ReadSinceChunk, reads a 4-byte chunk id and 4-byte Size from File, and returns the chunk id or 0 on short read. It is a shared resource deserializer helper, not CMeshPart-specific. Runtime resource IO behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CMeshPart__ReadHeaderPairAndResetByteCount"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00423960", "CChunkReader__Read", "__thiscall", boolType,
                "Name/signature correction: CChunkReader::Read source-parity helper; increments ReadSinceChunk by size*count, reads that many bytes through CDXMemBuffer__Read, and returns whether the full byte count was read. Runtime resource IO behavior, concrete layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CMeshPart__ReadBlockAndAccumulateByteCount"},
                new ParameterImpl[] {param("this", voidPtr), param("outBuffer", voidPtr), param("size", intType), param("count", intType)}),
            new Spec("0x00423990", "CChunkReader__Skip", "__fastcall", intType,
                "Name/signature correction: CChunkReader::Skip source-parity helper; computes Size-ReadSinceChunk, sets ReadSinceChunk to Size, and returns CDXMemBuffer__Skip(File, remaining). Runtime resource IO behavior, concrete layout, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CChunkerStream__SkipRemainingChunkBytes"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004239b0", "CWorld__GetSubstateField_12C", "__thiscall", intType,
                "Signature/comment pass: small CWorld accessor returning the nested field at *(this+4)+0x12c; called by world/mesh deserialization checks. Exact field name, concrete layout, runtime world behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004239f0", "CUnitAI__InitDefaults_AutoConfigTestPath", "__fastcall", voidPtr,
                "Signature/comment correction: constructor-style CUnitAI defaults initializer; seeds runtime flags/timers, copies c:\\beaautoconfigtest\\ into +0x44, initializes additional default strings/state fields, and sets timeout +0x318 based on DAT_0066e94e. CUnitAI source body is absent; concrete layout, runtime AI behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x005158f0", "PCPlatform__DeviceFlip", "__thiscall", voidType,
                "Name/signature correction: source-aligned CPCPlatform::DeviceFlip(BOOL) wrapper; reads mFrameTimer from this+0x0, calls CFrameTimer__Frame when present, then runs screen-dump/device-lost restore helpers. The inGame argument is stack-cleaned but not used in the current retail body; exact display/runtime behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"Platform__FinalizeAsyncSaveCareer"},
                new ParameterImpl[] {param("this", voidPtr), param("inGame", intType)}),
            new Spec("0x00515950", "PCPlatform__GetFPS", "__fastcall", floatType,
                "Name/signature correction: source-aligned CPCPlatform::GetFPS helper; returns frame timer field +0x4 when mFrameTimer exists, otherwise returns 1.0f. Exact CFrameTimer field identity, runtime FPS behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"PtrFloatAt4__GetOrOne"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00547d70", "CDXMemBuffer__ctor", "__fastcall", voidPtr,
                "Name/signature correction: CDXMemBuffer constructor source-parity body; zeros data/CRC pointer and state fields used by CChunkReader. Corrects stale CChunker owner label; exact layout, runtime IO behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CChunker__CChunker"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00547d90", "CDXMemBuffer__dtor_base", "__fastcall", voidType,
                "Name/signature correction: CDXMemBuffer destructor-base body; frees mData and mCRCData-style owned buffers. Corrects stale CChunker destructor label; exact allocator behavior, runtime IO behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"CChunker__Destructor"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00547ec0", "CDXMemBuffer__InitFromFile", "__thiscall", boolType,
                "Name/signature correction: CDXMemBuffer::InitFromFile source-parity helper; allocates the read buffer, opens the file, initializes read cursor/EOF state, optionally skips start bytes, handles CRC-style side data, and returns success. Concrete layout, runtime IO behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"DXMemBuffer__OpenRead"},
                new ParameterImpl[] {param("this", voidPtr), param("filename", charPtr), param("memType", intType), param("mungePath", intType), param("startSkip", uintType)}),
            new Spec("0x005482d0", "CDXMemBuffer__Skip", "__thiscall", intType,
                "Name/signature correction: CDXMemBuffer::Skip source-parity helper; advances the read cursor across the active buffer and reloads blocks as needed, returning the byte count skipped. Concrete layout, runtime IO behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"DXMemBuffer__Skip"},
                new ParameterImpl[] {param("this", voidPtr), param("size", intType)}),
            new Spec("0x00548570", "CDXMemBuffer__Read", "__thiscall", intType,
                "Name/signature correction: CDXMemBuffer::Read source-parity helper; copies bytes from the buffered file reader into caller storage, reloads blocks as needed, updates position, and returns the byte count read. Concrete layout, runtime IO behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"DXMemBuffer__ReadBytes"},
                new ParameterImpl[] {param("this", voidPtr), param("data", voidPtr), param("size", intType)}),
            new Spec("0x00548c00", "CDXMemBuffer__Close", "__fastcall", boolType,
                "Name/signature correction: CDXMemBuffer::Close source-parity helper; in read mode it closes the handle and frees read/CRC buffers, while write mode flushes remaining bytes and CRC side data before cleanup. Concrete layout, runtime IO behavior, tags, locals, and rebuild parity remain unproven.",
                new String[] {"DXMemBuffer__Close"},
                new ParameterImpl[] {param("this", voidPtr)})
        };

        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        for (Spec spec : specs) {
            boolean didRename = applySpec(spec, dryRun);
            if (dryRun) {
                skipped++;
            }
            else {
                updated++;
                if (didRename) {
                    renamed++;
                }
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " renamed=" + renamed + " missing=0 bad=0");
    }
}
