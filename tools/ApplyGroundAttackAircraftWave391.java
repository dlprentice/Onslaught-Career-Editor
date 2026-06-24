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

public class ApplyGroundAttackAircraftWave391 extends GhidraScript {
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
            "ground-attack-aircraft-wave391",
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
                "0x0047bab0",
                "CGroundAttackAI__InitState",
                "__fastcall",
                voidType,
                "Wave391 RTTI owner correction: called immediately after the CGroundAttackAI allocation/vtable install in CGroundAttackAircraft__Init. The body clears field +0x60, randomizes the +0x64 timer/float, and calls CGroundAttackAircraft__CloseBay. GroundAttackAircraft.cpp source body is missing from Stuart source; concrete layout, runtime behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CGroundAttackAircraft__InitState"},
                tags("cgroundattackai", "init-state", "bay-state", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047bbf0",
                "CGroundAttackAircraft__Init",
                "__thiscall",
                voidType,
                "Wave391 lifecycle correction: function table 0x005e2bf0 slot 0 points here and the body delegates to CAirUnit__Init before allocating/installing CMCGroundAttack, CGroundAttackAI, and CGroundAttackGuide components. It initializes default animation/state fields and seeds a random timing value. Corrects the older constructor label; concrete layouts, runtime behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CGroundAttackAircraft__Constructor"},
                tags("cgroundattackaircraft", "init", "component-create", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_data", voidPtr)
                }
            ),
            new Spec(
                "0x0047bd70",
                "CGroundAttackAI__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave391 RTTI owner correction: CGroundAttackAI vtable 0x005dbd4c slot 1 points here. The wrapper calls CGroundAttackAI__Destructor, frees this when flags bit 0 is set, and returns this. Corrects the older GroundAttackAircraft owner label; runtime destruction behavior and rebuild parity remain unproven.",
                new String[] {"CGroundAttackAircraft__ScalarDeletingDestructor"},
                tags("cgroundattackai", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x0047bd90",
                "CGroundAttackAI__Destructor",
                "__fastcall",
                voidType,
                "Wave391 RTTI owner correction: destructor body reached by the CGroundAttackAI scalar-deleting wrapper. The body restores the CUnitAI base vtable 0x005d8d1c, removes linked reader/set fields at observed offsets +0x28, +0x24, and +0x0c when present, then calls CMonitor__Shutdown. Concrete layout, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CGroundAttackAircraft__Destructor"},
                tags("cgroundattackai", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047be30",
                "CGroundAttackGuide__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave391 RTTI owner correction: CGroundAttackGuide vtable 0x005dbd20 slot 1 points here. The wrapper calls CGroundAttackGuide__Destructor, frees this when flags bit 0 is set, and returns this. Corrects the stale GillMHead label; runtime destruction behavior and rebuild parity remain unproven.",
                new String[] {"CGillMHead__ScalarDeletingDestructor2"},
                tags("cgroundattackguide", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x0047be50",
                "CGroundAttackGuide__Destructor",
                "__fastcall",
                voidType,
                "Wave391 RTTI owner correction: destructor body reached by the CGroundAttackGuide scalar-deleting wrapper. The body removes the linked reader/set field at +0x2c when present, then calls CMonitor__Shutdown. Corrects the stale GillMHead label; concrete layout, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMHead__Destructor2"},
                tags("cgroundattackguide", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047bfa0",
                "CGroundAttackAircraft__OpenBay",
                "__fastcall",
                voidType,
                "Wave391 signature/comment hardening: if bay state +0x27c is idle or closing, the body sets state 2 and plays the open animation token through the model animation database. Static retail evidence only; exact state enum, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cgroundattackaircraft", "bay-state", "animation-state", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047bff0",
                "CGroundAttackAircraft__CloseBay",
                "__fastcall",
                voidType,
                "Wave391 signature/comment hardening: if bay state +0x27c is open or opening, the body sets state 3 and plays the close animation token through the model animation database. Static retail evidence only; exact state enum, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cgroundattackaircraft", "bay-state", "animation-state", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047c040",
                "CGroundAttackAircraft__AdvanceCloseShootAnimationState",
                "__fastcall",
                intType,
                "Wave391 owner correction: GroundAttackAircraft function table 0x005e2bf0 slot 50 points here. The body compares the current animation against open, shoot, and close tokens, advances to shoot or idle animation, and writes bay state +0x27c. Corrects the older broad CUnitAI label; exact source identity, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__AdvanceCloseShootAnimationState"},
                tags("cgroundattackaircraft", "bay-state", "animation-state", "owner-corrected", "signature-hardened", "comment-hardened"),
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
