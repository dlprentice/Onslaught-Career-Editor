//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyDecodeFeatureTailWave895 extends GhidraScript {
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
            "decode-feature-tail-wave895",
            "wave895-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-texture-decode-infrastructure",
            "raw-commentless-tail"
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
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + ex.getMessage());
        }
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x00598390",
                "CFastVB__DetectCpuFeatureMask",
                "int CFastVB__DetectCpuFeatureMask(void)",
                "Wave895 static read-back: CPU feature-mask detector feeding CFastVB__InitDispatchOpsFromFeatureFlags at 0x00598474. Static retail Ghidra evidence only: preserves the current name/signature while the CPUID body seeds mask bit 0, queries basic leaf 0 and version leaf 1, checks EDX bits 0x800000 and 0x02000000, probes extended leaves 0x80000000/0x80000001, compares the vendor string against AuthenticAMD/UnknownVendr context, and ORs observed extended feature bits 0x4/0x80/0x100/0x200 before returning the dispatch feature mask. Exact feature-bit names, SIMD dispatch semantics, runtime CPU coverage, BEA patching, and rebuild parity remain unproven.",
                tags("cpu-feature-mask", "cpuid", "dispatch-feature-gate")
            ),
            new Spec(
                "0x0059a71a",
                "CFastVB__SelectBestNodeTreeMatch",
                "int CFastVB__SelectBestNodeTreeMatch(void)",
                "Wave895 static read-back: CFastVB node-tree selector previously deferred by Wave709 and called from CTexture__ValidateConstantRegisterDeclarationType at 0x00599349 plus CDXTexture__ProcessTextureChunkAndEmitBindings at 0x00599576. Static retail Ghidra evidence only: preserves the current name/signature while the hidden ECX/stack ABI body clears optional outputs, scans candidate node-tree lists, scores and compares node/payload compatibility, handles ambiguous or undeclared identifiers through diagnostic ids 0xbbd/0xbfb/0xbbc/0xc06, can synthesize or reference node-type records for NULL, dword, float, vector, matrix, string, texture, pixelshader, vertexshader, intN, floatN, and double-like cases, and returns observed selector/error values including 0, 1, -0x7fffbffb, and -0x7ff8fff2. Exact node-tree layout, compatibility-score semantics, hidden ABI completeness, runtime parser behavior, BEA patching, and rebuild parity remain unproven.",
                tags("node-tree-selector", "shader-parser-compatibility", "hidden-stack-abi")
            ),
            new Spec(
                "0x0059b150",
                "CTexture__InitDecodeLookupScratchTables",
                "void CTexture__InitDecodeLookupScratchTables(void)",
                "Wave895 static read-back: decode lookup/scratch table initializer previously deferred by Wave710 and called by CTexture__InitializeDecodePipelineFromHeader at 0x0059b1e0. Static retail Ghidra evidence only: preserves the current name/signature while the hidden EAX state body allocates scratch storage through the state allocator callback, stores state+0x148 at base+0x100, clears the first 0x40 dwords, writes an identity byte table for 0..255, fills 0x60 dwords with 0xffffffff, clears another 0x60 dwords, and copies 0x20 dwords into the later scratch mirror. Exact decode-state field names, table roles, allocator contract, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("decode-lookup-scratch", "hidden-eax-state", "decode-pipeline")
            ),
            new Spec(
                "0x0059b1d0",
                "CTexture__InitializeDecodePipelineFromHeader",
                "void CTexture__InitializeDecodePipelineFromHeader(void)",
                "Wave895 static read-back: decode-pipeline initializer called by CTexture__CreateDecodeDispatchContext at 0x0059b4f9. Static retail Ghidra evidence only: preserves the current name/signature while the hidden ESI state body computes block geometry, initializes lookup scratch tables, tests compact decode eligibility, sets decode mode flags, emits callback event ids 0x2f/0x30/1, initializes scanline/color/entropy/output/coefficient/history/conversion resources, runs decode vtable callbacks at state[1]+0x18 and state[0x6e]+8, and optionally fills an output descriptor when direct-path state permits it. Exact decode-state layout, callback ABI, mode flag meanings, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("decode-pipeline-init", "hidden-esi-state", "callback-vtable")
            ),
            new Spec(
                "0x0059b510",
                "CDXTexture__ValidateJpegFrameAndBuildScanLayout",
                "void CDXTexture__ValidateJpegFrameAndBuildScanLayout(void)",
                "Wave895 static read-back: JPEG frame validator and scan-layout builder called by CDXTexture__DecodeState_AdvanceFrame at 0x0059b9e2. Static retail Ghidra evidence only: preserves the current name/signature while the hidden ESI JPEG state body checks width/height against 0xffdc, requires precision 8, caps component count at 10, validates horizontal/vertical sampling factors in 1..4, computes component block and plane fields with CDXTexture__CeilDiv, writes per-component descriptor offsets including +0x1c/+0x20/+0x24/+0x34/+0x38/+0x3c/+0x40/+0x44/+0x48, stores MCU row count at state+0x51, and toggles the decode controller slot +0x10. Exact JPEG component descriptor schema, sampling enum names, runtime JPEG/image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-frame-layout", "mcu-layout", "hidden-esi-state")
            ),
            new Spec(
                "0x0059b6f0",
                "CTexture__BuildComponentPlaneLayoutTables",
                "uint CTexture__BuildComponentPlaneLayoutTables(void)",
                "Wave895 static read-back: component plane/MCU layout table builder called by CDXTexture__DecodeState_RunPostFrameCallbacks at 0x0059b926. Static retail Ghidra evidence only: preserves the current name/signature while the hidden ESI state body validates component count in 1..4, calculates MCU grid dimensions at state+0x58/+0x59, writes per-component block layout fields +0x34/+0x38/+0x3c/+0x40/+0x44/+0x48, builds the component index table at state+0x5b with overflow/event id 0x0d checks, and uses a single-component shortcut that seeds default layout values. Exact component-plane schema, return-value meaning, MCU-table limits, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("component-plane-layout", "mcu-component-table", "hidden-esi-state")
            ),
            new Spec(
                "0x0059b880",
                "CTexture__EnsureComponentDecodeScratchBlocks",
                "void CTexture__EnsureComponentDecodeScratchBlocks(void)",
                "Wave895 static read-back: component scratch-block materializer called by CDXTexture__DecodeState_RunPostFrameCallbacks at 0x0059b92d. Static retail Ghidra evidence only: preserves the current name/signature while the hidden EBX state body walks selected components, validates each component template selector in 0..3, emits event id 0x34 when the selector/template is invalid, allocates a scratch block through the decode allocator callback, copies 0x21 dwords from the selected template block, and stores the new block pointer at component+0x4c. Exact template-block schema, component selector semantics, allocator ownership, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                tags("component-scratch-blocks", "hidden-ebx-state", "decode-allocator")
            ),
            new Spec(
                "0x0059be00",
                "CDXTexture__CreateDecodeJobDescriptor",
                "int CDXTexture__CreateDecodeJobDescriptor(void)",
                "Wave895 static read-back: decode job descriptor allocator callback previously deferred by Wave711 and registered by CDXTexture__InitDecodeAllocatorVtable through DATA xref 0x0059c563. Static retail Ghidra evidence only: preserves the current name/signature while the locked stack-ABI body validates mode 1 or emits allocator event id 0x0e, allocates a 0x248-byte block via CDXTexture__AllocFromBank_SplitBlock, stores caller descriptor fields into slots 1/2/3/8/10, clears slot 0, and links the descriptor into the owner list at allocator_state+0x44. Exact descriptor schema, stack parameter names, allocator-state layout, callback contract, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("decode-job-descriptor", "allocator-vtable-callback", "locked-stack-abi")
            ),
            new Spec(
                "0x0059be70",
                "CDXTexture__AllocDecodeBlockAndLink",
                "int CDXTexture__AllocDecodeBlockAndLink(void)",
                "Wave895 static read-back: decode block allocator/link callback previously deferred by Wave711 and registered by CDXTexture__InitDecodeAllocatorVtable through DATA xref 0x0059c56a. Static retail Ghidra evidence only: preserves the current name/signature while the locked stack-ABI body matches the 0x248-byte allocation and field population pattern of 0x0059be00, validates mode 1 or emits allocator event id 0x0e, and links the allocated block into the parallel owner list at allocator_state+0x48. Exact descriptor schema, stack parameter names, allocator-state layout, callback contract, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                tags("decode-block-link", "allocator-vtable-callback", "locked-stack-abi")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = (args == null || args.length == 0) ? "dry" : args[0];
        boolean dryRun = isDryRun(mode);
        println("ApplyDecodeFeatureTailWave895 mode=" + (dryRun ? "dry" : "apply"));

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
            throw new IllegalStateException("ApplyDecodeFeatureTailWave895 had failures");
        }
    }
}
