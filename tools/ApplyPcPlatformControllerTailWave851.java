//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyPcPlatformControllerTailWave851 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedSignature;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedSignature, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedSignature = expectedSignature;
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
            "pc-platform-controller-tail-wave851",
            "wave851-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified"
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

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        return fn.getSignature().toString().equals(spec.expectedSignature);
    }

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            ok = false;
        }
        if (!signatureMatches(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedSignature + " actual=" + fn.getSignature());
            ok = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            ok = false;
        }
        if (!hasAllTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            ok = false;
        }
        if (!ok) {
            stats.bad++;
        }
        return ok;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            stats.bad++;
            return;
        }
        if (!signatureMatches(fn, spec)) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedSignature + " actual=" + fn.getSignature());
            stats.bad++;
            return;
        }

        boolean needsCommentOrTags = !spec.comment.equals(fn.getComment()) || !hasAllTags(fn, spec.tags);
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }

        if (!needsCommentOrTags) {
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " needsCommentOrTags=true");
            stats.skipped++;
            return;
        }

        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        if (readBackMatches(fn, spec, stats)) {
            println("APPLY_OK: " + spec.address + " " + spec.expectedName + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005140e0",
                "CDXEngine__CaptureAviFrame",
                "void CDXEngine__CaptureAviFrame(void)",
                "Wave851 static read-back/comment hardening: CDXEngine__PostRender calls this AVI capture helper at 0x0053ef63. When DAT_008892d5 is nonzero, the body acquires/locks the D3D render target through device globals, copies rows into DAT_00889180 using width DAT_00888a08 and height DAT_00888a0c, writes one frame through AVIStreamWrite(DAT_008891bc,DAT_00889188,...), logs \"AVIStreamWrite() failed!\" on failure, releases acquired surfaces, and increments DAT_00889188. Static retail/source-reference evidence only; exact D3D surface/AVI buffer layouts, runtime capture output, filesystem behavior, BEA patching, and rebuild parity remain deferred.",
                tags("pc-runtime", "avi-capture", "post-render")
            ),
            new Spec(
                "0x00514210",
                "OptionsEntries__InitDefaultSingleBindingsTable",
                "void __cdecl OptionsEntries__InitDefaultSingleBindingsTable(void)",
                "Wave851 static read-back/comment hardening: initializes the PC single/default options binding table from DAT_008892d8 through DAT_00889898 with 47 OptionsEntries__InitSingleBindingEntry calls, then writes the DAT_008898b8 sentinel. Source PCController.cpp default mapping rows support the controller/action/key-binding role, but the exact retail options-entry field schema and runtime remap/persistence behavior remain deferred. Static retail/source-reference evidence only; BEA patching and rebuild parity remain deferred.",
                tags("controller", "options-bindings", "source-pccontroller")
            ),
            new Spec(
                "0x00514620",
                "CPCController__scalar_deleting_dtor",
                "void * __thiscall CPCController__scalar_deleting_dtor(void * this, uchar free_flag)",
                "Wave851 static read-back/comment hardening: CPCController scalar deleting destructor vtable slot 0 at 0x005e48e0. The body calls CController__dtor_Thunk(this), conditionally frees this through CDXMemoryManager__Free(&DAT_009c3df0,this) when free_flag bit 0 is set, and returns this. Static retail/source-reference evidence only; exact controller allocation ownership, runtime destruction behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "vtable", "destructor")
            ),
            new Spec(
                "0x00514640",
                "CPCController__GetJoyAnalogueLeftX",
                "float __stdcall CPCController__GetJoyAnalogueLeftX(int pad_number)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 9 at 0x005e4904. The body guards pad_number against DAT_00888ff8, then reads current pad-state field +0x00 from (&DAT_00888f94)[pad_number] and scales by the 0.001 constant. Source PCController::GetJoyAnalogueLeftX matches the LT.JoyState(pad)->lX / 1000.0f direction. Static retail/source-reference evidence only; exact pad-state layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "analogue-input", "source-pccontroller")
            ),
            new Spec(
                "0x00514670",
                "CPCController__GetJoyAnalogueLeftY",
                "float __stdcall CPCController__GetJoyAnalogueLeftY(int pad_number)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 10 at 0x005e4908. The body guards pad_number against DAT_00888ff8, then reads current pad-state field +0x04 from (&DAT_00888f94)[pad_number] and scales by the 0.001 constant. Source PCController::GetJoyAnalogueLeftY matches the LT.JoyState(pad)->lY / 1000.0f direction. Static retail/source-reference evidence only; exact pad-state layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "analogue-input", "source-pccontroller")
            ),
            new Spec(
                "0x005146a0",
                "CPCController__GetJoyAnalogueRightX",
                "float __stdcall CPCController__GetJoyAnalogueRightX(int pad_number)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 11 at 0x005e490c. The body guards pad_number against DAT_00888ff8, then reads current pad-state field +0x08 from (&DAT_00888f94)[pad_number] and scales by the 0.001 constant. Source PCController::GetJoyAnalogueRightX matches the LT.JoyState(pad)->lZ / 1000.0f direction. Static retail/source-reference evidence only; exact pad-state layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "analogue-input", "source-pccontroller")
            ),
            new Spec(
                "0x005146d0",
                "CPCController__GetJoyAnalogueRightY",
                "float __stdcall CPCController__GetJoyAnalogueRightY(int pad_number)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 12 at 0x005e4910. The body checks the per-pad enabled/present table at DAT_00889014, guards pad_number against DAT_00888ff8, then reads current pad-state field +0x14, subtracts 32768.0f, and scales by 1/32768. Source PCController::GetJoyAnalogueRightY matches the LT.JoyState(pad)->lRz center/scale direction. Static retail/source-reference evidence only; exact pad-state layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "analogue-input", "source-pccontroller")
            ),
            new Spec(
                "0x005147b0",
                "CPCController__GetJoyButtonOnce",
                "bool __stdcall CPCController__GetJoyButtonOnce(int pad_number, int button)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 3 at 0x005e48ec. The body returns true only for the joystick button edge old==0/current!=0 using old pad-state table (&DAT_00888fa4)[pad_number] and current pad-state table (&DAT_00888f94)[pad_number] at button byte offset 0x30+button. Source PCController.h delegates this virtual to LT.JoyButtonOnce. Static retail/source-reference evidence only; exact pad-state layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "button-input", "source-pccontroller")
            ),
            new Spec(
                "0x005147f0",
                "CPCController__GetJoyButtonOn",
                "bool __stdcall CPCController__GetJoyButtonOn(int pad_number, int button)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 4 at 0x005e48f0. The body returns whether the current pad-state table (&DAT_00888f94)[pad_number] has a nonzero byte at offset 0x30+button. Source PCController.h delegates this virtual to LT.JoyButtonOn. Static retail/source-reference evidence only; exact pad-state layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "button-input", "source-pccontroller")
            ),
            new Spec(
                "0x00514810",
                "CPCController__GetJoyButtonRelease",
                "bool __stdcall CPCController__GetJoyButtonRelease(int pad_number, int button)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 5 at 0x005e48f4. The body returns true only for the joystick button release edge old!=0/current==0 using old pad-state table (&DAT_00888fa4)[pad_number] and current pad-state table (&DAT_00888f94)[pad_number] at button byte offset 0x30+button. Source PCController.h delegates this virtual to LT.JoyButtonRelease. Static retail/source-reference evidence only; exact pad-state layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "button-input", "source-pccontroller")
            ),
            new Spec(
                "0x00514850",
                "CPCController__GetKeyOnce",
                "bool __stdcall CPCController__GetKeyOnce(int key)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 6 at 0x005e48f8. The body forwards key to Wave850-readback PlatformInput__GetKeyOnceCore(&DAT_00855bb0,key), which reads/clears the once table and records consumed keys. Source PCController.h maps this virtual to PLATFORM.KeyOnce(key), and PCPlatform.cpp maps KeyOnce to LT.xKeyOnce. Static retail/source-reference evidence only; exact key-table/queue layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "keyboard-input", "source-pccontroller", "wave850-bridge")
            ),
            new Spec(
                "0x00514870",
                "CPCController__GetKeyState3",
                "bool __stdcall CPCController__GetKeyState3(int key)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 8 at 0x005e4900. The body forwards key to Wave850-readback PlatformInput__GetKeyState3Core(&DAT_00855bb0,key), which reads the held-state table without clearing. Source controller mapping uses key-on style queries for held mappings. Static retail/source-reference evidence only; exact key-table layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "keyboard-input", "wave850-bridge")
            ),
            new Spec(
                "0x00514890",
                "CPCController__GetKeyOn",
                "bool __stdcall CPCController__GetKeyOn(int key)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 7 at 0x005e48fc. The body forwards key to PlatformInput__GetKeyOn(key), which returns DAT_00888c94[key]. Source PCController.h maps this virtual to PLATFORM.KeyOn(key), and PCPlatform.cpp maps KeyOn to LT.xKeyOn. Static retail/source-reference evidence only; exact key-table layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "keyboard-input", "source-pccontroller")
            ),
            new Spec(
                "0x005148b0",
                "CPCController__GetJoyPovX",
                "float __stdcall CPCController__GetJoyPovX(int pad_number)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 13 at 0x005e4914. The body reads current pad-state POV field +0x20, returns 0.0f when the low word is -1, otherwise returns sin(POV * 0.00017453294). Static retail evidence only; exact DirectInput POV units/layout, runtime controller behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "pov-input")
            ),
            new Spec(
                "0x00514900",
                "CPCController__GetJoyPovY",
                "float __stdcall CPCController__GetJoyPovY(int pad_number)",
                "Wave851 static read-back/comment hardening: CPCController vtable slot 14 at 0x005e4918. The body reads current pad-state POV field +0x20, returns 0.0f when the low word is -1, otherwise returns -cos(POV * 0.00017453294). Static retail evidence only; exact DirectInput POV units/layout, runtime controller behavior, BEA patching, and rebuild parity remain deferred.",
                tags("controller", "pov-input")
            ),
            new Spec(
                "0x00514950",
                "PCPlatform__GetStorageDeviceCount",
                "int __stdcall PCPlatform__GetStorageDeviceCount(int * out_count)",
                "Wave851 static read-back/comment hardening: PC storage-device compatibility helper called by frontend storage/device flows. The body writes *out_count=1 and returns 0, modelling a single PC storage device for the console-shaped API. Static retail evidence only; runtime frontend save-device behavior, exact API contract, BEA patching, and rebuild parity remain deferred.",
                tags("pc-platform", "save-storage", "frontend-storage")
            ),
            new Spec(
                "0x00514960",
                "PCPlatform__GetStorageDeviceInfo",
                "int __stdcall PCPlatform__GetStorageDeviceInfo(int device, int * out_inserted, int * out_formatted, int * out_free_bytes, int * out_total_bytes)",
                "Wave851 static read-back/comment hardening: PC storage-device info compatibility helper called by frontend development/load/save/directory/virtual-keyboard paths. The body writes inserted=1 and formatted=1 when those outputs are non-null, writes 0x7fffffff to free/total byte outputs when present, and returns 0. Static retail evidence only; runtime frontend save-device behavior, actual filesystem capacity checks, BEA patching, and rebuild parity remain deferred.",
                tags("pc-platform", "save-storage", "frontend-storage")
            ),
            new Spec(
                "0x005149a0",
                "PCPlatform__GetStorageDeviceDisplayName",
                "int __stdcall PCPlatform__GetStorageDeviceDisplayName(int device, ushort * out_name)",
                "Wave851 static read-back/comment hardening: PC storage-device display-name helper called by CFEPDevelopment__RefreshWorldListCore. The body fetches localization string id 0x28, copies it to out_name via CRT__WStrCpy, and returns 0. Static retail evidence only; exact localized text, runtime frontend display behavior, BEA patching, and rebuild parity remain deferred.",
                tags("pc-platform", "save-storage", "localization")
            ),
            new Spec(
                "0x00514be0",
                "EnumerateSaveFiles_Main",
                "int __stdcall EnumerateSaveFiles_Main(int device, short * save_name, int * out_index, int allowed_overwrite)",
                "Wave851 static read-back/comment hardening: main PC save-name validation/enumeration helper called by CFEPSaveGame__CreateSave and CPauseMenu__ResumeGameAndPersistOptions. The body creates the \"savegames\\\" directory, builds \"savegames\\\" + FromWCHAR(save_name) + \".bes\", returns 6 when overwrite is disallowed and that path already opens for read, probes the path for write/create, then enumerates \"savegames\\*.bes\" via Win32 wrappers, skips attributes mask 0x16, strips the .bes suffix, compares case-insensitive wide names, writes the found index when applicable, closes the find handle, and returns 0 on match or 1 on failure. Static retail evidence only; runtime filesystem/save behavior, exact error-code contract, BEA patching, and rebuild parity remain deferred.",
                tags("pc-platform", "save-storage", "save-enumeration")
            ),
            new Spec(
                "0x00515190",
                "PCPlatform__CopyStorageDeviceId",
                "int __stdcall PCPlatform__CopyStorageDeviceId(int device, int * out_device)",
                "Wave851 static read-back/comment hardening: PC storage-device id compatibility helper called by CFEPDevelopment__RefreshWorldListCore and CFEPSaveGame__CreateSave. The body writes the input device id to *out_device and returns 0. Static retail evidence only; runtime frontend save-device behavior, BEA patching, and rebuild parity remain deferred.",
                tags("pc-platform", "save-storage", "frontend-storage")
            ),
            new Spec(
                "0x00515320",
                "PCPlatform__InitMusicPlaylist",
                "void __fastcall PCPlatform__InitMusicPlaylist(void * this)",
                "Wave851 static read-back/comment hardening: music/platform initialization slot at data xref 0x005e4934. The body calls PCPlatform__InitAsyncMusicStream(), then calls CMusic__LoadPlaylistFromDir(this,\"data\\music\"). Source Music.cpp has the playlist directory path flow through CMusic::AddDirectoryToPlaylist; the exact retail vtable owner name and platform music-device layout remain bounded. Static retail/source-reference evidence only; runtime audio playback, filesystem behavior, BEA patching, and rebuild parity remain deferred.",
                tags("music", "pc-platform", "playlist")
            ),
            new Spec(
                "0x00515970",
                "PlatformInput__GetKeyOn",
                "uchar __stdcall PlatformInput__GetKeyOn(int key)",
                "Wave851 static read-back/comment hardening: platform key-held wrapper called by CController__DoMappings, CPCController__GetKeyOn, DXParticleTexture__RenderAll, and CWaterRenderSystem__RenderMainPass. The body returns DAT_00888c94[key]. Source PCPlatform.cpp KeyOn maps to LT.xKeyOn(c), and ltshell.h xKeyOn returns KeyDown[c]. Static retail/source-reference evidence only; exact key-table ownership/layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("platform-input", "keyboard-input", "source-pcplatform")
            ),
            new Spec(
                "0x00515980",
                "PlatformInput__ConsumeKeyOnce",
                "uchar __stdcall PlatformInput__ConsumeKeyOnce(int key)",
                "Wave851 static read-back/comment hardening: platform one-shot key consumer called by frontend/game rendering paths. The body reads DAT_00888d94[key], clears that byte, and returns the consumed value. Source PCPlatform.cpp KeyOnce maps to LT.xKeyOnce(c), and ltshell.h xKeyOnce reads then clears KeyWasDown[c]. Static retail/source-reference evidence only; exact key-table ownership/layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("platform-input", "keyboard-input", "source-pcplatform")
            ),
            new Spec(
                "0x005159b0",
                "PlatformInput__ResetKeyStateTables",
                "void PlatformInput__ResetKeyStateTables(void)",
                "Wave851 static read-back/comment hardening: platform key-state reset wrapper called by frontend init, level load, FMV flow, and CDXFMV vfunc context. The body calls PlatformInput__ClearAllKeyStateTables(&DAT_00855bb0). Static retail/source-reference evidence only; exact key-table ownership/layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("platform-input", "keyboard-input", "reset")
            ),
            new Spec(
                "0x005159c0",
                "PLATFORM__SetKeySink",
                "void __stdcall PLATFORM__SetKeySink(void * key_sink)",
                "Wave851 static read-back/comment hardening: platform key-sink wrapper called by console bind/remap and controller-definition remap flows. The body forwards key_sink to Wave848-readback PlatformInput__SetKeySinkCore(&DAT_00855bb0,key_sink). Source PCPlatform.cpp SetKeytrap maps to LT.SetKeytrap(trap), and ltshell.cpp stores mCurrentKeytrap. Static retail/source-reference evidence only; exact callback ABI/key-sink layout, runtime remap behavior, BEA patching, and rebuild parity remain deferred.",
                tags("platform-input", "key-sink", "controls-remap", "wave848-bridge")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
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
            throw new RuntimeException("Wave851 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            currentProgram.flushEvents();
        }
    }
}
