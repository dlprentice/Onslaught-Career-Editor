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

public class ApplyGillMHeadAIWave390 extends GhidraScript {
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
            "gillmhead-ai-wave390",
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
                "0x0047a760",
                "CGillMHead__CreateGillMHeadAIComponent",
                "__thiscall",
                voidType,
                "Wave390 owner/name/signature correction: GillMHead.cpp allocation path at line 0x13. The function allocates a 0x64-byte type-0x16 object, initializes it through CWarspite__Init with the owner and init data, installs the CGillMHeadAI RTTI vtable 0x005dbcec, clears field +0x60, and stores the component at this+0x13c. Static retail evidence only; exact source method name, concrete layouts, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMHead__Create"},
                tags("cgillmhead", "cgillmheadai", "component-create", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_data", voidPtr)
                }
            ),
            new Spec(
                "0x0047a7f0",
                "CGillMHeadAI__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave390 RTTI owner correction: CGillMHeadAI vtable 0x005dbcec slot 1 points here. The wrapper calls CGillMHeadAI__Destructor, frees this when flags bit 0 is set, and returns this. Static retail evidence only; runtime destruction behavior and rebuild parity remain unproven.",
                new String[] {"CGillMHead__ScalarDeletingDestructor"},
                tags("cgillmheadai", "destructor", "scalar-deleting-dtor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x0047a810",
                "CGillMHeadAI__Destructor",
                "__fastcall",
                voidType,
                "Wave390 RTTI owner correction: destructor body reached by the CGillMHeadAI scalar-deleting wrapper. The body restores the CUnitAI base vtable 0x005d8d1c, removes linked active-reader/resource handles at offsets +0x28, +0x24, and +0x0c when present, then calls CMonitor__Shutdown. Static retail evidence only; concrete layout, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMHead__Destructor"},
                tags("cgillmheadai", "destructor", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047a8b0",
                "CGillMHeadAI__TryTransitionIdleToOpen",
                "__fastcall",
                intType,
                "Wave390 RTTI owner/signature correction: GillMHead AI state helper referenced from pointer table 0x005e42d8 slot 30. It checks the current animation against idle, gates through CUnit__UpdateDeployStateAndChargeEffects, then asks the shared animation helper to play open. Static retail evidence only; exact source method name, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMHead__TryTransitionIdleToOpen"},
                tags("cgillmheadai", "animation-state", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047a900",
                "CGillMHeadAI__AdvanceOpenAttackCloseState",
                "__fastcall",
                intType,
                "Wave390 RTTI owner/signature correction: GillMHead AI state helper referenced from pointer table 0x005e42d8 slot 3. It compares the current animation against open, attack, close, and idle tokens, uses a target/timeout gate before close, and requests shared animation playback transitions. Static retail evidence only; exact source method name, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMHead__AdvanceOpenAttackCloseState"},
                tags("cgillmheadai", "animation-state", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047afc0",
                "CGillMHeadAI__UpdateAimTransformAndTargetReader",
                "__fastcall",
                voidType,
                "Wave390 RTTI owner/name/signature correction: CGillMHeadAI vtable 0x005dbcec slot 3 points here. The body dispatches the base update slot, checks target/range state, selects the support/escort target, computes an aim transform 100 units along the owner facing vector, calls CWarspite__UpdateAimTransformAndAttachTargetReader, and dispatches an owner vfunc afterward. Static retail evidence only; exact source method name, concrete layout, runtime targeting behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMHead__Update"},
                tags("cgillmheadai", "targeting", "warspite-base", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0047b090",
                "CGillMHeadAI__UpdateTargetBallisticArcFlags",
                "__fastcall",
                voidType,
                "Wave390 owner/name/signature correction from the older setup-model wording: CGillMHeadAI vtable 0x005dbcec slot 4 points here. The body clears a stale target reader when flagged, selects support/escort context, updates two ballistic firing-readiness flags through CUnit__CanFireAtTarget_BallisticArcB/A, and falls back through vfunc +0x2c when no usable target is present. Static retail evidence only; exact source method name, concrete layout, runtime firing behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMHead__SetupModel"},
                tags("cgillmheadai", "targeting", "ballistic-arc", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004d0ff0",
                "CPauseMenu__InitPauseSession",
                "__thiscall",
                voidType,
                "Wave390 signature/comment hardening: CGame__Pause calls this on CGame::mPauseMenu when pause-menu activation is requested. The body initializes pause-menu session state, timestamps, iterator/selection state, control-context latch field +0x48, and enables/disables an objective-dependent menu item. Static retail evidence only; exact CPauseMenu layout, UI runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cpausemenu", "pause-flow", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("activate_control", intType)
                }
            ),
            new Spec(
                "0x004d10b0",
                "CPauseMenu__DeactivatePauseSession",
                "__thiscall",
                voidType,
                "Wave390 owner/name/signature correction from the older GillMHead label: CGame__UnPause calls this on CGame::mPauseMenu when free camera is not active. The body clears active state field +0x10, timestamps +0x30, releases handles at +0x08 and +0x3c through their scalar-deleting destructors, and updates control-context latch field +0x48 from the deactivate argument. Static retail evidence only; exact CPauseMenu layout, UI runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMHead__ResetAnimationStateAndPauseLatch"},
                tags("cpausemenu", "pause-flow", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("deactivate_control", intType)
                }
            ),
            new Spec(
                "0x004f4530",
                "SharedUnitAnimation__FindAnimationIndexOrZero",
                "__thiscall",
                intType,
                "Wave390 shared-helper correction from the older CGillMHead-specific label: callers include CGillMHeadAI animation-state helpers and BattleEngine animation/morph paths. The body checks the animation owner at this+0x30, asks it for the animation database through vfunc +0x24, returns 0 when absent, otherwise calls FindAnimationIndex for the supplied token. Static retail evidence only; exact owning base class, concrete layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMHead__FindAnimationIndexOrZero"},
                tags("shared-animation", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("animation_name", voidPtr)
                }
            ),
            new Spec(
                "0x004f4560",
                "SharedUnitAnimation__PlayAnimationByNameIfPresent",
                "__thiscall",
                voidType,
                "Wave390 shared-helper correction from the older CGillMHead-specific label: callers include CGillMHeadAI animation-state helpers and BattleEngine animation/morph paths. The body resolves an animation token through the owner at this+0x30 when present, falls back to index 0 when absent, then dispatches vfunc +0xf0 with the resolved animation index and two playback flags. Static retail evidence only; exact owning base class, concrete layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {"CGillMHead__PlayAnimationByNameIfPresent"},
                tags("shared-animation", "owner-corrected", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("animation_name", voidPtr),
                    param("play_flag", intType),
                    param("reset_flag", intType)
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
