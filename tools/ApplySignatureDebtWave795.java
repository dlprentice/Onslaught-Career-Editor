//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.LongLongDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedLongLongDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplySignatureDebtWave795 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] params, String comment, String[] tags) {
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "signature-debt-wave795",
            "wave795-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "param-name-hardened",
            "final-exact-undefined-signature-debt"
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

    private boolean hasCallingConvention(Spec spec) {
        return spec.callingConvention != null && !spec.callingConvention.trim().isEmpty();
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ");
        if (hasCallingConvention(spec)) {
            sb.append(spec.callingConvention).append(" ");
        }
        sb.append(spec.name).append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        } else {
            for (int i = 0; i < spec.params.length; i++) {
                if (i > 0) {
                    sb.append(", ");
                }
                sb.append(spec.params[i].getDataType().getDisplayName())
                    .append(" ")
                    .append(spec.params[i].getName());
            }
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        String signature = fn.getSignature().toString();
        if (!signature.equals(expectedSignature(spec))) {
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

            String signature = fn.getSignature().toString();
            boolean signatureNeedsUpdate = !signature.equals(expectedSignature(spec));
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
                println("DRY: " + spec.address + " " + spec.name + " signature=" + signature + " -> " + expectedSignature(spec));
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
                spec.params
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + spec.name + " signature=" + expectedSignature(spec));
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
        println("ApplySignatureDebtWave795 mode=" + (dryRun ? "dry" : "apply"));

        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType longLongType = LongLongDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType ulongLongType = UnsignedLongLongDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004acde0",
                "CMeshCollisionVolume__InitContactOutputRecord",
                null,
                voidType,
                new ParameterImpl[] {},
                "Wave795 signature-debt hardening: clears the final MeshCollisionVolume exact-undefined return while preserving the Wave445 boundary. This is a shared contact-output tail block reached by a conditional jump from CMeshCollisionVolume__VFunc_03_004ac6e0 at 0x004acd22, not a clean source-level callable boundary. The block uses hidden EBX as the contact/output record, copies caller-frame stack values at +0x40/+0x44/+0x48/+0x4c into record +0x10/+0x14/+0x18/+0x1c, zeroes record +0x00/+0x04/+0x08, copies caller-frame stack +0x20 into record +0x0c, sets record +0x20 to 1, then falls into the parent-style register restore and RET 0x10 epilogue. Static retail instruction/decompile/xref evidence only; exact contact-record layout, hidden EBX/caller-frame ABI, source boundary, runtime collision behavior, and rebuild parity remain unproven.",
                tags("meshcollisionvolume", "tail-block", "hidden-ebx", "retail-collision", "undefined-signature-cleared")
            ),
            new Spec(
                "0x0056a140",
                "__allshl",
                "__fastcall",
                longLongType,
                new ParameterImpl[] {
                    param("shift_count", byteType),
                    param("value_high", intType)
                },
                "Wave795 signature-debt hardening: Visual Studio library-matched signed 64-bit left-shift helper. Pre-Wave795 decompile renders longlong __fastcall __allshl(byte, int), with shift_count in CL, value_high in the rendered register parameter, the low dword hidden in EAX, and the shifted result returned in EDX:EAX. Called by CRT__InputFormatCore at 0x00563486 and 0x005634d6. Static retail CRT helper evidence only; exact compiler CRT source version, hidden EAX/EDX ABI contract, runtime arithmetic behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-studio", "integer64-shift", "crt-runtime", "undefined-signature-cleared")
            ),
            new Spec(
                "0x005d0648",
                "__setjmp3",
                "__cdecl",
                intType,
                new ParameterImpl[] {
                    param("jmp_buffer", voidPtr),
                    param("unwind_count", intType),
                    param("registration_record", voidPtr),
                    param("try_level_or_unwind_value", intType)
                },
                "Wave795 signature-debt hardening: Visual Studio library-matched __setjmp3 helper. Pre-Wave795 instruction/decompile evidence stores EBP/EBX/EDI/ESI/ESP/return-address into the jmp buffer, writes magic 0x56433230, records the FS exception-list pointer, optionally stores registration_record and try-level/unwind data, and copies up to six additional hidden stack dwords when unwind_count exceeds two. Static retail CRT helper evidence only; exact jmp-buffer layout, vararg tail contract, SEH runtime behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-studio", "setjmp", "seh", "undefined-signature-cleared")
            ),
            new Spec(
                "0x005d06d0",
                "__aullshr",
                "__fastcall",
                ulongLongType,
                new ParameterImpl[] {
                    param("shift_count", byteType),
                    param("value_high", uintType)
                },
                "Wave795 signature-debt hardening: Visual Studio library-matched unsigned 64-bit logical right-shift helper. Pre-Wave795 decompile renders ulonglong __fastcall __aullshr(byte, uint), with shift_count in CL, value_high in the rendered register parameter, the low dword hidden in EAX, and the shifted result returned in EDX:EAX. Retail xref comes from CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4 at 0x005854f6. Static retail CRT helper evidence only; exact compiler CRT source version, hidden EAX/EDX ABI contract, runtime arithmetic behavior, and rebuild parity remain unproven.",
                tags("library-match", "visual-studio", "integer64-shift", "crt-runtime", "undefined-signature-cleared")
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
            throw new IllegalStateException("Wave795 apply encountered missing/bad rows");
        }
    }
}
