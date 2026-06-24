//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedCharDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFrontendPreviewWave379 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] allowedExistingNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] allowedExistingNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.allowedExistingNames = allowedExistingNames;
            this.parameters = parameters;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function findFunctionAtSpecAddress(String addressText) {
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = findFunctionAtSpecAddress(spec.address);
            if (fn == null) {
                throw new IllegalStateException("Function not found at " + spec.address);
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            if (dryRun) {
                if (!fn.getName().equals(spec.name)) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (!fn.getName().equals(spec.name)) {
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

            Function readBack = findFunctionAtSpecAddress(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (IllegalStateException ex) {
            if (ex.getMessage() != null && ex.getMessage().startsWith("Function not found")) {
                stats.missing++;
            } else {
                stats.bad++;
            }
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "frontend-preview-wave379",
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
        DataType voidPtr = PointerDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType ucharType = UnsignedCharDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00466130",
                "CGenericCamera__ctor",
                "__fastcall",
                voidType,
                "Name/comment correction: CGenericCamera constructor body sets the CGenericCamera vtable used by the multiplayer frontend preview setup. Static xref/vtable evidence only; runtime camera behavior remains unproven.",
                tags("frontend", "camera", "constructor", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CGenericCamera__ctor_like_00466130"},
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00466140",
                "CGenericCamera__GetPos",
                "__thiscall",
                voidType,
                "Signature/comment hardening: copies four dwords from this+0x34 through this+0x40 into out_pos and returns with ret 0x4. Static instruction/vtable evidence only; runtime camera position behavior remains unproven.",
                tags("frontend", "camera", "position", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("out_pos", voidPtr)}
            ),
            new Spec(
                "0x00466170",
                "CGenericCamera__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Signature/comment hardening: scalar deleting destructor calls CGenericCamera__dtor, conditionally frees this when free_flag bit 0 is set, and returns this. Static destructor evidence only; runtime camera cleanup remains unproven.",
                tags("frontend", "camera", "destructor", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("free_flag", ucharType)}
            ),
            new Spec(
                "0x004661b0",
                "CGenericCamera__dtor",
                "__fastcall",
                voidType,
                "Signature/comment hardening: destructor-base body resets the receiver vtable to the base CGenericCamera table at 0x005d9260. Static destructor evidence only; runtime camera cleanup remains unproven.",
                tags("frontend", "camera", "destructor", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x0046b950",
                "CFEPMultiplayerStart__LoadPreviewMeshFromConfig",
                "__thiscall",
                voidType,
                "Signature/comment hardening: copies transform/config data from preview_config, builds a resource descriptor from its name field, creates the preview object at +0x58, and initializes animation/timer fields +0x44/+0x48/+0x4c/+0x50/+0x54. Static decompile/xref evidence only; runtime preview mesh behavior remains unproven.",
                tags("frontend", "multiplayer", "preview", "mesh", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("preview_config", voidPtr)}
            ),
            new Spec(
                "0x0046ba90",
                "CFrontEndThing__dtor_base",
                "__fastcall",
                voidType,
                "Name/signature correction: not a constructor; destructor-base body resets the CFrontEndThing vtable and releases the preview object pointer at +0x58 when present. Static cleanup xrefs only; runtime frontend cleanup remains unproven.",
                tags("frontend", "preview", "destructor", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFrontEndThing__ctor_like_0046ba90"},
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x0046bab0",
                "CFEPMultiplayerStart__SetPreviewAnimationByName",
                "__thiscall",
                voidType,
                "Signature/comment hardening: if preview object +0x58 exposes an animation set, resolves animation_name through FindAnimationIndex, updates preview duration at +0x48, and clears timer/state field +0x4c. Static decompile/instruction evidence only; runtime preview animation behavior remains unproven.",
                tags("frontend", "multiplayer", "preview", "animation", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("animation_name", charPtr)}
            ),
            new Spec(
                "0x0046bc20",
                "CFEPMultiplayerStart__StopPreviewAnimation",
                "__fastcall",
                voidType,
                "Signature/comment hardening: if preview object +0x58 exists, dispatches its vcall +0x08 with zero and returns. Static render-path xrefs only; runtime preview animation behavior remains unproven.",
                tags("frontend", "multiplayer", "preview", "animation", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x0046c030",
                "CThingCamera__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Name/signature correction: scalar deleting destructor calls CThingCamera__dtor_base, conditionally frees this when free_flag bit 0 is set, and returns this. Static vtable/destructor evidence only; runtime thing-camera cleanup remains unproven.",
                tags("frontend", "camera", "thing-camera", "destructor", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CThingCamera__VFunc_08_0046c030"},
                new ParameterImpl[] {param("this", voidPtr), param("free_flag", ucharType)}
            ),
            new Spec(
                "0x0046c050",
                "CThingCamera__dtor_base",
                "__fastcall",
                voidType,
                "Name/signature correction: not a constructor; destructor-base body removes the linked reader cell at this+0x4 from its set when present, then resets the receiver to the base CGenericCamera vtable. Static destructor evidence only; runtime thing-camera cleanup remains unproven.",
                tags("frontend", "camera", "thing-camera", "destructor", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CCamera__ctor_like_0046c050"},
                new ParameterImpl[] {param("this", voidPtr)}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave379 frontend preview apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
