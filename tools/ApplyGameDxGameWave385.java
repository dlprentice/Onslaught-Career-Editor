//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyGameDxGameWave385 extends GhidraScript {
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
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        if (spec.parameters.length == 0) {
            sb.append("void");
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
            "game-dxgame-wave385",
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
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0046c210",
                "CGame__ctor",
                "__fastcall",
                voidPtr,
                "Wave385 owner correction: CGame constructor, not an IController-only constructor. Retail evidence starts from the IController vtable at 0x005d9388, initializes monitor/list state, source-visible CGame settings and state fields, then installs the CGame vtable at 0x005dbbb4. Static retail/source/RTTI evidence only; exact layout, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"IController__ctor_like_0046c210"},
                tags("cgame", "constructor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x0046c2b0",
                "CGame__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave385 owner correction: scalar-deleting destructor wrapper for CGame. It calls CGame__dtor, checks the caller delete flag, optionally frees this through OID__FreeObject, and returns this. Static retail evidence only; runtime deletion behavior and rebuild parity remain unproven.",
                new String[] {"CGame__VFunc_01_0046c2b0"},
                tags("cgame", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}
            ),
            new Spec(
                "0x0046c2d0",
                "CGame__dtor",
                "__fastcall",
                voidType,
                "Wave385 owner correction: CGame destructor body, not a constructor. It restores the CGame vtable, unregisters active-reader style links at this+0xa04 and this+0x9f8 when present, then calls CMonitor__Shutdown. Static retail evidence only; exact layout, runtime shutdown behavior, and rebuild parity remain unproven.",
                new String[] {"CGame__ctor_like_0046c2d0", "CGame__dtor"},
                tags("cgame", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00541f00",
                "CDXGame__dtor_thunk",
                "__fastcall",
                voidType,
                "Wave385 owner correction: CDXGame destructor thunk. The function is an unconditional jump to CGame__dtor; source shows CDXGame derives from CGame and retail RTTI resolves the adjacent secondary vtable to CDXGame. Static retail/source/RTTI evidence only; runtime destruction behavior and rebuild parity remain unproven.",
                new String[] {"CGame__ctor_like_0046c2d0", "CGame__dtor"},
                tags("dxgame", "destructor", "jump-thunk", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00541f10",
                "CDXGame__ctor",
                "__fastcall",
                voidPtr,
                "Wave385 owner correction: CDXGame constructor, not CFrontEndVideo. It calls CGame__ctor, then installs the CDXGame secondary vtable at 0x005e509c; RTTI at that vtable resolves to CDXGame and Stuart source defines CDXGame : CGame. Static retail/source/RTTI evidence only; runtime DirectX game construction and rebuild parity remain unproven.",
                new String[] {"CFrontEndVideo__CFrontEndVideo"},
                tags("dxgame", "constructor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00541f30",
                "CDXGame__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave385 owner correction: scalar-deleting destructor wrapper for CDXGame, not CFrontEndVideo. It calls CDXGame__dtor_thunk, checks the caller delete flag, optionally frees this through OID__FreeObject, and returns this. Static retail/RTTI evidence only; runtime deletion behavior and rebuild parity remain unproven.",
                new String[] {"CFrontEndVideo__scalar_dtor"},
                tags("dxgame", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}
            ),
            new Spec(
                "0x00541120",
                "CBinkOpenThread__ctor",
                "__fastcall",
                voidPtr,
                "Wave385 owner correction: CBinkOpenThread constructor, not CFrontEndVideo destructor. It calls the CWaitingThread constructor at 0x00528bc0, installs vtable 0x005e5078, and RTTI for that vtable resolves to CBinkOpenThread. Static retail/RTTI evidence only; adjacent vtable-slot body at 0x00541140, runtime Bink thread behavior, and rebuild parity remain unproven.",
                new String[] {"CFrontEndVideo__dtor"},
                tags("bink-open-thread", "constructor", "owner-corrected", "signature-hardened", "comment-hardened"),
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
            throw new IllegalStateException("Wave385 CGame/CDXGame apply had failures");
        }
    }
}
