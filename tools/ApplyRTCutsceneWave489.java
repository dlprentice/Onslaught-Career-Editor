//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyRTCutsceneWave489 extends GhidraScript {
    private static class Spec {
        final String address;
        final String[] allowedExistingNames;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final boolean createIfMissing;
        final String[] tags;

        Spec(
                String address,
                String[] allowedExistingNames,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                boolean createIfMissing,
                String[] tags) {
            this.address = address;
            this.allowedExistingNames = allowedExistingNames;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.createIfMissing = createIfMissing;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(Address address) {
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
            "rtcutscene-wave489",
            "retail-binary-evidence"
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

    private Function createFunctionAt(Spec spec, Address address) throws Exception {
        DisassembleCommand cmd = new DisassembleCommand(address, null, true);
        cmd.applyTo(currentProgram, monitor);
        Function fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = functionAtEntry(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        return fn;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            boolean createdNow = false;

            if (fn == null) {
                if (!spec.createIfMissing) {
                    stats.missing++;
                    println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                    return;
                }
                if (dryRun) {
                    stats.wouldCreate++;
                    println("DRY: " + spec.address + " <missing> -> create " + expectedSignature(spec));
                    return;
                }
                fn = createFunctionAt(spec, address);
                createdNow = true;
                stats.created++;
            }

            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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

            Function readBack = functionAtEntry(address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            String expectedSignature = expectedSignature(spec);
            if (!actualSignature.equals(expectedSignature)) {
                throw new IllegalStateException(
                    "Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature
                );
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> actualTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
                }
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getName() + " -> " + actualSignature + (createdNow ? " created" : ""));
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(intType);
        DataType byteType = ByteDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004d6a30",
                new String[] {"CRenderThing__VFunc_01_004d6a30"},
                "CRenderThing__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init_record", voidPtr), param("context_token", intType)},
                "Wave489 name/signature/comment hardening: CRTCutscene__Init and CRTMesh__Init call this CRenderThing base initializer. The body copies init_record+0x400 into this+0x08, writes the observed 0x3727c5ac marker at this+0x04, and clears this+0x0c; the third stack parameter is preserved in the call contract but unused by this body. Static retail evidence only; exact source name, full CRenderThing layout, runtime render behavior, and rebuild parity remain unproven.",
                false,
                tags("crenderthing", "base-init", "signature-corrected", "renamed", "comment-hardened")
            ),
            new Spec(
                "0x004d6b20",
                new String[] {"VFuncSlot_07_004d6b20"},
                "SharedVFunc__ReturnZero_004d6b20",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave489 shared-vtable correction: many unrelated vtables and save/load callsites reference this single body, which returns 0 without reading object state. The broad xref set prevents an owner-specific label. Static retail evidence only; exact virtual contracts, caller semantics, runtime behavior, and rebuild parity remain unproven.",
                false,
                tags("shared-vfunc", "return-zero", "signature-corrected", "renamed", "comment-hardened")
            ),
            new Spec(
                "0x00405940",
                new String[] {},
                "SharedVFunc__ReturnZeroRet4_00405940",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("arg0", voidPtr)},
                "Wave489 function-boundary recovery: RTCutscene vtable 0x005dea38 slot 5 points at this previously missing two-instruction shared body. It clears EAX and returns with RET 0x4, so the caller-visible result is 0 with one stack argument cleaned. Static retail vtable/instruction evidence only; exact owner coverage, virtual contract, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("shared-vfunc", "return-zero", "ret4", "function-created", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbb60",
                new String[] {"CRTCutscene__CRTCutscene"},
                "CRTCutscene__CRTCutscene",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave489 signature/comment hardening: PCRTID__CreateObject calls this CRTCutscene constructor for type id 5. The body clears this+0x10, installs vtable 0x005dea38, and clears the count at this+0x18. Static retail evidence only; exact class layout, allocator ownership, runtime cutscene behavior, and rebuild parity remain unproven.",
                false,
                tags("rtcutscene", "constructor", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbb80",
                new String[] {},
                "CRenderThing__VFunc_07_ClearRenderOutputs",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("arg0", voidPtr),
                    param("arg1", voidPtr),
                    param("out_vec4", voidPtr),
                    param("out_matrix", voidPtr),
                    param("arg4", voidPtr),
                    param("arg5", voidPtr)
                },
                "Wave489 function-boundary recovery: RTCutscene and neighboring render-object vtables point at this previously missing RET 0x18 body. It clears the first three dwords of one output record, writes the fourth from the observed scratch/local lane, and copies the 0x30-byte matrix/global block at 0x0083ccd8 into another caller-provided output. Static retail vtable/instruction evidence only; exact render-object owner, argument names, runtime transform behavior, fourth-lane semantics, and rebuild parity remain unproven.",
                true,
                tags("crenderthing", "vfunc-slot-07", "render-output", "function-created", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbbe0",
                new String[] {},
                "CRenderThing__VFunc_08_ClearVec3",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("out_vec3", voidPtr), param("arg1", voidPtr)},
                "Wave489 function-boundary recovery: RTCutscene and neighboring render-object vtables point at this previously missing RET 0x8 body. It clears three dwords at the first stack argument and otherwise ignores object state. Static retail vtable/instruction evidence only; exact render-object owner, vector type, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("crenderthing", "vfunc-slot-08", "clear-vec3", "function-created", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbc10",
                new String[] {},
                "SharedVFunc__ReturnMinusOneRet4_004dbc10",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("arg0", voidPtr)},
                "Wave489 function-boundary recovery: RTCutscene vtable 0x005dea38 slot 19 and neighboring tables point at this previously missing two-instruction body. It returns -1 and cleans one stack argument with RET 0x4. Static retail vtable/instruction evidence only; exact owner coverage, virtual contract, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("shared-vfunc", "return-minus-one", "ret4", "function-created", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbc30",
                new String[] {"CRTCutscene__Destructor"},
                "CRTCutscene__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave489 name/signature/comment hardening: RTCutscene vtable 0x005dea38 slot 0 points at this scalar deleting destructor wrapper. It calls CRTCutscene__dtor, tests delete flag bit 0, optionally frees this through CDXMemoryManager__Free(&DAT_009c3df0, this), and returns this. Static retail evidence only; exact lifetime ownership, exception cleanup behavior, runtime behavior, and rebuild parity remain unproven.",
                false,
                tags("rtcutscene", "destructor", "scalar-deleting-dtor", "signature-corrected", "renamed", "comment-hardened")
            ),
            new Spec(
                "0x004dbc50",
                new String[] {"CRTCutscene__DestructorImpl"},
                "CRTCutscene__dtor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave489 name/signature/comment hardening: destructor body for CRTCutscene. It restores the RTCutscene vtable, frees the active mesh-pointer array at this+0x14 when the active flag at this+0x20 is set, clears active/current-index state, frees each 0x100-byte name buffer from the this+0x1c table, frees that name table, restores the CRenderThing vtable, and destroys the child/owned pointer at this+0x10 when present. Static retail evidence only; exact field names, ownership rules, runtime behavior, and rebuild parity remain unproven.",
                false,
                tags("rtcutscene", "destructor", "mesh-name-table", "signature-corrected", "renamed", "comment-hardened")
            ),
            new Spec(
                "0x004dbd20",
                new String[] {"CRenderThing__ctor_like_004dbd20"},
                "CRenderThing__dtor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave489 name/signature/comment correction: exception-unwind thunks and CRTCutscene__dtor use this as the CRenderThing destructor body, not as a constructor. It restores vtable 0x005deaac and dispatches the owned/child pointer at this+0x10 through its vtable slot 0 with delete flag 1 when present. Static retail evidence only; exact CRenderThing layout, ownership semantics, runtime behavior, and rebuild parity remain unproven.",
                false,
                tags("crenderthing", "destructor", "owner-corrected", "signature-corrected", "renamed", "comment-hardened")
            ),
            new Spec(
                "0x004dbd50",
                new String[] {"CRenderThing__VFunc_00_004dbd50"},
                "CRenderThing__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave489 name/signature/comment correction: CRenderThing vtable slot 0 points at this scalar deleting destructor wrapper. It restores the CRenderThing vtable, destroys the owned/child pointer at this+0x10 when present, optionally frees this through CDXMemoryManager__Free(&DAT_009c3df0, this) when delete flag bit 0 is set, and returns this. Static retail evidence only; exact CRenderThing layout, lifetime ownership, runtime behavior, and rebuild parity remain unproven.",
                false,
                tags("crenderthing", "destructor", "scalar-deleting-dtor", "signature-corrected", "renamed", "comment-hardened")
            ),
            new Spec(
                "0x004dbd80",
                new String[] {"CRTCutscene__Init"},
                "CRTCutscene__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init_record", voidPtr)},
                "Wave489 signature/comment hardening: RTCutscene vtable 0x005dea38 slot 1 points at this initializer. It calls CRenderThing__Init, reads init_record+0x418 as the cutscene element count, allocates the this+0x14 mesh-pointer array and this+0x1c name-buffer table with RTCutscene.cpp debug allocator tags, copies each source name pointer from init_record+0x414 into a new 0x100-byte buffer, sets playback scalar this+0x04 to 1.0, clears active flag this+0x20, and sets current index this+0x24 to -1. Static retail evidence only; exact source structure, runtime asset behavior, and rebuild parity remain unproven.",
                false,
                tags("rtcutscene", "init", "mesh-name-table", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbe50",
                new String[] {},
                "CRTCutscene__Activate",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave489 function-boundary recovery: RTCutscene vtable 0x005dea38 slot 12 points at this previously missing activator. If the active flag at this+0x20 is clear, it walks the element-name table at this+0x1c for count this+0x18, calls CMesh__FindOrCreate(name, 1), stores returned mesh pointers into the this+0x14 array, and sets active. Static retail evidence only; exact activation semantics, mesh cache lifetime, runtime cutscene behavior, and rebuild parity remain unproven.",
                true,
                tags("rtcutscene", "activate", "mesh-cache", "function-created", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbe90",
                new String[] {"CRTCutscene__Reset"},
                "CRTCutscene__Reset",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave489 signature/comment hardening: RTCutscene vtable 0x005dea38 slot 13 points at this reset/deactivate helper. When active, it frees the mesh-pointer array at this+0x14, clears that pointer, clears active flag this+0x20, and resets current index this+0x24 to -1. Static retail evidence only; mesh-cache refcount semantics, runtime cutscene behavior, and rebuild parity remain unproven.",
                false,
                tags("rtcutscene", "reset", "deactivate", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbec0",
                new String[] {},
                "CRTCutscene__RenderCurrent",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("render_context", voidPtr)},
                "Wave489 function-boundary recovery: RTCutscene vtable 0x005dea38 slot 2 points at this previously missing RET 0x4 body. It requires active state and a nonnegative current index, obtains the current mesh through the vtable +0x24 path, stages the 0x0083ccd8 transform block, toggles DAT_00704e60 around a CSphere__RenderAnimatedRecursive-style render call, and logs the RTCutscene.cpp string at 0x00631e50 when no current index is selected. Static retail evidence only; exact render contract, source name, runtime visual behavior, and rebuild parity remain unproven.",
                true,
                tags("rtcutscene", "render-current", "function-created", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbf70",
                new String[] {"CRTCutscene__SetCurrentIndex"},
                "CRTCutscene__SetCurrentIndex",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("current_index", intType)},
                "Wave489 signature/comment hardening: CCutscene update/prep callsites use this setter to write current_index into CRTCutscene field this+0x24. Static retail evidence only; exact sequencing, runtime cutscene behavior, and rebuild parity remain unproven.",
                false,
                tags("rtcutscene", "current-index", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbf80",
                new String[] {},
                "CRTCutscene__GetCurrentMesh",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave489 function-boundary recovery: RTCutscene vtable 0x005dea38 slot 9 points at this previously missing getter. It returns 0 unless this+0x08 is nonzero, active flag this+0x20 is set, and current index this+0x24 is not -1; otherwise it returns the mesh pointer from the this+0x14 array at the current index. Static retail evidence only; exact field names, active-state contract, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("rtcutscene", "current-mesh", "getter", "function-created", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbfb0",
                new String[] {},
                "CRTCutscene__GetDefaultScalar",
                "__fastcall",
                floatType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave489 function-boundary recovery: RTCutscene vtable 0x005dea38 slot 6 points at this previously missing x87 scalar-return body. It returns the global float at 0x005d856c and otherwise ignores object state. Static retail evidence only; exact virtual contract, runtime meaning of the default scalar, and rebuild parity remain unproven.",
                true,
                tags("rtcutscene", "float-return", "default-scalar", "function-created", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbfc0",
                new String[] {},
                "CRTCutscene__GetCurrentMeshEntryValue",
                "__thiscall",
                floatType,
                new ParameterImpl[] {param("this", voidPtr), param("type_id", intType), param("out_index", intPtr)},
                "Wave489 function-boundary recovery: RTCutscene vtable 0x005dea38 slot 14 points at this previously missing RET 0x8 x87-return body. It fetches the current mesh through vtable +0x24 and, when present, forwards type_id and out_index to CMesh__FindEntryValueByTypeId; otherwise it returns the default float at 0x005d856c. Static retail evidence only; exact type-id contract, runtime cutscene usage, and rebuild parity remain unproven.",
                true,
                tags("rtcutscene", "current-mesh", "entry-lookup", "float-return", "function-created", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004dbff0",
                new String[] {},
                "CRTCutscene__BuildCurrentFrameOutputs",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_primary", voidPtr),
                    param("out_secondary", voidPtr),
                    param("animation_query", voidPtr),
                    param("out_scalar", voidPtr)
                },
                "Wave489 function-boundary recovery: RTCutscene vtable 0x005dea38 slot 17 points at this previously missing RET 0x10 body. It obtains the current mesh through vtable +0x24, optionally queries animation state through the caller-supplied object, computes a frame/sample index, dispatches CMeshPart-style helpers, writes output records, and falls back to identity/default output blocks when current mesh or lookup state is unavailable. Static retail evidence only; exact argument names, animation contract, output record layouts, runtime visual behavior, and rebuild parity remain unproven.",
                true,
                tags("rtcutscene", "current-mesh", "frame-output", "function-created", "signature-corrected", "comment-hardened")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("ApplyRTCutsceneWave489 failed; see log");
        }
    }
}
