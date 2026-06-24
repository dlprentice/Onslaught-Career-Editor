//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyFinalStaticTailWave900 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "final-static-tail-wave900",
            "wave900-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "final-commentless-tail",
            "static-function-quality-closure"
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
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("MISSING_READBACK: " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("BADNAME_READBACK: " + spec.address + " got " + fn.getName());
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            throw new IllegalStateException("BADSIG_READBACK: " + spec.address + " got " + fn.getSignature());
        }
        String comment = fn.getComment();
        if (comment == null || !comment.equals(spec.comment)) {
            throw new IllegalStateException("BADCOMMENT_READBACK: " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("BADTAGS_READBACK: " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    stats.wouldRename++;
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                    return;
                }
                stats.renamed++;
                println("RENAME_BLOCKED_BY_POLICY: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.bad++;
                return;
            }
            if (!fn.getSignature().toString().equals(spec.signature)) {
                println("BADSIG: " + spec.address + " got " + fn.getSignature() + " expected " + spec.signature);
                stats.bad++;
                return;
            }
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + spec.signature);
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
            Thread.sleep(50);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + ex.getMessage());
        }
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x005d04e6",
                "RtlUnwind",
                "void __stdcall RtlUnwind(PVOID TargetFrame, PVOID TargetIp, PEXCEPTION_RECORD ExceptionRecord, PVOID ReturnValue)",
                "Wave900 final static-tail read-back: Windows RtlUnwind import thunk at IAT slot 0x005d81e4, called by __global_unwind2 at 0x0055d99b and CRT__SehRtlUnwindAndRestoreFrame at 0x0055d705. Static retail Ghidra evidence only: preserves the current stdcall import signature while the body is the one-instruction JMP through the import address table. Exact Windows runtime unwind behavior, exception-dispatch behavior, BEA patching, and rebuild parity remain unproven.",
                tags("windows-import-thunk", "rtl-unwind", "crt-seh-bridge", "one-instruction-thunk")
            ),
            new Spec(
                "0x005d06f0",
                "CRT__InitSehFrameNoop",
                "void CRT__InitSehFrameNoop(void)",
                "Wave900 final static-tail read-back: compact CRT SEH-frame setup helper called by CDXTexture__InitCpuVendorAndSimdFlags at 0x005891cb. Static retail Ghidra evidence only: preserves the current name/signature while the locked-stack body pushes -1, the incoming EAX, and FS:[0], installs ESP into FS:[0], copies the caller EBP into the stack record, pivots EBP to ESP+0xc, pushes the original EAX return target, and returns. Exact CRT helper source identity, compiler prolog role, runtime exception behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-seh-frame", "locked-stack-abi", "cdxtexture-simd-init", "compiler-runtime")
            ),
            new Spec(
                "0x005d08ad",
                "CRT__TmpFile_OpenUniqueBinaryStream",
                "int CRT__TmpFile_OpenUniqueBinaryStream(void)",
                "Wave900 final static-tail read-back: CRT temporary binary-stream opener called by CDXTexture__InitHostIoCallbacks at 0x005b1d51. Static retail Ghidra evidence only: preserves the current name/signature while the locked-stack body locks CRT slot 3, initializes or increments the temp-name buffer at DAT_009d3038, acquires a stream slot, opens a file descriptor with flags 0x8542 and permission 0x180, retries on errno 0x11 via CRT__IncrementDotSuffixCounter, duplicates the selected name into stream+0x1c, stores DAT_009d0ad4|0x80 and the file descriptor, unlocks the stream route, and returns the stream pointer or 0. Exact CRT FILE layout, temporary-name policy, runtime filesystem behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-tempfile", "cdxtexture-host-io", "locked-stack-abi", "filesystem-runtime-boundary")
            ),
            new Spec(
                "0x005d0a9f",
                "CRT__LongJmpProbe_NoOp",
                "void CRT__LongJmpProbe_NoOp(void)",
                "Wave900 final static-tail read-back: _longjmp-adjacent CRT probe helper called by _longjmp at 0x005d05f0. Static retail Ghidra evidence only: preserves the current name/signature while the locked-stack SEH-shaped body installs a temporary exception-list frame, touches the jmp-buffer pointer at EBP+0x8, writes local status 1, restores FS:[0], and returns with RET 0x4. Exact CRT source identity, jmp-buffer schema, runtime longjmp/SEH behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-longjmp", "seh-shaped-probe", "locked-stack-abi", "compiler-runtime")
            ),
            new Spec(
                "0x005d0c0c",
                "GetCurrentProcessId",
                "DWORD __stdcall GetCurrentProcessId(void)",
                "Wave900 final static-tail read-back: Windows GetCurrentProcessId import thunk at IAT slot 0x005d8144, called by init_namebuf at 0x005d09c9. Static retail Ghidra evidence only: preserves the current stdcall import signature while the body is the one-instruction JMP through the import address table. Exact Windows runtime/process-id behavior, temp-name entropy role, BEA patching, and rebuild parity remain unproven.",
                tags("windows-import-thunk", "get-current-process-id", "temp-name-helper", "one-instruction-thunk")
            ),
            new Spec(
                "0x005d0c7f",
                "CRT__LCMapStringW_AnsiCompat",
                "int CRT__LCMapStringW_AnsiCompat(void)",
                "Wave900 final static-tail read-back: CRT wide-string locale mapping compatibility helper called by CFEPSaveGame__WideCharToLowerCompat at 0x005d0a89. Static retail Ghidra evidence only: preserves the current name/signature while the locked-stack body probes LCMapStringW versus LCMapStringA support into DAT_009d304c, bounds the input length through CRT__WcsNLen, directly calls LCMapStringW when available, otherwise falls back through WideCharToMultiByte, LCMapStringA, optional strncpy for byte output, MultiByteToWideChar, codepage DAT_009d09a8, and alloca probes. Exact CRT locale policy, parameter names, runtime save-name collation behavior, BEA patching, and rebuild parity remain unproven.",
                tags("crt-locale", "frontend-save-name", "wide-string-compat", "locked-stack-abi")
            ),
            new Spec(
                "0x005d5120",
                "CTexture__FindTexture_Unwind",
                "void CTexture__FindTexture_Unwind(void)",
                "Wave900 final static-tail read-back: texture.cpp CTexture__FindTexture unwind cleanup callback reached from scope-table DATA xref 0x0061d9cc. Static retail Ghidra evidence only: preserves the current name/signature while the locked-stack body pushes debug line 0x98, debug path pointer 0x00632ef0 (C:\\dev\\ONSLAUGHT2\\texture.cpp), allocation/type value 0x2, loads the allocation pointer from EBP-0x210, and calls OID__FreeObject_Callback. Exact parent source body, allocation ownership, runtime exception cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("texture-find-unwind", "scope-table", "texture-cpp", "oid-free-callback")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = (args == null || args.length == 0) ? "dry" : args[0];
        boolean dryRun = isDryRun(mode);
        println("ApplyFinalStaticTailWave900 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }

        println(String.format(
            "SUMMARY: updated=%d skipped=%d renamed=%d would_rename=%d missing=%d bad=%d",
            stats.updated,
            stats.skipped,
            stats.renamed,
            stats.wouldRename,
            stats.missing,
            stats.bad
        ));
        if (stats.missing != 0 || stats.bad != 0 || stats.renamed != 0) {
            throw new IllegalStateException("ApplyFinalStaticTailWave900 had failures");
        }
    }
}
