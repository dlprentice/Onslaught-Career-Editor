//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyFrontendMediaCommonVideoTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] allowedExistingNames;
        final ParameterImpl[] parameters;
        final boolean createIfMissing;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] allowedExistingNames,
                ParameterImpl[] parameters,
                boolean createIfMissing) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.allowedExistingNames = allowedExistingNames;
            this.parameters = parameters;
            this.createIfMissing = createIfMissing;
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

    private Function createMissingFunction(Spec spec) throws Exception {
        Address address = addr(spec.address);
        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, spec.name);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + spec.address + " (disassemble=" + disasmOk + ")");
        }
        return created;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = findFunctionAtSpecAddress(spec.address);
            boolean missing = fn == null;
            if (missing && !spec.createIfMissing) {
                throw new IllegalStateException("Function not found at " + spec.address);
            }
            if (fn != null && !allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            if (dryRun) {
                if (missing) {
                    stats.wouldCreate++;
                } else if (!fn.getName().equals(spec.name)) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " -> " + expectedSignature(spec) + (missing ? " (create)" : ""));
                stats.skipped++;
                return;
            }

            if (missing) {
                fn = createMissingFunction(spec);
                stats.created++;
            } else if (!fn.getName().equals(spec.name)) {
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
            "frontend-media-wave374",
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
        DataType boolType = BooleanDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec("0x00452b00", "CFEPCommon__Init", "__thiscall", boolType,
                "Boundary/name/signature correction: CFEPCommon vtable init slot was previously missing as a function object. It clears this+0x4, opens the common FEBack128.vid menu background through CDXFrontEndVideo__Open, and returns true. Static retail/source-correlated evidence only; exact class layout, runtime video behavior, and rebuild parity remain unproven.",
                tags("frontend", "common-page", "video", "boundary-created", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)},
                true),

            new Spec("0x00452b30", "CFEPCommon__Shutdown", "__thiscall", voidType,
                "Name/signature correction: CFEPCommon teardown vfunc calls CDXFrontEndVideo__CloseVideo, frees the owned this+0x4 object when present through OID__FreeObject, and clears the pointer. Static retail/source-correlated evidence only; exact class layout, runtime video behavior, and rebuild parity remain unproven.",
                tags("frontend", "common-page", "video", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPCommon__VFunc_01_00452b30"},
                new ParameterImpl[] {param("this", voidPtr)},
                false),

            new Spec("0x00452b60", "CFrontEndPage__Process_NoOp", "__thiscall", voidType,
                "Signature/comment correction: shared frontend page process no-op. Instruction body is RET 0x4, matching a thiscall receiver plus one state stack argument; broad vtable and wrapper call references reuse it as a harmless default process slot. Static retail evidence only; exact caller type identities, runtime behavior, and rebuild parity remain unproven.",
                tags("frontend", "frontend-page", "shared-noop", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("state", intType)},
                false),

            new Spec("0x00452ce0", "CFrontEnd__RenderVideoQuadScaledToWindow", "__stdcall", voidType,
                "Signature/comment correction: frontend video-quad render helper. It resolves default center coordinates from PLATFORM window dimensions when the sentinel center is passed, sets D3D render state, scales width/height against the window, and calls CDXFrontEndVideo__Render with the ARGB value. Static retail evidence only; exact source method identity, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("frontend", "video", "render", "signature-hardened", "comment-hardened"),
                new String[] {},
                new ParameterImpl[] {param("scale", floatType), param("argb", intType), param("center_x", floatType), param("center_y", floatType)},
                false),

            new Spec("0x00452da0", "SharedVFunc__NoOp_Ret08", "__stdcall", voidType,
                "Owner/name/signature correction: zero-body shared vtable target consists of RET 0x8 and is referenced by broad unrelated vtables plus a dispatch-post-hook caller, so the older slot-specific label was too narrow. Static retail evidence only; exact semantic contract, caller type systems, runtime behavior, and rebuild parity remain unproven.",
                tags("shared-noop", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"VFuncSlot_06_00452da0"},
                new ParameterImpl[] {param("unused0", intType), param("unused1", intType)},
                false),

            new Spec("0x00452db0", "CFEPCommon__StartVideo", "__thiscall", voidType,
                "Owner/name/signature correction: source-correlated CFEPCommon::StartVideo-style helper used by the Goodies FMV return path and another frontend call site. It opens data/video/FEBack128.vid through CDXFrontEndVideo__Open with 0x80 by 0x80 dimensions and consumes one start_flag stack argument. Static retail/source-correlated evidence only; exact flag meaning, runtime video behavior, and rebuild parity remain unproven.",
                tags("frontend", "common-page", "video", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPGoodies__OpenVideo", "CFEPGoodies__Helper_00452db0"},
                new ParameterImpl[] {param("this", voidPtr), param("start_flag", intType)},
                false),

            new Spec("0x00452de0", "CFEPCommon__StopVideo", "__thiscall", voidType,
                "Owner/name/signature correction: source-correlated CFEPCommon::StopVideo-style helper used by the Goodies FMV path. The body tail-jumps to CDXFrontEndVideo__CloseVideo after selecting the frontend video singleton. Static retail/source-correlated evidence only; runtime video behavior and rebuild parity remain unproven.",
                tags("frontend", "common-page", "video", "owner-corrected", "name-corrected", "signature-hardened", "comment-hardened"),
                new String[] {"CFEPGoodies__CloseVideo", "CFEPGoodies__Helper_00452de0"},
                new ParameterImpl[] {param("this", voidPtr)},
                false)
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped + " created=" + stats.created + " would_create=" + stats.wouldCreate + " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename + " missing=" + stats.missing + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Frontend/media common video tranche failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
