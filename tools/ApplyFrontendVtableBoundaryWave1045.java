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
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyFrontendVtableBoundaryWave1045 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
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
        int created = 0;
        int wouldCreate = 0;
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

    private Function functionAtEntry(Address address) {
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function existing = functionAtEntry(address);
        if (existing != null) {
            return existing;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null) {
            throw new IllegalStateException("Address is inside existing function "
                + containing.getName() + " at " + containing.getEntryPoint());
        }
        if (dryRun) {
            stats.wouldCreate++;
            println("DRY_CREATE: " + spec.address + " -> " + expectedSignature(spec));
            return null;
        }

        if (getInstructionAt(address) == null && (getDataAt(address) != null || currentProgram.getListing().getDefinedDataContaining(address) != null)) {
            currentProgram.getListing().clearCodeUnits(address, address.add(15), false);
        }
        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, spec.name);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + spec.address + " (disassemble=" + disasmOk + ")");
        }
        stats.created++;
        return created;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = getOrCreate(spec, dryRun, stats);
        if (fn == null) {
            return;
        }

        boolean renameNeeded = !fn.getName().equals(spec.name);
        boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
        boolean commentOrTagsNeedUpdate = fn.getComment() == null
            || !fn.getComment().equals(spec.comment)
            || !hasAllTags(fn, spec);

        if (!renameNeeded && !signatureNeedsUpdate && !commentOrTagsNeedUpdate) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else if (commentOrTagsNeedUpdate) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (signatureNeedsUpdate) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        }
        fn.setComment(spec.comment);
        Set<String> existingTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                fn.addTag(tag);
            }
        }
        if (!signatureNeedsUpdate && commentOrTagsNeedUpdate) {
            stats.commentOnlyUpdated++;
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50L);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "frontend-vtable-boundary-wave1045",
            "wave1045-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "signature-hardened",
            "comment-hardened",
            "frontend",
            "vtable-slot"
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
        println("ApplyFrontendVtableBoundaryWave1045 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0045c7a0",
                "CFEPGoodies__Init",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave1045 frontend vtable-boundary recovery: CFEPGoodies vtable 0x005db998 slot 0 points at this previously missing function object. Retail bytes at 0x0045c7a0 initialize Goodies page fields including selected-grid offsets this+0x13c/+0x140, animation/pan fields through this+0x1d8, copy a default table from 0x00679870 into this+0x1a0, and call platform/frontend helpers before returning. Static retail Ghidra/vtable/source-shape evidence only; exact CFEPGoodies layout, runtime Goodies wall behavior, asset playback, BEA patching, and rebuild parity remain unproven.",
                tags("goodies", "slot-0", "init")
            ),
            new Spec(
                "0x0045c9e0",
                "CFEPGoodies__Shutdown",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave1045 frontend vtable-boundary recovery: CFEPGoodies vtable 0x005db998 slot 1 points at this compact shutdown thunk, which jumps to CFEPGoodies__FreeUpGoodyResources at 0x0045cd10. Static retail Ghidra/vtable/source-shape evidence only; exact CFEPGoodies layout, runtime resource lifetime, BEA patching, and rebuild parity remain unproven.",
                tags("goodies", "slot-1", "shutdown", "thunk")
            ),
            new Spec(
                "0x0045e0d0",
                "CFEPGoodies__Render",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("transition", floatType),
                    param("dest", intType)
                },
                "Wave1045 frontend vtable-boundary recovery: CFEPGoodies vtable 0x005db998 slot 5 points at this previously missing render function object. The body has a large stack frame, uses Goodies page fields and frontend draw helpers, reaches the overlay-effect call at 0x0045ff36, and returns with RET 0x8 before CFEPLevelSelect__ctor. Source CFEPGoodies.cpp defines Render(float transition, EFrontEndPage dest) after RenderPreCommon and before TransitionNotification. Static retail Ghidra/vtable/source-shape evidence only; exact CFEPGoodies layout, runtime Goodies wall/model/video behavior, visual parity, BEA patching, and rebuild parity remain unproven.",
                tags("goodies", "slot-5", "render")
            ),
            new Spec(
                "0x0045ffa0",
                "CFEPGoodies__TransitionNotification",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("from_page", intType)
                },
                "Wave1045 frontend vtable-boundary recovery: CFEPGoodies vtable 0x005db998 slot 6 points at this previously missing transition-notification function object. Retail bytes call PLATFORM__GetSysTimeFloat through 0x0088a0a8, reset Goodies selection/animation fields from the 0x00679870 default table, and return after the recovered render body. Source CFEPGoodies.cpp defines TransitionNotification(EFrontEndPage from) with start-time/reset behavior. Static retail Ghidra/vtable/source-shape evidence only; exact CFEPGoodies layout, runtime transition behavior, BEA patching, and rebuild parity remain unproven.",
                tags("goodies", "slot-6", "transition-notification")
            ),
            new Spec(
                "0x005216c0",
                "CFEPWingmen__Init",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave1045 frontend vtable-boundary recovery: CFEPWingmen vtable 0x005dba10 slot 0 points at this previously missing init function object. The body uses an SEH frame, clears Wingmen state fields this+0x14..+0x20, allocates/initializes frontend thing resources and list state, and returns before the saved CFEPWingmen__Destroy slot. FEPWingmen.cpp source is absent from references/Onslaught, so this is retail Ghidra/vtable evidence only; exact Wingmen layout, runtime menu behavior, BEA patching, and rebuild parity remain unproven.",
                tags("wingmen", "slot-0", "init")
            ),
            new Spec(
                "0x00521d20",
                "CFEPWingmen__ButtonPressed",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("button", intType),
                    param("val", floatType)
                },
                "Wave1045 frontend vtable-boundary recovery: CFEPWingmen vtable 0x005dba10 slot 3 points at this previously missing button handler. CFEPWingmen__Update calls vtable +0x0c in dev-mode/state-zero flow; the body dispatches frontend button ids, calls shared frontend navigation helpers, updates DAT_008a956c/current-level state, and has RET 0x8 exits. FEPWingmen.cpp source is absent from references/Onslaught, so this is retail Ghidra/vtable evidence only; exact button semantics, runtime Wingmen menu behavior, BEA patching, and rebuild parity remain unproven.",
                tags("wingmen", "slot-3", "button")
            ),
            new Spec(
                "0x00522160",
                "CFEPWingmen__RenderPreCommon",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("transition", floatType),
                    param("dest", intType)
                },
                "Wave1045 frontend vtable-boundary recovery: CFEPWingmen vtable 0x005dba10 slot 4 points at this previously missing render-pre-common function object. The compact body reads transition from the stack, conditionally draws a small frontend overlay through CFrontEnd__RenderPreCommonFade-style helper 0x004530b0, and returns with RET 0x8 without using ECX. FEPWingmen.cpp source is absent from references/Onslaught, so this is retail Ghidra/vtable evidence only; exact page-transition semantics, runtime visual behavior, BEA patching, and rebuild parity remain unproven.",
                tags("wingmen", "slot-4", "render-pre-common")
            ),
            new Spec(
                "0x00522190",
                "CFEPWingmen__Render",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("transition", floatType),
                    param("dest", intType)
                },
                "Wave1045 frontend vtable-boundary recovery: CFEPWingmen vtable 0x005dba10 slot 5 points at this previously missing render function object. The body has a 0x148-byte stack frame, calls CFrontEnd__GetShadowOffsetX/Y, RenderState_Set, CDXEngine__ApplyPendingRenderState, CDXSurf__RenderSurface, CFEPWingmen__FindCurrentLevelRecord, text rendering helpers, and the shared CFrontEnd__RenderOverlayEffects at 0x005230ac before RET 0x8. FEPWingmen.cpp source is absent from references/Onslaught, so this is retail Ghidra/vtable evidence only; exact Wingmen layout/text semantics, runtime visual behavior, BEA patching, and rebuild parity remain unproven.",
                tags("wingmen", "slot-5", "render")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun, stats);
            } catch (Exception ex) {
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
                stats.bad++;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1045 frontend vtable boundary apply encountered missing/bad rows");
        }
    }
}
