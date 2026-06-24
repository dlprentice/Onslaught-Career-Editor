//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyGillMFamilyWave389 extends GhidraScript {
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
            "gillm-family-wave389",
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
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004799c0",
                "CGillM__VFunc09_InitGroundedSpawnState",
                "__thiscall",
                voidType,
                "Wave389 CGillM owner/signature correction: CGillM RTTI vtable 0x005e0b30 slot 9. The body clears cooldown field +0x26c, stamps +0x270 from the global timer, adjusts the spawn/init state flag fields, calls the inherited slot-9 body, samples static-shadow ground height, marks +0x274 grounded, and snapshots current position into +0x278. Static retail evidence only; exact source method name, concrete layouts, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CGillM__VFunc_09_004799c0"},
                tags("cgillm", "vtable-slot", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("spawn_state", voidPtr)
                }
            ),
            new Spec(
                "0x00479a50",
                "CGillM__InitLegMotion",
                "__thiscall",
                voidType,
                "Wave389 signature/comment hardening: CGillM vtable 0x005e0b30 slot 117 points here. The body looks up the LegMotion animation, allocates a 0xf0-byte CMCGillM motion-controller object with GillM.cpp line 0x2d evidence, installs CMCGillM vtable 0x005dbc74, stores it at this+0x70, and seeds CMCMech motion parameters from init data. Static retail evidence only; concrete init-data layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cgillm", "cmcgillm", "legmotion", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_data", voidPtr)
                }
            ),
            new Spec(
                "0x00479b40",
                "SharedCMCMech__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave389 shared-destructor correction: CMCBattleEngine, CMCGillM, and CMCThunderHead RTTI vtables all point slot 1 at this scalar-deleting destructor body. It calls CMCMech__Destructor, frees this when flags bit 0 is set, and returns this. Static retail evidence only; exact derived-class destructor ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_01_00479b40"},
                tags("shared-cmc", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x00479b60",
                "CGillM__InitGillMAIComponent",
                "__thiscall",
                voidType,
                "Wave389 owner/signature correction: CGillM vtable 0x005e0b30 slot 118 points here. The body allocates a 0x60-byte object with GillM.cpp line 0x38 evidence, initializes it through CWarspite__Init, installs CGillMAI RTTI vtable 0x005dbcb4, and stores the component at this+0x13c. Static retail evidence only; exact AI layout, source method name, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CGillM__InitWarspiteComponent"},
                tags("cgillm", "cgillmai", "warspite-base", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_data", voidPtr)
                }
            ),
            new Spec(
                "0x00479bf0",
                "CGillMAI__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave389 destructor correction: CGillMAI RTTI vtable 0x005dbcb4 slot 1 points here. The wrapper calls CGillMAI__Destructor, frees this when flags bit 0 is set, and returns this. Static retail evidence only; exact source destructor identity, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMAI__VFunc_01_00479bf0"},
                tags("cgillmai", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x00479c10",
                "CGillMAI__Destructor",
                "__fastcall",
                voidType,
                "Wave389 destructor correction: body called only by the CGillMAI scalar-deleting destructor in this read-back. It restores the base CUnitAI-style vtable, removes tracked set entries at this+0x28, this+0x24, and this+0x0c when linked, then calls CMonitor__Shutdown. Static retail evidence only; exact base-layout identity, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ctor_like_00479c10"},
                tags("cgillmai", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00479cb0",
                "CGillM__InitTerrainGuideComponent",
                "__fastcall",
                voidType,
                "Wave389 owner/name/signature correction: CGillM vtable 0x005e0b30 slot 119 points here. The body allocates a 0x20-byte object with GillM.cpp line 0x3e evidence, initializes it through CTerrainGuide__ctor_like_004f1ec0, and stores the result at this+0x208. Static retail evidence only; exact guide layout, source method name, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CGillM__InitComponent208"},
                tags("cgillm", "terrain-guide", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00479d10",
                "CGillM__UpdateGroundedVerticalDrift",
                "__fastcall",
                voidType,
                "Wave389 owner correction from the older CExplosionInitThing label: CGillM RTTI vtable 0x005e0b30 slot 66 points here. The body uses +0x274 grounded state, +0x244 mode/state, static-shadow height sampling, and vertical drift fields +0x84/+0xcc before dispatching the shared update helper. Static retail evidence only; exact source name, field meanings, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__UpdateGroundedVerticalDrift"},
                tags("cgillm", "grounded-state", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00479db0",
                "CGillM__TriggerRandomArmHitAnimationIfReady",
                "__fastcall",
                voidType,
                "Wave389 owner/name correction from the older CExplosionInitThing label: GillM-family body with Gill_M_Left_Arm and Gill_M_Right_Arm string evidence. It gates on cooldown field +0x26c, walks the child/component list at +0x19c, selects a left/right arm token from the random result, calls the hit-animation helper for the matching arm, then resets the cooldown timer. Static retail evidence only; exact source name, arm-list layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__TriggerRandomGillArmSubEffect"},
                tags("cgillm", "arm-hit-animation", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00479f30",
                "CGillM__ComputeTerrainClearanceNoiseScale",
                "__fastcall",
                doubleType,
                "Wave389 owner correction from the older CUnitAI label: GillM-family terrain helper reached from the CMCGillM slot-wrapper region. It gates on +0x274, +0x244, and motion-vector magnitude, samples two static-shadow heights, derives a slope/angle value, and scales the result. Static retail evidence only; exact source name, field meanings, runtime movement behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ComputeTerrainClearanceNoiseScale"},
                tags("cgillm", "terrain", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047a0b0",
                "CGillM__ComputeLateralSlopeAlignment",
                "__fastcall",
                doubleType,
                "Wave389 owner correction from the older CUnitAI label: GillM-family lateral terrain-alignment helper reached from the CMCGillM slot-wrapper region. The body uses heading field +0x114, samples a heightfield normal at the current position, projects lateral slope alignment, and returns a scalar. Static retail evidence only; exact source name, field meanings, runtime movement behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ComputeLateralSlopeAlignment"},
                tags("cgillm", "terrain", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
