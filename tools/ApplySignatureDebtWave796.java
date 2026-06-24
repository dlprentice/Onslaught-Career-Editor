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

public class ApplySignatureDebtWave796 extends GhidraScript {
    private static class ParamSpec {
        final String name;
        final DataType dataType;
        final int existingIndex;

        ParamSpec(String name, DataType dataType, int existingIndex) {
            this.name = name;
            this.dataType = dataType;
            this.existingIndex = existingIndex;
        }
    }

    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParamSpec[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParamSpec[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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

    private ParamSpec param(String name, DataType dataType) {
        return new ParamSpec(name, dataType, -1);
    }

    private ParamSpec existingParamType(String name, int existingIndex) {
        return new ParamSpec(name, null, existingIndex);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "signature-debt-wave796",
            "wave796-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "param-name-hardened",
            "final-param-signature-debt"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private DataType resolveDataType(Function fn, ParamSpec param) {
        if (param.dataType != null) {
            return param.dataType;
        }
        Parameter[] existing = fn.getParameters();
        if (param.existingIndex < 0 || param.existingIndex >= existing.length) {
            throw new IllegalArgumentException(
                "Existing parameter index " + param.existingIndex + " unavailable for " + fn.getName()
                + " (count=" + existing.length + ")"
            );
        }
        return existing[param.existingIndex].getDataType();
    }

    private ParameterImpl[] buildParams(Function fn, Spec spec) throws Exception {
        ParameterImpl[] rendered = new ParameterImpl[spec.params.length];
        for (int i = 0; i < spec.params.length; i++) {
            ParamSpec param = spec.params[i];
            rendered[i] = new ParameterImpl(param.name, resolveDataType(fn, param), currentProgram);
        }
        return rendered;
    }

    private boolean hasCallingConvention(Spec spec) {
        return spec.callingConvention != null && !spec.callingConvention.trim().isEmpty();
    }

    private String expectedSignature(Spec spec, ParameterImpl[] params) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ");
        if (hasCallingConvention(spec)) {
            sb.append(spec.callingConvention).append(" ");
        }
        sb.append(spec.name).append("(");
        boolean renderedAnyParam = false;
        if ("__thiscall".equals(spec.callingConvention)) {
            sb.append("void * this");
            renderedAnyParam = true;
        }
        if (params.length == 0 && !renderedAnyParam) {
            sb.append("void");
        } else {
            for (int i = 0; i < params.length; i++) {
                if (renderedAnyParam || i > 0) {
                    sb.append(", ");
                }
                sb.append(params[i].getDataType().getDisplayName())
                    .append(" ")
                    .append(params[i].getName());
                renderedAnyParam = true;
            }
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        ParameterImpl[] params = buildParams(fn, spec);
        String signature = fn.getSignature().toString();
        if (!signature.equals(expectedSignature(spec, params))) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + signature);
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> actualTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actualTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
                stats.bad++;
                return;
            }

            ParameterImpl[] params = buildParams(fn, spec);
            String expected = expectedSignature(spec, params);
            String signature = fn.getSignature().toString();
            boolean signatureNeedsUpdate = !signature.equals(expected);
            boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(spec.comment);
            Set<String> actualTags = tagNames(fn);
            boolean tagsNeedUpdate = false;
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    tagsNeedUpdate = true;
                    break;
                }
            }

            if (!signatureNeedsUpdate && !commentNeedsUpdate && !tagsNeedUpdate) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name + " signature=" + signature + " -> " + expected);
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                } else {
                    stats.commentOnlyUpdated++;
                }
                stats.skipped++;
                return;
            }

            if (hasCallingConvention(spec)) {
                fn.setCallingConvention(spec.callingConvention);
            }
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                params
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + spec.name + " signature=" + expected);
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.updated++;
            Thread.sleep(50L);
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
            stats.bad++;
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplySignatureDebtWave796 mode=" + (dryRun ? "dry" : "apply"));

        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004bbcd0",
                "CNamedMesh__VFunc_09_004bbcd0",
                "__thiscall",
                voidType,
                new ParamSpec[] {
                    param("init_record", voidPtr),
                    param("unused_slot_arg", voidPtr)
                },
                "Wave796 final param-signature-debt hardening: preserves the Wave458 CNamedMesh vtable-slot boundary while naming the two visible stack parameters. The current decompile uses init_record as the init pointer, writes init_record+0x64 to this+0xe0, forces init flags/state, calls CActor__Init, sets a STAND-like animation, snapshots this+0x1c..0x28 into DAT_00807528..34, conditionally schedules event 3000, and adds this to world occupancy/static-shadow tracking. The second visible slot remains unused in the decompile. Static retail Ghidra evidence only; hidden register/thiscall storage, runtime NamedMesh behavior, exact layout/source identity, and rebuild parity remain unproven.",
                tags("named-mesh", "actor-init", "occupancy", "hidden-abi", "param-debt-cleared")
            ),
            new Spec(
                "0x00564486",
                "CRT__FmodReduceCore",
                "__cdecl",
                intType,
                new ParamSpec[] {
                    param("divisor_mantissa_low", intType),
                    param("divisor_mid_bits", uintType),
                    param("divisor_sign_exp_high", intType)
                },
                "Wave796 final param-signature-debt hardening: preserves the Wave630 CRT fmod/FPU boundary while naming the visible packed divisor words. The helper is called twice from CRT__FmodCore, saves EAX/EBX/ECX, compares exponent/zero/Inf/NaN fields, iterates FPREM-style reductions over caller-stack long-double scratch slots, adjusts the FPU control word, and returns through the custom hidden EAX path. Static FPU remainder evidence only; exact caller-stack payload layout, CRT helper identity, runtime rounding behavior, and rebuild parity remain unproven.",
                tags("crt-fmod", "fpu-remainder", "custom-stack", "crt-runtime", "param-debt-cleared")
            ),
            new Spec(
                "0x00574a99",
                "`vector_constructor_iterator'",
                "__stdcall",
                voidType,
                new ParamSpec[] {
                    param("base", voidPtr),
                    param("element_size", uintType),
                    param("element_count", intType),
                    existingParamType("constructor", 3)
                },
                "Wave796 final param-signature-debt hardening: Visual Studio 2003 Release library-matched vector constructor iterator. The saved signature names the conventional base, element_size, element_count, and constructor callback parameters while preserving the existing constructor function-pointer datatype; the decompile still shows the active base pointer through hidden EDI and loops constructor(unaff_EDI) element_count times. Static library-match evidence only; exact compiler helper source version, hidden EDI/base-storage contract, runtime C++ array construction behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-studio-2003", "vector-constructor", "cpp-runtime", "param-debt-cleared")
            ),
            new Spec(
                "0x00591460",
                "CDXTexture__DecodeJpegSegment_StartOfFrame",
                "__fastcall",
                intType,
                new ParamSpec[] {
                    param("sof_marker", intType)
                },
                "Wave796 final param-signature-debt hardening: preserves the Wave691 JPEG start-of-frame parser boundary while naming the visible SOF marker/context parameter. The helper records hidden EAX and sof_marker into the decode state, reads precision/width/height/component count, validates dimensions and component triplets, fills component descriptors, and emits diagnostics 0x3a/0x20/0x0b/0x65. Static register-context Ghidra evidence only; exact SOF marker enum, hidden EAX/ESI/EBX/EBP ABI, frame-header layout, runtime decode fidelity, and rebuild parity remain unproven.",
                tags("cdxtexture", "jpeg", "start-of-frame", "register-context", "param-debt-cleared")
            ),
            new Spec(
                "0x00591fc0",
                "CDXTexture__ParseJfifApp0Header",
                "__fastcall",
                voidType,
                new ParamSpec[] {
                    param("segment_start_offset", intType)
                },
                "Wave796 final param-signature-debt hardening: preserves the Wave691 JPEG APP0 parser boundary while naming the visible segment_start_offset parameter. The helper combines hidden EAX payload length with segment_start_offset for diagnostic offsets, validates JFIF/JFXX signatures from hidden EDI payload bytes, records version/density/thumbnail fields, and emits diagnostics 0x4d/0x57/0x58/0x5a/0x77/0x6c/0x6d/0x6e/0x59. Static register-context Ghidra evidence only; exact APP0 offset contract, hidden EAX/ESI/EDI ABI, density enum, thumbnail policy, runtime decode fidelity, and rebuild parity remain unproven.",
                tags("cdxtexture", "jpeg", "app0", "jfif", "param-debt-cleared")
            ),
            new Spec(
                "0x005921a0",
                "CDXTexture__ParseAdobeApp14Header",
                "__thiscall",
                voidType,
                new ParamSpec[] {
                    param("segment_start_offset", uintType),
                    param("unused_context", intType)
                },
                "Wave796 final param-signature-debt hardening: preserves the Wave691 JPEG APP14 Adobe parser boundary while naming the two visible stack parameters. Ghidra still renders the payload length as the synthetic this argument and keeps the register-held payload pointer outside formal parameters; segment_start_offset is added to that length for diagnostics, and unused_context is not used in the decompile. Static register-context Ghidra evidence only; exact APP14 transform enum, hidden EAX/ESI ABI, offset contract, color-transform policy, runtime decode fidelity, and rebuild parity remain unproven.",
                tags("cdxtexture", "jpeg", "app14", "adobe", "param-debt-cleared")
            ),
            new Spec(
                "0x00592ca0",
                "CDXTexture__FormatChunkTagForDiagnostics",
                "__thiscall",
                voidType,
                new ParamSpec[] {
                    param("decode_state", intType),
                    param("message_text", intType),
                    param("unused_context", voidPtr)
                },
                "Wave796 final param-signature-debt hardening: preserves the Wave693 PNG chunk-diagnostic formatter boundary while naming the visible stack parameters. Ghidra still renders the ECX output buffer as the synthetic this argument; decode_state supplies the chunk tag at +0x10c, message_text is copied when nonzero after the formatted tag, and unused_context remains unused in the decompile. Static metadata/decompile evidence only; exact output-buffer capacity, chunk-state layout, message lifetime, runtime PNG diagnostic fidelity, and rebuild parity remain unproven.",
                tags("cdxtexture", "png", "diagnostic-format", "chunk-tag", "param-debt-cleared")
            ),
            new Spec(
                "0x0059c070",
                "CTexture__ProcessRowBatchesLinearStride",
                "__stdcall",
                voidType,
                new ParamSpec[] {
                    param("callback_context", intType),
                    param("callback_mode", intType)
                },
                "Wave796 final param-signature-debt hardening: preserves the Wave712 linear row-batch walker boundary while naming the two visible stack parameters. The helper uses a hidden ESI row-batch descriptor, advances linear row pointers by descriptor stride/bounds/limits, and invokes callback slot [0xc] with callback_context plus byte offset/size when callback_mode is zero, or callback slot [0xd] with callback_context plus row pointer otherwise. Static hidden-ESI Ghidra evidence only; exact row-batch descriptor layout, callback ABI, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("texture", "row-batch", "linear-row-batches", "hidden-esi", "param-debt-cleared")
            ),
            new Spec(
                "0x0059c110",
                "CTexture__ProcessRowBatchesMcuStride128",
                "__stdcall",
                voidType,
                new ParamSpec[] {
                    param("callback_context", intType),
                    param("callback_mode", intType)
                },
                "Wave796 final param-signature-debt hardening: preserves the Wave712 MCU-stride row-batch walker boundary while naming the two visible stack parameters. The helper uses a hidden ESI row-batch descriptor, advances rows with 0x80-scaled byte counts, and invokes callback slot [0xc] with callback_context plus byte offset/size when callback_mode is zero, or callback slot [0xd] with callback_context plus row pointer otherwise. Static hidden-ESI Ghidra evidence only; exact row-batch descriptor layout, callback ABI, MCU/component semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("texture", "row-batch", "mcu-row-batches", "hidden-esi", "param-debt-cleared")
            ),
            new Spec(
                "0x0059e310",
                "CDXTexture__WriteJpegHuffmanTable",
                "__thiscall",
                voidType,
                new ParamSpec[] {
                    param("table_index", intType),
                    param("unused_context", intType)
                },
                "Wave796 final param-signature-debt hardening: preserves the Wave716 JPEG DHT writer boundary while naming the visible table_index and unused_context parameters. Hidden EAX selects the table class/context; table_index selects the encoder-state descriptor from this+0x58 or this+0x68, contributes the emitted table class/id byte, and unused_context remains unused in the decompile. The helper sums the 16 Huffman code-count bytes, writes the DHT marker/length/table id/counts/symbols, and marks the descriptor as written. Static register-context Ghidra evidence only; exact Huffman descriptor layout, table-class enum, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                tags("cdxtexture", "jpeg", "huffman-table", "hidden-eax-context", "param-debt-cleared")
            ),
            new Spec(
                "0x005a7617",
                "CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles",
                "__stdcall",
                voidType,
                new ParamSpec[] {
                    param("out_matrix4", voidPtr),
                    param("packed_angle_pair_low", intType),
                    param("packed_angle_pair_high", intType)
                },
                "Wave796 final param-signature-debt hardening: preserves the Wave721 CFastVB dispatch-op boundary while naming the visible output matrix pointer and packed angle-pair dwords. The helper scales hidden stack input plus CONCAT44(packed_angle_pair_high, packed_angle_pair_low) by constant 0x005ef190, calls the fast trig pair helper three times, and writes the observed matrix4 fields before FastExitMediaState. Static custom-stack Ghidra evidence only; exact dispatch-table slot schema, hidden packed stack ABI, vector/matrix storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.",
                tags("cfastvb", "dispatch-table", "euler-angles", "matrix4x4", "param-debt-cleared")
            ),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0 would_rename=0"
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave796 apply encountered missing/bad rows");
        }
    }
}
