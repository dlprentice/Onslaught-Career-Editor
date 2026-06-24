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

public class ApplyFEPMainWave401 extends GhidraScript {
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

    private Function functionAtEntry(String addressText) {
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "fepmain-wave401",
            "frontend",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
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
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004621b0",
                "CFEPMain__Init",
                "__fastcall",
                intType,
                "Wave401 comment hardening: CFEPMain init seeds selection/timer state at +0x14/+0x1c/+0x20 and returns 1 from the CFEPMain vtable slice. Static retail evidence only; exact source identity, concrete CFEPMain layout, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "init", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004621d0",
                "CFEPMain__GetMenuType",
                "__cdecl",
                intType,
                "Wave401 signature/comment correction: no-argument menu-type getter returns constant 7. Static retail/vtable evidence only; exact source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "menu-type", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {}
            ),
            new Spec(
                "0x004621e0",
                "CFEPMain__GetActionCount",
                "__stdcall",
                intType,
                "Wave401 signature/comment correction: stack-only menu_state switch returns enabled action counts, including career-in-progress gating for states 1/8, controller-count gating for state 3, memory-card/dialog flag at state 2, and default zero. Static retail evidence only; exact source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "action-count", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("menu_state", intType)
                }
            ),
            new Spec(
                "0x00462250",
                "CFEPMain__ButtonPressed",
                "__thiscall",
                voidType,
                "Wave401 comment hardening: thiscall button handler covers menu up/down/select and language-cycling inputs 0x2a/0x2b/0x2c/0x36/0x37, updates selection fields +0x8/+0xc/+0x14/+0x18/+0x1c/+0x20, calls virtual action/count guards, and plays frontend sounds. Static retail evidence only; exact source identity, concrete layout, runtime input behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "input", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("button", intType),
                    param("val", floatType)
                }
            ),
            new Spec(
                "0x004623e0",
                "CFEPMain__DoAction",
                "__fastcall",
                voidType,
                "Wave401 comment refresh: action handler switches on +0x8 menu selection for New Game/Continue/Load/Options/Multiplayer/Goodies/Credits/Return, calls Career blank/save-list refresh helpers, updates page globals and DAT_0089d94c, and routes FrontEnd pages 7/0x10/8/0x11/0xb. Static retail/debug-path evidence only; FEPMain.cpp is absent from the current Stuart source snapshot, and exact source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "action", "comment-hardened", "source-boundary"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00462640",
                "CFEPMain__Process",
                "__thiscall",
                voidType,
                "Wave401 comment hardening: process loop handles state-gated menu updates, checks career nodes 800/0x2e5, owns the FEPMain.cpp debug-path allocation call before CCareer__Save and CFEPOptions__WriteDefaultOptionsFile, and can route to page 0x0c or refresh new-game setup. Static retail evidence only; runtime save/frontend behavior, concrete layout, exact source identity, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "process", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("state", intType)
                }
            ),
            new Spec(
                "0x00462b70",
                "CFEPMain__RenderPreCommon",
                "__stdcall",
                voidType,
                "Wave401 signature/comment correction: stack-only transition/dest helper clamps transition, handles dest 0x0c, computes front-end video fade values, and draws/prepares the shared main-menu pre-render layer. Static retail evidence only; exact source identity, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "render-precommon", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("transition", floatType),
                    param("dest", intType)
                }
            ),
            new Spec(
                "0x00462c90",
                "CFEPMain__Update",
                "__stdcall",
                voidType,
                "Wave401 signature/comment correction: stack-only menu_state helper maps menu states to FrontEndText token lookups 0,1,2,4,5,6,3, or fallback 8. Static retail evidence only; exact source identity, runtime localization behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "localization", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("menu_state", intType)
                }
            ),
            new Spec(
                "0x00462d40",
                "CFEPMain__Render",
                "__thiscall",
                voidType,
                "Wave401 comment hardening: main render path uses +0x8 selection state plus transition/dest arguments to draw main-menu surfaces/text, language arrows/pulse state, and state-specific menu rows. Static retail evidence only; exact source identity, runtime rendering behavior, concrete layout, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "render", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("transition", floatType),
                    param("dest", intType)
                }
            ),
            new Spec(
                "0x004644d0",
                "CFEPMain__TransitionNotification",
                "__fastcall",
                voidType,
                "Wave401 comment hardening: transition hook resets +0x14 to -1.0, refreshes +0x4 from PLATFORM time, promotes state 0 to 1 when CAREER_mCareerInProgress is set, mirrors selection to +0xc, and stores float selection at +0x10. Static retail evidence only; exact source identity, runtime transition behavior, concrete layout, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "transition", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from", intType)
                }
            ),
            new Spec(
                "0x00464520",
                "CFEPMain__ActiveNotification",
                "__fastcall",
                voidType,
                "Wave401 comment hardening: active-notification hook clears +0x14 and +0x18 from the CFEPMain vtable slice and returns with one ignored page argument. Static retail evidence only; exact source identity, runtime activation behavior, concrete layout, and rebuild parity remain unproven.",
                new String[] {},
                tags("fepmain", "active-notification", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from_page", intType)
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
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (!dryRun && (stats.missing != 0 || stats.bad != 0)) {
            throw new IllegalStateException("Wave401 FEPMain apply had failures");
        }
    }
}
