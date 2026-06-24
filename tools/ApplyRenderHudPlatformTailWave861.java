//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
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

public class ApplyRenderHudPlatformTailWave861 extends GhidraScript {
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
            "render-hud-platform-tail-wave861",
            "wave861-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "important-connective-infrastructure"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Spec commentOnly(String address, String name, String prototype, String comment, String... extraTags) {
        return new Spec(address, name, prototype, null, null, null, comment, tags(extraTags));
    }

    private Spec signature(String address, String name, String prototype, String convention,
            DataType returnType, ParameterImpl[] parameters, String comment, String... extraTags) {
        String[] combined = new String[extraTags.length + 1];
        combined[0] = "signature-hardened";
        System.arraycopy(extraTags, 0, combined, 1, extraTags.length);
        return new Spec(address, name, prototype, convention, returnType, parameters, comment, tags(combined));
    }

    private Spec[] specs() throws Exception {
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType floatType = FloatDataType.dataType;

        return new Spec[] {
            commentOnly(
                "0x00523a70",
                "CDXEngine__RenderMouseCursorSprite",
                "void CDXEngine__RenderMouseCursorSprite(void)",
                "Wave861 static read-back/comment hardening: cursor/HUD sprite helper called by CGameInterface__Render, CLevelBriefingLog__Render, CMessageLog__Render, CPauseMenu__Render, and CFrontEnd__RenderCursorEndSceneAndAsyncSave. Lazily resolves mouse.tga into DAT_0089bd98, falls back to meshtex\\default.tga via DAT_0089ce84/refcount increment when the mouse texture lookup fails, then calls CVBufTexture__DrawSpriteEx using DAT_0089bda8/DAT_0089bda4 cursor coordinates and DAT_00640054 alpha state. Static retail Ghidra/string/xref evidence only; exact cursor global layout, runtime cursor rendering, BEA patching, and rebuild parity remain unproven.",
                "render",
                "hud",
                "cursor",
                "texture"
            ),
            commentOnly(
                "0x00523b30",
                "CVBufTexture__DestroyGlobalHudHandle89BD98",
                "void CVBufTexture__DestroyGlobalHudHandle89BD98(void)",
                "Wave861 static read-back/comment hardening: CLTShell shutdown helper for global cursor/HUD texture handle DAT_0089bd98. If present, decrements the texture refcount through CTexture__DecrementRefCountFromNameField(texture+8), then clears DAT_0089bd98. Static retail evidence only; exact owner/source identity, runtime texture lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                "texture",
                "shutdown",
                "refcount"
            ),
            commentOnly(
                "0x00527990",
                "CGame__DrawLocalCoopControllerPrompt",
                "void CGame__DrawLocalCoopControllerPrompt(void)",
                "Wave861 static read-back/comment hardening: local co-op/controller prompt renderer reached from CFrontEnd__Render, CGame__Render, and CFEPMultiplayerStart__Render. Uses viewport/window dimensions, controller-port comparisons through CFrontEnd__GetPlayer0ControllerPort, localized text tokens via FrontEndText__GetLocalizedOrFallbackTextByToken/CText__GetStringById, TextLayout__WrapWideTextToFixedLines, CDXFont__GetTextExtent, CVBufTexture__DrawSpriteWithDefaultTextureFallback, and CDXFont__DrawText; sets DAT_009c690d/DAT_009c68ac prompt state bytes. Static retail/source-reference evidence only; exact argument ABI/controller prompt state layout, runtime unplug/reconnect UI behavior, BEA patching, and rebuild parity remain unproven.",
                "game",
                "frontend",
                "hud",
                "controller"
            ),
            signature(
                "0x00527de0",
                "CWaterRenderSystem__ResetAndMarkSourceFlag",
                "void CWaterRenderSystem__ResetAndMarkSourceFlag(void * validation_record)",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("validation_record", voidPtr, currentProgram)
                },
                "Wave861 static read-back/signature correction: ECX-only render validation helper called three times from CWaterRenderSystem__RenderMainPass. The body clears DAT_00854dd8 and sets DAT_00854dd9 from whether validation_record+0x10 is zero, linking this row to the Wave570 render-validation record helpers around 0x00527cc0-0x00527e00. Static retail evidence only; exact validation-record/source identity, runtime water/D3D validation behavior, BEA patching, and rebuild parity remain unproven.",
                "water",
                "render-validation"
            ),
            commentOnly(
                "0x00527f50",
                "PCPlatform__AsyncMusicStreamWorkerMain",
                "int PCPlatform__AsyncMusicStreamWorkerMain(void)",
                "Wave861 static read-back/comment hardening: CreateThread target installed by PCPlatform__InitAsyncMusicStream. The worker waits on four event handles around DAT_0089beb8/DAT_0089bec4/DAT_0089bec0/DAT_0089bebc, opens/validates the COggFileRead-like stream at DAT_0089bfd4 for 44100 Hz stereo, fills DirectSound buffer ranges through DAT_0089bec8 vtable calls, zero-fills underrun gaps, tracks DAT_0089bed0/DAT_0089becc/DAT_0089beac, and exits on wait case 3. Static retail evidence only; exact DirectSound/Ogg object layouts, runtime audio playback, thread-safety behavior, BEA patching, and rebuild parity remain unproven.",
                "pc-platform",
                "audio",
                "async-music"
            ),
            commentOnly(
                "0x005282b0",
                "PCPlatform__InitAsyncMusicStream",
                "void PCPlatform__InitAsyncMusicStream(void)",
                "Wave861 static read-back/comment hardening: async music stream initializer called by PCPlatform__InitMusicPlaylist before CMusic__LoadPlaylistFromDir(this,\"data\\music\"). Builds a DirectSound-style buffer format for 0xac44 Hz stereo/16-bit audio, creates four event handles, starts PCPlatform__AsyncMusicStreamWorkerMain with CreateThread, initializes the stream buffer through DAT_0089bec8, allocates a 0x22f0 COggFileRead-like object into DAT_0089bfd4, clears DAT_0089bed4, and resets DAT_0089bed0. Static retail/string/xref evidence only; exact DirectSound buffer descriptor, Ogg reader layout, runtime audio playback, BEA patching, and rebuild parity remain unproven.",
                "pc-platform",
                "audio",
                "async-music",
                "init"
            ),
            commentOnly(
                "0x00528460",
                "PCPlatform__ShutdownAsyncMusicStream",
                "void PCPlatform__ShutdownAsyncMusicStream(void)",
                "Wave861 static read-back/comment hardening: async music stream shutdown helper reached from the PCPlatform music/device cleanup band. When DAT_0089bec8 exists it signals the shutdown event DAT_0089bebc, polls DAT_0089beb4 until the worker exits, stops/releases the DirectSound buffer object, closes the event handles, destroys DAT_0089bfd4 when present, clears DAT_0089bed4, and resets DAT_0089bed0. Static retail evidence only; exact shutdown ownership, runtime thread/audio behavior, BEA patching, and rebuild parity remain unproven.",
                "pc-platform",
                "audio",
                "async-music",
                "shutdown"
            ),
            signature(
                "0x00528540",
                "PCPlatform__KickAsyncMusicStreamRead",
                "void PCPlatform__KickAsyncMusicStreamRead(char * track_path)",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("track_path", charPtr, currentProgram)
                },
                "Wave861 static read-back/signature correction: cdecl one-argument async music read-kick helper. If the DirectSound buffer object DAT_0089bec8 exists, it queries the current status through vtable slot 0x24, compares track_path with DAT_0089bed4 using CRT__MbsIcmp_LocaleLock, copies new paths into DAT_0089bed4 with CRT__MbsNcpy_LocaleLock, clears DAT_0089beac, and signals DAT_0089beb8 to wake the worker. Static retail evidence only; exact track path lifetime, stream state layout, runtime music behavior, BEA patching, and rebuild parity remain unproven.",
                "pc-platform",
                "audio",
                "async-music",
                "path"
            ),
            commentOnly(
                "0x005285b0",
                "PCPlatform__ResetAsyncMusicStream",
                "void PCPlatform__ResetAsyncMusicStream(void)",
                "Wave861 static read-back/comment hardening: async music reset helper for the active DirectSound buffer object at DAT_0089bec8. When present, it invokes vtable slot 0x48, resets event handles DAT_0089bec4 and DAT_0089bec0, and also calls ResetEvent on the handle currently resolved by Ghidra as PCPlatform__KickAsyncMusicStreamRead because of a symbol/address collision. Static retail evidence only; exact event-handle global naming, runtime reset behavior, BEA patching, and rebuild parity remain unproven.",
                "pc-platform",
                "audio",
                "async-music",
                "reset"
            ),
            signature(
                "0x005285e0",
                "PCPlatform__UpdateAsyncMusicStreamVolume",
                "void PCPlatform__UpdateAsyncMusicStreamVolume(float normalized_volume)",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    new ParameterImpl("normalized_volume", floatType, currentProgram)
                },
                "Wave861 static read-back/signature correction: cdecl one-float async music volume helper. When DAT_0089bec8 exists, it clamps normalized_volume to 0.0-1.0, applies the observed power curve, converts the result into a DirectSound attenuation-style value using the 10000.0 constant at 0x005db3b4, and forwards it through DAT_0089bec8 vtable slot 0x3c. Static retail evidence only; exact volume curve semantics, DirectSound unit contract, runtime audio behavior, BEA patching, and rebuild parity remain unproven.",
                "pc-platform",
                "audio",
                "async-music",
                "volume"
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

    private boolean conventionOk(Function fn, String expectedConvention) throws Exception {
        if (expectedConvention == null) {
            return true;
        }
        return expectedConvention.equals(fn.getCallingConventionName());
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
        boolean prototypeOk = fn.getSignature().getPrototypeString().equals(spec.expectedPrototype);
        boolean conventionOk = conventionOk(fn, spec.callingConvention);
        boolean signatureOk = prototypeOk && conventionOk;
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
            println("BADSIG: " + spec.address + " expected=" + spec.expectedPrototype + " convention=" + spec.callingConvention + " actual=" + fn.getSignature().getPrototypeString() + " convention=" + fn.getCallingConventionName());
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
                && conventionOk(readback, spec.callingConvention)
                && spec.comment.equals(readback.getComment())
                && hasAllTags(readback, spec.tags);
            if (readbackOk) {
                println("READBACK_OK: " + spec.address + " " + actualSignature + " convention=" + readback.getCallingConventionName());
            } else {
                println("READBACK_BAD: " + spec.address + " name=" + readback.getName() + " signature=" + actualSignature + " convention=" + readback.getCallingConventionName());
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
