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

public class ApplyFEPMultiplayerStartRuntimeWave857 extends GhidraScript {
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
            "fepmultiplayerstart-runtime-wave857",
            "wave857-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "frontend",
            "fepmultiplayerstart",
            "multiplayer-start",
            "subobj4034"
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
                "0x0051b600",
                "CFEPMultiplayerStart__SubObj4034__ctor",
                "void __fastcall CFEPMultiplayerStart__SubObj4034__ctor(void * this)",
                "__fastcall",
                voidType,
                new ParameterImpl[] {},
                "Wave857 static read-back: CFEPMultiplayerStart SubObj4034 constructor called from CFEPMultiplayerStart__ctor at 0x00466049 for the embedded helper at owner+0x4034. The body installs vtable 0x005e49b4 and clears the observed field at this+0x10. Static retail Ghidra evidence only; FEPMultiplayerStart.cpp source is absent from the current source snapshot, and exact subobject layout, runtime multiplayer-start behavior, BEA patching, and rebuild parity remain unproven.",
                tags("constructor", "owner-plus-4034", "vtable-005e49b4")
            ),
            new Spec(
                "0x0051b610",
                "CFEPMultiplayerStart__SubObj4034__ResetFlags",
                "void __fastcall CFEPMultiplayerStart__SubObj4034__ResetFlags(void * this)",
                "__fastcall",
                voidType,
                new ParameterImpl[] {},
                "Wave857 static read-back: CFEPMultiplayerStart SubObj4034 reset helper clears this+0x0c and global gate DAT_00677614, sets this+0x10 to 1, then re-clears the gate and this+0x0c when platform/global state DAT_0083d448 is zero. It is called from the newly created SubObj4034 vtable-slot init/process helpers at 0x0051b64e and 0x0051b6cf. Static retail Ghidra evidence only; exact field names, runtime multiplayer-start state behavior, BEA patching, and rebuild parity remain unproven.",
                tags("reset-flags", "runtime-gate", "dat-00677614")
            ),
            new Spec(
                "0x0051b640",
                "CFEPMultiplayerStart__SubObj4034__Init",
                "int __fastcall CFEPMultiplayerStart__SubObj4034__Init(void * this)",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    new ParameterImpl("this", voidPtr, currentProgram)
                },
                "Wave857 static read-back/function-create: CFEPMultiplayerStart SubObj4034 vtable 0x005e49b4 slot 0 function created at 0x0051b640 after dry-run create verified would_create. The body clears this+0x0c, sets this+0x14 to 1, calls CFEPMultiplayerStart__SubObj4034__ResetFlags, and returns 1. Static retail Ghidra evidence only; exact source method identity, concrete SubObj4034 layout, runtime page-init behavior, BEA patching, and rebuild parity remain unproven.",
                tags("function-created", "signature-hardened", "vtable-slot", "subobj4034-init")
            ),
            new Spec(
                "0x0051b660",
                "CFEPMultiplayerStart__SubObj4034__ButtonPressed",
                "void __thiscall CFEPMultiplayerStart__SubObj4034__ButtonPressed(void * this, int button, float val)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("button", intType, currentProgram),
                    new ParameterImpl("val", floatType, currentProgram)
                },
                "Wave857 static read-back/function-create: CFEPMultiplayerStart SubObj4034 vtable 0x005e49b4 slot 3 function created at 0x0051b660 after dry-run create verified would_create. The body handles button 0x2c only when this+0x0c is zero, clears DAT_006630cc, chooses frontend target page/time from DAT_008a9ab4 and DAT_0083d448, calls CFrontEnd__SetPage(&DAT_0089d758, page, time), then plays frontend sound 1. The second stack argument is preserved in the signature for vtable ABI shape but is not read by the body. Static retail Ghidra evidence only; exact button-label mapping, runtime frontend transition behavior, BEA patching, and rebuild parity remain unproven.",
                tags("function-created", "signature-hardened", "vtable-slot", "button-handler", "frontend-page-transition")
            ),
            new Spec(
                "0x0051b6b0",
                "CFEPMultiplayerStart__SubObj4034__Process",
                "void __thiscall CFEPMultiplayerStart__SubObj4034__Process(void * this, int state)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("state", intType, currentProgram)
                },
                "Wave857 static read-back/function-create: CFEPMultiplayerStart SubObj4034 vtable 0x005e49b4 slot 2 function created at 0x0051b6b0 after dry-run create verified would_create. The body returns immediately for nonzero state, checks a movie/HUD gate, calls CFEPMultiplayerStart__SubObj4034__ResetFlags when that gate is active, dispatches the slot-3 button handler with button 0x2c after a dev-mode timeout, updates inactivity/timer fields at this+0x04 and this+0x18, reacts to DAT_00677614/DAT_00677624/DAT_0067762c completion state, and ends by processing mouse/full-window dispatch through CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture. Static retail Ghidra evidence only; exact state-machine semantics, hidden register assumptions, runtime movie/HUD behavior, BEA patching, and rebuild parity remain unproven.",
                tags("function-created", "signature-hardened", "vtable-slot", "page-process", "runtime-state")
            ),
            new Spec(
                "0x0051be70",
                "CFEPMultiplayerStart__SubObj4034__InitRuntimeState",
                "void __fastcall CFEPMultiplayerStart__SubObj4034__InitRuntimeState(void * this)",
                "__fastcall",
                voidType,
                new ParameterImpl[] {},
                "Wave857 static read-back: CFEPMultiplayerStart SubObj4034 runtime-state initializer, DATA-referenced from 0x005e49cc near vtable 0x005e49b4. The body stores PLATFORM__GetSysTimeFloat at this+0x04, writes -1 to DAT_0089d9cc, calls CFEPMultiplayerStart__SetCurrentSelection(&DAT_0089be50, 0) and CFEPMultiplayerStart__SetCurrentSelection(&DAT_0089be5c, 0), and clears this+0x18. Static retail Ghidra evidence only; exact source method identity, concrete SubObj4034 layout, runtime selection behavior, BEA patching, and rebuild parity remain unproven.",
                tags("runtime-state-init", "selection-state", "data-xref")
            ),
            new Spec(
                "0x0051da60",
                "CFEPMultiplayerStart__InitSelection",
                "void __thiscall CFEPMultiplayerStart__InitSelection(void * this, int mode)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("mode", intType, currentProgram)
                },
                "Wave857 static read-back: CFEPMultiplayerStart selection initializer referenced from primary vtable 0x005db8d0 slot data at 0x005db910. The body stores PLATFORM__GetSysTimeFloat plus transition delay 0x005d8ba0 at this+0x04, clears an 0x12-dword selection/animation table starting at this+0x10, and when mode is 0x0f seeds one table entry to 1.0 using index fields at this+0x60 and this+0x64. Static retail Ghidra evidence only; exact FEPMultiplayerStart layout, source method identity, runtime selection UI behavior, BEA patching, and rebuild parity remain unproven.",
                tags("primary-page-helper", "selection-init", "vtable-data")
            ),
            new Spec(
                "0x0051ddd0",
                "CFEPMultiplayerStart__HandleInput",
                "void __thiscall CFEPMultiplayerStart__HandleInput(void * this, int button, int player_index)",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("button", intType, currentProgram),
                    new ParameterImpl("player_index", intType, currentProgram)
                },
                "Wave857 static read-back: CFEPMultiplayerStart per-player selection input helper called twice from CFEPMultiplayerStart__Render at 0x0051ee7b and 0x0051ef9e after mouse hit-tests. For player_index != -1, button 0x2a increments the player's config index at this+0x18+player_index*4 with wraparound from CFEPMultiplayerStart__GetConfigCount, plays sound 0, and pulses this+0x20+player_index*4 to 1.0. Button 0x2b decrements with wraparound, plays sound 0, and pulses this+0x28+player_index*4 to 1.0. Static retail Ghidra evidence only; exact button-label mapping, concrete player-selection layout, runtime frontend behavior, BEA patching, and rebuild parity remain unproven.",
                tags("primary-page-helper", "selection-input", "render-click-handler")
            )
        };
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasTags(Function fn, String[] expected) {
        Set<String> actual = tagNames(fn);
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private String normalizeSignature(String signature) {
        StringBuilder result = new StringBuilder();
        boolean lastWasSpace = false;
        for (int i = 0; i < signature.length(); i++) {
            char ch = signature.charAt(i);
            if (ch == 0x200b || ch == 0x200c || ch == 0x200d || ch == 0xfeff) {
                continue;
            }
            if (ch == 0x00a0 || Character.isWhitespace(ch)) {
                if (!lastWasSpace) {
                    result.append(' ');
                    lastWasSpace = true;
                }
                continue;
            }
            result.append(ch);
            lastWasSpace = false;
        }
        return result.toString().trim();
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.expectedName)) {
            return false;
        }
        if (!normalizeSignature(fn.getSignature().toString()).equals(normalizeSignature(spec.expectedSignature))) {
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
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + spec.expectedName + " already matched");
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
        println("ApplyFEPMultiplayerStartRuntimeWave857 mode=" + (dryRun ? "dry" : "apply"));

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
            throw new IllegalStateException("Wave857 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
