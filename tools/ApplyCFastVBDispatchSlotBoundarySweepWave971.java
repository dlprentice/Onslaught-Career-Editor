//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCFastVBDispatchSlotBoundarySweepWave971 extends GhidraScript {
    private static class Spec {
        final String address;
        final String slot;
        final String store;
        final String previousTerminal;
        final String firstInstruction;
        final String terminal;

        Spec(String address, String slot, String store, String previousTerminal, String firstInstruction, String terminal) {
            this.address = address;
            this.slot = slot;
            this.store = store;
            this.previousTerminal = previousTerminal;
            this.firstInstruction = firstInstruction;
            this.terminal = terminal;
        }

        String suffix() {
            return address.substring(2);
        }

        String name() {
            return "CFastVB__DispatchOp_Slot" + slot.substring(2).toUpperCase() + "_" + suffix();
        }

        String comment() {
            return "Wave971 CFastVB dispatch-slot boundary sweep: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +" +
                slot + " at " + store + ". The block starts after " + previousTerminal + ", begins with " + firstInstruction +
                ", and reaches first observed terminal " + terminal + ". Signature is intentionally stack-locked as int(void). " +
                "Static retail Ghidra evidence only; exact dispatch-table slot schema, vector/quaternion/matrix layout, packed lane order, hidden MMX/SSE/register ABI, exact source identity, runtime CPU dispatch/math/render behavior, BEA patching, and rebuild parity remain separate proof.";
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private boolean hasAllTags(Function fn, String[] expectedTags) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expectedTags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean signatureMatches(Function fn) {
        DataType intType = IntegerDataType.dataType;
        return fn.getReturnType() != null
            && (fn.getReturnType().isEquivalent(intType) || fn.getReturnType().getDisplayName().equals(intType.getDisplayName()))
            && fn.getParameterCount() == 0;
    }

    private void applySignature(Function fn) throws Exception {
        fn.setReturnType(IntegerDataType.dataType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            new ParameterImpl[] {}
        );
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec("0x005a4fee", "0xb0", "0x005985e0", "0x005a4feb RET 0x18", "MOV EDX, dword ptr [ESP + 0x8]", "0x005a504f RET 0x8"),
            new Spec("0x005a50f9", "0xe0", "0x00598630", "0x005a50f6 RET 0x8", "MOV EDX, dword ptr [ESP + 0x8]", "0x005a519b RET 0x8"),
            new Spec("0x005a5bd7", "0x0c", "0x005984a4", "0x005a5bd4 RET 0x1c", "FEMMS", "0x005a5e06 RET 0xc"),
            new Spec("0x005a5e09", "0x2c", "0x005984d5", "0x005a5e06 RET 0xc", "MOV EAX, dword ptr [ESP + 0x4]", "0x005a5ed5 RET 0x4"),
            new Spec("0x005a5ed8", "0x68", "0x0059853e", "0x005a5ed5 RET 0x4", "MOV EAX, dword ptr [ESP + 0x4]", "0x005a5f25 RET 0x10"),
            new Spec("0x005a5f28", "0x6c", "0x00598545", "0x005a5f25 RET 0x10", "FEMMS", "0x005a6010 RET 0xc"),
            new Spec("0x005a6013", "0x70", "0x0059854c", "0x005a6010 RET 0xc", "FEMMS", "0x005a60ec RET 0x8"),
            new Spec("0x005a77bc", "0xa4", "0x005985c2", "0x005a77b9 RET 0x10", "MOV EAX, dword ptr [ESP + 0x4]", "0x005a7ced RET 0x14"),
            new Spec("0x005a923f", "0x10", "0x00598658", "0x005a923c RET 0xc", "FEMMS", "0x005a945f RET 0xc"),
            new Spec("0x005a996b", "0x48", "0x00598506", "0x005a9968 RET 0xc", "FEMMS", "0x005a9984 RET 0xc"),
            new Spec("0x005a9987", "0x04", "0x00598496", "0x005a9984 RET 0xc", "FEMMS", "0x005a99f5 RET 0xc"),
            new Spec("0x005a9abe", "0xcc", "0x005985f4", "0x005a9abb RET 0x8", "MOV EDX, dword ptr [ESP + 0xc]", "0x005a9b2c RET 0x18"),
            new Spec("0x005a9b2f", "0xc4", "0x0059861c", "0x005a9b2c RET 0x18", "FEMMS", "0x005a9c00 RET 0x18"),
            new Spec("0x005a9c03", "0xc8", "0x0059864e", "0x005a9c00 RET 0x18", "MOVD MM0, dword ptr [ESP + 0x18]", "0x005a9cea RET 0x18"),
            new Spec("0x005aa5c0", "0xe4", "0x00598673", "0x005aa5a7 RET 0xc", "SUB ESP, 0x1c", "0x005aa738 RET 0xc"),
            new Spec("0x005aa82d", "0x44", "0x005984ff", "0x005aa82a RET 0xc", "FEMMS", "0x005aa8c2 RET 0x18"),
            new Spec("0x005aa8c5", "0xc0", "0x005985fe", "0x005aa8c2 RET 0x18", "MOV EDX, dword ptr [ESP + 0xc]", "0x005aa90b RET 0x18"),
            new Spec("0x005aa90e", "0xb8", "0x00598608", "0x005aa90b RET 0x18", "MOV EDX, dword ptr [ESP + 0x8]", "0x005aa94e RET 0x8"),
            new Spec("0x005aa951", "0xbc", "0x00598644", "0x005aa94e RET 0x8", "MOVD MM0, dword ptr [ESP + 0x18]", "0x005aa9f9 RET 0x18"),
            new Spec("0x005aa9fc", "0x08", "0x0059849d", "0x005aa9f9 RET 0x18", "FEMMS", "0x005aaa7b RET 0xc"),
            new Spec("0x005aaa7e", "0x20", "0x005984c0", "0x005aaa7b RET 0xc", "FEMMS", "0x005aaada RET 0x8"),
            new Spec("0x005aaadd", "0x40", "0x005984f8", "0x005aaada RET 0x8", "PUSH EBX", "0x005aac0c RET 0x10"),
            new Spec("0x005aac0f", "0xd8", "0x005985ea", "0x005aac0c RET 0x10", "MOV EDX, dword ptr [ESP + 0xc]", "0x005aac7d RET 0x18"),
            new Spec("0x005aac80", "0xd0", "0x00598612", "0x005aac7d RET 0x18", "FEMMS", "0x005aad45 RET 0x18"),
            new Spec("0x005aad48", "0xd4", "0x0059863a", "0x005aad45 RET 0x18", "MOVD MM0, dword ptr [ESP + 0x18]", "0x005aae23 RET 0x18"),
            new Spec("0x005aae26", "0x30", "0x005984dc", "0x005aae23 RET 0x18", "FEMMS", "0x005aae66 RET 0xc"),
            new Spec("0x005aae69", "0x34", "0x005984e3", "0x005aae66 RET 0xc", "FEMMS", "0x005aaf4a RET 0x10"),
            new Spec("0x005aaf4d", "0x58", "0x00598522", "0x005aaf4a RET 0x10", "MOV EAX, dword ptr [ESP + 0x8]", "0x005aafc5 RET 0x10")
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();
        String[] tags = new String[] {
            "static-reaudit",
            "cfastvb-dispatch-slot-boundary-sweep-wave971",
            "wave971-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "dispatch-table-target",
            "cfastvb",
            "packed-math",
            "stack-locked",
            "comment-hardened",
            "signature-hardened"
        };

        for (Spec spec : specs()) {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            if (fn == null) {
                if (dryRun) {
                    println("WOULD_CREATE: " + spec.address + " " + spec.name());
                    stats.wouldCreate++;
                    continue;
                }
                boolean disassembled = disassemble(address);
                fn = createFunction(address, spec.name());
                if (fn == null) {
                    println("BAD: could not create function at " + spec.address + " disassembled=" + disassembled);
                    stats.bad++;
                    continue;
                }
                stats.created++;
            }

            boolean changed = false;
            if (!fn.getName().equals(spec.name())) {
                if (dryRun) {
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name());
                    stats.wouldRename++;
                    changed = true;
                } else {
                    fn.setName(spec.name(), SourceType.USER_DEFINED);
                    stats.renamed++;
                    changed = true;
                }
            }

            if (!signatureMatches(fn)) {
                if (dryRun) {
                    println("WOULD_SIGNATURE: " + spec.address + " int " + spec.name() + "(void)");
                    stats.signatureUpdated++;
                    changed = true;
                } else {
                    applySignature(fn);
                    stats.signatureUpdated++;
                    changed = true;
                }
            }

            if (fn.getComment() == null || !fn.getComment().equals(spec.comment())) {
                if (dryRun) {
                    println("WOULD_COMMENT: " + spec.address);
                    stats.commentOnlyUpdated++;
                    changed = true;
                } else {
                    fn.setComment(spec.comment());
                    stats.commentOnlyUpdated++;
                    changed = true;
                }
            }

            if (!hasAllTags(fn, tags)) {
                if (dryRun) {
                    println("WOULD_TAGS: " + spec.address);
                    stats.commentOnlyUpdated++;
                    changed = true;
                } else {
                    for (String tag : tags) {
                        fn.addTag(tag);
                    }
                    stats.commentOnlyUpdated++;
                    changed = true;
                }
            }

            if (changed) {
                stats.updated++;
            } else {
                stats.skipped++;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave971 CFastVB dispatch-slot boundary sweep encountered missing/bad rows");
        }
    }
}
