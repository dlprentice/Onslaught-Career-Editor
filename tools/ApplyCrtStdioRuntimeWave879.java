//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtStdioRuntimeWave879 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] previousNames;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String[] previousNames, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousNames = previousNames;
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

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "crt-stdio-runtime-wave879",
            "wave879-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-crt-runtime-infrastructure",
            "high-importance-low-local-evidence-density",
            "compiler-runtime",
            "crt-stdio",
            "raw-commentless-head"
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
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        String actualSignature = readBack.getSignature().toString();
        if (!actualSignature.equals(spec.signature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature);
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!nameAllowed(fn.getName(), spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + fn.getSignature());
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.signature);
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055dcb0",
                "CRT__AcosDispatch_ST0",
                new String[] {"OID__AcosWrapper"},
                "void CRT__AcosDispatch_ST0(void)",
                "Wave879 static read-back: owner-corrected CRT acos dispatch wrapper formerly OID__AcosWrapper. The body receives the active x87 ST0 value as Ghidra float10, stores it as a double, calls CRT__ExtractFiniteExponentMaskOrPassThrough on the double words, then calls CRT__Acos(low, high). Xref export shows 41 gameplay/world/math callsites, so the OID owner label was too narrow. Static retail CRT/FPU evidence only; exact MSVC helper identity, x87 status behavior, full IEEE edge-case parity, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("owner-corrected", "fpu-math", "acos-dispatch", "st0-dispatch")
            ),
            new Spec(
                "0x0055dd7b",
                "CRT__RunStaticInitRangesWithOptionalCallback",
                new String[] {"CFastVB__RunStaticInitRangesWithOptionalCallback"},
                "void CRT__RunStaticInitRangesWithOptionalCallback(void)",
                "Wave879 static read-back: owner-corrected CRT static-initialization range walker formerly CFastVB__RunStaticInitRangesWithOptionalCallback. The body conditionally calls PTR_CRT__InitRuntimeFromStoredFrameGlobals_006532e8, then invokes CRT__InvokeFunctionPointerRange over 0x00622b10-0x00622b28 and 0x00622000-0x00622b0c. Its direct xref is entry, so the CFastVB owner label was too narrow. Static retail CRT startup evidence only; exact table ownership, callback prototypes, initialization ordering, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("owner-corrected", "static-init", "function-pointer-ranges", "entry-xref")
            ),
            new Spec(
                "0x0055de6f",
                "CRT__Lock_0x0D",
                new String[] {},
                "void CRT__Lock_0x0D(void)",
                "Wave879 static read-back: compact CRT lock-index wrapper that calls CRT__LockByIndex(0x0d). Xrefs are CRT__DoExit and CRT__DoExit_1, tying it to process/onexit shutdown synchronization. Static retail CRT lock evidence only; exact CRT lock table identity, shutdown concurrency behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("crt-lock", "exit-lock", "shutdown")
            ),
            new Spec(
                "0x0055de78",
                "CRT__Unlock_0x0D",
                new String[] {},
                "void CRT__Unlock_0x0D(void)",
                "Wave879 static read-back: compact CRT unlock-index wrapper that calls CRT__UnlockByIndex(0x0d). Xrefs are CRT__DoExit and CRT__DoExit_1, pairing it with CRT__Lock_0x0D around shutdown/onexit handling. Static retail CRT lock evidence only; exact CRT lock table identity, shutdown concurrency behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("crt-lock", "exit-lock", "shutdown")
            ),
            new Spec(
                "0x0055de9b",
                "sprintf",
                new String[] {},
                "int __cdecl sprintf(char * dst, char * format)",
                "Wave879 static read-back: CRT sprintf-family formatted-output wrapper. The body seeds a stack output descriptor with dst, mode bits 0x42, and limit 0x7fffffff, calls CRT__FormatOutputToStream with format and stack varargs, then either terminates the output buffer or flushes through CRT__FlushPendingStreamWrites. Xref export shows 304 callsites across errors, config, gameplay, renderer, resource, and logging paths. Static retail CRT stdio evidence only; exact CRT version, complete format semantics, buffer-safety contract, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("printf-family", "format-output", "varargs", "stdio-string-output")
            ),
            new Spec(
                "0x0055def0",
                "CRT__AllocaProbe",
                new String[] {},
                "void CRT__AllocaProbe(void)",
                "Wave879 static read-back: CRT stack-probe helper for dynamic stack allocation. The body walks downward by 0x1000-byte pages from ESP toward the requested stack target in EAX, touches each page, then restores the caller return address on the adjusted stack. Xref export shows 40 compiler/runtime callers. Static retail compiler-runtime evidence only; exact MSVC helper identity, guard-page behavior, stack-commit side effects, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("alloca-probe", "stack-probe", "compiler-runtime")
            ),
            new Spec(
                "0x0055e38c",
                "vsprintf",
                new String[] {},
                "int __cdecl vsprintf(char * dst, char * format, void * args)",
                "Wave879 static read-back: CRT vsprintf-family wrapper. The body builds the same unbounded stack output descriptor pattern as sprintf, passes the supplied args pointer directly to CRT__FormatOutputToStream, and terminates or flushes the output cursor. Xrefs include CConsole__Printf, Log__WriteFormatted, CDXApplication__ShowErrorBoxV, and WinMain error/reporting paths. Static retail CRT stdio evidence only; exact CRT version, complete format semantics, buffer-safety contract, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("printf-family", "format-output", "varargs", "stdio-string-output")
            ),
            new Spec(
                "0x0055e3ea",
                "CRT__FpuIntrinsicDispatch2Thunk",
                new String[] {"CPDSimpleSprite__FpuDispatchStub"},
                "void __cdecl CRT__FpuIntrinsicDispatch2Thunk(void)",
                "Wave879 static read-back: owner-corrected CRT/FPU intrinsic dispatch thunk formerly CPDSimpleSprite__FpuDispatchStub. The body tail-calls __cintrindisp2 and returns, while xref export shows 44 broad math/renderer/gameplay/UI callsites rather than a sprite-local helper. Static retail compiler-runtime evidence only; exact intrinsic selector semantics, x87/SSE status behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("owner-corrected", "fpu-intrinsic-dispatch", "compiler-runtime", "broad-math-xrefs")
            ),
            new Spec(
                "0x0055e42a",
                "Win32__CaptureSystemTimeAsFileTimeTicks",
                new String[] {},
                "void Win32__CaptureSystemTimeAsFileTimeTicks(void)",
                "Wave879 static read-back: Win32 time snapshot helper. DATA xref 0x00622b18 points to this static initializer-style row; the body calls GetSystemTimeAsFileTime and combines the low/high FILETIME words into the global tick pair at 0x009d0900. Static retail Win32/CRT startup evidence only; exact global ownership, wall-clock policy, runtime ordering, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("system-time", "filetime", "static-init", "win32")
            ),
            new Spec(
                "0x0055e490",
                "fopen",
                new String[] {},
                "void * __cdecl fopen(char * path, char * mode)",
                "Wave879 static read-back: CRT fopen wrapper that forwards path, mode, and flag 0x40 to CRT__OpenFileByModeString_AutoUnlock. Xref export shows 29 file-opening callsites spanning console logs, resource files, missions, textures, sound, save/load, and frontend paths. Static retail CRT file I/O evidence only; exact CRT version, share/lock policy, path normalization, runtime filesystem behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("stdio-file", "fopen", "file-io")
            ),
            new Spec(
                "0x0055e4a3",
                "fclose",
                new String[] {},
                "int __cdecl fclose(void * file)",
                "Wave879 static read-back: CRT fclose wrapper. The body rejects/clears stream records flagged with bit 0x40, otherwise locks the stream route, calls __fclose_lk, releases the route, and returns the close result. Xref export shows 29 matching close callsites across the same file/log/resource/save paths as fopen. Static retail CRT file I/O evidence only; exact CRT version, stream flag meaning, close/flush side effects, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("stdio-file", "fclose", "file-io")
            ),
            new Spec(
                "0x0055e520",
                "fprintf",
                new String[] {},
                "int __cdecl fprintf(void * file, char * format)",
                "Wave879 static read-back: CRT fprintf-family wrapper. The body locks the stream route for file, ensures its stream buffer, formats through CRT__FormatOutputToStream with stack varargs, flushes pending writes when needed, unlocks, and returns the format result. Xrefs are CConsole__Printf, Log__WriteFormatted, and Log__VWriteFormatted path evidence. Static retail CRT stdio evidence only; exact CRT version, complete format semantics, stream-buffer contract, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("printf-family", "format-output", "stdio-file", "varargs")
            ),
            new Spec(
                "0x0055e607",
                "WcsLen",
                new String[] {},
                "int __cdecl WcsLen(short * wstr)",
                "Wave879 static read-back: 16-bit wide-string length helper. The body advances over short units until the terminating zero and returns the element count. Xref export shows 23 UI/text conversion callsites including FromWCHAR, FE button/menu text, FrontEnd__GetLevelName, and mission text wrapping. Static retail wide-string evidence only; exact CRT identity, null-pointer behavior, runtime localization behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("wide-string", "wcslen", "ui-text")
            ),
            new Spec(
                "0x0055dccd",
                "CRT__Acos",
                new String[] {},
                "double __cdecl CRT__Acos(int lowWord, uint highWord)",
                "Wave879 context refresh: acos-style floating-point helper checks FPU control-word state, handles domain/special-value paths, computes atan(sqrt((1-x)*(1+x)), x) for in-range values, and dispatches CRT math error/exit handling through DAT_009d08b4. Xref evidence now reaches it from owner-corrected CRT__AcosDispatch_ST0 at 0x0055dcb0. Static retail math helper evidence only; exact CRT version, full IEEE edge-case parity, runtime math status behavior, BEA patching, and rebuild parity remain unproven.",
                tags("context-refresh", "math-helper", "fpu-control", "callsite-verified")
            ),
            new Spec(
                "0x0055da76",
                "CRT__InitRuntimeFromStoredFrameGlobals",
                new String[] {},
                "void CRT__InitRuntimeFromStoredFrameGlobals(void)",
                "Wave879 context refresh: runtime initialization stub tied to stored frame/global setup. The body calls CRT__InitFloatConversionDispatchTable, probes processor features through CDXTexture__ProbeProcessorFeaturePresentOrFallback, stores the result in DAT_009d08b8, then calls CRT__InitFpuControlWord_0x10000_0x30000. Xrefs include computed call evidence from owner-corrected CRT__RunStaticInitRangesWithOptionalCallback and DATA row 0x006532e8. Static retail runtime-init evidence only; exact startup table semantics, CPU feature policy, FPU side effects, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("context-refresh", "runtime-init", "fpu-control", "static-init")
            ),
            new Spec(
                "0x0055de81",
                "CRT__InvokeFunctionPointerRange",
                new String[] {},
                "void __cdecl CRT__InvokeFunctionPointerRange(void * begin, void * end)",
                "Wave879 context refresh: iterates 4-byte function-pointer slots from begin to end and calls each non-null entry. Xrefs include CRT__DoExit and owner-corrected CRT__RunStaticInitRangesWithOptionalCallback. Static retail CRT helper evidence only; exact table ownership, callback prototypes, runtime initialization/shutdown ordering, BEA patching, and rebuild parity remain unproven.",
                tags("context-refresh", "function-pointer-range", "static-init", "callsite-verified")
            )
        };

        println("MODE: " + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (!dryRun) {
            println("REPORT: Save requested by headless post-script");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave879 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
