//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyFEPScreenPosCoreWave859 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedPrototype;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedPrototype, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedPrototype = expectedPrototype;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "fepscreenpos-core-wave859",
            "wave859-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "frontend",
            "fepscreenpos",
            "screen-position"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0051f9f0",
                "CFEPScreenPos__Init",
                "int CFEPScreenPos__Init(void * this)",
                null,
                null,
                null,
                "Wave859 static read-back: CFEPScreenPos vtable 0x005db858 slot 0 init helper. The body clears calibration/page fields at this+0x04 and this+0x08 and returns 1. Static retail Ghidra evidence only; exact CFEPScreenPos layout, runtime screen-position calibration behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "init", "calibration-state")
            ),
            new Spec(
                "0x0051fa00",
                "CFEPScreenPos__ButtonPressed",
                "void CFEPScreenPos__ButtonPressed(void * this, int button, float val)",
                null,
                null,
                null,
                "Wave859 static read-back: CFEPScreenPos vtable 0x005db858 slot 3 button handler. Buttons 0x2a/0x2b adjust this+0x08 within -0x32..0x40 and persist through CCareer__SetKillCounterTopByte_23F8; buttons 0x36/0x37 adjust this+0x04 by four within -0x3f..0x40 and persist through CCareer__SetKillCounterTopByte_23F4; button 0x2c accepts back to page 0x11 with sound 1; button 0x2e plays sound 2, restores top-byte metadata from the backup pair at this+0x10 through CFEPOptions__SetKillCounterTopBytes_23F4_23F8, then returns to page 0x11. Static retail Ghidra evidence only; exact screen-axis semantics, runtime UI behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "button-handler", "career-top-byte", "calibration-input")
            ),
            new Spec(
                "0x0051fb60",
                "CFEPScreenPos__RenderPreCommon",
                "void CFEPScreenPos__RenderPreCommon(float transition, int dest)",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("transition", floatType, currentProgram),
                    new ParameterImpl("dest", intType, currentProgram)
                },
                "Wave859 static read-back/signature correction: CFEPScreenPos vtable 0x005db858 slot 4 pre-common render helper. Raw instructions read only stack arguments [ESP+4] transition and [ESP+8] dest, return with RET 0x8, and call CFrontEnd__RenderPreCommonFade(transition, 0x3fffffff, dest) only when transition compares equal to 1.0. The stale extra first parameter was removed. Static retail Ghidra evidence only; exact transition/destination semantics, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "render-precommon", "signature-hardened", "fade")
            ),
            new Spec(
                "0x0051fb90",
                "CFEPScreenPos__Render",
                "void CFEPScreenPos__Render(float transition, int dest)",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("transition", floatType, currentProgram),
                    new ParameterImpl("dest", intType, currentProgram)
                },
                "Wave859 static read-back/signature correction: CFEPScreenPos vtable 0x005db858 slot 5 render helper. Raw instructions use the two stack arguments as transition/destination, draw sliding text borders through CFrontEnd__DrawSlidingTextBordersAndMask when transition is 1.0, render the strings at 0x0063fcf0 and 0x0063fcc8, render context help prompts 5 and 6, draw the title string at 0x0063fcb0, and render overlay effects when transition is 1.0. The stale extra first parameter was removed. Static retail Ghidra evidence only; exact runtime screen-position visuals/input behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "render", "signature-hardened", "screen-position-text")
            ),
            new Spec(
                "0x0051fd50",
                "CFEPScreenPos__TransitionNotification",
                "void CFEPScreenPos__TransitionNotification(void * this, int from_page)",
                null,
                null,
                null,
                "Wave859 static read-back: CFEPScreenPos vtable 0x005db858 slot 6 transition-notification helper. The body records PLATFORM__GetSysTimeFloat()+delay at this+0x0c, snapshots CCareer top-byte metadata through CFEPOptions__GetKillCounterTopBytes_23F4_23F8 into this+0x10/0x14, then copies the snapshot into active calibration fields this+0x04/0x08. Static retail Ghidra evidence only; exact CFEPScreenPos layout, runtime transition behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "transition-notification", "career-top-byte", "timer")
            )
        };
    }

    private Set<String> currentTags(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, String[] expected) {
        Set<String> actual = currentTags(fn);
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean applyTags(Function fn, String[] expected, boolean dryRun) {
        boolean changed = false;
        Set<String> actual = currentTags(fn);
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                changed = true;
                if (!dryRun) {
                    fn.addTag(tag);
                }
            }
        }
        return changed;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            stats.bad++;
            return;
        }

        boolean nameOk = fn.getName().equals(spec.expectedName);
        boolean signatureOk = fn.getSignature().getPrototypeString().equals(spec.expectedPrototype);
        boolean commentOk = spec.comment.equals(fn.getComment());
        boolean tagsOk = hasAllTags(fn, spec.tags);
        boolean canUpdateSignature = spec.callingConvention != null;

        if (!nameOk && !dryRun) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
        }
        if (!nameOk) {
            stats.wouldRename++;
            if (!dryRun) {
                stats.renamed++;
            }
        }

        if (!signatureOk && canUpdateSignature) {
            if (!dryRun) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            stats.signatureUpdated++;
        } else if (!signatureOk) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedPrototype + " actual=" + fn.getSignature().getPrototypeString());
            stats.bad++;
        }

        if (!commentOk && !dryRun) {
            fn.setComment(spec.comment);
        }
        if (!tagsOk) {
            applyTags(fn, spec.tags, dryRun);
        }

        if (commentOk && tagsOk && signatureOk && nameOk) {
            stats.skipped++;
            println("SKIP_OK: " + spec.address + " " + spec.expectedName);
        } else {
            stats.updated++;
            if (signatureOk || !canUpdateSignature) {
                stats.commentOnlyUpdated++;
            }
            println((dryRun ? "DRY_UPDATE: " : "APPLY_UPDATE: ") + spec.address + " " + spec.expectedName);
        }

        if (!dryRun) {
            Function readback = functionAtEntry(spec.address);
            String actualSignature = readback.getSignature().getPrototypeString();
            boolean readbackOk = readback.getName().equals(spec.expectedName)
                && actualSignature.equals(spec.expectedPrototype)
                && spec.comment.equals(readback.getComment())
                && hasAllTags(readback, spec.tags);
            if (readbackOk) {
                println("READBACK_OK: " + spec.address + " " + actualSignature);
            } else {
                println("READBACK_BAD: " + spec.address + " name=" + readback.getName() + " signature=" + actualSignature);
                stats.bad++;
            }
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
