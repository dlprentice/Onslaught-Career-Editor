//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyQueueHeadHelperWave388 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
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

    private Function functionAtEntry(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Function fn = getFunctionAt(toAddr(addressText));
        if (fn == null) {
            fn = getFunctionContaining(toAddr(addressText));
            if (fn != null && !fn.getEntryPoint().equals(toAddr(addressText))) {
                fn = null;
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: missing function at " + spec.address + " for " + spec.name);
                return;
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

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "queue-head-helper-wave388",
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
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004098c0",
                "CLine__VFunc_01_004098c0",
                "__thiscall",
                intType,
                "Wave388 queue-head helper correction: CLine vtable-slot wrapper with data xrefs from the CLine vtable region. It forwards the ECX receiver plus four stack arguments to dispatch_target vfunc +0x10. Exact argument types, dispatch target class, source identity, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cline", "vtable-wrapper", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("arg0", voidPtr),
                    param("arg1", voidPtr),
                    param("dispatch_target", voidPtr),
                    param("arg3", voidPtr)
                }
            ),
            new Spec(
                "0x00409e60",
                "CGeneralVolume__ToDoubleIdentity",
                "__stdcall",
                doubleType,
                "Wave388 queue-head helper comment: x87 identity-style float-to-double helper used by JetPart yaw/pitch and GeneralVolume axis-input wrappers. The retail body computes constant - (constant - input_value). Exact source purpose, control behavior, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("general-volume", "x87", "input-axis", "comment-hardened"),
                new ParameterImpl[] {
                    param("input_value", floatType)
                }
            ),
            new Spec(
                "0x0040d320",
                "Mat34__MultiplyBasisToOut",
                "__thiscall",
                voidPtr,
                "Wave388 owner/signature correction: owner-neutral Mat34-style 3x3 basis multiply. ECX is lhs_basis, the first stack argument is out_basis, the second stack argument is rhs_basis, and the function returns out_basis in EAX after writing the 0x30-byte output basis. Broad BattleEngine, MeshPart, CMCBuggy, CMCTentacle, CMonitor, particle, tree, and render callsites make the old CMCBuggy-only owner label too narrow. Concrete matrix layout, exact source identity, locals/types, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CMCBuggy__MultiplyMat34Basis"},
                tags("mat34", "matrix-basis", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_basis", voidPtr),
                    param("rhs_basis", voidPtr)
                }
            ),
            new Spec(
                "0x00414010",
                "CMonitor__ClearCurrentTrackedEntryFlag60",
                "__thiscall",
                voidType,
                "Wave388 queue-head helper correction: calls CBattleEngineWalkerPart__GetCurrentWeapon from the receiver and clears field +0x60 on the current weapon/tracked entry when present. Callers include CMonitor__Process, CBattleEngine__Morph, and CBattleEngine__AugmentWeapon. Exact owner boundary, tracked-entry layout, runtime weapon behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("monitor", "weapon-entry", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0041ad10",
                "Vec3__AddInPlace",
                "__thiscall",
                voidType,
                "Wave388 owner/signature correction: owner-neutral Vec3 in-place add helper. ECX is the destination vector, the one stack argument is add_vec3, and RET 0x4 plus broad CMeshPart, CMCBuggy, CCylinder, CMCTentacle, sprite, and camera-adjacent callsites make the old CMCTentacle-only owner label too narrow. Concrete vector layout, exact source identity, locals/types, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CMCTentacle__AddVec3InPlace"},
                tags("vec3", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("add_vec3", voidPtr)
                }
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
            throw new IllegalStateException("Wave388 queue-head helper apply had failures");
        }
    }
}
