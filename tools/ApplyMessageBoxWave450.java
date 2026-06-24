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

public class ApplyMessageBoxWave450 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedCurrentName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String expectedCurrentName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
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
            "messagebox-wave450",
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
                "0x004b6f10",
                "CMessage__VFunc_01_004b6f10",
                "CMessage__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave450 name/signature/comment correction: scalar-deleting destructor wrapper for the CMessage-style queued message object. Calls CMessage__dtor_base, frees this through CDXMemoryManager when flags bit 0 is set, returns this, and ret 0x4 confirms one stack flags argument. Static retail evidence only; exact source class identity, concrete message layout, runtime dialog behavior, and rebuild parity remain unproven.",
                tags("message", "destructor", "scalar-deleting-dtor", "signature-corrected", "name-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004b6f70",
                "CMessage__WordWrapToLineBuffer",
                "CMessage__WordWrapToLineBuffer",
                "__thiscall",
                voidType,
                "Wave450 signature/comment hardening: word-wraps the message wide-text body into an eight-line 0x56-wide wide-char line buffer, using max_chars_per_line and max_visible_lines to wrap/scroll lines and using ellipsis dots after the source text end. Ret 0xc confirms three stack arguments after this and removes the stale phantom fourth argument. Static retail evidence only; exact CMessage layout, localization semantics, runtime text reveal behavior, and rebuild parity remain unproven.",
                tags("message", "word-wrap", "wide-text", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("line_buffer", voidPtr),
                    param("max_chars_per_line", intType),
                    param("max_visible_lines", intType)
                }
            ),
            new Spec(
                "0x004b7160",
                "CMessage__ctor_like_004b7160",
                "CMessage__dtor_base",
                "__fastcall",
                voidType,
                "Wave450 name/signature/comment correction: base destructor for the CMessage-style queued message object. Resets the vtable to the shared CMessage table, clears field +0x28, removes the active reader cell at +0x30 from its pointer set when present, and delegates to CMonitor__Shutdown. Static retail evidence only; exact source class identity, concrete message layout, runtime dialog behavior, and rebuild parity remain unproven.",
                tags("message", "destructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b71e0",
                "CMonitor__ctor_like_004b71e0",
                "CMessageBox__ctor_base",
                "__fastcall",
                voidPtr,
                "Wave450 name/signature/comment correction: constructor/base initializer for the CMessageBox queue/reveal object. Initializes the CSPtrSet queue, random seed, active-message fields, portrait/reveal state, voice path byte, queue-advance flag, default portrait slot, text-speed scale from font extent, portrait texture slots, and active reader globals, then returns this. Static retail evidence only; exact CMessageBox layout, runtime dialog behavior, and rebuild parity remain unproven.",
                tags("messagebox", "constructor", "portrait", "queue", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b7300",
                "CMessageBox__scalar_deleting_dtor",
                "CMessageBox__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave450 signature/comment hardening: scalar-deleting destructor wrapper for CMessageBox. Calls CMessageBox__dtor_base, frees this through CDXMemoryManager when flags bit 0 is set, returns this, and ret 0x4 confirms one stack flags argument. Static retail evidence only; exact CMessageBox layout, runtime dialog behavior, and rebuild parity remain unproven.",
                tags("messagebox", "destructor", "scalar-deleting-dtor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004b7320",
                "CGame__LoadMessageBoxPortraitTextures",
                "CMessageBox__LoadPortraitTextures",
                "__fastcall",
                voidType,
                "Wave450 name/signature/comment correction: loads the MessageBox portrait texture table into this CMessageBox object. Resolves Carver, Tat, Kramer, Tara, Simmons, Lorenzo, Billy, commander, officer, radio officer, technic, pilot, noise, and box textures, writes texture pointers through +0x34..+0x1a4, and seeds matching text-id/token fields at +0x16c..+0x19c. Static retail evidence only; exact portrait table semantics, runtime texture behavior, and rebuild parity remain unproven.",
                tags("messagebox", "portrait", "textures", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b7930",
                "CMessageBox__ctor_like_004b7930",
                "CMessageBox__dtor_base",
                "__fastcall",
                voidType,
                "Wave450 name/signature/comment correction: base destructor for CMessageBox. Releases portrait texture counters across the 13x6 portrait table, releases noise/box textures, stops and releases active voice state, drains queued CMessage entries through their vtable slot, clears the queue, resets active/reveal fields, clears the active reader global, and delegates to CMonitor__Shutdown. Static retail evidence only; exact ownership semantics, runtime voice/dialog behavior, and rebuild parity remain unproven.",
                tags("messagebox", "destructor", "portrait", "voice", "queue", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b7ab0",
                "CDropship__SelectPortraitIndex",
                "CMessageBox__SelectPortraitIndex",
                "__thiscall",
                intType,
                "Wave450 name/signature/comment correction: selects the CMessageBox portrait slot for a queued message by comparing message_text_wide against text ids stored at this+0x16c and by using the commander fallback substring check. Logs an error and falls back to slot 2 when no portrait text matches. Ret 0x4 confirms one stack text argument and removes the stale phantom second argument. Static retail evidence only; exact text-id semantics, runtime portrait selection, and rebuild parity remain unproven.",
                tags("messagebox", "portrait", "text", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("message_text_wide", voidPtr)
                }
            ),
            new Spec(
                "0x004b7b60",
                "CDropship__RequestQueueAdvance",
                "CMessageBox__RequestQueueAdvance",
                "__fastcall",
                voidType,
                "Wave450 name/signature/comment correction: sets the CMessageBox queue-advance flag at +0x2c0 and tail-jumps into CMessageBox__TryAdvanceQueuedMessage. Static retail evidence only; exact queue-state layout, runtime dialog behavior, and rebuild parity remain unproven.",
                tags("messagebox", "queue", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b7b70",
                "CUnitAI__ResetField2C0",
                "CMessageBox__ClearQueueAdvanceFlag",
                "__fastcall",
                voidType,
                "Wave450 name/signature/comment correction: clears the CMessageBox queue-advance flag at +0x2c0 and returns. Static retail evidence only; exact queue-state layout, runtime dialog behavior, and rebuild parity remain unproven.",
                tags("messagebox", "queue", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b7b80",
                "CDropship__TryAdvanceQueuedPortrait",
                "CMessageBox__TryAdvanceQueuedMessage",
                "__fastcall",
                voidType,
                "Wave450 name/signature/comment correction: advances the CMessageBox queued-message list when the box is idle, visible-ready, and queue-advance is armed. Drops invalid queue entries, promotes the next valid message to +0x08, initializes reveal/portrait state, selects the portrait slot, writes the active texture pointer, schedules event 0xbbc after 0.2 seconds, and stamps message timing. Static retail evidence only; exact CMessageBox/CMessage layouts, runtime dialog behavior, and rebuild parity remain unproven.",
                tags("messagebox", "queue", "portrait", "event-scheduling", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b7ca0",
                "IScript__InsertSortedAndTryAdvancePortrait",
                "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance",
                "__thiscall",
                voidType,
                "Wave450 name/signature/comment correction: inserts queued_message into the CMessageBox CSPtrSet queue sorted by queued_message+0x2c priority/order, rebuilds the queue through a temporary CSPtrSet, and triggers CMessageBox__TryAdvanceQueuedMessage when this was the first queued message and the box is ready. Ret 0x4 confirms one stack queued-message argument and removes the stale phantom second argument. Static retail evidence only; exact script/audio caller semantics, queue ownership, runtime dialog behavior, and rebuild parity remain unproven.",
                tags("messagebox", "queue", "script-audio", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("queued_message", voidPtr)
                }
            ),
            new Spec(
                "0x004b7ea0",
                "CMessageBox__StartVoiceOrFallbackTextReveal",
                "CMessageBox__StartVoiceOrFallbackTextReveal",
                "__fastcall",
                voidType,
                "Wave450 signature/comment hardening: starts active CMessageBox voice playback setup when an audio name exists, or falls back to text reveal when gated/no sample is available. Builds language/messagebox paths, updates active reader globals, waits for Bink open state, starts async voice loading when enabled, and otherwise delegates to CMessageBox__AdvanceRevealAndScheduleNextTick. Static retail evidence only; exact audio path semantics, runtime voice playback, and rebuild parity remain unproven.",
                tags("messagebox", "voice", "text-reveal", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b8020",
                "CMessageBox__AdvanceRevealAndScheduleNextTick",
                "CMessageBox__AdvanceRevealAndScheduleNextTick",
                "__fastcall",
                voidType,
                "Wave450 signature/comment hardening: advances active message reveal state, handles no-sample/gated fallback, increments visible wide-character reveal count, schedules event 3000 while reveal continues, schedules event 0xbba when reveal/hold completes, and calls CMessageBox__StopVoicePlaybackIfNotInCutscene when needed. Static retail evidence only; exact timing semantics, runtime voice/text behavior, and rebuild parity remain unproven.",
                tags("messagebox", "text-reveal", "voice", "event-scheduling", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004b82a0",
                "CMessageLog__GetEntryField3CByIndex",
                "CMessageLog__GetEntryField3CByIndex",
                "__thiscall",
                intType,
                "Wave450 signature/comment hardening: returns the message-log entry field at this + entry_index*0x18 + 0x3c. Ret 0x4 confirms one stack entry-index argument and removes the stale phantom second argument. Static retail evidence only; exact CMessageLog entry layout, runtime UI behavior, and rebuild parity remain unproven.",
                tags("messagelog", "accessor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("entry_index", intType)
                }
            ),
            new Spec(
                "0x004b82b0",
                "CDXEngine__RenderBattleLinePulseSprites",
                "CDXEngine__RenderBattleLinePulseSprites",
                "__thiscall",
                voidType,
                "Wave450 signature/comment hardening: renders the active MessageBox battle-line pulse/noise sprites using CMessageBox state, random seed at +0x28, active portrait texture +0x1b0, noise texture +0x1a4, alpha/fade scalar +0x20, and CVBufTexture__DrawSpriteEx. Ret 0xc confirms three stack arguments after this and removes the stale phantom fourth argument. Static retail evidence only; exact screen-space semantics, runtime rendering, and rebuild parity remain unproven.",
                tags("messagebox", "dxengine", "battleline", "render", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("screen_x", intType),
                    param("screen_y", floatType),
                    param("viewport_height", intType)
                }
            ),
            new Spec(
                "0x004b8800",
                "CMessageBox__StopVoicePlaybackIfNotInCutscene",
                "CMessageBox__StopVoicePlaybackIfNotInCutscene",
                "__fastcall",
                voidType,
                "Wave450 signature/comment hardening: when the cutscene gate is clear, clears the CMessageBox voice path byte at +0x1c0 and stops/releases the active voice channel global DAT_008073d0 through CMessageBox__StopAndReleaseChannel and its vtable release. Static retail evidence only; exact audio object ownership, runtime voice behavior, and rebuild parity remain unproven.",
                tags("messagebox", "voice", "audio", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
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
            throw new RuntimeException("Wave450 apply had missing/bad entries");
        }
    }
}
