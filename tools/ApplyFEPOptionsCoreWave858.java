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

public class ApplyFEPOptionsCoreWave858 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedSignature, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
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
            "fepoptions-core-wave858",
            "wave858-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "frontend",
            "fepoptions",
            "options-page"
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
                "0x0051f370",
                "CFEPOptions__GetState",
                "int CFEPOptions__GetState(void * this)",
                null,
                null,
                null,
                "Wave858 static read-back: CFEPOptions state getter called by CFrontEnd__Process at 0x00466c8d and CGame__LoadLevel at 0x0046cf49. The body returns the signed byte at this+0x05. Static retail Ghidra evidence only; exact CFEPOptions layout, runtime frontend/options behavior, BEA patching, and rebuild parity remain unproven.",
                tags("state-getter", "this-plus-05")
            ),
            new Spec(
                "0x0051f4b0",
                "CFEPOptions__Init",
                "int CFEPOptions__Init(void * this)",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    new ParameterImpl("this", voidPtr, currentProgram)
                },
                "Wave858 static read-back/function-create: CFEPOptions vtable 0x005db8a8 slot 0 function created at 0x0051f4b0 after dry-run create verified would_create. The body clears the page state field at this+0x04 and returns 1. Static retail Ghidra evidence only; exact CFEPOptions layout, runtime options-page init behavior, BEA patching, and rebuild parity remain unproven.",
                tags("function-created", "signature-hardened", "vtable-slot", "options-init")
            ),
            new Spec(
                "0x0051f4c0",
                "CFEPOptions__Shutdown",
                "void CFEPOptions__Shutdown(void * this)",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("this", voidPtr, currentProgram)
                },
                "Wave858 static read-back/function-create: CFEPOptions vtable 0x005db8a8 slot 1 function created at 0x0051f4c0 after dry-run create verified would_create. The body frees non-null g_pOptionsContext through its vtable slot +4 with flag 1, then clears global pointer 0x0089bc30. The ECX page pointer is preserved in the signature for vtable ABI shape but is not read by the body. Static retail Ghidra evidence only; exact options-context class/layout, runtime shutdown behavior, BEA patching, and rebuild parity remain unproven.",
                tags("function-created", "signature-hardened", "vtable-slot", "context-shutdown", "g-poptionscontext")
            ),
            new Spec(
                "0x0051f4e0",
                "CFEPOptions__ButtonPressed",
                "void CFEPOptions__ButtonPressed(void * this, int button, float val)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("button", intType, currentProgram),
                    new ParameterImpl("val", floatType, currentProgram)
                },
                "Wave858 static read-back/function-create: CFEPOptions vtable 0x005db8a8 slot 3 function created at 0x0051f4e0 after dry-run create verified would_create. The body delegates button/analog arguments to g_pOptionsContext vtable slot +0x0c with a leading zero argument and returns with RET 0x8. The ECX page pointer is preserved in the signature for vtable ABI shape but is not read by the body. Static retail Ghidra evidence only; exact options-context vtable contract, runtime options input behavior, BEA patching, and rebuild parity remain unproven.",
                tags("function-created", "signature-hardened", "vtable-slot", "button-handler", "context-delegate")
            ),
            new Spec(
                "0x0051f500",
                "CFEPOptions__SaveDefaultOptions",
                "void CFEPOptions__SaveDefaultOptions(int return_flag)",
                null,
                null,
                null,
                "Wave858 static read-back: CFEPOptions default-options save helper called by CFEPOptions__ProcessInput at 0x0051f65d and CFEPGoodies__ButtonPressed at 0x0045d0f4. The body chooses a frontend return page from DAT_008a1388/DAT_008a9584/DAT_0083d448, serializes CAREER through CCareer__GetSaveSize and CCareer__Save into a CDXMemoryManager buffer allocated with FEPOptions.cpp debug string 0x0063fc88 line 0xfa, writes defaultoptions.bea at 0x0063fc74 through fopen/fwrite/fclose, prints Couldn't write defaultoptions at 0x0063fc54 on failure, and frees the buffer. Static retail Ghidra evidence only; runtime filesystem behavior, exact frontend state semantics, BEA patching, and rebuild parity remain unproven.",
                tags("defaultoptions", "save-options", "career-serialize", "file-io")
            ),
            new Spec(
                "0x0051f600",
                "CFEPOptions__ProcessInput",
                "void CFEPOptions__ProcessInput(void * this, int state)",
                null,
                null,
                null,
                "Wave858 static read-back: CFEPOptions process/state-machine vtable slot 2 at 0x005db8b0. The body advances page state values 0/2/3/5, special-cases state 4 when only one controller is present, and when state is zero plus g_pOptionsContext+0x10 is zero either routes to page 0x12 for context mode 1 or calls CFEPOptions__SaveDefaultOptions(1). Static retail Ghidra evidence only; exact page-state semantics, options-context layout, runtime frontend behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "process-state", "options-context")
            ),
            new Spec(
                "0x0051f6d0",
                "CFEPOptions__RenderPreCommon",
                "void CFEPOptions__RenderPreCommon(float transition, int dest)",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("transition", floatType, currentProgram),
                    new ParameterImpl("dest", intType, currentProgram)
                },
                "Wave858 static read-back/function-create: CFEPOptions vtable 0x005db8a8 slot 4 function created at 0x0051f6d0 after dry-run create verified would_create. The body forces transition to 1.0 for destination/page ids 0x12 and 0x13, then calls CFrontEnd__RenderPreCommonFade(&DAT_0089d758, transition, 0x3fffffff, dest) and returns with RET 0x8. Static retail Ghidra evidence only; exact transition/destination semantics, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("function-created", "signature-hardened", "vtable-slot", "render-precommon", "fade")
            ),
            new Spec(
                "0x0051f700",
                "CFEPOptions__Update",
                "void CFEPOptions__Update(void * this, float transition, int dest)",
                null,
                null,
                null,
                "Wave858 static read-back: CFEPOptions render/update vtable slot 5 at 0x005db8bc. The body draws sliding text borders, renders g_pOptionsContext through CPauseMenu__Render, falls back to localized title id 0x265233 when no title text is returned, draws the title bar, debug-traces non-null title text, renders context help prompt id 1, clamps transition-derived overlay alpha, and calls CFrontEnd__RenderOverlayEffects. Static retail Ghidra evidence only; exact render argument naming, options-context layout, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vtable-slot", "render-update", "pause-menu-render", "overlay")
            ),
            new Spec(
                "0x0051f8e0",
                "CFEPOptions__Cleanup",
                "void CFEPOptions__Cleanup(void)",
                null,
                null,
                null,
                "Wave858 static read-back: CFEPOptions cleanup helper called from CFrontEnd__SetLanguage at 0x00466ab3. The body mirrors shutdown/context cleanup by freeing non-null g_pOptionsContext through its vtable slot +4 with flag 1 and clearing global pointer 0x0089bc30. Static retail Ghidra evidence only; exact context class/layout, runtime language-change cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cleanup", "context-shutdown", "g-poptionscontext")
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
        boolean signatureOk = fn.getSignature().getPrototypeString().equals(spec.expectedSignature);
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
            println("BADSIG: " + spec.address + " expected=" + spec.expectedSignature + " actual=" + fn.getSignature().getPrototypeString());
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
                && actualSignature.equals(spec.expectedSignature)
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
