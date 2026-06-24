//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyGroundUnitVehicleWave392 extends GhidraScript {
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
            "ground-unit-vehicle-wave392",
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
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0047c730",
                "CGroundUnit__Init",
                "__thiscall",
                voidType,
                "Wave392 signature/comment hardening: CGroundUnit vtable 0x005e32d4 slot 9 points here. The body delegates to CUnit__Init, copies profile movement fields, scans Thruster markers, adds linked nodes to the +0x1d4 set, and initializes +0x1e4/+0x250/+0x254/+0x25c state. GroundUnit.cpp source body is missing from Stuart source; concrete layout, runtime behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {},
                tags("cgroundunit", "init", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_data", voidPtr)
                }
            ),
            new Spec(
                "0x0047c8e0",
                "CGroundUnit__CreateCollisionSphere",
                "__thiscall",
                voidType,
                "Wave392 signature/comment hardening: CGroundUnit vtable 0x005e32d4 slot 35 and CGroundVehicle vtable 0x005e297c slot 35 point here. The body creates a radius-derived CLine collision sphere when collision_owner+0x0c is empty, stores it, and calls CThing__AddCollision. Exact collision structure layout, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cgroundunit", "collision", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("collision_owner", voidPtr)
                }
            ),
            new Spec(
                "0x0047c970",
                "CGroundUnit__UpdateLinkedEffectsByHeightClearance",
                "__fastcall",
                voidType,
                "Wave392 owner correction: CGroundUnit vtable 0x005e32d4 slot 66 points here, superseding the over-specific CCannon owner label. The helper samples height clearance, finalizes or updates the linked +0x1d4/+0x1e4 effect state, adjusts motion/attachment state including +0x25c, and calls CUnit__UpdateMotionAttachmentsAndEffects. Cross-subclass xrefs remain expected; GroundUnit.cpp source body is missing, so exact source identity, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CCannon__UpdateLinkedEffectsByHeightClearance"},
                tags("cgroundunit", "height-clearance", "linked-effects", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047ce80",
                "CGroundUnit__MarkDestroyedAndResetState",
                "__fastcall",
                intType,
                "Wave392 owner correction: CGroundUnit vtable 0x005e32d4 slot 50 points here, superseding the over-specific CCannon owner label. The body calls CUnit__MarkDestroyedAndCleanupLinks, returns 0 on failure, clears +0x25c on success, and returns 1. Cross-subclass xrefs remain expected; exact source identity, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"CCannon__MarkDestroyedAndResetState"},
                tags("cgroundunit", "destruction-reset", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047cea0",
                "CGroundUnit__ClearLinkedThingFlagsAndResetCounter",
                "__fastcall",
                voidType,
                "Wave392 owner correction: this body walks the GroundUnit linked set at +0x1d4, calls CUnit__FinalizeLinkedUnitStateAndClear for each linked unit, and clears +0x1e4. This supersedes the older CUnitAI owner label because the same fields are initialized by CGroundUnit__Init and used by the GroundUnit height-clearance helper. Exact source identity, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ClearLinkedThingFlagsAndResetCounter"},
                tags("cgroundunit", "linked-effects", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047cfd0",
                "CGroundVehicle__Init",
                "__thiscall",
                voidType,
                "Wave392 signature/comment hardening: CGroundVehicle vtable 0x005e297c slot 9 points here. The body delegates to CGroundUnit__Init, checks the WheelMotion animation token, installs either CMCGroundVehicle or CMCBuggy motion control, constructs CGroundVehicleGuide, and installs a Warspite-related component at +0x13c. GroundVehicle.cpp source body is missing; concrete layouts, runtime behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {},
                tags("cgroundvehicle", "init", "component-create", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_data", voidPtr)
                }
            ),
            new Spec(
                "0x0047d590",
                "CGroundVehicleGuide__Constructor",
                "__thiscall",
                voidPtr,
                "Wave392 signature/name hardening: CGroundVehicle__Init allocates the CGroundVehicleGuide object and calls this constructor. The body calls CGuide__ctor_base, allocates two small owned buffers, installs CGroundVehicleGuide vtable 0x005dbd90, and stores CUnit__GetGridMapByType(owner_unit) at +0x20. Exact guide layout, runtime guide behavior, and rebuild parity remain unproven.",
                new String[] {"CGroundVehicleGuide__ctor_like_0047d590"},
                tags("cgroundvehicleguide", "constructor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_unit", voidPtr)
                }
            ),
            new Spec(
                "0x0047d650",
                "CGroundVehicleGuide__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave392 signature/name hardening: CGroundVehicleGuide vtable 0x005dbd90 slot 1 points here. The wrapper calls CGroundVehicleGuide__Destructor, frees this when flags bit 0 is set, and returns this. Runtime destruction behavior and rebuild parity remain unproven.",
                new String[] {"CGroundVehicleGuide__VFunc_01_0047d650"},
                tags("cgroundvehicleguide", "destructor", "scalar-deleting-dtor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x0047d6d0",
                "CGroundVehicleGuide__Destructor",
                "__fastcall",
                voidType,
                "Wave392 signature/name hardening: destructor body reached by CGroundVehicleGuide__ScalarDeletingDestructor. The body frees owned fields +0x3c and +0x34 before CMonitor__Shutdown. Exact guide layout, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CGroundVehicleGuide__FreeObjectIfPresent"},
                tags("cgroundvehicleguide", "destructor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00496a50",
                "CMCGroundVehicle__Constructor",
                "__thiscall",
                voidPtr,
                "Wave392 signature/name hardening: CGroundVehicle__Init constructs this motion controller when the WheelMotion animation is absent. The body calls CMotionController__ctor_like_004bae30, installs CMCGroundVehicle vtable 0x005dc35c, stores the motion target at +0x8, and initializes +0x0c/+0x10 to 0xc479c000. Concrete controller layout, runtime motion behavior, and rebuild parity remain unproven.",
                new String[] {"CMCGroundVehicle__ctor_like_00496a50"},
                tags("cmcgroundvehicle", "constructor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("motion_target", voidPtr)
                }
            ),
            new Spec(
                "0x00496a80",
                "CMCGroundVehicle__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave392 signature/name hardening: CMCGroundVehicle vtable 0x005dc35c slot 1 points here. The wrapper calls CMCGroundVehicle__Destructor, frees this when flags bit 0 is set, and returns this. Runtime cleanup behavior and rebuild parity remain unproven.",
                new String[] {"CMCGroundVehicle__VFunc_01_00496a80"},
                tags("cmcgroundvehicle", "destructor", "scalar-deleting-dtor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x00496aa0",
                "CMCGroundVehicle__Destructor",
                "__fastcall",
                voidType,
                "Wave392 signature/name hardening: destructor body reached by CMCGroundVehicle__ScalarDeletingDestructor. The body restores CMCGroundVehicle vtable 0x005dc35c, clears +0x8, then tails into CMotionController__ctor_like_004bae50. Exact controller layout, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CMCGroundVehicle__ctor_like_00496aa0"},
                tags("cmcgroundvehicle", "destructor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0050ed10",
                "CGroundUnit__Constructor",
                "__fastcall",
                voidPtr,
                "Wave392 signature/name hardening: CWorldPhysicsManager__CreateThingByType calls this constructor for several ground-unit type cases. The body calls CActor__ctor_like_004f7e90, installs CGroundUnit primary vtable 0x005e32d4 and secondary vtable 0x005e325c, then returns this. Exact type-id mapping, runtime creation behavior, and rebuild parity remain unproven.",
                new String[] {"CGroundUnit__ctor_like_0050ed10"},
                tags("cgroundunit", "constructor", "signature-hardened", "comment-hardened"),
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
