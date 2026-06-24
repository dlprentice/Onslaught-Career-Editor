//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyMenuItemPauseMenuRawHeadWave824 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedSignature, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedSignature = expectedSignature;
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
            "menuitem-pausemenu-raw-head-wave824",
            "wave824-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "menuitem",
            "pause-menu"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x004cf050",
                "CMenuItem__Destructor_Thunk",
                "void __thiscall CMenuItem__Destructor_Thunk(void * this)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {},
                "Wave824 static read-back/name correction: single-instruction jump thunk at 0x004cf050 to 0x004a3730 CMenuItem__Destructor. The observed caller is 0x004cf030 CMouseSensitivityMenuItem__scalar_deleting_dtor, which destroys the base menu-item subobject before optional CDXMemoryManager__Free. The target destructor body releases texture/resource handles at +0x1c and +0x20 and unlinks the monitor/owner node at +0x34 via CSPtrSet__Remove. This row is the thunk entry, not the destructor body itself. Static retail Ghidra evidence only; exact MouseSensitivityMenuItem layout, runtime frontend behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "jump-thunk", "menuitem-destructor")
            ),
            new Spec(
                "0x004d04d0",
                "CPauseMenu__ReloadSharedBlankTexture",
                "void __cdecl CPauseMenu__ReloadSharedBlankTexture(void)",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave824 static read-back/signature hardening: reloads the shared pause/menu blank texture cache. If DAT_0082b490 is non-null, the helper releases the cached texture through CTexture__DecrementRefCountFromNameField(DAT_0082b490+8), clears the global, then reloads FrontEnd_v2/FE_Blank.tga through CTexture__FindTexture(name,4,0,1,0,1) and stores the returned handle back to DAT_0082b490. Static retail Ghidra evidence only; exact texture-cache lifetime, runtime pause/menu rendering behavior, BEA patching, and rebuild parity remain deferred.",
                tags("pause-texture-cache", "blank-texture")
            ),
            new Spec(
                "0x004d05c0",
                "CMenuItemRange__IsBindingActive",
                "int __thiscall CMenuItemRange__IsBindingActive(void * this)",
                "__thiscall",
                intType,
                new ParameterImpl[] {},
                "Wave824 static read-back/comment hardening: binding-context predicate used by CMenuItemRange__Render. The body reads the binding/range context pointer at this+0x08 and returns 1 only when that pointer is non-null and the byte at context+0x08 is non-zero; otherwise it returns 0. CMenuItemRange__Render uses this predicate while deciding whether mouse hover/click handling can advance into bound child items. Static retail Ghidra evidence only; exact binding-context layout, runtime input behavior, source-body identity, BEA patching, and rebuild parity remain deferred.",
                tags("binding-context", "predicate")
            ),
            new Spec(
                "0x004d0de0",
                "CPauseMenu__GetBindingCapacityWarningText",
                "short * __cdecl CPauseMenu__GetBindingCapacityWarningText(void)",
                "__cdecl",
                shortPtr,
                new ParameterImpl[] {},
                "Wave824 static read-back/name/signature correction: returns a localized wide-text warning pointer or null for controller-binding capacity. It first calls Controls__FindFirstFreeBindingSlot(0) and returns Localization__GetStringById(0xe8) when no player-one slot is free. For multiplayer-range levels (0 < DAT_008a9ac0 < 9) where CGame__IsMultiplayer(&DAT_008a9a98) is true, it also checks Controls__FindFirstFreeBindingSlot(1) and returns Localization__GetStringById(0xe9) when no player-two slot is free. Otherwise it returns null. CPauseMenu__ButtonPressed uses the non-null result to abort entry into the binding-prompt flow. Static retail Ghidra evidence only; exact localized string identity, controller-binding table layout, runtime pause-menu input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "binding-capacity", "localized-warning")
            )
        };
    }

    private boolean hasTags(Function fn, String[] expected) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.expectedName)) {
            return false;
        }
        if (!fn.getSignature().toString().equals(spec.expectedSignature)) {
            return false;
        }
        if (!fn.getSignature().getReturnType().isEquivalent(spec.returnType)) {
            return false;
        }
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        return true;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }

        if (!fn.getName().equals(spec.expectedName)) {
            if (dryRun) {
                println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.expectedName);
                stats.wouldRename++;
            } else {
                fn.setName(spec.expectedName, SourceType.USER_DEFINED);
                println("RENAMED: " + spec.address + " " + spec.expectedName);
                stats.renamed++;
            }
        }

        boolean signatureOk = sameSignature(fn, spec);
        boolean commentOk = spec.comment.equals(fn.getComment());
        boolean tagsOk = hasTags(fn, spec.tags);
        if (signatureOk && commentOk && tagsOk) {
            println("SKIP: " + spec.address + " " + spec.expectedName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY_UPDATE: " + spec.address + " " + spec.expectedName
                + " signature_ok=" + signatureOk + " comment_ok=" + commentOk + " tags_ok=" + tagsOk);
            if (!signatureOk) {
                stats.signatureUpdated++;
            } else {
                stats.commentOnlyUpdated++;
            }
            stats.skipped++;
            return;
        }

        if (!signatureOk) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        } else {
            stats.commentOnlyUpdated++;
        }
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        boolean readbackOk = true;
        if (!sameSignature(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedSignature + " actual=" + fn.getSignature());
            stats.bad++;
            readbackOk = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            stats.bad++;
            readbackOk = false;
        }
        if (!hasTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            stats.bad++;
            readbackOk = false;
        }
        if (readbackOk) {
            println("READBACK_OK: " + spec.address + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0] : "dry";
        boolean dryRun = isDryRun(mode);
        println("ApplyMenuItemPauseMenuRawHeadWave824 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave824 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
