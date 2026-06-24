//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
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

public class ApplyPlatformInputCoreWave848 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "platform-input-core-wave848",
            "wave848-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "source-reference-ltshell"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean sameDataType(DataType a, DataType b) {
        if (a == null || b == null) {
            return a == b;
        }
        return a.getName().equals(b.getName()) || a.getDisplayName().equals(b.getDisplayName()) || a.isEquivalent(b);
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        Parameter[] actualParams = fn.getParameters();
        if (actualParams.length != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < actualParams.length; i++) {
            Parameter actual = actualParams[i];
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

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            ok = false;
        }
        if (!sameSignature(fn, spec)) {
            println("BADSIG: " + spec.address + " actual=" + fn.getSignature() + " convention=" + fn.getCallingConventionName());
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
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

        boolean needsRename = false;
        boolean needsSignature = !sameSignature(fn, spec);
        boolean needsCommentOrTags = !spec.comment.equals(fn.getComment()) || !hasAllTags(fn, spec.tags);

        if (needsRename) {
            stats.wouldRename++;
        }
        if (needsSignature) {
            stats.signatureUpdated++;
        }
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }

        if (!needsRename && !needsSignature && !needsCommentOrTags) {
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName()
                + " needsRename=" + needsRename
                + " needsSignature=" + needsSignature
                + " needsCommentOrTags=" + needsCommentOrTags);
            stats.skipped++;
            return;
        }

        if (needsSignature) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
        }
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            println("READBACK_MISSING: " + spec.address);
            stats.bad++;
            return;
        }
        if (readBackMatches(readBack, spec, stats)) {
            println("READBACK_OK: " + spec.address + " " + readBack.getName() + " " + readBack.getSignature());
            stats.updated++;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }
        println("ApplyPlatformInputCoreWave848 mode=" + (dryRun ? "dry" : "apply"));

        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00513120",
                "PlatformInput__InitDirectInput",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("window_handle", voidPtr)
                },
                "Wave848 static read-back/signature/comment hardening: DirectInput startup/enumeration path corresponding to source PCLTShell::InitDirectInput(HWND). The body seeds the global key-state queue pointer at 0x0063dc1c with 0x00855424, clears four new-type pad flags at this+0x33444, sets four DodgyJoyX-style slots at this+0x330cc to 1, writes deadzone 0x96 at this+0x330e0, calls DirectInput8Create at 0x00513178 with version 0x800/IID 0x0060c14c/output this+0x33478, enumerates game controllers through callback 0x00512ff0, rejects no-pad retail startup unless DAT_00662dd4 is set, caps joypad count to four, sets data format/cooperative level/capabilities/axis callbacks, sorts new-type pads ahead of old-type pads, and prints Found %d joypads. Static retail/source evidence only; exact DirectInput interface layout, exact pad-structure layout, runtime device behavior, BEA patching, and rebuild parity remain deferred.",
                tags("directinput", "joypad-enumeration", "signature-hardened", "ret-4")
            ),
            new Spec(
                "0x00513370",
                "PlatformInput__PollPadState",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("pad_index", intType),
                    param("rotate_buttons", boolType)
                },
                "Wave848 static read-back/comment hardening: per-pad DirectInput poll/update helper corresponding to source PCLTShell::UpdateJoystick(int). The body bounds pad_index against this+0x33448, checks the connected/enabled byte at this+0x33474+pad_index, optionally swaps current/old DIJOYSTATE2 buffers at this+0x333e4/0x333f4 when rotate_buttons is true, clears the active 0x110-byte state buffer, polls the DirectInput device at this+0x33408+pad_index*4 via vfunc +0x64, reacquires through vfunc +0x1c while HRESULT 0x8007001e/input-lost repeats, reads device state through vfunc +0x24, rotates button bytes 0x30-0x33 for new-type pads, and clears both state buffers when the pad is out of range or disabled. Static retail/source evidence only; exact DIJOYSTATE2 field schema, runtime controller behavior, BEA patching, and rebuild parity remain deferred.",
                tags("directinput", "joypad-poll", "comment-hardened", "ret-8")
            ),
            new Spec(
                "0x005134a0",
                "CEngine__GrabScreenshot",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("screenshot_index", intType)
                },
                "Wave848 static read-back/signature/comment hardening: screenshot capture helper corresponding to source ltshell.cpp grab path. The body obtains the render target through device globals, handles a surface-acquisition failure by routing HRESULT through HResultToString and DebugTrace(\"Failed for %s\"), checks surface formats 0x15/0x16, locks the surface read-only, formats the output path with string 0x0062c610 \"grabs\\\\scr%.4d.tga\" and the screenshot_index stack argument, calls ImageIO__WriteTGA24, unlocks the surface, and releases acquired surfaces. Static retail/source evidence only; exact D3D surface interface identity, runtime screenshot output behavior, filesystem behavior, BEA patching, and rebuild parity remain deferred.",
                tags("screenshot", "d3d-surface", "signature-hardened", "ret-4")
            ),
            new Spec(
                "0x005135f0",
                "PlatformInput__SetKeySinkCore",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("key_sink", voidPtr)
                },
                "Wave848 static read-back/comment hardening: key-sink setter used by PLATFORM__SetKeySink and CFEPVirtualKeyboard process/shutdown paths. The body stores key_sink into this+0x33458 and returns with RET 0x4. Static retail evidence only; exact key-sink object type, virtual-keyboard runtime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("key-sink", "virtual-keyboard", "comment-hardened", "ret-4")
            )
        };

        Stats stats = new Stats();
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
            throw new RuntimeException("Wave848 apply encountered missing/bad rows");
        }
    }
}
