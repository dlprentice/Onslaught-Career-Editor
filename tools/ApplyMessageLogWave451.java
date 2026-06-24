//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
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

public class ApplyMessageLogWave451 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedCurrentName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(String address, String expectedCurrentName, String name, String callingConvention,
                DataType returnType, String comment, String[] tags, ParameterImpl[] parameters) {
            this.address = address;
            this.expectedCurrentName = expectedCurrentName;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
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

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            Function containing = getFunctionContaining(entry);
            if (containing != null && containing.getEntryPoint().equals(entry)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
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
            "messagelog-wave451",
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

            String currentName = fn.getName();
            if (!currentName.equals(spec.expectedCurrentName) && !currentName.equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }
            boolean renameNeeded = !currentName.equals(spec.name);

            if (dryRun) {
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                stats.skipped++;
                return;
            }

            if (renameNeeded) {
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

            println("OK: " + spec.address + " " + readBack.getSignature());
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
        DataType byteType = ByteDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004b8850",
                "CDXEngine__RenderMessageBoxOverlay",
                "CMessageBox__RenderOverlay",
                "__thiscall",
                voidType,
                "Wave451 name/signature/comment correction: renders and animates the active CMessageBox overlay from the object in ECX. The CHud callsite passes DAT_008a9d84 in ECX and a caller-pushed value 7; ret 0x4 confirms one stack argument. The body fades field +0x2c4, renders the segmented message box bar, word-wraps the active CMessage through CMessage__WordWrapToLineBuffer, draws visible lines, and stops voice playback when the cutscene gate is active. Static retail evidence only; exact overlay layout, runtime message display, and rebuild parity remain unproven.",
                tags("messagebox", "overlay", "render", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("viewport_height", intType)
                }
            ),
            new Spec(
                "0x004b8dd0",
                "CGameMenu__ctor_like_004b8dd0",
                "CMessageLog__ctor_base",
                "__fastcall",
                voidPtr,
                "Wave451 name/signature/comment correction: constructor/base initializer for CMessageLog. Initializes the inherited pointer-set queue at +0x18, clears queue/render counters and texture slots, clears the shared arrow texture global, installs the CMessageLog vtable, and returns this. Static retail evidence only; exact CMessageLog layout, runtime menu behavior, and rebuild parity remain unproven.",
                tags("messagelog", "constructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b8e50",
                "CMessageLog__VFunc_01_004b8e50",
                "CMessageLog__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave451 name/signature/comment correction: scalar-deleting destructor wrapper for CMessageLog. Calls CMessageLog__dtor_base, frees this through CDXMemoryManager when flags bit 0 is set, returns this, and ret 0x4 confirms one stack flags argument. Static retail evidence only; exact CMessageLog layout, runtime menu behavior, and rebuild parity remain unproven.",
                tags("messagelog", "destructor", "scalar-deleting-dtor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004b8e70",
                "CMessageLog__LoadTextures",
                "CMessageLog__LoadTextures",
                "__fastcall",
                voidType,
                "Wave451 signature/comment hardening: loads the CMessageLog end-curve, arrow, blank, head-frame, and head-frame mask textures into slots +0x08..+0x14 and shared arrow texture global DAT_00807418. Static retail evidence only; exact texture ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("messagelog", "textures", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b8ef0",
                "CMessageLog__EnqueueMessageNode",
                "CMessageLog__EnqueueMessageNode",
                "__thiscall",
                voidType,
                "Wave451 signature/comment hardening: adds message_node to the head of the CMessageLog pointer-set queue at this+0x18. Ret 0x4 confirms one stack message-node argument and removes the stale phantom second argument. Static retail evidence only; exact node ownership, runtime log ordering, and rebuild parity remain unproven.",
                tags("messagelog", "queue", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("message_node", voidPtr)
                }
            ),
            new Spec(
                "0x004b8f00",
                "CMessageLog__ctor_like_004b8f00",
                "CMessageLog__dtor_base",
                "__fastcall",
                voidType,
                "Wave451 name/signature/comment correction: base destructor for CMessageLog. Walks queued message nodes through their vtable release slot, clears the pointer-set queue, resets render counters, releases loaded message-log textures and the shared arrow texture global, then calls CMonitor__Shutdown. Static retail evidence only; exact node ownership, texture lifetime, runtime menu behavior, and rebuild parity remain unproven.",
                tags("messagelog", "destructor", "textures", "queue", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b9010",
                "CMessageLog__RenderPanelFrame",
                "CMessageLog__RenderPanelFrame",
                "__thiscall",
                voidType,
                "Wave451 signature/comment hardening: renders the CMessageLog framed panel using the end-curve and blank textures at +0x08/+0x0c. Ret 0x14 confirms five stack arguments after this: screen_x, screen_y, width, height, and alpha. The body clamps width/height to 0x40, draws four corners, edge stretches, and center fill, then restores render state. Static retail evidence only; exact screen-space semantics, runtime UI behavior, and rebuild parity remain unproven.",
                tags("messagelog", "render", "panel-frame", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("screen_x", intType),
                    param("screen_y", intType),
                    param("width", intType),
                    param("height", intType),
                    param("alpha", floatType)
                }
            ),
            new Spec(
                "0x004b93f0",
                "CMessageLog__Render",
                "CMessageLog__Render",
                "__thiscall",
                voidType,
                "Wave451 signature/comment hardening: renders the active CMessageLog overlay when enabled, including the title, empty-log panel, queued message cards, scroll arrows, click regions, close/back affordance, and mouse cursor. Ret 0x4 confirms one caller-pushed render-context argument from CDXEngine__PostRender. Static retail evidence only; exact UI state layout, runtime input behavior, and rebuild parity remain unproven.",
                tags("messagelog", "render", "input", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("render_context", intType)
                }
            ),
            new Spec(
                "0x004b9a80",
                "CMessageLog__RenderMessageCard",
                "CMessageLog__RenderMessageCard",
                "__thiscall",
                intType,
                "Wave451 signature/comment hardening: word-wraps and measures a queued CMessage node, optionally renders its panel frame, portrait, timestamp, and up to eight wrapped text lines, then returns the card height. Ret 0x14 confirms five stack arguments after this: message_node, screen_x, screen_y, alpha, and measure_only. Static retail evidence only; exact message/card layout, runtime text behavior, and rebuild parity remain unproven.",
                tags("messagelog", "render", "message-card", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("message_node", voidPtr),
                    param("screen_x", floatType),
                    param("screen_y", floatType),
                    param("alpha", floatType),
                    param("measure_only", intType)
                }
            ),
            new Spec(
                "0x004b9ea0",
                "CMessageLog__ResetRenderState",
                "CMessageLog__ResetRenderState",
                "__fastcall",
                voidType,
                "Wave451 signature/comment hardening: enables the CMessageLog overlay and clears scroll/render interpolation fields at +0x2c, +0x30, +0x38, and +0x3c. Static retail evidence only; exact UI state semantics, runtime menu behavior, and rebuild parity remain unproven.",
                tags("messagelog", "state-reset", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b9ec0",
                "CMessageLog__VFunc_03_004b9ec0",
                "CMessageLog__HandleInputCommand",
                "__thiscall",
                voidType,
                "Wave451 name/signature/comment correction: handles CMessageLog scroll/back input commands from the vtable slot. Button 0x2a scrolls up, 0x2b scrolls down when more rows are available, and 0x2e closes the log, initializes the pause session, relinquishes controller ownership, and plays frontend sounds. Ret 0xc confirms controller_index, button_code, and analog_value stack arguments. Static retail evidence only; exact input routing, runtime menu behavior, and rebuild parity remain unproven.",
                tags("messagelog", "input", "scroll", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("controller_index", intType),
                    param("button_code", intType),
                    param("analog_value", floatType)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0 would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave451 apply had missing/bad entries");
        }
    }
}
