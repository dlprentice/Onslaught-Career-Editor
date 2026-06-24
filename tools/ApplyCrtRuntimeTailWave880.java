//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCrtRuntimeTailWave880 extends GhidraScript {
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
            "crt-runtime-tail-wave880",
            "wave880-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-crt-runtime-infrastructure",
            "high-importance-low-local-evidence-density",
            "compiler-runtime",
            "crt-stdio",
            "crt-math",
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
                "0x0055ecb1",
                "CRT__UnlockHeapLock9_0055ecb1",
                new String[] {},
                "void CRT__UnlockHeapLock9_0055ecb1(void)",
                "Wave880 static read-back: CRT heap-allocation cleanup thunk. The body pushes lock index 9, calls CRT__UnlockByIndex, pops the stack slot, and returns. Xref evidence shows the only caller is CRT__HeapAllocBase at 0x0055ec4a, matching an early heap-allocation unlock path. Static retail lock-helper evidence only; exact CRT lock table semantics, thread behavior, allocator runtime state, BEA patching, and rebuild parity remain unproven.",
                tags("heap-lock", "unlock-index-9", "heap-alloc-cleanup")
            ),
            new Spec(
                "0x0055ed10",
                "CRT__UnlockHeapLock9_0055ed10",
                new String[] {},
                "void CRT__UnlockHeapLock9_0055ed10(void)",
                "Wave880 static read-back: second CRT heap-allocation cleanup thunk. The body pushes lock index 9, calls CRT__UnlockByIndex, pops the stack slot, and returns. Xref evidence shows the only caller is CRT__HeapAllocBase at 0x0055ec4a, matching a later heap-allocation unlock path. Static retail lock-helper evidence only; exact CRT lock table semantics, thread behavior, allocator runtime state, BEA patching, and rebuild parity remain unproven.",
                tags("heap-lock", "unlock-index-9", "heap-alloc-cleanup")
            ),
            new Spec(
                "0x0055f0ef",
                "CRT__UnlockHeapLock",
                new String[] {},
                "void CRT__UnlockHeapLock(void)",
                "Wave880 static read-back: CRT free-path heap-lock release thunk. The body pushes lock index 9, calls CRT__UnlockByIndex, pops the stack slot, and returns. Xref evidence shows the only caller is CRT__FreeBase at 0x0055f085. Static retail lock-helper evidence only; exact CRT lock table semantics, free-path runtime ownership, BEA patching, and rebuild parity remain unproven.",
                tags("heap-lock", "unlock-index-9", "free-path-cleanup")
            ),
            new Spec(
                "0x0055f147",
                "CRT__UnlockHeapLock_Alt",
                new String[] {},
                "void CRT__UnlockHeapLock_Alt(void)",
                "Wave880 static read-back: alternate CRT free-path heap-lock release thunk. The body pushes lock index 9, calls CRT__UnlockByIndex, pops the stack slot, and returns. Xref evidence shows the only caller is CRT__FreeBase at 0x0055f085, distinct from 0x0055f0ef but using the same lock index. Static retail lock-helper evidence only; exact CRT lock table semantics, free-path runtime ownership, BEA patching, and rebuild parity remain unproven.",
                tags("heap-lock", "unlock-index-9", "free-path-cleanup")
            ),
            new Spec(
                "0x0055f16e",
                "fwrite",
                new String[] {},
                "int __cdecl fwrite(void * ptr, int size, int count, void * file)",
                "Wave880 static read-back: public CRT fwrite wrapper. The body locks the stream through CRT__LockRouteByAddress(file), calls CRT__FWriteCore(ptr,size,count,file), unlocks through CRT__UnlockRouteByAddress(file), and returns the core element count. Xrefs include ImageIO__WriteTGA24, PCPlatform__WriteSaveFile, CFEPOptions default-options saves, and CDXEngine landscape texture cache writes. Static retail stdio evidence only; exact CRT version, text/binary mode behavior, runtime file I/O behavior, BEA patching, and rebuild parity remain unproven.",
                tags("stdio", "fwrite-wrapper", "file-output")
            ),
            new Spec(
                "0x0055f2a7",
                "CRT__WcsStr",
                new String[] {"CDropship__FindSubstringW"},
                "short * __cdecl CRT__WcsStr(short * haystack, short * needle)",
                "Wave880 static read-back: owner-corrected wide-substring helper formerly CDropship__FindSubstringW. The body walks a 16-bit haystack, compares the 16-bit needle at each offset, returns the matching haystack pointer when the needle terminates, and returns null when the haystack terminates first. The only xref is CMessageBox__SelectPortraitIndex, consistent with the commander fallback substring check and not Dropship ownership. Static retail wide-string evidence only; exact CRT identity, locale/case behavior, runtime portrait selection, BEA patching, and rebuild parity remain unproven.",
                tags("owner-corrected", "wide-string", "substring", "messagebox-caller")
            ),
            new Spec(
                "0x0055f380",
                "CRT__AcosClassifyAndDispatch",
                new String[] {},
                "void CRT__AcosClassifyAndDispatch(void)",
                "Wave880 static read-back: x87 acos classification/dispatch wrapper. The body spills ST0 as a double, calls CRT__ExtractFiniteExponentMaskOrPassThrough on the split double words, then calls CRT__AcosCoreWithFpuGuards with the same split double. Xrefs include three CStaticShadows__RayTriangleIntersect calls plus two no-function math stubs. Static retail FPU/math evidence only; exact CRT identity/version, x87 status behavior, all acos domain/exception semantics, BEA patching, and rebuild parity remain unproven.",
                tags("fpu-math", "acos-dispatch", "x87")
            ),
            new Spec(
                "0x0055f4d7",
                "fread",
                new String[] {},
                "int __cdecl fread(void * ptr, int size, int count, void * file)",
                "Wave880 static read-back: public CRT fread wrapper. The body locks the stream through CRT__LockRouteByAddress(file), calls CRT__FReadCore(ptr,size,count,file), unlocks through CRT__UnlockRouteByAddress(file), and returns the core element count. Xrefs include CLTShell startup file reads, CVertexShader clone, OggVorbisStream decoder/read paths, and PCPlatform__ReadSaveFile. Static retail stdio evidence only; exact CRT version, text/binary mode behavior, runtime file I/O/audio/save behavior, BEA patching, and rebuild parity remain unproven.",
                tags("stdio", "fread-wrapper", "file-input")
            ),
            new Spec(
                "0x0055fa40",
                "CRT__PowDispatch_ST0_ST1",
                new String[] {},
                "void CRT__PowDispatch_ST0_ST1(void)",
                "Wave880 static read-back: x87 pow dispatch wrapper. The body swaps ST0/ST1, spills the base and exponent as two doubles on the stack, passes split double words to CRT__PowCoreWithFpuGuards, and returns. Xrefs include CDXTexture PNG gamma/decode paths and PCPlatform__UpdateAsyncMusicStreamVolume. Static retail FPU/math evidence only; exact CRT identity/version, all pow domain/exception semantics, runtime PNG/audio behavior, BEA patching, and rebuild parity remain unproven.",
                tags("fpu-math", "pow-dispatch", "x87")
            ),
            new Spec(
                "0x0055fc35",
                "CRT__IsFloat10Integral_0055fc35",
                new String[] {},
                "void CRT__IsFloat10Integral_0055fc35(void)",
                "Wave880 static read-back: pow-core x87 integral-test helper. Instruction evidence duplicates ST0, rounds and compares it, initializes CL to zero, then takes the non-integral path through a scaling multiply before a second round/compare sequence; the two xrefs are both inside CRT__PowCoreWithFpuGuards. Ghidra keeps the signature as void because the helper uses x87/flag/register side effects rather than a normal C return. Static retail FPU/math evidence only; exact side-effect contract, all pow integral-exponent semantics, BEA patching, and rebuild parity remain unproven.",
                tags("fpu-math", "pow-integral-test", "x87-side-effect")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply") + " specs=" + specs.length);
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
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave880 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }
}
