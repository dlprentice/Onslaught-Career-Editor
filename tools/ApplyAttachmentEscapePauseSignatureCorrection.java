//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyAttachmentEscapePauseSignatureCorrection extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedCurrentNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedCurrentNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedCurrentNames = allowedCurrentNames;
            this.tags = tags;
            this.parameters = parameters;
        }
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

    private Function getFunctionOrThrow(String addressText) throws Exception {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addressText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private boolean allowedName(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedCurrentNames) {
            if (currentName.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String signatureText(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ");
        sb.append(spec.callingConvention).append(" ");
        sb.append(spec.name).append("(");
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

    private void applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!allowedName(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return;
        }

        if (!fn.getName().equals(spec.name)) {
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
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = getFunctionOrThrow(spec.address);
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "attachment-escape-pause-wave365",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec("0x0044a830", "VFuncSlot_03_0044a830", "__thiscall", voidType,
                "Wave365 signature/comment/tag hardening: shared vtable-slot body copies three dwords from source_vector3 into this+0x08..this+0x10 and returns with ret 0x4. CRadarWarningReceiver__Init calls it to copy a config-vector payload before reading range/update interval fields. Owner unresolved by this tranche; exact source identity, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("signature-hardened", "owner-deferred"),
                new ParameterImpl[] {param("this", voidPtr), param("source_vector3", voidPtr)}),
            new Spec("0x0044a850", "OID__GetAttachmentOrOriginTransform", "__thiscall", voidType,
                "Wave365 signature/comment/tag hardening: OID attachment helper reads the attachment id at this+0x0c, falls back to the base object position at +0x1c when no attachment is selected or the attachment origin is sentinel, and otherwise queries vfunc +0x160 to populate out_origin. Static retail evidence only; exact OID structure layout, attachment selector meaning, runtime targeting behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("oid", "attachment", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("out_origin", voidPtr)}),
            new Spec("0x0044a930", "OID__GetAttachmentOrBaseOrientationMatrix", "__thiscall", voidType,
                "Wave365 signature/comment/tag hardening: OID attachment helper reads the attachment id at this+0x0c, falls back to the base orientation matrix at +0x3c when no attachment is selected or the attachment origin is sentinel, and otherwise queries vfunc +0x160 to populate out_matrix. Static retail evidence only; exact OID structure layout, attachment selector meaning, runtime targeting behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("oid", "attachment", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("out_matrix", voidPtr)}),
            new Spec("0x0044aab0", "CEscapePod__InitRocketMeshAndEngineEffect", "__thiscall", voidType,
                "Wave365 owner/name/signature hardening: CEscapePod init-style body adjusts init flags, builds a CResourceDescriptor for m_rocket.msh, creates the render/resource object, calls CActor__Init, then attaches the Muspell_Engine_Small_Effect particle effect when its node is found. Static retail evidence only; exact source method name, concrete CEscapePod/init layouts, runtime escape-pod behavior, and rebuild parity remain unproven.",
                new String[] {"CEscapePod__VFunc_09_0044aab0"},
                tags("escape-pod", "initializer", "owner-corrected"),
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec("0x0044adb0", "CEulerAngles__ctor_from_FMatrix", "__thiscall", voidPtr,
                "Wave365 owner correction: CEulerAngles constructor-style helper derives yaw/pitch/roll from an FMatrix using OID__AcosWrapper and fpatan, zeroing yaw/roll in the singular fallback path. Corrects the stale CExplosionInitThing owner label; source CEulerAngles callsites exist, but exact math convention, concrete FMatrix layout, runtime orientation behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__ExtractYawPitchFromMatrixIfValid"},
                tags("math", "euler", "owner-corrected"),
                new ParameterImpl[] {param("this", voidPtr), param("matrix", voidPtr)}),
            new Spec("0x0044ae20", "CPauseMenu__InitAndSetActiveReader", "__thiscall", voidPtr,
                "Wave365 signature/comment/tag hardening: binding prompt helper initializes the local active-reader cell, stores action_id in the 16-bit field at +0x04, binds reader through CGenericActiveReader__SetReader, returns this, and ends with ret 0x8. Static retail evidence only; exact pause-menu action layout, source identity, runtime control-binding behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("pause-menu", "active-reader", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("action_id", intType), param("reader", voidPtr)}),
        };

        int updated = 0;
        int skipped = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun);
                if (dryRun) {
                    skipped++;
                }
                else {
                    updated++;
                }
            }
            catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println("targets=" + specs.length + " updated=" + updated + " skipped=" + skipped + " failed=" + failed + " dry=" + dryRun);
        if (failed != 0) {
            throw new IllegalStateException("Failed targets: " + failed);
        }
    }
}
